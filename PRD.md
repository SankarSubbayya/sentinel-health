# Sentinel Health — Product Requirements Document

**Version:** 0.2 (post-clinician review)
**Last updated:** 2026-04-28
**Owner:** Sankar
**Clinical advisor:** "Mama" (practising clinician, India) — joined as hackathon team member 2026-04-28
**Submission deadline:** 2026-05-18, 11:59 PM UTC (20 days)

---

## 1. Overview

Sentinel Health is an **offline-first, voice-enabled triage net for the five grassroots emergencies** — Trauma, Poisoning, Snake Bite, MI (heart attack), and Stroke. It runs **entirely on a clinic laptop** via Gemma 4 + Ollama (no cloud), grounds every recommendation in published guidelines, and uses a deterministic safety layer to flag time-critical conditions independently of the LLM.

It is **decision support for the spoke** in a hub-and-spoke healthcare network — designed to help a community health worker (CHW) or rural clinician decide *treat-here vs. escalate-to-hub* in seconds, even with no internet.

**Hackathon target:** Gemma 4 Good Hackathon — Main Track + Health & Sciences Impact + Ollama Special Tech. Total upside: $60,000.

---

## 2. Problem

In the regions where most preventable deaths happen, primary care is delivered by **CHWs and generalists, not specialists**. They face four compounding problems:

1. **Internet unavailability.** Cloud-based AI is a non-starter at the village clinic.
2. **Reference inaccessibility.** Paper guidelines are outdated or absent; specialist consult is hours away.
3. **Triage burden.** A CHW seeing 20 patients/day cannot be expert across cardiology, neurology, toxicology, trauma.
4. **Missed red flags.** Time-critical conditions (MI, Stroke, sepsis, snake-bite envenomation) get misclassified as benign — delayed escalation kills.

### 2.1 Hub-and-spoke positioning

| Network role | Reality on the ground | Sentinel Health's job |
|---|---|---|
| **Hub** = district / tertiary hospital — specialists, ICU, imaging | Hours away by ambulance | We don't replace it; we feed it the right patients faster |
| **Spoke** = PHC / village clinic / mobile CHW — limited tools, no internet | Patient's first contact | We sit here. Triage, escalate, and bridge the wait. |

**TAI-VADE alignment.** The Indian Ministry of Health's *Trauma & Accident Emergency Care Initiative* defines five grassroots emergencies that every PHC must triage and act on: **Trauma, Poisoning, Snake Bite, MI, Stroke.** Sentinel Health's primary scope is exactly this list — chosen because clinicians, regulators, and pilot clinics already recognize it.

Existing solutions either require internet (Ada, Babylon), aren't grounded in evidence (consumer chatbots), or require specialist training to use (UpToDate). **None work for a CHW with no internet, no specialist training, and a snake-bite patient already at the door.**

---

## 3. Target Users

### Primary: Maria — Community Health Worker
- Rural Uganda; 8th-grade education; intermediate English + Luganda
- Walks between villages with a tablet/laptop; no reliable connectivity
- Sees 15–25 patients/day; trained to take vitals + history, not diagnose
- **Need:** *"Tell me if this patient is in danger and what to do next."*

### Secondary: Dr. Asha — Solo Rural Physician
- District hospital, rural India; flaky internet
- Sees 60–80 patients/day across all ages and complaints
- Wants a sanity-check on differentials, latest guideline, drug interactions
- **Need:** *"I think this is X — am I missing something?"*

### Clinical Advisor: Mama
- Practising clinician (India); joined the project 2026-04-28
- Reviews KB content, validates triage decisions, advises on grassroots realities
- Strong principle: the app must be **supplementary, confirmatory, and avoid both over- and under-diagnosis**

---

## 4. Goals & Non-Goals

