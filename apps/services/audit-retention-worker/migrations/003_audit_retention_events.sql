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
--   * For each (tenant × category × run) we insert one row here that
--     captures the FULL set of deleted entry_hashes (not just the last
--     one) so a subsequent chain-validation sweep can recognise every
--     surviving row whose prev_hash points at a deleted predecessor as
--     a legitimate retention gap — not tampering. Recording only the
--     newest deleted hash would be insufficient: per-category retention
--     with DIFFERENT retention_days (the realistic config — auth 90d,
--     billing 1825d) produces non-contiguous deletions interleaved
--     within the per-tenant chain, so multiple surviving rows can
--     point at separate deleted predecessors from the same run.
--   * This table is itself append-only; an attacker that can forge
--     retention events could hide a DELETE — so we apply the same
--     append-only triggers as audit_log and require SELECT-only access
--     for every role that isn't the retention worker.
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE IF NOT EXISTS audit_retention_events (
    id                         UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id                  VARCHAR(100) NOT NULL,

    -- What was deleted
    -- last_deleted_seq_num is the highest seq_num within this tenant that
    -- was REMOVED by this run (semantic: the last row NOT retained, i.e.
    -- the newest of the deleted rows). After retention, the first
    -- surviving row has seq_num > last_deleted_seq_num.
    last_deleted_seq_num       BIGINT       NOT NULL,
    last_deleted_entry_hash    VARCHAR(64)  NOT NULL,
    rows_deleted               BIGINT       NOT NULL,
    -- Every deleted row's entry_hash, in seq_num ascending order.
    -- validate_chain()'s retention-awareness walks this union across all
    -- retention events for the tenant and treats any surviving
    -- prev_hash match as a legitimate gap. Stored as TEXT[] rather than
    -- a child table to keep a single-row transaction contract — one
    -- retention event = one atomic write. See README for storage
    -- sizing; SHA-256 hexes at ~10k rows/day amount to ~230MB/year
    -- per busy tenant before any compaction.
    deleted_entry_hashes       TEXT[]       NOT NULL DEFAULT ARRAY[]::TEXT[],

    -- Policy context
    category_filter            VARCHAR(50),  -- NULL = all categories
    retention_days             INT          NOT NULL,
    cutoff_timestamp           TIMESTAMPTZ  NOT NULL,

    -- Optional archive reference; set iff the deleted rows were written to
    -- object storage before DELETE. NULL means the rows were hard-deleted
    -- with no archive.
    archive_location           TEXT,
    archive_sha256             VARCHAR(64),

    -- Operational metadata
    executed_at                TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    executed_by                VARCHAR(100) NOT NULL DEFAULT 'audit-retention-worker',
    dry_run                    BOOLEAN      NOT NULL DEFAULT FALSE,

    CONSTRAINT chk_retention_days_positive CHECK (retention_days > 0),
    CONSTRAINT chk_rows_deleted_nonneg      CHECK (rows_deleted >= 0),
    CONSTRAINT chk_deleted_hash_length      CHECK (char_length(last_deleted_entry_hash) = 64),
    -- The hash array must be consistent with the row count. We can't
    -- exactly enforce equality (rare cases where a hash is unavailable)
    -- but we can at least enforce "no more than we claim we deleted".
    CONSTRAINT chk_hash_array_bounds        CHECK (
        cardinality(deleted_entry_hashes) <= rows_deleted
    )
);

CREATE INDEX IF NOT EXISTS idx_retention_events_tenant_seq
    ON audit_retention_events (tenant_id, last_deleted_seq_num);

CREATE INDEX IF NOT EXISTS idx_retention_events_executed_at
    ON audit_retention_events (executed_at DESC);

-- GIN index on the hash array — lets validate_chain lookup a candidate
-- prev_hash in O(log n) across every retention event for the tenant
-- rather than scanning every array linearly. Optional: costs ~extra
-- 1x the array size to maintain; worth it on any tenant with > ~10k
-- accumulated retention events.
CREATE INDEX IF NOT EXISTS idx_retention_events_deleted_hashes
    ON audit_retention_events USING GIN (deleted_entry_hashes);

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
