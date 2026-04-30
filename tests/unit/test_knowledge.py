"""Unit tests for the knowledge base loader.

Validates condition matching, red flag detection, and triage keyword logic
against the on-disk JSON KB. No LLM, no network.
"""

from __future__ import annotations

import pytest

from app.knowledge.loader import kb


class TestKBLoading:
    def test_conditions_loaded(self):
        assert len(kb.conditions) >= 15
        ids = {c["id"] for c in kb.conditions}
        for required in [
            "acs",
            "acute_mi",
            "stroke",
            "dka",
            "hypoglycemia",
            "sepsis",
            "anaphylaxis",
            "major_trauma",
            "poisoning",
            "snake_bite",
        ]:
            assert required in ids, f"missing condition: {required}"

    def test_red_flags_loaded(self):
        assert len(kb.red_flags) >= 10
        ids = {f["id"] for f in kb.red_flags}
        for required in [
            "rf_chest_pain_acute",
            "rf_anginal_history",
            "rf_atypical_acs_high_risk",
            "rf_major_trauma",
            "rf_poisoning",
            "rf_organophosphate",
            "rf_snake_bite",
        ]:
            assert required in ids, f"missing red flag: {required}"

    def test_taivade_conditions_have_during_transport(self):
        """TAI-VADE 5 + other RED-eligible conditions must ship a transport
        protocol per PRD §11."""
        required_with_transport = {
            "acs",
            "acute_mi",
            "stroke",
            "major_trauma",
            "poisoning",
            "snake_bite",
            "dka",
            "anaphylaxis",
            "sepsis",
        }
        for c in kb.conditions:
            if c["id"] in required_with_transport:
                assert c.get("during_transport"), (
                    f"{c['id']} is RED-eligible but has no during_transport field"
                )

    def test_snake_bite_has_folk_error_correction(self):
        snake = next(c for c in kb.conditions if c["id"] == "snake_bite")
        assert snake.get("folk_error_correction"), (
            "snake_bite must include folk_error_correction (tourniquet warning)"
        )
        assert "tourniquet" in snake["folk_error_correction"].lower()


class TestRelevantConditions:
    def test_chest_pain_matches_acs(self):
        result = kb.get_relevant_conditions("chest pain and shortness of breath")
        ids = [c["id"] for c in result]
        assert "acs" in ids or "acute_mi" in ids

    def test_fall_from_height_matches_trauma(self):
        result = kb.get_relevant_conditions(
            "fell from height of 3 meters, severe back pain after fall"
        )
        ids = [c["id"] for c in result]
        assert "major_trauma" in ids

    def test_paracetamol_overdose_matches_poisoning(self):
        result = kb.get_relevant_conditions(
            "took 30 paracetamol tablets in self-harm attempt"
        )
        ids = [c["id"] for c in result]
        assert "poisoning" in ids

    def test_snake_bite_with_variant_phrasing_matches(self):
        result = kb.get_relevant_conditions(
            "snake bit child two hours ago, swelling at bite site"
        )
        ids = [c["id"] for c in result]
        assert "snake_bite" in ids

    def test_runny_nose_does_not_match_high_acuity(self):
        result = kb.get_relevant_conditions("runny nose, mild cough, sore throat")
        ids = [c["id"] for c in result]
        for high_acuity in ["acs", "stroke", "major_trauma", "snake_bite"]:
            assert high_acuity not in ids


class TestRedFlagDetection:
    def test_chest_pain_triggers_red_flag(self):
        flags = kb.check_red_flags("chest pain with shortness of breath")
        assert len(flags) > 0
        assert any(f["triage_level"] == "RED" for f in flags)

    def test_anginal_history_triggers_red_flag(self):
        flags = kb.check_red_flags(
            "pressure-like chest discomfort that comes when walking uphill, radiates to jaw"
        )
        assert any(f["id"] == "rf_anginal_history" for f in flags)

    def test_snake_bite_triggers_red_flag(self):
        flags = kb.check_red_flags("snake bite on right ankle 30 minutes ago")
        assert any(f["id"] == "rf_snake_bite" for f in flags)

    def test_organophosphate_triggers_red_flag(self):
        flags = kb.check_red_flags(
            "farmer ingested pesticide, drooling, small pupils"
        )
        assert any(f["id"] == "rf_organophosphate" for f in flags) or any(
            f["id"] == "rf_poisoning" for f in flags
        )

    def test_road_accident_triggers_trauma_red_flag(self):
        flags = kb.check_red_flags(
            "patient brought after road accident, chest pain and thigh deformity"
        )
        assert any(f["id"] == "rf_major_trauma" for f in flags)

    def test_facial_drooping_triggers_red_flag(self):
        flags = kb.check_red_flags(
            "sudden facial drooping on right side and slurred speech"
        )
        assert any(f["id"] == "rf_facial_drooping" for f in flags)

    def test_runny_nose_does_not_trigger_red_flag(self):
        flags = kb.check_red_flags("mild runny nose and sore throat")
        assert len(flags) == 0


class TestTriageLevel:
    @pytest.mark.parametrize(
        "symptoms,expected",
        [
            ("mild runny nose and cough", "GREEN"),
            ("severe headache with confusion", "RED"),
            ("moderate fever and dehydration", "YELLOW"),
            ("unconscious and unresponsive", "RED"),
        ],
    )
    def test_triage_level_classification(self, symptoms, expected):
        assert kb.get_triage_level(symptoms) == expected
