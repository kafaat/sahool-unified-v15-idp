"""
Tests for advanced weather endpoints
اختبارات نقاط النهاية المتقدمة للطقس

Covers: evapotranspiration, GDD, spray-window, frost-risk,
        drought-index, chill-hours, metrics, and input validation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

try:
    from fastapi.testclient import TestClient
except BaseException as e:
    if isinstance(e, (KeyboardInterrupt, SystemExit, GeneratorExit)):
        raise
    pytest.skip("fastapi not installed", allow_module_level=True)


TENANT_ID = "00000000-0000-0000-0000-000000000123"
FIELD_ID = "field-456"


@pytest.fixture
def app():
    """Create FastAPI test app instance with auth dependency overridden"""
    from src.main import app as weather_app

    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User

    def fake_current_user():
        user = MagicMock(spec=User)
        user.id = "test-user-001"
        user.email = "test@sahool.sa"
        user.roles = ["farmer"]
        user.tenant_id = TENANT_ID
        return user

    weather_app.dependency_overrides[get_current_user] = fake_current_user
    yield weather_app
    weather_app.dependency_overrides.clear()


@pytest.fixture
def client(app):
    """Create test client with tenant context"""
    c = TestClient(app)
    c.headers["X-Tenant-ID"] = TENANT_ID
    return c


# ============== Evapotranspiration ==============


class TestEvapotranspirationEndpoint:
    """Test /weather/evapotranspiration endpoint"""

    def test_et0_calculation_success(self, client):
        """Test successful ET0 calculation"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/evapotranspiration",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 28.0,
                    "humidity_pct": 55.0,
                    "wind_speed_kmh": 12.0,
                    "solar_radiation_mj": 20.0,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert data["tenant_id"] == TENANT_ID
        assert data["field_id"] == FIELD_ID
        et = data["evapotranspiration"]
        assert "et0_mm_day" in et
        assert "classification" in et
        assert "recommendation_ar" in et
        assert "recommendation_en" in et
        assert et["et0_mm_day"] >= 0

    def test_et0_high_temperature(self, client):
        """Test ET0 increases with high temperature"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response_cool = client.post(
                "/weather/evapotranspiration",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 15.0,
                    "humidity_pct": 60.0,
                    "wind_speed_kmh": 10.0,
                    "solar_radiation_mj": 15.0,
                },
            )
            response_hot = client.post(
                "/weather/evapotranspiration",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 42.0,
                    "humidity_pct": 20.0,
                    "wind_speed_kmh": 10.0,
                    "solar_radiation_mj": 25.0,
                },
            )

        assert response_cool.status_code == 200
        assert response_hot.status_code == 200
        et_cool = response_cool.json()["evapotranspiration"]["et0_mm_day"]
        et_hot = response_hot.json()["evapotranspiration"]["et0_mm_day"]
        assert et_hot > et_cool

    def test_et0_invalid_coordinates(self, client):
        """Test validation rejects invalid humidity (out of range)"""
        response = client.post(
            "/weather/evapotranspiration",
            json={
                "tenant_id": TENANT_ID,
                "field_id": FIELD_ID,
                "temp_c": 25.0,
                "humidity_pct": 150.0,  # Invalid: > 100
                "wind_speed_kmh": 10.0,
            },
        )
        assert response.status_code == 422

    def test_et0_missing_tenant(self, client):
        """Test requires tenant_id"""
        response = client.post(
            "/weather/evapotranspiration",
            json={
                "field_id": FIELD_ID,
                "temp_c": 25.0,
                "humidity_pct": 55.0,
                "wind_speed_kmh": 10.0,
            },
        )
        assert response.status_code == 422


# ============== Growing Degree Days ==============


class TestGDDEndpoint:
    """Test /weather/gdd endpoint"""

    def test_gdd_calculation_success(self, client):
        """Test Growing Degree Days calculation"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/gdd",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_max_c": 30.0,
                    "temp_min_c": 18.0,
                    "base_temp_c": 10.0,
                    "upper_temp_c": 30.0,
                },
            )

        assert response.status_code == 200
        data = response.json()
        gdd = data["growing_degree_days"]
        assert gdd["gdd_daily"] > 0
        assert gdd["base_temp_c"] == 10.0
        assert "growth_rate" in gdd
        assert gdd["growth_rate"] != "dormant"
        assert "recommendation_ar" in gdd
        assert "recommendation_en" in gdd

    def test_gdd_below_base_temperature(self, client):
        """Test GDD is zero when temp below base"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/gdd",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_max_c": 8.0,
                    "temp_min_c": 2.0,
                    "base_temp_c": 10.0,
                    "upper_temp_c": 30.0,
                },
            )

        assert response.status_code == 200
        data = response.json()
        gdd = data["growing_degree_days"]
        assert gdd["gdd_daily"] == 0
        assert gdd["growth_rate"] == "dormant"


# ============== Spray Window ==============


class TestSprayWindowEndpoint:
    """Test /weather/spray-window endpoint"""

    def test_spray_suitable_conditions(self, client):
        """Test spray window suitable in calm weather"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/spray-window",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 22.0,
                    "humidity_pct": 55.0,
                    "wind_speed_kmh": 8.0,
                    "precipitation_probability": 5.0,
                },
            )

        assert response.status_code == 200
        data = response.json()
        spray = data["spray_window"]
        assert spray["is_suitable"] is True
        assert spray["suitability"] in ("excellent", "good")
        assert spray["score"] >= 60
        assert "recommendation_ar" in spray
        assert "recommendation_en" in spray

    def test_spray_unsuitable_windy(self, client):
        """Test spray window unsuitable in high wind"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/spray-window",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 22.0,
                    "humidity_pct": 55.0,
                    "wind_speed_kmh": 30.0,  # Very windy
                    "precipitation_probability": 80.0,  # Rain likely
                },
            )

        assert response.status_code == 200
        data = response.json()
        spray = data["spray_window"]
        assert spray["is_suitable"] is False
        assert spray["suitability"] in ("poor", "fair")
        assert "wind_too_strong" in spray["issues"]
        assert "rain_likely" in spray["issues"]

    def test_spray_unsuitable_triggers_publish(self, client):
        """Test publish_weather_alert is called when spray window is unsuitable and publisher is set"""
        mock_publisher = MagicMock()
        mock_publisher.publish_weather_alert = AsyncMock(return_value="event-id-spray")

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = mock_publisher

            response = client.post(
                "/weather/spray-window",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 22.0,
                    "humidity_pct": 55.0,
                    "wind_speed_kmh": 30.0,  # Very windy → is_suitable=False
                    "precipitation_probability": 80.0,  # Rain likely
                },
            )

        assert response.status_code == 200
        spray = response.json()["spray_window"]
        assert spray["is_suitable"] is False
        mock_publisher.publish_weather_alert.assert_awaited_once()
        call_kwargs = mock_publisher.publish_weather_alert.call_args.kwargs
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["field_id"] == FIELD_ID
        assert call_kwargs["alert_type"] == "spray_window_unsuitable"

    def test_spray_suitable_does_not_publish(self, client):
        """Test publish_weather_alert is NOT called when spray window is suitable"""
        mock_publisher = MagicMock()
        mock_publisher.publish_weather_alert = AsyncMock(return_value="event-id-spray")

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = mock_publisher

            response = client.post(
                "/weather/spray-window",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 22.0,
                    "humidity_pct": 55.0,
                    "wind_speed_kmh": 8.0,  # Calm → is_suitable=True
                    "precipitation_probability": 5.0,
                },
            )

        assert response.status_code == 200
        spray = response.json()["spray_window"]
        assert spray["is_suitable"] is True
        mock_publisher.publish_weather_alert.assert_not_awaited()

    # The contract path is /weather/spray-windows (plural — see
    # WEATHER_ENDPOINTS.SPRAY_WINDOWS). Both the plural and legacy
    # singular are wired to the SAME handler, so both paths MUST
    # accept the same payload and return the same shape. These two
    # tests catch routing regressions on either alias.
    @pytest.mark.parametrize("path", ["/weather/spray-windows", "/weather/spray-window"])
    def test_spray_window_accepts_both_path_spellings(self, client, path):
        """POST to plural (contract) and singular (legacy) return the same shape."""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None
            response = client.post(
                path,
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 22.0,
                    "humidity_pct": 55.0,
                    "wind_speed_kmh": 8.0,
                    "precipitation_probability": 5.0,
                },
            )
        assert response.status_code == 200, f"path {path} returned {response.status_code}"
        data = response.json()
        assert "spray_window" in data
        assert "is_suitable" in data["spray_window"]


# ============== Frost Risk ==============


class TestFrostRiskEndpoint:
    """Test /weather/frost-risk endpoint"""

    def test_frost_critical_below_zero(self, client):
        """Test critical frost risk below 0 C"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/frost-risk",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": -3.0,
                    "humidity_pct": 90.0,
                    "wind_speed_kmh": 3.0,
                    "cloud_cover_pct": 10.0,
                },
            )

        assert response.status_code == 200
        data = response.json()
        frost = data["frost_risk"]
        assert frost["frost_likely"] is True
        assert frost["risk_level"] in ("high", "critical")
        assert frost["risk_score"] >= 50
        assert "recommendation_ar" in frost
        assert "recommendation_en" in frost
        assert len(frost["protection_measures"]) > 0

    def test_no_frost_warm(self, client):
        """Test no frost risk at warm temperature"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/frost-risk",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "temp_c": 20.0,
                    "humidity_pct": 50.0,
                    "wind_speed_kmh": 15.0,
                    "cloud_cover_pct": 60.0,
                },
            )

        assert response.status_code == 200
        data = response.json()
        frost = data["frost_risk"]
        assert frost["frost_likely"] is False
        assert frost["risk_level"] == "none"
        assert frost["risk_score"] == 0


# ============== Drought Index ==============


class TestDroughtIndexEndpoint:
    """Test /weather/drought-index endpoint"""

    def test_drought_severe(self, client):
        """Test severe drought detection"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/drought-index",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "precipitation_mm": 10.0,
                    "et0_mm": 120.0,  # Very high ET vs low precip
                    "days": 30,
                },
            )

        assert response.status_code == 200
        data = response.json()
        drought = data["drought_index"]
        assert drought["drought_level"] in ("severe", "extreme")
        assert drought["irrigation_need_mm"] > 0
        assert drought["water_balance_mm"] < 0
        assert "recommendation_ar" in drought
        assert "recommendation_en" in drought

    def test_no_drought(self, client):
        """Test no drought in wet conditions"""
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/drought-index",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "precipitation_mm": 150.0,
                    "et0_mm": 90.0,  # Precip exceeds ET
                    "days": 30,
                },
            )

        assert response.status_code == 200
        data = response.json()
        drought = data["drought_index"]
        assert drought["drought_level"] == "none"
        assert drought["water_balance_mm"] > 0
        assert drought["irrigation_need_mm"] == 0


