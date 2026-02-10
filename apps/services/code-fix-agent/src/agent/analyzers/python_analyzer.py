"""
SAHOOL Code Fix Agent - Python Analyzer
محلل Python

Comprehensive Python code analyzer with:
- Syntax checking
- Type checking (via mypy)
- Security analysis (via bandit patterns)
- Style checking (via ruff patterns)
- Complexity analysis
"""

import ast
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


class PythonAnalyzer(BaseAnalyzer):
    """
    محلل Python
    Python Analyzer

    Features:
    - Syntax validation
    - Type inference and checking
    - Security vulnerability detection
    - Code style analysis
    - Complexity metrics
    """

    LANGUAGE = "python"
    VERSION = "1.0.0"

    # Security patterns (based on bandit)
    SECURITY_PATTERNS = [
        {
            "pattern": r"\beval\s*\(",
            "code": "B307",
            "message": "Use of eval() is dangerous",
            "message_ar": "استخدام eval() خطير",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"\bexec\s*\(",
            "code": "B102",
            "message": "Use of exec() is dangerous",
            "message_ar": "استخدام exec() خطير",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"subprocess\.(?:call|run|Popen).*shell\s*=\s*True",
            "code": "B602",
            "message": "Shell injection vulnerability",
            "message_ar": "ثغرة حقن الأوامر",
            "severity": IssueSeverity.ERROR,
        },
        {
            "pattern": r"pickle\.loads?\s*\(",
            "code": "B301",
            "message": "Pickle deserialization is unsafe",
            "message_ar": "فك تسلسل pickle غير آمن",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"yaml\.load\s*\([^,)]+\)",
            "code": "B506",
            "message": "Use yaml.safe_load() instead of yaml.load()",
            "message_ar": "استخدم yaml.safe_load() بدلاً من yaml.load()",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"hashlib\.(?:md5|sha1)\s*\(",
            "code": "B303",
            "message": "Weak hash function (MD5/SHA1)",
            "message_ar": "دالة تجزئة ضعيفة (MD5/SHA1)",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"random\.\w+\(",
            "code": "B311",
            "message": "Standard random is not cryptographically secure",
            "message_ar": "random القياسي ليس آمناً للتشفير",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"assert\s+",
            "code": "B101",
            "message": "Assert statements can be disabled with -O flag",
            "message_ar": "يمكن تعطيل تعليمات assert بعلامة -O",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"except\s*:",
            "code": "B110",
            "message": "Bare except catches all exceptions",
            "message_ar": "except فارغ يلتقط جميع الاستثناءات",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"password\s*=\s*[\"'][^\"']+[\"']",
            "code": "B105",
            "message": "Hardcoded password detected",
            "message_ar": "تم اكتشاف كلمة مرور ثابتة",
            "severity": IssueSeverity.ERROR,
        },
        {
            "pattern": r"(?:secret|api_key|token)\s*=\s*[\"'][^\"']+[\"']",
            "code": "B105",
            "message": "Hardcoded secret detected",
            "message_ar": "تم اكتشاف سر ثابت",
            "severity": IssueSeverity.ERROR,
        },
    ]

    # Style patterns
    STYLE_PATTERNS = [
        {
            "pattern": r"^\s*import\s+\*",
            "code": "F403",
            "message": "Star imports are discouraged",
            "message_ar": "استيراد النجمة غير مستحسن",
            "severity": IssueSeverity.WARNING,
        },
        {
            "pattern": r"^\s*print\s*\(",
            "code": "T201",
            "message": "Print statement found (use logging instead)",
            "message_ar": "تم العثور على print (استخدم logging بدلاً)",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"#\s*TODO",
            "code": "FIX002",
            "message": "TODO comment found",
            "message_ar": "تم العثور على تعليق TODO",
            "severity": IssueSeverity.INFO,
        },
        {
            "pattern": r"#\s*FIXME",
            "code": "FIX001",
            "message": "FIXME comment found",
            "message_ar": "تم العثور على تعليق FIXME",
            "severity": IssueSeverity.WARNING,
        },
    ]

    async def analyze(self, code: str, file_path: str = "<string>") -> AnalysisResult:
        """
        تحليل كود Python
        Analyze Python code
        """
        start_time = time.time()
        issues: list[AnalysisIssue] = []

        try:
            # Syntax check
            if self.config.check_syntax:
                syntax_issues = await self.check_syntax(code)
                issues.extend(syntax_issues)

                # If syntax errors, skip other checks
                if any(i.severity == IssueSeverity.ERROR for i in syntax_issues):
                    return AnalysisResult(
                        success=False,
                        language=self.LANGUAGE,
                        file_path=file_path,
                        issues=[i for i in issues if self._should_include_issue(i)],
                        metrics=self._calculate_basic_metrics(code),
                        analysis_time_ms=(time.time() - start_time) * 1000,
                        analyzer_version=self.VERSION,
                    )

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

            # Logic check
            if self.config.check_logic:
                logic_issues = await self.check_logic(code)
                issues.extend(logic_issues)

            # Calculate metrics
            metrics = self._calculate_metrics(code)

            # Filter and limit issues
            filtered_issues = [i for i in issues if self._should_include_issue(i)]
            if len(filtered_issues) > self.config.max_issues:
                filtered_issues = filtered_issues[: self.config.max_issues]

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
            logger.error("python_analysis_error", error=str(e))
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

        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(
                AnalysisIssue(
                    file_path="<string>",
                    line_start=e.lineno or 1,
                    line_end=e.lineno or 1,
                    column_start=e.offset or 0,
                    severity=IssueSeverity.ERROR,
                    category=IssueCategory.SYNTAX,
                    code="E999",
                    message=f"Syntax error: {e.msg}",
                    message_ar=f"خطأ نحوي: {e.msg}",
                    confidence=1.0,
                )
            )

        return issues

    async def check_types(self, code: str) -> list[AnalysisIssue]:
        """التحقق من الأنواع"""
        issues: list[AnalysisIssue] = []

        try:
            tree = ast.parse(code)

            # Check for common type issues
            for node in ast.walk(tree):
                # Check for None comparison with is
                if isinstance(node, ast.Compare):
                    for op, comparator in zip(node.ops, node.comparators):
                        if isinstance(comparator, ast.Constant) and comparator.value is None:
                            if not isinstance(op, (ast.Is, ast.IsNot)):
                                issues.append(
                                    AnalysisIssue(
                                        file_path="<string>",
                                        line_start=node.lineno,
                                        line_end=node.lineno,
                                        category=IssueCategory.TYPE,
                                        code="E711",
                                        message="Comparison to None should use 'is' or 'is not'",
                                        message_ar="المقارنة مع None يجب أن تستخدم 'is' أو 'is not'",
                                        severity=IssueSeverity.WARNING,
                                        fix_available=True,
                                    )
                                )

                # Check for True/False comparison
                if isinstance(node, ast.Compare):
                    for op, comparator in zip(node.ops, node.comparators):
                        if isinstance(comparator, ast.Constant) and comparator.value in (
                            True,
                            False,
                        ):
                            if isinstance(op, (ast.Eq, ast.NotEq)):
                                issues.append(
                                    AnalysisIssue(
                                        file_path="<string>",
                                        line_start=node.lineno,
                                        line_end=node.lineno,
                                        category=IssueCategory.TYPE,
                                        code="E712",
                                        message="Comparison to True/False should use 'if x:' or 'if not x:'",
                                        message_ar="المقارنة مع True/False يجب أن تستخدم 'if x:' أو 'if not x:'",
                                        severity=IssueSeverity.WARNING,
                                        fix_available=True,
                                    )
                                )

        except SyntaxError:
            pass  # Already caught in syntax check

        return issues

    async def check_security(self, code: str) -> list[AnalysisIssue]:
        """التحقق من الأمان"""
        issues: list[AnalysisIssue] = []
        lines = code.split("\n")

        for pattern_info in self.SECURITY_PATTERNS:
            pattern = re.compile(pattern_info["pattern"], re.IGNORECASE)
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    issues.append(
                        AnalysisIssue(
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
                        )
                    )

        return issues

    async def check_style(self, code: str) -> list[AnalysisIssue]:
        """التحقق من الأسلوب"""
        issues: list[AnalysisIssue] = []
        lines = code.split("\n")

        # Line length check
        for i, line in enumerate(lines, 1):
            if len(line) > self.config.max_line_length:
                issues.append(
                    AnalysisIssue(
                        file_path="<string>",
                        line_start=i,
                        line_end=i,
                        severity=IssueSeverity.INFO,
                        category=IssueCategory.STYLE,
                        code="E501",
                        message=f"Line too long ({len(line)} > {self.config.max_line_length})",
                        message_ar=f"السطر طويل جداً ({len(line)} > {self.config.max_line_length})",
                        fix_available=False,
                    )
                )

        # Trailing whitespace
        for i, line in enumerate(lines, 1):
            if line.rstrip() != line and line.strip():
                issues.append(
                    AnalysisIssue(
                        file_path="<string>",
                        line_start=i,
                        line_end=i,
                        severity=IssueSeverity.INFO,
                        category=IssueCategory.STYLE,
                        code="W291",
                        message="Trailing whitespace",
                        message_ar="مسافة بيضاء في نهاية السطر",
                        fix_available=True,
                        fix_code=line.rstrip(),
                    )
                )

        # Pattern-based style checks
        for pattern_info in self.STYLE_PATTERNS:
            pattern = re.compile(pattern_info["pattern"], re.MULTILINE)
            for i, line in enumerate(lines, 1):
                if pattern.search(line):
                    issues.append(
                        AnalysisIssue(
                            file_path="<string>",
                            line_start=i,
                            line_end=i,
                            severity=pattern_info["severity"],
                            category=IssueCategory.STYLE,
                            code=pattern_info["code"],
                            message=pattern_info["message"],
                            message_ar=pattern_info["message_ar"],
                            source_code=line.strip(),
                        )
                    )

        return issues

    async def check_logic(self, code: str) -> list[AnalysisIssue]:
        """التحقق من المنطق"""
        issues: list[AnalysisIssue] = []

        try:
            tree = ast.parse(code)

            # Check for unused imports
            imports = set()
            used_names = set()

            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    for alias in node.names:
                        imports.add((alias.asname or alias.name, node.lineno))
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                    used_names.add(node.id)

            for name, line in imports:
                base_name = name.split(".")[0]
                if base_name not in used_names and name not in used_names:
                    issues.append(
                        AnalysisIssue(
                            file_path="<string>",
                            line_start=line,
                            line_end=line,
                            severity=IssueSeverity.WARNING,
                            category=IssueCategory.LOGIC,
                            code="F401",
                            message=f"'{name}' imported but unused",
                            message_ar=f"'{name}' مستورد ولكن غير مستخدم",
                            fix_available=True,
                        )
                    )

            # Check for unreachable code
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    found_return = False
                    for stmt in node.body:
                        if found_return:
                            issues.append(
                                AnalysisIssue(
                                    file_path="<string>",
                                    line_start=stmt.lineno,
                                    line_end=stmt.lineno,
                                    severity=IssueSeverity.WARNING,
                                    category=IssueCategory.LOGIC,
                                    code="W0101",
                                    message="Unreachable code",
                                    message_ar="كود لا يمكن الوصول إليه",
                                )
                            )
                            break
                        if isinstance(stmt, ast.Return):
                            found_return = True

        except SyntaxError:
            pass

        return issues

    def _calculate_metrics(self, code: str) -> dict[str, Any]:
        """حساب المقاييس"""
        metrics = self._calculate_basic_metrics(code)

        try:
            tree = ast.parse(code)

            # Count definitions
            functions = 0
            classes = 0
            methods = 0

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions += 1
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                    # Count methods in class
                    for item in node.body:
                        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            methods += 1

            metrics.update(
                {
                    "functions": functions,
                    "classes": classes,
                    "methods": methods,
                    "cyclomatic_complexity": self._calculate_complexity(tree),
                }
            )

        except SyntaxError:
            pass

        return metrics

    def _calculate_basic_metrics(self, code: str) -> dict[str, Any]:
        """حساب المقاييس الأساسية"""
        lines = code.split("\n")
        return {
            "total_lines": len(lines),
            "code_lines": len([l for l in lines if l.strip() and not l.strip().startswith("#")]),
            "comment_lines": len([l for l in lines if l.strip().startswith("#")]),
            "blank_lines": len([l for l in lines if not l.strip()]),
            "avg_line_length": sum(len(l) for l in lines) / max(len(lines), 1),
        }

    def _calculate_complexity(self, tree: ast.AST) -> int:
        """حساب التعقيد السيكلوماتي"""
        complexity = 1

        for node in ast.walk(tree):
            if isinstance(
                node,
                (
                    ast.If,
                    ast.For,
                    ast.While,
                    ast.ExceptHandler,
                    ast.With,
                    ast.Assert,
                    ast.comprehension,
                ),
            ):
                complexity += 1
            elif isinstance(node, ast.BoolOp):
                complexity += len(node.values) - 1

        return complexity
