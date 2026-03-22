"""
Tests for models and service methods defined in main.py
Tests CodeReviewHandler, CodeReviewService methods, and Pydantic models.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch, PropertyMock

import pytest

# Add service directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# We need to import from src.main which has heavy dependencies.
# Pre-mock the shared modules and external deps that may not be available.
_mock_shared_auth = MagicMock()
_mock_shared_auth.dependencies.get_current_user = MagicMock()
_mock_shared_auth.models.User = MagicMock()
sys.modules.setdefault("shared.auth", _mock_shared_auth)
sys.modules.setdefault("shared.auth.dependencies", _mock_shared_auth.dependencies)
sys.modules.setdefault("shared.auth.models", _mock_shared_auth.models)
sys.modules.setdefault("shared.errors_py", MagicMock(
    add_request_id_middleware=MagicMock(),
    setup_exception_handlers=MagicMock(),
))
sys.modules.setdefault("shared.middleware.tenant_context", MagicMock(
    TenantContextMiddleware=type("FakeMW", (), {"__init__": lambda *a, **kw: None}),
))


from src.main import (
    CacheStatsResponse,
    CodeReviewHandler,
    CodeReviewRequest,
    CodeReviewService,
    FileReviewRequest,
    HealthResponse,
    ModelInfo,
    PRReviewRequest,
    ReviewResponse,
    get_service,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Pydantic Model Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCodeReviewRequest:
    def test_defaults(self):
        req = CodeReviewRequest(code="x = 1")
        assert req.language is None
        assert req.filename is None
        assert req.use_cache is True
        assert req.model is None

    def test_all_fields(self):
        req = CodeReviewRequest(
            code="def f(): pass",
            language="python",
            filename="test.py",
            use_cache=False,
            model="codellama",
        )
        assert req.language == "python"
        assert req.use_cache is False


class TestFileReviewRequest:
    def test_creation(self):
        req = FileReviewRequest(file_path="/app/src/main.py")
        assert req.file_path == "/app/src/main.py"


class TestPRReviewRequest:
    def test_defaults(self):
        req = PRReviewRequest(pr_number=42)
        assert req.pr_number == 42
        assert req.owner is None
        assert req.repo is None
        assert req.post_comment is True


class TestReviewResponse:
    def test_creation(self):
        resp = ReviewResponse(
            summary="Good code",
            score=85,
            critical_issues=["bug1"],
            suggestions=["add tests"],
            security_concerns=[],
            agricultural_issues=["NDVI issue"],
            model_used="codellama",
            cached=True,
        )
        assert resp.score == 85
        assert resp.cached is True
        assert len(resp.agricultural_issues) == 1

    def test_score_min(self):
        resp = ReviewResponse(summary="Bad", score=0)
        assert resp.score == 0

    def test_score_max(self):
        resp = ReviewResponse(summary="Perfect", score=100)
        assert resp.score == 100

    def test_score_out_of_range(self):
        with pytest.raises(Exception):
            ReviewResponse(summary="X", score=101)

    def test_score_negative(self):
        with pytest.raises(Exception):
            ReviewResponse(summary="X", score=-1)


class TestHealthResponse:
    def test_creation(self):
        resp = HealthResponse(
            status="healthy",
            service="code-review-service",
            ollama_connected=True,
            available_models=["deepseek", "codellama"],
            cache_enabled=True,
            github_enabled=False,
        )
        assert resp.version == "16.0.0"
        assert len(resp.available_models) == 2

    def test_defaults(self):
        resp = HealthResponse(
            status="degraded",
            service="code-review-service",
            ollama_connected=False,
        )
        assert resp.available_models == []
        assert resp.cache_enabled is False
        assert resp.github_enabled is False


class TestCacheStatsResponse:
    def test_creation(self):
        resp = CacheStatsResponse(backend="memory", size=50, hits=30, misses=20, hit_rate="60.0%")
        assert resp.size == 50
        assert resp.hit_rate == "60.0%"

    def test_defaults(self):
        resp = CacheStatsResponse(backend="disabled")
        assert resp.size is None
        assert resp.hits == 0
        assert resp.misses == 0


class TestModelInfo:
    def test_creation(self):
        info = ModelInfo(name="deepseek", url="http://ollama:11434", available=True, priority=0)
        assert info.name == "deepseek"
        assert info.priority == 0


# ═══════════════════════════════════════════════════════════════════════════════
# CodeReviewService Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCodeReviewServiceMethods:
    """Test CodeReviewService methods with mocked settings."""

    @pytest.fixture
    def service(self):
        """Create a service with mocked settings."""
        svc = CodeReviewService.__new__(CodeReviewService)
        svc.settings = MagicMock(
            enable_cache=False,
            github_token=None,
            enable_agricultural_rules=False,
            enable_fallback=False,
            ollama_url="http://localhost:11434",
            ollama_model="test-model",
            review_on_change=False,
            max_retries=1,
            retry_delay=0,
            max_file_size=1000000,
            log_reviews_to_file=False,
            watch_paths="",
            cache_backend="memory",
            redis_url="redis://localhost:6379",
            cache_file_path="/tmp/test.json",
            cache_max_size=10,
            cache_ttl=3600,
            github_api_url="https://api.github.com",
            github_webhook_secret=None,
            get_fallback_models_list=MagicMock(return_value=[]),
        )
        svc.session = None
        svc.observer = None
        svc.cache = None
        svc.github = None
        svc.agricultural_engine = MagicMock()
        svc._available_models = []
        return svc

    def test_parse_response_valid_json(self, service):
        result = service._parse_response('{"summary": "Good", "score": 90}')
        assert result["summary"] == "Good"
        assert result["score"] == 90

    def test_parse_response_json_code_block(self, service):
        text = '```json\n{"summary": "OK", "score": 70}\n```'
        result = service._parse_response(text)
        assert result["score"] == 70

    def test_parse_response_generic_code_block(self, service):
        text = '```\n{"summary": "Test"}\n```'
        result = service._parse_response(text)
        assert result["summary"] == "Test"
        assert result["score"] == 75  # default

    def test_parse_response_invalid_json(self, service):
        result = service._parse_response("Not JSON at all")
        assert result["summary"] == "Not JSON at all"
        assert result["score"] == 75

    def test_parse_response_empty(self, service):
        result = service._parse_response("")
        assert result["summary"] == "No response"

    def test_create_review_prompt_with_language(self, service):
        prompt = service._create_review_prompt(Path("test.py"), "x = 1", language="python")
        assert "Python" in prompt
        assert "test.py" in prompt

    def test_create_review_prompt_typescript(self, service):
        prompt = service._create_review_prompt(Path("app.ts"), "const x = 1")
        assert "TypeScript" in prompt

    def test_create_review_prompt_unknown_ext(self, service):
        prompt = service._create_review_prompt(Path("file.xyz"), "content")
        assert "Code" in prompt

    def test_create_review_prompt_agri_context(self, service):
        from src.agricultural_rules import AgriculturalAnalysis

        analysis = AgriculturalAnalysis(
            is_agricultural_code=True,
            detected_domains=["ndvi", "sensor"],
        )
        prompt = service._create_review_prompt(Path("ndvi.py"), "ndvi = 0.5", agri_analysis=analysis)
        assert "ndvi" in prompt.lower() or "sensor" in prompt.lower()

    def test_create_review_prompt_truncation(self, service):
        long_code = "x = 1\n" * 10000  # Way more than 5000 chars
        prompt = service._create_review_prompt(Path("big.py"), long_code)
        # The code in the prompt should be limited
        assert len(prompt) < len(long_code)

    def test_get_available_models_empty(self, service):
        models = service.get_available_models()
        assert models == []

    def test_get_available_models_populated(self, service):
        service._available_models = [
            ("deepseek", "http://localhost:11434", True),
            ("codellama", "http://localhost:11434", False),
        ]
        models = service.get_available_models()
        assert len(models) == 2
        assert models[0].name == "deepseek"
        assert models[0].available is True
        assert models[1].available is False
        assert models[0].priority == 0
        assert models[1].priority == 1

    def test_log_review_no_logging(self, service):
        """When log_reviews_to_file is False, _log_review should do nothing."""
        service.settings.log_reviews_to_file = False
        # Should not raise
        service._log_review(Path("test.py"), {"score": 80, "summary": "OK"})


# ═══════════════════════════════════════════════════════════════════════════════
# CodeReviewHandler Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestCodeReviewHandler:
    """Test the CodeReviewHandler file watcher logic."""

    @pytest.fixture
    def handler(self):
        mock_service = MagicMock()
        mock_service.settings = MagicMock(
            max_file_size=1000000,
            watch_paths="apps/services:shared",
            debounce_delay=0.1,
        )
        return CodeReviewHandler(mock_service)

    def test_should_review_valid_python(self, handler, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        handler.settings.watch_paths = str(tmp_path)
        assert handler._should_review(test_file) is True

    def test_should_review_invalid_extension(self, handler, tmp_path):
        test_file = tmp_path / "image.png"
        test_file.write_bytes(b"\x89PNG")
        handler.settings.watch_paths = str(tmp_path)
        assert handler._should_review(test_file) is False

    def test_should_review_file_too_large(self, handler, tmp_path):
        test_file = tmp_path / "big.py"
        test_file.write_text("x" * 2000000)
        handler.settings.max_file_size = 1000000
        handler.settings.watch_paths = str(tmp_path)
        assert handler._should_review(test_file) is False

    def test_should_review_outside_watch_path(self, handler, tmp_path):
        test_file = tmp_path / "test.py"
        test_file.write_text("x = 1")
        handler.settings.watch_paths = "/some/other/path"
        assert handler._should_review(test_file) is False

    def test_should_review_nonexistent_file(self, handler):
        assert handler._should_review(Path("/nonexistent/file.py")) is False

    def test_on_modified_directory(self, handler):
        event = MagicMock()
        event.is_directory = True
        handler.on_modified(event)
        # Should return early, no review scheduled

    def test_on_created_directory(self, handler):
        event = MagicMock()
        event.is_directory = True
        handler.on_created(event)
        # Should return early, no review scheduled

    def test_valid_extensions(self, handler, tmp_path):
        """Test all valid extensions are recognized."""
        handler.settings.watch_paths = str(tmp_path)
        valid_exts = [".py", ".ts", ".tsx", ".js", ".jsx", ".yml", ".yaml",
                      ".json", ".md", ".sh", ".dockerfile", ".tf", ".go", ".rs"]
        for ext in valid_exts:
            test_file = tmp_path / f"test{ext}"
            test_file.write_text("content")
            assert handler._should_review(test_file) is True, f"Extension {ext} should be reviewable"


# ═══════════════════════════════════════════════════════════════════════════════
# get_service Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestGetService:
    def test_get_service_singleton(self):
        """get_service returns a CodeReviewService instance."""
        import src.main as main_module
        main_module._service_instance = None  # Reset
        svc = get_service()
        assert isinstance(svc, CodeReviewService)
        svc2 = get_service()
        assert svc is svc2  # Same instance
        main_module._service_instance = None  # Cleanup


# ═══════════════════════════════════════════════════════════════════════════════
# Async Method Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
class TestCodeReviewServiceAsync:
    """Test async methods of CodeReviewService."""

    @pytest.fixture
    def service(self):
        svc = CodeReviewService.__new__(CodeReviewService)
        svc.settings = MagicMock(
            enable_cache=False,
            github_token=None,
            enable_agricultural_rules=False,
            enable_fallback=False,
            ollama_url="http://localhost:11434",
            ollama_model="test-model",
            review_on_change=False,
            max_retries=1,
            retry_delay=0,
            max_file_size=1000000,
            log_reviews_to_file=False,
            watch_paths="",
            cache_backend="memory",
            redis_url="redis://localhost:6379",
            cache_file_path="/tmp/test.json",
            cache_max_size=10,
            cache_ttl=3600,
            github_api_url="https://api.github.com",
            github_webhook_secret=None,
            github_comment_threshold=70,
            get_fallback_models_list=MagicMock(return_value=[]),
        )
        svc.session = MagicMock()
        svc.observer = None
        svc.cache = None
        svc.github = None
        svc.agricultural_engine = MagicMock()
        svc._available_models = []
        return svc

    async def test_review_code_empty_raises(self, service):
        """Empty code should raise ValueError."""
        with pytest.raises(ValueError, match="empty"):
            await service.review_code("   ")

    async def test_review_code_with_cache_hit(self, service):
        """Test review_code returns cached result."""
        service.settings.enable_cache = True
        mock_cache = AsyncMock()
        mock_cache.get = AsyncMock(return_value={"summary": "cached", "score": 80})
        service.cache = mock_cache

        result = await service.review_code("x = 1", use_cache=True)
        assert result["cached"] is True
        assert result["summary"] == "cached"

    async def test_get_review_with_fallback_no_models(self, service):
        """When no models available, return error."""
        service._available_models = []
        result, model = await service._get_review_with_fallback("prompt")
        assert "error" in result
        assert model == "none"

    async def test_check_ollama_health_failure(self, service):
        """Test ollama health check when connection fails."""
        service.session = MagicMock()
        service.session.get = MagicMock(side_effect=Exception("Connection refused"))
        result = await service.check_ollama_health()
        assert result is False

    async def test_close_cleanup(self, service):
        """Test close cleans up resources."""
        mock_session = AsyncMock()
        mock_observer = MagicMock()
        mock_github = AsyncMock()

        service.session = mock_session
        service.observer = mock_observer
        service.github = mock_github

        await service.close()
        mock_session.close.assert_called_once()
        mock_observer.stop.assert_called_once()
        mock_github.close.assert_called_once()

    async def test_close_no_resources(self, service):
        """Test close with no resources to clean."""
        service.session = None
        service.observer = None
        service.github = None
        await service.close()  # Should not raise

    async def test_review_pr_no_github(self, service):
        """Test review_pr raises when GitHub not configured."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException):
            await service.review_pr(pr_number=1)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
