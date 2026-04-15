"""
Conftest for task-service tests.
Provides mock 'database' module so that src.models and src.database
can import Base, TenantMixin, TimestampMixin without the shared package.
Also sets up an in-memory SQLite database for integration-style tests.
"""

import os
import sys
import types

# Add service root to path for src imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

_tests_dir = os.path.dirname(os.path.abspath(__file__))
_service_dir = os.path.normpath(os.path.join(_tests_dir, ".."))

# IMPORTANT: shared database path must be FIRST so that `from database import Base`
# resolves to the shared database package, not src/database.py
_shared_db_path = os.path.normpath(os.path.join(_service_dir, "..", "shared"))
# Remove if already in path, then re-insert at position 0
if _shared_db_path in sys.path:
    sys.path.remove(_shared_db_path)
sys.path.insert(0, _shared_db_path)

from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, String, Text, TypeDecorator, create_engine, event
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

# ---------------------------------------------------------------------------
# 1. Fake 'database' module with real SQLAlchemy Base + mixins
# ---------------------------------------------------------------------------

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

# Inject before anything from src is imported
sys.modules["database"] = _fake_database


# ---------------------------------------------------------------------------
# 2. Patch PostgreSQL-only types so SQLite works
# ---------------------------------------------------------------------------
# ARRAY(Text) -> JSON (stored as JSON list in SQLite)
import sqlalchemy.dialects.postgresql as _pg

_orig_array = _pg.ARRAY  # noqa: N816


class _FakeARRAY(TypeDecorator):
    """Store ARRAY columns as JSON in SQLite."""

    impl = JSON
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__()


_pg.ARRAY = _FakeARRAY

# JSONB -> JSON for SQLite
_pg.JSONB = JSON

# UUID -> String for SQLite
_orig_uuid = _pg.UUID  # noqa: N816


class _FakeUUID(TypeDecorator):
    """Store UUID columns as String in SQLite."""

    impl = String(36)
    cache_ok = True

    def __init__(self, *args, **kwargs):
        super().__init__()


_pg.UUID = _FakeUUID

# Register Python uuid.UUID adapter for sqlite3 so it can bind UUID values
import sqlite3
import uuid as _uuid

sqlite3.register_adapter(_uuid.UUID, lambda u: str(u))
sqlite3.register_converter("UUID", lambda b: _uuid.UUID(b.decode()))
