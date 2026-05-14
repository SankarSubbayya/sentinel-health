"""Unit tests for multimodal image plumbing.

Verifies: the prompt builder injects an image-attached clause only when
has_image is true; OllamaClient strips a data-URL prefix correctly; the
Ollama HTTP payload includes `images` only when an image is provided.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import json
import pytest

from app.core import llm as llm_module
from app.core.llm import OllamaClient, _strip_data_url


class TestStripDataUrl:
    def test_strips_data_url_prefix(self):
        assert _strip_data_url("data:image/jpeg;base64,ABCDEF") == "ABCDEF"
        assert _strip_data_url("data:image/png;base64,XYZ") == "XYZ"

    def test_raw_base64_passthrough(self):
        assert _strip_data_url("ABCDEF==") == "ABCDEF=="

    def test_empty_passthrough(self):
        assert _strip_data_url("") == ""


class TestPromptBuilderImageClause:
    def test_no_image_no_clause(self):
        prompt = OllamaClient.build_diagnosis_prompt(
            "chest pain", "55M smoker", [], has_image=False
        )
        assert "IMAGE IS ATTACHED" not in prompt
        assert "wound, rash, snake" not in prompt

    def test_with_image_inserts_clause(self):
        prompt = OllamaClient.build_diagnosis_prompt(
            "snake bit child", "rural area", [], has_image=True
        )
        assert "IMAGE IS ATTACHED" in prompt
        assert "additional clinical evidence" in prompt

    def test_image_clause_appears_before_candidates(self):
        prompt = OllamaClient.build_diagnosis_prompt(
            "x", "", [], has_image=True
        )
        assert prompt.index("IMAGE IS ATTACHED") < prompt.index("CANDIDATE CONDITIONS")


@pytest.mark.asyncio
class TestOllamaPayload:
    async def _capture_payload(self, monkeypatch, image=None):
        """Run generate_diagnosis with httpx.AsyncClient mocked, return the JSON payload sent."""
        captured = {}

        class _FakeResponse:
            status_code = 200
            def json(self):
                return {"response": '{"differential_diagnosis":[],"triage_level":"GREEN","red_flags_detected":[],"escalation_required":false}'}

        class _FakeClient:
            def __init__(self, *a, **kw):
                pass
            async def __aenter__(self):
                return self
            async def __aexit__(self, *a):
                return False
            async def post(self, url, json):
                captured["url"] = url
                captured["json"] = json
                return _FakeResponse()

        monkeypatch.setattr(llm_module.httpx, "AsyncClient", _FakeClient)

        client = OllamaClient()
        await client.generate_diagnosis("the prompt", language="en", image=image)
        return captured

    async def test_no_image_omits_images_field(self, monkeypatch):
        captured = await self._capture_payload(monkeypatch, image=None)
        assert "images" not in captured["json"]

    async def test_image_added_as_array(self, monkeypatch):
        captured = await self._capture_payload(monkeypatch, image="ABCDEF==")
        assert captured["json"]["images"] == ["ABCDEF=="]

    async def test_data_url_prefix_stripped_in_payload(self, monkeypatch):
        captured = await self._capture_payload(
            monkeypatch, image="data:image/jpeg;base64,RAW123"
        )
        assert captured["json"]["images"] == ["RAW123"]
