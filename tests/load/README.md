# SAHOOL Platform - Load Testing Suite

Comprehensive load testing suite for the SAHOOL agricultural platform using k6.

## Overview

This test suite includes multiple load testing scenarios to ensure the SAHOOL platform can handle production traffic and scale effectively.

### Test Scenarios

| Scenario | Duration | VUs | Purpose |
|----------|----------|-----|---------|
| **Smoke** | 1 minute | 1 | Verify basic functionality |
| **Load** | 10 minutes | 50 | Test normal production load |
| **Stress** | 15 minutes | 200 (peak) | Find breaking point |
| **Spike** | 8 minutes | 10→200→10 | Test sudden traffic bursts |
| **Soak** | 2 hours | 20 | Detect memory leaks |

## Prerequisites

### Option 1: Local k6 Installation

**macOS:**
```bash
brew install k6
```

**Linux (Debian/Ubuntu):**
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg \
  --keyserver hkp://keyserver.ubuntu.com:80 \
  --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | \
  sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

**Windows:**
```powershell
choco install k6
```

### Option 2: Docker

Use the provided `docker-compose.load.yml` (recommended for CI/CD).

## Quick Start

### 1. Using Shell Script (Recommended)

```bash
cd tests/load

# Run smoke test (quick validation)
./run-tests.sh smoke

# Run load test (production simulation)
./run-tests.sh load

# Run stress test (find limits)
./run-tests.sh stress

# Run spike test (sudden bursts)
./run-tests.sh spike

# Run soak test (2 hours)
./run-tests.sh soak

# Run all tests
./run-tests.sh all
```

### 2. Using k6 Directly

```bash
cd tests/load

# Smoke test
k6 run scenarios/smoke.js

# Load test
k6 run scenarios/load.js

# With custom configuration
k6 run \
  -e BASE_URL=https://api.sahool.io \
  -e ENVIRONMENT=production \
  scenarios/load.js
```

### 3. Using Docker Compose

```bash
cd tests/load

# Start infrastructure (InfluxDB + Grafana)
docker-compose -f docker-compose.load.yml up -d influxdb grafana

# Run smoke test
docker-compose -f docker-compose.load.yml run --rm k6 run scenarios/smoke.js

# Run load test
docker-compose -f docker-compose.load.yml run --rm k6 run scenarios/load.js

# View results in Grafana: http://localhost:3030
# Default credentials: admin/admin

# Cleanup
docker-compose -f docker-compose.load.yml down
```

## Configuration

### Environment Variables

Configure test environment using environment variables:

```bash
# Service URLs
export BASE_URL=http://localhost:8000
export FIELD_SERVICE_URL=http://localhost:8080
export WEATHER_URL=http://localhost:8092
export BILLING_URL=http://localhost:8089
export SATELLITE_URL=http://localhost:8090
export EQUIPMENT_URL=http://localhost:8101
export TASK_URL=http://localhost:8103
export CROP_HEALTH_URL=http://localhost:8095

# Test configuration
export ENVIRONMENT=staging
export TENANT_ID=tenant_loadtest
export TEST_USER_EMAIL=loadtest@sahool.io
export TEST_USER_PASSWORD=LoadTest123!

# Results
export RESULTS_DIR=./results
```

### Package Tier Testing

Tests include scenarios for all package tiers:

- **Free**: 3 fields, 10 satellite analyses/month
- **Starter**: 10 fields, 50 satellite analyses/month, 20 AI diagnoses/month
- **Professional**: 50 fields, 200 satellite analyses/month, 100 AI diagnoses/month
- **Enterprise**: Unlimited fields, analyses, and diagnoses

## Test Scenarios Details

### 1. Smoke Test (`scenarios/smoke.js`)

**Purpose**: Quick validation that all critical paths work.

**What it tests**:
- Health checks
- Authentication
- Field CRUD operations
- Weather forecast
- Billing plans

**When to run**: After every deployment, before other tests.

```bash
./run-tests.sh smoke
```

**Expected duration**: ~1 minute

### 2. Load Test (`scenarios/load.js`)

**Purpose**: Simulate expected production load.

**What it tests**:
- 50 concurrent users
- Field management (60% of users)
- Weather data (40% of users)
- Satellite imagery (20% of users)
- Operations management (35% of users)
- Task management (30% of users)
- Equipment management (15% of users)
- Irrigation calculations (25% of users)
- Billing operations (10% of users)

**Performance targets**:
- P95 response time < 500ms
- Error rate < 1%
- Throughput > 50 RPS

```bash
./run-tests.sh load
```

**Expected duration**: ~10 minutes

### 3. Stress Test (`scenarios/stress.js`)

