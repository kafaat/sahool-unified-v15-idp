-- ============================================================================
-- GlobalGAP Compliance Schema
-- مخطط قاعدة بيانات الامتثال لـ GlobalGAP
-- ============================================================================
--
-- This schema manages GlobalGAP certification compliance tracking for farms
-- يدير هذا المخطط تتبع الامتثال لشهادات GlobalGAP للمزارع
--
-- Created: 2025-12-28
-- Version: 1.0.0
-- ============================================================================

-- Enable UUID extension if not already enabled
-- تمكين امتداد UUID إذا لم يكن ممكّنًا بالفعل
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- Table: globalgap_registrations
-- جدول: تسجيلات GlobalGAP
-- ============================================================================
-- Stores farm GlobalGAP registration and certification information
-- يخزن معلومات تسجيل وشهادات GlobalGAP للمزارع
-- ============================================================================

CREATE TABLE IF NOT EXISTS globalgap_registrations (
    -- Primary Key / المفتاح الأساسي
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Farm Reference / مرجع المزرعة
    farm_id UUID NOT NULL,
    -- COMMENT: Links to the farm entity in the farm management system
    -- تعليق: يرتبط بكيان المزرعة في نظام إدارة المزارع

    -- GlobalGAP Number (GGN) / رقم GlobalGAP
    ggn VARCHAR(13) UNIQUE,
    -- COMMENT: 13-digit unique GlobalGAP Number assigned to the farm
    -- تعليق: رقم GlobalGAP الفريد المكون من 13 رقمًا المخصص للمزرعة

    -- Registration Details / تفاصيل التسجيل
    registration_date TIMESTAMP,
    -- COMMENT: Date when farm registered with GlobalGAP
    -- تعليق: تاريخ تسجيل المزرعة في GlobalGAP

    -- Certificate Status / حالة الشهادة
    certificate_status VARCHAR(20),
    -- COMMENT: Current status (ACTIVE, SUSPENDED, EXPIRED, WITHDRAWN)
    -- تعليق: الحالة الحالية (نشط، معلق، منتهي الصلاحية، مسحوب)

    -- Validity Period / فترة الصلاحية
    valid_from DATE,
    -- COMMENT: Certificate validity start date
    -- تعليق: تاريخ بداية صلاحية الشهادة

    valid_to DATE,
    -- COMMENT: Certificate validity end date
    -- تعليق: تاريخ انتهاء صلاحية الشهادة

    -- Certification Scope / نطاق الشهادة
    scope VARCHAR(50),
    -- COMMENT: Certification scope (e.g., FRUIT_VEGETABLES, FLOWERS_ORNAMENTALS)
    -- تعليق: نطاق الشهادة (مثل: الفواكه والخضروات، الزهور والنباتات الزينة)

    -- Audit Metadata / بيانات التدقيق الوصفية
    created_at TIMESTAMP DEFAULT NOW(),
    -- COMMENT: Record creation timestamp
    -- تعليق: الطابع الزمني لإنشاء السجل

    updated_at TIMESTAMP DEFAULT NOW(),
    -- COMMENT: Record last update timestamp
    -- تعليق: الطابع الزمني لآخر تحديث للسجل

    -- Constraints / القيود
    CONSTRAINT check_valid_dates CHECK (valid_to IS NULL OR valid_from IS NULL OR valid_to >= valid_from),
    CONSTRAINT check_certificate_status CHECK (certificate_status IN ('ACTIVE', 'SUSPENDED', 'EXPIRED', 'WITHDRAWN', 'PENDING'))
);

-- Add comments to table
-- إضافة تعليقات على الجدول
COMMENT ON TABLE globalgap_registrations IS 'GlobalGAP farm registrations and certifications - تسجيلات وشهادات GlobalGAP للمزارع';
COMMENT ON COLUMN globalgap_registrations.id IS 'Unique registration identifier - معرف التسجيل الفريد';
COMMENT ON COLUMN globalgap_registrations.farm_id IS 'Reference to farm entity - مرجع لكيان المزرعة';
COMMENT ON COLUMN globalgap_registrations.ggn IS '13-digit GlobalGAP Number - رقم GlobalGAP المكون من 13 رقمًا';
COMMENT ON COLUMN globalgap_registrations.registration_date IS 'Registration date with GlobalGAP - تاريخ التسجيل في GlobalGAP';
COMMENT ON COLUMN globalgap_registrations.certificate_status IS 'Current certificate status - حالة الشهادة الحالية';
COMMENT ON COLUMN globalgap_registrations.valid_from IS 'Certificate validity start date - تاريخ بداية صلاحية الشهادة';
COMMENT ON COLUMN globalgap_registrations.valid_to IS 'Certificate validity end date - تاريخ انتهاء صلاحية الشهادة';
COMMENT ON COLUMN globalgap_registrations.scope IS 'Certification scope - نطاق الشهادة';

