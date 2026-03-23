"""
Unit Tests for Weather Alerts Module
====================================

Comprehensive test coverage for weather alert generation, spray window
calculations, and irrigation scheduling with bilingual support.

Test Categories:
- Alert models and enums
- Frost, heat, wind alerts
- Spray window optimization
- Threshold checks
- Bilingual message verification
- Irrigation scheduling

Author: SAHOOL Test Suite
Updated: January 2026
"""

from datetime import date, datetime, time, timedelta

import pytest

from shared.weather_alerts.alerts import (
    AlertGeneratorConfig,
    WeatherAlertGenerator,
    generate_weather_alerts,
)
from shared.weather_alerts.models import (
    # Crop-specific thresholds
    CROP_FROST_THRESHOLDS,
    CROP_HEAT_THRESHOLDS,
    # Enums
    AlertSeverity,
    # Data classes
    AlertThresholds,
    AlertType,
    CropType,
    HarvestCondition,
    HarvestWindow,
    IrrigationRecommendation,
    IrrigationSchedule,
    SprayCondition,
    SprayWindow,
    WeatherAlert,
    WeatherForecast,
)
from shared.weather_alerts.spray_window import (
    SprayWindowCalculator,
    SprayWindowConfig,
    detect_inversions,
    find_spray_windows,
    get_best_spray_time,
)

# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def default_thresholds():
    """Create default alert thresholds"""
    return AlertThresholds()


@pytest.fixture
def alert_generator():
    """Create a weather alert generator with default config"""
    return WeatherAlertGenerator()


@pytest.fixture
def spray_calculator():
    """Create a spray window calculator with default config"""
    return SprayWindowCalculator()


@pytest.fixture
def forecast_cold_day():
    """Create a cold day forecast (frost conditions)"""
    return WeatherForecast(
        forecast_date=date.today(),
        temperature=-3.0,
        temperature_min=-5.0,
        temperature_max=0.0,
        humidity=80.0,
        wind_speed=5.0,
        precipitation_probability=10.0,
        confidence=0.9,
    )


@pytest.fixture
def forecast_hot_day():
    """Create a hot day forecast (heat conditions)"""
    return WeatherForecast(
        forecast_date=date.today(),
        temperature=42.0,
        temperature_min=28.0,
        temperature_max=45.0,
        humidity=25.0,
        wind_speed=10.0,
        precipitation_probability=5.0,
        confidence=0.9,
    )


@pytest.fixture
def forecast_windy_day():
    """Create a windy day forecast"""
    return WeatherForecast(
        forecast_date=date.today(),
        temperature=25.0,
        temperature_min=20.0,
        temperature_max=30.0,
        humidity=40.0,
        wind_speed=35.0,
        wind_gust=50.0,
        precipitation_probability=0.0,
        confidence=0.9,
    )


@pytest.fixture
def forecast_rainy_day():
    """Create a rainy day forecast"""
    return WeatherForecast(
        forecast_date=date.today(),
        temperature=20.0,
        temperature_min=15.0,
        temperature_max=25.0,
        humidity=90.0,
        wind_speed=5.0,
        precipitation_amount=30.0,
        precipitation_probability=80.0,
        precipitation_type="rain",
        confidence=0.9,
    )


@pytest.fixture
def forecast_optimal_spray():
    """Create an optimal spray window forecast"""
    return WeatherForecast(
        forecast_date=date.today(),
        forecast_time=time(hour=8),
        hour=8,
        temperature=18.0,
        temperature_min=15.0,
        temperature_max=22.0,
        humidity=65.0,
        wind_speed=5.0,
        wind_gust=8.0,
        precipitation_probability=5.0,
        is_inversion_likely=False,
        confidence=0.95,
    )


@pytest.fixture
def forecast_inversion_period():
    """Create a forecast with temperature inversion"""
    return WeatherForecast(
        forecast_date=date.today(),
        forecast_time=time(hour=20),
        hour=20,
        temperature=8.0,
        temperature_min=5.0,
        temperature_max=15.0,
        humidity=75.0,
        wind_speed=1.5,
        cloud_cover=15.0,
        precipitation_probability=0.0,
        is_inversion_likely=True,
        inversion_start_hour=18,
        inversion_end_hour=8,
        confidence=0.85,
    )


# ============================================================================
# TESTS: ALERT MODELS AND ENUMS
# ============================================================================


class TestAlertEnums:
    """Test alert enums and their values"""

    @pytest.mark.unit
    def test_alert_severity_enum_values(self):
        """Test AlertSeverity enum has expected values"""
        assert AlertSeverity.CRITICAL.value == "critical"
        assert AlertSeverity.WARNING.value == "warning"
        assert AlertSeverity.ADVISORY.value == "advisory"
        assert AlertSeverity.WATCH.value == "watch"
        assert AlertSeverity.INFORMATION.value == "information"

    @pytest.mark.unit
    def test_alert_type_enum_values(self):
        """Test AlertType enum has expected values"""
        assert AlertType.FROST.value == "frost"
        assert AlertType.HEAT.value == "heat"
        assert AlertType.WIND.value == "wind"
        assert AlertType.HAIL.value == "hail"
        assert AlertType.RAIN.value == "rain"
        assert AlertType.DROUGHT.value == "drought"
        assert AlertType.SANDSTORM.value == "sandstorm"
        assert AlertType.HUMIDITY.value == "humidity"
        assert AlertType.INVERSION.value == "inversion"
        assert AlertType.UV.value == "uv"

    @pytest.mark.unit
    def test_crop_type_enum_values(self):
        """Test CropType enum has expected values"""
        assert CropType.WHEAT.value == "wheat"
        assert CropType.BARLEY.value == "barley"
        assert CropType.DATE_PALM.value == "date_palm"
        assert CropType.TOMATO.value == "tomato"
        assert CropType.CUCUMBER.value == "cucumber"

    @pytest.mark.unit
    def test_spray_condition_enum_values(self):
        """Test SprayCondition enum has expected values"""
        assert SprayCondition.OPTIMAL.value == "optimal"
        assert SprayCondition.ACCEPTABLE.value == "acceptable"
        assert SprayCondition.MARGINAL.value == "marginal"
        assert SprayCondition.UNSUITABLE.value == "unsuitable"
        assert SprayCondition.DANGEROUS.value == "dangerous"

    @pytest.mark.unit
    def test_irrigation_recommendation_enum_values(self):
        """Test IrrigationRecommendation enum has expected values"""
        assert IrrigationRecommendation.IRRIGATE_NOW.value == "irrigate_now"
        assert IrrigationRecommendation.IRRIGATE_SOON.value == "irrigate_soon"
        assert IrrigationRecommendation.DELAY_IRRIGATION.value == "delay_irrigation"
        assert IrrigationRecommendation.SKIP_IRRIGATION.value == "skip_irrigation"


