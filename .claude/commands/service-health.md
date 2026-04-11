---
description: Check health and readiness of all SAHOOL microservices
argument-hint: [service-name]
---

Check the health, readiness, and basic metrics of SAHOOL services. If `$1` is provided, check only that service; otherwise check all.

## Steps

1. Read `governance/services.yaml` to get the authoritative list of services + ports.
2. For each service (or just `$1`):
   - `curl -sf http://localhost:$PORT/healthz` — liveness
   - `curl -sf http://localhost:$PORT/readyz` — readiness (checks DB + NATS)
   - `curl -sf http://localhost:$PORT/metrics | head -50` — Prometheus metrics sample

3. Run parallel checks with `make health` as a sanity cross-check.

4. Aggregate results into a table:

   ```
   | Service | Port | Live | Ready | DB | NATS | Notes |
   ```

5. For any service that is **unhealthy** or **not-ready**:
   - Fetch the last 20 log lines: `docker compose logs --tail=20 <service>`
   - Identify the likely cause (connection refused, JWT misconfig, migration needed)
   - Suggest the shortest fix, but do NOT apply it without user approval

6. Cross-reference port drift:
   - Compare actual listening ports against `packages/shared-types/src/contracts/service-ports.ts`
   - Flag any mismatch

## Output format

```
## Healthy services (N)
[table]

## Unhealthy services (N)
[table + diagnostics]

## Port drift (N)
[diff between actual and contract]

## Recommended next actions
[bulleted list]
```

Do NOT restart or modify any running service. This is a read-only diagnostic command.
