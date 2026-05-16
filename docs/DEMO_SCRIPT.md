# Sentinel Health — 3-Minute Demo Video

**Target runtime:** 2:50–2:58 (leave ~10s of headroom under the 3:00 hard limit).
**Format:** YouTube, viewable without login.
**Scoring weights to hit:** Impact & Vision (40), Storytelling (30), Technical Depth (30).
**Live demo URL:** https://triage.accurateai.org/demo

---

## Structure at a glance

| Beat | In  | Out  | Shot |
|------|-----|------|------|
| 1. Hook — the human stakes | 0:00 | 0:15 | Talking head + B-roll of rural clinic |
| 2. Problem in one sentence | 0:15 | 0:30 | TAI-VADE text card |
| 3. ECG · chest-pain RED with multimodal Gemma | 0:30 | 1:20 | Screen capture, attach photo, RED card with tabs |
| 4. WhatsApp handoff to hub group | 1:20 | 1:55 | Tap Copy → switch to WhatsApp group → paste |
| 5. Multilingual snake-bite + verifiable offline | 1:55 | 2:25 | Language switch · Hindi/Tamil · WiFi off + still works |
| 6. How it works (the tech)| 2:25 | 2:45 | Architecture diagram + eval numbers |
| 7. Close — mission + URLs | 2:45 | 2:58 | Logo, GitHub, demo URL, disclaimer card |

---

## Beat 1 — Hook (0:00–0:15)

**Voice-over (read warmly, not breathlessly):**

> "Two billion people get their primary care from a community health worker, not a doctor. They see chest pain. They see snake bites. They see strokes. And they have no internet to look anything up."

**Visual:** B-roll — rural clinic exterior, hands on a paper register, a phone showing "No signal". Cut to a CHW listening to a patient.

**Why this works:** Opens on impact. The number frames the stakes; the visuals say "this is real, not a slide."

---

## Beat 2 — Problem (0:15–0:30)

**VO:**

> "Time-critical conditions get misclassified as benign. Delayed escalation kills. We built Sentinel Health so a community health worker with a laptop and no signal can still triage like there's a doctor in the room — for the five grassroots emergencies."

**Visual:** Text card animating in:
- **Trauma** · **Poisoning** · **Snake Bite** · **MI** · **Stroke**

Sentinel Health logo pops at 0:28.

---

## Beat 3 — ECG · chest-pain RED with multimodal Gemma (0:30–1:20)

This is the **headline scene** — image input, real clinical reasoning, KB-grounded plan, all in one flow.

**VO over screen capture of `https://triage.accurateai.org/demo`:**

> "Here's what a CHW sees. No login, no cloud. The model — Gemma 4 — is running on a laptop. Watch."

