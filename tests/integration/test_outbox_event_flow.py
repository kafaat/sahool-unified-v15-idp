"""
SAHOOL Event Flow Integration Tests
Tests for schema validation and outbox event flow
"""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest


class TestSchemaRegistry:
    """Test schema registry loading and validation"""

    def test_schema_registry_loads(self):
        """Registry loads all schemas from disk"""
        from shared.libs.events.schema_registry import SchemaRegistry

        registry = SchemaRegistry.load()
        schemas = registry.list_schemas()

        assert len(schemas) > 0
        assert "events.field.created:v1" in registry

    def test_schema_entry_lookup(self):
        """Can look up schema entries by ref"""
        from shared.libs.events.schema_registry import SchemaRegistry

        registry = SchemaRegistry.load()
        entry = registry.entry("events.field.created:v1")

        assert entry.ref == "events.field.created:v1"
        assert entry.topic == "field.created"
        assert entry.version == 1
        assert entry.owner == "field_suite"

    def test_unknown_schema_raises(self):
        """Unknown schema_ref raises KeyError"""
        from shared.libs.events.schema_registry import SchemaRegistry

        registry = SchemaRegistry.load()

        with pytest.raises(KeyError, match="Unknown schema_ref"):
            registry.entry("events.nonexistent:v1")

    def test_list_by_owner(self):
        """Can list schemas by owner"""
        from shared.libs.events.schema_registry import SchemaRegistry

        registry = SchemaRegistry.load()
        field_schemas = registry.list_by_owner("field_suite")

        assert (
            len(field_schemas) >= 3
        )  # field.created, field.updated, farm.created, crop.planted
        assert all(s.owner == "field_suite" for s in field_schemas)


class TestSchemaValidation:
    """Test payload validation against schemas"""

    @pytest.fixture
    def registry(self):
        from shared.libs.events.schema_registry import SchemaRegistry

        return SchemaRegistry.load()

    def test_valid_field_created_payload(self, registry):
        """Valid payload passes validation"""
        pytest.importorskip("jsonschema")

        payload = {
            "field_id": str(uuid4()),
            "farm_id": str(uuid4()),
            "name": "Test Field",
            "geometry_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            "created_at": datetime.now(UTC).isoformat(),
        }

        # Should not raise
        registry.validate("events.field.created:v1", payload)

    def test_missing_required_field_fails(self, registry):
        """Missing required field fails validation"""
        jsonschema = pytest.importorskip("jsonschema")

        payload = {
            "field_id": str(uuid4()),
            "farm_id": str(uuid4()),
            # name is missing
            "geometry_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            "created_at": datetime.now(UTC).isoformat(),
        }

        with pytest.raises(jsonschema.ValidationError):
            registry.validate("events.field.created:v1", payload)

    def test_invalid_uuid_format_fails(self, registry):
        """Invalid UUID format fails validation"""
        jsonschema = pytest.importorskip("jsonschema")

        payload = {
            "field_id": "not-a-uuid",  # Invalid
            "farm_id": str(uuid4()),
            "name": "Test Field",
            "geometry_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            "created_at": datetime.now(UTC).isoformat(),
        }

        with pytest.raises(jsonschema.ValidationError):
            registry.validate("events.field.created:v1", payload)

    def test_additional_properties_rejected(self, registry):
        """Additional properties are rejected"""
        jsonschema = pytest.importorskip("jsonschema")

        payload = {
            "field_id": str(uuid4()),
            "farm_id": str(uuid4()),
            "name": "Test Field",
            "geometry_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            "created_at": datetime.now(UTC).isoformat(),
            "unexpected_field": "should fail",  # Not in schema
        }

        with pytest.raises(jsonschema.ValidationError):
            registry.validate("events.field.created:v1", payload)


class TestEventEnvelope:
    """Test event envelope creation"""

    def test_envelope_creation(self):
        """EventEnvelope creates with all required fields"""
        from shared.libs.events.envelope import EventEnvelope

        tenant_id = uuid4()
        correlation_id = uuid4()

        envelope = EventEnvelope(
            event_type="field.created",
            tenant_id=tenant_id,
            correlation_id=correlation_id,
            schema_ref="events.field.created:v1",
            producer="field_suite",
            payload={"test": "data"},
        )

        assert envelope.event_type == "field.created"
        assert envelope.tenant_id == tenant_id
        assert envelope.correlation_id == correlation_id
        assert envelope.event_version == 1
        assert envelope.event_id is not None
        assert envelope.occurred_at is not None

    def test_envelope_to_json_dict(self):
        """EventEnvelope serializes to JSON dict"""
        from shared.libs.events.envelope import EventEnvelope

        envelope = EventEnvelope(
            event_type="field.created",
            tenant_id=uuid4(),
            correlation_id=uuid4(),
            schema_ref="events.field.created:v1",
            producer="field_suite",
            payload={"field_id": "123"},
        )

        data = envelope.to_json_dict()

        assert isinstance(data["event_id"], str)
        assert isinstance(data["tenant_id"], str)
        assert isinstance(data["occurred_at"], str)
        assert data["event_type"] == "field.created"


class TestEventCatalogGeneration:
    """Test event catalog generator"""

    def test_catalog_generator_runs(self):
        """Catalog generator runs without errors"""
        from tools.events.generate_catalog import generate_catalog

        catalog = generate_catalog()

        assert "# Event Catalog" in catalog
        assert "events.field.created:v1" in catalog
        assert "field_suite" in catalog


class TestProducerHelpers:
    """Test producer helper functions"""

    def test_get_registry(self):
        """get_registry returns singleton"""
        from shared.libs.events.producer import get_registry

        reg1 = get_registry()
        reg2 = get_registry()

        assert reg1 is reg2

    def test_validate_payload(self):
        """validate_payload validates without enqueuing"""
        pytest.importorskip("jsonschema")
        from shared.libs.events.producer import validate_payload

        valid = validate_payload(
            "events.field.created:v1",
            {
                "field_id": str(uuid4()),
                "farm_id": str(uuid4()),
                "name": "Test",
                "geometry_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
                "created_at": datetime.now(UTC).isoformat(),
            },
        )

        assert valid is True
