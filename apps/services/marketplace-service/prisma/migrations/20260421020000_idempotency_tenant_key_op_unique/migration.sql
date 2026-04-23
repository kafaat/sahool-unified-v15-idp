-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Composite UNIQUE on (tenant_id, key, operation) for idempotency_keys
-- قيد فريد مركّب لمفاتيح منع التكرار لعزل المستأجرين
--
-- Background: `idempotency_keys.key` is a global PRIMARY KEY for historical
-- reasons. Combined with the pre-fix SELECT that matched only on `key` +
-- `operation` (no tenant filter), a client in tenant A picking the same
-- Idempotency-Key as tenant B would hit tenant A's cached response — a
-- cross-tenant data leak.
--
-- The accompanying commit fixes the SELECT to include tenant_id AND detects
-- the cross-tenant collision at INSERT time (re-SELECT strictly by tenant
-- after an ON CONFLICT DO NOTHING return of 0). This migration adds the
-- composite UNIQUE as defense-in-depth so any future raw-SQL caller that
-- reintroduces the bug still gets blocked at the DB layer.
-- ═══════════════════════════════════════════════════════════════════════════════

-- drift:safe reason=CREATE UNIQUE INDEX inside Prisma's DDL transaction cannot use CONCURRENTLY; additive constraint on a table where `key` is already globally unique (the PK), so existing rows trivially satisfy the tighter composite.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_idempotency_tenant_key_op"
    ON "idempotency_keys" ("tenant_id", "key", "operation");
