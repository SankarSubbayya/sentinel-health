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


def _transport_eta_line() -> str | None:
    """Compute the 'Transport ETA: ~N min (K km to <hub>)' string from config.

    Returns None if no distance is configured — the section is omitted from
    the escalation message rather than emitting a placeholder.
    """
    km = settings.nearest_hub_km
    kmh = settings.avg_ambulance_kmh
    if not km or km <= 0 or not kmh or kmh <= 0:
        return None
    eta_min = int(round((km / kmh) * 60))
    hub = settings.hub_group_name or settings.hub_physician_name or "the hub"
    km_str = f"{km:g}"  # drop trailing zeros: 18.0 → "18"
    return f"~{eta_min} min ({km_str} km to {hub})"


def build_whatsapp_escalation(
    diagnosis: dict[str, Any],
    symptoms: str,
    patient_context: str = "",
    session_id: str | None = None,
    ambulance_number: str | None = None,
) -> dict[str, Any] | None:
    """Return WhatsApp handoff payload, or None if not a RED case.

    `ambulance_number` is an optional free-text label (e.g. "AMB-12" or
    a phone number) that the CHW assigns at dispatch time; surfaces in
    the Transport section so the hub can correlate ambulance arrival.
    """
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

    eta_line = _transport_eta_line()
    if ambulance_number or eta_line:
        lines += ["", "*Transport:*"]
        if ambulance_number:
            lines.append(f"Ambulance: {ambulance_number}")
        if eta_line:
            lines.append(f"ETA: {eta_line}")

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
        "ambulance_number": ambulance_number or None,
        "transport_eta": _transport_eta_line(),
        "nearest_hub_km": settings.nearest_hub_km if settings.nearest_hub_km > 0 else None,
        "text": text,
        "wa_me_url": wa_me_url,
    }
