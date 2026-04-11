-- Migration: 002_cooperative_bookings_orders
-- Description: Create cooperative_bookings and cooperative_purchase_orders tables
--              required by admin portal (Wave 2) - حجوزات وأوامر شراء التعاونية
-- Service: cooperative-service
-- Date: 2026-04-10

-- Ensure uuid generation is available
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ─────────────────────────────────────────────────────────────────────────────
-- Cooperative Bookings (admin-portal workflow) - حجوزات التعاونية
-- Distinct from existing resource_bookings; supports approve/reject workflow
-- with optimistic locking via the `version` column.
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cooperative_bookings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    cooperative_id UUID NOT NULL,
    resource_id UUID,
    requested_by UUID NOT NULL,
    booking_date TIMESTAMPTZ NOT NULL,
    duration_hours NUMERIC(5,2),
    status TEXT NOT NULL DEFAULT 'pending', -- pending|approved|rejected|cancelled|completed
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    notes TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

COMMENT ON TABLE cooperative_bookings IS 'Cooperative booking approval workflow - سير عمل الموافقة على الحجوزات';

CREATE INDEX IF NOT EXISTS idx_coop_bookings_tenant_status
    ON cooperative_bookings (tenant_id, status, booking_date DESC);

CREATE INDEX IF NOT EXISTS idx_coop_bookings_cooperative
    ON cooperative_bookings (cooperative_id);

-- ─────────────────────────────────────────────────────────────────────────────
-- Cooperative Purchase Orders - أوامر شراء التعاونية
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS cooperative_purchase_orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    cooperative_id UUID NOT NULL,
    supplier_id UUID,
    total_amount NUMERIC(14,2) NOT NULL,
    currency TEXT DEFAULT 'SAR',
    status TEXT NOT NULL DEFAULT 'draft', -- draft|sent|received|paid|cancelled
    items JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

COMMENT ON TABLE cooperative_purchase_orders IS 'Cooperative purchase orders - أوامر شراء التعاونية';

CREATE INDEX IF NOT EXISTS idx_coop_po_tenant
    ON cooperative_purchase_orders (tenant_id, status, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_coop_po_cooperative
    ON cooperative_purchase_orders (cooperative_id);

-- Migration tracking
INSERT INTO public._migrations (name) VALUES ('002_cooperative_bookings_orders')
ON CONFLICT (name) DO NOTHING;
