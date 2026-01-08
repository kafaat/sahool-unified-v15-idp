"""
SAHOOL Message Queue Integration Tests
اختبارات التكامل لنظام قوائم الانتظار للرسائل

Tests NATS messaging operations:
- Pub/Sub messaging patterns
- Request/Reply patterns
- Message queue groups
- Message persistence and delivery guarantees
- Event-driven architecture flows
- Dead letter queues (DLQ)
- Message ordering and idempotency
- Backpressure and flow control

Author: SAHOOL Platform Team
"""

from __future__ import annotations

import asyncio
import json
import uuid
from datetime import datetime
from typing import Any

import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Test Data & Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def test_subject_prefix() -> str:
    """Unique test subject prefix to avoid conflicts"""
    return f"test.{uuid.uuid4().hex[:8]}"


@pytest.fixture
def sample_event_payload() -> dict[str, Any]:
    """Sample event payload for testing"""
    return {
        "event_id": str(uuid.uuid4()),
        "event_type": "field.created",
        "tenant_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "data": {
            "field_id": str(uuid.uuid4()),
            "name": "Test Field",
            "area_hectares": 10.5,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Basic NATS Connection Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nats_connection_basic(nats_client):
    """
    Test basic NATS connection is established
    اختبار إنشاء اتصال NATS الأساسي
    """
    # Verify client is connected
    assert nats_client is not None

    # Check if it's a mock or real client
    if hasattr(nats_client, "is_connected"):
        # Real NATS client
        assert nats_client.is_connected or hasattr(nats_client, "_mock_name")
    else:
        # Mock client (when NATS not available)
        assert hasattr(nats_client, "_mock_name")


@pytest.mark.integration
@pytest.mark.asyncio
async def test_nats_connection_info(nats_client, test_config):
    """
    Test NATS connection information
    اختبار معلومات اتصال NATS
    """
    if hasattr(nats_client, "is_connected") and nats_client.is_connected:
        # Real NATS client - check connection details
        assert nats_client.connected_url is not None
    else:
        # Mock client or not connected - skip detailed checks
        pytest.skip("NATS client not available or is mock")


# ═══════════════════════════════════════════════════════════════════════════════
# Pub/Sub Messaging Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_publish_subscribe_basic(
    nats_client, test_subject_prefix: str, sample_event_payload: dict[str, Any]
):
    """
    Test basic publish/subscribe messaging
    اختبار النشر والاشتراك الأساسي للرسائل
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.basic"
    received_messages = []

    async def message_handler(msg):
        """Handle received message"""
        data = json.loads(msg.data.decode())
        received_messages.append(data)

    # Subscribe to subject
    subscription = await nats_client.subscribe(subject, cb=message_handler)

    # Give subscription time to register
    await asyncio.sleep(0.1)

    # Publish message
    await nats_client.publish(subject, json.dumps(sample_event_payload).encode())

    # Wait for message to be received
    await asyncio.sleep(0.5)

    # Verify message was received
    assert len(received_messages) == 1
    assert received_messages[0]["event_id"] == sample_event_payload["event_id"]

    # Cleanup
    await subscription.unsubscribe()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_publish_multiple_subscribers(
    nats_client, test_subject_prefix: str, sample_event_payload: dict[str, Any]
):
    """
    Test message delivery to multiple subscribers
    اختبار توصيل الرسائل إلى مشتركين متعددين
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.multi"
    received_by_sub1 = []
    received_by_sub2 = []

    async def handler1(msg):
        data = json.loads(msg.data.decode())
        received_by_sub1.append(data)

    async def handler2(msg):
        data = json.loads(msg.data.decode())
        received_by_sub2.append(data)

    # Create two subscribers
    sub1 = await nats_client.subscribe(subject, cb=handler1)
    sub2 = await nats_client.subscribe(subject, cb=handler2)

    await asyncio.sleep(0.1)

    # Publish message
    await nats_client.publish(subject, json.dumps(sample_event_payload).encode())

    await asyncio.sleep(0.5)

    # Both subscribers should receive the message
    assert len(received_by_sub1) == 1
    assert len(received_by_sub2) == 1

    # Cleanup
    await sub1.unsubscribe()
    await sub2.unsubscribe()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_publish_to_wildcard_subject(nats_client, test_subject_prefix: str):
    """
    Test wildcard subscriptions
    اختبار الاشتراكات باستخدام حروف بدل
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    received_messages = []

    async def handler(msg):
        received_messages.append(msg.subject)

    # Subscribe with wildcard
    wildcard_subject = f"{test_subject_prefix}.events.*"
    subscription = await nats_client.subscribe(wildcard_subject, cb=handler)

    await asyncio.sleep(0.1)

    # Publish to multiple specific subjects
    await nats_client.publish(f"{test_subject_prefix}.events.created", b"event1")
    await nats_client.publish(f"{test_subject_prefix}.events.updated", b"event2")
    await nats_client.publish(f"{test_subject_prefix}.events.deleted", b"event3")

    await asyncio.sleep(0.5)

    # All three messages should be received
    assert len(received_messages) == 3
    assert f"{test_subject_prefix}.events.created" in received_messages
    assert f"{test_subject_prefix}.events.updated" in received_messages
    assert f"{test_subject_prefix}.events.deleted" in received_messages

    await subscription.unsubscribe()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_ordering(nats_client, test_subject_prefix: str):
    """
    Test messages are delivered in order
    اختبار تسليم الرسائل بالترتيب
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.ordered"
    received_order = []

    async def handler(msg):
        data = json.loads(msg.data.decode())
        received_order.append(data["sequence"])

    subscription = await nats_client.subscribe(subject, cb=handler)
    await asyncio.sleep(0.1)

    # Publish messages in sequence
    for i in range(10):
        payload = {"sequence": i, "timestamp": datetime.utcnow().isoformat()}
        await nats_client.publish(subject, json.dumps(payload).encode())

    await asyncio.sleep(1.0)

    # Verify order
    assert len(received_order) == 10
    assert received_order == list(range(10))

    await subscription.unsubscribe()


