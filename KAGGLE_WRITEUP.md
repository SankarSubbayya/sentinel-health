# Sentinel Health

### An offline triage net for the five grassroots emergencies — built on Gemma 4 and Ollama

**Tracks:** Main Track · Health & Sciences Impact · Ollama Special Technology

**Code:** github.com/SankarSubbayya/sentinel-health · **Live demo:** `<cloud-run-url>/demo`

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

A POST to `/api/v1/diagnose` executes five deterministic steps. **(1)** A keyword pre-check scans the symptom string for red-flag terms (Layer 1 safety, no LLM). **(2)** The knowledge base — JSON files of WHO/CDC/ACC-grounded conditions — ranks candidate conditions by symptom-keyword overlap. **(3)** A prompt is built that contains *only those candidates* and is sent to Gemma 4. **(4)** A post-check re-runs the red-flag scan and overrides triage to RED if any flag fired, regardless of LLM confidence (Layer 2 safety). **(5)** On RED, the service attaches the during-transport protocol from the KB and builds a structured WhatsApp message with a `wa.me` deep-link so the CHW can hand off to the hub physician with one tap.

The architecture has three load-bearing invariants. The LLM is *grounded*, never free — it must select from KB candidates or return "No acute condition identified"; it cannot invent. The safety engine can override the LLM but never the reverse — a keyword red flag forces RED even on LLM-GREEN. Confidence is **capped at 0.9** in the JSON Schema — the model can never claim certainty.

## How we used Gemma 4 specifically

The model is `gemma4:e4b-it-q4_K_M` — the instruction-tuned 4B-parameter variant, Q4 quantized, served via Ollama. We made three Gemma-specific design choices:

**JSON Schema enforcement.** Every diagnosis call passes a strict `DIAGNOSIS_SCHEMA` to Ollama's `format` parameter. The schema requires up to three differentials, each with a condition string, a confidence float (max 0.9), reasoning, guideline reference, and recommendation. The schema is the contract: structured output is not a parsing fallback, it is the integration boundary. We saw zero JSON-decoding failures across the eval suite using this approach — Gemma's structured output is the load-bearing feature that makes the safety layer composable.

**System prompt that rules out hallucination.** The system prompt names the candidate-conditions list as the *only* source of valid diagnoses. If none plausibly fit, the model is instructed to return a specific "No acute condition identified" object with triage GREEN. We discovered early that a freely-prompted Gemma will helpfully invent an MI to fill a slot — grounding it with an explicit "do not invent, return the default" rule cut over-diagnosis dramatically.

**Local CPU inference.** Q4 quantization gives us ~5-second latency per diagnose call on a mid-range laptop CPU. That is well inside the clinical window for an unhurried CHW workflow. Running locally is not a workaround; it is the *product*. There is no cloud call, no API key, no rate limit, no downtime, no privacy compromise. The whole pitch falls apart if Gemma needs the internet.

## The safety layer and the WhatsApp handoff

The hardest part of building a clinical AI is not making it smart; it is making it *safe in the failure mode where it is wrong*. A 4B-parameter model will misclassify cases; the design question is what happens when it does.

Our answer is a deterministic safety engine that runs independently of the model. A small set of keyword red-flag rules — "fang marks", "crushing chest pain", "facial droop", "pesticide", "unresponsive", etc. — fires before *and* after the LLM call. If a flag fires, the final triage is RED no matter what the LLM said. The model can be wrong about subtle differentials; it cannot be wrong about whether the patient gets escalated, because that decision is not actually made by the model.

The hub handoff is the other half. On RED, we build a `wa.me` deep-link containing the safety reason, top differential with confidence, symptoms verbatim, patient context, the during-transport protocol from the KB, and a one-line disclaimer for the receiving doctor. The CHW taps once; WhatsApp opens with the message pre-filled on their own phone; they review and send. This preserves CHW-in-the-loop — the app prepares, the human commits — and it requires no Twilio, no Meta Business API, no auto-send liability. The same architecture that runs offline for diagnosis works for the handoff: the link is generated locally; delivery depends on the CHW's phone connectivity, which is the right place for that dependency to live.

## Evaluation

We built a 31-vignette synthetic eval suite covering every TAI-VADE category plus the high-yield mimics (DKA, hypoglycemia, sepsis, anaphylaxis, severe dehydration). Each vignette has a ground-truth triage level and condition. **Current results: 30/31 pass (96.8%), with sensitivity 21/21 (100%) and specificity 8/10 (80%).** The one failure is *over-triage* of benign palpitations — the model flagged RED when GREEN would have been correct. We consider this the right error to make: 100% sensitivity means no time-critical case was missed; erring toward the hospital is what a careful CHW would do; and the cost of an unnecessary escalation is bounded while the cost of a missed RED is unbounded. We track sensitivity and specificity separately and deliberately do not tune toward 31/31 — the safety layer's job is to *fail loudly toward escalation*.

## Challenges we hit

**Hallucination under uncertainty.** Early Gemma runs would invent conditions to fill the differential slot when symptoms were ambiguous. Fixed by KB grounding and an explicit "return the default" rule.

**Over-confidence.** Initial prompts produced confidence values of 0.95+ for ambiguous cases. Fixed by hard-capping at 0.9 in the JSON Schema — the model literally cannot output higher.

**Folk-remedy harm.** In snake-bite cases, the worst outcomes come from a tourniquet applied by the family, not the envenomation. We added a `folk_error_correction` field that surfaces alongside the diagnosis whenever the symptom text contains tourniquet/cut-and-suck/induced-vomiting phrases — turning a misdiagnosis vector into a teaching moment.

**Escalation without internet.** Standard "send a WhatsApp from the server" architectures require Twilio, an internet connection at the spoke, and uphold-able audit guarantees we cannot promise in a hackathon MVP. We replaced the entire problem with a `wa.me` deep-link: zero infrastructure, CHW-in-the-loop, fully offline-resilient.

## Why these choices

The dominant alternative architecture is "send symptoms to a hosted Gemini/GPT endpoint and post-process." It is faster to build, but it fails the village clinic. Local Gemma 4 via Ollama is the only choice that survives no-internet, no-rate-limit, no-PHI-leaving-the-laptop constraints simultaneously. JSON-schema enforcement converts a chatty model into a programmable component. The deterministic safety layer is the architecture's load-bearing innovation: it is the answer to "what happens when the AI is wrong about a 60-year-old's chest pain?"

## Tracks

We submit primarily to the **Main Track** (vision: democratizing decision support for the two billion people whose primary care is delivered by CHWs); to **Health & Sciences Impact** (direct clinical impact on time-critical conditions); and to **Ollama Special Technology** (a 100% local Gemma 4 deployment that is verifiable offline by disabling the laptop's network and re-running the suite). The video demo shows all three.

*Decision support tool. Not a diagnostic system. Always consult a qualified physician.*
