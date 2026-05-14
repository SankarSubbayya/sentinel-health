# Sentinel Health

### An offline triage net for the five grassroots emergencies — built on Gemma 4 and Ollama

**Tracks:** Main Track · Health & Sciences Impact · Ollama Special Technology

**Code:** github.com/SankarSubbayya/sentinel-health · **Live demo:** https://triage.accurateai.org/demo

---

## The problem

Two billion people receive primary care from a community health worker (CHW), not a doctor. CHWs face chest pain, snake bites, sudden confusion, and pesticide ingestion every day — and most of them have no internet, no specialist within hours, and a paper guideline binder that is years out of date. The Indian Ministry of Health's **TAI-VADE** framework names five emergencies that account for the bulk of preventable mortality at the village level: **Trauma, Poisoning, Snake Bite, MI, and Stroke**. The common failure mode is not exotic disease — it is *under-triage of a time-critical condition that looked benign in the first 30 seconds*. Sentinel Health is built for those 30 seconds.

We treat this as a triage problem, not a diagnostic one. The legal and clinical posture is identical to UpToDate: a decision-support tool that supplements the clinician, never replaces them. The persistent in-app disclaimer is load-bearing.

## Architecture

The system runs entirely on a clinic laptop with no inbound network requirement:

```
Browser (voice in) → FastAPI → DiagnosisService
                                  ├─ KB keyword match (candidate conditions)
                                  ├─ Gemma 4 via Ollama (JSON-schema enforced)
                                  ├─ Safety engine (red-flag override → RED)
                                  └─ Escalation (WhatsApp wa.me deep-link, RED only)
```

A POST to `/api/v1/diagnose` runs five deterministic steps: keyword pre-check for red flags (Layer 1, no LLM); KB ranks candidate conditions by symptom overlap; a prompt is built with *only those candidates* and sent to Gemma 4; a post-check re-runs the red-flag scan and overrides triage to RED if any flag fired regardless of LLM confidence (Layer 2); on RED, the during-transport protocol and a `wa.me` WhatsApp handoff are attached.

Three load-bearing invariants: the LLM is *grounded* (must pick from candidates or return "No acute condition identified" — cannot invent); the safety engine can override the LLM but never the reverse; confidence is capped at 0.9 in the JSON Schema.

## How we used Gemma 4 specifically

The model is `gemma4:e4b-it-q4_K_M` — instruction-tuned 4B-parameter, Q4 quantized, served via Ollama. Three Gemma-specific design choices:

**JSON Schema enforcement.** Every diagnose call passes a strict `DIAGNOSIS_SCHEMA` to Ollama's `format` parameter — up to three differentials with confidence capped at 0.9, reasoning, guideline reference, recommendation. Structured output is the integration boundary, not a parsing fallback. Zero JSON-decoding failures across the eval suite.

**System prompt that rules out hallucination.** The prompt names the candidate-conditions list as the only valid source. If none fit, the model returns a fixed "No acute condition identified" object with triage GREEN. A freely-prompted Gemma will invent an MI to fill a slot; grounding cuts over-diagnosis dramatically.

**Multimodal image input.** Gemma 4 IT accepts images via Ollama's `images` field. A photo of a snake, ECG, wound, or container label flows in as additional clinical evidence — particularly load-bearing when the patient is unconscious and no verbal history is available.

**Local CPU inference.** Q4 gives ~5-second latency per call on a mid-range laptop CPU. Running locally is not a workaround; it is *the product*. The whole pitch falls apart if Gemma needs the internet.

## The safety layer and the WhatsApp handoff

The hardest part of building a clinical AI is not making it smart; it is making it *safe when it is wrong*. A 4B-parameter model will misclassify cases; the design question is what happens then.

Our answer: a deterministic safety engine that runs independently of the model. Keyword red-flag rules — "fang marks", "crushing chest pain", "facial droop", "pesticide", "unresponsive" — fire before *and* after the LLM call. If a flag fires, final triage is RED regardless of what the LLM said. The model can be wrong about differentials; it cannot be wrong about whether the patient gets escalated, because that decision isn't actually made by the model.

On RED, the system builds a `wa.me` deep-link with the safety reason, top differential, symptoms verbatim, patient context, during-transport protocol, and disclaimer for the receiving doctor. The CHW taps once; WhatsApp opens with the message pre-filled on their own phone; they review and send. App prepares, human commits. No Twilio, no Meta Business API, no auto-send liability. Delivery depends on the CHW's phone connectivity — the right place for that dependency to live.

