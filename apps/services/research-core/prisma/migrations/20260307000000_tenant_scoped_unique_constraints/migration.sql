-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Replace global unique constraints with tenant-scoped constraints
-- استبدال قيود التفرد العامة بقيود مقيدة بالمستأجر
-- Purpose: Ensure uniqueness is scoped per tenant, not globally
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Drop existing global unique constraints
-- الخطوة 1: حذف قيود التفرد العامة الحالية

-- germplasm.accessionNumber: global → tenant-scoped
DROP INDEX IF EXISTS "germplasm_accessionNumber_key";

-- seed_lots.lotNumber: global → tenant-scoped
DROP INDEX IF EXISTS "seed_lots_lotNumber_key";

-- research_daily_logs.offlineId: global → tenant-scoped
DROP INDEX IF EXISTS "research_daily_logs_offlineId_key";

-- lab_samples.sampleCode: global → tenant-scoped
DROP INDEX IF EXISTS "lab_samples_sampleCode_key";

-- digital_signatures (entityType, entityId, signerId, purpose): global → tenant-scoped
DROP INDEX IF EXISTS "digital_signatures_entityType_entityId_signerId_purpose_key";

-- Step 2: Create tenant-scoped unique constraints
-- الخطوة 2: إنشاء قيود التفرد المقيدة بالمستأجر

CREATE UNIQUE INDEX IF NOT EXISTS "uq_germplasm_tenant_accession"
  ON "germplasm" ("tenant_id", "accessionNumber");

CREATE UNIQUE INDEX IF NOT EXISTS "uq_seed_lot_tenant_number"
  ON "seed_lots" ("tenant_id", "lotNumber");

CREATE UNIQUE INDEX IF NOT EXISTS "uq_daily_log_tenant_offline"
  ON "research_daily_logs" ("tenant_id", "offlineId");

CREATE UNIQUE INDEX IF NOT EXISTS "uq_lab_sample_tenant_code"
  ON "lab_samples" ("tenant_id", "sampleCode");

CREATE UNIQUE INDEX IF NOT EXISTS "uq_signature_tenant_entity"
  ON "digital_signatures" ("tenant_id", "entityType", "entityId", "signerId", "purpose");
