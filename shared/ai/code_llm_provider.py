"""
Code-Specialized LLM Provider
=============================
مزود نماذج اللغة المتخصص بالكود

Specialized LLM provider for code-related tasks:
- Code completion and generation
- Code review and analysis
- Bug fixing suggestions
- Test generation
- Documentation generation
- Refactoring suggestions

Extends the base LLMProviderManager with code-specific features.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

from .llm_provider import (
    LLMProvider,
    LLMProviderManager,
)
from .validation import escape_prompt_input

logger = structlog.get_logger(__name__)


class CodeTaskType(StrEnum):
    """Types of code-related tasks."""

    COMPLETION = "completion"
    REVIEW = "review"
    FIX = "fix"
    TEST_GENERATION = "test_generation"
    DOCUMENTATION = "documentation"
    REFACTOR = "refactor"
    EXPLAIN = "explain"
    TRANSLATE = "translate"


@dataclass
class CodeContext:
    """Context for code operations."""

    file_path: str | None = None
    language: str | None = None
    code: str | None = None
    cursor_position: int | None = None
    prefix: str | None = None
    suffix: str | None = None
    error_message: str | None = None
    related_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_path": self.file_path,
            "language": self.language,
            "code": self.code,
            "cursor_position": self.cursor_position,
            "prefix": self.prefix,
            "suffix": self.suffix,
            "error_message": self.error_message,
            "related_files": self.related_files,
        }


@dataclass
class CodeCompletionResult:
    """Result of code completion."""

    completions: list[str]
    language: str
    confidence: list[float]
    provider: LLMProvider
    model: str
    latency_ms: float
    tokens_used: int


@dataclass
class CodeReviewResult:
    """Result of code review."""

    issues: list[dict[str, Any]]
    suggestions: list[dict[str, Any]]
    security_concerns: list[dict[str, Any]]
    performance_notes: list[str]
    overall_score: float  # 0-10
    summary: str
    summary_ar: str  # Arabic summary
    provider: LLMProvider
    model: str
    latency_ms: float


@dataclass
class CodeFixResult:
    """Result of code fix suggestion."""

    original_code: str
    fixed_code: str
    changes: list[dict[str, Any]]
    explanation: str
    explanation_ar: str  # Arabic explanation
    confidence: float
    provider: LLMProvider
    model: str
    latency_ms: float


class CodeLLMProvider:
    """
    Code-specialized LLM Provider.

    مزود نماذج اللغة المتخصص بالكود

    Provides code-specific operations on top of the base LLM provider.

    Features:
        - Code completion with multi-line support
        - Code review with security analysis
        - Bug fix suggestions with explanations
        - Test generation for Python, TypeScript, Dart
        - Documentation generation (docstrings, README)
        - Code refactoring suggestions

    Example:
        provider = CodeLLMProvider()

        # Code completion
        result = await provider.complete_code(
            prefix="def calculate_area(",
            language="python"
        )

        # Code review
        review = await provider.review_code(
            code="def foo(): pass",
            language="python"
        )

        # Fix code
        fix = await provider.fix_code(
            code="x = 1 / 0",
            error_message="ZeroDivisionError"
        )
    """

    # Model recommendations by task
    RECOMMENDED_MODELS = {
        CodeTaskType.COMPLETION: {
            LLMProvider.OLLAMA: "codellama:7b",
            LLMProvider.DEEPSEEK: "deepseek-coder",
            LLMProvider.OPENAI: "gpt-4o",
            LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
        },
        CodeTaskType.REVIEW: {
            LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
            LLMProvider.OPENAI: "gpt-4o",
            LLMProvider.DEEPSEEK: "deepseek-coder",
        },
        CodeTaskType.FIX: {
            LLMProvider.DEEPSEEK: "deepseek-coder",
            LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
            LLMProvider.OLLAMA: "codellama:13b",
        },
    }

    # System prompts by task
    SYSTEM_PROMPTS = {
        CodeTaskType.COMPLETION: """You are an expert code completion assistant. Complete the code based on the context provided.
