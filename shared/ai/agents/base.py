"""
Base Autonomous Agent
=====================
الوكيل المستقل الأساسي

Inspired by:
- Dexter: Autonomous task decomposition and self-validation
- OpenCode: Dual-agent pattern (Plan/Build modes)
- Claude Code: Tool use patterns

Features:
- Task decomposition into structured steps
- Autonomous tool selection and execution
- Self-assessment and validation
- Loop detection and step limits
- Streaming progress updates

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import asyncio

# Tool Guard integration — enforce allowlist/blocklist before tool execution
import os as _os
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator, Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

from ..audit import get_audit_logger
from ..circuit_breaker import get_circuit_breaker
from ..llm_provider import LLMProviderManager, get_llm_manager

try:
    from ..guardrails.tool_guard import ToolCallContext, ToolGuard

    _tool_guard = ToolGuard()
    _HAS_TOOL_GUARD = True
except ImportError:
    _HAS_TOOL_GUARD = False
    _tool_guard = None
    # Fail-closed in production — tool guard is a security requirement
    if _os.getenv("ENVIRONMENT", "").lower() == "production":
        raise RuntimeError(
            "shared.ai.guardrails.tool_guard is required in production but could not be imported. "
            "Agent tool execution would be unguarded."
        )

logger = structlog.get_logger()


class AgentMode(StrEnum):
    """
    Agent operation mode.
    وضع تشغيل الوكيل

    Inspired by OpenCode's dual-agent pattern.
    """

    PLAN = "plan"  # Read-only analysis, no modifications
    EXECUTE = "execute"  # Full access, can make changes
    HYBRID = "hybrid"  # Plan then execute with approval


class AgentState(StrEnum):
    """Agent execution state."""

    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"


class CollaborationRole(StrEnum):
    """
    Role of agent in collaboration.
    دور الوكيل في التعاون
    """

    COORDINATOR = "coordinator"  # Coordinates multiple agents
    SPECIALIST = "specialist"  # Provides specialized expertise
    EXECUTOR = "executor"  # Executes tasks
    REVIEWER = "reviewer"  # Reviews and validates


class ConsensusType(StrEnum):
    """
    Type of consensus mechanism.
    نوع آلية الإجماع
    """

    UNANIMOUS = "unanimous"  # All agents must agree
    MAJORITY = "majority"  # >50% must agree
    WEIGHTED = "weighted"  # Weighted by agent expertise
    COORDINATOR_DECIDES = "coordinator_decides"  # Coordinator makes final call


class MemoryType(StrEnum):
    """
    Type of memory entry.
    نوع إدخال الذاكرة
    """

    EXPERIENCE = "experience"  # Past execution experience
    FEEDBACK = "feedback"  # User or system feedback
    LEARNING = "learning"  # Learned patterns
    CONTEXT = "context"  # Contextual information


@dataclass
class AgentCapability:
    """
    Capability of an agent.
    قدرة الوكيل
    """

    name: str
    name_ar: str
    description: str
    description_ar: str
    confidence: float = 1.0  # 0-1
    tags: list[str] = field(default_factory=list)


@dataclass
class MemoryEntry:
    """
    Memory entry for agent learning.
    إدخال ذاكرة لتعلم الوكيل
    """

    memory_id: str
    memory_type: MemoryType
    content: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0-1
    created_at: datetime = field(default_factory=datetime.utcnow)
    accessed_count: int = 0
    last_accessed: datetime | None = None


@dataclass
class DelegatedTask:
    """
    Task delegated to a sub-agent.
    مهمة مفوضة لوكيل فرعي
    """

    task_id: str
    agent_id: str
    agent_name: str
    description: str
    description_ar: str
    context: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"  # pending, in_progress, completed, failed
    result: Any = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None


@dataclass
class HelpRequest:
    """
    Request for help from another agent.
    طلب مساعدة من وكيل آخر
    """

    request_id: str
    requesting_agent: str
    problem: str
    problem_ar: str
    target_agent: str | None = None  # None = broadcast to all
    context: dict[str, Any] = field(default_factory=dict)
    urgency: str = "normal"  # low, normal, high, critical
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ConsensusProposal:
    """
    Proposal for multi-agent consensus.
    اقتراح للإجماع متعدد الوكلاء
    """

    proposal_id: str
    proposer_agent: str
    title: str
    title_ar: str
    description: str
    description_ar: str
    options: list[dict[str, Any]] = field(default_factory=list)
    votes: dict[str, str] = field(default_factory=dict)  # agent_id -> option_id
    consensus_type: ConsensusType = ConsensusType.MAJORITY
    status: str = "pending"  # pending, voting, decided, rejected
    decision: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: datetime | None = None


@dataclass
class AgentTool:
    """
    Tool definition for agent use.
    تعريف أداة لاستخدام الوكيل
    """

    name: str
    name_ar: str
    description: str
    description_ar: str
    input_schema: dict[str, Any]
    handler: Callable[..., Any]
    requires_approval: bool = False
    is_destructive: bool = False
    tags: list[str] = field(default_factory=list)

    def to_llm_format(self) -> dict[str, Any]:
        """Convert to LLM tool format (Anthropic/OpenAI compatible)."""
        return {
            "name": self.name,
            "description": f"{self.description}\n{self.description_ar}",
            "input_schema": self.input_schema,
        }


@dataclass
class ToolResult:
    """Result of tool execution."""

    tool_name: str
    success: bool
    result: Any
    error: str | None = None
    execution_time_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "tool_name": self.tool_name,
            "success": self.success,
            "result": self.result if self.success else None,
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
        }


@dataclass
class AgentStep:
    """
    A single step in agent execution.
    خطوة واحدة في تنفيذ الوكيل

    Inspired by Dexter's structured research steps.
    """

    step_id: str
    step_number: int
    description: str
    description_ar: str
    tool_name: str | None = None
    tool_input: dict[str, Any] = field(default_factory=dict)
    expected_output: str | None = None
    status: str = "pending"  # pending, in_progress, completed, failed, skipped
    result: ToolResult | None = None
    reasoning: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_number": self.step_number,
            "description": self.description,
            "description_ar": self.description_ar,
            "tool_name": self.tool_name,
            "tool_input": self.tool_input,
            "status": self.status,
            "result": self.result.to_dict() if self.result else None,
            "reasoning": self.reasoning,
        }


@dataclass
class StepResult:
    """Result of executing a step."""

    step: AgentStep
    success: bool
    output: Any
    validation_passed: bool = True
    validation_message: str | None = None
    needs_retry: bool = False
    next_steps: list[AgentStep] = field(default_factory=list)


class BaseAutonomousAgent(ABC):
    """
    Base class for autonomous AI agents.
    الفئة الأساسية للوكلاء المستقلين

    Features inspired by Dexter, OpenCode, and Claude Code:
    - Task decomposition into structured steps
    - Autonomous tool selection
    - Self-validation and refinement
    - Loop detection and step limits
    - Streaming progress updates

    Example:
        class CropAnalysisAgent(BaseAutonomousAgent):
            async def decompose_task(self, task):
                # Break down crop analysis into steps
                return [
                    AgentStep(description="Fetch satellite imagery"),
                    AgentStep(description="Calculate NDVI"),
                    AgentStep(description="Analyze crop health"),
                    AgentStep(description="Generate recommendations"),
                ]
    """

    # Safety limits (inspired by Dexter)
    MAX_STEPS = 50
    MAX_RETRIES = 3
    MAX_LOOP_ITERATIONS = 5
    TIMEOUT_SECONDS = 300

    def __init__(
        self,
        agent_id: str,
        name: str,
        name_ar: str,
        description: str,
        description_ar: str,
        mode: AgentMode = AgentMode.HYBRID,
        tenant_id: str = "sahool",
        llm_manager: LLMProviderManager | None = None,
        enable_audit: bool = True,
        collaboration_role: CollaborationRole = CollaborationRole.EXECUTOR,
    ):
        """
        Initialize autonomous agent.

        Args:
            agent_id: Unique agent identifier
            name: Agent name (English)
            name_ar: Agent name (Arabic)
            description: Agent description
            description_ar: Agent description (Arabic)
            mode: Operation mode (plan/execute/hybrid)
            tenant_id: Tenant ID for multi-tenancy
            llm_manager: LLM provider manager (auto-created if None)
            enable_audit: Enable audit logging
            collaboration_role: Role in multi-agent collaboration
        """
        self.agent_id = agent_id
        self.name = name
        self.name_ar = name_ar
        self.description = description
        self.description_ar = description_ar
        self.mode = mode
        self.tenant_id = tenant_id
        self.collaboration_role = collaboration_role

        # State management
        self.state = AgentState.IDLE
        self.current_task: str | None = None
        self.steps: list[AgentStep] = []
        self.current_step_index = 0
        self.execution_history: list[dict[str, Any]] = []

        # Tools
        self.tools: dict[str, AgentTool] = {}
        self._register_default_tools()

        # LLM and services
        self.llm = llm_manager or get_llm_manager(tenant_id)
        self.audit_logger = get_audit_logger(tenant_id) if enable_audit else None

        # Circuit breaker for resilience
        self.circuit_breaker = get_circuit_breaker(f"agent_{agent_id}")

        # Loop detection
        self._step_hashes: set[str] = set()
        self._retry_counts: dict[str, int] = {}

        # Statistics
        self.stats = {
            "tasks_completed": 0,
            "tasks_failed": 0,
            "steps_executed": 0,
            "tools_used": {},
            "total_time_ms": 0,
        }

        logger.info(
            "autonomous_agent_initialized",
            agent_id=self.agent_id,
            name=self.name,
            mode=self.mode.value,
            collaboration_role=self.collaboration_role.value,
        )

    @abstractmethod
    def _register_default_tools(self) -> None:
        """Register default tools for this agent type."""
        pass

    @abstractmethod
    async def decompose_task(self, task: str, context: dict[str, Any]) -> list[AgentStep]:
        """
        Decompose task into executable steps.
        تقسيم المهمة إلى خطوات قابلة للتنفيذ

        Inspired by Dexter's task decomposition.

        Args:
            task: Natural language task description
            context: Additional context (field_id, crop_type, etc.)

        Returns:
            List of agent steps
        """
        pass

    @abstractmethod
    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """
        Validate step result (self-assessment).
        التحقق من نتيجة الخطوة (التقييم الذاتي)

        Inspired by Dexter's self-validation.

        Args:
            step: Executed step
            result: Tool execution result
            context: Execution context

        Returns:
            Tuple of (is_valid, validation_message)
        """
        pass

    def register_tool(self, tool: AgentTool) -> None:
        """Register a tool for this agent."""
        self.tools[tool.name] = tool
        logger.debug(
            "tool_registered",
            agent_id=self.agent_id,
            tool_name=tool.name,
        )

    def get_available_tools(self) -> list[AgentTool]:
        """Get list of available tools."""
        return list(self.tools.values())

    async def run(
        self,
        task: str,
        context: dict[str, Any] | None = None,
        approval_callback: Callable[[list[AgentStep]], bool] | None = None,
    ) -> dict[str, Any]:
        """
        Run the agent on a task.
        تشغيل الوكيل على مهمة

        Args:
            task: Natural language task description
            context: Additional context
            approval_callback: Callback for approval in HYBRID mode

        Returns:
            Execution result
        """
        context = context or {}
        start_time = datetime.now(UTC)

        self.current_task = task
        self.state = AgentState.PLANNING
        self._step_hashes.clear()
        self._retry_counts.clear()

        try:
            # Step 1: Decompose task
            logger.info("task_decomposition_started", agent_id=self.agent_id, task=task[:100])
            self.steps = await self.decompose_task(task, context)

            if not self.steps:
                raise ValueError("Task decomposition returned no steps")

            logger.info(
                "task_decomposition_completed",
                agent_id=self.agent_id,
                num_steps=len(self.steps),
            )

            # Step 2: Approval for HYBRID mode
            if self.mode == AgentMode.HYBRID and approval_callback:
                self.state = AgentState.WAITING_APPROVAL
                if not approval_callback(self.steps):
                    return {
                        "success": False,
                        "status": "rejected",
                        "message": "Execution plan rejected",
                        "message_ar": "تم رفض خطة التنفيذ",
                        "steps": [s.to_dict() for s in self.steps],
                    }

            # Step 3: Execute (if not PLAN mode)
            if self.mode != AgentMode.PLAN:
                self.state = AgentState.EXECUTING
                await self._execute_steps(context)

            # Step 4: Generate final result
            self.state = AgentState.COMPLETED
            self.stats["tasks_completed"] += 1

            execution_time_ms = (datetime.now(UTC) - start_time).total_seconds() * 1000
            self.stats["total_time_ms"] += execution_time_ms

            result = self._generate_result(execution_time_ms)

            # Audit log
            if self.audit_logger:
                self.audit_logger.log_agent_execution(
                    agent_id=self.agent_id,
                    task=task[:500],
                    success=True,
                    execution_time_ms=execution_time_ms,
                    steps_executed=len([s for s in self.steps if s.status == "completed"]),
                )

            return result

        except Exception as e:
            self.state = AgentState.FAILED
            self.stats["tasks_failed"] += 1

            logger.error(
                "agent_execution_failed",
                agent_id=self.agent_id,
                task=task[:100],
                error=str(e),
            )

            return {
                "success": False,
                "status": "failed",
                "error": str(e),
                "steps": [s.to_dict() for s in self.steps],
            }

    async def run_stream(
        self,
        task: str,
        context: dict[str, Any] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Run agent with streaming progress updates.
        تشغيل الوكيل مع تحديثات التقدم المتدفقة

        Yields progress updates during execution.
        """
        context = context or {}
        self.current_task = task
        self.state = AgentState.PLANNING

        # Yield planning start
        yield {
            "type": "status",
            "state": "planning",
            "message": "Analyzing task and creating execution plan",
            "message_ar": "تحليل المهمة وإنشاء خطة التنفيذ",
        }

        # Decompose task
        self.steps = await self.decompose_task(task, context)

        yield {
            "type": "plan",
            "steps": [s.to_dict() for s in self.steps],
            "total_steps": len(self.steps),
        }

        if self.mode == AgentMode.PLAN:
            yield {
                "type": "complete",
                "mode": "plan_only",
                "steps": [s.to_dict() for s in self.steps],
            }
            return

        # Execute steps with streaming
        self.state = AgentState.EXECUTING

        for i, step in enumerate(self.steps):
            yield {
                "type": "step_start",
                "step_number": i + 1,
                "total_steps": len(self.steps),
                "description": step.description,
                "description_ar": step.description_ar,
            }

            step_result = await self._execute_single_step(step, context)

            yield {
                "type": "step_complete",
                "step_number": i + 1,
                "success": step_result.success,
                "output": step_result.output,
                "validation_passed": step_result.validation_passed,
            }

            if not step_result.success and not step_result.needs_retry:
                yield {
                    "type": "error",
                    "step_number": i + 1,
                    "error": str(step_result.output),
                }
                break

        # Final result
        self.state = AgentState.COMPLETED
        yield {
            "type": "complete",
            "success": all(s.status == "completed" for s in self.steps),
            "steps": [s.to_dict() for s in self.steps],
        }

    async def _execute_steps(self, context: dict[str, Any]) -> None:
        """Execute all steps with retry and validation."""
        for i, step in enumerate(self.steps):
            if i >= self.MAX_STEPS:
                logger.warning("max_steps_reached", agent_id=self.agent_id)
                break

            self.current_step_index = i
            step_result = await self._execute_single_step(step, context)

            # Add dynamically discovered steps
            if step_result.next_steps:
                insert_pos = i + 1
                for new_step in step_result.next_steps:
                    self.steps.insert(insert_pos, new_step)
                    insert_pos += 1

            if not step_result.success and not step_result.needs_retry:
                break

    async def _execute_single_step(
        self,
        step: AgentStep,
        context: dict[str, Any],
    ) -> StepResult:
        """Execute a single step with validation."""
        step.status = "in_progress"
        datetime.now(UTC)

        # Loop detection
        step_hash = f"{step.tool_name}:{hash(str(step.tool_input))}"
        if step_hash in self._step_hashes:
            iteration_count = self._retry_counts.get(step_hash, 0) + 1
            self._retry_counts[step_hash] = iteration_count

            if iteration_count > self.MAX_LOOP_ITERATIONS:
                logger.warning(
                    "loop_detected",
                    agent_id=self.agent_id,
                    step=step.description,
                )
                step.status = "failed"
                return StepResult(
                    step=step,
                    success=False,
                    output="Loop detected - same step executed too many times",
                    validation_passed=False,
                )

        self._step_hashes.add(step_hash)

        try:
            # Execute tool if specified
            if step.tool_name and step.tool_name in self.tools:
                tool = self.tools[step.tool_name]
                tool_result = await self._execute_tool(tool, step.tool_input)
                step.result = tool_result

                # Update stats
                self.stats["steps_executed"] += 1
                self.stats["tools_used"][tool.name] = self.stats["tools_used"].get(tool.name, 0) + 1

                if not tool_result.success:
                    step.status = "failed"
                    return StepResult(
                        step=step,
                        success=False,
                        output=tool_result.error,
                        validation_passed=False,
                    )

                # Self-validation (inspired by Dexter)
                is_valid, validation_msg = await self.validate_step_result(step, tool_result, context)

                if not is_valid:
                    retry_count = self._retry_counts.get(step.step_id, 0)
                    if retry_count < self.MAX_RETRIES:
                        self._retry_counts[step.step_id] = retry_count + 1
                        step.status = "pending"
                        return StepResult(
                            step=step,
                            success=False,
                            output=tool_result.result,
                            validation_passed=False,
                            validation_message=validation_msg,
                            needs_retry=True,
                        )

                step.status = "completed"
                step.completed_at = datetime.now(UTC)

                return StepResult(
                    step=step,
                    success=True,
                    output=tool_result.result,
                    validation_passed=is_valid,
                    validation_message=validation_msg,
                )

            # No tool - just mark as completed
            step.status = "completed"
            step.completed_at = datetime.now(UTC)

            return StepResult(
                step=step,
                success=True,
                output=None,
                validation_passed=True,
            )

        except Exception as e:
            step.status = "failed"
            logger.error(
                "step_execution_failed",
                agent_id=self.agent_id,
                step=step.description,
                error=str(e),
            )

            return StepResult(
                step=step,
                success=False,
                output=str(e),
                validation_passed=False,
            )

    async def _execute_tool(
        self,
        tool: AgentTool,
        inputs: dict[str, Any],
    ) -> ToolResult:
        """Execute a tool with guard checks and error handling."""
        start_time = datetime.now(UTC)

        # SECURITY: Run tool call through ToolGuard before execution
        if _HAS_TOOL_GUARD and _tool_guard is not None:
            try:
                context = ToolCallContext(
                    tool=tool.name,
                    args=inputs,
                    agent_id=getattr(self, "agent_id", None),
                )
                decision = _tool_guard.check(context)
                if not decision.allowed:
                    logger.warning(
                        "tool_guard_blocked",
                        tool=tool.name,
                        reason=decision.reason,
                        layer=decision.layer,
                    )
                    return ToolResult(
                        tool_name=tool.name,
                        success=False,
                        result=None,
                        error=f"Tool blocked by guard: {decision.reason}",
                        execution_time_ms=0,
                    )
            except Exception as guard_err:
                logger.error("tool_guard_error", tool=tool.name, error=str(guard_err))
                # Fail-closed: block tool execution when guard itself fails
                return ToolResult(
                    tool_name=tool.name,
                    success=False,
                    result=None,
                    error=f"Tool guard check failed: {type(guard_err).__name__}",
                    execution_time_ms=0,
                )

        try:
            # Use circuit breaker for resilience
            if asyncio.iscoroutinefunction(tool.handler):
                result = await self.circuit_breaker.call(tool.handler, **inputs)
            else:
                result = await self.circuit_breaker.call(asyncio.to_thread, tool.handler, **inputs)

            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return ToolResult(
                tool_name=tool.name,
                success=True,
                result=result,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return ToolResult(
                tool_name=tool.name,
                success=False,
                result=None,
                error=str(e),
                execution_time_ms=execution_time,
            )

    def _generate_result(self, execution_time_ms: float) -> dict[str, Any]:
        """Generate final execution result."""
        completed_steps = [s for s in self.steps if s.status == "completed"]
        failed_steps = [s for s in self.steps if s.status == "failed"]

        # Collect all step outputs
        outputs = []
        for step in completed_steps:
            if step.result:
                outputs.append(
                    {
                        "step": step.description,
                        "output": step.result.result,
                    }
                )

        return {
            "success": len(failed_steps) == 0,
            "status": "completed" if len(failed_steps) == 0 else "partial",
            "agent_id": self.agent_id,
            "task": self.current_task,
            "execution_time_ms": execution_time_ms,
            "steps_total": len(self.steps),
            "steps_completed": len(completed_steps),
            "steps_failed": len(failed_steps),
            "steps": [s.to_dict() for s in self.steps],
            "outputs": outputs,
            "summary": self._generate_summary(outputs),
        }

    def _generate_summary(self, outputs: list[dict[str, Any]]) -> str:
        """Generate summary of execution (to be overridden)."""
        return f"Executed {len(outputs)} steps successfully."

    def get_status(self) -> dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "name_ar": self.name_ar,
            "mode": self.mode.value,
            "state": self.state.value,
            "current_task": self.current_task,
            "current_step": self.current_step_index,
            "total_steps": len(self.steps),
            "stats": self.stats,
        }

    def reset(self) -> None:
        """Reset agent state."""
        self.state = AgentState.IDLE
        self.current_task = None
        self.steps = []
        self.current_step_index = 0
        self._step_hashes.clear()
        self._retry_counts.clear()
