-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Drift Detection Fix (Report 5c6dd891-251)
-- إصلاح كشف الانحراف - تقرير 5c6dd891-251
-- Purpose: Resolve critical NOT NULL without DEFAULT and risky migration patterns
-- Service: marketplace-service
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Critical Fix 1: Ensure all tenant_id columns have safe DEFAULT
-- Migration 20260225 set DEFAULT 'default'; migration 20260227 changed to
-- 'unassigned'. Re-affirm to close drift scanner gap.
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE "products" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "orders" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "order_items" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "wallets" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "transactions" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "loans" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "credit_events" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "escrows" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "scheduled_payments" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "wallet_audit_logs" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "product_reviews" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "review_responses" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "seller_profiles" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "buyer_profiles" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- ─────────────────────────────────────────────────────────────────────────────
-- Critical Fix 2: Ensure all updatedAt columns have DEFAULT now()
-- Prisma @updatedAt does not generate SQL-level DEFAULT.
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE "products" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "orders" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "wallets" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "loans" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "scheduled_payments" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "seller_profiles" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "buyer_profiles" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "product_reviews" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "review_responses" ALTER COLUMN "updated_at" SET DEFAULT now();

-- ─────────────────────────────────────────────────────────────────────────────
-- Critical Fix 3: audit_logs NOT NULL columns need safe defaults
-- The audit_logs CREATE TABLE (20260101_add_audit_logs) has several NOT NULL
-- columns without DEFAULT. Add defaults for direct SQL insert safety.
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE "audit_logs" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';
ALTER TABLE "audit_logs" ALTER COLUMN "actor_type" SET DEFAULT 'system';
ALTER TABLE "audit_logs" ALTER COLUMN "action" SET DEFAULT 'unknown';
ALTER TABLE "audit_logs" ALTER COLUMN "category" SET DEFAULT 'general';
ALTER TABLE "audit_logs" ALTER COLUMN "severity" SET DEFAULT 'info';
ALTER TABLE "audit_logs" ALTER COLUMN "resource_type" SET DEFAULT 'unknown';
ALTER TABLE "audit_logs" ALTER COLUMN "resource_id" SET DEFAULT 'unknown';
ALTER TABLE "audit_logs" ALTER COLUMN "correlation_id" SET DEFAULT gen_random_uuid()::text;

-- ─────────────────────────────────────────────────────────────────────────────
-- Medium: Non-concurrent index creation (Acknowledged)
-- فهارس غير متزامنة (مقبولة)
--
-- 1. idx_products_deleted_at, idx_orders_deleted_at, idx_wallets_deleted_at,
--    idx_loans_deleted_at (from 20260101000000_add_soft_delete_fields):
--    Created during scheduled maintenance window with low traffic. Acceptable.
--
-- 2. idx_audit_tenant_created, idx_audit_actor_created, idx_audit_resource,
--    idx_audit_correlation, idx_audit_category_created, idx_audit_severity,
--    idx_audit_action (from 20260101_add_audit_logs):
--    Created during initial table creation (CREATE TABLE IF NOT EXISTS).
--    Table was empty at creation time. Acceptable.
--
-- All subsequent migrations use CREATE INDEX CONCURRENTLY.
-- ═══════════════════════════════════════════════════════════════════════════════
