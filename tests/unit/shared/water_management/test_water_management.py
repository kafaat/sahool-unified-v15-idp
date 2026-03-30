"""
Unit tests for shared/water_management module.
اختبارات وحدة إدارة المياه.
"""

import pytest
from datetime import date, datetime, UTC

from shared.water_management.models import (
    WaterSourceType,
    WaterSourceStatus,
    WaterQualityClass,
    WaterRightType,
    AllocationPeriod,
    IrrigationMethod,
    AlertSeverity,
    ComplianceStatus,
    MeterType,
    GeoLocation,
    WaterMeter,
    WaterSource,
    WaterRight,
    WaterAllocation,
    WaterQualityTest,
    WaterConsumptionRecord,
    IrrigationEvent,
    WaterAlert,
    SaudiWaterStandards,
)
from shared.water_management.efficiency import (
    EfficiencyBenchmarks,
    IrrigationEfficiencyMetrics,
    FieldWaterBalance,
    IrrigationEfficiencyCalculator,
)


_NOW = datetime(2026, 1, 15, 12, 0, 0, tzinfo=UTC)


# ============================================================================
# Enum Tests
# ============================================================================


@pytest.mark.unit
class TestWaterSourceTypeEnum:
    def test_all_values(self):
        assert WaterSourceType.WELL == "well"
        assert WaterSourceType.ARTESIAN_WELL == "artesian_well"
        assert WaterSourceType.TANK == "tank"
        assert WaterSourceType.RESERVOIR == "reservoir"
        assert WaterSourceType.CANAL == "canal"
        assert WaterSourceType.DESALINATED == "desalinated"
        assert WaterSourceType.RAINWATER == "rainwater"
        assert WaterSourceType.SPRING == "spring"

    def test_count(self):
        assert len(WaterSourceType) == 11


@pytest.mark.unit
class TestWaterSourceStatusEnum:
    def test_all_values(self):
        assert WaterSourceStatus.ACTIVE == "active"
        assert WaterSourceStatus.INACTIVE == "inactive"
        assert WaterSourceStatus.MAINTENANCE == "maintenance"
        assert WaterSourceStatus.DEPLETED == "depleted"
        assert WaterSourceStatus.CONTAMINATED == "contaminated"
        assert WaterSourceStatus.PERMIT_EXPIRED == "permit_expired"
        assert WaterSourceStatus.SUSPENDED == "suspended"

    def test_count(self):
        assert len(WaterSourceStatus) == 8


@pytest.mark.unit
class TestWaterQualityClassEnum:
    def test_all_values(self):
        assert WaterQualityClass.CLASS_A == "A"
        assert WaterQualityClass.CLASS_B == "B"
        assert WaterQualityClass.CLASS_C == "C"
        assert WaterQualityClass.CLASS_D == "D"
        assert WaterQualityClass.UNFIT == "unfit"

    def test_count(self):
        assert len(WaterQualityClass) == 5


@pytest.mark.unit
class TestWaterRightTypeEnum:
    def test_all_values(self):
        assert WaterRightType.TRADITIONAL == "traditional"
        assert WaterRightType.LICENSED == "licensed"
        assert WaterRightType.PERMIT == "permit"
        assert WaterRightType.EMERGENCY == "emergency"
        assert WaterRightType.TEMPORARY == "temporary"
        assert WaterRightType.TRANSFERRED == "transferred"

    def test_count(self):
        assert len(WaterRightType) == 6


@pytest.mark.unit
class TestAllocationPeriodEnum:
    def test_all_values(self):
        assert AllocationPeriod.DAILY == "daily"
        assert AllocationPeriod.WEEKLY == "weekly"
        assert AllocationPeriod.MONTHLY == "monthly"
        assert AllocationPeriod.SEASONAL == "seasonal"
        assert AllocationPeriod.ANNUAL == "annual"


@pytest.mark.unit
class TestIrrigationMethodEnum:
    def test_all_values(self):
        assert IrrigationMethod.DRIP == "drip"
        assert IrrigationMethod.SPRINKLER == "sprinkler"
        assert IrrigationMethod.CENTER_PIVOT == "center_pivot"
        assert IrrigationMethod.FLOOD == "flood"