-- ============================================================================
-- Table: compliance_records
-- جدول: سجلات الامتثال
-- ============================================================================
-- Stores audit results and compliance scores
-- يخزن نتائج التدقيق ودرجات الامتثال
-- ============================================================================

CREATE TABLE IF NOT EXISTS compliance_records (
    -- Primary Key / المفتاح الأساسي
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Registration Reference / مرجع التسجيل
    registration_id UUID NOT NULL REFERENCES globalgap_registrations(id) ON DELETE CASCADE,
    -- COMMENT: Links to the GlobalGAP registration
    -- تعليق: يرتبط بتسجيل GlobalGAP

    -- Checklist Information / معلومات قائمة التحقق
    checklist_version VARCHAR(10),
    -- COMMENT: Version of the GlobalGAP checklist used (e.g., "5.3", "6.0")
    -- تعليق: إصدار قائمة التحقق GlobalGAP المستخدمة (مثل: "5.3"، "6.0")

    -- Audit Date / تاريخ التدقيق
    audit_date DATE,
    -- COMMENT: Date when the audit was conducted
    -- تعليق: تاريخ إجراء التدقيق

    -- Compliance Scores / درجات الامتثال
    major_must_score DECIMAL(5,2),
    -- COMMENT: Percentage score for Major Must compliance points (0-100)
    -- تعليق: نسبة درجة نقاط الامتثال الرئيسية الإلزامية (0-100)

    minor_must_score DECIMAL(5,2),
    -- COMMENT: Percentage score for Minor Must compliance points (0-100)
    -- تعليق: نسبة درجة نقاط الامتثال الفرعية الإلزامية (0-100)

    overall_compliance DECIMAL(5,2),
    -- COMMENT: Overall compliance percentage (0-100)
    -- تعليق: نسبة الامتثال الإجمالية (0-100)

    -- Auditor Notes / ملاحظات المدقق
    auditor_notes TEXT,
    -- COMMENT: General notes and observations from the auditor
    -- تعليق: ملاحظات وملاحظات عامة من المدقق

    -- Audit Metadata / بيانات التدقيق الوصفية
    created_at TIMESTAMP DEFAULT NOW(),
    -- COMMENT: Record creation timestamp
    -- تعليق: الطابع الزمني لإنشاء السجل

    -- Constraints / القيود
    CONSTRAINT check_major_must_score CHECK (major_must_score IS NULL OR (major_must_score >= 0 AND major_must_score <= 100)),
    CONSTRAINT check_minor_must_score CHECK (minor_must_score IS NULL OR (minor_must_score >= 0 AND minor_must_score <= 100)),
    CONSTRAINT check_overall_compliance CHECK (overall_compliance IS NULL OR (overall_compliance >= 0 AND overall_compliance <= 100))
);

-- Add comments to table
-- إضافة تعليقات على الجدول
COMMENT ON TABLE compliance_records IS 'GlobalGAP audit results and compliance scores - نتائج تدقيق GlobalGAP ودرجات الامتثال';
COMMENT ON COLUMN compliance_records.id IS 'Unique compliance record identifier - معرف سجل الامتثال الفريد';
COMMENT ON COLUMN compliance_records.registration_id IS 'Reference to GlobalGAP registration - مرجع لتسجيل GlobalGAP';
COMMENT ON COLUMN compliance_records.checklist_version IS 'GlobalGAP checklist version - إصدار قائمة التحقق GlobalGAP';
COMMENT ON COLUMN compliance_records.audit_date IS 'Audit execution date - تاريخ تنفيذ التدقيق';
COMMENT ON COLUMN compliance_records.major_must_score IS 'Major Must compliance score (0-100%) - درجة الامتثال الرئيسية الإلزامية (0-100%)';
COMMENT ON COLUMN compliance_records.minor_must_score IS 'Minor Must compliance score (0-100%) - درجة الامتثال الفرعية الإلزامية (0-100%)';
COMMENT ON COLUMN compliance_records.overall_compliance IS 'Overall compliance percentage (0-100%) - نسبة الامتثال الإجمالية (0-100%)';
COMMENT ON COLUMN compliance_records.auditor_notes IS 'Auditor general notes - ملاحظات المدقق العامة';

