# Sentinel Health — Product Requirements Document

**Version:** 0.1 (Hackathon MVP)
**Last updated:** 2026-04-27
**Owner:** Sankar
**Submission deadline:** 2026-05-18, 11:59 PM UTC (21 days)

---

## 1. Overview

Sentinel Health is an **offline-first, voice-enabled clinical decision support web app** that helps community health workers (CHWs) and rural clinicians triage patients in low-resource, low-connectivity settings. It runs **entirely on a local laptop** — Gemma 4 inference happens on-device via Ollama, with no cloud calls — and grounds every recommendation in published medical guidelines plus an explicit safety layer that flags emergencies.

**Hackathon target:** Gemma 4 Good Hackathon — Main Track + Health & Sciences Impact + Ollama Special Tech.

---

## 2. Problem

In the regions where most preventable deaths happen, the healthcare workforce is **CHWs and generalist clinicians, not specialists**. They face four compounding problems:

1. **Internet unavailability.** Cloud-based AI is a non-starter at the village clinic.
2. **Reference inaccessibility.** Paper guidelines are outdated or absent; specialist consult is hours away.
3. **Triage burden.** A CHW seeing 20 patients/day can't be expert at cardiology, endocrinology, and acute care.
4. **Missed red flags.** Time-critical conditions (ACS, DKA, sepsis) get misclassified as benign — delayed escalation kills.

Existing solutions either require internet (Ada, Babylon), aren't grounded in evidence (consumer chatbots), or require specialist training to use (UpToDate). **None work for a CHW with no internet and no specialist training.**

---

## 3. Target Users

### Primary: Maria — Community Health Worker
- Rural Uganda; 8th-grade education; intermediate English + Luganda
- Walks between villages with a tablet/laptop; no reliable connectivity
- Sees 15–25 patients/day; trained to take vitals + history, not diagnose
- **Need:** "Tell me if this patient is in danger and what to do next."

### Secondary: Dr. Asha — Solo Rural Physician
- District hospital, rural India; flaky internet
- Sees 60–80 patients/day across all ages and complaints
- Wants a sanity check on differential, latest guideline, drug interactions
- **Need:** "I think this is X — am I missing something?"

---

## 4. Goals & Non-Goals

### Goals (MVP)
- Voice-first symptom intake; works in English (multilingual stretch)
- Differential diagnosis (top 3) with confidence scores and guideline citations
- Hard red-flag rules that escalate independently of LLM confidence
- Runs **fully offline** on a clinic laptop (8GB+ RAM, no GPU required)
- Covers three condition families: **cardiology, diabetes, general acute**
- Hero scenario (chest-pain / ACS) demonstrably bulletproof for the video
- Persistent local notes (SQLite); sync queue stub for future

### Non-Goals (MVP)
- Real patient data, EHR integration, HIPAA compliance
- Chronic disease longitudinal tracking
- Drug-interaction database (pharmacology stretch only)
- Native mobile app (web works; mobile is post-hackathon)
- Physician-validated accuracy benchmarks (synthetic test cases only)
- Multilingual UI beyond English (stretch goal if time allows)

---

## 5. Success Metrics

### Hackathon (judged 2026-05-18)
| Metric | Target |
|---|---|
| Submission complete (writeup + video + repo + live demo + cover) | 100% |
| Hero scenario works flawlessly on first try in video | Yes |
| Synthetic test cases passing | ≥ 18 / 20 |
| Demo runs offline (airplane mode shown on camera) | Yes |
| Video duration | ≤ 3:00 |
| Writeup word count | ≤ 1,500 |

### Product (post-hackathon)
- Time-to-triage decision: < 90 seconds from start of voice input
- Red-flag detection sensitivity on validation cases: ≥ 95%
- Diagnostic accuracy (top-3 includes ground truth): ≥ 80%
- p95 inference latency on a clinic-class laptop: < 8 seconds

---

## 6. Hero Scenario (Video Demo)

> **Setting:** Rural clinic. Laptop on table. Phone shows "no service." Maria, the CHW, opens Sentinel Health.
>
> **Patient:** 55-year-old man. Chief complaint described by Maria via voice: "Chest pain, shortness of breath, started two hours ago, sweating."
>
> **App responds (≤ 8 sec):**
> ```
> ⚠ RED FLAG: Possible Acute Coronary Syndrome
>
> Top differentials (confidence):
>   1. Acute Coronary Syndrome — 78%
>      → URGENT: arrange hospital transport now
>      → Citation: 2023 ACC/AHA Chest Pain Guideline §3.2
>   2. Pulmonary Embolism — 15%
>      → Ask: recent immobility? unilateral leg swelling?
>   3. GERD — 7%
>      → Less likely given diaphoresis + dyspnea
>
> Next steps: vitals (BP, HR, SpO2), aspirin 325mg if no allergy,
> document onset time, prepare transport.
> ```
>
> **Closing shot:** Network panel — no requests leave the laptop.

