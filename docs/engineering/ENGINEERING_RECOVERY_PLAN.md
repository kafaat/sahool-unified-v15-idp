# SAHOOL Engineering Recovery Plan

## خطة الإنقاذ الهندسي - منصة سهول v15.5

**Classification:** INTERNAL - ENGINEERING LEADERSHIP
**Status:** APPROVED FOR EXECUTION
**Effective Date:** 2024-01-20
**Review Cycle:** Weekly

---

## Executive Summary | الملخص التنفيذي

### الوضع الحالي

منصة SAHOOL تواجه **ديون تقنية حرجة** تهدد استقرار الإنتاج وقابلية التوسع. هذه الخطة تحدد مسار إنقاذ مدته **8 أسابيع** لتحويل المنصة من "نموذج أولي ناجح" إلى "منتج جاهز للإنتاج".

### القرار الاستراتيجي

```
┌─────────────────────────────────────────────────────────────────────┐
│                    🛑 FEATURE FREEZE - 8 WEEKS                      │
│                                                                     │
│  ❌ لا ميزات جديدة                                                 │
│  ❌ لا UI/UX تحسينات                                               │
│  ❌ لا Refactors تجميلية                                           │
│                                                                     │
│  ✅ استقرار البنية التحتية                                         │
│  ✅ توحيد المعايير                                                 │
│  ✅ رصد ومراقبة                                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### الأرقام الرئيسية

| المقياس                 | الحالي   | الهدف      | الأثر |
| ----------------------- | -------- | ---------- | ----- |
| MTTR (Time to Recovery) | 4+ ساعات | <30 دقيقة  | -87%  |
| تكلفة البنية التحتية    | $X/شهر   | $0.35X/شهر | -65%  |
| الأعطال الأسبوعية       | 3-5      | <0.5       | -90%  |
| وقت Onboarding للمطور   | 2 أسبوع  | 3 أيام     | -78%  |

---

## Phase 0: Firefighting (الأسبوعين 1-2)

### 🚨 الإطفاء الفوري - Critical Fixes

### 0.1 Kong Gateway HA

**المشكلة:** نقطة فشل واحدة (SPOF)
**الأثر:** أي عطل في Kong = توقف كامل للمنصة

```yaml
# File: infrastructure/kong/kong-ha.yml
# Priority: P0 - CRITICAL

deployment:
  replicas: 3
  strategy:
    type: RollingUpdate
    maxUnavailable: 1
    maxSurge: 1

  affinity:
    podAntiAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        - labelSelector:
            matchLabels:
              app: kong
          topologyKey: kubernetes.io/hostname

health_checks:
  liveness:
    path: /status
    interval: 10s
    timeout: 5s
    failureThreshold: 3
  readiness:
    path: /status/ready
    interval: 5s
    timeout: 3s
```

**المهام:**

- [ ] تفعيل Kong replicas (3 instances)
- [ ] تكوين Pod Anti-Affinity
- [ ] إضافة Health Checks
- [ ] تكوين Session Affinity للـ WebSockets
- [ ] اختبار Failover Scenario

**Owner:** DevOps Lead
**Deadline:** Day 5
**Verification:** Chaos test - kill pod, verify <5s recovery

---

### 0.2 NDVI Cache Layer

**المشكلة:** Offline-First يتعارض مع Real-time NDVI
**الأثر:** تطبيق "ميداني" لا يعمل بدون إنترنت

```typescript
// File: shared/libs/cache/ndvi-cache.service.ts
// Priority: P0 - CRITICAL

import { Injectable } from "@nestjs/common";
import { Redis } from "ioredis";

interface NDVICacheEntry {
  value: number;
  timestamp: Date;
  source: "satellite" | "interpolated" | "historical";
  confidence: number;
  ttl_hours: number;
}

@Injectable()
export class NDVICacheService {
  private readonly redis: Redis;
  private readonly DEFAULT_TTL_HOURS = 24;
  private readonly STALE_TTL_HOURS = 72;

  /**
   * استراتيجية Cache متعددة المستويات:
   *
   * L1: Memory (5 دقائق) - أسرع وصول
   * L2: Redis (24 ساعة) - مشترك بين الخوادم
   * L3: PostgreSQL (72 ساعة) - Stale fallback
   */

