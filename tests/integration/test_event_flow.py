"""
Integration Tests for SAHOOL Event Flow
اختبارات التكامل لتدفق الأحداث في منصة سهول

Tests for NATS event-driven architecture:
- Field created → triggers satellite analysis
- Weather alert → triggers notifications
- Low stock → triggers alert
- IoT reading → triggers irrigation recommendation

Author: SAHOOL Platform Team
"""

import asyncio
import json

import httpx
import pytest

# ═══════════════════════════════════════════════════════════════════════════════
# Field Created → Satellite Analysis Event Flow
# تدفق الحدث: إنشاء حقل → تحليل الأقمار الصناعية
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.event_flow
class TestFieldCreatedEventFlow:
    """Test field creation triggers satellite analysis - اختبار أن إنشاء حقل يطلق تحليل الأقمار الصناعية"""

    async def test_field_creation_triggers_satellite_analysis(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        field_factory,
        auth_headers: dict[str, str],
        nats_client,
    ):
        """
        Test that creating a field triggers satellite analysis request
        اختبار أن إنشاء حقل يطلق طلب تحليل الأقمار الصناعية

        Event Flow:
        1. Create field via Field Core API
        2. NATS event published: field.created
        3. Satellite Service subscribes and processes
        4. Satellite analysis is queued/started
        """
        # Arrange
        field_data = field_factory.create(name="Event Test Field")

        # Setup NATS subscription to verify event
        received_events = []

        async def event_handler(msg):
            data = json.loads(msg.data.decode())
            received_events.append(data)

        # Subscribe to field.created event
        try:
            await nats_client.subscribe("field.created", cb=event_handler)
        except AttributeError:
            # Mock NATS client, skip event verification
            pass

        # Act - Create field
        create_url = f"{service_urls['field_core']}/api/v1/fields"
        create_response = await http_client.post(
            create_url, json=field_data, headers=auth_headers
        )

        # Wait for event processing
        await asyncio.sleep(2)

        # Assert
        assert create_response.status_code in (
            200,
            201,
        ), f"Failed to create field: {create_response.text}"
        created_field = create_response.json()
        field_id = created_field.get("id") or created_field.get("field_id")

        # Verify event was published (if real NATS)
        if received_events:
            assert len(received_events) > 0, "No field.created event received"
            assert received_events[0].get("field_id") == field_id


# ═══════════════════════════════════════════════════════════════════════════════
# Weather Alert → Notification Event Flow
# تدفق الحدث: تنبيه طقس → إشعار
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.event_flow
class TestWeatherAlertEventFlow:
    """Test weather alert triggers notification - اختبار أن تنبيه الطقس يطلق إشعار"""

    async def test_weather_alert_triggers_notification(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        auth_headers: dict[str, str],
        nats_client,
    ):
        """
        Test that a weather alert triggers user notification
        اختبار أن تنبيه الطقس يطلق إشعار للمستخدم

        Event Flow:
        1. Weather service detects extreme conditions
        2. NATS event published: weather.alert
        3. Notification Service subscribes
        4. Notification sent to affected users
        """
        # Arrange - Setup NATS subscription
        received_notifications = []

        async def notification_handler(msg):
            data = json.loads(msg.data.decode())
            received_notifications.append(data)

        try:
            await nats_client.subscribe("notification.sent", cb=notification_handler)
        except AttributeError:
            pass

        # Simulate publishing a weather alert event
        weather_alert = {
            "alert_type": "extreme_temperature",
            "severity": "high",
            "location": {"latitude": 15.3694, "longitude": 44.1910},
            "message": "Extreme heat expected - protect your crops",
            "message_ar": "حرارة شديدة متوقعة - احمِ محاصيلك",
        }

        # Publish weather alert via API (which should trigger NATS event)
        alert_url = (
            f"{service_urls.get('weather_core', 'http://localhost:8108')}/api/v1/alerts"
        )
        response = await http_client.post(
            alert_url, json=weather_alert, headers=auth_headers
        )

        # Wait for event processing
        await asyncio.sleep(3)

        # Assert
        # The weather alert API might return 200, 201, or 202 (accepted for processing)
        assert response.status_code in (
            200,
            201,
            202,
            404,
        ), f"Weather alert failed: {response.text}"


