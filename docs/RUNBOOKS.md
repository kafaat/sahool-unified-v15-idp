# Incident Runbooks

## Overview

This document provides step-by-step procedures for common incidents in the SAHOOL platform.

## Table of Contents

1. [Service Down](#service-down)
2. [High Error Rate](#high-error-rate)
3. [High Latency](#high-latency)
4. [Database Connection Issues](#database-connection-issues)
5. [Cache Failures](#cache-failures)
6. [Authentication Failures](#authentication-failures)
7. [Disk Space Issues](#disk-space-issues)
8. [Memory Exhaustion](#memory-exhaustion)

---

## Service Down

### Symptoms

- Health check endpoint returns 503 or times out
- Kubernetes shows pod as not ready
- Alerts: `ServiceDown`

### Investigation Steps

1. **Check pod status**

   ```bash
   kubectl get pods -l app=<service-name>
   kubectl describe pod <pod-name>
   ```

2. **Check recent logs**

   ```bash
   kubectl logs <pod-name> --tail=100
   kubectl logs <pod-name> --previous  # If pod restarted
   ```

3. **Check health endpoint**

   ```bash
   curl http://<service-url>/health
   ```

4. **Check resource usage**
   ```bash
   kubectl top pod <pod-name>
   ```

### Common Causes & Solutions

#### Database Connection Failure

**Symptoms**: Readiness check fails with database error

**Solution**:

```bash
# Check database connectivity
kubectl exec -it <pod-name> -- psql -h postgres -U sahool -c "SELECT 1"

# Check database pod status
kubectl get pods -l app=postgres

# Restart service pod
kubectl delete pod <pod-name>
```

#### Configuration Error

**Symptoms**: Pod crashes immediately on startup

**Solution**:

```bash
# Check environment variables
kubectl describe pod <pod-name> | grep -A 20 Environment

# Verify secrets exist
kubectl get secrets

# Check ConfigMaps
kubectl get configmaps
```

#### Out of Memory

**Symptoms**: Pod killed with OOMKilled status

**Solution**:

```bash
# Increase memory limits
kubectl set resources deployment/<service-name> --limits=memory=1Gi

# Or edit deployment
kubectl edit deployment <service-name>
# Update: spec.template.spec.containers[0].resources.limits.memory
```

### Escalation

If issue persists after 30 minutes:

1. Page on-call engineer
2. Open Slack incident channel: `#incident-<timestamp>`
3. Document all investigation steps

---

## High Error Rate

### Symptoms

- Error rate > 5% of requests
- Metrics show spike in `service_errors_total`
- Alerts: `HighErrorRate`

### Investigation Steps

1. **Check error types**

   ```promql
   # In Prometheus
   rate(service_errors_total[5m]) by (type, severity)
   ```

2. **Review error logs**

   ```bash
   kubectl logs <pod-name> | grep -i error | tail -50
   ```

3. **Check specific endpoint**

   ```promql
   rate(service_requests_total{status=~"5.."}[5m]) by (endpoint)
   ```

4. **Review recent deployments**
   ```bash
   kubectl rollout history deployment/<service-name>
   ```

### Common Causes & Solutions

#### Database Query Failures

**Symptoms**: Errors contain "database" or "query"

**Solution**:

```bash
# Check database connection pool
curl http://<service-url>/debug/vars | jq '.database'

# Review slow queries
kubectl exec -it postgres-0 -- psql -U sahool -c "
  SELECT query, calls, total_time, mean_time
  FROM pg_stat_statements
  ORDER BY total_time DESC
  LIMIT 10;"

# Restart service to reset connection pool
kubectl rollout restart deployment/<service-name>
```

#### External API Failures

**Symptoms**: Errors mention external service (weather API, satellite API)

**Solution**:

```bash
# Check external service status
curl -I https://<external-api>

# Enable circuit breaker (if available)
kubectl set env deployment/<service-name> CIRCUIT_BREAKER_ENABLED=true

# Temporarily disable feature
kubectl set env deployment/<service-name> FEATURE_<name>_ENABLED=false
```

#### Validation Errors

**Symptoms**: 400 errors, validation failures

**Solution**:

```bash
# Review recent input changes
kubectl logs <pod-name> | grep -B 5 "validation error"

# Check API schema version
curl http://<service-url>/ | jq '.version'

# Rollback if recent deployment
kubectl rollout undo deployment/<service-name>
```

### Recovery

1. **Immediate**: Roll back to previous version

   ```bash
   kubectl rollout undo deployment/<service-name>
   ```

2. **Short-term**: Implement fix and deploy
3. **Long-term**: Add monitoring/alerting for this error type

---

## High Latency

### Symptoms

- P95 latency > 5 seconds
- Timeout errors
- Alerts: `HighResponseTime`

### Investigation Steps

1. **Check latency by endpoint**

   ```promql
   histogram_quantile(0.95,
     rate(service_request_duration_seconds_bucket[5m])
   ) by (endpoint)
   ```

2. **Check database queries**

   ```bash
   kubectl exec -it postgres-0 -- psql -U sahool -c "
     SELECT pid, query, state, wait_event_type, wait_event
     FROM pg_stat_activity
     WHERE state != 'idle'
     ORDER BY query_start;"
   ```

3. **Check cache hit rate**

   ```promql
   rate(cache_hits_total[5m]) /
   (rate(cache_hits_total[5m]) + rate(cache_misses_total[5m]))
   ```

4. **Review traces** (if OpenTelemetry enabled)

### Common Causes & Solutions

#### Slow Database Queries

**Symptoms**: Database query time high

**Solution**:

```bash
# Add missing indexes
kubectl exec -it postgres-0 -- psql -U sahool -c "
  CREATE INDEX CONCURRENTLY idx_fields_user_id ON fields(user_id);"

# Analyze query plan
kubectl exec -it postgres-0 -- psql -U sahool -c "
  EXPLAIN ANALYZE <slow-query>;"

# Increase connection pool size
kubectl set env deployment/<service-name> DB_POOL_SIZE=50
```

#### Cache Miss Storm

**Symptoms**: Cache hit rate < 50%

**Solution**:

```bash
# Warm cache
curl -X POST http://<service-url>/admin/cache/warm

# Increase cache TTL
kubectl set env deployment/<service-name> CACHE_TTL_SECONDS=900

# Restart Redis
kubectl rollout restart statefulset/redis
```

#### High Load

**Symptoms**: CPU/memory usage high

**Solution**:

```bash
# Scale horizontally
kubectl scale deployment/<service-name> --replicas=5

# Increase resource limits
kubectl set resources deployment/<service-name> \
  --limits=cpu=2,memory=2Gi \
  --requests=cpu=1,memory=1Gi
```

---

## Database Connection Issues

### Symptoms

- "connection refused" errors
- "too many connections" errors
- Readiness checks failing

### Investigation Steps

1. **Check connection count**

   ```bash
   kubectl exec -it postgres-0 -- psql -U sahool -c "
     SELECT count(*) FROM pg_stat_activity;"
   ```

2. **Check connection pool**

   ```bash
   curl http://<service-url>/debug/vars | jq '.database.pool'
   ```

3. **Check database pod**
   ```bash
   kubectl get pod postgres-0
   kubectl logs postgres-0 --tail=50
   ```

### Solutions

#### Too Many Connections

```bash
# Increase max_connections in PostgreSQL
kubectl edit configmap postgres-config
# Add: max_connections = 200

# Restart PostgreSQL
kubectl rollout restart statefulset/postgres

# Reduce connection pool size per service
kubectl set env deployment/<service-name> DB_POOL_SIZE=10
```

#### Connection Leaks

```bash
# Check for idle connections
kubectl exec -it postgres-0 -- psql -U sahool -c "
  SELECT pid, usename, application_name, state, state_change
  FROM pg_stat_activity
  WHERE state = 'idle in transaction'
  AND state_change < NOW() - INTERVAL '5 minutes';"

# Kill long-running idle connections
kubectl exec -it postgres-0 -- psql -U sahool -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = 'idle in transaction'
  AND state_change < NOW() - INTERVAL '10 minutes';"

# Restart service to reset pool
kubectl rollout restart deployment/<service-name>
```

---

## Cache Failures

### Symptoms

- Redis connection errors
- Cache hit rate drops to 0%
- Increased database load

### Investigation Steps

1. **Check Redis status**

   ```bash
   kubectl get pod -l app=redis
   kubectl exec -it redis-0 -- redis-cli ping
   ```

2. **Check memory usage**

   ```bash
   kubectl exec -it redis-0 -- redis-cli info memory
   ```

3. **Check service logs**
   ```bash
   kubectl logs <pod-name> | grep -i redis
   ```

### Solutions

#### Redis Out of Memory

```bash
# Clear cache
kubectl exec -it redis-0 -- redis-cli FLUSHALL

# Increase memory limit
kubectl set resources statefulset/redis --limits=memory=2Gi

# Enable eviction policy
kubectl exec -it redis-0 -- redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

#### Redis Unavailable

```bash
# Services should fall back to no-cache mode
# Verify fallback is working
curl http://<service-url>/health/ready

# Restart Redis
kubectl rollout restart statefulset/redis

# Services will reconnect automatically
```

---

## Authentication Failures

### Symptoms

- 401 Unauthorized errors
- "Invalid token" errors
- Login failures

### Investigation Steps

1. **Check auth service**

   ```bash
   kubectl get pods -l app=auth-service
   curl http://auth-service:8001/health
   ```

2. **Verify JWT secret**

   ```bash
   kubectl get secret jwt-secret -o yaml
   ```

3. **Check token expiry**
   ```bash
   # Decode JWT token (use jwt.io or CLI tool)
   echo "<token>" | jwt decode -
   ```

### Solutions

#### Invalid JWT Secret

```bash
# Verify all services use same secret
kubectl get deployments -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.template.spec.containers[0].env[?(@.name=="JWT_SECRET_KEY")].value}{"\n"}{end}'

# Update secret
kubectl create secret generic jwt-secret \
  --from-literal=JWT_SECRET_KEY=<new-secret> \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart all services
kubectl rollout restart deployment
```

#### Token Expiry Issues

```bash
# Increase token lifetime
kubectl set env deployment/auth-service JWT_ACCESS_TOKEN_EXPIRE_MINUTES=120

# Force re-login for all users
# (Clear refresh tokens from database)
```

---

## Escalation Matrix

| Severity                                  | Response Time     | Escalation Path                  |
| ----------------------------------------- | ----------------- | -------------------------------- |
| **Critical** (Service down in production) | Immediate         | → DevOps Lead → CTO              |
| **High** (Performance degradation)        | 15 min            | → On-call Engineer → DevOps Lead |
| **Medium** (Non-critical errors)          | 1 hour            | → On-call Engineer               |
| **Low** (Warnings, low impact)            | Next business day | → Create ticket                  |

## Post-Incident

After resolving an incident:

1. **Document resolution** in incident channel
2. **Update runbook** if new procedure discovered
3. **Schedule post-mortem** (for Critical/High severity)
4. **Create improvement tickets**
5. **Update monitoring/alerts** to catch earlier

## References

- [Observability Guide](./OBSERVABILITY.md)
- [Operations Guide](./OPERATIONS.md)
- [Security Guide](./SECURITY.md)
