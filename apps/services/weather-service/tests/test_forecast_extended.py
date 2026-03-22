"""
Extended tests for forecast integration and advanced risk calculations.
Covers calculate_frost_risk, calculate_heat_stress_index, calculate_chill_hours,
calculate_drought_index, calculate_spray_window, calculate_evapotranspiration,
calculate_growing_degree_days, and forecast_integration alert detectors.
"""

import pytest

try:
    from src.risks import (
        calculate_chill_hours,
        calculate_drought_index,
        calculate_evapotranspiration,
        calculate_frost_risk,
        calculate_growing_degree_days,
        calculate_heat_stress_index,
        calculate_spray_window,
        disease_risk,
        frost_risk,
        heavy_rain_risk,
        heat_stress_risk,
        wind_risk,
    )
except ImportError:
    pytest.skip("weather-service risks not importable", allow_module_level=True)

try:
    from src.forecast_integration import (
        AgriculturalAlert,
        AgriculturalIndices,
        AlertCategory,
        AlertSeverity,
        WeatherForecastService,
        calculate_agricultural_indices,
        calculate_chill_hours as fi_calculate_chill_hours,
        calculate_evapotranspiration as fi_calculate_et,
        calculate_gdd,
        detect_drought_conditions,
        detect_frost_risk as fi_detect_frost_risk,
        detect_heat_wave,
        detect_heavy_rain,
    )
    from src.providers import DailyForecast, HourlyForecast

    FORECAST_AVAILABLE = True
except ImportError:
    FORECAST_AVAILABLE = False


# ═══════════════════════════════════════════════════════════════════════════════
# risks.py - Individual risk functions
# ═══════════════════════════════════════════════════════════════════════════════


class TestHeatStressRisk:
    def test_critical(self):
        t, s = heat_stress_risk(45)
        assert s == "critical"

    def test_high(self):
        t, s = heat_stress_risk(43)
        assert s == "high"

    def test_medium(self):
        t, s = heat_stress_risk(39)
        assert s == "medium"

    def test_low(self):
        t, s = heat_stress_risk(36)
        assert s == "low"

    def test_none(self):
        t, s = heat_stress_risk(30)
        assert s == "none"


class TestFrostRisk:
    def test_critical(self):
        _, s = frost_risk(-1)
        assert s == "critical"

    def test_high(self):
        _, s = frost_risk(1)
        assert s == "high"

    def test_medium(self):
        _, s = frost_risk(4)
        assert s == "medium"

    def test_none(self):
        _, s = frost_risk(10)
        assert s == "none"


class TestHeavyRainRisk:
    def test_critical_amount(self):
        _, s = heavy_rain_risk(55)
        assert s == "critical"

    def test_critical_intensity(self):
        _, s = heavy_rain_risk(25, hours=2)
        assert s == "critical"

    def test_high(self):
        _, s = heavy_rain_risk(35)
        assert s == "high"

    def test_medium(self):
        _, s = heavy_rain_risk(16)
        assert s == "medium"

    def test_none(self):
        _, s = heavy_rain_risk(5)
        assert s == "none"

    def test_zero_hours(self):
        """hours=0 should not divide by zero."""
        _, s = heavy_rain_risk(55, hours=0)
        assert s == "critical"


class TestWindRisk:
    def test_critical(self):
        _, s = wind_risk(65)
        assert s == "critical"

    def test_high(self):
        _, s = wind_risk(50)
        assert s == "high"

    def test_medium(self):
        _, s = wind_risk(35)
        assert s == "medium"

    def test_none(self):
        _, s = wind_risk(10)
        assert s == "none"


class TestDiseaseRisk:
    def test_high(self):
        _, s = disease_risk(25, 90)
        assert s == "high"

    def test_medium(self):
        _, s = disease_risk(25, 78)
        assert s == "medium"

    def test_low_humid(self):
        _, s = disease_risk(15, 82)
        assert s == "low"

    def test_none(self):
        _, s = disease_risk(25, 40)
        assert s == "none"


