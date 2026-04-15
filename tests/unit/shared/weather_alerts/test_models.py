"""
Unit tests for shared/weather_alerts/models.py
Tests weather alert data models including enums, WeatherForecast,
WeatherAlert, SprayWindow, IrrigationSchedule, HarvestWindow,
AlertThresholds, and crop-specific threshold data.
"""

import pytest
from datetime import date, time, datetime, UTC

from shared.weather_alerts.models import (
    # Enums
    AlertSeverity,
    AlertType,
    SprayCondition,
    IrrigationRecommendation,
    HarvestCondition,
    CropType,
    # Dataclasses
    WeatherForecast,
    WeatherAlert,
    SprayWindow,
    IrrigationSchedule,
    HarvestWindow,
    AlertThresholds,
    # Data
    CROP_FROST_THRESHOLDS,
    CROP_HEAT_THRESHOLDS,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    def test_alert_severity(self):
        assert AlertSeverity.CRITICAL == "critical"
        assert AlertSeverity.WARNING == "warning"
        assert AlertSeverity.ADVISORY == "advisory"
        assert AlertSeverity.WATCH == "watch"
        assert AlertSeverity.INFORMATION == "information"

    def test_alert_type(self):
        assert AlertType.FROST == "frost"
        assert AlertType.HEAT == "heat"
        assert AlertType.SANDSTORM == "sandstorm"
        assert AlertType.HAIL == "hail"

    def test_spray_condition(self):
        assert SprayCondition.OPTIMAL == "optimal"
        assert SprayCondition.DANGEROUS == "dangerous"

    def test_irrigation_recommendation(self):
        assert IrrigationRecommendation.IRRIGATE_NOW == "irrigate_now"
        assert IrrigationRecommendation.SKIP_IRRIGATION == "skip_irrigation"
        assert IrrigationRecommendation.MONITOR == "monitor"

    def test_harvest_condition(self):
        assert HarvestCondition.OPTIMAL == "optimal"
        assert HarvestCondition.RISKY == "risky"
        assert HarvestCondition.UNSUITABLE == "unsuitable"

    def test_crop_type(self):
        assert CropType.WHEAT == "wheat"
        assert CropType.DATE_PALM == "date_palm"
        assert CropType.GENERAL == "general"


# =============================================================================
# WeatherForecast Tests
# =============================================================================


class TestWeatherForecast:
    def test_creation_minimal(self):
        wf = WeatherForecast(forecast_date=date(2026, 3, 22))
        assert wf.forecast_date == date(2026, 3, 22)
        assert wf.temperature == 0.0
        assert wf.confidence == 0.8
        assert wf.source == "weather_service"

    def test_creation_full(self):
        wf = WeatherForecast(
            forecast_date=date(2026, 3, 22),
            hour=14,
            temperature=32.0,
            temperature_min=22.0,
            temperature_max=35.0,
            humidity=45.0,
            wind_speed=15.0,
            wind_direction="NW",
            precipitation_probability=10.0,
            precipitation_amount=0.0,
            uv_index=8,
            is_inversion_likely=True,
        )
        assert wf.hour == 14
        assert wf.temperature == 32.0
        assert wf.uv_index == 8
        assert wf.is_inversion_likely is True

    def test_to_dict(self):
        wf = WeatherForecast(
            forecast_date=date(2026, 3, 22),
            forecast_time=time(14, 0),
            temperature=28.0,
        )
        d = wf.to_dict()
        assert d["forecast_date"] == "2026-03-22"
        assert d["forecast_time"] == "14:00:00"
        assert d["temperature"] == 28.0

    def test_to_dict_no_time(self):
        wf = WeatherForecast(forecast_date=date(2026, 3, 22))
        d = wf.to_dict()
        assert d["forecast_time"] is None


# =============================================================================
# WeatherAlert Tests
# =============================================================================


class TestWeatherAlert:
    def test_creation_defaults(self):
        alert = WeatherAlert()
        assert alert.id  # UUID
        assert alert.alert_type == AlertType.FROST
        assert alert.severity == AlertSeverity.WARNING
        assert alert.is_active is True
        assert alert.currency == "SAR"
        assert alert.confidence == 0.8

    def test_creation_with_values(self):
        alert = WeatherAlert(
            alert_type=AlertType.HEAT,
            severity=AlertSeverity.CRITICAL,
            title="Extreme Heat Wave",
            title_ar="موجة حر شديدة",
            trigger_value=48.0,
            threshold_value=45.0,
            trigger_unit="°C",
            affected_crops=["wheat", "barley"],
        )
        assert alert.alert_type == AlertType.HEAT
        assert alert.severity == AlertSeverity.CRITICAL
        assert alert.trigger_value == 48.0
        assert len(alert.affected_crops) == 2

    def test_get_priority_icon(self):
        assert WeatherAlert(severity=AlertSeverity.CRITICAL).get_priority_icon() == "[!!!]"
        assert WeatherAlert(severity=AlertSeverity.WARNING).get_priority_icon() == "[!!]"
        assert WeatherAlert(severity=AlertSeverity.ADVISORY).get_priority_icon() == "[!]"
        assert WeatherAlert(severity=AlertSeverity.WATCH).get_priority_icon() == "[.]"
        assert WeatherAlert(severity=AlertSeverity.INFORMATION).get_priority_icon() == "[i]"

    def test_to_dict(self):
        now = datetime.now(UTC)
        alert = WeatherAlert(
            alert_type=AlertType.FROST,
            severity=AlertSeverity.WARNING,
            field_id="field-001",
            valid_from=now,
            valid_until=now,
            title="Frost Alert",
            title_ar="تنبيه صقيع",
        )
        d = alert.to_dict()
        assert d["alert_type"] == "frost"
        assert d["severity"] == "warning"
        assert d["field_id"] == "field-001"
        assert d["title"] == "Frost Alert"
        assert d["valid_from"] is not None

    def test_to_dict_none_dates(self):
        alert = WeatherAlert()
        d = alert.to_dict()
        assert d["valid_from"] is None
        assert d["valid_until"] is None
        assert d["acknowledged_at"] is None
        assert d["resolved_at"] is None


# =============================================================================
# SprayWindow Tests
# =============================================================================


class TestSprayWindow:
    def test_creation_defaults(self):
        sw = SprayWindow()
        assert sw.id  # UUID
        assert sw.overall_condition == SprayCondition.UNSUITABLE
        assert sw.score == 0.0
        assert sw.drift_risk == "low"
        assert sw.suitable_for_systemic is True
        assert sw.suitable_for_volatile is False

    def test_creation_with_values(self):
        sw = SprayWindow(
            overall_condition=SprayCondition.OPTIMAL,
            score=95.0,
            temperature_score=90.0,
            humidity_score=85.0,
            wind_score=95.0,
        )
        assert sw.overall_condition == SprayCondition.OPTIMAL
        assert sw.score == 95.0

    def test_to_dict(self):
        now = datetime.now(UTC)
        sw = SprayWindow(
            start_time=now,
            end_time=now,
            duration_hours=4.0,
            overall_condition=SprayCondition.ACCEPTABLE,
        )
        d = sw.to_dict()
        assert d["overall_condition"] == "acceptable"
        assert d["duration_hours"] == 4.0
        assert d["start_time"] is not None

    def test_to_dict_no_times(self):
        sw = SprayWindow()
        d = sw.to_dict()
        assert d["start_time"] is None
        assert d["end_time"] is None


# =============================================================================
# IrrigationSchedule Tests
# =============================================================================


class TestIrrigationSchedule:
    def test_creation_defaults(self):
        sched = IrrigationSchedule()
        assert sched.id  # UUID
        assert sched.crop_type == CropType.GENERAL
        assert sched.recommendation == IrrigationRecommendation.MONITOR
        assert sched.adjustment_factor == 1.0
        assert sched.confidence == 0.8

    def test_creation_with_values(self):
        sched = IrrigationSchedule(
            field_id="field-001",
            crop_type=CropType.WHEAT,
            recommendation=IrrigationRecommendation.IRRIGATE_NOW,
            recommended_amount_mm=25.0,
            expected_rain_mm=5.0,
            expected_et_mm=6.0,
        )
        assert sched.recommendation == IrrigationRecommendation.IRRIGATE_NOW
        assert sched.recommended_amount_mm == 25.0

    def test_to_dict(self):
        sched = IrrigationSchedule(
            field_id="field-001",
            recommended_date=date(2026, 3, 25),
            recommended_time=time(6, 0),
            recommended_amount_mm=30.0,
            reason="Low soil moisture",
            reason_ar="رطوبة تربة منخفضة",
        )
        d = sched.to_dict()
        assert d["field_id"] == "field-001"
        assert d["recommended_date"] == "2026-03-25"
        assert d["recommended_time"] == "06:00:00"
        assert d["recommended_amount_mm"] == 30.0

    def test_to_dict_no_dates(self):
        sched = IrrigationSchedule()
        d = sched.to_dict()
        assert d["recommended_date"] is None
        assert d["recommended_time"] is None
        assert d["optimal_window_start"] is None


# =============================================================================
# HarvestWindow Tests
# =============================================================================


class TestHarvestWindow:
    def test_creation_defaults(self):
        hw = HarvestWindow()
        assert hw.id  # UUID
        assert hw.crop_type == CropType.GENERAL
        assert hw.overall_condition == HarvestCondition.ACCEPTABLE
        assert hw.drying_needed is False

    def test_creation_with_values(self):
        hw = HarvestWindow(
            field_id="field-001",
            crop_type=CropType.WHEAT,
            overall_condition=HarvestCondition.OPTIMAL,
            score=90.0,
            expected_rain_probability=5.0,
            dry_hours_available=12.0,
        )
        assert hw.overall_condition == HarvestCondition.OPTIMAL
        assert hw.score == 90.0

    def test_to_dict(self):
        hw = HarvestWindow(
            optimal_date=date(2026, 5, 15),
            optimal_time=time(8, 0),
            overall_condition=HarvestCondition.GOOD,
        )
        d = hw.to_dict()
        assert d["optimal_date"] == "2026-05-15"
        assert d["optimal_time"] == "08:00:00"
        assert d["overall_condition"] == "good"

    def test_to_dict_no_dates(self):
        hw = HarvestWindow()
        d = hw.to_dict()
        assert d["window_start"] is None
        assert d["optimal_date"] is None


# =============================================================================
# AlertThresholds Tests
# =============================================================================


class TestAlertThresholds:
    def test_creation_defaults(self):
        at = AlertThresholds()
        assert at.frost_critical == -2.0
        assert at.frost_warning == 0.0
        assert at.heat_critical == 45.0
        assert at.wind_spray_max == 15.0
        assert at.rain_spray_threshold == 0.5
        assert at.spray_temp_min == 10.0
        assert at.spray_temp_max == 30.0
        assert at.uv_extreme == 11

    def test_to_dict(self):
        at = AlertThresholds()
        d = at.to_dict()
        assert d["frost_critical"] == -2.0
        assert d["heat_critical"] == 45.0
        assert d["wind_critical"] == 80.0
        assert d["harvest_rain_probability_max"] == 30.0
        assert d["uv_high"] == 6

    def test_custom_thresholds(self):
        at = AlertThresholds(
            frost_critical=-5.0,
            heat_critical=50.0,
            wind_spray_max=12.0,
        )
        assert at.frost_critical == -5.0
        assert at.heat_critical == 50.0
        assert at.wind_spray_max == 12.0


# =============================================================================
# Crop-Specific Threshold Data Tests
# =============================================================================


class TestCropThresholds:
    def test_frost_thresholds_all_crops(self):
        """All defined crop types should have frost thresholds."""
        expected_crops = [
            CropType.WHEAT, CropType.BARLEY, CropType.DATE_PALM,
            CropType.TOMATO, CropType.CUCUMBER, CropType.CITRUS,
            CropType.GRAPE, CropType.OLIVE, CropType.ALFALFA,
            CropType.GENERAL,
        ]
        for crop in expected_crops:
            assert crop in CROP_FROST_THRESHOLDS, f"Missing frost thresholds for {crop}"
            thresholds = CROP_FROST_THRESHOLDS[crop]
            assert "critical" in thresholds
            assert "warning" in thresholds
            assert "advisory" in thresholds
            # Critical should be most severe (lowest)
            assert thresholds["critical"] <= thresholds["warning"]
            assert thresholds["warning"] <= thresholds["advisory"]

    def test_heat_thresholds_all_crops(self):
        """All defined crop types should have heat thresholds."""
        expected_crops = [
            CropType.WHEAT, CropType.BARLEY, CropType.DATE_PALM,
            CropType.TOMATO, CropType.CUCUMBER, CropType.GENERAL,
        ]
        for crop in expected_crops:
            assert crop in CROP_HEAT_THRESHOLDS, f"Missing heat thresholds for {crop}"
            thresholds = CROP_HEAT_THRESHOLDS[crop]
            assert "critical" in thresholds
            assert "warning" in thresholds
            assert "advisory" in thresholds
            # Critical should be highest temperature
            assert thresholds["critical"] >= thresholds["warning"]
            assert thresholds["warning"] >= thresholds["advisory"]

    def test_date_palm_heat_tolerance(self):
        """Date palm should have highest heat tolerance."""
        palm = CROP_HEAT_THRESHOLDS[CropType.DATE_PALM]
        wheat = CROP_HEAT_THRESHOLDS[CropType.WHEAT]
        assert palm["critical"] > wheat["critical"]

    def test_cucumber_frost_sensitivity(self):
        """Cucumber should be most sensitive to frost."""
        cucumber = CROP_FROST_THRESHOLDS[CropType.CUCUMBER]
        wheat = CROP_FROST_THRESHOLDS[CropType.WHEAT]
        assert cucumber["critical"] > wheat["critical"]
