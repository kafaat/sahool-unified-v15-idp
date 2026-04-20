-- Migration: add_tenant_isolation (no-op)
-- All operations in this migration are already handled by 20260225000000_init.
-- user_profiles, user_sessions, and refresh_tokens are created with tenant_id,
-- and idx_profile_tenant, idx_session_tenant, idx_refresh_token_tenant are all
-- created in the init migration. This file must remain to prevent Prisma drift.
SELECT 1; -- no-op sentinel
