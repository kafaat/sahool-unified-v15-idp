-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add composite UNIQUE(id, tenant_id) for IDOR defense-in-depth
-- إضافة قيد فريد مركّب (id, tenant_id) لتعزيز عزل المستأجرين
--
-- Purpose: Expose a Prisma `id_tenantId` compound-key accessor so call sites
-- can do `findUnique({ where: { id_tenantId: { id, tenantId } } })` and
-- `update({ where: { id_tenantId: ... } })` — closing IDOR (Insecure Direct
-- Object Reference) gaps where a cross-tenant actor could otherwise access
-- rows by guessing UUIDs.
--
-- Notes:
--   • `id` is already UNIQUE via the PK; adding `(id, tenant_id)` is a strictly
--     additive constraint (no existing row can violate it).
--   • No CONCURRENTLY: these tables are small enough and the indexes are
--     written inside Prisma's DDL transaction (drift:safe pattern).
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; strictly additive constraint on already-unique id column — no row can violate it.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_conversation_id_tenant" ON "conversations" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_message_id_tenant" ON "messages" ("id", "tenant_id");
CREATE UNIQUE INDEX IF NOT EXISTS "uq_participant_id_tenant" ON "participants" ("id", "tenant_id");
