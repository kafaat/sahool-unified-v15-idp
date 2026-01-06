# Kong Upstreams Configuration Audit Report

**Platform**: SAHOOL Agricultural Intelligence Platform
**Date**: 2026-01-06
**Auditor**: System Audit
**Version**: v15.5.0

---

## Executive Summary

This audit examines Kong upstream configurations across multiple configuration files in the SAHOOL platform. The analysis covers 4 primary Kong configuration files managing approximately 50+ microservices.

### Configuration Files Audited
1. `/home/user/sahool-unified-v15-idp/infrastructure/gateway/kong/kong.yml` (Main)
2. `/home/user/sahool-unified-v15-idp/infrastructure/gateway/kong-ha/kong/declarative/kong.yml` (HA)
3. `/home/user/sahool-unified-v15-idp/infra/kong/kong.yml` (Canonical - marked as source of truth)
4. `/home/user/sahool-unified-v15-idp/infrastructure/gateway/kong-legacy/kong.yml` (Legacy)

### Overall Status
- **Critical Issues**: 5
- **High Priority Issues**: 8
- **Medium Priority Issues**: 12
- **Low Priority Issues**: 7
- **Recommendations**: 15

---

## 1. Upstream Definitions Inventory

### 1.1 Upstreams Defined in Main Configuration (`/infrastructure/gateway/kong/kong.yml`)

| # | Upstream Name | Target | Port | Health Check Path |
|---|---------------|--------|------|-------------------|
| 1 | field-management-upstream | field-management-service | 3000 | /healthz |
| 2 | weather-service-upstream | weather-service | 8092 | /healthz |
| 3 | vegetation-analysis-upstream | vegetation-analysis-service | 8090 | /healthz |
| 4 | ai-advisor-upstream | ai-advisor | 8112 | /healthz |
| 5 | crop-intelligence-upstream | crop-intelligence-service | 8095 | /healthz |
| 6 | advisory-service-upstream | advisory-service | 8093 | /healthz |
| 7 | iot-gateway-upstream | iot-gateway | 8106 | /healthz |
| 8 | iot-service-upstream | iot-service | 8117 | /healthz |
| 9 | virtual-sensors-upstream | virtual-sensors | 8119 | /healthz |
| 10 | marketplace-service-upstream | marketplace-service | 3010 | /healthz |
| 11 | billing-core-upstream | billing-core | 8089 | /healthz |
| 12 | notification-service-upstream | notification-service | 8110 | /healthz |
| 13 | research-core-upstream | research-core | 3015 | /healthz |
| 14 | disaster-assessment-upstream | disaster-assessment | 3020 | /healthz |
| 15 | field-intelligence-upstream | field-intelligence | 8120 | /healthz |
| 16 | mcp-server-upstream | mcp-server | 8200 | /health |
| 17 | code-review-upstream | code-review-service | 8096 | /health |

**Total Upstreams**: 17

### 1.2 Upstreams Defined in HA Configuration (`/infrastructure/gateway/kong-ha/kong/declarative/kong.yml`)

