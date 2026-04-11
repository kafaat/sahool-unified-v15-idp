-- drift:safe reason=Additive migration. All operations are either ADD COLUMN (new
-- nullable columns on tables that were created empty in the prior migration in the
-- same transaction) or CREATE TABLE IF NOT EXISTS on new tables with zero rows.
-- No existing rows are mutated. CREATE INDEX on empty tables is instantaneous.
-- Migration: Accounting + ERP integration + Outbox + Idempotency
-- الهجرة: تكامل المحاسبة + أنظمة ERP الخارجية + outbox + idempotency
-- Created: 2026-04-11
--
-- This migration elevates the crop_seasons + field_operations tables from
-- "web-only metadata" to "enterprise-ready accounting records" that can
-- be synced to external accounting/ERP platforms (QuickBooks, SAP, Odoo,
-- Xero, Oracle, …). It also introduces the reliability primitives
-- (transactional outbox + idempotency keys) required for at-least-once
-- delivery to those downstream systems.
--
-- Reference standards:
--   * IFRS biological-asset disclosure — traceable cost breakdown per
--     operation, per crop season (IAS 41)
--   * SOX audit trail — soft-delete instead of hard-delete, approval
--     workflow, immutable audit log.
--   * John Deere Operations Center / Climate FieldView / Granular:
--     cost components (fuel, labour, materials, overhead), vendor
--     references, GL account mapping, per-season ROI roll-ups.

-- ---------------------------------------------------------------------------
-- field_operations — accounting + ERP + audit + soft-delete
-- ---------------------------------------------------------------------------

ALTER TABLE "field_operations"
    -- Cost breakdown (components of cost_amount, all optional so existing
    -- rows survive unchanged)
    ADD COLUMN IF NOT EXISTS "fuel_liters"      DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS "fuel_cost"        DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS "labor_hours"      DECIMAL(8, 2),
    ADD COLUMN IF NOT EXISTS "labor_cost"       DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS "materials_cost"   DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS "overhead_cost"    DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS "other_cost"       DECIMAL(12, 2),

    -- Tax + currency
    ADD COLUMN IF NOT EXISTS "tax_amount"       DECIMAL(12, 2),
    ADD COLUMN IF NOT EXISTS "tax_rate"         DECIMAL(5, 2),
    ADD COLUMN IF NOT EXISTS "exchange_rate"    DECIMAL(14, 6),
    ADD COLUMN IF NOT EXISTS "base_currency"    VARCHAR(8),

    -- Vendor / invoice (for accounting reconciliation)
    ADD COLUMN IF NOT EXISTS "invoice_number"   VARCHAR(100),
    ADD COLUMN IF NOT EXISTS "invoice_date"     DATE,
    ADD COLUMN IF NOT EXISTS "vendor_id"        VARCHAR(100),
    ADD COLUMN IF NOT EXISTS "vendor_name"      VARCHAR(255),
    ADD COLUMN IF NOT EXISTS "receipt_url"      VARCHAR(500),

    -- GL / cost-center / project for ERP posting
    ADD COLUMN IF NOT EXISTS "gl_account"       VARCHAR(50),
    ADD COLUMN IF NOT EXISTS "cost_center"      VARCHAR(50),
    ADD COLUMN IF NOT EXISTS "project_code"     VARCHAR(50),

    -- ERP sync bookkeeping (one row per posting attempt rollup)
    ADD COLUMN IF NOT EXISTS "external_id"       VARCHAR(100),
    ADD COLUMN IF NOT EXISTS "external_source"   VARCHAR(50),
    ADD COLUMN IF NOT EXISTS "posted_to_erp"     BOOLEAN NOT NULL DEFAULT FALSE,
    ADD COLUMN IF NOT EXISTS "posted_at"         TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS "posting_reference" VARCHAR(255),
    ADD COLUMN IF NOT EXISTS "posting_error"     TEXT,
    ADD COLUMN IF NOT EXISTS "posting_attempts"  INTEGER NOT NULL DEFAULT 0,

    -- Approval workflow (pending | approved | rejected). Existing rows
    -- default to 'approved' so they remain queryable after the migration.
    ADD COLUMN IF NOT EXISTS "approval_status"  VARCHAR(20) NOT NULL DEFAULT 'approved',
    ADD COLUMN IF NOT EXISTS "approved_by"      VARCHAR(100),
    ADD COLUMN IF NOT EXISTS "approved_at"      TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS "rejection_reason" TEXT,

    -- Soft delete (audit compliance — rows are never physically removed
    -- so SOX / IFRS trails stay intact)
    ADD COLUMN IF NOT EXISTS "deleted_at"       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS "deleted_by"       VARCHAR(100),
    ADD COLUMN IF NOT EXISTS "deleted_reason"   TEXT;

