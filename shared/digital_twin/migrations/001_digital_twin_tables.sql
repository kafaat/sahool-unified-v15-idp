-- SPDX-License-Identifier: Proprietary
-- Copyright (c) 2026 KAFAAT - SAHOOL Platform
-- ============================================================
-- Digital Twin Tables - جداول التوأم الرقمي
-- Migration: 001_digital_twin_tables.sql
-- ============================================================
-- Run with:  psql $DATABASE_URL -f 001_digital_twin_tables.sql
-- ============================================================

-- 1. Daily simulation state for every field
-- ------------------------------------------
CREATE TABLE IF NOT EXISTS field_daily_state (
    id                      uuid PRIMARY KEY,
    tenant_id               uuid        NOT NULL,
    field_id                uuid        NOT NULL,
    day                     date        NOT NULL,

    -- Agro-meteorology
    et0_mm                  double precision,
    etc_mm                  double precision,

    -- Crop growth
    phenology_stage         text,
    gdd_cum                 double precision,
    lai                     double precision,
    biomass_kg_ha           double precision,
    root_depth_m            double precision,

    -- Soil water balance
    soil_water_mm           double precision,
    depletion_mm            double precision,
    water_stress            double precision,
    n_stress                double precision,
    runoff_mm               double precision,
    deep_perc_mm            double precision,

    -- Applied inputs that day
    rainfall_mm             double precision NOT NULL DEFAULT 0,
    irrigation_applied_mm   double precision NOT NULL DEFAULT 0,
    nitrogen_applied_kg_ha  double precision NOT NULL DEFAULT 0,

    -- Quality / assimilation
    confidence              double precision NOT NULL DEFAULT 0.6,
    assimilation_flags      text[]           NOT NULL DEFAULT '{}',
    notes                   text,

    created_at              timestamptz      NOT NULL DEFAULT now(),
    updated_at              timestamptz      NOT NULL DEFAULT now(),

    CONSTRAINT uq_fds_tenant_field_day UNIQUE (tenant_id, field_id, day)
);

CREATE INDEX IF NOT EXISTS idx_fds_field_day
    ON field_daily_state (tenant_id, field_id, day DESC);

-- Auto-update updated_at
CREATE OR REPLACE FUNCTION _set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'trg_fds_updated_at'
    ) THEN
        CREATE TRIGGER trg_fds_updated_at
        BEFORE UPDATE ON field_daily_state
        FOR EACH ROW EXECUTE FUNCTION _set_updated_at();
    END IF;
END;
$$;


-- 2. Field observations (NDVI, LAI, soil moisture, etc.)
-- -------------------------------------------------------
CREATE TABLE IF NOT EXISTS field_observation (
    id          uuid        PRIMARY KEY,
    tenant_id   uuid        NOT NULL,
    field_id    uuid        NOT NULL,
    ts          timestamptz NOT NULL,

    source      text        NOT NULL,   -- sentinel-2 | uav | iot_sensor | manual
    obs_type    text        NOT NULL,   -- ndvi | lai | soil_moisture | canopy_temp | …
    value       double precision NOT NULL,
    quality     double precision NOT NULL DEFAULT 0.7,
    meta        jsonb       NOT NULL DEFAULT '{}'::jsonb,

    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_obs_field_ts
    ON field_observation (tenant_id, field_id, ts DESC);

CREATE INDEX IF NOT EXISTS idx_obs_type_ts
    ON field_observation (tenant_id, field_id, obs_type, ts DESC);


-- 3. Irrigation recommendations
-- ------------------------------
CREATE TABLE IF NOT EXISTS irrigation_recommendation (
    id              uuid        PRIMARY KEY,
    tenant_id       uuid        NOT NULL,
    field_id        uuid        NOT NULL,
    day             date        NOT NULL,

    recommended_mm  double precision NOT NULL,
    reason_codes    text[]      NOT NULL DEFAULT '{}',
    explanation     jsonb       NOT NULL DEFAULT '{}'::jsonb,
    confidence      double precision NOT NULL DEFAULT 0.7,

    created_at      timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_irec_tenant_field_day UNIQUE (tenant_id, field_id, day)
);

CREATE INDEX IF NOT EXISTS idx_irec_field_day
    ON irrigation_recommendation (tenant_id, field_id, day DESC);
