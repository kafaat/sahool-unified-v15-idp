# Kong DNS Resolution Issues - Update

## Current Status

Kong is still reporting DNS resolution errors for:
- `ai-advisor` - DNS name error
- `marketplace-service` - DNS name error

## Root Causes

### 1. ai-advisor Service
**Issue:** Python code error - `NameError: name 'logger' is not defined`
- **Location:** `apps/services/ai-advisor/src/main.py` line 45
- **Problem:** `logger` was being used before it was defined
- **Fix Applied:** Moved structlog configuration and logger definition before the A2A import try/except block
- **Status:** ✅ Fixed - Service rebuilt and restarted

### 2. marketplace-service
**Issue:** PgBouncer authentication failure
- **Error:** `password authentication failed for user "pgbouncer" (server_login_retry)`
- **Status:** ⏳ Ongoing - Same issue affecting multiple Prisma-based services
- **Impact:** Service constantly restarting, not stable for DNS resolution

## Fixes Applied

### ai-advisor Code Fix
**File:** `apps/services/ai-advisor/src/main.py`

**Before:**
```python
# Import A2A Protocol Support
try:
    from a2a.server import create_a2a_router
    from .a2a_adapter import create_ai_advisor_a2a_agent
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False
    logger.warning("A2A protocol support not available")  # ❌ logger not defined yet

# Configure structured logging
structlog.configure(...)
logger = structlog.get_logger()  # ✅ logger defined here
```

**After:**
```python
# Configure structured logging FIRST
structlog.configure(...)
logger = structlog.get_logger()  # ✅ logger defined first

# Import A2A Protocol Support
try:
    from a2a.server import create_a2a_router
    from .a2a_adapter import create_ai_advisor_a2a_agent
    A2A_AVAILABLE = True
except ImportError:
    A2A_AVAILABLE = False
    logger.warning("A2A protocol support not available")  # ✅ logger now available
```

## Expected Results

### ai-advisor
- ✅ Service should start without `NameError`
- ✅ Service should become stable and available for DNS resolution
- ✅ Kong DNS errors for `ai-advisor` should stop once service is stable

### marketplace-service
- ⏳ Still needs PgBouncer authentication fix
- ⏳ Once authentication is fixed, service should stabilize
- ⏳ Kong DNS errors will stop once service is stable

## Verification

To verify the fixes:
```bash
# Check ai-advisor status
docker compose ps ai-advisor

# Check ai-advisor logs for errors
docker logs sahool-ai-advisor --tail 50 | grep -i "error\|nameerror"

# Check Kong DNS errors (should decrease for ai-advisor)
docker logs sahool-kong --tail 100 | grep -i "ai-advisor"

# Check marketplace-service status (still restarting)
docker compose ps marketplace-service
```

## Next Steps

1. ✅ **ai-advisor code fix** - Completed
2. ⏳ **Verify ai-advisor stability** - Monitor logs
3. ⏳ **Fix PgBouncer authentication** - For marketplace-service and other Prisma services
4. ⏳ **Monitor Kong DNS resolution** - Should improve as services stabilize

## Related Issues

- PgBouncer authentication failures affecting multiple services
- Services restarting prevent consistent DNS registration
- Kong DNS errors are symptoms of service instability


