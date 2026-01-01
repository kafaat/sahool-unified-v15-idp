"""
A2A Protocol Implementation
تطبيق بروتوكول A2A

Core protocol message types, state management, and conversation handling.
أنواع رسائل البروتوكول الأساسية وإدارة الحالة ومعالجة المحادثات.
"""

from enum import Enum
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class TaskState(str, Enum):
    """
    Task execution states
    حالات تنفيذ المهام
    """

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageType(str, Enum):
    """
    A2A message types
    أنواع رسائل A2A
    """

    TASK = "task"
    TASK_RESULT = "task_result"
    ERROR = "error"
    HEARTBEAT = "heartbeat"
    CANCEL = "cancel"


class A2AMessage(BaseModel):
    """
    Base A2A message structure
    بنية رسالة A2A الأساسية

    Following Linux Foundation A2A specification.
    وفقاً لمواصفات Linux Foundation A2A.
    """

    message_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    message_type: MessageType
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    sender_agent_id: str
    receiver_agent_id: Optional[str] = None
    conversation_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }


class TaskMessage(A2AMessage):
    """
    Task request message
    رسالة طلب المهمة

    Sent from one agent to another to request task execution.
    ترسل من وكيل إلى آخر لطلب تنفيذ مهمة.
    """

    message_type: MessageType = MessageType.TASK
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_type: str = Field(..., description="Type of task to execute")
    task_description: str = Field(..., description="Human-readable task description")
    parameters: Dict[str, Any] = Field(default_factory=dict)
    priority: int = Field(default=5, ge=1, le=10, description="Task priority 1-10")
    timeout_seconds: Optional[int] = Field(default=300, description="Task timeout")
    require_streaming: bool = Field(
        default=False, description="Request streaming response"
    )
    context: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional context"
    )


class TaskResultMessage(A2AMessage):
    """
    Task result message
    رسالة نتيجة المهمة

    Sent by the executing agent back to the requesting agent.
    ترسل من الوكيل المنفذ إلى الوكيل الطالب.
    """

    message_type: MessageType = MessageType.TASK_RESULT
    task_id: str
    state: TaskState
    result: Optional[Dict[str, Any]] = None
    progress: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Task progress 0-1"
    )
    is_final: bool = Field(default=True, description="Is this the final result?")
    partial_result: Optional[Dict[str, Any]] = Field(
        default=None, description="Partial result for streaming"
    )
    execution_time_ms: Optional[int] = Field(
        default=None, description="Execution time in milliseconds"
    )


class ErrorMessage(A2AMessage):
    """
    Error message
    رسالة خطأ

    Sent when an error occurs during task processing.
    ترسل عند حدوث خطأ أثناء معالجة المهمة.
    """

    message_type: MessageType = MessageType.ERROR
    task_id: Optional[str] = None
    error_code: str
    error_message: str
    error_details: Optional[Dict[str, Any]] = None
    recoverable: bool = Field(default=False, description="Can the task be retried?")


class HeartbeatMessage(A2AMessage):
    """
    Heartbeat message for connection monitoring
    رسالة نبض لمراقبة الاتصال
    """

    message_type: MessageType = MessageType.HEARTBEAT
    agent_status: str = Field(default="active")
    load: Optional[float] = Field(
        default=None, ge=0.0, le=1.0, description="Agent load 0-1"
    )


class CancelMessage(A2AMessage):
    """
    Task cancellation request
    طلب إلغاء المهمة
    """

    message_type: MessageType = MessageType.CANCEL
    task_id: str
    reason: Optional[str] = None


