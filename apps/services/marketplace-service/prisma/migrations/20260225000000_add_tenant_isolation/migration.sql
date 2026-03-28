-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add tenant_id to marketplace models missing tenant isolation
-- إضافة معرف المستأجر لجداول السوق التي تفتقر لعزل المستأجر
-- Purpose: Multi-tenant isolation (drift fix)
-- Note: SellerProfile and BuyerProfile already have tenant_id
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Add tenant_id columns with safe DEFAULT for existing rows
-- الخطوة 1: إضافة أعمدة tenant_id مع قيمة افتراضية آمنة

ALTER TABLE "products" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "orders" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "order_items" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "wallets" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "transactions" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "loans" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "credit_events" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "escrows" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "scheduled_payments" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "wallet_audit_logs" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "product_reviews" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "review_responses" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';

-- Step 2: Create tenant isolation indexes
-- الخطوة 3: إنشاء فهارس عزل المستأجر

CREATE INDEX IF NOT EXISTS "idx_product_tenant" ON "products" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_product_tenant_status" ON "products" ("tenant_id", "status");
CREATE INDEX IF NOT EXISTS "idx_order_tenant" ON "orders" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_order_tenant_status" ON "orders" ("tenant_id", "status");
CREATE INDEX IF NOT EXISTS "idx_order_item_tenant" ON "order_items" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_wallet_tenant" ON "wallets" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_transaction_tenant" ON "transactions" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_loan_tenant" ON "loans" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_credit_event_tenant" ON "credit_events" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_escrow_tenant" ON "escrows" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_scheduled_payment_tenant" ON "scheduled_payments" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_wallet_audit_tenant" ON "wallet_audit_logs" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_review_tenant" ON "product_reviews" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_review_response_tenant" ON "review_responses" ("tenant_id");
