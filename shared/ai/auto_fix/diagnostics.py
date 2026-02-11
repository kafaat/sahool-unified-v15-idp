"""
Code Diagnostics Module
=======================
وحدة تشخيص الأخطاء البرمجية

Provides integration with multiple linting and analysis tools
to detect code issues across Python, TypeScript, and Dart.

Supported Tools:
    - Ruff (Python linting/formatting)
    - ESLint (JavaScript/TypeScript)
    - Mypy (Python type checking)
    - Bandit (Python security)
    - Dart Analyze (Flutter/Dart)
    - Semgrep (Pattern-based security scanning)
    - Pylint (Advanced Python linting)

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio
import hashlib
import json
import logging
import os
import re
import time
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .models import (
    CodeLocation,
    Diagnostic,
    DiagnosticCategory,
    DiagnosticReport,
    DiagnosticSeverity,
    ToolType,
)

logger = logging.getLogger(__name__)


class DiagnosticError(Exception):
    """Exception raised for diagnostic errors."""

    pass


# ============================================================================
# CIRCUIT BREAKER - For resilient tool execution
# ============================================================================


@dataclass
class CircuitBreakerState:
    """State for circuit breaker pattern."""

    failures: int = 0
    last_failure: datetime | None = None
    state: str = "closed"  # closed, open, half_open
    success_count: int = 0


class CircuitBreaker:
    """
    Circuit breaker for diagnostic tool execution.

    قاطع الدائرة لتنفيذ أدوات التشخيص

    Prevents cascading failures when tools become unavailable.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        half_open_successes: int = 2,
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_successes = half_open_successes
        self._states: dict[str, CircuitBreakerState] = {}

    def _get_state(self, tool: str) -> CircuitBreakerState:
        if tool not in self._states:
            self._states[tool] = CircuitBreakerState()
        return self._states[tool]

    def can_execute(self, tool: str) -> bool:
        """Check if tool execution is allowed."""
        state = self._get_state(tool)

        if state.state == "closed":
            return True

        if state.state == "open":
            if state.last_failure:
                elapsed = (datetime.now(UTC) - state.last_failure).total_seconds()
                if elapsed >= self.recovery_timeout:
                    state.state = "half_open"
                    state.success_count = 0
                    logger.info(f"Circuit breaker for {tool} moved to half_open")
                    return True
            return False

        # half_open state
        return True

    def record_success(self, tool: str) -> None:
        """Record successful execution."""
        state = self._get_state(tool)

        if state.state == "half_open":
            state.success_count += 1
            if state.success_count >= self.half_open_successes:
                state.state = "closed"
                state.failures = 0
                logger.info(f"Circuit breaker for {tool} closed")
        elif state.state == "closed":
            state.failures = max(0, state.failures - 1)

    def record_failure(self, tool: str) -> None:
        """Record failed execution."""
        state = self._get_state(tool)
        state.failures += 1
        state.last_failure = datetime.now(UTC)

        if state.state == "half_open":
            state.state = "open"
            logger.warning(f"Circuit breaker for {tool} reopened")
        elif state.failures >= self.failure_threshold:
            state.state = "open"
            logger.warning(f"Circuit breaker for {tool} opened after {state.failures} failures")

    def get_status(self) -> dict[str, dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {
            tool: {
                "state": state.state,
                "failures": state.failures,
                "last_failure": state.last_failure.isoformat() if state.last_failure else None,
            }
            for tool, state in self._states.items()
        }


# ============================================================================
# CACHING - For repeated diagnostics
# ============================================================================


@dataclass
class CacheEntry:
    """Cache entry for diagnostic results."""

    result: list[Diagnostic]
    created_at: datetime
    file_hash: str
    tool: ToolType


class DiagnosticCache:
    """
    Cache for diagnostic results.

    ذاكرة تخزين مؤقتة لنتائج التشخيص

    Caches results based on file content hash to avoid repeated analysis.
    """

    def __init__(self, ttl_seconds: int = 300, max_entries: int = 1000):
        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._cache: dict[str, CacheEntry] = {}
        self._hits = 0
        self._misses = 0

    def _make_key(self, file_path: str, tool: ToolType) -> str:
        return f"{file_path}:{tool.value}"

    def _compute_hash(self, file_path: str) -> str:
        """Compute hash of file content."""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read(), usedforsecurity=False).hexdigest()
        except (FileNotFoundError, OSError):
            return ""

    def get(self, file_path: str, tool: ToolType) -> list[Diagnostic] | None:
        """Get cached diagnostics if valid."""
        key = self._make_key(file_path, tool)
        entry = self._cache.get(key)

        if not entry:
            self._misses += 1
            return None

        # Check TTL
        age = (datetime.now(UTC) - entry.created_at).total_seconds()
        if age > self.ttl_seconds:
            del self._cache[key]
            self._misses += 1
            return None

        # Check file hash
        current_hash = self._compute_hash(file_path)
        if current_hash != entry.file_hash:
            del self._cache[key]
            self._misses += 1
            return None

        self._hits += 1
        return entry.result

    def set(self, file_path: str, tool: ToolType, result: list[Diagnostic]) -> None:
        """Cache diagnostic results."""
        # Evict oldest entries if at capacity
        if len(self._cache) >= self.max_entries:
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k].created_at)
            del self._cache[oldest_key]

        key = self._make_key(file_path, tool)
        self._cache[key] = CacheEntry(
            result=result,
            created_at=datetime.now(UTC),
            file_hash=self._compute_hash(file_path),
            tool=tool,
        )

    def invalidate(self, file_path: str | None = None) -> None:
        """Invalidate cache entries."""
        if file_path:
            keys_to_delete = [k for k in self._cache if k.startswith(f"{file_path}:")]
            for key in keys_to_delete:
                del self._cache[key]
        else:
            self._cache.clear()

    def get_stats(self) -> dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        return {
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total * 100, 2) if total > 0 else 0,
        }


