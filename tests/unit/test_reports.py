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