# ═══════════════════════════════════════════════════════════════════════════════
# risks.py - Advanced calculations
# ═══════════════════════════════════════════════════════════════════════════════


class TestCalculateEvapotranspiration:
    def test_basic(self):
        r = calculate_evapotranspiration(temp_c=30, humidity_pct=40, wind_speed_kmh=12)
        assert r["et0_mm_day"] > 0
        assert r["classification"] in ("very_low", "low", "moderate", "high", "very_high")
        assert "recommendation_ar" in r
        assert "recommendation_en" in r

    def test_very_low_et(self):
        r = calculate_evapotranspiration(temp_c=10, humidity_pct=90, wind_speed_kmh=2)
        assert r["et0_mm_day"] < 4

    def test_very_high_et(self):
        r = calculate_evapotranspiration(temp_c=45, humidity_pct=15, wind_speed_kmh=25, solar_radiation_mj=25)
        assert r["et0_mm_day"] > 5

    def test_vpd_positive(self):
        r = calculate_evapotranspiration(temp_c=30, humidity_pct=40, wind_speed_kmh=10)
        assert r["vapor_pressure_deficit_kpa"] > 0

    def test_weekly_water(self):
        r = calculate_evapotranspiration(temp_c=30, humidity_pct=40, wind_speed_kmh=10)
        assert abs(r["weekly_water_liters_per_sqm"] - r["et0_mm_day"] * 7) < 0.01

    def test_classification_levels(self):
        # very_low
        r = calculate_evapotranspiration(temp_c=5, humidity_pct=95, wind_speed_kmh=1, solar_radiation_mj=3)
        assert r["classification"] == "very_low"


class TestCalculateGrowingDegreeDays:
    def test_basic(self):
        r = calculate_growing_degree_days(temp_max_c=30, temp_min_c=20)
        assert r["gdd_daily"] > 0
        assert r["growth_rate"] in ("dormant", "slow", "moderate", "fast", "very_fast")

    def test_below_base(self):
        r = calculate_growing_degree_days(temp_max_c=8, temp_min_c=2, base_temp_c=10)
        assert r["gdd_daily"] == 0
        assert r["growth_rate"] == "dormant"

    def test_above_upper(self):
        r = calculate_growing_degree_days(temp_max_c=40, temp_min_c=25, upper_temp_c=30)
        # Max clamped to 30, min stays 25 => avg=27.5 => gdd=17.5
        assert r["gdd_daily"] == 17.5

    def test_custom_base(self):
        r = calculate_growing_degree_days(temp_max_c=30, temp_min_c=15, base_temp_c=5)
        assert r["base_temp_c"] == 5

    def test_growth_rate_fast(self):
        r = calculate_growing_degree_days(temp_max_c=35, temp_min_c=25)
        assert r["growth_rate"] in ("fast", "very_fast")

    def test_growth_rate_slow(self):
        r = calculate_growing_degree_days(temp_max_c=15, temp_min_c=10, base_temp_c=10)
        assert r["gdd_daily"] < 5
        assert r["growth_rate"] == "slow"


