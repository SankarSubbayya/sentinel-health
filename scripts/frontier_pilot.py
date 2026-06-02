"""Pilot batch: run Case A (snake bite) + Case B (redacted ECG) + 5 audit-log
RED text cases against Claude Opus 4.7, GPT-5, and Gemini 2.7 Flash. Capture
results for §7.5 of docs/small_vs_frontier.md.

Usage:  .venv/bin/python scripts/frontier_pilot.py

Reads .env from the project root. Writes data/frontier_pilot/results.jsonl
(one line per (case, provider) pair) and prints a summary table.
"""

from __future__ import annotations

import base64
import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

OUT_DIR = Path(__file__).resolve().parents[1] / "data" / "frontier_pilot"
OUT_DIR.mkdir(parents=True, exist_ok=True)
RESULTS = OUT_DIR / "results.jsonl"

# ─── Cases ────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are a clinical decision support assistant for community health workers "
    "in rural India. Given symptoms (and optionally an image), produce a JSON "
    "object with these fields: triage_level (RED/YELLOW/GREEN), top_condition, "
    "confidence (0..1), reasoning, recommendation. Be concise. Return JSON ONLY."
)


def img_b64(path: str) -> str:
    return base64.b64encode(Path(path).read_bytes()).decode()


CASES = [
    # Image cases — exact same as §7.3 Case A and Case B testing
    {
        "id": "A1",
        "label": "Case A · snake bite image · minimal text",
        "symptoms": "patient brought in with this wound on forearm, child screaming",
        "context": "child, rural India, monsoon",
        "image_path": "data/hand_image.jpeg",
        "gold_triage": "RED",
        "gold_condition": "Snake Bite Envenomation",
    },
    {
        "id": "A2",
        "label": "Case A · snake bite image · contextual phrasing",
        "symptoms": "I was sleeping outside and my hand began to hurt very strongly",
        "context": "",
        "image_path": "data/hand_image.jpeg",
        "gold_triage": "RED",
        "gold_condition": "Snake Bite Envenomation",
    },
    {
        "id": "B1",
        "label": "Case B · ECG image · clinical phrasing",
        "symptoms": "55-year-old with crushing chest pain and sweating for 30 minutes, ECG attached",
        "context": "Diabetic, smoker",
        "image_path": "data/ecg_redacted.jpeg",
        "gold_triage": "RED",
        "gold_condition": "Acute Myocardial Infarction",
    },
    {
        "id": "B2",
        "label": "Case B · ECG image · minimal text",
        "symptoms": "see attached ECG",
        "context": "",
        "image_path": "data/ecg_redacted.jpeg",
        "gold_triage": "RED",
        "gold_condition": "Acute Myocardial Infarction",
    },
    # 5 text-only audit-log RED cases (no image)
    {
        "id": "T1",
        "label": "Audit-log T1 · MI atypical",
        "symptoms": "60-year-old woman with jaw pain, nausea, fatigue for one hour",
        "context": "Type 2 diabetes, hypertension",
        "image_path": None,
        "gold_triage": "RED",
        "gold_condition": "Acute Coronary Syndrome",
    },
    {
        "id": "T2",
        "label": "Audit-log T2 · Snake bite",
        "symptoms": "snake bit child two hours ago, family tied a rope, swelling at bite site",
        "context": "Rural India, monsoon season",
        "image_path": None,
        "gold_triage": "RED",
        "gold_condition": "Snake Bite Envenomation",
    },
    {
        "id": "T3",
        "label": "Audit-log T3 · Organophosphate poisoning",
        "symptoms": "farmer ingested pesticide one hour ago, drooling, small pupils, slow heart rate",
        "context": "Suspected organophosphate",
        "image_path": None,
        "gold_triage": "RED",
        "gold_condition": "Organophosphate Poisoning",
    },
    {
        "id": "T4",
        "label": "Audit-log T4 · Stroke",
        "symptoms": "one side of body not moving, slurred speech started 45 minutes ago",
        "context": "70-year-old male, hypertensive",
        "image_path": None,
        "gold_triage": "RED",
        "gold_condition": "Acute Stroke",
    },
    {
        "id": "T5",
        "label": "Audit-log T5 · Major trauma",
        "symptoms": "road accident 30 minutes ago, conscious but unable to move legs, neck pain",
        "context": "Two-wheeler crash, helmet on",
        "image_path": None,
        "gold_triage": "RED",
        "gold_condition": "Major Trauma",
    },
]


# ─── Providers ────────────────────────────────────────────────────────────


def user_text(c: dict) -> str:
    parts = [f"Symptoms: {c['symptoms']}"]
    if c.get("context"):
        parts.append(f"Patient context: {c['context']}")
    parts.append("Return JSON with the required fields.")
    return "\n".join(parts)


