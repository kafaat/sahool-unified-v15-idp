-- Migration: 002_add_version_and_split_status
-- Description: Add optimistic locking (version) column and extend batch status enum with 'split'
-- Service: traceability-service
-- Date: 2026-04-10
-- Wave: Sahool Wave 2

-- ─────────────────────────────────────────────────────────────────────────────
-- 1. Add version column for optimistic locking - إضافة عمود الإصدار للقفل التفاؤلي
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE produce_batches
    ADD COLUMN IF NOT EXISTS version INTEGER NOT NULL DEFAULT 1;

CREATE INDEX IF NOT EXISTS idx_batches_version ON produce_batches(id, version);

COMMENT ON COLUMN produce_batches.version IS
    'Optimistic locking version - incremented on every update - الإصدار للقفل التفاؤلي';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2. Auto-increment version on UPDATE via trigger - زيادة الإصدار تلقائياً
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION bump_produce_batch_version()
RETURNS TRIGGER AS $$
BEGIN
    -- Only bump version if user did not explicitly set it (optimistic locking path)
    IF NEW.version = OLD.version THEN
        NEW.version := OLD.version + 1;
    END IF;
    NEW.updated_at := NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_batches_version ON produce_batches;
CREATE TRIGGER trigger_batches_version
    BEFORE UPDATE ON produce_batches
    FOR EACH ROW
    EXECUTE FUNCTION bump_produce_batch_version();

-- ─────────────────────────────────────────────────────────────────────────────
-- 3. Extend batch status CHECK constraint to include 'split'
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE produce_batches DROP CONSTRAINT IF EXISTS valid_batch_status;
ALTER TABLE produce_batches ADD CONSTRAINT valid_batch_status CHECK (status IN (
    'created', 'harvested', 'in_processing', 'in_storage',
    'in_transit', 'at_retail', 'sold', 'expired', 'split', 'recalled'
));

-- ─────────────────────────────────────────────────────────────────────────────
-- 4. Extend supply_chain_events event_type to include 'recall'
-- ─────────────────────────────────────────────────────────────────────────────
ALTER TABLE supply_chain_events DROP CONSTRAINT IF EXISTS valid_event_type;
ALTER TABLE supply_chain_events ADD CONSTRAINT valid_event_type CHECK (event_type IN (
    'harvest', 'processing', 'storage', 'transport',
    'retail', 'consumer_scan', 'quality_check', 'certification', 'recall'
));

-- Migration tracking
INSERT INTO public._migrations (name) VALUES ('002_add_version_and_split_status')
ON CONFLICT (name) DO NOTHING;