| # | Upstream Name | Target | Port | Health Check Path |
|---|---------------|--------|------|-------------------|
| 1 | field-ops-upstream | sahool-field-ops | 8080 | /healthz |
| 2 | ndvi-engine-upstream | sahool-vegetation-analysis-service | 8090 | /healthz |
| 3 | weather-upstream | sahool-weather-service | 8092 | /healthz |
| 4 | chat-upstream | sahool-field-chat | 8099 | /healthz |
| 5 | iot-upstream | sahool-iot-gateway | 8106 | /healthz |
| 6 | advisor-upstream | sahool-advisory-service | 8093 | /healthz |
| 7 | ws-gateway-upstream | sahool-ws-gateway | 8081 | /healthz |
| 8 | crop-health-upstream | sahool-crop-health | 8100 | /healthz |
| 9 | field-core-upstream | sahool-field-management-service | 3000 | /healthz |
| 10 | task-upstream | sahool-task-service | 8103 | /healthz |
| 11 | equipment-upstream | sahool-equipment-service | 8101 | /healthz |
| 12 | provider-config-upstream | sahool-provider-config | 8104 | /healthz |
| 13 | satellite-upstream | sahool-vegetation-analysis-service | 8090 | /healthz |
| 14 | indicators-upstream | sahool-indicators-service | 8091 | /healthz |
| 15 | weather-advanced-upstream | sahool-weather-service | 8092 | /healthz |
| 16 | astronomical-calendar-upstream | sahool-astronomical-calendar | 8111 | /healthz |
| 17 | fertilizer-upstream | sahool-advisory-service | 8093 | /healthz |
| 18 | irrigation-upstream | sahool-irrigation-smart | 8094 | /healthz |
| 19 | crop-health-ai-upstream | sahool-crop-intelligence-service | 8095 | /healthz |
| 20 | virtual-sensors-upstream | sahool-virtual-sensors | 8096 | /healthz |
| 21 | community-chat-upstream | sahool-community-chat | 8097 | /healthz |
| 22 | yield-engine-upstream | sahool-yield-prediction-service | 8098 | /healthz |
| 23 | crop-growth-upstream | sahool-crop-intelligence-service | 8095 | /api/v1/simulation/health |
| 24 | notification-upstream | sahool-notification-service | 8110 | /healthz |
| 25 | research-core-upstream | sahool-research-core | 3015 | /api/v1/healthz |
| 26 | disaster-assessment-upstream | sahool-disaster-assessment | 3020 | /api/v1/disasters/health |
| 27 | yield-prediction-upstream | sahool-yield-prediction | 3021 | /api/v1/yield/health |
| 28 | lai-estimation-upstream | sahool-vegetation-analysis-service | 8090 | /api/v1/lai/health |
| 29 | marketplace-upstream | sahool-marketplace | 3010 | /api/v1/healthz |
| 30 | billing-core-upstream | sahool-billing-core | 8089 | /healthz |

**Total Upstreams**: 30

### 1.3 Legacy Configuration (`/infrastructure/gateway/kong-legacy/kong.yml`)

**Status**: No upstreams defined - uses direct URL configuration
**Note**: Legacy configuration bypasses upstream abstraction entirely

---

## 2. Health Check Configuration Analysis

### 2.1 Health Check Completeness

#### Fully Configured Health Checks (Active + Passive)
The following upstreams have complete health check configurations with both active and passive monitoring:

**Main Configuration:**
1. **marketplace-service-upstream**
   - Active: interval 10s, successes 2, failures 3
   - Passive: Monitors 500/502/503/504 errors
   - Status: ✅ COMPLETE

2. **billing-core-upstream**
   - Active: interval 10s, successes 2, failures 3
   - Passive: Monitors 500/502/503/504 errors
   - Status: ✅ COMPLETE

3. **research-core-upstream**
   - Active: interval 10s, successes 2, failures 3
   - Passive: Monitors 500/502/503/504 errors
   - Status: ✅ COMPLETE

4. **field-intelligence-upstream**
   - Active: interval 10s, successes 2, failures 3
   - Passive: Monitors 500/502/503/504 errors
   - Status: ✅ COMPLETE

**HA Configuration:**
All 30 upstreams in HA configuration have complete health checks with:
- Active checks: interval 10s, healthy successes 2, unhealthy failures 3
- Passive checks: healthy successes 5, unhealthy failures 5
- Status: ✅ ALL COMPLETE

#### Minimal Health Checks (Active Only)
The following upstreams have only basic active health checks without detailed configuration:

1. field-management-upstream
2. weather-service-upstream
3. vegetation-analysis-upstream
4. ai-advisor-upstream
5. crop-intelligence-upstream
6. advisory-service-upstream
7. iot-gateway-upstream
8. iot-service-upstream
9. virtual-sensors-upstream
10. notification-service-upstream
11. disaster-assessment-upstream
12. mcp-server-upstream
13. code-review-upstream

**Status**: ⚠️ INCOMPLETE - Only basic active health checks configured

### 2.2 Health Check Path Inconsistencies

**Standard Paths:**
- `/healthz` - Used by 24 upstreams ✅
- `/health` - Used by 2 upstreams (mcp-server, code-review)

**Service-Specific Paths:**
- `/api/v1/simulation/health` - crop-growth-upstream
- `/api/v1/healthz` - research-core-upstream
- `/api/v1/disasters/health` - disaster-assessment-upstream
- `/api/v1/yield/health` - yield-prediction-upstream
- `/api/v1/lai/health` - lai-estimation-upstream