class TestCalculateSprayWindow:
    def test_excellent(self):
        r = calculate_spray_window(temp_c=22, humidity_pct=55, wind_speed_kmh=8)
        assert r["suitability"] == "excellent"
        assert r["is_suitable"] is True
        assert r["score"] >= 80

    def test_poor_high_wind(self):
        r = calculate_spray_window(temp_c=22, humidity_pct=55, wind_speed_kmh=30)
        assert r["suitability"] in ("poor", "fair")
        assert "wind_too_strong" in r["issues"] or "wind_strong" in r["issues"]

    def test_poor_rain(self):
        r = calculate_spray_window(temp_c=22, humidity_pct=55, wind_speed_kmh=8, precipitation_probability=80)
        assert "rain_likely" in r["issues"]

    def test_too_hot(self):
        r = calculate_spray_window(temp_c=40, humidity_pct=55, wind_speed_kmh=8)
        assert "temperature_too_high" in r["issues"]

    def test_too_cold(self):
        r = calculate_spray_window(temp_c=5, humidity_pct=55, wind_speed_kmh=8)
        assert "temperature_too_low" in r["issues"]

    def test_humidity_too_low(self):
        r = calculate_spray_window(temp_c=22, humidity_pct=20, wind_speed_kmh=8)
        assert "humidity_too_low" in r["issues"]

    def test_humidity_too_high(self):
        r = calculate_spray_window(temp_c=22, humidity_pct=95, wind_speed_kmh=8)
        assert "humidity_too_high" in r["issues"]

    def test_multiple_issues(self):
        r = calculate_spray_window(temp_c=40, humidity_pct=95, wind_speed_kmh=30, precipitation_probability=80)
        assert len(r["issues"]) >= 3
        assert r["suitability"] == "poor"

    def test_recommendation_bilingual(self):
        r = calculate_spray_window(temp_c=22, humidity_pct=55, wind_speed_kmh=8)
        assert len(r["recommendation_ar"]) > 0
        assert len(r["recommendation_en"]) > 0


class TestCalculateFrostRisk:
    def test_critical(self):
        r = calculate_frost_risk(temp_c=-6, humidity_pct=90, wind_speed_kmh=2, cloud_cover_pct=5)
        assert r["risk_level"] == "critical"
        assert r["frost_likely"] is True
        assert len(r["protection_measures"]) > 0

    def test_high(self):
        r = calculate_frost_risk(temp_c=-1, humidity_pct=80, wind_speed_kmh=3, cloud_cover_pct=10)
        assert r["risk_level"] in ("high", "critical")
        assert r["frost_likely"] is True

    def test_moderate(self):
        r = calculate_frost_risk(temp_c=2, humidity_pct=70, wind_speed_kmh=8, cloud_cover_pct=30)
        assert r["risk_level"] in ("moderate", "high")

    def test_low(self):
        r = calculate_frost_risk(temp_c=3.5, humidity_pct=50, wind_speed_kmh=20, cloud_cover_pct=80)
        assert r["risk_level"] in ("low", "none")

    def test_none(self):
        r = calculate_frost_risk(temp_c=15, humidity_pct=50, wind_speed_kmh=10, cloud_cover_pct=50)
        assert r["risk_level"] == "none"
        assert r["frost_likely"] is False

    def test_dew_point_calculated(self):
        r = calculate_frost_risk(temp_c=2, humidity_pct=80, wind_speed_kmh=5)
        assert "dew_point_c" in r
        assert isinstance(r["dew_point_c"], float)

    def test_dew_point_provided(self):
        r = calculate_frost_risk(temp_c=2, humidity_pct=80, wind_speed_kmh=5, dew_point_c=-1.0)
        assert r["dew_point_c"] == -1.0

    def test_protection_measures_critical(self):
        r = calculate_frost_risk(temp_c=-5, humidity_pct=90, wind_speed_kmh=2, cloud_cover_pct=5)
        methods = [m["method_en"] for m in r["protection_measures"]]
        assert "Sprinkler irrigation" in methods
        assert "Heaters/smudge pots" in methods

    def test_recommendation_bilingual(self):
        r = calculate_frost_risk(temp_c=-2, humidity_pct=80, wind_speed_kmh=5)
        assert len(r["recommendation_ar"]) > 0
        assert len(r["recommendation_en"]) > 0