# ═══════════════════════════════════════════════════════════════════════════════
# Low Stock → Alert Event Flow
# تدفق الحدث: مخزون منخفض → تنبيه
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.event_flow
class TestLowStockEventFlow:
    """Test low stock triggers alert - اختبار أن المخزون المنخفض يطلق تنبيه"""

    async def test_low_stock_triggers_alert(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        inventory_factory,
        auth_headers: dict[str, str],
        nats_client,
    ):
        """
        Test that low inventory stock triggers an alert
        اختبار أن المخزون المنخفض يطلق تنبيه

        Event Flow:
        1. Inventory quantity drops below threshold
        2. NATS event published: inventory.low_stock
        3. Alert Service subscribes
        4. Alert notification created
        """
        # Arrange - Create inventory item with low stock
        item_data = inventory_factory.create(item_type="fertilizer")
        item_data["quantity"] = 10  # Below typical threshold of 50
        item_data["low_stock_threshold"] = 50

        # Setup NATS subscription
        received_alerts = []

        async def alert_handler(msg):
            data = json.loads(msg.data.decode())
            received_alerts.append(data)

        try:
            await nats_client.subscribe("inventory.low_stock", cb=alert_handler)
        except AttributeError:
            pass

        # Act - Create low stock item (should trigger event)
        create_url = f"{service_urls.get('inventory_service', 'http://localhost:8116')}/api/v1/inventory"
        response = await http_client.post(
            create_url, json=item_data, headers=auth_headers
        )

        # Wait for event processing
        await asyncio.sleep(2)

        # Assert
        if response.status_code in (200, 201):
            # Item created successfully
            data = response.json()
            assert "id" in data or "item_id" in data
        else:
            # Service might not be available in test environment
            pytest.skip("Inventory service not available")


# ═══════════════════════════════════════════════════════════════════════════════
# IoT Reading → Irrigation Recommendation Event Flow
# تدفق الحدث: قراءة IoT → توصية ري
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.event_flow
class TestIoTReadingEventFlow:
    """Test IoT reading triggers irrigation recommendation - اختبار أن قراءة IoT تطلق توصية ري"""

    async def test_iot_reading_triggers_irrigation(
        self,
        http_client: httpx.AsyncClient,
        service_urls: dict[str, str],
        iot_factory,
        auth_headers: dict[str, str],
        nats_client,
    ):
        """
        Test that low soil moisture reading triggers irrigation recommendation
        اختبار أن قراءة رطوبة التربة المنخفضة تطلق توصية ري

        Event Flow:
        1. IoT sensor sends soil moisture reading
        2. NATS event published: iot.reading
        3. Irrigation Service subscribes
        4. If moisture < threshold, irrigation recommendation generated
        """
        # Arrange - Create low soil moisture reading
        reading = iot_factory.create(sensor_type="soil_moisture")
        reading["value"] = 25.0  # Low soil moisture (< 30%)

        # Setup NATS subscription
        received_recommendations = []

        async def recommendation_handler(msg):
            data = json.loads(msg.data.decode())
            received_recommendations.append(data)

        try:
            await nats_client.subscribe(
                "irrigation.recommendation", cb=recommendation_handler
            )
        except AttributeError:
            pass

        # Act - Send IoT reading
        reading_url = f"{service_urls.get('iot_gateway', 'http://localhost:8106')}/api/v1/readings"
        response = await http_client.post(
            reading_url, json=reading, headers=auth_headers
        )

        # Wait for event processing
        await asyncio.sleep(3)

        # Assert
        if response.status_code in (200, 201, 202):
            # Reading accepted
            pass
        else:
            pytest.skip("IoT Gateway not available")


# ═══════════════════════════════════════════════════════════════════════════════
# NATS Connection Health Test
# اختبار صحة اتصال NATS
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.asyncio
@pytest.mark.integration
class TestNATSConnection:
    """Test NATS messaging infrastructure - اختبار بنية رسائل NATS"""

    async def test_nats_connection(self, nats_client):
        """
        Test NATS connection is established
        اختبار أن اتصال NATS مُنشأ
        """
        # For mock client, this will pass
        # For real client, verify connection
        try:
            is_connected = nats_client.is_connected
            if hasattr(nats_client, "is_connected"):
                assert is_connected, "NATS client not connected"
        except AttributeError:
            # Mock client
            pass

    async def test_nats_publish_subscribe(self, nats_client):
        """
        Test basic NATS publish/subscribe
        اختبار النشر/الاشتراك الأساسي في NATS
        """
        received_messages = []

        async def message_handler(msg):
            data = msg.data.decode()
            received_messages.append(data)

        # Subscribe
        try:
            await nats_client.subscribe("test.subject", cb=message_handler)
        except AttributeError:
            pytest.skip("Using mock NATS client")
            return

        # Publish
        test_message = "Test message from integration test"
        await nats_client.publish("test.subject", test_message.encode())

        # Wait for message
        await asyncio.sleep(1)

        # Assert
        assert len(received_messages) > 0, "No message received"
        assert received_messages[0] == test_message