**Purpose**: Find the system's breaking point.

**Load profile**:
1. Warm up: 0 → 20 VUs (2 min)
2. Ramp up: 20 → 100 VUs (3 min)
3. Increase: 100 → 150 VUs (3 min)
4. Peak stress: 150 → 200 VUs (2 min)
5. Hold: 200 VUs (2 min)
6. Recovery: 200 → 50 VUs (2 min)
7. Cool down: 50 → 0 VUs (1 min)

**What to monitor**:
- Maximum sustainable load
- Error rates under stress
- Recovery time
- Resource exhaustion points

```bash
./run-tests.sh stress
```

**Expected duration**: ~15 minutes

### 4. Spike Test (`scenarios/spike.js`)

**Purpose**: Test auto-scaling and sudden traffic handling.

**Load profile**:
1. Normal: 10 VUs (30s)
2. **SPIKE 1**: 10 → 200 VUs in 30s
3. Hold: 200 VUs (2 min)
4. Drop: 200 → 10 VUs (30s)
5. Recovery: 10 VUs (2 min)
6. **SPIKE 2**: 10 → 150 VUs in 30s
7. Hold: 150 VUs (1 min)
8. Cool down: 150 → 0 VUs (30s)

**What to monitor**:
- Response time during spike vs normal
- Error rate during spike
- Recovery time after spike
- Rate limiting effectiveness
- Circuit breaker activations

```bash
./run-tests.sh spike
```

**Expected duration**: ~8 minutes

### 5. Soak Test (`scenarios/soak.js`)

**Purpose**: Detect memory leaks and performance degradation over time.

**Load profile**:
- Ramp up: 0 → 20 VUs (5 min)
- Soak: 20 VUs constant (1h 50m)
- Ramp down: 20 → 0 VUs (5 min)

**What it tests**:
- Memory leak detection
- Database connection pool stability
- Cache effectiveness over time
- Long-running operation handling
- Resource cleanup

**What to monitor**:
- Response time trends (should remain stable)
- Memory usage patterns (should not continuously grow)
- Error rate stability
- Database connection leaks
- Cache hit rates

```bash
./run-tests.sh soak
```

**Expected duration**: 2 hours

## Understanding Results

### k6 Output Metrics

```
checks.........................: 99.50% ✓ 1990     ✗ 10
data_received..................: 15 MB  25 kB/s
data_sent......................: 1.2 MB 2.0 kB/s
http_req_blocked...............: avg=1.25ms  min=1µs   med=5µs    max=567ms p(90)=9µs    p(95)=12µs
http_req_connecting............: avg=432µs   min=0s    med=0s     max=220ms p(90)=0s     p(95)=0s
http_req_duration..............: avg=234ms   min=89ms  med=198ms  max=2.1s  p(90)=387ms  p(95)=456ms
http_req_failed................: 0.50%  ✓ 10       ✗ 1990
http_req_receiving.............: avg=128µs   min=22µs  med=98µs   max=8ms   p(90)=189µs  p(95)=234µs
http_req_sending...............: avg=45µs    min=7µs   med=35µs   max=3ms   p(90)=78µs   p(95)=98µs
http_req_tls_handshaking.......: avg=0s      min=0s    med=0s     max=0s    p(90)=0s     p(95)=0s
http_req_waiting...............: avg=234ms   min=89ms  med=198ms  max=2.1s  p(90)=387ms  p(95)=455ms
http_reqs......................: 2000   3.33/s
iteration_duration.............: avg=15s     min=12s   med=14.8s  max=18s   p(90)=16s    p(95)=16.5s
iterations.....................: 100    0.166/s
vus............................: 50     min=0      max=50
vus_max........................: 50     min=50     max=50
```

### Key Metrics Explained

- **checks**: Percentage of successful assertions (should be > 99%)
- **http_req_duration**: Response time (p95 < 500ms is good)
- **http_req_failed**: Error rate (should be < 1%)
- **http_reqs**: Requests per second (throughput)
- **vus**: Number of virtual users

### Thresholds

Tests will **PASS** if:

| Metric | Smoke | Load | Stress | Spike | Soak |
|--------|-------|------|--------|-------|------|
| P95 Duration | <800ms | <500ms | <2000ms | <1500ms | <600ms |
| P99 Duration | <1500ms | <1000ms | <5000ms | <3000ms | <1200ms |
| Error Rate | <1% | <1% | <5% | <5% | <1% |
| Checks | >99% | >99% | >95% | >95% | >99% |

Tests will **FAIL** if thresholds are not met.

## Grafana Dashboards

When using Docker Compose with InfluxDB:

1. Open Grafana: http://localhost:3030
2. Login: admin/admin
3. View k6 metrics in real-time
4. Pre-configured dashboards show:
   - Response times (P50, P90, P95, P99)
   - Request rate
   - Error rate
   - Virtual users
   - Custom metrics

## Results Storage

Results are saved in the `results/` directory:

```
results/
├── smoke_20251226_143022.json
├── smoke_20251226_143022_summary.json
├── load_20251226_144530.json
├── load_20251226_144530_summary.json
└── ...
```

### Uploading to InfluxDB

To store results in InfluxDB for historical analysis:

```bash
export INFLUXDB_URL=http://localhost:8086
export INFLUXDB_TOKEN=${INFLUXDB_ADMIN_TOKEN}
export INFLUXDB_ORG=sahool
export INFLUXDB_BUCKET=k6

k6 run --out influxdb=$INFLUXDB_URL scenarios/load.js
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Load Tests

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  smoke-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run smoke test
        run: |
          docker-compose -f docker-compose.yml up -d
          cd tests/load
          ./run-tests.sh smoke
      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: smoke-test-results
          path: tests/load/results/

  load-test:
    runs-on: ubuntu-latest
    needs: smoke-test
    steps:
      - uses: actions/checkout@v3
      - name: Run load test
        run: |
          docker-compose -f docker-compose.yml up -d
          cd tests/load
          ./run-tests.sh load
```

### GitLab CI Example

```yaml
load-tests:
  stage: test
  image: grafana/k6:latest
  script:
    - cd tests/load
    - k6 run scenarios/load.js
  artifacts:
    paths:
      - tests/load/results/
    expire_in: 7 days
  only:
    - schedules
```

## Troubleshooting

### Common Issues

**1. k6 not found**
```bash
# Install k6
brew install k6  # macOS
# OR use Docker
docker-compose -f docker-compose.load.yml run k6 run scenarios/smoke.js
```

**2. Services not reachable**
```bash
# Check service health
./run-tests.sh --check-only

# Update URLs
export FIELD_SERVICE_URL=http://your-service-url:8080
```

**3. Authentication failures**
```bash
# Check test user credentials
export TEST_USER_EMAIL=your-test-user@example.com
export TEST_USER_PASSWORD=your-password
```

**4. Tests failing due to quota limits**
```bash
# Use different tenant for load testing
export TENANT_ID=tenant_loadtest

# Or increase quota limits for test tenant
```

**5. High error rates**
- Check service logs
- Verify database connections
- Check resource limits (CPU, memory)
- Review rate limiting configuration

## Best Practices

### Before Running Tests

1. **Smoke test first**: Always run smoke test before longer tests
2. **Check health**: Use `--check-only` to verify services are ready
3. **Use test data**: Don't run load tests against production data
4. **Coordinate with team**: Schedule long tests to avoid conflicts
5. **Monitor resources**: Keep an eye on CPU, memory, disk I/O

### During Tests

1. **Monitor logs**: Watch service logs for errors
2. **Track metrics**: Use Grafana to monitor in real-time
3. **Don't interrupt**: Let tests complete naturally
4. **Document issues**: Note any anomalies or errors

### After Tests

1. **Review results**: Check all metrics and thresholds
2. **Compare baselines**: Track performance trends over time
3. **Clean up**: Remove test data if needed
4. **Share findings**: Document and share results with team
5. **Action items**: Create tickets for any issues found

## Performance Targets (SLA)

### Response Times

| Endpoint Type | P95 | P99 |
|--------------|-----|-----|
| Health checks | <100ms | <200ms |
| Read operations | <300ms | <500ms |
| Write operations | <500ms | <1000ms |
| Satellite analysis | <2000ms | <5000ms |
| Weather forecast | <500ms | <1000ms |

### Availability

- **Uptime**: 99.9% (43 minutes downtime/month)
- **Error rate**: <0.1% under normal load
- **Success rate**: >99.9%

### Scalability

- **Concurrent users**: Support 1000+ concurrent users
- **Request rate**: Handle 100+ RPS per service
- **Database**: Support 10000+ records per table
- **Response degradation**: <20% slowdown at 2x expected load

## Resources

- [k6 Documentation](https://k6.io/docs/)
- [k6 Best Practices](https://k6.io/docs/testing-guides/test-types/)
- [InfluxDB Documentation](https://docs.influxdata.com/)
- [Grafana Dashboards](https://grafana.com/grafana/dashboards/)

## Support

For issues or questions:
- Check logs in `results/` directory
- Review service logs
- Contact: devops@sahool.io

---

**SAHOOL Platform Load Testing Suite v1.0**
Last updated: December 2025
