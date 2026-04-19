-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add generic scope + archive fields to Conversation
-- إضافة نطاق عام + حقل الأرشفة لجدول المحادثات
--
-- Ported from the archived field-chat service so chat-service can serve the
-- 5 previously-missing thread endpoints (by-scope lookup, archive, add/remove
-- participant, message search). All additions are nullable / default-valued,
-- so existing marketplace rows (product/order conversations) stay valid
-- without a backfill.
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Add nullable scope + archive columns.

ALTER TABLE "conversations" ADD COLUMN IF NOT EXISTS "scope_type"  VARCHAR;
ALTER TABLE "conversations" ADD COLUMN IF NOT EXISTS "scope_id"    VARCHAR;
ALTER TABLE "conversations" ADD COLUMN IF NOT EXISTS "archived_at" TIMESTAMP(3);

-- Step 2: Indexes — one tenant-scoped lookup and one for the scope uniqueness.

CREATE INDEX IF NOT EXISTS "idx_conversation_tenant_scope"
    ON "conversations" ("tenant_id", "scope_type");

-- Partial unique index: enforce one conversation per (tenant, scope_type, scope_id)
-- ONLY when both scope fields are set. Nulls are ignored, which keeps the
-- marketplace flows (productId/orderId-only conversations) from colliding.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_conversation_scope"
    ON "conversations" ("tenant_id", "scope_type", "scope_id")
    WHERE "scope_type" IS NOT NULL AND "scope_id" IS NOT NULL;
