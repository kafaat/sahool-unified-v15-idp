-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration 005: Disaster Management Tables (SUPERSEDED)
-- جداول إدارة الكوارث (تم استبدالها)
--
-- STATUS: SUPERSEDED by V20260130__add_disaster_tables.sql
--
-- This migration originally created disaster tables with VARCHAR IDs and
-- GEOGRAPHY types. It has been superseded by V20260130 which uses:
--   - UUID primary keys (platform standard)
--   - GEOMETRY types (PostGIS standard, consistent with field_boundaries)
--   - Additional fields (priority, status enum, sent_at, total_recipients)
--
-- This file is now a no-op stub to prevent conflicts. The disaster_affected_fields
-- junction table from the original migration has been added to V20260130.
-- ═══════════════════════════════════════════════════════════════════════════════

-- No-op: All disaster tables are created by V20260130__add_disaster_tables.sql
DO $$
BEGIN
    RAISE NOTICE 'Migration 005: Skipped - superseded by V20260130__add_disaster_tables.sql';
END;
$$;