@pytest.mark.unit
class TestAlertSeverityEnum:
    def test_has_members(self):
        members = [m.value for m in AlertSeverity]
        assert len(members) >= 3


@pytest.mark.unit
class TestComplianceStatusEnum:
    def test_has_members(self):
        members = [m.value for m in ComplianceStatus]
        assert len(members) >= 2


@pytest.mark.unit
class TestMeterTypeEnum:
    def test_has_members(self):
        members = [m.value for m in MeterType]
        assert len(members) >= 2


# ============================================================================
# Model Tests
# ============================================================================


@pytest.mark.unit
class TestGeoLocation:
    def test_creation(self):
        loc = GeoLocation(lat=24.7, lng=46.7)
        assert loc.lat == 24.7
        assert loc.lng == 46.7

    def test_with_elevation(self):
        loc = GeoLocation(lat=24.7, lng=46.7, elevation_m=600.0)
        assert loc.elevation_m == 600.0

    def test_defaults(self):
        loc = GeoLocation(lat=24.7, lng=46.7)
        assert loc.elevation_m is None
        assert loc.accuracy_m is None


@pytest.mark.unit
class TestWaterMeter:
    def test_creation(self):
        meter = WaterMeter(
            id="WM-001",
            tenant_id="T1",
            source_id="WS-001",
            name="Main Meter",
            name_ar="العداد الرئيسي",
            meter_type=MeterType(list(MeterType)[0].value),
            model="FlowMax 3000",
            serial_number="SN-12345",
            manufacturer="WaterTech",
        )
        assert meter.id == "WM-001"
        assert meter.name_ar == "العداد الرئيسي"

    def test_defaults(self):
        meter = WaterMeter(
            id="WM-002",
            tenant_id="T1",
            source_id="WS-001",
            name="Meter A",
            name_ar="عداد أ",
            meter_type=MeterType(list(MeterType)[0].value),
            model="M100",
            serial_number="SN-999",
            manufacturer="Acme",
        )
        assert meter.current_reading_m3 == 0.0
        assert meter.calibration_factor == 1.0
        assert meter.is_active is True


@pytest.mark.unit
class TestWaterSource:
    def test_creation(self):
        ws = WaterSource(
            id="WS-001",
            tenant_id="T1",
            name="Main Well",
            name_ar="البئر الرئيسي",
            farm_id="FARM-001",
            source_type=WaterSourceType.WELL,
            status=WaterSourceStatus.ACTIVE,
        )
        assert ws.name == "Main Well"
        assert ws.name_ar == "البئر الرئيسي"
        assert ws.source_type == WaterSourceType.WELL

    def test_bilingual(self):
        ws = WaterSource(
            id="WS-002",
            tenant_id="T1",
            name="Artesian Well #3",
            name_ar="بئر ارتوازي رقم 3",
            farm_id="FARM-001",
            source_type=WaterSourceType.ARTESIAN_WELL,
            status=WaterSourceStatus.ACTIVE,
        )
        assert ws.name_ar == "بئر ارتوازي رقم 3"

    def test_to_dict(self):
        ws = WaterSource(
            id="WS-003",
            tenant_id="T1",
            name="Tank",
            name_ar="خزان",
            farm_id="FARM-001",
            source_type=WaterSourceType.TANK,
            status=WaterSourceStatus.ACTIVE,
        )
        d = ws.to_dict()
        assert isinstance(d, dict)
        assert d["source_type"] == "tank"


@pytest.mark.unit
class TestWaterAllocation:
    def test_creation(self):
        wa = WaterAllocation(
            id="WA-001",
            tenant_id="T1",
            farm_id="FARM-001",
            field_id="F1",
            water_right_id="WR-001",
        )
        assert wa.id == "WA-001"
        assert wa.farm_id == "FARM-001"

    def test_defaults(self):
        wa = WaterAllocation(
            id="WA-002",
            tenant_id="T1",
            farm_id="FARM-001",
            field_id="F1",
            water_right_id="WR-001",
        )
        assert wa.field_id == "F1"


