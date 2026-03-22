"""
Tests for SAHOOL Event Models
==============================
Tests for event enums, metadata, and Pydantic event models.
"""

from __future__ import annotations

from datetime import datetime, timezone, UTC
from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from shared.events.models import (
    AdvisorRecommendationEvent,
    AlertCreatedEvent,
    CropPlantedEvent,
    EventMetadata,
    EventMetadataDTO,
    EventPriority,
    EventStatus,
    FarmCreatedEvent,
    FieldCreatedEvent,
    FieldUpdatedEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
)


# =============================================================================
# Event Enum Tests
# =============================================================================


class TestEventPriority:
    """Test EventPriority enum."""

    def test_values(self):
        assert EventPriority.LOW == "low"
        assert EventPriority.MEDIUM == "medium"
        assert EventPriority.HIGH == "high"
        assert EventPriority.CRITICAL == "critical"

    def test_is_str_enum(self):
        assert isinstance(EventPriority.LOW, str)

    def test_all_members(self):
        assert len(EventPriority) == 4


class TestEventStatus:
    """Test EventStatus enum."""

    def test_values(self):
        assert EventStatus.PENDING == "pending"
        assert EventStatus.PROCESSING == "processing"
        assert EventStatus.COMPLETED == "completed"
        assert EventStatus.FAILED == "failed"

    def test_is_str_enum(self):
        assert isinstance(EventStatus.PENDING, str)

    def test_all_members(self):
        assert len(EventStatus) == 4


# =============================================================================
# EventMetadataDTO Tests
# =============================================================================


class TestEventMetadataDTO:
    """Test EventMetadataDTO model."""

    def test_all_fields_optional(self):
        """All fields default to None."""
        meta = EventMetadataDTO()
        assert meta.correlation_id is None
        assert meta.causation_id is None
        assert meta.user_id is None
        assert meta.trace_id is None
        assert meta.span_id is None

    def test_with_values(self):
        meta = EventMetadataDTO(
            correlation_id="corr-1",
            causation_id="cause-1",
            user_id="user-1",
            trace_id="trace-1",
            span_id="span-1",
        )
        assert meta.correlation_id == "corr-1"
        assert meta.user_id == "user-1"

    def test_backward_compatible_alias(self):
        """EventMetadata is an alias for EventMetadataDTO."""
        assert EventMetadata is EventMetadataDTO


# =============================================================================
# FieldCreatedEvent Tests
# =============================================================================


class TestFieldCreatedEvent:
    """Test FieldCreatedEvent model."""

    @pytest.fixture
    def valid_field_event_data(self):
        return {
            "field_id": str(uuid4()),
            "farm_id": str(uuid4()),
            "name": "Wheat Field North",
            "geometry_wkt": "POLYGON((46.7 24.7, 46.8 24.7, 46.8 24.8, 46.7 24.8, 46.7 24.7))",
            "created_at": datetime.now(UTC),
        }

    def test_valid_creation(self, valid_field_event_data):
        event = FieldCreatedEvent(**valid_field_event_data)
        assert event.name == "Wheat Field North"
        assert isinstance(event.field_id, UUID)

    def test_with_optional_fields(self, valid_field_event_data):
        valid_field_event_data.update({
            "name_ar": "حقل القمح الشمالي",
            "area_hectares": 5.2,
            "soil_type": "clay_loam",
            "irrigation_type": "drip",
        })
        event = FieldCreatedEvent(**valid_field_event_data)
        assert event.name_ar == "حقل القمح الشمالي"
        assert event.area_hectares == 5.2

    def test_name_too_short_fails(self, valid_field_event_data):
        valid_field_event_data["name"] = ""
        with pytest.raises(ValidationError):
            FieldCreatedEvent(**valid_field_event_data)

    def test_name_too_long_fails(self, valid_field_event_data):
        valid_field_event_data["name"] = "x" * 121
        with pytest.raises(ValidationError):
            FieldCreatedEvent(**valid_field_event_data)

    def test_geometry_wkt_too_short_fails(self, valid_field_event_data):
        valid_field_event_data["geometry_wkt"] = "POINT(0)"  # < 10 chars
        with pytest.raises(ValidationError):
            FieldCreatedEvent(**valid_field_event_data)

    def test_negative_area_fails(self, valid_field_event_data):
        valid_field_event_data["area_hectares"] = -1.0
        with pytest.raises(ValidationError):
            FieldCreatedEvent(**valid_field_event_data)

    def test_missing_required_field_fails(self):
        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=str(uuid4()),
                # missing farm_id, name, geometry_wkt, created_at
            )

    def test_serialization(self, valid_field_event_data):
        event = FieldCreatedEvent(**valid_field_event_data)
        json_str = event.model_dump_json()
        assert "Wheat Field North" in json_str


