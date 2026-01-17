# Iteration 002 — Fix PgBouncer Hardcoded Password

**Timestamp:** 2026-01-08T21:18:00Z
**Target service:** pgbouncer
**Goal:** Remove hardcoded password from PgBouncer config to enable dynamic password injection

## Evidence (Before)

- config file: `infrastructure/core/pgbouncer/pgbouncer.ini:8`
- content: `sahool = host=postgres port=5432 dbname=sahool user=sahool password=change_this_secure_password_in_production`
- issue: Password hardcoded, will not match actual POSTGRES_PASSWORD

## Hypothesis

- PgBouncer authentication will fail because hardcoded password differs from environment variable
- edoburu/pgbouncer image expects to inject password via DB_PASSWORD environment variable

## Actions Taken

### File Changes

- `infrastructure/core/pgbouncer/pgbouncer.ini`
  - Removed hardcoded `password=change_this_secure_password_in_production` from line 8
  - Removed `user=sahool` (not needed when using auth_query)
  - Commented out `sahool_readonly` as postgres-replica is not defined in docker-compose
  - Updated wildcard entry to use simpler format
  - Added documentation comments explaining password injection

## Evidence (After)

- config line 8: `sahool = host=postgres port=5432 dbname=sahool`
- No hardcoded passwords in config file

## Result

- **PASS**
- Next step: Create required directories for volume mounts (Fix 3)