---

## 7. User Flows

### 7.1 Primary flow: Triage a new patient
1. Open app → "New patient" button
2. Tap mic → speak chief complaint + history
3. App transcribes (Web Speech API), shows text for confirmation
4. App may ask 1–3 clarifying questions (e.g., "How long?", "Pain radiates?")
5. App returns ranked differentials + red flags + next steps + citations
6. Worker can: save note, print, mark for follow-up

### 7.2 Supporting flows
- **Review past notes** (local SQLite, no sync)
- **Look up a condition** (browse KB without a patient context)
- **Settings:** language, model size (e2b/e4b), disclaimer reset

---

## 8. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| F-1 | Voice input via Web Speech API (browser-native) | P0 |
| F-2 | Text input fallback (always available) | P0 |
| F-3 | Multi-turn clarifying questions (up to 3 rounds) | P0 |
| F-4 | Top-3 differential diagnosis with confidence (0–100) | P0 |
| F-5 | Citation per diagnosis (KB source + section) | P0 |
| F-6 | Red-flag rules engine (deterministic, runs alongside LLM) | P0 |
| F-7 | Offline operation (verifiable: airplane mode works) | P0 |
| F-8 | Persistent disclaimer ("triage support, not diagnosis") | P0 |
| F-9 | Local note storage (SQLite) | P1 |
| F-10 | Print / export note as PDF | P1 |
| F-11 | KB browser (read conditions without patient context) | P2 |
| F-12 | Multilingual voice input (es, fr, hi, sw stretch) | P2 |

---

## 9. Technical Architecture

```
┌─────────────────────────────────────────────────┐
│ Browser (Chromium / Safari)                     │
│  • Web Speech API (STT, TTS optional)           │
│  • Single-page web app (vanilla JS or React)    │
│  • localStorage for session, SQLite via WASM    │
└──────────────────────┬──────────────────────────┘
                       │ HTTP (localhost:8000)
                       ▼
┌─────────────────────────────────────────────────┐
│ FastAPI backend (Python 3.12)                   │
│  • /diagnose — orchestrates LLM + KB + safety   │
│  • /clarify — generates follow-up questions     │
│  • /kb — read-only KB endpoints                 │
└─────────┬───────────────────────────┬───────────┘
          │                           │
          ▼                           ▼
┌─────────────────────┐    ┌──────────────────────┐
│ Ollama (localhost)  │    │ Knowledge + Safety    │
│ gemma4:e4b-it-q4    │    │ • conditions.json     │
│ (~3GB, runs on CPU) │    │ • red_flags.json      │
└─────────────────────┘    │ • triage_rules.json   │
                           │ • safety.py rules     │
                           └──────────────────────┘
```

### Key technical choices

