-- ═══════════════════════════════════════════════════════════════════════════════
-- Migration: Initial schema for research-core
-- الترحيل: المخطط الأساسي لنواة البحث العلمي
-- Creates all tables, enums, indexes, and constraints from scratch
-- ═══════════════════════════════════════════════════════════════════════════════

-- Step 1: Create enums
CREATE TYPE "ExperimentStatus" AS ENUM ('draft', 'active', 'locked', 'completed', 'archived');
CREATE TYPE "SampleType" AS ENUM ('soil', 'plant', 'water', 'pest', 'other');
CREATE TYPE "TreatmentType" AS ENUM ('fertilizer', 'pesticide', 'irrigation', 'seed_variety', 'other');
CREATE TYPE "LogCategory" AS ENUM ('observation', 'measurement', 'treatment', 'harvest', 'weather', 'pest', 'planting', 'germination', 'other');
CREATE TYPE "GermplasmType" AS ENUM ('seed', 'cutting', 'tissue', 'pollen', 'other');
CREATE TYPE "SeedQualityGrade" AS ENUM ('certified', 'foundation', 'registered', 'breeder', 'commercial', 'farmer_saved');

-- Step 2: Create germplasm table
CREATE TABLE "germplasm" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "accession_number" VARCHAR(50) NOT NULL,
    "common_name" VARCHAR(255) NOT NULL,
    "common_name_ar" VARCHAR(255),
    "scientific_name" VARCHAR(255),
    "genus" VARCHAR(100),
    "species" VARCHAR(100),
    "subspecies" VARCHAR(100),
    "cultivar" VARCHAR(100),
    "variety" VARCHAR(100),
    "pedigree" TEXT,
    "type" "GermplasmType" NOT NULL DEFAULT 'seed',
    "country_of_origin" VARCHAR(100),
    "region_of_origin" VARCHAR(255),
    "collection_site" VARCHAR(255),
    "collection_date" DATE,
    "collected_by" TEXT,
    "donor_institution" VARCHAR(255),
    "donor_accession_number" VARCHAR(50),
    "growth_habit" VARCHAR(100),
    "maturity_days" INTEGER,
    "yield_potential" VARCHAR(100),
    "drought_tolerance" VARCHAR(50),
    "disease_resistance" JSONB NOT NULL DEFAULT '{}',
    "pest_resistance" JSONB NOT NULL DEFAULT '{}',
    "quality_traits" JSONB NOT NULL DEFAULT '{}',
    "storage_location" VARCHAR(255),
    "storage_conditions" VARCHAR(255),
    "storage_temperature" DECIMAL(5,2),
    "storage_humidity" DECIMAL(5,2),
    "is_available" BOOLEAN NOT NULL DEFAULT true,
    "quantity_available" DECIMAL(10,3),
    "quantity_unit" VARCHAR(50),
    "description" TEXT,
    "description_ar" TEXT,
    "photos" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "documents" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "germplasm_pkey" PRIMARY KEY ("id")
);

-- Step 3: Create seed_lots table
CREATE TABLE "seed_lots" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "germplasm_id" TEXT NOT NULL,
    "lot_number" VARCHAR(50) NOT NULL,
    "initial_quantity" DECIMAL(10,3) NOT NULL,
    "current_quantity" DECIMAL(10,3) NOT NULL,
    "quantity_unit" VARCHAR(50) NOT NULL,
    "seed_count" INTEGER,
    "thousand_seed_weight" DECIMAL(8,3),
    "quality_grade" "SeedQualityGrade" NOT NULL DEFAULT 'commercial',
    "germination_rate" DECIMAL(5,2),
    "germination_test_date" DATE,
    "purity_percentage" DECIMAL(5,2),
    "moisture_content" DECIMAL(5,2),
    "vigor_index" DECIMAL(5,2),
    "production_date" DATE,
    "harvest_date" DATE,
    "production_location" VARCHAR(255),
    "production_season" VARCHAR(50),
    "produced_by" TEXT,
    "certification_number" VARCHAR(100),
    "certified_by" VARCHAR(255),
    "certification_date" DATE,
    "expiry_date" DATE,
    "is_treated" BOOLEAN NOT NULL DEFAULT false,
    "treatment_type" VARCHAR(100),
    "treatment_product" VARCHAR(255),
    "treatment_date" DATE,
    "storage_location" VARCHAR(255),
    "storage_conditions" VARCHAR(255),
    "notes" TEXT,
    "notes_ar" TEXT,
    "photos" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "documents" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "seed_lots_pkey" PRIMARY KEY ("id")
);

