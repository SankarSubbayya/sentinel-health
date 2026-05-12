# Sentinel Health — 3-Minute Demo Video

**Target runtime:** 2:50–2:58 (leave ~10s of headroom under the 3:00 hard limit).
**Format:** YouTube, viewable without login.
**Scoring weights to hit:** Impact & Vision (40), Storytelling (30), Technical Depth (30).

---

## Structure at a glance

| Beat | In  | Out  | Shot |
|------|-----|------|------|
| 1. Hook — the human stakes | 0:00 | 0:15 | Talking head + B-roll of rural clinic / CHW |
| 2. Problem in one sentence | 0:15 | 0:30 | Map / village footage + on-screen stat |
| 3. Live demo: snake-bite case | 0:30 | 1:30 | Screen capture of `localhost:8000/demo` |
| 4. Live demo: WhatsApp handoff | 1:30 | 2:00 | Screen capture → mobile capture of WhatsApp |
| 5. How it works (the tech)| 2:00 | 2:35 | Architecture diagram + Ollama log snippets |
| 6. Close — mission + URL | 2:35 | 2:55 | Logo, GitHub URL, demo URL, disclaimer card |

---

## Beat 1 — Hook (0:00–0:15)

**Voice-over (read warmly, not breathlessly):**

> "Two billion people get their primary care from a community health worker, not a doctor. They see chest pain. They see snake bites. They see strokes. And they have no internet to look anything up."

**Visual:** B-roll — rural clinic exterior, hands on a paper register, a phone showing "No signal". Cut to a CHW listening to a patient.

**Why this works:** Opens on impact. The number frames the stakes; the visuals say "this is real, not a slide."

---

## Beat 2 — Problem (0:15–0:30)

**VO:**

> "Time-critical conditions get misclassified as benign. Delayed escalation kills. We built Sentinel Health so a CHW with a laptop and no signal can still triage like there's a doctor in the room."

**Visual:** On-screen text card with the five TAI-VADE emergencies — Trauma, Poisoning, Snake Bite, MI, Stroke — fading in one by one. Logo pop at 0:28.

---

## Beat 3 — Live demo, snake-bite RED case (0:30–1:30)

**VO over screen capture of `http://localhost:8000/demo`:**

> "Here's what a CHW sees. No login, no cloud. The model — Gemma 4 — is running on this laptop. Watch."

**Action on screen:**
1. (0:32) Click the **"Snake bite · RED"** example button. Symptoms pre-fill.
2. (0:38) Click **Diagnose**. The "thinking" indicator runs ~3–5s on screen.
3. (0:45) The result card renders. Camera **pauses on the RED banner** for a beat.

**VO at 0:50:**

> "Triage: RED. Differential: snake-bite envenomation. But look at this — the safety layer didn't wait for the model. It picked up 'fang marks' from the keyword scan and forced RED before Gemma even answered. That's deliberate. The LLM can be wrong. The safety rule can't."

**Action on screen (0:55–1:15):**
- Scroll to the **during-transport protocol** card. Pause.
- Scroll to the **folk-error correction** banner ("DO NOT apply a tourniquet"). Pause.

**VO at 1:15:**

> "And because the worst snake-bite outcomes come from *folk* remedies, not the bite, we surface the correction the same way."

---

## Beat 4 — WhatsApp escalation (1:30–2:00)

**Action on screen:**
- (1:30) Scroll to the green **"Escalate to hub via WhatsApp"** card.
- (1:34) Click **"Preview message"** — message text expands.

**VO at 1:36:**

> "On a RED case, the app prepares the hub-physician handoff for the CHW. Reason, top differential, symptoms, during-transport protocol — already formatted. The CHW reviews, taps once, and WhatsApp opens with the message ready to send from their own phone."

**Action (1:48):** Tap **"Send via WhatsApp"** — cut to mobile screen capture of WhatsApp opening with the pre-filled message visible.

**VO at 1:54:**

> "Decision support, not auto-send. The CHW is always the one who hits the button."

---

## Beat 5 — How it works (2:00–2:35)

**Visual:** Replace the demo with the architecture diagram from `README.md`. Highlight elements as VO names them.

**VO:**

> "Three things make this work. **One:** Gemma 4 runs locally via Ollama. No cloud call ever leaves the laptop. **Two:** the model is *grounded* — it can only pick from conditions in our knowledge base, with confidence capped at 0.9. It never invents a diagnosis. **Three:** a deterministic safety layer screens for red flags independently. If the keyword scan fires, triage is forced to RED — even if Gemma said GREEN."

**Visual at 2:25:** Snap of `tests/eval_cases.py` running, terminal showing `PASS: 30/31  (96.8%)` and `SENSITIVITY: 21/21  (100.0%)`.

**VO at 2:28:**

> "Thirty-one synthetic clinical vignettes, thirty pass. Sensitivity one hundred percent — every RED case caught. The one failure is over-triage, not under-triage. Erring toward the hospital is the right error."

---

## Beat 6 — Close (2:35–2:55)

**Visual:** Logo card. Three URLs stacked:
- **Demo:** `<cloud-run-url>/demo`
- **Code:** `github.com/SankarSubbayya/sentinel-health`
- **Writeup:** Kaggle link

**VO:**

> "Sentinel Health. An offline triage net for the five grassroots emergencies. Built for the Gemma 4 Good Hackathon. Decision support — never a substitute for clinical judgment."

**End card (2:55):** Disclaimer in small text — *"Decision support tool. Not a diagnostic system. Always consult a qualified physician."*

---

## Production notes

- **Screen capture:** record at 1920×1080, 60fps. Crop the browser chrome so the demo fills the frame.
- **VO:** record dry, no background music under the demo segments — let the typing/clicking carry. Add a soft underscore (instrumental, royalty-free) at beats 1, 2, 6 only.
- **Captions:** burn-in subtitles for the entire video. Judges may watch muted.
- **Pace:** the snake-bite demo is the emotional anchor. Don't rush it. If you're tight on time, trim beat 5, not beat 3 or 4.
- **No fake data:** judges score 30 pts on "real, functional technology — not faked for demo." Run a real case; the timing variance is fine.
- **Cover image:** screenshot of the RED-banner triage card with the WhatsApp button visible. Crop tight.

## Recording checklist

- [ ] Ollama running, `gemma4:e4b-it-q4_K_M` warm (run a dummy diagnose once before record)
- [ ] `.env` has a real `HUB_PHYSICIAN_PHONE` (your own phone is fine — you'll be the recipient on camera)
- [ ] Demo URL deployed to Cloud Run, tested in the browser you're going to record
- [ ] Browser zoomed to 110–125% so text is readable in 1080p
- [ ] Mobile screen recording set up in advance (iOS Control Center / Android Screen Recorder)
- [ ] One full take dry-run before the real take
- [ ] Re-run eval suite the morning of, update the on-screen "18/20" if the number changed
