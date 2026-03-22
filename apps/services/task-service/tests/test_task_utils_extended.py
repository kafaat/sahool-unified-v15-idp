"""
Extended tests for src/task_utils.py
Tests enums, data classes, NDVI priority, content generation, activity translations,
and async service integration with mocks.
"""

import asyncio
from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.task_utils import (
    TaskCreateData,
    TaskPriority,
    TaskStatus,
    TaskType,
    _empty_astronomical_data,
    calculate_ndvi_priority,
    db_task_to_dict,
    fetch_field_manager,
    generate_ndvi_task_content,
    generate_task_id,
    get_activity_translation,
    get_due_date_for_priority,
    get_task_type_activity,
)


# ── Enum tests ─────────────────────────────────────────────────────────


class TestTaskType:
    def test_all_values(self):
        expected = [
            "irrigation", "fertilization", "spraying", "scouting",
            "maintenance", "sampling", "harvest", "planting", "other",
        ]
        for val in expected:
            assert val in [t.value for t in TaskType]

    def test_is_str_enum(self):
        assert isinstance(TaskType.IRRIGATION, str)
        assert TaskType.IRRIGATION == "irrigation"


class TestTaskPriority:
    def test_all_values(self):
        assert TaskPriority.LOW == "low"
        assert TaskPriority.MEDIUM == "medium"
        assert TaskPriority.HIGH == "high"
        assert TaskPriority.URGENT == "urgent"


class TestTaskStatus:
    def test_all_values(self):
        assert TaskStatus.PENDING == "pending"
        assert TaskStatus.IN_PROGRESS == "in_progress"
        assert TaskStatus.COMPLETED == "completed"
        assert TaskStatus.CANCELLED == "cancelled"
        assert TaskStatus.OVERDUE == "overdue"


# ── TaskCreateData ─────────────────────────────────────────────────────


class TestTaskCreateData:
    def test_required_fields(self):
        data = TaskCreateData(
            tenant_id="t1",
            title="Test",
            task_type=TaskType.IRRIGATION,
        )
        assert data.tenant_id == "t1"
        assert data.title == "Test"
        assert data.task_type == TaskType.IRRIGATION
        assert data.priority == TaskPriority.MEDIUM  # default
        assert data.metadata == {}  # default
        assert data.astronomical_warnings == []

    def test_all_fields(self):
        now = datetime.now(UTC)
        data = TaskCreateData(
            tenant_id="t1",
            title="Full",
            task_type=TaskType.HARVEST,
            priority=TaskPriority.HIGH,
            title_ar="كامل",
            description="desc",
            description_ar="وصف",
            field_id="f1",
            zone_id="z1",
            assigned_to="user1",
            created_by="admin",
            due_date=now,
            scheduled_time="08:00",
            estimated_duration_minutes=60,
            metadata={"key": "val"},
            astronomical_score=8,
            moon_phase_at_due_date="Full Moon",
            lunar_mansion_at_due_date="Al-Thurayya",
            optimal_time_of_day="07:00-10:00",
            suggested_by_calendar=True,
            astronomical_recommendation={"rec": "good"},
            astronomical_warnings=["warning1"],
        )
        assert data.field_id == "f1"
        assert data.astronomical_score == 8
        assert data.suggested_by_calendar is True

    def test_metadata_defaults_to_empty(self):
        data = TaskCreateData(
            tenant_id="t1", title="T", task_type=TaskType.OTHER,
            metadata=None,
        )
        assert data.metadata == {}

    def test_warnings_defaults_to_empty(self):
        data = TaskCreateData(
            tenant_id="t1", title="T", task_type=TaskType.OTHER,
            astronomical_warnings=None,
        )
        assert data.astronomical_warnings == []


# ── generate_task_id ───────────────────────────────────────────────────


class TestGenerateTaskId:
    def test_starts_with_task(self):
        tid = generate_task_id()
        assert tid.startswith("task_")

    def test_unique(self):
        ids = {generate_task_id() for _ in range(100)}
        assert len(ids) == 100

    def test_length(self):
        tid = generate_task_id()
        # "task_" + 12 hex chars = 17
        assert len(tid) == 17


# ── calculate_ndvi_priority ────────────────────────────────────────────


