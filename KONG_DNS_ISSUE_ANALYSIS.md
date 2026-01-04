# Kong DNS Resolution Issue Analysis

## Problem Summary
Kong is reporting DNS resolution errors for `marketplace-service` and `research-core`:
- `dns server error: 3 name error` - DNS name doesn't exist
- `dns server error: 2 server failure` - DNS server failure

## Root Cause
**The DNS errors are a symptom, not the root cause.**

The actual issue is:
1. **Services are constantly restarting** due to database connection failures
2. **PgBouncer authentication is failing** - services can't connect to PostgreSQL
3. **Because services aren't stable**, they're not available on the Docker network
4. **Kong can't resolve DNS** for services that aren't running/stable

## Service Status
- `sahool-marketplace`: Restarting (database connection failure)
- `sahool-research-core`: Restarting (database connection failure)

Both services show:
```
PrismaClientInitializationError: Error querying the database: 
FATAL: server login has been failing, cached error: 
password authentication failed for user "pgbouncer" (server_login_retry)
```

## Kong Configuration
Kong is correctly configured:
- Service names match Docker Compose service names: `marketplace-service` and `research-core`
- Upstream targets are correct: `marketplace-service:3010` and `research-core:3015`
- The issue is that these services aren't stable enough for DNS resolution

## PgBouncer Authentication Issue
PgBouncer is failing to authenticate the `pgbouncer` user when connecting to PostgreSQL to run `auth_query`:

```
WARNING server login failed: FATAL password authentication failed for user "pgbouncer"
```

### Current Configuration
- `pgbouncer` user exists in PostgreSQL with password set
- `AUTH_USER_PASSWORD` environment variable is set in docker-compose.yml
- `auth_user = pgbouncer` in pgbouncer.ini
- `auth_query = SELECT usename, passwd FROM pg_shadow WHERE usename=$1`

### Problem
The `edoburu/pgbouncer` Docker image may not be using the `AUTH_USER_PASSWORD` environment variable correctly, or it needs to be configured differently.

## Solution Path

### Option 1: Fix PgBouncer Authentication (Recommended)
1. Verify the `pgbouncer` user password matches `POSTGRES_PASSWORD`
2. Check if `edoburu/pgbouncer` image supports `AUTH_USER_PASSWORD`
3. Alternative: Configure password in `userlist.txt` or directly in connection string
4. Test PgBouncer connection to PostgreSQL

### Option 2: Temporary Workaround
1. Bypass PgBouncer temporarily for affected services
2. Connect directly to PostgreSQL (not recommended for production)
3. Fix PgBouncer auth, then switch back

### Option 3: Use Different PgBouncer Image
1. Try a different PgBouncer image that better supports SCRAM-SHA-256
2. Or build a custom image with proper configuration

## Expected Outcome
Once PgBouncer authentication is fixed:
1. Services will connect to the database successfully
2. Services will stabilize and stop restarting
3. Services will be available on the Docker network
4. Kong will be able to resolve DNS names
5. Kong DNS errors will disappear

## Next Steps
1. **Investigate edoburu/pgbouncer image documentation** for correct `AUTH_USER_PASSWORD` usage
2. **Test PgBouncer connection** directly: `docker exec sahool-pgbouncer psql -h postgres -U pgbouncer -d sahool`
3. **Verify password match** between `AUTH_USER_PASSWORD` and PostgreSQL `pgbouncer` user
4. **Consider alternative configuration** if environment variable approach doesn't work

## Files to Review
- `docker-compose.yml` - PgBouncer service configuration
- `infrastructure/core/pgbouncer/pgbouncer.ini` - PgBouncer configuration
- `infrastructure/core/postgres/init/02-pgbouncer-user.sql` - User creation script

## Related Issues
- Database connection failures in multiple services
- PgBouncer SCRAM-SHA-256 authentication
- Service stability issues




