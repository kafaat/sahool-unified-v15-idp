-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add tenant_id to chat-service models
-- إضافة معرف المستأجر لجداول خدمة المحادثات
-- Purpose: Multi-tenant isolation (drift fix)
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Add tenant_id columns with safe DEFAULT for existing rows

-- drift:safe reason=CREATE INDEX inside a Prisma-managed transaction cannot use CONCURRENTLY; zero-downtime index creation must be run manually outside Prisma migrate on large production tables.
ALTER TABLE "conversations" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "messages" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "participants" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';

-- Step 2: Remove DEFAULT constraint

ALTER TABLE "conversations" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "messages" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "participants" ALTER COLUMN "tenant_id" DROP DEFAULT;

-- Step 3: Create tenant isolation indexes

CREATE INDEX IF NOT EXISTS "idx_conversation_tenant" ON "conversations" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_conversation_tenant_active" ON "conversations" ("tenant_id", "is_active");
CREATE INDEX IF NOT EXISTS "idx_message_tenant" ON "messages" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_participant_tenant" ON "participants" ("tenant_id");