# ============== Chill Hours ==============


class TestChillHoursEndpoint:
    """Test /weather/chill-hours endpoint"""

    def test_chill_hours_utah_model(self, client):
        """Test Utah model chill hours"""
        # Generate 48 hours of data in the optimal Utah range (2.5-9.1 C = 1.0 unit each)
        hourly_temps = [5.0] * 48

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/chill-hours",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "hourly_temps": hourly_temps,
                    "model": "utah",
                },
            )

        assert response.status_code == 200
        data = response.json()
        chill = data["chill_hours"]
        assert chill["model"] == "utah"
        assert chill["chill_units"] == 48.0  # 48 hours * 1.0 unit each
        assert chill["hours_analyzed"] == 48
        assert "satisfied_crops" in chill
        assert "insufficient_crops" in chill
        assert "recommendation_ar" in chill
        assert "recommendation_en" in chill

    def test_chill_hours_simple_model(self, client):
        """Test simple model chill hours"""
        # 24 hours below threshold, 24 hours above
        hourly_temps = [3.0] * 24 + [15.0] * 24

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None

            response = client.post(
                "/weather/chill-hours",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "hourly_temps": hourly_temps,
                    "model": "simple",
                    "base_temp_c": 7.2,
                },
            )

        assert response.status_code == 200
        data = response.json()
        chill = data["chill_hours"]
        assert chill["model"] == "simple"
        # Only the 24 hours at 3.0 C are below 7.2 C threshold
        assert chill["chill_units"] == 24
        assert chill["hours_analyzed"] == 48

    def test_invalid_model_rejected(self, client):
        """Test invalid chill model name rejected"""
        response = client.post(
            "/weather/chill-hours",
            json={
                "tenant_id": TENANT_ID,
                "field_id": FIELD_ID,
                "hourly_temps": [5.0] * 24,
                "model": "nonexistent_model",
            },
        )
        assert response.status_code == 422


