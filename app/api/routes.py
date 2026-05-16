"""HTTP routes: diagnose, clarify, triage, KB browse, and health checks."""

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from typing import Optional
from app.core.llm import ollama_client
from app.knowledge.loader import kb
from app.services.diagnosis import diagnosis_service
from app.services import reports as reports_service
from app.services.images import validate_image

router = APIRouter()


class DiagnoseRequest(BaseModel):
    symptoms: str
    patient_context: Optional[str] = ""
    session_id: Optional[str] = None
    language: Optional[str] = "en"
    image: Optional[str] = None  # base64-encoded JPEG/PNG (data URL or raw)


class TriageRequest(BaseModel):
    symptoms: str


class ClarifyRequest(BaseModel):
    symptoms: str
    patient_context: Optional[str] = ""
    session_id: Optional[str] = None
    language: Optional[str] = "en"


@router.get("/healthz")
async def healthz():
    """Lightweight liveness check — does not touch Ollama."""
    return {"status": "ok"}


@router.get("/health")
async def health_check():
    """Check API and Ollama health."""
    ollama_health = await ollama_client.health_check()

    if ollama_health.get("status") == "ok":
        return {
            "status": "ok",
            "service": "Sentinel Health API",
            "ollama": "connected",
            "model": ollama_client.model,
        }
    else:
        raise HTTPException(
            status_code=503,
            detail={
                "status": "error",
                "message": "Ollama service not available. Please ensure Ollama is running.",
                "ollama_error": ollama_health.get("message"),
            },
        )


@router.post("/api/v1/diagnose")
async def diagnose(request: DiagnoseRequest):
    """
    Generate differential diagnosis from symptoms.

    Returns:
    - differential_diagnosis: List of top 3 diagnoses with confidence and guidelines
    - triage_level: RED/YELLOW/GREEN
    - safety: Red flags and escalation info
    """
    if not request.symptoms or len(request.symptoms.strip()) < 5:
        raise HTTPException(status_code=400, detail="Symptoms must be at least 5 characters")

    # Fail fast on a malformed image so the CHW sees "Image is truncated"
    # instead of a silent YELLOW from the diagnose() exception fallback.
    if request.image:
        _, _, err = validate_image(request.image)
        if err:
            raise HTTPException(status_code=400, detail=err)

    result = await diagnosis_service.diagnose(
        request.symptoms,
        request.patient_context,
        language=request.language or "en",
        image=request.image,
    )
    return result


@router.post("/api/v1/clarify")
async def clarify(request: ClarifyRequest):
    """
    Generate 1–2 high-yield clarifying questions when the differential is uncertain.

    Returns:
    - questions: list of 1–2 {id, text, rationale} objects
    - session_id: opaque id for the clarification turn
    """
    if not request.symptoms or len(request.symptoms.strip()) < 5:
        raise HTTPException(status_code=400, detail="Symptoms must be at least 5 characters")

    return await diagnosis_service.clarify(
        request.symptoms, request.patient_context, language=request.language or "en"
    )


@router.get("/api/v1/kb/conditions")
async def list_kb_conditions():
    """List KB conditions with summary fields (id, name, category, urgency)."""
    return {
        "conditions": [
            {
                "id": c.get("id"),
                "name": c.get("name"),
                "category": c.get("category"),
                "urgency": c.get("urgency"),
            }
            for c in kb.conditions
        ]
    }


@router.get("/api/v1/kb/conditions/{condition_id}")
async def get_kb_condition(condition_id: str):
    """Return the full KB record for a single condition by id."""
    for c in kb.conditions:
        if c.get("id") == condition_id:
            return c
    raise HTTPException(status_code=404, detail=f"Condition '{condition_id}' not found")


@router.post("/api/v1/triage")
async def triage(request: TriageRequest):
    """
    Quick triage without full diagnosis (RED/YELLOW/GREEN).

    Fast, keyword-based assessment for initial risk stratification.
    """
    if not request.symptoms or len(request.symptoms.strip()) < 5:
        raise HTTPException(status_code=400, detail="Symptoms must be at least 5 characters")

    result = await diagnosis_service.triage(request.symptoms)
    return result


@router.get("/api/v1/reports")
async def list_reports(limit: int = 50):
    """Return the most recent N persisted diagnose reports (newest first)."""
    limit = max(1, min(limit, 500))
    return {"reports": reports_service.list_reports(limit=limit)}


@router.get("/api/v1/reports/{session_id}")
async def get_report(session_id: str):
    """Return one persisted report by session_id, or 404."""
    rec = reports_service.get_report(session_id)
    if rec is None:
        raise HTTPException(status_code=404, detail=f"No report with session_id {session_id!r}")
    return rec


@router.get("/api/v1/reports/{session_id}/image")
async def get_report_image(session_id: str):
    """Serve the persisted image (ECG / wound / etc.) for the report.

    Returns 404 if the report has no image attached or the side-file is missing.
    Content-type is derived from the stored file extension.
    """
    got = reports_service.read_report_image(session_id)
    if got is None:
        raise HTTPException(
            status_code=404,
            detail=f"No image for session_id {session_id!r}",
        )
    image_bytes, mime = got
    return Response(content=image_bytes, media_type=mime)


@router.get("/")
async def root():
    """API documentation."""
    return {
        "name": "Sentinel Health API",
        "version": "0.1.0",
        "description": "Clinical decision support for community health workers",
        "endpoints": {
            "GET /healthz": "Lightweight liveness check (no Ollama)",
            "GET /health": "Check API and Ollama connectivity",
            "POST /api/v1/diagnose": "Generate differential diagnosis from symptoms",
            "POST /api/v1/clarify": "Generate 1–2 clarifying questions for uncertain differentials",
            "POST /api/v1/triage": "Quick RED/YELLOW/GREEN triage",
            "GET /api/v1/kb/conditions": "List KB conditions (id, name, category, urgency)",
            "GET /api/v1/kb/conditions/{id}": "Full KB record for one condition",
            "GET /api/v1/reports": "List persisted diagnose reports (newest first)",
            "GET /api/v1/reports/{session_id}": "Fetch one report by session_id",
            "GET /api/v1/reports/{session_id}/image": "Serve the persisted ECG/wound photo for the report (404 if none)",
            "GET /demo": "Interactive demo interface",
        },
        "disclaimer": "This is a decision support tool, not a diagnostic system. Always consult licensed healthcare providers.",
    }
