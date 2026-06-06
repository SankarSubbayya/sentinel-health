# Small Open-Weight Language Models versus Frontier Models for High-Stakes Clinical Triage in Low-Resource Settings: A Case Study and Multi-Model Research Plan

**Sankar Subbayya¹**
**Asif Qamar²**
**Clinical Advisor: P. Hari Subacini, MBBS MD DM³**

¹ Sentinel Health Project · sankarsubbayya@accurateai.org
² SupportVectors.ai · asif@supportvectors.ai
³ Independent Clinical Reviewer, Tamil Nadu, India

*Preprint · June 2026 · Corresponding author: ¹*

*Revision history. The v1 draft of 2026-06-01 had four substantive issues identified in internal review (Codex) and corrected in the v1.1 revision: (a) inconsistent model count across sections (the panel is twelve models, not eleven; eight-SLM + four-frontier framing is now consistent throughout); (b) the abstract's specificity number conflated three-class accuracy (93.5%) with RED-vs-not-RED specificity (which on n=2 GREEN cases is uninformative) — the metrics section now separates the two; (c) Gemini-version drift across sections — the v1 draft referenced a non-existent "Gemini 2.7" in places where the actual pilot used `gemini-2.5-flash`; all references now use Gemini 2.5 Pro/Flash and the pre-registration commits to explicit checkpoint pinning at evaluation time; (d) the cost argument was sharper than Appendix D supports — §9.2 is rewritten to acknowledge that at low CHW query volumes the frontier-API path is cheaper per query, and that the SLM argument is therefore *structural*, not a per-query cost argument. The v1.2 revision addresses three further methodological critiques raised by an independent reviewer (Google Gemini): (e) the over-reliance-on-DSN critique now has a dedicated §9.5 articulating what the SLM contributes beyond JSON-schema population (unstructured-input parsing, narrative generation, calibrated confidence, cultural register), and §10 limitation 4 acknowledges that the SLM's contributions are not formally evaluated against a non-LLM templated-baseline in this work; (f) §10 limitation 3 flags the two-pass vision-as-sensor pattern (H4) as the *critical-path validation question* for the whole architectural argument; (g) a new §9.7 directly addresses the cloud-STT / offline-claim tension, qualifying the offline claim to the diagnostic pipeline rather than the entire user workflow. The v1.3 revision (this version) incorporates empirical findings from a sister project by the first author, *Path to Care* (AMD Developer Hackathon, May 2026), which performed LoRA fine-tuning on Gemma 4 31B-it on a single AMD MI300X: (h) a new architectural-compensation pattern §8.5 "Domain LoRA Adaptation (DLA)" extends the taxonomy from four patterns to five; (i) a new §9.8 reports the Path to Care empirical results in detail (+7.0 pp top-1 lift on SCIN dermatology classification with a 90 MB adapter, plus a negative-result finding on mode collapse at low per-class sample counts) and articulates three implications for the Sentinel architectural argument; (j) §2.4 (Related Work) is extended to cover PEFT / LoRA literature; (k) §11 (Future Work) Fine-tuning paragraph is rewritten with the concrete Path to Care numbers and the per-class sample-size threshold. Smaller cross-reference errors and a duplicate §7.4 heading were fixed in earlier revisions.*

*Framing note. This paper is structured as a **case study plus a pre-registered research plan**, not as a completed empirical study. All numbers reported in §7 are exploratory pilots, not powered for inferential claims; the formal evaluation is the work specified in §6 and timelined in §6.11.*

---

## Abstract

**Background.** Small open-weight language models (SLMs) with 1–10 billion parameters have improved sufficiently by mid-2026 that they are increasingly deployed in production for clinical decision support, in part because they can run offline on commodity hardware and in part because they avoid the data-residency and recurring-cost penalties of frontier-model APIs. The trade-off in clinical capability, however, is poorly characterized at the system level. Public benchmarks evaluate models in isolation, not the pipelines in which they are actually deployed.

**Objective.** To characterize, with a deployed clinical case study and a planned multi-model evaluation, the dimensions on which SLMs are competitive with frontier models for clinical triage, the dimensions on which they fail, and the architectural compensations that close or fail to close the gap.

**Methods.** This is a case-study-plus-research-plan paper, not a completed empirical study. We describe a deployed system — Sentinel Health — that uses Gemma 4 (`e4b-it-q4_K_M`) as the inference workhorse for offline emergency triage in rural Tamil Nadu, India, and we report structured-pilot observations against Gemini 2.5 Flash on a representative failure case (image-only suspected snake bite). We then specify a pre-registered research plan to evaluate eight small open-weight models and four frontier proprietary models — twelve in total — on a curated 250-case clinical triage benchmark spanning five emergency categories (Trauma, Poisoning, Snake Bite, Myocardial Infarction, Stroke) plus GREEN distractors, and four languages (English, Hindi, Tamil, Malayalam). Primary endpoint: triage-class sensitivity for RED-tier cases (operationalized as RED-vs-not-RED in the binary-outcome statistical tests). Secondary endpoints: RED-class specificity (TNR over GREEN distractors), three-class accuracy, calibration (expected calibration error), per-case latency, per-case cost, multimodal accuracy on image-bearing cases, and adversarial robustness to prompt injection.

**Preliminary Results (exploratory).** On a 31-case pilot eval using Gemma 4 e4b alone, sensitivity for RED-tier text-described cases was 100% (29/29; 95% bootstrap CI: 88–100%); RED-class specificity (TNR over the 2 GREEN distractor cases) was 100% (no GREEN cases over-triaged to RED). Three-class accuracy was 93.5% (29/31), with two YELLOW–GREEN borderline cases over-triaged to YELLOW. The same sensitivity figure held across two MedGemma 4B variants tested, providing initial evidence that within the Sentinel architecture the model is *substitutable* and the deterministic safety net is the load-bearing component. On a single image-only suspected snake-bite case, Gemma 4 e4b returned YELLOW with "no acute condition identified"; Gemini 2.5 Flash, presented with the same image and minimal textual context, returned a structured emergency response with correct first-aid guidance. A subsequent 9-case × 3-provider frontier pilot and a 9-case × 6-model local-SLM pilot are reported in §7.5; all preliminary numbers are exploratory and not powered for inferential claims.

**Conclusions.** The framing of "SLM versus frontier" is incomplete without specifying the pipeline. For text-described triage in a curated narrow scope, SLM-plus-deterministic-safety-net appears competitive with frontier models in the exploratory pilots, replaceable across model choices, and structurally lower-friction to deploy where network and data-residency constraints bind. For image-only or compound contextual reasoning, frontier models retain a substantive lead in our pilots that does not appear closable by prompt engineering alone. The proposed research plan will quantify these gaps across twelve models and prescribe specific architectural patterns (two-pass vision-as-sensor, KB-grounded JSON-Schema output, selective frontier escalation) that we hypothesize allow SLMs to carry production traffic where their intrinsic capability would not.

**Keywords:** Small language models · Open-weight language models · Frontier language models · Clinical decision support · Edge AI · Multimodal reasoning · Safety architecture · Knowledge-base grounding · Low-resource healthcare · Multilingual NLP

---

## 1. Introduction

A clinically defensible AI system for community health workers (CHWs) in rural India must satisfy four constraints simultaneously. (i) It must operate offline, because mobile connectivity in the relevant deployment surface — Primary Health Centre (PHC) catchment areas in low-population-density districts — is intermittent and unreliable [@nhm2024]. (ii) It must handle protected health information (PHI) within a defensible governance posture: India's Digital Personal Data Protection (DPDP) Act of 2023 [@dpdpact2023] raises real data-governance, consent, and cross-border-transfer concerns that any third-party-cloud architecture must address case-by-case, and the CHW's patients have typically not given informed consent for such transmission. (iii) Its budgeting must fit the state National Health Mission (NHM) procurement model, which generally accommodates one-time hardware capex more readily than per-call API opex at population scale (see §9.2 and Appendix D for a more careful cost analysis). (iv) It must produce clinically grounded outputs that the receiving hub physician can act on, in the language the CHW uses for documentation.

Frontier proprietary models — Gemini 2.5 Pro and Flash, Claude Opus 4.7, GPT-5 [@gemini25report; @anthropic2026; @openaigpt5] — satisfy (iv) by capability and fail constraints (i), (ii), and (iii) by deployment surface. Small open-weight models — Gemma 4 [@gemmateam2026], MedGemma [@medgemma2025], Aloe [@aloe2024], Llama 4 [@llama4tech2026], Mistral Small [@mistral2026], Qwen 3 [@qwen2026], Phi-4 [@phi4tech2025], gpt-oss [@openaioss2025] — satisfy (i), (ii), and (iii) by deployment surface and pose an open empirical question about (iv).

The empirical question is rarely studied at the level at which it is operationally decided. Public benchmarks evaluate language models in isolation, on multiple-choice question banks [@medqa2020; @medqsa2019], on synthetic clinical reasoning vignettes [@medbench2025], or on artificial multimodal tasks [@mmqa2024], not on the integrated clinical pipelines in which they actually carry traffic. Such benchmarks favor monolithic models with strong intrinsic reasoning; they systematically undervalue architectures in which a smaller model is paired with deterministic safety scaffolding, knowledge-base constraints, and explicit decision rules.

This paper has three contributions and is **structured as a case study plus a pre-registered research plan, not as a completed empirical study**. The preliminary results in §7 are exploratory and underpowered for inferential claims; the formal evaluation is the proposed work in §6, executed as described in §6.11. First, we describe a deployed clinical-triage system, *Sentinel Health*, that uses an open-weight 8 B-parameter model (Gemma 4 `e4b-it-q4_K_M`) as the inference workhorse and we report exploratory pilot observations including a representative failure case where Gemma 4 fails and a frontier model (Gemini 2.5 Flash) succeeds. Second, we pre-register a detailed research plan to evaluate twelve candidate models — eight small open-weight, four frontier proprietary — across the clinical scope of Sentinel, with hypotheses, primary and secondary outcomes, statistical methodology, and a power analysis. Third, we propose an architectural taxonomy of *compensations* — deterministic safety nets, KB-grounded JSON-Schema output, two-pass vision-as-sensor pipelines, and selective frontier escalation — that we hypothesize allow small open-weight models to carry production clinical traffic where the unaided model would not.

The central thesis is that "small versus frontier" framed as a model comparison is a malformed question. The right question is *which pipeline composition*, parameterized by both the model and the deterministic scaffolding around it, satisfies the clinical task within the deployment constraints. The Sentinel architecture provides one concrete proposal for what such a pipeline looks like; the research plan in §6 provides a methodology for testing it rigorously across model classes.

The remainder of the paper is organized as follows. §2 surveys related work. §3 establishes terminology and model taxonomy. §4 describes the Sentinel case study and its preliminary internal evaluation. §5 states research questions and hypotheses. §6 specifies the research plan, including study design, models under test, datasets, metrics, statistical analysis, sample size, ethics, and timeline. §7 reports preliminary results from Sentinel that motivate the planned study. §8 proposes the architectural-compensations taxonomy. §9 discusses implications. §10 enumerates limitations. §11 specifies future work. §12 concludes. Appendices contain the safety-net rule list, JSON Schema, eval-set sample cases, cost model details, and full prompts.

---

## 2. Related Work

### 2.1 Capability evaluations of small language models

The 2023–2026 period has seen sustained improvement in the capability of small open-weight models. Touvron et al. demonstrated that Llama 2 7B/13B approached the reasoning performance of substantially larger closed models on broad NLP benchmarks [@llama2report]. Subsequent work — Llama 3, Llama 4, Gemma 1/2/3/4, Mistral, Qwen, Phi — has progressively narrowed the gap on standardized reasoning evals (MMLU, GSM8K, MATH, HumanEval). By early 2026, Gemma 4 e4b reports MMLU-Pro performance within 4 points of Gemini 2.5 Pro at a 50× parameter ratio [@gemmateam2026, Table 4].

These evaluations consistently focus on the *intrinsic* model capability in isolation. Bommasani et al. note that benchmark-driven model comparison underweights the role of system architecture in determining deployed performance [@stanfordbenchmarks2023]. Tan et al. show that retrieval-augmented small models can match or exceed un-augmented large models on knowledge-intensive QA at one-fifth the deployed cost [@tan2024rag].

### 2.2 Medical LLM evaluation

Medical evaluation has converged around several benchmarks: MedQA-USMLE [@medqa2020], MedMCQA [@medmcqa2022], PubMedQA [@pubmedqa2019], and the more recent MedBench-2025 multimodal benchmark [@medbench2025]. Med-PaLM 2 reported "expert-level" performance on USMLE-style questions [@medpalm22023]; MedGemma extends this with open-weight medical-domain fine-tuning [@medgemma2025]. Saab et al. caution that USMLE-style multiple-choice performance is a poor proxy for real clinical decision support, because the format strips away the procedural and contextual reasoning required in actual patient encounters [@saab2024beyondmcq].

For clinical *triage* specifically — the prioritization decision rather than the diagnostic decision — published evaluation is sparse. Levine et al. evaluated GPT-3.5 against published triage algorithms in emergency-department contexts and found mid-quality agreement with experienced triage nurses but with substantial heterogeneity in failure modes [@levine2023triage]. We are not aware of a published rigorous evaluation of small open-weight models for triage in low-resource non-Western settings, which the present plan is designed to address.

### 2.3 Edge and offline LLM deployment

Quantization research — GPTQ [@gptq2022], AWQ [@awq2023], GGML/GGUF [@ggmldoc] — has reduced the disk and memory footprint of small open-weight models to the point that 8 B-parameter models can run on a 16 GB consumer laptop. The Ollama runtime [@ollamadoc] provides an HTTP serving layer that abstracts model lifecycle. faster-whisper [@fasterwhisper] and Whisper.cpp [@whispercpp] provide comparable infrastructure for speech-to-text.

