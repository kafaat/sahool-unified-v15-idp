"""
Sprint 16: Alert Service Initial Migration

Creates tables for alerts and alert rules with multi-tenancy support.

Revision ID: s16_0001
Revises: None
Create Date: 2025-12-27
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "s16_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Create alerts and alert_rules tables.
    """
    # -------------------------------------------------------------------------
    # Alerts Table
    # -------------------------------------------------------------------------
    op.create_table(
        "alerts",
        # Identity
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("field_id", sa.String(length=100), nullable=False),
        # Classification
        sa.Column("type", sa.String(length=40), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        # Content (bilingual)
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("title_en", sa.String(length=200), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("message_en", sa.Text(), nullable=True),
        # Recommendations (JSON arrays)
        sa.Column("recommendations", postgresql.JSONB(), nullable=True),
        sa.Column("recommendations_en", postgresql.JSONB(), nullable=True),
        # Metadata
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
        # Source tracking
        sa.Column("source_service", sa.String(length=80), nullable=True),
        sa.Column("correlation_id", sa.String(length=100), nullable=True),
        # Timestamps
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        # Acknowledgment
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("acknowledged_by", sa.String(length=100), nullable=True),
        # Dismissal
        sa.Column("dismissed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("dismissed_by", sa.String(length=100), nullable=True),
        # Resolution
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("resolved_by", sa.String(length=100), nullable=True),
        sa.Column("resolution_note", sa.Text(), nullable=True),
    )

    # Indexes for alerts table
    # Primary query pattern: field + status + created_at
    op.create_index(
        "ix_alerts_field_status",
        "alerts",
        ["field_id", "status", "created_at"],
    )

    # Tenant-wide queries
    op.create_index(
        "ix_alerts_tenant_created",
        "alerts",
        ["tenant_id", "created_at"],
    )

    # Type and severity filtering
    op.create_index(
        "ix_alerts_type_severity",
        "alerts",
        ["type", "severity"],
    )

    # Active alerts query
    op.create_index(
        "ix_alerts_active",
        "alerts",
        ["status", "expires_at"],
    )

    # Source tracking
    op.create_index(
        "ix_alerts_source",
        "alerts",
        ["source_service"],
    )

    # -------------------------------------------------------------------------
    # Alert Rules Table
    # -------------------------------------------------------------------------
    op.create_table(
        "alert_rules",
        # Identity
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("field_id", sa.String(length=100), nullable=False),
        # Rule naming (bilingual)
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("name_en", sa.String(length=100), nullable=True),
        # Rule status
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default="true"),
        # Rule condition (JSON)
        # Structure: {metric: str, operator: str, value: float, duration_minutes: int}
        sa.Column("condition", postgresql.JSONB(), nullable=False),
        # Alert configuration (JSON)
        # Structure: {type: str, severity: str, title: str, title_en: str, message_template: str}
        sa.Column("alert_config", postgresql.JSONB(), nullable=False),
        # Cooldown period
        sa.Column("cooldown_hours", sa.Integer(), nullable=False, server_default="24"),
        # Tracking
        sa.Column("last_triggered_at", sa.DateTime(timezone=True), nullable=True),
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

    # Indexes for alert_rules table
    # Field rules query
    op.create_index(
        "ix_alert_rules_field",
        "alert_rules",
        ["field_id", "enabled"],
    )

    # Tenant rules query
    op.create_index(
        "ix_alert_rules_tenant",
        "alert_rules",
        ["tenant_id", "enabled"],
    )

    # Active rules query
    op.create_index(
        "ix_alert_rules_enabled",
        "alert_rules",
        ["enabled", "last_triggered_at"],
    )


def downgrade() -> None:
    """
    Drop alerts and alert_rules tables.
    """
    # Drop alert_rules table
    op.drop_index("ix_alert_rules_enabled", table_name="alert_rules")
    op.drop_index("ix_alert_rules_tenant", table_name="alert_rules")
    op.drop_index("ix_alert_rules_field", table_name="alert_rules")
    op.drop_table("alert_rules")

    # Drop alerts table
    op.drop_index("ix_alerts_source", table_name="alerts")
    op.drop_index("ix_alerts_active", table_name="alerts")
    op.drop_index("ix_alerts_type_severity", table_name="alerts")
    op.drop_index("ix_alerts_tenant_created", table_name="alerts")
    op.drop_index("ix_alerts_field_status", table_name="alerts")
    op.drop_table("alerts")
