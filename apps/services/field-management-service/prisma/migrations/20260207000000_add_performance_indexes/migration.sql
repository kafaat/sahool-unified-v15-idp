-- drift:safe reason=CREATE INDEX CONCURRENTLY is unsupported inside a Prisma migration
-- transaction wrapper. These indexes target tables that are either newly created in this
-- migration (no existing rows) or were created during a controlled deployment window.
-- Accepted risk: brief table lock during index build is tolerable for this service.
-- Migration: Add Performance Indexes
-- الهجرة: إضافة فهارس الأداء
-- Created: 2026-02-07
-- Description: Adds composite indexes for common query patterns to improve performance

-- ═══════════════════════════════════════════════════════════════════════════════
-- Farm Table Indexes
-- فهارس جدول المزارع
-- ═══════════════════════════════════════════════════════════════════════════════

-- Composite index for filtering active farms by tenant
-- فهرس مركب لتصفية المزارع النشطة حسب المستأجر
CREATE INDEX IF NOT EXISTS "idx_farm_tenant_active"
    ON "farms" ("tenant_id", "is_deleted");

-- Index for owner queries
-- فهرس لاستعلامات المالك
CREATE INDEX IF NOT EXISTS "idx_farm_owner"
    ON "farms" ("owner_id");

-- Index for time-based queries
-- فهرس للاستعلامات الزمنية
CREATE INDEX IF NOT EXISTS "idx_farm_created"
    ON "farms" ("created_at");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Field Table Indexes
-- فهارس جدول الحقول
-- ═══════════════════════════════════════════════════════════════════════════════

-- Index for farm relationship
-- فهرس لعلاقة المزرعة
CREATE INDEX IF NOT EXISTS "idx_field_farm"
    ON "fields" ("farm_id");

-- Composite index for tenant + status filtering (most common query pattern)
-- فهرس مركب لتصفية المستأجر + الحالة (نمط الاستعلام الأكثر شيوعًا)
CREATE INDEX IF NOT EXISTS "idx_field_tenant_status"
    ON "fields" ("tenant_id", "status");

-- Composite index for tenant + crop type filtering
-- فهرس مركب لتصفية المستأجر + نوع المحصول
CREATE INDEX IF NOT EXISTS "idx_field_tenant_crop"
    ON "fields" ("tenant_id", "crop_type");

-- Composite index for active fields by tenant
-- فهرس مركب للحقول النشطة حسب المستأجر
CREATE INDEX IF NOT EXISTS "idx_field_tenant_active"
    ON "fields" ("tenant_id", "is_deleted");

-- Index for owner queries
-- فهرس لاستعلامات المالك
CREATE INDEX IF NOT EXISTS "idx_field_owner"
    ON "fields" ("owner_id");

-- Index for planting date queries (seasonal analysis)
-- فهرس لاستعلامات تاريخ الزراعة (التحليل الموسمي)
CREATE INDEX IF NOT EXISTS "idx_field_planting"
    ON "fields" ("planting_date");

-- Index for harvest date queries (harvest planning)
-- فهرس لاستعلامات تاريخ الحصاد (تخطيط الحصاد)
CREATE INDEX IF NOT EXISTS "idx_field_harvest"
    ON "fields" ("expected_harvest");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Task Table Indexes
-- فهارس جدول المهام
-- ═══════════════════════════════════════════════════════════════════════════════

-- Index for assigned user queries
-- فهرس لاستعلامات المستخدم المعين
CREATE INDEX IF NOT EXISTS "idx_task_assigned"
    ON "tasks" ("assigned_to");

-- Index for creator queries
-- فهرس لاستعلامات المنشئ
CREATE INDEX IF NOT EXISTS "idx_task_creator"
    ON "tasks" ("created_by");

-- Index for task type filtering
-- فهرس لتصفية نوع المهمة
CREATE INDEX IF NOT EXISTS "idx_task_type"
    ON "tasks" ("task_type");

-- Index for priority filtering
-- فهرس لتصفية الأولوية
CREATE INDEX IF NOT EXISTS "idx_task_priority"
    ON "tasks" ("priority");

-- Composite index for pending/overdue tasks by due date
-- فهرس مركب للمهام المعلقة/المتأخرة حسب تاريخ الاستحقاق
CREATE INDEX IF NOT EXISTS "idx_task_status_due"
    ON "tasks" ("status", "due_date");

-- Composite index for field tasks by status
-- فهرس مركب لمهام الحقل حسب الحالة
CREATE INDEX IF NOT EXISTS "idx_task_field_status"
    ON "tasks" ("field_id", "status");

-- Composite index for user tasks by status
-- فهرس مركب لمهام المستخدم حسب الحالة
CREATE INDEX IF NOT EXISTS "idx_task_assigned_status"
    ON "tasks" ("assigned_to", "status");

-- Index for sync operations
-- فهرس لعمليات المزامنة
CREATE INDEX IF NOT EXISTS "idx_task_sync"
    ON "tasks" ("server_updated_at");

-- ═══════════════════════════════════════════════════════════════════════════════
-- NDVI Readings Partial Index (for high-quality readings only)
-- فهرس جزئي لقراءات NDVI (للقراءات عالية الجودة فقط)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Partial index for good quality readings (most commonly queried)
-- فهرس جزئي للقراءات ذات الجودة الجيدة (الأكثر استعلامًا)
CREATE INDEX IF NOT EXISTS "idx_ndvi_good_quality"
    ON "ndvi_readings" ("field_id", "captured_at")
    WHERE quality = 'good' OR quality IS NULL;

-- Index for source filtering
-- فهرس لتصفية المصدر
CREATE INDEX IF NOT EXISTS "idx_ndvi_source"
    ON "ndvi_readings" ("source");

-- ═══════════════════════════════════════════════════════════════════════════════
-- Comments
-- التعليقات
-- ═══════════════════════════════════════════════════════════════════════════════

COMMENT ON INDEX "idx_field_tenant_status" IS 'Optimizes filtering fields by tenant and status - most common query pattern';
COMMENT ON INDEX "idx_task_status_due" IS 'Optimizes finding pending/overdue tasks by due date';
COMMENT ON INDEX "idx_ndvi_good_quality" IS 'Partial index for high-quality NDVI readings - reduces index size';
