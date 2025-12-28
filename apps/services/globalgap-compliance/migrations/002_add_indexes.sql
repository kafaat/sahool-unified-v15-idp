-- ============================================================================
-- GlobalGAP Compliance - Performance Indexes
-- فهارس الأداء لنظام الامتثال GlobalGAP
-- ============================================================================
--
-- This migration adds performance indexes for efficient querying
-- يضيف هذا الترحيل فهارس الأداء للاستعلام الفعال
--
-- Created: 2025-12-28
-- Version: 1.0.0
-- ============================================================================

-- ============================================================================
-- Indexes for: globalgap_registrations
-- فهارس لجدول: تسجيلات GlobalGAP
-- ============================================================================

-- Index on farm_id for fast lookup by farm
-- فهرس على farm_id للبحث السريع حسب المزرعة
CREATE INDEX IF NOT EXISTS idx_globalgap_registrations_farm_id
    ON globalgap_registrations(farm_id);
COMMENT ON INDEX idx_globalgap_registrations_farm_id IS 'Fast lookup by farm - البحث السريع حسب المزرعة';

-- Index on GGN for fast lookup by GlobalGAP Number
-- فهرس على GGN للبحث السريع حسب رقم GlobalGAP
CREATE INDEX IF NOT EXISTS idx_globalgap_registrations_ggn
    ON globalgap_registrations(ggn) WHERE ggn IS NOT NULL;
COMMENT ON INDEX idx_globalgap_registrations_ggn IS 'Fast lookup by GlobalGAP Number - البحث السريع حسب رقم GlobalGAP';

-- Index on certificate_status for filtering active certificates
-- فهرس على certificate_status لتصفية الشهادات النشطة
CREATE INDEX IF NOT EXISTS idx_globalgap_registrations_status
    ON globalgap_registrations(certificate_status);
COMMENT ON INDEX idx_globalgap_registrations_status IS 'Filter by certificate status - التصفية حسب حالة الشهادة';

-- Composite index on farm_id and certificate_status for common queries
-- فهرس مركب على farm_id و certificate_status للاستعلامات الشائعة
CREATE INDEX IF NOT EXISTS idx_globalgap_registrations_farm_status
    ON globalgap_registrations(farm_id, certificate_status);
COMMENT ON INDEX idx_globalgap_registrations_farm_status IS 'Farm and status composite lookup - البحث المركب حسب المزرعة والحالة';

-- Index on valid_to for finding expiring certificates
-- فهرس على valid_to للعثور على الشهادات المنتهية الصلاحية
CREATE INDEX IF NOT EXISTS idx_globalgap_registrations_valid_to
    ON globalgap_registrations(valid_to) WHERE valid_to IS NOT NULL;
COMMENT ON INDEX idx_globalgap_registrations_valid_to IS 'Find expiring certificates - العثور على الشهادات المنتهية الصلاحية';

-- Index on scope for filtering by certification type
-- فهرس على scope للتصفية حسب نوع الشهادة
CREATE INDEX IF NOT EXISTS idx_globalgap_registrations_scope
    ON globalgap_registrations(scope);
COMMENT ON INDEX idx_globalgap_registrations_scope IS 'Filter by certification scope - التصفية حسب نطاق الشهادة';

-- Index on created_at for chronological queries
-- فهرس على created_at للاستعلامات الزمنية
CREATE INDEX IF NOT EXISTS idx_globalgap_registrations_created_at
    ON globalgap_registrations(created_at DESC);
COMMENT ON INDEX idx_globalgap_registrations_created_at IS 'Chronological ordering - الترتيب الزمني';

-- ============================================================================
-- Indexes for: compliance_records
-- فهارس لجدول: سجلات الامتثال
-- ============================================================================

-- Index on registration_id for fast lookup by registration
-- فهرس على registration_id للبحث السريع حسب التسجيل
CREATE INDEX IF NOT EXISTS idx_compliance_records_registration_id
    ON compliance_records(registration_id);
COMMENT ON INDEX idx_compliance_records_registration_id IS 'Fast lookup by registration - البحث السريع حسب التسجيل';

-- Index on audit_date for chronological queries and date range filters
-- فهرس على audit_date للاستعلامات الزمنية وتصفيات النطاق الزمني
CREATE INDEX IF NOT EXISTS idx_compliance_records_audit_date
    ON compliance_records(audit_date DESC) WHERE audit_date IS NOT NULL;
