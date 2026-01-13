# Farmer Profile Migration Guide

# دليل ترحيل ملفات المزارعين

This guide explains how to migrate the notification-service from in-memory farmer storage to PostgreSQL.

## Overview | نظرة عامة

**Migration Date:** 2026-01-08

**What Changed:**

- ✅ Farmer profiles now stored in PostgreSQL instead of in-memory dictionary
- ✅ Three new database tables: `farmer_profiles`, `farmer_crops`, `farmer_fields`
- ✅ All endpoints updated to use database operations
- ✅ Proper error handling and connection pooling implemented

## Prerequisites | المتطلبات الأساسية

1. **PostgreSQL Database Running**

   ```bash
   # Check if PostgreSQL is running
   pg_isready

   # Or start it if needed
   sudo systemctl start postgresql
   ```

2. **Database Created**

   ```bash
   # Create database (if not exists)
   createdb sahool_notifications

   # Or using psql
   psql -U postgres -c "CREATE DATABASE sahool_notifications;"
   ```

3. **Environment Variables Set**
   ```bash
   # In .env file or export:
   export DATABASE_URL="postgresql://username:password@localhost:5432/sahool_notifications"
   ```

## Migration Methods | طرق الترحيل

There are three ways to run this migration:

### Method 1: Python Migration Script (Recommended) ⭐

The easiest and safest method:

```bash
# Navigate to notification-service directory
cd apps/services/notification-service

# Run the migration script
python migrate_farmer_profiles.py
```

**What it does:**

- ✅ Connects to PostgreSQL
- ✅ Creates all three tables with proper indexes
- ✅ Verifies tables were created successfully
- ✅ Creates sample test data (optional)
- ✅ Provides detailed logging and error messages

**Rollback:**

```bash
# To undo the migration (drops all farmer tables)
python migrate_farmer_profiles.py --rollback
```

### Method 2: Aerich Migration (ORM-based)

Using Tortoise ORM's migration tool:

```bash
# Initialize Aerich (first time only)
aerich init -t src.database.TORTOISE_ORM_LOCAL

# Initialize database
aerich init-db

# Generate migration
aerich migrate --name add_farmer_profiles

# Apply migration
aerich upgrade
```

**Rollback:**

```bash
# Downgrade to previous migration
aerich downgrade -1
```

### Method 3: Manual SQL Script

If you prefer direct SQL execution:

```bash
# Apply the SQL migration
psql -U postgres -d sahool_notifications -f migrations/farmer_profiles_schema.sql

# Or using environment variable
psql $DATABASE_URL -f migrations/farmer_profiles_schema.sql
```

**Rollback:**

```sql
-- Connect to database
psql sahool_notifications

-- Drop tables in reverse order
DROP TABLE IF EXISTS farmer_fields CASCADE;
DROP TABLE IF EXISTS farmer_crops CASCADE;
DROP TABLE IF EXISTS farmer_profiles CASCADE;
DROP FUNCTION IF EXISTS update_updated_at_column();
```

## Verification | التحقق

After running the migration, verify it succeeded:

### 1. Check Tables Exist

```bash
# Using psql
psql sahool_notifications -c "\dt"

# Should show:
#  farmer_profiles
#  farmer_crops
#  farmer_fields
```

### 2. Check Table Structure

```bash
# Describe farmer_profiles table
psql sahool_notifications -c "\d farmer_profiles"
```

### 3. Test the API

```bash
# Start the service
cd apps/services/notification-service
uvicorn src.main:app --reload --port 8110

# In another terminal, test the register endpoint
curl -X POST http://localhost:8110/v1/farmers/register \
  -H "Content-Type: application/json" \
  -d '{
    "farmer_id": "test-123",
    "name": "Test Farmer",
    "name_ar": "مزارع تجريبي",
    "governorate": "sanaa",
    "crops": ["tomato", "wheat"],
    "field_ids": ["field-001"],
    "phone": "+967771234567",
    "language": "ar"
  }'

# Check health endpoint
curl http://localhost:8110/healthz

# Check stats
curl http://localhost:8110/v1/stats
```

### 4. Verify Data in Database

