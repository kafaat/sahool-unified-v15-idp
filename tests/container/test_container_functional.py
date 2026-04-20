"""
SAHOOL Comprehensive Container Functional Tests – All Services
================================================================
اختبارات وظيفية شاملة لجميع الحاويات والخدمات

Validates the **functional correctness** of every container:
- Service entry points exist and follow platform patterns
- API routes are defined (not stub services)
- Database, NATS, and Redis connectivity patterns
- Environment variable usage consistency
- Dockerfile ↔ source code alignment
- Shared module imports and usage
- Security patterns (auth, CORS, rate limiting)
- Service version consistency
- Structured logging configuration

All tests are **static analysis** — no Docker daemon required.

Run:
    pytest tests/container/test_container_functional.py -v --tb=short
    pytest tests/container/test_container_functional.py -v -n auto  # parallel

Arabic summary:
    يتحقق هذا الملف من الصحة الوظيفية لكل خدمة: نقاط الدخول، مسارات API،
    أنماط الاتصال بقواعد البيانات، واتساق متغيرات البيئة.
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

pytestmark = [pytest.mark.container, pytest.mark.smoke]

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"
SERVICES_DIR = REPO_ROOT / "apps" / "services"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Services excluded from registry validation because they are registered
# in separate categories (GPU_SERVICES, DEPRECATED_SERVICES).
_REGISTRY_EXEMPT_SERVICES: set[str] = {"wechat-service", "vllm-deepseek"}

# Placeholder/test values to exclude from hardcoded-secret detection.
_SECRET_PLACEHOLDER_RE = re.compile(
    r"test|example|placeholder|changeme|xxxx|dummy|mock|sample|secret-key-for",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Caches
# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}
_source_cache: dict[str, str] = {}
_requirements_cache: dict[str, str] = {}
_compose_cache: dict[str, Any] | None = None
_node_src_cache: dict[str, str] = {}
_package_json_cache: dict[str, dict] = {}


def _read_dockerfile(svc: str) -> str:
    if svc not in _dockerfile_cache:
        path = SERVICES_DIR / svc / "Dockerfile"
        _dockerfile_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _dockerfile_cache[svc]


def _read_requirements(svc: str) -> str:
    if svc not in _requirements_cache:
        path = SERVICES_DIR / svc / "requirements.txt"
        _requirements_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _requirements_cache[svc]


def _req_packages(svc: str) -> set[str]:
    text = _read_requirements(svc)
    pkgs: set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("-"):
            continue
        name = re.split(r"[>=<!\[;]", line)[0].strip().lower().replace("-", "_")
        if name:
            pkgs.add(name)
    return pkgs


def _read_python_source(svc: str, max_files: int = 30) -> str:
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


def _read_node_source(svc: str, max_files: int = 30) -> str:
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


def _read_package_json(svc: str) -> dict:
    """Read and cache package.json for a Node.js service."""
    if svc not in _package_json_cache:
        import json

        path = SERVICES_DIR / svc / "package.json"
        if path.exists():
            try:
                _package_json_cache[svc] = json.loads(path.read_text("utf-8"))
            except (json.JSONDecodeError, OSError):
                _package_json_cache[svc] = {}
        else:
            _package_json_cache[svc] = {}
    return _package_json_cache[svc]


def _load_compose() -> dict[str, Any]:
    global _compose_cache
    if _compose_cache is None:
        content = MAIN_COMPOSE.read_text("utf-8")
        # Remove YAML comments (lines starting with #, or inline # comments)
        lines = []
        for line in content.splitlines():
            stripped = line.lstrip()
            if stripped.startswith("#"):
                continue
            # Remove inline comments (after values, not inside strings)
            lines.append(line)
        content = "\n".join(lines)
        # Substitute ${VAR:-default} → default, ${VAR:?msg} → placeholder
        content = re.sub(r"\$\{[^:}]+:-([^}]*)\}", r"\1", content)
        content = re.sub(r"\$\{[^}]+\}", "placeholder", content)
        _compose_cache = yaml.safe_load(content) or {}
    return _compose_cache


def _get_env_keys(services: dict, svc: str) -> set[str]:
    """Extract environment variable keys regardless of list or dict format."""
    if svc not in services:
        return set()
    env = services[svc].get("environment", {})
    if isinstance(env, dict):
        return set(env.keys())
    if isinstance(env, list):
        keys: set[str] = set()
        for item in env:
            s = str(item)
            if "=" in s:
                keys.add(s.split("=", 1)[0].strip())
        return keys
    return set()


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def compose_data() -> dict[str, Any]:
    return _load_compose()


@pytest.fixture(scope="module")
def services(compose_data: dict) -> dict[str, Any]:
    return compose_data.get("services", {})


# ============================================================================
# 1. Service Entry Points — Every service must have a main file
# ============================================================================


class TestServiceEntryPoints:
    """نقاط الدخول لكل خدمة يجب أن تكون موجودة"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_main_exists(self, svc: str) -> None:
        """Each Python service has src/main.py."""
        path = SERVICES_DIR / svc / "src" / "main.py"
        assert path.exists(), (
            f"Python service '{svc}' is missing src/main.py entry point"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_entry_exists(self, svc: str) -> None:
        """Each Node.js service has src/main.ts or src/index.ts."""
        main_ts = SERVICES_DIR / svc / "src" / "main.ts"
        index_ts = SERVICES_DIR / svc / "src" / "index.ts"
        assert main_ts.exists() or index_ts.exists(), (
            f"Node.js service '{svc}' is missing src/main.ts or src/index.ts"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_main_imports_fastapi(self, svc: str) -> None:
        """Python main.py must import FastAPI."""
        path = SERVICES_DIR / svc / "src" / "main.py"
        if not path.exists():
            pytest.skip(f"{svc}/src/main.py not found")
        content = path.read_text("utf-8", errors="ignore")
        assert "FastAPI" in content or "fastapi" in content, (
            f"Python service '{svc}' main.py does not import FastAPI"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_entry_imports_nestjs(self, svc: str) -> None:
        """Node.js entry point must import NestJS or Express."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no TypeScript source")
        assert "NestFactory" in src or "express" in src.lower(), (
            f"Node.js service '{svc}' does not import NestJS/Express"
        )


# ============================================================================
# 2. API Routes — Services must define real routes (not stubs)
# ============================================================================


class TestAPIRoutes:
    """كل خدمة يجب أن تحدد مسارات API حقيقية"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_routes(self, svc: str) -> None:
        """Python service defines at least one API route."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no Python source")
        route_patterns = [
            r"@(?:app|router)\.(get|post|put|delete|patch)\(",
            r"app\.include_router\(",
            r"APIRouter\(",
        ]
        total = sum(len(re.findall(p, src)) for p in route_patterns)
        assert total >= 1, (
            f"Python service '{svc}' has no API route decorators"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_routes(self, svc: str) -> None:
        """Node.js service defines at least one controller or route."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no TypeScript source")
        route_patterns = [
            r"@(?:Get|Post|Put|Delete|Patch)\(",
            r"@Controller\(",
            r"router\.(get|post|put|delete|patch)\(",
        ]
        total = sum(len(re.findall(p, src)) for p in route_patterns)
        assert total >= 1, (
            f"Node.js service '{svc}' has no route decorators"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_not_minimal_stub(self, svc: str) -> None:
        """Python service main.py has substantive logic (> 50 lines)."""
        path = SERVICES_DIR / svc / "src" / "main.py"
        if not path.exists():
            pytest.skip(f"{svc}/src/main.py not found")
        lines = path.read_text("utf-8", errors="ignore").splitlines()
        non_blank = [l for l in lines if l.strip() and not l.strip().startswith("#")]
        assert len(non_blank) >= 50, (
            f"Python service '{svc}' main.py has only {len(non_blank)} non-blank lines — "
            f"likely a stub"
        )


# ============================================================================
# 3. Health Endpoints in Source Code
# ============================================================================


class TestHealthEndpointsInSource:
    """فحص نقاط صحة الخدمات في الشيفرة المصدرية"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_health_endpoint(self, svc: str) -> None:
        """Python service source defines /healthz or /health."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no Python source")
        assert re.search(r'["\']/(healthz?|readyz?)["\']', src), (
            f"Python service '{svc}' has no /healthz or /health endpoint in source"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_health_endpoint(self, svc: str) -> None:
        """Node.js service source defines health or healthz."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no TypeScript source")
        has_health = bool(re.search(
            r"health|healthz|readyz|HealthModule|TerminusModule",
            src,
            re.IGNORECASE,
        ))
        assert has_health, (
            f"Node.js service '{svc}' has no health endpoint in source"
        )


# ============================================================================
# 4. Database Connectivity Patterns
# ============================================================================


class TestDatabasePatterns:
    """أنماط الاتصال بقاعدة البيانات"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_database_env(self, svc: str, services: dict) -> None:
        """Python services that use DB must have DATABASE_URL in env."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        uses_db = bool(re.search(
            r"asyncpg|DATABASE_URL|db_pool|tortoise|sqlalchemy",
            src,
            re.IGNORECASE,
        ))
        if not uses_db:
            pytest.skip(f"{svc} does not use a database")
        # Check if DB is optional (guarded by env check or None default)
        optional_db = bool(re.search(
            r'DATABASE_URL.*None|getenv.*DATABASE.*is not None|'
            r'if db_url:|if database_url:|db_url = os\.getenv|'
            r'if not db_url:|getattr.*db_pool.*None|'
            r'outbox_disabled|db_pool\s*=\s*None',
            src,
        ))
        if optional_db:
            pytest.skip(f"{svc} uses database optionally")
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        env_keys = _get_env_keys(services, svc)
        assert "DATABASE_URL" in env_keys, (
            f"Python service '{svc}' uses DB in source but has no DATABASE_URL in compose"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_database_env(self, svc: str, services: dict) -> None:
        """Node.js services that use Prisma must have DATABASE_URL."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        uses_prisma = "PrismaService" in src or "PrismaClient" in src
        if not uses_prisma:
            pytest.skip(f"{svc} does not use Prisma")
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        env_keys = _get_env_keys(services, svc)
        assert "DATABASE_URL" in env_keys, (
            f"Node.js service '{svc}' uses Prisma but has no DATABASE_URL in compose"
        )


# ============================================================================
# 5. NATS Event Connectivity
# ============================================================================


class TestNATSConnectivity:
    """اتصال NATS للخدمات"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_nats_env(self, svc: str, services: dict) -> None:
        """Python services that import nats must have NATS_URL in compose."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        uses_nats = bool(re.search(r"import nats|from nats|NATS_URL|nc\.publish|nc\.subscribe", src))
        if not uses_nats:
            pytest.skip(f"{svc} does not use NATS")
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        env_keys = _get_env_keys(services, svc)
        assert "NATS_URL" in env_keys, (
            f"Python service '{svc}' uses NATS in source but has no NATS_URL in compose"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_nats_depends_on(self, svc: str, services: dict) -> None:
        """Python services that use NATS should depend on nats container."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        uses_nats = bool(re.search(r"import nats|from nats|NATS_URL", src))
        if not uses_nats:
            pytest.skip(f"{svc} does not use NATS")
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        depends = services[svc].get("depends_on", {})
        dep_names = list(depends.keys()) if isinstance(depends, dict) else depends
        assert "nats" in dep_names, (
            f"Python service '{svc}' uses NATS but does not depend_on 'nats'"
        )


# ============================================================================
# 6. Redis Connectivity
# ============================================================================


class TestRedisConnectivity:
    """اتصال Redis للخدمات"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_redis_env(self, svc: str, services: dict) -> None:
        """Python services that require Redis must have REDIS_URL.

        Services with optional Redis (checked via os.getenv fallback) are skipped.
        """
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        # Only flag required Redis usage, not optional (os.getenv with fallback)
        uses_redis = bool(re.search(r"import redis|from redis|aioredis|REDIS_URL", src))
        if not uses_redis:
            pytest.skip(f"{svc} does not use Redis")
        # Check if Redis is optional (guarded by env check or None default)
        optional_redis = bool(re.search(
            r'REDIS_URL.*None|getenv.*REDIS.*is not None|getenv.*REDIS.*or\b|'
            r'REDIS_URL.*\|\s*None|use_redis=.*getenv|if redis_url:|'
            r'settings\.redis_url|redis_url\s*=\s*self\.settings',
            src,
        ))
        if optional_redis:
            pytest.skip(f"{svc} uses Redis optionally")
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        env_keys = _get_env_keys(services, svc)
        has_redis = "REDIS_URL" in env_keys or "REDIS_HOST" in env_keys
        assert has_redis, (
            f"Python service '{svc}' requires Redis but has no REDIS_URL in compose"
        )


# ============================================================================
# 7. Dockerfile ↔ Source Alignment
# ============================================================================


class TestDockerfileSourceAlignment:
    """محاذاة Dockerfile مع الشيفرة المصدرية"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_requirements_txt(self, svc: str) -> None:
        """Python service must have requirements.txt."""
        path = SERVICES_DIR / svc / "requirements.txt"
        assert path.exists(), f"Python service '{svc}' missing requirements.txt"

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_requirements_has_fastapi(self, svc: str) -> None:
        """Python service requirements.txt must include fastapi."""
        pkgs = _req_packages(svc)
        if not pkgs:
            pytest.skip(f"{svc} has no requirements.txt")
        assert "fastapi" in pkgs, (
            f"Python service '{svc}' requirements.txt missing fastapi"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_requirements_has_uvicorn(self, svc: str) -> None:
        """Python service requirements.txt must include uvicorn."""
        pkgs = _req_packages(svc)
        if not pkgs:
            pytest.skip(f"{svc} has no requirements.txt")
        assert "uvicorn" in pkgs, (
            f"Python service '{svc}' requirements.txt missing uvicorn"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_has_package_json(self, svc: str) -> None:
        """Node.js service must have package.json."""
        path = SERVICES_DIR / svc / "package.json"
        assert path.exists(), f"Node.js service '{svc}' missing package.json"

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_package_has_nestjs(self, svc: str) -> None:
        """Node.js service should depend on @nestjs/core."""
        pkg = _read_package_json(svc)
        if not pkg:
            pytest.skip(f"{svc} has no package.json")
        all_deps = {**pkg.get("dependencies", {}), **pkg.get("devDependencies", {})}
        assert "@nestjs/core" in all_deps, (
            f"Node.js service '{svc}' package.json missing @nestjs/core"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_dockerfile_exposes_correct_port(self, svc: str) -> None:
        """Dockerfile EXPOSE matches the registered port."""
        expected_port = PYTHON_SERVICES[svc]
        df = _read_dockerfile(svc)
        if not df:
            pytest.skip(f"{svc} has no Dockerfile")
        # Match EXPOSE with literal port or ${PORT:-default}
        expose_match = re.findall(
            r"EXPOSE\s+(?:\$\{[^}]*:-)?(\d+)", df, re.IGNORECASE
        )
        if not expose_match:
            pytest.skip(f"{svc} Dockerfile has no EXPOSE with literal port")
        exposed_ports = [int(p) for p in expose_match]
        assert expected_port in exposed_ports, (
            f"Python service '{svc}' Dockerfile EXPOSE {exposed_ports} "
            f"does not include registered port {expected_port}"
        )


# ============================================================================
# 8. Security Patterns
# ============================================================================


class TestSecurityPatterns:
    """أنماط الأمان في الخدمات"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_no_hardcoded_secrets(self, svc: str) -> None:
        """Python source must not contain hardcoded secrets."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        # Look for obvious hardcoded secrets (not env vars)
        secret_patterns = [
            r'(?:password|secret|api_key)\s*=\s*["\'][^"\']{8,}["\']',
        ]
        for pattern in secret_patterns:
            matches = re.findall(pattern, src, re.IGNORECASE)
            # Filter out test/example/placeholder values
            real_secrets = [
                m for m in matches
                if not _SECRET_PLACEHOLDER_RE.search(m)
            ]
            assert not real_secrets, (
                f"Python service '{svc}' may contain hardcoded secrets: {real_secrets[:3]}"
            )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_dockerfile_non_root(self, svc: str) -> None:
        """Dockerfile should create/use a non-root user."""
        df = _read_dockerfile(svc)
        if not df:
            pytest.skip(f"{svc} has no Dockerfile")
        has_user = bool(re.search(r"USER\s+(?!root)\w+", df, re.IGNORECASE))
        has_useradd = bool(re.search(r"useradd|adduser|groupadd", df))
        assert has_user or has_useradd, (
            f"Python service '{svc}' Dockerfile does not use a non-root user"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_dockerfile_non_root(self, svc: str) -> None:
        """Node.js Dockerfile should create/use a non-root user."""
        df = _read_dockerfile(svc)
        if not df:
            pytest.skip(f"{svc} has no Dockerfile")
        has_user = bool(re.search(r"USER\s+(?!root)\w+", df, re.IGNORECASE))
        has_useradd = bool(re.search(r"useradd|adduser|groupadd|node", df))
        assert has_user or has_useradd, (
            f"Node.js service '{svc}' Dockerfile does not use a non-root user"
        )


# ============================================================================
# 9. Structured Logging
# ============================================================================


class TestStructuredLogging:
    """تسجيل منظم للخدمات"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_uses_structured_logging(self, svc: str) -> None:
        """Python service source should use structlog or logging_config."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_logging = bool(re.search(
            r"structlog|setup_logging|logging\.getLogger|logger\s*=|import logging",
            src,
        ))
        # Also check requirements for structlog
        pkgs = _req_packages(svc)
        has_structlog_dep = "structlog" in pkgs
        assert has_logging or has_structlog_dep, (
            f"Python service '{svc}' has no logging setup (structlog, logging, or setup_logging)"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_uses_logging(self, svc: str) -> None:
        """Node.js service should use a logger."""
        src = _read_node_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        has_logging = bool(re.search(
            r"Logger|pino|winston|console\.log|nestjs-pino",
            src,
        ))
        assert has_logging, (
            f"Node.js service '{svc}' has no logging setup"
        )


# ============================================================================
# 10. Service Version Consistency
# ============================================================================


class TestServiceVersionConsistency:
    """اتساق إصدار الخدمات"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_version_declared(self, svc: str) -> None:
        """Python service declares a version string (directly or via settings)."""
        path = SERVICES_DIR / svc / "src" / "main.py"
        if not path.exists():
            pytest.skip(f"{svc}/src/main.py not found")
        content = path.read_text("utf-8", errors="ignore")
        has_version = bool(re.search(
            r'(?:version|VERSION|__version__|SERVICE_VERSION)\s*[=:]\s*["\'][\d.]+'
            r'|version\s*=\s*settings\.\w+'
            r'|Version:\s*\d+\.\d+',
            content,
        ))
        assert has_version, (
            f"Python service '{svc}' main.py has no version declaration"
        )


# ============================================================================
# 11. Compose Environment ↔ Dockerfile ENV Alignment
# ============================================================================


class TestComposeDockerfileEnvAlignment:
    """محاذاة المتغيرات البيئية بين Compose و Dockerfile"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_port_env_matches_registry(self, svc: str, services: dict) -> None:
        """Compose PORT env var matches registry port."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        env = services[svc].get("environment", {})
        port_val = None
        if isinstance(env, dict):
            port_val = env.get("PORT", "")
        elif isinstance(env, list):
            for item in env:
                s = str(item)
                if s.startswith("PORT="):
                    port_val = s.split("=", 1)[1].strip()
                    break
        if not port_val or str(port_val) == "placeholder":
            pytest.skip(f"{svc} PORT not set or is placeholder")
        try:
            compose_port = int(str(port_val))
        except (ValueError, TypeError):
            pytest.skip(f"{svc} PORT is not numeric: {port_val}")
        expected = PYTHON_SERVICES[svc]
        assert compose_port == expected, (
            f"Python service '{svc}' compose PORT={compose_port} "
            f"does not match registry port {expected}"
        )


# ============================================================================
# 12. Dependency Completeness — Critical Packages
# ============================================================================


class TestDependencyCompleteness:
    """اكتمال التبعيات — الحزم الحرجة"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_pydantic(self, svc: str) -> None:
        """Python services typically need pydantic for request/response models."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        uses_pydantic = "pydantic" in src.lower() or "BaseModel" in src
        if not uses_pydantic:
            pytest.skip(f"{svc} does not use pydantic")
        pkgs = _req_packages(svc)
        assert "pydantic" in pkgs, (
            f"Python service '{svc}' uses pydantic but missing from requirements.txt"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_nats_in_requirements(self, svc: str) -> None:
        """Python services that use NATS must have nats-py in requirements."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        uses_nats = bool(re.search(r"^import nats|^from nats ", src, re.MULTILINE))
        if not uses_nats:
            pytest.skip(f"{svc} does not directly import nats")
        pkgs = _req_packages(svc)
        has_nats = "nats_py" in pkgs or "nats" in pkgs
        assert has_nats, (
            f"Python service '{svc}' imports nats but missing nats-py from requirements.txt"
        )


# ============================================================================
# 13. Init Container Validation
# ============================================================================


class TestInitContainerFunctionality:
    """وظائف حاويات التهيئة"""

    @pytest.mark.parametrize("svc", sorted(INIT_SERVICES))
    def test_init_has_command_or_entrypoint(self, svc: str, services: dict) -> None:
        """Init containers must define a command or entrypoint."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        has_cmd = "command" in cfg or "entrypoint" in cfg
        # Also check Dockerfile for CMD/ENTRYPOINT
        df = _read_dockerfile(svc)
        if df:
            has_cmd = has_cmd or bool(re.search(r"^(CMD|ENTRYPOINT)", df, re.MULTILINE | re.IGNORECASE))
        assert has_cmd, (
            f"Init container '{svc}' has no command, entrypoint, or Dockerfile CMD"
        )

    @pytest.mark.parametrize("svc", sorted(INIT_SERVICES))
    def test_init_no_ports(self, svc: str, services: dict) -> None:
        """Init containers should not expose ports."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        ports = services[svc].get("ports", [])
        assert not ports, (
            f"Init container '{svc}' should not expose ports but has: {ports}"
        )


# ============================================================================
# 14. Infrastructure Container Validation
# ============================================================================


class TestInfraContainerFunctionality:
    """وظائف حاويات البنية التحتية"""

    @pytest.mark.parametrize("svc", sorted(INFRA_SERVICES))
    def test_infra_has_volumes(self, svc: str, services: dict) -> None:
        """Stateful infra services should have volume mounts."""
        stateful = {"postgres", "redis", "nats", "minio", "milvus", "qdrant", "mongo", "vault", "etcd", "mlflow"}
        if svc not in stateful:
            pytest.skip(f"{svc} is not a stateful service")
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        volumes = cfg.get("volumes", [])
        assert volumes, (
            f"Stateful infrastructure service '{svc}' has no volume mounts"
        )

    @pytest.mark.parametrize("svc", sorted(INFRA_SERVICES - INIT_SERVICES))
    def test_infra_has_restart_policy(self, svc: str, services: dict) -> None:
        """Infrastructure services should have restart: unless-stopped."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        restart = cfg.get("restart", "")
        # YAML 1.1 may parse 'no' as False
        if restart is False:
            pytest.skip(f"{svc} is an init container (restart: no)")
        assert restart == "unless-stopped", (
            f"Infrastructure service '{svc}' has restart='{restart}', "
            f"expected 'unless-stopped'"
        )


# ============================================================================
# 15. Portless Worker Validation
# ============================================================================


class TestPortlessWorkerFunctionality:
    """وظائف العمال بدون منافذ"""

    @pytest.mark.parametrize("svc", sorted(PORTLESS_SERVICES))
    def test_worker_has_dockerfile(self, svc: str) -> None:
        """Worker services must have a Dockerfile."""
        path = SERVICES_DIR / svc / "Dockerfile"
        assert path.exists(), f"Worker service '{svc}' missing Dockerfile"

    @pytest.mark.parametrize("svc", sorted(PORTLESS_SERVICES))
    def test_worker_has_source(self, svc: str) -> None:
        """Worker services must have source code."""
        src_dir = SERVICES_DIR / svc / "src"
        main_py = SERVICES_DIR / svc / "main.py"
        assert src_dir.exists() or main_py.exists(), (
            f"Worker service '{svc}' missing both src/ directory and main.py"
        )

    @pytest.mark.parametrize("svc", sorted(PORTLESS_SERVICES))
    def test_worker_no_ports_in_compose(self, svc: str, services: dict) -> None:
        """Workers should not expose ports in compose."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        ports = services[svc].get("ports", [])
        assert not ports, (
            f"Portless worker '{svc}' should not expose ports but has: {ports}"
        )


# ============================================================================
# 16. Cross-Service Consistency
# ============================================================================


class TestCrossServiceConsistency:
    """اتساق الخدمات العابرة"""

    def test_all_python_services_have_dockerfile(self) -> None:
        """Every registered Python service has a Dockerfile."""
        missing = [
            svc for svc in PYTHON_SERVICES
            if not (SERVICES_DIR / svc / "Dockerfile").exists()
        ]
        assert not missing, f"Python services without Dockerfile: {missing}"

    def test_all_node_services_have_dockerfile(self) -> None:
        """Every registered Node.js service has a Dockerfile."""
        missing = [
            svc for svc in NODE_SERVICES
            if not (SERVICES_DIR / svc / "Dockerfile").exists()
        ]
        assert not missing, f"Node.js services without Dockerfile: {missing}"

    def test_no_port_conflicts_in_registry(self) -> None:
        """Service registry has no duplicate ports."""
        all_ports: dict[int, list[str]] = {}
        for svc, port in {**PYTHON_SERVICES, **NODE_SERVICES}.items():
            all_ports.setdefault(port, []).append(svc)
        conflicts = {p: svcs for p, svcs in all_ports.items() if len(svcs) > 1}
        assert not conflicts, f"Port conflicts in registry: {conflicts}"

    def test_compose_has_all_registered_services(self, services: dict) -> None:
        """docker-compose.yml contains all registered HTTP services."""
        missing = [
            svc for svc in ALL_HTTP_SERVICES
            if svc not in services
        ]
        assert not missing, (
            f"Registered HTTP services missing from docker-compose.yml: {missing}"
        )

    def test_python_services_count_consistency(self) -> None:
        """Python service count in registry matches filesystem."""
        on_disk = {
            d.name for d in SERVICES_DIR.iterdir()
            if d.is_dir()
            and (d / "src" / "main.py").exists()
            and (d / "Dockerfile").exists()
            and d.name not in {"shared", "test-harness-sidecar"}
        }
        # Some services on disk may not be registered yet
        registered = set(PYTHON_SERVICES)
        missing_from_registry = on_disk - registered - set(NODE_SERVICES) - PORTLESS_SERVICES - _REGISTRY_EXEMPT_SERVICES
        # Soft check: no more than 5 unregistered Python services
        assert len(missing_from_registry) <= 5, (
            f"Too many Python services on disk not in registry ({len(missing_from_registry)}): "
            f"{sorted(missing_from_registry)}"
        )


# ============================================================================
# 17. Shared Module Access
# ============================================================================


class TestSharedModuleAccess:
    """الوصول إلى الوحدات المشتركة"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_dockerfile_copies_shared(self, svc: str) -> None:
        """Python Dockerfile copies shared/ for platform modules."""
        df = _read_dockerfile(svc)
        if not df:
            pytest.skip(f"{svc} has no Dockerfile")
        # Check for COPY shared/ or COPY --from=... shared/
        has_shared = bool(re.search(r"COPY.*shared", df, re.IGNORECASE))
        # Some services use PYTHONPATH to access shared
        has_pythonpath = bool(re.search(r"PYTHONPATH.*shared", df, re.IGNORECASE))
        assert has_shared or has_pythonpath, (
            f"Python service '{svc}' Dockerfile does not COPY shared/ directory"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_source_imports_shared(self, svc: str) -> None:
        """Python services should import from shared modules."""
        src = _read_python_source(svc)
        if not src:
            pytest.skip(f"{svc} has no source")
        imports_shared = bool(re.search(
            r"from shared\.|import shared\.",
            src,
        ))
        # Allow services that add shared to path
        adds_shared_path = bool(re.search(r"shared.*path|sys\.path.*shared", src, re.IGNORECASE))
        assert imports_shared or adds_shared_path, (
            f"Python service '{svc}' does not import from shared/ modules"
        )


# ============================================================================
# 18. Summary Statistics
# ============================================================================


class TestFunctionalSummary:
    """إحصائيات ملخصة للاختبارات الوظيفية"""

    def test_all_services_have_source_code(self) -> None:
        """All registered services have source code on disk."""
        missing: list[str] = []
        for svc in list(PYTHON_SERVICES) + list(NODE_SERVICES):
            src_dir = SERVICES_DIR / svc / "src"
            if not src_dir.exists():
                missing.append(svc)
        assert not missing, (
            f"Services without src/ directory: {missing}"
        )

    def test_service_directory_structure(self) -> None:
        """All services follow standard directory layout."""
        issues: list[str] = []
        for svc in PYTHON_SERVICES:
            svc_dir = SERVICES_DIR / svc
            if not svc_dir.exists():
                issues.append(f"{svc}: directory missing")
                continue
            if not (svc_dir / "Dockerfile").exists():
                issues.append(f"{svc}: Dockerfile missing")
            if not (svc_dir / "src").exists():
                issues.append(f"{svc}: src/ missing")
            if not (svc_dir / "requirements.txt").exists():
                issues.append(f"{svc}: requirements.txt missing")
        assert not issues, (
            f"Service structure issues:\n" + "\n".join(f"  {i}" for i in issues)
        )

    def test_total_functional_coverage(self) -> None:
        """Ensure we're testing a substantial number of services."""
        total = len(PYTHON_SERVICES) + len(NODE_SERVICES) + len(PORTLESS_SERVICES)
        assert total >= 60, (
            f"Only {total} services tested — expected at least 60"
        )
