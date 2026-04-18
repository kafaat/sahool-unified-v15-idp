-- ═══════════════════════════════════════════════════════════════════════════
-- SAHOOL Audit Service — Cold-Storage Archive Table
-- Migration: 004_audit_log_archive
-- Created:   2026-04-18
-- Purpose:   Close the compliance gap between retention (DELETE) and replay.
--            Before migration 003 the retention worker would DELETE rows from
--            audit_log and record only metadata + the deleted entry_hashes in
--            audit_retention_events. The row CONTENT (user_id, action,
--            details JSONB, etc.) was discarded — auditors running replay
--            over the 5-year GlobalGAP / SOC 2 window saw invisible holes
--            wherever the nightly sweep had cleared per-category retention.
--            Migration 004 adds audit_log_archive: a mirror of audit_log
--            populated by a CTE inside the retention transaction. The
--            replay endpoint (/api/v1/audit/logs/archived) reads from it
--            without touching the hot audit_log table.
-- ═══════════════════════════════════════════════════════════════════════════
--
-- Design notes:
--   * Schema mirrors audit_log exactly so the CTE-copy is a `SELECT *` with
--     two extra columns tacked on (archived_at, archived_by). Any migration
--     that widens audit_log must also widen this table — flagged in the
--     audit-service README.
--   * Append-only: INSERT allowed under the same retention session variable
--     that gates audit_log DELETE; UPDATE / DELETE blocked unconditionally.
--     An archive that can be rewritten is not an archive.
--   * No hash-chain re-validation on archive rows — the entry_hash column
--     is copied verbatim from the live row, so running validate_chain over
--     audit_log UNION audit_log_archive would reproduce the pre-retention
--     chain exactly. Not exposed as an endpoint yet (separate work); the
--     column is preserved so we don't have to backfill later.
--   * tenant_id RLS mirrors audit_log: every SELECT must SET LOCAL
--     app.current_tenant_id or the policy returns zero rows.
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS audit_log_archive (
    -- Mirrors audit_log columns exactly.
    id              UUID         NOT NULL,
    tenant_id       VARCHAR(100) NOT NULL,
    seq_num         BIGINT       NOT NULL,

    user_id         VARCHAR(255) NOT NULL,
    action          VARCHAR(255) NOT NULL,
    category        VARCHAR(50)  NOT NULL,
    severity        VARCHAR(20)  NOT NULL,

    resource_type   VARCHAR(100),
    resource_id     VARCHAR(255),

    correlation_id  UUID,
    ip_address      INET,
    user_agent      TEXT,

    success         BOOLEAN      NOT NULL,
    error_code      VARCHAR(50),
    error_message   TEXT,

    details         JSONB        NOT NULL DEFAULT '{}'::jsonb,
    old_value       JSONB,
    new_value       JSONB,

    entry_hash      VARCHAR(64)  NOT NULL,
    prev_hash       VARCHAR(64),

    created_at      TIMESTAMPTZ  NOT NULL,

    -- Archive-specific metadata.
    archived_at     TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    archived_by     VARCHAR(100) NOT NULL DEFAULT 'audit-retention-worker',

    -- (tenant_id, seq_num) is unique in audit_log and remains unique here;
    -- use it as PK so replay queries by (tenant_id, seq_num) are O(log n)
    -- and duplicate archival of the same row (e.g. worker retried after a
    -- partial failure) is rejected at the DB layer.
    PRIMARY KEY (tenant_id, seq_num),

    CONSTRAINT chk_archive_severity CHECK (
        severity IN ('debug', 'info', 'warning', 'error', 'critical')
    ),
    CONSTRAINT chk_archive_hash_length CHECK (char_length(entry_hash) = 64)
);

