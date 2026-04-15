-- CreateEnum
CREATE TYPE "ItemCategory" AS ENUM ('SEEDS', 'FERTILIZER', 'PESTICIDE', 'HERBICIDE', 'FUNGICIDE', 'INSECTICIDE', 'EQUIPMENT', 'TOOLS', 'IRRIGATION', 'PACKAGING', 'FUEL', 'OTHER');

-- CreateEnum
CREATE TYPE "MovementType" AS ENUM ('PURCHASE', 'SALE', 'RETURN', 'ADJUSTMENT', 'TRANSFER', 'WASTE', 'USAGE', 'PRODUCTION', 'RESTOCK');

-- CreateEnum
CREATE TYPE "AlertType" AS ENUM ('LOW_STOCK', 'OUT_OF_STOCK', 'EXPIRING_SOON', 'EXPIRED', 'REORDER_POINT', 'OVERSTOCK', 'STORAGE_CONDITION');

-- CreateEnum
CREATE TYPE "AlertPriority" AS ENUM ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL');

-- CreateEnum
CREATE TYPE "AlertStatus" AS ENUM ('ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'SNOOZED');

-- CreateEnum
CREATE TYPE "WarehouseType" AS ENUM ('MAIN', 'FIELD', 'COLD', 'CHEMICAL', 'SEED', 'FUEL');

-- CreateEnum
CREATE TYPE "StorageCondition" AS ENUM ('AMBIENT', 'COOL', 'COLD', 'FROZEN', 'DRY', 'CONTROLLED');

-- CreateEnum
CREATE TYPE "TransferType" AS ENUM ('INTER_WAREHOUSE', 'RECEIVING', 'DISPATCH');

-- CreateEnum
CREATE TYPE "TransferStatus" AS ENUM ('PENDING', 'APPROVED', 'IN_TRANSIT', 'COMPLETED', 'CANCELLED');

-- CreateTable
CREATE TABLE "inventory_items" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "name_ar" TEXT NOT NULL,
    "sku" TEXT,
    "category" "ItemCategory" NOT NULL,
    "description" TEXT,
    "description_ar" TEXT,
    "quantity" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "unit" TEXT NOT NULL,
    "reorder_level" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "reorder_point" DOUBLE PRECISION,
    "max_stock" DOUBLE PRECISION,
    "unit_cost" DOUBLE PRECISION,
    "selling_price" DOUBLE PRECISION,
    "location" TEXT,
    "batch_number" TEXT,
    "expiry_date" TIMESTAMP(3),
    "min_temperature" DOUBLE PRECISION,
    "max_temperature" DOUBLE PRECISION,
    "min_humidity" DOUBLE PRECISION,
    "max_humidity" DOUBLE PRECISION,
    "supplier" TEXT,
    "barcode" TEXT,
    "image_url" TEXT,
    "notes" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "last_restocked" TIMESTAMP(3),

    CONSTRAINT "inventory_items_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "inventory_movements" (
    "id" TEXT NOT NULL,
    "item_id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "type" "MovementType" NOT NULL,
    "quantity" DOUBLE PRECISION NOT NULL,
    "unit_cost" DOUBLE PRECISION,
    "reference_id" TEXT,
    "reference_type" TEXT,
    "from_location" TEXT,
    "to_location" TEXT,
    "notes" TEXT,
    "notes_ar" TEXT,
    "performed_by" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "inventory_movements_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "inventory_alerts" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "alert_type" "AlertType" NOT NULL,
    "priority" "AlertPriority" NOT NULL,
    "status" "AlertStatus" NOT NULL DEFAULT 'ACTIVE',
    "item_id" TEXT NOT NULL,
    "item_name" TEXT NOT NULL,
    "item_name_ar" TEXT NOT NULL,
    "title_en" TEXT NOT NULL,
    "title_ar" TEXT NOT NULL,
    "message_en" TEXT NOT NULL,
    "message_ar" TEXT NOT NULL,
    "current_value" DOUBLE PRECISION NOT NULL,
    "threshold_value" DOUBLE PRECISION NOT NULL,
    "recommended_action_en" TEXT NOT NULL,
    "recommended_action_ar" TEXT NOT NULL,
    "action_url" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "acknowledged_at" TIMESTAMP(3),
    "acknowledged_by" TEXT,
    "resolved_at" TIMESTAMP(3),
    "resolved_by" TEXT,
    "resolution_notes" TEXT,
    "snooze_until" TIMESTAMP(3),

    CONSTRAINT "inventory_alerts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "alert_settings" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "expiry_warning_days" INTEGER NOT NULL DEFAULT 30,
    "expiry_critical_days" INTEGER NOT NULL DEFAULT 7,
    "default_reorder_level" DOUBLE PRECISION NOT NULL DEFAULT 10,
    "enable_email_alerts" BOOLEAN NOT NULL DEFAULT true,
    "enable_push_alerts" BOOLEAN NOT NULL DEFAULT true,
    "enable_sms_alerts" BOOLEAN NOT NULL DEFAULT false,
    "alert_check_interval" INTEGER NOT NULL DEFAULT 60,
    "max_alerts_per_day" INTEGER NOT NULL DEFAULT 100,
    "auto_resolve_on_restock" BOOLEAN NOT NULL DEFAULT true,
    "auto_resolve_expired" BOOLEAN NOT NULL DEFAULT false,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "alert_settings_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "warehouses" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "name_ar" TEXT NOT NULL,
    "warehouse_type" "WarehouseType" NOT NULL,
    "latitude" DOUBLE PRECISION,
    "longitude" DOUBLE PRECISION,
    "address" TEXT,
    "governorate" TEXT,
    "capacity_value" DOUBLE PRECISION NOT NULL,
    "capacity_unit" TEXT NOT NULL DEFAULT 'cubic_meter',
    "current_usage" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "storage_condition" "StorageCondition" NOT NULL DEFAULT 'AMBIENT',
    "temp_min" DOUBLE PRECISION,
    "temp_max" DOUBLE PRECISION,
    "humidity_min" DOUBLE PRECISION,
    "humidity_max" DOUBLE PRECISION,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "manager_id" TEXT,
    "manager_name" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "warehouses_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "zones" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "warehouse_id" TEXT NOT NULL,
    "name" TEXT NOT NULL,
    "name_ar" TEXT,
    "capacity" DOUBLE PRECISION NOT NULL,
    "current_usage" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "condition" "StorageCondition",
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "zones_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "storage_locations" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "zone_id" TEXT NOT NULL,
    "aisle" TEXT NOT NULL,
    "shelf" TEXT NOT NULL,
    "bin" TEXT NOT NULL,
    "location_code" TEXT NOT NULL,
    "capacity" DOUBLE PRECISION NOT NULL,
    "is_occupied" BOOLEAN NOT NULL DEFAULT false,
    "current_item_id" TEXT,
    "current_qty" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "storage_locations_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "stock_transfers" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "item_id" TEXT NOT NULL,
    "from_warehouse_id" TEXT,
    "to_warehouse_id" TEXT NOT NULL,
    "quantity" DOUBLE PRECISION NOT NULL,
    "unit_cost" DOUBLE PRECISION,
    "total_cost" DOUBLE PRECISION,
    "transfer_type" "TransferType" NOT NULL,
    "status" "TransferStatus" NOT NULL DEFAULT 'PENDING',
    "requested_by" TEXT NOT NULL,
    "approved_by" TEXT,
    "performed_by" TEXT,
    "requested_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "approved_at" TIMESTAMP(3),
    "completed_at" TIMESTAMP(3),
    "notes" TEXT,

    CONSTRAINT "stock_transfers_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE UNIQUE INDEX "inventory_items_sku_key" ON "inventory_items"("sku");

-- CreateIndex
CREATE INDEX "inventory_items_tenant_id_idx" ON "inventory_items"("tenant_id");

-- CreateIndex
CREATE INDEX "inventory_items_category_idx" ON "inventory_items"("category");

-- CreateIndex
CREATE INDEX "inventory_items_quantity_idx" ON "inventory_items"("quantity");

-- CreateIndex
CREATE INDEX "inventory_items_expiry_date_idx" ON "inventory_items"("expiry_date");

-- CreateIndex
CREATE INDEX "idx_inventory_tenant_cat_qty" ON "inventory_items"("tenant_id", "category", "quantity");

-- CreateIndex
CREATE INDEX "inventory_movements_item_id_idx" ON "inventory_movements"("item_id");

-- CreateIndex
CREATE INDEX "inventory_movements_tenant_id_idx" ON "inventory_movements"("tenant_id");

-- CreateIndex
CREATE INDEX "inventory_movements_type_idx" ON "inventory_movements"("type");

-- CreateIndex
CREATE INDEX "inventory_movements_created_at_idx" ON "inventory_movements"("created_at");

-- CreateIndex
CREATE INDEX "idx_movement_item_date" ON "inventory_movements"("item_id", "created_at");

-- CreateIndex
CREATE INDEX "idx_movement_tenant_type_date" ON "inventory_movements"("tenant_id", "type", "created_at");

-- CreateIndex
CREATE INDEX "inventory_alerts_tenant_id_idx" ON "inventory_alerts"("tenant_id");

-- CreateIndex
CREATE INDEX "inventory_alerts_status_priority_idx" ON "inventory_alerts"("status", "priority");

-- CreateIndex
CREATE INDEX "inventory_alerts_item_id_idx" ON "inventory_alerts"("item_id");

-- CreateIndex
CREATE INDEX "inventory_alerts_alert_type_idx" ON "inventory_alerts"("alert_type");

-- CreateIndex
CREATE INDEX "inventory_alerts_created_at_idx" ON "inventory_alerts"("created_at");

-- CreateIndex
CREATE UNIQUE INDEX "alert_settings_tenant_id_key" ON "alert_settings"("tenant_id");

-- CreateIndex
CREATE INDEX "warehouses_tenant_id_idx" ON "warehouses"("tenant_id");

-- CreateIndex
CREATE INDEX "idx_warehouse_active" ON "warehouses"("is_active");

-- CreateIndex
CREATE INDEX "idx_warehouse_type" ON "warehouses"("warehouse_type");

-- CreateIndex
CREATE INDEX "idx_warehouse_location" ON "warehouses"("latitude", "longitude");

-- CreateIndex
CREATE UNIQUE INDEX "warehouses_tenant_id_name_key" ON "warehouses"("tenant_id", "name");

-- CreateIndex
CREATE INDEX "zones_tenant_id_idx" ON "zones"("tenant_id");

-- CreateIndex
CREATE INDEX "zones_warehouse_id_idx" ON "zones"("warehouse_id");

-- CreateIndex
CREATE UNIQUE INDEX "zones_warehouse_id_name_key" ON "zones"("warehouse_id", "name");

-- CreateIndex
CREATE UNIQUE INDEX "storage_locations_location_code_key" ON "storage_locations"("location_code");

-- CreateIndex
CREATE INDEX "storage_locations_tenant_id_idx" ON "storage_locations"("tenant_id");

-- CreateIndex
CREATE INDEX "storage_locations_zone_id_idx" ON "storage_locations"("zone_id");

-- CreateIndex
CREATE INDEX "storage_locations_location_code_idx" ON "storage_locations"("location_code");

-- CreateIndex
CREATE INDEX "storage_locations_current_item_id_idx" ON "storage_locations"("current_item_id");

-- CreateIndex
CREATE INDEX "stock_transfers_tenant_id_idx" ON "stock_transfers"("tenant_id");

-- CreateIndex
CREATE INDEX "stock_transfers_item_id_idx" ON "stock_transfers"("item_id");

-- CreateIndex
CREATE INDEX "stock_transfers_from_warehouse_id_idx" ON "stock_transfers"("from_warehouse_id");

-- CreateIndex
CREATE INDEX "stock_transfers_to_warehouse_id_idx" ON "stock_transfers"("to_warehouse_id");

-- CreateIndex
CREATE INDEX "stock_transfers_status_idx" ON "stock_transfers"("status");

-- AddForeignKey
ALTER TABLE "inventory_movements" ADD CONSTRAINT "inventory_movements_item_id_fkey" FOREIGN KEY ("item_id") REFERENCES "inventory_items"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "inventory_alerts" ADD CONSTRAINT "inventory_alerts_item_id_fkey" FOREIGN KEY ("item_id") REFERENCES "inventory_items"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "zones" ADD CONSTRAINT "zones_warehouse_id_fkey" FOREIGN KEY ("warehouse_id") REFERENCES "warehouses"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "storage_locations" ADD CONSTRAINT "storage_locations_zone_id_fkey" FOREIGN KEY ("zone_id") REFERENCES "zones"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stock_transfers" ADD CONSTRAINT "stock_transfers_item_id_fkey" FOREIGN KEY ("item_id") REFERENCES "inventory_items"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stock_transfers" ADD CONSTRAINT "stock_transfers_from_warehouse_id_fkey" FOREIGN KEY ("from_warehouse_id") REFERENCES "warehouses"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "stock_transfers" ADD CONSTRAINT "stock_transfers_to_warehouse_id_fkey" FOREIGN KEY ("to_warehouse_id") REFERENCES "warehouses"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

