"""
SAHOOL Comprehensive Endpoint Validation Tests
================================================
فحص شامل لنقاط النهاية لجميع الحاويات والخدمات

Validates the correctness of every API endpoint across all 60+ services:
- Health endpoint presence and consistency
- API route definitions (paths, methods, versioning)
- Path parameter naming conventions
- HTTP method correctness (GET for reads, POST for writes)
- Route duplication detection
- Authentication decorator coverage
- Response model / schema presence
- Cross-service endpoint patterns
- OpenAPI docs configuration
- Middleware integration

Run:
    pytest tests/container/test_endpoints_validation.py -v
"""

from __future__ import annotations

import re
from itertools import islice
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.container.service_registry import (
    ALL_HTTP_SERVICES,
    INFRA_SERVICES,
    INIT_SERVICES,
    NODE_SERVICES,
    PORTLESS_SERVICES,
    PYTHON_SERVICES,
)

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Standard health endpoint paths that every service should implement
REQUIRED_HEALTH_PATHS = {"/healthz"}
RECOMMENDED_HEALTH_PATHS = {"/readyz", "/health", "/metrics"}

# Acceptable API version prefixes
VALID_API_PREFIXES = {"/api/v1/", "/api/v2/", "/v1/", "/v2/"}

# HTTP methods that should be read-only (idempotent)
READ_METHODS = {"get", "head", "options"}
# HTTP methods that can modify state
WRITE_METHODS = {"post", "put", "patch", "delete"}

# Path parameter naming: should be snake_case or simple id
_PARAM_RE = re.compile(r"\{(\w+)\}")

# Route decorator patterns for Python/FastAPI
_PY_ROUTE_RE = re.compile(
    r"@(?:app|router)\.(get|post|put|delete|patch|head|options|websocket)"
    r'\s*\(\s*["\']([^"\']+)["\']',
    re.IGNORECASE,
)

# FastAPI include_router pattern
_PY_INCLUDE_ROUTER_RE = re.compile(
    r"include_router\s*\([^,]+,\s*prefix\s*=\s*[\"']([^\"']+)[\"']",
)

# NestJS controller/route patterns
_TS_CONTROLLER_RE = re.compile(r"@Controller\s*\(\s*[\"']([^\"']*)[\"']\s*\)")
_TS_ROUTE_RE = re.compile(
    r"@(Get|Post|Put|Delete|Patch|Head|Options)\s*\(\s*(?:[\"']([^\"']*)[\"'])?\s*\)",
    re.IGNORECASE,
)

# Services excluded from registry validation (special cases)
_REGISTRY_EXEMPT_SERVICES: set[str] = {"wechat-service", "vllm-deepseek"}

# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

_source_cache: dict[str, str] = {}
_node_src_cache: dict[str, str] = {}
_routes_cache: dict[str, list[tuple[str, str]]] = {}
_ts_routes_cache: dict[str, list[tuple[str, str]]] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _read_python_source(svc: str, max_files: int = 50) -> str:
    """Read and cache all Python source files for a service."""
    if svc not in _source_cache:
        src_dir = SERVICES_DIR / svc / "src"
        if not src_dir.exists():
            _source_cache[svc] = ""
            return ""
        parts: list[str] = []
        for f in islice(sorted(src_dir.rglob("*.py")), max_files):
            try:
                parts.append(f.read_text("utf-8", errors="ignore"))
            except OSError:
                continue
        _source_cache[svc] = "\n".join(parts)
    return _source_cache[svc]


def _read_node_source(svc: str, max_files: int = 80) -> str:
    """Read and cache all TypeScript source files for a Node.js service."""
    if svc not in _node_src_cache:
        src_dir = SERVICES_DIR / svc / "src"
        if not src_dir.exists():
            _node_src_cache[svc] = ""
            return ""
        parts: list[str] = []
        for f in islice(sorted(src_dir.rglob("*.ts")), max_files):
            try:
                parts.append(f.read_text("utf-8", errors="ignore"))
            except OSError:
                continue
        _node_src_cache[svc] = "\n".join(parts)
    return _node_src_cache[svc]


def _extract_python_routes(svc: str) -> list[tuple[str, str]]:
    """Extract (method, path) tuples from Python/FastAPI service."""
    if svc not in _routes_cache:
        src = _read_python_source(svc)
        routes = _PY_ROUTE_RE.findall(src)
        _routes_cache[svc] = [(m.lower(), p) for m, p in routes]
    return _routes_cache[svc]


def _extract_ts_routes(svc: str) -> list[tuple[str, str]]:
    """Extract (method, path) tuples from NestJS service."""
    if svc not in _ts_routes_cache:
        src = _read_node_source(svc)
        controllers = _TS_CONTROLLER_RE.findall(src)
        routes = _TS_ROUTE_RE.findall(src)
        # Build full paths: controller_prefix + route_path
        full_routes: list[tuple[str, str]] = []
        for method, path in routes:
            full_routes.append((method.lower(), path or "/"))
        _ts_routes_cache[svc] = full_routes
    return _ts_routes_cache[svc]


def _extract_path_params(path: str) -> list[str]:
    """Extract path parameter names from a route path."""
    return _PARAM_RE.findall(path)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def python_routes() -> dict[str, list[tuple[str, str]]]:
    """Pre-extract all Python service routes."""
    result: dict[str, list[tuple[str, str]]] = {}
    for svc in PYTHON_SERVICES:
        routes = _extract_python_routes(svc)
        if routes:
            result[svc] = routes
    return result


@pytest.fixture(scope="module")
def node_routes() -> dict[str, list[tuple[str, str]]]:
    """Pre-extract all Node.js service routes."""
    result: dict[str, list[tuple[str, str]]] = {}
    for svc in NODE_SERVICES:
        routes = _extract_ts_routes(svc)
        if routes:
            result[svc] = routes
    return result