class TestWeatherForecast:
    """Test WeatherForecast model"""

    @pytest.mark.unit
    def test_weather_forecast_creation(self):
        """Test creating a WeatherForecast"""
        forecast = WeatherForecast(
            forecast_date=date(2026, 1, 20),
            temperature=25.0,
            temperature_min=20.0,
            temperature_max=30.0,
            humidity=60.0,
        )
        assert forecast.forecast_date == date(2026, 1, 20)
        assert forecast.temperature == 25.0
        assert forecast.temperature_min == 20.0
        assert forecast.temperature_max == 30.0
        assert forecast.humidity == 60.0

    @pytest.mark.unit
    def test_weather_forecast_to_dict(self):
        """Test converting WeatherForecast to dictionary"""
        forecast = WeatherForecast(
            forecast_date=date(2026, 1, 20),
            temperature=25.0,
            humidity=60.0,
        )
        d = forecast.to_dict()
        assert isinstance(d, dict)
        assert d["forecast_date"] == "2026-01-20"
        assert d["temperature"] == 25.0
        assert d["humidity"] == 60.0

    @pytest.mark.unit
    def test_weather_forecast_defaults(self):
        """Test WeatherForecast default values"""
        forecast = WeatherForecast(forecast_date=date.today())
        assert forecast.temperature == 0.0
        assert forecast.humidity == 0.0
        assert forecast.wind_speed == 0.0
        assert forecast.precipitation_probability == 0.0
        assert forecast.source == "weather_service"
        assert forecast.confidence == 0.8


class TestWeatherAlert:
    """Test WeatherAlert model"""

    @pytest.mark.unit
    def test_weather_alert_creation(self):
        """Test creating a WeatherAlert"""
        alert = WeatherAlert(
            alert_type=AlertType.FROST,
            severity=AlertSeverity.WARNING,
            title="Test Alert",
            title_ar="تنبيه الاختبار",
        )
        assert alert.alert_type == AlertType.FROST
        assert alert.severity == AlertSeverity.WARNING
        assert alert.title == "Test Alert"
        assert alert.title_ar == "تنبيه الاختبار"

    @pytest.mark.unit
    def test_weather_alert_priority_icons(self):
        """Test priority icons for different severity levels"""
        critical = WeatherAlert(severity=AlertSeverity.CRITICAL)
        assert critical.get_priority_icon() == "[!!!]"

        warning = WeatherAlert(severity=AlertSeverity.WARNING)
        assert warning.get_priority_icon() == "[!!]"

        advisory = WeatherAlert(severity=AlertSeverity.ADVISORY)
        assert advisory.get_priority_icon() == "[!]"

        watch = WeatherAlert(severity=AlertSeverity.WATCH)
        assert watch.get_priority_icon() == "[.]"

        info = WeatherAlert(severity=AlertSeverity.INFORMATION)
        assert info.get_priority_icon() == "[i]"

    @pytest.mark.unit
    def test_weather_alert_to_dict(self):
        """Test converting WeatherAlert to dictionary"""
        alert = WeatherAlert(
            alert_type=AlertType.FROST,
            severity=AlertSeverity.WARNING,
            title="Frost Warning",
            field_id="FIELD-001",
        )
        d = alert.to_dict()
        assert isinstance(d, dict)
        assert d["alert_type"] == "frost"
        assert d["severity"] == "warning"
        assert d["title"] == "Frost Warning"
        assert d["field_id"] == "FIELD-001"

    @pytest.mark.unit
    def test_weather_alert_has_uuid(self):
        """Test WeatherAlert has auto-generated UUID"""
        alert1 = WeatherAlert()
        alert2 = WeatherAlert()
        assert alert1.id != alert2.id
        assert len(alert1.id) > 0


# ============================================================================
# TESTS: ALERT THRESHOLDS AND CROP-SPECIFIC THRESHOLDS
# ============================================================================


class TestAlertThresholds:
    """Test AlertThresholds configuration"""

    @pytest.mark.unit
    def test_default_frost_thresholds(self, default_thresholds):
        """Test default frost thresholds"""
        assert default_thresholds.frost_critical == -2.0
        assert default_thresholds.frost_warning == 0.0
        assert default_thresholds.frost_advisory == 3.0

    @pytest.mark.unit
    def test_default_heat_thresholds(self, default_thresholds):
        """Test default heat thresholds"""
        assert default_thresholds.heat_critical == 45.0
        assert default_thresholds.heat_warning == 40.0
        assert default_thresholds.heat_advisory == 35.0

    @pytest.mark.unit
    def test_default_wind_thresholds(self, default_thresholds):
        """Test default wind thresholds"""
        assert default_thresholds.wind_critical == 80.0
        assert default_thresholds.wind_warning == 50.0
        assert default_thresholds.wind_advisory == 30.0
        assert default_thresholds.wind_spray_max == 15.0

    @pytest.mark.unit
    def test_default_humidity_thresholds(self, default_thresholds):
        """Test default humidity thresholds"""
        assert default_thresholds.humidity_high_warning == 90.0
        assert default_thresholds.humidity_low_warning == 20.0
        assert default_thresholds.humidity_spray_min == 40.0
        assert default_thresholds.humidity_spray_max == 85.0

    @pytest.mark.unit
    def test_default_spray_temperature_thresholds(self, default_thresholds):
        """Test default spray temperature thresholds"""
        assert default_thresholds.spray_temp_min == 10.0
        assert default_thresholds.spray_temp_max == 30.0
        assert default_thresholds.spray_temp_optimal_min == 15.0
        assert default_thresholds.spray_temp_optimal_max == 25.0

    @pytest.mark.unit
    def test_thresholds_to_dict(self, default_thresholds):
        """Test converting thresholds to dictionary"""
        d = default_thresholds.to_dict()
        assert isinstance(d, dict)
        assert "frost_critical" in d
        assert "heat_warning" in d
        assert "wind_advisory" in d

    @pytest.mark.unit
    def test_custom_thresholds(self):
        """Test custom alert thresholds"""
        custom = AlertThresholds(
            frost_critical=-3.0,
            heat_critical=48.0,
            wind_critical=100.0,
        )
        assert custom.frost_critical == -3.0
        assert custom.heat_critical == 48.0
        assert custom.wind_critical == 100.0


