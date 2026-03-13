-- Migration: Disaster Management Tables
-- جداول إدارة الكوارث
-- Required by disaster-assessment service
--
-- NOTE: These tables are now managed by Prisma ORM migrations.
-- The disaster-assessment service runs `prisma migrate deploy` on startup,
-- which creates the correct schema (UUID IDs, native enums, proper columns).
--
-- This init script previously created tables with a different schema
-- (VARCHAR IDs, no enums, missing columns like description/description_ar)
-- which conflicted with Prisma migrations.
--
-- Table creation has been removed to prevent schema conflicts.
-- Prisma migrations are the single source of truth for:
--   - disaster_reports (with disaster_type, disaster_severity, disaster_status enums)
--   - disaster_alerts (with disaster_alert_type enum)
--   - field_assessments
--   - alert_subscriptions

SELECT 'Disaster tables managed by Prisma migrations (disaster-assessment service)' AS status;