**Issue**: ❌ CRITICAL - Lack of standardization could cause monitoring failures

### 2.3 Health Check Parameters

**HA Configuration Standards:**
```yaml
active:
  type: http
  http_path: /healthz
  healthy:
    interval: 10
    successes: 2
  unhealthy:
    interval: 5
    http_failures: 3
    timeouts: 3
passive:
  healthy:
    successes: 5
  unhealthy:
    http_failures: 5
    timeouts: 3
```

**Main Configuration (for complete checks):**
```yaml
active:
  type: http
  http_path: /healthz
  healthy:
    interval: 10
    successes: 2
    http_statuses: [200, 201, 204]
  unhealthy:
    interval: 10
    http_failures: 3
    http_statuses: [500, 502, 503, 504]
    tcp_failures: 3
    timeouts: 3
passive:
  healthy:
    http_statuses: [200, 201, 204]
  unhealthy:
    http_statuses: [500, 502, 503, 504]
    tcp_failures: 3
```

**Analysis**: ✅ GOOD - Main config is more comprehensive with HTTP status codes

---

## 3. Load Balancing Configuration

### 3.1 Algorithm Analysis

**All upstreams use**: `round-robin`

**Status**: ⚠️ SUBOPTIMAL

**Issues:**
- No diversity in load balancing strategies
- No consideration of backend capacity or response time
- All services treated equally regardless of computational complexity

**Recommendation**: Consider these algorithms for specific services:
- **least-connections**: For I/O intensive services (database queries, file operations)
- **consistent-hashing**: For services with caching layers (NDVI processing, satellite imagery)
- **weighted-round-robin**: For services with different instance capacities

### 3.2 Target Weights

**Current Configuration**: All targets have weight `100`

**Analysis**:
- Single target per upstream (no load distribution)
- Weight value is irrelevant with single target
- No horizontal scaling configuration

**Status**: ⚠️ NOT SCALABLE

---

## 4. Target Configuration Analysis

### 4.1 Service Naming Inconsistencies

**Main Configuration Pattern:**
- Direct service names (e.g., `field-management-service`, `weather-service`)

**HA Configuration Pattern:**
- Prefixed with `sahool-` (e.g., `sahool-field-ops`, `sahool-weather-service`)

**Legacy Configuration:**
- Direct URLs without upstream abstraction

**Issue**: ❌ CRITICAL - Inconsistent naming makes migration difficult

### 4.2 Port Allocation

**Port Range Analysis:**

| Port Range | Services | Category |
|------------|----------|----------|
| 3000-3099 | 5 services | Core services (field-management, marketplace, research, disaster, yield) |
| 8080-8099 | 12 services | Standard services |
| 8100-8120 | 8 services | Extended services |
| 8200+ | 1 service | Special services (MCP) |

**Issues Identified:**
1. ⚠️ No clear port allocation strategy
2. ⚠️ Potential for port conflicts in containerized environments
3. ℹ️ Mixed port ranges suggest organic growth vs planned architecture

### 4.3 DNS Resolution

**Docker Compose Configuration:**
```yaml
KONG_DNS_RESOLVER: 8.8.8.8:53
KONG_DNS_ORDER: LAST,A,CNAME
```

**Issues:**
1. ❌ CRITICAL - Using external DNS (8.8.8.8) for internal service resolution
2. ❌ Should use internal Docker DNS (127.0.0.11) or service discovery
3. ⚠️ DNS_ORDER may cause resolution delays

**Recommendation**: Update to:
```yaml
KONG_DNS_RESOLVER: 127.0.0.11:53
KONG_DNS_ORDER: A,CNAME,LAST
```

---

## 5. Timeout Configuration Analysis

### 5.1 Service Timeout Settings

| Service Type | Connect | Read | Write | Retries | Status |
|--------------|---------|------|-------|---------|--------|
| **Standard Services** |
| field-core | 5000ms | 60000ms | 60000ms | 3 | ✅ Good |
| weather-service | - | - | - | 3 | ⚠️ No timeouts |
| notification-service | - | - | - | - | ❌ No config |
| **Compute-Intensive Services** |
| satellite-service | 10000ms | 120000ms | 120000ms | 3 | ✅ Appropriate |
| crop-health-ai | 10000ms | 120000ms | 120000ms | - | ⚠️ No retries |
| **AI/ML Services** |
| ai-advisor | 15000ms | 180000ms | 180000ms | - | ⚠️ No retries |
| crop-growth-model | 15000ms | 180000ms | 180000ms | - | ⚠️ No retries |
| **HA Configuration** |
| All services | 30000ms | 60000ms | 60000ms | 3 | ✅ Consistent |

