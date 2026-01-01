-- ═══════════════════════════════════════════════════════════════════════════════
-- CRITICAL SECURITY FIX: Double-Spend Vulnerability Prevention
-- Migration: 001_add_double_spend_protection.sql
-- Description: Adds version control, idempotency keys, and audit logging
--              to prevent double-spending in wallet transactions
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Add version column to wallets table for optimistic locking
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE wallets
ADD COLUMN IF NOT EXISTS version INTEGER DEFAULT 1 NOT NULL;

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Add daily withdrawal tracking columns
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE wallets
ADD COLUMN IF NOT EXISTS daily_withdraw_limit DECIMAL(14,2) DEFAULT 10000.00,
ADD COLUMN IF NOT EXISTS single_transaction_limit DECIMAL(14,2) DEFAULT 50000.00,
ADD COLUMN IF NOT EXISTS daily_withdrawn_today DECIMAL(14,2) DEFAULT 0.00,
ADD COLUMN IF NOT EXISTS last_withdraw_reset TIMESTAMPTZ,
ADD COLUMN IF NOT EXISTS requires_pin_for_amount DECIMAL(14,2) DEFAULT 5000.00,
ADD COLUMN IF NOT EXISTS escrow_balance DECIMAL(14,2) DEFAULT 0.00;

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Add idempotency_key to transactions table
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE transactions
ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(255) UNIQUE,
ADD COLUMN IF NOT EXISTS balance_before DECIMAL(14,2),
ADD COLUMN IF NOT EXISTS user_id UUID REFERENCES users(id),
ADD COLUMN IF NOT EXISTS ip_address VARCHAR(45),
ADD COLUMN IF NOT EXISTS user_agent TEXT;

-- Create index on idempotency_key for fast lookups
CREATE INDEX IF NOT EXISTS idx_transactions_idempotency_key
ON transactions(idempotency_key) WHERE idempotency_key IS NOT NULL;

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Create wallet_audit_log table for complete audit trail
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS wallet_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    transaction_id UUID REFERENCES transactions(id) ON DELETE SET NULL,
    user_id UUID REFERENCES users(id),
    operation VARCHAR(50) NOT NULL,
    balance_before DECIMAL(14,2) NOT NULL,
    balance_after DECIMAL(14,2) NOT NULL,
    amount DECIMAL(14,2) NOT NULL,
    escrow_balance_before DECIMAL(14,2) DEFAULT 0,
    escrow_balance_after DECIMAL(14,2) DEFAULT 0,
    version_before INTEGER NOT NULL,
    version_after INTEGER NOT NULL,
    idempotency_key VARCHAR(255),
    ip_address VARCHAR(45),
    user_agent TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_wallet_audit_wallet ON wallet_audit_log(wallet_id);
CREATE INDEX IF NOT EXISTS idx_wallet_audit_transaction ON wallet_audit_log(transaction_id);
CREATE INDEX IF NOT EXISTS idx_wallet_audit_user ON wallet_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_wallet_audit_created ON wallet_audit_log(created_at);
CREATE INDEX IF NOT EXISTS idx_wallet_audit_operation ON wallet_audit_log(operation);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5. Create credit_events table (if not exists)
-- ─────────────────────────────────────────────────────────────────────────────
DO $$ BEGIN
    CREATE TYPE credit_event_type AS ENUM (
        'LOAN_REPAID_ONTIME',
        'LOAN_REPAID_LATE',
        'LOAN_DEFAULTED',
        'ORDER_COMPLETED',
        'ORDER_CANCELLED',
        'VERIFICATION_UPGRADE',
        'FARM_VERIFIED',
        'COOPERATIVE_JOINED',
        'LAND_VERIFIED'
    );
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS credit_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    event_type credit_event_type NOT NULL,
    amount DECIMAL(14,2),
    impact INTEGER DEFAULT 0,
    description TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_events_wallet ON credit_events(wallet_id);
CREATE INDEX IF NOT EXISTS idx_credit_events_type ON credit_events(event_type);
CREATE INDEX IF NOT EXISTS idx_credit_events_created ON credit_events(created_at);