Rules:
- Return ONLY the completion, no explanations
- Match the coding style of the existing code
- Use proper indentation
- Follow language conventions
أنت مساعد ذكي لإكمال الكود. أكمل الكود بناءً على السياق المقدم.""",
        CodeTaskType.REVIEW: """You are an expert code reviewer. Analyze the code for:
1. Bugs and potential issues
2. Security vulnerabilities (OWASP Top 10)
3. Performance concerns
4. Code style and best practices
5. Maintainability and readability

Return your analysis in JSON format with:
- issues: list of {severity, line, message, suggestion}
- suggestions: list of {type, description}
- security_concerns: list of {cwe_id, description, severity}
- performance_notes: list of strings
- overall_score: number 0-10
- summary: brief summary in English
- summary_ar: brief summary in Arabic

أنت مراجع كود خبير. حلل الكود بحثاً عن الأخطاء والثغرات الأمنية.""",
        CodeTaskType.FIX: """You are an expert debugging assistant. Fix the code based on the error provided.
Return your fix in JSON format with:
- fixed_code: the corrected code
- changes: list of {line, original, replacement, reason}
- explanation: detailed explanation in English
- explanation_ar: detailed explanation in Arabic
- confidence: your confidence level (0-1)

أنت مساعد تصحيح أخطاء خبير. أصلح الكود بناءً على الخطأ المقدم.""",
        CodeTaskType.TEST_GENERATION: """You are an expert test writer. Generate comprehensive tests for the provided code.
Include:
- Unit tests for each function/method
- Edge cases and error handling tests
- Integration tests where applicable
- Use pytest for Python, Jest/Vitest for TypeScript, flutter_test for Dart

أنت كاتب اختبارات خبير. قم بإنشاء اختبارات شاملة للكود المقدم.""",
        CodeTaskType.DOCUMENTATION: """You are an expert technical writer. Generate documentation for the code.
Include:
- Module/class docstrings
- Function documentation with parameters and returns
- Usage examples
- Note any important caveats
- Support both English and Arabic where appropriate

أنت كاتب تقني خبير. قم بإنشاء توثيق للكود.""",
        CodeTaskType.REFACTOR: """You are an expert code refactoring assistant. Suggest improvements for:
1. Code organization and structure
2. Naming conventions
3. Design patterns
4. Reducing complexity
5. Improving testability

Return suggestions in JSON format with:
- refactorings: list of {type, location, before, after, reason}
- overall_assessment: summary of code quality
- priority_order: ordered list of most important changes

أنت مساعد إعادة هيكلة كود خبير. اقترح تحسينات للكود.""",
        CodeTaskType.EXPLAIN: """You are an expert code explainer. Explain the code clearly for:
- What it does
- How it works
- Why it's implemented this way
- Any important patterns or techniques used

Provide explanations in both English and Arabic.

أنت شارح كود خبير. اشرح الكود بوضوح.""",
    }

    def __init__(
        self,
        llm_manager: LLMProviderManager | None = None,
        tenant_id: str = "sahool",
        enable_streaming: bool = True,
    ):
        """
        Initialize CodeLLMProvider.

        Args:
            llm_manager: Base LLM manager (auto-created if None)
            tenant_id: Tenant ID for audit logging
            enable_streaming: Enable streaming responses
        """
        self.tenant_id = tenant_id
        self.enable_streaming = enable_streaming

        self._manager = llm_manager or LLMProviderManager(tenant_id=tenant_id)

    @property
    def available_providers(self) -> list[LLMProvider]:
        """Get available providers."""
        return self._manager.available_providers

    async def complete_code(
        self,
        prefix: str,
        suffix: str = "",
        language: str = "python",
        num_completions: int = 1,
        max_tokens: int = 256,
        preferred_provider: LLMProvider | None = None,
    ) -> CodeCompletionResult:
        """
        Generate code completions.

        توليد إكمالات الكود

        Args:
            prefix: Code before cursor
            suffix: Code after cursor (for fill-in-the-middle)
            language: Programming language
            num_completions: Number of completions to generate
            max_tokens: Maximum tokens per completion
            preferred_provider: Preferred provider

        Returns:
            CodeCompletionResult with completions
        """
        start_time = datetime.now(UTC)

        safe_prefix = escape_prompt_input(prefix)
        safe_suffix = escape_prompt_input(suffix)

        prompt = f"""Complete the following {language} code:

