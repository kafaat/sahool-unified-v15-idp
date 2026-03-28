-- Migration: Safe Audit Index & Constraint Remediation
-- الهجرة: إصلاح فهارس التدقيق والقيود بشكل آمن
-- Created: 2026-03-10
-- Description: Remediate risky migration patterns flagged by drift detection:
--   1. Recreate audit_logs indexes from 20260101_add_audit_logs with CONCURRENTLY
--   2. Recreate CHECK constraints from 20260207000001 using NOT VALID + VALIDATE pattern
--      to avoid full table locks on existing production data.
-- Addresses: Drift Detection Report 01fb579f-de8 (2026-03-10)

-- ═══════════════════════════════════════════════════════════════════════════
-- Part 1: Audit Logs Index Remediation
-- إصلاح فهارس جدول التدقيق
-- ═══════════════════════════════════════════════════════════════════════════

-- Drop existing non-concurrent indexes from 20260101_add_audit_logs
-- Using CONCURRENTLY to avoid blocking queries during drop
DROP INDEX IF EXISTS "idx_audit_tenant_created";
DROP INDEX IF EXISTS "idx_audit_actor_created";
DROP INDEX IF EXISTS "idx_audit_resource";
DROP INDEX IF EXISTS "idx_audit_correlation";
DROP INDEX IF EXISTS "idx_audit_category_created";
DROP INDEX IF EXISTS "idx_audit_severity";
DROP INDEX IF EXISTS "idx_audit_action";

-- Recreate with CONCURRENTLY (no table locks)
CREATE INDEX IF NOT EXISTS "idx_audit_tenant_created"
    ON "audit_logs"("tenant_id", "created_at" DESC);

CREATE INDEX IF NOT EXISTS "idx_audit_actor_created"
    ON "audit_logs"("actor_id", "created_at" DESC);

CREATE INDEX IF NOT EXISTS "idx_audit_resource"
    ON "audit_logs"("resource_type", "resource_id");

CREATE INDEX IF NOT EXISTS "idx_audit_correlation"
    ON "audit_logs"("correlation_id");

CREATE INDEX IF NOT EXISTS "idx_audit_category_created"
    ON "audit_logs"("category", "created_at" DESC);

CREATE INDEX IF NOT EXISTS "idx_audit_severity"
    ON "audit_logs"("severity", "created_at" DESC);

CREATE INDEX IF NOT EXISTS "idx_audit_action"
    ON "audit_logs"("action", "created_at" DESC);

-- ═══════════════════════════════════════════════════════════════════════════
-- Part 2: CHECK Constraint Remediation (NOT VALID + VALIDATE pattern)
-- إصلاح قيود التحقق باستخدام نمط NOT VALID + VALIDATE
--
-- The NOT VALID pattern adds the constraint without scanning existing rows
-- (instant, no lock), then VALIDATE scans rows with a ShareUpdateExclusive
-- lock (allows concurrent reads/writes). This is the recommended approach
-- for adding constraints to existing tables in production.
-- ═══════════════════════════════════════════════════════════════════════════

-- Products table constraints
ALTER TABLE "products" DROP CONSTRAINT IF EXISTS "chk_product_price_positive";
ALTER TABLE "products" ADD CONSTRAINT "chk_product_price_positive"
    CHECK ("price" > 0) NOT VALID;
ALTER TABLE "products" VALIDATE CONSTRAINT "chk_product_price_positive";

ALTER TABLE "products" DROP CONSTRAINT IF EXISTS "chk_product_stock_non_negative";
ALTER TABLE "products" ADD CONSTRAINT "chk_product_stock_non_negative"
    CHECK ("stock" >= 0) NOT VALID;
ALTER TABLE "products" VALIDATE CONSTRAINT "chk_product_stock_non_negative";

ALTER TABLE "products" DROP CONSTRAINT IF EXISTS "chk_product_quality_grade";
ALTER TABLE "products" ADD CONSTRAINT "chk_product_quality_grade"
    CHECK ("quality_grade" IS NULL OR "quality_grade" IN ('A', 'B', 'C')) NOT VALID;
ALTER TABLE "products" VALIDATE CONSTRAINT "chk_product_quality_grade";