  async getNDVI(fieldId: string, date: Date): Promise<NDVICacheEntry | null> {
    // 1. Try L1 (Memory)
    const l1Key = `ndvi:l1:${fieldId}:${this.dateKey(date)}`;
    const l1Value = this.memoryCache.get(l1Key);
    if (l1Value) return l1Value;

    // 2. Try L2 (Redis)
    const l2Key = `ndvi:${fieldId}:${this.dateKey(date)}`;
    const l2Value = await this.redis.get(l2Key);
    if (l2Value) {
      const entry = JSON.parse(l2Value);
      this.memoryCache.set(l1Key, entry, 300); // 5 min
      return entry;
    }

    // 3. Try L3 (Stale from DB)
    const staleEntry = await this.getStaleFromDB(fieldId, date);
    if (staleEntry) {
      staleEntry.source = "historical";
      staleEntry.confidence *= 0.8; // Reduce confidence
      return staleEntry;
    }

    // 4. Interpolation fallback
    return this.interpolateFromNeighbors(fieldId, date);
  }

  async setNDVI(
    fieldId: string,
    date: Date,
    value: number,
    source: string,
  ): Promise<void> {
    const entry: NDVICacheEntry = {
      value,
      timestamp: new Date(),
      source: source as any,
      confidence: source === "satellite" ? 0.95 : 0.75,
      ttl_hours: this.DEFAULT_TTL_HOURS,
    };

    const key = `ndvi:${fieldId}:${this.dateKey(date)}`;

    // Set in Redis with TTL
    await this.redis.setex(
      key,
      this.DEFAULT_TTL_HOURS * 3600,
      JSON.stringify(entry),
    );

    // Set in Memory
    this.memoryCache.set(
      `ndvi:l1:${fieldId}:${this.dateKey(date)}`,
      entry,
      300,
    );

    // Persist to DB for stale fallback
    await this.persistToStaleDB(fieldId, date, entry);
  }

  private async interpolateFromNeighbors(
    fieldId: string,
    date: Date,
  ): Promise<NDVICacheEntry | null> {
    // Get spatial neighbors within 5km
    const neighbors = await this.getNeighborFields(fieldId, 5000);

    if (neighbors.length === 0) return null;

    // Inverse Distance Weighting
    const values = await Promise.all(
      neighbors.map((n) =>
        this.redis.get(`ndvi:${n.id}:${this.dateKey(date)}`),
      ),
    );

    const validValues = values
      .filter((v) => v !== null)
      .map((v) => JSON.parse(v!));

    if (validValues.length === 0) return null;

    const interpolated =
      validValues.reduce((sum, v) => sum + v.value, 0) / validValues.length;

    return {
      value: interpolated,
      timestamp: new Date(),
      source: "interpolated",
      confidence: 0.6 * (validValues.length / neighbors.length),
      ttl_hours: 12, // Shorter TTL for interpolated
    };
  }

  private dateKey(date: Date): string {
    return date.toISOString().split("T")[0];
  }
}
```

**المهام:**

- [ ] إنشاء NDVICacheService
- [ ] تكوين Redis Cluster
- [ ] إضافة Stale DB schema
- [ ] تنفيذ Interpolation algorithm
- [ ] اختبار Offline scenarios

**Owner:** Backend Lead
**Deadline:** Day 7
**Verification:** Network disconnect test, verify data availability

---

### 0.3 PostGIS Critical Indexes

**المشكلة:** استعلامات مكانية بدون فهارس = 400% تكلفة زائدة
**الأثر:** $X/شهر مهدرة على compute

```sql
-- File: migrations/0001_critical_indexes.sql
-- Priority: P0 - CRITICAL

-- 1. GIST Index على geometry columns
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_geometry_gist
ON fields USING GIST (geometry);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_field_boundaries_geom_gist
ON field_boundaries USING GIST (boundary);

-- 2. Composite index للاستعلامات الشائعة
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_fields_tenant_active
ON fields (tenant_id, is_active)
WHERE is_active = true;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ndvi_readings_field_date
ON ndvi_readings (field_id, reading_date DESC);

