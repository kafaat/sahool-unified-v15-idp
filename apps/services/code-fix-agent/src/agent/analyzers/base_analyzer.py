"""
SAHOOL Code Fix Agent - Base Analyzer
المحلل الأساسي

Abstract base class for language-specific analyzers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class IssueSeverity(Enum):
    """شدة المشكلة"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    HINT = "hint"


class IssueCategory(Enum):
    """فئة المشكلة"""
    SYNTAX = "syntax"
    TYPE = "type"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    LOGIC = "logic"
    DEPRECATION = "deprecation"
    BEST_PRACTICE = "best_practice"


@dataclass
class AnalysisConfig:
    """
    إعدادات التحليل
    Analysis configuration
    """
    # Severity levels to check
    check_errors: bool = True
    check_warnings: bool = True
    check_info: bool = False
    check_hints: bool = False

    # Categories to check
    check_syntax: bool = True
    check_types: bool = True
    check_security: bool = True
    check_performance: bool = True
    check_style: bool = False
    check_logic: bool = True

    # Limits
    max_issues: int = 100
    max_line_length: int = 120
    max_complexity: int = 10

    # Language-specific settings
    language_config: dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisIssue:
    """
    مشكلة في الكود
    Code issue
    """
    # Location
    file_path: str
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0

    # Issue details
    severity: IssueSeverity = IssueSeverity.WARNING
    category: IssueCategory = IssueCategory.LOGIC
    code: str = ""
    message: str = ""
    message_ar: str = ""

    # Context
    source_code: str = ""
    suggestion: str = ""
    suggestion_ar: str = ""

    # Fix
    fix_available: bool = False
    fix_code: str | None = None

    # Metadata
    rule_id: str | None = None
    confidence: float = 0.8
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "file_path": self.file_path,
            "line_start": self.line_start,
            "line_end": self.line_end,
            "column_start": self.column_start,
            "column_end": self.column_end,
            "severity": self.severity.value,
            "category": self.category.value,
            "code": self.code,
            "message": self.message,
            "message_ar": self.message_ar,
            "source_code": self.source_code,
            "suggestion": self.suggestion,
            "suggestion_ar": self.suggestion_ar,
            "fix_available": self.fix_available,
            "rule_id": self.rule_id,
            "confidence": self.confidence,
        }


@dataclass
class AnalysisResult:
    """
    نتيجة التحليل
    Analysis result
    """
    success: bool
    language: str
    file_path: str
    issues: list[AnalysisIssue] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    analysis_time_ms: float = 0.0
    analyzer_version: str = "1.0.0"
    error: str | None = None

    @property
    def error_count(self) -> int:
        return len([i for i in self.issues if i.severity == IssueSeverity.ERROR])

    @property
    def warning_count(self) -> int:
        return len([i for i in self.issues if i.severity == IssueSeverity.WARNING])

    def to_dict(self) -> dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "success": self.success,
            "language": self.language,
            "file_path": self.file_path,
            "issues": [i.to_dict() for i in self.issues],
            "issue_count": len(self.issues),
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "metrics": self.metrics,
            "analysis_time_ms": self.analysis_time_ms,
            "analyzer_version": self.analyzer_version,
            "error": self.error,
        }


class BaseAnalyzer(ABC):
    """
    المحلل الأساسي
    Base Analyzer

    Abstract base class for all language analyzers.
    """

    LANGUAGE: str = "unknown"
    VERSION: str = "1.0.0"

    def __init__(self, config: AnalysisConfig | None = None):
        """
        تهيئة المحلل

        Args:
            config: إعدادات التحليل
        """
        self.config = config or AnalysisConfig()
        logger.debug("analyzer_initialized", language=self.LANGUAGE)

    @abstractmethod
    async def analyze(self, code: str, file_path: str = "<string>") -> AnalysisResult:
        """
        تحليل الكود
        Analyze code

        Args:
            code: الكود المصدري
            file_path: مسار الملف

        Returns:
            نتيجة التحليل
        """
        pass

    @abstractmethod
    async def check_syntax(self, code: str) -> list[AnalysisIssue]:
        """
        التحقق من بناء الجملة
        Check syntax
        """
        pass

    @abstractmethod
    async def check_types(self, code: str) -> list[AnalysisIssue]:
        """
        التحقق من الأنواع
        Check types
        """
        pass

    @abstractmethod
    async def check_security(self, code: str) -> list[AnalysisIssue]:
        """
        التحقق من الأمان
        Check security
        """
        pass

    @abstractmethod
    async def check_style(self, code: str) -> list[AnalysisIssue]:
        """
        التحقق من الأسلوب
        Check style
        """
        pass

    def _should_include_issue(self, issue: AnalysisIssue) -> bool:
        """التحقق من تضمين المشكلة"""
        # Check severity
        if issue.severity == IssueSeverity.ERROR and not self.config.check_errors:
            return False
        if issue.severity == IssueSeverity.WARNING and not self.config.check_warnings:
            return False
        if issue.severity == IssueSeverity.INFO and not self.config.check_info:
            return False
        if issue.severity == IssueSeverity.HINT and not self.config.check_hints:
            return False

        # Check category
        if issue.category == IssueCategory.SYNTAX and not self.config.check_syntax:
            return False
        if issue.category == IssueCategory.TYPE and not self.config.check_types:
            return False
        if issue.category == IssueCategory.SECURITY and not self.config.check_security:
            return False
        if issue.category == IssueCategory.PERFORMANCE and not self.config.check_performance:
            return False
        if issue.category == IssueCategory.STYLE and not self.config.check_style:
            return False

        return True
