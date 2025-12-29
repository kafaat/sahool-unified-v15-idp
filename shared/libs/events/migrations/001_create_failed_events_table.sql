-- Migration: Create failed_events table for Dead Letter Queue
-- Description: Stores failed NATS events with full error context for analysis and retry
-- Author: SAHOOL Platform Team
-- Date: 2025-01-15

-- Create failed_events table
CREATE TABLE IF NOT EXISTS failed_events (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Event identification
    event_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    original_subject VARCHAR(255) NOT NULL,

    -- Source context
    source_service VARCHAR(100) NOT NULL,
    tenant_id VARCHAR(255),
    field_id VARCHAR(255),
    farmer_id VARCHAR(255),

    -- Error context
    error_message TEXT NOT NULL,
    error_type VARCHAR(100) NOT NULL,
    stack_trace TEXT,

    -- Retry context
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    first_attempt_at TIMESTAMPTZ NOT NULL,
    last_attempt_at TIMESTAMPTZ NOT NULL,

    -- Original data (JSONB for better querying and indexing)
    original_data JSONB NOT NULL,
    original_headers JSONB NOT NULL DEFAULT '{}'::jsonb,

    -- DLQ metadata
    dlq_timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    dlq_reason VARCHAR(100) NOT NULL DEFAULT 'max_retries_exceeded',

    -- Processing status
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    resolved_at TIMESTAMPTZ,
    resolution_notes TEXT,

    -- Alerting
    alert_sent BOOLEAN NOT NULL DEFAULT FALSE,
    alert_sent_at TIMESTAMPTZ,

    -- Audit timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_failed_events_event_id ON failed_events(event_id);
CREATE INDEX IF NOT EXISTS idx_failed_events_event_type ON failed_events(event_type);
CREATE INDEX IF NOT EXISTS idx_failed_events_source_service ON failed_events(source_service);
CREATE INDEX IF NOT EXISTS idx_failed_events_tenant_id ON failed_events(tenant_id) WHERE tenant_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_failed_events_field_id ON failed_events(field_id) WHERE field_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_failed_events_farmer_id ON failed_events(farmer_id) WHERE farmer_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_failed_events_error_type ON failed_events(error_type);
CREATE INDEX IF NOT EXISTS idx_failed_events_status ON failed_events(status);
CREATE INDEX IF NOT EXISTS idx_failed_events_dlq_timestamp ON failed_events(dlq_timestamp);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_failed_events_event_type_status ON failed_events(event_type, status);
CREATE INDEX IF NOT EXISTS idx_failed_events_source_service_status ON failed_events(source_service, status);
CREATE INDEX IF NOT EXISTS idx_failed_events_tenant_status ON failed_events(tenant_id, status) WHERE tenant_id IS NOT NULL;

-- JSONB indexes for querying original_data
CREATE INDEX IF NOT EXISTS idx_failed_events_original_data_gin ON failed_events USING gin(original_data);

-- Trigger to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_failed_events_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_failed_events_updated_at ON failed_events;
CREATE TRIGGER trigger_failed_events_updated_at
    BEFORE UPDATE ON failed_events
    FOR EACH ROW
    EXECUTE FUNCTION update_failed_events_updated_at();

-- Comments for documentation
COMMENT ON TABLE failed_events IS 'Dead Letter Queue - stores failed NATS events for analysis and retry';
COMMENT ON COLUMN failed_events.id IS 'Primary key UUID';
COMMENT ON COLUMN failed_events.event_id IS 'Original event ID from the event data';
COMMENT ON COLUMN failed_events.event_type IS 'Event type extracted from subject (e.g., ndvi_computed)';
COMMENT ON COLUMN failed_events.original_subject IS 'Original NATS subject where event was published';
COMMENT ON COLUMN failed_events.source_service IS 'Service that originally published the event';
COMMENT ON COLUMN failed_events.error_message IS 'Error message from the exception';
COMMENT ON COLUMN failed_events.error_type IS 'Python exception type (e.g., ValueError, DatabaseError)';
COMMENT ON COLUMN failed_events.retry_count IS 'Number of processing attempts before DLQ routing';
COMMENT ON COLUMN failed_events.max_retries IS 'Maximum retries configured for the consumer';
COMMENT ON COLUMN failed_events.original_data IS 'Complete original event data as JSONB';
COMMENT ON COLUMN failed_events.status IS 'Processing status: pending, retried, resolved, discarded';
COMMENT ON COLUMN failed_events.dlq_reason IS 'Reason for DLQ routing: max_retries_exceeded, validation_error, etc.';
COMMENT ON COLUMN failed_events.alert_sent IS 'Whether an alert was sent for this failure';

-- Grant permissions (adjust as needed for your environment)
-- GRANT SELECT, INSERT, UPDATE ON failed_events TO sahool_app;
-- GRANT USAGE, SELECT ON SEQUENCE failed_events_id_seq TO sahool_app;

-- Verify table creation
SELECT 'Failed events table created successfully' AS status,
       COUNT(*) AS index_count
FROM pg_indexes
WHERE tablename = 'failed_events';
