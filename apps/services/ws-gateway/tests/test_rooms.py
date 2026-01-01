"""
Unit Tests for Room Management
اختبارات الوحدة لإدارة الغرف
"""

import pytest
from unittest.mock import Mock, AsyncMock
from src.rooms import Room, RoomManager, RoomType


class TestRoom:
    """Test Room class"""

    def test_room_initialization(self):
        """Test room initialization"""
        room = Room("test-room", RoomType.FIELD)

        assert room.room_id == "test-room"
        assert room.room_type == RoomType.FIELD
        assert len(room.connections) == 0
        assert room.is_empty is True
        assert room.connection_count == 0

    def test_add_connection(self):
        """Test adding connection to room"""
        room = Room("test-room", RoomType.USER)
        room.add_connection("conn-123")

        assert "conn-123" in room.connections
        assert room.connection_count == 1
        assert room.is_empty is False

    def test_remove_connection(self):
        """Test removing connection from room"""
        room = Room("test-room", RoomType.FIELD)
        room.add_connection("conn-123")
        room.add_connection("conn-456")

        room.remove_connection("conn-123")

        assert "conn-123" not in room.connections
        assert "conn-456" in room.connections
        assert room.connection_count == 1

    def test_remove_nonexistent_connection(self):
        """Test removing connection that doesn't exist"""
        room = Room("test-room", RoomType.FIELD)
        room.remove_connection("nonexistent")  # Should not raise error

        assert room.is_empty is True


