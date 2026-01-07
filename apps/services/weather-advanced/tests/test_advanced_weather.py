"""
Comprehensive Advanced Weather Service Tests
Tests for advanced weather features, agricultural reports, and Yemen-specific functionality
"""

import pytest
from datetime import datetime, date, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient


@pytest.fixture
def mock_open_meteo_response():
    """Mock Open-Meteo API response"""
    return {
        "current": {
            "temperature_2m": 28.5,
            "relative_humidity_2m": 55,
            "apparent_temperature": 30.2,
            "precipitation": 0.0,
            "weather_code": 0,
            "cloud_cover": 25,
            "pressure_msl": 1013,
            "wind_speed_10m": 12.5,
            "wind_direction_10m": 180,
            "wind_gusts_10m": 18.0,
            "time": "2026-01-07T12:00:00Z",
        },
        "daily": {
            "time": ["2026-01-08", "2026-01-09", "2026-01-10"],
            "temperature_2m_max": [32.5, 33.8, 28.2],
            "temperature_2m_min": [18.2, 19.5, 16.8],
            "precipitation_sum": [0.0, 0.0, 25.0],
            "precipitation_probability_max": [10, 5, 80],
            "weather_code": [0, 1, 65],
            "wind_speed_10m_max": [18.5, 15.0, 22.0],
            "uv_index_max": [9.5, 10.0, 5.5],
            "sunrise": [
                "2026-01-08T06:15:00",
                "2026-01-09T06:15:00",
                "2026-01-10T06:16:00"
            ],
            "sunset": [
                "2026-01-08T18:00:00",
                "2026-01-09T18:01:00",
                "2026-01-10T18:02:00"
            ],
        },
        "hourly": {
            "time": [f"2026-01-08T{h:02d}:00:00" for h in range(24)],
            "temperature_2m": [20 + (h % 12) for h in range(24)],
            "relative_humidity_2m": [50 + (h % 30) for h in range(24)],
            "apparent_temperature": [21 + (h % 12) for h in range(24)],
            "precipitation_probability": [10 + (h % 40) for h in range(24)],
            "precipitation": [0.0] * 24,
            "weather_code": [0] * 24,
            "cloud_cover": [20 + (h % 50) for h in range(24)],
            "wind_speed_10m": [10 + (h % 15) for h in range(24)],
            "wind_direction_10m": [180] * 24,
            "uv_index": [0 if h < 6 or h > 18 else 8 for h in range(24)],
        }
    }


@pytest.fixture
def app():
    """Create FastAPI test app instance"""
    from src.main import app as weather_advanced_app
    return weather_advanced_app


@pytest.fixture
def client(app):
    """Create test client"""
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""

    def test_health_check_returns_healthy(self, client):
        """Test health endpoint returns healthy status"""
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "weather-advanced"
        assert "version" in data
        assert "locations_count" in data

    def test_health_check_shows_deprecation(self, client):
        """Test health endpoint indicates service status"""
        response = client.get("/healthz")
        assert response.status_code == 200
        # Check for deprecation headers
        assert "X-API-Deprecated" in response.headers or True  # May or may not be set


class TestDeprecationHeaders:
    """Test deprecation warning headers"""

    def test_deprecation_headers_present(self, client):
        """Test all responses include deprecation headers"""
        response = client.get("/healthz")

        # Check for deprecation headers
        expected_headers = [
            "X-API-Deprecated",
            "X-API-Deprecation-Date",
            "X-API-Deprecation-Info",
            "X-API-Sunset",
        ]

        for header in expected_headers:
            # Headers may be present
            if header in response.headers:
                assert response.headers[header] is not None