-- Step 4: Create experiments table
CREATE TABLE "experiments" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "title_ar" VARCHAR(255),
    "description" TEXT,
    "description_ar" TEXT,
    "hypothesis" TEXT,
    "hypothesis_ar" TEXT,
    "start_date" DATE NOT NULL,
    "end_date" DATE,
    "status" "ExperimentStatus" NOT NULL DEFAULT 'draft',
    "locked_at" TIMESTAMP(3),
    "locked_by" TEXT,
    "principal_researcher_id" TEXT NOT NULL,
    "organization_id" TEXT,
    "farm_id" TEXT,
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "tags" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,
    "version" INTEGER NOT NULL DEFAULT 1,

    CONSTRAINT "experiments_pkey" PRIMARY KEY ("id")
);

-- Step 5: Create research_protocols table
CREATE TABLE "research_protocols" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "experiment_id" TEXT NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "name_ar" VARCHAR(255),
    "description" TEXT,
    "description_ar" TEXT,
    "methodology" TEXT NOT NULL,
    "methodology_ar" TEXT,
    "variables" JSONB NOT NULL DEFAULT '{}',
    "measurement_schedule" JSONB NOT NULL DEFAULT '{}',
    "equipment_required" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "safety_guidelines" TEXT,
    "version" INTEGER NOT NULL DEFAULT 1,
    "approved_by" TEXT,
    "approved_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "research_protocols_pkey" PRIMARY KEY ("id")
);

-- Step 6: Create research_plots table
CREATE TABLE "research_plots" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "experiment_id" TEXT NOT NULL,
    "plot_code" VARCHAR(50) NOT NULL,
    "name" VARCHAR(255),
    "name_ar" VARCHAR(255),
    "area_sqm" DECIMAL(10,2),
    "soil_type" VARCHAR(100),
    "soil_ph" DECIMAL(4,2),
    "previous_crop" VARCHAR(100),
    "replicate_number" INTEGER NOT NULL DEFAULT 1,
    "block_number" INTEGER,
    "row_number" INTEGER,
    "column_number" INTEGER,
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "research_plots_pkey" PRIMARY KEY ("id")
);

-- Step 7: Create treatments table
CREATE TABLE "treatments" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "experiment_id" TEXT NOT NULL,
    "plot_id" TEXT,
    "treatment_code" VARCHAR(50) NOT NULL,
    "name" VARCHAR(255) NOT NULL,
    "name_ar" VARCHAR(255),
    "type" "TreatmentType" NOT NULL,
    "description" TEXT,
    "description_ar" TEXT,
    "dosage" VARCHAR(100),
    "dosage_unit" VARCHAR(50),
    "application_method" VARCHAR(100),
    "application_frequency" VARCHAR(100),
    "start_date" DATE,
    "end_date" DATE,
    "is_control" BOOLEAN NOT NULL DEFAULT false,
    "parameters" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "treatments_pkey" PRIMARY KEY ("id")
);

-- Step 8: Create plantings table
CREATE TABLE "plantings" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "experiment_id" TEXT NOT NULL,
    "plot_id" TEXT,
    "germplasm_id" TEXT NOT NULL,
    "seed_lot_id" TEXT,
    "planting_date" DATE NOT NULL,
    "planting_method" VARCHAR(100),
    "seeding_rate" DECIMAL(10,3),
    "seeding_rate_unit" VARCHAR(50),
    "seeds_per_hill" INTEGER,
    "seed_depth" DECIMAL(5,2),
    "seed_depth_unit" VARCHAR(20),
    "row_spacing" DECIMAL(6,2),
    "plant_spacing" DECIMAL(6,2),
    "spacing_unit" VARCHAR(20),
    "planted_area" DECIMAL(10,2),
    "planted_area_unit" VARCHAR(20),
    "number_of_rows" INTEGER,
    "plants_per_row" INTEGER,
    "total_plants_expected" INTEGER,
    "germination_date" DATE,
    "emergence_date" DATE,
    "germination_count" INTEGER,
    "germination_percentage" DECIMAL(5,2),
    "thinning_date" DATE,
    "final_plant_count" INTEGER,
    "planted_by" TEXT NOT NULL,
    "notes" TEXT,
    "notes_ar" TEXT,
    "photos" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "plantings_pkey" PRIMARY KEY ("id")
);

