"""
ReAct Agent Pattern
====================
نمط وكيل التفكير والعمل

Implements the ReAct (Reasoning + Acting) pattern for AI agents.
Based on "ReAct: Synergizing Reasoning and Acting in Language Models" paper.

Features:
- Explicit thought/action/observation traces
- Intermediate reasoning steps captured and validated
- Reflection for self-correction
- Confidence scoring at each step
- Full reasoning trace export for debugging

Author: SAHOOL Platform Team
Updated: January 2026
"""

import uuid
from abc import abstractmethod
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import structlog

from ..llm_provider import LLMProviderManager
from .base import (
    AgentMode,
    AgentStep,
    BaseAutonomousAgent,
    ToolResult,
)

logger = structlog.get_logger()


class ReActStepType(StrEnum):
    """نوع خطوة ReAct"""

    THOUGHT = "thought"  # Reasoning step
    ACTION = "action"  # Tool execution
    OBSERVATION = "observation"  # Result from action
    REFLECTION = "reflection"  # Self-assessment


@dataclass
class ReActThought:
    """
    Thought step in ReAct pattern.
    خطوة التفكير في نمط ReAct

    Captures the agent's reasoning before taking an action.
    """

    thought_id: str
    content: str  # The reasoning text
    content_ar: str  # Arabic version
    confidence: float  # How confident in this reasoning (0-1)
    alternatives: list[str] = field(default_factory=list)  # Alternative thoughts considered
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "thought_id": self.thought_id,
            "type": "thought",
            "content": self.content,
            "content_ar": self.content_ar,
            "confidence": self.confidence,
            "alternatives": self.alternatives,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReActAction:
    """
    Action step in ReAct pattern.
    خطوة العمل في نمط ReAct

    The action to take based on the thought.
    """

    action_id: str
    action_type: str  # Tool name or action type
    action_input: dict[str, Any]  # Input parameters
    rationale: str  # Why this action was chosen
    rationale_ar: str  # Arabic version
    expected_outcome: str  # What we expect to happen
    expected_outcome_ar: str
    confidence: float  # Confidence in action success (0-1)
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "action_id": self.action_id,
            "type": "action",
            "action_type": self.action_type,
            "action_input": self.action_input,
            "rationale": self.rationale,
            "rationale_ar": self.rationale_ar,
            "expected_outcome": self.expected_outcome,
            "expected_outcome_ar": self.expected_outcome_ar,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReActObservation:
    """
    Observation step in ReAct pattern.
    خطوة الملاحظة في نمط ReAct

    The result of executing an action.
    """

    observation_id: str
    action_id: str  # Reference to the action
    success: bool  # Whether action succeeded
    result: Any  # The actual result
    summary: str  # Human-readable summary
    summary_ar: str  # Arabic version
    execution_time_ms: float  # How long it took
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "observation_id": self.observation_id,
            "type": "observation",
            "action_id": self.action_id,
            "success": self.success,
            "result": self.result if isinstance(self.result, (str, int, float, bool, list, dict)) else str(self.result),
            "summary": self.summary,
            "summary_ar": self.summary_ar,
            "execution_time_ms": self.execution_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReActReflection:
    """
    Reflection step in ReAct pattern.
    خطوة التأمل في نمط ReAct

    Self-assessment after observation.
    """

    reflection_id: str
    observation_id: str  # Reference to the observation
    assessment: str  # What does this observation tell us
    assessment_ar: str  # Arabic version
    goal_progress: str  # Progress toward the goal
    goal_progress_ar: str
    next_step_suggestion: str  # What should we do next
    next_step_suggestion_ar: str
    confidence: float  # Confidence in the assessment
    should_continue: bool  # Should we continue with more steps
    needs_correction: bool  # Do we need to correct course
    correction_reason: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))

    def to_dict(self) -> dict[str, Any]:
        return {
            "reflection_id": self.reflection_id,
            "type": "reflection",
            "observation_id": self.observation_id,
            "assessment": self.assessment,
            "assessment_ar": self.assessment_ar,
            "goal_progress": self.goal_progress,
            "goal_progress_ar": self.goal_progress_ar,
            "next_step_suggestion": self.next_step_suggestion,
            "next_step_suggestion_ar": self.next_step_suggestion_ar,
            "confidence": self.confidence,
            "should_continue": self.should_continue,
            "needs_correction": self.needs_correction,
            "correction_reason": self.correction_reason,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class ReActStep:
    """
    Complete ReAct step with thought, action, observation, and reflection.
    خطوة ReAct كاملة مع التفكير والعمل والملاحظة والتأمل
    """

    step_id: str
    step_number: int
    thought: ReActThought
    action: ReActAction | None = None
    observation: ReActObservation | None = None
    reflection: ReActReflection | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "step_id": self.step_id,
            "step_number": self.step_number,
            "thought": self.thought.to_dict(),
            "action": self.action.to_dict() if self.action else None,
            "observation": self.observation.to_dict() if self.observation else None,
            "reflection": self.reflection.to_dict() if self.reflection else None,
        }

    @property
    def is_complete(self) -> bool:
        """Check if all components are filled."""
        return all([self.thought, self.action, self.observation, self.reflection])

    @property
    def overall_confidence(self) -> float:
        """Calculate overall confidence for this step."""
        confidences = [self.thought.confidence]
        if self.action:
            confidences.append(self.action.confidence)
        if self.reflection:
            confidences.append(self.reflection.confidence)
        return sum(confidences) / len(confidences)