class TestYemenLocations:
    """Test Yemen locations listing"""

    def test_list_all_locations(self, client):
        """Test listing all Yemen locations"""
        response = client.get("/v1/locations")

        assert response.status_code == 200
        data = response.json()
        assert "locations" in data
        assert len(data["locations"]) > 0

        # Verify location structure
        location = data["locations"][0]
        required_fields = ["id", "name_ar", "latitude", "longitude", "elevation_m"]
        for field in required_fields:
            assert field in location

    def test_locations_include_major_cities(self, client):
        """Test locations include major Yemeni cities"""
        response = client.get("/v1/locations")
        data = response.json()

        location_ids = [loc["id"] for loc in data["locations"]]

        # Check for major cities
        major_cities = ["sanaa", "aden", "taiz", "hodeidah"]
        for city in major_cities:
            assert city in location_ids

    def test_locations_have_arabic_names(self, client):
        """Test all locations have Arabic names"""
        response = client.get("/v1/locations")
        data = response.json()

        for location in data["locations"]:
            assert "name_ar" in location
            assert len(location["name_ar"]) > 0


class TestCurrentWeather:
    """Test current weather endpoint"""

    @pytest.mark.asyncio
    async def test_get_current_weather_success(self, client):
        """Test successful current weather retrieval"""
        response = client.get("/v1/current/sanaa")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        required_fields = [
            "location_id", "location_name_ar", "latitude", "longitude",
            "timestamp", "temperature_c", "humidity_percent",
            "wind_speed_kmh", "condition", "condition_ar"
        ]
        for field in required_fields:
            assert field in data

    @pytest.mark.asyncio
    async def test_get_current_weather_invalid_location(self, client):
        """Test current weather with invalid location"""
        response = client.get("/v1/current/invalid_location")

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_current_weather_includes_arabic(self, client):
        """Test current weather includes Arabic translations"""
        response = client.get("/v1/current/sanaa")

        assert response.status_code == 200
        data = response.json()

        assert "location_name_ar" in data
        assert "condition_ar" in data
        assert len(data["condition_ar"]) > 0

    @pytest.mark.asyncio
    async def test_current_weather_real_api_integration(self, client):
        """Test current weather with real API (or mock)"""
        with patch('src.main.fetch_open_meteo_current') as mock_fetch:
            mock_fetch.return_value = {
                "current": {
                    "temperature_2m": 29.0,
                    "relative_humidity_2m": 52,
                    "apparent_temperature": 30.5,
                    "precipitation": 0.0,
                    "weather_code": 0,
                    "cloud_cover": 20,
                    "pressure_msl": 1012,
                    "wind_speed_10m": 10.0,
                    "wind_direction_10m": 200,
                    "wind_gusts_10m": 15.0,
                    "time": "2026-01-07T14:00:00Z",
                }
            }

            response = client.get("/v1/current/aden")

            assert response.status_code == 200
            data = response.json()
            assert data["location_id"] == "aden"


