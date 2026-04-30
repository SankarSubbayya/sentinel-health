"""Unit tests for DiagnosisService.

Mocks the LLM call so tests run fast. Verifies orchestration:
- LLM response parsing (plain JSON, code-fenced, malformed)
- escalation_required propagation when LLM itself returns RED
- safety override when LLM is too soft
- error handling
"""

from __future__ import annotations

import pytest

from app.services.diagnosis import DiagnosisService, diagnosis_service


class TestParseLLMResponse:
    def test_plain_json(self):
        raw = '{"differential_diagnosis": [{"condition": "X", "confidence": 0.5, "reasoning": "r", "guideline_reference": "g", "recommendation": "rec"}], "triage_level": "RED", "red_flags_detected": [], "escalation_required": true}'
        parsed = DiagnosisService._parse_llm_response(raw)
        assert parsed["triage_level"] == "RED"
        assert len(parsed["differential_diagnosis"]) == 1

    def test_code_fenced_json(self):
        raw = '```json\n{"triage_level": "YELLOW", "differential_diagnosis": [], "red_flags_detected": [], "escalation_required": false}\n```'
        parsed = DiagnosisService._parse_llm_response(raw)
        assert parsed["triage_level"] == "YELLOW"

    def test_generic_code_fence(self):
        raw = '```\n{"triage_level": "GREEN", "differential_diagnosis": [], "red_flags_detected": [], "escalation_required": false}\n```'
        parsed = DiagnosisService._parse_llm_response(raw)
        assert parsed["triage_level"] == "GREEN"

    def test_malformed_returns_safe_default(self):
        parsed = DiagnosisService._parse_llm_response("not json at all")
        assert parsed["triage_level"] == "YELLOW"
        assert parsed["differential_diagnosis"]
        assert parsed["differential_diagnosis"][0]["condition"] == "Unable to parse response"


@pytest.mark.asyncio
class TestDiagnoseFlow:
    async def test_diagnose_red_flag_input_escalates(
        self, patch_ollama_generate, mock_llm_response_factory
    ):
        """Even if LLM returns YELLOW, a RED flag in the symptoms must
        escalate. Anti-under-diagnosis guarantee."""
        patch_ollama_generate(mock_llm_response_factory(triage="YELLOW"))
        result = await diagnosis_service.diagnose(
            symptoms="chest pain with shortness of breath and sweating",
            patient_context="55-year-old smoker",
        )
        assert result["triage_level"] == "RED"
        assert result["safety"]["escalation_required"] is True

    async def test_diagnose_propagates_red_when_llm_red(
        self, patch_ollama_generate, mock_llm_response_factory
    ):
        """When LLM itself returns RED, escalation_required must be true
        (regression test for the diagnosis.py escalation_required bug)."""
        patch_ollama_generate(
            mock_llm_response_factory(
                triage="RED", primary_condition="DKA", primary_confidence=0.85
            )
        )
        result = await diagnosis_service.diagnose(
            symptoms="severe thirst, fruity breath, vomiting",
            patient_context="type 1 diabetic, missed insulin",
        )
        assert result["triage_level"] == "RED"
        assert result["safety"]["escalation_required"] is True

    async def test_diagnose_benign_input_stays_green(
        self, patch_ollama_generate, mock_llm_response_factory
    ):
        patch_ollama_generate(
            mock_llm_response_factory(
                triage="GREEN", primary_condition="Common Cold", primary_confidence=0.6
            )
        )
        result = await diagnosis_service.diagnose(
            symptoms="mild runny nose and cough", patient_context=""
        )
        assert result["triage_level"] == "GREEN"
        assert result["safety"]["escalation_required"] is False

    async def test_diagnose_propagates_during_transport_on_red(
        self, patch_ollama_generate, mock_llm_response_factory
    ):
        """RED triage with a matching KB condition (ACS for chest pain) must
        attach a non-empty during_transport bridging instruction."""
        patch_ollama_generate(
            mock_llm_response_factory(
                triage="RED",
                primary_condition="Acute Coronary Syndrome",
                primary_confidence=0.85,
            )
        )
        result = await diagnosis_service.diagnose(
            symptoms="chest pain with shortness of breath and sweating",
            patient_context="55-year-old smoker",
        )
        assert result["triage_level"] == "RED"
        assert isinstance(result.get("during_transport"), str)
        assert result["during_transport"].strip()

    async def test_diagnose_attaches_folk_error_correction_on_snake_bite_with_tourniquet(
        self, patch_ollama_generate, mock_llm_response_factory
    ):
        """snake_02 vignette: snake bite + 'tied a rope' must surface the
        condition's folk_error_correction string in the response."""
        patch_ollama_generate(
            mock_llm_response_factory(
                triage="RED",
                primary_condition="Snake Bite Envenomation",
                primary_confidence=0.85,
            )
        )
        result = await diagnosis_service.diagnose(
            symptoms="Snake bit child two hours ago, family tied a rope tightly above the bite, swelling and pain at bite site",
            patient_context="Tourniquet still in place; rural India",
        )
        assert isinstance(result.get("folk_error_correction"), str)
        assert result["folk_error_correction"].strip()
        assert "tourniquet" in result["folk_error_correction"].lower()

    async def test_diagnose_returns_disclaimer(
        self, patch_ollama_generate, mock_llm_response_factory
    ):
        patch_ollama_generate(mock_llm_response_factory())
        result = await diagnosis_service.diagnose(symptoms="some symptoms")
        assert "disclaimer" in result
        assert "triage support" in result["disclaimer"].lower()

    async def test_diagnose_handles_llm_exception(self, monkeypatch):
        from app.core import llm
        from unittest.mock import AsyncMock

        monkeypatch.setattr(
            llm.ollama_client,
            "generate_diagnosis",
            AsyncMock(side_effect=Exception("Ollama is down")),
        )
        result = await diagnosis_service.diagnose(symptoms="some symptoms")
        assert "error" in result
        # On error, default to conservative triage with escalation
        assert result["safety"]["escalation_required"] is True


@pytest.mark.asyncio
class TestTriageFlow:
    """Quick keyword-based triage path (no LLM)."""

    async def test_triage_chest_pain_returns_red(self):
        result = await diagnosis_service.triage("chest pain with shortness of breath")
        assert result["triage_level"] == "RED"
        assert result["escalation_required"] is True

    async def test_triage_cold_returns_green(self):
        result = await diagnosis_service.triage("mild runny nose and sore throat")
        assert result["triage_level"] == "GREEN"
        assert result["escalation_required"] is False

    async def test_triage_includes_recommendation(self):
        result = await diagnosis_service.triage("chest pain")
        assert "recommendation" in result
        assert result["recommendation"]