# =============================================================================
# FieldUpdatedEvent Tests
# =============================================================================


class TestFieldUpdatedEvent:
    """Test FieldUpdatedEvent model."""

    def test_minimal_creation(self):
        event = FieldUpdatedEvent(
            field_id=str(uuid4()),
            updated_at=datetime.now(UTC),
        )
        assert event.name is None
        assert event.ndvi_value is None

    def test_with_ndvi(self):
        event = FieldUpdatedEvent(
            field_id=str(uuid4()),
            ndvi_value=0.72,
            updated_at=datetime.now(UTC),
        )
        assert event.ndvi_value == 0.72

    def test_ndvi_below_minus_one_fails(self):
        with pytest.raises(ValidationError):
            FieldUpdatedEvent(
                field_id=str(uuid4()),
                ndvi_value=-1.5,
                updated_at=datetime.now(UTC),
            )

    def test_ndvi_above_one_fails(self):
        with pytest.raises(ValidationError):
            FieldUpdatedEvent(
                field_id=str(uuid4()),
                ndvi_value=1.5,
                updated_at=datetime.now(UTC),
            )

    def test_ndvi_boundary_values(self):
        """NDVI can be exactly -1 or 1."""
        event_min = FieldUpdatedEvent(
            field_id=str(uuid4()),
            ndvi_value=-1.0,
            updated_at=datetime.now(UTC),
        )
        event_max = FieldUpdatedEvent(
            field_id=str(uuid4()),
            ndvi_value=1.0,
            updated_at=datetime.now(UTC),
        )
        assert event_min.ndvi_value == -1.0
        assert event_max.ndvi_value == 1.0


# =============================================================================
# FarmCreatedEvent Tests
# =============================================================================


class TestFarmCreatedEvent:
    """Test FarmCreatedEvent model."""

    def test_valid_creation(self):
        event = FarmCreatedEvent(
            farm_id=str(uuid4()),
            tenant_id=str(uuid4()),
            name="Al-Rashid Farm",
            location_lat=24.7,
            location_lon=46.7,
            created_at=datetime.now(UTC),
        )
        assert event.name == "Al-Rashid Farm"
        assert event.location_lat == 24.7

    def test_with_arabic_name(self):
        event = FarmCreatedEvent(
            farm_id=str(uuid4()),
            tenant_id=str(uuid4()),
            name="Al-Rashid",
            name_ar="الراشد",
            location_lat=24.7,
            location_lon=46.7,
            created_at=datetime.now(UTC),
        )
        assert event.name_ar == "الراشد"

    def test_latitude_out_of_range(self):
        with pytest.raises(ValidationError):
            FarmCreatedEvent(
                farm_id=str(uuid4()),
                tenant_id=str(uuid4()),
                name="Farm",
                location_lat=91.0,
                location_lon=46.7,
                created_at=datetime.now(UTC),
            )

    def test_longitude_out_of_range(self):
        with pytest.raises(ValidationError):
            FarmCreatedEvent(
                farm_id=str(uuid4()),
                tenant_id=str(uuid4()),
                name="Farm",
                location_lat=24.7,
                location_lon=181.0,
                created_at=datetime.now(UTC),
            )


# =============================================================================
# CropPlantedEvent Tests
# =============================================================================


