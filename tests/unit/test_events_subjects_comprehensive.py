"""
Comprehensive Event Subjects Tests for SAHOOL Platform
اختبارات شاملة لموضوعات الأحداث لمنصة سهول

Tests cover:
- Subject naming convention
- All domain subject constants
- Wildcard subjects
- Subject pattern validation
"""

from __future__ import annotations

import pytest

from shared.events.subjects import (
    SAHOOL_FARM_ALL,
    SAHOOL_FARM_CREATED,
    SAHOOL_FARM_DELETED,
    SAHOOL_FARM_UPDATED,
    SAHOOL_FIELD_ALL,
    SAHOOL_FIELD_CREATED,
    SAHOOL_FIELD_DELETED,
    SAHOOL_FIELD_UPDATED,
    SAHOOL_HEALTH_DISEASE_DETECTED,
    SAHOOL_HEALTH_PEST_DETECTED,
    SAHOOL_HEALTH_STRESS_COLD,
    SAHOOL_HEALTH_STRESS_DETECTED,
    SAHOOL_HEALTH_STRESS_HEAT,
    SAHOOL_HEALTH_STRESS_NUTRIENT,
    SAHOOL_HEALTH_STRESS_WATER,
    SAHOOL_NDVI_ANOMALY,
    SAHOOL_NDVI_COMPUTED,
    SAHOOL_SATELLITE_ALL,
    SAHOOL_SATELLITE_ANOMALIES_ALL,
    SAHOOL_SATELLITE_ANOMALY,
    SAHOOL_SATELLITE_DATA_READY,
    SAHOOL_SATELLITE_PROCESSING_COMPLETED,
    SAHOOL_SATELLITE_PROCESSING_FAILED,
    SAHOOL_SATELLITE_PROCESSING_STARTED,
    SAHOOL_WEATHER_ALERT,
    SAHOOL_WEATHER_ALERT_DROUGHT,
    SAHOOL_WEATHER_ALERT_FROST,
    SAHOOL_WEATHER_ALERT_HEATWAVE,
    SAHOOL_WEATHER_ALERT_RAIN,
    SAHOOL_WEATHER_ALERT_STORM,
    SAHOOL_WEATHER_ALERT_WIND,
    SAHOOL_WEATHER_ALERTS_ALL,
    SAHOOL_WEATHER_ALL,
    SAHOOL_WEATHER_FORECAST,
)


@pytest.mark.unit
class TestSubjectNamingConvention:
    """Tests for subject naming convention: sahool.{domain}.{action}"""

    def test_all_subjects_start_with_sahool(self):
        """Test that all subjects start with 'sahool.'"""
        subjects = [
            SAHOOL_FIELD_CREATED,
            SAHOOL_FIELD_UPDATED,
            SAHOOL_FIELD_DELETED,
            SAHOOL_FARM_CREATED,
            SAHOOL_FARM_UPDATED,
            SAHOOL_FARM_DELETED,
            SAHOOL_WEATHER_FORECAST,
            SAHOOL_WEATHER_ALERT,
            SAHOOL_SATELLITE_DATA_READY,
            SAHOOL_NDVI_COMPUTED,
            SAHOOL_HEALTH_DISEASE_DETECTED,
        ]
        for subject in subjects:
            assert subject.startswith("sahool."), f"Subject '{subject}' does not start with 'sahool.'"

    def test_subjects_use_dot_separator(self):
        """Test that subjects use dots as separators"""
        subjects = [
            SAHOOL_FIELD_CREATED,
            SAHOOL_WEATHER_ALERT_FROST,
            SAHOOL_SATELLITE_PROCESSING_STARTED,
        ]
        for subject in subjects:
            parts = subject.split(".")
            assert len(parts) >= 3, f"Subject '{subject}' should have at least 3 parts"

    def test_no_uppercase_in_subjects(self):
        """Test that subjects don't contain uppercase characters"""
        subjects = [
            SAHOOL_FIELD_CREATED,
            SAHOOL_FARM_UPDATED,
            SAHOOL_WEATHER_FORECAST,
        ]
        for subject in subjects:
            # Wildcards are lowercase
            cleaned = subject.replace("*", "")
            assert cleaned == cleaned.lower(), f"Subject '{subject}' contains uppercase"


@pytest.mark.unit
class TestFieldSubjects:
    """Tests for field-related subjects"""

    def test_field_crud_subjects(self):
        """Test field CRUD subjects"""
        assert SAHOOL_FIELD_CREATED == "sahool.field.created"
        assert SAHOOL_FIELD_UPDATED == "sahool.field.updated"
        assert SAHOOL_FIELD_DELETED == "sahool.field.deleted"

    def test_field_wildcard(self):
        """Test field wildcard subject"""
        assert SAHOOL_FIELD_ALL == "sahool.field.*"


