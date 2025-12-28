# Redis Sentinel Integration Guide
# دليل التكامل مع Redis Sentinel

## دمج Redis Sentinel مع الخدمات الحالية | Integrating with Existing Services

### 1. تحديث متغيرات البيئة | Update Environment Variables

أضف المتغيرات التالية إلى ملف `.env` الرئيسي:

```bash
# Redis Sentinel Configuration
REDIS_PASSWORD=your_secure_password_here
REDIS_MASTER_NAME=sahool-master
REDIS_SENTINEL_HOST_1=localhost
REDIS_SENTINEL_HOST_2=localhost
REDIS_SENTINEL_HOST_3=localhost
REDIS_DB=0
REDIS_MAX_CONNECTIONS=50
```

---

### 2. Python Services Integration

#### Option A: Using Existing Code

إذا كان لديك كود يستخدم Redis بالفعل:

**قبل:**
```python
import redis

# Old way
redis_client = redis.Redis(
    host='localhost',
    port=6379,
    password='password',
    db=0
)
```

**بعد:**
```python
from shared.cache import get_redis_client

# New way with Sentinel
redis_client = get_redis_client()
```

#### Option B: Gradual Migration

للانتقال التدريجي، يمكنك استخدام feature flag:

```python
import os
from shared.cache import get_redis_client
import redis

def get_cache_client():
    """Get Redis client with Sentinel support if enabled"""
    use_sentinel = os.getenv('USE_REDIS_SENTINEL', 'false').lower() == 'true'
    
    if use_sentinel:
        return get_redis_client()
    else:
        # Fallback to standalone Redis
        return redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            password=os.getenv('REDIS_PASSWORD'),
            db=int(os.getenv('REDIS_DB', 0))
        )
```

---

### 3. TypeScript/Node.js Services Integration

#### NestJS Integration

**shared/cache/redis.module.ts:**
```typescript
import { Module, Global } from '@nestjs/common';
import { getRedisSentinelClient } from './redis-sentinel';

@Global()
@Module({
  providers: [
    {
      provide: 'REDIS_CLIENT',
      useFactory: () => getRedisSentinelClient(),
    },
  ],
  exports: ['REDIS_CLIENT'],
})
export class RedisModule {}
```

**Usage in services:**
```typescript
import { Injectable, Inject } from '@nestjs/common';
import { RedisSentinelClient } from '@sahool/cache';

@Injectable()
export class CacheService {
  constructor(
    @Inject('REDIS_CLIENT')
    private readonly redis: RedisSentinelClient,
  ) {}

  async get(key: string): Promise<string | null> {
    return this.redis.get(key, true);
  }

  async set(key: string, value: string, ttl?: number): Promise<void> {
    await this.redis.set(key, value, ttl ? { ex: ttl } : undefined);
  }
}
```

#### Express Integration

```typescript
import express from 'express';
import { getRedisSentinelClient } from '@sahool/cache';

const app = express();
const redis = getRedisSentinelClient();

// Middleware for session
app.use(async (req, res, next) => {
  const sessionId = req.headers['x-session-id'];
  if (sessionId) {
    const session = await redis.get(`session:${sessionId}`);
    if (session) {
      req.session = JSON.parse(session);
    }
  }
  next();
});
```

---

### 4. FastAPI Integration (Python)

**app/core/redis.py:**
```python
from fastapi import FastAPI
from shared.cache import get_redis_client, close_redis_client

def init_redis(app: FastAPI):
    """Initialize Redis Sentinel client"""
    
    @app.on_event("startup")
    async def startup():
        app.state.redis = get_redis_client()
        print("✓ Redis Sentinel connected")
    
    @app.on_event("shutdown")
    async def shutdown():
        close_redis_client()
        print("✓ Redis Sentinel disconnected")
```

**Usage:**
```python
from fastapi import FastAPI, Depends, Request

app = FastAPI()
init_redis(app)

def get_redis(request: Request):
    return request.app.state.redis

@app.get("/users/{user_id}")
async def get_user(
    user_id: int,
    redis = Depends(get_redis)
):
    # Try cache first
    cached = redis.get(f"user:{user_id}", use_slave=True)
    if cached:
        return json.loads(cached)
    
    # Get from database
    user = await db.get_user(user_id)
    
    # Cache for 1 hour
    redis.set(f"user:{user_id}", json.dumps(user), ex=3600)
    
    return user
```

---

### 5. Replacing Existing Redis Service

إذا كنت تستخدم Redis الحالي في `docker-compose.yml`:

**قبل:**
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**بعد:**
```yaml
# استبدله بـ:
services:
  redis:
    extends:
      file: docker-compose.redis-ha.yml
      service: redis-master
```

**أو استخدم النظام الكامل:**
```bash
# إيقاف Redis القديم
docker-compose stop redis

# بدء Redis Sentinel
docker-compose -f docker-compose.redis-ha.yml up -d

# تحديث المتغيرات في .env
USE_REDIS_SENTINEL=true
```

---

### 6. Monitoring Integration

#### Prometheus

أضف إلى `prometheus.yml`:
```yaml
scrape_configs:
  - job_name: 'redis-sentinel'
    static_configs:
      - targets: ['localhost:9121']
```

#### Grafana

```bash
# Import dashboards
# Dashboard ID: 11835 (Redis)
# Dashboard ID: 763 (Sentinel)
```

---

### 7. Example Service Updates

#### Notification Service