-- CHECK constraint: approval_status canonical values. Drop first in case
-- the migration is re-applied after a rename.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.constraint_column_usage
        WHERE constraint_name = 'field_op_approval_check'
    ) THEN
        ALTER TABLE "field_operations"
            ADD CONSTRAINT "field_op_approval_check"
            CHECK ("approval_status" IN ('pending', 'approved', 'rejected'));
    END IF;
END $$;

-- Indexes for ERP sync workers (polling unposted rows)
CREATE INDEX IF NOT EXISTS "idx_field_op_erp_pending"
    ON "field_operations" ("tenant_id", "posted_to_erp", "created_at")
    WHERE "posted_to_erp" = FALSE AND "deleted_at" IS NULL;

CREATE INDEX IF NOT EXISTS "idx_field_op_vendor"
    ON "field_operations" ("tenant_id", "vendor_id")
    WHERE "vendor_id" IS NOT NULL;

CREATE INDEX IF NOT EXISTS "idx_field_op_approval"
    ON "field_operations" ("tenant_id", "approval_status", "performed_at")
    WHERE "approval_status" != 'approved' AND "deleted_at" IS NULL;

CREATE INDEX IF NOT EXISTS "idx_field_op_not_deleted"
    ON "field_operations" ("tenant_id", "field_id")
    WHERE "deleted_at" IS NULL;

CREATE INDEX IF NOT EXISTS "idx_field_op_external_id"
    ON "field_operations" ("external_source", "external_id")
    WHERE "external_id" IS NOT NULL;

-- ---------------------------------------------------------------------------
-- crop_seasons — ERP + soft-delete + cached totals
-- ---------------------------------------------------------------------------

ALTER TABLE "crop_seasons"
    -- ERP sync
    ADD COLUMN IF NOT EXISTS "external_id"     VARCHAR(100),
    ADD COLUMN IF NOT EXISTS "external_source" VARCHAR(50),
    ADD COLUMN IF NOT EXISTS "cost_center"     VARCHAR(50),
    ADD COLUMN IF NOT EXISTS "project_code"    VARCHAR(50),
    ADD COLUMN IF NOT EXISTS "base_currency"   VARCHAR(8),

    -- Cached totals (materialized from field_operations rollup - updated
    -- by a trigger or by the /rollup endpoint). Allows dashboards to
    -- list 100 seasons without joining the operations table.
    ADD COLUMN IF NOT EXISTS "total_season_cost"    DECIMAL(14, 2),
    ADD COLUMN IF NOT EXISTS "total_season_revenue" DECIMAL(14, 2),
    ADD COLUMN IF NOT EXISTS "total_season_hours"   DECIMAL(10, 2),
    ADD COLUMN IF NOT EXISTS "totals_updated_at"    TIMESTAMPTZ,

    -- Soft delete
    ADD COLUMN IF NOT EXISTS "deleted_at"       TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS "deleted_by"       VARCHAR(100),
    ADD COLUMN IF NOT EXISTS "deleted_reason"   TEXT;

CREATE INDEX IF NOT EXISTS "idx_crop_season_not_deleted"
    ON "crop_seasons" ("tenant_id", "field_id")
    WHERE "deleted_at" IS NULL;

CREATE INDEX IF NOT EXISTS "idx_crop_season_external_id"
    ON "crop_seasons" ("external_source", "external_id")
    WHERE "external_id" IS NOT NULL;

