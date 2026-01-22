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
- Sub-agent spawning and collaboration (NEW)
- Memory integration for learning (NEW)
- Consensus participation for multi-agent decisions (NEW)

Author: SAHOOL Platform Team
Updated: January 2026
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, AsyncIterator, TYPE_CHECKING
import asyncio
import uuid
import hashlib
import json
from collections import defaultdict

import structlog

from ..llm_provider import LLMProviderManager, LLMResponse, get_llm_manager
from ..audit import get_audit_logger
from ..circuit_breaker import CircuitBreaker, get_circuit_breaker

if TYPE_CHECKING:
    from .base import BaseAutonomousAgent

logger = structlog.get_logger()


class AgentMode(str, Enum):
    """
    Agent operation mode.
    وضع تشغيل الوكيل

    Inspired by OpenCode's dual-agent pattern.
    """
    PLAN = "plan"           # Read-only analysis, no modifications
    EXECUTE = "execute"     # Full access, can make changes
    HYBRID = "hybrid"       # Plan then execute with approval
    COLLABORATE = "collaborate"  # Multi-agent collaboration mode


class CollaborationRole(str, Enum):
    """
    Role in multi-agent collaboration.
    الدور في التعاون متعدد الوكلاء
    """
    COORDINATOR = "coordinator"  # Orchestrates other agents | المنسق
    SPECIALIST = "specialist"    # Domain expert | المتخصص
    VALIDATOR = "validator"      # Validates decisions | المدقق
    ADVISOR = "advisor"          # Provides recommendations | المستشار


class ConsensusType(str, Enum):
    """
    Type of consensus mechanism.
    نوع آلية الإجماع
    """
    MAJORITY = "majority"           # Simple majority vote | أغلبية بسيطة
    WEIGHTED = "weighted"           # Weighted by confidence | موزون بالثقة
    UNANIMOUS = "unanimous"         # All must agree | إجماع تام
    LEADER_DECIDES = "leader"       # Leader makes final call | القائد يقرر


class MemoryType(str, Enum):
    """
    Type of agent memory.
    نوع ذاكرة الوكيل
    """
    SHORT_TERM = "short_term"       # Current session | الجلسة الحالية
    WORKING = "working"             # Active task context | سياق المهمة النشطة
    EPISODIC = "episodic"           # Past experiences | التجارب السابقة
    SEMANTIC = "semantic"           # Domain knowledge | المعرفة المجالية
    PROCEDURAL = "procedural"       # Learned procedures | الإجراءات المكتسبة


class AgentState(str, Enum):
    """Agent execution state."""
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_APPROVAL = "waiting_approval"
    COLLABORATING = "collaborating"        # Working with other agents | التعاون مع وكلاء آخرين
    WAITING_CONSENSUS = "waiting_consensus"  # Waiting for consensus | انتظار الإجماع
    DELEGATING = "delegating"              # Delegating to sub-agent | التفويض لوكيل فرعي


@dataclass
class MemoryEntry:
    """
    Memory entry for agent learning.
    إدخال الذاكرة لتعلم الوكيل
    """
    entry_id: str
    memory_type: MemoryType
    content: dict[str, Any]
    context: dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5  # 0.0-1.0 importance score
    timestamp: datetime = field(default_factory=datetime.utcnow)
    access_count: int = 0
    last_accessed: datetime | None = None
    tags: list[str] = field(default_factory=list)
    embedding: list[float] | None = None  # For semantic search

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "memory_type": self.memory_type.value,
            "content": self.content,
            "context": self.context,
            "importance": self.importance,
            "timestamp": self.timestamp.isoformat(),
            "access_count": self.access_count,
            "tags": self.tags,
        }


@dataclass
class HelpRequest:
    """
    Request for help from another agent.
    طلب مساعدة من وكيل آخر
    """
    request_id: str
    from_agent_id: str
    to_agent_id: str | None  # None = broadcast to capable agents
    task_description: str
    task_description_ar: str
    required_capability: str
    context: dict[str, Any] = field(default_factory=dict)
    urgency: str = "normal"  # low, normal, high, critical
    created_at: datetime = field(default_factory=datetime.utcnow)
    deadline: datetime | None = None
    status: str = "pending"  # pending, accepted, in_progress, completed, rejected

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "from_agent_id": self.from_agent_id,
            "to_agent_id": self.to_agent_id,
            "task_description": self.task_description,
            "task_description_ar": self.task_description_ar,
            "required_capability": self.required_capability,
            "urgency": self.urgency,
            "status": self.status,
        }


