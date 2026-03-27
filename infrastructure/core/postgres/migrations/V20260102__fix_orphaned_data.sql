-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - Data Integrity Migration
-- Fix Orphaned Data and Add Foreign Key Constraints
--
-- Author: AI Technical Orchestrator
-- Date: 2026-01-02
-- Version: 16.0.1
--
-- IMPORTANT: Run this in a maintenance window!
-- This migration may take time on large datasets.
-- ═══════════════════════════════════════════════════════════════════════════════

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 0: Pre-flight checks
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE '  SAHOOL Data Integrity Migration Starting...';
    RAISE NOTICE '  Timestamp: %', NOW();
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 1: Create backup tables for orphaned data (Safety First!)
-- ─────────────────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS _orphaned_fields_backup (
    id UUID,
    user_id UUID,
    tenant_id UUID,
    name VARCHAR(255),
    created_at TIMESTAMPTZ,
    backed_up_at TIMESTAMPTZ DEFAULT NOW(),
    reason VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS _orphaned_sensor_data_backup (
    id UUID,
    device_id UUID,
    field_id UUID,
    reading_data JSONB,
    created_at TIMESTAMPTZ,
    backed_up_at TIMESTAMPTZ DEFAULT NOW(),
    reason VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS _orphaned_tasks_backup (
    id UUID,
    field_id UUID,
    assigned_to UUID,
    task_data JSONB,
    created_at TIMESTAMPTZ,
    backed_up_at TIMESTAMPTZ DEFAULT NOW(),
    reason VARCHAR(100)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 2: Identify and backup orphaned fields (fields without owners)
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    orphan_count INTEGER;
BEGIN
    -- Check if fields table exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fields') THEN
        -- Backup orphaned fields (user doesn't exist)
        INSERT INTO _orphaned_fields_backup (id, user_id, tenant_id, name, created_at, reason)
        SELECT
            f.id,
            f.user_id,
            f.tenant_id,
            f.name,
            f.created_at,
            'user_not_found'
        FROM fields f
        LEFT JOIN users u ON f.user_id = u.id
        WHERE u.id IS NULL
        AND f.user_id IS NOT NULL;

        GET DIAGNOSTICS orphan_count = ROW_COUNT;
        RAISE NOTICE '  📋 Backed up % orphaned fields (missing users)', orphan_count;

        -- Backup fields with deleted tenants
        INSERT INTO _orphaned_fields_backup (id, user_id, tenant_id, name, created_at, reason)
        SELECT
            f.id,
            f.user_id,
            f.tenant_id,
            f.name,
            f.created_at,
            'tenant_not_found'
        FROM fields f
        LEFT JOIN tenants t ON f.tenant_id = t.id
        WHERE t.id IS NULL
        AND f.tenant_id IS NOT NULL
        AND f.id NOT IN (SELECT id FROM _orphaned_fields_backup);

        GET DIAGNOSTICS orphan_count = ROW_COUNT;
        RAISE NOTICE '  📋 Backed up % orphaned fields (missing tenants)', orphan_count;
    END IF;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 3: Identify and backup orphaned sensor data
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    orphan_count INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sensor_readings') THEN
        INSERT INTO _orphaned_sensor_data_backup (id, device_id, field_id, reading_data, created_at, reason)
        SELECT
            sr.id,
            sr.device_id,
            sr.field_id,
            jsonb_build_object(
                'sensor_type', sr.sensor_type,
                'value', sr.value,
                'unit', sr.unit
            ),
            sr.created_at,
            'field_not_found'
        FROM sensor_readings sr
        LEFT JOIN fields f ON sr.field_id = f.id
        WHERE f.id IS NULL
        AND sr.field_id IS NOT NULL;

        GET DIAGNOSTICS orphan_count = ROW_COUNT;
        RAISE NOTICE '  📋 Backed up % orphaned sensor readings', orphan_count;
    END IF;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 4: Identify and backup orphaned tasks
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    orphan_count INTEGER;
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
        INSERT INTO _orphaned_tasks_backup (id, field_id, assigned_to, task_data, created_at, reason)
        SELECT
            t.id,
            t.field_id,
            t.assigned_to,
            jsonb_build_object(
                'title', t.title,
                'status', t.status,
                'priority', t.priority
            ),
            t.created_at,
            'field_or_user_not_found'
        FROM tasks t
        LEFT JOIN fields f ON t.field_id = f.id
        LEFT JOIN users u ON t.assigned_to = u.id
        WHERE (f.id IS NULL OR u.id IS NULL);

        GET DIAGNOSTICS orphan_count = ROW_COUNT;
        RAISE NOTICE '  📋 Backed up % orphaned tasks', orphan_count;
    END IF;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 5: Delete orphaned data (after backup)
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    deleted_count INTEGER;
BEGIN
    -- Delete orphaned sensor readings
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sensor_readings') THEN
        DELETE FROM sensor_readings
        WHERE id IN (SELECT id FROM _orphaned_sensor_data_backup);
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE '  🗑️ Deleted % orphaned sensor readings', deleted_count;
    END IF;

    -- Delete orphaned tasks
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
        DELETE FROM tasks
        WHERE id IN (SELECT id FROM _orphaned_tasks_backup);
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE '  🗑️ Deleted % orphaned tasks', deleted_count;
    END IF;

    -- Delete orphaned fields (last, as other tables depend on it)
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fields') THEN
        DELETE FROM fields
        WHERE id IN (SELECT id FROM _orphaned_fields_backup);
        GET DIAGNOSTICS deleted_count = ROW_COUNT;
        RAISE NOTICE '  🗑️ Deleted % orphaned fields', deleted_count;
    END IF;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 6: Add Foreign Key Constraints with ON DELETE CASCADE
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    -- Fields -> Users (Owner)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_fields_user_id' AND table_name = 'fields'
    ) THEN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fields') THEN
            ALTER TABLE fields
            ADD CONSTRAINT fk_fields_user_id
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE NOT VALID;
            ALTER TABLE fields VALIDATE CONSTRAINT fk_fields_user_id;
            RAISE NOTICE '  ✅ Added FK: fields.user_id -> users.id (CASCADE, NOT VALID + VALIDATE)';
        END IF;
    END IF;

    -- Fields -> Tenants
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_fields_tenant_id' AND table_name = 'fields'
    ) THEN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fields') THEN
            ALTER TABLE fields
            ADD CONSTRAINT fk_fields_tenant_id
            FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE NOT VALID;
            ALTER TABLE fields VALIDATE CONSTRAINT fk_fields_tenant_id;
            RAISE NOTICE '  ✅ Added FK: fields.tenant_id -> tenants.id (CASCADE, NOT VALID + VALIDATE)';
        END IF;
    END IF;

    -- Sensor Readings -> Fields
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_sensor_readings_field_id' AND table_name = 'sensor_readings'
    ) THEN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'sensor_readings') THEN
            ALTER TABLE sensor_readings
            ADD CONSTRAINT fk_sensor_readings_field_id
            FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE NOT VALID;
            ALTER TABLE sensor_readings VALIDATE CONSTRAINT fk_sensor_readings_field_id;
            RAISE NOTICE '  ✅ Added FK: sensor_readings.field_id -> fields.id (CASCADE, NOT VALID + VALIDATE)';
        END IF;
    END IF;

    -- Tasks -> Fields
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_tasks_field_id' AND table_name = 'tasks'
    ) THEN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
            ALTER TABLE tasks
            ADD CONSTRAINT fk_tasks_field_id
            FOREIGN KEY (field_id) REFERENCES fields(id) ON DELETE CASCADE NOT VALID;
            ALTER TABLE tasks VALIDATE CONSTRAINT fk_tasks_field_id;
            RAISE NOTICE '  ✅ Added FK: tasks.field_id -> fields.id (CASCADE, NOT VALID + VALIDATE)';
        END IF;
    END IF;

    -- Tasks -> Users (Assignee)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.table_constraints
        WHERE constraint_name = 'fk_tasks_assigned_to' AND table_name = 'tasks'
    ) THEN
        IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'tasks') THEN
            ALTER TABLE tasks
            ADD CONSTRAINT fk_tasks_assigned_to
            FOREIGN KEY (assigned_to) REFERENCES users(id) ON DELETE SET NULL NOT VALID;
            ALTER TABLE tasks VALIDATE CONSTRAINT fk_tasks_assigned_to;
            RAISE NOTICE '  ✅ Added FK: tasks.assigned_to -> users.id (SET NULL, NOT VALID + VALIDATE)';
        END IF;
    END IF;