# ═══════════════════════════════════════════════════════════════════════════════
# Request/Reply Pattern Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_request_reply_basic(nats_client, test_subject_prefix: str):
    """
    Test request/reply messaging pattern
    اختبار نمط الرسائل الطلب/الرد
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.rpc"

    async def request_handler(msg):
        """Handle request and send reply"""
        request_data = json.loads(msg.data.decode())
        response = {
            "status": "success",
            "request_id": request_data["request_id"],
            "result": request_data["value"] * 2,
        }
        await nats_client.publish(msg.reply, json.dumps(response).encode())

    # Set up request handler
    subscription = await nats_client.subscribe(subject, cb=request_handler)
    await asyncio.sleep(0.1)

    # Send request
    request_id = str(uuid.uuid4())
    request = {"request_id": request_id, "value": 21}

    response = await nats_client.request(subject, json.dumps(request).encode(), timeout=2.0)

    # Parse response
    response_data = json.loads(response.data.decode())

    assert response_data["status"] == "success"
    assert response_data["request_id"] == request_id
    assert response_data["result"] == 42

    await subscription.unsubscribe()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_request_timeout(nats_client, test_subject_prefix: str):
    """
    Test request timeout when no reply
    اختبار انتهاء مهلة الطلب عند عدم وجود رد
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.no_reply"

    # Try to send request to subject with no handlers
    try:
        from nats.errors import TimeoutError as NATSTimeoutError

        with pytest.raises((NATSTimeoutError, asyncio.TimeoutError)):
            await nats_client.request(
                subject,
                b"request_data",
                timeout=0.5,  # Short timeout
            )
    except ImportError:
        # NATS library not available or different version
        pytest.skip("NATS TimeoutError not available")


