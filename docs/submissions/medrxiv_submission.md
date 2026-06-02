# medRxiv submission package — Sentinel small-vs-frontier paper

Submit at <https://www.medrxiv.org/submit-a-manuscript>. medRxiv is a clinical
preprint server operated by Cold Spring Harbor Lab, BMJ, and Yale. Posts
within 48 hours of submission after screening (basic completeness and lack of
clinical-harm content; not peer review).

## Step-by-step

1. **Create / log in** to a medRxiv account using the author's institutional
   email if available.
2. **Start submission** → "Submit a Preprint."
3. Choose **Subject Area**: `Health Informatics` (primary). Secondary: `Health
   Policy`.
4. **Article type**: `New Results` (since the paper has preliminary empirical
   data) or `Methods` (since the principal contribution is the pre-registered
   research plan). Either is acceptable; `New Results` is more discoverable in
   medRxiv's "newest" listings.
5. Upload `docs/small_vs_frontier.pdf` as the main manuscript.
6. **Cover letter**: paste the text from §"Cover letter" below.
7. Fill the metadata fields (title, authors, abstract, keywords, funding,
   conflicts) per the §"Metadata" section.
8. **Reporting checklist**: medRxiv asks which reporting standard applies. For
   our case, **TRIPOD-AI** (Transparent Reporting of a multivariable
   prediction model for Individual Prognosis Or Diagnosis — AI extension) is
   the closest fit even though we don't have a developed prediction model yet.
   The protocol section can reference the TRIPOD-AI checklist as the planned
   reporting standard for the formal study.
9. Submit.

---

## Cover letter (paste verbatim, edit names/dates as needed)

```
To the Editors, medRxiv

We are submitting our preprint, "Small Open-Weight Language Models versus
Frontier Models for High-Stakes Clinical Triage in Low-Resource Settings: A
Case Study and Multi-Model Research Plan," for posting on medRxiv under the
Health Informatics subject area.

This work is structured as a case study plus a pre-registered research plan,
not as a completed empirical study. It is grounded in a deployed clinical
decision support tool, Sentinel Health, currently in use with a clinical
advisor in Tamil Nadu, India. The principal contributions are:

1. A characterization of where small open-weight language models (specifically
Gemma 4, MedGemma, and the broader open-weight panel) succeed and fail
in high-stakes clinical triage relative to frontier proprietary models
(Gemini 2.5, Claude Opus 4.7, GPT-5), with attention to deployment surface
constraints (offline operation, PHI residency, recurring cost).

2. A pre-registered research plan for a 12-model × 250-case formal
evaluation (SentinelEval-250) with seven hypotheses, statistical
methodology, sample-size power analysis, and ethical-review provisions.

3. An architectural taxonomy of compensations — deterministic safety net,
KB-grounded JSON-Schema output, two-pass vision-as-sensor, selective
frontier escalation — that we hypothesize allow open-weight models to
carry production clinical traffic in deployment surfaces where frontier
APIs are not viable.

All exploratory pilot numbers in §7 are clearly labeled as such and are
underpowered for inferential claims; the formal study is the proposed
work. We have addressed two prior internal review cycles (Codex on
structural/factual issues; an independent reviewer on methodological
concerns including the over-reliance-on-safety-net critique, the unproven
status of the vision-as-sensor architecture, and the cloud-STT versus
offline-claim tension) and the revision history is documented in the
front matter.

The case study has been reviewed informally by a practicing clinician (Dr.
P. Hari Subacini, MBBS MD DM, Tamil Nadu, India). The formal SentinelEval-250
study will undergo institutional ethics committee review before any
patient-derived data is incorporated; that review has not yet been initiated
and is part of the proposed timeline (§6.10–6.11).

Code, prompts, JSON schemas, safety-net rule sets, pilot results, and the
SentinelEval-250 case construction will be openly available under
Apache-2.0 at https://github.com/SankarSubbayya/sentinel-health.

We have no conflicts of interest to disclose. No external funding supported
this work; it was conducted as an unfunded research project alongside the
Gemma 4 Good Hackathon submission (Kaggle, 2026).

Thank you for your consideration.

Sincerely,
Sankar Subbayya (corresponding author)
sankarsubbayya@accurateai.org
On behalf of the listed authors and the clinical advisor.
```

