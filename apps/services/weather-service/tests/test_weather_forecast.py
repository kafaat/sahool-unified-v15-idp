"""
Comprehensive Weather Forecast Tests
Tests for forecast calculations, alert generation, and agricultural indices
"""

import pytest
from datetime import date, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from src.forecast_integration import (
    WeatherForecastService,
    detect_frost_risk,
    detect_heat_wave,
    detect_heavy_rain,
    detect_drought_conditions,
    calculate_gdd,
    calculate_chill_hours,
    calculate_evapotranspiration,
    calculate_agricultural_indices,
    AlertSeverity,
    AlertCategory,
)
from src.providers.open_meteo import DailyForecast, HourlyForecast


@pytest.fixture
def sample_daily_forecast():
    """Sample daily forecast data for testing"""
    return [
        DailyForecast(
            date="2026-01-08",
            temp_max_c=32.5,
            temp_min_c=18.2,
            precipitation_mm=0.0,
            precipitation_probability_pct=10.0,
            wind_speed_max_kmh=18.5,
            uv_index_max=9.5,
            sunrise="06:15",
            sunset="18:00",
        ),
        DailyForecast(
            date="2026-01-09",
            temp_max_c=35.8,
            temp_min_c=20.5,
            precipitation_mm=0.0,
            precipitation_probability_pct=5.0,
            wind_speed_max_kmh=15.0,
            uv_index_max=10.0,
            sunrise="06:15",
            sunset="18:01",
        ),
        DailyForecast(
            date="2026-01-10",
            temp_max_c=28.2,
            temp_min_c=16.8,
            precipitation_mm=25.0,
            precipitation_probability_pct=80.0,
            wind_speed_max_kmh=22.0,
            uv_index_max=5.5,
            sunrise="06:16",
            sunset="18:02",
        ),
    ]


@pytest.fixture
def sample_hourly_forecast():
    """Sample hourly forecast data for testing"""
    base_time = datetime(2026, 1, 8, 0, 0, 0)
    return [
        HourlyForecast(
            datetime=(base_time + timedelta(hours=i)).isoformat(),
            temperature_c=20 + (i % 12),
            humidity_pct=50 + (i % 30),
            precipitation_mm=0.0 if i % 6 != 0 else 2.5,
            precipitation_probability_pct=10 + (i % 40),
            wind_speed_kmh=10 + (i % 15),
            cloud_cover_pct=20 + (i % 50),
        )
        for i in range(24)
    ]


class TestFrostRiskDetection:
    """Test frost risk detection"""

    def test_detect_frost_critical(self, sample_daily_forecast):
        """Test critical frost risk detection"""
        # Create forecast with critical frost conditions
        frost_forecast = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=8.0,
                temp_min_c=-2.0,  # Critical frost
                precipitation_mm=0.0,
                precipitation_probability_pct=0.0,
                wind_speed_max_kmh=5.0,
                uv_index_max=4.0,
                sunrise="06:20",
                sunset="17:55",
            )
        ]

        alerts = detect_frost_risk(frost_forecast)

        assert len(alerts) > 0
        assert alerts[0].category == AlertCategory.TEMPERATURE
        assert alerts[0].severity == AlertSeverity.CRITICAL
        assert "frost" in alerts[0].alert_type.lower()

    def test_detect_frost_high(self, sample_daily_forecast):
        """Test high frost risk detection"""
        frost_forecast = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=10.0,
                temp_min_c=1.5,  # High frost risk
                precipitation_mm=0.0,
                precipitation_probability_pct=0.0,
                wind_speed_max_kmh=5.0,
                uv_index_max=4.0,
                sunrise="06:20",
                sunset="17:55",
            )
        ]

        alerts = detect_frost_risk(frost_forecast)

        assert len(alerts) > 0
        assert alerts[0].severity == AlertSeverity.HIGH

    def test_no_frost_risk(self, sample_daily_forecast):
        """Test no frost risk in normal conditions"""
        alerts = detect_frost_risk(sample_daily_forecast)

        # Normal temperatures, no frost alerts
        frost_alerts = [a for a in alerts if "frost" in a.alert_type.lower()]
        assert len(frost_alerts) == 0

    def test_frost_recommendations(self):
        """Test frost alert includes recommendations"""
        frost_forecast = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=8.0,
                temp_min_c=0.5,
                precipitation_mm=0.0,
                precipitation_probability_pct=0.0,
                wind_speed_max_kmh=5.0,
                uv_index_max=4.0,
                sunrise="06:20",
                sunset="17:55",
            )
        ]

        alerts = detect_frost_risk(frost_forecast)

        assert len(alerts) > 0
        assert len(alerts[0].recommendations_ar) > 0
        assert len(alerts[0].recommendations_en) > 0


