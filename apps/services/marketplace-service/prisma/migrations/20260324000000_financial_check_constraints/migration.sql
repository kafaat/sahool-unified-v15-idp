-- Migration: Financial CHECK Constraints
-- Date: 2026-03-24
--
-- Adds database-level CHECK constraints to prevent financial data corruption:
-- 1. Wallet balance must be non-negative
-- 2. Wallet escrow balance must be non-negative
-- 3. Wallet loan limit must be non-negative
-- 4. Wallet credit score within valid range (300-850)
-- 5. Transaction amount must be positive
-- 6. Product price must be non-negative
-- 7. Order subtotal and total must be non-negative
--
-- These constraints provide defense-in-depth alongside application-level validation.

-- ============================================================================
-- 1. Wallets - Financial integrity constraints
-- ============================================================================
ALTER TABLE "wallets"
  ADD CONSTRAINT chk_wallet_balance_non_negative
    CHECK ("balance" >= 0),
  ADD CONSTRAINT chk_wallet_escrow_non_negative
    CHECK ("escrow_balance" >= 0),
  ADD CONSTRAINT chk_wallet_loan_limit_non_negative
    CHECK ("loan_limit" >= 0),
  ADD CONSTRAINT chk_wallet_credit_score_range
    CHECK ("credit_score" >= 300 AND "credit_score" <= 850),
  ADD CONSTRAINT chk_wallet_daily_limit_non_negative
    CHECK ("daily_withdraw_limit" >= 0),
  ADD CONSTRAINT chk_wallet_single_limit_non_negative
    CHECK ("single_transaction_limit" >= 0);

-- ============================================================================
-- 2. Transactions - Amount validation
-- ============================================================================
ALTER TABLE "transactions"
  ADD CONSTRAINT chk_transaction_amount_positive
    CHECK ("amount" > 0);

-- ============================================================================
-- 3. Products - Price validation
-- ============================================================================
ALTER TABLE "products"
  ADD CONSTRAINT chk_product_price_non_negative
    CHECK ("price" >= 0);

-- ============================================================================
-- 4. Orders - Total validation
-- ============================================================================
ALTER TABLE "orders"
  ADD CONSTRAINT chk_order_subtotal_non_negative
    CHECK ("subtotal" >= 0),
  ADD CONSTRAINT chk_order_total_non_negative
    CHECK ("total" >= 0);

-- ============================================================================
-- 5. Loans - Amount validation
-- ============================================================================
ALTER TABLE "loans"
  ADD CONSTRAINT chk_loan_amount_positive
    CHECK ("amount" > 0),
  ADD CONSTRAINT chk_loan_paid_non_negative
    CHECK ("paid_amount" >= 0),
  ADD CONSTRAINT chk_loan_total_due_positive
    CHECK ("total_due" > 0);
