-- Migration: Fix Equipment Table
-- إصلاح جدول المعدات
-- Adds equipment_id column if missing

-- Add equipment_id column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'equipment' AND column_name = 'equipment_id'
    ) THEN
        ALTER TABLE equipment ADD COLUMN equipment_id VARCHAR(50);
        -- Copy id to equipment_id for existing records
        UPDATE equipment SET equipment_id = id WHERE equipment_id IS NULL;
        RAISE NOTICE 'Added equipment_id column to equipment table';
    ELSE
        RAISE NOTICE 'equipment_id column already exists';
    END IF;
END $$;

SELECT 'Equipment table fix completed!' AS status;
