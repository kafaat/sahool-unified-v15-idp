"""
Tests for FieldOps Client - HTTP client for field-management-service
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import httpx

from src.fieldops_client import FieldOpsClient, get_fieldops_client


class TestFieldOpsClientInit:
    """Tests for FieldOpsClient initialization"""

    def test_default_base_url(self):
        """Test default URL uses field-management-service"""
        client = FieldOpsClient()
        assert "field-management-service" in client.base_url

    def test_custom_base_url(self):
        """Test custom base URL"""
        client = FieldOpsClient(base_url="http://custom:9999")
        assert client.base_url == "http://custom:9999"

    def test_initial_client_is_none(self):
        """Test _client starts as None"""
        client = FieldOpsClient()
        assert client._client is None


class TestFieldOpsClientGetClient:
    """Tests for lazy HTTP client creation"""

    @pytest.mark.asyncio
    async def test_get_client_creates_client(self):
        """Test _get_client creates httpx.AsyncClient on first call"""
        client = FieldOpsClient(base_url="http://test:3000")
        http_client = await client._get_client()
        assert http_client is not None
        assert client._client is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_get_client_reuses_client(self):
        """Test _get_client returns same instance on subsequent calls"""
        client = FieldOpsClient(base_url="http://test:3000")
        c1 = await client._get_client()
        c2 = await client._get_client()
        assert c1 is c2
        await client.close()


class TestFieldOpsClientClose:
    """Tests for client cleanup"""

    @pytest.mark.asyncio
    async def test_close_with_no_client(self):
        """Test close when no client has been created"""
        client = FieldOpsClient()
        await client.close()  # Should not raise
        assert client._client is None

    @pytest.mark.asyncio
    async def test_close_with_active_client(self):
        """Test close properly cleans up the HTTP client"""
        client = FieldOpsClient(base_url="http://test:3000")
        await client._get_client()  # Create client
        assert client._client is not None
        await client.close()
        assert client._client is None


class TestFieldOpsClientCreateTask:
    """Tests for task creation"""

    @pytest.mark.asyncio
    async def test_create_task_success(self):
        """Test successful task creation returns response data"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "task-1", "status": "open"}

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.create_task(
            tenant_id="tenant-1",
            field_id="field-1",
            title="Test Task",
            description="Test Description",
            priority="high",
        )

        assert result == {"id": "task-1", "status": "open"}
        mock_http.post.assert_called_once()
        call_kwargs = mock_http.post.call_args
        payload = call_kwargs.kwargs["json"] if "json" in call_kwargs.kwargs else call_kwargs[1]["json"]
        assert payload["tenant_id"] == "tenant-1"
        assert payload["field_id"] == "field-1"
        assert payload["priority"] == "high"
        assert payload["source"] == "agro_rules"
        assert payload["status"] == "open"

    @pytest.mark.asyncio
    async def test_create_task_with_correlation_id(self):
        """Test task creation includes correlation_id when provided"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task-2"}

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        await client.create_task(
            tenant_id="t1",
            field_id="f1",
            title="T",
            description="D",
            priority="low",
            correlation_id="corr-123",
        )

        payload = mock_http.post.call_args.kwargs["json"]
        assert payload["correlation_id"] == "corr-123"

    @pytest.mark.asyncio
    async def test_create_task_with_metadata(self):
        """Test task creation includes metadata when provided"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "task-3"}

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        await client.create_task(
            tenant_id="t1",
            field_id="f1",
            title="T",
            description="D",
            priority="medium",
            metadata={"key": "value"},
        )

        payload = mock_http.post.call_args.kwargs["json"]
        assert payload["metadata"] == {"key": "value"}

    @pytest.mark.asyncio
    async def test_create_task_without_optional_fields(self):
        """Test task creation omits optional fields when not provided"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "task-4"}

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        await client.create_task(
            tenant_id="t1",
            field_id="f1",
            title="T",
            description="D",
            priority="low",
        )

        payload = mock_http.post.call_args.kwargs["json"]
        assert "correlation_id" not in payload
        assert "metadata" not in payload

    @pytest.mark.asyncio
    async def test_create_task_non_success_status(self):
        """Test task creation handles non-success HTTP status"""
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.text = "Validation error"

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.create_task(
            tenant_id="t1",
            field_id="f1",
            title="T",
            description="D",
            priority="low",
        )

        assert result["status"] == "error"
        assert result["code"] == 422

    @pytest.mark.asyncio
    async def test_create_task_connection_error(self):
        """Test task creation handles connection errors"""
        mock_http = AsyncMock()
        mock_http.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.create_task(
            tenant_id="t1",
            field_id="f1",
            title="T",
            description="D",
            priority="low",
        )

        assert result["status"] == "connection_error"

    @pytest.mark.asyncio
    async def test_create_task_generic_error(self):
        """Test task creation handles generic exceptions"""
        mock_http = AsyncMock()
        mock_http.post = AsyncMock(side_effect=RuntimeError("unexpected"))

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.create_task(
            tenant_id="t1",
            field_id="f1",
            title="T",
            description="D",
            priority="low",
        )

        assert result["status"] == "error"
        assert "unexpected" in result["error"]

    @pytest.mark.asyncio
    async def test_create_task_custom_params(self):
        """Test task creation with custom task_type, due_hours, source"""
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "task-5"}

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        await client.create_task(
            tenant_id="t1",
            field_id="f1",
            title="T",
            description="D",
            priority="urgent",
            task_type="emergency",
            due_hours=2,
            source="iot_rules",
        )

        payload = mock_http.post.call_args.kwargs["json"]
        assert payload["task_type"] == "emergency"
        assert payload["source"] == "iot_rules"


class TestFieldOpsClientUpdateTaskStatus:
    """Tests for task status updates"""

    @pytest.mark.asyncio
    async def test_update_task_status_success(self):
        """Test successful status update"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "task-1", "status": "completed"}

        mock_http = AsyncMock()
        mock_http.patch = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.update_task_status("task-1", "completed")

        assert result["status"] == "completed"
        mock_http.patch.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_task_status_error(self):
        """Test status update handles exceptions"""
        mock_http = AsyncMock()
        mock_http.patch = AsyncMock(side_effect=RuntimeError("fail"))

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.update_task_status("task-1", "completed")
        assert result["status"] == "error"


