-- Migration: 002_create_irrigation_support_tables
-- Description: Support tables queried by src/database_utils.py (IrrigationDB).
-- Service: irrigation-smart
-- Date: 2026-04-18
--
-- NOTE: `irrigation_schedules` lives in 001_create_irrigation_schedules.sql
-- because the HTTP CRUD at /api/v1/irrigation/schedules needs it at boot.
-- This migration adds the four orphan-use tables that database_utils.py
-- references but that the lifespan does NOT yet wire a pool for. Schema
-- derived directly from the INSERT/SELECT bindings in database_utils.py.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ─────────────────────────────────────────────────────────────────────────────
-- irrigation_plans — plan header saved by save_irrigation_plan()
-- Matches INSERT at database_utils.py:134.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS irrigation_plans (
    id                  UUID PRIMARY KEY,
    field_id            VARCHAR(100) NOT NULL,
    crop                VARCHAR(100) NOT NULL,
    growth_stage        VARCHAR(50)  NOT NULL,
    total_water_m3      DECIMAL(12, 3) NOT NULL,
    estimated_cost_yer  DECIMAL(12, 2) NOT NULL,
    schedules_count     INTEGER       NOT NULL DEFAULT 0,
    tenant_id           VARCHAR(100),
    created_at          TIMESTAMPTZ   NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_irrigation_plans_tenant_field
    ON irrigation_plans(tenant_id, field_id, created_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- irrigation_executions — actual irrigation events for history/analytics
-- Matches SELECT at database_utils.py:67 and INSERT at 207.
-- References irrigation_schedules (created by migration 001).
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS irrigation_executions (
    id                UUID PRIMARY KEY,
    field_id          VARCHAR(100) NOT NULL,
    plan_id           UUID REFERENCES irrigation_plans(id) ON DELETE SET NULL,
    schedule_id       UUID REFERENCES irrigation_schedules(id) ON DELETE SET NULL,
    amount_mm         DECIMAL(10, 3) NOT NULL,
    duration_minutes  INTEGER       NOT NULL,
    method            VARCHAR(50),
    executed_at       TIMESTAMPTZ   NOT NULL,
    tenant_id         VARCHAR(100),
    created_at        TIMESTAMPTZ   NOT NULL DEFAULT NOW()
);
-- Query pattern: WHERE field_id = $1 AND executed_at >= $2 AND tenant_id = $4
CREATE INDEX IF NOT EXISTS idx_irrigation_executions_tenant_field_time
    ON irrigation_executions(tenant_id, field_id, executed_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- soil_moisture_readings — sensor ingest, deduped on (sensor_id, reading_time)
-- Matches SELECT at database_utils.py:98 and INSERT at 246.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS soil_moisture_readings (
    id                UUID PRIMARY KEY,
    field_id          VARCHAR(100) NOT NULL,
    sensor_id         VARCHAR(100) NOT NULL,
    reading_time      TIMESTAMPTZ  NOT NULL,
    depth_cm          INTEGER      NOT NULL DEFAULT 30,
    moisture_percent  DECIMAL(6, 3),
    temperature_c     DECIMAL(6, 3),
    ec_ds_m           DECIMAL(6, 3),
    tenant_id         VARCHAR(100),
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_soil_moisture_sensor_time UNIQUE (sensor_id, reading_time)
);
CREATE INDEX IF NOT EXISTS idx_soil_moisture_tenant_field_time
    ON soil_moisture_readings(tenant_id, field_id, reading_time DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- water_balance — daily ET / rainfall / irrigation roll-up per field
-- Matches SELECT at database_utils.py:284.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS water_balance (
    field_id         VARCHAR(100) NOT NULL,
    date             DATE         NOT NULL,
    et_mm            DECIMAL(8, 3) NOT NULL DEFAULT 0,
    rainfall_mm      DECIMAL(8, 3) NOT NULL DEFAULT 0,
    irrigation_mm    DECIMAL(8, 3) NOT NULL DEFAULT 0,
    tenant_id        VARCHAR(100),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    PRIMARY KEY (tenant_id, field_id, date)
);
CREATE INDEX IF NOT EXISTS idx_water_balance_field_date
    ON water_balance(field_id, date DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- Migration bookkeeping
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public._migrations (
    name        VARCHAR(255) PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO public._migrations (name)
VALUES ('002_create_irrigation_support_tables')
ON CONFLICT (name) DO NOTHING;
