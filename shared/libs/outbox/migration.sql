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

-- Hot path: relay polls unpublished rows in insertion order, filtering
-- out rows currently claimed by a running worker.
CREATE INDEX IF NOT EXISTS idx_outbox_unpublished
    ON outbox_messages (created_at)
    WHERE published_at IS NULL;

-- Secondary path: tenant-scoped inspection / replay.
CREATE INDEX IF NOT EXISTS idx_outbox_tenant
    ON outbox_messages (tenant_id, created_at);
