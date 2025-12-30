"""
Unit Tests for NATS Bridge
اختبارات الوحدة لجسر NATS

Tests the functionality of AgentNATSBridge.
يختبر وظيفة AgentNATSBridge.
"""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from nats_bridge import (
    AgentNATSBridge,
    AgentMessage,
    MessageType,
    MessagePriority,
)


class TestAgentMessage:
    """Test AgentMessage class | اختبار فئة AgentMessage"""

    def test_message_creation(self):
        """Test creating a message | اختبار إنشاء رسالة"""
        message = AgentMessage(
            message_type=MessageType.REQUEST,
            sender_id="agent-1",
            content={"query": "test"},
            recipient_id="agent-2",
        )

        assert message.sender_id == "agent-1"
        assert message.recipient_id == "agent-2"
        assert message.content == {"query": "test"}
        assert message.message_type == MessageType.REQUEST
        assert message.priority == MessagePriority.NORMAL

    def test_message_to_dict(self):
        """Test converting message to dict | اختبار تحويل الرسالة إلى قاموس"""
        message = AgentMessage(
            message_type=MessageType.REQUEST,
            sender_id="agent-1",
            content={"test": "data"},
        )

        msg_dict = message.to_dict()

        assert msg_dict["sender_id"] == "agent-1"
        assert msg_dict["content"] == {"test": "data"}
        assert msg_dict["message_type"] == "request"
        assert "message_id" in msg_dict
        assert "timestamp" in msg_dict

    def test_message_from_dict(self):
        """Test creating message from dict | اختبار إنشاء رسالة من قاموس"""
        data = {
            "message_id": "test-123",
            "message_type": "request",
            "sender_id": "agent-1",
            "recipient_id": "agent-2",
            "content": {"query": "test"},
            "correlation_id": "corr-123",
            "priority": "high",
            "timestamp": "2024-01-01T00:00:00",
            "metadata": {}
        }

        message = AgentMessage.from_dict(data)

        assert message.message_id == "test-123"
        assert message.sender_id == "agent-1"
        assert message.priority == MessagePriority.HIGH

    def test_message_json_serialization(self):
        """Test JSON serialization | اختبار التسلسل JSON"""
        message = AgentMessage(
            message_type=MessageType.BROADCAST,
            sender_id="agent-1",
            content={"announcement": "test"},
        )

        json_str = message.to_json()
        reconstructed = AgentMessage.from_json(json_str)

        assert reconstructed.sender_id == message.sender_id
        assert reconstructed.content == message.content
        assert reconstructed.message_type == message.message_type