## Evaluation

A 31-vignette synthetic eval suite covers every TAI-VADE category plus the high-yield mimics (DKA, hypoglycemia, sepsis, anaphylaxis, severe dehydration). **Results: 30/31 pass (96.8%), sensitivity 21/21 (100%), specificity 8/10 (80%).** The one failure is over-triage of benign palpitations — the right error to make. We track sensitivity and specificity separately and deliberately do not tune toward 31/31; the safety layer's job is to *fail loudly toward escalation*.

## Clinical advisor input

The product was reviewed with a practising clinician (Hari Subscini) who routinely refers from primary health centres (PHCs) to tertiary care in India. Three "confusion zones" — points where the CHW gets stuck and decision support is most valuable — emerged from that conversation and shape the current scope:

1. **ECG diagnosis and the thrombolysis decision.** "Should I thrombolyse?" is a clinician-level decision that requires monitor, ventilator, and defibrillator — equipment that won't be available at PHC level. Our response: the model identifies likely STEMI findings on an attached ECG photo and prepares the IV-cannula + loading-dose + ambulance protocol, but defers the lytics decision to the receiving hub physician. Thrombolysis eligibility and contraindications are written into the during-transport protocol as decision support for the hub, not a directive for the spoke.

2. **Skin lesions.** *"Skin lesions need a definite diagnosis than a probable one. So credibility and accuracy of skin lesions diagnosis need to be improved. It should narrow down to single diagnosis and few differentials."* We added cellulitis, cutaneous abscess, eczema/contact dermatitis, tinea, and tetanus-prone wounds to the KB so the multimodal pipeline has real candidates to ground in. The system prompt explicitly instructs the model to acknowledge dermatology uncertainty when image-led, cap confidence at 0.7 for skin lesions, and recommend specialist photo-referral. A 4B-parameter quantised model is not a dermatologist; honesty about that is the load-bearing design choice.

3. **The unconscious patient with no history.** *"This tool is not useful if we don't know what happened, the patient just fell down."* This is exactly the case where multimodal Gemma earns its keep — when the symptom narrative is empty, the image becomes the history. The `rf_unconscious_no_history` red flag forces RED triage and the system prompt routes the model into "image-led reasoning" mode: describe what you see (pupils, wound, container label, ECG features) as a substitute for the verbal history that isn't available.

The advisor also validated the project scope — the five TAI-VADE emergencies plus the high-yield mimics — and explicitly named image attachment as the critical addition: *"I attach the image. Some of it missed it. I'll add that."* We shipped W3-F2 (camera capture + multimodal Gemma) directly in response.

The conversation also surfaced the PHC workflow the tool should sit inside: ECG → preliminary treatment (venflon + loading doses) → ambulance with assigned number → intimate the tertiary centre via app → ambulance tracking from both ends → document what was done. We cover the *intimation* leg through the WhatsApp escalation and the *documentation* leg through the append-only audit log. Ambulance tracking and closed-loop follow-up are on the V2 roadmap, not in this submission.

## Challenges we hit

**Hallucination.** Early Gemma runs invented conditions to fill the slot — fixed by KB grounding and an explicit "return the default" rule. **Over-confidence** — fixed by hard-capping at 0.9 in the JSON Schema. **Folk-remedy harm** — snake-bite outcomes are often driven by tourniquets applied by family; a `folk_error_correction` field surfaces alongside the diagnosis whenever tourniquet/cut-and-suck/induced-vomiting phrases appear. **Escalation without internet** — replaced "Twilio + server + audit guarantees" with a `wa.me` deep-link: zero infrastructure, CHW-in-the-loop, offline-resilient.

## Why these choices

The dominant alternative — "send symptoms to a hosted Gemini/GPT endpoint" — fails the village clinic. Local Gemma 4 is the only choice that survives no-internet, no-rate-limit, no-PHI-leaving-the-laptop simultaneously. JSON-schema enforcement converts a chatty model into a programmable component. The deterministic safety layer is the load-bearing innovation: it answers "what happens when the AI is wrong about a 60-year-old's chest pain?"

## Tracks

We submit primarily to the **Main Track** (vision: democratizing decision support for the two billion people whose primary care is delivered by CHWs); to **Health & Sciences Impact** (direct clinical impact on time-critical conditions); and to **Ollama Special Technology** (a 100% local Gemma 4 deployment that is verifiable offline by disabling the laptop's network and re-running the suite). The video demo shows all three.

*Decision support tool. Not a diagnostic system. Always consult a qualified physician.*
