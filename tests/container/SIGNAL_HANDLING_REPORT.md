# Signal Handling & Graceful Shutdown Report

**Date**: 2026-01-06
**Branch**: claude/fix-kong-dns-errors-h51fh
**Scope**: All services in `/apps/services/`

---

## Executive Summary

**CRITICAL FINDINGS**: Zero services implement proper graceful shutdown handling. This poses significant risks for data integrity, connection leaks, and cascading failures during deployments, scaling operations, and container orchestration.

### Risk Level: HIGH

- **Services Analyzed**: 52 services with Dockerfiles
- **Services with SIGTERM handlers**: 0 (0%)
- **Services with SIGINT handlers**: 0 (0%)
- **Services using tini/dumb-init**: 0 (0%)
- **Services with stop_grace_period**: 0 (0%)
- **Dockerfiles using ENTRYPOINT**: 0 (0%)
- **Dockerfiles using CMD**: 52 (100%)

---

## 1. Signal Handler Analysis

### 1.1 Node.js Services (NestJS & Express)

**Pattern Searched**: `process.on('SIGTERM')`, `process.on('SIGINT')`

**Result**: NO signal handlers found in any Node.js service

**Services Checked**:

- `/apps/services/chat-service/src/main.ts` - NO signal handling
- `/apps/services/user-service/src/main.ts` - NO signal handling
- `/apps/services/iot-service/src/main.ts` - NO signal handling
- `/apps/services/marketplace-service/src/main.ts` - NO signal handling
- `/apps/services/community-chat/` - NO signal handling
- `/apps/services/yield-prediction-service/` - NO signal handling
- `/apps/services/disaster-assessment/` - NO signal handling
- `/apps/services/lai-estimation/` - NO signal handling
- `/apps/services/crop-growth-model/` - NO signal handling
- `/apps/services/research-core/` - NO signal handling
- `/apps/services/field-core/` - NO signal handling
- `/apps/services/field-management-service/` - NO signal handling

**Impact**:

- WebSocket connections terminated abruptly (chat-service, community-chat, ws-gateway)
- Database connections not closed properly
- Redis connections leaked
- MQTT connections dropped without cleanup (iot-service)
- Prisma connections not released
- In-flight HTTP requests terminated mid-processing
- Message queue consumers not gracefully stopped

### 1.2 Python Services (FastAPI & Uvicorn)

**Pattern Searched**: `signal.signal(signal.SIGTERM`, `signal.signal(signal.SIGINT`

**Result**: NO signal handlers found in any Python service

**Services Checked**:

- `/apps/services/ai-advisor/src/main.py` - NO signal handling
- `/apps/services/field-ops/src/main.py` - NO signal handling
- `/apps/services/provider-config/src/main.py` - NO signal handling
- `/apps/services/task-service/src/main.py` - NO signal handling
- `/apps/services/weather-service/` - NO signal handling
- `/apps/services/weather-advanced/` - NO signal handling
- `/apps/services/weather-core/` - NO signal handling
- `/apps/services/crop-health-ai/` - NO signal handling
- `/apps/services/vegetation-analysis-service/` - NO signal handling
- `/apps/services/satellite-service/` - NO signal handling
- `/apps/services/ndvi-engine/` - NO signal handling
- `/apps/services/ndvi-processor/` - NO signal handling
- `/apps/services/yield-engine/` - NO signal handling
- `/apps/services/virtual-sensors/` - NO signal handling
- `/apps/services/crop-intelligence-service/` - NO signal handling
- `/apps/services/iot-gateway/` - NO signal handling
- `/apps/services/field-service/` - NO signal handling
- `/apps/services/field-chat/` - NO signal handling
- `/apps/services/billing-core/` - NO signal handling
- `/apps/services/crop-health/` - NO signal handling
- `/apps/services/mcp-server/` - NO signal handling
- `/apps/services/alert-service/` - NO signal handling
- `/apps/services/astronomical-calendar/` - NO signal handling
- `/apps/services/irrigation-smart/` - NO signal handling
- `/apps/services/globalgap-compliance/` - NO signal handling
- `/apps/services/ai-agents-core/` - NO signal handling
- `/apps/services/fertilizer-advisor/` - NO signal handling
- `/apps/services/equipment-service/` - NO signal handling
- `/apps/services/inventory-service/` - NO signal handling
- `/apps/services/indicators-service/` - NO signal handling
- `/apps/services/agro-advisor/` - NO signal handling
- `/apps/services/advisory-service/` - NO signal handling
- `/apps/services/agent-registry/` - NO signal handling
- `/apps/services/agro-rules/` - NO signal handling (worker process)
- `/apps/services/code-review-service/` - NO signal handling
- `/apps/services/demo-data/` - NO signal handling
- `/apps/services/ws-gateway/` - NO signal handling

**Impact**:

- AI/LLM requests interrupted mid-generation
- Database transactions not rolled back
- HTTP client connections not closed
- File handles not released
- Background tasks not cancelled
- Vector database connections (Qdrant) not closed
- Redis connections leaked
- NATS connections not properly closed
- Async tasks not awaited before shutdown
- uvicorn workers killed without cleanup

**Special Concern - Uvicorn Workers**:
Many services run with `--workers 2` flag:

