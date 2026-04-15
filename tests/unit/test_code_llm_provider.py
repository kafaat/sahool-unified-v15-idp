"""
Code LLM Provider Test Suite
=============================
مجموعة اختبارات مزود نماذج اللغة للكود

Tests for:
- Code completion
- Code review
- Code fix suggestions
- Test generation
- Documentation generation

Author: SAHOOL Platform Team
Updated: January 2026
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Test markers
pytestmark = [pytest.mark.unit, pytest.mark.llm]


class TestCodeTaskType:
    """Test CodeTaskType enum."""

    def test_task_types_exist(self):
        """Test all task types are defined."""
        from shared.ai.code_llm_provider import CodeTaskType

        assert CodeTaskType.COMPLETION.value == "completion"
        assert CodeTaskType.REVIEW.value == "review"
        assert CodeTaskType.FIX.value == "fix"
        assert CodeTaskType.TEST_GENERATION.value == "test_generation"
        assert CodeTaskType.DOCUMENTATION.value == "documentation"
        assert CodeTaskType.REFACTOR.value == "refactor"
        assert CodeTaskType.EXPLAIN.value == "explain"


class TestCodeContext:
    """Test CodeContext data class."""

    def test_code_context_creation(self):
        """Test CodeContext creation."""
        from shared.ai.code_llm_provider import CodeContext

        context = CodeContext(
            file_path="/src/main.py",
            language="python",
            code="def hello(): pass",
        )

        assert context.file_path == "/src/main.py"
        assert context.language == "python"
        assert context.code == "def hello(): pass"

    def test_code_context_to_dict(self):
        """Test CodeContext to_dict method."""
        from shared.ai.code_llm_provider import CodeContext

        context = CodeContext(
            file_path="/src/main.py",
            language="python",
            code="def hello(): pass",
            cursor_position=10,
        )

        data = context.to_dict()
        assert data["file_path"] == "/src/main.py"
        assert data["language"] == "python"
        assert data["cursor_position"] == 10


class TestCodeCompletionResult:
    """Test CodeCompletionResult data class."""

    def test_completion_result_creation(self):
        """Test CodeCompletionResult creation."""
        from shared.ai.code_llm_provider import CodeCompletionResult
        from shared.ai.llm_provider import LLMProvider

        result = CodeCompletionResult(
            completions=["completion1", "completion2"],
            language="python",
            confidence=[0.9, 0.7],
            provider=LLMProvider.OLLAMA,
            model="codellama:7b",
            latency_ms=150.0,
            tokens_used=100,
        )

        assert len(result.completions) == 2
        assert result.language == "python"
        assert result.latency_ms == 150.0


class TestCodeReviewResult:
    """Test CodeReviewResult data class."""

    def test_review_result_creation(self):
        """Test CodeReviewResult creation."""
        from shared.ai.code_llm_provider import CodeReviewResult
        from shared.ai.llm_provider import LLMProvider

        result = CodeReviewResult(
            issues=[{"severity": "high", "message": "Bug found"}],
            suggestions=[{"type": "improvement", "description": "Use list comprehension"}],
            security_concerns=[],
            performance_notes=["Consider caching"],
            overall_score=7.5,
            summary="Good code with minor issues",
            summary_ar="كود جيد مع بعض المشاكل البسيطة",
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-sonnet",
            latency_ms=500.0,
        )

        assert len(result.issues) == 1
        assert result.overall_score == 7.5
        assert result.summary_ar is not None


class TestCodeFixResult:
    """Test CodeFixResult data class."""

    def test_fix_result_creation(self):
        """Test CodeFixResult creation."""
        from shared.ai.code_llm_provider import CodeFixResult
        from shared.ai.llm_provider import LLMProvider

        result = CodeFixResult(
            original_code="x = 1 / 0",
            fixed_code="x = 1 / max(divisor, 1)",
            changes=[{"line": 1, "original": "1 / 0", "replacement": "1 / max(divisor, 1)"}],
            explanation="Added guard against division by zero",
            explanation_ar="تمت إضافة حماية ضد القسمة على صفر",
            confidence=0.95,
            provider=LLMProvider.DEEPSEEK,
            model="deepseek-coder",
            latency_ms=200.0,
        )

        assert result.original_code != result.fixed_code
        assert result.confidence == 0.95
        assert len(result.changes) == 1


class TestCodeLLMProvider:
    """Test CodeLLMProvider functionality."""

    def test_provider_initialization(self):
        """Test provider initializes correctly."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()
        assert provider is not None

    def test_provider_with_custom_tenant(self):
        """Test provider with custom tenant ID."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider(tenant_id="custom-tenant")
        assert provider.tenant_id == "custom-tenant"

    def test_recommended_models_defined(self):
        """Test recommended models are defined."""
        from shared.ai.code_llm_provider import CodeLLMProvider, CodeTaskType
        from shared.ai.llm_provider import LLMProvider

        assert CodeTaskType.COMPLETION in CodeLLMProvider.RECOMMENDED_MODELS
        assert CodeTaskType.REVIEW in CodeLLMProvider.RECOMMENDED_MODELS
        assert CodeTaskType.FIX in CodeLLMProvider.RECOMMENDED_MODELS

    def test_system_prompts_defined(self):
        """Test system prompts are defined for all task types."""
        from shared.ai.code_llm_provider import CodeLLMProvider, CodeTaskType

        for task_type in [
            CodeTaskType.COMPLETION,
            CodeTaskType.REVIEW,
            CodeTaskType.FIX,
            CodeTaskType.TEST_GENERATION,
            CodeTaskType.DOCUMENTATION,
            CodeTaskType.REFACTOR,
            CodeTaskType.EXPLAIN,
        ]:
            assert task_type in CodeLLMProvider.SYSTEM_PROMPTS
            assert len(CodeLLMProvider.SYSTEM_PROMPTS[task_type]) > 0

    def test_detect_test_framework_python(self):
        """Test test framework detection for Python."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()
        framework = provider._detect_test_framework("python")
        assert framework == "pytest"

    def test_detect_test_framework_typescript(self):
        """Test test framework detection for TypeScript."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()
        framework = provider._detect_test_framework("typescript")
        assert framework == "vitest"

    def test_detect_test_framework_dart(self):
        """Test test framework detection for Dart."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()
        framework = provider._detect_test_framework("dart")
        assert framework == "flutter_test"

    def test_parse_completions_code_block(self):
        """Test parsing completions from code blocks."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()

        text = """Here is the completion:
```python
print("Hello")
```"""

        completions = provider._parse_completions(text, 1)
        assert len(completions) >= 1

    def test_parse_json_response_code_block(self):
        """Test parsing JSON from code block."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()

        text = """Here is the analysis:
```json
{"issues": [], "overall_score": 8.5}
```"""

        data = provider._parse_json_response(text)
        assert data.get("overall_score") == 8.5

    def test_parse_json_response_raw(self):
        """Test parsing raw JSON response."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()

        text = '{"issues": [], "overall_score": 7.0}'

        data = provider._parse_json_response(text)
        assert data.get("overall_score") == 7.0

    def test_parse_json_response_invalid(self):
        """Test parsing invalid JSON returns empty dict."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()

        text = "This is not JSON"

        data = provider._parse_json_response(text)
        assert data == {}

    def test_extract_code_block_with_language(self):
        """Test extracting code block with language tag."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()

        text = """Here is the code:
```python
def hello():
    print("Hello")
```"""

        code = provider._extract_code_block(text, "python")
        assert "def hello():" in code

    def test_extract_code_block_generic(self):
        """Test extracting generic code block."""
        from shared.ai.code_llm_provider import CodeLLMProvider

        provider = CodeLLMProvider()

        text = """Here is the code:
```
def hello():
    pass
```"""

        code = provider._extract_code_block(text, "python")
        assert "def hello():" in code


class TestCodeLLMProviderAsync:
    """Test async methods of CodeLLMProvider."""

    @pytest.mark.asyncio
    async def test_complete_code(self):
        """Test code completion."""
        from shared.ai.code_llm_provider import CodeLLMProvider
        from shared.ai.llm_provider import LLMProvider, LLMResponse

        provider = CodeLLMProvider()

        # Mock the LLM manager
        mock_response = LLMResponse(
            text="): return x + y",
            provider=LLMProvider.OLLAMA,
            model="codellama:7b",
            tokens_input=50,
            tokens_output=10,
        )

        with patch.object(provider._manager, "generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_response

            result = await provider.complete_code(
                prefix="def add(x, y",
                language="python",
            )

            assert result is not None
            assert len(result.completions) >= 1

    @pytest.mark.asyncio
    async def test_review_code(self):
        """Test code review."""
        from shared.ai.code_llm_provider import CodeLLMProvider
        from shared.ai.llm_provider import LLMProvider, LLMResponse

        provider = CodeLLMProvider()

        # Mock response with JSON
        mock_response = LLMResponse(
            text='{"issues": [], "suggestions": [], "security_concerns": [], "performance_notes": [], "overall_score": 8.0, "summary": "Good code", "summary_ar": "كود جيد"}',
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-sonnet",
            tokens_input=100,
            tokens_output=50,
        )

        with patch.object(provider._manager, "generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_response

            result = await provider.review_code(
                code="def hello(): print('hello')",
                language="python",
            )

            assert result is not None
            assert result.overall_score == 8.0

    @pytest.mark.asyncio
    async def test_fix_code(self):
        """Test code fix."""
        from shared.ai.code_llm_provider import CodeLLMProvider
        from shared.ai.llm_provider import LLMProvider, LLMResponse

        provider = CodeLLMProvider()

        # Mock response with fix
        mock_response = LLMResponse(
            text='{"fixed_code": "x = 1", "changes": [], "explanation": "Fixed", "explanation_ar": "تم الإصلاح", "confidence": 0.9}',
            provider=LLMProvider.DEEPSEEK,
            model="deepseek-coder",
            tokens_input=100,
            tokens_output=50,
        )

        with patch.object(provider._manager, "generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_response

            result = await provider.fix_code(
                code="x = 1 / 0",
                error_message="ZeroDivisionError",
            )

            assert result is not None
            assert result.confidence == 0.9

    @pytest.mark.asyncio
    async def test_generate_tests(self):
        """Test test generation."""
        from shared.ai.code_llm_provider import CodeLLMProvider
        from shared.ai.llm_provider import LLMProvider, LLMResponse

        provider = CodeLLMProvider()

        mock_response = LLMResponse(
            text='```python\ndef test_hello():\n    assert hello() == "hello"\n```',
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-sonnet",
            tokens_input=100,
            tokens_output=50,
        )

        with patch.object(provider._manager, "generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_response

            result = await provider.generate_tests(
                code='def hello(): return "hello"',
                language="python",
            )

            assert "test_hello" in result

    @pytest.mark.asyncio
    async def test_explain_code(self):
        """Test code explanation."""
        from shared.ai.code_llm_provider import CodeLLMProvider
        from shared.ai.llm_provider import LLMProvider, LLMResponse

        provider = CodeLLMProvider()

        mock_response = LLMResponse(
            text="## English Explanation\nThis function prints hello.\n\n## الشرح بالعربية\nهذه الدالة تطبع مرحبا.",
            provider=LLMProvider.ANTHROPIC,
            model="claude-3-5-sonnet",
            tokens_input=100,
            tokens_output=50,
        )

        with patch.object(provider._manager, "generate", new_callable=AsyncMock) as mock_gen:
            mock_gen.return_value = mock_response

            result = await provider.explain_code(
                code='def hello(): print("hello")',
                language="python",
            )

            assert "english" in result
            assert "arabic" in result


class TestGetCodeLLMProvider:
    """Test get_code_llm_provider function."""

    def test_get_code_llm_provider(self):
        """Test getting global provider."""
        from shared.ai.code_llm_provider import get_code_llm_provider

        provider1 = get_code_llm_provider()
        provider2 = get_code_llm_provider()

        # Should return same instance
        assert provider1 is provider2


# Fixtures
@pytest.fixture
def mock_provider():
    """Create mock code LLM provider."""
    from shared.ai.code_llm_provider import CodeLLMProvider

    return CodeLLMProvider(tenant_id="test")
