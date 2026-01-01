"""
Inventory Database Models
نماذج قاعدة بيانات المخزون
"""

from datetime import datetime, date
from decimal import Decimal
from enum import Enum
from typing import Optional
import uuid

from sqlalchemy import (
    Column,
    String,
    Float,
    Integer,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Text,
    Numeric,
    Enum as SQLEnum,
    Index,
    func,
)
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column, DeclarativeBase
from sqlalchemy.ext.declarative import declared_attr


# Define base classes locally for Docker compatibility
class Base(DeclarativeBase):
    """Base class for all database models"""

    pass


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
        return mapped_column(String(50), nullable=False, index=True)


class TenantEntity(Base, TimestampMixin, TenantMixin):
    """Base entity with tenant support"""

    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )


class MovementType(str, Enum):
    """Types of inventory movements"""

    RECEIPT = "receipt"  # Receiving from supplier
    ISSUE = "issue"  # Issuing to field/operation
    ADJUSTMENT = "adjustment"  # Stock adjustment
    TRANSFER = "transfer"  # Transfer between warehouses
    RETURN = "return"  # Return from field
    WRITE_OFF = "write_off"  # Damaged/expired write-off


class TransactionType(str, Enum):
    """Types of inventory transactions"""

    PURCHASE = "purchase"
    SALE = "sale"
    USE = "use"  # Used in farming operation
    WASTE = "waste"  # Damaged/expired
    RETURN = "return"


class UnitOfMeasure(str, Enum):
    """Standard units of measure"""

    KG = "kg"
    LITER = "liter"
    PIECE = "piece"
    BAG = "bag"
    BOX = "box"
    BOTTLE = "bottle"


class ItemCategory(Base, TimestampMixin):
    """Item categories (fertilizer, pesticide, seed, etc.)"""

    __tablename__ = "inventory_categories"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )

    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    items = relationship("InventoryItem", back_populates="category")


class Warehouse(TenantEntity):
    """Warehouse/storage locations"""

    __tablename__ = "inventory_warehouses"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    capacity: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    items = relationship("InventoryItem", back_populates="warehouse")
    movements = relationship(
        "InventoryMovement",
        foreign_keys="InventoryMovement.warehouse_id",
        back_populates="warehouse",
    )


class Supplier(TenantEntity):
    """Suppliers for inventory items"""

    __tablename__ = "inventory_suppliers"

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    code: Mapped[str] = mapped_column(String(50), nullable=False)
    contact_person: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lead_time_days: Mapped[int] = mapped_column(Integer, default=7)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    items = relationship("InventoryItem", back_populates="supplier")


class InventoryItem(TenantEntity):
    """Main inventory item master data"""

    __tablename__ = "inventory_items"

    # Basic info
    name_en: Mapped[str] = mapped_column(String(200), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(200), nullable=False)
    sku: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    barcode: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True, index=True
    )

    # Category and classification
    category_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_categories.id"), nullable=False
    )

    # Storage
    warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_warehouses.id"), nullable=True
    )

    # Supplier
    supplier_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_suppliers.id"), nullable=True
    )

    # Stock levels
    current_stock: Mapped[float] = mapped_column(Float, default=0.0)
    reserved_stock: Mapped[float] = mapped_column(Float, default=0.0)
    available_stock: Mapped[float] = mapped_column(Float, default=0.0)
    reorder_level: Mapped[float] = mapped_column(Float, default=0.0)
    reorder_quantity: Mapped[float] = mapped_column(Float, default=0.0)

    # Unit and measurement
    unit_of_measure: Mapped[str] = mapped_column(
        SQLEnum(UnitOfMeasure, name="unit_of_measure"), default=UnitOfMeasure.KG
    )

    # Cost and valuation
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), default=Decimal("0.00"))
    average_cost: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00")
    )
    total_value: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00")
    )

    # Expiry tracking
    has_expiry: Mapped[bool] = mapped_column(Boolean, default=False)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    shelf_life_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Additional attributes
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    category = relationship("ItemCategory", back_populates="items")
    warehouse = relationship("Warehouse", back_populates="items")
    supplier = relationship("Supplier", back_populates="items")
    movements = relationship("InventoryMovement", back_populates="item")
    transactions = relationship("InventoryTransaction", back_populates="item")

    # Indexes for performance
    __table_args__ = (
        # Existing indexes
        Index("idx_inventory_items_category", "category_id"),
        Index("idx_inventory_items_warehouse", "warehouse_id"),
        # Performance indexes
        # Composite index for SKU lookups within tenant
        Index("idx_inventory_items_sku_tenant", "tenant_id", "sku"),
        # Partial index for low stock items (requires PostgreSQL)
        # WHERE current_stock <= reorder_level
        Index(
            "idx_inventory_items_low_stock",
            "tenant_id",
            "current_stock",
            postgresql_where=sa.text("current_stock <= reorder_level"),
        ),
        # Partial index for items with expiry dates
        # WHERE has_expiry = true AND expiry_date IS NOT NULL
        Index(
            "idx_inventory_items_expiry",
            "expiry_date",
            postgresql_where=sa.text("has_expiry = true AND expiry_date IS NOT NULL"),
        ),
        # Partial index for barcode lookups (only when barcode exists)
        # WHERE barcode IS NOT NULL
        Index(
            "idx_inventory_items_barcode",
            "barcode",
            postgresql_where=sa.text("barcode IS NOT NULL"),
        ),
    )


