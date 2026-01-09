"""
Unit Tests for Events Subscriber and DLQ
Tests subscriber configuration, DLQ config, and monitoring
"""

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pydantic import ValidationError

from shared.events.dlq_config import (
    DLQConfig,
    DLQMessageMetadata,
    StreamConfig,
    get_dlq_stream_config,
    should_retry,
    is_retriable_error,
)
from shared.events.subscriber import (
    EventSubscriber,
    SubscriberConfig,
)


# ═══════════════════════════════════════════════════════════════════════════
# DLQ Config Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestDLQConfig:
    """Test DLQConfig model"""

    def test_default_config(self):
        """Test default DLQ configuration"""
        config = DLQConfig()
        assert config.max_retry_attempts == 3
        assert config.initial_retry_delay == 1.0
        assert config.max_retry_delay == 60.0
        assert config.backoff_multiplier == 2.0
        assert config.dlq_stream_name == "SAHOOL_DLQ"
        assert config.dlq_subject_prefix == "sahool.dlq"
        assert config.dlq_max_age_days == 30
        assert config.dlq_max_messages == 100000
        assert config.alert_threshold == 100
        assert config.alert_enabled is True

    def test_custom_config(self):
        """Test custom DLQ configuration"""
        config = DLQConfig(
            max_retry_attempts=5,
            initial_retry_delay=2.0,
            max_retry_delay=120.0,
            backoff_multiplier=3.0,
            dlq_stream_name="CUSTOM_DLQ",
            alert_threshold=50,
        )
        assert config.max_retry_attempts == 5
        assert config.initial_retry_delay == 2.0
        assert config.max_retry_delay == 120.0
        assert config.backoff_multiplier == 3.0
        assert config.dlq_stream_name == "CUSTOM_DLQ"
        assert config.alert_threshold == 50

    def test_config_validation_max_retry(self):
        """Test max_retry_attempts validation"""
        config = DLQConfig(max_retry_attempts=1)
        assert config.max_retry_attempts == 1

        config = DLQConfig(max_retry_attempts=10)
        assert config.max_retry_attempts == 10

    def test_config_validation_delays(self):
        """Test delay validation"""
        config = DLQConfig(initial_retry_delay=0.1)
        assert config.initial_retry_delay == 0.1

        config = DLQConfig(max_retry_delay=1.0)
        assert config.max_retry_delay == 1.0

    def test_get_retry_delay(self):
        """Test retry delay calculation with exponential backoff"""
        config = DLQConfig(
            initial_retry_delay=1.0,
            max_retry_delay=60.0,
            backoff_multiplier=2.0,
        )

        # Attempt 1: 1.0 * 2^0 = 1.0
        assert config.get_retry_delay(1) == 1.0
        # Attempt 2: 1.0 * 2^1 = 2.0
        assert config.get_retry_delay(2) == 2.0
        # Attempt 3: 1.0 * 2^2 = 4.0
        assert config.get_retry_delay(3) == 4.0
        # Attempt 4: 1.0 * 2^3 = 8.0
        assert config.get_retry_delay(4) == 8.0

    def test_get_retry_delay_capped(self):
        """Test retry delay is capped at max_retry_delay"""
        config = DLQConfig(
            initial_retry_delay=10.0,
            max_retry_delay=30.0,
            backoff_multiplier=2.0,
        )

        # Attempt 1: 10.0
        assert config.get_retry_delay(1) == 10.0
        # Attempt 2: 20.0
        assert config.get_retry_delay(2) == 20.0
        # Attempt 3: 40.0 -> capped to 30.0
        assert config.get_retry_delay(3) == 30.0
        # Attempt 4: 80.0 -> capped to 30.0
        assert config.get_retry_delay(4) == 30.0

    def test_get_dlq_subject(self):
        """Test DLQ subject generation"""
        config = DLQConfig()

        result = config.get_dlq_subject("sahool.field.created")
        assert result == "sahool.dlq.field.created"

        result = config.get_dlq_subject("sahool.weather.alert")
        assert result == "sahool.dlq.weather.alert"

        # Without sahool prefix
        result = config.get_dlq_subject("field.created")
        assert result == "sahool.dlq.field.created"

    @patch.dict(
        os.environ,
        {
            "DLQ_MAX_RETRIES": "5",
            "DLQ_INITIAL_DELAY": "2.0",
            "DLQ_MAX_DELAY": "120.0",
            "DLQ_BACKOFF_MULTIPLIER": "3.0",
            "DLQ_STREAM_NAME": "ENV_DLQ",
            "DLQ_ALERT_THRESHOLD": "200",
        },
    )
    def test_from_env(self):
        """Test configuration from environment variables"""
        config = DLQConfig.from_env()
        assert config.max_retry_attempts == 5
        assert config.initial_retry_delay == 2.0
        assert config.max_retry_delay == 120.0
        assert config.backoff_multiplier == 3.0
        assert config.dlq_stream_name == "ENV_DLQ"
        assert config.alert_threshold == 200


