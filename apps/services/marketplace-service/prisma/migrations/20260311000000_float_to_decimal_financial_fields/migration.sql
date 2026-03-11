-- Migration: Float to Decimal for Financial Fields
-- Date: 2026-03-11
--
-- CRITICAL FIX: Convert all financial Float (DOUBLE PRECISION) columns to
-- DECIMAL(15,2) to prevent floating-point rounding errors in monetary calculations.
-- Float types (IEEE 754) cannot precisely represent decimal fractions like 0.10,
-- leading to silent rounding errors in balances, totals, and transaction amounts.
--
-- Exception: interest_rate uses DECIMAL(5,4) for percentage precision (e.g., 0.0200 = 2%).
--
-- Non-financial Float fields (stock, quantity, rating) are intentionally left as
-- DOUBLE PRECISION since they represent quantities/scores, not money.

-- ============================================================================
-- 1. Products - price
-- ============================================================================
ALTER TABLE "products"
  ALTER COLUMN "price" TYPE DECIMAL(15,2) USING "price"::DECIMAL(15,2);

-- ============================================================================
-- 2. Orders - subtotal, delivery_fee, service_fee, total_amount
-- ============================================================================
ALTER TABLE "orders"
  ALTER COLUMN "subtotal" TYPE DECIMAL(15,2) USING "subtotal"::DECIMAL(15,2),
  ALTER COLUMN "delivery_fee" TYPE DECIMAL(15,2) USING "delivery_fee"::DECIMAL(15,2),
  ALTER COLUMN "service_fee" TYPE DECIMAL(15,2) USING "service_fee"::DECIMAL(15,2),
  ALTER COLUMN "total_amount" TYPE DECIMAL(15,2) USING "total_amount"::DECIMAL(15,2);

-- ============================================================================
-- 3. Order Items - unit_price, total_price
-- ============================================================================
ALTER TABLE "order_items"
  ALTER COLUMN "unit_price" TYPE DECIMAL(15,2) USING "unit_price"::DECIMAL(15,2),
  ALTER COLUMN "total_price" TYPE DECIMAL(15,2) USING "total_price"::DECIMAL(15,2);

-- ============================================================================
-- 4. Wallets - balance, escrow_balance, loan_limit, current_loan,
--    daily_withdraw_limit, single_transaction_limit, requires_pin_for_amount,
--    daily_withdrawn_today
-- ============================================================================
ALTER TABLE "wallets"
  ALTER COLUMN "balance" TYPE DECIMAL(15,2) USING "balance"::DECIMAL(15,2),
  ALTER COLUMN "escrow_balance" TYPE DECIMAL(15,2) USING "escrow_balance"::DECIMAL(15,2),
  ALTER COLUMN "loan_limit" TYPE DECIMAL(15,2) USING "loan_limit"::DECIMAL(15,2),
  ALTER COLUMN "current_loan" TYPE DECIMAL(15,2) USING "current_loan"::DECIMAL(15,2),
  ALTER COLUMN "daily_withdraw_limit" TYPE DECIMAL(15,2) USING "daily_withdraw_limit"::DECIMAL(15,2),
  ALTER COLUMN "single_transaction_limit" TYPE DECIMAL(15,2) USING "single_transaction_limit"::DECIMAL(15,2),
  ALTER COLUMN "requires_pin_for_amount" TYPE DECIMAL(15,2) USING "requires_pin_for_amount"::DECIMAL(15,2),
  ALTER COLUMN "daily_withdrawn_today" TYPE DECIMAL(15,2) USING "daily_withdrawn_today"::DECIMAL(15,2);

-- ============================================================================
-- 5. Transactions - amount, balance_after, balance_before
-- ============================================================================
ALTER TABLE "transactions"
  ALTER COLUMN "amount" TYPE DECIMAL(15,2) USING "amount"::DECIMAL(15,2),
  ALTER COLUMN "balance_after" TYPE DECIMAL(15,2) USING "balance_after"::DECIMAL(15,2),
  ALTER COLUMN "balance_before" TYPE DECIMAL(15,2) USING "balance_before"::DECIMAL(15,2);

-- ============================================================================
-- 6. Loans - amount, interest_rate (DECIMAL(5,4)), total_due, paid_amount,
--    collateral_value
-- ============================================================================
ALTER TABLE "loans"
  ALTER COLUMN "amount" TYPE DECIMAL(15,2) USING "amount"::DECIMAL(15,2),
  ALTER COLUMN "interest_rate" TYPE DECIMAL(5,4) USING "interest_rate"::DECIMAL(5,4),
  ALTER COLUMN "total_due" TYPE DECIMAL(15,2) USING "total_due"::DECIMAL(15,2),
  ALTER COLUMN "paid_amount" TYPE DECIMAL(15,2) USING "paid_amount"::DECIMAL(15,2),
  ALTER COLUMN "collateral_value" TYPE DECIMAL(15,2) USING "collateral_value"::DECIMAL(15,2);

-- ============================================================================
-- 7. Credit Events - amount
-- ============================================================================
ALTER TABLE "credit_events"
  ALTER COLUMN "amount" TYPE DECIMAL(15,2) USING "amount"::DECIMAL(15,2);

-- ============================================================================
-- 8. Escrows - amount
-- ============================================================================
ALTER TABLE "escrows"
  ALTER COLUMN "amount" TYPE DECIMAL(15,2) USING "amount"::DECIMAL(15,2);

-- ============================================================================
-- 9. Scheduled Payments - amount
-- ============================================================================
ALTER TABLE "scheduled_payments"
  ALTER COLUMN "amount" TYPE DECIMAL(15,2) USING "amount"::DECIMAL(15,2);

-- ============================================================================
-- 10. Wallet Audit Logs - balance_before, balance_after, amount,
--     escrow_balance_before, escrow_balance_after
-- ============================================================================
ALTER TABLE "wallet_audit_logs"
  ALTER COLUMN "balance_before" TYPE DECIMAL(15,2) USING "balance_before"::DECIMAL(15,2),
  ALTER COLUMN "balance_after" TYPE DECIMAL(15,2) USING "balance_after"::DECIMAL(15,2),
  ALTER COLUMN "amount" TYPE DECIMAL(15,2) USING "amount"::DECIMAL(15,2),
  ALTER COLUMN "escrow_balance_before" TYPE DECIMAL(15,2) USING "escrow_balance_before"::DECIMAL(15,2),
  ALTER COLUMN "escrow_balance_after" TYPE DECIMAL(15,2) USING "escrow_balance_after"::DECIMAL(15,2);

-- ============================================================================
-- 11. Seller Profiles - total_revenue
-- ============================================================================
ALTER TABLE "seller_profiles"
  ALTER COLUMN "total_revenue" TYPE DECIMAL(15,2) USING "total_revenue"::DECIMAL(15,2);

-- ============================================================================
-- 12. Buyer Profiles - total_spent
-- ============================================================================
ALTER TABLE "buyer_profiles"
  ALTER COLUMN "total_spent" TYPE DECIMAL(15,2) USING "total_spent"::DECIMAL(15,2);