class TestCalculateNdviPriority:
    def test_critical_ndvi_urgent(self):
        assert calculate_ndvi_priority(0.1) == TaskPriority.URGENT

    def test_low_ndvi_high(self):
        assert calculate_ndvi_priority(0.25) == TaskPriority.HIGH

    def test_significant_drop_urgent(self):
        assert calculate_ndvi_priority(0.5, previous_ndvi=0.8) == TaskPriority.URGENT

    def test_moderate_drop_high(self):
        assert calculate_ndvi_priority(0.6, previous_ndvi=0.8) == TaskPriority.HIGH

    def test_small_drop_medium(self):
        assert calculate_ndvi_priority(0.72, previous_ndvi=0.8) == TaskPriority.MEDIUM

    def test_z_score_urgent(self):
        assert calculate_ndvi_priority(0.5, alert_metadata={"z_score": 3.5}) == TaskPriority.URGENT

    def test_z_score_high(self):
        assert calculate_ndvi_priority(0.5, alert_metadata={"z_score": 2.5}) == TaskPriority.HIGH

    def test_z_score_medium(self):
        assert calculate_ndvi_priority(0.5, alert_metadata={"z_score": 1.6}) == TaskPriority.MEDIUM

    def test_critical_alert_type(self):
        assert calculate_ndvi_priority(0.5, alert_type="critical") == TaskPriority.HIGH

    def test_drop_alert_type(self):
        assert calculate_ndvi_priority(0.5, alert_type="drop") == TaskPriority.MEDIUM

    def test_anomaly_default_low(self):
        assert calculate_ndvi_priority(0.5, alert_type="anomaly") == TaskPriority.LOW

    def test_previous_ndvi_zero_skips_drop(self):
        # previous_ndvi=0 should skip drop calculation
        assert calculate_ndvi_priority(0.5, previous_ndvi=0) == TaskPriority.LOW

    def test_negative_z_score(self):
        assert calculate_ndvi_priority(0.5, alert_metadata={"z_score": -3.5}) == TaskPriority.URGENT


# ── generate_ndvi_task_content ─────────────────────────────────────────


class TestGenerateNdviTaskContent:
    def test_critical_content(self):
        title, title_ar, desc, desc_ar = generate_ndvi_task_content(
            "critical", 0.15, None, "field_1",
        )
        assert "Critical" in title
        assert "حرج" in title_ar
        assert "NDVI: 0.150" in desc

    def test_drop_content(self):
        title, title_ar, desc, desc_ar = generate_ndvi_task_content(
            "drop", 0.5, 0.8, "field_1",
        )
        assert "Decline" in title
        assert "37.5%" in desc

    def test_anomaly_content(self):
        title, title_ar, desc, desc_ar = generate_ndvi_task_content(
            "anomaly", 0.4, None, "field_1",
        )
        assert "Unusual" in title

    def test_zone_included(self):
        title, title_ar, _, _ = generate_ndvi_task_content(
            "critical", 0.15, None, "f1", zone_id="z1",
        )
        assert "Zone: z1" in title
        assert "المنطقة: z1" in title_ar

    def test_drop_with_no_previous(self):
        # previous_ndvi=None should result in 0.0% drop
        _, _, desc, _ = generate_ndvi_task_content(
            "drop", 0.5, None, "f1",
        )
        assert "0.0%" in desc

    def test_drop_with_zero_previous(self):
        _, _, desc, _ = generate_ndvi_task_content(
            "drop", 0.5, 0, "f1",
        )
        assert "0.0%" in desc


# ── get_due_date_for_priority ──────────────────────────────────────────


class TestGetDueDateForPriority:
    def test_urgent(self):
        before = datetime.now(UTC)
        result = get_due_date_for_priority(TaskPriority.URGENT)
        expected_max = before + timedelta(hours=4, seconds=2)
        assert result <= expected_max

    def test_high(self):
        before = datetime.now(UTC)
        result = get_due_date_for_priority(TaskPriority.HIGH)
        assert result > before
        assert result < before + timedelta(hours=13)

    def test_medium(self):
        before = datetime.now(UTC)
        result = get_due_date_for_priority(TaskPriority.MEDIUM)
        assert result > before
        assert result < before + timedelta(days=2)

    def test_low(self):
        before = datetime.now(UTC)
        result = get_due_date_for_priority(TaskPriority.LOW)
        assert result > before
        assert result < before + timedelta(days=3)


# ── get_activity_translation ───────────────────────────────────────────


class TestGetActivityTranslation:
    def test_arabic_input(self):
        en, ar = get_activity_translation("زراعة")
        assert en == "planting"
        assert ar == "زراعة"

    def test_english_input(self):
        en, ar = get_activity_translation("irrigation")
        assert en == "irrigation"
        assert ar == "ري"

    def test_all_arabic_activities(self):
        arabic = ["زراعة", "ري", "حصاد", "تسميد", "تقليم", "غرس", "رش", "فحص", "جمع عينات"]
        for activity in arabic:
            en, ar = get_activity_translation(activity)
            assert en != ""
            assert ar != ""

    def test_unknown_activity(self):
        en, ar = get_activity_translation("unknown_activity")
        assert en == "unknown_activity"
        assert ar == "unknown_activity"

    def test_case_insensitive(self):
        en, ar = get_activity_translation("Irrigation")
        # The function lowercases, so this should work
        assert en == "irrigation"


# ── get_task_type_activity ─────────────────────────────────────────────


class TestGetTaskTypeActivity:
    def test_all_types(self):
        for task_type in TaskType:
            result = get_task_type_activity(task_type)
            assert isinstance(result, str)
            assert len(result) > 0

    def test_irrigation(self):
        assert get_task_type_activity(TaskType.IRRIGATION) == "ري"

    def test_harvest(self):
        assert get_task_type_activity(TaskType.HARVEST) == "حصاد"

    def test_other(self):
        assert get_task_type_activity(TaskType.OTHER) == "زراعة"


