"""
Tests for /api/v1/irrigation/schedules CRUD + related validators.

Scope: contract + validator coverage only. Runtime CRUD behaviour (DB
round-trips) is covered separately via integration tests when a DB
pool is available; here we exercise:

  - `ScheduleUpdateRequest` validator rejects explicit null on NOT NULL
    columns but permits it on nullable ones
  - `ScheduleUpdateRequest` allows an empty payload (no-op update)
  - The service-wide HTTPException handler wraps detail into the
    canonical `ApiResponse` envelope (`{success, error, errorAr, ...}`)
    instead of FastAPI's default `{detail: ...}` shape
  - The 503 code path from `_require_db_pool` also flows through the
    envelope handler
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

# ---------------------------------------------------------------------------
# ScheduleUpdateRequest — NOT NULL column guard
# ---------------------------------------------------------------------------


class TestScheduleUpdateRequestValidator:
    """The model validator rejects explicit null for the three columns
    declared NOT NULL in migrations/001_create_irrigation_schedules.sql."""

    @pytest.fixture
    def Model(self):
        from src.main import ScheduleUpdateRequest

        return ScheduleUpdateRequest

    def test_empty_payload_ok(self, Model):
        """No fields set → no-op update. Must not raise."""
        m = Model()
        assert m.model_fields_set == set()

    def test_touch_nullable_column_ok(self, Model):
        """Updating a nullable column is always fine."""
        m = Model(status="active")
        assert "status" in m.model_fields_set

    def test_null_notnull_column_rejected(self, Model):
        """Explicit null on irrigation_date must be rejected."""
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            Model.model_validate({"irrigation_date": None})
        with pytest.raises(ValidationError):
            Model.model_validate({"duration_minutes": None})
        with pytest.raises(ValidationError):
            Model.model_validate({"water_amount_liters": None})

    def test_null_nullable_column_ok(self, Model):
        """Explicit null on a nullable column (notes) is permitted."""
        m = Model.model_validate({"notes": None})
        assert "notes" in m.model_fields_set
        assert m.notes is None

    def test_valid_update_preserves_values(self, Model):
        m = Model(status="active", duration_minutes=30)
        assert m.status == "active"
        assert m.duration_minutes == 30


# ---------------------------------------------------------------------------
# HTTPException envelope
# ---------------------------------------------------------------------------
#
# The service registers `@app.exception_handler(HTTPException)` that
# normalises every HTTPException — no matter where it's raised — into
# `{success: false, error, errorAr, errorCode?}`. We validate via
# `_require_db_pool` which raises 503 when no pool is configured (the
# TestClient starts the app with no lifespan by default, so db_pool
# is None).


@pytest.fixture
def client():
    """Module-local client fixture (mirrors conftest.py pattern)."""
    from src.main import app

    return TestClient(app)


class TestHTTPExceptionEnvelope:
    def test_schedules_list_without_db_returns_envelope_503(self, client: TestClient):
        """Calling list schedules without a DB pool must return the envelope.

        We can't hit the endpoint without auth; instead, exercise the
        503 path by calling _require_db_pool directly through a route
        we know fails before auth. The HTTPException handler is the
        thing under test.
        """
        # Trigger the handler via a path that raises HTTPException before
        # any auth dependency. We use a non-existent route to observe the
        # default 404 handler — but HTTPException 404 for wrong paths is
        # handled by Starlette's router, not our @exception_handler, so
        # instead we invoke the handler directly.
        from fastapi import HTTPException
        from src.main import _http_exception_envelope

        async def _run():
            from starlette.requests import Request
            from starlette.types import Scope

            # Synthetic Request shell; the handler only reads `exc`.
            scope: Scope = {"type": "http", "method": "GET", "headers": []}
            req = Request(scope)  # type: ignore[arg-type]
            return await _http_exception_envelope(
                req,
                HTTPException(
                    status_code=503,
                    detail={
                        "error": "Database not configured",
                        "error_ar": "قاعدة البيانات غير مُهيّأة",
                    },
                ),
            )

        import asyncio

        resp = asyncio.run(_run())
        assert resp.status_code == 503
        import json

        body = json.loads(resp.body)
        assert body["success"] is False
        assert body["error"] == "Database not configured"
        assert body["errorAr"] == "قاعدة البيانات غير مُهيّأة"

    def test_string_detail_mirrors_to_both_langs(self):
        """Plain string detail → errorAr falls back to same value."""
        import asyncio
        import json

        from fastapi import HTTPException
        from src.main import _http_exception_envelope
        from starlette.requests import Request

        async def _run():
            scope = {"type": "http", "method": "GET", "headers": []}
            req = Request(scope)  # type: ignore[arg-type]
            return await _http_exception_envelope(req, HTTPException(status_code=404, detail="Schedule not found"))

        resp = asyncio.run(_run())
        body = json.loads(resp.body)
        assert body["success"] is False
        assert body["error"] == "Schedule not found"
        assert body["errorAr"] == "Schedule not found"

    def test_extra_dict_keys_forwarded(self):
        """Custom keys on the detail (e.g. validActivities) are preserved
        at the top level of the envelope."""
        import asyncio
        import json

        from fastapi import HTTPException
        from src.main import _http_exception_envelope
        from starlette.requests import Request

        async def _run():
            scope = {"type": "http", "method": "GET", "headers": []}
            req = Request(scope)  # type: ignore[arg-type]
            return await _http_exception_envelope(
                req,
                HTTPException(
                    status_code=400,
                    detail={
                        "error": "Bad input",
                        "error_ar": "مدخل غير صالح",
                        "error_code": "BAD_INPUT",
                        "validOptions": ["a", "b"],
                    },
                ),
            )

        resp = asyncio.run(_run())
        body = json.loads(resp.body)
        assert body["errorCode"] == "BAD_INPUT"
        assert body["validOptions"] == ["a", "b"]