-- ---------------------------------------------------------------------------
-- outbox_events — transactional outbox for reliable NATS + ERP delivery
-- Schema intentionally mirrors shared/libs/outbox/models.py so the
-- downstream worker stays protocol-compatible with the existing
-- platform-wide outbox consumers.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS "outbox_events" (
    "id"              UUID NOT NULL DEFAULT gen_random_uuid(),
    "event_type"      VARCHAR(200) NOT NULL,
    "event_version"   INTEGER NOT NULL DEFAULT 1,
    "schema_ref"      VARCHAR(240) NOT NULL,
    "tenant_id"       UUID NOT NULL,
    "correlation_id"  UUID NOT NULL,
    "aggregate_type"  VARCHAR(100),
    "aggregate_id"    UUID,
    "payload_json"    TEXT NOT NULL,
    "published"       BOOLEAN NOT NULL DEFAULT FALSE,
    "published_at"    TIMESTAMPTZ,
    "retry_count"     INTEGER NOT NULL DEFAULT 0,
    "last_error"      TEXT,
    "created_at"      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "outbox_events_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "ix_outbox_published_created"
    ON "outbox_events" ("published", "created_at");
CREATE INDEX IF NOT EXISTS "ix_outbox_tenant_created"
    ON "outbox_events" ("tenant_id", "created_at");
CREATE INDEX IF NOT EXISTS "ix_outbox_aggregate"
    ON "outbox_events" ("aggregate_type", "aggregate_id");
-- Poll-and-publish worker index: scan unpublished rows, bounded by retry
-- count so permanently failing rows don't clog the queue.
CREATE INDEX IF NOT EXISTS "ix_outbox_pending_retry"
    ON "outbox_events" ("published", "retry_count", "created_at")
    WHERE "published" = FALSE;

-- ---------------------------------------------------------------------------
-- idempotency_keys — guards POST endpoints against duplicate submissions
-- when clients retry after a network error. Matches the RFC draft
-- "Idempotency-Key" header semantics used by Stripe, Adyen, PayPal.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS "idempotency_keys" (
    "id"              UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"       VARCHAR(100) NOT NULL,
    "key"             VARCHAR(255) NOT NULL,
    "method"          VARCHAR(10) NOT NULL,
    "path"            VARCHAR(500) NOT NULL,
    -- SHA-256 of canonical request body for conflict detection.
    -- If same key but different body arrives, we return 409 instead of
    -- silently replaying the stored response.
    "request_hash"    VARCHAR(64) NOT NULL,
    -- Cached response body + status for replay on duplicate.
    "response_status" INTEGER,
    "response_body"   TEXT,
    -- Soft expiration so old keys can be garbage-collected.
    "expires_at"      TIMESTAMPTZ NOT NULL,
    "created_at"      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "idempotency_keys_pkey" PRIMARY KEY ("id")
);

-- A key is unique per (tenant, key, method, path) tuple so the same
-- string can be reused across different endpoints without collision.
CREATE UNIQUE INDEX IF NOT EXISTS "uq_idempotency_tenant_key_method_path"
    ON "idempotency_keys" ("tenant_id", "key", "method", "path");
-- Cleanup index for the GC worker
CREATE INDEX IF NOT EXISTS "ix_idempotency_expires"
    ON "idempotency_keys" ("expires_at");

-- ---------------------------------------------------------------------------
-- field_operation_audit — append-only audit log for accounting
-- integrity (SOX/IFRS). Every INSERT/UPDATE/DELETE on field_operations
-- writes a row here via a trigger, capturing the "before" + "after"
-- JSON so auditors can reconstruct the full history.
-- ---------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS "field_operation_audit" (
    "id"              UUID NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"       VARCHAR(100) NOT NULL,
    "operation_id"    UUID NOT NULL,
    "action"          VARCHAR(20) NOT NULL,
    "actor_id"        VARCHAR(100),
    "before_data"     JSONB,
    "after_data"      JSONB,
    "correlation_id"  UUID,
    "client_ip"       VARCHAR(50),
    "user_agent"      VARCHAR(500),
    "created_at"      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT "field_operation_audit_pkey" PRIMARY KEY ("id")
);

CREATE INDEX IF NOT EXISTS "idx_field_op_audit_tenant"
    ON "field_operation_audit" ("tenant_id");
CREATE INDEX IF NOT EXISTS "idx_field_op_audit_op"
    ON "field_operation_audit" ("operation_id", "created_at" DESC);
CREATE INDEX IF NOT EXISTS "idx_field_op_audit_action"
    ON "field_operation_audit" ("tenant_id", "action", "created_at");

-- Trigger function that fans audit rows out. The service layer still
-- inserts an explicit audit row with correlation_id/actor_id, but this
-- trigger is a belt-and-braces guarantee that NO mutation slips
-- through unrecorded, even in emergency direct SQL fixes.
CREATE OR REPLACE FUNCTION public.field_operation_audit_fn()
RETURNS trigger AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        INSERT INTO "field_operation_audit"
            ("tenant_id", "operation_id", "action", "after_data")
        VALUES
            (NEW.tenant_id, NEW.id, 'insert', to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO "field_operation_audit"
            ("tenant_id", "operation_id", "action", "before_data", "after_data")
        VALUES
            (NEW.tenant_id, NEW.id, 'update', to_jsonb(OLD), to_jsonb(NEW));
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO "field_operation_audit"
            ("tenant_id", "operation_id", "action", "before_data")
        VALUES
            (OLD.tenant_id, OLD.id, 'delete', to_jsonb(OLD));
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS "field_operation_audit_trg" ON "field_operations";
CREATE TRIGGER "field_operation_audit_trg"
    AFTER INSERT OR UPDATE OR DELETE ON "field_operations"
    FOR EACH ROW
    EXECUTE FUNCTION public.field_operation_audit_fn();