**Action on screen:**
1. (0:32) Click the **"ECG · attach photo · RED"** example chip. Symptoms pre-fill: *"55-year-old with crushing chest pain and sweating for 30 minutes."*
2. (0:38) Click the **📷** button → attach a 12-lead ECG photo (have a real-looking one ready — search for "STEMI ECG" if you don't have one).
3. (0:43) Click **Diagnose**. "Thinking" indicator for ~5 seconds.
4. (0:48) The RED triage card renders. Camera pauses on the banner.

**VO at 0:50:**

> "Triage RED. The keyword scan caught 'crushing chest pain' before Gemma even answered. That's the safety layer — deterministic rules that fire independently of the model. The model can be wrong about subtle differentials. It cannot be wrong about whether the patient gets escalated."

**Action (0:58):** Click the **Action** tab — *not visible yet* but click. The recommendation reads:

> *"Establish IV access (venflon), give Aspirin 325 mg chewed + Clopidogrel 300 mg loading + Atorvastatin 80 mg loading if no contraindication. Photograph the 12-lead ECG and send to the hub physician for thrombolysis decision."*

**VO at 1:05:**

> "Look at this. The plan reads like a clinician wrote it — because our clinical advisor did. The exact preliminary protocol used at a PHC in Tamil Nadu, ready in five seconds."

**Action (1:10):** Click the **Transport** tab. Shows during-transport protocol + the **thrombolysis decision criteria** block — eligibility, contraindications.

**VO at 1:14:**

> "And on the Transport tab — thrombolysis decision criteria for the receiving hub. Because at the PHC level, the CHW doesn't have a defibrillator or a ventilator. Their job is stabilise and transport. The lytics decision belongs to the hub."

---

## Beat 4 — WhatsApp handoff to hub group (1:20–1:55)

**Action on screen (1:20):**
1. Click the **Escalate** tab. Card shows recipient: *"TVMCH Cardiology Hub and Spoke"*.
2. Show the 🚑 ETA chip: *"Transport ETA: ~22 min (18 km to TVMCH)"*.
3. (1:25) Type *"AMB-12"* into the **Ambulance #** input. The preview updates live to include the ambulance line.
4. (1:30) Click **Preview message**. Camera pauses on the structured handoff — From / To / H/o / Sentinel reading / Plan / Transport / Thrombolysis decision.

**VO at 1:34:**

> "The hub physician already has this format in their WhatsApp group. We give them exactly what they expect — H/o, Sentinel reading, plan at spoke, transport, thrombolysis decision. The CHW didn't have to type any of it."

**Action (1:42):** Click **"Copy to TVMCH Cardiology Hub and Spoke"** button. Button flips to "Copied — open WhatsApp and paste".

**Action (1:46):** Cut to **mobile screen capture** of WhatsApp opening the hub group → long-press in the message field → Paste → review the message in WhatsApp's compose view → tap Send.

**VO at 1:50:**

> "App prepares. CHW reviews. CHW commits. Decision support, never auto-send."

---

## Beat 5 — Multilingual + verifiable offline (1:55–2:25)

Two short proofs that the system isn't a one-language English-on-the-internet trick.

**Action on screen (1:55):**
1. Click **हि** (Hindi) in the language switch.
2. UI labels switch to Devanagari.
3. (2:00) Tap the **🎤** microphone, dictate in Hindi: *"बच्चे को साँप ने काटा है, दांत के निशान दिख रहे हैं"* (snake bit child, fang marks visible).
4. Click Diagnose.

**VO at 2:05:**

> "Hindi voice in. Reasoning in Devanagari out. Tamil and Malayalam too. Because the CHW in a village in Tamil Nadu doesn't speak English."

**Action (2:10):** RED card renders. Reasoning + recommendation visibly in Hindi script.

**Action (2:14):** Toggle macOS WiFi off in the menu bar. Status icon visibly changes to "Wi-Fi: Off".

**VO at 2:17:**

> "And here's the proof. No internet. The model is running on this device. Same architecture, same answer, no cloud call. We just expose a public URL through Cloudflare so judges can click a link."

**Action (2:20):** Run another diagnose locally (the previous one is already done) just to show the spinner → result with WiFi off.

---

## Beat 6 — How it works (2:25–2:45)

**Visual:** Switch to a static architecture diagram (clean version of the one in [README.md](README.md)):

```
Browser (voice) ─► FastAPI ─► DiagnosisService
                                  │
                                  ├── KB lookup ────────────┐
                                  ├── Gemma 4 / Ollama ─────┤
                                  ├── Safety override ──────┤ → RED ─► wa.me handoff
                                  └── Audit log ────────────┘
```

**VO:**

> "Three load-bearing pieces. One — Gemma 4 runs locally via Ollama. Two — it's grounded — picks from twenty-three KB conditions or returns 'No acute condition identified.' It never invents. Three — a deterministic safety engine that overrides the model on time-critical cases."

**Action (2:38):** Cut to terminal showing the eval suite:

```
PASS: 29/31  (93.5%)
SENSITIVITY: 21/21  (100.0%)
SPECIFICITY:  8/10  (80.0%)
```

**VO at 2:40:**

> "Thirty-one synthetic clinical vignettes. Sensitivity one hundred percent — no missed RED. The handful of failures are over-triage. Erring toward the hospital is the right error."

---

## Beat 7 — Close (2:45–2:58)

**Visual:** Logo card. Three URLs stacked:

- **Demo:** `https://triage.accurateai.org/demo`
- **Code:** `github.com/SankarSubbayya/sentinel-health`
- **Writeup:** Kaggle link

**VO:**

> "Sentinel Health. Offline triage for the five grassroots emergencies. Reviewed with a practising clinician. Decision support — never a substitute for clinical judgment. Built for the Gemma 4 Good Hackathon."

**End card (2:55):** Small text — *"Decision support tool. Not a diagnostic system. Always consult a qualified physician."*

---

## Production notes

- **Screen capture:** record at 1920×1080, 60fps. Crop browser chrome.
- **VO:** dry recording, no background music under the demo segments — let the typing/clicking carry. Soft underscore (royalty-free instrumental) only on beats 1, 2, 7.
- **Captions:** burn-in subtitles for the entire video. Judges may watch muted.
- **Pace:** Beat 3 (ECG + Action/Transport) is the emotional+technical anchor — don't rush it. If tight, trim Beat 6, not Beat 3.
- **Real data only:** judges score 30 pts on "real, functional technology — not faked for demo." Run a real case each time. Timing variance is fine.
- **Cover image:** screenshot of the RED-banner triage card with tabs + WhatsApp Copy button visible. Crop tight.

## Recording checklist

- [ ] Ollama running, `gemma4:e4b-it-q4_K_M` warm (run a dummy diagnose once before recording)
- [ ] `.env` configured:
  - `HUB_GROUP_NAME=TVMCH Cardiology Hub and Spoke`
  - `HUB_PHYSICIAN_NAME=Dr. Hari`
  - `FACILITY_NAME=PHC Anaikatti`
  - `CHW_NAME=Lakshmi`
  - `NEAREST_HUB_KM=18`
  - `AVG_AMBULANCE_KMH=50`
- [ ] Demo URL working: `curl https://triage.accurateai.org/healthz` → `{"status":"ok"}`
- [ ] Browser zoomed to 110–125% so text is readable in 1080p
- [ ] Hard-refresh demo so latest UI loads (Cmd-Shift-R)
- [ ] Mobile screen recording set up (iOS Control Center / Android Screen Recorder)
- [ ] A real-looking ECG photo on your desktop ready to attach
- [ ] WhatsApp on phone has the TVMCH Cardiology Hub group (real or pinned for demo)
- [ ] One full take dry-run before the real take
- [ ] Re-run eval suite the morning of, update on-screen numbers if they shift

## What to cut if you're over 3:00

In order:
1. Beat 6 (How it works) — trim to 12 seconds, drop the architecture diagram, keep only the eval numbers
2. Beat 5b (offline proof) — keep the language switch, drop the WiFi toggle scene
3. Beat 4 — trim the WhatsApp mobile cut, just show the Copy-to-clipboard toast

Keep beats 1, 2, 3 (ECG flow), and 7 no matter what. Those are the load-bearing seconds.
