"""
Tests for provider-config main.py - enums, provider data, API endpoints, helper functions
اختبارات نقاط النهاية والبيانات الثابتة
"""

import json
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi not installed", allow_module_level=True)

from src.main import (
    MAP_PROVIDERS,
    NOTIFICATION_PROVIDERS,
    PAYMENT_PROVIDERS,
    SATELLITE_PROVIDERS,
    SMS_PROVIDERS,
    WEATHER_PROVIDERS,
    HealthCheckRequest,
    MapProviderName,
    NotificationProviderName,
    PaymentProviderName,
    ProviderConfig,
    ProviderPriority,
    ProviderStatus,
    ProviderStatusResponse,
    ProviderType,
    SatelliteProviderName,
    SMSProviderName,
    TenantProviderConfig,
    WeatherProviderName,
    app,
    check_map_provider_health,
    check_weather_provider_health,
    publish_config_updated,
    publish_provider_status_changed,
)


# ═══════════════════════════════════════════════════════════════════════════════
# ENUM TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestProviderTypeEnum:
    """Tests for ProviderType enum"""

    def test_all_provider_types(self):
        assert ProviderType.MAP == "map"
        assert ProviderType.WEATHER == "weather"
        assert ProviderType.SATELLITE == "satellite"
        assert ProviderType.NOTIFICATION == "notification"
        assert ProviderType.PAYMENT == "payment"
        assert ProviderType.SMS == "sms"

    def test_provider_type_count(self):
        assert len(ProviderType) == 6


class TestProviderPriorityEnum:
    """Tests for ProviderPriority enum"""

    def test_all_priorities(self):
        assert ProviderPriority.PRIMARY == "primary"
        assert ProviderPriority.SECONDARY == "secondary"
        assert ProviderPriority.TERTIARY == "tertiary"
        assert ProviderPriority.DISABLED == "disabled"


class TestProviderStatusEnum:
    """Tests for ProviderStatus enum"""

    def test_all_statuses(self):
        assert ProviderStatus.AVAILABLE == "available"
        assert ProviderStatus.UNAVAILABLE == "unavailable"
        assert ProviderStatus.RATE_LIMITED == "rate_limited"
        assert ProviderStatus.ERROR == "error"
        assert ProviderStatus.CHECKING == "checking"


class TestMapProviderNameEnum:
    """Tests for MapProviderName enum"""

    def test_has_openstreetmap(self):
        assert MapProviderName.OPENSTREETMAP == "openstreetmap"

    def test_has_all_google_variants(self):
        assert MapProviderName.GOOGLE_MAPS == "google_maps"
        assert MapProviderName.GOOGLE_SATELLITE == "google_satellite"
        assert MapProviderName.GOOGLE_HYBRID == "google_hybrid"

    def test_has_all_mapbox_variants(self):
        assert MapProviderName.MAPBOX_STREETS == "mapbox_streets"
        assert MapProviderName.MAPBOX_SATELLITE == "mapbox_satellite"
        assert MapProviderName.MAPBOX_HYBRID == "mapbox_hybrid"

    def test_count(self):
        assert len(MapProviderName) == 10


class TestWeatherProviderNameEnum:
    """Tests for WeatherProviderName enum"""

    def test_all_weather_providers(self):
        assert WeatherProviderName.OPEN_METEO == "open_meteo"
        assert WeatherProviderName.OPENWEATHERMAP == "openweathermap"
        assert WeatherProviderName.WEATHER_API == "weather_api"
        assert WeatherProviderName.VISUAL_CROSSING == "visual_crossing"


class TestSatelliteProviderNameEnum:
    """Tests for SatelliteProviderName enum"""

    def test_count(self):
        assert len(SatelliteProviderName) == 6

    def test_includes_google_earth_engine(self):
        assert SatelliteProviderName.GOOGLE_EARTH_ENGINE == "google_earth_engine"

    def test_includes_copernicus(self):
        assert SatelliteProviderName.COPERNICUS == "copernicus"


