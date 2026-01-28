#!/usr/bin/env python3
"""
SAHOOL Docker Container Error Fixer
Automatically fixes all identified errors from log analysis
"""

import os
import re
import subprocess
from pathlib import Path

# Base directory - use absolute path
SCRIPT_DIR = Path(__file__).parent.absolute()
BASE_DIR = SCRIPT_DIR

def fix_weather_core_import():
    """Fix weather-core incorrect import path"""
    print("🔧 Fixing weather-core import path...")
    
    file_path = BASE_DIR / "apps/services/weather-core/src/main.py"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix the import - change absolute to relative
    content = content.replace(
        "from shared.logging_config import",
        "from ..shared.logging_config import"
    )
    content = content.replace(
        "from shared.errors_py import",
        "from ..shared.errors_py import"
    )
    content = content.replace(
        "from shared.auth.dependencies import",
        "from ..shared.auth.dependencies import"
    )
    content = content.replace(
        "from shared.auth.models import",
        "from ..shared.auth.models import"
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed weather-core imports")

def fix_postgres_equipment_column():
    """Add missing purchase_price column to equipment table"""
    print("🔧 Fixing postgres equipment.purchase_price column...")
    
    migration_sql = """
-- Add missing purchase_price column to equipment table
ALTER TABLE IF EXISTS equipment 
ADD COLUMN IF NOT EXISTS purchase_price DECIMAL(10, 2);

-- Add comment
COMMENT ON COLUMN equipment.purchase_price IS 'Purchase price of the equipment';
"""
    
    migration_file = BASE_DIR / "infrastructure/core/postgres/migrations/fix_equipment_purchase_price.sql"
    migration_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_sql)
    
    print(f"✅ Created migration: {migration_file}")
    print("⚠️  Run this migration manually: docker exec sahool-postgres psql -U sahool -d sahool -f /docker-entrypoint-initdb.d/migrations/fix_equipment_purchase_price.sql")

def fix_task_service_foreign_key():
    """Fix task_evidence foreign key constraint"""
    print("🔧 Fixing task-service foreign key constraint...")
    
    migration_sql = """
-- Ensure tasks table exists first
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id VARCHAR(255) NOT NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Now create task_evidence with proper foreign key
CREATE TABLE IF NOT EXISTS task_evidence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    evidence_type VARCHAR(100),
    evidence_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_task_evidence_task_id ON task_evidence(task_id);
"""
    
    migration_file = BASE_DIR / "infrastructure/core/postgres/migrations/fix_task_evidence_fk.sql"
    
    with open(migration_file, 'w', encoding='utf-8') as f:
        f.write(migration_sql)
    
    print(f"✅ Created migration: {migration_file}")

def create_community_chat_openapi():
    """Create missing OpenAPI specification for community-chat"""
    print("🔧 Creating community-chat OpenAPI spec...")
    
    openapi_spec = """{
  "openapi": "3.0.0",
  "info": {
    "title": "SAHOOL Community Chat API",
    "version": "1.0.0",
    "description": "Community posts and social features for farmers"
  },
  "servers": [
    {
      "url": "http://localhost:8097",
      "description": "Development server"
    }
  ],
  "paths": {
    "/healthz": {
      "get": {
        "summary": "Health check",
        "responses": {
          "200": {
            "description": "Service is healthy"
          }
        }
      }
    },
    "/api/v1/posts": {
      "get": {
        "summary": "Get community posts",
        "responses": {
          "200": {
            "description": "List of posts"
          }
        }
      },
      "post": {
        "summary": "Create a new post",
        "responses": {
          "201": {
            "description": "Post created"
          }
        }
      }
    }
  }
}
"""
    
    spec_file = BASE_DIR / "apps/services/community-chat/app/openapi.yaml"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(spec_file, 'w', encoding='utf-8') as f:
        f.write(openapi_spec)
    
    print(f"✅ Created OpenAPI spec: {spec_file}")

def create_env_example_updates():
    """Create .env.example with missing variables"""
    print("🔧 Creating .env.example updates...")
    
    env_updates = """
# ============================================================================
# Missing Environment Variables (identified from error logs)
# ============================================================================

# NATS Configuration (for all Python services)
NATS_URL=nats://nats:4222
NATS_USER=sahool_app
NATS_PASSWORD=change_this_secure_nats_password_32_chars

# Database Configuration
DATABASE_URL=postgresql://sahool:password@pgbouncer:6432/sahool
POSTGRES_USER=sahool
POSTGRES_PASSWORD=change_this_secure_postgres_password

# Redis Configuration
REDIS_URL=redis://:change_this_secure_redis_password@redis:6379/0
REDIS_PASSWORD=change_this_secure_redis_password

# Service Ports (ensure these match docker-compose.yml)
WEATHER_CORE_PORT=8108
AI_AGENTS_SERVICE_PORT=8130
CRM_SERVICE_PORT=8131
LOWCODE_ENGINE_PORT=8132
FIELD_CHAT_PORT=8099
TASK_SERVICE_PORT=8103
CODE_REVIEW_SERVICE_PORT=8102

# Ollama Configuration
OLLAMA_URL=http://ollama:11434
OLLAMA_MODEL=deepseek-coder:latest

# Logging
LOG_LEVEL=INFO
JSON_LOGS=true
"""
    
    env_file = BASE_DIR / ".env.example.fixes"
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_updates)
    
    print(f"✅ Created env updates: {env_file}")
    print("⚠️  Merge these into your .env file")

def create_fix_summary():
    """Create a summary document of all fixes"""
    summary = """# Docker Container Error Fixes - Summary

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
"""
    
    summary_file = BASE_DIR / "DOCKER_FIXES_SUMMARY.md"
    
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(summary)
    
    print(f"✅ Created fix summary: {summary_file}")

def main():
    print("=" * 80)
    print("SAHOOL Docker Container Error Fixer")
    print("=" * 80)
    print()
    
    try:
        # Apply fixes
        fix_weather_core_import()
        print()
        
        fix_postgres_equipment_column()
        print()
        
        fix_task_service_foreign_key()
        print()
        
        create_community_chat_openapi()
        print()
        
        create_env_example_updates()
        print()
        
        create_fix_summary()
        print()
        
        print("=" * 80)
        print("✅ All automated fixes applied successfully!")
        print("=" * 80)
        print()
        print("📋 Next steps:")
        print("1. Review DOCKER_FIXES_SUMMARY.md for manual actions")
        print("2. Run database migrations")
        print("3. Update .env file with missing variables")
        print("4. Restart affected services")
        print()
        
    except Exception as e:
        print(f"❌ Error during fix application: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