```bash
# Count farmers
psql sahool_notifications -c "SELECT COUNT(*) FROM farmer_profiles;"

# View all farmers
psql sahool_notifications -c "SELECT farmer_id, name, name_ar, governorate FROM farmer_profiles;"

# View farmer with crops
psql sahool_notifications -c "
SELECT
    fp.farmer_id,
    fp.name_ar,
    fp.governorate,
    fc.crop_type
FROM farmer_profiles fp
LEFT JOIN farmer_crops fc ON fp.id = fc.farmer_id
ORDER BY fp.farmer_id;
"
```

## Database Schema | مخطط قاعدة البيانات

### Tables Created:

#### 1. `farmer_profiles`

Stores main farmer information.

| Column        | Type         | Description              |
| ------------- | ------------ | ------------------------ |
| id            | UUID         | Primary key              |
| tenant_id     | VARCHAR(100) | Multi-tenancy support    |
| farmer_id     | VARCHAR(100) | Unique farmer identifier |
| name          | VARCHAR(255) | Farmer name (English)    |
| name_ar       | VARCHAR(255) | Farmer name (Arabic)     |
| governorate   | VARCHAR(50)  | Governorate location     |
| district      | VARCHAR(100) | District/area            |
| phone         | VARCHAR(20)  | Phone number             |
| email         | VARCHAR(255) | Email address            |
| fcm_token     | VARCHAR(500) | Firebase token for push  |
| language      | VARCHAR(5)   | Preferred language       |
| is_active     | BOOLEAN      | Active status            |
| metadata      | JSONB        | Additional data          |
| created_at    | TIMESTAMP    | Creation timestamp       |
| updated_at    | TIMESTAMP    | Last update timestamp    |
| last_login_at | TIMESTAMP    | Last login time          |

#### 2. `farmer_crops`

Junction table for farmer's crops.

| Column        | Type        | Description                     |
| ------------- | ----------- | ------------------------------- |
| id            | UUID        | Primary key                     |
| farmer_id     | UUID        | FK to farmer_profiles           |
| crop_type     | VARCHAR(50) | Crop type (tomato, wheat, etc.) |
| area_hectares | FLOAT       | Cultivated area                 |
| planting_date | DATE        | Planting date                   |
| harvest_date  | DATE        | Expected harvest                |
| is_active     | BOOLEAN     | Active status                   |
| created_at    | TIMESTAMP   | Creation timestamp              |
| updated_at    | TIMESTAMP   | Last update timestamp           |

#### 3. `farmer_fields`

Junction table for farmer's fields.

| Column     | Type         | Description           |
| ---------- | ------------ | --------------------- |
| id         | UUID         | Primary key           |
| farmer_id  | UUID         | FK to farmer_profiles |
| field_id   | VARCHAR(100) | Field identifier      |
| field_name | VARCHAR(255) | Field name/label      |
| latitude   | FLOAT        | Field latitude        |
| longitude  | FLOAT        | Field longitude       |
| is_active  | BOOLEAN      | Active status         |
| created_at | TIMESTAMP    | Creation timestamp    |
| updated_at | TIMESTAMP    | Last update timestamp |

## Code Changes Summary | ملخص تغييرات الكود

### Files Modified:

1. **`src/models.py`**
   - ✅ Added `FarmerProfile` model
   - ✅ Added `FarmerCrop` model
   - ✅ Added `FarmerField` model

2. **`src/repository.py`**
   - ✅ Added `FarmerProfileRepository` class with CRUD operations
   - ✅ Methods: create, get_by_farmer_id, update, delete, find_by_criteria, etc.

3. **`src/main.py`**
   - ✅ Removed in-memory `FARMER_PROFILES` dictionary
   - ✅ Updated `/v1/farmers/register` endpoint to use database
   - ✅ Updated `determine_recipients_by_criteria()` to query database
   - ✅ Updated all `send_*_notification()` functions to use database
   - ✅ Updated `/healthz` endpoint to show database farmer count
   - ✅ Updated `/v1/stats` endpoint to query database

### New Files Created:

1. **`migrate_farmer_profiles.py`**
   - Migration script with rollback support
   - Creates tables and sample data
   - Comprehensive error handling

