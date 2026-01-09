"""
Unit Tests for Contracts Event Base Module
Tests event validation against JSON schemas
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

import pytest

from shared.contracts.events.base import BaseEvent, EventMetadata, _schema_cache


@dataclass
class SampleEventWithSchema(BaseEvent):
    """Sample event with a valid schema path"""

    EVENT_TYPE = "field.created"
    EVENT_VERSION = "1.0.0"
    SCHEMA_PATH = "field.created.v1.json"

    field_id: UUID = None
    name: str = ""
    geometry: dict[str, Any] = field(default_factory=dict)
    area_hectares: float = 0.0

    def _payload_to_dict(self) -> dict[str, Any]:
        return {
            "field_id": str(self.field_id),
            "tenant_id": str(self.tenant_id),
            "name": self.name,
            "geometry": self.geometry,
            "area_hectares": self.area_hectares,
        }


@dataclass
class SampleEventNoSchema(BaseEvent):
    """Sample event without a schema path"""

    EVENT_TYPE = "test.no_schema"
    EVENT_VERSION = "1.0.0"
    SCHEMA_PATH = ""

    test_field: str = ""

    def _payload_to_dict(self) -> dict[str, Any]:
        return {"test_field": self.test_field}


@dataclass
class SampleEventInvalidSchema(BaseEvent):
    """Sample event with a non-existent schema path"""

    EVENT_TYPE = "test.invalid"
    EVENT_VERSION = "1.0.0"
    SCHEMA_PATH = "non_existent_schema.json"

    test_field: str = ""

    def _payload_to_dict(self) -> dict[str, Any]:
        return {"test_field": self.test_field}


class TestEventValidation:
    """Tests for BaseEvent.validate() method"""

    def test_validate_no_schema_returns_true(self):
        """Test that validate() returns True when SCHEMA_PATH is empty"""
        event = SampleEventNoSchema(
            tenant_id=uuid4(),
            test_field="test_value",
        )
        assert event.validate() is True

    def test_validate_with_valid_event_data(self):
        """Test that validate() returns True for valid event data"""
        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Test Field",
            geometry={"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
            area_hectares=10.5,
        )
        assert event.validate() is True

    def test_validate_with_missing_schema_file(self):
        """Test that validate() raises FileNotFoundError for missing schema"""
        event = SampleEventInvalidSchema(
            tenant_id=uuid4(),
            test_field="test_value",
        )
        with pytest.raises(FileNotFoundError) as exc_info:
            event.validate()
        assert "non_existent_schema.json" in str(exc_info.value)

    def test_validate_with_invalid_event_data(self):
        """Test that validate() raises ValidationError for invalid data"""
        from jsonschema import ValidationError

        # Create event with invalid geometry type (should be Polygon or MultiPolygon)
        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="",  # Empty name - minimum length is 1
            geometry={"type": "InvalidType", "coordinates": []},
            area_hectares=-1.0,  # Negative area - minimum is 0
        )

        with pytest.raises(ValidationError):
            event.validate()


class TestSchemaLoading:
    """Tests for schema loading and caching"""

    def test_schema_cache_stores_loaded_schemas(self):
        """Test that schemas are cached after first load"""
        # Clear cache first
        _schema_cache.clear()

        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Test Field",
            geometry={"type": "Polygon", "coordinates": [[[0, 0], [1, 0], [1, 1], [0, 0]]]},
            area_hectares=10.5,
        )

        # First validation should load schema
        event.validate()
        assert "field.created.v1.json" in _schema_cache

    def test_load_schema_returns_dict(self):
        """Test that _load_schema returns a dictionary"""
        schema = BaseEvent._load_schema("base-event.v1.json")
        assert isinstance(schema, dict)
        assert "$schema" in schema
        assert "properties" in schema


class TestEventMetadata:
    """Tests for EventMetadata class"""

    def test_event_metadata_creation(self):
        """Test creating EventMetadata"""
        correlation_id = uuid4()
        metadata = EventMetadata(
            correlation_id=correlation_id,
            user_id=uuid4(),
            trace_id="trace-123",
        )

        assert metadata.correlation_id == correlation_id
        assert metadata.trace_id == "trace-123"

    def test_event_metadata_to_dict(self):
        """Test EventMetadata.to_dict()"""
        correlation_id = uuid4()
        user_id = uuid4()
        metadata = EventMetadata(
            correlation_id=correlation_id,
            user_id=user_id,
            trace_id="trace-123",
            span_id="span-456",
        )

        result = metadata.to_dict()
        assert result["correlation_id"] == str(correlation_id)
        assert result["user_id"] == str(user_id)
        assert result["trace_id"] == "trace-123"
        assert result["span_id"] == "span-456"


class TestBaseEventSerialization:
    """Tests for BaseEvent serialization methods"""

    def test_to_json_returns_string(self):
        """Test that to_json() returns a valid JSON string"""
        import json

        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Test Field",
            geometry={"type": "Polygon", "coordinates": []},
            area_hectares=10.5,
        )

        json_str = event.to_json()
        assert isinstance(json_str, str)

        # Should be valid JSON
        parsed = json.loads(json_str)
        assert "event_id" in parsed
        assert "event_type" in parsed
        assert parsed["event_type"] == "field.created"

    def test_to_dict_contains_required_fields(self):
        """Test that to_dict() contains all required fields"""
        tenant_id = uuid4()
        event = SampleEventWithSchema(
            tenant_id=tenant_id,
            field_id=uuid4(),
            name="Test Field",
            geometry={"type": "Polygon", "coordinates": []},
            area_hectares=10.5,
        )

        result = event.to_dict()

        assert "event_id" in result
        assert "event_type" in result
        assert "event_version" in result
        assert "timestamp" in result
        assert "tenant_id" in result
        assert "payload" in result
        assert result["tenant_id"] == str(tenant_id)
        assert result["event_type"] == "field.created"
        assert result["event_version"] == "1.0.0"
