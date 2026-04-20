"""Lifecycle endpoint tests — no DB required.

Uses FastAPI TestClient. /healthz and /version don't touch the DB.
/readyz hits ``check_connection`` which returns False if no pool —
that's the expected behaviour without an init_pool() call.
"""

from __future__ import annotations

import pytest


pytestmark = pytest.mark.unit


def test_healthz_returns_alive():
    """``/healthz`` is a leaf handler — no DB, no NATS, no anything."""
    from fastapi.testclient import TestClient
    from src.main import app

    # Plain TestClient (no ``with`` block) → no lifespan startup → no
    # accidental DB connection attempt during a unit test.
    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"alive": True}


def test_version_returns_metadata():
    from fastapi.testclient import TestClient
    from src.main import app

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/version")
    assert resp.status_code == 200
    body = resp.json()
    assert body["sidecar_version"] == "1.0.0"
    assert body["contract_version"] == "1.0.0"
    assert body["environment"] in ("local", "ci", "staging", "test")


def test_readyz_503_when_db_pool_missing():
    """Without lifespan startup, the pool is None → DB check returns False
    → ready=False → status 503. This is the correct behaviour."""
    from fastapi.testclient import TestClient
    from src.main import app

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get("/readyz")
    assert resp.status_code == 503
    body = resp.json()
    assert body["ready"] is False
    assert body["database"] is False
    assert body["test_mode"] is True


def test_introspect_requires_seed_token():
    """Auth-protected endpoints reject requests without the token."""
    from fastapi.testclient import TestClient
    from src.main import app

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get(
        "/test-introspect/v1/invariants/rls/tenant_e2e_local",
    )
    # Header missing → 422 (Pydantic) or 401 (handler) depending on FastAPI version
    assert resp.status_code in (401, 422), (
        f"Unauthenticated request should be rejected, got {resp.status_code}"
    )


def test_introspect_rejects_wrong_seed_token():
    from fastapi.testclient import TestClient
    from src.main import app

    client = TestClient(app, raise_server_exceptions=False)
    resp = client.get(
        "/test-introspect/v1/invariants/rls/tenant_e2e_local",
        headers={"X-Test-Seed-Token": "wrong"},
    )
    assert resp.status_code == 401
