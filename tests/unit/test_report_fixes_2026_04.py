"""
Platform Report Fixes Verification Tests — April 2026
اختبارات التحقق من إصلاحات تقرير المنصة — أبريل 2026

Validates fixes for issues identified in:
  docs/reports/platform-comprehensive-review-2026-04-01.md

Tests verify:
1. No hardcoded credentials in docker-compose.test.yml (Issue #23)
2. Redis HA sentinel passwords not exposed via Docker Compose interpolation (Issue #24)
3. AI guardrails integrated in llm-orchestrator-service (Issue #12)
4. AI guardrails integrated in ai-agents-service (Issue #12)
5. .env.test contains all required variables for docker-compose.test.yml
"""

import ast
import re
from pathlib import Path

import pytest

# ═══════════════════════════════════════════════════════════════════════════
# Paths
# ═══════════════════════════════════════════════════════════════════════════

ROOT = Path(__file__).parent.parent.parent
DOCKER_COMPOSE_TEST = ROOT / "docker-compose.test.yml"
DOCKER_COMPOSE_REDIS_HA = ROOT / "docker-compose.redis-ha.yml"
ENV_TEST = ROOT / ".env.test"
LLM_ORCHESTRATOR_MAIN = ROOT / "apps" / "services" / "llm-orchestrator-service" / "src" / "main.py"
AI_AGENTS_MAIN = ROOT / "apps" / "services" / "ai-agents-service" / "src" / "main.py"
COPILOT_CHAT = ROOT / "apps" / "services" / "copilot-api" / "src" / "api" / "v1" / "chat.py"
GUARDRAILS_INIT = ROOT / "shared" / "guardrails" / "__init__.py"
GUARDRAILS_MIDDLEWARE = ROOT / "shared" / "guardrails" / "middleware.py"


# ═══════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def docker_compose_test_content():
    """Load docker-compose.test.yml content."""
    return DOCKER_COMPOSE_TEST.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def docker_compose_redis_ha_content():
    """Load docker-compose.redis-ha.yml content."""
    return DOCKER_COMPOSE_REDIS_HA.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def env_test_content():
    """Load .env.test content."""
    return ENV_TEST.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def env_test_vars(env_test_content):
    """Parse .env.test into a dict of variable names → values."""
    env_vars = {}
    for line in env_test_content.splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, value = line.partition("=")
            env_vars[key.strip()] = value.strip()
    return env_vars


@pytest.fixture(scope="module")
def llm_orchestrator_main_content():
    """Load llm-orchestrator-service main.py content."""
    return LLM_ORCHESTRATOR_MAIN.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def ai_agents_main_content():
    """Load ai-agents-service main.py content."""
    return AI_AGENTS_MAIN.read_text(encoding="utf-8")


# ═══════════════════════════════════════════════════════════════════════════
# Issue #23: No Hardcoded Credentials in docker-compose.test.yml
# المشكلة رقم 23: لا بيانات اعتماد مضمنة في ملف docker-compose.test.yml
# ═══════════════════════════════════════════════════════════════════════════


