"""Add PostGIS Support - Spatial Data Capabilities
إضافة دعم PostGIS - قدرات البيانات المكانية

Enables PostGIS extension and adds spatial columns for:
- Field boundaries (حدود الحقول)
- Field locations (مواقع الحقول)
- Sensor locations (مواقع أجهزة الاستشعار)

Revision ID: 002
Revises: 001
Create Date: 2026-01-02
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text
from sqlalchemy.dialects import postgresql

# معرفات المراجعة، تستخدم بواسطة Alembic
# Revision identifiers, used by Alembic
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    ترقية قاعدة البيانات - إضافة دعم PostGIS
    Upgrade database - Add PostGIS support
    """

    # الحصول على الاتصال
    # Get connection
    conn = op.get_bind()

    # =========================================================================
    # تمكين امتدادات PostGIS / Enable PostGIS Extensions
    # =========================================================================
    print("Enabling PostGIS extensions...")
    print("تمكين امتدادات PostGIS...")

    # تمكين PostGIS الأساسي / Enable core PostGIS
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))

    # تمكين PostGIS Topology (اختياري) / Enable PostGIS Topology (optional)
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_topology"))

    # تمكين PostGIS Raster (اختياري) / Enable PostGIS Raster (optional)
    # conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis_raster"))

    conn.commit()

    # =========================================================================
    # إضافة أعمدة مكانية لجدول الحقول / Add Spatial Columns to Fields Table
    # =========================================================================
    print("Adding spatial columns to fields table...")
    print("إضافة أعمدة مكانية لجدول الحقول...")

    # إضافة عمود الموقع (نقطة المركز)
    # Add location column (center point)
    conn.execute(text(
        """
        SELECT AddGeometryColumn(
            'fields',        -- table_name
            'location',      -- column_name
            4326,            -- srid (WGS84)
            'POINT',         -- type
            2                -- dimension
        )
        """
    ))

    # إضافة عمود الحدود (مضلع)
    # Add boundary column (polygon)
    conn.execute(text(
        """
        SELECT AddGeometryColumn(
            'fields',        -- table_name
            'boundary',      -- column_name
            4326,            -- srid (WGS84)
            'POLYGON',       -- type
            2                -- dimension
        )
        """
    ))

    conn.commit()

    # إنشاء فهارس مكانية للحقول / Create spatial indexes for fields
    print("Creating spatial indexes for fields...")
    print("إنشاء فهارس مكانية للحقول...")

    conn.execute(text(
        """
        CREATE INDEX idx_fields_location_gist
        ON fields USING GIST (location)
        """
    ))

    conn.execute(text(
        """
        CREATE INDEX idx_fields_boundary_gist
        ON fields USING GIST (boundary)
        """
    ))

    conn.commit()

    # =========================================================================
    # إضافة أعمدة مكانية لجدول أجهزة الاستشعار / Add Spatial Columns to Sensors Table
    # =========================================================================
    print("Adding spatial columns to sensors table...")
    print("إضافة أعمدة مكانية لجدول أجهزة الاستشعار...")

    # إضافة عمود الموقع للاستشعار
    # Add location column for sensors
    conn.execute(text(
        """
        SELECT AddGeometryColumn(
            'sensors',       -- table_name
            'location',      -- column_name
            4326,            -- srid (WGS84)
            'POINT',         -- type
            2                -- dimension
        )
        """
    ))

    conn.commit()

    # إنشاء فهرس مكاني لأجهزة الاستشعار / Create spatial index for sensors
    print("Creating spatial index for sensors...")
    print("إنشاء فهرس مكاني لأجهزة الاستشعار...")

    conn.execute(text(
        """
        CREATE INDEX idx_sensors_location_gist
        ON sensors USING GIST (location)
        """
    ))

    conn.commit()

    # =========================================================================
    # ترحيل البيانات الموجودة / Migrate Existing Data
    # =========================================================================
    print("Migrating existing location data...")
    print("ترحيل بيانات الموقع الموجودة...")

    # تحديث مواقع الحقول من center_latitude/center_longitude
    # Update field locations from center_latitude/center_longitude
    conn.execute(text(
        """
        UPDATE fields
        SET location = ST_SetSRID(
            ST_MakePoint(center_longitude, center_latitude),
            4326
        )
        WHERE center_latitude IS NOT NULL
        AND center_longitude IS NOT NULL
        """
    ))

    # تحديث حدود الحقول من boundary_geojson
    # Update field boundaries from boundary_geojson
    conn.execute(text(
        """
        UPDATE fields
        SET boundary = ST_SetSRID(
            ST_GeomFromGeoJSON(boundary_geojson::text),
            4326
        )
        WHERE boundary_geojson IS NOT NULL
        """
    ))

    # تحديث مواقع أجهزة الاستشعار من latitude/longitude
    # Update sensor locations from latitude/longitude
    conn.execute(text(
        """
        UPDATE sensors
        SET location = ST_SetSRID(
            ST_MakePoint(longitude, latitude),
            4326
        )
        WHERE latitude IS NOT NULL
        AND longitude IS NOT NULL
        """
    ))

    conn.commit()

    # =========================================================================
    # إضافة دوال مساعدة PostGIS / Add PostGIS Helper Functions
    # =========================================================================
    print("Creating helper functions...")
    print("إنشاء دوال مساعدة...")

    # دالة لحساب مساحة الحقل بالهكتار
    # Function to calculate field area in hectares
    conn.execute(text(
        """
        CREATE OR REPLACE FUNCTION calculate_field_area_hectares(boundary_geom geometry)
        RETURNS FLOAT AS $$
        BEGIN
            -- حساب المساحة بالمتر المربع ثم تحويلها إلى هكتار
            -- Calculate area in square meters then convert to hectares
            RETURN ST_Area(boundary_geom::geography) / 10000.0;
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
        """
    ))

    # دالة لحساب المركز من الحدود
    # Function to calculate center from boundary
    conn.execute(text(
        """
        CREATE OR REPLACE FUNCTION calculate_field_center(boundary_geom geometry)
        RETURNS geometry AS $$
        BEGIN
            -- حساب نقطة المركز من المضلع
            -- Calculate center point from polygon
            RETURN ST_Centroid(boundary_geom);
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
        """
    ))

    # دالة لحساب المسافة بين نقطتين بالمتر
    # Function to calculate distance between two points in meters
    conn.execute(text(
        """
        CREATE OR REPLACE FUNCTION calculate_distance_meters(
            point1 geometry,
            point2 geometry
        )
        RETURNS FLOAT AS $$
        BEGIN
            -- حساب المسافة بالمتر
            -- Calculate distance in meters
            RETURN ST_Distance(point1::geography, point2::geography);
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
        """
    ))

    # دالة للتحقق مما إذا كانت نقطة داخل مضلع
    # Function to check if point is within polygon
    conn.execute(text(
        """
        CREATE OR REPLACE FUNCTION is_point_in_field(
            point_geom geometry,
            field_boundary geometry
        )
        RETURNS BOOLEAN AS $$
        BEGIN
            -- التحقق مما إذا كانت النقطة داخل الحدود
            -- Check if point is within boundary
            RETURN ST_Within(point_geom, field_boundary);
        END;
        $$ LANGUAGE plpgsql IMMUTABLE;
        """
    ))

    # دالة للعثور على الحقول القريبة
    # Function to find nearby fields
    conn.execute(text(
        """
        CREATE OR REPLACE FUNCTION find_nearby_fields(
            reference_location geometry,
            radius_meters FLOAT
        )
        RETURNS TABLE(field_id UUID, distance_meters FLOAT) AS $$
        BEGIN
            RETURN QUERY
            SELECT
                id,
                ST_Distance(location::geography, reference_location::geography) as dist
            FROM fields
            WHERE location IS NOT NULL
            AND ST_DWithin(
                location::geography,
                reference_location::geography,
                radius_meters
            )
            ORDER BY dist;
        END;
        $$ LANGUAGE plpgsql STABLE;
        """
    ))

    conn.commit()

    # =========================================================================
    # إضافة قيود التحقق / Add Check Constraints
    # =========================================================================
    print("Adding validation constraints...")
    print("إضافة قيود التحقق...")

    # التأكد من أن الحدود صالحة
    # Ensure boundaries are valid
    conn.execute(text(
        """
        ALTER TABLE fields
        ADD CONSTRAINT chk_fields_boundary_valid
        CHECK (boundary IS NULL OR ST_IsValid(boundary))
        """
    ))

    # التأكد من أن المواقع صالحة
    # Ensure locations are valid
    conn.execute(text(
        """
        ALTER TABLE fields
        ADD CONSTRAINT chk_fields_location_valid
        CHECK (location IS NULL OR ST_IsValid(location))
        """
    ))

    conn.execute(text(
        """
        ALTER TABLE sensors
        ADD CONSTRAINT chk_sensors_location_valid
        CHECK (location IS NULL OR ST_IsValid(location))
        """
    ))

    conn.commit()

    # =========================================================================
    # إنشاء عرض للبيانات المكانية / Create Spatial Data View
    # =========================================================================
    print("Creating spatial data views...")
    print("إنشاء عروض البيانات المكانية...")

    conn.execute(text(
        """
        CREATE OR REPLACE VIEW field_spatial_info AS
        SELECT
            f.id,
            f.tenant_id,
            f.farm_id,
            f.name,
            f.name_ar,
            f.area_hectares,
            -- الموقع بصيغة GeoJSON / Location as GeoJSON
            ST_AsGeoJSON(f.location)::jsonb as location_geojson,
            -- الحدود بصيغة GeoJSON / Boundary as GeoJSON
            ST_AsGeoJSON(f.boundary)::jsonb as boundary_geojson,
            -- الإحداثيات / Coordinates
            ST_X(f.location) as longitude,
            ST_Y(f.location) as latitude,
            -- المساحة المحسوبة / Calculated area
            CASE
                WHEN f.boundary IS NOT NULL THEN
                    ST_Area(f.boundary::geography) / 10000.0
                ELSE NULL
            END as calculated_area_hectares,
            -- محيط الحدود بالمتر / Perimeter in meters
            CASE
                WHEN f.boundary IS NOT NULL THEN
                    ST_Perimeter(f.boundary::geography)
                ELSE NULL
            END as perimeter_meters
        FROM fields f
        """
    ))

    conn.commit()

    print("PostGIS migration completed successfully!")
    print("اكتملت هجرة PostGIS بنجاح!")


