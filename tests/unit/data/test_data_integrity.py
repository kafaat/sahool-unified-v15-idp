"""
Data Integrity Bug-Hunting Tests for SAHOOL Platform
=====================================================
These tests target data validation boundaries, encoding issues,
and type confusion bugs that could corrupt agricultural data.

Run with:
    ENVIRONMENT=test JWT_SECRET_KEY=test-secret-key-for-unit-tests-only-32chars \
    PYTHONPATH=. pytest tests/unit/data/test_data_integrity.py -v --timeout=30
"""

from __future__ import annotations

import os
import uuid
from datetime import UTC, date, datetime, timedelta, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")


# =============================================================================
# 1. UUID Field Validation
# =============================================================================


class TestUUIDValidation:
    """BUG TARGET: Invalid UUIDs accepted in fields that should require UUIDs."""

    def test_field_created_event_rejects_invalid_uuid(self):
        """Bug: field_id accepts non-UUID strings."""
        from shared.events.models import FieldCreatedEvent

        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id="not-a-uuid",
                farm_id=str(uuid.uuid4()),
                name="Test Field",
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
                created_at=datetime.now(UTC),
            )

    def test_field_created_event_accepts_valid_uuid(self):
        """Baseline: valid UUIDs should work."""
        from shared.events.models import FieldCreatedEvent

        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name="Test Field",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            created_at=datetime.now(UTC),
        )
        assert event.field_id is not None

    def test_task_event_rejects_invalid_uuid(self):
        """Bug: task_id accepts non-UUID strings."""
        from shared.events.models import TaskCreatedEvent

        with pytest.raises(ValidationError):
            TaskCreatedEvent(
                task_id="invalid-id",
                field_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                title="Test Task",
                priority="high",
                created_at=datetime.now(UTC),
            )

    def test_farm_event_rejects_non_uuid_tenant(self):
        """Bug: tenant_id in FarmCreatedEvent accepts arbitrary strings."""
        from shared.events.models import FarmCreatedEvent

        with pytest.raises(ValidationError):
            FarmCreatedEvent(
                farm_id=uuid.uuid4(),
                tenant_id="not-a-valid-uuid",
                name="Test Farm",
                location_lat=24.7,
                location_lon=46.7,
                created_at=datetime.now(UTC),
            )


# =============================================================================
# 2. NDVI Value Bounds [-1, 1]
# =============================================================================


class TestNDVIBounds:
    """BUG TARGET: NDVI values outside physical range [-1.0, 1.0] being accepted."""

    def test_ndvi_greater_than_1_rejected(self):
        """Bug: NDVI value > 1.0 should be physically impossible."""
        from shared.satellite.sentinel_ndvi import NDVIResult, VegetationIndex

        with pytest.raises(ValueError, match="outside valid range"):
            NDVIResult(
                field_id="FIELD-001",
                timestamp=datetime.now(UTC),
                index_type=VegetationIndex.NDVI,
                mean_value=1.5,  # Invalid
                min_value=0.5,
                max_value=1.5,
                std_value=0.1,
                cloud_coverage=10.0,
                pixel_count=100,
            )

    def test_ndvi_less_than_minus_1_rejected(self):
        """Bug: NDVI value < -1.0 should be physically impossible."""
        from shared.satellite.sentinel_ndvi import NDVIResult, VegetationIndex

        with pytest.raises(ValueError, match="outside valid range"):
            NDVIResult(
                field_id="FIELD-001",
                timestamp=datetime.now(UTC),
                index_type=VegetationIndex.NDVI,
                mean_value=-1.5,  # Invalid
                min_value=-1.5,
                max_value=0.5,
                std_value=0.1,
                cloud_coverage=10.0,
                pixel_count=100,
            )

    def test_ndvi_exactly_1_accepted(self):
        """Boundary: NDVI = 1.0 is valid (dense vegetation)."""
        from shared.satellite.sentinel_ndvi import NDVIResult, VegetationIndex

        result = NDVIResult(
            field_id="FIELD-001",
            timestamp=datetime.now(UTC),
            index_type=VegetationIndex.NDVI,
            mean_value=1.0,
            min_value=0.5,
            max_value=1.0,
            std_value=0.1,
            cloud_coverage=10.0,
            pixel_count=100,
        )
        assert result.mean_value == 1.0

    def test_ndvi_exactly_minus_1_accepted(self):
        """Boundary: NDVI = -1.0 is valid (water bodies)."""
        from shared.satellite.sentinel_ndvi import NDVIResult, VegetationIndex

        result = NDVIResult(
            field_id="FIELD-001",
            timestamp=datetime.now(UTC),
            index_type=VegetationIndex.NDVI,
            mean_value=-1.0,
            min_value=-1.0,
            max_value=-0.5,
            std_value=0.1,
            cloud_coverage=10.0,
            pixel_count=100,
        )
        assert result.mean_value == -1.0

    def test_ndvi_update_event_validates_range(self):
        """Bug: FieldUpdatedEvent ndvi_value may not validate range."""
        from shared.events.models import FieldUpdatedEvent

        with pytest.raises(ValidationError):
            FieldUpdatedEvent(
                field_id=uuid.uuid4(),
                ndvi_value=1.5,  # Out of range
                updated_at=datetime.now(UTC),
            )

    def test_ndvi_update_event_negative_valid(self):
        """NDVI can be negative (water). Test near-boundary."""
        from shared.events.models import FieldUpdatedEvent

        event = FieldUpdatedEvent(
            field_id=uuid.uuid4(),
            ndvi_value=-0.99,  # Valid
            updated_at=datetime.now(UTC),
        )
        assert event.ndvi_value == -0.99

    def test_ndvi_update_event_rejects_below_minus_1(self):
        """Bug: FieldUpdatedEvent ndvi_value < -1 should be rejected."""
        from shared.events.models import FieldUpdatedEvent

        with pytest.raises(ValidationError):
            FieldUpdatedEvent(
                field_id=uuid.uuid4(),
                ndvi_value=-1.01,
                updated_at=datetime.now(UTC),
            )


