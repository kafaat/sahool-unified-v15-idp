-- ═══════════════════════════════════════════════════════════════════════════
-- SAHOOL Audit Service — Retention role
-- Migration: 002_audit_retention_role
-- Created:   2026-04-17
-- Purpose:   Create a dedicated role that is allowed to bypass the
--            append-only triggers on audit_log so retention jobs can
--            delete (or archive-then-delete) expired rows without the
--            service role itself gaining mutation rights.
-- ═══════════════════════════════════════════════════════════════════════════
--
-- How this works:
--   * Migration 001 installed trg_audit_log_no_update / no_delete triggers
--     that raise unless the session variable `sahool.audit_retention_job`
--     equals 'on'.
--   * The retention worker connects as role `audit_retention`, sets that
--     variable inside its transaction, and issues DELETE statements.
--   * The service role (e.g. `sahool_audit`) does NOT get the
--     SET sahool.audit_retention_job privilege at the GRANT level, so
--     it can neither accidentally delete rows nor be exploited to do so.
--
-- Operator workflow:
--   BEGIN;
--     SET LOCAL ROLE audit_retention;
--     SET LOCAL sahool.audit_retention_job = 'on';
--     DELETE FROM audit_log WHERE created_at < NOW() - INTERVAL '5 years';
--   COMMIT;
-- ═══════════════════════════════════════════════════════════════════════════

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'audit_retention') THEN
        CREATE ROLE audit_retention NOLOGIN;
    END IF;
END
$$;

-- Narrow privilege: retention role can read + delete; never INSERT/UPDATE.
GRANT SELECT, DELETE ON audit_log TO audit_retention;

-- Retention role is also exempt from RLS (it enforces platform-wide
-- retention, not per-tenant); without this it would only see zero rows.
ALTER ROLE audit_retention BYPASSRLS;

-- The chain-validation sweep (see main.py _chain_validation_loop) needs a
-- cross-tenant read too. Same reasoning — grant BYPASSRLS to the service
-- role ONLY for audit-service's own pool, not to any other service's role.
-- (No CREATE ROLE for the service role here; the platform provisions it
--  under a conventional name, e.g. `sahool_audit`. We document the
--  requirement rather than creating it to stay DB-provisioner-agnostic.)
COMMENT ON ROLE audit_retention IS
    'SAHOOL audit retention worker. Set LOCAL sahool.audit_retention_job=on '
    'to bypass audit_log append-only triggers. Grants: SELECT, DELETE, '
    'BYPASSRLS. Never grant INSERT/UPDATE.';

INSERT INTO audit_service_schema_migrations (version)
    VALUES ('002_audit_retention_role')
    ON CONFLICT DO NOTHING;
