-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - Additional Improvements Migration
-- التحسينات الإضافية
-- Version: V20260105_002
-- Description: Complete remaining improvements from GAPS_AND_RECOMMENDATIONS.md
-- Priority: High (Phase 2 & 3)
-- ═══════════════════════════════════════════════════════════════════════════════

-- ═══════════════════════════════════════════════════════════════════════════════
-- 1. Foreign Key Constraints for Data Integrity
-- قيود المفاتيح الأجنبية لضمان سلامة البيانات
-- Priority: HIGH - Ensures referential integrity
-- ═══════════════════════════════════════════════════════════════════════════════

-- Add foreign keys for inventory_items (if table exists)
DO $$
BEGIN
    -- Check if inventory_items table exists
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'inventory_items'
    ) THEN
        
        -- Add FK to suppliers (if suppliers table exists and FK doesn't exist)
        IF EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'suppliers'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'fk_inventory_items_supplier'
        ) THEN
            -- Add constraint only if supplier_id column exists
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'inventory_items' 
                AND column_name = 'supplier_id'
            ) THEN
                ALTER TABLE inventory_items 
                ADD CONSTRAINT fk_inventory_items_supplier 
                FOREIGN KEY (supplier_id) 
                REFERENCES suppliers(id) 
                ON DELETE SET NULL;
                
                RAISE NOTICE '✅ Added FK: inventory_items -> suppliers';
            END IF;
        END IF;
        
        -- Add FK to inventory_warehouses (if table exists)
        IF EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'inventory_warehouses'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'fk_inventory_items_warehouse'
        ) THEN
            -- Add constraint only if warehouse_id column exists
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'inventory_items' 
                AND column_name = 'warehouse_id'
            ) THEN
                ALTER TABLE inventory_items 
                ADD CONSTRAINT fk_inventory_items_warehouse 
                FOREIGN KEY (warehouse_id) 
                REFERENCES inventory_warehouses(id) 
                ON DELETE RESTRICT;
                
                RAISE NOTICE '✅ Added FK: inventory_items -> inventory_warehouses';
            END IF;
        END IF;
        
        -- Add FK to inventory_categories (if table exists)
        IF EXISTS (
            SELECT 1 FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'inventory_categories'
        ) AND NOT EXISTS (
            SELECT 1 FROM information_schema.table_constraints 
            WHERE constraint_name = 'fk_inventory_items_category'
        ) THEN
            -- Add constraint only if category_id column exists
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'inventory_items' 
                AND column_name = 'category_id'
            ) THEN
                ALTER TABLE inventory_items 
                ADD CONSTRAINT fk_inventory_items_category 
                FOREIGN KEY (category_id) 
                REFERENCES inventory_categories(id) 
                ON DELETE SET NULL;
                
                RAISE NOTICE '✅ Added FK: inventory_items -> inventory_categories';
            END IF;
        END IF;
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- 2. Composite Indexes for High-Performance Queries
-- الفهارس المركبة للاستعلامات عالية الأداء
-- Priority: HIGH - Dramatically improves query performance
-- ═══════════════════════════════════════════════════════════════════════════════

-- Add composite index on sensor_readings (tenant_id, timestamp DESC)
-- Optimizes time-series queries for sensor data
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'sensor_readings'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'sensor_readings' 
        AND column_name = 'tenant_id'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'sensor_readings' 
        AND column_name = 'timestamp'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_tenant_time 
        ON sensor_readings(tenant_id, timestamp DESC);
        
        COMMENT ON INDEX idx_sensor_readings_tenant_time IS 
        'Composite index for efficient time-series queries by tenant';
        
        RAISE NOTICE '✅ Added composite index: sensor_readings(tenant_id, timestamp)';
    END IF;
END $$;

-- Add composite index on sensors (tenant_id, is_active)
-- Optimizes queries for active sensors by tenant
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'sensors'
    ) THEN
        -- Check if we have the necessary columns
        IF EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_schema = 'public' 
            AND table_name = 'sensors' 
            AND column_name = 'tenant_id'
        ) THEN
            -- Create partial index for active sensors if is_active column exists
            IF EXISTS (
                SELECT 1 FROM information_schema.columns 
                WHERE table_schema = 'public' 
                AND table_name = 'sensors' 
                AND column_name = 'is_active'
            ) THEN
                -- Partial index optimized for active sensor queries
                CREATE INDEX IF NOT EXISTS idx_sensors_tenant_active 
                ON sensors(tenant_id, is_active) 
                WHERE is_active = true;
                
                COMMENT ON INDEX idx_sensors_tenant_active IS 
                'Partial composite index for active sensors by tenant - optimizes WHERE tenant_id = ? AND is_active = true queries';
                
                RAISE NOTICE '✅ Added partial composite index: sensors(tenant_id, is_active) WHERE is_active = true';
            END IF;
        END IF;
    END IF;
