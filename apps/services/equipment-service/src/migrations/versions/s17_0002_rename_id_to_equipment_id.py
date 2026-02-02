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

    FIX: Drop and recreate foreign key constraints to allow type change.
    """
    conn = op.get_bind()

    # Check if the 'id' column exists (to make migration idempotent)
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
        # Step 1: Drop foreign key constraints that reference equipment.id
        try:
            op.drop_constraint(
                "equipment_maintenance_equipment_id_fkey",
                "equipment_maintenance",
                type_="foreignkey"
            )
            print("✅ Dropped foreign key constraint equipment_maintenance_equipment_id_fkey")
        except Exception as e:
            print(f"ℹ️  Foreign key constraint may not exist: {e}")

        # Step 2: Rename and change type of equipment.id
        op.alter_column(
            "equipment",
            "id",
            new_column_name="equipment_id",
            existing_type=sa.dialects.postgresql.UUID(),
            type_=sa.String(length=50),
            existing_nullable=False,
            postgresql_using="id::text"  # Cast UUID to text during conversion
        )
        print("✅ Renamed equipment.id to equipment.equipment_id")

        # Step 3: Also change equipment_maintenance.equipment_id type if it exists
        try:
            op.alter_column(
                "equipment_maintenance",
                "equipment_id",
                existing_type=sa.dialects.postgresql.UUID(),
                type_=sa.String(length=50),
                existing_nullable=False,
                postgresql_using="equipment_id::text"
            )
            print("✅ Changed equipment_maintenance.equipment_id type to String(50)")
        except Exception as e:
            print(f"ℹ️  equipment_maintenance.equipment_id may already be correct type: {e}")

        # Step 4: Recreate foreign key constraint
        try:
            op.create_foreign_key(
                "equipment_maintenance_equipment_id_fkey",
                "equipment_maintenance",
                "equipment",
                ["equipment_id"],
                ["equipment_id"],
                ondelete="CASCADE"
            )
            print("✅ Recreated foreign key constraint")
        except Exception as e:
            print(f"ℹ️  Could not recreate foreign key: {e}")
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
