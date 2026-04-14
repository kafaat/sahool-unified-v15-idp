"""
SAHOOL AI Tool Registry - سجل أدوات الذكاء الاصطناعي
====================================================

Dynamic tool registry for AI agents to discover, configure, and use quality tools.
نظام تسجيل ديناميكي للأدوات يتيح للوكلاء اكتشافها وتكوينها واستخدامها.

Features:
- Dynamic tool discovery and registration
- Project-level configuration support (.sahool-quality.yaml)
- Tool capability querying
- Performance metrics tracking
- Circuit breaker integration
- Parallel tool execution

Usage:
    from shared.ai.tool_registry import (
        ToolRegistry,
        get_tool_registry,
        QualityConfig,
        ToolCapability,
    )

    # Get global registry
    registry = get_tool_registry()

    # Get tools for a language
    python_tools = registry.get_tools_for_language("python")

    # Execute tools dynamically
    results = await registry.run_tools(
        file_path="src/main.py",
        tools=["ruff", "mypy", "bandit"]
    )
"""

from __future__ import annotations

import asyncio
import hashlib
import os
import shutil
import subprocess
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

import structlog
import yaml

logger = structlog.get_logger(__name__)


# =============================================================================
# Enums - التعدادات
# =============================================================================


class ToolCategory(StrEnum):
    """Tool category classification - تصنيف فئة الأداة"""

    LINTER = "linter"
    FORMATTER = "formatter"
    TYPE_CHECKER = "type_checker"
    SECURITY = "security"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    PERFORMANCE = "performance"


class ToolCapability(StrEnum):
    """Tool capabilities - قدرات الأداة"""

    AUTO_FIX = "auto_fix"
    INCREMENTAL = "incremental"
    PARALLEL = "parallel"
    CACHING = "caching"
    WATCH_MODE = "watch_mode"
    CONFIG_FILE = "config_file"
    CUSTOM_RULES = "custom_rules"
    JSON_OUTPUT = "json_output"
    SARIF_OUTPUT = "sarif_output"


class ToolStatus(StrEnum):
    """Tool availability status - حالة توفر الأداة"""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    DISABLED = "disabled"
    CIRCUIT_OPEN = "circuit_open"


class Language(StrEnum):
    """Supported languages - اللغات المدعومة"""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    DART = "dart"
    GO = "go"
    RUST = "rust"
    JAVA = "java"
    KOTLIN = "kotlin"


# =============================================================================
# Data Classes - فئات البيانات
# =============================================================================


@dataclass
class ToolInfo:
    """Information about a registered tool - معلومات عن أداة مسجلة"""

    id: str
    name: str
    name_ar: str
    category: ToolCategory
    languages: list[Language]
    command: str
    version_command: str
    capabilities: list[ToolCapability]
    default_args: list[str] = field(default_factory=list)
    config_file: str | None = None
    priority: int = 100  # Lower = higher priority
    timeout_seconds: int = 60
    description: str = ""
    description_ar: str = ""
    homepage: str = ""

    # Runtime state
    status: ToolStatus = ToolStatus.UNAVAILABLE
    version: str | None = None
    last_check: datetime | None = None


@dataclass
class ToolResult:
    """Result from running a tool - نتيجة تشغيل أداة"""

    tool_id: str
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    duration_ms: float
    issues_count: int = 0
    fixed_count: int = 0
    error_message: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class QualityConfig:
    """Project-level quality configuration - إعدادات الجودة على مستوى المشروع"""

    # Enabled tools per language
    python_tools: list[str] = field(default_factory=lambda: ["ruff", "mypy", "bandit"])
    typescript_tools: list[str] = field(default_factory=lambda: ["eslint", "tsc"])
    dart_tools: list[str] = field(default_factory=lambda: ["dart_analyze", "dart_format"])

    # Global settings
    fail_on_warning: bool = False
    auto_fix: bool = True
    parallel_execution: bool = True
    max_parallel_tools: int = 4
    cache_enabled: bool = True
    cache_ttl_seconds: int = 300

    # Tool-specific overrides
    tool_overrides: dict[str, dict[str, Any]] = field(default_factory=dict)

    # Excluded paths
    exclude_patterns: list[str] = field(
        default_factory=lambda: [
            "**/node_modules/**",
            "**/.git/**",
            "**/build/**",
            "**/dist/**",
            "**/*.g.dart",
            "**/*.freezed.dart",
        ]
    )

    @classmethod
    def from_yaml(cls, path: Path | str) -> QualityConfig:
        """Load configuration from YAML file - تحميل الإعدادات من ملف YAML"""
        path = Path(path)
        if not path.exists():
            return cls()

        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}

        return cls(
            python_tools=data.get("python", {}).get("tools", cls().python_tools),
            typescript_tools=data.get("typescript", {}).get("tools", cls().typescript_tools),
            dart_tools=data.get("dart", {}).get("tools", cls().dart_tools),
            fail_on_warning=data.get("fail_on_warning", False),
            auto_fix=data.get("auto_fix", True),
            parallel_execution=data.get("parallel", True),
            max_parallel_tools=data.get("max_parallel_tools", 4),
            cache_enabled=data.get("cache", {}).get("enabled", True),
            cache_ttl_seconds=data.get("cache", {}).get("ttl", 300),
            tool_overrides=data.get("tool_overrides", {}),
            exclude_patterns=data.get("exclude", cls().exclude_patterns),
        )


