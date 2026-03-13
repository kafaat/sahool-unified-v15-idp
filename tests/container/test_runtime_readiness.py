"""
SAHOOL Container Runtime Readiness Tests
==========================================
اختبارات جاهزية التشغيل لجميع حاويات سهول

Validates that services are structurally ready to run at container startup.
All tests are static (parse files only – no Docker daemon, no network).

Coverage:
1.  Python module structure     – __init__.py, FastAPI app, lifespan
2.  Python entrypoint validity  – valid syntax, CMD module exists
3.  Node.js entrypoint validity – entry files, tsconfig, scripts
4.  Environment configuration   – required env vars, no hardcoded secrets
5.  Compose service config      – container naming, healthcheck timing
6.  Python import chain         – shared/ imports resolve
7.  Service README presence     – documentation completeness

Run:
    pytest tests/container/test_runtime_readiness.py -v --tb=short
    pytest tests/container/test_runtime_readiness.py -v -n auto
"""

from __future__ import annotations

import ast
import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.container.service_registry import (
    ALL_HTTP_SERVICES,
    INFRA_SERVICES,
    NODE_SERVICES,
    PORTLESS_SERVICES,
    PYTHON_SERVICES,
)

pytestmark = [pytest.mark.container, pytest.mark.smoke]

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _main_py(svc: str) -> Path | None:
    """Return path to main.py for a Python service."""
    for candidate in [
        SERVICES_DIR / svc / "src" / "main.py",
        SERVICES_DIR / svc / "main.py",
    ]:
        if candidate.exists():
            return candidate
    return None


def _read_dockerfile(svc: str) -> str:
    path = SERVICES_DIR / svc / "Dockerfile"
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""


def _env_str(svc_def: dict) -> str:
    env = svc_def.get("environment", {})
    if isinstance(env, dict):
        return " ".join(f"{k}={v}" for k, v in env.items())
    if isinstance(env, list):
        return " ".join(str(e) for e in env)
    return ""


# ===========================================================================
# 1. Python Module Structure
# ===========================================================================


