-- SAHOOL Inventory Service - CRUD tables with optimistic locking
-- جداول المخزون مع القفل التفاؤلي
--
-- Wave 2 migration: introduces a simpler inventory schema used by the
-- /api/v1/inventory CRUD endpoints. These tables are suffixed _v2 to avoid
-- collisions with the legacy SQLAlchemy-managed `inventory_items` /
-- `inventory_transactions` tables used by analytics workflows.
--
-- Do NOT execute as part of CI; apply manually via alembic/psql when ready.

BEGIN;

CREATE TABLE IF NOT EXISTS inventory_items_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name TEXT NOT NULL,
    name_ar TEXT,
    sku TEXT,
    category TEXT,
    quantity NUMERIC(14,4) NOT NULL DEFAULT 0,
    unit TEXT NOT NULL,
    unit_price NUMERIC(14,4),
    currency TEXT DEFAULT 'SAR',
    low_stock_threshold NUMERIC(14,4),
    supplier_id UUID,
    location TEXT,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_inventory_items_v2_tenant_sku
    ON inventory_items_v2 (tenant_id, sku)
    WHERE sku IS NOT NULL AND is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_inventory_items_v2_tenant
    ON inventory_items_v2 (tenant_id)
    WHERE is_deleted = FALSE;

CREATE INDEX IF NOT EXISTS idx_inventory_items_v2_tenant_category
    ON inventory_items_v2 (tenant_id, category)
    WHERE is_deleted = FALSE;

CREATE TABLE IF NOT EXISTS inventory_transactions_v2 (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    item_id UUID NOT NULL REFERENCES inventory_items_v2(id),
    transaction_type TEXT NOT NULL, -- purchase|sale|adjustment|transfer|consumption
    quantity_delta NUMERIC(14,4) NOT NULL,
    quantity_after NUMERIC(14,4) NOT NULL,
    reason TEXT,
    performed_by UUID,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_inventory_tx_v2_tenant_item
    ON inventory_transactions_v2 (tenant_id, item_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_inventory_tx_v2_tenant_created
    ON inventory_transactions_v2 (tenant_id, created_at DESC);

COMMIT;
