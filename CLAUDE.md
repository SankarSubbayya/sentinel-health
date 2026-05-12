# CLAUDE.md

Project guidance for Claude Code when working in this repo.

## What this is

**Sentinel Health** — an offline-first clinical decision support web app for community health workers (CHWs) in low-resource settings. Built for the **Gemma 4 Good Hackathon** (Google DeepMind / Kaggle, 2026). Scoped to the five TAI-VADE grassroots emergencies (Trauma, Poisoning, Snake Bite, MI, Stroke) plus high-yield mimics (DKA, hypoglycemia, sepsis, anaphylaxis, severe dehydration).

The product posture is **decision support, not diagnosis** — same legal posture as UpToDate. The persistent in-app disclaimer is load-bearing.

## Architecture

```
Browser (demo/index.html, Web Speech API)
        │   HTTP/JSON
        ▼
FastAPI app (main.py → app/api/routes.py)
        │
        ├──► app/services/diagnosis.py   (orchestrator)
        │           │
        │           ├──► app/knowledge/loader.py   (KB keyword match)
        │           │       └── app/knowledge/data/*.json  (conditions, red_flags, triage_rules)
        │           │
        │           ├──► app/core/llm.py           (Ollama client + JSON-Schema-enforced prompts)
        │           │       └── Gemma 4 via Ollama (local, CPU)
        │           │
        │           ├──► app/services/safety.py    (deterministic red-flag override → RED)
        │           │
        │           └──► app/services/escalation.py (WhatsApp hub-physician handoff, RED only)
        │
        └──► app/core/config.py   (env-driven settings)
```

### Request flow (`POST /api/v1/diagnose`)
1. `pre_check` — keyword red-flag scan (Layer 1 safety, no LLM).
2. KB lookup picks top-N candidate conditions by symptom-keyword overlap.
3. LLM prompt is built with **KB-grounded candidates only**; Gemma 4 is called with a strict JSON Schema (`DIAGNOSIS_SCHEMA`) — confidence capped at 0.9, conditions must come from the candidate list, falls back to "No acute condition identified" if none match.
4. `post_check` — if any red flag fired, override LLM triage to RED regardless of LLM confidence (Layer 2 safety).
5. For RED triage, attach `during_transport` protocol from KB; for folk-error phrases (tourniquet on snake bite, etc.), attach `folk_error_correction`; build a WhatsApp `escalation` block (recipient, text, `wa.me` deep-link) for the hub-physician handoff.

### Key invariants
- **LLM is grounded, never free**: it picks from KB candidates; it does not invent conditions.
- **Safety engine can override LLM, never the reverse**: a keyword red-flag forces RED even if the LLM said GREEN.
- **Confidence cap 0.9**: enforced by JSON Schema.
- **`/healthz` does NOT touch Ollama**; `/health` does.
- **Escalation is CHW-in-the-loop, never auto-send**: the server returns a `wa.me` URL with the message pre-filled; the CHW reviews and taps Send from their own phone. No Twilio / Meta API calls — preserves the offline-first posture.

## Layout

| Path | Purpose |
|---|---|
| `main.py` | FastAPI entry, mounts router, serves `/demo` |
| `app/api/routes.py` | HTTP endpoints (`/diagnose`, `/clarify`, `/triage`, `/kb/*`, `/health`, `/healthz`) |
| `app/services/diagnosis.py` | Orchestrator (KB + LLM + safety) |
| `app/services/safety.py` | Pre/post red-flag override engine |
| `app/services/escalation.py` | Builds the WhatsApp hub handoff message + `wa.me` link (RED only) |
| `app/core/llm.py` | Ollama client, system prompts, JSON schemas |
| `app/core/config.py` | Pydantic settings (env-driven) |
| `app/knowledge/loader.py` | KB load + keyword matching |
| `app/knowledge/data/*.json` | Conditions, red flags, triage rules |
| `demo/index.html` | Single-file demo UI (voice in, past-patients panel) |
| `tests/unit/`, `tests/integration/`, `tests/eval_cases.py` | Unit, API, and 31-vignette eval suite |

## Run

```bash
ollama pull gemma4:e4b-it-q4_K_M
uv sync
uv run uvicorn main:app --reload     # → http://localhost:8000/demo
uv run python -m tests.eval_cases --save   # current: 30/31 (96.8%), sensitivity 100%
```

## Conventions when editing

- **Don't bypass safety**: never let LLM output flow back to the client without `safety_engine.post_check`.
- **Don't widen the KB silently**: new conditions go in `app/knowledge/data/conditions.json` with `symptoms`, `guideline`, `urgency`, and (for RED) `during_transport`. Add a matching eval case.
- **Keep `/healthz` cheap**: it's the liveness probe, no external calls.
- **Module docstrings are one line** (W2-P3 convention, see recent commits).
- **Demo fonts must be system-stack** (W2-P1): no Google Fonts / CDN — the whole point is offline.
- **Tests**: `tests/unit` for pure logic, `tests/integration` for FastAPI routes (httpx + mocked Ollama where needed), `tests/eval_cases.py` for the 20 synthetic vignettes.
- **Escalation config** (env): `HUB_PHYSICIAN_PHONE`, `HUB_PHYSICIAN_NAME`, `FACILITY_NAME`. Empty phone → `wa.me` contact picker; the feature still works with no config.

## Hackathon docs

- `README.md` — pitch and quick start
- `PRD.md` — full product requirements
- `SENTINEL_HEALTH.md` — clinical / architectural design
- `HACKATHON.md` — Kaggle hackathon rules
- `.rocketride/docs/` — RocketRide pipeline docs (read these before any RocketRide work, per `.claude/rules/rocketride.md`)
