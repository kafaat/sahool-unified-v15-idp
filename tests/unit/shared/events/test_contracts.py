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
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from shared.events.contracts import (
    AgentExecutionCompletedEvent,
    AgentExecutionStartedEvent,
    BaseEvent,
    CropStressEvent,
    DiseaseDetectedEvent,
    FarmerCreatedEvent,
    FieldCreatedEvent,
    FieldDeletedEvent,
    FieldUpdatedEvent,
    PaymentCompletedEvent,
    SatelliteDataReadyEvent,
    SubscriptionCreatedEvent,
    WeatherAlertEvent,
    WeatherForecastEvent,
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
        """Test that BaseEvent auto-generates timestamp."""
        event = BaseEvent()
        assert event.timestamp is not None
        assert isinstance(event.timestamp, datetime)

    def test_base_event_event_type(self):
        """Test event_type returns class name."""
        event = BaseEvent()
        assert event.event_type == "BaseEvent"

    def test_base_event_serialization(self):
        """Test JSON serialization."""
        event = BaseEvent()
        parsed = json.loads(event.model_dump_json())
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
        field_id = uuid4()
        farm_id = uuid4()
        tenant_id = uuid4()
        event = FieldCreatedEvent(
            field_id=field_id,
            farm_id=farm_id,
            tenant_id=tenant_id,
            name="Test Field",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
        )

        assert event.field_id == field_id
        assert event.farm_id == farm_id
        assert event.name == "Test Field"

    def test_field_created_optional_fields(self):
        """Test optional fields."""
        event = FieldCreatedEvent(
            field_id=uuid4(),
            farm_id=uuid4(),
            tenant_id=uuid4(),
            name="Test Field",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            area_hectares=25.5,
            soil_type="clay",
        )

        assert event.area_hectares == 25.5
        assert event.soil_type == "clay"

    def test_field_created_inherits_base(self):
        """Test inheritance from BaseEvent."""
        event = FieldCreatedEvent(
            field_id=uuid4(),
            farm_id=uuid4(),
            tenant_id=uuid4(),
            name="Test Field",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
        )

        assert hasattr(event, "event_id")
        assert hasattr(event, "timestamp")

    def test_field_created_serialization(self):
        """Test JSON serialization."""
        field_id = uuid4()
        farm_id = uuid4()
        tenant_id = uuid4()
        event = FieldCreatedEvent(
            field_id=field_id,
            farm_id=farm_id,
            tenant_id=tenant_id,
            name="Test Field",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            area_hectares=25.5,
        )

        data = json.loads(event.model_dump_json())

        assert data["field_id"] == str(field_id)
        assert data["farm_id"] == str(farm_id)
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
        field_id = uuid4()
        event = FieldUpdatedEvent(
            field_id=field_id,
            name="New Name",
            area_hectares=30.0,
        )

        assert event.field_id == field_id
        assert event.name == "New Name"
        assert event.area_hectares == 30.0

    def test_field_updated_empty_changes(self):
        """Test update with minimal fields."""
        field_id = uuid4()
        event = FieldUpdatedEvent(
            field_id=field_id,
        )

        assert event.field_id == field_id
        assert event.name is None


# =============================================================================
# Test FieldDeletedEvent
# =============================================================================


class TestFieldDeletedEvent:
    """Tests for FieldDeletedEvent model."""

    def test_field_deleted(self):
        """Test delete event."""
        field_id = uuid4()
        farm_id = uuid4()
        tenant_id = uuid4()
        event = FieldDeletedEvent(
            field_id=field_id,
            farm_id=farm_id,
            tenant_id=tenant_id,
        )

        assert event.field_id == field_id
        assert event.farm_id == farm_id


# =============================================================================
# Test WeatherForecastEvent
# =============================================================================


class TestWeatherForecastEvent:
    """Tests for WeatherForecastEvent model."""

    def test_weather_forecast_event(self):
        """Test weather forecast event."""
        event = WeatherForecastEvent(
            location_lat=24.7,
            location_lon=46.7,
            forecast_date=datetime.now(UTC),
            temperature=28.0,
            humidity=65.0,
            wind_speed=12.0,
            precipitation=5.0,
        )

        assert event.location_lat == 24.7
        assert event.temperature == 28.0
        assert event.humidity == 65.0


# =============================================================================
# Test WeatherAlertEvent
# =============================================================================


class TestWeatherAlertEvent:
    """Tests for WeatherAlertEvent model."""

    def test_weather_alert_event(self):
        """Test weather alert event."""
        event = WeatherAlertEvent(
            tenant_id=uuid4(),
            alert_type="frost",
            severity="warning",
            title="Frost Warning",
            message="Frost warning for tonight",
            message_ar="تحذير من الصقيع الليلة",
            start_time=datetime.now(UTC),
        )

        assert event.alert_type == "frost"
        assert event.severity == "warning"


# =============================================================================
# Test SatelliteDataReadyEvent
# =============================================================================


class TestSatelliteDataReadyEvent:
    """Tests for SatelliteDataReadyEvent model."""

    def test_satellite_data_ready(self):
        """Test satellite data ready event."""
        event = SatelliteDataReadyEvent(
            field_id=uuid4(),
            tenant_id=uuid4(),
            satellite_source="Sentinel-2",
            capture_date=datetime.now(UTC),
            cloud_coverage=10.5,
            ndvi_mean=0.65,
        )

        assert event.satellite_source == "Sentinel-2"
        assert event.cloud_coverage == 10.5
        assert event.ndvi_mean == 0.65


# =============================================================================
# Test DiseaseDetectedEvent
# =============================================================================


class TestDiseaseDetectedEvent:
    """Tests for DiseaseDetectedEvent model."""

    def test_disease_detected(self):
        """Test disease detection event."""
        event = DiseaseDetectedEvent(
            field_id=uuid4(),
            tenant_id=uuid4(),
            disease_name="Wheat Leaf Rust",
            disease_name_ar="صدأ أوراق القمح",
            severity="high",
            confidence_score=0.87,
            affected_area_hectares=1.5,
        )

        assert event.disease_name == "Wheat Leaf Rust"
        assert event.confidence_score == 0.87
        assert event.affected_area_hectares == 1.5


# =============================================================================
# Test CropStressEvent
# =============================================================================


class TestCropStressEvent:
    """Tests for CropStressEvent model."""

    def test_crop_stress_event(self):
        """Test crop stress event."""
        event = CropStressEvent(
            field_id=uuid4(),
            tenant_id=uuid4(),
            stress_type="water",
            severity="medium",
            confidence_score=0.75,
        )

        assert event.stress_type == "water"
        assert event.severity == "medium"


# =============================================================================
# Test Billing Events
# =============================================================================


class TestBillingEvents:
    """Tests for billing-related events."""

    def test_subscription_created(self):
        """Test subscription created event."""
        event = SubscriptionCreatedEvent(
            subscription_id=uuid4(),
            tenant_id=uuid4(),
            user_id=uuid4(),
            plan_id="professional",
            plan_name="Professional Plan",
            plan_tier="professional",
            billing_cycle="annual",
            start_date=datetime.now(UTC),
            price_amount=499.0,
            currency="SAR",
        )

        assert event.plan_id == "professional"
        assert event.price_amount == 499.0

    def test_payment_completed(self):
        """Test payment completed event."""
        event = PaymentCompletedEvent(
            payment_id=uuid4(),
            tenant_id=uuid4(),
            amount=499.0,
            currency="SAR",
            payment_method="credit_card",
            transaction_id="txn-123",
        )

        assert event.payment_method == "credit_card"
        assert event.amount == 499.0


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
            tenant_id="tenant-1",
            task="When should I irrigate?",
        )

        assert event.execution_id == "exec-123"
        assert event.agent_type == "farm_advisor"

    def test_agent_execution_completed(self):
        """Test agent execution completed event."""
        event = AgentExecutionCompletedEvent(
            execution_id="exec-123",
            agent_type="farm_advisor",
            tenant_id="tenant-1",
            duration_ms=1500,
            total_steps=3,
        )

        assert event.duration_ms == 1500
        assert event.total_steps == 3


# =============================================================================
# Test Farmer Events
# =============================================================================


class TestFarmerEvents:
    """Tests for farmer/CRM events."""

    def test_farmer_created(self):
        """Test farmer created event."""
        event = FarmerCreatedEvent(
            farmer_id="farmer-123",
            tenant_id="tenant-1",
            name="Ahmed Al-Rashid",
            name_ar="أحمد الراشد",
            phone="+966501234567",
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
        field_id = str(uuid4())
        farm_id = str(uuid4())
        tenant_id = str(uuid4())
        json_data = {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "field_id": field_id,
            "farm_id": farm_id,
            "tenant_id": tenant_id,
            "name": "Test Field",
            "geometry_wkt": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            "area_hectares": 25.5,
        }

        event = FieldCreatedEvent.model_validate(json_data)

        assert str(event.field_id) == field_id
        assert event.area_hectares == 25.5

    def test_event_round_trip(self):
        """Test serialization and deserialization round trip."""
        field_id = uuid4()
        farm_id = uuid4()
        tenant_id = uuid4()
        original = FieldCreatedEvent(
            field_id=field_id,
            farm_id=farm_id,
            tenant_id=tenant_id,
            name="Test Field",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            area_hectares=25.5,
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
