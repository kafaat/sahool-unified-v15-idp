"""
Async unit tests for Task Service task_utils module.
اختبارات غير متزامنة لوحدة أدوات المهام
"""

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from src.exceptions import (
    AstronomicalServiceError,
    AstronomicalServiceTimeoutError,
)
from src.task_utils import (
    TaskCreateData,
    TaskPriority,
    TaskType,
    enrich_task_with_astronomy,
    fetch_astronomical_best_days,
    fetch_astronomical_daily_data,
    fetch_astronomical_data,
    fetch_field_manager,
    send_task_notification,
)


class TestFetchFieldManager:
    """Tests for fetch_field_manager"""

    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"user_id": "user_ahmed"}

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await fetch_field_manager("field_001", "tenant_1")
            assert result == "user_ahmed"

    @pytest.mark.asyncio
    async def test_field_not_found(self):
        mock_response = MagicMock()
        mock_response.status_code = 404

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await fetch_field_manager("nonexistent", "tenant_1")
            assert result is None

    @pytest.mark.asyncio
    async def test_invalid_field_id(self):
        result = await fetch_field_manager("bad@id!", "tenant_1")
        assert result is None

    @pytest.mark.asyncio
    async def test_timeout(self):
        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.TimeoutException("timeout")
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await fetch_field_manager("field_001", "tenant_1")
            assert result is None

    @pytest.mark.asyncio
    async def test_connection_error(self):
        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.RequestError("connection refused")
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await fetch_field_manager("field_001", "tenant_1")
            assert result is None

    @pytest.mark.asyncio
    async def test_server_error(self):
        mock_response = MagicMock()
        mock_response.status_code = 500

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await fetch_field_manager("field_001", "tenant_1")
            assert result is None

    @pytest.mark.asyncio
    async def test_no_user_id_in_response(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"name": "North Field"}

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await fetch_field_manager("field_001", "tenant_1")
            assert result is None
class TestFetchAstronomicalBestDays:
    """Tests for fetch_astronomical_best_days"""

    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "best_days": [{"date": "2025-06-15", "score": 9}]
        }

        mock_cache = AsyncMock()
        mock_cache.get_best_days = AsyncMock(return_value=None)
        mock_cache.set_best_days = AsyncMock(return_value=True)

        with patch("src.cache.astronomical_cache", mock_cache):
            with patch("src.task_utils.httpx.AsyncClient") as MockClient:
                mock_client = AsyncMock()
                mock_client.get.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                MockClient.return_value = mock_client

                result = await fetch_astronomical_best_days("زراعة", 30)
                assert "best_days" in result

    @pytest.mark.asyncio
    async def test_cached_result(self):
        cached_data = {"best_days": [{"date": "2025-06-15", "score": 8}]}
        mock_cache = AsyncMock()
        mock_cache.get_best_days = AsyncMock(return_value=cached_data)

        with patch("src.cache.astronomical_cache", mock_cache):
            result = await fetch_astronomical_best_days("ري", 30)
            assert result == cached_data

    @pytest.mark.asyncio
    async def test_service_error(self):
        mock_cache = AsyncMock()
        mock_cache.get_best_days = AsyncMock(return_value=None)

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with patch("src.cache.astronomical_cache", mock_cache):
            with patch("src.task_utils.httpx.AsyncClient") as MockClient:
                mock_client = AsyncMock()
                mock_client.get.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                MockClient.return_value = mock_client

                with pytest.raises(AstronomicalServiceError):
                    await fetch_astronomical_best_days("زراعة", 30)

    @pytest.mark.asyncio
    async def test_timeout(self):
        mock_cache = AsyncMock()
        mock_cache.get_best_days = AsyncMock(return_value=None)

        with patch("src.cache.astronomical_cache", mock_cache):
            with patch("src.task_utils.httpx.AsyncClient") as MockClient:
                mock_client = AsyncMock()
                mock_client.get.side_effect = httpx.TimeoutException("timeout")
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                MockClient.return_value = mock_client

                with pytest.raises(AstronomicalServiceTimeoutError):
                    await fetch_astronomical_best_days("زراعة", 30)
class TestFetchAstronomicalDailyData:
    """Tests for fetch_astronomical_daily_data"""

    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "moon_phase": {"name": "Full Moon"},
            "lunar_mansion": {"name": "Al-Sharatain"},
        }

        mock_cache = AsyncMock()
        mock_cache.get_daily_data = AsyncMock(return_value=None)
        mock_cache.set_daily_data = AsyncMock(return_value=True)

        with patch("src.cache.astronomical_cache", mock_cache):
            with patch("src.task_utils.httpx.AsyncClient") as MockClient:
                mock_client = AsyncMock()
                mock_client.get.return_value = mock_response
                mock_client.__aenter__ = AsyncMock(return_value=mock_client)
                mock_client.__aexit__ = AsyncMock(return_value=False)
                MockClient.return_value = mock_client

                result = await fetch_astronomical_daily_data("2025-06-15")
                assert "moon_phase" in result

    @pytest.mark.asyncio
    async def test_cached_result(self):
        cached = {"moon_phase": {"name": "Waning"}}
        mock_cache = AsyncMock()
        mock_cache.get_daily_data = AsyncMock(return_value=cached)

        with patch("src.cache.astronomical_cache", mock_cache):
            result = await fetch_astronomical_daily_data("2025-06-15")
            assert result == cached
