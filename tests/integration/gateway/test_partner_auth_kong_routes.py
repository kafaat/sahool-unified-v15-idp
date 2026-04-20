"""Validation tests for Kong declarative config — partner-auth routes.

These tests ensure the kong.yml declaration stays in sync with the
contracts (service port, endpoint paths) even if someone forgets to
update one of them.

Run:
    pytest tests/integration/gateway/test_partner_auth_kong_routes.py -v
"""

from __future__ import annotations

import pathlib
from typing import Any, Dict, List

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[3]
KONG_CONFIG = REPO_ROOT / "infrastructure" / "gateway" / "kong" / "active" / "kong.yml"


@pytest.fixture(scope="module")
def kong_config() -> dict[str, Any]:
    """Load and parse the active Kong config once per test module."""
    assert KONG_CONFIG.exists(), f"Kong config not found at {KONG_CONFIG}"
    with KONG_CONFIG.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh)


@pytest.fixture(scope="module")
def partner_auth_services(kong_config: dict[str, Any]) -> list[dict[str, Any]]:
    """Return every Kong service block whose host=partner-auth-service."""
    services = kong_config.get("services", [])
    return [s for s in services if s.get("host") == "partner-auth-service"]


class TestPartnerAuthServiceBlock:
    """The docker-compose container `partner-auth-service` on port 3030
    must be reachable via at least one Kong `services:` entry."""

    def test_at_least_one_partner_auth_service_declared(self, partner_auth_services):
        assert len(partner_auth_services) >= 4, (
            "Expected at least 4 service blocks for partner-auth "
            "(oauth-public, wellknown, admin, health); "
            f"found {len(partner_auth_services)}"
        )

    def test_all_point_to_port_3030(self, partner_auth_services):
        for svc in partner_auth_services:
            assert svc["port"] == 3030, (
                f"Service {svc['name']} points to port {svc['port']}; "
                "contract says PARTNER_AUTH = 3030"
            )

    def test_all_use_http_protocol(self, partner_auth_services):
        for svc in partner_auth_services:
            assert svc["protocol"] == "http"


class TestPartnerAuthRoutes:
    """Every contract endpoint must have at least one matching Kong route."""

    # Mirror of the TS contract constants (kept in sync manually — this
    # test exists precisely to catch drift).
    EXPECTED_OAUTH_PATHS = {
        "/partner/v1/oauth/token",
        "/partner/v1/oauth/authorize",
        "/partner/v1/oauth/revoke",
        "/partner/v1/oauth/introspect",
        "/partner/v1/oauth/userinfo",
    }
    EXPECTED_WELLKNOWN_PATHS = {
        "/.well-known/openid-configuration",
        "/.well-known/jwks.json",
    }
    EXPECTED_ADMIN_PREFIX = "/api/v1/admin/partner-auth"

    def _collect_paths(self, services: list[dict[str, Any]]) -> set[str]:
        paths: set[str] = set()
        for svc in services:
            for route in svc.get("routes", []):
                for path in route.get("paths", []):
                    paths.add(path)
        return paths

    def test_all_oauth_paths_routed(self, partner_auth_services):
        paths = self._collect_paths(partner_auth_services)
        missing = self.EXPECTED_OAUTH_PATHS - paths
        assert not missing, f"Kong config missing OAuth routes: {missing}"

    def test_all_wellknown_paths_routed(self, partner_auth_services):
        paths = self._collect_paths(partner_auth_services)
        missing = self.EXPECTED_WELLKNOWN_PATHS - paths
        assert not missing, (
            f"Kong config missing well-known routes: {missing}. "
            "OIDC discovery + JWKS must be public and cached."
        )

    def test_admin_prefix_routed(self, partner_auth_services):
        paths = self._collect_paths(partner_auth_services)
        assert any(
            p.startswith(self.EXPECTED_ADMIN_PREFIX) for p in paths
        ), f"No Kong route matches admin prefix {self.EXPECTED_ADMIN_PREFIX}"

    def test_health_endpoints_routed(self, partner_auth_services):
        paths = self._collect_paths(partner_auth_services)
        assert "/healthz" in paths and "/readyz" in paths, (
            "K8s liveness/readiness probes must route to partner-auth"
        )


class TestSecurityPlugins:
    """Security-critical plugin attachments."""

    def test_token_route_has_rate_limiting(self, partner_auth_services):
        """The /token endpoint is the highest-value attack surface (credential
        stuffing) — it must have rate-limiting attached."""
        for svc in partner_auth_services:
            for route in svc.get("routes", []):
                if "/partner/v1/oauth/token" in route.get("paths", []):
                    plugins = route.get("plugins", []) or []
                    names = {p.get("name") for p in plugins}
                    assert "rate-limiting" in names, (
                        "/partner/v1/oauth/token MUST have rate-limiting plugin"
                    )
                    return
        pytest.fail("No route matched /partner/v1/oauth/token")

    def test_admin_routes_require_jwt(self, partner_auth_services):
        """Defense-in-depth: admin routes should require JWT at Kong layer
        even though AdminGuard enforces role=ADMIN in the service."""
        for svc in partner_auth_services:
            if svc["name"] != "partner-auth-admin":
                continue
            plugins = svc.get("plugins", []) or []
            names = {p.get("name") for p in plugins}
            assert "jwt" in names, (
                "partner-auth-admin service must have `jwt` plugin attached"
            )
            assert "rate-limiting" in names, (
                "partner-auth-admin service must have rate-limiting"
            )
            return
        pytest.fail("No service block named 'partner-auth-admin'")

    def test_wellknown_endpoints_cached(self, partner_auth_services):
        """JWKS and OIDC discovery are static for hours at a time — must
        use proxy-cache to reduce load on partner-auth-service."""
        for svc in partner_auth_services:
            if svc["name"] != "partner-auth-wellknown":
                continue
            for route in svc.get("routes", []):
                plugins = route.get("plugins", []) or []
                names = {p.get("name") for p in plugins}
                assert "proxy-cache" in names, (
                    f"Well-known route {route['name']} must have proxy-cache"
                )
            return
        pytest.fail("No service block named 'partner-auth-wellknown'")


class TestRoutesDoNotLeak:
    """Kong must NOT expose internal-only paths."""

    def test_no_admin_ui_routed_yet(self, kong_config):
        """The /api/v1/admin/partner-auth/ui path (future branch) must NOT
        be routed until the admin UI ships."""
        services = kong_config.get("services", [])
        paths: set[str] = set()
        for svc in services:
            for route in svc.get("routes", []):
                for path in route.get("paths", []):
                    paths.add(path)
        assert "/api/v1/admin/partner-auth/ui" not in paths, (
            "Admin UI path leaked into Kong — should be added only in "
            "claude/wave1-partner-portal-ui"
        )
