# Docker Container Error Fixes - Summary

## Fixes Applied

### 1. ✅ weather-core - Import Path Fix
**Error**: `ModuleNotFoundError: No module named 'shared'`
**Fix**: Changed absolute imports to relative imports in `weather-core/src/main.py`
- `from shared.logging_config` → `from ..shared.logging_config`
- `from shared.errors_py` → `from ..shared.errors_py`
- `from shared.auth.*` → `from ..shared.auth.*`

### 2. ✅ postgres - Missing Column Fix
**Error**: `column equipment.purchase_price does not exist`
**Fix**: Created migration `fix_equipment_purchase_price.sql`
**Action Required**: Run migration manually:
```bash
docker exec sahool-postgres psql -U sahool -d sahool -f /docker-entrypoint-initdb.d/migrations/fix_equipment_purchase_price.sql
```

### 3. ✅ task-service - Foreign Key Constraint Fix
**Error**: `foreign key constraint violation on task_evidence.task_id`
**Fix**: Created migration `fix_task_evidence_fk.sql` to ensure `tasks` table exists before `task_evidence`
**Action Required**: Run migration manually

### 4. ✅ community-chat - Missing OpenAPI Spec
**Error**: `ENOENT: no such file or directory, open 'app/openapi.yaml'`
**Fix**: Created `community-chat/app/openapi.yaml` with basic API specification

### 5. ⚠️ NATS Configuration Issues (Multiple Services)
**Services Affected**: ai-agents-service, lowcode-engine, crm-service
**Error**: `Client.connect() got an unexpected keyword argument 'max_pending_size'`
**Root Cause**: Outdated NATS client usage or incorrect configuration
**Fix Required**: Update NATS client connections in these services

### 6. ✅ Environment Variables
**Fix**: Created `.env.example.fixes` with all missing environment variables
**Action Required**: Merge into your `.env` file

## Services Status After Fixes

### ✅ Fixed (Ready to Restart)
- weather-core
- community-chat

### ⚠️ Requires Manual Migration
- postgres (equipment table)
- task-service (foreign key)

### 🔍 Requires Code Review
- ai-agents-service (NATS config)
- lowcode-engine (NATS config)
- crm-service (NATS config)
- field-chat (database connection string)
- code-review-service (aiohttp connector cleanup)
- field-management-service (GeoJSON validation)
- marketplace-service (configuration)
- ollama (database connection)

## Next Steps

1. **Restart Fixed Services**:
   ```bash
   docker-compose restart weather-core community-chat
   ```

2. **Run Database Migrations**:
   ```bash
   # Copy migrations to postgres container
   docker cp infrastructure/core/postgres/migrations/fix_equipment_purchase_price.sql sahool-postgres:/tmp/
   docker cp infrastructure/core/postgres/migrations/fix_task_evidence_fk.sql sahool-postgres:/tmp/
   
   # Run migrations
   docker exec sahool-postgres psql -U sahool -d sahool -f /tmp/fix_equipment_purchase_price.sql
   docker exec sahool-postgres psql -U sahool -d sahool -f /tmp/fix_task_evidence_fk.sql
   ```

3. **Update Environment Variables**:
   ```bash
   # Merge .env.example.fixes into .env
   cat .env.example.fixes >> .env
   # Then edit .env to set proper passwords
   ```

4. **Review NATS Configuration**:
   - Check NATS client version in affected services
   - Remove `max_pending_size` parameter if present
   - Ensure NATS_URL, NATS_USER, NATS_PASSWORD are set correctly

5. **Full System Restart**:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Verification

After applying fixes, run the log analyzer again:
```bash
python analyze_logs.py
```

Expected result: Reduced error count, especially for weather-core, community-chat, postgres, and task-service.