class TestDLQMessageMetadata:
    """Test DLQMessageMetadata model"""

    def test_metadata_creation(self):
        """Test creating DLQ message metadata"""
        metadata = DLQMessageMetadata(
            original_subject="sahool.field.created",
            failure_reason="Handler error",
            failure_timestamp="2024-01-01T00:00:00Z",
            retry_count=3,
        )
        assert metadata.original_subject == "sahool.field.created"
        assert metadata.failure_reason == "Handler error"
        assert metadata.retry_count == 3

    def test_metadata_defaults(self):
        """Test metadata default values"""
        metadata = DLQMessageMetadata(
            original_subject="sahool.test",
            failure_reason="Error",
            failure_timestamp="2024-01-01T00:00:00Z",
        )
        assert metadata.retry_count == 0
        assert metadata.replayed is False
        assert metadata.replay_count == 0
        assert metadata.retry_timestamps == []
        assert metadata.retry_errors == []

    def test_metadata_with_optional_fields(self):
        """Test metadata with optional fields"""
        metadata = DLQMessageMetadata(
            original_subject="sahool.test",
            failure_reason="Error",
            failure_timestamp="2024-01-01T00:00:00Z",
            original_event_id="evt-123",
            correlation_id="corr-456",
            error_type="ValueError",
            error_traceback="Traceback...",
            consumer_service="test-service",
            consumer_version="1.0.0",
            handler_function="handle_event",
        )
        assert metadata.original_event_id == "evt-123"
        assert metadata.correlation_id == "corr-456"
        assert metadata.error_type == "ValueError"
        assert metadata.consumer_service == "test-service"


class TestStreamConfig:
    """Test StreamConfig model"""

    def test_stream_config_creation(self):
        """Test creating stream config"""
        config = StreamConfig(
            name="TEST_STREAM",
            subjects=["test.>"],
        )
        assert config.name == "TEST_STREAM"
        assert config.subjects == ["test.>"]
        assert config.retention == "limits"
        assert config.storage == "file"
        assert config.replicas == 1

    def test_stream_config_custom(self):
        """Test stream config with custom values"""
        config = StreamConfig(
            name="CUSTOM_STREAM",
            subjects=["custom.>"],
            retention="workqueue",
            max_age_seconds=86400,
            max_messages=10000,
            storage="memory",
            replicas=3,
        )
        assert config.name == "CUSTOM_STREAM"
        assert config.retention == "workqueue"
        assert config.max_age_seconds == 86400
        assert config.max_messages == 10000
        assert config.storage == "memory"
        assert config.replicas == 3


class TestDLQHelperFunctions:
    """Test DLQ helper functions"""

    def test_get_dlq_stream_config(self):
        """Test get_dlq_stream_config function"""
        dlq_config = DLQConfig(
            dlq_stream_name="MY_DLQ",
            dlq_subject_prefix="my.dlq",
            dlq_max_age_days=7,
            dlq_max_messages=5000,
        )
        stream_config = get_dlq_stream_config(dlq_config)

        assert stream_config.name == "MY_DLQ"
        assert stream_config.subjects == ["my.dlq.>"]
        assert stream_config.max_age_seconds == 7 * 86400
        assert stream_config.max_messages == 5000

    def test_should_retry_true(self):
        """Test should_retry returns True when attempts remaining"""
        config = DLQConfig(max_retry_attempts=3)

        assert should_retry(1, config) is True
        assert should_retry(2, config) is True

    def test_should_retry_false(self):
        """Test should_retry returns False when max attempts reached"""
        config = DLQConfig(max_retry_attempts=3)

        assert should_retry(3, config) is False
        assert should_retry(4, config) is False

    def test_is_retriable_error_transient(self):
        """Test is_retriable_error for transient errors"""
        # Transient errors should be retriable
        assert is_retriable_error(ConnectionError("Network error")) is True
        assert is_retriable_error(TimeoutError("Timeout")) is True
        assert is_retriable_error(Exception("Generic error")) is True

    def test_is_retriable_error_permanent(self):
        """Test is_retriable_error for permanent errors"""
        # Permanent errors should not be retriable
        assert is_retriable_error(ValueError("Invalid value")) is False
        assert is_retriable_error(KeyError("missing_key")) is False
        assert is_retriable_error(TypeError("Wrong type")) is False


