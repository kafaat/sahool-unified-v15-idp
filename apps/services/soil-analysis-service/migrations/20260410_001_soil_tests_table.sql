-- Migration: 20260410_001_soil_tests_table
-- Description: Wave 2 hardened soil_tests table with tenant isolation.
--              Create the canonical persistent store to replace the legacy
--              in-memory `_soil_tests: dict` used by src/api/v1/soil_tests.py.
-- Service: soil-analysis-service
-- Date: 2026-04-10
--
-- This migration is additive and idempotent so it can be applied even on
-- databases that already ran 001_create_soil_tests.sql.

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE IF NOT EXISTS soil_tests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    field_id UUID,
    sample_date TIMESTAMPTZ NOT NULL,
    ph NUMERIC(4,2),
    ec NUMERIC(6,2),
    organic_matter NUMERIC(5,2),
    nitrogen_nitrate_ppm NUMERIC(8,2),
    phosphorus_ppm NUMERIC(8,2),
    potassium_ppm NUMERIC(8,2),
    calcium_ppm NUMERIC(8,2),
    magnesium_ppm NUMERIC(8,2),
    raw_data JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX IF NOT EXISTS idx_soil_tests_tenant_field
    ON soil_tests (tenant_id, field_id);

-- Lab report uploads - مرفقات تقارير المعامل
CREATE TABLE IF NOT EXISTS soil_lab_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    test_id UUID,
    filename VARCHAR(512) NOT NULL,
    mime_type VARCHAR(128) NOT NULL,
    size_bytes BIGINT NOT NULL,
    storage_url TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_soil_lab_reports_tenant
    ON soil_lab_reports (tenant_id);
CREATE INDEX IF NOT EXISTS idx_soil_lab_reports_test
    ON soil_lab_reports (test_id);
