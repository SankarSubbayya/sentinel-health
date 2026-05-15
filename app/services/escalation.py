"""Build the WhatsApp hub-physician handoff message for RED triage.

Message body mirrors the real-world PHC → tertiary handoff format used in
WhatsApp hub-and-spoke groups (per Hari's TVMCH Cardiology group example):
header → from/to/ref → H/o + patient + Sentinel reading → plan at spoke →
during transport → (optional) thrombolysis decision for hub → disclaimer.

The payload returned has two destinations:
  - `wa_me_url`: single-contact deep-link (works when a specific physician
    has been configured as the recipient).
  - `text` + `recipient_label`: the message body + a label like
    "TVMCH Cardiology Hub and Spoke" for a clipboard-copy button in the
    UI, so the CHW can paste into the group chat (WhatsApp has no group
    deep-link).
"""

from datetime import datetime, timezone
from typing import Any
from urllib.parse import quote
from app.core.config import settings


def _normalise_phone(phone: str) -> str:
    """Strip everything except digits — wa.me wants country-code + number, no '+'."""
    return "".join(ch for ch in phone if ch.isdigit())


def _spoke_label() -> str:
    """From: line — facility plus optional CHW name."""
    if settings.chw_name:
        return f"{settings.facility_name} · {settings.chw_name}"
    return settings.facility_name


def _hub_label() -> str:
    """To: line — group name if configured, otherwise the named physician."""
    return settings.hub_group_name or settings.hub_physician_name


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
    thrombolysis = diagnosis.get("phc_thrombolysis_decision", "")
    now = datetime.now(timezone.utc)
    ts = now.isoformat(timespec="seconds")
    date_short = now.strftime("%d/%m/%y")

    conf_pct = (
        f"{int(round(float(confidence) * 100))}%"
        if isinstance(confidence, (int, float))
        else "—"
    )

    lines = [
        "*Sentinel Health — RED escalation*",
        f"_{date_short} · ref {session_id[:8] if session_id else '—'}_",
        "",
        f"*From:* {_spoke_label()}",
        f"*To:*   {_hub_label()}",
        f"*At:*   {ts}",
        "",
        f"*Reason:* {reason}",
    ]
    if patient_context.strip():
        lines.append(f"*Patient:* {patient_context.strip()}")
    lines.append(f"*H/o:* {symptoms.strip()}")

    lines += [
        "",
        f"*Sentinel reading:* {condition} ({conf_pct})",
    ]
    if reasoning:
        lines.append(reasoning)
    if guideline:
        lines.append(f"_Guideline:_ {guideline}")

    if recommendation:
        lines += ["", "*Plan at spoke:*", recommendation]
    if transport:
        lines += ["", "*During transport:*", transport]
    if thrombolysis:
        lines += ["", "*Thrombolysis decision (for hub):*", thrombolysis]

    lines += [
        "",
        "_Decision support only — final judgment with the receiving clinician._",
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
        "group_name": settings.hub_group_name or None,
        "recipient_label": _hub_label(),
        "text": text,
        "wa_me_url": wa_me_url,
    }
