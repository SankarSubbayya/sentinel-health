"""Run synthetic clinical cases through the diagnosis service and score the results.

Usage:
    python -m tests.eval_cases               # run all cases
    python -m tests.eval_cases --limit 3     # run first 3
    python -m tests.eval_cases --case card_01_classic_acs   # one case

Pass criteria (per case):
  - triage: predicted >= expected (RED > YELLOW > GREEN). More-conservative is OK.
  - primary_diagnosis: top differential's matched condition id is in expected_condition_ids.
  - red_flag: if expected_red_flag is true, escalation_required must be true.

Exits with code 0 if pass rate >= 18/20 (90%), 1 otherwise.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.knowledge.loader import kb
from app.services.diagnosis import diagnosis_service

CASES_PATH = Path(__file__).parent / "cases" / "clinical_cases.json"
RESULTS_DIR = Path(__file__).parent / "results"

TRIAGE_RANK = {"GREEN": 0, "YELLOW": 1, "RED": 2}
PASS_THRESHOLD = 0.90  # ≥ 27/30
SENSITIVITY_TARGET = 0.95  # of RED cases, ≥ 95% must be caught as RED
SPECIFICITY_TARGET = 0.80  # of non-RED cases, ≥ 80% must NOT be over-escalated to RED


SYNONYMS = {
    "stable angina": "acs",
    "unstable angina": "acs",
    "angina": "acs",
    "myocardial infarction": "acute_mi",
    "mi": "acute_mi",
    "stemi": "acute_mi",
    "nstemi": "acs",
    "heart attack": "acute_mi",
    "ketoacidosis": "dka",
    "hyperosmolar hyperglycemic state": "hyperglycemia",
    "hhs": "hyperglycemia",
    "reactive hypoglycemia": "hypoglycemia",
    "low blood sugar": "hypoglycemia",
    "high blood sugar": "hyperglycemia",
    "cold": "common_cold",
    "upper respiratory infection": "common_cold",
    "uri": "common_cold",
    "influenza": "flu",
    "cva": "stroke",
    "ischemic stroke": "stroke",
    "septic shock": "sepsis",
    "severe sepsis": "sepsis",
    "hypertensive emergency": "hypertensive_crisis",
    "hypertensive encephalopathy": "htn_encephalopathy",
    "anaphylactic reaction": "anaphylaxis",
    "trauma": "major_trauma",
    "polytrauma": "major_trauma",
    "blunt trauma": "major_trauma",
    "head injury": "major_trauma",
    "traumatic brain injury": "major_trauma",
    "tbi": "major_trauma",
    "fracture": "major_trauma",
    "laceration": "major_trauma",
    "minor laceration": "major_trauma",
    "minor injury": "major_trauma",
    "intoxication": "poisoning",
    "overdose": "poisoning",
    "drug overdose": "poisoning",
    "paracetamol overdose": "poisoning",
    "acetaminophen overdose": "poisoning",
    "organophosphate poisoning": "poisoning",
    "organophosphate toxicity": "poisoning",
    "pesticide poisoning": "poisoning",
    "ingestion": "poisoning",
    "accidental ingestion": "poisoning",
    "snake bite": "snake_bite",
    "snakebite": "snake_bite",
    "envenomation": "snake_bite",
    "snake envenomation": "snake_bite",
    "neurotoxic envenomation": "snake_bite",
    "hemotoxic envenomation": "snake_bite",
    "viper bite": "snake_bite",
    "cobra bite": "snake_bite",
    "krait bite": "snake_bite",
    "no acute condition identified": "benign_default",
    "no acute condition": "benign_default",
    "no specific condition": "benign_default",
    "no specific condition identified": "benign_default",
    "minor injury": "benign_default",
    "minor laceration": "benign_default",
    "minor wound": "benign_default",
    "no urgent diagnosis": "benign_default",
    "no acute finding": "benign_default",
}


def _normalize(name: str) -> str:
    """Strip parenthetical suffixes and lowercase."""
    s = name.split("(")[0].strip().lower()
    return s


def map_condition_to_id(condition_name: str) -> str | None:
    """Best-effort map an LLM-produced condition string to a KB id."""
    name_norm = _normalize(condition_name)
    if not name_norm:
        return None

    if name_norm in SYNONYMS:
        return SYNONYMS[name_norm]

    for c in kb.conditions:
        if c["id"].lower() == name_norm:
            return c["id"]
        kb_name_norm = _normalize(c["name"])
        if kb_name_norm == name_norm:
            return c["id"]

    for c in kb.conditions:
        kb_name_norm = _normalize(c["name"])
        if kb_name_norm in name_norm or name_norm in kb_name_norm:
            return c["id"]

    for syn, target_id in SYNONYMS.items():
        if syn in name_norm:
            return target_id

    return None


def score_case(case: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    expected_triage = case["expected_triage"]
    expected_ids = set(case["expected_condition_ids"])
    expected_red_flag = case["expected_red_flag"]

    predicted_triage = result.get("triage_level", "GREEN")
    triage_pass = TRIAGE_RANK.get(predicted_triage, 0) >= TRIAGE_RANK[expected_triage]

    differentials = result.get("differential_diagnosis", [])
    if differentials:
        top = differentials[0].get("condition", "")
        top_id = map_condition_to_id(top)
        diagnosis_pass = top_id in expected_ids if top_id else False
    else:
        top = ""
        top_id = None
        diagnosis_pass = False

    safety = result.get("safety", {})
    escalation_required = safety.get("escalation_required", False)
    red_flag_pass = (not expected_red_flag) or escalation_required

    overall_pass = triage_pass and diagnosis_pass and red_flag_pass

    return {
        "case_id": case["id"],
        "category": case["category"],
        "expected_triage": expected_triage,
        "predicted_triage": predicted_triage,
        "triage_pass": triage_pass,
        "expected_condition_ids": list(expected_ids),
        "top_diagnosis": top,
        "top_diagnosis_id": top_id,
        "diagnosis_pass": diagnosis_pass,
        "expected_red_flag": expected_red_flag,
        "escalation_required": escalation_required,
        "red_flag_pass": red_flag_pass,
        "overall_pass": overall_pass,
    }


async def run_case(case: dict[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    result = await diagnosis_service.diagnose(
        symptoms=case["symptoms"],
        patient_context=case.get("patient_context", ""),
    )
    elapsed = time.monotonic() - started
    score = score_case(case, result)
    score["elapsed_sec"] = round(elapsed, 2)
    score["error"] = result.get("error")
    return score


def format_row(score: dict[str, Any]) -> str:
    mark = "PASS" if score["overall_pass"] else "FAIL"
    parts = [
        f"[{mark}]",
        f"{score['case_id']:<35}",
        f"triage {score['predicted_triage']:<6} (exp {score['expected_triage']:<6})",
        f"top: {(score['top_diagnosis'] or '-')[:32]:<32}",
        f"{score['elapsed_sec']:>5.1f}s",
    ]
    if score.get("error"):
        parts.append(f"ERR: {score['error'][:60]}")
    return " ".join(parts)


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--case", type=str, default=None)
    parser.add_argument("--save", action="store_true", help="Write results JSON")
    args = parser.parse_args()

    payload = json.loads(CASES_PATH.read_text())
    cases = payload["cases"]
    if args.case:
        cases = [c for c in cases if c["id"] == args.case]
        if not cases:
            print(f"No case with id {args.case}")
            return 1
    if args.limit:
        cases = cases[: args.limit]

    print(f"Running {len(cases)} cases against diagnosis_service")
    print("-" * 100)

    scores: list[dict[str, Any]] = []
    for case in cases:
        score = await run_case(case)
        scores.append(score)
        print(format_row(score))

    passed = sum(1 for s in scores if s["overall_pass"])
    total = len(scores)
    pass_rate = passed / total if total else 0.0

    red_total = sum(1 for s in scores if s["expected_triage"] == "RED")
    red_caught = sum(
        1 for s in scores if s["expected_triage"] == "RED" and s["predicted_triage"] == "RED"
    )
    nonred_total = sum(1 for s in scores if s["expected_triage"] != "RED")
    nonred_kept = sum(
        1 for s in scores if s["expected_triage"] != "RED" and s["predicted_triage"] != "RED"
    )
    sensitivity = red_caught / red_total if red_total else 0.0
    specificity = nonred_kept / nonred_total if nonred_total else 0.0

    print("-" * 100)
    print(f"PASS: {passed}/{total}  ({pass_rate * 100:.1f}%)")
    print(
        f"SENSITIVITY: {red_caught}/{red_total}  ({sensitivity * 100:.1f}%)  "
        f"[target ≥ {SENSITIVITY_TARGET * 100:.0f}%]"
    )
    print(
        f"SPECIFICITY: {nonred_kept}/{nonred_total}  ({specificity * 100:.1f}%)  "
        f"[target ≥ {SPECIFICITY_TARGET * 100:.0f}%]"
    )

    breakdown = {}
    for s in scores:
        cat = s["category"]
        breakdown.setdefault(cat, [0, 0])
        breakdown[cat][1] += 1
        if s["overall_pass"]:
            breakdown[cat][0] += 1
    for cat, (p, t) in sorted(breakdown.items()):
        print(f"  {cat:<14}  {p}/{t}")

    failure_modes = {"triage": 0, "diagnosis": 0, "red_flag": 0}
    for s in scores:
        if s["overall_pass"]:
            continue
        if not s["triage_pass"]:
            failure_modes["triage"] += 1
        if not s["diagnosis_pass"]:
            failure_modes["diagnosis"] += 1
        if not s["red_flag_pass"]:
            failure_modes["red_flag"] += 1
    if total - passed:
        print("Failure modes:", failure_modes)

    if args.save:
        RESULTS_DIR.mkdir(exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        out = RESULTS_DIR / f"eval_{timestamp}.json"
        out.write_text(
            json.dumps(
                {
                    "timestamp": timestamp,
                    "passed": passed,
                    "total": total,
                    "pass_rate": pass_rate,
                    "sensitivity": sensitivity,
                    "specificity": specificity,
                    "red_caught": red_caught,
                    "red_total": red_total,
                    "nonred_kept": nonred_kept,
                    "nonred_total": nonred_total,
                    "scores": scores,
                },
                indent=2,
            )
        )
        print(f"Results written to {out}")

    targets_hit = (
        pass_rate >= PASS_THRESHOLD
        and sensitivity >= SENSITIVITY_TARGET
        and specificity >= SPECIFICITY_TARGET
    )
    return 0 if targets_hit else 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
