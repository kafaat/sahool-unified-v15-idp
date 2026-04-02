"""
Tests for LLM gaps — streaming, provider failover, availability cache TTL,
cloud provider mocks (Anthropic / OpenAI / Google / DeepSeek), health checks.

يغطي هذه الاختبارات الفجوات المكتشفة في الفحص العميق لكود LLM:
- معالجة خطأ JSON في streaming
- انتهاء صلاحية كاش توافر المزود (TTL)
- failover chain بين المزودين
- health checks لجميع المزودين
- استدعاءات المزودين السحابيين (Anthropic / OpenAI / Google / DeepSeek)
"""

from __future__ import annotations

import json
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from shared.llm.config import OllamaConfig
from shared.llm.ollama import OllamaError, OllamaProvider
from shared.llm.provider import (
    GenerationResponse,
    GenerationStatus,
    Message,
    ModelNotFoundError,
    ProviderType,
)
from shared.llm.router import (
    AllProvidersFailedError,
    LLMRouter,
    RoutingDecision,
    _AVAILABILITY_CACHE_TTL,
)


# ═══════════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════════


def _make_ollama_response(text: str = "ok") -> GenerationResponse:
    return GenerationResponse(
        text=text,
        model="llama3.2",
        provider=ProviderType.OLLAMA,
        status=GenerationStatus.SUCCESS,
        tokens_input=5,
        tokens_output=3,
        latency_ms=50.0,
        cost_usd=0.0,
    )


# ═══════════════════════════════════════════════════════════════════════════
# Fix 1 — streaming JSON parse error handling (ollama.py)
# ═══════════════════════════════════════════════════════════════════════════


class TestOllamaStreamingJsonErrors:
    """Verify that malformed JSON lines are skipped, not fatal (Bug #1)."""

    @pytest.mark.asyncio
    async def test_generate_stream_skips_malformed_json(self):
        """
        A single malformed JSON line in the stream must not terminate the
        generator — valid subsequent lines must still arrive.

        يجب أن يتم تجاهل سطر JSON غير صالح وليس إنهاء الـ stream.
        """
        good_line = json.dumps({"response": "hello", "done": False})
        bad_line = "NOT JSON{{{"
        final_line = json.dumps({"response": " world", "done": True})

        raw_lines = [good_line, bad_line, final_line]

        provider = OllamaProvider(OllamaConfig())

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        async def fake_aiter_lines():
            for line in raw_lines:
                yield line

        mock_response.aiter_lines = fake_aiter_lines

        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_cm)

        with patch.object(provider, "_get_client", AsyncMock(return_value=mock_client)):
            chunks = []
            async for chunk in provider.generate_stream("Hello"):
                chunks.append(chunk)

        texts = [c.text for c in chunks if c.text]
        assert "hello" in texts, "Valid chunk before bad line must arrive"
        assert " world" in texts, "Valid chunk after bad line must arrive"
        # Stream terminates on the final done=True chunk
        assert chunks[-1].is_final is True

    @pytest.mark.asyncio
    async def test_chat_stream_skips_malformed_json(self):
        """
        Same resilience requirement for chat_stream (Bug #1 — second instance).
        """
        good_line = json.dumps({"message": {"content": "hi"}, "done": False})
        bad_line = "GARBAGE"
        final_line = json.dumps({"message": {"content": " there"}, "done": True})

        raw_lines = [good_line, bad_line, final_line]

        provider = OllamaProvider(OllamaConfig())

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        async def fake_aiter_lines():
            for line in raw_lines:
                yield line

        mock_response.aiter_lines = fake_aiter_lines

        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_cm)

        with patch.object(provider, "_get_client", AsyncMock(return_value=mock_client)):
            chunks = []
            msgs = [Message(role="user", content="Hello")]
            async for chunk in provider.chat_stream(msgs):
                chunks.append(chunk)

        texts = [c.text for c in chunks if c.text]
        assert "hi" in texts
        assert " there" in texts
        assert chunks[-1].is_final is True

    @pytest.mark.asyncio
    async def test_generate_stream_all_malformed_yields_nothing(self):
        """
        If every line is malformed, the stream should complete with no chunks
        rather than raising an exception.
        """
        raw_lines = ["GARBAGE1", "GARBAGE2", "GARBAGE3"]

        provider = OllamaProvider(OllamaConfig())

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.raise_for_status = MagicMock()

        async def fake_aiter_lines():
            for line in raw_lines:
                yield line

        mock_response.aiter_lines = fake_aiter_lines

        mock_cm = MagicMock()
        mock_cm.__aenter__ = AsyncMock(return_value=mock_response)
        mock_cm.__aexit__ = AsyncMock(return_value=False)

        mock_client = MagicMock()
        mock_client.stream = MagicMock(return_value=mock_cm)

        with patch.object(provider, "_get_client", AsyncMock(return_value=mock_client)):
            chunks = []
            async for chunk in provider.generate_stream("Hello"):
                chunks.append(chunk)

        # No valid JSON → no chunks emitted, but no exception raised
        assert chunks == []


