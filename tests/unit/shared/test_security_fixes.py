"""
Tests for security fixes applied across shared modules.
اختبارات إصلاحات الأمان عبر الوحدات المشتركة

Validates all CRITICAL and HIGH severity fixes from the security review:
- SQL injection prevention (parameterized queries)
- Command injection prevention (allowlists, subprocess validation)
- SSRF prevention (URL scheme validation)
- Auth bypass prevention (tenant isolation, role checks)
- Rate limiting (fail-closed, hash collision)
- Information disclosure prevention
- CORS security
- Division by zero guards
- Path traversal prevention
- Overflow protection
"""

from __future__ import annotations

import hashlib
import inspect
import math
import os
import time
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# 1. SQL Injection Prevention Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestFieldBoundariesSQLInjection:
    """Test parameterized queries in field_boundaries."""

    def test_to_postgis_insert_returns_parameterized_query(self):
        """Verify to_postgis_insert returns (sql, params) tuple, not raw SQL."""
        from shared.field_boundaries.models import (
            BoundaryStatus,
            BoundaryType,
            FieldBoundary,
            Polygon,
        )

        boundary = FieldBoundary(
            id="test-id",
            field_id="field-1",
            tenant_id="tenant-1",
            owner_id="owner-1",
            name="Test Field",
            name_ar="حقل اختبار",
            boundary_type=BoundaryType.FIELD,
            status=BoundaryStatus.APPROVED,
            geometry=Polygon(
                coordinates=[[(46.0, 24.0), (46.1, 24.0), (46.1, 24.1), (46.0, 24.1), (46.0, 24.0)]],
            ),
            area_hectares=10.0,
            perimeter_meters=400.0,
        )

        result = boundary.to_postgis_insert()

        # Must return tuple (sql, params)
        assert isinstance(result, tuple), "Must return (sql, params) tuple"
        sql, params = result
        assert isinstance(sql, str)
        assert isinstance(params, list)

        # SQL must use $N placeholders, not f-string values
        assert "$1" in sql
        assert "$9" in sql  # geometry param
        assert "ST_GeomFromGeoJSON($9)" in sql

        # SQL must NOT contain literal values
        assert "test-id" not in sql
        assert "tenant-1" not in sql
        assert "field-1" not in sql

        # Params must contain actual values
        assert params[0] == "test-id"
        assert params[2] == "tenant-1"

    def test_to_postgis_insert_sql_injection_in_values(self):
        """Verify SQL injection payloads are safely parameterized."""
        from shared.field_boundaries.models import (
            BoundaryStatus,
            BoundaryType,
            FieldBoundary,
            Polygon,
        )

        malicious_name = "'; DROP TABLE fields; --"
        boundary = FieldBoundary(
            id="id-1",
            field_id="f-1",
            tenant_id="t-1",
            owner_id="o-1",
            name=malicious_name,
            name_ar="test",
            boundary_type=BoundaryType.FIELD,
            status=BoundaryStatus.APPROVED,
            geometry=Polygon(
                coordinates=[[(46.0, 24.0), (46.1, 24.0), (46.1, 24.1), (46.0, 24.1), (46.0, 24.0)]],
            ),
        )

        sql, params = boundary.to_postgis_insert()

        # Malicious string must be in params, NOT in SQL
        assert "DROP TABLE" not in sql
        assert malicious_name in params


class TestGeometryParameterizedQuery:
    """Test parameterized neighbor query in geometry module."""

    def test_neighbor_query_uses_parameter_placeholder(self):
        """Verify generate_postgis_neighbors_query uses $2 placeholder for buffer."""
        from shared.field_boundaries.geometry import generate_postgis_neighbors_query

        source = inspect.getsource(generate_postgis_neighbors_query)
        assert "$2" in source, "Buffer distance must use $2 parameter placeholder"
        # Should NOT have {buffer_m} f-string interpolation in SQL
        assert "{buffer_m}" not in source, "Must not use f-string for buffer_m"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. Command Injection Prevention Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestMCPClientExecutableValidation:
    """Test MCP client subprocess executable validation."""

    def test_rejects_nonexistent_executable(self):
        """Verify MCP client rejects unknown executables."""
        httpx = pytest.importorskip("httpx")  # noqa: F841
        from shared.mcp.client import MCPClient, MCPClientError

        with pytest.raises(MCPClientError, match="not found"):
            MCPClient(command=["/nonexistent/binary", "--arg"])

    def test_rejects_path_traversal_in_command(self):
        """Verify path traversal in command is rejected."""
        httpx = pytest.importorskip("httpx")  # noqa: F841
        from shared.mcp.client import MCPClient, MCPClientError

        with pytest.raises(MCPClientError, match="not found"):
            MCPClient(command=["../../etc/passwd"])

    def test_accepts_valid_executable(self):
        """Verify known executables are accepted."""
        httpx = pytest.importorskip("httpx")  # noqa: F841
        from shared.mcp.client import MCPClient

        # 'python3' should be findable
        client = MCPClient(command=["python3", "--version"])
        assert client.command is not None
        assert client.command[0].startswith("/")  # Resolved to absolute path