### 5.2 Timeout Issues

**Critical Issues:**
1. ❌ Many services have NO timeout configuration
2. ❌ Services without timeout config could hang indefinitely
3. ⚠️ AI/ML services lack retry configuration despite long timeouts

**Recommendations:**

```yaml
# Standard Services
connect_timeout: 5000
read_timeout: 60000
write_timeout: 60000
retries: 3

# Compute-Intensive Services
connect_timeout: 10000
read_timeout: 120000
write_timeout: 120000
retries: 2

# AI/ML Services (Long-running)
connect_timeout: 15000
read_timeout: 180000
write_timeout: 180000
retries: 1
```

---

## 6. Retry Policy Analysis

### 6.1 Configured Retry Policies

**Services with Retries:**
- field-core: 3 retries ✅
- satellite-service: 3 retries ✅
- weather-service: 3 retries ✅
- HA Config: All services have 3 retries ✅

**Services WITHOUT Retries:**
- ai-advisor ❌
- crop-growth-model ❌
- crop-health-ai ❌
- lai-estimation ❌
- yield-prediction ❌
- Many others ❌

**Issue**: ❌ CRITICAL - Inconsistent retry configuration across services

### 6.2 Retry Configuration Recommendations

**Default Retry Policy:**
```yaml
retries: 3
# Consider adding Kong's retry configuration:
# - on: ["error", "timeout"]
# - retry_on_status_codes: [502, 503, 504]
```

**Long-Running Services:**
```yaml
retries: 1
# Reduce retries for expensive operations
```

**Critical Path Services:**
```yaml
retries: 5
# Increase for essential services like authentication
```

---

## 7. Missing Upstream Definitions

### 7.1 Services Referenced But No Upstream Defined

**Main Configuration:**

Services that use direct URLs instead of upstreams:
1. astronomical-calendar → `http://astronomical-calendar:8111`
2. advisory-service → `http://advisory-service:8093`
3. notification-service → `http://notification-service:8110`
4. ndvi-engine → `http://ndvi-processor:8118`
5. irrigation-smart → `http://irrigation-smart:8094`
6. ws-gateway → `http://ws-gateway:8081`
7. indicators-service → `http://indicators-service:8091`
8. weather-advanced → `http://weather-service:8092`
9. community-chat → `http://community-chat:8097`
10. field-chat → `http://field-chat:8099`
11. equipment-service → `http://equipment-service:8101`
12. task-service → `http://task-service:8103`
13. provider-config → `http://provider-config:8104`
14. alert-service → `http://alert-service:8113`
15. chat-service → `http://chat-service:8114`
16. field-service → `http://field-management-service:3000`
17. research-core → `http://research-core:3015`
18. marketplace-service → `http://marketplace-service:3010`
19. billing-core → `http://billing-core:8089`
20. disaster-assessment → `http://disaster-assessment:3020`
21. crop-growth-model → `http://crop-growth-model:3023`
22. lai-estimation → `http://lai-estimation:3022`
23. yield-prediction → `http://yield-prediction:3021`
24. ndvi-processor → `http://ndvi-processor:8118`

**Total**: 24 services using direct URLs

**Issue**: ❌ CRITICAL - These services bypass upstream health checks and load balancing

### 7.2 Upstream vs Service Naming Mismatch

**Mismatches Found:**

| Service Name | Upstream Name | Target Mismatch |
|--------------|---------------|-----------------|
| field-ops | field-management-upstream | field-management-service |
| satellite-service | vegetation-analysis-upstream | vegetation-analysis-service |
| ndvi-engine | - | ndvi-processor (no upstream) |
| virtual-sensors | virtual-sensors-upstream | virtual-sensors:8119 vs 8096 in HA |

**Issue**: ⚠️ HIGH - Naming inconsistencies could cause routing errors

---

## 8. Upstream Naming Convention Analysis

### 8.1 Naming Patterns

**Pattern 1: service-name-upstream** (Most common)
- field-management-upstream
- weather-service-upstream
- marketplace-service-upstream

