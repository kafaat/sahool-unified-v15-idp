"""
Extended tests for src/models.py
"""

import os
import sys

# Ensure shared database path is first
_shared_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
if _shared_path in sys.path:
    sys.path.remove(_shared_path)
sys.path.insert(0, _shared_path)

import pytest


class TestTaskModel:
    def test_import(self):
        from src.models import Task
        assert Task is not None

    def test_tablename(self):
        from src.models import Task
        assert Task.__tablename__ == "tasks"

    def test_repr(self):
        from src.models import Task
        task = Task()
        task.task_id = "test-123"
        task.title = "Test Task"
        task.status = "pending"
        r = repr(task)
        assert "test-123" in r
        assert "Test Task" in r

    def test_columns_exist(self):
        from src.models import Task
        columns = [c.name for c in Task.__table__.columns]
        expected = [
            "task_id", "title", "title_ar", "description", "description_ar",
            "task_type", "priority", "status",
            "field_id", "zone_id", "assigned_to", "created_by",
            "due_date", "scheduled_time", "estimated_duration_minutes",
            "actual_duration_minutes", "completed_at", "completion_notes",
            "task_metadata",
            "astronomical_score", "moon_phase_at_due_date",
            "lunar_mansion_at_due_date", "optimal_time_of_day",
            "suggested_by_calendar", "astronomical_recommendation",
            "astronomical_warnings",
            "tenant_id", "created_at", "updated_at",
        ]
        for col_name in expected:
            assert col_name in columns, f"Column {col_name} not found"

    def test_indexes(self):
        from src.models import Task
        index_names = [idx.name for idx in Task.__table__.indexes]
        for idx in ["idx_tasks_tenant_status", "idx_tasks_assigned_status",
                     "idx_tasks_field_status", "idx_tasks_due_date_status"]:
            assert idx in index_names

    def test_relationship_evidence(self):
        from src.models import Task
        assert "evidence" in Task.__mapper__.relationships


class TestTaskEvidenceModel:
    def test_import(self):
        from src.models import TaskEvidence
        assert TaskEvidence is not None

    def test_tablename(self):
        from src.models import TaskEvidence
        assert TaskEvidence.__tablename__ == "task_evidence"

    def test_repr(self):
        from src.models import TaskEvidence
        ev = TaskEvidence()
        ev.evidence_id = "ev-1"
        ev.task_id = "t-1"
        ev.type = "photo"
        assert "ev-1" in repr(ev)

    def test_columns_exist(self):
        from src.models import TaskEvidence
        columns = [c.name for c in TaskEvidence.__table__.columns]
        for col in ["evidence_id", "task_id", "type", "content", "captured_at", "location"]:
            assert col in columns

    def test_indexes(self):
        from src.models import TaskEvidence
        index_names = [idx.name for idx in TaskEvidence.__table__.indexes]
        assert "idx_evidence_task_id" in index_names
        assert "idx_evidence_type" in index_names


class TestTaskHistoryModel:
    def test_import(self):
        from src.models import TaskHistory
        assert TaskHistory is not None

    def test_tablename(self):
        from src.models import TaskHistory
        assert TaskHistory.__tablename__ == "task_history"

    def test_repr(self):
        from src.models import TaskHistory
        h = TaskHistory()
        h.task_id = "t-1"
        h.action = "created"
        h.performed_by = "admin"
        r = repr(h)
        assert "t-1" in r and "created" in r

    def test_columns_exist(self):
        from src.models import TaskHistory
        columns = [c.name for c in TaskHistory.__table__.columns]
        for col in ["history_id", "task_id", "action", "old_status", "new_status",
                     "performed_by", "changes", "notes"]:
            assert col in columns

    def test_indexes(self):
        from src.models import TaskHistory
        index_names = [idx.name for idx in TaskHistory.__table__.indexes]
        assert "idx_history_task_id" in index_names
        assert "idx_history_action" in index_names