# ═══════════════════════════════════════════════════════════════════════════
# Subscriber Config Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestSubscriberConfig:
    """Test SubscriberConfig model"""

    def test_default_config(self):
        """Test default subscriber configuration"""
        with patch.dict(os.environ, {"NATS_URL": ""}, clear=False):
            config = SubscriberConfig()
            assert config.enable_jetstream is True
            assert config.max_reconnect_attempts == 60
            assert config.connect_timeout == 10

    @patch.dict(
        os.environ,
        {"NATS_URL": "nats://test-server:4222", "SERVICE_NAME": "test-subscriber"},
    )
    def test_config_from_env(self):
        """Test configuration from environment variables"""
        config = SubscriberConfig()
        assert "nats://test-server:4222" in config.servers
        assert config.name == "test-subscriber"

    def test_custom_config(self):
        """Test custom subscriber configuration"""
        config = SubscriberConfig(
            servers=["nats://server1:4222", "nats://server2:4222"],
            name="custom-subscriber",
            enable_jetstream=False,
            max_reconnect_attempts=30,
        )
        assert len(config.servers) == 2
        assert config.name == "custom-subscriber"
        assert config.enable_jetstream is False
        assert config.max_reconnect_attempts == 30


# ═══════════════════════════════════════════════════════════════════════════
# Event Subscriber Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestEventSubscriber:
    """Test EventSubscriber class"""

    @pytest.fixture
    def config(self):
        """Create test subscriber config"""
        return SubscriberConfig(
            servers=["nats://localhost:4222"],
            name="test-subscriber",
            enable_jetstream=True,
        )

    @pytest.fixture
    def subscriber(self, config):
        """Create EventSubscriber instance"""
        return EventSubscriber(
            config=config, service_name="test-service", service_version="1.0.0"
        )

    def test_subscriber_creation(self, subscriber):
        """Test creating subscriber"""
        assert subscriber.service_name == "test-service"
        assert subscriber.service_version == "1.0.0"
        assert subscriber.is_connected is False

    def test_subscriber_stats(self, subscriber):
        """Test getting subscriber stats"""
        stats = subscriber.stats

        assert "connected" in stats
        assert "message_count" in stats
        assert "error_count" in stats
        assert stats["service_name"] == "test-service"

    @pytest.mark.asyncio
    @patch("shared.events.subscriber._nats_available", True)
    @patch("nats.connect")
    async def test_subscriber_connect_success(self, mock_connect, subscriber):
        """Test successful connection to NATS"""
        mock_nc = AsyncMock()
        mock_nc.jetstream = MagicMock()
        mock_connect.return_value = mock_nc

        result = await subscriber.connect()

        assert result is True
        assert subscriber.is_connected is True
        mock_connect.assert_called_once()

    @pytest.mark.asyncio
    @patch("shared.events.subscriber._nats_available", False)
    async def test_subscriber_connect_no_nats(self, subscriber):
        """Test connection fails when NATS not available"""
        result = await subscriber.connect()

        assert result is False
        assert subscriber.is_connected is False

    @pytest.mark.asyncio
    @patch("shared.events.subscriber._nats_available", True)
    @patch("nats.connect")
    async def test_subscriber_connect_failure(self, mock_connect, subscriber):
        """Test connection failure"""
        mock_connect.side_effect = Exception("Connection failed")

        result = await subscriber.connect()

        assert result is False
        assert subscriber.is_connected is False

    @pytest.mark.asyncio
    @patch("shared.events.subscriber._nats_available", True)
    @patch("nats.connect")
    async def test_subscriber_close(self, mock_connect, subscriber):
        """Test closing subscriber connection"""
        mock_nc = AsyncMock()
        mock_nc.jetstream = MagicMock()
        mock_connect.return_value = mock_nc

        await subscriber.connect()
        await subscriber.close()

        assert subscriber.is_connected is False
        mock_nc.drain.assert_called_once()
        mock_nc.close.assert_called_once()

    def test_dlq_config_separate(self):
        """Test DLQ config can be created separately"""
        dlq_config = DLQConfig(
            max_retry_attempts=5,
            initial_retry_delay=0.5,
        )
        # DLQ config is used separately with subscriber for retry logic
        assert dlq_config.max_retry_attempts == 5
        assert dlq_config.initial_retry_delay == 0.5
        assert dlq_config.get_retry_delay(1) == 0.5


# ═══════════════════════════════════════════════════════════════════════════
# Subscriber Context Manager Tests
# ═══════════════════════════════════════════════════════════════════════════


class TestSubscriberContextManager:
    """Test EventSubscriber as context manager"""

    @pytest.mark.asyncio
    @patch("shared.events.subscriber._nats_available", True)
    @patch("nats.connect")
    async def test_context_manager(self, mock_connect):
        """Test using subscriber as async context manager"""
        mock_nc = AsyncMock()
        mock_nc.jetstream = MagicMock()
        mock_connect.return_value = mock_nc

        config = SubscriberConfig(servers=["nats://localhost:4222"])

        async with EventSubscriber(config=config) as subscriber:
            assert subscriber.is_connected is True

        assert subscriber.is_connected is False
