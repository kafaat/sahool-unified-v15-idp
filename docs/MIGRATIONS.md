# SAHOOL Platform - Database Migration Rules

## Overview

This document defines strict rules for database migrations to prevent conflicts
and ensure safe deployments across all environments.

## Golden Rules

### 1. Immutability After Merge

> **No migration is ever edited after merge to main.**

Once a migration is merged:
- It cannot be modified
- It cannot be deleted
- If there's an error, create a new migration to fix it

### 2. Sprint Prefixes

Each sprint has its own migration prefix to prevent file conflicts:

| Sprint | Prefix | Example |
|--------|--------|---------|
| Sprint 1 | `s1_` | `s1_001_initial_schema.py` |
| Sprint 2 | `s2_` | `s2_001_add_indexes.py` |
| Sprint 3 | `s3_` | `s3_001_refactor_fields.py` |
| Sprint 4 | `s4_` | `s4_001_add_events.py` |
| Sprint 5 | `s5_` | `s5_001_marketplace.py` |
| Sprint 6 | `s6_` | `s6_001_analytics.py` |
| Sprint 7 | `s7_` | `s7_001_ai_features.py` |

### 3. Downgrade Support

> **Downgrade must always work.**

Every `upgrade()` must have a working `downgrade()`:

```python
def upgrade():
    op.add_column('fields', sa.Column('ndvi_score', sa.Float()))

def downgrade():
    op.drop_column('fields', 'ndvi_score')
```

### 4. Atomic Changes

> **One logical change = one migration.**

Bad:
```python
# DON'T: Multiple unrelated changes
def upgrade():
    op.add_column('users', ...)
    op.create_table('products', ...)
    op.add_index('fields', ...)
```

Good:
```python
# DO: Separate migrations
# s3_001_add_user_email.py
# s3_002_create_products_table.py
# s3_003_add_field_indexes.py
```

## Naming Convention

```
{sprint_prefix}_{sequence}_{description}.py
```

- `sprint_prefix`: `s1_`, `s2_`, etc.
- `sequence`: 3-digit number (`001`, `002`, etc.)
- `description`: snake_case, max 30 chars

Examples:
- `s1_001_initial_schema.py`
- `s3_005_add_ndvi_column.py`
- `s7_012_create_ai_feedback_table.py`

## Migration Checklist

Before creating a migration:

- [ ] Check current sprint prefix
- [ ] Check last sequence number in your sprint
- [ ] Write both `upgrade()` and `downgrade()`
- [ ] Test `downgrade()` locally
- [ ] Review with team if schema change is significant

## Conflict Prevention

### Working on the Same Sprint

If two developers work on Sprint 3 migrations:

1. **Communicate**: Announce in team chat before creating
2. **Pull first**: Always `git pull` before creating
3. **Use next sequence**: Check existing migrations first

### Feature Branches

When working on a feature branch:

1. Create migration with your sprint prefix
2. If main has new migrations when merging:
   - Keep your migration as-is
   - Increment sequence if conflict

## Recovery Procedures

### Migration Failed in Production

1. **Don't edit the migration**
2. Create a new migration to fix:
   ```python
   # s3_006_fix_column_type.py
   def upgrade():
       op.alter_column('fields', 'area', type_=sa.Numeric(10, 2))
   ```

### Need to Remove a Column

1. First migration: Mark as deprecated
2. Wait for next release cycle
3. Second migration: Remove column

```python
# s4_001_deprecate_old_field.py
def upgrade():
    # Add new column
    op.add_column('fields', sa.Column('area_sqm', sa.Float()))
    # Migrate data
    op.execute("UPDATE fields SET area_sqm = area * 10000")

# s5_001_remove_deprecated_field.py
def upgrade():
    op.drop_column('fields', 'area')  # Now safe to remove
```

## Environment Safety

### Development
- Run all migrations
- Test downgrades

### Staging
- Run all migrations
- Verify with production-like data

### Production
- Run during maintenance window
- Have rollback plan ready
- Monitor after deployment

## Commands

```bash
# Create new migration
alembic revision -m "s3_005_add_ndvi_column"

# Upgrade to latest
alembic upgrade head

# Downgrade one step
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```