-- 3. Partial index للبيانات الحديثة
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sensor_readings_recent
ON sensor_readings (field_id, created_at DESC)
WHERE created_at > NOW() - INTERVAL '30 days';

-- 4. BRIN index للبيانات الزمنية الكبيرة
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_weather_data_time_brin
ON weather_data USING BRIN (timestamp);

-- 5. تحليل الجداول بعد الفهرسة
ANALYZE fields;
ANALYZE field_boundaries;
ANALYZE ndvi_readings;
ANALYZE sensor_readings;
ANALYZE weather_data;
```

**المهام:**

- [ ] تنفيذ migration في off-peak hours
- [ ] مراقبة index creation progress
- [ ] التحقق من query plans بعد الفهرسة
- [ ] إضافة PGBouncer connection pooling
- [ ] تكوين Materialized Views للتقارير

**Owner:** DBA / Backend Lead
**Deadline:** Day 4
**Verification:** EXPLAIN ANALYZE على top 10 queries

---

### 0.4 PGBouncer Connection Pooling

**المشكلة:** كل service يفتح connections مباشرة = exhaustion
**الأثر:** connection limit errors تحت الضغط

```yaml
# File: infrastructure/pgbouncer/pgbouncer.yml
# Priority: P0 - CRITICAL

apiVersion: apps/v1
kind: Deployment
metadata:
  name: pgbouncer
spec:
  replicas: 2
  template:
    spec:
      containers:
        - name: pgbouncer
          image: edoburu/pgbouncer:1.21.0
          env:
            - name: POOL_MODE
              value: "transaction"
            - name: DEFAULT_POOL_SIZE
              value: "20"
            - name: MIN_POOL_SIZE
              value: "5"
            - name: RESERVE_POOL_SIZE
              value: "5"
            - name: MAX_CLIENT_CONN
              value: "1000"
            - name: MAX_DB_CONNECTIONS
              value: "100"
          ports:
            - containerPort: 5432
          resources:
            requests:
              memory: "128Mi"
              cpu: "100m"
            limits:
              memory: "256Mi"
              cpu: "500m"
```

**المهام:**

- [ ] نشر PGBouncer deployment
- [ ] تحديث connection strings في جميع الخدمات
- [ ] تكوين monitoring لـ connection stats
- [ ] اختبار load scenario

**Owner:** DevOps Lead
**Deadline:** Day 3
**Verification:** 500 concurrent connections test

---

## Phase 1: Stabilization (الأسبوعين 3-4)

### ⚖️ التثبيت والتوحيد

### 1.1 Platform Manifest

**المشكلة:** لا توجد نقطة حقيقة واحدة للإصدارات
**الأثر:** "Works on my machine" + Integration failures

```yaml
# File: .platform-manifest.yml
# Priority: P1 - HIGH

schema_version: "1.0"
platform_version: "15.5.0"
last_updated: "2024-01-20"
maintainer: "platform-team@sahool.io"

# ═══════════════════════════════════════════════════════════════════
# Runtime Versions (Enforced)
# ═══════════════════════════════════════════════════════════════════

runtimes:
  node:
    version: "20.10.0"
    package_manager: "pnpm@8.14.0"
    enforcement: "strict"

  python:
    version: "3.11.7"
    package_manager: "poetry@1.7.1"
    enforcement: "strict"

  flutter:
    version: "3.16.5"
    dart_version: "3.2.3"
    enforcement: "strict"

# ═══════════════════════════════════════════════════════════════════
# Shared Libraries (Centralized)
# ═══════════════════════════════════════════════════════════════════

shared_libs:
  typescript:
    - name: "@sahool/auth"
      version: "1.2.0"
      path: "shared/libs/auth"
      consumers: ["api-gateway", "mobile-bff", "all-services"]

    - name: "@sahool/events"
      version: "1.1.0"
      path: "shared/libs/events"
      consumers: ["all-services"]

    - name: "@sahool/cache"
      version: "1.0.0"
      path: "shared/libs/cache"
      consumers: ["satellite-service", "virtual-sensors", "yield-prediction"]

    - name: "@sahool/field-first"
      version: "1.0.0"
      path: "shared/libs/field-first"
      consumers: ["all-field-services"]

  python:
    - name: "sahool-common"
      version: "1.0.0"
      path: "shared/python/sahool_common"
      consumers: ["virtual-sensors", "crop-growth-timing"]

