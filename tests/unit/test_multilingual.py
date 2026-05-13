"""Unit tests for multilingual keyword matching in the KB loader.

Verifies that red flags and condition lookups fire on Hindi, Tamil, and
Malayalam phrasings (not just English). The safety layer is load-bearing,
so this exercises the cross-language path that catches a CHW dictating
in their own language.
"""

from __future__ import annotations

import pytest

from app.knowledge.loader import kb


class TestMultilingualRedFlags:
    @pytest.mark.parametrize(
        "phrase,expected_flag_id",
        [
            # Hindi
            ("मरीज़ को सीने में दर्द है", "rf_chest_pain_acute"),
            ("मरीज़ बेहोश है", "rf_altered_consciousness"),
            ("किसान ने ज़हर खा लिया", "rf_poisoning"),
            ("साँप ने काटा है", "rf_snake_bite"),
            ("चेहरा लटक गया", "rf_facial_drooping"),
            ("मिर्गी का दौरा पड़ा", "rf_seizure"),
            ("दुर्घटना हुई है", "rf_major_trauma"),
            # Tamil
            ("நோயாளிக்கு மார்பு வலி", "rf_chest_pain_acute"),
            ("விஷம் குடித்தார்", "rf_poisoning"),
            ("பாம்பு கடித்தது", "rf_snake_bite"),
            ("முகம் தொங்குகிறது", "rf_facial_drooping"),
            ("வலிப்பு வந்தது", "rf_seizure"),
            # Malayalam
            ("രോഗിക്ക് നെഞ്ച് വേദന", "rf_chest_pain_acute"),
            ("വിഷം കുടിച്ചു", "rf_poisoning"),
            ("പാമ്പ് കടിച്ചു", "rf_snake_bite"),
            ("മുഖം കോടി", "rf_facial_drooping"),
            ("അപകടം ഉണ്ടായി", "rf_major_trauma"),
        ],
    )
    def test_red_flag_fires_on_non_english_phrase(self, phrase, expected_flag_id):
        flags = kb.check_red_flags(phrase)
        flag_ids = {f["id"] for f in flags}
        assert expected_flag_id in flag_ids, (
            f"Expected {expected_flag_id} to fire on {phrase!r}; got {flag_ids}"
        )

    def test_english_keywords_still_work(self):
        """Adding multilingual variants must not regress English matching."""
        flags = kb.check_red_flags("severe chest pain and sweating")
        assert any(f["id"] == "rf_chest_pain_acute" for f in flags)

    def test_no_false_positive_on_benign_non_english(self):
        """A benign Hindi sentence should not fire any red flag."""
        flags = kb.check_red_flags("मरीज़ को हल्की खांसी है")  # mild cough
        assert flags == []


class TestMultilingualConditionLookup:
    def test_forward_compatible_symptoms_local(self):
        """If a condition has `symptoms_local`, the loader must scan it.

        We synthesize a condition with `symptoms_local` and verify match.
        (No production condition has translations yet; loader is forward-
        compatible per W3-F1.)
        """
        original = kb.conditions
        try:
            kb.conditions = [
                {
                    "id": "test_condition",
                    "name": "Test Condition",
                    "symptoms": [],
                    "symptoms_local": {
                        "hi": ["परीक्षण लक्षण"],
                        "ta": ["சோதனை அறிகுறி"],
                        "ml": ["പരീക്ഷണ ലക്ഷണം"],
                    },
                }
            ]
            assert kb.get_relevant_conditions("रोगी को परीक्षण लक्षण है")[0]["id"] == "test_condition"
            assert kb.get_relevant_conditions("சோதனை அறிகுறி உள்ளது")[0]["id"] == "test_condition"
            assert kb.get_relevant_conditions("പരീക്ഷണ ലക്ഷണം കാണുന്നു")[0]["id"] == "test_condition"
        finally:
            kb.conditions = original