@pytest.mark.unit
class TestIrrigationEvent:
    def test_creation(self):
        ie = IrrigationEvent(
            id="IE-001",
            tenant_id="T1",
            farm_id="FARM-001",
            field_id="FIELD-001",
            source_id="WS-001",
        )
        assert ie.field_id == "FIELD-001"
        assert ie.farm_id == "FARM-001"

    def test_to_dict(self):
        ie = IrrigationEvent(
            id="IE-002",
            tenant_id="T1",
            farm_id="FARM-001",
            field_id="F1",
            source_id="WS-001",
        )
        d = ie.to_dict()
        assert isinstance(d, dict)
        assert d["field_id"] == "F1"


@pytest.mark.unit
class TestWaterQualityTest:
    def test_creation(self):
        qt = WaterQualityTest(
            id="QT-001",
            tenant_id="T1",
            source_id="WS-001",
            tested_at=_NOW,
        )
        assert qt.source_id == "WS-001"

    def test_to_dict(self):
        qt = WaterQualityTest(
            id="QT-002",
            tenant_id="T1",
            source_id="WS-001",
            tested_at=_NOW,
        )
        d = qt.to_dict()
        assert isinstance(d, dict)


@pytest.mark.unit
class TestSaudiWaterStandards:
    def test_has_ec_thresholds(self):
        s = SaudiWaterStandards()
        assert hasattr(s, "EC_CLASS_A_MAX") or hasattr(s, "ec_thresholds") or hasattr(s, "EC_THRESHOLDS")

    def test_has_ph_range(self):
        s = SaudiWaterStandards()
        assert hasattr(s, "PH_MIN") or hasattr(s, "ph_range") or hasattr(s, "PH_RANGE")


# ============================================================================
# Efficiency Tests
# ============================================================================


@pytest.mark.unit
class TestEfficiencyBenchmarks:
    def test_drip_benchmarks(self):
        b = EfficiencyBenchmarks()
        assert b.APP_EFF_DRIP_MIN == 85.0
        assert b.APP_EFF_DRIP_GOOD == 90.0
        assert b.APP_EFF_DRIP_EXCELLENT == 95.0

    def test_flood_benchmarks(self):
        b = EfficiencyBenchmarks()
        assert b.APP_EFF_FLOOD_MIN == 40.0
        assert b.APP_EFF_FLOOD_GOOD == 55.0

    def test_drip_better_than_flood(self):
        b = EfficiencyBenchmarks()
        assert b.APP_EFF_DRIP_MIN > b.APP_EFF_FLOOD_EXCELLENT

    def test_conveyance_lined_better(self):
        b = EfficiencyBenchmarks()
        assert b.CONV_LINED_CANAL > b.CONV_UNLINED_CANAL

    def test_distribution_uniformity(self):
        b = EfficiencyBenchmarks()
        assert b.DU_DRIP_MIN == 85.0
        assert b.DU_SPRINKLER_MIN == 75.0
        assert b.DU_PIVOT_MIN == 80.0


@pytest.mark.unit
class TestIrrigationEfficiencyMetrics:
    def test_creation(self):
        m = IrrigationEfficiencyMetrics(
            id="EM-001",
            tenant_id="T1",
            farm_id="FARM-001",
            field_id="F1",
            calculation_date=_NOW,
        )
        assert m.id == "EM-001"
        assert m.field_id == "F1"

    def test_defaults(self):
        m = IrrigationEfficiencyMetrics(
            id="EM-002",
            tenant_id="T1",
            farm_id="FARM-001",
            field_id="F1",
            calculation_date=_NOW,
        )
        assert m.period_start is None
        assert m.period_end is None


@pytest.mark.unit
class TestFieldWaterBalance:
    def test_creation(self):
        wb = FieldWaterBalance(
            field_id="F1",
            tenant_id="T1",
            period_start=date(2026, 1, 1),
            period_end=date(2026, 1, 31),
        )
        assert wb.field_id == "F1"
        assert wb.period_start == date(2026, 1, 1)


@pytest.mark.unit
class TestIrrigationEfficiencyCalculator:
    def test_creation(self):
        calc = IrrigationEfficiencyCalculator(tenant_id="T1")
        assert calc is not None

    def test_has_methods(self):
        calc = IrrigationEfficiencyCalculator(tenant_id="T1")
        assert hasattr(calc, "calculate_application_efficiency")