# ═══════════════════════════════════════════════════════════════════
# Infrastructure Components
# ═══════════════════════════════════════════════════════════════════

infrastructure:
  postgres:
    version: "16.1"
    extensions:
      - postgis: "3.4"
      - pg_stat_statements: "1.10"
    min_connections: 20
    max_connections: 100

  redis:
    version: "7.2"
    cluster_mode: true
    min_nodes: 3

  nats:
    version: "2.10"
    jetstream: true
    cluster_size: 3

  kong:
    version: "3.5"
    db_mode: "db-less"
    replicas: 3

# ═══════════════════════════════════════════════════════════════════
# Services Registry
# ═══════════════════════════════════════════════════════════════════

services:
  # ─────────────────────────────────────────────────────────────────
  # Field-First Activated Services
  # ─────────────────────────────────────────────────────────────────

  satellite-service:
    type: python
    version: "1.3.0"
    port: 8090
    status: active
    field_first: true
    dependencies:
      - "@sahool/cache"
      - "sahool-common"

  virtual-sensors:
    type: python
    version: "1.2.0"
    port: 8085
    status: active
    field_first: true
    dependencies:
      - "@sahool/events"
      - "sahool-common"

  yield-prediction:
    type: nestjs
    version: "1.1.0"
    port: 8091
    status: active
    field_first: true
    dependencies:
      - "@sahool/auth"
      - "@sahool/field-first"

  lai-estimation:
    type: nestjs
    version: "1.1.0"
    port: 8093
    status: active
    field_first: true
    dependencies:
      - "@sahool/auth"
      - "@sahool/field-first"

  # ─────────────────────────────────────────────────────────────────
  # Core Services
  # ─────────────────────────────────────────────────────────────────

  api-gateway:
    type: nestjs
    version: "2.0.0"
    port: 3000
    status: active
    dependencies:
      - "@sahool/auth"

  notification-service:
    type: nestjs
    version: "1.5.0"
    port: 8083
    status: active
    dependencies:
      - "@sahool/events"

# ═══════════════════════════════════════════════════════════════════
# Compatibility Matrix
# ═══════════════════════════════════════════════════════════════════

compatibility:
  mobile_app:
    min_version: "2.1.0"
    recommended_version: "2.3.0"
    breaking_changes_after: "3.0.0"

  api:
    current_version: "v1"
    deprecated_versions: []
    sunset_versions: []

# ═══════════════════════════════════════════════════════════════════
# Validation Rules
# ═══════════════════════════════════════════════════════════════════

validation:
  pre_commit:
    - check_node_version
    - check_python_version
    - check_dependencies
    - lint
    - type_check

  pre_deploy:
    - manifest_validation
    - dependency_audit
    - security_scan
    - integration_tests
```

**المهام:**

- [ ] إنشاء .platform-manifest.yml
- [ ] كتابة manifest validator script
- [ ] إضافة pre-commit hook
- [ ] تكوين CI/CD للتحقق
- [ ] توثيق في README

**Owner:** Platform Lead
**Deadline:** Day 14
**Verification:** CI blocks on manifest violation

---

### 1.2 Unified Auth Library

**المشكلة:** 5 تطبيقات مختلفة لـ JWT validation
**الأثر:** Security inconsistencies + maintenance overhead

```typescript
// File: shared/libs/auth/src/index.ts
// Priority: P1 - HIGH

export * from "./guards/jwt.guard";
export * from "./guards/roles.guard";
export * from "./guards/tenant.guard";
export * from "./decorators/current-user.decorator";
export * from "./decorators/requires-role.decorator";
export * from "./services/token.service";
export * from "./middleware/auth.middleware";
export * from "./types";

// File: shared/libs/auth/src/guards/jwt.guard.ts

import {
  Injectable,
  CanActivate,
  ExecutionContext,
  UnauthorizedException,
} from "@nestjs/common";
import { TokenService } from "../services/token.service";

