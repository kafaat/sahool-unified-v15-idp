"""
Unit tests for the Phase 2 geofence → FieldOperation auto-draft bridge.

Tests cover:

* Equipment type → operation type classification
* Skip rules (wrong alert type, wrong zone type, no field mapping)
* Payload shape (matches field-management-service's
  ``CreateFieldOperationDto``)
* NATS publish of ``sahool.tenant.{tid}.field_operation.auto_drafted``
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import UTC, datetime

import pytest

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
_BRIDGE_PATH = os.path.join(
    _REPO_ROOT,
    "apps",
    "services",
    "equipment-service",
    "src",
    "geofence_autoop",
    "bridge.py",
)
_spec = importlib.util.spec_from_file_location("phase2_geofence_autoop", _BRIDGE_PATH)
assert _spec and _spec.loader
_bridge_mod = importlib.util.module_from_spec(_spec)
sys.modules["phase2_geofence_autoop"] = _bridge_mod
_spec.loader.exec_module(_bridge_mod)

EQUIPMENT_TO_OPERATION = _bridge_mod.EQUIPMENT_TO_OPERATION
GeofenceAutoOperationBridge = _bridge_mod.GeofenceAutoOperationBridge
GeofenceEvent = _bridge_mod.GeofenceEvent
classify_operation = _bridge_mod.classify_operation
AutoOperationResult = _bridge_mod.AutoOperationResult


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "eq_type,expected",
    [
        ("tractor", "plowing"),
        ("TRACTOR", "plowing"),  # Case-insensitive
        ("harvester", "harvesting"),
        ("sprayer", "spraying"),
        ("drone", "scouting"),
        ("pump", "irrigation"),
        ("pivot", "irrigation"),
        ("dragonfly-mk2", "other"),  # Unknown → fallback
    ],
)
def test_classify_operation(eq_type, expected):
    assert classify_operation(eq_type) == expected


def test_equipment_to_operation_keys_are_canonical():
    # All canonical field-management-service operation types must be
    # producible from the equipment → operation map
    canonical = {"plowing", "harvesting", "spraying", "scouting", "irrigation", "other"}
    assert set(EQUIPMENT_TO_OPERATION.values()).issubset(canonical)


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------


class FakeNats:
    def __init__(self):
        self.published: list[tuple[str, bytes]] = []

    async def publish(self, subject: str, payload: bytes):
        self.published.append((subject, payload))


@pytest.fixture
def bridge() -> GeofenceAutoOperationBridge:
    return GeofenceAutoOperationBridge(
        field_management_url="http://fake:0",
        nats_client=FakeNats(),
        timeout=0.1,
    )


def _event(**overrides) -> GeofenceEvent:
    base = GeofenceEvent(
        equipment_id="eq_tractor_1",
        tenant_id="t-1",
        geofence_id="gf_field_1",
        geofence_type="field",
        alert_type="entry",
        lat=24.5,
        lng=46.7,
        timestamp=datetime(2026, 4, 11, 7, 30, tzinfo=UTC),
        field_id="F-1",
        equipment_type="tractor",
        equipment_name="John Deere 8R",
    )
    for k, v in overrides.items():
        setattr(base, k, v)
    return base


# ---------------------------------------------------------------------------
# Skip rules
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skip_exit_alert(bridge: GeofenceAutoOperationBridge):
    result = await bridge.handle(_event(alert_type="exit"))
    assert result.handled is False
    assert result.reason == "skipped"
    assert "not actionable" in (result.error or "")


@pytest.mark.asyncio
async def test_skip_restricted_zone(bridge: GeofenceAutoOperationBridge):
    result = await bridge.handle(_event(geofence_type="restricted"))
    assert result.handled is False
    assert result.reason == "skipped"
    assert "not a field zone" in (result.error or "")


@pytest.mark.asyncio
async def test_skip_no_field_mapping(bridge: GeofenceAutoOperationBridge):
    result = await bridge.handle(_event(field_id=None))
    assert result.handled is False
    assert result.reason == "skipped"
    assert "field_id mapping" in (result.error or "")


@pytest.mark.asyncio
async def test_speeding_alert_is_skipped(bridge: GeofenceAutoOperationBridge):
    result = await bridge.handle(_event(alert_type="speeding"))
    assert result.reason == "skipped"


# ---------------------------------------------------------------------------
# Payload shape
# ---------------------------------------------------------------------------


def test_build_payload_matches_dto(bridge: GeofenceAutoOperationBridge):
    event = _event()
    payload = bridge._build_payload(event, "plowing")
    # Required DTO fields present
    assert payload["operationType"] == "plowing"
    assert "performedAt" in payload
    assert payload["equipmentId"] == "eq_tractor_1"
    assert payload["equipmentName"] == "John Deere 8R"
    assert "Auto-drafted" in payload["notes"]
    # No unknown fields (field-management-service uses whitelist=true)
    allowed = {
        "operationType",
        "performedAt",
        "endedAt",
        "durationHours",
        "costAmount",
        "costCurrency",
        "cropSeasonId",
        "equipmentId",
        "equipmentName",
        "equipmentNameAr",
        "notes",
        "fuelLiters",
        "fuelCost",
        "laborHours",
        "laborCost",
        "materialsCost",
        "overheadCost",
        "otherCost",
        "taxAmount",
        "taxRate",
        "exchangeRate",
        "baseCurrency",
    }
    assert set(payload.keys()).issubset(allowed)


def test_build_payload_carries_crop_season(bridge: GeofenceAutoOperationBridge):
    payload = bridge._build_payload(
        _event(crop_season_id="CS-1"), "irrigation"
    )
    assert payload["cropSeasonId"] == "CS-1"


def test_build_payload_truncates_long_equipment_name(
    bridge: GeofenceAutoOperationBridge,
):
    payload = bridge._build_payload(
        _event(equipment_name="A" * 1000), "plowing"
    )
    # Must stay within the 255-char VARCHAR limit
    assert len(payload["equipmentName"]) <= 255


# ---------------------------------------------------------------------------
# NATS publish
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_publish_drafted_event_emits_tenant_scoped_subject(
    bridge: GeofenceAutoOperationBridge,
):
    event = _event()
    result = AutoOperationResult(
        handled=True,
        reason="drafted",
        operation_id="op-42",
        operation_type="plowing",
        field_id="F-1",
    )
    await bridge._publish_drafted_event(event, result)

    published = bridge.nats_client.published  # type: ignore[union-attr]
    assert len(published) == 1
    subject, body = published[0]
    assert subject == "sahool.tenant.t-1.field_operation.auto_drafted"
    decoded = json.loads(body)
    assert decoded["operation_id"] == "op-42"
    assert decoded["field_id"] == "F-1"
    assert decoded["operation_type"] == "plowing"
    assert decoded["source"] == "geofence_auto"
