"""
Auto-Fix Models
===============
نماذج البيانات لمحرك الإصلاح التلقائي

Data models for the auto-fix engine including diagnostics,
fixes, and audit integration.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any


class DiagnosticSeverity(StrEnum):
    """Severity levels for diagnostics."""

    ERROR = "error"  # خطأ - يجب إصلاحه
    WARNING = "warning"  # تحذير - يُفضل إصلاحه
    INFO = "info"  # معلومات - للتحسين
    HINT = "hint"  # تلميح - اختياري


class DiagnosticCategory(StrEnum):
    """Categories of code diagnostics."""

    SYNTAX = "syntax"  # أخطاء بناء الجملة
    TYPE = "type"  # أخطاء الأنواع
    SECURITY = "security"  # ثغرات أمنية
    PERFORMANCE = "performance"  # مشاكل الأداء
    STYLE = "style"  # مشاكل التنسيق
    BEST_PRACTICE = "best_practice"  # أفضل الممارسات
    DEPRECATION = "deprecation"  # استخدام مهمل
    LOGIC = "logic"  # أخطاء منطقية
    IMPORT = "import"  # مشاكل الاستيراد
    NAMING = "naming"  # مشاكل التسمية


class FixStrategy(StrEnum):
    """Strategy for applying fixes."""

    MINIMAL = "minimal"  # أقل تغيير ممكن
    SAFE = "safe"  # تغييرات آمنة فقط
    COMPREHENSIVE = "comprehensive"  # تغييرات شاملة
    REFACTOR = "refactor"  # إعادة هيكلة كاملة


class FixConfidence(StrEnum):
    """Confidence level for a fix."""

    HIGH = "high"  # ثقة عالية (>90%)
    MEDIUM = "medium"  # ثقة متوسطة (70-90%)
    LOW = "low"  # ثقة منخفضة (<70%)


class ToolType(StrEnum):
    """Types of linting/analysis tools."""

    # Layer 1: Code Quality & Static Analysis | جودة الكود والتحليل الثابت
    RUFF = "ruff"  # Python linter/formatter
    ESLINT = "eslint"  # JavaScript/TypeScript linter
    BIOME = "biome"  # Fast unified linter + formatter
    OXLINT = "oxlint"  # Ultra-fast JS linter (Rust)
    PYLINT = "pylint"  # Python deep linter

    # Layer 2: Type Checking | فحص الأنواع
    MYPY = "mypy"  # Python type checker
    PYRIGHT = "pyright"  # Python type checker (fast)
    TYPESCRIPT = "typescript"  # TypeScript compiler

    # Layer 3: Security SAST | فحص الأمان
    BANDIT = "bandit"  # Python security linter
    SEMGREP = "semgrep"  # Pattern-based scanner
    CODEQL = "codeql"  # Semantic security analysis
    TRIVY = "trivy"  # Container & config scanner

    # Layer 4: Dependency & Supply Chain | التبعيات وسلسلة التوريد
    NPM_AUDIT = "npm_audit"  # npm vulnerability audit
    PIP_AUDIT = "pip_audit"  # Python dependency audit

    # Layer 5: Architecture & Dependencies | الهندسة المعمارية والتبعيات
    KNIP = "knip"  # Dead code detection (JS/TS)
    MADGE = "madge"  # Circular dependency detection
    DEPCHECK = "depcheck"  # Unused dependency detection
    VULTURE = "vulture"  # Dead code detection (Python)
    RADON = "radon"  # Code complexity analysis (Python)

    # Layer 6: Mobile | التطبيق المحمول
    DART_ANALYZE = "dart_analyze"  # Dart/Flutter analyzer

    # Layer 7: Container & Infrastructure | الحاويات والبنية التحتية
    HADOLINT = "hadolint"  # Dockerfile linter
    DETECT_SECRETS = "detect_secrets"  # Secret detection


class QualityLayer(StrEnum):
    """Quality analysis layers for enterprise platforms."""

    LINT_FORMAT = "lint_format"  # الطبقة 1: التنسيق والتدقيق
    TYPE_CHECK = "type_check"  # الطبقة 2: فحص الأنواع
    SECURITY_SAST = "security_sast"  # الطبقة 3: الأمان
    DEPENDENCY_SECURITY = "dependency_security"  # الطبقة 4: أمان التبعيات
    ARCHITECTURE = "architecture"  # الطبقة 5: الهندسة المعمارية
    DEAD_CODE = "dead_code"  # الطبقة 6: الكود الميت والتعقيد
    TESTING = "testing"  # الطبقة 7: الاختبارات
    CONTAINER = "container"  # الطبقة 8: الحاويات والبنية التحتية


@dataclass
class CodeLocation:
    """Location of code in a file."""

    file_path: str
    line_start: int
    line_end: int | None = None
    column_start: int | None = None
    column_end: int | None = None

    def __str__(self) -> str:
        """Format location as string."""
        loc = f"{self.file_path}:{self.line_start}"
        if self.column_start:
            loc += f":{self.column_start}"
        if self.line_end and self.line_end != self.line_start:
            loc += f"-{self.line_end}"
        return loc


@dataclass
class Diagnostic:
    """A code diagnostic (error, warning, etc.)."""

    id: str
    message: str
    message_ar: str  # Arabic message
    severity: DiagnosticSeverity
    category: DiagnosticCategory
    location: CodeLocation
    rule_id: str | None = None
    tool: ToolType | None = None
    source_code: str | None = None
    suggestion: str | None = None
    suggestion_ar: str | None = None
    documentation_url: str | None = None
    related_diagnostics: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "message": self.message,
            "message_ar": self.message_ar,
            "severity": self.severity.value,
            "category": self.category.value,
            "location": {
                "file_path": self.location.file_path,
                "line_start": self.location.line_start,
                "line_end": self.location.line_end,
                "column_start": self.location.column_start,
                "column_end": self.location.column_end,
            },
            "rule_id": self.rule_id,
            "tool": self.tool.value if self.tool else None,
            "source_code": self.source_code,
            "suggestion": self.suggestion,
            "suggestion_ar": self.suggestion_ar,
            "documentation_url": self.documentation_url,
            "related_diagnostics": self.related_diagnostics,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class CodeFix:
    """A proposed fix for a diagnostic."""

    id: str
    diagnostic_id: str
    description: str
    description_ar: str
    original_code: str
    fixed_code: str
    strategy: FixStrategy
    confidence: FixConfidence
    is_safe: bool = True
    requires_review: bool = False
    breaking_change: bool = False
    test_required: bool = False
    related_fixes: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "diagnostic_id": self.diagnostic_id,
            "description": self.description,
            "description_ar": self.description_ar,
            "original_code": self.original_code,
            "fixed_code": self.fixed_code,
            "strategy": self.strategy.value,
            "confidence": self.confidence.value,
            "is_safe": self.is_safe,
            "requires_review": self.requires_review,
            "breaking_change": self.breaking_change,
            "test_required": self.test_required,
            "related_fixes": self.related_fixes,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class FixResult:
    """Result of applying a fix."""

    fix_id: str
    success: bool
    applied_at: datetime
    file_path: str
    backup_path: str | None = None
    error_message: str | None = None
    verification_passed: bool | None = None
    rollback_available: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "fix_id": self.fix_id,
            "success": self.success,
            "applied_at": self.applied_at.isoformat(),
            "file_path": self.file_path,
            "backup_path": self.backup_path,
            "error_message": self.error_message,
            "verification_passed": self.verification_passed,
            "rollback_available": self.rollback_available,
        }


@dataclass
class DiagnosticReport:
    """A report of diagnostics for a codebase or file."""

    id: str
    target: str  # File or directory path
    diagnostics: list[Diagnostic]
    total_errors: int = 0
    total_warnings: int = 0
    total_info: int = 0
    total_hints: int = 0
    tools_used: list[ToolType] = field(default_factory=list)
    scan_duration_ms: float = 0.0
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        """Calculate totals from diagnostics."""
        self.total_errors = sum(1 for d in self.diagnostics if d.severity == DiagnosticSeverity.ERROR)
        self.total_warnings = sum(1 for d in self.diagnostics if d.severity == DiagnosticSeverity.WARNING)
        self.total_info = sum(1 for d in self.diagnostics if d.severity == DiagnosticSeverity.INFO)
        self.total_hints = sum(1 for d in self.diagnostics if d.severity == DiagnosticSeverity.HINT)

    @property
    def has_errors(self) -> bool:
        """Check if report has any errors."""
        return self.total_errors > 0

    @property
    def has_issues(self) -> bool:
        """Check if report has any issues."""
        return len(self.diagnostics) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "target": self.target,
            "diagnostics": [d.to_dict() for d in self.diagnostics],
            "summary": {
                "total_errors": self.total_errors,
                "total_warnings": self.total_warnings,
                "total_info": self.total_info,
                "total_hints": self.total_hints,
                "total_issues": len(self.diagnostics),
            },
            "tools_used": [t.value for t in self.tools_used],
            "scan_duration_ms": self.scan_duration_ms,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class FixPlan:
    """A plan for applying multiple fixes."""

    id: str
    diagnostic_report_id: str
    fixes: list[CodeFix]
    strategy: FixStrategy
    total_fixes: int = 0
    safe_fixes: int = 0
    review_required: int = 0
    estimated_impact: str | None = None
    estimated_impact_ar: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self):
        """Calculate fix statistics."""
        self.total_fixes = len(self.fixes)
        self.safe_fixes = sum(1 for f in self.fixes if f.is_safe)
        self.review_required = sum(1 for f in self.fixes if f.requires_review)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "diagnostic_report_id": self.diagnostic_report_id,
            "fixes": [f.to_dict() for f in self.fixes],
            "strategy": self.strategy.value,
            "summary": {
                "total_fixes": self.total_fixes,
                "safe_fixes": self.safe_fixes,
                "review_required": self.review_required,
            },
            "estimated_impact": self.estimated_impact,
            "estimated_impact_ar": self.estimated_impact_ar,
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class AuditEntry:
    """Audit log entry for fix operations."""

    id: str
    action: str  # diagnose, fix_planned, fix_applied, fix_rolled_back
    actor: str  # user_id or system
    target: str  # file or directory
    details: dict[str, Any]
    severity: DiagnosticSeverity | None = None
    success: bool = True
    error: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "action": self.action,
            "actor": self.actor,
            "target": self.target,
            "details": self.details,
            "severity": self.severity.value if self.severity else None,
            "success": self.success,
            "error": self.error,
            "timestamp": self.timestamp.isoformat(),
        }