class ConversationContext:
    """
    Manages conversation state between agents
    يدير حالة المحادثة بين الوكلاء
    """

    def __init__(self, conversation_id: Optional[str] = None):
        """
        Initialize conversation context
        تهيئة سياق المحادثة

        Args:
            conversation_id: Optional conversation ID, auto-generated if not provided
        """
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.messages: List[A2AMessage] = []
        self.tasks: Dict[str, TaskState] = {}
        self.metadata: Dict[str, Any] = {}
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def add_message(self, message: A2AMessage) -> None:
        """
        Add message to conversation history
        إضافة رسالة إلى سجل المحادثة

        Args:
            message: A2A message to add
        """
        self.messages.append(message)
        self.updated_at = datetime.utcnow()

        # Update task state if this is a task-related message
        # تحديث حالة المهمة إذا كانت هذه رسالة متعلقة بالمهمة
        if isinstance(message, TaskMessage):
            self.tasks[message.task_id] = TaskState.PENDING
        elif isinstance(message, TaskResultMessage):
            self.tasks[message.task_id] = message.state

    def get_task_state(self, task_id: str) -> Optional[TaskState]:
        """
        Get current state of a task
        الحصول على الحالة الحالية للمهمة

        Args:
            task_id: Task identifier

        Returns:
            Task state or None if not found
        """
        return self.tasks.get(task_id)

    def get_messages_by_type(self, message_type: MessageType) -> List[A2AMessage]:
        """
        Filter messages by type
        تصفية الرسائل حسب النوع

        Args:
            message_type: Type of messages to retrieve

        Returns:
            List of messages of the specified type
        """
        return [msg for msg in self.messages if msg.message_type == message_type]

    def get_messages_by_task(self, task_id: str) -> List[A2AMessage]:
        """
        Get all messages related to a specific task
        الحصول على جميع الرسائل المتعلقة بمهمة معينة

        Args:
            task_id: Task identifier

        Returns:
            List of task-related messages
        """
        return [
            msg
            for msg in self.messages
            if isinstance(msg, (TaskMessage, TaskResultMessage, ErrorMessage))
            and getattr(msg, "task_id", None) == task_id
        ]

    def get_summary(self) -> Dict[str, Any]:
        """
        Get conversation summary
        الحصول على ملخص المحادثة

        Returns:
            Summary dictionary with statistics
        """
        return {
            "conversation_id": self.conversation_id,
            "total_messages": len(self.messages),
            "tasks": {
                "total": len(self.tasks),
                "pending": sum(
                    1 for s in self.tasks.values() if s == TaskState.PENDING
                ),
                "in_progress": sum(
                    1 for s in self.tasks.values() if s == TaskState.IN_PROGRESS
                ),
                "completed": sum(
                    1 for s in self.tasks.values() if s == TaskState.COMPLETED
                ),
                "failed": sum(1 for s in self.tasks.values() if s == TaskState.FAILED),
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "duration_seconds": (self.updated_at - self.created_at).total_seconds(),
        }

    def clear_completed_tasks(self) -> int:
        """
        Remove completed tasks from tracking
        إزالة المهام المكتملة من التتبع

        Returns:
            Number of tasks cleared
        """
        completed_tasks = [
            task_id
            for task_id, state in self.tasks.items()
            if state == TaskState.COMPLETED
        ]
        for task_id in completed_tasks:
            del self.tasks[task_id]
        return len(completed_tasks)


class TaskQueue:
    """
    Priority queue for managing tasks
    قائمة انتظار ذات أولوية لإدارة المهام
    """

    def __init__(self):
        """Initialize task queue | تهيئة قائمة انتظار المهام"""
        self.tasks: Dict[str, TaskMessage] = {}
        self.states: Dict[str, TaskState] = {}

    def add_task(self, task: TaskMessage) -> None:
        """
        Add task to queue
        إضافة مهمة إلى القائمة

        Args:
            task: Task message to add
        """
        self.tasks[task.task_id] = task
        self.states[task.task_id] = TaskState.PENDING

    def get_task(self, task_id: str) -> Optional[TaskMessage]:
        """
        Retrieve task by ID
        استرجاع المهمة بواسطة المعرف

        Args:
            task_id: Task identifier

        Returns:
            Task message or None
        """
        return self.tasks.get(task_id)

    def update_state(self, task_id: str, state: TaskState) -> None:
        """
        Update task state
        تحديث حالة المهمة

        Args:
            task_id: Task identifier
            state: New task state
        """
        if task_id in self.states:
            self.states[task_id] = state

    def get_pending_tasks(self) -> List[TaskMessage]:
        """
        Get all pending tasks sorted by priority
        الحصول على جميع المهام المعلقة مرتبة حسب الأولوية

        Returns:
            List of pending tasks
        """
        pending = [
            task
            for task_id, task in self.tasks.items()
            if self.states[task_id] == TaskState.PENDING
        ]
        return sorted(pending, key=lambda t: t.priority, reverse=True)

    def remove_task(self, task_id: str) -> bool:
        """
        Remove task from queue
        إزالة المهمة من القائمة

        Args:
            task_id: Task identifier

        Returns:
            True if task was removed, False if not found
        """
        if task_id in self.tasks:
            del self.tasks[task_id]
            del self.states[task_id]
            return True
        return False

    def get_stats(self) -> Dict[str, int]:
        """
        Get queue statistics
        الحصول على إحصائيات القائمة

        Returns:
            Dictionary with task counts by state
        """
        return {
            "total": len(self.tasks),
            "pending": sum(1 for s in self.states.values() if s == TaskState.PENDING),
            "in_progress": sum(
                1 for s in self.states.values() if s == TaskState.IN_PROGRESS
            ),
            "completed": sum(
                1 for s in self.states.values() if s == TaskState.COMPLETED
            ),
            "failed": sum(1 for s in self.states.values() if s == TaskState.FAILED),
        }