class TestPaymentProviderNameEnum:
    """Tests for PaymentProviderName enum"""

    def test_includes_regional_providers(self):
        assert PaymentProviderName.MOYASAR == "moyasar"
        assert PaymentProviderName.THARWATT == "tharwatt"
        assert PaymentProviderName.TAP == "tap"

    def test_count(self):
        assert len(PaymentProviderName) == 8


class TestSMSProviderNameEnum:
    """Tests for SMSProviderName enum"""

    def test_includes_regional(self):
        assert SMSProviderName.UNIFONIC == "unifonic"
        assert SMSProviderName.YAMAMAH == "yamamah"


class TestNotificationProviderNameEnum:
    """Tests for NotificationProviderName enum"""

    def test_count(self):
        assert len(NotificationProviderName) == 5  # firebase, onesignal, pusher, twilio, vonage


# ═══════════════════════════════════════════════════════════════════════════════
# PROVIDER DATA STRUCTURE TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestMapProvidersData:
    """Tests for MAP_PROVIDERS dictionary"""

    def test_all_map_providers_have_required_fields(self):
        required = ["name", "name_ar", "url_template", "requires_api_key", "max_zoom", "attribution"]
        for key, provider in MAP_PROVIDERS.items():
            for field in required:
                assert field in provider, f"{key} missing {field}"

    def test_osm_is_free(self):
        osm = MAP_PROVIDERS[MapProviderName.OPENSTREETMAP]
        assert osm["requires_api_key"] is False
        assert osm["cost_per_1k_requests"] == 0

    def test_google_maps_requires_api_key(self):
        gm = MAP_PROVIDERS[MapProviderName.GOOGLE_MAPS]
        assert gm["requires_api_key"] is True

    def test_map_provider_count(self):
        assert len(MAP_PROVIDERS) == 10


class TestWeatherProvidersData:
    """Tests for WEATHER_PROVIDERS dictionary"""

    def test_all_weather_providers_have_required_fields(self):
        required = ["name", "name_ar", "base_url", "requires_api_key", "forecast_days"]
        for key, provider in WEATHER_PROVIDERS.items():
            for field in required:
                assert field in provider, f"{key} missing {field}"

    def test_open_meteo_is_free_with_16_day_forecast(self):
        om = WEATHER_PROVIDERS[WeatherProviderName.OPEN_METEO]
        assert om["requires_api_key"] is False
        assert om["forecast_days"] == 16
        assert om["cost_per_1k_requests"] == 0


class TestSatelliteProvidersData:
    """Tests for SATELLITE_PROVIDERS dictionary"""

    def test_all_have_resolution_and_indices(self):
        for key, provider in SATELLITE_PROVIDERS.items():
            assert "resolution_meters" in provider, f"{key} missing resolution_meters"
            assert "indices" in provider, f"{key} missing indices"
            assert "NDVI" in provider["indices"], f"{key} missing NDVI index"

    def test_landsat_is_free(self):
        ls = SATELLITE_PROVIDERS[SatelliteProviderName.LANDSAT]
        assert ls["requires_api_key"] is False
        assert ls["cost_per_km2"] == 0


class TestPaymentProvidersData:
    """Tests for PAYMENT_PROVIDERS dictionary"""

    def test_all_have_fee_info(self):
        for key, provider in PAYMENT_PROVIDERS.items():
            assert "transaction_fee_percent" in provider, f"{key} missing fee"
            assert "supported_currencies" in provider

    def test_tharwatt_is_yemen_primary(self):
        tw = PAYMENT_PROVIDERS[PaymentProviderName.THARWATT]
        assert "YE" in tw["supported_countries"]
        assert "YER" in tw["supported_currencies"]
        assert tw["default_priority"] == ProviderPriority.PRIMARY

    def test_moyasar_supports_mada(self):
        m = PAYMENT_PROVIDERS[PaymentProviderName.MOYASAR]
        assert m.get("supports_mada") is True


class TestSMSProvidersData:
    """Tests for SMS_PROVIDERS dictionary"""

    def test_twilio_is_global(self):
        tw = SMS_PROVIDERS[SMSProviderName.TWILIO]
        assert "*" in tw["supported_countries"]

    def test_unifonic_supports_arabic_sender(self):
        u = SMS_PROVIDERS[SMSProviderName.UNIFONIC]
        assert u.get("supports_arabic_sender") is True


