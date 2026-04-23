-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) for IDOR defense-in-depth
-- إضافة قيد فريد مركّب (id, tenant_id) لتعزيز عزل المستأجرين
--
-- Purpose: Expose Prisma `id_tenantId` compound-key accessor so update / delete
-- call sites in events.service.ts and alert.service.ts can bind both id and
-- tenantId atomically, closing TOCTOU windows between pre-check and mutation.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive constraint on already-unique id column — no row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_disaster_report_id_tenant" ON "disaster_reports" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_disaster_alert_id_tenant" ON "disaster_alerts" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_field_assessment_id_tenant" ON "field_assessments" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_alert_subscription_id_tenant" ON "alert_subscriptions" ("id", "tenant_id");
