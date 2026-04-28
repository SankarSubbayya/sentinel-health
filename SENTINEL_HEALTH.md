# Sentinel Health — Clinical Decision Support for Resource-Limited Settings

**Hackathon:** Gemma 4 Good Hackathon (Kaggle)  
**Submission Deadline:** May 18, 2026 (11:59 PM UTC)  
**Prize Tracks:** Main Track ($50k) + Health & Sciences Impact ($10k)  
**Status:** MVP in development

---

## Problem Statement

Healthcare providers in low-resource clinics lack timely access to clinical decision support. Community health workers (CHWs) and rural physicians must diagnose complex conditions—often cardiology, diabetes, general medicine—with limited reference materials and no internet connectivity.

**Sentinel Health** bridges this gap: an offline-first, voice-enabled AI clinical assistant that helps healthcare workers triage patients and recommend evidence-based care pathways.

---

## MVP Scope (Hackathon)

### Core Features
- **Voice-first interface** — Symptom collection via speech (supports multiple languages)
- **Multi-condition support** — Initial focus: cardiology, diabetes, general acute conditions
- **Offline-capable** — Runs locally on mobile/tablet via Ollama or LiteRT
- **Explainable reasoning** — Diagnosis with confidence scores and guideline citations
- **Safety layer** — Flags red flags and escalation triggers (e.g., hypertensive crisis)

### MVP Non-Goals (Post-Hackathon)
- Real patient data integration (HIPAA/compliance deferred)
- Chronic disease longitudinal tracking
- Full EHR integration
- Physician gold-standard validation dataset

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────┐
│  Mobile App (Flutter/React Native)                  │
│  • Voice input (on-device STT)                      │
│  • Symptom collection form                         │
│  • Diagnosis output + confidence                    │
│  • Offline-first design                            │
└──────────────────┬──────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
   ┌────▼────┐          ┌────▼────┐
   │ Ollama  │  OR      │ LiteRT  │
   │ (Local) │          │(Mobile) │
   └────┬────┘          └────┬────┘
        │                     │
   ┌────▼─────────────────────▼────┐
   │  Gemma 4 (Quantized)           │
   │  • Zero internet required       │
   │  • ~500MB-2GB model            │
   └────┬──────────────────────┬────┘
        │                      │
   ┌────▼──────────┐    ┌─────▼──────────┐
   │ Medical KB    │    │ Safety Rules   │
   │ (WHO, CDC)    │    │ (Red flags,    │
   │               │    │  escalation)   │
   └───────────────┘    └────────────────┘
```

### Components
| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Flutter or React Native | Cross-platform mobile, offline-first |
| **Voice** | on-device STT (Whisper/local) | Speech-to-text, no cloud required |
| **LLM** | Gemma 4 via Ollama/LiteRT | Local inference, clinical reasoning |
| **Knowledge Base** | Embedded medical data (JSON/SQLite) | Symptom-diagnosis mappings, guidelines |
| **Safety Layer** | Rule engine + LLM confidence scoring | Red flags, escalation criteria |
| **Storage** | SQLite | Local patient notes, history, sync queue |

---

## Workflow (Clinical)

```
1. CHW opens app at clinic (no internet)
2. Patient describes symptoms via voice
3. App transcribes and clarifies (via Gemma 4)
4. Gemma 4 generates differential diagnosis
5. Safety layer checks for red flags
6. App displays top 3 diagnoses + confidence scores
7. CHW can print, save, or sync later
```

### Example Output
```
PATIENT: Chest pain, shortness of breath, for 2 hours

DIAGNOSIS (Confidence):
1. Acute Coronary Syndrome (ACS) - 78%
   → RED FLAG: Immediate escalation to hospital
   → Guideline: 2023 ACC Chest Pain Protocol
   
2. Pulmonary Embolism - 15%
   → Check: Recent immobility? DVT risk?
   
3. Acute Gastroesophageal Reflux - 7%
   → Less likely given vital signs