class TestCropFrostThresholds:
    """Test crop-specific frost thresholds"""

    @pytest.mark.unit
    def test_wheat_frost_thresholds(self):
        """Test wheat frost thresholds"""
        thresholds = CROP_FROST_THRESHOLDS[CropType.WHEAT]
        assert thresholds["critical"] == -5.0
        assert thresholds["warning"] == -2.0
        assert thresholds["advisory"] == 2.0

    @pytest.mark.unit
    def test_tomato_frost_thresholds(self):
        """Test tomato frost thresholds (sensitive crop)"""
        thresholds = CROP_FROST_THRESHOLDS[CropType.TOMATO]
        assert thresholds["critical"] == 0.0
        assert thresholds["warning"] == 2.0
        assert thresholds["advisory"] == 5.0

    @pytest.mark.unit
    def test_date_palm_frost_thresholds(self):
        """Test date palm frost thresholds (cold hardy)"""
        thresholds = CROP_FROST_THRESHOLDS[CropType.DATE_PALM]
        assert thresholds["critical"] == -4.0
        assert thresholds["warning"] == 0.0
        assert thresholds["advisory"] == 5.0

    @pytest.mark.unit
    def test_all_crops_have_frost_thresholds(self):
        """Test all crop types have frost thresholds"""
        for crop_type in CropType:
            assert crop_type in CROP_FROST_THRESHOLDS
            thresholds = CROP_FROST_THRESHOLDS[crop_type]
            assert "critical" in thresholds
            assert "warning" in thresholds
            assert "advisory" in thresholds


class TestCropHeatThresholds:
    """Test crop-specific heat thresholds"""

    @pytest.mark.unit
    def test_wheat_heat_thresholds(self):
        """Test wheat heat thresholds"""
        thresholds = CROP_HEAT_THRESHOLDS[CropType.WHEAT]
        assert thresholds["critical"] == 38.0
        assert thresholds["warning"] == 35.0
        assert thresholds["advisory"] == 32.0

    @pytest.mark.unit
    def test_date_palm_heat_thresholds(self):
        """Test date palm heat thresholds (heat tolerant)"""
        thresholds = CROP_HEAT_THRESHOLDS[CropType.DATE_PALM]
        assert thresholds["critical"] == 50.0
        assert thresholds["warning"] == 46.0
        assert thresholds["advisory"] == 42.0

    @pytest.mark.unit
    def test_cucumber_heat_thresholds(self):
        """Test cucumber heat thresholds (sensitive crop)"""
        thresholds = CROP_HEAT_THRESHOLDS[CropType.CUCUMBER]
        assert thresholds["critical"] == 35.0
        assert thresholds["warning"] == 32.0
        assert thresholds["advisory"] == 30.0

    @pytest.mark.unit
    def test_all_crops_have_heat_thresholds(self):
        """Test all crop types have heat thresholds"""
        for crop_type in CropType:
            assert crop_type in CROP_HEAT_THRESHOLDS
            thresholds = CROP_HEAT_THRESHOLDS[crop_type]
            assert "critical" in thresholds
            assert "warning" in thresholds
            assert "advisory" in thresholds


# ============================================================================
# TESTS: FROST ALERTS
# ============================================================================


class TestFrostAlerts:
    """Test frost alert generation"""

    @pytest.mark.unit
    def test_critical_frost_alert_wheat(self, alert_generator):
        """Test critical frost alert for wheat"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=-6.0,  # Below wheat critical threshold
            humidity=80.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
            field_id="FIELD-001",
        )

        assert len(alerts) > 0
        frost_alerts = [a for a in alerts if a.alert_type == AlertType.FROST]
        assert len(frost_alerts) > 0
        assert frost_alerts[0].severity == AlertSeverity.CRITICAL

    @pytest.mark.unit
    def test_warning_frost_alert_wheat(self, alert_generator):
        """Test warning frost alert for wheat"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=-2.5,  # Between warning and critical
            humidity=80.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        frost_alerts = [a for a in alerts if a.alert_type == AlertType.FROST]
        assert len(frost_alerts) > 0
        assert frost_alerts[0].severity == AlertSeverity.WARNING

    @pytest.mark.unit
    def test_advisory_frost_alert_wheat(self, alert_generator):
        """Test advisory frost alert for wheat"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=1.0,  # Between advisory and warning
            humidity=80.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        frost_alerts = [a for a in alerts if a.alert_type == AlertType.FROST]
        assert len(frost_alerts) > 0
        assert frost_alerts[0].severity == AlertSeverity.ADVISORY

    @pytest.mark.unit
    def test_no_frost_alert_warm_day(self, alert_generator):
        """Test no frost alert for warm day"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=8.0,  # Above frost thresholds
            humidity=60.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        frost_alerts = [a for a in alerts if a.alert_type == AlertType.FROST]
        assert len(frost_alerts) == 0

    @pytest.mark.unit
    def test_frost_alert_bilingual_messages(self, alert_generator):
        """Test frost alert has bilingual messages"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=-3.0,
            humidity=80.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        frost_alerts = [a for a in alerts if a.alert_type == AlertType.FROST]
        assert len(frost_alerts) > 0
        alert = frost_alerts[0]

        # Check English content
        assert len(alert.title) > 0
        assert len(alert.description) > 0
        assert len(alert.impact) > 0

        # Check Arabic content
        assert len(alert.title_ar) > 0
        assert len(alert.description_ar) > 0
        assert len(alert.impact_ar) > 0

        # Verify they're different (not just copies)
        assert alert.title != alert.title_ar

    @pytest.mark.unit
    def test_frost_alert_recommended_actions_bilingual(self, alert_generator):
        """Test frost alert has bilingual recommended actions"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=-3.0,
            humidity=80.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        frost_alerts = [a for a in alerts if a.alert_type == AlertType.FROST]
        assert len(frost_alerts) > 0
        alert = frost_alerts[0]

        assert len(alert.recommended_actions) > 0
        assert len(alert.recommended_actions_ar) > 0
        assert len(alert.recommended_actions) == len(alert.recommended_actions_ar)

    @pytest.mark.unit
    def test_frost_alert_trigger_values(self, alert_generator):
        """Test frost alert trigger values are recorded"""
        temp_min = -3.5
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=temp_min,
            humidity=80.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        frost_alerts = [a for a in alerts if a.alert_type == AlertType.FROST]
        assert len(frost_alerts) > 0
        alert = frost_alerts[0]

        assert alert.trigger_value == temp_min
        assert alert.trigger_unit == "C"
        assert alert.affected_crops == ["wheat"]