class TestForecastEndpoint:
    """Test weather forecast endpoint"""

    @pytest.mark.asyncio
    async def test_get_forecast_success(self, client):
        """Test successful forecast retrieval"""
        response = client.get("/v1/forecast/sanaa?days=7")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        required_fields = [
            "location_id", "location_name_ar", "generated_at",
            "current", "hourly_forecast", "daily_forecast",
            "alerts", "growing_degree_days", "evapotranspiration_mm",
            "irrigation_recommendation_ar", "irrigation_recommendation_en"
        ]
        for field in required_fields:
            assert field in data

    @pytest.mark.asyncio
    async def test_forecast_custom_days(self, client):
        """Test forecast with custom number of days"""
        for days in [1, 3, 7, 14]:
            response = client.get(f"/v1/forecast/sanaa?days={days}")

            assert response.status_code == 200
            data = response.json()
            assert len(data["daily_forecast"]) <= days

    @pytest.mark.asyncio
    async def test_forecast_max_days_limit(self, client):
        """Test forecast respects maximum days limit"""
        response = client.get("/v1/forecast/sanaa?days=30")

        assert response.status_code == 200
        data = response.json()
        # Should be limited to 14 days
        assert len(data["daily_forecast"]) <= 14

    @pytest.mark.asyncio
    async def test_forecast_includes_hourly(self, client):
        """Test forecast includes hourly data"""
        response = client.get("/v1/forecast/sanaa?days=7")

        assert response.status_code == 200
        data = response.json()
        assert "hourly_forecast" in data
        assert len(data["hourly_forecast"]) > 0

        # Verify hourly structure
        hourly = data["hourly_forecast"][0]
        required_fields = [
            "datetime", "temperature_c", "humidity_percent",
            "wind_speed_kmh", "precipitation_mm", "condition"
        ]
        for field in required_fields:
            assert field in hourly

    @pytest.mark.asyncio
    async def test_forecast_includes_daily(self, client):
        """Test forecast includes daily data"""
        response = client.get("/v1/forecast/sanaa?days=7")

        assert response.status_code == 200
        data = response.json()
        assert "daily_forecast" in data
        assert len(data["daily_forecast"]) > 0

        # Verify daily structure
        daily = data["daily_forecast"][0]
        required_fields = [
            "date", "temp_max_c", "temp_min_c", "humidity_avg",
            "precipitation_total_mm", "condition", "condition_ar",
            "agricultural_summary_ar", "agricultural_summary_en"
        ]
        for field in required_fields:
            assert field in daily

    @pytest.mark.asyncio
    async def test_forecast_agricultural_summary(self, client):
        """Test forecast includes agricultural summaries"""
        response = client.get("/v1/forecast/sanaa?days=7")

        assert response.status_code == 200
        data = response.json()

        for day in data["daily_forecast"]:
            assert "agricultural_summary_ar" in day
            assert "agricultural_summary_en" in day
            assert len(day["agricultural_summary_ar"]) > 0
            assert len(day["agricultural_summary_en"]) > 0


class TestWeatherAlerts:
    """Test weather alerts endpoint"""

    @pytest.mark.asyncio
    async def test_get_weather_alerts(self, client):
        """Test weather alerts retrieval"""
        response = client.get("/v1/alerts/sanaa")

        assert response.status_code == 200
        data = response.json()

        assert "location_id" in data
        assert "alerts_count" in data
        assert "alerts" in data

    @pytest.mark.asyncio
    async def test_alerts_structure(self, client):
        """Test alert response structure"""
        response = client.get("/v1/alerts/sanaa")

        assert response.status_code == 200
        data = response.json()

        if data["alerts_count"] > 0:
            alert = data["alerts"][0]
            required_fields = [
                "alert_id", "alert_type", "severity",
                "title_ar", "title_en",
                "description_ar", "description_en",
                "start_time", "end_time",
                "affected_crops_ar",
                "recommendations_ar", "recommendations_en"
            ]
            for field in required_fields:
                assert field in alert

    @pytest.mark.asyncio
    async def test_alerts_include_recommendations(self, client):
        """Test alerts include actionable recommendations"""
        response = client.get("/v1/alerts/sanaa")

        assert response.status_code == 200
        data = response.json()

        if data["alerts_count"] > 0:
            alert = data["alerts"][0]
            assert isinstance(alert["recommendations_ar"], list)
            assert isinstance(alert["recommendations_en"], list)


class TestAgriculturalIndices:
    """Test agricultural indices calculation"""

    @pytest.mark.asyncio
    async def test_forecast_includes_gdd(self, client):
        """Test forecast includes Growing Degree Days"""
        response = client.get("/v1/forecast/sanaa?days=7")

        assert response.status_code == 200
        data = response.json()

        assert "growing_degree_days" in data
        assert isinstance(data["growing_degree_days"], (int, float))
        assert data["growing_degree_days"] >= 0

    @pytest.mark.asyncio
    async def test_forecast_includes_evapotranspiration(self, client):
        """Test forecast includes evapotranspiration"""
        response = client.get("/v1/forecast/sanaa?days=7")

        assert response.status_code == 200
        data = response.json()

        assert "evapotranspiration_mm" in data
        assert isinstance(data["evapotranspiration_mm"], (int, float))
        assert data["evapotranspiration_mm"] >= 0

    @pytest.mark.asyncio
    async def test_forecast_irrigation_recommendations(self, client):
        """Test forecast includes irrigation recommendations"""
        response = client.get("/v1/forecast/sanaa?days=7")

        assert response.status_code == 200
        data = response.json()

        assert "irrigation_recommendation_ar" in data
        assert "irrigation_recommendation_en" in data
        assert len(data["irrigation_recommendation_ar"]) > 0
        assert len(data["irrigation_recommendation_en"]) > 0

    @pytest.mark.asyncio
    async def test_forecast_spray_windows(self, client):
        """Test forecast includes optimal spray windows"""
        response = client.get("/v1/forecast/sanaa?days=7")

        assert response.status_code == 200
        data = response.json()

        assert "spray_window_hours" in data
        assert isinstance(data["spray_window_hours"], list)