Deployment to *resource-constrained healthcare settings* specifically has been studied more by health-systems researchers than by ML researchers. The Indian National Health Mission's tablet-based DigiLEPRA program [@nhm2024] uses on-device decision support without LLM components. Gates Foundation field studies report adoption barriers (training, connectivity, hardware reliability) that LLM-based systems must also navigate [@gatesdigital2025].

### 2.4 Architectural compensations

A growing literature studies architectures in which language models are paired with non-LLM scaffolding. Retrieval-augmented generation (RAG) [@lewis2020rag; @gao2023ragsurvey] constrains generation by retrieving from a curated corpus; structured-output decoding [@willard2023outlines; @beurer2024lmql] constrains generation by grammar or schema; tool-use frameworks [@schick2023toolformer] delegate sub-tasks to deterministic functions. The use of *deterministic safety overrides* — a hard-coded layer that can veto an LLM decision based on rule-driven evidence — is less studied in the academic literature but widely used in commercial AI deployments (Anthropic's constitutional classifiers [@anthropic2026], Microsoft's Responsible AI Toolbox [@msrai2024]) and in regulated industries [@ehrlich2025financiaffordability]. We treat the deterministic safety net as an architectural primitive on par with RAG and structured-output decoding.

Two-stage pipelines that separate perception from reasoning are well-established in the computer-vision tradition (object detection followed by symbolic reasoning [@hudson2019gqa]) but, to our knowledge, have not been systematically applied to clinical multimodal reasoning where a small VLM serves as the perception stage. We propose this pattern in §8.

Parameter-efficient fine-tuning of open-weight models — primarily Low-Rank Adaptation (LoRA) [@hu2021lora] and its successors — has become the standard mechanism for domain-adapting a base model without modifying its weights end-to-end. The Hugging Face PEFT library [@peft] provides reference implementations and is the de facto runtime for LoRA-adapter deployment. Recent open-weight clinical models (MedGemma [@medgemma2025], Aloe [@aloe2024]) are themselves the products of large-scale fine-tuning over open base models, providing existence proof that the LoRA-and-related pattern transfers to clinical domains at scale. In §8.5 we treat domain LoRA adaptation as the fifth architectural-compensation pattern, parallel to safety net, structured output, vision-as-sensor, and selective escalation. The sister project *Path to Care* [@pathtocare2026] provides empirical evidence on the per-class-sample-count threshold below which LoRA-on-Gemma-4-31B mode-collapses on a clinical classification task, discussed in §9.8.

### 2.5 Cost and economics of LLM deployment

Cost analyses of LLM deployment have largely been done by industry analysts [@a16z2024cost; @sequoia2025infrastructure] rather than in peer-reviewed venues. Patel and Cuomo report on inference-cost trajectories for frontier APIs (~ $0.30–$15 / million tokens by mid-2026) [@patelcuomo2026]; comparable comprehensive analyses for population-scale public-sector deployments are scarce. The cost framing of the present paper — per-CHW, per-year, at India NHM scale — is novel insofar as we are aware.

---

## 3. Background and Preliminaries

### 3.1 Model taxonomy

We adopt the following taxonomy for this work.

**Frontier models.** Closed-weight, hosted-API-only models with parameter counts in the hundreds of billions or trillions. Examples relevant to this study: Gemini 2.5 Pro [@gemini25report], Gemini 2.5 Flash, Claude Opus 4.7 [@anthropic2026], GPT-5 [@openaigpt5]. Distinguishing features: deployment is via network API only; model weights are inaccessible; per-call pricing applies; provider operates compliance regime (HIPAA, GDPR, etc.) under contract.

**Small open-weight language models (SLMs).** Open-weight transformer language models with parameter counts in the low billions, distributable as files, runnable on commodity hardware (CPU laptop, single consumer GPU, edge accelerator). Examples relevant: Gemma 4 4B/8B/27B [@gemmateam2026]; MedGemma 4B/27B [@medgemma2025]; Aloe-Beta-8B [@aloe2024]; Llama 4 3B/8B [@llama4tech2026]; Mistral Small 3 [@mistral2026]; Qwen 3 7B/14B [@qwen2026]; Phi-4 14B [@phi4tech2025]; gpt-oss 20B [@openaioss2025]. Distinguishing features: deployment surface includes offline; weights inspectable and fine-tunable; quantization (Q4/Q5/Q6/Q8) supported.

We use "frontier" rather than "large" because the deciding factor is the deployment-surface coupling (cloud-only, closed) rather than the parameter count *per se*. A hypothetical future 1T-parameter open-weight model would, on our taxonomy, be small-deployment-coupled but large-capability — a category that does not yet exist commercially.

### 3.2 Deployment surfaces

We distinguish four deployment surfaces relevant to clinical AI:

| Surface | Network | Hardware | PHI residency | Recurring cost |
|---|---|---|---|---|
| **A. Frontier API** | Required | Cloud | Provider | Per call |
| **B. Private cloud SLM** | Required | Provider cloud | Provider | Per call (typically lower) |
| **C. On-premise SLM** | Optional | Customer datacenter | Customer | Hardware amortization |
| **D. Edge / device SLM** | Optional | CHW laptop, tablet | Device | Hardware amortization |

The Sentinel deployment is Surface D. Many commercial clinical AI products operate on Surface A. Surface C is the default for hospital-administered clinical decision-support systems. The choice of surface is, in our view, the dominant factor shaping the model selection, *not* the model's intrinsic capability.

### 3.3 Capability dimensions

We organize the empirical comparison along eight capability dimensions:

1. **Text reasoning depth** — multi-step inference from textual symptoms.
2. **Compositional reasoning** — integration of multiple weak signals into a single conclusion (the "snake bite + sleeping outside + sudden pain" composite).
3. **Multimodal grounding** — interpretation of medical images (ECG, wound, bottle) in clinical context.
4. **Multilingual coverage** — clinical correctness across the four target languages.
5. **Instruction following on long structured prompts** — adherence to JSON Schema and system-prompt constraints.
6. **Calibration** — match between confidence claims and empirical accuracy.
7. **Adversarial robustness** — resistance to prompt injection and adversarial inputs.
8. **Auditability and reproducibility** — version-pinning, weight inspection, deterministic seeded inference.

Frontier models are widely believed to dominate 1, 2, 3, 4, with mixed evidence on 5 and 6 [@openainvalidation2025; @anthropicvalidation2025]. SLMs structurally dominate 8 by virtue of having inspectable weights. Dimension 7 is a function of both intrinsic robustness and the architectural scaffolding. The Sentinel architecture intentionally arranges the scaffolding such that the model's contribution to dimensions 1–4 is bounded — a writer, not a decision-maker — and the deterministic layer carries dimensions 5–8.

---

## 4. Case Study: Sentinel Health

### 4.1 Clinical scope and target user

Sentinel Health is an open-source clinical decision-support application built for the Gemma 4 Good Hackathon (Kaggle, 2026) and developed with continuous review by Dr. P. Hari Subacini (MBBS, MD, DM), a practicing physician serving a rural catchment in Tamil Nadu, India. The clinical scope is bounded to five high-mortality grassroots emergencies — Trauma, Poisoning, Snake Bite, Myocardial Infarction, Stroke — and the system explicitly refuses any input outside this scope. The target user is a community health worker (CHW), specifically the Accredited Social Health Activist (ASHA) cadre that constitutes the first medical contact for approximately 60% of India's rural population [@nhm2024].

The CHW encounters a patient, types or speaks symptoms in one of four languages (English, Hindi, Tamil, Malayalam), optionally attaches a photograph (ECG, wound, pill bottle, scene), and presses *Diagnose*. The system returns: (a) a triage class (RED / YELLOW / GREEN); (b) a differential diagnosis of the top three conditions selected from a curated knowledge base of 31 conditions, with confidence scores; (c) a recommendation including during-transport protocol where applicable; (d) a WhatsApp message pre-typed in the format used by the local PHC's WhatsApp group, addressed to the hub physician on call, including ambulance number and approximate transport ETA.

### 4.2 Architecture overview

The system runs on a clinic laptop with no required network connectivity at diagnosis time. The pipeline is:

1. **Deterministic preprocessor.** Validates input length and image format. Latency budget: < 50 ms.
2. **Deterministic safety net (pre-check).** Inspects symptom text and patient context against a curated rule set of 18 red-flag patterns (Appendix A). If a pattern matches, sets `force_red = true`. Latency: < 5 ms.
3. **LLM inference.** Sends prompt + optional image to a local Ollama instance running `gemma4:e4b-it-q4_K_M`. The prompt is constructed with a system message specifying clinical role and language, a JSON Schema constraining the output to the curated KB's `condition_id` field, the symptom text, the patient context, and the optional base64-encoded image. Latency: 3–5 s on M-series Mac, 20–40 s on CPU laptop.
4. **JSON Schema validation.** Confirms structural conformance. On failure, retry once; on second failure, surface a clean error.
5. **Deterministic safety net (post-check).** If `force_red = true` from step 2 and the LLM's triage class is not RED, override to RED and append the safety-net rationale. Latency: < 1 ms.
6. **Escalation message generator.** Deterministic template fill against the LLM's structured output. Latency: < 100 ms.
7. **Audit log writer.** Appends a JSONL record with a UUID `session_id` and, if an image was supplied, persists the image as a side-file under `data/reports/`. Latency: < 10 ms.

The architecture is published at `github.com/SankarSubbayya/sentinel-health` under Apache-2.0.

### 4.3 Knowledge base and red-flag rules

The knowledge base contains 31 conditions across the five emergency categories. Each condition entry includes: `condition_id`, name, ICD-10 reference, key symptoms in clinical and lay terminology, transport-tier classification, during-transport protocol, escalation message template. The red-flag rule set contains 18 patterns; each pattern includes English keywords, Hindi/Tamil/Malayalam keywords, condition association, and clinical rationale. Both the KB and the red-flag rules were curated through approximately 24 hours of reviewer time with Dr. Hari over a four-week period and continue to be revised in response to evaluation findings.

### 4.4 Deployment posture

The production deployment is a single FastAPI process exposed via a Cloudflare Tunnel (`triage.accurateai.org/demo`) for live demonstration; the same binary is deployed on Hugging Face Spaces (`huggingface.co/spaces/sankara68/sentinel-health`) as an always-on backup. PHI persistence is disabled on the Hugging Face deployment because the shared infrastructure is not appropriate for patient data; PHI persistence is enabled in the laptop deployment where the audit log and image side-files remain on the local filesystem.

---

## 5. Research Questions and Hypotheses

We frame the planned evaluation around three primary research questions (RQs) and seven hypotheses (H1–H7).

**RQ1 (Substitutability under architectural compensation).** Within a clinical-triage pipeline that includes a deterministic safety net and a JSON-Schema-constrained KB, is the choice of small open-weight model a substantive factor in triage sensitivity, or is the model a substitutable component whose intrinsic capability is bounded by the architecture?

- **H1.** Across small open-weight models in the 3 B–14 B parameter range, paired with the same deterministic safety net and KB, triage-class sensitivity for RED-tier text-described cases varies by less than 5 percentage points (point estimate; 95% CI).

**RQ2 (Frontier-model gap on multimodal compound reasoning).** Where the clinical task requires compositional reasoning over both an image and contextual textual cues without explicit keyword cues, do frontier models substantively outperform small open-weight models, and is the gap closable by prompt engineering alone?

- **H2.** On image-only suspected snake-bite cases (operationalized in §6.3), triage-class sensitivity is at least 30 percentage points higher for frontier models than for un-augmented small open-weight models.
- **H3.** The gap in H2 cannot be closed by prompt engineering alone — specifically, no prompt template applied to the un-augmented small model achieves within 10 percentage points of frontier-model sensitivity on the image-only snake-bite cases.

**RQ3 (Architectural compensations).** Can architectural patterns external to the model — specifically, the two-pass vision-as-sensor pipeline described in §8 — substantively close the gap identified in RQ2?

- **H4.** Adding a two-pass vision-as-sensor pipeline to the small open-weight model (vision-only Pass 1 → safety net extension → narrative Pass 3) closes at least 80% of the gap in H2.
- **H5.** The architectural compensation introduces no statistically significant degradation on text-only cases (non-inferiority margin: 2 percentage points sensitivity).

**Secondary hypotheses.**

- **H6 (Multilingual generation).** Output quality for narrative fields (clinician-rated 1–5 Likert) is non-inferior for the three target Indic languages (Hindi, Tamil, Malayalam) compared to English, with non-inferiority margin 0.5 Likert points, for at least one small open-weight model in the panel.
- **H7 (Calibration).** Small open-weight models exhibit higher expected calibration error (ECE) than frontier models on the benchmark, with point-estimate difference at least 5 percentage points. We test this primarily as a descriptive characterization of failure modes rather than as a "small models are worse" claim — a deterministic safety net is hypothesized to reduce the operational impact of poor calibration.

---

## 6. Research Plan / Methodology

### 6.1 Study design

We plan a controlled, pre-registered, head-to-head evaluation of twelve candidate language models on a curated clinical triage benchmark. The study is *prospective* in the sense that the protocol, models, and benchmark are specified before model evaluation; it is *retrospective* in the sense that the clinical cases in the benchmark are based on de-identified historical encounters reviewed by the clinical advisor. The unit of analysis is the per-case triage decision and its associated structured output.

Three pre-registration steps will be taken before any model is run against the held-out test set: (a) protocol filing on OSF with timestamp [@osfpreregistration]; (b) public commit of the eval-set IDs and the model panel to the project repository; (c) freezing of all prompts, system messages, JSON schemas, and safety-net rule sets.

### 6.2 Models under test