# ============================================================================
# SECURITY PATTERNS - Advanced vulnerability detection
# ============================================================================


@dataclass
class SecurityPattern:
    """Security vulnerability pattern."""

    id: str
    pattern: str
    severity: str  # critical, high, medium, low
    category: str  # injection, crypto, auth, etc.
    message: str
    message_ar: str
    suggestion: str
    suggestion_ar: str
    cwe: str | None = None  # Common Weakness Enumeration
    owasp: str | None = None  # OWASP category
    languages: list[str] = field(default_factory=lambda: ["python"])


# Comprehensive security patterns database
SECURITY_PATTERNS: list[SecurityPattern] = [
    # SQL Injection
    SecurityPattern(
        id="SEC001",
        pattern=r'execute\s*\(\s*["\'].*%[sd].*["\']\s*%',
        severity="critical",
        category="injection",
        message="SQL Injection vulnerability via string formatting",
        message_ar="ثغرة حقن SQL عبر تنسيق النص",
        suggestion="Use parameterized queries instead",
        suggestion_ar="استخدم الاستعلامات المعلمة بدلاً من ذلك",
        cwe="CWE-89",
        owasp="A03:2021",
    ),
    SecurityPattern(
        id="SEC002",
        pattern=r'execute\s*\(\s*f["\']',
        severity="critical",
        category="injection",
        message="SQL Injection vulnerability via f-string",
        message_ar="ثغرة حقن SQL عبر f-string",
        suggestion="Use parameterized queries instead",
        suggestion_ar="استخدم الاستعلامات المعلمة بدلاً من ذلك",
        cwe="CWE-89",
        owasp="A03:2021",
    ),
    # Command Injection
    SecurityPattern(
        id="SEC003",
        pattern=r"os\.system\s*\(",
        severity="high",
        category="injection",
        message="Potential command injection via os.system",
        message_ar="احتمال حقن الأوامر عبر os.system",
        suggestion="Use subprocess with shell=False",
        suggestion_ar="استخدم subprocess مع shell=False",
        cwe="CWE-78",
        owasp="A03:2021",
    ),
    SecurityPattern(
        id="SEC004",
        pattern=r"subprocess\..*shell\s*=\s*True",
        severity="high",
        category="injection",
        message="Shell injection risk with shell=True",
        message_ar="خطر حقن الأوامر مع shell=True",
        suggestion="Use shell=False and pass arguments as list",
        suggestion_ar="استخدم shell=False ومرر الوسائط كقائمة",
        cwe="CWE-78",
        owasp="A03:2021",
    ),
    # Dangerous Functions
    SecurityPattern(
        id="SEC005",
        pattern=r"\beval\s*\(",
        severity="critical",
        category="code_execution",
        message="Use of eval() allows arbitrary code execution",
        message_ar="استخدام eval() يسمح بتنفيذ كود عشوائي",
        suggestion="Use ast.literal_eval() for safe parsing",
        suggestion_ar="استخدم ast.literal_eval() للتحليل الآمن",
        cwe="CWE-94",
        owasp="A03:2021",
        languages=["python", "javascript", "typescript"],
    ),
    SecurityPattern(
        id="SEC006",
        pattern=r"\bexec\s*\(",
        severity="critical",
        category="code_execution",
        message="Use of exec() allows arbitrary code execution",
        message_ar="استخدام exec() يسمح بتنفيذ كود عشوائي",
        suggestion="Avoid exec() or use restricted execution",
        suggestion_ar="تجنب exec() أو استخدم التنفيذ المقيد",
        cwe="CWE-94",
        owasp="A03:2021",
    ),
    # Deserialization
    SecurityPattern(
        id="SEC007",
        pattern=r"pickle\.loads?\s*\(",
        severity="critical",
        category="deserialization",
        message="Unsafe deserialization with pickle",
        message_ar="فك تسلسل غير آمن باستخدام pickle",
        suggestion="Use safe serialization formats like JSON",
        suggestion_ar="استخدم تنسيقات التسلسل الآمنة مثل JSON",
        cwe="CWE-502",
        owasp="A08:2021",
    ),
    SecurityPattern(
        id="SEC008",
        pattern=r"yaml\.load\s*\([^,)]+\)",
        severity="high",
        category="deserialization",
        message="Unsafe YAML loading without Loader specification",
        message_ar="تحميل YAML غير آمن بدون تحديد Loader",
        suggestion="Use yaml.safe_load() instead",
        suggestion_ar="استخدم yaml.safe_load() بدلاً من ذلك",
        cwe="CWE-502",
        owasp="A08:2021",
    ),
    # Hardcoded Secrets
    SecurityPattern(
        id="SEC009",
        pattern=r'(?i)(password|secret|api_key|apikey|token|auth)\s*=\s*["\'][^"\']+["\']',
        severity="critical",
        category="secrets",
        message="Hardcoded secret or credential detected",
        message_ar="تم اكتشاف سر أو اعتماد مكتوب في الكود",
        suggestion="Use environment variables or secret manager",
        suggestion_ar="استخدم متغيرات البيئة أو مدير الأسرار",
        cwe="CWE-798",
        owasp="A07:2021",
    ),
    # Weak Cryptography
    SecurityPattern(
        id="SEC010",
        pattern=r"(?i)(md5|sha1)\s*\(",
        severity="medium",
        category="crypto",
        message="Use of weak cryptographic hash function",
        message_ar="استخدام دالة تجزئة تشفيرية ضعيفة",
        suggestion="Use SHA-256 or stronger hash functions",
        suggestion_ar="استخدم SHA-256 أو دوال تجزئة أقوى",
        cwe="CWE-327",
        owasp="A02:2021",
    ),
    SecurityPattern(
        id="SEC011",
        pattern=r"(?i)random\.(random|randint|choice)\s*\(",
        severity="medium",
        category="crypto",
        message="Use of insecure random for security-sensitive operations",
        message_ar="استخدام عشوائي غير آمن للعمليات الحساسة أمنياً",
        suggestion="Use secrets module for cryptographic randomness",
        suggestion_ar="استخدم وحدة secrets للعشوائية التشفيرية",
        cwe="CWE-330",
        owasp="A02:2021",
    ),
    # Path Traversal
    SecurityPattern(
        id="SEC012",
        pattern=r"open\s*\([^)]*\+[^)]*\)",
        severity="high",
        category="path_traversal",
        message="Potential path traversal vulnerability",
        message_ar="احتمال ثغرة اجتياز المسار",
        suggestion="Validate and sanitize file paths",
        suggestion_ar="تحقق من مسارات الملفات وطهرها",
        cwe="CWE-22",
        owasp="A01:2021",
    ),
    # XSS (Frontend)
    SecurityPattern(
        id="SEC013",
        pattern=r"innerHTML\s*=",
        severity="high",
        category="xss",
        message="XSS risk with innerHTML assignment",
        message_ar="خطر XSS مع تعيين innerHTML",
        suggestion="Use textContent or sanitize input",
        suggestion_ar="استخدم textContent أو طهر المدخلات",
        cwe="CWE-79",
        owasp="A03:2021",
        languages=["javascript", "typescript"],
    ),
    SecurityPattern(
        id="SEC014",
        pattern=r"dangerouslySetInnerHTML",
        severity="high",
        category="xss",
        message="Potential XSS via dangerouslySetInnerHTML",
        message_ar="احتمال XSS عبر dangerouslySetInnerHTML",
        suggestion="Sanitize content before rendering",
        suggestion_ar="طهر المحتوى قبل العرض",
        cwe="CWE-79",
        owasp="A03:2021",
        languages=["javascript", "typescript"],
    ),
    # SSRF
    SecurityPattern(
        id="SEC015",
        pattern=r"requests\.(get|post|put|delete)\s*\([^)]*\+",
        severity="high",
        category="ssrf",
        message="Potential SSRF vulnerability",
        message_ar="احتمال ثغرة SSRF",
        suggestion="Validate and whitelist URLs",
        suggestion_ar="تحقق من عناوين URL وقم بإدراجها في القائمة البيضاء",
        cwe="CWE-918",
        owasp="A10:2021",
    ),
    # Insecure SSL
    SecurityPattern(
        id="SEC016",
        pattern=r"verify\s*=\s*False",
        severity="high",
        category="ssl",
        message="SSL certificate verification disabled",
        message_ar="تحقق شهادة SSL معطل",
        suggestion="Enable SSL certificate verification",
        suggestion_ar="قم بتفعيل التحقق من شهادة SSL",
        cwe="CWE-295",
        owasp="A07:2021",
    ),
    # Debug Mode
    SecurityPattern(
        id="SEC017",
        pattern=r"(?i)debug\s*=\s*True",
        severity="medium",
        category="config",
        message="Debug mode enabled in production code",
        message_ar="وضع التصحيح مفعل في كود الإنتاج",
        suggestion="Disable debug mode in production",
        suggestion_ar="قم بتعطيل وضع التصحيح في الإنتاج",
        cwe="CWE-489",
        owasp="A05:2021",
    ),
    # Assert Statements
    SecurityPattern(
        id="SEC018",
        pattern=r"\bassert\s+",
        severity="low",
        category="assertion",
        message="Assert statements can be disabled with -O flag",
        message_ar="يمكن تعطيل عبارات assert مع علم -O",
        suggestion="Use proper validation instead of assert",
        suggestion_ar="استخدم التحقق المناسب بدلاً من assert",
        cwe="CWE-617",
        owasp="A04:2021",
    ),
]