# =============================================================================
# 3. Coordinate Validation (Lat/Lng)
# =============================================================================


class TestCoordinateValidation:
    """BUG TARGET: Invalid lat/lng coordinates accepted in farm/field models."""

    def test_latitude_out_of_range(self):
        """Bug: Latitude > 90 or < -90 accepted."""
        from shared.events.models import FarmCreatedEvent

        with pytest.raises(ValidationError):
            FarmCreatedEvent(
                farm_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                name="Test Farm",
                location_lat=91.0,  # Invalid
                location_lon=46.7,
                created_at=datetime.now(UTC),
            )

    def test_longitude_out_of_range(self):
        """Bug: Longitude > 180 or < -180 accepted."""
        from shared.events.models import FarmCreatedEvent

        with pytest.raises(ValidationError):
            FarmCreatedEvent(
                farm_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                name="Test Farm",
                location_lat=24.7,
                location_lon=181.0,  # Invalid
                created_at=datetime.now(UTC),
            )

    def test_negative_latitude(self):
        """Bug: Latitude = -91 should be rejected."""
        from shared.events.models import FarmCreatedEvent

        with pytest.raises(ValidationError):
            FarmCreatedEvent(
                farm_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                name="Test Farm",
                location_lat=-91.0,
                location_lon=46.7,
                created_at=datetime.now(UTC),
            )

    def test_boundary_coordinates_accepted(self):
        """Boundary: exact -90, 90, -180, 180 should all be valid."""
        from shared.events.models import FarmCreatedEvent

        # South pole
        event = FarmCreatedEvent(
            farm_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            name="South Pole Farm",
            location_lat=-90.0,
            location_lon=-180.0,
            created_at=datetime.now(UTC),
        )
        assert event.location_lat == -90.0

        # North pole
        event2 = FarmCreatedEvent(
            farm_id=uuid.uuid4(),
            tenant_id=uuid.uuid4(),
            name="North Pole Farm",
            location_lat=90.0,
            location_lon=180.0,
            created_at=datetime.now(UTC),
        )
        assert event2.location_lat == 90.0


# =============================================================================
# 4. Arabic Text Encoding
# =============================================================================


