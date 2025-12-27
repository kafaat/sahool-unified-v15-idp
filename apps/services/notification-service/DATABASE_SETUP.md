# SAHOOL Notification Service - Database Setup Guide
# دليل إعداد قاعدة البيانات لخدمة الإشعارات

## Overview | نظرة عامة

This service uses PostgreSQL with Tortoise ORM for storing notifications, templates, and user preferences.

تستخدم هذه الخدمة PostgreSQL مع Tortoise ORM لتخزين الإشعارات والقوالب وتفضيلات المستخدم.

## Prerequisites | المتطلبات الأساسية

1. PostgreSQL 13 or higher
2. Python 3.9 or higher
3. pip or poetry package manager

## Quick Start | البداية السريعة

### 1. Install Dependencies | تثبيت المكتبات

```bash
cd apps/services/notification-service
pip install -r requirements.txt
```

### 2. Create PostgreSQL Database | إنشاء قاعدة البيانات

```bash
# Login to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE sahool_notifications;
CREATE USER sahool WITH PASSWORD 'sahool123';
GRANT ALL PRIVILEGES ON DATABASE sahool_notifications TO sahool;

# Exit
\q
```

### 3. Configure Environment | تهيئة البيئة

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and update DATABASE_URL if needed
nano .env
```

### 4. Initialize Database with Aerich | تهيئة قاعدة البيانات باستخدام Aerich

```bash
# Initialize Aerich (first time only)
aerich init -t src.database.TORTOISE_ORM

# Initialize database
aerich init-db

# This will create all tables based on the models
```

### 5. Run Migrations (For updates) | تشغيل الترحيلات (للتحديثات)

```bash
# After making changes to models, create a new migration
aerich migrate --name "description_of_changes"

# Apply migrations
aerich upgrade
```

## Database Schema | مخطط قاعدة البيانات

### Tables | الجداول

#### 1. notifications
Stores all notifications sent to users.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | VARCHAR(100) | Multi-tenancy support |
| user_id | VARCHAR(100) | Farmer/User ID |
| title | VARCHAR(255) | Notification title (English) |
| title_ar | VARCHAR(255) | Notification title (Arabic) |
| body | TEXT | Notification body (English) |
| body_ar | TEXT | Notification body (Arabic) |
| type | VARCHAR(50) | Type: weather_alert, pest_outbreak, etc. |
| priority | VARCHAR(20) | Priority: low, medium, high, critical |
| channel | VARCHAR(20) | Channel: push, sms, in_app |
| status | VARCHAR(20) | Status: pending, sent, failed, read |
| sent_at | TIMESTAMP | When notification was sent |
| read_at | TIMESTAMP | When user read the notification |
| data | JSON | Additional metadata |
| action_url | VARCHAR(500) | Deep link or action URL |
| target_governorates | JSON | List of target governorates |
| target_crops | JSON | List of target crops |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |
| expires_at | TIMESTAMP | Expiration timestamp |

#### 2. notification_templates
Reusable templates for common notifications.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | VARCHAR(100) | Multi-tenancy support |
| name | VARCHAR(100) | Template name/slug (unique) |
| description | VARCHAR(255) | Template description |
| title_template | VARCHAR(255) | Title with {{variables}} |
| title_template_ar | VARCHAR(255) | Arabic title template |
| body_template | TEXT | Body with {{variables}} |
| body_template_ar | TEXT | Arabic body template |
| type | VARCHAR(50) | Default notification type |
| priority | VARCHAR(20) | Default priority |
| channel | VARCHAR(20) | Default channel |
| variables | JSON | Available variables |
| default_data | JSON | Default data |
| is_active | BOOLEAN | Active status |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

#### 3. notification_preferences
User preferences for receiving notifications.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| tenant_id | VARCHAR(100) | Multi-tenancy support |
| user_id | VARCHAR(100) | Farmer/User ID |
| channel | VARCHAR(20) | Channel: push, sms, in_app |
| enabled | BOOLEAN | Is channel enabled |
| quiet_hours_start | TIME | Quiet hours start (e.g., 22:00) |
| quiet_hours_end | TIME | Quiet hours end (e.g., 06:00) |
| notification_types | JSON | Type-specific preferences |
| min_priority | VARCHAR(20) | Minimum priority to receive |
| device_tokens | JSON | FCM/APNS device tokens |
| language | VARCHAR(10) | Preferred language (ar, en) |
| timezone | VARCHAR(50) | User timezone |
| created_at | TIMESTAMP | Creation timestamp |
| updated_at | TIMESTAMP | Last update timestamp |

**Unique constraint:** (user_id, channel)

#### 4. notification_logs
Tracks delivery attempts and status.

| Column | Type | Description |
|--------|------|-------------|
| id | UUID | Primary key |
| notification_id | UUID | Foreign key to notifications |
| channel | VARCHAR(20) | Channel used for delivery |
| status | VARCHAR(20) | Status: success, failed, pending, retry |
| error_message | TEXT | Error message if failed |
| error_code | VARCHAR(50) | Error code |
| provider_response | JSON | Response from FCM, SMS gateway, etc. |
| provider_message_id | VARCHAR(255) | Message ID from provider |
| retry_count | INTEGER | Number of retry attempts |
| next_retry_at | TIMESTAMP | When to retry next |
| attempted_at | TIMESTAMP | Attempt timestamp |
| completed_at | TIMESTAMP | Completion timestamp |

## Development Mode | وضع التطوير

For quick development, you can auto-create schemas:

```bash
# Set in .env
CREATE_DB_SCHEMA=true