# ============== Metrics ==============


class TestMetricsEndpoint:
    """Test /metrics endpoint"""

    def test_metrics_returns_prometheus_format(self, client):
        """Test /metrics returns Prometheus format"""
        response = client.get("/metrics")
        # Either returns Prometheus metrics (200) or not-installed (501)
        assert response.status_code in (200, 501)
        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            # Prometheus content type or text/plain
            assert "text/" in content_type or "openmetrics" in content_type


# ============== Input Validation ==============


class TestInputValidation:
    """Test input validation across weather endpoints"""

    def test_temperature_out_of_range(self, client):
        """Test temp_c > 60 rejected"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": TENANT_ID,
                "field_id": FIELD_ID,
                "temp_c": 65.0,  # Exceeds le=60
            },
        )
        assert response.status_code == 422

    def test_humidity_out_of_range(self, client):
        """Test humidity > 100 rejected"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": TENANT_ID,
                "field_id": FIELD_ID,
                "temp_c": 25.0,
                "humidity_pct": 110.0,  # Exceeds le=100
            },
        )
        assert response.status_code == 422

    def test_negative_wind_rejected(self, client):
        """Test negative wind speed rejected"""
        response = client.post(
            "/weather/irrigation",
            json={
                "tenant_id": TENANT_ID,
                "field_id": FIELD_ID,
                "temp_c": 25.0,
                "humidity_pct": 55.0,
                "wind_speed_kmh": -5.0,  # ge=0 violated
                "precipitation_mm": 0.0,
            },
        )
        assert response.status_code == 422

    def test_forecast_days_clamped(self, client):
        """Test days parameter clamped to 1-16"""
        with patch("src.main.app.state") as mock_state:
            mock_provider = MagicMock()
            mock_provider.get_daily_forecast = AsyncMock(return_value=[])
            mock_state.weather_provider = mock_provider
            mock_state.multi_provider = None
            mock_state.publisher = None

            response = client.post(
                "/weather/forecast?days=50",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "lat": 15.35,
                    "lon": 44.20,
                },
            )

        # The endpoint clamps to 16, does not reject
        assert response.status_code == 200

    def test_correlation_id_too_long(self, client):
        """Test correlation_id max 200 chars"""
        response = client.post(
            "/weather/assess",
            json={
                "tenant_id": TENANT_ID,
                "field_id": FIELD_ID,
                "temp_c": 25.0,
                "correlation_id": "x" * 201,  # Exceeds max_length=200
            },
        )
        assert response.status_code == 422