class TestRoomManager:
    """Test RoomManager class"""

    @pytest.mark.asyncio
    async def test_add_connection(self, mock_websocket):
        """Test adding a WebSocket connection"""
        manager = RoomManager()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=mock_websocket,
            user_id="user-123",
            tenant_id="tenant-456",
        )

        assert "conn-1" in manager.connections
        assert "conn-1" in manager.connection_metadata
        assert manager.connection_metadata["conn-1"]["user_id"] == "user-123"
        assert manager.connection_metadata["conn-1"]["tenant_id"] == "tenant-456"

        # Check auto-joined rooms
        tenant_room = f"{RoomType.TENANT}:tenant-456"
        user_room = f"{RoomType.USER}:user-123"

        assert tenant_room in manager.rooms
        assert user_room in manager.rooms
        assert "conn-1" in manager.rooms[tenant_room].connections
        assert "conn-1" in manager.rooms[user_room].connections

    @pytest.mark.asyncio
    async def test_remove_connection(self, mock_websocket):
        """Test removing a WebSocket connection"""
        manager = RoomManager()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=mock_websocket,
            user_id="user-123",
            tenant_id="tenant-456",
        )

        await manager.remove_connection("conn-1")

        assert "conn-1" not in manager.connections
        assert "conn-1" not in manager.connection_metadata
        assert "conn-1" not in manager.connection_rooms

    @pytest.mark.asyncio
    async def test_join_room(self, mock_websocket):
        """Test joining a room"""
        manager = RoomManager()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=mock_websocket,
            user_id="user-123",
            tenant_id="tenant-456",
        )

        result = await manager.join_room("conn-1", "field:field-789")

        assert result is True
        assert "field:field-789" in manager.rooms
        assert "conn-1" in manager.rooms["field:field-789"].connections

    @pytest.mark.asyncio
    async def test_join_room_invalid_connection(self):
        """Test joining room with invalid connection"""
        manager = RoomManager()

        result = await manager.join_room("nonexistent", "field:field-789")

        assert result is False

    @pytest.mark.asyncio
    async def test_leave_room(self, mock_websocket):
        """Test leaving a room"""
        manager = RoomManager()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=mock_websocket,
            user_id="user-123",
            tenant_id="tenant-456",
        )

        await manager.join_room("conn-1", "field:field-789")
        result = await manager.leave_room("conn-1", "field:field-789")

        assert result is True
        # Room should be deleted if empty and not persistent
        assert "field:field-789" not in manager.rooms

    @pytest.mark.asyncio
    async def test_broadcast_to_room(self, mock_websocket):
        """Test broadcasting message to room"""
        manager = RoomManager()

        # Add multiple connections
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=ws1,
            user_id="user-1",
            tenant_id="tenant-456",
        )

        await manager.add_connection(
            connection_id="conn-2",
            websocket=ws2,
            user_id="user-2",
            tenant_id="tenant-456",
        )

        await manager.join_room("conn-1", "test-room")
        await manager.join_room("conn-2", "test-room")

        message = {"type": "test", "data": "hello"}
        sent_count = await manager.broadcast_to_room("test-room", message)

        assert sent_count == 2
        ws1.send_json.assert_called_with(message)
        ws2.send_json.assert_called_with(message)

    @pytest.mark.asyncio
    async def test_broadcast_to_room_with_exclude(self, mock_websocket):
        """Test broadcasting with excluded connection"""
        manager = RoomManager()

        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=ws1,
            user_id="user-1",
            tenant_id="tenant-456",
        )

        await manager.add_connection(
            connection_id="conn-2",
            websocket=ws2,
            user_id="user-2",
            tenant_id="tenant-456",
        )

        await manager.join_room("conn-1", "test-room")
        await manager.join_room("conn-2", "test-room")

        message = {"type": "test", "data": "hello"}
        sent_count = await manager.broadcast_to_room(
            "test-room", message, exclude_connection="conn-1"
        )

        assert sent_count == 1
        ws1.send_json.assert_not_called()
        ws2.send_json.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_user(self, mock_websocket):
        """Test sending message to user"""
        manager = RoomManager()

        ws1 = AsyncMock()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=ws1,
            user_id="user-123",
            tenant_id="tenant-456",
        )

        message = {"type": "direct", "data": "message for you"}
        sent_count = await manager.send_to_user("user-123", message)

        assert sent_count >= 1
        ws1.send_json.assert_called()

    @pytest.mark.asyncio
    async def test_send_to_tenant(self, mock_websocket):
        """Test sending message to tenant"""
        manager = RoomManager()

        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=ws1,
            user_id="user-1",
            tenant_id="tenant-456",
        )

        await manager.add_connection(
            connection_id="conn-2",
            websocket=ws2,
            user_id="user-2",
            tenant_id="tenant-456",
        )

        message = {"type": "tenant_announcement", "data": "all hands meeting"}
        sent_count = await manager.send_to_tenant("tenant-456", message)

        assert sent_count == 2

    @pytest.mark.asyncio
    async def test_send_to_field(self, mock_websocket):
        """Test sending message to field"""
        manager = RoomManager()

        ws1 = AsyncMock()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=ws1,
            user_id="user-123",
            tenant_id="tenant-456",
        )

        await manager.join_room("conn-1", "field:field-789")

        message = {"type": "field_update", "data": "irrigation started"}
        sent_count = await manager.send_to_field("field-789", message)

        assert sent_count >= 1

    def test_get_connection_metadata(self, mock_websocket):
        """Test getting connection metadata"""
        manager = RoomManager()

        # Manually add metadata
        manager.connection_metadata["conn-1"] = {
            "user_id": "user-123",
            "tenant_id": "tenant-456",
        }

        metadata = manager.get_connection_metadata("conn-1")

        assert metadata is not None
        assert metadata["user_id"] == "user-123"

    @pytest.mark.asyncio
    async def test_get_user_connections(self, mock_websocket):
        """Test getting all connections for a user"""
        manager = RoomManager()

        ws1 = AsyncMock()
        ws2 = AsyncMock()

        # Same user, multiple connections
        await manager.add_connection(
            connection_id="conn-1",
            websocket=ws1,
            user_id="user-123",
            tenant_id="tenant-456",
        )

        await manager.add_connection(
            connection_id="conn-2",
            websocket=ws2,
            user_id="user-123",
            tenant_id="tenant-456",
        )

        connections = manager.get_user_connections("user-123")

        assert len(connections) == 2
        assert "conn-1" in connections
        assert "conn-2" in connections

    @pytest.mark.asyncio
    async def test_get_stats(self, mock_websocket):
        """Test getting room statistics"""
        manager = RoomManager()

        await manager.add_connection(
            connection_id="conn-1",
            websocket=mock_websocket,
            user_id="user-123",
            tenant_id="tenant-456",
        )

        stats = manager.get_stats()

        assert "total_connections" in stats
        assert "total_rooms" in stats
        assert "rooms" in stats
        assert stats["total_connections"] >= 1

    def test_persistent_room_check(self):
        """Test persistent room identification"""
        manager = RoomManager()

        assert manager._is_persistent_room("tenant:tenant-123") is True
        assert manager._is_persistent_room("global:announcements") is True
        assert manager._is_persistent_room("field:field-456") is False
        assert manager._is_persistent_room("user:user-789") is False
