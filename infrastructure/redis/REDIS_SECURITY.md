# Redis Security Implementation - SAHOOL Platform

# تنفيذ أمان Redis - منصة سهول

## Overview | نظرة عامة

This document describes the comprehensive security measures implemented for Redis in the SAHOOL agricultural platform.

يوضح هذا المستند تدابير الأمان الشاملة المطبقة على Redis في منصة سهول الزراعية.

## Security Features | ميزات الأمان

### 1. Authentication | المصادقة

**Password Protection:**

- All Redis connections require password authentication via `REDIS_PASSWORD`
- Password is stored in environment variables, not in configuration files
- All services use authenticated connection strings: `redis://:${REDIS_PASSWORD}@redis:6379/0`

**حماية كلمة المرور:**

- جميع اتصالات Redis تتطلب مصادقة كلمة المرور عبر `REDIS_PASSWORD`
- يتم تخزين كلمة المرور في متغيرات البيئة، وليس في ملفات التكوين
- جميع الخدمات تستخدم سلاسل الاتصال المصادق عليها

```bash
# Generate a strong password
openssl rand -base64 32
```

### 2. Command Security | أمان الأوامر

**Dangerous Commands Renamed:**

To prevent accidental or malicious execution, the following commands have been renamed:

| Original Command | Renamed To                           | Purpose                             |
| ---------------- | ------------------------------------ | ----------------------------------- |
| `FLUSHDB`        | `SAHOOL_FLUSHDB_DANGER_f5a8d2e9`     | Delete all keys in current database |
| `FLUSHALL`       | `SAHOOL_FLUSHALL_DANGER_b3c7f1a4`    | Delete all keys in all databases    |
| `CONFIG`         | `SAHOOL_CONFIG_ADMIN_c8e2d4f6`       | Modify configuration at runtime     |
| `DEBUG`          | `""` (disabled)                      | Debugging commands                  |
| `SHUTDOWN`       | `SAHOOL_SHUTDOWN_ADMIN_a9f3e7b1`     | Shutdown server                     |
| `BGSAVE`         | `SAHOOL_BGSAVE_ADMIN_d4b8f2c5`       | Background save                     |
| `BGREWRITEAOF`   | `SAHOOL_BGREWRITEAOF_ADMIN_e7c3a9f2` | Background AOF rewrite              |
| `KEYS`           | `SAHOOL_KEYS_SCAN_ONLY_f8d3b7e2`     | List keys (use SCAN instead)        |

**Usage Example:**

```bash
# To use renamed command (admin only)
redis-cli -a $REDIS_PASSWORD SAHOOL_CONFIG_ADMIN_c8e2d4f6 GET maxmemory
```

### 3. Network Security | أمان الشبكة

**Docker Network Isolation:**

- Redis runs in isolated Docker network (`sahool-network`)
- Port 6379 bound to `127.0.0.1` only (localhost) for host access
- Services access Redis via Docker internal DNS (`redis:6379`)

**Protected Mode:**

- Enabled to require authentication even within Docker network
- Prevents unauthorized access from other containers

**Connection Limits:**

- Maximum 10,000 concurrent clients
- Connection timeout: 300 seconds (5 minutes)
- TCP keepalive: 60 seconds

### 4. Data Persistence | ثبات البيانات

**AOF (Append Only File):**

- Primary persistence method
- `appendfsync everysec` - fsync every second (good balance)
- Auto-rewrite when file grows 100% and is at least 64MB
- Loaded on startup with truncated file recovery

**RDB Snapshots:**

- Secondary backup method
- Saves after: 15min (1 change), 5min (10 changes), 1min (10K changes)
- Compressed and checksummed
- Stored in `/data` volume

**Data Directory:**

```bash
/data
├── sahool-appendonly.aof  # AOF file
└── sahool-dump.rdb         # RDB snapshot
```

### 5. Memory Management | إدارة الذاكرة

**Memory Limits:**

- Maximum memory: 512MB (configurable)
- Container memory limit: 768MB (includes Redis overhead)
- Container memory reservation: 256MB

**Eviction Policy:**

- `allkeys-lru`: Removes least recently used keys when memory full
- Alternative policies available: `volatile-lru`, `noeviction`, etc.

