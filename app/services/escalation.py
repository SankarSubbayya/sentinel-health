"""Build the WhatsApp hub-physician handoff message for RED triage."""

from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote
from app.core.config import settings


def _normalise_phone(phone: str) -> str:
    """Strip everything except digits — wa.me wants country-code + number, no '+'."""
    return "".join(ch for ch in phone if ch.isdigit())


def build_whatsapp_escalation(
    diagnosis: dict[str, Any],
    symptoms: str,
    patient_context: str = "",
    session_id: str | None = None,
) -> dict[str, Any] | None:
    """Return WhatsApp handoff payload, or None if not a RED case."""
    if (diagnosis.get("triage_level") or "").upper() != "RED":
        return None

    top = (diagnosis.get("differential_diagnosis") or [{}])[0]
    condition = top.get("condition", "Unknown")
    confidence = top.get("confidence")
    guideline = top.get("guideline_reference", "")
    reasoning = top.get("reasoning", "")
    recommendation = top.get("recommendation", "")
    safety = diagnosis.get("safety") or {}
    reason = safety.get("escalation_reason") or "Red flag detected"
    transport = diagnosis.get("during_transport", "")
    ts = datetime.now(timezone.utc).isoformat(timespec="seconds")

    conf_pct = (
        f"{int(round(float(confidence) * 100))}%"
        if isinstance(confidence, (int, float))
        else "—"
    )

    lines = [
        "*Sentinel Health — RED escalation*",
        f"From: {settings.facility_name}",
        f"To: {settings.hub_physician_name}",
        f"At:   {ts}",
    ]
    if session_id:
        lines.append(f"Ref:  {session_id[:8]}")
    lines += [
        "",
        f"*Reason:* {reason}",
        f"*Top differential:* {condition} ({conf_pct})",
    ]
    if reasoning:
        lines.append(f"*Reasoning:* {reasoning}")
    if guideline:
        lines.append(f"*Guideline:* {guideline}")
    if recommendation:
        lines.append(f"*Action:* {recommendation}")
    lines += [
        "",
        f"*Symptoms:* {symptoms.strip()}",
    ]
    if patient_context.strip():
        lines.append(f"*Patient:* {patient_context.strip()}")
    if transport:
        lines += ["", f"*During transport:* {transport}"]
    lines += [
        "",
        "Decision support only — final judgment with the receiving clinician.",
    ]

    text = "\n".join(lines)
    phone = _normalise_phone(settings.hub_physician_phone)

    wa_me_url = (
        f"https://wa.me/{phone}?text={quote(text)}"
        if phone
        else f"https://wa.me/?text={quote(text)}"
    )

    return {
        "phone": settings.hub_physician_phone or None,
        "recipient_name": settings.hub_physician_name,
        "text": text,
        "wa_me_url": wa_me_url,
    }