### Design Principles (from clinician review)
1. **Supplementary, not replacement.** *"No doctor can be replaced by an app."* The disclaimer is load-bearing, not decorative.
2. **Confirmatory, not informational.** Lead with **action** ("Refer to hospital NOW; give aspirin 325 mg if no allergy"), not menus of possibilities. ChatGPT-style "you could consider…" is a failure mode.
3. **Avoid both over- and under-diagnosis.** Track sensitivity AND specificity — neither alone is enough. Over-diagnosis floods the hub; under-diagnosis kills.
4. **History trumps tests.** Typical anginal pain → must escalate **even if** ECG, Echo, troponin are all normal (unstable angina). The app must encode this.
5. **Few smart questions.** A compounder won't ask the right 10 questions. Pick the one or two highest-yield discriminators per condition.
6. **Bridge the referral.** RED diagnoses must include a *during-transport* protocol (what drug, what monitoring, what to do if patient deteriorates).
7. **Clinical gestalt is irreplaceable.** Walking gait, skin turgor, "toxic look" — we explicitly cannot capture these. Out of scope, by design.

### Goals (MVP)
- Voice-first symptom intake (English; multilingual stretch)
- Differential diagnosis (top 3) with confidence (capped at 0.9), guideline citation, and **action-first recommendation**
- Hard red-flag rules that escalate independently of LLM confidence
- Runs **fully offline** on a clinic laptop (8 GB+ RAM, no GPU)
- Covers the **TAI-VADE 5 grassroots emergencies** (Trauma, Poisoning, Snake Bite, MI, Stroke) plus high-yield supporting conditions (DKA, hypoglycemia, sepsis, anaphylaxis, severe dehydration)
- Each high-urgency condition ships a **during-transport protocol**
- Hero scenario (chest-pain / atypical-angina) demonstrably bulletproof for the video
- Reports both **sensitivity** and **specificity** on the synthetic test set

### Non-Goals (MVP)
- Real patient data, EHR integration, HIPAA compliance
- Replacing clinical visual gestalt (face, gait, skin) — explicit out-of-scope
- Chronic disease longitudinal tracking
- Drug-interaction database (pharmacology stretch only)
- Native mobile app (web works; mobile is post-hackathon)
- Multimodal input (ECG image, dermatology image) — Phase 2
- WhatsApp / async-message integration with on-call rotation — Phase 2
- Physician-validated accuracy benchmarks (synthetic test cases only in MVP; clinician spot-review in Week 3)

---

## 5. Success Metrics

### Hackathon (judged 2026-05-18)
| Metric | Target |
|---|---|
| Submission complete (writeup + video + repo + live demo + cover) | 100% |
| Hero scenario works flawlessly on first try in video | Yes |
| Synthetic test cases passing | ≥ 27 / 30 (90%) |
| **Sensitivity** (RED cases caught) | ≥ 95% |
| **Specificity** (non-RED not over-escalated) | ≥ 80% |
| Demo runs offline (airplane mode shown on camera) | Yes |
| Video duration | ≤ 3:00 |
| Writeup word count | ≤ 1,500 |
| Clinical advisor (Mama) signs off on hero scenario | Yes |

### Product (post-hackathon)
- Time-to-triage decision: < 90 seconds from start of voice input
- Door-to-decision SLO at the spoke (operator-facing): ≤ 10 minutes for chest-pain (matches ECG SLO)
- Diagnostic accuracy (top-3 includes ground truth): ≥ 80%
- p95 inference latency on a clinic-class laptop: < 8 seconds

---

## 6. Hero Scenario (Video Demo)

> **Setting:** Rural clinic. Laptop on table. Phone shows "no service." Maria, the CHW, opens Sentinel Health.
>
> **Patient:** 60-year-old woman, diabetic. Chief complaint described by Maria via voice: *"Jaw pain, nausea, just feels exhausted, started one hour ago."* No chest pain. Past clinic visit had a normal ECG.
>
> **App responds (≤ 8 sec):**
> ```
> ⚠ ESCALATE NOW — possible Acute Coronary Syndrome (atypical)
>
> Action: Arrange immediate hospital transport. Aspirin 325 mg
>         chewed if no allergy. Document onset time. Continuous
>         vitals during transport.
>
> Why: Atypical anginal presentation in a diabetic woman.
>      A normal prior ECG does NOT rule out unstable angina —
>      history of typical anginal symptoms warrants urgent angiography
>      per ACC/AHA 2023.
>
> During transport: monitor BP / HR / SpO2. If chest pain
>                   develops, give second aspirin if available.
>                   Do NOT give nitrates if SBP < 90.
>
> Differentials (capped 0.9):
>   1. ACS — 0.85
>   2. Pulmonary Embolism — 0.10
>   3. GERD — 0.05
> ```
>
> **Closing shot:** Network panel — no requests leave the laptop.

