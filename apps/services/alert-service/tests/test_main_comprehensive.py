"""
SAHOOL Alert Service - Comprehensive Main Module Tests
Tests for sanitize_log_input, get_tenant_id, event handlers, create_alert_internal,
health endpoints, and lifespan management.
"""

import pytest

try:
    import pydantic  # noqa: F401
    from fastapi.testclient import TestClient
except ImportError:
    pytest.skip("fastapi/pydantic not installed", allow_module_level=True)

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import UUID, uuid4


# ═══════════════════════════════════════════════════════════════════════════════
# sanitize_log_input Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestSanitizeLogInput:
    """Tests for the sanitize_log_input function."""

    def test_removes_newlines(self):
        from src.main import sanitize_log_input

        assert sanitize_log_input("line1\nline2") == "line1\\nline2"

    def test_removes_carriage_returns(self):
        from src.main import sanitize_log_input

        assert sanitize_log_input("line1\rline2") == "line1\\rline2"

    def test_removes_tabs(self):
        from src.main import sanitize_log_input

        assert sanitize_log_input("col1\tcol2") == "col1\\tcol2"

    def test_combined_control_chars(self):
        from src.main import sanitize_log_input

        result = sanitize_log_input("a\nb\rc\td")
        assert result == "a\\nb\\rc\\td"

    def test_no_special_chars(self):
        from src.main import sanitize_log_input

        assert sanitize_log_input("normal string") == "normal string"

    def test_empty_string(self):
        from src.main import sanitize_log_input

        assert sanitize_log_input("") == ""

    def test_non_string_input(self):
        from src.main import sanitize_log_input

        assert sanitize_log_input(12345) == "12345"

    def test_none_input(self):
        from src.main import sanitize_log_input

        assert sanitize_log_input(None) == "None"

    def test_uuid_input(self):
        from src.main import sanitize_log_input

        uid = uuid4()
        assert sanitize_log_input(uid) == str(uid)

    def test_log_injection_attempt(self):
        from src.main import sanitize_log_input

        # Classic log injection: attacker tries to forge a log entry
        malicious = "user-123\n2025-01-01 CRITICAL: Admin logged in"
        result = sanitize_log_input(malicious)
        assert "\n" not in result
        assert "\\n" in result


# ═══════════════════════════════════════════════════════════════════════════════
# get_tenant_id Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestGetTenantId:
    """Tests for get_tenant_id dependency."""

    def test_valid_uuid(self):
        from src.main import get_tenant_id

        tenant = "11111111-1111-1111-1111-111111111111"
        result = get_tenant_id(tenant)
        assert result == tenant

    def test_missing_header(self):
        from fastapi import HTTPException
        from src.main import get_tenant_id

        with pytest.raises(HTTPException) as exc_info:
            get_tenant_id(None)
        assert exc_info.value.status_code == 400
        assert "required" in exc_info.value.detail.lower()

    def test_invalid_uuid_format(self):
        from fastapi import HTTPException
        from src.main import get_tenant_id

        with pytest.raises(HTTPException) as exc_info:
            get_tenant_id("not-a-uuid")
        assert exc_info.value.status_code == 400
        assert "UUID" in exc_info.value.detail

    def test_empty_string(self):
        from fastapi import HTTPException
        from src.main import get_tenant_id

        with pytest.raises(HTTPException) as exc_info:
            get_tenant_id("")
        assert exc_info.value.status_code == 400


# ═══════════════════════════════════════════════════════════════════════════════
# _PERIOD_PATTERN Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestPeriodPattern:
    """Tests for the period regex pattern used in stats endpoint."""

    def test_valid_patterns(self):
        from src.main import _PERIOD_PATTERN

        assert _PERIOD_PATTERN.match("7d")
        assert _PERIOD_PATTERN.match("30d")
        assert _PERIOD_PATTERN.match("90d")
        assert _PERIOD_PATTERN.match("365d")
        assert _PERIOD_PATTERN.match("1d")
        assert _PERIOD_PATTERN.match("3650d")

    def test_invalid_patterns(self):
        from src.main import _PERIOD_PATTERN

        assert not _PERIOD_PATTERN.match("d")
        assert not _PERIOD_PATTERN.match("7")
        assert not _PERIOD_PATTERN.match("7h")
        assert not _PERIOD_PATTERN.match("")
        assert not _PERIOD_PATTERN.match("12345d")  # >4 digits
        assert not _PERIOD_PATTERN.match("-7d")