**قبل:**
```python
# apps/services/notification-service/src/cache.py
import redis

redis_client = redis.Redis(
    host='redis',
    port=6379,
    decode_responses=True
)
```

**بعد:**
```python
# apps/services/notification-service/src/cache.py
from shared.cache import get_redis_client

redis_client = get_redis_client()

# No other changes needed!
# The API is compatible
```

#### Auth Service

**قبل:**
```typescript
// apps/services/auth-service/src/redis.ts
import Redis from 'ioredis';

export const redis = new Redis({
  host: 'redis',
  port: 6379,
});
```

**بعد:**
```typescript
// apps/services/auth-service/src/redis.ts
import { getRedisSentinelClient } from '@sahool/cache';

export const redis = getRedisSentinelClient();

// Compatible API, minimal changes needed
```

---

### 8. Testing Migration

```bash
# 1. Start both old and new Redis
docker-compose up -d redis
docker-compose -f docker-compose.redis-ha.yml up -d

# 2. Migrate data (if needed)
redis-cli -h localhost -p 6379 --rdb /tmp/dump.rdb
redis-cli -h localhost -p 6379 --rdb - | \
  redis-cli -h localhost -p 6379 -a $REDIS_PASSWORD --pipe

# 3. Test services with new Redis
USE_REDIS_SENTINEL=true docker-compose up service-name

# 4. If successful, stop old Redis
docker-compose stop redis
```

---

### 9. Health Check Updates

Add to your service health checks:

```python
# Health check endpoint
@app.get("/health")
async def health_check():
    health = {
        "status": "healthy",
        "checks": {}
    }
    
    # Check Redis
    try:
        redis_health = redis_client.health_check()
        health["checks"]["redis"] = redis_health
        
        if redis_health["status"] != "healthy":
            health["status"] = "degraded"
    except Exception as e:
        health["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health["status"] = "unhealthy"
    
    return health
```

---

### 10. Migration Checklist

- [ ] تحديث `.env` بمتغيرات Sentinel
- [ ] تثبيت المكتبات المطلوبة
  - Python: `pip install redis hiredis`
  - Node.js: `npm install ioredis`
- [ ] تحديث استيراد Redis في الخدمات
- [ ] اختبار الاتصال
- [ ] نقل البيانات (إذا لزم الأمر)
- [ ] تحديث health checks
- [ ] تحديث المراقبة
- [ ] اختبار Failover
- [ ] توثيق التغييرات
- [ ] تدريب الفريق

---

### 11. Rollback Plan

في حالة وجود مشاكل:

```bash
# 1. Stop Sentinel cluster
docker-compose -f docker-compose.redis-ha.yml down

# 2. Start old Redis
docker-compose up -d redis

# 3. Restore backup
redis-cli -h localhost -p 6379 < backup.rdb

# 4. Update .env
USE_REDIS_SENTINEL=false

# 5. Restart services
docker-compose restart
```

---

### 12. Production Deployment

```bash
# 1. Backup current data
make backup

# 2. Deploy in maintenance window
# 2a. Update environment
cp .env .env.backup
cat >> .env << 'ENVEOF'
USE_REDIS_SENTINEL=true
REDIS_PASSWORD=production_password
ENVEOF

# 2b. Start Sentinel cluster
docker-compose -f docker-compose.redis-ha.yml up -d

# 2c. Verify health
make health

# 2d. Migrate data if needed
# Use Redis replication for zero-downtime

# 2e. Update services gradually
# Blue-green deployment recommended

# 3. Monitor for 24-48 hours
make logs -f

# 4. Test failover in staging first
make test-failover
```

---

### 13. Performance Tuning

```python
# For high-traffic services
from shared.cache import RedisSentinelConfig, RedisSentinelClient

config = RedisSentinelConfig()
config.max_connections = 100  # Increase for high traffic
config.socket_timeout = 2  # Reduce for faster failover

redis = RedisSentinelClient(config)
```

---

### 14. Advanced Usage

#### Rate Limiting

```python
from shared.cache.examples import RateLimiter

limiter = RateLimiter(max_requests=1000, window=60)

@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    client_ip = request.client.host
    
    if not limiter.is_allowed(client_ip):
        return JSONResponse(
            status_code=429,
            content={"error": "Rate limit exceeded"}
        )
    
    return await call_next(request)
```

#### Distributed Lock

```python
from shared.cache.examples import DistributedLock

@app.post("/export")
async def export_data():
    lock = DistributedLock("export:process", timeout=300)
    
    if not lock.acquire(blocking=False):
        raise HTTPException(409, "Export already in progress")
    
    try:
        # Perform export
        result = await perform_export()
        return result
    finally:
        lock.release()
```

#### Session Management

```typescript
import { SessionManager } from '@sahool/cache/examples';

const sessions = new SessionManager();

app.post('/login', async (req, res) => {
  const { username, password } = req.body;
  
  // Authenticate
  const user = await authenticate(username, password);
  
  // Create session
  const sessionId = generateSessionId();
  await sessions.create(sessionId, {
    userId: user.id,
    username: user.username,
    role: user.role,
  }, 3600);
  
  res.json({ sessionId });
});
```

---

## الدعم | Support

للمساعدة في التكامل:
- 📧 Email: support@sahool.platform
- 📝 GitHub Issues
- 📖 Documentation: `/shared/cache/README.md`

---

**Success!** 🎉 Your services are now using Redis Sentinel with High Availability!
