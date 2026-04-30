"""Unit tests for the SafetyEngine.

Verifies the deterministic safety layer: pre-check fires red flags,
post-check overrides under-triaged LLM output, and validate_llm_response
catches malformed payloads.

The clinician principle this enforces: avoid both over-diagnosis AND
under-diagnosis. The safety engine is the anti-under-diagnosis layer.
"""

from __future__ import annotations

import pytest

from app.services.safety import safety_engine


class TestPreCheck:
    def test_no_flags_for_benign_symptoms(self):
        result = safety_engine.pre_check("mild runny nose and sore throat")
        assert result["is_red_flag"] is False
        assert result["escalation_required"] is False
        assert result["urgency"] == "NORMAL"

    def test_flags_for_classic_chest_pain(self):
        result = safety_engine.pre_check(
            "chest pain with shortness of breath and sweating"
        )
        assert result["is_red_flag"] is True
        assert result["escalation_required"] is True
        assert result["urgency"] == "IMMEDIATE"

    def test_flags_for_anginal_pain_history(self):
        result = safety_engine.pre_check(
            "pressure-like chest discomfort, exertional, radiates to jaw"
        )
        assert result["is_red_flag"] is True
        flag_ids = [f["id"] for f in result["flags_detected"]]
        assert "rf_anginal_history" in flag_ids

    def test_flags_for_snake_bite(self):
        result = safety_engine.pre_check("snake bite on ankle, fang marks")
        assert result["is_red_flag"] is True

    def test_flags_for_road_accident(self):
        result = safety_engine.pre_check(
            "patient after road accident with thigh deformity"
        )
        assert result["is_red_flag"] is True

    def test_flags_for_pesticide_ingestion(self):
        result = safety_engine.pre_check(
            "swallowed pesticide one hour ago, drooling, small pupils"
        )
        assert result["is_red_flag"] is True

    def test_flags_for_stroke_signs(self):
        result = safety_engine.pre_check(
            "facial drooping and arm weakness on right side"
        )
        assert result["is_red_flag"] is True


class TestPostCheckOverride:
    """Post-check is the hard rule: a deterministic red flag MUST override
    a too-soft LLM triage. This is the anti-under-diagnosis guarantee."""

    def test_override_yellow_to_red_when_red_flag_present(self):
        result = safety_engine.post_check(
            llm_triage="YELLOW",
            symptoms="chest pain with shortness of breath",
            llm_output={},
        )
        assert result["final_triage"] == "RED"
        assert result["override_applied"] is True
        assert result["override_reason"] is not None

    def test_override_green_to_red_for_anginal_history(self):
        result = safety_engine.post_check(
            llm_triage="GREEN",
            symptoms="pressure-like chest pain on exertion radiating to left arm",
            llm_output={},
        )
        assert result["final_triage"] == "RED"
        assert result["override_applied"] is True

    def test_no_override_when_llm_already_red(self):
        result = safety_engine.post_check(
            llm_triage="RED",
            symptoms="chest pain and shortness of breath",
            llm_output={},
        )
        assert result["final_triage"] == "RED"
        assert result["override_applied"] is False

    def test_no_override_for_benign_symptoms(self):
        result = safety_engine.post_check(
            llm_triage="GREEN",
            symptoms="mild runny nose and sore throat",
            llm_output={},
        )
        assert result["final_triage"] == "GREEN"
        assert result["override_applied"] is False


class TestValidateLLMResponse:
    def test_valid_json_passes(self):
        assert safety_engine.validate_llm_response('{"foo": "bar"}') is True

    def test_invalid_json_fails(self):
        assert safety_engine.validate_llm_response("not json") is False

    def test_partial_json_fails(self):
        assert safety_engine.validate_llm_response('{"foo": "bar"') is False

    def test_whitespace_around_json_passes(self):
        assert safety_engine.validate_llm_response('  {"foo": "bar"}  ') is True