# ═══════════════════════════════════════════════════════════════════════════
# Fix 2 — provider availability cache TTL (router.py)
# ═══════════════════════════════════════════════════════════════════════════


class TestRouterAvailabilityCacheTTL:
    """Verify that _check_provider_available respects _AVAILABILITY_CACHE_TTL."""

    @pytest.mark.asyncio
    async def test_ttl_constant_is_positive(self):
        """TTL must be a positive number."""
        assert _AVAILABILITY_CACHE_TTL > 0

    @pytest.mark.asyncio
    async def test_fresh_negative_result_is_cached(self):
        """
        A False availability result that was just stored must not trigger
        a new health check within the TTL window.
        """
        router = LLMRouter()

        call_count = 0

        async def mock_is_available() -> bool:
            nonlocal call_count
            call_count += 1
            return False

        mock_provider = MagicMock()
        mock_provider.is_available = mock_is_available

        with patch.object(router, "_get_provider", return_value=mock_provider):
            # First call — actually invokes is_available
            result1 = await router._check_provider_available(ProviderType.OLLAMA)
            # Second call — must use cache, NOT call is_available again
            result2 = await router._check_provider_available(ProviderType.OLLAMA)

        assert result1 is False
        assert result2 is False
        assert call_count == 1, "is_available should only be called once (cache hit on second call)"

    @pytest.mark.asyncio
    async def test_stale_negative_result_triggers_recheck(self):
        """
        Once the TTL has passed, a previously-False result must be re-checked
        so a provider that was temporarily down can recover.
        """
        router = LLMRouter()

        call_count = 0

        async def mock_is_available() -> bool:
            nonlocal call_count
            call_count += 1
            return False

        mock_provider = MagicMock()
        mock_provider.is_available = mock_is_available

        with patch.object(router, "_get_provider", return_value=mock_provider):
            # Populate cache
            await router._check_provider_available(ProviderType.OLLAMA)
            assert call_count == 1

            # Simulate TTL expiry by back-dating the timestamp
            router._provider_available_at[ProviderType.OLLAMA] = (
                time.monotonic() - _AVAILABILITY_CACHE_TTL - 1.0
            )

            # Should re-check now that cache is stale
            await router._check_provider_available(ProviderType.OLLAMA)

        assert call_count == 2, "is_available must be called again after TTL expires"

    @pytest.mark.asyncio
    async def test_generation_error_clears_both_cache_entries(self):
        """
        When generate() fails, both _provider_available and
        _provider_available_at must be cleared so the next availability
        check is fresh (not stale).
        Patch decide_routing to always return an OLLAMA decision so the test
        is not affected by the runtime ENVIRONMENT env var.
        """
        router = LLMRouter()

        # Manually set a stale True entry
        router._provider_available[ProviderType.OLLAMA] = True
        router._provider_available_at[ProviderType.OLLAMA] = time.monotonic() - 1.0

        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=RuntimeError("network failure"))
        mock_provider.is_available = AsyncMock(return_value=True)

        fixed_decision = RoutingDecision(
            provider_type=ProviderType.OLLAMA,
            model="llama3.2",
            reason="test",
            fallbacks=[],
        )

        with (
            patch.object(router, "_get_provider", return_value=mock_provider),
            patch.object(router, "_check_provider_available", return_value=True),
            patch.object(router, "decide_routing", return_value=fixed_decision),
        ):
            try:
                await router.generate("test")
            except AllProvidersFailedError:
                pass  # expected — all providers failed

        assert router._provider_available.get(ProviderType.OLLAMA) is None
        assert ProviderType.OLLAMA not in router._provider_available_at


