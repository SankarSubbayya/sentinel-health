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
