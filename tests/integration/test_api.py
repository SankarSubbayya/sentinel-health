"""Integration tests for the FastAPI surface.

Hits the actual API endpoints via TestClient. The Ollama LLM is mocked so
tests are fast and deterministic — but the rest of the request pipeline
(routing, validation, KB lookup, safety engine) runs for real.
"""

from __future__ import annotations

import base64

import pytest


# Structurally-complete JPEG (SOI + JFIF + 300 bytes padding + EOI).
# Passes W3-F9b's validate_image without being a real image — fine because
# Ollama is mocked in these tests so the bytes are never actually decoded.
_VALID_JPEG_BYTES = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    + bytes(300)
    + b"\xff\xd9"
)
_VALID_JPEG_DATA_URL = "data:image/jpeg;base64," + base64.b64encode(_VALID_JPEG_BYTES).decode()


class TestRootAndHealth:
    def test_root_redirects_to_demo(self, api_client):
        r = api_client.get("/", follow_redirects=False)
        assert r.status_code == 307
        assert r.headers["location"] == "/demo"

    def test_api_index_returns_endpoint_list(self, api_client):
        r = api_client.get("/api")
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

    def test_diagnose_red_attaches_whatsapp_escalation(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
        monkeypatch,
    ):
        """RED triage must produce an `escalation` block with a wa.me URL."""
        from app.services import escalation as esc_mod

        monkeypatch.setattr(esc_mod.settings, "hub_physician_phone", "+91 98765-43210")
        monkeypatch.setattr(esc_mod.settings, "hub_physician_name", "Dr. Hub")
        monkeypatch.setattr(esc_mod.settings, "facility_name", "Test Spoke")

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

        esc = body.get("escalation")
        assert esc, "RED diagnose response must include `escalation`"
        assert esc["recipient_name"] == "Dr. Hub"
        assert esc["phone"] == "+91 98765-43210"
        assert esc["wa_me_url"].startswith("https://wa.me/919876543210?text=")
        assert "Acute Coronary Syndrome" in esc["text"]
        assert "Test Spoke" in esc["text"]
        assert "Decision support only" in esc["text"]

    def test_diagnose_green_omits_escalation(
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
            json={"symptoms": "mild runny nose and cough for two days"},
        )
        assert r.status_code == 200
        assert "escalation" not in r.json()

    def test_diagnose_safety_override_to_red_still_attaches_escalation(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
        monkeypatch,
    ):
        """Even when only the safety layer (not the LLM) escalates to RED,
        the escalation block must still be present — that's the whole point
        of the override path."""
        from app.services import escalation as esc_mod

        monkeypatch.setattr(esc_mod.settings, "hub_physician_phone", "")

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
        esc = body.get("escalation")
        assert esc, "Safety-override RED must still attach escalation"
        # No phone configured → wa.me contact-picker fallback
        assert esc["wa_me_url"].startswith("https://wa.me/?text=")
        assert esc["phone"] is None

    def test_diagnose_accepts_language_param_and_forwards_to_llm(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
        monkeypatch,
    ):
        """A non-English `language` param must (a) be accepted by the API,
        (b) reach the Ollama call as a system-prompt directive, and (c)
        not break safety-override RED on Hindi keyword input."""
        from app.core import llm
        from unittest.mock import AsyncMock

        captured_payloads = []

        async def _capture(prompt, language="en", image=None):
            captured_payloads.append({"prompt": prompt, "language": language})
            return mock_llm_response_factory(
                triage="RED",
                primary_condition="Snake Bite Envenomation",
                primary_confidence=0.85,
            )

        monkeypatch.setattr(
            llm.ollama_client, "generate_diagnosis", AsyncMock(side_effect=_capture)
        )

        # Hindi: "snake bit child two hours ago, fang marks visible"
        r = api_client.post(
            "/api/v1/diagnose",
            json={
                "symptoms": "बच्चे को साँप ने काटा है दो घंटे पहले, दांत के निशान दिख रहे हैं",
                "patient_context": "rural area",
                "language": "hi",
            },
        )
        assert r.status_code == 200
        body = r.json()
        assert body["triage_level"] == "RED"
        assert captured_payloads, "Ollama call was not made"
        assert captured_payloads[0]["language"] == "hi"

    def test_diagnose_accepts_image_and_forwards_to_llm(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
        monkeypatch,
    ):
        """`image` field on the request must reach the Ollama call, and the
        prompt must mention the attached image."""
        from app.core import llm
        from unittest.mock import AsyncMock

        captured = []

        async def _capture(prompt, language="en", image=None):
            captured.append({"prompt": prompt, "language": language, "image": image})
            return mock_llm_response_factory(
                triage="RED",
                primary_condition="Snake Bite Envenomation",
                primary_confidence=0.85,
            )

        monkeypatch.setattr(
            llm.ollama_client, "generate_diagnosis", AsyncMock(side_effect=_capture)
        )

        r = api_client.post(
            "/api/v1/diagnose",
            json={
                "symptoms": "snake bit child on the ankle, fang marks visible",
                "patient_context": "rural area",
                "image": _VALID_JPEG_DATA_URL,
            },
        )
        assert r.status_code == 200
        assert captured, "Ollama call was not made"
        assert captured[0]["image"] == _VALID_JPEG_DATA_URL
        assert "IMAGE IS ATTACHED" in captured[0]["prompt"]

    def test_malformed_image_returns_400_with_useful_detail(
        self,
        api_client,
    ):
        """W3-F9b: bad image fails fast at the API boundary with a clean 400,
        not a silent YELLOW from the diagnose() exception fallback."""
        # The exact base64 from the original bug report — 22-byte JPEG header,
        # no actual image data.
        bad_image = "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAA=="
        r = api_client.post(
            "/api/v1/diagnose",
            json={"symptoms": "chest pain and sweating", "image": bad_image},
        )
        assert r.status_code == 400
        detail = r.json().get("detail", "")
        assert "image" in detail.lower()
        # Should mention truncation or size (which is the actual problem here)
        assert "truncated" in detail.lower() or "too small" in detail.lower()

    def test_truncated_jpeg_returns_400(
        self,
        api_client,
    ):
        import base64
        # 1000 bytes JPEG header with no EOI trailer
        truncated = b"\xff\xd8\xff\xe0" + b"\x00" * 996
        b64 = base64.b64encode(truncated).decode()
        r = api_client.post(
            "/api/v1/diagnose",
            json={
                "symptoms": "chest pain",
                "image": f"data:image/jpeg;base64,{b64}",
            },
        )
        assert r.status_code == 400
        assert "FFD9" in r.json()["detail"] or "truncated" in r.json()["detail"].lower()

    def test_valid_image_still_works(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
        monkeypatch,
    ):
        """Regression: a structurally-valid image must NOT trigger the new 400."""
        import base64
        from app.core import llm
        from unittest.mock import AsyncMock

        monkeypatch.setattr(
            llm.ollama_client,
            "generate_diagnosis",
            AsyncMock(return_value=mock_llm_response_factory(triage="RED")),
        )

        # Structurally complete JPEG: SOI + JFIF + padding + EOI
        valid = (
            b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
            + bytes(300)
            + b"\xff\xd9"
        )
        b64 = base64.b64encode(valid).decode()
        r = api_client.post(
            "/api/v1/diagnose",
            json={
                "symptoms": "chest pain and sweating",
                "image": f"data:image/jpeg;base64,{b64}",
            },
        )
        assert r.status_code == 200

    def test_diagnose_without_image_does_not_mention_image_in_prompt(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
        monkeypatch,
    ):
        from app.core import llm
        from unittest.mock import AsyncMock

        captured = []

        async def _capture(prompt, language="en", image=None):
            captured.append({"prompt": prompt, "image": image})
            return mock_llm_response_factory(triage="GREEN")

        monkeypatch.setattr(
            llm.ollama_client, "generate_diagnosis", AsyncMock(side_effect=_capture)
        )
        r = api_client.post("/api/v1/diagnose", json={"symptoms": "mild cough"})
        assert r.status_code == 200
        assert captured[0]["image"] is None
        assert "IMAGE IS ATTACHED" not in captured[0]["prompt"]

    def test_diagnose_defaults_language_to_english(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
        monkeypatch,
    ):
        """Omitting `language` must default to 'en' (back-compat)."""
        from app.core import llm
        from unittest.mock import AsyncMock

        captured = []

        async def _capture(prompt, language="en", image=None):
            captured.append(language)
            return mock_llm_response_factory(triage="GREEN", primary_condition="Common Cold")

        monkeypatch.setattr(
            llm.ollama_client, "generate_diagnosis", AsyncMock(side_effect=_capture)
        )
        r = api_client.post(
            "/api/v1/diagnose", json={"symptoms": "mild runny nose and cough"}
        )
        assert r.status_code == 200
        assert captured == ["en"]

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