```{language}
{safe_prefix}<CURSOR>{safe_suffix}
```

Provide {num_completions} completion(s). Return ONLY the code to insert at <CURSOR>."""

        response = await self._manager.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPTS[CodeTaskType.COMPLETION],
            max_tokens=max_tokens,
            temperature=0.3,  # Lower for more deterministic completions
            preferred_provider=preferred_provider or LLMProvider.OLLAMA,
        )

        # Parse completions
        completions = self._parse_completions(response.text, num_completions)

        latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        return CodeCompletionResult(
            completions=completions,
            language=language,
            confidence=[0.8] * len(completions),  # Default confidence
            provider=response.provider,
            model=response.model,
            latency_ms=latency_ms,
            tokens_used=response.tokens_input + response.tokens_output,
        )

    async def review_code(
        self,
        code: str,
        language: str = "python",
        file_path: str | None = None,
        check_security: bool = True,
        check_performance: bool = True,
        preferred_provider: LLMProvider | None = None,
    ) -> CodeReviewResult:
        """
        Review code for issues and suggestions.

        مراجعة الكود للمشاكل والاقتراحات

        Args:
            code: Code to review
            language: Programming language
            file_path: Optional file path for context
            check_security: Include security analysis
            check_performance: Include performance analysis
            preferred_provider: Preferred provider

        Returns:
            CodeReviewResult with issues and suggestions
        """
        start_time = datetime.now(UTC)

        safe_code = escape_prompt_input(code)
        context = f"File: {escape_prompt_input(file_path)}\n" if file_path else ""

        prompt = f"""{context}Review the following {language} code:

```{language}
{safe_code}
```

{"Include security vulnerability analysis (OWASP Top 10, CWE)." if check_security else ""}
{"Include performance analysis." if check_performance else ""}

Return your analysis as JSON."""

        response = await self._manager.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPTS[CodeTaskType.REVIEW],
            max_tokens=2048,
            temperature=0.2,
            preferred_provider=preferred_provider or LLMProvider.ANTHROPIC,
        )

        # Parse review result
        review_data = self._parse_json_response(response.text)

        latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        return CodeReviewResult(
            issues=review_data.get("issues", []),
            suggestions=review_data.get("suggestions", []),
            security_concerns=review_data.get("security_concerns", []),
            performance_notes=review_data.get("performance_notes", []),
            overall_score=review_data.get("overall_score", 5.0),
            summary=review_data.get("summary", ""),
            summary_ar=review_data.get("summary_ar", ""),
            provider=response.provider,
            model=response.model,
            latency_ms=latency_ms,
        )

    async def fix_code(
        self,
        code: str,
        error_message: str | None = None,
        language: str = "python",
        file_path: str | None = None,
        preferred_provider: LLMProvider | None = None,
    ) -> CodeFixResult:
        """
        Suggest fixes for code issues.

        اقتراح إصلاحات لمشاكل الكود

        Args:
            code: Code with issues
            error_message: Error message (if any)
            language: Programming language
            file_path: Optional file path for context
            preferred_provider: Preferred provider

        Returns:
            CodeFixResult with fix suggestions
        """
        start_time = datetime.now(UTC)

        safe_code = escape_prompt_input(code)
        context = f"File: {escape_prompt_input(file_path)}\n" if file_path else ""
        error_context = f"\nError: {escape_prompt_input(error_message)}" if error_message else ""

        prompt = f"""{context}Fix the following {language} code:{error_context}

```{language}
{safe_code}
```

