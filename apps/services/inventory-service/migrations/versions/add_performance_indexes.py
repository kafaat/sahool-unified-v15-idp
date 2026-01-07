"""
Add Performance Indexes to Inventory Tables

Creates optimized indexes for common query patterns:
- Low stock items filtering
- Expiry date tracking
- Movement date range queries
- SKU and barcode lookups
- Transaction party references

Revision ID: inv_0001_perf_indexes
Revises: None
Create Date: 2026-01-01
"""

import sqlalchemy as sa
from alembic import op

revision = "inv_0001_perf_indexes"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create performance indexes for inventory tables.
    """
    # -------------------------------------------------------------------------
    # Inventory Items Performance Indexes
    # -------------------------------------------------------------------------

    # Partial index for low stock items (WHERE current_stock <= reorder_level)
    # Used for: Low stock alerts and reorder suggestions
    op.execute(
        """
        CREATE INDEX idx_inventory_items_low_stock
        ON inventory_items (tenant_id, current_stock)
        WHERE current_stock <= reorder_level
    """
    )

    # Partial index for items with expiry dates
    # Used for: Expiry tracking and FIFO/FEFO inventory management
    op.execute(
        """
        CREATE INDEX idx_inventory_items_expiry
        ON inventory_items (expiry_date)
        WHERE has_expiry = true AND expiry_date IS NOT NULL
    """
    )

    # Composite index for SKU lookups within tenant
    # Used for: Item search by SKU (most common lookup pattern)
    op.create_index(
        "idx_inventory_items_sku_tenant",
        "inventory_items",
        ["tenant_id", "sku"],
    )

    # Partial index for barcode lookups (only when barcode exists)
    # Used for: Barcode scanning operations
    op.execute(
        """
        CREATE INDEX idx_inventory_items_barcode
        ON inventory_items (barcode)
        WHERE barcode IS NOT NULL
    """
    )

    # -------------------------------------------------------------------------
    # Inventory Movements Performance Indexes
    # -------------------------------------------------------------------------

    # Composite index for date range queries with descending order
    # Used for: Movement history, audit trails, recent activity
    op.create_index(
        "idx_inventory_movements_date_range",
        "inventory_movements",
        ["tenant_id", sa.text("movement_date DESC")],
    )

    # -------------------------------------------------------------------------
    # Inventory Transactions Performance Indexes
    # -------------------------------------------------------------------------

    # Partial index for party-related transactions
    # Used for: Customer/Supplier transaction history
    op.execute(
        """
        CREATE INDEX idx_inventory_transactions_party
        ON inventory_transactions (party_id)
        WHERE party_id IS NOT NULL
    """
    )


def downgrade() -> None:
    """
    Drop performance indexes for inventory tables.
    """
    # Drop inventory_transactions indexes
    op.drop_index("idx_inventory_transactions_party", table_name="inventory_transactions")

    # Drop inventory_movements indexes
    op.drop_index("idx_inventory_movements_date_range", table_name="inventory_movements")

    # Drop inventory_items indexes
    op.drop_index("idx_inventory_items_barcode", table_name="inventory_items")
    op.drop_index("idx_inventory_items_sku_tenant", table_name="inventory_items")
    op.drop_index("idx_inventory_items_expiry", table_name="inventory_items")
    op.drop_index("idx_inventory_items_low_stock", table_name="inventory_items")
