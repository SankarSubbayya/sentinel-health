"""Pilot batch (SLM side): run the same 9 cases as scripts/frontier_pilot.py
against 6 local Ollama models — Gemma 4 e4b (Sentinel production), MedGemma
4B Q8, MedGemma 27B, Qwen 3 8B, Llama 3.2, and gpt-oss 20B. Vision-capable
models run all 9 cases; text-only models run the 5 text cases.

Writes data/frontier_pilot/slm_results.jsonl and prints a summary table.
"""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path

import sys
import httpx

# Reuse CASES + helpers from the frontier-pilot script
sys.path.insert(0, str(Path(__file__).resolve().parent))
from frontier_pilot import CASES, parse_json_lenient, user_text  # type: ignore  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "data" / "frontier_pilot" / "slm_results.jsonl"
OLLAMA = "http://localhost:11434"
SYSTEM = (
    "You are a clinical decision support assistant for community health workers "
    "in rural India. Given symptoms (and optionally an image), produce a JSON "
    "object with these fields: triage_level (RED/YELLOW/GREEN), top_condition, "
    "confidence (0..1), reasoning, recommendation. Be concise. Return JSON ONLY."
)


# (model_id, has_vision, label)
MODELS = [
    ("gemma4:e4b-it-q4_K_M", True, "Gemma 4 e4b Q4_K_M (Sentinel prod)"),
    ("amsaravi/medgemma-4b-it:q8", True, "MedGemma 4B Q8"),
    ("alibayram/medgemma:27b", True, "MedGemma 27B"),
    ("qwen3:8b", False, "Qwen 3 8B"),
    ("llama3.2:latest", False, "Llama 3.2 (latest)"),
    ("gpt-oss:20b", False, "gpt-oss 20B"),
]


def call_ollama(model: str, case: dict) -> dict:
    prompt = SYSTEM + "\n\n" + user_text(case)
    body: dict = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
    }
    if case.get("image_path"):
        body["images"] = [base64.b64encode(Path(case["image_path"]).read_bytes()).decode()]
    t0 = time.time()
    try:
        r = httpx.post(f"{OLLAMA}/api/generate", json=body, timeout=600)
        r.raise_for_status()
        d = r.json()
        text = d.get("response", "")
        return {
            "elapsed_s": round(time.time() - t0, 2),
            "raw": text,
            "parsed": parse_json_lenient(text),
            "eval_count": d.get("eval_count"),
            "prompt_eval_count": d.get("prompt_eval_count"),
        }
    except Exception as e:
        return {"elapsed_s": round(time.time() - t0, 2), "error": str(e)[:300]}


def main():
    OUT.unlink(missing_ok=True)
    n_cases_per_model = sum(
        len(CASES) if vision else sum(1 for c in CASES if not c.get("image_path"))
        for _, vision, _ in MODELS
    )
    print(f"Total SLM inference calls: {n_cases_per_model}\n")

    summary: list = []
    for model, vision, label in MODELS:
        print(f"━━ {label}  [{model}]")
        for c in CASES:
            if c.get("image_path") and not vision:
                continue
            res = call_ollama(model, c)
            row = {
                "case_id": c["id"],
                "case_label": c["label"],
                "gold_triage": c["gold_triage"],
                "gold_condition": c["gold_condition"],
                "has_image": c.get("image_path") is not None,
                "provider": "ollama",
                "model": model,
                "model_label": label,
                **res,
            }
            with OUT.open("a") as f:
                f.write(json.dumps(row) + "\n")
            triage = (row.get("parsed") or {}).get("triage_level") or "ERR"
            cond = (row.get("parsed") or {}).get("top_condition") or ""
            err = row.get("error", "")
            print(
                f"   {c['id']:4s} {'IMG' if c.get('image_path') else 'TXT':3s} "
                f"{row['elapsed_s']:6.1f}s  {triage:6s}  {cond[:40]:40s} {err[:50]}"
            )
            summary.append(row)
        print()

    # Summary table
    print("\n" + "═" * 110)
    print("SUMMARY · sensitivity by model")
    print("═" * 110)
    print(f"{'model':40s}  {'cases':6s}  {'RED-correct':12s}  {'med_lat':8s}  {'p95_lat':8s}")
    by_model: dict = {}
    for s in summary:
        by_model.setdefault(s["model"], []).append(s)
    for model, _, label in MODELS:
        rs = by_model.get(model, [])
        if not rs:
            continue
        red_correct = sum(
            1 for r in rs if (r.get("parsed") or {}).get("triage_level") == r["gold_triage"]
        )
        lats = sorted([r["elapsed_s"] for r in rs if r.get("elapsed_s")])
        med = lats[len(lats) // 2] if lats else 0
        p95 = lats[max(0, int(len(lats) * 0.95) - 1)] if lats else 0
        print(f"{label:40s}  {len(rs):6d}  {red_correct}/{len(rs):<10d}  {med:6.1f}s  {p95:6.1f}s")

    print(f"\nResults written to {OUT}")


if __name__ == "__main__":
    main()