2. **`migrations/farmer_profiles_schema.sql`**
   - Manual SQL migration script
   - Includes indexes and triggers
   - Rollback instructions included

3. **`MIGRATION_GUIDE.md`**
   - This comprehensive migration guide

## Troubleshooting | استكشاف الأخطاء

### Issue: "DATABASE_URL not set"

```bash
# Solution: Set the environment variable
export DATABASE_URL="postgresql://user:password@localhost:5432/sahool_notifications"

# Or add to .env file
echo 'DATABASE_URL=postgresql://user:password@localhost:5432/sahool_notifications' >> .env
```

### Issue: "Connection refused"

```bash
# Check if PostgreSQL is running
pg_isready

# Start PostgreSQL
sudo systemctl start postgresql

# Check the port (default 5432)
sudo netstat -plnt | grep postgres
```

### Issue: "Database does not exist"

```bash
# Create the database
createdb sahool_notifications

# Or using psql
psql -U postgres -c "CREATE DATABASE sahool_notifications;"
```

### Issue: "Tables already exist"

If you get a "table already exists" error:

```bash
# Option 1: Drop and recreate
psql sahool_notifications -c "DROP TABLE IF EXISTS farmer_fields, farmer_crops, farmer_profiles CASCADE;"
python migrate_farmer_profiles.py

# Option 2: Use rollback then migrate
python migrate_farmer_profiles.py --rollback
python migrate_farmer_profiles.py
```

### Issue: Migration script fails

```bash
# Check Python path
which python
python --version  # Should be 3.11+

# Check dependencies
pip install -r requirements.txt

# Run with verbose logging
python -u migrate_farmer_profiles.py
```

## Performance Considerations | اعتبارات الأداء

The new database implementation includes:

1. **Indexes** on frequently queried columns:
   - `farmer_id` (unique, indexed)
   - `governorate` (indexed)
   - `tenant_id` (indexed)
   - Composite indexes for common queries

2. **Connection Pooling** via Tortoise ORM:
   - Configured in `database.py`
   - Automatic connection management
   - Async support for concurrent requests

3. **Query Optimization**:
   - `prefetch_related()` for crops and fields
   - Batch operations for bulk inserts
   - Efficient JOIN queries

4. **Caching Recommendations**:
   - Consider Redis for frequently accessed farmer profiles
   - Cache farmer counts and stats
   - Implement query result caching for broadcast notifications

## Next Steps | الخطوات التالية

After successful migration:

1. **Monitor Performance**

   ```bash
   # Check query performance
   psql sahool_notifications -c "SELECT * FROM pg_stat_statements ORDER BY total_time DESC LIMIT 10;"
   ```

2. **Set up Backups**

   ```bash
   # Create backup
   pg_dump sahool_notifications > backup_$(date +%Y%m%d).sql

   # Restore backup
   psql sahool_notifications < backup_20260108.sql
   ```

3. **Configure Auto-vacuum**

   ```sql
   ALTER TABLE farmer_profiles SET (autovacuum_vacuum_scale_factor = 0.1);
   ALTER TABLE farmer_crops SET (autovacuum_vacuum_scale_factor = 0.1);
   ALTER TABLE farmer_fields SET (autovacuum_vacuum_scale_factor = 0.1);
   ```

4. **Set up Monitoring**
   - Monitor database connections
   - Track query performance
   - Set up alerts for database errors

## Support | الدعم

If you encounter issues:

1. Check the logs in the notification service
2. Review PostgreSQL logs: `tail -f /var/log/postgresql/postgresql-*.log`
3. Check database connectivity: `psql $DATABASE_URL`
4. Verify environment variables: `printenv | grep DATABASE`

## Migration Completed! ✅

You have successfully migrated the notification-service farmer profiles to PostgreSQL!

The service now has:

- ✅ Persistent farmer data storage
- ✅ Proper database schema with relationships
- ✅ Indexed queries for performance
- ✅ Error handling and connection pooling
- ✅ Migration and rollback scripts

## تم إكمال الترحيل بنجاح! ✅

تم ترحيل ملفات المزارعين إلى PostgreSQL بنجاح!