-- ───────────────────────────────────────────────────────────────────────────
-- Indexes — aligned with the replay query patterns.
--   GET /api/v1/audit/logs/archived?start=...&end=... → tenant + created_at
--   GET /api/v1/audit/logs/archived?user_id=X         → tenant + user
--   GET /api/v1/audit/logs/archived?category=X        → tenant + category
-- ───────────────────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_audit_archive_tenant_created
    ON audit_log_archive (tenant_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_archive_tenant_user
    ON audit_log_archive (tenant_id, user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_archive_tenant_category
    ON audit_log_archive (tenant_id, category, created_at DESC);

-- ───────────────────────────────────────────────────────────────────────────
-- Append-only enforcement.
-- INSERT is gated on the same `sahool.audit_retention_job` session variable
-- the retention worker already sets before DELETE — so a random writer
-- cannot populate the archive table and make fake "deleted" rows appear in
-- replay. UPDATE / DELETE are blocked unconditionally.
-- ───────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION audit_log_archive_block_mutations()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
    -- Block UPDATE and DELETE without exception.
    IF TG_OP IN ('UPDATE', 'DELETE') THEN
        RAISE EXCEPTION
            'audit_log_archive is append-only; % blocked for tenant=% seq=%',
            TG_OP,
            COALESCE(OLD.tenant_id, NEW.tenant_id),
            COALESCE(OLD.seq_num, NEW.seq_num)
            USING ERRCODE = 'insufficient_privilege';
    END IF;
    -- INSERT: require the retention session variable. This is the same
    -- guard audit_log uses to allow its DELETE, so archive INSERT is
    -- scoped to exactly the same transactions that are also deleting
    -- from audit_log.
    IF TG_OP = 'INSERT' THEN
        IF current_setting('sahool.audit_retention_job', true) IS NULL
           OR current_setting('sahool.audit_retention_job', true) <> 'on' THEN
            RAISE EXCEPTION
                'audit_log_archive INSERT requires sahool.audit_retention_job=on; '
                'got %',
                COALESCE(current_setting('sahool.audit_retention_job', true), '(unset)')
                USING ERRCODE = 'insufficient_privilege';
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$;

DROP TRIGGER IF EXISTS trg_audit_archive_no_update ON audit_log_archive;
CREATE TRIGGER trg_audit_archive_no_update
    BEFORE UPDATE ON audit_log_archive
    FOR EACH ROW EXECUTE FUNCTION audit_log_archive_block_mutations();

DROP TRIGGER IF EXISTS trg_audit_archive_no_delete ON audit_log_archive;
CREATE TRIGGER trg_audit_archive_no_delete
    BEFORE DELETE ON audit_log_archive
    FOR EACH ROW EXECUTE FUNCTION audit_log_archive_block_mutations();

DROP TRIGGER IF EXISTS trg_audit_archive_guard_insert ON audit_log_archive;
CREATE TRIGGER trg_audit_archive_guard_insert
    BEFORE INSERT ON audit_log_archive
    FOR EACH ROW EXECUTE FUNCTION audit_log_archive_block_mutations();

-- ───────────────────────────────────────────────────────────────────────────
-- Row-level security — same tenant isolation as audit_log.
-- Replay queries from audit-service must `SET LOCAL app.current_tenant_id`
-- before SELECT or the policy returns zero rows.
-- ───────────────────────────────────────────────────────────────────────────
ALTER TABLE audit_log_archive ENABLE ROW LEVEL SECURITY;
ALTER TABLE audit_log_archive FORCE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS audit_log_archive_tenant_isolation ON audit_log_archive;
CREATE POLICY audit_log_archive_tenant_isolation ON audit_log_archive
    USING (tenant_id = current_setting('app.current_tenant_id', true))
    WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true));

-- ───────────────────────────────────────────────────────────────────────────
-- Privileges — retention worker writes; audit-service reads.
-- ───────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'audit_retention') THEN
        GRANT INSERT, SELECT ON audit_log_archive TO audit_retention;
    END IF;
END
$$;

-- ───────────────────────────────────────────────────────────────────────────
-- Bookkeeping
-- ───────────────────────────────────────────────────────────────────────────
INSERT INTO audit_retention_schema_migrations (version)
    VALUES ('004_audit_log_archive')
    ON CONFLICT DO NOTHING;