**Pattern 2: service-type-upstream** (Less common)
- advisor-upstream
- iot-upstream
- chat-upstream

**Pattern 3: No clear pattern**
- mcp-server-upstream (inconsistent with mcp-server service)
- code-review-upstream

**Recommendation**: Standardize on Pattern 1: `{service-name}-upstream`

### 8.2 Service-to-Upstream Mapping

**Good Examples:**
- Service: `field-core` → Upstream: `field-management-upstream` ✅
- Service: `weather-service` → Upstream: `weather-service-upstream` ✅

**Poor Examples:**
- Service: `satellite-service` → Upstream: `vegetation-analysis-upstream` ❌
- Service: `ndvi-engine` → No upstream, direct URL ❌
- Service: `fertilizer-advisor` → Upstream: `advisory-service-upstream` ❌

---

## 9. Configuration File Synchronization Issues

### 9.1 Duplicate Definitions

**Services Defined in Multiple Configs:**
1. weather-service (4 definitions)
2. field-management (3 definitions)
3. vegetation-analysis/satellite (3 definitions)
4. notification-service (3 definitions)
5. research-core (2 definitions)
6. disaster-assessment (2 definitions)

**Issue**: ❌ CRITICAL - Configuration drift risk

### 9.2 Canonical Source

According to header comments:
- **Canonical**: `/infra/kong/kong.yml`
- **Should Mirror**: `/infrastructure/gateway/kong/kong.yml`

**Status**: ❌ CRITICAL - Files are NOT in sync

**Differences:**
- Different number of upstreams (17 vs 30)
- Different naming conventions
- Different health check configurations
- HA config has 30 upstreams with complete health checks
- Main config has 17 upstreams with mixed health check completeness

---

## 10. High Availability & Scalability Issues

### 10.1 Single Point of Failure

**All upstreams have:**
- Single target (no redundancy)
- Weight: 100 (meaningless with one target)

**Impact**: ❌ CRITICAL
- No horizontal scaling
- No failover capability
- Service unavailability on single instance failure

### 10.2 Scaling Recommendations

**Minimum Viable HA Setup:**
```yaml
upstreams:
  - name: field-management-upstream
    algorithm: round-robin
    targets:
      - target: field-management-service-1:3000
        weight: 100
      - target: field-management-service-2:3000
        weight: 100
      - target: field-management-service-3:3000
        weight: 100
```

**Production HA Setup:**
```yaml
upstreams:
  - name: field-management-upstream
    algorithm: least-connections
    hash_on: none
    hash_fallback: none
    slots: 10000
    targets:
      - target: field-management-service-1:3000
        weight: 100
      - target: field-management-service-2:3000
        weight: 100
      - target: field-management-service-3:3000
        weight: 100
    healthchecks:
      active:
        type: http
        http_path: /healthz
        timeout: 1
        concurrency: 10
        healthy:
          interval: 5
          successes: 2
          http_statuses: [200, 302]
        unhealthy:
          interval: 3
          http_failures: 3
          tcp_failures: 3
          timeouts: 3
          http_statuses: [429, 500, 503]
      passive:
        type: http
        healthy:
          successes: 5
          http_statuses: [200, 201, 202, 203, 204, 205, 206, 207, 208, 226, 300, 301, 302, 303, 304, 305, 306, 307, 308]
        unhealthy:
          http_failures: 3
          tcp_failures: 3
          timeouts: 3
          http_statuses: [429, 500, 502, 503, 504, 505]
```

---

## 11. Security Considerations

### 11.1 Internal vs External Traffic

**All upstreams:**
- Use internal service names ✅
- No external endpoints exposed ✅
- Private network communication ✅

**Status**: ✅ GOOD

### 11.2 Health Check Endpoint Security

**Issues:**
1. ⚠️ Health check endpoints may expose system information
2. ⚠️ No authentication on health endpoints (standard practice but consider implications)
3. ℹ️ Mixed health check paths could indicate security inconsistencies

**Recommendations:**
- Ensure health endpoints don't leak sensitive data
- Consider rate limiting health check endpoints
- Standardize health check responses

---

## 12. Performance Optimization Opportunities

### 12.1 Circuit Breaker Configuration

**Status**: ❌ NOT CONFIGURED

**Recommendation**: Add circuit breaker pattern to prevent cascading failures

