"""
Task Repository Layer - طبقة مستودع المهام

Provides database operations for tasks and evidence.
يوفر عمليات قاعدة البيانات للمهام والأدلة.
"""

import logging
from datetime import datetime
from typing import Optional, List

from sqlalchemy import select, and_, or_, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session, selectinload

from .models import Task, TaskEvidence, TaskHistory

logger = logging.getLogger(__name__)


class TaskRepository:
    """
    Repository for Task database operations
    مستودع لعمليات قاعدة بيانات المهام
    """

    def __init__(self, db: Session):
        """Initialize repository with database session"""
        self.db = db

    def create_task(self, task: Task) -> Task:
        """
        Create a new task
        إنشاء مهمة جديدة
        """
        try:
            self.db.add(task)
            self.db.commit()
            self.db.refresh(task)

            # Record history
            self._record_history(
                task_id=task.task_id,
                action="created",
                new_status=task.status,
                performed_by=task.created_by,
            )

            logger.info(f"Created task: {task.task_id}")
            return task
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating task: {e}")
            raise

    def get_task_by_id(self, task_id: str, tenant_id: str) -> Optional[Task]:
        """
        Get task by ID and tenant
        الحصول على مهمة بواسطة المعرف والمستأجر
        """
        return (
            self.db.query(Task)
            .options(selectinload(Task.evidence))
            .filter(
                and_(
                    Task.task_id == task_id,
                    Task.tenant_id == tenant_id,
                )
            )
            .first()
        )

    def list_tasks(
        self,
        tenant_id: str,
        field_id: Optional[str] = None,
        status: Optional[str] = None,
        task_type: Optional[str] = None,
        priority: Optional[str] = None,
        assigned_to: Optional[str] = None,
        due_before: Optional[datetime] = None,
        due_after: Optional[datetime] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Task], int]:
        """
        List tasks with filters and pagination
        قائمة المهام مع الفلاتر والترقيم

        Returns:
            Tuple of (tasks, total_count)
        """
        # Build query with filters
        query = self.db.query(Task).filter(Task.tenant_id == tenant_id)

        if field_id:
            query = query.filter(Task.field_id == field_id)
        if status:
            query = query.filter(Task.status == status)
        if task_type:
            query = query.filter(Task.task_type == task_type)
        if priority:
            query = query.filter(Task.priority == priority)
        if assigned_to:
            query = query.filter(Task.assigned_to == assigned_to)
        if due_before:
            query = query.filter(Task.due_date <= due_before)
        if due_after:
            query = query.filter(Task.due_date >= due_after)

        # Get total count before pagination
        total = query.count()

        # Apply sorting and pagination
        tasks = (
            query.order_by(Task.due_date.asc(), Task.priority.asc())
            .offset(offset)
            .limit(limit)
            .all()
        )

        return tasks, total

    def update_task(
        self,
        task_id: str,
        tenant_id: str,
        updates: dict,
        performed_by: str,
    ) -> Optional[Task]:
        """
        Update task fields
        تحديث حقول المهمة
        """
        task = self.get_task_by_id(task_id, tenant_id)
        if not task:
            return None

        try:
            old_status = task.status
            changes = {}

            for key, value in updates.items():
                if hasattr(task, key) and value is not None:
                    old_value = getattr(task, key)
                    if old_value != value:
                        changes[key] = {
                            "old": str(old_value) if old_value else None,
                            "new": str(value),
                        }
                    setattr(task, key, value)

            task.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(task)

            # Record history if there were changes
            if changes:
                self._record_history(
                    task_id=task_id,
                    action="updated",
                    old_status=old_status if old_status != task.status else None,
                    new_status=task.status if old_status != task.status else None,
                    performed_by=performed_by,
                    changes=changes,
                )

            logger.info(f"Updated task: {task_id} with {len(changes)} changes")
            return task

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating task {task_id}: {e}")
            raise

    def delete_task(self, task_id: str, tenant_id: str) -> bool:
        """
        Delete a task
        حذف مهمة
        """
        task = self.get_task_by_id(task_id, tenant_id)
        if not task:
            return False

        try:
            self.db.delete(task)
            self.db.commit()
            logger.info(f"Deleted task: {task_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting task {task_id}: {e}")
            raise

    def start_task(
        self,
        task_id: str,
        tenant_id: str,
        performed_by: str,
    ) -> Optional[Task]:
        """
        Mark task as in progress
        تعيين المهمة كقيد التنفيذ
        """
        task = self.get_task_by_id(task_id, tenant_id)
        if not task:
            return None

        if task.status != "pending":
            raise ValueError("Task is not in pending status")

        try:
            old_status = task.status
            task.status = "in_progress"
            task.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(task)

            self._record_history(
                task_id=task_id,
                action="started",
                old_status=old_status,
                new_status="in_progress",
                performed_by=performed_by,
            )

            logger.info(f"Started task: {task_id}")
            return task

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error starting task {task_id}: {e}")
            raise

    def complete_task(
        self,
        task_id: str,
        tenant_id: str,
        performed_by: str,
        notes: Optional[str] = None,
        actual_duration_minutes: Optional[int] = None,
        completion_metadata: Optional[dict] = None,
    ) -> Optional[Task]:
        """
        Mark task as completed
        تعيين المهمة كمكتملة
        """
        task = self.get_task_by_id(task_id, tenant_id)
        if not task:
            return None

        try:
            old_status = task.status
            now = datetime.utcnow()

            task.status = "completed"
            task.completed_at = now
            task.updated_at = now
            task.completion_notes = notes

            if actual_duration_minutes:
                task.actual_duration_minutes = actual_duration_minutes

            if completion_metadata:
                task.metadata = {**(task.metadata or {}), **completion_metadata}

            self.db.commit()
            self.db.refresh(task)

            self._record_history(
                task_id=task_id,
                action="completed",
                old_status=old_status,
                new_status="completed",
                performed_by=performed_by,
                notes=notes,
            )

            logger.info(f"Completed task: {task_id}")
            return task

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error completing task {task_id}: {e}")
            raise

    def cancel_task(
        self,
        task_id: str,
        tenant_id: str,
        performed_by: str,
        reason: Optional[str] = None,
    ) -> Optional[Task]:
        """
        Cancel a task
        إلغاء مهمة
        """
        task = self.get_task_by_id(task_id, tenant_id)
        if not task:
            return None

        try:
            old_status = task.status
            task.status = "cancelled"
            task.updated_at = datetime.utcnow()

            if reason:
                task.metadata = {**(task.metadata or {}), "cancel_reason": reason}

            self.db.commit()
            self.db.refresh(task)

            self._record_history(
                task_id=task_id,
                action="cancelled",
                old_status=old_status,
                new_status="cancelled",
                performed_by=performed_by,
                notes=reason,
            )

            logger.info(f"Cancelled task: {task_id}")
            return task

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling task {task_id}: {e}")
            raise

    def add_evidence(
        self,
        evidence: TaskEvidence,
    ) -> TaskEvidence:
        """
        Add evidence to a task
        إضافة دليل إلى مهمة
        """
        try:
            self.db.add(evidence)

            # Update task's updated_at timestamp
            task = self.db.query(Task).filter(Task.task_id == evidence.task_id).first()
            if task:
                task.updated_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(evidence)

            logger.info(f"Added evidence: {evidence.evidence_id} to task: {evidence.task_id}")
            return evidence

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding evidence: {e}")
            raise

    def get_task_stats(self, tenant_id: str) -> dict:
        """
        Get task statistics for a tenant
        الحصول على إحصائيات المهام للمستأجر
        """
        from datetime import timedelta

        now = datetime.utcnow()
        week_start = now - timedelta(days=now.weekday())
        week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)
        week_end = week_start + timedelta(days=7)

        # Total counts by status
        total = self.db.query(func.count(Task.task_id)).filter(Task.tenant_id == tenant_id).scalar()
        pending = self.db.query(func.count(Task.task_id)).filter(
            and_(Task.tenant_id == tenant_id, Task.status == "pending")
        ).scalar()
        in_progress = self.db.query(func.count(Task.task_id)).filter(
            and_(Task.tenant_id == tenant_id, Task.status == "in_progress")
        ).scalar()
        completed = self.db.query(func.count(Task.task_id)).filter(
            and_(Task.tenant_id == tenant_id, Task.status == "completed")
        ).scalar()

        # Overdue tasks
        overdue = self.db.query(func.count(Task.task_id)).filter(
            and_(
                Task.tenant_id == tenant_id,
                Task.status.notin_(["completed", "cancelled"]),
                Task.due_date < now,
            )
        ).scalar()

        # Week progress
        week_total = self.db.query(func.count(Task.task_id)).filter(
            and_(
                Task.tenant_id == tenant_id,
                Task.due_date >= week_start,
                Task.due_date < week_end,
            )
        ).scalar()

        week_completed = self.db.query(func.count(Task.task_id)).filter(
            and_(
                Task.tenant_id == tenant_id,
                Task.due_date >= week_start,
                Task.due_date < week_end,
                Task.status == "completed",
            )
        ).scalar()

        return {
            "total": total or 0,
            "pending": pending or 0,
            "in_progress": in_progress or 0,
            "completed": completed or 0,
            "overdue": overdue or 0,
            "week_progress": {
                "completed": week_completed or 0,
                "total": week_total or 0,
                "percentage": (
                    round(week_completed / week_total * 100)
                    if week_total > 0
                    else 0
                ),
            },
        }

    def _record_history(
        self,
        task_id: str,
        action: str,
        performed_by: str,
        old_status: Optional[str] = None,
        new_status: Optional[str] = None,
        changes: Optional[dict] = None,
        notes: Optional[str] = None,
    ) -> None:
        """
        Record a history entry for task changes
        تسجيل سجل التغييرات للمهمة
        """
        try:
            history = TaskHistory(
                task_id=task_id,
                action=action,
                old_status=old_status,
                new_status=new_status,
                performed_by=performed_by,
                changes=changes,
                notes=notes,
            )
            self.db.add(history)
            # Note: Not committing here as this is called within other transactions

        except Exception as e:
            logger.error(f"Error recording history for task {task_id}: {e}")
            # Don't raise, just log - history should not block main operations