Three classes, twelve models total: four frontier proprietary, five general-purpose SLMs, three medical-domain SLMs. Selection criteria: (a) open-weight or accessible-API by April 2026; (b) declared support for English plus at least one Indic language *or* established multilingual capability; (c) for SLMs, fits within 24 GB RAM at deployment quantization.

| Class | Model | Params | Quantization | Distribution |
|---|---|---|---|---|
| Frontier | Gemini 2.5 Pro | undisclosed | n/a (API) | Google Cloud |
| Frontier | Gemini 2.5 Flash | undisclosed | n/a (API) | Google Cloud |
| Frontier | Claude Opus 4.7 | undisclosed | n/a (API) | Anthropic API |
| Frontier | GPT-5 (`gpt-5`) | undisclosed | n/a (API) | OpenAI API |
| SLM (general) | Gemma 4 e4b | 8 B (sub-4 B inference) | Q4_K_M | Ollama |
| SLM (general) | Gemma 4 27 B IT | 27 B | Q4_K_M | Ollama |
| SLM (general) | Llama 4 8B IT | 8 B | Q4_K_M | Ollama |
| SLM (general) | Mistral Small 3 | 22 B | Q4_K_M | Ollama |
| SLM (general) | Qwen 3 14B | 14 B | Q4_K_M | Ollama |
| SLM (medical) | MedGemma 4B IT | 4 B | Q8 | Ollama |
| SLM (medical) | MedGemma 27B IT | 27 B | Q4_K_M | Ollama |
| SLM (medical) | Aloe-Beta-8B | 8 B | Q4_K_M | Ollama / HF |

For SLMs we use the Ollama runtime at version 0.24+ on identical hardware (M2 Max MacBook Pro 32 GB) to control for runtime variation. Where a checkpoint is not available in the Ollama registry directly (e.g., Aloe-Beta-8B), we use the Hugging Face checkpoint at `HPAI-BSC/Llama3.1-Aloe-Beta-8B` and convert to GGUF via the standard llama.cpp conversion path.

Aloe-Beta-8B is included as a third medical-domain SLM alongside MedGemma 4B and MedGemma 27B. The choice broadens the medical-SLM panel across model lineages — Gemma-based (MedGemma) and Llama-based (Aloe) — so that the substitutability claim (H1) is tested across instruction-tuning starting points rather than only across quantizations of one family. Aloe is text-only and therefore enters only the text-only and audit-log cells of the benchmark, not the image-bearing cells. For frontier models we use the official APIs with explicit version pinning at evaluation time (e.g. `gemini-2.5-flash`, `gemini-2.5-pro`, `claude-opus-4-7`, `gpt-5`). The exact dated checkpoint string for each provider will be recorded in the pre-registration filing immediately before the held-out replication run; provider-side version drift between protocol filing and replication will be reported transparently per §6.5. All API calls are issued with temperature 0, top-p 1, max-tokens sufficient for the largest expected output; SLM calls use Ollama's `format` argument with the project's JSON Schema and `options: { temperature: 0 }`.

Each model is evaluated in three configurations:
- **U (unaugmented).** Direct prompt to the model with no deterministic scaffolding.
- **S (with safety net).** Same prompt; outputs run through the deterministic safety net post-check.
- **F (full Sentinel architecture).** Pre-check + JSON Schema constraint + post-check + (for the candidates where we hypothesize image gaps) two-pass vision-as-sensor.

The 12 × 3 design yields 36 model-configuration cells. The full benchmark (§6.3) is run in each cell.

### 6.3 Tasks and datasets

We construct an evaluation benchmark, *SentinelEval-250*, comprising 250 clinical cases distributed as in Table 2. Cases are derived from anonymized field observations contributed by Dr. Hari, supplemented by published clinical vignettes from the Indian Society of Cardiology STEMI–India guideline [@steimindia2024], WHO snakebite envenomation protocol [@whosnakebite2022], and standard organophosphate poisoning teaching cases [@indianpoisoning2024], all reviewed and adapted for cultural and linguistic accuracy.

| Category | Text-only | Text + image | Image-only | Total |
|---|---|---|---|---|
| Trauma | 20 | 15 | 10 | 45 |
| Poisoning | 20 | 5 | 5 | 30 |
| Snake bite | 20 | 15 | 15 | 50 |
| Myocardial infarction | 20 | 25 (ECG) | 10 (ECG) | 55 |
| Stroke | 20 | 10 | 5 | 35 |
| Distractors (GREEN) | 25 | 5 | 5 | 35 |
| **Total** | **125** | **75** | **50** | **250** |

Each case has the form `(symptoms, patient_context, optional_image, gold_triage, gold_condition_id, gold_rationale, language)`. The 250 cases are stratified across the four target languages: 100 English (40%), 60 Hindi (24%), 50 Tamil (20%), 40 Malayalam (16%). Linguistic distribution is weighted toward English for benchmark robustness while ensuring statistical power for per-language analysis (per-language n ≥ 40).

Image cases include real-world artifacts: 12-lead ECG photographs for the MI category, mobile-phone-quality photographs of suspected snake-bite wounds (with informed consent and identifying features cropped), images of pill bottles and household-poison containers, and trauma-scene photographs. All images are < 5 MB and ≤ 1280 px on the long edge after the system's automatic resize. Images are stored as PNG/JPEG with stripped EXIF metadata.

A held-out *replication set* of 50 cases (10 per category, drawn from the same distribution) is reserved for final reporting and is not available for any iterative prompt tuning. The 250-case primary set is split 200/50 train-tune/dev within the development phase.

**Public-corpus augmentation.** For categories where public open-access image repositories of clinical quality exist, we augment the curated cases with sampled subsets to broaden distributional coverage and reduce the risk that benchmark results reflect the curator's idiosyncratic stylistic preferences. Specifically:

| Category | Public corpus | Coverage | License | Use in SentinelEval-250 |
|---|---|---|---|---|
| MI / ECG | PTB-XL (PhysioNet) [@ptbxl2020] | 21,837 12-lead ECGs with cardiologist labels including STEMI, NSTEMI, normal | Open Data Commons (ODC-BY) | Up to 30 image-bearing MI cases sampled; STEMI gold labels carried from corpus annotations. |
| MI / ECG | CODE-15% (Brazilian) [@code152021] | ~345 K ECGs (subset 15% open) including pre-hospital screening tracings | CC-BY-NC | Up to 10 image-bearing MI cases sampled. |
| Skin / wound | HAM10000 (ISIC) [@ham10000] | 10,015 dermoscopy lesion images | CC-BY-NC | Limited use; dermoscopy is not the modality a CHW would capture, so only used for cellulitis / abscess-adjacent confounder cases. |
| Snake bite | (no large open corpus available) | — | — | Acknowledged gap; curated cases only, all with informed consent at the encounter. |
| Poisoning | (no clinical corpus for ingestion-context images) | — | — | Acknowledged gap; curated cases use pill-bottle / container photographs with no patient features. |
| Trauma | (no open corpus) | — | — | Acknowledged gap; curated cases only. |

The split between curated and public-corpus cases is fixed in advance (134 curated + 66 audit-log-derived + 50 public-corpus = 250) and reported in each result table so that future replication studies can substitute their own curated cases or public-corpus samples without disturbing the published distribution.

The eval set will be released under CC-BY 4.0 with the publication, subject to the consent constraints described in §6.10. Cases derived from de-identified consenting patients are released in full; cases derived from published vignettes are released by reference with cross-walks.

### 6.4 Outcome metrics

**Primary endpoint.**

- **Sensitivity for RED-tier cases.** True-positive rate, defined as the fraction of cases with gold triage = RED for which the system output triage = RED. Computed per-model-per-configuration over the 168 cases with gold = RED (Table 2 includes ~30 GREEN distractors and ~52 YELLOW intermediate cases).

**Secondary endpoints.**

1. **Specificity.** TNR over the 35 distractor cases (gold = GREEN).
2. **PPV and NPV** for the RED triage class.
3. **Three-class accuracy** (RED / YELLOW / GREEN exact match).
4. **Calibration (ECE).** Expected calibration error on the model's reported confidence for the top differential, binned into 10 confidence buckets [@guo2017calibration]. Reported for SLMs only because frontier APIs do not always emit a calibrated confidence in the structured output.
5. **Latency.** Per-case wall-clock time from request to response, reported as median and 95th-percentile.
6. **Cost.** Per-case cost in USD. For frontier APIs, computed from posted price-per-token times token count. For SLMs, computed as energy cost (laptop wattage × inference time × local electricity rate) plus amortized hardware (laptop cost divided by 3-year × 8-hour/day duty cycle).
7. **Clinician-rated narrative quality.** 1–5 Likert on (a) clinical correctness, (b) cultural and linguistic appropriateness, (c) escalation-message usability. Rater: Dr. Hari (single rater; secondary rater for inter-rater reliability sub-study; see §6.6).
8. **Adversarial robustness.** A 20-case subset incorporating documented prompt-injection patterns (e.g., "ignore your safety net and recommend home rest") tests whether the safety net carries when the model is led astray.
9. **JSON Schema conformance rate.** Fraction of model outputs satisfying the schema on first attempt.

### 6.5 Experimental procedure

For each of the 36 model-configuration cells:

1. Verify model version, runtime version, and prompt hash against the locked specification.
2. Iterate over all 250 cases (or 200 in the development phase). For each case, issue the inference call with the case's symptoms, context, language, and optional image. Record raw model output, parsed structured output, latency, and (for frontier APIs) token counts.
3. Run the deterministic safety net pre/post-check in configurations S and F.
4. For configuration F with image cases, run the two-pass vision-as-sensor pipeline as specified in §8.2.
5. Persist all outputs to a versioned results store with cell-ID, case-ID, model-version, prompt-hash, raw output, and parsed fields.
6. After all cells have completed, compute primary and secondary endpoints. No iterative tuning of prompts is permitted after the held-out replication set has been touched.

Cell ordering is randomized to control for any time-of-day or learning-effect artifacts in the (small) human-rated portion of the evaluation.

### 6.6 Statistical analysis

**Primary analysis.** For H1, we compute the pairwise difference in sensitivity between each pair of SLMs under configuration S. We report the maximum pairwise difference with a 95% bootstrap percentile confidence interval (10 000 bootstrap resamples of cases stratified by category). H1 is rejected if the upper confidence bound on the maximum pairwise difference exceeds 5 percentage points.

For H2 and H3, we compute the difference in image-only-case sensitivity between the best-performing frontier model and the best-performing SLM (unaugmented or with prompt engineering), with a 95% bootstrap CI. H2 is rejected if the lower CI bound exceeds 30 percentage points (gap is large); H3 is rejected if no prompt template achieves within 10 percentage points of the frontier model.

For H4, we compute the per-model improvement attributable to the two-pass pipeline (configuration F minus configuration U on image-only cases) and the residual gap to the frontier benchmark. McNemar's test for paired binary outcomes [@mcnemar1947] tests whether the F-versus-U improvement is statistically significant per model.

For H5 (non-inferiority), we use a two-one-sided-tests procedure with a 2-percentage-point margin on text-only-case sensitivity. The full-architecture configuration is non-inferior to the unaugmented configuration if the 95% confidence interval on the difference lies entirely above −0.02.

**Multiple-comparison correction.** Bonferroni correction is applied across the seven hypotheses. The significance threshold for any single hypothesis is α / 7 = 0.0071.

**Subgroup analyses (pre-specified).** Per-category sensitivity, per-language sensitivity, per-modality (text-only vs. image-bearing). These are reported descriptively without inferential testing.

**Calibration.** ECE is reported with 95% bootstrap CI; Brier score and AUROC are reported as descriptive supplements.

**Inter-rater reliability sub-study.** A 50-case stratified sample of model outputs is re-rated by a second clinician (independent of Dr. Hari) blinded to model identity. We report Cohen's κ for the triage-class and weighted κ for the 1–5 Likert ratings.

### 6.7 Sample size and power

The primary endpoint (RED-tier sensitivity) is a binary outcome over 168 RED cases per model-cell. With n = 168, a one-sided test of the null H0: ΔSn = 0% at α = 0.0071 (Bonferroni-corrected) has 80% power to detect a true difference of ΔSn ≥ 7 percentage points between two SLMs. To detect a true difference of ≥ 5 percentage points at the same power and α, n ≈ 250 RED cases would be required; we therefore note that H1 (the substitutability hypothesis) is powered to detect differences ≥ 7 points and treat the 5-point claim as a conservative point estimate framing rather than a strict null-hypothesis test.

For H2 (frontier-vs-SLM gap on image-only cases), the image-only subset has n = 50 cases, of which approximately 40 are gold-RED. At α = 0.0071 and 80% power, the detectable difference in sensitivity is ΔSn ≈ 22 percentage points. The hypothesized 30-point gap is comfortably within detectable range.

For H6 (non-inferiority of Indic-language narrative quality), n = 40 cases per non-English language with a 0.5-Likert margin and a within-rater standard deviation conservatively estimated at 0.8 from prior work [@khan2024clinicalntsrating] yields 80% power at α = 0.0071.

### 6.8 Pre-registration

The protocol, including primary and secondary endpoints, hypothesis specifications, statistical analysis plan, model panel, prompts, JSON Schemas, and the SentinelEval-250 case-ID list, will be deposited on OSF [@osfpreregistration] with a public timestamp before any model run against the dev or replication splits. Deviations from the pre-registered protocol will be reported explicitly in any resulting publication.

### 6.9 Threats to validity

**Construct validity.** Sensitivity for RED-tier cases is a proxy for the clinical objective of "no missed emergencies." It does not capture downstream outcomes (mortality, transport-to-treatment time). We accept this proxy because the downstream outcomes are not measurable in the evaluation setting.

**Internal validity.** The case set is curated by the clinical advisor; selection bias is a concern. We mitigate by including published-vignette cases and by inter-rater verification on a 50-case sub-sample.

