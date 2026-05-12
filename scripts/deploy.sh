#!/usr/bin/env bash
# Deploy Sentinel Health to Google Cloud Run with an NVIDIA L4 GPU.
#
# Prereqs (one-time):
#   gcloud auth login
#   gcloud config set project YOUR_PROJECT_ID
#
# Cost note: --min-instances=1 keeps an L4 GPU warm 24/7 (~$0.50/hr ≈ $360/mo).
# For a judge-window-only demo, set min-instances=0 and accept ~60s cold start,
# or scale down between sessions.

set -euo pipefail

PROJECT_ID="${GCP_PROJECT:-$(gcloud config get-value project 2>/dev/null)}"
REGION="${REGION:-us-central1}"
REPO="${REPO:-sentinel}"
SERVICE="${SERVICE:-sentinel-health}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${SERVICE}:latest"

if [[ -z "$PROJECT_ID" ]]; then
  echo "ERROR: no GCP project set. Run: gcloud config set project YOUR_PROJECT_ID" >&2
  exit 1
fi

echo ">> Project: $PROJECT_ID    Region: $REGION    Image: $IMAGE"

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

echo ">> Deploying to Cloud Run with NVIDIA L4 GPU"
gcloud run deploy "$SERVICE" \
  --image "$IMAGE" \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --memory 16Gi \
  --cpu 4 \
  --gpu 1 \
  --gpu-type nvidia-l4 \
  --no-cpu-throttling \
  --max-instances 2 \
  --min-instances 1 \
  --concurrency 4 \
  --timeout 300 \
  --port 8080 \
  --set-env-vars "OLLAMA_BASE_URL=http://localhost:11434,OLLAMA_MODEL=gemma4:e4b-it-q4_K_M,HUB_PHYSICIAN_PHONE=${HUB_PHYSICIAN_PHONE:-},HUB_PHYSICIAN_NAME=${HUB_PHYSICIAN_NAME:-Hub Physician},FACILITY_NAME=${FACILITY_NAME:-Spoke clinic}" \
  --project "$PROJECT_ID"

URL=$(gcloud run services describe "$SERVICE" --region "$REGION" --format='value(status.url)' --project "$PROJECT_ID")
echo ""
echo ">> Deployed: $URL"
echo ">> Demo:     $URL/demo"
echo ">> Health:   $URL/health"
