"""
Sprint 17: Equipment Service Initial Migration

Creates tables for equipment, maintenance records, and alerts.

Revision ID: s17_0001
Revises: None
Create Date: 2026-01-06
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s17_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create equipment, equipment_maintenance, and equipment_alerts tables.
    """
    # -------------------------------------------------------------------------
    # Equipment Table
    # -------------------------------------------------------------------------
    op.create_table(
        "equipment",
        # Identity
        sa.Column("equipment_id", sa.String(length=50), primary_key=True),
        sa.Column("tenant_id", sa.String(length=100), nullable=False),
        # Basic information (bilingual)
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("name_ar", sa.String(length=200), nullable=True),
        # Equipment classification
        sa.Column("equipment_type", sa.String(length=50), nullable=False),
        sa.Column(
            "status", sa.String(length=20), nullable=False, server_default="operational"
        ),
        # Equipment details
        sa.Column("brand", sa.String(length=100), nullable=True),
        sa.Column("model", sa.String(length=100), nullable=True),
        sa.Column("serial_number", sa.String(length=100), nullable=True, unique=True),
        sa.Column("year", sa.Integer(), nullable=True),
        # Purchase information
        sa.Column("purchase_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("purchase_price", sa.Numeric(precision=12, scale=2), nullable=True),
        # Location information
        sa.Column("field_id", sa.String(length=100), nullable=True),
        sa.Column("location_name", sa.String(length=200), nullable=True),
        # Specifications
        sa.Column("horsepower", sa.Integer(), nullable=True),
        sa.Column("fuel_capacity_liters", sa.Numeric(precision=8, scale=2), nullable=True),
        # Telemetry data
        sa.Column("current_fuel_percent", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("current_hours", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("current_lat", sa.Numeric(precision=10, scale=7), nullable=True),
        sa.Column("current_lon", sa.Numeric(precision=10, scale=7), nullable=True),
        # Maintenance scheduling
        sa.Column("last_maintenance_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_maintenance_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("next_maintenance_hours", sa.Numeric(precision=10, scale=2), nullable=True),
        # QR code for easy identification
        sa.Column("qr_code", sa.String(length=100), nullable=True, unique=True),
        # Additional metadata
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        # Timestamps
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

    # Indexes for equipment table
    # Primary query pattern: tenant + status
    op.create_index(
        "ix_equipment_tenant_status",
        "equipment",
        ["tenant_id", "status"],
    )

    # Equipment type queries
    op.create_index(
        "ix_equipment_type_status",
        "equipment",
        ["equipment_type", "status"],
    )

    # Field-based queries
    op.create_index(
        "ix_equipment_field_status",
        "equipment",
        ["field_id", "status"],
    )

    # Maintenance scheduling queries
    op.create_index(
        "ix_equipment_next_maintenance",
        "equipment",
        ["next_maintenance_at"],
    )

    # -------------------------------------------------------------------------
    # Equipment Maintenance Table
    # -------------------------------------------------------------------------
    op.create_table(
        "equipment_maintenance",
        # Identity
        sa.Column("record_id", sa.String(length=50), primary_key=True),
        sa.Column("equipment_id", sa.String(length=50), nullable=False),
        # Maintenance details
        sa.Column("maintenance_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("description_ar", sa.Text(), nullable=True),
        # Who and when
        sa.Column("performed_by", sa.String(length=100), nullable=True),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False),
        # Cost tracking
        sa.Column("cost", sa.Numeric(precision=10, scale=2), nullable=True),
        # Additional details
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("parts_replaced", postgresql.ARRAY(sa.String()), nullable=True),
    )

    # Indexes for equipment_maintenance table
    # Equipment maintenance history
    op.create_index(
        "ix_maintenance_equipment_date",
        "equipment_maintenance",
        ["equipment_id", "performed_at"],
    )

    # Maintenance type analysis
    op.create_index(
        "ix_maintenance_type",
        "equipment_maintenance",
        ["maintenance_type", "performed_at"],
    )

    # -------------------------------------------------------------------------
    # Equipment Alerts Table
    # -------------------------------------------------------------------------
    op.create_table(
        "equipment_alerts",
        # Identity
        sa.Column("alert_id", sa.String(length=50), primary_key=True),
        sa.Column("equipment_id", sa.String(length=50), nullable=False),
        sa.Column("equipment_name", sa.String(length=200), nullable=False),
        # Alert details
        sa.Column("maintenance_type", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("description_ar", sa.Text(), nullable=True),
        # Priority
        sa.Column("priority", sa.String(length=20), nullable=False),
        # Due dates
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("due_hours", sa.Numeric(precision=10, scale=2), nullable=True),
        # Status
        sa.Column("is_overdue", sa.Boolean(), nullable=False, server_default="false"),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )

    # Indexes for equipment_alerts table
    # Overdue alerts
    op.create_index(
        "ix_alerts_overdue",
        "equipment_alerts",
        ["is_overdue", "priority"],
    )

    # Equipment alerts
    op.create_index(
        "ix_alerts_equipment_due",
        "equipment_alerts",
        ["equipment_id", "due_at"],
    )


def downgrade() -> None:
    """
    Drop equipment, equipment_maintenance, and equipment_alerts tables.
    """
    # Drop equipment_alerts table
    op.drop_index("ix_alerts_equipment_due", table_name="equipment_alerts")
    op.drop_index("ix_alerts_overdue", table_name="equipment_alerts")
    op.drop_table("equipment_alerts")

    # Drop equipment_maintenance table
    op.drop_index("ix_maintenance_type", table_name="equipment_maintenance")
    op.drop_index("ix_maintenance_equipment_date", table_name="equipment_maintenance")
    op.drop_table("equipment_maintenance")

    # Drop equipment table
    op.drop_index("ix_equipment_next_maintenance", table_name="equipment")
    op.drop_index("ix_equipment_field_status", table_name="equipment")
    op.drop_index("ix_equipment_type_status", table_name="equipment")
    op.drop_index("ix_equipment_tenant_status", table_name="equipment")
    op.drop_table("equipment")
