-- SAHOOL Field Core - Geospatial Indexes and Farm Support
-- Migration: Add advanced geospatial features and Farm table
-- Created: 2026-01-01

-- ═══════════════════════════════════════════════════════════════════════════
-- 1. Create Farms Table with Geospatial Support
-- ═══════════════════════════════════════════════════════════════════════════

CREATE TABLE farms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version INTEGER NOT NULL DEFAULT 1,

    -- Basic Info
    name VARCHAR(255) NOT NULL,
    tenant_id VARCHAR(100) NOT NULL,
    owner_id VARCHAR(100) NOT NULL,

    -- Geospatial (PostGIS)
    location geometry(Point, 4326),  -- Farm headquarters/main location
    boundary geometry(Polygon, 4326),  -- Farm boundary (optional)

    -- Calculated Fields
    total_area_hectares DECIMAL(10, 4),

    -- Contact & Address
    address VARCHAR(500),
    phone VARCHAR(50),
    email VARCHAR(255),

    -- Flexible Metadata
    metadata JSONB,

    -- Sync Metadata
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    server_updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    etag VARCHAR(64) DEFAULT uuid_generate_v4()::text,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for Farms
CREATE INDEX idx_farm_tenant ON farms(tenant_id);
CREATE INDEX idx_farm_owner ON farms(owner_id);
CREATE INDEX idx_farm_sync ON farms(server_updated_at);
CREATE INDEX idx_farms_location ON farms USING GIST(location);
CREATE INDEX idx_farms_boundary ON farms USING GIST(boundary);

-- Triggers for Farms
CREATE TRIGGER update_farms_updated_at
    BEFORE UPDATE ON farms
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_farms_server_updated_at
    BEFORE UPDATE ON farms
    FOR EACH ROW
    EXECUTE FUNCTION update_server_updated_at_column();

CREATE TRIGGER increment_farms_version
    BEFORE UPDATE ON farms
    FOR EACH ROW
    EXECUTE FUNCTION increment_version_column();

-- Auto-calculate farm area from boundary
CREATE OR REPLACE FUNCTION calculate_farm_area()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.boundary IS NOT NULL THEN
        -- Calculate area in hectares using ST_Area with geography cast
        NEW.total_area_hectares = ST_Area(NEW.boundary::geography) / 10000;
    END IF;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER calculate_farms_area
    BEFORE INSERT OR UPDATE OF boundary ON farms
    FOR EACH ROW
    EXECUTE FUNCTION calculate_farm_area();

-- ═══════════════════════════════════════════════════════════════════════════
-- 2. Add Farm Reference to Fields Table (Optional)
-- ═══════════════════════════════════════════════════════════════════════════

ALTER TABLE fields ADD COLUMN farm_id UUID REFERENCES farms(id) ON DELETE SET NULL;
CREATE INDEX idx_field_farm ON fields(farm_id);

-- ═══════════════════════════════════════════════════════════════════════════
-- 3. Create Geospatial Helper Functions
-- ═══════════════════════════════════════════════════════════════════════════