class TestHeatWaveDetection:
    """Test heat wave detection"""

    def test_detect_heat_wave_critical(self):
        """Test critical heat wave detection (3+ consecutive hot days)"""
        heat_forecast = [
            DailyForecast(
                date=f"2026-01-{10+i}",
                temp_max_c=42.0 + i,  # Critical heat
                temp_min_c=28.0,
                precipitation_mm=0.0,
                precipitation_probability_pct=0.0,
                wind_speed_max_kmh=15.0,
                uv_index_max=11.0,
                sunrise="06:15",
                sunset="18:00",
            )
            for i in range(5)  # 5 consecutive hot days
        ]

        alerts = detect_heat_wave(heat_forecast)

        assert len(alerts) > 0
        heat_wave_alerts = [a for a in alerts if a.alert_type == "heat_wave"]
        assert len(heat_wave_alerts) > 0
        assert heat_wave_alerts[0].severity == AlertSeverity.CRITICAL
        assert heat_wave_alerts[0].affected_days >= 3

    def test_detect_heat_wave_medium(self):
        """Test medium heat wave detection"""
        heat_forecast = [
            DailyForecast(
                date=f"2026-01-{10+i}",
                temp_max_c=38.0,  # Medium heat wave threshold
                temp_min_c=25.0,
                precipitation_mm=0.0,
                precipitation_probability_pct=0.0,
                wind_speed_max_kmh=15.0,
                uv_index_max=10.0,
                sunrise="06:15",
                sunset="18:00",
            )
            for i in range(4)  # 4 consecutive days
        ]

        alerts = detect_heat_wave(heat_forecast)

        assert len(alerts) > 0
        assert alerts[0].severity in [AlertSeverity.MEDIUM, AlertSeverity.HIGH]

    def test_no_heat_wave_insufficient_days(self):
        """Test no heat wave with insufficient consecutive days"""
        forecast = [
            DailyForecast(
                date="2026-01-10",
                temp_max_c=39.0,
                temp_min_c=25.0,
                precipitation_mm=0.0,
                precipitation_probability_pct=0.0,
                wind_speed_max_kmh=15.0,
                uv_index_max=10.0,
                sunrise="06:15",
                sunset="18:00",
            ),
            DailyForecast(
                date="2026-01-11",
                temp_max_c=39.0,
                temp_min_c=25.0,
                precipitation_mm=0.0,
                precipitation_probability_pct=0.0,
                wind_speed_max_kmh=15.0,
                uv_index_max=10.0,
                sunrise="06:15",
                sunset="18:00",
            ),
            # Only 2 days, not enough for heat wave
        ]

        alerts = detect_heat_wave(forecast)

        # Should not trigger heat wave (requires 3+ days)
        assert len(alerts) == 0

    def test_heat_wave_recommendations(self):
        """Test heat wave alert includes irrigation recommendations"""
        heat_forecast = [
            DailyForecast(
                date=f"2026-01-{10+i}",
                temp_max_c=40.0,
                temp_min_c=26.0,
                precipitation_mm=0.0,
                precipitation_probability_pct=0.0,
                wind_speed_max_kmh=15.0,
                uv_index_max=11.0,
                sunrise="06:15",
                sunset="18:00",
            )
            for i in range(3)
        ]

        alerts = detect_heat_wave(heat_forecast)

        assert len(alerts) > 0
        assert any("irrigation" in rec.lower() or "ري" in rec
                   for rec in alerts[0].recommendations_en)