class TestDriftDetectionCommandAllowlist:
    """Test command allowlist in drift detection remediation."""

    def test_rejects_unauthorized_command(self):
        """Verify unapproved commands are blocked."""
        from shared.drift_detection.models import RemediationAction
        from shared.drift_detection.remediation import AutoRemediationEngine

        engine = AutoRemediationEngine(working_dir="/tmp")

        action = RemediationAction(
            id="test-1",
            command="rm -rf /",
            description="malicious",
        )

        import asyncio

        result = asyncio.get_event_loop().run_until_complete(
            engine._execute_auto_fix(action)
        )

        assert not result.success
        assert "not in allowed commands" in result.error

    def test_allows_approved_commands(self):
        """Verify approved commands pass the allowlist check."""
        from shared.drift_detection.remediation import AutoRemediationEngine

        engine = AutoRemediationEngine(working_dir="/tmp")

        # Check the allowlist contains expected tools
        assert "git" in engine._ALLOWED_COMMANDS
        assert "ruff" in engine._ALLOWED_COMMANDS
        assert "npm" in engine._ALLOWED_COMMANDS

        # Dangerous commands should NOT be in the allowlist
        assert "rm" not in engine._ALLOWED_COMMANDS
        assert "curl" not in engine._ALLOWED_COMMANDS
        assert "bash" not in engine._ALLOWED_COMMANDS
        assert "sh" not in engine._ALLOWED_COMMANDS


# ═══════════════════════════════════════════════════════════════════════════════
# 3. SSRF Prevention Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestLLMProviderSSRF:
    """Test SSRF prevention in LLM provider."""

    def test_rejects_file_protocol(self):
        """Verify file:// URLs are rejected."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        with pytest.raises(ValueError, match="http/https"):
            LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="test",
                base_url="file:///etc/passwd",
            )

    def test_rejects_ftp_protocol(self):
        """Verify ftp:// URLs are rejected."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        with pytest.raises(ValueError, match="http/https"):
            LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="test",
                base_url="ftp://evil.com/payload",
            )

    def test_rejects_gopher_protocol(self):
        """Verify gopher:// URLs are rejected."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        with pytest.raises(ValueError, match="http/https"):
            LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="test",
                base_url="gopher://evil.com/",
            )

    def test_accepts_http_url(self):
        """Verify http:// URLs are accepted."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="test",
            base_url="http://localhost:11434",
        )
        assert config.base_url == "http://localhost:11434"

    def test_accepts_https_url(self):
        """Verify https:// URLs are accepted."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        config = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="test",
            base_url="https://api.example.com",
        )
        assert config.base_url == "https://api.example.com"

    def test_accepts_none_url(self):
        """Verify None base_url is accepted."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        config = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="test",
            base_url=None,
        )
        assert config.base_url is None


class TestWeChatSSRF:
    """Test SSRF prevention in WeChat config."""

    def test_validates_mcp_url_scheme(self):
        """Verify non-http schemes are flagged."""
        structlog = pytest.importorskip("structlog")  # noqa: F841
        from shared.integrations.wechat.config import WeChatConfig

        config = WeChatConfig(mcp_url="file:///etc/passwd")
        errors = config.validate()

        assert any("http" in e.lower() or "https" in e.lower() for e in errors)

    def test_validates_mcp_url_hostname(self):
        """Verify missing hostname is flagged."""
        structlog = pytest.importorskip("structlog")  # noqa: F841
        from shared.integrations.wechat.config import WeChatConfig

        config = WeChatConfig(mcp_url="http://")
        errors = config.validate()

        assert any("hostname" in e.lower() for e in errors)

    def test_accepts_valid_http_url(self):
        """Verify valid HTTP URLs pass validation."""
        structlog = pytest.importorskip("structlog")  # noqa: F841
        from shared.integrations.wechat.config import WeChatConfig

        config = WeChatConfig(mcp_url="http://localhost:8765")
        errors = config.validate()

        # Should have no URL-related errors
        url_errors = [e for e in errors if "scheme" in e.lower() or "hostname" in e.lower()]
        assert len(url_errors) == 0

    def test_timeout_upper_bounds(self):
        """Verify timeout bounds are enforced."""
        structlog = pytest.importorskip("structlog")  # noqa: F841
        from shared.integrations.wechat.config import WeChatConfig

        config = WeChatConfig(connect_timeout=9999, read_timeout=9999)
        errors = config.validate()

        assert any("120" in e for e in errors)  # connect_timeout bound
        assert any("300" in e for e in errors)  # read_timeout bound