class TestReportsEndpoints:
    @pytest.fixture(autouse=True)
    def _isolate_reports(self, tmp_path, monkeypatch):
        from app.services import reports as reports_module

        p = tmp_path / "reports.jsonl"
        monkeypatch.setattr(reports_module.settings, "reports_path", str(p))
        monkeypatch.setattr(reports_module.settings, "reports_enabled", True)
        yield

    def test_diagnose_persists_a_report(
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
        diag = api_client.post(
            "/api/v1/diagnose",
            json={"symptoms": "55-year-old with crushing chest pain"},
        )
        assert diag.status_code == 200
        session_id = diag.json()["session_id"]

        listed = api_client.get("/api/v1/reports")
        assert listed.status_code == 200
        body = listed.json()
        assert len(body["reports"]) == 1
        rec = body["reports"][0]
        assert rec["session_id"] == session_id
        assert rec["triage_level"] == "RED"
        assert rec["symptoms"] == "55-year-old with crushing chest pain"

    def test_list_reports_newest_first(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
    ):
        patch_ollama_generate(mock_llm_response_factory(triage="GREEN"))
        ids = []
        for sx in ["case one", "case two", "case three"]:
            r = api_client.post("/api/v1/diagnose", json={"symptoms": sx})
            ids.append(r.json()["session_id"])

        body = api_client.get("/api/v1/reports").json()
        assert [r["session_id"] for r in body["reports"]] == list(reversed(ids))

    def test_list_respects_limit_query(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
    ):
        patch_ollama_generate(mock_llm_response_factory(triage="GREEN"))
        for _ in range(5):
            api_client.post("/api/v1/diagnose", json={"symptoms": "mild cough"})
        body = api_client.get("/api/v1/reports?limit=2").json()
        assert len(body["reports"]) == 2

    def test_get_by_session_id(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
    ):
        patch_ollama_generate(mock_llm_response_factory(triage="GREEN"))
        sid = api_client.post(
            "/api/v1/diagnose", json={"symptoms": "mild cough"}
        ).json()["session_id"]

        r = api_client.get(f"/api/v1/reports/{sid}")
        assert r.status_code == 200
        assert r.json()["session_id"] == sid

    def test_get_unknown_returns_404(self, api_client):
        r = api_client.get("/api/v1/reports/no-such-session-id")
        assert r.status_code == 404

    def test_report_records_image_presence_and_side_file(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
    ):
        """W3-F9: image is persisted as a side-file (not inline in JSONL);
        the report record carries the path + byte count; the
        /reports/{sid}/image endpoint serves the bytes back."""
        patch_ollama_generate(mock_llm_response_factory(triage="RED", primary_condition="Snake Bite Envenomation"))
        r = api_client.post(
            "/api/v1/diagnose",
            json={"symptoms": "snake bite, fang marks visible", "image": _VALID_JPEG_DATA_URL},
        )
        assert r.status_code == 200
        sid = r.json()["session_id"]

        listed = api_client.get("/api/v1/reports").json()
        rec = listed["reports"][0]
        assert rec["image_present"] is True
        assert rec["image_path"] is not None
        assert rec["image_path"].startswith("images/")
        assert rec["image_bytes"] == len(_VALID_JPEG_BYTES)

        # Endpoint serves the persisted bytes with correct content-type.
        img_resp = api_client.get(f"/api/v1/reports/{sid}/image")
        assert img_resp.status_code == 200
        assert img_resp.headers["content-type"] == "image/jpeg"
        assert img_resp.content == _VALID_JPEG_BYTES

    def test_image_endpoint_404_when_no_image(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
    ):
        patch_ollama_generate(mock_llm_response_factory(triage="GREEN"))
        r = api_client.post("/api/v1/diagnose", json={"symptoms": "mild cough"})
        sid = r.json()["session_id"]
        img_resp = api_client.get(f"/api/v1/reports/{sid}/image")
        assert img_resp.status_code == 404

    def test_image_endpoint_404_for_unknown_session(self, api_client):
        r = api_client.get("/api/v1/reports/no-such-sid/image")
        assert r.status_code == 404


class TestReportsDisabled:
    def test_diagnose_does_not_persist_when_disabled(
        self,
        api_client,
        patch_ollama_generate,
        mock_llm_response_factory,
        tmp_path,
        monkeypatch,
    ):
        from app.services import reports as reports_module

        p = tmp_path / "reports.jsonl"
        monkeypatch.setattr(reports_module.settings, "reports_path", str(p))
        monkeypatch.setattr(reports_module.settings, "reports_enabled", False)

        patch_ollama_generate(mock_llm_response_factory(triage="GREEN"))
        r = api_client.post("/api/v1/diagnose", json={"symptoms": "mild cough"})
        assert r.status_code == 200
        assert not p.exists()
        listed = api_client.get("/api/v1/reports").json()
        assert listed["reports"] == []


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
