"""
WebSocket Room Management
إدارة الغرف في الويب سوكيت

Manages room subscriptions for targeted message delivery
"""

import logging
from datetime import datetime

from fastapi import WebSocket

logger = logging.getLogger("ws-gateway.rooms")


class RoomType:
    """
    Room type prefixes
    أنواع الغرف
    """

    FIELD = "field"
    FARM = "farm"
    USER = "user"
    TENANT = "tenant"
    ALERTS = "alerts"
    WEATHER = "weather"
    CHAT = "chat"
    GLOBAL = "global"


class Room:
    """Represents a WebSocket room"""

    def __init__(self, room_id: str, room_type: str):
        self.room_id = room_id
        self.room_type = room_type
        self.connections: set[str] = set()
        self.created_at = datetime.utcnow()
        self.metadata: dict = {}

    def add_connection(self, connection_id: str):
        """Add connection to room"""
        self.connections.add(connection_id)
        logger.info(f"Connection {connection_id} joined room {self.room_id}")

    def remove_connection(self, connection_id: str):
        """Remove connection from room"""
        self.connections.discard(connection_id)
        logger.info(f"Connection {connection_id} left room {self.room_id}")

    @property
    def is_empty(self) -> bool:
        """Check if room is empty"""
        return len(self.connections) == 0

    @property
    def connection_count(self) -> int:
        """Get number of connections in room"""
        return len(self.connections)


