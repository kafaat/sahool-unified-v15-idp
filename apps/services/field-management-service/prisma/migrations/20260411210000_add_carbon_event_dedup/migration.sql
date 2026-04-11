-- drift:safe reason=Additive migration only. Single CREATE TABLE IF NOT EXISTS
-- with zero initial rows, no mutations to existing tables, no locks
-- observable to production traffic.

-- Migration: Add carbon_event_dedup table for carbon-service idempotency
-- الهجرة: إضافة جدول إزالة تكرار أحداث الكربون — الحماية من المعالجة المزدوجة
-- Created: 2026-04-11
--
-- Context (Phase 1 follow-up — kafaat/sahool-unified-v15-idp#1556):
--
-- `carbon-service` subscribes to `sahool.field.operation.recorded` on NATS
-- and auto-computes per-operation CO2 via IPCC Tier 1. NATS delivers
-- at-least-once, so a broker redelivery / consumer restart / network blip
-- can cause the same event to be processed twice. This table gives the
-- subscriber a persistent dedup layer keyed on (tenant_id, operation_id)
-- so replays become cheap no-ops instead of duplicate compute + duplicate
-- downstream outbox events.
--
-- The column shapes mirror the `shared/libs/saga/` convention (text PK
-- components, sha256 hex hash, nullable processed_at). We deliberately do
-- NOT use a UUID surrogate because the natural key (tenant_id, operation_id)
-- is already globally unique and cheaper for lookup.
--
-- Related code:
--   * apps/services/carbon-service/src/events/operation_subscriber.py
--     — reads this table inside `handler(msg)` before running the engine.
--   * shared/libs/saga/models.py
--     — existing saga idempotency pattern we mirror.

CREATE TABLE IF NOT EXISTS "carbon_event_dedup" (
    -- Natural composite primary key: one row per (tenant, operation).
    "tenant_id"    VARCHAR(100) NOT NULL,
    "operation_id" UUID NOT NULL,

    -- SHA-256 hex digest of the canonical JSON event payload. Used for
    -- tamper detection: if the same operation_id arrives with a different
    -- payload_hash we log a warning and still dedupe (the outbox should
    -- never emit a different payload for the same operation, so any
    -- divergence is a platform bug we want to surface).
    "payload_hash" CHAR(64) NOT NULL,

    -- When the subscriber first accepted and ran the event. INSERT happens
    -- before the engine runs so concurrent consumers in the same queue
    -- group see the lock immediately and skip.
    "processed_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Result bookkeeping — useful for the "why was carbon not computed?"
    -- forensics path and for the backfill worker that re-scans rows where
    -- the engine failed. Nullable so a failed dedup insert can be retried.
    "carbon_computed_at" TIMESTAMPTZ,
    "error_message"      TEXT,

    -- Correlation for tracing — every NATS envelope carries a
    -- correlation_id / event_id, we stash it so an operator can chase
    -- the end-to-end path through Jaeger.
    "correlation_id" VARCHAR(100),

    -- Row age — bounded by the GC job (see idx_carbon_dedup_age below).
    -- Events older than 30 days get pruned so the table stays small;
    -- replays that late would miss the dedup window but the UPDATE's
    -- `WHERE carbon_computed_at IS NULL` guard on field_operations
    -- still protects the business table (belt-and-suspenders).
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    PRIMARY KEY ("tenant_id", "operation_id")
);

-- Index for the nightly GC / TTL job that deletes rows older than 30
-- days. `DELETE FROM carbon_event_dedup WHERE created_at < NOW() - INTERVAL '30 days'`
-- runs in O(n_old) instead of O(all) thanks to this index.
CREATE INDEX IF NOT EXISTS "idx_carbon_dedup_age"
    ON "carbon_event_dedup" ("created_at");

-- Index for the "which events failed?" diagnostic query
--     SELECT * FROM carbon_event_dedup WHERE error_message IS NOT NULL
-- Used by the backfill worker and by ops dashboards.
CREATE INDEX IF NOT EXISTS "idx_carbon_dedup_errors"
    ON "carbon_event_dedup" ("tenant_id", "processed_at" DESC)
    WHERE "error_message" IS NOT NULL;

-- Note: the existing `idx_field_op_carbon_pending` partial index on
-- field_operations(WHERE carbon_computed_at IS NULL) is our second line
-- of defence. Even if a replay somehow bypasses carbon_event_dedup, the
-- UPDATE statement in operation_subscriber.py will include
-- `WHERE carbon_computed_at IS NULL` and silently no-op on the second run.
