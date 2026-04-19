"""
Regression tests for the three deferred-fix items shipped on
PR `claude/finish-deferred-fixes`:

1. weather-service Yemen-location-scoped routes
   (handler-level coverage already lives in the service's own
   tests/test_advanced_endpoints.py::TestYemenLocationEndpoints — this
   file only sanity-checks the contract entries).

2. inventory-service Kong split — `/api/v1/inventory/categories` and
   `/api/v1/inventory/analytics` must reach the backend's `/v1/*`
   handlers via dedicated Kong services with `path: /v1/categories`
   and `path: /v1/analytics` respectively. A shared `path: /v1` would
   strip the matched suffix and rewrite to just `/v1` upstream.

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
    apps/mobile/lib/core/services/service_registry.dart) and
    /api/v1/inventory/analytics/* (analytics_service). Backend handlers
    are at @app.get("/v1/categories") and @app.get("/v1/analytics/*").

    Each legacy sub-tree needs its OWN Kong service because Kong's
    strip_path consumes the FULL matched route path. With one shared
    legacy service using `path: /v1`, /api/v1/inventory/categories would
    strip to "" and rewrite to just "/v1" — never reaching the backend's
    /v1/categories handler. So we have:
      inventory-service-legacy-categories  → path: /v1/categories
      inventory-service-legacy-analytics   → path: /v1/analytics
      inventory-service                     → strip_path: false (modern)
    """

    def _services_named(self, kong_config: dict, name: str) -> list[dict]:
        return [s for s in kong_config.get("services", []) if s.get("name") == name]

    def test_categories_service_path_is_v1_categories(self, kong_config):
        """Without `path: /v1/categories`, the strip+prepend math leaves
        the upstream URL at "/v1" — backend's /v1/categories handler
        never matches. The path MUST include the categories suffix."""
        svc = self._services_named(kong_config, "inventory-service-legacy-categories")
        assert len(svc) == 1, "Expected exactly one inventory-service-legacy-categories entry"
        assert svc[0]["host"] == "inventory-service"
        assert svc[0].get("path") == "/v1/categories", (
            "inventory-service-legacy-categories MUST set path:/v1/categories — "
            "with just /v1, /api/v1/inventory/categories rewrites to /v1 and 404s"
        )

    def test_categories_route_owns_only_categories_path(self, kong_config):
        svc = self._services_named(kong_config, "inventory-service-legacy-categories")
        assert svc, "inventory-service-legacy-categories missing"
        all_paths = {p for r in svc[0]["routes"] for p in r.get("paths", [])}
        assert all_paths == {"/api/v1/inventory/categories"}, (
            f"Expected exactly one route /api/v1/inventory/categories, got {all_paths}"
        )

    def test_analytics_service_path_is_v1_analytics(self, kong_config):
        """Same logic: without `path: /v1/analytics`, strip+prepend would
        send /api/v1/inventory/analytics/forecast to /v1/forecast (no
        analytics segment) — backend's /v1/analytics/forecast 404s."""
        svc = self._services_named(kong_config, "inventory-service-legacy-analytics")
        assert len(svc) == 1, "Expected exactly one inventory-service-legacy-analytics entry"
        assert svc[0]["host"] == "inventory-service"
        assert svc[0].get("path") == "/v1/analytics", (
            "inventory-service-legacy-analytics MUST set path:/v1/analytics — "
            "with just /v1, /api/v1/inventory/analytics/forecast rewrites to /v1/forecast and 404s"
        )

    def test_analytics_route_owns_only_analytics_path(self, kong_config):
        svc = self._services_named(kong_config, "inventory-service-legacy-analytics")
        assert svc, "inventory-service-legacy-analytics missing"
        all_paths = {p for r in svc[0]["routes"] for p in r.get("paths", [])}
        assert all_paths == {"/api/v1/inventory/analytics"}, (
            f"Expected exactly one route /api/v1/inventory/analytics, got {all_paths}"
        )

    def test_modern_inventory_uses_strip_path_false(self, kong_config):
        """The catch-all inventory route must forward as-is so the modern
        APIRouter(prefix='/api/v1/inventory') in src/api/v1/inventory.py
        receives the full path."""
        modern = self._services_named(kong_config, "inventory-service")
        assert len(modern) == 1
        assert modern[0].get("path") is None  # No service-level rewrite
        main_routes = [r for r in modern[0]["routes"] if "/api/v1/inventory" in r.get("paths", [])]
        assert main_routes, "No /api/v1/inventory route on inventory-service"
        assert main_routes[0]["strip_path"] is False, (
            "Modern inventory route MUST be strip_path:false — the backend's "
            "router is mounted at prefix='/api/v1/inventory', stripping kills it"
        )

    def test_all_three_inventory_services_share_upstream(self, kong_config):
        """Longest-prefix match steers /categories + /analytics to the
        dedicated legacy services; anything else (/{itemId}, /stats, etc.)
        goes to the modern catch-all. All three MUST point at the same
        backend upstream so a single deployment serves every variant."""
        names = (
            "inventory-service-legacy-categories",
            "inventory-service-legacy-analytics",
            "inventory-service",
        )
        hosts = {self._services_named(kong_config, n)[0]["host"] for n in names if self._services_named(kong_config, n)}
        assert hosts == {"inventory-service"}, (
            f"All three inventory services must share host=inventory-service, got {hosts}"
        )

    def test_legacy_inventory_services_have_same_rate_limits(self, kong_config):
        """Both legacy services MUST carry the same rate-limiting config as
        the modern route. Without this, a client can sidestep the 60/min cap
        by hitting /api/v1/inventory/categories or /api/v1/inventory/analytics
        instead of /api/v1/inventory/{itemId}.
        """

        def _rate_limit(svc_name: str) -> dict | None:
            svc = self._services_named(kong_config, svc_name)
            if not svc:
                return None
            for p in svc[0].get("plugins") or []:
                if p.get("name") == "rate-limiting":
                    return p.get("config", {})
            return None

        modern = _rate_limit("inventory-service")
        assert modern is not None, "Modern inventory-service must have rate-limiting (baseline)"

        for legacy_name in ("inventory-service-legacy-categories", "inventory-service-legacy-analytics"):
            legacy = _rate_limit(legacy_name)
            assert legacy is not None, f"{legacy_name} missing rate-limiting plugin"
            # Compare only the caps — other fields (`fault_tolerant`, `policy`)
            # are execution knobs and can match loosely.
            for key in ("minute", "hour"):
                assert legacy.get(key) == modern.get(key), (
                    f"{legacy_name} rate-limiting {key!r} = {legacy.get(key)} "
                    f"differs from modern inventory-service {key!r} = {modern.get(key)}"
                )


