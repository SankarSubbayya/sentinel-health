#!/usr/bin/env bash
# Sentinel Health autonomous worker heartbeat.
# Adapted from pillowtalk — runs one task per invocation with a pytest guardrail.
#
# Usage:
#   ./heartbeat.sh           # one autonomous session
#   ./heartbeat.sh --dry-run # show what claude would be told, don't run it
#
# Logs: /tmp/sentinel-harness-YYYYMMDD-HHMM.log

set -uo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HARNESS_DIR="${REPO_ROOT}/.harness"
LOG_FILE="/tmp/sentinel-harness-$(date +%Y%m%d-%H%M).log"
DRY_RUN="${1:-}"

cd "$REPO_ROOT" || exit 1

log() { echo "[$(date '+%H:%M:%S')] $*" | tee -a "$LOG_FILE"; }

log "=== Sentinel Health harness — session start ==="
log "Repo:    $REPO_ROOT"
log "Branch:  $(git rev-parse --abbrev-ref HEAD)"
log "Commit:  $(git rev-parse --short HEAD)"

# 1. Sync with remote (rebase + autostash so local in-flight edits don't blow up)
log "Syncing with origin..."
git pull --rebase --autostash origin "$(git rev-parse --abbrev-ref HEAD)" 2>&1 | tee -a "$LOG_FILE" || {
  log "git pull failed — aborting session."
  exit 1
}

# 2. Pre-flight: tests must be green before we start. If they're red, the
#    repo is in a bad state — don't make it worse.
log "Pre-flight pytest..."
if ! uv run pytest -q >>"$LOG_FILE" 2>&1; then
  log "Pre-flight tests are RED — refusing to do work in a broken state."
  log "Fix the failing tests manually, then re-enable the harness."
  exit 1
fi
log "Pre-flight tests green."

# 3. Build the prompt and dispatch Claude.
#    Using `read -r -d ''` instead of $(cat <<EOF ...) to avoid bash mis-parsing
#    backticks inside the heredoc.
read -r -d '' PROMPT <<'PROMPT_EOF' || true
You are operating the Sentinel Health autonomous worker.

Read .harness/CLAUDE.md and .harness/TODO.md in this repository.

Then:
1. Pick the FIRST unchecked, non-BLOCKED task in TODO.md.
2. Implement it in as few files as possible. Follow CLAUDE.md hard rules.
3. Run: uv run pytest -q
4. If tests pass:
   - Check off the task in TODO.md (replace "- [ ]" with "- [x]" on that line).
   - Stage only the files you changed.
   - Commit with message format: "harness: <one-line summary>".
   - Push to origin on the current branch.
5. If tests fail:
   - Run: git restore .
   - Add a "[BLOCKED: <reason>]" annotation on that task line in TODO.md.
   - Commit only the TODO.md note.
   - Push.

Do exactly ONE task. Then stop. Do not proceed to a second task.
Do not run tests/eval_cases.py -- too slow and depends on Ollama.
Do not modify .env, force-push, or weaken the safety engine.
Be terse -- avoid unnecessary commentary in your output.
PROMPT_EOF

if [[ "$DRY_RUN" == "--dry-run" ]]; then
  log "=== DRY RUN — prompt that would be sent to claude ==="
  echo "$PROMPT" | tee -a "$LOG_FILE"
  log "=== End of dry run ==="
  exit 0
fi

if ! command -v claude >/dev/null 2>&1; then
  log "claude CLI not found in PATH. Install with: npm i -g @anthropic-ai/claude-code"
  exit 1
fi

log "Dispatching claude (this can take several minutes)..."
log "---"
claude --print --permission-mode bypassPermissions "$PROMPT" 2>&1 | tee -a "$LOG_FILE"
CLAUDE_EXIT=$?
log "---"
log "Claude exited with code $CLAUDE_EXIT"

# 4. Post-flight: verify tests still green. If somehow they're not, surface it loudly.
log "Post-flight pytest..."
if ! uv run pytest -q >>"$LOG_FILE" 2>&1; then
  log "POST-FLIGHT TESTS RED — repo may be in a bad state. Investigate $LOG_FILE."
  exit 2
fi
log "Post-flight tests green."

# 5. Show what changed in the session, for the human.
log "=== Session diff summary ==="
git log --oneline "@{1}.." 2>&1 | tee -a "$LOG_FILE"
log "=== Session end ==="