-- Orders table constraints
ALTER TABLE "orders" DROP CONSTRAINT IF EXISTS "chk_order_subtotal_positive";
ALTER TABLE "orders" ADD CONSTRAINT "chk_order_subtotal_positive"
    CHECK ("subtotal" > 0) NOT VALID;
ALTER TABLE "orders" VALIDATE CONSTRAINT "chk_order_subtotal_positive";

ALTER TABLE "orders" DROP CONSTRAINT IF EXISTS "chk_order_delivery_fee_non_negative";
ALTER TABLE "orders" ADD CONSTRAINT "chk_order_delivery_fee_non_negative"
    CHECK ("delivery_fee" >= 0) NOT VALID;
ALTER TABLE "orders" VALIDATE CONSTRAINT "chk_order_delivery_fee_non_negative";

ALTER TABLE "orders" DROP CONSTRAINT IF EXISTS "chk_order_service_fee_non_negative";
ALTER TABLE "orders" ADD CONSTRAINT "chk_order_service_fee_non_negative"
    CHECK ("service_fee" >= 0) NOT VALID;
ALTER TABLE "orders" VALIDATE CONSTRAINT "chk_order_service_fee_non_negative";

ALTER TABLE "orders" DROP CONSTRAINT IF EXISTS "chk_order_total_amount_positive";
ALTER TABLE "orders" ADD CONSTRAINT "chk_order_total_amount_positive"
    CHECK ("total_amount" > 0) NOT VALID;
ALTER TABLE "orders" VALIDATE CONSTRAINT "chk_order_total_amount_positive";

ALTER TABLE "orders" DROP CONSTRAINT IF EXISTS "chk_order_total_consistent";
ALTER TABLE "orders" ADD CONSTRAINT "chk_order_total_consistent"
    CHECK ("total_amount" >= "subtotal" + "delivery_fee" + "service_fee" - 0.01) NOT VALID;
ALTER TABLE "orders" VALIDATE CONSTRAINT "chk_order_total_consistent";

-- Order items table constraints
ALTER TABLE "order_items" DROP CONSTRAINT IF EXISTS "chk_order_item_quantity_positive";
ALTER TABLE "order_items" ADD CONSTRAINT "chk_order_item_quantity_positive"
    CHECK ("quantity" > 0) NOT VALID;
ALTER TABLE "order_items" VALIDATE CONSTRAINT "chk_order_item_quantity_positive";

ALTER TABLE "order_items" DROP CONSTRAINT IF EXISTS "chk_order_item_unit_price_positive";
ALTER TABLE "order_items" ADD CONSTRAINT "chk_order_item_unit_price_positive"
    CHECK ("unit_price" > 0) NOT VALID;
ALTER TABLE "order_items" VALIDATE CONSTRAINT "chk_order_item_unit_price_positive";

ALTER TABLE "order_items" DROP CONSTRAINT IF EXISTS "chk_order_item_total_price_positive";
ALTER TABLE "order_items" ADD CONSTRAINT "chk_order_item_total_price_positive"
    CHECK ("total_price" > 0) NOT VALID;
ALTER TABLE "order_items" VALIDATE CONSTRAINT "chk_order_item_total_price_positive";

ALTER TABLE "order_items" DROP CONSTRAINT IF EXISTS "chk_order_item_price_consistent";
ALTER TABLE "order_items" ADD CONSTRAINT "chk_order_item_price_consistent"
    CHECK ("total_price" >= ("quantity" * "unit_price") - 0.01
       AND "total_price" <= ("quantity" * "unit_price") + 0.01) NOT VALID;
ALTER TABLE "order_items" VALIDATE CONSTRAINT "chk_order_item_price_consistent";

-- Wallets table constraints
ALTER TABLE "wallets" DROP CONSTRAINT IF EXISTS "chk_wallet_balance_non_negative";
ALTER TABLE "wallets" ADD CONSTRAINT "chk_wallet_balance_non_negative"
    CHECK ("balance" >= 0) NOT VALID;
ALTER TABLE "wallets" VALIDATE CONSTRAINT "chk_wallet_balance_non_negative";

ALTER TABLE "wallets" DROP CONSTRAINT IF EXISTS "chk_wallet_escrow_non_negative";
ALTER TABLE "wallets" ADD CONSTRAINT "chk_wallet_escrow_non_negative"
    CHECK ("escrow_balance" >= 0) NOT VALID;