# ═══════════════════════════════════════════════════════════════════════════
# Provider failover chain
# ═══════════════════════════════════════════════════════════════════════════


class TestProviderFailoverChain:
    """Verify that the router falls back through providers on failure."""

    @pytest.mark.asyncio
    async def test_falls_back_to_next_provider_on_error(self):
        """
        When the primary provider raises an exception, the router must
        attempt the next provider in the fallback list.
        """
        router = LLMRouter()

        call_log: list[str] = []

        async def first_fail(*_a, **_kw):
            call_log.append("first")
            raise RuntimeError("primary failed")

        async def second_ok(*_a, **_kw):
            call_log.append("second")
            return _make_ollama_response("fallback ok")

        primary_provider = MagicMock()
        primary_provider.generate = AsyncMock(side_effect=first_fail)

        fallback_provider = MagicMock()
        fallback_provider.generate = AsyncMock(side_effect=second_ok)

        providers_map = {
            ProviderType.OLLAMA: primary_provider,
            ProviderType.OPENAI_COMPAT: fallback_provider,
        }

        async def fake_get_provider(pt):
            return providers_map.get(pt)

        decision = RoutingDecision(
            provider_type=ProviderType.OLLAMA,
            model="llama3.2",
            reason="test",
            fallbacks=[(ProviderType.OPENAI_COMPAT, "gpt-4o-mini")],
        )

        with (
            patch.object(router, "_get_provider", side_effect=fake_get_provider),
            patch.object(router, "_check_provider_available", return_value=True),
            patch.object(router, "decide_routing", return_value=decision),
        ):
            response = await router.generate("hello", enable_fallback=True)

        assert response.text == "fallback ok"
        assert "first" in call_log
        assert "second" in call_log
        assert router._stats.fallback_count == 1

    @pytest.mark.asyncio
    async def test_all_providers_fail_raises_all_providers_failed(self):
        """
        When every provider in the chain fails, AllProvidersFailedError
        must be raised containing all individual errors.
        """
        router = LLMRouter()

        failing_provider = MagicMock()
        failing_provider.generate = AsyncMock(side_effect=RuntimeError("down"))

        decision = RoutingDecision(
            provider_type=ProviderType.OLLAMA,
            model="llama3.2",
            reason="test",
            fallbacks=[(ProviderType.OPENAI_COMPAT, "model-x")],
        )

        with (
            patch.object(router, "_get_provider", return_value=failing_provider),
            patch.object(router, "_check_provider_available", return_value=True),
            patch.object(router, "decide_routing", return_value=decision),
        ):
            with pytest.raises(AllProvidersFailedError) as exc_info:
                await router.generate("hello", enable_fallback=True)

        err = exc_info.value
        assert len(err.errors) == 2
        # Both provider names should appear in the error message
        assert "ollama" in str(err).lower()

    @pytest.mark.asyncio
    async def test_fallback_disabled_stops_after_first_failure(self):
        """
        With enable_fallback=False, the router must NOT try the next provider.
        """
        router = LLMRouter()

        call_log: list[str] = []

        async def first_fail(*_a, **_kw):
            call_log.append("primary")
            raise RuntimeError("primary failed")

        async def second_ok(*_a, **_kw):  # must NOT be reached
            call_log.append("fallback")
            return _make_ollama_response("should not be returned")

        providers_map = {
            ProviderType.OLLAMA: MagicMock(generate=AsyncMock(side_effect=first_fail)),
            ProviderType.OPENAI_COMPAT: MagicMock(generate=AsyncMock(side_effect=second_ok)),
        }

        decision = RoutingDecision(
            provider_type=ProviderType.OLLAMA,
            model="llama3.2",
            reason="test",
            fallbacks=[(ProviderType.OPENAI_COMPAT, "gpt-4o-mini")],
        )

        with (
            patch.object(router, "_get_provider", side_effect=lambda pt: providers_map.get(pt)),
            patch.object(router, "_check_provider_available", return_value=True),
            patch.object(router, "decide_routing", return_value=decision),
        ):
            with pytest.raises(AllProvidersFailedError):
                await router.generate("hello", enable_fallback=False)

        assert "primary" in call_log
        assert "fallback" not in call_log


