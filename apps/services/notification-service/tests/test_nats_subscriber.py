"""
Tests for src/nats_subscriber.py - NATS Subscriber Logic

Covers:
- SubscriberConfig defaults and parsing
- _get_nats_servers() and _get_nats_credentials()
- ReceivedEvent model
- NATSSubscriber class (connect, subscribe, handlers, message processing)
- Event-to-notification conversion
- Irrigation and decision recommendation handlers
- Singleton subscriber management
"""

import asyncio
import json
import os
from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from src.nats_subscriber import (
    NATSSubscriber,
    ReceivedEvent,
    SubscriberConfig,
    _get_nats_credentials,
    _get_nats_servers,
)

# ─────────────────────────────────────────────────────────────────────────────
# SubscriberConfig
# ─────────────────────────────────────────────────────────────────────────────


class TestSubscriberConfig:
    def test_default_config(self):
        config = SubscriberConfig()
        assert config.name == "notification-subscriber"
        assert config.reconnect_time_wait == 2
        assert config.max_reconnect_attempts == 60
        assert config.user is None
        assert config.password is None
        assert len(config.analysis_subjects) > 0

    def test_custom_config(self):
        config = SubscriberConfig(
            servers=["nats://custom:4222"],
            name="custom-sub",
            user="admin",
            password="secret",
        )
        assert config.servers == ["nats://custom:4222"]
        assert config.name == "custom-sub"
        assert config.user == "admin"
        assert config.password == "secret"

    def test_analysis_subjects_include_key_patterns(self):
        config = SubscriberConfig()
        subjects = config.analysis_subjects
        assert "sahool.analysis.*" in subjects
        assert "sahool.advisory.*" in subjects
        assert "sahool.recommendation.>" in subjects
        assert "sahool.vision.>" in subjects
        assert "sahool.alert.*" in subjects
        assert "sahool.task.*" in subjects
        assert "sahool.notification.*" in subjects


# ─────────────────────────────────────────────────────────────────────────────
# NATS URL Parsing
# ─────────────────────────────────────────────────────────────────────────────


class TestGetNatsServers:
    def test_default_when_no_env(self):
        with patch.dict(os.environ, {"NATS_URL": ""}, clear=False):
            # With empty string, urlparse may behave differently
            servers = _get_nats_servers()
            assert isinstance(servers, list)
            assert len(servers) >= 1

    def test_parses_standard_url(self):
        with patch.dict(os.environ, {"NATS_URL": "nats://myhost:4222"}, clear=False):
            servers = _get_nats_servers()
            assert servers == ["nats://myhost:4222"]

    def test_parses_url_with_credentials(self):
        with patch.dict(os.environ, {"NATS_URL": "nats://admin:pass123@myhost:4222"}, clear=False):
            servers = _get_nats_servers()
            assert servers == ["nats://myhost:4222"]

    def test_fallback_on_parse_error(self):
        with patch.dict(os.environ, {"NATS_URL": "not-a-url"}, clear=False):
            servers = _get_nats_servers()
            assert isinstance(servers, list)
            assert len(servers) >= 1


class TestGetNatsCredentials:
    def test_no_credentials(self):
        with patch.dict(os.environ, {"NATS_URL": ""}, clear=False):
            user, password = _get_nats_credentials()
            assert user is None
            assert password is None

    def test_with_credentials(self):
        with patch.dict(os.environ, {"NATS_URL": "nats://admin:secret@host:4222"}, clear=False):
            user, password = _get_nats_credentials()
            assert user == "admin"
            assert password == "secret"

    def test_no_password(self):
        with patch.dict(os.environ, {"NATS_URL": "nats://host:4222"}, clear=False):
            user, password = _get_nats_credentials()
            assert user is None
            assert password is None


# ─────────────────────────────────────────────────────────────────────────────
# ReceivedEvent Model
# ─────────────────────────────────────────────────────────────────────────────


class TestReceivedEvent:
    def test_minimal_event(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="analysis.ndvi",
            source_service="vegetation-analysis-service",
            timestamp=datetime.now(UTC),
        )
        assert event.event_id == "evt-1"
        assert event.notification_priority == "medium"
        assert event.notification_channels == ["in_app"]
        assert event.data == {}

    def test_full_event(self):
        event = ReceivedEvent(
            event_id="evt-2",
            event_type="irrigation.recommendation.ready",
            source_service="irrigation-smart",
            timestamp=datetime.now(UTC),
            tenant_id="tenant-1",
            field_id="field-123",
            farmer_id="farmer-456",
            data={"amount_mm": 25},
            notification_priority="high",
            notification_channels=["push", "in_app"],
            action_template={"title_ar": "ري", "title_en": "Irrigation"},
        )
        assert event.tenant_id == "tenant-1"
        assert event.field_id == "field-123"
        assert event.farmer_id == "farmer-456"
        assert event.notification_priority == "high"
        assert event.action_template is not None


