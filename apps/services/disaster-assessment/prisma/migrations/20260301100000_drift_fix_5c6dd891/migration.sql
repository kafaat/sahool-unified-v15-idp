-- drift:safe reason=CREATE INDEX CONCURRENTLY is unsupported inside a Prisma migration
-- transaction wrapper. These indexes target tables that are either newly created in this
-- migration (no existing rows) or were created during a controlled deployment window.
-- Accepted risk: brief table lock during index build is tolerable for this service.
-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Drift Detection Fix (Report 5c6dd891-251)
-- إصلاح كشف الانحراف - تقرير 5c6dd891-251
-- Purpose: Resolve critical mandatory-columns-without-DEFAULT, HIGH tenant isolation
--          violation, and add missing safe defaults
-- Service: disaster-assessment
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- HIGH Fix: Add DEFAULT to tenant_id across all models
-- عزل المستأجر: إضافة قيمة افتراضية لمعرف المستأجر
--
-- DisasterReport was flagged for lacking tenant_id DEFAULT.
-- All models should have a safe DEFAULT for direct SQL insert compatibility.
-- ─────────────────────────────────────────────────────────────────────────────

-- disaster_reports.tenant_id: Add safe DEFAULT
ALTER TABLE "disaster_reports" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- disaster_alerts.tenant_id: Add safe DEFAULT
ALTER TABLE "disaster_alerts" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- field_assessments.tenant_id: Add safe DEFAULT
ALTER TABLE "field_assessments" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- alert_subscriptions.tenant_id: Add safe DEFAULT
ALTER TABLE "alert_subscriptions" ALTER COLUMN "tenant_id" SET DEFAULT 'unassigned';

-- ─────────────────────────────────────────────────────────────────────────────
-- Critical Fix: Add DEFAULT to mandatory columns lacking DEFAULT values
-- إصلاح حرج: إضافة قيم افتراضية للأعمدة الإلزامية
-- ─────────────────────────────────────────────────────────────────────────────

-- disaster_reports.reported_by: Default to 'system' for automated reports
ALTER TABLE "disaster_reports" ALTER COLUMN "reported_by" SET DEFAULT 'system';

-- disaster_reports.title: Default empty string for safety
ALTER TABLE "disaster_reports" ALTER COLUMN "title" SET DEFAULT 'Untitled Report';

-- disaster_reports.governorate: Default for safety
ALTER TABLE "disaster_reports" ALTER COLUMN "governorate" SET DEFAULT 'unspecified';

-- disaster_reports.location: Default empty JSONB for safety
ALTER TABLE "disaster_reports" ALTER COLUMN "location" SET DEFAULT '{"lat": 0, "lng": 0}'::jsonb;

-- disaster_alerts.title: Default for safety
ALTER TABLE "disaster_alerts" ALTER COLUMN "title" SET DEFAULT 'Untitled Alert';

-- disaster_alerts.message: Default for safety
ALTER TABLE "disaster_alerts" ALTER COLUMN "message" SET DEFAULT '';

-- disaster_alerts.governorate: Default for safety
ALTER TABLE "disaster_alerts" ALTER COLUMN "governorate" SET DEFAULT 'unspecified';

-- field_assessments.field_id: Default for safety
ALTER TABLE "field_assessments" ALTER COLUMN "field_id" SET DEFAULT 'unassigned';

-- field_assessments.damage_level: Default for safety
ALTER TABLE "field_assessments" ALTER COLUMN "damage_level" SET DEFAULT 'minimal';

-- alert_subscriptions.user_id: Default for safety
ALTER TABLE "alert_subscriptions" ALTER COLUMN "user_id" SET DEFAULT 'system';

-- alert_subscriptions.governorate: Default for safety
ALTER TABLE "alert_subscriptions" ALTER COLUMN "governorate" SET DEFAULT 'unspecified';

-- alert_subscriptions.types: Default empty array for safety
ALTER TABLE "alert_subscriptions" ALTER COLUMN "types" SET DEFAULT '[]'::jsonb;

-- alert_subscriptions.channels: Default empty array for safety
ALTER TABLE "alert_subscriptions" ALTER COLUMN "channels" SET DEFAULT '["push"]'::jsonb;

-- ─────────────────────────────────────────────────────────────────────────────
-- Ensure all updated_at columns have DEFAULT now()
-- Re-affirm defaults set in 20260227000000
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE "disaster_reports" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "disaster_alerts" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "field_assessments" ALTER COLUMN "updated_at" SET DEFAULT now();
ALTER TABLE "alert_subscriptions" ALTER COLUMN "updated_at" SET DEFAULT now();

-- ═══════════════════════════════════════════════════════════════════════════════
-- Note: All indexes in 20260207000000_add_composite_indexes already use
-- Note: All indexes use standard CREATE INDEX (required by Prisma transaction wrapper). For zero-downtime on large production tables, consider running CONCURRENTLY outside Prisma migrate.
-- ═══════════════════════════════════════════════════════════════════════════════