class TestPythonModuleStructure:
    """Python service source must follow correct module patterns.
    يجب أن تتبع مصادر خدمات Python أنماط الوحدات الصحيحة."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_src_has_init_py(self, svc_name: str) -> None:
        """src/ directory must have __init__.py for proper module resolution."""
        init = SERVICES_DIR / svc_name / "src" / "__init__.py"
        assert init.exists(), (
            f"{svc_name}/src/__init__.py missing – Python module resolution will fail"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_main_py_exists(self, svc_name: str) -> None:
        """Service must have a main.py entry point."""
        main = _main_py(svc_name)
        assert main is not None, f"{svc_name} has no src/main.py entry point"

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_main_py_defines_fastapi_app(self, svc_name: str) -> None:
        """main.py must define a FastAPI application variable."""
        main = _main_py(svc_name)
        if main is None:
            pytest.skip(f"No main.py for {svc_name}")
        content = main.read_text(errors="replace")
        has_app = bool(re.search(
            r"app\s*=\s*FastAPI\(|FastAPI\(\s*\n",
            content,
        ))
        assert has_app, f"{svc_name}/main.py does not define 'app = FastAPI(...)'"

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_main_py_imports_fastapi(self, svc_name: str) -> None:
        """main.py must import FastAPI."""
        main = _main_py(svc_name)
        if main is None:
            pytest.skip(f"No main.py for {svc_name}")
        content = main.read_text(errors="replace")
        assert "from fastapi" in content or "import fastapi" in content, (
            f"{svc_name}/main.py does not import FastAPI"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_main_py_has_lifespan_pattern(self, svc_name: str) -> None:
        """main.py should use lifespan or startup/shutdown event handlers."""
        main = _main_py(svc_name)
        if main is None:
            pytest.skip(f"No main.py for {svc_name}")
        content = main.read_text(errors="replace")
        has_lifespan = bool(re.search(
            r"lifespan|asynccontextmanager|on_event.*startup|on_event.*shutdown"
            r"|async\s+def\s+startup|async\s+def\s+shutdown|@app\.\w+event",
            content,
            re.IGNORECASE,
        ))
        if not has_lifespan:
            # Some services use inline setup or don't need lifecycle management
            pytest.xfail(
                f"{svc_name}/main.py has no lifespan or startup/shutdown handler "
                f"(recommended for proper resource cleanup)"
            )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_api_dir_has_init_py(self, svc_name: str) -> None:
        """If src/api/ exists, it must have __init__.py."""
        api_dir = SERVICES_DIR / svc_name / "src" / "api"
        if not api_dir.is_dir():
            pytest.skip(f"{svc_name} has no src/api/ directory")
        init = api_dir / "__init__.py"
        assert init.exists(), f"{svc_name}/src/api/__init__.py missing"


# ===========================================================================
# 2. Python Entrypoint Validity
# ===========================================================================


class TestPythonEntrypointValidity:
    """Python source must be syntactically valid.
    يجب أن تكون مصادر Python صحيحة نحوياً."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_main_py_valid_syntax(self, svc_name: str) -> None:
        """main.py must be valid Python syntax (compile check)."""
        main = _main_py(svc_name)
        if main is None:
            pytest.skip(f"No main.py for {svc_name}")
        source = main.read_text(errors="replace")
        try:
            ast.parse(source, filename=str(main))
        except SyntaxError as e:
            pytest.fail(f"{svc_name}/main.py has SyntaxError: {e}")

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_no_syntax_errors_in_src(self, svc_name: str) -> None:
        """No .py file under src/ should have syntax errors."""
        src_dir = SERVICES_DIR / svc_name / "src"
        if not src_dir.is_dir():
            pytest.skip(f"No src/ for {svc_name}")
        errors: list[str] = []
        for py_file in src_dir.rglob("*.py"):
            try:
                ast.parse(py_file.read_text(errors="replace"), filename=str(py_file))
            except SyntaxError as e:
                errors.append(f"{py_file.relative_to(REPO_ROOT)}: {e}")
        assert not errors, (
            f"{svc_name} has Python syntax errors:\n"
            + "\n".join(f"  {e}" for e in errors[:5])
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_dockerfile_cmd_module_exists(self, svc_name: str) -> None:
        """CMD in Dockerfile must reference a module that exists."""
        content = _read_dockerfile(svc_name)
        if not content:
            pytest.skip(f"No Dockerfile for {svc_name}")
        # Look for patterns like: src.main, src.main:app
        match = re.search(r"src\.main", content)
        if not match:
            pytest.skip(f"{svc_name} CMD does not reference src.main")
        main = SERVICES_DIR / svc_name / "src" / "main.py"
        assert main.exists(), (
            f"{svc_name} Dockerfile CMD references src.main but file doesn't exist"
        )


# ===========================================================================
# 3. Node.js Entrypoint Validity
# ===========================================================================


class TestNodeEntrypointValidity:
    """Node.js service entry points must be valid.
    يجب أن تكون نقاط دخول Node.js صالحة."""

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_entry_file_exists(self, svc_name: str) -> None:
        """src/index.ts or src/main.ts must exist."""
        svc_dir = SERVICES_DIR / svc_name
        has_entry = (
            (svc_dir / "src" / "index.ts").exists()
            or (svc_dir / "src" / "main.ts").exists()
        )
        assert has_entry, f"{svc_name} missing src/index.ts or src/main.ts"

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_tsconfig_exists_and_valid(self, svc_name: str) -> None:
        """tsconfig.json must exist and be valid JSON."""
        tsconfig = SERVICES_DIR / svc_name / "tsconfig.json"
        if not tsconfig.exists():
            # Some NestJS services use tsconfig.build.json
            tsconfig = SERVICES_DIR / svc_name / "tsconfig.build.json"
        assert tsconfig.exists(), f"{svc_name} missing tsconfig.json"
        try:
            # tsconfig allows comments, use a lenient parse
            content = tsconfig.read_text(encoding="utf-8")
            # Strip single-line comments for parsing
            stripped = re.sub(r"//.*$", "", content, flags=re.MULTILINE)
            # Strip trailing commas
            stripped = re.sub(r",\s*([\]}])", r"\1", stripped)
            json.loads(stripped)
        except (json.JSONDecodeError, ValueError) as e:
            pytest.fail(f"{svc_name}/tsconfig.json is invalid: {e}")

    @pytest.mark.parametrize("svc_name", sorted(NODE_SERVICES))
    def test_package_json_has_start_or_build(self, svc_name: str) -> None:
        """package.json must have start or build script."""
        pkg = SERVICES_DIR / svc_name / "package.json"
        if not pkg.exists():
            pytest.skip(f"No package.json for {svc_name}")
        data = json.loads(pkg.read_text(encoding="utf-8"))
        scripts = data.get("scripts", {})
        assert "start" in scripts or "build" in scripts or "start:prod" in scripts, (
            f"{svc_name}/package.json missing start/build script"
        )


# ===========================================================================
# 4. Environment Configuration
# ===========================================================================


class TestEnvironmentConfiguration:
    """Critical env vars must be set in docker-compose.yml.
    يجب تعيين متغيرات البيئة الحرجة في docker-compose.yml."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_environment_var_set(self, services: dict, svc_name: str) -> None:
        """Service must declare ENVIRONMENT or NODE_ENV."""
        svc = services.get(svc_name, {})
        env = _env_str(svc)
        has_env = "ENVIRONMENT=" in env or "NODE_ENV=" in env
        assert has_env, f"'{svc_name}' missing ENVIRONMENT or NODE_ENV"

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_python_log_level_set(self, services: dict, svc_name: str) -> None:
        """Python services must set LOG_LEVEL."""
        svc = services.get(svc_name, {})
        env = _env_str(svc)
        assert "LOG_LEVEL=" in env, f"'{svc_name}' missing LOG_LEVEL env var"

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_no_hardcoded_production_passwords(
        self, services: dict, svc_name: str
    ) -> None:
        """No hardcoded production passwords in environment section."""
        svc = services.get(svc_name, {})
        env = svc.get("environment", {})
        if isinstance(env, dict):
            items = list(env.items())
        elif isinstance(env, list):
            items = []
            for e in env:
                if "=" in str(e):
                    k, v = str(e).split("=", 1)
                    items.append((k, v))
        else:
            items = []

        for key, value in items:
            key_upper = key.upper()
            if any(s in key_upper for s in ["PASSWORD", "SECRET", "API_KEY", "TOKEN"]):
                val_str = str(value)
                # Should use ${VAR} substitution, not a literal
                if not val_str.startswith("${") and len(val_str) > 8:
                    # Allow known test values
                    if "test" not in val_str.lower() and "changeme" not in val_str.lower():
                        pytest.fail(
                            f"'{svc_name}' has hardcoded credential in env: "
                            f"{key}={val_str[:20]}..."
                        )


# ===========================================================================
# 5. Compose Service Configuration
# ===========================================================================


class TestComposeServiceConfiguration:
    """Compose services must be properly configured.
    يجب تكوين خدمات Compose بشكل صحيح."""

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_service_has_restart_policy(self, services: dict, svc_name: str) -> None:
        """Every service must have a restart policy."""
        svc = services.get(svc_name, {})
        assert "restart" in svc, f"'{svc_name}' missing restart policy"

    @pytest.mark.parametrize("svc_name", sorted(ALL_HTTP_SERVICES))
    def test_healthcheck_interval_reasonable(
        self, services: dict, svc_name: str
    ) -> None:
        """Compose healthcheck interval should be <= 60s if defined."""
        svc = services.get(svc_name, {})
        hc = svc.get("healthcheck", {})
        if not hc:
            pytest.skip(f"{svc_name} has no compose healthcheck")
        interval = hc.get("interval", "")
        if not interval:
            pytest.skip(f"{svc_name} healthcheck has no interval")
        # Parse interval like "30s", "1m"
        if isinstance(interval, str):
            if interval.endswith("s"):
                secs = int(interval[:-1])
            elif interval.endswith("m"):
                secs = int(interval[:-1]) * 60
            else:
                pytest.skip(f"Cannot parse interval: {interval}")
            assert secs <= 60, (
                f"'{svc_name}' healthcheck interval {interval} exceeds 60s"
            )


# ===========================================================================
# 6. Python Import Chain Validation
# ===========================================================================


class TestPythonImportChain:
    """Imports from shared/ must reference existing modules.
    يجب أن تشير الاستيرادات من shared/ إلى وحدات موجودة."""

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_shared_imports_resolve(self, svc_name: str) -> None:
        """Imports from shared.* must reference directories that exist."""
        main = _main_py(svc_name)
        if main is None:
            pytest.skip(f"No main.py for {svc_name}")
        content = main.read_text(errors="replace")
        # Find all "from shared.xxx" or "import shared.xxx" patterns
        shared_imports = re.findall(
            r"(?:from|import)\s+(shared\.\w+)", content
        )
        missing: list[str] = []
        for imp in shared_imports:
            # shared.auth -> shared/auth/
            parts = imp.split(".")
            if len(parts) >= 2:
                module_dir = REPO_ROOT / "shared" / parts[1]
                module_file = REPO_ROOT / "shared" / f"{parts[1]}.py"
                if not module_dir.is_dir() and not module_file.exists():
                    missing.append(imp)
        assert not missing, (
            f"{svc_name} imports non-existent shared modules: {missing}"
        )

    @pytest.mark.parametrize("svc_name", sorted(PYTHON_SERVICES))
    def test_no_imports_from_deprecated(self, svc_name: str) -> None:
        """No imports from deprecated/archived service code."""
        src_dir = SERVICES_DIR / svc_name / "src"
        if not src_dir.is_dir():
            pytest.skip(f"No src/ for {svc_name}")
        deprecated = {
            "satellite-service", "weather-advanced", "crop-health-ai",
            "crop-health", "fertilizer-advisor", "field-ops",
            "field-core", "field-service", "agro-advisor", "ndvi-engine",
        }
        violations: list[str] = []
        for py_file in src_dir.rglob("*.py"):
            content = py_file.read_text(errors="replace")
            for dep_svc in deprecated:
                # Convert to module name: field-ops -> field_ops
                module_name = dep_svc.replace("-", "_")
                if f"from {module_name}" in content or f"import {module_name}" in content:
                    violations.append(
                        f"{py_file.relative_to(REPO_ROOT)}: imports {dep_svc}"
                    )
        assert not violations, (
            f"{svc_name} imports from deprecated services:\n"
            + "\n".join(f"  {v}" for v in violations[:5])
        )


# ===========================================================================
# 7. Service README Presence
# ===========================================================================


class TestServiceReadmePresence:
    """Every service must have documentation.
    يجب أن يكون لكل خدمة وثائق."""

    @pytest.mark.parametrize(
        "svc_name", sorted({**PYTHON_SERVICES, **NODE_SERVICES})
    )
    def test_readme_exists(self, svc_name: str) -> None:
        """Service must have a README.md file."""
        readme = SERVICES_DIR / svc_name / "README.md"
        assert readme.exists(), f"{svc_name} missing README.md"

    @pytest.mark.parametrize(
        "svc_name", sorted({**PYTHON_SERVICES, **NODE_SERVICES})
    )
    def test_readme_not_trivial(self, svc_name: str) -> None:
        """README must have at least 10 lines of content."""
        readme = SERVICES_DIR / svc_name / "README.md"
        if not readme.exists():
            pytest.skip(f"No README for {svc_name}")
        lines = readme.read_text(errors="replace").splitlines()
        assert len(lines) >= 10, (
            f"{svc_name}/README.md has only {len(lines)} lines – too short"
        )
