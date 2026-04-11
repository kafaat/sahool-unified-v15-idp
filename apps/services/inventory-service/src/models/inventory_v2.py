"""
Inventory v2 ORM models for Wave 2 CRUD endpoints.
نماذج المخزون v2 لنقاط نهاية CRUD في الموجة الثانية.

These models map to the ``inventory_items_v2`` and ``inventory_transactions_v2``
tables introduced by ``migrations/20260410_inventory_tables.sql``. They are kept
in a dedicated module so the legacy ``inventory_items`` tables used by the
analytics layer remain untouched.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .inventory import Base


class InventoryItemV2(Base):
    """Wave 2 inventory item with optimistic locking support."""

    __tablename__ = "inventory_items_v2"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ar: Mapped[str | None] = mapped_column(String(200), nullable=True)
    sku: Mapped[str | None] = mapped_column(String(120), nullable=True)
    category: Mapped[str | None] = mapped_column(String(120), nullable=True, index=True)

    quantity: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False, default=Decimal("0"))
    unit: Mapped[str] = mapped_column(String(32), nullable=False)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)
    currency: Mapped[str] = mapped_column(String(8), default="SAR")
    low_stock_threshold: Mapped[Decimal | None] = mapped_column(Numeric(14, 4), nullable=True)

    supplier_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    location: Mapped[str | None] = mapped_column(String(200), nullable=True)

    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )

    # Optimistic concurrency control - قفل تفاؤلي
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    transactions = relationship("InventoryTransactionV2", back_populates="item", cascade="all,delete-orphan")

    __table_args__ = (
        Index("idx_inventory_items_v2_tenant_category_wave2", "tenant_id", "category"),
        Index("idx_inventory_items_v2_tenant_wave2", "tenant_id", "is_deleted"),
    )


class InventoryTransactionV2(Base):
    """Wave 2 inventory movement / adjustment log."""

    __tablename__ = "inventory_transactions_v2"

    id: Mapped[uuid.UUID] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    item_id: Mapped[str] = mapped_column(String(36), ForeignKey("inventory_items_v2.id"), nullable=False)

    transaction_type: Mapped[str] = mapped_column(String(32), nullable=False)
    quantity_delta: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    quantity_after: Mapped[Decimal] = mapped_column(Numeric(14, 4), nullable=False)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    performed_by: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    item = relationship("InventoryItemV2", back_populates="transactions")

    __table_args__ = (
        Index(
            "idx_inventory_tx_v2_tenant_item_wave2",
            "tenant_id",
            "item_id",
            "created_at",
        ),
    )
