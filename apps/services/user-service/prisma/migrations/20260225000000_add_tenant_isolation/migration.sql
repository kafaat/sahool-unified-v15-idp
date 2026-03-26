-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Add tenant_id to user-service models missing tenant isolation
-- إضافة معرف المستأجر لجداول خدمة المستخدمين
-- Purpose: Multi-tenant isolation (drift fix)
-- Note: User model already has tenant_id. Adding to related models.
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Add tenant_id columns with safe DEFAULT for existing rows

ALTER TABLE "user_profiles" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "user_sessions" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';
ALTER TABLE "refresh_tokens" ADD COLUMN IF NOT EXISTS "tenant_id" VARCHAR NOT NULL DEFAULT 'default';

-- Step 2: Backfill tenant_id from parent User table
-- الخطوة 2: ملء tenant_id من جدول المستخدم الأصلي

UPDATE "user_profiles" p SET "tenant_id" = u."tenant_id"
FROM "users" u WHERE p."user_id" = u."id" AND p."tenant_id" = 'default';

UPDATE "user_sessions" s SET "tenant_id" = u."tenant_id"
FROM "users" u WHERE s."user_id" = u."id" AND s."tenant_id" = 'default';

UPDATE "refresh_tokens" r SET "tenant_id" = u."tenant_id"
FROM "users" u WHERE r."user_id" = u."id" AND r."tenant_id" = 'default';

-- Step 3: Remove DEFAULT constraint

ALTER TABLE "user_profiles" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "user_sessions" ALTER COLUMN "tenant_id" DROP DEFAULT;
ALTER TABLE "refresh_tokens" ALTER COLUMN "tenant_id" DROP DEFAULT;

-- Step 4: Create tenant isolation indexes

CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_profile_tenant" ON "user_profiles" ("tenant_id");
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_session_tenant" ON "user_sessions" ("tenant_id");
CREATE INDEX CONCURRENTLY IF NOT EXISTS "idx_refresh_token_tenant" ON "refresh_tokens" ("tenant_id");
