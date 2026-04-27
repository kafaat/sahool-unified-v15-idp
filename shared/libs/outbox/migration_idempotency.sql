-- SAHOOL Outbox — Write-Side Idempotency Pattern
-- =================================================
-- نمط idempotency على جانب الكتابة
--
-- PURPOSE
-- -------
-- The outbox relay guarantees at-least-once delivery.  If a relay worker
-- crashes after publishing to NATS but before marking the row as sent, the
-- same event will be re-delivered on restart.  The consumer's
-- ``processed_events`` dedup table prevents double side-effects *most* of
-- the time, but there is a narrow crash window where that guard can also be
-- missed.
--
-- The definitive protection is a UNIQUE constraint on the ``event_id`` column
-- of every side-effect table.  A duplicate INSERT then becomes a constraint
-- violation (idempotent by the DB engine) rather than silent double-write.
--
-- PATTERN
-- -------
-- Apply this migration to every table that is written as a side-effect of an
-- outbox event.  Replace <table_name> with your actual table name.
--
-- Step 1 — Add event_id column if not already present:

ALTER TABLE <table_name>
ADD COLUMN IF NOT EXISTS event_id UUID;

-- Step 2 — Backfill existing rows so the NOT NULL constraint can be applied
--           (use a sentinel value or the row's own PK turned into a UUID):
-- UPDATE <table_name> SET event_id = gen_random_uuid() WHERE event_id IS NULL;

-- Step 3 — Add the uniqueness constraint (idempotency guard):

ALTER TABLE <table_name>
ADD CONSTRAINT uq_<table_name>_event_id UNIQUE (event_id);

-- Step 4 (optional) — Make the column NOT NULL once all rows are backfilled:
-- ALTER TABLE <table_name> ALTER COLUMN event_id SET NOT NULL;


-- REAL EXAMPLE — crop_intelligence results table
-- ------------------------------------------------
-- If the crop-intelligence service writes to a `crop_analysis_results` table,
-- the migration looks like this:
--
-- ALTER TABLE crop_analysis_results
-- ADD COLUMN IF NOT EXISTS event_id UUID;
--
-- ALTER TABLE crop_analysis_results
-- ADD CONSTRAINT uq_crop_analysis_results_event_id UNIQUE (event_id);


-- CONSUMER INSERT PATTERN
-- -----------------------
-- When the consumer handles an event, use INSERT ... ON CONFLICT DO NOTHING
-- so a duplicate delivery is silently skipped instead of raising an error:
--
--     INSERT INTO crop_analysis_results (event_id, field_id, ndvi, ...)
--     VALUES ($1, $2, $3, ...)
--     ON CONFLICT ON CONSTRAINT uq_crop_analysis_results_event_id DO NOTHING;
--
-- Combined with the processed_events guard this gives two independent layers:
--   Layer 1 — processed_events: fast in-memory/DB dedup before any work
--   Layer 2 — UNIQUE(event_id): physical DB constraint, immune to race conditions


-- PROCESSED_EVENTS TABLE (reference — already created in core migration)
-- -----------------------------------------------------------------------
-- CREATE TABLE IF NOT EXISTS processed_events (
--     event_id   UUID        PRIMARY KEY,
--     processed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
--     subject    TEXT        NOT NULL,
--     tenant_id  TEXT
-- );
-- CREATE INDEX IF NOT EXISTS idx_processed_events_processed_at
--     ON processed_events (processed_at);
