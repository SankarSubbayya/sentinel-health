# Sentinel Health — Clinical Decision Support for Resource-Limited Settings

**Hackathon:** Gemma 4 Good Hackathon (Kaggle)
**Submission Deadline:** May 18, 2026 (11:59 PM UTC)
**Prize Tracks:** Main Track · Health & Sciences Impact · Ollama Special Technology
**Live demo:** [https://triage.accurateai.org/demo](https://triage.accurateai.org/demo)
**Code:** [github.com/SankarSubbayya/sentinel-health](https://github.com/SankarSubbayya/sentinel-health)
**Status:** Shipped — submission-ready as of W3-F8

---

## Problem statement

Two billion people receive primary care from a community health worker (CHW), not a doctor. At the village clinic level — particularly in rural India, the design context for this project — CHWs face four compounding constraints:

1. **No internet.** Cloud LLMs are a non-starter at the spoke.
2. **No specialist.** The nearest cardiologist / dermatologist / toxicologist is hours away.
3. **No follow-up.** Per our clinical advisor: *"Follow-up illa"* — one staff member, who refers and the loop closes there.
4. **Limited equipment.** No defibrillator, no ventilator, no monitor — which means clinical decisions like "should I thrombolyse?" cannot be safely made at the spoke even when the diagnosis is correct.

The product scope is deliberately narrow: the five **TAI-VADE** grassroots emergencies — Trauma, Poisoning, Snake Bite, MI, Stroke — plus the high-yield mimics (DKA, hypoglycemia, sepsis, anaphylaxis, severe dehydration, common skin/wound presentations). Outside that scope, the system returns *"No acute condition identified"* by design rather than inventing.

**Posture:** decision support, not diagnosis. Legal stance identical to UpToDate or a paper guideline; the persistent disclaimer is load-bearing.

---

## Architecture

```
Browser (voice in, image attach, multilingual UI)
        │   HTTP/JSON
        ▼
FastAPI (main.py → app/api/routes.py)
        │
        └──► DiagnosisService (app/services/diagnosis.py)
               │
               ├──► KB lookup (app/knowledge/loader.py)
               │       └── conditions.json (23 conditions)
               │       └── red_flags.json (18 flags) + multilingual keywords
               │
               ├──► OllamaClient (app/core/llm.py)
               │       └── gemma4:e4b-it-q4_K_M (4B IT Q4, vision-capable)
               │       └── JSON Schema-enforced output
               │       └── System prompt: KB-grounded, image-led reasoning mode
               │
               ├──► SafetyEngine (app/services/safety.py)
               │       └── pre_check + post_check
               │       └── Forces RED on red-flag keyword match
               │
               ├──► EscalationBuilder (app/services/escalation.py)
               │       └── PHC-format WhatsApp handoff body
               │       └── wa.me deep-link + clipboard-copy path
               │       └── Ambulance # + transport ETA
               │
               └──► ReportLog (app/services/reports.py)
                       └── Append-only JSONL audit trail
```

### Request flow — `POST /api/v1/diagnose`

1. **Pre-check** — keyword red-flag scan on the symptom string. Independent of the LLM. Fires on en / hi / ta / ml variants.
2. **KB lookup** — ranks candidate conditions by symptom-keyword overlap (English + native scripts via `symptoms_local`).
3. **Prompt** built containing *only* those KB candidates plus the patient context, language directive, and (if image present) an "image is attached" clause.
4. **Gemma 4 call** — JSON-Schema-enforced. Output: up to 3 differentials, each with `condition` (English, must be from candidates), `confidence` (0.0–0.9), `reasoning`, `guideline_reference`, `recommendation`. Plus `triage_level`, `red_flags_detected`, `escalation_required`.
5. **Post-check** — re-runs the red-flag scan and **overrides triage to RED if any flag fired**, regardless of LLM confidence.
6. **RED-only enrichments** — attach `during_transport` protocol from the matched KB condition, `phc_thrombolysis_decision` if applicable, `folk_error_correction` if relevant phrases appear, and a structured `escalation` block (WhatsApp message body + `wa.me` URL + clipboard label).
7. **Audit log** — append the full response + inputs + timestamp to `data/reports/reports.jsonl`.

### Three load-bearing invariants

- **Grounded LLM** — the model must pick from KB candidates or return "No acute condition identified." It cannot invent conditions.
- **Safety can override LLM, never the reverse** — keyword red-flag forces RED even on LLM-GREEN. The decision to escalate is not actually made by the model.
- **Confidence cap 0.9** — enforced by the JSON Schema. The model literally cannot output higher.

---

## What's shipped

| Feature | Where |
|---|---|
| Voice input (en / hi / ta / ml) | Web Speech API in `demo/index.html` |
| Multilingual UI + Gemma localized output | `app/core/llm.py::_language_directive` + `I18N` dict |
| Multimodal image input (camera + gallery) | `app/core/llm.py` + `demo/index.html` (lifted from amd_hackathon) |
| KB-grounded differential + JSON Schema | `app/core/llm.py::DIAGNOSIS_SCHEMA` |
| Deterministic safety override (Layer 1 + 2) | `app/services/safety.py` |
| Tabbed RED card (Action / Transport / Escalate / Differential) | `demo/index.html::renderDiagnosis` |
| WhatsApp hub-group escalation (PHC format) | `app/services/escalation.py` |
| Clipboard "Copy to <group>" + wa.me deep-link | `demo/index.html::copyEscalation` |
| Ambulance # input → live-injected into message | `demo/index.html::updateAmbulance` |
| Transport ETA from configured distance | `app/services/escalation.py::_transport_eta_line` |
| Folk-remedy correction banner | `app/knowledge/data/conditions.json::folk_error_correction` |
| Thrombolysis decision criteria for hub | `conditions.json::acute_mi.phc_thrombolysis_decision` |
| Append-only audit log (JSONL, PHI-on-device) | `app/services/reports.py` + `/api/v1/reports` endpoints |
| 163-test suite + 31-vignette clinical eval | `tests/unit/`, `tests/integration/`, `tests/eval_cases.py` |
| Cloudflare-tunneled public demo URL | `triage.accurateai.org` (named tunnel) |

---

## Clinical advisor input

The product was reviewed in two sessions with **Hari Subscini**, a practising clinician who routinely refers from PHCs to tertiary care in India. Three "confusion zones" — where the CHW gets stuck and decision support is most valuable — shaped the W3-F5 scope:

1. **ECG / thrombolysis decision.** Thrombolysis at PHC level requires monitor + ventilator + defibrillator that won't be available — so the system identifies likely STEMI findings on an attached ECG photo, prepares the preliminary protocol (venflon + aspirin 325 + clopidogrel 300 + atorvastatin 80), and defers the lytics decision to the hub physician with the eligibility + contraindications written into the during-transport block.
2. **Skin lesions.** *"Skin lesions need a definite diagnosis than a probable one. Should narrow down to single diagnosis and few differentials."* Added cellulitis, cutaneous abscess, eczema/contact dermatitis, tinea, and tetanus-prone wounds to the KB. The system prompt instructs the model to cap dermatology confidence at 0.7 and recommend specialist photo-referral. A compressed 8B Q4 model is not a dermatologist.
3. **Unconscious patient, no history.** *"This tool is not useful if we don't know what happened, the patient just fell down."* The `rf_unconscious_no_history` red flag forces RED, and the prompt routes the model into image-led reasoning mode — describe pupils / wound / container label / ECG features as a substitute for the verbal history that isn't available.

The advisor also validated the project scope and explicitly named image attachment as the critical addition: *"I attach the image. Some of it missed it. I'll add that."* That single line drove W3-F2 (multimodal image input).

The PHC workflow the tool sits inside, per Hari: preliminary treatment → ambulance with assigned number → intimate the tertiary centre via WhatsApp group → tracking → documentation. We cover all of it except live GPS tracking, which is V2.

---

## Evaluation

A 31-vignette synthetic eval suite covers every TAI-VADE category plus high-yield mimics. Each vignette has a ground-truth triage level and condition.

**Current results (`gemma4:e4b-it-q4_K_M`):** 29/31 pass (93.5%), sensitivity 21/21 (100%), specificity 8/10 (80%). All failures are over-triage.

**Bake-off (2026-05-15)** validated that the architectural safety claim is model-independent:

| Model | Pass | Sensitivity | Specificity |
|---|---|---|---|
| gemma4:e4b-it-q4_K_M | 29/31 (93.5%) | 21/21 (100%) | 8/10 (80%) |
| amsaravi/medgemma-4b-it:q8 | 24/31 (77.4%) | 21/21 (100%) | 8/10 (80%) |
| alibayram/medgemma:4b | 28/31 (90.3%) | 21/21 (100%) | 8/10 (80%) |

All three score **100% sensitivity** — every RED case is caught regardless of which LLM is in the middle. The diagnosis-name match differs by model; the escalation decision does not.

---

## Tech stack

| Layer | What we used | Why |
|---|---|---|
| Frontend | Single-file HTML + vanilla JS (`demo/index.html`) | No build step. Works offline. Same file is the entire UI surface. |
| Voice in | Web Speech API | Built into Chrome/Safari. Supports en-IN, hi-IN, ta-IN, ml-IN out of the box. |
| Backend | Python 3.12 + FastAPI + uvicorn | Async; trivial to mock for tests; common in clinical-research stacks. |
| LLM runtime | Ollama 2026.5 | Single-binary, runs offline, supports multimodal models, simple HTTP API. |
| Model | `gemma4:e4b-it-q4_K_M` | Google's compressed Gemma 4 "e4b" — 8B weights, sub-4B inference footprint, Q4_K_M (~9.6 GB on disk), vision-capable, ~5-9s/call on M-series GPU. |
| KB | JSON files in `app/knowledge/data/` | Editable by hand, version-controlled, no DB. |
| Safety | Deterministic Python rule engine | Independent of the model; auditable. |
| Audit log | Append-only JSONL (`data/reports/reports.jsonl`) | POSIX atomic-append; no DB; PHI stays on the same device that delivers care. |
| Dependency manager | `uv` | Fast, lockfile-driven. |
| Live demo | Cloudflared named tunnel → `triage.accurateai.org` | Public URL, no IP exposure. Architecture is offline; tunnel is demo affordance only. |

---

## Getting started

### Prereqs

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)
- [Ollama](https://ollama.com)

### Run locally

```bash
ollama pull gemma4:e4b-it-q4_K_M           # ~9.6 GB, one-time
git clone https://github.com/SankarSubbayya/sentinel-health.git
cd sentinel-health
uv sync
uv run uvicorn main:app --reload           # http://localhost:8000/demo
```

### Verifiable-offline

```bash
# Disconnect from internet, then:
uv run uvicorn main:app
curl -X POST http://localhost:8000/api/v1/diagnose \
    -H 'Content-Type: application/json' \
    -d '{"symptoms":"55-year-old with crushing chest pain and sweating"}'
# Works. No cloud call.
```

### Run the 31-case eval

```bash
uv run python -m tests.eval_cases --save
```

### Optional `.env`

```ini
OLLAMA_MODEL=gemma4:e4b-it-q4_K_M
HUB_PHYSICIAN_PHONE=+91...
HUB_PHYSICIAN_NAME=Dr. Hari
HUB_GROUP_NAME=TVMCH Cardiology Hub and Spoke
FACILITY_NAME=PHC Anaikatti
CHW_NAME=Lakshmi
NEAREST_HUB_KM=18
AVG_AMBULANCE_KMH=50
REPORTS_ENABLED=true
```

---

## File structure

```
sentinel-health/
├── main.py                              # FastAPI entry
├── app/
│   ├── api/routes.py                    # HTTP endpoints
│   ├── core/
│   │   ├── llm.py                       # Ollama client + JSON schemas + prompts
│   │   └── config.py                    # Pydantic settings
│   ├── services/
│   │   ├── diagnosis.py                 # Orchestrator
│   │   ├── safety.py                    # Red-flag override engine
│   │   ├── escalation.py                # WhatsApp handoff builder
│   │   └── reports.py                   # JSONL audit log
│   └── knowledge/
│       ├── loader.py                    # KB load + multilingual keyword match
│       └── data/
│           ├── conditions.json          # 23 conditions
│           ├── red_flags.json           # 18 red flags (en/hi/ta/ml)
│           └── triage_rules.json
├── demo/index.html                      # Single-file demo UI
├── tests/
│   ├── unit/                            # Pure logic
│   ├── integration/                     # FastAPI routes
│   ├── eval_cases.py                    # 31-vignette clinical eval
│   └── cases/                           # Vignette data
├── scripts/
│   ├── deploy.sh                        # Cloud Run deploy (GPU or --cpu)
│   ├── eval_bakeoff.sh                  # Multi-model eval comparison
│   └── start.sh                         # Cloud Run container entrypoint
├── Dockerfile                           # Bundled Ollama + Gemma 4 + FastAPI
├── KAGGLE_WRITEUP.md
├── DEMO_SCRIPT.md
├── README.md
├── CLAUDE.md                            # Project guidance for agent runs
└── SENTINEL_HEALTH.md                   # This file
```

---

## Safety & compliance posture

### Hackathon MVP

- No real patient data — synthetic test cases only.
- Persistent in-app disclaimer: *"Triage support only. Not a substitute for clinical judgment."*
- Safety override forces RED on time-critical keywords regardless of LLM confidence.
- Escalation is CHW-in-the-loop — the system prepares the message; the human commits.
- PHI (symptoms + patient context + attached image) lives on the same device that delivers care; can be disabled with `REPORTS_ENABLED=false` for the cloud demo so PHI doesn't land on the tunnel host.

### Production roadmap

- DPDP Act 2023 (India) compliance audit for PHI handling.
- Bias mitigation testing across language / region / age cohorts.
- Licensed-physician validation on a real (not synthetic) vignette dataset.
- Regulatory pathway (India MoHFW digital-health framework).
- Closed-loop ambulance tracking (live GPS).
- Per-facility hub routing (currently single global hub).
- Per-condition fine-tuning (the amd_hackathon SCIN-LoRA pattern, for dermatology specifically).

---

## Roadmap

### ✅ Phase 1 — Hackathon MVP (Apr–May 2026)

- ✅ FastAPI backend with Gemma 4 via Ollama
- ✅ Voice input (Web Speech API)
- ✅ KB-grounded differential with JSON-Schema enforcement
- ✅ Deterministic safety override engine
- ✅ WhatsApp hub-group escalation (PHC format)
- ✅ Multimodal image input (camera + gallery)
- ✅ Multilingual (en / hi / ta / ml) — UI + voice + Gemma output
- ✅ Tabbed RED card (Action / Transport / Escalate / Differential)
- ✅ Ambulance # input + transport ETA
- ✅ Append-only audit log
- ✅ Clinical advisor review (Hari Subscini)
- ✅ 31-vignette eval — 100% sensitivity, 80% specificity
- ✅ Live demo URL (Cloudflare named tunnel)
- ⏳ Demo video (3 min) — script ready
- ⏳ Kaggle submission

### Phase 2 — Pilot (Q3–Q4 2026)

- Physician validation against real vignette dataset
- Closed-loop ambulance tracking
- Per-facility hub routing
- DPDP compliance audit
- Hindi/Tamil/Malayalam KB translations for `during_transport` and `recommendation` fields (currently English-only in the KB)
- Beta deployment at pilot PHC

### Phase 3 — Scale (2027+)

- Multi-spoke / multi-hub deployment
- Domain-specific LoRA fine-tunes (dermatology, ECG)
- Integration with state EHR systems
- Outcome tracking + bias auditing
- Regulatory submission

---

## Contact

**Lead:** Sankar
**Email:** sankara68@gmail.com
**Clinical advisor:** Hari Subscini

---

*Last updated: May 15, 2026 — post W3-F8.*
