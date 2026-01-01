"""
Base Models and Mixins
النماذج الأساسية والمزيجات
"""

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Column, DateTime, String, Boolean, func, event
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models"""

    # Generate __tablename__ automatically from class name
    @declared_attr.directive
    def __tablename__(cls) -> str:
        # Convert CamelCase to snake_case
        name = cls.__name__
        return "".join(["_" + c.lower() if c.isupper() else c for c in name]).lstrip(
            "_"
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary"""
        return {
            column.name: getattr(self, column.name) for column in self.__table__.columns
        }

    def __repr__(self) -> str:
        """String representation"""
        pk = getattr(self, "id", None)
        return f"<{self.__class__.__name__}(id={pk})>"


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class TenantMixin:
    """Mixin for multi-tenant support"""

    @declared_attr
    def tenant_id(cls) -> Mapped[str]:
        return mapped_column(
            String(50),
            nullable=False,
            index=True,
        )


class SoftDeleteMixin:
    """Mixin for soft delete support"""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


class UUIDMixin:
    """Mixin for UUID primary key"""

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )


class AuditMixin(TimestampMixin):
    """Mixin for audit trail"""

    created_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    updated_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )


# =============================================================================
# Common Models (can be imported by any service)
# =============================================================================


class BaseEntity(Base, UUIDMixin, TimestampMixin):
    """Base entity with UUID and timestamps"""

    __abstract__ = True


class TenantEntity(Base, UUIDMixin, TimestampMixin, TenantMixin):
    """Base entity with tenant support"""

    __abstract__ = True


class AuditedEntity(Base, UUIDMixin, AuditMixin, TenantMixin):
    """Base entity with full audit trail"""

    __abstract__ = True
