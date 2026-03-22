"""
Tests for FieldOps Client
"""

import pytest

try:
    from unittest.mock import AsyncMock, MagicMock, patch

    import httpx

    from src.fieldops_client import FieldOpsClient, get_fieldops_client
except ImportError:
    pytest.skip("agro-rules dependencies not installed", allow_module_level=True)


class TestFieldOpsClientInit:
    """Test FieldOpsClient initialization"""

    def test_default_url(self):
        """Test default base URL"""
        client = FieldOpsClient()
        assert client.base_url == "http://field-management-service:3000"

    def test_custom_url(self):
        """Test custom base URL"""
        client = FieldOpsClient("http://localhost:3000")
        assert client.base_url == "http://localhost:3000"

    def test_client_initially_none(self):
        """Test HTTP client is initially None"""
        client = FieldOpsClient()
        assert client._client is None


class TestFieldOpsClientGetClient:
    """Test HTTP client creation"""

    @pytest.mark.asyncio
    async def test_get_client_creates_client(self):
        """Test _get_client creates httpx client"""
        client = FieldOpsClient("http://localhost:3000")
        http_client = await client._get_client()

        assert http_client is not None
        assert client._client is not None
        await client.close()

    @pytest.mark.asyncio
    async def test_get_client_reuses_client(self):
        """Test _get_client returns same client on second call"""
        client = FieldOpsClient("http://localhost:3000")
        http_client1 = await client._get_client()
        http_client2 = await client._get_client()

        assert http_client1 is http_client2
        await client.close()


class TestFieldOpsClientClose:
    """Test client close"""

    @pytest.mark.asyncio
    async def test_close_resets_client(self):
        """Test close resets the internal client"""
        client = FieldOpsClient("http://localhost:3000")
        await client._get_client()
        assert client._client is not None

        await client.close()
        assert client._client is None

    @pytest.mark.asyncio
    async def test_close_when_no_client(self):
        """Test close is safe when no client exists"""
        client = FieldOpsClient()
        await client.close()  # Should not raise


class TestFieldOpsClientCreateTask:
    """Test create_task method"""

    @pytest.mark.asyncio
    async def test_create_task_success(self):
        """Test successful task creation"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "task-123", "status": "open"}

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.create_task(
            tenant_id="tenant-1",
            field_id="field-1",
            title="Test task",
            description="Test description",
            priority="high",
            correlation_id="corr-1",
            task_type="irrigation",
            due_hours=6,
            source="agro_rules",
            metadata={"key": "value"},
        )

        assert result == {"id": "task-123", "status": "open"}
        mock_http.post.assert_called_once()
        call_args = mock_http.post.call_args
        payload = call_args.kwargs["json"]
        assert payload["tenant_id"] == "tenant-1"
        assert payload["field_id"] == "field-1"
        assert payload["correlation_id"] == "corr-1"
        assert payload["metadata"] == {"key": "value"}
        assert payload["priority"] == "high"
        assert payload["source"] == "agro_rules"
        assert payload["status"] == "open"

    @pytest.mark.asyncio
    async def test_create_task_without_optional_params(self):
        """Test task creation without optional params"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task-456"}

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.create_task(
            tenant_id="tenant-1",
            field_id="field-1",
            title="Test",
            description="Desc",
            priority="low",
        )

        assert result == {"id": "task-456"}
        call_args = mock_http.post.call_args
        payload = call_args.kwargs["json"]
        assert "correlation_id" not in payload
        assert "metadata" not in payload

    @pytest.mark.asyncio
    async def test_create_task_error_status(self):
        """Test task creation with error response"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.create_task(
            tenant_id="t",
            field_id="f",
            title="T",
            description="D",
            priority="low",
        )

        assert result["status"] == "error"
        assert result["code"] == 500

    @pytest.mark.asyncio
    async def test_create_task_connection_error(self):
        """Test task creation with connection error"""
        client = FieldOpsClient("http://localhost:3000")

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(side_effect=httpx.ConnectError("Connection refused"))
        client._client = mock_http

        result = await client.create_task(
            tenant_id="t",
            field_id="f",
            title="T",
            description="D",
            priority="low",
        )

        assert result["status"] == "connection_error"

    @pytest.mark.asyncio
    async def test_create_task_generic_exception(self):
        """Test task creation with generic exception"""
        client = FieldOpsClient("http://localhost:3000")

        mock_http = AsyncMock()
        mock_http.post = AsyncMock(side_effect=Exception("Unexpected error"))
        client._client = mock_http

        result = await client.create_task(
            tenant_id="t",
            field_id="f",
            title="T",
            description="D",
            priority="low",
        )

        assert result["status"] == "error"

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


class TestFieldOpsClientUpdateTask:
    """Test update_task_status method"""

    @pytest.mark.asyncio
    async def test_update_task_success(self):
        """Test successful task update"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.json.return_value = {"id": "task-1", "status": "completed"}

        mock_http = AsyncMock()
        mock_http.patch = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.update_task_status("task-1", "completed")
        assert result["status"] == "completed"

    @pytest.mark.asyncio
    async def test_update_task_error(self):
        """Test task update with error"""
        client = FieldOpsClient("http://localhost:3000")

        mock_http = AsyncMock()
        mock_http.patch = AsyncMock(side_effect=Exception("fail"))
        client._client = mock_http

        result = await client.update_task_status("task-1", "completed")
        assert result["status"] == "error"