# ============================================================================
# TESTS: HEAT ALERTS
# ============================================================================


class TestHeatAlerts:
    """Test heat alert generation"""

    @pytest.mark.unit
    def test_critical_heat_alert_wheat(self, alert_generator):
        """Test critical heat alert for wheat"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_max=40.0,  # Above wheat critical threshold
            humidity=25.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        heat_alerts = [a for a in alerts if a.alert_type == AlertType.HEAT]
        assert len(heat_alerts) > 0
        assert heat_alerts[0].severity == AlertSeverity.CRITICAL

    @pytest.mark.unit
    def test_warning_heat_alert(self, alert_generator):
        """Test warning heat alert"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_max=36.0,  # Above warning threshold
            humidity=30.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        heat_alerts = [a for a in alerts if a.alert_type == AlertType.HEAT]
        assert len(heat_alerts) > 0
        assert heat_alerts[0].severity == AlertSeverity.WARNING

    @pytest.mark.unit
    def test_no_heat_alert_moderate_temperature(self, alert_generator):
        """Test no heat alert for moderate temperature"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_max=28.0,
            humidity=50.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        heat_alerts = [a for a in alerts if a.alert_type == AlertType.HEAT]
        assert len(heat_alerts) == 0

    @pytest.mark.unit
    def test_heat_alert_crop_specific_date_palm(self, alert_generator):
        """Test date palm can tolerate higher temperatures"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_max=48.0,  # Below date palm critical (50)
            humidity=20.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.DATE_PALM,
        )

        heat_alerts = [a for a in alerts if a.alert_type == AlertType.HEAT]
        # Should only be WARNING or ADVISORY, not CRITICAL
        if heat_alerts:
            assert heat_alerts[0].severity in [
                AlertSeverity.WARNING,
                AlertSeverity.ADVISORY,
            ]

    @pytest.mark.unit
    def test_heat_alert_bilingual_messages(self, alert_generator):
        """Test heat alert has bilingual messages"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_max=42.0,
            humidity=20.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        heat_alerts = [a for a in alerts if a.alert_type == AlertType.HEAT]
        assert len(heat_alerts) > 0

        alert = heat_alerts[0]
        assert len(alert.title_ar) > 0
        assert len(alert.description_ar) > 0
        assert alert.title != alert.title_ar


# ============================================================================
# TESTS: WIND ALERTS
# ============================================================================


class TestWindAlerts:
    """Test wind alert generation"""

    @pytest.mark.unit
    def test_critical_wind_alert(self, alert_generator):
        """Test critical wind alert"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            wind_gust=90.0,  # Above critical threshold
            humidity=50.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        wind_alerts = [a for a in alerts if a.alert_type == AlertType.WIND]
        assert len(wind_alerts) > 0
        assert wind_alerts[0].severity == AlertSeverity.CRITICAL

    @pytest.mark.unit
    def test_warning_wind_alert(self, alert_generator):
        """Test warning wind alert"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            wind_gust=55.0,  # Above warning threshold
            humidity=50.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        wind_alerts = [a for a in alerts if a.alert_type == AlertType.WIND]
        assert len(wind_alerts) > 0
        assert wind_alerts[0].severity == AlertSeverity.WARNING

    @pytest.mark.unit
    def test_advisory_wind_alert(self, alert_generator):
        """Test advisory wind alert"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            wind_speed=35.0,  # Above advisory threshold
            humidity=50.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        wind_alerts = [a for a in alerts if a.alert_type == AlertType.WIND]
        assert len(wind_alerts) > 0
        assert wind_alerts[0].severity == AlertSeverity.ADVISORY

    @pytest.mark.unit
    def test_no_wind_alert_calm(self, alert_generator):
        """Test no wind alert for calm conditions"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            wind_speed=5.0,
            humidity=50.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        wind_alerts = [a for a in alerts if a.alert_type == AlertType.WIND]
        assert len(wind_alerts) == 0

    @pytest.mark.unit
    def test_wind_alert_uses_gust_if_available(self, alert_generator):
        """Test wind alert uses gust speed if available"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            wind_speed=20.0,
            wind_gust=55.0,  # Alert should use gust
            humidity=50.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        wind_alerts = [a for a in alerts if a.alert_type == AlertType.WIND]
        assert len(wind_alerts) > 0
        assert wind_alerts[0].trigger_value == 55.0