@dataclass
class ToolMetrics:
    """Performance metrics for a tool - مقاييس أداء الأداة"""

    tool_id: str
    total_runs: int = 0
    successful_runs: int = 0
    failed_runs: int = 0
    total_duration_ms: float = 0.0
    avg_duration_ms: float = 0.0
    issues_found: int = 0
    issues_fixed: int = 0
    last_run: datetime | None = None
    circuit_opens: int = 0


# =============================================================================
# Tool Registry - سجل الأدوات
# =============================================================================


class ToolRegistry:
    """
    Dynamic tool registry for AI agents.
    سجل أدوات ديناميكي لوكلاء الذكاء الاصطناعي.

    Features:
    - Automatic tool discovery
    - Configuration-based tool selection
    - Performance metrics tracking
    - Circuit breaker pattern
    - Parallel execution support
    """

    # Default tools configuration
    DEFAULT_TOOLS: list[ToolInfo] = [
        # Python Tools
        ToolInfo(
            id="ruff",
            name="Ruff",
            name_ar="راف",
            category=ToolCategory.LINTER,
            languages=[Language.PYTHON],
            command="ruff",
            version_command="ruff --version",
            capabilities=[
                ToolCapability.AUTO_FIX,
                ToolCapability.INCREMENTAL,
                ToolCapability.PARALLEL,
                ToolCapability.JSON_OUTPUT,
                ToolCapability.CONFIG_FILE,
            ],
            default_args=["check", "--output-format=json"],
            config_file="ruff.toml",
            priority=10,
            timeout_seconds=120,
            description="Fast Python linter and formatter",
            description_ar="أداة فحص وتنسيق Python سريعة",
            homepage="https://docs.astral.sh/ruff/",
        ),
        ToolInfo(
            id="mypy",
            name="Mypy",
            name_ar="مايبي",
            category=ToolCategory.TYPE_CHECKER,
            languages=[Language.PYTHON],
            command="mypy",
            version_command="mypy --version",
            capabilities=[
                ToolCapability.INCREMENTAL,
                ToolCapability.CACHING,
                ToolCapability.CONFIG_FILE,
            ],
            default_args=["--ignore-missing-imports", "--no-error-summary"],
            config_file="mypy.ini",
            priority=20,
            timeout_seconds=180,
            description="Static type checker for Python",
            description_ar="مدقق أنواع ثابت لـ Python",
            homepage="https://mypy-lang.org/",
        ),
        ToolInfo(
            id="bandit",
            name="Bandit",
            name_ar="بانديت",
            category=ToolCategory.SECURITY,
            languages=[Language.PYTHON],
            command="bandit",
            version_command="bandit --version",
            capabilities=[
                ToolCapability.JSON_OUTPUT,
                ToolCapability.CONFIG_FILE,
                ToolCapability.CUSTOM_RULES,
            ],
            default_args=["-r", "-f", "json", "-ll"],
            config_file=".bandit",
            priority=30,
            timeout_seconds=120,
            description="Security linter for Python",
            description_ar="أداة فحص أمني لـ Python",
            homepage="https://bandit.readthedocs.io/",
        ),
        ToolInfo(
            id="pylint",
            name="Pylint",
            name_ar="بايلنت",
            category=ToolCategory.LINTER,
            languages=[Language.PYTHON],
            command="pylint",
            version_command="pylint --version",
            capabilities=[
                ToolCapability.JSON_OUTPUT,
                ToolCapability.CONFIG_FILE,
                ToolCapability.CUSTOM_RULES,
            ],
            default_args=["--output-format=json"],
            config_file=".pylintrc",
            priority=40,
            timeout_seconds=180,
            description="Advanced Python code analyzer",
            description_ar="محلل كود Python متقدم",
            homepage="https://pylint.org/",
        ),
        # TypeScript/JavaScript Tools
        ToolInfo(
            id="eslint",
            name="ESLint",
            name_ar="إي إس لنت",
            category=ToolCategory.LINTER,
            languages=[Language.TYPESCRIPT, Language.JAVASCRIPT],
            command="npx",
            version_command="npx eslint --version",
            capabilities=[
                ToolCapability.AUTO_FIX,
                ToolCapability.JSON_OUTPUT,
                ToolCapability.CONFIG_FILE,
                ToolCapability.CUSTOM_RULES,
            ],
            default_args=["eslint", "--format=json"],
            config_file="eslint.config.js",
            priority=10,
            timeout_seconds=120,
            description="Linter for JavaScript and TypeScript",
            description_ar="أداة فحص لـ JavaScript و TypeScript",
            homepage="https://eslint.org/",
        ),
        ToolInfo(
            id="tsc",
            name="TypeScript Compiler",
            name_ar="مترجم تايب سكريبت",
            category=ToolCategory.TYPE_CHECKER,
            languages=[Language.TYPESCRIPT],
            command="npx",
            version_command="npx tsc --version",
            capabilities=[
                ToolCapability.INCREMENTAL,
                ToolCapability.CONFIG_FILE,
                ToolCapability.WATCH_MODE,
            ],
            default_args=["tsc", "--noEmit", "--skipLibCheck"],
            config_file="tsconfig.json",
            priority=20,
            timeout_seconds=180,
            description="TypeScript type checker",
            description_ar="مدقق أنواع TypeScript",
            homepage="https://www.typescriptlang.org/",
        ),
        ToolInfo(
            id="prettier",
            name="Prettier",
            name_ar="بريتير",
            category=ToolCategory.FORMATTER,
            languages=[Language.TYPESCRIPT, Language.JAVASCRIPT],
            command="npx",
            version_command="npx prettier --version",
            capabilities=[
                ToolCapability.AUTO_FIX,
                ToolCapability.CONFIG_FILE,
            ],
            default_args=["prettier", "--check"],
            config_file=".prettierrc",
            priority=30,
            timeout_seconds=60,
            description="Code formatter for multiple languages",
            description_ar="منسق كود للعديد من اللغات",
            homepage="https://prettier.io/",
        ),
        # Dart/Flutter Tools
        ToolInfo(
            id="dart_analyze",
            name="Dart Analyzer",
            name_ar="محلل دارت",
            category=ToolCategory.LINTER,
            languages=[Language.DART],
            command="dart",
            version_command="dart --version",
            capabilities=[
                ToolCapability.CONFIG_FILE,
            ],
            default_args=["analyze", "--format=json"],
            config_file="analysis_options.yaml",
            priority=10,
            timeout_seconds=120,
            description="Static analyzer for Dart",
            description_ar="محلل ثابت لـ Dart",
            homepage="https://dart.dev/tools/dart-analyze",
        ),
        ToolInfo(
            id="dart_format",
            name="Dart Formatter",
            name_ar="منسق دارت",
            category=ToolCategory.FORMATTER,
            languages=[Language.DART],
            command="dart",
            version_command="dart --version",
            capabilities=[
                ToolCapability.AUTO_FIX,
            ],
            default_args=["format", "--set-exit-if-changed"],
            priority=20,
            timeout_seconds=60,
            description="Code formatter for Dart",
            description_ar="منسق كود لـ Dart",
            homepage="https://dart.dev/tools/dart-format",
        ),
        ToolInfo(
            id="flutter_analyze",
            name="Flutter Analyzer",
            name_ar="محلل فلاتر",
            category=ToolCategory.LINTER,
            languages=[Language.DART],
            command="flutter",
            version_command="flutter --version",
            capabilities=[
                ToolCapability.CONFIG_FILE,
            ],
            default_args=["analyze", "--no-fatal-infos"],
            config_file="analysis_options.yaml",
            priority=15,
            timeout_seconds=180,
            description="Flutter-specific analyzer",
            description_ar="محلل خاص بـ Flutter",
            homepage="https://docs.flutter.dev/",
        ),
        ToolInfo(
            id="import_sorter",
            name="Import Sorter",
            name_ar="مرتب الاستيرادات",
            category=ToolCategory.FORMATTER,
            languages=[Language.DART],
            command="dart",
            version_command="dart --version",
            capabilities=[
                ToolCapability.AUTO_FIX,
                ToolCapability.CONFIG_FILE,
            ],
            default_args=["run", "import_sorter:main"],
            config_file="import_sorter.yaml",
            priority=25,
            timeout_seconds=60,
            description="Import organizer for Dart",
            description_ar="منظم الاستيرادات لـ Dart",
            homepage="https://pub.dev/packages/import_sorter",
        ),
        # Multi-language Tools
        ToolInfo(
            id="semgrep",
            name="Semgrep",
            name_ar="سيمجريب",
            category=ToolCategory.SECURITY,
            languages=[
                Language.PYTHON,
                Language.TYPESCRIPT,
                Language.JAVASCRIPT,
                Language.GO,
                Language.JAVA,
                Language.KOTLIN,
            ],
            command="semgrep",
            version_command="semgrep --version",
            capabilities=[
                ToolCapability.CUSTOM_RULES,
                ToolCapability.JSON_OUTPUT,
                ToolCapability.SARIF_OUTPUT,
                ToolCapability.PARALLEL,
            ],
            default_args=["scan", "--json", "--config=auto"],
            priority=50,
            timeout_seconds=300,
            description="Semantic code analyzer for security",
            description_ar="محلل دلالي للكود للأمان",
            homepage="https://semgrep.dev/",
        ),
        ToolInfo(
            id="gitleaks",
            name="Gitleaks",
            name_ar="جيت ليكس",
            category=ToolCategory.SECURITY,
            languages=[
                Language.PYTHON,
                Language.TYPESCRIPT,
                Language.JAVASCRIPT,
                Language.DART,
                Language.GO,
            ],
            command="gitleaks",
            version_command="gitleaks version",
            capabilities=[
                ToolCapability.JSON_OUTPUT,
                ToolCapability.CONFIG_FILE,
            ],
            default_args=["detect", "--no-git", "--report-format=json"],
            config_file=".gitleaks.toml",
            priority=60,
            timeout_seconds=120,
            description="Secret detection tool",
            description_ar="أداة كشف الأسرار",
            homepage="https://gitleaks.io/",
        ),
    ]

    def __init__(
        self,
        config: QualityConfig | None = None,
        config_path: Path | str | None = None,
    ):
        """
        Initialize tool registry.
        تهيئة سجل الأدوات.

        Args:
            config: Quality configuration object
            config_path: Path to .sahool-quality.yaml
        """
        self._tools: dict[str, ToolInfo] = {}
        self._metrics: dict[str, ToolMetrics] = {}
        self._circuit_breakers: dict[str, _CircuitBreaker] = {}
        self._cache: dict[str, tuple[ToolResult, float]] = {}
        self._hooks: dict[str, list[Callable]] = {
            "before_run": [],
            "after_run": [],
            "on_error": [],
        }

        # Load configuration
        if config:
            self._config = config
        elif config_path:
            self._config = QualityConfig.from_yaml(config_path)
        else:
            # Try to find .sahool-quality.yaml in current directory
            default_path = Path(".sahool-quality.yaml")
            self._config = QualityConfig.from_yaml(default_path) if default_path.exists() else QualityConfig()

        # Register default tools
        for tool in self.DEFAULT_TOOLS:
            self.register(tool)

        # Initialize metrics
        for tool_id in self._tools:
            self._metrics[tool_id] = ToolMetrics(tool_id=tool_id)
            self._circuit_breakers[tool_id] = _CircuitBreaker(tool_id)

        logger.info(
            "tool_registry_initialized",
            tools_count=len(self._tools),
            config_loaded=config_path is not None,
        )

    def register(self, tool: ToolInfo) -> None:
        """
        Register a tool in the registry.
        تسجيل أداة في السجل.
        """
        self._tools[tool.id] = tool
        if tool.id not in self._metrics:
            self._metrics[tool.id] = ToolMetrics(tool_id=tool.id)
        if tool.id not in self._circuit_breakers:
            self._circuit_breakers[tool.id] = _CircuitBreaker(tool.id)

        logger.debug("tool_registered", tool_id=tool.id, name=tool.name)

    def unregister(self, tool_id: str) -> None:
        """
        Remove a tool from the registry.
        إزالة أداة من السجل.
        """
        if tool_id in self._tools:
            del self._tools[tool_id]
            logger.debug("tool_unregistered", tool_id=tool_id)

    def get_tool(self, tool_id: str) -> ToolInfo | None:
        """Get tool by ID - الحصول على أداة بواسطة المعرف"""
        return self._tools.get(tool_id)

    def get_all_tools(self) -> list[ToolInfo]:
        """Get all registered tools - الحصول على جميع الأدوات المسجلة"""
        return list(self._tools.values())

    def get_tools_for_language(
        self,
        language: Language | str,
        category: ToolCategory | None = None,
    ) -> list[ToolInfo]:
        """
        Get tools available for a specific language.
        الحصول على الأدوات المتاحة للغة معينة.

        Args:
            language: Programming language
            category: Optional category filter

        Returns:
            List of tools sorted by priority
        """
        if isinstance(language, str):
            language = Language(language.lower())

        tools = [
            tool
            for tool in self._tools.values()
            if language in tool.languages
            and tool.status != ToolStatus.DISABLED
            and (category is None or tool.category == category)
        ]

        return sorted(tools, key=lambda t: t.priority)

    def get_enabled_tools(self, language: Language | str) -> list[ToolInfo]:
        """
        Get enabled tools for a language based on configuration.
        الحصول على الأدوات الممكّنة للغة بناءً على الإعدادات.
        """
        if isinstance(language, str):
            language = Language(language.lower())

        # Get configured tools for this language
        if language == Language.PYTHON:
            enabled_ids = self._config.python_tools
        elif language in (Language.TYPESCRIPT, Language.JAVASCRIPT):
            enabled_ids = self._config.typescript_tools
        elif language == Language.DART:
            enabled_ids = self._config.dart_tools
        else:
            enabled_ids = []

        tools = []
        for tool_id in enabled_ids:
            tool = self.get_tool(tool_id)
            if tool and tool.status != ToolStatus.DISABLED:
                tools.append(tool)

        return tools

    async def check_availability(self, tool_id: str | None = None) -> dict[str, bool]:
        """
        Check if tools are available on the system.
        التحقق من توفر الأدوات على النظام.

        Args:
            tool_id: Specific tool to check, or None for all tools

        Returns:
            Dict of tool_id -> available
        """
        tools_to_check = [self._tools[tool_id]] if tool_id else list(self._tools.values())
        results: dict[str, bool] = {}

        for tool in tools_to_check:
            try:
                # Check if command exists
                cmd = tool.command.split()[0]
                available = shutil.which(cmd) is not None

                if available:
                    # Try to get version
                    try:
                        # nosemgrep: dangerous-subprocess-use-audit -- internal tooling (Auto-Fix/diagnostics); args are hardcoded program names + validated paths, not user-controlled shell strings
                        result = subprocess.run(
                            tool.version_command.split(),
                            capture_output=True,
                            text=True,
                            timeout=10,
                        )
                        if result.returncode == 0:
                            tool.version = result.stdout.strip().split("\n")[0]
                            tool.status = ToolStatus.AVAILABLE
                        else:
                            tool.status = ToolStatus.UNAVAILABLE
                            available = False
                    except Exception:
                        tool.status = ToolStatus.UNAVAILABLE
                        available = False
                else:
                    tool.status = ToolStatus.UNAVAILABLE

                tool.last_check = datetime.now(UTC)
                results[tool.id] = available

            except Exception as e:
                logger.warning(
                    "tool_check_failed",
                    tool_id=tool.id,
                    error=str(e),
                )
                results[tool.id] = False
                tool.status = ToolStatus.UNAVAILABLE

        return results

    async def run_tool(
        self,
        tool_id: str,
        target: str | Path,
        extra_args: list[str] | None = None,
        auto_fix: bool | None = None,
        timeout: int | None = None,
    ) -> ToolResult:
        """
        Run a single tool on a target.
        تشغيل أداة واحدة على هدف.

        Args:
            tool_id: Tool identifier
            target: File or directory to analyze
            extra_args: Additional arguments
            auto_fix: Override auto-fix setting
            timeout: Override timeout

        Returns:
            ToolResult with output and metrics
        """
        tool = self.get_tool(tool_id)
        if not tool:
            return ToolResult(
                tool_id=tool_id,
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Tool '{tool_id}' not found in registry",
                duration_ms=0,
                error_message=f"Tool '{tool_id}' not found",
            )

        # Check circuit breaker
        cb = self._circuit_breakers.get(tool_id)
        if cb and cb.is_open:
            self._metrics[tool_id].circuit_opens += 1
            return ToolResult(
                tool_id=tool_id,
                success=False,
                exit_code=-1,
                stdout="",
                stderr="Circuit breaker is open",
                duration_ms=0,
                error_message="Tool temporarily unavailable (circuit breaker open)",
            )

        # Check cache
        cache_key = self._get_cache_key(tool_id, str(target), extra_args)
        if self._config.cache_enabled:
            cached = self._cache.get(cache_key)
            if cached:
                result, timestamp = cached
                if time.time() - timestamp < self._config.cache_ttl_seconds:
                    logger.debug("cache_hit", tool_id=tool_id, target=str(target))
                    return result

        # Call hooks
        for hook in self._hooks["before_run"]:
            hook(tool_id, target)

        # Build command
        args = [tool.command] + tool.default_args + (extra_args or [])

        # Add auto-fix flag if supported
        should_fix = auto_fix if auto_fix is not None else self._config.auto_fix
        if should_fix and ToolCapability.AUTO_FIX in tool.capabilities:
            if tool_id == "ruff" or tool_id == "eslint":
                args.append("--fix")
            elif tool_id in ("dart_format", "import_sorter"):
                # These tools fix by default
                pass

        # Add target
        args.append(str(target))

        # Apply tool-specific overrides
        if tool_id in self._config.tool_overrides:
            overrides = self._config.tool_overrides[tool_id]
            if "args" in overrides:
                args.extend(overrides["args"])

        # Run the tool
        start_time = time.time()
        try:
            # nosemgrep: dangerous-asyncio-create-exec-audit -- internal tooling; args are hardcoded program names + validated paths, not user-controlled shell strings
            process = await asyncio.create_subprocess_exec(
                *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            tool_timeout = timeout or tool.timeout_seconds
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=tool_timeout,
            )

            duration_ms = (time.time() - start_time) * 1000
            exit_code = process.returncode or 0

            # Parse issues count (tool-specific)
            issues_count = self._parse_issues_count(tool_id, stdout.decode(), stderr.decode())

            result = ToolResult(
                tool_id=tool_id,
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout.decode(),
                stderr=stderr.decode(),
                duration_ms=duration_ms,
                issues_count=issues_count,
            )

            # Update metrics
            self._update_metrics(tool_id, result)

            # Update circuit breaker
            if cb:
                if result.success:
                    cb.record_success()
                else:
                    cb.record_failure()

            # Cache result
            if self._config.cache_enabled:
                self._cache[cache_key] = (result, time.time())

            # Call hooks
            for hook in self._hooks["after_run"]:
                hook(tool_id, target, result)

            return result

        except TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            result = ToolResult(
                tool_id=tool_id,
                success=False,
                exit_code=-1,
                stdout="",
                stderr=f"Tool timed out after {tool.timeout_seconds}s",
                duration_ms=duration_ms,
                error_message="Timeout",
            )

            if cb:
                cb.record_failure()

            for hook in self._hooks["on_error"]:
                hook(tool_id, target, result)

            return result

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            result = ToolResult(
                tool_id=tool_id,
                success=False,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                duration_ms=duration_ms,
                error_message=str(e),
            )

            if cb:
                cb.record_failure()

            for hook in self._hooks["on_error"]:
                hook(tool_id, target, result)

            return result

    async def run_tools(
        self,
        target: str | Path,
        tools: list[str] | None = None,
        language: Language | str | None = None,
        parallel: bool | None = None,
    ) -> list[ToolResult]:
        """
        Run multiple tools on a target.
        تشغيل أدوات متعددة على هدف.

        Args:
            target: File or directory to analyze
            tools: List of tool IDs (if None, auto-detect from language)
            language: Programming language (for auto-detection)
            parallel: Override parallel execution setting

        Returns:
            List of ToolResults
        """
        # Determine which tools to run
        if tools:
            tools_to_run = [self.get_tool(t) for t in tools if self.get_tool(t)]
        elif language:
            tools_to_run = self.get_enabled_tools(language)
        else:
            # Try to detect language from file extension
            target_path = Path(target)
            ext_to_lang = {
                ".py": Language.PYTHON,
                ".ts": Language.TYPESCRIPT,
                ".tsx": Language.TYPESCRIPT,
                ".js": Language.JAVASCRIPT,
                ".jsx": Language.JAVASCRIPT,
                ".dart": Language.DART,
            }
            lang = ext_to_lang.get(target_path.suffix.lower())
            tools_to_run = self.get_enabled_tools(lang) if lang else []

        if not tools_to_run:
            return []

        # Execute tools
        should_parallel = parallel if parallel is not None else self._config.parallel_execution

        if should_parallel and len(tools_to_run) > 1:
            # Run in parallel with semaphore
            semaphore = asyncio.Semaphore(self._config.max_parallel_tools)

            async def run_with_semaphore(tool: ToolInfo) -> ToolResult:
                async with semaphore:
                    return await self.run_tool(tool.id, target)

            results = await asyncio.gather(*[run_with_semaphore(tool) for tool in tools_to_run])
            return list(results)
        else:
            # Run sequentially
            results = []
            for tool in tools_to_run:
                result = await self.run_tool(tool.id, target)
                results.append(result)
            return results

    def get_metrics(self, tool_id: str | None = None) -> dict[str, ToolMetrics]:
        """
        Get performance metrics for tools.
        الحصول على مقاييس الأداء للأدوات.
        """
        if tool_id:
            return {tool_id: self._metrics[tool_id]} if tool_id in self._metrics else {}
        return dict(self._metrics)

    def add_hook(self, event: str, callback: Callable) -> None:
        """
        Add a hook for tool events.
        إضافة خطاف لأحداث الأدوات.

        Events: before_run, after_run, on_error
        """
        if event in self._hooks:
            self._hooks[event].append(callback)

    def clear_cache(self, tool_id: str | None = None) -> None:
        """
        Clear the results cache.
        مسح ذاكرة التخزين المؤقت للنتائج.
        """
        if tool_id:
            self._cache = {k: v for k, v in self._cache.items() if not k.startswith(f"{tool_id}:")}
        else:
            self._cache.clear()

    def reset_circuit_breakers(self) -> None:
        """Reset all circuit breakers - إعادة تعيين جميع قواطع الدائرة"""
        for cb in self._circuit_breakers.values():
            cb.reset()

    def _get_cache_key(self, tool_id: str, target: str, extra_args: list[str] | None) -> str:
        """Generate cache key - توليد مفتاح التخزين المؤقت"""
        args_str = ":".join(extra_args) if extra_args else ""
        content = f"{tool_id}:{target}:{args_str}"

        # Add file hash if it's a file
        try:
            if os.path.isfile(target):
                with open(target, "rb") as f:
                    file_hash = hashlib.md5(f.read(), usedforsecurity=False).hexdigest()[:8]
                content += f":{file_hash}"
        except Exception:
            pass

        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def _update_metrics(self, tool_id: str, result: ToolResult) -> None:
        """Update tool metrics - تحديث مقاييس الأداة"""
        metrics = self._metrics[tool_id]
        metrics.total_runs += 1
        metrics.total_duration_ms += result.duration_ms
        metrics.issues_found += result.issues_count
        metrics.issues_fixed += result.fixed_count
        metrics.last_run = result.timestamp

        if result.success:
            metrics.successful_runs += 1
        else:
            metrics.failed_runs += 1

        # Update average duration
        metrics.avg_duration_ms = metrics.total_duration_ms / metrics.total_runs

    def _parse_issues_count(self, tool_id: str, stdout: str, stderr: str) -> int:
        """Parse issues count from tool output - استخراج عدد المشاكل من مخرجات الأداة"""
        import json
        import re

        try:
            if tool_id == "ruff":
                # Ruff JSON output is a list of issues
                data = json.loads(stdout) if stdout else []
                return len(data) if isinstance(data, list) else 0
            elif tool_id == "eslint":
                data = json.loads(stdout) if stdout else []
                return sum(len(f.get("messages", [])) for f in data if isinstance(f, dict))
            elif tool_id == "bandit":
                data = json.loads(stdout) if stdout else {}
                return len(data.get("results", []))
            elif tool_id == "mypy":
                # Count lines with "error:" or "warning:"
                return len(re.findall(r"(error|warning):", stdout + stderr))
            elif tool_id in ("dart_analyze", "flutter_analyze"):
                # Count "info", "warning", "error" lines
                return len(re.findall(r"(info|warning|error)\s+-", stdout + stderr))
            else:
                # Generic: count non-empty lines
                return len([l for l in stdout.split("\n") if l.strip()])
        except Exception:
            return 0


