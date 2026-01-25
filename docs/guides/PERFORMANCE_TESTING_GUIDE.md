# Performance Testing Guide

## دليل اختبار الأداء

**Version**: 1.0  
**Last Updated**: 2026-01-02  
**Related**: tests/load/README.md, POST_MERGE_VERIFICATION.md

---

## 📋 Overview | نظرة عامة

This guide provides comprehensive instructions for performance testing the SAHOOL platform using the k6 load testing framework added in PR #315.

يوفر هذا الدليل تعليمات شاملة لاختبار أداء منصة سهول باستخدام إطار اختبار الأحمال k6.

---

## 🎯 Testing Objectives | أهداف الاختبار

### Primary Goals

1. **Baseline Performance**: Establish performance benchmarks for all services
2. **Capacity Planning**: Determine system limits under various load conditions
3. **Regression Detection**: Identify performance degradation in new releases
4. **Bottleneck Identification**: Find and document performance bottlenecks
5. **Resource Optimization**: Guide infrastructure scaling decisions

### Key Performance Indicators (KPIs)

- **Response Time**: p95, p99 latency for API endpoints
- **Throughput**: Requests per second (RPS)
- **Error Rate**: Percentage of failed requests
- **Resource Utilization**: CPU, Memory, Network, Disk I/O
- **Concurrent Users**: Maximum supported simultaneous users

---

## 🏗️ Test Infrastructure | البنية التحتية للاختبار

### Components

```
tests/load/
├── scenarios/               # k6 test scenarios
│   ├── smoke.js            # Minimal load validation
│   ├── load.js             # Normal load testing
│   ├── stress.js           # Beyond capacity testing
│   ├── spike.js            # Sudden load increase
│   └── soak.js             # Extended duration testing
├── lib/
│   ├── config.js           # Configuration management
│   └── helpers.js          # Utility functions
├── simulation/             # Multi-client simulation
│   ├── scripts/
│   │   ├── web-dashboard-simulation.js
│   │   ├── mobile-app-simulation.js
│   │   └── agent-simulation.js
│   └── docker-compose-sim.yml
├── grafana/                # Visualization dashboards
├── docker-compose.load.yml # Load testing infrastructure
└── run-tests.sh            # Test execution script
```

### Prerequisites

**Software Requirements:**

- Docker & Docker Compose (v2+)
- k6 (for local runs)
- 8GB+ RAM recommended
- 4+ CPU cores recommended

**Infrastructure Requirements:**

- SAHOOL platform running (all services)
- PostgreSQL database
- Redis cache
- NATS message queue
- Monitoring stack (optional but recommended)

---

## 🚀 Quick Start | البدء السريع

### 1. Start SAHOOL Platform

```bash
# Using docker-one-by-one script (recommended for resource-constrained systems)
./docker-one-by-one.sh

# OR using standard docker compose
docker compose up -d

# Verify all services are running
docker compose ps

# Check health endpoints
curl http://localhost:8080/healthz
```

### 2. Start Load Testing Infrastructure

```bash
cd tests/load

# Start InfluxDB and Grafana
docker compose -f docker-compose.load.yml up -d

# Access Grafana at http://localhost:3000
# Default credentials: admin/admin
```

### 3. Run Smoke Test

```bash
# Quick validation (minimal load)
./run-tests.sh smoke

# Expected output:
# - Test duration: ~30 seconds
# - Virtual users: 1-5
# - Success rate: 100%
```

### 4. View Results

```bash
# Grafana dashboards
open http://localhost:3000

# InfluxDB metrics
open http://localhost:8086

# Check test results directory
ls -la results/
```

---

## 📊 Test Scenarios | سيناريوهات الاختبار

### 1. Smoke Test (اختبار الدخان)

**Purpose**: Verify system works with minimal load

**Configuration:**

- Duration: 30 seconds
- Virtual Users: 1-5
- Target RPS: 10-20

**Command:**

```bash
./run-tests.sh smoke
```

**Success Criteria:**

- ✅ 100% success rate
- ✅ p95 latency < 500ms
- ✅ No errors

---

### 2. Load Test (اختبار الحمل)

**Purpose**: Test system under normal expected load

**Configuration:**

- Duration: 5-10 minutes
- Virtual Users: 50-100
- Target RPS: 100-500

**Command:**

```bash
./run-tests.sh load
```

**Success Criteria:**

- ✅ 99.9% success rate
- ✅ p95 latency < 1000ms
- ✅ Error rate < 0.1%
- ✅ CPU < 70%
- ✅ Memory < 80%

---

### 3. Stress Test (اختبار الإجهاد)

**Purpose**: Find system breaking point

**Configuration:**

- Duration: 10-20 minutes
- Virtual Users: 100-500+ (gradually increasing)
- Target RPS: 500-2000+

**Command:**

```bash
./run-tests.sh stress
```

**Success Criteria:**

- ✅ System gracefully degrades (no crashes)
- ✅ Error messages are clear
- ✅ Recovery after load reduction
- ⚠️ Identify max capacity

---

### 4. Spike Test (اختبار الارتفاع المفاجئ)

**Purpose**: Test system behavior with sudden traffic increase

**Configuration:**

- Duration: 5-10 minutes
- Virtual Users: 1 → 500 (sudden jump)
- Target RPS: 10 → 1000

**Command:**

```bash
./run-tests.sh spike
```

**Success Criteria:**

- ✅ System handles spike without crashes
- ✅ Auto-scaling triggers (if configured)
- ✅ Response times recover after spike

---

### 5. Soak Test (اختبار النقع)

**Purpose**: Verify system stability over extended period

**Configuration:**

