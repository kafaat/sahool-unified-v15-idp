"""
Event Snapshot Tests
====================
اختبارات لقطات الأحداث

Snapshot tests to ensure event schemas remain stable.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import os
from datetime import datetime, UTC
from pathlib import Path
from typing import Any

import pytest

from shared.events.contracts import (
    FieldCreatedEvent,
    FieldUpdatedEvent,
    WeatherForecastEvent,
    SatelliteDataReadyEvent,
    DiseaseDetectedEvent,
    AgentExecutionCompletedEvent,
)


# =============================================================================
# Snapshot Configuration
# =============================================================================

SNAPSHOT_DIR = Path(__file__).parent / "event_snapshots"


def ensure_snapshot_dir():
    """Ensure snapshot directory exists."""
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)


def get_snapshot_path(name: str) -> Path:
    """Get path for a snapshot file."""
    return SNAPSHOT_DIR / f"{name}.json"


def save_snapshot(name: str, data: dict) -> None:
    """Save a snapshot."""
    ensure_snapshot_dir()
    path = get_snapshot_path(name)

    # Normalize data for comparison
    normalized = normalize_for_snapshot(data)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(normalized, f, indent=2, ensure_ascii=False, default=str)


def load_snapshot(name: str) -> dict | None:
    """Load a snapshot."""
    path = get_snapshot_path(name)
    if not path.exists():
        return None

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def normalize_for_snapshot(data: dict) -> dict:
    """
    Normalize data for snapshot comparison.
    Remove volatile fields like timestamps and IDs.
    """
    volatile_fields = ["event_id", "timestamp", "created_at", "updated_at"]

    def normalize(obj: Any) -> Any:
        if isinstance(obj, dict):
            return {
                k: "<VOLATILE>" if k in volatile_fields else normalize(v)
                for k, v in sorted(obj.items())
            }
        elif isinstance(obj, list):
            return [normalize(item) for item in obj]
        elif isinstance(obj, datetime):
            return "<DATETIME>"
        else:
            return obj

    return normalize(data)


def compare_with_snapshot(name: str, data: dict, update: bool = False) -> bool:
    """
    Compare data with snapshot.

    Args:
        name: Snapshot name
        data: Current data
        update: Whether to update snapshot if different

    Returns:
        True if matches, False otherwise
    """
    normalized = normalize_for_snapshot(data)
    existing = load_snapshot(name)

    if existing is None:
        # No snapshot exists, create it
        save_snapshot(name, data)
        return True

    if normalized == existing:
        return True

    if update:
        save_snapshot(name, data)
        return True

    return False


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def fixed_timestamp() -> datetime:
    """Fixed timestamp for reproducible tests."""
    return datetime(2026, 1, 15, 10, 30, 0, tzinfo=UTC)


@pytest.fixture
def update_snapshots() -> bool:
    """Check if snapshots should be updated."""
    return os.environ.get("UPDATE_SNAPSHOTS", "").lower() == "true"


# =============================================================================
# Field Event Snapshots
# =============================================================================


class TestFieldEventSnapshots:
    """Snapshot tests for field events."""

    def test_field_created_snapshot(self, update_snapshots):
        """Test FieldCreatedEvent schema stability."""
        event = FieldCreatedEvent(
            field_id="field-snapshot-001",
            farm_id="farm-snapshot-001",
            name="Snapshot Test Field",
            area_hectares=50.0,
            crop_type="wheat",
        )

        data = json.loads(event.model_dump_json())

        if update_snapshots or not load_snapshot("field_created"):
            save_snapshot("field_created", data)
            pytest.skip("Snapshot created/updated")

        snapshot = load_snapshot("field_created")
        current = normalize_for_snapshot(data)

        assert current == snapshot, "FieldCreatedEvent schema has changed!"

    def test_field_updated_snapshot(self, update_snapshots):
        """Test FieldUpdatedEvent schema stability."""
        event = FieldUpdatedEvent(
            field_id="field-snapshot-001",
            farm_id="farm-snapshot-001",
            changes={"name": "Updated Field", "area_hectares": 55.0},
        )

        data = json.loads(event.model_dump_json())

        if update_snapshots or not load_snapshot("field_updated"):
            save_snapshot("field_updated", data)
            pytest.skip("Snapshot created/updated")

        snapshot = load_snapshot("field_updated")
        current = normalize_for_snapshot(data)

        assert current == snapshot, "FieldUpdatedEvent schema has changed!"


# =============================================================================
# Weather Event Snapshots
# =============================================================================


class TestWeatherEventSnapshots:
    """Snapshot tests for weather events."""

    def test_weather_forecast_snapshot(self, update_snapshots, fixed_timestamp):
        """Test WeatherForecastEvent schema stability."""
        event = WeatherForecastEvent(
            field_id="field-snapshot-001",
            forecast_date=fixed_timestamp,
            temperature_min=15.0,
            temperature_max=28.0,
            precipitation_mm=5.0,
            humidity_percent=65.0,
            wind_speed_kmh=12.0,
        )

        data = json.loads(event.model_dump_json())

        if update_snapshots or not load_snapshot("weather_forecast"):
            save_snapshot("weather_forecast", data)
            pytest.skip("Snapshot created/updated")

        snapshot = load_snapshot("weather_forecast")
        current = normalize_for_snapshot(data)

        assert current == snapshot, "WeatherForecastEvent schema has changed!"


# =============================================================================
# Satellite Event Snapshots
# =============================================================================


class TestSatelliteEventSnapshots:
    """Snapshot tests for satellite events."""

    def test_satellite_data_ready_snapshot(self, update_snapshots, fixed_timestamp):
        """Test SatelliteDataReadyEvent schema stability."""
        event = SatelliteDataReadyEvent(
            field_id="field-snapshot-001",
            satellite_id="sentinel-2a",
            image_date=fixed_timestamp,
            cloud_cover_percent=10.5,
            ndvi_available=True,
        )

        data = json.loads(event.model_dump_json())

        if update_snapshots or not load_snapshot("satellite_data_ready"):
            save_snapshot("satellite_data_ready", data)
            pytest.skip("Snapshot created/updated")

        snapshot = load_snapshot("satellite_data_ready")
        current = normalize_for_snapshot(data)

        assert current == snapshot, "SatelliteDataReadyEvent schema has changed!"


# =============================================================================
# Health Event Snapshots
# =============================================================================


class TestHealthEventSnapshots:
    """Snapshot tests for health/disease events."""

    def test_disease_detected_snapshot(self, update_snapshots):
        """Test DiseaseDetectedEvent schema stability."""
        event = DiseaseDetectedEvent(
            field_id="field-snapshot-001",
            disease_type="wheat_rust",
            disease_name="Wheat Leaf Rust",
            disease_name_ar="صدأ أوراق القمح",
            severity="moderate",
            confidence_score=0.87,
            affected_area_percent=15.0,
        )

        data = json.loads(event.model_dump_json())

        if update_snapshots or not load_snapshot("disease_detected"):
            save_snapshot("disease_detected", data)
            pytest.skip("Snapshot created/updated")

        snapshot = load_snapshot("disease_detected")
        current = normalize_for_snapshot(data)

        assert current == snapshot, "DiseaseDetectedEvent schema has changed!"


# =============================================================================
# Agent Event Snapshots
# =============================================================================


class TestAgentEventSnapshots:
    """Snapshot tests for AI agent events."""

    def test_agent_execution_completed_snapshot(self, update_snapshots):
        """Test AgentExecutionCompletedEvent schema stability."""
        event = AgentExecutionCompletedEvent(
            execution_id="exec-snapshot-001",
            agent_type="farm_advisor",
            output_data={
                "recommendation": "Irrigate in 2 days",
                "confidence": 0.92,
            },
            duration_ms=1500,
            success=True,
        )

        data = json.loads(event.model_dump_json())

        if update_snapshots or not load_snapshot("agent_execution_completed"):
            save_snapshot("agent_execution_completed", data)
            pytest.skip("Snapshot created/updated")

        snapshot = load_snapshot("agent_execution_completed")
        current = normalize_for_snapshot(data)

        assert current == snapshot, "AgentExecutionCompletedEvent schema has changed!"


# =============================================================================
# Schema Structure Tests
# =============================================================================


class TestEventSchemaStructure:
    """Tests for event schema structure."""

    def test_all_events_have_required_base_fields(self):
        """Test that all events have required base fields."""
        events = [
            FieldCreatedEvent(field_id="f1", farm_id="farm1", name="Field"),
            FieldUpdatedEvent(field_id="f1", farm_id="farm1", changes={}),
            WeatherForecastEvent(
                field_id="f1",
                forecast_date=datetime.now(UTC),
                temperature_min=10,
                temperature_max=20,
                precipitation_mm=0,
                humidity_percent=50,
                wind_speed_kmh=10,
            ),
        ]

        for event in events:
            data = event.model_dump()

            # All events must have these base fields
            assert "event_id" in data, f"{type(event).__name__} missing event_id"
            assert "timestamp" in data, f"{type(event).__name__} missing timestamp"

    def test_field_events_have_field_id(self):
        """Test that field events have field_id."""
        field_events = [
            FieldCreatedEvent(field_id="f1", farm_id="farm1", name="Field"),
            FieldUpdatedEvent(field_id="f1", farm_id="farm1", changes={}),
        ]

        for event in field_events:
            data = event.model_dump()
            assert "field_id" in data
            assert "farm_id" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