# ═══════════════════════════════════════════════════════════════════════════
# Health checks
# ═══════════════════════════════════════════════════════════════════════════


class TestProviderHealthChecks:
    """Tests for provider health check paths."""

    @pytest.mark.asyncio
    async def test_unavailable_provider_is_skipped(self):
        """
        When is_available() returns False, the router must skip that provider
        and not attempt a generate() call.
        """
        router = LLMRouter()

        generate_called = False

        async def should_not_be_called(*_a, **_kw):
            nonlocal generate_called
            generate_called = True
            return _make_ollama_response()

        mock_provider = MagicMock()
        mock_provider.is_available = AsyncMock(return_value=False)
        mock_provider.generate = AsyncMock(side_effect=should_not_be_called)

        decision = RoutingDecision(
            provider_type=ProviderType.OLLAMA,
            model="llama3.2",
            reason="test",
            fallbacks=[],
        )

        with (
            patch.object(router, "_get_provider", return_value=mock_provider),
            patch.object(router, "decide_routing", return_value=decision),
        ):
            with pytest.raises(AllProvidersFailedError):
                await router.generate("hello", enable_fallback=False)

        assert not generate_called

    @pytest.mark.asyncio
    async def test_health_check_timeout_marks_provider_unavailable(self):
        """
        A timeout during is_available() must store False in the cache.
        Mock asyncio.wait_for to raise TimeoutError immediately so the test
        does not actually wait 5 seconds.
        """
        import asyncio

        router = LLMRouter()

        mock_provider = MagicMock()
        mock_provider.is_available = AsyncMock(return_value=True)

        with (
            patch.object(router, "_get_provider", return_value=mock_provider),
            patch("asyncio.wait_for", side_effect=asyncio.TimeoutError),
        ):
            result = await router._check_provider_available(ProviderType.OLLAMA)

        assert result is False
        assert router._provider_available[ProviderType.OLLAMA] is False

    @pytest.mark.asyncio
    async def test_available_provider_stored_in_cache(self):
        """
        When is_available() returns True the result must be cached so
        a second call does not invoke is_available() again.
        """
        router = LLMRouter()

        call_count = 0

        async def healthy():
            nonlocal call_count
            call_count += 1
            return True

        mock_provider = MagicMock()
        mock_provider.is_available = healthy

        with patch.object(router, "_get_provider", return_value=mock_provider):
            r1 = await router._check_provider_available(ProviderType.OLLAMA)
            r2 = await router._check_provider_available(ProviderType.OLLAMA)

        assert r1 is True
        assert r2 is True
        assert call_count == 1


