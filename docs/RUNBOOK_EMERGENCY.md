# SAHOOL Emergency Response Runbook

## CRITICAL: Tenant Data Leak Detected

### Symptoms

- Users report seeing other tenants' data
- Error logs show cross-tenant queries
- Monitoring alerts: `TenantIsolationBreach`

### Immediate Response (First 5 minutes)

#### 1. STOP THE BLEEDING

```bash
# Enable emergency read-only mode
kubectl apply -f k8s/emergency/read-only-mode.yaml

# Or scale down affected services
kubectl scale deployment affected-service --replicas=0
```

#### 2. NOTIFY STAKEHOLDERS

- Post in **#incident-response** Slack
- Page on-call engineer
- Notify security team if PII involved

### Investigation (Next 15 minutes)

```python
# scripts/emergency_investigation.py
import asyncio
from shared.platform import tenant_db

async def investigate_leak():
    """Find source of tenant isolation breach"""

    async with tenant_db() as conn:
        # 1. Check recent queries without tenant context
        suspicious = await conn.fetch("""
            SELECT
                query,
                calls,
                mean_time,
                rows
            FROM pg_stat_statements
            WHERE query NOT LIKE '%current_tenant%'
            AND query LIKE '%SELECT%FROM%fields%'
            AND calls > 0
            ORDER BY calls DESC
            LIMIT 20
        """)

        print("Suspicious queries (no tenant filter):")
        for row in suspicious:
            print(f"  {row['query'][:100]}...")

        # 2. Check RLS status
        tables = await conn.fetch("""
            SELECT tablename, rowsecurity, forcerowsecurity
            FROM pg_tables
            WHERE schemaname = 'public'
        """)

        for table in tables:
            if not table['rowsecurity']:
                print(f"❌ RLS DISABLED: {table['tablename']}")

        # 3. Check recent deployments
        print("\nRecent deployments:")
        # Query deployment logs

asyncio.run(investigate_leak())
```

### Recovery

#### 1. Fix the Issue

- **If RLS disabled:** `ALTER TABLE X FORCE ROW LEVEL SECURITY;`
- **If code bug:** Deploy hotfix
- **If config error:** Rollback to last known good

#### 2. Verify Fix

```bash
python scripts/verify-isolation.py --environment production
```

#### 3. Resume Service

```bash
kubectl scale deployment affected-service --replicas=10
```

#### 4. Post-Incident

- Write incident report
- Update runbook
- Schedule post-mortem

---

## HIGH: Service Degradation

### Symptoms

- High latency alerts
- Error rate spike
- Tenant complaint about slowness

### Response

```bash
# Check service health
sahool-cli status --environment production

# Check resource utilization
kubectl top pods -n sahool-production

# Auto-scale if needed
sahool-cli auto-scale --environment production

# Rollback if recent deploy
sahool-cli rollback --service <name> --to-version <previous>
```

---

## MEDIUM: Database Connection Exhaustion

### Symptoms

- `too many clients` errors in logs
- Connection pool timeouts
- Services unable to query database

### Response

```bash
# Check active connections
psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"

# Check connections per tenant
psql -c "
  SELECT current_setting('app.current_tenant', true) AS tenant,
         state, count(*)
  FROM pg_stat_activity
  GROUP BY 1, 2
  ORDER BY 3 DESC;
"

# Terminate idle connections
psql -c "
  SELECT pg_terminate_backend(pid)
  FROM pg_stat_activity
  WHERE state = 'idle'
  AND state_change < NOW() - INTERVAL '10 minutes';
"
```

---

## Contacts

| Role              | Contact                           |
|-------------------|-----------------------------------|
| Platform Team     | #sahool-platform (Slack)          |
| On-Call Engineer  | PagerDuty rotation                |
| Security Team     | security@sahool.dev               |
| Database Admin    | dba@sahool.dev                    |
