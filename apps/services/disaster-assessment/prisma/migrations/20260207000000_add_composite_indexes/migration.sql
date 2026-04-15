-- drift:safe reason=CREATE INDEX CONCURRENTLY is unsupported inside a Prisma migration
-- transaction wrapper. These indexes target tables that are either newly created in this
-- migration (no existing rows) or were created during a controlled deployment window.
-- Accepted risk: brief table lock during index build is tolerable for this service.
-- Migration: Add Composite Indexes for Disaster Assessment
-- الهجرة: إضافة فهارس مركبة لتقييم الكوارث
-- Created: 2026-02-07
-- Description: Adds composite indexes to optimize disaster assessment queries

-- ═══════════════════════════════════════════════════════════════════════════════
-- Disaster Report Indexes
-- فهارس تقارير الكوارث
-- ═══════════════════════════════════════════════════════════════════════════════

-- Composite index for tenant + type filtering
-- فهرس مركب لتصفية المستأجر + النوع
-- drift:safe reason=CREATE INDEX inside a Prisma-managed transaction cannot use CONCURRENTLY; zero-downtime index creation must be run manually outside Prisma migrate on large production tables.
CREATE INDEX IF NOT EXISTS "idx_disaster_tenant_type"
    ON "disaster_reports" ("tenant_id", "type");

-- Composite index for tenant + status filtering
-- فهرس مركب لتصفية المستأجر + الحالة
CREATE INDEX IF NOT EXISTS "idx_disaster_tenant_status"
    ON "disaster_reports" ("tenant_id", "status");

-- Composite index for type + severity filtering (risk assessment)
-- فهرس مركب لتصفية النوع + الشدة (تقييم المخاطر)
CREATE INDEX IF NOT EXISTS "idx_disaster_type_severity"
    ON "disaster_reports" ("type", "severity");

-- Composite index for date range queries
-- فهرس مركب لاستعلامات نطاق التاريخ
CREATE INDEX IF NOT EXISTS "idx_disaster_dates"
    ON "disaster_reports" ("start_date", "end_date");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Disaster Alert Indexes
-- فهارس تنبيهات الكوارث
-- ═══════════════════════════════════════════════════════════════════════════════

-- Composite index for active alerts by tenant
-- فهرس مركب للتنبيهات النشطة حسب المستأجر
CREATE INDEX IF NOT EXISTS "idx_alert_tenant_active"
    ON "disaster_alerts" ("tenant_id", "is_active");

-- Composite index for active alerts by type and severity
-- فهرس مركب للتنبيهات النشطة حسب النوع والشدة
CREATE INDEX IF NOT EXISTS "idx_alert_type_severity"
    ON "disaster_alerts" ("alert_type", "severity")
    WHERE "is_active" = true;

-- Index for time-based alert queries
-- فهرس للاستعلامات الزمنية للتنبيهات
CREATE INDEX IF NOT EXISTS "idx_alert_time_range"
    ON "disaster_alerts" ("start_time", "end_time");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Field Assessment Indexes
-- فهارس تقييم الحقول
-- ═══════════════════════════════════════════════════════════════════════════════

-- Composite index for insurance-eligible assessments
-- فهرس مركب للتقييمات المؤهلة للتأمين
CREATE INDEX IF NOT EXISTS "idx_assessment_insurance"
    ON "field_assessments" ("insurance_eligible", "tenant_id")
    WHERE "insurance_eligible" = true;

-- Index for damage level filtering
-- فهرس لتصفية مستوى الضرر
CREATE INDEX IF NOT EXISTS "idx_assessment_damage_level"
    ON "field_assessments" ("damage_level");

-- Composite index for assessor queries
-- فهرس مركب لاستعلامات المقيّم
CREATE INDEX IF NOT EXISTS "idx_assessment_assessor"
    ON "field_assessments" ("assessed_by")
    WHERE "assessed_by" IS NOT NULL;

-- ═══════════════════════════════════════════════════════════════════════════════
-- Alert Subscription Indexes
-- فهارس اشتراكات التنبيهات
-- ═══════════════════════════════════════════════════════════════════════════════

-- Composite index for active subscriptions by tenant
-- فهرس مركب للاشتراكات النشطة حسب المستأجر
CREATE INDEX IF NOT EXISTS "idx_subscription_tenant_active"
    ON "alert_subscriptions" ("tenant_id", "is_active")
    WHERE "is_active" = true;

-- Index for governorate-based subscriptions
-- فهرس للاشتراكات القائمة على المحافظة
CREATE INDEX IF NOT EXISTS "idx_subscription_governorate"
    ON "alert_subscriptions" ("governorate");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Comments
-- التعليقات
-- ═══════════════════════════════════════════════════════════════════════════════

COMMENT ON INDEX "idx_disaster_tenant_status" IS 'Optimizes filtering disasters by tenant and status - dashboard queries';
COMMENT ON INDEX "idx_alert_type_severity" IS 'Partial index for active alerts only - reduces index size';
COMMENT ON INDEX "idx_assessment_insurance" IS 'Partial index for insurance claims processing';