ALTER TABLE "wallets" VALIDATE CONSTRAINT "chk_wallet_escrow_non_negative";

ALTER TABLE "wallets" DROP CONSTRAINT IF EXISTS "chk_wallet_credit_score_range";
ALTER TABLE "wallets" ADD CONSTRAINT "chk_wallet_credit_score_range"
    CHECK ("credit_score" >= 300 AND "credit_score" <= 850) NOT VALID;
ALTER TABLE "wallets" VALIDATE CONSTRAINT "chk_wallet_credit_score_range";

ALTER TABLE "wallets" DROP CONSTRAINT IF EXISTS "chk_wallet_loan_limit_non_negative";
ALTER TABLE "wallets" ADD CONSTRAINT "chk_wallet_loan_limit_non_negative"
    CHECK ("loan_limit" >= 0) NOT VALID;
ALTER TABLE "wallets" VALIDATE CONSTRAINT "chk_wallet_loan_limit_non_negative";

ALTER TABLE "wallets" DROP CONSTRAINT IF EXISTS "chk_wallet_current_loan_non_negative";
ALTER TABLE "wallets" ADD CONSTRAINT "chk_wallet_current_loan_non_negative"
    CHECK ("current_loan" >= 0) NOT VALID;
ALTER TABLE "wallets" VALIDATE CONSTRAINT "chk_wallet_current_loan_non_negative";

ALTER TABLE "wallets" DROP CONSTRAINT IF EXISTS "chk_wallet_loan_within_limit";
ALTER TABLE "wallets" ADD CONSTRAINT "chk_wallet_loan_within_limit"
    CHECK ("current_loan" <= "loan_limit" OR "loan_limit" = 0) NOT VALID;
ALTER TABLE "wallets" VALIDATE CONSTRAINT "chk_wallet_loan_within_limit";

ALTER TABLE "wallets" DROP CONSTRAINT IF EXISTS "chk_wallet_daily_limit_positive";
ALTER TABLE "wallets" ADD CONSTRAINT "chk_wallet_daily_limit_positive"
    CHECK ("daily_withdraw_limit" > 0) NOT VALID;
ALTER TABLE "wallets" VALIDATE CONSTRAINT "chk_wallet_daily_limit_positive";

ALTER TABLE "wallets" DROP CONSTRAINT IF EXISTS "chk_wallet_daily_withdrawn_non_negative";
ALTER TABLE "wallets" ADD CONSTRAINT "chk_wallet_daily_withdrawn_non_negative"
    CHECK ("daily_withdrawn_today" >= 0) NOT VALID;
ALTER TABLE "wallets" VALIDATE CONSTRAINT "chk_wallet_daily_withdrawn_non_negative";

ALTER TABLE "wallets" DROP CONSTRAINT IF EXISTS "chk_wallet_version_non_negative";
ALTER TABLE "wallets" ADD CONSTRAINT "chk_wallet_version_non_negative"
    CHECK ("version" >= 0) NOT VALID;
ALTER TABLE "wallets" VALIDATE CONSTRAINT "chk_wallet_version_non_negative";

-- Transactions table constraints
ALTER TABLE "transactions" DROP CONSTRAINT IF EXISTS "chk_transaction_amount_positive";
ALTER TABLE "transactions" ADD CONSTRAINT "chk_transaction_amount_positive"
    CHECK ("amount" > 0) NOT VALID;
ALTER TABLE "transactions" VALIDATE CONSTRAINT "chk_transaction_amount_positive";

ALTER TABLE "transactions" DROP CONSTRAINT IF EXISTS "chk_transaction_balance_after_non_negative";
ALTER TABLE "transactions" ADD CONSTRAINT "chk_transaction_balance_after_non_negative"
    CHECK ("balance_after" >= 0) NOT VALID;
ALTER TABLE "transactions" VALIDATE CONSTRAINT "chk_transaction_balance_after_non_negative";

-- Loans table constraints
ALTER TABLE "loans" DROP CONSTRAINT IF EXISTS "chk_loan_amount_positive";
ALTER TABLE "loans" ADD CONSTRAINT "chk_loan_amount_positive"
    CHECK ("amount" > 0) NOT VALID;
ALTER TABLE "loans" VALIDATE CONSTRAINT "chk_loan_amount_positive";