class TestAgentNATSBridge:
    """Test AgentNATSBridge class | اختبار فئة AgentNATSBridge"""

    def test_bridge_initialization(self):
        """Test bridge initialization | اختبار تهيئة الجسر"""
        bridge = AgentNATSBridge(
            agent_id="test-agent",
            nats_url="nats://localhost:4222"
        )

        assert bridge.agent_id == "test-agent"
        assert bridge.nats_url == "nats://localhost:4222"
        assert bridge.is_connected is False
        assert len(bridge.subscriptions) == 0

    def test_get_agent_topic(self):
        """Test topic name generation | اختبار توليد أسماء المواضيع"""
        bridge = AgentNATSBridge(agent_id="test-agent")

        request_topic = bridge._get_agent_topic("request")
        assert request_topic == "sahool.agents.test-agent.request"

        response_topic = bridge._get_agent_topic("response", "other-agent")
        assert response_topic == "sahool.agents.other-agent.response"

    def test_get_council_topic(self):
        """Test council topic generation | اختبار توليد موضوع المجلس"""
        bridge = AgentNATSBridge(agent_id="test-agent")

        council_topic = bridge._get_council_topic("crop-council")
        assert council_topic == "sahool.agents.council.crop-council"

    @pytest.mark.asyncio
    async def test_connect_not_available(self):
        """Test connection when NATS not available | اختبار الاتصال عند عدم توفر NATS"""
        bridge = AgentNATSBridge(
            agent_id="test-agent",
            nats_url="nats://localhost:9999"  # Invalid port
        )

        # Should raise an exception when NATS is not available
        # يجب أن يثير استثناء عند عدم توفر NATS
        with pytest.raises(Exception):
            await asyncio.wait_for(bridge.connect(), timeout=5.0)

    @pytest.mark.asyncio
    async def test_publish_without_connection(self):
        """Test publishing without connection | اختبار النشر بدون اتصال"""
        bridge = AgentNATSBridge(agent_id="test-agent")

        with pytest.raises(ConnectionError):
            await bridge.publish_to_agent(
                agent_id="other-agent",
                content={"test": "data"}
            )

    @pytest.mark.asyncio
    async def test_broadcast_without_connection(self):
        """Test broadcast without connection | اختبار البث بدون اتصال"""
        bridge = AgentNATSBridge(agent_id="test-agent")

        with pytest.raises(ConnectionError):
            await bridge.broadcast(content={"test": "data"})

    @pytest.mark.asyncio
    async def test_request_opinion_without_connection(self):
        """Test request opinion without connection | اختبار طلب الرأي بدون اتصال"""
        bridge = AgentNATSBridge(agent_id="test-agent")

        with pytest.raises(ConnectionError):
            await bridge.request_opinion(
                agent_id="other-agent",
                query="test query"
            )

    def test_health_check(self):
        """Test health check | اختبار الفحص الصحي"""
        bridge = AgentNATSBridge(
            agent_id="test-agent",
            nats_url="nats://localhost:4222"
        )

        health = asyncio.run(bridge.health_check())

        assert health["agent_id"] == "test-agent"
        assert health["connected"] is False
        assert health["subscriptions"] == []
        assert health["pending_requests"] == 0
        assert health["nats_url"] == "nats://localhost:4222"


def test_message_priority_enum():
    """Test MessagePriority enum | اختبار تعداد أولوية الرسائل"""
    assert MessagePriority.LOW.value == "low"
    assert MessagePriority.NORMAL.value == "normal"
    assert MessagePriority.HIGH.value == "high"
    assert MessagePriority.URGENT.value == "urgent"


def test_message_type_enum():
    """Test MessageType enum | اختبار تعداد نوع الرسائل"""
    assert MessageType.REQUEST.value == "request"
    assert MessageType.RESPONSE.value == "response"
    assert MessageType.BROADCAST.value == "broadcast"
    assert MessageType.COUNCIL.value == "council"
    assert MessageType.NOTIFICATION.value == "notification"
    assert MessageType.HEARTBEAT.value == "heartbeat"


if __name__ == "__main__":
    # Run simple tests without pytest
    # تشغيل الاختبارات البسيطة بدون pytest
    print("Running NATS Bridge Tests...")
    print("تشغيل اختبارات جسر NATS...")
    print("=" * 60)

    # Test message creation
    print("\n1. Testing message creation...")
    message = AgentMessage(
        message_type=MessageType.REQUEST,
        sender_id="test-agent",
        content={"query": "test"}
    )
    print(f"   ✓ Message created with ID: {message.message_id}")

    # Test message serialization
    print("\n2. Testing message serialization...")
    json_str = message.to_json()
    reconstructed = AgentMessage.from_json(json_str)
    assert reconstructed.sender_id == message.sender_id
    print(f"   ✓ Message serialized and deserialized successfully")

    # Test bridge initialization
    print("\n3. Testing bridge initialization...")
    bridge = AgentNATSBridge(agent_id="test-agent")
    assert bridge.agent_id == "test-agent"
    print(f"   ✓ Bridge initialized for agent: {bridge.agent_id}")

    # Test topic generation
    print("\n4. Testing topic generation...")
    topic = bridge._get_agent_topic("request")
    assert topic == "sahool.agents.test-agent.request"
    print(f"   ✓ Topic generated: {topic}")

    # Test health check
    print("\n5. Testing health check...")
    health = asyncio.run(bridge.health_check())
    assert health["agent_id"] == "test-agent"
    print(f"   ✓ Health check passed")

    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("جميع الاختبارات نجحت! ✓")