**Memory Monitoring:**

```bash
# Check memory usage
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD INFO memory

# Check eviction statistics
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD INFO stats | grep evicted
```

### 6. Performance Monitoring | مراقبة الأداء

**Slow Query Log:**

- Logs queries taking > 10ms
- Keeps last 128 slow queries
- View with: `SLOWLOG GET 10`

**Latency Monitoring:**

- Monitors events taking > 100ms
- View with: `LATENCY LATEST`

**Monitoring Commands:**

```bash
# View slow queries
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SLOWLOG GET 10

# View latency events
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD LATENCY LATEST

# Monitor real-time commands
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD MONITOR

# Get server info
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD INFO
```

### 7. Resource Limits | حدود الموارد

**CPU Limits:**

- Maximum: 1 CPU core
- Reserved: 0.25 CPU cores

**Memory Limits:**

- Maximum: 768MB (container)
- Redis maxmemory: 512MB
- Reserved: 256MB

**Client Buffer Limits:**

- Normal clients: unlimited
- Replica clients: 256MB hard, 64MB soft
- Pub/Sub clients: 32MB hard, 8MB soft

## Configuration Files | ملفات التكوين

### Main Configuration

**Location:** `/home/user/sahool-unified-v15-idp/infrastructure/redis/redis-docker.conf`

This file contains all Redis security and performance settings optimized for Docker.

### Docker Compose

**Location:** `/home/user/sahool-unified-v15-idp/docker-compose.yml`

Redis service definition with volume mounts and security options.

### Environment Variables

**Location:** `/home/user/sahool-unified-v15-idp/.env`

```bash
# Required
REDIS_PASSWORD=your_secure_password_here

# Optional (defaults shown)
REDIS_MAXMEMORY=512mb
```

## Service Integration | تكامل الخدمات

All SAHOOL services connect to Redis using the following pattern:

```bash
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
```

**Services using Redis:**

1. Field Management Service (port 3000)
2. Marketplace Service (port 3010)
3. Research Core (port 3015)
4. Disaster Assessment (port 3020)
5. Yield Prediction (port 3021)
6. LAI Estimation (port 3022)
7. Crop Growth Model (port 3023)
8. Chat Service (port 8114)
9. IoT Service (port 8117)
10. Community Chat (port 8097)
11. Field Operations (port 8080)
12. WebSocket Gateway (port 8081)
13. Billing Core (port 8089)
14. Vegetation Analysis (port 8090)
15. Field Chat (port 8099)
16. Agent Registry (port 8107)
17. Farm AI Assistant (port 8109)
18. Kong API Gateway (for rate limiting)

## Kong Rate Limiting | تحديد معدل Kong

Kong uses Redis for distributed rate limiting:

**Configuration in kong.yml:**

```yaml
plugins:
  - name: rate-limiting
    config:
      policy: redis
      redis_host: redis
      redis_port: 6379
      redis_password: ${REDIS_PASSWORD}
      redis_database: 1
      redis_timeout: 2000
      fault_tolerant: true
```

**Database Allocation:**

- Database 0: Application data (sessions, cache)
- Database 1: Kong rate limiting
- Databases 2-15: Available for future use

## Health Checks | فحوصات الصحة

**Health Check Command:**

```bash
redis-cli -a ${REDIS_PASSWORD} ping | grep PONG
```

**Health Check Schedule:**

- Interval: 10 seconds
- Timeout: 5 seconds
- Retries: 5
- Start period: 10 seconds

**Manual Health Check:**

```bash
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD PING
# Expected output: PONG

docker exec sahool-redis redis-cli -a $REDIS_PASSWORD INFO server
```

## Backup and Recovery | النسخ الاحتياطي والاسترداد

### Manual Backup

**Create RDB Snapshot:**

```bash
# Using renamed command
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SAHOOL_BGSAVE_ADMIN_d4b8f2c5
```

**Backup Files:**

```bash
# Copy RDB snapshot
docker cp sahool-redis:/data/sahool-dump.rdb ./backup/

# Copy AOF file
docker cp sahool-redis:/data/sahool-appendonly.aof ./backup/
```

