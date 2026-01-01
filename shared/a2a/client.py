"""
A2A Client Implementation
تطبيق عميل A2A

Client for discovering agents and sending tasks.
عميل لاكتشاف الوكلاء وإرسال المهام.
"""

from typing import Dict, Any, List, Optional, AsyncIterator
import httpx
import structlog
from datetime import datetime
import asyncio

from .protocol import (
    TaskMessage,
    TaskResultMessage,
    ErrorMessage,
    TaskState,
    MessageType,
)
from .agent import AgentCard

logger = structlog.get_logger()


class AgentDiscovery:
    """
    Agent discovery service
    خدمة اكتشاف الوكلاء

    Discovers available agents via their .well-known/agent-card.json endpoint.
    يكتشف الوكلاء المتاحة عبر نقطة النهاية .well-known/agent-card.json.
    """

    def __init__(self, timeout: int = 30):
        """
        Initialize agent discovery
        تهيئة اكتشاف الوكلاء

        Args:
            timeout: HTTP request timeout in seconds
        """
        self.timeout = timeout
        self.discovered_agents: Dict[str, AgentCard] = {}

    async def discover_agent(self, base_url: str) -> Optional[AgentCard]:
        """
        Discover agent at given URL
        اكتشاف الوكيل على عنوان URL المحدد

        Args:
            base_url: Base URL of the agent service

        Returns:
            Agent card or None if discovery failed
        """
        try:
            # Try standard A2A well-known endpoint
            # محاولة نقطة النهاية القياسية well-known لـ A2A
            well_known_url = f"{base_url.rstrip('/')}/.well-known/agent-card.json"

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(well_known_url)
                response.raise_for_status()

                agent_data = response.json()
                agent_card = AgentCard(**agent_data)

                # Cache discovered agent
                # تخزين الوكيل المكتشف مؤقتاً
                self.discovered_agents[agent_card.agent_id] = agent_card

                logger.info(
                    "agent_discovered",
                    agent_id=agent_card.agent_id,
                    name=agent_card.name,
                    base_url=base_url,
                )

                return agent_card

        except httpx.HTTPStatusError as e:
            logger.error(
                "agent_discovery_http_error",
                base_url=base_url,
                status_code=e.response.status_code,
                error=str(e),
            )
            return None

        except Exception as e:
            logger.error("agent_discovery_failed", base_url=base_url, error=str(e))
            return None

    async def discover_multiple(self, base_urls: List[str]) -> List[AgentCard]:
        """
        Discover multiple agents concurrently
        اكتشاف وكلاء متعددة بشكل متزامن

        Args:
            base_urls: List of agent base URLs

        Returns:
            List of successfully discovered agent cards
        """
        tasks = [self.discover_agent(url) for url in base_urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter out None and exceptions
        # تصفية None والاستثناءات
        agent_cards = [result for result in results if isinstance(result, AgentCard)]

        logger.info(
            "multiple_agents_discovered",
            total_attempted=len(base_urls),
            successful=len(agent_cards),
        )

        return agent_cards

    def get_agent_by_id(self, agent_id: str) -> Optional[AgentCard]:
        """
        Get cached agent card by ID
        الحصول على بطاقة الوكيل المخزنة مؤقتاً بواسطة المعرف

        Args:
            agent_id: Agent identifier

        Returns:
            Agent card or None
        """
        return self.discovered_agents.get(agent_id)

    def get_agents_by_capability(self, capability_id: str) -> List[AgentCard]:
        """
        Find agents with specific capability
        البحث عن الوكلاء بقدرة محددة

        Args:
            capability_id: Capability identifier

        Returns:
            List of matching agent cards
        """
        matching_agents = []

        for agent_card in self.discovered_agents.values():
            for capability in agent_card.capabilities:
                if capability.capability_id == capability_id:
                    matching_agents.append(agent_card)
                    break

        return matching_agents

    def search_agents(
        self,
        name_pattern: Optional[str] = None,
        tags: Optional[List[str]] = None,
        provider: Optional[str] = None,
    ) -> List[AgentCard]:
        """
        Search for agents by various criteria
        البحث عن الوكلاء بمعايير متنوعة

        Args:
            name_pattern: Pattern to match agent name
            tags: Tags to match in capabilities
            provider: Provider organization name

        Returns:
            List of matching agent cards
        """
        results = []

        for agent_card in self.discovered_agents.values():
            # Check name pattern
            # التحقق من نمط الاسم
            if name_pattern and name_pattern.lower() not in agent_card.name.lower():
                continue

            # Check provider
            # التحقق من المزود
            if provider and provider.lower() != agent_card.provider.lower():
                continue

            # Check tags
            # التحقق من العلامات
            if tags:
                agent_tags = set()
                for capability in agent_card.capabilities:
                    agent_tags.update(capability.tags)

                if not any(tag in agent_tags for tag in tags):
                    continue

            results.append(agent_card)

        return results


class A2AClient:
    """
    A2A Client for sending tasks to agents
    عميل A2A لإرسال المهام إلى الوكلاء

    Handles task submission, result retrieval, and streaming.
    يتعامل مع إرسال المهام واسترجاع النتائج والبث.
    """

    def __init__(self, sender_agent_id: str, timeout: int = 300, max_retries: int = 3):
        """
        Initialize A2A client
        تهيئة عميل A2A

        Args:
            sender_agent_id: ID of the sending agent
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries for failed requests
        """
        self.sender_agent_id = sender_agent_id
        self.timeout = timeout
        self.max_retries = max_retries
        self.discovery = AgentDiscovery(timeout=timeout)

        logger.info("a2a_client_initialized", sender_agent_id=sender_agent_id)

    async def send_task(
        self,
        agent_card: AgentCard,
        task_type: str,
        task_description: str,
        parameters: Dict[str, Any],
        priority: int = 5,
        timeout_seconds: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
    ) -> TaskResultMessage:
        """
        Send task to agent and wait for result
        إرسال مهمة إلى الوكيل وانتظار النتيجة

        Args:
            agent_card: Target agent card
            task_type: Type of task
            task_description: Human-readable description
            parameters: Task parameters
            priority: Task priority (1-10)
            timeout_seconds: Task timeout
            context: Additional context
            conversation_id: Optional conversation ID

        Returns:
            Task result message
        """
        # Create task message
        # إنشاء رسالة المهمة
        task = TaskMessage(
            sender_agent_id=self.sender_agent_id,
            receiver_agent_id=agent_card.agent_id,
            conversation_id=conversation_id,
            task_type=task_type,
            task_description=task_description,
            parameters=parameters,
            priority=priority,
            timeout_seconds=timeout_seconds or self.timeout,
            context=context,
        )

        # Send task via HTTP
        # إرسال المهمة عبر HTTP
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    str(agent_card.task_endpoint),
                    json=task.dict(),
                    headers={
                        "Content-Type": "application/json",
                        "X-A2A-Protocol-Version": "1.0",
                    },
                )
                response.raise_for_status()

                result_data = response.json()
                result = TaskResultMessage(**result_data)

                logger.info(
                    "task_sent_successfully",
                    task_id=task.task_id,
                    receiver_agent_id=agent_card.agent_id,
                    state=result.state,
                )

                return result

        except httpx.HTTPStatusError as e:
            logger.error(
                "task_send_http_error",
                task_id=task.task_id,
                status_code=e.response.status_code,
                error=str(e),
            )

            # Create error result
            # إنشاء نتيجة خطأ
            return TaskResultMessage(
                sender_agent_id=agent_card.agent_id,
                receiver_agent_id=self.sender_agent_id,
                conversation_id=conversation_id,
                task_id=task.task_id,
                state=TaskState.FAILED,
                result={"error": f"HTTP {e.response.status_code}: {str(e)}"},
                is_final=True,
            )

        except Exception as e:
            logger.error("task_send_failed", task_id=task.task_id, error=str(e))

            return TaskResultMessage(
                sender_agent_id=agent_card.agent_id,
                receiver_agent_id=self.sender_agent_id,
                conversation_id=conversation_id,
                task_id=task.task_id,
                state=TaskState.FAILED,
                result={"error": str(e)},
                is_final=True,
            )

    async def stream_task(
        self,
        agent_card: AgentCard,
        task_type: str,
        task_description: str,
        parameters: Dict[str, Any],
        priority: int = 5,
        context: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
    ) -> AsyncIterator[TaskResultMessage]:
        """
        Send task with streaming results via WebSocket
        إرسال مهمة مع نتائج متدفقة عبر WebSocket

        Args:
            agent_card: Target agent card
            task_type: Type of task
            task_description: Human-readable description
            parameters: Task parameters
            priority: Task priority (1-10)
            context: Additional context
            conversation_id: Optional conversation ID

        Yields:
            Task result messages as they arrive
        """
        if not agent_card.websocket_endpoint:
            raise ValueError(f"Agent {agent_card.agent_id} does not support streaming")

        # Create task message
        # إنشاء رسالة المهمة
        task = TaskMessage(
            sender_agent_id=self.sender_agent_id,
            receiver_agent_id=agent_card.agent_id,
            conversation_id=conversation_id,
            task_type=task_type,
            task_description=task_description,
            parameters=parameters,
            priority=priority,
            require_streaming=True,
            context=context,
        )

        try:
            # Connect to WebSocket
            # الاتصال بـ WebSocket
            import websockets

            ws_url = str(agent_card.websocket_endpoint)

            async with websockets.connect(ws_url) as websocket:
                # Send task
                # إرسال المهمة
                await websocket.send(task.json())

                logger.info(
                    "streaming_task_sent",
                    task_id=task.task_id,
                    receiver_agent_id=agent_card.agent_id,
                )

                # Receive results
                # استقبال النتائج
                while True:
                    message_data = await websocket.recv()

                    # Parse message
                    # تحليل الرسالة
                    import json

                    message_dict = json.loads(message_data)

                    if (
                        message_dict.get("message_type")
                        == MessageType.TASK_RESULT.value
                    ):
                        result = TaskResultMessage(**message_dict)
                        yield result

                        # Stop if final result
                        # التوقف إذا كانت النتيجة النهائية
                        if result.is_final:
                            break

                    elif message_dict.get("message_type") == MessageType.ERROR.value:
                        error = ErrorMessage(**message_dict)
                        logger.error(
                            "streaming_task_error",
                            task_id=task.task_id,
                            error_code=error.error_code,
                            error_message=error.error_message,
                        )

                        # Yield error as failed result
                        # إرجاع الخطأ كنتيجة فاشلة
                        yield TaskResultMessage(
                            sender_agent_id=agent_card.agent_id,
                            receiver_agent_id=self.sender_agent_id,
                            conversation_id=conversation_id,
                            task_id=task.task_id,
                            state=TaskState.FAILED,
                            result={"error": error.error_message},
                            is_final=True,
                        )
                        break

        except Exception as e:
            logger.error("streaming_task_failed", task_id=task.task_id, error=str(e))

            yield TaskResultMessage(
                sender_agent_id=agent_card.agent_id,
                receiver_agent_id=self.sender_agent_id,
                conversation_id=conversation_id,
                task_id=task.task_id,
                state=TaskState.FAILED,
                result={"error": str(e)},
                is_final=True,
            )

    async def batch_send_tasks(
        self,
        tasks: List[Dict[str, Any]],
        agent_card: AgentCard,
        conversation_id: Optional[str] = None,
    ) -> List[TaskResultMessage]:
        """
        Send multiple tasks to the same agent concurrently
        إرسال مهام متعددة إلى نفس الوكيل بشكل متزامن

        Args:
            tasks: List of task specifications
            agent_card: Target agent card
            conversation_id: Optional shared conversation ID

        Returns:
            List of task result messages
        """
        # Create task coroutines
        # إنشاء coroutines للمهام
        task_coroutines = [
            self.send_task(
                agent_card=agent_card,
                task_type=task_spec["task_type"],
                task_description=task_spec["task_description"],
                parameters=task_spec["parameters"],
                priority=task_spec.get("priority", 5),
                context=task_spec.get("context"),
                conversation_id=conversation_id,
            )
            for task_spec in tasks
        ]

        # Execute concurrently
        # التنفيذ بشكل متزامن
        results = await asyncio.gather(*task_coroutines, return_exceptions=True)

        # Filter out exceptions
        # تصفية الاستثناءات
        successful_results = [
            result for result in results if isinstance(result, TaskResultMessage)
        ]

        logger.info(
            "batch_tasks_completed",
            total_tasks=len(tasks),
            successful=len(successful_results),
        )

        return successful_results

    async def poll_task_status(
        self,
        agent_card: AgentCard,
        task_id: str,
        poll_interval: int = 5,
        max_attempts: int = 60,
    ) -> TaskResultMessage:
        """
        Poll for task status until completion
        الاستفسار عن حالة المهمة حتى الاكتمال

        Args:
            agent_card: Target agent card
            task_id: Task identifier
            poll_interval: Seconds between polls
            max_attempts: Maximum polling attempts

        Returns:
            Final task result message
        """
        for attempt in range(max_attempts):
            try:
                # Query task status endpoint
                # الاستعلام عن نقطة نهاية حالة المهمة
                status_url = f"{agent_card.task_endpoint}/status/{task_id}"

                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(status_url)
                    response.raise_for_status()

                    result_data = response.json()
                    result = TaskResultMessage(**result_data)

                    # Check if final
                    # التحقق من النهائية
                    if result.is_final:
                        return result

                    # Wait before next poll
                    # الانتظار قبل الاستفسار التالي
                    await asyncio.sleep(poll_interval)

            except Exception as e:
                logger.error(
                    "task_status_poll_failed",
                    task_id=task_id,
                    attempt=attempt,
                    error=str(e),
                )

                if attempt == max_attempts - 1:
                    # Return timeout error
                    # إرجاع خطأ انتهاء الوقت
                    return TaskResultMessage(
                        sender_agent_id=agent_card.agent_id,
                        receiver_agent_id=self.sender_agent_id,
                        task_id=task_id,
                        state=TaskState.FAILED,
                        result={"error": "Polling timeout"},
                        is_final=True,
                    )

                await asyncio.sleep(poll_interval)

        # Max attempts reached
        # تم الوصول إلى الحد الأقصى من المحاولات
        return TaskResultMessage(
            sender_agent_id=agent_card.agent_id,
            receiver_agent_id=self.sender_agent_id,
            task_id=task_id,
            state=TaskState.FAILED,
            result={"error": "Max polling attempts reached"},
            is_final=True,
        )