@Injectable()
export class JwtGuard implements CanActivate {
  constructor(private readonly tokenService: TokenService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest();
    const token = this.extractToken(request);

    if (!token) {
      throw new UnauthorizedException("No token provided");
    }

    try {
      const payload = await this.tokenService.verifyToken(token);

      // Attach user to request
      request.user = {
        id: payload.sub,
        email: payload.email,
        roles: payload.roles,
        tenantId: payload.tenant_id,
        permissions: payload.permissions,
      };

      return true;
    } catch (error) {
      throw new UnauthorizedException("Invalid token");
    }
  }

  private extractToken(request: any): string | null {
    const authHeader = request.headers.authorization;
    if (!authHeader) return null;

    const [type, token] = authHeader.split(" ");
    return type === "Bearer" ? token : null;
  }
}

// File: shared/libs/auth/src/services/token.service.ts

import { Injectable } from "@nestjs/common";
import * as jose from "jose";

export interface TokenPayload {
  sub: string;
  email: string;
  roles: string[];
  tenant_id: string;
  permissions: string[];
  iat: number;
  exp: number;
}

@Injectable()
export class TokenService {
  private readonly publicKey: jose.KeyLike;
  private readonly issuer: string;
  private readonly audience: string;

  constructor() {
    // Load from environment
    this.issuer = process.env.JWT_ISSUER || "sahool";
    this.audience = process.env.JWT_AUDIENCE || "sahool-api";
  }

  async verifyToken(token: string): Promise<TokenPayload> {
    const { payload } = await jose.jwtVerify(token, this.publicKey, {
      issuer: this.issuer,
      audience: this.audience,
    });

    return payload as unknown as TokenPayload;
  }

  async generateToken(user: any, expiresIn: string = "1h"): Promise<string> {
    // Implementation
  }
}
```

**المهام:**

- [ ] إنشاء @sahool/auth package
- [ ] Migrate جميع الخدمات لاستخدام الـ library
- [ ] إزالة الـ duplicate auth code
- [ ] إضافة unit tests
- [ ] توثيق API

**Owner:** Security Lead
**Deadline:** Day 21
**Verification:** All services using same auth lib

---

### 1.3 Offline Conflict Resolution

**المشكلة:** لا توجد قواعد واضحة لحل التعارضات
**الأثر:** Data loss أو silent overwrites

```dart
// File: mobile/lib/core/sync/conflict_resolver.dart
// Priority: P1 - HIGH

enum ConflictStrategy {
  serverWins,
  clientWins,
  merge,
  manual,
}

class ConflictResolutionRule {
  final String entityType;
  final ConflictStrategy defaultStrategy;
  final Map<String, ConflictStrategy> fieldStrategies;

  const ConflictResolutionRule({
    required this.entityType,
    required this.defaultStrategy,
    this.fieldStrategies = const {},
  });
}

class ConflictResolver {
  static const Map<String, ConflictResolutionRule> rules = {
    // ─────────────────────────────────────────────────────────────────
    // Field Data: Server wins (authoritative source)
    // ─────────────────────────────────────────────────────────────────
    'field': ConflictResolutionRule(
      entityType: 'field',
      defaultStrategy: ConflictStrategy.serverWins,
      fieldStrategies: {
        'notes': ConflictStrategy.merge,
        'local_name': ConflictStrategy.clientWins,
      },
    ),

    // ─────────────────────────────────────────────────────────────────
    // Sensor Readings: Last write wins (time-based)
    // ─────────────────────────────────────────────────────────────────
    'sensor_reading': ConflictResolutionRule(
      entityType: 'sensor_reading',
      defaultStrategy: ConflictStrategy.serverWins,
    ),

    // ─────────────────────────────────────────────────────────────────
    // Tasks: Merge with user confirmation
    // ─────────────────────────────────────────────────────────────────
    'task': ConflictResolutionRule(
      entityType: 'task',
      defaultStrategy: ConflictStrategy.merge,
      fieldStrategies: {
        'status': ConflictStrategy.manual,
        'completed_at': ConflictStrategy.serverWins,
      },
    ),

    // ─────────────────────────────────────────────────────────────────
    // User Preferences: Client wins (user's device)
    // ─────────────────────────────────────────────────────────────────
    'user_preference': ConflictResolutionRule(
      entityType: 'user_preference',
      defaultStrategy: ConflictStrategy.clientWins,
    ),
  };

