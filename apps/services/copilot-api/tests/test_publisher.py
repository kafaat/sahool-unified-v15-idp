"""
Tests for NATS Event Publisher (events/publisher.py)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import json
from unittest.mock import AsyncMock, MagicMock

import pytest

pytestmark = [pytest.mark.unit]


class TestCopilotEvents:
    def test_all_event_types_defined(self):
        from src.events.publisher import COPILOT_EVENTS

        expected = [
            "chat_started",
            "chat_completed",
            "chat_failed",
            "tool_executed",
            "tool_blocked",
            "prompt_injection_detected",
            "rate_limit_exceeded",
        ]
        for evt in expected:
            assert evt in COPILOT_EVENTS

    def test_event_subjects_follow_naming_convention(self):
        from src.events.publisher import COPILOT_EVENTS

        for key, subject in COPILOT_EVENTS.items():
            assert subject.startswith("sahool.copilot.")


class TestPublishCopilotEvent:
    @pytest.mark.asyncio
    async def test_returns_false_when_nc_is_none(self):
        from src.events.publisher import publish_copilot_event

        result = await publish_copilot_event(None, "chat_started", {"user_id": "u1"})
        assert result is False

    @pytest.mark.asyncio
    async def test_returns_false_for_unknown_event_type(self):
        from src.events.publisher import publish_copilot_event

        nc = AsyncMock()
        result = await publish_copilot_event(nc, "nonexistent_event", {})
        assert result is False
        nc.publish.assert_not_called()

    @pytest.mark.asyncio
    async def test_publishes_to_correct_subject(self):
        from src.events.publisher import COPILOT_EVENTS, publish_copilot_event

        nc = AsyncMock()
        result = await publish_copilot_event(nc, "chat_started", {"user_id": "u1"})
        assert result is True
        nc.publish.assert_called_once()
        call_args = nc.publish.call_args
        assert call_args[0][0] == COPILOT_EVENTS["chat_started"]

    @pytest.mark.asyncio
    async def test_payload_contains_required_fields(self):
        from src.events.publisher import publish_copilot_event

        nc = AsyncMock()
        await publish_copilot_event(nc, "chat_completed", {"session_id": "s1", "elapsed_ms": 100.0})

        payload_bytes = nc.publish.call_args[0][1]
        payload = json.loads(payload_bytes.decode())
        assert payload["service"] == "copilot-api"
        assert payload["event_type"] == "chat_completed"
        assert payload["session_id"] == "s1"
        assert "timestamp" in payload

    @pytest.mark.asyncio
    async def test_returns_false_on_publish_exception(self):
        from src.events.publisher import publish_copilot_event

        nc = AsyncMock()
        nc.publish.side_effect = Exception("NATS connection error")
        result = await publish_copilot_event(nc, "chat_started", {})
        assert result is False
