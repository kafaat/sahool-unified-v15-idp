"""
Integration Tests for Kong API Gateway Routes
اختبارات التكامل لمسارات Kong API Gateway

These tests verify that Kong routes are properly configured
and accessible for the SAHOOL platform services.
"""

import os
from pathlib import Path

import pytest
import yaml

# ═══════════════════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════════════════

KONG_CONFIG_PATH = Path(__file__).parent.parent.parent / "infra" / "kong" / "kong.yml"
KONG_GATEWAY_CONFIG_PATH = (
    Path(__file__).parent.parent.parent / "infrastructure" / "gateway" / "kong" / "kong.yml"
)


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture
def kong_config():
    """Load Kong configuration from YAML file."""
    with open(KONG_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture
def kong_gateway_config():
    """Load Kong gateway configuration from YAML file."""
    with open(KONG_GATEWAY_CONFIG_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


# ═══════════════════════════════════════════════════════════════════════════
# Tests - Kong Configuration Structure
# ═══════════════════════════════════════════════════════════════════════════


class TestKongConfigStructure:
    """Test Kong configuration structure and required sections."""

    def test_config_format_version(self, kong_config):
        """Verify Kong config has correct format version."""
        assert kong_config.get("_format_version") == "3.0"

    def test_config_has_services(self, kong_config):
        """Verify Kong config has services defined."""
        assert "services" in kong_config
        assert len(kong_config["services"]) > 0

    def test_config_has_upstreams(self, kong_config):
        """Verify Kong config has upstreams defined."""
        assert "upstreams" in kong_config
        assert len(kong_config["upstreams"]) > 0

    def test_config_has_plugins(self, kong_config):
        """Verify Kong config has global plugins defined."""
        assert "plugins" in kong_config
        assert len(kong_config["plugins"]) > 0

    def test_config_has_consumers(self, kong_config):
        """Verify Kong config has consumers defined."""
        assert "consumers" in kong_config
        assert len(kong_config["consumers"]) > 0

    def test_config_has_acls(self, kong_config):
        """Verify Kong config has ACL groups defined."""
        assert "acls" in kong_config
        assert len(kong_config["acls"]) > 0


# ═══════════════════════════════════════════════════════════════════════════
# Tests - Required Services
# ═══════════════════════════════════════════════════════════════════════════


class TestRequiredServices:
    """Test that all required services are configured."""

    REQUIRED_SERVICES = [
        "field-core",
        "weather-core",
        "astronomical-calendar",
        "notification-service",
        "satellite-service",
        "ndvi-engine",
        "crop-health-ai",
        "ai-advisor",
        "field-intelligence",
    ]

    def test_required_services_exist(self, kong_config):
        """Verify all required services are defined."""
        service_names = [s["name"] for s in kong_config["services"]]
        for required_service in self.REQUIRED_SERVICES:
            assert required_service in service_names, f"Missing service: {required_service}"

    def test_services_have_routes(self, kong_config):
        """Verify all services have at least one route."""
        for service in kong_config["services"]:
            assert "routes" in service, f"Service {service['name']} missing routes"
            assert len(service["routes"]) > 0, f"Service {service['name']} has no routes"

    def test_services_have_valid_urls_or_hosts(self, kong_config):
        """Verify all services have valid URL or host configuration."""
        for service in kong_config["services"]:
            has_url = "url" in service
            has_host = "host" in service
            assert has_url or has_host, f"Service {service['name']} missing url or host"


# ═══════════════════════════════════════════════════════════════════════════
# Tests - Astronomical Calendar Routes
# ═══════════════════════════════════════════════════════════════════════════


class TestAstronomicalCalendarRoutes:
    """Test astronomical calendar service routes for backward compatibility."""

    def test_astronomical_calendar_exists(self, kong_config):
        """Verify astronomical-calendar service exists."""
        service_names = [s["name"] for s in kong_config["services"]]
        assert "astronomical-calendar" in service_names

    def test_astronomical_calendar_has_dual_paths(self, kong_config):
        """Verify astronomical-calendar supports both paths for backward compatibility."""
        for service in kong_config["services"]:
            if service["name"] == "astronomical-calendar":
                for route in service["routes"]:
                    if route["name"] == "astronomical-calendar-route":
                        paths = route.get("paths", [])
                        assert "/api/v1/astronomical" in paths, "Missing /api/v1/astronomical path"
                        assert "/api/v1/calendar" in paths, "Missing /api/v1/calendar path"
                        return
        pytest.fail("astronomical-calendar-route not found")


# ═══════════════════════════════════════════════════════════════════════════
# Tests - Security Plugins
# ═══════════════════════════════════════════════════════════════════════════


class TestSecurityPlugins:
    """Test security-related plugins configuration."""

    def test_cors_plugin_configured(self, kong_config):
        """Verify CORS plugin is configured globally."""
        plugin_names = [p["name"] for p in kong_config["plugins"]]
        assert "cors" in plugin_names

    def test_cors_allows_localhost(self, kong_config):
        """Verify CORS allows localhost for development."""
        for plugin in kong_config["plugins"]:
            if plugin["name"] == "cors":
                origins = plugin["config"].get("origins", [])
                assert any("localhost" in o for o in origins), "CORS should allow localhost"
                return
        pytest.fail("CORS plugin not found")

    def test_security_headers_configured(self, kong_config):
        """Verify security headers are configured."""
        for plugin in kong_config["plugins"]:
            if plugin["name"] == "response-transformer":
                headers = plugin["config"].get("add", {}).get("headers", [])
                header_str = " ".join(headers)
                assert "X-Frame-Options" in header_str, "Missing X-Frame-Options header"
                assert "X-Content-Type-Options" in header_str, (
                    "Missing X-Content-Type-Options header"
                )
                assert "X-XSS-Protection" in header_str, "Missing X-XSS-Protection header"
                return
        pytest.fail("response-transformer plugin not found")

    def test_prometheus_plugin_enabled(self, kong_config):
        """Verify Prometheus metrics plugin is enabled."""
        plugin_names = [p["name"] for p in kong_config["plugins"]]
        assert "prometheus" in plugin_names

    def test_correlation_id_plugin_enabled(self, kong_config):
        """Verify correlation ID plugin is enabled."""
        plugin_names = [p["name"] for p in kong_config["plugins"]]
        assert "correlation-id" in plugin_names


# ═══════════════════════════════════════════════════════════════════════════
# Tests - Rate Limiting
# ═══════════════════════════════════════════════════════════════════════════


class TestRateLimiting:
    """Test rate limiting configuration."""

    def test_services_have_rate_limiting(self, kong_config):
        """Verify services have rate limiting plugins."""
        services_with_rate_limit = 0
        for service in kong_config["services"]:
            plugins = service.get("plugins", [])
            for plugin in plugins:
                if plugin.get("name") == "rate-limiting":
                    services_with_rate_limit += 1
                    break

        # Most services should have rate limiting
        total_services = len(kong_config["services"])
        assert services_with_rate_limit > total_services * 0.8, (
            f"Only {services_with_rate_limit}/{total_services} services have rate limiting"
        )

    def test_rate_limiting_uses_redis(self, kong_config):
        """Verify rate limiting uses Redis policy."""
        for service in kong_config["services"]:
            plugins = service.get("plugins", [])
            for plugin in plugins:
                if plugin.get("name") == "rate-limiting":
                    config = plugin.get("config", {})
                    assert config.get("policy") == "redis", (
                        f"Service {service['name']} should use Redis for rate limiting"
                    )


# ═══════════════════════════════════════════════════════════════════════════
# Tests - ACL Configuration
# ═══════════════════════════════════════════════════════════════════════════


class TestACLConfiguration:
    """Test ACL (Access Control List) configuration."""

    EXPECTED_USER_GROUPS = [
        "starter-users",
        "professional-users",
        "enterprise-users",
        "research-users",
        "admin-users",
    ]

    def test_all_user_groups_defined(self, kong_config):
        """Verify all expected user groups are defined in ACLs."""
        acl_groups = [acl["group"] for acl in kong_config["acls"]]
        for group in self.EXPECTED_USER_GROUPS:
            assert group in acl_groups, f"Missing ACL group: {group}"

    def test_consumers_have_jwt_secrets(self, kong_config):
        """Verify consumers have JWT secrets configured."""
        for consumer in kong_config["consumers"]:
            assert "jwt_secrets" in consumer, f"Consumer {consumer['username']} missing jwt_secrets"
            assert len(consumer["jwt_secrets"]) > 0, (
                f"Consumer {consumer['username']} has no jwt_secrets"
            )


# ═══════════════════════════════════════════════════════════════════════════
# Tests - Field Intelligence Service
# ═══════════════════════════════════════════════════════════════════════════


class TestFieldIntelligenceService:
    """Test field-intelligence service configuration."""

    def test_field_intelligence_exists(self, kong_config):
        """Verify field-intelligence service exists."""
        service_names = [s["name"] for s in kong_config["services"]]
        assert "field-intelligence" in service_names

    def test_field_intelligence_has_correct_port(self, kong_config):
        """Verify field-intelligence uses correct port."""
        for service in kong_config["services"]:
            if service["name"] == "field-intelligence":
                url = service.get("url", "")
                assert "8119" in url, "field-intelligence should use port 8119"
                return
        pytest.fail("field-intelligence service not found")

    def test_field_intelligence_requires_professional_access(self, kong_config):
        """Verify field-intelligence requires at least professional access."""
        for service in kong_config["services"]:
            if service["name"] == "field-intelligence":
                for plugin in service.get("plugins", []):
                    if plugin.get("name") == "acl":
                        allowed = plugin["config"].get("allow", [])
                        assert "professional-users" in allowed or "enterprise-users" in allowed
                        return
        pytest.fail("field-intelligence ACL configuration not found")


# ═══════════════════════════════════════════════════════════════════════════
# Tests - Configuration Consistency
# ═══════════════════════════════════════════════════════════════════════════


class TestConfigurationConsistency:
    """Test consistency between Kong configuration files."""

    def test_both_configs_have_same_format_version(self, kong_config, kong_gateway_config):
        """Verify both configs use the same format version."""
        assert kong_config.get("_format_version") == kong_gateway_config.get("_format_version")

    def test_both_configs_have_astronomical_calendar(self, kong_config, kong_gateway_config):
        """Verify both configs have astronomical-calendar service."""
        names1 = [s["name"] for s in kong_config["services"]]
        names2 = [s["name"] for s in kong_gateway_config["services"]]
        assert "astronomical-calendar" in names1
        assert "astronomical-calendar" in names2

    def test_both_configs_have_field_intelligence(self, kong_config, kong_gateway_config):
        """Verify both configs have field-intelligence service."""
        names1 = [s["name"] for s in kong_config["services"]]
        names2 = [s["name"] for s in kong_gateway_config["services"]]
        assert "field-intelligence" in names1
        assert "field-intelligence" in names2


# ═══════════════════════════════════════════════════════════════════════════
# Tests - Health Check Endpoint
# ═══════════════════════════════════════════════════════════════════════════


class TestHealthCheckEndpoint:
    """Test health check endpoint configuration."""

    def test_health_check_service_exists(self, kong_config):
        """Verify health-check service exists."""
        service_names = [s["name"] for s in kong_config["services"]]
        assert "health-check" in service_names

    def test_health_check_returns_200(self, kong_config):
        """Verify health-check returns 200 status code."""
        for service in kong_config["services"]:
            if service["name"] == "health-check":
                for plugin in service.get("plugins", []):
                    if plugin.get("name") == "request-termination":
                        assert plugin["config"]["status_code"] == 200
                        return
        pytest.fail("health-check request-termination plugin not found")


# ═══════════════════════════════════════════════════════════════════════════
# Tests - Root Endpoint
# ═══════════════════════════════════════════════════════════════════════════


class TestRootEndpoint:
    """Test root endpoint configuration."""

    def test_root_endpoint_service_exists(self, kong_config):
        """Verify root-endpoint service exists."""
        service_names = [s["name"] for s in kong_config["services"]]
        assert "root-endpoint" in service_names

    def test_root_endpoint_has_slash_path(self, kong_config):
        """Verify root-endpoint has / path configured."""
        for service in kong_config["services"]:
            if service["name"] == "root-endpoint":
                for route in service.get("routes", []):
                    paths = route.get("paths", [])
                    assert "/" in paths, "root-endpoint should have / path"
                    return
        pytest.fail("root-endpoint route not found")

    def test_root_endpoint_returns_json(self, kong_config):
        """Verify root-endpoint returns JSON response."""
        for service in kong_config["services"]:
            if service["name"] == "root-endpoint":
                for plugin in service.get("plugins", []):
                    if plugin.get("name") == "request-termination":
                        config = plugin.get("config", {})
                        assert config.get("status_code") == 200
                        assert config.get("content_type") == "application/json"
                        assert "body" in config
                        return
        pytest.fail("root-endpoint request-termination plugin not found")

    def test_root_endpoint_contains_platform_info(self, kong_config):
        """Verify root-endpoint contains SAHOOL platform information."""
        for service in kong_config["services"]:
            if service["name"] == "root-endpoint":
                for plugin in service.get("plugins", []):
                    if plugin.get("name") == "request-termination":
                        body = plugin["config"].get("body", "")
                        assert "SAHOOL" in body
                        assert "version" in body
                        assert "16.0.0" in body
                        return
        pytest.fail("root-endpoint body not found")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