END $$;

-- Add composite index on devices (tenant_id, status, last_seen)
-- Optimizes queries for device status monitoring
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'devices'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'devices' 
        AND column_name = 'tenant_id'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'devices' 
        AND column_name = 'status'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_devices_tenant_status 
        ON devices(tenant_id, status);
        
        COMMENT ON INDEX idx_devices_tenant_status IS 
        'Composite index for device status queries by tenant';
        
        RAISE NOTICE '✅ Added composite index: devices(tenant_id, status)';
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- 3. Additional GIN Indexes for JSONB Metadata
-- فهارس GIN إضافية لبيانات JSONB
-- Priority: MEDIUM - Improves metadata search performance
-- ═══════════════════════════════════════════════════════════════════════════════

-- Add GIN index for sensors metadata
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'sensors'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'sensors' 
        AND column_name = 'metadata'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_sensors_metadata_gin 
        ON sensors USING GIN (metadata);
        
        COMMENT ON INDEX idx_sensors_metadata_gin IS 
        'GIN index for sensors metadata JSONB queries';
        
        RAISE NOTICE '✅ Added GIN index: sensors.metadata';
    END IF;
END $$;

-- Add GIN index for devices metadata
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'devices'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'devices' 
        AND column_name = 'metadata'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_devices_metadata_gin 
        ON devices USING GIN (metadata);
        
        COMMENT ON INDEX idx_devices_metadata_gin IS 
        'GIN index for devices metadata JSONB queries';
        
        RAISE NOTICE '✅ Added GIN index: devices.metadata';
    END IF;
END $$;

-- Add GIN index for sensor_readings metadata
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'sensor_readings'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'sensor_readings' 
        AND column_name = 'metadata'
    ) THEN
        CREATE INDEX IF NOT EXISTS idx_sensor_readings_metadata_gin 
        ON sensor_readings USING GIN (metadata);
        
        COMMENT ON INDEX idx_sensor_readings_metadata_gin IS 
        'GIN index for sensor_readings metadata JSONB queries';
        
        RAISE NOTICE '✅ Added GIN index: sensor_readings.metadata';
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- 4. Performance Indexes for Common Query Patterns
-- فهارس الأداء لأنماط الاستعلامات الشائعة
-- Priority: MEDIUM - Optimizes frequently used queries
-- ═══════════════════════════════════════════════════════════════════════════════

-- Add index on inventory_items for low stock alerts
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'inventory_items'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'inventory_items' 
        AND column_name = 'current_quantity'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'inventory_items' 
        AND column_name = 'reorder_level'
    ) THEN
        -- Partial index for items below reorder level
        CREATE INDEX IF NOT EXISTS idx_inventory_items_low_stock 
        ON inventory_items(current_quantity, reorder_level) 
        WHERE current_quantity < reorder_level;
        
        COMMENT ON INDEX idx_inventory_items_low_stock IS 
        'Partial index for low stock alerts';
        
        RAISE NOTICE '✅ Added partial index: inventory_items low stock';
    END IF;
END $$;

-- Add index on inventory_items for expiry tracking
DO $$
BEGIN
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = 'inventory_items'
    ) AND EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'public' 
        AND table_name = 'inventory_items' 
        AND column_name = 'expiry_date'
    ) THEN
        -- Partial index for items with expiry dates
        CREATE INDEX IF NOT EXISTS idx_inventory_items_expiry 
        ON inventory_items(expiry_date) 
        WHERE expiry_date IS NOT NULL;
        
        COMMENT ON INDEX idx_inventory_items_expiry IS 
        'Partial index for expiry date tracking';
        
        RAISE NOTICE '✅ Added partial index: inventory_items expiry_date';
    END IF;
END $$;

-- ═══════════════════════════════════════════════════════════════════════════════
-- 5. Log Migration Completion
-- ═══════════════════════════════════════════════════════════════════════════════

DO $$
BEGIN
    -- Record migration if _migrations table exists
    IF EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name = '_migrations'
    ) THEN
        INSERT INTO public._migrations (name, applied_at) 
        VALUES ('V20260105__add_additional_improvements', CURRENT_TIMESTAMP)
        ON CONFLICT (name) DO NOTHING;
    END IF;
    
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE '✅ Migration V20260105__add_additional_improvements completed!';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
    RAISE NOTICE 'Summary of improvements:';
    RAISE NOTICE '  1. Foreign key constraints for data integrity';
    RAISE NOTICE '  2. Composite indexes for high-performance queries';
    RAISE NOTICE '  3. GIN indexes for JSONB metadata searches';
    RAISE NOTICE '  4. Partial indexes for common query patterns';
    RAISE NOTICE '═══════════════════════════════════════════════════════════════';
END $$;