def parse_json_lenient(s: str) -> dict | None:
    """Pull out the first JSON object found in a response string."""
    s = s.strip()
    if s.startswith("```"):
        s = s.strip("`")
        if s.lower().startswith("json"):
            s = s[4:]
    try:
        return json.loads(s)
    except json.JSONDecodeError:
        pass
    import re

    m = re.search(r"\{.*\}", s, re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except json.JSONDecodeError:
            return None
    return None


def call_anthropic(c: dict) -> dict:
    import anthropic

    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    content: list = [{"type": "text", "text": user_text(c)}]
    if c.get("image_path"):
        content.insert(
            0,
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": "image/jpeg",
                    "data": img_b64(c["image_path"]),
                },
            },
        )
    model = "claude-opus-4-7"
    t0 = time.time()
    try:
        r = client.messages.create(
            model=model,
            max_tokens=600,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": content}],
        )
        text = r.content[0].text if r.content else ""
        return {
            "provider": "anthropic",
            "model": model,
            "elapsed_s": round(time.time() - t0, 2),
            "raw": text,
            "parsed": parse_json_lenient(text),
            "input_tokens": r.usage.input_tokens,
            "output_tokens": r.usage.output_tokens,
        }
    except Exception as e:
        return {
            "provider": "anthropic",
            "model": model,
            "elapsed_s": round(time.time() - t0, 2),
            "error": str(e)[:300],
        }


def call_openai(c: dict) -> dict:
    import openai

    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    content: list = [{"type": "input_text", "text": user_text(c)}]
    if c.get("image_path"):
        content.append(
            {
                "type": "input_image",
                "image_url": f"data:image/jpeg;base64,{img_b64(c['image_path'])}",
            }
        )
    model = "gpt-5"
    t0 = time.time()
    try:
        r = client.responses.create(
            model=model,
            instructions=SYSTEM_PROMPT,
            input=[{"role": "user", "content": content}],
        )
        text = r.output_text
        usage = getattr(r, "usage", None)
        return {
            "provider": "openai",
            "model": model,
            "elapsed_s": round(time.time() - t0, 2),
            "raw": text,
            "parsed": parse_json_lenient(text),
            "input_tokens": getattr(usage, "input_tokens", None) if usage else None,
            "output_tokens": getattr(usage, "output_tokens", None) if usage else None,
        }
    except Exception as e:
        return {
            "provider": "openai",
            "model": model,
            "elapsed_s": round(time.time() - t0, 2),
            "error": str(e)[:300],
        }


def call_gemini(c: dict) -> dict:
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    parts: list = [types.Part.from_text(text=user_text(c))]
    if c.get("image_path"):
        parts.append(
            types.Part.from_bytes(
                data=Path(c["image_path"]).read_bytes(), mime_type="image/jpeg"
            )
        )
    model = "gemini-2.5-flash"  # Gemini 2.7 isn't out yet at API time; use latest stable
    t0 = time.time()
    try:
        r = client.models.generate_content(
            model=model,
            config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
            contents=[types.Content(role="user", parts=parts)],
        )
        text = r.text or ""
        return {
            "provider": "google",
            "model": model,
            "elapsed_s": round(time.time() - t0, 2),
            "raw": text,
            "parsed": parse_json_lenient(text),
            "input_tokens": getattr(r.usage_metadata, "prompt_token_count", None),
            "output_tokens": getattr(r.usage_metadata, "candidates_token_count", None),
        }
    except Exception as e:
        return {
            "provider": "google",
            "model": model,
            "elapsed_s": round(time.time() - t0, 2),
            "error": str(e)[:300],
        }


# ─── Driver ────────────────────────────────────────────────────────────────


def main():
    print(f"Cases: {len(CASES)}    Providers: 3    Total calls: {len(CASES) * 3}\n")
    RESULTS.unlink(missing_ok=True)

    summary = []
    for c in CASES:
        print(f"━━ {c['id']}  {c['label']}")
        for fn in (call_anthropic, call_openai, call_gemini):
            res = fn(c)
            out = {
                "case_id": c["id"],
                "case_label": c["label"],
                "gold_triage": c["gold_triage"],
                "gold_condition": c["gold_condition"],
                "has_image": c.get("image_path") is not None,
                **res,
            }
            with RESULTS.open("a") as f:
                f.write(json.dumps(out) + "\n")

            triage = (out.get("parsed") or {}).get("triage_level") or "ERR"
            cond = (out.get("parsed") or {}).get("top_condition") or ""
            err = out.get("error", "")
            print(
                f"   {out['provider']:9s} {out['model']:24s}  "
                f"{out['elapsed_s']:5.1f}s  "
                f"{triage:6s}  {cond[:40]:40s}  {err[:50]}"
            )
            summary.append(out)
        print()

    # Compact summary table
    print("\n" + "═" * 90)
    print("SUMMARY")
    print("═" * 90)
    print(f"{'case':4s} {'gold':5s}  {'anthropic':30s} {'openai':30s} {'google':30s}")
    by = {}
    for s in summary:
        by.setdefault(s["case_id"], {})[s["provider"]] = s

    for cid in [c["id"] for c in CASES]:
        row = by.get(cid, {})
        a = (row.get("anthropic", {}).get("parsed") or {}).get("triage_level") or "—"
        o = (row.get("openai", {}).get("parsed") or {}).get("triage_level") or "—"
        g = (row.get("google", {}).get("parsed") or {}).get("triage_level") or "—"
        gold = next(c["gold_triage"] for c in CASES if c["id"] == cid)
        print(f"{cid:4s} {gold:5s}  {a:30s} {o:30s} {g:30s}")

    print(f"\nResults written to {RESULTS}")


if __name__ == "__main__":
    main()
