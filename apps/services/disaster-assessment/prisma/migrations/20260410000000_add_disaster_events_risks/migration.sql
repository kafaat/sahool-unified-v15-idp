-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add disaster_events and disaster_risks tables
-- إضافة جداول أحداث الكوارث ومخاطرها
-- ═══════════════════════════════════════════════════════════════════════════════
--
-- Purpose:
--   Provide a purpose-built storage layer for the new /api/v1/disasters/events/*
--   and /api/v1/disasters/risks/* endpoints. The existing `disaster_reports`
--   and `field_assessments` tables remain the primary source of truth; these
--   tables act as a denormalized view suitable for high-cardinality per-field
--   risk tracking and structured event streaming.
--
-- Safety:
--   CREATE IF NOT EXISTS is used throughout. Tables are additive and do not
--   alter existing columns or indexes. Requires the pgcrypto extension for
--   gen_random_uuid() (already enabled in upstream init migrations).
--
-- NOTE: This migration is intentionally NOT run by CI automation. It is
--       provided as-is for DBAs to apply during the Wave 2 rollout.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=additive-disaster-tables-with-concurrent-indexes
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "postgis";

-- ─────────────────────────────────────────────────────────────────────────────
-- disaster_events
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS disaster_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    event_type TEXT NOT NULL, -- flood|drought|frost|storm|pest_outbreak|disease_outbreak|fire
    severity TEXT NOT NULL,   -- low|medium|high|critical
    location GEOGRAPHY(POINT, 4326),
    field_id UUID,
    description TEXT,
    description_ar TEXT,
    reported_by UUID,
    reported_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status TEXT NOT NULL DEFAULT 'active', -- active|monitoring|resolved
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_disaster_events_tenant
    ON disaster_events (tenant_id, status, reported_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- disaster_risks
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS disaster_risks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    risk_type TEXT NOT NULL,
    field_id UUID,
    risk_score NUMERIC(4,2),  -- 0.00 to 10.00
    probability NUMERIC(4,2), -- 0.00 to 1.00
    mitigation_plan TEXT,
    mitigation_plan_ar TEXT,
    computed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_disaster_risks_tenant_field
    ON disaster_risks (tenant_id, field_id);
