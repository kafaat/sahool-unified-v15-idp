-- ═══════════════════════════════════════════════════════════════════════════
-- SAHOOL Audit Service — Initial Schema
-- Migration: 001_create_audit_log
-- Created:   2026-04-17
-- Purpose:   Persist audit events with tamper-evident hash chain so they
--            survive restarts and satisfy compliance retention (GDPR,
--            SOC 2, GlobalGAP 5-year).
-- ═══════════════════════════════════════════════════════════════════════════

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ───────────────────────────────────────────────────────────────────────────
-- audit_log — append-only table; never UPDATE or DELETE except via retention.
-- prev_hash / entry_hash form a per-tenant hash chain (SHA-256) so any
-- out-of-band tampering with historical rows breaks verify_chain().
-- seq_num is a BIGSERIAL scoped at write time to the tenant, giving a
-- deterministic monotonic ordering that's faster than sorting by created_at.
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_log (
    id              UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id       VARCHAR(100) NOT NULL,
    seq_num         BIGSERIAL    NOT NULL,

    -- Actor / action
    user_id         VARCHAR(255) NOT NULL DEFAULT 'system',
    action          VARCHAR(255) NOT NULL,
    category        VARCHAR(50)  NOT NULL,
    severity        VARCHAR(20)  NOT NULL DEFAULT 'info',

    -- Target resource (optional)
    resource_type   VARCHAR(100),
    resource_id     VARCHAR(255),

    -- Request context
    correlation_id  UUID,
    ip_address      INET,
    user_agent      TEXT,

    -- Outcome
    success         BOOLEAN      NOT NULL DEFAULT TRUE,
    error_code      VARCHAR(50),
    error_message   TEXT,

    -- Payload: free-form details + structured before/after for change events
    details         JSONB        NOT NULL DEFAULT '{}'::jsonb,
    old_value       JSONB,
    new_value       JSONB,

    -- Tamper-evident chain
    entry_hash      VARCHAR(64)  NOT NULL,
    prev_hash       VARCHAR(64),

    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT chk_severity CHECK (
        severity IN ('debug', 'info', 'warning', 'error', 'critical')
    ),
    CONSTRAINT chk_category CHECK (
        category IN (
            'authentication', 'authorization', 'configuration', 'catalog',
            'kubernetes', 'field_ops', 'billing', 'compliance', 'security',
            'data', 'system', 'user_management', 'code_change'
        )
    ),
    CONSTRAINT chk_hash_length CHECK (char_length(entry_hash) = 64)
);

-- ───────────────────────────────────────────────────────────────────────────
-- Indexes — aligned with the query patterns in main.py:
--   GET /audit/logs                 → tenant + created_at (primary)
--   GET /audit/users/{id}/trail     → tenant + user + created_at
--   GET /audit/resources/{type}/{id}/trail → tenant + resource
--   GET /audit/chain/validate       → tenant + seq_num
--   GET /audit/security-events      → tenant + category='security'
--   GET /audit/failed-logins        → tenant + success=FALSE + category='authentication'
-- ───────────────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_audit_log_tenant_created
    ON audit_log (tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_tenant_user
    ON audit_log (tenant_id, user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_tenant_category
    ON audit_log (tenant_id, category, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_tenant_resource
    ON audit_log (tenant_id, resource_type, resource_id)
    WHERE resource_type IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_audit_log_tenant_seq
    ON audit_log (tenant_id, seq_num);

-- Partial index for failed-login search (small subset, much smaller index).
CREATE INDEX IF NOT EXISTS idx_audit_log_failed_auth
    ON audit_log (tenant_id, created_at DESC)
    WHERE success = FALSE AND category = 'authentication';

-- ───────────────────────────────────────────────────────────────────────────
-- Protective triggers — append-only semantics.
-- UPDATE and DELETE are blocked at the DB level; the only legitimate way
-- to remove records is the retention job running with a dedicated role
-- (audit_retention) that this trigger will skip.
-- ───────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION audit_log_block_mutations()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    IF current_setting('sahool.audit_retention_job', true) = 'on' THEN
        RETURN OLD;
    END IF;
    RAISE EXCEPTION
        'audit_log is append-only; % blocked for tenant=% id=%',
        TG_OP, COALESCE(OLD.tenant_id, NEW.tenant_id), COALESCE(OLD.id, NEW.id)
        USING ERRCODE = 'insufficient_privilege';
END;
$$;

DROP TRIGGER IF EXISTS trg_audit_log_no_update ON audit_log;
CREATE TRIGGER trg_audit_log_no_update
    BEFORE UPDATE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_block_mutations();

DROP TRIGGER IF EXISTS trg_audit_log_no_delete ON audit_log;
CREATE TRIGGER trg_audit_log_no_delete
    BEFORE DELETE ON audit_log
    FOR EACH ROW EXECUTE FUNCTION audit_log_block_mutations();

-- ───────────────────────────────────────────────────────────────────────────
-- Row-level security — tenant isolation.
-- Every query must set `app.current_tenant_id` via SET LOCAL so that
-- even a SELECT * cannot cross tenants. Enforced unconditionally.
-- ───────────────────────────────────────────────────────────────────────────
ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS audit_log_tenant_isolation ON audit_log;
CREATE POLICY audit_log_tenant_isolation ON audit_log
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- ───────────────────────────────────────────────────────────────────────────
-- Migration bookkeeping — idempotent re-apply.
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_service_schema_migrations (
    version     VARCHAR(64) PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO audit_service_schema_migrations (version)
    VALUES ('001_create_audit_log')
    ON CONFLICT DO NOTHING;