-- Step 9: Create research_daily_logs table
CREATE TABLE "research_daily_logs" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "experiment_id" TEXT NOT NULL,
    "plot_id" TEXT,
    "treatment_id" TEXT,
    "log_date" DATE NOT NULL,
    "log_time" VARCHAR(8),
    "category" "LogCategory" NOT NULL,
    "title" VARCHAR(255) NOT NULL,
    "title_ar" VARCHAR(255),
    "notes" TEXT,
    "notes_ar" TEXT,
    "measurements" JSONB NOT NULL DEFAULT '{}',
    "weather_conditions" JSONB NOT NULL DEFAULT '{}',
    "photos" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "attachments" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "recorded_by" TEXT NOT NULL,
    "device_id" VARCHAR(100),
    "offline_id" VARCHAR(100),
    "hash" VARCHAR(64),
    "synced_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "research_daily_logs_pkey" PRIMARY KEY ("id")
);

-- Step 10: Create lab_samples table
CREATE TABLE "lab_samples" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "experiment_id" TEXT NOT NULL,
    "plot_id" TEXT,
    "log_id" TEXT,
    "sample_code" VARCHAR(100) NOT NULL,
    "type" "SampleType" NOT NULL,
    "description" TEXT,
    "description_ar" TEXT,
    "collection_date" DATE NOT NULL,
    "collection_time" VARCHAR(8),
    "collected_by" TEXT NOT NULL,
    "storage_location" VARCHAR(255),
    "storage_conditions" VARCHAR(255),
    "quantity" DECIMAL(10,3),
    "quantity_unit" VARCHAR(50),
    "analysis_status" VARCHAR(50) NOT NULL DEFAULT 'pending',
    "analysis_results" JSONB NOT NULL DEFAULT '{}',
    "analyzed_by" TEXT,
    "analyzed_at" TIMESTAMP(3),
    "photos" TEXT[] DEFAULT ARRAY[]::TEXT[],
    "metadata" JSONB NOT NULL DEFAULT '{}',
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "lab_samples_pkey" PRIMARY KEY ("id")
);

-- Step 11: Create digital_signatures table
CREATE TABLE "digital_signatures" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "entity_type" VARCHAR(50) NOT NULL,
    "entity_id" TEXT NOT NULL,
    "signer_id" TEXT NOT NULL,
    "signature_hash" VARCHAR(128) NOT NULL,
    "algorithm" VARCHAR(50) NOT NULL DEFAULT 'HMAC-SHA256',
    "payload_hash" VARCHAR(128) NOT NULL,
    "timestamp" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ip_address" VARCHAR(45),
    "device_info" JSONB NOT NULL DEFAULT '{}',
    "purpose" VARCHAR(100),
    "is_valid" BOOLEAN NOT NULL DEFAULT true,
    "invalidated_at" TIMESTAMP(3),
    "invalidated_reason" TEXT,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "digital_signatures_pkey" PRIMARY KEY ("id")
);

-- Step 12: Create experiment_collaborators table
CREATE TABLE "experiment_collaborators" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "experiment_id" TEXT NOT NULL,
    "user_id" TEXT NOT NULL,
    "role" VARCHAR(50) NOT NULL,
    "permissions" JSONB NOT NULL DEFAULT '{"read": true, "write": false, "admin": false}',
    "invited_by" TEXT,
    "accepted_at" TIMESTAMP(3),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "experiment_collaborators_pkey" PRIMARY KEY ("id")
);

-- Step 13: Create experiment_audit_log table
CREATE TABLE "experiment_audit_log" (
    "id" TEXT NOT NULL,
    "tenant_id" TEXT NOT NULL,
    "experiment_id" TEXT,
    "entity_type" VARCHAR(50) NOT NULL,
    "entity_id" TEXT NOT NULL,
    "action" VARCHAR(50) NOT NULL,
    "old_values" JSONB,
    "new_values" JSONB,
    "changed_by" TEXT NOT NULL,
    "changed_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "ip_address" VARCHAR(45),
    "user_agent" TEXT,

    CONSTRAINT "experiment_audit_log_pkey" PRIMARY KEY ("id")
);

-- Step 14: Create unique constraints
CREATE UNIQUE INDEX "uq_germplasm_tenant_accession" ON "germplasm"("tenant_id", "accession_number");
CREATE UNIQUE INDEX "uq_seed_lot_tenant_number" ON "seed_lots"("tenant_id", "lot_number");
CREATE UNIQUE INDEX "research_plots_experiment_id_plot_code_key" ON "research_plots"("experiment_id", "plot_code");
CREATE UNIQUE INDEX "uq_daily_log_tenant_offline" ON "research_daily_logs"("tenant_id", "offline_id");
CREATE UNIQUE INDEX "uq_lab_sample_tenant_code" ON "lab_samples"("tenant_id", "sample_code");
CREATE UNIQUE INDEX "digital_signatures_tenant_id_entity_type_entity_id_signer_i_key" ON "digital_signatures"("tenant_id", "entity_type", "entity_id", "signer_id", "purpose");
CREATE UNIQUE INDEX "experiment_collaborators_experiment_id_user_id_key" ON "experiment_collaborators"("experiment_id", "user_id");