# ═══════════════════════════════════════════════════════════════════════════
# Cloud provider API call mocks (Anthropic / OpenAI / Google / DeepSeek)
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMProviderManagerCloudProviders:
    """
    Tests for cloud provider integrations using mocks.
    These tests cover the previously-untested _call_anthropic,
    _call_openai, _call_google, and _call_deepseek paths.
    """

    def _make_manager_with_provider(self, provider_enum, model: str, api_key: str = "test-key"):
        """Create a manager with exactly one explicitly-configured provider."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider, LLMProviderManager

        cfg = LLMConfig(
            provider=provider_enum,
            model=model,
            api_key=api_key,
            priority=0,
        )
        return LLMProviderManager(configs=[cfg], enable_audit=False, enable_metrics=False)

    @pytest.mark.asyncio
    async def test_call_anthropic_used_for_anthropic_provider(self):
        """_call_anthropic must be invoked when ANTHROPIC is the active provider."""
        from shared.ai.llm_provider import LLMProvider, LLMProviderManager, LLMResponse

        manager = self._make_manager_with_provider(LLMProvider.ANTHROPIC, "claude-3-haiku-20240307")

        expected = LLMResponse(
            text="The answer is 42.",
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-haiku-20240307",
            tokens_input=10,
            tokens_output=8,
            latency_ms=200.0,
            cost_usd=0.0002,
        )

        with patch.object(manager, "_call_anthropic", new_callable=AsyncMock, return_value=expected) as mock_call:
            response = await manager.generate(prompt="What is the meaning of life?")

        mock_call.assert_called_once()
        assert response.text == "The answer is 42."
        assert response.provider == LLMProvider.ANTHROPIC

    @pytest.mark.asyncio
    async def test_call_openai_used_for_openai_provider(self):
        """_call_openai must be invoked when OPENAI is the active provider."""
        from shared.ai.llm_provider import LLMProvider, LLMResponse

        manager = self._make_manager_with_provider(LLMProvider.OPENAI, "gpt-4o-mini")

        expected = LLMResponse(
            text="OpenAI response",
            provider=LLMProvider.OPENAI,
            model="gpt-4o-mini",
            tokens_input=15,
            tokens_output=10,
            latency_ms=300.0,
            cost_usd=0.0001,
        )

        with patch.object(manager, "_call_openai", new_callable=AsyncMock, return_value=expected) as mock_call:
            response = await manager.generate(prompt="Say hello")

        mock_call.assert_called_once()
        assert response.text == "OpenAI response"
        assert response.provider == LLMProvider.OPENAI

    @pytest.mark.asyncio
    async def test_call_google_used_for_google_provider(self):
        """_call_google must be invoked when GOOGLE is the active provider."""
        from shared.ai.llm_provider import LLMProvider, LLMResponse

        manager = self._make_manager_with_provider(LLMProvider.GOOGLE, "gemini-1.5-flash")

        expected = LLMResponse(
            text="Gemini response",
            provider=LLMProvider.GOOGLE,
            model="gemini-1.5-flash",
            tokens_input=12,
            tokens_output=9,
            latency_ms=250.0,
            cost_usd=0.00005,
        )

        with patch.object(manager, "_call_google", new_callable=AsyncMock, return_value=expected) as mock_call:
            response = await manager.generate(prompt="Summarize agriculture")

        mock_call.assert_called_once()
        assert response.text == "Gemini response"
        assert response.provider == LLMProvider.GOOGLE

    @pytest.mark.asyncio
    async def test_call_deepseek_used_for_deepseek_provider(self):
        """_call_deepseek must be invoked when DEEPSEEK is the active provider."""
        from shared.ai.llm_provider import LLMProvider, LLMResponse

        manager = self._make_manager_with_provider(LLMProvider.DEEPSEEK, "deepseek-coder")

        expected = LLMResponse(
            text="DeepSeek code response",
            provider=LLMProvider.DEEPSEEK,
            model="deepseek-coder",
            tokens_input=20,
            tokens_output=15,
            latency_ms=180.0,
            cost_usd=0.00003,
        )

        with patch.object(manager, "_call_deepseek", new_callable=AsyncMock, return_value=expected) as mock_call:
            response = await manager.generate(prompt="Write a Python function")

        mock_call.assert_called_once()
        assert response.text == "DeepSeek code response"
        assert response.provider == LLMProvider.DEEPSEEK

    @pytest.mark.asyncio
    async def test_cloud_provider_raises_on_api_failure(self):
        """When a cloud provider API call fails, AllProvidersFailedError must be raised."""
        from shared.ai.llm_provider import AllProvidersFailedError, LLMProvider, LLMProviderError

        manager = self._make_manager_with_provider(LLMProvider.ANTHROPIC, "claude-3-haiku-20240307")

        with patch.object(
            manager,
            "_call_anthropic",
            new_callable=AsyncMock,
            side_effect=LLMProviderError("API key invalid", provider=LLMProvider.ANTHROPIC),
        ):
            with pytest.raises(AllProvidersFailedError):
                await manager.generate(prompt="test")

    @pytest.mark.asyncio
    async def test_provider_fallback_from_anthropic_to_ollama(self):
        """When Anthropic fails, manager falls back to Ollama if it's configured."""
        from shared.ai.llm_provider import LLMConfig, LLMProvider, LLMProviderError, LLMProviderManager, LLMResponse

        configs = [
            LLMConfig(provider=LLMProvider.ANTHROPIC, model="claude-3-haiku", api_key="key", priority=0),
            LLMConfig(provider=LLMProvider.OLLAMA, model="codellama:7b", priority=1),
        ]
        manager = LLMProviderManager(configs=configs, enable_audit=False, enable_metrics=False)

        ollama_response = LLMResponse(
            text="Ollama fallback response",
            provider=LLMProvider.OLLAMA,
            model="codellama:7b",
            tokens_input=10,
            tokens_output=5,
            latency_ms=100.0,
            cost_usd=0.0,
        )

        with (
            patch.object(
                manager,
                "_call_anthropic",
                new_callable=AsyncMock,
                side_effect=LLMProviderError("Anthropic down", provider=LLMProvider.ANTHROPIC),
            ),
            patch.object(
                manager,
                "_call_ollama",
                new_callable=AsyncMock,
                return_value=ollama_response,
            ),
        ):
            response = await manager.generate(prompt="test")

        assert response.text == "Ollama fallback response"
        assert response.provider == LLMProvider.OLLAMA