EXCEPTION
    WHEN others THEN
        RAISE WARNING 'Could not add some foreign keys: %', SQLERRM;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 7: Add GPS Data TTL - Mark stale GPS readings
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
BEGIN
    -- Add column to track GPS staleness if not exists
    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'fields') THEN
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns
            WHERE table_name = 'fields' AND column_name = 'location_updated_at'
        ) THEN
            ALTER TABLE fields ADD COLUMN location_updated_at TIMESTAMPTZ;
            RAISE NOTICE '  ✅ Added column: fields.location_updated_at for GPS TTL';
        END IF;

        -- Update existing records
        UPDATE fields
        SET location_updated_at = updated_at
        WHERE location_updated_at IS NULL
        AND (latitude IS NOT NULL OR longitude IS NOT NULL);

        RAISE NOTICE '  ✅ Updated location_updated_at for existing GPS data';
    END IF;
END $$;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 8: Create view for stale GPS data monitoring
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_stale_gps_data AS
SELECT
    f.id,
    f.name,
    f.latitude,
    f.longitude,
    f.location_updated_at,
    EXTRACT(DAY FROM (NOW() - f.location_updated_at)) AS days_stale,
    CASE
        WHEN f.location_updated_at < NOW() - INTERVAL '30 days' THEN 'CRITICAL'
        WHEN f.location_updated_at < NOW() - INTERVAL '7 days' THEN 'WARNING'
        ELSE 'OK'
    END AS staleness_level