# ─────────────────────────────────────────────────────────────────────────────
# NATSSubscriber
# ─────────────────────────────────────────────────────────────────────────────


class TestNATSSubscriber:
    def test_init_default_config(self):
        subscriber = NATSSubscriber()
        assert subscriber.config is not None
        assert subscriber._connected is False
        assert subscriber._nc is None
        assert subscriber._subscriptions == []

    def test_init_with_config(self):
        config = SubscriberConfig(name="test-sub")
        subscriber = NATSSubscriber(config=config)
        assert subscriber.config.name == "test-sub"

    def test_init_with_callback(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)
        assert subscriber._notification_callback is callback

    def test_is_connected_false_when_not_connected(self):
        subscriber = NATSSubscriber()
        assert subscriber.is_connected is False

    def test_is_connected_true_when_connected(self):
        subscriber = NATSSubscriber()
        subscriber._connected = True
        subscriber._nc = MagicMock()
        assert subscriber.is_connected is True

    def test_is_connected_false_when_nc_is_none(self):
        subscriber = NATSSubscriber()
        subscriber._connected = True
        subscriber._nc = None
        assert subscriber.is_connected is False

    def test_register_handler(self):
        subscriber = NATSSubscriber()
        handler = MagicMock()
        subscriber.register_handler("test.event", handler)
        assert "test.event" in subscriber._handlers
        assert subscriber._handlers["test.event"] is handler

    def test_connect_without_nats_available(self):
        async def _run():
            subscriber = NATSSubscriber()
            with patch("src.nats_subscriber._nats_available", False):
                result = await subscriber.connect()
                assert result is False
        asyncio.run(_run())

    def test_subscribe_when_not_connected(self):
        async def _run():
            subscriber = NATSSubscriber()
            result = await subscriber.subscribe()
            assert result is False
        asyncio.run(_run())

    def test_close_without_connection(self):
        async def _run():
            subscriber = NATSSubscriber()
            await subscriber.close()
            assert subscriber._connected is False
        asyncio.run(_run())

    def test_close_with_subscriptions(self):
        async def _run():
            subscriber = NATSSubscriber()
            mock_sub = AsyncMock()
            subscriber._subscriptions = [mock_sub]
            subscriber._nc = AsyncMock()
            subscriber._connected = True

            await subscriber.close()

            mock_sub.unsubscribe.assert_called_once()
            subscriber._nc.close.assert_called_once()
            assert subscriber._connected is False
            assert subscriber._subscriptions == []
        asyncio.run(_run())


# ─────────────────────────────────────────────────────────────────────────────
# Event to Notification Conversion
# ─────────────────────────────────────────────────────────────────────────────


