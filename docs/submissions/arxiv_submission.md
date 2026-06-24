# arXiv submission package — Sentinel small-vs-frontier paper

Submit at <https://arxiv.org/submit>. arXiv requires endorsement for first-time
submissions to most CS categories — if Sankar's account has no prior
submissions in `cs.CL` or `cs.CY`, request endorsement from a colleague who
does. Alternative: `stat.ML` does not always require endorsement and is a
reasonable cross-list for this paper.

## Step-by-step

1. **Sign in** to arxiv.org with the author's institutional email if possible
   (gets the affiliation-tag right). If not, the personal email is fine.
2. **Start submission** → "Start New Submission."
3. **Upload format**: choose **PDF** (not LaTeX source). Upload
   `docs/small_vs_frontier.pdf`.
4. Paste the metadata below into the corresponding fields.
5. **Add license**: choose **arXiv non-exclusive license to distribute** (the
   default). This is compatible with the project's Apache-2.0 code license.
6. Submit. Expect ~1–3 business days before the paper appears in the daily
   listing (arXiv moderates).

---

## Metadata to paste

### Title

```
Small Open-Weight Language Models versus Frontier Models for High-Stakes Clinical Triage in Low-Resource Settings: A Case Study and Multi-Model Research Plan
```

### Authors (one per line, "First Last" format)

```
Sankar Subbayya
P. Hari Subacini
Asif Qamar
```

Affiliations field (separate field on arXiv):

```
1. Sentinel Health Project
2. Independent Clinical Reviewer, Tamil Nadu, India
3. SupportVectors.ai
```

### Abstract (4000-char cap on arXiv; current draft is well within)

Paste the full Abstract block from `docs/small_vs_frontier.md` lines 17–25
(Background / Methods / Preliminary Results / Conclusions). Or copy-paste this
single-paragraph version that arXiv likes for the listing page:

```
Small open-weight language models (SLMs) with 1–10 billion parameters have improved sufficiently by mid-2026 that they are increasingly deployed in production for clinical decision support, in part because they can run offline on commodity hardware and in part because they avoid the data-residency and recurring-cost penalties of frontier-model APIs. The clinical-capability trade-off, however, is poorly characterized at the system level: public benchmarks evaluate models in isolation, not the pipelines in which they are actually deployed. We characterize this trade-off using a deployed clinical case study (Sentinel Health, an offline triage tool for community health workers in rural Tamil Nadu) and a planned multi-model evaluation. We report exploratory pilot observations: on 9 cases against three frontier providers (Claude Opus 4.7, GPT-5, Gemini 2.5 Flash) all three returned RED-tier triage at 9/9 sensitivity, including on an image-only suspected snake-bite case where Gemma 4 e4b returned YELLOW with "no acute condition identified." On a 9-case 6-model local-Ollama SLM pilot, sensitivity ranged from 0/5 to 9/9, and the same atypical-MI text case was misclassified to YELLOW by 3 of 6 SLMs as "dental infection" or "gastroenteritis." We pre-register a 12-model × 250-case evaluation (SentinelEval-250) with seven hypotheses, a defined statistical methodology, sample-size power analysis, and a 30-week timeline. We propose an architectural taxonomy of compensations — deterministic safety nets, KB-grounded JSON-Schema output, two-pass vision-as-sensor pipelines, and selective frontier escalation — that we hypothesize allow SLMs to carry production clinical traffic. The framing claim is that the right unit of evaluation is the pipeline, not the model.
```

### Categories

Primary:

```
cs.CL  (Computation and Language)
```

Secondary (cross-list):

```
cs.CY  (Computers and Society)
cs.AI  (Artificial Intelligence)
```

If endorsement for `cs.CL` is a blocker on first submission, fall back to:

```
Primary:  stat.ML  (Machine Learning)
Cross:    cs.CY, cs.AI
```

### Comments field

```
v1.2 · 39 pages · 5 appendices · 45 references. Case study + pre-registered research plan; preliminary numbers are exploratory pilots, not powered for inferential claims. Revision history reflecting two rounds of independent review (structural/factual + methodological) is included in the front matter. Code, models, eval harness, and SentinelEval-250 case-set construction at https://github.com/SankarSubbayya/sentinel-health · Apache-2.0.
```

### Journal-ref field

Leave blank (this is a preprint).

### DOI field

Leave blank.

### MSC / ACM-class

Leave blank (optional, arXiv does not require either for CS papers).

---

## After submission

- Save the arXiv ID (e.g., `arXiv:2606.NNNNN`) once it's assigned.
- Update `docs/small_vs_frontier.md` reference section to include the arXiv
  ID self-reference once available.
- Tweet / LinkedIn announcement is optional — wait until the medRxiv version
  is also up so both go out together.
- Asif's confirmation note (see `discord_message_asif.md`) should land
  *before* the arXiv submission so his co-author status is settled before
  the timestamp is permanent. arXiv allows replacements but not removal of
  authors on a v1 once it's posted.
