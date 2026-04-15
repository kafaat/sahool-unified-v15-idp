"""
AgentRunner for OpenMultiAgent
===============================
منفذ الوكيل لإطار OpenMultiAgent

Provides the core conversation loop that ties together an LLM adapter,
a tool registry, and shared memory to execute agent tasks.

يوفر حلقة المحادثة الأساسية التي تربط بين محول LLM وسجل الأدوات
والذاكرة المشتركة لتنفيذ مهام الوكلاء.

Execution flow:
    1. Build context from memory + task
    2. Call LLM with available tools
    3. If LLM requests a tool -> dispatch, add result to context
    4. Repeat until LLM returns a final answer or max_iterations reached
    5. Store result in memory

Author: SAHOOL Platform Team
Updated: April 2026
"""

from __future__ import annotations

import asyncio
import json
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any
from uuid import uuid4

import structlog
from pydantic import BaseModel, ConfigDict, Field

from shared.ai.orchestration.models import (
    AgentCapability,
    Task,
    TaskResult,
    TaskStatus,
)

from .llm_adapter import LLMAdapter

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Supporting types
# ---------------------------------------------------------------------------


class RunnerStatus(StrEnum):
    """Lifecycle status of an AgentRunner. | حالة دورة حياة منفذ الوكيل."""

    IDLE = "idle"
    RUNNING = "running"
    WAITING_TOOL = "waiting_tool"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class MessageRole(StrEnum):
    """Role of a message in the conversation context. | دور الرسالة في سياق المحادثة."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


@dataclass
class Message:
    """A single message in the conversation history. | رسالة واحدة في سجل المحادثة."""

    role: MessageRole
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


class AgentConfig(BaseModel):
    """
    Configuration for an agent managed by :class:`AgentRunner`.

    إعدادات وكيل يديره منفذ الوكيل.
    """

    model_config = ConfigDict(use_enum_values=True)

    agent_id: str = Field(
        default_factory=lambda: f"agent-{uuid4().hex[:8]}",
        description="Unique agent identifier | معرف الوكيل الفريد",
    )
    name: str = Field(description="Agent display name (English)")
    name_ar: str = Field(default="", description="Agent display name (Arabic) | اسم الوكيل بالعربية")
    role: str = Field(
        default="general",
        description="Agent role description | وصف دور الوكيل",
    )
    system_prompt: str = Field(
        default="You are a helpful agricultural AI assistant for the SAHOOL platform.",
        description="System prompt injected at the start of each run",
    )
    capabilities: list[AgentCapability] = Field(default_factory=list)
    max_iterations: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum tool-use iterations per run | الحد الأقصى لتكرارات استخدام الأدوات",
    )
    iteration_timeout_s: float = Field(
        default=60.0,
        gt=0,
        description="Timeout per iteration in seconds | المهلة لكل تكرار بالثواني",
    )
    available_tools: list[str] = Field(
        default_factory=list,
        description="Tool names this agent is allowed to use | أسماء الأدوات المتاحة للوكيل",
    )


# ---------------------------------------------------------------------------
# Shared memory interface
# ---------------------------------------------------------------------------


class SharedMemory:
    """
    Simple key-value shared state store for inter-agent communication.

    مخزن حالة مشتركة بسيط بنمط مفتاح-قيمة للتواصل بين الوكلاء.
    """

    def __init__(self) -> None:
        self._store: dict[str, Any] = {}
        self._history: list[dict[str, Any]] = []

    def get(self, key: str, default: Any = None) -> Any:
        return self._store.get(key, default)

    def set(self, key: str, value: Any, *, agent_id: str = "") -> None:
        self._store[key] = value
        self._history.append(
            {
                "action": "set",
                "key": key,
                "agent_id": agent_id,
                "timestamp": datetime.now(UTC).isoformat(),
            }
        )

    def delete(self, key: str) -> None:
        self._store.pop(key, None)

    def keys(self) -> list[str]:
        return list(self._store.keys())

    def snapshot(self) -> dict[str, Any]:
        """Return a shallow copy of the current store. | إرجاع نسخة سطحية من المخزن الحالي."""
        return dict(self._store)

    def get_history(self) -> list[dict[str, Any]]:
        return list(self._history)


# ---------------------------------------------------------------------------
# Tool dispatch protocol
# ---------------------------------------------------------------------------


class ToolDispatcher:
    """
    Bridges the :class:`AgentRunner` to the platform :class:`ToolRegistry`.

    يربط منفذ الوكيل بسجل الأدوات في المنصة.

    Agents express tool calls as ``{"tool": "<name>", "args": {...}}``
    in their LLM output.  The dispatcher maps the name to a registered
    handler and executes it.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, Any] = {}

    def register(self, name: str, handler: Any) -> None:
        """Register a callable handler for *name*."""
        self._handlers[name] = handler

    async def dispatch(self, tool_name: str, args: dict[str, Any]) -> Any:
        """
        Execute a registered tool.

        تنفيذ أداة مسجلة.

        Args:
            tool_name: The tool identifier.
            args: Keyword arguments to pass to the tool handler.

        Returns:
            The tool's return value, serialised to a string for the LLM.

        Raises:
            KeyError: If *tool_name* is not registered.
        """
        handler = self._handlers.get(tool_name)
        if handler is None:
            available = ", ".join(sorted(self._handlers)) or "(none)"
            raise KeyError(f"Tool '{tool_name}' is not registered. Available: {available}")
        logger.info("tool_dispatch.start", tool=tool_name, args_keys=list(args.keys()))
        start = time.monotonic()
        try:
            if asyncio.iscoroutinefunction(handler):
                result = await handler(**args)
            else:
                result = handler(**args)
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.info("tool_dispatch.done", tool=tool_name, elapsed_ms=round(elapsed_ms, 1))
            return result
        except Exception:
            logger.exception("tool_dispatch.error", tool=tool_name)
            raise

    @property
    def registered_tools(self) -> list[str]:
        return sorted(self._handlers)


