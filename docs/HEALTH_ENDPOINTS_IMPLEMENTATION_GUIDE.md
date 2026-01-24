# Health Endpoints Implementation Guide | دليل تنفيذ نقاط فحص الصحة

> Standard health check implementation for SAHOOL services

## Overview | نظرة عامة

This document provides implementation guidelines for adding health check endpoints to services that currently lack them. Health endpoints are essential for Kubernetes deployments and operational monitoring.

هذا المستند يوفر إرشادات التنفيذ لإضافة نقاط فحص الصحة للخدمات التي تفتقر إليها حالياً. نقاط فحص الصحة ضرورية لنشر Kubernetes والمراقبة التشغيلية.

---

## Services Requiring Health Endpoints | الخدمات التي تحتاج نقاط فحص الصحة

### Node.js Services (10 services)

| Service | Port | Framework | Priority |
|---------|------|-----------|----------|
| Community Chat | 8097 | NestJS | High |
| Disaster Assessment | 3020 | NestJS | High |
| IoT Service | 8117 | NestJS | High |
| LAI Estimation | 3022 | NestJS | Medium |
| Marketplace Service | 3010 | NestJS | High |
| Research Core | 3015 | NestJS | Medium |
| User Service | 3025 | NestJS | Critical |
| Yield Prediction | 3021 | NestJS | Medium |
| Yield Prediction Service | 3021 | NestJS | Medium |
| Chat Service | - | NestJS | Medium |

### Python Services (4 services)

| Service | Port | Framework | Priority |
|---------|------|-----------|----------|
| Agro Rules | 8151 | FastAPI | Medium |
| Code Review Agent | - | FastAPI | Low |
| Crop Growth Model | 3023 | FastAPI | Medium |
| Demo Data | - | FastAPI | Low |

---

## Standard Implementation | التنفيذ القياسي

### Python (FastAPI) Template

```python
from fastapi import FastAPI, Depends
from datetime import datetime
import asyncio

app = FastAPI(title="Service Name", version="16.0.0")

# Track startup time for uptime calculation
_startup_time = datetime.utcnow()

@app.get("/health", tags=["Health"])
def health():
    """
    Full health check with dependency status
    فحص الصحة الكامل مع حالة التبعيات
    """
    return {
        "status": "healthy",
        "service": "service-name",
        "version": "16.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - _startup_time).total_seconds(),
        "dependencies": {
            "database": check_database_health(),
            "nats": check_nats_health(),
            "redis": check_redis_health()
        }
    }

@app.get("/healthz", tags=["Health"])
def healthz():
    """
    Kubernetes liveness probe - Is the process alive?
    فحص الحياة لـ Kubernetes - هل العملية حية؟
    """
    return {
        "status": "healthy",
        "service": "service-name",
        "version": "16.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/readyz", tags=["Health"])
async def readyz():
    """
    Kubernetes readiness probe - Can the service handle traffic?
    فحص الجاهزية لـ Kubernetes - هل الخدمة جاهزة للتعامل مع الطلبات؟
    """
    db_ready = await check_database_ready()
    nats_ready = await check_nats_ready()

    is_ready = db_ready and nats_ready

    return {
        "status": "ready" if is_ready else "not_ready",
        "service": "service-name",
        "database": db_ready,
        "nats": nats_ready
    }

# Helper functions
def check_database_health():
    """Check database connectivity"""
    try:
        # Replace with actual check
        return "connected"
    except Exception:
        return "disconnected"

def check_nats_health():
    """Check NATS connectivity"""
    try:
        # Replace with actual check
        return "connected"
    except Exception:
        return "disconnected"

def check_redis_health():
    """Check Redis connectivity"""
    try:
        # Replace with actual check
        return "connected"
    except Exception:
        return "disconnected"

async def check_database_ready():
    """Check if database is ready for queries"""
    try:
        # Replace with actual check (e.g., await db.execute("SELECT 1"))
        return True
    except Exception:
        return False

async def check_nats_ready():
    """Check if NATS is ready"""
    try:
        # Replace with actual check
        return True
    except Exception:
        return False
```

### Node.js (NestJS) Template

```typescript
// health.controller.ts
import { Controller, Get } from '@nestjs/common';
import { HealthCheck, HealthCheckService, TypeOrmHealthIndicator, MemoryHealthIndicator } from '@nestjs/terminus';

@Controller()
export class HealthController {
  private readonly startupTime = new Date();

  constructor(
    private health: HealthCheckService,
    private db: TypeOrmHealthIndicator,
    private memory: MemoryHealthIndicator,
  ) {}

  @Get('/health')
  @HealthCheck()
  async check() {
    return this.health.check([
      () => this.db.pingCheck('database'),
      () => this.memory.checkHeap('memory_heap', 150 * 1024 * 1024),
    ]);
  }

  @Get('/healthz')
  healthz() {
    return {
      status: 'healthy',
      service: 'service-name',
      version: '16.0.0',
      timestamp: new Date().toISOString(),
    };
  }

  @Get('/readyz')
  async readyz() {
    let dbReady = false;
    let natsReady = false;

    try {
      // Check database
      await this.db.pingCheck('database');
      dbReady = true;
    } catch (e) {
      dbReady = false;
    }

    try {
      // Check NATS (if applicable)
      natsReady = true; // Replace with actual check
    } catch (e) {
      natsReady = false;
    }

    const isReady = dbReady && natsReady;

    return {
      status: isReady ? 'ready' : 'not_ready',
      service: 'service-name',
      database: dbReady,
      nats: natsReady,
    };
  }
}

// health.module.ts
import { Module } from '@nestjs/common';
import { TerminusModule } from '@nestjs/terminus';
import { HealthController } from './health.controller';

@Module({
  imports: [TerminusModule],
  controllers: [HealthController],
})
export class HealthModule {}

// app.module.ts - Add HealthModule to imports
@Module({
  imports: [
    // ... other imports
    HealthModule,
  ],
})
export class AppModule {}
```