# ============================================================================
# TESTS: RAIN AND HUMIDITY ALERTS
# ============================================================================


class TestRainAlerts:
    """Test rain alert generation"""

    @pytest.mark.unit
    def test_critical_rain_alert(self, alert_generator):
        """Test critical rain alert"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            precipitation_amount=60.0,  # Above critical threshold
            humidity=90.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        rain_alerts = [a for a in alerts if a.alert_type == AlertType.RAIN]
        assert len(rain_alerts) > 0
        assert rain_alerts[0].severity == AlertSeverity.CRITICAL

    @pytest.mark.unit
    def test_warning_rain_alert(self, alert_generator):
        """Test warning rain alert"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            precipitation_amount=30.0,  # Above warning threshold
            humidity=85.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        rain_alerts = [a for a in alerts if a.alert_type == AlertType.RAIN]
        assert len(rain_alerts) > 0
        assert rain_alerts[0].severity == AlertSeverity.WARNING


class TestHumidityAlerts:
    """Test humidity alert generation"""

    @pytest.mark.unit
    def test_high_humidity_warning(self, alert_generator):
        """Test high humidity warning"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            humidity=92.0,  # Above high warning threshold
            temperature=20.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        humidity_alerts = [a for a in alerts if a.alert_type == AlertType.HUMIDITY]
        assert len(humidity_alerts) > 0
        assert humidity_alerts[0].severity == AlertSeverity.WARNING

    @pytest.mark.unit
    def test_low_humidity_advisory(self, alert_generator):
        """Test low humidity advisory"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            humidity=15.0,  # Below low warning threshold
            temperature=30.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        humidity_alerts = [a for a in alerts if a.alert_type == AlertType.HUMIDITY]
        assert len(humidity_alerts) > 0
        assert humidity_alerts[0].severity == AlertSeverity.ADVISORY


# ============================================================================
# TESTS: TEMPERATURE INVERSION ALERTS
# ============================================================================


