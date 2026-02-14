"""
Sprint 8: NDVI Time-Series Storage

Creates tables for NDVI observations and alerts with temporal indexing.

Revision ID: s8_0001
Revises: None
Create Date: 2024-01-01
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s8_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # NDVI Observations Table
    # -------------------------------------------------------------------------
    op.create_table(
        "ndvi_observations",
        # Identity
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), nullable=False),
        # Observation date
        sa.Column("obs_date", sa.Date(), nullable=False),
        # NDVI values
        sa.Column("ndvi_mean", sa.Float(), nullable=False),
        sa.Column("ndvi_min", sa.Float(), nullable=True),
        sa.Column("ndvi_max", sa.Float(), nullable=True),
        sa.Column("ndvi_std", sa.Float(), nullable=True),
        sa.Column("ndvi_p10", sa.Float(), nullable=True),
        sa.Column("ndvi_p90", sa.Float(), nullable=True),
        # Quality metrics
        sa.Column("cloud_coverage", sa.Float(), nullable=False, server_default="0"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0"),
        sa.Column("pixel_count", sa.Integer(), nullable=True),
        # Source tracking
        sa.Column("source", sa.String(length=80), nullable=False, server_default="sentinel2"),
        sa.Column("scene_id", sa.String(length=200), nullable=True),
        # Metadata
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # Primary query pattern: field + date range
    op.create_index("ix_ndvi_field_date", "ndvi_observations", ["field_id", "obs_date"])

    # Tenant-wide queries
    op.create_index("ix_ndvi_tenant_date", "ndvi_observations", ["tenant_id", "obs_date"])

    # Source filtering
    op.create_index("ix_ndvi_source", "ndvi_observations", ["source"])

    # Unique constraint: one observation per field per date per source
    op.create_index(
        "uq_ndvi_field_date_source",
        "ndvi_observations",
        ["field_id", "obs_date", "source"],
        unique=True,
    )

    # -------------------------------------------------------------------------
    # NDVI Alerts Table
    # -------------------------------------------------------------------------
    op.create_table(
        "ndvi_alerts",
        # Identity
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("observation_id", postgresql.UUID(as_uuid=True), nullable=True),
        # Alert details
        sa.Column("alert_type", sa.String(length=40), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="medium"),
        sa.Column("current_value", sa.Float(), nullable=False),
        sa.Column("threshold_value", sa.Float(), nullable=True),
        sa.Column("deviation_pct", sa.Float(), nullable=True),
        sa.Column("z_score", sa.Float(), nullable=True),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("message_ar", sa.Text(), nullable=True),
        # Status tracking
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by", postgresql.UUID(as_uuid=True), nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # Field alerts query
    op.create_index("ix_ndvi_alerts_field", "ndvi_alerts", ["field_id", "created_at"])

    # Tenant alerts query
    op.create_index("ix_ndvi_alerts_tenant", "ndvi_alerts", ["tenant_id", "created_at"])

    # Unacknowledged alerts query
    op.create_index("ix_ndvi_alerts_unacked", "ndvi_alerts", ["tenant_id", "acknowledged"])

    # Foreign key to observations (optional, soft reference)
    # Not enforced to allow alert retention even if observation is deleted


def downgrade() -> None:
    # Drop alerts table
    op.drop_index("ix_ndvi_alerts_unacked", table_name="ndvi_alerts")
    op.drop_index("ix_ndvi_alerts_tenant", table_name="ndvi_alerts")
    op.drop_index("ix_ndvi_alerts_field", table_name="ndvi_alerts")
    op.drop_table("ndvi_alerts")

    # Drop observations table
    op.drop_index("uq_ndvi_field_date_source", table_name="ndvi_observations")
    op.drop_index("ix_ndvi_source", table_name="ndvi_observations")
    op.drop_index("ix_ndvi_tenant_date", table_name="ndvi_observations")
    op.drop_index("ix_ndvi_field_date", table_name="ndvi_observations")
    op.drop_table("ndvi_observations")