class TestFieldOpsClientGetTask:
    """Tests for getting a task"""

    @pytest.mark.asyncio
    async def test_get_task_success(self):
        """Test successful task retrieval"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task-1", "title": "Test"}

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.get_task("task-1")
        assert result is not None
        assert result["id"] == "task-1"

    @pytest.mark.asyncio
    async def test_get_task_not_found(self):
        """Test task not found returns None"""
        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.get_task("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_task_error(self):
        """Test get task handles exceptions"""
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=RuntimeError("fail"))

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.get_task("task-1")
        assert result is None


class TestFieldOpsClientListTasks:
    """Tests for listing tasks"""

    @pytest.mark.asyncio
    async def test_list_tasks_with_data_key(self):
        """Test list tasks with 'data' response format"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "t1"}, {"id": "t2"}]}

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.list_tasks(tenant_id="tenant-1")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_list_tasks_with_tasks_key(self):
        """Test list tasks with 'tasks' response format"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tasks": [{"id": "t1"}]}

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.list_tasks()
        assert len(result) == 1

    @pytest.mark.asyncio
    async def test_list_tasks_with_filters(self):
        """Test list tasks passes filter params"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": []}

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        await client.list_tasks(tenant_id="t1", field_id="f1", status="open", limit=10)

        call_kwargs = mock_http.get.call_args
        params = call_kwargs.kwargs.get("params") or call_kwargs[1].get("params", {})
        assert params["tenant_id"] == "t1"
        assert params["field_id"] == "f1"
        assert params["status"] == "open"
        assert params["limit"] == 10

    @pytest.mark.asyncio
    async def test_list_tasks_non_200(self):
        """Test list tasks returns empty on non-200 status"""
        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.list_tasks()
        assert result == []

    @pytest.mark.asyncio
    async def test_list_tasks_error(self):
        """Test list tasks handles exceptions"""
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=RuntimeError("fail"))

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.list_tasks()
        assert result == []


class TestFieldOpsClientHealthCheck:
    """Tests for health check"""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """Test health check returns True when service is up"""
        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self):
        """Test health check returns False on non-200"""
        mock_response = MagicMock()
        mock_response.status_code = 503

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_connection_error(self):
        """Test health check returns False on connection error"""
        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=Exception("conn refused"))

        client = FieldOpsClient(base_url="http://test:3000")
        client._client = mock_http

        result = await client.health_check()
        assert result is False


class TestGetFieldOpsClientSingleton:
    """Tests for the singleton factory"""

    def test_get_fieldops_client_returns_instance(self):
        """Test factory returns a FieldOpsClient"""
        import src.fieldops_client as mod

        mod._client = None  # Reset singleton
        client = get_fieldops_client()
        assert isinstance(client, FieldOpsClient)
        mod._client = None  # Cleanup

    def test_get_fieldops_client_is_singleton(self):
        """Test factory returns same instance"""
        import src.fieldops_client as mod

        mod._client = None
        c1 = get_fieldops_client()
        c2 = get_fieldops_client()
        assert c1 is c2
        mod._client = None
