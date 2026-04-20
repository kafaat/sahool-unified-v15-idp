"""
SAHOOL Comprehensive Container Smoke Tests – All 94 Containers
================================================================
اختبارات الدخان الشاملة لجميع الحاويات – 94 حاوية

A single test module that validates **every** container declared in
docker-compose.yml: infrastructure, init containers, GPU services,
application services (Python/Node.js), and portless workers.

All tests are **static analysis** — no Docker daemon required.

Coverage:
 1.  Compose completeness    – every registered service is in docker-compose.yml
 2.  Image or build          – each service has an image: or build: directive
 3.  Restart policy          – long-running services use unless-stopped, init use no
 4.  Healthcheck presence    – long-running services declare a healthcheck
 5.  Network membership      – all services are on sahool-network
 6.  No privileged mode      – no service runs privileged
 7.  Environment essentials  – app services declare PORT/ENVIRONMENT
 8.  Logging config          – app services use json-file with rotation
 9.  Dependency validation   – depends_on targets exist in compose
 10. Port conflict detection – no two services share the same host port
 11. Dockerfile existence    – built services have a Dockerfile on disk
 12. Infrastructure images   – infra services pin image versions (no :latest)
 13. Init container policy   – init containers use restart: no
 14. No orphan services      – compose has no services unknown to registry

Run:
    pytest tests/container/test_all_containers_smoke.py -v --tb=short
    pytest tests/container/test_all_containers_smoke.py -v -n auto  # parallel

Arabic summary:
    يتحقق هذا الملف من كل حاوية في المنصة: البنية التحتية، خدمات التطبيقات،
    حاويات التهيئة، وخدمات GPU. الاختبارات ثابتة ولا تحتاج إلى Docker.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.container.service_registry import (
    ALL_COMPOSE_SERVICES,
    ALL_HTTP_SERVICES,
    DEPRECATED_SERVICES,
    GPU_SERVICES,
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
# Long-running services = everything except init containers
# ---------------------------------------------------------------------------

LONG_RUNNING_SERVICES: set[str] = ALL_COMPOSE_SERVICES - INIT_SERVICES

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def compose_raw() -> dict[str, Any]:
    """Load the raw docker-compose.yml once."""
    assert MAIN_COMPOSE.exists(), f"docker-compose.yml not found at {MAIN_COMPOSE}"
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose_raw: dict) -> dict[str, Any]:
    """Return the 'services' mapping from docker-compose.yml."""
    return compose_raw.get("services", {})


# ============================================================================
# 1. Compose Completeness — every registered service must exist
# ============================================================================


class TestComposeCompleteness:
    """كل خدمة مسجلة يجب أن تكون موجودة في docker-compose.yml"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"Python service '{svc}' missing from docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"Node.js service '{svc}' missing from docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(INFRA_SERVICES))
    def test_infra_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"Infrastructure service '{svc}' missing from docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(INIT_SERVICES))
    def test_init_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"Init container '{svc}' missing from docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(PORTLESS_SERVICES))
    def test_portless_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"Portless service '{svc}' missing from docker-compose.yml"

    @pytest.mark.parametrize("svc", sorted(GPU_SERVICES))
    def test_gpu_service_in_compose(self, services: dict, svc: str) -> None:
        assert svc in services, f"GPU service '{svc}' missing from docker-compose.yml"

    def test_total_registered_count(self, services: dict) -> None:
        """Registry covers the majority of compose services."""
        compose_names = set(services.keys())
        registered = ALL_COMPOSE_SERVICES
        coverage = len(registered & compose_names) / max(len(compose_names), 1)
        assert coverage >= 0.90, (
            f"Registry covers only {coverage:.0%} of compose services. "
            f"Unregistered: {sorted(compose_names - registered)}"
        )


# ============================================================================
# 2. Image or Build — every service must define image: or build:
# ============================================================================


