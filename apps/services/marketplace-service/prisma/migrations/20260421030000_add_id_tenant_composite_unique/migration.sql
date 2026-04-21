-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) to every marketplace model
-- قيد فريد مركّب (id, tenant_id) لجميع نماذج السوق والخدمات المالية
--
-- Context: marketplace-service was flagged as "Phase 3 — needs design
-- decision" in the original IDOR audit (commit e9929b57). The design
-- decision is now made: wallets / loans / escrows / orders / reviews /
-- profiles are all tenant-stamped rows. This migration enables the
-- Prisma `id_tenantId` composite-key accessor so the fintech + reviews
-- + profiles refactor (commits 1c0ce119, 13857cf1, and the pending
-- commit) can bind tenant atomically on every `findUnique` / `update` /
-- `delete`.
--
-- IdempotencyKey has its own composite in migration 20260421020000.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive on already-unique id columns — no existing row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_product_id_tenant"            ON "products"           ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_order_id_tenant"              ON "orders"             ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_order_item_id_tenant"         ON "order_items"        ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_wallet_id_tenant"             ON "wallets"            ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_transaction_id_tenant"        ON "transactions"       ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_loan_id_tenant"               ON "loans"              ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_credit_event_id_tenant"       ON "credit_events"      ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_escrow_id_tenant"             ON "escrows"            ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_scheduled_payment_id_tenant"  ON "scheduled_payments" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_wallet_audit_log_id_tenant"   ON "wallet_audit_logs"  ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_seller_profile_id_tenant"     ON "seller_profiles"    ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_buyer_profile_id_tenant"      ON "buyer_profiles"     ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_product_review_id_tenant"     ON "product_reviews"    ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_review_response_id_tenant"    ON "review_responses"   ("id", "tenant_id");