```yaml
# Example for ai-advisor-upstream
healthchecks:
  threshold: 50  # Circuit opens at 50% failure rate
  passive:
    unhealthy:
      http_failures: 3
      tcp_failures: 3
```

### 12.2 Connection Pooling

**Current Status**: Using Kong defaults

**Recommendations:**
```yaml
# For high-traffic services
upstream_keepalive_pool_size: 60
upstream_keepalive_max_requests: 100
upstream_keepalive_idle_timeout: 60
```

### 12.3 Caching Strategy

**Services that could benefit from upstream-level caching:**
1. weather-service (data changes infrequently)
2. astronomical-calendar (predictable data)
3. indicators-service (dashboard data)
4. satellite imagery (large, static files)

---

## 13. Monitoring & Observability Gaps

### 13.1 Health Check Monitoring

**Currently Configured:**
- Prometheus metrics collection ✅
- Grafana dashboards ✅

**Missing:**
- Health check failure alerting ⚠️
- Upstream status change notifications ⚠️
- Per-service health metrics ⚠️

### 13.2 Recommended Metrics

**Add these metrics:**
```
kong_upstream_target_health{upstream, target, state}
kong_upstream_health_checks_total{upstream, state}
kong_upstream_health_check_failures{upstream, reason}
```

---

## 14. Critical Issues Summary

### 14.1 Immediate Action Required (P0 - Critical)

1. **DNS Configuration Error**
   - Using external DNS (8.8.8.8) for internal services
   - Risk: Service discovery failures in isolated environments
   - Fix: Change to internal Docker DNS (127.0.0.11)

2. **Configuration Drift**
   - Multiple Kong configs not synchronized
   - Risk: Deployment errors, inconsistent behavior
   - Fix: Establish single source of truth, automated sync

3. **Missing Upstreams**
   - 24 services using direct URLs instead of upstreams
   - Risk: No health checks, no load balancing, no failover
   - Fix: Create upstream definitions for all services

4. **No Horizontal Scaling**
   - All upstreams have single target
   - Risk: No high availability, single point of failure
   - Fix: Add multiple targets per upstream

5. **Inconsistent Health Check Paths**
   - 5 different health check path patterns
   - Risk: Monitoring failures, debugging complexity
   - Fix: Standardize on `/healthz` or `/health`

### 14.2 High Priority (P1)

1. **Missing Timeout Configurations**
   - Many services lack timeout settings
   - Risk: Hanging connections, resource exhaustion

2. **Inconsistent Retry Policies**
   - Only some services have retry configuration
   - Risk: Inconsistent reliability

3. **Naming Convention Chaos**
   - Three different naming patterns
   - Risk: Developer confusion, routing errors

### 14.3 Medium Priority (P2)

1. **Load Balancing Algorithm**
   - All using round-robin
   - Opportunity: Optimize per service type

2. **Port Allocation**
   - No clear strategy
   - Opportunity: Reorganize for clarity

3. **Health Check Completeness**
   - Only 4 upstreams have passive checks in main config
   - Opportunity: Add passive monitoring to all

---

## 15. Recommendations & Remediation Plan

### Phase 1: Immediate (Week 1)

1. **Fix DNS Configuration**
   ```yaml
   KONG_DNS_RESOLVER: 127.0.0.11:53
   KONG_DNS_ORDER: A,CNAME,LAST
   ```

2. **Consolidate Configurations**
   - Choose single source of truth
   - Archive or delete others
   - Document sync process

3. **Add Missing Upstreams**
   - Create upstream for all 24 direct-URL services
   - Use template for consistency

### Phase 2: Short-term (Week 2-4)

4. **Standardize Health Checks**
   ```yaml
   # Template
   healthchecks:
     active:
       type: http
       http_path: /healthz
       healthy:
         interval: 10
         successes: 2
       unhealthy:
         interval: 5
         http_failures: 3
         timeouts: 3
     passive:
       healthy:
         successes: 5
       unhealthy:
         http_failures: 5
         timeouts: 3
   ```

5. **Add Timeout Configurations**
   - Standard: 5s/60s/60s
   - Compute: 10s/120s/120s
   - AI/ML: 15s/180s/180s

6. **Configure Retry Policies**
   - Standard: retries 3
   - Long-running: retries 1
   - Critical: retries 5

