"""
Conftest for task-service tests.
Provides mock 'database' module so that src.models and src.database
can import Base, TenantMixin, TimestampMixin without the shared package.
"""

import sys
import types
from datetime import UTC, datetime
from unittest.mock import MagicMock

from sqlalchemy import DateTime, String, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


# Build a fake 'database' module with real SQLAlchemy Base and mixins
_fake_database = types.ModuleType("database")


class _Base(DeclarativeBase):
    pass


class _TimestampMixin:
    """Mixin providing created_at / updated_at columns."""

    created_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=True,
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=True,
    )


class _TenantMixin:
    """Mixin providing tenant_id column."""

    tenant_id: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True,
    )


_fake_database.Base = _Base
_fake_database.TimestampMixin = _TimestampMixin
_fake_database.TenantMixin = _TenantMixin

# Inject into sys.modules before anything imports it
sys.modules["database"] = _fake_database
