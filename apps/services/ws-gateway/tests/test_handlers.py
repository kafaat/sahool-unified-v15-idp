"""
Unit Tests for WebSocket Message Handlers
اختبارات الوحدة لمعالجات رسائل WebSocket
"""

from unittest.mock import AsyncMock

import pytest
from src.handlers import WebSocketMessageHandler
from src.rooms import RoomManager


class TestWebSocketMessageHandler:
    """Test WebSocketMessageHandler class"""

    @pytest.fixture
    def setup_handler(self):
        """Setup handler with room manager"""
        room_manager = RoomManager()
        handler = WebSocketMessageHandler(room_manager)
        return handler, room_manager

    @pytest.mark.asyncio
    async def test_handle_ping(self, setup_handler):
        """Test ping message handling"""
        handler, _ = setup_handler

        response = await handler.handle_ping("conn_001", {"type": "ping"})

        assert response["type"] == "pong"
        assert "timestamp" in response

    @pytest.mark.asyncio
    async def test_handle_subscribe(self, setup_handler):
        """Test subscribe message handling"""
        handler, room_manager = setup_handler
        ws = AsyncMock()

        # Add connection first
        await room_manager.add_connection("conn_001", ws, "user_123", "tenant_001")

        message = {"type": "subscribe", "topics": ["alerts", "weather"]}

        response = await handler.handle_subscribe("conn_001", message)

        assert response["type"] == "subscribed"
        assert len(response["topics"]) > 0
        assert isinstance(response["failed"], list)

    @pytest.mark.asyncio
    async def test_handle_subscribe_single_topic(self, setup_handler):
        """Test subscribing to single topic (not a list)"""
        handler, room_manager = setup_handler
        ws = AsyncMock()

        await room_manager.add_connection("conn_001", ws, "user_123", "tenant_001")

        message = {"type": "subscribe", "topics": "alerts"}  # Single string, not list

        response = await handler.handle_subscribe("conn_001", message)

        assert response["type"] == "subscribed"

    @pytest.mark.asyncio
    async def test_handle_unsubscribe(self, setup_handler):
        """Test unsubscribe message handling"""
        handler, room_manager = setup_handler
        ws = AsyncMock()

        await room_manager.add_connection("conn_001", ws, "user_123", "tenant_001")

        # Subscribe first
        await room_manager.join_room("conn_001", "alerts")

        # Unsubscribe
        message = {"type": "unsubscribe", "topics": ["alerts"]}

        response = await handler.handle_unsubscribe("conn_001", message)

        assert response["type"] == "unsubscribed"
        assert "alerts" in response["topics"]

    @pytest.mark.asyncio
    async def test_handle_join_room(self, setup_handler):
        """Test join room message handling"""
        handler, room_manager = setup_handler
        ws = AsyncMock()

        await room_manager.add_connection("conn_001", ws, "user_123", "tenant_001")

        message = {"type": "join_room", "room": "field:field_123"}

        response = await handler.handle_join_room("conn_001", message)

        assert response["type"] == "room_joined"
        assert response["room"] == "field:field_123"
        assert "field:field_123" in room_manager.rooms

    @pytest.mark.asyncio
    async def test_handle_join_room_missing_room_id(self, setup_handler):
        """Test join room without room ID"""
        handler, _ = setup_handler

        message = {
            "type": "join_room"
            # Missing room
        }

        response = await handler.handle_join_room("conn_001", message)

        assert response["type"] == "error"
        assert "Missing room ID" in response["error"]

    @pytest.mark.asyncio
    async def test_handle_leave_room(self, setup_handler):
        """Test leave room message handling"""
        handler, room_manager = setup_handler
        ws = AsyncMock()

        await room_manager.add_connection("conn_001", ws, "user_123", "tenant_001")
        await room_manager.join_room("conn_001", "field:field_123")

        message = {"type": "leave_room", "room": "field:field_123"}

        response = await handler.handle_leave_room("conn_001", message)

        assert response["type"] == "room_left"
        assert response["room"] == "field:field_123"

    @pytest.mark.asyncio
    async def test_handle_broadcast(self, setup_handler):
        """Test broadcast message handling"""
        handler, room_manager = setup_handler
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await room_manager.add_connection("conn_001", ws1, "user_1", "tenant_001")
        await room_manager.add_connection("conn_002", ws2, "user_2", "tenant_001")

        await room_manager.join_room("conn_001", "field:field_123")
        await room_manager.join_room("conn_002", "field:field_123")

        message = {
            "type": "broadcast",
            "room": "field:field_123",
            "message": {"content": "Hello room"},
        }

        response = await handler.handle_broadcast("conn_001", message)

        assert response["type"] == "broadcast_sent"
        assert response["room"] == "field:field_123"
        assert response["recipients"] == 1  # Excludes sender

    @pytest.mark.asyncio
    async def test_handle_broadcast_missing_room(self, setup_handler):
        """Test broadcast without room ID"""
        handler, _ = setup_handler

        message = {
            "type": "broadcast",
            "message": {"content": "Hello"},
            # Missing room
        }

        response = await handler.handle_broadcast("conn_001", message)

        assert response["type"] == "error"
        assert "Missing room ID" in response["error"]

    @pytest.mark.asyncio
    async def test_handle_typing(self, setup_handler):
        """Test typing indicator handling"""
        handler, room_manager = setup_handler
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await room_manager.add_connection("conn_001", ws1, "user_1", "tenant_001")
        await room_manager.add_connection("conn_002", ws2, "user_2", "tenant_001")

        await room_manager.join_room("conn_001", "chat:chat_123")
        await room_manager.join_room("conn_002", "chat:chat_123")

        message = {"type": "typing", "room": "chat:chat_123", "typing": True}

        response = await handler.handle_typing("conn_001", message)

        assert response["type"] == "typing_sent"
        assert response["room"] == "chat:chat_123"
        # ws2 should receive typing indicator
        assert ws2.send_json.called

    @pytest.mark.asyncio
    async def test_handle_read_receipt(self, setup_handler):
        """Test read receipt handling"""
        handler, room_manager = setup_handler
        ws1 = AsyncMock()
        ws2 = AsyncMock()

        await room_manager.add_connection("conn_001", ws1, "user_1", "tenant_001")
        await room_manager.add_connection("conn_002", ws2, "user_2", "tenant_001")

        await room_manager.join_room("conn_001", "chat:chat_123")
        await room_manager.join_room("conn_002", "chat:chat_123")

        message = {"type": "read", "room": "chat:chat_123", "message_id": "msg_456"}

        response = await handler.handle_read("conn_001", message)

        assert response["type"] == "read_sent"
        assert response["room"] == "chat:chat_123"
        assert response["message_id"] == "msg_456"
        assert ws2.send_json.called

    @pytest.mark.asyncio
    async def test_handle_unknown_message_type(self, setup_handler):
        """Test handling unknown message type"""
        handler, _ = setup_handler

        message = {"type": "unknown_type", "data": "test"}

        response = await handler.handle_message("conn_001", message)

        assert response["type"] == "error"
        assert "Unknown message type" in response["error"]

    @pytest.mark.asyncio
    async def test_handle_missing_message_type(self, setup_handler):
        """Test handling message without type"""
        handler, _ = setup_handler

        message = {
            "data": "test"
            # Missing type
        }

        response = await handler.handle_message("conn_001", message)

        assert response["type"] == "error"
        assert "Missing message type" in response["error"]

    @pytest.mark.asyncio
    async def test_topic_validation_global_topics(self, setup_handler):
        """Test global topics are always accessible"""
        handler, room_manager = setup_handler
        ws = AsyncMock()

        await room_manager.add_connection("conn_001", ws, "user_123", "tenant_001")

        # Global topics should be accessible
        assert handler._validate_topic_access("conn_001", "alerts")
        assert handler._validate_topic_access("conn_001", "weather")
        assert handler._validate_topic_access("conn_001", "global:system")

    @pytest.mark.asyncio
    async def test_topic_validation_tenant_match(self, setup_handler):
        """Test tenant topic validation"""
        handler, room_manager = setup_handler
        ws = AsyncMock()

        await room_manager.add_connection("conn_001", ws, "user_123", "tenant_001")

        # Own tenant - should be accessible
        assert handler._validate_topic_access("conn_001", "tenant:tenant_001")

        # Different tenant - should not be accessible
        assert not handler._validate_topic_access("conn_001", "tenant:tenant_999")

    @pytest.mark.asyncio
    async def test_topic_validation_user_match(self, setup_handler):
        """Test user topic validation"""
        handler, room_manager = setup_handler
        ws = AsyncMock()

        await room_manager.add_connection("conn_001", ws, "user_123", "tenant_001")

        # Own user - should be accessible
        assert handler._validate_topic_access("conn_001", "user:user_123")

        # Different user - should not be accessible
        assert not handler._validate_topic_access("conn_001", "user:user_999")

    @pytest.mark.asyncio
    async def test_broadcast_permission_validation(self, setup_handler):
        """Test broadcast permission validation"""
        handler, room_manager = setup_handler
        ws = AsyncMock()

        await room_manager.add_connection("conn_001", ws, "user_123", "tenant_001")

        # Should be able to broadcast to accessible rooms
        assert handler._validate_broadcast_permission("conn_001", "alerts")
        assert handler._validate_broadcast_permission("conn_001", "tenant:tenant_001")

        # Should not broadcast to inaccessible rooms
        assert not handler._validate_broadcast_permission("conn_001", "tenant:tenant_999")
