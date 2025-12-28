# Inventory Service Database Migrations

This directory contains database migration files for the SAHOOL Inventory Service.

## Generating Migrations

To generate a new migration after modifying models:

```bash
# From the inventory-service directory
alembic revision --autogenerate -m "description of changes"
```

## Applying Migrations

To apply pending migrations:

```bash
# Apply all pending migrations
alembic upgrade head

# Apply specific migration
alembic upgrade <revision_id>

# Rollback one migration
alembic downgrade -1
```

## Initial Migration

The initial migration should be generated to create all tables from the SQLAlchemy models in `src/models/inventory.py`.

To generate the initial migration:

```bash
alembic revision --autogenerate -m "initial inventory schema"
```

## Database URL

The migration scripts use the `DATABASE_URL` environment variable. If not set, it falls back to the URL in `alembic.ini`.

```bash
export DATABASE_URL="postgresql+asyncpg://user:password@host:port/dbname"
```

## Note

After Alembic migrations are set up, remove the `Base.metadata.create_all()` call from `src/main.py` and use migrations instead.
