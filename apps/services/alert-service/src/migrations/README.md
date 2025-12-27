# Alert Service Database Migrations

This directory contains Alembic database migrations for the SAHOOL Alert Service.

## Structure

```
migrations/
├── env.py              # Alembic environment configuration
├── script.py.mako      # Template for new migrations
├── __init__.py
└── versions/           # Migration scripts
    ├── __init__.py
    └── s16_0001_alerts_initial.py  # Initial migration
```

## Database Schema

### Tables

#### alerts
Stores agricultural alerts and warnings.

**Key Fields:**
- `id` (UUID): Primary key
- `tenant_id` (UUID): Multi-tenancy support
- `field_id` (String): Field reference
- `type` (String): Alert type (weather, pest, disease, etc.)
- `severity` (String): Severity level (critical, high, medium, low, info)
- `status` (String): Status (active, acknowledged, dismissed, resolved, expired)
- `title`, `title_en`: Bilingual titles
- `message`, `message_en`: Bilingual messages
- `recommendations`, `recommendations_en`: JSONB arrays
- `metadata`: JSONB for additional data
- Timestamps: `created_at`, `expires_at`, `acknowledged_at`, `dismissed_at`, `resolved_at`

**Indexes:**
- `ix_alerts_field_status`: Field + status + created_at
- `ix_alerts_tenant_created`: Tenant-wide queries
- `ix_alerts_type_severity`: Type and severity filtering
- `ix_alerts_active`: Active alerts query
- `ix_alerts_source`: Source tracking

#### alert_rules
Stores automated alert rule configurations.

**Key Fields:**
- `id` (UUID): Primary key
- `tenant_id` (UUID): Multi-tenancy support
- `field_id` (String): Field reference
- `name`, `name_en`: Bilingual rule names
- `enabled` (Boolean): Active status
- `condition` (JSONB): Rule condition configuration
- `alert_config` (JSONB): Alert configuration
- `cooldown_hours` (Integer): Cooldown period
- `last_triggered_at`: Last trigger timestamp
- Timestamps: `created_at`, `updated_at`

**Indexes:**
- `ix_alert_rules_field`: Field + enabled
- `ix_alert_rules_tenant`: Tenant + enabled
- `ix_alert_rules_enabled`: Active rules query

## Usage

### Running Migrations

From the `apps/services/alert-service` directory:

```bash
# Upgrade to latest version
alembic upgrade head

# Downgrade one version
alembic downgrade -1

# Show current version
alembic current

# Show migration history
alembic history
```

### Creating New Migrations

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "description"

# Create empty migration
alembic revision -m "description"
```

### Environment Variables

Set the database URL:

```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/sahool_alerts"
```

Or use default: `postgresql://postgres:postgres@localhost:5432/sahool_alerts`

## Migration Guidelines

1. **Always test migrations in development first**
2. **Never edit existing migrations** - create new ones instead
3. **Always provide both upgrade() and downgrade() functions**
4. **Use transactions for data migrations**
5. **Document complex migrations**
6. **Test rollback (downgrade) functionality**

## Initial Setup

For a fresh database:

```bash
# Create database
createdb sahool_alerts

# Run migrations
alembic upgrade head
```

## Troubleshooting

### Migration fails with "relation already exists"

This usually means the table was created manually. Either:
1. Drop the table and run migration
2. Mark migration as run: `alembic stamp head`

### Database URL not found

Ensure `DATABASE_URL` environment variable is set or update `database.py`

## References

- Alembic Documentation: https://alembic.sqlalchemy.org/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
