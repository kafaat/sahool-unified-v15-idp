# Redis Security Quick Start Guide
# دليل البدء السريع لأمان Redis

**Platform:** SAHOOL Unified Agricultural Platform v15-IDP
**Version:** 1.0.0
**Last Updated:** 2026-01-06

---

## Quick Reference

This is a quick-start guide for enabling Redis security features. For complete documentation, see [REDIS_SECURITY_HARDENING_SUMMARY.md](../../REDIS_SECURITY_HARDENING_SUMMARY.md).

---

## Table of Contents

1. [Current Status](#1-current-status)
2. [Enable TLS (5 Minutes)](#2-enable-tls-5-minutes)
3. [Enable ACL (10 Minutes)](#3-enable-acl-10-minutes)
4. [Verify Security](#4-verify-security)
5. [Troubleshooting](#5-troubleshooting)

---

## 1. Current Status

**✅ Already Configured:**
- ✅ Strong password authentication (`REDIS_PASSWORD`)
- ✅ Dangerous commands renamed (FLUSHDB, FLUSHALL, etc.)
- ✅ Memory limits and eviction policy
- ✅ AOF + RDB persistence
- ✅ Network isolation (Docker)
- ✅ Connection timeouts
- ✅ Slow query logging
- ✅ Kubernetes maxmemory settings

**⚠️ Optional (Ready to Enable):**
- ⚠️ TLS/SSL encryption (configured, disabled by default)
- ⚠️ ACL (Access Control Lists) with 4 user roles (configured, disabled by default)

---

## 2. Enable TLS (5 Minutes)

### Step 1: Generate Certificates

```bash
# Run certificate generation script
./scripts/generate-redis-certs.sh

# Verify certificates created
ls -la config/redis/certs/
# Expected: ca.crt, ca.key, server.crt, server.key, client.crt, client.key
```

### Step 2: Update Docker Compose

**For Standalone Redis (`docker-compose.yml`):**

```yaml
redis:
  command: [
    "redis-server",
    "/usr/local/etc/redis/redis.conf",
    "--requirepass", "${REDIS_PASSWORD:?REDIS_PASSWORD is required}",
    "--maxmemory", "512mb",
    # UNCOMMENT THESE LINES FOR TLS:
    "--port", "0",
    "--tls-port", "6379",
    "--tls-cert-file", "/etc/redis/certs/server.crt",
    "--tls-key-file", "/etc/redis/certs/server.key",
    "--tls-ca-cert-file", "/etc/redis/certs/ca.crt",
    "--tls-auth-clients", "optional"
  ]
  volumes:
    - redis_data:/data
    - ./infrastructure/redis/redis-secure.conf:/usr/local/etc/redis/redis.conf:ro
    - ./config/redis/certs:/etc/redis/certs:ro  # UNCOMMENT THIS LINE
```

**For HA Redis (`docker-compose.redis-ha.yml`):**

Add the same TLS arguments and volume mount to:
- `redis-master`
- `redis-replica-1`
- `redis-replica-2`

### Step 3: Update Connection Strings

**Before:**
```
redis://:${REDIS_PASSWORD}@redis:6379/0
```

**After:**
```
rediss://:${REDIS_PASSWORD}@redis:6379/0
```

Note the double 's' in `rediss://` for TLS connections.

### Step 4: Restart Redis

```bash
# For standalone
docker-compose restart redis

# For HA
docker-compose -f docker-compose.redis-ha.yml restart
```

### Step 5: Verify TLS

```bash
# Test TLS connection
redis-cli --tls \
  --cert config/redis/certs/client.crt \
  --key config/redis/certs/client.key \
  --cacert config/redis/certs/ca.crt \
  -h localhost -p 6379 -a $REDIS_PASSWORD PING

# Expected: PONG
```

**✅ TLS is now enabled!**

---

## 3. Enable ACL (10 Minutes)

### Step 1: Set ACL Passwords

Add to `.env` file:

```bash
# Existing
REDIS_PASSWORD=your-strong-password-here

# Add these for ACL
REDIS_APP_PASSWORD=app-user-password-32-chars-minimum
REDIS_ADMIN_PASSWORD=admin-user-password-32-chars-minimum
REDIS_KONG_PASSWORD=kong-user-password-32-chars-minimum
REDIS_READONLY_PASSWORD=readonly-user-password-32-chars-minimum
```

**Security Tip:** Generate strong passwords:

```bash
# Generate random passwords (Linux/Mac)
openssl rand -base64 32
```

### Step 2: Enable ACL in Configuration

Edit `infrastructure/redis/redis-secure.conf` and uncomment these lines:

```conf
# Line 56-72: Uncomment ACL user definitions

# Disable default user (line 54)
user default off nopass nocommands

# Application user (lines 56-62)
user sahool_app on >${REDIS_APP_PASSWORD} ~session:* ~cache:* +@read +@write +@string +@hash +@list +@set +@sorted-set +@pubsub -@admin -@dangerous -@scripting

# Kong Gateway user (line 64-66)
user kong_gateway on >${REDIS_KONG_PASSWORD} ~ratelimit:* +@read +@write -@admin -@dangerous

# Read-only user (lines 68-70)
user sahool_readonly on >${REDIS_READONLY_PASSWORD} ~* +@read +@connection +ping +info +client +cluster +config|get -@write -@admin -@dangerous

# Admin user (line 72)
user sahool_admin on >${REDIS_ADMIN_PASSWORD} ~* +@all
```

### Step 3: Restart Redis

```bash
docker-compose restart redis
```

### Step 4: Update Service Connection Strings

**Application Services:**

```bash
# Old (single password)
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0

# New (ACL user)
REDIS_URL=redis://sahool_app:${REDIS_APP_PASSWORD}@redis:6379/0
```

**Kong Gateway:**

```bash
# Update Kong configuration to use kong_gateway user
REDIS_URL=redis://kong_gateway:${REDIS_KONG_PASSWORD}@redis:6379/1
```

**Note:** Kong uses database 1 for rate limiting, applications use database 0.

### Step 5: Restart All Services

```bash
docker-compose restart
```

### Step 6: Verify ACL

```bash
# Test app user (should work)
redis-cli -h localhost -p 6379 \
  --user sahool_app --pass $REDIS_APP_PASSWORD \
  SET session:test value
# Expected: OK

# Test app user trying admin command (should fail)
redis-cli -h localhost -p 6379 \
  --user sahool_app --pass $REDIS_APP_PASSWORD \
  CONFIG GET maxmemory
# Expected: NOPERM error

# Test admin user (should work)
redis-cli -h localhost -p 6379 \
  --user sahool_admin --pass $REDIS_ADMIN_PASSWORD \
  CONFIG GET maxmemory
# Expected: maxmemory value
```

**✅ ACL is now enabled!**

---

## 4. Verify Security

### Security Checklist

```bash
# 1. Check authentication
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD PING
# Expected: PONG

# 2. Check TLS (if enabled)
redis-cli --tls --cacert config/redis/certs/ca.crt \
  -h localhost -p 6379 -a $REDIS_PASSWORD INFO server | grep redis_version
# Expected: redis_version:7.x.x

# 3. Check ACL (if enabled)
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD ACL LIST
# Expected: List of users (sahool_app, sahool_admin, etc.)

# 4. Check dangerous commands are renamed
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD FLUSHDB
# Expected: ERR unknown command

# 5. Check memory limits
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD CONFIG GET maxmemory
# Expected: maxmemory: 512000000 (512MB)

# 6. Check persistence
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD INFO persistence | grep aof_enabled
# Expected: aof_enabled:1

# 7. Check slow query logging
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SLOWLOG GET 1
# Expected: Slow query log entry (or empty if no slow queries)
```

---

## 5. Troubleshooting

### Redis Won't Start

```bash
# Check logs
docker logs sahool-redis

# Common issues:
# - Missing certificate files (if TLS enabled)
# - Syntax error in redis-secure.conf
# - Environment variables not set
```

**Fix:**

```bash
# Verify config file
docker exec sahool-redis redis-server --test-memory 1024

# Check environment variables
docker exec sahool-redis env | grep REDIS
```

### TLS Connection Fails

```bash
# Check certificates exist
ls -la config/redis/certs/
# Expected: server.crt, server.key, ca.crt

# Check certificate validity
openssl x509 -in config/redis/certs/server.crt -noout -dates
# Expected: notBefore and notAfter dates

# Verify certificate chain
openssl verify -CAfile config/redis/certs/ca.crt config/redis/certs/server.crt
# Expected: OK
```

**Fix:**

```bash
# Regenerate certificates
./scripts/generate-redis-certs.sh

# Restart Redis
docker-compose restart redis
```

### ACL Permission Denied

```bash
# Check ACL configuration
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD ACL LIST

# Check user exists
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD ACL GETUSER sahool_app

# Verify password
redis-cli -h localhost -p 6379 --user sahool_app --pass $REDIS_APP_PASSWORD PING
```

**Fix:**

```bash
# Verify .env file has ACL passwords
cat .env | grep REDIS_APP_PASSWORD

# Check config file has ACL users uncommented
grep "^user sahool_app" infrastructure/redis/redis-secure.conf

# Restart Redis
docker-compose restart redis
```

### Services Can't Connect

**Symptoms:**
- Connection timeout
- Authentication failed
- ERR unknown command

**Common Causes:**

1. **Wrong password:** Check `.env` file
2. **Wrong protocol:** Use `rediss://` for TLS, `redis://` without TLS
3. **Wrong user:** Use ACL username in connection string
4. **Network issue:** Check Docker network connectivity

**Fix:**

```bash
# Test from container
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD PING

# Test network connectivity
docker exec sahool-field-management-service ping redis

# Check connection string in service
docker exec sahool-field-management-service env | grep REDIS_URL
```

---

## Quick Command Reference

### Certificate Management

```bash
# Generate certificates
./scripts/generate-redis-certs.sh

# View certificate details
openssl x509 -in config/redis/certs/server.crt -noout -text

# Check expiration
openssl x509 -in config/redis/certs/server.crt -noout -dates
```

### ACL Management

```bash
# List all users
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD ACL LIST

# View user permissions
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD ACL GETUSER sahool_app

# Test user login
redis-cli --user sahool_app --pass $REDIS_APP_PASSWORD PING
```

### Monitoring

```bash
# Check memory usage
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD INFO memory

# View slow queries
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SLOWLOG GET 10

# Check client connections
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD CLIENT LIST

# Monitor commands in real-time
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD MONITOR
```

### High Availability (Sentinel)

```bash
# Check Sentinel master
docker exec sahool-redis-sentinel-1 redis-cli -p 26379 SENTINEL MASTER sahool-master

# Check replicas
docker exec sahool-redis-sentinel-1 redis-cli -p 26379 SENTINEL REPLICAS sahool-master

# Check Sentinels
docker exec sahool-redis-sentinel-1 redis-cli -p 26379 SENTINEL SENTINELS sahool-master
```

---

## Need Help?

**Documentation:**
- Full guide: `REDIS_SECURITY_HARDENING_SUMMARY.md`
- Audit report: `tests/database/REDIS_AUDIT.md`
- Security details: `infrastructure/redis/REDIS_SECURITY.md`
- TLS setup: `config/redis/REDIS_TLS_SETUP.md`

**Support:**
- DevOps Team: For general questions
- Security Team: For security-related issues
- Platform Architect: For architecture decisions

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-06

---

*End of Quick Start Guide*
