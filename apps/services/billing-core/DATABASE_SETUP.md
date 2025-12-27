# SAHOOL Billing Core - Database Setup Guide
# دليل إعداد قاعدة البيانات

This guide explains how to set up and manage the PostgreSQL database for the billing-core service.

## 📋 Table of Contents

1. [Architecture](#architecture)
2. [Database Schema](#database-schema)
3. [Setup Instructions](#setup-instructions)
4. [Database Migrations](#database-migrations)
5. [Environment Variables](#environment-variables)
6. [Development Workflow](#development-workflow)
7. [Production Deployment](#production-deployment)

---

## 🏗️ Architecture

The billing-core service uses:
- **PostgreSQL** as the primary database
- **Async SQLAlchemy** for ORM and database operations
- **Alembic** for database migrations
- **asyncpg** as the PostgreSQL driver

### File Structure

```
billing-core/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── database.py           # Database configuration & session management
│   ├── models.py             # SQLAlchemy ORM models
│   ├── repository.py         # Database operations (CRUD)
│   └── main.py              # FastAPI application
├── alembic/
│   ├── versions/            # Migration scripts
│   │   └── 001_initial_billing_schema.py
│   ├── env.py               # Alembic environment configuration
│   └── script.py.mako       # Migration template
├── alembic.ini              # Alembic configuration
└── requirements.txt         # Python dependencies
```

---

## 📊 Database Schema

### Tables

#### 1. **subscriptions** (الاشتراكات)
Stores tenant subscription information.

**Columns:**
- `id` (UUID) - Primary key
- `tenant_id` (String) - Tenant/customer identifier
- `plan_id` (String) - Plan identifier (free, starter, professional, enterprise)
- `status` (Enum) - Subscription status (active, trial, past_due, canceled, suspended, expired)
- `billing_cycle` (Enum) - Billing frequency (monthly, quarterly, yearly)
- `currency` (Enum) - Currency (USD, YER)
- `start_date`, `end_date` - Subscription period
- `trial_end_date` - Trial period end date
- `next_billing_date` - Next billing date
- `payment_method` (Enum) - Payment method
- `metadata` (JSONB) - Additional data
- `created_at`, `updated_at` - Timestamps

**Indexes:**
- `idx_subscription_tenant_status` - (tenant_id, status)
- `idx_subscription_next_billing` - (next_billing_date, status)

---

#### 2. **invoices** (الفواتير)
Stores billing invoices.

**Columns:**
- `id` (UUID) - Primary key
- `invoice_number` (String) - Human-readable invoice number (e.g., SAH-2025-0001)
- `subscription_id` (UUID) - Foreign key to subscriptions
- `tenant_id` (String) - Tenant identifier
- `status` (Enum) - Invoice status (draft, pending, paid, overdue, canceled, refunded)
- `currency` (Enum) - Currency
- `issue_date`, `due_date`, `paid_date` - Important dates
- `subtotal`, `tax_amount`, `discount_amount`, `total` - Amounts
- `amount_paid`, `amount_due` - Payment tracking
- `line_items` (JSONB) - Invoice line items
- `notes`, `notes_ar` - Additional notes

**Indexes:**
- `idx_invoice_tenant_status` - (tenant_id, status)
- `idx_invoice_due_date_status` - (due_date, status)

---

#### 3. **payments** (المدفوعات)
Tracks payment transactions.

**Columns:**
- `id` (UUID) - Primary key
- `invoice_id` (UUID) - Foreign key to invoices
- `tenant_id` (String) - Tenant identifier
- `amount` (Numeric) - Payment amount
- `currency` (Enum) - Currency
- `status` (Enum) - Payment status (pending, processing, succeeded, failed, refunded)
- `method` (Enum) - Payment method (credit_card, bank_transfer, mobile_money, cash, tharwatt)
- `paid_at`, `processed_at` - Processing timestamps
- `failure_reason` - Failure description
- `stripe_payment_id`, `tharwatt_transaction_id` - External references
- `metadata` (JSONB) - Additional data

**Indexes:**
- `idx_payment_tenant_status` - (tenant_id, status)
- `idx_payment_created` - (created_at)

---

#### 4. **usage_records** (سجلات الاستخدام)
Records usage metrics for usage-based billing.

**Columns:**
- `id` (UUID) - Primary key
- `subscription_id` (UUID) - Foreign key to subscriptions
- `tenant_id` (String) - Tenant identifier
- `metric_type` (String) - Metric name (e.g., 'satellite_analyses_per_month')
- `quantity` (Integer) - Usage quantity
- `recorded_at` - Timestamp of usage
- `metadata` (JSONB) - Additional context

**Indexes:**
- `idx_usage_subscription_metric` - (subscription_id, metric_type)
- `idx_usage_tenant_metric_date` - (tenant_id, metric_type, recorded_at)

---

## 🚀 Setup Instructions

### 1. Prerequisites

- PostgreSQL 14+ installed and running
- Python 3.11+
- Required Python packages (see requirements.txt)

### 2. Install Dependencies

```bash
cd apps/services/billing-core
pip install -r requirements.txt
```

### 3. Configure Database

Set the database URL in your environment:

```bash
# Development
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/sahool_billing"

# Or create a .env file
echo "DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/sahool_billing" > .env
```

### 4. Create Database

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE sahool_billing;

# Create user (optional)
CREATE USER sahool_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE sahool_billing TO sahool_user;
```

### 5. Run Migrations

```bash
# Initialize the database (creates tables)
cd apps/services/billing-core
alembic upgrade head
```

### 6. Verify Setup

```bash
# Run the service
python src/main.py

# Check health endpoint
curl http://localhost:8089/healthz
```

Expected response:
```json
{
  "status": "ok",
  "service": "billing-core",
  "version": "15.6.0",
  "database": {
    "status": "healthy",
    "database": "postgresql"
  }
}
```

---

## 🔄 Database Migrations

### Using Alembic

Alembic manages database schema changes through migrations.

#### Create a New Migration

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Add new column to subscriptions"

# Create empty migration (for manual changes)
alembic revision -m "Add custom index"
```

#### Apply Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade to specific version
alembic upgrade +1

# Show current version
alembic current

# Show migration history
alembic history
```

#### Rollback Migrations

```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific version
alembic downgrade <revision_id>

# Downgrade all migrations
alembic downgrade base
```

---

## 🔧 Environment Variables

### Required Variables

```bash
# Database Connection
DATABASE_URL="postgresql+asyncpg://user:password@host:port/database"

# Optional: Override individual settings
DB_POOL_SIZE=20              # Connection pool size (default: 5 for dev, 20 for prod)
DB_MAX_OVERFLOW=40           # Max overflow connections (default: 10 for dev, 40 for prod)
DB_POOL_TIMEOUT=30           # Connection timeout in seconds
DB_POOL_RECYCLE=3600         # Connection recycle time in seconds
```

### Example Configurations

**Development:**
```bash
export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/sahool_billing"
export ENVIRONMENT="development"
```

**Production:**
```bash
export DATABASE_URL="postgresql+asyncpg://sahool_user:secure_password@db.production.com:5432/sahool_billing"
export ENVIRONMENT="production"
export DB_POOL_SIZE=50
export DB_MAX_OVERFLOW=100
```

---

## 💻 Development Workflow

### 1. Making Schema Changes

```python
# 1. Update models in src/models.py
class Subscription(Base):
    # Add new column
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

# 2. Generate migration
alembic revision --autogenerate -m "Add notes to subscription"

# 3. Review generated migration in alembic/versions/

# 4. Apply migration
alembic upgrade head
```

### 2. Testing Database Operations

```python
# Example: Test repository functions
from src.database import get_db_context
from src.repository import BillingRepository
from src.models import SubscriptionStatus

async def test_subscription():
    async with get_db_context() as db:
        repo = BillingRepository(db)

        # Create subscription
        subscription = await repo.subscriptions.create(
            tenant_id="test-tenant",
            plan_id="starter",
            billing_cycle=BillingCycle.MONTHLY,
            start_date=date.today(),
            end_date=date.today() + timedelta(days=30),
        )

        # Get subscription
        result = await repo.subscriptions.get_by_id(subscription.id)
        print(result)
```

### 3. Database Reset (Development Only)

```bash
# WARNING: This will delete all data!
alembic downgrade base
alembic upgrade head
```

---

## 🚀 Production Deployment

### 1. Database Preparation

```bash
# 1. Create production database
createdb -U postgres sahool_billing_prod

# 2. Set up replication (recommended)
# 3. Configure backups
# 4. Set up monitoring
```

### 2. Migration Strategy

```bash
# 1. Backup database
pg_dump sahool_billing_prod > backup_$(date +%Y%m%d_%H%M%S).sql

# 2. Test migrations on staging
export DATABASE_URL="postgresql+asyncpg://user:pass@staging-db/sahool_billing"
alembic upgrade head

# 3. Apply to production
export DATABASE_URL="postgresql+asyncpg://user:pass@prod-db/sahool_billing"
alembic upgrade head

# 4. Verify
curl https://api.sahool.com/billing/healthz
```

### 3. Connection Pooling

For production, use proper connection pooling:

```python
# Configured in src/database.py
POOL_SIZE = 50        # Adjust based on expected load
MAX_OVERFLOW = 100    # Maximum connections
POOL_TIMEOUT = 30     # Wait time for connection
POOL_RECYCLE = 3600   # Recycle connections every hour
```

### 4. Monitoring

Monitor these metrics:
- Active connections
- Query performance
- Database size
- Slow queries
- Lock contention

---

## 🔍 Troubleshooting

### Connection Issues

```bash
# Test database connection
psql -U postgres -d sahool_billing -c "SELECT 1;"

# Check if database exists
psql -U postgres -l | grep sahool_billing

# Verify asyncpg driver
python -c "import asyncpg; print('asyncpg OK')"
```

### Migration Issues

```bash
# Check current migration version
alembic current

# Show pending migrations
alembic history

# Force to specific version (dangerous!)
alembic stamp <revision_id>
```

### Performance Issues

```sql
-- Check slow queries
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check table sizes
SELECT schemaname, tablename,
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;

-- Check indexes
SELECT schemaname, tablename, indexname,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_indexes
WHERE schemaname = 'public';
```

---

## 📚 Additional Resources

- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/)

---

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review application logs
3. Check PostgreSQL logs
4. Contact the development team

---

**Last Updated:** December 27, 2025
**Version:** 15.6.0