-- ============================================================================
-- Table: checklist_responses
-- جدول: استجابات قائمة التحقق
-- ============================================================================
-- Stores individual checklist item responses during audits
-- يخزن استجابات عناصر قائمة التحقق الفردية أثناء التدقيق
-- ============================================================================

CREATE TABLE IF NOT EXISTS checklist_responses (
    -- Primary Key / المفتاح الأساسي
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Compliance Record Reference / مرجع سجل الامتثال
    compliance_record_id UUID NOT NULL REFERENCES compliance_records(id) ON DELETE CASCADE,
    -- COMMENT: Links to the compliance record
    -- تعليق: يرتبط بسجل الامتثال

    -- Checklist Item / عنصر قائمة التحقق
    checklist_item_id VARCHAR(20),
    -- COMMENT: GlobalGAP checklist item identifier (e.g., "FV.1.1.1")
    -- تعليق: معرف عنصر قائمة التحقق GlobalGAP (مثل: "FV.1.1.1")

    -- Response / الاستجابة
    response VARCHAR(20),
    -- COMMENT: Compliance response (COMPLIANT, NON_COMPLIANT, NOT_APPLICABLE, RECOMMENDATION)
    -- تعليق: استجابة الامتثال (ملتزم، غير ملتزم، غير قابل للتطبيق، توصية)

    -- Evidence / الأدلة
    evidence_path TEXT,
    -- COMMENT: Path to supporting evidence/documentation
    -- تعليق: المسار إلى الأدلة/الوثائق الداعمة

    -- Notes / الملاحظات
    notes TEXT,
    -- COMMENT: Detailed notes for this checklist item
    -- تعليق: ملاحظات مفصلة لعنصر قائمة التحقق هذا

    -- Audit Metadata / بيانات التدقيق الوصفية
    created_at TIMESTAMP DEFAULT NOW(),
    -- COMMENT: Record creation timestamp
    -- تعليق: الطابع الزمني لإنشاء السجل

    -- Constraints / القيود
    CONSTRAINT check_response CHECK (response IN ('COMPLIANT', 'NON_COMPLIANT', 'NOT_APPLICABLE', 'RECOMMENDATION'))
);

-- Add comments to table
-- إضافة تعليقات على الجدول
COMMENT ON TABLE checklist_responses IS 'Individual checklist item responses - استجابات عناصر قائمة التحقق الفردية';
COMMENT ON COLUMN checklist_responses.id IS 'Unique response identifier - معرف الاستجابة الفريد';
COMMENT ON COLUMN checklist_responses.compliance_record_id IS 'Reference to compliance record - مرجع لسجل الامتثال';
COMMENT ON COLUMN checklist_responses.checklist_item_id IS 'GlobalGAP checklist item ID - معرف عنصر قائمة التحقق GlobalGAP';
COMMENT ON COLUMN checklist_responses.response IS 'Compliance response status - حالة استجابة الامتثال';
COMMENT ON COLUMN checklist_responses.evidence_path IS 'Path to supporting evidence - المسار إلى الأدلة الداعمة';
COMMENT ON COLUMN checklist_responses.notes IS 'Detailed notes for checklist item - ملاحظات مفصلة لعنصر قائمة التحقق';

-- ============================================================================
-- Table: non_conformances
-- جدول: عدم المطابقات
-- ============================================================================
-- Tracks non-conformances and corrective actions
-- يتتبع عدم المطابقات والإجراءات التصحيحية
-- ============================================================================

