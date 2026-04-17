-- ═══════════════════════════════════════════════════════════════════════════
-- SAHOOL Audit Service — Retention Event Log
-- Migration: 003_audit_retention_events
-- Created:   2026-04-18
-- Purpose:   Record every retention-driven DELETE against audit_log so:
--            (a) compliance can reconstruct what was removed and when,
--            (b) chain-validation tooling can treat retention gaps as
--                expected rather than as tamper evidence,
--            (c) operators can prove to auditors that retention ran.
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Relationship to audit_log:
--   * The retention worker deletes rows from audit_log with the
--     `audit_retention` role under `SET LOCAL sahool.audit_retention_job=on`
--     (see migrations 001 + 002).
--   * For each contiguous deletion (per tenant × per category × per run) we
--     insert one row here capturing the seq_num + entry_hash of the last
--     deleted row. A future audit-service PR will teach validate_chain()
--     to consult this table and accept gaps at those exact seq_nums.
--   * This table is itself append-only; an attacker that can forge
--     retention events could hide a DELETE — so we apply the same
--     append-only triggers as audit_log and require SELECT-only access
--     for every role that isn't the retention worker.
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS audit_retention_events (
    id                        UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id                 VARCHAR(100) NOT NULL,

    -- What was deleted
    -- last_retained_seq_num is the highest seq_num within this tenant that
    -- was removed by this run. After retention, the first surviving row has
    -- seq_num > last_retained_seq_num (typically +1, or +N across a gap if
    -- the category filter excluded interleaved rows).
    last_retained_seq_num     BIGINT       NOT NULL,
    last_retained_entry_hash  VARCHAR(64)  NOT NULL,
    rows_deleted              BIGINT       NOT NULL,

    -- Policy context
    category_filter           VARCHAR(50),  -- NULL = all categories
    retention_days            INT          NOT NULL,
    cutoff_timestamp          TIMESTAMPTZ  NOT NULL,

    -- Optional archive reference; set iff the deleted rows were written to
    -- object storage before DELETE. NULL means the rows were hard-deleted
    -- with no archive.
    archive_location          TEXT,
    archive_sha256            VARCHAR(64),

    -- Operational metadata
    executed_at               TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    executed_by               VARCHAR(100) NOT NULL DEFAULT 'audit-retention-worker',
    dry_run                   BOOLEAN      NOT NULL DEFAULT FALSE,

    CONSTRAINT chk_retention_days_positive CHECK (retention_days > 0),
    CONSTRAINT chk_rows_deleted_nonneg      CHECK (rows_deleted >= 0),
    CONSTRAINT chk_retention_hash_length    CHECK (char_length(last_retained_entry_hash) = 64)
);

CREATE INDEX IF NOT EXISTS idx_retention_events_tenant_seq
    ON audit_retention_events (tenant_id, last_retained_seq_num);

CREATE INDEX IF NOT EXISTS idx_retention_events_executed_at
    ON audit_retention_events (executed_at DESC);

-- ───────────────────────────────────────────────────────────────────────────
-- Append-only enforcement — same pattern as audit_log.
-- No session-variable escape hatch here: retention events themselves must
-- never be rewritten, even by the retention worker.
-- ───────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION audit_retention_events_block_mutations()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    RAISE EXCEPTION
        'audit_retention_events is strictly append-only; % blocked id=%',
        TG_OP, COALESCE(OLD.id, NEW.id)
        USING ERRCODE = 'insufficient_privilege';
END;
$$;

DROP TRIGGER IF EXISTS trg_retention_events_no_update ON audit_retention_events;
CREATE TRIGGER trg_retention_events_no_update
    BEFORE UPDATE ON audit_retention_events
    FOR EACH ROW EXECUTE FUNCTION audit_retention_events_block_mutations();

DROP TRIGGER IF EXISTS trg_retention_events_no_delete ON audit_retention_events;
CREATE TRIGGER trg_retention_events_no_delete
    BEFORE DELETE ON audit_retention_events
    FOR EACH ROW EXECUTE FUNCTION audit_retention_events_block_mutations();

-- ───────────────────────────────────────────────────────────────────────────
-- Privileges — retention worker writes; audit-service reads; nothing else.
-- ───────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'audit_retention') THEN
        GRANT INSERT, SELECT ON audit_retention_events TO audit_retention;
    END IF;
END
$$;

-- ───────────────────────────────────────────────────────────────────────────
-- Bookkeeping — use a worker-owned migration table so the retention worker
-- and audit-service can evolve their schemas independently without colliding
-- on version numbers in audit_service_schema_migrations.
-- ───────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS audit_retention_schema_migrations (
    version     VARCHAR(64) PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO audit_retention_schema_migrations (version)
    VALUES ('003_audit_retention_events')
    ON CONFLICT DO NOTHING;