def downgrade() -> None:
    """
    التراجع عن الترقية - إزالة دعم PostGIS
    Downgrade database - Remove PostGIS support
    """

    # الحصول على الاتصال
    # Get connection
    conn = op.get_bind()

    print("Removing PostGIS support...")
    print("إزالة دعم PostGIS...")

    # =========================================================================
    # إزالة العرض / Drop View
    # =========================================================================
    conn.execute(text("DROP VIEW IF EXISTS field_spatial_info"))

    # =========================================================================
    # إزالة القيود / Drop Constraints
    # =========================================================================
    conn.execute(text(
        "ALTER TABLE fields DROP CONSTRAINT IF EXISTS chk_fields_boundary_valid"
    ))
    conn.execute(text(
        "ALTER TABLE fields DROP CONSTRAINT IF EXISTS chk_fields_location_valid"
    ))
    conn.execute(text(
        "ALTER TABLE sensors DROP CONSTRAINT IF EXISTS chk_sensors_location_valid"
    ))

    # =========================================================================
    # إزالة الدوال المساعدة / Drop Helper Functions
    # =========================================================================
    conn.execute(text("DROP FUNCTION IF EXISTS calculate_field_area_hectares"))
    conn.execute(text("DROP FUNCTION IF EXISTS calculate_field_center"))
    conn.execute(text("DROP FUNCTION IF EXISTS calculate_distance_meters"))
    conn.execute(text("DROP FUNCTION IF EXISTS is_point_in_field"))
    conn.execute(text("DROP FUNCTION IF EXISTS find_nearby_fields"))

    # =========================================================================
    # إزالة الفهارس المكانية / Drop Spatial Indexes
    # =========================================================================
    conn.execute(text("DROP INDEX IF EXISTS idx_fields_location_gist"))
    conn.execute(text("DROP INDEX IF EXISTS idx_fields_boundary_gist"))
    conn.execute(text("DROP INDEX IF EXISTS idx_sensors_location_gist"))

    # =========================================================================
    # إزالة الأعمدة المكانية / Drop Spatial Columns
    # =========================================================================
    # من جدول الحقول / From fields table
    conn.execute(text(
        "SELECT DropGeometryColumn('fields', 'location')"
    ))
    conn.execute(text(
        "SELECT DropGeometryColumn('fields', 'boundary')"
    ))

    # من جدول أجهزة الاستشعار / From sensors table
    conn.execute(text(
        "SELECT DropGeometryColumn('sensors', 'location')"
    ))

    conn.commit()

    # =========================================================================
    # إزالة امتدادات PostGIS / Drop PostGIS Extensions
    # =========================================================================
    # ملاحظة: لا نزيل الامتدادات لأنها قد تكون مستخدمة في أماكن أخرى
    # Note: We don't drop extensions as they might be used elsewhere
    # conn.execute(text("DROP EXTENSION IF EXISTS postgis_topology"))
    # conn.execute(text("DROP EXTENSION IF EXISTS postgis"))

    print("PostGIS support removed successfully!")
    print("تمت إزالة دعم PostGIS بنجاح!")