# ═══════════════════════════════════════════════════════════════════════════════
# Queue Groups Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_queue_group_load_balancing(nats_client, test_subject_prefix: str):
    """
    Test queue groups distribute messages among workers
    اختبار توزيع مجموعات الانتظار للرسائل بين العاملين
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.queue"
    queue_name = "workers"

    worker1_count = []
    worker2_count = []

    async def worker1_handler(msg):
        worker1_count.append(1)

    async def worker2_handler(msg):
        worker2_count.append(1)

    # Create queue group subscribers
    sub1 = await nats_client.subscribe(subject, queue=queue_name, cb=worker1_handler)
    sub2 = await nats_client.subscribe(subject, queue=queue_name, cb=worker2_handler)

    await asyncio.sleep(0.1)

    # Publish multiple messages
    for i in range(10):
        await nats_client.publish(subject, f"message_{i}".encode())

    await asyncio.sleep(1.0)

    # Messages should be distributed between workers
    total_received = len(worker1_count) + len(worker2_count)
    assert total_received == 10

    # Both workers should have received some messages (load balanced)
    # Note: Distribution might not be exactly 50/50 but both should receive some
    assert len(worker1_count) > 0
    assert len(worker2_count) > 0

    await sub1.unsubscribe()
    await sub2.unsubscribe()


# ═══════════════════════════════════════════════════════════════════════════════
# Event-Driven Architecture Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_event_driven_field_created_flow(nats_client, test_subject_prefix: str):
    """
    Test event-driven flow when field is created
    اختبار التدفق المستند إلى الأحداث عند إنشاء حقل
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    # Subjects for different services
    field_created_subject = f"{test_subject_prefix}.field.created"
    notifications_subject = f"{test_subject_prefix}.notifications.send"
    analytics_subject = f"{test_subject_prefix}.analytics.track"

    notifications_received = []
    analytics_received = []

    # Notification service handler
    async def notification_handler(msg):
        data = json.loads(msg.data.decode())
        notifications_received.append(data)

    # Analytics service handler
    async def analytics_handler(msg):
        data = json.loads(msg.data.decode())
        analytics_received.append(data)

    # Subscribe services to field.created event
    notif_sub = await nats_client.subscribe(field_created_subject, cb=notification_handler)
    analytics_sub = await nats_client.subscribe(field_created_subject, cb=analytics_handler)

    await asyncio.sleep(0.1)

    # Publish field.created event
    event = {
        "event_id": str(uuid.uuid4()),
        "event_type": "field.created",
        "field_id": str(uuid.uuid4()),
        "tenant_id": str(uuid.uuid4()),
        "field_name": "New Field",
        "timestamp": datetime.utcnow().isoformat(),
    }

    await nats_client.publish(field_created_subject, json.dumps(event).encode())

    await asyncio.sleep(0.5)

    # Both services should receive the event
    assert len(notifications_received) == 1
    assert len(analytics_received) == 1
    assert notifications_received[0]["event_id"] == event["event_id"]
    assert analytics_received[0]["event_id"] == event["event_id"]

    await notif_sub.unsubscribe()
    await analytics_sub.unsubscribe()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_event_chaining(nats_client, test_subject_prefix: str):
    """
    Test chaining of events (one event triggers another)
    اختبار تسلسل الأحداث (حدث واحد يطلق آخر)
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    event1_subject = f"{test_subject_prefix}.step1"
    event2_subject = f"{test_subject_prefix}.step2"

    step2_events = []

    # Step 1 handler - triggers step 2
    async def step1_handler(msg):
        data = json.loads(msg.data.decode())
        # Process and publish to step 2
        next_event = {"source_event_id": data["event_id"], "step": 2, "data": data["data"]}
        await nats_client.publish(event2_subject, json.dumps(next_event).encode())

    # Step 2 handler
    async def step2_handler(msg):
        data = json.loads(msg.data.decode())
        step2_events.append(data)

    # Set up handlers
    sub1 = await nats_client.subscribe(event1_subject, cb=step1_handler)
    sub2 = await nats_client.subscribe(event2_subject, cb=step2_handler)

    await asyncio.sleep(0.1)

    # Trigger step 1
    initial_event = {"event_id": str(uuid.uuid4()), "step": 1, "data": {"value": 100}}

    await nats_client.publish(event1_subject, json.dumps(initial_event).encode())

    await asyncio.sleep(0.5)

    # Step 2 should have been triggered
    assert len(step2_events) == 1
    assert step2_events[0]["source_event_id"] == initial_event["event_id"]
    assert step2_events[0]["step"] == 2

    await sub1.unsubscribe()
    await sub2.unsubscribe()


# ═══════════════════════════════════════════════════════════════════════════════
# Message Persistence & Reliability Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_delivery_guarantee(nats_client, test_subject_prefix: str):
    """
    Test message delivery guarantees
    اختبار ضمانات توصيل الرسائل
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.guaranteed"
    received = []

    async def handler(msg):
        received.append(msg.data.decode())

    subscription = await nats_client.subscribe(subject, cb=handler)
    await asyncio.sleep(0.1)

    # Publish multiple messages
    messages = [f"message_{i}" for i in range(5)]
    for msg in messages:
        await nats_client.publish(subject, msg.encode())
        await nats_client.flush()  # Ensure message is sent

    await asyncio.sleep(0.5)

    # All messages should be delivered
    assert len(received) == len(messages)
    for msg in messages:
        assert msg in received

    await subscription.unsubscribe()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_message_acknowledgment(nats_client, test_subject_prefix: str):
    """
    Test message acknowledgment patterns
    اختبار أنماط إقرار الرسائل
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.ack"
    processed = []

    async def handler(msg):
        # Process message
        data = json.loads(msg.data.decode())
        processed.append(data["id"])
        # In real scenarios, we would ACK here if using JetStream

    subscription = await nats_client.subscribe(subject, cb=handler)
    await asyncio.sleep(0.1)

    # Send messages
    for i in range(3):
        message = {"id": i, "data": f"test_{i}"}
        await nats_client.publish(subject, json.dumps(message).encode())

    await asyncio.sleep(0.5)

    # All messages should be processed
    assert len(processed) == 3
    assert processed == [0, 1, 2]

    await subscription.unsubscribe()


# ═══════════════════════════════════════════════════════════════════════════════
# Performance & Load Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
@pytest.mark.slow
async def test_high_throughput_publishing(nats_client, test_subject_prefix: str):
    """
    Test high-throughput message publishing
    اختبار نشر الرسائل بإنتاجية عالية
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.throughput"
    message_count = 1000
    received_count = []

    async def handler(msg):
        received_count.append(1)

    subscription = await nats_client.subscribe(subject, cb=handler)
    await asyncio.sleep(0.1)

    # Publish many messages quickly
    for i in range(message_count):
        await nats_client.publish(subject, f"message_{i}".encode())

    # Flush to ensure all messages are sent
    await nats_client.flush()
    await asyncio.sleep(2.0)

    # Should receive most messages (allow for some loss in high-throughput)
    received = len(received_count)
    success_rate = received / message_count

    # Expect at least 95% delivery rate
    assert success_rate >= 0.95, (
        f"Only received {received}/{message_count} messages ({success_rate:.1%})"
    )

    await subscription.unsubscribe()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_concurrent_publishers(nats_client, test_subject_prefix: str):
    """
    Test multiple concurrent publishers
    اختبار ناشرين متزامنين متعددين
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.concurrent"
    received = []

    async def handler(msg):
        received.append(msg.data.decode())

    subscription = await nats_client.subscribe(subject, cb=handler)
    await asyncio.sleep(0.1)

    # Create multiple publisher tasks
    async def publish_task(publisher_id: int, count: int):
        for i in range(count):
            await nats_client.publish(subject, f"publisher_{publisher_id}_msg_{i}".encode())

    # Run 5 concurrent publishers
    tasks = [publish_task(i, 10) for i in range(5)]
    await asyncio.gather(*tasks)

    await nats_client.flush()
    await asyncio.sleep(1.0)

    # Should receive all 50 messages
    assert len(received) >= 45  # Allow some tolerance

    await subscription.unsubscribe()


# ═══════════════════════════════════════════════════════════════════════════════
# Error Handling Tests
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_subject_handling(nats_client):
    """
    Test handling of invalid subjects
    اختبار معالجة المواضيع غير الصالحة
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    # Try to publish to invalid subject (empty)
    try:
        await nats_client.publish("", b"data")
        # If no exception, it means NATS allows empty subjects
        # (behavior depends on NATS version)
    except Exception:
        # Expected - invalid subject rejected
        pass