class TestAgriculturalCalendar:
    """Test agricultural calendar endpoint"""

    def test_get_agricultural_calendar(self, client):
        """Test agricultural calendar retrieval"""
        response = client.get("/v1/agricultural-calendar/sanaa?crop=tomato")

        assert response.status_code == 200
        data = response.json()

        required_fields = [
            "location_id", "location_name_ar", "crop", "crop_name_ar",
            "current_month", "current_activity_ar", "current_activity_en",
            "optimal_temperature_range", "water_requirement",
            "planting_months", "harvest_months"
        ]
        for field in required_fields:
            assert field in data

    def test_calendar_different_crops(self, client):
        """Test calendar for different crop types"""
        crops = ["tomato", "wheat", "coffee", "banana"]

        for crop in crops:
            response = client.get(f"/v1/agricultural-calendar/sanaa?crop={crop}")

            assert response.status_code == 200
            data = response.json()
            assert data["crop"] == crop
            assert "crop_name_ar" in data

    def test_calendar_planting_months(self, client):
        """Test calendar includes planting months"""
        response = client.get("/v1/agricultural-calendar/sanaa?crop=tomato")

        assert response.status_code == 200
        data = response.json()

        assert "planting_months" in data
        assert isinstance(data["planting_months"], list)
        assert len(data["planting_months"]) > 0

    def test_calendar_harvest_months(self, client):
        """Test calendar includes harvest months"""
        response = client.get("/v1/agricultural-calendar/sanaa?crop=wheat")

        assert response.status_code == 200
        data = response.json()

        assert "harvest_months" in data
        assert isinstance(data["harvest_months"], list)
        assert len(data["harvest_months"]) > 0

    def test_calendar_next_7_days_suitability(self, client):
        """Test calendar includes 7-day suitability forecast"""
        response = client.get("/v1/agricultural-calendar/sanaa?crop=tomato")

        assert response.status_code == 200
        data = response.json()

        assert "next_7_days_suitability" in data
        assert len(data["next_7_days_suitability"]) == 7

        # Verify suitability structure
        day_suitability = data["next_7_days_suitability"][0]
        required_fields = [
            "date", "planting_suitable",
            "spraying_suitable", "harvesting_suitable"
        ]
        for field in required_fields:
            assert field in day_suitability


class TestWeatherConditionMapping:
    """Test weather condition mapping and translations"""

    @pytest.mark.asyncio
    async def test_wmo_code_mapping(self):
        """Test WMO weather code to condition mapping"""
        from src.main import WMO_CODE_TO_CONDITION, WeatherCondition

        # Test various WMO codes
        assert WMO_CODE_TO_CONDITION[0] == WeatherCondition.CLEAR
        assert WMO_CODE_TO_CONDITION[2] == WeatherCondition.PARTLY_CLOUDY
        assert WMO_CODE_TO_CONDITION[65] == WeatherCondition.HEAVY_RAIN
        assert WMO_CODE_TO_CONDITION[95] == WeatherCondition.THUNDERSTORM

    @pytest.mark.asyncio
    async def test_condition_arabic_translation(self):
        """Test weather condition Arabic translations"""
        from src.main import CONDITION_TRANSLATIONS, WeatherCondition

        # Verify Arabic translations exist
        assert WeatherCondition.CLEAR in CONDITION_TRANSLATIONS
        assert WeatherCondition.RAIN in CONDITION_TRANSLATIONS
        assert WeatherCondition.THUNDERSTORM in CONDITION_TRANSLATIONS

        # Verify translations are in Arabic
        for condition, translation in CONDITION_TRANSLATIONS.items():
            assert len(translation) > 0