-- Step 15: Create indexes for germplasm
CREATE INDEX "idx_germplasm_tenant" ON "germplasm"("tenant_id");
CREATE INDEX "idx_germplasm_tenant_available" ON "germplasm"("tenant_id", "is_available");
CREATE INDEX "idx_germplasm_available" ON "germplasm"("is_available");
CREATE INDEX "idx_germplasm_type" ON "germplasm"("type");
CREATE INDEX "idx_germplasm_common_name" ON "germplasm"("common_name");

-- Step 16: Create indexes for seed_lots
CREATE INDEX "idx_seed_lot_tenant" ON "seed_lots"("tenant_id");
CREATE INDEX "idx_seed_lot_germplasm" ON "seed_lots"("germplasm_id");
CREATE INDEX "idx_seed_lot_quality" ON "seed_lots"("quality_grade");
CREATE INDEX "idx_seed_lot_expiry" ON "seed_lots"("expiry_date");
CREATE INDEX "idx_seed_lot_production" ON "seed_lots"("production_date");

-- Step 17: Create indexes for experiments
CREATE INDEX "idx_experiment_tenant" ON "experiments"("tenant_id");
CREATE INDEX "idx_experiment_tenant_status" ON "experiments"("tenant_id", "status");
CREATE INDEX "idx_experiment_status" ON "experiments"("status");
CREATE INDEX "idx_experiment_pi" ON "experiments"("principal_researcher_id");
CREATE INDEX "idx_experiment_org" ON "experiments"("organization_id");
CREATE INDEX "idx_experiment_farm" ON "experiments"("farm_id");
CREATE INDEX "idx_experiment_start_date" ON "experiments"("start_date");
CREATE INDEX "idx_experiment_end_date" ON "experiments"("end_date");
CREATE INDEX "idx_experiment_status_date" ON "experiments"("status", "start_date");

-- Step 18: Create indexes for research_protocols
CREATE INDEX "idx_protocol_tenant" ON "research_protocols"("tenant_id");
CREATE INDEX "idx_protocol_experiment" ON "research_protocols"("experiment_id");

-- Step 19: Create indexes for research_plots
CREATE INDEX "idx_plot_tenant" ON "research_plots"("tenant_id");

-- Step 20: Create indexes for treatments
CREATE INDEX "idx_treatment_tenant" ON "treatments"("tenant_id");
CREATE INDEX "idx_treatment_experiment" ON "treatments"("experiment_id");
CREATE INDEX "idx_treatment_plot" ON "treatments"("plot_id");
CREATE INDEX "idx_treatment_type" ON "treatments"("type");
CREATE INDEX "idx_treatment_control" ON "treatments"("is_control");

-- Step 21: Create indexes for plantings
CREATE INDEX "idx_planting_tenant" ON "plantings"("tenant_id");
CREATE INDEX "idx_planting_experiment" ON "plantings"("experiment_id");
CREATE INDEX "idx_planting_plot" ON "plantings"("plot_id");
CREATE INDEX "idx_planting_germplasm" ON "plantings"("germplasm_id");
CREATE INDEX "idx_planting_seed_lot" ON "plantings"("seed_lot_id");
CREATE INDEX "idx_planting_date" ON "plantings"("planting_date");
CREATE INDEX "idx_planting_exp_date" ON "plantings"("experiment_id", "planting_date");

-- Step 22: Create indexes for research_daily_logs
CREATE INDEX "idx_daily_log_tenant" ON "research_daily_logs"("tenant_id");
CREATE INDEX "idx_daily_log_experiment" ON "research_daily_logs"("experiment_id");
CREATE INDEX "idx_daily_log_plot" ON "research_daily_logs"("plot_id");
CREATE INDEX "idx_daily_log_treatment" ON "research_daily_logs"("treatment_id");
CREATE INDEX "idx_daily_log_date" ON "research_daily_logs"("log_date");
CREATE INDEX "idx_daily_log_category" ON "research_daily_logs"("category");
CREATE INDEX "idx_daily_log_exp_date" ON "research_daily_logs"("experiment_id", "log_date");
CREATE INDEX "idx_daily_log_recorder" ON "research_daily_logs"("recorded_by");