# ═══════════════════════════════════════════════════════════════════════════════
# Event Handler Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestHandleNdviAnomaly:
    """Tests for handle_ndvi_anomaly event handler."""

    @pytest.mark.asyncio
    async def test_high_severity(self):
        from src.main import handle_ndvi_anomaly

        data = {
            "event_id": "e1",
            "field_id": "field-1",
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "severity": "high",
            "anomaly_type": "drop",
            "current_ndvi": 0.1,
            "correlation_id": "c1",
        }

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_ndvi_anomaly(data)

        mock_internal.assert_awaited_once()
        alert_create = mock_internal.call_args[0][0]
        assert alert_create.severity.value == "high"

    @pytest.mark.asyncio
    async def test_non_high_severity(self):
        from src.main import handle_ndvi_anomaly

        data = {
            "event_id": "e1",
            "field_id": "field-1",
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "severity": "moderate",
            "anomaly_type": "minor",
        }

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_ndvi_anomaly(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.severity.value == "medium"

    @pytest.mark.asyncio
    async def test_missing_fields_uses_defaults(self):
        from src.main import handle_ndvi_anomaly

        data = {"event_id": "e1", "tenant_id": "11111111-1111-1111-1111-111111111111"}

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_ndvi_anomaly(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.field_id == "unknown"

    @pytest.mark.asyncio
    async def test_missing_tenant_id_drops_event(self):
        """Events without tenant_id should be dropped for tenant isolation."""
        from src.main import handle_ndvi_anomaly

        data = {"event_id": "e1", "field_id": "f1"}

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_ndvi_anomaly(data)

        # Should NOT call create_alert_internal when tenant_id is missing
        mock_internal.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        from src.main import handle_ndvi_anomaly

        data = {"event_id": "e1", "field_id": "f1", "tenant_id": "11111111-1111-1111-1111-111111111111"}

        with patch("src.main.create_alert_internal", AsyncMock(side_effect=Exception("DB error"))):
            # Should not raise
            await handle_ndvi_anomaly(data)


class TestHandleWeatherAlert:
    """Tests for handle_weather_alert event handler."""

    @pytest.mark.asyncio
    async def test_extreme_severity(self):
        from src.main import handle_weather_alert

        data = {
            "event_id": "e1",
            "field_id": "field-1",
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "severity": "extreme",
            "title": "Flood",
            "title_en": "Flood",
            "message": "Flooding",
            "message_en": "Flooding",
        }

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_weather_alert(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.severity.value == "critical"

    @pytest.mark.asyncio
    async def test_minor_severity(self):
        from src.main import handle_weather_alert

        data = {"event_id": "e1", "field_id": "field-1", "tenant_id": "11111111-1111-1111-1111-111111111111", "severity": "minor"}

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_weather_alert(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.severity.value == "low"

    @pytest.mark.asyncio
    async def test_unknown_severity_defaults_to_medium(self):
        from src.main import handle_weather_alert

        data = {"event_id": "e1", "field_id": "field-1", "tenant_id": "11111111-1111-1111-1111-111111111111", "severity": "unknown_level"}

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_weather_alert(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.severity.value == "medium"

    @pytest.mark.asyncio
    async def test_with_expires_at(self):
        from src.main import handle_weather_alert

        data = {
            "event_id": "e1",
            "field_id": "field-1",
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "severity": "severe",
            "expires_at": "2026-12-31T23:59:59+00:00",
        }

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_weather_alert(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.expires_at is not None

    @pytest.mark.asyncio
    async def test_without_expires_at(self):
        from src.main import handle_weather_alert

        data = {"event_id": "e1", "field_id": "field-1", "tenant_id": "11111111-1111-1111-1111-111111111111"}

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_weather_alert(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.expires_at is None

    @pytest.mark.asyncio
    async def test_missing_tenant_id_drops_event(self):
        """Events without tenant_id should be dropped for tenant isolation."""
        from src.main import handle_weather_alert

        data = {"event_id": "e1", "field_id": "f1"}

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_weather_alert(data)

        mock_internal.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        from src.main import handle_weather_alert

        data = {"event_id": "e1", "field_id": "f1", "tenant_id": "11111111-1111-1111-1111-111111111111"}

        with patch("src.main.create_alert_internal", AsyncMock(side_effect=Exception("fail"))):
            await handle_weather_alert(data)


class TestHandleIotThreshold:
    """Tests for handle_iot_threshold event handler."""

    @pytest.mark.asyncio
    async def test_moisture_metric_maps_to_soil_moisture_type(self):
        from src.main import handle_iot_threshold

        data = {
            "event_id": "e1",
            "field_id": "field-1",
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "metric": "soil_moisture",
            "value": 15,
            "threshold": 25,
        }

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_iot_threshold(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.type.value == "soil_moisture"

    @pytest.mark.asyncio
    async def test_non_moisture_metric_maps_to_general_type(self):
        from src.main import handle_iot_threshold

        data = {
            "event_id": "e1",
            "field_id": "field-1",
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "metric": "temperature",
            "value": 45,
            "threshold": 40,
        }

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_iot_threshold(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.type.value == "general"

    @pytest.mark.asyncio
    async def test_moisture_case_insensitive(self):
        from src.main import handle_iot_threshold

        data = {
            "event_id": "e1",
            "field_id": "field-1",
            "tenant_id": "11111111-1111-1111-1111-111111111111",
            "metric": "Soil_Moisture_Level",
            "value": 10,
            "threshold": 20,
        }

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_iot_threshold(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.type.value == "soil_moisture"

    @pytest.mark.asyncio
    async def test_missing_metric_defaults(self):
        from src.main import handle_iot_threshold

        data = {"event_id": "e1", "tenant_id": "11111111-1111-1111-1111-111111111111"}

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_iot_threshold(data)

        alert_create = mock_internal.call_args[0][0]
        assert alert_create.field_id == "unknown"

    @pytest.mark.asyncio
    async def test_missing_tenant_id_drops_event(self):
        """Events without tenant_id should be dropped for tenant isolation."""
        from src.main import handle_iot_threshold

        data = {"event_id": "e1", "field_id": "f1", "metric": "x"}

        mock_internal = AsyncMock(return_value={"id": "alert-1"})
        with patch("src.main.create_alert_internal", mock_internal):
            await handle_iot_threshold(data)

        # Should NOT call create_alert_internal when tenant_id is missing
        mock_internal.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_exception_handling(self):
        from src.main import handle_iot_threshold

        data = {"event_id": "e1", "field_id": "f1", "tenant_id": "11111111-1111-1111-1111-111111111111", "metric": "x"}

        with patch("src.main.create_alert_internal", AsyncMock(side_effect=Exception("fail"))):
            await handle_iot_threshold(data)


# ═══════════════════════════════════════════════════════════════════════════════
# create_alert_internal Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestCreateAlertInternal:
    """Tests for create_alert_internal helper."""

    @pytest.mark.asyncio
    async def test_missing_tenant_id_rejected(self):
        """create_alert_internal should reject alerts without tenant_id."""
        from fastapi import HTTPException
        from src.main import create_alert_internal
        from src.models import AlertCreate, AlertSeverity, AlertType

        alert_data = AlertCreate(
            field_id="f1",
            type=AlertType.WEATHER,
            severity=AlertSeverity.LOW,
            title="T",
            message="M",
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_alert_internal(alert_data)
        assert exc_info.value.status_code == 400
        assert "tenant" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_invalid_tenant_id_rejected(self):
        """create_alert_internal should reject alerts with non-UUID tenant_id."""
        from fastapi import HTTPException
        from src.main import create_alert_internal
        from src.models import AlertCreate, AlertSeverity, AlertType

        alert_data = AlertCreate(
            field_id="f1",
            tenant_id="not-a-valid-uuid",
            type=AlertType.WEATHER,
            severity=AlertSeverity.LOW,
            title="T",
            message="M",
        )

        with pytest.raises(HTTPException) as exc_info:
            await create_alert_internal(alert_data)
        assert exc_info.value.status_code == 400

    @pytest.mark.asyncio
    async def test_database_not_available(self):
        from fastapi import HTTPException
        from src.main import create_alert_internal
        from src.models import AlertCreate, AlertSeverity, AlertType

        alert_data = AlertCreate(
            field_id="f1",
            tenant_id="11111111-1111-1111-1111-111111111111",
            type=AlertType.WEATHER,
            severity=AlertSeverity.LOW,
            title="T",
            message="M",
        )

        with patch("src.main.SessionLocal", None):
            with pytest.raises(HTTPException) as exc_info:
                await create_alert_internal(alert_data)
            assert exc_info.value.status_code == 503

    @pytest.mark.asyncio
    async def test_successful_creation_with_publisher(self):
        from src.main import app, create_alert_internal
        from src.models import AlertCreate, AlertSeverity, AlertType

        alert_data = AlertCreate(
            field_id="f1",
            tenant_id="11111111-1111-1111-1111-111111111111",
            type=AlertType.PEST,
            severity=AlertSeverity.HIGH,
            title="Pest Alert",
            message="Pests found",
        )

        mock_db = MagicMock()
        mock_alert_obj = MagicMock()
        mock_alert_obj.id = uuid4()
        mock_alert_obj.to_dict.return_value = {
            "id": str(mock_alert_obj.id),
            "field_id": "f1",
        }

        mock_publisher = AsyncMock()
        app.state.publisher = mock_publisher

        with patch("src.main.SessionLocal", return_value=mock_db):
            with patch("src.main.create_alert", return_value=mock_alert_obj):
                result = await create_alert_internal(alert_data)

        assert result["id"] == str(mock_alert_obj.id)
        mock_db.commit.assert_called_once()
        mock_publisher.publish_alert_created.assert_awaited_once()

        # Cleanup
        app.state.publisher = None

    @pytest.mark.asyncio
    async def test_successful_creation_without_publisher(self):
        from src.main import app, create_alert_internal
        from src.models import AlertCreate, AlertSeverity, AlertType

        alert_data = AlertCreate(
            field_id="f1",
            tenant_id="11111111-1111-1111-1111-111111111111",
            type=AlertType.WEATHER,
            severity=AlertSeverity.LOW,
            title="T",
            message="M",
        )

        mock_db = MagicMock()
        mock_alert_obj = MagicMock()
        mock_alert_obj.id = uuid4()
        mock_alert_obj.to_dict.return_value = {"id": str(mock_alert_obj.id)}

        app.state.publisher = None

        with patch("src.main.SessionLocal", return_value=mock_db):
            with patch("src.main.create_alert", return_value=mock_alert_obj):
                result = await create_alert_internal(alert_data)

        assert "id" in result
        mock_db.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_rollback_on_exception(self):
        from src.main import create_alert_internal
        from src.models import AlertCreate, AlertSeverity, AlertType

        alert_data = AlertCreate(
            field_id="f1",
            tenant_id="11111111-1111-1111-1111-111111111111",
            type=AlertType.WEATHER,
            severity=AlertSeverity.LOW,
            title="T",
            message="M",
        )

        mock_db = MagicMock()

        with patch("src.main.SessionLocal", return_value=mock_db):
            with patch("src.main.create_alert", side_effect=Exception("DB error")):
                with pytest.raises(Exception, match="DB error"):
                    await create_alert_internal(alert_data)

        mock_db.rollback.assert_called_once()
        mock_db.close.assert_called_once()


# ═══════════════════════════════════════════════════════════════════════════════
# App-Level Tests (health endpoints via TestClient)
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.commit = MagicMock()
    session.close = MagicMock()
    session.execute = MagicMock()
    return session


@pytest.fixture
def test_client(mock_db_session):
    """Create test client with mocked dependencies."""
    with patch("src.main.check_db_connection", return_value=True):
        with patch("src.main.get_publisher", new=AsyncMock()):
            with patch("src.main.get_subscriber", new=AsyncMock()):
                from src.database import get_db
                from src.main import app

                app.dependency_overrides[get_db] = lambda: mock_db_session
                client = TestClient(app, raise_server_exceptions=False)
                yield client
                app.dependency_overrides.clear()


class TestHealthEndpointsComprehensive:
    """Extended health endpoint tests."""

    def test_health_returns_timestamp(self, test_client):
        response = test_client.get("/health")
        data = response.json()
        assert "timestamp" in data

    def test_health_nats_dependency_status(self, test_client):
        response = test_client.get("/health")
        data = response.json()
        assert "dependencies" in data
        assert "nats" in data["dependencies"]

    def test_healthz_shows_publisher_subscriber_status(self, test_client):
        response = test_client.get("/healthz")
        data = response.json()
        assert "nats_publisher" in data
        assert "nats_subscriber" in data

    def test_readyz_includes_counts(self, test_client, mock_db_session):
        # Mock the count queries
        mock_scalar_result = MagicMock()
        mock_scalar_result.scalar.return_value = 42
        mock_db_session.execute.return_value = mock_scalar_result

        with patch("src.main.check_db_connection", return_value=True):
            with patch("src.main.SessionLocal", return_value=mock_db_session):
                response = test_client.get("/readyz")

        data = response.json()
        assert "alerts_count" in data
        assert "rules_count" in data


class TestStatsEndpointValidation:
    """Tests for stats endpoint period validation."""

    def test_invalid_period_format(self, test_client):
        response = test_client.get(
            "/alerts/stats",
            params={"period": "abc"},
            headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
        )
        assert response.status_code == 422  # FastAPI query validation

    def test_stats_with_zero_total(self, test_client, mock_db_session):
        mock_stats = {
            "total_alerts": 0,
            "active_alerts": 0,
            "by_type": {},
            "by_severity": {},
            "by_status": {},
            "acknowledged_count": 0,
            "resolved_count": 0,
            "average_resolution_hours": None,
        }
        with patch("src.main.get_alert_statistics", return_value=mock_stats):
            response = test_client.get(
                "/alerts/stats",
                params={"period": "30d"},
                headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["acknowledged_rate"] == 0
        assert data["resolved_rate"] == 0

    def test_stats_rate_calculation(self, test_client, mock_db_session):
        mock_stats = {
            "total_alerts": 200,
            "active_alerts": 50,
            "by_type": {"weather": 100},
            "by_severity": {"high": 100},
            "by_status": {"active": 50, "acknowledged": 50, "resolved": 100},
            "acknowledged_count": 50,
            "resolved_count": 100,
            "average_resolution_hours": 3.5,
        }
        with patch("src.main.get_alert_statistics", return_value=mock_stats):
            response = test_client.get(
                "/alerts/stats",
                params={"period": "30d"},
                headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
            )
        assert response.status_code == 200
        data = response.json()
        assert data["acknowledged_rate"] == 25.0
        assert data["resolved_rate"] == 50.0


class TestTenantValidationEndpoints:
    """Test tenant validation through API endpoints."""

    def test_invalid_tenant_uuid_on_create(self, test_client):
        response = test_client.post(
            "/alerts",
            json={
                "field_id": "f1",
                "type": "weather",
                "severity": "low",
                "title": "T",
                "message": "M",
            },
            headers={"X-Tenant-Id": "bad-uuid"},
        )
        assert response.status_code == 400

    def test_missing_tenant_on_get_rules(self, test_client):
        response = test_client.get("/alerts/rules")
        assert response.status_code == 400

    def test_rule_tenant_mismatch(self, test_client, mock_db_session):
        payload = {
            "field_id": "field-1",
            "tenant_id": "22222222-2222-2222-2222-222222222222",
            "name": "Rule",
            "condition": {"metric": "ndvi", "operator": "lt", "value": 0.3},
            "alert_config": {"type": "ndvi_low", "severity": "high", "title": "T"},
        }
        response = test_client.post(
            "/alerts/rules",
            json=payload,
            headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
        )
        assert response.status_code == 403

    def test_delete_rule_invalid_id_format(self, test_client):
        response = test_client.delete(
            "/alerts/rules/not-a-uuid",
            headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
        )
        assert response.status_code == 400


class TestAlertActionEdgeCases:
    """Edge case tests for alert action endpoints."""

    def test_acknowledge_invalid_uuid(self, test_client):
        response = test_client.post(
            "/alerts/bad-uuid/acknowledge",
            params={"user_id": "user-1"},
            headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
        )
        assert response.status_code == 400

    def test_resolve_invalid_uuid(self, test_client):
        response = test_client.post(
            "/alerts/bad-uuid/resolve",
            params={"user_id": "user-1"},
            headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
        )
        assert response.status_code == 400

    def test_dismiss_invalid_uuid(self, test_client):
        response = test_client.post(
            "/alerts/bad-uuid/dismiss",
            params={"user_id": "user-1"},
            headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
        )
        assert response.status_code == 400

    def test_acknowledge_not_found(self, test_client, mock_db_session):
        alert_id = str(uuid4())
        with patch("src.main.get_alert", return_value=None):
            response = test_client.post(
                f"/alerts/{alert_id}/acknowledge",
                params={"user_id": "user-1"},
                headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
            )
        assert response.status_code == 404

    def test_resolve_not_found(self, test_client, mock_db_session):
        alert_id = str(uuid4())
        with patch("src.main.get_alert", return_value=None):
            response = test_client.post(
                f"/alerts/{alert_id}/resolve",
                params={"user_id": "user-1"},
                headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
            )
        assert response.status_code == 404

    def test_dismiss_not_found(self, test_client, mock_db_session):
        alert_id = str(uuid4())
        with patch("src.main.get_alert", return_value=None):
            response = test_client.post(
                f"/alerts/{alert_id}/dismiss",
                params={"user_id": "user-1"},
                headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
            )
        assert response.status_code == 404

    def test_update_alert_no_update_data(self, test_client, mock_db_session):
        """When update_data has no status, should return the alert as-is."""
        mock_alert = MagicMock()
        mock_alert.status = "active"
        mock_alert.to_dict.return_value = {
            "id": str(uuid4()),
            "field_id": "f1",
            "tenant_id": None,
            "type": "weather",
            "severity": "low",
            "status": "active",
            "title": "T",
            "title_en": None,
            "message": "M",
            "message_en": None,
            "recommendations": [],
            "recommendations_en": [],
            "metadata": {},
            "source_service": None,
            "correlation_id": None,
            "created_at": datetime.now(UTC).isoformat(),
            "expires_at": None,
            "acknowledged_at": None,
            "acknowledged_by": None,
            "dismissed_at": None,
            "dismissed_by": None,
            "resolved_at": None,
            "resolved_by": None,
            "resolution_note": None,
        }

        alert_id = str(uuid4())
        with patch("src.main.get_alert", return_value=mock_alert):
            response = test_client.patch(
                f"/alerts/{alert_id}",
                json={},  # empty update
                headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
            )
        assert response.status_code == 200

    def test_delete_alert_invalid_uuid(self, test_client):
        response = test_client.delete(
            "/alerts/bad-uuid",
            headers={"X-Tenant-Id": "11111111-1111-1111-1111-111111111111"},
        )
        assert response.status_code == 400