class InventoryMovement(TenantEntity):
    """
    Track all inventory movements (receipts, issues, transfers, adjustments)
    حركات المخزون (استلام، صرف، تحويل، تعديل)
    """

    __tablename__ = "inventory_movements"

    # Movement details
    movement_type: Mapped[str] = mapped_column(
        SQLEnum(MovementType, name="movement_type"), nullable=False
    )

    movement_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    reference_no: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Item and warehouse
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False
    )

    warehouse_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_warehouses.id"), nullable=False
    )

    # For transfers
    to_warehouse_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_warehouses.id"), nullable=True
    )

    # Quantity and cost
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    total_cost: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    # Field/operation reference (for issues)
    field_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    crop_season_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    operation_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Additional info
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    item = relationship("InventoryItem", back_populates="movements")
    warehouse = relationship(
        "Warehouse", foreign_keys=[warehouse_id], back_populates="movements"
    )
    to_warehouse = relationship("Warehouse", foreign_keys=[to_warehouse_id])

    # Indexes
    __table_args__ = (
        Index("idx_inventory_movements_tenant_date", "tenant_id", "movement_date"),
        Index("idx_inventory_movements_item", "item_id"),
        Index("idx_inventory_movements_field", "field_id"),
        # Performance index for date range queries with descending order
        # Used for: Movement history, audit trails, recent activity
        Index(
            "idx_inventory_movements_date_range",
            "tenant_id",
            sa.text("movement_date DESC"),
        ),
    )


class InventoryTransaction(TenantEntity):
    """
    Financial transactions for inventory (purchases, sales, usage valuation)
    المعاملات المالية للمخزون
    """

    __tablename__ = "inventory_transactions"

    # Transaction details
    transaction_type: Mapped[str] = mapped_column(
        SQLEnum(TransactionType, name="transaction_type"), nullable=False
    )

    transaction_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    reference_no: Mapped[str] = mapped_column(String(100), nullable=False, index=True)

    # Item
    item_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("inventory_items.id"), nullable=False
    )

    # Quantity and amount
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(15, 2), nullable=False)

    # Additional costs (shipping, tax, etc.)
    additional_costs: Mapped[Decimal] = mapped_column(
        Numeric(15, 2), default=Decimal("0.00")
    )

    # Field/crop reference
    field_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    crop_season_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Customer/Supplier reference
    party_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    party_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    item = relationship("InventoryItem", back_populates="transactions")

    # Indexes
    __table_args__ = (
        Index(
            "idx_inventory_transactions_tenant_date", "tenant_id", "transaction_date"
        ),
        Index("idx_inventory_transactions_item", "item_id"),
        Index("idx_inventory_transactions_field", "field_id"),
        # Performance index for party-related transactions (partial index)
        # WHERE party_id IS NOT NULL
        # Used for: Customer/Supplier transaction history
        Index(
            "idx_inventory_transactions_party",
            "party_id",
            postgresql_where=sa.text("party_id IS NOT NULL"),
        ),
    )
