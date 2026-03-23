"""
Tests for change_detector module.
Tests cover ChangeDetector, ChangeEvent, ChangeReport, NDVIDataPoint,
classify_change, anomaly detection, severity, recommendations, and helper methods.
"""

import sys
import os
from datetime import date

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.change_detector import (
    ChangeDetector,
    ChangeEvent,
    ChangeReport,
    ChangeType,
    NDVIDataPoint,
    SeverityLevel,
    TrendDirection,
)


# =============================================================================
# Enum Tests
# =============================================================================


class TestEnums:
    def test_change_types(self):
        assert ChangeType.VEGETATION_INCREASE.value == "vegetation_increase"
        assert ChangeType.HARVEST.value == "harvest"
        assert ChangeType.NO_CHANGE.value == "no_change"
        assert len(ChangeType) == 11

    def test_severity_levels(self):
        assert SeverityLevel.LOW.value == "low"
        assert SeverityLevel.CRITICAL.value == "critical"
        assert len(SeverityLevel) == 4

    def test_trend_directions(self):
        assert TrendDirection.IMPROVING.value == "improving"
        assert TrendDirection.STABLE.value == "stable"
        assert TrendDirection.DECLINING.value == "declining"


# =============================================================================
# Data Model Tests
# =============================================================================


class TestChangeEvent:
    def test_creation(self):
        event = ChangeEvent(
            field_id="F001",
            change_type=ChangeType.VEGETATION_INCREASE,
            severity=SeverityLevel.LOW,
            detected_date=date(2025, 3, 15),
            location={"lat": 15.5, "lon": 44.2, "affected_area_ha": 1.0},
            ndvi_before=0.5,
            ndvi_after=0.7,
            ndvi_change=0.2,
            change_percent=40.0,
            confidence=0.85,
            description_ar="زيادة",
            description_en="Increase",
            recommended_action_ar="استمر",
            recommended_action_en="Continue",
        )
        assert event.field_id == "F001"
        assert event.change_type == ChangeType.VEGETATION_INCREASE

    def test_clamping(self):
        event = ChangeEvent(
            field_id="F001",
            change_type=ChangeType.NO_CHANGE,
            severity=SeverityLevel.LOW,
            detected_date=date(2025, 1, 1),
            location={"lat": 0, "lon": 0},
            ndvi_before=1.5,  # Should clamp to 1.0
            ndvi_after=-1.5,  # Should clamp to -1.0
            ndvi_change=3.0,  # Should clamp to 2.0
            change_percent=0.0,
            confidence=1.5,  # Should clamp to 1.0
            description_ar="",
            description_en="",
            recommended_action_ar="",
            recommended_action_en="",
        )
        assert event.ndvi_before == 1.0
        assert event.ndvi_after == -1.0
        assert event.ndvi_change == 2.0
        assert event.confidence == 1.0

    def test_to_dict(self):
        event = ChangeEvent(
            field_id="F001",
            change_type=ChangeType.HARVEST,
            severity=SeverityLevel.MEDIUM,
            detected_date=date(2025, 5, 1),
            location={"lat": 15.5, "lon": 44.2},
            ndvi_before=0.7,
            ndvi_after=0.2,
            ndvi_change=-0.5,
            change_percent=-71.4,
            confidence=0.9,
            description_ar="حصاد",
            description_en="Harvest",
            recommended_action_ar="خطط",
            recommended_action_en="Plan",
        )
        d = event.to_dict()
        assert d["change_type"] == "harvest"
        assert d["severity"] == "medium"
        assert d["detected_date"] == "2025-05-01"


class TestChangeReport:
    def test_to_dict(self):
        report = ChangeReport(
            field_id="F001",
            analysis_period={"start_date": "2025-01-01", "end_date": "2025-03-01"},
            events=[],
            overall_trend=TrendDirection.STABLE,
            ndvi_trend=0.0,
            anomaly_count=0,
            severity_summary={},
            change_type_summary={},
            summary_ar="مستقر",
            summary_en="Stable",
            recommendations_ar=["مراقبة"],
            recommendations_en=["Monitor"],
        )
        d = report.to_dict()
        assert d["field_id"] == "F001"
        assert d["overall_trend"] == "stable"
        assert d["anomaly_count"] == 0


