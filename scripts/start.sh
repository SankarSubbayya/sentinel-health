#!/usr/bin/env bash
set -euo pipefail

ollama serve &
OLLAMA_PID=$!

until curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; do
  sleep 1
done

# Warm the model into memory so first /diagnose call doesn't pay the load cost.
curl -sf -X POST http://localhost:11434/api/generate \
  -H 'Content-Type: application/json' \
  -d '{"model":"gemma4:e4b-it-q4_K_M","prompt":"ok","stream":false,"keep_alive":"24h"}' \
  >/dev/null || true

exec /app/.venv/bin/uvicorn main:app --host 0.0.0.0 --port "${PORT:-8080}"