  Future<T> resolve<T>({
    required String entityType,
    required T serverVersion,
    required T clientVersion,
    required DateTime serverTimestamp,
    required DateTime clientTimestamp,
  }) async {
    final rule = rules[entityType];
    if (rule == null) {
      // Default: Server wins
      return serverVersion;
    }

    switch (rule.defaultStrategy) {
      case ConflictStrategy.serverWins:
        return serverVersion;

      case ConflictStrategy.clientWins:
        return clientVersion;

      case ConflictStrategy.merge:
        return _mergeVersions(serverVersion, clientVersion, rule);

      case ConflictStrategy.manual:
        return _promptUserResolution(serverVersion, clientVersion);
    }
  }

  T _mergeVersions<T>(T server, T client, ConflictResolutionRule rule) {
    // Field-level merge based on rule.fieldStrategies
    // Implementation depends on entity structure
    throw UnimplementedError();
  }

  Future<T> _promptUserResolution<T>(T server, T client) async {
    // Show UI for user to choose
    throw UnimplementedError();
  }
}
```

**المهام:**

- [ ] تعريف conflict rules لكل entity
- [ ] تنفيذ ConflictResolver
- [ ] إضافة UI للـ manual resolution
- [ ] اختبار scenarios
- [ ] توثيق القواعد

**Owner:** Mobile Lead
**Deadline:** Day 28
**Verification:** Offline sync test with conflicts

---

## Phase 2: Prevention (الأسابيع 5-8)

### 🛡️ الوقاية والمراقبة

### 2.1 Pre-commit Hooks

**المشكلة:** Issues تُكتشف في CI بعد ساعات
**الأثر:** Developer time wasted + delayed feedback

```yaml
# File: .husky/pre-commit
# Priority: P2 - MEDIUM

#!/bin/sh
. "$(dirname "$0")/_/husky.sh"

echo "🔍 Running pre-commit checks..."

# 1. Manifest Validation
echo "📋 Checking platform manifest..."
node scripts/validate-manifest.js || exit 1

# 2. Version Checks
echo "🔢 Checking runtime versions..."
node scripts/check-versions.js || exit 1

# 3. Lint Staged Files
echo "🧹 Linting staged files..."
npx lint-staged || exit 1

# 4. Type Check
echo "📝 Type checking..."
npx tsc --noEmit || exit 1

# 5. Security Audit (quick)
echo "🔒 Quick security check..."
npm audit --audit-level=high || exit 1

echo "✅ All pre-commit checks passed!"
```

```javascript
// File: scripts/validate-manifest.js

const yaml = require("js-yaml");
const fs = require("fs");
const path = require("path");

const MANIFEST_PATH = ".platform-manifest.yml";

function validateManifest() {
  console.log("Validating platform manifest...");

  const manifest = yaml.load(fs.readFileSync(MANIFEST_PATH, "utf8"));
  const errors = [];

  // Check Node version
  const requiredNode = manifest.runtimes.node.version;
  const currentNode = process.version.slice(1);
  if (currentNode !== requiredNode) {
    errors.push(
      `Node version mismatch: required ${requiredNode}, found ${currentNode}`,
    );
  }

  // Check service ports are unique
  const ports = new Set();
  for (const [name, service] of Object.entries(manifest.services)) {
    if (ports.has(service.port)) {
      errors.push(`Duplicate port ${service.port} in service ${name}`);
    }
    ports.add(service.port);
  }

  // Check dependencies exist
  for (const [name, service] of Object.entries(manifest.services)) {
    for (const dep of service.dependencies || []) {
      const libExists =
        manifest.shared_libs.typescript.some((l) => l.name === dep) ||
        manifest.shared_libs.python.some((l) => l.name === dep);
      if (!libExists && !dep.startsWith("@sahool/")) {
        errors.push(`Unknown dependency ${dep} in service ${name}`);
      }
    }
  }

  if (errors.length > 0) {
    console.error("❌ Manifest validation failed:");
    errors.forEach((e) => console.error(`  - ${e}`));
    process.exit(1);
  }

  console.log("✅ Manifest is valid");
}

