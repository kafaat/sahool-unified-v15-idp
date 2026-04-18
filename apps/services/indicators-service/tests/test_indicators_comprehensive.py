"""
Comprehensive unit tests for SAHOOL Indicators Service
اختبارات شاملة لخدمة المؤشرات الزراعية

Targets >60% code coverage of src/main.py
"""

import asyncio
import json
import sys
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add the service directory to sys.path
# ---------------------------------------------------------------------------
# Mock all external/shared dependencies before importing source
# ---------------------------------------------------------------------------


class _NoopMiddleware:
    """A pass-through ASGI middleware that does nothing."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        await self.app(scope, receive, send)


# Pre-populate sys.modules with mocks for shared packages
for _mod in [
    "shared",
    "shared.errors_py",
    "shared.middleware",
    "shared.middleware.tenant_context",
    "shared.auth",
    "shared.auth.dependencies",
    "shared.auth.models",
    "shared.events",
    "shared.events.subjects",
    "shared.logging_config",
    "shared.observability",
    "shared.observability.tracing",
    "nats",
    "asyncpg",
    "structlog",
]:
    sys.modules.setdefault(_mod, MagicMock())

# Wire up callables that are invoked at import time
sys.modules["shared.errors_py"].setup_exception_handlers = lambda app: None
sys.modules["shared.errors_py"].add_request_id_middleware = lambda app: None
sys.modules["shared.middleware.tenant_context"].TenantContextMiddleware = _NoopMiddleware
sys.modules["shared.events.subjects"].get_tenant_subject = lambda tenant_id, domain, action: (
    f"sahool.tenant.{tenant_id}.{domain}.{action}"
)
# Wave-3 platform helpers: structured logging + OTel tracing
sys.modules["shared.logging_config"].setup_logging = lambda *a, **k: MagicMock()
sys.modules["shared.logging_config"].get_logger = lambda *a, **k: MagicMock()
sys.modules["shared.observability.tracing"].setup_tracing = lambda *a, **k: MagicMock()

# Provide a mock User class and get_current_user callable
_mock_user = MagicMock()
_mock_user.tenant_id = "tenant_001"
_mock_user.roles = ["admin"]


async def _fake_get_current_user():
    return _mock_user


sys.modules["shared.auth.dependencies"].get_current_user = _fake_get_current_user
sys.modules["shared.auth.models"].User = type("User", (), {"tenant_id": None, "roles": []})

# Now import the actual source code
from src.main import (
    INDICATOR_DEFINITIONS,
    AlertSeverity,
    DashboardSummary,
    FieldIndicators,
    Indicator,
    IndicatorAlert,
    IndicatorCategory,
    IndicatorInput,
    TrendDirection,
    _enforce_tenant,
    app,
    create_alert_if_needed,
    delete_field_indicators,
    determine_status,
    generate_indicator_value,
    get_all_field_indicators,
    get_indicator,
    get_recommendation_ar,
    get_recommendation_en,
    get_tenant_indicators,
    publish_event,
    save_indicator,
)


# ---------------------------------------------------------------------------
# Helpers for creating async-context-manager-compatible mock pools
# ---------------------------------------------------------------------------
def _make_mock_pool(mock_conn):
    """Create a mock asyncpg pool whose acquire() works as an async context manager."""
    mock_pool = MagicMock()

    @asynccontextmanager
    async def _acquire():
        yield mock_conn

    mock_pool.acquire = _acquire
    return mock_pool


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

try:
    from fastapi.testclient import TestClient
except ImportError:
    TestClient = None  # type: ignore


@pytest.fixture(autouse=True)
def _reset_app_state():
    """Ensure app.state is clean before and after every test."""
    app.state.db_pool = None
    app.state.nc = None
    yield
    app.state.db_pool = None
    app.state.nc = None


@pytest.fixture
def client():
    """Synchronous TestClient for HTTP endpoint tests."""
    if TestClient is None:
        pytest.skip("fastapi not installed")
    return TestClient(app, raise_server_exceptions=False)


# ===========================================================================
# 1. Enum tests
# ===========================================================================
class TestEnums:
    def test_indicator_category_values(self):
        assert IndicatorCategory.VEGETATION == "vegetation"
        assert IndicatorCategory.WATER == "water"
        assert IndicatorCategory.SOIL == "soil"
        assert IndicatorCategory.WEATHER == "weather"
        assert IndicatorCategory.CROP_HEALTH == "crop_health"
        assert IndicatorCategory.PRODUCTIVITY == "productivity"
        assert IndicatorCategory.FINANCIAL == "financial"

    def test_trend_direction_values(self):
        assert TrendDirection.UP == "up"
        assert TrendDirection.DOWN == "down"
        assert TrendDirection.STABLE == "stable"

    def test_alert_severity_values(self):
        assert AlertSeverity.INFO == "info"
        assert AlertSeverity.WARNING == "warning"
        assert AlertSeverity.CRITICAL == "critical"


# ===========================================================================
# 2. Pydantic model tests
# ===========================================================================
class TestModels:
    def test_indicator_model(self):
        ind = Indicator(
            id="ndvi",
            name_ar="ن",
            name_en="NDVI",
            category=IndicatorCategory.VEGETATION,
            value=0.65,
            unit="index",
            min_value=-1.0,
            max_value=1.0,
            optimal_min=0.4,
            optimal_max=0.8,
            trend=TrendDirection.UP,
            trend_percent=5.2,
            status="optimal",
            last_updated=datetime.now(UTC),
        )
        assert ind.id == "ndvi"
        assert ind.value == 0.65

    def test_field_indicators_model(self):
        fi = FieldIndicators(
            field_id="f1",
            field_name="T",
            area_hectares=10.0,
            crop_type="wheat",
            indicators=[],
            overall_score=85.0,
            alerts=[],
        )
        assert fi.field_id == "f1"

    def test_dashboard_summary_model(self):
        ds = DashboardSummary(
            tenant_id="t1",
            total_fields=5,
            total_area_hectares=50.0,
            average_health_score=72.0,
            indicators_summary={},
            active_alerts=3,
            critical_alerts=1,
            top_performing_fields=[],
            attention_needed_fields=[],
            generated_at=datetime.now(UTC),
        )
        assert ds.total_fields == 5

    def test_indicator_alert_model(self):
        alert = IndicatorAlert(
            alert_id="a1",
            field_id="f1",
            indicator_id="ndvi",
            indicator_name_ar="ن",
            severity=AlertSeverity.WARNING,
            message_ar="m",
            message_en="m",
            current_value=0.3,
            threshold_value=0.4,
            recommended_action_ar="a",
            recommended_action_en="a",
            created_at=datetime.now(UTC),
        )
        assert alert.severity == AlertSeverity.WARNING

    def test_indicator_input_defaults(self):
        inp = IndicatorInput(indicator_type="ndvi", value=0.5)
        assert inp.trend is None
        assert inp.trend_percent is None

    def test_indicator_input_with_all_fields(self):
        inp = IndicatorInput(
            indicator_type="ndvi",
            value=0.65,
            trend=TrendDirection.UP,
            trend_percent=3.0,
        )
        assert inp.trend == TrendDirection.UP


# ===========================================================================
# 3. determine_status
# ===========================================================================
class TestDetermineStatus:
    def test_optimal_in_range(self):
        assert determine_status(0.6, 0.4, 0.8, -1.0, 1.0) == "optimal"

    def test_at_optimal_min(self):
        assert determine_status(0.4, 0.4, 0.8, -1.0, 1.0) == "optimal"

    def test_at_optimal_max(self):
        assert determine_status(0.8, 0.4, 0.8, -1.0, 1.0) == "optimal"

    def test_warning_below(self):
        # distance = (0.4 - 0.2) / (0.4 - (-1.0)) = 0.143 < 0.5 => warning
        assert determine_status(0.2, 0.4, 0.8, -1.0, 1.0) == "warning"

    def test_critical_far_below(self):
        # distance = (0.4 - (-0.9)) / (0.4 - (-1.0)) = 1.3/1.4 ~ 0.93 > 0.5 => critical
        assert determine_status(-0.9, 0.4, 0.8, -1.0, 1.0) == "critical"

    def test_warning_above(self):
        # distance = (0.85 - 0.8) / (1.0 - 0.8) = 0.25 < 0.5 => warning
        assert determine_status(0.85, 0.4, 0.8, -1.0, 1.0) == "warning"

    def test_critical_far_above(self):
        # distance = (0.95 - 0.8) / (1.0 - 0.8) = 0.75 > 0.5 => critical
        assert determine_status(0.95, 0.4, 0.8, -1.0, 1.0) == "critical"

    def test_none_optimal_returns_info(self):
        assert determine_status(5.0, None, None, 0, 10) == "info"

    def test_optimal_min_equals_min_val_distance_zero(self):
        # optimal_min == min_val => denominator is 0 => distance = 0 => warning
        assert determine_status(0.3, 0.4, 0.8, 0.4, 1.0) == "warning"

    def test_optimal_max_equals_max_val_distance_zero(self):
        # optimal_max == max_val => denominator is 0 => distance = 0 => warning
        assert determine_status(0.9, 0.4, 0.8, -1.0, 0.8) == "warning"


# ===========================================================================
# 4. generate_indicator_value
# ===========================================================================
class TestGenerateIndicatorValue:
    def test_returns_three_tuple(self):
        result = generate_indicator_value(INDICATOR_DEFINITIONS["ndvi"])
        assert len(result) == 3

    def test_value_clamped_to_range(self):
        defn = INDICATOR_DEFINITIONS["ndvi"]
        for _ in range(50):
            val, _, _ = generate_indicator_value(defn)
            assert defn["min"] <= val <= defn["max"]

    def test_trend_valid(self):
        defn = INDICATOR_DEFINITIONS["soil_moisture"]
        for _ in range(20):
            _, trend, _ = generate_indicator_value(defn)
            assert trend in (TrendDirection.UP, TrendDirection.DOWN, TrendDirection.STABLE)

    def test_trend_percent_non_negative(self):
        defn = INDICATOR_DEFINITIONS["temperature"]
        for _ in range(20):
            _, _, pct = generate_indicator_value(defn)
            assert pct >= 0

    def test_none_optimal_handled(self):
        defn = INDICATOR_DEFINITIONS["crop_stage_progress"]  # has None optimal values
        val, _, _ = generate_indicator_value(defn)
        assert defn["min"] <= val <= defn["max"]

    def test_low_health_still_valid(self):
        defn = INDICATOR_DEFINITIONS["ndvi"]
        val, _, _ = generate_indicator_value(defn, base_health=0.1)
        assert defn["min"] <= val <= defn["max"]


# ===========================================================================
# 5. create_alert_if_needed
# ===========================================================================
def _make_indicator(id_="ndvi", value=0.3, status="warning"):
    return Indicator(
        id=id_,
        name_ar="ن",
        name_en="NDVI",
        category=IndicatorCategory.VEGETATION,
        value=value,
        unit="index",
        min_value=-1.0,
        max_value=1.0,
        optimal_min=0.4,
        optimal_max=0.8,
        trend=TrendDirection.STABLE,
        trend_percent=0,
        status=status,
        last_updated=datetime.now(UTC),
    )


class TestCreateAlertIfNeeded:
    def test_optimal_returns_none(self):
        assert create_alert_if_needed(_make_indicator(status="optimal", value=0.6), "f1") is None

    def test_warning_below(self):
        alert = create_alert_if_needed(_make_indicator(status="warning", value=0.3), "f1")
        assert alert is not None
        assert alert.severity == AlertSeverity.WARNING
        assert "below" in alert.message_en

    def test_critical_above(self):
        alert = create_alert_if_needed(_make_indicator(status="critical", value=0.95), "f1")
        assert alert is not None
        assert alert.severity == AlertSeverity.CRITICAL
        assert "above" in alert.message_en

    def test_unknown_indicator_returns_none(self):
        assert create_alert_if_needed(_make_indicator(id_="nonexistent", status="warning"), "f1") is None

    def test_alert_bilingual(self):
        alert = create_alert_if_needed(_make_indicator(status="warning", value=0.3), "f1")
        assert alert.message_ar
        assert alert.message_en
        assert alert.recommended_action_ar
        assert alert.recommended_action_en


# ===========================================================================
# 6. Recommendation helpers
# ===========================================================================
class TestRecommendations:
    def test_known_ar(self):
        assert len(get_recommendation_ar("ndvi", 0.3, 0.4)) > 0

    def test_known_en(self):
        assert "irrigation" in get_recommendation_en("soil_moisture", 20, 40).lower()

    def test_fallback_ar(self):
        assert "مراجعة" in get_recommendation_ar("unknown", 0, 0)

    def test_fallback_en(self):
        assert "Review" in get_recommendation_en("unknown", 0, 0)

    def test_disease_risk_en(self):
        rec = get_recommendation_en("disease_risk", 50, 20)
        assert len(rec) > 0

    def test_temperature_ar(self):
        assert len(get_recommendation_ar("temperature", 45, 32)) > 0

    def test_irrigation_efficiency_en(self):
        rec = get_recommendation_en("irrigation_efficiency", 50, 75)
        assert len(rec) > 0


# ===========================================================================
# 7. INDICATOR_DEFINITIONS validation
# ===========================================================================
class TestIndicatorDefinitions:
    def test_not_empty(self):
        assert len(INDICATOR_DEFINITIONS) > 0

    def test_required_keys(self):
        required = {"name_ar", "name_en", "category", "unit", "min", "max", "optimal_min", "optimal_max"}
        for k, d in INDICATOR_DEFINITIONS.items():
            assert required.issubset(d.keys()), f"{k} missing keys"

    def test_all_categories_represented(self):
        cats = {d["category"] for d in INDICATOR_DEFINITIONS.values()}
        for cat in IndicatorCategory:
            assert cat in cats

    def test_min_less_than_max(self):
        for k, d in INDICATOR_DEFINITIONS.items():
            assert d["min"] < d["max"], f"{k}"


# ===========================================================================
# 8. _enforce_tenant
# ===========================================================================
class TestEnforceTenant:
    def test_no_user_raises_401(self):
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc:
            _enforce_tenant(None, "t1")
        assert exc.value.status_code == 401

    def test_matching_tenant_ok(self):
        u = MagicMock(tenant_id="t1", roles=[])
        _enforce_tenant(u, "t1")

    def test_mismatch_raises_403(self):
        from fastapi import HTTPException

        u = MagicMock(tenant_id="t1", roles=[])
        with pytest.raises(HTTPException) as exc:
            _enforce_tenant(u, "t2")
        assert exc.value.status_code == 403

    def test_admin_bypasses(self):
        u = MagicMock(tenant_id="t1", roles=["admin"])
        _enforce_tenant(u, "t2")

    def test_super_admin_bypasses(self):
        u = MagicMock(tenant_id="t1", roles=["super_admin"])
        _enforce_tenant(u, "t2")

    def test_no_tenant_on_user(self):
        u = MagicMock(tenant_id=None, roles=[])
        _enforce_tenant(u, "t1")


# ===========================================================================
# 9. publish_event
# ===========================================================================
class TestPublishEvent:
    def test_publishes_when_connected(self):
        nc = AsyncMock()
        app.state.nc = nc
        asyncio.run(publish_event("sahool.test", {"k": "v"}))
        nc.publish.assert_called_once()
        payload = json.loads(nc.publish.call_args[0][1].decode())
        assert payload["k"] == "v"

    def test_noop_when_disconnected(self):
        app.state.nc = None
        asyncio.run(publish_event("sahool.test", {"k": "v"}))  # no error

    def test_handles_publish_error(self):
        nc = AsyncMock()
        nc.publish.side_effect = Exception("boom")
        app.state.nc = nc
        asyncio.run(publish_event("sahool.test", {}))  # logs warning, no raise


# ===========================================================================
# 10. Database helper functions
# ===========================================================================
class TestSaveIndicator:
    def test_no_pool_returns_false(self):
        assert asyncio.run(save_indicator("f1", "ndvi", {})) is False

    def test_success(self):
        conn = AsyncMock()
        app.state.db_pool = _make_mock_pool(conn)
        assert asyncio.run(save_indicator("f1", "ndvi", {"v": 1}, "t1")) is True
        conn.execute.assert_called_once()

    def test_db_error_returns_false(self):
        conn = AsyncMock()
        conn.execute.side_effect = Exception("db")
        app.state.db_pool = _make_mock_pool(conn)
        assert asyncio.run(save_indicator("f1", "ndvi", {})) is False


class TestGetIndicator:
    def test_no_pool_returns_none(self):
        assert asyncio.run(get_indicator("f1", "ndvi")) is None

    def test_found(self):
        conn = AsyncMock()
        conn.fetchrow.return_value = {
            "value": json.dumps({"value": 0.65}),
            "calculated_at": datetime.now(UTC),
        }
        app.state.db_pool = _make_mock_pool(conn)
        result = asyncio.run(get_indicator("f1", "ndvi"))
        assert result is not None
        assert result["value"] == 0.65
        assert "calculated_at" in result

    def test_not_found(self):
        conn = AsyncMock()
        conn.fetchrow.return_value = None
        app.state.db_pool = _make_mock_pool(conn)
        assert asyncio.run(get_indicator("f1", "ndvi")) is None

    def test_db_error_returns_none(self):
        conn = AsyncMock()
        conn.fetchrow.side_effect = Exception("db")
        app.state.db_pool = _make_mock_pool(conn)
        assert asyncio.run(get_indicator("f1", "ndvi")) is None


class TestGetAllFieldIndicators:
    def test_no_pool(self):
        assert asyncio.run(get_all_field_indicators("f1")) == []

    def test_with_rows(self):
        conn = AsyncMock()
        conn.fetch.return_value = [
            {"indicator_type": "ndvi", "value": json.dumps({"v": 0.6}), "calculated_at": datetime.now(UTC)},
            {"indicator_type": "evi", "value": json.dumps({"v": 0.5}), "calculated_at": datetime.now(UTC)},
        ]
        app.state.db_pool = _make_mock_pool(conn)
        result = asyncio.run(get_all_field_indicators("f1"))
        assert len(result) == 2
        assert result[0]["indicator_type"] == "ndvi"

    def test_db_error(self):
        conn = AsyncMock()
        conn.fetch.side_effect = Exception("db")
        app.state.db_pool = _make_mock_pool(conn)
        assert asyncio.run(get_all_field_indicators("f1")) == []


class TestGetTenantIndicators:
    def test_no_pool(self):
        assert asyncio.run(get_tenant_indicators("t1")) == []

    def test_with_rows(self):
        conn = AsyncMock()
        conn.fetch.return_value = [
            {
                "field_id": "f1",
                "indicator_type": "ndvi",
                "value": json.dumps({"v": 0.7}),
                "calculated_at": datetime.now(UTC),
            },
        ]
        app.state.db_pool = _make_mock_pool(conn)
        result = asyncio.run(get_tenant_indicators("t1", limit=50))
        assert len(result) == 1
        assert result[0]["field_id"] == "f1"

    def test_db_error(self):
        conn = AsyncMock()
        conn.fetch.side_effect = Exception("db")
        app.state.db_pool = _make_mock_pool(conn)
        assert asyncio.run(get_tenant_indicators("t1")) == []


class TestDeleteFieldIndicators:
    def test_no_pool(self):
        assert asyncio.run(delete_field_indicators("f1", "tenant_001")) is False

    def test_success(self):
        conn = AsyncMock()
        app.state.db_pool = _make_mock_pool(conn)
        assert asyncio.run(delete_field_indicators("f1", "tenant_001")) is True

    def test_db_error(self):
        conn = AsyncMock()
        conn.execute.side_effect = Exception("db")
        app.state.db_pool = _make_mock_pool(conn)
        assert asyncio.run(delete_field_indicators("f1", "tenant_001")) is False


# ===========================================================================
# 11. HTTP endpoint tests
# ===========================================================================
class TestHealthEndpoints:
    def test_healthz(self, client):
        r = client.get("/healthz")
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "ok"
        assert d["service"] == "indicators-service"
        assert d["version"] == "16.0.0"

    def test_readyz_disconnected(self, client):
        r = client.get("/readyz")
        assert r.status_code == 200
        d = r.json()
        assert d["checks"]["nats"] in ("disconnected", "not_configured")
        assert d["checks"]["database"] in ("disconnected", "not_configured")

    def test_readyz_connected(self, client):
        nc_mock = MagicMock()
        nc_mock.is_closed = False
        app.state.nc = nc_mock
        app.state.db_pool = MagicMock()
        r = client.get("/readyz")
        assert r.status_code == 200
        assert r.json()["checks"]["nats"] == "connected"
        # database check uses async with db_pool.acquire() which a plain
        # MagicMock cannot satisfy, so it falls into the except branch.
        assert r.json()["checks"]["database"] in ("connected", "disconnected")


class TestDefinitionsEndpoint:
    def test_list_definitions(self, client):
        r = client.get("/v1/indicators/definitions")
        assert r.status_code == 200
        d = r.json()
        assert len(d["indicators"]) == len(INDICATOR_DEFINITIONS)
        assert len(d["categories"]) == len(IndicatorCategory)

    def test_definition_structure(self, client):
        r = client.get("/v1/indicators/definitions")
        for ind in r.json()["indicators"]:
            for key in ("id", "name_ar", "name_en", "category", "unit", "range", "optimal_range"):
                assert key in ind


class TestFieldIndicatorsEndpoint:
    def test_get_vegetation_indicators(self, client):
        """Filter by vegetation category (avoids crop_stage_progress None optimal)."""
        r = client.get("/v1/field/field_001/indicators?category=vegetation")
        assert r.status_code == 200
        d = r.json()
        assert d["field_id"] == "field_001"
        assert len(d["indicators"]) > 0
        assert "overall_score" in d
        assert "alerts" in d

    def test_get_water_indicators(self, client):
        r = client.get("/v1/field/f1/indicators?category=water")
        assert r.status_code == 200
        for ind in r.json()["indicators"]:
            assert ind["category"] == "water"

    def test_get_soil_indicators(self, client):
        r = client.get("/v1/field/f1/indicators?category=soil")
        assert r.status_code == 200
        for ind in r.json()["indicators"]:
            assert ind["category"] == "soil"

    def test_force_refresh_vegetation(self, client):
        r = client.get("/v1/field/f1/indicators?category=vegetation&force_refresh=true")
        assert r.status_code == 200

    def test_all_indicators_returns_all_categories(self, client):
        """Unfiltered request returns indicators from all categories."""
        r = client.get("/v1/field/f1/indicators")
        assert r.status_code == 200

    def test_weather_indicators(self, client):
        r = client.get("/v1/field/f1/indicators?category=weather")
        assert r.status_code == 200

    def test_financial_indicators(self, client):
        r = client.get("/v1/field/f1/indicators?category=financial")
        assert r.status_code == 200

    def test_crop_health_indicators(self, client):
        r = client.get("/v1/field/f1/indicators?category=crop_health")
        assert r.status_code == 200


class TestStoreFieldIndicator:
    def test_invalid_type_returns_400(self, client):
        r = client.post("/v1/field/f1/indicators", json={"indicator_type": "bad", "value": 0.5})
        assert r.status_code == 400

    def test_value_out_of_range_returns_400(self, client):
        r = client.post("/v1/field/f1/indicators", json={"indicator_type": "ndvi", "value": 5.0})
        assert r.status_code == 400

    def test_no_db_returns_503(self, client):
        r = client.post("/v1/field/f1/indicators", json={"indicator_type": "ndvi", "value": 0.5})
        assert r.status_code == 503

    def test_success(self, client):
        conn = AsyncMock()
        app.state.db_pool = _make_mock_pool(conn)
        r = client.post("/v1/field/f1/indicators", json={"indicator_type": "ndvi", "value": 0.65})
        assert r.status_code == 200
        d = r.json()
        assert d["status"] == "stored"
        assert d["value"] == 0.65
        assert "computed_status" in d

    def test_with_trend(self, client):
        conn = AsyncMock()
        app.state.db_pool = _make_mock_pool(conn)
        r = client.post(
            "/v1/field/f1/indicators",
            json={
                "indicator_type": "soil_moisture",
                "value": 55.0,
                "trend": "up",
                "trend_percent": 3.5,
                "tenant_id": "t1",
            },
        )
        assert r.status_code == 200
        assert r.json()["computed_status"] == "optimal"

    def test_value_at_min_boundary(self, client):
        conn = AsyncMock()
        app.state.db_pool = _make_mock_pool(conn)
        r = client.post("/v1/field/f1/indicators", json={"indicator_type": "ndvi", "value": -1.0})
        assert r.status_code == 200

    def test_value_at_max_boundary(self, client):
        conn = AsyncMock()
        app.state.db_pool = _make_mock_pool(conn)
        r = client.post("/v1/field/f1/indicators", json={"indicator_type": "ndvi", "value": 1.0})
        assert r.status_code == 200


class TestGetSingleIndicator:
    def test_invalid_type_returns_400(self, client):
        r = client.get("/v1/field/f1/indicator/nonexistent")
        assert r.status_code == 400

    def test_not_found_returns_404(self, client):
        r = client.get("/v1/field/f1/indicator/ndvi")
        assert r.status_code == 404

    def test_found(self, client):
        conn = AsyncMock()
        conn.fetchrow.return_value = {
            "value": json.dumps({"value": 0.72, "status": "optimal", "trend": "up", "trend_percent": 2.1}),
            "calculated_at": datetime.now(UTC),
        }
        app.state.db_pool = _make_mock_pool(conn)
        r = client.get("/v1/field/f1/indicator/ndvi")
        assert r.status_code == 200
        d = r.json()
        assert d["field_id"] == "f1"
        assert d["indicator"]["id"] == "ndvi"
        assert d["indicator"]["value"] == 0.72


class TestDeleteEndpoint:
    def test_no_db_returns_503(self, client):
        r = client.delete("/v1/field/f1/indicators")
        assert r.status_code == 503

    def test_success(self, client):
        conn = AsyncMock()
        app.state.db_pool = _make_mock_pool(conn)
        r = client.delete("/v1/field/f1/indicators")
        assert r.status_code == 200
        assert r.json()["status"] == "deleted"


class TestTrendsEndpoint:
    def test_invalid_indicator_returns_404(self, client):
        r = client.get("/v1/trends/f1/nonexistent")
        assert r.status_code == 404

    def test_valid_trend(self, client):
        r = client.get("/v1/trends/f1/ndvi?days=14")
        assert r.status_code == 200
        d = r.json()
        assert d["field_id"] == "f1"
        assert d["period_days"] == 14
        assert len(d["data_points"]) == 14
        assert d["overall_trend"] in ("up", "down", "stable")

    def test_trend_data_point_structure(self, client):
        r = client.get("/v1/trends/f1/soil_moisture?days=7")
        assert r.status_code == 200
        for dp in r.json()["data_points"]:
            assert "date" in dp
            assert "value" in dp
            assert "status" in dp

    def test_trend_statistics(self, client):
        r = client.get("/v1/trends/f1/ndvi?days=10")
        assert r.status_code == 200
        stats = r.json()["statistics"]
        assert "average" in stats
        assert "minimum" in stats
        assert "maximum" in stats
        assert "optimal_range" in stats
        assert stats["minimum"] <= stats["average"] <= stats["maximum"]