This scenario showcases three of the doctor's principles at once: history-trumps-tests, action-first, during-transport bridging.

---

## 7. User Flows

### 7.1 Primary flow: Triage a new patient
1. Open app → "New patient"
2. Tap mic → speak chief complaint + history
3. App transcribes (Web Speech API), shows text for confirmation
4. App asks **at most 1–2 high-yield clarifying questions** (e.g., "Is the chest pain pressure-like and worse with exertion?")
5. App returns: **action header**, then top differentials, citations, and *during-transport protocol* if RED
6. Worker can: save note, print, mark for follow-up

### 7.2 Supporting flows
- **Review past notes** (local SQLite, no sync)
- **Look up a condition** (browse KB without a patient context)
- **Snake-bite folk-error correction:** if user mentions "tied a rope" / "tourniquet", app shows correction protocol on top
- **Settings:** language, model size (e2b/e4b), disclaimer reset

---

## 8. Functional Requirements

| ID | Requirement | Priority |
|---|---|---|
| F-1 | Voice input via Web Speech API (browser-native) | P0 |
| F-2 | Text input fallback (always available) | P0 |
| F-3 | Multi-turn clarifying questions, capped at 2 rounds | P0 |
| F-4 | Top-3 differential diagnosis with confidence ≤ 0.9 | P0 |
| F-5 | **Action-first** recommendation (single sentence at top of response) | P0 |
| F-6 | Citation per diagnosis (KB source + section) | P0 |
| F-7 | Red-flag rules engine (deterministic, runs alongside LLM) | P0 |
| F-8 | **Anginal-pain history rule** — typical angina → RED even with normal tests | P0 |
| F-9 | **During-transport protocol** for every RED-eligible condition | P0 |
| F-10 | Snake-bite folk-error counter-instruction | P0 |
| F-11 | Offline operation (verifiable: airplane mode works) | P0 |
| F-12 | Persistent disclaimer ("triage support, not diagnosis") | P0 |
| F-13 | Eval reports sensitivity AND specificity, not just pass rate | P0 |
| F-14 | Local note storage (SQLite) | P1 |
| F-15 | Print / export note as PDF | P1 |
| F-16 | KB browser (read conditions without patient context) | P2 |
| F-17 | Multilingual voice input (es, fr, hi, sw stretch) | P2 |
| F-18 | Async / WhatsApp integration with on-call rotation | P3 (Phase 2) |
| F-19 | Auto-escalation timer (e.g., 10-min ECG SLO) | P3 (Phase 2) |
| F-20 | Image input (ECG, skin lesion) | P3 (Phase 2) |

---

## 9. Technical Architecture

```
┌─────────────────────────────────────────────────┐
│ Browser (Chromium / Safari)                     │
│  • Web Speech API (STT, TTS optional)           │
│  • Single-page web app                          │
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
│ gemma4:e4b-it-q4_K_M│    │ • conditions.json     │
│ ~3GB, runs on CPU   │    │ • red_flags.json      │
└─────────────────────┘    │ • triage_rules.json   │
                           │ • transport_protocols │
                           │ • safety.py rules     │
                           └──────────────────────┘
```

### Key technical choices