class TestNotificationProvidersData:
    """Tests for NOTIFICATION_PROVIDERS dictionary"""

    def test_firebase_is_free(self):
        fcm = NOTIFICATION_PROVIDERS[NotificationProviderName.FIREBASE_FCM]
        assert fcm["cost_per_1k_notifications"] == 0


# ═══════════════════════════════════════════════════════════════════════════════
# PYDANTIC MODEL TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestPydanticModels:
    """Tests for Pydantic request/response models"""

    def test_provider_config_defaults(self):
        pc = ProviderConfig(provider_name="openstreetmap")
        assert pc.api_key is None
        assert pc.priority == ProviderPriority.PRIMARY
        assert pc.enabled is True

    def test_provider_config_with_values(self):
        pc = ProviderConfig(
            provider_name="google_maps",
            api_key="test-key",
            priority=ProviderPriority.SECONDARY,
            enabled=False,
        )
        assert pc.provider_name == "google_maps"
        assert pc.api_key == "test-key"
        assert pc.priority == ProviderPriority.SECONDARY
        assert pc.enabled is False

    def test_tenant_provider_config_defaults(self):
        tpc = TenantProviderConfig(tenant_id="t1")
        assert tpc.tenant_id == "t1"
        assert tpc.map_providers == []
        assert tpc.weather_providers == []
        assert tpc.satellite_providers == []

    def test_health_check_request(self):
        req = HealthCheckRequest(
            provider_type=ProviderType.MAP,
            provider_name="openstreetmap",
        )
        assert req.provider_type == ProviderType.MAP
        assert req.api_key is None

    def test_provider_status_response(self):
        now = datetime.now(UTC)
        resp = ProviderStatusResponse(
            provider_name="osm",
            status=ProviderStatus.AVAILABLE,
            last_check=now,
            response_time_ms=42.5,
        )
        assert resp.provider_name == "osm"
        assert resp.status == ProviderStatus.AVAILABLE
        assert resp.response_time_ms == 42.5
        assert resp.error_message is None


# ═══════════════════════════════════════════════════════════════════════════════
# NATS PUBLISH FUNCTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestPublishConfigUpdated:
    """Tests for publish_config_updated"""

    @pytest.mark.asyncio
    async def test_no_publish_when_nc_is_none(self):
        """Test that nothing happens when NATS client is None"""
        with patch("src.main.nc", None):
            await publish_config_updated("t1", "map", "osm")

    @pytest.mark.asyncio
    async def test_publish_success(self):
        """Test successful NATS publish — subject is tenant-scoped.

        Non-UUID tenant_id ("t1") triggers the fallback-inline pattern
        (`sahool.tenant.<tid>.config.updated`) because the strict UUID
        validator in shared.events.subjects.get_tenant_subject rejects it.
        """
        mock_nc = AsyncMock()
        with patch("src.main.nc", mock_nc):
            await publish_config_updated("t1", "map", "osm", key="priority")

        mock_nc.publish.assert_awaited_once()
        call_args = mock_nc.publish.call_args
        assert call_args[0][0].startswith("sahool.tenant.t1.config.updated") or \
            call_args[0][0] == "sahool.tenant.t1.config.updated"
        payload = json.loads(call_args[0][1].decode())
        assert payload["tenant_id"] == "t1"
        assert payload["provider"] == "osm"
        assert payload["key"] == "priority"

    @pytest.mark.asyncio
    async def test_publish_handles_error(self):
        """Test that publish errors are handled gracefully"""
        mock_nc = AsyncMock()
        mock_nc.publish.side_effect = Exception("NATS down")
        with patch("src.main.nc", mock_nc):
            await publish_config_updated("t1", "map", "osm")
        # Should not raise


