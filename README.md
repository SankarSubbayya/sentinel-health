# Sentinel Health

> **An offline triage net for the five grassroots emergencies — Trauma, Poisoning, Snake Bite, MI, Stroke.**

Sentinel Health is an offline-first, voice-enabled clinical decision support web app powered by **Gemma 4** running locally via **Ollama**. It is the **AI triage layer for the spoke** in a hub-and-spoke healthcare network — designed to help a community health worker or rural clinician decide *treat-here vs. escalate-to-hub* in seconds, even with no internet.

Scope is aligned to **TAI-VADE**, the Indian Ministry of Health framework for grassroots emergency care: Trauma, Poisoning, Snake Bite, MI, and Stroke — plus the high-yield conditions that present similarly (DKA, hypoglycemia, sepsis, anaphylaxis, severe dehydration).

Built for the **Gemma 4 Good Hackathon** (Google DeepMind / Kaggle, 2026), with clinical advisory from a practising clinician.

---

## The Pitch

**Elevator (10 sec):**
Sentinel Health gives community health workers an offline AI assistant that helps them spot life-threatening conditions and make the right referral — even with no internet.

**Story (30 sec):**
Two billion people get their primary care from community health workers, not doctors. These workers see chest pain, fever, sudden confusion every day — but they aren't trained to diagnose, and they have no internet to look things up. Sentinel Health runs Gemma 4 entirely on a clinic laptop. Voice in, ranked differential diagnosis out, with a guideline citation and a hard safety layer that flags emergencies. No cloud, no excuses.

**Mission:**
Democratize clinical decision support for low-resource healthcare — supplementary to the clinician, never a replacement.

### Design principles (from clinician review)
1. **Supplementary, not replacement.** No doctor can be replaced by an app — the disclaimer is load-bearing.
2. **Confirmatory, not informational.** Lead with action ("Refer NOW; aspirin 325 mg if no allergy"), not menus of possibilities.
3. **No over- and no under-diagnosis.** We track sensitivity and specificity separately.
4. **History trumps tests.** Typical anginal pain → escalate, even if ECG / Echo / troponin are normal (unstable angina).
5. **Bridge the referral.** Every RED diagnosis ships with a *during-transport* protocol.

---

## Who Is This For?

The tool is **for the healthcare worker** — not the patient and not directly the doctor.

- **Primary user — Community Health Worker (CHW):** limited training, sees patients in villages with no internet, needs help triaging and escalating.
- **Secondary user — Rural physician:** uses it as a second opinion when seeing 60–80 patients/day.
- **The patient never touches the app.** The CHW listens to the patient, then dictates symptoms into the app.

This is deliberate. A tool for clinicians is **decision support**, not diagnosis — same legal posture as UpToDate or a paper guideline. The persistent in-app disclaimer reads: *"Triage support only. Not a substitute for clinical judgment."*

---

## How It Works

```
Voice (browser)  →  FastAPI backend  →  Gemma 4 via Ollama  →  KB-grounded diagnosis
                          │                                          │
                          └──────►  Rule-based safety engine  ◄──────┘
                                   (red flags override LLM)
```

- **Frontend:** browser web app, Web Speech API for voice in
- **Backend:** Python / FastAPI
- **Model:** `gemma4:e4b-it-q4_K_M` — instruction-tuned 4B-class, Q4 quantized, runs on CPU
- **Knowledge base:** WHO / CDC / ACC guidelines as JSON; cardiology + diabetes + general acute
- **Safety layer:** deterministic red-flag rules that escalate independently of LLM confidence

Every diagnosis comes back with: top-3 differentials, confidence (capped at 0.9), guideline citation, recommended next action, and a triage level (RED / YELLOW / GREEN).

---

## Hackathon Tracks

| Track | Why we fit |
|---|---|
| **Main Track** ($50k) | Big vision (CHWs everywhere) + working offline + emotional story |
| **Health & Sciences Impact** ($10k) | Direct: democratizes specialist knowledge for primary care |
| **Ollama Special Tech** ($10k) | 100% local Gemma 4 deployment, verifiable offline |

Total prize upside: **$60,000.**

---

## Status

| Milestone | Status |
|---|---|
| End-to-end backend (Gemma 4 + KB + safety) | ✅ Working |
| Synthetic test suite, 20 vignettes | ✅ 18/20 passing (90%) |
| Web frontend with voice | 🚧 Week 2 |
| Demo video (≤ 3 min) | 🚧 Week 3 |
| Kaggle writeup (≤ 1,500 words) | 🚧 Week 3 |
| Submission deadline | 2026-05-18, 11:59 PM UTC |

---

## Quick Start

Requires Python 3.12+, [uv](https://github.com/astral-sh/uv), and [Ollama](https://ollama.com).

```bash
# 1. Pull the model (~3 GB, one time)
ollama pull gemma4:e4b-it-q4_K_M

# 2. Install Python dependencies
uv sync

# 3. Run the backend
uv run uvicorn main:app --reload

# 4. Open the demo in your browser
open http://localhost:8000/demo
```

### Run the validation suite

```bash
uv run python -m tests.eval_cases --save
```

This runs 20 synthetic clinical cases through the diagnosis service and reports the pass rate. Target: ≥ 18 / 20.

---

## Project Documents

- [PRD.md](PRD.md) — full product requirements
- [SENTINEL_HEALTH.md](SENTINEL_HEALTH.md) — clinical / architectural design
- [HACKATHON.md](HACKATHON.md) — Kaggle hackathon rules and tracks

---

## Disclaimer

This is a hackathon MVP and a **decision support tool, not a diagnostic system**. Results are for triage guidance only and should not replace clinical judgment by licensed healthcare providers. Always consult a qualified physician for diagnosis and treatment.