**Model: `gemma4:e4b-it-q4`**
- 4B-class instruction-tuned, Q4 quantized → ~3GB on disk, ~5GB RAM at runtime
- Runs on any modern laptop without a GPU
- Sufficient for KB-grounded reasoning (we don't ask it to recall medical facts; we feed it the KB)

**Why web, not mobile**
- Faster to ship in 3 weeks
- Live demo URL satisfies hackathon requirement
- Browsers ship Web Speech API for free
- Offline story still credible: "Gemma 4 runs on this laptop, not in the cloud" — proven on camera

**Why hybrid LLM + rule engine**
- LLM provides reasoning + citation generation
- Rule engine enforces red-flag escalation **independently of LLM confidence**
- A misclassified ACS still trips the rule engine on chest pain + dyspnea + diaphoresis
- This is the "Safety & Trust" angle for the writeup

**Prompting strategy**
- KB-grounded: relevant condition entries injected into context
- Structured output: JSON schema for differentials + confidence + citation
- Few-shot examples for each condition family
- Temperature 0.2 (consistency over creativity)

---

## 10. Knowledge Base Scope

| Condition family | Conditions (MVP) | Source |
|---|---|---|
| **Cardiology** | ACS, hypertensive crisis, heart failure exacerbation | 2023 ACC/AHA, WHO PEN |
| **Diabetes** | DKA, hypoglycemia, hyperosmolar hyperglycemic state | ADA 2025 Standards |
| **General acute** | Sepsis, severe dehydration, asthma exacerbation, acute abdomen | WHO IMCI, IMAI |

All sources are **public/open**. Citations include source + section so the user can verify offline (KB shipped with app).

---

## 11. Safety & Trust

- Persistent footer: *"Triage support only. Not a substitute for clinical judgment. In emergencies, escalate immediately."*
- Red-flag rules trigger **before** the LLM response is shown — even if the LLM disagrees
- Confidence scores capped at 90% (we never claim diagnostic certainty)
- All outputs include: differential rank, confidence, citation, "what to ask next"
- No outbound network requests during diagnosis (verifiable by judge in DevTools)

---

## 12. Prize Track Alignment

| Track | How we win |
|---|---|
| **Main ($50k)** | Vision (CHWs everywhere) + execution (working offline) + story (Maria) |
| **Health & Sciences ($10k)** | Direct: democratizes specialist knowledge for primary care |
| **Ollama Special ($10k)** | Best Gemma 4 deployment via Ollama; 100% local; verifiable offline |

Total upside: **$60k.**

The video must explicitly show:
1. Real medical use case with stakes
2. Voice → diagnosis → red flag → action, in under 30 seconds of screen time
3. Network disconnect / airplane mode
4. `ollama list` output showing local Gemma 4

---

## 13. Timeline (3 weeks)

### Week 1 — Apr 27 – May 3: Core engine works end-to-end
- [ ] Pull `gemma4:e4b-it-q4` and validate it runs locally
- [ ] Wire Ollama into existing `app/services/diagnosis.py`
- [ ] Define structured-output prompts (differential JSON schema)
- [ ] Expand KB to cover all 3 condition families
- [ ] Build 20 synthetic test cases (cardiac, diabetes, general acute)
- [ ] Pass ≥ 18 / 20 on text-only input

### Week 2 — May 4 – May 10: Web app + voice
- [ ] Build SPA frontend (chat UI + red-flag banner)
- [ ] Web Speech API integration (STT in, optional TTS out)
- [ ] Multi-turn clarifying questions
- [ ] Citation rendering with KB drill-down
- [ ] SQLite-WASM local note storage
- [ ] End-to-end test: voice → diagnosis → red flag, fully offline

### Week 3 — May 11 – May 17: Demo + writeup + submit
- [ ] Record video (script Mon, shoot Tue/Wed, edit Thu)
- [ ] Kaggle writeup (≤ 1,500 words)
- [ ] Deploy live demo: hosted web URL + downloadable Docker image
- [ ] Cover image + media gallery
- [ ] Buffer day (May 17) — test full submission flow
- [ ] Submit before May 18, 11:59 PM UTC

---

## 14. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `e4b-it-q4` not capable enough for structured output | Medium | High | Heavy KB grounding; fall back to `e4b-it-q8` or `26b` cloud demo |
| Web Speech API flaky / browser-specific | Medium | Medium | Always offer text input fallback; demo in Chrome |
| Live demo deployment hard (Ollama is local) | High | Medium | Provide hosted web URL **+** Dockerfile for "true offline" reproduction |
| Test case construction takes longer than budgeted | Medium | High | Time-box to 1 day; reuse published clinical vignettes |
| Video production overrun | Medium | High | Scripted day 1, shot day 2, edited day 3 — no perfectionism |
| One condition family doesn't work well | Medium | Medium | Hero scenario is cardiac; demote diabetes/general to "also handles" |

---

## 15. Out of Scope (Explicit)

To prevent scope creep, these are **not in MVP**:

- Real EHR / HL7 / FHIR integration
- Multi-user accounts, auth, role-based access
- Server-side patient data persistence
- Chronic disease longitudinal tracking
- Drug-interaction checker
- Wearables / device integration
- Native mobile builds (Flutter/React Native)
- Multimodal input (X-ray, ECG image)
- Fine-tuning Gemma 4 (use base instruct + KB grounding only)

---

## 16. Open Questions

1. Live demo hosting — which provider? (Fly.io / Render / Railway with Ollama-in-container?)
2. TTS — speak the diagnosis back, or keep text-only? (lean: text-only for MVP)
3. Multilingual stretch — pick one language to demo (Swahili? Hindi? Spanish?) for emotional weight in video?
4. Do we want a "physician verified" disclaimer voiceover in the video, or skip the regulatory framing entirely?
5. License choice for the public repo (MIT / Apache 2.0 / AGPL)?

---

*End of PRD v0.1*
