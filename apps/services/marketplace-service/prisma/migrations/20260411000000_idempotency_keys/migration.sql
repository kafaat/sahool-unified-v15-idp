-- drift:safe reason=additive-idempotency-table
-- Migration: Idempotency keys cache table
-- Date: 2026-04-11
--
-- Adds `idempotency_keys` table that caches responses of money-moving
-- endpoints (deposit / withdraw / transfer / createOrder) keyed by the
-- `Idempotency-Key` HTTP header (RFC draft: "The Idempotency-Key HTTP
-- Header Field").
--
-- This migration is purely additive:
--   * CREATE TABLE IF NOT EXISTS  — safe on re-apply
--   * CREATE INDEX CONCURRENTLY IF NOT EXISTS  — no write lock
--
-- The corresponding Prisma model is `IdempotencyKey` in schema.prisma.
-- Runtime access is via parameterized raw SQL in
-- src/fintech/idempotency.service.ts so the service keeps compiling even
-- when `prisma generate` has not been refreshed yet.

CREATE TABLE IF NOT EXISTS idempotency_keys (
    key            TEXT        PRIMARY KEY,
    tenant_id      UUID        NOT NULL,
    user_id        UUID        NOT NULL,
    operation      TEXT        NOT NULL,
    request_hash   TEXT        NOT NULL,
    response_body  JSONB,
    status_code    INTEGER,
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Most common access path: list recent keys per tenant for the cleanup
-- job and for operator debugging.
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_idempotency_keys_tenant_created
    ON idempotency_keys (tenant_id, created_at DESC);

-- Secondary lookup: by operation (e.g. stats of deposits via this flow).
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_idempotency_keys_operation
    ON idempotency_keys (operation);
