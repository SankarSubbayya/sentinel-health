# OSF pre-registration form — SentinelEval-250

Submit at <https://osf.io>. Recommended template: **OSF Standard
Pre-Registration** (10-section form). For a methods-heavy study like this,
the "OSF-Standard" template is a better fit than the simpler
"AsPredicted.org-style" template because it accommodates secondary outcomes,
threats to validity, and ethics review fields.

This document maps each OSF form field to the corresponding content already
in `docs/small_vs_frontier.md`. Paste each block into the matching OSF field.

---

## Step-by-step

1. Sign in to OSF (`osf.io`). Create an account if first time.
2. Click **My Projects** → **Create Project**.
   - Title: `SentinelEval-250: A Pre-Registered Evaluation of Small Open-Weight and Frontier Language Models for High-Stakes Clinical Triage in Low-Resource Settings`
   - Storage: leave at OSF Storage (default).
   - Set the project to **private** initially. Make public only after
     registration is finalized.
3. Inside the project, click **Registrations** → **New Registration**.
4. Choose template: **OSF-Standard Pre-Registration** (sometimes labeled
   "OSF Preregistration Template").
5. Paste the content from §"Form fields" below into each section.
6. **Attach the manuscript** (`docs/small_vs_frontier.pdf`) and the harness
   scripts (`scripts/frontier_pilot.py`, `scripts/slm_pilot.py`) as
   supplementary files.
7. Choose **embargo**: 0 days (immediate public registration). The whole
   point is the public timestamp.
8. Submit. OSF assigns a DOI within minutes.

---

## Form fields

### 1. Title

```
SentinelEval-250: A Pre-Registered Evaluation of Small Open-Weight and Frontier Language Models for High-Stakes Clinical Triage in Low-Resource Settings
```

### 2. Description / Summary (≤2000 chars)

```
This pre-registration specifies the protocol for the formal SentinelEval-250 evaluation described in Section 6 of the accompanying preprint (Subbayya, Qamar, Subacini 2026, "Small Open-Weight Language Models versus Frontier Models for High-Stakes Clinical Triage in Low-Resource Settings: A Case Study and Multi-Model Research Plan"). The study will evaluate twelve candidate language models (four frontier proprietary, five general-purpose small open-weight, three medical-domain small open-weight) on a curated 250-case clinical triage benchmark stratified across five emergency categories (Trauma, Poisoning, Snake Bite, Myocardial Infarction, Stroke) plus GREEN distractor cases, and four languages (English, Hindi, Tamil, Malayalam). Each model is evaluated in three pipeline configurations (unaugmented, with deterministic safety net, with full Sentinel Health architecture including two-pass vision-as-sensor), yielding 36 model-configuration cells. Primary endpoint is RED-tier triage sensitivity. The seven pre-registered hypotheses, statistical analysis plan, sample-size justification, threats to validity, and ethics provisions are detailed in §6 of the manuscript. This pre-registration timestamp commits to the protocol prior to running any model against the held-out replication set.
```

### 3. Has data collection begun?

```
Exploratory pilot data has been collected and reported in §7 of the preprint
(a 31-case Sentinel internal evaluation, a 9-case 3-provider frontier pilot,
a 9-case 6-model local-SLM pilot, and aggregate statistics over 721
production audit-log sessions). These are exploratory and underpowered for
inferential claims and are NOT the data covered by this pre-registration.

The data covered by this pre-registration — the 250-case SentinelEval-250
benchmark with full 12-model × 3-configuration evaluation — has NOT yet
been collected. Benchmark construction has not begun beyond the
audit-log-derived subset (66 cases).
```

### 4. Hypotheses

Paste verbatim from `docs/small_vs_frontier.md` §5 (Research Questions and
Hypotheses). The seven hypotheses are:

```
H1 (Substitutability across SLMs):
Across small open-weight models in the 3 B–14 B parameter range, paired with the same deterministic safety net and KB, triage-class sensitivity for RED-tier text-described cases varies by less than 5 percentage points (point estimate; 95% CI).

H2 (Frontier-vs-SLM gap on image-only compound reasoning):
On image-only suspected snake-bite cases (operationalized in §6.3), triage-class sensitivity is at least 30 percentage points higher for frontier models than for un-augmented small open-weight models.

H3 (Prompt-engineering does not close the H2 gap):
The gap in H2 cannot be closed by prompt engineering alone — no prompt template applied to the un-augmented small model achieves within 10 percentage points of frontier-model sensitivity on the image-only snake-bite cases.

H4 (Two-pass vision-as-sensor closes the gap):
Adding a two-pass vision-as-sensor pipeline to the small open-weight model (vision-only Pass 1 → safety net extension → narrative Pass 3) closes at least 80% of the gap in H2.

H5 (Non-inferiority on text-only cases):
The architectural compensation introduces no statistically significant degradation on text-only cases (non-inferiority margin: 2 percentage points sensitivity).

H6 (Multilingual non-inferiority):
Output quality for narrative fields (clinician-rated 1–5 Likert) is non-inferior for the three target Indic languages compared to English, with non-inferiority margin 0.5 Likert points, for at least one small open-weight model in the panel.

H7 (Calibration):
Small open-weight models exhibit higher expected calibration error (ECE) than frontier models on the benchmark, with point-estimate difference at least 5 percentage points.
```

### 5. Study Design

```
Controlled, pre-registered, head-to-head evaluation of twelve candidate language models on a curated 250-case clinical triage benchmark (SentinelEval-250). Each model is evaluated in three pipeline configurations (Unaugmented / with Safety net / Full Sentinel architecture), yielding 36 model-configuration cells. The benchmark is split 200/50 train-tune/dev within the development phase, with a held-out 50-case replication set reserved for final reporting. Models, prompts, JSON schemas, and safety-net rule sets are frozen at pre-registration filing and are not modified after the held-out set has been touched.

The unit of analysis is the per-case triage decision and its associated structured output. The study is prospective in protocol specification and retrospective in case sourcing (clinical cases are reviewed by the clinical advisor before inclusion, drawn from de-identified historical encounters and published clinical vignettes).

Full study-design specification is at §6.1 of the manuscript.
```

### 6. Sampling Plan

```
The case set comprises 250 cases distributed across five emergency categories (Trauma, Poisoning, Snake Bite, Myocardial Infarction, Stroke) plus a GREEN distractor category. Stratification by modality (text-only / text + image / image-only) and language (English, Hindi, Tamil, Malayalam) is specified in Table 2 of §6.3.

Three sources contribute cases:
- 66 from the deployed Sentinel system's production audit log (de-identified)
- 134 clinician-curated novel cases (constructed by Dr. P. Hari Subacini)
- 50 adapted published clinical vignettes (STEMI-India, WHO snakebite guideline, Indian organophosphate guideline)

A held-out replication set of 50 cases (10 per category, drawn from the same distribution) is reserved for final reporting and is not available for any iterative prompt tuning.

Sample size and power analysis are at §6.7. With n=168 RED cases per model-cell, the primary endpoint (RED-tier sensitivity comparison) is powered at 80% to detect a 7-percentage-point difference at Bonferroni-corrected α = 0.0071.
```

### 7. Variables

**Manipulated variables** (independent):

```
- Model identity (12 levels): the four frontier and eight SLM candidates listed in §6.2 Table 1.
- Pipeline configuration (3 levels): Unaugmented (U), with Safety net (S), Full Sentinel architecture (F).
- Case modality (3 levels): text-only / text + image / image-only.
- Case language (4 levels): English, Hindi, Tamil, Malayalam.
- Case clinical category (6 levels): Trauma, Poisoning, Snake Bite, MI, Stroke, GREEN distractor.
```

**Measured variables** (dependent):

```
PRIMARY:
- Triage-class sensitivity for RED-tier cases (binary outcome per case).

SECONDARY (descriptive + inferential):
- RED-class specificity (TNR over GREEN distractor cases)
- Three-class accuracy
- PPV and NPV for RED triage class
- Expected calibration error (ECE) for SLMs (frontier APIs do not always emit calibrated confidence)
- Per-case latency (median, 95th percentile)
- Per-case cost in USD (frontier: posted price × token count; SLM: hardware + energy amortization)
- Clinician-rated narrative quality (Likert 1–5 on correctness, cultural-linguistic appropriateness, escalation-message usability)
- Adversarial robustness on 20-case prompt-injection subset
- JSON Schema conformance rate (fraction of model outputs satisfying schema on first attempt)
```

