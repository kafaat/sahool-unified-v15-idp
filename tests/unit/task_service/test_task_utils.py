"""
Unit tests for Task Service Utilities
اختبارات الوحدة لأدوات خدمة المهام

Tests:
- Task ID generation
- NDVI priority calculation
- Task content generation
- Due date calculation
- Activity translation
"""

from datetime import UTC, datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

# Import from the src package (conftest.py sets up the path)
try:
    from src.task_utils import (
        TaskCreateData,
        TaskPriority,
        TaskType,
        calculate_ndvi_priority,
        db_task_to_dict,
        generate_ndvi_task_content,
        generate_task_id,
        get_activity_translation,
        get_due_date_for_priority,
        get_task_type_activity,
    )
except ModuleNotFoundError:
    pytest.skip("Task service src module not found - run tests from service directory", allow_module_level=True)


class TestTaskIdGeneration:
    """Test task ID generation"""

    def test_generate_task_id_format(self):
        """Test that generated task IDs have correct format"""
        task_id = generate_task_id()

        assert task_id.startswith("task_")
        assert len(task_id) == 17  # "task_" + 12 hex chars

    def test_generate_task_id_uniqueness(self):
        """Test that generated task IDs are unique"""
        ids = [generate_task_id() for _ in range(100)]
        unique_ids = set(ids)

        assert len(unique_ids) == 100


class TestNdviPriorityCalculation:
    """Test NDVI priority calculation"""

    def test_critical_ndvi_urgent(self):
        """Test that critical NDVI values get urgent priority"""
        # Very low NDVI
        priority = calculate_ndvi_priority(ndvi_value=0.15)
        assert priority == TaskPriority.URGENT

        # Low NDVI
        priority = calculate_ndvi_priority(ndvi_value=0.25)
        assert priority == TaskPriority.HIGH

    def test_significant_drop_priority(self):
        """Test priority based on NDVI drop percentage"""
        # 30%+ drop = urgent
        priority = calculate_ndvi_priority(
            ndvi_value=0.5,
            previous_ndvi=0.8,  # 37.5% drop
        )
        assert priority == TaskPriority.URGENT

        # 20-30% drop = high
        priority = calculate_ndvi_priority(
            ndvi_value=0.6,
            previous_ndvi=0.8,  # 25% drop
        )
        assert priority == TaskPriority.HIGH

        # 10-20% drop = medium
        priority = calculate_ndvi_priority(
            ndvi_value=0.7,
            previous_ndvi=0.8,  # 12.5% drop
        )
        assert priority == TaskPriority.MEDIUM

    def test_z_score_priority(self):
        """Test priority based on z-score deviation"""
        # High z-score = urgent
        priority = calculate_ndvi_priority(
            ndvi_value=0.5,
            alert_metadata={"z_score": 3.5},
        )
        assert priority == TaskPriority.URGENT

        # Moderate z-score = high
        priority = calculate_ndvi_priority(
            ndvi_value=0.5,
            alert_metadata={"z_score": 2.5},
        )
        assert priority == TaskPriority.HIGH

    def test_alert_type_fallback(self):
        """Test priority based on alert type fallback"""
        # Critical alert = high
        priority = calculate_ndvi_priority(
            ndvi_value=0.6,
            alert_type="critical",
        )
        assert priority == TaskPriority.HIGH

        # Drop alert = medium
        priority = calculate_ndvi_priority(
            ndvi_value=0.6,
            alert_type="drop",
        )
        assert priority == TaskPriority.MEDIUM

        # Anomaly alert = low
        priority = calculate_ndvi_priority(
            ndvi_value=0.6,
            alert_type="anomaly",
        )
        assert priority == TaskPriority.LOW