COMMENT ON INDEX idx_compliance_records_audit_date IS 'Chronological audit queries - الاستعلامات الزمنية للتدقيق';

-- Composite index on registration_id and audit_date for audit history
-- فهرس مركب على registration_id و audit_date لتاريخ التدقيق
CREATE INDEX IF NOT EXISTS idx_compliance_records_reg_audit_date
    ON compliance_records(registration_id, audit_date DESC);
COMMENT ON INDEX idx_compliance_records_reg_audit_date IS 'Audit history per registration - تاريخ التدقيق لكل تسجيل';

-- Index on checklist_version for version-specific queries
-- فهرس على checklist_version للاستعلامات الخاصة بالإصدار
CREATE INDEX IF NOT EXISTS idx_compliance_records_checklist_version
    ON compliance_records(checklist_version);
COMMENT ON INDEX idx_compliance_records_checklist_version IS 'Filter by checklist version - التصفية حسب إصدار قائمة التحقق';

-- Index on overall_compliance for finding low compliance scores
-- فهرس على overall_compliance للعثور على درجات الامتثال المنخفضة
CREATE INDEX IF NOT EXISTS idx_compliance_records_overall_compliance
    ON compliance_records(overall_compliance) WHERE overall_compliance IS NOT NULL;
COMMENT ON INDEX idx_compliance_records_overall_compliance IS 'Sort and filter by compliance score - الترتيب والتصفية حسب درجة الامتثال';

-- Index on major_must_score for critical compliance queries
-- فهرس على major_must_score للاستعلامات الحرجة للامتثال
CREATE INDEX IF NOT EXISTS idx_compliance_records_major_must_score
    ON compliance_records(major_must_score) WHERE major_must_score IS NOT NULL;
COMMENT ON INDEX idx_compliance_records_major_must_score IS 'Filter by major must score - التصفية حسب درجة الامتثال الرئيسية';

-- Index on created_at for recent audits
-- فهرس على created_at للتدقيقات الأخيرة
CREATE INDEX IF NOT EXISTS idx_compliance_records_created_at
    ON compliance_records(created_at DESC);
COMMENT ON INDEX idx_compliance_records_created_at IS 'Recent audits lookup - البحث عن التدقيقات الأخيرة';

-- ============================================================================
-- Indexes for: checklist_responses
-- فهارس لجدول: استجابات قائمة التحقق
-- ============================================================================

-- Index on compliance_record_id for fast lookup by compliance record
-- فهرس على compliance_record_id للبحث السريع حسب سجل الامتثال
CREATE INDEX IF NOT EXISTS idx_checklist_responses_compliance_record_id
    ON checklist_responses(compliance_record_id);
COMMENT ON INDEX idx_checklist_responses_compliance_record_id IS 'Fast lookup by compliance record - البحث السريع حسب سجل الامتثال';

-- Index on checklist_item_id for analyzing specific checklist items across audits
-- فهرس على checklist_item_id لتحليل عناصر قائمة التحقق المحددة عبر التدقيقات
CREATE INDEX IF NOT EXISTS idx_checklist_responses_item_id
    ON checklist_responses(checklist_item_id);
COMMENT ON INDEX idx_checklist_responses_item_id IS 'Analyze specific checklist items - تحليل عناصر قائمة التحقق المحددة';

-- Index on response for filtering by compliance status
-- فهرس على response للتصفية حسب حالة الامتثال
CREATE INDEX IF NOT EXISTS idx_checklist_responses_response
    ON checklist_responses(response);
COMMENT ON INDEX idx_checklist_responses_response IS 'Filter by response type - التصفية حسب نوع الاستجابة';

-- Composite index on compliance_record_id and response for filtering responses
-- فهرس مركب على compliance_record_id و response لتصفية الاستجابات
CREATE INDEX IF NOT EXISTS idx_checklist_responses_record_response
    ON checklist_responses(compliance_record_id, response);
COMMENT ON INDEX idx_checklist_responses_record_response IS 'Filter responses per record - تصفية الاستجابات لكل سجل';

-- Composite index on checklist_item_id and response for item analysis
-- فهرس مركب على checklist_item_id و response لتحليل العنصر
CREATE INDEX IF NOT EXISTS idx_checklist_responses_item_response
    ON checklist_responses(checklist_item_id, response);