class TestFetchAstronomicalData:
    """Tests for fetch_astronomical_data"""

    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "overall_farming_score": 8,
            "moon_phase": {"name": "Waxing Crescent", "farming_good": True},
            "lunar_mansion": {"name": "Al-Sharatain"},
            "recommendations": [],
        }
        mock_response.raise_for_status = MagicMock()

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            due_date = datetime(2025, 6, 15, tzinfo=UTC)
            result = await fetch_astronomical_data(due_date, TaskType.IRRIGATION)
            assert result["score"] == 8
            assert result["optimal_time"] == "06:00-08:00"  # irrigation time

    @pytest.mark.asyncio
    async def test_harvest_optimal_time(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "overall_farming_score": 7,
            "moon_phase": {"name": "Full", "farming_good": True},
            "lunar_mansion": {"name": "Test"},
            "recommendations": [],
        }
        mock_response.raise_for_status = MagicMock()

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            due_date = datetime(2025, 6, 15, tzinfo=UTC)
            result = await fetch_astronomical_data(due_date, TaskType.HARVEST)
            assert result["optimal_time"] == "07:00-11:00"

    @pytest.mark.asyncio
    async def test_low_score_warnings(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "overall_farming_score": 3,
            "moon_phase": {"name": "New Moon", "farming_good": False},
            "lunar_mansion": {"name": "Test"},
            "recommendations": [],
        }
        mock_response.raise_for_status = MagicMock()

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            due_date = datetime(2025, 6, 15, tzinfo=UTC)
            result = await fetch_astronomical_data(due_date, TaskType.PLANTING)
            assert len(result["warnings"]) > 0

    @pytest.mark.asyncio
    async def test_http_error_returns_empty(self):
        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.HTTPError("fail")
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            due_date = datetime(2025, 6, 15, tzinfo=UTC)
            result = await fetch_astronomical_data(due_date, TaskType.OTHER)
            assert result["score"] is None
            assert result["warnings"] == []
class TestEnrichTaskWithAstronomy:
    """Tests for enrich_task_with_astronomy"""

    @pytest.mark.asyncio
    async def test_no_due_date_returns_unchanged(self):
        data = TaskCreateData(
            tenant_id="t1",
            title="Test",
            task_type=TaskType.SCOUTING,
            due_date=None,
        )
        result = await enrich_task_with_astronomy(data, TaskType.SCOUTING)
        assert result.astronomical_score is None

    @pytest.mark.asyncio
    async def test_enriches_with_astronomical_data(self):
        data = TaskCreateData(
            tenant_id="t1",
            title="Test",
            task_type=TaskType.PLANTING,
            due_date=datetime(2025, 6, 15, tzinfo=UTC),
        )

        mock_astro = {
            "score": 9,
            "moon_phase_ar": "هلال متزايد",
            "lunar_mansion_ar": "الشرطان",
            "optimal_time": "07:00-10:00",
            "full_data": {"raw": "data"},
            "warnings": [],
        }

        with patch("src.task_utils.fetch_astronomical_data", new_callable=AsyncMock, return_value=mock_astro):
            result = await enrich_task_with_astronomy(data, TaskType.PLANTING)
            assert result.astronomical_score == 9
            assert result.moon_phase_at_due_date == "هلال متزايد"
            assert result.optimal_time_of_day == "07:00-10:00"
class TestSendTaskNotification:
    """Tests for send_task_notification"""

    @pytest.mark.asyncio
    async def test_successful_notification(self):
        mock_response = MagicMock()
        mock_response.status_code = 201

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await send_task_notification(
                tenant_id="t1",
                task_id="task_001",
                title="Test Task",
                title_ar="مهمة اختبار",
                description="desc",
                description_ar="وصف",
                assigned_to="user_1",
                priority=TaskPriority.HIGH,
                task_type=TaskType.IRRIGATION,
                field_id="field_1",
                zone_id=None,
                due_date=datetime.now(UTC),
            )
            assert result is True

    @pytest.mark.asyncio
    async def test_notification_failure(self):
        """Notification errors should not crash, just return False"""
        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.post.side_effect = Exception("network error")
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await send_task_notification(
                tenant_id="t1",
                task_id="task_001",
                title="Test",
                title_ar=None,
                description=None,
                description_ar=None,
                assigned_to="user_1",
                priority=TaskPriority.MEDIUM,
                task_type=TaskType.SCOUTING,
                field_id=None,
                zone_id=None,
                due_date=None,
            )
            assert result is False
