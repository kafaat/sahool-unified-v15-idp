-- Migration: 001_create_field_indicators
-- Description: Create field_indicators table consumed by indicators-service
-- Service: indicators-service
-- Date: 2026-04-18
--
-- Schema derived from INSERT at src/main.py:397 and the SELECT queries
-- elsewhere in that file. Primary lookup is (tenant_id, field_id,
-- indicator_type); the ON CONFLICT in the INSERT demands a unique index
-- on exactly that triplet.

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS field_indicators (
    -- Surrogate key so external references can use a stable id.
    id              UUID         PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Natural key. INSERT uses
    --   ON CONFLICT (tenant_id, field_id, indicator_type)
    -- so a UNIQUE constraint is required (see below).
    tenant_id       VARCHAR(100) NOT NULL,
    field_id        VARCHAR(100) NOT NULL,
    indicator_type  VARCHAR(50)  NOT NULL,

    -- Value is stored as JSONB — main.py does json.dumps(value) at
    -- insert (line 404) and the SELECT side reads it back as JSON.
    value           JSONB        NOT NULL,

    calculated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),

    CONSTRAINT uq_field_indicator UNIQUE (tenant_id, field_id, indicator_type)
);

-- Hot query: WHERE field_id = $1 AND indicator_type = $2 AND tenant_id = $3
CREATE INDEX IF NOT EXISTS idx_field_indicators_lookup
    ON field_indicators (tenant_id, field_id, indicator_type);

-- Secondary: WHERE field_id = $1 AND tenant_id = $2 (list all indicators)
CREATE INDEX IF NOT EXISTS idx_field_indicators_by_field
    ON field_indicators (tenant_id, field_id, calculated_at DESC);

COMMENT ON TABLE field_indicators IS
    'Per-field aggregated indicators (NDVI, EVI, LAI, soil moisture, etc.) with trend metadata in value JSONB.';

-- Migration bookkeeping (follows the pattern used by traceability-service).
CREATE TABLE IF NOT EXISTS public._migrations (
    name        VARCHAR(255) PRIMARY KEY,
    applied_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
INSERT INTO public._migrations (name)
VALUES ('001_create_field_indicators')
ON CONFLICT (name) DO NOTHING;
