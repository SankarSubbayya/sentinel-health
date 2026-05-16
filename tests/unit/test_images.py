"""Unit tests for validate_image — the cheap pre-flight check that fails
malformed images at the API boundary so they don't crash Ollama and get
absorbed into the diagnose service's broad YELLOW-fallback handler.
"""

from __future__ import annotations

import base64

import pytest

from app.services.images import validate_image


# Synthetic JPEG that passes our validator: real SOI/JFIF header,
# padding to clear the 200-byte minimum, and a real EOI trailer.
# validate_image doesn't decode pixel data — it only checks magic bytes,
# size, and trailer — so the middle can be arbitrary bytes.
_VALID_JPEG_BYTES = (
    b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00"
    + bytes(300)
    + b"\xff\xd9"
)

_VALID_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    + bytes(180)  # padding to clear min-size
    + b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _b64(data: bytes) -> str:
    return base64.b64encode(data).decode()


def _data_url(data: bytes, mime: str) -> str:
    return f"data:{mime};base64,{_b64(data)}"


class TestHappyPath:
    def test_valid_jpeg_data_url(self):
        bytes_out, ext, err = validate_image(_data_url(_VALID_JPEG_BYTES, "image/jpeg"))
        assert err is None
        assert ext == "jpg"
        assert bytes_out == _VALID_JPEG_BYTES

    def test_valid_jpeg_raw_base64(self):
        bytes_out, ext, err = validate_image(_b64(_VALID_JPEG_BYTES))
        assert err is None
        assert ext == "jpg"

    def test_valid_png(self):
        _, ext, err = validate_image(_data_url(_VALID_PNG_BYTES, "image/png"))
        assert err is None
        assert ext == "png"


class TestTruncation:
    """These are the actual failure modes — header alone, no EOF marker, etc."""

    def test_header_only_22_byte_jpeg_is_rejected(self):
        # This is the exact base64 from the bug report.
        bad = "/9j/4AAQSkZJRgABAQEASABIAAD/2wBDAA=="
        _, _, err = validate_image(bad)
        assert err is not None
        assert "too small" in err.lower() or "truncated" in err.lower()

    def test_jpeg_missing_eoi_is_rejected(self):
        # 1000 bytes starting with FFD8FFE0 but no FFD9 trailer.
        bad = b"\xff\xd8\xff\xe0" + b"\x00" * 996
        _, _, err = validate_image(_b64(bad))
        assert err is not None
        assert "FFD9" in err or "truncated" in err.lower()

    def test_png_missing_iend_is_rejected(self):
        bad = b"\x89PNG\r\n\x1a\n" + b"x" * 300  # no IEND chunk
        _, _, err = validate_image(_b64(bad))
        assert err is not None
        assert "iend" in err.lower() or "truncated" in err.lower()


class TestRejections:
    def test_empty_string(self):
        _, _, err = validate_image("")
        assert err is not None
        assert "empty" in err.lower()

    def test_malformed_data_url(self):
        _, _, err = validate_image("data:totally bogus,xxx")
        assert err is not None
        assert "data url" in err.lower()

    def test_garbage_base64(self):
        _, _, err = validate_image("data:image/jpeg;base64,!!!not base64@@@")
        assert err is not None
        assert "base64" in err.lower()

    def test_unknown_format(self):
        # 300 bytes that decode fine but have no recognised image magic.
        bytes_300 = b"\x00\x01\x02\x03" + b"X" * 296
        _, _, err = validate_image(_b64(bytes_300))
        assert err is not None
        assert "not recognised" in err.lower()

    def test_mime_contradicts_magic_bytes(self):
        # JPEG bytes but data URL says PNG → caught.
        url = _data_url(_VALID_JPEG_BYTES, "image/png")
        _, _, err = validate_image(url)
        assert err is not None
        assert "contradicts" in err.lower()


class TestFormats:
    def test_webp_passes(self):
        # RIFF chunk size + WEBP magic + padding to clear the size floor.
        webp = b"RIFF" + (300).to_bytes(4, "little") + b"WEBP" + b"\x00" * 300
        _, ext, err = validate_image(_b64(webp))
        assert err is None
        assert ext == "webp"

    def test_gif_passes(self):
        gif = b"GIF89a" + b"\x00" * 250 + b"\x3b"  # trailer byte
        _, ext, err = validate_image(_b64(gif))
        assert err is None
        assert ext == "gif"

    def test_heic_passes(self):
        # HEIC: 4 size bytes, "ftyp", brand "heic"
        heic = b"\x00\x00\x00\x18ftypheic" + b"\x00" * 300
        _, ext, err = validate_image(_b64(heic))
        assert err is None
        assert ext == "heic"