class TestFieldOpsClientGetTask:
    """Test get_task method"""

    @pytest.mark.asyncio
    async def test_get_task_success(self):
        """Test successful task retrieval"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "task-1", "title": "Test"}

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.get_task("task-1")
        assert result == {"id": "task-1", "title": "Test"}

    @pytest.mark.asyncio
    async def test_get_task_not_found(self):
        """Test task not found returns None"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 404

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.get_task("task-999")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_task_error(self):
        """Test get task with error returns None"""
        client = FieldOpsClient("http://localhost:3000")

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=Exception("fail"))
        client._client = mock_http

        result = await client.get_task("task-1")
        assert result is None


class TestFieldOpsClientListTasks:
    """Test list_tasks method"""

    @pytest.mark.asyncio
    async def test_list_tasks_success(self):
        """Test successful task listing"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"data": [{"id": "t1"}, {"id": "t2"}]}

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.list_tasks(tenant_id="t1", field_id="f1", status="open")
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_list_tasks_old_format(self):
        """Test list tasks with old response format"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"tasks": [{"id": "t1"}]}

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)
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
    async def test_list_tasks_error_status(self):
        """Test list tasks with error status returns empty"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.list_tasks()
        assert result == []

    @pytest.mark.asyncio
    async def test_list_tasks_exception(self):
        """Test list tasks with exception returns empty"""
        client = FieldOpsClient("http://localhost:3000")

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=Exception("fail"))
        client._client = mock_http

        result = await client.list_tasks()
        assert result == []


class TestFieldOpsClientHealthCheck:
    """Test health_check method"""

    @pytest.mark.asyncio
    async def test_health_check_healthy(self):
        """Test healthy service"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 200

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.health_check()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self):
        """Test unhealthy service"""
        client = FieldOpsClient("http://localhost:3000")

        mock_response = MagicMock()
        mock_response.status_code = 503

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(return_value=mock_response)
        client._client = mock_http

        result = await client.health_check()
        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_exception(self):
        """Test health check with connection error"""
        client = FieldOpsClient("http://localhost:3000")

        mock_http = AsyncMock()
        mock_http.get = AsyncMock(side_effect=Exception("fail"))
        client._client = mock_http

        result = await client.health_check()
        assert result is False


class TestGetFieldOpsClientSingleton:
    """Test get_fieldops_client function"""

    def test_returns_client_instance(self):
        """Test singleton returns a FieldOpsClient"""
        import src.fieldops_client as module

        module._client = None  # Reset singleton
        client = get_fieldops_client()
        assert isinstance(client, FieldOpsClient)

    def test_returns_same_instance(self):
        """Test singleton returns same instance"""
        import src.fieldops_client as module

        module._client = None  # Reset singleton
        client1 = get_fieldops_client()
        client2 = get_fieldops_client()
        assert client1 is client2
        module._client = None  # Cleanup