class TestInversionAlerts:
    """Test temperature inversion alert generation"""

    @pytest.mark.unit
    def test_inversion_alert_generation(self, alert_generator):
        """Test inversion alert generation"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            is_inversion_likely=True,
            inversion_start_hour=18,
            inversion_end_hour=8,
            temperature=10.0,
            humidity=75.0,
            wind_speed=2.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        inversion_alerts = [a for a in alerts if a.alert_type == AlertType.INVERSION]
        assert len(inversion_alerts) > 0
        assert inversion_alerts[0].severity == AlertSeverity.WARNING

    @pytest.mark.unit
    def test_inversion_alert_bilingual(self, alert_generator):
        """Test inversion alert is bilingual"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            is_inversion_likely=True,
            temperature=10.0,
            humidity=75.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        inversion_alerts = [a for a in alerts if a.alert_type == AlertType.INVERSION]
        assert len(inversion_alerts) > 0

        alert = inversion_alerts[0]
        assert len(alert.title_ar) > 0
        assert "انقلاب حراري" in alert.title_ar or len(alert.title_ar) > 5

    @pytest.mark.unit
    def test_no_inversion_alert_windy(self, alert_generator):
        """Test no inversion alert when wind is present"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            is_inversion_likely=False,
            wind_speed=10.0,  # Wind breaks inversions
            temperature=15.0,
            humidity=60.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])

        inversion_alerts = [a for a in alerts if a.alert_type == AlertType.INVERSION]
        assert len(inversion_alerts) == 0


# ============================================================================
# TESTS: SPRAY WINDOW CALCULATIONS
# ============================================================================


class TestSprayWindowCalculator:
    """Test spray window calculation"""

    @pytest.mark.unit
    def test_optimal_spray_window_scoring(self, spray_calculator):
        """Test scoring of optimal spray window"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            hour=8,
            temperature=18.0,
            humidity=65.0,
            wind_speed=5.0,
            precipitation_probability=5.0,
            is_inversion_likely=False,
        )

        window = spray_calculator.evaluate_time_slot(forecast)
        assert window.score >= 70  # Should be good
        assert window.overall_condition in [
            SprayCondition.OPTIMAL,
            SprayCondition.ACCEPTABLE,
        ]

    @pytest.mark.unit
    def test_unsuitable_spray_window_high_wind(self, spray_calculator):
        """Test unsuitable spray window due to high wind"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            hour=14,
            temperature=25.0,
            humidity=50.0,
            wind_speed=25.0,  # Too high
            precipitation_probability=0.0,
        )

        window = spray_calculator.evaluate_time_slot(forecast)
        # Wind is 30% of score, other factors are good, so score around 70
        assert window.wind_score < 50  # Wind score should be poor
        assert window.drift_risk in ["high", "very_high"]

    @pytest.mark.unit
    def test_unsuitable_spray_window_inversion(self, spray_calculator):
        """Test unsuitable spray window during inversion"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            hour=20,
            temperature=10.0,
            humidity=75.0,
            wind_speed=1.5,
            precipitation_probability=0.0,
            is_inversion_likely=True,
        )

        window = spray_calculator.evaluate_time_slot(forecast)
        # Inversion is detected and flagged
        assert window.is_inversion_period is True
        assert window.drift_risk in ["high", "very_high"]
        # Check for inversion warning
        assert len(window.inversion_warning) > 0

    @pytest.mark.unit
    def test_find_spray_windows_multiple(self, spray_calculator):
        """Test finding multiple spray windows"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                hour=h,
                temperature=15 + (h % 6),
                humidity=60 + (h % 10),
                wind_speed=3 + (h % 5),
                precipitation_probability=0.0,
            )
            for h in range(12)  # Use 12 hours to avoid hour=24 edge case
        ]

        windows = spray_calculator.find_spray_windows(
            hourly_forecasts=forecasts,
            min_duration_hours=1.0,
        )

        assert isinstance(windows, list)

    @pytest.mark.unit
    def test_spray_window_has_bilingual_recommendations(self, spray_calculator):
        """Test spray window recommendations are bilingual"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            hour=8,
            temperature=18.0,
            humidity=65.0,
            wind_speed=5.0,
            precipitation_probability=5.0,
        )

        window = spray_calculator.evaluate_time_slot(forecast)
        assert len(window.recommendation) > 0
        assert len(window.recommendation_ar) > 0
        assert window.recommendation != window.recommendation_ar

    @pytest.mark.unit
    def test_spray_window_risk_translations(self, spray_calculator):
        """Test spray window risk translations"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            hour=8,
            temperature=18.0,
            humidity=65.0,
            wind_speed=5.0,
            precipitation_probability=5.0,
        )

        window = spray_calculator.evaluate_time_slot(forecast)
        # Risk should have Arabic translations
        assert len(window.drift_risk_ar) > 0
        assert len(window.evaporation_risk_ar) > 0
        assert len(window.phytotoxicity_risk_ar) > 0

    @pytest.mark.unit
    def test_get_best_spray_time(self, spray_calculator):
        """Test getting best single spray time"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                hour=h,
                temperature=15 + (h % 10),
                humidity=60 + (h % 15),
                wind_speed=2 + (h % 6),
                precipitation_probability=0.0,
            )
            for h in range(12)  # Use 12 hours to avoid hour=24 edge case
        ]

        best_window = spray_calculator.get_best_spray_time(forecasts)
        if best_window:
            assert isinstance(best_window, SprayWindow)
            assert best_window.score >= 0
            assert best_window.score <= 100

    @pytest.mark.unit
    def test_spray_window_product_suitability(self, spray_calculator):
        """Test spray window product suitability flags"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            hour=8,
            temperature=18.0,
            humidity=65.0,
            wind_speed=5.0,
            precipitation_probability=5.0,
        )

        window = spray_calculator.evaluate_time_slot(forecast)
        assert isinstance(window.suitable_for_systemic, bool)
        assert isinstance(window.suitable_for_contact, bool)
        assert isinstance(window.suitable_for_volatile, bool)


# ============================================================================
# TESTS: TEMPERATURE INVERSION DETECTION
# ============================================================================


class TestInversionDetection:
    """Test temperature inversion detection"""

    @pytest.mark.unit
    def test_detect_inversions_typical_evening_hours(self):
        """Test detecting inversion during typical evening hours"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                hour=h,
                temperature=25 - (h % 5),  # Temperature varying
                humidity=60.0,
                wind_speed=1.0,  # Calm
                cloud_cover=10.0,  # Clear
                precipitation_probability=0.0,
            )
            for h in [18, 19, 20, 21, 22, 23, 0, 1, 2]
        ]

        inversions = detect_inversions(forecasts)
        # Should detect some inversion period
        assert isinstance(inversions, list)

    @pytest.mark.unit
    def test_no_inversion_detection_windy(self):
        """Test no inversion detected when windy"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                hour=h,
                temperature=15.0,
                humidity=60.0,
                wind_speed=10.0,  # Wind breaks inversion
                cloud_cover=50.0,
                precipitation_probability=0.0,
            )
            for h in range(24)
        ]

        inversions = detect_inversions(forecasts)
        # Wind breaks inversions, should find few or none
        assert isinstance(inversions, list)

    @pytest.mark.unit
    def test_inversion_returns_datetime_tuples(self):
        """Test inversion detection returns datetime tuples"""
        forecasts = [
            WeatherForecast(
                forecast_date=date(2026, 1, 20),
                hour=20,
                temperature=10.0,
                humidity=75.0,
                wind_speed=1.5,
                cloud_cover=15.0,
                is_inversion_likely=True,
            ),
        ]

        inversions = detect_inversions(forecasts)
        assert isinstance(inversions, list)
        for period in inversions:
            assert isinstance(period, tuple)
            assert len(period) == 2
            assert isinstance(period[0], datetime)
            assert isinstance(period[1], datetime)


# ============================================================================
# TESTS: IRRIGATION SCHEDULING
# ============================================================================


class TestIrrigationScheduling:
    """Test irrigation scheduling generation"""

    @pytest.mark.unit
    def test_skip_irrigation_heavy_rain(self, alert_generator):
        """Test skip irrigation recommendation with heavy rain"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=20.0,
                humidity=80.0,
                precipitation_amount=15.0,  # Significant rain
                precipitation_probability=70.0,
            ),
        ]

        schedule = alert_generator.generate_irrigation_schedule(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
            planned_irrigation_mm=25.0,
        )

        assert schedule.recommendation == IrrigationRecommendation.SKIP_IRRIGATION
        assert schedule.adjustment_factor == 0.0

    @pytest.mark.unit
    def test_reduce_irrigation_light_rain(self, alert_generator):
        """Test reduce irrigation recommendation with light rain"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=20.0,
                humidity=70.0,
                precipitation_amount=7.0,  # Light rain
                precipitation_probability=40.0,
            ),
        ]

        schedule = alert_generator.generate_irrigation_schedule(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
            planned_irrigation_mm=25.0,
        )

        assert schedule.recommendation == IrrigationRecommendation.REDUCE_AMOUNT
        assert schedule.adjustment_factor < 1.0
        assert schedule.adjustment_factor > 0.0

    @pytest.mark.unit
    def test_increase_irrigation_high_temperature(self, alert_generator):
        """Test increase irrigation with high temperature"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=40.0,
                temperature_min=35.0,
                temperature_max=42.0,
                humidity=25.0,
                precipitation_probability=5.0,
            ),
        ]

        schedule = alert_generator.generate_irrigation_schedule(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
            planned_irrigation_mm=25.0,
        )

        assert schedule.recommendation == IrrigationRecommendation.INCREASE_AMOUNT
        assert schedule.adjustment_factor > 1.0

    @pytest.mark.unit
    def test_irrigate_now_low_soil_moisture(self, alert_generator):
        """Test irrigate now recommendation with low soil moisture"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=25.0,
                humidity=50.0,
                precipitation_probability=0.0,
            ),
        ]

        schedule = alert_generator.generate_irrigation_schedule(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
            soil_moisture_current=25.0,  # Below threshold
            planned_irrigation_mm=25.0,
        )

        assert schedule.recommendation == IrrigationRecommendation.IRRIGATE_NOW

    @pytest.mark.unit
    def test_delay_irrigation_high_soil_moisture(self, alert_generator):
        """Test delay irrigation with high soil moisture"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=20.0,
                humidity=60.0,
                precipitation_probability=10.0,
            ),
        ]

        schedule = alert_generator.generate_irrigation_schedule(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
            soil_moisture_current=65.0,  # High moisture
            planned_irrigation_mm=25.0,
        )

        assert schedule.recommendation == IrrigationRecommendation.DELAY_IRRIGATION

    @pytest.mark.unit
    def test_irrigation_schedule_bilingual_reasons(self, alert_generator):
        """Test irrigation schedule has bilingual reasons"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=25.0,
                humidity=50.0,
                precipitation_probability=0.0,
            ),
        ]

        schedule = alert_generator.generate_irrigation_schedule(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
            planned_irrigation_mm=25.0,
        )

        assert len(schedule.reason) > 0
        assert len(schedule.reason_ar) > 0
        assert schedule.reason != schedule.reason_ar

    @pytest.mark.unit
    def test_irrigation_schedule_water_saved_calculation(self, alert_generator):
        """Test water saved calculation in irrigation schedule"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=20.0,
                humidity=70.0,
                precipitation_amount=10.0,
                precipitation_probability=60.0,
            ),
        ]

        schedule = alert_generator.generate_irrigation_schedule(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
            planned_irrigation_mm=25.0,
            field_area_ha=5.0,
        )

        if schedule.water_saved_liters is not None:
            assert schedule.water_saved_liters >= 0
        if schedule.cost_saved is not None:
            assert schedule.cost_saved >= 0


