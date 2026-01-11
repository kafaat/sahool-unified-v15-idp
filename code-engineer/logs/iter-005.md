# Iteration 005 — Document Non-Existent Kong Upstreams

**Timestamp:** 2026-01-08T21:27:00Z
**Target service:** kong (16 non-existent service upstreams)
**Goal:** Document non-existent upstreams to prevent confusion and aid future debugging

## Evidence (Before)
- Kong config defines 16 upstreams for services not in docker-compose.yml
- These services will fail healthchecks and return 503 when accessed
- No documentation exists about these placeholder services

## Hypothesis
- Kong will load successfully but routes to these services will fail
- Active healthchecks will spam logs with connection failures
- Developers may be confused about which services are actually implemented

## Actions Taken

### File Changes
- `infrastructure/gateway/kong/kong.yml` (lines 486-513)
  - Added detailed warning comment block
  - Listed all 16 non-existent services with their ports
  - Documented fix options:
    1. Implement the services in docker-compose.yml
    2. Comment out the upstreams and corresponding routes

## Non-Existent Services Listed
| Service | Port |
|---------|------|
| user-service | 3025 |
| agent-registry | 8150 |
| ai-agents-core | 8122 |
| globalgap-compliance | 8153 |
| analytics-service | 8154 |
| reporting-service | 8155 |
| integration-service | 8156 |
| audit-service | 8157 |
| export-service | 8158 |
| import-service | 8159 |
| admin-dashboard | 3001 |
| monitoring-service | 8160 |
| logging-service | 8161 |
| tracing-service | 8162 |
| cache-service | 8163 |
| search-service | 8164 |

## Evidence (After)
- Warning comment block added at line 486-513
- Future developers will understand these are placeholder services

## Result
- **PASS** (Documentation fix - services still return 503)
- Known Issue: Routes to these 16 services will return 503
- Next step: Make Ollama optional with profile (Fix 7)