COMMENT ON INDEX idx_checklist_responses_item_response IS 'Item compliance analysis - تحليل امتثال العنصر';

-- Index on created_at for chronological queries
-- فهرس على created_at للاستعلامات الزمنية
CREATE INDEX IF NOT EXISTS idx_checklist_responses_created_at
    ON checklist_responses(created_at DESC);
COMMENT ON INDEX idx_checklist_responses_created_at IS 'Chronological ordering - الترتيب الزمني';

-- ============================================================================
-- Indexes for: non_conformances
-- فهارس لجدول: عدم المطابقات
-- ============================================================================

-- Index on compliance_record_id for fast lookup by compliance record
-- فهرس على compliance_record_id للبحث السريع حسب سجل الامتثال
CREATE INDEX IF NOT EXISTS idx_non_conformances_compliance_record_id
    ON non_conformances(compliance_record_id);
COMMENT ON INDEX idx_non_conformances_compliance_record_id IS 'Fast lookup by compliance record - البحث السريع حسب سجل الامتثال';

-- Index on severity for filtering critical non-conformances
-- فهرس على severity لتصفية عدم المطابقات الحرجة
CREATE INDEX IF NOT EXISTS idx_non_conformances_severity
    ON non_conformances(severity);
COMMENT ON INDEX idx_non_conformances_severity IS 'Filter by severity level - التصفية حسب مستوى الخطورة';

-- Index on status for filtering open/resolved issues
-- فهرس على status لتصفية القضايا المفتوحة/المحلولة
CREATE INDEX IF NOT EXISTS idx_non_conformances_status
    ON non_conformances(status);
COMMENT ON INDEX idx_non_conformances_status IS 'Filter by resolution status - التصفية حسب حالة الحل';

-- Composite index on status and severity for prioritization queries
-- فهرس مركب على status و severity لاستعلامات الأولوية
CREATE INDEX IF NOT EXISTS idx_non_conformances_status_severity
    ON non_conformances(status, severity);
COMMENT ON INDEX idx_non_conformances_status_severity IS 'Prioritize by status and severity - تحديد الأولوية حسب الحالة والخطورة';

-- Index on due_date for finding overdue corrective actions
-- فهرس على due_date للعثور على الإجراءات التصحيحية المتأخرة
CREATE INDEX IF NOT EXISTS idx_non_conformances_due_date
    ON non_conformances(due_date) WHERE due_date IS NOT NULL AND status != 'RESOLVED' AND status != 'VERIFIED';
COMMENT ON INDEX idx_non_conformances_due_date IS 'Find overdue actions - العثور على الإجراءات المتأخرة';

-- Index on resolved_date for tracking resolution timeline
-- فهرس على resolved_date لتتبع الجدول الزمني للحل
CREATE INDEX IF NOT EXISTS idx_non_conformances_resolved_date
    ON non_conformances(resolved_date DESC) WHERE resolved_date IS NOT NULL;
COMMENT ON INDEX idx_non_conformances_resolved_date IS 'Track resolution timeline - تتبع الجدول الزمني للحل';

-- Index on checklist_item_id for analyzing recurring non-conformances
-- فهرس على checklist_item_id لتحليل عدم المطابقات المتكررة
CREATE INDEX IF NOT EXISTS idx_non_conformances_checklist_item_id
    ON non_conformances(checklist_item_id);
COMMENT ON INDEX idx_non_conformances_checklist_item_id IS 'Analyze recurring non-conformances - تحليل عدم المطابقات المتكررة';

-- Composite index on compliance_record_id and status for record-specific filtering
-- فهرس مركب على compliance_record_id و status للتصفية الخاصة بالسجل
CREATE INDEX IF NOT EXISTS idx_non_conformances_record_status
    ON non_conformances(compliance_record_id, status);
COMMENT ON INDEX idx_non_conformances_record_status IS 'Filter non-conformances per record - تصفية عدم المطابقات لكل سجل';

-- ============================================================================
-- Additional Performance Optimizations
-- تحسينات الأداء الإضافية
-- ============================================================================

-- Update table statistics for query optimizer
-- تحديث إحصائيات الجدول لمحسن الاستعلام
ANALYZE globalgap_registrations;
ANALYZE compliance_records;
ANALYZE checklist_responses;
ANALYZE non_conformances;

-- ============================================================================
-- End of Performance Indexes Migration
-- نهاية ترحيل فهارس الأداء
-- ============================================================================