### Automated Backup

Use the backup script in `/home/user/sahool-unified-v15-idp/scripts/backup/backup_redis.sh`

### Recovery

**Restore from Backup:**

```bash
# Stop Redis
docker-compose stop redis

# Copy backup files to volume
docker cp ./backup/sahool-dump.rdb sahool-redis:/data/
docker cp ./backup/sahool-appendonly.aof sahool-redis:/data/

# Start Redis
docker-compose start redis
```

## Maintenance Commands | أوامر الصيانة

### Clear All Data (USE WITH CAUTION!)

```bash
# Using renamed command
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SAHOOL_FLUSHALL_DANGER_b3c7f1a4
```

### Clear Current Database

```bash
# Using renamed command
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SAHOOL_FLUSHDB_DANGER_f5a8d2e9
```

### View All Keys (Use SCAN in Production)

```bash
# Development only - use SCAN in production
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SAHOOL_KEYS_SCAN_ONLY_f8d3b7e2 '*'

# Production-safe way to list keys
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SCAN 0 COUNT 100
```

### Rewrite AOF

```bash
# Using renamed command
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SAHOOL_BGREWRITEAOF_ADMIN_e7c3a9f2
```

## Security Best Practices | أفضل ممارسات الأمان

### 1. Password Management

- ✅ Use strong passwords (minimum 32 characters)
- ✅ Generate with: `openssl rand -base64 32`
- ✅ Store in `.env` file (never commit to Git)
- ✅ Rotate passwords periodically
- ❌ Never hardcode passwords in application code

### 2. Network Security

- ✅ Keep Redis in Docker network only
- ✅ Bind to localhost for host access
- ✅ Use firewall rules to restrict access
- ❌ Never expose Redis to public internet

### 3. Command Security

- ✅ Use renamed commands for administrative tasks
- ✅ Use SCAN instead of KEYS in production
- ✅ Limit administrative access
- ❌ Don't share renamed command names publicly

### 4. Monitoring

- ✅ Monitor slow queries regularly
- ✅ Set up alerts for memory usage
- ✅ Track eviction metrics
- ✅ Monitor connection counts

### 5. Backup

- ✅ Regular automated backups
- ✅ Test restore procedures
- ✅ Store backups securely
- ✅ Maintain multiple backup generations

## Troubleshooting | استكشاف الأخطاء وإصلاحها

### Connection Refused

```bash
# Check if Redis is running
docker ps | grep redis

# Check logs
docker logs sahool-redis

# Test connection
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD PING
```

### Authentication Errors

```bash
# Verify password is set
echo $REDIS_PASSWORD

# Test authentication
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD AUTH $REDIS_PASSWORD
```

### Memory Issues

```bash
# Check memory usage
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD INFO memory

# Check eviction policy
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD CONFIG GET maxmemory-policy

# Clear specific database
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SELECT 1
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SAHOOL_FLUSHDB_DANGER_f5a8d2e9
```

### Performance Issues

```bash
# Check slow queries
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD SLOWLOG GET 20

# Check latency
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD LATENCY LATEST

# Check command statistics
docker exec sahool-redis redis-cli -a $REDIS_PASSWORD INFO commandstats
```

## Future Enhancements | التحسينات المستقبلية

### TLS/SSL Encryption

To enable TLS for Redis connections, uncomment the TLS section in `redis-docker.conf` and configure certificates.

### Redis Sentinel (High Availability)

For production deployments requiring high availability, implement Redis Sentinel for automatic failover.

### Redis Cluster (Scalability)

For horizontal scaling, implement Redis Cluster with multiple shards.

### ACL (Access Control Lists)

Redis 6+ supports fine-grained ACLs. Configure different users for different services with specific permissions.

## References | المراجع

- [Redis Security Documentation](https://redis.io/docs/management/security/)
- [Redis Persistence](https://redis.io/docs/management/persistence/)
- [Redis Best Practices](https://redis.io/docs/manual/patterns/)
- [Docker Redis Security](https://hub.docker.com/_/redis)

---

**Last Updated:** 2026-01-06
**Author:** SAHOOL DevOps Team
**Version:** 1.0.0
