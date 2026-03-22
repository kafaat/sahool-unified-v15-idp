"""
Unit tests for NATS publisher module.
اختبارات وحدة ناشر NATS
"""

import sys
from unittest.mock import AsyncMock, MagicMock, patch

import pytest


# We need to mock the shared.events.publisher import before importing the module
@pytest.fixture(autouse=True)
def mock_shared_events():
    """Mock the shared events module that nats_publisher imports"""
    mock_publisher_class = MagicMock()
    mock_config_class = MagicMock()
    mock_module = MagicMock()
    mock_module.EventPublisher = mock_publisher_class
    mock_module.PublisherConfig = mock_config_class

    with patch.dict(
        "sys.modules",
        {
            "shared": MagicMock(),
            "shared.events": MagicMock(),
            "shared.events.publisher": mock_module,
        },
    ):
        yield mock_publisher_class, mock_config_class


class TestNatsPublisher:
    """Tests for NatsPublisher class"""

    def test_init(self, mock_shared_events):
        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher()
        assert publisher.connected is False
        assert publisher._service_name == "task-service"

    def test_init_custom_name(self, mock_shared_events):
        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher(service_name="custom-service")
        assert publisher._service_name == "custom-service"

    def test_is_connected_false_initially(self, mock_shared_events):
        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher()
        assert publisher.is_connected is False

    @pytest.mark.asyncio
    async def test_connect_success(self, mock_shared_events):
        mock_publisher_class, mock_config_class = mock_shared_events
        mock_ep = AsyncMock()
        mock_ep.connect.return_value = True
        mock_ep.is_connected = True
        mock_publisher_class.return_value = mock_ep

        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher()
        result = await publisher.connect("nats://localhost:4222")
        assert result is True
        assert publisher.connected is True

    @pytest.mark.asyncio
    async def test_connect_failure(self, mock_shared_events):
        mock_publisher_class, mock_config_class = mock_shared_events
        mock_ep = AsyncMock()
        mock_ep.connect.side_effect = Exception("connection refused")
        mock_publisher_class.return_value = mock_ep

        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher()
        result = await publisher.connect("nats://bad:4222")
        assert result is False
        assert publisher.connected is False

    @pytest.mark.asyncio
    async def test_disconnect(self, mock_shared_events):
        mock_publisher_class, _ = mock_shared_events
        mock_ep = AsyncMock()
        mock_ep.connect.return_value = True
        mock_ep.is_connected = True
        mock_publisher_class.return_value = mock_ep

        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher()
        await publisher.connect("nats://localhost:4222")
        await publisher.disconnect()
        assert publisher.connected is False

    @pytest.mark.asyncio
    async def test_publish_event_not_connected(self, mock_shared_events):
        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher()
        result = await publisher.publish_event(
            subject="sahool.task.created",
            event_type="task.created",
            payload={"taskId": "t1"},
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_publish_event_success(self, mock_shared_events):
        mock_publisher_class, _ = mock_shared_events
        mock_ep = AsyncMock()
        mock_ep.connect.return_value = True
        mock_ep.is_connected = True
        mock_ep.publish_json.return_value = True
        mock_publisher_class.return_value = mock_ep

        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher()
        await publisher.connect("nats://localhost:4222")

        result = await publisher.publish_event(
            subject="sahool.task.created",
            event_type="task.created",
            payload={"taskId": "task_001", "tenantId": "t1"},
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_publish_event_adds_sahool_prefix(self, mock_shared_events):
        mock_publisher_class, _ = mock_shared_events
        mock_ep = AsyncMock()
        mock_ep.connect.return_value = True
        mock_ep.is_connected = True
        mock_ep.publish_json.return_value = True
        mock_publisher_class.return_value = mock_ep

        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher()
        await publisher.connect("nats://localhost:4222")

        await publisher.publish_event(
            subject="task.created",  # Without sahool. prefix
            event_type="task.created",
            payload={"taskId": "t1"},
        )

        # Verify the subject was prefixed
        call_args = mock_ep.publish_json.call_args
        assert call_args[0][0] == "sahool.task.created"

    @pytest.mark.asyncio
    async def test_publish_event_error(self, mock_shared_events):
        mock_publisher_class, _ = mock_shared_events
        mock_ep = AsyncMock()
        mock_ep.connect.return_value = True
        mock_ep.is_connected = True
        mock_ep.publish_json.side_effect = Exception("publish failed")
        mock_publisher_class.return_value = mock_ep

        from src.events.nats_publisher import NatsPublisher

        publisher = NatsPublisher()
        await publisher.connect("nats://localhost:4222")

        result = await publisher.publish_event(
            subject="sahool.task.created",
            event_type="task.created",
            payload={"taskId": "t1"},
        )
        assert result is False


class TestGlobalPublisher:
    """Tests for global publisher functions"""

    def test_get_set_publisher(self, mock_shared_events):
        # Initially None
        import src.events.nats_publisher as module
        from src.events.nats_publisher import NatsPublisher, get_publisher, set_publisher

        old = module._publisher
        module._publisher = None

        assert get_publisher() is None

        pub = NatsPublisher()
        set_publisher(pub)
        assert get_publisher() is pub

        # Restore
        module._publisher = old


class TestEventPublishFunctions:
    """Tests for individual event publish functions"""

    @pytest.mark.asyncio
    async def test_publish_task_created_no_publisher(self, mock_shared_events):
        import src.events.nats_publisher as module
        from src.events.nats_publisher import publish_task_created

        old = module._publisher
        module._publisher = None

        result = await publish_task_created(
            task_id="t1",
            tenant_id="tenant_1",
            task_type="irrigation",
            priority="high",
        )
        assert result is False
        module._publisher = old

    @pytest.mark.asyncio
    async def test_publish_task_updated_no_publisher(self, mock_shared_events):
        import src.events.nats_publisher as module
        from src.events.nats_publisher import publish_task_updated

        old = module._publisher
        module._publisher = None

        result = await publish_task_updated(
            task_id="t1",
            tenant_id="tenant_1",
            changes={"status": {"old": "pending", "new": "in_progress"}},
        )
        assert result is False
        module._publisher = old

    @pytest.mark.asyncio
    async def test_publish_task_assigned_no_publisher(self, mock_shared_events):
        import src.events.nats_publisher as module
        from src.events.nats_publisher import publish_task_assigned

        old = module._publisher
        module._publisher = None

        result = await publish_task_assigned(
            task_id="t1",
            tenant_id="tenant_1",
            assigned_to="user_1",
        )
        assert result is False
        module._publisher = old

    @pytest.mark.asyncio
    async def test_publish_task_started_no_publisher(self, mock_shared_events):
        import src.events.nats_publisher as module
        from src.events.nats_publisher import publish_task_started

        old = module._publisher
        module._publisher = None

        result = await publish_task_started(
            task_id="t1",
            tenant_id="tenant_1",
            started_by="user_1",
        )
        assert result is False
        module._publisher = old

    @pytest.mark.asyncio
    async def test_publish_task_completed_no_publisher(self, mock_shared_events):
        import src.events.nats_publisher as module
        from src.events.nats_publisher import publish_task_completed

        old = module._publisher
        module._publisher = None

        result = await publish_task_completed(
            task_id="t1",
            tenant_id="tenant_1",
            completed_by="user_1",
        )
        assert result is False
        module._publisher = old

    @pytest.mark.asyncio
    async def test_publish_task_cancelled_no_publisher(self, mock_shared_events):
        import src.events.nats_publisher as module
        from src.events.nats_publisher import publish_task_cancelled

        old = module._publisher
        module._publisher = None

        result = await publish_task_cancelled(
            task_id="t1",
            tenant_id="tenant_1",
            cancelled_by="user_1",
            reason="Weather",
        )
        assert result is False
        module._publisher = old
