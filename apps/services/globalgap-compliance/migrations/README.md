# GlobalGAP Compliance Database Migrations

# ترحيلات قاعدة بيانات الامتثال لـ GlobalGAP

This directory contains SQL migrations for the GlobalGAP Compliance tracking system.

يحتوي هذا الدليل على ترحيلات SQL لنظام تتبع الامتثال لـ GlobalGAP.

## Migration Files

### 001_initial_schema.sql
**Initial database schema creation**
**إنشاء مخطط قاعدة البيانات الأولي**

Creates the following tables:
- `globalgap_registrations` - Farm GlobalGAP registrations and certifications
- `compliance_records` - Audit results and compliance scores
- `checklist_responses` - Individual checklist item responses
- `non_conformances` - Non-conformances and corrective actions

ينشئ الجداول التالية:
- `globalgap_registrations` - تسجيلات وشهادات GlobalGAP للمزارع
- `compliance_records` - نتائج التدقيق ودرجات الامتثال
- `checklist_responses` - استجابات عناصر قائمة التحقق الفردية
- `non_conformances` - عدم المطابقات والإجراءات التصحيحية

### 002_add_indexes.sql
**Performance indexes for efficient querying**
**فهارس الأداء للاستعلام الفعال**

Adds indexes for:
- Fast lookups by farm, GGN, and status
- Chronological queries by audit dates
- Filtering by compliance scores
- Non-conformance tracking

يضيف فهارس لـ:
- البحث السريع حسب المزرعة، GGN، والحالة
- الاستعلامات الزمنية حسب تواريخ التدقيق
- التصفية حسب درجات الامتثال
- تتبع عدم المطابقات

## Running Migrations

### Using psql

```bash
# Set database connection
export DATABASE_URL="postgresql://user:password@host:port/database"

# Run migrations in order
psql $DATABASE_URL -f migrations/001_initial_schema.sql
psql $DATABASE_URL -f migrations/002_add_indexes.sql
```

### Using Python asyncpg

```python
import asyncpg
import asyncio

async def run_migrations():
    conn = await asyncpg.connect('postgresql://user:password@host:port/database')

    # Read and execute migration files
    with open('migrations/001_initial_schema.sql', 'r') as f:
        await conn.execute(f.read())

    with open('migrations/002_add_indexes.sql', 'r') as f:
        await conn.execute(f.read())

    await conn.close()

asyncio.run(run_migrations())
```

## Database Schema Overview

### Entity Relationships

```
globalgap_registrations (1) ──→ (*) compliance_records
                                      │
                                      ├─→ (*) checklist_responses
                                      │
                                      └─→ (*) non_conformances
```

### Key Features

1. **UUID Primary Keys**: All tables use UUID for primary keys
2. **Cascade Deletes**: Deleting a registration cascades to all related records
3. **Check Constraints**: Ensures data integrity (scores 0-100%, valid dates, etc.)
4. **Automatic Timestamps**: Auto-updating `updated_at` field for registrations
5. **Performance Indexes**: Comprehensive indexes for common query patterns
6. **Bilingual Comments**: All schema elements have English and Arabic descriptions

### Certificate Status Values
- `ACTIVE` - Active certificate
- `SUSPENDED` - Suspended certificate
- `EXPIRED` - Expired certificate
- `WITHDRAWN` - Withdrawn certificate
- `PENDING` - Pending registration

### Response Values
- `COMPLIANT` - Item is compliant
- `NON_COMPLIANT` - Item is not compliant
- `NOT_APPLICABLE` - Item is not applicable
- `RECOMMENDATION` - Recommended improvement

### Non-Conformance Severity
- `MAJOR` - Major non-conformance
- `MINOR` - Minor non-conformance
- `RECOMMENDATION` - Recommendation for improvement

### Non-Conformance Status
- `OPEN` - Open issue
- `IN_PROGRESS` - Corrective action in progress
- `RESOLVED` - Issue resolved
- `VERIFIED` - Resolution verified

## Usage with Repository Classes

The `src/database.py` module provides repository classes for easy database access:

```python
from src.database import (
    registrations_repo,
    compliance_repo,
    checklist_repo,
    non_conformance_repo,
    init_db
)

# Initialize database connection pool
await init_db()

# Create a new registration
registration = await registrations_repo.create(
    farm_id=farm_uuid,
    ggn="4052852000000",
    certificate_status="ACTIVE",
    scope="FRUIT_VEGETABLES"
)

# Create compliance record
compliance = await compliance_repo.create(
    registration_id=registration['id'],
    checklist_version="6.0",
    audit_date=date.today(),
    overall_compliance=95.5
)

# Get active registrations
active = await registrations_repo.get_active_registrations()

# Get expiring certificates
expiring = await registrations_repo.get_expiring_soon(days=30)
```

## Database Backup

### Backup Command
```bash
pg_dump -h host -U user -d sahool_globalgap -F c -f backup_$(date +%Y%m%d).dump
```

### Restore Command
```bash
pg_restore -h host -U user -d sahool_globalgap -c backup_20231228.dump
```

## Maintenance

### Analyze Tables
Run after bulk inserts or updates:
```sql
ANALYZE globalgap_registrations;
ANALYZE compliance_records;
ANALYZE checklist_responses;
ANALYZE non_conformances;
```

### Vacuum Tables
Reclaim space and update statistics:
```sql
VACUUM ANALYZE globalgap_registrations;
VACUUM ANALYZE compliance_records;
VACUUM ANALYZE checklist_responses;
VACUUM ANALYZE non_conformances;
```

## Monitoring

Check table sizes:
```sql
SELECT
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE tablename IN (
    'globalgap_registrations',
    'compliance_records',
    'checklist_responses',
    'non_conformances'
)
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

## Version History

- **1.0.0** (2025-12-28): Initial schema with registrations, compliance records, checklist responses, and non-conformances
