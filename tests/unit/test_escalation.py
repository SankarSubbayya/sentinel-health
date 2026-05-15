"""Unit tests for the WhatsApp escalation builder.

Verifies: RED-only firing, phone normalisation, URL percent-encoding,
fallback contact-picker URL when no phone is configured.
"""

from __future__ import annotations

from urllib.parse import unquote, urlparse, parse_qs

import pytest

from app.services import escalation as escalation_module
from app.services.escalation import build_whatsapp_escalation


@pytest.fixture(autouse=True)
def _reset_settings():
    """Snapshot and restore settings to avoid cross-test bleed."""
    s = escalation_module.settings
    saved = (
        s.hub_physician_phone,
        s.hub_physician_name,
        s.hub_group_name,
        s.facility_name,
        s.chw_name,
    )
    yield
    (
        s.hub_physician_phone,
        s.hub_physician_name,
        s.hub_group_name,
        s.facility_name,
        s.chw_name,
    ) = saved


def _diag(triage="RED", **extra):
    base = {
        "triage_level": triage,
        "differential_diagnosis": [
            {
                "condition": "Acute MI",
                "confidence": 0.8,
                "reasoning": "Classic anginal pain with diaphoresis.",
                "guideline_reference": "ACC/AHA 2023",
                "recommendation": "Arrange immediate transport; aspirin 325 mg if no allergy.",
            }
        ],
        "safety": {
            "is_red_flag": True,
            "escalation_required": True,
            "escalation_reason": "Cardiac red flag",
        },
        "during_transport": "Aspirin 325 mg; supine; vitals q5min.",
    }
    base.update(extra)
    return base


class TestFiring:
    def test_returns_none_for_green(self):
        assert build_whatsapp_escalation(_diag(triage="GREEN"), "mild cough") is None

    def test_returns_none_for_yellow(self):
        assert build_whatsapp_escalation(_diag(triage="YELLOW"), "fever") is None

    def test_returns_payload_for_red(self):
        payload = build_whatsapp_escalation(_diag(), "chest pain", "55M, diabetic")
        assert payload is not None
        assert payload["recipient_name"]
        assert payload["text"]
        assert payload["wa_me_url"].startswith("https://wa.me/")


class TestMessageContent:
    def test_includes_load_bearing_fields(self):
        payload = build_whatsapp_escalation(
            _diag(), "crushing chest pain radiating to left arm", "55M, diabetic"
        )
        text = payload["text"]
        assert "RED escalation" in text
        assert "Acute MI" in text
        assert "Cardiac red flag" in text
        assert "ACC/AHA 2023" in text
        assert "crushing chest pain" in text
        assert "55M, diabetic" in text
        assert "Aspirin 325 mg" in text
        assert "Decision support only" in text

    def test_session_id_truncated_in_header(self):
        payload = build_whatsapp_escalation(
            _diag(), "chest pain", session_id="abcdef1234567890"
        )
        # 8-char prefix appears in the italicised ref line
        assert "abcdef12" in payload["text"]
        # full 16-char id must NOT appear (truncation enforced)
        assert "abcdef1234567890" not in payload["text"]

    def test_handles_missing_top_diagnosis(self):
        diag = _diag()
        diag["differential_diagnosis"] = []
        payload = build_whatsapp_escalation(diag, "unconscious patient")
        assert payload is not None
        assert "Unknown" in payload["text"]
        assert "Cardiac red flag" in payload["text"]


class TestPhoneAndUrl:
    def test_phone_strips_non_digits(self):
        escalation_module.settings.hub_physician_phone = "+91 98765-43210"
        payload = build_whatsapp_escalation(_diag(), "chest pain")
        parsed = urlparse(payload["wa_me_url"])
        assert parsed.path == "/919876543210"

    def test_no_phone_falls_back_to_contact_picker(self):
        escalation_module.settings.hub_physician_phone = ""
        payload = build_whatsapp_escalation(_diag(), "chest pain")
        parsed = urlparse(payload["wa_me_url"])
        assert parsed.path == "/"
        assert "text" in parse_qs(parsed.query)

    def test_text_query_param_round_trips(self):
        escalation_module.settings.hub_physician_phone = "+1 555 0100"
        payload = build_whatsapp_escalation(_diag(), "chest pain & sweating", "55M")
        parsed = urlparse(payload["wa_me_url"])
        text_param = parse_qs(parsed.query)["text"][0]
        assert unquote(text_param) == payload["text"]
        assert "&" in payload["text"]


class TestClinicalPHCFormat:
    """W3-F6: message body mirrors the real PHC → tertiary group format."""

    def test_message_has_clinical_section_headers(self):
        payload = build_whatsapp_escalation(_diag(), "chest pain", "55M diabetic")
        text = payload["text"]
        assert "*Reason:*" in text
        assert "*H/o:*" in text
        assert "*Patient:*" in text
        assert "*Sentinel reading:*" in text
        assert "*Plan at spoke:*" in text
        assert "*During transport:*" in text

    def test_thrombolysis_section_appears_when_present(self):
        diag = _diag()
        diag["phc_thrombolysis_decision"] = "STEMI eligible. Onset < 12h. No contraindications."
        payload = build_whatsapp_escalation(diag, "chest pain")
        assert "*Thrombolysis decision (for hub):*" in payload["text"]
        assert "STEMI eligible" in payload["text"]

    def test_thrombolysis_section_omitted_when_absent(self):
        payload = build_whatsapp_escalation(_diag(), "chest pain")
        assert "Thrombolysis decision" not in payload["text"]


class TestGroupAndCHWIdentity:
    """W3-F6: HUB_GROUP_NAME + CHW_NAME wiring."""

    def test_recipient_label_uses_group_when_set(self):
        escalation_module.settings.hub_group_name = "TVMCH Cardiology Hub and Spoke"
        escalation_module.settings.hub_physician_name = "Dr. Foo"
        payload = build_whatsapp_escalation(_diag(), "chest pain")
        assert payload["recipient_label"] == "TVMCH Cardiology Hub and Spoke"
        assert payload["group_name"] == "TVMCH Cardiology Hub and Spoke"
        assert "TVMCH Cardiology Hub and Spoke" in payload["text"]

    def test_recipient_label_falls_back_to_physician(self):
        escalation_module.settings.hub_group_name = ""
        escalation_module.settings.hub_physician_name = "Dr. Bar"
        payload = build_whatsapp_escalation(_diag(), "chest pain")
        assert payload["recipient_label"] == "Dr. Bar"
        assert payload["group_name"] is None

    def test_chw_name_appears_in_from_line(self):
        escalation_module.settings.facility_name = "PHC Anaikatti"
        escalation_module.settings.chw_name = "Lakshmi"
        payload = build_whatsapp_escalation(_diag(), "chest pain")
        assert "*From:* PHC Anaikatti · Lakshmi" in payload["text"]

    def test_chw_name_omitted_when_blank(self):
        escalation_module.settings.facility_name = "Spoke clinic"
        escalation_module.settings.chw_name = ""
        payload = build_whatsapp_escalation(_diag(), "chest pain")
        assert "*From:* Spoke clinic" in payload["text"]
        # The middot separator should not appear when no CHW name
        assert " · " not in [
            line for line in payload["text"].split("\n") if line.startswith("*From:*")
        ][0]