-- Step 23: Create indexes for lab_samples
CREATE INDEX "idx_lab_sample_tenant" ON "lab_samples"("tenant_id");
CREATE INDEX "idx_lab_sample_experiment" ON "lab_samples"("experiment_id");
CREATE INDEX "idx_lab_sample_plot" ON "lab_samples"("plot_id");
CREATE INDEX "idx_lab_sample_log" ON "lab_samples"("log_id");
CREATE INDEX "idx_lab_sample_type" ON "lab_samples"("type");
CREATE INDEX "idx_lab_sample_status" ON "lab_samples"("analysis_status");
CREATE INDEX "idx_lab_sample_collection_date" ON "lab_samples"("collection_date");
CREATE INDEX "idx_lab_sample_exp_date" ON "lab_samples"("experiment_id", "collection_date");

-- Step 24: Create indexes for digital_signatures
CREATE INDEX "idx_signature_tenant" ON "digital_signatures"("tenant_id");
CREATE INDEX "idx_signature_entity" ON "digital_signatures"("entity_type", "entity_id");
CREATE INDEX "idx_signature_signer" ON "digital_signatures"("signer_id");
CREATE INDEX "idx_signature_valid" ON "digital_signatures"("is_valid");

-- Step 25: Create indexes for experiment_collaborators
CREATE INDEX "idx_collaborator_tenant" ON "experiment_collaborators"("tenant_id");

-- Step 26: Create indexes for experiment_audit_log
CREATE INDEX "idx_audit_log_tenant" ON "experiment_audit_log"("tenant_id");
CREATE INDEX "idx_audit_log_experiment" ON "experiment_audit_log"("experiment_id");
CREATE INDEX "idx_audit_log_entity" ON "experiment_audit_log"("entity_type", "entity_id");
CREATE INDEX "idx_audit_log_user" ON "experiment_audit_log"("changed_by");
CREATE INDEX "idx_audit_log_date" ON "experiment_audit_log"("changed_at");
CREATE INDEX "idx_audit_log_action" ON "experiment_audit_log"("action");

-- Step 27: Add foreign key constraints
ALTER TABLE "seed_lots" ADD CONSTRAINT "seed_lots_germplasm_id_fkey" FOREIGN KEY ("germplasm_id") REFERENCES "germplasm"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "research_protocols" ADD CONSTRAINT "research_protocols_experiment_id_fkey" FOREIGN KEY ("experiment_id") REFERENCES "experiments"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "research_plots" ADD CONSTRAINT "research_plots_experiment_id_fkey" FOREIGN KEY ("experiment_id") REFERENCES "experiments"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "treatments" ADD CONSTRAINT "treatments_experiment_id_fkey" FOREIGN KEY ("experiment_id") REFERENCES "experiments"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "treatments" ADD CONSTRAINT "treatments_plot_id_fkey" FOREIGN KEY ("plot_id") REFERENCES "research_plots"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "plantings" ADD CONSTRAINT "plantings_experiment_id_fkey" FOREIGN KEY ("experiment_id") REFERENCES "experiments"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "plantings" ADD CONSTRAINT "plantings_germplasm_id_fkey" FOREIGN KEY ("germplasm_id") REFERENCES "germplasm"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
ALTER TABLE "plantings" ADD CONSTRAINT "plantings_seed_lot_id_fkey" FOREIGN KEY ("seed_lot_id") REFERENCES "seed_lots"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "research_daily_logs" ADD CONSTRAINT "research_daily_logs_experiment_id_fkey" FOREIGN KEY ("experiment_id") REFERENCES "experiments"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "research_daily_logs" ADD CONSTRAINT "research_daily_logs_plot_id_fkey" FOREIGN KEY ("plot_id") REFERENCES "research_plots"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "research_daily_logs" ADD CONSTRAINT "research_daily_logs_treatment_id_fkey" FOREIGN KEY ("treatment_id") REFERENCES "treatments"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "lab_samples" ADD CONSTRAINT "lab_samples_experiment_id_fkey" FOREIGN KEY ("experiment_id") REFERENCES "experiments"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "lab_samples" ADD CONSTRAINT "lab_samples_plot_id_fkey" FOREIGN KEY ("plot_id") REFERENCES "research_plots"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "lab_samples" ADD CONSTRAINT "lab_samples_log_id_fkey" FOREIGN KEY ("log_id") REFERENCES "research_daily_logs"("id") ON DELETE SET NULL ON UPDATE CASCADE;
ALTER TABLE "experiment_collaborators" ADD CONSTRAINT "experiment_collaborators_experiment_id_fkey" FOREIGN KEY ("experiment_id") REFERENCES "experiments"("id") ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE "experiment_audit_log" ADD CONSTRAINT "experiment_audit_log_experiment_id_fkey" FOREIGN KEY ("experiment_id") REFERENCES "experiments"("id") ON DELETE SET NULL ON UPDATE CASCADE;
