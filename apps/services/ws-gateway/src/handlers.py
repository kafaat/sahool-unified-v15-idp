"""
WebSocket Message Handlers
معالجات رسائل الويب سوكيت

Handles incoming WebSocket messages from clients
"""

import logging
from datetime import datetime
from typing import Any

from .events import EventType
from .rooms import RoomManager, RoomType

logger = logging.getLogger("ws-gateway.handlers")


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
            if not self._validate_topic_access(connection_id, topic):
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
            "timestamp": datetime.utcnow().isoformat(),
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
            "timestamp": datetime.utcnow().isoformat(),
            "message_ar": f"تم إلغاء الاشتراك من {len(left)} موضوع",
        }

    async def handle_ping(self, connection_id: str, message: dict) -> dict:
        """
        Respond to ping
        الرد على رسالة ping
        """
        return {
            "type": "pong",
            "timestamp": datetime.utcnow().isoformat(),
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
        if not self._validate_broadcast_permission(connection_id, room_id):
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
            "timestamp": datetime.utcnow().isoformat(),
        }

        # Broadcast (excluding sender)
        sent_count = await self.room_manager.broadcast_to_room(
            room_id, broadcast_msg, exclude_connection=connection_id
        )

        return {
            "type": "broadcast_sent",
            "room": room_id,
            "recipients": sent_count,
            "timestamp": datetime.utcnow().isoformat(),
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

        if not self._validate_topic_access(connection_id, room_id):
            return {
                "type": "error",
                "error": "Not authorized to join this room",
                "message_ar": "غير مصرح لك بالانضمام لهذه الغرفة",
            }

        success = await self.room_manager.join_room(connection_id, room_id)

        return {
            "type": "room_joined" if success else "error",
            "room": room_id,
            "timestamp": datetime.utcnow().isoformat(),
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
            "timestamp": datetime.utcnow().isoformat(),
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
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.room_manager.broadcast_to_room(
            room_id, typing_msg, exclude_connection=connection_id
        )

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
            "timestamp": datetime.utcnow().isoformat(),
        }

        await self.room_manager.broadcast_to_room(
            room_id, read_msg, exclude_connection=connection_id
        )

        return {
            "type": "read_sent",
            "room": room_id,
            "message_id": message_id,
        }

    def _validate_topic_access(self, connection_id: str, topic: str) -> bool:
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

        # Global topics - always allowed
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

        # Field/Farm topics - should belong to tenant
        # In production, verify field/farm ownership via database
        if topic_type in [RoomType.FIELD, RoomType.FARM]:
            return True  # Simplified - add proper validation

        return False

    def _validate_broadcast_permission(self, connection_id: str, room_id: str) -> bool:
        """
        Validate if connection can broadcast to room
        التحقق من صلاحية البث في الغرفة
        """
        # For now, allow broadcast if user can join the room
        return self._validate_topic_access(connection_id, room_id)
