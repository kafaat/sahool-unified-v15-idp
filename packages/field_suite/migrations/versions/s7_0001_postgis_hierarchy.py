"""
Sprint 7: PostGIS hierarchy - Farm→Field→Zone→SubZone

This migration:
1. Enables PostGIS extension
2. Creates farms, fields, zones, sub_zones tables
3. Adds native PostGIS geometry columns (geom)
4. Creates GIST spatial indexes for efficient queries

Revision ID: s7_0001
Revises: None
Create Date: 2024-01-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = "s7_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # Enable PostGIS extension
    # -------------------------------------------------------------------------
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")

    # -------------------------------------------------------------------------
    # Create farms table
    # -------------------------------------------------------------------------
    op.create_table(
        "farms",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("name_ar", sa.String(length=140), nullable=True),
        sa.Column("latitude", sa.Float(), nullable=True),
        sa.Column("longitude", sa.Float(), nullable=True),
        sa.Column("total_area_hectares", sa.Float(), nullable=True),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index("ix_farms_tenant", "farms", ["tenant_id"])
    op.create_index("ix_farms_owner", "farms", ["owner_id"])

    # -------------------------------------------------------------------------
    # Create fields table with PostGIS geometry
    # -------------------------------------------------------------------------
    op.create_table(
        "fields",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("farm_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("name_ar", sa.String(length=140), nullable=True),
        sa.Column("geometry_wkt", sa.Text(), nullable=False),
        sa.Column("center_latitude", sa.Float(), nullable=True),
        sa.Column("center_longitude", sa.Float(), nullable=True),
        sa.Column("area_hectares", sa.Float(), nullable=False),
        sa.Column("soil_type", sa.String(length=40), nullable=True),
        sa.Column("irrigation_type", sa.String(length=40), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("current_crop_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_foreign_key(
        "fk_fields_farm",
        "fields",
        "farms",
        ["farm_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_fields_tenant", "fields", ["tenant_id"])
    op.create_index("ix_fields_farm", "fields", ["farm_id"])

    # Add PostGIS geometry column
    op.execute(
        """
        ALTER TABLE fields
        ADD COLUMN geom geometry(Polygon, 4326);
    """
    )

    # Create GIST spatial index
    op.execute("CREATE INDEX ix_fields_geom ON fields USING GIST (geom);")

    # -------------------------------------------------------------------------
    # Create zones table with PostGIS geometry
    # -------------------------------------------------------------------------
    op.create_table(
        "zones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("name_ar", sa.String(length=140), nullable=True),
        sa.Column(
            "zone_type",
            sa.String(length=40),
            nullable=False,
            server_default="management",
        ),
        sa.Column("geometry_wkt", sa.Text(), nullable=False),
        sa.Column("center_latitude", sa.Float(), nullable=True),
        sa.Column("center_longitude", sa.Float(), nullable=True),
        sa.Column("area_hectares", sa.Float(), nullable=False),
        sa.Column("properties", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_foreign_key(
        "fk_zones_field",
        "zones",
        "fields",
        ["field_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_zones_tenant", "zones", ["tenant_id"])
    op.create_index("ix_zones_field", "zones", ["field_id"])
    op.create_index("ix_zones_type", "zones", ["zone_type"])

    # Add PostGIS geometry column
    op.execute(
        """
        ALTER TABLE zones
        ADD COLUMN geom geometry(Polygon, 4326);
    """
    )

    # Create GIST spatial index
    op.execute("CREATE INDEX ix_zones_geom ON zones USING GIST (geom);")

    # -------------------------------------------------------------------------
    # Create sub_zones table with PostGIS geometry
    # -------------------------------------------------------------------------
    op.create_table(
        "sub_zones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("zone_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=140), nullable=False),
        sa.Column("name_ar", sa.String(length=140), nullable=True),
        sa.Column("geometry_wkt", sa.Text(), nullable=False),
        sa.Column("center_latitude", sa.Float(), nullable=True),
        sa.Column("center_longitude", sa.Float(), nullable=True),
        sa.Column("area_hectares", sa.Float(), nullable=False),
        sa.Column("properties", postgresql.JSONB(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_foreign_key(
        "fk_subzones_zone",
        "sub_zones",
        "zones",
        ["zone_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_subzones_tenant", "sub_zones", ["tenant_id"])
    op.create_index("ix_subzones_zone", "sub_zones", ["zone_id"])

    # Add PostGIS geometry column
    op.execute(
        """
        ALTER TABLE sub_zones
        ADD COLUMN geom geometry(Polygon, 4326);
    """
    )

    # Create GIST spatial index
    op.execute("CREATE INDEX ix_subzones_geom ON sub_zones USING GIST (geom);")

    # -------------------------------------------------------------------------
    # Create trigger to auto-sync geometry_wkt → geom on INSERT/UPDATE
    # -------------------------------------------------------------------------
    op.execute(
        """
        CREATE OR REPLACE FUNCTION sync_geometry_from_wkt()
        RETURNS TRIGGER AS $$
        BEGIN
            IF NEW.geometry_wkt IS NOT NULL AND (OLD IS NULL OR OLD.geometry_wkt != NEW.geometry_wkt) THEN
                NEW.geom := ST_GeomFromText(NEW.geometry_wkt, 4326);
            END IF;
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    )

    # Apply trigger to all spatial tables
    # Use explicit statements for each table to avoid SQL injection concerns
    # (Table names are known at compile time, but explicit statements are safer)
    op.execute(
        """
        CREATE TRIGGER trg_fields_sync_geom
        BEFORE INSERT OR UPDATE ON fields
        FOR EACH ROW
        EXECUTE FUNCTION sync_geometry_from_wkt();
    """
    )
    op.execute(
        """
        CREATE TRIGGER trg_zones_sync_geom
        BEFORE INSERT OR UPDATE ON zones
        FOR EACH ROW
        EXECUTE FUNCTION sync_geometry_from_wkt();
    """
    )
    op.execute(
        """
        CREATE TRIGGER trg_sub_zones_sync_geom
        BEFORE INSERT OR UPDATE ON sub_zones
        FOR EACH ROW
        EXECUTE FUNCTION sync_geometry_from_wkt();
    """
    )


def downgrade() -> None:
    # Drop triggers - use explicit statements to avoid SQL injection concerns
    op.execute("DROP TRIGGER IF EXISTS trg_fields_sync_geom ON fields;")
    op.execute("DROP TRIGGER IF EXISTS trg_zones_sync_geom ON zones;")
    op.execute("DROP TRIGGER IF EXISTS trg_sub_zones_sync_geom ON sub_zones;")

    op.execute("DROP FUNCTION IF EXISTS sync_geometry_from_wkt();")

    # Drop spatial indexes
    op.execute("DROP INDEX IF EXISTS ix_subzones_geom;")
    op.execute("DROP INDEX IF EXISTS ix_zones_geom;")
    op.execute("DROP INDEX IF EXISTS ix_fields_geom;")

    # Drop tables (cascades foreign keys)
    op.drop_table("sub_zones")
    op.drop_table("zones")
    op.drop_table("fields")
    op.drop_table("farms")

    # Note: We don't drop PostGIS extension as other tables may use it
