"""
SAHOOL Container Health Fix Validation Tests
=============================================
Validates the fixes for weather-service unhealthy and audit-service startup failures.

Diagnoses and validations tested:
1. asyncio.Lock() lazy initialization (no module-level Lock creation)
2. errors_py file/package conflict resolution in Dockerfiles
3. Health check start_period sufficiency (>= 30s)
4. audit-service Dockerfile copies main shared/ modules
5. Shared module import chain integrity
6. Docker-compose dependency graph correctness
7. Health endpoint validation (/healthz format and sync)
8. Dockerfile security & build validation (non-root, PYTHONPATH, HEALTHCHECK)

Run: pytest tests/container/test_container_health_fixes.py -v --tb=short
"""

import ast
import re
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"
SERVICES_DIR = REPO_ROOT / "apps" / "services"
SHARED_DIR = REPO_ROOT / "shared"
SVC_SHARED_DIR = REPO_ROOT / "apps" / "services" / "shared"

WEATHER_SERVICE_DIR = SERVICES_DIR / "weather-service"
AUDIT_SERVICE_DIR = SERVICES_DIR / "audit-service"


def _load_compose() -> dict:
    """Load main docker-compose.yml."""
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


def _read_file(path: Path) -> str:
    """Read file content safely."""
    return path.read_text(encoding="utf-8", errors="replace")


# ═══════════════════════════════════════════════════════════════════════════════
# Test 1: asyncio.Lock() Lazy Initialization
# ═══════════════════════════════════════════════════════════════════════════════


