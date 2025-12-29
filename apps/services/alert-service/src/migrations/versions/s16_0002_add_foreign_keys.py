"""
Sprint 16: Add Foreign Key and CHECK Constraints

Adds foreign key constraints for tenant_id and field_id references,
and CHECK constraint for cooldown_hours validation.

Revision ID: s16_0002
Revises: s16_0001
Create Date: 2025-12-29
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "s16_0002"
down_revision = "s16_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Add foreign key constraints and CHECK constraints.

    Note: This migration assumes that 'tenants' and 'fields' tables exist
    in the same database schema. If these are cross-service references,
    you may need to adjust the implementation or create reference tables.
    """

    # -------------------------------------------------------------------------
    # Add Foreign Key Constraints to alerts table
    # -------------------------------------------------------------------------

    # Add FK constraint for tenant_id
    # Note: Drop existing index first if it exists, as FK will create its own index
    op.create_foreign_key(
        "fk_alerts_tenant_id",
        "alerts",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # Add FK constraint for field_id
    op.create_foreign_key(
        "fk_alerts_field_id",
        "alerts",
        "fields",
        ["field_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # -------------------------------------------------------------------------
    # Add Foreign Key Constraints to alert_rules table
    # -------------------------------------------------------------------------

    # Add FK constraint for tenant_id
    op.create_foreign_key(
        "fk_alert_rules_tenant_id",
        "alert_rules",
        "tenants",
        ["tenant_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # Add FK constraint for field_id
    op.create_foreign_key(
        "fk_alert_rules_field_id",
        "alert_rules",
        "fields",
        ["field_id"],
        ["id"],
        ondelete="CASCADE"
    )

    # -------------------------------------------------------------------------
    # Add CHECK Constraint to alert_rules table
    # -------------------------------------------------------------------------

    # Ensure cooldown_hours is positive
    op.create_check_constraint(
        "ck_alert_rules_cooldown_positive",
        "alert_rules",
        "cooldown_hours > 0"
    )


def downgrade() -> None:
    """
    Remove foreign key constraints and CHECK constraints.
    """

    # -------------------------------------------------------------------------
    # Drop CHECK Constraint
    # -------------------------------------------------------------------------
    op.drop_constraint(
        "ck_alert_rules_cooldown_positive",
        "alert_rules",
        type_="check"
    )

    # -------------------------------------------------------------------------
    # Drop Foreign Key Constraints from alert_rules table
    # -------------------------------------------------------------------------
    op.drop_constraint(
        "fk_alert_rules_field_id",
        "alert_rules",
        type_="foreignkey"
    )

    op.drop_constraint(
        "fk_alert_rules_tenant_id",
        "alert_rules",
        type_="foreignkey"
    )

    # -------------------------------------------------------------------------
    # Drop Foreign Key Constraints from alerts table
    # -------------------------------------------------------------------------
    op.drop_constraint(
        "fk_alerts_field_id",
        "alerts",
        type_="foreignkey"
    )

    op.drop_constraint(
        "fk_alerts_tenant_id",
        "alerts",
        type_="foreignkey"
    )