validateManifest();
```

**المهام:**

- [ ] إعداد Husky
- [ ] كتابة validation scripts
- [ ] تكوين lint-staged
- [ ] توثيق للمطورين
- [ ] اختبار على PRs

**Owner:** DX Lead
**Deadline:** Day 35
**Verification:** PR blocked on hook failure

---

### 2.2 Health Monitoring Dashboard

**المشكلة:** لا رؤية موحدة لصحة النظام
**الأثر:** Issues discovered by users, not monitoring

```yaml
# File: infrastructure/monitoring/health-dashboard.yml
# Priority: P2 - MEDIUM

# Grafana Dashboard Configuration
dashboard:
  title: "SAHOOL Platform Health"
  refresh: "30s"

  panels:
    # ─────────────────────────────────────────────────────────────────
    # Row 1: Critical Metrics
    # ─────────────────────────────────────────────────────────────────

    - title: "Service Health"
      type: stat
      query: |
        sum(up{job=~"sahool-.*"}) / count(up{job=~"sahool-.*"}) * 100
      thresholds:
        - value: 95
          color: green
        - value: 80
          color: yellow
        - value: 0
          color: red

    - title: "API Latency P95"
      type: gauge
      query: |
        histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{job="api-gateway"}[5m]))
      thresholds:
        - value: 0.5
          color: green
        - value: 1
          color: yellow
        - value: 2
          color: red

    - title: "Error Rate"
      type: stat
      query: |
        sum(rate(http_requests_total{status=~"5.."}[5m])) / sum(rate(http_requests_total[5m])) * 100
      thresholds:
        - value: 1
          color: green
        - value: 5
          color: yellow
        - value: 10
          color: red

    # ─────────────────────────────────────────────────────────────────
    # Row 2: Field-First Metrics
    # ─────────────────────────────────────────────────────────────────

    - title: "ActionTemplate Generation Rate"
      type: graph
      query: |
        sum(rate(action_templates_generated_total[5m])) by (service)

    - title: "NATS Message Throughput"
      type: graph
      query: |
        sum(rate(nats_messages_published_total[5m])) by (topic)

    - title: "Offline Sync Queue"
      type: stat
      query: |
        sum(offline_sync_queue_size)

    # ─────────────────────────────────────────────────────────────────
    # Row 3: Infrastructure
    # ─────────────────────────────────────────────────────────────────

    - title: "PostgreSQL Connections"
      type: graph
      query: |
        pg_stat_activity_count{state="active"}
      thresholds:
        - value: 80
          color: yellow
        - value: 95
          color: red

    - title: "Redis Memory Usage"
      type: gauge
      query: |
        redis_memory_used_bytes / redis_memory_max_bytes * 100

    - title: "Kong Request Rate"
      type: graph
      query: |
        sum(rate(kong_http_status[5m])) by (code)

# Alert Rules
alerts:
  - name: HighErrorRate
    condition: error_rate > 5%
    for: 5m
    severity: critical
    notify: [slack, pagerduty]

  - name: SlowAPI
    condition: p95_latency > 2s
    for: 10m
    severity: warning
    notify: [slack]

  - name: DatabaseConnectionHigh
    condition: pg_connections > 80%
    for: 5m
    severity: warning
    notify: [slack]
```

**المهام:**

- [ ] نشر Prometheus + Grafana
- [ ] تكوين service metrics
- [ ] إنشاء dashboard
- [ ] تكوين alerts
- [ ] توثيق runbooks

**Owner:** SRE Lead
**Deadline:** Day 42
**Verification:** Alert fires on simulated outage

---

### 2.3 Architecture Decision Records (ADRs)

**المشكلة:** قرارات معمارية غير موثقة
**الأثر:** Repeated debates + inconsistent decisions

```markdown
<!-- File: docs/adr/0001-field-first-architecture.md -->

# ADR-0001: Field-First Architecture Pattern

## Status

Accepted

## Context

SAHOOL is designed to serve farmers in rural Yemen where:

- Internet connectivity is unreliable
- Field workers need real-time decisions
- Analysis services produce complex outputs

## Decision

We adopt Field-First Architecture where:

1. Every analysis service MUST produce an ActionTemplate
2. All data must be available offline within 24h TTL
3. Notifications use NATS event spine
4. Badge system distinguishes data sources