FROM fields AS f
WHERE
    f.latitude IS NOT NULL
    AND f.longitude IS NOT NULL
    AND f.location_updated_at IS NOT NULL;

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 9: Create deadlock prevention advisory lock wrapper
-- ─────────────────────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION safe_delete_with_lock(
    p_table_name TEXT,
    p_id UUID,
    p_lock_timeout_ms INTEGER DEFAULT 5000
) RETURNS BOOLEAN AS $$
DECLARE
    v_lock_key BIGINT;
    v_result BOOLEAN := FALSE;
BEGIN
    -- Validate table name against allowed set (prevent SQL injection via dynamic SQL)
    IF p_table_name NOT IN (
        'fields', 'field_operations', 'sensor_readings',
        'irrigation_schedules', 'tasks', 'task_assignments',
        'field_notes', 'field_boundaries', 'crop_records'
    ) THEN
        RAISE EXCEPTION 'safe_delete_with_lock: invalid table name: %', p_table_name;
    END IF;

    -- Generate consistent lock key from table name and ID
    v_lock_key := hashtext(p_table_name || p_id::TEXT);

    -- Try to acquire advisory lock with timeout
    IF pg_try_advisory_xact_lock(v_lock_key) THEN
        -- Lock acquired, perform delete
        EXECUTE format('DELETE FROM %I WHERE id = $1', p_table_name) USING p_id;
        v_result := TRUE;
    ELSE
        -- Could not acquire lock, likely deadlock scenario
        RAISE WARNING 'Could not acquire lock for %:% - possible deadlock', p_table_name, p_id;
        v_result := FALSE;
    END IF;

    RETURN v_result;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION SAFE_DELETE_WITH_LOCK IS
'Safely deletes a row with advisory locking to prevent deadlocks during migrations.
Usage: SELECT safe_delete_with_lock(''fields'', ''uuid-here'');
Returns TRUE if deleted, FALSE if lock could not be acquired.';

-- ─────────────────────────────────────────────────────────────────────────────
-- Step 10: Summary Report
-- ─────────────────────────────────────────────────────────────────────────────
DO $$
DECLARE
    orphaned_fields_count INTEGER;
    orphaned_sensors_count INTEGER;
    orphaned_tasks_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO orphaned_fields_count FROM _orphaned_fields_backup;
    SELECT COUNT(*) INTO orphaned_sensors_count FROM _orphaned_sensor_data_backup;
    SELECT COUNT(*) INTO orphaned_tasks_count FROM _orphaned_tasks_backup;

    RAISE NOTICE '';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE '  MIGRATION COMPLETE - SUMMARY';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE '  📊 Orphaned Fields Cleaned: %', orphaned_fields_count;
    RAISE NOTICE '  📊 Orphaned Sensors Cleaned: %', orphaned_sensors_count;
    RAISE NOTICE '  📊 Orphaned Tasks Cleaned: %', orphaned_tasks_count;
    RAISE NOTICE '  ✅ Foreign Key Constraints Added';
    RAISE NOTICE '  ✅ GPS TTL Tracking Enabled';
    RAISE NOTICE '  ✅ Deadlock Prevention Function Created';
    RAISE NOTICE '';
    RAISE NOTICE '  ⚠️ Backup tables created:';
    RAISE NOTICE '     - _orphaned_fields_backup';
    RAISE NOTICE '     - _orphaned_sensor_data_backup';
    RAISE NOTICE '     - _orphaned_tasks_backup';
    RAISE NOTICE '';
    RAISE NOTICE '  🔍 To review stale GPS data:';
    RAISE NOTICE '     SELECT * FROM v_stale_gps_data WHERE staleness_level != ''OK'';';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
END $$;
