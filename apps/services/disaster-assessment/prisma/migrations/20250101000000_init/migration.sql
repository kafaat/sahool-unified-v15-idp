-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "postgis";

-- CreateEnum
CREATE TYPE "disaster_type" AS ENUM ('flood', 'drought', 'frost', 'hail', 'storm', 'pest', 'disease', 'locust', 'wildfire');

-- CreateEnum
CREATE TYPE "disaster_severity" AS ENUM ('low', 'medium', 'high', 'critical');

-- CreateEnum
CREATE TYPE "disaster_status" AS ENUM ('reported', 'verified', 'active', 'monitoring', 'resolved', 'archived');

-- CreateEnum
CREATE TYPE "disaster_alert_type" AS ENUM ('weather', 'pest', 'disease', 'flood', 'drought', 'frost', 'locust', 'general');

-- CreateTable
CREATE TABLE "disaster_reports" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "type" "disaster_type" NOT NULL DEFAULT 'flood',
    "severity" "disaster_severity" NOT NULL DEFAULT 'medium',
    "status" "disaster_status" NOT NULL DEFAULT 'reported',
    "title" VARCHAR(255) NOT NULL,
    "title_ar" VARCHAR(255),
    "description" TEXT,
    "description_ar" TEXT,
    "governorate" VARCHAR(100) NOT NULL,
    "district" VARCHAR(100),
    "location" JSONB NOT NULL,
    "affected_radius_km" DOUBLE PRECISION,
    "affected_area" DOUBLE PRECISION,
    "affected_fields_count" INTEGER NOT NULL DEFAULT 0,
    "total_affected_area_hectares" DOUBLE PRECISION,
    "total_estimated_loss_yer" BIGINT,
    "reported_by" VARCHAR(255) NOT NULL DEFAULT 'system',
    "tenant_id" VARCHAR(100) NOT NULL DEFAULT 'unassigned',
    "start_date" TIMESTAMPTZ,
    "end_date" TIMESTAMPTZ,
    "verified_at" TIMESTAMPTZ,
    "resolved_at" TIMESTAMPTZ,
    "images" JSONB,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "disaster_reports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "disaster_alerts" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "alert_type" "disaster_alert_type" NOT NULL DEFAULT 'weather',
    "severity" "disaster_severity" NOT NULL DEFAULT 'medium',
    "title" VARCHAR(255) NOT NULL,
    "title_ar" VARCHAR(255),
    "message" TEXT NOT NULL,
    "message_ar" TEXT,
    "description" TEXT,
    "description_ar" TEXT,
    "governorate" VARCHAR(100) NOT NULL,
    "governorate_ar" VARCHAR(100),
    "start_time" TIMESTAMPTZ NOT NULL,
    "end_time" TIMESTAMPTZ,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "recommendations" JSONB,
    "recommendations_ar" JSONB,
    "report_id" UUID,
    "tenant_id" VARCHAR(100) NOT NULL DEFAULT 'unassigned',
    "sent_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "disaster_alerts_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "field_assessments" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "field_id" VARCHAR(100) NOT NULL,
    "disaster_id" UUID NOT NULL,
    "damage_percentage" DOUBLE PRECISION NOT NULL,
    "damage_level" VARCHAR(50) NOT NULL,
    "damage_level_ar" VARCHAR(50),
    "affected_area_hectares" DOUBLE PRECISION NOT NULL,
    "estimated_loss_yer" BIGINT NOT NULL,
    "affected_crop_type" VARCHAR(100),
    "recommendations" JSONB,
    "recommendations_ar" JSONB,
    "insurance_eligible" BOOLEAN NOT NULL DEFAULT false,
    "insurance_claim_amount" BIGINT,
    "assessment_notes" TEXT,
    "assessment_images" JSONB,
    "assessed_by" VARCHAR(255),
    "tenant_id" VARCHAR(100) NOT NULL DEFAULT 'unassigned',
    "assessed_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "field_assessments_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "alert_subscriptions" (
    "id" UUID NOT NULL DEFAULT gen_random_uuid(),
    "user_id" VARCHAR(255) NOT NULL,
    "tenant_id" VARCHAR(100) NOT NULL DEFAULT 'unassigned',
    "governorate" VARCHAR(100) NOT NULL,
    "types" JSONB NOT NULL,
    "channels" JSONB NOT NULL,
    "is_active" BOOLEAN NOT NULL DEFAULT true,
    "alert_id" UUID,
    "created_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "alert_subscriptions_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "idx_disaster_tenant" ON "disaster_reports"("tenant_id");

-- CreateIndex
CREATE INDEX "idx_disaster_governorate" ON "disaster_reports"("governorate");

-- CreateIndex
CREATE INDEX "idx_disaster_type" ON "disaster_reports"("type");

-- CreateIndex
CREATE INDEX "idx_disaster_status" ON "disaster_reports"("status");

-- CreateIndex
CREATE INDEX "idx_disaster_severity" ON "disaster_reports"("severity");

-- CreateIndex
CREATE INDEX "idx_disaster_created" ON "disaster_reports"("created_at");

-- CreateIndex
CREATE INDEX "idx_disaster_tenant_type" ON "disaster_reports"("tenant_id", "type");

-- CreateIndex
CREATE INDEX "idx_disaster_tenant_status" ON "disaster_reports"("tenant_id", "status");

-- CreateIndex
CREATE INDEX "idx_disaster_type_severity" ON "disaster_reports"("type", "severity");

-- CreateIndex
CREATE INDEX "idx_disaster_dates" ON "disaster_reports"("start_date", "end_date");

-- CreateIndex
CREATE INDEX "idx_alert_tenant" ON "disaster_alerts"("tenant_id");

-- CreateIndex
CREATE INDEX "idx_alert_governorate" ON "disaster_alerts"("governorate");

-- CreateIndex
CREATE INDEX "idx_alert_type" ON "disaster_alerts"("alert_type");

-- CreateIndex
CREATE INDEX "idx_alert_active" ON "disaster_alerts"("is_active");

-- CreateIndex
CREATE INDEX "idx_alert_severity" ON "disaster_alerts"("severity");

-- CreateIndex
CREATE INDEX "idx_alert_report" ON "disaster_alerts"("report_id");

-- CreateIndex
CREATE INDEX "idx_assessment_field" ON "field_assessments"("field_id");

-- CreateIndex
CREATE INDEX "idx_assessment_disaster" ON "field_assessments"("disaster_id");

-- CreateIndex
CREATE INDEX "idx_assessment_tenant" ON "field_assessments"("tenant_id");

-- CreateIndex
CREATE UNIQUE INDEX "idx_subscription_user_gov" ON "alert_subscriptions"("user_id", "governorate");

-- CreateIndex
CREATE INDEX "idx_subscription_tenant" ON "alert_subscriptions"("tenant_id");

-- CreateIndex
CREATE INDEX "idx_subscription_alert" ON "alert_subscriptions"("alert_id");

-- AddForeignKey
ALTER TABLE "disaster_alerts" ADD CONSTRAINT "disaster_alerts_report_id_fkey" FOREIGN KEY ("report_id") REFERENCES "disaster_reports"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "field_assessments" ADD CONSTRAINT "field_assessments_disaster_id_fkey" FOREIGN KEY ("disaster_id") REFERENCES "disaster_reports"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "alert_subscriptions" ADD CONSTRAINT "alert_subscriptions_alert_id_fkey" FOREIGN KEY ("alert_id") REFERENCES "disaster_alerts"("id") ON DELETE SET NULL ON UPDATE CASCADE;