## Consequences

### Positive

- Mobile app works offline
- Field workers get actionable guidance
- Clear data provenance

### Negative

- More complex service contracts
- Higher storage requirements on device
- Sync complexity increases

## Compliance

All new services MUST:

- Implement ActionTemplate endpoints
- Publish to NATS on analysis completion
- Include Badge in responses

## Related

- ADR-0002: Offline-First Mobile Architecture
- ADR-0003: NATS Event Spine Pattern
```

**المهام:**

- [ ] إنشاء ADR template
- [ ] توثيق القرارات الحالية (10 ADRs)
- [ ] إضافة ADR review process
- [ ] ربط بـ PR template

**Owner:** Architect
**Deadline:** Day 56
**Verification:** 10 ADRs documented

---

## Success Metrics | معايير النجاح

### Sprint 0 (Week 2)

| Metric          | Target             | Verification                   |
| --------------- | ------------------ | ------------------------------ |
| Kong HA         | 3 replicas running | `kubectl get pods -l app=kong` |
| NDVI Cache Hit  | >80%               | Redis stats                    |
| Query Time      | <100ms avg         | pg_stat_statements             |
| Connection Pool | <50% usage         | PGBouncer stats                |

### Sprint 1 (Week 4)

| Metric               | Target        | Verification       |
| -------------------- | ------------- | ------------------ |
| Manifest Coverage    | 100% services | CI check           |
| Auth Lib Adoption    | 100% services | Dependency audit   |
| Conflict Rules       | All entities  | Code review        |
| Zero Downtime Deploy | Success       | Canary deploy test |

### Sprint 2 (Week 8)

| Metric               | Target       | Verification     |
| -------------------- | ------------ | ---------------- |
| Pre-commit Pass Rate | >95%         | Git hooks        |
| Alert Response Time  | <5 min       | PagerDuty SLA    |
| ADR Coverage         | 10 documents | Directory count  |
| MTTR                 | <30 min      | Incident reports |

---

## Risk Register | سجل المخاطر

| Risk                   | Probability | Impact | Mitigation               |
| ---------------------- | ----------- | ------ | ------------------------ |
| Feature freeze延長     | Medium      | High   | Weekly stakeholder sync  |
| Key person dependency  | Medium      | High   | Pair programming + docs  |
| Scope creep            | High        | Medium | Strict change control    |
| Integration regression | Medium      | High   | Comprehensive test suite |
| Team fatigue           | Medium      | Medium | Celebrate milestones     |

---

## Communication Plan | خطة التواصل

### Weekly

- **Monday:** Sprint planning + blocker review
- **Wednesday:** Technical deep-dive
- **Friday:** Demo + retrospective

### Stakeholders

- **Engineering:** Daily standups
- **Product:** Weekly status
- **Leadership:** Bi-weekly executive summary
- **Board:** Monthly progress report

---

## Rollback Plan | خطة التراجع

If recovery efforts cause instability:

1. **Immediate:** Revert to pre-recovery state
2. **24h:** Root cause analysis
3. **48h:** Revised approach proposal
4. **72h:** Stakeholder approval for retry

---

## Appendix

### A. Team Allocation

| Role    | Allocation | Sprint 0    | Sprint 1 | Sprint 2    |
| ------- | ---------- | ----------- | -------- | ----------- |
| Backend | 3 FTE      | Kong, Cache | Auth lib | Monitoring  |
| DevOps  | 2 FTE      | PGBouncer   | CI/CD    | Alerts      |
| Mobile  | 2 FTE      | -           | Sync     | Conflict UI |
| QA      | 1 FTE      | Testing     | Testing  | Testing     |

### B. Dependencies

- Redis Cluster license (if applicable)
- PagerDuty account
- Grafana Cloud (or self-hosted)

### C. Budget

| Item              | Cost  | Justification      |
| ----------------- | ----- | ------------------ |
| Redis Enterprise  | $X/mo | HA requirement     |
| Monitoring        | $Y/mo | Grafana Cloud      |
| Chaos Engineering | $Z/mo | Gremlin (optional) |

---

**Document Owner:** Platform Team
**Last Updated:** 2024-01-20
**Next Review:** 2024-01-27