# Start the service (it will create tables automatically)
python src/main.py
```

**⚠️ WARNING:** Never use `CREATE_DB_SCHEMA=true` in production! Always use Aerich migrations.

## Production Setup | إعداد الإنتاج

### 1. Use Aerich Migrations

```bash
# Never set CREATE_DB_SCHEMA in production
CREATE_DB_SCHEMA=false

# Use migrations instead
aerich upgrade
```

### 2. Database Connection Pooling

Update DATABASE_URL with connection pool parameters:

```
DATABASE_URL=postgres://user:pass@host:5432/db?min_size=10&max_size=20
```

### 3. Backup Strategy

```bash
# Backup database
pg_dump -U sahool sahool_notifications > backup.sql

# Restore database
psql -U sahool sahool_notifications < backup.sql
```

## Common Operations | العمليات الشائعة

### Check Database Connection

```bash
python -c "from src.database import wait_for_db; import asyncio; asyncio.run(wait_for_db())"
```

### Run Database Health Check

```bash
cd src
python database.py
```

### Reset Database (Development Only!)

```bash
# Drop all tables
aerich downgrade

# Recreate tables
aerich upgrade
```

### View Migration History

```bash
aerich history
```

### Rollback Migration

```bash
aerich downgrade
```

## Indexes | الفهارس

The following indexes are created for performance:

- `(user_id, status)` - Fast user notification queries
- `(user_id, created_at)` - User notifications sorted by date
- `(type, created_at)` - Type-based queries
- `(tenant_id, user_id)` - Multi-tenant queries
- `(status, attempted_at)` on logs - Failed delivery queries

## Performance Tips | نصائح الأداء

1. **Partitioning**: Consider partitioning `notifications` table by `created_at` for large datasets
2. **Archiving**: Archive old notifications (>30 days) to separate table
3. **Indexes**: Add custom indexes based on query patterns
4. **Connection Pooling**: Use appropriate pool size for your load

## Troubleshooting | حل المشاكل

### Connection Refused

```bash
# Check PostgreSQL is running
systemctl status postgresql

# Check DATABASE_URL is correct
echo $DATABASE_URL
```

### Permission Denied

```bash
# Grant permissions
psql -U postgres
GRANT ALL PRIVILEGES ON DATABASE sahool_notifications TO sahool;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO sahool;
```

### Migration Conflicts

```bash
# View current migration
aerich history

# Rollback problematic migration
aerich downgrade

# Fix models and recreate migration
aerich migrate --name "fix_migration"
```

## Support | الدعم

For issues or questions:
- Check logs: `tail -f logs/notification-service.log`
- Database logs: `tail -f /var/log/postgresql/postgresql-13-main.log`
- GitHub Issues: https://github.com/your-org/sahool/issues

---

**Created by:** SAHOOL Development Team
**Last Updated:** December 2025
**Version:** 15.4.0
