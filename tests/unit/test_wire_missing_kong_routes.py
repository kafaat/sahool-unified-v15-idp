"""
Regression tests for the Kong routes added in PR
`claude/wire-missing-kong-routes`.

Every path below has a matching `@Controller("api/v1/...")` NestJS
controller in field-management-service — the backends have been running
all along, but Kong didn't declare the path, so every request 404'd at
the gateway. The audit caught this because web/admin/mobile were calling
these paths (FARM_ENDPOINTS alone has 256+ references across apps/web).

These unit tests are file-level assertions: they load kong.yml and
assert the specific paths live on the field-management-service route
with `strip_path: false` (so the full /api/v1/... URL is forwarded to
the backend's @Controller prefix).
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
KONG_ACTIVE = REPO_ROOT / "infrastructure" / "gateway" / "kong" / "active" / "kong.yml"

pytestmark = [pytest.mark.unit]


@pytest.fixture(scope="module")
def kong_config() -> dict:
    if not KONG_ACTIVE.exists():
        pytest.skip(f"Kong config not found at {KONG_ACTIVE}")
    with open(KONG_ACTIVE, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class TestFieldManagementMissingKongRoutes:
    """Each of these paths has a live backend controller on
    field-management-service (port 3000). Adding the path to the Kong
    route is enough to unblock every affected client — no backend or
    contract change needed.
    """

    def _field_management_route(self, kong_config: dict) -> dict:
        for svc in kong_config.get("services", []):
            if svc.get("name") == "field-management-service":
                for route in svc.get("routes", []):
                    if route.get("name") == "field-management-service-route":
                        return route
        pytest.fail("field-management-service-route not found in kong.yml")

    @pytest.mark.parametrize(
        "path,backend_controller",
        [
            ("/api/v1/farms", "farms/farms.controller.ts"),
            ("/api/v1/field-operations", "field-operations/field-operations.controller.ts"),
            ("/api/v1/field-reports", "field-reports/field-reports.controller.ts"),
            ("/api/v1/field-sub-zones", "field-sub-zones/field-sub-zones.controller.ts"),
            ("/api/v1/erp-sync", "erp-sync/erp-sync.controller.ts"),
        ],
    )
    def test_path_is_routed(self, kong_config, path, backend_controller):
        """Kong MUST route `path` → field-management-service, otherwise
        the backend controller at `backend_controller` is unreachable
        externally despite being fully implemented."""
        route = self._field_management_route(kong_config)
        assert path in route.get("paths", []), (
            f"{path} missing from Kong route paths. Backend at "
            f"apps/services/field-management-service/src/{backend_controller} "
            f"is live but every external call 404s at the gateway."
        )

    def test_route_strip_path_is_false(self, kong_config):
        """The backend controllers use `@Controller('api/v1/...')` — Kong
        MUST forward the full path. strip_path:true would send the backend
        a bare `/`, which doesn't match any controller."""
        route = self._field_management_route(kong_config)
        assert route.get("strip_path") is False, (
            "field-management-service-route MUST be strip_path:false — "
            "NestJS controllers are mounted at api/v1/..., stripping the "
            "prefix kills every route"
        )

    def test_route_supports_mutation_methods(self, kong_config):
        """Farms / field-ops / erp-sync all need POST/PUT/PATCH/DELETE
        (full CRUD on each). Just GET won't cut it."""
        route = self._field_management_route(kong_config)
        methods = set(route.get("methods", []))
        for verb in ("GET", "POST", "PUT", "PATCH", "DELETE"):
            assert verb in methods, f"{verb} missing from field-management-service-route methods"
