import json
import uuid
from typing import Dict, Any
from app.core.llm import ollama_client
from app.knowledge.loader import kb
from app.services.safety import safety_engine


_FOLK_ERROR_PHRASES = (
    "tied a rope",
    "tourniquet",
    "applied tourniquet",
    "cut and suck",
    "induced vomiting",
)
_FOLK_ERROR_RED_FLAG_IDS = {"rf_snake_bite", "rf_poisoning", "rf_organophosphate"}


class DiagnosisService:
    """Orchestrate clinical reasoning flow."""

    @staticmethod
    async def diagnose(symptoms: str, patient_context: str = "") -> Dict[str, Any]:
        """Main diagnosis flow."""
        session_id = str(uuid.uuid4())

        try:
            safety_pre = safety_engine.pre_check(symptoms)

            relevant_conditions = kb.get_relevant_conditions(symptoms)

            prompt = ollama_client.build_diagnosis_prompt(
                symptoms, patient_context, relevant_conditions
            )

            llm_response = await ollama_client.generate_diagnosis(prompt)

            parsed = DiagnosisService._parse_llm_response(llm_response)

            safety_post = safety_engine.post_check(
                parsed.get("triage_level", "YELLOW"), symptoms, parsed
            )

            final_triage = safety_post["final_triage"]
            response = {
                "session_id": session_id,
                "differential_diagnosis": parsed.get("differential_diagnosis", []),
                "safety": {
                    "is_red_flag": safety_post["pre_check_flags"]["is_red_flag"],
                    "escalation_required": final_triage == "RED"
                    or safety_post["override_applied"]
                    or safety_post["pre_check_flags"]["escalation_required"],
                    "escalation_reason": safety_post["override_reason"]
                    or (
                        safety_post["pre_check_flags"]["flags_detected"][0].get("name")
                        if safety_post["pre_check_flags"]["flags_detected"]
                        else None
                    ),
                },
                "triage_level": final_triage,
                "disclaimer": "For triage support only. Not a substitute for clinical judgment. Always consult a healthcare provider for final diagnosis and treatment decisions.",
            }

            if final_triage == "RED":
                for cond in relevant_conditions:
                    transport = cond.get("during_transport")
                    if transport:
                        response["during_transport"] = transport
                        break

            symptoms_lower = symptoms.lower()
            if any(p in symptoms_lower for p in _FOLK_ERROR_PHRASES):
                flag_ids = {
                    f.get("id")
                    for f in safety_post["pre_check_flags"].get("flags_detected", [])
                }
                if flag_ids & _FOLK_ERROR_RED_FLAG_IDS:
                    for cond in relevant_conditions:
                        correction = cond.get("folk_error_correction")
                        if correction:
                            response["folk_error_correction"] = correction
                            break

            return response

        except Exception as e:
            return {
                "session_id": session_id,
                "error": str(e),
                "triage_level": "YELLOW",
                "differential_diagnosis": [],
                "safety": {
                    "is_red_flag": True,
                    "escalation_required": True,
                    "escalation_reason": "System error - refer to healthcare provider",
                },
                "disclaimer": "For triage support only. Not a substitute for clinical judgment.",
            }

    @staticmethod
    async def clarify(symptoms: str, patient_context: str = "") -> Dict[str, Any]:
        """Generate 1–2 high-yield clarifying questions for the most likely differential."""
        session_id = str(uuid.uuid4())

        try:
            relevant_conditions = kb.get_relevant_conditions(symptoms)
            prompt = ollama_client.build_clarify_prompt(
                symptoms, patient_context, relevant_conditions
            )
            llm_response = await ollama_client.generate_clarification(prompt)
            parsed = DiagnosisService._parse_llm_response(llm_response)

            questions = parsed.get("questions", [])[:2]
            questions = [
                q for q in questions
                if isinstance(q, dict) and q.get("text", "").strip()
            ]

            return {
                "session_id": session_id,
                "questions": questions,
                "disclaimer": "Clarifying questions are decision support only. Final clinical judgment rests with the licensed provider.",
            }

        except Exception as e:
            return {
                "session_id": session_id,
                "questions": [],
                "error": str(e),
                "disclaimer": "Clarifying questions are decision support only.",
            }

    @staticmethod
    async def triage(symptoms: str) -> Dict[str, Any]:
        """Quick triage without full diagnosis."""
        session_id = str(uuid.uuid4())

        try:
            triage_level = kb.get_triage_level(symptoms)

            safety_pre = safety_engine.pre_check(symptoms)

            if safety_pre["is_red_flag"]:
                triage_level = "RED"
                escalation_reason = safety_pre["flags_detected"][0].get("name")
            else:
                escalation_reason = None

            return {
                "session_id": session_id,
                "triage_level": triage_level,
                "escalation_required": triage_level == "RED",
                "escalation_reason": escalation_reason,
                "recommendation": {
                    "RED": "Immediate hospital/emergency referral",
                    "YELLOW": "Urgent evaluation needed (within 1 hour)",
                    "GREEN": "Non-urgent, can follow up with clinic",
                }.get(triage_level, "Uncertain - recommend medical evaluation"),
                "disclaimer": "This is a triage tool only. For diagnosis and treatment, consult a healthcare provider.",
            }

        except Exception as e:
            return {
                "session_id": session_id,
                "error": str(e),
                "triage_level": "YELLOW",
                "escalation_required": True,
                "escalation_reason": "System error",
                "recommendation": "Please consult a healthcare provider",
            }

    @staticmethod
    def _parse_llm_response(response_text: str) -> Dict[str, Any]:
        """Parse LLM JSON response safely."""
        try:
            json_text = response_text.strip()
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0]
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0]

            parsed = json.loads(json_text)
            return parsed

        except json.JSONDecodeError:
            return {
                "differential_diagnosis": [
                    {
                        "condition": "Unable to parse response",
                        "confidence": 0.0,
                        "reasoning": "LLM response parsing error",
                        "guideline_reference": "N/A",
                        "recommendation": "Please consult healthcare provider",
                    }
                ],
                "triage_level": "YELLOW",
                "red_flags_detected": [],
                "escalation_required": False,
            }


diagnosis_service = DiagnosisService()