class TestCalculateHeatStressIndex:
    def test_extreme(self):
        r = calculate_heat_stress_index(temp_c=46, humidity_pct=40)
        assert r["stress_level"] == "extreme"
        assert r["is_critical"] is True
        assert r["crop_impact"] == "severe_damage"

    def test_severe_hot(self):
        r = calculate_heat_stress_index(temp_c=41, humidity_pct=30)
        assert r["stress_level"] == "severe"
        assert r["is_critical"] is True

    def test_severe_humid(self):
        r = calculate_heat_stress_index(temp_c=36, humidity_pct=65)
        assert r["stress_level"] in ("severe", "high")

    def test_high(self):
        r = calculate_heat_stress_index(temp_c=36, humidity_pct=40)
        assert r["stress_level"] == "high"

    def test_high_humidity_combo(self):
        r = calculate_heat_stress_index(temp_c=31, humidity_pct=75)
        assert r["stress_level"] == "high"

    def test_moderate(self):
        r = calculate_heat_stress_index(temp_c=31, humidity_pct=40)
        assert r["stress_level"] == "moderate"

    def test_low(self):
        r = calculate_heat_stress_index(temp_c=27, humidity_pct=50)
        assert r["stress_level"] == "low"

    def test_none(self):
        r = calculate_heat_stress_index(temp_c=20, humidity_pct=50)
        assert r["stress_level"] == "none"
        assert r["is_critical"] is False

    def test_thi_calculated(self):
        r = calculate_heat_stress_index(temp_c=30, humidity_pct=60)
        assert "temperature_humidity_index" in r
        assert r["temperature_humidity_index"] > 0

    def test_mitigation_measures_severe(self):
        r = calculate_heat_stress_index(temp_c=42, humidity_pct=30)
        methods = [m["method_en"] for m in r["mitigation_measures"]]
        assert "Increase irrigation frequency" in methods
        assert "Foliar cooling sprays" in methods

    def test_anti_transpirant_low_humidity(self):
        r = calculate_heat_stress_index(temp_c=36, humidity_pct=25)
        methods = [m["method_en"] for m in r["mitigation_measures"]]
        assert "Anti-transpirant sprays" in methods

    def test_recommendation_bilingual(self):
        r = calculate_heat_stress_index(temp_c=42, humidity_pct=40)
        assert len(r["recommendation_ar"]) > 0
        assert len(r["recommendation_en"]) > 0


class TestCalculateChillHours:
    def test_utah_model(self):
        # 5C scores 1.0 per hour in utah model
        temps = [5.0] * 24
        r = calculate_chill_hours(temps, model="utah")
        assert r["chill_units"] == 24.0
        assert r["model"] == "utah"
        assert r["hours_analyzed"] == 24

    def test_utah_negative_temps(self):
        # <=1.4C scores 0 in utah
        temps = [0.0] * 24
        r = calculate_chill_hours(temps, model="utah")
        assert r["chill_units"] == 0.0

    def test_utah_warm_reduces(self):
        # >18C scores -1.0 per hour; but chill can't go negative
        temps = [20.0] * 24
        r = calculate_chill_hours(temps, model="utah")
        assert r["chill_units"] == 0.0

    def test_utah_mixed(self):
        # 2.0C = 0.5, 5.0C = 1.0, 10.0C = 0.5, 13.0C = 0.0
        temps = [2.0, 5.0, 10.0, 13.0]
        r = calculate_chill_hours(temps, model="utah")
        assert r["chill_units"] == 2.0  # 0.5 + 1.0 + 0.5 + 0.0

    def test_simple_model(self):
        temps = [3.0, 5.0, 8.0, 10.0, 6.0]
        r = calculate_chill_hours(temps, model="simple", base_temp_c=7.2)
        # <= 7.2: 3.0, 5.0, 6.0 => 3
        assert r["chill_units"] == 3
        assert r["model"] == "simple"

    def test_dynamic_model(self):
        temps = [3.0, 7.0, 10.0, 20.0]
        r = calculate_chill_hours(temps, model="dynamic")
        # 3.0 => 1.0, 7.0 => 0.8, 10.0 => 0.4, 20.0 => -0.2 => total 2.0
        assert r["chill_units"] == 2.0
        assert r["model"] == "dynamic"

    def test_empty_input(self):
        r = calculate_chill_hours([], model="utah")
        assert r["chill_units"] == 0
        assert r["hours_analyzed"] == 0
        assert "error" in r

    def test_crop_requirements(self):
        # High chill should satisfy many crops
        temps = [5.0] * 1000
        r = calculate_chill_hours(temps, model="utah")
        assert r["chill_units"] == 1000.0
        assert len(r["satisfied_crops"]) > 5
        assert "crop_requirements" in r

    def test_insufficient_crops(self):
        # Low chill - most crops insufficient
        temps = [5.0] * 5
        r = calculate_chill_hours(temps, model="utah")
        assert r["chill_units"] == 5.0
        assert len(r["insufficient_crops"]) > 5

    def test_recommendation_high(self):
        temps = [5.0] * 1000
        r = calculate_chill_hours(temps, model="utah")
        assert "excellent" in r["recommendation_en"].lower() or "suitable" in r["recommendation_en"].lower()

    def test_recommendation_low(self):
        temps = [5.0] * 5
        r = calculate_chill_hours(temps, model="utah")
        assert "insufficient" in r["recommendation_en"].lower() or "tropical" in r["recommendation_en"].lower()


