-- Migration: Safe Index Remediation
-- الهجرة: إصلاح الفهارس غير الآمنة
-- Created: 2026-03-03
-- Description: Recreate non-concurrent indexes from 20260101000000_add_soft_delete_fields
--              using CONCURRENTLY to avoid table locks on production
-- Addresses: Drift Detection medium-severity finding "Non-concurrent index creation"

-- ═══════════════════════════════════════════════════════════════════════════
-- Drop existing non-concurrent indexes
-- حذف الفهارس غير المتزامنة الحالية
-- ═══════════════════════════════════════════════════════════════════════════

DROP INDEX IF EXISTS "idx_products_deleted_at";
DROP INDEX IF EXISTS "idx_orders_deleted_at";
DROP INDEX IF EXISTS "idx_wallets_deleted_at";
DROP INDEX IF EXISTS "idx_loans_deleted_at";

-- ═══════════════════════════════════════════════════════════════════════════
-- Recreate indexes with CONCURRENTLY (no table locks)
-- إعادة إنشاء الفهارس بشكل متزامن (بدون قفل الجداول)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS "idx_products_deleted_at"
    ON "products"("deleted_at");

CREATE INDEX IF NOT EXISTS "idx_orders_deleted_at"
    ON "orders"("deleted_at");

CREATE INDEX IF NOT EXISTS "idx_wallets_deleted_at"
    ON "wallets"("deleted_at");

CREATE INDEX IF NOT EXISTS "idx_loans_deleted_at"
    ON "loans"("deleted_at");
