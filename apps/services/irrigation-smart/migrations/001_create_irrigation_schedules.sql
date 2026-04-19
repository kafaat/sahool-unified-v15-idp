-- Migration: 001_create_irrigation_schedules
-- Description: Minimal schema for /api/v1/irrigation/schedules CRUD.
-- Service: irrigation-smart
-- Date: 2026-04-18
--
-- Only the table that the HTTP CRUD endpoints use is created here. Other
-- tables referenced by the (currently orphaned) src/database_utils.py
-- class are tracked in a separate migration track when/if that code is
-- wired into the lifespan.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- irrigation_schedules — per-event schedule row.
-- The POST /api/v1/irrigation/schedules endpoint writes here; GET reads.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS irrigation_schedules (
    id                    UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id             VARCHAR(100) NOT NULL,
    field_id              VARCHAR(100) NOT NULL,
    plan_id               UUID,
    irrigation_date       DATE         NOT NULL,
    start_time            TIME,
    duration_minutes      INTEGER      NOT NULL,
    water_amount_liters   DECIMAL(12, 2) NOT NULL,
    urgency               VARCHAR(20),
    method                VARCHAR(50),
    status                VARCHAR(30)  NOT NULL DEFAULT 'active',
    notes                 TEXT,
    created_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at            TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    -- Values aligned with the web IrrigationStatus union
    -- (apps/web/src/lib/api/types.ts:312 → 'active' | 'paused' | 'completed').
    -- Legacy pending/cancelled/skipped dropped from the CHECK so the DB
    -- rejects them explicitly (they were never emitted by the contract).
    CONSTRAINT valid_schedule_status CHECK (
        status IN ('active', 'paused', 'completed')
    )
);

-- Defensive migration for deployments that already ran an earlier revision
-- of this file (when the CHECK accepted pending/cancelled/skipped): re-map
-- those rows to the closest contract value before the stricter CHECK
-- replaces the old one. No-op on a fresh DB because the table was just
-- created with the right CHECK.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE table_name = 'irrigation_schedules'
          AND constraint_name = 'valid_schedule_status'
    ) THEN
        UPDATE irrigation_schedules
           SET status = CASE
                            WHEN status = 'pending'   THEN 'active'
                            WHEN status IN ('cancelled', 'skipped') THEN 'paused'
                            ELSE status
                        END
         WHERE status IN ('pending', 'cancelled', 'skipped');
    END IF;
END $$;

-- Primary list query: WHERE tenant_id=$1 [AND field_id=$2] ORDER BY irrigation_date
CREATE INDEX IF NOT EXISTS idx_irrigation_schedules_tenant_field_date
    ON irrigation_schedules (tenant_id, field_id, irrigation_date DESC);
CREATE INDEX IF NOT EXISTS idx_irrigation_schedules_tenant_date
    ON irrigation_schedules (tenant_id, irrigation_date DESC);

COMMENT ON TABLE irrigation_schedules IS
    'Per-event irrigation schedule rows managed by /api/v1/irrigation/schedules CRUD.';

-- Migration bookkeeping
-- The platform already owns `public._migrations` with schema
-- (id SERIAL PRIMARY KEY, name VARCHAR UNIQUE, applied_at TIMESTAMP),
-- created by infrastructure/core/postgres/migrations/001_init_extensions.sql.
-- We only INSERT here; defining a different schema would shadow the
-- platform tracker and break tooling that reads it.
INSERT INTO public._migrations (name)
VALUES ('001_create_irrigation_schedules')
ON CONFLICT (name) DO NOTHING;