class TestNotificationRoutingSSRF:
    """Test SSRF prevention in notification routing."""

    def test_route_result_contains_service_name_not_url(self):
        """Verify routing results use service names, not full URLs."""
        from shared.notification_routing import (
            NotificationChannel,
            NotificationRouter,
        )

        router = NotificationRouter()
        service = router.get_service_endpoint(NotificationChannel.PUSH)

        # Should have service name and endpoint path, not full URL
        assert "service" in service
        assert "endpoint" in service
        assert service["service"] == "notification-service"
        assert service["endpoint"].startswith("/")


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Notification Preferences Tenant Isolation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestNotificationPreferencesTenantIsolation:
    """Test tenant isolation in notification preferences."""

    def test_tenant_id_required_in_storage_key(self):
        """Verify InMemoryStorage raises on empty tenant_id."""
        from shared.notification_preferences.manager import InMemoryStorage

        storage = InMemoryStorage()

        with pytest.raises(ValueError, match="tenant_id"):
            storage._key("user-1", "")

    @pytest.mark.asyncio
    async def test_get_requires_tenant_id(self):
        """Verify get() requires tenant_id parameter."""
        from shared.notification_preferences.manager import InMemoryStorage

        storage = InMemoryStorage()

        sig = inspect.signature(storage.get)
        params = list(sig.parameters.keys())
        assert "tenant_id" in params

        # tenant_id should not have a default value
        param = sig.parameters["tenant_id"]
        assert param.default is inspect.Parameter.empty, "tenant_id must be required (no default)"

    @pytest.mark.asyncio
    async def test_list_all_requires_tenant_id(self):
        """Verify list_all() requires tenant_id parameter."""
        from shared.notification_preferences.manager import InMemoryStorage

        storage = InMemoryStorage()

        sig = inspect.signature(storage.list_all)
        param = sig.parameters["tenant_id"]
        assert param.default is inspect.Parameter.empty, "tenant_id must be required"


# ═══════════════════════════════════════════════════════════════════════════════
# 5. CORS Security Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCORSCredentialsWithWildcard:
    """Test CORS credentials disabled with wildcard origins."""

    def test_setup_cors_disables_credentials_for_wildcard(self):
        """Verify setup_cors_middleware sets allow_credentials=False with '*'."""
        source_path = Path("shared/cors_config.py")
        content = source_path.read_text()

        # The setup_cors_middleware must contain the wildcard credentials guard
        assert '"*" not in origins' in content or "'*' not in origins" in content
        assert "allow_creds" in content

    def test_service_template_cors_guard(self):
        """Verify service template has CORS wildcard credentials guard."""
        template_path = Path("shared/templates/service_template.py")
        content = template_path.read_text()

        assert '"*" not in' in content or "'*' not in" in content


# ═══════════════════════════════════════════════════════════════════════════════
# 6. Error Information Disclosure Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestErrorInformationDisclosure:
    """Test that error responses don't leak internal details."""

    def test_create_error_response_structure(self):
        """Verify create_error_response returns safe JSON without internal details."""
        from shared.errors_py import ErrorCode, SahoolException, create_error_response

        exc = SahoolException(
            message="An unexpected error occurred",
            message_ar="حدث خطأ غير متوقع",
            code=ErrorCode.INTERNAL_ERROR,
            status_code=500,
        )

        response = create_error_response(exc)

        # Response should be a JSONResponse
        assert response.status_code == 500
        # Body should not contain internal Python exception class names
        body_text = response.body.decode() if hasattr(response, "body") else str(response)
        assert "TypeError" not in body_text
        assert "ValueError" not in body_text
        assert "KeyError" not in body_text
        assert "traceback" not in body_text.lower()