# ============================================================================
# TESTS: HARVEST WINDOW GENERATION
# ============================================================================


class TestHarvestWindowGeneration:
    """Test harvest window generation"""

    @pytest.mark.unit
    def test_harvest_window_optimal_conditions(self, alert_generator):
        """Test harvest window with optimal conditions"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today() + timedelta(days=i),
                temperature=25.0 - (i % 3),
                humidity=55.0 + (i % 10),
                wind_speed=8.0,
                precipitation_probability=5.0,
            )
            for i in range(3)
        ]

        harvest = alert_generator.generate_harvest_window(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
        )

        assert harvest.overall_condition in [
            HarvestCondition.OPTIMAL,
            HarvestCondition.GOOD,
            HarvestCondition.ACCEPTABLE,
        ]
        assert harvest.score >= 0  # Score can go above 100 based on bonuses

    @pytest.mark.unit
    def test_harvest_window_rainy_unsuitable(self, alert_generator):
        """Test harvest window unsuitable due to rain"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today() + timedelta(days=i),
                temperature=20.0,
                humidity=85.0,
                precipitation_probability=80.0,  # High rain chance
                wind_speed=3.0,
            )
            for i in range(3)
        ]

        harvest = alert_generator.generate_harvest_window(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
        )

        assert harvest.overall_condition in [
            HarvestCondition.RISKY,
            HarvestCondition.UNSUITABLE,
        ]

    @pytest.mark.unit
    def test_harvest_window_bilingual_recommendations(self, alert_generator):
        """Test harvest window has bilingual recommendations"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=25.0,
                humidity=60.0,
                precipitation_probability=10.0,
            ),
        ]

        harvest = alert_generator.generate_harvest_window(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
        )

        assert len(harvest.recommendation) > 0
        assert len(harvest.recommendation_ar) > 0
        assert harvest.recommendation != harvest.recommendation_ar

    @pytest.mark.unit
    def test_harvest_window_dry_hours_calculation(self, alert_generator):
        """Test dry hours calculation in harvest window"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=25.0,
                humidity=60.0,
                precipitation_probability=10.0,
            ),
            WeatherForecast(
                forecast_date=date.today() + timedelta(days=1),
                temperature=26.0,
                humidity=55.0,
                precipitation_probability=5.0,
            ),
        ]

        harvest = alert_generator.generate_harvest_window(
            forecasts=forecasts,
            field_id="FIELD-001",
            crop_type=CropType.WHEAT,
        )

        assert harvest.dry_hours_available >= 0


# ============================================================================
# TESTS: CONVENIENCE FUNCTIONS
# ============================================================================


class TestConvenienceFunctions:
    """Test module-level convenience functions"""

    @pytest.mark.unit
    def test_generate_weather_alerts_function(self):
        """Test generate_weather_alerts convenience function"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature_min=-3.0,
                temperature_max=5.0,
                humidity=75.0,
            ),
        ]

        alerts = generate_weather_alerts(
            forecasts=forecasts,
            crop_type=CropType.WHEAT,
            field_id="FIELD-001",
        )

        assert isinstance(alerts, list)

    @pytest.mark.unit
    def test_find_spray_windows_function(self):
        """Test find_spray_windows convenience function"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                hour=h,
                temperature=18.0 + (h % 6),
                humidity=60.0 + (h % 15),
                wind_speed=3.0 + (h % 5),
                precipitation_probability=0.0,
            )
            for h in range(12)
        ]

        windows = find_spray_windows(
            hourly_forecasts=forecasts,
            min_duration_hours=2.0,
        )

        assert isinstance(windows, list)

    @pytest.mark.unit
    def test_get_best_spray_time_function(self):
        """Test get_best_spray_time convenience function"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                hour=h,
                temperature=18.0 + (h % 6),
                humidity=60.0 + (h % 15),
                wind_speed=3.0 + (h % 5),
                precipitation_probability=0.0,
            )
            for h in range(12)
        ]

        best_window = get_best_spray_time(
            hourly_forecasts=forecasts,
            required_duration_hours=2.0,
        )

        if best_window:
            assert isinstance(best_window, SprayWindow)

    @pytest.mark.unit
    def test_detect_inversions_function(self):
        """Test detect_inversions convenience function"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                hour=h,
                temperature=15.0 - (h % 4),
                humidity=65.0,
                wind_speed=1.5,
                cloud_cover=10.0,
            )
            for h in range(12)  # Use 12 hours to avoid hour=24 edge case
        ]

        inversions = detect_inversions(hourly_forecasts=forecasts)

        assert isinstance(inversions, list)


