from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.core.llm import ollama_client
from app.services.diagnosis import diagnosis_service

router = APIRouter()


class DiagnoseRequest(BaseModel):
    symptoms: str
    patient_context: Optional[str] = ""
    session_id: Optional[str] = None


class TriageRequest(BaseModel):
    symptoms: str


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

    result = await diagnosis_service.diagnose(request.symptoms, request.patient_context)
    return result


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


@router.get("/")
async def root():
    """API documentation."""
    return {
        "name": "Sentinel Health API",
        "version": "0.1.0",
        "description": "Clinical decision support for community health workers",
        "endpoints": {
            "GET /health": "Check API and Ollama connectivity",
            "POST /api/v1/diagnose": "Generate differential diagnosis from symptoms",
            "POST /api/v1/triage": "Quick RED/YELLOW/GREEN triage",
            "GET /demo": "Interactive demo interface",
        },
        "disclaimer": "This is a decision support tool, not a diagnostic system. Always consult licensed healthcare providers.",
    }