class TestNDVIDataPoint:
    def test_creation(self):
        point = NDVIDataPoint(date=date(2025, 1, 1), ndvi=0.65)
        assert point.ndvi == 0.65
        assert point.ndwi is None
        assert point.cloud_cover == 0.0

    def test_with_optional_fields(self):
        point = NDVIDataPoint(
            date=date(2025, 1, 1),
            ndvi=0.65,
            ndwi=0.3,
            ndmi=0.2,
            cloud_cover=10.0,
        )
        assert point.ndwi == 0.3
        assert point.ndmi == 0.2


# =============================================================================
# ChangeDetector Tests
# =============================================================================


class TestChangeDetector:
    @pytest.fixture
    def detector(self):
        return ChangeDetector()

    # =========================================================================
    # classify_change Tests
    # =========================================================================

    def test_no_change(self, detector):
        result = detector.classify_change(0.5, 0.52, 10, "summer")
        assert result == ChangeType.NO_CHANGE

    def test_harvest_detection(self, detector):
        result = detector.classify_change(0.7, 0.15, 14, "spring")
        assert result == ChangeType.HARVEST

    def test_planting_detection(self, detector):
        result = detector.classify_change(0.15, 0.4, 30, "fall")
        assert result == ChangeType.PLANTING

    def test_land_clearing(self, detector):
        # Rapid drop to near zero, rate > 0.015 per day
        # Must not match harvest (ndvi_before>0.5, after<0.3, change<-0.3, days<=30)
        # So use ndvi_before < 0.5 to avoid harvest match
        result = detector.classify_change(0.45, 0.1, 10, "winter")
        assert result == ChangeType.LAND_CLEARING

    def test_crop_damage(self, detector):
        # Moderate rapid drop within 14 days from healthy state
        result = detector.classify_change(0.6, 0.3, 10, "summer")
        assert result == ChangeType.CROP_DAMAGE

    def test_pest_disease(self, detector):
        # Gradual decrease from healthy state over > 14 days
        result = detector.classify_change(0.7, 0.5, 30, "summer")
        assert result == ChangeType.PEST_DISEASE

    def test_vegetation_increase(self, detector):
        result = detector.classify_change(0.3, 0.5, 30, "spring")
        assert result == ChangeType.VEGETATION_INCREASE

    def test_vegetation_decrease(self, detector):
        result = detector.classify_change(0.5, 0.35, 30, "summer")
        assert result == ChangeType.VEGETATION_DECREASE

    def test_flooding_with_ndwi(self, detector):
        result = detector.classify_change(0.5, 0.2, 10, "summer", ndwi_before=0.1, ndwi_after=0.4)
        assert result == ChangeType.FLOODING

    def test_water_stress_with_ndwi(self, detector):
        result = detector.classify_change(0.5, 0.3, 10, "summer", ndwi_before=0.3, ndwi_after=0.1)
        assert result == ChangeType.WATER_STRESS

    def test_drought_stress_with_ndwi(self, detector):
        result = detector.classify_change(0.6, 0.25, 10, "summer", ndwi_before=0.3, ndwi_after=0.0)
        assert result == ChangeType.DROUGHT_STRESS

    # =========================================================================
    # _determine_severity Tests
    # =========================================================================

    def test_severity_critical(self, detector):
        assert detector._determine_severity(35.0, 5) == SeverityLevel.CRITICAL

    def test_severity_high(self, detector):
        assert detector._determine_severity(25.0, 20) == SeverityLevel.HIGH

    def test_severity_medium(self, detector):
        assert detector._determine_severity(15.0, 30) == SeverityLevel.MEDIUM

    def test_severity_low(self, detector):
        assert detector._determine_severity(5.0, 30) == SeverityLevel.LOW

    def test_severity_rapid_daily_change(self, detector):
        # daily_change = 15/3 = 5 > 2.0 => CRITICAL
        assert detector._determine_severity(15.0, 3) == SeverityLevel.CRITICAL

    # =========================================================================
    # _calculate_confidence Tests
    # =========================================================================

    def test_confidence_large_change(self, detector):
        conf = detector._calculate_confidence(50.0, 14)
        assert 0.8 <= conf <= 0.95

    def test_confidence_small_change(self, detector):
        conf = detector._calculate_confidence(5.0, 14)
        assert conf < 0.8

    def test_confidence_very_short_span(self, detector):
        conf = detector._calculate_confidence(20.0, 2)
        assert conf > 0.5

    def test_confidence_long_span(self, detector):
        conf = detector._calculate_confidence(20.0, 60)
        assert conf > 0.5

    # =========================================================================
    # _get_season Tests
    # =========================================================================

    def test_season_winter(self, detector):
        assert detector._get_season(date(2025, 12, 15)) == "winter"
        assert detector._get_season(date(2025, 1, 15)) == "winter"
        assert detector._get_season(date(2025, 2, 15)) == "winter"

    def test_season_spring(self, detector):
        assert detector._get_season(date(2025, 3, 15)) == "spring"
        assert detector._get_season(date(2025, 5, 15)) == "spring"

    def test_season_summer(self, detector):
        assert detector._get_season(date(2025, 6, 15)) == "summer"
        assert detector._get_season(date(2025, 8, 15)) == "summer"

    def test_season_fall(self, detector):
        assert detector._get_season(date(2025, 9, 15)) == "fall"
        assert detector._get_season(date(2025, 11, 15)) == "fall"

    # =========================================================================
    # _calculate_trend Tests
    # =========================================================================

    def test_trend_increasing(self, detector):
        values = [0.3, 0.4, 0.5, 0.6, 0.7]
        trend = detector._calculate_trend(values)
        assert trend > 0

    def test_trend_decreasing(self, detector):
        values = [0.7, 0.6, 0.5, 0.4, 0.3]
        trend = detector._calculate_trend(values)
        assert trend < 0

    def test_trend_stable(self, detector):
        values = [0.5, 0.5, 0.5, 0.5]
        trend = detector._calculate_trend(values)
        assert trend == 0.0

    def test_trend_single_value(self, detector):
        assert detector._calculate_trend([0.5]) == 0.0

    def test_trend_empty(self, detector):
        assert detector._calculate_trend([]) == 0.0

    # =========================================================================
    # _determine_overall_trend Tests
    # =========================================================================

    def test_overall_improving(self, detector):
        result = detector._determine_overall_trend(0.01, [{"deviation": 0.1}])
        assert result == TrendDirection.IMPROVING

    def test_overall_declining(self, detector):
        result = detector._determine_overall_trend(-0.01, [{"deviation": -0.1}, {"deviation": -0.2}])
        assert result == TrendDirection.DECLINING

    def test_overall_stable(self, detector):
        result = detector._determine_overall_trend(0.0, [])
        assert result == TrendDirection.STABLE

    # =========================================================================
    # generate_recommendation Tests
    # =========================================================================

    def test_recommendation_vegetation_increase(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.VEGETATION_INCREASE, SeverityLevel.LOW, None)
        assert "irrigation" in en.lower() or "growing" in en.lower()

    def test_recommendation_water_stress_low(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.WATER_STRESS, SeverityLevel.LOW, None)
        assert "water stress" in en.lower() or "monitor" in en.lower()

    def test_recommendation_water_stress_critical(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.WATER_STRESS, SeverityLevel.CRITICAL, None)
        assert "urgent" in en.lower() or "risk" in en.lower()

    def test_recommendation_harvest(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.HARVEST, SeverityLevel.MEDIUM, None)
        assert "harvest" in en.lower() or "plan" in en.lower()

    def test_recommendation_no_change(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.NO_CHANGE, SeverityLevel.LOW, None)
        assert "stable" in en.lower() or "continue" in en.lower()

    def test_recommendation_flooding(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.FLOODING, SeverityLevel.HIGH, None)
        assert "drainage" in en.lower() or "water" in en.lower()

    def test_recommendation_land_clearing(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.LAND_CLEARING, SeverityLevel.HIGH, None)
        assert "clearing" in en.lower() or "field" in en.lower()

    def test_recommendation_crop_damage(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.CROP_DAMAGE, SeverityLevel.HIGH, None)
        assert "inspect" in en.lower() or "damage" in en.lower()

    def test_recommendation_pest_disease(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.PEST_DISEASE, SeverityLevel.MEDIUM, None)
        assert "pest" in en.lower() or "disease" in en.lower()

    def test_recommendation_drought_stress(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.DROUGHT_STRESS, SeverityLevel.HIGH, None)
        assert "drought" in en.lower() or "irrigation" in en.lower()

    def test_recommendation_planting(self, detector):
        ar, en = detector.generate_recommendation(ChangeType.PLANTING, SeverityLevel.LOW, None)
        assert "planting" in en.lower() or "moisture" in en.lower()

    # =========================================================================
    # _generate_change_description Tests
    # =========================================================================

    def test_description_vegetation_increase(self, detector):
        ar, en = detector._generate_change_description(
            ChangeType.VEGETATION_INCREASE, 0.2, 40.0, date(2025, 1, 1), date(2025, 1, 15)
        )
        assert "40.0%" in en
        assert "14 days" in en

    def test_description_harvest(self, detector):
        ar, en = detector._generate_change_description(
            ChangeType.HARVEST, -0.5, -71.4, date(2025, 4, 1), date(2025, 4, 15)
        )
        assert "Harvest" in en

    def test_description_no_change(self, detector):
        ar, en = detector._generate_change_description(
            ChangeType.NO_CHANGE, 0.01, 2.0, date(2025, 1, 1), date(2025, 1, 15)
        )
        assert "No significant" in en

    # =========================================================================
    # _count_by_severity / _count_by_change_type Tests
    # =========================================================================

    def test_count_by_severity(self, detector):
        events = [
            self._make_event(SeverityLevel.LOW, ChangeType.NO_CHANGE),
            self._make_event(SeverityLevel.CRITICAL, ChangeType.CROP_DAMAGE),
            self._make_event(SeverityLevel.CRITICAL, ChangeType.WATER_STRESS),
        ]
        counts = detector._count_by_severity(events)
        assert counts["low"] == 1
        assert counts["critical"] == 2
        assert counts["medium"] == 0

    def test_count_by_change_type(self, detector):
        events = [
            self._make_event(SeverityLevel.LOW, ChangeType.HARVEST),
            self._make_event(SeverityLevel.LOW, ChangeType.HARVEST),
            self._make_event(SeverityLevel.LOW, ChangeType.PLANTING),
        ]
        counts = detector._count_by_change_type(events)
        assert counts["harvest"] == 2
        assert counts["planting"] == 1

    # =========================================================================
    # _generate_summary Tests
    # =========================================================================

    def test_summary_no_events(self, detector):
        ar, en = detector._generate_summary([], 0.0, TrendDirection.STABLE, date(2025, 1, 1), date(2025, 3, 1))
        assert "No significant" in en

    def test_summary_with_critical(self, detector):
        events = [self._make_event(SeverityLevel.CRITICAL, ChangeType.CROP_DAMAGE)]
        ar, en = detector._generate_summary(events, -0.01, TrendDirection.DECLINING, date(2025, 1, 1), date(2025, 3, 1))
        assert "critical" in en.lower()

    def test_summary_with_high(self, detector):
        events = [self._make_event(SeverityLevel.HIGH, ChangeType.WATER_STRESS)]
        ar, en = detector._generate_summary(
            events, -0.005, TrendDirection.DECLINING, date(2025, 1, 1), date(2025, 3, 1)
        )
        assert "high" in en.lower()

    # =========================================================================
    # _generate_recommendations Tests
    # =========================================================================

    def test_recommendations_no_events(self, detector):
        ar, en = detector._generate_recommendations([], TrendDirection.STABLE, None)
        assert "monitoring" in en[0].lower()

    def test_recommendations_declining_trend(self, detector):
        events = [self._make_event(SeverityLevel.MEDIUM, ChangeType.VEGETATION_DECREASE)]
        ar, en = detector._generate_recommendations(events, TrendDirection.DECLINING, None)
        assert any("decline" in r.lower() or "monitoring" in r.lower() for r in en)

    # =========================================================================
    # _create_empty_report Tests
    # =========================================================================

    def test_empty_report(self, detector):
        report = detector._create_empty_report("F001", date(2025, 1, 1), date(2025, 3, 1))
        assert report.field_id == "F001"
        assert report.overall_trend == TrendDirection.STABLE
        assert report.events == []
        assert "Insufficient" in report.summary_en

    # =========================================================================
    # _calculate_expected_pattern Tests
    # =========================================================================

    def test_expected_pattern_wheat(self, detector):
        data = [
            NDVIDataPoint(date=date(2025, 1, 15), ndvi=0.5),
            NDVIDataPoint(date=date(2025, 2, 15), ndvi=0.6),
            NDVIDataPoint(date=date(2025, 3, 15), ndvi=0.7),
        ]
        pattern = detector._calculate_expected_pattern(data, "wheat")
        assert pattern is not None
        assert len(pattern) == 3

    def test_expected_pattern_coffee_perennial(self, detector):
        data = [
            NDVIDataPoint(date=date(2025, 1, 15), ndvi=0.7),
            NDVIDataPoint(date=date(2025, 7, 15), ndvi=0.75),
        ]
        pattern = detector._calculate_expected_pattern(data, "coffee")
        assert pattern is not None
        assert len(pattern) == 2

    def test_expected_pattern_unknown_crop(self, detector):
        data = [NDVIDataPoint(date=date(2025, 1, 15), ndvi=0.5)]
        pattern = detector._calculate_expected_pattern(data, "unknown_crop")
        assert pattern is None

    # =========================================================================
    # detect_anomalies Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_detect_anomalies_no_data(self, detector):
        result = await detector.detect_anomalies([])
        assert result == []

    @pytest.mark.asyncio
    async def test_detect_anomalies_insufficient(self, detector):
        data = [NDVIDataPoint(date=date(2025, 1, 1), ndvi=0.5)]
        result = await detector.detect_anomalies(data)
        assert result == []

    @pytest.mark.asyncio
    async def test_detect_anomalies_with_outlier(self, detector):
        data = [
            NDVIDataPoint(date=date(2025, 1, 1), ndvi=0.5),
            NDVIDataPoint(date=date(2025, 1, 10), ndvi=0.5),
            NDVIDataPoint(date=date(2025, 1, 20), ndvi=0.5),
            NDVIDataPoint(date=date(2025, 1, 30), ndvi=0.5),
            NDVIDataPoint(date=date(2025, 2, 10), ndvi=0.1),  # Outlier
        ]
        result = await detector.detect_anomalies(data)
        assert len(result) >= 1

    @pytest.mark.asyncio
    async def test_detect_anomalies_with_expected_pattern(self, detector):
        data = [
            NDVIDataPoint(date=date(2025, 1, 1), ndvi=0.5),
            NDVIDataPoint(date=date(2025, 1, 10), ndvi=0.55),
            NDVIDataPoint(date=date(2025, 1, 20), ndvi=0.55),
            NDVIDataPoint(date=date(2025, 1, 30), ndvi=0.6),
            NDVIDataPoint(date=date(2025, 2, 10), ndvi=-0.1),  # Large anomaly
        ]
        expected = [0.5, 0.55, 0.55, 0.6, 0.65]
        result = await detector.detect_anomalies(data, expected)
        assert len(result) >= 1

    # =========================================================================
    # compare_dates Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_compare_dates_increase(self, detector):
        event = await detector.compare_dates(
            "F001",
            15.5,
            44.2,
            date(2025, 1, 1),
            date(2025, 1, 20),
            0.3,
            0.55,
        )
        assert event.change_type == ChangeType.VEGETATION_INCREASE
        assert event.ndvi_change > 0

    @pytest.mark.asyncio
    async def test_compare_dates_decrease(self, detector):
        event = await detector.compare_dates(
            "F001",
            15.5,
            44.2,
            date(2025, 1, 1),
            date(2025, 1, 20),
            0.6,
            0.35,
        )
        assert event.ndvi_change < 0

    @pytest.mark.asyncio
    async def test_compare_dates_with_ndwi(self, detector):
        event = await detector.compare_dates(
            "F001",
            15.5,
            44.2,
            date(2025, 1, 1),
            date(2025, 1, 20),
            0.6,
            0.3,
            ndwi1=0.3,
            ndwi2=0.1,
        )
        assert event.additional_metrics is not None
        assert "ndwi_change" in event.additional_metrics

    @pytest.mark.asyncio
    async def test_compare_dates_zero_before(self, detector):
        event = await detector.compare_dates(
            "F001",
            15.5,
            44.2,
            date(2025, 1, 1),
            date(2025, 1, 20),
            0.0,
            0.3,
        )
        assert event.change_percent == 0  # Avoid division by zero

    # =========================================================================
    # detect_changes Tests
    # =========================================================================

    @pytest.mark.asyncio
    async def test_detect_changes_no_data(self, detector):
        report = await detector.detect_changes("F001", 15.5, 44.2, date(2025, 1, 1), date(2025, 3, 1))
        assert report.field_id == "F001"
        assert report.overall_trend == TrendDirection.STABLE
        assert "Insufficient" in report.summary_en

    @pytest.mark.asyncio
    async def test_detect_changes_with_data(self, detector):
        timeseries = [
            NDVIDataPoint(date=date(2025, 1, 1), ndvi=0.5),
            NDVIDataPoint(date=date(2025, 1, 15), ndvi=0.55),
            NDVIDataPoint(date=date(2025, 2, 1), ndvi=0.6),
            NDVIDataPoint(date=date(2025, 2, 15), ndvi=0.65),
            NDVIDataPoint(date=date(2025, 3, 1), ndvi=0.5),
        ]
        report = await detector.detect_changes(
            "F001",
            15.5,
            44.2,
            date(2025, 1, 1),
            date(2025, 3, 1),
            ndvi_timeseries=timeseries,
        )
        assert report.field_id == "F001"
        assert isinstance(report.overall_trend, TrendDirection)

    @pytest.mark.asyncio
    async def test_detect_changes_with_crop_type(self, detector):
        timeseries = [
            NDVIDataPoint(date=date(2025, 1, 1), ndvi=0.4),
            NDVIDataPoint(date=date(2025, 1, 15), ndvi=0.5),
            NDVIDataPoint(date=date(2025, 2, 1), ndvi=0.6),
            NDVIDataPoint(date=date(2025, 2, 15), ndvi=0.7),
        ]
        report = await detector.detect_changes(
            "F001",
            15.5,
            44.2,
            date(2025, 1, 1),
            date(2025, 3, 1),
            crop_type="wheat",
            ndvi_timeseries=timeseries,
        )
        assert report is not None

    @pytest.mark.asyncio
    async def test_detect_changes_cloudy_data_filtered(self, detector):
        timeseries = [
            NDVIDataPoint(date=date(2025, 1, 1), ndvi=0.5, cloud_cover=5),
            NDVIDataPoint(date=date(2025, 1, 10), ndvi=0.1, cloud_cover=90),  # Filtered
            NDVIDataPoint(date=date(2025, 1, 20), ndvi=0.55, cloud_cover=10),
        ]
        report = await detector.detect_changes(
            "F001",
            15.5,
            44.2,
            date(2025, 1, 1),
            date(2025, 2, 1),
            ndvi_timeseries=timeseries,
        )
        # With only 2 clean points, should return empty report
        assert report is not None

    # =========================================================================
    # Helper
    # =========================================================================

    @staticmethod
    def _make_event(severity: SeverityLevel, change_type: ChangeType) -> ChangeEvent:
        return ChangeEvent(
            field_id="F001",
            change_type=change_type,
            severity=severity,
            detected_date=date(2025, 1, 15),
            location={"lat": 15.5, "lon": 44.2},
            ndvi_before=0.6,
            ndvi_after=0.3,
            ndvi_change=-0.3,
            change_percent=-50.0,
            confidence=0.8,
            description_ar="وصف",
            description_en="Description",
            recommended_action_ar="إجراء",
            recommended_action_en="Action required",
        )
