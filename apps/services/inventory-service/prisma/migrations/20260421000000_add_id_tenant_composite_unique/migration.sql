-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) for IDOR defense-in-depth
-- إضافة قيد فريد مركّب (id, tenant_id) لتعزيز عزل المستأجرين
--
-- Purpose: Expose the Prisma `id_tenantId` accessor so warehouse_manager.py
-- and application_tracker.py can do `find_unique`/`update`/`delete` with the
-- tenant bound atomically. These two modules are currently dormant (no
-- production endpoints wire them up) but their find_unique({"id": X})
-- patterns would be IDOR-prone once wired, so this migration plus the
-- accompanying signature-change refactor closes the gap pre-emptively.
--
-- Skipped:
--   * alert_settings — already UNIQUE on tenant_id (one row per tenant).
--   * batch_lots / input_applications / stock_movements / application_plans
--     — referenced by the Python code but NOT defined in schema.prisma.
--     The dependent modules need a schema addition before those tables
--     can exist; adding a composite index here would be a no-op DDL.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive constraint on already-unique id column — no row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_inventory_item_id_tenant" ON "inventory_items" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_inventory_movement_id_tenant" ON "inventory_movements" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_inventory_alert_id_tenant" ON "inventory_alerts" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_warehouse_id_tenant" ON "warehouses" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_zone_id_tenant" ON "zones" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_storage_location_id_tenant" ON "storage_locations" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_stock_transfer_id_tenant" ON "stock_transfers" ("id", "tenant_id");