### 8. Analysis Plan

```
PRIMARY ANALYSIS (H1):
Pairwise difference in RED-tier sensitivity between each pair of SLMs under configuration S. Maximum pairwise difference reported with 95% bootstrap percentile CI (10,000 bootstrap resamples of cases stratified by category). H1 rejected if upper CI bound exceeds 5 percentage points.

PRIMARY ANALYSIS (H2, H3):
Difference in image-only-case sensitivity between best-performing frontier model and best-performing SLM, with 95% bootstrap CI. H2 rejected if lower CI bound exceeds 30 points; H3 rejected if no prompt template achieves within 10 points of frontier-model sensitivity.

PRIMARY ANALYSIS (H4):
Per-model improvement attributable to the two-pass pipeline (F minus U on image-only cases). McNemar's test for paired binary outcomes per model.

PRIMARY ANALYSIS (H5):
Two-one-sided-tests (TOST) procedure with 2-percentage-point margin on text-only-case sensitivity.

MULTIPLE-COMPARISON CORRECTION:
Bonferroni correction across the seven hypotheses. Threshold for any single hypothesis: α / 7 = 0.0071.

PRE-SPECIFIED SUBGROUP ANALYSES:
Per-category sensitivity, per-language sensitivity, per-modality. Reported descriptively without inferential testing.

INTER-RATER RELIABILITY SUB-STUDY:
50-case stratified sample re-rated by independent blinded second clinician. Cohen's κ (triage class) and weighted κ (Likert).

Full analysis plan is at §6.6 of the manuscript.
```

### 9. Other (threats to validity, exclusions, ethics)

```
THREATS TO VALIDITY (full text at §6.9):
- Construct validity: sensitivity is a proxy for missed-emergency rate; downstream outcomes (mortality, transport-to-treatment time) are not measured.
- Internal validity: clinical advisor curated subset is at risk of selection bias; mitigated via published-vignette cases and inter-rater verification sub-study.
- External validity: Tamil Nadu rural CHW deployment; findings may not transfer to other low-resource settings.
- Model knowledge contamination: published vignettes may be in pretraining data; field-observation stratum reported separately.

EXCLUSION RULES:
- Cases requiring information beyond the deployed system's input modalities (e.g., live ultrasound) are excluded from the benchmark.
- API errors (server 5xx, timeout > 10 minutes) cause that specific (model, case) cell to be marked as "missing" rather than imputed.

ETHICS (full text at §6.10):
The protocol will be submitted for institutional ethics-committee review in Tamil Nadu before any patient-derived data is incorporated. Cases derived from real encounters require explicit informed consent or de-identification to DPDP Act / HIPAA Safe Harbor standards. No model is fine-tuned on patient data in this study.
```

### 10. Pre-registration files to attach

```
- docs/small_vs_frontier.pdf (current manuscript v1.2)
- scripts/frontier_pilot.py (frontier-pilot harness)
- scripts/slm_pilot.py (local-SLM-pilot harness)
- data/frontier_pilot/results.jsonl (frontier-pilot raw results, exploratory)
- data/frontier_pilot/slm_results.jsonl (SLM-pilot raw results, exploratory)
- data/ecg_redaction_provenance.json (image-provenance record)
```

---

## After submission

- OSF assigns a DOI (`10.17605/OSF.IO/XXXXX`) within minutes.
- Add the OSF DOI to the manuscript's §6.8 Pre-registration paragraph and
  re-post as v1.3 to arXiv / medRxiv. (The DOI must be added *after*
  registration; before, the line currently reads "The protocol will be
  deposited on OSF [@osfpreregistration] with a public timestamp before any
  model run...")
- The OSF DOI is the load-bearing artifact: it is the proof, when the formal
  study completes 30 weeks from now, that the protocol was specified before
  the data was collected. Without it, any "pre-registered" claim in the
  completed-study paper is weakly defensible.
- After registration is filed, switch the OSF project from private to public.