Return your fix as JSON with fixed_code, changes, explanation, explanation_ar, and confidence."""

        response = await self._manager.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPTS[CodeTaskType.FIX],
            max_tokens=2048,
            temperature=0.1,  # Very low for consistent fixes
            preferred_provider=preferred_provider or LLMProvider.DEEPSEEK,
        )

        # Parse fix result
        fix_data = self._parse_json_response(response.text)

        latency_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000

        return CodeFixResult(
            original_code=code,
            fixed_code=fix_data.get("fixed_code", code),
            changes=fix_data.get("changes", []),
            explanation=fix_data.get("explanation", ""),
            explanation_ar=fix_data.get("explanation_ar", ""),
            confidence=fix_data.get("confidence", 0.5),
            provider=response.provider,
            model=response.model,
            latency_ms=latency_ms,
        )

    async def generate_tests(
        self,
        code: str,
        language: str = "python",
        file_path: str | None = None,
        test_framework: str | None = None,
        preferred_provider: LLMProvider | None = None,
    ) -> str:
        """
        Generate tests for code.

        توليد اختبارات للكود

        Args:
            code: Code to generate tests for
            language: Programming language
            file_path: Optional file path
            test_framework: Test framework (auto-detected if None)
            preferred_provider: Preferred provider

        Returns:
            Generated test code
        """
        # Auto-detect test framework
        if test_framework is None:
            test_framework = self._detect_test_framework(language)

        safe_code = escape_prompt_input(code)
        context = f"File: {escape_prompt_input(file_path)}\n" if file_path else ""

        prompt = f"""{context}Generate comprehensive {test_framework} tests for the following {language} code:

```{language}
{safe_code}
```

Include:
1. Unit tests for each function/method
2. Edge cases
3. Error handling tests
4. Type validation (if applicable)

Return ONLY the test code."""

        response = await self._manager.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPTS[CodeTaskType.TEST_GENERATION],
            max_tokens=4096,
            temperature=0.3,
            preferred_provider=preferred_provider or LLMProvider.ANTHROPIC,
        )

        return self._extract_code_block(response.text, language)

    async def generate_documentation(
        self,
        code: str,
        language: str = "python",
        doc_style: str = "google",
        include_arabic: bool = True,
        preferred_provider: LLMProvider | None = None,
    ) -> str:
        """
        Generate documentation for code.

        توليد توثيق للكود

        Args:
            code: Code to document
            language: Programming language
            doc_style: Documentation style (google, numpy, sphinx)
            include_arabic: Include Arabic translations
            preferred_provider: Preferred provider

        Returns:
            Documented code
        """
        arabic_instruction = (
            """
Include Arabic translations in docstrings where appropriate:
- Module docstring: Include Arabic description
- Function docstrings: Include Arabic brief
"""
            if include_arabic
            else ""
        )

        safe_code = escape_prompt_input(code)

        prompt = f"""Add comprehensive {doc_style}-style documentation to the following {language} code:

```{language}
{safe_code}
```

{arabic_instruction}

Return the fully documented code."""

        response = await self._manager.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPTS[CodeTaskType.DOCUMENTATION],
            max_tokens=4096,
            temperature=0.3,
            preferred_provider=preferred_provider or LLMProvider.ANTHROPIC,
        )

        return self._extract_code_block(response.text, language)

    async def explain_code(
        self,
        code: str,
        language: str = "python",
        detail_level: str = "medium",
        preferred_provider: LLMProvider | None = None,
    ) -> dict[str, str]:
        """
        Explain code in detail.

        شرح الكود بالتفصيل

        Args:
            code: Code to explain
            language: Programming language
            detail_level: Level of detail (brief, medium, detailed)
            preferred_provider: Preferred provider

        Returns:
            Dictionary with English and Arabic explanations
        """
        safe_code = escape_prompt_input(code)

        prompt = f"""Explain the following {language} code at a {detail_level} level of detail:

```{language}
{safe_code}
```

Provide explanations in both English and Arabic.

Format your response as:
## English Explanation
[Your English explanation]