@dataclass
class ReActTrace:
    """
    Complete reasoning trace for a ReAct execution.
    سجل الاستدلال الكامل لتنفيذ ReAct
    """

    trace_id: str
    task: str
    task_ar: str
    steps: list[ReActStep] = field(default_factory=list)
    final_answer: str | None = None
    final_answer_ar: str | None = None
    success: bool = False
    total_tokens_used: int = 0
    total_execution_time_ms: float = 0
    started_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "task": self.task,
            "task_ar": self.task_ar,
            "steps": [s.to_dict() for s in self.steps],
            "final_answer": self.final_answer,
            "final_answer_ar": self.final_answer_ar,
            "success": self.success,
            "total_tokens_used": self.total_tokens_used,
            "total_execution_time_ms": self.total_execution_time_ms,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "step_count": len(self.steps),
            "average_confidence": self.average_confidence,
        }

    @property
    def average_confidence(self) -> float:
        """Calculate average confidence across all steps."""
        if not self.steps:
            return 0.0
        return sum(s.overall_confidence for s in self.steps) / len(self.steps)

    def to_mermaid(self) -> str:
        """Export trace as Mermaid diagram for visualization."""
        lines = ["graph TD"]

        for i, step in enumerate(self.steps):
            step_id = f"S{i}"

            # Thought node
            thought_text = step.thought.content[:50].replace('"', "'")
            lines.append(f'    {step_id}T["{thought_text}..."]')

            # Action node
            if step.action:
                action_text = f"{step.action.action_type}"
                lines.append(f'    {step_id}A["{action_text}"]')
                lines.append(f"    {step_id}T --> {step_id}A")

            # Observation node
            if step.observation:
                obs_text = "✓" if step.observation.success else "✗"
                lines.append(f'    {step_id}O(("{obs_text}"))')
                if step.action:
                    lines.append(f"    {step_id}A --> {step_id}O")

            # Reflection node
            if step.reflection:
                refl_text = "Continue" if step.reflection.should_continue else "Done"
                lines.append(f"    {step_id}R{{{refl_text}}}")
                if step.observation:
                    lines.append(f"    {step_id}O --> {step_id}R")

            # Connect to next step
            if i < len(self.steps) - 1:
                next_id = f"S{i + 1}"
                if step.reflection:
                    lines.append(f"    {step_id}R --> {next_id}T")

        return "\n".join(lines)