- Duration: 2-24 hours
- Virtual Users: 50-100 (constant)
- Target RPS: 100-200 (steady)

**Command:**

```bash
./run-tests.sh soak
```

**Success Criteria:**

- ✅ No memory leaks
- ✅ No connection pool exhaustion
- ✅ Consistent performance
- ✅ No resource degradation

---

## 🎯 Performance Targets | أهداف الأداء

### API Response Times

| Endpoint Type    | p50    | p95     | p99     |
| ---------------- | ------ | ------- | ------- |
| Health Check     | <50ms  | <100ms  | <200ms  |
| Read Operations  | <100ms | <500ms  | <1000ms |
| Write Operations | <200ms | <1000ms | <2000ms |
| Complex Queries  | <500ms | <2000ms | <5000ms |
| File Uploads     | <1s    | <5s     | <10s    |

### Throughput

| Service      | Target RPS | Max RPS |
| ------------ | ---------- | ------- |
| Field Ops    | 200        | 1000    |
| Billing      | 100        | 500     |
| Satellite    | 50         | 200     |
| Weather      | 100        | 500     |
| Notification | 500        | 2000    |

### Resource Utilization

| Resource | Normal | Warning | Critical |
| -------- | ------ | ------- | -------- |
| CPU      | <50%   | 50-70%  | >70%     |
| Memory   | <60%   | 60-80%  | >80%     |
| Disk I/O | <50%   | 50-75%  | >75%     |
| Network  | <40%   | 40-60%  | >60%     |

---

## 📈 Monitoring & Metrics | المراقبة والمقاييس

### Real-time Dashboards

**Grafana Dashboards:**

1. **k6 Load Testing Dashboard**
   - Request rate
   - Response times (p50, p95, p99)
   - Error rate
   - Active virtual users

2. **System Resources Dashboard**
   - CPU usage per service
   - Memory consumption
   - Network traffic
   - Disk I/O

3. **Application Metrics Dashboard**
   - API endpoint latency
   - Database query performance
   - Cache hit rate
   - Queue depth

### InfluxDB Queries

```sql
-- Average response time by endpoint (with time bucketing)
SELECT mean("value") FROM "http_req_duration"
WHERE time > now() - 1h
GROUP BY time(1m), "url"

-- Error rate over time
SELECT count("value") FROM "http_req_failed"
WHERE "value" = 1 AND time > now() - 1h
GROUP BY time(1m)

-- Request rate per minute
SELECT count("value") FROM "http_reqs"
WHERE time > now() - 1h
GROUP BY time(1m)
```

---

## 🔍 Analysis & Reporting | التحليل والإبلاغ

### Post-Test Analysis

```bash
# Generate HTML report
k6 run --out json=results.json scenarios/load.js
k6 json-to-html results.json > report.html

# View results
open report.html
```

### Key Metrics to Report

1. **Performance Summary**
   - Total requests
   - Success rate
   - Average/p95/p99 response times
   - Requests per second

2. **Resource Utilization**
   - Peak CPU usage
   - Peak memory usage
   - Network bandwidth
   - Database connections

3. **Errors & Failures**
   - Error types and counts
   - Failed endpoints
   - Root cause analysis

4. **Recommendations**
   - Scaling recommendations
   - Optimization opportunities
   - Configuration changes

---

## 🐛 Troubleshooting | استكشاف الأخطاء

### Common Issues

#### High Response Times

```bash
# Check database slow queries
docker compose logs postgres | grep "duration:"

# Check Redis performance
redis-cli --latency

# Review service logs
docker compose logs [service-name]
```

#### Memory Leaks

```bash
# Monitor memory over time
docker stats --no-stream

# Check for goroutine leaks (Go services)
curl http://localhost:6060/debug/pprof/heap

# Check for event loop blocks (Node.js services)
curl http://localhost:9229/json
```

#### Connection Pool Exhaustion

```bash
# Check database connections
SELECT count(*) FROM pg_stat_activity;

# Check Redis connections
redis-cli CLIENT LIST | wc -l
```

---

## 📝 Best Practices | أفضل الممارسات

### Test Execution

1. **Isolate Environment**: Run tests in dedicated environment
2. **Consistent State**: Reset database between test runs
3. **Realistic Data**: Use production-like data volumes
4. **Gradual Ramp**: Increase load gradually
5. **Monitor Resources**: Watch CPU, memory, network during tests

### Test Development

1. **Parameterize**: Use environment variables for configuration
2. **Modular**: Break tests into reusable functions
3. **Assertions**: Add meaningful checks and thresholds
4. **Documentation**: Document test scenarios and expectations
5. **Version Control**: Track test changes in git

### Continuous Testing

1. **Automated Runs**: Schedule regular performance tests
2. **Baseline Comparison**: Compare against previous runs
3. **Alert on Regression**: Notify on performance degradation
4. **Track Trends**: Monitor performance over time
5. **Document Changes**: Record infrastructure/code changes

---

## 🔗 References | المراجع

- [k6 Documentation](https://k6.io/docs/)
- [Load Testing Guide](tests/load/README.md)
- [Quick Start](tests/load/QUICKSTART.md)
- [Docker Guide](docs/DOCKER.md)
- [Post-Merge Verification](POST_MERGE_VERIFICATION.md)

---

## 📅 Testing Schedule | جدول الاختبار

### Recommended Frequency

| Test Type | Frequency    | Duration   |
| --------- | ------------ | ---------- |
| Smoke     | Every commit | 1 min      |
| Load      | Daily        | 10 min     |
| Stress    | Weekly       | 30 min     |
| Spike     | Weekly       | 15 min     |
| Soak      | Monthly      | 4-24 hours |

---

**Note**: Always run tests in a non-production environment first!