class TestArabicTextEncoding:
    """BUG TARGET: Arabic text corruption or encoding issues."""

    def test_arabic_name_preserved_in_field_event(self):
        """Bug: Arabic text garbled after model serialization/deserialization."""
        from shared.events.models import FieldCreatedEvent

        arabic_name = "حقل القمح الشمالي"
        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name="Northern Wheat Field",
            name_ar=arabic_name,
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            created_at=datetime.now(UTC),
        )
        assert event.name_ar == arabic_name

        # Test round-trip through JSON serialization
        json_str = event.model_dump_json()
        assert arabic_name in json_str

    def test_arabic_text_in_weather_alert(self):
        """Bug: Arabic strings in weather alerts lost or corrupted."""
        from shared.weather_alerts.models import AlertSeverity, AlertType, WeatherAlert

        alert = WeatherAlert(
            alert_type=AlertType.FROST,
            severity=AlertSeverity.CRITICAL,
            title="CRITICAL: Severe Frost Warning",
            title_ar="حرج: تحذير صقيع شديد",
            description="Temperatures dropping to -5C",
            description_ar="من المتوقع أن تنخفض درجات الحرارة إلى -5 درجة مئوية",
        )
        assert alert.title_ar == "حرج: تحذير صقيع شديد"
        # Verify to_dict preserves Arabic
        d = alert.to_dict()
        assert d["title_ar"] == "حرج: تحذير صقيع شديد"
        assert d["description_ar"].startswith("من المتوقع")

    def test_mixed_arabic_english_text(self):
        """Bug: Mixed Arabic/English text causes encoding issues."""
        from shared.events.models import FieldCreatedEvent

        mixed_name = "Field-001 (حقل-001)"
        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name=mixed_name,
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            created_at=datetime.now(UTC),
        )
        assert event.name == mixed_name

    def test_arabic_diacritics_preserved(self):
        """Bug: Arabic diacritics (tashkeel) stripped or corrupted."""
        from shared.events.models import FieldCreatedEvent

        text_with_diacritics = "حَقْلُ القَمْحِ"  # With tashkeel
        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name="Wheat Field",
            name_ar=text_with_diacritics,
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            created_at=datetime.now(UTC),
        )
        assert event.name_ar == text_with_diacritics


# =============================================================================
# 5. Empty String vs None Handling
# =============================================================================


class TestEmptyStringVsNone:
    """BUG TARGET: Confusion between empty string and None in optional fields."""

    def test_empty_name_rejected_in_field_event(self):
        """Bug: Empty name should be rejected (min_length=1)."""
        from shared.events.models import FieldCreatedEvent

        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid.uuid4(),
                farm_id=uuid.uuid4(),
                name="",  # Empty - should fail min_length=1
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
                created_at=datetime.now(UTC),
            )

    def test_none_name_ar_is_valid(self):
        """name_ar is optional (None should be accepted)."""
        from shared.events.models import FieldCreatedEvent

        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name="Valid Name",
            name_ar=None,  # Optional
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            created_at=datetime.now(UTC),
        )
        assert event.name_ar is None

    def test_empty_geometry_wkt_rejected(self):
        """Bug: Empty geometry WKT should be rejected (min_length=10)."""
        from shared.events.models import FieldCreatedEvent

        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid.uuid4(),
                farm_id=uuid.uuid4(),
                name="Test Field",
                geometry_wkt="",  # Empty
                created_at=datetime.now(UTC),
            )


# =============================================================================
# 6. Negative Values Where Not Allowed
# =============================================================================


class TestNegativeValues:
    """BUG TARGET: Negative values accepted in fields that must be non-negative."""

    def test_negative_area_rejected(self):
        """Bug: Negative area in hectares should be rejected."""
        from shared.events.models import FieldCreatedEvent

        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid.uuid4(),
                farm_id=uuid.uuid4(),
                name="Test Field",
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
                area_hectares=-5.0,  # Invalid
                created_at=datetime.now(UTC),
            )

    def test_zero_area_accepted(self):
        """Boundary: area=0 should be valid (point field)."""
        from shared.events.models import FieldCreatedEvent

        event = FieldCreatedEvent(
            field_id=uuid.uuid4(),
            farm_id=uuid.uuid4(),
            name="Test Field",
            geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
            area_hectares=0.0,
            created_at=datetime.now(UTC),
        )
        assert event.area_hectares == 0.0

    def test_negative_confidence_rejected(self):
        """Bug: confidence_score < 0 in advisory recommendations."""
        from shared.events.models import AdvisorRecommendationEvent

        with pytest.raises(ValidationError):
            AdvisorRecommendationEvent(
                recommendation_id=uuid.uuid4(),
                field_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                recommendation_type="irrigation",
                title="Test",
                description="Test description",
                priority="medium",
                confidence_score=-0.1,  # Invalid
                created_at=datetime.now(UTC),
            )

    def test_confidence_above_1_rejected(self):
        """Bug: confidence_score > 1.0 should be rejected."""
        from shared.events.models import AdvisorRecommendationEvent

        with pytest.raises(ValidationError):
            AdvisorRecommendationEvent(
                recommendation_id=uuid.uuid4(),
                field_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                recommendation_type="irrigation",
                title="Test",
                description="Test description",
                priority="medium",
                confidence_score=1.1,  # Invalid
                created_at=datetime.now(UTC),
            )


