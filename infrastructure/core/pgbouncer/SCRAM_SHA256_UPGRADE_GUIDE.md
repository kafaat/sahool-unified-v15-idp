# PgBouncer Authentication Upgrade: MD5 to SCRAM-SHA-256

**Platform:** SAHOOL Unified IDP Platform
**Date:** 2026-01-08
**Migration Status:** ✅ COMPLETED
**PgBouncer Version:** 1.21.0
**PostgreSQL Version:** 16.x

---

## Executive Summary

This guide documents the complete upgrade of PgBouncer authentication from MD5 to SCRAM-SHA-256, providing stronger password hashing and authentication security for the SAHOOL platform.

### What Changed

| Component | Before | After |
|-----------|--------|-------|
| **PgBouncer auth_type** | `md5` | `scram-sha-256` |
| **PostgreSQL password_encryption** | `scram-sha-256` | `scram-sha-256` (no change) |
| **pg_hba.conf auth method** | `scram-sha-256` | `scram-sha-256` (no change) |

### Security Benefits

1. **Salted Password Hashing** - Prevents rainbow table attacks
2. **Challenge-Response Authentication** - Prevents replay attacks
3. **No Plaintext Transmission** - Passwords never sent in plaintext
4. **Forward Secrecy** - Session keys derived during authentication
5. **Mutual Authentication** - Both client and server verify identities

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Configuration Changes](#configuration-changes)
3. [Migration Process](#migration-process)
4. [Testing](#testing)
5. [Rollback Procedure](#rollback-procedure)
6. [Troubleshooting](#troubleshooting)
7. [Technical Details](#technical-details)

---

## Prerequisites

Before starting the migration, verify the following:

### 1. PostgreSQL Configuration

```bash
# Verify password_encryption setting
docker exec sahool-postgres psql -U sahool -d sahool -c "SHOW password_encryption;"
```

Expected output: `scram-sha-256`

### 2. pg_hba.conf Configuration

```bash
# Check pg_hba.conf authentication methods
docker exec sahool-postgres cat /var/lib/postgresql/data/pg_hba.conf | grep -E "^host|^hostssl"
```

All entries should use `scram-sha-256` (already configured).

### 3. User Password Audit

```bash
# Check if any users still have MD5 passwords
docker exec sahool-postgres psql -U sahool -d sahool <<EOF
SELECT usename,
       CASE
           WHEN passwd IS NULL THEN 'No Password'
           WHEN passwd LIKE 'md5%' THEN 'MD5'
           WHEN passwd LIKE 'SCRAM-SHA-256%' THEN 'SCRAM-SHA-256'
           ELSE 'Unknown'
       END as encryption_method
FROM pg_shadow
WHERE usename NOT IN ('postgres');
EOF
```

All users should have `SCRAM-SHA-256` passwords.

---

## Configuration Changes

### 1. PgBouncer Docker Compose

**File:** `/infrastructure/core/pgbouncer/docker-compose.pgbouncer.yml`

```yaml
# Line 43: Changed from md5 to scram-sha-256
AUTH_TYPE: scram-sha-256
AUTH_USER: ${POSTGRES_USER:-sahool}
AUTH_QUERY: SELECT usename, passwd FROM pgbouncer.get_auth($1)
```

### 2. PgBouncer Configuration File

**File:** `/infrastructure/core/pgbouncer/pgbouncer.ini`

```ini
# Line 32: Changed from md5 to scram-sha-256
auth_type = scram-sha-256
auth_query = SELECT usename, passwd FROM pgbouncer.get_auth($1)
auth_user = sahool
```

### 3. PostgreSQL Configuration

**File:** `/config/postgres/postgresql.conf`

```conf
# Line 133: Already configured (no change needed)
password_encryption = scram-sha-256
```

**File:** `/config/postgres/pg_hba.conf`

```conf
# All authentication methods already use scram-sha-256 (no change needed)
hostssl sahool          sahool          172.16.0.0/12          scram-sha-256
hostssl all             sahool          10.0.0.0/8             scram-sha-256
```

---

## Migration Process

### Step 1: Run Pre-Migration Checks

```bash
# Navigate to project root
cd /home/user/sahool-unified-v15-idp

# Run the migration script to verify configuration
docker exec sahool-postgres psql -U sahool -d sahool -f \
  /docker-entrypoint-initdb.d/migrations/V20260108__upgrade_pgbouncer_scram_sha256.sql
```

This script will:
- ✓ Verify PostgreSQL password_encryption is `scram-sha-256`
- ✓ Audit all user passwords (identify MD5 vs SCRAM)
- ✓ Grant necessary permissions (pg_monitor to sahool user)
- ✓ Verify pgbouncer.get_auth() function exists
- ✓ Create helper function to reset passwords if needed

### Step 2: Reset MD5 Passwords (If Needed)

If any users have MD5 passwords, reset them:

```sql
-- Connect to PostgreSQL
docker exec -it sahool-postgres psql -U sahool -d sahool

-- Reset individual user password
SELECT pgbouncer.reset_user_password_to_scram('username', 'new_password');

-- Or manually:
ALTER USER username PASSWORD 'new_password';
-- (Will automatically use scram-sha-256 encryption)
```

### Step 3: Stop PgBouncer Service

```bash
# Stop PgBouncer (if running standalone)
docker compose -f infrastructure/core/pgbouncer/docker-compose.pgbouncer.yml down

# Or stop from main docker-compose
docker compose stop pgbouncer
```

### Step 4: Update Configuration Files

The configuration files have already been updated:
- ✅ `docker-compose.pgbouncer.yml` - AUTH_TYPE changed to scram-sha-256
- ✅ `pgbouncer.ini` - auth_type changed to scram-sha-256

No manual changes needed - files are ready for deployment.

### Step 5: Start PgBouncer with New Configuration

```bash
# Start PgBouncer (standalone deployment)
docker compose -f infrastructure/core/pgbouncer/docker-compose.pgbouncer.yml up -d

# Or start from main docker-compose
docker compose up -d pgbouncer

# Check logs for successful startup
docker logs sahool-pgbouncer --tail 50
```

Look for:
```
LOG kernel file descriptor limit: 1048576 (hard: 1048576); max_client_conn: 500, max expected fd use: 512
LOG listening on 0.0.0.0:6432
LOG process up: pgbouncer 1.21.0, libevent 2.1.12-stable
```

### Step 6: Verify PgBouncer Health

```bash
# Check PgBouncer is running
docker ps | grep pgbouncer

# Check health status
docker inspect sahool-pgbouncer --format='{{.State.Health.Status}}'
# Expected: healthy

# Check PgBouncer admin console
docker exec -it sahool-pgbouncer psql -h localhost -p 6432 -U sahool -d pgbouncer -c "SHOW POOLS;"
```

---

## Testing

### Test 1: Direct PostgreSQL Connection (Baseline)

```bash
# Connect directly to PostgreSQL (bypassing PgBouncer)
docker exec -it sahool-postgres psql -h postgres -U sahool -d sahool

# Verify connection method
\conninfo
# Should show: SCRAM-SHA-256 authentication
```

### Test 2: PgBouncer Connection

```bash
# Connect through PgBouncer
docker exec -it sahool-postgres psql -h sahool-pgbouncer -p 6432 -U sahool -d sahool

# Run a simple query
SELECT current_user, current_database(), version();

# Check connection info
\conninfo
```

### Test 3: Application Service Connection

```bash
# Test from a microservice container
docker exec -it <service-container> psql \
  "host=sahool-pgbouncer port=6432 dbname=sahool user=sahool sslmode=require"
```

### Test 4: Connection Pool Statistics

```bash
# Connect to PgBouncer admin
docker exec -it sahool-pgbouncer psql -h localhost -p 6432 -U sahool -d pgbouncer

-- Check pool status
SHOW POOLS;
SHOW DATABASES;
SHOW CLIENTS;
SHOW SERVERS;

-- Check statistics
SHOW STATS;
```

Expected output for `SHOW POOLS`:
```
 database |   user   | cl_active | cl_waiting | sv_active | sv_idle | sv_used
----------+----------+-----------+------------+-----------+---------+---------
 sahool   | sahool   |         0 |          0 |         0 |      10 |       0
```

### Test 5: Authentication Failure Handling

```bash
# Try to connect with wrong password (should fail gracefully)
docker exec -it sahool-postgres psql \
  "host=sahool-pgbouncer port=6432 dbname=sahool user=sahool password=wrong"

# Expected error:
# psql: error: connection to server at "sahool-pgbouncer" (172.x.x.x), port 6432 failed:
# FATAL:  password authentication failed for user "sahool"
```

### Test 6: Load Testing

```bash
# Simulate multiple concurrent connections
for i in {1..10}; do
  docker exec sahool-postgres psql \
    -h sahool-pgbouncer -p 6432 -U sahool -d sahool \
    -c "SELECT pg_sleep(1), current_user;" &
done

# Monitor pool activity
docker exec sahool-pgbouncer psql -h localhost -p 6432 -U sahool -d pgbouncer \
  -c "SHOW POOLS;" -c "SHOW CLIENTS;"
```

---

## Rollback Procedure

If issues occur, you can rollback to MD5 authentication:

### Step 1: Stop PgBouncer

```bash
docker compose -f infrastructure/core/pgbouncer/docker-compose.pgbouncer.yml down
```

### Step 2: Revert Configuration Changes

**File:** `docker-compose.pgbouncer.yml`
```yaml
# Revert line 43
AUTH_TYPE: md5
```

**File:** `pgbouncer.ini`
```ini
# Revert line 32
auth_type = md5
```

### Step 3: Restart PgBouncer

```bash
docker compose -f infrastructure/core/pgbouncer/docker-compose.pgbouncer.yml up -d
```

**Note:** PostgreSQL can still use SCRAM-SHA-256 passwords even when PgBouncer uses MD5 auth_type, because the auth_query function retrieves the password hashes directly from pg_shadow.

---

## Troubleshooting

### Issue 1: Authentication Failed for User

**Symptom:**
```
FATAL: password authentication failed for user "sahool"
```

**Causes:**
1. User password is not SCRAM-SHA-256 encoded
2. auth_user (sahool) doesn't have pg_monitor role
3. pgbouncer.get_auth() function missing or has wrong permissions

**Solution:**
```sql
-- 1. Verify user password encryption
SELECT usename, passwd FROM pg_shadow WHERE usename = 'sahool';
-- Should show: SCRAM-SHA-256$...

-- 2. Grant pg_monitor role
GRANT pg_monitor TO sahool;

-- 3. Verify function exists
SELECT * FROM pg_proc WHERE proname = 'get_auth';

-- 4. Grant execute permissions
GRANT EXECUTE ON FUNCTION pgbouncer.get_auth(TEXT) TO sahool;
```

### Issue 2: PgBouncer Can't Connect to PostgreSQL

**Symptom:**
```
LOG C-0x12345: sahool/sahool@localhost:6432 login failed: password authentication failed
```

**Causes:**
1. auth_user credentials incorrect in environment variables
2. PostgreSQL pg_hba.conf doesn't allow PgBouncer connection
3. Network connectivity issues

**Solution:**
```bash
# 1. Check environment variables
docker inspect sahool-pgbouncer | grep -A 10 Env

# 2. Verify pg_hba.conf allows Docker network
docker exec sahool-postgres cat /var/lib/postgresql/data/pg_hba.conf

# 3. Test direct PostgreSQL connection from PgBouncer container
docker exec sahool-pgbouncer psql -h postgres -U sahool -d sahool
```

### Issue 3: Connection Timeout

**Symptom:**
```
timeout: could not connect to server
```

**Causes:**
1. PgBouncer not running
2. Network configuration issue
3. Port not exposed

**Solution:**
```bash
# 1. Check PgBouncer is running
docker ps | grep pgbouncer

# 2. Check network connectivity
docker exec sahool-pgbouncer ping postgres

# 3. Verify port binding
docker port sahool-pgbouncer
# Expected: 6432/tcp -> 127.0.0.1:6432
```

### Issue 4: Too Many Connections

**Symptom:**
```
FATAL: sorry, too many clients already
```

**Causes:**
1. max_client_conn reached
2. Connection leak in application
3. Pool size too small

**Solution:**
```bash
# Check current connections
docker exec sahool-pgbouncer psql -h localhost -p 6432 -U sahool -d pgbouncer \
  -c "SHOW CLIENTS;" -c "SHOW POOLS;"

# Increase limits in pgbouncer.ini if needed:
# max_client_conn = 800
# max_db_connections = 250
# default_pool_size = 30
```

### Issue 5: SSL/TLS Issues

**Symptom:**
```
FATAL: no pg_hba.conf entry for host
```

**Causes:**
1. SSL certificates missing
2. pg_hba.conf requires SSL but client doesn't use it
3. Certificate verification failed

**Solution:**
```bash
# Check if SSL is required
docker exec sahool-postgres cat /var/lib/postgresql/data/pg_hba.conf | grep hostssl

# For development, you can temporarily allow non-SSL from Docker network
# Add to pg_hba.conf (DEVELOPMENT ONLY):
# host    all             sahool          172.16.0.0/12          scram-sha-256

# Restart PostgreSQL
docker compose restart postgres
```

---

## Technical Details

### How SCRAM-SHA-256 Authentication Works

1. **Client → PgBouncer:** Client sends username
2. **PgBouncer → PostgreSQL:** PgBouncer runs `auth_query` using `auth_user`
3. **PostgreSQL:** Executes `pgbouncer.get_auth(username)` function
4. **Function:** Returns SCRAM-SHA-256 password hash from `pg_shadow`
5. **PgBouncer:** Performs SCRAM challenge-response with client
6. **Client:** Proves knowledge of password without sending it
7. **PgBouncer:** Verifies response matches stored hash
8. **Success:** Connection established

### Authentication Flow Diagram

```
┌─────────────┐          ┌──────────────┐          ┌──────────────┐
│   Client    │          │  PgBouncer   │          │ PostgreSQL   │
│ (App/User)  │          │ (Pooler)     │          │  (Database)  │
└─────────────┘          └──────────────┘          └──────────────┘
      │                          │                          │
      │  1. Connect (username)   │                          │
      │─────────────────────────>│                          │
      │                          │                          │
      │                          │  2. auth_query           │
      │                          │  (get_auth function)     │
      │                          │─────────────────────────>│
      │                          │                          │
      │                          │  3. SCRAM hash           │
      │                          │<─────────────────────────│
      │                          │                          │
      │  4. SCRAM challenge      │                          │
      │<─────────────────────────│                          │
      │                          │                          │
      │  5. SCRAM response       │                          │
      │─────────────────────────>│                          │
      │                          │                          │
      │  6. Verify response      │                          │
      │     (success)            │                          │
      │                          │                          │
      │  7. Connection OK        │                          │
      │<─────────────────────────│                          │
      │                          │                          │
```

### pgbouncer.get_auth() Function

```sql
CREATE OR REPLACE FUNCTION pgbouncer.get_auth(p_usename TEXT)
RETURNS TABLE(usename NAME, passwd TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT
        u.usename::NAME,
        u.passwd::TEXT
    FROM pg_catalog.pg_shadow u
    WHERE u.usename = p_usename;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

**Key Points:**
- `SECURITY DEFINER` - Runs with owner privileges (can read pg_shadow)
- Returns password hash from `pg_shadow` system catalog
- Hash format: `SCRAM-SHA-256$<iteration-count>:<salt>$<stored-key>:<server-key>`
- PgBouncer uses this hash for SCRAM authentication

### SCRAM-SHA-256 Password Format

```
SCRAM-SHA-256$4096:Aa1Bb2Cc3Dd4Ee5Ff6Gg7Hh8==$StoredKey:ServerKey
│            │    │                           │         │
│            │    └─ Base64 salt              │         └─ Server key (auth server)
│            └────── Iteration count          └─────────── Stored key (client proof)
└─────────────────── Hash algorithm
```

**Components:**
- **Algorithm:** SCRAM-SHA-256 (SHA-256 based)
- **Iterations:** 4096 (default, prevents brute force)
- **Salt:** Random bytes, prevents rainbow tables
- **Stored Key:** Client proof verification
- **Server Key:** Server authentication

### Performance Comparison: MD5 vs SCRAM-SHA-256

| Metric | MD5 | SCRAM-SHA-256 | Impact |
|--------|-----|---------------|--------|
| **Hash Time** | ~0.1 ms | ~1-2 ms | +10-20x (negligible for auth) |
| **Security** | Weak (deprecated) | Strong (modern) | ✓ Significant improvement |
| **Salt** | No | Yes | ✓ Prevents rainbow tables |
| **Challenge-Response** | No | Yes | ✓ Prevents replay attacks |
| **Password Transmission** | Hash sent | Never sent | ✓ Enhanced security |
| **Connection Overhead** | Minimal | Slightly higher | ~1-2ms per connection |
| **PgBouncer Compatibility** | Full | Full (v1.18+) | ✓ No compatibility issues |

### Security Considerations

1. **Password Storage**
   - SCRAM-SHA-256 hashes are one-way (cannot be reversed)
   - Even if database is compromised, passwords are safe
   - Salt prevents rainbow table attacks

2. **Network Security**
   - Always use SSL/TLS for connections (configured in pg_hba.conf)
   - SCRAM adds authentication security, SSL adds transport security
   - Combined: Strong end-to-end security

3. **Backward Compatibility**
   - PostgreSQL can store both MD5 and SCRAM passwords simultaneously
   - Old clients with MD5 passwords can still connect if pg_hba.conf allows
   - Migration can be gradual (user-by-user password resets)

4. **Best Practices**
   - Always set `password_encryption = scram-sha-256` in postgresql.conf
   - Use `hostssl` entries in pg_hba.conf (require SSL)
   - Regularly rotate database passwords
   - Monitor authentication failures in logs

---

## References

### Documentation

- [PostgreSQL SCRAM Authentication](https://www.postgresql.org/docs/16/auth-password.html)
- [PgBouncer Configuration](https://www.pgbouncer.org/config.html)
- [RFC 5802: SCRAM-SHA-1](https://tools.ietf.org/html/rfc5802)
- [RFC 7677: SCRAM-SHA-256](https://tools.ietf.org/html/rfc7677)

### Files Modified

1. `/infrastructure/core/pgbouncer/docker-compose.pgbouncer.yml`
2. `/infrastructure/core/pgbouncer/pgbouncer.ini`
3. `/infrastructure/core/postgres/init/02-pgbouncer-user.sql`
4. `/infrastructure/core/postgres/migrations/V20260108__upgrade_pgbouncer_scram_sha256.sql`

### Configuration Files (No Changes Needed)

1. `/config/postgres/postgresql.conf` - Already has `password_encryption = scram-sha-256`
2. `/config/postgres/pg_hba.conf` - Already uses `scram-sha-256` authentication

---

## Monitoring and Maintenance

### Logs to Monitor

```bash
# PgBouncer logs
docker logs -f sahool-pgbouncer

# Look for authentication errors
docker logs sahool-pgbouncer 2>&1 | grep -i "auth\|failed\|error"

# PostgreSQL logs
docker logs -f sahool-postgres | grep -i "auth\|scram"
```

### Regular Health Checks

```bash
#!/bin/bash
# health-check.sh - Run this script periodically

echo "=== PgBouncer Health Check ==="

# 1. Check PgBouncer is running
if docker ps | grep -q sahool-pgbouncer; then
    echo "✓ PgBouncer is running"
else
    echo "✗ PgBouncer is not running"
    exit 1
fi

# 2. Check pool status
echo ""
echo "Pool Status:"
docker exec sahool-pgbouncer psql -h localhost -p 6432 -U sahool -d pgbouncer \
  -c "SHOW POOLS;" -t

# 3. Check authentication method
echo ""
echo "PostgreSQL password_encryption:"
docker exec sahool-postgres psql -U sahool -d sahool \
  -c "SHOW password_encryption;" -t

# 4. Test connection
echo ""
echo "Connection test:"
if docker exec sahool-postgres psql -h sahool-pgbouncer -p 6432 -U sahool -d sahool \
  -c "SELECT 'OK' as status;" -t | grep -q "OK"; then
    echo "✓ Connection successful"
else
    echo "✗ Connection failed"
    exit 1
fi

echo ""
echo "=== All checks passed ==="
```

### Metrics to Track

1. **Authentication Success Rate**
   - Monitor for sudden increases in auth failures
   - Could indicate password issues or attacks

2. **Connection Pool Utilization**
   - Track `cl_active / max_client_conn` ratio
   - Alert if consistently above 80%

3. **Query Wait Time**
   - Monitor `SHOW STATS` for high wait times
   - Indicates pool exhaustion

4. **Server Connection Count**
   - Track `sv_active + sv_idle` in `SHOW POOLS`
   - Should stay below `max_db_connections`

---

## Conclusion

The SCRAM-SHA-256 authentication upgrade provides significantly enhanced security for the SAHOOL platform while maintaining full compatibility with existing applications.

**Migration Status:** ✅ COMPLETE

**Security Improvements:**
- ✓ Strong password hashing (SCRAM-SHA-256 vs MD5)
- ✓ Salt-based protection against rainbow tables
- ✓ Challenge-response prevents replay attacks
- ✓ No plaintext password transmission
- ✓ Mutual authentication (client and server)

**Performance Impact:** Negligible (~1-2ms per connection)

**Compatibility:** Full (no application changes required)

For questions or issues, refer to the troubleshooting section or contact the platform team.

---

**Last Updated:** 2026-01-08
**Version:** 1.0
**Status:** Production Ready
