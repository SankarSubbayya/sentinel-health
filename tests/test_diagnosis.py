import pytest
from app.knowledge.loader import kb
from app.services.safety import safety_engine
from app.services.diagnosis import DiagnosisService


def test_knowledge_base_loads():
    """Test that knowledge base loads correctly."""
    assert len(kb.conditions) > 0
    assert len(kb.red_flags) > 0
    assert kb.triage_rules is not None


def test_get_relevant_conditions():
    """Test condition matching."""
    symptoms = "chest pain and shortness of breath"
    relevant = kb.get_relevant_conditions(symptoms)

    assert len(relevant) > 0
    assert any("coronary" in c.get("name", "").lower() or
               "cardiac" in c.get("name", "").lower() or
               "acs" in c.get("id", "").lower()
               for c in relevant)


def test_check_red_flags():
    """Test red flag detection."""
    symptoms = "chest pain with shortness of breath"
    flags = kb.check_red_flags(symptoms)

    assert len(flags) > 0


def test_red_flag_detection_severe():
    """Test that severe symptoms trigger red flags."""
    symptoms = "unconscious and unresponsive"
    flags = kb.check_red_flags(symptoms)

    assert len(flags) > 0
    assert any(flag.get("triage_level") == "RED" for flag in flags)


def test_triage_non_urgent():
    """Test green triage for non-urgent symptoms."""
    symptoms = "mild runny nose and cough"
    triage = kb.get_triage_level(symptoms)

    assert triage == "GREEN"


def test_safety_engine_pre_check():
    """Test safety pre-check layer."""
    symptoms = "chest pain with shortness of breath"
    result = safety_engine.pre_check(symptoms)

    assert result["is_red_flag"] is True
    assert result["escalation_required"] is True


def test_llm_response_parsing():
    """Test JSON response parsing."""
    mock_response = """{
        "differential_diagnosis": [
            {
                "condition": "Test Condition",
                "confidence": 0.8,
                "reasoning": "test",
                "guideline_reference": "test",
                "recommendation": "test"
            }
        ],
        "triage_level": "RED",
        "red_flags_detected": [],
        "escalation_required": true
    }"""

    parsed = DiagnosisService._parse_llm_response(mock_response)

    assert parsed is not None
    assert "differential_diagnosis" in parsed
    assert len(parsed["differential_diagnosis"]) > 0


def test_llm_response_parsing_with_code_blocks():
    """Test parsing of code-block wrapped JSON."""
    mock_response = """```json
    {
        "differential_diagnosis": [],
        "triage_level": "YELLOW",
        "red_flags_detected": [],
        "escalation_required": false
    }
    ```"""

    parsed = DiagnosisService._parse_llm_response(mock_response)

    assert parsed is not None
    assert parsed["triage_level"] == "YELLOW"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
