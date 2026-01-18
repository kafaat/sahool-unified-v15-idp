"""
SAHOOL Code Fix Agent - Dart Analyzer
محلل Dart

Dart/Flutter code analyzer with:
- Syntax checking
- Type checking patterns
- Security analysis
- Flutter best practices
"""

import re
import time
from typing import Any

import structlog

from .base_analyzer import (
    AnalysisConfig,
    AnalysisIssue,
    AnalysisResult,
    BaseAnalyzer,
    IssueCategory,
    IssueSeverity,
)

logger = structlog.get_logger(__name__)


class DartAnalyzer(BaseAnalyzer):
    """
    محلل Dart
    Dart/Flutter Analyzer
    """

    LANGUAGE = "dart"
    VERSION = "1.0.0"

    # Security patterns
    SECURITY_PATTERNS = [
        {
            "pattern": r"http://(?!localhost)",
            "code": "D001",
            "message": "Use HTTPS instead of HTTP",
            "message_ar": "استخدم HTTPS بدلاً من HTTP",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"print\s*\(",
            "code": "D002",
            "message": "Use debugPrint or logging instead of print",
            "message_ar": "استخدم debugPrint أو logging بدلاً من print",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"(?:password|secret|api_key|token)\s*[:=]\s*['\"][^'\"]+['\"]",
            "code": "D003",
            "message": "Hardcoded secret detected",
            "message_ar": "تم اكتشاف سر ثابت",
            "severity": IssueSeverity.ERROR,
        },
    ]

    # Style patterns
    STYLE_PATTERNS = [
        {
            "pattern": r"^\s*var\s+\w+\s*=",
            "code": "D101",
            "message": "Prefer explicit type annotation over 'var'",
            "message_ar": "يفضل التعليق التوضيحي الصريح للنوع بدلاً من 'var'",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"//\s*TODO",
            "code": "D110",
            "message": "TODO comment found",
            "message_ar": "تم العثور على تعليق TODO",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"//\s*FIXME",
            "code": "D111",
            "message": "FIXME comment found",
            "message_ar": "تم العثور على تعليق FIXME",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"dynamic\s+\w+",
            "code": "D102",
            "message": "Avoid using 'dynamic' type",
            "message_ar": "تجنب استخدام نوع 'dynamic'",
            "severity": IssueSeverity.WARNING,
        },
    ]

    # Flutter-specific patterns
    FLUTTER_PATTERNS = [
        {
            "pattern": r"setState\s*\(\s*\(\s*\)\s*{[^}]*\}\s*\)",
            "code": "F001",
            "message": "Empty setState call",
            "message_ar": "استدعاء setState فارغ",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"Container\s*\([^)]*\)",
            "code": "F002",
            "message": "Consider using SizedBox or DecoratedBox instead of Container",
            "message_ar": "فكر في استخدام SizedBox أو DecoratedBox بدلاً من Container",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"Column\s*\([^)]*children:\s*\[[^\]]*Expanded",
            "code": "F003",
            "message": "Consider using Flexible instead of Expanded in Column",
            "message_ar": "فكر في استخدام Flexible بدلاً من Expanded في Column",
            "severity": IssueSeverity.INFO,
        },
    ]

    async def analyze(self, code: str, file_path: str = "<string>") -> AnalysisResult:
        """تحليل كود Dart"""
        start_time = time.time()
        issues: list[AnalysisIssue] = []

        try:
            # Syntax check
            if self.config.check_syntax:
                syntax_issues = await self.check_syntax(code)
                issues.extend(syntax_issues)

            # Type check
            if self.config.check_types:
                type_issues = await self.check_types(code)
                issues.extend(type_issues)

            # Security check
            if self.config.check_security:
                security_issues = await self.check_security(code)
                issues.extend(security_issues)

            # Style check
            if self.config.check_style:
                style_issues = await self.check_style(code)
                issues.extend(style_issues)

            # Flutter-specific checks
            flutter_issues = await self.check_flutter_patterns(code)
            issues.extend(flutter_issues)

            # Calculate metrics
            metrics = self._calculate_metrics(code)

            # Filter and limit issues
            filtered_issues = [i for i in issues if self._should_include_issue(i)]
            if len(filtered_issues) > self.config.max_issues:
                filtered_issues = filtered_issues[:self.config.max_issues]

            return AnalysisResult(
                success=True,
                language=self.LANGUAGE,
                file_path=file_path,
                issues=filtered_issues,
                metrics=metrics,
                analysis_time_ms=(time.time() - start_time) * 1000,
                analyzer_version=self.VERSION,
            )

        except Exception as e:
            logger.error("dart_analysis_error", error=str(e))
            return AnalysisResult(
                success=False,
                language=self.LANGUAGE,
                file_path=file_path,
                issues=issues,
                analysis_time_ms=(time.time() - start_time) * 1000,
                analyzer_version=self.VERSION,
                error=str(e),
            )

    async def check_syntax(self, code: str) -> list[AnalysisIssue]:
        """التحقق من بناء الجملة"""
        issues: list[AnalysisIssue] = []
        lines = code.split("\n")

        # Check for unclosed brackets
        brackets = {"(": ")", "[": "]", "{": "}"}
        stack: list[tuple[str, int]] = []

        for i, line in enumerate(lines, 1):
            # Skip string contents
            in_string = False
            string_char = None

            for j, char in enumerate(line):
                if char in "\"'" and (j == 0 or line[j-1] != "\\"):
                    if not in_string:
                        in_string = True
                        string_char = char
                    elif char == string_char:
                        in_string = False
                        string_char = None
                    continue

                if in_string:
                    continue

                if char in brackets:
                    stack.append((char, i))
                elif char in brackets.values():
                    if stack:
                        open_bracket, _ = stack.pop()
                        if brackets[open_bracket] != char:
                            issues.append(AnalysisIssue(
                                file_path="<string>",
                                line_start=i,
                                line_end=i,
                                column_start=j,
                                severity=IssueSeverity.ERROR,
                                category=IssueCategory.SYNTAX,
                                code="DS001",
                                message=f"Mismatched bracket: expected '{brackets[open_bracket]}' but found '{char}'",
                                message_ar=f"قوس غير متطابق",
                            ))

        return issues

    async def check_types(self, code: str) -> list[AnalysisIssue]:
        """التحقق من الأنواع"""
        issues: list[AnalysisIssue] = []
        lines = code.split("\n")

        # Check for dynamic type usage
        dynamic_pattern = re.compile(r"\bdynamic\b")
        for i, line in enumerate(lines, 1):
            if dynamic_pattern.search(line):
                issues.append(AnalysisIssue(
                    file_path="<string>",
                    line_start=i,
                    line_end=i,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.TYPE,
                    code="DT001",
                    message="Avoid using 'dynamic' type",
                    message_ar="تجنب استخدام نوع 'dynamic'",
                    source_code=line.strip(),
                ))

        # Check for missing type annotations
        var_pattern = re.compile(r"^\s*var\s+(\w+)\s*=")
        for i, line in enumerate(lines, 1):
            match = var_pattern.search(line)
            if match:
                issues.append(AnalysisIssue(
                    file_path="<string>",
                    line_start=i,
                    line_end=i,
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.TYPE,
                    code="DT002",
                    message=f"Consider using explicit type for '{match.group(1)}'",
                    message_ar=f"فكر في استخدام نوع صريح لـ '{match.group(1)}'",
                    source_code=line.strip(),
                ))

        return issues

    async def check_security(self, code: str) -> list[AnalysisIssue]:
        """التحقق من الأمان"""
        issues: list[AnalysisIssue] = []
        lines = code.split("\n")

        for pattern_info in self.SECURITY_PATTERNS:
            pattern = re.compile(pattern_info["pattern"], re.IGNORECASE)
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    issues.append(AnalysisIssue(
                        file_path="<string>",
                        line_start=i,
                        line_end=i,
                        severity=pattern_info["severity"],
                        category=IssueCategory.SECURITY,
                        code=pattern_info["code"],
                        message=pattern_info["message"],
                        message_ar=pattern_info["message_ar"],
                        source_code=line.strip(),
                        confidence=0.9,
                    ))

        return issues

    async def check_style(self, code: str) -> list[AnalysisIssue]:
        """التحقق من الأسلوب"""
        issues: list[AnalysisIssue] = []
        lines = code.split("\n")

        # Line length check
        for i, line in enumerate(lines, 1):
            if len(line) > self.config.max_line_length:
                issues.append(AnalysisIssue(
                    file_path="<string>",
                    line_start=i,
                    line_end=i,
                    severity=IssueSeverity.INFO,
                    category=IssueCategory.STYLE,
                    code="DS501",
                    message=f"Line too long ({len(line)} > {self.config.max_line_length})",
                    message_ar=f"السطر طويل جداً",
                ))

        # Pattern-based style checks
        for pattern_info in self.STYLE_PATTERNS:
            pattern = re.compile(pattern_info["pattern"])
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    issues.append(AnalysisIssue(
                        file_path="<string>",
                        line_start=i,
                        line_end=i,
                        severity=pattern_info["severity"],
                        category=IssueCategory.STYLE,
                        code=pattern_info["code"],
                        message=pattern_info["message"],
                        message_ar=pattern_info["message_ar"],
                        source_code=line.strip(),
                    ))

        return issues

    async def check_flutter_patterns(self, code: str) -> list[AnalysisIssue]:
        """التحقق من أنماط Flutter"""
        issues: list[AnalysisIssue] = []
        lines = code.split("\n")

        # Check if this is a Flutter file
        if "flutter" not in code.lower() and "widget" not in code.lower():
            return issues

        for pattern_info in self.FLUTTER_PATTERNS:
            pattern = re.compile(pattern_info["pattern"], re.DOTALL)
            for match in pattern.finditer(code):
                line_num = code[:match.start()].count("\n") + 1
                issues.append(AnalysisIssue(
                    file_path="<string>",
                    line_start=line_num,
                    line_end=line_num,
                    severity=pattern_info["severity"],
                    category=IssueCategory.BEST_PRACTICE,
                    code=pattern_info["code"],
                    message=pattern_info["message"],
                    message_ar=pattern_info["message_ar"],
                ))

        return issues

    def _calculate_metrics(self, code: str) -> dict[str, Any]:
        """حساب المقاييس"""
        lines = code.split("\n")

        # Count classes
        class_pattern = re.compile(r"\bclass\s+\w+")
        classes = sum(1 for line in lines if class_pattern.search(line))

        # Count functions/methods
        func_pattern = re.compile(r"(?:void|Future|Stream|\w+)\s+\w+\s*\([^)]*\)\s*(?:async\s*)?{")
        functions = sum(1 for line in lines if func_pattern.search(line))

        # Count widgets (Flutter)
        widget_pattern = re.compile(r"class\s+\w+\s+extends\s+(?:Stateless|Stateful)Widget")
        widgets = sum(1 for line in lines if widget_pattern.search(line))

        return {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("//")]),
            "comment_lines": len([l for l in lines if l.strip().startswith("//")]),
            "blank_lines": len([l for l in lines if not l.strip()]),
            "classes": classes,
            "functions": functions,
            "widgets": widgets,
        }