class TestHeavyRainDetection:
    """Test heavy rain detection"""

    def test_detect_heavy_rain_critical(self):
        """Test critical heavy rain detection"""
        rain_forecast = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=25.0,
                temp_min_c=18.0,
                precipitation_mm=75.0,  # Critical level
                precipitation_probability_pct=95.0,
                wind_speed_max_kmh=30.0,
                uv_index_max=3.0,
                sunrise="06:20",
                sunset="17:55",
            )
        ]

        alerts = detect_heavy_rain(rain_forecast)

        assert len(alerts) > 0
        assert alerts[0].category == AlertCategory.PRECIPITATION
        assert alerts[0].severity == AlertSeverity.CRITICAL

    def test_detect_heavy_rain_medium(self):
        """Test medium heavy rain detection"""
        rain_forecast = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=25.0,
                temp_min_c=18.0,
                precipitation_mm=20.0,  # Medium level
                precipitation_probability_pct=70.0,
                wind_speed_max_kmh=25.0,
                uv_index_max=4.0,
                sunrise="06:20",
                sunset="17:55",
            )
        ]

        alerts = detect_heavy_rain(rain_forecast)

        assert len(alerts) > 0
        assert alerts[0].severity == AlertSeverity.MEDIUM

    def test_no_heavy_rain(self, sample_daily_forecast):
        """Test no heavy rain alerts for light precipitation"""
        light_rain = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=25.0,
                temp_min_c=18.0,
                precipitation_mm=5.0,  # Light rain
                precipitation_probability_pct=40.0,
                wind_speed_max_kmh=15.0,
                uv_index_max=6.0,
                sunrise="06:20",
                sunset="17:55",
            )
        ]

        alerts = detect_heavy_rain(light_rain)

        # Should not trigger heavy rain alert
        assert len(alerts) == 0

    def test_heavy_rain_confidence(self):
        """Test heavy rain alert confidence based on probability"""
        rain_forecast = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=25.0,
                temp_min_c=18.0,
                precipitation_mm=35.0,
                precipitation_probability_pct=85.0,
                wind_speed_max_kmh=25.0,
                uv_index_max=3.0,
                sunrise="06:20",
                sunset="17:55",
            )
        ]

        alerts = detect_heavy_rain(rain_forecast)

        assert len(alerts) > 0
        # Confidence should be based on precipitation probability
        assert alerts[0].confidence >= 0.8


class TestDroughtDetection:
    """Test drought conditions detection"""

    def test_detect_drought_critical(self):
        """Test critical drought detection"""
        # Create 14 days of minimal precipitation
        drought_forecast = [
            DailyForecast(
                date=f"2026-01-{10+i}",
                temp_max_c=35.0,
                temp_min_c=22.0,
                precipitation_mm=0.0,  # No rain
                precipitation_probability_pct=5.0,
                wind_speed_max_kmh=20.0,
                uv_index_max=10.0,
                sunrise="06:15",
                sunset="18:00",
            )
            for i in range(14)
        ]

        alerts = detect_drought_conditions(drought_forecast)

        assert len(alerts) > 0
        assert alerts[0].category == AlertCategory.DROUGHT
        assert alerts[0].severity in [AlertSeverity.CRITICAL, AlertSeverity.HIGH]

    def test_detect_drought_with_history(self):
        """Test drought detection with historical data"""
        # Historical dry period
        history = [
            DailyForecast(
                date=f"2025-12-{20+i}",
                temp_max_c=32.0,
                temp_min_c=20.0,
                precipitation_mm=0.5,
                precipitation_probability_pct=10.0,
                wind_speed_max_kmh=18.0,
                uv_index_max=9.0,
                sunrise="06:20",
                sunset="17:50",
            )
            for i in range(7)
        ]

        # Current forecast also dry
        forecast = [
            DailyForecast(
                date=f"2026-01-{10+i}",
                temp_max_c=34.0,
                temp_min_c=21.0,
                precipitation_mm=0.0,
                precipitation_probability_pct=5.0,
                wind_speed_max_kmh=20.0,
                uv_index_max=10.0,
                sunrise="06:15",
                sunset="18:00",
            )
            for i in range(7)
        ]

        alerts = detect_drought_conditions(forecast, history)

        assert len(alerts) > 0

    def test_no_drought_sufficient_rain(self):
        """Test no drought with sufficient rainfall"""
        forecast = [
            DailyForecast(
                date=f"2026-01-{10+i}",
                temp_max_c=30.0,
                temp_min_c=20.0,
                precipitation_mm=15.0 if i % 3 == 0 else 0.0,  # Regular rain
                precipitation_probability_pct=60.0 if i % 3 == 0 else 20.0,
                wind_speed_max_kmh=15.0,
                uv_index_max=8.0,
                sunrise="06:15",
                sunset="18:00",
            )
            for i in range(14)
        ]

        alerts = detect_drought_conditions(forecast)

        # Should not trigger drought with sufficient rainfall
        assert len(alerts) == 0


