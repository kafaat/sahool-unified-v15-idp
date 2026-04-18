-- SAHOOL Outbox Messages Table
-- جدول رسائل الصندوق الصادر
--
-- Canonical schema for the asyncpg-based transactional outbox pattern.
-- Services that still use SQLAlchemy (`OutboxEvent` / `OutboxWorker`) use
-- the separate `outbox_events` table defined in `models.py`.
--
-- See: shared/libs/outbox/README.md
CREATE TABLE IF NOT EXISTS outbox_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    tenant_id TEXT,
    subject TEXT NOT NULL,
    payload BYTEA NOT NULL,
    headers JSONB DEFAULT '{}'::jsonb,
    published_at TIMESTAMPTZ,
    retry_count INT NOT NULL DEFAULT 0
);

-- Hot path: relay polls unpublished rows in insertion order.
CREATE INDEX IF NOT EXISTS idx_outbox_unpublished
    ON outbox_messages (created_at)
    WHERE published_at IS NULL;

-- Secondary path: tenant-scoped inspection / replay.
CREATE INDEX IF NOT EXISTS idx_outbox_tenant
    ON outbox_messages (tenant_id, created_at);