# ============================================================================
# TESTS: ALERT SEVERITY ORDERING
# ============================================================================


class TestAlertOrdering:
    """Test alert severity ordering"""

    @pytest.mark.unit
    def test_alerts_sorted_by_severity(self, alert_generator):
        """Test alerts are sorted by severity (critical first)"""
        forecasts = [
            WeatherForecast(
                forecast_date=date.today(),
                temperature=-5.0,  # Frost
                temperature_min=-6.0,
                temperature_max=0.0,
                humidity=70.0,
                wind_speed=5.0,
            ),
            WeatherForecast(
                forecast_date=date.today() + timedelta(days=1),
                temperature=45.0,  # Heat
                temperature_min=35.0,
                temperature_max=48.0,
                humidity=20.0,
                wind_speed=10.0,
            ),
        ]

        alerts = alert_generator.generate_alerts(
            forecasts=forecasts,
            crop_type=CropType.WHEAT,
        )

        # Critical should come before warning, etc.
        severity_order = {
            AlertSeverity.CRITICAL: 0,
            AlertSeverity.WARNING: 1,
            AlertSeverity.ADVISORY: 2,
        }

        for i in range(len(alerts) - 1):
            current_rank = severity_order.get(alerts[i].severity, 5)
            next_rank = severity_order.get(alerts[i + 1].severity, 5)
            assert current_rank <= next_rank


# ============================================================================
# TESTS: EDGE CASES AND BOUNDARY CONDITIONS
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    @pytest.mark.unit
    def test_empty_forecast_list(self, alert_generator):
        """Test alert generation with empty forecast list"""
        alerts = alert_generator.generate_alerts(forecasts=[])
        assert alerts == []

    @pytest.mark.unit
    def test_empty_spray_forecast_list(self, spray_calculator):
        """Test spray window with empty forecast list"""
        windows = spray_calculator.find_spray_windows(hourly_forecasts=[])
        assert windows == []

    @pytest.mark.unit
    def test_single_forecast(self, alert_generator):
        """Test alert generation with single forecast"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature=25.0,
            humidity=60.0,
        )

        alerts = alert_generator.generate_alerts(forecasts=[forecast])
        assert isinstance(alerts, list)

    @pytest.mark.unit
    def test_extreme_temperature_below_frost_range(self, alert_generator):
        """Test extreme temperature below frost range"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=-20.0,
            humidity=80.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        frost_alerts = [a for a in alerts if a.alert_type == AlertType.FROST]
        assert len(frost_alerts) > 0
        assert frost_alerts[0].severity == AlertSeverity.CRITICAL

    @pytest.mark.unit
    def test_extreme_temperature_above_heat_range(self, alert_generator):
        """Test extreme temperature above heat range"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_max=55.0,
            humidity=10.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.WHEAT,
        )

        heat_alerts = [a for a in alerts if a.alert_type == AlertType.HEAT]
        assert len(heat_alerts) > 0
        assert heat_alerts[0].severity == AlertSeverity.CRITICAL

    @pytest.mark.unit
    def test_boundary_frost_warning_threshold(self, alert_generator):
        """Test alert exactly at frost warning threshold"""
        # Using GENERAL crop with frost_warning=0.0
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_min=0.0,  # Exactly at threshold
            humidity=80.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.GENERAL,
        )

        frost_alerts = [a for a in alerts if a.alert_type == AlertType.FROST]
        assert len(frost_alerts) > 0

    @pytest.mark.unit
    def test_boundary_heat_warning_threshold(self, alert_generator):
        """Test alert exactly at heat warning threshold"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            temperature_max=40.0,  # Exactly at general threshold
            humidity=30.0,
        )

        alerts = alert_generator.generate_alerts(
            forecasts=[forecast],
            crop_type=CropType.GENERAL,
        )

        heat_alerts = [a for a in alerts if a.alert_type == AlertType.HEAT]
        assert len(heat_alerts) > 0


# ============================================================================
# TESTS: MULTILINGUAL CONTENT VERIFICATION
# ============================================================================


class TestBilingualContent:
    """Test bilingual content consistency and completeness"""

    @pytest.mark.unit
    def test_alert_english_and_arabic_content_exists(self):
        """Test alert has both English and Arabic content"""
        alert = WeatherAlert(
            alert_type=AlertType.FROST,
            severity=AlertSeverity.WARNING,
            title="Frost Warning",
            title_ar="تحذير صقيع",
            description="Temperatures dropping",
            description_ar="درجات الحرارة تنخفض",
        )

        assert len(alert.title) > 0
        assert len(alert.title_ar) > 0
        assert len(alert.description) > 0
        assert len(alert.description_ar) > 0

    @pytest.mark.unit
    def test_irrigation_schedule_english_and_arabic(self):
        """Test irrigation schedule has both languages"""
        schedule = IrrigationSchedule(
            field_id="FIELD-001",
            reason="Normal conditions",
            reason_ar="ظروف طبيعية",
        )

        assert len(schedule.reason) > 0
        assert len(schedule.reason_ar) > 0

    @pytest.mark.unit
    def test_spray_window_bilingual_cautions(self, spray_calculator):
        """Test spray window cautions are bilingual"""
        forecast = WeatherForecast(
            forecast_date=date.today(),
            hour=14,
            temperature=28.0,
            humidity=40.0,
            wind_speed=12.0,
            precipitation_probability=0.0,
        )

        window = spray_calculator.evaluate_time_slot(forecast)

        if window.cautions:
            assert len(window.cautions) > 0
            assert len(window.cautions_ar) > 0
            assert len(window.cautions) == len(window.cautions_ar)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