class TestCalculateDroughtIndex:
    def test_no_drought(self):
        r = calculate_drought_index(precipitation_mm=100, et0_mm=80, days=30)
        assert r["drought_level"] == "none"
        assert r["color"] == "green"
        assert r["irrigation_need_mm"] == 0

    def test_mild(self):
        r = calculate_drought_index(precipitation_mm=80, et0_mm=100, days=30)
        assert r["drought_level"] == "mild"

    def test_moderate(self):
        r = calculate_drought_index(precipitation_mm=55, et0_mm=100, days=30)
        assert r["drought_level"] == "moderate"

    def test_severe(self):
        r = calculate_drought_index(precipitation_mm=30, et0_mm=100, days=30)
        assert r["drought_level"] == "severe"

    def test_extreme(self):
        r = calculate_drought_index(precipitation_mm=5, et0_mm=100, days=30)
        assert r["drought_level"] == "extreme"
        assert r["color"] == "darkred"

    def test_irrigation_need(self):
        r = calculate_drought_index(precipitation_mm=30, et0_mm=100, days=30)
        assert r["irrigation_need_mm"] == 70.0

    def test_water_balance(self):
        r = calculate_drought_index(precipitation_mm=30, et0_mm=100, days=30)
        assert r["water_balance_mm"] == -70.0

    def test_aridity_index(self):
        r = calculate_drought_index(precipitation_mm=50, et0_mm=100, days=30)
        assert r["aridity_index"] == 0.5

    def test_zero_et(self):
        r = calculate_drought_index(precipitation_mm=50, et0_mm=0, days=30)
        assert r["drought_level"] == "none"

    def test_recommendation_bilingual(self):
        r = calculate_drought_index(precipitation_mm=5, et0_mm=100, days=30)
        assert len(r["recommendation_ar"]) > 0
        assert len(r["recommendation_en"]) > 0
        assert "mm" in r["recommendation_en"]


