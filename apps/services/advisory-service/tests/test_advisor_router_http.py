"""HTTP-level tests for the /v2 advisor router.

Mounts the router on a minimal FastAPI app (no lifespan, no shared deps)
so we can exercise request/response shapes, validation, pending-decision
storage and the tenant-mismatch guard without spinning up the full
advisory-service.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

_SVC_ROOT = Path(__file__).resolve().parents[1]
if str(_SVC_ROOT) not in sys.path:
    sys.path.insert(0, str(_SVC_ROOT))

from src import advisor_router  # noqa: E402
from src.advisor_engine import AdvisorEngine  # noqa: E402
from src.feedback import FeedbackPublisher  # noqa: E402
from src.governance import GovernanceEngine  # noqa: E402
from src.learning import LearningEngine  # noqa: E402


class _FakeKG:
    async def search_entities(self, query, entity_type=None, limit=20):
        return []

    async def close(self):
        pass


class _SilentFeedback(FeedbackPublisher):
    def __init__(self) -> None:
        super().__init__(nats_url="nats://disabled")
        self.sent: list[dict] = []

    async def publish_feedback(self, feedback):
        self.sent.append(feedback)
        return True

    async def close(self):
        pass


@pytest.fixture(autouse=True)
def _reset_router_state(monkeypatch):
    """Inject a fully-mocked AdvisorEngine and clear pending storage."""
    advisor = AdvisorEngine(
        kg_client=_FakeKG(),  # type: ignore[arg-type]
        crag_kb=None,
        governance=GovernanceEngine(),
        learning=LearningEngine(),
        feedback=_SilentFeedback(),
        embedding_func=None,
    )

    async def _get_advisor() -> AdvisorEngine:
        return advisor

    monkeypatch.setattr(advisor_router, "_get_advisor", _get_advisor)
    advisor_router._pending_memory.clear()
    monkeypatch.setattr(advisor_router, "_redis_singleton", None)
    monkeypatch.setattr(advisor_router, "_redis_unavailable", True)
    yield


@pytest.fixture
def client() -> TestClient:
    app = FastAPI()
    app.include_router(advisor_router.router)

    # Override JWT auth (which would otherwise return 401 without a token).
    # The `Depends(...)` was captured at module load — we override the
    # underlying callable that FastAPI resolves at request time.
    try:
        from shared.auth.dependencies import get_current_user  # noqa: PLC0415

        async def _fake_user():
            return {"id": "test-user", "tenant_id": "default"}

        app.dependency_overrides[get_current_user] = _fake_user
    except Exception:
        pass
    return TestClient(app)


def _ok_payload(**overrides):
    base = {
        "ndvi": 0.5,
        "ndwi": 0.1,  # forces water_stress → increase_irrigation (auto-approved)
        "soil_moisture": 0.5,
        "temperature": 25.0,
        "crop_type": "wheat",
        "growth_stage": "vegetative",
        "region": "saudi",
    }
    base.update(overrides)
    return base


def test_recommend_validation_rejects_out_of_range_ndvi(client: TestClient) -> None:
    resp = client.post("/v2/recommend", json=_ok_payload(ndvi=1.5))
    assert resp.status_code == 422


def test_recommend_auto_approve_returns_no_decision_id(client: TestClient) -> None:
    resp = client.post("/v2/recommend", json=_ok_payload())
    assert resp.status_code == 200
    body = resp.json()
    assert body["action"] == "increase_irrigation"
    assert body["status"] == "approved"
    assert body["requires_approval"] is False
    assert "decision_id" not in body


def test_recommend_pending_then_approve_flow(client: TestClient) -> None:
    # Nitrogen deficiency → add_nitrogen → pending_approval
    resp = client.post("/v2/recommend", json=_ok_payload(ndwi=0.5, nitrogen_level=0.2))
    assert resp.status_code == 200
    body = resp.json()
    assert body["action"] == "add_nitrogen"
    assert body["status"] == "pending_approval"
    decision_id = body["decision_id"]
    assert decision_id in advisor_router._pending_memory

    # Approve it
    resp2 = client.post(
        "/v2/approve",
        json={"decision_id": decision_id, "modified_action": "add_nitrogen_low_dose"},
    )
    assert resp2.status_code == 200
    body2 = resp2.json()
    assert body2["status"] == "approved"
    assert body2["decision"]["action"] == "add_nitrogen_low_dose"
    # Pending entry consumed
    assert decision_id not in advisor_router._pending_memory


def test_approve_unknown_decision_returns_404(client: TestClient) -> None:
    resp = client.post("/v2/approve", json={"decision_id": "does-not-exist"})
    assert resp.status_code == 404


def test_reject_pending_flow(client: TestClient) -> None:
    resp = client.post("/v2/recommend", json=_ok_payload(ndwi=0.5, nitrogen_level=0.2))
    decision_id = resp.json()["decision_id"]

    resp2 = client.post("/v2/reject", json={"decision_id": decision_id, "reason": "soil pH too low"})
    assert resp2.status_code == 200
    body = resp2.json()
    assert body["status"] == "rejected"
    assert "soil pH too low" in body["decision"]["governance_reason"]


def test_feedback_invalid_result_value_rejected(client: TestClient) -> None:
    resp = client.post("/v2/feedback", json={"decision_id": "x", "result": "great"})
    assert resp.status_code == 422


def test_feedback_publishes_event(client: TestClient) -> None:
    resp = client.post("/v2/feedback", json={"decision_id": "any", "result": "improved"})
    assert resp.status_code == 200
    assert resp.json()["status"] == "feedback_recorded"


def test_feedback_tenant_mismatch_rejected(client: TestClient) -> None:
    """Feedback on a tenant-scoped decision must fail-closed for other tenants.

    Regression for cross-tenant feedback poisoning: the stored decision is
    tenant-scoped to ``"default"`` (set by the fake user on /recommend), so a
    direct in-memory injection mimicking a different tenant's record must be
    rejected with 403 instead of silently publishing feedback.
    """
    advisor_router._pending_memory["foreign-decision"] = {
        "tenant_id": "other-tenant",
        "field_context": {"crop": "wheat", "region": "saudi"},
        "action": "add_nitrogen",
    }
    resp = client.post(
        "/v2/feedback",
        json={"decision_id": "foreign-decision", "result": "improved"},
    )
    assert resp.status_code == 403


def test_pending_memory_is_bounded(client: TestClient, monkeypatch) -> None:
    """Long Redis outages must not exhaust process memory."""
    monkeypatch.setattr(advisor_router, "_PENDING_MEMORY_MAX", 3)
    # Generate 5 pending decisions; only the last 3 should survive.
    for _ in range(5):
        resp = client.post("/v2/recommend", json=_ok_payload(ndwi=0.5, nitrogen_level=0.2))
        assert resp.status_code == 200
    assert len(advisor_router._pending_memory) == 3