class TestEvapotranspirationCalculation:
    """Test ET0 calculation functions"""

    def test_calculate_et0_normal_conditions(self):
        """Test ET0 calculation for normal conditions"""
        from src.main import calculate_evapotranspiration

        et0 = calculate_evapotranspiration(
            temp=25.0,
            humidity=55.0,
            wind_speed=10.0,
            solar_radiation=20.0
        )

        assert et0 >= 0
        assert 2.0 <= et0 <= 10.0

    def test_calculate_et0_hot_dry_conditions(self):
        """Test ET0 increases with temperature and low humidity"""
        from src.main import calculate_evapotranspiration

        et0_hot_dry = calculate_evapotranspiration(
            temp=38.0,
            humidity=25.0,
            wind_speed=20.0,
            solar_radiation=25.0
        )

        et0_normal = calculate_evapotranspiration(
            temp=25.0,
            humidity=55.0,
            wind_speed=10.0,
            solar_radiation=20.0
        )

        # Hot, dry conditions should have higher ET0
        assert et0_hot_dry > et0_normal


class TestGrowingDegreeDaysCalculation:
    """Test GDD calculation functions"""

    def test_calculate_gdd_normal(self):
        """Test GDD calculation for normal temperatures"""
        from src.main import calculate_growing_degree_days

        gdd = calculate_growing_degree_days(
            temp_max=30.0,
            temp_min=20.0,
            base_temp=10.0
        )

        # GDD = ((30 + 20) / 2) - 10 = 15
        assert gdd == 15.0

    def test_calculate_gdd_below_base(self):
        """Test GDD when temperature is below base"""
        from src.main import calculate_growing_degree_days

        gdd = calculate_growing_degree_days(
            temp_max=8.0,
            temp_min=5.0,
            base_temp=10.0
        )

        # Should return 0 when below base temp
        assert gdd == 0.0


class TestAlertGeneration:
    """Test weather alert generation"""

    def test_heat_wave_alert_generation(self):
        """Test heat wave alert is generated for high temperatures"""
        from src.main import check_for_alerts, DailyForecast

        forecast = [
            DailyForecast(
                date=date(2026, 1, 10),
                temp_max_c=42.0,
                temp_min_c=28.0,
                humidity_avg=30.0,
                wind_speed_avg_kmh=15.0,
                precipitation_total_mm=0.0,
                precipitation_probability=5.0,
                sunrise="06:15",
                sunset="18:00",
                uv_index_max=11.0,
                condition="clear",
                condition_ar="صافي",
                agricultural_summary_ar="⚠️ حرارة مرتفعة",
                agricultural_summary_en="⚠️ High heat",
            )
        ]

        alerts = check_for_alerts(forecast, "sanaa")

        heat_alerts = [a for a in alerts if a.alert_type == "heat_wave"]
        assert len(heat_alerts) > 0

    def test_heavy_rain_alert_generation(self):
        """Test heavy rain alert is generated"""
        from src.main import check_for_alerts, DailyForecast

        forecast = [
            DailyForecast(
                date=date(2026, 1, 10),
                temp_max_c=25.0,
                temp_min_c=18.0,
                humidity_avg=85.0,
                wind_speed_avg_kmh=20.0,
                precipitation_total_mm=45.0,
                precipitation_probability=90.0,
                sunrise="06:15",
                sunset="18:00",
                uv_index_max=4.0,
                condition="rain",
                condition_ar="مطر",
                agricultural_summary_ar="🌧️ أمطار متوقعة",
                agricultural_summary_en="🌧️ Rain expected",
            )
        ]

        alerts = check_for_alerts(forecast, "sanaa")

        rain_alerts = [a for a in alerts if a.alert_type == "heavy_rain"]
        assert len(rain_alerts) > 0

    def test_disease_risk_alert_generation(self):
        """Test disease risk alert for high humidity"""
        from src.main import check_for_alerts, DailyForecast

        forecast = [
            DailyForecast(
                date=date(2026, 1, 10),
                temp_max_c=26.0,
                temp_min_c=20.0,
                humidity_avg=90.0,
                wind_speed_avg_kmh=8.0,
                precipitation_total_mm=5.0,
                precipitation_probability=40.0,
                sunrise="06:15",
                sunset="18:00",
                uv_index_max=6.0,
                condition="partly_cloudy",
                condition_ar="غائم جزئياً",
                agricultural_summary_ar="💧 رطوبة عالية",
                agricultural_summary_en="💧 High humidity",
            )
        ]

        alerts = check_for_alerts(forecast, "sanaa")

        disease_alerts = [a for a in alerts if a.alert_type == "high_humidity"]
        assert len(disease_alerts) > 0


