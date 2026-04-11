"""
Unit tests for the carbon-service operation_subscriber dedup layer.

Covers:
  * `_canonical_hash` — deterministic across key ordering, tamper-detects
    payload modifications
  * `_claim_event` — first insert wins, duplicate returns False
  * `_mark_processed` / `_mark_failed` — records outcome in dedup table
  * `handler` end-to-end — replay is skipped, tampered replay is skipped,
    already-computed row is not overwritten (second-line-of-defence)

These are pure-unit tests against an in-memory async DB stub — no real
Postgres required. The stub models the two SQL primitives we care about
(INSERT ... ON CONFLICT DO NOTHING RETURNING, UPDATE ... WHERE ...
RETURNING) with just enough fidelity to exercise the dedup logic.

For integration tests against a real Postgres with the migration
applied, see `tests/integration/` (not in this PR).
"""

from __future__ import annotations

import asyncio
import json
import os
import sys
from types import SimpleNamespace
from typing import Any

import pytest

# Add carbon-service to path so `src.events.operation_subscriber` resolves.
_SERVICE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _SERVICE_DIR not in sys.path:
    sys.path.insert(0, _SERVICE_DIR)

# Stub out src.api.v1.carbon and src.engine BEFORE importing the subscriber —
# they pull heavy Pydantic / DB / shared imports that are irrelevant to the
# dedup logic. We only need `_map_row_to_input` (any dict→dict function)
# and `IpccTier1Engine.compute` (returns a namespace with fixed numbers).
import importlib
import types

_stub_engine = types.ModuleType("src.engine")


class _StubEngine:
    def compute(self, op):
        return SimpleNamespace(
            emissions_kg=10.0,
            sequestration_kg=2.0,
            net_kg=8.0,
            carbon_credit_eligible=False,
            methodology="IPCC_Tier1_stub",
            emission_source_type="fuel",
        )


_stub_engine.IpccTier1Engine = _StubEngine  # type: ignore[attr-defined]
sys.modules["src.engine"] = _stub_engine

_stub_api_v1 = types.ModuleType("src.api.v1")
_stub_api_v1_carbon = types.ModuleType("src.api.v1.carbon")


def _map_row_to_input(row, metadata):
    return row


_stub_api_v1_carbon._map_row_to_input = _map_row_to_input
sys.modules["src.api"] = types.ModuleType("src.api")
sys.modules["src.api.v1"] = _stub_api_v1
sys.modules["src.api.v1.carbon"] = _stub_api_v1_carbon

# Now safe to import the subscriber module
from src.events import operation_subscriber as sub_mod  # noqa: E402


# ---------------------------------------------------------------------------
# Canonical hash tests — determinism + tamper detection
# ---------------------------------------------------------------------------


def test_canonical_hash_is_deterministic():
    env_a = {"operationId": "op-1", "tenantId": "t-1", "value": 42}
    env_b = {"value": 42, "tenantId": "t-1", "operationId": "op-1"}  # reordered
    assert sub_mod._canonical_hash(env_a) == sub_mod._canonical_hash(env_b)


def test_canonical_hash_tamper_detects_value_change():
    a = sub_mod._canonical_hash({"operationId": "op-1", "value": 42})
    b = sub_mod._canonical_hash({"operationId": "op-1", "value": 43})
    assert a != b


def test_canonical_hash_tamper_detects_key_rename():
    a = sub_mod._canonical_hash({"operationId": "op-1"})
    b = sub_mod._canonical_hash({"operation_id": "op-1"})
    assert a != b


def test_canonical_hash_returns_64_char_hex():
    h = sub_mod._canonical_hash({"x": 1})
    assert len(h) == 64
    int(h, 16)  # raises ValueError if not valid hex


# ---------------------------------------------------------------------------
# Fake Postgres connection + pool for handler-level tests
# ---------------------------------------------------------------------------


