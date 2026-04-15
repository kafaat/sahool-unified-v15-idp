-- Migration: Rename equipment.id to equipment.equipment_id
-- Fixes schema mismatch where database has 'id' column but model expects 'equipment_id'

-- Step 1: Check if 'id' column exists
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'equipment' AND column_name = 'id'
    ) THEN
        -- Step 2: Rename the column
        ALTER TABLE equipment RENAME COLUMN id TO equipment_id;
        
        -- Step 3: Convert UUID to String (VARCHAR)
        -- First, convert existing UUIDs to strings
        ALTER TABLE equipment ALTER COLUMN equipment_id TYPE VARCHAR(50) USING equipment_id::text;
        
        RAISE NOTICE '✅ Successfully renamed equipment.id to equipment.equipment_id';
    ELSE
        RAISE NOTICE 'ℹ️  Column id not found in equipment table, migration may already be applied';
    END IF;
END $$;

-- Verify the change
SELECT
    column_name,
    data_type,
    is_nullable
FROM information_schema.columns
WHERE table_name = 'equipment' AND column_name = 'equipment_id';
