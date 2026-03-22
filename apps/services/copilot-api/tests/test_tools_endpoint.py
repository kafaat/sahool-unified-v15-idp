"""
Tests for Tool Execution Endpoints helpers (api/v1/tools.py)
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

pytestmark = [pytest.mark.unit]


class TestExecuteTool:
    @pytest.mark.asyncio
    async def test_rag_search_tool(self):
        from src.api.v1.tools import _execute_tool
        from src.rag.service import RAGDocument, SearchResult

        mock_rag = MagicMock()
        mock_rag.search = AsyncMock(
            return_value=[
                SearchResult(
                    document=RAGDocument(id="d1", text="Result text here", metadata={}),
                    score=0.9,
                )
            ]
        )

        with patch("src.api.v1.tools.get_rag_service", return_value=mock_rag):
            result = await _execute_tool("rag.search", {"query": "test", "k": 3})
            assert len(result) == 1
            assert result[0]["id"] == "d1"
            assert result[0]["score"] == 0.9

    @pytest.mark.asyncio
    async def test_rag_add_tool(self):
        from src.api.v1.tools import _execute_tool
        from src.rag.service import RAGDocument

        mock_rag = MagicMock()
        mock_rag.add_document = AsyncMock(
            return_value=RAGDocument(id="new-1", text="added", metadata={})
        )

        with patch("src.api.v1.tools.get_rag_service", return_value=mock_rag):
            result = await _execute_tool("rag.add", {"text": "new doc"})
            assert result["id"] == "new-1"
            assert result["created"] is True

    @pytest.mark.asyncio
    async def test_rag_delete_tool(self):
        from src.api.v1.tools import _execute_tool

        mock_rag = MagicMock()
        mock_rag.delete_document = AsyncMock(return_value=True)

        with patch("src.api.v1.tools.get_rag_service", return_value=mock_rag):
            result = await _execute_tool("rag.delete", {"id": "d1"})
            assert result["deleted"] is True

    @pytest.mark.asyncio
    async def test_rag_list_tool(self):
        from src.api.v1.tools import _execute_tool
        from src.rag.service import RAGDocument

        doc = RAGDocument(id="d1", text="test", metadata={})
        mock_rag = MagicMock()
        mock_rag.list_documents = AsyncMock(return_value=[doc])

        with patch("src.api.v1.tools.get_rag_service", return_value=mock_rag):
            result = await _execute_tool("rag.list", {})
            assert len(result) == 1

    @pytest.mark.asyncio
    async def test_unknown_tool_raises(self):
        from src.api.v1.tools import _execute_tool

        with pytest.raises(ValueError, match="Unknown tool"):
            await _execute_tool("unknown.tool", {})

    @pytest.mark.asyncio
    async def test_deploy_plan_tool(self):
        from src.api.v1.tools import _execute_tool

        result = await _execute_tool("deploy.plan", {})
        assert "plan" in result
        assert "steps" in result
        assert result["requires_approval"] is True

    @pytest.mark.asyncio
    async def test_deploy_status_tool(self):
        from src.api.v1.tools import _execute_tool

        result = await _execute_tool("deploy.status", {"environment": "staging"})
        assert result["environment"] == "staging"
        assert result["status"] == "healthy"

    @pytest.mark.asyncio
    async def test_deploy_validate_tool(self):
        from src.api.v1.tools import _execute_tool

        result = await _execute_tool("deploy.validate", {})
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_deploy_unknown_action(self):
        from src.api.v1.tools import _execute_tool

        result = await _execute_tool("deploy.unknown", {})
        assert "error" in result

    @pytest.mark.asyncio
    async def test_code_tool_requires_http_client(self):
        from src.api.v1.tools import _execute_tool

        with pytest.raises(ValueError, match="http_client is required"):
            await _execute_tool("code.analyze", {"path": "."}, http_client=None)

    @pytest.mark.asyncio
    async def test_field_tool_requires_http_client(self):
        from src.api.v1.tools import _execute_tool

        with pytest.raises(ValueError, match="http_client is required"):
            await _execute_tool("field.list", {}, http_client=None)

    @pytest.mark.asyncio
    async def test_weather_tool_requires_http_client(self):
        from src.api.v1.tools import _execute_tool

        with pytest.raises(ValueError, match="http_client is required"):
            await _execute_tool("weather.forecast", {}, http_client=None)


class TestProxyToCodeAgent:
    @pytest.mark.asyncio
    async def test_unknown_action_returns_error(self):
        from src.api.v1.tools import _proxy_to_code_agent

        mock_client = AsyncMock()
        result = await _proxy_to_code_agent("code.unknown_action", {}, mock_client)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_successful_analyze(self):
        from src.api.v1.tools import _proxy_to_code_agent

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"issues": []}

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        result = await _proxy_to_code_agent("code.analyze", {"path": "."}, mock_client)
        assert result == {"issues": []}

    @pytest.mark.asyncio
    async def test_service_error(self):
        from src.api.v1.tools import _proxy_to_code_agent

        mock_response = MagicMock()
        mock_response.status_code = 500

        mock_client = AsyncMock()
        mock_client.post.return_value = mock_response

        result = await _proxy_to_code_agent("code.analyze", {}, mock_client)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_connection_failure(self):
        from src.api.v1.tools import _proxy_to_code_agent

        mock_client = AsyncMock()
        mock_client.post.side_effect = Exception("connection refused")

        result = await _proxy_to_code_agent("code.fix", {}, mock_client)
        assert "error" in result
        assert "unavailable" in result["error"]


class TestProxyToFieldService:
    @pytest.mark.asyncio
    async def test_unknown_action(self):
        from src.api.v1.tools import _proxy_to_field_service

        mock_client = AsyncMock()
        result = await _proxy_to_field_service("field.unknownaction", {}, mock_client)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_list_action_uses_get(self):
        from src.api.v1.tools import _proxy_to_field_service

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"fields": []}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        result = await _proxy_to_field_service("field.list", {}, mock_client)
        mock_client.get.assert_called_once()
        assert result == {"fields": []}

    @pytest.mark.asyncio
    async def test_get_action_uses_get_with_id(self):
        from src.api.v1.tools import _proxy_to_field_service

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "f1"}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        result = await _proxy_to_field_service("field.get", {"id": "f1"}, mock_client)
        assert result == {"id": "f1"}


class TestProxyToWeatherService:
    @pytest.mark.asyncio
    async def test_unknown_action(self):
        from src.api.v1.tools import _proxy_to_weather_service

        mock_client = AsyncMock()
        result = await _proxy_to_weather_service("weather.unknownaction", {}, mock_client)
        assert "error" in result

    @pytest.mark.asyncio
    async def test_forecast_action(self):
        from src.api.v1.tools import _proxy_to_weather_service

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"temp": 28}

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        result = await _proxy_to_weather_service("weather.forecast", {"lat": 24.7, "lon": 46.7}, mock_client)
        assert result == {"temp": 28}

    @pytest.mark.asyncio
    async def test_connection_failure(self):
        from src.api.v1.tools import _proxy_to_weather_service

        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("timeout")

        result = await _proxy_to_weather_service("weather.current", {}, mock_client)
        assert "error" in result
        assert "unavailable" in result["error"]


class TestHandleDeployTool:
    @pytest.mark.asyncio
    async def test_plan(self):
        from src.api.v1.tools import _handle_deploy_tool

        result = await _handle_deploy_tool("deploy.plan", {})
        assert "plan" in result
        assert "steps" in result

    @pytest.mark.asyncio
    async def test_status(self):
        from src.api.v1.tools import _handle_deploy_tool

        result = await _handle_deploy_tool("deploy.status", {"environment": "production"})
        assert result["environment"] == "production"

    @pytest.mark.asyncio
    async def test_validate(self):
        from src.api.v1.tools import _handle_deploy_tool

        result = await _handle_deploy_tool("deploy.validate", {})
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_unknown(self):
        from src.api.v1.tools import _handle_deploy_tool

        result = await _handle_deploy_tool("deploy.rollback", {})
        assert "error" in result
