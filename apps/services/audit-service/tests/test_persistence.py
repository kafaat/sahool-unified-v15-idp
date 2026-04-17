"""
Integration tests for the audit-service persistence layer.

These tests exercise the *same* code path used in production:
  * POST /api/v1/audit/logs writes through ``app.state.store``
  * GET  /api/v1/audit/logs and friends read through the same store
  * /api/v1/audit/chain/validate recomputes the per-tenant hash chain

The PostgreSQL backend is only exercised when TEST_DATABASE_URL is set;
otherwise we fall back to ``InMemoryAuditStore`` which uses the exact
same hash-chain and query logic. Both backends share the
``compute_entry_hash`` helper, so a passing in-memory test demonstrates
the hashing is symmetric with validation.
"""

from __future__ import annotations

import os

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover
    pytest.skip("fastapi not installed", allow_module_level=True)

# Must be set before importing src.main so the lifespan picks the in-memory store.
os.environ.setdefault("ENVIRONMENT", "test")

VALID_TENANT_ID = "00000000-0000-0000-0000-000000000042"
OTHER_TENANT_ID = "11111111-1111-1111-1111-111111111111"


@pytest.fixture
def client():
    """TestClient with auth overridden for ``VALID_TENANT_ID``."""
    from src.main import app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    async def _user():
        return User(
            id="test-user",
            email="t@example.com",
            tenant_id=VALID_TENANT_ID,
            roles=["admin"],
        )

    app.dependency_overrides[get_current_user] = _user
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def cross_tenant_client():
    """TestClient posing as a user in ``OTHER_TENANT_ID``. Used to verify
    that reads never cross tenants even when the X-Tenant-Id header lies.
    """
    from src.main import app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    async def _user():
        return User(
            id="other-user",
            email="o@example.com",
            tenant_id=OTHER_TENANT_ID,
            roles=["admin"],
        )

    app.dependency_overrides[get_current_user] = _user
    try:
        with TestClient(app) as c:
            yield c
    finally:
        app.dependency_overrides.clear()


HDR = {"X-Tenant-Id": VALID_TENANT_ID}


# ═══════════════════════════════════════════════════════════════════════════
# Core persistence contract
# ═══════════════════════════════════════════════════════════════════════════


def test_write_returns_entry_with_hash_and_seq(client):
    """POST must return the persisted entry with id, seq_num, entry_hash
    and prev_hash filled by the store — not by the caller."""
    r = client.post(
        "/api/v1/audit/logs",
        headers=HDR,
        json={
            "action": "user.login",
            "category": "authentication",
            "severity": "info",
            "details": {"method": "password"},
        },
    )
    assert r.status_code == 200, r.text
    entry = r.json()
    assert entry["id"]
    assert entry["tenant_id"] == VALID_TENANT_ID
    assert entry["user_id"] == "test-user"
    assert entry["action"] == "user.login"
    assert entry["category"] == "authentication"
    assert entry["seq_num"] == 1  # first write for this tenant (isolated)
    assert len(entry["entry_hash"]) == 64  # SHA-256 hex
    assert entry["prev_hash"] == "0" * 64  # genesis


def test_sequence_numbers_are_monotonic(client):
    ids = []
    for i in range(5):
        r = client.post(
            "/api/v1/audit/logs",
            headers=HDR,
            json={
                "action": f"field.update.{i}",
                "category": "field_ops",
                "severity": "info",
                "details": {"n": i},
            },
        )
        assert r.status_code == 200
        ids.append(r.json()["seq_num"])
    assert ids == sorted(ids)
    assert len(set(ids)) == len(ids)  # unique


def test_each_entry_links_to_previous_hash(client):
    first = client.post(
        "/api/v1/audit/logs",
        headers=HDR,
        json={"action": "a", "category": "authentication", "severity": "info", "details": {}},
    ).json()
    second = client.post(
        "/api/v1/audit/logs",
        headers=HDR,
        json={"action": "b", "category": "authentication", "severity": "info", "details": {}},
    ).json()
    assert second["prev_hash"] == first["entry_hash"]


# ═══════════════════════════════════════════════════════════════════════════
# Write-then-read
# ═══════════════════════════════════════════════════════════════════════════


def test_read_back_after_write(client):
    payload = {
        "action": "field.created",
        "category": "field_ops",
        "severity": "info",
        "resource_type": "field",
        "resource_id": "F-001",
        "details": {"area_ha": 12.5},
    }
    written = client.post("/api/v1/audit/logs", headers=HDR, json=payload).json()

    r = client.get("/api/v1/audit/logs", headers=HDR)
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    ids = [e["id"] for e in body["items"]]
    assert written["id"] in ids


def test_filter_by_action_pushes_down(client):
    # Two different actions in the same tenant.
    client.post(
        "/api/v1/audit/logs",
        headers=HDR,
        json={"action": "auth.login.success", "category": "authentication", "severity": "info", "details": {}},
    )
    client.post(
        "/api/v1/audit/logs",
        headers=HDR,
        json={"action": "auth.login.failed", "category": "authentication", "severity": "warning", "details": {}},
    )
    r = client.get("/api/v1/audit/logs?action=auth.login.failed", headers=HDR)
    body = r.json()
    assert all(e["action"] == "auth.login.failed" for e in body["items"])
    assert body["total"] >= 1


