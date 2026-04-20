-- Migration: add_tenant_to_role (no-op)
-- All operations in this migration are already handled by 20260225000000_init.
-- The user_roles table is created with tenant_id, uq_role_tenant_name unique index,
-- and idx_role_tenant index at init time, making every statement here a no-op.
-- This file must remain so Prisma does not detect schema drift.
SELECT 1; -- no-op sentinel