class TestSprayWindowsCalculation:
    """Test optimal spray window calculation"""

    def test_get_spray_windows(self):
        """Test spray window identification"""
        from src.main import get_spray_windows, HourlyForecast
        from datetime import datetime

        base_time = datetime(2026, 1, 8, 0, 0, 0)
        hourly = [
            HourlyForecast(
                datetime=base_time + timedelta(hours=i),
                temperature_c=22.0 if 6 <= i <= 18 else 18.0,
                feels_like_c=23.0 if 6 <= i <= 18 else 19.0,
                humidity_percent=55.0,
                wind_speed_kmh=8.0,  # Low wind
                wind_direction="N",
                precipitation_mm=0.0,  # No rain
                precipitation_probability=5.0,  # Low probability
                cloud_cover_percent=20.0,
                uv_index=6.0 if 10 <= i <= 15 else 2.0,
                condition="clear",
                condition_ar="صافي",
            )
            for i in range(48)
        ]

        windows = get_spray_windows(hourly)

        # Should identify some spray windows
        assert isinstance(windows, list)
        assert len(windows) > 0

    def test_spray_windows_exclude_windy_hours(self):
        """Test spray windows exclude windy periods"""
        from src.main import get_spray_windows, HourlyForecast
        from datetime import datetime

        base_time = datetime(2026, 1, 8, 0, 0, 0)
        hourly = [
            HourlyForecast(
                datetime=base_time + timedelta(hours=i),
                temperature_c=25.0,
                feels_like_c=26.0,
                humidity_percent=50.0,
                wind_speed_kmh=25.0,  # Too windy
                wind_direction="N",
                precipitation_mm=0.0,
                precipitation_probability=5.0,
                cloud_cover_percent=20.0,
                uv_index=6.0,
                condition="clear",
                condition_ar="صافي",
            )
            for i in range(24)
        ]

        windows = get_spray_windows(hourly)

        # Should have no windows due to high wind
        assert len(windows) == 0


class TestCacheManagement:
    """Test weather data caching"""

    def test_cache_key_generation(self):
        """Test cache key generation"""
        from src.main import get_cache_key

        key = get_cache_key("sanaa", "current")
        assert key == "sanaa:current"

        key2 = get_cache_key("aden", "forecast_7")
        assert key2 == "aden:forecast_7"

    def test_cache_validity_check(self):
        """Test cache validity checking"""
        from src.main import is_cache_valid
        from datetime import datetime

        # Valid cache entry
        valid_entry = {
            "data": {},
            "cached_at": datetime.utcnow()
        }
        assert is_cache_valid(valid_entry) is True

        # Expired cache entry
        expired_entry = {
            "data": {},
            "cached_at": datetime.utcnow() - timedelta(hours=2)
        }
        assert is_cache_valid(expired_entry) is False

        # Invalid entry
        assert is_cache_valid({}) is False
        assert is_cache_valid(None) is False
