-- SAHOOL Outbox Messages Table
-- جدول رسائل الصندوق الصادر
--
-- Canonical schema for the asyncpg-based transactional outbox pattern.
-- Services that still use SQLAlchemy (`OutboxEvent` / `OutboxWorker`) use
-- the separate `outbox_events` table defined in `models.py`.
--
-- See: shared/libs/outbox/README.md

-- The gen_random_uuid() default below ships with PostgreSQL 13+ core
-- (via pgcrypto), but older clusters or custom images may omit the
-- extension. Enable it idempotently so a fresh database applying this
-- migration doesn't fail with "function gen_random_uuid() does not exist".
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS outbox_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tenant_id TEXT,
    subject TEXT NOT NULL,
    payload BYTEA NOT NULL,
    headers JSONB DEFAULT '{}'::jsonb,
    published_at TIMESTAMPTZ,
    retry_count INT NOT NULL DEFAULT 0,
    -- Claim state for multi-replica relay. When a relay worker picks a
    -- batch, it stamps claimed_at+claimed_by atomically inside the fetch
    -- transaction. Other relays filter `claimed_at IS NULL OR claim is
    -- expired` in their SELECT so the same row cannot be published twice
    -- by two workers. A TTL on claimed_at protects against a worker that
    -- crashed mid-publish.
    claimed_at TIMESTAMPTZ,
    claimed_by TEXT
);

-- Idempotent migrations for existing deployments that pre-date the claim
-- columns: ADD COLUMN IF NOT EXISTS is a no-op when the column already
-- exists, so this file can be re-applied safely.
ALTER TABLE outbox_messages ADD COLUMN IF NOT EXISTS claimed_at TIMESTAMPTZ;
ALTER TABLE outbox_messages ADD COLUMN IF NOT EXISTS claimed_by TEXT;

-- Dead-letter support: rows that have exhausted all relay retries are
-- stamped with dead_lettered_at so the relay skips them permanently.
-- A separate monitoring query / replay tool can inspect these rows.
ALTER TABLE outbox_messages ADD COLUMN IF NOT EXISTS dead_lettered_at TIMESTAMPTZ;

-- Hot path: relay polls rows that are pending (not published, not dead-lettered)
-- in insertion order, filtering out rows currently claimed by a running worker.
CREATE INDEX IF NOT EXISTS idx_outbox_pending
    ON outbox_messages (created_at)
    WHERE published_at IS NULL AND dead_lettered_at IS NULL;

-- Legacy index kept for compatibility with existing deployments; the new
-- idx_outbox_pending index is more selective.
CREATE INDEX IF NOT EXISTS idx_outbox_unpublished
    ON outbox_messages (created_at)
    WHERE published_at IS NULL;

-- Secondary path: tenant-scoped inspection / replay.
CREATE INDEX IF NOT EXISTS idx_outbox_tenant
    ON outbox_messages (tenant_id, created_at);

-- ---------------------------------------------------------------------------
-- Replay Lifecycle State Machine
-- آلة حالة دورة حياة إعادة التشغيل
-- ---------------------------------------------------------------------------
--
-- Tracks the lifecycle of replayed rows through the relay pipeline.
-- Values:
--   NULL          — row has never been replayed (initial state / normal DLQ)
--   'REPLAYING'   — dead_lettered_at cleared by reset_dead_lettered(); the
--                   relay is attempting to re-publish this row.
--   'RECOVERED'   — relay successfully published the row after a replay;
--                   the row is fully healed.
--   'FAILED_FINAL'— relay dead-lettered the row a second time after a replay
--                   attempt; the failure is persistent and replay cannot fix it.
--
-- The partial index on 'REPLAYING' rows lets the relay quickly find rows
-- currently in-flight under a replay attempt for forensic inspection.
-- ---------------------------------------------------------------------------

ALTER TABLE outbox_messages ADD COLUMN IF NOT EXISTS replay_state TEXT;

-- Partial index: relay/ops tools can quickly locate in-flight replay attempts.
CREATE INDEX IF NOT EXISTS idx_outbox_replaying
    ON outbox_messages (id)
    WHERE replay_state = 'REPLAYING';

-- ---------------------------------------------------------------------------
-- Distributed Replay Ledger
-- جدول سجل إعادة التشغيل الموزّع
-- ---------------------------------------------------------------------------
--
-- Tracks every successful ``reset_dead_lettered()`` call across ALL service
-- instances.  ``DistributedReplayGovernor`` queries this table to enforce a
-- cluster-wide sliding-window rate limit per NATS subject, preventing replay
-- storms even when multiple processes run concurrently.
--
-- Design notes:
--   • TIMESTAMPTZ is used so timezone differences between replicas cannot
--     corrupt window comparisons.
--   • ``instance_id`` records which pod/process triggered the replay for
--     forensic tracing (pairs with the ``replayed_by`` in outbox_published
--     log records).
--   • Rows are never updated — only inserted.  Old rows outside the longest
--     possible window are safe to purge periodically:
--       DELETE FROM outbox_replay_ledger
--       WHERE replayed_at < NOW() - INTERVAL '7 days';
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS outbox_replay_ledger (
    id           BIGSERIAL    PRIMARY KEY,
    subject      TEXT         NOT NULL,
    replayed_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    replayed_by  TEXT         NOT NULL DEFAULT 'system',
    instance_id  TEXT
);

-- Index for the sliding-window COUNT query executed by
-- DistributedReplayGovernor.check():
--   SELECT COUNT(*) FROM outbox_replay_ledger
--   WHERE subject = $1 AND replayed_at > NOW() - $2 * INTERVAL '1 second'
CREATE INDEX IF NOT EXISTS idx_replay_ledger_subject_time
    ON outbox_replay_ledger (subject, replayed_at DESC);