class TestEventToNotificationData:
    def setup_method(self):
        self.subscriber = NATSSubscriber()

    def test_ndvi_event_maps_to_crop_health(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="ndvi_analysis",
            source_service="vegetation-analysis",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["type"] == "crop_health"

    def test_irrigation_event_maps_correctly(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="irrigation_schedule",
            source_service="irrigation-smart",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["type"] == "irrigation_reminder"

    def test_pest_event_maps_correctly(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="pest_detected",
            source_service="pest-detection",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["type"] == "pest_outbreak"

    def test_weather_event_maps_correctly(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="weather_alert",
            source_service="weather-service",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["type"] == "weather_alert"

    def test_unknown_event_maps_to_system(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="unknown_event",
            source_service="some-service",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["type"] == "system"

    def test_priority_mapping(self):
        for priority in ["low", "medium", "high", "critical"]:
            event = ReceivedEvent(
                event_id="evt-1",
                event_type="test",
                source_service="test",
                timestamp=datetime.now(UTC),
                notification_priority=priority,
            )
            result = self.subscriber._event_to_notification_data(event)
            assert result["priority"] == priority

    def test_unknown_priority_defaults_to_medium(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="test",
            source_service="test",
            timestamp=datetime.now(UTC),
            notification_priority="unknown",
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["priority"] == "medium"

    def test_with_action_template(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="advisory",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            action_template={
                "title_ar": "توصية",
                "title_en": "Recommendation",
                "description_ar": "نص التوصية",
                "description_en": "Recommendation text",
                "urgency": "high",
            },
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["title"] == "Recommendation"
        assert result["title_ar"] == "توصية"
        assert result["body"] == "Recommendation text"
        assert result["priority"] == "high"

    def test_with_action_template_summary_ar(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="advisory",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            action_template={
                "title_ar": "توصية",
                "title_en": "Rec",
                "summary_ar": "ملخص",
            },
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["body_ar"] == "ملخص"

    def test_without_action_template(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="test_update",
            source_service="test-service",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert "Update:" in result["title"]
        assert "تحديث:" in result["title_ar"]
        assert "test-service" in result["body"]

    def test_target_farmers_with_farmer_id(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="test",
            source_service="test",
            timestamp=datetime.now(UTC),
            farmer_id="farmer-123",
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["target_farmers"] == ["farmer-123"]

    def test_target_farmers_without_farmer_id(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="test",
            source_service="test",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["target_farmers"] == []

    def test_channels_from_event(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="test",
            source_service="test",
            timestamp=datetime.now(UTC),
            notification_channels=["push", "sms"],
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["channels"] == ["push", "sms"]

    def test_data_merged_with_event_data(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="test",
            source_service="test",
            timestamp=datetime.now(UTC),
            data={"field_id": "f-1", "custom": "value"},
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["data"]["custom"] == "value"
        assert result["data"]["event_id"] == "evt-1"
        assert result["data"]["source_service"] == "test"

    def test_expires_in_hours(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="test",
            source_service="test",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["expires_in_hours"] == 48

    def test_disease_event_maps_to_crop_health(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="disease_detected",
            source_service="crop-intelligence",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["type"] == "crop_health"

    def test_fertilization_event_maps_to_task_reminder(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="fertilization_plan",
            source_service="advisory",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["type"] == "task_reminder"

    def test_action_event_maps_to_task_reminder(self):
        event = ReceivedEvent(
            event_id="evt-1",
            event_type="action_required",
            source_service="task-service",
            timestamp=datetime.now(UTC),
        )
        result = self.subscriber._event_to_notification_data(event)
        assert result["type"] == "task_reminder"


# ─────────────────────────────────────────────────────────────────────────────
# Irrigation Recommendation Handler
# ─────────────────────────────────────────────────────────────────────────────


class TestIrrigationRecommendationHandler:
    @pytest.mark.asyncio
    async def test_basic_irrigation_recommendation(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-irr-1",
            event_type="irrigation.recommendation.ready",
            source_service="irrigation-smart",
            timestamp=datetime.now(UTC),
            field_id="field-123",
            tenant_id="tenant-1",
            farmer_id="farmer-456",
            data={
                "recommendation": {
                    "amount_mm": 25,
                    "title": "Irrigation Ready",
                    "title_ar": "الري جاهز",
                    "description": "Apply 25mm",
                    "description_ar": "طبق 25 ملم",
                }
            },
        )

        await subscriber._handle_irrigation_recommendation(event)

        callback.assert_called_once()
        notification_data = callback.call_args[0][0]
        assert notification_data["type"] == "irrigation_reminder"
        assert "25" in notification_data["title"]
        assert notification_data["channels"] == ["in_app"]

    @pytest.mark.asyncio
    async def test_irrigation_without_amount_mm(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-irr-2",
            event_type="irrigation.recommendation.ready",
            source_service="irrigation-smart",
            timestamp=datetime.now(UTC),
            data={
                "recommendation": {
                    "title": "Custom Title",
                    "title_ar": "عنوان مخصص",
                }
            },
        )

        await subscriber._handle_irrigation_recommendation(event)

        callback.assert_called_once()
        notification_data = callback.call_args[0][0]
        assert notification_data["title"] == "Custom Title"

    @pytest.mark.asyncio
    async def test_irrigation_without_callback(self):
        subscriber = NATSSubscriber(notification_callback=None)

        event = ReceivedEvent(
            event_id="evt-irr-3",
            event_type="irrigation.recommendation.ready",
            source_service="irrigation-smart",
            timestamp=datetime.now(UTC),
            data={"recommendation": {}},
        )

        # Should not raise
        await subscriber._handle_irrigation_recommendation(event)

    @pytest.mark.asyncio
    async def test_irrigation_field_id_from_data(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-irr-4",
            event_type="irrigation.recommendation.ready",
            source_service="irrigation-smart",
            timestamp=datetime.now(UTC),
            data={
                "field_id": "field-from-data",
                "recommendation": {"amount_mm": 10},
            },
        )

        await subscriber._handle_irrigation_recommendation(event)
        notification_data = callback.call_args[0][0]
        assert notification_data["data"]["field_id"] == "field-from-data"

    @pytest.mark.asyncio
    async def test_irrigation_with_custom_channels(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-irr-5",
            event_type="irrigation.recommendation.ready",
            source_service="irrigation-smart",
            timestamp=datetime.now(UTC),
            notification_channels=["push", "sms"],
            data={"recommendation": {"amount_mm": 15}},
        )

        await subscriber._handle_irrigation_recommendation(event)
        notification_data = callback.call_args[0][0]
        assert notification_data["channels"] == ["push", "sms"]


# ─────────────────────────────────────────────────────────────────────────────
# Decision Recommendation Handler
# ─────────────────────────────────────────────────────────────────────────────


class TestDecisionRecommendationHandler:
    @pytest.mark.asyncio
    async def test_irrigation_type_maps_correctly(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-dec-1",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            field_id="field-123",
            data={
                "recommendation": {
                    "type": "irrigation",
                    "title": "Irrigate Now",
                    "title_ar": "اروي الآن",
                    "description": "Apply water",
                    "description_ar": "طبق الماء",
                }
            },
        )

        await subscriber._handle_decision_recommendation(event)
        notification_data = callback.call_args[0][0]
        assert notification_data["type"] == "irrigation_reminder"

    @pytest.mark.asyncio
    async def test_pest_control_type(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-dec-2",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            data={
                "recommendation": {
                    "type": "pest_control",
                    "title": "Pest Alert",
                    "title_ar": "تنبيه آفات",
                }
            },
        )

        await subscriber._handle_decision_recommendation(event)
        notification_data = callback.call_args[0][0]
        assert notification_data["type"] == "pest_outbreak"

    @pytest.mark.asyncio
    async def test_fertilizer_type(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-dec-3",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            data={
                "recommendation": {
                    "type": "fertilizer",
                }
            },
        )

        await subscriber._handle_decision_recommendation(event)
        notification_data = callback.call_args[0][0]
        assert notification_data["type"] == "task_reminder"

    @pytest.mark.asyncio
    async def test_harvest_type(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-dec-4",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            data={
                "recommendation": {
                    "type": "harvest",
                }
            },
        )

        await subscriber._handle_decision_recommendation(event)
        notification_data = callback.call_args[0][0]
        assert notification_data["type"] == "task_reminder"

    @pytest.mark.asyncio
    async def test_unknown_type_maps_to_system(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-dec-5",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            data={
                "recommendation": {
                    "type": "unknown_type",
                }
            },
        )

        await subscriber._handle_decision_recommendation(event)
        notification_data = callback.call_args[0][0]
        assert notification_data["type"] == "system"

    @pytest.mark.asyncio
    async def test_priority_from_recommendation(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-dec-6",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            data={
                "recommendation": {
                    "type": "irrigation",
                    "priority": "critical",
                }
            },
        )

        await subscriber._handle_decision_recommendation(event)
        notification_data = callback.call_args[0][0]
        assert notification_data["priority"] == "critical"

    @pytest.mark.asyncio
    async def test_without_callback(self):
        subscriber = NATSSubscriber(notification_callback=None)

        event = ReceivedEvent(
            event_id="evt-dec-7",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            data={"recommendation": {}},
        )

        # Should not raise
        await subscriber._handle_decision_recommendation(event)

    @pytest.mark.asyncio
    async def test_expires_in_48_hours(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-dec-8",
            event_type="recommendation.created",
            source_service="advisory-service",
            timestamp=datetime.now(UTC),
            data={"recommendation": {"type": "general"}},
        )

        await subscriber._handle_decision_recommendation(event)
        notification_data = callback.call_args[0][0]
        assert notification_data["expires_in_hours"] == 48


# ─────────────────────────────────────────────────────────────────────────────
# Message Handler
# ─────────────────────────────────────────────────────────────────────────────


class TestMessageHandler:
    @pytest.mark.asyncio
    async def test_message_handler_parses_json(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        msg_data = {
            "event_id": "evt-msg-1",
            "event_type": "test.event",
            "source_service": "test-service",
            "timestamp": datetime.now(UTC).isoformat(),
            "data": {"key": "value"},
        }

        mock_msg = MagicMock()
        mock_msg.subject = "sahool.analysis.test"
        mock_msg.data = json.dumps(msg_data).encode("utf-8")

        await subscriber._message_handler(mock_msg)
        # callback should be called (for _process_event_to_notification)
        assert callback.called

    @pytest.mark.asyncio
    async def test_message_handler_invalid_json(self):
        subscriber = NATSSubscriber()

        mock_msg = MagicMock()
        mock_msg.subject = "sahool.analysis.test"
        mock_msg.data = b"not valid json"

        # Should not raise
        await subscriber._message_handler(mock_msg)

    @pytest.mark.asyncio
    async def test_message_handler_derives_irrigation_event_type(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)
        subscriber._handlers["irrigation.recommendation.ready"] = AsyncMock()

        msg_data = {
            "event_id": "evt-msg-2",
            "source_service": "irrigation-smart",
            "timestamp": datetime.now(UTC).isoformat(),
            "data": {},
        }

        mock_msg = MagicMock()
        mock_msg.subject = "sahool.irrigation.recommendation.ready.v1"
        mock_msg.data = json.dumps(msg_data).encode("utf-8")

        await subscriber._message_handler(mock_msg)
        subscriber._handlers["irrigation.recommendation.ready"].assert_called_once()

    @pytest.mark.asyncio
    async def test_message_handler_derives_recommendation_event_type(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)
        subscriber._handlers["recommendation.created"] = AsyncMock()

        msg_data = {
            "event_id": "evt-msg-3",
            "source_service": "advisory-service",
            "timestamp": datetime.now(UTC).isoformat(),
            "data": {},
        }

        mock_msg = MagicMock()
        mock_msg.subject = "sahool.recommendation.fertilizer"
        mock_msg.data = json.dumps(msg_data).encode("utf-8")

        await subscriber._message_handler(mock_msg)
        subscriber._handlers["recommendation.created"].assert_called_once()

    @pytest.mark.asyncio
    async def test_message_handler_uses_event_type_from_payload(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        msg_data = {
            "event_id": "evt-msg-4",
            "event_type": "custom.type",
            "source_service": "test",
            "timestamp": datetime.now(UTC).isoformat(),
            "data": {},
        }

        mock_msg = MagicMock()
        mock_msg.subject = "sahool.analysis.test"
        mock_msg.data = json.dumps(msg_data).encode("utf-8")

        await subscriber._message_handler(mock_msg)
        assert callback.called


# ─────────────────────────────────────────────────────────────────────────────
# Process Event to Notification
# ─────────────────────────────────────────────────────────────────────────────


class TestProcessEventToNotification:
    @pytest.mark.asyncio
    async def test_process_event_calls_callback(self):
        callback = MagicMock()
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-proc-1",
            event_type="test",
            source_service="test",
            timestamp=datetime.now(UTC),
        )

        await subscriber._process_event_to_notification(event)
        callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_event_without_callback(self):
        subscriber = NATSSubscriber(notification_callback=None)

        event = ReceivedEvent(
            event_id="evt-proc-2",
            event_type="test",
            source_service="test",
            timestamp=datetime.now(UTC),
        )

        # Should not raise
        await subscriber._process_event_to_notification(event)

    @pytest.mark.asyncio
    async def test_process_event_callback_error_handled(self):
        callback = MagicMock(side_effect=Exception("callback error"))
        subscriber = NATSSubscriber(notification_callback=callback)

        event = ReceivedEvent(
            event_id="evt-proc-3",
            event_type="test",
            source_service="test",
            timestamp=datetime.now(UTC),
        )

        # Should not raise despite callback error
        await subscriber._process_event_to_notification(event)


# ─────────────────────────────────────────────────────────────────────────────
# Callback Methods
# ─────────────────────────────────────────────────────────────────────────────


class TestCallbackMethods:
    @pytest.mark.asyncio
    async def test_error_callback(self):
        subscriber = NATSSubscriber()
        # Should not raise
        await subscriber._error_callback(Exception("test error"))

    @pytest.mark.asyncio
    async def test_disconnected_callback(self):
        subscriber = NATSSubscriber()
        subscriber._connected = True
        await subscriber._disconnected_callback()
        assert subscriber._connected is False

    @pytest.mark.asyncio
    async def test_reconnected_callback(self):
        subscriber = NATSSubscriber()
        subscriber._connected = False
        await subscriber._reconnected_callback()
        assert subscriber._connected is True