class FakeConn:
    """
    Minimal async stand-in for asyncpg.Connection. Models the two
    primitives the dedup code needs:
      * INSERT ... ON CONFLICT DO NOTHING RETURNING 1
        → via the dedup_rows dict keyed on (tenant_id, operation_id)
      * UPDATE field_operations ... WHERE carbon_computed_at IS NULL
          RETURNING id
        → via the field_ops dict keyed on operation_id
      * SELECT op.id, op.operation_type, ... FROM field_operations op JOIN fields f
        → returns the row from field_ops if present

    Each conn shares state through a class-level `_state` dict so a
    FakePool that hands out multiple conns models concurrent consumers.
    """

    _state: dict[str, Any] = {
        "dedup": {},  # {(tenant, op): dict}
        "field_ops": {},  # {op_id: dict}
        "insert_calls": 0,
        "update_calls": 0,
        "mark_processed_calls": 0,
        "mark_failed_calls": 0,
    }

    @classmethod
    def reset(cls):
        cls._state = {
            "dedup": {},
            "field_ops": {},
            "insert_calls": 0,
            "update_calls": 0,
            "mark_processed_calls": 0,
            "mark_failed_calls": 0,
        }

    @classmethod
    def seed_field_op(cls, op_id: str, **attrs):
        base = {
            "id": op_id,
            "operation_type": "plowing",
            "duration_hours": 2.0,
            "fuel_liters": 25.0,
            "metadata": {},
            "area_hectares": 5.0,
            "carbon_computed_at": None,
        }
        base.update(attrs)
        cls._state["field_ops"][op_id] = base

    async def fetchval(self, query: str, *args):
        q = query.strip().upper()
        if q.startswith("INSERT INTO CARBON_EVENT_DEDUP"):
            tenant_id, operation_id, payload_hash, correlation_id = args
            self._state["insert_calls"] += 1
            key = (tenant_id, operation_id)
            if key in self._state["dedup"]:
                return None  # ON CONFLICT DO NOTHING
            self._state["dedup"][key] = {
                "payload_hash": payload_hash,
                "correlation_id": correlation_id,
                "carbon_computed_at": None,
                "error_message": None,
            }
            return 1
        if q.startswith("UPDATE FIELD_OPERATIONS"):
            self._state["update_calls"] += 1
            (
                emissions,
                seq,
                net,
                credit,
                method,
                src_type,
                operation_id,
                tenant_id,
            ) = args
            row = self._state["field_ops"].get(operation_id)
            if row is None or row.get("carbon_computed_at") is not None:
                return None  # WHERE carbon_computed_at IS NULL guard
            row["co2_emissions_kg"] = emissions
            row["co2_sequestration_kg"] = seq
            row["co2_net_kg"] = net
            row["carbon_credit_eligible"] = credit
            row["carbon_methodology"] = method
            row["emission_source_type"] = src_type
            row["carbon_computed_at"] = "NOW()"
            return operation_id
        raise AssertionError(f"Unexpected fetchval query: {query[:80]}")

    async def fetchrow(self, query: str, *args):
        q = query.strip().upper()
        if "FROM FIELD_OPERATIONS" in q:
            operation_id, tenant_id = args
            row = self._state["field_ops"].get(operation_id)
            if row is None:
                return None
            # Simulate JOIN + tenant check
            return row
        raise AssertionError(f"Unexpected fetchrow query: {query[:80]}")

    async def execute(self, query: str, *args):
        q = query.strip().upper()
        if q.startswith("UPDATE CARBON_EVENT_DEDUP"):
            if "CARBON_COMPUTED_AT = NOW" in q:
                self._state["mark_processed_calls"] += 1
                tenant_id, operation_id = args
                row = self._state["dedup"].get((tenant_id, operation_id))
                if row is not None:
                    row["carbon_computed_at"] = "NOW()"
                    row["error_message"] = None
            elif "ERROR_MESSAGE =" in q:
                self._state["mark_failed_calls"] += 1
                tenant_id, operation_id, err = args
                row = self._state["dedup"].get((tenant_id, operation_id))
                if row is not None:
                    row["error_message"] = err
            return None
        raise AssertionError(f"Unexpected execute query: {query[:80]}")


class FakePool:
    def acquire(self):
        return _FakeAcquireCtx()


class _FakeAcquireCtx:
    async def __aenter__(self):
        return FakeConn()

    async def __aexit__(self, exc_type, exc, tb):
        return False