def test_filter_by_resource(client):
    client.post(
        "/api/v1/audit/logs",
        headers=HDR,
        json={
            "action": "field.updated",
            "category": "field_ops",
            "severity": "info",
            "resource_type": "field",
            "resource_id": "F-042",
            "details": {},
        },
    )
    r = client.get(
        "/api/v1/audit/resources/field/F-042/trail",
        headers=HDR,
    )
    assert r.status_code == 200
    body = r.json()
    assert body["total"] >= 1
    for entry in body["items"]:
        assert entry["resource_type"] == "field"
        assert entry["resource_id"] == "F-042"


# ═══════════════════════════════════════════════════════════════════════════
# Tamper detection
# ═══════════════════════════════════════════════════════════════════════════


def test_validate_chain_happy_path(client):
    for i in range(3):
        client.post(
            "/api/v1/audit/logs",
            headers=HDR,
            json={
                "action": f"a{i}",
                "category": "authentication",
                "severity": "info",
                "details": {"i": i},
            },
        )
    r = client.get("/api/v1/audit/chain/validate", headers=HDR)
    assert r.status_code == 200
    body = r.json()
    assert body["valid"] is True
    assert body["invalid_entries"] == []
    assert body["total_entries"] >= 3


def test_validate_chain_detects_tampering():
    """If a historical entry is mutated out-of-band, the recomputed hash
    no longer matches the stored ``entry_hash`` and validation fails.

    This test reaches directly into the in-memory store (the backend
    that serves CI) to simulate tampering — a legitimate attacker would
    have bypassed the DB triggers that prevent UPDATE in production.
    """
    import asyncio

    from src.main import app
    from src.persistence import InMemoryAuditStore

    store = InMemoryAuditStore()

    async def run():
        for i in range(3):
            await store.write(
                {
                    "tenant_id": VALID_TENANT_ID,
                    "user_id": "u",
                    "action": f"a{i}",
                    "category": "authentication",
                    "severity": "info",
                    "details": {"i": i},
                }
            )
        # Tamper with entry #1 (details field) without recomputing hash.
        store._by_tenant[VALID_TENANT_ID][1]["details"] = {"i": 99}
        return await store.validate_chain(VALID_TENANT_ID)

    result = asyncio.get_event_loop().run_until_complete(run())
    assert result.valid is False
    assert any("entry_hash mismatch" in err for err in result.errors)


# ═══════════════════════════════════════════════════════════════════════════
# Tenant isolation
# ═══════════════════════════════════════════════════════════════════════════


def test_writes_are_tenant_isolated(client, cross_tenant_client):
    # Write as VALID_TENANT_ID.
    client.post(
        "/api/v1/audit/logs",
        headers={"X-Tenant-Id": VALID_TENANT_ID},
        json={"action": "secret.access", "category": "security", "severity": "info", "details": {}},
    )
    # Read as OTHER_TENANT_ID — must not see it.
    r = cross_tenant_client.get(
        "/api/v1/audit/logs",
        headers={"X-Tenant-Id": OTHER_TENANT_ID},
    )
    assert r.status_code == 200
    for entry in r.json()["items"]:
        assert entry["tenant_id"] == OTHER_TENANT_ID
        assert entry["action"] != "secret.access"


def test_header_tenant_must_match_jwt_tenant(client):
    # Authenticated as VALID_TENANT_ID but claiming OTHER_TENANT_ID → 403.
    r = client.get(
        "/api/v1/audit/logs",
        headers={"X-Tenant-Id": OTHER_TENANT_ID},
    )
    assert r.status_code == 403


# ═══════════════════════════════════════════════════════════════════════════
# tenants_with_activity_since — feeds the periodic chain-validation sweep
# ═══════════════════════════════════════════════════════════════════════════


def test_tenants_with_activity_returns_writers_only():
    """Only tenants that actually wrote should show up; dormant tenants
    with historical entries older than the cutoff are excluded.

    Uses ``asyncio.run`` rather than
    ``get_event_loop().run_until_complete`` (deprecated under modern
    pytest/Python event-loop policies) and passes ``created_at``
    through the public ``write()`` API — no reaching into the store's
    private ``_by_tenant`` dict.
    """
    import asyncio
    from datetime import UTC, datetime, timedelta

    from src.persistence import InMemoryAuditStore

    async def _run():
        store = InMemoryAuditStore()
        now = datetime.now(UTC)

        await store.write({
            "tenant_id": "tenant-active-1",
            "user_id": "u1",
            "action": "x",
            "category": "authentication",
            "severity": "info",
            "details": {},
            "created_at": now.isoformat(),
        })
        await store.write({
            "tenant_id": "tenant-active-2",
            "user_id": "u2",
            "action": "y",
            "category": "authentication",
            "severity": "info",
            "details": {},
            "created_at": now.isoformat(),
        })
        # Dormant tenant: backdated via the public API, no private access.
        await store.write({
            "tenant_id": "tenant-dormant",
            "user_id": "u3",
            "action": "z",
            "category": "authentication",
            "severity": "info",
            "details": {},
            "created_at": (now - timedelta(days=30)).isoformat(),
        })

        since = now - timedelta(hours=1)
        return await store.tenants_with_activity_since(since)

    tenants = asyncio.run(_run())
    assert "tenant-active-1" in tenants
    assert "tenant-active-2" in tenants
    assert "tenant-dormant" not in tenants
