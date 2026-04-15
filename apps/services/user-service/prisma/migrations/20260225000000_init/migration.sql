-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Initial schema for user-service
-- الترحيل: المخطط الأساسي لخدمة المستخدمين
-- Creates all tables, enums, indexes, and constraints from scratch
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Create enums
CREATE TYPE "UserRole" AS ENUM ('SUPER_ADMIN', 'ADMIN', 'MANAGER', 'AGRONOMIST', 'FARMER', 'WORKER', 'RESEARCHER', 'VIEWER');
CREATE TYPE "UserStatus" AS ENUM ('ACTIVE', 'INACTIVE', 'SUSPENDED', 'PENDING');

-- Step 2: Create users table
CREATE TABLE "users" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "phone" TEXT,
    "password_hash" TEXT NOT NULL,
    "first_name" TEXT NOT NULL,
    "last_name" TEXT NOT NULL,
    "name_ar" TEXT,
    "first_name_ar" TEXT,
    "last_name_ar" TEXT,
    "role" "UserRole" NOT NULL DEFAULT 'VIEWER',
    "status" "UserStatus" NOT NULL DEFAULT 'PENDING',
    "email_verified" BOOLEAN NOT NULL DEFAULT false,
    "phone_verified" BOOLEAN NOT NULL DEFAULT false,
    "last_login_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "failed_login_attempts" INTEGER NOT NULL DEFAULT 0,
    "lockout_until" TIMESTAMP(3),
    "last_failed_login_at" TIMESTAMP(3),
    "password_reset_token" TEXT,
    "password_reset_expiry" TIMESTAMP(3),

    CONSTRAINT "users_pkey" PRIMARY KEY ("id")
);

-- Step 3: Create user_profiles table
CREATE TABLE "user_profiles" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "national_id" TEXT,
    "date_of_birth" TIMESTAMP(3),
    "address" TEXT,
    "city" TEXT,
    "region" TEXT,
    "country" TEXT DEFAULT 'SA',
    "avatar_url" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "user_profiles_pkey" PRIMARY KEY ("id")
);

-- Step 4: Create user_roles table (custom roles/permissions)
CREATE TABLE "user_roles" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "permissions" JSONB NOT NULL,
    "is_system" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "user_roles_pkey" PRIMARY KEY ("id")
);

-- Step 5: Create user_sessions table
CREATE TABLE "user_sessions" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "ip_address" TEXT,
    "user_agent" TEXT,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "user_sessions_pkey" PRIMARY KEY ("id")
);

-- Step 6: Create refresh_tokens table
CREATE TABLE "refresh_tokens" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "jti" TEXT NOT NULL,
    "family" TEXT NOT NULL,
    "token" TEXT NOT NULL,
    "expires_at" TIMESTAMP(3) NOT NULL,
    "revoked" BOOLEAN NOT NULL DEFAULT false,
    "used" BOOLEAN NOT NULL DEFAULT false,
    "used_at" TIMESTAMP(3),
    "replaced_by" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "refresh_tokens_pkey" PRIMARY KEY ("id")
);

-- Step 7: Create many-to-many join table for User <-> Role
CREATE TABLE "_UserAssignedRoles" (
    "A" TEXT NOT NULL,
    "B" TEXT NOT NULL,

    CONSTRAINT "_UserAssignedRoles_AB_pkey" PRIMARY KEY ("A", "B")
);

-- Step 8: Create unique constraints
CREATE UNIQUE INDEX "users_email_key" ON "users"("email");
CREATE UNIQUE INDEX "user_profiles_user_id_key" ON "user_profiles"("user_id");
CREATE UNIQUE INDEX "user_sessions_token_key" ON "user_sessions"("token");
CREATE UNIQUE INDEX "refresh_tokens_jti_key" ON "refresh_tokens"("jti");
CREATE UNIQUE INDEX "refresh_tokens_token_key" ON "refresh_tokens"("token");
CREATE UNIQUE INDEX "uq_role_tenant_name" ON "user_roles"("tenant_id", "name");

-- Step 9: Create indexes for users table
CREATE INDEX "users_tenant_id_idx" ON "users"("tenant_id");
CREATE INDEX "users_email_idx" ON "users"("email");
CREATE INDEX "users_status_idx" ON "users"("status");
CREATE INDEX "users_role_idx" ON "users"("role");
CREATE INDEX "idx_user_last_login" ON "users"("last_login_at");
CREATE INDEX "idx_user_tenant_status" ON "users"("tenant_id", "status");
CREATE INDEX "idx_user_tenant_email" ON "users"("tenant_id", "email");
CREATE INDEX "idx_user_tenant_role" ON "users"("tenant_id", "role");
CREATE INDEX "idx_user_lockout_until" ON "users"("lockout_until");

-- Step 10: Create indexes for user_profiles table
CREATE INDEX "idx_profile_tenant" ON "user_profiles"("tenant_id");
CREATE INDEX "user_profiles_user_id_idx" ON "user_profiles"("user_id");
CREATE INDEX "user_profiles_national_id_idx" ON "user_profiles"("national_id");

-- Step 11: Create indexes for user_roles table
CREATE INDEX "idx_role_tenant" ON "user_roles"("tenant_id");

-- Step 12: Create indexes for user_sessions table
CREATE INDEX "idx_session_tenant" ON "user_sessions"("tenant_id");
CREATE INDEX "user_sessions_user_id_idx" ON "user_sessions"("user_id");
CREATE INDEX "user_sessions_token_idx" ON "user_sessions"("token");
CREATE INDEX "user_sessions_expires_at_idx" ON "user_sessions"("expires_at");
CREATE INDEX "idx_session_user_expiry" ON "user_sessions"("user_id", "expires_at");

-- Step 13: Create indexes for refresh_tokens table
CREATE INDEX "idx_refresh_token_tenant" ON "refresh_tokens"("tenant_id");
CREATE INDEX "refresh_tokens_user_id_idx" ON "refresh_tokens"("user_id");
CREATE INDEX "refresh_tokens_jti_idx" ON "refresh_tokens"("jti");
CREATE INDEX "refresh_tokens_family_idx" ON "refresh_tokens"("family");
CREATE INDEX "refresh_tokens_token_idx" ON "refresh_tokens"("token");
CREATE INDEX "refresh_tokens_expires_at_idx" ON "refresh_tokens"("expires_at");
CREATE INDEX "idx_refresh_token_cleanup" ON "refresh_tokens"("user_id", "revoked", "expires_at");
CREATE INDEX "idx_refresh_token_revoked_expiry" ON "refresh_tokens"("revoked", "expires_at");

-- Step 14: Create index for join table
CREATE INDEX "_UserAssignedRoles_B_index" ON "_UserAssignedRoles"("B");

-- Step 15: Add foreign key constraints
ALTER TABLE "user_profiles" ADD CONSTRAINT "user_profiles_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "user_sessions" ADD CONSTRAINT "user_sessions_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "refresh_tokens" ADD CONSTRAINT "refresh_tokens_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "_UserAssignedRoles" ADD CONSTRAINT "_UserAssignedRoles_A_fkey" FOREIGN KEY ("A") REFERENCES "users"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "_UserAssignedRoles" ADD CONSTRAINT "_UserAssignedRoles_B_fkey" FOREIGN KEY ("B") REFERENCES "user_roles"("id") ON DELETE CASCADE ON UPDATE CASCADE;