class TestNoHardcodedCredentials:
    """Verify docker-compose.test.yml has no hardcoded passwords or secrets."""

    # Patterns that indicate hardcoded default credentials.
    # We look for ${VAR:-some_default} where the default is a real-looking password.
    HARDCODED_DEFAULT_PATTERN = re.compile(
        r"\$\{(?:POSTGRES_PASSWORD|REDIS_PASSWORD|JWT_SECRET_KEY|STRIPE_API_KEY|"
        r"QDRANT_API_KEY|OPENWEATHERMAP_API_KEY|WEATHERAPI_KEY|THARWATT_API_KEY)"
        r":-[^}]+\}"
    )

    # Patterns for completely bare/literal passwords (not using env vars at all)
    BARE_PASSWORD_PATTERN = re.compile(
        r"(?:password|secret|api_key|token)\s*[:=]\s*['\"]?(?![\$\{])[a-zA-Z0-9_-]{6,}",
        re.IGNORECASE,
    )

    def test_no_hardcoded_default_passwords(self, docker_compose_test_content):
        """No ${VAR:-default_password} patterns should exist for security-sensitive vars."""
        matches = self.HARDCODED_DEFAULT_PATTERN.findall(docker_compose_test_content)
        assert not matches, (
            f"Found hardcoded default credentials in docker-compose.test.yml: {matches}. "
            "Use ${VAR:?required} instead of ${VAR:-default} for passwords."
        )

    def test_no_bare_test_jwt_token(self, docker_compose_test_content):
        """TEST_JWT_TOKEN should not be a bare string — use env var."""
        # Match literal assignment like: TEST_JWT_TOKEN=some-value (no $ reference)
        bare_jwt = re.findall(
            r"TEST_JWT_TOKEN=(?!\$)[^\s]+",
            docker_compose_test_content,
        )
        assert not bare_jwt, (
            f"Found bare TEST_JWT_TOKEN value: {bare_jwt}. "
            "Use ${TEST_JWT_TOKEN:-} to reference environment variable."
        )

    def test_uses_required_env_vars(self, docker_compose_test_content):
        """Critical credentials should use :? (required) syntax, not :- (default)."""
        # POSTGRES_PASSWORD must be required
        assert "${POSTGRES_PASSWORD:?" in docker_compose_test_content, (
            "POSTGRES_PASSWORD should use :? (required) syntax"
        )
        # REDIS_PASSWORD must be required
        assert "${REDIS_PASSWORD:?" in docker_compose_test_content, (
            "REDIS_PASSWORD should use :? (required) syntax"
        )
        # JWT_SECRET_KEY must be required
        assert "${JWT_SECRET_KEY:?" in docker_compose_test_content, (
            "JWT_SECRET_KEY should use :? (required) syntax"
        )

    def test_documentation_references_env_file(self, docker_compose_test_content):
        """docker-compose.test.yml header should reference .env.test for credentials."""
        assert ".env.test" in docker_compose_test_content, (
            "docker-compose.test.yml should reference .env.test file in its header comments"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Issue #24: Redis HA Sentinel Passwords Not Exposed
# المشكلة رقم 24: كلمات مرور Redis Sentinel غير مكشوفة
# ═══════════════════════════════════════════════════════════════════════════


class TestRedisHASentinelSecurity:
    """Verify Redis HA sentinel passwords are not exposed in docker inspect."""

    def test_sentinel_uses_runtime_expansion(self, docker_compose_redis_ha_content):
        """Sentinel auth-pass should use $$ (runtime) not $ (compose-time) expansion."""
        # Find all sentinel auth-pass lines
        auth_lines = [
            line.strip()
            for line in docker_compose_redis_ha_content.splitlines()
            if "sentinel auth-pass" in line
        ]
        assert len(auth_lines) >= 3, (
            f"Expected at least 3 sentinel auth-pass lines, found {len(auth_lines)}"
        )
        for line in auth_lines:
            # Should use $${REDIS_PASSWORD} (escaped $ → runtime expansion)
            # NOT ${REDIS_PASSWORD} (compose-time interpolation → visible in inspect)
            assert "$${REDIS_PASSWORD}" in line or "$$REDIS_PASSWORD" in line, (
                f"Sentinel auth-pass should use runtime variable expansion ($$), "
                f"not compose-time interpolation ($). Line: {line}"
            )

    def test_no_literal_passwords_in_sentinel(self, docker_compose_redis_ha_content):
        """No literal password values should appear in sentinel config."""
        # Check that no plaintext password appears after 'sentinel auth-pass'
        literal_password = re.findall(
            r"sentinel auth-pass sahool-master\s+[a-zA-Z0-9_!@#%^&*()-]+(?:\s|$)",
            docker_compose_redis_ha_content,
        )
        # Filter out env var references
        for match in literal_password:
            assert "$" in match, (
                f"Found possible literal password in sentinel config: {match}"
            )


# ═══════════════════════════════════════════════════════════════════════════
# .env.test Completeness
# اكتمال ملف .env.test
# ═══════════════════════════════════════════════════════════════════════════


class TestEnvTestCompleteness:
    """Verify .env.test contains all variables needed by docker-compose.test.yml."""

    REQUIRED_VARS = [
        "POSTGRES_PASSWORD",
        "REDIS_PASSWORD",
        "JWT_SECRET_KEY",
        "STRIPE_API_KEY",
        "QDRANT_API_KEY",
    ]

    def test_all_required_vars_present(self, env_test_vars):
        """All variables required by docker-compose.test.yml must be in .env.test."""
        missing = [var for var in self.REQUIRED_VARS if var not in env_test_vars]
        assert not missing, (
            f"Missing required variables in .env.test: {missing}. "
            f"docker-compose.test.yml will fail without these."
        )

    def test_passwords_are_non_empty(self, env_test_vars):
        """Password variables in .env.test must have non-empty values."""
        password_vars = ["POSTGRES_PASSWORD", "REDIS_PASSWORD", "JWT_SECRET_KEY"]
        empty = [var for var in password_vars if not env_test_vars.get(var)]
        assert not empty, f"Empty password variables in .env.test: {empty}"

    def test_jwt_secret_minimum_length(self, env_test_vars):
        """JWT secret key must be at least 32 characters."""
        jwt_key = env_test_vars.get("JWT_SECRET_KEY", "")
        assert len(jwt_key) >= 32, (
            f"JWT_SECRET_KEY in .env.test is only {len(jwt_key)} chars, "
            "minimum 32 required for HS256"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Issue #12: AI Guardrails Integration
# المشكلة رقم 12: تكامل حواجز أمان الذكاء الاصطناعي
# ═══════════════════════════════════════════════════════════════════════════


class TestGuardrailsIntegration:
    """Verify AI guardrails are integrated in all AI services."""

    def test_guardrails_module_exists(self):
        """shared/guardrails/__init__.py must exist and export key classes."""
        assert GUARDRAILS_INIT.exists(), "shared/guardrails/__init__.py not found"
        content = GUARDRAILS_INIT.read_text(encoding="utf-8")
        assert "GuardrailsMiddleware" in content
        assert "GuardrailsConfig" in content
        assert "setup_guardrails" in content
        assert "TrustLevel" in content

    def test_guardrails_middleware_exists(self):
        """shared/guardrails/middleware.py must exist with setup_guardrails()."""
        assert GUARDRAILS_MIDDLEWARE.exists(), "shared/guardrails/middleware.py not found"
        content = GUARDRAILS_MIDDLEWARE.read_text(encoding="utf-8")
        assert "def setup_guardrails" in content
        assert "class GuardrailsMiddleware" in content

    def test_llm_orchestrator_imports_guardrails(self, llm_orchestrator_main_content):
        """llm-orchestrator-service must import guardrails."""
        assert "from shared.guardrails" in llm_orchestrator_main_content, (
            "llm-orchestrator-service/src/main.py must import from shared.guardrails"
        )

    def test_llm_orchestrator_calls_setup_guardrails(self, llm_orchestrator_main_content):
        """llm-orchestrator-service must call setup_guardrails()."""
        assert "setup_guardrails(" in llm_orchestrator_main_content, (
            "llm-orchestrator-service/src/main.py must call setup_guardrails()"
        )

    def test_llm_orchestrator_guardrails_config(self, llm_orchestrator_main_content):
        """llm-orchestrator-service must configure GuardrailsConfig."""
        assert "GuardrailsConfig(" in llm_orchestrator_main_content, (
            "llm-orchestrator-service/src/main.py must create GuardrailsConfig"
        )

    def test_ai_agents_imports_guardrails(self, ai_agents_main_content):
        """ai-agents-service must import guardrails."""
        assert "from shared.guardrails" in ai_agents_main_content, (
            "ai-agents-service/src/main.py must import from shared.guardrails"
        )

    def test_ai_agents_calls_setup_guardrails(self, ai_agents_main_content):
        """ai-agents-service must call setup_guardrails()."""
        assert "setup_guardrails(" in ai_agents_main_content, (
            "ai-agents-service/src/main.py must call setup_guardrails()"
        )

    def test_ai_agents_guardrails_config(self, ai_agents_main_content):
        """ai-agents-service must configure GuardrailsConfig."""
        assert "GuardrailsConfig(" in ai_agents_main_content, (
            "ai-agents-service/src/main.py must create GuardrailsConfig"
        )

    def test_copilot_api_has_guardrails(self):
        """copilot-api must have guardrails (baseline — was already integrated)."""
        assert COPILOT_CHAT.exists(), "copilot-api chat.py not found"
        content = COPILOT_CHAT.read_text(encoding="utf-8")
        assert "guardrails" in content.lower() or "input_filter" in content, (
            "copilot-api/src/api/v1/chat.py must use guardrails or input_filter"
        )


# ═══════════════════════════════════════════════════════════════════════════
# Guardrails Configuration Quality
# جودة إعدادات حواجز الأمان
# ═══════════════════════════════════════════════════════════════════════════


class TestGuardrailsConfigQuality:
    """Verify guardrails configurations follow best practices."""

    def test_llm_orchestrator_excludes_health_paths(self, llm_orchestrator_main_content):
        """Health/readiness endpoints must be excluded from guardrails."""
        assert "/healthz" in llm_orchestrator_main_content
        assert "/readyz" in llm_orchestrator_main_content

    def test_llm_orchestrator_has_strict_paths(self, llm_orchestrator_main_content):
        """AI-facing endpoints must be in strict_paths for enhanced checking."""
        assert "strict_paths" in llm_orchestrator_main_content

    def test_ai_agents_excludes_health_paths(self, ai_agents_main_content):
        """Health/readiness endpoints must be excluded from guardrails."""
        assert "/healthz" in ai_agents_main_content
        assert "/readyz" in ai_agents_main_content

    def test_ai_agents_block_violations_enabled(self, ai_agents_main_content):
        """block_violations must be True to prevent unsafe input from reaching AI."""
        assert "block_violations=True" in ai_agents_main_content

    def test_llm_orchestrator_pii_masking_enabled(self, llm_orchestrator_main_content):
        """PII masking must be enabled to protect farmer data."""
        assert "mask_pii=True" in llm_orchestrator_main_content

    def test_guardrails_conditional_import(self, llm_orchestrator_main_content):
        """Guardrails import must be conditional (try/except) for graceful degradation."""
        assert "GUARDRAILS_AVAILABLE" in llm_orchestrator_main_content
        # Should have a try/except block for import
        assert "except ImportError" in llm_orchestrator_main_content

    def test_guardrails_env_toggle(self, llm_orchestrator_main_content):
        """Guardrails must be toggleable via GUARDRAILS_ENABLED env var."""
        assert "GUARDRAILS_ENABLED" in llm_orchestrator_main_content


# ═══════════════════════════════════════════════════════════════════════════
# Cross-Validation: All 3 AI Services Have Guardrails
# التحقق المتقاطع: جميع خدمات AI الثلاث لديها حواجز أمان
# ═══════════════════════════════════════════════════════════════════════════


class TestAllAIServicesProtected:
    """Verify all AI-facing services have guardrails protection."""

    AI_SERVICES_WITH_GUARDRAILS = [
        ("copilot-api", ROOT / "apps" / "services" / "copilot-api" / "src"),
        ("llm-orchestrator-service", ROOT / "apps" / "services" / "llm-orchestrator-service" / "src"),
        ("ai-agents-service", ROOT / "apps" / "services" / "ai-agents-service" / "src"),
    ]

    @pytest.mark.parametrize("service_name,src_path", AI_SERVICES_WITH_GUARDRAILS)
    def test_service_has_guardrails_reference(self, service_name, src_path):
        """Each AI service must reference guardrails in its source code."""
        found = False
        for py_file in src_path.rglob("*.py"):
            content = py_file.read_text(encoding="utf-8", errors="ignore")
            if "guardrails" in content.lower() or "input_filter" in content:
                found = True
                break
        assert found, (
            f"Service {service_name} has no guardrails reference in {src_path}. "
            "All AI services must integrate shared.guardrails for safety."
        )
