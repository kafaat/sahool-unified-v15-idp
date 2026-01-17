# CI Issues Resolved - January 2026

This document tracks CI/CD issues discovered and resolved to prevent recurrence.

## Issue Summary

| #   | Issue                      | Root Cause                                      | Fix                                                  | Files Changed                                   |
| --- | -------------------------- | ----------------------------------------------- | ---------------------------------------------------- | ----------------------------------------------- |
| 1   | Services not in governance | New services added without registration         | Register all services in `governance/services.yaml`  | governance/services.yaml                        |
| 2   | Duplicate port conflict    | Port 8095 used by two services                  | Assign unique port 8150 to crop-intelligence-service | governance/services.yaml                        |
| 3   | Null port in agro-rules    | NATS worker had `port: null`                    | Assign port 8151 to agro-rules                       | governance/services.yaml                        |
| 4   | Slack webhook failure      | `SLACK_WEBHOOK_URL` secret missing              | Make Slack notifications conditional                 | cd-staging.yml, cd-production.yml, security.yml |
| 5   | Layer services mismatch    | New services not in `event_architecture.layers` | Update layer service lists                           | governance/services.yaml                        |

---

## Detailed Analysis

### 1. Services Not Registered in Governance

**Problem:** 8 services existed in code but were not registered in `governance/services.yaml`:

- mcp-server
- agro-rules
- crop-intelligence-service
- equipment-service
- task-service
- ws-gateway
- ndvi-processor
- field-intelligence

**Impact:** CI validation failed because generators couldn't find service definitions.

**Solution:** Added all 8 services to `governance/services.yaml` with proper configuration:

- Port assignment
- Layer assignment
- Category assignment
- Events (produces/consumes)
- Dependencies

**Prevention:** Before adding a new service directory, always:

1. Add entry to `governance/services.yaml`
2. Run `make generate-infra` to regenerate compose files
3. Run validators before committing

---

### 2. Duplicate Port Conflict

**Problem:** Port 8095 was assigned to both:

- `crop-health-ai` (existing deprecated service)
- `crop-intelligence-service` (new replacement service)

**Impact:** Docker Compose validation failed due to port conflict.

**Solution:** Changed `crop-intelligence-service` port from 8095 to 8150.

**Prevention:**

- CI now validates unique ports via `governance-ci.yml`
- Use port ranges:
  - 3000-3999: NestJS services
  - 8000-8099: Python core services
  - 8100-8199: Python additional services
  - 8200+: Integration services

---

### 3. Null Port in agro-rules Service

**Problem:** `agro-rules` was defined with `port: null` because it's a NATS worker without HTTP endpoint.

**Impact:** Docker Compose generator produced invalid YAML:

```yaml
ports:
  - None:None
healthcheck:
  test: http://localhost:NoneNone
```

**Solution:** Assigned port 8151 to agro-rules with HTTP healthcheck.

**Prevention:** All services must have valid ports. NATS workers should still expose HTTP for:

- Health checks
- Metrics endpoint
- Debugging

---

### 4. Slack Webhook Secret Missing

**Problem:** CI workflows failed because `SLACK_WEBHOOK_URL` secret was not configured in repository.

**Impact:** Deploy to Staging and other workflows failed at notification steps.

**Solution:** Made Slack notifications conditional:

```yaml
# Before
if: ${{ failure() }}

# After
if: ${{ failure() && secrets.SLACK_WEBHOOK_URL != '' }}
```

**Prevention:** All optional integrations should check for secret existence before using.

**Files Changed:**

- `.github/workflows/cd-staging.yml`
- `.github/workflows/cd-production.yml`
- `.github/workflows/security.yml`

---

### 5. Event Architecture Layers Mismatch

**Problem:** New services were not listed in `event_architecture.layers` section.

**Impact:** Documentation inconsistency between layer definitions and actual services.

**Solution:** Updated `event_architecture.layers` to include all services:

```yaml
intelligence:
  services:
    [
      ...,
      agro-rules,
      crop-intelligence-service,
      ndvi-processor,
      field-intelligence,
    ]

business:
  services: [..., mcp-server, task-service, equipment-service, ws-gateway]
```

**Prevention:** When adding services, update both:

1. `services:` section with full configuration
2. `event_architecture.layers:` with service name in correct layer

---

## Commits

| Commit     | Description                                                        |
| ---------- | ------------------------------------------------------------------ |
| `9d556d63` | feat: register missing services in governance                      |
| `071b90a7` | ci: add missing services to container testing workflow             |
| `6fcd02e4` | chore: regenerate infrastructure files after governance update     |
| `b6beccc4` | chore: regenerate compose files from services.yaml                 |
| `d5b7bb74` | fix: resolve duplicate port conflict for crop-intelligence-service |
| `9142c409` | fix: assign port 8151 to agro-rules service                        |
| `a09e3815` | fix: make Slack notifications conditional on webhook secret        |
| `1e7b63c5` | fix: update event_architecture.layers with new services            |

---

## Validation Checklist

Before pushing changes to governance or services:

- [ ] All services registered in `governance/services.yaml`
- [ ] Each service has unique port
- [ ] Service layer matches `event_architecture.layers`
- [ ] Run `python3 scripts/generators/generate_infra.py --all`
- [ ] Run `python tools/generators/compose-generator.py`
- [ ] Verify no git diff after regeneration
- [ ] All Dockerfiles exist for registered services

## CI Workflows Affected

| Workflow              | What it Checks                        |
| --------------------- | ------------------------------------- |
| `infra-sync.yml`      | Generated files match source          |
| `generator-guard.yml` | Compose files in sync                 |
| `governance-ci.yml`   | Port uniqueness, service registration |
| `container-tests.yml` | Services build and start              |

---

_Last Updated: January 2026_
