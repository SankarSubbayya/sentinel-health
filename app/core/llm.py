import json
import httpx
from typing import Any
from app.core.config import settings


DIAGNOSIS_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "differential_diagnosis": {
            "type": "array",
            "minItems": 1,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "condition": {"type": "string"},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 0.9},
                    "reasoning": {"type": "string"},
                    "guideline_reference": {"type": "string"},
                    "recommendation": {"type": "string"},
                },
                "required": [
                    "condition",
                    "confidence",
                    "reasoning",
                    "guideline_reference",
                    "recommendation",
                ],
            },
        },
        "triage_level": {"type": "string", "enum": ["RED", "YELLOW", "GREEN"]},
        "red_flags_detected": {"type": "array", "items": {"type": "string"}},
        "escalation_required": {"type": "boolean"},
        "escalation_reason": {"type": "string"},
    },
    "required": [
        "differential_diagnosis",
        "triage_level",
        "red_flags_detected",
        "escalation_required",
    ],
}


SYSTEM_PROMPT = """You are Sentinel Health, a clinical decision support tool for community health workers in low-resource settings. You provide triage guidance and differential diagnoses, NOT definitive diagnoses. Be confirmatory, not informational — lead with action, not menus of possibilities.

Rules:
- Reason ONLY from the candidate conditions provided to you. NEVER invent or guess conditions that are not in the candidate list.
- If the candidate list is empty or none of the candidates plausibly fit the symptoms, return EXACTLY:
    differential_diagnosis: [{"condition": "No acute condition identified", "confidence": 0.5, "reasoning": "Symptoms do not match any condition in the local knowledge base. This is likely benign or out of scope.", "guideline_reference": "N/A — refer to clinician if concern persists", "recommendation": "Observe and follow up. Refer to a clinician if symptoms worsen or new symptoms develop."}]
  with triage_level "GREEN" and escalation_required false. Do NOT invent a condition like "MI" or "Stroke" to fill the slot.
- Cap confidence at 0.9 — never claim certainty.
- triage_level is RED for life-threatening, YELLOW for urgent, GREEN for non-urgent.
- escalation_required must be true for any RED triage.
- Always recommend physician confirmation in your recommendation field.
- Output must conform exactly to the requested JSON schema."""


class OllamaClient:
    def __init__(self, base_url: str | None = None, model: str | None = None):
        self.base_url = base_url or settings.ollama_base_url
        self.model = model or settings.ollama_model
        self.timeout = settings.ollama_timeout_seconds
        self.temperature = settings.ollama_temperature

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.base_url}/api/tags")
                if response.status_code == 200:
                    tags = response.json()
                    model_names = [m.get("name", "") for m in tags.get("models", [])]
                    return {
                        "status": "ok",
                        "model_available": self.model in model_names,
                        "models": model_names,
                    }
                return {"status": "error", "message": "Ollama not responding"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def generate_diagnosis(self, prompt: str) -> str:
        """Call Gemma 4 via Ollama with JSON Schema-enforced output."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "format": DIAGNOSIS_SCHEMA,
            "options": {"temperature": self.temperature},
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/generate", json=payload
                )
                if response.status_code != 200:
                    raise Exception(f"Ollama error {response.status_code}: {response.text}")
                return response.json().get("response", "")
        except httpx.TimeoutException:
            raise Exception(f"Ollama timeout after {self.timeout}s — model may be cold-loading")

    @staticmethod
    def build_diagnosis_prompt(
        symptoms: str, patient_context: str, relevant_conditions: list[dict]
    ) -> str:
        """Build user prompt with patient data + KB-grounded candidate conditions."""
        if relevant_conditions:
            conditions_block = "\n".join(
                f"- {c['name']} ({c.get('category', 'general')}): "
                f"key symptoms = {', '.join(c.get('symptoms', [])[:5])}; "
                f"guideline = {c.get('guideline', 'N/A')}; "
                f"urgency = {c.get('urgency', 'UNKNOWN')}"
                for c in relevant_conditions[:6]
            )
        else:
            conditions_block = (
                "(NONE — no candidate conditions matched the symptoms in our KB. "
                "Per system rules, return the 'No acute condition identified' "
                "default with triage GREEN. Do NOT invent a condition.)"
            )

        context_block = patient_context.strip() if patient_context.strip() else "(none provided)"

        return f"""PATIENT SYMPTOMS:
{symptoms}

PATIENT CONTEXT:
{context_block}

CANDIDATE CONDITIONS (KB-grounded — choose differentials from these):
{conditions_block}

Produce up to 3 differentials ranked by clinical likelihood. For each:
- condition: choose from the candidate conditions above when possible
- confidence: 0.0–0.9 (never claim certainty)
- reasoning: 1–2 sentences citing specific symptoms
- guideline_reference: use the guideline string from the candidate
- recommendation: concrete next action (e.g., "Arrange immediate hospital transport")

Then set triage_level (RED/YELLOW/GREEN), list any red_flags_detected, and set escalation_required (true if RED)."""


ollama_client = OllamaClient()