- `/apps/services/yield-engine/Dockerfile`: `CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8098", "--workers", "2"]`
- `/apps/services/crop-health-ai/Dockerfile`: `CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8095", "--workers", "2"]`

Worker processes will be forcefully killed without coordinated shutdown.

---

## 2. Dockerfile Analysis

### 2.1 Process Init Systems

**Pattern Searched**: `tini`, `dumb-init`

**Result**: NO init systems found in any Dockerfile

**Impact**:

- Zombie processes not reaped
- Signals not properly forwarded to child processes
- PID 1 problem: Services run as PID 1, which has special signal handling in Linux
- Multi-worker services (uvicorn --workers 2) won't propagate signals to workers

**Example Dockerfiles Checked**:

- `/apps/services/chat-service/Dockerfile` - NO tini/dumb-init
- `/apps/services/ai-advisor/Dockerfile` - NO tini/dumb-init
- All 52 Dockerfiles - NO tini/dumb-init

### 2.2 CMD vs ENTRYPOINT Usage

**CMD Usage**: 52 services (100%)
**ENTRYPOINT Usage**: 0 services (0%)

**All Services Use CMD**:

```dockerfile
# Node.js services
CMD ["node", "dist/main.js"]
CMD ["npm", "start"]

# Python services
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8095"]
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8112"]
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT}"]
CMD ["python", "-u", "main.py"]
CMD ["python", "-m", "src.worker"]
```

**Impact**:

- Services run directly as PID 1
- Shell-based CMD (`sh -c`) creates additional process layer
- Signals must be handled by application code (currently NOT implemented)
- No init system to handle zombie processes

**Recommendation**: Consider using ENTRYPOINT with exec form for better signal handling, or add tini.

---

## 3. Docker Compose Configuration

### 3.1 stop_grace_period

**Pattern Searched**: `stop_grace_period` in all docker-compose\*.yml files

**Files Checked**:

- `/docker-compose.yml` (2525 lines)
- `/docker-compose.prod.yml`
- `/docker-compose.test.yml`
- `/docker-compose.tls.yml`
- `/docker/docker-compose.infra.yml`
- `/docker/docker-compose.iot.yml`
- `/infrastructure/monitoring/docker-compose.monitoring.yml`
- `/infrastructure/gateway/kong/docker-compose.yml`
- All other docker-compose files

**Result**: NO stop_grace_period configured for ANY service

**Default Behavior**:

- Docker default `stop_grace_period` is **10 seconds**
- After 10 seconds, Docker sends SIGKILL (force kill, cannot be caught)
- Since no services handle SIGTERM, they run for full 10 seconds then get SIGKILL

**Impact**:

- Services killed after 10 seconds regardless of cleanup needs
- No opportunity for proper cleanup even if implemented
- Database connections forcefully closed
- In-flight requests terminated
- Data corruption risk for services writing to disk/database

---

## 4. Service-Specific Risks

### 4.1 Critical Data Services

**High Risk Services** (data loss/corruption):

1. **field-management-service** (Node.js)
   - Uses Prisma ORM
   - Manages field data, operations
   - NO graceful shutdown
   - Risk: Database transaction corruption

2. **task-service** (Python)
   - PostgreSQL with SQLAlchemy
   - Task scheduling and completion
   - NO graceful shutdown
   - Risk: Task state corruption

3. **marketplace-service** (Node.js)
   - Financial transactions
   - Order management
   - NO graceful shutdown
   - Risk: Payment/order data inconsistency

4. **billing-core** (Python)
   - Financial data
   - NO graceful shutdown
   - Risk: Billing data corruption

### 4.2 Real-Time Communication Services

**High Risk Services** (connection leaks):

1. **chat-service** (Node.js)
   - Socket.IO WebSocket server
   - Real-time messaging
   - NO graceful shutdown
   - Risk: Client connections dropped without notification, message loss

2. **community-chat** (Node.js)
   - WebSocket connections
   - NO graceful shutdown
   - Risk: Active chat sessions terminated abruptly

3. **ws-gateway** (Python)
   - WebSocket gateway
   - NO graceful shutdown
   - Risk: Gateway connections not properly closed

4. **iot-service** (Node.js)
   - MQTT broker connections
   - Sensor data streams
   - NO graceful shutdown
   - Risk: MQTT sessions not properly ended, QoS message loss

### 4.3 AI/ML Services

**High Risk Services** (expensive operation interruption):

1. **ai-advisor** (Python)
   - Multi-agent AI system
   - Long-running LLM requests
   - NO graceful shutdown
   - Risk: Expensive AI operations terminated mid-generation, cost tracking lost

2. **crop-health-ai** (Python)
   - Image analysis (computer vision)
   - ML inference
   - NO graceful shutdown
   - Risk: Model inference interrupted, uploaded images not processed

3. **ai-agents-core** (Python)
   - Core AI agent framework
   - NO graceful shutdown
   - Risk: Agent state lost

### 4.4 Data Processing Services

**High Risk Services** (processing pipeline corruption):

1. **ndvi-processor** (Python)
   - Satellite image processing
   - NO graceful shutdown
   - Risk: Partial NDVI calculations, corrupted results

2. **ndvi-engine** (Python)
   - NDVI computation pipeline
   - NO graceful shutdown
   - Risk: Processing jobs interrupted