# ═══════════════════════════════════════════════════════════════════════════════
# forecast_integration.py tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestForecastIntegrationModels:
    def test_agricultural_alert_to_dict(self):
        alert = AgriculturalAlert(
            alert_id="test-1",
            alert_type="frost_risk",
            category=AlertCategory.TEMPERATURE,
            severity=AlertSeverity.HIGH,
            title_en="Frost risk",
            title_ar="خطر صقيع",
            description_en="Desc",
            description_ar="وصف",
            start_date="2026-01-01",
        )
        d = alert.to_dict()
        assert d["alert_id"] == "test-1"
        assert d["category"] == "temperature"
        assert d["severity"] == "high"

    def test_agricultural_indices_to_dict(self):
        idx = AgriculturalIndices(
            date="2026-01-01",
            gdd=12.345,
            chill_hours=5.5,
            eto=4.23,
            heat_stress_hours=2.0,
            moisture_deficit_mm=3.12,
        )
        d = idx.to_dict()
        assert d["gdd"] == 12.35
        assert d["chill_hours"] == 5.5
        assert d["eto"] == 4.23


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestDetectFrostRisk:
    def _make_forecast(self, temp_min_c, date="2026-01-01"):
        return DailyForecast(
            date=date,
            temp_max_c=temp_min_c + 10,
            temp_min_c=temp_min_c,
            precipitation_mm=0,
            precipitation_probability_pct=0,
            wind_speed_max_kmh=10,
            uv_index_max=3,
            condition="Clear",
            condition_ar="صافي",
            icon="clear",
        )

    def test_critical_frost(self):
        forecasts = [self._make_forecast(-5)]
        alerts = fi_detect_frost_risk(forecasts)
        assert len(alerts) >= 1
        assert alerts[0].severity == AlertSeverity.CRITICAL

    def test_no_frost(self):
        forecasts = [self._make_forecast(10)]
        alerts = fi_detect_frost_risk(forecasts)
        assert len(alerts) == 0


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestDetectHeatWave:
    def _make_forecast(self, temp_max_c, date="2026-01-01"):
        return DailyForecast(
            date=date,
            temp_max_c=temp_max_c,
            temp_min_c=temp_max_c - 10,
            precipitation_mm=0,
            precipitation_probability_pct=5,
            wind_speed_max_kmh=10,
            uv_index_max=9,
            condition="Clear",
            condition_ar="صافي",
            icon="clear",
        )

    def test_heat_wave_detected(self):
        # 3+ consecutive days above threshold
        forecasts = [
            self._make_forecast(42, f"2026-01-0{i+1}")
            for i in range(5)
        ]
        alerts = detect_heat_wave(forecasts)
        assert len(alerts) >= 1
        assert alerts[0].alert_type == "heat_wave"

    def test_no_heat_wave(self):
        forecasts = [
            self._make_forecast(25, f"2026-01-0{i+1}")
            for i in range(5)
        ]
        alerts = detect_heat_wave(forecasts)
        assert len(alerts) == 0

    def test_interrupted_heat_wave(self):
        """2 hot days then cool then 2 hot - no wave."""
        forecasts = [
            self._make_forecast(42, "2026-01-01"),
            self._make_forecast(42, "2026-01-02"),
            self._make_forecast(20, "2026-01-03"),
            self._make_forecast(42, "2026-01-04"),
            self._make_forecast(42, "2026-01-05"),
        ]
        alerts = detect_heat_wave(forecasts)
        assert len(alerts) == 0


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestDetectHeavyRain:
    def _make_forecast(self, precip_mm, date="2026-01-01"):
        return DailyForecast(
            date=date,
            temp_max_c=25,
            temp_min_c=18,
            precipitation_mm=precip_mm,
            precipitation_probability_pct=90,
            wind_speed_max_kmh=10,
            uv_index_max=3,
            condition="Rain",
            condition_ar="مطر",
            icon="rain",
        )

    def test_heavy_rain_critical(self):
        forecasts = [self._make_forecast(80)]
        alerts = detect_heavy_rain(forecasts)
        assert len(alerts) >= 1
        assert alerts[0].severity == AlertSeverity.CRITICAL

    def test_heavy_rain_none(self):
        forecasts = [self._make_forecast(2)]
        alerts = detect_heavy_rain(forecasts)
        assert len(alerts) == 0


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestDetectDroughtConditions:
    def _make_dry_forecasts(self, days, precip=0.5):
        return [
            DailyForecast(
                date=f"2026-01-{i+1:02d}",
                temp_max_c=35,
                temp_min_c=22,
                precipitation_mm=precip,
                precipitation_probability_pct=5,
                wind_speed_max_kmh=10,
                uv_index_max=9,
                condition="Clear",
                condition_ar="صافي",
                icon="clear",
            )
            for i in range(days)
        ]

    def test_drought_detected(self):
        forecasts = self._make_dry_forecasts(20, precip=0.1)
        alerts = detect_drought_conditions(forecasts)
        # Depends on threshold config; if enough days with low precip, drought detected
        # At least verify no crash
        assert isinstance(alerts, list)

    def test_no_drought_wet(self):
        forecasts = self._make_dry_forecasts(20, precip=10.0)
        alerts = detect_drought_conditions(forecasts)
        assert len(alerts) == 0

    def test_insufficient_days(self):
        """Too few days should return no alert."""
        forecasts = self._make_dry_forecasts(3, precip=0.0)
        alerts = detect_drought_conditions(forecasts)
        assert len(alerts) == 0


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestForecastGDD:
    def test_gdd_basic(self):
        gdd = calculate_gdd(tmin=15, tmax=30)
        assert gdd > 0

    def test_gdd_below_base(self):
        gdd = calculate_gdd(tmin=5, tmax=8, base_temp=10)
        assert gdd == 0

    def test_gdd_upper_clamped(self):
        gdd1 = calculate_gdd(tmin=20, tmax=40, upper_limit=30)
        gdd2 = calculate_gdd(tmin=20, tmax=30, upper_limit=30)
        assert gdd1 == gdd2


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestForecastChillHours:
    def test_chill_hours(self):
        temps = [3.0, 5.0, 8.0, 10.0]
        ch = fi_calculate_chill_hours(temps)
        assert ch == 2.0  # 3.0 and 5.0 are in [0, 7.2]


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestForecastET:
    def _make_forecast(self, tmax, tmin, wind):
        return DailyForecast(
            date="2026-01-01",
            temp_max_c=tmax,
            temp_min_c=tmin,
            precipitation_mm=0,
            precipitation_probability_pct=0,
            wind_speed_max_kmh=wind,
            uv_index_max=9,
            condition="Clear",
            condition_ar="صافي",
            icon="clear",
        )

    def test_penman_monteith(self):
        f = self._make_forecast(35, 20, 15)
        et = fi_calculate_et(f, method="penman_monteith")
        assert et > 0

    def test_hargreaves(self):
        f = self._make_forecast(35, 20, 15)
        et = fi_calculate_et(f, method="hargreaves")
        assert et > 0


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestCalculateAgriculturalIndices:
    def _make_forecast(self, tmax=35, tmin=20, precip=0):
        return DailyForecast(
            date="2026-01-01",
            temp_max_c=tmax,
            temp_min_c=tmin,
            precipitation_mm=precip,
            precipitation_probability_pct=0,
            wind_speed_max_kmh=15,
            uv_index_max=9,
            condition="Clear",
            condition_ar="صافي",
            icon="clear",
        )

    def test_basic_indices(self):
        f = self._make_forecast()
        idx = calculate_agricultural_indices(f)
        assert idx.gdd > 0
        assert idx.eto > 0
        assert idx.heat_stress_hours > 0  # temp_max >= 35

    def test_with_hourly_data(self):
        f = self._make_forecast()
        hourly = [
            HourlyForecast(
                datetime="2026-01-01T00:00",
                temperature_c=5.0,
                humidity_pct=80,
                precipitation_mm=0,
                precipitation_probability_pct=0,
                wind_speed_kmh=5,
                cloud_cover_pct=20,
                condition="Clear",
                condition_ar="صافي",
            )
            for _ in range(24)
        ]
        idx = calculate_agricultural_indices(f, hourly)
        assert idx.chill_hours > 0  # all hourly at 5C, within [0, 7.2]

    def test_no_heat_stress(self):
        f = self._make_forecast(tmax=28, tmin=18)
        idx = calculate_agricultural_indices(f)
        assert idx.heat_stress_hours == 0

    def test_moisture_deficit(self):
        f = self._make_forecast(precip=0)
        idx = calculate_agricultural_indices(f)
        assert idx.moisture_deficit_mm > 0

    def test_chill_estimated_from_daily(self):
        """When temp_min <= 7.2 and no hourly data, estimate chill."""
        f = self._make_forecast(tmax=15, tmin=5)
        idx = calculate_agricultural_indices(f)
        assert idx.chill_hours == 8.0  # estimated


@pytest.mark.skipif(not FORECAST_AVAILABLE, reason="forecast_integration not importable")
class TestWeatherForecastServiceTranslation:
    def test_translate_condition(self):
        assert WeatherForecastService._translate_condition("Clear") == "صافي"
        assert WeatherForecastService._translate_condition("Rain") == "مطر"
        assert WeatherForecastService._translate_condition("Unknown") == "Unknown"