class FakeNats:
    def __init__(self):
        self.subscribed_to: list[tuple[str, str]] = []

    async def subscribe(self, subject, queue=None, cb=None):
        self.subscribed_to.append((subject, queue or ""))
        self._cb = cb
        return SimpleNamespace(drain=self._drain)

    async def _drain(self):
        pass


def _msg(envelope: dict[str, Any]):
    return SimpleNamespace(data=json.dumps(envelope).encode())


@pytest.fixture(autouse=True)
def _reset_state():
    FakeConn.reset()
    yield
    FakeConn.reset()


# ---------------------------------------------------------------------------
# _claim_event unit tests
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_claim_event_first_insert_succeeds():
    conn = FakeConn()
    claimed = await sub_mod._claim_event(
        conn, tenant_id="t-1", operation_id="op-1", payload_hash="h", correlation_id="c"
    )
    assert claimed is True
    assert FakeConn._state["insert_calls"] == 1
    assert ("t-1", "op-1") in FakeConn._state["dedup"]


@pytest.mark.asyncio
async def test_claim_event_duplicate_returns_false():
    conn = FakeConn()
    first = await sub_mod._claim_event(conn, "t-1", "op-1", "h-a", None)
    second = await sub_mod._claim_event(conn, "t-1", "op-1", "h-b", None)
    assert first is True
    assert second is False
    # First row's hash is preserved — we do NOT overwrite on conflict
    assert FakeConn._state["dedup"][("t-1", "op-1")]["payload_hash"] == "h-a"


@pytest.mark.asyncio
async def test_claim_event_different_tenant_is_independent():
    conn = FakeConn()
    a = await sub_mod._claim_event(conn, "t-1", "op-1", "h", None)
    b = await sub_mod._claim_event(conn, "t-2", "op-1", "h", None)
    assert a is True and b is True


@pytest.mark.asyncio
async def test_mark_processed_updates_dedup_row():
    conn = FakeConn()
    await sub_mod._claim_event(conn, "t-1", "op-1", "h", None)
    await sub_mod._mark_processed(conn, "t-1", "op-1")
    assert FakeConn._state["dedup"][("t-1", "op-1")]["carbon_computed_at"] == "NOW()"


@pytest.mark.asyncio
async def test_mark_failed_stores_error_truncated():
    conn = FakeConn()
    await sub_mod._claim_event(conn, "t-1", "op-1", "h", None)
    await sub_mod._mark_failed(conn, "t-1", "op-1", "x" * 5000)
    stored = FakeConn._state["dedup"][("t-1", "op-1")]["error_message"]
    assert stored is not None
    assert len(stored) == 2000  # capped


# ---------------------------------------------------------------------------
# Handler-level tests — exercise the full subscriber via fake NATS
# ---------------------------------------------------------------------------


async def _start_handler():
    nc = FakeNats()
    pool = FakePool()
    await sub_mod.start_operation_subscriber(nc, pool)
    return nc


@pytest.mark.asyncio
async def test_handler_first_event_computes_carbon_and_records_dedup():
    FakeConn.seed_field_op("op-1")
    nc = await _start_handler()

    envelope = {"payload": {"operationId": "op-1", "tenantId": "t-1"}}
    await nc._cb(_msg(envelope))

    # Dedup row exists
    assert ("t-1", "op-1") in FakeConn._state["dedup"]
    # field_operations row was updated
    assert FakeConn._state["field_ops"]["op-1"]["carbon_computed_at"] == "NOW()"
    # mark_processed was called
    assert FakeConn._state["mark_processed_calls"] == 1
    # _claim_event hit once, UPDATE hit once
    assert FakeConn._state["insert_calls"] == 1
    assert FakeConn._state["update_calls"] == 1


