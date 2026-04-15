"""
WebSocket Message Handlers
معالجات رسائل الويب سوكيت

Handles incoming WebSocket messages from clients
"""

import logging
import os
from datetime import UTC, datetime
from typing import Any

import httpx

from .events import EventType
from .rooms import RoomManager, RoomType

FIELD_MANAGEMENT_BASE_URL = os.getenv(
    "FIELD_MANAGEMENT_SERVICE_URL",
    "http://field-management-service:3000",
)

try:
    FIELD_MANAGEMENT_TIMEOUT = float(os.getenv("FIELD_MANAGEMENT_TIMEOUT", "5.0"))
except (ValueError, TypeError):
    FIELD_MANAGEMENT_TIMEOUT = 5.0

# When True, field/farm access is granted when field-management-service is
# unreachable (fail-open).  Set to "false" for fail-closed behaviour.
WS_FIELD_ACCESS_FAIL_OPEN = os.getenv("WS_FIELD_ACCESS_FAIL_OPEN", "false").lower() in (
    "true",
    "1",
    "yes",
)

logger = logging.getLogger("ws-gateway.handlers")

# Reuse a single httpx.AsyncClient for connection pooling
_http_client: httpx.AsyncClient | None = None


def _get_http_client() -> httpx.AsyncClient:
    """Return a shared httpx.AsyncClient, creating it on first use."""
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=FIELD_MANAGEMENT_TIMEOUT)
    return _http_client


class MessageType:
    """Client message types"""

    SUBSCRIBE = "subscribe"
    UNSUBSCRIBE = "unsubscribe"
    PING = "ping"
    BROADCAST = "broadcast"
    JOIN_ROOM = "join_room"
    LEAVE_ROOM = "leave_room"
    TYPING = "typing"
    READ = "read"