```

---

## Development Roadmap

### Phase 1: MVP (Hackathon, Apr-May 2026)
- [ ] Mobile app skeleton (Flutter/React Native)
- [ ] Voice input + Gemma 4 integration via Ollama
- [ ] Symptom collection workflow
- [ ] Medical knowledge base (cardiology, diabetes, acute conditions)
- [ ] Safety rules and red-flag detection
- [ ] Demo video (3 min)
- [ ] Writeup (≤1,500 words)
- [ ] Deploy demo (accessible URL or files)

### Phase 2: Validation (Post-Hackathon)
- [ ] Collaborate with licensed physician
- [ ] Test on 20-50 representative patient cases
- [ ] Refine prompts and reasoning via DSPy
- [ ] HIPAA/compliance audit
- [ ] Beta deployment at pilot clinic

### Phase 3: Full Expansion (6-12 months)
- [ ] Longitudinal chronic disease tracking
- [ ] Multi-agent agentic system (Intake, Synthesis, Reasoning, Escalation)
- [ ] Integration with EHR/lab systems
- [ ] Bias auditing across demographics
- [ ] Regulatory approval (if applicable)

---

## Prize Strategy

| Track | Target | Why |
|-------|--------|-----|
| **Main Track** | $50,000 | Best overall (vision + storytelling + execution) |
| **Health & Sciences** | $10,000 | Democratizes healthcare knowledge |
| **Ollama Special** | $10,000 | Best local Gemma 4 deployment |
| **Total Potential** | **$60,000** | — |

### Video Demo Focus
- **Story:** CHW at rural clinic, no internet, uses Sentinel Health to avoid misdiagnosis
- **Emotional hook:** Real impact on patient outcomes
- **Technical showcase:** Voice-first, offline, instant diagnosis
- **3 minutes:** Problem → Solution → Demo → Impact

---

## Tech Stack

### Mobile
- **Framework:** Flutter (best for cross-platform, offline)
- **Language:** Dart
- **Offline:** Hive or SQLite for local storage

### LLM & Inference
- **Base Model:** Gemma 4 (quantized Q4 or Q5)
- **Runtime:** Ollama (CPU-friendly) or LiteRT (mobile-optimized)
- **Inference Framework:** Python backend (FastAPI) + mobile bridge

### Medical Knowledge
- **Sources:** WHO, CDC, ACC guidelines (public/open)
- **Format:** JSON or SQLite for fast retrieval
- **Safety Rules:** Python rule engine

### Deployment
- **Local:** APK/IPA for Android/iOS
- **Demo:** Docker container + web UI (for judges)

---

## Getting Started

### Prerequisites
- Python 3.12+
- Flutter/React Native (for mobile)
- Ollama (for local LLM)
- Git

### Setup (Draft)
```bash
# Clone repo
git clone <repo-url>
cd sentinel-health

# Install dependencies
pip install -r requirements.txt
flutter pub get  # if using Flutter

# Download Gemma 4 via Ollama
ollama pull gemma:7b-instruct-q4_K_M

# Run backend
python main.py

# Run mobile app
flutter run -d <device>
```

---

## File Structure
```
sentinel-health/
├── SENTINEL_HEALTH.md          # This file
├── main.py                     # FastAPI backend + LLM integration
├── mobile/                     # Flutter app
│   ├── lib/
│   ├── pubspec.yaml
│   └── ...
├── medical_kb/                 # Knowledge base (cardiology, diabetes, etc.)
│   ├── conditions.json
│   ├── symptoms.json
│   └── guidelines.json
├── safety_rules/               # Red flags, escalation logic
│   └── rules.py
├── tests/                      # Test cases
└── docs/                       # Architecture, design decisions
```

---

## Safety & Compliance Notes

### For MVP
- ✅ No real patient data (synthetic test cases only)
- ✅ Clear disclaimer: "For triage support only, not diagnosis"
- ✅ Always escalates critical conditions to human provider
- ✅ Open medical guidelines only (no proprietary data)

### For Production (Post-Hackathon)
- HIPAA compliance audit required
- Bias mitigation testing across demographics
- Licensed physician validation on patient datasets
- Regulatory pathway (e.g., FDA, local health authority)

---

## Success Criteria (Hackathon)

| Criterion | Target |
|-----------|--------|
| **Functional MVP** | Voice → Diagnosis → Safety flags working |
| **Offline capability** | Runs on tablet with no internet |
| **Video demo** | <3 min, compelling narrative, real demo (not faked) |
| **Code quality** | Well-documented, reproducible, clear Gemma 4 usage |
| **Writeup** | <1,500 words, explains architecture + Gemma 4 innovation |

---

## Contributing

This is a collaborative hackathon project. For post-hackathon expansion, we welcome physician collaborators, medical informaticists, and ML engineers.

---

## License

TBD (MIT or similar for open-source medical AI)

---

## Contact

**Hackathon Lead:** Sankar  
**Email:** sankara68@gmail.com  
**Timeline:** MVP by May 18, 2026

---

*Last updated: April 19, 2026*
