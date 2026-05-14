"""Unit tests for the W3-F5 clinical-advisor-driven additions.

Maps directly to Hari Subscini's three confusion zones:
  1. ECG / thrombolysis decision  → MI/ACS during-transport contains the
     PHC-level eligibility + contraindication checklist.
  2. Skin lesions  → KB has the priority dermatology conditions and they
     match plausible CHW input.
  3. Unconscious + no history  → rf_unconscious_no_history fires on the
     load-bearing keyword variants in en/hi/ta/ml.
"""

from __future__ import annotations

import pytest

from app.knowledge.loader import kb


class TestSkinLesionConditions:
    @pytest.mark.parametrize(
        "symptoms,expected_id",
        [
            ("Red spreading skin around the wound on lower leg, warm to touch", "cellulitis"),
            ("Painful lump under skin with pus discharging", "cutaneous_abscess"),
            ("Itchy rash, dry scaly skin after handling soap", "eczema_dermatitis"),
            ("Ring shaped rash on the thigh, very itchy", "tinea_fungal"),
            ("Patient stepped on a rusty nail in the field two days ago", "wound_tetanus_prone"),
        ],
    )
    def test_skin_condition_matched(self, symptoms, expected_id):
        matches = kb.get_relevant_conditions(symptoms)
        ids = [c["id"] for c in matches]
        assert expected_id in ids, f"{expected_id} not in {ids} for symptoms: {symptoms!r}"

    def test_cellulitis_has_urgent_urgency(self):
        cellulitis = next(c for c in kb.conditions if c["id"] == "cellulitis")
        assert cellulitis["urgency"] == "URGENT"
        # Spreading-edge-and-pen instruction is the load-bearing clinical advice
        assert "edge" in cellulitis["recommendation"].lower()

    def test_abscess_recommends_incision_and_drainage(self):
        abscess = next(c for c in kb.conditions if c["id"] == "cutaneous_abscess")
        assert "incision" in abscess["recommendation"].lower() or "i&d" in abscess["recommendation"].lower()


class TestThrombolysisDecisionSupport:
    def test_acute_mi_has_thrombolysis_field(self):
        mi = next(c for c in kb.conditions if c["id"] == "acute_mi")
        assert "phc_thrombolysis_decision" in mi, "Hari's thrombolysis checklist is missing"
        text = mi["phc_thrombolysis_decision"].lower()
        # Eligibility must mention STEMI / ST elevation
        assert "stemi" in text or "st elevation" in text
        # Contraindications must mention intracranial bleed
        assert "intracranial" in text or "haemorrhage" in text or "hemorrhage" in text
        # 12-hour window
        assert "12" in text

    def test_acute_mi_recommendation_includes_phc_preliminary_treatment(self):
        """Hari's workflow: venflon + loading doses before transport."""
        mi = next(c for c in kb.conditions if c["id"] == "acute_mi")
        rec = mi["recommendation"].lower()
        assert "aspirin" in rec
        assert "clopidogrel" in rec or "loading" in rec
        assert "venflon" in rec or "iv" in rec


class TestUnconsciousNoHistoryRedFlag:
    @pytest.mark.parametrize(
        "phrase",
        [
            # English
            "Adult man found unconscious by the roadside, no witness",
            "Patient brought in unconscious, no history available",
            "Found collapsed, no one knows what happened",
            "Cannot give history, unresponsive on arrival",
            # Hindi
            "मरीज़ बेहोश मिला, कोई गवाह नहीं",
            # Tamil
            "வயலில் மயக்கமாக கண்டெடுக்கப்பட்டார், சாட்சி இல்லை",
            # Malayalam
            "വയലിൽ ബോധരഹിതനായി കണ്ടെത്തി",
        ],
    )
    def test_fires_on_no_history_variants(self, phrase):
        flags = kb.check_red_flags(phrase)
        flag_ids = {f["id"] for f in flags}
        assert "rf_unconscious_no_history" in flag_ids, (
            f"rf_unconscious_no_history should fire on {phrase!r}; got {flag_ids}"
        )

    def test_does_not_fire_on_witnessed_unconscious_with_history(self):
        """A witnessed seizure with full history shouldn't trip THIS specific flag
        (other altered-consciousness flags may still fire — that's correct)."""
        flags = kb.check_red_flags("Patient had a seizure during meal, family witnessed, postictal now")
        flag_ids = {f["id"] for f in flags}
        assert "rf_unconscious_no_history" not in flag_ids

    def test_red_flag_action_mentions_image_path(self):
        """The action field is the load-bearing instruction — must point CHW
        at the image-led workflow Hari described."""
        from app.knowledge.loader import kb as loader_kb
        flag = next(f for f in loader_kb.red_flags if f["id"] == "rf_unconscious_no_history")
        assert "image" in flag["action"].lower() or "photograph" in flag["action"].lower()