@pytest.mark.unit
class TestFarmSubjects:
    """Tests for farm-related subjects"""

    def test_farm_crud_subjects(self):
        """Test farm CRUD subjects"""
        assert SAHOOL_FARM_CREATED == "sahool.farm.created"
        assert SAHOOL_FARM_UPDATED == "sahool.farm.updated"
        assert SAHOOL_FARM_DELETED == "sahool.farm.deleted"

    def test_farm_wildcard(self):
        """Test farm wildcard subject"""
        assert SAHOOL_FARM_ALL == "sahool.farm.*"


@pytest.mark.unit
class TestWeatherSubjects:
    """Tests for weather-related subjects"""

    def test_weather_base_subjects(self):
        """Test weather base subjects"""
        assert SAHOOL_WEATHER_FORECAST == "sahool.weather.forecast"
        assert SAHOOL_WEATHER_ALERT == "sahool.weather.alert"

    def test_weather_alert_types(self):
        """Test specific weather alert subjects"""
        assert SAHOOL_WEATHER_ALERT_FROST == "sahool.weather.alert.frost"
        assert SAHOOL_WEATHER_ALERT_HEATWAVE == "sahool.weather.alert.heatwave"
        assert SAHOOL_WEATHER_ALERT_STORM == "sahool.weather.alert.storm"
        assert SAHOOL_WEATHER_ALERT_RAIN == "sahool.weather.alert.rain"
        assert SAHOOL_WEATHER_ALERT_DROUGHT == "sahool.weather.alert.drought"
        assert SAHOOL_WEATHER_ALERT_WIND == "sahool.weather.alert.wind"

    def test_weather_wildcards(self):
        """Test weather wildcard subjects"""
        assert SAHOOL_WEATHER_ALL == "sahool.weather.*"
        assert SAHOOL_WEATHER_ALERTS_ALL == "sahool.weather.alert.*"


@pytest.mark.unit
class TestSatelliteSubjects:
    """Tests for satellite-related subjects"""

    def test_satellite_processing_subjects(self):
        """Test satellite processing lifecycle subjects"""
        assert SAHOOL_SATELLITE_DATA_READY == "sahool.satellite.data.ready"
        assert SAHOOL_SATELLITE_PROCESSING_STARTED == "sahool.satellite.processing.started"
        assert SAHOOL_SATELLITE_PROCESSING_COMPLETED == "sahool.satellite.processing.completed"
        assert SAHOOL_SATELLITE_PROCESSING_FAILED == "sahool.satellite.processing.failed"

    def test_satellite_anomaly_subjects(self):
        """Test satellite anomaly detection subjects"""
        assert SAHOOL_SATELLITE_ANOMALY == "sahool.satellite.anomaly"

    def test_ndvi_subjects(self):
        """Test NDVI-specific subjects"""
        assert SAHOOL_NDVI_COMPUTED == "sahool.satellite.ndvi.computed"
        assert SAHOOL_NDVI_ANOMALY == "sahool.satellite.ndvi.anomaly"

    def test_satellite_wildcards(self):
        """Test satellite wildcard subjects"""
        assert SAHOOL_SATELLITE_ALL == "sahool.satellite.*"
        assert SAHOOL_SATELLITE_ANOMALIES_ALL == "sahool.satellite.anomaly.*"


@pytest.mark.unit
class TestHealthSubjects:
    """Tests for crop health subjects"""

    def test_detection_subjects(self):
        """Test disease, pest, and stress detection subjects"""
        assert SAHOOL_HEALTH_DISEASE_DETECTED == "sahool.health.disease.detected"
        assert SAHOOL_HEALTH_PEST_DETECTED == "sahool.health.pest.detected"
        assert SAHOOL_HEALTH_STRESS_DETECTED == "sahool.health.stress.detected"

    def test_stress_type_subjects(self):
        """Test specific stress type subjects"""
        assert SAHOOL_HEALTH_STRESS_WATER == "sahool.health.stress.water"
        assert SAHOOL_HEALTH_STRESS_NUTRIENT == "sahool.health.stress.nutrient"
        assert SAHOOL_HEALTH_STRESS_HEAT == "sahool.health.stress.heat"
        assert SAHOOL_HEALTH_STRESS_COLD == "sahool.health.stress.cold"
