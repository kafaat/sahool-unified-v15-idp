"""
SAHOOL Saga Models
===================
نماذج بيانات Saga للتخزين المستدام

SQLAlchemy models for persisting saga execution state.
Enables crash recovery — if the orchestrator dies mid-saga,
a new instance can pick up where it left off.
"""

from __future__ import annotations

import enum
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    Enum,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


class SagaState(str, enum.Enum):
    """Saga execution state."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"


class StepState(str, enum.Enum):
    """Individual step state."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"
    FAILED = "failed"
    SKIPPED = "skipped"


class SagaExecution(Base):
    """
    Persistent record of a saga execution.

    Each saga run creates one SagaExecution with multiple
    SagaStepRecords tracking individual step progress.
    """

    __tablename__ = "saga_executions"

    id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    saga_name: Mapped[str] = mapped_column(
        String(200), nullable=False, comment="Saga definition name"
    )
    idempotency_key: Mapped[str] = mapped_column(
        String(200), nullable=False, unique=True,
        comment="Idempotency key to prevent duplicate execution",
    )
    state: Mapped[str] = mapped_column(
        Enum(SagaState, native_enum=False, length=20),
        nullable=False,
        default=SagaState.PENDING,
    )
    context_json: Mapped[str] = mapped_column(
        Text, nullable=False, default="{}",
        comment="Saga context as JSON (input data + step results)",
    )
    current_step: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
        comment="Current step index (0-based)",
    )
    total_steps: Mapped[int] = mapped_column(
        Integer, nullable=False,
    )
    tenant_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True,
    )
    correlation_id: Mapped[str] = mapped_column(
        String(100), nullable=False, default=lambda: str(uuid4()),
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False,
        default=lambda: datetime.now(UTC),
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    __table_args__ = (
        Index("ix_saga_state", "state"),
        Index("ix_saga_tenant", "tenant_id"),
        Index("ix_saga_idempotency", "idempotency_key", unique=True),
    )


class SagaStepRecord(Base):
    """
    Persistent record of a single saga step execution.
    """

    __tablename__ = "saga_step_records"

    id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid4()),
    )
    saga_id: Mapped[str] = mapped_column(
        PGUUID(as_uuid=False), nullable=False,
        comment="FK to saga_executions.id",
    )
    step_index: Mapped[int] = mapped_column(
        Integer, nullable=False,
    )
    step_name: Mapped[str] = mapped_column(
        String(200), nullable=False,
    )
    state: Mapped[str] = mapped_column(
        Enum(StepState, native_enum=False, length=20),
        nullable=False,
        default=StepState.PENDING,
    )
    result_json: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Step result as JSON",
    )
    error_message: Mapped[str | None] = mapped_column(
        Text, nullable=True,
    )
    compensation_error: Mapped[str | None] = mapped_column(
        Text, nullable=True,
        comment="Error during compensation (if any)",
    )
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0,
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True,
    )

    __table_args__ = (
        Index("ix_step_saga_id", "saga_id"),
        Index("ix_step_saga_index", "saga_id", "step_index"),
    )