class AsyncTaskRepository:
    """
    Async repository for Task database operations
    مستودع غير متزامن لعمليات قاعدة بيانات المهام
    """

    def __init__(self, db: AsyncSession):
        """Initialize async repository with database session"""
        self.db = db

    async def create_task(self, task: Task) -> Task:
        """Create a new task asynchronously"""
        try:
            self.db.add(task)
            await self.db.commit()
            await self.db.refresh(task)

            await self._record_history(
                task_id=task.task_id,
                action="created",
                new_status=task.status,
                performed_by=task.created_by,
            )

            logger.info(f"Created task: {task.task_id}")
            return task
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating task: {e}")
            raise

    async def get_task_by_id(self, task_id: str, tenant_id: str) -> Optional[Task]:
        """Get task by ID asynchronously"""
        result = await self.db.execute(
            select(Task)
            .options(selectinload(Task.evidence))
            .filter(
                and_(
                    Task.task_id == task_id,
                    Task.tenant_id == tenant_id,
                )
            )
        )
        return result.scalar_one_or_none()

    async def _record_history(
        self,
        task_id: str,
        action: str,
        performed_by: str,
        old_status: Optional[str] = None,
        new_status: Optional[str] = None,
        changes: Optional[dict] = None,
        notes: Optional[str] = None,
    ) -> None:
        """Record a history entry asynchronously"""
        try:
            history = TaskHistory(
                task_id=task_id,
                action=action,
                old_status=old_status,
                new_status=new_status,
                performed_by=performed_by,
                changes=changes,
                notes=notes,
            )
            self.db.add(history)

        except Exception as e:
            logger.error(f"Error recording history for task {task_id}: {e}")
