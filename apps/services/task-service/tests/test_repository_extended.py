"""
Extended tests for src/repository.py
Uses sys.path manipulation to ensure shared database module is importable.
"""

import os
import sys

# Ensure shared database path is first so `from database import Base` works
_shared_path = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
if _shared_path in sys.path:
    sys.path.remove(_shared_path)
sys.path.insert(0, _shared_path)

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.repository import AsyncTaskRepository, TaskRepository, _sanitize_id


class TestSanitizeId:
    def test_normal(self):
        assert _sanitize_id("task_123") == "task_123"

    def test_newline_removal(self):
        assert "\n" not in _sanitize_id("task\n123")

    def test_truncation(self):
        assert len(_sanitize_id("a" * 200)) == 100

    def test_empty(self):
        assert _sanitize_id("") == ""

    def test_none(self):
        assert _sanitize_id(None) == ""


class TestTaskRepository:
    def _make_db(self):
        return MagicMock()

    def _make_task(self, task_id="task_1", status="pending"):
        task = MagicMock()
        task.task_id = task_id
        task.status = status
        task.created_by = "admin"
        task.task_metadata = {}
        return task

    def test_create_task(self):
        db = self._make_db()
        repo = TaskRepository(db)
        task = self._make_task()
        result = repo.create_task(task)
        db.add.assert_called()
        db.commit.assert_called()
        assert result == task

    def test_create_task_rollback(self):
        db = self._make_db()
        db.commit.side_effect = Exception("err")
        repo = TaskRepository(db)
        with pytest.raises(Exception):
            repo.create_task(self._make_task())
        db.rollback.assert_called_once()

    def test_get_task_by_id(self):
        db = self._make_db()
        t = self._make_task()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = t
        repo = TaskRepository(db)
        assert repo.get_task_by_id("task_1", "t1") == t

    def test_get_task_not_found(self):
        db = self._make_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        repo = TaskRepository(db)
        assert repo.get_task_by_id("x", "t1") is None

    def test_list_tasks(self):
        db = self._make_db()
        mq = MagicMock()
        db.query.return_value.filter.return_value = mq
        mq.count.return_value = 2
        mq.filter.return_value = mq
        mq.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [
            self._make_task("t1"), self._make_task("t2"),
        ]
        repo = TaskRepository(db)
        tasks, total = repo.list_tasks("tenant1")
        assert total == 2 and len(tasks) == 2

    def test_list_tasks_with_filters(self):
        db = self._make_db()
        mq = MagicMock()
        db.query.return_value.filter.return_value = mq
        mq.filter.return_value = mq
        mq.count.return_value = 1
        mq.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self._make_task()]
        repo = TaskRepository(db)
        tasks, total = repo.list_tasks("t1", field_id="f1", status="pending",
                                       task_type="irrigation", priority="high", assigned_to="u1")
        assert total == 1

    def test_update_task_not_found(self):
        db = self._make_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        repo = TaskRepository(db)
        assert repo.update_task("x", "t1", {"title": "new"}, "admin") is None

    def test_update_task_success(self):
        db = self._make_db()
        task = self._make_task()
        task.title = "Old"
        db.query.return_value.options.return_value.filter.return_value.first.return_value = task
        repo = TaskRepository(db)
        result = repo.update_task("task_1", "t1", {"title": "New"}, "admin")
        db.commit.assert_called()
        assert result is not None

    def test_delete_task_success(self):
        db = self._make_db()
        task = self._make_task()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = task
        repo = TaskRepository(db)
        assert repo.delete_task("task_1", "t1") is True

    def test_delete_task_not_found(self):
        db = self._make_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        repo = TaskRepository(db)
        assert repo.delete_task("x", "t1") is False

    def test_start_task_success(self):
        db = self._make_db()
        task = self._make_task(status="pending")
        db.query.return_value.options.return_value.filter.return_value.first.return_value = task
        repo = TaskRepository(db)
        assert repo.start_task("task_1", "t1", "admin") is not None

    def test_start_task_not_found(self):
        db = self._make_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        repo = TaskRepository(db)
        assert repo.start_task("x", "t1", "admin") is None

    def test_start_task_wrong_status(self):
        db = self._make_db()
        task = self._make_task(status="completed")
        db.query.return_value.options.return_value.filter.return_value.first.return_value = task
        repo = TaskRepository(db)
        with pytest.raises(ValueError):
            repo.start_task("task_1", "t1", "admin")

    def test_complete_task_success(self):
        db = self._make_db()
        task = self._make_task(status="in_progress")
        db.query.return_value.options.return_value.filter.return_value.first.return_value = task
        repo = TaskRepository(db)
        assert repo.complete_task("task_1", "t1", "admin", notes="Done") is not None

    def test_complete_task_not_found(self):
        db = self._make_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        repo = TaskRepository(db)
        assert repo.complete_task("x", "t1", "admin") is None

    def test_cancel_task_success(self):
        db = self._make_db()
        task = self._make_task()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = task
        repo = TaskRepository(db)
        assert repo.cancel_task("task_1", "t1", "admin", reason="done") is not None

    def test_cancel_task_not_found(self):
        db = self._make_db()
        db.query.return_value.options.return_value.filter.return_value.first.return_value = None
        repo = TaskRepository(db)
        assert repo.cancel_task("x", "t1", "admin") is None

    def test_add_evidence(self):
        db = self._make_db()
        db.query.return_value.filter.return_value.first.return_value = self._make_task()
        evidence = MagicMock()
        evidence.evidence_id = "ev_1"
        evidence.task_id = "task_1"
        repo = TaskRepository(db)
        repo.add_evidence(evidence)
        db.add.assert_called_with(evidence)

    def test_get_task_stats(self):
        db = self._make_db()
        db.query.return_value.filter.return_value.scalar.return_value = 10
        repo = TaskRepository(db)
        stats = repo.get_task_stats("t1")
        assert "total" in stats and "week_progress" in stats

    def test_record_history_error_handled(self):
        db = self._make_db()
        db.add.side_effect = Exception("fail")
        repo = TaskRepository(db)
        repo._record_history(task_id="t1", action="created", performed_by="admin")


class TestAsyncTaskRepository:
    @pytest.mark.asyncio
    async def test_create_task(self):
        db = AsyncMock()
        task = MagicMock()
        task.task_id = "task_1"
        task.status = "pending"
        task.created_by = "admin"
        repo = AsyncTaskRepository(db)
        result = await repo.create_task(task)
        db.commit.assert_awaited()
        assert result == task

    @pytest.mark.asyncio
    async def test_create_task_rollback(self):
        db = AsyncMock()
        db.commit.side_effect = Exception("err")
        task = MagicMock()
        task.task_id = "t1"
        repo = AsyncTaskRepository(db)
        with pytest.raises(Exception):
            await repo.create_task(task)
        db.rollback.assert_awaited()

    @pytest.mark.asyncio
    async def test_get_task_by_id(self):
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = MagicMock()
        db.execute.return_value = mock_result
        repo = AsyncTaskRepository(db)
        assert await repo.get_task_by_id("t1", "t1") is not None

    @pytest.mark.asyncio
    async def test_get_task_not_found(self):
        db = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        db.execute.return_value = mock_result
        repo = AsyncTaskRepository(db)
        assert await repo.get_task_by_id("x", "t1") is None

    @pytest.mark.asyncio
    async def test_record_history(self):
        db = AsyncMock()
        repo = AsyncTaskRepository(db)
        await repo._record_history(task_id="t1", action="created", performed_by="admin")
        db.add.assert_called()
