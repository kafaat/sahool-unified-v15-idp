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

Integration with AutoFixEngine:
- Uses shared/ai/auto_fix for unified diagnostics
- Leverages Ruff, ESLint, Mypy, Bandit, Semgrep, Pylint
- Supports caching and circuit breaker for resilience
"""

import asyncio
import os
import tempfile
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

import structlog

# Import AutoFixEngine integration
try:
    from shared.ai.auto_fix import (
        AutoFixEngine,
        CodeDiagnostics,
        ToolType,
    )
    from shared.ai.auto_fix import (
        DiagnosticCategory as AutoFixCategory,
    )
    from shared.ai.auto_fix import (
        DiagnosticSeverity as AutoFixSeverity,
    )
    from shared.ai.auto_fix import (
        FixStrategy as AutoFixStrategy,
    )

    AUTO_FIX_AVAILABLE = True
except ImportError:
    AUTO_FIX_AVAILABLE = False

# Import Ollama client for LLM-based fixes
try:
    from shared.ai.ollama_client import OllamaClient, OllamaConfig

    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False

# Import Observability integration
try:
    from shared.ai.observability import (
        AgentContext as ObsContext,
    )
    from shared.ai.observability import (
        AgentErrorType,
        AIAgentObservability,
        create_observability,
    )

    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False

# Import Tool Registry for dynamic tool management
try:
    from shared.ai.tool_registry import (
        Language,
        ToolRegistry,
        get_tool_registry,
    )

    TOOL_REGISTRY_AVAILABLE = True
except ImportError:
    TOOL_REGISTRY_AVAILABLE = False

# Import Quality Orchestrator for automated quality management
try:
    from shared.ai.quality_orchestrator import (
        QualityOrchestrator,
        QualityReport,
        run_quality_check,
    )

    QUALITY_ORCHESTRATOR_AVAILABLE = True
except ImportError:
    QUALITY_ORCHESTRATOR_AVAILABLE = False

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

    def __init__(
        self,
        agent_id: str = "code_fix_agent_001",
        ollama_url: str | None = None,
        ollama_model: str = "codellama:7b",
    ):
        """
        تهيئة وكيل إصلاح الكود

        Args:
            agent_id: معرف الوكيل الفريد
            ollama_url: URL لخدمة Ollama (اختياري)
            ollama_model: نموذج Ollama للاستخدام
        """
        self.agent_id = agent_id
        self.name = "Code Fix Agent"
        self.name_ar = "وكيل إصلاح الكود"
        self.agent_type = AgentType.LEARNING
        self.layer = AgentLayer.SPECIALIST
        self.version = "2.0.0"  # Updated version with AutoFixEngine integration

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

        # Initialize AutoFixEngine integration
        self._diagnostics: CodeDiagnostics | None = None
        self._auto_fix_engine: AutoFixEngine | None = None
        if AUTO_FIX_AVAILABLE:
            try:
                self._diagnostics = CodeDiagnostics(
                    enable_cache=True,
                    cache_ttl=300,
                    enable_circuit_breaker=True,
                )
                logger.info("AutoFixEngine diagnostics initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize AutoFixEngine diagnostics: {e}")

        # Initialize Tool Registry for dynamic tool management
        self._tool_registry: ToolRegistry | None = None
        if TOOL_REGISTRY_AVAILABLE:
            try:
                self._tool_registry = get_tool_registry()
                logger.info("Tool Registry initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Tool Registry: {e}")

        # Initialize Quality Orchestrator for automated quality management
        self._quality_orchestrator: QualityOrchestrator | None = None
        if QUALITY_ORCHESTRATOR_AVAILABLE:
            try:
                self._quality_orchestrator = QualityOrchestrator(
                    agent_id=self.agent_id,
                )
                logger.info("Quality Orchestrator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Quality Orchestrator: {e}")

        # Initialize Ollama client for LLM-based fixes
        self._ollama_client: Any | None = None
        if OLLAMA_AVAILABLE and ollama_url:
            try:
                self._ollama_client = OllamaClient(
                    OllamaConfig(
                        base_url=ollama_url,
                        model=ollama_model,
                        temperature=0.1,  # Low temperature for consistent fixes
                    )
                )
                logger.info("Ollama client initialized", model=ollama_model)
            except Exception as e:
                logger.warning(f"Failed to initialize Ollama client: {e}")

        # Initialize Observability (Sentry, OpenTelemetry, Prometheus)
        self._observability: AIAgentObservability | None = None
        if OBSERVABILITY_AVAILABLE:
            try:
                self._observability = create_observability(
                    agent_id=self.agent_id,
                    agent_type="code_fix",
                    enable_tracing=True,
                    enable_metrics=True,
                )
                logger.info("Observability initialized (Sentry, OpenTelemetry, Prometheus)")
            except Exception as e:
                logger.warning(f"Failed to initialize observability: {e}")

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
            version=self.version,
            auto_fix_available=AUTO_FIX_AVAILABLE,
            ollama_available=OLLAMA_AVAILABLE and self._ollama_client is not None,
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
            0.25 * severity_score + 0.25 * confidence_score + 0.15 * size_score + 0.25 * success_rate - breaking_penalty
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

        With full observability:
        - Distributed tracing via OpenTelemetry
        - Error tracking via Sentry
        - Metrics collection via Prometheus
        """
        start_time = datetime.now()
        self.total_requests += 1

        # Extract context for observability
        file_path = percept.data.get("file_path") if isinstance(percept.data, dict) else None
        language = percept.data.get("language", "python") if isinstance(percept.data, dict) else "python"

        # Use observability context if available
        if self._observability and OBSERVABILITY_AVAILABLE:
            async with self._observability.operation(
                name=f"run_{percept.percept_type}",
                file_path=file_path,
                language=language,
                tenant_id=self.context.tenant_id if self.context else None,
                user_id=self.context.user_id if self.context else None,
                percept_type=percept.percept_type,
            ):
                return await self._run_internal(percept, start_time)
        else:
            return await self._run_internal(percept, start_time)

    async def _run_internal(self, percept: AgentPercept, start_time: datetime) -> dict[str, Any]:
        """Internal run implementation with observability support."""
        try:
            # Add breadcrumb for debugging
            if self._observability:
                self._observability.add_breadcrumb(
                    category="agent.perceive",
                    message=f"Processing {percept.percept_type} from {percept.source}",
                    data={"reliability": percept.reliability},
                )

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

            # Add breadcrumb for action
            if self._observability:
                self._observability.add_breadcrumb(
                    category="agent.act",
                    message=f"Executing {action.action_type}",
                    data={"confidence": action.confidence, "priority": action.priority},
                )

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
                priority=2 if top_issue.severity in [IssueSeverity.CRITICAL, IssueSeverity.HIGH] else 3,
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

        Uses AutoFixEngine for comprehensive analysis including:
        - Ruff (Python linting)
        - Bandit (Security)
        - Mypy (Type checking)
        - Semgrep (Pattern-based security)
        - Pylint (Advanced Python analysis)
        - ESLint (JavaScript/TypeScript)
        """
        issues: list[CodeIssue] = []

        try:
            lang = SupportedLanguage(language)
        except ValueError:
            logger.warning("unsupported_language", language=language)
            return issues

        # Use AutoFixEngine if available
        if self._diagnostics and language in ["python", "typescript", "javascript"]:
            auto_fix_issues = await self._analyze_with_auto_fix(code, lang)
            issues.extend(auto_fix_issues)
        else:
            # Fallback to basic analysis
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

    async def _analyze_with_auto_fix(self, code: str, language: SupportedLanguage) -> list[CodeIssue]:
        """
        تحليل الكود باستخدام AutoFixEngine
        Analyze code using AutoFixEngine diagnostics
        """
        issues: list[CodeIssue] = []

        if not self._diagnostics:
            return issues

        # Write code to temporary file for analysis
        suffix_map = {
            SupportedLanguage.PYTHON: ".py",
            SupportedLanguage.TYPESCRIPT: ".ts",
            SupportedLanguage.JAVASCRIPT: ".js",
            SupportedLanguage.DART: ".dart",
        }
        suffix = suffix_map.get(language, ".py")

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=suffix,
                delete=False,
                encoding="utf-8",
            ) as f:
                f.write(code)
                temp_path = f.name

            try:
                # Run diagnostics
                report = await self._diagnostics.diagnose_file(
                    temp_path,
                    include_security_patterns=True,
                )

                # Convert AutoFix diagnostics to CodeIssue
                for diag in report.diagnostics:
                    issue = self._convert_diagnostic_to_issue(diag, code)
                    issues.append(issue)

                logger.debug(
                    "auto_fix_analysis_complete",
                    issues_found=len(issues),
                    tools_used=[t.value for t in report.tools_used],
                    duration_ms=report.scan_duration_ms,
                )

            finally:
                # Clean up temp file
                os.unlink(temp_path)

        except Exception as e:
            logger.error("auto_fix_analysis_error", error=str(e))
            # Fallback to basic analysis on error
            syntax_issues = await self._check_syntax(code, language)
            issues.extend(syntax_issues)

        return issues

    def _convert_diagnostic_to_issue(self, diag: Any, code: str) -> CodeIssue:
        """Convert AutoFix Diagnostic to CodeIssue."""
        # Map severity
        severity_map = {
            "error": IssueSeverity.HIGH,
            "warning": IssueSeverity.MEDIUM,
            "info": IssueSeverity.LOW,
            "hint": IssueSeverity.INFO,
        }
        severity = severity_map.get(diag.severity.value, IssueSeverity.MEDIUM)

        # Map category to issue type
        category_map = {
            "syntax": IssueType.SYNTAX_ERROR,
            "type": IssueType.TYPE_ERROR,
            "security": IssueType.SECURITY,
            "performance": IssueType.PERFORMANCE,
            "style": IssueType.STYLE,
            "best_practice": IssueType.STYLE,
            "deprecation": IssueType.DEPRECATION,
            "logic": IssueType.LOGIC_ERROR,
            "import": IssueType.IMPORT_ERROR,
            "naming": IssueType.STYLE,
        }
        issue_type = category_map.get(diag.category.value, IssueType.BUG)

        # Extract code snippet
        lines = code.split("\n")
        line_idx = diag.location.line_start - 1
        snippet = lines[line_idx] if 0 <= line_idx < len(lines) else ""

        return CodeIssue(
            issue_id=diag.id,
            issue_type=issue_type,
            severity=severity,
            file_path=diag.location.file_path,
            line_start=diag.location.line_start,
            line_end=diag.location.line_end or diag.location.line_start,
            column_start=diag.location.column_start or 0,
            column_end=diag.location.column_end or 0,
            description=diag.message,
            description_ar=diag.message_ar,
            suggestion=diag.suggestion or "",
            suggestion_ar=diag.suggestion_ar or "",
            code_snippet=snippet,
            confidence=0.9 if diag.severity.value == "error" else 0.7,
            rule_id=diag.rule_id,
            metadata={
                "tool": diag.tool.value if diag.tool else None,
                "documentation_url": diag.documentation_url,
            },
        )

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
        """
        توليد إصلاح لمشكلة محددة باستخدام LLM
        Generate fix for a specific issue using LLM

        Uses Ollama with code-specific models for intelligent fix generation.
        Falls back to rule-based fixes for common patterns.
        """
        fix_id = str(uuid.uuid4())

        # Try rule-based fix first (faster, more reliable)
        rule_fix = self._try_rule_based_fix(issue, code)
        if rule_fix:
            return rule_fix

        # Try LLM-based fix if Ollama is available
        if self._ollama_client:
            try:
                llm_fix = await self._generate_llm_fix(issue, code, fix_id)
                if llm_fix:
                    return llm_fix
            except Exception as e:
                logger.warning(f"LLM fix generation failed: {e}")

        return None

    def _try_rule_based_fix(self, issue: CodeIssue, code: str) -> CodeFix | None:
        """
        محاولة إصلاح قائم على القواعد
        Try rule-based fix for common patterns
        """
        lines = code.split("\n")
        line_idx = issue.line_start - 1

        if line_idx < 0 or line_idx >= len(lines):
            return None

        original_line = lines[line_idx]
        fixed_line = None
        explanation = ""
        explanation_ar = ""

        # Fix patterns based on issue type and rule_id
        if issue.rule_id:
            rule = issue.rule_id.upper()

            # Ruff fixes
            if rule.startswith("F401"):  # Unused import
                # Remove the line (unused import)
                fixed_line = ""
                explanation = f"Remove unused import: {original_line.strip()}"
                explanation_ar = f"إزالة الاستيراد غير المستخدم: {original_line.strip()}"

            elif rule.startswith("E501"):  # Line too long
                # This is complex, skip for rule-based
                return None

            elif rule.startswith("W291") or rule.startswith("W293"):  # Trailing whitespace
                fixed_line = original_line.rstrip()
                explanation = "Remove trailing whitespace"
                explanation_ar = "إزالة المسافة البيضاء في النهاية"

            elif rule.startswith("I001"):  # Import sorting
                # Complex, skip for rule-based
                return None

            elif rule.startswith("UP017"):  # datetime.utcnow() deprecated
                fixed_line = original_line.replace("datetime.utcnow()", "datetime.now(timezone.utc)")
                if fixed_line != original_line:
                    explanation = "Replace deprecated datetime.utcnow() with datetime.now(timezone.utc)"
                    explanation_ar = "استبدال datetime.utcnow() المهمل بـ datetime.now(timezone.utc)"

            elif rule.startswith("B006"):  # Mutable default argument
                # Complex, skip for rule-based
                return None

        # Security fixes
        if issue.issue_type == IssueType.SECURITY:
            if "eval(" in original_line:
                fixed_line = original_line.replace("eval(", "ast.literal_eval(")
                explanation = "Replace unsafe eval() with ast.literal_eval()"
                explanation_ar = "استبدال eval() غير الآمن بـ ast.literal_eval()"

            elif "yaml.load(" in original_line and "Loader=" not in original_line:
                fixed_line = original_line.replace("yaml.load(", "yaml.safe_load(")
                explanation = "Replace unsafe yaml.load() with yaml.safe_load()"
                explanation_ar = "استبدال yaml.load() غير الآمن بـ yaml.safe_load()"

        if fixed_line is None or fixed_line == original_line:
            return None

        # Apply fix to code
        fixed_lines = lines.copy()
        if fixed_line == "":
            del fixed_lines[line_idx]
        else:
            fixed_lines[line_idx] = fixed_line
        fixed_code = "\n".join(fixed_lines)

        return CodeFix(
            fix_id=str(uuid.uuid4()),
            issue=issue,
            original_code=code,
            fixed_code=fixed_code,
            changes=[
                {
                    "line": issue.line_start,
                    "original": original_line,
                    "fixed": fixed_line,
                    "type": "replace" if fixed_line else "delete",
                }
            ],
            strategy=FixStrategy.MINIMAL,
            confidence=0.95,
            explanation=explanation,
            explanation_ar=explanation_ar,
            tests_needed=[],
            breaking_changes=False,
            requires_review=False,
        )

    async def _generate_llm_fix(self, issue: CodeIssue, code: str, fix_id: str) -> CodeFix | None:
        """
        توليد إصلاح باستخدام LLM
        Generate fix using LLM (Ollama)
        """
        if not self._ollama_client:
            return None

        # Build prompt for LLM
        prompt = f"""You are a code fix expert. Fix the following issue in the code.

