# Small Open-Weight versus Frontier Models for ECG and Echocardiography Triage in Low-Resource Cardiology: A Case Corpus and a Focused Research Plan

**Subbayya Sankaranarayanan¹**
**P. Hari Subacini, MBBS MD DM²**
**Asif Qamar³**

¹ Sentinel Health Project · sankarsubbayya@accurateai.org
² Consultant Cardiologist, Tamil Nadu, India
³ SupportVectors.ai · asif@supportvectors.ai

*Preprint · v0.1 · 2026-08-07 · Corresponding author: ¹*

*Framing note. This is a focused companion to our general clinical-triage study, "Small Open-Weight Language Models versus Frontier Models for High-Stakes Clinical Triage in Low-Resource Settings: Two Case Studies and a Multi-Model Research Plan" (Sankaranarayanan, Subacini, Qamar, 2026; Zenodo DOI [10.5281/zenodo.21047535](https://doi.org/10.5281/zenodo.21047535)). The general paper argues that clinical AI should be evaluated at the pipeline level, not the model level, and proposes a taxonomy of architectural compensations (deterministic safety net, KB-grounded structured output, two-pass vision-as-sensor, selective frontier escalation, domain LoRA adaptation). This paper applies that framework narrowly and deeply to one organ system — the heart — where the diagnostic artifacts (12-lead ECG, echocardiography report) are concrete, structured, and clinician-labelable. As with the general paper, this is a case corpus plus a pre-registered research plan, not a completed empirical study. All numbers reported are exploratory; the formal evaluation is the proposed work.*

---

## Abstract

**Background.** Cardiac emergencies — acute coronary syndromes, decompensated cardiomyopathy, life-threatening conduction disease — are among the highest-mortality conditions a community health worker (CHW) or primary health centre (PHC) will encounter, and they are exactly the conditions where the diagnostic artifact (the 12-lead ECG) is captured at the point of care but interpreted, if at all, hours later by a cardiologist who is tens of kilometres away. Small open-weight language models with vision (SLMs) can in principle read an ECG photograph offline on a clinic laptop. Whether they should be trusted to, and under what surrounding system, is unstudied at the pipeline level.

**Objective.** To characterize where SLMs are good enough for cardiac triage from ECG and echocardiography artifacts, where they are not, and which system-level safeguards narrow the gap with frontier models — using a real, clinician-labelled paired ECG + echo corpus and a focused research plan.

**Methods.** We assemble a small corpus of real cardiac records from a rural Tamil Nadu cardiology practice: 12-lead ECGs and echocardiography reports, including two patients with paired ECG + echo (one normal, one with reduced ejection fraction), read and signed by a consultant cardiologist (the second author). We apply the architectural framework of the companion general paper to the cardiac domain, and we pre-register an evaluation of small open-weight and frontier models on a cardiac-triage benchmark spanning normal tracings, ischemia, conduction block, reduced-EF cardiomyopathy, and structural findings.

**Preliminary observations (exploratory).** On the general-paper pilots, Gemma 4 e4b read ST-segment elevation on a 12-lead ECG photograph and articulated it in free text, but under minimal textual prompting its schema-bound differential picker conservatively returned "no acute condition identified" — a structured-output failure distinct from a perception failure. Frontier models did not exhibit this failure on the same image. The present corpus extends that observation to a wider cardiac spread (normal, ischemia, complete right bundle branch block, EF 39% cardiomyopathy, atrial septal defect) and to a second modality (echo reports), and motivates the formal evaluation.

**Conclusions.** ECG and echo triage is a domain where the small-model-plus-scaffolding thesis is unusually testable, because the ground truth is a structured cardiologist reading rather than a subjective narrative. The proposed study measures the SLM-versus-frontier gap across cardiac artifact types and tests whether the same architectural compensations — safety net, structured output, vision-as-sensor, and an inter-field consistency check specific to ECG reasoning — make an offline SLM pipeline safe enough for first-contact cardiac triage.

**Keywords:** ECG interpretation · Echocardiography · Cardiac triage · Small open-weight language models · Frontier language models · Edge AI · Clinical decision support · Low-resource cardiology · Multimodal reasoning · Reduced ejection fraction

---

## 1. Introduction

The 12-lead ECG is the most information-dense artifact a first-contact health worker in a low-resource setting can capture. It is cheap to acquire (a portable machine and a roll of thermal paper), it is diagnostic for the conditions that kill fastest (ST-elevation myocardial infarction, high-grade block, dangerous arrhythmia), and — critically for an AI argument — its correct interpretation is a *structured* task with a cardiologist-agreed ground truth, unlike the open-ended narrative reasoning that dominates general triage.

The problem is not acquisition; it is interpretation latency. In the rural Tamil Nadu catchment that motivates this work, an ECG is often photographed on a phone at the PHC and forwarded — over an intermittent connection — to a consultant cardiologist for a reading that may arrive hours later. During those hours a STEMI patient is losing myocardium. An offline system that could give the CHW an immediate, safe triage class from the ECG photograph — "this needs the cath lab now" versus "this can wait for the routine reading" — would change outcomes even if it never replaced the cardiologist's definitive read.

The companion general paper [@sankaranarayanan2026general] makes the case that clinical AI should be evaluated as a pipeline, not as a bare model, and that a small open-weight model wrapped in deterministic scaffolding can carry production clinical traffic where a frontier API cannot be deployed at all (no connectivity, no per-call billing, no consent posture for cloud PHI transfer). That paper spans five emergency categories and two organ systems (general triage plus dermatology). Its single most instructive result, however, is cardiac: on a 12-lead ECG photograph, Gemma 4 e4b's vision module *recognized* ST-segment elevation and wrote it into its reasoning field, yet its schema-bound differential picker, under minimal text, still returned "no acute condition identified." That is not a perception failure — the model saw the finding — it is a structured-output failure, and it is exactly the kind of failure a narrow, deep, domain-specific evaluation can isolate and fix.

This paper narrows to the heart. Section 2 reviews ECG and echo AI. Section 3 describes the clinical problem at the CHW/PHC level. Section 4 presents the real ECG + echo case corpus. Section 5 applies the architectural framework to cardiac artifacts, including an ECG-specific inter-field consistency check. Section 6 pre-registers a cardiac-triage evaluation. Section 7 reports preliminary observations. Sections 8–10 discuss, bound, and conclude.

---

## 2. Related Work

### 2.1 Deep learning on ECGs

ECG classification is one of the most mature medical-AI subfields. Public corpora — PTB-XL [@ptbxl2020] (21,837 12-lead records with cardiologist labels), CODE-15% [@code152021] (a large Brazilian pre-hospital screening set), and the older MIT-BIH arrhythmia database — have driven CNN and transformer models that match cardiologist accuracy on rhythm and STEMI detection from the *digital signal*. The gap this paper addresses is different: the CHW does not have the digital signal, only a *photograph* of the printed tracing, and the task is not fine-grained classification but safe triage.

### 2.2 LLM and VLM interpretation of ECG images

Vision-language models reading ECG *images* (rather than signals) is a newer and less-settled area. Frontier multimodal models can describe an ECG photograph in clinical terms; the reliability of that description, and its translation into a safe triage decision, is not well characterized for small open-weight models. This paper contributes exploratory evidence and a plan to measure it.

### 2.3 Echocardiography AI

Automated echo interpretation has focused on video (view classification, EF estimation from cine loops) rather than on the *report*. In a low-resource setting the CHW is more likely to hold a printed echo report — a structured document with measurements (EF, chamber dimensions) and an impression — than a cine loop. Reading and triaging from the report is a document-understanding task well suited to an SLM with vision, and is part of the corpus and plan here.

### 2.4 Architectural framework

We inherit the five-pattern architectural taxonomy of the companion paper [@sankaranarayanan2026general] — deterministic safety net, KB-grounded JSON-Schema output, two-pass vision-as-sensor, selective frontier escalation, and domain LoRA adaptation — and specialize it to cardiac artifacts in §5. We do not restate the taxonomy's general motivation here; the reader is referred to that paper.

---

## 3. The Clinical Problem

The target user is the same as in the general paper: a community health worker (ASHA cadre) or a PHC nurse who is the first medical contact for a rural population, with a consultant cardiologist reachable only intermittently. The cardiac-specific workflow is:

1. A patient presents with chest pain, breathlessness, palpitations, or collapse.
2. The PHC captures a 12-lead ECG (and, where a machine is present, may have a prior echo report on file).
3. Today: the ECG is photographed and forwarded for a cardiologist reading that arrives after a delay; in the interval the CHW has no decision support.
4. Proposed: an offline SLM pipeline gives an immediate triage class from the ECG photograph — RED (activate transfer / thrombolysis pathway now), YELLOW (urgent but not immediate), GREEN (routine) — with the definitive cardiologist read still to follow.

The triage decision, not the diagnosis, is the product. The cardiologist diagnoses; the system buys time by getting the sickest patients moving before the read arrives. This is the same "decision support, not diagnosis" posture as the general system, applied to the one artifact where the stakes of interpretation latency are highest.

---

## 4. Case Corpus

We assembled a corpus of real cardiac records from the second author's cardiology practice in Tamil Nadu. All records are photographs of printed artifacts (ECG tracings and echo reports) as they would be captured at the point of care. Every echo report in the corpus was read and signed by the second author (Consultant Cardiologist, MD DNB DM Cardiology). The corpus is small and is used here to illustrate the cardiac artifact spread and to seed the formal benchmark of §6; it is not itself the evaluation.

**Privacy.** Every record contains protected health information (patient name, ID, age, date, referring organisation). The raw images are not part of any public artifact of this paper. Redacted, rotation-corrected versions — patient-identifying regions removed, EXIF stripped — will be published only with the second author's explicit sign-off on each redaction and confirmation of informed consent, per the ethics provisions of the companion paper. Figures in the published version of this paper will use those redacted versions; the present draft describes the records textually.

### 4.1 Corpus composition

| Case | Artifact(s) | Age/Sex | Cardiologist finding | Triage relevance |
|---|---|---|---|---|
| **A** | 12-lead ECG | F | Sinus rhythm; incomplete right bundle branch block; moderate T-wave abnormality; consider anterior ischemia; abnormal ECG | Abnormal — YELLOW/RED |
| **B** | 12-lead ECG (GE MAC2000) | — | Clean tracing; machine report "unconfirmed"; no marked abnormality | Likely normal (pending gold-label) |
| **C** | 12-lead ECG **+** echo report | 35 M | ECG within normal limits (sinus rhythm, sinus arrhythmia, rsr' in V1/V2); echo normal, EF 71%, no regional wall-motion abnormality, normal valves | Normal — GREEN (paired ECG + echo) |
| **D** | 12-lead ECG **+** echo report (2 pp) | 60 M | ECG: sinus rhythm, complete right bundle branch block, concordant T waves in anterior leads, rule out IHD (QRS 128 ms); echo: global LV hypokinesia (inferior > anterior), LA/LV mildly dilated, moderate MR, EF 39%, moderate LV systolic dysfunction, grade II diastolic dysfunction | Abnormal — RED (paired ECG + echo; reduced-EF cardiomyopathy / ?ischemic) |
| **E** | Echo report | 24 F | OS-ASD (left-to-right shunt 2.1–2.3 cm), RA/RV/MPA mildly dilated, mild TR, normal LV systolic function EF 72% | Structural finding; not an acute emergency |

### 4.2 What makes this corpus useful

Three properties make even this small corpus valuable for the SLM-versus-frontier question:

First, **it spans the clinically meaningful cardiac axis** — normal (C), ischemia (A), conduction block (D-ECG), reduced-EF cardiomyopathy (D-echo), and structural disease (E) — rather than clustering on one finding.

Second, **it contains two paired ECG + echo studies of the same patient** (Case C normal, Case D abnormal). A paired normal-vs-reduced-EF contrast on the same modality pair is a clean RED/GREEN cardiac axis and is exactly the kind of grounded case that a benchmark's MI/cardiac category needs.

Third, **the ground truth is a signed cardiologist reading**, not a crowd label or a synthetic vignette. The gold labels carry clinical authority by construction, because the labelling cardiologist is a co-author.

### 4.3 Artifact-quality notes

The ECGs are photographed in landscape and require rotation for upright reading — a preprocessing step, not a model capability. The echo reports are clean document photographs. Image quality is representative of real point-of-care capture (phone camera, ambient lighting, occasional finger or clipboard in frame), which is the correct distribution to evaluate against and a harder one than clean scanned corpora.

---

## 5. Architecture for Cardiac Artifacts

We specialize the general framework [@sankaranarayanan2026general, §8] to ECG and echo artifacts. The five patterns carry over; two deserve cardiac-specific treatment.

### 5.1 Two-pass vision-as-sensor for ECGs

Applied to an ECG photograph, Pass 1 is a narrow structured-output query — "Report which of the following ECG findings are present: ST elevation, ST depression, pathological Q waves, T-wave inversion, wide QRS (>120 ms), tachycardia, bradycardia, irregular rhythm, …" — and Pass 2 is the triage-reasoning call with those findings appended and matched against the deterministic rule layer. The intuition from the companion paper holds: asking a small VLM "is there ST elevation in the anterior leads, yes or no" is a question it can answer; asking it "is this a STEMI requiring cath-lab activation given this photograph and this vague history" is the compound question it fails.

### 5.2 ECG inter-field consistency check

The companion paper documented a structured-output failure specific to ECGs (§7.3, Case B there): Gemma 4 e4b wrote "ST elevation in multiple leads, highly concerning for acute myocardial injury" into its reasoning field, then selected "no acute condition identified" as its differential. The cardiac-specific compensation is an inter-field consistency check: if the reasoning field contains an ischemia/injury phrase (ST elevation, ST depression, myocardial injury, ischemia), the differential picker is not permitted to return a benign class. This is a deterministic post-processor rule, cheap to implement, and it targets a failure mode we have already observed rather than a hypothetical one. It is, in effect, a deterministic safety net operating on the model's own narrative rather than on the input text.

### 5.3 Echo-report understanding

Echo reports are structured documents; the relevant SLM task is document understanding (extract EF, chamber dimensions, impression) plus a triage mapping (EF < 40% and symptomatic → urgent cardiology follow-up; ASD with shunt → structural referral, not emergency). KB-grounded structured output applies directly: the model extracts fields, the deterministic layer maps them to a triage tier from a cardiologist-curated rule set.

---

## 6. Research Plan

We pre-register a cardiac-triage evaluation, *SentinelCardio*, following the design discipline of the general paper's SentinelEval-250 [@sankaranarayanan2026general, §6].

### 6.1 Artifact classes and target benchmark

The benchmark will contain 12-lead ECG photographs and echo-report photographs stratified across cardiac triage-relevant categories: normal, ischemia/STEMI, conduction block, arrhythmia, reduced-EF cardiomyopathy, and structural disease, plus a GREEN distractor set (normal ECGs and normal echos). Target size and per-category counts will be fixed at pre-registration; the real corpus of §4 seeds the curated component, augmented by public-corpus ECGs (PTB-XL [@ptbxl2020], CODE-15% [@code152021]) for the signal-derived categories where large labelled sets exist.

### 6.2 Models under test

The same twelve-model panel as the general paper — four frontier (Gemini 2.5 Pro/Flash, Claude Opus 4.7, GPT-5) and eight small open-weight (Gemma 4 e4b/27B, Llama 4 8B, Mistral Small 3, Qwen 3 14B, MedGemma 4B/27B, Aloe-Beta-8B) — restricted to vision-capable models for the image-bearing ECG and echo cases.

### 6.3 Primary endpoint

RED-tier sensitivity for time-critical cardiac findings (STEMI, high-grade block with instability, symptomatic reduced-EF decompensation), analyzed as RED-vs-not-RED. The cardinal safety metric, as in the general paper, is the false-negative RED→GREEN rate: a missed STEMI triaged as routine is the failure the system exists to prevent.

### 6.4 Secondary endpoints

ECG-finding extraction accuracy (Pass-1 vision-as-sensor F1 against cardiologist-marked findings), echo-field extraction accuracy (EF, chamber dimensions), three-tier triage accuracy, calibration, latency, and the rate at which the inter-field consistency check (§5.2) fires and corrects an otherwise-benign differential.

### 6.5 Configurations, statistics, ethics, timeline

Configurations (unaugmented / safety-net / full pipeline), multiple-comparison correction, bootstrap confidence intervals, inter-rater reliability against a second cardiologist, and the ethics/consent provisions follow the general paper's methodology [@sankaranarayanan2026general, §6.4–6.11] specialized to cardiac artifacts. Patient-derived cardiac records enter the benchmark only after institutional ethics review and per-record consent confirmation.

---

## 7. Preliminary Observations

No formal evaluation has been run for this cardiac-focused study. Two exploratory observations, both inherited or extended from the companion paper, motivate it.

**(1) The ECG structured-output failure is real and cardiac-specific.** On a real 12-lead ECG photograph, Gemma 4 e4b under minimal text returned RED triage but a "no acute condition identified" differential while its reasoning field explicitly described ST elevation "highly concerning for acute myocardial injury" [@sankaranarayanan2026general, §7.3]. This is the motivating failure for the inter-field consistency check of §5.2. It is exactly the kind of defect that a narrow cardiac evaluation can quantify (how often does the reasoning field contradict the differential?) and fix (does the consistency check recover it?).

**(2) The corpus spans the axis the benchmark needs.** The five cardiac cases of §4 already provide a normal ECG+echo pair (C), a reduced-EF ECG+echo pair (D), an ischemia ECG (A), a clean ECG (B), and a structural echo (E). Even before augmentation, this is enough to exercise the RED/GREEN axis (Case D vs Case C) on paired same-patient artifacts — the cleanest possible contrast, because model performance can be compared on two patients who differ in cardiac status but were captured on the same machines under the same conditions.

Both observations are exploratory; the formal SentinelCardio evaluation of §6 is the work that would substantiate them.

---

## 8. Discussion

Cardiac triage is an unusually favourable domain for testing the small-model-plus-scaffolding thesis, for one reason: the ground truth is objective and structured. A snake-bite triage depends on context a model may or may not weight correctly; a STEMI is on the tracing or it is not, and a cardiologist will agree with a cardiologist. That objectivity makes the SLM-versus-frontier gap measurable with less label noise than general triage, and it makes the inter-field consistency check (§5.2) a precise, testable intervention rather than a soft heuristic.

The echo-report modality also extends the general paper's reach. The general system reads ECGs, wounds, and scenes; it does not read structured clinical documents. Echo-report understanding is a document-plus-triage task that the same KB-grounded structured-output pattern handles, and it is common in exactly the reduced-EF cardiomyopathy population (Case D) where an offline triage aid has clear value.

The economic and deployment arguments carry over unchanged from the companion paper: an offline ECG-triage aid on a clinic laptop is deployable where a frontier-API cardiology service is not, and its value is highest precisely in the interpretation-latency window that a low-resource cardiac workflow cannot otherwise close.

---

## 9. Limitations

1. **The corpus is small and single-practice.** Five cases from one Tamil Nadu cardiology practice illustrate the artifact spread; they do not power any inferential claim. The formal benchmark of §6 is the intended evidence.
2. **No formal evaluation has been run** for this cardiac-focused study; the preliminary observations are inherited from the companion paper or descriptive of the corpus.
3. **Photograph-of-tracing is a lossy modality.** The corpus and plan deliberately use point-of-care photographs, not the digital ECG signal; results will not transfer to signal-based ECG models and vice versa.
4. **Echo triage from the report, not the study.** The system reads the cardiologist's printed report, which already contains an EF and impression; it is a document-understanding-plus-triage task, not primary echo interpretation.
5. **Redaction and consent are prerequisites.** No patient-derived cardiac record appears in any public artifact of this paper until redacted and signed off by the second author, per the companion paper's ethics provisions.

---

## 10. Conclusion

The heart is where interpretation latency costs the most and where the diagnostic artifact is most structured — which makes it the sharpest possible test of whether a small offline model, wrapped in the right deterministic scaffolding, can safely triage. We have described a real, cardiologist-labelled ECG + echo corpus that spans the clinically meaningful cardiac axis, specialized the companion paper's architectural framework to cardiac artifacts (including an ECG inter-field consistency check that targets a failure we have already observed), and pre-registered a focused evaluation. The claim is not that a small model can read an ECG as well as a cardiologist; it is that a small-model pipeline may be able to get the sickest cardiac patients moving before the cardiologist's read arrives — and that this is measurable, in this domain, with unusually clean ground truth.

---

## Ethics Statement

The cardiac records described in this paper are real clinical artifacts from the second author's cardiology practice and contain protected health information. No raw record is included in any public artifact. Redacted, rotation-corrected versions will be published only with the second author's per-record sign-off and confirmation of informed consent for research and educational use, and after institutional ethics-committee review, consistent with the ethics provisions of the companion paper. The second author is the cardiologist of record for the echo reports and the clinical authority for all gold-label assignments.

## Data and Code Availability

This paper is a companion to [@sankaranarayanan2026general] (Zenodo DOI [10.5281/zenodo.21047535](https://doi.org/10.5281/zenodo.21047535)). The Sentinel Health architecture is at `github.com/SankarSubbayya/sentinel-health` under Apache-2.0. The SentinelCardio benchmark of §6 is under construction; redacted corpus figures and the benchmark will be released, subject to the consent and de-identification constraints above, upon completion of the planned study. Public ECG corpora referenced (PTB-XL, CODE-15%) are available from their respective providers under their published licenses.

## Acknowledgements

Dr. P. Hari Subacini (MBBS, MD, DM Cardiology), second author and Consultant Cardiologist, provided the cardiac case corpus, read and signed the echocardiography reports, and is the clinical authority for all triage gold-labels. Asif Qamar (SupportVectors.ai), third author, contributed to the architectural framework this paper specializes.

---

## References

[@sankaranarayanan2026general] Sankaranarayanan, S., Subacini, P. H., Qamar, A. *Small Open-Weight Language Models versus Frontier Models for High-Stakes Clinical Triage in Low-Resource Settings: Two Case Studies and a Multi-Model Research Plan.* Preprint, Zenodo, 2026. DOI: 10.5281/zenodo.21047535.

[@ptbxl2020] Wagner, P., Strodthoff, N., Bousseljot, R.-D., et al. *PTB-XL: A Large Publicly Available Electrocardiography Dataset.* Scientific Data 7, 154 (2020).

[@code152021] Ribeiro, A. H., et al. *Automatic Diagnosis of the 12-Lead ECG Using a Deep Neural Network.* Nature Communications 11, 1760 (2020). CODE-15% release: 2021.
