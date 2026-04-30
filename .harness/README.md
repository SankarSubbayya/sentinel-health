# Sentinel Health — Autonomous Worker Harness

A pillowtalk-style harness that lets Claude Code work through the **Week 2 backlog** on its own — wakes on a timer, picks one task from `TODO.md`, implements it, runs the test suite as a guardrail, and commits + pushes only if tests stay green.

---

## What it does

```
   ┌──────────────────────────────────────┐
   │ launchd / cron timer (every 30 min)  │
   └──────────────┬───────────────────────┘
                  ▼
   ┌──────────────────────────────────────┐
   │ heartbeat.sh                         │
   │  1. git pull --rebase                │
   │  2. pre-flight pytest (must be green)│
   │  3. claude reads CLAUDE.md + TODO.md │
   │     → does ONE task                  │
   │     → runs pytest                    │
   │     → commits + pushes if green      │
   │  4. post-flight pytest               │
   │  5. log session to /tmp/             │
   └──────────────────────────────────────┘
```

One **task per session**. The timer fires every 30 min by default — most sessions take 5–15 min, so the cadence stays clean.

---

## Files

| File | Purpose |
|---|---|
| [CLAUDE.md](CLAUDE.md) | Project context + rules the agent must follow (read once, deeply) |
| [TODO.md](TODO.md) | Week 2 task checklist — the agent's source of work |
| [heartbeat.sh](heartbeat.sh) | One-session runner with pytest guardrails |
| [install.sh](install.sh) | Schedules the heartbeat (launchd on macOS, cron on Linux) |
| [uninstall.sh](uninstall.sh) | Tears down the schedule |

---

## Setup

### Prerequisites
- `claude` CLI (`npm i -g @anthropic-ai/claude-code` and authenticated)
- `uv`, `git`
- Test suite is green (`uv run pytest -q`) — required by pre-flight

### Install (default 30-min cadence)
```bash
cd .harness
./install.sh
```

### Custom interval
```bash
INTERVAL_SECONDS=900 ./install.sh   # 15 min
INTERVAL_SECONDS=3600 ./install.sh  # 1 hr
```
(Minimum 600s / 10 min — anything less is too aggressive given pytest + claude timing.)

### Stop
```bash
./uninstall.sh
```

---

## Manual one-shot
You don't have to schedule it. Run a single autonomous session at any time:

```bash
./heartbeat.sh
```

Or preview what claude would be told (no actual run):

```bash
./heartbeat.sh --dry-run
```

---

## Guardrails (what stops it from going off the rails)

1. **Pre-flight pytest** — if tests are red before the session starts, the session aborts. The repo has to already be in a known-good state.
2. **Single-task discipline** — the prompt instructs "do exactly ONE task; then stop." No marathon runs.
3. **Auto-revert on red tests** — if the agent's edits break tests, it runs `git restore .` and only commits a `[BLOCKED]` annotation in `TODO.md`.
4. **No eval suite at runtime** — `tests/eval_cases.py` is forbidden in unattended sessions (3+ min, depends on Ollama). Only `pytest -q` runs.
5. **Hard-rule list in CLAUDE.md** — never delete `.env`, never weaken the safety engine, never raise the confidence cap above 0.9, never add cloud-dependent features, never force-push.
6. **Post-flight pytest** — second test run after the agent finishes; surfaces any drift loudly.
7. **Auto-rebase on pull** — `git pull --rebase --autostash` keeps history linear and avoids merge commits when you're working in parallel.

---

## What's in TODO.md right now

Week 2 backlog organized by area:

- **Backend (W2-B1 to W2-B4):** during_transport in API response, `/clarify` endpoint, `/kb` endpoints, snake-bite folk-error detector
- **Frontend (W2-F1 to W2-F5):** transport panel rendering, folk-error banner, multi-turn clarify flow, KB browser modal, local notes via SQLite-WASM
- **Polish (W2-P1 to W2-P3):** offline-font audit, `/healthz` lightweight liveness, module docstrings

Week 3 (Dockerfile, cloud deploy, video, writeup) is listed but **gated** — those need human direction and are not for the autonomous worker.

---

## Logs

- Per-session log: `/tmp/sentinel-harness-YYYYMMDD-HHMM.log`
- Aggregate stdout (launchd): `/tmp/sentinel-harness.out.log`
- Aggregate stderr (launchd): `/tmp/sentinel-harness.err.log`

After a session, `git log --oneline` shows what the worker did.

---

## When to add a new task

Append it to `TODO.md` with:
- A specific, verifiable acceptance criterion (the harness can't grade vibes)
- The files it should touch
- Whether it depends on a previous task (mark `Depends on: W2-Bx`)

Don't add tasks that require browser testing (the agent can't drive a browser) — those stay in the human-driven Week 3 list.

---

## Stopping mid-flight

The heartbeat runs for at most one launchd cycle. If you want to pause work entirely:

```bash
./uninstall.sh
```

If you want to skip tasks, prefix them with `[BLOCKED: <reason>]` in TODO.md and the agent will skip them next session.