**Model: `gemma4:e4b-it-q4_K_M`** — 4B-class instruction-tuned, Q4 quantized → ~3 GB on disk, runs on CPU. Sufficient for KB-grounded reasoning (we don't ask it to recall medical facts; we feed it the KB).

**Why web, not mobile** — fastest path to a public live-demo URL; Web Speech API is free; offline story still credible because Gemma 4 runs locally.

**Why hybrid LLM + rule engine** — LLM produces structured differentials; deterministic rules enforce RED escalation regardless of LLM confidence. **Specifically required by the doctor's "no over- and no under-diagnosis" principle**: the rule engine bounds the LLM in both directions.

**Prompting strategy** — KB-grounded, JSON-Schema-enforced output (Ollama `format` parameter), temperature 0.2 (consistency over creativity), short prompts that lead the model to *action* not *commentary*.

---

## 10. Knowledge Base Scope

### 10.1 Primary scope — TAI-VADE 5 grassroots emergencies (P0)

| # | Condition family | Specific entries (MVP) | Source |
|---|---|---|---|
| 1 | **Trauma** | Multi-system trauma, head injury w/ GCS drop, major fracture w/ shock, penetrating injury | ATLS 10th, WHO Trauma Care Checklist |
| 2 | **Poisoning** | Organophosphate (pesticide), paracetamol overdose, accidental child ingestion, alcohol/methanol | WHO Poisons Centres, AAPCC |
| 3 | **Snake Bite** | Hemotoxic envenomation, neurotoxic envenomation, dry bite | WHO Snake Bite Mgmt 2017, ICMR India |
| 4 | **MI** | ACS (typical), **atypical / unstable angina with normal tests**, acute MI (STEMI) | 2023 ACC/AHA Chest Pain Guideline |
| 5 | **Stroke** | Acute ischemic stroke, hemorrhagic stroke (suspected) | AHA/ASA 2023 |

Every condition in this group ships:
- A **history-driven trigger** (not just keyword-driven)
- An **action-first recommendation**
- A **during-transport protocol** (what to do in the ambulance)
- For snake bite specifically: a **folk-error counter-instruction** ("DO NOT apply tourniquet — instead immobilize the limb, keep below heart level…")

### 10.2 Supporting scope — high-yield co-presentations (P0)

These overlap symptomatically with the Big 5 and must be in the differential:

| Family | Conditions |
|---|---|
| **Cardiology / Vascular** | Hypertensive crisis, hypertensive encephalopathy, pulmonary embolism, heart failure exacerbation |
| **Diabetes / Metabolic** | DKA, hypoglycemia, hyperglycemic crisis (HHS) |
| **Acute illness** | Sepsis, severe dehydration, pneumonia, anaphylaxis |
| **Benign-but-common** | Common cold, influenza (so the app doesn't over-escalate every fever) |

### 10.3 Out of KB scope (MVP)
- Pediatrics (different vitals norms — needs separate model)
- Obstetrics (separate clinical pathways)
- Mental health emergencies
- Anything requiring physical exam findings the CHW can't reliably elicit

All sources are **public/open**. Citations include source + section so the user can verify offline (KB ships with the app).

---

## 11. Safety & Trust

### 11.1 The four hard rules
1. **Persistent disclaimer.** *"Triage support only. Not a substitute for clinical judgment. In emergencies, escalate immediately."* Visible on every screen.
2. **Confidence cap at 0.9.** We never claim diagnostic certainty.
3. **Deterministic red-flag rules trigger BEFORE the LLM response is shown** — even if the LLM disagrees.
4. **No outbound network requests during diagnosis** — verifiable by judge in DevTools / `tcpdump`.

### 11.2 Anti-failure-mode design (per clinician review)
- **Anti-under-diagnosis:** rule engine fires on red-flag keywords; **anginal-pain history rule** fires even when no other red flag is present; sensitivity is reported separately.
- **Anti-over-diagnosis:** specificity is reported separately; rule engine doesn't escalate on benign keywords (cough, runny nose, mild fever); LLM temperature low.
- **Anti-"information dump":** response always opens with a single-sentence action header; differentials are *evidence*, not the headline.
- **Anti-folk-error:** known dangerous folk practices (tourniquet for snake bite, induced vomiting for caustic ingestion, etc.) trigger explicit counter-instruction.

### 11.3 What we explicitly do not promise
- We do not capture the patient's gait, face, skin turgor, or other gestalt findings — out of scope.
- We do not replace specialist judgment for ambiguous cases — the design is "always-escalate-when-uncertain".
- We do not provide pediatric or obstetric triage.

---

## 12. Prize Track Alignment

| Track | How we win |
|---|---|
| **Main ($50k)** | Vision (TAI-VADE-aligned grassroots safety net) + execution (working offline) + story (Maria + Mama) |
| **Health & Sciences ($10k)** | Direct: democratizes specialist knowledge for primary care; clinician-validated |
| **Ollama Special ($10k)** | Best Gemma 4 deployment via Ollama; 100% local; verifiable offline |

The video must explicitly show:
1. Real medical use case with clear stakes (atypical-angina hero, then snake-bite second example)
2. Voice → action → escalation, in under 30 seconds of screen time
3. Network disconnect / airplane mode
4. `ollama list` showing local Gemma 4
5. Clinician advisor (Mama) on screen briefly endorsing the approach

---

## 13. Timeline (3 weeks → 20 days remaining)

### ✅ Week 1 — Apr 27 – May 3: Core engine end-to-end
- [x] Pull `gemma4:e4b-it-q4_K_M` and validate locally
- [x] Wire Ollama into `app/services/diagnosis.py`
- [x] Define structured-output prompts (JSON Schema enforced)
- [x] Build 20 synthetic test cases (cardiology, diabetes, general acute)
- [x] **Pass ≥ 18 / 20 → achieved 18 / 20 (90%) on 2026-04-27**
- [ ] **Expand KB with TAI-VADE 5: Trauma, Poisoning, Snake Bite (MI + Stroke already in)**
- [ ] **Add anginal-pain history rule to red_flags.json**
- [ ] **Add `during_transport` field to all RED-eligible conditions**
- [ ] **Add 10 new test cases (TAI-VADE-aligned)**
- [ ] **Update eval harness to report sensitivity / specificity**

### Week 2 — May 4 – May 10: Web app + voice
- [ ] Build SPA frontend (chat UI + red-flag banner + action header)
- [ ] Web Speech API integration (STT)
- [ ] Multi-turn clarifying questions (max 2 rounds)
- [ ] Citation rendering with KB drill-down
- [ ] Snake-bite folk-error detection in UI flow
- [ ] SQLite-WASM local note storage
- [ ] End-to-end test: voice → action → escalation, fully offline

### Week 3 — May 11 – May 17: Demo + writeup + submit
- [ ] Clinician (Mama) reviews hero scenario; sign-off
- [ ] Record video (script Mon, shoot Tue/Wed, edit Thu)
- [ ] Kaggle writeup (≤ 1,500 words)
- [ ] Deploy live demo: hosted web URL + downloadable Docker image
- [ ] Cover image + media gallery
- [ ] Buffer day (May 17) — full submission flow rehearsal
- [ ] Submit before May 18, 11:59 PM UTC

---

## 14. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| `e4b-it-q4` not capable enough for atypical-angina reasoning | Medium | High | History-trigger rule encoded deterministically (doesn't depend on LLM); fallback to `e4b-it-q8` |
| Snake-bite / poisoning KB is shallow without expert input | High | Medium | Mama reviews KB entries Week 1–2; cite WHO/ICMR sources |
| Web Speech API flaky / browser-specific | Medium | Medium | Always offer text input fallback; demo in Chrome |
| Live demo deployment hard (Ollama is local) | High | Medium | Hosted web URL with Ollama-in-container + downloadable image |
| Sens/spec trade-off — over-escalation kills specificity | Medium | High | Tune rule keywords with mama's input; report both metrics; aim for sens ≥ 95%, spec ≥ 80% |
| Video production overrun | Medium | High | Script day 1, shoot day 2, edit day 3; keep hero scenario tight |
| Scope creep beyond TAI-VADE 5 | Medium | High | Hold the line. Pediatric/OB/mental health are explicitly out. |

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
- Multimodal input (ECG image, dermatology image)
- Pediatric triage (different vitals norms)
- Obstetric triage
- Mental health emergencies
- WhatsApp / async-message integration with on-call rotation
- Auto-escalation timers and on-call duty rotation
- Replacing clinical visual gestalt (face, gait, skin) — explicit
- Fine-tuning Gemma 4 (use base instruct + KB grounding only)

---

## 16. Open Questions

1. **TAI-VADE acronym expansion** — confirm the full expansion with Mama before using it in the writeup. Five-pillar framework is solid regardless.
2. Live demo hosting — Fly.io / Render / Railway with Ollama-in-container?
3. TTS — speak diagnoses back, or keep text-only? (lean: text-only for MVP)
4. Multilingual stretch — pick one language to demo (Hindi feels right given Mama's involvement) for emotional weight.
5. Should snake-bite folk-error correction also handle local-language idioms ("tied a string") or stay English-only?
6. License choice for the public repo (MIT / Apache 2.0 / AGPL)?
7. Do we want a brief "endorsed by practising clinician" line in the writeup, or stay anonymous on Mama's request?

---

*End of PRD v0.2 — incorporates clinician feedback session 2026-04-28*
