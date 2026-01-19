"""
SAHOOL Code Fix Agent - TypeScript Analyzer
محلل TypeScript

TypeScript/JavaScript code analyzer with:
- Syntax checking
- Type checking patterns
- Security analysis
- Style checking
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


class TypeScriptAnalyzer(BaseAnalyzer):
    """
    محلل TypeScript
    TypeScript/JavaScript Analyzer
    """

    LANGUAGE = "typescript"
    VERSION = "1.0.0"

    # Security patterns
    SECURITY_PATTERNS = [
        {
            "pattern": r"\beval\s*\(",
            "code": "S106",
            "message": "Use of eval() is dangerous",
            "message_ar": "استخدام eval() خطير",
            "severity": IssueSeverity.ERROR,
        },
        {
            "pattern": r"innerHTML\s*=",
            "code": "S109",
            "message": "innerHTML can lead to XSS vulnerabilities",
            "message_ar": "innerHTML يمكن أن يؤدي إلى ثغرات XSS",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"dangerouslySetInnerHTML",
            "code": "S110",
            "message": "dangerouslySetInnerHTML can lead to XSS",
            "message_ar": "dangerouslySetInnerHTML يمكن أن يؤدي إلى XSS",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"document\.write\s*\(",
            "code": "S111",
            "message": "document.write can be exploited for XSS",
            "message_ar": "document.write يمكن استغلاله لـ XSS",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"new\s+Function\s*\(",
            "code": "S107",
            "message": "new Function() is similar to eval()",
            "message_ar": "new Function() مشابه لـ eval()",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"(?:password|secret|api_key|token)\s*[:=]\s*['\"][^'\"]+['\"]",
            "code": "S105",
            "message": "Hardcoded secret detected",
            "message_ar": "تم اكتشاف سر ثابت",
            "severity": IssueSeverity.ERROR,
        },
        {
            "pattern": r"console\.(log|debug|info)\s*\(",
            "code": "S120",
            "message": "Console statement should be removed in production",
            "message_ar": "يجب إزالة تعليمات console في الإنتاج",
            "severity": IssueSeverity.INFO,
        },
    ]

    # Style patterns
    STYLE_PATTERNS = [
        {
            "pattern": r"var\s+\w+",
            "code": "T001",
            "message": "Use 'let' or 'const' instead of 'var'",
            "message_ar": "استخدم 'let' أو 'const' بدلاً من 'var'",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"==(?!=)",
            "code": "T002",
            "message": "Use strict equality (===) instead of loose equality (==)",
            "message_ar": "استخدم المساواة الصارمة (===) بدلاً من المساواة المرنة (==)",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"!=(?!=)",
            "code": "T003",
            "message": "Use strict inequality (!==) instead of loose inequality (!=)",
            "message_ar": "استخدم عدم المساواة الصارمة (!==)",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"//\s*TODO",
            "code": "T010",
            "message": "TODO comment found",
            "message_ar": "تم العثور على تعليق TODO",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"//\s*FIXME",
            "code": "T011",
            "message": "FIXME comment found",
            "message_ar": "تم العثور على تعليق FIXME",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"any(?:\s|;|,|\))",
            "code": "T020",
            "message": "Avoid using 'any' type",
            "message_ar": "تجنب استخدام نوع 'any'",
            "severity": IssueSeverity.WARNING,
        },
    ]

    async def analyze(self, code: str, file_path: str = "<string>") -> AnalysisResult:
        """تحليل كود TypeScript"""
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
            logger.error("typescript_analysis_error", error=str(e))
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

        # Basic syntax checks
        lines = code.split("\n")

        # Check for unclosed brackets
        brackets = {"(": ")", "[": "]", "{": "}"}
        stack: list[tuple[str, int]] = []

        for i, line in enumerate(lines, 1):
            for j, char in enumerate(line):
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
                                code="S001",
                                message=f"Mismatched bracket: expected '{brackets[open_bracket]}' but found '{char}'",
                                message_ar=f"قوس غير متطابق: متوقع '{brackets[open_bracket]}' ولكن وجد '{char}'",
                            ))
                    else:
                        issues.append(AnalysisIssue(
                            file_path="<string>",
                            line_start=i,
                            line_end=i,
                            column_start=j,
                            severity=IssueSeverity.ERROR,
                            category=IssueCategory.SYNTAX,
                            code="S002",
                            message=f"Unexpected closing bracket: '{char}'",
                            message_ar=f"قوس إغلاق غير متوقع: '{char}'",
                        ))

        for open_bracket, line in stack:
            issues.append(AnalysisIssue(
                file_path="<string>",
                line_start=line,
                line_end=line,
                severity=IssueSeverity.ERROR,
                category=IssueCategory.SYNTAX,
                code="S003",
                message=f"Unclosed bracket: '{open_bracket}'",
                message_ar=f"قوس غير مغلق: '{open_bracket}'",
            ))

        return issues

    async def check_types(self, code: str) -> list[AnalysisIssue]:
        """التحقق من الأنواع"""
        issues: list[AnalysisIssue] = []
        lines = code.split("\n")

        # Check for 'any' type usage
        any_pattern = re.compile(r":\s*any\b")
        for i, line in enumerate(lines, 1):
            if any_pattern.search(line):
                issues.append(AnalysisIssue(
                    file_path="<string>",
                    line_start=i,
                    line_end=i,
                    severity=IssueSeverity.WARNING,
                    category=IssueCategory.TYPE,
                    code="T101",
                    message="Explicit 'any' type should be avoided",
                    message_ar="يجب تجنب نوع 'any' الصريح",
                    source_code=line.strip(),
                ))

        # Check for missing type annotations on function parameters
        func_pattern = re.compile(r"(?:function|const|let)\s+\w+\s*=?\s*(?:async\s*)?\([^)]*\)")
        param_pattern = re.compile(r"\(([^)]*)\)")

        for i, line in enumerate(lines, 1):
            if func_pattern.search(line):
                param_match = param_pattern.search(line)
                if param_match:
                    params = param_match.group(1)
                    if params and ":" not in params and params.strip():
                        issues.append(AnalysisIssue(
                            file_path="<string>",
                            line_start=i,
                            line_end=i,
                            severity=IssueSeverity.INFO,
                            category=IssueCategory.TYPE,
                            code="T102",
                            message="Function parameters should have type annotations",
                            message_ar="يجب أن تحتوي معاملات الدالة على تعليقات توضيحية للنوع",
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
                    code="S501",
                    message=f"Line too long ({len(line)} > {self.config.max_line_length})",
                    message_ar=f"السطر طويل جداً ({len(line)} > {self.config.max_line_length})",
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

    def _calculate_metrics(self, code: str) -> dict[str, Any]:
        """حساب المقاييس"""
        lines = code.split("\n")

        # Count functions
        function_pattern = re.compile(r"(?:function|const|let|var)\s+\w+\s*=?\s*(?:async\s*)?\(")
        functions = sum(1 for line in lines if function_pattern.search(line))

        # Count classes
        class_pattern = re.compile(r"\bclass\s+\w+")
        classes = sum(1 for line in lines if class_pattern.search(line))

        # Count interfaces
        interface_pattern = re.compile(r"\binterface\s+\w+")
        interfaces = sum(1 for line in lines if interface_pattern.search(line))

        return {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("//")]),
            "comment_lines": len([l for l in lines if l.strip().startswith("//")]),
            "blank_lines": len([l for l in lines if not l.strip()]),
            "functions": functions,
            "classes": classes,
            "interfaces": interfaces,
        }
