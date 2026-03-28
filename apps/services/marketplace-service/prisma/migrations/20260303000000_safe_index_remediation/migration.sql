-- Migration: Safe Index Remediation
-- الهجرة: إصلاح الفهارس غير الآمنة
-- Created: 2026-03-03
-- Description: Recreate indexes from 20260101000000_add_soft_delete_fields
--              using standard CREATE INDEX (runs inside Prisma transaction wrapper)
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
-- Recreate indexes (standard CREATE INDEX, may briefly lock table)
-- إعادة إنشاء الفهارس (قد يتم قفل الجدول لفترة وجيزة أثناء الإنشاء)
-- ═══════════════════════════════════════════════════════════════════════════

CREATE INDEX IF NOT EXISTS "idx_products_deleted_at"
    ON "products"("deleted_at");

CREATE INDEX IF NOT EXISTS "idx_orders_deleted_at"
    ON "orders"("deleted_at");

CREATE INDEX IF NOT EXISTS "idx_wallets_deleted_at"
    ON "wallets"("deleted_at");

CREATE INDEX IF NOT EXISTS "idx_loans_deleted_at"
    ON "loans"("deleted_at");