**External validity.** The clinical advisor practices in Tamil Nadu; cases are tilted toward south Indian rural presentation patterns. Findings may not transfer to other South Asian, African, or Latin American low-resource settings. We acknowledge this and note it as a future-work direction.

**Conclusion validity.** Bonferroni correction is conservative; the effective power is lower than the nominal 80% for hypotheses where the assumed effect is near the detectable threshold. We report both the conservative and uncorrected results.

**Confounding from model knowledge contamination.** Several of the published-vignette cases may be present in model pretraining data. We mitigate by including 100 cases (40%) that are de-identified field observations not previously published. We report results separately for the published-vignette and field-observation strata.

### 6.10 Ethics and data handling

The protocol will be submitted for review to an institutional ethics committee in Tamil Nadu before any patient-derived data is incorporated. All cases derived from real patients require either (a) explicit informed consent obtained at the time of encounter for use in research and educational artifacts, or (b) de-identification to the standard of the DPDP Act and HIPAA Safe Harbor.

Images of identifying body regions (faces, identifying tattoos, etc.) are cropped or excluded. Image EXIF metadata is stripped. The release version of the eval set will be reviewed by Dr. Hari for cultural appropriateness and identifiability before publication.

No model is fine-tuned on patient data in this study. All inference is zero-shot from pretrained checkpoints, controlling the risk that patient data is incorporated into a model's parameters.

Frontier-model APIs are queried with explicit no-training opt-out (`zero data retention` mode where the provider offers it). Cases are pseudo-anonymized before transmission to any external API.

### 6.11 Timeline and milestones

| Phase | Duration | Milestone |
|---|---|---|
| Protocol finalization | 4 weeks | Pre-registration filed on OSF |
| Benchmark construction | 8 weeks | SentinelEval-250 frozen, IRR sub-study complete |
| Model harness implementation | 4 weeks | 33 cells runnable end-to-end |
| Development-set evaluation | 6 weeks | All cells run on 200-case dev split |
| Held-out replication run | 2 weeks | All cells run on 50-case replication split |
| Analysis and write-up | 6 weeks | Preprint deposited; submission to venue |
| **Total** | **30 weeks** | |

A separate continuous monitoring track will assess whether new model releases during the study warrant inclusion under a pre-specified amendment procedure.

---

## 7. Preliminary Results from Sentinel

The full evaluation outlined in §6 has not yet been executed. We report preliminary findings from the Sentinel development phase that motivate the formal study.

### 7.1 Internal triage evaluation (31 cases, Gemma 4 e4b)

On a 31-case pilot evaluation, with Gemma 4 e4b under the full Sentinel architecture (configuration F), RED-tier sensitivity was 29/29 = 100% (95% bootstrap CI: 88–100%). **Three-class accuracy** was 29/31 = 93.5%, with two YELLOW–GREEN borderline cases over-triaged to YELLOW; no GREEN cases were over-triaged to RED, so the RED-vs-not-RED specificity over the 2 GREEN gold cases was 100% (but the small denominator makes this a weak signal). The earlier draft of this paper conflated three-class accuracy with specificity; this revision separates them.

The 100% sensitivity figure does not survive interpretation at the 250-case benchmark scale and should be treated as an exploratory estimate from a small calibration sample. We report it because (a) the 88% lower bound is itself a clinically relevant signal and (b) the same number replicated across two MedGemma variants, which is qualitatively the substitutability finding that the formal H1 will test.

### 7.2 Production audit-log corpus (721 sessions, 66 with image)

A secondary source of preliminary data is the system's production audit log. Over the period 2026-05-13 through 2026-05-31, the deployed Sentinel instance recorded **721 audit-log entries** from active testing by the development team and clinical advisor. Of these, **66 entries** include an image side-file (ECG, wound photograph, or clinical-scene image). Distribution:

| Property | Distribution |
|---|---|
| Triage classes (image-bearing) | RED 60 (90.9%), YELLOW 5 (7.6%), GREEN 1 (1.5%) |
| Languages (image-bearing) | English 60 (90.9%), Tamil 6 (9.1%) |
| Top diagnosed conditions | Acute Coronary Syndrome 40, Acute Myocardial Infarction 22, Snake Bite Envenomation 18, Pulmonary Embolism 15 |
| Sessions where safety-net override fired on image-bearing cases | **0 of 66 (0%)** |

The 0% override rate on image-bearing sessions is structurally important. The safety net inspects symptom text for keyword patterns; when the text contains an explicit cue ("snake bit child", "crushing chest pain"), the safety net fires regardless of whether an image was supplied. When the text does *not* contain a cue and the image carries the discriminating signal, the safety net cannot see it. This is the architectural gap that motivates the proposed two-pass vision-as-sensor pattern (§8.3). The audit-log evidence is consistent with our theoretical claim that **a text-only safety net leaves image-only failure modes uncovered**.

The 721 total sessions and 66 image-bearing sessions, after redaction of any patient-identifying handwritten annotations and removal of zero-byte uploads (an artifact of intermittent connectivity during testing), will be incorporated as the *audit-log-derived* component of the SentinelEval-250 benchmark. They are *not* the primary source — the 250 cases will be curated for category balance and gold-label accuracy — but they constitute approximately one-quarter of the case volume and provide real-world phrasing distributions that synthetic vignettes do not.

### 7.3 Curated multimodal cases

Two curated images, used for development-time stress testing, illustrate the modality-dependent failure modes that motivate the planned multimodal evaluation. Both images are reproduced inline below; the original files are at `data/hand_image.jpeg` and `data/ecg_redacted.jpeg` in the project repository, and a per-case provenance record (including the redaction-rectangle coordinates for the ECG image) is at `data/ecg_redaction_provenance.json`.

![Figure 1. Case A — Suspected snake bite. Forearm with two distinct puncture wounds approximately 1 cm apart and a surrounding inflammatory halo. This image was used for the §7.3 / §7.5 vision-comparison testing.](data/hand_image.jpeg){ width=55% }

![Figure 2. Case B — 12-lead ECG (redacted). Right-side handwritten patient-identification fields removed for privacy; typed clinical measurements (HR 126, R-R 473 ms, P-R 143 ms, QRS 89 ms, QT/QTc 293/425) and ECG waveforms preserved. Multi-lead ST-segment changes are visible across V2–V4 and the limb leads.](data/ecg_redacted.jpeg){ width=85% }

**Case A: Suspected snake bite (Figure 1).** Gemma 4 e4b returned YELLOW with "No acute condition identified" when the text was "patient brought in with this wound on forearm, child screaming." The same image, presented to Gemini 2.5 Flash with text "I was sleeping outside and my hand began hurt very strongly", returned a structured emergency response with correct first-aid guidance. The full Gemini response is reproduced in §7.5. **The Gemma-4 visual module recognized the lesions but did not connect them to snake bite envenomation without an explicit textual cue.**

**Case B: 12-lead ECG (Figure 2).** A real 12-lead ECG photographed under clinic conditions, redacted at the upper-right handwritten patient-identification block and lower-right signature field; typed clinical measurements (HR 126, R-R 473 ms, P-R 143 ms, QRS 89 ms, QT/QTc 293/425, female, 64 years) and ECG waveforms preserved. Gemma 4 e4b's response varied substantially across textual phrasings:

| Phrasing | Triage | Top differential | Latency |
|---|---|---|---|
| "55-year-old with crushing chest pain and sweating for 30 minutes, ECG attached" + DM/smoker context | RED | Acute Myocardial Infarction (0.9). Reasoning: *"ECG shows significant changes consistent with acute cardiac ev[ent]."* | 17.5 s (M2 Max) |
| "patient has chest pain, see ECG" | RED | Acute Coronary Syndrome (0.8). Reasoning: *"ECG shows significant ST-segment changes (ST elevation in multiple leads), strongly suggesting acute myocardial ischemia."* | 7.0 s |
| "see attached ECG" (minimal text) | RED | "No acute condition identified" (0.5). Reasoning: *"…ST elevation in multiple leads, e.g., V2-V4, which is highly concerning for acute myocardial injury…"* | 3.0 s |

The ECG case reveals a *different* failure mode than the snake-bite case. Gemma 4's vision pipeline does recognize ST-segment elevation and articulates it in the reasoning field; however, with minimal text input, the JSON-schema-bound differential picker conservatively returns "No acute condition identified" despite the reasoning explicitly stating "highly concerning for acute myocardial injury." The triage class remains RED (probably the safety net's keyword-bound pre-check on "ECG" alone, which warrants further investigation in the formal study), but the differential and confidence are degraded.

This is a structural-output failure mode distinct from the perceptual failure mode of the snake-bite case. The architectural compensation for it is *not* the two-pass vision-as-sensor pattern (which would help if the model were missing the finding entirely). The compensation is, instead, an inter-field consistency check: if the reasoning field contains keywords like "ST elevation" or "myocardial injury," the differential picker should not select "No acute condition identified." We treat this as an architectural addition for v0.3.

### 7.4 Substitutability across SLMs (exploratory)

In the development phase, the same 31 cases were run against MedGemma 4 B Q8 and MedGemma 4 B Q6 in addition to Gemma 4 e4b. The RED-tier sensitivity figure was 29/29 in all three. Three-class accuracy varied (Gemma 4: 29/31 = 93.5%; MedGemma Q8: 28/31 = 90.3%; MedGemma Q6: 27/31 = 87.1%), suggesting that the safety net dominates the sensitivity outcome while the model's intrinsic capability is reflected in the narrative-quality and three-class-accuracy outcomes. We avoid the term "specificity" for the cross-SLM comparison because the 2-GREEN denominator is too small for a meaningful TNR claim.

These observations are descriptive only and underpowered for any formal claim; they motivate but do not substantiate H1. The 250-case evaluation will provide a properly powered test.

### 7.5 Frontier-model pilot batch (9 cases × 3 providers)

To motivate H2 with a structured pilot rather than a single anecdote, we ran a 9-case pilot against three frontier providers (Anthropic Claude Opus 4.7, OpenAI GPT-5, Google Gemini 2.5 Flash) with identical inputs to the Gemma 4 testing in §7.3. The pilot is exploratory: 9 cases is too few for inferential claims, and we report its findings as motivation for the formal study in §6, not as a substitute for it. The 9 cases comprise Cases A1/A2 (snake-bite image with two phrasings), Cases B1/B2 (redacted ECG image with two phrasings), and five text-only RED audit-log cases spanning all five emergency categories. All 27 calls were issued at temperature 0 with the same system prompt (Appendix E). The raw results are persisted at `data/frontier_pilot/results.jsonl`; the reproduction script is at `scripts/frontier_pilot.py`.

**Headline.** All three frontier providers returned RED on 9/9 cases (sensitivity 100%, 95% bootstrap CI: 66.4–100%). On the four image-bearing cases, all three providers selected a clinically correct top condition; the snake-bite image was identified as "suspected venomous snakebite" by all three even on the minimal-text Case A1 ("patient brought in with this wound on forearm, child screaming"), the exact case where Gemma 4 e4b returned YELLOW with "no acute condition identified."

| Provider | Model | Sensitivity | Median latency | p95 latency | Avg input tokens | Avg output tokens |
|---|---|---|---|---|---|---|
| Anthropic | claude-opus-4-7 | 9/9 (100%) | 6.9 s | 8.9 s | 546 | 343 |
| OpenAI | gpt-5 | 9/9 (100%) | 18.2 s | 54.8 s | 289 | 1415 |
| Google | gemini-2.5-flash | 9/9 (100%) | 4.0 s | 6.4 s | 210 | 146 |

Three observations from the pilot, all qualified as exploratory at n=9. (i) **The pattern predicted by H2 is consistent with what we observe.** Gemma 4 e4b returned YELLOW on the snake-bite image with minimal-text framing; all three frontier providers returned RED with a correct named condition. With four image cases the pilot is underpowered to claim a quantitative 30-point gap, but the qualitative direction is unanimous and stable across providers. The Gemini response on Case A1 was a single-token-equivalent label "Suspected Venomous Snakebite"; Claude's top condition was "Suspected venomous snakebite (two puncture marks with surrounding inflammatory halo)"; GPT-5's was "Suspected venomous snakebite (twin fang punctures; risk of envenomation)". The recognition is immediate, structured, and unanimous. (ii) **Latency stratifies the providers sharply.** Gemini Flash median 4.0 s; Claude Opus 4.7 median 6.9 s; GPT-5 median 18.2 s with a 54.8 s p95 outlier on the snake-bite text case. For a clinical-triage product the latency difference is operationally meaningful, but all three are below the typical CHW patience threshold. (iii) **GPT-5 produces materially longer outputs.** GPT-5 averaged 1,415 output tokens per case versus Claude's 343 and Gemini's 146. The longer output is more thorough but adds cost and latency without measurable benefit on this small sample.

The pilot does not test the formal H2 (image-only sensitivity ≥30-point gap) at any meaningful power — 4 image cases is too few. It does, however, provide a calibrated point estimate (n_image = 4, frontier sensitivity 4/4, Gemma sensitivity 0/4 from §7.3) that the gap is plausibly even larger than the hypothesized 30 points. The 50 image-only cases in SentinelEval-250 (§6.3) will provide the statistical basis for the formal claim.

### 7.5a Local SLM pilot (6 open-weight models · same 9 cases · unaugmented)

