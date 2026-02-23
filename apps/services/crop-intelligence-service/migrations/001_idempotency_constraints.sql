-- Migration: 001_idempotency_constraints
-- Date: 2026-02-23
-- Purpose: Add idempotency constraints for replay safety
-- Scope: field_observation UNIQUE constraint + processed_events dedup table

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Add UNIQUE constraint on field_observation to prevent duplicate inserts
--    on replay.  The natural key is (tenant, field, obs_type, timestamp, source).
-- ─────────────────────────────────────────────────────────────────────────────

CREATE UNIQUE INDEX IF NOT EXISTS uq_field_observation_natural_key
    ON field_observation (tenant_id, field_id, obs_type, ts, source);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Processed events table for consumer-side event_id deduplication.
--    Services can INSERT-or-IGNORE before processing a message and skip
--    if the event_id was already handled.
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS processed_events (
    event_id    TEXT        PRIMARY KEY,
    subject     TEXT        NOT NULL,
    service     TEXT        NOT NULL,
    processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Auto-purge entries older than 7 days (lightweight, no TimescaleDB needed)
CREATE INDEX IF NOT EXISTS idx_processed_events_ttl
    ON processed_events (processed_at);

-- Cleanup job (run via pg_cron or application-level scheduled task):
-- DELETE FROM processed_events WHERE processed_at < NOW() - INTERVAL '7 days';
