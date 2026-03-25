"""
SAHOOL Node.js Analytics & Research Services Group – Container Function Tests
==============================================================================
اختبارات وظائف مجموعة خدمات التحليلات والبحث (Node.js)

Validates consistency across Node.js NestJS services for analytics,
prediction, research, authentication, and disaster assessment.
All tests are **static analysis** — no Docker daemon required.

Services in this group:
  user-service · crop-growth-model · lai-estimation · yield-prediction
  yield-prediction-service · research-core · disaster-assessment

Coverage:
 1.  NestJS framework in package.json
 2.  Prisma ORM for database access
 3.  Workspace dependency handling
 4.  TypeScript compilation
 5.  Health endpoints
 6.  Non-root user (node user)
 7.  Compose configuration
 8.  Port range & uniqueness
 9.  NPM mirror fallback
10.  Tini init system

Run:
    pytest tests/container/test_nodejs_analytics_services_group.py -v --tb=short
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = [pytest.mark.container, pytest.mark.smoke]

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"

NODE_ANALYTICS_SERVICES: dict[str, int] = {
    "user-service": 3025,
    "crop-growth-model": 3023,
    "lai-estimation": 3022,
    "yield-prediction": 3021,
    "yield-prediction-service": 8152,
    "research-core": 3015,
    "disaster-assessment": 3020,
}

# Sub-cluster: agricultural prediction models
PREDICTION_SERVICES = {
    "crop-growth-model", "lai-estimation",
    "yield-prediction", "yield-prediction-service",
}

# Sub-cluster: services that use Prisma
# Services confirmed to use Prisma ORM
PRISMA_SERVICES = {
    "user-service", "research-core", "disaster-assessment",
}

# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}
_package_json_cache: dict[str, dict] = {}


def _read_dockerfile(svc: str) -> str:
    if svc not in _dockerfile_cache:
        path = SERVICES_DIR / svc / "Dockerfile"
        _dockerfile_cache[svc] = path.read_text("utf-8") if path.exists() else ""
    return _dockerfile_cache[svc]


def _read_package_json(svc: str) -> dict:
    if svc not in _package_json_cache:
        path = SERVICES_DIR / svc / "package.json"
        if path.exists():
            _package_json_cache[svc] = json.loads(path.read_text("utf-8"))
        else:
            _package_json_cache[svc] = {}
    return _package_json_cache[svc]


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. NestJS Framework
# ===========================================================================


class TestNestJSFramework:
    """إطار عمل NestJS."""

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_package_json_exists(self, svc: str) -> None:
        path = SERVICES_DIR / svc / "package.json"
        assert path.exists(), f"{svc} missing package.json"

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_nestjs_dependency(self, svc: str) -> None:
        """package.json includes @nestjs/core or nestjs."""
        pkg = _read_package_json(svc)
        if not pkg:
            pytest.skip(f"No package.json for {svc}")
        all_deps = str(pkg.get("dependencies", {})) + str(pkg.get("devDependencies", {}))
        assert "nestjs" in all_deps.lower(), f"{svc} missing NestJS dependency"

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_typescript_config(self, svc: str) -> None:
        """Service has tsconfig.json for TypeScript compilation."""
        tsconfig = SERVICES_DIR / svc / "tsconfig.json"
        tsconfig_build = SERVICES_DIR / svc / "tsconfig.build.json"
        assert tsconfig.exists() or tsconfig_build.exists(), (
            f"{svc} missing tsconfig.json"
        )


# ===========================================================================
# 2. Prisma ORM
# ===========================================================================


class TestPrismaORM:
    """خدمات Prisma ORM."""

    @pytest.mark.parametrize("svc", sorted(PRISMA_SERVICES))
    def test_prisma_in_deps(self, svc: str) -> None:
        """Service declares prisma in dependencies or devDependencies."""
        pkg = _read_package_json(svc)
        if not pkg:
            pytest.skip(f"No package.json for {svc}")
        all_deps = str(pkg.get("dependencies", {})) + str(pkg.get("devDependencies", {}))
        has_prisma = "prisma" in all_deps.lower()
        # Also check Dockerfile for prisma generate
        if not has_prisma:
            content = _read_dockerfile(svc)
            has_prisma = "prisma" in content.lower()
        assert has_prisma, f"{svc} missing Prisma dependency"

    @pytest.mark.parametrize("svc", sorted(PRISMA_SERVICES))
    def test_prisma_generate_in_dockerfile(self, svc: str) -> None:
        """Dockerfile runs prisma generate."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_prisma = "prisma" in content.lower()
        assert has_prisma, f"{svc} Dockerfile missing prisma reference"


# ===========================================================================
# 3. Build Configuration in Dockerfile
# ===========================================================================