# ===========================================================================
# 2. JSDoc @deprecated → Dart @Deprecated codegen
# ===========================================================================


class TestDartDeprecatedAnnotations:
    """The TypeScript api-endpoints.ts marks legacy paths with JSDoc
    `@deprecated`. The codegen at scripts/sync-contracts-to-dart.ts must
    propagate those into Dart `@Deprecated('msg')` annotations so mobile
    builds emit warnings when callers touch them.

    Counts are asserted EXACTLY: every JSDoc @deprecated tag inside an
    *_ENDPOINTS object should produce one and only one `@Deprecated(...)`
    annotation in the generated Dart. A mismatch in either direction is
    a codegen bug — extras mean over-eager parsing, missing means a
    regex regression dropped a tag.
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
    a cheap local pre-push check that mirrors the dedicated CI workflow
    in api-contracts-guard.yml.

    Skipped when the Node toolchain is not pre-installed locally. We
    deliberately do NOT fall back to `npx` (which would download `tsx`
    on demand): that adds 10–20s per test run, hits the network, and
    would silently fail in air-gapped CI runners. The
    api-contracts-guard.yml workflow runs the same check inside a
    properly-set-up Node environment, so coverage isn't lost.
    """

    def test_dart_contracts_are_in_sync(self):
        import subprocess

        # Prefer a project-local `tsx` (node_modules/.bin/tsx) that the
        # api-contracts-guard CI workflow installs. If it isn't there,
        # skip — running pytest shouldn't trigger an `npx` download.
        local_tsx = REPO_ROOT / "node_modules" / ".bin" / "tsx"
        if not local_tsx.exists():
            pytest.skip(
                f"tsx not pre-installed at {local_tsx} — skipping live codegen check. "
                "api-contracts-guard.yml exercises the same path in CI."
            )

        result = subprocess.run(
            [str(local_tsx), "scripts/sync-contracts-to-dart.ts", "--check"],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert result.returncode == 0, (
            f"sync-contracts-to-dart --check failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}\n\n"
            f"Run: npx tsx scripts/sync-contracts-to-dart.ts (without --check)"
        )
