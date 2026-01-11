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


# Sample valid GeoJSON geometries for testing
VALID_POLYGON = {
    "type": "Polygon",
    "coordinates": [
        [
            [35.123, 31.456],  # longitude, latitude
            [35.234, 31.456],
            [35.234, 31.567],
            [35.123, 31.567],
            [35.123, 31.456],  # closed ring - first and last must match
        ]
    ],
}

VALID_MULTIPOLYGON = {
    "type": "MultiPolygon",
    "coordinates": [
        [
            [
                [35.0, 31.0],
                [35.1, 31.0],
                [35.1, 31.1],
                [35.0, 31.1],
                [35.0, 31.0],
            ]
        ],
        [
            [
                [36.0, 32.0],
                [36.1, 32.0],
                [36.1, 32.1],
                [36.0, 32.1],
                [36.0, 32.0],
            ]
        ],
    ],
}


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
            geometry=VALID_POLYGON,
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

        # Create event with empty name (minimum length is 1)
        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="",
            geometry=VALID_POLYGON,
            area_hectares=-1.0,  # Negative area - minimum is 0
        )

        with pytest.raises(ValidationError):
            event.validate()


class TestGeoJSONGeometryValidation:
    """Tests for GeoJSON geometry validation (RFC 7946 compliant)"""

    def test_valid_polygon_geometry(self):
        """Test validation passes for valid Polygon geometry"""
        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Field with Polygon",
            geometry=VALID_POLYGON,
            area_hectares=5.0,
        )
        assert event.validate() is True

    def test_valid_multipolygon_geometry(self):
        """Test validation passes for valid MultiPolygon geometry"""
        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Field with MultiPolygon",
            geometry=VALID_MULTIPOLYGON,
            area_hectares=15.0,
        )
        assert event.validate() is True

    def test_polygon_with_altitude(self):
        """Test validation passes for Polygon with altitude (3D coordinates)"""
        geometry = {
            "type": "Polygon",
            "coordinates": [
                [
                    [35.0, 31.0, 100.0],  # longitude, latitude, altitude
                    [35.1, 31.0, 100.0],
                    [35.1, 31.1, 100.0],
                    [35.0, 31.1, 100.0],
                    [35.0, 31.0, 100.0],
                ]
            ],
        }
        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Field with 3D coordinates",
            geometry=geometry,
            area_hectares=5.0,
        )
        assert event.validate() is True

    def test_invalid_geometry_type(self):
        """Test validation fails for invalid geometry type"""
        from jsonschema import ValidationError

        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Field with invalid type",
            geometry={"type": "Point", "coordinates": [35.0, 31.0]},  # Point not allowed
            area_hectares=5.0,
        )
        with pytest.raises(ValidationError):
            event.validate()

    def test_polygon_with_insufficient_points(self):
        """Test validation fails for polygon with less than 4 points"""
        from jsonschema import ValidationError

        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Field with invalid polygon",
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [[35.0, 31.0], [35.1, 31.0], [35.0, 31.0]]  # Only 3 points
                ],
            },
            area_hectares=5.0,
        )
        with pytest.raises(ValidationError):
            event.validate()

    def test_polygon_with_empty_coordinates(self):
        """Test validation fails for polygon with empty coordinates"""
        from jsonschema import ValidationError

        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Field with empty coordinates",
            geometry={"type": "Polygon", "coordinates": []},
            area_hectares=5.0,
        )
        with pytest.raises(ValidationError):
            event.validate()

    def test_polygon_with_invalid_position_format(self):
        """Test validation fails for invalid position format"""
        from jsonschema import ValidationError

        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Field with invalid positions",
            geometry={
                "type": "Polygon",
                "coordinates": [
                    [
                        [35.0],  # Only 1 coordinate instead of 2
                        [35.1],
                        [35.1],
                        [35.0],
                    ]
                ],
            },
            area_hectares=5.0,
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
            geometry=VALID_POLYGON,
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
            geometry=VALID_POLYGON,
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
            geometry=VALID_POLYGON,
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

    def test_geometry_preserved_in_serialization(self):
        """Test that geometry coordinates are preserved during serialization"""
        import json

        event = SampleEventWithSchema(
            tenant_id=uuid4(),
            field_id=uuid4(),
            name="Test Field",
            geometry=VALID_POLYGON,
            area_hectares=10.5,
        )

        result = event.to_dict()
        assert result["payload"]["geometry"]["type"] == "Polygon"
        assert result["payload"]["geometry"]["coordinates"] == VALID_POLYGON["coordinates"]
