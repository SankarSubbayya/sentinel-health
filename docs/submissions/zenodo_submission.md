# Zenodo submission package — Sentinel small-vs-frontier paper

Submit at <https://zenodo.org/uploads/new>. Zenodo is the open-access archive
operated by CERN with EU funding; no endorsement is required, DOI is assigned
within minutes of publishing, and the record is permanent. Posting time:
<5 minutes from "Publish" click. The Zenodo DOI is a real, indexed,
Google-Scholar-discoverable citation handle.

## Why Zenodo alongside (or instead of) arXiv

- **No endorsement requirement.** Anyone can publish.
- **Instant DOI** (`10.5281/zenodo.NNNNNNNN`).
- **GitHub integration.** Zenodo can mint a DOI per release tag in
  `SankarSubbayya/sentinel-health`, automatically attaching the repo's
  release artifacts to the record. This is the most reproducibility-friendly
  setup for a paper whose code, eval set, and prompts are all in the repo.
- **CC-BY-4.0 license** is the recommended default and is what most clinical
  preprints use.
- **Versioning support.** Future revisions (v1.6, v2.0) can be uploaded as
  new versions of the same Zenodo record; each version gets its own DOI
  and the parent "concept DOI" resolves to the latest. This is how to
  handle the post-completed-study v2 release.

## Step-by-step

1. **Sign in** to zenodo.org using ORCID (preferred — establishes author
   identity unambiguously) or GitHub OAuth. If signing up fresh, ORCID
   linkage takes ~2 minutes.
2. **New Upload** → drag-and-drop `docs/small_vs_frontier.pdf` into the
   upload zone. Wait for the file to finish processing (~10 seconds for
   1.34 MB).
3. **Resource type**: select `Publication` → `Preprint`.
4. **Title**: paste the title (see §"Metadata to paste" below).
5. **Creators**: add each author with affiliation and (if available) ORCID.
6. **Description**: paste the abstract.
7. **Additional notes**: paste the comments-field text.
8. **Communities**: optionally add the paper to `Open Science Framework`
   or `medRxiv` communities for cross-discoverability. Optional.
9. **License**: select `Creative Commons Attribution 4.0 International (CC-BY-4.0)`.
10. **Keywords**: paste from the keyword list below.
11. **Related/alternate identifiers** (optional but useful):
    - If you have a medRxiv DOI already, add it as `is supplemented by`.
    - If you have an OSF pre-registration DOI, add it as `is supplemented by`.
    - GitHub repo URL: add as `is supplement to` with type `URL`.
12. Click **Publish**. Zenodo assigns the DOI immediately. Save it.

Total time once logged in: ~10–15 minutes.

---

## Metadata to paste

### Title

```
Small Open-Weight Language Models versus Frontier Models for High-Stakes Clinical Triage in Low-Resource Settings: Two Case Studies and a Multi-Model Research Plan
```

### Creators (with affiliations and ORCIDs)

| Order | Name | Affiliation | ORCID |
|---|---|---|---|
| 1 | Sankar Subbayya | Sentinel Health Project | (add if you have one) |
| 2 | P. Hari Subacini, MBBS MD DM | Independent Clinical Reviewer, Tamil Nadu, India | (add if available) |
| 3 | Asif Qamar | SupportVectors.ai | (add if available) |

Each Creator on Zenodo requires `Family name, Given name(s)` format:
```
Subbayya, Sankar
Subacini, P. Hari
Qamar, Asif
```

### Description (paste verbatim — Zenodo accepts ~5000 chars)

```
By mid-2026, small open-weight language models (SLMs) with 1–10 billion parameters are good enough to deploy in production for clinical decision support. Builders pick them for two reasons: they run offline on commodity hardware, and they sidestep the data-residency and per-call cost penalties of frontier-model APIs. The clinical-capability trade-off, however, is poorly characterized at the system level. Public benchmarks evaluate models in isolation, not the pipelines in which they actually carry production traffic.

We characterize this trade-off using two deployed case studies built by the first author in rural Tamil Nadu — Sentinel Health (Gemma 4 e4b on a clinic laptop, offline emergency triage) and Path to Care (Gemma 4 31B-it on a single AMD MI300X, LoRA-tuned dermatology classification) — and a planned multi-model evaluation.

Exploratory pilots: three frontier providers (Claude Opus 4.7, GPT-5, Gemini 2.5 Flash) returned RED-tier triage at 9/9 sensitivity including on an image-only suspected snake-bite case where Gemma 4 e4b returned YELLOW with "no acute condition identified." Six local SLMs ranged from 0/5 to 9/9 sensitivity on the same cases. The atypical-MI text case was misclassified to YELLOW by 3 of 6 SLMs.

The two case studies converged on the same architectural primitive — a deterministic safety scaffolding pattern — without coordination. We pre-register a 12-model × 250-case evaluation (SentinelEval-250) with seven hypotheses, a defined statistical methodology, sample-size power analysis, and a 30-week timeline. We propose an architectural taxonomy of five compensations — deterministic safety nets, KB-grounded JSON-Schema output, two-pass vision-as-sensor pipelines, selective frontier escalation, and domain LoRA adaptation — that we hypothesize allow SLMs to carry production clinical traffic. The framing claim is that the right unit of evaluation is the pipeline, not the model.

Code, prompts, JSON schemas, safety-net rule sets, pilot results, and the SentinelEval-250 case construction at https://github.com/SankarSubbayya/sentinel-health (Apache-2.0).
```

### Keywords (Zenodo accepts unlimited; aim for ~10)

```
small language models
clinical decision support
offline AI
multimodal reasoning
community health workers
low-resource healthcare
LoRA fine-tuning
Gemma 4
frontier language models
pre-registered research plan
```

### Additional notes / comments

```
v1.5 · two case studies (Sentinel Health offline laptop deployment + Path to Care AMD MI300X deployment with LoRA fine-tuning) + a pre-registered research plan. Preliminary numbers in §7 are exploratory pilots, not powered for inferential claims. Companion artifacts: medRxiv preprint (DOI: TBD upon medRxiv posting), OSF pre-registration (DOI: TBD upon OSF locking), GitHub source repository at https://github.com/SankarSubbayya/sentinel-health under Apache-2.0.
```

### Related/alternate identifiers (optional)

- GitHub source code: `https://github.com/SankarSubbayya/sentinel-health` → relation: `is supplement to` (resource type: software)
- medRxiv DOI (after medRxiv assigns one): `10.1101/<NNNN>` → relation: `is supplemented by` (resource type: publication)
- OSF pre-registration DOI (after OSF locks one): `10.17605/OSF.IO/<NNNNN>` → relation: `is supplemented by` (resource type: publication / preregistration)

You can add these later — Zenodo allows editing the metadata of a published record (without changing the DOI) for related-identifier additions.

### License

```
Creative Commons Attribution 4.0 International (CC-BY-4.0)
```

### Version

```
1.5
```

---

## After Zenodo publishes

- Save the DOI (e.g., `10.5281/zenodo.NNNNNNNN`).
- Add it to the manuscript's references section as a self-citation in the next paper revision.
- Update the project README to link the Zenodo DOI alongside the GitHub repo.
- If a medRxiv DOI or OSF DOI is assigned later, return to the Zenodo record → Edit → add them as related identifiers. No new version needed.

## Versioning policy

Zenodo allows new versions of the same record. When the v2 (completed-study)
paper is ready (~9–12 months from now), upload it as a new version under
the same parent record. The parent (concept) DOI resolves to whichever
version is latest; each version retains its own DOI for archival pinning.