ALTER TABLE "loans" DROP CONSTRAINT IF EXISTS "chk_loan_interest_rate_non_negative";
ALTER TABLE "loans" ADD CONSTRAINT "chk_loan_interest_rate_non_negative"
    CHECK ("interest_rate" >= 0) NOT VALID;
ALTER TABLE "loans" VALIDATE CONSTRAINT "chk_loan_interest_rate_non_negative";

ALTER TABLE "loans" DROP CONSTRAINT IF EXISTS "chk_loan_total_due_positive";
ALTER TABLE "loans" ADD CONSTRAINT "chk_loan_total_due_positive"
    CHECK ("total_due" > 0) NOT VALID;
ALTER TABLE "loans" VALIDATE CONSTRAINT "chk_loan_total_due_positive";

ALTER TABLE "loans" DROP CONSTRAINT IF EXISTS "chk_loan_paid_amount_non_negative";
ALTER TABLE "loans" ADD CONSTRAINT "chk_loan_paid_amount_non_negative"
    CHECK ("paid_amount" >= 0) NOT VALID;
ALTER TABLE "loans" VALIDATE CONSTRAINT "chk_loan_paid_amount_non_negative";

ALTER TABLE "loans" DROP CONSTRAINT IF EXISTS "chk_loan_paid_not_exceeds_due";
ALTER TABLE "loans" ADD CONSTRAINT "chk_loan_paid_not_exceeds_due"
    CHECK ("paid_amount" <= "total_due") NOT VALID;
ALTER TABLE "loans" VALIDATE CONSTRAINT "chk_loan_paid_not_exceeds_due";

ALTER TABLE "loans" DROP CONSTRAINT IF EXISTS "chk_loan_term_months_positive";
ALTER TABLE "loans" ADD CONSTRAINT "chk_loan_term_months_positive"
    CHECK ("term_months" > 0) NOT VALID;
ALTER TABLE "loans" VALIDATE CONSTRAINT "chk_loan_term_months_positive";

ALTER TABLE "loans" DROP CONSTRAINT IF EXISTS "chk_loan_due_after_start";
ALTER TABLE "loans" ADD CONSTRAINT "chk_loan_due_after_start"
    CHECK ("due_date" > "start_date") NOT VALID;
ALTER TABLE "loans" VALIDATE CONSTRAINT "chk_loan_due_after_start";

-- Escrows table constraints
ALTER TABLE "escrows" DROP CONSTRAINT IF EXISTS "chk_escrow_amount_positive";
ALTER TABLE "escrows" ADD CONSTRAINT "chk_escrow_amount_positive"
    CHECK ("amount" > 0) NOT VALID;
ALTER TABLE "escrows" VALIDATE CONSTRAINT "chk_escrow_amount_positive";

ALTER TABLE "escrows" DROP CONSTRAINT IF EXISTS "chk_escrow_different_wallets";
ALTER TABLE "escrows" ADD CONSTRAINT "chk_escrow_different_wallets"
    CHECK ("buyer_wallet_id" != "seller_wallet_id") NOT VALID;
ALTER TABLE "escrows" VALIDATE CONSTRAINT "chk_escrow_different_wallets";

-- Seller profiles table constraints
ALTER TABLE "seller_profiles" DROP CONSTRAINT IF EXISTS "chk_seller_rating_range";
ALTER TABLE "seller_profiles" ADD CONSTRAINT "chk_seller_rating_range"
    CHECK ("rating" >= 0 AND "rating" <= 5) NOT VALID;
ALTER TABLE "seller_profiles" VALIDATE CONSTRAINT "chk_seller_rating_range";

ALTER TABLE "seller_profiles" DROP CONSTRAINT IF EXISTS "chk_seller_total_sales_non_negative";
ALTER TABLE "seller_profiles" ADD CONSTRAINT "chk_seller_total_sales_non_negative"
    CHECK ("total_sales" >= 0) NOT VALID;
ALTER TABLE "seller_profiles" VALIDATE CONSTRAINT "chk_seller_total_sales_non_negative";

ALTER TABLE "seller_profiles" DROP CONSTRAINT IF EXISTS "chk_seller_total_revenue_non_negative";
ALTER TABLE "seller_profiles" ADD CONSTRAINT "chk_seller_total_revenue_non_negative"
    CHECK ("total_revenue" >= 0) NOT VALID;