class RoomManager:
    """
    Manages WebSocket rooms for organized message routing
    إدارة الغرف لتوجيه الرسائل بشكل منظم
    """

    def __init__(self):
        # Map of room_id -> Room
        self.rooms: dict[str, Room] = {}

        # Map of connection_id -> Set[room_id]
        self.connection_rooms: dict[str, set[str]] = {}

        # Map of connection_id -> WebSocket
        self.connections: dict[str, WebSocket] = {}

        # Map of connection_id -> metadata (user_id, tenant_id, etc.)
        self.connection_metadata: dict[str, dict] = {}

    async def add_connection(
        self,
        connection_id: str,
        websocket: WebSocket,
        user_id: str,
        tenant_id: str,
        metadata: dict | None = None,
    ):
        """
        Add a new WebSocket connection
        إضافة اتصال جديد
        """
        self.connections[connection_id] = websocket
        self.connection_rooms[connection_id] = set()
        self.connection_metadata[connection_id] = {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "connected_at": datetime.utcnow().isoformat(),
            **(metadata or {}),
        }

        # Auto-join tenant room
        await self.join_room(connection_id, f"{RoomType.TENANT}:{tenant_id}")

        # Auto-join user room
        await self.join_room(connection_id, f"{RoomType.USER}:{user_id}")

        logger.info(
            f"Connection {connection_id} added. User: {user_id}, Tenant: {tenant_id}"
        )

    async def remove_connection(self, connection_id: str):
        """
        Remove a WebSocket connection and clean up rooms
        إزالة الاتصال وتنظيف الغرف
        """
        if connection_id not in self.connections:
            return

        # Leave all rooms
        if connection_id in self.connection_rooms:
            room_ids = list(self.connection_rooms[connection_id])
            for room_id in room_ids:
                await self.leave_room(connection_id, room_id)

        # Clean up
        del self.connections[connection_id]
        if connection_id in self.connection_rooms:
            del self.connection_rooms[connection_id]
        if connection_id in self.connection_metadata:
            del self.connection_metadata[connection_id]

        logger.info(f"Connection {connection_id} removed")

    async def join_room(self, connection_id: str, room_id: str) -> bool:
        """
        Join a room
        الانضمام إلى غرفة
        """
        if connection_id not in self.connections:
            logger.warning(f"Connection {connection_id} not found")
            return False

        # Parse room type
        room_type = room_id.split(":")[0] if ":" in room_id else RoomType.GLOBAL

        # Create room if it doesn't exist
        if room_id not in self.rooms:
            self.rooms[room_id] = Room(room_id, room_type)
            logger.info(f"Room {room_id} created")

        # Add connection to room
        self.rooms[room_id].add_connection(connection_id)
        self.connection_rooms[connection_id].add(room_id)

        return True

    async def leave_room(self, connection_id: str, room_id: str) -> bool:
        """
        Leave a room
        مغادرة غرفة
        """
        if room_id not in self.rooms:
            return False

        # Remove connection from room
        self.rooms[room_id].remove_connection(connection_id)

        if connection_id in self.connection_rooms:
            self.connection_rooms[connection_id].discard(room_id)

        # Delete empty rooms (except persistent rooms)
        if self.rooms[room_id].is_empty and not self._is_persistent_room(room_id):
            del self.rooms[room_id]
            logger.info(f"Empty room {room_id} deleted")

        return True

    async def broadcast_to_room(
        self, room_id: str, message: dict, exclude_connection: str | None = None
    ) -> int:
        """
        Broadcast message to all connections in a room
        بث رسالة لجميع الاتصالات في الغرفة

        Returns: Number of successful sends
        """
        if room_id not in self.rooms:
            logger.warning(f"Room {room_id} not found")
            return 0

        sent_count = 0
        room = self.rooms[room_id]

        for conn_id in room.connections:
            if exclude_connection and conn_id == exclude_connection:
                continue

            if await self._send_to_connection(conn_id, message):
                sent_count += 1

        logger.debug(
            f"Broadcasted to room {room_id}: {sent_count}/{room.connection_count} sent"
        )
        return sent_count

    async def send_to_user(self, user_id: str, message: dict) -> int:
        """
        Send message to all connections of a user
        إرسال رسالة لجميع اتصالات المستخدم
        """
        room_id = f"{RoomType.USER}:{user_id}"
        return await self.broadcast_to_room(room_id, message)

    async def send_to_tenant(self, tenant_id: str, message: dict) -> int:
        """
        Send message to all connections in a tenant
        إرسال رسالة لجميع الاتصالات في المستأجر
        """
        room_id = f"{RoomType.TENANT}:{tenant_id}"
        return await self.broadcast_to_room(room_id, message)

    async def send_to_field(self, field_id: str, message: dict) -> int:
        """
        Send message to all watchers of a field
        إرسال رسالة لجميع المراقبين لحقل معين
        """
        room_id = f"{RoomType.FIELD}:{field_id}"
        return await self.broadcast_to_room(room_id, message)

    async def _send_to_connection(self, connection_id: str, message: dict) -> bool:
        """
        Send message to a specific connection
        إرسال رسالة لاتصال محدد
        """
        if connection_id not in self.connections:
            return False

        try:
            websocket = self.connections[connection_id]
            await websocket.send_json(message)
            return True
        except Exception as e:
            logger.error(f"Failed to send to {connection_id}: {e}")
            # Schedule cleanup
            return False

    def _is_persistent_room(self, room_id: str) -> bool:
        """Check if room should persist even when empty"""
        # Keep tenant and global rooms
        return room_id.startswith(f"{RoomType.TENANT}:") or room_id.startswith(
            f"{RoomType.GLOBAL}:"
        )

    def get_connection_metadata(self, connection_id: str) -> dict | None:
        """Get metadata for a connection"""
        return self.connection_metadata.get(connection_id)

    def get_user_connections(self, user_id: str) -> set[str]:
        """Get all connection IDs for a user"""
        room_id = f"{RoomType.USER}:{user_id}"
        if room_id in self.rooms:
            return self.rooms[room_id].connections.copy()
        return set()

    def get_stats(self) -> dict:
        """
        Get room statistics
        الحصول على إحصائيات الغرف
        """
        return {
            "total_connections": len(self.connections),
            "total_rooms": len(self.rooms),
            "rooms": {
                room_id: {
                    "type": room.room_type,
                    "connections": room.connection_count,
                    "created_at": room.created_at.isoformat(),
                }
                for room_id, room in self.rooms.items()
            },
            "connections_by_room_type": self._get_connections_by_room_type(),
        }

    def _get_connections_by_room_type(self) -> dict[str, int]:
        """Get connection count by room type"""
        stats = {}
        for room in self.rooms.values():
            room_type = room.room_type
            if room_type not in stats:
                stats[room_type] = 0
            stats[room_type] += room.connection_count
        return stats
