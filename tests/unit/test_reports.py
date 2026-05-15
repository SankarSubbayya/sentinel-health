"""Unit tests for the append-only report log.

Verifies: save/list/get roundtrip; ordering (newest first); limit; disabled
mode is a no-op; missing file gracefully returns empty; malformed lines
are skipped not crashed-on.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services import reports as reports_module
from app.services.reports import save_report, list_reports, get_report


@pytest.fixture
def temp_reports_path(tmp_path, monkeypatch):
    """Point the reports service at an isolated tmp file and re-enable."""
    p = tmp_path / "reports.jsonl"
    monkeypatch.setattr(reports_module.settings, "reports_path", str(p))
    monkeypatch.setattr(reports_module.settings, "reports_enabled", True)
    return p


def _resp(session_id: str, triage: str = "RED", condition: str = "Acute MI"):
    return {
        "session_id": session_id,
        "triage_level": triage,
        "differential_diagnosis": [
            {"condition": condition, "confidence": 0.8, "reasoning": "x"}
        ],
        "safety": {"is_red_flag": True, "escalation_required": True, "escalation_reason": "r"},
    }


class TestSaveAndList:
    def test_save_returns_path(self, temp_reports_path):
        path = save_report(_resp("s1"), "chest pain", "55M")
        assert path == str(temp_reports_path)
        assert temp_reports_path.exists()

    def test_save_appends_one_line_per_call(self, temp_reports_path):
        save_report(_resp("s1"), "chest pain")
        save_report(_resp("s2"), "snake bite")
        save_report(_resp("s3"), "stroke")
        lines = temp_reports_path.read_text().strip().split("\n")
        assert len(lines) == 3

    def test_list_returns_newest_first(self, temp_reports_path):
        save_report(_resp("s1"), "first")
        save_report(_resp("s2"), "second")
        save_report(_resp("s3"), "third")
        out = list_reports()
        assert [r["session_id"] for r in out] == ["s3", "s2", "s1"]

    def test_list_respects_limit(self, temp_reports_path):
        for i in range(5):
            save_report(_resp(f"s{i}"), f"case {i}")
        assert len(list_reports(limit=2)) == 2

    def test_record_includes_inputs_and_timestamp(self, temp_reports_path):
        save_report(
            _resp("s1"),
            symptoms="chest pain and sweating",
            patient_context="55M smoker",
            language="hi",
        )
        rec = list_reports()[0]
        assert rec["session_id"] == "s1"
        assert rec["symptoms"] == "chest pain and sweating"
        assert rec["patient_context"] == "55M smoker"
        assert rec["language"] == "hi"
        assert rec["triage_level"] == "RED"
        assert "ts" in rec


class TestGet:
    def test_get_returns_matching_record(self, temp_reports_path):
        save_report(_resp("alpha"), "a")
        save_report(_resp("beta"), "b")
        rec = get_report("beta")
        assert rec is not None
        assert rec["session_id"] == "beta"

    def test_get_returns_none_for_missing(self, temp_reports_path):
        save_report(_resp("alpha"), "a")
        assert get_report("nope") is None

    def test_get_handles_missing_file(self, temp_reports_path):
        assert not temp_reports_path.exists()
        assert get_report("anything") is None


class TestDisabled:
    def test_save_is_noop_when_disabled(self, tmp_path, monkeypatch):
        p = tmp_path / "reports.jsonl"
        monkeypatch.setattr(reports_module.settings, "reports_path", str(p))
        monkeypatch.setattr(reports_module.settings, "reports_enabled", False)
        result = save_report(_resp("s1"), "chest pain")
        assert result is None
        assert not p.exists()


class TestRobustness:
    def test_malformed_lines_skipped(self, temp_reports_path):
        save_report(_resp("good1"), "x")
        # inject a broken line between two good ones
        with temp_reports_path.open("a") as f:
            f.write("{not valid json\n")
        save_report(_resp("good2"), "y")
        out = list_reports()
        ids = [r["session_id"] for r in out]
        assert ids == ["good2", "good1"]

    def test_blank_lines_ignored(self, temp_reports_path):
        save_report(_resp("s1"), "x")
        with temp_reports_path.open("a") as f:
            f.write("\n\n   \n")
        save_report(_resp("s2"), "y")
        assert len(list_reports()) == 2

    def test_unicode_survives_roundtrip(self, temp_reports_path):
        save_report(
            _resp("hindi"),
            symptoms="सीने में दर्द",
            patient_context="५५ साल पुरुष",
            language="hi",
        )
        rec = get_report("hindi")
        assert rec is not None
        assert rec["symptoms"] == "सीने में दर्द"
        assert rec["patient_context"] == "५५ साल पुरुष"


class TestImageSideFile:
    """W3-F9: attached images are persisted as side-files in
    data/reports/images/<sid>.<ext> for record-of-care."""

    # A 1x1 red JPEG as a minimal valid blob.
    _RAW_JPEG_BYTES = bytes.fromhex(
        "ffd8ffe000104a46494600010100000100010000ffdb004300080606070605080707"
        "070909080a0c140d0c0b0b0c1912130f141d1a1f1e1d1a1c1c20242e2720222c231c"
        "1c2837292c30313434341f27393d38323c2e333432ffdb0043010909090c0b0c180d"
        "0d1832211c213232323232323232323232323232323232323232323232323232323232"
        "32323232323232323232323232323232323232323232323232ffc00011080001000103"
        "012200021101031101ffc4001f0000010501010101010100000000000000000102030405"
        "060708090a0bffc400b5100002010303020403050504040000017d010203000411051221"
        "31410613516107227114328191a1082342b1c11552d1f02433627282090a161718191a"
        "25262728292a3435363738393a434445464748494a535455565758595a636465666768"
        "696a737475767778797a838485868788898a92939495969798999aa2a3a4a5a6a7a8a9"
        "aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d9dae1e2e3e4e5e6e7"
        "e8e9eaf1f2f3f4f5f6f7f8f9faffc4001f0100030101010101010101010000000000000"
        "00102030405060708090a0bffc400b5110002010204040304070504040001027700010"
        "20311040521314106125161072271143281914250a1b1c109233352f0156272d10a16"
        "2434e125f11718191a262728292a35363738393a434445464748494a5354555657585"
        "95a636465666768696a737475767778797a82838485868788898a92939495969798999"
        "aa2a3a4a5a6a7a8a9aab2b3b4b5b6b7b8b9bac2c3c4c5c6c7c8c9cad2d3d4d5d6d7d8d"
        "9dae2e3e4e5e6e7e8e9eaf2f3f4f5f6f7f8f9faffda000c03010002110311003f00fbf"
        "cffd9"
    )

    def _jpeg_data_url(self):
        import base64 as _b
        return "data:image/jpeg;base64," + _b.b64encode(self._RAW_JPEG_BYTES).decode()

    def test_image_written_to_side_file(self, temp_reports_path):
        save_report(_resp("withimg"), "chest pain", image=self._jpeg_data_url())
        images_dir = temp_reports_path.parent / "images"
        files = list(images_dir.iterdir()) if images_dir.exists() else []
        assert len(files) == 1
        assert files[0].suffix == ".jpg"
        # The bytes on disk match the original image, not the b64 string.
        assert files[0].read_bytes() == self._RAW_JPEG_BYTES

    def test_record_carries_image_path_and_bytes(self, temp_reports_path):
        save_report(_resp("withimg"), "chest pain", image=self._jpeg_data_url())
        rec = get_report("withimg")
        assert rec is not None
        assert rec["image_present"] is True
        assert rec["image_path"] is not None
        assert rec["image_path"].startswith("images/")
        assert rec["image_path"].endswith(".jpg")
        assert rec["image_bytes"] == len(self._RAW_JPEG_BYTES)

    def test_no_image_no_side_file(self, temp_reports_path):
        save_report(_resp("noimg"), "chest pain", image=None)
        images_dir = temp_reports_path.parent / "images"
        assert not images_dir.exists() or list(images_dir.iterdir()) == []
        rec = get_report("noimg")
        assert rec["image_present"] is False
        assert rec["image_path"] is None
        assert rec["image_bytes"] == 0

    def test_png_gets_png_extension(self, temp_reports_path):
        import base64 as _b
        png = _b.b64encode(b"\x89PNG\r\n\x1a\n" + b"x" * 32).decode()
        save_report(_resp("pngsid"), "x", image=f"data:image/png;base64,{png}")
        path = temp_reports_path.parent / "images"
        files = list(path.iterdir())
        assert any(f.suffix == ".png" for f in files)

    def test_raw_base64_no_data_url_defaults_to_jpg(self, temp_reports_path):
        import base64 as _b
        b64 = _b.b64encode(self._RAW_JPEG_BYTES).decode()
        save_report(_resp("rawsid"), "x", image=b64)
        path = temp_reports_path.parent / "images"
        files = list(path.iterdir())
        assert len(files) == 1
        assert files[0].suffix == ".jpg"

    def test_disabled_mode_does_not_write_image(self, tmp_path, monkeypatch):
        p = tmp_path / "reports.jsonl"
        monkeypatch.setattr(reports_module.settings, "reports_path", str(p))
        monkeypatch.setattr(reports_module.settings, "reports_enabled", False)
        save_report(_resp("s1"), "x", image=self._jpeg_data_url())
        images_dir = tmp_path / "images"
        assert not images_dir.exists()

    def test_read_report_image_returns_bytes_and_mime(self, temp_reports_path):
        save_report(_resp("withimg"), "chest pain", image=self._jpeg_data_url())
        from app.services.reports import read_report_image
        got = read_report_image("withimg")
        assert got is not None
        blob, mime = got
        assert blob == self._RAW_JPEG_BYTES
        assert mime == "image/jpeg"

    def test_read_report_image_none_when_no_image(self, temp_reports_path):
        save_report(_resp("noimg"), "chest pain", image=None)
        from app.services.reports import read_report_image
        assert read_report_image("noimg") is None

    def test_read_report_image_none_for_missing_report(self, temp_reports_path):
        from app.services.reports import read_report_image
        assert read_report_image("nonexistent") is None

    def test_filename_sanitises_session_id(self, temp_reports_path):
        # session_id with slashes/punctuation must not escape the images dir.
        save_report(_resp("../escape/me!"), "x", image=self._jpeg_data_url())
        images_dir = temp_reports_path.parent / "images"
        files = list(images_dir.iterdir())
        assert len(files) == 1
        # No slashes / double-dots survive in the filename.
        assert "/" not in files[0].name
        assert ".." not in files[0].name