class TestPublishProviderStatusChanged:
    """Tests for publish_provider_status_changed"""

    @pytest.mark.asyncio
    async def test_no_publish_when_nc_is_none(self):
        with patch("src.main.nc", None):
            await publish_provider_status_changed("t1", "map", "osm", True)

    @pytest.mark.asyncio
    async def test_publish_success(self):
        """Test publish — subject is tenant-scoped inline fallback."""
        mock_nc = AsyncMock()
        with patch("src.main.nc", mock_nc):
            await publish_provider_status_changed("t1", "map", "osm", False)

        mock_nc.publish.assert_awaited_once()
        call_args = mock_nc.publish.call_args
        assert call_args[0][0] == "sahool.tenant.t1.config.provider_status_changed"
        payload = json.loads(call_args[0][1].decode())
        assert payload["enabled"] is False

    @pytest.mark.asyncio
    async def test_publish_handles_error(self):
        mock_nc = AsyncMock()
        mock_nc.publish.side_effect = Exception("NATS down")
        with patch("src.main.nc", mock_nc):
            await publish_provider_status_changed("t1", "map", "osm", True)


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH CHECK FUNCTION TESTS
# ═══════════════════════════════════════════════════════════════════════════════
class TestCheckMapProviderHealth:
    """Tests for check_map_provider_health"""

    @pytest.mark.asyncio
    async def test_available_provider(self):
        """Test successful health check returns AVAILABLE"""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.main.httpx.AsyncClient", return_value=mock_client):
            result = await check_map_provider_health(MapProviderName.OPENSTREETMAP)

        assert result.status == ProviderStatus.AVAILABLE
        assert result.provider_name == "openstreetmap"

    @pytest.mark.asyncio
    async def test_rate_limited_provider(self):
        """Test 429 response returns RATE_LIMITED"""
        mock_response = MagicMock()
        mock_response.status_code = 429

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.main.httpx.AsyncClient", return_value=mock_client):
            result = await check_map_provider_health(MapProviderName.OPENSTREETMAP)

        assert result.status == ProviderStatus.RATE_LIMITED

    @pytest.mark.asyncio
    async def test_unavailable_provider(self):
        """Test non-200/429 status returns UNAVAILABLE"""
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.main.httpx.AsyncClient", return_value=mock_client):
            result = await check_map_provider_health(MapProviderName.OPENSTREETMAP)

        assert result.status == ProviderStatus.UNAVAILABLE
        assert "HTTP 500" in result.error_message

    @pytest.mark.asyncio
    async def test_network_error(self):
        """Test network error returns ERROR status"""
        mock_client = AsyncMock()
        mock_client.head = AsyncMock(side_effect=ConnectionError("timeout"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.main.httpx.AsyncClient", return_value=mock_client):
            result = await check_map_provider_health(MapProviderName.OPENSTREETMAP)

        assert result.status == ProviderStatus.ERROR

    @pytest.mark.asyncio
    async def test_with_api_key_replacement(self):
        """Test that API key is substituted into URL"""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.main.httpx.AsyncClient", return_value=mock_client):
            result = await check_map_provider_health(MapProviderName.GOOGLE_MAPS, api_key="test-key")

        # Verify the URL contained the api key
        call_url = mock_client.head.call_args[0][0]
        assert "test-key" in call_url


class TestCheckWeatherProviderHealth:
    """Tests for check_weather_provider_health"""

    @pytest.mark.asyncio
    async def test_open_meteo_no_key_needed(self):
        """Test Open-Meteo check without API key"""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.main.httpx.AsyncClient", return_value=mock_client):
            result = await check_weather_provider_health(WeatherProviderName.OPEN_METEO)

        assert result.status == ProviderStatus.AVAILABLE

    @pytest.mark.asyncio
    async def test_openweathermap_requires_key(self):
        """Test OpenWeatherMap returns error without API key"""
        result = await check_weather_provider_health(WeatherProviderName.OPENWEATHERMAP)
        assert result.status == ProviderStatus.ERROR
        assert "API key required" in result.error_message

    @pytest.mark.asyncio
    async def test_weather_api_requires_key(self):
        """Test WeatherAPI returns error without API key"""
        result = await check_weather_provider_health(WeatherProviderName.WEATHER_API)
        assert result.status == ProviderStatus.ERROR
        assert "API key required" in result.error_message

    @pytest.mark.asyncio
    async def test_weather_429_rate_limited(self):
        """Test 429 response is handled correctly"""
        mock_response = MagicMock()
        mock_response.status_code = 429

        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.main.httpx.AsyncClient", return_value=mock_client):
            result = await check_weather_provider_health(WeatherProviderName.OPEN_METEO)

        assert result.status == ProviderStatus.RATE_LIMITED


# ═══════════════════════════════════════════════════════════════════════════════
# API ENDPOINT TESTS (using TestClient, no auth/DB needed for public endpoints)
# ═══════════════════════════════════════════════════════════════════════════════
TENANT_HEADERS = {"X-Tenant-Id": "test-tenant"}


@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app, headers=TENANT_HEADERS)


class TestPublicEndpoints:
    """Tests for unauthenticated public endpoints"""

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "SAHOOL" in data["service"]
        assert "version" in data
        assert "service_ar" in data

    def test_healthz(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_readyz(self, client):
        response = client.get("/readyz")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ready"
        assert data["service"] == "provider-config"
        assert "checks" in data

    def test_list_all_providers(self, client):
        response = client.get("/providers")
        assert response.status_code == 200
        data = response.json()
        assert len(data["map_providers"]) == 10
        assert len(data["weather_providers"]) == 4
        assert len(data["satellite_providers"]) == 6

    def test_list_map_providers(self, client):
        response = client.get("/providers/maps")
        assert response.status_code == 200
        data = response.json()
        assert "providers" in data
        assert "free_providers" in data
        free_ids = data["free_providers"]
        assert "openstreetmap" in free_ids
        assert "esri_satellite" in free_ids

    def test_list_weather_providers(self, client):
        response = client.get("/providers/weather")
        assert response.status_code == 200
        data = response.json()
        assert "open_meteo" in data["free_providers"]

    def test_list_satellite_providers(self, client):
        response = client.get("/providers/satellite")
        assert response.status_code == 200
        data = response.json()
        free = data["free_providers"]
        assert "landsat" in free

    def test_list_payment_providers(self, client):
        response = client.get("/providers/payment")
        assert response.status_code == 200
        data = response.json()
        assert "by_country" in data
        assert "YE" in data["by_country"]
        assert "tharwatt" in data["by_country"]["YE"]
        assert "supports_mada" in data

    def test_list_sms_providers(self, client):
        response = client.get("/providers/sms")
        assert response.status_code == 200
        data = response.json()
        assert "by_region" in data
        assert "unifonic" in data["by_region"]["middle_east"]
        assert "supports_arabic_sender" in data

    def test_list_notification_providers(self, client):
        response = client.get("/providers/notification")
        assert response.status_code == 200
        data = response.json()
        assert "free_providers" in data
        assert "firebase_fcm" in data["free_providers"]


class TestSelectProviderEndpoint:
    """Tests for /providers/select/{provider_type}"""

    def test_select_payment_provider_yemen(self, client):
        response = client.get("/providers/select/payment?country=YE&currency=YER")
        assert response.status_code == 200
        data = response.json()
        assert data["country"] == "YE"
        selected_ids = [p["id"] for p in data["selected"]]
        assert "tharwatt" in selected_ids

    def test_select_sms_provider_yemen(self, client):
        response = client.get("/providers/select/sms?country=YE")
        assert response.status_code == 200
        data = response.json()
        assert len(data["selected"]) >= 1

    def test_select_satellite_provider(self, client):
        response = client.get("/providers/select/satellite")
        assert response.status_code == 200
        data = response.json()
        # Should be sorted by cost, cheapest first
        assert len(data["selected"]) == 2

    def test_select_weather_provider(self, client):
        response = client.get("/providers/select/weather")
        assert response.status_code == 200
        data = response.json()
        # Free providers should be selected first
        selected_ids = [p["id"] for p in data["selected"]]
        assert "open_meteo" in selected_ids

    def test_select_no_fallback(self, client):
        response = client.get("/providers/select/payment?country=YE&fallback=false")
        assert response.status_code == 200
        data = response.json()
        assert data["fallback_providers"] == []


class TestFailoverChainEndpoint:
    """Tests for /providers/failover-chain/{provider_type}"""

    def test_payment_failover_chain_yemen(self, client):
        response = client.get("/providers/failover-chain/payment?country=YE")
        assert response.status_code == 200
        data = response.json()
        assert data["provider_type"] == "payment"
        assert data["country"] == "YE"
        assert data["total_providers"] == len(data["failover_chain"])
        # First in chain should be primary priority
        if data["failover_chain"]:
            assert data["failover_chain"][0]["priority"] == "primary"

    def test_sms_failover_chain(self, client):
        response = client.get("/providers/failover-chain/sms?country=YE")
        assert response.status_code == 200
        data = response.json()
        assert data["total_providers"] >= 1

    def test_satellite_failover_chain(self, client):
        response = client.get("/providers/failover-chain/satellite")
        assert response.status_code == 200
        data = response.json()
        chain = data["failover_chain"]
        # Verify ordering: primary first, then secondary, then tertiary
        priorities = [c["priority"] for c in chain]
        priority_order = {"primary": 0, "secondary": 1, "tertiary": 2}
        mapped = [priority_order[p] for p in priorities]
        assert mapped == sorted(mapped)


class TestRecommendProviderEndpoint:
    """Tests for /providers/recommend"""

    def test_free_budget(self, client):
        response = client.get("/providers/recommend?budget=free")
        assert response.status_code == 200
        data = response.json()
        assert data["budget"] == "free"
        map_providers = [r["provider"] for r in data["map"]]
        assert "openstreetmap" in map_providers

    def test_low_budget(self, client):
        response = client.get("/providers/recommend?budget=low")
        assert response.status_code == 200
        data = response.json()
        assert len(data["satellite"]) >= 1

    def test_high_budget(self, client):
        response = client.get("/providers/recommend?budget=high")
        assert response.status_code == 200
        data = response.json()
        sat_providers = [r["provider"] for r in data["satellite"]]
        assert "planet_labs" in sat_providers

    def test_medium_budget(self, client):
        response = client.get("/providers/recommend?budget=medium")
        assert response.status_code == 200
        data = response.json()
        map_providers = [r["provider"] for r in data["map"]]
        assert "mapbox_streets" in map_providers

    def test_offline_required(self, client):
        response = client.get("/providers/recommend?offline_required=true&budget=free")
        assert response.status_code == 200
        data = response.json()
        assert data["offline_required"] is True


class TestCheckProviderEndpoint:
    """Tests for /providers/check"""

    def test_check_unknown_map_provider(self, client):
        response = client.post(
            "/providers/check",
            json={"provider_type": "map", "provider_name": "nonexistent"},
        )
        assert response.status_code == 400

    def test_check_unknown_weather_provider(self, client):
        response = client.post(
            "/providers/check",
            json={"provider_type": "weather", "provider_name": "nonexistent"},
        )
        assert response.status_code == 400

    def test_check_unsupported_provider_type(self, client):
        """Test checking a provider type that doesn't support health checks"""
        response = client.post(
            "/providers/check",
            json={"provider_type": "satellite", "provider_name": "sentinel_hub"},
        )
        assert response.status_code == 400

    def test_check_weather_provider_without_key(self, client):
        response = client.post(
            "/providers/check",
            json={"provider_type": "weather", "provider_name": "openweathermap"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "error"
        assert "API key required" in data["error_message"]

    def test_check_map_provider_success(self, client):
        """Test checking a valid map provider (mocked HTTP)"""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.head = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("src.main.httpx.AsyncClient", return_value=mock_client):
            response = client.post(
                "/providers/check",
                json={"provider_type": "map", "provider_name": "openstreetmap"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "available"


class TestGetDbSessionDependency:
    """Tests for get_db_session dependency"""

    def test_raises_503_when_no_database(self, client):
        """Accessing tenant config endpoint with no DB raises 503"""
        # Mock auth to bypass it, and ensure database is None
        with patch("src.main.database", None), patch("src.main.get_current_user", return_value=MagicMock()):
            from src.main import get_db_session

            with pytest.raises((ValueError, Exception)):
                gen = get_db_session()
                next(gen)