# ═══════════════════════════════════════════════════════════════════════════
# LLMConfig SSRF protection
# ═══════════════════════════════════════════════════════════════════════════


class TestLLMConfigSSRFProtection:
    """SSRF protection: base_url must only accept http/https."""

    def test_http_base_url_accepted(self):
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        cfg = LLMConfig(
            provider=LLMProvider.OLLAMA,
            model="codellama:7b",
            base_url="http://localhost:11434",
        )
        assert cfg.base_url == "http://localhost:11434"

    def test_https_base_url_accepted(self):
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        cfg = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-haiku",
            api_key="key",
            base_url="https://api.anthropic.com",
        )
        assert cfg.base_url is not None

    def test_file_scheme_rejected(self):
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        with pytest.raises(ValueError, match="http/https"):
            LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="x",
                base_url="file:///etc/passwd",
            )

    def test_ftp_scheme_rejected(self):
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        with pytest.raises(ValueError, match="http/https"):
            LLMConfig(
                provider=LLMProvider.OLLAMA,
                model="x",
                base_url="ftp://attacker.com/model",
            )

    def test_masked_api_key_short(self):
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        cfg = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-haiku",
            api_key="sk",
        )
        assert cfg.masked_api_key == "****"

    def test_masked_api_key_normal(self):
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        cfg = LLMConfig(
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-haiku",
            api_key="sk-ant-1234ABCD",
        )
        assert cfg.masked_api_key is not None
        assert cfg.masked_api_key.startswith("****")
        assert "ABCD" in cfg.masked_api_key
        # Full key must NOT appear
        assert "sk-ant-1234" not in cfg.masked_api_key

    def test_api_key_not_in_repr(self):
        from shared.ai.llm_provider import LLMConfig, LLMProvider

        cfg = LLMConfig(
            provider=LLMProvider.OPENAI,
            model="gpt-4o",
            api_key="super-secret-key",
        )
        r = repr(cfg)
        assert "super-secret-key" not in r


