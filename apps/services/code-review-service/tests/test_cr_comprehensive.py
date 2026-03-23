"""
Comprehensive tests for Code Review Service
اختبارات شاملة لخدمة مراجعة الكود

Covers: cache, agricultural_rules, github_integration, main service logic, models
"""

import hashlib
import json
import os
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# Add service directory to path
# ═══════════════════════════════════════════════════════════════════════════════
# Cache Tests (cache.py)
# ═══════════════════════════════════════════════════════════════════════════════
class TestGenerateCacheKey:
    """Tests for the generate_cache_key function."""

    def test_cache_key_deterministic(self):
        from src.cache import generate_cache_key

        key1 = generate_cache_key("print('hello')", "python", "model1")
        key2 = generate_cache_key("print('hello')", "python", "model1")
        assert key1 == key2

    def test_cache_key_different_code(self):
        from src.cache import generate_cache_key

        key1 = generate_cache_key("print('a')", "python")
        key2 = generate_cache_key("print('b')", "python")
        assert key1 != key2

    def test_cache_key_different_language(self):
        from src.cache import generate_cache_key

        key1 = generate_cache_key("x = 1", "python")
        key2 = generate_cache_key("x = 1", "javascript")
        assert key1 != key2

    def test_cache_key_none_values(self):
        from src.cache import generate_cache_key

        key = generate_cache_key("code", None, None)
        assert len(key) == 32  # SHA256 truncated to 32 chars

    def test_cache_key_length(self):
        from src.cache import generate_cache_key

        key = generate_cache_key("some code", "py", "model")
        assert len(key) == 32


