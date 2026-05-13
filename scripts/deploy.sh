#!/usr/bin/env bash
# Deploy Sentinel Health to Google Cloud Run.
#
# Usage:
#   ./scripts/deploy.sh              # GPU mode (nvidia-l4) — needs L4 quota
#   ./scripts/deploy.sh --cpu        # CPU-only mode — no quota request needed
#
# Prereqs (one-time):
#   gcloud auth login
#   gcloud config set project YOUR_PROJECT_ID
#
# Cost notes:
#   GPU mode: --min-instances=1 keeps an L4 warm 24/7 (~$0.71/hr ≈ $500/mo
#             list, ~$140 for a 7-day demo). Sub-second diagnose latency.
#   CPU mode: no GPU bill. ~8 vCPU / 16 GiB instance ≈ $0.20/hr (~$35 for
#             a 7-day demo). Diagnose latency rises from ~3s to ~15-30s
#             but the demo is functionally identical.

set -euo pipefail

MODE="gpu"
for arg in "$@"; do
  case "$arg" in
    --cpu) MODE="cpu" ;;
    --gpu) MODE="gpu" ;;
    -h|--help)
      sed -n '2,16p' "$0"
      exit 0
      ;;
    *)
      echo "ERROR: unknown argument: $arg" >&2
      echo "Run with -h for usage." >&2
      exit 1
      ;;
  esac
done

PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-us-central1}"
REPO="${REPO:-sentinel}"
SERVICE="${SERVICE:-sentinel-health}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"

if [[ -z "$PROJECT_ID" ]]; then
  echo "ERROR: no GCP project set. Run: gcloud config set project YOUR_PROJECT_ID" >&2
  exit 1
fi

echo ">> Project: $PROJECT_ID    Region: $REGION    Mode: $MODE    Image: $IMAGE"

echo ">> Enabling required services (idempotent)"
gcloud services enable \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  --project "$PROJECT_ID"

echo ">> Ensuring Artifact Registry repo exists"
gcloud artifacts repositories describe "$REPO" --location="$REGION" --project "$PROJECT_ID" >/dev/null 2>&1 || \
  gcloud artifacts repositories create "$REPO" \
    --repository-format=docker \
    --location="$REGION" \
    --description="Sentinel Health images" \
    --project "$PROJECT_ID"

echo ">> Building image with Cloud Build (model bake makes this ~10–15 min)"
gcloud builds submit \
  --tag "$IMAGE" \
  --machine-type=e2-highcpu-32 \
  --timeout=30m \
  --project "$PROJECT_ID"

ENV_VARS="OLLAMA_BASE_URL=http://localhost:11434,OLLAMA_MODEL=gemma4:e4b-it-q4_K_M,HUB_PHYSICIAN_PHONE=${HUB_PHYSICIAN_PHONE:-},HUB_PHYSICIAN_NAME=${HUB_PHYSICIAN_NAME:-Hub Physician},FACILITY_NAME=${FACILITY_NAME:-Spoke clinic}"

DEPLOY_ARGS=(
  --image "$IMAGE"
  --region "$REGION"
  --platform managed
  --allow-unauthenticated
  --no-cpu-throttling
  --max-instances 2
  --min-instances 1
  --port 8080
  --set-env-vars "$ENV_VARS"
  --project "$PROJECT_ID"
)

if [[ "$MODE" == "gpu" ]]; then
  echo ">> Deploying to Cloud Run with NVIDIA L4 GPU"
  DEPLOY_ARGS+=(
    --memory 16Gi
    --cpu 4
    --gpu 1
    --gpu-type nvidia-l4
    --concurrency 4
    --timeout 300
  )
else
  echo ">> Deploying to Cloud Run on CPU only (no GPU)"
  DEPLOY_ARGS+=(
    --memory 16Gi
    --cpu 8
    --concurrency 2
    --timeout 600
  )
fi

gcloud run deploy "$SERVICE" "${DEPLOY_ARGS[@]}"

URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)' --project "$PROJECT_ID")
echo ""
echo ">> Deployed:  $URL"
echo ">> Demo:      $URL/demo"
echo ">> Health:    $URL/health"
echo ">> Mode:      $MODE"
if [[ "$MODE" == "cpu" ]]; then
  echo ">> Note:      First diagnose call may take 30-60s while the model loads;"
  echo ">>            subsequent calls ~15-30s. Redeploy with no args to use GPU"
  echo ">>            once your L4 quota is granted."
fi
