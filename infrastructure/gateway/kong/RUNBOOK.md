# Kong API Gateway Runbook
# دليل تشغيل بوابة Kong API

**SAHOOL Platform - Agricultural Intelligence Platform**
**Version:** v16.1.0
**Last Updated:** 2026-02-11

---

## Table of Contents | جدول المحتويات

1. [Quick Reference](#quick-reference)
2. [Common Issues](#common-issues)
3. [Health Checks](#health-checks)
4. [Performance Tuning](#performance-tuning)
5. [Security Incidents](#security-incidents)
6. [Backup and Recovery](#backup-and-recovery)

---

## Quick Reference | المرجع السريع

### Service URLs

| Service | URL | Description |
|---------|-----|-------------|
| **Kong Proxy** | http://localhost:8000 | Main API Gateway entry point |
| **Kong Admin** | http://localhost:8001 | Admin API (localhost only) |
| **Kong Status** | http://localhost:8100/status | Health and metrics |
| **Prometheus** | http://localhost:9090 | Metrics and monitoring |
| **Grafana** | http://localhost:3002 | Dashboards (admin/sahool-admin-2026) |
| **Konga** | http://localhost:1337 | Admin UI (DB mode only) |

### Quick Commands

```bash
# Start Kong (DB-less mode - recommended)
cd infrastructure/gateway/kong
docker compose --profile dbless up -d

# Stop Kong
docker compose --profile dbless down

# Reload configuration (DB-less)
docker compose exec kong-dbless kong reload

# Check Kong health
curl http://localhost:8100/status

# View Kong logs
docker compose logs -f kong-dbless

# Check all services status
curl -s http://localhost:8001/status | jq

# View Prometheus metrics
curl http://localhost:8100/metrics
```

---

## Common Issues | المشاكل الشائعة

### Issue 1: Kong Container Fails to Start

**Symptoms:**
- Container exits immediately
- Error: "database not found" or "migrations needed"

**Solution:**
```bash
# For DB mode
docker compose --profile db up -d kong-database
docker compose run --rm kong-migrations
docker compose --profile db up -d kong

# For DB-less mode (check config syntax)
cd infrastructure/gateway/kong
python3 -c "import yaml; yaml.safe_load(open('kong.yml'))"
# If valid, restart
docker compose --profile dbless restart kong-dbless
```

### Issue 2: Service Not Reachable Through Kong

**Symptoms:**
- 502 Bad Gateway
- 503 Service Unavailable
- Connection refused

**Diagnostics:**
```bash
# 1. Check if service is running
docker ps | grep <service-name>

# 2. Check Kong can reach the service
docker exec kong-dbless ping <service-name>

# 3. Check DNS resolution
docker exec kong-dbless nslookup <service-name>

# 4. Check service health directly
curl http://<service-name>:<port>/healthz

# 5. Check Kong routes
curl http://localhost:8001/routes | jq '.data[] | select(.name | contains("<service>"))'
```

**Solution:**
1. Ensure service is in the same Docker network (`sahool-network`)
2. Verify service name matches `docker-compose.yml` service key (not `container_name`)
3. Check port number is the container internal port (not host-mapped port)
4. Reload Kong config if changes were made

### Issue 3: High Latency

**Symptoms:**
- Requests taking >1 second
- Prometheus shows high response times

**Diagnostics:**
```bash
# Check Kong metrics
curl http://localhost:8100/metrics | grep kong_latency

# Check upstream service health
curl http://localhost:8001/upstreams/<upstream-name>/health

# View detailed request timing
docker compose logs kong-dbless | grep -E "latency|upstream"
```

**Solutions:**
1. **Enable caching** for read-heavy endpoints (weather, NDVI, satellite data)
2. **Increase worker processes**:
   ```yaml
   # In docker-compose.yml
   KONG_NGINX_WORKER_PROCESSES: 4  # Fixed from 'auto' (see C12 fix, 2026-03-13)
   KONG_NGINX_WORKER_CONNECTIONS: 16384  # Increase from 8192
   ```
3. **Enable upstream keepalive** (already configured)
4. **Add load balancing** with upstreams

### Issue 4: Rate Limiting Not Working

**Symptoms:**
- Users exceed rate limits
- No rate limit headers in response

**Diagnostics:**
```bash
# Check if Redis is running
docker ps | grep kong-redis
docker exec kong-redis redis-cli ping

# Check rate limiting plugin
curl http://localhost:8001/plugins | jq '.data[] | select(.name == "rate-limiting")'

# Test rate limiting
for i in {1..100}; do curl -I http://localhost:8000/api/v1/weather; done
```

**Solution:**
```bash
# Ensure Redis is healthy
docker compose restart kong-redis

# Check plugin configuration
# For Redis-based (distributed):
# policy: redis
# redis_host: kong-redis
# redis_port: 6379

# For local (single node):
# policy: local
```

### Issue 5: CORS Errors in Browser

**Symptoms:**
- "Access-Control-Allow-Origin" errors
- Preflight OPTIONS requests failing

**Diagnostics:**
```bash
# Test CORS headers
curl -I -X OPTIONS http://localhost:8000/api/v1/fields \
  -H "Origin: https://app.sahool.com" \
  -H "Access-Control-Request-Method: POST"
```

**Solution:**
1. **Development**: Wildcard is enabled (`origins: ["*"]`)
2. **Production**: Update origins in `kong.yml`:
   ```yaml
   origins:
     - "https://app.sahool.com"
     - "https://admin.sahool.com"
   credentials: true
   ```
3. Use production template: `kong-cors-production.yml`

---

## Health Checks | فحوصات الصحة

### Manual Health Check

```bash
#!/bin/bash
# Check all Kong components

echo "=== Kong Gateway Health ==="
curl -s http://localhost:8100/status | jq

echo "\n=== Redis Health ==="
docker exec kong-redis redis-cli ping

echo "\n=== Database Health (DB mode only) ==="
docker exec kong-postgres pg_isready -U kong

echo "\n=== Prometheus Health ==="
curl -s http://localhost:9090/-/healthy

echo "\n=== Grafana Health ==="
curl -s http://localhost:3002/api/health | jq
```

### Automated Monitoring

Prometheus alerts configured in `alerts/kong-alerts.yml`:

- **HighErrorRate**: >5% 5xx responses
- **HighLatency**: P95 >1s
- **ServiceDown**: Service unavailable for 1min
- **HighMemoryUsage**: >80% memory

View alerts: http://localhost:9090/alerts

---

## Performance Tuning | تحسين الأداء

### Current Settings (Optimized)

```yaml
# Worker Processes
KONG_NGINX_WORKER_PROCESSES: 4  # Fixed from 'auto' to avoid startup delays on high-core hosts
KONG_NGINX_WORKER_CONNECTIONS: 8192

# Buffering
KONG_NGINX_PROXY_BUFFER_SIZE: 128k
KONG_NGINX_PROXY_BUFFERS: "4 256k"
KONG_NGINX_PROXY_BUSY_BUFFERS_SIZE: 256k

# Keepalive
KONG_UPSTREAM_KEEPALIVE_POOL_SIZE: 120
KONG_UPSTREAM_KEEPALIVE_MAX_REQUESTS: 1000
KONG_UPSTREAM_KEEPALIVE_IDLE_TIMEOUT: 60

# Memory
KONG_MEM_CACHE_SIZE: 256m
```

### Performance Benchmarking

```bash
# Install Apache Bench
sudo apt-get install apache2-utils

# Test throughput (1000 requests, 10 concurrent)
ab -n 1000 -c 10 http://localhost:8000/api/v1/health

# With authentication
ab -n 1000 -c 10 -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/fields
```

**Expected Performance:**
- **Throughput**: >10,000 req/s per node
- **Latency P50**: <10ms
- **Latency P95**: <50ms
- **Latency P99**: <100ms

### Optimization Checklist

- [ ] Enable proxy-cache for read-heavy endpoints
- [ ] Use Redis for distributed rate limiting
- [ ] Configure upstreams with health checks
- [ ] Enable response compression (gzip)
- [ ] Use connection pooling (already enabled)
- [ ] Monitor and adjust worker processes
- [ ] Add multiple Kong nodes for HA

---

## Security Incidents | حوادث الأمان

### DDoS Attack

**Detection:**
```bash
# Check request rate
docker compose logs kong-dbless | grep -c "GET\|POST" | tail -100

# Check rate limiting triggers
curl http://localhost:8100/metrics | grep kong_rate_limiting
```

**Mitigation:**
1. Reduce rate limits temporarily
2. Enable IP blocking:
   ```bash
   # Add to kong.yml under global plugins
   - name: ip-restriction
     config:
       deny:
         - "1.2.3.4"  # Attacker IP
   ```
3. Use CDN/WAF (Cloudflare) upstream

### Suspicious Traffic

**Indicators:**
- SQL injection attempts in logs
- Scanner user-agents (sqlmap, Nikto)
- Unusual request patterns

**Response:**
```bash
# Check bot-detection plugin
curl http://localhost:8001/plugins | jq '.data[] | select(.name == "bot-detection")'

# View blocked requests
docker compose logs kong-dbless | grep "403\|bot-detection"

# Add IP to blocklist
# Update kong.yml > ip-restriction plugin > deny list
```

### Data Breach Attempt

**Immediate Actions:**
1. Enable audit logging:
   ```yaml
   - name: file-log
     config:
       path: /var/log/kong/audit.log
   ```
2. Review access logs for suspicious patterns
3. Rotate JWT secrets immediately
4. Notify security team

---

## Backup and Recovery | النسخ الاحتياطي والاستعادة

### Backup Configuration (DB-less)

```bash
# All configs are in Git - just commit changes
cd infrastructure/gateway/kong
git add kong.yml kong-*.yml
git commit -m "Kong config backup $(date +%Y-%m-%d)"
git push
```

### Backup Database (DB mode)

```bash
# Backup Kong database
docker exec kong-postgres pg_dump -U kong kong > kong_backup_$(date +%Y%m%d).sql

# Backup to S3
aws s3 cp kong_backup_$(date +%Y%m%d).sql s3://sahool-backups/kong/
```

### Restore from Backup

```bash
# DB-less: Just reload config
docker compose exec kong-dbless kong reload

# DB mode: Restore database
docker exec -i kong-postgres psql -U kong < kong_backup_20260211.sql
docker compose restart kong
```

### Disaster Recovery

1. **Kong node failure**:
   ```bash
   # Start replacement node (HA cluster)
   docker compose --profile dbless up -d --scale kong-dbless=3
   ```

2. **Configuration corruption**:
   ```bash
   # Revert to last known good config
   git checkout HEAD~1 infrastructure/gateway/kong/kong.yml
   docker compose exec kong-dbless kong reload
   ```

3. **Complete cluster failure**:
   ```bash
   # Restore from infrastructure as code
   cd infrastructure/gateway/kong
   docker compose --profile dbless up -d
   # Config is declarative - auto-applies on startup
   ```

---

## Monitoring Queries | استعلامات المراقبة

### Prometheus Queries

```promql
# Request rate per service
sum(rate(kong_http_requests_total[5m])) by (service)

# Error rate
sum(rate(kong_http_requests_total{code=~"5.."}[5m])) / sum(rate(kong_http_requests_total[5m]))

# P95 latency
histogram_quantile(0.95, sum(rate(kong_latency_bucket[5m])) by (le))

# Active connections
kong_nginx_connections_active

# Memory usage
kong_memory_lua_shared_dict_bytes / kong_memory_lua_shared_dict_total_bytes
```

### Grafana Dashboards

Pre-configured dashboard: `grafana/dashboards/kong-dashboard.json`

**Panels:**
- Request rate (QPS)
- Error rate (%)
- Latency (P50, P95, P99)
- Bandwidth (in/out)
- Active connections
- Cache hit rate
- Rate limiting events

---

## Maintenance Windows | نوافذ الصيانة

### Zero-Downtime Reload

```bash
# DB-less mode (recommended)
docker compose exec kong-dbless kong reload
# ~100ms reload time, no downtime

# DB mode (requires migrations)
docker compose run --rm kong-migrations up
docker compose exec kong kong reload
```

### Upgrade Kong

```bash
# 1. Backup current config
git commit -am "Backup before Kong upgrade"

# 2. Update docker-compose.yml
# Change: kong:3.5-alpine -> kong:3.6-alpine

# 3. Pull new image
docker compose pull kong-dbless

# 4. Restart (brief downtime ~5s)
docker compose up -d kong-dbless

# 5. Verify
curl http://localhost:8001/status | jq '.version'
```

---

## Contact Information | معلومات الاتصال

**On-Call Engineer:** ops@sahool.com
**Slack Channel:** #kong-alerts
**PagerDuty:** kong-gateway-prod

**Escalation:**
1. Level 1: DevOps Team
2. Level 2: Platform Engineering
3. Level 3: CTO

---

## Additional Resources | موارد إضافية

- [Kong Documentation](https://docs.konghq.com/)
- [Kong Admin API Reference](https://docs.konghq.com/gateway/latest/admin-api/)
- [SAHOOL ADR-004: Kong API Gateway](../../docs/adr/ADR-004-kong-api-gateway.md)
- [Kong Security Audit](../../tests/middleware/KONG_SECURITY_AUDIT.md)
- [Kong Performance Audit](../../tests/middleware/KONG_PERFORMANCE_AUDIT.md)

---

**Document Version:** 1.0
**Maintained By:** Platform Engineering Team
**Review Cycle:** Quarterly