# ============== Agricultural Report ==============


class TestAgriculturalReportEndpoint:
    """Test /weather/agricultural-report endpoint — publisher integration"""

    def _make_weather(self, temp_c=28.0, humidity_pct=50.0, wind_speed_kmh=10.0):
        """Build a minimal mock weather object."""
        w = MagicMock()
        w.temperature_c = temp_c
        w.humidity_pct = humidity_pct
        w.wind_speed_kmh = wind_speed_kmh
        w.precipitation_mm = 0.0
        w.cloud_cover_pct = 20.0
        return w

    def test_publish_forecast_issued_called_with_correct_args(self, client):
        """
        /weather/agricultural-report must call publish_forecast_issued with
        provider, days=1, and correlation_id when a publisher is present.
        Prevents regression of the TypeError fixed in the previous session.
        """
        mock_publisher = MagicMock()
        mock_publisher.publish_forecast_issued = AsyncMock(return_value="event-ag-001")
        mock_publisher.publish_weather_alert = AsyncMock(return_value="event-alert-001")

        mock_weather = self._make_weather(temp_c=25.0)

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = mock_publisher
            mock_state.multi_provider = None
            mock_provider = MagicMock()
            mock_provider.get_current = AsyncMock(return_value=mock_weather)
            mock_state.weather_provider = mock_provider

            response = client.post(
                "/weather/agricultural-report",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "lat": 15.35,
                    "lon": 44.20,
                    "correlation_id": "corr-ag-001",
                },
            )

        assert response.status_code == 200
        mock_publisher.publish_forecast_issued.assert_awaited_once()
        call_kwargs = mock_publisher.publish_forecast_issued.call_args.kwargs
        assert call_kwargs["tenant_id"] == TENANT_ID
        assert call_kwargs["field_id"] == FIELD_ID
        assert call_kwargs["provider"] == "Open-Meteo"
        assert call_kwargs["days"] == 1
        assert call_kwargs["correlation_id"] == "corr-ag-001"

    def test_publish_forecast_issued_not_called_without_publisher(self, client):
        """publish_forecast_issued must not be called when no publisher is configured."""
        mock_weather = self._make_weather(temp_c=25.0)

        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None
            mock_state.multi_provider = None
            mock_provider = MagicMock()
            mock_provider.get_current = AsyncMock(return_value=mock_weather)
            mock_state.weather_provider = mock_provider

            response = client.post(
                "/weather/agricultural-report",
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": FIELD_ID,
                    "lat": 15.35,
                    "lon": 44.20,
                },
            )

        assert response.status_code == 200
        data = response.json()
        assert "evapotranspiration" in data
        assert "growing_degree_days" in data
        assert "spray_window" in data
        assert "irrigation_adjustment" in data