class TestNdviTaskContentGeneration:
    """Test NDVI task content generation"""

    def test_critical_alert_content(self):
        """Test content generation for critical alerts"""
        title, title_ar, desc, desc_ar = generate_ndvi_task_content(
            alert_type="critical",
            ndvi_value=0.2,
            previous_ndvi=0.5,
            field_id="field_123",
        )

        assert "Critical" in title
        assert "حرج" in title_ar
        assert "0.2" in desc  # NDVI value included
        assert "field_123" in title

    def test_drop_alert_content(self):
        """Test content generation for drop alerts"""
        title, title_ar, desc, desc_ar = generate_ndvi_task_content(
            alert_type="drop",
            ndvi_value=0.4,
            previous_ndvi=0.7,
            field_id="field_123",
        )

        assert "Decline" in title or "Drop" in title
        assert "تراجع" in title_ar or "انخفض" in title_ar
        # Drop percentage should be calculated
        assert "%" in desc

    def test_anomaly_alert_content(self):
        """Test content generation for anomaly alerts"""
        title, title_ar, desc, desc_ar = generate_ndvi_task_content(
            alert_type="anomaly",
            ndvi_value=0.5,
            previous_ndvi=None,
            field_id="field_123",
        )

        assert "Unusual" in title or "Abnormal" in title
        assert "غير معتاد" in title_ar or "غير طبيعية" in title_ar

    def test_zone_id_included(self):
        """Test that zone ID is included when provided"""
        title, title_ar, _, _ = generate_ndvi_task_content(
            alert_type="critical",
            ndvi_value=0.2,
            previous_ndvi=0.5,
            field_id="field_123",
            zone_id="zone_A",
        )

        assert "zone_A" in title or "Zone" in title
        assert "zone_A" in title_ar or "المنطقة" in title_ar

    def test_arabic_content_present(self):
        """Test that Arabic content is generated"""
        _, title_ar, _, desc_ar = generate_ndvi_task_content(
            alert_type="critical",
            ndvi_value=0.2,
            previous_ndvi=0.5,
            field_id="field_123",
        )

        # Check for Arabic characters
        arabic_chars = set("ابتثجحخدذرزسشصضطظعغفقكلمنهوي")
        assert any(char in title_ar for char in arabic_chars)
        assert any(char in desc_ar for char in arabic_chars)


class TestDueDateCalculation:
    """Test due date calculation"""

    def test_urgent_due_date(self):
        """Test due date for urgent priority"""
        before = datetime.now(UTC)
        due_date = get_due_date_for_priority(TaskPriority.URGENT)
        after = datetime.now(UTC)

        # Should be 4 hours from now
        expected_min = before + timedelta(hours=4)
        expected_max = after + timedelta(hours=4)

        assert expected_min <= due_date <= expected_max

    def test_high_due_date(self):
        """Test due date for high priority"""
        before = datetime.now(UTC)
        due_date = get_due_date_for_priority(TaskPriority.HIGH)
        after = datetime.now(UTC)

        # Should be 12 hours from now
        expected_min = before + timedelta(hours=12)
        expected_max = after + timedelta(hours=12)

        assert expected_min <= due_date <= expected_max

    def test_medium_due_date(self):
        """Test due date for medium priority"""
        before = datetime.now(UTC)
        due_date = get_due_date_for_priority(TaskPriority.MEDIUM)
        after = datetime.now(UTC)

        # Should be 1 day from now
        expected_min = before + timedelta(days=1)
        expected_max = after + timedelta(days=1)

        assert expected_min <= due_date <= expected_max

    def test_low_due_date(self):
        """Test due date for low priority"""
        before = datetime.now(UTC)
        due_date = get_due_date_for_priority(TaskPriority.LOW)
        after = datetime.now(UTC)

        # Should be 2 days from now
        expected_min = before + timedelta(days=2)
        expected_max = after + timedelta(days=2)

        assert expected_min <= due_date <= expected_max


class TestActivityTranslation:
    """Test activity translation"""

    def test_arabic_to_english(self):
        """Test translation from Arabic to English"""
        # Arabic input
        en, ar = get_activity_translation("زراعة")
        assert en == "planting"
        assert ar == "زراعة"

        en, ar = get_activity_translation("ري")
        assert en == "irrigation"
        assert ar == "ري"

        en, ar = get_activity_translation("حصاد")
        assert en == "harvest"
        assert ar == "حصاد"

    def test_english_to_arabic(self):
        """Test translation from English to Arabic"""
        # English input
        en, ar = get_activity_translation("planting")
        assert en == "planting"
        assert ar == "زراعة"

        en, ar = get_activity_translation("irrigation")
        assert en == "irrigation"
        assert ar == "ري"

    def test_unknown_activity(self):
        """Test handling unknown activity"""
        en, ar = get_activity_translation("unknown_activity")
        assert en == "unknown_activity"
        assert ar == "unknown_activity"

    def test_case_insensitive(self):
        """Test case insensitive matching"""
        en1, ar1 = get_activity_translation("PLANTING")
        en2, ar2 = get_activity_translation("Planting")
        en3, ar3 = get_activity_translation("planting")

        assert en1 == en2 == en3 == "planting"