-- Function to find fields within a radius (in kilometers)
CREATE OR REPLACE FUNCTION find_fields_in_radius(
    p_lat DOUBLE PRECISION,
    p_lng DOUBLE PRECISION,
    p_radius_km DOUBLE PRECISION,
    p_tenant_id VARCHAR(100) DEFAULT NULL
)
RETURNS TABLE(
    field_id UUID,
    field_name VARCHAR(255),
    distance_km DOUBLE PRECISION,
    area_hectares DECIMAL(10, 4),
    crop_type VARCHAR(100),
    centroid_lat DOUBLE PRECISION,
    centroid_lng DOUBLE PRECISION
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.name,
        -- Calculate distance in kilometers using ST_Distance with geography
        ST_Distance(
            ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography,
            f.centroid::geography
        ) / 1000 AS distance_km,
        f.area_hectares,
        f.crop_type,
        ST_Y(f.centroid::geometry) AS centroid_lat,
        ST_X(f.centroid::geometry) AS centroid_lng
    FROM fields f
    WHERE
        f.is_deleted = FALSE
        AND f.centroid IS NOT NULL
        AND (p_tenant_id IS NULL OR f.tenant_id = p_tenant_id)
        -- Filter by radius using geography for accurate distance
        AND ST_DWithin(
            ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography,
            f.centroid::geography,
            p_radius_km * 1000  -- Convert km to meters
        )
    ORDER BY distance_km ASC;
END;
$$ LANGUAGE plpgsql;

-- Function to find nearby farms
CREATE OR REPLACE FUNCTION find_nearby_farms(
    p_lat DOUBLE PRECISION,
    p_lng DOUBLE PRECISION,
    p_limit INTEGER DEFAULT 10,
    p_tenant_id VARCHAR(100) DEFAULT NULL
)
RETURNS TABLE(
    farm_id UUID,
    farm_name VARCHAR(255),
    distance_km DOUBLE PRECISION,
    total_area_hectares DECIMAL(10, 4),
    location_lat DOUBLE PRECISION,
    location_lng DOUBLE PRECISION,
    phone VARCHAR(50),
    email VARCHAR(255)
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        fm.id,
        fm.name,
        -- Calculate distance in kilometers
        ST_Distance(
            ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)::geography,
            fm.location::geography
        ) / 1000 AS distance_km,
        fm.total_area_hectares,
        ST_Y(fm.location::geometry) AS location_lat,
        ST_X(fm.location::geometry) AS location_lng,
        fm.phone,
        fm.email
    FROM farms fm
    WHERE
        fm.is_deleted = FALSE
        AND fm.location IS NOT NULL
        AND (p_tenant_id IS NULL OR fm.tenant_id = p_tenant_id)
    ORDER BY distance_km ASC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql;

-- Function to calculate field area by ID
CREATE OR REPLACE FUNCTION get_field_area(
    p_field_id UUID
)
RETURNS DECIMAL(10, 4) AS $$
DECLARE
    v_area DECIMAL(10, 4);
BEGIN
    SELECT
        CASE
            WHEN boundary IS NOT NULL THEN
                ST_Area(boundary::geography) / 10000
            ELSE
                area_hectares
        END
    INTO v_area
    FROM fields
    WHERE id = p_field_id;

    RETURN v_area;
END;
$$ LANGUAGE plpgsql;

-- Function to check if a point is within a field boundary
CREATE OR REPLACE FUNCTION check_point_in_field(
    p_lat DOUBLE PRECISION,
    p_lng DOUBLE PRECISION,
    p_field_id UUID
)
RETURNS BOOLEAN AS $$
DECLARE
    v_is_inside BOOLEAN;
BEGIN
    SELECT
        ST_Contains(
            boundary,
            ST_SetSRID(ST_MakePoint(p_lng, p_lat), 4326)
        )
    INTO v_is_inside
    FROM fields
    WHERE id = p_field_id
        AND boundary IS NOT NULL;

    RETURN COALESCE(v_is_inside, FALSE);
END;
$$ LANGUAGE plpgsql;

-- Function to get fields within a bounding box
CREATE OR REPLACE FUNCTION find_fields_in_bbox(
    p_min_lat DOUBLE PRECISION,
    p_min_lng DOUBLE PRECISION,
    p_max_lat DOUBLE PRECISION,
    p_max_lng DOUBLE PRECISION,
    p_tenant_id VARCHAR(100) DEFAULT NULL
)
RETURNS TABLE(
    field_id UUID,
    field_name VARCHAR(255),
    area_hectares DECIMAL(10, 4),
    crop_type VARCHAR(100),
    boundary_geojson JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        f.id,
        f.name,
        f.area_hectares,
        f.crop_type,
        ST_AsGeoJSON(f.boundary)::jsonb
    FROM fields f
    WHERE
        f.is_deleted = FALSE
        AND f.boundary IS NOT NULL
        AND (p_tenant_id IS NULL OR f.tenant_id = p_tenant_id)
        -- Check if field intersects with bounding box
        AND ST_Intersects(
            f.boundary,
            ST_MakeEnvelope(p_min_lng, p_min_lat, p_max_lng, p_max_lat, 4326)
        );
END;
$$ LANGUAGE plpgsql;

-- Function to calculate distance between two fields
CREATE OR REPLACE FUNCTION calculate_fields_distance(
    p_field_id_1 UUID,
    p_field_id_2 UUID
)
RETURNS DOUBLE PRECISION AS $$
DECLARE
    v_distance DOUBLE PRECISION;
BEGIN
    SELECT
        ST_Distance(f1.centroid::geography, f2.centroid::geography) / 1000
    INTO v_distance
    FROM fields f1, fields f2
    WHERE f1.id = p_field_id_1
        AND f2.id = p_field_id_2
        AND f1.centroid IS NOT NULL
        AND f2.centroid IS NOT NULL;

    RETURN v_distance;
END;
$$ LANGUAGE plpgsql;

-- Function to get field statistics by region (using bounding box)
CREATE OR REPLACE FUNCTION get_region_field_stats(
    p_min_lat DOUBLE PRECISION,
    p_min_lng DOUBLE PRECISION,
    p_max_lat DOUBLE PRECISION,
    p_max_lng DOUBLE PRECISION,
    p_tenant_id VARCHAR(100) DEFAULT NULL
)
RETURNS TABLE(
    total_fields BIGINT,
    total_area_ha DECIMAL(15, 4),
    avg_field_size_ha DECIMAL(10, 4),
    crop_distribution JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT,
        SUM(f.area_hectares)::DECIMAL(15, 4),
        AVG(f.area_hectares)::DECIMAL(10, 4),
        jsonb_object_agg(f.crop_type, crop_count) AS crop_distribution
    FROM (
        SELECT
            f.area_hectares,
            f.crop_type,
            COUNT(*) as crop_count
        FROM fields f
        WHERE
            f.is_deleted = FALSE
            AND f.boundary IS NOT NULL
            AND (p_tenant_id IS NULL OR f.tenant_id = p_tenant_id)
            AND ST_Intersects(
                f.boundary,
                ST_MakeEnvelope(p_min_lng, p_min_lat, p_max_lng, p_max_lat, 4326)
            )
        GROUP BY f.crop_type, f.area_hectares
    ) f;
END;
$$ LANGUAGE plpgsql;

-- ═══════════════════════════════════════════════════════════════════════════
-- 4. Create Additional Views for Geospatial Queries
-- ═══════════════════════════════════════════════════════════════════════════

-- View for farms with GeoJSON
CREATE VIEW farms_geojson AS
SELECT
    id,
    version,
    name,
    tenant_id,
    owner_id,
    ST_AsGeoJSON(location)::jsonb as location_geojson,
    ST_AsGeoJSON(boundary)::jsonb as boundary_geojson,
    total_area_hectares,
    address,
    phone,
    email,
    metadata,
    is_deleted,
    server_updated_at,
    etag,
    created_at,
    updated_at
FROM farms
WHERE is_deleted = FALSE;

-- View for fields with farm info
CREATE VIEW fields_with_farm AS
SELECT
    f.id as field_id,
    f.name as field_name,
    f.crop_type,
    f.area_hectares,
    f.status,
    ST_AsGeoJSON(f.boundary)::jsonb as field_boundary_geojson,
    ST_AsGeoJSON(f.centroid)::jsonb as field_centroid_geojson,
    fm.id as farm_id,
    fm.name as farm_name,
    fm.owner_id,
    ST_AsGeoJSON(fm.location)::jsonb as farm_location_geojson,
    f.tenant_id,
    f.created_at,
    f.updated_at
FROM fields f
LEFT JOIN farms fm ON f.farm_id = fm.id
WHERE f.is_deleted = FALSE;

-- ═══════════════════════════════════════════════════════════════════════════
-- 5. Add Comments for Documentation
-- ═══════════════════════════════════════════════════════════════════════════

COMMENT ON TABLE farms IS 'Farm locations and boundaries with PostGIS geometry support';
COMMENT ON COLUMN farms.location IS 'Farm headquarters location as PostGIS Point (lat/lng)';
COMMENT ON COLUMN farms.boundary IS 'Farm boundary as PostGIS Polygon';

COMMENT ON FUNCTION find_fields_in_radius IS 'Find all fields within a radius (km) from a point';
COMMENT ON FUNCTION find_nearby_farms IS 'Find nearest farms from a given location';
COMMENT ON FUNCTION get_field_area IS 'Calculate field area in hectares from boundary geometry';
COMMENT ON FUNCTION check_point_in_field IS 'Check if a lat/lng point is inside a field boundary';
COMMENT ON FUNCTION find_fields_in_bbox IS 'Find all fields within a bounding box';
COMMENT ON FUNCTION calculate_fields_distance IS 'Calculate distance in km between two fields';
COMMENT ON FUNCTION get_region_field_stats IS 'Get agricultural statistics for a region';