# ═══════════════════════════════════════════════════════════════════════════════
# 7. Division by Zero / Numeric Safety Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestPestScoutingDivisionByZero:
    """Test division by zero prevention in pest scouting."""

    def test_zero_threshold_after_modifiers_does_not_produce_inf(self):
        """Verify zero adj_action doesn't produce float('inf')."""
        from shared.pest_scouting.thresholds import assess_threshold

        # Use a known pest from the database but with growth_stage_modifier = 0
        # We test the guard by checking source code has the protection
        source = inspect.getsource(assess_threshold)

        # Must contain zero-threshold guard
        assert "adj_action <= 0" in source, "Must guard against zero adj_action"
        assert "adj_economic <= 0" in source, "Must guard against zero adj_economic"
        assert "999.9" in source, "Must cap percentage at 999.9"

    def test_assess_threshold_returns_capped_percentages(self):
        """Verify assess_threshold caps percentage values."""
        from shared.pest_scouting.models import CropType
        from shared.pest_scouting.thresholds import assess_threshold

        # Use a real pest from the threshold database — aphid on wheat
        result = assess_threshold(
            pest_id="APH001",
            crop_type=CropType.WHEAT,
            observed_value=5.0,
            growth_stage="seedling",
        )

        if result is not None:
            # Percentages must never be inf
            assert not math.isinf(result.percentage_of_action_threshold)
            assert not math.isinf(result.percentage_of_economic_threshold)
            assert result.percentage_of_action_threshold <= 999.9
            assert result.percentage_of_economic_threshold <= 999.9


class TestSalinitySARCalculation:
    """Test SAR calculation guards against division by zero."""

    def test_sar_with_zero_calcium_magnesium(self):
        """Verify SAR returns 0.0 when ca+mg <= 0."""
        from shared.salinity.module import calculate_sar

        result = calculate_sar(na=5.0, ca=0.0, mg=0.0)
        assert result == 0.0
        assert not math.isinf(result)
        assert not math.isnan(result)

    def test_sar_with_negative_inputs(self):
        """Verify SAR handles negative inputs safely."""
        from shared.salinity.module import calculate_sar

        result = calculate_sar(na=5.0, ca=-1.0, mg=0.5)
        assert result == 0.0

    def test_sar_with_valid_inputs(self):
        """Verify SAR calculates correctly with valid inputs."""
        from shared.salinity.module import calculate_sar

        result = calculate_sar(na=10.0, ca=4.0, mg=2.0)
        expected = 10.0 / math.sqrt((4.0 + 2.0) / 2.0)
        assert abs(result - expected) < 0.001


class TestEquipmentMaintenanceDivisionByZero:
    """Test equipment maintenance division by zero guard."""

    def test_expected_life_guard_exists(self):
        """Verify expected_life is guarded with max(..., 1) to prevent div/0."""
        from shared.equipment_maintenance.predictor import PredictiveMaintenanceEngine

        engine = PredictiveMaintenanceEngine(tenant_id="test-tenant")
        source = inspect.getsource(engine.assess_component_health)
        assert "max(" in source, "Expected life must be guarded with max()"


# ═══════════════════════════════════════════════════════════════════════════════
# 8. Soil Sensor Security Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestSoilSensorTenantIsolation:
    """Test sensor data tenant isolation."""

    def test_rejects_unregistered_sensor_readings(self):
        """Verify readings from unregistered sensors are ignored."""
        from shared.soil_sensors.models import SensorReading, SensorType
        from shared.soil_sensors.processor import SensorDataProcessor

        processor = SensorDataProcessor(field_id="field-1", tenant_id="tenant-1")

        # Don't register any sensor — reading should be silently dropped
        reading = SensorReading(
            sensor_id="unregistered-sensor",
            reading_type=SensorType.MOISTURE,
            value=50.0,
            unit="percent",
            timestamp=datetime.now(UTC),
        )

        alerts = processor.add_reading(reading)

        # Should return empty — reading rejected
        assert alerts == []
        assert "unregistered-sensor" not in processor._readings

    def test_accepts_registered_sensor_readings(self):
        """Verify readings from registered sensors are accepted."""
        from shared.soil_sensors.models import (
            SensorProtocol,
            SensorReading,
            SensorType,
            SoilSensor,
        )
        from shared.soil_sensors.processor import SensorDataProcessor

        processor = SensorDataProcessor(field_id="field-1", tenant_id="tenant-1")
        processor.register_sensor(
            SoilSensor(
                id="sensor-1",
                tenant_id="tenant-1",
                field_id="field-1",
                name="Test Sensor",
                name_ar="مجس اختبار",
                sensor_type=SensorType.MOISTURE,
                protocol=SensorProtocol.MQTT,
                model="CropX-100",
                manufacturer="CropX",
                lat=24.7,
                lng=46.7,
            )
        )

        reading = SensorReading(
            sensor_id="sensor-1",
            reading_type=SensorType.MOISTURE,
            value=45.0,
            unit="percent",
            timestamp=datetime.now(UTC),
        )

        processor.add_reading(reading)
        assert "sensor-1" in processor._readings


