"""
Tests for Water Management Module - اختبارات وحدة إدارة المياه

Covers:
- Enum values (WaterSourceType, WaterSourceStatus, WaterQualityClass, etc.)
- WaterSource model, properties, and serialization
- WaterMeter model and consumption calculation
- WaterRight model, validity, and allocation tracking
- WaterAllocation model and utilization
- WaterQualityTest model and classification
- WaterConsumptionRecord and IrrigationEvent models
- WaterAlert model and serialization
- SaudiWaterStandards constants and regional limits
- EfficiencyBenchmarks for irrigation methods and crops
- IrrigationEfficiencyMetrics calculations
- FieldWaterBalance water balance calculations
- WaterLevelMonitor alert generation
- WaterLevelReading and WaterLevelTrend models
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

import pytest

from shared.water_management.efficiency import (
    EfficiencyBenchmarks,
    FieldWaterBalance,
    IrrigationEfficiencyMetrics,
)
from shared.water_management.models import (
    AlertSeverity,
    AllocationPeriod,
    ComplianceStatus,
    GeoLocation,
    IrrigationEvent,
    IrrigationMethod,
    MeterType,
    SaudiWaterStandards,
    WaterAlert,
    WaterAllocation,
    WaterConsumptionRecord,
    WaterMeter,
    WaterQualityClass,
    WaterQualityParameter,
    WaterQualityTest,
    WaterRight,
    WaterRightType,
    WaterSource,
    WaterSourceStatus,
    WaterSourceType,
)
from shared.water_management.monitoring import (
    WaterLevelMonitor,
    WaterLevelReading,
    WaterLevelTrend,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Enum Tests - اختبارات التعدادات
# ═══════════════════════════════════════════════════════════════════════════════


class TestWaterEnums:
    """Test water management enumerations."""

    def test_water_source_types(self):
        assert WaterSourceType.WELL == "well"
        assert WaterSourceType.ARTESIAN_WELL == "artesian_well"
        assert WaterSourceType.TANK == "tank"
        assert WaterSourceType.RESERVOIR == "reservoir"
        assert WaterSourceType.CANAL == "canal"
        assert WaterSourceType.TREATED_WASTEWATER == "treated_wastewater"
        assert WaterSourceType.DESALINATED == "desalinated"
        assert WaterSourceType.RAINWATER == "rainwater"
        assert WaterSourceType.SPRING == "spring"

    def test_water_source_status(self):
        assert WaterSourceStatus.ACTIVE == "active"
        assert WaterSourceStatus.INACTIVE == "inactive"
        assert WaterSourceStatus.MAINTENANCE == "maintenance"
        assert WaterSourceStatus.DEPLETED == "depleted"
        assert WaterSourceStatus.CONTAMINATED == "contaminated"
        assert WaterSourceStatus.PERMIT_EXPIRED == "permit_expired"

    def test_water_quality_class(self):
        assert WaterQualityClass.CLASS_A == "A"
        assert WaterQualityClass.CLASS_B == "B"
        assert WaterQualityClass.CLASS_C == "C"
        assert WaterQualityClass.CLASS_D == "D"
        assert WaterQualityClass.UNFIT == "unfit"

    def test_water_right_types(self):
        assert WaterRightType.TRADITIONAL == "traditional"
        assert WaterRightType.LICENSED == "licensed"
        assert WaterRightType.PERMIT == "permit"
        assert WaterRightType.EMERGENCY == "emergency"
        assert WaterRightType.TRANSFERRED == "transferred"

    def test_allocation_periods(self):
        assert AllocationPeriod.DAILY == "daily"
        assert AllocationPeriod.WEEKLY == "weekly"
        assert AllocationPeriod.MONTHLY == "monthly"
        assert AllocationPeriod.SEASONAL == "seasonal"
        assert AllocationPeriod.ANNUAL == "annual"

    def test_irrigation_methods(self):
        assert IrrigationMethod.DRIP == "drip"
        assert IrrigationMethod.SPRINKLER == "sprinkler"
        assert IrrigationMethod.CENTER_PIVOT == "center_pivot"
        assert IrrigationMethod.FLOOD == "flood"
        assert IrrigationMethod.FURROW == "furrow"
        assert IrrigationMethod.SUBSURFACE == "subsurface"
        assert IrrigationMethod.MANUAL == "manual"

    def test_alert_severity(self):
        assert AlertSeverity.INFO == "info"
        assert AlertSeverity.LOW == "low"
        assert AlertSeverity.MEDIUM == "medium"
        assert AlertSeverity.HIGH == "high"
        assert AlertSeverity.CRITICAL == "critical"

    def test_compliance_status(self):
        assert ComplianceStatus.COMPLIANT == "compliant"
        assert ComplianceStatus.NON_COMPLIANT == "non_compliant"
        assert ComplianceStatus.PENDING_REVIEW == "pending_review"
        assert ComplianceStatus.WARNING == "warning"

    def test_meter_types(self):
        assert MeterType.MECHANICAL == "mechanical"
        assert MeterType.ULTRASONIC == "ultrasonic"
        assert MeterType.SMART == "smart"


# ═══════════════════════════════════════════════════════════════════════════════
# GeoLocation Tests - اختبارات الموقع الجغرافي
# ═══════════════════════════════════════════════════════════════════════════════


class TestGeoLocation:
    """Test GeoLocation dataclass."""

    def test_basic_creation(self):
        loc = GeoLocation(lat=24.7, lng=46.7)
        assert loc.lat == 24.7
        assert loc.lng == 46.7
        assert loc.elevation_m is None

    def test_with_elevation(self):
        loc = GeoLocation(lat=24.7, lng=46.7, elevation_m=600.0, accuracy_m=3.0)
        assert loc.elevation_m == 600.0
        assert loc.accuracy_m == 3.0


# ═══════════════════════════════════════════════════════════════════════════════
# WaterMeter Tests - اختبارات عداد المياه
# ═══════════════════════════════════════════════════════════════════════════════


def _create_sample_meter(**overrides) -> WaterMeter:
    defaults = {
        "id": "meter-001",
        "source_id": "src-001",
        "tenant_id": "tenant-001",
        "name": "Main Well Meter",
        "name_ar": "عداد البئر الرئيسي",
        "meter_type": MeterType.SMART,
        "model": "SWM-200",
        "serial_number": "SN12345",
        "manufacturer": "SAHOOL",
    }
    defaults.update(overrides)
    return WaterMeter(**defaults)


class TestWaterMeter:
    """Test WaterMeter model."""

    def test_meter_creation(self):
        meter = _create_sample_meter()
        assert meter.id == "meter-001"
        assert meter.name_ar == "عداد البئر الرئيسي"
        assert meter.is_active is True
        assert meter.is_certified is True

    def test_meter_calculate_consumption_normal(self):
        meter = _create_sample_meter(current_reading_m3=1500.0, calibration_factor=1.0)
        consumption = meter.calculate_consumption(previous_reading=1000.0)
        assert consumption == 500.0

    def test_meter_calculate_consumption_with_calibration(self):
        meter = _create_sample_meter(current_reading_m3=1500.0, calibration_factor=1.05)
        consumption = meter.calculate_consumption(previous_reading=1000.0)
        assert consumption == pytest.approx(525.0)

    def test_meter_calculate_consumption_rollover(self):
        meter = _create_sample_meter(current_reading_m3=100.0)
        consumption = meter.calculate_consumption(previous_reading=999900.0)
        assert consumption > 0  # Should handle rollover

    def test_meter_to_dict(self):
        meter = _create_sample_meter()
        d = meter.to_dict()
        assert d["id"] == "meter-001"
        assert d["meter_type"] == "smart"
        assert d["is_active"] is True
        assert d["name_ar"] == "عداد البئر الرئيسي"


# ═══════════════════════════════════════════════════════════════════════════════
# WaterSource Tests - اختبارات مصدر المياه
# ═══════════════════════════════════════════════════════════════════════════════


def _create_sample_source(**overrides) -> WaterSource:
    defaults = {
        "id": "src-001",
        "tenant_id": "tenant-001",
        "farm_id": "farm-001",
        "name": "Main Well",
        "name_ar": "البئر الرئيسي",
        "source_type": WaterSourceType.WELL,
    }
    defaults.update(overrides)
    return WaterSource(**defaults)


class TestWaterSource:
    """Test WaterSource model."""

    def test_source_creation(self):
        src = _create_sample_source()
        assert src.id == "src-001"
        assert src.source_type == WaterSourceType.WELL
        assert src.status == WaterSourceStatus.ACTIVE
        assert src.water_quality_class == WaterQualityClass.CLASS_B

    def test_license_valid(self):
        src = _create_sample_source(
            license_expiry_at=date.today() + timedelta(days=365),
        )
        assert src.is_license_valid is True

    def test_license_expired(self):
        src = _create_sample_source(
            license_expiry_at=date.today() - timedelta(days=1),
        )
        assert src.is_license_valid is False

    def test_license_no_expiry(self):
        src = _create_sample_source()
        assert src.is_license_valid is False

    def test_extraction_remaining(self):
        src = _create_sample_source(
            licensed_extraction_m3_year=10000.0,
            total_extracted_m3_ytd=3000.0,
        )
        assert src.extraction_remaining_m3_year == 7000.0

    def test_extraction_remaining_exceeded(self):
        src = _create_sample_source(
            licensed_extraction_m3_year=10000.0,
            total_extracted_m3_ytd=12000.0,
        )
        assert src.extraction_remaining_m3_year == 0

    def test_extraction_remaining_none(self):
        src = _create_sample_source()
        assert src.extraction_remaining_m3_year is None

    def test_extraction_utilization_percent(self):
        src = _create_sample_source(
            licensed_extraction_m3_year=10000.0,
            total_extracted_m3_ytd=5000.0,
        )
        assert src.extraction_utilization_percent == pytest.approx(50.0)

    def test_extraction_utilization_none(self):
        src = _create_sample_source()
        assert src.extraction_utilization_percent is None

    def test_source_to_dict(self):
        src = _create_sample_source(
            location=GeoLocation(lat=24.7, lng=46.7),
            max_capacity_m3=5000.0,
        )
        d = src.to_dict()
        assert d["id"] == "src-001"
        assert d["source_type"] == "well"
        assert d["location"]["lat"] == 24.7
        assert d["capacity"]["max_capacity_m3"] == 5000.0

    def test_source_to_dict_well_info(self):
        src = _create_sample_source(
            source_type=WaterSourceType.WELL,
            well_depth_m=200.0,
            aquifer_name="Saq",
            aquifer_name_ar="طبقة الساق",
        )
        d = src.to_dict()
        assert d["well_info"]["depth_m"] == 200.0
        assert d["well_info"]["aquifer_name_ar"] == "طبقة الساق"

    def test_source_to_dict_non_well_no_well_info(self):
        src = _create_sample_source(source_type=WaterSourceType.TANK)
        d = src.to_dict()
        assert d["well_info"] is None


# ═══════════════════════════════════════════════════════════════════════════════
# WaterRight Tests - اختبارات حقوق المياه
# ═══════════════════════════════════════════════════════════════════════════════


def _create_sample_right(**overrides) -> WaterRight:
    defaults = {
        "id": "right-001",
        "tenant_id": "tenant-001",
        "farm_id": "farm-001",
    }
    defaults.update(overrides)
    return WaterRight(**defaults)


class TestWaterRight:
    """Test WaterRight model."""

    def test_right_creation(self):
        right = _create_sample_right()
        assert right.right_type == WaterRightType.LICENSED
        assert right.status == ComplianceStatus.COMPLIANT

    def test_right_is_valid_active(self):
        right = _create_sample_right(
            valid_from=date.today() - timedelta(days=30),
            valid_until=date.today() + timedelta(days=335),
        )
        assert right.is_valid is True

    def test_right_is_valid_expired(self):
        right = _create_sample_right(
            valid_from=date.today() - timedelta(days=400),
            valid_until=date.today() - timedelta(days=35),
        )
        assert right.is_valid is False

    def test_right_is_valid_not_yet_started(self):
        right = _create_sample_right(
            valid_from=date.today() + timedelta(days=30),
        )
        assert right.is_valid is False

    def test_right_is_valid_no_dates(self):
        right = _create_sample_right()
        assert right.is_valid is True

    def test_remaining_allocation_annual(self):
        right = _create_sample_right(
            allocated_m3_year=50000.0,
            used_m3_ytd=20000.0,
            allocation_period=AllocationPeriod.ANNUAL,
        )
        assert right.remaining_allocation_m3 == 30000.0

    def test_remaining_allocation_monthly(self):
        right = _create_sample_right(
            allocated_m3_month=5000.0,
            used_m3_current_period=3000.0,
            allocation_period=AllocationPeriod.MONTHLY,
        )
        assert right.remaining_allocation_m3 == 2000.0

    def test_utilization_percent_annual(self):
        right = _create_sample_right(
            allocated_m3_year=50000.0,
            used_m3_ytd=25000.0,
        )
        assert right.utilization_percent == pytest.approx(50.0)

    def test_utilization_percent_zero_allocation(self):
        right = _create_sample_right(allocated_m3_year=0.0)
        assert right.utilization_percent == 0.0

    def test_right_to_dict(self):
        right = _create_sample_right(
            permit_number="MEWA-2024-001",
            allocated_m3_year=50000.0,
            crop_restrictions=["wheat", "barley"],
        )
        d = right.to_dict()
        assert d["permit_number"] == "MEWA-2024-001"
        assert d["allocation"]["annual_m3"] == 50000.0
        assert d["conditions"]["crop_restrictions"] == ["wheat", "barley"]


# ═══════════════════════════════════════════════════════════════════════════════
# WaterAllocation Tests - اختبارات تخصيص المياه
# ═══════════════════════════════════════════════════════════════════════════════


class TestWaterAllocation:
    """Test WaterAllocation model."""

    def test_allocation_creation(self):
        alloc = WaterAllocation(
            id="alloc-001",
            tenant_id="tenant-001",
            farm_id="farm-001",
            field_id="field-001",
            water_right_id="right-001",
        )
        assert alloc.irrigation_method == IrrigationMethod.DRIP
        assert alloc.priority == 5

    def test_allocation_remaining(self):
        alloc = WaterAllocation(
            id="alloc-001",
            tenant_id="t",
            farm_id="f",
            field_id="fl",
            water_right_id="r",
            allocated_m3=10000.0,
            consumed_m3=6000.0,
        )
        assert alloc.remaining_m3 == 4000.0

    def test_allocation_remaining_over_consumed(self):
        alloc = WaterAllocation(
            id="alloc-001",
            tenant_id="t",
            farm_id="f",
            field_id="fl",
            water_right_id="r",
            allocated_m3=10000.0,
            consumed_m3=12000.0,
        )
        assert alloc.remaining_m3 == 0

    def test_allocation_utilization(self):
        alloc = WaterAllocation(
            id="alloc-001",
            tenant_id="t",
            farm_id="f",
            field_id="fl",
            water_right_id="r",
            allocated_m3=10000.0,
            consumed_m3=7500.0,
        )
        assert alloc.utilization_percent == pytest.approx(75.0)

    def test_allocation_utilization_zero(self):
        alloc = WaterAllocation(
            id="alloc-001",
            tenant_id="t",
            farm_id="f",
            field_id="fl",
            water_right_id="r",
            allocated_m3=0.0,
        )
        assert alloc.utilization_percent == 0.0

    def test_allocation_to_dict(self):
        alloc = WaterAllocation(
            id="alloc-001",
            tenant_id="t",
            farm_id="f",
            field_id="fl",
            water_right_id="r",
            crop_type="wheat",
            crop_type_ar="قمح",
            allocated_m3=5000.0,
            consumed_m3=2000.0,
        )
        d = alloc.to_dict()
        assert d["crop"]["type"] == "wheat"
        assert d["crop"]["type_ar"] == "قمح"
        assert d["allocation"]["remaining_m3"] == 3000.0
        assert d["allocation"]["utilization_percent"] == pytest.approx(40.0)


# ═══════════════════════════════════════════════════════════════════════════════
# WaterQualityTest Tests - اختبارات جودة المياه
# ═══════════════════════════════════════════════════════════════════════════════


class TestWaterQualityTest:
    """Test WaterQualityTest model."""

    def test_classify_water_ec_class_a(self):
        test = WaterQualityTest(
            id="qt-001",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
            electrical_conductivity_ds_m=0.5,
        )
        assert test.classify_water() == WaterQualityClass.CLASS_A

    def test_classify_water_ec_class_b(self):
        test = WaterQualityTest(
            id="qt-002",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
            electrical_conductivity_ds_m=2.0,
        )
        assert test.classify_water() == WaterQualityClass.CLASS_B

    def test_classify_water_ec_class_c(self):
        test = WaterQualityTest(
            id="qt-003",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
            electrical_conductivity_ds_m=5.0,
        )
        assert test.classify_water() == WaterQualityClass.CLASS_C

    def test_classify_water_ec_class_d(self):
        test = WaterQualityTest(
            id="qt-004",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
            electrical_conductivity_ds_m=8.0,
        )
        assert test.classify_water() == WaterQualityClass.CLASS_D

    def test_classify_water_ec_unfit(self):
        test = WaterQualityTest(
            id="qt-005",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
            electrical_conductivity_ds_m=12.0,
        )
        assert test.classify_water() == WaterQualityClass.UNFIT

    def test_classify_water_tds_class_a(self):
        test = WaterQualityTest(
            id="qt-006",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
            tds_ppm=300.0,
        )
        assert test.classify_water() == WaterQualityClass.CLASS_A

    def test_classify_water_tds_class_b(self):
        test = WaterQualityTest(
            id="qt-007",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
            tds_ppm=1500.0,
        )
        assert test.classify_water() == WaterQualityClass.CLASS_B

    def test_classify_water_tds_unfit(self):
        test = WaterQualityTest(
            id="qt-008",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
            tds_ppm=7000.0,
        )
        assert test.classify_water() == WaterQualityClass.UNFIT

    def test_classify_water_default(self):
        test = WaterQualityTest(
            id="qt-009",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
        )
        assert test.classify_water() == WaterQualityClass.CLASS_B

    def test_quality_test_to_dict(self):
        test = WaterQualityTest(
            id="qt-001",
            source_id="src-001",
            tenant_id="tenant-001",
            tested_at=datetime.now(UTC),
            ph=7.2,
            electrical_conductivity_ds_m=1.5,
            tds_ppm=1000.0,
            lab_name="MEWA Lab",
            lab_name_ar="مختبر وزارة البيئة",
            suitable_for_irrigation=True,
            suitable_crops=["wheat", "barley"],
        )
        d = test.to_dict()
        assert d["key_parameters"]["ph"] == 7.2
        assert d["key_parameters"]["ec_ds_m"] == 1.5
        assert d["lab"]["name_ar"] == "مختبر وزارة البيئة"
        assert d["assessment"]["suitable_for_irrigation"] is True

    def test_quality_parameters(self):
        param = WaterQualityParameter(
            parameter="pH",
            parameter_ar="الأس الهيدروجيني",
            value=7.5,
            unit="",
            min_acceptable=6.5,
            max_acceptable=8.5,
            is_within_limits=True,
        )
        d = param.to_dict()
        assert d["parameter"] == "pH"
        assert d["parameter_ar"] == "الأس الهيدروجيني"
        assert d["is_within_limits"] is True


# ═══════════════════════════════════════════════════════════════════════════════
# WaterConsumptionRecord Tests - اختبارات سجل الاستهلاك
# ═══════════════════════════════════════════════════════════════════════════════


class TestWaterConsumptionRecord:
    """Test WaterConsumptionRecord model."""

    def test_record_creation(self):
        record = WaterConsumptionRecord(
            id="rec-001",
            tenant_id="tenant-001",
            farm_id="farm-001",
            source_id="src-001",
            volume_m3=150.0,
            purpose="irrigation",
            purpose_ar="ري",
        )
        assert record.volume_m3 == 150.0
        assert record.purpose == "irrigation"
        assert record.purpose_ar == "ري"

    def test_record_to_dict(self):
        record = WaterConsumptionRecord(
            id="rec-001",
            tenant_id="tenant-001",
            farm_id="farm-001",
            source_id="src-001",
            volume_m3=200.0,
            irrigation_method=IrrigationMethod.DRIP,
            crop_type="wheat",
        )
        d = record.to_dict()
        assert d["consumption"]["volume_m3"] == 200.0
        assert d["irrigation"]["method"] == "drip"
        assert d["crop_type"] == "wheat"


# ═══════════════════════════════════════════════════════════════════════════════
# IrrigationEvent Tests - اختبارات حدث الري
# ═══════════════════════════════════════════════════════════════════════════════


class TestIrrigationEvent:
    """Test IrrigationEvent model."""

    def test_event_creation(self):
        event = IrrigationEvent(
            id="evt-001",
            tenant_id="tenant-001",
            farm_id="farm-001",
            field_id="field-001",
            source_id="src-001",
            volume_m3=50.0,
            depth_mm=25.0,
            duration_minutes=120,
            irrigation_method=IrrigationMethod.CENTER_PIVOT,
        )
        assert event.volume_m3 == 50.0
        assert event.duration_minutes == 120
        assert event.status == "completed"

    def test_event_to_dict(self):
        event = IrrigationEvent(
            id="evt-001",
            tenant_id="t",
            farm_id="f",
            field_id="fl",
            source_id="s",
            volume_m3=50.0,
            soil_moisture_before=25.0,
            soil_moisture_after=45.0,
            trigger_type="sensor",
            trigger_type_ar="حساس",
        )
        d = event.to_dict()
        assert d["application"]["volume_m3"] == 50.0
        assert d["soil_moisture"]["before"] == 25.0
        assert d["soil_moisture"]["after"] == 45.0
        assert d["trigger"]["type"] == "sensor"
        assert d["trigger"]["type_ar"] == "حساس"


# ═══════════════════════════════════════════════════════════════════════════════
# WaterAlert Tests - اختبارات التنبيهات
# ═══════════════════════════════════════════════════════════════════════════════


class TestWaterAlert:
    """Test WaterAlert model."""

    def test_alert_creation(self):
        alert = WaterAlert(
            id="alert-001",
            tenant_id="tenant-001",
            farm_id="farm-001",
            alert_type="low_level",
            severity=AlertSeverity.HIGH,
            title_en="Low Water Level",
            title_ar="مستوى مياه منخفض",
        )
        assert alert.severity == AlertSeverity.HIGH
        assert alert.acknowledged is False
        assert alert.resolved is False

    def test_alert_to_dict(self):
        alert = WaterAlert(
            id="alert-001",
            tenant_id="tenant-001",
            farm_id="farm-001",
            alert_type="quality_issue",
            severity=AlertSeverity.CRITICAL,
            title_en="Water Quality Issue",
            title_ar="مشكلة في جودة المياه",
            message_en="EC level exceeded threshold",
            message_ar="مستوى الموصلية الكهربائية تجاوز الحد",
            triggered_value=8.5,
            threshold_value=6.0,
            unit="dS/m",
        )
        d = alert.to_dict()
        assert d["severity"] == "critical"
        assert d["title"]["ar"] == "مشكلة في جودة المياه"
        assert d["context"]["triggered_value"] == 8.5
        assert d["context"]["unit"] == "dS/m"


# ═══════════════════════════════════════════════════════════════════════════════
# SaudiWaterStandards Tests - اختبارات المعايير السعودية
# ═══════════════════════════════════════════════════════════════════════════════


class TestSaudiWaterStandards:
    """Test Saudi water regulation constants."""

    def test_ec_thresholds(self):
        assert SaudiWaterStandards.EC_CLASS_A_MAX == 0.7
        assert SaudiWaterStandards.EC_CLASS_B_MAX == 3.0
        assert SaudiWaterStandards.EC_CLASS_C_MAX == 6.0
        assert SaudiWaterStandards.EC_CLASS_D_MAX == 10.0

    def test_tds_thresholds(self):
        assert SaudiWaterStandards.TDS_CLASS_A_MAX == 450
        assert SaudiWaterStandards.TDS_CLASS_B_MAX == 2000

    def test_ph_range(self):
        assert SaudiWaterStandards.PH_MIN == 6.5
        assert SaudiWaterStandards.PH_MAX == 8.5

    def test_extraction_limit_central(self):
        limit = SaudiWaterStandards.get_extraction_limit("central")
        assert limit == 8000

    def test_extraction_limit_arabic(self):
        limit = SaudiWaterStandards.get_extraction_limit("الشرقية")
        assert limit == 10000

    def test_extraction_limit_western(self):
        assert SaudiWaterStandards.get_extraction_limit("western") == 6000

    def test_meter_requirements(self):
        assert SaudiWaterStandards.METER_REQUIRED_WELL_DEPTH_M == 50
        assert SaudiWaterStandards.METER_CALIBRATION_INTERVAL_MONTHS == 12

    def test_reporting_requirements(self):
        assert SaudiWaterStandards.CONSUMPTION_REPORT_FREQUENCY_DAYS == 90
        assert SaudiWaterStandards.QUALITY_TEST_FREQUENCY_MONTHS == 6


# ═══════════════════════════════════════════════════════════════════════════════
# EfficiencyBenchmarks Tests - اختبارات معايير الكفاءة
# ═══════════════════════════════════════════════════════════════════════════════


class TestEfficiencyBenchmarks:
    """Test irrigation efficiency benchmarks."""

    def test_drip_efficiency(self):
        min_v, good, excellent = EfficiencyBenchmarks.get_app_efficiency_benchmark(IrrigationMethod.DRIP)
        assert min_v == 85.0
        assert good == 90.0
        assert excellent == 95.0

    def test_sprinkler_efficiency(self):
        min_v, good, excellent = EfficiencyBenchmarks.get_app_efficiency_benchmark(IrrigationMethod.SPRINKLER)
        assert min_v == 70.0

    def test_pivot_efficiency(self):
        min_v, good, excellent = EfficiencyBenchmarks.get_app_efficiency_benchmark(IrrigationMethod.CENTER_PIVOT)
        assert min_v == 75.0

    def test_flood_efficiency(self):
        min_v, good, excellent = EfficiencyBenchmarks.get_app_efficiency_benchmark(IrrigationMethod.FLOOD)
        assert min_v == 40.0
        assert excellent == 65.0

    def test_furrow_efficiency(self):
        min_v, _, _ = EfficiencyBenchmarks.get_app_efficiency_benchmark(IrrigationMethod.FURROW)
        assert min_v == 50.0

    def test_unknown_method_defaults(self):
        min_v, good, excellent = EfficiencyBenchmarks.get_app_efficiency_benchmark(IrrigationMethod.MANUAL)
        assert min_v == 50.0
        assert excellent == 85.0

    def test_water_productivity_wheat(self):
        min_v, good, excellent = EfficiencyBenchmarks.get_water_productivity_benchmark("wheat")
        assert min_v == 0.8
        assert excellent == 1.5

    def test_water_productivity_wheat_arabic(self):
        min_v, _, _ = EfficiencyBenchmarks.get_water_productivity_benchmark("قمح")
        assert min_v == 0.8

    def test_water_productivity_date_palm(self):
        _, good, _ = EfficiencyBenchmarks.get_water_productivity_benchmark("date_palm")
        assert good == 2.5

    def test_water_productivity_date_palm_arabic(self):
        _, _, excellent = EfficiencyBenchmarks.get_water_productivity_benchmark("نخيل")
        assert excellent == 3.5

    def test_water_productivity_tomato(self):
        _, good, _ = EfficiencyBenchmarks.get_water_productivity_benchmark("tomato")
        assert good == 15.0

    def test_water_productivity_unknown_crop(self):
        min_v, good, excellent = EfficiencyBenchmarks.get_water_productivity_benchmark("unknown_crop")
        assert min_v == 0.5
        assert good == 1.0
        assert excellent == 2.0


# ═══════════════════════════════════════════════════════════════════════════════
# IrrigationEfficiencyMetrics Tests - اختبارات مقاييس كفاءة الري
# ═══════════════════════════════════════════════════════════════════════════════


class TestIrrigationEfficiencyMetrics:
    """Test efficiency metrics calculations."""

    def _create_metrics(self, **overrides) -> IrrigationEfficiencyMetrics:
        defaults = {
            "id": "eff-001",
            "tenant_id": "tenant-001",
            "farm_id": "farm-001",
            "field_id": "field-001",
            "calculation_date": datetime.now(UTC),
        }
        defaults.update(overrides)
        return IrrigationEfficiencyMetrics(**defaults)

    def test_calculate_overall_efficiency(self):
        m = self._create_metrics(
            application_efficiency=90.0,
            distribution_uniformity=85.0,
            conveyance_efficiency=95.0,
        )
        result = m.calculate_overall_efficiency()
        # 90 * (85/100) * (95/100) = 72.675
        assert result == pytest.approx(72.675)
        assert m.overall_efficiency == result

    def test_calculate_overall_efficiency_app_only(self):
        m = self._create_metrics(application_efficiency=85.0)
        result = m.calculate_overall_efficiency()
        assert result == 85.0

    def test_calculate_overall_efficiency_none(self):
        m = self._create_metrics()
        assert m.calculate_overall_efficiency() is None

    def test_calculate_wue(self):
        m = self._create_metrics(
            water_supplied_m3=10000.0,
            crop_yield_kg=12000.0,
        )
        wue = m.calculate_wue()
        assert wue == pytest.approx(1.2)

    def test_calculate_wue_zero_water(self):
        m = self._create_metrics(water_supplied_m3=0.0, crop_yield_kg=100.0)
        assert m.calculate_wue() is None

    def test_calculate_wue_no_yield(self):
        m = self._create_metrics(water_supplied_m3=10000.0)
        assert m.calculate_wue() is None

    def test_calculate_economic_productivity(self):
        m = self._create_metrics(
            water_supplied_m3=10000.0,
            crop_value_sar=50000.0,
        )
        econ = m.calculate_economic_productivity()
        assert econ == pytest.approx(5.0)

    def test_calculate_economic_productivity_zero(self):
        m = self._create_metrics(water_supplied_m3=0.0, crop_value_sar=50000.0)
        assert m.calculate_economic_productivity() is None

    def test_metrics_to_dict(self):
        m = self._create_metrics(
            water_supplied_m3=10000.0,
            application_efficiency=90.0,
            efficiency_rating="good",
            efficiency_rating_ar="جيد",
        )
        d = m.to_dict()
        assert d["water_volumes"]["supplied_m3"] == 10000.0
        assert d["efficiency_metrics"]["application_efficiency"] == 90.0
        assert d["rating"]["level"] == "good"
        assert d["rating"]["level_ar"] == "جيد"


# ═══════════════════════════════════════════════════════════════════════════════
# FieldWaterBalance Tests - اختبارات ميزان المياه
# ═══════════════════════════════════════════════════════════════════════════════


class TestFieldWaterBalance:
    """Test field water balance calculations."""

    def _create_balance(self, **overrides) -> FieldWaterBalance:
        defaults = {
            "field_id": "field-001",
            "tenant_id": "tenant-001",
            "period_start": date(2026, 1, 1),
            "period_end": date(2026, 3, 31),
        }
        defaults.update(overrides)
        return FieldWaterBalance(**defaults)

    def test_balanced_water_budget(self):
        bal = self._create_balance(
            irrigation_m3=500.0,
            rainfall_m3=100.0,
            et_crop_m3=400.0,
            deep_percolation_m3=50.0,
            runoff_m3=50.0,
            soil_water_start_m3=200.0,
            soil_water_end_m3=300.0,
        )
        error = bal.calculate_balance()
        # Inputs: 500 + 100 = 600
        # Outputs: 400 + 50 + 50 = 500
        # Calculated storage change: 600 - 500 = 100
        # Actual storage change: 300 - 200 = 100
        # Error: 100 - 100 = 0
        assert error == pytest.approx(0.0)

    def test_positive_balance_error(self):
        bal = self._create_balance(
            irrigation_m3=500.0,
            rainfall_m3=100.0,
            et_crop_m3=300.0,
            deep_percolation_m3=50.0,
            runoff_m3=50.0,
            soil_water_start_m3=200.0,
            soil_water_end_m3=250.0,
        )
        error = bal.calculate_balance()
        # Inputs: 600, Outputs: 400, Calc storage: 200
        # Actual storage: 50
        # Error: 200 - 50 = 150
        assert error == pytest.approx(150.0)

    def test_balance_error_percent(self):
        bal = self._create_balance(
            irrigation_m3=1000.0,
            et_crop_m3=800.0,
            soil_water_start_m3=100.0,
            soil_water_end_m3=100.0,
        )
        bal.calculate_balance()
        # Inputs: 1000, Outputs: 800, Calc storage: 200, Actual: 0
        # Error: 200/1000 * 100 = 20%
        assert bal.balance_error_percent == pytest.approx(20.0)

    def test_balance_to_dict(self):
        bal = self._create_balance(
            irrigation_m3=500.0,
            area_ha=10.0,
        )
        d = bal.to_dict()
        assert d["field_id"] == "field-001"
        assert d["area_ha"] == 10.0
        assert d["inputs"]["irrigation_m3"] == 500.0


# ═══════════════════════════════════════════════════════════════════════════════
# WaterLevelMonitor Tests - اختبارات مراقب مستوى المياه
# ═══════════════════════════════════════════════════════════════════════════════


class TestWaterLevelMonitor:
    """Test WaterLevelMonitor alert system."""

    def _create_monitor_and_source(self, max_capacity=10000.0):
        monitor = WaterLevelMonitor(tenant_id="tenant-001")
        source = _create_sample_source(max_capacity_m3=max_capacity)
        return monitor, source

    def test_record_reading(self):
        monitor, source = self._create_monitor_and_source()
        reading = monitor.record_reading(source, level_m3=5000.0)
        assert reading.level_m3 == 5000.0
        assert reading.level_percent == pytest.approx(50.0)

    def test_record_reading_auto_percent(self):
        monitor, source = self._create_monitor_and_source(max_capacity=10000.0)
        reading = monitor.record_reading(source, level_m3=2500.0)
        assert reading.level_percent == pytest.approx(25.0)

    def test_record_reading_well_drawdown(self):
        monitor, source = self._create_monitor_and_source()
        reading = monitor.record_reading(
            source,
            static_level_m=50.0,
            dynamic_level_m=58.0,
        )
        assert reading.drawdown_m == pytest.approx(8.0)

    def test_critical_low_level_alert(self):
        monitor, source = self._create_monitor_and_source()
        reading = monitor.record_reading(source, level_m3=500.0)
        # 500/10000 = 5% -> critical low
        alerts = monitor.check_alerts(source, reading)
        assert len(alerts) >= 1
        critical_alerts = [a for a in alerts if a.severity == AlertSeverity.CRITICAL]
        assert len(critical_alerts) >= 1
        assert "حرج" in critical_alerts[0].title_ar or "منخفض" in critical_alerts[0].title_ar

    def test_warning_low_level_alert(self):
        monitor, source = self._create_monitor_and_source()
        reading = monitor.record_reading(source, level_m3=2000.0)
        # 2000/10000 = 20% -> warning low
        alerts = monitor.check_alerts(source, reading)
        assert len(alerts) >= 1
        high_alerts = [a for a in alerts if a.severity == AlertSeverity.HIGH]
        assert len(high_alerts) >= 1

    def test_normal_level_no_alert(self):
        monitor, source = self._create_monitor_and_source()
        reading = monitor.record_reading(source, level_m3=5000.0)
        # 50% -> normal
        alerts = monitor.check_alerts(source, reading)
        assert len(alerts) == 0

    def test_critical_high_level_alert(self):
        monitor, source = self._create_monitor_and_source()
        reading = monitor.record_reading(source, level_m3=9800.0)
        # 98% -> critical high (overflow risk)
        alerts = monitor.check_alerts(source, reading)
        assert len(alerts) >= 1
        assert any(a.alert_type == "critical_high_level" for a in alerts)

    def test_critical_drawdown_alert(self):
        monitor, source = self._create_monitor_and_source()
        reading = monitor.record_reading(
            source,
            static_level_m=50.0,
            dynamic_level_m=62.0,
        )
        # drawdown = 12m -> critical (>10m)
        alerts = monitor.check_alerts(source, reading)
        critical = [a for a in alerts if a.alert_type == "critical_drawdown"]
        assert len(critical) >= 1

    def test_drawdown_warning_alert(self):
        monitor, source = self._create_monitor_and_source()
        reading = monitor.record_reading(
            source,
            static_level_m=50.0,
            dynamic_level_m=56.0,
        )
        # drawdown = 6m -> warning (>5m, <10m)
        alerts = monitor.check_alerts(source, reading)
        warnings = [a for a in alerts if a.alert_type == "drawdown_warning"]
        assert len(warnings) >= 1

    def test_reading_cache_limit(self):
        monitor, source = self._create_monitor_and_source()
        for _ in range(1100):
            monitor.record_reading(source, level_m3=5000.0)
        # Should trim to 1000
        assert len(monitor._readings_cache[source.id]) <= 1000


# ═══════════════════════════════════════════════════════════════════════════════
# WaterLevelReading Tests - اختبارات قراءة مستوى المياه
# ═══════════════════════════════════════════════════════════════════════════════


class TestWaterLevelReading:
    """Test WaterLevelReading model."""

    def test_reading_creation(self):
        reading = WaterLevelReading(
            id="rd-001",
            source_id="src-001",
            tenant_id="tenant-001",
            timestamp=datetime.now(UTC),
            level_m3=5000.0,
            level_percent=50.0,
        )
        assert reading.level_m3 == 5000.0
        assert reading.is_valid is True
        assert reading.reading_quality == 1.0

    def test_reading_to_dict(self):
        reading = WaterLevelReading(
            id="rd-001",
            source_id="src-001",
            tenant_id="tenant-001",
            timestamp=datetime.now(UTC),
            level_m3=5000.0,
            level_percent=50.0,
            sensor_id="sensor-001",
            battery_percent=85.0,
        )
        d = reading.to_dict()
        assert d["level"]["volume_m3"] == 5000.0
        assert d["sensor"]["battery_percent"] == 85.0


# ═══════════════════════════════════════════════════════════════════════════════
# WaterLevelTrend Tests - اختبارات اتجاه المستوى
# ═══════════════════════════════════════════════════════════════════════════════


class TestWaterLevelTrend:
    """Test WaterLevelTrend model."""

    def test_trend_creation(self):
        trend = WaterLevelTrend(
            source_id="src-001",
            period_start=datetime.now(UTC) - timedelta(days=7),
            period_end=datetime.now(UTC),
            reading_count=100,
            valid_readings=95,
            avg_level_m3=5000.0,
            trend="decreasing",
            trend_ar="منخفض",
        )
        assert trend.trend == "decreasing"
        assert trend.trend_ar == "منخفض"
        assert trend.valid_readings == 95

    def test_trend_to_dict(self):
        trend = WaterLevelTrend(
            source_id="src-001",
            period_start=datetime.now(UTC) - timedelta(days=7),
            period_end=datetime.now(UTC),
            change_rate_m3_day=-50.0,
            days_until_empty=100.0,
        )
        d = trend.to_dict()
        assert d["trend"]["change_rate_m3_day"] == -50.0
        assert d["projections"]["days_until_empty"] == 100.0