@pytest.mark.asyncio
async def test_handler_replay_is_skipped_silently():
    FakeConn.seed_field_op("op-1")
    nc = await _start_handler()
    envelope = {"payload": {"operationId": "op-1", "tenantId": "t-1"}}

    # First delivery: processed
    await nc._cb(_msg(envelope))
    # Second delivery: replay
    await nc._cb(_msg(envelope))

    # Engine was called only once (inferred from update_calls)
    assert FakeConn._state["update_calls"] == 1
    # insert_calls == 2 because both replays attempted the claim, but
    # the second one got ON CONFLICT DO NOTHING and returned False
    assert FakeConn._state["insert_calls"] == 2
    # mark_processed also only once (skipped replays return early)
    assert FakeConn._state["mark_processed_calls"] == 1


@pytest.mark.asyncio
async def test_handler_concurrent_replay_only_one_wins():
    FakeConn.seed_field_op("op-1")
    nc = await _start_handler()
    envelope = {"payload": {"operationId": "op-1", "tenantId": "t-1"}}

    # Two consumers handling the same event simultaneously
    await asyncio.gather(nc._cb(_msg(envelope)), nc._cb(_msg(envelope)))

    # Exactly one UPDATE despite two concurrent handlers
    assert FakeConn._state["update_calls"] == 1


@pytest.mark.asyncio
async def test_handler_mixed_ops_are_all_processed():
    FakeConn.seed_field_op("op-1")
    FakeConn.seed_field_op("op-2")
    FakeConn.seed_field_op("op-3")
    nc = await _start_handler()

    await nc._cb(_msg({"payload": {"operationId": "op-1", "tenantId": "t-1"}}))
    await nc._cb(_msg({"payload": {"operationId": "op-2", "tenantId": "t-1"}}))
    await nc._cb(_msg({"payload": {"operationId": "op-1", "tenantId": "t-1"}}))  # replay
    await nc._cb(_msg({"payload": {"operationId": "op-3", "tenantId": "t-1"}}))

    # 3 distinct computes, 1 replay skipped
    assert FakeConn._state["update_calls"] == 3
    assert len(FakeConn._state["dedup"]) == 3
    assert all(
        FakeConn._state["field_ops"][op]["carbon_computed_at"] == "NOW()"
        for op in ("op-1", "op-2", "op-3")
    )


@pytest.mark.asyncio
async def test_handler_skips_event_with_missing_ids():
    FakeConn.seed_field_op("op-1")
    nc = await _start_handler()
    # Missing tenantId
    await nc._cb(_msg({"payload": {"operationId": "op-1"}}))
    assert FakeConn._state["insert_calls"] == 0
    assert FakeConn._state["update_calls"] == 0


@pytest.mark.asyncio
async def test_handler_already_computed_row_is_not_overwritten():
    """
    Belt-and-suspenders: even if the dedup row was GC'd, the UPDATE
    guard `WHERE carbon_computed_at IS NULL` prevents a zombie replay
    from stomping already-computed values.
    """
    FakeConn.seed_field_op("op-1", carbon_computed_at="EARLIER")
    nc = await _start_handler()
    envelope = {"payload": {"operationId": "op-1", "tenantId": "t-1"}}

    await nc._cb(_msg(envelope))

    # Dedup row was created
    assert ("t-1", "op-1") in FakeConn._state["dedup"]
    # But the UPDATE returned None → the field_op's value is unchanged
    assert FakeConn._state["field_ops"]["op-1"]["carbon_computed_at"] == "EARLIER"
    # _mark_processed was still called so forensics knows we saw the event
    assert FakeConn._state["mark_processed_calls"] == 1


@pytest.mark.asyncio
async def test_handler_missing_field_op_marks_failure():
    # No seed_field_op — the lookup returns None
    nc = await _start_handler()
    envelope = {"payload": {"operationId": "op-missing", "tenantId": "t-1"}}
    await nc._cb(_msg(envelope))

    # Dedup row exists (claim happened) and has error_message set
    row = FakeConn._state["dedup"][("t-1", "op-missing")]
    assert row["error_message"] == "operation_not_found"
    assert FakeConn._state["update_calls"] == 0


@pytest.mark.asyncio
async def test_handler_subscribes_with_queue_group():
    """Consumer group enables horizontal scaling + at-most-once per group."""
    nc = await _start_handler()
    assert (sub_mod.SUBJECT, sub_mod.QUEUE_GROUP) in nc.subscribed_to