# =============================================================================
# Circuit Breaker - قاطع الدائرة
# =============================================================================


class _CircuitBreaker:
    """Simple circuit breaker for tool resilience - قاطع دائرة بسيط لمرونة الأدوات"""

    def __init__(
        self,
        tool_id: str,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
    ):
        self.tool_id = tool_id
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time: float | None = None
        self._is_open = False

    @property
    def is_open(self) -> bool:
        """Check if circuit breaker is open"""
        if not self._is_open:
            return False

        # Check if recovery timeout has passed
        if self.last_failure_time:
            elapsed = time.time() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self._is_open = False
                self.failures = 0
                return False

        return True

    def record_success(self) -> None:
        """Record successful execution"""
        self.failures = 0
        self._is_open = False

    def record_failure(self) -> None:
        """Record failed execution"""
        self.failures += 1
        self.last_failure_time = time.time()

        if self.failures >= self.failure_threshold:
            self._is_open = True
            logger.warning(
                "circuit_breaker_opened",
                tool_id=self.tool_id,
                failures=self.failures,
            )

    def reset(self) -> None:
        """Reset the circuit breaker"""
        self.failures = 0
        self._is_open = False
        self.last_failure_time = None


# =============================================================================
# Global Instance - النسخة العامة
# =============================================================================

