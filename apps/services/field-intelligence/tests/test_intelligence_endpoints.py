"""
Tests for the /api/v1/fields/{id}/intelligence/* + /api/v1/intelligence/*
stub endpoints.

Scope: contract conformance only — each test asserts the response shape
matches the TypeScript interfaces the web client consumes
(apps/web/src/features/fields/api/field-intelligence-api.ts →
LivingFieldScore / FieldZone[] / FieldAlert[] / FieldRecommendation[] /
CreatedTask / BestDay[] / DateValidation). Stubs are deterministic, so
tests assert byte-level equality between two calls with the same input.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Auth bypass
# ---------------------------------------------------------------------------
# The router has a `Depends(get_current_user)` on every endpoint.  The unit
# tests here are shape-only — we don't exercise the auth path — so override
# the dependency to a dummy user for the whole test module.
@pytest.fixture(autouse=True)
def override_auth(client: TestClient):
    from src.api.intelligence_endpoints import User, get_current_user
    from src.main import app

    async def _fake_user() -> User:  # type: ignore[override]
        # The real `shared.auth.models.User` is a dataclass with required
        # `id` / `email` / `roles` fields (and several optional ones); a
        # bare `User()` call would `TypeError`. Build via the dataclass
        # constructor when the shared model is available, fall back to
        # the permissive stub attributes otherwise (for the ImportError
        # branch in intelligence_endpoints.py).
        try:
            u = User(
                id="test-user",
                email="test-user@example.com",
                roles=[],
                tenant_id="tenant-test",
            )  # type: ignore[call-arg]
        except TypeError:
            u = User()
            u.id = "test-user"  # type: ignore[attr-defined]
            u.tenant_id = "tenant-test"  # type: ignore[attr-defined]
        return u

    app.dependency_overrides[get_current_user] = _fake_user
    yield
    app.dependency_overrides.pop(get_current_user, None)


# ---------------------------------------------------------------------------
# Envelope helper
# ---------------------------------------------------------------------------


def _assert_ok_envelope(body: dict) -> dict:
    """Assert `{success: true, data: ...}` and return `data`."""
    assert body.get("success") is True, f"expected success=true, got {body}"
    assert "data" in body, f"expected 'data' key, got {body}"
    return body["data"]


# ---------------------------------------------------------------------------
# LivingFieldScore
# ---------------------------------------------------------------------------


class TestLivingFieldScore:
    def test_shape(self, client: TestClient):
        r = client.get("/api/v1/fields/field-abc/intelligence/score")
        assert r.status_code == 200
        data = _assert_ok_envelope(r.json())
        # Top-level keys per LivingFieldScore TypeScript interface
        for key in (
            "fieldId",
            "overall",
            "health",
            "hydration",
            "attention",
            "astral",
            "trend",
            "trendPercentage",
            "lastUpdated",
            "components",
        ):
            assert key in data, f"missing key: {key}"
        assert data["fieldId"] == "field-abc"
        assert 0 <= data["overall"] <= 100
        assert data["trend"] in ("improving", "stable", "declining")
        # components sub-object
        components = data["components"]
        for comp in ("ndvi", "soilMoisture", "taskCompletion", "astronomical"):
            assert comp in components, f"missing component: {comp}"

    def test_deterministic(self, client: TestClient):
        """Two reads with the same field_id must be byte-identical."""
        r1 = client.get("/api/v1/fields/field-xyz/intelligence/score").json()
        r2 = client.get("/api/v1/fields/field-xyz/intelligence/score").json()
        assert r1 == r2

    def test_different_fields_differ(self, client: TestClient):
        r1 = client.get("/api/v1/fields/field-a/intelligence/score").json()
        r2 = client.get("/api/v1/fields/field-b/intelligence/score").json()
        assert r1["data"]["overall"] != r2["data"]["overall"] or r1 != r2


# ---------------------------------------------------------------------------
# FieldZone[] / FieldAlert[] / FieldRecommendation[]
# All three MUST return `data` as an array directly (not an object wrapper).
# ---------------------------------------------------------------------------


class TestArrayResponses:
    @pytest.mark.parametrize(
        "path",
        [
            "/api/v1/fields/field-x/intelligence/zones",
            "/api/v1/fields/field-x/intelligence/alerts",
            "/api/v1/fields/field-x/intelligence/recommendations",
        ],
    )
    def test_data_is_array(self, client: TestClient, path: str):
        r = client.get(path)
        assert r.status_code == 200
        data = _assert_ok_envelope(r.json())
        assert isinstance(data, list), f"{path}: data should be array, got {type(data).__name__}"

    def test_alerts_respects_status_param(self, client: TestClient):
        """Status query param is accepted without error."""
        r = client.get("/api/v1/fields/field-x/intelligence/alerts", params={"status": "resolved"})
        assert r.status_code == 200


# ---------------------------------------------------------------------------
# CreatedTask (POST /intelligence/alerts/{id}/create-task)
# ---------------------------------------------------------------------------


class TestCreateTaskFromAlert:
    def test_shape(self, client: TestClient):
        payload = {
            "title": "Inspect field",
            "titleAr": "تفقد الحقل",
            "priority": "high",
            "description": "Walk the southern edge",
            "descriptionAr": "افحص الحافة الجنوبية",
            "dueDate": "2026-05-01",
        }
        r = client.post("/api/v1/intelligence/alerts/alert-123/create-task", json=payload)
        assert r.status_code == 202
        task = _assert_ok_envelope(r.json())
        # CreatedTask required fields per TS interface
        for key in (
            "id",
            "fieldId",
            "alertId",
            "title",
            "titleAr",
            "priority",
            "status",
            "createdAt",
        ):
            assert key in task, f"missing CreatedTask key: {key}"
        assert task["alertId"] == "alert-123"
        assert task["title"] == "Inspect field"
        assert task["titleAr"] == "تفقد الحقل"
        assert task["priority"] == "high"
        # CreatedTask.fieldId is required-non-empty by the web TS interface.
        assert isinstance(task["fieldId"], str) and task["fieldId"], "fieldId must be non-empty"

    def test_client_supplied_field_id_echoed(self, client: TestClient):
        """When the client sends fieldId it MUST be echoed back on the task."""
        payload = {
            "title": "t",
            "titleAr": "ع",
            "priority": "low",
            "fieldId": "field-explicit-42",
        }
        r = client.post("/api/v1/intelligence/alerts/alert-xy/create-task", json=payload)
        assert r.status_code == 202
        assert r.json()["data"]["fieldId"] == "field-explicit-42"

    def test_idempotent_task_id(self, client: TestClient):
        """Same alert_id must produce the same task id (for optimistic UI retries)."""
        payload = {"title": "t", "titleAr": "ع", "priority": "low"}
        r1 = client.post("/api/v1/intelligence/alerts/alert-fixed/create-task", json=payload).json()
        r2 = client.post("/api/v1/intelligence/alerts/alert-fixed/create-task", json=payload).json()
        assert r1["data"]["id"] == r2["data"]["id"]

    def test_invalid_priority_rejected(self, client: TestClient):
        r = client.post(
            "/api/v1/intelligence/alerts/alert-1/create-task",
            json={"title": "t", "titleAr": "ع", "priority": "bogus"},
        )
        assert r.status_code == 422


# ---------------------------------------------------------------------------
# BestDay[]
# ---------------------------------------------------------------------------


class TestBestDays:
    def test_shape(self, client: TestClient):
        r = client.get(
            "/api/v1/intelligence/best-days",
            params={"activity": "planting", "days": 7, "field_id": "f1"},
        )
        assert r.status_code == 200
        days = _assert_ok_envelope(r.json())
        assert isinstance(days, list)
        assert len(days) == 7
        d0 = days[0]
        for key in (
            "date",
            "score",
            "suitability",
            "suitabilityAr",
            "weather",
            "astronomical",
            "reasons",
            "reasonsAr",
        ):
            assert key in d0, f"missing BestDay key: {key}"
        # Ranked best-first
        scores = [d["score"] for d in days]
        assert scores == sorted(scores, reverse=True)

    def test_unknown_activity_returns_envelope_400(self, client: TestClient):
        r = client.get(
            "/api/v1/intelligence/best-days",
            params={"activity": "underwater-farming", "days": 3},
        )
        assert r.status_code == 400
        body = r.json()
        # Error body follows the same envelope, not FastAPI's {detail: ...}
        assert body.get("success") is False
        assert "error" in body
        assert "errorAr" in body
        assert body.get("errorCode") == "INVALID_ACTIVITY"
        assert "validActivities" in body


# ---------------------------------------------------------------------------
# DateValidation
# ---------------------------------------------------------------------------


class TestValidateDate:
    def test_shape(self, client: TestClient):
        r = client.post(
            "/api/v1/intelligence/validate-date",
            json={"date": "2026-05-15", "activity": "irrigation", "field_id": "f1"},
        )
        assert r.status_code == 200
        validation = _assert_ok_envelope(r.json())
        for key in (
            "date",
            "activity",
            "activityAr",
            "suitable",
            "score",
            "rating",
            "ratingAr",
            "reasons",
            "reasonsAr",
        ):
            assert key in validation, f"missing DateValidation key: {key}"
        assert validation["date"] == "2026-05-15"
        assert validation["activity"] == "irrigation"
        assert isinstance(validation["suitable"], bool)

    def test_unknown_activity_returns_envelope_400(self, client: TestClient):
        r = client.post(
            "/api/v1/intelligence/validate-date",
            json={"date": "2026-05-15", "activity": "unknown"},
        )
        assert r.status_code == 400
        body = r.json()
        assert body.get("success") is False
        assert body.get("errorCode") == "INVALID_ACTIVITY"


# ---------------------------------------------------------------------------
# Aggregate /field-intelligence/{id}
# ---------------------------------------------------------------------------


class TestAggregate:
    def test_shape(self, client: TestClient):
        r = client.get("/api/v1/field-intelligence/field-agg")
        assert r.status_code == 200
        data = _assert_ok_envelope(r.json())
        for key in ("fieldId", "score", "zones", "alerts", "recommendations"):
            assert key in data, f"missing key: {key}"
        assert data["fieldId"] == "field-agg"
        # Nested flat-ness: zones/alerts/recommendations are direct arrays,
        # not wrapped in another envelope.
        assert isinstance(data["zones"], list)
        assert isinstance(data["alerts"], list)
        assert isinstance(data["recommendations"], list)
        # score is the LivingFieldScore object (not re-wrapped)
        assert "overall" in data["score"]
        assert "components" in data["score"]
