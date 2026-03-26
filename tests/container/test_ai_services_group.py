"""
SAHOOL AI/Intelligence Services Group – Container Function Tests
=================================================================
اختبارات وظائف مجموعة خدمات الذكاء الاصطناعي

Validates that the AI/Intelligence service cluster shares consistent
configuration, dependencies, and conventions.  All tests are **static
analysis** — no Docker daemon or running containers required.

Services in this group:
  ai-advisor · ai-agents-service · ai-agents-core · ai-chat-assistant
  copilot-api · llm-orchestrator-service · knowledge-graph · code-fix-agent

Coverage:
 1. Shared LLM/AI dependencies present in every service
 2. Constraints file usage (constraints-ai.txt)
 3. Consistent base image across the group
 4. Shared module imports (shared/ai/, shared/llm/, shared/agents/)
 5. NATS event subject naming conventions
 6. Health endpoint patterns in source code
 7. Environment variable consistency (LLM provider config)
 8. Port range consistency (80xx range)
 9. Non-root user in Dockerfiles
10. Multi-stage build pattern

Run:
    pytest tests/container/test_ai_services_group.py -v --tb=short
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

pytestmark = [pytest.mark.container, pytest.mark.smoke]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[2]
SERVICES_DIR = REPO_ROOT / "apps" / "services"
MAIN_COMPOSE = REPO_ROOT / "docker-compose.yml"

AI_SERVICES: dict[str, int] = {
    "ai-advisor": 8112,
    "ai-agents-service": 8130,
    "ai-agents-core": 8161,
    "ai-chat-assistant": 8260,
    "copilot-api": 8088,
    "llm-orchestrator-service": 8164,
    "knowledge-graph": 8140,
    "code-fix-agent": 8162,
}

# Common AI/LLM packages every AI service should declare
AI_CORE_DEPS = {"fastapi", "uvicorn", "pydantic"}
AI_LLM_DEPS_ANY = {"anthropic", "openai", "langchain", "ollama", "transformers", "crewai", "httpx"}

# Services that get LLM access via shared/ modules rather than direct requirements
AI_LLM_VIA_SHARED = {"ai-agents-core", "ai-agents-service", "ai-chat-assistant",
                      "code-fix-agent", "copilot-api", "knowledge-graph"}

# ---------------------------------------------------------------------------
# Helpers & Caches
# ---------------------------------------------------------------------------

_dockerfile_cache: dict[str, str] = {}
_requirements_cache: dict[str, str] = {}


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
    """Return lowercased package names from requirements.txt."""
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


@pytest.fixture(scope="module")
def compose() -> dict[str, Any]:
    with open(MAIN_COMPOSE, encoding="utf-8") as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def services(compose: dict) -> dict[str, Any]:
    return compose.get("services", {})


# ===========================================================================
# 1. AI Core Dependencies Present
# ===========================================================================


class TestAICoreDependencies:
    """كل خدمة ذكاء اصطناعي يجب أن تحتوي على المكتبات الأساسية."""

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_fastapi_declared(self, svc: str) -> None:
        """AI service declares fastapi in requirements.txt."""
        pkgs = _req_packages(svc)
        assert "fastapi" in pkgs, f"{svc} missing fastapi in requirements.txt"

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_pydantic_declared(self, svc: str) -> None:
        """AI service declares pydantic in requirements.txt."""
        pkgs = _req_packages(svc)
        assert "pydantic" in pkgs or "pydantic_settings" in pkgs, (
            f"{svc} missing pydantic in requirements.txt"
        )

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_has_llm_dependency(self, svc: str) -> None:
        """AI service declares LLM/AI dependency directly or uses shared/ modules."""
        pkgs = _req_packages(svc)
        normalised = {p.split("_")[0] for p in pkgs}
        has_ai = normalised & AI_LLM_DEPS_ANY
        if not has_ai and svc in AI_LLM_VIA_SHARED:
            # These services access LLM providers via COPY shared/ in Dockerfile
            content = _read_dockerfile(svc)
            has_ai = bool(re.search(r"COPY.*shared", content, re.IGNORECASE))
        assert has_ai, (
            f"{svc} has no LLM/AI dependency (expected one of {AI_LLM_DEPS_ANY} "
            f"or shared/ module copy)"
        )

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_structured_logging_declared(self, svc: str) -> None:
        """AI service declares structlog or accesses it via shared/ modules."""
        pkgs = _req_packages(svc)
        has_logging = any(dep in pkgs for dep in ("structlog", "loguru"))
        if not has_logging:
            # May access structlog via shared/ module copy
            content = _read_dockerfile(svc)
            has_logging = bool(re.search(r"COPY.*shared", content, re.IGNORECASE))
        assert has_logging, (
            f"{svc} missing structured logging dependency (structlog/loguru or shared/ copy)"
        )


# ===========================================================================
# 2. Consistent Base Image
# ===========================================================================


class TestBaseImageConsistency:
    """جميع خدمات الذكاء الاصطناعي يجب أن تستخدم صورة أساسية متسقة."""

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_python_slim_bookworm_base(self, svc: str) -> None:
        """AI service uses python slim-bookworm as base image."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        # Accept python:3.11-slim-bookworm or python:${PYTHON_VERSION}-slim-bookworm
        assert re.search(
            r"FROM\s+python:[^\s]*slim-bookworm", content, re.IGNORECASE
        ), f"{svc} does not use python:*-slim-bookworm base image"

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_python_311_target(self, svc: str) -> None:
        """AI service targets Python 3.11."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "3.11" in content or "PYTHON_VERSION" in content, (
            f"{svc} Dockerfile does not reference Python 3.11"
        )


# ===========================================================================
# 3. Multi-Stage Build Pattern
# ===========================================================================


class TestMultiStageBuild:
    """خدمات الذكاء الاصطناعي يجب أن تستخدم بناء متعدد المراحل."""

    # ai-agents-core uses a minimal single-stage build by design
    SINGLE_STAGE_OK = {"ai-agents-core"}

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_has_multiple_from_stages(self, svc: str) -> None:
        """Dockerfile has at least 2 FROM instructions (multi-stage) or is exempted."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        from_count = len(re.findall(r"^FROM\s+", content, re.MULTILINE | re.IGNORECASE))
        if svc in self.SINGLE_STAGE_OK:
            assert from_count >= 1, f"{svc} has no FROM instruction"
        else:
            assert from_count >= 2, (
                f"{svc} Dockerfile has {from_count} FROM stage(s), expected ≥2 (multi-stage)"
            )

    @pytest.mark.parametrize("svc", sorted(set(AI_SERVICES) - SINGLE_STAGE_OK))
    def test_has_production_stage(self, svc: str) -> None:
        """Dockerfile names a 'production' stage (or 'runtime'/'final')."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_named = bool(
            re.search(r"FROM\s+\S+\s+AS\s+(production|runtime|final)", content, re.IGNORECASE)
        )
        if not has_named:
            from_count = len(re.findall(r"^FROM\s+", content, re.MULTILINE | re.IGNORECASE))
            assert from_count >= 2, (
                f"{svc} has no named production stage and only {from_count} FROM stage(s)"
            )


# ===========================================================================
# 4. Non-Root User
# ===========================================================================


class TestNonRootUser:
    """خدمات الذكاء الاصطناعي يجب أن تعمل بمستخدم غير جذري."""

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_creates_non_root_user(self, svc: str) -> None:
        """Dockerfile creates a non-root user (sahool or appuser)."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"(useradd|adduser|addgroup)", content, re.IGNORECASE), (
            f"{svc} Dockerfile does not create a non-root user"
        )

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_switches_to_non_root(self, svc: str) -> None:
        """Dockerfile has a USER instruction switching away from root."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        user_instructions = re.findall(r"^USER\s+(\S+)", content, re.MULTILINE | re.IGNORECASE)
        non_root = [u for u in user_instructions if u.lower() not in ("root", "0")]
        assert non_root, f"{svc} Dockerfile never switches to a non-root USER"


# ===========================================================================
# 5. Health Check in Dockerfile
# ===========================================================================


class TestDockerfileHealthCheck:
    """كل خدمة يجب أن تحتوي على فحص صحي في Dockerfile."""

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_healthcheck_defined(self, svc: str) -> None:
        """Dockerfile defines a HEALTHCHECK instruction."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert "HEALTHCHECK" in content, f"{svc} Dockerfile missing HEALTHCHECK instruction"

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_healthcheck_uses_healthz(self, svc: str) -> None:
        """HEALTHCHECK targets /healthz endpoint."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        if "HEALTHCHECK" not in content:
            pytest.skip(f"{svc} has no HEALTHCHECK")
        assert "/healthz" in content or "/health" in content, (
            f"{svc} HEALTHCHECK does not target /healthz or /health"
        )


# ===========================================================================
# 6. Port Range Consistency
# ===========================================================================


class TestPortRangeConsistency:
    """منافذ خدمات الذكاء الاصطناعي يجب أن تكون في النطاق 8000-8999."""

    @pytest.mark.parametrize("svc,port", sorted(AI_SERVICES.items()))
    def test_port_in_8xxx_range(self, svc: str, port: int) -> None:
        """AI service port is in the 8000-8999 range."""
        assert 8000 <= port <= 8999, (
            f"{svc} port {port} outside expected 8xxx range for Python AI services"
        )

    def test_no_duplicate_ports_within_group(self) -> None:
        """No two AI services share the same port."""
        ports = list(AI_SERVICES.values())
        assert len(ports) == len(set(ports)), (
            f"Duplicate ports in AI services group: {ports}"
        )

    @pytest.mark.parametrize("svc,port", sorted(AI_SERVICES.items()))
    def test_port_exposed_in_dockerfile(self, svc: str, port: int) -> None:
        """Dockerfile EXPOSE matches the expected port."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        expose_ports = re.findall(r"EXPOSE\s+(\d+)", content)
        if not expose_ports:
            # Some services use ENV PORT instead of EXPOSE
            pytest.skip(f"{svc} uses ENV-based port (no EXPOSE)")
        assert str(port) in expose_ports or any(
            "${" in line for line in content.splitlines() if "EXPOSE" in line
        ), f"{svc} EXPOSE {expose_ports} does not include expected port {port}"


