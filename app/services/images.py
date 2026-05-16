"""Shared image-handling helpers.

`validate_image` does a cheap, dependency-free integrity check on a
base64-encoded image (raw or data-URL):

  - Strip the data-URL prefix if present.
  - Base64-decode strictly (rejects whitespace/garbage variants).
  - Detect format from magic bytes (JPEG, PNG, WEBP, HEIC, GIF).
  - Verify the format-specific end-of-file marker is present (so a
    truncated upload that just happens to have a valid header is
    caught here, not by Ollama at inference time).
  - Reject anything below 200 bytes as obviously truncated.

We do this at the API boundary so that a malformed image returns 400
with a useful message, rather than 500'ing inside Ollama and getting
absorbed into the diagnose service's broad YELLOW-fallback exception
handler (where the error becomes invisible).
"""

from __future__ import annotations

import base64
import re

_MIME_TO_EXT = {
    "image/jpeg": "jpg",
    "image/jpg": "jpg",
    "image/png": "png",
    "image/webp": "webp",
    "image/heic": "heic",
    "image/heif": "heic",
    "image/gif": "gif",
}

_MIN_IMAGE_BYTES = 200


def validate_image(image_str: str) -> tuple[bytes, str, str | None]:
    """Validate a base64-encoded image.

    Returns:
        (raw_bytes, extension, error_message)
        - On success: (bytes, "jpg"|"png"|..., None)
        - On failure: (bytes_so_far_or_empty, "", error_message)
    """
    if not image_str:
        return b"", "", "image is empty"

    # Strip the data-URL prefix if present.
    mime: str | None = None
    if image_str.startswith("data:"):
        m = re.match(r"^data:([\w/+\-.]+);base64,(.*)$", image_str, flags=re.DOTALL)
        if not m:
            return b"", "", "image: malformed data URL (expected data:image/...;base64,...)"
        mime = m.group(1).lower().strip()
        b64 = m.group(2)
    else:
        b64 = image_str

    # Strict base64 decode — rejects whitespace/non-base64 chars.
    try:
        data = base64.b64decode(b64, validate=True)
    except Exception as e:
        return b"", "", f"image: base64 decode failed ({e})"

    if len(data) < _MIN_IMAGE_BYTES:
        return data, "", (
            f"image is too small ({len(data)} bytes) — looks like the JPEG header "
            "alone, not a full image. Did the upload get truncated?"
        )

    # Detect format from magic bytes and verify the end-of-file marker.
    if data[:3] == b"\xff\xd8\xff":
        ext = "jpg"
        if not data.endswith(b"\xff\xd9"):
            return data, ext, (
                "JPEG is truncated — missing the end-of-image marker (FFD9). "
                "The file was cut off before being fully written."
            )
    elif data[:8] == b"\x89PNG\r\n\x1a\n":
        ext = "png"
        # Valid PNG ends with the IEND chunk: 00 00 00 00 49 45 4E 44 AE 42 60 82
        if not data.endswith(b"\x49\x45\x4e\x44\xae\x42\x60\x82"):
            return data, ext, "PNG is truncated — missing the IEND chunk."
    elif data[:4] == b"RIFF" and len(data) >= 12 and data[8:12] == b"WEBP":
        ext = "webp"
        # WEBP files don't have a strict end marker; trust the RIFF chunk size.
    elif len(data) >= 12 and data[4:8] == b"ftyp" and data[8:12] in (b"heic", b"heix", b"mif1", b"msf1"):
        ext = "heic"
    elif data[:6] in (b"GIF87a", b"GIF89a"):
        ext = "gif"
        if not data.endswith(b"\x3b"):
            return data, ext, "GIF is truncated — missing the trailer byte (0x3B)."
    else:
        return data, "", (
            "image format not recognised — expected JPEG, PNG, WEBP, HEIC, or GIF. "
            f"First 8 bytes seen: {data[:8].hex()}"
        )

    # If a MIME was declared in the data URL, sanity-check it matches the bytes.
    if mime and _MIME_TO_EXT.get(mime) and _MIME_TO_EXT[mime] != ext:
        return data, ext, (
            f"image MIME {mime!r} contradicts detected format {ext!r} — "
            "possible upload error."
        )

    return data, ext, None
