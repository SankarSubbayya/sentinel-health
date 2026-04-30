"""Integration tests for the FastAPI surface.

Hits the actual API endpoints via TestClient. The Ollama LLM is mocked so
tests are fast and deterministic — but the rest of the request pipeline
(routing, validation, KB lookup, safety engine) runs for real.
"""

from __future__ import annotations

import pytest


class TestRootAndHealth:
    def test_root_returns_api_info(self, api_client):
        r = api_client.get("/")
        assert r.status_code == 200
        body = r.json()
        assert body["name"] == "Sentinel Health API"
        assert "endpoints" in body
        assert "disclaimer" in body

    def test_health_when_ollama_up(self, api_client, patch_ollama_health):
        patch_ollama_health(status="ok", model_available=True)
        r = api_client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "ok"
        assert body["ollama"] == "connected"

    def test_health_when_ollama_down(self, api_client, patch_ollama_health):
        patch_ollama_health(status="error", model_available=False)
        r = api_client.get("/health")
        assert r.status_code == 503

    def test_healthz_returns_ok_even_when_ollama_down(
        self, api_client, monkeypatch
    ):
        from unittest.mock import AsyncMock
        from app.core import llm

        monkeypatch.setattr(
            llm.ollama_client,
            "health_check",
            AsyncMock(side_effect=RuntimeError("ollama unreachable")),
        )
        r = api_client.get("/healthz")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}

    def test_demo_page_served(self, api_client):
        r = api_client.get("/demo")
        # Either the HTML loads, or the file-not-found JSON branch runs
        assert r.status_code == 200


class TestDiagnoseEndpoint:
    def test_diagnose_red_input_returns_red(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
    ):
        patch_ollama_generate(
            mock_llm_response_factory(
                triage="RED",
                primary_condition="Acute Coronary Syndrome",
                primary_confidence=0.8,
            )
        )
        r = api_client.post(
            "/api/v1/diagnose",
            json={
                "symptoms": "55-year-old man with crushing chest pain, sweating, shortness of breath",
                "patient_context": "Hypertension, smoker",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["triage_level"] == "RED"
        assert body["safety"]["escalation_required"] is True
        assert body["differential_diagnosis"]
        assert "disclaimer" in body

    def test_diagnose_green_input_returns_green(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
    ):
        patch_ollama_generate(
            mock_llm_response_factory(
                triage="GREEN",
                primary_condition="Common Cold",
                primary_confidence=0.6,
            )
        )
        r = api_client.post(
            "/api/v1/diagnose",
            json={
                "symptoms": "mild runny nose and cough for two days",
                "patient_context": "",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["triage_level"] == "GREEN"
        assert body["safety"]["escalation_required"] is False

    def test_diagnose_safety_overrides_soft_llm(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
    ):
        """LLM says YELLOW, but red flag rule fires → final must be RED."""
        patch_ollama_generate(mock_llm_response_factory(triage="YELLOW"))
        r = api_client.post(
            "/api/v1/diagnose",
            json={
                "symptoms": "snake bite on right ankle, fang marks visible",
                "patient_context": "rural area",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["triage_level"] == "RED"
        assert body["safety"]["escalation_required"] is True

    def test_diagnose_rejects_too_short_symptoms(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
    ):
        patch_ollama_generate(mock_llm_response_factory())
        r = api_client.post("/api/v1/diagnose", json={"symptoms": "abc"})
        assert r.status_code == 400

    def test_diagnose_validation_error_on_missing_field(self, api_client):
        r = api_client.post("/api/v1/diagnose", json={})
        assert r.status_code == 422


class TestClarifyEndpoint:
    def test_clarify_returns_one_or_two_nonempty_questions(
        self, api_client, monkeypatch
    ):
        from unittest.mock import AsyncMock
        from app.core import llm

        canned = (
            '{"questions": ['
            '{"id": "q1", "text": "Did the chest pain radiate to the left arm or jaw?",'
            ' "rationale": "Distinguishes ACS from musculoskeletal pain"},'
            '{"id": "q2", "text": "Was the patient sweating during the episode?",'
            ' "rationale": "Diaphoresis raises ACS likelihood"}'
            "]}"
        )
        monkeypatch.setattr(
            llm.ollama_client, "generate_clarification", AsyncMock(return_value=canned)
        )

        r = api_client.post(
            "/api/v1/clarify",
            json={"symptoms": "chest discomfort for 30 minutes, otherwise unsure"},
        )
        assert r.status_code == 200
        body = r.json()
        assert "session_id" in body
        assert 1 <= len(body["questions"]) <= 2
        for q in body["questions"]:
            assert q["text"].strip()
            assert "id" in q
            assert "rationale" in q

    def test_clarify_rejects_too_short(self, api_client):
        r = api_client.post("/api/v1/clarify", json={"symptoms": "x"})
        assert r.status_code == 400


class TestTriageEndpoint:
    def test_triage_red_for_chest_pain(self, api_client):
        r = api_client.post(
            "/api/v1/triage",
            json={"symptoms": "chest pain with shortness of breath and sweating"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body["triage_level"] == "RED"
        assert body["escalation_required"] is True
        assert "Immediate" in body["recommendation"] or "hospital" in body["recommendation"]

    def test_triage_red_for_snake_bite(self, api_client):
        r = api_client.post(
            "/api/v1/triage", json={"symptoms": "snake bite, fang marks on ankle"}
        )
        assert r.status_code == 200
        body = r.json()
        assert body["triage_level"] == "RED"

    def test_triage_green_for_runny_nose(self, api_client):
        r = api_client.post(
            "/api/v1/triage", json={"symptoms": "mild runny nose and sore throat"}
        )
        assert r.status_code == 200
        body = r.json()
        assert body["triage_level"] == "GREEN"
        assert body["escalation_required"] is False

    def test_triage_rejects_too_short(self, api_client):
        r = api_client.post("/api/v1/triage", json={"symptoms": "x"})
        assert r.status_code == 400


class TestKBEndpoints:
    def test_list_conditions_returns_summary_fields(self, api_client):
        r = api_client.get("/api/v1/kb/conditions")
        assert r.status_code == 200
        body = r.json()
        assert "conditions" in body
        assert len(body["conditions"]) >= 18
        ids = {c["id"] for c in body["conditions"]}
        assert "snake_bite" in ids
        assert "acs" in ids
        # Summary fields only — must NOT leak full record
        for c in body["conditions"]:
            assert set(c.keys()) == {"id", "name", "category", "urgency"}

    def test_get_condition_detail_exposes_folk_error_correction(self, api_client):
        r = api_client.get("/api/v1/kb/conditions/snake_bite")
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == "snake_bite"
        assert "folk_error_correction" in body
        assert body["folk_error_correction"].strip()
        assert "DO NOT" in body["folk_error_correction"]

    def test_get_condition_unknown_returns_404(self, api_client):
        r = api_client.get("/api/v1/kb/conditions/not_a_real_condition")
        assert r.status_code == 404