# ---------------------------------------------------------------------------
# Tool-call parser
# ---------------------------------------------------------------------------

_TOOL_CALL_MARKER = '{"tool":'


def _parse_tool_call(text: str) -> tuple[str, dict[str, Any]] | None:
    """
    Attempt to extract a JSON tool-call from the LLM output.

    Expected format::

        {"tool": "tool_name", "args": {"key": "value"}}

    Returns ``(tool_name, args)`` or ``None`` if no tool call is found.
    """
    idx = text.find(_TOOL_CALL_MARKER)
    if idx == -1:
        return None

    # Find the matching closing brace (simple depth counter).
    depth = 0
    start = idx
    for i in range(start, len(text)):
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    obj = json.loads(text[start : i + 1])
                    tool_name = obj.get("tool")
                    args = obj.get("args", {})
                    if isinstance(tool_name, str) and isinstance(args, dict):
                        return tool_name, args
                except (json.JSONDecodeError, TypeError):
                    return None
                break
    return None


# ---------------------------------------------------------------------------
# AgentRunner
# ---------------------------------------------------------------------------


class AgentRunner:
    """
    Conversation loop and tool dispatch engine for a single agent.

    محرك حلقة المحادثة وإرسال الأدوات لوكيل واحد.

    The runner ties together:

    * An :class:`AgentConfig` describing the agent's identity and limits.
    * An :class:`LLMAdapter` for inference.
    * A :class:`ToolDispatcher` for executing tool calls.
    * A :class:`SharedMemory` for cross-agent state.

    Example::

        runner = AgentRunner(
            agent=AgentConfig(name="Crop Expert", name_ar="خبير المحاصيل"),
            llm=adapter,
            tools=dispatcher,
            memory=SharedMemory(),
        )
        result = await runner.run(task)
    """

    def __init__(
        self,
        agent: AgentConfig,
        llm: LLMAdapter,
        tools: ToolDispatcher,
        memory: SharedMemory,
    ) -> None:
        self.agent = agent
        self.llm = llm
        self.tools = tools
        self.memory = memory

        self._status = RunnerStatus.IDLE
        self._conversation: list[Message] = []
        self._iteration_count = 0

    # -- properties --------------------------------------------------------

    @property
    def status(self) -> RunnerStatus:
        return self._status

    @property
    def conversation(self) -> list[Message]:
        """Return a copy of the current conversation history."""
        return list(self._conversation)

    # -- public interface --------------------------------------------------

    async def run(self, task: Task) -> TaskResult:
        """
        Execute the full conversation loop for *task*.

        تنفيذ حلقة المحادثة الكاملة للمهمة.

        Steps:
            1. Build context from memory + task description.
            2. Call LLM.
            3. If LLM output contains a tool call -> dispatch, append
               result to conversation, goto 2.
            4. Repeat until a final answer is produced or
               ``max_iterations`` is exceeded.
            5. Store the result in shared memory.

        Args:
            task: The :class:`Task` to execute.

        Returns:
            A :class:`TaskResult` with the outcome.
        """
        self._status = RunnerStatus.RUNNING
        self._conversation.clear()
        self._iteration_count = 0
        started_at = datetime.now(UTC)
        start_mono = time.monotonic()

        log = logger.bind(agent_id=self.agent.agent_id, task_id=task.task_id)
        log.info("agent_runner.start", task_desc=task.description[:80])

        # 1. Build initial context ----------------------------------------
        self._conversation.append(
            Message(
                role=MessageRole.SYSTEM,
                content=self.agent.system_prompt,
            )
        )

        # Inject memory snapshot as context
        mem_snapshot = self.memory.snapshot()
        if mem_snapshot:
            self._conversation.append(
                Message(
                    role=MessageRole.SYSTEM,
                    content=f"Shared memory context:\n{json.dumps(mem_snapshot, default=str, ensure_ascii=False)}",
                )
            )

        # Inject available tools
        if self.tools.registered_tools:
            tool_list = ", ".join(self.tools.registered_tools)
            self._conversation.append(
                Message(
                    role=MessageRole.SYSTEM,
                    content=(
                        f"You have the following tools available: {tool_list}. "
                        "To use a tool, respond with a JSON object: "
                        '{"tool": "<name>", "args": {<arguments>}}. '
                        "When you have the final answer, respond normally without a tool call."
                    ),
                )
            )

        # Inject task context
        task_context = f"Task: {task.description}\nTask (AR): {task.description_ar}\nPriority: {task.priority}\n"
        if task.context:
            task_context += f"Context data: {json.dumps(task.context, default=str, ensure_ascii=False)}\n"
        if task.field_id:
            task_context += f"Field ID: {task.field_id}\n"

        self._conversation.append(Message(role=MessageRole.USER, content=task_context))

        # 2-4. Conversation loop ------------------------------------------
        final_answer: str | None = None
        error_msg: str | None = None
        error_msg_ar: str | None = None

        try:
            while self._iteration_count < self.agent.max_iterations:
                self._iteration_count += 1
                log.debug("agent_runner.iteration", iteration=self._iteration_count)

                # Build prompt from conversation
                prompt_text = self._build_prompt()

                # Call LLM with per-iteration timeout
                try:
                    response_text = await asyncio.wait_for(
                        self.llm.prompt(prompt_text),
                        timeout=self.agent.iteration_timeout_s,
                    )
                except TimeoutError:
                    log.warning(
                        "agent_runner.iteration_timeout",
                        iteration=self._iteration_count,
                        timeout_s=self.agent.iteration_timeout_s,
                    )
                    error_msg = f"Iteration {self._iteration_count} timed out after {self.agent.iteration_timeout_s}s"
                    error_msg_ar = (
                        f"انتهت مهلة التكرار {self._iteration_count} بعد {self.agent.iteration_timeout_s} ثانية"
                    )
                    self._status = RunnerStatus.TIMEOUT
                    break

                self._conversation.append(
                    Message(
                        role=MessageRole.ASSISTANT,
                        content=response_text,
                    )
                )

                # Check for tool call
                tool_call = _parse_tool_call(response_text)
                if tool_call is None:
                    # No tool call -> treat as final answer
                    final_answer = response_text
                    self._status = RunnerStatus.COMPLETED
                    break

                # Dispatch tool
                tool_name, tool_args = tool_call
                self._status = RunnerStatus.WAITING_TOOL
                log.info("agent_runner.tool_call", tool=tool_name, iteration=self._iteration_count)

                try:
                    tool_result = await self.dispatch_tool(tool_name, tool_args)
                    tool_result_str = json.dumps(tool_result, default=str, ensure_ascii=False)
                except KeyError as exc:
                    tool_result_str = f"Error: {exc}"
                except Exception as exc:
                    tool_result_str = f"Tool execution failed: {type(exc).__name__}: {exc}"
                    log.warning("agent_runner.tool_error", tool=tool_name, error=str(exc))

                self._conversation.append(
                    Message(
                        role=MessageRole.TOOL,
                        content=tool_result_str,
                        name=tool_name,
                    )
                )
                self._status = RunnerStatus.RUNNING

            else:
                # max_iterations exhausted
                log.warning(
                    "agent_runner.max_iterations",
                    max_iterations=self.agent.max_iterations,
                )
                # Use last assistant message as partial answer
                last_assistant = [m for m in self._conversation if m.role == MessageRole.ASSISTANT]
                final_answer = last_assistant[-1].content if last_assistant else None
                error_msg = f"Reached max iterations ({self.agent.max_iterations})"
                error_msg_ar = f"تم الوصول إلى الحد الأقصى للتكرارات ({self.agent.max_iterations})"

        except Exception as exc:
            log.exception("agent_runner.error")
            self._status = RunnerStatus.FAILED
            error_msg = f"{type(exc).__name__}: {exc}"
            error_msg_ar = f"خطأ: {exc}"

        # 5. Build result and store in memory -----------------------------
        elapsed_ms = (time.monotonic() - start_mono) * 1000
        success = self._status == RunnerStatus.COMPLETED and final_answer is not None

        result = TaskResult(
            task_id=task.task_id,
            agent_id=self.agent.agent_id,
            status=TaskStatus.COMPLETED if success else TaskStatus.FAILED,
            success=success,
            result=final_answer,
            error=error_msg,
            error_ar=error_msg_ar,
            execution_time_ms=round(elapsed_ms, 1),
            started_at=started_at,
            completed_at=datetime.now(UTC),
            metadata={
                "iterations": self._iteration_count,
                "provider": self.llm.get_provider_name(),
            },
        )

        # Persist to shared memory
        self.memory.set(
            f"result:{task.task_id}",
            result.model_dump(mode="json"),
            agent_id=self.agent.agent_id,
        )

        log.info(
            "agent_runner.done",
            success=success,
            iterations=self._iteration_count,
            elapsed_ms=round(elapsed_ms, 1),
        )
        return result

    async def prompt(self, message: str) -> str:
        """
        Perform a single LLM call outside the task loop.

        تنفيذ استدعاء LLM واحد خارج حلقة المهام.

        Args:
            message: The user message.

        Returns:
            Generated text.
        """
        return await self.llm.prompt(message)

    async def stream(self, message: str) -> AsyncIterator[str]:
        """
        Stream a single LLM response.

        تدفق استجابة LLM واحدة.

        Args:
            message: The user message.

        Yields:
            Text chunks.
        """
        async for chunk in self.llm.stream(message):
            yield chunk

    async def dispatch_tool(self, tool_name: str, args: dict[str, Any]) -> Any:
        """
        Execute a tool via the dispatcher.

        تنفيذ أداة عبر المرسل.

        Args:
            tool_name: Registered tool name.
            args: Arguments to pass.

        Returns:
            Tool result value.
        """
        return await self.tools.dispatch(tool_name, args)

    # -- internal helpers --------------------------------------------------

    def _build_prompt(self) -> str:
        """
        Serialise the conversation history into a single prompt string.

        تسلسل سجل المحادثة إلى سلسلة نصية واحدة.
        """
        parts: list[str] = []
        for msg in self._conversation:
            prefix = msg.role.value.upper()
            if msg.name:
                prefix = f"TOOL[{msg.name}]"
            parts.append(f"[{prefix}]\n{msg.content}")
        return "\n\n".join(parts)
