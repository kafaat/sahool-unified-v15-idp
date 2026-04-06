"""
Tests for docker-compose.yml service configuration fixes
اختبارات إصلاحات تكوين الخدمات في docker-compose

Validates:
- code-review-agent has ANTHROPIC_API_KEY
- code-review-service profile is NOT gpu
- code-fix-agent has OLLAMA_URL and OLLAMA_MODEL
"""

import os

import pytest

try:
    import yaml
except ImportError:
    yaml = None

COMPOSE_PATH = os.path.join(os.path.dirname(__file__), "../../docker-compose.yml")


@pytest.fixture
def compose_config():
    """Load docker-compose.yml as dict."""
    if yaml is None:
        pytest.skip("PyYAML not installed")
    with open(COMPOSE_PATH) as f:
        return yaml.safe_load(f)


class TestCodeReviewAgentConfig:
    """Test code-review-agent docker-compose configuration."""

    def test_anthropic_api_key_present(self, compose_config):
        """code-review-agent must have ANTHROPIC_API_KEY in environment."""
        service = compose_config["services"]["code-review-agent"]
        env_list = service.get("environment", [])

        anthropic_vars = [e for e in env_list if "ANTHROPIC_API_KEY" in str(e)]
        assert len(anthropic_vars) >= 1, (
            "code-review-agent missing ANTHROPIC_API_KEY environment variable"
        )

    def test_has_ai_agents_profile(self, compose_config):
        """code-review-agent should be in ai-agents profile."""
        service = compose_config["services"]["code-review-agent"]
        profiles = service.get("profiles", [])
        assert "ai-agents" in profiles


class TestCodeReviewServiceConfig:
    """Test code-review-service docker-compose configuration."""

    def test_profile_not_gpu(self, compose_config):
        """code-review-service should NOT be in gpu profile."""
        service = compose_config["services"]["code-review-service"]
        profiles = service.get("profiles", [])
        assert "gpu" not in profiles, (
            "code-review-service should not require GPU profile. "
            "It uses Ollama (LLM), not CUDA directly."
        )

    def test_profile_is_ai_or_tools(self, compose_config):
        """code-review-service should be in ai or tools profile."""
        service = compose_config["services"]["code-review-service"]
        profiles = service.get("profiles", [])
        assert "ai" in profiles or "tools" in profiles, (
            f"code-review-service profiles should include 'ai' or 'tools', got: {profiles}"
        )

    def test_depends_on_ollama(self, compose_config):
        """code-review-service should depend on ollama."""
        service = compose_config["services"]["code-review-service"]
        depends = service.get("depends_on", {})
        assert "ollama" in depends, (
            "code-review-service should depend on ollama"
        )


class TestCodeFixAgentConfig:
    """Test code-fix-agent docker-compose configuration."""

    def test_ollama_url_present(self, compose_config):
        """code-fix-agent must have OLLAMA_URL in environment."""
        service = compose_config["services"]["code-fix-agent"]
        env_list = service.get("environment", [])

        ollama_vars = [e for e in env_list if "OLLAMA_URL" in str(e)]
        assert len(ollama_vars) >= 1, (
            "code-fix-agent missing OLLAMA_URL environment variable. "
            "Without it, localhost:11434 is used inside the container, "
            "which doesn't reach the ollama service."
        )

    def test_ollama_url_points_to_service(self, compose_config):
        """OLLAMA_URL should point to ollama service (not localhost)."""
        service = compose_config["services"]["code-fix-agent"]
        env_list = service.get("environment", [])

        for env in env_list:
            if "OLLAMA_URL=" in str(env):
                assert "ollama:" in str(env), (
                    f"OLLAMA_URL should point to 'ollama:11434', got: {env}"
                )
                assert "localhost" not in str(env), (
                    f"OLLAMA_URL should NOT use localhost inside Docker: {env}"
                )

    def test_ollama_model_present(self, compose_config):
        """code-fix-agent should have OLLAMA_MODEL in environment."""
        service = compose_config["services"]["code-fix-agent"]
        env_list = service.get("environment", [])

        model_vars = [e for e in env_list if "OLLAMA_MODEL" in str(e)]
        assert len(model_vars) >= 1, (
            "code-fix-agent missing OLLAMA_MODEL environment variable"
        )
