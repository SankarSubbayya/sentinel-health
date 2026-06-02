---
marp: true
theme: default
paginate: true
size: 16:9
backgroundColor: "#FAFAF7"
color: "#18181B"
footer: "Sentinel Health · Gemma 4 Good Hackathon · May 2026"
style: |
  @import url("https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght,SOFT,WONK@9..144,300..900,0..100,0..1&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap");

  section {
    font-family: "Inter", -apple-system, "Segoe UI", sans-serif;
    padding: 56px 72px 80px 72px;
    font-size: 22px;
    line-height: 1.5;
    font-feature-settings: "ss01" on, "cv11" on;
  }
  h1 {
    font-family: "Fraunces", "Iowan Old Style", Georgia, serif;
    color: #0F766E;
    font-weight: 600;
    font-size: 72px;
    margin: 0 0 8px 0;
    letter-spacing: -0.035em;
    line-height: 0.95;
    font-variation-settings: "opsz" 144, "SOFT" 30, "WONK" 1;
  }
  h2 {
    font-family: "Fraunces", "Iowan Old Style", Georgia, serif;
    color: #0F766E;
    font-weight: 500;
    font-size: 44px;
    margin: 0 0 24px 0;
    border-bottom: 2px solid #CCFBF1;
    padding-bottom: 10px;
    letter-spacing: -0.025em;
    line-height: 1.05;
    font-variation-settings: "opsz" 96, "SOFT" 20, "WONK" 0;
  }
  h3 {
    color: #0F766E;
    font-weight: 600;
    font-size: 22px;
    margin: 0 0 6px 0;
    letter-spacing: -0.005em;
  }
  strong { color: #134E4A; }
  code {
    font-family: "JetBrains Mono", "SF Mono", Menlo, monospace;
    background: #ECFDF5;
    color: #115E59;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 0.88em;
  }
  pre {
    background: #134E4A !important;
    color: #CCFBF1 !important;
    border-radius: 8px;
    padding: 20px 24px;
    font-size: 17px;
    line-height: 1.5;
  }
  pre code { background: transparent; color: inherit; padding: 0; }
  table {
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 19px;
  }
  th {
    background: #ECFDF5;
    color: #115E59;
    text-align: left;
    padding: 10px 14px;
    font-weight: 600;
    border-bottom: 2px solid #A7F3D0;
  }
  td {
    padding: 9px 14px;
    border-bottom: 1px solid #E5E7EB;
    vertical-align: top;
  }
  blockquote {
    border-left: 4px solid #0F766E;
    background: #F0FDF4;
    padding: 14px 20px;
    margin: 0;
    color: #134E4A;
    font-style: italic;
    font-size: 22px;
  }
  ul, ol { margin: 0 0 12px 0; padding-left: 28px; }
  li { margin: 6px 0; }
  .lead {
    font-size: 26px;
    line-height: 1.5;
    color: #27272A;
    max-width: 920px;
  }
  .small { font-size: 16px; color: #52525B; }
  .center { text-align: center; }
  .tag {
    display: inline-block;
    background: #0F766E;
    color: white;
    padding: 4px 12px;
    border-radius: 4px;
    font-size: 14px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-right: 6px;
  }
  .tag-outline {
    background: white;
    color: #0F766E;
    border: 2px solid #0F766E;
  }
  .tag-red { background: #DC2626; }
  .cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 24px 0;
  }
  .card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 18px 20px;
  }
  .card h4 {
    color: #115E59;
    font-size: 17px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin: 0 0 8px 0;
    font-weight: 600;
  }
  .card p { margin: 0; font-size: 17px; line-height: 1.5; color: #3F3F46; }
  .metric-cards {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin: 18px 0 0 0;
  }
  .metric-card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 18px 18px 16px 18px;
    border-top: 3px solid #0F766E;
  }
  .metric-card.red { border-top-color: #DC2626; }
  .metric-value {
    font-family: "JetBrains Mono", monospace;
    font-size: 38px;
    font-weight: 700;
    line-height: 1;
    color: #134E4A;
    letter-spacing: -0.02em;
    margin: 0 0 6px 0;
  }
  .metric-card.red .metric-value { color: #991B1B; }
  .metric-label {
    font-family: "JetBrains Mono", monospace;
    font-size: 10px;
    font-weight: 600;
    color: #6B7280;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    margin: 0 0 12px 0;
  }
  .metric-card p { margin: 0; font-size: 14px; line-height: 1.45; color: #3F3F46; }
  .pipeline {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
    margin: 24px 0;
    align-items: stretch;
  }
  .stage {
    background: white;
    border: 2px solid #0F766E;
    border-radius: 10px;
    padding: 18px 16px;
    position: relative;
  }
  .stage.safety { border-color: #DC2626; }
  .stage .n {
    font-family: "JetBrains Mono", monospace;
    color: #5EEAD4;
    font-size: 14px;
    font-weight: 700;
  }
  .stage.safety .n { color: #FCA5A5; }
  .stage h4 { color: #115E59; font-size: 18px; margin: 4px 0 6px 0; }
  .stage.safety h4 { color: #991B1B; }
  .stage .latency {
    font-family: "JetBrains Mono", monospace;
    color: #0F766E;
    font-size: 13px;
    font-weight: 600;
  }
  .stage.safety .latency { color: #DC2626; }
  .stage .body { font-size: 14px; color: #52525B; margin-top: 8px; line-height: 1.45; }
  /* Cover slide — dark, with teal+red accents matching the demo's RED triage UI. */
  section.cover,
  section.cover[data-class~="cover"] {
    background:
      radial-gradient(900px 600px at 92% -8%, rgba(15,118,110,0.22) 0%, transparent 60%),
      radial-gradient(800px 600px at -4% 108%, rgba(220,38,38,0.18) 0%, transparent 55%),
      linear-gradient(180deg, #0B1413 0%, #11181B 100%) !important;
    background-color: #0B1413 !important;
    color: #FAFAFA !important;
  }
  section.cover footer { color: rgba(255,255,255,0.4) !important; }
  section.cover .eyebrow {
    display: inline-block;
    font-family: "JetBrains Mono", monospace;
    font-size: 12px;
    font-weight: 500;
    color: #5EEAD4;
    letter-spacing: 0.32em;
    text-transform: uppercase;
    padding: 5px 11px;
    border: 1px solid rgba(94,234,212,0.45);
    background: rgba(15,118,110,0.10);
    border-radius: 3px;
    margin-bottom: 26px;
  }
  section.cover h1 {
    color: #FAFAFA;
    font-family: "Fraunces", "Iowan Old Style", Georgia, serif;
    font-weight: 500;
    font-size: 132px;
    line-height: 0.88;
    letter-spacing: -0.055em;
    margin: 0 0 14px 0;
    font-variation-settings: "opsz" 144, "SOFT" 40, "WONK" 1;
  }
  section.cover h1 .accent {
    color: #5EEAD4;
    font-weight: 400;
    font-style: italic;
    font-variation-settings: "opsz" 144, "SOFT" 70, "WONK" 1;
  }
  section.cover .rule {
    width: 56px;
    height: 2px;
    background: #DC2626;
    margin: 30px 0 22px 0;
    border-radius: 1px;
  }
  section.cover .lead {
    color: #E4E4E7;
    font-size: 25px;
    max-width: 940px;
    font-weight: 400;
    line-height: 1.5;
  }
  section.cover .lead strong { color: #FAFAFA; font-weight: 600; }
  section.cover .lead .second {
    display: block;
    margin-top: 10px;
    color: #A1A1AA;
    font-size: 21px;
  }
  section.cover .meta {
    color: #71717A;
    font-family: "JetBrains Mono", monospace;
    font-size: 13px;
    letter-spacing: 0.18em;
  }
  section.cover code {
    background: rgba(15,118,110,0.18);
    color: #99F6E4;
    border: 1px solid rgba(94,234,212,0.30);
  }
  section.cover .tag {
    background: rgba(15,118,110,0.18);
    color: #99F6E4;
    border: 1px solid rgba(94,234,212,0.40);
    font-family: "JetBrains Mono", monospace;
    font-size: 11px;
    letter-spacing: 0.16em;
    padding: 5px 11px;
  }
  section.cover .tag-red {
    background: rgba(220,38,38,0.15);
    color: #FCA5A5;
    border-color: rgba(220,38,38,0.45);
  }
  section.cover .tag-outline {
    background: transparent;
    color: #A1A1AA;
    border-color: rgba(161,161,170,0.4);
  }
---

<!-- _class: cover -->
<!-- _backgroundColor: "#0B1413" -->
<!-- _color: "#FAFAFA" -->
<!-- _paginate: false -->

<span class="eyebrow">Offline triage · v0.1</span>

# Sentinel <span class="accent">Health</span>

<div class="rule"></div>

<p class="lead">
<strong>Multimodal Gemma 4, a deterministic safety net, and a WhatsApp handoff to the hub physician.</strong>
<span class="second">Runs entirely on a clinic laptop with no internet. Scoped to the five emergencies where rural CHWs lose patients to delay: trauma, poisoning, snake bite, MI, stroke.</span>
</p>

<p style="margin-top:32px;">
  <span class="tag">GEMMA 4 GOOD HACKATHON</span>
  <span class="tag tag-red">FIVE TAI-VADE EMERGENCIES</span>
  <span class="tag tag-outline">EN · HI · TA · ML</span>
</p>

<p class="meta" style="margin-top:36px;">
  SANKAR SUBBAYYA   ·   CLINICAL ADVISOR: DR. P. HARI SUBACINI   ·   2026.05.30
</p>

<!--
SPEAKER NOTES — Slide 1 (~10s)
Open with the one-liner under the title. Don't read the tags out loud.
Hold for ~5 seconds, then advance.
-->

---

## What an ASHA worker actually has at 9:30 PM on a Tuesday

<div class="cards">
<div class="card">
<h4>The CHW in the village</h4>
<p><em>"This patient looks serious. Should I send her to the PHC, or wait?"</em></p>
<p style="margin-top:10px; color:#6B7280;">Today: an MBBS-trained physician is 38 km away. No textbook in the bag.</p>
</div>
<div class="card">
<h4>The hub physician on WhatsApp</h4>
<p><em>"Send me the patient's symptoms — but write it the way I need to read it."</em></p>
<p style="margin-top:10px; color:#6B7280;">Today: a voice note of vague terms. No vitals format, no escalation tier.</p>
</div>
<div class="card">
<h4>The district health office</h4>
<p><em>"Which CHW handled what, in which village, with what outcome?"</em></p>
<p style="margin-top:10px; color:#6B7280;">Today: a paper register. No record-of-care, no analytics.</p>
</div>
</div>

<p class="lead" style="margin-top:24px;">
<strong>India has roughly one million ASHAs.</strong> The blocker on rural emergency outcomes isn't medicine. It's the 4–6 hour gap between the first physical contact and the first physician opinion.
</p>

<!--
SPEAKER NOTES — Slide 2 (~25s)
Three personas, three problems, one shared bottleneck: the first contact is
not the first medical decision. Sentinel collapses that gap to under a minute.
-->

---

## A real case from the demo · 32 seconds, end-to-end

<p class="lead" style="margin-bottom:12px;"><strong>60-year-old woman. Jaw pain, nausea, fatigue, one hour. Diabetic + hypertensive.</strong> The CHW types it in Tamil.</p>

<table style="font-size: 19px;">
<tbody>
<tr>
<td style="width:84px;"><code>t=0s</code></td>
<td>CHW opens Sentinel on the offline laptop. Picks the Tamil chip. Types or speaks the symptoms.</td>
</tr>
<tr>
<td><code>t=2ms</code></td>
<td><strong>Deterministic safety net fires</strong>: female · jaw pain · diabetic match the atypical-MI keyword set. <code>force_red=true</code> regardless of what Gemma says next.</td>
</tr>
<tr>
<td><code>t=4s</code></td>
<td>Gemma 4 reads the symptoms, picks <strong>STEMI/NSTEMI</strong> from the KB candidates. JSON Schema rejects any free-text invention.</td>
</tr>
<tr>
<td><code>t=10s</code></td>
<td>CHW taps the camera, attaches the 12-lead ECG photo. Gemma 4's vision module confirms ST elevation in leads II, III, aVF.</td>
</tr>
<tr>
<td><code>t=24s</code></td>
<td><span style="color:#B91C1C; font-weight:600;">● RED</span> · differential, during-transport protocol, thrombolysis criteria. <strong>WhatsApp handoff message generated</strong> in the PHC group format with ambulance number + ETA.</td>
</tr>
<tr>
<td><code>t=32s</code></td>
<td>CHW taps "Send to hub physician" — the message opens in WhatsApp, pre-typed. Audit record + ECG photo persist locally.</td>
</tr>
</tbody>
</table>

<p class="small" style="margin-top:14px;">
The safety net cannot be talked out of <code>RED</code> by a more "reassuring" LLM. Gemma's job is the structured plan, not the triage class.
</p>

<!--
SPEAKER NOTES — Slide 3 (~30s)
This is the "what is it" slide. Land three beats: (1) deterministic safety
overrides the LLM, (2) JSON Schema means the model picks from a KB list, it
can't invent, (3) the WhatsApp message is in the format Dr. Hari's group
already uses — no re-formatting for the receiving physician.
-->

---

## The four-stage pipeline

<div class="pipeline">
<div class="stage safety">
<div class="n">01</div>
<h4>Safety net</h4>
<div class="latency">&lt; 5 ms</div>
<div class="body">Keyword red-flag overrides. ~38 atypical-MI / stroke / poison patterns. Curated with Dr. Hari, not scraped.</div>
</div>
<div class="stage">
<div class="n">02</div>
<h4>Symptom intake</h4>
<div class="latency">voice or text</div>
<div class="body">Web Speech API for voice (Chrome cloud STT, Apple on-device STT). 4 languages. Optional ECG/wound photo.</div>
</div>
<div class="stage">
<div class="n">03</div>
<h4>Gemma 4 grounded</h4>
<div class="latency">3–5 s GPU · 20–40 s CPU</div>
<div class="body"><code>gemma4:e4b-it-q4_K_M</code> via Ollama. JSON Schema response. Multimodal: text + ECG/wound photo.</div>
</div>
<div class="stage">
<div class="n">04</div>
<h4>WhatsApp handoff</h4>
<div class="latency">&lt; 100 ms</div>
<div class="body"><code>wa.me</code> deep-link in real PHC group format. Ambulance, ETA, during-transport protocol.</div>
</div>
</div>

<p class="lead" style="margin-top:18px; font-size:23px;">
<strong>The safety net runs first</strong> because the model can be wrong, but the safety net is built from a clinician's red-flag list. Gemma's structured plan never determines triage class on its own.
</p>

<!--
SPEAKER NOTES — Slide 4 (~30s)
Hit the order. Safety first, intake second, model third, escalation last.
The "safety net runs first" line is the architectural commitment — the model
is a writer, the keyword layer is the decision-maker. Mention the bake-off
result on the next slide as supporting evidence.
-->

---

## Why Gemma 4 — and where it specifically earns its place

<div class="cards" style="grid-template-columns: repeat(2, 1fr);">
<div class="card">
<h4>Multimodal in 8B / sub-4B inference</h4>
<p>Gemma 4 reads ECG photos, wound images, and pill bottles. At <code>q4_K_M</code> the model is ~9.6 GB on disk with a sub-4B inference footprint — small enough to bake into a Cloud Run image and small enough to load on a 16 GB laptop alongside Ollama.</p>
</div>
<div class="card">
<h4>JSON Schema-enforced output via Ollama</h4>
<p>We pass an explicit <code>format</code> schema to Ollama. The model returns <code>{triage, condition_id, rationale, transport}</code> — it can't free-form into "this might be MI but possibly anxiety". <code>condition_id</code> is constrained to the curated KB list, so it picks, never invents.</p>
</div>
<div class="card">
<h4>Open weights · no API key · no per-call cost</h4>
<p>Every other comparable clinical AI assumes a working internet and a credit card. Sentinel doesn't. A state health system can deploy this on refurbished laptops, no recurring spend. We tested on three models (Gemma 4 8B, MedGemma 4B Q8, MedGemma 4B) — <strong>100% sensitivity held across all three</strong>. The safety net carries; the model is replaceable.</p>
</div>
<div class="card">
<h4>4-language reasoning, with an honest STT caveat</h4>
<p>Gemma reasons in English, Hindi, Tamil, Malayalam. Voice transcription is a separate question: we tried Whisper-small for offline STT and Indian-language quality wasn't acceptable. The shipping app uses Chrome's cloud STT (which crushes Whisper for Indic scripts) with a clear "voice needs internet" hint. Diagnose itself remains offline.</p>
</div>
</div>

<!--
SPEAKER NOTES — Slide 5 (~30s)
The honest STT slide. We picked Gemma 4 because vision + small footprint +
open weights = the rural-laptop fit. We did NOT pick Whisper for transcription
because it isn't good enough for Tamil/Malayalam. Be willing to say that
out loud — it's the credibility move.
-->

---

## Live demo · 5:50 walkthrough

<table>
<thead>
<tr><th style="width: 70px;">t</th><th>Beat</th><th>What you see</th></tr>
</thead>
<tbody>
<tr><td><code>0:00</code></td><td><strong>Empty state</strong> · Tamil selected · five scope chips</td><td>How-to · TAI-VADE chips · example cards</td></tr>
<tr><td><code>0:30</code></td><td><strong>Cardiac · RED</strong> · 60yo woman, jaw pain, diabetic</td><td><span style="color:#B91C1C; font-weight:600;">● RED</span> · safety net cited · STEMI/NSTEMI</td></tr>
<tr><td><code>1:40</code></td><td><strong>ECG attach</strong> · camera button on the offline laptop</td><td>Gemma vision · ST elevation called · differential refined</td></tr>
<tr><td><code>2:50</code></td><td><strong>Snake bite · RED</strong> · monsoon season, rural India</td><td><span style="color:#B91C1C; font-weight:600;">● RED</span> · neurotoxic protocol · ASV dose</td></tr>
<tr><td><code>3:40</code></td><td><strong>Found unconscious · no history</strong></td><td>Photograph pills/bottles · partial input handling</td></tr>
<tr><td><code>4:30</code></td><td><strong>WhatsApp handoff</strong> · pre-typed message opens</td><td>PHC group format · ambulance # · ETA</td></tr>
<tr><td><code>5:20</code></td><td><strong>Audit log</strong> · the village's record-of-care</td><td>Append-only JSONL · ECG side-file persists</td></tr>
</tbody>
</table>

<p class="lead" style="margin-top:16px; font-size:21px;">
Two demo URLs: <code>triage.accurateai.org/demo</code> (full PHI features, runs on my laptop) and <code>huggingface.co/spaces/sankara68/sentinel-health</code> (CPU, always-on, PHI persistence off).
</p>

<!--
SPEAKER NOTES — Slide 6 (~5s — then switch to video or live demo)
Don't read each beat. Switch to youtu.be/vQ-ansEd8dY or open
triage.accurateai.org/demo and walk the Cardiac example.
-->

---

## What's measured — and where the safety net earns its keep

<div class="metric-cards">

<div class="metric-card red">
<div class="metric-value">100%</div>
<div class="metric-label">SENSITIVITY · 29 / 29 RED CASES</div>
<p>Zero missed red flags across the evaluation set. <strong>True across all three models tested</strong> (Gemma 4 8B, MedGemma 4B Q8, MedGemma 4B). The safety net, not the model, carries this.</p>
</div>

<div class="metric-card">
<div class="metric-value">80%</div>
<div class="metric-label">SPECIFICITY · 29 / 31 OVERALL</div>
<p>2 GREEN cases triaged YELLOW by an over-cautious model. Acceptable failure mode — the cost of a false escalation is a phone call; the cost of a missed MI is irreversible.</p>
</div>

<div class="metric-card">
<div class="metric-value">197</div>
<div class="metric-label">PYTESTS PASSING</div>
<p>Unit + integration. Covers the safety net keyword rules, JSON-Schema validation, the WhatsApp message generator, image validation, audit-log roundtrip.</p>
</div>

<div class="metric-card">
<div class="metric-value">4</div>
<div class="metric-label">LANGUAGES · INDIC SCRIPTS</div>
<p>English, Hindi, Tamil, Malayalam — UI, voice intake, Gemma reasoning prompts, escalation message. Reviewed end-to-end with Dr. Hari.</p>
</div>

</div>

<p class="small center" style="margin-top:16px;">
The model is a writer. The safety net is the doctor. That's the originality.
</p>

<!--
SPEAKER NOTES — Slide 7 (~30s)
The 100% sensitivity number is the headline. The bake-off across three
models is the proof — it's the architecture, not the weights. Specificity
of 80% is honest: we accept a small over-triage rate because under-triage
is catastrophic.
-->

---

## Three buyers · one deployment unit

<div class="cards" style="grid-template-columns: repeat(3, 1fr);">

<div class="card">
<h4>ASHA / CHW</h4>
<p style="font-size:14px; line-height:1.45;"><strong>Before:</strong> guess and refer. No textbook, no second opinion until the PHC.</p>
<p style="font-size:14px; line-height:1.45; margin-top:6px;"><strong>After:</strong> 30-second structured triage, in her own language, with a ready-to-send escalation.</p>
</div>

<div class="card">
<h4>Hub physician (PHC)</h4>
<p style="font-size:14px; line-height:1.45;"><strong>Before:</strong> WhatsApp voice notes she has to re-interpret while seeing other patients.</p>
<p style="font-size:14px; line-height:1.45; margin-top:6px;"><strong>After:</strong> messages in her own group format with vitals, differential, ETA. Reads in 5 seconds.</p>
</div>

<div class="card">
<h4>District / NHM</h4>
<p style="font-size:14px; line-height:1.45;"><strong>Before:</strong> paper register. No outcome tracking.</p>
<p style="font-size:14px; line-height:1.45; margin-top:6px;"><strong>After:</strong> append-only audit log per laptop. De-identifiable rollup for the district health office.</p>
</div>

</div>

<div class="metric-cards" style="grid-template-columns: repeat(3, 1fr); margin-top:14px;">

<div class="metric-card">
<div class="metric-value">~1M</div>
<div class="metric-label">ASHAS · INDIA ALONE</div>
<p>National Health Mission workforce. <strong>Add Bangladesh, Indonesia, Sub-Saharan Africa</strong> — the CHW model is the standard low-resource primary care interface.</p>
</div>

<div class="metric-card">
<div class="metric-value">$0</div>
<div class="metric-label">RECURRING · PER CHW</div>
<p>Open weights, runs on refurbished hardware. No subscription, no per-call API fee, no PHI on a third-party server. State health systems can budget this.</p>
</div>

<div class="metric-card">
<div class="metric-value">~5 hrs</div>
<div class="metric-label">TIME-TO-PHYSICIAN GAP</div>
<p>Field-typical delay from first symptom to first physician opinion in remote Tamil Nadu (Dr. Hari's observation). Sentinel target: <strong>under 5 minutes</strong>.</p>
</div>

</div>

<!--
SPEAKER NOTES — Slide 8 (~25s)
Three personas, three before/afters. Then three numbers: TAM (~1M ASHAs),
unit economics ($0 recurring), outcome gap (5 hours → 5 minutes). Don't
hyperbolize — the field number is from Dr. Hari, not a Gartner report.
-->

---

## What's next — and what we deliberately left out

<div class="cards" style="grid-template-columns: repeat(2, 1fr);">
<div class="card">
<h4>Offline STT done right</h4>
<p>Whisper-small was shipped and reverted: English fine, Tamil/Malayalam unacceptable. Path forward is either a fine-tuned Whisper on Indic medical terms or AI4Bharat's IndicConformer — not a stock open model. Until then, voice uses Chrome STT with a clear connectivity hint.</p>
</div>
<div class="card">
<h4>Hub physician dashboard</h4>
<p>Today the handoff lands in a WhatsApp group. Next: a lightweight dashboard at the PHC tablet for the physician to triage incoming messages, acknowledge them, and close the loop back to the CHW.</p>
</div>
<div class="card">
<h4>Scope expansion beyond TAI-VADE</h4>
<p>Obstetric emergencies (post-partum hemorrhage, eclampsia), pediatric severe fever, snake-bite serotyping by photo. Each addition is a KB entry + a safety-net keyword set + a few eval cases. The architecture doesn't change.</p>
</div>
<div class="card">
<h4>What we left out on purpose</h4>
<p>No generic "ask the AI anything" mode. No free-form chat. No conditions outside the five-emergency scope. The safety net only works because the scope is bounded; broadening the surface would dilute the only thing that makes this safe.</p>
</div>
</div>

<!--
SPEAKER NOTES — Slide 9 (~25s)
The roadmap slide. The "left out on purpose" card is the discipline statement.
Most clinical AI demos fail because they try to be everything; ours works
because it isn't. That's the message.
-->

---

<!-- _class: cover -->
<!-- _backgroundColor: "#0B1413" -->
<!-- _color: "#FAFAFA" -->

<span class="eyebrow">Try it · &lt; 30 seconds</span>

# Sentinel <span class="accent">Health</span>

<div class="rule"></div>

<p class="lead">
<strong>One laptop, no internet, four languages, five emergencies.</strong>
<span class="second">Live demo on the clinic laptop via Cloudflare tunnel. Always-on public demo on Hugging Face Spaces (CPU, ~30 s/call).</span>
</p>

<div style="background: rgba(13,30,28,0.7); border: 1px solid rgba(94,234,212,0.18); border-radius: 8px; padding: 22px 26px; max-width: 940px; margin-top: 22px;">
<pre style="background:transparent !important; color:#99F6E4 !important; padding:0; margin:0; font-size:18px; line-height:1.65;"><code><span style="color:#A1A1AA;"># Live demo + project pages</span>
open <strong>https://triage.accurateai.org/demo</strong>
open <strong>https://sentinel.accurateai.org</strong>
open <strong>https://huggingface.co/spaces/sankara68/sentinel-health</strong>

<span style="color:#A1A1AA;"># Or clone &amp; run yourself</span>
git clone github.com/SankarSubbayya/sentinel-health
ollama pull gemma4:e4b-it-q4_K_M
uv sync &amp;&amp; uv run uvicorn main:app --port 8000
open http://localhost:8000/demo</code></pre>
</div>

<p class="meta" style="margin-top:28px;">
GITHUB.COM/SANKARSUBBAYYA/SENTINEL-HEALTH   ·   APACHE-2.0   ·   CLINICAL ADVISOR: DR. P. HARI SUBACINI
</p>

<!--
SPEAKER NOTES — Slide 10 (~15s, closing)
Close with the one-liner. Show the URLs. Thank Dr. Hari by name. Don't
take a curtain call — the demo was the curtain call.
-->
