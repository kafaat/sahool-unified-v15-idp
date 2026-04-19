"""
Regression tests for the three deferred-fix items shipped on
PR `claude/finish-deferred-fixes`:

1. weather-service Yemen-location-scoped routes
   (handler-level coverage already lives in the service's own
   tests/test_advanced_endpoints.py::TestYemenLocationEndpoints — this
   file only sanity-checks the contract entries).

2. inventory-service Kong split — `/api/v1/inventory/categories` and
   `/api/v1/inventory/analytics` must reach the backend's `/v1/*`
   handlers via a dedicated Kong service with `path: /v1`.

3. scripts/sync-contracts-to-dart.ts — JSDoc `@deprecated` tags must
   land as Dart `@Deprecated('msg')` annotations in the generated
   apps/mobile/lib/core/contracts/api_endpoints.dart.

These are pure file-level assertions (no docker / no live Kong) so
they can run in any CI job that has Python + the repo checked out.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
KONG_ACTIVE = REPO_ROOT / "infrastructure" / "gateway" / "kong" / "active" / "kong.yml"
TS_ENDPOINTS = REPO_ROOT / "packages" / "shared-types" / "src" / "contracts" / "api-endpoints.ts"
DART_ENDPOINTS = REPO_ROOT / "apps" / "mobile" / "lib" / "core" / "contracts" / "api_endpoints.dart"

pytestmark = [pytest.mark.unit]


# ===========================================================================
# 1. inventory-service Kong split
# ===========================================================================


@pytest.fixture(scope="module")
def kong_config() -> dict:
    """Load the active Kong config used by docker-compose."""
    if not KONG_ACTIVE.exists():
        pytest.skip(f"Kong config not found at {KONG_ACTIVE}")
    with open(KONG_ACTIVE, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


class TestInventoryKongSplit:
    """The mobile client calls /api/v1/inventory/categories (see
    apps/mobile/lib/core/services/service_registry.dart). Backend handlers
    are at @app.get("/v1/categories") — a Kong path rewrite is required.
    """

    def _services_named(self, kong_config: dict, name: str) -> list[dict]:
        return [s for s in kong_config.get("services", []) if s.get("name") == name]

    def test_inventory_legacy_service_exists(self, kong_config):
        """inventory-service-legacy is the dedicated split that handles
        the /v1/categories + /v1/analytics paths."""
        legacy = self._services_named(kong_config, "inventory-service-legacy")
        assert len(legacy) == 1, "Expected exactly one inventory-service-legacy entry"
        assert legacy[0]["host"] == "inventory-service"  # share the same upstream
        assert legacy[0].get("path") == "/v1", (
            "inventory-service-legacy MUST set path:/v1 — without the rewrite, "
            "Kong forwards /categories instead of /v1/categories and the backend 404s"
        )

    def test_legacy_routes_cover_categories_and_analytics(self, kong_config):
        legacy_list = self._services_named(kong_config, "inventory-service-legacy")
        assert legacy_list, "inventory-service-legacy missing — see test_inventory_legacy_service_exists"
        legacy = legacy_list[0]
        all_paths = {p for r in legacy["routes"] for p in r.get("paths", [])}
        assert "/api/v1/inventory/categories" in all_paths
        assert "/api/v1/inventory/analytics" in all_paths

    def test_modern_inventory_uses_strip_path_false(self, kong_config):
        """The non-legacy inventory route must forward as-is so the modern
        APIRouter(prefix='/api/v1/inventory') in src/api/v1/inventory.py
        receives the full path."""
        modern = self._services_named(kong_config, "inventory-service")
        assert len(modern) == 1
        # No service-level path rewrite — just forward.
        assert modern[0].get("path") is None
        # Find the main /api/v1/inventory route.
        main_routes = [r for r in modern[0]["routes"] if "/api/v1/inventory" in r.get("paths", [])]
        assert main_routes, "No /api/v1/inventory route on inventory-service"
        assert main_routes[0]["strip_path"] is False, (
            "Modern inventory route MUST be strip_path:false — the backend's "
            "router is mounted at prefix='/api/v1/inventory', stripping kills it"
        )

    def test_no_path_collision_between_legacy_and_modern(self, kong_config):
        """Longest-prefix match must steer /categories + /analytics to the
        legacy service. Anything else (/{itemId}, /stats, etc.) goes to the
        modern service. We assert both services exist on the SAME upstream
        so Kong can do that routing decision."""
        legacy_list = self._services_named(kong_config, "inventory-service-legacy")
        modern_list = self._services_named(kong_config, "inventory-service")
        assert legacy_list and modern_list, (
            "Both inventory-service-legacy and inventory-service entries are required"
        )
        assert legacy_list[0]["host"] == modern_list[0]["host"], (
            "Both inventory Kong services must point at the same upstream "
            f"(legacy={legacy_list[0]['host']!r}, modern={modern_list[0]['host']!r})"
        )


# ===========================================================================
# 2. JSDoc @deprecated → Dart @Deprecated codegen
# ===========================================================================


class TestDartDeprecatedAnnotations:
    """The TypeScript api-endpoints.ts marks legacy paths with JSDoc
    `@deprecated`. The codegen at scripts/sync-contracts-to-dart.ts must
    propagate those into Dart `@Deprecated('msg')` annotations so mobile
    builds emit warnings when callers touch them.

    Counts checked against the snapshot taken when the codegen lands; if
    the live contract grows new @deprecated entries the count will
    only increase — assert_>= guards that direction.
    """

    @pytest.fixture(scope="class")
    def ts_source(self) -> str:
        if not TS_ENDPOINTS.exists():
            pytest.skip(f"TS contracts not found at {TS_ENDPOINTS}")
        return TS_ENDPOINTS.read_text(encoding="utf-8")

    @pytest.fixture(scope="class")
    def dart_source(self) -> str:
        if not DART_ENDPOINTS.exists():
            pytest.skip(f"Dart contracts not found at {DART_ENDPOINTS}")
        return DART_ENDPOINTS.read_text(encoding="utf-8")

    def test_dart_contains_deprecated_annotations(self, dart_source):
        """At least one @Deprecated() must appear — proves the codegen ran
        with the JSDoc-aware version."""
        count = dart_source.count("@Deprecated(")
        assert count > 0, (
            "No @Deprecated annotations in api_endpoints.dart — either the "
            "codegen regressed or no JSDoc @deprecated tags exist in TS source. "
            "Run: npx tsx scripts/sync-contracts-to-dart.ts"
        )

    def test_dart_count_matches_ts_count(self, ts_source, dart_source):
        """Every JSDoc @deprecated tag inside an *_ENDPOINTS object should
        produce exactly one Dart @Deprecated annotation. Counts must match."""
        # Match @deprecated only inside `export const FOO_ENDPOINTS = { ... } as const;`
        # blocks (skip module-level @deprecated comments etc).
        ts_count = 0
        for group_match in re.finditer(
            r"export\s+const\s+[A-Z][A-Z0-9_]*_ENDPOINTS\s*=\s*\{([\s\S]*?)\}\s*as\s*const\s*;",
            ts_source,
        ):
            body = group_match.group(1)
            # Each comment block immediately preceding a KEY: tagged with @deprecated.
            ts_count += len(
                re.findall(
                    r"/\*\*[\s\S]*?@deprecated[\s\S]*?\*/\s*[A-Z][A-Z0-9_]*\s*:",
                    body,
                )
            )

        dart_count = dart_source.count("@Deprecated(")
        assert dart_count == ts_count, (
            f"Mismatch: {ts_count} TS @deprecated tags inside endpoint groups, "
            f"{dart_count} Dart @Deprecated annotations. "
            "Re-run: npx tsx scripts/sync-contracts-to-dart.ts"
        )

    def test_specific_known_deprecations_present(self, dart_source):
        """Sample of known-deprecated endpoints; if the codegen drops any
        of these we want a clear failure pinning the cause."""
        # WEATHER_CORE_CURRENT etc are the canonical examples.
        for member in ("weatherCoreCurrent", "weatherCoreForecast"):
            pattern = rf"@Deprecated\([^\)]+\)\s+static const String {member}\s*="
            assert re.search(pattern, dart_source), (
                f"Expected @Deprecated annotation immediately before "
                f"`static const String {member}` in the Dart contracts"
            )


# ===========================================================================
# 3. Yemen-location weather contract entries
# ===========================================================================


class TestYemenWeatherContract:
    """The three weather-by-location entries used to be marked
    "never implemented" — this test snapshots the live shape so a future
    refactor can't silently revert that promise."""

    @pytest.fixture(scope="class")
    def ts_source(self) -> str:
        if not TS_ENDPOINTS.exists():
            pytest.skip(f"TS contracts not found at {TS_ENDPOINTS}")
        return TS_ENDPOINTS.read_text(encoding="utf-8")

    @pytest.mark.parametrize(
        "key,expected_path",
        [
            ("KONG_CURRENT_BY_LOCATION", "/api/v1/weather/v1/current/{locationId}"),
            ("KONG_FORECAST_BY_LOCATION", "/api/v1/weather/v1/forecast/{locationId}"),
            ("KONG_LOCATIONS", "/api/v1/weather/v1/locations"),
        ],
    )
    def test_yemen_endpoint_paths_unchanged(self, ts_source, key, expected_path):
        # Path is interpolated from `${API_PREFIX}/...`; expected is the
        # resolved form with /api/v1 substituted in.
        backend_path = expected_path.replace("/api/v1", "${API_PREFIX}", 1)
        assert backend_path in ts_source, (
            f"Contract entry {key} no longer carries the path "
            f"{expected_path!r} — backend handlers in weather-service rely on this"
        )

    def test_yemen_endpoints_not_marked_deprecated(self, ts_source):
        """They MUST NOT regress to @deprecated — backend now serves them.
        Find each KEY and confirm the JSDoc block immediately above does
        not contain `@deprecated`."""
        for key in ("KONG_CURRENT_BY_LOCATION", "KONG_FORECAST_BY_LOCATION", "KONG_LOCATIONS"):
            # Look for JSDoc immediately before the key (tolerates whitespace).
            m = re.search(rf"/\*\*([\s\S]*?)\*/\s*{key}\s*:", ts_source)
            if m and "@deprecated" in m.group(1):
                pytest.fail(
                    f"{key} is marked @deprecated, but weather-service now "
                    f"implements it via @app.get('/weather/v1/...'). Drop the tag."
                )


# ===========================================================================
# 4. Codegen sync guard
# ===========================================================================


class TestDartCodegenInSync:
    """Run the live sync script in --check mode. If anyone edits the
    TypeScript contracts (including adding/removing @deprecated tags) and
    forgets to regenerate the Dart files, this test fails immediately —
    the same gate the GitHub Actions workflow enforces, but available
    as a cheap local pre-push check.
    """

    def test_dart_contracts_are_in_sync(self):
        import shutil
        import subprocess

        if shutil.which("npx") is None:
            pytest.skip("npx not available — skipping live codegen check")

        result = subprocess.run(
            ["npx", "tsx", "scripts/sync-contracts-to-dart.ts", "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert result.returncode == 0, (
            f"sync-contracts-to-dart --check failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}\n\n"
            f"Run: npx tsx scripts/sync-contracts-to-dart.ts (without --check)"
        )