class TestTaskTypeActivityMapping:
    """Test task type to activity mapping"""

    def test_task_type_to_activity(self):
        """Test mapping task types to Arabic activities"""
        assert get_task_type_activity(TaskType.PLANTING) == "زراعة"
        assert get_task_type_activity(TaskType.IRRIGATION) == "ري"
        assert get_task_type_activity(TaskType.HARVEST) == "حصاد"
        assert get_task_type_activity(TaskType.FERTILIZATION) == "تسميد"
        assert get_task_type_activity(TaskType.SPRAYING) == "رش"
        assert get_task_type_activity(TaskType.MAINTENANCE) == "تقليم"
        assert get_task_type_activity(TaskType.SCOUTING) == "فحص"
        assert get_task_type_activity(TaskType.SAMPLING) == "جمع عينات"

    def test_other_task_type(self):
        """Test OTHER task type defaults to planting"""
        assert get_task_type_activity(TaskType.OTHER) == "زراعة"


class TestTaskCreateData:
    """Test TaskCreateData data class"""

    def test_creation_with_required_fields(self):
        """Test creating TaskCreateData with required fields"""
        data = TaskCreateData(
            tenant_id="tenant_123",
            title="Test Task",
            task_type=TaskType.IRRIGATION,
        )

        assert data.tenant_id == "tenant_123"
        assert data.title == "Test Task"
        assert data.task_type == TaskType.IRRIGATION
        assert data.priority == TaskPriority.MEDIUM  # Default
        assert data.metadata == {}  # Default

    def test_creation_with_all_fields(self):
        """Test creating TaskCreateData with all fields"""
        due_date = datetime.now(UTC)

        data = TaskCreateData(
            tenant_id="tenant_123",
            title="Test Task",
            title_ar="مهمة اختبار",
            description="Description",
            description_ar="وصف",
            task_type=TaskType.IRRIGATION,
            priority=TaskPriority.HIGH,
            field_id="field_123",
            zone_id="zone_A",
            assigned_to="user_123",
            created_by="admin",
            due_date=due_date,
            scheduled_time="09:00",
            estimated_duration_minutes=60,
            metadata={"key": "value"},
            astronomical_score=8,
            moon_phase_at_due_date="Full Moon",
            lunar_mansion_at_due_date="Test Mansion",
            suggested_by_calendar=True,
        )

        assert data.title_ar == "مهمة اختبار"
        assert data.priority == TaskPriority.HIGH
        assert data.field_id == "field_123"
        assert data.due_date == due_date
        assert data.astronomical_score == 8
        assert data.suggested_by_calendar is True