---

## Metadata fields

### Title

```
Small Open-Weight Language Models versus Frontier Models for High-Stakes Clinical Triage in Low-Resource Settings: A Case Study and Multi-Model Research Plan
```

### Short title (running head, ≤ 60 chars)

```
SLMs vs frontier models for offline clinical triage
```

### Authors (medRxiv asks for ORCID where possible)

| Order | Name | Affiliation | ORCID | Corresponding |
|---|---|---|---|---|
| 1 | Sankar Subbayya | Sentinel Health Project, San Francisco Bay Area | (add if you have one) | ✓ |
| 2 | Asif Qamar | SupportVectors.ai | (add if available) |  |
| 3 | P. Hari Subacini | Independent Clinical Reviewer, Tamil Nadu, India | (add if available) | clinical advisor |

(Adjust author list based on Asif's response. medRxiv allows author-order
edits before posting; once posted, additions/removals require a withdrawal
and re-submission of a new version.)

### Abstract

Paste the Background/Methods/Preliminary Results/Conclusions block from
`docs/small_vs_frontier.md` (lines 17–25). medRxiv accepts ~3000 char
abstracts which our structured-abstract version fits within.

### Keywords (medRxiv asks for 3–6)

```
small language models; clinical decision support; offline AI; community health workers; multimodal reasoning; low-resource healthcare; pre-registered research plan
```

### Subject category

Primary: `Health Informatics`
Secondary: `Health Policy`

### Funding statement

```
No external funding supported this work.
```

### Conflict of interest

```
The authors declare no competing interests.
```

### Author contributions (CRediT taxonomy)

```
Sankar Subbayya: conceptualization, methodology, software, formal analysis, writing — original draft, writing — review and editing, project administration.

Asif Qamar: methodology, validation, writing — review and editing.

P. Hari Subacini: clinical curation and review of safety-net rules, knowledge base, evaluation cases, multilingual narrative quality; writing — review of clinical sections.
```

### Ethical review statement

```
The case study and exploratory pilots involved no patient-identifiable data
beyond clinically-redacted teaching cases reviewed and consented for inclusion
by the clinical advisor. The proposed formal SentinelEval-250 study will
undergo institutional ethics-committee review prior to incorporation of any
patient-derived data; that review has not yet been initiated.
```

### Data availability statement

```
All code, prompts, JSON schemas, safety-net rule sets, the redacted Case A
and Case B images, the audit-log corpus aggregates, and the pilot results
are available at https://github.com/SankarSubbayya/sentinel-health under
Apache License 2.0. The SentinelEval-250 case set construction is in
progress; the full benchmark will be released under CC-BY 4.0 upon
completion of the planned study, subject to the consent and de-identification
constraints described in §6.10 of the manuscript.
```

### Code availability statement

```
The Sentinel Health application source code is at
https://github.com/SankarSubbayya/sentinel-health under Apache-2.0. The
frontier-pilot harness (scripts/frontier_pilot.py), local-SLM-pilot harness
(scripts/slm_pilot.py), and raw results (data/frontier_pilot/*.jsonl) are in
the same repository.
```

---

## After submission

- medRxiv typically assigns a DOI within 48 hours of posting.
- The medRxiv DOI is the more clinically-credible reference; the arXiv ID
  is the more ML-community-discoverable reference. List both in any future
  citation.
- medRxiv allows revisions ("new versions") with a separate DOI suffix
  (`/v2`, `/v3`). When the SentinelEval-250 formal study completes, post a
  v2 here rather than starting a new submission.
- Do not press-release until both arXiv and medRxiv are posted.
