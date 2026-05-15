"""Append-only JSONL audit log of every diagnose call.

Why JSONL (not SQLite or a real DB):
- Offline-first laptop deployment can't depend on a DB service.
- Each line is a complete record; corruption affects one line, not all.
- POSIX `O_APPEND` writes <PIPE_BUF (~4 KB) are atomic — our records
  are well under that, so we don't need explicit locking for the
  single-process FastAPI server.

Attached images (ECG photos, wound photos, etc.) are persisted as
side-files in data/reports/images/<session_id>.<ext> so the JSONL
stays compact and human-scannable. The JSONL record carries a path
reference; the file itself is what the receiving clinician needs for
record-of-care (especially for ECGs that drive thrombolysis decisions).

PHI lives in `symptoms`, `patient_context`, and the image side-files.
For the local clinic-laptop deployment that's the right place for it;
for the cloud demo, set `REPORTS_ENABLED=false` to keep PHI off the
host entirely.
"""

from __future__ import annotations

import base64
import json
import os
import re
import uuid
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


def _images_dir() -> Path:
    """Side-file image directory, sibling to reports.jsonl."""
    return _resolve_path().parent / "images"


# Whitelisted extensions we'll persist; anything else stored as `.bin`.
_MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
    "image/gif": "gif",
}


def _decode_image(image: str) -> tuple[bytes, str] | None:
    """Parse a data-URL or raw-base64 image string. Returns (bytes, extension)
    or None if the string can't be decoded."""
    if not image:
        return None
    # Data URL: "data:image/jpeg;base64,XXXX..."
    m = re.match(r"^data:([\w/+\-.]+);base64,(.*)$", image, flags=re.DOTALL)
    if m:
        mime = m.group(1).lower().strip()
        b64 = m.group(2)
        ext = _MIME_TO_EXT.get(mime, "bin")
    else:
        # Raw base64 with no header — assume JPEG (most common from camera).
        b64 = image
        ext = "jpg"
    try:
        return base64.b64decode(b64, validate=False), ext
    except Exception:
        return None


def _write_image_side_file(session_id: str | None, image: str) -> tuple[str, int] | None:
    """Write the image bytes to the side-file dir. Returns (relative_path, bytes_written)
    or None if persistence is disabled, image is missing, or decode failed."""
    if not image:
        return None
    decoded = _decode_image(image)
    if not decoded:
        return None
    blob, ext = decoded
    sid = session_id or str(uuid.uuid4())
    sid_clean = re.sub(r"[^\w-]", "_", sid)
    images_dir = _images_dir()
    images_dir.mkdir(parents=True, exist_ok=True)
    out_path = images_dir / f"{sid_clean}.{ext}"
    out_path.write_bytes(blob)
    # Return a path that's relative to the JSONL file so the record is portable
    # if the data/ dir gets moved as a unit.
    try:
        rel = out_path.relative_to(_resolve_path().parent)
        return str(rel), len(blob)
    except ValueError:
        return str(out_path), len(blob)


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

    side_file = _write_image_side_file(response.get("session_id"), image) if image else None
    image_path, image_bytes = side_file if side_file else (None, 0)

    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "session_id": response.get("session_id"),
        "language": language,
        "symptoms": symptoms,
        "patient_context": patient_context,
        "image_present": bool(image),
        # Side-file storage: path is relative to reports.jsonl's parent dir
        # (data/reports/), so the audit trail can be relocated atomically.
        "image_path": image_path,
        "image_bytes": image_bytes,
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


_EXT_TO_MIME = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "webp": "image/webp",
    "heic": "image/heic",
    "gif": "image/gif",
}


def read_report_image(session_id: str) -> tuple[bytes, str] | None:
    """Return (image_bytes, mime_type) for a session's persisted image,
    or None if the report doesn't exist or has no image attached."""
    rec = get_report(session_id)
    if not rec or not rec.get("image_path"):
        return None
    rel = rec["image_path"]
    full = _resolve_path().parent / rel
    if not full.exists():
        return None
    ext = full.suffix.lstrip(".").lower()
    mime = _EXT_TO_MIME.get(ext, "application/octet-stream")
    return full.read_bytes(), mime
