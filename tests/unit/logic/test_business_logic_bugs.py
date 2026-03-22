"""
Business Logic Bug-Hunting Tests for SAHOOL Platform
=====================================================
These tests target edge cases in agricultural calculations,
boundary conditions in weather alerts, and precision issues
in financial computations.

Run with:
    ENVIRONMENT=test JWT_SECRET_KEY=test-secret-key-for-unit-tests-only-32chars \
    PYTHONPATH=. pytest tests/unit/logic/test_business_logic_bugs.py -v --timeout=30
"""

from __future__ import annotations

import os
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest

os.environ.setdefault("ENVIRONMENT", "test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-unit-tests-only-32chars")
os.environ.setdefault("DATABASE_URL", "")
os.environ.setdefault("NATS_URL", "")


# =============================================================================
# 1. Fertilizer Calculator Edge Cases
# =============================================================================


class TestFertilizerCalculatorEdgeCases:
    """BUG TARGET: Division by zero, negative inputs, and zero-area fields."""

    def test_zero_area_field(self):
        """Bug: Zero area_ha causes division by zero or nonsensical results."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_rate_for_nutrient(
            fertilizer_code="urea",
            target_nutrient="N",
            target_kg_per_ha=46.0,
            area_ha=0.0,
        )
        # rate_kg_total = rate_kg_ha * 0.0 = 0, which is correct
        assert result.rate_kg_total == 0.0
        assert result.area_ha == 0.0

    def test_zero_target_nutrient(self):
        """Bug: Target of 0 kg/ha should return 0 rate, not error."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_rate_for_nutrient(
            fertilizer_code="urea",
            target_nutrient="N",
            target_kg_per_ha=0.0,
            area_ha=5.0,
        )
        assert result.rate_kg_per_ha == 0.0
        assert result.rate_kg_total == 0.0

    def test_unknown_fertilizer_raises_error(self):
        """Bug: Unknown fertilizer code silently returns None instead of error."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        with pytest.raises(ValueError, match="Unknown fertilizer"):
            calc.calculate_rate_for_nutrient(
                fertilizer_code="magic_powder",
                target_nutrient="N",
                target_kg_per_ha=46.0,
                area_ha=5.0,
            )

    def test_nutrient_not_in_fertilizer(self):
        """Bug: Requesting a nutrient not present in fertilizer (e.g., K from Urea)."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        with pytest.raises(ValueError, match="does not contain"):
            calc.calculate_rate_for_nutrient(
                fertilizer_code="urea",
                target_nutrient="K2O",  # Urea has 0% K2O
                target_kg_per_ha=30.0,
                area_ha=5.0,
            )

    def test_very_large_area(self):
        """Bug: Very large area causes integer overflow or float precision loss."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_rate_for_nutrient(
            fertilizer_code="urea",
            target_nutrient="N",
            target_kg_per_ha=46.0,
            area_ha=100000.0,  # 100,000 hectares
        )
        # rate_kg_ha = (46/46)*100 = 100 kg/ha
        # total = 100 * 100000 = 10,000,000 kg
        assert result.rate_kg_total == 10000000.0

    def test_dunum_conversion(self):
        """Bug: Dunum conversion (1 dunum = 0.1 ha) is incorrectly calculated."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_rate_for_nutrient(
            fertilizer_code="urea",
            target_nutrient="N",
            target_kg_per_ha=46.0,
            area_ha=1.0,
        )
        # rate_per_dunum should be rate_per_ha / 10
        expected_per_dunum = round(result.rate_kg_per_ha / 10, 2)
        assert result.rate_kg_per_dunum == expected_per_dunum

    def test_blend_with_zero_targets(self):
        """Bug: Blend calculation with all zero targets might crash."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_blend(
            target_n_kg_ha=0.0,
            target_p_kg_ha=0.0,
            target_k_kg_ha=0.0,
        )
        assert result.total_n_kg_ha == 0.0
        assert result.total_p_kg_ha == 0.0
        assert result.total_k_kg_ha == 0.0
        assert len(result.components) == 0

    def test_blend_with_only_nitrogen(self):
        """Bug: Blend with only N target but no P or K might have issues."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_blend(
            target_n_kg_ha=50.0,
            target_p_kg_ha=0.0,
            target_k_kg_ha=0.0,
        )
        # Should use urea for N
        assert result.total_n_kg_ha > 0
        assert len(result.components) >= 1

    def test_blend_variance_calculation_with_zero_target(self):
        """Bug: Division by zero in variance calculation when target is zero."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_blend(
            target_n_kg_ha=50.0,
            target_p_kg_ha=0.0,  # Zero target
            target_k_kg_ha=0.0,  # Zero target
        )
        # Variance should be 0 when target is 0, not ZeroDivisionError
        assert result.p_variance_percent == 0.0
        assert result.k_variance_percent == 0.0

    def test_blend_negative_remaining_n_from_dap(self):
        """Bug: DAP provides N alongside P, which can make remaining_n negative.
        If remaining_n goes negative, the blend should not subtract from urea."""
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        # Request low N but high P - DAP (18-46-0) will provide excess N
        result = calc.calculate_blend(
            target_n_kg_ha=5.0,  # Very low N target
            target_p_kg_ha=46.0,  # Needs 100 kg/ha DAP -> gives 18 kg N
            target_k_kg_ha=0.0,
        )
        # DAP gives 18 kg N, but target was only 5 kg N.
        # remaining_n becomes 5 - 18 = -13 (negative)
        # If urea check is `remaining_n > 0`, no urea will be applied.
        # But total N delivered (18) exceeds target (5).
        assert result.total_n_kg_ha >= 5.0  # At least target met

    def test_cost_analysis_zero_area(self):
        """BUG FIXED: CostAnalysis dataclass default_factory now uses lambda correctly.

        Previously, `analysis_date: datetime = field(default_factory=datetime.now(UTC).replace(tzinfo=None))`
        evaluated at class definition time. Now fixed with lambda wrapper.

        Tests that zero area cost analysis works correctly with no applications.
        """
        from shared.fertilizer_management.calculator import FertilizerCalculator

        calc = FertilizerCalculator()
        result = calc.calculate_cost_analysis(
            field_id="FIELD-001",
            season="winter-2025",
            area_ha=0.0,
            applications=[],
        )
        assert result.field_id == "FIELD-001"
        assert result.season == "winter-2025"
        assert result.area_ha == 0.0
        assert result.total_cost == Decimal("0.00")
        assert result.cost_per_ha == Decimal("0.00")

    def test_dataclass_default_factory_bug(self):
        """BUG FIXED: FertilizerApplication can now be created without explicit application_date.

        The default_factory now correctly uses lambda wrapper. Verify that
        FertilizerApplication creates successfully with a valid default date.
        """
        from shared.fertilizer_management.models import FertilizerApplication

        app = FertilizerApplication(
            id="FA-001",
            tenant_id="T-001",
            field_id="FIELD-001",
            fertilizer_id="urea",
            # Omit application_date to use the default_factory
        )
        assert app.id == "FA-001"
        assert app.field_id == "FIELD-001"
        assert isinstance(app.application_date, datetime)
        assert isinstance(app.created_at, datetime)
        assert isinstance(app.updated_at, datetime)


# =============================================================================
# 2. NDVI Health Classification at Boundaries
# =============================================================================


class TestNDVIHealthClassification:
    """BUG TARGET: Health classification at exact boundary values."""

    def _make_ndvi(self, mean_value: float):
        """Helper to create NDVIResult."""
        from shared.satellite.sentinel_ndvi import NDVIResult, VegetationIndex

        return NDVIResult(
            field_id="FIELD-001",
            timestamp=datetime.now(UTC),
            index_type=VegetationIndex.NDVI,
            mean_value=mean_value,
            min_value=min(mean_value, 0.0),
            max_value=max(mean_value, 0.0),
            std_value=0.05,
            cloud_coverage=5.0,
            pixel_count=100,
        )

    def test_ndvi_exactly_0_6_is_healthy(self):
        """Bug: Boundary at 0.6 - should be 'healthy' per >= 0.6 rule."""
        result = self._make_ndvi(0.6)
        assert result.health_status == "healthy"

    def test_ndvi_just_below_0_6_is_moderate(self):
        """Bug: 0.5999 should be 'moderate', not 'healthy'."""
        result = self._make_ndvi(0.5999)
        assert result.health_status == "moderate"

    def test_ndvi_exactly_0_4_is_moderate(self):
        """Bug: Boundary at 0.4 - should be 'moderate' per >= 0.4 rule."""
        result = self._make_ndvi(0.4)
        assert result.health_status == "moderate"

    def test_ndvi_just_below_0_4_is_stressed(self):
        """Bug: 0.3999 should be 'stressed', not 'moderate'."""
        result = self._make_ndvi(0.3999)
        assert result.health_status == "stressed"

    def test_ndvi_exactly_0_2_is_stressed(self):
        """Bug: Boundary at 0.2 - should be 'stressed' per >= 0.2 rule."""
        result = self._make_ndvi(0.2)
        assert result.health_status == "stressed"

    def test_ndvi_just_below_0_2_is_critical(self):
        """Bug: 0.1999 should be 'critical', not 'stressed'."""
        result = self._make_ndvi(0.1999)
        assert result.health_status == "critical"

    def test_ndvi_zero_is_critical(self):
        """NDVI = 0.0 (bare soil) should be 'critical'."""
        result = self._make_ndvi(0.0)
        assert result.health_status == "critical"

    def test_ndvi_negative_is_critical(self):
        """NDVI < 0 (water) should be 'critical'."""
        result = self._make_ndvi(-0.5)
        assert result.health_status == "critical"


# =============================================================================
# 3. Weather Alert Threshold Boundaries
# =============================================================================


class TestWeatherAlertBoundaries:
    """BUG TARGET: Off-by-one errors at alert threshold boundaries."""

    def test_frost_exactly_at_critical_threshold(self):
        """Bug: temp exactly at critical threshold (-2.0C for GENERAL) should trigger critical."""
        from shared.weather_alerts.alerts import WeatherAlertGenerator
        from shared.weather_alerts.models import AlertSeverity, CropType, WeatherForecast

        generator = WeatherAlertGenerator()
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=-2.0,  # Exactly at GENERAL critical threshold
            temperature_max=10.0,
        )
        alerts = generator.generate_alerts([forecast], crop_type=CropType.GENERAL)
        frost_alerts = [a for a in alerts if a.alert_type.value == "frost"]
        assert len(frost_alerts) >= 1
        assert frost_alerts[0].severity == AlertSeverity.CRITICAL

    def test_frost_just_above_critical_is_warning(self):
        """Bug: temp at -1.9C (above -2.0 critical) should be warning, not critical."""
        from shared.weather_alerts.alerts import WeatherAlertGenerator
        from shared.weather_alerts.models import AlertSeverity, CropType, WeatherForecast

        generator = WeatherAlertGenerator()
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=-1.9,  # Above critical (-2.0), at or below warning (0.0)
            temperature_max=10.0,
        )
        alerts = generator.generate_alerts([forecast], crop_type=CropType.GENERAL)
        frost_alerts = [a for a in alerts if a.alert_type.value == "frost"]
        assert len(frost_alerts) >= 1
        assert frost_alerts[0].severity == AlertSeverity.WARNING

    def test_heat_exactly_at_critical_threshold(self):
        """Bug: temp exactly at critical (45C for GENERAL) should be critical."""
        from shared.weather_alerts.alerts import WeatherAlertGenerator
        from shared.weather_alerts.models import AlertSeverity, CropType, WeatherForecast

        generator = WeatherAlertGenerator()
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=30.0,
            temperature_max=45.0,  # Exactly at GENERAL critical threshold
        )
        alerts = generator.generate_alerts([forecast], crop_type=CropType.GENERAL)
        heat_alerts = [a for a in alerts if a.alert_type.value == "heat"]
        assert len(heat_alerts) >= 1
        assert heat_alerts[0].severity == AlertSeverity.CRITICAL

    def test_heat_just_below_advisory_no_alert(self):
        """Bug: temp just below advisory threshold should produce NO heat alert."""
        from shared.weather_alerts.alerts import WeatherAlertGenerator
        from shared.weather_alerts.models import CropType, WeatherForecast

        generator = WeatherAlertGenerator()
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=20.0,
            temperature_max=34.9,  # Below GENERAL advisory (35.0)
        )
        alerts = generator.generate_alerts([forecast], crop_type=CropType.GENERAL)
        heat_alerts = [a for a in alerts if a.alert_type.value == "heat"]
        assert len(heat_alerts) == 0

    def test_frost_above_advisory_no_alert(self):
        """Bug: temp above advisory threshold should produce NO frost alert."""
        from shared.weather_alerts.alerts import WeatherAlertGenerator
        from shared.weather_alerts.models import CropType, WeatherForecast

        generator = WeatherAlertGenerator()
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=3.1,  # Above GENERAL advisory (3.0)
            temperature_max=15.0,
        )
        alerts = generator.generate_alerts([forecast], crop_type=CropType.GENERAL)
        frost_alerts = [a for a in alerts if a.alert_type.value == "frost"]
        assert len(frost_alerts) == 0

    def test_extreme_cold_triggers_critical(self):
        """Bug: Extreme cold (-40C) should trigger critical frost alert."""
        from shared.weather_alerts.alerts import WeatherAlertGenerator
        from shared.weather_alerts.models import AlertSeverity, CropType, WeatherForecast

        generator = WeatherAlertGenerator()
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=-40.0,
            temperature_max=-20.0,
        )
        alerts = generator.generate_alerts([forecast], crop_type=CropType.GENERAL)
        frost_alerts = [a for a in alerts if a.alert_type.value == "frost"]
        assert len(frost_alerts) >= 1
        assert frost_alerts[0].severity == AlertSeverity.CRITICAL

    def test_extreme_heat_50c_triggers_critical(self):
        """Bug: 50C should trigger critical heat for most crops (except date palm)."""
        from shared.weather_alerts.alerts import WeatherAlertGenerator
        from shared.weather_alerts.models import AlertSeverity, CropType, WeatherForecast

        generator = WeatherAlertGenerator()
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=35.0,
            temperature_max=50.0,
        )
        alerts = generator.generate_alerts([forecast], crop_type=CropType.WHEAT)
        heat_alerts = [a for a in alerts if a.alert_type.value == "heat"]
        assert len(heat_alerts) >= 1
        assert heat_alerts[0].severity == AlertSeverity.CRITICAL

    def test_crop_specific_thresholds_differ(self):
        """Bug: Crop-specific thresholds not being applied - all crops using GENERAL."""
        from shared.weather_alerts.models import CROP_FROST_THRESHOLDS, CropType

        # Wheat is more cold-tolerant than tomato
        wheat_critical = CROP_FROST_THRESHOLDS[CropType.WHEAT]["critical"]  # -5.0
        tomato_critical = CROP_FROST_THRESHOLDS[CropType.TOMATO]["critical"]  # 0.0
        assert wheat_critical < tomato_critical, "Wheat should tolerate colder temps than tomato"

    def test_empty_forecast_list_returns_no_alerts(self):
        """Bug: Empty forecast list causes crash instead of empty result."""
        from shared.weather_alerts.alerts import WeatherAlertGenerator

        generator = WeatherAlertGenerator()
        alerts = generator.generate_alerts([])
        assert alerts == []


# =============================================================================
# 4. NDVI Time Series Trend Calculation
# =============================================================================


class TestNDVITimeSeries:
    """BUG TARGET: Trend calculation edge cases."""

    def test_trend_with_single_measurement(self):
        """Bug: Single measurement should report insufficient_data, not crash."""
        from shared.satellite.sentinel_ndvi import NDVIResult, TimeSeriesNDVI, VegetationIndex

        ts = TimeSeriesNDVI(
            field_id="FIELD-001",
            start_date=datetime.now(UTC),
            end_date=datetime.now(UTC),
            measurements=[
                NDVIResult(
                    field_id="FIELD-001",
                    timestamp=datetime.now(UTC),
                    index_type=VegetationIndex.NDVI,
                    mean_value=0.5,
                    min_value=0.3,
                    max_value=0.7,
                    std_value=0.1,
                    cloud_coverage=5.0,
                    pixel_count=100,
                )
            ],
        )
        ts.calculate_trend()
        assert ts.trend == "insufficient_data"

    def test_trend_with_two_measurements_improving(self):
        """Bug: Two measurements should detect improving trend."""
        from shared.satellite.sentinel_ndvi import NDVIResult, TimeSeriesNDVI, VegetationIndex

        ts = TimeSeriesNDVI(
            field_id="FIELD-001",
            start_date=datetime.now(UTC) - timedelta(days=30),
            end_date=datetime.now(UTC),
            measurements=[
                NDVIResult(
                    field_id="FIELD-001",
                    timestamp=datetime.now(UTC) - timedelta(days=30),
                    index_type=VegetationIndex.NDVI,
                    mean_value=0.3,
                    min_value=0.2,
                    max_value=0.4,
                    std_value=0.05,
                    cloud_coverage=5.0,
                    pixel_count=100,
                ),
                NDVIResult(
                    field_id="FIELD-001",
                    timestamp=datetime.now(UTC),
                    index_type=VegetationIndex.NDVI,
                    mean_value=0.7,
                    min_value=0.5,
                    max_value=0.9,
                    std_value=0.05,
                    cloud_coverage=5.0,
                    pixel_count=100,
                ),
            ],
        )
        ts.calculate_trend()
        assert ts.trend == "improving"

    def test_trend_with_stable_measurements(self):
        """Bug: Nearly identical measurements should be 'stable'."""
        from shared.satellite.sentinel_ndvi import NDVIResult, TimeSeriesNDVI, VegetationIndex

        measurements = []
        for i in range(4):
            measurements.append(
                NDVIResult(
                    field_id="FIELD-001",
                    timestamp=datetime.now(UTC) - timedelta(days=30 - i * 10),
                    index_type=VegetationIndex.NDVI,
                    mean_value=0.65 + (i * 0.01),  # Very slight change
                    min_value=0.5,
                    max_value=0.8,
                    std_value=0.05,
                    cloud_coverage=5.0,
                    pixel_count=100,
                )
            )

        ts = TimeSeriesNDVI(
            field_id="FIELD-001",
            start_date=datetime.now(UTC) - timedelta(days=30),
            end_date=datetime.now(UTC),
            measurements=measurements,
        )
        ts.calculate_trend()
        assert ts.trend == "stable"


# =============================================================================
# 5. Environmental Compliance Boundary Checks
# =============================================================================


class TestEnvironmentalCompliance:
    """BUG TARGET: Compliance thresholds at exact boundaries."""

    def test_nitrogen_exactly_at_limit(self):
        """BUG FIXED: EnvironmentalCompliance default_factory now uses lambda correctly.

        Tests that N exactly at 200 kg/ha limit is compliant (not a violation).
        """
        from shared.fertilizer_management.calculator import FertilizerCalculator
        from shared.fertilizer_management.models import ComplianceLevel, FertilizerApplication

        calc = FertilizerCalculator()
        apps = [
            FertilizerApplication(
                id="FA-001",
                tenant_id="T-001",
                field_id="FIELD-001",
                fertilizer_id="urea",
                nitrogen_applied_kg_ha=200.0,
            )
        ]
        result = calc.check_environmental_compliance("FIELD-001", apps)
        # Exactly at limit should NOT be a violation (only > limit is violation)
        assert result.n_compliance != ComplianceLevel.VIOLATION
        assert result.overall_status != ComplianceLevel.VIOLATION

    def test_nitrogen_above_limit_is_violation(self):
        """BUG FIXED: Tests that N above 200 kg/ha limit is flagged as violation."""
        from shared.fertilizer_management.calculator import FertilizerCalculator
        from shared.fertilizer_management.models import ComplianceLevel, FertilizerApplication

        calc = FertilizerCalculator()
        apps = [
            FertilizerApplication(
                id="FA-001",
                tenant_id="T-001",
                field_id="FIELD-001",
                fertilizer_id="urea",
                nitrogen_applied_kg_ha=250.0,
            )
        ]
        result = calc.check_environmental_compliance("FIELD-001", apps)
        assert result.n_compliance == ComplianceLevel.VIOLATION
        assert result.overall_status == ComplianceLevel.VIOLATION
        assert len(result.violations_en) >= 1

    def test_nitrogen_at_80_percent_is_warning(self):
        """BUG FIXED: Tests that N above 80% of limit (160 kg/ha) triggers warning."""
        from shared.fertilizer_management.calculator import FertilizerCalculator
        from shared.fertilizer_management.models import ComplianceLevel, FertilizerApplication

        calc = FertilizerCalculator()
        apps = [
            FertilizerApplication(
                id="FA-001",
                tenant_id="T-001",
                field_id="FIELD-001",
                fertilizer_id="urea",
                nitrogen_applied_kg_ha=170.0,  # Above 80% (160) but below 200
            )
        ]
        result = calc.check_environmental_compliance("FIELD-001", apps)
        assert result.n_compliance == ComplianceLevel.WARNING
        assert result.overall_status == ComplianceLevel.WARNING

    def test_water_body_too_close_is_violation(self):
        """BUG FIXED: Tests that water body proximity below buffer zone triggers violation."""
        from shared.fertilizer_management.calculator import FertilizerCalculator
        from shared.fertilizer_management.models import ComplianceLevel

        calc = FertilizerCalculator()
        result = calc.check_environmental_compliance(
            "FIELD-001",
            applications=[],
            water_body_distance_m=5.0,  # Below 10m buffer zone
        )
        assert result.buffer_compliance == ComplianceLevel.VIOLATION
        assert result.overall_status == ComplianceLevel.VIOLATION
        assert len(result.violations_en) >= 1


# =============================================================================
# 6. Nutrient Balance Edge Cases
# =============================================================================


class TestNutrientBalance:
    """BUG TARGET: Edge cases in nutrient balance calculations."""

    def test_balance_with_zero_target_yield(self):
        """BUG FIXED: SoilTest and NutrientBalance default_factory now use lambda correctly.

        Tests that zero target yield produces a valid nutrient balance with
        zero crop requirements.
        """
        from shared.fertilizer_management.calculator import FertilizerCalculator
        from shared.fertilizer_management.models import SoilTest

        calc = FertilizerCalculator()
        soil_test = SoilTest(
            id="ST-001",
            tenant_id="T-001",
            field_id="FIELD-001",
            sample_date=datetime.now(UTC),
            nitrogen_ppm=20.0,
            phosphorus_ppm=15.0,
            potassium_ppm=150.0,
            ph=7.0,
        )
        result = calc.calculate_nutrient_balance(
            field_id="FIELD-001",
            season="winter-2025",
            crop="wheat",
            crop_ar="قمح",
            soil_test=soil_test,
            target_yield_tons_ha=0.0,
            applications=[],
        )
        assert result.crop_n_requirement_kg_ha == 0.0
        assert result.crop_p_requirement_kg_ha == 0.0
        assert result.crop_k_requirement_kg_ha == 0.0
        # With zero requirements, soil nutrients create surplus
        assert result.n_balance_kg_ha >= 0.0

    def test_balance_with_unknown_crop_uses_defaults(self):
        """BUG FIXED: Unknown crop type uses default nutrient factors without crashing."""
        from shared.fertilizer_management.calculator import FertilizerCalculator
        from shared.fertilizer_management.models import SoilTest

        calc = FertilizerCalculator()
        soil_test = SoilTest(
            id="ST-001",
            tenant_id="T-001",
            field_id="FIELD-001",
            sample_date=datetime.now(UTC),
            nitrogen_ppm=20.0,
            phosphorus_ppm=15.0,
            potassium_ppm=150.0,
            ph=7.0,
        )
        result = calc.calculate_nutrient_balance(
            field_id="FIELD-001",
            season="winter-2025",
            crop="saffron",
            crop_ar="زعفران",
            soil_test=soil_test,
            target_yield_tons_ha=2.0,
            applications=[],
        )
        # Unknown crop "saffron" should use default factors: N=20, P=10, K=15
        assert result.crop_n_requirement_kg_ha == 20 * 2.0  # 40.0
        assert result.crop_p_requirement_kg_ha == 10 * 2.0  # 20.0
        assert result.crop_k_requirement_kg_ha == 15 * 2.0  # 30.0

    def test_nutrient_status_determination(self):
        """BUG FIXED: SoilTest can now be created without explicit created_at.

        Verifies that SoilTest default_factory works correctly and produces
        a valid datetime for created_at.
        """
        from shared.fertilizer_management.models import SoilTest

        soil_test = SoilTest(
            id="ST-001",
            tenant_id="T-001",
            field_id="FIELD-001",
            sample_date=datetime.now(UTC),
            nitrogen_ppm=20.0,
            phosphorus_ppm=15.0,
            potassium_ppm=150.0,
            ph=7.0,
            # Omit created_at to use the fixed default_factory
        )
        assert soil_test.id == "ST-001"
        assert isinstance(soil_test.created_at, datetime)
        assert soil_test.nitrogen_ppm == 20.0