class TestImageOrBuild:
    """كل حاوية يجب أن تحدد image أو build"""

    @pytest.mark.parametrize("svc", sorted(ALL_COMPOSE_SERVICES))
    def test_has_image_or_build(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        assert "image" in cfg or "build" in cfg, (
            f"Service '{svc}' has neither 'image:' nor 'build:' directive"
        )


# ============================================================================
# 3. Restart Policy
# ============================================================================


class TestRestartPolicy:
    """سياسة إعادة التشغيل لجميع الحاويات"""

    @pytest.mark.parametrize("svc", sorted(LONG_RUNNING_SERVICES))
    def test_long_running_has_restart(self, services: dict, svc: str) -> None:
        """Long-running services must have a restart policy."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        policy = cfg.get("restart", "")
        # YAML 1.1: 'no' may be parsed as boolean False
        assert policy and policy is not True, (
            f"Long-running service '{svc}' is missing 'restart' policy"
        )

    @pytest.mark.parametrize("svc", sorted(INIT_SERVICES))
    def test_init_container_restart_no(self, services: dict, svc: str) -> None:
        """Init containers should use restart: no (or 'no')."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        policy = cfg.get("restart", "")
        # YAML 1.1 parses bare `no` as boolean False
        assert policy == "no" or policy is False, (
            f"Init container '{svc}' restart policy is '{policy}', expected 'no'"
        )


# ============================================================================
# 4. Healthcheck Presence
# ============================================================================


class TestHealthcheckPresence:
    """فحص صحة الحاويات طويلة التشغيل"""

    # Init containers don't need healthchecks
    _EXEMPT = INIT_SERVICES | {"code-review-agent", "demo-data"}

    @pytest.mark.parametrize("svc", sorted(LONG_RUNNING_SERVICES))
    def test_healthcheck_declared(self, services: dict, svc: str) -> None:
        """Long-running service has a healthcheck in compose."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        if svc in self._EXEMPT:
            pytest.skip(f"{svc} is exempt from healthcheck requirement")
        cfg = services[svc]
        assert "healthcheck" in cfg, (
            f"Long-running service '{svc}' has no 'healthcheck' in compose"
        )

    @pytest.mark.parametrize("svc", sorted(LONG_RUNNING_SERVICES - _EXEMPT))
    def test_healthcheck_has_test(self, services: dict, svc: str) -> None:
        """Healthcheck declares a 'test' command."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        hc = services[svc].get("healthcheck", {})
        if not hc:
            pytest.skip(f"{svc} has no healthcheck")
        assert "test" in hc, (
            f"Service '{svc}' healthcheck is missing 'test' command"
        )

    @pytest.mark.parametrize("svc", sorted(LONG_RUNNING_SERVICES - _EXEMPT))
    def test_healthcheck_has_interval(self, services: dict, svc: str) -> None:
        """Healthcheck declares an interval."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        hc = services[svc].get("healthcheck", {})
        if not hc:
            pytest.skip(f"{svc} has no healthcheck")
        assert "interval" in hc, (
            f"Service '{svc}' healthcheck is missing 'interval'"
        )


# ============================================================================
# 5. Network Membership
# ============================================================================


class TestNetworkMembership:
    """جميع الحاويات يجب أن تكون على شبكة sahool"""

    @pytest.mark.parametrize("svc", sorted(ALL_COMPOSE_SERVICES))
    def test_on_sahool_network(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        nets = cfg.get("networks", {})
        if isinstance(nets, list):
            net_names = nets
        elif isinstance(nets, dict):
            net_names = list(nets.keys())
        else:
            net_names = []
        assert any("sahool" in n for n in net_names), (
            f"Service '{svc}' is not on any sahool network (networks: {net_names})"
        )


# ============================================================================
# 6. No Privileged Mode
# ============================================================================


class TestNoPrivileged:
    """لا توجد حاويات تعمل بصلاحيات مميزة"""

    @pytest.mark.parametrize("svc", sorted(ALL_COMPOSE_SERVICES))
    def test_not_privileged(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        assert cfg.get("privileged") is not True, (
            f"Service '{svc}' runs as privileged (security risk)"
        )

    @pytest.mark.parametrize("svc", sorted(ALL_COMPOSE_SERVICES))
    def test_no_host_pid(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        assert cfg.get("pid") != "host", (
            f"Service '{svc}' uses pid: host (security risk)"
        )

    @pytest.mark.parametrize("svc", sorted(ALL_COMPOSE_SERVICES))
    def test_no_host_network(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        assert cfg.get("network_mode") != "host", (
            f"Service '{svc}' uses network_mode: host (security risk)"
        )


# ============================================================================
# 7. Environment Essentials (app services only)
# ============================================================================


class TestEnvironmentEssentials:
    """المتغيرات البيئية الأساسية لخدمات التطبيقات"""

    @staticmethod
    def _env_keys(cfg: dict) -> set[str]:
        """Extract environment variable keys from a compose service config."""
        env = cfg.get("environment", {})
        if isinstance(env, dict):
            return set(env.keys())
        if isinstance(env, list):
            return {
                e.split("=", 1)[0] for e in env if isinstance(e, str) and "=" in e
            } | {e for e in env if isinstance(e, str) and "=" not in e}
        return set()

    @pytest.mark.parametrize("svc", sorted(ALL_HTTP_SERVICES))
    def test_has_port_env(self, services: dict, svc: str) -> None:
        """HTTP service declares PORT or a *_PORT env var."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        keys = self._env_keys(services[svc])
        has_port = any(k == "PORT" or k.endswith("_PORT") for k in keys)
        assert has_port, f"Service '{svc}' missing PORT env var"

    @pytest.mark.parametrize("svc", sorted(ALL_HTTP_SERVICES))
    def test_has_environment_or_node_env(self, services: dict, svc: str) -> None:
        """HTTP service declares ENVIRONMENT or NODE_ENV."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        keys = self._env_keys(services[svc])
        assert "ENVIRONMENT" in keys or "NODE_ENV" in keys, (
            f"Service '{svc}' missing ENVIRONMENT/NODE_ENV env var"
        )

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_has_log_level(self, services: dict, svc: str) -> None:
        """Python service declares LOG_LEVEL."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        keys = self._env_keys(services[svc])
        assert "LOG_LEVEL" in keys, f"Python service '{svc}' missing LOG_LEVEL"


# ============================================================================
# 8. Logging Configuration (app services only)
# ============================================================================


class TestLoggingConfig:
    """تكوين السجلات لخدمات التطبيقات"""

    @pytest.mark.parametrize("svc", sorted(ALL_HTTP_SERVICES))
    def test_logging_driver(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        driver = cfg.get("logging", {}).get("driver", "")
        assert driver == "json-file", (
            f"Service '{svc}' logging driver is '{driver}', expected 'json-file'"
        )

    @pytest.mark.parametrize("svc", sorted(ALL_HTTP_SERVICES))
    def test_logging_max_size(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        opts = services[svc].get("logging", {}).get("options", {})
        assert "max-size" in opts, (
            f"Service '{svc}' logging missing 'max-size'"
        )

    @pytest.mark.parametrize("svc", sorted(ALL_HTTP_SERVICES))
    def test_logging_max_file(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        opts = services[svc].get("logging", {}).get("options", {})
        assert "max-file" in opts, (
            f"Service '{svc}' logging missing 'max-file'"
        )


# ============================================================================
# 9. Dependency Validation
# ============================================================================


class TestDependencyValidation:
    """التحقق من سلاسل التبعيات"""

    @pytest.mark.parametrize("svc", sorted(ALL_COMPOSE_SERVICES))
    def test_depends_on_targets_exist(self, services: dict, svc: str) -> None:
        """All depends_on targets are valid compose services."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        depends = services[svc].get("depends_on", {})
        if isinstance(depends, list):
            dep_names = depends
        elif isinstance(depends, dict):
            dep_names = list(depends.keys())
        else:
            dep_names = []
        for dep in dep_names:
            assert dep in services, (
                f"Service '{svc}' depends_on '{dep}' which is not in compose"
            )

    @pytest.mark.parametrize("svc", sorted(ALL_HTTP_SERVICES))
    def test_app_has_dependencies(self, services: dict, svc: str) -> None:
        """HTTP services should declare at least one dependency."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        depends = services[svc].get("depends_on", {})
        assert depends, f"Service '{svc}' has no depends_on"


# ============================================================================
# 10. Port Conflict Detection
# ============================================================================


class TestPortConflicts:
    """كشف تعارض المنافذ"""

    def test_no_duplicate_host_ports(self, services: dict) -> None:
        """No two services share the same host-side port."""
        seen: dict[int, str] = {}
        duplicates: list[str] = []
        for svc_name, svc in services.items():
            for p in svc.get("ports", []):
                p_str = str(p)
                parts = p_str.split(":")
                if len(parts) < 2:
                    continue
                host_str = parts[0].strip()
                m = re.search(r":-?(\d+)", host_str)
                if m:
                    host_port = int(m.group(1))
                elif host_str.isdigit():
                    host_port = int(host_str)
                else:
                    continue
                if host_port in seen:
                    duplicates.append(
                        f"Port {host_port}: '{svc_name}' ↔ '{seen[host_port]}'"
                    )
                else:
                    seen[host_port] = svc_name
        assert not duplicates, (
            "Duplicate host ports:\n" + "\n".join(f"  {d}" for d in duplicates)
        )


# ============================================================================
# 11. Dockerfile Existence (built services only)
# ============================================================================


class TestDockerfileExistence:
    """وجود ملف Dockerfile لكل خدمة مبنية من المصدر"""

    @pytest.mark.parametrize("svc", sorted(PYTHON_SERVICES))
    def test_python_dockerfile_exists(self, svc: str) -> None:
        path = SERVICES_DIR / svc / "Dockerfile"
        assert path.exists(), f"Dockerfile missing for Python service '{svc}'"

    @pytest.mark.parametrize("svc", sorted(NODE_SERVICES))
    def test_node_dockerfile_exists(self, svc: str) -> None:
        path = SERVICES_DIR / svc / "Dockerfile"
        assert path.exists(), f"Dockerfile missing for Node.js service '{svc}'"

    @pytest.mark.parametrize("svc", sorted(PORTLESS_SERVICES))
    def test_portless_dockerfile_exists(self, svc: str) -> None:
        path = SERVICES_DIR / svc / "Dockerfile"
        assert path.exists(), f"Dockerfile missing for portless service '{svc}'"


# ============================================================================
# 12. Infrastructure Image Pinning
# ============================================================================


class TestInfraImagePinning:
    """تثبيت إصدار صور البنية التحتية"""

    @pytest.mark.parametrize("svc", sorted(INFRA_SERVICES))
    def test_image_not_latest(self, services: dict, svc: str) -> None:
        """Infrastructure images should pin a version, not use :latest."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        image = cfg.get("image", "")
        if not image:
            pytest.skip(f"{svc} uses build: instead of image:")
        assert not image.endswith(":latest"), (
            f"Infrastructure service '{svc}' uses ':latest' tag — pin a version"
        )

    @pytest.mark.parametrize("svc", sorted(INFRA_SERVICES))
    def test_image_has_tag(self, services: dict, svc: str) -> None:
        """Infrastructure images should include a version tag."""
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        image = cfg.get("image", "")
        if not image:
            pytest.skip(f"{svc} uses build: instead of image:")
        # Image should have a tag (name:tag or name@sha256:...)
        has_tag = ":" in image or "@" in image
        assert has_tag, (
            f"Infrastructure service '{svc}' image '{image}' has no version tag"
        )


# ============================================================================
# 13. No Orphan Services
# ============================================================================


class TestNoOrphanServices:
    """لا توجد خدمات يتيمة غير مسجلة"""

    def test_compose_services_are_registered(self, services: dict) -> None:
        """All compose services should be in the service registry."""
        compose_names = set(services.keys())
        registered = ALL_COMPOSE_SERVICES
        orphans = compose_names - registered
        assert not orphans, (
            f"Compose services not in registry: {sorted(orphans)}. "
            f"Add them to tests/container/service_registry.py"
        )


# ============================================================================
# 14. Infrastructure Healthcheck Quality
# ============================================================================


class TestInfraHealthcheckQuality:
    """جودة فحص صحة البنية التحتية"""

    _INFRA_WITH_HEALTHCHECK = INFRA_SERVICES - {"etcd-perms-init"}

    @pytest.mark.parametrize("svc", sorted(_INFRA_WITH_HEALTHCHECK))
    def test_infra_has_healthcheck(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        cfg = services[svc]
        assert "healthcheck" in cfg, (
            f"Infrastructure service '{svc}' should have a healthcheck"
        )

    @pytest.mark.parametrize("svc", sorted(_INFRA_WITH_HEALTHCHECK))
    def test_infra_healthcheck_has_retries(self, services: dict, svc: str) -> None:
        if svc not in services:
            pytest.skip(f"{svc} not in compose")
        hc = services[svc].get("healthcheck", {})
        if not hc:
            pytest.skip(f"{svc} has no healthcheck")
        assert "retries" in hc, (
            f"Infrastructure service '{svc}' healthcheck missing 'retries'"
        )


# ============================================================================
# 15. Summary Statistics
# ============================================================================


class TestSummaryStatistics:
    """إحصائيات ملخصة للتحقق من عدم وجود تراجع"""

    def test_python_service_count(self, services: dict) -> None:
        """Python service count matches registry."""
        in_compose = [s for s in PYTHON_SERVICES if s in services]
        assert len(in_compose) == len(PYTHON_SERVICES), (
            f"Expected {len(PYTHON_SERVICES)} Python services, "
            f"found {len(in_compose)} in compose"
        )

    def test_node_service_count(self, services: dict) -> None:
        """Node.js service count matches registry."""
        in_compose = [s for s in NODE_SERVICES if s in services]
        assert len(in_compose) == len(NODE_SERVICES), (
            f"Expected {len(NODE_SERVICES)} Node.js services, "
            f"found {len(in_compose)} in compose"
        )

    def test_infra_service_count(self, services: dict) -> None:
        """Infrastructure service count matches registry."""
        in_compose = [s for s in INFRA_SERVICES if s in services]
        assert len(in_compose) == len(INFRA_SERVICES), (
            f"Expected {len(INFRA_SERVICES)} infra services, "
            f"found {len(in_compose)} in compose"
        )

    def test_init_container_count(self, services: dict) -> None:
        """Init container count matches registry."""
        in_compose = [s for s in INIT_SERVICES if s in services]
        assert len(in_compose) == len(INIT_SERVICES), (
            f"Expected {len(INIT_SERVICES)} init containers, "
            f"found {len(in_compose)} in compose"
        )

    def test_total_service_count(self, services: dict) -> None:
        """Total compose services should be ≥ 85 (guard against mass deletion)."""
        assert len(services) >= 85, (
            f"Only {len(services)} services in compose — expected at least 85"
        )
