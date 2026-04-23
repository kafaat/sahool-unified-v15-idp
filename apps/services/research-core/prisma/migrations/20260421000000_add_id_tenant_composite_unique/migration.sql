-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) for IDOR defense-in-depth
-- إضافة قيد فريد مركّب (id, tenant_id) لتعزيز عزل المستأجرين
--
-- Purpose: Expose the Prisma `id_tenantId` accessor so the ~16 update / delete
-- call sites across experiments, treatments, protocols, samples, logs,
-- signatures modules bind tenantId atomically with id, eliminating the TOCTOU
-- window between `findOne(id, tenantId)` pre-check and subsequent
-- `update({id})`/`delete({id})`.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive constraint on already-unique id column — no row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_germplasm_id_tenant" ON "germplasm" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_seed_lot_id_tenant" ON "seed_lots" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_planting_id_tenant" ON "plantings" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_experiment_id_tenant" ON "experiments" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_research_protocol_id_tenant" ON "research_protocols" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_research_plot_id_tenant" ON "research_plots" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_treatment_id_tenant" ON "treatments" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_research_daily_log_id_tenant" ON "research_daily_logs" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_lab_sample_id_tenant" ON "lab_samples" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_digital_signature_id_tenant" ON "digital_signatures" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_experiment_collaborator_id_tenant" ON "experiment_collaborators" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_experiment_audit_log_id_tenant" ON "experiment_audit_log" ("id", "tenant_id");
