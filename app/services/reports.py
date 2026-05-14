"""Append-only JSONL audit log of every diagnose call.

Why JSONL (not SQLite or a real DB):
- Offline-first laptop deployment can't depend on a DB service.
- Each line is a complete record; corruption affects one line, not all.
- POSIX `O_APPEND` writes <PIPE_BUF (~4 KB) are atomic — our records
  are well under that, so we don't need explicit locking for the
  single-process FastAPI server.

PHI lives in `symptoms` and `patient_context` fields. For the local
clinic-laptop deployment that's the right place for it; for the cloud
demo, set `REPORTS_ENABLED=false` to keep PHI off the host.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from datetime import datetime, timezone
from typing import Any
from app.core.config import settings


def _resolve_path() -> Path:
    """Path is taken as-is if absolute, otherwise relative to repo root."""
    p = Path(settings.reports_path)
    if not p.is_absolute():
        p = Path(__file__).resolve().parents[2] / p
    return p


def save_report(
    response: dict[str, Any],
    symptoms: str,
    patient_context: str = "",
    language: str = "en",
    image: str | None = None,
) -> str | None:
    """Append one report to the JSONL log. Returns the file path written, or
    None if persistence is disabled.

    Image bytes are NOT stored — we only record presence + approximate size
    to keep the audit log compact and avoid pinning PHI photos to disk."""
    if not settings.reports_enabled:
        return None

    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": response.get("session_id"),
        "language": language,
        "symptoms": symptoms,
        "patient_context": patient_context,
        "image_present": bool(image),
        "image_size_b64": len(image) if image else 0,
        "triage_level": response.get("triage_level"),
        "differential_diagnosis": response.get("differential_diagnosis", []),
        "safety": response.get("safety", {}),
        "during_transport": response.get("during_transport"),
        "folk_error_correction": response.get("folk_error_correction"),
        "escalation": response.get("escalation"),
    }

    path = _resolve_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    line = json.dumps(record, ensure_ascii=False) + "\n"
    # Open with O_APPEND so concurrent writes (e.g., uvicorn workers) don't
    # interleave; short writes are atomic.
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o644)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)
    return str(path)


def list_reports(limit: int | None = None) -> list[dict[str, Any]]:
    """Return the most recent N reports (newest first)."""
    limit = limit or settings.reports_list_default_limit
    path = _resolve_path()
    if not path.exists():
        return []

    # Stream from the end if the file is large; for hackathon scale (10s-100s
    # of records) we can just read everything.
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    records.reverse()
    return records[:limit]


def get_report(session_id: str) -> dict[str, Any] | None:
    """Find one report by session_id. Returns None if not found."""
    path = _resolve_path()
    if not path.exists():
        return None
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("session_id") == session_id:
                return rec
    return None