-- ─────────────────────────────────────────────────────────────────────────────
-- 6. Create escrow table (if not exists)
-- ─────────────────────────────────────────────────────────────────────────────
DO $$ BEGIN
    CREATE TYPE escrow_status AS ENUM ('HELD', 'RELEASED', 'REFUNDED', 'DISPUTED');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS escrow (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    order_id VARCHAR(255) UNIQUE NOT NULL,
    buyer_wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    seller_wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    amount DECIMAL(14,2) NOT NULL,
    status escrow_status DEFAULT 'HELD',
    notes TEXT,
    dispute_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    released_at TIMESTAMPTZ,
    refunded_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS idx_escrow_order ON escrow(order_id);
CREATE INDEX IF NOT EXISTS idx_escrow_buyer ON escrow(buyer_wallet_id);
CREATE INDEX IF NOT EXISTS idx_escrow_seller ON escrow(seller_wallet_id);
CREATE INDEX IF NOT EXISTS idx_escrow_status ON escrow(status);

-- ─────────────────────────────────────────────────────────────────────────────
-- 7. Create scheduled_payments table (if not exists)
-- ─────────────────────────────────────────────────────────────────────────────
DO $$ BEGIN
    CREATE TYPE payment_frequency AS ENUM ('DAILY', 'WEEKLY', 'BIWEEKLY', 'MONTHLY', 'QUARTERLY', 'YEARLY');
EXCEPTION WHEN duplicate_object THEN NULL; END $$;

CREATE TABLE IF NOT EXISTS scheduled_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    wallet_id UUID NOT NULL REFERENCES wallets(id) ON DELETE CASCADE,
    loan_id UUID REFERENCES loans(id) ON DELETE SET NULL,
    amount DECIMAL(14,2) NOT NULL,
    frequency payment_frequency NOT NULL,
    next_payment_date DATE NOT NULL,
    last_payment_date DATE,
    description TEXT,
    description_ar TEXT,
    is_active BOOLEAN DEFAULT true,
    failed_attempts INTEGER DEFAULT 0,
    last_failure_reason TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_scheduled_payments_wallet ON scheduled_payments(wallet_id);
CREATE INDEX IF NOT EXISTS idx_scheduled_payments_next_date ON scheduled_payments(next_payment_date) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_scheduled_payments_loan ON scheduled_payments(loan_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- 8. Create function to auto-increment wallet version
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION increment_wallet_version()
RETURNS TRIGGER AS $$
BEGIN
    -- Only increment version if balance or escrow_balance changed
    IF (NEW.balance IS DISTINCT FROM OLD.balance) OR
       (NEW.escrow_balance IS DISTINCT FROM OLD.escrow_balance) THEN
        NEW.version = OLD.version + 1;
        NEW.updated_at = NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to auto-increment version
DROP TRIGGER IF EXISTS wallet_version_trigger ON wallets;
CREATE TRIGGER wallet_version_trigger
    BEFORE UPDATE ON wallets
    FOR EACH ROW
    EXECUTE FUNCTION increment_wallet_version();

-- ─────────────────────────────────────────────────────────────────────────────
-- 9. Create function to prevent negative balances
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION check_wallet_balance()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.balance < 0 THEN
        RAISE EXCEPTION 'Wallet balance cannot be negative. Attempted balance: %', NEW.balance;
    END IF;
    IF NEW.escrow_balance < 0 THEN
        RAISE EXCEPTION 'Wallet escrow balance cannot be negative. Attempted balance: %', NEW.escrow_balance;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to check balance
DROP TRIGGER IF EXISTS wallet_balance_check_trigger ON wallets;
CREATE TRIGGER wallet_balance_check_trigger
    BEFORE INSERT OR UPDATE ON wallets
    FOR EACH ROW
    EXECUTE FUNCTION check_wallet_balance();

-- ─────────────────────────────────────────────────────────────────────────────
-- 10. Add constraints
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE wallets
ADD CONSTRAINT check_wallet_balance_non_negative CHECK (balance >= 0),
ADD CONSTRAINT check_wallet_escrow_non_negative CHECK (escrow_balance >= 0);

-- ─────────────────────────────────────────────────────────────────────────────
-- 11. Create helper function for safe wallet updates with locking
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION safe_wallet_debit(
    p_wallet_id UUID,
    p_amount DECIMAL(14,2),
    p_expected_version INTEGER,
    p_operation VARCHAR(50)
)
RETURNS TABLE(
    success BOOLEAN,
    new_balance DECIMAL(14,2),
    new_version INTEGER,
    error_message TEXT
) AS $$
DECLARE
    v_current_balance DECIMAL(14,2);
    v_current_version INTEGER;
    v_new_balance DECIMAL(14,2);
    v_new_version INTEGER;
BEGIN
    -- Lock the wallet row for update
    SELECT balance, version INTO v_current_balance, v_current_version
    FROM wallets
    WHERE id = p_wallet_id
    FOR UPDATE;

    -- Check if wallet exists
    IF NOT FOUND THEN
        RETURN QUERY SELECT false, 0.00::DECIMAL(14,2), 0, 'Wallet not found';
        RETURN;
    END IF;

    -- Optimistic locking check
    IF v_current_version != p_expected_version THEN
        RETURN QUERY SELECT false, v_current_balance, v_current_version,
            'Version mismatch - wallet was modified by another transaction';
        RETURN;
    END IF;

    -- Check sufficient balance
    IF v_current_balance < p_amount THEN
        RETURN QUERY SELECT false, v_current_balance, v_current_version,
            'Insufficient balance';
        RETURN;
    END IF;

    -- Calculate new balance
    v_new_balance := v_current_balance - p_amount;
    v_new_version := v_current_version + 1;

    -- Update wallet
    UPDATE wallets
    SET balance = v_new_balance,
        version = v_new_version,
        updated_at = NOW()
    WHERE id = p_wallet_id;

    -- Return success
    RETURN QUERY SELECT true, v_new_balance, v_new_version, NULL::TEXT;
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════════════════════════════
-- Migration Verification
-- ═══════════════════════════════════════════════════════════════════════════
DO $$
BEGIN
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE '  DOUBLE-SPEND PROTECTION MIGRATION COMPLETE';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE '  ✓ Added version column to wallets table';
    RAISE NOTICE '  ✓ Added idempotency_key to transactions table';
    RAISE NOTICE '  ✓ Created wallet_audit_log table';
    RAISE NOTICE '  ✓ Created credit_events table';
    RAISE NOTICE '  ✓ Created escrow table';
    RAISE NOTICE '  ✓ Created scheduled_payments table';
    RAISE NOTICE '  ✓ Added wallet version auto-increment trigger';
    RAISE NOTICE '  ✓ Added balance validation constraints';
    RAISE NOTICE '  ✓ Created safe_wallet_debit() helper function';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
END;
$$;
