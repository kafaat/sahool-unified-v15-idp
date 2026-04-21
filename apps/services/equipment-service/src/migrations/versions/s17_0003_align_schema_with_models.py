"""
Sprint 17: Align equipment table schema with db_models.py

The initial migration (s17_0001) created columns with legacy names. The current
db_models.py maps Python attributes to different DB column names. This migration
renames the columns to match, so SQLAlchemy generates correct SQL.

Column renames:
  equipment_id      → id               (PK; Python attr still equipment_id)
  equipment_type    → type             (Python attr still equipment_type)
  brand             → manufacturer
  field_id          → assigned_field_id
  location_name     → current_location
  current_hours     → operating_hours
  last_maintenance_at → last_maintenance_date
  next_maintenance_at → next_maintenance_date
  metadata          → documents

Index renames follow the column renames. Indexes on unchanged columns are
preserved as-is.

Revision ID: s17_0003
Revises: s17_0002
Create Date: 2026-04-21
"""

import sqlalchemy as sa
from alembic import op

revision = "s17_0003"
down_revision = "s17_0002"
branch_labels = None
depends_on = None

# Map of old_column_name → new_column_name in the equipment table.
_EQUIPMENT_COLUMN_RENAMES = {
    "equipment_id": "id",
    "equipment_type": "type",
    "brand": "manufacturer",
    "field_id": "assigned_field_id",
    "location_name": "current_location",
    "current_hours": "operating_hours",
    "last_maintenance_at": "last_maintenance_date",
    "next_maintenance_at": "next_maintenance_date",
    "metadata": "documents",
}

# Indexes to drop before renaming columns, and re-create after with updated
# column references. Tuple: (index_name, table, new_columns).
_INDEXES_TO_RECREATE = [
    ("ix_equipment_type_status", "equipment", ["type", "status"]),
    ("ix_equipment_field_status", "equipment", ["assigned_field_id", "status"]),
    ("ix_equipment_next_maintenance", "equipment", ["next_maintenance_date"]),
]

# New indexes defined in db_models.py that didn't exist before.
_NEW_INDEXES = [
    ("ix_equipment_tenant_type", "equipment", ["tenant_id", "type"]),
    ("ix_equipment_tenant_maintenance", "equipment", ["tenant_id", "next_maintenance_date"]),
]


def _column_exists(conn, table: str, column: str) -> bool:
    result = conn.execute(
        sa.text(
            "SELECT 1 FROM information_schema.columns "
            "WHERE table_name = :t AND column_name = :c"
        ),
        {"t": table, "c": column},
    )
    return result.fetchone() is not None


def _index_exists(conn, index: str) -> bool:
    result = conn.execute(
        sa.text(
            "SELECT 1 FROM pg_indexes WHERE indexname = :i"
        ),
        {"i": index},
    )
    return result.fetchone() is not None


def upgrade() -> None:
    conn = op.get_bind()

    # ------------------------------------------------------------------
    # 1. Drop indexes that reference columns about to be renamed.
    # ------------------------------------------------------------------
    for idx_name, _table, _cols in _INDEXES_TO_RECREATE:
        if _index_exists(conn, idx_name):
            op.drop_index(idx_name, table_name="equipment", if_exists=True)

    # ------------------------------------------------------------------
    # 2. Drop FK on equipment_maintenance so we can rename equipment.id.
    # ------------------------------------------------------------------
    try:
        op.drop_constraint(
            "equipment_maintenance_equipment_id_fkey",
            "equipment_maintenance",
            type_="foreignkey",
        )
    except Exception:
        pass  # FK may not exist

    # ------------------------------------------------------------------
    # 3. Rename columns (idempotent: skip if target name already present).
    # ------------------------------------------------------------------
    for old_name, new_name in _EQUIPMENT_COLUMN_RENAMES.items():
        if _column_exists(conn, "equipment", old_name) and not _column_exists(conn, "equipment", new_name):
            op.alter_column("equipment", old_name, new_column_name=new_name)

    # ------------------------------------------------------------------
    # 4. Re-create renamed indexes.
    # ------------------------------------------------------------------
    for idx_name, table, cols in _INDEXES_TO_RECREATE:
        if not _index_exists(conn, idx_name):
            op.create_index(idx_name, table, cols)

    # ------------------------------------------------------------------
    # 5. Create new indexes from db_models.py that didn't exist before.
    # ------------------------------------------------------------------
    for idx_name, table, cols in _NEW_INDEXES:
        if not _index_exists(conn, idx_name):
            op.create_index(idx_name, table, cols)


def downgrade() -> None:
    conn = op.get_bind()

    # Drop new indexes
    for idx_name, _table, _cols in _NEW_INDEXES:
        if _index_exists(conn, idx_name):
            op.drop_index(idx_name, table_name="equipment", if_exists=True)

    # Drop recreated indexes
    for idx_name, _table, _cols in _INDEXES_TO_RECREATE:
        if _index_exists(conn, idx_name):
            op.drop_index(idx_name, table_name="equipment", if_exists=True)

    # Reverse renames
    reverse = {v: k for k, v in _EQUIPMENT_COLUMN_RENAMES.items()}
    for old_name, new_name in reverse.items():
        if _column_exists(conn, "equipment", old_name) and not _column_exists(conn, "equipment", new_name):
            op.alter_column("equipment", old_name, new_column_name=new_name)

    # Restore old indexes
    for idx_name, table, cols in _INDEXES_TO_RECREATE:
        if not _index_exists(conn, idx_name):
            # Restore with original column names (pre-rename)
            orig_cols = [_EQUIPMENT_COLUMN_RENAMES.get(c, c) for c in
                         {"type": ["equipment_type", "status"],
                          "assigned_field_id": ["field_id", "status"],
                          "next_maintenance_date": ["next_maintenance_at"]}
                         .get(cols[0], cols)]
            op.create_index(idx_name, table, orig_cols)
