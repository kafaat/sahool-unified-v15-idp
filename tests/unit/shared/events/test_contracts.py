"""
Tests for Event Contracts Module
================================
اختبارات وحدة عقود الأحداث

Comprehensive tests for Pydantic event models.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
from datetime import datetime, UTC
from uuid import uuid4

import pytest

from shared.events.contracts import (
    BaseEvent,
    FieldCreatedEvent,
    FieldUpdatedEvent,
    FieldDeletedEvent,
    WeatherForecastEvent,
    WeatherAlertEvent,
    SatelliteDataReadyEvent,
    DiseaseDetectedEvent,
    CropStressEvent,
    SubscriptionCreatedEvent,
    PaymentCompletedEvent,
    AgentExecutionStartedEvent,
    AgentExecutionCompletedEvent,
    FarmerCreatedEvent,
)


# =============================================================================
# Test BaseEvent
# =============================================================================


class TestBaseEvent:
    """Tests for BaseEvent model."""

    def test_base_event_has_event_id(self):
        """Test that BaseEvent auto-generates event_id."""
        event = BaseEvent()
        assert event.event_id is not None
        assert len(event.event_id) > 0

    def test_base_event_has_timestamp(self):
        """Test that BaseEvent has timestamp."""
        event = BaseEvent()
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)

    def test_base_event_timestamp_is_utc(self):
        """Test that timestamp is UTC."""
        event = BaseEvent()
        # Timestamp should be close to now
        now = datetime.now(UTC)
        diff = abs((event.timestamp - now).total_seconds())
        assert diff < 5  # Within 5 seconds

    def test_base_event_unique_ids(self):
        """Test that each event has unique ID."""
        events = [BaseEvent() for _ in range(100)]
        ids = [e.event_id for e in events]
        assert len(ids) == len(set(ids))

    def test_base_event_serialization(self):
        """Test BaseEvent JSON serialization."""
        event = BaseEvent()
        json_str = event.model_dump_json()

        assert isinstance(json_str, str)
        parsed = json.loads(json_str)
        assert "event_id" in parsed
        assert "timestamp" in parsed

    def test_base_event_source_service(self):
        """Test source_service field."""
        event = BaseEvent(source_service="test-service")
        assert event.source_service == "test-service"


# =============================================================================
# Test FieldCreatedEvent
# =============================================================================


class TestFieldCreatedEvent:
    """Tests for FieldCreatedEvent model."""

    def test_field_created_required_fields(self):
        """Test required fields."""
        event = FieldCreatedEvent(
            field_id="field-123",
            farm_id="farm-456",
            name="Test Field",
        )

        assert event.field_id == "field-123"
        assert event.farm_id == "farm-456"
        assert event.name == "Test Field"

    def test_field_created_optional_fields(self):
        """Test optional fields."""
        event = FieldCreatedEvent(
            field_id="field-123",
            farm_id="farm-456",
            name="Test Field",
            area_hectares=25.5,
            crop_type="wheat",
        )

        assert event.area_hectares == 25.5
        assert event.crop_type == "wheat"

    def test_field_created_inherits_base(self):
        """Test inheritance from BaseEvent."""
        event = FieldCreatedEvent(
            field_id="field-123",
            farm_id="farm-456",
            name="Test Field",
        )

        assert hasattr(event, "event_id")
        assert hasattr(event, "timestamp")

    def test_field_created_serialization(self):
        """Test JSON serialization."""
        event = FieldCreatedEvent(
            field_id="field-123",
            farm_id="farm-456",
            name="Test Field",
            area_hectares=25.5,
        )

        data = json.loads(event.model_dump_json())

        assert data["field_id"] == "field-123"
        assert data["farm_id"] == "farm-456"
        assert data["area_hectares"] == 25.5

    def test_field_created_validation(self):
        """Test field validation."""
        # Missing required fields should raise
        with pytest.raises(Exception):  # ValidationError
            FieldCreatedEvent()


# =============================================================================
# Test FieldUpdatedEvent
# =============================================================================


class TestFieldUpdatedEvent:
    """Tests for FieldUpdatedEvent model."""

    def test_field_updated_with_changes(self):
        """Test update event with changes."""
        event = FieldUpdatedEvent(
            field_id="field-123",
            farm_id="farm-456",
            changes={"name": "New Name", "area_hectares": 30.0},
        )

        assert event.field_id == "field-123"
        assert "name" in event.changes
        assert event.changes["area_hectares"] == 30.0

    def test_field_updated_empty_changes(self):
        """Test update with no changes."""
        event = FieldUpdatedEvent(
            field_id="field-123",
            farm_id="farm-456",
            changes={},
        )

        assert event.changes == {}


# =============================================================================
# Test FieldDeletedEvent
# =============================================================================


class TestFieldDeletedEvent:
    """Tests for FieldDeletedEvent model."""

    def test_field_deleted(self):
        """Test delete event."""
        event = FieldDeletedEvent(
            field_id="field-123",
            farm_id="farm-456",
        )

        assert event.field_id == "field-123"
        assert event.farm_id == "farm-456"


# =============================================================================
# Test WeatherForecastEvent
# =============================================================================


class TestWeatherForecastEvent:
    """Tests for WeatherForecastEvent model."""

    def test_weather_forecast_event(self):
        """Test weather forecast event."""
        event = WeatherForecastEvent(
            field_id="field-123",
            forecast_date=datetime.now(UTC),
            temperature_min=15.0,
            temperature_max=28.0,
            precipitation_mm=5.0,
            humidity_percent=65.0,
            wind_speed_kmh=12.0,
        )

        assert event.field_id == "field-123"
        assert event.temperature_min == 15.0
        assert event.temperature_max == 28.0


# =============================================================================
# Test WeatherAlertEvent
# =============================================================================


class TestWeatherAlertEvent:
    """Tests for WeatherAlertEvent model."""

    def test_weather_alert_event(self):
        """Test weather alert event."""
        event = WeatherAlertEvent(
            field_id="field-123",
            alert_type="frost",
            severity="high",
            message="Frost warning for tonight",
            message_ar="تحذير من الصقيع الليلة",
        )

        assert event.alert_type == "frost"
        assert event.severity == "high"


# =============================================================================
# Test SatelliteDataReadyEvent
# =============================================================================


class TestSatelliteDataReadyEvent:
    """Tests for SatelliteDataReadyEvent model."""

    def test_satellite_data_ready(self):
        """Test satellite data ready event."""
        event = SatelliteDataReadyEvent(
            field_id="field-123",
            satellite_id="sentinel-2a",
            image_date=datetime.now(UTC),
            cloud_cover_percent=10.5,
            ndvi_available=True,
        )

        assert event.satellite_id == "sentinel-2a"
        assert event.cloud_cover_percent == 10.5
        assert event.ndvi_available is True


# =============================================================================
# Test DiseaseDetectedEvent
# =============================================================================


class TestDiseaseDetectedEvent:
    """Tests for DiseaseDetectedEvent model."""

    def test_disease_detected(self):
        """Test disease detection event."""
        event = DiseaseDetectedEvent(
            field_id="field-123",
            disease_type="wheat_rust",
            disease_name="Wheat Leaf Rust",
            disease_name_ar="صدأ أوراق القمح",
            severity="moderate",
            confidence_score=0.87,
            affected_area_percent=15.0,
        )

        assert event.disease_type == "wheat_rust"
        assert event.confidence_score == 0.87
        assert event.affected_area_percent == 15.0


# =============================================================================
# Test CropStressEvent
# =============================================================================


class TestCropStressEvent:
    """Tests for CropStressEvent model."""

    def test_crop_stress_event(self):
        """Test crop stress event."""
        event = CropStressEvent(
            field_id="field-123",
            stress_type="water",
            stress_level="moderate",
            ndvi_deviation=-0.15,
        )

        assert event.stress_type == "water"
        assert event.stress_level == "moderate"


# =============================================================================
# Test Billing Events
# =============================================================================


class TestBillingEvents:
    """Tests for billing-related events."""

    def test_subscription_created(self):
        """Test subscription created event."""
        event = SubscriptionCreatedEvent(
            subscription_id="sub-123",
            user_id="user-456",
            plan_id="professional",
            amount=499.0,
            currency="SAR",
        )

        assert event.subscription_id == "sub-123"
        assert event.plan_id == "professional"
        assert event.amount == 499.0

    def test_payment_completed(self):
        """Test payment completed event."""
        event = PaymentCompletedEvent(
            payment_id="pay-123",
            subscription_id="sub-123",
            amount=499.0,
            currency="SAR",
            payment_method="credit_card",
        )

        assert event.payment_id == "pay-123"
        assert event.payment_method == "credit_card"


# =============================================================================
# Test Agent Events
# =============================================================================


class TestAgentEvents:
    """Tests for AI agent events."""

    def test_agent_execution_started(self):
        """Test agent execution started event."""
        event = AgentExecutionStartedEvent(
            execution_id="exec-123",
            agent_type="farm_advisor",
            input_data={"query": "When should I irrigate?"},
        )

        assert event.execution_id == "exec-123"
        assert event.agent_type == "farm_advisor"

    def test_agent_execution_completed(self):
        """Test agent execution completed event."""
        event = AgentExecutionCompletedEvent(
            execution_id="exec-123",
            agent_type="farm_advisor",
            output_data={"recommendation": "Irrigate in 2 days"},
            duration_ms=1500,
            success=True,
        )

        assert event.duration_ms == 1500
        assert event.success is True


# =============================================================================
# Test Farmer Events
# =============================================================================


class TestFarmerEvents:
    """Tests for farmer/CRM events."""

    def test_farmer_created(self):
        """Test farmer created event."""
        event = FarmerCreatedEvent(
            farmer_id="farmer-123",
            name="Ahmed Al-Rashid",
            name_ar="أحمد الراشد",
            phone="+966501234567",
            region="Riyadh",
        )

        assert event.farmer_id == "farmer-123"
        assert event.name_ar == "أحمد الراشد"


# =============================================================================
# Test Event Deserialization
# =============================================================================


class TestEventDeserialization:
    """Tests for event deserialization."""

    def test_field_event_from_json(self):
        """Test creating event from JSON."""
        json_data = {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "field_id": "field-123",
            "farm_id": "farm-456",
            "name": "Test Field",
            "area_hectares": 25.5,
        }

        event = FieldCreatedEvent.model_validate(json_data)

        assert event.field_id == "field-123"
        assert event.area_hectares == 25.5

    def test_event_round_trip(self):
        """Test serialization and deserialization round trip."""
        original = FieldCreatedEvent(
            field_id="field-123",
            farm_id="farm-456",
            name="Test Field",
            area_hectares=25.5,
            crop_type="wheat",
        )

        # Serialize
        json_str = original.model_dump_json()

        # Deserialize
        restored = FieldCreatedEvent.model_validate_json(json_str)

        assert restored.field_id == original.field_id
        assert restored.farm_id == original.farm_id
        assert restored.area_hectares == original.area_hectares


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