# Arabic translations for common error messages
ERROR_TRANSLATIONS: dict[str, str] = {
    # Syntax & Structure
    "undefined name": "اسم غير معرّف",
    "unused import": "استيراد غير مستخدم",
    "unused variable": "متغير غير مستخدم",
    "missing whitespace": "مسافة بيضاء ناقصة",
    "line too long": "السطر طويل جداً",
    "expected indentation": "المسافة البادئة متوقعة",
    "invalid syntax": "بناء جملة غير صالح",
    "undefined variable": "متغير غير معرّف",
    "module not found": "الوحدة غير موجودة",
    "unreachable code": "كود لا يمكن الوصول إليه",
    "duplicate key": "مفتاح مكرر",
    "naming convention": "اصطلاح التسمية",
    "missing return": "إرجاع ناقص",
    "redefinition": "إعادة تعريف",
    "shadowing": "تظليل المتغير",
    # Type Errors
    "type mismatch": "عدم تطابق النوع",
    "incompatible type": "نوع غير متوافق",
    "missing type": "نوع مفقود",
    "argument type": "نوع الوسيطة",
    "return type": "نوع الإرجاع",
    "generic type": "نوع عام",
    "optional type": "نوع اختياري",
    # Security
    "security vulnerability": "ثغرة أمنية",
    "hardcoded secret": "سر مكتوب في الكود",
    "sql injection": "حقن SQL",
    "xss vulnerability": "ثغرة XSS",
    "command injection": "حقن الأوامر",
    "path traversal": "اجتياز المسار",
    "insecure random": "عشوائي غير آمن",
    "weak hash": "تجزئة ضعيفة",
    "ssrf": "طلب من جانب الخادم مزور",
    "unsafe deserialization": "فك تسلسل غير آمن",
    "ssl verification": "التحقق من SSL",
    "debug mode": "وضع التصحيح",
    # Performance
    "performance": "أداء",
    "inefficient": "غير فعال",
    "n+1 query": "استعلام N+1",
    "memory leak": "تسرب الذاكرة",
    "blocking call": "استدعاء محجوب",
    "unnecessary loop": "حلقة غير ضرورية",
    # Best Practice
    "deprecated": "مهمل",
    "possible bug": "خطأ محتمل",
    "complexity": "تعقيد",
    "maintainability": "قابلية الصيانة",
    "testability": "قابلية الاختبار",
    "code smell": "رائحة الكود",
    "magic number": "رقم سحري",
    "global variable": "متغير عام",
    # Documentation
    "missing docstring": "توثيق مفقود",
    "incomplete docstring": "توثيق ناقص",
    "outdated comment": "تعليق قديم",
}