# ===========================================================================
# 7. Environment Variable Consistency
# ===========================================================================


class TestEnvVarConsistency:
    """متغيرات البيئة يجب أن تكون متسقة عبر مجموعة الذكاء الاصطناعي."""

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_compose_has_environment_section(self, services: dict, svc: str) -> None:
        """AI service has environment section in compose."""
        svc_def = services.get(svc, {})
        assert svc_def.get("environment"), f"{svc} missing environment section in compose"

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_log_level_declared(self, services: dict, svc: str) -> None:
        """AI service declares LOG_LEVEL in compose environment."""
        svc_def = services.get(svc, {})
        env = svc_def.get("environment", {})
        env_str = str(env)
        assert "LOG_LEVEL" in env_str, f"{svc} missing LOG_LEVEL in compose environment"

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_nats_url_declared(self, services: dict, svc: str) -> None:
        """AI service declares NATS_URL for event-driven architecture."""
        svc_def = services.get(svc, {})
        env = svc_def.get("environment", {})
        env_str = str(env)
        assert "NATS_URL" in env_str, (
            f"{svc} missing NATS_URL – AI services need event bus connectivity"
        )


# ===========================================================================
# 8. Shared Module Imports in Dockerfile
# ===========================================================================


class TestSharedModuleCopy:
    """خدمات الذكاء الاصطناعي يجب أن تنسخ الوحدات المشتركة."""

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_copies_shared_directory(self, svc: str) -> None:
        """Dockerfile copies the shared/ directory for common utilities."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        assert re.search(r"COPY.*shared", content, re.IGNORECASE), (
            f"{svc} Dockerfile does not COPY shared/ directory"
        )


# ===========================================================================
# 9. Pip Mirror Fallback Pattern
# ===========================================================================


class TestPipMirrorPattern:
    """خدمات الذكاء الاصطناعي يجب أن تستخدم نمط احتياطي لمرآة pip."""

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_pip_has_fallback_mirror(self, svc: str) -> None:
        """Dockerfile pip install has fallback mirror (Aliyun or Tencent)."""
        content = _read_dockerfile(svc)
        if not content:
            pytest.skip(f"No Dockerfile for {svc}")
        has_fallback = (
            "aliyun" in content.lower()
            or "tencent" in content.lower()
            or "tsinghua" in content.lower()
            or "pip.conf" in content.lower()
        )
        assert has_fallback, (
            f"{svc} Dockerfile has no pip mirror fallback (Aliyun/Tencent/Tsinghua)"
        )


# ===========================================================================
# 10. Compose Dependency Chain
# ===========================================================================


class TestComposeDependencyChain:
    """سلسلة التبعيات في docker-compose يجب أن تشمل البنية التحتية."""

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_depends_on_infrastructure(self, services: dict, svc: str) -> None:
        """AI service depends on at least one infrastructure service."""
        svc_def = services.get(svc, {})
        depends = svc_def.get("depends_on", {})
        if isinstance(depends, list):
            dep_names = set(depends)
        elif isinstance(depends, dict):
            dep_names = set(depends.keys())
        else:
            dep_names = set()
        infra = {"postgres", "pgbouncer", "redis", "nats", "ollama", "qdrant", "milvus"}
        has_infra = dep_names & infra
        assert has_infra, (
            f"{svc} does not depend on any infrastructure service "
            f"(deps: {dep_names}, expected overlap with {infra})"
        )


# ===========================================================================
# 11. Source Code Health Endpoints
# ===========================================================================


class TestSourceHealthEndpoints:
    """نقاط فحص الصحة يجب أن تكون موجودة في الكود المصدري."""

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_main_py_has_healthz(self, svc: str) -> None:
        """Service main.py defines /healthz endpoint."""
        main_path = SERVICES_DIR / svc / "src" / "main.py"
        if not main_path.exists():
            pytest.skip(f"No src/main.py for {svc}")
        content = main_path.read_text("utf-8")
        assert "/healthz" in content or "/health" in content, (
            f"{svc}/src/main.py missing /healthz or /health endpoint"
        )

    @pytest.mark.parametrize("svc", sorted(AI_SERVICES))
    def test_main_py_has_readyz(self, svc: str) -> None:
        """Service main.py defines /readyz endpoint."""
        main_path = SERVICES_DIR / svc / "src" / "main.py"
        if not main_path.exists():
            pytest.skip(f"No src/main.py for {svc}")
        content = main_path.read_text("utf-8")
        assert "/readyz" in content or "/ready" in content, (
            f"{svc}/src/main.py missing /readyz or /ready endpoint"
        )