class TestAsyncioLockInitialization:
    """Verify asyncio.Lock() is NOT created at module level."""

    def test_no_module_level_asyncio_lock_in_publish(self):
        """publish.py must not create asyncio.Lock() at module level.

        Creating asyncio.Lock() before the event loop starts is deprecated
        since Python 3.10 and raises RuntimeError in 3.12+.
        """
        publish_py = WEATHER_SERVICE_DIR / "src" / "events" / "publish.py"
        assert publish_py.exists(), f"publish.py not found at {publish_py}"

        source = _read_file(publish_py)
        tree = ast.parse(source)

        module_level_lock_calls = []
        for node in ast.iter_child_nodes(tree):
            # Look for top-level assignments like:
            #   _publisher_lock = asyncio.Lock()
            #   _publisher_lock: asyncio.Lock = asyncio.Lock()
            value = None
            if isinstance(node, ast.Assign):
                value = node.value
            elif isinstance(node, ast.AnnAssign):
                value = node.value

            if isinstance(value, ast.Call):
                call = value
                # Check if it's asyncio.Lock()
                if isinstance(call.func, ast.Attribute):
                    if (
                        call.func.attr == "Lock"
                        and isinstance(call.func.value, ast.Name)
                        and call.func.value.id == "asyncio"
                    ):
                        module_level_lock_calls.append(node.lineno)

        assert len(module_level_lock_calls) == 0, (
            f"Found asyncio.Lock() at module level on line(s) {module_level_lock_calls}. "
            "asyncio.Lock() must be created lazily inside an async function."
        )

    def test_publisher_lock_initialized_as_none(self):
        """_publisher_lock should be initialized as None at module level."""
        publish_py = WEATHER_SERVICE_DIR / "src" / "events" / "publish.py"
        source = _read_file(publish_py)

        # Check that _publisher_lock is initialized to None
        assert re.search(
            r"^_publisher_lock\s*(?::\s*[^=]+)?\s*=\s*None\s*$", source, re.MULTILINE
        ), "_publisher_lock should be initialized to None at module level"

    def test_lock_created_inside_async_function(self):
        """asyncio.Lock() should be created inside get_publisher() (async context)."""
        publish_py = WEATHER_SERVICE_DIR / "src" / "events" / "publish.py"
        source = _read_file(publish_py)

        # Check that asyncio.Lock() is created inside get_publisher function
        get_publisher_match = re.search(
            r"async def get_publisher\(\).*?(?=\nasync def |\nclass |\Z)",
            source,
            re.DOTALL,
        )
        assert get_publisher_match, "get_publisher() function not found"

        func_body = get_publisher_match.group(0)
        assert "asyncio.Lock()" in func_body, (
            "asyncio.Lock() should be created inside get_publisher() for lazy initialization"
        )

    def test_no_module_level_asyncio_lock_across_all_services(self):
        """Scan all Python services for module-level asyncio.Lock() usage."""
        violations = []

        for svc_dir in SERVICES_DIR.iterdir():
            if not svc_dir.is_dir():
                continue
            for py_file in svc_dir.rglob("*.py"):
                # Skip test files and __pycache__
                if "__pycache__" in str(py_file) or "__tests__" in str(py_file):
                    continue
                try:
                    source = _read_file(py_file)
                    tree = ast.parse(source)
                except (SyntaxError, UnicodeDecodeError):
                    continue

                for node in ast.iter_child_nodes(tree):
                    value = None
                    if isinstance(node, ast.Assign):
                        value = node.value
                    elif isinstance(node, ast.AnnAssign):
                        value = node.value

                    if isinstance(value, ast.Call):
                        call = value
                        if isinstance(call.func, ast.Attribute):
                            if (
                                call.func.attr == "Lock"
                                and isinstance(call.func.value, ast.Name)
                                and call.func.value.id == "asyncio"
                            ):
                                rel = py_file.relative_to(REPO_ROOT)
                                violations.append(f"{rel}:{node.lineno}")

        assert len(violations) == 0, (
            f"Found module-level asyncio.Lock() in {len(violations)} file(s): "
            + ", ".join(violations[:10])
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Test 2: errors_py File/Package Conflict
# ═══════════════════════════════════════════════════════════════════════════════


class TestErrorsPyModuleConflict:
    """Verify errors_py file/package conflict is handled in Dockerfiles."""

    def test_shared_has_errors_py_file(self):
        """Main shared/ has errors_py.py (the file version)."""
        assert (SHARED_DIR / "errors_py.py").is_file(), (
            "shared/errors_py.py should exist as the main shared module"
        )

    def test_svc_shared_has_errors_py_package(self):
        """apps/services/shared/ has errors_py/ (the package version)."""
        assert (SVC_SHARED_DIR / "errors_py").is_dir(), (
            "apps/services/shared/errors_py/ should exist as a package"
        )
        assert (SVC_SHARED_DIR / "errors_py" / "__init__.py").is_file(), (
            "apps/services/shared/errors_py/__init__.py must exist"
        )

    def test_weather_dockerfile_removes_errors_py_file(self):
        """Weather-service Dockerfile must remove errors_py.py after COPY overlay."""
        dockerfile = WEATHER_SERVICE_DIR / "Dockerfile"
        content = _read_file(dockerfile)

        # Verify rm targets the correct shared path (not a typo like s/shared)
        assert re.search(
            r"rm\s+-f\s+(?:\./shared|/app/shared)/errors_py\.py", content
        ), (
            "Weather-service Dockerfile must remove shared/errors_py.py "
            "using correct path (./shared/ or /app/shared/)"
        )

    def test_audit_dockerfile_removes_errors_py_file(self):
        """Audit-service Dockerfile must remove errors_py.py after COPY overlay."""
        dockerfile = AUDIT_SERVICE_DIR / "Dockerfile"
        content = _read_file(dockerfile)

        assert re.search(
            r"rm\s+-f\s+(?:\./shared|/app/shared)/errors_py\.py", content
        ), (
            "Audit-service Dockerfile must remove shared/errors_py.py "
            "using correct path (./shared/ or /app/shared/)"
        )

    def test_errors_py_package_exports_required_symbols(self):
        """The errors_py package must export all symbols needed by services."""
        init_py = SVC_SHARED_DIR / "errors_py" / "__init__.py"
        content = _read_file(init_py)

        required_exports = [
            "ExternalServiceException",
            "InternalServerException",
            "add_request_id_middleware",
            "setup_exception_handlers",
            "AppException",
            "ValidationException",
            "NotFoundException",
        ]
        for symbol in required_exports:
            assert symbol in content, (
                f"errors_py package __init__.py must export '{symbol}'"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Test 3: Health Check Configuration
# ═══════════════════════════════════════════════════════════════════════════════


class TestHealthCheckConfiguration:
    """Verify health check timing is sufficient for cold starts."""

    MIN_START_PERIOD_SECONDS = 30  # Minimum acceptable start_period

    @pytest.fixture(scope="class")
    def compose(self):
        return _load_compose()

    def _parse_duration(self, duration_str: str) -> int:
        """Parse Docker duration string to seconds."""
        if duration_str.endswith("s"):
            return int(duration_str[:-1])
        if duration_str.endswith("m"):
            return int(duration_str[:-1]) * 60
        return int(duration_str)

    def test_weather_service_start_period(self, compose):
        """weather-service start_period must be >= 30s."""
        svc = compose["services"]["weather-service"]
        hc = svc.get("healthcheck", {})
        start_period = self._parse_duration(hc.get("start_period", "0s"))

        assert start_period >= self.MIN_START_PERIOD_SECONDS, (
            f"weather-service start_period is {start_period}s, "
            f"must be >= {self.MIN_START_PERIOD_SECONDS}s for cold starts"
        )

    def test_audit_service_start_period(self, compose):
        """audit-service start_period must be >= 30s."""
        svc = compose["services"]["audit-service"]
        hc = svc.get("healthcheck", {})
        start_period = self._parse_duration(hc.get("start_period", "0s"))

        assert start_period >= self.MIN_START_PERIOD_SECONDS, (
            f"audit-service start_period is {start_period}s, "
            f"must be >= {self.MIN_START_PERIOD_SECONDS}s for cold starts"
        )

    def test_weather_dockerfile_start_period_matches_compose(self, compose):
        """Dockerfile and docker-compose start_period should be consistent."""
        dockerfile = WEATHER_SERVICE_DIR / "Dockerfile"
        content = _read_file(dockerfile)

        # Extract start-period from Dockerfile HEALTHCHECK
        df_match = re.search(r"--start-period=(\d+s)", content)
        assert df_match, "Dockerfile must have HEALTHCHECK --start-period"
        df_period = self._parse_duration(df_match.group(1))

        # Extract from compose
        svc = compose["services"]["weather-service"]
        compose_period = self._parse_duration(
            svc.get("healthcheck", {}).get("start_period", "0s")
        )

        assert df_period == compose_period, (
            f"Dockerfile start-period ({df_period}s) != "
            f"docker-compose start_period ({compose_period}s)"
        )

    def test_audit_dockerfile_start_period_matches_compose(self, compose):
        """Dockerfile and docker-compose start_period should be consistent."""
        dockerfile = AUDIT_SERVICE_DIR / "Dockerfile"
        content = _read_file(dockerfile)

        df_match = re.search(r"--start-period=(\d+s)", content)
        assert df_match, "Dockerfile must have HEALTHCHECK --start-period"
        df_period = self._parse_duration(df_match.group(1))

        svc = compose["services"]["audit-service"]
        compose_period = self._parse_duration(
            svc.get("healthcheck", {}).get("start_period", "0s")
        )

        assert df_period == compose_period, (
            f"Dockerfile start-period ({df_period}s) != "
            f"docker-compose start_period ({compose_period}s)"
        )

    @pytest.mark.parametrize(
        "service_name",
        ["weather-service", "audit-service"],
    )
    def test_fixed_services_start_period_sufficient(self, compose, service_name):
        """Fixed services must have start_period >= 30s."""
        svc = compose["services"][service_name]
        hc = svc.get("healthcheck", {})
        start_period = self._parse_duration(hc.get("start_period", "0s"))

        assert start_period >= self.MIN_START_PERIOD_SECONDS, (
            f"{service_name} start_period is {start_period}s, "
            f"must be >= {self.MIN_START_PERIOD_SECONDS}s"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Test 4: Audit Service Dockerfile Shared Modules
# ═══════════════════════════════════════════════════════════════════════════════


class TestAuditServiceDockerfile:
    """Verify audit-service Dockerfile copies all required shared modules."""

    def test_copies_main_shared_directory(self):
        """audit-service Dockerfile must COPY shared/ (main) before overlay."""
        dockerfile = AUDIT_SERVICE_DIR / "Dockerfile"
        content = _read_file(dockerfile)

        # Must have COPY shared/ before COPY apps/services/shared/
        main_copy = re.search(r"COPY.*\bshared/\s+\./shared/", content)
        svc_copy = re.search(r"COPY.*apps/services/shared/\s+\./shared/", content)

        assert main_copy, (
            "audit-service Dockerfile must COPY shared/ ./shared/ "
            "(main shared modules)"
        )
        assert svc_copy, (
            "audit-service Dockerfile must COPY apps/services/shared/ ./shared/ "
            "(service-specific overlay)"
        )

        # main shared/ must come BEFORE service shared/
        assert main_copy.start() < svc_copy.start(), (
            "COPY shared/ must come BEFORE COPY apps/services/shared/ "
            "to ensure proper overlay ordering"
        )

    def test_weather_service_same_copy_pattern(self):
        """weather-service should follow the same COPY pattern."""
        dockerfile = WEATHER_SERVICE_DIR / "Dockerfile"
        content = _read_file(dockerfile)

        main_copy = re.search(r"COPY.*\bshared/\s+/app/shared/", content)
        svc_copy = re.search(r"COPY.*apps/services/shared/\s+/app/shared/", content)

        assert main_copy, "weather-service must COPY shared/ /app/shared/"
        assert svc_copy, "weather-service must COPY apps/services/shared/ /app/shared/"
        assert main_copy.start() < svc_copy.start(), (
            "COPY shared/ must come BEFORE COPY apps/services/shared/"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Test 5: Shared Module Import Chain Integrity
# ═══════════════════════════════════════════════════════════════════════════════


class TestSharedModuleImportChain:
    """Verify all shared module imports can resolve correctly."""

    def test_svc_shared_auth_self_contained(self):
        """apps/services/shared/auth/ must have all files imported by __init__.py."""
        auth_dir = SVC_SHARED_DIR / "auth"
        init_py = auth_dir / "__init__.py"
        content = _read_file(init_py)

        # Extract relative imports: from .xxx import ...
        imported_modules = re.findall(r"from \.([\w]+) import", content)

        for mod in imported_modules:
            mod_file = auth_dir / f"{mod}.py"
            assert mod_file.exists(), (
                f"auth/__init__.py imports from .{mod} but "
                f"{mod}.py not found in {auth_dir}"
            )

    def test_svc_shared_errors_py_self_contained(self):
        """apps/services/shared/errors_py/ must have all sub-modules."""
        pkg_dir = SVC_SHARED_DIR / "errors_py"
        init_py = pkg_dir / "__init__.py"
        content = _read_file(init_py)

        imported_modules = re.findall(r"from \.([\w]+) import", content)

        for mod in imported_modules:
            mod_file = pkg_dir / f"{mod}.py"
            assert mod_file.exists(), (
                f"errors_py/__init__.py imports from .{mod} but "
                f"{mod}.py not found in {pkg_dir}"
            )

    def test_svc_shared_middleware_self_contained(self):
        """apps/services/shared/middleware/ must have all sub-modules."""
        mw_dir = SVC_SHARED_DIR / "middleware"
        init_py = mw_dir / "__init__.py"
        content = _read_file(init_py)

        imported_modules = re.findall(r"from \.([\w]+) import", content)

        for mod in imported_modules:
            mod_file = mw_dir / f"{mod}.py"
            assert mod_file.exists(), (
                f"middleware/__init__.py imports from .{mod} but "
                f"{mod}.py not found in {mw_dir}"
            )

    def test_weather_service_imports_resolve(self):
        """All top-level imports in weather-service main.py must resolve."""
        main_py = WEATHER_SERVICE_DIR / "src" / "main.py"
        assert main_py.exists(), f"weather-service main.py not found at {main_py}"

        # Check mandatory imports (not wrapped in try/except)
        mandatory_imports = [
            ("shared.auth.dependencies", "get_current_user"),
            ("shared.auth.models", "User"),
            ("shared.errors_py", "ExternalServiceException"),
            ("shared.errors_py", "InternalServerException"),
            ("shared.errors_py", "add_request_id_middleware"),
            ("shared.errors_py", "setup_exception_handlers"),
        ]

        for module, symbol in mandatory_imports:
            parts = module.split(".")
            if parts[0] == "shared":
                # Check in apps/services/shared/ (which overlays main shared/)
                sub_path = "/".join(parts[1:])

                # Could be a file or package
                file_path = SVC_SHARED_DIR / f"{sub_path}.py"
                pkg_init = SVC_SHARED_DIR / sub_path / "__init__.py"
                main_file = SHARED_DIR / f"{sub_path}.py"
                main_pkg = SHARED_DIR / sub_path / "__init__.py"

                found = (
                    file_path.exists()
                    or pkg_init.exists()
                    or main_file.exists()
                    or main_pkg.exists()
                )
                assert found, (
                    f"Import '{module}.{symbol}' cannot resolve: "
                    f"neither {file_path} nor {pkg_init} nor "
                    f"{main_file} nor {main_pkg} exists"
                )

    def test_audit_service_imports_resolve(self):
        """All top-level imports in audit-service main.py must resolve."""
        main_py = AUDIT_SERVICE_DIR / "src" / "main.py"
        assert main_py.exists(), f"audit-service main.py not found at {main_py}"

        # Extract non-try/except shared imports
        mandatory_imports = [
            ("shared.auth.dependencies", "get_current_user"),
            ("shared.errors_py", "add_request_id_middleware"),
            ("shared.errors_py", "setup_exception_handlers"),
            ("shared.middleware.tenant_context", "TenantContextMiddleware"),
        ]

        for module, symbol in mandatory_imports:
            parts = module.split(".")
            if parts[0] == "shared":
                sub_path = "/".join(parts[1:])
                file_path = SVC_SHARED_DIR / f"{sub_path}.py"
                pkg_init = SVC_SHARED_DIR / sub_path / "__init__.py"
                main_file = SHARED_DIR / f"{sub_path}.py"
                main_pkg = SHARED_DIR / sub_path / "__init__.py"

                found = (
                    file_path.exists()
                    or pkg_init.exists()
                    or main_file.exists()
                    or main_pkg.exists()
                )
                assert found, (
                    f"Import '{module}.{symbol}' cannot resolve for audit-service"
                )


# ═══════════════════════════════════════════════════════════════════════════════
# Test 6: Docker-Compose Dependency Graph
# ═══════════════════════════════════════════════════════════════════════════════


class TestDependencyGraph:
    """Verify dependency graph is correct and won't cause cascade failures."""

    @pytest.fixture(scope="class")
    def compose(self):
        return _load_compose()

    def test_audit_service_does_not_depend_on_weather(self, compose):
        """audit-service must NOT depend on weather-service."""
        svc = compose["services"]["audit-service"]
        deps = svc.get("depends_on", {})
        dep_names = list(deps.keys()) if isinstance(deps, dict) else deps

        assert "weather-service" not in dep_names, (
            "audit-service should NOT depend on weather-service"
        )

    def test_weather_service_depends_only_on_infra(self, compose):
        """weather-service should only depend on infrastructure services."""
        svc = compose["services"]["weather-service"]
        deps = svc.get("depends_on", {})
        dep_names = set(deps.keys()) if isinstance(deps, dict) else set(deps)

        infra_services = {"postgres", "pgbouncer", "redis", "nats", "vault", "kong", "etcd"}
        non_infra = dep_names - infra_services
        assert len(non_infra) == 0, (
            f"weather-service depends on non-infrastructure services: {non_infra}"
        )

    def test_audit_service_depends_only_on_infra(self, compose):
        """audit-service should only depend on infrastructure services."""
        svc = compose["services"]["audit-service"]
        deps = svc.get("depends_on", {})
        dep_names = set(deps.keys()) if isinstance(deps, dict) else set(deps)

        infra_services = {"postgres", "pgbouncer", "redis", "nats", "vault", "kong", "etcd"}
        non_infra = dep_names - infra_services
        assert len(non_infra) == 0, (
            f"audit-service depends on non-infrastructure services: {non_infra}"
        )

    def test_all_healthy_dependencies_exist(self, compose):
        """Every service_healthy dependency must reference an existing service."""
        services = compose.get("services", {})
        violations = []

        for svc_name, svc_config in services.items():
            deps = svc_config.get("depends_on", {})
            if not isinstance(deps, dict):
                continue
            for dep_name, dep_config in deps.items():
                if isinstance(dep_config, dict) and dep_config.get("condition") == "service_healthy":
                    if dep_name not in services:
                        violations.append(f"{svc_name} -> {dep_name}")

        assert len(violations) == 0, (
            f"Services reference non-existent healthy dependencies: {violations}"
        )

    def test_services_with_healthy_deps_have_healthchecks(self, compose):
        """Every service referenced with service_healthy must define a healthcheck."""
        services = compose.get("services", {})
        deps_needing_healthcheck = set()

        for svc_config in services.values():
            deps = svc_config.get("depends_on", {})
            if not isinstance(deps, dict):
                continue
            for dep_name, dep_config in deps.items():
                if isinstance(dep_config, dict) and dep_config.get("condition") == "service_healthy":
                    deps_needing_healthcheck.add(dep_name)

        missing_healthcheck = []
        for dep_name in deps_needing_healthcheck:
            if dep_name in services:
                svc = services[dep_name]
                if "healthcheck" not in svc:
                    # Check if the service uses an image with built-in healthcheck
                    if "build" in svc:
                        # Built service - check Dockerfile has HEALTHCHECK
                        missing_healthcheck.append(dep_name)

        # Filter out services that define HEALTHCHECK in their Dockerfile
        # (not visible in compose, but still valid for Docker health checks).
        truly_missing = []
        for svc_name in missing_healthcheck:
            dockerfile = SERVICES_DIR / svc_name / "Dockerfile"
            if dockerfile.exists():
                content = _read_file(dockerfile)
                if "HEALTHCHECK" in content:
                    continue  # Has Dockerfile-level healthcheck
            truly_missing.append(svc_name)

        assert len(truly_missing) == 0, (
            f"Services depended on as service_healthy but missing healthcheck "
            f"(neither in compose nor Dockerfile): {truly_missing}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Test 7: Health Endpoint Validation
# ═══════════════════════════════════════════════════════════════════════════════


class TestHealthEndpointValidation:
    """Verify health endpoints exist and return correct format."""

    def test_weather_service_has_healthz_endpoint(self):
        """weather-service must define /healthz endpoint."""
        main_py = WEATHER_SERVICE_DIR / "src" / "main.py"
        content = _read_file(main_py)

        assert re.search(r'@app\.get\(\s*["\']/?healthz["\']', content), (
            "weather-service must define @app.get('/healthz') endpoint"
        )

    def test_audit_service_has_healthz_endpoint(self):
        """audit-service must define /healthz endpoint."""
        main_py = AUDIT_SERVICE_DIR / "src" / "main.py"
        content = _read_file(main_py)

        assert re.search(r'@app\.get\(\s*["\']/?healthz["\']', content), (
            "audit-service must define @app.get('/healthz') endpoint"
        )

    def test_weather_healthz_returns_status_field(self):
        """weather-service /healthz must return 'status' field."""
        main_py = WEATHER_SERVICE_DIR / "src" / "main.py"
        content = _read_file(main_py)

        # Find the healthz function body
        match = re.search(
            r'@app\.get\(\s*["\']/?healthz["\']\s*\)\s*\n'
            r'(?:async )?def \w+\([^)]*\).*?(?=\n@|\nclass |\Z)',
            content,
            re.DOTALL,
        )
        assert match, "/healthz endpoint not found"
        func_body = match.group(0)
        assert '"status"' in func_body or "'status'" in func_body, (
            "/healthz must return a response containing 'status' field"
        )

    def test_weather_healthz_not_async_dependent(self):
        """weather-service /healthz should be sync (no DB/NATS checks for liveness)."""
        main_py = WEATHER_SERVICE_DIR / "src" / "main.py"
        content = _read_file(main_py)

        match = re.search(
            r'@app\.get\(\s*["\']/?healthz["\']\s*\)\s*\n(async )?def',
            content,
        )
        assert match, "/healthz endpoint not found"
        # Liveness probe should be sync (no await = no dependency on external services)
        assert match.group(1) is None, (
            "/healthz (liveness probe) should be a sync function to avoid "
            "false unhealthy status when external dependencies are slow"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Test 8: Dockerfile Security & Build Validation
# ═══════════════════════════════════════════════════════════════════════════════


class TestDockerfileBuildValidation:
    """Verify Dockerfiles follow security and build best practices."""

    @pytest.mark.parametrize(
        "service_name",
        ["weather-service", "audit-service"],
    )
    def test_non_root_user(self, service_name):
        """Service must run as non-root user."""
        dockerfile = SERVICES_DIR / service_name / "Dockerfile"
        content = _read_file(dockerfile)

        assert re.search(r"^USER\s+sahool", content, re.MULTILINE), (
            f"{service_name} Dockerfile must switch to non-root user 'sahool'"
        )

    @pytest.mark.parametrize(
        "service_name",
        ["weather-service", "audit-service"],
    )
    def test_pythonpath_set(self, service_name):
        """PYTHONPATH must be set to /app for shared module resolution."""
        dockerfile = SERVICES_DIR / service_name / "Dockerfile"
        content = _read_file(dockerfile)

        assert "PYTHONPATH" in content, (
            f"{service_name} Dockerfile must set PYTHONPATH"
        )

    @pytest.mark.parametrize(
        "service_name",
        ["weather-service", "audit-service"],
    )
    def test_healthcheck_directive_exists(self, service_name):
        """Dockerfile must have a HEALTHCHECK directive."""
        dockerfile = SERVICES_DIR / service_name / "Dockerfile"
        content = _read_file(dockerfile)

        assert "HEALTHCHECK" in content, (
            f"{service_name} Dockerfile must have HEALTHCHECK directive"
        )