def translate_message(message: str) -> str:
    """Translate error message to Arabic."""
    message_lower = message.lower()
    for eng, ar in ERROR_TRANSLATIONS.items():
        if eng in message_lower:
            return ar
    return "خطأ في الكود"


def get_category_from_rule(rule_id: str, tool: ToolType) -> DiagnosticCategory:
    """Determine category from rule ID and tool."""
    if tool == ToolType.RUFF:
        if rule_id.startswith("E"):
            return DiagnosticCategory.SYNTAX
        elif rule_id.startswith("F"):
            return DiagnosticCategory.LOGIC
        elif rule_id.startswith("W"):
            return DiagnosticCategory.STYLE
        elif rule_id.startswith("I"):
            return DiagnosticCategory.IMPORT
        elif rule_id.startswith("N"):
            return DiagnosticCategory.NAMING
        elif rule_id.startswith("B"):
            return DiagnosticCategory.BEST_PRACTICE
        elif rule_id.startswith("S"):
            return DiagnosticCategory.SECURITY
        elif rule_id.startswith("UP"):
            return DiagnosticCategory.DEPRECATION
        elif rule_id.startswith("SIM"):
            return DiagnosticCategory.PERFORMANCE
    elif tool == ToolType.BANDIT:
        return DiagnosticCategory.SECURITY
    elif tool == ToolType.MYPY:
        return DiagnosticCategory.TYPE
    elif tool == ToolType.ESLINT:
        if "security" in rule_id.lower():
            return DiagnosticCategory.SECURITY
        elif "no-unused" in rule_id:
            return DiagnosticCategory.LOGIC
        elif "style" in rule_id or "format" in rule_id:
            return DiagnosticCategory.STYLE

    return DiagnosticCategory.LOGIC


def get_severity_from_level(level: str) -> DiagnosticSeverity:
    """Convert tool-specific level to DiagnosticSeverity."""
    level = level.lower()
    if level in ("error", "e", "high", "critical"):
        return DiagnosticSeverity.ERROR
    elif level in ("warning", "w", "warn", "medium"):
        return DiagnosticSeverity.WARNING
    elif level in ("info", "information", "i", "low"):
        return DiagnosticSeverity.INFO
    return DiagnosticSeverity.HINT