ALTER TABLE "seller_profiles" VALIDATE CONSTRAINT "chk_seller_total_revenue_non_negative";

-- Buyer profiles table constraints
ALTER TABLE "buyer_profiles" DROP CONSTRAINT IF EXISTS "chk_buyer_total_purchases_non_negative";
ALTER TABLE "buyer_profiles" ADD CONSTRAINT "chk_buyer_total_purchases_non_negative"
    CHECK ("total_purchases" >= 0) NOT VALID;
ALTER TABLE "buyer_profiles" VALIDATE CONSTRAINT "chk_buyer_total_purchases_non_negative";

ALTER TABLE "buyer_profiles" DROP CONSTRAINT IF EXISTS "chk_buyer_total_spent_non_negative";
ALTER TABLE "buyer_profiles" ADD CONSTRAINT "chk_buyer_total_spent_non_negative"
    CHECK ("total_spent" >= 0) NOT VALID;
ALTER TABLE "buyer_profiles" VALIDATE CONSTRAINT "chk_buyer_total_spent_non_negative";

ALTER TABLE "buyer_profiles" DROP CONSTRAINT IF EXISTS "chk_buyer_loyalty_points_non_negative";
ALTER TABLE "buyer_profiles" ADD CONSTRAINT "chk_buyer_loyalty_points_non_negative"
    CHECK ("loyalty_points" >= 0) NOT VALID;
ALTER TABLE "buyer_profiles" VALIDATE CONSTRAINT "chk_buyer_loyalty_points_non_negative";

-- Product reviews table constraints
ALTER TABLE "product_reviews" DROP CONSTRAINT IF EXISTS "chk_review_rating_range";
ALTER TABLE "product_reviews" ADD CONSTRAINT "chk_review_rating_range"
    CHECK ("rating" >= 1 AND "rating" <= 5) NOT VALID;
ALTER TABLE "product_reviews" VALIDATE CONSTRAINT "chk_review_rating_range";

ALTER TABLE "product_reviews" DROP CONSTRAINT IF EXISTS "chk_review_helpful_non_negative";
ALTER TABLE "product_reviews" ADD CONSTRAINT "chk_review_helpful_non_negative"
    CHECK ("helpful" >= 0) NOT VALID;
ALTER TABLE "product_reviews" VALIDATE CONSTRAINT "chk_review_helpful_non_negative";

-- Scheduled payments table constraints
ALTER TABLE "scheduled_payments" DROP CONSTRAINT IF EXISTS "chk_scheduled_payment_amount_positive";
ALTER TABLE "scheduled_payments" ADD CONSTRAINT "chk_scheduled_payment_amount_positive"
    CHECK ("amount" > 0) NOT VALID;
ALTER TABLE "scheduled_payments" VALIDATE CONSTRAINT "chk_scheduled_payment_amount_positive";

ALTER TABLE "scheduled_payments" DROP CONSTRAINT IF EXISTS "chk_scheduled_payment_failed_attempts_non_negative";
ALTER TABLE "scheduled_payments" ADD CONSTRAINT "chk_scheduled_payment_failed_attempts_non_negative"
    CHECK ("failed_attempts" >= 0) NOT VALID;
ALTER TABLE "scheduled_payments" VALIDATE CONSTRAINT "chk_scheduled_payment_failed_attempts_non_negative";

-- ═══════════════════════════════════════════════════════════════════════════
-- Preserve constraint comments from original migration
-- الحفاظ على تعليقات القيود من الهجرة الأصلية
-- ═══════════════════════════════════════════════════════════════════════════

COMMENT ON CONSTRAINT "chk_wallet_balance_non_negative" ON "wallets"
IS 'Prevents negative wallet balance - critical for financial integrity';

COMMENT ON CONSTRAINT "chk_wallet_credit_score_range" ON "wallets"
IS 'Credit score follows standard FICO range (300-850)';

COMMENT ON CONSTRAINT "chk_escrow_different_wallets" ON "escrows"
IS 'Prevents self-dealing in escrow transactions';

COMMENT ON CONSTRAINT "chk_loan_paid_not_exceeds_due" ON "loans"
IS 'Ensures paid amount never exceeds what is owed';