@dataclass
class DelegatedTask:
    """
    Task delegated to a sub-agent.
    مهمة مفوضة لوكيل فرعي
    """
    task_id: str
    parent_agent_id: str
    sub_agent_id: str
    task: str
    task_ar: str
    context: dict[str, Any] = field(default_factory=dict)
    status: str = "pending"
    result: Any = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "parent_agent_id": self.parent_agent_id,
            "sub_agent_id": self.sub_agent_id,
            "task": self.task,
            "task_ar": self.task_ar,
            "status": self.status,
            "result": self.result,
        }


@dataclass
class ConsensusProposal:
    """
    Proposal for multi-agent consensus.
    اقتراح للإجماع متعدد الوكلاء
    """
    proposal_id: str
    proposer_agent_id: str
    topic: str
    topic_ar: str
    options: list[dict[str, Any]]
    consensus_type: ConsensusType = ConsensusType.WEIGHTED
    votes: dict[str, dict[str, Any]] = field(default_factory=dict)  # agent_id -> vote
    deadline: datetime | None = None
    status: str = "open"  # open, closed, decided
    final_decision: dict[str, Any] | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def add_vote(
        self,
        agent_id: str,
        option_index: int,
        confidence: float,
        reasoning: str,
    ) -> None:
        """Add a vote to the proposal."""
        self.votes[agent_id] = {
            "option_index": option_index,
            "confidence": confidence,
            "reasoning": reasoning,
            "timestamp": datetime.utcnow().isoformat(),
        }

    def calculate_result(self) -> dict[str, Any]:
        """Calculate consensus result based on votes."""
        if not self.votes:
            return {"decided": False, "reason": "No votes received"}

        if self.consensus_type == ConsensusType.MAJORITY:
            # Count votes per option
            vote_counts = defaultdict(int)
            for vote in self.votes.values():
                vote_counts[vote["option_index"]] += 1
            winner = max(vote_counts, key=vote_counts.get)
            return {
                "decided": True,
                "winning_option": winner,
                "votes_for_winner": vote_counts[winner],
                "total_votes": len(self.votes),
            }

        elif self.consensus_type == ConsensusType.WEIGHTED:
            # Weight votes by confidence
            weighted_scores = defaultdict(float)
            for vote in self.votes.values():
                weighted_scores[vote["option_index"]] += vote["confidence"]
            winner = max(weighted_scores, key=weighted_scores.get)
            return {
                "decided": True,
                "winning_option": winner,
                "weighted_score": weighted_scores[winner],
                "total_weight": sum(v["confidence"] for v in self.votes.values()),
            }

        elif self.consensus_type == ConsensusType.UNANIMOUS:
            options = [v["option_index"] for v in self.votes.values()]
            if len(set(options)) == 1:
                return {"decided": True, "winning_option": options[0], "unanimous": True}
            return {"decided": False, "reason": "No unanimous agreement"}

        return {"decided": False, "reason": "Unknown consensus type"}

    def to_dict(self) -> dict[str, Any]:
        return {
            "proposal_id": self.proposal_id,
            "proposer_agent_id": self.proposer_agent_id,
            "topic": self.topic,
            "topic_ar": self.topic_ar,
            "options": self.options,
            "consensus_type": self.consensus_type.value,
            "votes": self.votes,
            "status": self.status,
            "final_decision": self.final_decision,
        }