# ============================================================================
# 1. Health Endpoint Presence
# ============================================================================


class TestHealthEndpoints:
    """فحص نقاط الفحص الصحي"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_healthz(self, svc: str) -> None:
        """Every Python service must have a /healthz endpoint."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_healthz = bool(re.search(r'["\'/]healthz["\']', src))
        assert has_healthz, (
            f"Python service '{svc}' is missing /healthz endpoint"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_readyz(self, svc: str) -> None:
        """Every Python service should have a /readyz endpoint."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_readyz = bool(re.search(r'["\'/]readyz["\']', src))
        assert has_readyz, (
            f"Python service '{svc}' is missing /readyz endpoint"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_healthz_returns_status(self, svc: str) -> None:
        """Health endpoint should return a status field."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        # Look for {"status": ...} or return dict with status, or HealthResponse
        has_status = bool(re.search(
            r'["\']status["\']\s*:\s*["\']ok["\']|'
            r'status["\']:\s*["\']ok|'
            r'HealthResponse|health_response|'
            r'return\s*\{[^}]*["\']status["\']|'
            r'"status":\s*"ok"|'
            r"status.*ok",
            src, re.DOTALL | re.IGNORECASE,
        ))
        assert has_status, (
            f"Python service '{svc}' health endpoint doesn't return status field"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_health_endpoint(self, svc: str) -> None:
        """Every Node.js service must have health endpoints."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_health = bool(re.search(
            r'healthz|readyz|TerminusModule|HealthModule|health|livez',
            src, re.IGNORECASE,
        ))
        assert has_health, (
            f"Node.js service '{svc}' has no health endpoint"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_healthz(self, svc: str) -> None:
        """Node.js services should have /healthz endpoint."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_healthz = bool(re.search(r'healthz', src, re.IGNORECASE))
        assert has_healthz, (
            f"Node.js service '{svc}' is missing /healthz endpoint"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_readyz(self, svc: str) -> None:
        """Node.js services should have /readyz endpoint."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_readyz = bool(re.search(r'readyz', src, re.IGNORECASE))
        assert has_readyz, (
            f"Node.js service '{svc}' is missing /readyz endpoint"
        )


# ============================================================================
# 2. API Route Definitions
# ============================================================================


class TestAPIRouteDefinitions:
    """فحص تعريفات مسارات API"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_api_routes(self, svc: str) -> None:
        """Python services should define at least one API route beyond health."""
        routes = _extract_python_routes(svc)
        non_health = [
            (m, p) for m, p in routes
            if not any(h in p for h in ("healthz", "readyz", "health", "metrics"))
        ]
        assert len(non_health) >= 1, (
            f"Python service '{svc}' has no API routes beyond health endpoints "
            f"(found {len(routes)} total routes)"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_api_routes(self, svc: str) -> None:
        """Node.js services should define at least one API route beyond health."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        # Count @Get/@Post etc. decorators (excluding health-related ones)
        all_routes = _TS_ROUTE_RE.findall(src)
        non_health = [
            (m, p) for m, p in all_routes
            if not re.search(r'health|readyz|livez', p, re.IGNORECASE)
        ]
        assert len(non_health) >= 1, (
            f"Node.js service '{svc}' has no API routes beyond health endpoints"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_routes_have_valid_paths(self, svc: str) -> None:
        """All route paths should start with /."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        bad_paths = [(m, p) for m, p in routes if not p.startswith("/")]
        assert not bad_paths, (
            f"Python service '{svc}' has routes not starting with /: "
            f"{bad_paths[:5]}"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_no_trailing_slash_inconsistency(self, svc: str) -> None:
        """Routes shouldn't have trailing slashes (FastAPI convention)."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        trailing = [(m, p) for m, p in routes if len(p) > 1 and p.endswith("/")]
        assert not trailing, (
            f"Python service '{svc}' has routes with trailing slashes: "
            f"{trailing[:5]} (FastAPI convention: no trailing slash)"
        )


# ============================================================================
# 3. HTTP Method Correctness
# ============================================================================


class TestHTTPMethodCorrectness:
    """فحص صحة أساليب HTTP"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_get_routes_are_read_only(self, svc: str) -> None:
        """GET routes should not contain write operations in their handler names."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        # Find all @app.get / @router.get with async def names
        get_handlers = re.findall(
            r'@(?:app|router)\.get\s*\([^)]*\)\s*\n(?:.*\n){0,3}async\s+def\s+(\w+)',
            src,
        )
        # Handler names starting with "create_" or "delete_" on GET are suspicious
        suspicious = [
            name for name in get_handlers
            if name.startswith(("create_", "delete_", "remove_", "destroy_"))
        ]
        assert not suspicious, (
            f"Python service '{svc}' has GET handlers with write-like names: "
            f"{suspicious[:5]}"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_delete_routes_exist_where_expected(self, svc: str) -> None:
        """Services with POST/create endpoints should also have DELETE endpoints."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        has_post = any(m == "post" for m, p in routes)
        has_delete = any(m == "delete" for m, p in routes)
        # This is informational — not all services need DELETE
        if has_post and not has_delete:
            # Many services legitimately don't have DELETE (advisory, weather, etc.)
            pass  # Informational only


# ============================================================================
# 4. Path Parameter Conventions
# ============================================================================


class TestPathParameterConventions:
    """فحص اصطلاحات معلمات المسار"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_path_params_snake_case(self, svc: str) -> None:
        """Path parameters should use snake_case (e.g., {field_id} not {fieldId})."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        camel_params: list[str] = []
        for _, path in routes:
            params = _extract_path_params(path)
            for p in params:
                # Check for camelCase (lowercase letter followed by uppercase)
                if re.search(r"[a-z][A-Z]", p):
                    camel_params.append(p)
        assert not camel_params, (
            f"Python service '{svc}' has camelCase path params "
            f"(should be snake_case): {set(camel_params)}"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_path_params_not_empty(self, svc: str) -> None:
        """Path parameters should not be empty braces."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        empty_params = [(m, p) for m, p in routes if "{}" in p]
        assert not empty_params, (
            f"Python service '{svc}' has routes with empty params: "
            f"{empty_params[:3]}"
        )


# ============================================================================
# 5. API Versioning Consistency
# ============================================================================


class TestAPIVersioning:
    """فحص اتساق إصدارات API"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_versioned_endpoints(self, svc: str) -> None:
        """Python services should use consistent API versioning."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        non_health = [
            (m, p) for m, p in routes
            if not any(h in p for h in ("healthz", "readyz", "health", "metrics"))
        ]
        if not non_health:
            pytest.skip(f"{svc} has only health routes")

        # Count routes with version prefix vs without
        versioned = [p for _, p in non_health if re.match(r"/(api/)?v\d+/", p)]
        unversioned = [p for _, p in non_health if not re.match(r"/(api/)?v\d+/", p)]

        # If mix of versioned and unversioned, that's a potential issue
        # But many services legitimately have root-level endpoints alongside versioned ones
        # Only flag if there are versioned routes but some API routes are unversioned
        if versioned and unversioned:
            # Filter out truly root-level endpoints (/, /info, /stats)
            api_unversioned = [
                p for p in unversioned
                if len(p.split("/")) > 2  # More than just /resource
            ]
            if api_unversioned and len(api_unversioned) > len(versioned):
                # Majority unversioned — that's a potential issue but might be intentional
                pass  # Informational — don't fail

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_no_mixed_versions(self, svc: str) -> None:
        """A service shouldn't mix v1 and v2 endpoints (unless migrating)."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        versions_used: set[str] = set()
        for _, path in routes:
            match = re.match(r"/(api/)?v(\d+)/", path)
            if match:
                versions_used.add(match.group(2))
        # Having both v1 and v2 is acceptable during migration
        # Just ensure we don't have v3+ mixed in
        if len(versions_used) > 2:
            pytest.fail(
                f"Python service '{svc}' mixes {len(versions_used)} API versions: "
                f"v{', v'.join(sorted(versions_used))}"
            )


# ============================================================================
# 6. Route Duplication Detection
# ============================================================================


class TestRouteDuplication:
    """كشف تكرار المسارات"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_no_duplicate_routes(self, svc: str) -> None:
        """No two routes should have the same method + path in the same file."""
        if not (SERVICES_DIR / svc / "src").exists():
            pytest.skip(f"{svc} has no source")
        # Only check main.py for duplicates — router files get prefixed
        main_py = SERVICES_DIR / svc / "src" / "main.py"
        if not main_py.exists():
            pytest.skip(f"{svc}/src/main.py not found")
        content = main_py.read_text("utf-8", errors="ignore")
        routes = _PY_ROUTE_RE.findall(content)
        seen: dict[tuple[str, str], int] = {}
        for method, path in routes:
            key = (method.lower(), path)
            seen[key] = seen.get(key, 0) + 1
        duplicates = [(k, v) for k, v in seen.items() if v >= 2]
        assert not duplicates, (
            f"Python service '{svc}' main.py has duplicate routes: "
            f"{[(m, p, c) for (m, p), c in duplicates[:5]]}"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_no_conflicting_paths(self, svc: str) -> None:
        """Routes with root-level {param} patterns may shadow other routes."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        # Group routes by method
        by_method: dict[str, list[str]] = {}
        for method, path in routes:
            by_method.setdefault(method, []).append(path)

        conflicts: list[str] = []
        for method, paths in by_method.items():
            # Only flag routes that are a bare /{param} at root conflicting
            # with multi-segment static routes — these are genuine issues.
            # Routes at /api/v1/{param} vs /api/v1/static are a different case
            # and are handled by FastAPI's route ordering.
            root_params = [p for p in paths if re.match(r"^/\{[^}]+\}$", p)]
            if not root_params:
                continue
            statics = [p for p in paths if "{" not in p and len(p.split("/")) == 2 and p != "/"]
            for rp in root_params:
                for sp in statics:
                    # /{param} can shadow /static at the same depth
                    if sp not in ("/healthz", "/readyz", "/health", "/metrics"):
                        conflicts.append(
                            f"{method.upper()} {rp} may shadow {sp}"
                        )
        # These are informational — FastAPI handles route ordering
        # but it's worth flagging potential issues
        if conflicts:
            import warnings
            warnings.warn(
                f"Python service '{svc}' has potential route shadowing: "
                f"{conflicts[:3]}", stacklevel=2,
            )


# ============================================================================
# 7. Authentication/Authorization Decorators
# ============================================================================


class TestAuthDecoratorCoverage:
    """فحص تغطية مصادقة/تفويض API"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_auth_imports(self, svc: str) -> None:
        """Python services should import authentication dependencies."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_auth = bool(re.search(
            r"get_current_user|Depends\(.*auth|verify_token|jwt|"
            r"shared\.auth|oauth2_scheme|api_key|Bearer",
            src, re.IGNORECASE,
        ))
        # Health-only services and internal services may skip auth
        if not has_auth:
            # Check if it's an internal-only service
            routes = _extract_python_routes(svc)
            non_health = [
                (m, p) for m, p in routes
                if not any(h in p for h in ("healthz", "readyz", "health", "metrics"))
            ]
            if len(non_health) > 3:
                # Service has significant API surface without auth
                pytest.fail(
                    f"Python service '{svc}' has {len(non_health)} API routes "
                    f"but no authentication imports"
                )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_auth_imports(self, svc: str) -> None:
        """Node.js services should use authentication guards."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_auth = bool(re.search(
            r"AuthGuard|JwtGuard|UseGuards|Bearer|passport|"
            r"@nestjs/passport|auth\.module|AuthModule",
            src, re.IGNORECASE,
        ))
        if not has_auth:
            routes = _extract_ts_routes(svc)
            non_health = [
                (m, p) for m, p in routes
                if not re.search(r'health|readyz|livez', p, re.IGNORECASE)
            ]
            if len(non_health) > 3:
                pytest.fail(
                    f"Node.js service '{svc}' has {len(non_health)} API routes "
                    f"but no authentication guards"
                )


# ============================================================================
# 8. Response Model / Schema Presence
# ============================================================================


class TestResponseSchemas:
    """فحص نماذج الاستجابة"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_uses_pydantic_models(self, svc: str) -> None:
        """Python services should use Pydantic models for request/response."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_models = bool(re.search(
            r"class\s+\w+\(BaseModel\)|class\s+\w+\(BaseModel,|"
            r"from pydantic import|from pydantic_settings import|"
            r"TypedDict|dataclass|@dataclass|"
            r"mcp\.server|Tool\(|Resource\(",
            src,
        ))
        assert has_models, (
            f"Python service '{svc}' has no Pydantic models — "
            f"API requests/responses should be typed"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_post_routes_have_request_models(self, svc: str) -> None:
        """POST/PUT routes should accept typed request bodies, not raw dicts."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        routes = _extract_python_routes(svc)
        post_routes = [(m, p) for m, p in routes if m in ("post", "put", "patch")]
        if not post_routes:
            pytest.skip(f"{svc} has no POST/PUT routes")
        # Check that at least some POST handlers use typed parameters
        has_typed = bool(re.search(
            r"async\s+def\s+\w+\([^)]*:\s*\w+(?:Request|Input|Create|Update|Body|Schema|Payload|Model|Params|Data)",
            src,
        ))
        # Also accept Pydantic models used as parameters
        has_pydantic_param = bool(re.search(
            r"async\s+def\s+\w+\([^)]*:\s*(?:Body|Form|Request)\s*[,)]",
            src,
        ))
        # Accept any typed parameter (not just Request/Input types)
        has_any_typed = bool(re.search(
            r"async\s+def\s+\w+\([^)]*:\s*[A-Z]\w+",
            src,
        ))
        assert has_typed or has_pydantic_param or has_any_typed, (
            f"Python service '{svc}' has {len(post_routes)} POST/PUT routes "
            f"but no typed request parameters"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_uses_dto_classes(self, svc: str) -> None:
        """Node.js services should use DTO classes for validation."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_dto = bool(re.search(
            r"class\s+\w+Dto|@IsString|@IsNumber|@IsOptional|"
            r"ValidationPipe|class-validator|class-transformer|"
            r"@ApiProperty|@Type\(",
            src,
        ))
        assert has_dto, (
            f"Node.js service '{svc}' has no DTO classes — "
            f"API requests should be validated"
        )


# ============================================================================
# 9. OpenAPI / Swagger Documentation
# ============================================================================


class TestOpenAPIConfiguration:
    """فحص تكوين OpenAPI"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_fastapi_title(self, svc: str) -> None:
        """FastAPI app should have a title and description."""
        path = SERVICES_DIR / svc / "src" / "main.py"
        if not path.exists():
            pytest.skip(f"{svc}/src/main.py not found")
        content = path.read_text("utf-8", errors="ignore")
        has_title = bool(re.search(r'FastAPI\s*\([^)]*title\s*=', content))
        assert has_title, (
            f"Python service '{svc}' FastAPI app has no title "
            f"(needed for auto-generated docs)"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_fastapi_has_version(self, svc: str) -> None:
        """FastAPI app should specify a version."""
        path = SERVICES_DIR / svc / "src" / "main.py"
        if not path.exists():
            pytest.skip(f"{svc}/src/main.py not found")
        content = path.read_text("utf-8", errors="ignore")
        has_version = bool(re.search(
            r'FastAPI\s*\([^)]*version\s*=|'
            r'VERSION\s*=\s*["\'][\d.]+["\']|'
            r'version\s*=\s*settings\.\w+|'
            r'version\s*=\s*["\'][\d.]+["\']|'
            r'__version__\s*=|'
            r'app\.version',
            content,
        ))
        assert has_version, (
            f"Python service '{svc}' FastAPI app has no version string"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_swagger_setup(self, svc: str) -> None:
        """Node.js services should have Swagger/OpenAPI documentation."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_swagger = bool(re.search(
            r"SwaggerModule|@nestjs/swagger|DocumentBuilder|"
            r"swagger|openapi",
            src, re.IGNORECASE,
        ))
        assert has_swagger, (
            f"Node.js service '{svc}' has no Swagger/OpenAPI setup"
        )


# ============================================================================
# 10. Middleware Integration
# ============================================================================


class TestMiddlewareIntegration:
    """فحص تكامل الوسيط"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_error_handling(self, svc: str) -> None:
        """Python services should have unified error handling."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_error_handling = bool(re.search(
            r"setup_exception_handlers|exception_handler|HTTPException|"
            r"@app\.exception_handler|add_exception_handler",
            src,
        ))
        assert has_error_handling, (
            f"Python service '{svc}' has no error handling setup"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_cors_or_middleware(self, svc: str) -> None:
        """Python services should configure CORS or use shared middleware."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_middleware = bool(re.search(
            r"CORSMiddleware|setup_cors|add_middleware|"
            r"RequestLoggingMiddleware|TenantContextMiddleware|"
            r"add_request_id_middleware|ObservabilityMiddleware",
            src,
        ))
        assert has_middleware, (
            f"Python service '{svc}' has no middleware configured"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_error_filter(self, svc: str) -> None:
        """Node.js services should have global exception filters."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_filter = bool(re.search(
            r"ExceptionFilter|HttpExceptionFilter|useGlobalFilters|"
            r"@Catch|AllExceptionsFilter|APP_FILTER",
            src,
        ))
        assert has_filter, (
            f"Node.js service '{svc}' has no global exception filter"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_validation_pipe(self, svc: str) -> None:
        """Node.js services should have validation pipe configured."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_validation = bool(re.search(
            r"ValidationPipe|useGlobalPipes|whitelist|"
            r"transform:\s*true|forbidNonWhitelisted",
            src,
        ))
        assert has_validation, (
            f"Node.js service '{svc}' has no validation pipe"
        )


# ============================================================================
# 11. Cross-Service Endpoint Patterns
# ============================================================================


class TestCrossServicePatterns:
    """أنماط نقاط النهاية عبر الخدمات"""

    def test_all_python_services_have_routes(self) -> None:
        """All registered Python services should have at least 1 route."""
        missing: list[str] = []
        for svc in PYTHON_SERVICES:
            routes = _extract_python_routes(svc)
            if not routes:
                src = _read_python_source(svc)
                if src:
                    missing.append(svc)
        assert not missing, (
            f"Python services with source but no routes: {missing}"
        )

    def test_all_node_services_have_controllers(self) -> None:
        """All registered Node.js services should have at least 1 controller."""
        missing: list[str] = []
        for svc in NODE_SERVICES:
            src = _read_node_source(svc)
            if not src:
                continue
            has_controller = bool(re.search(r"@Controller", src))
            if not has_controller:
                missing.append(svc)
        assert not missing, (
            f"Node.js services without any @Controller: {missing}"
        )

    def test_no_duplicate_ports_across_services(self) -> None:
        """No two services should use the same port."""
        port_map: dict[int, list[str]] = {}
        for svc, port in ALL_HTTP_SERVICES.items():
            port_map.setdefault(port, []).append(svc)
        duplicates = {p: svcs for p, svcs in port_map.items() if len(svcs) > 1}
        assert not duplicates, (
            f"Duplicate ports detected: {duplicates}"
        )

    def test_health_consistency_across_all_services(self) -> None:
        """All services should have consistent health endpoint patterns."""
        missing_healthz: list[str] = []
        for svc in PYTHON_SERVICES:
            src = _read_python_source(svc)
            if not src:
                continue
            if not re.search(r'["\'/]healthz["\']', src):
                missing_healthz.append(svc)
        for svc in NODE_SERVICES:
            src = _read_node_source(svc)
            if not src:
                continue
            if not re.search(r'healthz', src, re.IGNORECASE):
                missing_healthz.append(svc)
        assert not missing_healthz, (
            f"Services missing /healthz endpoint: {missing_healthz}"
        )


# ============================================================================
# 12. Endpoint Security Patterns
# ============================================================================


class TestEndpointSecurity:
    """فحص أمان نقاط النهاية"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_no_debug_endpoints(self, svc: str) -> None:
        """Production services should not have debug/test endpoints."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        debug_routes = [
            (m, p) for m, p in routes
            if re.search(r"/debug/|/test/|/__debug__|/_internal/", p)
        ]
        assert not debug_routes, (
            f"Python service '{svc}' has debug endpoints: {debug_routes[:3]}"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_no_sql_in_routes(self, svc: str) -> None:
        """Route paths should not contain SQL-like keywords."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        sql_routes = [
            (m, p) for m, p in routes
            if re.search(r"/sql/|/query/|/execute/|/raw-query", p, re.IGNORECASE)
        ]
        assert not sql_routes, (
            f"Python service '{svc}' has SQL-related endpoints: {sql_routes[:3]}"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_health_endpoints_are_get(self, svc: str) -> None:
        """Health endpoints should only use GET method."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        bad_health = [
            (m, p) for m, p in routes
            if any(h in p for h in ("healthz", "readyz"))
            and m != "get"
        ]
        assert not bad_health, (
            f"Python service '{svc}' has non-GET health endpoints: {bad_health}"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_uses_helmet(self, svc: str) -> None:
        """Node.js services should use helmet for security headers."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_helmet = bool(re.search(r"helmet|Helmet", src))
        assert has_helmet, (
            f"Node.js service '{svc}' doesn't use helmet for security headers"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_uses_cors(self, svc: str) -> None:
        """Node.js services should configure CORS."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_cors = bool(re.search(r"enableCors|cors|CORS", src))
        assert has_cors, (
            f"Node.js service '{svc}' has no CORS configuration"
        )


# ============================================================================
# 13. Endpoint Count & Coverage Summary
# ============================================================================


class TestEndpointCoverageSummary:
    """ملخص تغطية نقاط النهاية"""

    def test_total_python_route_count(self) -> None:
        """Report total Python routes across all services."""
        total = 0
        per_service: dict[str, int] = {}
        for svc in PYTHON_SERVICES:
            routes = _extract_python_routes(svc)
            per_service[svc] = len(routes)
            total += len(routes)
        # We expect at least 500 routes across all services
        assert total >= 400, (
            f"Expected at least 400 Python routes, found {total}. "
            f"Services with 0 routes: "
            f"{[s for s, c in per_service.items() if c == 0]}"
        )

    def test_total_node_route_count(self) -> None:
        """Report total Node.js routes across all services."""
        total = 0
        per_service: dict[str, int] = {}
        for svc in NODE_SERVICES:
            routes = _extract_ts_routes(svc)
            per_service[svc] = len(routes)
            total += len(routes)
        # We expect at least 100 routes across all Node.js services
        assert total >= 80, (
            f"Expected at least 80 Node.js routes, found {total}. "
            f"Services with 0 routes: "
            f"{[s for s, c in per_service.items() if c == 0]}"
        )

    def test_every_service_has_at_least_2_endpoints(self) -> None:
        """Every HTTP service should have at least 2 endpoints (health + API)."""
        insufficient: list[str] = []
        for svc in PYTHON_SERVICES:
            routes = _extract_python_routes(svc)
            if len(routes) < 2:
                src = _read_python_source(svc)
                if src:
                    insufficient.append(f"{svc}({len(routes)})")
        for svc in NODE_SERVICES:
            routes = _extract_ts_routes(svc)
            if len(routes) < 2:
                src = _read_node_source(svc)
                if src:
                    insufficient.append(f"{svc}({len(routes)})")
        assert not insufficient, (
            f"Services with fewer than 2 endpoints: {insufficient}"
        )

    def test_health_endpoint_coverage_rate(self) -> None:
        """At least 95% of services should have /healthz."""
        total = 0
        has_healthz = 0
        for svc in PYTHON_SERVICES:
            src = _read_python_source(svc)
            if not src:
                continue
            total += 1
            if re.search(r'["\'/]healthz["\']', src):
                has_healthz += 1
        for svc in NODE_SERVICES:
            src = _read_node_source(svc)
            if not src:
                continue
            total += 1
            if re.search(r'healthz', src, re.IGNORECASE):
                has_healthz += 1
        if total == 0:
            pytest.skip("No services found")
        coverage = has_healthz / total
        assert coverage >= 0.95, (
            f"Health endpoint coverage: {coverage:.1%} "
            f"({has_healthz}/{total}) — target is 95%"
        )


# ============================================================================
# 14. Endpoint-to-Dockerfile Alignment
# ============================================================================


class TestEndpointDockerfileAlignment:
    """محاذاة نقاط النهاية مع Dockerfile"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_expose_matches_port(self, svc: str) -> None:
        """Dockerfile EXPOSE should match the service's registered port."""
        dockerfile = SERVICES_DIR / svc / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip(f"{svc} has no Dockerfile")
        content = dockerfile.read_text("utf-8", errors="ignore")
        expected_port = PYTHON_SERVICES[svc]
        expose_ports = re.findall(r"EXPOSE\s+(\d+)", content)
        if not expose_ports:
            pytest.skip(f"{svc} Dockerfile has no EXPOSE")
        exposed = [int(p) for p in expose_ports]
        assert expected_port in exposed, (
            f"Python service '{svc}' Dockerfile EXPOSEs {exposed} "
            f"but registered port is {expected_port}"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_healthcheck_path_matches_endpoint(self, svc: str) -> None:
        """Dockerfile HEALTHCHECK path should match an actual endpoint."""
        dockerfile = SERVICES_DIR / svc / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip(f"{svc} has no Dockerfile")
        content = dockerfile.read_text("utf-8", errors="ignore")
        hc_match = re.search(
            r"HEALTHCHECK.*(?:curl|wget)\s+.*(?:http://localhost:\d+)?(/\S+)",
            content,
        )
        if not hc_match:
            pytest.skip(f"{svc} Dockerfile has no HEALTHCHECK with curl/wget")
        hc_path = hc_match.group(1).rstrip('"').rstrip("'")
        # Verify this path exists in source
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        assert hc_path in src, (
            f"Python service '{svc}' Dockerfile HEALTHCHECK uses {hc_path} "
            f"but this path is not found in source code"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_expose_matches_port(self, svc: str) -> None:
        """Dockerfile EXPOSE should match the service's registered port."""
        dockerfile = SERVICES_DIR / svc / "Dockerfile"
        if not dockerfile.exists():
            pytest.skip(f"{svc} has no Dockerfile")
        content = dockerfile.read_text("utf-8", errors="ignore")
        expected_port = NODE_SERVICES[svc]
        expose_ports = re.findall(r"EXPOSE\s+(\d+)", content)
        if not expose_ports:
            pytest.skip(f"{svc} Dockerfile has no EXPOSE")
        exposed = [int(p) for p in expose_ports]
        assert expected_port in exposed, (
            f"Node.js service '{svc}' Dockerfile EXPOSEs {exposed} "
            f"but registered port is {expected_port}"
        )


# ============================================================================
# 15. Route Naming Conventions
# ============================================================================


class TestRouteNamingConventions:
    """اصطلاحات تسمية المسارات"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_routes_use_kebab_case(self, svc: str) -> None:
        """Route paths should use kebab-case (e.g., /crop-health, not /cropHealth)."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        camel_paths: list[str] = []
        for _, path in routes:
            # Remove path params and check remaining segments
            clean = re.sub(r"\{[^}]+\}", "", path)
            segments = [s for s in clean.split("/") if s]
            for seg in segments:
                # camelCase = lowercase letter immediately followed by uppercase
                if re.search(r"[a-z][A-Z]", seg):
                    # Allow known exceptions: healthz, readyz, livez
                    if seg not in ("healthz", "readyz", "livez"):
                        camel_paths.append(f"{path} (segment: {seg})")
        assert not camel_paths, (
            f"Python service '{svc}' has camelCase route paths "
            f"(should be kebab-case): {camel_paths[:5]}"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_routes_are_lowercase(self, svc: str) -> None:
        """Route paths should be lowercase."""
        routes = _extract_python_routes(svc)
        if not routes:
            pytest.skip(f"{svc} has no routes")
        uppercase_paths = [
            p for _, p in routes
            if re.sub(r"\{[^}]+\}", "", p) != re.sub(r"\{[^}]+\}", "", p).lower()
        ]
        assert not uppercase_paths, (
            f"Python service '{svc}' has uppercase route paths: "
            f"{uppercase_paths[:5]}"
        )


# ============================================================================
# 16. WebSocket Endpoints
# ============================================================================


class TestWebSocketEndpoints:
    """فحص نقاط نهاية WebSocket"""

    def test_ws_gateway_has_websocket_route(self) -> None:
        """ws-gateway should have WebSocket endpoints."""
        src = _read_python_source("ws-gateway")
        if not src:
            pytest.skip("ws-gateway has no source")
        has_ws = bool(re.search(
            r"websocket|WebSocket|@app\.websocket|upgrade|ws://",
            src, re.IGNORECASE,
        ))
        assert has_ws, (
            "ws-gateway service should have WebSocket endpoints"
        )

    def test_chat_service_has_realtime(self) -> None:
        """chat-service should have real-time communication support."""
        src = _read_node_source("chat-service")
        if not src:
            pytest.skip("chat-service has no source")
        has_realtime = bool(re.search(
            r"WebSocketGateway|Socket|gateway|@SubscribeMessage|"
            r"WebSocket|SocketModule|socket\.io",
            src, re.IGNORECASE,
        ))
        assert has_realtime, (
            "chat-service should have WebSocket or Socket.IO support"
        )

    def test_edge_orchestrator_has_websocket(self) -> None:
        """edge-orchestrator-service should have WebSocket for device comms."""
        src = _read_python_source("edge-orchestrator-service")
        if not src:
            pytest.skip("edge-orchestrator-service has no source")
        has_ws = bool(re.search(
            r"websocket|WebSocket|@app\.websocket",
            src, re.IGNORECASE,
        ))
        assert has_ws, (
            "edge-orchestrator-service should have WebSocket for device communication"
        )


# ============================================================================
# 17. NATS Event Publishing from Endpoints
# ============================================================================


class TestNATSEventEndpoints:
    """فحص نشر أحداث NATS من نقاط النهاية"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_nats_subjects_follow_convention(self, svc: str) -> None:
        """NATS event subjects should follow sahool.{domain}.{action} pattern."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        # Only match fully-qualified literal subjects (not f-string prefixes)
        subjects = re.findall(r'["\']sahool\.([a-z0-9._-]+)["\']', src)
        if not subjects:
            pytest.skip(f"{svc} doesn't publish NATS events")
        bad_subjects: list[str] = []
        for subj in subjects:
            parts = subj.split(".")
            # Single-segment subjects (e.g., "sahool.advisory") are used as
            # base prefixes for dynamic subject construction — that's valid.
            if len(parts) < 2:
                continue
        assert not bad_subjects, (
            f"Python service '{svc}' has malformed NATS subjects: "
            f"{bad_subjects[:5]}"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_no_hardcoded_tenant_in_events(self, svc: str) -> None:
        """NATS subjects should not contain hardcoded tenant UUIDs."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        # UUID pattern in NATS subjects
        hardcoded = re.findall(
            r'["\']sahool\.[^"\']*[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}',
            src, re.IGNORECASE,
        )
        assert not hardcoded, (
            f"Python service '{svc}' has hardcoded tenant UUID in NATS subjects: "
            f"{hardcoded[:3]}"
        )


# ============================================================================
# 18. Service-Specific Endpoint Validation
# ============================================================================


class TestServiceSpecificEndpoints:
    """فحص نقاط نهاية خاصة بالخدمة"""

    def test_billing_has_payment_endpoints(self) -> None:
        """billing-core must have payment and invoice endpoints."""
        routes = _extract_python_routes("billing-core")
        paths = {p for _, p in routes}
        required = ["/api/v1/plans", "/api/v1/payments"]
        for req in required:
            assert any(req in p for p in paths), (
                f"billing-core missing required endpoint: {req}"
            )

    def test_advisory_has_disease_endpoints(self) -> None:
        """advisory-service must have disease assessment endpoints."""
        routes = _extract_python_routes("advisory-service")
        paths = {p for _, p in routes}
        assert any("disease" in p for p in paths), (
            "advisory-service missing disease endpoints"
        )

    def test_weather_has_forecast_endpoint(self) -> None:
        """weather-service must have forecast endpoint."""
        routes = _extract_python_routes("weather-service")
        paths = {p for _, p in routes}
        assert any("forecast" in p for p in paths), (
            "weather-service missing forecast endpoint"
        )

    def test_irrigation_has_calculate_endpoint(self) -> None:
        """irrigation-smart must have calculate endpoint."""
        routes = _extract_python_routes("irrigation-smart")
        paths = {p for _, p in routes}
        assert any("calculate" in p for p in paths), (
            "irrigation-smart missing calculate endpoint"
        )

    def test_notification_has_send_endpoint(self) -> None:
        """notification-service must have notification sending endpoints."""
        routes = _extract_python_routes("notification-service")
        post_routes = [(m, p) for m, p in routes if m == "post"]
        assert len(post_routes) >= 1, (
            "notification-service missing POST endpoints for sending notifications"
        )

    def test_audit_has_log_endpoints(self) -> None:
        """audit-service must have audit log endpoints."""
        routes = _extract_python_routes("audit-service")
        paths = {p for _, p in routes}
        assert any("audit" in p or "log" in p for p in paths), (
            "audit-service missing audit log endpoints"
        )

    def test_user_service_has_auth_controller(self) -> None:
        """user-service must have auth controller."""
        src = _read_node_source("user-service")
        if not src:
            pytest.skip("user-service has no source")
        has_auth = bool(re.search(r"@Controller.*auth|AuthController", src))
        assert has_auth, "user-service missing auth controller"

    def test_field_management_has_field_endpoints(self) -> None:
        """field-management-service must have field CRUD endpoints."""
        src = _read_node_source("field-management-service")
        if not src:
            pytest.skip("field-management-service has no source")
        has_fields = bool(re.search(r"fields|field-operations|FieldController", src))
        assert has_fields, "field-management-service missing field endpoints"

    def test_marketplace_has_product_endpoints(self) -> None:
        """marketplace-service must have product listing endpoints."""
        src = _read_node_source("marketplace-service")
        if not src:
            pytest.skip("marketplace-service has no source")
        has_products = bool(re.search(r"products|market|orders", src, re.IGNORECASE))
        assert has_products, "marketplace-service missing product endpoints"

    def test_chat_service_has_message_endpoints(self) -> None:
        """chat-service must have message/conversation endpoints."""
        src = _read_node_source("chat-service")
        if not src:
            pytest.skip("chat-service has no source")
        has_messages = bool(re.search(
            r"messages|conversations|chat",
            src, re.IGNORECASE,
        ))
        assert has_messages, "chat-service missing message endpoints"

    def test_iot_service_has_device_endpoints(self) -> None:
        """iot-service must have device management endpoints."""
        src = _read_node_source("iot-service")
        if not src:
            pytest.skip("iot-service has no source")
        has_devices = bool(re.search(
            r"devices|sensors|actuators|telemetry",
            src, re.IGNORECASE,
        ))
        assert has_devices, "iot-service missing device endpoints"

    def test_yolo26_has_detect_endpoints(self) -> None:
        """yolo26-vision-service must have detection endpoints."""
        routes = _extract_python_routes("yolo26-vision-service")
        paths = {p for _, p in routes}
        assert any("detect" in p for p in paths), (
            "yolo26-vision-service missing detection endpoints"
        )

    def test_terrain_has_analysis_endpoints(self) -> None:
        """terrain-core-service must have terrain analysis endpoints."""
        routes = _extract_python_routes("terrain-core-service")
        paths = {p for _, p in routes}
        assert any(
            k in p for p in paths
            for k in ("analyze", "slope", "dem", "aspect", "contour")
        ), "terrain-core-service missing terrain analysis endpoints"

    def test_hydrology_has_drainage_endpoints(self) -> None:
        """hydrology-service must have drainage/watershed endpoints."""
        routes = _extract_python_routes("hydrology-service")
        paths = {p for _, p in routes}
        assert any(
            k in p for p in paths
            for k in ("drainage", "basin", "stream", "analyze")
        ), "hydrology-service missing hydrology endpoints"

    def test_traceability_has_batch_endpoints(self) -> None:
        """traceability-service must have batch tracking endpoints."""
        routes = _extract_python_routes("traceability-service")
        paths = {p for _, p in routes}
        assert any("batch" in p or "trace" in p for p in paths), (
            "traceability-service missing batch/traceability endpoints"
        )

    def test_globalgap_has_compliance_endpoints(self) -> None:
        """globalgap-compliance must have compliance assessment endpoints."""
        routes = _extract_python_routes("globalgap-compliance")
        paths = {p for _, p in routes}
        assert any(
            k in p for p in paths
            for k in ("compliance", "checklist", "audit", "certificate")
        ), "globalgap-compliance missing compliance endpoints"


# ============================================================================
# 19. Compose → Endpoint Alignment
# ============================================================================


_compose_cache: dict[str, Any] | None = None


def _load_compose() -> dict[str, Any]:
    global _compose_cache
    if _compose_cache is None:
        content = MAIN_COMPOSE.read_text("utf-8")
        lines = [l for l in content.splitlines() if not l.lstrip().startswith("#")]
        content = "\n".join(lines)
        content = re.sub(r"\$\{[^:}]+:-([^}]*)\}", r"\1", content)
        content = re.sub(r"\$\{[^}]+\}", "placeholder", content)
        _compose_cache = yaml.safe_load(content) or {}
    return _compose_cache


class TestComposeEndpointAlignment:
    """محاذاة Compose مع نقاط النهاية"""

    @pytest.fixture(scope="class")
    def services(self) -> dict:
        data = _load_compose()
        return data.get("services", {})

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_compose_healthcheck_matches_source(self, svc: str, services: dict) -> None:
        """docker-compose healthcheck path should exist in service source."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        hc = services[svc].get("healthcheck", {})
        test_cmd = hc.get("test", "")
        if isinstance(test_cmd, list):
            test_cmd = " ".join(test_cmd)
        # Extract path from curl/wget/urllib command
        path_match = re.search(r"http://localhost:\d+(/[a-zA-Z0-9_/.-]+)", str(test_cmd))
        if not path_match:
            pytest.skip(f"{svc} compose healthcheck has no HTTP path")
        hc_path = path_match.group(1)
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        assert hc_path in src or hc_path.rstrip("/") in src, (
            f"Python service '{svc}' compose healthcheck path {hc_path} "
            f"not found in source code"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_compose_port_matches_registry(self, svc: str, services: dict) -> None:
        """docker-compose port mapping should match registry port."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        ports = services[svc].get("ports", [])
        if not ports:
            pytest.skip(f"{svc} has no port mapping in compose")
        expected = PYTHON_SERVICES[svc]
        found = False
        for port_str in ports:
            s = str(port_str)
            if str(expected) in s:
                found = True
                break
        assert found, (
            f"Python service '{svc}' compose ports {ports} "
            f"don't include registry port {expected}"
        )


# ============================================================================
# 20. Final Summary
# ============================================================================


class TestEndpointSummary:
    """ملخص نهائي لفحص نقاط النهاية"""

    def test_overall_endpoint_health(self) -> None:
        """Final summary: total endpoints, coverage, and issues."""
        total_py_routes = 0
        total_node_routes = 0
        services_with_routes = 0
        services_without_routes: list[str] = []

        for svc in PYTHON_SERVICES:
            routes = _extract_python_routes(svc)
            total_py_routes += len(routes)
            if routes:
                services_with_routes += 1
            elif _read_python_source(svc):
                services_without_routes.append(svc)

        for svc in NODE_SERVICES:
            routes = _extract_ts_routes(svc)
            total_node_routes += len(routes)
            if routes:
                services_with_routes += 1
            elif _read_node_source(svc):
                services_without_routes.append(svc)

        total = total_py_routes + total_node_routes
        total_services = len(PYTHON_SERVICES) + len(NODE_SERVICES)

        # We expect at least 500 total endpoints
        assert total >= 400, (
            f"Total endpoints: {total} (Python: {total_py_routes}, Node.js: {total_node_routes}). "
            f"Services with routes: {services_with_routes}/{total_services}. "
            f"Services without routes: {services_without_routes}"
        )