## الشرح بالعربية
[Your Arabic explanation]"""

        response = await self._manager.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPTS[CodeTaskType.EXPLAIN],
            max_tokens=2048,
            temperature=0.4,
            preferred_provider=preferred_provider or LLMProvider.ANTHROPIC,
        )

        # Parse explanations
        text = response.text
        english = ""
        arabic = ""

        # Extract English explanation
        en_match = re.search(r"## English Explanation\s*\n(.*?)(?=##|$)", text, re.DOTALL)
        if en_match:
            english = en_match.group(1).strip()

        # Extract Arabic explanation
        ar_match = re.search(r"## الشرح بالعربية\s*\n(.*?)(?=##|$)", text, re.DOTALL)
        if ar_match:
            arabic = ar_match.group(1).strip()

        return {
            "english": english or text,
            "arabic": arabic,
            "provider": response.provider.value,
            "model": response.model,
        }

    async def suggest_refactoring(
        self,
        code: str,
        language: str = "python",
        focus_areas: list[str] | None = None,
        preferred_provider: LLMProvider | None = None,
    ) -> dict[str, Any]:
        """
        Suggest code refactoring improvements.

        اقتراح تحسينات إعادة هيكلة الكود

        Args:
            code: Code to refactor
            language: Programming language
            focus_areas: Specific areas to focus on
            preferred_provider: Preferred provider

        Returns:
            Dictionary with refactoring suggestions
        """
        focus = ""
        if focus_areas:
            safe_areas = [escape_prompt_input(a) for a in focus_areas]
            focus = f"\nFocus on: {', '.join(safe_areas)}"

        safe_code = escape_prompt_input(code)

        prompt = f"""Analyze and suggest refactoring for the following {language} code:{focus}

```{language}
{safe_code}
```

Return your suggestions as JSON with:
- refactorings: list of {{type, location, before, after, reason, reason_ar}}
- overall_assessment: summary in English
- overall_assessment_ar: summary in Arabic
- priority_order: list of most important changes first"""

        response = await self._manager.generate(
            prompt=prompt,
            system_prompt=self.SYSTEM_PROMPTS[CodeTaskType.REFACTOR],
            max_tokens=3072,
            temperature=0.3,
            preferred_provider=preferred_provider or LLMProvider.ANTHROPIC,
        )

        result = self._parse_json_response(response.text)
        result["provider"] = response.provider.value
        result["model"] = response.model

        return result

    def _parse_completions(self, text: str, num_completions: int) -> list[str]:
        """Parse completions from response."""
        # Try to extract code blocks
        code_blocks = re.findall(r"```[\w]*\n?(.*?)```", text, re.DOTALL)
        if code_blocks:
            return code_blocks[:num_completions]

        # If no code blocks, use the raw text
        completions = text.strip().split("\n\n")
        return completions[:num_completions] if completions else [text.strip()]

    def _parse_json_response(self, text: str) -> dict[str, Any]:
        """Parse JSON from response text."""
        # Try to find JSON in the response
        json_match = re.search(r"```json\s*\n?(.*?)```", text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try to parse the entire response as JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try to find any JSON object in the text
        json_obj_match = re.search(r"\{.*\}", text, re.DOTALL)
        if json_obj_match:
            try:
                return json.loads(json_obj_match.group(0))
            except json.JSONDecodeError:
                pass

        # Return empty dict if no JSON found
        logger.warning("Could not parse JSON from response", text=text[:200])
        return {}

    def _extract_code_block(self, text: str, language: str) -> str:
        """Extract code block from response."""
        # Try to find code block with language
        pattern = rf"```{language}\s*\n?(.*?)```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # Try generic code block
        match = re.search(r"```[\w]*\s*\n?(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Return raw text
        return text.strip()

    def _detect_test_framework(self, language: str) -> str:
        """Detect appropriate test framework for language."""
        frameworks = {
            "python": "pytest",
            "typescript": "vitest",
            "javascript": "jest",
            "dart": "flutter_test",
            "go": "testing",
            "rust": "cargo test",
            "java": "junit",
        }
        return frameworks.get(language.lower(), "unittest")

    async def close(self) -> None:
        """Close the provider."""
        await self._manager.close()


# Global code provider instance
_global_code_provider: CodeLLMProvider | None = None


def get_code_llm_provider(tenant_id: str = "sahool") -> CodeLLMProvider:
    """
    Get or create the global Code LLM provider.

    الحصول على أو إنشاء مزود Code LLM العالمي
    """
    global _global_code_provider
    if _global_code_provider is None:
        _global_code_provider = CodeLLMProvider(tenant_id=tenant_id)
    return _global_code_provider