class TestSoilSensorOverflowProtection:
    """Test Z-score overflow protection."""

    def test_extreme_values_clamped_in_check_anomaly(self):
        """Verify extreme sensor values are clamped in anomaly check to prevent overflow."""
        from shared.soil_sensors.processor import SensorDataProcessor

        # The clamping logic is in _check_anomaly which is called by add_reading
        source = inspect.getsource(SensorDataProcessor._check_anomaly)
        assert "max(" in source or "min(" in source or "1e6" in source, (
            "Values must be clamped in _check_anomaly to prevent Z-score overflow"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 9. Path Traversal Prevention Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAgMLPathTraversal:
    """Test path traversal prevention in AgML."""

    def test_rejects_path_outside_allowed_dirs(self):
        """Verify cache_dir outside /tmp or /var/cache is rejected."""
        pytest.importorskip("structlog")
        from shared.ml.agml_integration import AgMLDatasetManager

        with pytest.raises(ValueError, match="cache_dir must be under"):
            AgMLDatasetManager(cache_dir="/etc/evil")

    def test_rejects_path_traversal_attack(self):
        """Verify path traversal sequences are blocked."""
        pytest.importorskip("structlog")
        from shared.ml.agml_integration import AgMLDatasetManager

        with pytest.raises(ValueError, match="cache_dir must be under"):
            AgMLDatasetManager(cache_dir="/tmp/../etc/passwd")

    def test_accepts_valid_tmp_path(self):
        """Verify /tmp paths are accepted."""
        pytest.importorskip("structlog")
        from shared.ml.agml_integration import AgMLDatasetManager

        manager = AgMLDatasetManager(cache_dir="/tmp/agml-test")
        assert str(manager.cache_dir).startswith("/tmp/")


# ═══════════════════════════════════════════════════════════════════════════════
# 10. Rate Limiter Security Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestRateLimiterFailClosed:
    """Test rate limiter fails closed when Redis is unavailable."""

    def test_in_memory_fallback_enforces_limits(self):
        """Verify in-memory fallback actually rate-limits."""
        try:
            from apps.kernel.common.middleware.rate_limiter import (
                EndpointConfig,
                FixedWindowLimiter,
            )
        except (ImportError, ModuleNotFoundError):
            pytest.skip("apps.kernel not on PYTHONPATH")
            return

        limiter = FixedWindowLimiter(redis_client=None)

        config = EndpointConfig(
            requests=3,
            period=60,
        )

        # Simulate Redis failure — should use in-memory fallback
        results = []
        for _ in range(5):
            allowed, remaining, _ = limiter._in_memory_check("client-1", "/test", config)
            results.append(allowed)

        # First 3 should be allowed, 4th and 5th should be blocked
        assert results[:3] == [True, True, True]
        assert results[3] is False
        assert results[4] is False

    def test_api_key_hash_no_truncation(self):
        """Verify API key hash uses full SHA-256, not truncated."""
        try:
            from apps.kernel.common.middleware.rate_limiter import ClientIdentifier
        except (ImportError, ModuleNotFoundError):
            pytest.skip("apps.kernel not on PYTHONPATH")
            return

        mock_request = MagicMock()
        mock_request.headers = {"X-API-Key": "test-api-key-12345"}
        mock_request.state = MagicMock(spec=[])  # No user_id attribute
        mock_request.client = MagicMock()
        mock_request.client.host = "127.0.0.1"

        client_id = ClientIdentifier.get_client_id(mock_request)

        # Full SHA-256 hash should be 64 chars
        expected_hash = hashlib.sha256(b"test-api-key-12345").hexdigest()
        assert client_id == f"apikey:{expected_hash}"
        assert len(expected_hash) == 64  # Full hash, not truncated


# ═══════════════════════════════════════════════════════════════════════════════
# 11. HMAC Secret Validation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestHMACSecretValidation:
    """Test HMAC secret length enforcement (TypeScript tested via source check)."""

    def test_hmac_secret_minimum_length_documented(self):
        """Verify HMAC secret validation exists in hash-utils.ts."""
        hash_utils_path = Path("packages/shared-crypto/src/hash-utils.ts")
        content = hash_utils_path.read_text()

        assert "secret.length < 64" in content, "Must enforce 64-char minimum"
        assert "32 bytes" in content, "Error message must mention 32 bytes"


# ═══════════════════════════════════════════════════════════════════════════════
# 12. Cooperative Tenant Isolation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCooperativeTenantIsolation:
    """Test tenant isolation in cooperative financial statements."""

    @pytest.mark.asyncio
    async def test_get_member_statement_requires_cooperative_id(self):
        """Verify get_member_statement requires requesting_cooperative_id."""
        from shared.cooperatives.revenue import RevenueService

        service = RevenueService(cooperative_id="coop-1")

        sig = inspect.signature(service.get_member_statement)
        assert "requesting_cooperative_id" in sig.parameters

    @pytest.mark.asyncio
    async def test_omitted_cooperative_id_denied(self):
        """Verify omitting requesting_cooperative_id defaults to '' and is denied."""
        from shared.cooperatives.revenue import RevenueService

        service = RevenueService(cooperative_id="coop-1")

        # Default value is "" which never matches a real cooperative_id
        with pytest.raises(PermissionError, match="different cooperative"):
            await service.get_member_statement(member_id="member-1")

    @pytest.mark.asyncio
    async def test_cross_cooperative_access_denied(self):
        """Verify cross-cooperative financial access is blocked."""
        from shared.cooperatives.revenue import RevenueService

        service = RevenueService(cooperative_id="coop-1")

        with pytest.raises(PermissionError, match="different cooperative"):
            await service.get_member_statement(
                member_id="member-1",
                requesting_cooperative_id="coop-2",  # Different cooperative!
            )

    @pytest.mark.asyncio
    async def test_same_cooperative_access_allowed(self):
        """Verify same-cooperative access succeeds."""
        from shared.cooperatives.revenue import RevenueService

        service = RevenueService(cooperative_id="coop-1")

        # Should not raise — same cooperative
        result = await service.get_member_statement(
            member_id="member-1",
            requesting_cooperative_id="coop-1",
        )
        assert isinstance(result, dict)
        assert result["member_id"] == "member-1"


# ═══════════════════════════════════════════════════════════════════════════════
# 13. Service Template Security Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestServiceTemplateSecurity:
    """Test security fixes in service template."""

    def test_no_sys_path_manipulation(self):
        """Verify service template doesn't use sys.path.insert."""
        template_path = Path("shared/templates/service_template.py")
        content = template_path.read_text()

        assert "sys.path.insert" not in content
        assert "sys.path.append" not in content

    def test_uses_proper_shared_imports(self):
        """Verify template uses shared.xxx imports."""
        template_path = Path("shared/templates/service_template.py")
        content = template_path.read_text()

        assert "from shared.middleware" in content
        assert "from shared.security" in content
        assert "from shared.observability" in content

    def test_cors_credentials_wildcard_guard(self):
        """Verify CORS credentials are guarded against wildcard."""
        template_path = Path("shared/templates/service_template.py")
        content = template_path.read_text()

        assert '"*" not in' in content or "'*' not in" in content


# ═══════════════════════════════════════════════════════════════════════════════
# 14. Audit Middleware Sensitive Parameter Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuditMiddlewareSanitization:
    """Test sensitive query parameter sanitization in audit middleware."""

    def test_sanitize_query_exists_in_middleware(self):
        """Verify sanitizeQuery method exists in audit middleware."""
        middleware_path = Path("packages/shared-audit/src/audit-middleware.ts")
        content = middleware_path.read_text()

        assert "sanitizeQuery" in content
        assert "SENSITIVE_PARAMS" in content
        assert "[REDACTED]" in content

    def test_sensitive_params_list_complete(self):
        """Verify all common sensitive params are in the blocklist."""
        middleware_path = Path("packages/shared-audit/src/audit-middleware.ts")
        content = middleware_path.read_text()

        for param in ["token", "api_key", "secret", "password", "access_token", "refresh_token"]:
            assert param in content, f"Missing sensitive param: {param}"