CREATE TABLE IF NOT EXISTS non_conformances (
    -- Primary Key / المفتاح الأساسي
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Compliance Record Reference / مرجع سجل الامتثال
    compliance_record_id UUID NOT NULL REFERENCES compliance_records(id) ON DELETE CASCADE,
    -- COMMENT: Links to the compliance record where non-conformance was identified
    -- تعليق: يرتبط بسجل الامتثال الذي تم فيه تحديد عدم المطابقة

    -- Checklist Item / عنصر قائمة التحقق
    checklist_item_id VARCHAR(20),
    -- COMMENT: GlobalGAP checklist item that failed compliance
    -- تعليق: عنصر قائمة التحقق GlobalGAP الذي فشل في الامتثال

    -- Severity / الخطورة
    severity VARCHAR(20),
    -- COMMENT: Severity level (MAJOR, MINOR, RECOMMENDATION)
    -- تعليق: مستوى الخطورة (رئيسي، فرعي، توصية)

    -- Description / الوصف
    description TEXT,
    -- COMMENT: Detailed description of the non-conformance
    -- تعليق: وصف مفصل لعدم المطابقة

    -- Corrective Action / الإجراء التصحيحي
    corrective_action TEXT,
    -- COMMENT: Planned or implemented corrective action
    -- تعليق: الإجراء التصحيحي المخطط أو المنفذ

    -- Deadlines / المواعيد النهائية
    due_date DATE,
    -- COMMENT: Deadline for corrective action implementation
    -- تعليق: الموعد النهائي لتنفيذ الإجراء التصحيحي

    resolved_date DATE,
    -- COMMENT: Date when non-conformance was resolved
    -- تعليق: تاريخ حل عدم المطابقة

    -- Status / الحالة
    status VARCHAR(20),
    -- COMMENT: Current status (OPEN, IN_PROGRESS, RESOLVED, VERIFIED)
    -- تعليق: الحالة الحالية (مفتوح، قيد التنفيذ، تم الحل، تم التحقق)

    -- Constraints / القيود
    CONSTRAINT check_severity CHECK (severity IN ('MAJOR', 'MINOR', 'RECOMMENDATION')),
    CONSTRAINT check_status CHECK (status IN ('OPEN', 'IN_PROGRESS', 'RESOLVED', 'VERIFIED')),
    CONSTRAINT check_resolution_dates CHECK (resolved_date IS NULL OR due_date IS NULL OR resolved_date >= due_date OR resolved_date < due_date)
);

-- Add comments to table
-- إضافة تعليقات على الجدول
COMMENT ON TABLE non_conformances IS 'Non-conformances and corrective actions - عدم المطابقات والإجراءات التصحيحية';
COMMENT ON COLUMN non_conformances.id IS 'Unique non-conformance identifier - معرف عدم المطابقة الفريد';
COMMENT ON COLUMN non_conformances.compliance_record_id IS 'Reference to compliance record - مرجع لسجل الامتثال';
COMMENT ON COLUMN non_conformances.checklist_item_id IS 'Failed checklist item ID - معرف عنصر قائمة التحقق الفاشل';
COMMENT ON COLUMN non_conformances.severity IS 'Severity level (MAJOR/MINOR/RECOMMENDATION) - مستوى الخطورة (رئيسي/فرعي/توصية)';
COMMENT ON COLUMN non_conformances.description IS 'Detailed non-conformance description - وصف تفصيلي لعدم المطابقة';
COMMENT ON COLUMN non_conformances.corrective_action IS 'Corrective action plan - خطة الإجراء التصحيحي';
COMMENT ON COLUMN non_conformances.due_date IS 'Corrective action deadline - الموعد النهائي للإجراء التصحيحي';
COMMENT ON COLUMN non_conformances.resolved_date IS 'Resolution date - تاريخ الحل';
COMMENT ON COLUMN non_conformances.status IS 'Current status - الحالة الحالية';

-- ============================================================================
-- Triggers for automatic timestamp updates
-- المحفزات للتحديثات التلقائية للطابع الزمني
-- ============================================================================

-- Function to update updated_at timestamp
-- وظيفة لتحديث الطابع الزمني updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for globalgap_registrations
-- محفز لجدول تسجيلات GlobalGAP
CREATE TRIGGER update_globalgap_registrations_updated_at
    BEFORE UPDATE ON globalgap_registrations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- End of Initial Schema Migration
-- نهاية ترحيل المخطط الأولي
-- ============================================================================