# =============================================================================
# 7. Floating Point Precision
# =============================================================================


class TestFloatingPointPrecision:
    """BUG TARGET: Floating point precision loss in financial calculations."""

    def test_fertilizer_cost_uses_decimal(self):
        """Bug: Fertilizer cost calculations using float lose precision."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_rate_for_nutrient(
            fertilizer_code="urea",
            target_nutrient="N",
            target_kg_per_ha=46.0,
            area_ha=10.0,
        )
        # Cost should be Decimal, not float
        assert isinstance(result.cost_per_ha, Decimal), "cost_per_ha should be Decimal to avoid precision loss"
        assert isinstance(result.cost_total, Decimal), "cost_total should be Decimal to avoid precision loss"

    def test_cost_calculation_no_floating_point_error(self):
        """Bug: 0.1 + 0.2 != 0.3 in float. Verify Decimal is used."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_rate_for_nutrient(
            fertilizer_code="urea",
            target_nutrient="N",
            target_kg_per_ha=1.0,
            area_ha=1.0,
        )
        # rate = (1.0 / 46.0) * 100 = 2.17391... kg/ha
        # cost = 2.50 * 2.17391... = ~5.43
        assert result.cost_per_ha > Decimal("0")


# =============================================================================
# 8. Priority/Status Pattern Validation
# =============================================================================


class TestPatternValidation:
    """BUG TARGET: Invalid enum values accepted in regex-validated fields."""

    def test_invalid_priority_rejected(self):
        """Bug: Invalid priority value bypasses pattern validation."""
        from shared.events.models import TaskCreatedEvent

        with pytest.raises(ValidationError):
            TaskCreatedEvent(
                task_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                title="Test Task",
                priority="SUPER_URGENT",  # Not in pattern
                created_at=datetime.now(UTC),
            )

    def test_valid_priorities_accepted(self):
        """Verify all valid priority values work."""
        from shared.events.models import TaskCreatedEvent

        for priority in ["low", "medium", "high", "urgent"]:
            event = TaskCreatedEvent(
                task_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                title="Test Task",
                priority=priority,
                created_at=datetime.now(UTC),
            )
            assert event.priority == priority

    def test_invalid_recommendation_type_rejected(self):
        """Bug: Invalid recommendation_type bypasses validation."""
        from shared.events.models import AdvisorRecommendationEvent

        with pytest.raises(ValidationError):
            AdvisorRecommendationEvent(
                recommendation_id=uuid.uuid4(),
                field_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                recommendation_type="magical_healing",  # Not valid
                title="Test",
                description="Test",
                priority="medium",
                confidence_score=0.8,
                created_at=datetime.now(UTC),
            )

    def test_invalid_alert_type_rejected(self):
        """Bug: Invalid alert_type bypasses validation."""
        from shared.events.models import AlertCreatedEvent

        with pytest.raises(ValidationError):
            AlertCreatedEvent(
                alert_id=uuid.uuid4(),
                tenant_id=uuid.uuid4(),
                alert_type="alien_invasion",  # Not valid
                severity="warning",
                title="Test",
                message="Test",
                created_at=datetime.now(UTC),
            )

    def test_name_max_length_enforced(self):
        """Bug: Field name exceeding max_length is accepted."""
        from shared.events.models import FieldCreatedEvent

        long_name = "A" * 121  # Exceeds max_length=120
        with pytest.raises(ValidationError):
            FieldCreatedEvent(
                field_id=uuid.uuid4(),
                farm_id=uuid.uuid4(),
                name=long_name,
                geometry_wkt="POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
                created_at=datetime.now(UTC),
            )