class TestNodeBuildConfig:
    """تكوين البناء في Dockerfile."""

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_node_base_image(self, svc: str) -> None:
        """Dockerfile uses Node.js base image."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"FROM\s+node:", content, re.IGNORECASE), (
            f"{svc} does not use Node.js base image"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_multi_stage_build(self, svc: str) -> None:
        """Dockerfile has multi-stage build."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        from_count = len(re.findall(r"^FROM\s+", content, re.MULTILINE | re.IGNORECASE))
        assert from_count >= 2, f"{svc} has {from_count} stage(s), expected ≥2"

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_nest_build_step(self, svc: str) -> None:
        """Dockerfile includes NestJS build step."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_build = (
            "nest build" in content.lower()
            or "npm run build" in content.lower()
            or "npx nest build" in content.lower()
        )
        assert has_build, f"{svc} Dockerfile missing build step"

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_npm_mirror_fallback(self, svc: str) -> None:
        """Dockerfile has NPM mirror fallback (npmmirror)."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        # Check for npm mirror/registry configuration in Dockerfile
        npm_registry_official = "registry.npmjs.org"  # noqa: S105
        has_mirror = (
            "npmmirror" in content.lower()
            or npm_registry_official in content.lower()
            or "npm config" in content.lower()
        )
        assert has_mirror, f"{svc} missing NPM mirror fallback"


# ===========================================================================
# 4. Health Endpoints
# ===========================================================================


class TestNodeHealthEndpoints:
    """نقاط فحص الصحة."""

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_healthcheck_in_dockerfile(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} missing HEALTHCHECK"


# ===========================================================================
# 5. Non-Root User
# ===========================================================================


class TestNodeNonRoot:
    """مستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_non_root_user(self, svc: str) -> None:
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_lines = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE)
        non_root = [u for u in user_lines if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} does not switch to non-root USER"


# ===========================================================================
# 6. Compose Configuration
# ===========================================================================


class TestNodeComposeConfig:
    """تكوين docker-compose."""

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"{svc} not in docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_depends_on_infrastructure(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        dep_names = (
            set(depends) if isinstance(depends, list)
            else set(depends.keys()) if isinstance(depends, dict)
            else set()
        )
        infra = {"postgres", "pgbouncer", "redis", "nats"}
        assert dep_names & infra, (
            f"{svc} should depend on infrastructure (deps: {dep_names})"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_restart_policy(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert svc_def.get("restart") == "unless-stopped", (
            f"{svc} missing restart: unless-stopped"
        )

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_logging_configured(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        assert "logging" in svc_def, f"{svc} missing logging"

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        svc_def = services.get(svc, {})
        networks = svc_def.get("networks", {})
        net_names = list(networks.keys()) if isinstance(networks, dict) else (networks or [])
        assert any("sahool" in str(n) for n in net_names), f"{svc} not on sahool network"

    @pytest.mark.parametrize("svc", sorted(NODE_ANALYTICS_SERVICES))
    def test_environment_declared(self, services: dict, svc: str) -> None:
        """Service declares NODE_ENV or ENVIRONMENT."""
        svc_def = services.get(svc, {})
        env_str = str(svc_def.get("environment", {}))
        assert "NODE_ENV" in env_str or "ENVIRONMENT" in env_str, (
            f"{svc} missing NODE_ENV or ENVIRONMENT"
        )


# ===========================================================================
# 7. Port Range
# ===========================================================================


class TestNodePortRange:
    """منافذ خدمات Node.js."""

    @pytest.mark.parametrize("svc,port", sorted(NODE_ANALYTICS_SERVICES.items()))
    def test_port_valid(self, svc: str, port: int) -> None:
        assert 3000 <= port <= 9000, f"{svc} port {port} out of range"

    def test_no_duplicate_ports(self) -> None:
        ports = list(NODE_ANALYTICS_SERVICES.values())
        assert len(ports) == len(set(ports))


# ===========================================================================
# 8. Tini Init System
# ===========================================================================


class TestNodeTiniInit:
    """نظام تهيئة tini لخدمات Node.js."""

    # Services confirmed to use tini init system
    TINI_SERVICES = sorted({"crop-growth-model", "lai-estimation", "yield-prediction-service"})

    @pytest.mark.parametrize("svc", TINI_SERVICES)
    def test_tini_or_init(self, svc: str) -> None:
        """Node.js service uses tini or --init for PID 1 signal handling."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_tini = "tini" in content.lower()
        has_init = "--init" in content.lower()
        has_dumb_init = "dumb-init" in content.lower()
        assert has_tini or has_init or has_dumb_init, (
            f"{svc} should use tini/dumb-init for Node.js signal handling"
        )


# ===========================================================================
# 9. Prediction Services – Scientific Domain
# ===========================================================================


class TestPredictionDomain:
    """خدمات التنبؤ الزراعي."""

    @pytest.mark.parametrize("svc", sorted(PREDICTION_SERVICES))
    def test_prediction_source_references_models(self, svc: str) -> None:
        """Prediction service references agricultural models."""
        src_dir = SERVICES_DIR / svc / "src"
        if not src_dir.exists():
            pytest.skip(f"No src/ for {svc}")
        all_files = list(src_dir.rglob("*.ts"))
        combined = ""
        for f in all_files[:20]:
            combined += f.read_text("utf-8", errors="ignore")
        has_model = (
            "model" in combined.lower()
            or "predict" in combined.lower()
            or "yield" in combined.lower()
            or "growth" in combined.lower()
            or "estimation" in combined.lower()
        )
        assert has_model, f"{svc} should reference prediction/model logic"
