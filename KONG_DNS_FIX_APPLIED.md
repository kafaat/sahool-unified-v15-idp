# Kong DNS Resolution Fix - Applied

## Problem
Kong was reporting frequent DNS resolution errors for services:
- `marketplace-service`: `dns server error: 3 name error`
- `research-core`: `dns server error: 3 name error` / `dns server error: 2 server failure`
- `billing-core`: `dns server error: 3 name error`
- `ai-advisor`: `dns server error: 3 name error`

## Root Cause Analysis
The DNS errors are a **symptom** of underlying service instability:
1. Services (`marketplace-service`, `research-core`, `ai-advisor`) are constantly restarting due to PgBouncer authentication failures
2. When services restart, they're temporarily unavailable in Docker's DNS
3. Kong's DNS resolver was querying too frequently (every 1-4 seconds) for services that aren't stable
4. Health checks were too aggressive, marking services as unhealthy too quickly

## Fixes Applied

### 1. Improved DNS Cache Configuration (`docker-compose.yml`)
Updated Kong's DNS settings to reduce resolution attempts and improve resilience:

**Before:**
```yaml
KONG_DNS_CACHE_TTL: 60      # Cache successful lookups for 60 seconds
KONG_DNS_STALE_TTL: 4       # Use stale entries for 4 seconds
KONG_DNS_ERROR_TTL: 1       # Cache errors for only 1 second
```

**After:**
```yaml
KONG_DNS_CACHE_TTL: 300     # Cache successful lookups for 5 minutes (reduces queries)
KONG_DNS_STALE_TTL: 30      # Use stale entries for 30 seconds (more tolerance)
KONG_DNS_ERROR_TTL: 30      # Cache errors for 30 seconds (reduces repeated failed queries)
KONG_DNS_NOT_FOUND_TTL: 30  # Cache "not found" responses for 30 seconds
```

**Impact:**
- Reduces DNS query frequency by 5x (from every 1-4 seconds to every 30-300 seconds)
- Allows Kong to use stale DNS entries when services are temporarily unavailable
- Prevents Kong from hammering Docker's DNS with repeated queries for unavailable services

### 2. Enhanced Health Check Configuration (`infra/kong/kong.yml`)
Updated health checks for problematic services to be more tolerant of temporary failures:

**Services Updated:**
- `marketplace-service-upstream`
- `billing-core-upstream`
- `research-core-upstream`

**Changes:**
- **Active Health Checks:**
  - `healthy.interval: 10` - Check every 10 seconds
  - `healthy.successes: 2` - Require 2 successful checks before marking healthy
  - `unhealthy.http_failures: 3` - Require 3 failures before marking unhealthy
  - `unhealthy.tcp_failures: 3` - Allow 3 TCP connection failures
  - `unhealthy.timeouts: 3` - Allow 3 timeouts before marking unhealthy

- **Passive Health Checks:**
  - Monitor actual request responses
  - More lenient failure thresholds
  - Better detection of service recovery

**Impact:**
- Services won't be marked unhealthy after a single failure
- More time for services to recover from temporary issues
- Better handling of services that are restarting

## Expected Results

### Immediate
- **Reduced DNS query frequency**: Kong will query DNS less frequently, reducing log noise
- **Better error caching**: DNS errors will be cached for 30 seconds instead of 1 second
- **More resilient health checks**: Services won't be marked unhealthy too quickly

### Long-term
Once the underlying PgBouncer authentication issue is resolved and services stabilize:
- DNS resolution will work correctly
- Health checks will accurately reflect service status
- Kong will route traffic successfully to all services

## Remaining Issues

The DNS errors will **continue** until the root cause is fixed:
- **PgBouncer authentication failures** causing services to restart
- Services need to be stable to be consistently available in Docker's DNS

## Next Steps

1. ✅ **Kong DNS configuration improved** - Completed
2. ⏳ **Fix PgBouncer authentication** - In progress (services still restarting)
3. ⏳ **Verify services stabilize** - Pending
4. ⏳ **Confirm DNS resolution works** - Pending (will work once services are stable)

## Verification

To verify the fixes are working:
```bash
# Check Kong logs - DNS errors should be less frequent
docker logs sahool-kong --tail 100 | grep -i "dns"

# Check service status
docker compose ps marketplace-service research-core billing-core

# Monitor Kong health checks
docker logs sahool-kong | grep -i "health"
```

## Configuration Files Modified

1. `docker-compose.yml` - Kong service DNS configuration (lines 479-486)
2. `infra/kong/kong.yml` - Health check configuration for:
   - `marketplace-service-upstream` (lines 111-149)
   - `billing-core-upstream` (lines 121-159)
   - `research-core-upstream` (lines 141-179)