_global_registry: ToolRegistry | None = None


def get_tool_registry(
    config: QualityConfig | None = None,
    config_path: Path | str | None = None,
) -> ToolRegistry:
    """
    Get or create the global tool registry.
    الحصول على أو إنشاء سجل الأدوات العام.
    """
    global _global_registry

    if _global_registry is None:
        _global_registry = ToolRegistry(config=config, config_path=config_path)
    return _global_registry


def reset_tool_registry() -> None:
    """Reset the global registry - إعادة تعيين السجل العام"""
    global _global_registry
    _global_registry = None


# =============================================================================
# Configuration Generator - مولد الإعدادات
# =============================================================================


def generate_default_config(output_path: Path | str | None = None) -> str:
    """
    Generate default .sahool-quality.yaml configuration.
    توليد إعدادات .sahool-quality.yaml الافتراضية.
    """
    config_content = """\
# SAHOOL Quality Configuration - إعدادات جودة سهول
# ===================================================
#
# This file configures which quality tools are enabled and their settings.
# هذا الملف يحدد أدوات الجودة الممكنة وإعداداتها.
#
# Place this file in your project root as .sahool-quality.yaml
# ضع هذا الملف في جذر مشروعك باسم .sahool-quality.yaml

# Global Settings - الإعدادات العامة
fail_on_warning: false
auto_fix: true
parallel: true
max_parallel_tools: 4

# Cache Configuration - إعدادات التخزين المؤقت
cache:
  enabled: true
  ttl: 300  # seconds

# Python Tools - أدوات Python
python:
  tools:
    - ruff      # Fast linting & formatting - فحص وتنسيق سريع
    - mypy      # Type checking - فحص الأنواع
    - bandit    # Security scanning - فحص أمني
    # - pylint  # Advanced analysis - تحليل متقدم (optional)
    # - semgrep # Security patterns - أنماط أمنية (optional)

# TypeScript/JavaScript Tools - أدوات TypeScript/JavaScript
typescript:
  tools:
    - eslint    # Linting - فحص الكود
    - tsc       # Type checking - فحص الأنواع
    # - prettier # Formatting - التنسيق (optional)

# Dart/Flutter Tools - أدوات Dart/Flutter
dart:
  tools:
    - dart_analyze    # Static analysis - تحليل ثابت
    - dart_format     # Formatting - التنسيق
    - import_sorter   # Import organization - تنظيم الاستيرادات
    # - flutter_analyze # Flutter-specific - خاص بـ Flutter

# Tool-Specific Overrides - تخصيصات الأدوات
tool_overrides:
  ruff:
    args: []
    # config: "ruff.toml"  # Custom config file

  eslint:
    args:
      - "--max-warnings=50"

  mypy:
    args:
      - "--ignore-missing-imports"
      - "--no-error-summary"

# Excluded Paths - المسارات المستبعدة
exclude:
  - "**/node_modules/**"
  - "**/.git/**"
  - "**/build/**"
  - "**/dist/**"
  - "**/*.g.dart"
  - "**/*.freezed.dart"
  - "**/generated/**"
"""

    if output_path:
        Path(output_path).write_text(config_content, encoding="utf-8")

    return config_content


# =============================================================================
# Exports - التصديرات
# =============================================================================

__all__ = [
    # Classes
    "ToolRegistry",
    "ToolInfo",
    "ToolResult",
    "QualityConfig",
    "ToolMetrics",
    # Enums
    "ToolCategory",
    "ToolCapability",
    "ToolStatus",
    "Language",
    # Functions
    "get_tool_registry",
    "reset_tool_registry",
    "generate_default_config",
]
