-- drift:safe reason=CREATE TABLE statements on tables that do not yet exist in any environment; no existing rows means no lock contention, so CONCURRENTLY is not required (and not possible inside a Prisma-managed DDL transaction).
-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Materialise the 4 dormant tables referenced by application_tracker
-- إضافة جداول batch_lots / stock_movements / input_applications / application_plans
--
-- Context: apps/services/inventory-service/src/application_tracker.py creates
-- and reads four Prisma models (batchlot, stockmovement, inputapplication,
-- applicationplan) that had NO corresponding `model` blocks in schema.prisma
-- until now. That made the Python class unusable at runtime. This migration
-- lands the tables with full multi-tenant isolation (tenant_id column +
-- @@unique([id, tenant_id]) composite unique) so the id_tenantId accessor
-- is available from the generated Prisma client.
-- ═══════════════════════════════════════════════════════════════════════════════

-- ── 1. batch_lots ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "batch_lots" (
    "id"               UUID         NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"        VARCHAR(100) NOT NULL,
    "item_id"          UUID         NOT NULL,
    "batch_number"     VARCHAR(100),
    "received_date"    TIMESTAMPTZ  NOT NULL,
    "expiry_date"      TIMESTAMPTZ,
    "initial_qty"      DOUBLE PRECISION NOT NULL,
    "remaining_qty"    DOUBLE PRECISION NOT NULL,
    "unit_cost"        DOUBLE PRECISION,
    "supplier"         VARCHAR(255),
    "supplier_batch"   VARCHAR(100),
    "notes"            TEXT,
    "created_at"       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    "updated_at"       TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT "batch_lots_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "batch_lots_item_id_fkey" FOREIGN KEY ("item_id")
        REFERENCES "inventory_items"("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS "uq_batch_lot_id_tenant" ON "batch_lots" ("id", "tenant_id");
CREATE INDEX IF NOT EXISTS "batch_lots_tenant_id_idx"       ON "batch_lots" ("tenant_id");
CREATE INDEX IF NOT EXISTS "batch_lots_item_id_idx"         ON "batch_lots" ("item_id");
CREATE INDEX IF NOT EXISTS "idx_batch_item_received"        ON "batch_lots" ("item_id", "received_date");
CREATE INDEX IF NOT EXISTS "idx_batch_expiry"               ON "batch_lots" ("expiry_date");

-- ── 2. stock_movements ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "stock_movements" (
    "id"             UUID         NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"      VARCHAR(100) NOT NULL,
    "item_id"        UUID         NOT NULL,
    "movement_type"  VARCHAR(50)  NOT NULL,
    "quantity"       DOUBLE PRECISION NOT NULL,
    "previous_qty"   DOUBLE PRECISION NOT NULL,
    "new_qty"        DOUBLE PRECISION NOT NULL,
    "unit_cost"      DOUBLE PRECISION,
    "total_cost"     DOUBLE PRECISION,
    "reference_type" VARCHAR(50),
    "reference_id"   VARCHAR(255),
    "field_id"       VARCHAR(255),
    "crop_season_id" VARCHAR(255),
    "performed_by"   VARCHAR(255) NOT NULL,
    "notes"          TEXT,
    "notes_ar"       TEXT,
    "created_at"     TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT "stock_movements_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "stock_movements_item_id_fkey" FOREIGN KEY ("item_id")
        REFERENCES "inventory_items"("id") ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS "uq_stock_movement_id_tenant" ON "stock_movements" ("id", "tenant_id");
CREATE INDEX IF NOT EXISTS "stock_movements_tenant_id_idx"      ON "stock_movements" ("tenant_id");
CREATE INDEX IF NOT EXISTS "stock_movements_item_id_idx"        ON "stock_movements" ("item_id");
CREATE INDEX IF NOT EXISTS "idx_stock_movement_item_date"       ON "stock_movements" ("item_id", "created_at");
CREATE INDEX IF NOT EXISTS "stock_movements_field_id_idx"       ON "stock_movements" ("field_id");
CREATE INDEX IF NOT EXISTS "stock_movements_crop_season_id_idx" ON "stock_movements" ("crop_season_id");
CREATE INDEX IF NOT EXISTS "stock_movements_movement_type_idx"  ON "stock_movements" ("movement_type");
CREATE INDEX IF NOT EXISTS "stock_movements_created_at_idx"     ON "stock_movements" ("created_at");

-- ── 3. input_applications ─────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "input_applications" (
    "id"                 UUID         NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"          VARCHAR(100) NOT NULL,
    "field_id"           VARCHAR(255) NOT NULL,
    "crop_season_id"     VARCHAR(255) NOT NULL,
    "item_id"            UUID         NOT NULL,
    "batch_lot_id"       UUID,
    "application_date"   TIMESTAMPTZ  NOT NULL,
    "method"             VARCHAR(50)  NOT NULL,
    "purpose"            VARCHAR(50)  NOT NULL,
    "quantity_applied"   DOUBLE PRECISION NOT NULL,
    "unit"               VARCHAR(50)  NOT NULL,
    "area_covered_ha"    DOUBLE PRECISION NOT NULL,
    "rate_per_ha"        DOUBLE PRECISION NOT NULL,
    "applied_by"         VARCHAR(255) NOT NULL,
    "withholding_days"   INTEGER,
    "safe_harvest_date"  DATE,
    "unit_cost"          DOUBLE PRECISION,
    "total_cost"         DOUBLE PRECISION,
    "temperature"        DOUBLE PRECISION,
    "humidity"           DOUBLE PRECISION,
    "wind_speed"         DOUBLE PRECISION,
    "growth_stage"       VARCHAR(100),
    "equipment_used"     VARCHAR(255),
    "ppe_used"           TEXT[]       NOT NULL DEFAULT ARRAY[]::TEXT[],
    "target_pest"        VARCHAR(255),
    "efficacy_rating"    INTEGER,
    "notes"              TEXT,
    "created_at"         TIMESTAMPTZ  NOT NULL DEFAULT now(),
    "updated_at"         TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT "input_applications_pkey" PRIMARY KEY ("id"),
    CONSTRAINT "input_applications_item_id_fkey" FOREIGN KEY ("item_id")
        REFERENCES "inventory_items"("id") ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT "input_applications_batch_lot_id_fkey" FOREIGN KEY ("batch_lot_id")
        REFERENCES "batch_lots"("id") ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE UNIQUE INDEX IF NOT EXISTS "uq_input_application_id_tenant" ON "input_applications" ("id", "tenant_id");
CREATE INDEX IF NOT EXISTS "input_applications_tenant_id_idx"      ON "input_applications" ("tenant_id");
CREATE INDEX IF NOT EXISTS "input_applications_field_id_idx"       ON "input_applications" ("field_id");
CREATE INDEX IF NOT EXISTS "input_applications_crop_season_id_idx" ON "input_applications" ("crop_season_id");
CREATE INDEX IF NOT EXISTS "input_applications_item_id_idx"        ON "input_applications" ("item_id");
CREATE INDEX IF NOT EXISTS "input_applications_batch_lot_id_idx"   ON "input_applications" ("batch_lot_id");
CREATE INDEX IF NOT EXISTS "input_applications_application_date_idx" ON "input_applications" ("application_date");
CREATE INDEX IF NOT EXISTS "idx_input_app_field_date"              ON "input_applications" ("field_id", "application_date" DESC);
CREATE INDEX IF NOT EXISTS "idx_input_app_season_date"             ON "input_applications" ("crop_season_id", "application_date" DESC);
CREATE INDEX IF NOT EXISTS "input_applications_safe_harvest_date_idx" ON "input_applications" ("safe_harvest_date");

-- ── 4. application_plans ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS "application_plans" (
    "id"                    UUID         NOT NULL DEFAULT gen_random_uuid(),
    "tenant_id"             VARCHAR(100) NOT NULL,
    "field_id"              VARCHAR(255) NOT NULL,
    "crop_season_id"        VARCHAR(255) NOT NULL,
    "crop_type"             VARCHAR(100) NOT NULL,
    "planned_applications"  JSONB        NOT NULL,
    "total_fertilizer_kg"   DOUBLE PRECISION NOT NULL DEFAULT 0,
    "total_pesticide_l"     DOUBLE PRECISION NOT NULL DEFAULT 0,
    "estimated_cost"        DOUBLE PRECISION NOT NULL DEFAULT 0,
    "status"                VARCHAR(20)  NOT NULL DEFAULT 'DRAFT',
    "approved_by"           VARCHAR(255),
    "approved_at"           TIMESTAMPTZ,
    "created_at"            TIMESTAMPTZ  NOT NULL DEFAULT now(),
    "updated_at"            TIMESTAMPTZ  NOT NULL DEFAULT now(),

    CONSTRAINT "application_plans_pkey" PRIMARY KEY ("id")
);

CREATE UNIQUE INDEX IF NOT EXISTS "uq_application_plan_id_tenant" ON "application_plans" ("id", "tenant_id");
CREATE INDEX IF NOT EXISTS "application_plans_tenant_id_idx"      ON "application_plans" ("tenant_id");
CREATE INDEX IF NOT EXISTS "application_plans_field_id_idx"       ON "application_plans" ("field_id");
CREATE INDEX IF NOT EXISTS "application_plans_crop_season_id_idx" ON "application_plans" ("crop_season_id");
CREATE INDEX IF NOT EXISTS "application_plans_status_idx"         ON "application_plans" ("status");