# ── _empty_astronomical_data ───────────────────────────────────────────


class TestEmptyAstronomicalData:
    def test_structure(self):
        data = _empty_astronomical_data()
        assert data["score"] is None
        assert data["moon_phase"] is None
        assert data["warnings"] == []
        assert data["full_data"] is None
        assert "lunar_mansion" in data
        assert "optimal_time" in data


# ── db_task_to_dict ────────────────────────────────────────────────────


class TestDbTaskToDict:
    def test_basic_conversion(self):
        now = datetime.now(UTC)
        mock_task = MagicMock()
        mock_task.task_id = "t1"
        mock_task.tenant_id = "tenant1"
        mock_task.title = "Test"
        mock_task.title_ar = "اختبار"
        mock_task.description = "desc"
        mock_task.description_ar = "وصف"
        mock_task.task_type = "irrigation"
        mock_task.priority = "high"
        mock_task.status = "pending"
        mock_task.field_id = "f1"
        mock_task.zone_id = "z1"
        mock_task.assigned_to = "user1"
        mock_task.created_by = "admin"
        mock_task.due_date = now
        mock_task.scheduled_time = "08:00"
        mock_task.estimated_duration_minutes = 60
        mock_task.actual_duration_minutes = 50
        mock_task.created_at = now
        mock_task.updated_at = now
        mock_task.completed_at = None
        mock_task.completion_notes = None
        mock_task.task_metadata = {"key": "val"}
        mock_task.evidence = []
        mock_task.astronomical_score = 8
        mock_task.moon_phase_at_due_date = "Full Moon"
        mock_task.lunar_mansion_at_due_date = "Al-Thurayya"
        mock_task.optimal_time_of_day = "07:00-10:00"
        mock_task.suggested_by_calendar = True
        mock_task.astronomical_recommendation = {"rec": "good"}
        mock_task.astronomical_warnings = ["warning1"]

        result = db_task_to_dict(mock_task)

        assert result["task_id"] == "t1"
        assert result["title"] == "Test"
        assert result["metadata"] == {"key": "val"}  # mapped from task_metadata
        assert result["astronomical_score"] == 8
        assert result["evidence"] == []
        assert result["due_date"] == now.isoformat()

    def test_none_dates(self):
        mock_task = MagicMock()
        mock_task.due_date = None
        mock_task.created_at = None
        mock_task.updated_at = None
        mock_task.completed_at = None
        mock_task.evidence = []
        mock_task.astronomical_warnings = None

        result = db_task_to_dict(mock_task)
        assert result["due_date"] is None
        assert result["created_at"] is None
        assert result["astronomical_warnings"] == []

    def test_evidence_serialization(self):
        now = datetime.now(UTC)
        mock_evidence = MagicMock()
        mock_evidence.evidence_id = "ev1"
        mock_evidence.task_id = "t1"
        mock_evidence.type = "photo"
        mock_evidence.content = "http://example.com/img.jpg"
        mock_evidence.captured_at = now
        mock_evidence.location = {"lat": 24.7, "lon": 46.7}

        mock_task = MagicMock()
        mock_task.evidence = [mock_evidence]
        mock_task.due_date = None
        mock_task.created_at = None
        mock_task.updated_at = None
        mock_task.completed_at = None
        mock_task.astronomical_warnings = []

        result = db_task_to_dict(mock_task)
        assert len(result["evidence"]) == 1
        assert result["evidence"][0]["evidence_id"] == "ev1"
        assert result["evidence"][0]["location"] == {"lat": 24.7, "lon": 46.7}


# ── fetch_field_manager ────────────────────────────────────────────────


class TestFetchFieldManager:
    @pytest.mark.asyncio
    async def test_invalid_field_id(self):
        result = await fetch_field_manager("bad@id", "t1")
        assert result is None

    @pytest.mark.asyncio
    async def test_successful_fetch(self):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"user_id": "user_123"}

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.return_value = mock_response
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await fetch_field_manager("field_1", "t1")
            assert result == "user_123"

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

            result = await fetch_field_manager("field_1", "t1")
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

            result = await fetch_field_manager("field_1", "t1")
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

            result = await fetch_field_manager("field_1", "t1")
            assert result is None

    @pytest.mark.asyncio
    async def test_timeout(self):
        import httpx

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.TimeoutException("timeout")
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await fetch_field_manager("field_1", "t1")
            assert result is None

    @pytest.mark.asyncio
    async def test_connection_error(self):
        import httpx

        with patch("src.task_utils.httpx.AsyncClient") as MockClient:
            mock_client = AsyncMock()
            mock_client.get.side_effect = httpx.ConnectError("refused")
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=False)
            MockClient.return_value = mock_client

            result = await fetch_field_manager("field_1", "t1")
            assert result is None