@dataclass
class AgentCapability:
    """
    Capability that an agent can provide.
    قدرة يمكن للوكيل تقديمها
    """
    name: str
    name_ar: str
    description: str
    description_ar: str
    domains: list[str] = field(default_factory=list)  # e.g., ["irrigation", "fertilizer"]
    skill_level: float = 0.8  # 0.0-1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "domains": self.domains,
            "skill_level": self.skill_level,
        }


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
    created_at: datetime = field(default_factory=datetime.utcnow)
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
        parent_agent: "BaseAutonomousAgent | None" = None,
        collaboration_role: CollaborationRole = CollaborationRole.SPECIALIST,
    ):
        """
        Initialize autonomous agent.
        تهيئة الوكيل المستقل

        Args:
            agent_id: Unique agent identifier | معرف الوكيل الفريد
            name: Agent name (English) | اسم الوكيل (إنجليزي)
            name_ar: Agent name (Arabic) | اسم الوكيل (عربي)
            description: Agent description | وصف الوكيل
            description_ar: Agent description (Arabic) | وصف الوكيل (عربي)
            mode: Operation mode (plan/execute/hybrid) | وضع التشغيل
            tenant_id: Tenant ID for multi-tenancy | معرف المستأجر
            llm_manager: LLM provider manager (auto-created if None)
            enable_audit: Enable audit logging | تمكين تسجيل التدقيق
            parent_agent: Parent agent if this is a sub-agent | الوكيل الأب إذا كان هذا وكيلاً فرعياً
            collaboration_role: Role in multi-agent collaboration | الدور في التعاون
        """
        self.agent_id = agent_id
        self.name = name
        self.name_ar = name_ar
        self.description = description
        self.description_ar = description_ar
        self.mode = mode
        self.tenant_id = tenant_id

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
            "delegations_made": 0,
            "help_requests_sent": 0,
            "consensus_participated": 0,
            "memories_stored": 0,
        }

        # === NEW: Sub-agent and Collaboration Support ===
        self.parent_agent = parent_agent
        self.collaboration_role = collaboration_role
        self.sub_agents: dict[str, "BaseAutonomousAgent"] = {}
        self.capabilities: list[AgentCapability] = []
        self._register_default_capabilities()

        # === NEW: Memory System for Learning ===
        self.memory: dict[MemoryType, list[MemoryEntry]] = {
            MemoryType.SHORT_TERM: [],
            MemoryType.WORKING: [],
            MemoryType.EPISODIC: [],
            MemoryType.SEMANTIC: [],
            MemoryType.PROCEDURAL: [],
        }
        self.memory_capacity: dict[MemoryType, int] = {
            MemoryType.SHORT_TERM: 50,
            MemoryType.WORKING: 20,
            MemoryType.EPISODIC: 500,
            MemoryType.SEMANTIC: 1000,
            MemoryType.PROCEDURAL: 200,
        }

        # === NEW: Collaboration State ===
        self.active_help_requests: dict[str, HelpRequest] = {}
        self.delegated_tasks: dict[str, DelegatedTask] = {}
        self.active_proposals: dict[str, ConsensusProposal] = {}
        self.collaboration_partners: dict[str, "BaseAutonomousAgent"] = {}

        # === NEW: Learning State ===
        self.feedback_history: list[dict[str, Any]] = []
        self.learned_patterns: dict[str, dict[str, Any]] = {}

        logger.info(
            "autonomous_agent_initialized",
            agent_id=self.agent_id,
            name=self.name,
            mode=self.mode.value,
            role=self.collaboration_role.value,
            is_sub_agent=parent_agent is not None,
        )

    def _register_default_capabilities(self) -> None:
        """
        Register default capabilities for this agent.
        تسجيل القدرات الافتراضية لهذا الوكيل
        Override in subclasses to add specific capabilities.
        """
        pass

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
        start_time = datetime.utcnow()

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

            execution_time_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
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
        start_time = datetime.utcnow()

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
                self.stats["tools_used"][tool.name] = (
                    self.stats["tools_used"].get(tool.name, 0) + 1
                )

                if not tool_result.success:
                    step.status = "failed"
                    return StepResult(
                        step=step,
                        success=False,
                        output=tool_result.error,
                        validation_passed=False,
                    )

                # Self-validation (inspired by Dexter)
                is_valid, validation_msg = await self.validate_step_result(
                    step, tool_result, context
                )

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
                step.completed_at = datetime.utcnow()

                return StepResult(
                    step=step,
                    success=True,
                    output=tool_result.result,
                    validation_passed=is_valid,
                    validation_message=validation_msg,
                )

            # No tool - just mark as completed
            step.status = "completed"
            step.completed_at = datetime.utcnow()

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
        """Execute a tool with error handling."""
        start_time = datetime.utcnow()

        try:
            # Use circuit breaker for resilience
            if asyncio.iscoroutinefunction(tool.handler):
                result = await self.circuit_breaker.call(tool.handler, **inputs)
            else:
                result = await self.circuit_breaker.call(
                    asyncio.to_thread, tool.handler, **inputs
                )

            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            return ToolResult(
                tool_name=tool.name,
                success=True,
                result=result,
                execution_time_ms=execution_time,
            )

        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000

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
                outputs.append({
                    "step": step.description,
                    "output": step.result.result,
                })

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

    # ========================================
    # SUB-AGENT SPAWNING
    # إنشاء الوكلاء الفرعيين
    # ========================================

    def spawn_sub_agent(
        self,
        agent_class: type["BaseAutonomousAgent"],
        agent_id: str | None = None,
        name: str | None = None,
        name_ar: str | None = None,
        mode: AgentMode | None = None,
        **kwargs: Any,
    ) -> "BaseAutonomousAgent":
        """
        Spawn a sub-agent for specialized tasks.
        إنشاء وكيل فرعي للمهام المتخصصة

        Args:
            agent_class: The agent class to instantiate | فئة الوكيل للإنشاء
            agent_id: Optional custom ID | معرف مخصص اختياري
            name: Optional custom name | اسم مخصص اختياري
            name_ar: Optional Arabic name | اسم عربي اختياري
            mode: Operating mode (defaults to EXECUTE) | وضع التشغيل
            **kwargs: Additional arguments for the agent | حجج إضافية

        Returns:
            The spawned sub-agent | الوكيل الفرعي المُنشأ

        Example:
            irrigation_agent = self.spawn_sub_agent(
                IrrigationSubAgent,
                agent_id="irrigation-sub-001"
            )
        """
        sub_agent_id = agent_id or f"{self.agent_id}-sub-{uuid.uuid4().hex[:8]}"

        sub_agent = agent_class(
            agent_id=sub_agent_id,
            name=name or f"{self.name} Sub-Agent",
            name_ar=name_ar or f"وكيل فرعي لـ {self.name_ar}",
            mode=mode or AgentMode.EXECUTE,
            tenant_id=self.tenant_id,
            llm_manager=self.llm,
            parent_agent=self,
            **kwargs,
        )

        self.sub_agents[sub_agent_id] = sub_agent

        logger.info(
            "sub_agent_spawned",
            parent_agent=self.agent_id,
            sub_agent=sub_agent_id,
            sub_agent_type=agent_class.__name__,
        )

        return sub_agent

    def get_sub_agent(self, agent_id: str) -> "BaseAutonomousAgent | None":
        """Get a sub-agent by ID."""
        return self.sub_agents.get(agent_id)

    def terminate_sub_agent(self, agent_id: str) -> bool:
        """
        Terminate and remove a sub-agent.
        إنهاء وإزالة وكيل فرعي
        """
        if agent_id in self.sub_agents:
            sub_agent = self.sub_agents.pop(agent_id)
            sub_agent.reset()
            logger.info(
                "sub_agent_terminated",
                parent_agent=self.agent_id,
                sub_agent=agent_id,
            )
            return True
        return False

    async def delegate_to_sub_agent(
        self,
        sub_agent_id: str,
        task: str,
        task_ar: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> DelegatedTask:
        """
        Delegate a task to a sub-agent.
        تفويض مهمة لوكيل فرعي

        Args:
            sub_agent_id: The sub-agent to delegate to
            task: Task description
            task_ar: Arabic task description
            context: Task context

        Returns:
            DelegatedTask with result
        """
        sub_agent = self.sub_agents.get(sub_agent_id)
        if not sub_agent:
            raise ValueError(f"Sub-agent not found: {sub_agent_id}")

        delegated = DelegatedTask(
            task_id=str(uuid.uuid4()),
            parent_agent_id=self.agent_id,
            sub_agent_id=sub_agent_id,
            task=task,
            task_ar=task_ar or task,
            context=context or {},
            status="in_progress",
        )

        self.delegated_tasks[delegated.task_id] = delegated
        self.state = AgentState.DELEGATING
        self.stats["delegations_made"] += 1

        logger.info(
            "task_delegated",
            parent_agent=self.agent_id,
            sub_agent=sub_agent_id,
            task_id=delegated.task_id,
        )

        try:
            result = await sub_agent.run(task=task, context=context)
            delegated.result = result
            delegated.status = "completed" if result.get("success") else "failed"
            delegated.completed_at = datetime.utcnow()

            # Learn from delegation outcome
            await self.store_memory(
                memory_type=MemoryType.EPISODIC,
                content={
                    "type": "delegation",
                    "task": task,
                    "sub_agent": sub_agent_id,
                    "success": result.get("success", False),
                    "result_summary": result.get("summary", ""),
                },
                importance=0.6,
                tags=["delegation", sub_agent.name],
            )

        except Exception as e:
            delegated.status = "failed"
            delegated.result = {"error": str(e)}
            logger.error("delegation_failed", task_id=delegated.task_id, error=str(e))

        self.state = AgentState.EXECUTING

        return delegated

    # ========================================
    # COLLABORATION METHODS
    # طرق التعاون
    # ========================================

    def register_capability(self, capability: AgentCapability) -> None:
        """
        Register a capability this agent can provide.
        تسجيل قدرة يمكن لهذا الوكيل تقديمها
        """
        self.capabilities.append(capability)
        logger.debug(
            "capability_registered",
            agent_id=self.agent_id,
            capability=capability.name,
        )

    def get_capabilities(self) -> list[AgentCapability]:
        """Get all registered capabilities."""
        return self.capabilities

    def has_capability(self, capability_name: str) -> bool:
        """Check if agent has a specific capability."""
        return any(c.name == capability_name for c in self.capabilities)

    def register_collaboration_partner(
        self,
        partner: "BaseAutonomousAgent",
    ) -> None:
        """
        Register another agent as a collaboration partner.
        تسجيل وكيل آخر كشريك للتعاون
        """
        self.collaboration_partners[partner.agent_id] = partner
        logger.info(
            "collaboration_partner_registered",
            agent_id=self.agent_id,
            partner_id=partner.agent_id,
        )

    async def request_help(
        self,
        task_description: str,
        task_description_ar: str,
        required_capability: str,
        context: dict[str, Any] | None = None,
        urgency: str = "normal",
        target_agent_id: str | None = None,
    ) -> HelpRequest:
        """
        Request help from another agent.
        طلب المساعدة من وكيل آخر

        Args:
            task_description: What help is needed | وصف المساعدة المطلوبة
            task_description_ar: Arabic description | الوصف بالعربية
            required_capability: The capability needed | القدرة المطلوبة
            context: Additional context | سياق إضافي
            urgency: low/normal/high/critical | الاستعجال
            target_agent_id: Specific agent to ask (None = broadcast)

        Returns:
            HelpRequest object | كائن طلب المساعدة

        Example:
            help_req = await self.request_help(
                task_description="Need irrigation schedule calculation",
                task_description_ar="أحتاج حساب جدول الري",
                required_capability="irrigation_calculation",
                urgency="high"
            )
        """
        request = HelpRequest(
            request_id=str(uuid.uuid4()),
            from_agent_id=self.agent_id,
            to_agent_id=target_agent_id,
            task_description=task_description,
            task_description_ar=task_description_ar,
            required_capability=required_capability,
            context=context or {},
            urgency=urgency,
        )

        self.active_help_requests[request.request_id] = request
        self.stats["help_requests_sent"] += 1

        logger.info(
            "help_requested",
            from_agent=self.agent_id,
            to_agent=target_agent_id or "broadcast",
            capability=required_capability,
            urgency=urgency,
        )

        # If target agent specified and is a partner, send directly
        if target_agent_id and target_agent_id in self.collaboration_partners:
            partner = self.collaboration_partners[target_agent_id]
            if partner.has_capability(required_capability):
                request.status = "accepted"
                result = await partner.run(
                    task=task_description,
                    context=context,
                )
                request.status = "completed"
                return request

        # Otherwise, find a capable partner
        for partner_id, partner in self.collaboration_partners.items():
            if partner.has_capability(required_capability):
                request.to_agent_id = partner_id
                request.status = "accepted"
                result = await partner.run(
                    task=task_description,
                    context=context,
                )
                request.status = "completed"
                return request

        # No capable partner found
        request.status = "no_capable_agent"
        logger.warning(
            "no_capable_agent_found",
            capability=required_capability,
        )

        return request

    async def delegate_task(
        self,
        task: str,
        task_ar: str,
        target_agent: "BaseAutonomousAgent | str",
        context: dict[str, Any] | None = None,
        wait_for_result: bool = True,
    ) -> DelegatedTask:
        """
        Delegate a task to another agent (partner or sub-agent).
        تفويض مهمة لوكيل آخر

        Args:
            task: Task description | وصف المهمة
            task_ar: Arabic description | الوصف بالعربية
            target_agent: Agent instance or ID | الوكيل المستهدف
            context: Task context | سياق المهمة
            wait_for_result: Wait for completion | انتظار الاكتمال

        Returns:
            DelegatedTask with result if waited
        """
        # Resolve target agent
        if isinstance(target_agent, str):
            agent = (
                self.sub_agents.get(target_agent)
                or self.collaboration_partners.get(target_agent)
            )
            if not agent:
                raise ValueError(f"Agent not found: {target_agent}")
            agent_id = target_agent
        else:
            agent = target_agent
            agent_id = agent.agent_id

        delegated = DelegatedTask(
            task_id=str(uuid.uuid4()),
            parent_agent_id=self.agent_id,
            sub_agent_id=agent_id,
            task=task,
            task_ar=task_ar,
            context=context or {},
            status="in_progress",
        )

        self.delegated_tasks[delegated.task_id] = delegated
        self.stats["delegations_made"] += 1

        logger.info(
            "task_delegated_to_partner",
            from_agent=self.agent_id,
            to_agent=agent_id,
            task_id=delegated.task_id,
        )

        if wait_for_result:
            try:
                result = await agent.run(task=task, context=context)
                delegated.result = result
                delegated.status = "completed" if result.get("success") else "failed"
                delegated.completed_at = datetime.utcnow()
            except Exception as e:
                delegated.status = "failed"
                delegated.result = {"error": str(e)}

        return delegated

    # ========================================
    # CONSENSUS PARTICIPATION
    # المشاركة في الإجماع
    # ========================================

    def create_consensus_proposal(
        self,
        topic: str,
        topic_ar: str,
        options: list[dict[str, Any]],
        consensus_type: ConsensusType = ConsensusType.WEIGHTED,
        deadline_minutes: int | None = None,
    ) -> ConsensusProposal:
        """
        Create a proposal for multi-agent consensus.
        إنشاء اقتراح للإجماع متعدد الوكلاء

        Args:
            topic: What to decide | موضوع القرار
            topic_ar: Arabic topic | الموضوع بالعربية
            options: List of options to vote on | قائمة الخيارات للتصويت
            consensus_type: How to reach consensus | نوع الإجماع
            deadline_minutes: Optional deadline | الموعد النهائي

        Returns:
            ConsensusProposal object

        Example:
            proposal = self.create_consensus_proposal(
                topic="Irrigation method for Field F003",
                topic_ar="طريقة الري للحقل F003",
                options=[
                    {"id": 0, "method": "drip", "cost": 500},
                    {"id": 1, "method": "sprinkler", "cost": 350},
                ],
                consensus_type=ConsensusType.WEIGHTED
            )
        """
        proposal = ConsensusProposal(
            proposal_id=str(uuid.uuid4()),
            proposer_agent_id=self.agent_id,
            topic=topic,
            topic_ar=topic_ar,
            options=options,
            consensus_type=consensus_type,
            deadline=datetime.utcnow() + timedelta(minutes=deadline_minutes) if deadline_minutes else None,
        )

        self.active_proposals[proposal.proposal_id] = proposal

        logger.info(
            "consensus_proposal_created",
            agent_id=self.agent_id,
            proposal_id=proposal.proposal_id,
            topic=topic[:50],
        )

        return proposal

    async def vote_on_proposal(
        self,
        proposal: ConsensusProposal,
        option_index: int,
        confidence: float,
        reasoning: str,
    ) -> None:
        """
        Cast a vote on a consensus proposal.
        التصويت على اقتراح الإجماع

        Args:
            proposal: The proposal to vote on | الاقتراح للتصويت
            option_index: Index of chosen option | فهرس الخيار المختار
            confidence: Confidence in the vote (0.0-1.0) | الثقة في التصويت
            reasoning: Explanation for the vote | شرح التصويت
        """
        proposal.add_vote(
            agent_id=self.agent_id,
            option_index=option_index,
            confidence=confidence,
            reasoning=reasoning,
        )

        self.stats["consensus_participated"] += 1

        logger.info(
            "consensus_vote_cast",
            agent_id=self.agent_id,
            proposal_id=proposal.proposal_id,
            option=option_index,
            confidence=confidence,
        )

    async def facilitate_consensus(
        self,
        proposal: ConsensusProposal,
        participating_agents: list["BaseAutonomousAgent"],
    ) -> dict[str, Any]:
        """
        Facilitate a consensus decision among agents.
        تسهيل قرار الإجماع بين الوكلاء

        Args:
            proposal: The proposal to decide on | الاقتراح للقرار
            participating_agents: Agents to participate | الوكلاء المشاركون

        Returns:
            Consensus result with final decision
        """
        self.state = AgentState.WAITING_CONSENSUS

        logger.info(
            "facilitating_consensus",
            proposal_id=proposal.proposal_id,
            num_agents=len(participating_agents),
        )

        # Collect votes from all participating agents
        for agent in participating_agents:
            if agent.agent_id not in proposal.votes:
                # Ask agent to analyze and vote
                vote = await self._get_agent_vote(agent, proposal)
                if vote:
                    proposal.add_vote(
                        agent_id=agent.agent_id,
                        **vote,
                    )

        # Calculate result
        result = proposal.calculate_result()
        proposal.final_decision = result
        proposal.status = "decided" if result.get("decided") else "no_consensus"

        self.state = AgentState.EXECUTING

        logger.info(
            "consensus_reached",
            proposal_id=proposal.proposal_id,
            decided=result.get("decided"),
            winning_option=result.get("winning_option"),
        )

        return result

    async def _get_agent_vote(
        self,
        agent: "BaseAutonomousAgent",
        proposal: ConsensusProposal,
    ) -> dict[str, Any] | None:
        """Get an agent's vote using LLM analysis."""
        try:
            prompt = f"""Analyze this decision and provide your vote.

Topic: {proposal.topic}
Topic (Arabic): {proposal.topic_ar}

Options:
{json.dumps(proposal.options, indent=2)}

Based on your expertise as {agent.name} ({agent.description}),
provide your vote as JSON with:
- option_index: The index of your chosen option
- confidence: Your confidence (0.0-1.0)
- reasoning: Brief explanation

Respond with JSON only."""

            response = await agent.llm.generate(
                prompt=prompt,
                temperature=0.2,
            )

            # Parse response
            import re
            json_match = re.search(r'\{[^}]+\}', response.text)
            if json_match:
                return json.loads(json_match.group())

        except Exception as e:
            logger.warning("failed_to_get_vote", agent_id=agent.agent_id, error=str(e))

        return None

    # ========================================
    # MEMORY INTEGRATION
    # تكامل الذاكرة
    # ========================================

    async def store_memory(
        self,
        memory_type: MemoryType,
        content: dict[str, Any],
        importance: float = 0.5,
        context: dict[str, Any] | None = None,
        tags: list[str] | None = None,
    ) -> MemoryEntry:
        """
        Store information in agent memory.
        تخزين المعلومات في ذاكرة الوكيل

        Args:
            memory_type: Type of memory to store in | نوع الذاكرة
            content: The content to store | المحتوى للتخزين
            importance: Importance score (0.0-1.0) | درجة الأهمية
            context: Additional context | سياق إضافي
            tags: Tags for retrieval | علامات للاسترجاع

        Returns:
            The stored MemoryEntry

        Example:
            await self.store_memory(
                memory_type=MemoryType.EPISODIC,
                content={
                    "event": "irrigation_recommendation",
                    "field_id": "F003",
                    "recommendation": "25mm",
                    "outcome": "farmer_accepted",
                },
                importance=0.8,
                tags=["irrigation", "success"]
            )
        """
        entry = MemoryEntry(
            entry_id=str(uuid.uuid4()),
            memory_type=memory_type,
            content=content,
            context=context or {},
            importance=importance,
            tags=tags or [],
        )

        # Enforce capacity limits
        memories = self.memory[memory_type]
        if len(memories) >= self.memory_capacity[memory_type]:
            # Remove least important memory
            memories.sort(key=lambda m: m.importance)
            memories.pop(0)

        memories.append(entry)
        self.stats["memories_stored"] += 1

        logger.debug(
            "memory_stored",
            agent_id=self.agent_id,
            memory_type=memory_type.value,
            importance=importance,
        )

        return entry

    async def recall_memories(
        self,
        memory_type: MemoryType | None = None,
        tags: list[str] | None = None,
        min_importance: float = 0.0,
        limit: int = 10,
        query: str | None = None,
    ) -> list[MemoryEntry]:
        """
        Recall memories from agent memory.
        استرجاع الذكريات من ذاكرة الوكيل

        Args:
            memory_type: Type of memory to search (None = all) | نوع الذاكرة
            tags: Filter by tags | تصفية بالعلامات
            min_importance: Minimum importance threshold | الحد الأدنى للأهمية
            limit: Maximum number of memories to return | الحد الأقصى للذكريات
            query: Text query for semantic search | استعلام نصي

        Returns:
            List of matching MemoryEntry objects
        """
        memories_to_search = []

        if memory_type:
            memories_to_search = self.memory[memory_type]
        else:
            for mem_list in self.memory.values():
                memories_to_search.extend(mem_list)

        # Filter by importance
        filtered = [m for m in memories_to_search if m.importance >= min_importance]

        # Filter by tags
        if tags:
            filtered = [
                m for m in filtered
                if any(t in m.tags for t in tags)
            ]

        # Sort by importance and recency
        filtered.sort(key=lambda m: (m.importance, m.timestamp), reverse=True)

        # Update access stats
        results = filtered[:limit]
        for memory in results:
            memory.access_count += 1
            memory.last_accessed = datetime.utcnow()

        return results

    async def learn_from_feedback(
        self,
        task_id: str,
        feedback: dict[str, Any],
    ) -> None:
        """
        Learn from farmer/user feedback to improve future recommendations.
        التعلم من ملاحظات المزارع لتحسين التوصيات المستقبلية

        Args:
            task_id: The task this feedback relates to | معرف المهمة
            feedback: Feedback data including:
                - rating: 1-5 star rating
                - outcome: success/partial/failure
                - comments: Text feedback
                - corrections: Any corrections to the advice
        """
        self.feedback_history.append({
            "task_id": task_id,
            "timestamp": datetime.utcnow().isoformat(),
            **feedback,
        })

        # Store as episodic memory
        await self.store_memory(
            memory_type=MemoryType.EPISODIC,
            content={
                "type": "feedback",
                "task_id": task_id,
                **feedback,
            },
            importance=0.7 if feedback.get("rating", 3) >= 4 else 0.8,  # Higher importance for negative
            tags=["feedback", feedback.get("outcome", "unknown")],
        )

        # Extract patterns for procedural memory
        if feedback.get("outcome") == "success" and feedback.get("rating", 0) >= 4:
            # This was a successful approach - learn the pattern
            task_context = next(
                (t for t in self.execution_history if t.get("task_id") == task_id),
                None
            )
            if task_context:
                pattern_key = self._generate_pattern_key(task_context)
                self.learned_patterns[pattern_key] = {
                    "context": task_context,
                    "feedback": feedback,
                    "success_count": self.learned_patterns.get(pattern_key, {}).get("success_count", 0) + 1,
                }

        logger.info(
            "learned_from_feedback",
            agent_id=self.agent_id,
            task_id=task_id,
            outcome=feedback.get("outcome"),
            rating=feedback.get("rating"),
        )

    def _generate_pattern_key(self, context: dict[str, Any]) -> str:
        """Generate a key for pattern matching."""
        key_parts = [
            context.get("task_type", "unknown"),
            context.get("crop_type", "unknown"),
            context.get("issue_type", "unknown"),
        ]
        return hashlib.sha256(":".join(key_parts).encode()).hexdigest()[:12]

    async def recall_similar_experience(
        self,
        context: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Recall similar past experiences to inform current decisions.
        استرجاع تجارب مماثلة لإرشاد القرارات الحالية

        Args:
            context: Current task context | سياق المهمة الحالية

        Returns:
            List of similar past experiences with outcomes
        """
        # Check learned patterns
        pattern_key = self._generate_pattern_key(context)
        if pattern_key in self.learned_patterns:
            return [self.learned_patterns[pattern_key]]

        # Search episodic memory
        memories = await self.recall_memories(
            memory_type=MemoryType.EPISODIC,
            min_importance=0.5,
            limit=5,
        )

        # Filter for relevant experiences
        relevant = []
        for memory in memories:
            content = memory.content
            if content.get("type") in ["feedback", "delegation", "task_completion"]:
                # Check similarity
                if (
                    content.get("crop_type") == context.get("crop_type")
                    or content.get("task_type") == context.get("task_type")
                ):
                    relevant.append({
                        "memory_id": memory.entry_id,
                        "content": content,
                        "importance": memory.importance,
                    })

        return relevant

    async def get_working_context(self) -> dict[str, Any]:
        """
        Get the current working memory context for task execution.
        الحصول على سياق الذاكرة العاملة الحالي لتنفيذ المهمة
        """
        working_memories = self.memory[MemoryType.WORKING]
        short_term = self.memory[MemoryType.SHORT_TERM]

        return {
            "working_memories": [m.to_dict() for m in working_memories[-10:]],
            "short_term_memories": [m.to_dict() for m in short_term[-10:]],
            "current_task": self.current_task,
            "current_step": self.current_step_index,
            "execution_history_recent": self.execution_history[-5:],
        }

    def clear_working_memory(self) -> None:
        """Clear working memory after task completion."""
        self.memory[MemoryType.WORKING].clear()
        self.memory[MemoryType.SHORT_TERM].clear()


# Import for timedelta used in consensus deadline
from datetime import timedelta
