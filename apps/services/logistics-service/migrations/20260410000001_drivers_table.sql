-- Migration: Create drivers table
-- Service: logistics-service (port 8167)
-- Wave: 2
-- Date: 2026-04-10
--
-- Introduces a first-class Driver entity for fleet management. Drivers are
-- tenant-scoped and referenced by vehicles/shipments. Schema deliberately
-- mirrors the Pydantic `Driver` model in src/main.py.

BEGIN;

CREATE TABLE IF NOT EXISTS drivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    name TEXT NOT NULL,
    name_ar TEXT,
    phone TEXT,
    license_number TEXT,
    vehicle_type TEXT,
    status TEXT NOT NULL DEFAULT 'active',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

-- Active-driver lookups scoped by tenant are the hot path for the
-- GET /api/v1/logistics/drivers endpoint. Partial index on active status.
CREATE INDEX IF NOT EXISTS idx_drivers_tenant ON drivers (tenant_id) WHERE status = 'active';

-- Additional lookup indices
CREATE INDEX IF NOT EXISTS idx_drivers_license ON drivers (license_number) WHERE license_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_drivers_vehicle_type ON drivers (vehicle_type) WHERE vehicle_type IS NOT NULL;

-- Constraint: status must be one of the supported enum values
ALTER TABLE drivers
    DROP CONSTRAINT IF EXISTS drivers_status_check;
ALTER TABLE drivers
    ADD CONSTRAINT drivers_status_check
    CHECK (status IN ('active', 'inactive'));

COMMIT;
