"""
Sprint 17: Rename equipment.id to equipment.equipment_id

Fixes schema mismatch where database has 'id' column but model expects 'equipment_id'.

Revision ID: s17_0002
Revises: s17_0001
Create Date: 2026-01-28
"""

import sqlalchemy as sa
from alembic import op

revision = "s17_0002"
down_revision = "s17_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """
    Rename 'id' column to 'equipment_id' in equipment table.
    Also update the type from UUID to String(50) to match the model.
    """
    # Check if the 'id' column exists (to make migration idempotent)
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'equipment' AND column_name = 'id'
            """
        )
    )
    has_id_column = result.fetchone() is not None

    if has_id_column:
        # Rename the column from 'id' to 'equipment_id'
        op.alter_column(
            "equipment",
            "id",
            new_column_name="equipment_id",
            existing_type=sa.dialects.postgresql.UUID(),
            type_=sa.String(length=50),
            existing_nullable=False,
        )
        print("✅ Renamed equipment.id to equipment.equipment_id")
    else:
        print("ℹ️  Column 'id' not found, assuming migration already applied")


def downgrade() -> None:
    """
    Rename 'equipment_id' column back to 'id'.
    """
    # Check if the 'equipment_id' column exists
    conn = op.get_bind()
    result = conn.execute(
        sa.text(
            """
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = 'equipment' AND column_name = 'equipment_id'
            """
        )
    )
    has_equipment_id_column = result.fetchone() is not None

    if has_equipment_id_column:
        # Rename the column back from 'equipment_id' to 'id'
        op.alter_column(
            "equipment",
            "equipment_id",
            new_column_name="id",
            existing_type=sa.String(length=50),
            type_=sa.dialects.postgresql.UUID(),
            existing_nullable=False,
        )
        print("✅ Renamed equipment.equipment_id back to equipment.id")
    else:
        print("ℹ️  Column 'equipment_id' not found, assuming downgrade already applied")