@pytest.mark.asyncio
class TestMemoryCache:
    """Tests for MemoryCache backend."""

    @pytest.fixture
    def cache(self):
        from src.cache import MemoryCache

        return MemoryCache(max_size=5, default_ttl=3600)

    async def test_set_and_get(self, cache):
        await cache.set("key1", {"score": 85})
        result = await cache.get("key1")
        assert result == {"score": 85}

    async def test_get_missing_key(self, cache):
        result = await cache.get("nonexistent")
        assert result is None

    async def test_get_expired_key(self, cache):
        """Test expired key returns None by manually setting past expiry."""
        # Directly insert with past expiry to avoid race condition
        cache._cache["expiring"] = ({"data": "old"}, time.time() - 1)
        result = await cache.get("expiring")
        assert result is None

    async def test_lru_eviction(self, cache):
        """Test LRU eviction when cache is full."""
        for i in range(6):  # max_size=5
            await cache.set(f"key{i}", {"i": i})
        # key0 should have been evicted
        result = await cache.get("key0")
        assert result is None
        result = await cache.get("key5")
        assert result == {"i": 5}

    async def test_delete(self, cache):
        await cache.set("key1", {"data": "value"})
        result = await cache.delete("key1")
        assert result is True
        assert await cache.get("key1") is None

    async def test_delete_missing(self, cache):
        result = await cache.delete("nonexistent")
        assert result is False

    async def test_clear(self, cache):
        await cache.set("k1", {"a": 1})
        await cache.set("k2", {"b": 2})
        result = await cache.clear()
        assert result is True
        assert await cache.get("k1") is None

    async def test_stats(self, cache):
        await cache.set("k1", {"a": 1})
        await cache.get("k1")  # hit
        await cache.get("k2")  # miss
        stats = await cache.stats()
        assert stats["backend"] == "memory"
        assert stats["size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert "hit_rate" in stats

    async def test_stats_no_accesses(self, cache):
        stats = await cache.stats()
        assert stats["hit_rate"] == "0.0%"


class TestCreateCacheBackend:
    """Tests for create_cache_backend factory."""

    def test_create_memory_backend(self):
        from src.cache import MemoryCache, create_cache_backend

        backend = create_cache_backend("memory", max_size=100, default_ttl=600)
        assert isinstance(backend, MemoryCache)

    def test_create_redis_backend(self):
        from src.cache import RedisCache, create_cache_backend

        backend = create_cache_backend("redis", redis_url="redis://localhost:6379")
        assert isinstance(backend, RedisCache)

    def test_create_redis_without_url_raises(self):
        from src.cache import create_cache_backend

        with pytest.raises(ValueError, match="redis_url required"):
            create_cache_backend("redis")

    def test_create_file_backend(self, tmp_path):
        from src.cache import FileCache, create_cache_backend

        cache_file = str(tmp_path / "cache.json")
        backend = create_cache_backend("file", cache_path=cache_file)
        assert isinstance(backend, FileCache)

    def test_create_unknown_backend_defaults_to_memory(self):
        from src.cache import MemoryCache, create_cache_backend

        backend = create_cache_backend("unknown_backend")
        assert isinstance(backend, MemoryCache)


@pytest.mark.asyncio
class TestFileCache:
    """Tests for FileCache backend."""

    @pytest.fixture
    def cache(self, tmp_path):
        from src.cache import FileCache

        cache_file = str(tmp_path / "test_cache.json")
        return FileCache(cache_path=cache_file)

    async def test_set_and_get(self, cache):
        await cache.set("k1", {"score": 90})
        result = await cache.get("k1")
        assert result == {"score": 90}

    async def test_get_missing_key(self, cache):
        result = await cache.get("missing")
        assert result is None

    async def test_get_expired(self, cache):
        """Test expired file cache entry by manually writing past expiry."""
        cache_data = {"exp": {"value": {"old": True}, "expiry": time.time() - 1, "created": time.time() - 2}}
        cache._save_cache(cache_data)
        result = await cache.get("exp")
        assert result is None

    async def test_delete(self, cache):
        await cache.set("k1", {"val": 1})
        assert await cache.delete("k1") is True
        assert await cache.get("k1") is None

    async def test_delete_missing(self, cache):
        assert await cache.delete("nope") is False

    async def test_clear(self, cache):
        await cache.set("k1", {"v": 1})
        await cache.clear()
        assert await cache.get("k1") is None

    async def test_stats(self, cache):
        await cache.set("k1", {"v": 1})
        await cache.get("k1")
        await cache.get("k2")
        stats = await cache.stats()
        assert stats["backend"] == "file"
        assert stats["hits"] == 1
        assert stats["misses"] == 1


# ═══════════════════════════════════════════════════════════════════════════════
# Agricultural Rules Tests (agricultural_rules.py)
# ═══════════════════════════════════════════════════════════════════════════════
class TestAgriculturalIssue:
    """Tests for AgriculturalIssue dataclass."""

    def test_to_dict(self):
        from src.agricultural_rules import AgriculturalIssue

        issue = AgriculturalIssue(
            category="ndvi",
            severity="critical",
            message_en="NDVI out of range",
            message_ar="NDVI خارج النطاق",
            line_number=10,
            code_snippet="ndvi = 2.0",
        )
        d = issue.to_dict()
        assert d["category"] == "ndvi"
        assert d["severity"] == "critical"
        assert "NDVI out of range" in d["message"]
        assert "NDVI خارج النطاق" in d["message"]
        assert d["line"] == 10
        assert d["snippet"] == "ndvi = 2.0"


class TestAgriculturalAnalysis:
    """Tests for AgriculturalAnalysis dataclass."""

    def test_add_critical_issue(self):
        from src.agricultural_rules import AgriculturalAnalysis, AgriculturalIssue

        analysis = AgriculturalAnalysis()
        analysis.add_issue(
            AgriculturalIssue(
                category="ndvi",
                severity="critical",
                message_en="Bad",
                message_ar="سيء",
            )
        )
        assert len(analysis.issues) == 1
        assert analysis.score_modifier == -15

    def test_add_warning_issue(self):
        from src.agricultural_rules import AgriculturalAnalysis, AgriculturalIssue

        analysis = AgriculturalAnalysis()
        analysis.add_issue(
            AgriculturalIssue(
                category="sensor",
                severity="warning",
                message_en="Warn",
                message_ar="تحذير",
            )
        )
        assert analysis.score_modifier == -5

    def test_add_info_issue(self):
        from src.agricultural_rules import AgriculturalAnalysis, AgriculturalIssue

        analysis = AgriculturalAnalysis()
        analysis.add_issue(
            AgriculturalIssue(
                category="general",
                severity="info",
                message_en="Info",
                message_ar="معلومة",
            )
        )
        assert analysis.score_modifier == -1

    def test_get_issue_messages(self):
        from src.agricultural_rules import AgriculturalAnalysis, AgriculturalIssue

        analysis = AgriculturalAnalysis()
        analysis.add_issue(
            AgriculturalIssue(
                category="ndvi",
                severity="warning",
                message_en="Range issue",
                message_ar="مشكلة نطاق",
            )
        )
        msgs = analysis.get_issue_messages()
        assert len(msgs) == 1
        assert "Range issue" in msgs[0]


class TestAgriculturalRulesEngine:
    """Tests for AgriculturalRulesEngine."""

    @pytest.fixture
    def engine(self):
        from src.agricultural_rules import AgriculturalRulesEngine

        return AgriculturalRulesEngine()

    def test_detect_ndvi_domain(self, engine):
        code = "ndvi = (nir - red) / (nir + red)"
        analysis = engine.analyze(code)
        assert "ndvi" in analysis.detected_domains
        assert analysis.is_agricultural_code is True

    def test_detect_lai_domain(self, engine):
        code = "lai = leaf_area_index(canopy)"
        analysis = engine.analyze(code)
        assert "lai" in analysis.detected_domains

    def test_detect_sensor_domain(self, engine):
        code = "reading = soil_moisture.read()"
        analysis = engine.analyze(code)
        assert "sensor" in analysis.detected_domains

    def test_detect_irrigation_domain(self, engine):
        code = "irrigation_schedule(drip, evapotranspiration)"
        analysis = engine.analyze(code)
        assert "irrigation" in analysis.detected_domains

    def test_detect_crop_domain(self, engine):
        code = "yield_prediction = predict_yield(crop_health)"
        analysis = engine.analyze(code)
        assert "crop" in analysis.detected_domains

    def test_non_agricultural_code(self, engine):
        code = "def hello():\n    print('world')"
        analysis = engine.analyze(code)
        assert analysis.is_agricultural_code is False
        assert len(analysis.issues) == 0

    def test_ndvi_out_of_range_critical(self, engine):
        code = "ndvi = 2.5"
        analysis = engine.analyze(code)
        critical_issues = [i for i in analysis.issues if i.severity == "critical"]
        assert len(critical_issues) >= 1

    def test_ndvi_division_by_zero_warning(self, engine):
        code = "result = (nir - red) / (nir + red)"
        analysis = engine.analyze(code)
        warnings = [i for i in analysis.issues if i.severity == "warning" and i.category == "ndvi"]
        assert len(warnings) >= 1

    def test_ndvi_threshold_without_comment(self, engine):
        code = "if ndvi < 0.3:\n    status = 'bad'"
        analysis = engine.analyze(code)
        info_issues = [i for i in analysis.issues if i.severity == "info" and i.category == "ndvi"]
        assert len(info_issues) >= 1

    def test_lai_out_of_range(self, engine):
        code = "lai = 15.0"
        analysis = engine.analyze(code)
        warnings = [i for i in analysis.issues if i.category == "lai"]
        assert len(warnings) >= 1

    def test_lai_negative(self, engine):
        code = "lai = -3"
        analysis = engine.analyze(code)
        critical = [i for i in analysis.issues if i.severity == "critical" and i.category == "lai"]
        assert len(critical) >= 1

    def test_soil_moisture_out_of_range(self, engine):
        code = "soil_moisture = 150"
        analysis = engine.analyze(code)
        warnings = [i for i in analysis.issues if i.category == "sensor"]
        assert len(warnings) >= 1

    def test_sensor_validation_warning(self, engine):
        code = "val = sensor_reading.read()\nprocess(val)"
        analysis = engine.analyze(code)
        sensor_warnings = [i for i in analysis.issues if i.category == "sensor"]
        assert len(sensor_warnings) >= 1

    def test_sensor_timeout_warning(self, engine):
        code = "mqtt_client.publish('topic', sensor_reading)"
        analysis = engine.analyze(code)
        info_issues = [i for i in analysis.issues if i.category == "sensor" and i.severity == "info"]
        assert len(info_issues) >= 1

    def test_temperature_unrealistic(self, engine):
        """Temperature > 70 should trigger warning. Pattern checks temperature = VALUE."""
        code = "temperature = 100\nsoil_moisture_check()"
        analysis = engine.analyze(code)
        warnings = [i for i in analysis.issues if i.category == "sensor"]
        assert len(warnings) >= 1

    def test_irrigation_negative_water_flow(self, engine):
        code = "water_flow = -50\nirrigation_start()"
        analysis = engine.analyze(code)
        critical = [i for i in analysis.issues if i.severity == "critical" and i.category == "irrigation"]
        assert len(critical) >= 1

    def test_irrigation_without_soil_moisture(self, engine):
        code = "def irrigate(field_id):\n    start_irrigation(field_id)"
        analysis = engine.analyze(code)
        warnings = [i for i in analysis.issues if i.category == "irrigation" and i.severity == "warning"]
        assert len(warnings) >= 1

    def test_et0_missing_factors(self, engine):
        code = "et0 = calculate_evapotranspiration(temperature)"
        analysis = engine.analyze(code)
        info_issues = [i for i in analysis.issues if i.category == "irrigation"]
        assert len(info_issues) >= 1

    def test_yield_prediction_no_confidence(self, engine):
        code = "predicted = yield_prediction(crop_health, ndvi)"
        analysis = engine.analyze(code)
        info_issues = [i for i in analysis.issues if i.category == "crop"]
        assert len(info_issues) >= 1

    def test_crop_health_single_index(self, engine):
        code = "status = crop_health(ndvi_value)"
        analysis = engine.analyze(code)
        info_issues = [i for i in analysis.issues if i.category == "crop"]
        assert len(info_issues) >= 1

    def test_general_timestamp_no_timezone(self, engine):
        code = "ndvi_date = datetime.now()\nndvi = 0.5"
        analysis = engine.analyze(code)
        info_issues = [i for i in analysis.issues if i.category == "general"]
        assert any("timezone" in i.message_en.lower() for i in info_issues)

    def test_general_coordinate_validation(self, engine):
        code = "lat = field.latitude\nndvi = compute_ndvi(lat)"
        analysis = engine.analyze(code)
        warnings = [i for i in analysis.issues if i.category == "general" and "coordinate" in i.message_en.lower()]
        assert len(warnings) >= 1

    def test_get_enhanced_prompt_agricultural(self, engine):
        from src.agricultural_rules import AgriculturalAnalysis

        analysis = AgriculturalAnalysis(
            is_agricultural_code=True,
            detected_domains=["ndvi", "irrigation"],
        )
        prompt = engine.get_enhanced_prompt(analysis)
        assert "NDVI" in prompt
        assert "irrigation" in prompt.lower()

    def test_get_enhanced_prompt_non_agricultural(self, engine):
        from src.agricultural_rules import AgriculturalAnalysis

        analysis = AgriculturalAnalysis(is_agricultural_code=False)
        prompt = engine.get_enhanced_prompt(analysis)
        assert prompt == ""


# ═══════════════════════════════════════════════════════════════════════════════
# GitHub Integration Tests (github_integration.py)
# ═══════════════════════════════════════════════════════════════════════════════
class TestPRReviewResult:
    """Tests for PRReviewResult class."""

    def test_initialization(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=42, owner="kafaat", repo="sahool")
        assert result.pr_number == 42
        assert result.files_reviewed == 0
        assert result.total_score == 0

    def test_add_file_review(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=1, owner="o", repo="r")
        result.add_file_review("test.py", {"score": 80, "summary": "Good"})
        assert result.files_reviewed == 1
        assert result.total_score == 80
        assert result.file_reviews[0]["file"] == "test.py"

    def test_add_multiple_file_reviews(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=1, owner="o", repo="r")
        result.add_file_review("a.py", {"score": 80})
        result.add_file_review("b.py", {"score": 60})
        assert result.files_reviewed == 2
        assert result.total_score == 70  # (80+60)//2

    def test_get_conclusion_success(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=1, owner="o", repo="r")
        result.add_file_review("a.py", {"score": 90})
        assert result.get_conclusion() == "success"

    def test_get_conclusion_neutral(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=1, owner="o", repo="r")
        result.add_file_review("a.py", {"score": 70})
        assert result.get_conclusion() == "neutral"

    def test_get_conclusion_failure(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=1, owner="o", repo="r")
        result.add_file_review("a.py", {"score": 40})
        assert result.get_conclusion() == "failure"

    def test_has_critical_issues_true(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=1, owner="o", repo="r")
        result.add_file_review("a.py", {"score": 40, "critical_issues": ["SQL injection"]})
        assert result.has_critical_issues() is True

    def test_has_critical_issues_false(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=1, owner="o", repo="r")
        result.add_file_review("a.py", {"score": 80, "critical_issues": []})
        assert result.has_critical_issues() is False

    def test_has_security_concerns(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=1, owner="o", repo="r")
        result.add_file_review("a.py", {"score": 60, "security_concerns": ["Hardcoded secret"]})
        assert result.has_security_concerns() is True

    def test_has_no_security_concerns(self):
        from src.github_integration import PRReviewResult

        result = PRReviewResult(pr_number=1, owner="o", repo="r")
        result.add_file_review("a.py", {"score": 80, "security_concerns": []})
        assert result.has_security_concerns() is False


class TestGitHubIntegration:
    """Tests for GitHubIntegration class."""

    def test_verify_webhook_no_secret(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok123", webhook_secret=None)
        assert gh.verify_webhook_signature(b"payload", "sha256=abc") is True

    def test_verify_webhook_invalid_signature(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok123", webhook_secret="mysecret")
        assert gh.verify_webhook_signature(b"payload", "invalid") is False

    def test_verify_webhook_missing_prefix(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok123", webhook_secret="mysecret")
        assert gh.verify_webhook_signature(b"payload", "md5=abc") is False

    def test_verify_webhook_empty_signature(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok123", webhook_secret="mysecret")
        assert gh.verify_webhook_signature(b"payload", "") is False

    def test_format_review_comment_high_score(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok")
        comment = gh.format_review_comment({"score": 85, "summary": "Good code"})
        assert "85/100" in comment
        assert "Good" in comment

    def test_format_review_comment_low_score(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok")
        comment = gh.format_review_comment(
            {
                "score": 40,
                "summary": "Needs work",
                "critical_issues": ["Bug found"],
                "security_concerns": ["XSS vulnerability"],
                "agricultural_issues": ["NDVI out of range"],
                "suggestions": ["Add tests"],
            }
        )
        assert "40/100" in comment
        assert "Bug found" in comment
        assert "XSS vulnerability" in comment
        assert "NDVI out of range" in comment

    def test_format_review_comment_with_file_path(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok")
        comment = gh.format_review_comment({"score": 70, "summary": "OK"}, file_path="src/main.py")
        assert "src/main.py" in comment

    def test_format_pr_summary_empty(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok")
        summary = gh.format_pr_summary([])
        assert "No files were reviewed" in summary

    def test_format_pr_summary_multiple_files(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok")
        reviews = [
            {
                "file": "a.py",
                "score": 90,
                "summary": "Great",
                "critical_issues": [],
                "security_concerns": [],
                "agricultural_issues": [],
            },
            {
                "file": "b.py",
                "score": 40,
                "summary": "Bad",
                "critical_issues": ["Bug"],
                "security_concerns": ["XSS"],
                "agricultural_issues": ["NDVI"],
            },
        ]
        summary = gh.format_pr_summary(reviews)
        assert "65/100" in summary  # (90+40)//2
        assert "a.py" in summary
        assert "b.py" in summary
        assert "Bug" in summary
        assert "XSS" in summary
        assert "NDVI" in summary

    def test_api_url_trailing_slash_stripped(self):
        from src.github_integration import GitHubIntegration

        gh = GitHubIntegration(token="tok", api_url="https://api.github.com/")
        assert gh.api_url == "https://api.github.com"


# ═══════════════════════════════════════════════════════════════════════════════
# Main Service Logic Tests - _parse_response and _create_review_prompt
# These test the methods directly on a manually-constructed service instance
# to avoid import issues from src.main (which has heavy dependencies).
# ═══════════════════════════════════════════════════════════════════════════════
class TestParseResponse:
    """Tests for CodeReviewService._parse_response logic (inline reimplementation)."""

    def _parse_response(self, response_text: str) -> dict:
        """Mirror of CodeReviewService._parse_response for unit testing."""
        try:
            if "```json" in response_text:
                start = response_text.find("```json") + 7
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()
            elif "```" in response_text:
                start = response_text.find("```") + 3
                end = response_text.find("```", start)
                response_text = response_text[start:end].strip()

            result = json.loads(response_text)
            result.setdefault("summary", "No summary provided")
            result.setdefault("critical_issues", [])
            result.setdefault("suggestions", [])
            result.setdefault("security_concerns", [])
            result.setdefault("agricultural_issues", [])
            result.setdefault("score", 75)
            return result
        except json.JSONDecodeError:
            return {
                "summary": response_text[:500] if response_text else "No response",
                "critical_issues": [],
                "suggestions": [],
                "security_concerns": [],
                "agricultural_issues": [],
                "score": 75,
            }

    def test_parse_valid_json(self):
        result = self._parse_response('{"summary": "Good", "score": 85}')
        assert result["summary"] == "Good"
        assert result["score"] == 85

    def test_parse_json_in_code_block(self):
        text = '```json\n{"summary": "OK", "score": 70}\n```'
        result = self._parse_response(text)
        assert result["summary"] == "OK"
        assert result["score"] == 70

    def test_parse_json_in_generic_code_block(self):
        text = '```\n{"summary": "Test", "score": 60}\n```'
        result = self._parse_response(text)
        assert result["summary"] == "Test"

    def test_parse_invalid_json_fallback(self):
        result = self._parse_response("This is not JSON at all")
        assert result["summary"] == "This is not JSON at all"
        assert result["score"] == 75

    def test_parse_empty_response(self):
        result = self._parse_response("")
        assert result["summary"] == "No response"
        assert result["score"] == 75

    def test_parse_defaults_filled(self):
        result = self._parse_response('{"summary": "Hello"}')
        assert result["critical_issues"] == []
        assert result["suggestions"] == []
        assert result["security_concerns"] == []
        assert result["agricultural_issues"] == []
        assert result["score"] == 75


class TestCreateReviewPromptLogic:
    """Tests for review prompt generation logic."""

    def _create_prompt(self, file_path, content, language=None):
        """Simplified version of the prompt creation logic."""
        file_ext = Path(file_path).suffix
        if language:
            file_type = language.capitalize()
        else:
            file_type = {
                ".py": "Python",
                ".ts": "TypeScript",
                ".tsx": "TypeScript React",
                ".js": "JavaScript",
                ".jsx": "JavaScript React",
                ".yml": "YAML",
                ".yaml": "YAML",
                ".json": "JSON",
                ".md": "Markdown",
                ".sh": "Bash",
                ".dockerfile": "Dockerfile",
                ".tf": "Terraform",
                ".go": "Go",
                ".rs": "Rust",
            }.get(file_ext, "Code")
        return f"Review {file_type} file: {file_path}\n{content[:5000]}"

    def test_prompt_with_language(self):
        prompt = self._create_prompt("test.py", "x=1", language="python")
        assert "Python" in prompt

    def test_prompt_without_language_uses_extension(self):
        prompt = self._create_prompt("app.ts", "const x = 1;")
        assert "TypeScript" in prompt

    def test_prompt_unknown_extension(self):
        prompt = self._create_prompt("file.xyz", "content")
        assert "Code" in prompt

    def test_prompt_truncates_code(self):
        long_code = "x = 1\n" * 10000
        prompt = self._create_prompt("big.py", long_code)
        assert len(prompt) < len(long_code)


# ═══════════════════════════════════════════════════════════════════════════════
# Redis Cache Tests (mock-based - no real Redis needed)
# ═══════════════════════════════════════════════════════════════════════════════
class TestRedisCacheKeyPrefixing:
    """Test RedisCache key prefixing logic."""

    def test_make_key(self):
        from src.cache import RedisCache

        cache = RedisCache(redis_url="redis://localhost:6379", prefix="review:")
        assert cache._make_key("abc") == "review:abc"

    def test_custom_prefix(self):
        from src.cache import RedisCache

        cache = RedisCache(redis_url="redis://localhost:6379", prefix="test_prefix:")
        assert cache._make_key("key") == "test_prefix:key"


# ═══════════════════════════════════════════════════════════════════════════════
# Settings Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestSettings:
    """Tests for Settings config class."""

    def test_get_fallback_models_list(self):
        from config.settings import Settings

        with patch.dict(os.environ, {}, clear=False):
            settings = Settings(fallback_models="model1@http://host1,model2@http://host2,model3")
            models = settings.get_fallback_models_list()
            assert len(models) == 3
            assert models[0] == ("model1", "http://host1")
            assert models[1] == ("model2", "http://host2")
            assert models[2] == ("model3", settings.ollama_url)

    def test_get_agricultural_keywords_list(self):
        from config.settings import Settings

        with patch.dict(os.environ, {}, clear=False):
            settings = Settings(agricultural_keywords="ndvi,lai,irrigation")
            keywords = settings.get_agricultural_keywords_list()
            assert keywords == ["ndvi", "lai", "irrigation"]

    def test_get_fallback_models_empty(self):
        from config.settings import Settings

        with patch.dict(os.environ, {}, clear=False):
            settings = Settings(fallback_models="")
            models = settings.get_fallback_models_list()
            assert models == []

    def test_default_settings(self):
        from config.settings import Settings

        with patch.dict(os.environ, {}, clear=False):
            settings = Settings()
            assert settings.ollama_model == "deepseek-coder-v2"
            assert settings.enable_cache is True
            assert settings.cache_backend == "memory"
            assert settings.enable_agricultural_rules is True
            assert settings.max_retries == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
