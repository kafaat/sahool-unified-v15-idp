-- ═══════════════════════════════════════════════════════════════════════════════
-- SAHOOL Platform - Base Tables Migration
-- الجداول الأساسية
-- ═══════════════════════════════════════════════════════════════════════════════

-- Skip if already applied
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM public._migrations WHERE name = '002_base_tables') THEN
        RAISE NOTICE 'Migration 002_base_tables already applied, skipping...';
        RETURN;
    END IF;

    -- Tenants table
    CREATE TABLE IF NOT EXISTS tenants.tenants (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        name VARCHAR(255) NOT NULL,
        name_ar VARCHAR(255),
        code VARCHAR(50) UNIQUE NOT NULL,
        status VARCHAR(20) DEFAULT 'active',
        settings JSONB DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Users table
    CREATE TABLE IF NOT EXISTS users.users (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tenant_id UUID REFERENCES tenants.tenants(id),
        email VARCHAR(255) UNIQUE NOT NULL,
        phone VARCHAR(50),
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(255),
        name_ar VARCHAR(255),
        role VARCHAR(50) DEFAULT 'user',
        is_active BOOLEAN DEFAULT true,
        last_login TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Farms table
    CREATE TABLE IF NOT EXISTS geo.farms (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        tenant_id UUID REFERENCES tenants.tenants(id),
        owner_id UUID REFERENCES users.users(id),
        name VARCHAR(255) NOT NULL,
        name_ar VARCHAR(255),
        governorate VARCHAR(100),
        district VARCHAR(100),
        area_hectares DECIMAL(10, 2),
        geometry GEOMETRY(MultiPolygon, 4326),
        center_point GEOMETRY(Point, 4326),
        status VARCHAR(20) DEFAULT 'active',
        health_score DECIMAL(5, 2),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Fields table
    CREATE TABLE IF NOT EXISTS geo.fields (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        farm_id UUID REFERENCES geo.farms(id) ON DELETE CASCADE,
        tenant_id UUID REFERENCES tenants.tenants(id),
        name VARCHAR(255) NOT NULL,
        name_ar VARCHAR(255),
        crop_type VARCHAR(100),
        area_hectares DECIMAL(10, 2),
        geometry GEOMETRY(Polygon, 4326),
        center_point GEOMETRY(Point, 4326),
        status VARCHAR(20) DEFAULT 'active',
        current_ndvi DECIMAL(4, 3),
        health_score DECIMAL(5, 2),
        last_satellite_update TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- Create spatial indexes
    CREATE INDEX IF NOT EXISTS idx_farms_geometry ON geo.farms USING GIST (geometry);
    CREATE INDEX IF NOT EXISTS idx_farms_center ON geo.farms USING GIST (center_point);
    CREATE INDEX IF NOT EXISTS idx_fields_geometry ON geo.fields USING GIST (geometry);
    CREATE INDEX IF NOT EXISTS idx_fields_center ON geo.fields USING GIST (center_point);

    -- Create regular indexes
    CREATE INDEX IF NOT EXISTS idx_farms_tenant ON geo.farms (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_farms_owner ON geo.farms (owner_id);
    CREATE INDEX IF NOT EXISTS idx_fields_farm ON geo.fields (farm_id);
    CREATE INDEX IF NOT EXISTS idx_users_tenant ON users.users (tenant_id);
    CREATE INDEX IF NOT EXISTS idx_users_email ON users.users (email);

    -- Record this migration
    INSERT INTO public._migrations (name) VALUES ('002_base_tables');

    RAISE NOTICE 'Migration 002_base_tables completed successfully';
END $$;
