# Service Code Fixes Required
# إصلاحات الكود المطلوبة للخدمات

---

## 1. marketplace-service - NATS URL Parsing

**File:** `apps/services/marketplace-service/src/events/events.service.ts`
**Line:** ~151

### Current Code (Broken)
```typescript
const nc = await connect({
  servers: process.env.NATS_URL || "nats://localhost:4222",
});
```

### Fixed Code
```typescript
const parseNatsUrl = (url: string) => {
  const parsed = new URL(url);
  return {
    servers: `${parsed.protocol}//${parsed.host}`,
    user: parsed.username || undefined,
    pass: parsed.password || undefined,
  };
};

const natsConfig = process.env.NATS_URL
  ? parseNatsUrl(process.env.NATS_URL)
  : { servers: "nats://localhost:4222" };

const nc = await connect(natsConfig);
```

### Alternative (Use Separate Env Vars)
```typescript
const nc = await connect({
  servers: process.env.NATS_SERVERS || "nats://nats:4222",
  user: process.env.NATS_USER,
  pass: process.env.NATS_PASSWORD,
});
```

---

## 2. virtual-sensors - Add NATS Dependency

**File:** `apps/services/virtual-sensors/requirements.txt`

### Add
```
nats-py>=2.7.0
```

---

## 3. field-chat - Fix Database Connection

**File:** `apps/services/field-chat/src/main.py` or `src/database.py`

### Issue
The service doesn't recognize `postgresql://` scheme - it requires `postgresql+asyncpg://` for async operations.

### Fix in docker-compose.yml
```yaml
environment:
  - DATABASE_URL=postgresql+asyncpg://${POSTGRES_USER}:${POSTGRES_PASSWORD}@pgbouncer:6432/${POSTGRES_DB}?ssl=disable
```

### Alternative: Fix in Code
```python
import os

db_url = os.getenv("DATABASE_URL", "")
# Convert postgresql:// to postgresql+asyncpg:// if needed
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)
```

---

## 4. equipment-service - Schema Migration

**File:** Database migration

### Issue
```
ERROR: column equipment.equipment_id does not exist at character 42
```

### Fix
Run missing database migration:
```bash
docker compose exec equipment-service python -m alembic upgrade head
# OR
docker compose exec equipment-service prisma migrate deploy
```

---

## 5. ai-agents-service - Graceful NATS Fallback

**File:** `apps/services/ai-agents-service/src/main.py`
**Lines:** ~277-290

### Current Code
```python
try:
    from shared.events.publisher import get_publisher
    app.state.publisher = await get_publisher(...)
except Exception as e:
    print(f"⚠️ NATS connection failed: {e}")
```

### Improved Code
```python
async def setup_nats(app: FastAPI, max_retries: int = 5):
    """Setup NATS with exponential backoff."""
    nats_url = os.getenv("NATS_URL")
    if not nats_url:
        logger.warning("NATS_URL not configured - running without event publishing")
        app.state.publisher = None
        return

    for attempt in range(max_retries):
        try:
            from shared.events.publisher import get_publisher
            app.state.publisher = await get_publisher(...)
            logger.info("NATS connected successfully")
            return
        except Exception as e:
            wait_time = 2 ** attempt
            logger.warning(f"NATS connection attempt {attempt+1}/{max_retries} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(wait_time)

    logger.error("Failed to connect to NATS after all retries")
    app.state.publisher = None
```

---

## 6. Python Services - Unified Database Connection Pattern

**Recommended Pattern for All Python Services**

```python
import os
from urllib.parse import urlparse, parse_qs, urlencode

def get_database_url() -> str:
    """Get database URL with SSL mode handling for PgBouncer."""
    db_url = os.getenv("DATABASE_URL", "")

    if not db_url:
        raise ValueError("DATABASE_URL not configured")

    parsed = urlparse(db_url)
    query_params = parse_qs(parsed.query)

    # Ensure SSL is disabled for PgBouncer in development
    if "pgbouncer" in parsed.netloc:
        if "sslmode" not in query_params and "ssl" not in query_params:
            query_params["sslmode"] = ["disable"]

    # Rebuild URL with updated query
    new_query = urlencode(query_params, doseq=True)
    new_url = parsed._replace(query=new_query).geturl()

    return new_url
```

---

## 7. Node.js Services - Unified Database Connection Pattern

**Recommended Pattern for Prisma Services**

```typescript
// lib/database.ts
import { PrismaClient } from '@prisma/client';

function getDatabaseUrl(): string {
  let url = process.env.DATABASE_URL || '';

  // Ensure SSL is disabled for PgBouncer in development
  if (url.includes('pgbouncer') && !url.includes('sslmode=')) {
    const separator = url.includes('?') ? '&' : '?';
    url = `${url}${separator}sslmode=disable`;
  }

  return url;
}

export const prisma = new PrismaClient({
  datasources: {
    db: {
      url: getDatabaseUrl(),
    },
  },
});
```

---

## Summary of Required Changes

| Service | File | Change Type | Priority |
|---------|------|-------------|----------|
| marketplace-service | events.service.ts | NATS URL parsing | CRITICAL |
| virtual-sensors | requirements.txt | Add nats-py | HIGH |
| field-chat | docker-compose.yml OR code | DB scheme fix | CRITICAL |
| equipment-service | Database migration | Run migration | CRITICAL |
| ai-agents-service | main.py | Improved retry logic | MEDIUM |
| All Python services | Shared pattern | DB URL handling | MEDIUM |
| All Node.js services | Shared pattern | DB URL handling | MEDIUM |

---

## Testing After Fixes

```bash
# 1. Rebuild affected services
docker compose build marketplace-service virtual-sensors field-chat ai-agents-service

# 2. Stop and restart with fresh volumes for testing
docker compose down
docker compose up -d postgres pgbouncer redis nats

# 3. Wait for infrastructure
sleep 30

# 4. Start services
docker compose up -d

# 5. Check logs for errors
docker compose logs --tail=50 marketplace-service | grep -i error
docker compose logs --tail=50 ai-agents-service | grep -i error
docker compose logs --tail=50 field-chat | grep -i error

# 6. Verify health
docker compose ps --format "table {{.Name}}\t{{.Status}}"
```
