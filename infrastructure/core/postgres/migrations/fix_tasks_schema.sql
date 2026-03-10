-- Fix tasks table schema to use task_id VARCHAR(50) instead of id UUID
-- This script fixes the schema mismatch between the init script and task-service models

-- Step 1: Drop all foreign key constraints that reference tasks table
DO $$
DECLARE
    r RECORD;
BEGIN
    FOR r IN (
        SELECT conname, conrelid::regclass AS table_name
        FROM pg_constraint
        WHERE confrelid = 'tasks'::regclass AND contype = 'f'
    ) LOOP
        EXECUTE format('ALTER TABLE %s DROP CONSTRAINT IF EXISTS %I', r.table_name, r.conname);
        RAISE NOTICE 'Dropped constraint % from %', r.conname, r.table_name;
    END LOOP;
END $$;

-- Step 2: Drop parent_task_id foreign key constraint
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_parent_task_id_fkey;

-- Step 3: Convert task_id from UUID to VARCHAR(50)
ALTER TABLE tasks ALTER COLUMN task_id TYPE VARCHAR(50) USING task_id::text;

-- Step 4: Convert parent_task_id from UUID to VARCHAR(50)
ALTER TABLE tasks ALTER COLUMN parent_task_id TYPE VARCHAR(50) USING parent_task_id::text;

-- Step 5: Recreate parent_task_id foreign key (NOT VALID to avoid full table scan)
ALTER TABLE tasks ADD CONSTRAINT tasks_parent_task_id_fkey
    FOREIGN KEY (parent_task_id) REFERENCES tasks(task_id) NOT VALID;
ALTER TABLE tasks VALIDATE CONSTRAINT tasks_parent_task_id_fkey;

-- Step 6: Recreate any other foreign keys that referenced tasks (if they exist)
-- Note: This will be handled by the services when they create their tables

-- Verification
SELECT 'Tasks table schema fixed!' AS status;
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'tasks' AND column_name LIKE '%task_id%'
ORDER BY ordinal_position;