# ═══════════════════════════════════════════════════════════════════════════
# Router stats
# ═══════════════════════════════════════════════════════════════════════════


class TestRouterStats:
    """Router statistics tracking."""

    @pytest.mark.asyncio
    async def test_successful_request_increments_stats(self):
        router = LLMRouter()

        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(return_value=_make_ollama_response("hello"))
        mock_provider.is_available = AsyncMock(return_value=True)

        decision = RoutingDecision(
            provider_type=ProviderType.OLLAMA,
            model="llama3.2",
            reason="test",
            fallbacks=[],
        )

        with (
            patch.object(router, "_get_provider", return_value=mock_provider),
            patch.object(router, "_check_provider_available", return_value=True),
            patch.object(router, "decide_routing", return_value=decision),
        ):
            await router.generate("hello")

        assert router.stats.total_requests == 1
        assert router.stats.successful_requests == 1
        assert router.stats.failed_requests == 0

    @pytest.mark.asyncio
    async def test_failed_request_increments_failed_stats(self):
        router = LLMRouter()

        mock_provider = MagicMock()
        mock_provider.generate = AsyncMock(side_effect=RuntimeError("oops"))

        decision = RoutingDecision(
            provider_type=ProviderType.OLLAMA,
            model="llama3.2",
            reason="test",
            fallbacks=[],
        )

        with (
            patch.object(router, "_get_provider", return_value=mock_provider),
            patch.object(router, "_check_provider_available", return_value=True),
            patch.object(router, "decide_routing", return_value=decision),
        ):
            with pytest.raises(AllProvidersFailedError):
                await router.generate("hello", enable_fallback=False)

        assert router.stats.failed_requests == 1


# ═══════════════════════════════════════════════════════════════════════════
# Empty generate() response detection
# ═══════════════════════════════════════════════════════════════════════════


class TestOllamaGenerateEmptyResponse:
    """
    The generate() path should behave predictably when the server returns
    an empty 'response' field.  The result is still SUCCESS (Ollama can
    legitimately return empty responses for some prompts), but the text
    must be an empty string — not None or missing.
    """

    @pytest.mark.asyncio
    async def test_empty_response_field_returned_as_empty_string(self):
        """An Ollama JSON response without 'response' key yields text=''."""
        provider = OllamaProvider(OllamaConfig())

        # Server returns valid JSON but with no 'response' key
        mock_http_response = MagicMock()
        mock_http_response.status_code = 200
        mock_http_response.raise_for_status = MagicMock()
        mock_http_response.json = MagicMock(return_value={"model": "llama3.2", "done": True})

        mock_client = MagicMock()
        mock_client.post = AsyncMock(return_value=mock_http_response)

        with patch.object(provider, "_get_client", AsyncMock(return_value=mock_client)):
            result = await provider.generate("test prompt")

        assert result.text == ""
        assert result.status == GenerationStatus.SUCCESS

    @pytest.mark.asyncio
    async def test_model_not_found_404_raises_correct_error(self):
        """A 404 response during generate() must raise ModelNotFoundError specifically."""
        import httpx

        provider = OllamaProvider(OllamaConfig())

        http_404 = httpx.HTTPStatusError(
            "404",
            request=MagicMock(),
            response=MagicMock(status_code=404),
        )

        mock_client = MagicMock()
        mock_client.post = AsyncMock(side_effect=http_404)

        with patch.object(provider, "_get_client", AsyncMock(return_value=mock_client)):
            with pytest.raises(ModelNotFoundError) as exc_info:
                await provider.generate("test", model="nonexistent-model")

        assert exc_info.value.model == "nonexistent-model"
        assert exc_info.value.provider == ProviderType.OLLAMA


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
