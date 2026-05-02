"""
Kong gateway health-route consistency tests.
اختبارات مسارات Kong لفحوصات الصحة

Kong forwards requests to upstream services. For our health-probe routes
(`/api/v1/<x>/healthz`, `/api/v1/<x>/readyz`), upstream services mount
`/healthz` and `/readyz` at the container root (Python services directly,
NestJS services via `setGlobalPrefix("api/v1", { exclude: ["healthz", ...] })`).

Therefore Kong health routes whose paths begin with `/api/v1/` MUST set
`strip_path: true` so the prefix is removed before forwarding to upstream.
A `strip_path: false` on such a route forwards the full unstripped path
to the upstream, which 404s — silently breaking K8s probes and external
monitoring.

This regression test asserts that invariant.
"""

from __future__ import annotations

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent.parent
KONG_YAML = PROJECT_ROOT / "infrastructure" / "gateway" / "kong" / "active" / "kong.yml"


def _load_kong_health_routes() -> list[dict]:
    """
    Return all Kong route entries whose name ends with '-health-route'.

    Each entry is a dict with: service_name, route_name, paths, strip_path.
    """
    yaml = pytest.importorskip("yaml")

    if not KONG_YAML.exists():
        pytest.skip(f"kong.yml not found at {KONG_YAML}")

    config = yaml.safe_load(KONG_YAML.read_text())
    services = config.get("services") or []

    health_routes: list[dict] = []
    for svc in services:
        for route in svc.get("routes") or []:
            rname = route.get("name", "")
            if not rname.endswith("-health-route"):
                continue
            health_routes.append(
                {
                    "service_name": svc.get("name", ""),
                    "route_name": rname,
                    "paths": list(route.get("paths") or []),
                    "strip_path": route.get("strip_path"),
                }
            )
    return health_routes


HEALTH_ROUTES = _load_kong_health_routes()
HEALTH_ROUTE_IDS = [r["route_name"] for r in HEALTH_ROUTES]


@pytest.mark.unit
class TestKongHealthRoutes:
    """Kong health-route invariants."""

    def test_health_routes_discovered(self):
        """Sanity: kong.yml exposes a non-trivial number of health routes."""
        assert len(HEALTH_ROUTES) >= 20, (
            f"Expected at least 20 *-health-route entries in kong.yml, found {len(HEALTH_ROUTES)}"
        )

    @pytest.mark.parametrize("route", HEALTH_ROUTES, ids=HEALTH_ROUTE_IDS)
    def test_health_route_strip_path_matches_path_prefix(self, route: dict):
        """
        Health routes whose paths start with /api/v1/ must use strip_path: true.
        Routes whose paths are bare /healthz (no prefix) must use strip_path: false.

        Mismatch causes Kong to forward an unstripped path to an upstream that
        only knows /healthz at root → 404.
        """
        paths = route["paths"]
        strip_path = route["strip_path"]
        rname = route["route_name"]

        assert paths, f"{rname}: no paths defined"

        api_v1_paths = [p for p in paths if p.startswith("/api/v1/")]
        bare_paths = [p for p in paths if not p.startswith("/api/v1/")]

        if api_v1_paths and not bare_paths:
            # All paths are prefixed → must strip the prefix
            assert strip_path is True, (
                f"{rname}: paths {api_v1_paths} are under /api/v1/<x>/ but strip_path={strip_path!r}. "
                f"Upstream services mount /healthz and /readyz at root; without strip_path:true, "
                f"Kong forwards the unstripped path and the probe 404s."
            )
        elif bare_paths and not api_v1_paths:
            # Bare paths → must NOT strip (would leave nothing)
            assert strip_path is False, (
                f"{rname}: paths {bare_paths} are bare; strip_path:true would strip them entirely."
            )
        # Mixed paths are not currently used; if introduced, decide explicitly per route.

    @pytest.mark.parametrize("route", HEALTH_ROUTES, ids=HEALTH_ROUTE_IDS)
    def test_health_route_paths_are_health_endpoints(self, route: dict):
        """Every path on a *-health-route must end with /healthz, /readyz, or /health."""
        valid_suffixes = ("/healthz", "/readyz", "/health")
        for p in route["paths"]:
            assert p.endswith(valid_suffixes), (
                f"{route['route_name']}: path {p!r} does not look like a health endpoint"
            )