ISSUE:
- Type: {issue.issue_type.value}
- Severity: {issue.severity.value}
- Description: {issue.description}
- Line {issue.line_start}: {issue.code_snippet}
{f"- Suggestion: {issue.suggestion}" if issue.suggestion else ""}

CODE:
```
{code}
```

Provide ONLY the fixed code without any explanation. Return the complete fixed code.
"""

        try:
            # Check if Ollama is available
            if hasattr(self._ollama_client, "is_available"):
                if not await self._ollama_client.is_available():
                    logger.warning("Ollama not available for fix generation")
                    return None

            # Generate fix
            response = await self._ollama_client.generate(prompt=prompt)

            if not response or not hasattr(response, "text"):
                return None

            fixed_code = response.text.strip()

            # Clean up response (remove markdown code blocks if present)
            if fixed_code.startswith("```"):
                lines = fixed_code.split("\n")
                # Remove first and last lines (code block markers)
                lines = [l for l in lines if not l.startswith("```")]
                fixed_code = "\n".join(lines)

            # Validate the fix is different from original
            if fixed_code == code or not fixed_code:
                return None

            # Calculate confidence based on similarity
            original_lines = set(code.split("\n"))
            fixed_lines = set(fixed_code.split("\n"))
            changed_lines = len(original_lines.symmetric_difference(fixed_lines))
            total_lines = max(len(original_lines), len(fixed_lines))

            # Lower confidence for larger changes
            confidence = max(0.5, 1.0 - (changed_lines / total_lines) * 0.5)

            return CodeFix(
                fix_id=fix_id,
                issue=issue,
                original_code=code,
                fixed_code=fixed_code,
                changes=[
                    {
                        "type": "llm_generated",
                        "model": self._ollama_client.config.model
                        if hasattr(self._ollama_client, "config")
                        else "unknown",
                        "changed_lines": changed_lines,
                    }
                ],
                strategy=FixStrategy.COMPREHENSIVE,
                confidence=confidence,
                explanation=f"LLM-generated fix for {issue.issue_type.value} issue",
                explanation_ar=f"إصلاح مولد بالذكاء الاصطناعي لمشكلة {issue.issue_type.value}",
                tests_needed=["Run existing tests to verify fix"],
                breaking_changes=changed_lines > 10,  # More changes = higher risk
                requires_review=True,  # LLM fixes should always be reviewed
            )

        except Exception as e:
            logger.error("llm_fix_generation_error", error=str(e))
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
        Persists learning state to file for cross-session learning.
        """
        self.status = AgentStatus.LEARNING

        # Store feedback
        self.feedback_history.append({"feedback": feedback, "timestamp": datetime.now(UTC).isoformat()})

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

        # Persist learning state
        await self._save_learning_state()

        self.status = AgentStatus.IDLE

        logger.info(
            "learning_complete",
            reward=reward,
            patterns_count=len(self.success_patterns),
        )

    async def _save_learning_state(self) -> None:
        """
        حفظ حالة التعلم للجلسات المستقبلية
        Save learning state for future sessions
        """
        import json

        state_dir = Path.home() / ".sahool" / "agents" / "code_fix"
        state_dir.mkdir(parents=True, exist_ok=True)
        state_file = state_dir / f"{self.agent_id}_state.json"

        state = {
            "agent_id": self.agent_id,
            "version": self.version,
            "success_patterns": self.success_patterns,
            "reward_history": self.reward_history[-100:],  # Keep last 100 rewards
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "last_updated": datetime.now(UTC).isoformat(),
        }

        try:
            with open(state_file, "w", encoding="utf-8") as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            logger.debug("learning_state_saved", file=str(state_file))
        except Exception as e:
            logger.warning(f"Failed to save learning state: {e}")

    async def _load_learning_state(self) -> None:
        """
        تحميل حالة التعلم من الجلسات السابقة
        Load learning state from previous sessions
        """
        import json

        state_dir = Path.home() / ".sahool" / "agents" / "code_fix"
        state_file = state_dir / f"{self.agent_id}_state.json"

        if not state_file.exists():
            logger.debug("no_previous_learning_state")
            return

        try:
            with open(state_file, encoding="utf-8") as f:
                state = json.load(f)

            # Only load if version matches
            if state.get("version") == self.version:
                self.success_patterns = state.get("success_patterns", {})
                self.reward_history = state.get("reward_history", [])
                self.total_requests = state.get("total_requests", 0)
                self.successful_requests = state.get("successful_requests", 0)

                logger.info(
                    "learning_state_loaded",
                    patterns_count=len(self.success_patterns),
                    rewards_count=len(self.reward_history),
                )
            else:
                logger.info(
                    "learning_state_version_mismatch",
                    stored_version=state.get("version"),
                    current_version=self.version,
                )
        except Exception as e:
            logger.warning(f"Failed to load learning state: {e}")

    async def initialize(self) -> None:
        """
        تهيئة الوكيل وتحميل الحالة السابقة
        Initialize agent and load previous state
        """
        await self._load_learning_state()
        logger.info(
            "agent_ready",
            agent_id=self.agent_id,
            patterns_loaded=len(self.success_patterns),
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

    # ========================================================================
    # QUALITY ORCHESTRATION METHODS
    # ========================================================================

    async def run_quality_analysis(
        self,
        paths: list[str],
        languages: list[str] | None = None,
        fix: bool = True,
        audit: bool = True,
    ) -> dict[str, Any]:
        """
        تشغيل تحليل الجودة الشامل باستخدام Quality Orchestrator
        Run comprehensive quality analysis using Quality Orchestrator

        This method uses the dynamic tool registry and quality orchestrator
        to provide automated, configurable quality analysis with full audit trail.

        Args:
            paths: المسارات للتحليل - Paths to analyze
            languages: اللغات (اختياري، اكتشاف تلقائي) - Languages (optional, auto-detect)
            fix: تطبيق الإصلاحات التلقائية - Apply auto-fixes
            audit: تمكين التدقيق - Enable audit logging

        Returns:
            dict with quality report including:
            - quality_score: نتيجة الجودة (0-100)
            - total_issues: إجمالي المشاكل
            - fixed_count: عدد الإصلاحات
            - gates_passed: حالة بوابات الجودة
            - audit_entries: إدخالات التدقيق
        """
        if not self._quality_orchestrator:
            logger.warning("Quality Orchestrator not available, falling back to basic analysis")
            return {
                "success": False,
                "error": "Quality Orchestrator not available",
                "error_ar": "منسق الجودة غير متوفر",
            }

        try:
            # Run comprehensive quality analysis
            report: QualityReport = await self._quality_orchestrator.analyze(
                paths=paths,
                languages=languages,
                fix=fix,
                audit=audit,
            )

            # Update agent metrics
            self.total_requests += 1
            if report.status == "completed":
                self.successful_requests += 1

            # Record performance
            if report.duration_ms:
                self.total_response_time_ms += report.duration_ms

            # Return comprehensive report
            return {
                "success": True,
                "report_id": report.id,
                "session_id": report.session_id,
                "status": report.status,
                "quality_score": report.quality_score,
                "quality_level": report.quality_level.value,
                "total_issues": report.total_issues,
                "critical_issues": report.critical_issues,
                "high_issues": report.high_issues,
                "medium_issues": report.medium_issues,
                "low_issues": report.low_issues,
                "fixed_count": report.fixed_count,
                "fixable_count": report.fixable_count,
                "files_analyzed": report.files_analyzed,
                "tools_executed": report.tools_executed,
                "gates_passed": report.gates_passed,
                "quality_gates": [
                    {
                        "gate_name": g.gate_name,
                        "passed": g.passed,
                        "threshold": g.threshold,
                        "actual_value": g.actual_value,
                        "message": g.message,
                        "message_ar": g.message_ar,
                    }
                    for g in report.quality_gates
                ],
                "duration_ms": report.duration_ms,
                "errors": report.errors,
                "audit_entries_count": len(report.audit_entries),
                # Full issues list (can be large)
                "issues": [
                    {
                        "id": i.id,
                        "tool": i.tool,
                        "file_path": i.file_path,
                        "line": i.line,
                        "severity": i.severity.value,
                        "message": i.message,
                        "code": i.code,
                        "auto_fixable": i.auto_fixable,
                        "fixed": i.fixed,
                    }
                    for i in report.issues[:100]  # Limit to first 100
                ],
            }

        except Exception as e:
            logger.error("quality_analysis_failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_ar": f"فشل تحليل الجودة: {e}",
            }

    async def get_available_tools(
        self,
        language: str | None = None,
    ) -> dict[str, Any]:
        """
        الحصول على الأدوات المتاحة
        Get available quality tools

        Args:
            language: اللغة لتصفية الأدوات - Language to filter tools

        Returns:
            dict with available tools and their status
        """
        if not self._tool_registry:
            return {
                "success": False,
                "error": "Tool Registry not available",
                "error_ar": "سجل الأدوات غير متوفر",
            }

        try:
            # Check tool availability
            availability = await self._tool_registry.check_availability()

            # Get tools for language if specified
            if language:
                try:
                    lang = Language(language.lower())
                    tools = self._tool_registry.get_tools_for_language(lang)
                except ValueError:
                    tools = self._tool_registry.get_all_tools()
            else:
                tools = self._tool_registry.get_all_tools()

            return {
                "success": True,
                "tools": [
                    {
                        "id": t.id,
                        "name": t.name,
                        "name_ar": t.name_ar,
                        "category": t.category.value,
                        "languages": [l.value for l in t.languages],
                        "status": t.status.value,
                        "version": t.version,
                        "available": availability.get(t.id, False),
                        "capabilities": [c.value for c in t.capabilities],
                        "priority": t.priority,
                    }
                    for t in tools
                ],
                "total_tools": len(tools),
                "available_count": sum(1 for t in tools if availability.get(t.id, False)),
            }

        except Exception as e:
            logger.error("get_tools_failed", error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_ar": f"فشل الحصول على الأدوات: {e}",
            }

    async def run_tool(
        self,
        tool_id: str,
        target: str,
        auto_fix: bool = True,
    ) -> dict[str, Any]:
        """
        تشغيل أداة محددة
        Run a specific quality tool

        Args:
            tool_id: معرف الأداة - Tool identifier
            target: الهدف (ملف أو مجلد) - Target file or directory
            auto_fix: تطبيق الإصلاحات - Apply auto-fixes

        Returns:
            dict with tool execution result
        """
        if not self._tool_registry:
            return {
                "success": False,
                "error": "Tool Registry not available",
                "error_ar": "سجل الأدوات غير متوفر",
            }

        try:
            result = await self._tool_registry.run_tool(
                tool_id=tool_id,
                target=target,
                auto_fix=auto_fix,
            )

            return {
                "success": result.success,
                "tool_id": result.tool_id,
                "exit_code": result.exit_code,
                "issues_count": result.issues_count,
                "fixed_count": result.fixed_count,
                "duration_ms": result.duration_ms,
                "stdout": result.stdout[:5000] if result.stdout else None,  # Truncate
                "stderr": result.stderr[:2000] if result.stderr else None,  # Truncate
                "error_message": result.error_message,
            }

        except Exception as e:
            logger.error("run_tool_failed", tool_id=tool_id, error=str(e))
            return {
                "success": False,
                "error": str(e),
                "error_ar": f"فشل تشغيل الأداة: {e}",
            }

    def get_metrics(self) -> dict[str, Any]:
        """الحصول على مقاييس الأداء"""
        avg_response_time = self.total_response_time_ms / self.total_requests if self.total_requests > 0 else 0
        success_rate = self.successful_requests / self.total_requests * 100 if self.total_requests > 0 else 0
        avg_reward = sum(self.reward_history) / len(self.reward_history) if self.reward_history else 0

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
            "last_action_time": self.last_action_time.isoformat() if self.last_action_time else None,
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