---

## Service-Specific Implementation | التنفيذ الخاص بكل خدمة

### 1. User Service (Critical Priority)

```typescript
// apps/services/user-service/src/health/health.controller.ts

import { Controller, Get } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';

@Controller()
export class HealthController {
  constructor(private prisma: PrismaService) {}

  @Get('/healthz')
  healthz() {
    return {
      status: 'healthy',
      service: 'user-service',
      version: '16.0.0',
      timestamp: new Date().toISOString(),
    };
  }

  @Get('/readyz')
  async readyz() {
    let dbReady = false;
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      dbReady = true;
    } catch (e) {
      dbReady = false;
    }

    return {
      status: dbReady ? 'ready' : 'not_ready',
      service: 'user-service',
      database: dbReady,
    };
  }

  @Get('/health')
  async health() {
    let dbStatus = 'disconnected';
    let userCount = 0;

    try {
      userCount = await this.prisma.user.count();
      dbStatus = 'connected';
    } catch (e) {
      // Database unavailable
    }

    return {
      status: dbStatus === 'connected' ? 'healthy' : 'degraded',
      service: 'user-service',
      version: '16.0.0',
      timestamp: new Date().toISOString(),
      dependencies: {
        database: dbStatus,
      },
      stats: {
        total_users: userCount,
      },
    };
  }
}
```

### 2. Marketplace Service (High Priority)

```typescript
// apps/services/marketplace-service/src/health/health.controller.ts

@Controller()
export class HealthController {
  constructor(private prisma: PrismaService) {}

  @Get('/healthz')
  healthz() {
    return {
      status: 'healthy',
      service: 'marketplace-service',
      version: '16.0.0',
      timestamp: new Date().toISOString(),
    };
  }

  @Get('/readyz')
  async readyz() {
    let dbReady = false;
    try {
      await this.prisma.$queryRaw`SELECT 1`;
      dbReady = true;
    } catch (e) {
      dbReady = false;
    }

    return {
      status: dbReady ? 'ready' : 'not_ready',
      service: 'marketplace-service',
      database: dbReady,
    };
  }

  @Get('/health')
  async health() {
    let dbStatus = 'disconnected';
    let listingsCount = 0;

    try {
      listingsCount = await this.prisma.listing.count();
      dbStatus = 'connected';
    } catch (e) {
      // Database unavailable
    }

    return {
      status: dbStatus === 'connected' ? 'healthy' : 'degraded',
      service: 'marketplace-service',
      version: '16.0.0',
      dependencies: {
        database: dbStatus,
      },
      stats: {
        total_listings: listingsCount,
      },
    };
  }
}
```

### 3. IoT Service (High Priority)

```typescript
// apps/services/iot-service/src/health/health.controller.ts

@Controller()
export class HealthController {
  constructor(
    private prisma: PrismaService,
    private nats: NatsService,
  ) {}

  @Get('/healthz')
  healthz() {
    return {
      status: 'healthy',
      service: 'iot-service',
      version: '16.0.0',
      timestamp: new Date().toISOString(),
    };
  }

  @Get('/readyz')
  async readyz() {
    let dbReady = false;
    let natsReady = false;

    try {
      await this.prisma.$queryRaw`SELECT 1`;
      dbReady = true;
    } catch (e) {
      dbReady = false;
    }

    try {
      natsReady = this.nats.isConnected();
    } catch (e) {
      natsReady = false;
    }

    const isReady = dbReady && natsReady;

    return {
      status: isReady ? 'ready' : 'not_ready',
      service: 'iot-service',
      database: dbReady,
      nats: natsReady,
    };
  }

  @Get('/health')
  async health() {
    let dbStatus = 'disconnected';
    let natsStatus = 'disconnected';
    let devicesCount = 0;

    try {
      devicesCount = await this.prisma.device.count();
      dbStatus = 'connected';
    } catch (e) {
      // Database unavailable
    }

    try {
      natsStatus = this.nats.isConnected() ? 'connected' : 'disconnected';
    } catch (e) {
      // NATS unavailable
    }

    return {
      status: dbStatus === 'connected' ? 'healthy' : 'degraded',
      service: 'iot-service',
      version: '16.0.0',
      dependencies: {
        database: dbStatus,
        nats: natsStatus,
      },
      stats: {
        total_devices: devicesCount,
      },
    };
  }
}
```

