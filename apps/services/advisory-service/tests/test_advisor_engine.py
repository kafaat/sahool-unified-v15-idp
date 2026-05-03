"""Tests for the AdvisorEngine orchestrator (with KG / CRAG / NATS mocked).

Uses minimal in-memory fakes to exercise the rule-based scoring path
end-to-end without requiring qdrant-client, httpx, or nats.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_SVC_ROOT = Path(__file__).resolve().parents[1]
if str(_SVC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SVC_ROOT))

from src.advisor_engine import AdvisorEngine  # noqa: E402
from src.feedback import FeedbackPublisher  # noqa: E402
from src.governance import GovernanceEngine  # noqa: E402
from src.learning import LearningEngine  # noqa: E402
from src.signal_derivation import FieldContext  # noqa: E402


class _FakeKG:
    async def search_entities(self, query, entity_type=None, limit=20):
        return [{"id": "rust", "name": "wheat rust"}]

    async def close(self):
        pass


class _SilentFeedback(FeedbackPublisher):
    def __init__(self) -> None:  # pragma: no cover - trivial
        super().__init__(nats_url="nats://disabled")
        self.sent: list[dict] = []

    async def publish_feedback(self, feedback, tenant_id=None):
        self.sent.append(feedback)
        return True

    async def close(self):
        pass


@pytest.fixture
def advisor() -> AdvisorEngine:
    return AdvisorEngine(
        kg_client=_FakeKG(),  # type: ignore[arg-type]
        crag_kb=None,  # CRAG path is exercised via separate unit tests
        governance=GovernanceEngine(),
        learning=LearningEngine(),
        feedback=_SilentFeedback(),
        embedding_func=None,
    )


@pytest.mark.asyncio
async def test_recommend_water_stress_increases_irrigation(advisor: AdvisorEngine) -> None:
    field = FieldContext(
        ndvi=0.5,
        ndwi=0.1,  # water stress
        soil_moisture=0.5,
        temperature=25.0,
        crop_type="wheat",
        growth_stage="vegetative",
        region="saudi",
    )
    decision = await advisor.generate_recommendation(field)
    assert decision["action"] == "increase_irrigation"
    assert decision["status"] == "approved"  # irrigation is auto-approved
    assert decision["signals"]["water_stress"] is True
    assert "common_diseases" in decision["graph_context"]


@pytest.mark.asyncio
async def test_recommend_nitrogen_requires_approval(advisor: AdvisorEngine) -> None:
    field = FieldContext(
        ndvi=0.5,
        ndwi=0.5,
        soil_moisture=0.5,
        temperature=25.0,
        crop_type="wheat",
        growth_stage="vegetative",
        region="saudi",
        nitrogen_level=0.2,
    )
    decision = await advisor.generate_recommendation(field)
    assert decision["action"] == "add_nitrogen"
    assert decision["requires_approval"] is True
    assert decision["status"] == "pending_approval"


@pytest.mark.asyncio
async def test_recommend_no_signals_yields_no_action(advisor: AdvisorEngine) -> None:
    field = FieldContext(
        ndvi=0.7,
        ndwi=0.5,
        soil_moisture=0.5,
        temperature=25.0,
        crop_type="wheat",
        growth_stage="vegetative",
        region="saudi",
    )
    decision = await advisor.generate_recommendation(field)
    assert decision["action"] == "no_action"


@pytest.mark.asyncio
async def test_record_feedback_publishes_and_learns(advisor: AdvisorEngine) -> None:
    await advisor.record_feedback(
        decision_id="dec-1",
        result="improved",
        crop="wheat",
        region="saudi",
        action="increase_irrigation",
    )
    sent = advisor.feedback.sent  # type: ignore[attr-defined]
    assert len(sent) == 1
    assert sent[0]["decision_id"] == "dec-1"
    # Learning should now register success.
    assert advisor.learning.get_success_rate("wheat", "saudi", "increase_irrigation") == 1.0


@pytest.mark.asyncio
async def test_feedback_publisher_no_nats_returns_false() -> None:
    publisher = FeedbackPublisher(nats_url="nats://disabled")
    # nc is never connected → publish should return False, not raise.
    result = await publisher.publish_feedback({"decision_id": "x"})
    assert result is False


@pytest.mark.asyncio
async def test_feedback_publisher_uses_tenant_scoped_subject() -> None:
    """``publish_feedback`` must construct ``sahool.tenant.<id>.advisory.feedback_recorded``."""
    import json

    captured: dict = {}

    class _RecordingNC:
        async def publish(self, subject, data):
            captured["subject"] = subject
            captured["payload"] = json.loads(data.decode())

    publisher = FeedbackPublisher(nats_url="nats://disabled")
    publisher.nc = _RecordingNC()  # type: ignore[assignment]

    tenant = "00000000-0000-4000-8000-000000000001"
    ok = await publisher.publish_feedback(
        {"decision_id": "dec-9", "result": "improved"},
        tenant_id=tenant,
    )
    assert ok is True
    assert captured["subject"] == f"sahool.tenant.{tenant}.advisory.feedback_recorded"
    assert captured["payload"]["tenant_id"] == tenant


@pytest.mark.asyncio
async def test_feedback_publisher_skips_when_tenant_missing() -> None:
    """Without a tenant_id the publish must NOT fall back to a global subject."""

    class _BoomNC:
        async def publish(self, subject, data):  # pragma: no cover - must not be called
            raise AssertionError(f"unexpected publish to {subject!r}")

    publisher = FeedbackPublisher(nats_url="nats://disabled")
    publisher.nc = _BoomNC()  # type: ignore[assignment]
    ok = await publisher.publish_feedback({"decision_id": "dec-9"})
    assert ok is False