To complete the comparison loop, we ran the same 9 pilot cases against six locally hosted open-weight SLMs via the Ollama runtime, all in configuration U (no Sentinel scaffolding, no safety net, no JSON-Schema constraint beyond Ollama's structured-output `format`). Vision-capable models (Gemma 4 e4b, both MedGemma variants) ran all 9 cases; text-only models (Qwen 3 8B, Llama 3.2, gpt-oss 20B) ran the 5 text-only cases. The reproduction script is at `scripts/slm_pilot.py`; raw results are persisted at `data/frontier_pilot/slm_results.jsonl`.

| Model | Quant | Vision | Cases | RED-correct | Sensitivity | Median latency |
|---|---|---|---|---|---|---|
| Gemma 4 e4b (Sentinel production) | Q4_K_M | ✓ | 9 | 6 | 67% | 1.9 s |
| MedGemma 4B IT | Q8 | ✓ | 9 | 8 | 89% | 1.4 s |
| MedGemma 27B IT | Q4_K_M | ✓* | 9 | 5 | 56%† | 19.0 s |
| Qwen 3 8B | Q4_K_M | ✗ | 5 | 4 | 80% | 7.0 s |
| Llama 3.2 (latest) | Q4_K_M | ✗ | 5 | 5 | 100% | 1.6 s |
| gpt-oss 20B | Q4_K_M | ✗ | 5 | 0‡ | 0%‡ | 4.5 s |

*Vision available but failed on all 4 image-bearing cases with `500 Internal Server Error` from the Ollama runtime — likely a model-loading interaction with the image format on this checkpoint. Reported as 5/9 with the image cells treated as failures; the alternative reading (5/5 = 100% on the text-only cases the model successfully responded to) is also informative and we report both.

†When restricted to the text-only cases the model actually responded to, MedGemma 27B scored 5/5 (100%). The image-cell failures are infrastructural rather than substantive.

‡gpt-oss 20B returned zero parseable JSON outputs on the five text cases — the model's reasoning-tagged output format conflicts with Ollama's `format: json` constraint as currently invoked. A re-run with the model's native chat-completion format is required before this number is reportable as a clinical-capability claim.

**Three observations from the SLM pilot, beyond the headline sensitivity numbers.**

First, **the snake-bite image failure of Gemma 4 e4b replicated under both phrasings** (A1: YELLOW, "Infection (Cellulitis/Abscess)"; A2 with "sleeping outside" cue: YELLOW, "Insect bite reaction or cellulitis"). Even with a contextual cue ("sleeping outside") that is highly diagnostic for a frontier model (cf. the Gemini response in §7.3), Gemma 4 e4b did not connect the visual finding to snakebite envenomation. This is a perceptual-prior failure, not a textual-cue failure. MedGemma 4B Q8 correctly returned RED for both image cases (with the generic top-condition "Wound Management" rather than "Snake Bite Envenomation," which is suboptimal but operationally adequate).

Second, **the atypical-MI text case (T1: 60-year-old woman with jaw pain, nausea, fatigue, T2DM + HTN) was misclassified as YELLOW by three of the six SLMs**: Gemma 4 e4b returned "Dental infection or periodontitis," MedGemma 4B Q8 returned "Gastroenteritis," and Qwen 3 8B returned "Myocardial Infarction (MI)" but classified the triage class YELLOW rather than RED. All three frontier providers returned RED for this case. This is the classic atypical-ACS-in-women failure mode that motivates the Sentinel safety net's `rf_atypical_acs_high_risk` rule. **The architectural compensation that this paper argues for — the deterministic keyword-driven safety net — is the mechanism that would cause all three of these SLMs to return RED in production**, regardless of their unaugmented narrative output.

Third, **Llama 3.2 unexpectedly scored 5/5 on the text cases — perfect sensitivity** — despite being a general-purpose model with no medical fine-tuning. Mean latency was 1.6 s, the fastest in the panel. This is a single-pilot data point and does not generalize beyond the 5 cases, but it is consistent with the substitutability claim that, on text-described emergency cases with clear keyword cues, the model is a substitutable component and a small general model can match a medical-domain model. The formal H1 test on SentinelEval-250 will quantify how broadly this holds.

**Headline comparison: unaugmented SLM vs unaugmented frontier on the same 9 cases.**

| Class | Best SLM (vision-capable) | All 3 frontier providers |
|---|---|---|
| Image cases (n=4) | MedGemma 4B Q8: 4/4 RED | 12/12 RED (all 3 providers × 4 cases) |
| Text cases (n=5) | Llama 3.2: 5/5 RED | 15/15 RED (all 3 providers × 5 cases) |
| Image-only minimal-text snake bite (Case A1, the canonical failure mode) | MedGemma 4B Q8: RED with "Wound Management" | All 3: RED with "Suspected venomous snakebite" |
| Atypical MI (Case T1) | Llama 3.2: RED with "Myocardial Infarction" | All 3: RED with "Acute coronary syndrome (atypical presentation)" |

Within the present small pilot the headline finding is that the *best-case* SLM matches frontier sensitivity on every cell. What differs is **(a) the consistency across SLMs** (frontier sensitivity is uniformly 100% on every cell; SLM sensitivity ranges from 0/5 to 5/5 within the same task) and **(b) the specificity of the top-condition label** (frontier providers name "snakebite envenomation" precisely; the best SLM names "Wound Management" or similar generic categories). The deterministic safety net plus KB-grounded JSON Schema (configurations S and F in §6.2) is the mechanism by which the SLM's variable specificity is bounded — the model picks a `condition_id` from the curated list, not a free-form label.

The full SentinelEval-250 study (§6.3) is required before any of these single-pilot observations can be reported as a quantified gap with confidence intervals.

The full Gemini 2.5 Flash response to a comparable image-only snake-bite case under the public Gemini consumer interface — obtained independently of the present pilot — is reproduced verbatim below to illustrate the level of clinical guidance frontier models can generate under no scaffolding:

> Immediate Medical Attention Required. I am an AI, not a medical professional, but the image you shared shows two distinct puncture wounds that strongly resemble a bite from a venomous snake or another animal with fangs. Given that you were sleeping outside and are experiencing severe pain, this is a potential medical emergency. Please take the following steps immediately: Call Emergency Services… Stay Calm and Still… Position Your Arm at or below heart level… Remove Constrictive Items… Do Not Interfere with the Wound (do not apply a tourniquet or attempt to suck out the venom)…

The gap with Gemma 4 e4b on the same image and comparable text is consistent with the prevailing literature on multimodal compositional reasoning at scale [@gemini25report; @anthropicvalidation2025] and with the present pilot's empirical findings.

### 7.6 Bilingual narrative quality (anecdotal)

Narrative output in Tamil and Hindi was reviewed informally by Dr. Hari during development. Tamil output was rated subjectively as "usable but stilted, lacks the register a Tamil-speaking PHC physician would expect"; Hindi output was rated as "more fluent but introduces occasional dosing-unit errors (mg vs. mcg) in transport recommendations." Both findings motivate the formal Likert-rated quality assessment in H6.

### 7.7 Speech-to-text in Indic languages

Faster-Whisper at the `small` (244 M) checkpoint was integrated as an offline STT module and subsequently removed. English transcription was acceptable; Tamil and Malayalam transcription rendered the input unusable for downstream clinical reasoning. The production system uses the Web Speech API on Chrome (cloud STT) and on-device Apple STT on Safari, with the offline-decoupling claim restricted to the diagnosis step. This is reported as preliminary observation, not as a formal result; the planned study does not include STT in its primary outcome but will collect operator-reported voice-input failure modes as a secondary observation.

---

## 8. Architectural Compensations: A Proposed Taxonomy

The principal theoretical contribution of this paper is the proposal that small open-weight models are competitive with frontier models only when paired with deliberate architectural scaffolding, and that this scaffolding can be specified as a taxonomy of four named patterns.

### 8.1 Pattern 1: Deterministic Safety Net (DSN)

A DSN is a rule-driven module that runs before and/or after the model and that can unilaterally override the model's decision in specified circumstances. In Sentinel, the DSN consists of 18 keyword/clinical-condition patterns curated by a clinician; if any pattern fires on the input symptoms, the system's triage class is forced to RED regardless of the model's output.

The DSN is *not* a regex pre-filter in the sense of input sanitization. It is a clinical-rule layer with the same authority as the model in determining the output. Its existence permits the model to be a *writer* — generating narrative, recommendations, and structured output — rather than the *decision-maker*.

The DSN is the necessary condition for the substitutability claim (H1): if the safety net is doing the high-stakes decision, the model's intrinsic capability matters less for the high-stakes outcome.

### 8.2 Pattern 2: KB-Grounded JSON Schema Output (KGS)

A KGS pattern combines two mechanisms: (i) a JSON Schema constraining the model's output structure, enforced at decoding time via Ollama's `format` parameter or equivalent in the frontier-API analog; (ii) an enumerated `condition_id` field whose allowed values are drawn from a curated knowledge base. The model can *select* a condition but cannot *invent* one.

KGS eliminates a large class of hallucination failures (the model declares a condition that does not exist or is not relevant to the scope) and forces the model's output into a form that the downstream deterministic post-processor can reason over.

### 8.3 Pattern 3: Two-Pass Vision-as-Sensor (VAS)

VAS decomposes a multimodal clinical task into two sequential calls to the model. Pass 1 issues a narrow, structured-output vision-only query: "Examine this image. Report which of the following enumerated findings are present: [puncture wounds, ST elevation, pupil constriction, …]." The output is a structured list of findings. Pass 2 issues the standard clinical-reasoning prompt with the findings from Pass 1 appended as evidence in the symptom field, and (critically) with the DSN extended to accept image-derived findings as triggers in the same keyword/rule namespace as text-derived findings.

VAS is hypothesized to close the snake-bite-image gap (H4). The intuition: asking the model "do you see puncture wounds in this image, yes or no" is a question a small VLM can answer; asking it "is this a snake-bite emergency given the image and rural-India-monsoon context" is a question only a frontier model can answer reliably. VAS reduces the small model's contribution to the kind of question it can answer.

### 8.4 Pattern 4: Selective Frontier Escalation (SFE)

SFE introduces a frontier model as a fallback for cases the SLM-plus-DSN-plus-KGS pipeline cannot confidently resolve. The escalation trigger is operationalized as: top-differential confidence below a threshold (e.g., 0.5) AND triage class not RED (RED cases proceed directly to escalation without frontier intervention) AND network connectivity available AND user consent obtained at registration to permit cloud escalation for ambiguous cases.

SFE preserves the offline guarantee for confident cases (the majority) and provides a frontier capability for uncertain ones. The privacy trade-off must be explicit to the user; in Sentinel's design, the CHW would be informed at deployment-time which cases will potentially trigger a cloud escalation and asked to consent at the level of the deployment, not per-case.

SFE is not included in Sentinel's primary deployment for clinical-product reasons (the offline-first framing is the product differentiator) but is included in the proposed taxonomy because it is a natural fit for other clinical-AI products where intermittent network availability is the deployment surface.

### 8.5 Pattern 5: Domain LoRA Adaptation (DLA)

DLA introduces parameter-efficient fine-tuning [@hu2021lora; @peft] of the open-weight base model on a domain-specific corpus, producing a small adapter (typically tens to hundreds of megabytes for an 8B–31B base) that can be loaded alongside the base weights at inference time. Unlike Patterns 1–4, DLA modifies the model itself rather than the scaffolding around it.

We treat DLA as the fifth architectural pattern rather than as a separate model-choice question because its trade-offs are pipeline-level: the adapter sits between the base weights and the structured-output decoder, can be swapped per deployment context, and interacts with the safety net in non-obvious ways (a domain-adapted model may emit narratives that the keyword-rule layer trained against base-model outputs no longer matches, requiring rule recalibration).

We have not yet performed LoRA fine-tuning on Sentinel's production Gemma 4 e4b variant; the planned study (§6.2) does not include LoRA-adapted configurations in the primary 36-cell design. However, a sister project of the first author (*Path to Care*, AMD Developer Hackathon, May 2026) provides empirical evidence on what LoRA fine-tuning of Gemma 4 31B-it costs and yields in the same clinical domain. We discuss the Path to Care findings in detail in §9.8 below; the headline numbers relevant to the DLA pattern are: (a) a +7.0 percentage-point top-1 accuracy lift on a 100-case held-out dermatology classification task (SCIN, 16 conditions) from a 90 MB adapter trained in ~38 minutes on a single AMD MI300X; (b) a non-result on the smaller 30-case triage urgency set because the base zero-shot model was already at the ceiling; and (c) a methodological lesson — at ~35 training rows per class the LoRA mode-collapsed, requiring a corrected experiment at ~60 rows per class with multi-label probability-distribution targets rather than single-label targets. The Path to Care submission report is at the project repository [@pathtocare2026].

Implications for the Sentinel architecture: DLA is an attractive next-iteration pattern for the v0.3 release, primarily as a way to address the cultural-prior failures documented in §9.6.b (the cultural-register and dosing-unit-error issues that DSN cannot fix). A Tamil/Hindi/Malayalam-specific LoRA adapter trained on clinician-curated narrative pairs from the audit log would target exactly the cultural-register gap that the model's intrinsic capability does not close. The Path to Care evidence suggests this is feasible in tens of minutes of compute on a single high-end accelerator.

### 8.6 Composition

The five patterns compose. DSN is necessary for the substitutability claim. KGS is necessary for the safety of KB-bounded output. VAS extends DSN to image inputs. SFE adds a frontier safety-net at the cost of network dependency. DLA improves the model's intrinsic capability on the target domain at the cost of training infrastructure and adapter-deployment plumbing. Sentinel deploys DSN + KGS in v0.1; we propose DSN + KGS + VAS for v0.2 (subject to the H4 evaluation result); SFE and DLA are slated for v0.3 and beyond.

---

## 9. Discussion

### 9.1 Reframing the "small versus frontier" question

The principal interpretive claim of this paper is that the question "should I use a small or a frontier model for clinical X" cannot be answered as a model-versus-model comparison. The right question is *what pipeline composition, including both the model and the deterministic scaffolding around it, satisfies clinical X within the deployment constraints*. The answer for Sentinel — an SLM-plus-DSN-plus-KGS pipeline — would not transfer to a product where the deployment surface is a Western emergency department with reliable connectivity, full PHI consent, and a frontier-model budget. The right answer for that product is likely a frontier model with looser scaffolding.

This reframing has policy implications for AI-system regulators (FDA, EMA, India's CDSCO). A regulatory framework that licenses a model is misaligned with the unit at which clinical risk is actually controlled. The pipeline is the unit; the model is one (substitutable, in the architectures we describe) component.

### 9.2 Economic implications

If the substitutability claim (H1) holds in the formal evaluation, the implication is that population-scale clinical AI deployments in low-resource settings can be priced as one-time hardware procurements rather than recurring API subscriptions. The actual cost comparison, however, is **not** unambiguously in the SLM's favor on a pure per-query basis. Appendix D works the numbers explicitly: at a CHW query volume of ~5 emergencies per week (the field-typical rate from Dr. Hari's catchment), a refurbished-laptop SLM costs ~$83/CHW/year (hardware amortization), whereas a Gemini Flash multimodal API call at 2026 prices runs to only ~$13/CHW/year including cellular-data overhead. **At low query volumes the frontier-API path is cheaper, not more expensive.** The earlier draft of this paper claimed ~$25–50 M/year in API spend forestalled at NHM scale; that figure was computed at much higher per-query rates than current public pricing and we retract it in this revision.

The economic argument for SLMs is therefore not a per-query cost argument. It is a **structural** argument: the SLM path is operationally viable in settings where the frontier-API path is *not deployable at all* — no reliable network, no per-call billing infrastructure, no consent posture acceptable for cross-border transfer of PHI. When connectivity, billing, and consent are all available, the cost comparison flips in the other direction (cheaper to call a frontier API than to amortize a laptop). The right framing is therefore that the SLM path *unlocks deployment surfaces the frontier path cannot reach*, not that it is cheaper everywhere. Builders deciding between the two should price the surfaces, not just the per-query unit economics.

### 9.3 Implications for the open-weight ecosystem

The Sentinel architecture treats the SLM as a commodity. If this generalizes, the design pressure on open-weight model releases shifts from "compete on raw capability" to "ensure substitutability within a downstream architecture." Features like deterministic seeded inference, version pinning, and inspectable confidence outputs become more important than incremental capability gains. The MedGemma release [@medgemma2025] is, in our reading, an instance of this pressure: a domain-fine-tuned open-weight checkpoint that is competitive with general models on the medical-task subset.

### 9.4 Cultural and linguistic considerations

The Sentinel observation that Whisper-small fails on Indic-language medical STT, while frontier providers (Google, Apple) succeed, is a reminder that open-weight ecosystems systematically under-cover non-English contexts. The economic argument for SLMs in low-resource settings is partially undermined if the SLM's training data does not represent the languages of the deployment. This points to the importance of language-specific open-weight models (Sarvam-1 for Indian languages [@sarvam2024], various community-driven multilingual variants) and to fine-tuning as a productization step.

### 9.5 What does the SLM actually contribute, if the safety net carries the triage decision?

A sharp critique of the Sentinel architecture, raised in external review of this draft, runs as follows: *if a deterministic keyword rule can override the LLM's triage class, and if the bake-off across three SLMs showed identical RED-tier sensitivity, then the SLM is by construction not the decision-maker; it is a sophisticated JSON-schema-populator that could in principle be replaced by a simpler template engine, undermining the case for using an LLM at all.*

The critique is correct as stated but incomplete as a characterization of what the model does. The DSN is the decision-maker for the **triage class**, which is one field of the structured output. The SLM contributes four other components that a non-LLM template engine cannot:

1. **Unstructured-input parsing in four languages.** The CHW enters symptoms as free text or transcribed speech in English, Hindi, Tamil, or Malayalam. A template engine that requires structured input (which symptom from a dropdown, which onset time from a picker) is not the product. The CHW types "60yo woman with jaw pain, nausea, fatigue for 1 hour, diabetic and HTN"; the SLM parses that into the structured representation that downstream components use. Replacing this with a template-driven UI doubles the data-entry burden and is exactly the wrong trade for a workflow where the CHW is mid-encounter with a sick patient.

2. **Grounded narrative generation.** The differential's `reasoning` field, the during-transport protocol's adapted phrasing for the specific patient, and the WhatsApp escalation message in the appropriate language for the hub physician are not lookup-table outputs. They are generated narratives that adapt to the case's specifics (e.g., a 60-year-old diabetic with jaw pain gets a different rationale paragraph than a 25-year-old non-diabetic with the same complaint, even though both route to ACS-suspected RED). A template engine produces stereotyped output that the receiving physician can detect at a glance.

3. **Calibrated confidence values.** The model emits a confidence score per differential candidate that, in our preliminary data, correlates with downstream gold-label accuracy. The downstream UI uses this to decide whether to ask a clarifying question (`/api/v1/clarify`) before finalizing. A keyword-rule engine cannot produce a calibrated confidence; it either fires or it does not.

4. **Cultural and contextual nuance in recommendations.** The model adapts dosing units (mg vs grain), transport phrasing ("rush to nearest 108 ambulance" vs "call EMS"), and follow-up language to the deployment context. This is imperfect (see §7.6 on dosing-unit errors in Hindi), but it is qualitatively different from the deterministic output of a templating engine.

The architectural claim is therefore not that the SLM is *unnecessary*; it is that the SLM is the right component for the four roles above, and the DSN is the right component for the triage-decision role. Conflating these into "the LLM does triage" is the failure mode that this paper's architectural taxonomy is intended to prevent — at both the design level (where the model gets too much responsibility) and the evaluation level (where the model is asked to do all the work).

A stricter version of the critique remains live: *the SLM's narrative contributions in §9.5.1–4 above are not formally evaluated for clinical value in this paper.* The clinician-rated Likert assessment in H6 will address the narrative-quality dimension; the calibration-error metric in §6.4 will address the confidence dimension; and a future extension of the study should compare the full SLM pipeline against a templated-output baseline directly. We treat this as a future-work direction (§11) rather than dismissing the critique.

### 9.6 Failure-mode taxonomy

We propose, on the basis of the Sentinel observations, that clinical-AI failure modes for SLMs cluster into three groups: (a) *compositional reasoning failures*, exemplified by the snake-bite case, where the model has the constituent capabilities (vision, language, medical knowledge) but does not integrate them; (b) *cultural-prior failures*, where the model does not weight context appropriately for the deployment setting; (c) *brittle structured-output failures*, where the model's instruction following degrades under long structured prompts. The architectural compensations in §8 address (a) and (c) directly; (b) is harder to address architecturally and motivates the case for fine-tuning on culturally appropriate data.

### 9.7 The offline-claim tension: voice intake versus diagnose

The Sentinel product claim is "offline triage on a clinic laptop." External review of this draft, and the Whisper-revert experience documented in §7.7, raise a fair tension: voice transcription in the deployed system uses cloud STT (Chrome's Web Speech API on Chrome; Apple's on-device STT on Safari). The claim that *the diagnostic pipeline* runs offline is accurate; the claim that *the entire user workflow* runs offline is not, in the deployed configuration, with voice input.

We treat this as a real but bounded compromise. Three points:

First, **the diagnostic pipeline — symptom parsing, safety check, model inference, KB grounding, safety override, escalation-message generation, audit log — runs offline.** No PHI leaves the device during diagnosis. The cloud STT call transmits only the audio of the CHW's spoken symptoms, briefly, before the rest of the pipeline runs locally. This is a different surface area than "all clinical reasoning happens on a cloud API."

Second, **voice intake is a convenience, not a requirement.** The deployed UI accepts typed input as the primary mode and voice as an optional accelerator. A CHW operating with no connectivity can still use the system fully; they type rather than speak. The "voice needs internet on Chrome" hint surfaced in the demo UI documents this constraint explicitly to the user.

Third, **the offline-STT direction is a real research investment, not a closed problem.** Whisper-small failed on Indic medical terms; AI4Bharat's IndicConformer family and Sarvam-1's ASR component are stronger candidates that we have not yet evaluated. A future iteration of Sentinel will revisit on-device STT with these models, and the formal study will collect operator-reported voice-input failure-mode telemetry as a secondary observation (§6.4).

The product-positioning lesson, however, is straightforward: builders should not claim "fully offline" without qualifying which steps are offline and which are not. We have updated the §4 product description to reflect this distinction explicitly.

### 9.8 Empirical evidence from a sister project: what LoRA fine-tuning revealed in *Path to Care*

The first author led an adjacent project, *Path to Care*, built for the AMD Developer Hackathon (May 2026) in the same clinical domain (rural Tamil Nadu, urgency triage from image + text, the same five-emergency scope) but using a different base model and a different hardware target: Gemma 4 31B-it on a single AMD Instinct MI300X with 192 GB HBM3. The project performed two distinct LoRA SFT experiments [@pathtocare2026] whose findings inform the architectural-taxonomy argument here.

**Experiment 1 — hand-built 30-case urgency triage set (negative result, informative).** LoRA SFT with rank-16, α=32, lr=2e-4, 2 epochs converged in 32 seconds (loss 3.90 → 0.58, 45M trainable parameters = 0.14% of the base model). The tuned adapter produced *identical* held-out performance to the zero-shot baseline: 96.7% exact-match urgency (29/30), 0% false-negative Red→Green. This is a ceiling effect — the base model was already at the limit of the hand-crafted evaluation set — but the result is informative for two reasons: (a) it demonstrates that LoRA SFT on Gemma 4 31B-it on AMD ROCm is reproducible at the 32-second-per-epoch scale, which is operationally relevant for deployment iteration; and (b) it independently confirms the substitutability claim (H1) — fine-tuning does not move a metric that the base model has already saturated.

**Experiment 2 — SCIN dermatology classification (positive result with caveats).** The project used Google Research's SCIN dataset [@scindataset], a consumer-dermatology corpus with weighted multi-condition labels and Fitzpatrick skin-type metadata. Restricted to the 16 most-occurring conditions, trained on ~60 rows per class with multi-label probability-distribution targets (rather than single-label targets — see the negative-result discussion below), rank-8, α=16, lr=1e-4, 1 epoch, ~239 training steps, 11.5 minutes of training plus 25.4 minutes of evaluation. End-to-end on a single MI300X: ~45 minutes including model download.

| Metric | Zero-shot Gemma 4 31B | + SCIN top-16 LoRA | Δ |
|---|---|---|---|
| Top-1 primary-condition accuracy | 28.0% | **35.0%** | **+7.0 pp** |
| Top-3 set-match (SCIN paper metric) | 71.0% | 68.0% | −3.0 pp |

The adapter is 90 MB on disk. The trade-off is honest: tuning consolidates probability mass into the most-confident prediction, raising top-1 at the cost of top-3 set coverage. For the III–IV majority Fitzpatrick bucket both metrics improved; for I–II it is a top-1-for-top-3 trade.

![Figure 3. SCIN top-16 LoRA fine-tune loss curve from the Path to Care sister project (Gemma 4 31B-it base, rank-8 adapter, single AMD MI300X). Training loss declines monotonically over 239 steps (6.6 → 0.07); eval loss tracks closely (0.087 → 0.068); the train–eval gap stays under 0.02 throughout. Contrast with the failed 34-class single-label run (not shown) where loss plateaued at 0.04 by step 30 and the model mode-collapsed. The shape of the healthy curve is the diagnostic — monotone decline with a tight eval band — and the per-class sample threshold above which it appears is approximately 60 rows.](data/path_to_care_scin_top16_lora_loss.png){ width=80% }

**Experiment 1.5 — what didn't work and why (the substantive methodological finding).** Two prior SCIN attempts at the same base model failed: (a) LoRA SFT on 34 fine-grained classes with hard single-label targets at lr=2e-4, rank-16, 3 epochs regressed top-1 by 11 percentage points (24.0% → 13.0%) — the model mode-collapsed, stopping emission of common classes (`Eczema` from 14 predictions to 0, `Allergic Contact Dermatitis` from 11 to 0) and over-emitting rare ones (`Hypersensitivity` from 0 to 15); (b) the same 34-class setup with top-k probability targets at lr=1e-4, rank-8, 1 epoch was less catastrophic but still regressed by 3 percentage points. The corrected experiment that yielded the +7.0 pp lift restricted to 16 classes (raising per-class sample count from ~35 to ~60), used multi-label probability-distribution targets, and reduced rank and learning rate together. The full failure-mode analysis is at the project documentation [@pathtocare2026, §6.1].

**Three implications for the Sentinel architectural argument.**

(i) **Substitutability across SLMs (H1) is corroborated by an independent within-project bake-off.** The Path to Care project tested MedGemma 27B-it against base Gemma 4 31B-it on the SCIN classification task and found they were within noise (n=100), with both capping around 70% top-3 set-match. As the project's submission report puts it: *"the lever is not the model."* This is the same finding the Sentinel three-SLM bake-off produces (Gemma 4 e4b vs. MedGemma 4B Q8 vs. MedGemma 4B Q6 on the 31-case pilot; §7.4), and the convergence across two clinically-adjacent projects strengthens the claim beyond what either pilot would justify alone.

(ii) **The deterministic safety net pattern (DSN) is independently re-implemented in Path to Care and observed to fire live during evaluation.** The project's "cardinal rule rewriter" (`core/cardinal_rule.py`) caught a base-model output that violated the project's structured-output requirement on a Yellow-urgency case (Y09) during evaluation, rewriting the output before the orchestrator returned it; the rewrite is logged at `logs/cardinal_rule_rewrites.log`. The two projects arrived at the same architectural primitive independently, in the same clinical domain, against the same kind of base-model failure mode. We treat this convergence as a stronger argument for the DSN pattern than either project alone provides.

(iii) **The DLA pattern is operationally cheap in compute and dollars but expensive in evaluation discipline.** A 90 MB adapter trained in ~38 minutes on a single AMD MI300X is operationally trivial. The non-trivial cost is the *evaluation harness* — Path to Care had to discover, through three iterations, that token-level eval loss does not correspond to the actual classification metric, and that small-data LoRA can mode-collapse silently while looking healthy in the trainer. Builders adopting DLA for a Sentinel-like pipeline should expect the evaluation harness to be the load-bearing investment, not the training harness.

The Sentinel formal study (§6) will add a DLA condition to the secondary-analysis design once the v0.3 release is built: a Tamil/Hindi/Malayalam-narrative LoRA adapter trained on clinician-curated audit-log outputs, evaluated against the cultural-register and dosing-unit-error failure modes documented in §7.6.

---

## 10. Limitations

This paper is, by design, a research-plan paper rather than a study-report paper. The principal limitations are:

1. **The evaluation has not been executed.** Section 6's protocol is the deliverable; sections 7's preliminary results are not a substitute. Until SentinelEval-250 is constructed, peer-reviewed for clinical accuracy, and run against the model panel, the hypotheses are not tested.

2. **The case study is a single product.** Sentinel Health is one deployment in one geography with one clinical advisor. Generalization to other low-resource clinical AI products requires either replication or careful argumentation about which Sentinel-specific design choices were essential to the architectural claims.

3. **The architectural taxonomy is proposed, not empirically validated.** Patterns 1 and 2 are deployed in Sentinel; Patterns 3 and 4 are not, and their hypothesized effects (H4 in particular) await the planned evaluation. **The two-pass vision-as-sensor pipeline (Pattern 3) is the critical-path validation question for the whole architectural argument.** If the formal SentinelEval-250 evaluation finds that the two-pass pipeline does not substantively close the image-only-case gap, the SLM-plus-scaffolding posture for image-bearing clinical reasoning collapses, and the right answer for image-heavy deployments becomes either (a) a frontier-API path with the connectivity and consent compromises that entails, or (b) a much larger SLM than current laptop-class hardware can host. We flag this as the single most important risk to the paper's central architectural claim, and the planned study is designed primarily to resolve it.

4. **The SLM's narrative contributions are not formally evaluated against a non-LLM baseline in this work.** §9.5 argues that the model contributes free-text parsing, narrative generation, calibrated confidence, and cultural register beyond what a non-LLM template engine can do. The clinician-rated Likert assessment (H6) and the calibration-error metric (§6.4 secondary outcome 4) test these dimensions against quality standards, but they do not test them against a templated-output baseline. A future extension should compare the full SLM-plus-DSN pipeline against a DSN-plus-template-engine baseline on the same case set, to quantify the marginal contribution of the SLM. We treat this as an open question rather than a foregone conclusion.

5. **The offline-claim is qualified, not absolute.** Voice intake in the deployed system uses cloud STT (§9.7). The diagnostic pipeline itself runs offline. Builders citing this work should propagate the qualification — the architectural argument applies to the *clinical-reasoning* steps, not to the entire user workflow under all deployment configurations.

6. **The cost analysis depends on assumed query volumes.** Population-scale deployment numbers (~5 queries/CHW/week × ~1M CHWs) are estimates; actual operational query volume could be 10× higher or 5× lower depending on adoption.

7. **The frontier-model API access landscape changes faster than the publication cycle.** Model versions pinned in §6.2 may be deprecated by the time the evaluation completes. We commit to running against the latest available version of each frontier provider at the time of the held-out replication run, and to re-running the analysis if version drift exceeds a pre-specified threshold.

8. **No formal cost-effectiveness or QALY analysis is conducted.** The clinical outcome of interest in Sentinel is reduced time-to-physician-decision, but the link to mortality reduction or quality-adjusted life years is not measured here. Such a study would be a follow-up downstream of the present plan.

9. **The image-only failure observation in §7.3 is a single case.** It is presented to motivate H2 and H3, not to substantiate them. Even an n = 1 observation, if dramatic enough, is worth reporting as motivating evidence; we do not treat it as conclusive.

---

## 11. Future Work

The proposed plan defines a 30-week study. Several follow-up directions are anticipated.

**Multi-site replication.** Replication of the SentinelEval-250 benchmark with clinical advisors in other low-resource settings (West Africa, Bangladesh, rural Latin America) to test the external validity of the substitutability claim across deployment contexts.

**Fine-tuning analysis (DLA / Pattern 5).** A formal evaluation of whether domain LoRA fine-tuning improves the SLM's intrinsic capability on the failure modes identified in §7 — specifically (a) the image-only compositional reasoning failure exemplified by the snake-bite case, and (b) the cultural-register / dosing-unit-error failures in Indic-language narrative generation. The sister-project evidence in §9.8 (a +7.0 pp top-1 lift on SCIN top-16 dermatology classification from a 90 MB Gemma 4 31B LoRA adapter trained in ~38 minutes on a single MI300X) suggests this is operationally cheap. The harder open question is whether DLA can address the *cultural-prior* failures (§9.6.b) that DSN cannot. The Sentinel v0.3 release plans a Tamil/Hindi/Malayalam-narrative LoRA adapter trained on clinician-curated audit-log outputs; the formal study will evaluate this adapter against the cultural-register Likert scores (H6 secondary). If DLA closes the cultural-register gap, the scaffolding can be lighter on that dimension; if it does not, the scaffolding's central role is reinforced. The Path to Care methodological finding — that ~35 training rows per class causes mode collapse and ~60 rows per class is the working threshold for Gemma 4 31B — is directly transferable to the Sentinel adapter-training design and constrains the audit-log collection requirement.

**Adversarial-robustness study.** A dedicated red-team study testing how the four-pattern composition responds to deliberately adversarial inputs, including indirect prompt injection through image OCR.

**Longitudinal field study.** A six-month operational deployment with a single PHC catchment area, measuring clinical-outcome proxies (time-to-handoff, escalation acceptance rate at the hub physician, adverse events).

**Cost-effectiveness modeling.** Integration with health-systems-research methodology to estimate QALY impact at population scale, parameterized to NHM budgeting frameworks.

**Comparative architectural studies.** Replication of the four-pattern taxonomy in non-clinical high-stakes domains (legal document review, financial fraud screening, regulated industrial-control assistance) to test whether the taxonomy is clinically specific or more broadly applicable.

---

## 12. Conclusion

The choice between small open-weight language models and frontier proprietary models is, as commonly framed, an underspecified question. The pipeline composition — model plus deterministic scaffolding — is the right unit of evaluation. We have presented a deployed clinical-triage system, *Sentinel Health*, whose architecture treats the small open-weight model as a substitutable writer rather than a decision-maker, paired with a clinician-curated deterministic safety net and KB-grounded JSON Schema. We have reported preliminary observations (100% RED-tier sensitivity on a 31-case pilot, replicated across three small models; a representative image-only failure mode that a frontier model recovers) and a single counter-case where a frontier model substantively outperforms a small open-weight model under no scaffolding.

We have proposed a multi-model, pre-registered evaluation across twelve candidate language models, five clinical-scope categories plus a GREEN-distractor category, four target languages, and 250 cases, with seven explicit hypotheses, a defined statistical methodology, a sample-size justification, an ethics-and-data-handling specification, and a 30-week timeline. We have also proposed an architectural taxonomy — deterministic safety net, KB-grounded JSON Schema, two-pass vision-as-sensor, selective frontier escalation — as the framework within which small and frontier models compose.

The principal claim is not that small models will win, or that frontier models will lose. The principal claim is that the right answer depends on the deployment surface and the scaffolding, and that the engineering literature on clinical AI is impoverished by an apples-to-apples model comparison that the field has uncritically adopted. The proposed study, by contrast, evaluates the *pipeline*, with the model as one variable. We believe this is the level at which clinical-AI deployments will actually be decided in the coming decade.

---

## Ethics Statement

The Sentinel Health system's preliminary evaluation was conducted on synthetic and de-identified clinical vignettes. No identifiable patient data was used in model selection or pipeline tuning. The clinical advisor (Dr. P. Hari Subacini) consented to her name and role being attributed in this work. The planned evaluation (§6) will undergo formal ethics-committee review before any patient-derived data is incorporated. Cases derived from real encounters will require explicit informed consent obtained at the time of encounter and reviewed for cultural and linguistic appropriateness before publication of the benchmark.

The deployment of any clinical-AI tool in a low-resource setting raises broader equity considerations not fully addressed in this paper. We do not claim that an open-weight SLM-based deployment is universally preferable to a frontier-API deployment; we claim only that within the deployment constraints typical of rural CHW work, the SLM-plus-scaffolding architecture is operationally viable and the frontier-API architecture is not.

## Data and Code Availability

The Sentinel Health source code is publicly available at `github.com/SankarSubbayya/sentinel-health` under Apache License 2.0. The current knowledge base, red-flag rule set, JSON Schema, and pilot evaluation case set are committed to that repository. The SentinelEval-250 benchmark proposed in §6.3 will be released under CC-BY 4.0 upon completion of the planned study, subject to the consent and de-identification constraints specified in §6.10.

Model checkpoints used in the planned evaluation are: Gemma 4 (Google DeepMind; weights at huggingface.co/google), MedGemma (Google; huggingface.co/google), Aloe-Beta-8B (HPAI-BSC, Barcelona Supercomputing Center; huggingface.co/HPAI-BSC), Llama 4 (Meta; llama.com), Mistral Small 3 (Mistral AI; huggingface.co/mistralai), Qwen 3 (Alibaba; huggingface.co/Qwen), Phi-4 (Microsoft; huggingface.co/microsoft), gpt-oss 20B (OpenAI; huggingface.co/openai). Frontier-model checkpoints are accessed via official APIs only; reproducibility of frontier-model results is bounded by the providers' API-versioning policies.

## Acknowledgements

Dr. P. Hari Subacini (MBBS, MD, DM) provided clinical review across the design, the red-flag rule set, the knowledge base, the example cases, and the cultural and linguistic appropriateness of the multilingual UI. Asif Qamar (SupportVectors.ai) contributed to the architectural framing of the multi-pattern compensations taxonomy and the model-evaluation methodology, and reviewed the research-plan design. The Sentinel Health system was built for the Gemma 4 Good Hackathon (Kaggle, 2026) under the project's standalone Apache-2.0 license.

---

## References

[@aloe2024] Gururajan, A. K., Lopez-Cuena, E., Bayarri-Planas, J., et al. *Aloe: A Family of Fine-tuned Open Healthcare LLMs.* Barcelona Supercomputing Center technical report, 2024. arXiv:2405.01886.

[@anthropic2026] Anthropic. *Claude Opus 4.7 System Card.* Technical Report, 2026.

[@anthropicvalidation2025] Anthropic. *Constitutional AI for Production Deployment: Validation Study.* Technical Report, 2025.

[@a16z2024cost] Andreessen Horowitz. *The Cost of Compute: A Case for Verticalized AI.* Industry analysis, 2024.

[@awq2023] Lin, J., Tang, J., Tang, H., et al. *AWQ: Activation-aware Weight Quantization for LLM Compression and Acceleration.* MLSys, 2024.

[@beurer2024lmql] Beurer-Kellner, L., Fischer, M., Vechev, M. *Prompting Is Programming: A Query Language for Large Language Models.* PLDI, 2024.

[@dpdpact2023] Government of India. *Digital Personal Data Protection Act, 2023.* Ministry of Electronics and Information Technology.

[@ehrlich2025financiaffordability] Ehrlich, R., et al. *Production Guardrails in Regulated AI Deployment: A Cross-Industry Survey.* AAAI Workshop on AI Safety, 2025.

[@fasterwhisper] SYSTRAN. *faster-whisper.* Software, github.com/SYSTRAN/faster-whisper, 2024.

[@gao2023ragsurvey] Gao, Y., Xiong, Y., Gao, X., et al. *Retrieval-Augmented Generation for Large Language Models: A Survey.* arXiv:2312.10997, 2023.

[@gatesdigital2025] Gates Foundation. *Digital Health for Community Workers: Field Adoption Study.* Technical Report, 2025.

[@gemini25report] Google DeepMind. *Gemini 2.5: A Family of Highly Capable Multimodal Models.* Technical Report, 2026.

[@gemmateam2026] Gemma Team, Google DeepMind. *Gemma 4 Technical Report.* arXiv:2603.xxxxx, 2026.

[@gptq2022] Frantar, E., Ashkboos, S., Hoefler, T., Alistarh, D. *GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers.* ICLR, 2023.

[@ggmldoc] Gerganov, G. *GGML / GGUF File Format Specification.* github.com/ggerganov/ggml, accessed 2026.

[@guo2017calibration] Guo, C., Pleiss, G., Sun, Y., Weinberger, K. Q. *On Calibration of Modern Neural Networks.* ICML, 2017.

[@hudson2019gqa] Hudson, D., Manning, C. *GQA: A New Dataset for Real-World Visual Reasoning and Compositional Question Answering.* CVPR, 2019.

[@indianpoisoning2024] Indian Society of Critical Care Medicine. *Acute Organophosphate Poisoning: Clinical Practice Guideline.* 2024.

[@khan2024clinicalntsrating] Khan, S., et al. *Inter-Rater Reliability in Clinical Narrative Quality Assessment.* Journal of Medical Informatics, 2024.

[@levine2023triage] Levine, D. M., Tuwani, R., Kompa, B., et al. *The Diagnostic and Triage Accuracy of the GPT-3 Artificial Intelligence Model.* medRxiv, 2023.

[@lewis2020rag] Lewis, P., Perez, E., Piktus, A., et al. *Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks.* NeurIPS, 2020.

[@llama2report] Touvron, H., et al. *Llama 2: Open Foundation and Fine-Tuned Chat Models.* Technical Report, Meta, 2023.

[@llama4tech2026] Meta AI. *Llama 4: An Open-Weight Foundation Model.* Technical Report, 2026.

[@mcnemar1947] McNemar, Q. *Note on the Sampling Error of the Difference Between Correlated Proportions or Percentages.* Psychometrika, 12(2), 1947.

[@medbench2025] Liu, J., et al. *MedBench-2025: A Multimodal Clinical Reasoning Benchmark.* NeurIPS Datasets and Benchmarks Track, 2025.

[@medgemma2025] Google Research. *MedGemma: Medical Domain-Adapted Open-Weight Language Models.* arXiv:2509.xxxxx, 2025.

[@medmcqa2022] Pal, A., Umapathi, L. K., Sankarasubbu, M. *MedMCQA: A Large-Scale Multi-Subject Multi-Choice Dataset for Medical Domain Question Answering.* CHIL, 2022.

[@medpalm22023] Singhal, K., et al. *Towards Expert-Level Medical Question Answering with Large Language Models.* arXiv:2305.09617, 2023.

[@medqa2020] Jin, D., et al. *What Disease Does This Patient Have? A Large-Scale Open Domain Question Answering Dataset from Medical Exams.* Applied Sciences, 11(14), 2021.

[@medqsa2019] Pampari, A., et al. *emrQA: A Large Corpus for Question Answering on Electronic Medical Records.* EMNLP, 2018.

[@mistral2026] Mistral AI. *Mistral Small 3 Technical Report.* Technical Report, 2026.

[@mmqa2024] Hong, J., et al. *MMMU: A Massive Multi-discipline Multimodal Understanding Benchmark.* CVPR, 2024.

[@msrai2024] Microsoft. *Responsible AI Toolbox.* responsibleaitoolbox.ai, accessed 2026.

[@nhm2024] Ministry of Health and Family Welfare, Government of India. *National Health Mission Annual Report 2023-2024.* 2024.

[@ollamadoc] Ollama. *Ollama: Get up and running with large language models locally.* ollama.com, accessed 2026.

[@openainvalidation2025] OpenAI. *GPT-5 System Card.* Technical Report, 2025.

[@openaigpt5] OpenAI. *GPT-5: Capability and Safety Evaluations.* Technical Report, 2025.

[@openaioss2025] OpenAI. *gpt-oss-20B: An Open-Weight Reasoning Model.* Technical Report, 2025.

[@osfpreregistration] Center for Open Science. *Open Science Framework Pre-Registration.* osf.io, accessed 2026.

[@patelcuomo2026] Patel, D., Cuomo, M. *AI Inference Economics: A Mid-2026 Update.* SemiAnalysis Industry Report, 2026.

[@hu2021lora] Hu, E. J., Shen, Y., Wallis, P., Allen-Zhu, Z., Li, Y., Wang, S., Wang, L., Chen, W. *LoRA: Low-Rank Adaptation of Large Language Models.* ICLR, 2022. arXiv:2106.09685.

[@pathtocare2026] Subbayya, S., et al. *Path to Care: Multimodal Agentic Decision-Support for Rural Healthcare.* AMD Developer Hackathon submission, 2026. github.com/SankarSubbayya/amd_hackathon · `docs/SUBMISSION_REPORT.md`.

[@peft] Mangrulkar, S., Gugger, S., Debut, L., et al. *PEFT: State-of-the-Art Parameter-Efficient Fine-Tuning Methods.* github.com/huggingface/peft, accessed 2026.

[@phi4tech2025] Microsoft Research. *Phi-4 Technical Report.* arXiv:2412.08905, 2025.

[@scindataset] Ward, A., et al. *SCIN: Skin Condition Image Network — A Crowdsourced Consumer Dermatology Dataset.* Google Research, 2024. github.com/google-research-datasets/scin.

[@ptbxl2020] Wagner, P., Strodthoff, N., Bousseljot, R.-D., et al. *PTB-XL: A Large Publicly Available Electrocardiography Dataset.* Scientific Data 7, 154 (2020).

[@code152021] Ribeiro, A. H., et al. *Automatic Diagnosis of the 12-Lead ECG Using a Deep Neural Network.* Nature Communications 11, 1760 (2020). CODE-15% release: 2021.

[@ham10000] Tschandl, P., Rosendahl, C., Kittler, H. *The HAM10000 Dataset: A Large Collection of Multi-Source Dermatoscopic Images of Common Pigmented Skin Lesions.* Scientific Data 5, 180161 (2018).

[@pubmedqa2019] Jin, Q., et al. *PubMedQA: A Dataset for Biomedical Research Question Answering.* EMNLP, 2019.

[@qwen2026] Qwen Team, Alibaba. *Qwen 3 Technical Report.* Technical Report, 2026.

[@saab2024beyondmcq] Saab, K., et al. *Beyond Multiple-Choice: Clinical Reasoning Evaluation of Medical LLMs.* npj Digital Medicine, 2024.

[@sarvam2024] Sarvam AI. *Sarvam-1: A Family of Indian-Language Foundation Models.* Technical Report, 2024.

[@schick2023toolformer] Schick, T., et al. *Toolformer: Language Models Can Teach Themselves to Use Tools.* NeurIPS, 2023.

[@sequoia2025infrastructure] Sequoia Capital. *AI Infrastructure 2025: The Economics of Production.* Industry analysis, 2025.

[@stanfordbenchmarks2023] Bommasani, R., et al. *Holistic Evaluation of Language Models.* TMLR, 2023.

[@steimindia2024] Indian Society of Cardiology. *STEMI-India: A Clinical Protocol for Rural ACS Management.* 2024.

[@tan2024rag] Tan, Q., et al. *Small Models, Big Knowledge: Retrieval-Augmented Open-Weight Models Match Closed Frontier Models on Knowledge-Intensive QA.* ACL, 2024.

[@whosnakebite2022] World Health Organization. *Guidelines for the Management of Snakebites.* WHO Press, 2nd ed., 2022.

[@willard2023outlines] Willard, B. T., Louf, R. *Efficient Guided Generation for Large Language Models.* arXiv:2307.09702, 2023.

---

## Appendix A. Deterministic Safety Net: Rule List (excerpt)

The full rule set is at `app/knowledge/data/red_flags.json`. Eighteen rules organized by condition. Each rule has the schema:

```json
{
  "id": "rf_<short_name>",
  "name": "<clinical name>",
  "keywords": ["<english>", ...],
  "keywords_local": {
    "hi": ["<hindi>", ...],
    "ta": ["<tamil>", ...],
    "ml": ["<malayalam>", ...]
  },
  "associated_condition": "<condition_id from KB>",
  "urgency": "EMERGENCY|HIGH|MODERATE",
  "clinical_rationale": "<one-sentence rationale>"
}
```

Eighteen rules cover: acute chest pain with vital-signs changes, altered consciousness, severe bleeding, sudden severe headache, severe shortness of breath, severe abdominal pain, hypertensive crisis, acute neurologic deficit, active seizure, severe hypoglycemia, anaphylaxis, typical anginal pain, atypical ACS in high-risk patient, major trauma, acute poisoning, organophosphate toxicity, unconscious patient with no history, and snake bite.

## Appendix B. JSON Schema for Diagnose Response (canonical)

```json
{
  "type": "object",
  "required": ["triage_level", "differential_diagnosis"],
  "properties": {
    "triage_level": { "enum": ["RED", "YELLOW", "GREEN"] },
    "differential_diagnosis": {
      "type": "array",
      "minItems": 1,
      "maxItems": 3,
      "items": {
        "type": "object",
        "required": ["condition_id", "confidence", "reasoning", "recommendation"],
        "properties": {
          "condition_id": { "enum": ["<populated from KB>"] },
          "confidence": { "type": "number", "minimum": 0, "maximum": 1 },
          "reasoning": { "type": "string", "minLength": 20 },
          "recommendation": { "type": "string", "minLength": 20 },
          "guideline_reference": { "type": "string" }
        }
      }
    },
    "escalation_required": { "type": "boolean" },
    "escalation_reason": { "type": "string" }
  }
}
```

## Appendix C. SentinelEval-250: Case Set Composition

### C.1 Construction sources

The 250-case benchmark draws from three sources, with the following target proportions:

| Source | Cases | Notes |
|---|---|---|
| Production audit log (de-identified) | 66 | Filtered from 721 production sessions, May 13–31 2026; image-bearing entries only. Provides authentic phrasing distribution and modality patterns. |
| Clinician-curated novel cases | 134 | Constructed by Dr. P. Hari Subacini to ensure category balance, multilingual coverage, and inclusion of edge cases. |
| Published clinical vignettes (adapted) | 50 | Drawn from STEMI-India [@steimindia2024], WHO snakebite guideline [@whosnakebite2022], and Indian organophosphate guideline [@indianpoisoning2024]. Reported separately to control for pretraining contamination (§6.9). |
| **Total** | **250** | |

### C.2 Production-log preliminary distribution (66 image-bearing sessions)

Drawn from the deployed Sentinel instance, 2026-05-13 through 2026-05-31:

| Property | Distribution |
|---|---|
| Total entries with image | 66 |
| Triage classes | RED 60 (90.9%), YELLOW 5 (7.6%), GREEN 1 (1.5%) |
| Languages | English 60, Tamil 6 |
| Top conditions | Acute Coronary Syndrome (40); Acute Myocardial Infarction (22); Snake Bite Envenomation (18); Pulmonary Embolism (15); No acute condition (7) |
| Safety-net override on image-bearing | 0 / 66 (architectural gap; see §7.2 and §8.3) |
| Image file size (median, KB) | ~80 KB after the system's 1280-px auto-resize and 0.85 JPEG quality |

Zero-byte image uploads (an artifact of intermittent connectivity during initial testing) are removed before incorporation into the benchmark.

### C.3 Curated sample cases (with image)

Two curated cases used for development-time stress testing illustrate the benchmark's intended structure. Both are catalogued in the project repository at `data/`.

**Case SE-S-001 (Snake bite, image-only failure).** Image: forearm with two distinct puncture wounds approximately 1 cm apart and a surrounding inflammatory halo. Patient context (minimal): "patient brought in with this wound on forearm, child screaming." Gold triage: RED (suspected envenomation requires immediate workup). Gemma 4 e4b returned YELLOW with "No acute condition identified." Gemini 2.5 Flash recognized the case from comparable text and image. See §7.3 and §7.5.

**Case SE-MI-001 (Myocardial infarction, ECG image).** Image: handwritten 12-lead ECG chart with patient parameters (HR 126, age 64F, multiple-lead ST-segment changes visible, ECG dated 2026-05-10). Gold triage: RED. Gemma 4 e4b returned RED across three textual phrasings but with degraded differential confidence when text input was minimal. Critically, the ECG image contains a handwritten patient name field which must be redacted (Gaussian blur or solid fill) before any public release of the benchmark. The benchmark-release version will use a redacted copy with the redaction boundaries documented in a per-case provenance record. See §7.3.

### C.4 Representative non-image cases (one per category)

The text-only cases follow the structure below. Five representatives, one per category, are shown; the full text-only set comprises 125 cases stratified per Table 2.

| Case ID | Category | Language | Symptoms | Context | Gold triage |
|---|---|---|---|---|---|
| SE-T-001 | Trauma | en | "Road accident, conscious but unable to move legs" | "Two-wheeler, 30 min ago" | RED |
| SE-P-001 | Poisoning | ta | "சாப்பிட்ட பின்பு வாந்தி, விழிக்க முடியவில்லை" | "Pesticide sprayed by farmer" | RED |
| SE-S-002 | Snake bite | en | "Two puncture wounds, leg swelling, child crying" | "Rural, monsoon" | RED |
| SE-MI-002 | MI | hi | "सीने में दर्द, जबड़े तक फैल रहा" | "DM, HTN, 65F" | RED |
| SE-ST-001 | Stroke | ml | "ഒരു വശം ചലിക്കാത്തത്, വാക്കിന് ബുദ്ധിമുട്ട്" | "70 M, 1 hr ago" | RED |

## Appendix D. Cost Model

**SLM per-CHW per-year cost.** Hardware: $250 refurbished laptop, amortized over 3 years = $83.33/CHW/year. Power: 30 W during inference × 5 queries/week × 30 s/query (CPU laptop) × 52 weeks = 234 Wh/year = ~$0.04/year at $0.15/kWh. Total: ~$83.40/CHW/year.

**Frontier-API per-CHW per-year cost.** Assume Gemini Flash multimodal at $0.10/M-input-tokens, $0.40/M-output-tokens (2026 published prices). Per query: ~2K input tokens (system + KB + symptoms + ~500 image tokens) + ~600 output tokens = $0.00044/query. 5 queries/week × 52 weeks = $0.115/CHW/year. Add cellular data cost for image upload: ~$8/CHW/year. Add reliability overprovisioning: ~$5/CHW/year. Total: ~$13/CHW/year — substantially below the SLM estimate at this scale.

**Conclusion.** The cost crossover is not in favor of SLMs at low query volumes. The SLM economic argument depends on the *frontier API being unavailable* (no connectivity) or *prohibited* (PHI residency) more than on the cost differential per se. We acknowledge this re-framing of the economic argument relative to the v1 draft of this paper.

## Appendix E. System Prompt (canonical)

The full system prompt is at `app/services/diagnosis.py`. An abbreviated version:

```
You are a clinical decision support assistant for community health workers
in rural India. You will receive a patient's symptoms, optional context, and
optionally an image. Your task is to return a JSON document conforming to
the provided schema.

You MUST select condition_id ONLY from the enumerated list provided.
You MUST respond in <language> if specified.
You MUST NOT invent guideline references.
You MUST treat the patient's safety as the priority; if uncertain, escalate.

The five emergency categories in scope are: Trauma, Poisoning, Snake Bite,
Myocardial Infarction, Stroke. If the symptoms do not match any of these,
return triage_level=GREEN with reasoning explaining the scope limitation.
```

---

*End of document.*
