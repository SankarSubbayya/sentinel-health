#!/usr/bin/env bash
# Run the 31-vignette eval against each candidate model and write
# a one-line summary plus the full JSON for each.
#
# Skips models that aren't pulled locally. Per-model timing varies
# from ~2 min (4B Q4) to ~30 min (27B on CPU).
#
# Usage: ./scripts/eval_bakeoff.sh
#        tail -f /tmp/eval_bakeoff.log

set -uo pipefail

LOG=/tmp/eval_bakeoff.log
SUMMARY=/tmp/eval_bakeoff_summary.txt
OUTDIR=tests/bakeoff
mkdir -p "$OUTDIR"

MODELS=(
  "gemma4:e4b-it-q4_K_M"
  "amsaravi/medgemma-4b-it:q8"
  "alibayram/medgemma:4b"
)

echo "=== Bake-off started $(date -u +%FT%TZ) ===" | tee -a "$LOG"
> "$SUMMARY"

# Confirm Ollama is up before starting (cheap check).
if ! curl -sf http://localhost:11434/api/tags >/dev/null; then
  echo "Ollama not running on :11434 — start it first." | tee -a "$LOG"
  exit 1
fi

AVAILABLE=$(curl -sf http://localhost:11434/api/tags | python3 -c "import sys,json; print('\n'.join(m['name'] for m in json.load(sys.stdin).get('models',[])))")

for MODEL in "${MODELS[@]}"; do
  echo "" | tee -a "$LOG"
  echo "── $MODEL ──" | tee -a "$LOG"
  if ! echo "$AVAILABLE" | grep -qx "$MODEL"; then
    echo "  SKIP: not pulled locally" | tee -a "$LOG"
    echo "$MODEL  SKIPPED" >> "$SUMMARY"
    continue
  fi

  START=$(date +%s)
  SLUG=$(echo "$MODEL" | sed 's#[/:]#_#g')
  OUT="$OUTDIR/eval_${SLUG}.txt"

  OLLAMA_MODEL="$MODEL" uv run python -m tests.eval_cases > "$OUT" 2>&1
  RC=$?
  END=$(date +%s)
  ELAPSED=$((END - START))

  # PASS line in eval_cases.py looks like: "PASS: 30/31  (96.8%)"
  PASS_LINE=$(grep -E "^PASS:" "$OUT" | head -1)
  SENS_LINE=$(grep -E "^SENSITIVITY:" "$OUT" | head -1)
  SPEC_LINE=$(grep -E "^SPECIFICITY:" "$OUT" | head -1)

  echo "  $PASS_LINE" | tee -a "$LOG"
  echo "  $SENS_LINE" | tee -a "$LOG"
  echo "  $SPEC_LINE" | tee -a "$LOG"
  echo "  elapsed ${ELAPSED}s  (full output: $OUT)" | tee -a "$LOG"

  printf "%-40s  %s  %s  %s  %ss\n" \
    "$MODEL" "$PASS_LINE" "$SENS_LINE" "$SPEC_LINE" "$ELAPSED" >> "$SUMMARY"

  if [[ $RC -ne 0 ]]; then
    echo "  exit $RC — see $OUT for traceback" | tee -a "$LOG"
  fi
done

echo "" | tee -a "$LOG"
echo "=== Done $(date -u +%FT%TZ) ===" | tee -a "$LOG"
echo "" | tee -a "$LOG"
echo "Summary:" | tee -a "$LOG"
cat "$SUMMARY" | tee -a "$LOG"