### 4. Agro Rules (Python)

```python
# apps/services/agro-rules/src/main.py

from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Agro Rules Engine", version="16.0.0")

_startup_time = datetime.utcnow()

@app.get("/healthz", tags=["Health"])
def healthz():
    """Kubernetes liveness probe | فحص الحياة"""
    return {
        "status": "healthy",
        "service": "agro-rules",
        "version": "16.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/readyz", tags=["Health"])
def readyz():
    """Kubernetes readiness probe | فحص الجاهزية"""
    # Agro rules is a stateless rule engine
    # Ready if rules are loaded
    rules_loaded = len(app.state.rules) > 0 if hasattr(app.state, 'rules') else True

    return {
        "status": "ready" if rules_loaded else "not_ready",
        "service": "agro-rules",
        "rules_loaded": rules_loaded
    }

@app.get("/health", tags=["Health"])
def health():
    """Full health check | فحص الصحة الكامل"""
    return {
        "status": "healthy",
        "service": "agro-rules",
        "version": "16.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": (datetime.utcnow() - _startup_time).total_seconds(),
        "dependencies": {}
    }
```

---

## Kubernetes Configuration | تكوين Kubernetes

### Standard Pod Configuration

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: service-name
  labels:
    app: service-name
spec:
  containers:
  - name: service-name
    image: sahool/service-name:16.0.0
    ports:
    - containerPort: 8080

    # Liveness Probe - Is the container alive?
    livenessProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 15
      periodSeconds: 20
      timeoutSeconds: 5
      failureThreshold: 3
      successThreshold: 1

    # Readiness Probe - Can it receive traffic?
    readinessProbe:
      httpGet:
        path: /readyz
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 10
      timeoutSeconds: 5
      failureThreshold: 3
      successThreshold: 1

    # Startup Probe - Has it started? (optional)
    startupProbe:
      httpGet:
        path: /healthz
        port: 8080
      initialDelaySeconds: 10
      periodSeconds: 5
      failureThreshold: 30
```

### Helm Values Template

```yaml
# helm/sahool/values.yaml

healthCheck:
  liveness:
    path: /healthz
    initialDelaySeconds: 15
    periodSeconds: 20
    timeoutSeconds: 5
    failureThreshold: 3
  readiness:
    path: /readyz
    initialDelaySeconds: 5
    periodSeconds: 10
    timeoutSeconds: 5
    failureThreshold: 3
```

---

## Docker Health Check | فحص صحة Docker

### Dockerfile Template

```dockerfile
FROM python:3.11-slim

# ... other Dockerfile content ...

# Health check using Python urllib (no curl needed)
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:${PORT:-8080}/healthz')" || exit 1

# Alternative with curl (if available)
# HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
#     CMD curl -f http://localhost:${PORT:-8080}/healthz || exit 1

CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

---

## Response Codes | رموز الاستجابة

| Endpoint | Success | Failure | Use Case |
|----------|---------|---------|----------|
| `/healthz` | 200 | 503 | Liveness - process alive |
| `/readyz` | 200 | 503 | Readiness - can handle traffic |
| `/health` | 200 | 200* | Monitoring - always returns, status in body |

*Note: `/health` should always return 200 with status in the body to allow monitoring systems to parse the response.

---

## Best Practices | أفضل الممارسات

1. **Liveness vs Readiness**:
   - Liveness: Should the container be restarted?
   - Readiness: Should traffic be sent to this pod?

2. **Database Checks**:
   - Use lightweight queries (`SELECT 1`)
   - Set appropriate timeouts
   - Don't block on slow queries

3. **Graceful Degradation**:
   - Return `degraded` status if non-critical dependencies fail
   - Keep service running if possible

4. **Startup Time**:
   - Set appropriate `initialDelaySeconds`
   - Use startup probes for slow-starting services

5. **Timeouts**:
   - Health check timeout < probe timeout
   - Don't exceed 5 seconds for health checks

---

## Implementation Checklist | قائمة التنفيذ

### Per Service

- [ ] Add `/healthz` endpoint (liveness)
- [ ] Add `/readyz` endpoint (readiness)
- [ ] Add `/health` endpoint (comprehensive)
- [ ] Update Dockerfile with HEALTHCHECK
- [ ] Update Kubernetes deployment
- [ ] Update service README
- [ ] Test health endpoints

### Verification

```bash
# Test liveness
curl -f http://localhost:8080/healthz

# Test readiness
curl -f http://localhost:8080/readyz

# Test comprehensive health
curl http://localhost:8080/health | jq
```

---

## Related Documentation | التوثيق ذو الصلة

- [DOCUMENTATION_AUDIT_REPORT.md](./DOCUMENTATION_AUDIT_REPORT.md) - Full documentation audit
- [HEALTH_ENDPOINTS_STANDARDS.md](./HEALTH_ENDPOINTS_STANDARDS.md) - Health check standards
- [Kubernetes Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

---

**Document Version**: 1.0
**Last Updated**: January 2026
**Author**: SAHOOL Platform Team
