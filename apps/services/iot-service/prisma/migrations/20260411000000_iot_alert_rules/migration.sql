-- drift:safe reason=additive-iot-alert-rules-table
-- Migration: iot_alert_rules (additive)
-- Adds a threshold-based alerting rules table for the IoT service.
-- This is an additive change: no existing tables or columns are modified,
-- and all DDL statements are idempotent (IF NOT EXISTS).

CREATE TABLE IF NOT EXISTS iot_alert_rules (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id UUID NOT NULL,
    sensor_id UUID,
    field_id UUID,
    metric TEXT NOT NULL,
    operator TEXT NOT NULL,
    threshold NUMERIC(14,4) NOT NULL,
    duration_seconds INTEGER DEFAULT 0,
    severity TEXT NOT NULL DEFAULT 'medium',
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    version INTEGER NOT NULL DEFAULT 1
);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_iot_alert_rules_tenant_enabled
    ON iot_alert_rules (tenant_id, enabled) WHERE enabled = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_iot_alert_rules_sensor
    ON iot_alert_rules (tenant_id, sensor_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_iot_alert_rules_field
    ON iot_alert_rules (tenant_id, field_id);
