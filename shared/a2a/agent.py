"""
A2A Agent Base Class
فئة الوكيل الأساسية لـ A2A

Base agent implementation with agent card generation and task handling.
تطبيق الوكيل الأساسي مع توليد بطاقة الوكيل ومعالجة المهام.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Callable, Awaitable
from datetime import datetime
from pydantic import BaseModel, Field, HttpUrl
import structlog

from .protocol import (
    TaskMessage,
    TaskResultMessage,
    ErrorMessage,
    TaskState,
    ConversationContext,
    TaskQueue,
)

logger = structlog.get_logger()


class AgentCapability(BaseModel):
    """
    Agent capability definition
    تعريف قدرة الوكيل
    """

    capability_id: str = Field(..., description="Unique capability identifier")
    name: str = Field(..., description="Capability name")
    description: str = Field(..., description="Capability description")
    input_schema: Dict[str, Any] = Field(..., description="JSON Schema for inputs")
    output_schema: Dict[str, Any] = Field(..., description="JSON Schema for outputs")
    examples: List[Dict[str, Any]] = Field(
        default_factory=list, description="Usage examples"
    )
    tags: List[str] = Field(default_factory=list, description="Capability tags")


class AgentCard(BaseModel):
    """
    Agent Card (A2A Discovery Document)
    بطاقة الوكيل (وثيقة اكتشاف A2A)

    Following Linux Foundation A2A specification for agent discovery.
    وفقاً لمواصفات Linux Foundation A2A لاكتشاف الوكلاء.
    """

    agent_id: str = Field(..., description="Unique agent identifier")
    name: str = Field(..., description="Agent name")
    version: str = Field(..., description="Agent version")
    description: str = Field(..., description="Agent description")

    # Agent metadata
    # بيانات تعريف الوكيل
    provider: str = Field(..., description="Agent provider/organization")
    contact_email: Optional[str] = None
    homepage: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = None

    # Capabilities
    # القدرات
    capabilities: List[AgentCapability] = Field(..., description="Agent capabilities")

    # Endpoints
    # نقاط النهاية
    task_endpoint: HttpUrl = Field(..., description="Task submission endpoint")
    websocket_endpoint: Optional[HttpUrl] = Field(
        None, description="WebSocket endpoint for streaming"
    )

    # Protocol support
    # دعم البروتوكول
    protocol_version: str = Field(default="1.0", description="A2A protocol version")
    supports_streaming: bool = Field(
        default=False, description="Supports streaming responses"
    )
    supports_batch: bool = Field(default=False, description="Supports batch requests")

    # Rate limits
    # حدود المعدل
    rate_limit: Optional[Dict[str, Any]] = Field(
        None, description="Rate limit information (requests_per_minute, etc.)"
    )

    # Authentication
    # المصادقة
    authentication_required: bool = Field(
        default=False, description="Requires authentication"
    )
    authentication_methods: List[str] = Field(
        default_factory=list,
        description="Supported auth methods (api_key, oauth2, etc.)",
    )

    # Status
    # الحالة
    status: str = Field(
        default="active", description="Agent status (active, maintenance, deprecated)"
    )
    last_updated: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }

    def to_well_known_format(self) -> Dict[str, Any]:
        """
        Convert to .well-known/agent-card.json format
        تحويل إلى تنسيق .well-known/agent-card.json

        Returns:
            Agent card as dictionary
        """
        return self.dict(exclude_none=True)


class A2AAgent(ABC):
    """
    Base A2A Agent Class
    فئة الوكيل الأساسية لـ A2A

    Provides core A2A protocol functionality:
    - Agent card generation
    - Task handling and routing
    - Response formatting
    - Conversation management

    يوفر وظائف بروتوكول A2A الأساسية:
    - توليد بطاقة الوكيل
    - معالجة المهام وتوجيهها
    - تنسيق الاستجابة
    - إدارة المحادثات
    """

    def __init__(
        self,
        agent_id: str,
        name: str,
        version: str,
        description: str,
        provider: str,
        task_endpoint: str,
        websocket_endpoint: Optional[str] = None,
    ):
        """
        Initialize A2A agent
        تهيئة وكيل A2A

        Args:
            agent_id: Unique agent identifier
            name: Agent name
            version: Agent version
            description: Agent description
            provider: Provider organization
            task_endpoint: HTTP endpoint for tasks
            websocket_endpoint: Optional WebSocket endpoint
        """
        self.agent_id = agent_id
        self.name = name
        self.version = version
        self.description = description
        self.provider = provider
        self.task_endpoint = task_endpoint
        self.websocket_endpoint = websocket_endpoint

        # Task management
        # إدارة المهام
        self.task_queue = TaskQueue()
        self.task_handlers: Dict[str, Callable] = {}
        self.conversations: Dict[str, ConversationContext] = {}

        # Statistics
        # الإحصائيات
        self.stats = {
            "tasks_received": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "total_execution_time_ms": 0,
        }

        logger.info(
            "a2a_agent_initialized",
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
        )

    @abstractmethod
    def get_capabilities(self) -> List[AgentCapability]:
        """
        Get agent capabilities
        الحصول على قدرات الوكيل

        Returns:
            List of agent capabilities
        """
        pass

    def get_agent_card(self) -> AgentCard:
        """
        Generate agent card for A2A discovery
        توليد بطاقة الوكيل لاكتشاف A2A

        Returns:
            Agent card with full metadata
        """
        return AgentCard(
            agent_id=self.agent_id,
            name=self.name,
            version=self.version,
            description=self.description,
            provider=self.provider,
            capabilities=self.get_capabilities(),
            task_endpoint=self.task_endpoint,
            websocket_endpoint=self.websocket_endpoint,
            supports_streaming=self.websocket_endpoint is not None,
            supports_batch=False,
            protocol_version="1.0",
            status="active",
            last_updated=datetime.utcnow(),
        )

    def register_task_handler(
        self,
        task_type: str,
        handler: Callable[[TaskMessage], Awaitable[Dict[str, Any]]],
    ) -> None:
        """
        Register handler for a specific task type
        تسجيل معالج لنوع مهمة محدد

        Args:
            task_type: Type of task to handle
            handler: Async function to handle the task
        """
        self.task_handlers[task_type] = handler
        logger.debug(
            "task_handler_registered", agent_id=self.agent_id, task_type=task_type
        )

    async def handle_task(self, task: TaskMessage) -> TaskResultMessage:
        """
        Handle incoming task
        معالجة المهمة الواردة

        Args:
            task: Task message to process

        Returns:
            Task result message
        """
        start_time = datetime.utcnow()
        self.stats["tasks_received"] += 1

        # Add to queue
        # إضافة إلى القائمة
        self.task_queue.add_task(task)
        self.task_queue.update_state(task.task_id, TaskState.IN_PROGRESS)

        # Get or create conversation context
        # الحصول على سياق المحادثة أو إنشائه
        conversation_id = task.conversation_id or task.task_id
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationContext(conversation_id)

        conversation = self.conversations[conversation_id]
        conversation.add_message(task)

        try:
            # Find and execute handler
            # البحث عن المعالج وتنفيذه
            handler = self.task_handlers.get(task.task_type)

            if not handler:
                raise ValueError(
                    f"No handler registered for task type: {task.task_type}"
                )

            # Execute task
            # تنفيذ المهمة
            result = await handler(task)

            # Calculate execution time
            # حساب وقت التنفيذ
            execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.stats["total_execution_time_ms"] += execution_time
            self.stats["tasks_completed"] += 1

            # Update state
            # تحديث الحالة
            self.task_queue.update_state(task.task_id, TaskState.COMPLETED)

            # Create result message
            # إنشاء رسالة النتيجة
            result_message = TaskResultMessage(
                sender_agent_id=self.agent_id,
                receiver_agent_id=task.sender_agent_id,
                conversation_id=conversation_id,
                task_id=task.task_id,
                state=TaskState.COMPLETED,
                result=result,
                is_final=True,
                execution_time_ms=int(execution_time),
            )

            conversation.add_message(result_message)

            logger.info(
                "task_completed",
                agent_id=self.agent_id,
                task_id=task.task_id,
                task_type=task.task_type,
                execution_time_ms=int(execution_time),
            )

            return result_message

        except Exception as e:
            # Handle error
            # معالجة الخطأ
            self.stats["tasks_failed"] += 1
            self.task_queue.update_state(task.task_id, TaskState.FAILED)

            logger.error(
                "task_failed",
                agent_id=self.agent_id,
                task_id=task.task_id,
                task_type=task.task_type,
                error=str(e),
            )

            # Create error message
            # إنشاء رسالة الخطأ
            error_message = ErrorMessage(
                sender_agent_id=self.agent_id,
                receiver_agent_id=task.sender_agent_id,
                conversation_id=conversation_id,
                task_id=task.task_id,
                error_code="TASK_EXECUTION_FAILED",
                error_message=str(e),
                error_details={"task_type": task.task_type},
                recoverable=False,
            )

            conversation.add_message(error_message)

            # Return as failed task result
            # الإرجاع كنتيجة مهمة فاشلة
            return TaskResultMessage(
                sender_agent_id=self.agent_id,
                receiver_agent_id=task.sender_agent_id,
                conversation_id=conversation_id,
                task_id=task.task_id,
                state=TaskState.FAILED,
                result={"error": str(e)},
                is_final=True,
            )

    async def stream_task_progress(
        self,
        task: TaskMessage,
        progress_callback: Callable[[float, Optional[Dict[str, Any]]], Awaitable[None]],
    ) -> TaskResultMessage:
        """
        Handle task with streaming progress updates
        معالجة المهمة مع تحديثات التقدم المتدفقة

        Args:
            task: Task message to process
            progress_callback: Async callback for progress updates

        Returns:
            Final task result message
        """
        # Similar to handle_task but with progress updates
        # مشابه لـ handle_task لكن مع تحديثات التقدم

        # This is a simplified version - implementations should call
        # progress_callback with updates during execution
        # هذه نسخة مبسطة - يجب أن تستدعي التطبيقات
        # progress_callback مع التحديثات أثناء التنفيذ

        return await self.handle_task(task)

    def get_conversation(self, conversation_id: str) -> Optional[ConversationContext]:
        """
        Get conversation context
        الحصول على سياق المحادثة

        Args:
            conversation_id: Conversation identifier

        Returns:
            Conversation context or None
        """
        return self.conversations.get(conversation_id)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics
        الحصول على إحصائيات الوكيل

        Returns:
            Statistics dictionary
        """
        queue_stats = self.task_queue.get_stats()
        avg_execution_time = (
            self.stats["total_execution_time_ms"] / self.stats["tasks_completed"]
            if self.stats["tasks_completed"] > 0
            else 0
        )

        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "version": self.version,
            "tasks_received": self.stats["tasks_received"],
            "tasks_completed": self.stats["tasks_completed"],
            "tasks_failed": self.stats["tasks_failed"],
            "success_rate": (
                self.stats["tasks_completed"] / self.stats["tasks_received"]
                if self.stats["tasks_received"] > 0
                else 0.0
            ),
            "average_execution_time_ms": avg_execution_time,
            "queue_stats": queue_stats,
            "active_conversations": len(self.conversations),
        }

    def cleanup_old_conversations(self, max_age_hours: int = 24) -> int:
        """
        Remove old conversation contexts
        إزالة سياقات المحادثات القديمة

        Args:
            max_age_hours: Maximum age in hours

        Returns:
            Number of conversations removed
        """
        now = datetime.utcnow()
        removed = 0

        conversation_ids = list(self.conversations.keys())
        for conv_id in conversation_ids:
            conv = self.conversations[conv_id]
            age_hours = (now - conv.created_at).total_seconds() / 3600

            if age_hours > max_age_hours:
                del self.conversations[conv_id]
                removed += 1

        if removed > 0:
            logger.info(
                "conversations_cleaned", agent_id=self.agent_id, removed=removed
            )

        return removed