class TestCropPlantedEvent:
    """Test CropPlantedEvent model."""

    def test_valid_creation(self):
        event = CropPlantedEvent(
            field_id=str(uuid4()),
            crop_type="wheat",
            planting_date=datetime.now(UTC),
        )
        assert event.crop_type == "wheat"
        assert event.variety is None
        assert event.expected_harvest_date is None

    def test_with_all_fields(self):
        now = datetime.now(UTC)
        event = CropPlantedEvent(
            field_id=str(uuid4()),
            crop_type="date_palm",
            variety="Khalas",
            planting_date=now,
            expected_harvest_date=now,
            area_hectares=3.5,
        )
        assert event.variety == "Khalas"
        assert event.area_hectares == 3.5

    def test_empty_crop_type_fails(self):
        with pytest.raises(ValidationError):
            CropPlantedEvent(
                field_id=str(uuid4()),
                crop_type="",
                planting_date=datetime.now(UTC),
            )


# =============================================================================
# TaskCreatedEvent Tests
# =============================================================================


class TestTaskCreatedEvent:
    """Test TaskCreatedEvent model."""

    def test_valid_creation(self):
        event = TaskCreatedEvent(
            task_id=str(uuid4()),
            tenant_id=str(uuid4()),
            title="Apply fertilizer to Field 3",
            priority="high",
            created_at=datetime.now(UTC),
        )
        assert event.title == "Apply fertilizer to Field 3"
        assert event.priority == "high"
        assert event.field_id is None

    def test_invalid_priority_fails(self):
        with pytest.raises(ValidationError):
            TaskCreatedEvent(
                task_id=str(uuid4()),
                tenant_id=str(uuid4()),
                title="Test task",
                priority="invalid_priority",
                created_at=datetime.now(UTC),
            )

    def test_valid_priorities(self):
        """All valid priority levels are accepted."""
        for priority in ["low", "medium", "high", "urgent"]:
            event = TaskCreatedEvent(
                task_id=str(uuid4()),
                tenant_id=str(uuid4()),
                title="Test",
                priority=priority,
                created_at=datetime.now(UTC),
            )
            assert event.priority == priority

    def test_empty_title_fails(self):
        with pytest.raises(ValidationError):
            TaskCreatedEvent(
                task_id=str(uuid4()),
                tenant_id=str(uuid4()),
                title="",
                priority="low",
                created_at=datetime.now(UTC),
            )


# =============================================================================
# TaskCompletedEvent Tests
# =============================================================================


class TestTaskCompletedEvent:
    """Test TaskCompletedEvent model."""

    def test_valid_creation(self):
        event = TaskCompletedEvent(
            task_id=str(uuid4()),
            completed_by=str(uuid4()),
            completed_at=datetime.now(UTC),
        )
        assert event.evidence_notes is None

    def test_with_evidence(self):
        event = TaskCompletedEvent(
            task_id=str(uuid4()),
            completed_by=str(uuid4()),
            completed_at=datetime.now(UTC),
            evidence_notes="Applied 46kg/ha Urea successfully",
        )
        assert "Urea" in event.evidence_notes


# =============================================================================
# AdvisorRecommendationEvent Tests
# =============================================================================


