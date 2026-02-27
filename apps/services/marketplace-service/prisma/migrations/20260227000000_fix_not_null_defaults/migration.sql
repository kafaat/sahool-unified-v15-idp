-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Fix NOT NULL columns without DEFAULT values
-- إصلاح أعمدة NOT NULL بدون قيم افتراضية
-- Purpose: Replace 'default' sentinel with 'unassigned' and ensure all NOT NULL
--          tenant_id columns have a safe DEFAULT for direct SQL inserts.
-- Drift Report: 7d5dc4c6-bc6
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Update existing 'default' sentinel values to 'unassigned'
-- الخطوة 1: تحديث القيم الافتراضية 'default' إلى 'unassigned'
UPDATE "products"          SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "orders"            SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "order_items"       SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "wallets"           SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "transactions"      SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "loans"             SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "credit_events"     SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "escrows"           SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "scheduled_payments" SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "wallet_audit_logs" SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "product_reviews"   SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';
UPDATE "review_responses"  SET "tenant_id" = 'unassigned' WHERE "tenant_id" = 'default';

-- Step 2: Set DEFAULT to 'unassigned' instead of keeping 'default'
-- الخطوة 2: تعيين القيمة الافتراضية 'unassigned'
ALTER TABLE "products"          ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "orders"            ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "order_items"       ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "wallets"           ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "transactions"      ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "loans"             ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "credit_events"     ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "escrows"           ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "scheduled_payments" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "wallet_audit_logs" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "product_reviews"   ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "review_responses"  ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- ═══════════════════════════════════════════════════════════════════════════════
-- Note on non-concurrent indexes from initial migrations:
-- idx_products_deleted_at, idx_orders_deleted_at, idx_audit_tenant_created
-- were created on low-volume tables during maintenance windows.
-- All tenant isolation indexes (20260225000000) already use CONCURRENTLY.
-- ═══════════════════════════════════════════════════════════════════════════════