class TestGrowingDegreeDays:
    """Test Growing Degree Days calculation"""

    def test_gdd_normal_temperatures(self):
        """Test GDD calculation with normal temperatures"""
        gdd = calculate_gdd(tmin=15.0, tmax=25.0, base_temp=10.0)

        # GDD = ((25 + 15) / 2) - 10 = 20 - 10 = 10
        assert gdd == 10.0

    def test_gdd_below_base_temp(self):
        """Test GDD when temperature is below base"""
        gdd = calculate_gdd(tmin=5.0, tmax=8.0, base_temp=10.0)

        # Temperatures clamped to base temp, GDD = 0
        assert gdd == 0.0

    def test_gdd_above_upper_limit(self):
        """Test GDD with temperature above upper limit"""
        gdd = calculate_gdd(tmin=25.0, tmax=35.0, base_temp=10.0, upper_limit=30.0)

        # Tmax clamped to 30, GDD = ((30 + 25) / 2) - 10 = 17.5
        assert gdd == 17.5

    def test_gdd_custom_base_temp(self):
        """Test GDD with custom base temperature"""
        # Different crops have different base temperatures
        gdd_wheat = calculate_gdd(tmin=12.0, tmax=22.0, base_temp=0.0)  # Wheat
        gdd_corn = calculate_gdd(tmin=12.0, tmax=22.0, base_temp=10.0)  # Corn

        assert gdd_wheat > gdd_corn


class TestChillHours:
    """Test chill hours calculation"""

    def test_chill_hours_normal(self):
        """Test chill hours calculation"""
        # Simulate hourly temperatures
        hourly_temps = [6.0, 5.5, 5.0, 4.5, 4.0, 3.5, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]

        chill_hours = calculate_chill_hours(hourly_temps, threshold=7.2)

        # Count temps between 0 and 7.2
        expected = sum(1 for t in hourly_temps if 0 <= t <= 7.2)
        assert chill_hours == expected

    def test_chill_hours_no_chill(self):
        """Test chill hours with warm temperatures"""
        hourly_temps = [15.0, 16.0, 17.0, 18.0, 20.0, 22.0]

        chill_hours = calculate_chill_hours(hourly_temps)

        assert chill_hours == 0.0

    def test_chill_hours_all_chill(self):
        """Test chill hours with all qualifying temperatures"""
        hourly_temps = [5.0] * 24  # All hours at 5°C

        chill_hours = calculate_chill_hours(hourly_temps)

        assert chill_hours == 24.0


class TestEvapotranspiration:
    """Test evapotranspiration calculation"""

    def test_eto_hargreaves_method(self):
        """Test ET0 using Hargreaves method"""
        forecast = DailyForecast(
            date="2026-01-15",
            temp_max_c=32.0,
            temp_min_c=18.0,
            precipitation_mm=0.0,
            precipitation_probability_pct=0.0,
            wind_speed_max_kmh=15.0,
            uv_index_max=9.0,
            sunrise="06:15",
            sunset="18:00",
        )

        eto = calculate_evapotranspiration(forecast, method="hargreaves")

        assert eto > 0
        # ET0 should be reasonable for these conditions
        assert 2.0 <= eto <= 10.0

    def test_eto_penman_monteith_method(self):
        """Test ET0 using Penman-Monteith method"""
        forecast = DailyForecast(
            date="2026-01-15",
            temp_max_c=35.0,
            temp_min_c=22.0,
            precipitation_mm=0.0,
            precipitation_probability_pct=0.0,
            wind_speed_max_kmh=20.0,
            uv_index_max=10.0,
            sunrise="06:15",
            sunset="18:00",
        )

        eto = calculate_evapotranspiration(forecast, method="penman_monteith")

        assert eto > 0
        assert 2.0 <= eto <= 12.0

    def test_eto_hot_windy_conditions(self):
        """Test ET0 increases with temperature and wind"""
        forecast_calm = DailyForecast(
            date="2026-01-15",
            temp_max_c=30.0,
            temp_min_c=20.0,
            precipitation_mm=0.0,
            precipitation_probability_pct=0.0,
            wind_speed_max_kmh=5.0,
            uv_index_max=8.0,
            sunrise="06:15",
            sunset="18:00",
        )

        forecast_windy_hot = DailyForecast(
            date="2026-01-15",
            temp_max_c=38.0,
            temp_min_c=25.0,
            precipitation_mm=0.0,
            precipitation_probability_pct=0.0,
            wind_speed_max_kmh=25.0,
            uv_index_max=11.0,
            sunrise="06:15",
            sunset="18:00",
        )

        eto_calm = calculate_evapotranspiration(forecast_calm)
        eto_windy_hot = calculate_evapotranspiration(forecast_windy_hot)

        # Hot, windy conditions should have higher ET0
        assert eto_windy_hot > eto_calm