class TestAdvisorRecommendationEvent:
    """Test AdvisorRecommendationEvent model."""

    def test_valid_creation(self):
        event = AdvisorRecommendationEvent(
            recommendation_id=str(uuid4()),
            field_id=str(uuid4()),
            tenant_id=str(uuid4()),
            recommendation_type="irrigation",
            title="Increase irrigation",
            description="Soil moisture below threshold",
            priority="high",
            confidence_score=0.85,
            created_at=datetime.now(UTC),
        )
        assert event.confidence_score == 0.85
        assert event.recommendation_type == "irrigation"

    def test_invalid_recommendation_type_fails(self):
        with pytest.raises(ValidationError):
            AdvisorRecommendationEvent(
                recommendation_id=str(uuid4()),
                field_id=str(uuid4()),
                tenant_id=str(uuid4()),
                recommendation_type="unknown_type",
                title="Test",
                description="Test",
                priority="low",
                confidence_score=0.5,
                created_at=datetime.now(UTC),
            )

    def test_valid_recommendation_types(self):
        for rtype in ["irrigation", "fertilizer", "pest", "harvest"]:
            event = AdvisorRecommendationEvent(
                recommendation_id=str(uuid4()),
                field_id=str(uuid4()),
                tenant_id=str(uuid4()),
                recommendation_type=rtype,
                title="Test",
                description="Test",
                priority="low",
                confidence_score=0.5,
                created_at=datetime.now(UTC),
            )
            assert event.recommendation_type == rtype

    def test_confidence_below_zero_fails(self):
        with pytest.raises(ValidationError):
            AdvisorRecommendationEvent(
                recommendation_id=str(uuid4()),
                field_id=str(uuid4()),
                tenant_id=str(uuid4()),
                recommendation_type="irrigation",
                title="Test",
                description="Test",
                priority="low",
                confidence_score=-0.1,
                created_at=datetime.now(UTC),
            )

    def test_confidence_above_one_fails(self):
        with pytest.raises(ValidationError):
            AdvisorRecommendationEvent(
                recommendation_id=str(uuid4()),
                field_id=str(uuid4()),
                tenant_id=str(uuid4()),
                recommendation_type="irrigation",
                title="Test",
                description="Test",
                priority="low",
                confidence_score=1.1,
                created_at=datetime.now(UTC),
            )

    def test_bilingual_fields(self):
        event = AdvisorRecommendationEvent(
            recommendation_id=str(uuid4()),
            field_id=str(uuid4()),
            tenant_id=str(uuid4()),
            recommendation_type="fertilizer",
            title="Apply nitrogen",
            title_ar="تطبيق النيتروجين",
            description="Nitrogen deficiency detected",
            description_ar="تم اكتشاف نقص النيتروجين",
            priority="high",
            confidence_score=0.9,
            created_at=datetime.now(UTC),
        )
        assert event.title_ar == "تطبيق النيتروجين"
        assert event.description_ar == "تم اكتشاف نقص النيتروجين"


# =============================================================================
# AlertCreatedEvent Tests
# =============================================================================


class TestAlertCreatedEvent:
    """Test AlertCreatedEvent model."""

    def test_valid_creation(self):
        event = AlertCreatedEvent(
            alert_id=str(uuid4()),
            tenant_id=str(uuid4()),
            alert_type="weather",
            severity="critical",
            title="Frost Alert",
            message="Temperature expected to drop below 0C",
            created_at=datetime.now(UTC),
        )
        assert event.severity == "critical"
        assert event.field_id is None

    def test_invalid_alert_type_fails(self):
        with pytest.raises(ValidationError):
            AlertCreatedEvent(
                alert_id=str(uuid4()),
                tenant_id=str(uuid4()),
                alert_type="unknown",
                severity="info",
                title="Test",
                message="Test",
                created_at=datetime.now(UTC),
            )

    def test_valid_alert_types(self):
        for atype in ["weather", "pest", "disease", "irrigation", "system"]:
            event = AlertCreatedEvent(
                alert_id=str(uuid4()),
                tenant_id=str(uuid4()),
                alert_type=atype,
                severity="info",
                title="Test",
                message="Test",
                created_at=datetime.now(UTC),
            )
            assert event.alert_type == atype

    def test_valid_severity_levels(self):
        for severity in ["info", "warning", "critical"]:
            event = AlertCreatedEvent(
                alert_id=str(uuid4()),
                tenant_id=str(uuid4()),
                alert_type="weather",
                severity=severity,
                title="Test",
                message="Test",
                created_at=datetime.now(UTC),
            )
            assert event.severity == severity

    def test_invalid_severity_fails(self):
        with pytest.raises(ValidationError):
            AlertCreatedEvent(
                alert_id=str(uuid4()),
                tenant_id=str(uuid4()),
                alert_type="weather",
                severity="low",
                title="Test",
                message="Test",
                created_at=datetime.now(UTC),
            )

    def test_bilingual_alert(self):
        event = AlertCreatedEvent(
            alert_id=str(uuid4()),
            tenant_id=str(uuid4()),
            alert_type="pest",
            severity="critical",
            title="Red Palm Weevil Detected",
            title_ar="تم اكتشاف سوسة النخيل الحمراء",
            message="RPW detected in Block B",
            message_ar="تم اكتشاف سوسة النخيل الحمراء في القطاع ب",
            created_at=datetime.now(UTC),
        )
        assert event.title_ar == "تم اكتشاف سوسة النخيل الحمراء"