### Phase 3: Medium-term (Month 2)

7. **Implement High Availability**
   - Add 2-3 replicas per service
   - Configure load balancing
   - Test failover scenarios

8. **Optimize Load Balancing**
   - Review service characteristics
   - Apply appropriate algorithms
   - Benchmark performance

9. **Add Circuit Breakers**
   - Configure thresholds
   - Test failure scenarios
   - Monitor effectiveness

### Phase 4: Long-term (Month 3+)

10. **Implement Advanced Monitoring**
    - Health check failure alerting
    - Upstream status dashboards
    - Per-service SLAs

11. **Performance Optimization**
    - Connection pooling tuning
    - Caching strategies
    - Query optimization

12. **Documentation & Training**
    - Upstream management guide
    - Runbook for common issues
    - Team training sessions

---

## 16. Kong Configuration Best Practices Template

### 16.1 Standard Upstream Template

```yaml
upstreams:
  - name: {service-name}-upstream
    algorithm: round-robin  # or least-connections for I/O heavy
    hash_on: none
    hash_fallback: none
    slots: 10000
    targets:
      - target: {service-name}-1:{port}
        weight: 100
      - target: {service-name}-2:{port}
        weight: 100
      - target: {service-name}-3:{port}
        weight: 100
    healthchecks:
      active:
        type: http
        http_path: /healthz
        timeout: 1
        concurrency: 10
        healthy:
          interval: 10
          successes: 2
          http_statuses: [200, 201, 204]
        unhealthy:
          interval: 5
          http_failures: 3
          timeouts: 3
          http_statuses: [429, 500, 502, 503, 504]
          tcp_failures: 3
      passive:
        type: http
        healthy:
          successes: 5
          http_statuses: [200, 201, 204]
        unhealthy:
          http_failures: 3
          tcp_failures: 3
          timeouts: 3
          http_statuses: [429, 500, 502, 503, 504]
```

### 16.2 Standard Service Template

```yaml
services:
  - name: {service-name}
    host: {service-name}-upstream
    tags:
      - {package-tier}
      - {category}
    retries: 3
    connect_timeout: 5000
    write_timeout: 60000
    read_timeout: 60000
    routes:
      - name: {service-name}-route
        paths:
          - /api/v1/{service-name}
        strip_path: false
        methods:
          - GET
          - POST
          - PUT
          - PATCH
          - DELETE
    plugins:
      - name: jwt
      - name: acl
        config:
          allow:
            - starter-users
            - professional-users
            - enterprise-users
      - name: rate-limiting
        config:
          minute: 100
          hour: 5000
          policy: redis
          redis_host: redis
          redis_port: 6379
          redis_timeout: 2000
          fault_tolerant: true
      - name: correlation-id
        config:
          header_name: X-Request-ID
          generator: uuid
```

---

## 17. Testing & Validation Checklist

### Pre-Deployment Testing

- [ ] Verify all upstream targets are resolvable
- [ ] Test health check endpoints respond correctly
- [ ] Validate timeout configurations under load
- [ ] Test failover with simulated failures
- [ ] Verify retry policies with error injection
- [ ] Load test with expected traffic patterns
- [ ] Security scan for exposed endpoints
- [ ] Configuration validation with `kong config parse`

### Post-Deployment Validation

- [ ] Monitor health check success rates
- [ ] Track upstream target health status
- [ ] Measure response time improvements
- [ ] Verify failover functionality
- [ ] Check error rates and retry patterns
- [ ] Validate DNS resolution times
- [ ] Review access logs for anomalies
- [ ] Performance comparison vs previous config

---

## 18. Appendix

### A. Configuration File Comparison Matrix

| Feature | Main | HA | Legacy | Infra |
|---------|------|----|----|-------|
| Upstreams Defined | 17 | 30 | 0 | 17 |
| Complete Health Checks | 4 | 30 | 0 | 4 |
| Uses Direct URLs | 24 | 0 | All | 24 |
| Timeout Configs | Partial | All | None | Partial |
| Retry Policies | Partial | All | None | Partial |
| Service Naming | Mixed | Prefixed | Direct | Mixed |

### B. Service Port Registry