class TestAgriculturalIndices:
    """Test agricultural indices calculation"""

    def test_calculate_indices_complete(self):
        """Test complete agricultural indices calculation"""
        daily = DailyForecast(
            date="2026-01-15",
            temp_max_c=32.0,
            temp_min_c=18.0,
            precipitation_mm=5.0,
            precipitation_probability_pct=40.0,
            wind_speed_max_kmh=15.0,
            uv_index_max=9.0,
            sunrise="06:15",
            sunset="18:00",
        )

        hourly = [
            HourlyForecast(
                datetime=f"2026-01-15T{h:02d}:00:00",
                temperature_c=20 + (h % 12),
                humidity_pct=50,
                precipitation_mm=0.0,
                precipitation_probability_pct=10,
                wind_speed_kmh=12,
                cloud_cover_pct=30,
            )
            for h in range(24)
        ]

        indices = calculate_agricultural_indices(daily, hourly)

        assert indices.date == "2026-01-15"
        assert indices.gdd >= 0
        assert indices.eto >= 0
        assert indices.moisture_deficit_mm >= 0

    def test_indices_heat_stress_hours(self):
        """Test heat stress hours calculation"""
        daily = DailyForecast(
            date="2026-01-15",
            temp_max_c=42.0,  # Very hot
            temp_min_c=28.0,
            precipitation_mm=0.0,
            precipitation_probability_pct=0.0,
            wind_speed_max_kmh=20.0,
            uv_index_max=11.0,
            sunrise="06:15",
            sunset="18:00",
        )

        # Hourly temps with several hours above 35°C
        hourly = [
            HourlyForecast(
                datetime=f"2026-01-15T{h:02d}:00:00",
                temperature_c=36.0 if 10 <= h <= 16 else 30.0,
                humidity_pct=40,
                precipitation_mm=0.0,
                precipitation_probability_pct=0,
                wind_speed_kmh=15,
                cloud_cover_pct=10,
            )
            for h in range(24)
        ]

        indices = calculate_agricultural_indices(daily, hourly)

        # Should detect heat stress hours
        assert indices.heat_stress_hours > 0

    def test_indices_moisture_deficit(self):
        """Test moisture deficit calculation"""
        daily = DailyForecast(
            date="2026-01-15",
            temp_max_c=35.0,
            temp_min_c=22.0,
            precipitation_mm=2.0,  # Light rain
            precipitation_probability_pct=30.0,
            wind_speed_max_kmh=18.0,
            uv_index_max=10.0,
            sunrise="06:15",
            sunset="18:00",
        )

        indices = calculate_agricultural_indices(daily)

        # ET0 should be greater than precipitation, creating deficit
        assert indices.moisture_deficit_mm >= 0
        assert indices.eto > indices.moisture_deficit_mm


