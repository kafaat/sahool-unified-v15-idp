"""
NATS Bridge for Multi-Agent Communication
جسر NATS للتواصل بين الوكلاء المتعددين

This module provides the communication infrastructure for agents to interact
with each other using NATS messaging system.

توفر هذه الوحدة البنية التحتية للاتصال للوكلاء للتفاعل
مع بعضهم البعض باستخدام نظام الرسائل NATS.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
from enum import Enum

import nats
from nats.aio.client import Client as NATSClient
from nats.aio.msg import Msg
from nats.errors import TimeoutError as NATSTimeoutError
import structlog

logger = structlog.get_logger()


class MessagePriority(Enum):
    """
    Message priority levels
    مستويات أولوية الرسائل
    """
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class MessageType(Enum):
    """
    Types of messages in the multi-agent system
    أنواع الرسائل في نظام الوكلاء المتعددين
    """
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    COUNCIL = "council"
    NOTIFICATION = "notification"
    HEARTBEAT = "heartbeat"


class AgentMessage:
    """
    Structured message format for agent communication
    تنسيق رسالة منظمة لتواصل الوكلاء
    """

    def __init__(
        self,
        message_type: MessageType,
        sender_id: str,
        content: Dict[str, Any],
        recipient_id: Optional[str] = None,
        council_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an agent message
        تهيئة رسالة وكيل

        Args:
            message_type: Type of message | نوع الرسالة
            sender_id: ID of sending agent | معرف الوكيل المرسل
            content: Message content | محتوى الرسالة
            recipient_id: ID of recipient agent | معرف الوكيل المستقبل
            council_id: Council ID for group messages | معرف المجلس لرسائل المجموعة
            correlation_id: ID to correlate request/response | معرف لربط الطلب/الاستجابة
            priority: Message priority | أولوية الرسالة
            metadata: Additional metadata | بيانات وصفية إضافية
        """
        self.message_id = str(uuid.uuid4())
        self.message_type = message_type
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.council_id = council_id
        self.content = content
        self.correlation_id = correlation_id or self.message_id
        self.priority = priority
        self.timestamp = datetime.utcnow().isoformat()
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert message to dictionary
        تحويل الرسالة إلى قاموس
        """
        return {
            "message_id": self.message_id,
            "message_type": self.message_type.value,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "council_id": self.council_id,
            "content": self.content,
            "correlation_id": self.correlation_id,
            "priority": self.priority.value,
            "timestamp": self.timestamp,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentMessage":
        """
        Create message from dictionary
        إنشاء رسالة من قاموس
        """
        msg = cls(
            message_type=MessageType(data["message_type"]),
            sender_id=data["sender_id"],
            content=data["content"],
            recipient_id=data.get("recipient_id"),
            council_id=data.get("council_id"),
            correlation_id=data.get("correlation_id"),
            priority=MessagePriority(data.get("priority", "normal")),
            metadata=data.get("metadata", {}),
        )
        msg.message_id = data["message_id"]
        msg.timestamp = data["timestamp"]
        return msg

    def to_json(self) -> str:
        """
        Convert message to JSON string
        تحويل الرسالة إلى نص JSON
        """
        return json.dumps(self.to_dict(), ensure_ascii=False)

    @classmethod
    def from_json(cls, json_str: str) -> "AgentMessage":
        """
        Create message from JSON string
        إنشاء رسالة من نص JSON
        """
        return cls.from_dict(json.loads(json_str))


class AgentNATSBridge:
    """
    NATS communication bridge for multi-agent system
    جسر اتصال NATS لنظام الوكلاء المتعددين

    Handles all agent-to-agent communication through NATS messaging.
    يتعامل مع جميع اتصالات الوكيل إلى الوكيل من خلال نظام رسائل NATS.

    Topics:
    - sahool.agents.{agent_id}.request - Incoming requests
    - sahool.agents.{agent_id}.response - Responses
    - sahool.agents.broadcast - Broadcast to all agents
    - sahool.agents.council.{council_id} - Council communications
    """

    def __init__(
        self,
        agent_id: str,
        nats_url: str = "nats://localhost:4222",
        max_reconnect_attempts: int = 10,
        reconnect_time_wait: int = 2,
    ):
        """
        Initialize NATS bridge
        تهيئة جسر NATS

        Args:
            agent_id: Unique agent identifier | معرف الوكيل الفريد
            nats_url: NATS server URL | عنوان خادم NATS
            max_reconnect_attempts: Max reconnection attempts | محاولات إعادة الاتصال القصوى
            reconnect_time_wait: Wait time between reconnects | وقت الانتظار بين إعادة الاتصال
        """
        self.agent_id = agent_id
        self.nats_url = nats_url
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_time_wait = reconnect_time_wait

        self.nc: Optional[NATSClient] = None
        self.subscriptions: Dict[str, Any] = {}
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self._is_connected = False

        logger.info(
            "nats_bridge_initialized",
            agent_id=agent_id,
            nats_url=nats_url
        )

    async def connect(self):
        """
        Connect to NATS server
        الاتصال بخادم NATS
        """
        try:
            self.nc = await nats.connect(
                servers=[self.nats_url],
                max_reconnect_attempts=self.max_reconnect_attempts,
                reconnect_time_wait=self.reconnect_time_wait,
                error_cb=self._error_callback,
                disconnected_cb=self._disconnected_callback,
                reconnected_cb=self._reconnected_callback,
                closed_cb=self._closed_callback,
            )
            self._is_connected = True

            # Subscribe to agent's request topic automatically
            # الاشتراك تلقائيًا في موضوع طلبات الوكيل
            await self.subscribe(
                self._get_agent_topic("request"),
                self._default_request_handler
            )

            # Subscribe to broadcast topic
            # الاشتراك في موضوع البث
            await self.subscribe(
                "sahool.agents.broadcast",
                self._default_broadcast_handler
            )

            logger.info(
                "nats_connected",
                agent_id=self.agent_id,
                server=self.nats_url
            )

        except Exception as e:
            logger.error(
                "nats_connection_failed",
                agent_id=self.agent_id,
                error=str(e)
            )
            raise

    async def disconnect(self):
        """
        Disconnect from NATS server
        قطع الاتصال عن خادم NATS
        """
        if self.nc and self._is_connected:
            # Unsubscribe from all topics
            # إلغاء الاشتراك من جميع المواضيع
            for sub in self.subscriptions.values():
                try:
                    await sub.unsubscribe()
                except Exception as e:
                    logger.warning("subscription_cleanup_failed", error=str(e))

            await self.nc.drain()
            self._is_connected = False

            logger.info("nats_disconnected", agent_id=self.agent_id)

    def _get_agent_topic(self, topic_type: str, agent_id: Optional[str] = None) -> str:
        """
        Get topic name for agent
        الحصول على اسم الموضوع للوكيل

        Args:
            topic_type: Type of topic (request/response) | نوع الموضوع
            agent_id: Agent ID (defaults to self) | معرف الوكيل

        Returns:
            Full topic name | اسم الموضوع الكامل
        """
        target_id = agent_id or self.agent_id
        return f"sahool.agents.{target_id}.{topic_type}"

    def _get_council_topic(self, council_id: str) -> str:
        """
        Get topic name for council
        الحصول على اسم الموضوع للمجلس

        Args:
            council_id: Council identifier | معرف المجلس

        Returns:
            Full topic name | اسم الموضوع الكامل
        """
        return f"sahool.agents.council.{council_id}"

    async def publish_to_agent(
        self,
        agent_id: str,
        content: Dict[str, Any],
        message_type: MessageType = MessageType.REQUEST,
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send message to specific agent
        إرسال رسالة إلى وكيل محدد

        Args:
            agent_id: Target agent ID | معرف الوكيل المستهدف
            content: Message content | محتوى الرسالة
            message_type: Type of message | نوع الرسالة
            priority: Message priority | أولوية الرسالة
            metadata: Additional metadata | بيانات وصفية إضافية

        Returns:
            Message ID | معرف الرسالة
        """
        if not self._is_connected:
            raise ConnectionError("NATS bridge not connected")

        message = AgentMessage(
            message_type=message_type,
            sender_id=self.agent_id,
            recipient_id=agent_id,
            content=content,
            priority=priority,
            metadata=metadata,
        )

        topic = self._get_agent_topic("request", agent_id)

        try:
            await self.nc.publish(
                topic,
                message.to_json().encode()
            )

            logger.info(
                "message_published",
                from_agent=self.agent_id,
                to_agent=agent_id,
                message_id=message.message_id,
                topic=topic
            )

            return message.message_id

        except Exception as e:
            logger.error(
                "message_publish_failed",
                from_agent=self.agent_id,
                to_agent=agent_id,
                error=str(e)
            )
            raise

    async def broadcast(
        self,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Broadcast message to all agents
        بث رسالة إلى جميع الوكلاء

        Args:
            content: Message content | محتوى الرسالة
            priority: Message priority | أولوية الرسالة
            metadata: Additional metadata | بيانات وصفية إضافية

        Returns:
            Message ID | معرف الرسالة
        """
        if not self._is_connected:
            raise ConnectionError("NATS bridge not connected")

        message = AgentMessage(
            message_type=MessageType.BROADCAST,
            sender_id=self.agent_id,
            content=content,
            priority=priority,
            metadata=metadata,
        )

        topic = "sahool.agents.broadcast"

        try:
            await self.nc.publish(
                topic,
                message.to_json().encode()
            )

            logger.info(
                "broadcast_published",
                from_agent=self.agent_id,
                message_id=message.message_id,
                topic=topic
            )

            return message.message_id

        except Exception as e:
            logger.error(
                "broadcast_failed",
                from_agent=self.agent_id,
                error=str(e)
            )
            raise

    async def publish_to_council(
        self,
        council_id: str,
        content: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send message to council
        إرسال رسالة إلى المجلس

        Args:
            council_id: Council identifier | معرف المجلس
            content: Message content | محتوى الرسالة
            priority: Message priority | أولوية الرسالة
            metadata: Additional metadata | بيانات وصفية إضافية

        Returns:
            Message ID | معرف الرسالة
        """
        if not self._is_connected:
            raise ConnectionError("NATS bridge not connected")

        message = AgentMessage(
            message_type=MessageType.COUNCIL,
            sender_id=self.agent_id,
            council_id=council_id,
            content=content,
            priority=priority,
            metadata=metadata,
        )

        topic = self._get_council_topic(council_id)

        try:
            await self.nc.publish(
                topic,
                message.to_json().encode()
            )

            logger.info(
                "council_message_published",
                from_agent=self.agent_id,
                council_id=council_id,
                message_id=message.message_id,
                topic=topic
            )

            return message.message_id

        except Exception as e:
            logger.error(
                "council_message_failed",
                from_agent=self.agent_id,
                council_id=council_id,
                error=str(e)
            )
            raise

    async def request_opinion(
        self,
        agent_id: str,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """
        Request opinion from another agent and wait for response
        طلب رأي من وكيل آخر والانتظار للاستجابة

        Args:
            agent_id: Target agent ID | معرف الوكيل المستهدف
            query: Question or query | سؤال أو استعلام
            context: Additional context | سياق إضافي
            timeout: Response timeout in seconds | مهلة الاستجابة بالثواني
            max_retries: Maximum retry attempts | محاولات إعادة المحاولة القصوى

        Returns:
            Agent's response | استجابة الوكيل
        """
        if not self._is_connected:
            raise ConnectionError("NATS bridge not connected")

        content = {
            "query": query,
            "context": context or {},
        }

        # Try with retries | المحاولة مع إعادة المحاولة
        for attempt in range(max_retries):
            try:
                message = AgentMessage(
                    message_type=MessageType.REQUEST,
                    sender_id=self.agent_id,
                    recipient_id=agent_id,
                    content=content,
                )

                # Create future for response
                # إنشاء مستقبل للاستجابة
                response_future = asyncio.Future()
                self.pending_requests[message.correlation_id] = response_future

                # Subscribe to response topic if not already
                # الاشتراك في موضوع الاستجابة إذا لم يتم بالفعل
                response_topic = self._get_agent_topic("response")
                if response_topic not in self.subscriptions:
                    await self.subscribe(response_topic, self._response_handler)

                # Publish request
                # نشر الطلب
                request_topic = self._get_agent_topic("request", agent_id)
                await self.nc.publish(
                    request_topic,
                    message.to_json().encode()
                )

                logger.info(
                    "opinion_requested",
                    from_agent=self.agent_id,
                    to_agent=agent_id,
                    correlation_id=message.correlation_id,
                    attempt=attempt + 1
                )

                # Wait for response with timeout
                # انتظار الاستجابة مع المهلة
                try:
                    response = await asyncio.wait_for(
                        response_future,
                        timeout=timeout
                    )

                    logger.info(
                        "opinion_received",
                        from_agent=agent_id,
                        to_agent=self.agent_id,
                        correlation_id=message.correlation_id
                    )

                    return response

                except asyncio.TimeoutError:
                    # Clean up pending request
                    # تنظيف الطلب المعلق
                    self.pending_requests.pop(message.correlation_id, None)

                    if attempt < max_retries - 1:
                        logger.warning(
                            "opinion_timeout_retry",
                            from_agent=self.agent_id,
                            to_agent=agent_id,
                            attempt=attempt + 1,
                            max_retries=max_retries
                        )
                        await asyncio.sleep(1)  # Wait before retry
                        continue
                    else:
                        logger.error(
                            "opinion_timeout",
                            from_agent=self.agent_id,
                            to_agent=agent_id,
                            timeout=timeout
                        )
                        raise TimeoutError(
                            f"No response from agent {agent_id} after {max_retries} attempts"
                        )

            except Exception as e:
                # Clean up pending request
                # تنظيف الطلب المعلق
                self.pending_requests.pop(message.correlation_id, None)

                if attempt < max_retries - 1:
                    logger.warning(
                        "opinion_request_error_retry",
                        from_agent=self.agent_id,
                        to_agent=agent_id,
                        error=str(e),
                        attempt=attempt + 1
                    )
                    await asyncio.sleep(1)
                    continue
                else:
                    logger.error(
                        "opinion_request_failed",
                        from_agent=self.agent_id,
                        to_agent=agent_id,
                        error=str(e)
                    )
                    raise

    async def send_response(
        self,
        recipient_id: str,
        content: Dict[str, Any],
        correlation_id: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Send response to a requesting agent
        إرسال استجابة إلى وكيل طالب

        Args:
            recipient_id: Requesting agent ID | معرف الوكيل الطالب
            content: Response content | محتوى الاستجابة
            correlation_id: Original request correlation ID | معرف ارتباط الطلب الأصلي
            metadata: Additional metadata | بيانات وصفية إضافية

        Returns:
            Message ID | معرف الرسالة
        """
        if not self._is_connected:
            raise ConnectionError("NATS bridge not connected")

        message = AgentMessage(
            message_type=MessageType.RESPONSE,
            sender_id=self.agent_id,
            recipient_id=recipient_id,
            content=content,
            correlation_id=correlation_id,
            metadata=metadata,
        )

        topic = self._get_agent_topic("response", recipient_id)

        try:
            await self.nc.publish(
                topic,
                message.to_json().encode()
            )

            logger.info(
                "response_sent",
                from_agent=self.agent_id,
                to_agent=recipient_id,
                correlation_id=correlation_id,
                message_id=message.message_id
            )

            return message.message_id

        except Exception as e:
            logger.error(
                "response_send_failed",
                from_agent=self.agent_id,
                to_agent=recipient_id,
                error=str(e)
            )
            raise

    async def subscribe(
        self,
        topic: str,
        handler: Callable[[AgentMessage], None],
        queue_group: Optional[str] = None,
    ):
        """
        Subscribe to a topic
        الاشتراك في موضوع

        Args:
            topic: Topic to subscribe to | الموضوع للاشتراك فيه
            handler: Message handler function | دالة معالج الرسائل
            queue_group: Optional queue group for load balancing | مجموعة قائمة الانتظار للتوازن
        """
        if not self._is_connected:
            raise ConnectionError("NATS bridge not connected")

        async def message_callback(msg: Msg):
            """Internal callback wrapper | غلاف استدعاء داخلي"""
            try:
                message = AgentMessage.from_json(msg.data.decode())
                await handler(message)
            except Exception as e:
                logger.error(
                    "message_handler_error",
                    topic=topic,
                    error=str(e)
                )

        try:
            subscription = await self.nc.subscribe(
                topic,
                cb=message_callback,
                queue=queue_group
            )

            self.subscriptions[topic] = subscription

            logger.info(
                "topic_subscribed",
                agent_id=self.agent_id,
                topic=topic,
                queue_group=queue_group
            )

        except Exception as e:
            logger.error(
                "subscription_failed",
                agent_id=self.agent_id,
                topic=topic,
                error=str(e)
            )
            raise

    async def subscribe_to_council(
        self,
        council_id: str,
        handler: Callable[[AgentMessage], None],
    ):
        """
        Subscribe to council communications
        الاشتراك في اتصالات المجلس

        Args:
            council_id: Council identifier | معرف المجلس
            handler: Message handler function | دالة معالج الرسائل
        """
        topic = self._get_council_topic(council_id)
        await self.subscribe(topic, handler)

    async def unsubscribe(self, topic: str):
        """
        Unsubscribe from a topic
        إلغاء الاشتراك من موضوع

        Args:
            topic: Topic to unsubscribe from | الموضوع لإلغاء الاشتراك منه
        """
        if topic in self.subscriptions:
            try:
                await self.subscriptions[topic].unsubscribe()
                del self.subscriptions[topic]

                logger.info(
                    "topic_unsubscribed",
                    agent_id=self.agent_id,
                    topic=topic
                )

            except Exception as e:
                logger.error(
                    "unsubscription_failed",
                    agent_id=self.agent_id,
                    topic=topic,
                    error=str(e)
                )
                raise

    async def _default_request_handler(self, message: AgentMessage):
        """
        Default handler for incoming requests
        المعالج الافتراضي للطلبات الواردة

        Args:
            message: Incoming message | الرسالة الواردة
        """
        logger.info(
            "request_received",
            from_agent=message.sender_id,
            to_agent=self.agent_id,
            message_id=message.message_id,
            correlation_id=message.correlation_id
        )

        # This should be overridden by the agent implementation
        # يجب تجاوز هذا من قبل تنفيذ الوكيل
        logger.warning(
            "no_custom_request_handler",
            agent_id=self.agent_id,
            message="Using default request handler - consider implementing a custom handler"
        )

    async def _default_broadcast_handler(self, message: AgentMessage):
        """
        Default handler for broadcast messages
        المعالج الافتراضي لرسائل البث

        Args:
            message: Broadcast message | رسالة البث
        """
        logger.info(
            "broadcast_received",
            from_agent=message.sender_id,
            message_id=message.message_id,
            content=message.content
        )

    async def _response_handler(self, message: AgentMessage):
        """
        Handler for response messages
        معالج رسائل الاستجابة

        Args:
            message: Response message | رسالة الاستجابة
        """
        correlation_id = message.correlation_id

        if correlation_id in self.pending_requests:
            future = self.pending_requests.pop(correlation_id)
            if not future.done():
                future.set_result(message.content)

            logger.debug(
                "response_correlated",
                correlation_id=correlation_id,
                from_agent=message.sender_id,
                to_agent=self.agent_id
            )
        else:
            logger.warning(
                "orphan_response",
                correlation_id=correlation_id,
                from_agent=message.sender_id,
                message="Received response with no pending request"
            )

    async def _error_callback(self, error: Exception):
        """
        Callback for NATS errors
        استدعاء لأخطاء NATS

        Args:
            error: Error exception | استثناء الخطأ
        """
        logger.error(
            "nats_error",
            agent_id=self.agent_id,
            error=str(error)
        )

    async def _disconnected_callback(self):
        """
        Callback when disconnected from NATS
        استدعاء عند قطع الاتصال من NATS
        """
        self._is_connected = False
        logger.warning(
            "nats_disconnected",
            agent_id=self.agent_id,
            message="Connection to NATS lost, will attempt reconnection"
        )

    async def _reconnected_callback(self):
        """
        Callback when reconnected to NATS
        استدعاء عند إعادة الاتصال بـ NATS
        """
        self._is_connected = True
        logger.info(
            "nats_reconnected",
            agent_id=self.agent_id,
            message="Successfully reconnected to NATS"
        )

    async def _closed_callback(self):
        """
        Callback when connection is closed
        استدعاء عند إغلاق الاتصال
        """
        self._is_connected = False
        logger.info(
            "nats_closed",
            agent_id=self.agent_id,
            message="NATS connection closed"
        )

    @property
    def is_connected(self) -> bool:
        """
        Check if connected to NATS
        التحقق من الاتصال بـ NATS

        Returns:
            Connection status | حالة الاتصال
        """
        return self._is_connected

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on NATS connection
        إجراء فحص صحي على اتصال NATS

        Returns:
            Health status | حالة الصحة
        """
        return {
            "agent_id": self.agent_id,
            "connected": self._is_connected,
            "subscriptions": list(self.subscriptions.keys()),
            "pending_requests": len(self.pending_requests),
            "nats_url": self.nats_url,
        }