class TestDbTaskToDict:
    """Test db_task_to_dict conversion function"""

    def test_basic_conversion(self):
        """Test converting basic task model to dict"""
        # Create mock task
        mock_task = MagicMock()
        mock_task.task_id = "task_123"
        mock_task.tenant_id = "tenant_123"
        mock_task.title = "Test Task"
        mock_task.title_ar = "مهمة اختبار"
        mock_task.description = "Description"
        mock_task.description_ar = "وصف"
        mock_task.task_type = "irrigation"
        mock_task.priority = "high"
        mock_task.status = "pending"
        mock_task.field_id = "field_123"
        mock_task.zone_id = None
        mock_task.assigned_to = "user_123"
        mock_task.created_by = "admin"
        mock_task.due_date = datetime(2024, 1, 15, tzinfo=UTC)
        mock_task.scheduled_time = "09:00"
        mock_task.estimated_duration_minutes = 60
        mock_task.actual_duration_minutes = None
        mock_task.created_at = datetime(2024, 1, 10, tzinfo=UTC)
        mock_task.updated_at = datetime(2024, 1, 10, tzinfo=UTC)
        mock_task.completed_at = None
        mock_task.completion_notes = None
        mock_task.task_metadata = {"key": "value"}
        mock_task.evidence = []
        mock_task.astronomical_score = 8
        mock_task.moon_phase_at_due_date = "Full Moon"
        mock_task.lunar_mansion_at_due_date = "Test"
        mock_task.optimal_time_of_day = "09:00"
        mock_task.suggested_by_calendar = True
        mock_task.astronomical_recommendation = {"rec": "data"}
        mock_task.astronomical_warnings = []

        result = db_task_to_dict(mock_task)

        assert result["task_id"] == "task_123"
        assert result["title"] == "Test Task"
        assert result["title_ar"] == "مهمة اختبار"
        assert result["task_type"] == "irrigation"
        assert result["due_date"] == "2024-01-15T00:00:00+00:00"
        assert result["metadata"] == {"key": "value"}
        assert result["astronomical_score"] == 8

    def test_none_dates(self):
        """Test that None dates are handled properly"""
        mock_task = MagicMock()
        mock_task.task_id = "task_123"
        mock_task.tenant_id = "tenant_123"
        mock_task.title = "Test"
        mock_task.title_ar = None
        mock_task.description = None
        mock_task.description_ar = None
        mock_task.task_type = "other"
        mock_task.priority = "low"
        mock_task.status = "pending"
        mock_task.field_id = None
        mock_task.zone_id = None
        mock_task.assigned_to = None
        mock_task.created_by = "system"
        mock_task.due_date = None
        mock_task.scheduled_time = None
        mock_task.estimated_duration_minutes = None
        mock_task.actual_duration_minutes = None
        mock_task.created_at = None
        mock_task.updated_at = None
        mock_task.completed_at = None
        mock_task.completion_notes = None
        mock_task.task_metadata = None
        mock_task.evidence = None
        mock_task.astronomical_score = None
        mock_task.moon_phase_at_due_date = None
        mock_task.lunar_mansion_at_due_date = None
        mock_task.optimal_time_of_day = None
        mock_task.suggested_by_calendar = False
        mock_task.astronomical_recommendation = None
        mock_task.astronomical_warnings = None

        result = db_task_to_dict(mock_task)

        assert result["due_date"] is None
        assert result["created_at"] is None
        assert result["evidence"] == []

    def test_evidence_conversion(self):
        """Test that evidence is converted properly"""
        mock_evidence = MagicMock()
        mock_evidence.evidence_id = "ev_123"
        mock_evidence.task_id = "task_123"
        mock_evidence.type = "photo"
        mock_evidence.content = "http://example.com/photo.jpg"
        mock_evidence.captured_at = datetime(2024, 1, 10, tzinfo=UTC)
        mock_evidence.location = {"lat": 24.7, "lon": 46.6}

        mock_task = MagicMock()
        mock_task.task_id = "task_123"
        mock_task.tenant_id = "tenant_123"
        mock_task.title = "Test"
        mock_task.title_ar = None
        mock_task.description = None
        mock_task.description_ar = None
        mock_task.task_type = "other"
        mock_task.priority = "low"
        mock_task.status = "pending"
        mock_task.field_id = None
        mock_task.zone_id = None
        mock_task.assigned_to = None
        mock_task.created_by = "system"
        mock_task.due_date = None
        mock_task.scheduled_time = None
        mock_task.estimated_duration_minutes = None
        mock_task.actual_duration_minutes = None
        mock_task.created_at = None
        mock_task.updated_at = None
        mock_task.completed_at = None
        mock_task.completion_notes = None
        mock_task.task_metadata = None
        mock_task.evidence = [mock_evidence]
        mock_task.astronomical_score = None
        mock_task.moon_phase_at_due_date = None
        mock_task.lunar_mansion_at_due_date = None
        mock_task.optimal_time_of_day = None
        mock_task.suggested_by_calendar = False
        mock_task.astronomical_recommendation = None
        mock_task.astronomical_warnings = None

        result = db_task_to_dict(mock_task)

        assert len(result["evidence"]) == 1
        assert result["evidence"][0]["evidence_id"] == "ev_123"
        assert result["evidence"][0]["type"] == "photo"
        assert result["evidence"][0]["location"] == {"lat": 24.7, "lon": 46.6}
