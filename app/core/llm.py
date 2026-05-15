"""Ollama client plus diagnosis/clarify JSON schemas and system prompts."""

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


CLARIFY_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "questions": {
            "type": "array",
            "minItems": 1,
            "maxItems": 2,
            "items": {
                "type": "object",
                "properties": {
                    "id": {"type": "string"},
                    "text": {"type": "string"},
                    "rationale": {"type": "string"},
                },
                "required": ["id", "text", "rationale"],
            },
        }
    },
    "required": ["questions"],
}


def _strip_data_url(image: str) -> str:
    """Accept either a raw base64 string or a data URL; return raw base64."""
    if "," in image and image.startswith("data:"):
        return image.split(",", 1)[1]
    return image


LANG_NAMES: dict[str, str] = {
    "en": "English",
    "hi": "Hindi (use Devanagari script)",
    "ta": "Tamil (use Tamil script)",
    "ml": "Malayalam (use Malayalam script)",
}


def _language_directive(language: str) -> str:
    """One-line instruction appended to system prompts to control output language."""
    label = LANG_NAMES.get(language, LANG_NAMES["en"])
    if language == "en":
        return ""
    return (
        f"\n\nUSER LANGUAGE: {label}. The user's symptoms may be in {label} or in English. "
        f"Output `reasoning`, `recommendation`, and (where natural) `guideline_reference` in {label}. "
        f"Keep the `condition` field in English (e.g., \"Acute Coronary Syndrome\") so it matches the candidate list. "
        f"Translate medical terminology into plain {label} that a community health worker would understand."
    )


CLARIFY_SYSTEM_PROMPT = """You are Sentinel Health. The community health worker has described symptoms but the differential is uncertain. Produce 1–2 high-yield clarifying questions targeted at distinguishing the most likely differential from the next most likely. Each question must be brief, plain-language, and answerable by the patient or family. Output must conform exactly to the requested JSON schema. Never produce more than 2 questions."""


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

Image-led reasoning (when an image is attached AND symptoms are sparse, e.g. "found unconscious, no history"):
- Use the image as the primary clinical evidence. Describe what you see (pupil size, wound, rash, container label, ECG features) in the `reasoning` field — that description is the history the CHW couldn't get verbally.
- For an ECG image with chest pain in context: identify ST elevation / depression / new LBBB / arrhythmia if visible. Defer the thrombolysis decision to the hub physician — your job is to flag findings and trigger transport, not to commit to lytics at PHC level.
- For skin lesions: be honest about uncertainty. A 4B-parameter model is not a dermatologist. Provide a single most-likely diagnosis with confidence ≤ 0.7 plus at most one differential, and recommend dermatology review or photo referral for definitive diagnosis.

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

    async def generate_diagnosis(
        self, prompt: str, language: str = "en", image: str | None = None
    ) -> str:
        """Call Gemma 4 via Ollama with JSON Schema-enforced output.

        If `image` is provided (base64 JPEG/PNG, with or without data URL
        prefix), it is passed in the Ollama `images` field — Gemma 4 IT
        treats it as multimodal evidence alongside the prompt.
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": SYSTEM_PROMPT + _language_directive(language),
            "stream": False,
            "format": DIAGNOSIS_SCHEMA,
            "options": {"temperature": self.temperature},
            "keep_alive": settings.ollama_keep_alive,
        }
        if image:
            payload["images"] = [_strip_data_url(image)]

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

    async def generate_clarification(self, prompt: str, language: str = "en") -> str:
        """Call Gemma 4 via Ollama for clarifying questions with JSON Schema-enforced output."""
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": CLARIFY_SYSTEM_PROMPT + _language_directive(language),
            "stream": False,
            "format": CLARIFY_SCHEMA,
            "options": {"temperature": self.temperature},
            "keep_alive": settings.ollama_keep_alive,
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
    def build_clarify_prompt(
        symptoms: str,
        patient_context: str,
        relevant_conditions: list[dict],
        language: str = "en",
    ) -> str:
        """Build user prompt for clarifying-question generation."""
        if relevant_conditions:
            conditions_block = "\n".join(
                f"- {c['name']} ({c.get('category', 'general')}): "
                f"key symptoms = {', '.join(c.get('symptoms', [])[:5])}"
                for c in relevant_conditions[:4]
            )
        else:
            conditions_block = "(no candidate conditions matched yet)"

        context_block = patient_context.strip() if patient_context.strip() else "(none provided)"

        return f"""PATIENT SYMPTOMS SO FAR:
{symptoms}

PATIENT CONTEXT:
{context_block}

POSSIBLE DIFFERENTIALS (KB-grounded):
{conditions_block}

Produce 1–2 short clarifying questions. For each:
- id: short slug (e.g. "q1")
- text: the question itself, plain language
- rationale: one short clause naming which differential it disambiguates"""

    @staticmethod
    def build_diagnosis_prompt(
        symptoms: str,
        patient_context: str,
        relevant_conditions: list[dict],
        language: str = "en",
        has_image: bool = False,
    ) -> str:
        """Build user prompt with patient data + KB-grounded candidate conditions."""
        def _cond_line(c: dict) -> str:
            parts = [
                f"- {c['name']} ({c.get('category', 'general')})",
                f"  key symptoms: {', '.join(c.get('symptoms', [])[:5])}",
                f"  guideline: {c.get('guideline', 'N/A')}",
                f"  urgency: {c.get('urgency', 'UNKNOWN')}",
            ]
            if c.get("recommendation"):
                parts.append(f"  protocol: {c['recommendation']}")
            if c.get("phc_thrombolysis_decision"):
                parts.append(f"  thrombolysis decision: {c['phc_thrombolysis_decision']}")
            return "\n".join(parts)

        if relevant_conditions:
            conditions_block = "\n".join(_cond_line(c) for c in relevant_conditions[:6])
        else:
            conditions_block = (
                "(NONE — no candidate conditions matched the symptoms in our KB. "
                "Per system rules, return the 'No acute condition identified' "
                "default with triage GREEN. Do NOT invent a condition.)"
            )

        context_block = patient_context.strip() if patient_context.strip() else "(none provided)"
        image_block = (
            "AN IMAGE IS ATTACHED (e.g., wound, rash, snake, ECG, container label). "
            "Treat it as additional clinical evidence alongside the symptoms. "
            "Reference what you see in your reasoning when relevant.\n\n"
            if has_image else ""
        )

        return f"""PATIENT SYMPTOMS:
{symptoms}

PATIENT CONTEXT:
{context_block}

{image_block}CANDIDATE CONDITIONS (KB-grounded — choose differentials from these):
{conditions_block}

Produce up to 3 differentials ranked by clinical likelihood. For each:
- condition: choose from the candidate conditions above when possible
- confidence: 0.0–0.9 (never claim certainty)
- reasoning: 1–2 sentences citing specific symptoms
- guideline_reference: use the guideline string from the candidate
- recommendation: concrete next action. If the candidate provides a `protocol` line above, your recommendation MUST surface the named drugs and doses verbatim (e.g., "Establish IV access (venflon), give Aspirin 325 mg chewed + Clopidogrel 300 mg loading…"). Do not paraphrase away the loading-dose recipe — a community health worker at a PHC needs the exact instruction, not a summary. Add the transport instruction at the end.

Then set triage_level (RED/YELLOW/GREEN), list any red_flags_detected, and set escalation_required (true if RED)."""


ollama_client = OllamaClient()