class CodeDiagnostics:
    """
    Code diagnostics engine.

    محرك تشخيص الأخطاء البرمجية

    Integrates with multiple linting tools to provide
    comprehensive code analysis with caching and circuit breaker.

    Example:
        diagnostics = CodeDiagnostics()
        report = await diagnostics.diagnose_file("src/main.py")
        for diag in report.diagnostics:
            print(f"{diag.severity}: {diag.message}")

    Features:
        - Multi-tool integration (Ruff, ESLint, Mypy, Bandit, Semgrep, Pylint)
        - Circuit breaker for resilient execution
        - Caching for repeated diagnostics
        - Advanced security pattern detection
        - Bilingual (Arabic/English) support
    """

    def __init__(
        self,
        ruff_path: str = "ruff",
        eslint_path: str = "eslint",
        mypy_path: str = "mypy",
        bandit_path: str = "bandit",
        dart_path: str = "dart",
        semgrep_path: str = "semgrep",
        pylint_path: str = "pylint",
        timeout: int = 60,
        enable_cache: bool = True,
        cache_ttl: int = 300,
        enable_circuit_breaker: bool = True,
    ):
        """
        Initialize CodeDiagnostics.

        Args:
            ruff_path: Path to ruff executable
            eslint_path: Path to eslint executable
            mypy_path: Path to mypy executable
            bandit_path: Path to bandit executable
            dart_path: Path to dart executable
            semgrep_path: Path to semgrep executable
            pylint_path: Path to pylint executable
            timeout: Timeout for tool execution in seconds
            enable_cache: Enable result caching
            cache_ttl: Cache time-to-live in seconds
            enable_circuit_breaker: Enable circuit breaker for tool failures
        """
        self.ruff_path = ruff_path
        self.eslint_path = eslint_path
        self.mypy_path = mypy_path
        self.bandit_path = bandit_path
        self.dart_path = dart_path
        self.semgrep_path = semgrep_path
        self.pylint_path = pylint_path
        self.timeout = timeout
        self._tool_available: dict[ToolType, bool | None] = {}

        # Initialize cache
        self._cache: DiagnosticCache | None = None
        if enable_cache:
            self._cache = DiagnosticCache(ttl_seconds=cache_ttl)

        # Initialize circuit breaker
        self._circuit_breaker: CircuitBreaker | None = None
        if enable_circuit_breaker:
            self._circuit_breaker = CircuitBreaker()

        # Statistics
        self._stats = {
            "total_scans": 0,
            "tool_runs": {t.value: 0 for t in ToolType},
            "errors": 0,
        }

    async def check_tool_available(self, tool: ToolType) -> bool:
        """Check if a tool is available."""
        if tool in self._tool_available:
            return self._tool_available[tool] or False

        cmd_map = {
            ToolType.RUFF: [self.ruff_path, "--version"],
            ToolType.ESLINT: [self.eslint_path, "--version"],
            ToolType.MYPY: [self.mypy_path, "--version"],
            ToolType.BANDIT: [self.bandit_path, "--version"],
            ToolType.DART_ANALYZE: [self.dart_path, "--version"],
            ToolType.SEMGREP: [self.semgrep_path, "--version"],
            ToolType.PYLINT: [self.pylint_path, "--version"],
        }

        cmd = cmd_map.get(tool)
        if not cmd:
            self._tool_available[tool] = False
            return False

        # Check circuit breaker
        if self._circuit_breaker and not self._circuit_breaker.can_execute(tool.value):
            logger.warning(f"Circuit breaker open for {tool.value}")
            return False

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )
            await asyncio.wait_for(proc.wait(), timeout=5)
            available = proc.returncode == 0
            self._tool_available[tool] = available

            if self._circuit_breaker:
                if available:
                    self._circuit_breaker.record_success(tool.value)
                else:
                    self._circuit_breaker.record_failure(tool.value)

        except (TimeoutError, FileNotFoundError, OSError):
            self._tool_available[tool] = False
            if self._circuit_breaker:
                self._circuit_breaker.record_failure(tool.value)

        return self._tool_available[tool] or False

    def _get_file_tools(self, file_path: str) -> list[ToolType]:
        """Determine which tools to use for a file."""
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".py":
            # Return tools in order of priority/speed
            return [
                ToolType.RUFF,
                ToolType.BANDIT,
                ToolType.MYPY,
                ToolType.PYLINT,
                ToolType.SEMGREP,
            ]
        elif suffix in (".ts", ".tsx", ".js", ".jsx"):
            return [ToolType.ESLINT, ToolType.SEMGREP]
        elif suffix == ".dart":
            return [ToolType.DART_ANALYZE]
        elif suffix in (".go",):
            return [ToolType.SEMGREP]  # Semgrep supports Go
        elif suffix in (".java", ".kt"):
            return [ToolType.SEMGREP]  # Semgrep supports Java/Kotlin
        return []

    def get_statistics(self) -> dict[str, Any]:
        """Get diagnostic engine statistics."""
        stats = dict(self._stats)
        if self._cache:
            stats["cache"] = self._cache.get_stats()
        if self._circuit_breaker:
            stats["circuit_breaker"] = self._circuit_breaker.get_status()
        return stats

    async def diagnose_file(
        self,
        file_path: str,
        tools: list[ToolType] | None = None,
        use_cache: bool = True,
        include_security_patterns: bool = True,
    ) -> DiagnosticReport:
        """
        Diagnose a single file.

        تشخيص ملف واحد

        Args:
            file_path: Path to the file to diagnose
            tools: Specific tools to use (auto-detected if None)
            use_cache: Use cached results if available
            include_security_patterns: Run built-in security pattern detection

        Returns:
            DiagnosticReport with all found issues
        """
        if not os.path.exists(file_path):
            raise DiagnosticError(f"File not found: {file_path}")

        start_time = time.time()
        self._stats["total_scans"] += 1

        if tools is None:
            tools = self._get_file_tools(file_path)

        all_diagnostics: list[Diagnostic] = []
        used_tools: list[ToolType] = []

        for tool in tools:
            # Check cache first
            if use_cache and self._cache:
                cached = self._cache.get(file_path, tool)
                if cached is not None:
                    all_diagnostics.extend(cached)
                    used_tools.append(tool)
                    continue

            if not await self.check_tool_available(tool):
                continue

            used_tools.append(tool)
            self._stats["tool_runs"][tool.value] += 1
            diags: list[Diagnostic] = []

            try:
                if tool == ToolType.RUFF:
                    diags = await self._run_ruff(file_path)
                elif tool == ToolType.ESLINT:
                    diags = await self._run_eslint(file_path)
                elif tool == ToolType.MYPY:
                    diags = await self._run_mypy(file_path)
                elif tool == ToolType.BANDIT:
                    diags = await self._run_bandit(file_path)
                elif tool == ToolType.DART_ANALYZE:
                    diags = await self._run_dart_analyze(file_path)
                elif tool == ToolType.SEMGREP:
                    diags = await self._run_semgrep(file_path)
                elif tool == ToolType.PYLINT:
                    diags = await self._run_pylint(file_path)

                # Cache results
                if self._cache:
                    self._cache.set(file_path, tool, diags)

                # Record success in circuit breaker
                if self._circuit_breaker:
                    self._circuit_breaker.record_success(tool.value)

            except DiagnosticError as e:
                logger.warning(f"Tool {tool.value} failed: {e}")
                self._stats["errors"] += 1
                if self._circuit_breaker:
                    self._circuit_breaker.record_failure(tool.value)
                continue

            all_diagnostics.extend(diags)

        # Run built-in security pattern detection
        if include_security_patterns:
            security_diags = await self._run_security_patterns(file_path)
            all_diagnostics.extend(security_diags)

        duration = (time.time() - start_time) * 1000

        return DiagnosticReport(
            id=str(uuid.uuid4()),
            target=file_path,
            diagnostics=all_diagnostics,
            tools_used=used_tools,
            scan_duration_ms=duration,
        )

    async def diagnose_directory(
        self,
        directory: str,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        max_files: int = 100,
    ) -> DiagnosticReport:
        """
        Diagnose all files in a directory.

        تشخيص جميع الملفات في مجلد

        Args:
            directory: Directory path to diagnose
            include_patterns: Glob patterns to include
            exclude_patterns: Glob patterns to exclude
            max_files: Maximum number of files to process

        Returns:
            Combined DiagnosticReport
        """
        if not os.path.isdir(directory):
            raise DiagnosticError(f"Directory not found: {directory}")

        start_time = time.time()

        if include_patterns is None:
            include_patterns = ["*.py", "*.ts", "*.tsx", "*.js", "*.jsx", "*.dart"]
        if exclude_patterns is None:
            exclude_patterns = [
                "**/node_modules/**",
                "**/.venv/**",
                "**/__pycache__/**",
                "**/dist/**",
                "**/build/**",
            ]

        # Find files
        files: list[str] = []
        dir_path = Path(directory)

        for pattern in include_patterns:
            for file_path in dir_path.rglob(pattern):
                if len(files) >= max_files:
                    break

                # Check exclusions
                excluded = any(file_path.match(excl) for excl in exclude_patterns)
                if not excluded and file_path.is_file():
                    files.append(str(file_path))

        # Run diagnostics on all files concurrently
        tasks = [self.diagnose_file(f) for f in files]
        reports = await asyncio.gather(*tasks, return_exceptions=True)

        # Combine results
        all_diagnostics: list[Diagnostic] = []
        all_tools: set[ToolType] = set()

        for report in reports:
            if isinstance(report, DiagnosticReport):
                all_diagnostics.extend(report.diagnostics)
                all_tools.update(report.tools_used)

        duration = (time.time() - start_time) * 1000

        return DiagnosticReport(
            id=str(uuid.uuid4()),
            target=directory,
            diagnostics=all_diagnostics,
            tools_used=list(all_tools),
            scan_duration_ms=duration,
        )

    async def _run_ruff(self, file_path: str) -> list[Diagnostic]:
        """Run ruff on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.ruff_path,
                "check",
                "--output-format=json",
                "--no-fix",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for item in results:
                message = item.get("message", "Unknown error")
                rule_id = item.get("code", "")

                diag = Diagnostic(
                    id=str(uuid.uuid4()),
                    message=message,
                    message_ar=translate_message(message),
                    severity=get_severity_from_level("error" if rule_id.startswith(("E", "F")) else "warning"),
                    category=get_category_from_rule(rule_id, ToolType.RUFF),
                    location=CodeLocation(
                        file_path=item.get("filename", file_path),
                        line_start=item.get("location", {}).get("row", 1),
                        line_end=item.get("end_location", {}).get("row"),
                        column_start=item.get("location", {}).get("column"),
                        column_end=item.get("end_location", {}).get("column"),
                    ),
                    rule_id=rule_id,
                    tool=ToolType.RUFF,
                    suggestion=item.get("fix", {}).get("message"),
                    documentation_url=item.get("url"),
                )
                diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"Ruff execution failed: {e}") from e

    async def _run_eslint(self, file_path: str) -> list[Diagnostic]:
        """Run eslint on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.eslint_path,
                "--format=json",
                "--no-fix",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for file_result in results:
                for msg in file_result.get("messages", []):
                    message = msg.get("message", "Unknown error")
                    rule_id = msg.get("ruleId", "")
                    severity = "error" if msg.get("severity", 1) == 2 else "warning"

                    diag = Diagnostic(
                        id=str(uuid.uuid4()),
                        message=message,
                        message_ar=translate_message(message),
                        severity=get_severity_from_level(severity),
                        category=get_category_from_rule(rule_id, ToolType.ESLINT),
                        location=CodeLocation(
                            file_path=file_result.get("filePath", file_path),
                            line_start=msg.get("line", 1),
                            line_end=msg.get("endLine"),
                            column_start=msg.get("column"),
                            column_end=msg.get("endColumn"),
                        ),
                        rule_id=rule_id,
                        tool=ToolType.ESLINT,
                        suggestion=msg.get("suggestions", [{}])[0].get("desc") if msg.get("suggestions") else None,
                    )
                    diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"ESLint execution failed: {e}") from e

    async def _run_mypy(self, file_path: str) -> list[Diagnostic]:
        """Run mypy on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.mypy_path,
                "--output=json",
                "--no-error-summary",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            diagnostics: list[Diagnostic] = []

            for line in stdout.decode().strip().split("\n"):
                if not line:
                    continue
                try:
                    item = json.loads(line)
                    message = item.get("message", "Unknown type error")

                    diag = Diagnostic(
                        id=str(uuid.uuid4()),
                        message=message,
                        message_ar=translate_message(message),
                        severity=get_severity_from_level(item.get("severity", "error")),
                        category=DiagnosticCategory.TYPE,
                        location=CodeLocation(
                            file_path=item.get("file", file_path),
                            line_start=item.get("line", 1),
                            column_start=item.get("column"),
                        ),
                        rule_id=item.get("code"),
                        tool=ToolType.MYPY,
                    )
                    diagnostics.append(diag)
                except json.JSONDecodeError:
                    continue

            return diagnostics

        except (TimeoutError, OSError) as e:
            raise DiagnosticError(f"Mypy execution failed: {e}") from e

    async def _run_bandit(self, file_path: str) -> list[Diagnostic]:
        """Run bandit security scanner on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.bandit_path,
                "-f",
                "json",
                "-q",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for item in results.get("results", []):
                message = item.get("issue_text", "Security issue")

                diag = Diagnostic(
                    id=str(uuid.uuid4()),
                    message=message,
                    message_ar=translate_message(message),
                    severity=get_severity_from_level(item.get("issue_severity", "medium")),
                    category=DiagnosticCategory.SECURITY,
                    location=CodeLocation(
                        file_path=item.get("filename", file_path),
                        line_start=item.get("line_number", 1),
                        line_end=item.get("line_range", [1])[-1],
                    ),
                    rule_id=item.get("test_id"),
                    tool=ToolType.BANDIT,
                    source_code=item.get("code"),
                    documentation_url=item.get("more_info"),
                )
                diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"Bandit execution failed: {e}") from e

    async def _run_dart_analyze(self, file_path: str) -> list[Diagnostic]:
        """Run dart analyze on a file."""
        try:
            proc = await asyncio.create_subprocess_exec(
                self.dart_path,
                "analyze",
                "--format=json",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for item in results.get("diagnostics", []):
                message = item.get("problemMessage", "Dart analysis issue")
                severity = item.get("severity", "WARNING").lower()

                diag = Diagnostic(
                    id=str(uuid.uuid4()),
                    message=message,
                    message_ar=translate_message(message),
                    severity=get_severity_from_level(severity),
                    category=get_category_from_rule(item.get("code", ""), ToolType.DART_ANALYZE),
                    location=CodeLocation(
                        file_path=item.get("location", {}).get("file", file_path),
                        line_start=item.get("location", {}).get("startLine", 1),
                        line_end=item.get("location", {}).get("endLine"),
                        column_start=item.get("location", {}).get("startColumn"),
                        column_end=item.get("location", {}).get("endColumn"),
                    ),
                    rule_id=item.get("code"),
                    tool=ToolType.DART_ANALYZE,
                    suggestion=item.get("correctionMessage"),
                    documentation_url=item.get("documentation"),
                )
                diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"Dart analyze execution failed: {e}") from e

    async def _run_semgrep(self, file_path: str) -> list[Diagnostic]:
        """
        Run Semgrep security scanner on a file.

        تشغيل ماسح Semgrep الأمني على ملف

        Semgrep provides pattern-based security scanning with
        support for multiple languages and OWASP rule sets.
        """
        try:
            # Determine language config
            suffix = Path(file_path).suffix.lower()
            {
                ".py": "python",
                ".js": "javascript",
                ".ts": "typescript",
                ".tsx": "typescript",
                ".jsx": "javascript",
                ".go": "go",
                ".java": "java",
                ".kt": "kotlin",
                ".rb": "ruby",
                ".php": "php",
            }.get(suffix, "generic")

            proc = await asyncio.create_subprocess_exec(
                self.semgrep_path,
                "scan",
                "--json",
                "--config=auto",  # Use automatic rule detection
                "--quiet",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for item in results.get("results", []):
                message = item.get("extra", {}).get("message", "Security issue")
                severity = item.get("extra", {}).get("severity", "WARNING").lower()
                rule_id = item.get("check_id", "")

                # Map Semgrep severity
                if severity in ("error", "high"):
                    diag_severity = DiagnosticSeverity.ERROR
                elif severity in ("warning", "medium"):
                    diag_severity = DiagnosticSeverity.WARNING
                else:
                    diag_severity = DiagnosticSeverity.INFO

                # Determine category from rule ID
                category = DiagnosticCategory.SECURITY
                if "sql" in rule_id.lower() or "xss" in rule_id.lower():
                    category = DiagnosticCategory.SECURITY
                elif "perf" in rule_id.lower():
                    category = DiagnosticCategory.PERFORMANCE

                diag = Diagnostic(
                    id=str(uuid.uuid4()),
                    message=message,
                    message_ar=translate_message(message),
                    severity=diag_severity,
                    category=category,
                    location=CodeLocation(
                        file_path=item.get("path", file_path),
                        line_start=item.get("start", {}).get("line", 1),
                        line_end=item.get("end", {}).get("line"),
                        column_start=item.get("start", {}).get("col"),
                        column_end=item.get("end", {}).get("col"),
                    ),
                    rule_id=rule_id,
                    tool=ToolType.SEMGREP,
                    source_code=item.get("extra", {}).get("lines"),
                    suggestion=item.get("extra", {}).get("fix"),
                    documentation_url=item.get("extra", {}).get("metadata", {}).get("source"),
                )
                diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"Semgrep execution failed: {e}") from e

    async def _run_pylint(self, file_path: str) -> list[Diagnostic]:
        """
        Run Pylint on a Python file.

        تشغيل Pylint على ملف Python

        Pylint provides advanced code analysis including:
        - Code complexity
        - Design patterns
        - Documentation completeness
        - Convention adherence
        """
        try:
            proc = await asyncio.create_subprocess_exec(
                self.pylint_path,
                "--output-format=json",
                "--disable=C0114,C0115,C0116",  # Disable docstring warnings (handled by other tools)
                "--max-line-length=120",
                file_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(
                proc.communicate(),
                timeout=self.timeout,
            )

            if not stdout:
                return []

            results = json.loads(stdout.decode())
            diagnostics: list[Diagnostic] = []

            for item in results:
                message = item.get("message", "Pylint issue")
                msg_id = item.get("message-id", "")
                symbol = item.get("symbol", "")

                # Map Pylint message types to severity
                msg_type = item.get("type", "convention")
                if msg_type == "error":
                    severity = DiagnosticSeverity.ERROR
                elif msg_type == "warning":
                    severity = DiagnosticSeverity.WARNING
                elif msg_type == "refactor":
                    severity = DiagnosticSeverity.INFO
                else:  # convention
                    severity = DiagnosticSeverity.HINT

                # Map to category
                category = self._get_pylint_category(msg_id, symbol)

                diag = Diagnostic(
                    id=str(uuid.uuid4()),
                    message=f"{message} ({symbol})",
                    message_ar=translate_message(message),
                    severity=severity,
                    category=category,
                    location=CodeLocation(
                        file_path=item.get("path", file_path),
                        line_start=item.get("line", 1),
                        line_end=item.get("endLine"),
                        column_start=item.get("column"),
                        column_end=item.get("endColumn"),
                    ),
                    rule_id=msg_id,
                    tool=ToolType.PYLINT,
                )
                diagnostics.append(diag)

            return diagnostics

        except (TimeoutError, json.JSONDecodeError, OSError) as e:
            raise DiagnosticError(f"Pylint execution failed: {e}") from e

    def _get_pylint_category(self, msg_id: str, symbol: str) -> DiagnosticCategory:
        """Map Pylint message to diagnostic category."""
        # Error categories (E)
        if msg_id.startswith("E"):
            if "syntax" in symbol:
                return DiagnosticCategory.SYNTAX
            elif "import" in symbol:
                return DiagnosticCategory.IMPORT
            return DiagnosticCategory.LOGIC

        # Warning categories (W)
        if msg_id.startswith("W"):
            if "unused" in symbol:
                return DiagnosticCategory.LOGIC
            elif "deprecated" in symbol:
                return DiagnosticCategory.DEPRECATION
            return DiagnosticCategory.BEST_PRACTICE

        # Refactor categories (R)
        if msg_id.startswith("R"):
            return DiagnosticCategory.PERFORMANCE

        # Convention categories (C)
        if msg_id.startswith("C"):
            if "name" in symbol:
                return DiagnosticCategory.NAMING
            return DiagnosticCategory.STYLE

        return DiagnosticCategory.LOGIC

    async def _run_security_patterns(self, file_path: str) -> list[Diagnostic]:
        """
        Run built-in security pattern detection.

        تشغيل كشف أنماط الأمان المدمج

        Provides fast, offline security scanning using regex patterns
        for common vulnerabilities (OWASP Top 10, CWE).
        """
        diagnostics: list[Diagnostic] = []

        # Read file content
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()
        except (FileNotFoundError, OSError):
            return diagnostics

        # Determine language
        suffix = Path(file_path).suffix.lower()
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
        }
        language = language_map.get(suffix, "unknown")

        # Check each security pattern
        for pattern in SECURITY_PATTERNS:
            # Skip patterns not applicable to this language
            if language not in pattern.languages:
                continue

            try:
                for match in re.finditer(pattern.pattern, content):
                    # Calculate line number
                    line_num = content[: match.start()].count("\n") + 1
                    col_start = match.start() - content.rfind("\n", 0, match.start()) - 1

                    # Map severity
                    severity_map = {
                        "critical": DiagnosticSeverity.ERROR,
                        "high": DiagnosticSeverity.ERROR,
                        "medium": DiagnosticSeverity.WARNING,
                        "low": DiagnosticSeverity.INFO,
                    }
                    severity = severity_map.get(pattern.severity, DiagnosticSeverity.WARNING)

                    diag = Diagnostic(
                        id=str(uuid.uuid4()),
                        message=pattern.message,
                        message_ar=pattern.message_ar,
                        severity=severity,
                        category=DiagnosticCategory.SECURITY,
                        location=CodeLocation(
                            file_path=file_path,
                            line_start=line_num,
                            line_end=line_num,
                            column_start=col_start,
                            column_end=col_start + len(match.group()),
                        ),
                        rule_id=pattern.id,
                        tool=ToolType.SEMGREP,  # Use SEMGREP as the tool type for consistency
                        source_code=match.group(),
                        suggestion=pattern.suggestion,
                        suggestion_ar=pattern.suggestion_ar,
                        documentation_url=f"https://cwe.mitre.org/data/definitions/{pattern.cwe[4:]}.html"
                        if pattern.cwe
                        else None,
                    )
                    diagnostics.append(diag)

            except re.error as e:
                logger.warning(f"Invalid regex pattern {pattern.id}: {e}")
                continue

        return diagnostics

    def format_report_markdown(
        self,
        report: DiagnosticReport,
        include_arabic: bool = True,
    ) -> str:
        """
        Format diagnostic report as markdown.

        تنسيق تقرير التشخيص كـ Markdown

        Args:
            report: The diagnostic report to format
            include_arabic: Include Arabic translations

        Returns:
            Formatted markdown string
        """
        lines = [
            "# Code Diagnostic Report | تقرير تشخيص الكود",
            "",
            f"**Target | الهدف**: `{report.target}`",
            f"**Scan Time | وقت الفحص**: {report.scan_duration_ms:.2f}ms",
            f"**Tools Used | الأدوات**: {', '.join(t.value for t in report.tools_used)}",
            "",
            "## Summary | ملخص",
            "",
            "| Severity | Count |",
            "|----------|-------|",
            f"| 🔴 Errors | {report.total_errors} |",
            f"| 🟠 Warnings | {report.total_warnings} |",
            f"| 🔵 Info | {report.total_info} |",
            f"| ⚪ Hints | {report.total_hints} |",
            "",
            "## Issues | المشاكل",
            "",
        ]

        severity_icons = {
            DiagnosticSeverity.ERROR: "🔴",
            DiagnosticSeverity.WARNING: "🟠",
            DiagnosticSeverity.INFO: "🔵",
            DiagnosticSeverity.HINT: "⚪",
        }

        for diag in report.diagnostics:
            icon = severity_icons.get(diag.severity, "⚪")
            lines.append(f"### {icon} {diag.rule_id or 'Unknown'}")
            lines.append("")
            lines.append(f"**Location**: `{diag.location}`")
            lines.append(f"**Message**: {diag.message}")

            if include_arabic and diag.message_ar:
                lines.append(f"**الرسالة**: {diag.message_ar}")

            if diag.suggestion:
                lines.append(f"**Suggestion**: {diag.suggestion}")

            if diag.documentation_url:
                lines.append(f"**Docs**: [{diag.rule_id}]({diag.documentation_url})")

            lines.append("")

        return "\n".join(lines)
