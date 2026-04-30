#!/usr/bin/env bash
# Burn through the TODO.md backlog as fast as possible.
# Runs heartbeat.sh back-to-back until no unblocked tasks remain or a session fails.
#
# Usage:
#   ./run_all.sh                 # foreground (good for tail -f)
#   nohup ./run_all.sh &         # background (logs to /tmp/sentinel-burndown.log)
#   MAX_ITERATIONS=20 ./run_all.sh
#
# Safety:
# - Stops if any heartbeat session exits non-zero (tests broken, claude failure)
# - Caps at MAX_ITERATIONS even if the TODO never empties (default 20)
# - Refuses to start if launchd timer is loaded (would cause conflicts)

set -uo pipefail

HARNESS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HEARTBEAT="${HARNESS_DIR}/heartbeat.sh"
TODO="${HARNESS_DIR}/TODO.md"

MAX_ITERATIONS="${MAX_ITERATIONS:-20}"

# --- Sanity: don't run in parallel with the launchd timer ---
if launchctl list 2>/dev/null | grep -q "com.sankar.sentinelhealth.harness"; then
  echo "⚠ launchd timer is currently loaded — would cause conflicts."
  echo "  Run: $HARNESS_DIR/uninstall.sh"
  echo "  Then re-run this script."
  exit 1
fi

count_unblocked() {
  grep -E "^- \[ \] " "$TODO" 2>/dev/null | grep -v "\[BLOCKED" | wc -l | tr -d ' '
}
count_blocked() {
  grep -E "^- \[ \] \[BLOCKED" "$TODO" 2>/dev/null | wc -l | tr -d ' '
}
count_done() {
  grep -E "^- \[x\]" "$TODO" 2>/dev/null | wc -l | tr -d ' '
}

start=$(date +%s)
iteration=0

echo "════════════════════════════════════════════════════════════"
echo "  Sentinel Health — burn-down mode"
echo "  Initial:  $(count_unblocked) unblocked  ·  $(count_blocked) blocked  ·  $(count_done) done"
echo "  Cap:      $MAX_ITERATIONS iterations"
echo "════════════════════════════════════════════════════════════"

while (( iteration < MAX_ITERATIONS )); do
  iteration=$((iteration + 1))
  remaining=$(count_unblocked)

  if (( remaining == 0 )); then
    echo ""
    echo "✓ No unblocked tasks remain. Burn-down complete."
    break
  fi

  echo ""
  echo "──────────────────────────────────────────────────────────"
  echo "  Iteration $iteration · $remaining unblocked task(s) left"
  echo "──────────────────────────────────────────────────────────"

  if ! "$HEARTBEAT"; then
    echo ""
    echo "✗ heartbeat exited non-zero — pausing burn-down."
    echo "  Last log: $(ls -t /tmp/sentinel-harness-*.log | head -1)"
    break
  fi

  # Tiny breather to let git settle and avoid hammering claude back-to-back
  sleep 5
done

elapsed=$(( $(date +%s) - start ))
mins=$((elapsed / 60))
secs=$((elapsed % 60))

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Burn-down summary"
echo "  Sessions run:  $iteration"
echo "  Wall time:     ${mins}m ${secs}s"
echo "  Done:          $(count_done)"
echo "  Unblocked:     $(count_unblocked)"
echo "  Blocked:       $(count_blocked)"
echo "════════════════════════════════════════════════════════════"

if (( $(count_blocked) > 0 )); then
  echo ""
  echo "Blocked tasks (need human review):"
  grep -E "^- \[ \] \[BLOCKED" "$TODO"
fi
