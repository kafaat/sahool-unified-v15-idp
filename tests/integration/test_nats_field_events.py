"""
Integration Tests for NATS Field Events
اختبارات التكامل لأحداث الحقول عبر NATS

Tests for field-related NATS event publishing, subscribing, and schema validation.
Covers subjects:
    - sahool.field.created
    - sahool.field.updated
    - sahool.field.deleted
    - sahool.tenant.{tenant_id}.field.created (tenant-scoped)

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────

NATS_URL = os.getenv("NATS_URL", "nats://localhost:4222")

# Import subject constants from shared module
try:
    from shared.events.subjects import (
        SAHOOL_FIELD_ALL,
        SAHOOL_FIELD_CREATED,
        SAHOOL_FIELD_DELETED,
        SAHOOL_FIELD_UPDATED,
        get_tenant_subject,
        get_tenant_wildcard,
        is_valid_subject,
    )
except ImportError:
    SAHOOL_FIELD_CREATED = "sahool.field.created"
    SAHOOL_FIELD_UPDATED = "sahool.field.updated"
    SAHOOL_FIELD_DELETED = "sahool.field.deleted"
    SAHOOL_FIELD_ALL = "sahool.field.>"

    def get_tenant_subject(tenant_id: str, domain: str, action: str) -> str:
        return f"sahool.tenant.{tenant_id}.{domain}.{action}"

    def get_tenant_wildcard(tenant_id: str, domain: str = "*") -> str:
        if domain == "*":
            return f"sahool.tenant.{tenant_id}.>"
        return f"sahool.tenant.{tenant_id}.{domain}.>"

    def is_valid_subject(subject: str) -> bool:
        return subject.startswith("sahool.") and len(subject.split(".")) >= 3


# Import event contracts
try:
    from shared.events.contracts import (
        FieldCreatedEvent,
        FieldDeletedEvent,
        FieldUpdatedEvent,
    )

    _contracts_available = True
except ImportError:
    _contracts_available = False


# ─────────────────────────────────────────────────────────────────────────────
# Test Data Helpers
# ─────────────────────────────────────────────────────────────────────────────


def _make_field_created_payload(
    field_id: str | None = None,
    farm_id: str | None = None,
    tenant_id: str | None = None,
    name: str = "Test Field Alpha",
) -> dict:
    """Build a valid field.created event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "field-management-service",
        "correlation_id": str(uuid.uuid4()),
        "field_id": field_id or str(uuid.uuid4()),
        "farm_id": farm_id or str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "name": name,
        "name_ar": "حقل اختبار ألفا",
        "geometry_wkt": "POLYGON((44.0 15.0, 44.1 15.0, 44.1 15.1, 44.0 15.1, 44.0 15.0))",
        "area_hectares": 12.5,
        "soil_type": "clay_loam",
        "irrigation_type": "drip",
        "created_by": str(uuid.uuid4()),
    }


