"""Red-flag safety engine that can override soft LLM triage to RED."""

from typing import Dict, List, Any
from app.knowledge.loader import kb


class SafetyEngine:
    """Two-layer safety system: pre-check and post-check for LLM output."""

    @staticmethod
    def pre_check(symptoms: str) -> Dict[str, Any]:
        """Fast, non-LLM red flag screening (Layer 1)."""
        red_flags = kb.check_red_flags(symptoms)

        return {
            "is_red_flag": len(red_flags) > 0,
            "flags_detected": red_flags,
            "escalation_required": len(red_flags) > 0,
            "urgency": red_flags[0].get("urgency", "UNKNOWN") if red_flags else "NORMAL",
        }

    @staticmethod
    def post_check(
        llm_triage: str, symptoms: str, llm_output: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Override LLM triage if safety layer detects RED (Layer 2)."""
        pre_check_result = SafetyEngine.pre_check(symptoms)

        if pre_check_result["is_red_flag"] and llm_triage != "RED":
            override_triage = "RED"
            override_reason = f"Safety override: {pre_check_result['flags_detected'][0].get('name', 'Red flag detected')}"
        else:
            override_triage = llm_triage
            override_reason = None

        return {
            "original_triage": llm_triage,
            "final_triage": override_triage,
            "override_applied": override_reason is not None,
            "override_reason": override_reason,
            "pre_check_flags": pre_check_result,
        }

    @staticmethod
    def validate_llm_response(response_text: str) -> bool:
        """Basic validation that LLM response is valid JSON-like."""
        response_text = response_text.strip()
        return response_text.startswith("{") and response_text.endswith("}")


safety_engine = SafetyEngine()