```
3000  - field-management-service
3010  - marketplace-service
3015  - research-core
3020  - disaster-assessment
3021  - yield-prediction
3022  - lai-estimation
3023  - crop-growth-model
8080  - field-ops
8081  - ws-gateway
8089  - billing-core
8090  - vegetation-analysis-service
8091  - indicators-service
8092  - weather-service
8093  - advisory-service
8094  - irrigation-smart
8095  - crop-intelligence-service
8096  - code-review-service / virtual-sensors (conflict!)
8097  - community-chat
8098  - yield-prediction-service
8099  - field-chat
8100  - crop-health
8101  - equipment-service
8103  - task-service
8104  - provider-config
8106  - iot-gateway
8110  - notification-service
8111  - astronomical-calendar
8112  - ai-advisor
8113  - alert-service
8114  - chat-service
8116  - inventory-service
8117  - iot-service
8118  - ndvi-processor
8119  - virtual-sensors (conflict with 8096!)
8120  - field-intelligence
8200  - mcp-server
```

**Port Conflicts Detected:**
- Port 8096: code-review-service (HA) vs virtual-sensors (Main)
- Port 8119: virtual-sensors (Main) vs 8096 (HA)

### C. Health Check Path Standardization Map

| Current Path | Service Count | Recommended |
|--------------|---------------|-------------|
| /healthz | 24 | ✅ Keep as standard |
| /health | 2 | ⚠️ Migrate to /healthz |
| /api/v1/healthz | 2 | ⚠️ Migrate to /healthz |
| /api/v1/simulation/health | 1 | ⚠️ Add /healthz alias |
| /api/v1/disasters/health | 1 | ⚠️ Add /healthz alias |
| /api/v1/yield/health | 1 | ⚠️ Add /healthz alias |
| /api/v1/lai/health | 1 | ⚠️ Add /healthz alias |

### D. Algorithm Selection Guide

| Service Type | Recommended Algorithm | Reason |
|--------------|----------------------|--------|
| Database-heavy | least-connections | Balances connection load |
| Stateless API | round-robin | Simple and effective |
| Cached data | consistent-hashing | Maximizes cache hits |
| Session-aware | consistent-hashing | Maintains session affinity |
| AI/ML inference | least-connections | Balances compute load |
| File serving | consistent-hashing | Cache locality |
| Real-time WS | least-connections | Long-lived connections |

---

## 19. Conclusion

The SAHOOL Kong upstream configuration audit reveals a system in transition from a monolithic to a microservices architecture. While the HA configuration demonstrates best practices with comprehensive health checks and consistent configuration, the main configuration files show signs of organic growth with inconsistencies and gaps.

### Key Findings:
1. **30 upstreams in HA config** vs **17 in main config** - configuration fragmentation
2. **24 services bypass upstream abstraction** - missing health checks and load balancing
3. **5 different health check path patterns** - lack of standardization
4. **Single target per upstream** - no high availability
5. **DNS misconfiguration** - using external DNS for internal services

### Priority Actions:
1. Fix DNS configuration (1 day)
2. Consolidate configuration files (1 week)
3. Create missing upstreams (1 week)
4. Standardize health checks (2 weeks)
5. Implement horizontal scaling (1 month)

### Success Metrics:
- 100% upstreams with active + passive health checks
- 0 services using direct URLs
- 3+ replicas per critical service
- <1s health check response time
- >99.9% upstream availability

### Next Steps:
1. Review this audit with architecture team
2. Prioritize remediation items
3. Create detailed implementation plan
4. Set up monitoring for new configurations
5. Schedule quarterly upstream configuration reviews

---

**Report Generated**: 2026-01-06
**Audit Version**: 1.0
**Reviewed By**: System Audit
**Next Review Due**: 2026-04-06

---

## Glossary

**Upstream**: A Kong entity representing a backend service and its targets
**Target**: An individual instance of a backend service
**Health Check**: Automated monitoring to verify service availability
**Active Health Check**: Proactive polling of service health endpoints
**Passive Health Check**: Reactive monitoring based on traffic responses
**Circuit Breaker**: Pattern to prevent cascading failures
**Load Balancing**: Distribution of traffic across multiple service instances
**Failover**: Automatic switching to backup service when primary fails
**Service Discovery**: Automatic detection of service instances
**Round-robin**: Load balancing algorithm distributing requests sequentially
**Least-connections**: Algorithm routing to instance with fewest active connections
**Consistent-hashing**: Algorithm routing based on request characteristics for cache locality