3. **vegetation-analysis-service** (Python)
   - Vegetation analysis
   - NO graceful shutdown
   - Risk: Analysis jobs lost

4. **yield-engine** (Python)
   - Yield prediction calculations
   - Runs with 2 workers
   - NO graceful shutdown
   - Risk: Yield calculations incomplete

### 4.5 External Integration Services

**Medium Risk Services** (connection/session leaks):

1. **weather-service**, **weather-core**, **weather-advanced** (Python)
   - External weather API connections
   - HTTP client sessions
   - NO graceful shutdown
   - Risk: HTTP client connections not closed, API rate limits affected

2. **satellite-service** (Python)
   - Satellite imagery providers
   - NO graceful shutdown
   - Risk: Provider connections not closed

3. **notification-service** (Python)
   - Email/SMS providers
   - NO graceful shutdown
   - Risk: Notification queue not flushed

4. **provider-config** (Python)
   - External provider management
   - NO graceful shutdown
   - Risk: Provider status not updated

---

## 5. Container Orchestration Impact

### 5.1 Kubernetes Behavior

**Default Kubernetes Pod Termination**:

1. Pod receives SIGTERM
2. `terminationGracePeriodSeconds` countdown starts (default: 30s)
3. If process still running after grace period, SIGKILL sent

**Current State**:

- Services don't handle SIGTERM → run until SIGKILL
- Wastes grace period time
- No cleanup occurs
- New pods start before old pods finish (overlapping traffic)

### 5.2 Docker Compose Behavior

**Docker Compose Stop**:

1. Sends SIGTERM to container
2. Waits `stop_grace_period` (default: 10s, none configured)
3. Sends SIGKILL

**Current State**:

- `docker-compose down` kills all services after 10s
- No cleanup occurs
- Database connections not closed
- Risk of database connection pool exhaustion

### 5.3 Docker Swarm Behavior

**Swarm Service Update**:

1. Starts new container
2. Sends SIGTERM to old container
3. Waits `stop_grace_period`
4. Sends SIGKILL

**Current State**:

- Rolling updates always wait full 10s per container
- Slow deployment times
- No graceful connection draining

---

## 6. Specific Scenarios & Failures

### 6.1 Database Connection Scenarios

**Scenario**: Service receives SIGTERM during database transaction

**Current Behavior**:

1. Service continues running (doesn't handle SIGTERM)
2. After 10s, receives SIGKILL
3. Database transaction not committed or rolled back
4. Database connection killed mid-transaction
5. PostgreSQL marks connection as "terminated abnormally"

**Impact**:

- PgBouncer connection pool may hold dead connections
- Database locks not released
- Transaction log bloat
- Risk of data corruption

### 6.2 WebSocket Connection Scenarios

**Scenario**: chat-service receives SIGTERM with 100 active WebSocket connections

**Current Behavior**:

1. Service continues running (doesn't handle SIGTERM)
2. After 10s, receives SIGKILL
3. All 100 WebSocket connections dropped instantly
4. No close frames sent to clients
5. Clients see network error, not graceful disconnect

**Impact**:

- Poor user experience (connection errors)
- Message loss for in-flight messages
- Clients must implement aggressive retry logic
- Socket.IO reconnection storms

### 6.3 AI Request Scenarios

**Scenario**: ai-advisor receives SIGTERM during OpenAI API call

**Current Behavior**:

1. Service continues running (doesn't handle SIGTERM)
2. After 10s, receives SIGKILL
3. OpenAI API request terminated mid-stream
4. Partial response discarded
5. Cost tracking not updated
6. HTTP client connection not closed

**Impact**:

- Wasted API credits (partial responses)
- Cost tracking inaccurate
- Client receives 502/504 error
- HTTP connection leak

### 6.4 File Upload Scenarios

**Scenario**: crop-health-ai receives SIGTERM during image upload processing

**Current Behavior**:

1. Service continues running (doesn't handle SIGTERM)
2. After 10s, receives SIGKILL
3. Image file partially written
4. ML model inference interrupted
5. Temporary files not cleaned up

**Impact**:

- Disk space leaked (temp files)
- Corrupted image files
- Processing job lost
- Client upload wasted

---

## 7. Recommended Solutions

### 7.1 Immediate Actions (Quick Wins)

#### A. Add stop_grace_period to docker-compose.yml

```yaml
services:
  chat-service:
    # ... existing config ...
    stop_grace_period: 30s # Allow 30s for cleanup

  ai-advisor:
    # ... existing config ...
    stop_grace_period: 60s # AI services need more time

  marketplace-service:
    # ... existing config ...
    stop_grace_period: 30s # Financial data needs proper cleanup
```

**Recommended grace periods**:

- Standard services: 30s
- AI/ML services: 60s
- Data processing services: 45s
- Simple services: 15s

#### B. Add tini to Python Dockerfiles

```dockerfile
FROM python:3.11-slim

# Install tini
RUN apt-get update && apt-get install -y tini && rm -rf /var/lib/apt/lists/*

# ... rest of Dockerfile ...

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

#### C. Add tini to Node.js Dockerfiles

```dockerfile
FROM node:20-alpine

# Install tini
RUN apk add --no-cache tini

# ... rest of Dockerfile ...

ENTRYPOINT ["/sbin/tini", "--"]
CMD ["node", "dist/main.js"]
```

### 7.2 Medium-Term Actions (Application Code)

#### A. Node.js/NestJS Signal Handlers

**Add to all NestJS main.ts files**:

```typescript
import { NestFactory } from "@nestjs/core";
import { AppModule } from "./app.module";

async function bootstrap() {
  const app = await NestFactory.create(AppModule);

  // ... existing configuration ...

  await app.listen(port);

  // Graceful shutdown handling
  const signals = ["SIGTERM", "SIGINT"];

  for (const signal of signals) {
    process.on(signal, async () => {
      console.log(`Received ${signal}, starting graceful shutdown...`);

      try {
        // Close server (stop accepting new connections)
        await app.close();
        console.log("Server closed successfully");

        // Exit successfully
        process.exit(0);
      } catch (error) {
        console.error("Error during shutdown:", error);
        process.exit(1);
      }
    });
  }

  // Handle uncaught errors during shutdown
  process.on("uncaughtException", (error) => {
    console.error("Uncaught exception during shutdown:", error);
    process.exit(1);
  });
}

bootstrap();
```

**What app.close() does**:

- Closes HTTP server (stops accepting connections)
- Waits for in-flight requests to complete
- Closes WebSocket connections gracefully
- Disconnects Prisma database connections
- Closes Redis connections
- Triggers NestJS `onApplicationShutdown` lifecycle hooks

#### B. Python/FastAPI Signal Handlers

**Add to all FastAPI main.py files**:

```python
import asyncio
import signal
from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn

# Global flag for shutdown
shutdown_event = asyncio.Event()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Service starting...")
    # ... existing startup code ...

    yield

    # Shutdown
    logger.info("Service shutting down...")
    # ... existing shutdown code ...
    # Close database connections
    # Close HTTP client sessions
    # Cancel background tasks

app = FastAPI(lifespan=lifespan)

# ... routes ...

def handle_shutdown(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    shutdown_event.set()

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    # Run with proper shutdown handling
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
    server = uvicorn.Server(config)

    try:
        server.run()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    finally:
        logger.info("Server stopped")
```

**For services with background tasks**:

```python
import asyncio

# Store background tasks
background_tasks = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting background tasks...")

    # Create background task
    task = asyncio.create_task(my_background_worker())
    background_tasks.add(task)

    yield

    # Shutdown
    logger.info("Cancelling background tasks...")
    for task in background_tasks:
        task.cancel()

    # Wait for cancellation
    await asyncio.gather(*background_tasks, return_exceptions=True)
    logger.info("All background tasks stopped")
```

#### C. Service-Specific Handlers

**chat-service (WebSocket cleanup)**:

```typescript
process.on("SIGTERM", async () => {
  console.log("SIGTERM received, closing WebSocket connections...");

  // Get Socket.IO server instance
  const io = app.get(SocketIoAdapter).io;

  // Emit disconnect event to all clients
  io.emit("server_shutdown", {
    message: "Server is shutting down, please reconnect",
  });

  // Close all socket connections
  const sockets = await io.fetchSockets();
  for (const socket of sockets) {
    socket.disconnect(true);
  }

  // Wait briefly for disconnects to process
  await new Promise((resolve) => setTimeout(resolve, 1000));

  // Close HTTP server
  await app.close();

  process.exit(0);
});
```

**ai-advisor (LLM request cleanup)**:

```python
import asyncio
import signal
from contextlib import asynccontextmanager

# Track active AI requests
active_requests = set()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    yield

    # Shutdown
    logger.info(f"Waiting for {len(active_requests)} AI requests to complete...")

    # Wait up to 30s for active requests
    try:
        await asyncio.wait_for(
            asyncio.gather(*active_requests, return_exceptions=True),
            timeout=30.0
        )
    except asyncio.TimeoutError:
        logger.warning("Some AI requests did not complete in time")

    logger.info("AI advisor shutdown complete")
```

**iot-service (MQTT cleanup)**:

```typescript
process.on("SIGTERM", async () => {
  console.log("SIGTERM received, closing MQTT connections...");

  const mqttService = app.get(MqttService);

  // Unsubscribe from all topics
  await mqttService.unsubscribeAll();

  // Disconnect MQTT client
  await mqttService.disconnect();

  // Close HTTP server
  await app.close();

  process.exit(0);
});
```

### 7.3 Long-Term Actions (Architecture)

#### A. Implement Health Check States

Add `/health/ready` and `/health/live` endpoints with shutdown state:

```typescript
enum ServiceState {
  STARTING,
  READY,
  SHUTTING_DOWN,
  STOPPED
}

let serviceState = ServiceState.STARTING;

// Readiness endpoint (used by load balancers)
@Get('/health/ready')
readiness() {
  if (serviceState === ServiceState.SHUTTING_DOWN ||
      serviceState === ServiceState.STOPPED) {
    throw new ServiceUnavailableException('Service is shutting down');
  }
  return { status: 'ready', state: serviceState };
}

// On SIGTERM
process.on('SIGTERM', async () => {
  serviceState = ServiceState.SHUTTING_DOWN;

  // Wait for load balancer to detect unhealthy state
  await new Promise(resolve => setTimeout(resolve, 5000));

  // Now close server
  await app.close();

  serviceState = ServiceState.STOPPED;
  process.exit(0);
});
```

#### B. Implement Connection Draining

For services with long-lived connections:

```typescript
let isShuttingDown = false;
const activeConnections = new Set();

// Track connections
server.on("connection", (conn) => {
  activeConnections.add(conn);
  conn.on("close", () => {
    activeConnections.delete(conn);
  });
});

process.on("SIGTERM", async () => {
  isShuttingDown = true;

  // Stop accepting new connections
  server.close();

  // Wait for active connections to finish (max 30s)
  const maxWait = 30000;
  const startTime = Date.now();

  while (activeConnections.size > 0 && Date.now() - startTime < maxWait) {
    console.log(`Waiting for ${activeConnections.size} connections...`);
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }

  // Force close remaining connections
  for (const conn of activeConnections) {
    conn.destroy();
  }

  process.exit(0);
});
```

#### C. Implement Graceful Shutdown Middleware

```typescript
// middleware/shutdown.middleware.ts
@Injectable()
export class ShutdownMiddleware implements NestMiddleware {
  private isShuttingDown = false;

  constructor() {
    process.on("SIGTERM", () => {
      this.isShuttingDown = true;
    });
  }

  use(req: Request, res: Response, next: NextFunction) {
    if (this.isShuttingDown) {
      res.status(503).json({
        error: "Service is shutting down",
        code: "SERVICE_UNAVAILABLE",
      });
      return;
    }
    next();
  }
}
```

---

## 8. Testing Graceful Shutdown

### 8.1 Manual Testing

**Test 1: Local Docker Container**

```bash
# Start service
docker-compose up -d chat-service

# Send SIGTERM
docker-compose stop chat-service

# Check logs for graceful shutdown
docker-compose logs chat-service

# Expected output:
# "Received SIGTERM, starting graceful shutdown..."
# "Server closed successfully"
```

**Test 2: Load Testing During Shutdown**

```bash
# Terminal 1: Start load test
while true; do curl http://localhost:8114/api/v1/health; sleep 0.1; done

# Terminal 2: Send SIGTERM
docker-compose stop chat-service

# Expected: No connection errors, all requests complete or get 503
```

**Test 3: Database Connection Check**

```bash
# Terminal 1: Monitor database connections
watch -n 1 'psql -U sahool -c "SELECT count(*) FROM pg_stat_activity WHERE application_name LIKE '\''%chat-service%'\'';"'

# Terminal 2: Stop service
docker-compose stop chat-service

# Expected: Connection count drops to 0 within grace period
```

### 8.2 Automated Testing

**Integration Test**:

```typescript
describe("Graceful Shutdown", () => {
  it("should close all connections on SIGTERM", async () => {
    // Start service
    const app = await bootstrap();

    // Create active connections
    const conn1 = await createWebSocketConnection();
    const conn2 = await createHttpRequest();

    // Send SIGTERM
    process.kill(process.pid, "SIGTERM");

    // Wait for shutdown
    await new Promise((resolve) => setTimeout(resolve, 5000));

    // Verify connections closed gracefully
    expect(conn1.readyState).toBe(WebSocket.CLOSED);
    expect(conn2.finished).toBe(true);
  });
});
```

### 8.3 Production Validation

**Kubernetes Rolling Update Test**:

```bash
# Watch pods
kubectl get pods -w -n sahool

# Trigger rolling update
kubectl rollout restart deployment/chat-service -n sahool

# Monitor logs
kubectl logs -f deployment/chat-service -n sahool

# Check for graceful shutdown messages
# Expected: "Received SIGTERM, starting graceful shutdown..."
```

**Metric to Monitor**:

- Connection error rate should NOT spike during deployments
- Request success rate should stay >99.9%
- Database connection pool should not show dead connections

---

## 9. Priority Implementation Matrix

### Critical Priority (Implement First)

| Service                  | Risk Level | Reason                                | Estimated Effort |
| ------------------------ | ---------- | ------------------------------------- | ---------------- |
| marketplace-service      | CRITICAL   | Financial transactions                | 4 hours          |
| billing-core             | CRITICAL   | Billing data                          | 4 hours          |
| chat-service             | HIGH       | 100+ concurrent WebSocket connections | 6 hours          |
| field-management-service | HIGH       | Core field data                       | 4 hours          |
| iot-service              | HIGH       | Real-time sensor data + MQTT          | 6 hours          |
| ai-advisor               | HIGH       | Expensive LLM operations              | 6 hours          |
| task-service             | HIGH       | Task state management                 | 4 hours          |

**Total Estimated Effort: 34 hours (4-5 days)**

### High Priority (Implement Second)

| Service              | Risk Level | Reason                   | Estimated Effort |
| -------------------- | ---------- | ------------------------ | ---------------- |
| user-service         | HIGH       | Authentication/session   | 4 hours          |
| community-chat       | HIGH       | WebSocket connections    | 4 hours          |
| crop-health-ai       | MEDIUM     | Image processing         | 4 hours          |
| ndvi-processor       | MEDIUM     | Satellite processing     | 4 hours          |
| weather-service      | MEDIUM     | External API connections | 3 hours          |
| notification-service | MEDIUM     | Message queue            | 3 hours          |

**Total Estimated Effort: 22 hours (3 days)**

### Medium Priority (Implement Third)

All remaining services: 30 services × 3 hours = 90 hours (11 days)

**Total Implementation Time: 146 hours (18-20 days with testing)**

---

## 10. Implementation Checklist

### Phase 1: Quick Wins (Week 1)

- [ ] Add `stop_grace_period` to all services in docker-compose.yml
  - [ ] Critical services: 60s
  - [ ] High priority services: 30s
  - [ ] Standard services: 20s
- [ ] Add tini to all Python service Dockerfiles
- [ ] Add tini to all Node.js service Dockerfiles
- [ ] Update all Dockerfiles to use ENTRYPOINT + CMD pattern
- [ ] Test tini integration in staging environment

### Phase 2: Critical Services (Week 2)

- [ ] marketplace-service: Add SIGTERM handler with transaction cleanup
- [ ] billing-core: Add SIGTERM handler with database cleanup
- [ ] chat-service: Add SIGTERM handler with WebSocket cleanup
- [ ] field-management-service: Add SIGTERM handler with Prisma cleanup
- [ ] iot-service: Add SIGTERM handler with MQTT cleanup
- [ ] ai-advisor: Add SIGTERM handler with request queue cleanup
- [ ] task-service: Add SIGTERM handler with task state cleanup
- [ ] Test all critical services in staging
- [ ] Monitor production metrics after deployment

### Phase 3: High Priority Services (Week 3)

- [ ] user-service: Add SIGTERM handler
- [ ] community-chat: Add SIGTERM handler
- [ ] crop-health-ai: Add SIGTERM handler
- [ ] ndvi-processor: Add SIGTERM handler
- [ ] weather-service: Add SIGTERM handler
- [ ] notification-service: Add SIGTERM handler
- [ ] Test all high priority services
- [ ] Deploy to production with monitoring

### Phase 4: Remaining Services (Weeks 4-5)

- [ ] Implement SIGTERM handlers for all remaining services
- [ ] Create shared shutdown utility libraries for Node.js and Python
- [ ] Update documentation and service templates
- [ ] Add graceful shutdown tests to CI/CD pipeline

### Phase 5: Validation (Week 6)

- [ ] Conduct load testing during rolling updates
- [ ] Verify database connection pool metrics
- [ ] Test Kubernetes pod eviction scenarios
- [ ] Monitor error rates during deployments
- [ ] Document lessons learned and best practices

---

## 11. Monitoring & Observability

### Metrics to Track

**Application Metrics**:

- `shutdown_duration_seconds` - Time taken for graceful shutdown
- `shutdown_requests_completed` - Requests completed during shutdown
- `shutdown_requests_rejected` - Requests rejected during shutdown (503)
- `shutdown_connections_closed` - Connections closed during shutdown
- `shutdown_success` - Boolean, was shutdown successful

**Infrastructure Metrics**:

- Container restart count (should decrease)
- Pod termination duration (should decrease to <30s)
- Database connection pool size (should not spike)
- Connection error rate (should stay flat during deployments)

**Business Metrics**:

- Transaction success rate (should stay >99.9%)
- Message delivery rate (should stay >99.9%)
- API error rate (should not spike during deployments)

### Logging Requirements

```typescript
// On SIGTERM received
logger.info("Graceful shutdown initiated", {
  timestamp: new Date().toISOString(),
  activeConnections: getActiveConnectionCount(),
  activeRequests: getActiveRequestCount(),
  pid: process.pid,
});

// During shutdown
logger.info("Closing server", {
  timestamp: new Date().toISOString(),
});

logger.info("Waiting for connections to close", {
  remainingConnections: getActiveConnectionCount(),
});

// On shutdown complete
logger.info("Graceful shutdown complete", {
  timestamp: new Date().toISOString(),
  duration: shutdownDuration,
  requestsCompleted: completedCount,
  requestsRejected: rejectedCount,
});
```

---

## 12. Architecture Patterns

### Pattern 1: Shared Shutdown Library (Node.js)

**File**: `apps/services/shared/shutdown/graceful-shutdown.ts`

```typescript
import { INestApplication } from "@nestjs/common";

export interface ShutdownOptions {
  gracePeriodMs?: number;
  signals?: NodeJS.Signals[];
}

export class GracefulShutdown {
  private isShuttingDown = false;
  private activeRequests = 0;

  constructor(
    private app: INestApplication,
    private options: ShutdownOptions = {},
  ) {
    const signals = options.signals || ["SIGTERM", "SIGINT"];

    for (const signal of signals) {
      process.on(signal, () => this.shutdown(signal));
    }
  }

  trackRequest() {
    this.activeRequests++;
    return () => {
      this.activeRequests--;
    };
  }

  private async shutdown(signal: string) {
    if (this.isShuttingDown) return;

    this.isShuttingDown = true;
    console.log(`Received ${signal}, starting graceful shutdown...`);

    const gracePeriod = this.options.gracePeriodMs || 30000;
    const startTime = Date.now();

    try {
      // Wait for active requests to complete
      while (this.activeRequests > 0 && Date.now() - startTime < gracePeriod) {
        console.log(
          `Waiting for ${this.activeRequests} requests to complete...`,
        );
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }

      // Close application
      await this.app.close();
      console.log("Graceful shutdown complete");
      process.exit(0);
    } catch (error) {
      console.error("Error during shutdown:", error);
      process.exit(1);
    }
  }
}

// Usage in main.ts:
// const shutdown = new GracefulShutdown(app);
```

### Pattern 2: Shared Shutdown Library (Python)

**File**: `apps/services/shared/shutdown/graceful_shutdown.py`

```python
import asyncio
import signal
import logging
from typing import Set, Callable
from contextlib import asynccontextmanager

logger = logging.getLogger(__name__)

class GracefulShutdown:
    def __init__(self, grace_period: int = 30):
        self.grace_period = grace_period
        self.is_shutting_down = False
        self.active_tasks: Set[asyncio.Task] = set()
        self.cleanup_callbacks: list[Callable] = []

    def register_cleanup(self, callback: Callable):
        """Register a cleanup callback to run on shutdown"""
        self.cleanup_callbacks.append(callback)

    def track_task(self, task: asyncio.Task):
        """Track an async task for graceful cancellation"""
        self.active_tasks.add(task)
        task.add_done_callback(self.active_tasks.discard)

    async def shutdown(self, signum: int):
        """Perform graceful shutdown"""
        if self.is_shutting_down:
            return

        self.is_shutting_down = True
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")

        # Cancel active tasks
        logger.info(f"Cancelling {len(self.active_tasks)} active tasks...")
        for task in self.active_tasks:
            task.cancel()

        # Wait for tasks to complete (with timeout)
        try:
            await asyncio.wait_for(
                asyncio.gather(*self.active_tasks, return_exceptions=True),
                timeout=self.grace_period
            )
        except asyncio.TimeoutError:
            logger.warning("Some tasks did not complete in time")

        # Run cleanup callbacks
        logger.info("Running cleanup callbacks...")
        for callback in self.cleanup_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback()
                else:
                    callback()
            except Exception as e:
                logger.error(f"Cleanup callback failed: {e}")

        logger.info("Graceful shutdown complete")

    def setup_signal_handlers(self):
        """Setup signal handlers for SIGTERM and SIGINT"""
        def handle_signal(signum, frame):
            asyncio.create_task(self.shutdown(signum))

        signal.signal(signal.SIGTERM, handle_signal)
        signal.signal(signal.SIGINT, handle_signal)

# Usage in main.py:
# shutdown_manager = GracefulShutdown(grace_period=30)
# shutdown_manager.setup_signal_handlers()
# shutdown_manager.register_cleanup(close_database)
```

### Pattern 3: Request Tracking Middleware

**Node.js**:

```typescript
@Injectable()
export class RequestTrackingMiddleware implements NestMiddleware {
  constructor(private shutdown: GracefulShutdown) {}

  use(req: Request, res: Response, next: NextFunction) {
    const release = this.shutdown.trackRequest();

    res.on("finish", release);
    res.on("close", release);

    next();
  }
}
```

**Python**:

```python
@app.middleware("http")
async def track_requests(request: Request, call_next):
    if shutdown_manager.is_shutting_down:
        return JSONResponse(
            status_code=503,
            content={"error": "Service is shutting down"}
        )

    task = asyncio.current_task()
    shutdown_manager.track_task(task)

    response = await call_next(request)
    return response
```

---

## 13. Conclusion

### Summary of Findings

This comprehensive analysis reveals a **critical gap in production readiness**: none of the 52 services implement graceful shutdown handling. This creates significant risks for:

1. **Data Integrity**: Database transactions and file operations interrupted
2. **User Experience**: Connections dropped abruptly without notification
3. **Resource Leaks**: Database connections, HTTP clients, file handles not closed
4. **Cost Efficiency**: Expensive AI operations wasted
5. **Reliability**: Cascading failures during deployments and scaling

### Impact Assessment

**Current State**:

- Every deployment, scaling operation, or container restart risks data corruption
- Database connection pool exhaustion during high-frequency deployments
- Poor user experience with connection errors
- Wasted compute resources and API credits

**After Implementation**:

- Zero-downtime deployments
- Improved system reliability
- Better resource utilization
- Enhanced user experience
- Compliance with production best practices

### Next Steps

1. **Immediate** (Week 1): Add `stop_grace_period` and tini to all services
2. **Critical** (Week 2): Implement signal handlers for 7 critical services
3. **High Priority** (Week 3): Implement signal handlers for 6 high-priority services
4. **Complete** (Weeks 4-5): Implement for all remaining services
5. **Validate** (Week 6): Test and monitor in production

### Risk Mitigation

Without these changes, the platform is at risk of:

- Data corruption during deployments
- Service degradation during scaling
- Kubernetes pod eviction failures
- Failed health checks
- Cascading failures

**Recommendation**: Treat this as a **P0 (Critical Priority)** issue and allocate dedicated engineering time to address it across all services within 6 weeks.

---

## Appendix A: All Services Status

### Services with Dockerfiles (52 total)

| #   | Service Name                | Type    | Dockerfile | SIGTERM | tini | stop_grace_period |
| --- | --------------------------- | ------- | ---------- | ------- | ---- | ----------------- |
| 1   | advisory-service            | Python  | ✓          | ✗       | ✗    | ✗                 |
| 2   | agent-registry              | Python  | ✓          | ✗       | ✗    | ✗                 |
| 3   | agro-advisor                | Python  | ✓          | ✗       | ✗    | ✗                 |
| 4   | agro-rules                  | Python  | ✓          | ✗       | ✗    | ✗                 |
| 5   | ai-advisor                  | Python  | ✓          | ✗       | ✗    | ✗                 |
| 6   | ai-agents-core              | Python  | ✓          | ✗       | ✗    | ✗                 |
| 7   | alert-service               | Python  | ✓          | ✗       | ✗    | ✗                 |
| 8   | astronomical-calendar       | Python  | ✓          | ✗       | ✗    | ✗                 |
| 9   | billing-core                | Python  | ✓          | ✗       | ✗    | ✗                 |
| 10  | chat-service                | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 11  | code-review-service         | Python  | ✓          | ✗       | ✗    | ✗                 |
| 12  | community-chat              | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 13  | crop-growth-model           | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 14  | crop-health                 | Python  | ✓          | ✗       | ✗    | ✗                 |
| 15  | crop-health-ai              | Python  | ✓          | ✗       | ✗    | ✗                 |
| 16  | crop-intelligence-service   | Python  | ✓          | ✗       | ✗    | ✗                 |
| 17  | demo-data                   | Python  | ✓          | ✗       | ✗    | ✗                 |
| 18  | disaster-assessment         | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 19  | equipment-service           | Python  | ✓          | ✗       | ✗    | ✗                 |
| 20  | fertilizer-advisor          | Python  | ✓          | ✗       | ✗    | ✗                 |
| 21  | field-chat                  | Python  | ✓          | ✗       | ✗    | ✗                 |
| 22  | field-core                  | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 23  | field-intelligence          | Python  | ✓          | ✗       | ✗    | ✗                 |
| 24  | field-management-service    | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 25  | field-ops                   | Python  | ✓          | ✗       | ✗    | ✗                 |
| 26  | field-service               | Python  | ✓          | ✗       | ✗    | ✗                 |
| 27  | globalgap-compliance        | Python  | ✓          | ✗       | ✗    | ✗                 |
| 28  | indicators-service          | Python  | ✓          | ✗       | ✗    | ✗                 |
| 29  | inventory-service           | Python  | ✓          | ✗       | ✗    | ✗                 |
| 30  | iot-gateway                 | Python  | ✓          | ✗       | ✗    | ✗                 |
| 31  | iot-service                 | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 32  | irrigation-smart            | Python  | ✓          | ✗       | ✗    | ✗                 |
| 33  | lai-estimation              | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 34  | marketplace-service         | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 35  | mcp-server                  | Python  | ✓          | ✗       | ✗    | ✗                 |
| 36  | ndvi-engine                 | Python  | ✓          | ✗       | ✗    | ✗                 |
| 37  | ndvi-processor              | Python  | ✓          | ✗       | ✗    | ✗                 |
| 38  | notification-service        | Python  | ✓          | ✗       | ✗    | ✗                 |
| 39  | provider-config             | Python  | ✓          | ✗       | ✗    | ✗                 |
| 40  | research-core               | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 41  | satellite-service           | Python  | ✓          | ✗       | ✗    | ✗                 |
| 42  | task-service                | Python  | ✓          | ✗       | ✗    | ✗                 |
| 43  | user-service                | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 44  | vegetation-analysis-service | Python  | ✓          | ✗       | ✗    | ✗                 |
| 45  | virtual-sensors             | Python  | ✓          | ✗       | ✗    | ✗                 |
| 46  | weather-advanced            | Python  | ✓          | ✗       | ✗    | ✗                 |
| 47  | weather-core                | Python  | ✓          | ✗       | ✗    | ✗                 |
| 48  | weather-service             | Python  | ✓          | ✗       | ✗    | ✗                 |
| 49  | ws-gateway                  | Python  | ✓          | ✗       | ✗    | ✗                 |
| 50  | yield-engine                | Python  | ✓          | ✗       | ✗    | ✗                 |
| 51  | yield-prediction            | Node.js | ✓          | ✗       | ✗    | ✗                 |
| 52  | yield-prediction-service    | Node.js | ✓          | ✗       | ✗    | ✗                 |

**Legend**: ✓ = Implemented, ✗ = Not Implemented

---

## Appendix B: Service Classification

### By Language/Framework

**Node.js/NestJS Services (13)**:

- chat-service, community-chat, crop-growth-model, disaster-assessment
- field-core, field-management-service, iot-service, lai-estimation
- marketplace-service, research-core, user-service, yield-prediction
- yield-prediction-service

**Python/FastAPI Services (39)**:

- All remaining services use Python with FastAPI + uvicorn

### By Risk Level

**CRITICAL (7 services)**:

- marketplace-service, billing-core, chat-service
- field-management-service, iot-service, ai-advisor, task-service

**HIGH (25 services)**:

- user-service, community-chat, crop-health-ai, ndvi-processor
- weather-service, notification-service, provider-config
- field-core, iot-gateway, crop-intelligence-service
- satellite-service, ndvi-engine, vegetation-analysis-service
- field-service, field-chat, yield-engine, virtual-sensors
- ws-gateway, alert-service, equipment-service, inventory-service
- agro-advisor, advisory-service, agent-registry, ai-agents-core

**MEDIUM (20 services)**:

- All remaining services

---

**Report Generated**: 2026-01-06
**Engineer**: Claude
**Branch**: claude/fix-kong-dns-errors-h51fh
**Status**: CRITICAL - IMMEDIATE ACTION REQUIRED