# ============== Weather Graph Routing ==============


class TestWeatherGraphRouting:
    """Test routing for the weather-graph endpoints.

    Both `/weather/fields/{id}/graph` (contract-aligned) and
    `/api/v1/weather/fields/{id}/graph` (legacy) now hit the same handler
    (apps/services/weather-service/src/main.py). The same applies to
    GET `/weather/graphs/{id}` + `/api/v1/weather/graphs/{id}`. These
    routing tests guard against regressions — they do not exercise the
    rendering pipeline (which needs a multi-provider + graph_store
    integration), only that both paths are registered and reachable.
    """

    @pytest.mark.parametrize(
        "path",
        [
            "/weather/fields/field-abc/graph",
            "/api/v1/weather/fields/field-abc/graph",
        ],
    )
    def test_graph_generate_accepts_both_path_spellings(self, client, path):
        """POST to the new and the legacy path both resolve to the same handler.

        We assert status is NOT 404 (route is registered) — a 400/422/500
        means the route reached the handler but the mocked upstream can't
        satisfy the full generation pipeline, which is fine for a pure
        routing test.
        """
        with patch("src.main.app.state") as mock_state:
            mock_state.publisher = None
            mock_state.multi_provider = None
            # Handler's pipeline: renderer.render(...) → SVG bytes, then
            # graph_store.store(...) returns (graph_id, url_path, expires_at).
            # Mocks honour the real call signatures so the handler doesn't 500.
            mock_state.graph_renderer = MagicMock()
            mock_state.graph_renderer.render = MagicMock(return_value=b"<svg/>")
            mock_state.graph_store = MagicMock()
            import datetime as _dt

            mock_state.graph_store.store = MagicMock(
                return_value=(
                    "graph-id-1",
                    "/api/v1/weather/graphs/graph-id-1?tid=x&sig=y",
                    _dt.datetime(2026, 4, 20, tzinfo=_dt.UTC),
                )
            )

            response = client.post(
                path,
                json={
                    "tenant_id": TENANT_ID,
                    "field_id": "field-abc",
                    "lat": 24.7,
                    "lon": 46.7,
                    "days": 14,
                    "metric": "combined",
                    "language": "ar",
                },
            )

        assert response.status_code != 404, (
            f"Route {path} not registered (got 404 — regression in Kong/contract alignment)"
        )

    @pytest.mark.parametrize(
        "path",
        [
            "/weather/graphs/graph-xyz",
            "/api/v1/weather/graphs/graph-xyz",
        ],
    )
    def test_graph_fetch_accepts_both_path_spellings(self, client, path):
        """GET the new and legacy graph-fetch paths — both must reach the handler."""
        response = client.get(
            path,
            params={"tid": TENANT_ID, "sig": "bad-sig-so-handler-400s"},
        )
        # 404 alone isn't enough to detect a missing route — the registered
        # handler itself returns 404 ("Graph not found") for unknown graph IDs.
        # weather-service wraps every error in the SAHOOL envelope
        # `{success:false, error:{code, message, ...}}`. The framework default
        # for a missing route is exactly "Not Found"; a handler-raised 404
        # carries a more specific message ("Graph not found", etc.). Verified
        # empirically by hitting an unregistered path against the live test
        # app — so checking that message catches "route not registered" while
        # still allowing the handler's own 404 responses through.
        if response.status_code == 404:
            try:
                body = response.json()
                error_msg = (body.get("error") or {}).get("message") or body.get("detail")
            except ValueError:
                error_msg = None
            assert error_msg != "Not Found", (
                f"Route {path} not registered (framework-default 'Not Found' returned — handler never reached)"
            )