class TestWeatherForecastService:
    """Test WeatherForecastService class"""

    @pytest.mark.asyncio
    async def test_service_initialization(self):
        """Test service initializes with providers"""
        with patch('src.forecast_integration.get_config') as mock_config:
            # Mock configuration
            mock_cfg = MagicMock()
            mock_cfg.providers = {
                "open_meteo": MagicMock(enabled=True),
            }
            mock_cfg.forecast_max_days = 16
            mock_config.return_value = mock_cfg

            service = WeatherForecastService()

            assert service.providers is not None
            assert len(service.providers) >= 0

    @pytest.mark.asyncio
    async def test_fetch_forecast_success(self):
        """Test successful forecast fetching"""
        with patch('src.forecast_integration.get_config') as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.providers = {
                "open_meteo": MagicMock(enabled=True, priority=MagicMock(value=1)),
            }
            mock_cfg.forecast_max_days = 16
            mock_config.return_value = mock_cfg

            service = WeatherForecastService()

            # Mock provider
            mock_provider = AsyncMock()
            mock_provider.is_configured = True
            mock_provider.get_daily_forecast = AsyncMock(return_value=[
                DailyForecast(
                    date="2026-01-15",
                    temp_max_c=32.0,
                    temp_min_c=18.0,
                    precipitation_mm=0.0,
                    precipitation_probability_pct=10.0,
                    wind_speed_max_kmh=15.0,
                    uv_index_max=9.0,
                    sunrise="06:15",
                    sunset="18:00",
                )
            ])
            mock_provider.get_hourly_forecast = AsyncMock(return_value=[])

            service.providers = {"open_meteo": mock_provider}

            daily, hourly, provider = await service.fetch_forecast(15.35, 44.20, 7)

            assert daily is not None
            assert len(daily) > 0
            assert provider == "open_meteo"

    @pytest.mark.asyncio
    async def test_fetch_forecast_provider_fallback(self):
        """Test provider fallback on failure"""
        with patch('src.forecast_integration.get_config') as mock_config:
            mock_cfg = MagicMock()
            mock_cfg.providers = {}
            mock_cfg.forecast_max_days = 16
            mock_config.return_value = mock_cfg

            service = WeatherForecastService()

            # Mock multiple providers, first fails
            mock_provider1 = AsyncMock()
            mock_provider1.is_configured = True
            mock_provider1.get_daily_forecast = AsyncMock(
                side_effect=Exception("API Error")
            )

            mock_provider2 = AsyncMock()
            mock_provider2.is_configured = True
            mock_provider2.get_daily_forecast = AsyncMock(return_value=[])
            mock_provider2.get_hourly_forecast = AsyncMock(return_value=[])

            service.providers = {
                "provider1": mock_provider1,
                "provider2": mock_provider2,
            }

            daily, hourly, provider = await service.fetch_forecast(15.35, 44.20, 7)

            # Should fallback to provider2
            assert provider == "provider2"

    def test_aggregate_forecasts_single_source(self):
        """Test forecast aggregation with single source"""
        service = WeatherForecastService()

        forecasts = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=32.0,
                temp_min_c=18.0,
                precipitation_mm=0.0,
                precipitation_probability_pct=10.0,
                wind_speed_max_kmh=15.0,
                uv_index_max=9.0,
                sunrise="06:15",
                sunset="18:00",
            )
        ]

        sources = [("provider1", forecasts)]
        aggregated = service.aggregate_forecasts(sources)

        assert len(aggregated) == 1
        assert aggregated[0].temp_max_c == 32.0

    def test_aggregate_forecasts_multiple_sources(self):
        """Test forecast aggregation with multiple sources"""
        service = WeatherForecastService()

        source1 = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=32.0,
                temp_min_c=18.0,
                precipitation_mm=0.0,
                precipitation_probability_pct=10.0,
                wind_speed_max_kmh=15.0,
                uv_index_max=9.0,
                sunrise="06:15",
                sunset="18:00",
            )
        ]

        source2 = [
            DailyForecast(
                date="2026-01-15",
                temp_max_c=34.0,
                temp_min_c=20.0,
                precipitation_mm=0.0,
                precipitation_probability_pct=15.0,
                wind_speed_max_kmh=18.0,
                uv_index_max=10.0,
                sunrise="06:15",
                sunset="18:00",
            )
        ]

        sources = [("provider1", source1), ("provider2", source2)]
        aggregated = service.aggregate_forecasts(sources)

        assert len(aggregated) == 1
        # Should average the values
        assert 32.0 <= aggregated[0].temp_max_c <= 34.0
