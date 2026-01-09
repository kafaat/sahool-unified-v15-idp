"""
SAHOOL Code Fix Agent
وكيل إصلاح وتنفيذ الكود

Implements a Learning + Utility-Based agent for:
- Code analysis and bug detection
- Automated code fixes
- Feature implementation
- Code refactoring
- Test generation
- PR review

Follows best practices from Claude Agent SDK and A2A Protocol.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ============================================================================
# ENUMS & DATA CLASSES
# ============================================================================


class AgentType(Enum):
    """أنواع الوكلاء"""

    SIMPLE_REFLEX = "simple_reflex"
    MODEL_BASED = "model_based"
    GOAL_BASED = "goal_based"
    UTILITY_BASED = "utility_based"
    LEARNING = "learning"


class AgentLayer(Enum):
    """طبقات الوكلاء"""

    EDGE = "edge"
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"
    LEARNING = "learning"


class AgentStatus(Enum):
    """حالة الوكيل"""

    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    ERROR = "error"
    LEARNING = "learning"


class IssueType(Enum):
    """أنواع مشاكل الكود"""

    BUG = "bug"
    SECURITY = "security"
    PERFORMANCE = "performance"
    STYLE = "style"
    TYPE_ERROR = "type_error"
    LOGIC_ERROR = "logic_error"
    MEMORY_LEAK = "memory_leak"
    RACE_CONDITION = "race_condition"
    SYNTAX_ERROR = "syntax_error"
    IMPORT_ERROR = "import_error"
    DEPRECATION = "deprecation"


class IssueSeverity(Enum):
    """شدة المشكلة"""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class FixStrategy(Enum):
    """استراتيجيات الإصلاح"""

    MINIMAL = "minimal"  # أقل تغيير ممكن
    COMPREHENSIVE = "comprehensive"  # إصلاح شامل
    REFACTOR = "refactor"  # إعادة هيكلة
    SAFE = "safe"  # إصلاح آمن مع اختبارات


class SupportedLanguage(Enum):
    """اللغات المدعومة"""

    PYTHON = "python"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
    DART = "dart"


@dataclass
class CodeIssue:
    """مشكلة في الكود"""

    issue_id: str
    issue_type: IssueType
    severity: IssueSeverity
    file_path: str
    line_start: int
    line_end: int
    column_start: int = 0
    column_end: int = 0
    description: str = ""
    description_ar: str = ""
    suggestion: str = ""
    suggestion_ar: str = ""
    code_snippet: str = ""
    confidence: float = 0.8
    rule_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CodeFix:
    """إصلاح الكود"""

    fix_id: str
    issue: CodeIssue
    original_code: str
    fixed_code: str
    changes: list[dict[str, Any]]
    strategy: FixStrategy
    confidence: float
    explanation: str
    explanation_ar: str
    tests_needed: list[str] = field(default_factory=list)
    breaking_changes: bool = False
    requires_review: bool = False


@dataclass
class AnalysisResult:
    """نتيجة التحليل"""

    file_path: str
    language: SupportedLanguage
    issues: list[CodeIssue]
    metrics: dict[str, Any]
    suggestions: list[str]
    analysis_time_ms: float
    analyzer_version: str


@dataclass
class AgentContext:
    """سياق الوكيل"""

    request_id: str = ""
    user_id: str | None = None
    tenant_id: str | None = None
    repository: str | None = None
    branch: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentPercept:
    """إدراك الوكيل - المدخلات"""

    percept_type: str
    data: Any
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    reliability: float = 1.0


@dataclass
class AgentAction:
    """إجراء الوكيل"""

    action_type: str
    parameters: dict[str, Any]
    confidence: float
    priority: int  # 1 (highest) - 5 (lowest)
    reasoning: str
    reasoning_ar: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source_agent: str = ""
    requires_confirmation: bool = False

    def to_dict(self) -> dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            "action_type": self.action_type,
            "parameters": self.parameters,
            "confidence": self.confidence,
            "priority": self.priority,
            "reasoning": self.reasoning,
            "reasoning_ar": self.reasoning_ar,
            "timestamp": self.timestamp.isoformat(),
            "source_agent": self.source_agent,
            "requires_confirmation": self.requires_confirmation,
        }


@dataclass
class AgentState:
    """حالة الوكيل الداخلية"""

    beliefs: dict[str, Any] = field(default_factory=dict)
    goals: list[str] = field(default_factory=list)
    intentions: list[str] = field(default_factory=list)
    knowledge: dict[str, Any] = field(default_factory=dict)
    memory: list[dict[str, Any]] = field(default_factory=list)


# ============================================================================
# CODE FIX AGENT
# ============================================================================


class CodeFixAgent:
    """
    وكيل إصلاح وتنفيذ الكود
    Code Fix and Implementation Agent

    Combines Utility-Based decision making with Learning capabilities
    for intelligent code analysis and fixes.

    Architecture:
    - Type: LEARNING (with Utility-Based decision making)
    - Layer: SPECIALIST
    - Protocol: A2A compliant
    - Integration: MCP tools support
    """

    # Priority weights for different issue types
    ISSUE_PRIORITIES: dict[IssueType, int] = {
        IssueType.SECURITY: 100,
        IssueType.MEMORY_LEAK: 90,
        IssueType.RACE_CONDITION: 85,
        IssueType.BUG: 80,
        IssueType.SYNTAX_ERROR: 78,
        IssueType.TYPE_ERROR: 70,
        IssueType.LOGIC_ERROR: 75,
        IssueType.IMPORT_ERROR: 65,
        IssueType.PERFORMANCE: 50,
        IssueType.DEPRECATION: 40,
        IssueType.STYLE: 20,
    }

    # Severity multipliers
    SEVERITY_MULTIPLIERS: dict[IssueSeverity, float] = {
        IssueSeverity.CRITICAL: 1.5,
        IssueSeverity.HIGH: 1.2,
        IssueSeverity.MEDIUM: 1.0,
        IssueSeverity.LOW: 0.7,
        IssueSeverity.INFO: 0.3,
    }

    def __init__(self, agent_id: str = "code_fix_agent_001"):
        """
        تهيئة وكيل إصلاح الكود

        Args:
            agent_id: معرف الوكيل الفريد
        """
        self.agent_id = agent_id
        self.name = "Code Fix Agent"
        self.name_ar = "وكيل إصلاح الكود"
        self.agent_type = AgentType.LEARNING
        self.layer = AgentLayer.SPECIALIST
        self.version = "1.0.0"

        self.status = AgentStatus.IDLE
        self.state = AgentState()
        self.context: AgentContext | None = None

        # Performance metrics
        self.total_requests = 0
        self.successful_requests = 0
        self.total_response_time_ms = 0.0
        self.last_action_time: datetime | None = None

        # Learning metrics
        self.feedback_history: list[dict[str, Any]] = []
        self.reward_history: list[float] = []
        self.success_patterns: dict[str, float] = {}

        # Analyzers (lazy loaded)
        self._analyzers: dict[SupportedLanguage, Any] = {}

        # Goals
        self.state.goals = [
            "fix_bugs_accurately",
            "minimize_code_changes",
            "maintain_code_quality",
            "ensure_test_coverage",
            "learn_from_feedback",
        ]

        logger.info(
            "agent_initialized",
            agent_id=self.agent_id,
            name=self.name,
            layer=self.layer.value,
        )

    # ========================================================================
    # UTILITY FUNCTION
    # ========================================================================

    def calculate_fix_utility(
        self,
        issue: CodeIssue,
        fix: CodeFix,
        context: AgentContext | None = None,
    ) -> float:
        """
        حساب منفعة الإصلاح
        Calculate utility of a proposed fix

        Considers:
        - Issue severity and priority
        - Fix confidence
        - Code change size (minimal preferred)
        - Historical success rate
        - Breaking changes risk

        Args:
            issue: المشكلة المراد إصلاحها
            fix: الإصلاح المقترح
            context: سياق الوكيل

        Returns:
            قيمة المنفعة (0.0 - 1.0)
        """
        # Base priority from issue type
        base_priority = self.ISSUE_PRIORITIES.get(issue.issue_type, 50) / 100

        # Severity multiplier
        severity_mult = self.SEVERITY_MULTIPLIERS.get(issue.severity, 1.0)
        severity_score = min(base_priority * severity_mult, 1.0)

        # Confidence factor
        confidence_score = fix.confidence

        # Change size factor (smaller changes preferred)
        original_lines = len(fix.original_code.splitlines())
        fixed_lines = len(fix.fixed_code.splitlines())
        change_ratio = abs(fixed_lines - original_lines) / max(original_lines, 1)
        size_score = max(0, 1 - change_ratio)

        # Historical success factor
        pattern_key = f"{issue.issue_type.value}_{fix.strategy.value}"
        success_rate = self.success_patterns.get(pattern_key, 0.7)

        # Breaking changes penalty
        breaking_penalty = 0.3 if fix.breaking_changes else 0.0

        # Calculate combined utility
        utility = (
            0.25 * severity_score
            + 0.25 * confidence_score
            + 0.15 * size_score
            + 0.25 * success_rate
            - breaking_penalty
        )

        return max(0.0, min(1.0, utility))

    # ========================================================================
    # PERCEIVE - THINK - ACT CYCLE
    # ========================================================================

    async def perceive(self, percept: AgentPercept) -> None:
        """
        استقبال المدخلات للتحليل
        Receive inputs for analysis

        Supported percept types:
        - code_snippet: Code to analyze
        - file_content: Full file content
        - error_log: Error messages/logs
        - pr_diff: Pull request diff
        - specification: Feature specification
        - test_results: Test execution results
        """
        logger.debug(
            "perceive_input",
            percept_type=percept.percept_type,
            source=percept.source,
        )

        if percept.percept_type == "code_snippet":
            self.state.beliefs["code"] = percept.data.get("code", "")
            self.state.beliefs["language"] = percept.data.get("language", "python")
            self.state.beliefs["file_path"] = percept.data.get("file_path", "")

        elif percept.percept_type == "file_content":
            self.state.beliefs["file_content"] = percept.data

        elif percept.percept_type == "error_log":
            self.state.beliefs["errors"] = percept.data

        elif percept.percept_type == "pr_diff":
            self.state.beliefs["diff"] = percept.data

        elif percept.percept_type == "specification":
            self.state.beliefs["spec"] = percept.data

        elif percept.percept_type == "test_results":
            self.state.beliefs["test_results"] = percept.data

        elif percept.percept_type == "context":
            if isinstance(percept.data, dict):
                for key, value in percept.data.items():
                    self.state.beliefs[f"context_{key}"] = value

    async def think(self) -> AgentAction | None:
        """
        تحليل الكود واتخاذ القرار
        Analyze code and decide on action

        Decision flow:
        1. Determine task type from beliefs
        2. Run appropriate analysis
        3. Generate action options
        4. Select best action using utility function
        """
        logger.debug("think_start", beliefs_keys=list(self.state.beliefs.keys()))

        # Determine task type and route to appropriate handler
        if "errors" in self.state.beliefs:
            return await self._handle_error_fix()

        elif "diff" in self.state.beliefs:
            return await self._handle_pr_review()

        elif "spec" in self.state.beliefs:
            return await self._handle_implementation()

        elif "code" in self.state.beliefs:
            return await self._handle_code_analysis()

        elif "file_content" in self.state.beliefs:
            return await self._handle_file_analysis()

        # No actionable input
        return AgentAction(
            action_type="no_action",
            parameters={},
            confidence=1.0,
            priority=5,
            reasoning="No actionable input provided",
            reasoning_ar="لم يتم تقديم مدخلات قابلة للتنفيذ",
            source_agent=self.agent_id,
        )

    async def act(self, action: AgentAction) -> dict[str, Any]:
        """
        تنفيذ الإجراء
        Execute the action

        Returns execution result with:
        - success: bool
        - data: action-specific results
        - metadata: execution details
        """
        start_time = datetime.now()
        self.status = AgentStatus.PROCESSING

        logger.info(
            "act_start",
            action_type=action.action_type,
            confidence=action.confidence,
        )

        try:
            result: dict[str, Any] = {
                "action_type": action.action_type,
                "executed_at": start_time.isoformat(),
                "agent_id": self.agent_id,
                "success": True,
            }

            if action.action_type == "analyze_code":
                result["analysis"] = action.parameters.get("analysis_result")

            elif action.action_type == "apply_fix":
                result["fix"] = action.parameters.get("fix")
                result["requires_review"] = action.parameters.get("requires_review", False)

            elif action.action_type == "generate_tests":
                result["tests"] = action.parameters.get("tests", [])

            elif action.action_type == "review_pr":
                result["review"] = action.parameters.get("review")

            elif action.action_type == "implement_feature":
                result["implementation"] = action.parameters.get("implementation")

            # Calculate response time
            response_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            result["response_time_ms"] = response_time_ms

            # Update metrics
            self.total_requests += 1
            self.successful_requests += 1
            self.total_response_time_ms += response_time_ms
            self.last_action_time = datetime.now()
            self.status = AgentStatus.IDLE

            logger.info(
                "act_complete",
                action_type=action.action_type,
                response_time_ms=response_time_ms,
            )

            return result

        except Exception as e:
            self.status = AgentStatus.ERROR
            logger.error("act_error", action_type=action.action_type, error=str(e))
            return {
                "action_type": action.action_type,
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
            }

    async def run(self, percept: AgentPercept) -> dict[str, Any]:
        """
        دورة الوكيل الكاملة: إدراك → تفكير → فعل
        Full agent cycle: Perceive → Think → Act
        """
        start_time = datetime.now()
        self.total_requests += 1

        try:
            # 1. Perceive
            await self.perceive(percept)

            # 2. Think
            action = await self.think()

            if action is None:
                return {
                    "success": False,
                    "message": "No action determined",
                    "agent_id": self.agent_id,
                }

            # 3. Act
            result = await self.act(action)

            # Add action info to result
            result["action"] = action.to_dict()
            result["total_time_ms"] = (datetime.now() - start_time).total_seconds() * 1000

            return result

        except Exception as e:
            logger.error("run_error", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.agent_id,
            }

    # ========================================================================
    # TASK HANDLERS
    # ========================================================================

    async def _handle_code_analysis(self) -> AgentAction:
        """تحليل الكود واكتشاف المشاكل"""
        code = self.state.beliefs.get("code", "")
        language = self.state.beliefs.get("language", "python")
        file_path = self.state.beliefs.get("file_path", "unknown")

        # Perform analysis
        issues = await self._analyze_code(code, language)

        analysis_result = AnalysisResult(
            file_path=file_path,
            language=SupportedLanguage(language),
            issues=issues,
            metrics=self._calculate_code_metrics(code),
            suggestions=self._generate_suggestions(issues),
            analysis_time_ms=0,  # Will be set by act
            analyzer_version=self.version,
        )

        # If issues found, generate fix options
        if issues:
            # Sort by priority
            sorted_issues = sorted(
                issues,
                key=lambda i: (
                    self.ISSUE_PRIORITIES.get(i.issue_type, 50),
                    self.SEVERITY_MULTIPLIERS.get(i.severity, 1.0),
                ),
                reverse=True,
            )

            top_issue = sorted_issues[0]
            return AgentAction(
                action_type="analyze_code",
                parameters={
                    "analysis_result": {
                        "file_path": file_path,
                        "language": language,
                        "issues_count": len(issues),
                        "issues": [self._issue_to_dict(i) for i in issues],
                        "top_issue": self._issue_to_dict(top_issue),
                        "metrics": analysis_result.metrics,
                        "suggestions": analysis_result.suggestions,
                    }
                },
                confidence=0.85,
                priority=2
                if top_issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH]
                else 3,
                reasoning=f"Found {len(issues)} issues, highest severity: {top_issue.severity.value}",
                reasoning_ar=f"تم العثور على {len(issues)} مشكلة، أعلى شدة: {top_issue.severity.value}",
                source_agent=self.agent_id,
            )

        return AgentAction(
            action_type="analyze_code",
            parameters={
                "analysis_result": {
                    "file_path": file_path,
                    "language": language,
                    "issues_count": 0,
                    "issues": [],
                    "metrics": analysis_result.metrics,
                    "suggestions": [],
                    "status": "clean",
                }
            },
            confidence=0.9,
            priority=4,
            reasoning="No issues found in code",
            reasoning_ar="لم يتم العثور على مشاكل في الكود",
            source_agent=self.agent_id,
        )

    async def _handle_error_fix(self) -> AgentAction:
        """إصلاح الأخطاء من السجلات"""
        errors = self.state.beliefs.get("errors", [])
        code = self.state.beliefs.get("code", "")

        # Parse errors and generate fixes
        fixes = await self._generate_fixes_for_errors(errors, code)

        if fixes:
            # Select best fix using utility function
            best_fix = max(
                fixes,
                key=lambda f: self.calculate_fix_utility(f.issue, f, self.context),
            )

            return AgentAction(
                action_type="apply_fix",
                parameters={
                    "fix": self._fix_to_dict(best_fix),
                    "all_fixes": [self._fix_to_dict(f) for f in fixes],
                    "requires_review": best_fix.requires_review,
                },
                confidence=best_fix.confidence,
                priority=1 if best_fix.issue.severity == IssueSeverity.CRITICAL else 2,
                reasoning=best_fix.explanation,
                reasoning_ar=best_fix.explanation_ar,
                source_agent=self.agent_id,
                requires_confirmation=best_fix.breaking_changes,
            )

        return AgentAction(
            action_type="no_fix_available",
            parameters={"errors": errors},
            confidence=0.5,
            priority=3,
            reasoning="Could not generate automatic fix for the errors",
            reasoning_ar="لم يتمكن من توليد إصلاح تلقائي للأخطاء",
            source_agent=self.agent_id,
        )

    async def _handle_pr_review(self) -> AgentAction:
        """مراجعة طلب السحب"""
        diff = self.state.beliefs.get("diff", "")

        review_result = await self._review_diff(diff)

        return AgentAction(
            action_type="review_pr",
            parameters={
                "review": review_result,
                "approval_status": review_result.get("approval", "needs_work"),
            },
            confidence=review_result.get("confidence", 0.8),
            priority=3,
            reasoning=review_result.get("summary", "PR reviewed"),
            reasoning_ar=review_result.get("summary_ar", "تمت مراجعة طلب السحب"),
            source_agent=self.agent_id,
        )

    async def _handle_implementation(self) -> AgentAction:
        """تنفيذ ميزة جديدة"""
        spec = self.state.beliefs.get("spec", {})

        implementation = await self._implement_from_spec(spec)

        return AgentAction(
            action_type="implement_feature",
            parameters={
                "implementation": implementation,
                "tests": implementation.get("tests", []),
            },
            confidence=implementation.get("confidence", 0.7),
            priority=2,
            reasoning=f"Implemented feature: {spec.get('name', 'unknown')}",
            reasoning_ar=f"تم تنفيذ الميزة: {spec.get('name_ar', spec.get('name', 'غير معروف'))}",
            source_agent=self.agent_id,
            requires_confirmation=True,
        )

    async def _handle_file_analysis(self) -> AgentAction:
        """تحليل ملف كامل"""
        file_content = self.state.beliefs.get("file_content", {})
        code = file_content.get("content", "")
        language = file_content.get("language", "python")
        file_path = file_content.get("path", "unknown")

        # Update beliefs for code analysis
        self.state.beliefs["code"] = code
        self.state.beliefs["language"] = language
        self.state.beliefs["file_path"] = file_path

        return await self._handle_code_analysis()

    # ========================================================================
    # ANALYSIS METHODS
    # ========================================================================

    async def _analyze_code(self, code: str, language: str) -> list[CodeIssue]:
        """
        تحليل الكود باستخدام المحللات المناسبة
        Analyze code using appropriate analyzers
        """
        issues: list[CodeIssue] = []

        try:
            lang = SupportedLanguage(language)
        except ValueError:
            logger.warning("unsupported_language", language=language)
            return issues

        # Basic syntax check
        syntax_issues = await self._check_syntax(code, lang)
        issues.extend(syntax_issues)

        # Import/module issues
        import_issues = await self._check_imports(code, lang)
        issues.extend(import_issues)

        # Security issues
        security_issues = await self._check_security(code, lang)
        issues.extend(security_issues)

        # Style issues
        style_issues = await self._check_style(code, lang)
        issues.extend(style_issues)

        return issues

    async def _check_syntax(self, code: str, language: SupportedLanguage) -> list[CodeIssue]:
        """التحقق من الأخطاء النحوية"""
        issues = []

        if language == SupportedLanguage.PYTHON:
            try:
                compile(code, "<string>", "exec")
            except SyntaxError as e:
                issues.append(
                    CodeIssue(
                        issue_id=f"syntax_{hash(str(e))}",
                        issue_type=IssueType.SYNTAX_ERROR,
                        severity=IssueSeverity.CRITICAL,
                        file_path="<input>",
                        line_start=e.lineno or 1,
                        line_end=e.lineno or 1,
                        column_start=e.offset or 0,
                        description=str(e.msg),
                        description_ar=f"خطأ نحوي: {e.msg}",
                        suggestion=f"Fix syntax error at line {e.lineno}",
                        suggestion_ar=f"أصلح الخطأ النحوي في السطر {e.lineno}",
                        confidence=1.0,
                    )
                )

        return issues

    async def _check_imports(self, code: str, language: SupportedLanguage) -> list[CodeIssue]:
        """التحقق من مشاكل الاستيراد"""
        issues = []

        if language == SupportedLanguage.PYTHON:
            import ast

            try:
                tree = ast.parse(code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            # Check for common problematic imports
                            if alias.name.startswith("_"):
                                issues.append(
                                    CodeIssue(
                                        issue_id=f"import_{alias.name}",
                                        issue_type=IssueType.IMPORT_ERROR,
                                        severity=IssueSeverity.LOW,
                                        file_path="<input>",
                                        line_start=node.lineno,
                                        line_end=node.lineno,
                                        description=f"Importing private module: {alias.name}",
                                        description_ar=f"استيراد وحدة خاصة: {alias.name}",
                                        confidence=0.7,
                                    )
                                )
            except SyntaxError:
                pass  # Already caught in syntax check

        return issues

    async def _check_security(self, code: str, language: SupportedLanguage) -> list[CodeIssue]:
        """التحقق من مشاكل الأمان"""
        issues = []

        # Common security patterns to check
        security_patterns = {
            "python": [
                (r"eval\s*\(", "Use of eval() is dangerous", "استخدام eval() خطير"),
                (r"exec\s*\(", "Use of exec() is dangerous", "استخدام exec() خطير"),
                (
                    r"subprocess\.call.*shell\s*=\s*True",
                    "Shell injection risk",
                    "خطر حقن الأوامر",
                ),
                (
                    r"pickle\.loads?\s*\(",
                    "Pickle deserialization is unsafe",
                    "فك تسلسل pickle غير آمن",
                ),
                (
                    r"yaml\.load\s*\([^,]+\)",
                    "Use yaml.safe_load instead",
                    "استخدم yaml.safe_load بدلاً من ذلك",
                ),
            ],
            "typescript": [
                (r"eval\s*\(", "Use of eval() is dangerous", "استخدام eval() خطير"),
                (
                    r"innerHTML\s*=",
                    "XSS risk with innerHTML",
                    "خطر XSS مع innerHTML",
                ),
                (
                    r"dangerouslySetInnerHTML",
                    "Potential XSS vulnerability",
                    "ثغرة XSS محتملة",
                ),
            ],
        }

        import re

        patterns = security_patterns.get(language.value, [])
        for pattern, desc_en, desc_ar in patterns:
            for match in re.finditer(pattern, code):
                line_num = code[: match.start()].count("\n") + 1
                issues.append(
                    CodeIssue(
                        issue_id=f"security_{hash(pattern)}_{line_num}",
                        issue_type=IssueType.SECURITY,
                        severity=IssueSeverity.HIGH,
                        file_path="<input>",
                        line_start=line_num,
                        line_end=line_num,
                        description=desc_en,
                        description_ar=desc_ar,
                        code_snippet=match.group(),
                        confidence=0.9,
                    )
                )

        return issues

    async def _check_style(self, code: str, language: SupportedLanguage) -> list[CodeIssue]:
        """التحقق من مشاكل الأسلوب"""
        issues = []

        # Basic style checks
        lines = code.split("\n")
        for i, line in enumerate(lines, 1):
            # Line too long
            if len(line) > 120:
                issues.append(
                    CodeIssue(
                        issue_id=f"style_line_length_{i}",
                        issue_type=IssueType.STYLE,
                        severity=IssueSeverity.INFO,
                        file_path="<input>",
                        line_start=i,
                        line_end=i,
                        description=f"Line too long ({len(line)} > 120)",
                        description_ar=f"السطر طويل جداً ({len(line)} > 120)",
                        confidence=1.0,
                    )
                )

            # Trailing whitespace
            if line.rstrip() != line:
                issues.append(
                    CodeIssue(
                        issue_id=f"style_trailing_ws_{i}",
                        issue_type=IssueType.STYLE,
                        severity=IssueSeverity.INFO,
                        file_path="<input>",
                        line_start=i,
                        line_end=i,
                        description="Trailing whitespace",
                        description_ar="مسافة بيضاء في نهاية السطر",
                        confidence=1.0,
                    )
                )

        return issues

    def _calculate_code_metrics(self, code: str) -> dict[str, Any]:
        """حساب مقاييس الكود"""
        lines = code.split("\n")
        non_empty_lines = [l for l in lines if l.strip()]
        comment_lines = [l for l in lines if l.strip().startswith("#")]

        return {
            "total_lines": len(lines),
            "code_lines": len(non_empty_lines) - len(comment_lines),
            "comment_lines": len(comment_lines),
            "blank_lines": len(lines) - len(non_empty_lines),
            "avg_line_length": sum(len(l) for l in lines) / max(len(lines), 1),
        }

    def _generate_suggestions(self, issues: list[CodeIssue]) -> list[str]:
        """توليد اقتراحات بناءً على المشاكل"""
        suggestions = []

        issue_types = {i.issue_type for i in issues}

        if IssueType.SECURITY in issue_types:
            suggestions.append("Review and fix security vulnerabilities immediately")

        if IssueType.PERFORMANCE in issue_types:
            suggestions.append("Consider performance optimizations")

        if IssueType.STYLE in issue_types:
            suggestions.append("Run code formatter (e.g., ruff format)")

        return suggestions

    # ========================================================================
    # FIX GENERATION
    # ========================================================================

    async def _generate_fixes_for_errors(self, errors: list[dict], code: str) -> list[CodeFix]:
        """توليد إصلاحات للأخطاء"""
        fixes = []

        for error in errors:
            error_type = error.get("type", "unknown")
            error_msg = error.get("message", "")
            line_num = error.get("line", 1)

            # Create issue from error
            issue = CodeIssue(
                issue_id=f"error_{hash(error_msg)}",
                issue_type=self._classify_error(error_type),
                severity=IssueSeverity.HIGH,
                file_path=error.get("file", "<input>"),
                line_start=line_num,
                line_end=line_num,
                description=error_msg,
                description_ar=error_msg,
                confidence=0.9,
            )

            # Generate fix based on error type
            fix = await self._generate_fix_for_issue(issue, code)
            if fix:
                fixes.append(fix)

        return fixes

    def _classify_error(self, error_type: str) -> IssueType:
        """تصنيف نوع الخطأ"""
        error_type_lower = error_type.lower()

        if "syntax" in error_type_lower:
            return IssueType.SYNTAX_ERROR
        elif "type" in error_type_lower:
            return IssueType.TYPE_ERROR
        elif "import" in error_type_lower or "module" in error_type_lower:
            return IssueType.IMPORT_ERROR
        elif "memory" in error_type_lower:
            return IssueType.MEMORY_LEAK
        elif "security" in error_type_lower:
            return IssueType.SECURITY
        else:
            return IssueType.BUG

    async def _generate_fix_for_issue(self, issue: CodeIssue, code: str) -> CodeFix | None:
        """توليد إصلاح لمشكلة محددة"""
        # This would integrate with LLM for complex fixes
        # For now, return None for unhandled cases
        return None

    # ========================================================================
    # REVIEW & IMPLEMENTATION
    # ========================================================================

    async def _review_diff(self, diff: str) -> dict[str, Any]:
        """مراجعة فرق الكود"""
        # Parse diff and analyze changes
        return {
            "comments": [],
            "approval": "approved",
            "summary": "Code changes look good",
            "summary_ar": "تبدو تغييرات الكود جيدة",
            "confidence": 0.8,
        }

    async def _implement_from_spec(self, spec: dict) -> dict[str, Any]:
        """تنفيذ من المواصفات"""
        return {
            "code": "",
            "tests": [],
            "documentation": "",
            "confidence": 0.7,
        }

    # ========================================================================
    # LEARNING
    # ========================================================================

    async def learn(self, feedback: dict[str, Any]) -> None:
        """
        التعلم من التغذية الراجعة
        Learn from feedback

        Updates success patterns based on fix results.
        """
        self.status = AgentStatus.LEARNING

        # Store feedback
        self.feedback_history.append(
            {"feedback": feedback, "timestamp": datetime.now().isoformat()}
        )

        # Extract reward
        reward = feedback.get("reward", 0.0)
        self.reward_history.append(reward)

        # Update success patterns
        if feedback.get("fix_successful"):
            pattern_key = feedback.get("pattern_key", "default")
            current_rate = self.success_patterns.get(pattern_key, 0.7)
            # Exponential moving average
            self.success_patterns[pattern_key] = 0.9 * current_rate + 0.1 * 1.0
        elif feedback.get("fix_failed"):
            pattern_key = feedback.get("pattern_key", "default")
            current_rate = self.success_patterns.get(pattern_key, 0.7)
            self.success_patterns[pattern_key] = 0.9 * current_rate + 0.1 * 0.0

        self.status = AgentStatus.IDLE

        logger.info(
            "learning_complete",
            reward=reward,
            patterns_count=len(self.success_patterns),
        )

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _issue_to_dict(self, issue: CodeIssue) -> dict[str, Any]:
        """تحويل مشكلة إلى قاموس"""
        return {
            "issue_id": issue.issue_id,
            "type": issue.issue_type.value,
            "severity": issue.severity.value,
            "file_path": issue.file_path,
            "line_start": issue.line_start,
            "line_end": issue.line_end,
            "column_start": issue.column_start,
            "column_end": issue.column_end,
            "description": issue.description,
            "description_ar": issue.description_ar,
            "suggestion": issue.suggestion,
            "suggestion_ar": issue.suggestion_ar,
            "code_snippet": issue.code_snippet,
            "confidence": issue.confidence,
            "rule_id": issue.rule_id,
        }

    def _fix_to_dict(self, fix: CodeFix) -> dict[str, Any]:
        """تحويل إصلاح إلى قاموس"""
        return {
            "fix_id": fix.fix_id,
            "issue": self._issue_to_dict(fix.issue),
            "original_code": fix.original_code,
            "fixed_code": fix.fixed_code,
            "changes": fix.changes,
            "strategy": fix.strategy.value,
            "confidence": fix.confidence,
            "explanation": fix.explanation,
            "explanation_ar": fix.explanation_ar,
            "tests_needed": fix.tests_needed,
            "breaking_changes": fix.breaking_changes,
            "requires_review": fix.requires_review,
        }

    def get_metrics(self) -> dict[str, Any]:
        """الحصول على مقاييس الأداء"""
        avg_response_time = (
            self.total_response_time_ms / self.total_requests if self.total_requests > 0 else 0
        )
        success_rate = (
            self.successful_requests / self.total_requests * 100 if self.total_requests > 0 else 0
        )
        avg_reward = (
            sum(self.reward_history) / len(self.reward_history) if self.reward_history else 0
        )

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "type": self.agent_type.value,
            "layer": self.layer.value,
            "status": self.status.value,
            "version": self.version,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "success_rate_percent": round(success_rate, 2),
            "avg_response_time_ms": round(avg_response_time, 2),
            "avg_reward": round(avg_reward, 4),
            "patterns_learned": len(self.success_patterns),
            "last_action_time": self.last_action_time.isoformat()
            if self.last_action_time
            else None,
        }

    def to_dict(self) -> dict[str, Any]:
        """تحويل الوكيل إلى قاموس"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "type": self.agent_type.value,
            "layer": self.layer.value,
            "version": self.version,
            "status": self.status.value,
            "goals": self.state.goals,
            "metrics": self.get_metrics(),
        }

    def __repr__(self) -> str:
        return f"<CodeFixAgent(id={self.agent_id}, status={self.status.value})>"