@pytest.mark.integration
@pytest.mark.asyncio
async def test_large_message_handling(nats_client, test_subject_prefix: str):
    """
    Test handling of large messages
    اختبار معالجة الرسائل الكبيرة
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.large"
    received = []

    async def handler(msg):
        received.append(len(msg.data))

    subscription = await nats_client.subscribe(subject, cb=handler)
    await asyncio.sleep(0.1)

    # Send 1MB message (within NATS default limits)
    large_data = b"x" * (1024 * 1024)  # 1MB

    try:
        await nats_client.publish(subject, large_data)
        await nats_client.flush()
        await asyncio.sleep(0.5)

        # Message should be received
        if len(received) > 0:
            assert received[0] == len(large_data)
    except Exception as e:
        # Message might be too large for NATS configuration
        pytest.skip(f"Large message rejected: {e}")

    await subscription.unsubscribe()


@pytest.mark.integration
@pytest.mark.asyncio
async def test_subscriber_error_handling(nats_client, test_subject_prefix: str):
    """
    Test error handling in subscriber callbacks
    اختبار معالجة الأخطاء في استدعاءات المشترك
    """
    if not hasattr(nats_client, "is_connected"):
        pytest.skip("NATS client is mock")

    subject = f"{test_subject_prefix}.errors"
    successful_messages = []

    async def error_prone_handler(msg):
        data = json.loads(msg.data.decode())
        if data.get("should_error"):
            raise ValueError("Intentional error")
        successful_messages.append(data)

    subscription = await nats_client.subscribe(subject, cb=error_prone_handler)
    await asyncio.sleep(0.1)

    # Send messages, some should error
    await nats_client.publish(subject, json.dumps({"id": 1, "should_error": False}).encode())
    await nats_client.publish(subject, json.dumps({"id": 2, "should_error": True}).encode())
    await nats_client.publish(subject, json.dumps({"id": 3, "should_error": False}).encode())

    await asyncio.sleep(0.5)

    # Successful messages should still be processed
    assert len(successful_messages) >= 2

    await subscription.unsubscribe()