class ReActAgent(BaseAutonomousAgent):
    """
    Agent implementing the ReAct pattern.
    وكيل ينفذ نمط ReAct

    Extends BaseAutonomousAgent with explicit reasoning traces.

    Key features:
    - Thought-Action-Observation-Reflection cycle
    - Explicit reasoning captured at each step
    - Self-correction through reflection
    - Confidence tracking throughout execution
    - Full trace export for debugging and learning

    Usage:
        class MyReActAgent(ReActAgent):
            async def generate_thought(self, context, goal, history):
                # Generate reasoning about what to do
                return ReActThought(...)

            async def select_action(self, thought, context):
                # Select action based on thought
                return ReActAction(...)

            async def reflect_on_observation(self, observation, goal, history):
                # Reflect on what happened
                return ReActReflection(...)
    """

    # ReAct-specific limits
    MAX_REACT_STEPS = 15
    MIN_CONFIDENCE_THRESHOLD = 0.3

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
        max_steps: int = 15,
        min_confidence: float = 0.3,
    ):
        """
        Initialize ReAct agent.

        Args:
            agent_id: Unique agent identifier
            name: Agent name (English)
            name_ar: Agent name (Arabic)
            description: Agent description
            description_ar: Agent description (Arabic)
            mode: Operation mode
            tenant_id: Tenant ID for multi-tenancy
            llm_manager: LLM provider manager
            enable_audit: Enable audit logging
            max_steps: Maximum ReAct steps
            min_confidence: Minimum confidence to continue
        """
        super().__init__(
            agent_id=agent_id,
            name=name,
            name_ar=name_ar,
            description=description,
            description_ar=description_ar,
            mode=mode,
            tenant_id=tenant_id,
            llm_manager=llm_manager,
            enable_audit=enable_audit,
        )

        self.max_steps = max_steps
        self.min_confidence = min_confidence

        # ReAct-specific state
        self.current_trace: ReActTrace | None = None
        self.react_history: list[ReActTrace] = []

        logger.info(
            "react_agent_initialized",
            agent_id=self.agent_id,
            max_steps=self.max_steps,
            min_confidence=self.min_confidence,
        )

    # ========================================================================
    # ABSTRACT METHODS - Must be implemented by subclasses
    # ========================================================================

    @abstractmethod
    async def generate_thought(
        self,
        context: dict[str, Any],
        goal: str,
        history: list[ReActStep],
    ) -> ReActThought:
        """
        Generate a thought about what to do next.
        توليد فكرة حول ما يجب فعله بعد ذلك

        This is where the agent reasons about the current situation.

        Args:
            context: Current execution context
            goal: The goal we're trying to achieve
            history: Previous ReAct steps

        Returns:
            ReActThought with reasoning
        """
        pass

    @abstractmethod
    async def select_action(
        self,
        thought: ReActThought,
        context: dict[str, Any],
    ) -> ReActAction:
        """
        Select an action based on the thought.
        اختيار إجراء بناءً على التفكير

        Args:
            thought: The reasoning that led to this action
            context: Current execution context

        Returns:
            ReActAction to execute
        """
        pass

    @abstractmethod
    async def reflect_on_observation(
        self,
        observation: ReActObservation,
        goal: str,
        history: list[ReActStep],
    ) -> ReActReflection:
        """
        Reflect on an observation and decide next steps.
        التأمل في الملاحظة وتحديد الخطوات التالية

        Args:
            observation: The observation to reflect on
            goal: The goal we're trying to achieve
            history: Previous ReAct steps

        Returns:
            ReActReflection with assessment and next step suggestion
        """
        pass

    @abstractmethod
    async def generate_final_answer(
        self,
        trace: ReActTrace,
        context: dict[str, Any],
    ) -> tuple[str, str]:
        """
        Generate the final answer from the trace.
        توليد الإجابة النهائية من السجل

        Args:
            trace: Complete ReAct trace
            context: Execution context

        Returns:
            Tuple of (answer_en, answer_ar)
        """
        pass

    # ========================================================================
    # REACT EXECUTION
    # ========================================================================

    async def run_react(
        self,
        task: str,
        task_ar: str,
        context: dict[str, Any] | None = None,
    ) -> ReActTrace:
        """
        Run the ReAct loop for a task.
        تشغيل حلقة ReAct لمهمة

        Args:
            task: Task description in English
            task_ar: Task description in Arabic
            context: Additional context

        Returns:
            Complete ReActTrace with all steps
        """
        context = context or {}
        start_time = datetime.now(UTC)

        # Initialize trace
        self.current_trace = ReActTrace(
            trace_id=str(uuid.uuid4()),
            task=task,
            task_ar=task_ar,
            started_at=start_time,
        )

        logger.info(
            "react_loop_started",
            agent_id=self.agent_id,
            task=task[:100],
            trace_id=self.current_trace.trace_id,
        )

        try:
            step_number = 0
            should_continue = True

            while should_continue and step_number < self.max_steps:
                step_number += 1

                # Execute one ReAct step
                react_step = await self._execute_react_step(
                    step_number=step_number,
                    goal=task,
                    context=context,
                )

                self.current_trace.steps.append(react_step)

                # Check if we should continue
                if react_step.reflection:
                    should_continue = react_step.reflection.should_continue

                    # Check confidence threshold
                    if react_step.overall_confidence < self.min_confidence:
                        logger.warning(
                            "confidence_below_threshold",
                            step=step_number,
                            confidence=react_step.overall_confidence,
                            threshold=self.min_confidence,
                        )
                        should_continue = False
                else:
                    should_continue = False

            # Generate final answer
            answer_en, answer_ar = await self.generate_final_answer(self.current_trace, context)
            self.current_trace.final_answer = answer_en
            self.current_trace.final_answer_ar = answer_ar
            self.current_trace.success = True

        except Exception as e:
            logger.error(
                "react_loop_failed",
                agent_id=self.agent_id,
                trace_id=self.current_trace.trace_id,
                error=str(e),
            )
            self.current_trace.success = False
            self.current_trace.final_answer = f"Error: {str(e)}"
            self.current_trace.final_answer_ar = f"خطأ: {str(e)}"

        # Finalize trace
        self.current_trace.completed_at = datetime.now(UTC)
        self.current_trace.total_execution_time_ms = (
            self.current_trace.completed_at - start_time
        ).total_seconds() * 1000

        # Store in history
        self.react_history.append(self.current_trace)

        # Audit log
        if self.audit_logger:
            self.audit_logger.log_agent_execution(
                agent_id=self.agent_id,
                task=task[:500],
                success=self.current_trace.success,
                execution_time_ms=self.current_trace.total_execution_time_ms,
                steps_executed=len(self.current_trace.steps),
            )

        logger.info(
            "react_loop_completed",
            agent_id=self.agent_id,
            trace_id=self.current_trace.trace_id,
            steps=len(self.current_trace.steps),
            success=self.current_trace.success,
            duration_ms=self.current_trace.total_execution_time_ms,
        )

        return self.current_trace

    async def _execute_react_step(
        self,
        step_number: int,
        goal: str,
        context: dict[str, Any],
    ) -> ReActStep:
        """Execute a single ReAct step."""
        step_id = f"{self.current_trace.trace_id}_step_{step_number}"
        history = self.current_trace.steps if self.current_trace else []

        # 1. THOUGHT - Generate reasoning
        logger.debug("react_generating_thought", step=step_number)
        thought = await self.generate_thought(context, goal, history)

        react_step = ReActStep(
            step_id=step_id,
            step_number=step_number,
            thought=thought,
        )

        # 2. ACTION - Select and prepare action
        logger.debug("react_selecting_action", step=step_number)
        action = await self.select_action(thought, context)
        react_step.action = action

        # 3. OBSERVATION - Execute action and observe
        logger.debug("react_executing_action", step=step_number, action=action.action_type)
        observation = await self._execute_action(action)
        react_step.observation = observation

        # 4. REFLECTION - Reflect on the observation
        logger.debug("react_reflecting", step=step_number)
        reflection = await self.reflect_on_observation(observation, goal, history + [react_step])
        react_step.reflection = reflection

        return react_step

    async def _execute_action(self, action: ReActAction) -> ReActObservation:
        """Execute an action and return the observation."""
        start_time = datetime.now(UTC)
        observation_id = f"obs_{action.action_id}"

        try:
            # Check if this is a tool we know about
            if action.action_type in self.tools:
                tool = self.tools[action.action_type]
                tool_result = await self._execute_tool(tool, action.action_input)

                return ReActObservation(
                    observation_id=observation_id,
                    action_id=action.action_id,
                    success=tool_result.success,
                    result=tool_result.result,
                    summary=f"Tool {action.action_type} {'succeeded' if tool_result.success else 'failed'}",
                    summary_ar=f"الأداة {action.action_type} {'نجحت' if tool_result.success else 'فشلت'}",
                    execution_time_ms=tool_result.execution_time_ms,
                )
            else:
                # Handle unknown action type
                return ReActObservation(
                    observation_id=observation_id,
                    action_id=action.action_id,
                    success=False,
                    result=None,
                    summary=f"Unknown action type: {action.action_type}",
                    summary_ar=f"نوع إجراء غير معروف: {action.action_type}",
                    execution_time_ms=(datetime.now(UTC) - start_time).total_seconds() * 1000,
                )

        except Exception as e:
            execution_time = (datetime.now(UTC) - start_time).total_seconds() * 1000

            return ReActObservation(
                observation_id=observation_id,
                action_id=action.action_id,
                success=False,
                result=str(e),
                summary=f"Action failed with error: {str(e)[:100]}",
                summary_ar=f"فشل الإجراء مع خطأ: {str(e)[:100]}",
                execution_time_ms=execution_time,
            )

    # ========================================================================
    # STREAMING SUPPORT
    # ========================================================================

    async def run_react_stream(
        self,
        task: str,
        task_ar: str,
        context: dict[str, Any] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """
        Run ReAct loop with streaming updates.
        تشغيل حلقة ReAct مع تحديثات متدفقة

        Yields progress updates as the agent executes.
        """
        context = context or {}
        start_time = datetime.now(UTC)

        # Initialize trace
        self.current_trace = ReActTrace(
            trace_id=str(uuid.uuid4()),
            task=task,
            task_ar=task_ar,
            started_at=start_time,
        )

        yield {
            "type": "start",
            "trace_id": self.current_trace.trace_id,
            "task": task,
            "task_ar": task_ar,
        }

        try:
            step_number = 0
            should_continue = True

            while should_continue and step_number < self.max_steps:
                step_number += 1
                history = self.current_trace.steps

                # Thought
                yield {"type": "thought_start", "step": step_number}
                thought = await self.generate_thought(context, task, history)
                yield {
                    "type": "thought_complete",
                    "step": step_number,
                    "thought": thought.to_dict(),
                }

                # Action
                yield {"type": "action_start", "step": step_number}
                action = await self.select_action(thought, context)
                yield {
                    "type": "action_complete",
                    "step": step_number,
                    "action": action.to_dict(),
                }

                # Observation
                yield {"type": "observation_start", "step": step_number}
                observation = await self._execute_action(action)
                yield {
                    "type": "observation_complete",
                    "step": step_number,
                    "observation": observation.to_dict(),
                }

                # Create step
                react_step = ReActStep(
                    step_id=f"{self.current_trace.trace_id}_step_{step_number}",
                    step_number=step_number,
                    thought=thought,
                    action=action,
                    observation=observation,
                )

                # Reflection
                yield {"type": "reflection_start", "step": step_number}
                reflection = await self.reflect_on_observation(observation, task, history + [react_step])
                react_step.reflection = reflection
                yield {
                    "type": "reflection_complete",
                    "step": step_number,
                    "reflection": reflection.to_dict(),
                }

                self.current_trace.steps.append(react_step)

                # Check if we should continue
                should_continue = reflection.should_continue

                if react_step.overall_confidence < self.min_confidence:
                    yield {
                        "type": "confidence_warning",
                        "step": step_number,
                        "confidence": react_step.overall_confidence,
                        "threshold": self.min_confidence,
                    }
                    should_continue = False

            # Generate final answer
            yield {"type": "generating_answer"}
            answer_en, answer_ar = await self.generate_final_answer(self.current_trace, context)
            self.current_trace.final_answer = answer_en
            self.current_trace.final_answer_ar = answer_ar
            self.current_trace.success = True

            yield {
                "type": "complete",
                "success": True,
                "answer": answer_en,
                "answer_ar": answer_ar,
                "trace": self.current_trace.to_dict(),
            }

        except Exception as e:
            self.current_trace.success = False
            self.current_trace.final_answer = f"Error: {str(e)}"
            self.current_trace.final_answer_ar = f"خطأ: {str(e)}"

            yield {
                "type": "error",
                "success": False,
                "error": str(e),
                "trace": self.current_trace.to_dict(),
            }

        # Finalize
        self.current_trace.completed_at = datetime.now(UTC)
        self.current_trace.total_execution_time_ms = (
            self.current_trace.completed_at - start_time
        ).total_seconds() * 1000
        self.react_history.append(self.current_trace)

    # ========================================================================
    # TRACE EXPORT & ANALYSIS
    # ========================================================================

    def export_trace(self, trace_id: str | None = None) -> dict[str, Any]:
        """
        Export a trace for debugging or learning.
        تصدير سجل للتصحيح أو التعلم
        """
        if trace_id:
            trace = next((t for t in self.react_history if t.trace_id == trace_id), None)
        else:
            trace = self.current_trace

        if not trace:
            return {"error": "Trace not found"}

        return {
            "trace": trace.to_dict(),
            "mermaid_diagram": trace.to_mermaid(),
            "summary": {
                "total_steps": len(trace.steps),
                "average_confidence": trace.average_confidence,
                "success": trace.success,
                "duration_ms": trace.total_execution_time_ms,
            },
        }

    def get_reasoning_summary(self, trace_id: str | None = None) -> str:
        """
        Get a human-readable summary of the reasoning.
        الحصول على ملخص مقروء للاستدلال
        """
        if trace_id:
            trace = next((t for t in self.react_history if t.trace_id == trace_id), None)
        else:
            trace = self.current_trace

        if not trace:
            return "No trace available"

        lines = [
            f"Task: {trace.task}",
            f"المهمة: {trace.task_ar}",
            "",
            "Reasoning Steps:",
            "=" * 50,
        ]

        for step in trace.steps:
            lines.append(f"\nStep {step.step_number}:")
            lines.append(f"  Thought: {step.thought.content}")
            if step.action:
                lines.append(f"  Action: {step.action.action_type}")
            if step.observation:
                lines.append(f"  Result: {'✓' if step.observation.success else '✗'} {step.observation.summary}")
            if step.reflection:
                lines.append(f"  Reflection: {step.reflection.assessment}")

        lines.append("")
        lines.append("=" * 50)
        lines.append(f"Final Answer: {trace.final_answer}")
        lines.append(f"الإجابة النهائية: {trace.final_answer_ar}")

        return "\n".join(lines)

    # ========================================================================
    # BASE CLASS IMPLEMENTATION
    # ========================================================================

    def _register_default_tools(self) -> None:
        """Register default tools - override in subclass."""
        pass

    async def decompose_task(
        self,
        task: str,
        context: dict[str, Any],
    ) -> list[AgentStep]:
        """
        Decompose task into steps.

        For ReAct agents, this runs the ReAct loop and converts to AgentSteps.
        """
        # Run ReAct loop
        trace = await self.run_react(
            task=task,
            task_ar=context.get("task_ar", task),
            context=context,
        )

        # Convert ReAct steps to AgentSteps
        agent_steps = []
        for react_step in trace.steps:
            if react_step.action:
                agent_step = AgentStep(
                    step_id=react_step.step_id,
                    step_number=react_step.step_number,
                    description=react_step.action.rationale,
                    description_ar=react_step.action.rationale_ar,
                    tool_name=react_step.action.action_type,
                    tool_input=react_step.action.action_input,
                    reasoning=react_step.thought.content,
                    status="completed" if react_step.observation and react_step.observation.success else "failed",
                )
                agent_steps.append(agent_step)

        return agent_steps

    async def validate_step_result(
        self,
        step: AgentStep,
        result: ToolResult,
        context: dict[str, Any],
    ) -> tuple[bool, str | None]:
        """
        Validate step result.

        For ReAct agents, validation is done through reflection.
        """
        # In ReAct, validation is part of the reflection step
        return result.success, None if result.success else result.error


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def create_thought(
    content: str,
    content_ar: str,
    confidence: float = 0.8,
    alternatives: list[str] | None = None,
) -> ReActThought:
    """Helper to create a ReActThought."""
    return ReActThought(
        thought_id=str(uuid.uuid4()),
        content=content,
        content_ar=content_ar,
        confidence=confidence,
        alternatives=alternatives or [],
    )


def create_action(
    action_type: str,
    action_input: dict[str, Any],
    rationale: str,
    rationale_ar: str,
    expected_outcome: str,
    expected_outcome_ar: str,
    confidence: float = 0.8,
) -> ReActAction:
    """Helper to create a ReActAction."""
    return ReActAction(
        action_id=str(uuid.uuid4()),
        action_type=action_type,
        action_input=action_input,
        rationale=rationale,
        rationale_ar=rationale_ar,
        expected_outcome=expected_outcome,
        expected_outcome_ar=expected_outcome_ar,
        confidence=confidence,
    )


def create_reflection(
    observation_id: str,
    assessment: str,
    assessment_ar: str,
    goal_progress: str,
    goal_progress_ar: str,
    next_step_suggestion: str,
    next_step_suggestion_ar: str,
    confidence: float = 0.8,
    should_continue: bool = True,
    needs_correction: bool = False,
    correction_reason: str | None = None,
) -> ReActReflection:
    """Helper to create a ReActReflection."""
    return ReActReflection(
        reflection_id=str(uuid.uuid4()),
        observation_id=observation_id,
        assessment=assessment,
        assessment_ar=assessment_ar,
        goal_progress=goal_progress,
        goal_progress_ar=goal_progress_ar,
        next_step_suggestion=next_step_suggestion,
        next_step_suggestion_ar=next_step_suggestion_ar,
        confidence=confidence,
        should_continue=should_continue,
        needs_correction=needs_correction,
        correction_reason=correction_reason,
    )
