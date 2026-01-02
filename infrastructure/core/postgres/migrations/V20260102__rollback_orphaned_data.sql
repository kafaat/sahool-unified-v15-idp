-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - ROLLBACK Migration
-- Restore Orphaned Data from Backup Tables
--
-- Author: AI Technical Orchestrator
-- Date: 2026-01-02
-- Version: 16.0.1
--
-- ⚠️ WARNING: Only run this if you need to UNDO the orphaned data cleanup!
-- This will restore the backed up orphaned records and remove FK constraints.
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 0: Verify this is intentional
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE '  ⚠️ ROLLBACK MIGRATION STARTING';
    RAISE NOTICE '  This will restore orphaned data and remove FK constraints!';
    RAISE NOTICE '  Timestamp: %', NOW();
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 1: Drop Foreign Key Constraints (reverse order)
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    -- Drop tasks -> users FK
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_tasks_assigned_to' AND table_name = 'tasks'
    ) THEN
        ALTER TABLE tasks DROP CONSTRAINT fk_tasks_assigned_to;
        RAISE NOTICE '  🔓 Dropped FK: fk_tasks_assigned_to';
    END IF;

    -- Drop tasks -> fields FK
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_tasks_field_id' AND table_name = 'tasks'
    ) THEN
        ALTER TABLE tasks DROP CONSTRAINT fk_tasks_field_id;
        RAISE NOTICE '  🔓 Dropped FK: fk_tasks_field_id';
    END IF;

    -- Drop sensor_readings -> fields FK
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_sensor_readings_field_id' AND table_name = 'sensor_readings'
    ) THEN
        ALTER TABLE sensor_readings DROP CONSTRAINT fk_sensor_readings_field_id;
        RAISE NOTICE '  🔓 Dropped FK: fk_sensor_readings_field_id';
    END IF;

    -- Drop fields -> tenants FK
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_fields_tenant_id' AND table_name = 'fields'
    ) THEN
        ALTER TABLE fields DROP CONSTRAINT fk_fields_tenant_id;
        RAISE NOTICE '  🔓 Dropped FK: fk_fields_tenant_id';
    END IF;

    -- Drop fields -> users FK
    IF EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_fields_user_id' AND table_name = 'fields'
    ) THEN
        ALTER TABLE fields DROP CONSTRAINT fk_fields_user_id;
        RAISE NOTICE '  🔓 Dropped FK: fk_fields_user_id';
    END IF;

    RAISE NOTICE '  ✅ All FK constraints removed';
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 2: Restore orphaned fields from backup
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    restored_count INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '_orphaned_fields_backup') THEN
        -- Only restore if not already in fields table
        INSERT INTO fields (id, user_id, tenant_id, name, created_at)
        SELECT id, user_id, tenant_id, name, created_at
        FROM _orphaned_fields_backup
        WHERE id NOT IN (SELECT id FROM fields WHERE id IS NOT NULL);

        GET DIAGNOSTICS restored_count = ROW_COUNT;
        RAISE NOTICE '  ♻️ Restored % orphaned fields', restored_count;
    ELSE
        RAISE NOTICE '  ⚠️ No backup table found for fields';
    END IF;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 3: Restore orphaned sensor readings from backup
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    restored_count INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '_orphaned_sensor_data_backup') THEN
        -- Restore with original reading data
        INSERT INTO sensor_readings (id, device_id, field_id, sensor_type, value, unit, created_at)
        SELECT
            id,
            device_id,
            field_id,
            reading_data->>'sensor_type',
            (reading_data->>'value')::DECIMAL,
            reading_data->>'unit',
            created_at
        FROM _orphaned_sensor_data_backup
        WHERE id NOT IN (SELECT id FROM sensor_readings WHERE id IS NOT NULL);

        GET DIAGNOSTICS restored_count = ROW_COUNT;
        RAISE NOTICE '  ♻️ Restored % orphaned sensor readings', restored_count;
    ELSE
        RAISE NOTICE '  ⚠️ No backup table found for sensor readings';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE WARNING 'Could not restore sensor readings: %', SQLERRM;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 4: Restore orphaned tasks from backup
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    restored_count INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = '_orphaned_tasks_backup') THEN
        INSERT INTO tasks (id, field_id, assigned_to, title, status, priority, created_at)
        SELECT
            id,
            field_id,
            assigned_to,
            task_data->>'title',
            task_data->>'status',
            task_data->>'priority',
            created_at
        FROM _orphaned_tasks_backup
        WHERE id NOT IN (SELECT id FROM tasks WHERE id IS NOT NULL);

        GET DIAGNOSTICS restored_count = ROW_COUNT;
        RAISE NOTICE '  ♻️ Restored % orphaned tasks', restored_count;
    ELSE
        RAISE NOTICE '  ⚠️ No backup table found for tasks';
    END IF;
EXCEPTION
    WHEN others THEN
        RAISE WARNING 'Could not restore tasks: %', SQLERRM;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 5: Drop the stale GPS view (optional cleanup)
-- ─────────────────────────────────────────────────────────────────────────────
DROP VIEW IF EXISTS v_stale_gps_data;
RAISE NOTICE '  🗑️ Dropped v_stale_gps_data view';

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 6: Summary
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE '  ROLLBACK COMPLETE';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE '  ♻️ Orphaned data has been restored from backup tables';
    RAISE NOTICE '  🔓 Foreign key constraints have been removed';
    RAISE NOTICE '';
    RAISE NOTICE '  ⚠️ The system is now in a degraded state!';
    RAISE NOTICE '  ⚠️ Orphaned data can accumulate again.';
    RAISE NOTICE '  ⚠️ Re-run the fix migration after resolving issues.';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
END $$;