class WebSocketMessageHandler:
    """
    Handles all incoming WebSocket messages
    معالج رسائل الويب سوكيت
    """

    def __init__(self, room_manager: RoomManager):
        self.room_manager = room_manager
        self.handlers = {
            MessageType.SUBSCRIBE: self.handle_subscribe,
            MessageType.UNSUBSCRIBE: self.handle_unsubscribe,
            MessageType.PING: self.handle_ping,
            MessageType.BROADCAST: self.handle_broadcast,
            MessageType.JOIN_ROOM: self.handle_join_room,
            MessageType.LEAVE_ROOM: self.handle_leave_room,
            MessageType.TYPING: self.handle_typing,
            MessageType.READ: self.handle_read,
        }

    async def handle_message(self, connection_id: str, message: dict[str, Any]) -> dict | None:
        """
        Route message to appropriate handler
        توجيه الرسالة إلى المعالج المناسب
        """
        msg_type = message.get("type")

        if not msg_type:
            return {
                "type": "error",
                "error": "Missing message type",
                "message_ar": "نوع الرسالة مفقود",
            }

        handler = self.handlers.get(msg_type)

        if not handler:
            return {
                "type": "error",
                "error": f"Unknown message type: {msg_type}",
                "message_ar": f"نوع رسالة غير معروف: {msg_type}",
            }

        try:
            return await handler(connection_id, message)
        except Exception as e:
            logger.error(f"Error handling {msg_type}: {e}", exc_info=True)
            return {
                "type": "error",
                "error": str(e),
                "message_ar": "حدث خطأ في معالجة الرسالة",
            }

    async def handle_subscribe(self, connection_id: str, message: dict) -> dict:
        """
        Subscribe to topics/rooms
        الاشتراك في المواضيع/الغرف

        Message format:
        {
            "type": "subscribe",
            "topics": ["field:123", "weather", "alerts"]
        }
        """
        topics = message.get("topics", [])

        if not isinstance(topics, list):
            topics = [topics]

        joined = []
        failed = []

        for topic in topics:
            # Validate topic format
            if not await self._validate_topic_access(connection_id, topic):
                failed.append(topic)
                continue

            # Join room for topic
            if await self.room_manager.join_room(connection_id, topic):
                joined.append(topic)
            else:
                failed.append(topic)

        return {
            "type": "subscribed",
            "topics": joined,
            "failed": failed,
            "timestamp": datetime.now(UTC).isoformat(),
            "message_ar": f"تم الاشتراك في {len(joined)} موضوع",
        }

    async def handle_unsubscribe(self, connection_id: str, message: dict) -> dict:
        """
        Unsubscribe from topics/rooms
        إلغاء الاشتراك من المواضيع
        """
        topics = message.get("topics", [])

        if not isinstance(topics, list):
            topics = [topics]

        left = []

        for topic in topics:
            if await self.room_manager.leave_room(connection_id, topic):
                left.append(topic)

        return {
            "type": "unsubscribed",
            "topics": left,
            "timestamp": datetime.now(UTC).isoformat(),
            "message_ar": f"تم إلغاء الاشتراك من {len(left)} موضوع",
        }

    async def handle_ping(self, connection_id: str, message: dict) -> dict:
        """
        Respond to ping
        الرد على رسالة ping
        """
        return {
            "type": "pong",
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def handle_broadcast(self, connection_id: str, message: dict) -> dict:
        """
        Broadcast message to room/topic
        بث رسالة إلى غرفة/موضوع

        Message format:
        {
            "type": "broadcast",
            "room": "field:123",
            "message": {...}
        }
        """
        room_id = message.get("room")
        msg_content = message.get("message", {})

        if not room_id:
            return {
                "type": "error",
                "error": "Missing room ID",
                "message_ar": "معرف الغرفة مفقود",
            }

        # Validate permission to broadcast to room
        if not await self._validate_broadcast_permission(connection_id, room_id):
            return {
                "type": "error",
                "error": "Not authorized to broadcast to this room",
                "message_ar": "غير مصرح لك بالبث في هذه الغرفة",
            }

        # Get sender metadata
        metadata = self.room_manager.get_connection_metadata(connection_id)

        # Prepare broadcast message
        broadcast_msg = {
            "type": "message",
            "room": room_id,
            "from": {
                "connection_id": connection_id,
                "user_id": metadata.get("user_id") if metadata else None,
            },
            "message": msg_content,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        # Broadcast (excluding sender)
        sent_count = await self.room_manager.broadcast_to_room(room_id, broadcast_msg, exclude_connection=connection_id)

        return {
            "type": "broadcast_sent",
            "room": room_id,
            "recipients": sent_count,
            "timestamp": datetime.now(UTC).isoformat(),
        }

    async def handle_join_room(self, connection_id: str, message: dict) -> dict:
        """
        Join a specific room
        الانضمام إلى غرفة محددة
        """
        room_id = message.get("room")

        if not room_id:
            return {
                "type": "error",
                "error": "Missing room ID",
                "message_ar": "معرف الغرفة مفقود",
            }

        if not await self._validate_topic_access(connection_id, room_id):
            return {
                "type": "error",
                "error": "Not authorized to join this room",
                "message_ar": "غير مصرح لك بالانضمام لهذه الغرفة",
            }

        success = await self.room_manager.join_room(connection_id, room_id)

        return {
            "type": "room_joined" if success else "error",
            "room": room_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "message_ar": "تم الانضمام للغرفة" if success else "فشل الانضمام للغرفة",
        }

    async def handle_leave_room(self, connection_id: str, message: dict) -> dict:
        """
        Leave a specific room
        مغادرة غرفة محددة
        """
        room_id = message.get("room")

        if not room_id:
            return {
                "type": "error",
                "error": "Missing room ID",
                "message_ar": "معرف الغرفة مفقود",
            }

        success = await self.room_manager.leave_room(connection_id, room_id)

        return {
            "type": "room_left" if success else "error",
            "room": room_id,
            "timestamp": datetime.now(UTC).isoformat(),
            "message_ar": "تم مغادرة الغرفة" if success else "فشل مغادرة الغرفة",
        }

    async def handle_typing(self, connection_id: str, message: dict) -> dict:
        """
        Handle typing indicator
        معالج مؤشر الكتابة
        """
        room_id = message.get("room")
        is_typing = message.get("typing", True)

        if not room_id:
            return {
                "type": "error",
                "error": "Missing room ID",
            }

        metadata = self.room_manager.get_connection_metadata(connection_id)

        # Broadcast typing status to room
        typing_msg = {
            "type": EventType.CHAT_TYPING,
            "room": room_id,
            "user_id": metadata.get("user_id") if metadata else None,
            "typing": is_typing,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await self.room_manager.broadcast_to_room(room_id, typing_msg, exclude_connection=connection_id)

        return {
            "type": "typing_sent",
            "room": room_id,
        }

    async def handle_read(self, connection_id: str, message: dict) -> dict:
        """
        Handle read receipt
        معالج إيصال القراءة
        """
        room_id = message.get("room")
        message_id = message.get("message_id")

        if not room_id or not message_id:
            return {
                "type": "error",
                "error": "Missing room ID or message ID",
            }

        metadata = self.room_manager.get_connection_metadata(connection_id)

        # Broadcast read status
        read_msg = {
            "type": EventType.CHAT_READ,
            "room": room_id,
            "message_id": message_id,
            "user_id": metadata.get("user_id") if metadata else None,
            "timestamp": datetime.now(UTC).isoformat(),
        }

        await self.room_manager.broadcast_to_room(room_id, read_msg, exclude_connection=connection_id)

        return {
            "type": "read_sent",
            "room": room_id,
            "message_id": message_id,
        }

    async def _validate_topic_access(self, connection_id: str, topic: str) -> bool:
        """
        Validate if connection has access to topic
        التحقق من صلاحية الوصول للموضوع
        """
        metadata = self.room_manager.get_connection_metadata(connection_id)
        if not metadata:
            return False

        tenant_id = metadata.get("tenant_id")
        user_id = metadata.get("user_id")

        # Parse topic
        parts = topic.split(":")
        topic_type = parts[0]

        # Global topics - always allowed (irrigation/fertilizer require tenant scoping)
        if topic_type in ["alerts", "weather", RoomType.GLOBAL]:
            return True

        # Tenant topic - check tenant match
        if topic_type == RoomType.TENANT:
            topic_tenant = parts[1] if len(parts) > 1 else None
            return topic_tenant == tenant_id

        # User topic - check user match
        if topic_type == RoomType.USER:
            topic_user = parts[1] if len(parts) > 1 else None
            return topic_user == user_id

        # Field/Farm topics - validate via field-management-service with graceful fallback
        if topic_type in [RoomType.FIELD, RoomType.FARM]:
            resource_id = parts[1] if len(parts) > 1 else None
            if not resource_id:
                logger.warning(f"Invalid {topic_type} topic format: {topic} - missing resource ID")
                return False

            # Support tenant-prefixed field IDs (e.g., field:tenant123:field456)
            # If the field ID includes a tenant prefix, validate it
            if len(parts) > 2:
                topic_tenant = parts[1]
                if topic_tenant != tenant_id:
                    logger.warning(
                        f"Tenant mismatch for {topic_type} topic: {topic}. "
                        f"User tenant: {tenant_id}, Topic tenant: {topic_tenant}"
                    )
                    return False
                # The actual resource ID is the last segment when tenant-prefixed
                resource_id = parts[2]

            # Validate access via field-management-service
            token = metadata.get("token")
            return await self._validate_field_access(
                resource_type=topic_type,
                resource_id=resource_id,
                user_id=user_id,
                tenant_id=tenant_id,
                token=token,
                topic=topic,
            )

        return False

    async def _validate_field_access(
        self,
        resource_type: RoomType,
        resource_id: str,
        user_id: str | None,
        tenant_id: str | None,
        token: str | None,
        topic: str,
    ) -> bool:
        """
        Validate field/farm access via field-management-service.
        Falls back to simplified (tenant-based) validation when the service
        is unreachable, ensuring graceful degradation for offline scenarios.

        التحقق من صلاحية الوصول للحقل/المزرعة عبر خدمة إدارة الحقول
        مع التراجع إلى التحقق المبسط عند عدم توفر الخدمة
        """
        # Build the endpoint path based on resource type
        if resource_type == RoomType.FIELD:
            path = f"/api/v1/fields/{resource_id}"
        elif resource_type == RoomType.FARM:
            path = f"/api/v1/farms/{resource_id}"
        else:
            path = f"/api/v1/fields/{resource_id}"

        url = f"{FIELD_MANAGEMENT_BASE_URL}{path}"
        headers: dict[str, str] = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if tenant_id:
            headers["X-Tenant-ID"] = tenant_id

        try:
            client = _get_http_client()
            response = await client.get(url, headers=headers)

            if response.status_code == 200:
                logger.info(
                    f"Field/farm access validated via field-management-service. "
                    f"Topic: {topic}, User: {user_id}, Tenant: {tenant_id}"
                )
                return True

            if 400 <= response.status_code < 500:
                # All client errors (400, 401, 403, 404, etc.) are explicit denials
                logger.warning(
                    f"Field/farm access denied by field-management-service "
                    f"(HTTP {response.status_code}). "
                    f"Topic: {topic}, User: {user_id}, Tenant: {tenant_id}"
                )
                return False

            # Server errors (5xx) - fall through to simplified validation
            logger.warning(
                f"Server error from field-management-service "
                f"(HTTP {response.status_code}). "
                f"Falling back to simplified validation. "
                f"Topic: {topic}, User: {user_id}, Tenant: {tenant_id}"
            )

        except (httpx.ConnectError, httpx.TimeoutException) as exc:
            logger.warning(
                f"field-management-service unreachable ({type(exc).__name__}). "
                f"Falling back to simplified validation. "
                f"Topic: {topic}, User: {user_id}, Tenant: {tenant_id}"
            )
        except httpx.HTTPError as exc:
            logger.warning(
                f"HTTP error contacting field-management-service: {exc}. "
                f"Falling back to simplified validation. "
                f"Topic: {topic}, User: {user_id}, Tenant: {tenant_id}"
            )

        # Graceful degradation: behaviour depends on WS_FIELD_ACCESS_FAIL_OPEN.
        if not WS_FIELD_ACCESS_FAIL_OPEN:
            logger.warning(
                f"Field/farm access denied (fail-closed, service unavailable). "
                f"Topic: {topic}, User: {user_id}, Tenant: {tenant_id}"
            )
            return False

        # Fail-open: allow access only if the user has a valid tenant_id
        # (authenticated user).  Without the authoritative check from
        # field-management-service we cannot verify field-level ownership, but
        # we ensure at minimum that an authenticated, tenant-scoped user is
        # making the request.
        if tenant_id:
            logger.info(
                f"Field/farm access granted (fail-open, service unavailable). "
                f"Topic: {topic}, User: {user_id}, Tenant: {tenant_id}"
            )
            return True

        logger.warning(f"Field/farm access denied (no tenant_id, service unavailable). Topic: {topic}, User: {user_id}")
        return False

    async def _validate_broadcast_permission(self, connection_id: str, room_id: str) -> bool:
        """
        Validate if connection can broadcast to room
        التحقق من صلاحية البث في الغرفة
        """
        # Allow broadcast if user can join the room
        return await self._validate_topic_access(connection_id, room_id)
