-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - MLflow Database Initialization
-- قاعدة بيانات MLflow لإدارة نماذج الذكاء الاصطناعي
-- ═══════════════════════════════════════════════════════════════════════════════
-- This creates a separate database for MLflow experiment tracking and model registry.
-- MLflow manages its own schema, so we only need to create the database.
-- ═══════════════════════════════════════════════════════════════════════════════

-- Create MLflow database if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = 'mlflow') THEN
        -- Can't create database inside transaction, so we use a workaround
        RAISE NOTICE 'MLflow database needs to be created. Run: CREATE DATABASE mlflow;';
    ELSE
        RAISE NOTICE 'MLflow database already exists';
    END IF;
END;
$$;

-- Create mlflow database (must be run separately if not exists)
-- Note: This is handled by the SELECT/CREATE below
SELECT 'CREATE DATABASE mlflow'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'mlflow')\gexec

-- Grant privileges to the application user
GRANT ALL PRIVILEGES ON DATABASE mlflow TO :POSTGRES_USER;

-- Note: MLflow will automatically create its schema tables when it first connects:
-- - experiments
-- - runs
-- - metrics
-- - params
-- - tags
-- - registered_models
-- - model_versions
-- - etc.

RAISE NOTICE '✅ MLflow database configuration complete';
