# Sentinel Health — Week 2 TODO

Pick the **first unchecked, non-BLOCKED** task each session. One task per session.

Acceptance criteria are explicit per task. If you can't satisfy them, mark the task `[BLOCKED: <reason>]` and move on.

---

## Week 2 — Web app + voice + multi-turn (May 4 – May 10, 2026)

### Backend

- [x] **W2-B1: Expose `during_transport` in the `/api/v1/diagnose` response.** — Code shipped in commit after iteration 1 (timed out before the unit-test step). `app/services/diagnosis.py` now attaches `response["during_transport"]` from the first matched RED-eligible KB candidate.

- [x] **W2-B1-test: Add unit test for `during_transport` propagation.**
  - Verify in `tests/unit/test_diagnosis.py` that when a RED-eligible condition matches (e.g., chest pain → ACS), `result["during_transport"]` is a non-empty string. Use `patch_ollama_generate` with a RED-flagged response.
  - Acceptance: new test passes; existing tests stay green.
  - Files: `tests/unit/test_diagnosis.py`.

- [x] **W2-B2: Add `POST /api/v1/clarify` endpoint.**
  - Returns 1–2 high-yield clarifying questions targeted at the most likely differential, given the symptoms so far.
  - Use a separate prompt (don't reuse the diagnosis prompt). Output schema: `{"questions": [{"id": "q1", "text": "...", "rationale": "..."}], "session_id": "..."}`.
  - Cap at 2 questions per the PRD's "few smart questions" principle.
  - Acceptance: integration test that posts symptoms and asserts 1–2 questions returned, each non-empty.
  - Files: `app/api/routes.py`, `app/services/diagnosis.py` (new method), `tests/integration/test_api.py`.

- [x] **W2-B3: Add `GET /api/v1/kb/conditions` and `GET /api/v1/kb/conditions/{id}` endpoints.**
  - Returns the KB conditions list (id, name, category, urgency only) and a single condition by id (full record).
  - Acceptance: integration tests asserting the snake_bite condition has `folk_error_correction` field exposed via the detail endpoint.
  - Files: `app/api/routes.py`, `tests/integration/test_api.py`.

- [x] **W2-B4: Add a "snake-bite folk-error" detector that runs on every diagnose call.**
  - If the symptoms text contains any of: "tied a rope", "tourniquet", "applied tourniquet", "cut and suck", "induced vomiting", AND a snake-bite or poisoning red flag fired, attach `response.folk_error_correction` (string) with the counter-instruction from the matched condition.
  - Acceptance: unit test that the snake_02 vignette ("family tied a rope") triggers the correction text being present in the response.
  - Files: `app/services/diagnosis.py`, `tests/unit/test_diagnosis.py`.

### Frontend

- [ ] **W2-F1: Render `during_transport` as a distinct panel in the UI when triage is RED.**
  - The new `demo/index.html` already has the CSS/HTML structure (`.action-section.transport`); wire it to read `response.during_transport` (preferred) before falling back to `differential_diagnosis[0].during_transport`.
  - Acceptance: a curl call returns the transport text and (manually) it shows in a panel below the action.
  - File: `demo/index.html`.

- [ ] **W2-F2: Render `folk_error_correction` as a prominent banner above the differential.**
  - Yellow/orange callout, bold "DO NOT" copy. This is the doctor's specific request.
  - Acceptance: the snake bite + tourniquet example renders the correction banner.
  - File: `demo/index.html`.

- [ ] **W2-F3: Add multi-turn clarifying flow.**
  - After the first diagnose response, if confidence on the top differential is < 0.6, fetch `/api/v1/clarify` and render the questions as inline buttons. User clicks an answer or types one, then re-submits with combined context. Cap at 2 rounds total.
  - Acceptance: a low-confidence case shows clarifying questions; clicking a button extends the conversation.
  - File: `demo/index.html`. Depends on **W2-B2**.

- [ ] **W2-F4: KB browser modal.**
  - Add a small "Browse KB" link in the header that opens a modal listing all conditions (grouped by category), each clickable to show full record (symptoms, guideline, during-transport, folk-error if any).
  - Acceptance: opens on click, lists all 18 conditions, snake_bite shows its folk-error.
  - File: `demo/index.html`. Depends on **W2-B3**.

- [ ] **W2-F5: Local notes via SQLite-WASM.**
  - On every diagnose response, persist `{session_id, timestamp, symptoms, triage_level, top_diagnosis}` to a local SQLite database in the browser. Add a "Past patients" panel in the header that lists the last 20 saves.
  - Acceptance: can refresh the page and still see past patient list.
  - File: `demo/index.html`.

### Polish

- [ ] **W2-P1: Replace `demo/index.html` body fontset with a system stack guaranteed to work offline.**
  - Audit the current `--font` variable — make sure no remote fonts (`fonts.googleapis.com` etc.) are referenced anywhere in the app. The offline claim is load-bearing.
  - Acceptance: `grep -r 'fonts.googleapis\|cdn\|http' demo/` returns zero hits in `<link>` or `<script src>` tags.
  - File: `demo/index.html`.

- [ ] **W2-P2: Add `/healthz` lightweight health endpoint that doesn't hit Ollama (for liveness checks).**
  - Returns `{"status": "ok"}` always, < 5 ms.
  - Acceptance: integration test that `/healthz` returns 200 even if Ollama is unreachable (mock the LLM client to fail health_check).
  - Files: `app/api/routes.py`, `tests/integration/test_api.py`.

- [ ] **W2-P3: Trim the docstrings of internal modules; add a one-line module docstring to each `app/**/*.py` file describing its job.**
  - Helps future contributors and the writeup.
  - Acceptance: every Python file under `app/` has a one-line top-of-file docstring; pytest still green.
  - Files: `app/**/*.py`.

---

## Week 3 — Demo + writeup + submit (May 11 – May 17, 2026)

These need human review (video direction, copy, deployment credentials) and are explicitly out of scope for the autonomous worker.

- [ ] [BLOCKED: needs human direction] **W3-D1: Dockerfile for Ollama-in-container** — pulls `gemma4:e4b-it-q4_K_M`, runs FastAPI + Ollama in one container.
- [ ] [BLOCKED: needs human direction] **W3-D2: docker-compose.yml** for judges to spin up locally.
- [ ] [BLOCKED: needs human direction] **W3-D3: Cloud deploy** — Fly.io or Railway with Ollama warm-loaded.
- [ ] [BLOCKED: needs human voice] **W3-W1: Kaggle writeup outline** (≤ 1500 words).
- [ ] [BLOCKED: needs human direction] **W3-V1: Video script** (≤ 3 min) — Maria + atypical-ACS hero + clinician (Mama) endorsement.
- [ ] [BLOCKED: needs human design call] **W3-V2: Cover image / media gallery**.
- [ ] [BLOCKED: needs human review] **W3-S1: Final submission rehearsal** — needs human eyes on the Kaggle form.

---

## Backlog / nice-to-have (only if Week 2 finishes early)

- [ ] [BLOCKED: deferred — only after Week 2 fully complete] **BL-1: Hindi voice input.** Web Speech API supports `hi-IN`. Add a language toggle.
- [ ] [BLOCKED: deferred — only after Week 2 fully complete] **BL-2: Print/PDF export of patient note.**
- [ ] [BLOCKED: deferred — only after Week 2 fully complete] **BL-3: Auto-escalation timer** — if no provider review in N minutes, surface a warning (mirrors the doctor's 10-minute ECG SLO).
- [ ] [BLOCKED: deferred — only after Week 2 fully complete] **BL-4: Multilingual voice** — Spanish, Swahili (`es-ES`, `sw-KE`).

---

*Format key: `- [ ] task` = todo. `- [x] task` = done. `- [ ] [BLOCKED: reason] task` = needs human.*
