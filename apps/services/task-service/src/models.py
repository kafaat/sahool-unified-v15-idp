"""
SQLAlchemy Database Models for Task Service
نماذج قاعدة البيانات لخدمة المهام

This file defines the database schema for tasks and evidence.
يحدد هذا الملف مخطط قاعدة البيانات للمهام والأدلة.
"""

import os
import sys
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

# Import shared database base classes
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "shared"))
from database.base import Base, TenantMixin, TimestampMixin


class Task(Base, TimestampMixin, TenantMixin):
    """
    Task model - نموذج المهمة

    Represents an agricultural task with full tracking and astronomical integration.
    يمثل مهمة زراعية مع التتبع الكامل والتكامل الفلكي.
    """

    __tablename__ = "tasks"

    # Primary Key
    task_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        index=True,
    )

    # Core Fields - الحقول الأساسية
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    title_ar: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    description_ar: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Task Attributes - سمات المهمة
    task_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )
    priority: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True,
        default="pending",
    )

    # Assignment & Location - التعيين والموقع
    field_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    zone_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    assigned_to: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )
    created_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Scheduling - الجدولة
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    scheduled_time: Mapped[str | None] = mapped_column(
        String(10),  # HH:MM format
        nullable=True,
    )
    estimated_duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    actual_duration_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Completion - الإنجاز
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    completion_notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Metadata - البيانات الوصفية
    metadata: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        default={},
    )

    # Astronomical Fields - الحقول الفلكية
    astronomical_score: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )
    moon_phase_at_due_date: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    lunar_mansion_at_due_date: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    optimal_time_of_day: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    suggested_by_calendar: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    astronomical_recommendation: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
    )
    astronomical_warnings: Mapped[list | None] = mapped_column(
        ARRAY(Text),
        nullable=True,
        default=[],
    )

    # Relationships - العلاقات
    evidence: Mapped[list["TaskEvidence"]] = relationship(
        "TaskEvidence",
        back_populates="task",
        cascade="all, delete-orphan",
        lazy="joined",
    )

    # Indexes for performance - الفهارس لتحسين الأداء
    __table_args__ = (
        Index("idx_tasks_tenant_status", "tenant_id", "status"),
        Index("idx_tasks_assigned_status", "assigned_to", "status"),
        Index("idx_tasks_field_status", "field_id", "status"),
        Index("idx_tasks_due_date_status", "due_date", "status"),
    )

    def __repr__(self):
        return f"<Task(task_id={self.task_id}, title={self.title}, status={self.status})>"


class TaskEvidence(Base, TimestampMixin):
    """
    Task Evidence model - نموذج أدلة المهمة

    Represents evidence attached to a task (photos, notes, voice recordings, measurements).
    يمثل الأدلة المرفقة بالمهمة (صور، ملاحظات، تسجيلات صوتية، قياسات).
    """

    __tablename__ = "task_evidence"

    # Primary Key
    evidence_id: Mapped[str] = mapped_column(
        String(50),
        primary_key=True,
        index=True,
    )

    # Foreign Key to Task
    task_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Evidence Details - تفاصيل الدليل
    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="photo, note, voice, measurement",
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        comment="URL for media or text content for notes",
    )
    captured_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )

    # Location (stored as JSONB for flexibility)
    location: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="GPS coordinates: {lat: float, lon: float}",
    )

    # Relationship back to Task
    task: Mapped["Task"] = relationship(
        "Task",
        back_populates="evidence",
    )

    # Index for performance
    __table_args__ = (
        Index("idx_evidence_task_id", "task_id"),
        Index("idx_evidence_type", "type"),
    )

    def __repr__(self):
        return f"<TaskEvidence(evidence_id={self.evidence_id}, task_id={self.task_id}, type={self.type})>"


class TaskHistory(Base, TimestampMixin):
    """
    Task History model - نموذج سجل المهمة

    Tracks all status changes and updates to tasks for audit trail.
    يتتبع جميع تغييرات الحالة والتحديثات على المهام لسجل المراجعة.
    """

    __tablename__ = "task_history"

    # Primary Key
    history_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # Foreign Key to Task
    task_id: Mapped[str] = mapped_column(
        String(50),
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Change Tracking - تتبع التغييرات
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="created, updated, started, completed, cancelled, assigned",
    )
    old_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )
    new_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    # User & Context
    performed_by: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    changes: Mapped[dict | None] = mapped_column(
        JSONB,
        nullable=True,
        comment="Detailed changes in JSON format",
    )
    notes: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    # Index for audit queries
    __table_args__ = (
        Index("idx_history_task_id", "task_id"),
        Index("idx_history_action", "action"),
        Index("idx_history_created_at", "created_at"),
    )

    def __repr__(self):
        return f"<TaskHistory(task_id={self.task_id}, action={self.action}, performed_by={self.performed_by})>"
