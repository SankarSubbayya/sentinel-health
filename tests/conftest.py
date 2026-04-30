"""Shared pytest fixtures.

The tests do NOT call real Ollama. The LLM client is mocked so the suite
runs fast and deterministic in CI.
"""

from __future__ import annotations

import json
from typing import Any
from unittest.mock import AsyncMock

import pytest


def make_llm_response(
    *,
    triage: str = "YELLOW",
    primary_condition: str = "Acute Coronary Syndrome",
    primary_confidence: float = 0.7,
    extra_differentials: list[dict] | None = None,
    red_flags: list[str] | None = None,
    escalation_required: bool | None = None,
) -> str:
    """Build a JSON string matching DIAGNOSIS_SCHEMA, suitable as
    OllamaClient.generate_diagnosis return value."""
    if escalation_required is None:
        escalation_required = triage == "RED"
    differentials = [
        {
            "condition": primary_condition,
            "confidence": primary_confidence,
            "reasoning": "Clinical features match.",
            "guideline_reference": "Test Guideline",
            "recommendation": "Refer to hospital.",
        }
    ]
    if extra_differentials:
        differentials.extend(extra_differentials)
    return json.dumps(
        {
            "differential_diagnosis": differentials,
            "triage_level": triage,
            "red_flags_detected": red_flags or [],
            "escalation_required": escalation_required,
            "escalation_reason": "Test escalation reason" if escalation_required else "",
        }
    )


@pytest.fixture
def mock_llm_response_factory():
    """Returns the make_llm_response helper for parameterized tests."""
    return make_llm_response


@pytest.fixture
def patch_ollama_generate(monkeypatch):
    """Patch ollama_client.generate_diagnosis to return canned strings.

    Usage:
        async def test_x(patch_ollama_generate):
            patch_ollama_generate(make_llm_response(triage="RED"))
            ...
    """
    from app.core import llm

    def _patch(response_text: str) -> AsyncMock:
        mock = AsyncMock(return_value=response_text)
        monkeypatch.setattr(llm.ollama_client, "generate_diagnosis", mock)
        return mock

    return _patch


@pytest.fixture
def patch_ollama_health(monkeypatch):
    """Patch ollama_client.health_check to return canned dicts."""
    from app.core import llm

    def _patch(status: str = "ok", model_available: bool = True) -> AsyncMock:
        mock = AsyncMock(
            return_value={
                "status": status,
                "model_available": model_available,
                "models": [llm.ollama_client.model] if model_available else [],
            }
        )
        monkeypatch.setattr(llm.ollama_client, "health_check", mock)
        return mock

    return _patch


@pytest.fixture
def api_client():
    """FastAPI TestClient bound to main:app."""
    from fastapi.testclient import TestClient
    from main import app

    return TestClient(app)
