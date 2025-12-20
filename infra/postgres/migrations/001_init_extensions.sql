-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - Initial Database Migration
-- تهيئة قاعدة البيانات الأولية
-- ═══════════════════════════════════════════════════════════════════════════════

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS btree_gist;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS geo;
CREATE SCHEMA IF NOT EXISTS crops;
CREATE SCHEMA IF NOT EXISTS users;
CREATE SCHEMA IF NOT EXISTS tenants;
CREATE SCHEMA IF NOT EXISTS iot;
CREATE SCHEMA IF NOT EXISTS market;

-- Migration tracking table
CREATE TABLE IF NOT EXISTS public._migrations (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Record this migration
INSERT INTO public._migrations (name) VALUES ('001_init_extensions')
ON CONFLICT (name) DO NOTHING;

-- Log success
DO $$
BEGIN
    RAISE NOTICE 'Migration 001_init_extensions completed successfully';
END $$;