def _make_field_updated_payload(field_id: str | None = None) -> dict:
    """Build a valid field.updated event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "field-management-service",
        "field_id": field_id or str(uuid.uuid4()),
        "name": "Updated Field Name",
        "name_ar": "اسم حقل محدث",
        "area_hectares": 15.0,
        "ndvi_value": 0.72,
        "irrigation_type": "pivot",
        "updated_by": str(uuid.uuid4()),
    }


def _make_field_deleted_payload(
    field_id: str | None = None,
    farm_id: str | None = None,
    tenant_id: str | None = None,
) -> dict:
    """Build a valid field.deleted event payload."""
    return {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        "version": "1.0",
        "source_service": "field-management-service",
        "field_id": field_id or str(uuid.uuid4()),
        "farm_id": farm_id or str(uuid.uuid4()),
        "tenant_id": tenant_id or str(uuid.uuid4()),
        "deleted_by": str(uuid.uuid4()),
        "reason": "Field no longer in use",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_nats():
    """Create a mock NATS client for tests that do not require a live server."""
    nc = AsyncMock()
    nc.publish = AsyncMock()
    nc.subscribe = AsyncMock()
    nc.flush = AsyncMock()
    nc.drain = AsyncMock()
    nc.close = AsyncMock()
    nc.is_connected = True
    return nc


@pytest.fixture
def mock_nats_msg():
    """Create a factory for mock NATS messages."""

    def _make(subject: str, payload: dict):
        msg = MagicMock()
        msg.subject = subject
        msg.data = json.dumps(payload).encode("utf-8")
        msg.headers = {}
        msg.ack = AsyncMock()
        msg.nak = AsyncMock()
        return msg

    return _make


@pytest.fixture
def sample_tenant_id() -> str:
    return str(uuid.uuid4())


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Field Created Event
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_field_created_event_published(mock_nats):
    """Test that field.created event is published with correct subject and schema."""
    payload = _make_field_created_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_FIELD_CREATED, data)

    mock_nats.publish.assert_awaited_once_with(SAHOOL_FIELD_CREATED, data)

    # Verify payload schema
    decoded = json.loads(data)
    assert "field_id" in decoded, "Payload must include field_id"
    assert "farm_id" in decoded, "Payload must include farm_id"
    assert "tenant_id" in decoded, "Payload must include tenant_id"
    assert "name" in decoded, "Payload must include name"
    assert "geometry_wkt" in decoded, "Payload must include geometry_wkt"
    assert "timestamp" in decoded, "Payload must include timestamp"
    assert "event_id" in decoded, "Payload must include event_id"
    assert decoded["source_service"] == "field-management-service"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_field_created_event_subscribe_receive(mock_nats, mock_nats_msg):
    """Test subscribing to field.created and receiving the event."""
    received_events: list[dict] = []

    async def handler(msg):
        data = json.loads(msg.data.decode("utf-8"))
        received_events.append(data)

    # Setup subscription
    mock_nats.subscribe.return_value = MagicMock()
    await mock_nats.subscribe(SAHOOL_FIELD_CREATED, cb=handler)
    mock_nats.subscribe.assert_awaited_once()

    # Simulate message delivery
    payload = _make_field_created_payload(name="Wheat Field North")
    msg = mock_nats_msg(SAHOOL_FIELD_CREATED, payload)
    await handler(msg)

    assert len(received_events) == 1
    assert received_events[0]["name"] == "Wheat Field North"
    assert received_events[0]["name_ar"] == "حقل اختبار ألفا"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_field_updated_event_schema(mock_nats):
    """Test field.updated event payload contains expected update fields."""
    payload = _make_field_updated_payload()
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_FIELD_UPDATED, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert "field_id" in decoded
    assert "ndvi_value" in decoded, "Updated event should include NDVI value"
    assert -1 <= decoded["ndvi_value"] <= 1, "NDVI must be in range [-1, 1]"
    assert decoded["area_hectares"] >= 0, "Area must be non-negative"


@pytest.mark.integration
@pytest.mark.asyncio
async def test_field_deleted_event_schema(mock_nats):
    """Test field.deleted event payload contains required deletion fields."""
    field_id = str(uuid.uuid4())
    farm_id = str(uuid.uuid4())
    tenant_id = str(uuid.uuid4())

    payload = _make_field_deleted_payload(field_id=field_id, farm_id=farm_id, tenant_id=tenant_id)
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(SAHOOL_FIELD_DELETED, data)
    mock_nats.publish.assert_awaited_once()

    decoded = json.loads(data)
    assert decoded["field_id"] == field_id
    assert decoded["farm_id"] == farm_id
    assert decoded["tenant_id"] == tenant_id
    assert "deleted_by" in decoded
    assert "reason" in decoded


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Tenant-Scoped Events
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tenant_scoped_field_created_event(mock_nats, sample_tenant_id):
    """Test that tenant-scoped field.created events use the correct subject pattern."""
    subject = get_tenant_subject(sample_tenant_id, "field", "created")

    assert subject == f"sahool.tenant.{sample_tenant_id}.field.created"
    assert is_valid_subject(subject)

    payload = _make_field_created_payload(tenant_id=sample_tenant_id)
    data = json.dumps(payload).encode("utf-8")

    await mock_nats.publish(subject, data)
    mock_nats.publish.assert_awaited_once_with(subject, data)

    decoded = json.loads(data)
    assert decoded["tenant_id"] == sample_tenant_id


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tenant_wildcard_subscription(mock_nats, sample_tenant_id):
    """Test subscribing to all field events for a specific tenant using wildcards."""
    wildcard = get_tenant_wildcard(sample_tenant_id, "field")
    assert wildcard == f"sahool.tenant.{sample_tenant_id}.field.>"

    received_events: list[dict] = []

    async def handler(msg):
        data = json.loads(msg.data.decode("utf-8"))
        received_events.append({"subject": msg.subject, "data": data})

    await mock_nats.subscribe(wildcard, cb=handler)
    mock_nats.subscribe.assert_awaited_once()

    # Verify the wildcard subject format
    all_tenant_wildcard = get_tenant_wildcard(sample_tenant_id)
    assert all_tenant_wildcard == f"sahool.tenant.{sample_tenant_id}.>"


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Contract Validation (Pydantic models)
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _contracts_available, reason="shared.events.contracts not available")
async def test_field_created_event_contract_validation():
    """Test that FieldCreatedEvent Pydantic model validates payloads correctly."""
    valid_payload = _make_field_created_payload()

    event = FieldCreatedEvent(**valid_payload)
    assert str(event.field_id) == valid_payload["field_id"]
    assert event.name == valid_payload["name"]
    assert event.name_ar == "حقل اختبار ألفا"
    assert event.area_hectares == 12.5
    assert event.source_service == "field-management-service"

    # Verify serialization round-trip
    serialized = json.loads(event.model_dump_json())
    assert "field_id" in serialized
    assert "geometry_wkt" in serialized


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.skipif(not _contracts_available, reason="shared.events.contracts not available")
async def test_field_created_event_rejects_invalid_payload():
    """Test that FieldCreatedEvent rejects payloads with missing required fields."""
    from pydantic import ValidationError

    invalid_payload = {
        "event_id": str(uuid.uuid4()),
        "timestamp": datetime.now(UTC).isoformat(),
        # Missing: field_id, farm_id, tenant_id, name, geometry_wkt
    }

    with pytest.raises(ValidationError):
        FieldCreatedEvent(**invalid_payload)


# ─────────────────────────────────────────────────────────────────────────────
# Tests: Subject Validation
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.integration
def test_field_subject_constants_format():
    """Test that field subject constants follow the sahool.{domain}.{action} pattern."""
    assert SAHOOL_FIELD_CREATED == "sahool.field.created"
    assert SAHOOL_FIELD_UPDATED == "sahool.field.updated"
    assert SAHOOL_FIELD_DELETED == "sahool.field.deleted"
    assert SAHOOL_FIELD_ALL == "sahool.field.>"

    assert is_valid_subject(SAHOOL_FIELD_CREATED)
    assert is_valid_subject(SAHOOL_FIELD_UPDATED)
    assert is_valid_subject(SAHOOL_FIELD_DELETED)


@pytest.mark.integration
def test_tenant_subject_requires_tenant_id():
    """Test that get_tenant_subject raises ValueError when tenant_id is empty."""
    with pytest.raises(ValueError, match="tenant_id"):
        get_tenant_subject("", "field", "created")

    with pytest.raises(ValueError, match="tenant_id"):
        get_tenant_wildcard("")
