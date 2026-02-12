# SAHOOL Infrastructure Security Configuration Guide
# دليل إعداد أمان البنية التحتية لسهول

**Version**: 16.0.0  
**Last Updated**: 2026-02-11

---

## Quick Start

### 1. Generate Required Secrets

```bash
# Generate all required secrets at once
cat > .env.local <<EOF
# NATS Security
NATS_SYSTEM_PASSWORD=$(openssl rand -base64 32)
NATS_JETSTREAM_KEY=$(openssl rand -base64 32)

# Redis Password
REDIS_PASSWORD=$(openssl rand -base64 32)

# PostgreSQL Password
POSTGRES_PASSWORD=$(openssl rand -base64 32)

# JWT Secret Key
JWT_SECRET_KEY=$(openssl rand -base64 32)
EOF

# Copy to .env
cat .env.local >> .env
```

### 2. Validate Configuration

```bash
# Run automated validation
./scripts/validate-containers.sh

# Expected output: "✓ All critical checks passed!"
```

### 3. Start Infrastructure

```bash
# Start core infrastructure
make infra-up

# Or manually
docker compose up -d postgres pgbouncer redis nats kong

# Check health
docker compose ps
```

---

## Security Checklist

### Pre-Deployment

- [ ] **All passwords generated** (no default values)
- [ ] **JWT_SECRET_KEY** set (32+ characters)
- [ ] **NATS_JETSTREAM_KEY** generated with openssl
- [ ] **REDIS_PASSWORD** set
- [ ] **POSTGRES_PASSWORD** set
- [ ] **.env file** excluded from git (.gitignore)
- [ ] **Validation script** passes

### Development Environment

- [ ] Services bound to localhost (127.0.0.1)
- [ ] TLS can be disabled for local testing
- [ ] Health checks enabled
- [ ] Logging configured

### Production Environment

- [ ] **TLS/SSL enabled** for all services
- [ ] **Certificates** generated and mounted
- [ ] **Firewall rules** configured
- [ ] **Monitoring** enabled (Prometheus/Grafana)
- [ ] **Backup strategy** implemented
- [ ] **Secrets management** (Vault/K8s secrets)

---

## Service-Specific Configuration

### Kong API Gateway

**Security Settings:**
```yaml
# Admin API - MUST be localhost only
KONG_ADMIN_LISTEN: 127.0.0.1:8001

# Production: Enable HTTPS
KONG_PROXY_LISTEN: "0.0.0.0:8000, 0.0.0.0:8443 ssl"
KONG_SSL_CERT: /etc/kong/ssl/server.crt
KONG_SSL_CERT_KEY: /etc/kong/ssl/server.key

# DNS resilience
KONG_DNS_NO_SYNC: "on"
KONG_DNS_CACHE_TTL: 300
```

**Certificate Setup:**
```bash
# Generate self-signed cert (development)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout infrastructure/gateway/kong/ssl/server.key \
  -out infrastructure/gateway/kong/ssl/server.crt \
  -days 365 \
  -subj "/CN=kong.sahool.local"

# Production: Use Let's Encrypt or corporate CA
```

**Access Control:**
- Admin API: localhost only (127.0.0.1:8001)
- Proxy: Public (8000, 8443)
- Rate limiting: Enabled via Kong plugins
- JWT authentication: Required for protected routes

---

### PostgreSQL + PgBouncer

**Security Settings:**
```yaml
# PostgreSQL
POSTGRES_PASSWORD: <generated-32-char-password>
# TLS in production (pgbouncer.ini):
# server_tls_sslmode = require
# client_tls_sslmode = require
```

**Connection Pooling:**
- Max DB connections: 250
- Default pool size: 30
- Transaction mode for safety
- Persistent userlist.txt (volume-backed)

**TLS Configuration:**
```ini
# infrastructure/core/pgbouncer/pgbouncer.ini
[databases]
sahool = host=postgres port=5432 dbname=sahool

[pgbouncer]
# Production TLS settings
server_tls_sslmode = require
server_tls_protocols = secure
server_tls_ciphers = HIGH:!aNULL:!MD5
client_tls_sslmode = require
client_tls_cert_file = /etc/pgbouncer/certs/client.crt
client_tls_key_file = /etc/pgbouncer/certs/client.key
client_tls_ca_file = /etc/pgbouncer/certs/ca.crt
```

**Access Control:**
- Port 5432: localhost only (127.0.0.1)
- Port 6432 (PgBouncer): localhost only (127.0.0.1)
- Services access via Docker network
- SCRAM-SHA-256 authentication

---

### Redis

**Security Settings:**
```yaml
# Authentication
REDIS_PASSWORD: <generated-32-char-password>

# Memory limits
REDIS_MAXMEMORY: 512mb

# ACL users (optional but recommended)
REDIS_APP_PASSWORD: <app-user-password>
REDIS_ADMIN_PASSWORD: <admin-user-password>
REDIS_KONG_PASSWORD: <kong-user-password>
```

**TLS Configuration:**
```bash
# Generate Redis TLS certificates
cd config/certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout redis-server.key \
  -out redis-server.crt \
  -days 365 \
  -subj "/CN=redis.sahool.local"

# Enable TLS in docker-compose.yml (uncomment):
# --port 0
# --tls-port 6379
# --tls-cert-file /etc/redis/certs/server.crt
# --tls-key-file /etc/redis/certs/server.key
```

**ACL Setup (Advanced):**
```bash
# Create ACL users
docker compose exec redis redis-cli -a "$REDIS_PASSWORD" <<EOF
ACL SETUSER app_user on >$REDIS_APP_PASSWORD ~* +@all
ACL SETUSER admin_user on >$REDIS_ADMIN_PASSWORD ~* +@all
ACL SETUSER kong_user on >$REDIS_KONG_PASSWORD ~* +@read +@write
ACL SETUSER readonly_user on >$REDIS_READONLY_PASSWORD ~* +@read
ACL SAVE
EOF
```

**Dangerous Commands:**
- FLUSHDB → Disabled (renamed)
- FLUSHALL → Disabled (renamed)
- CONFIG → Restricted
- SAVE → Restricted

---

### NATS

**Security Settings:**
```yaml
# User Authentication
NATS_USER: sahool_app
NATS_PASSWORD: <generated-32-char-password>

# Admin User
NATS_ADMIN_USER: nats_admin
NATS_ADMIN_PASSWORD: <generated-32-char-password>

# Monitoring User
NATS_MONITOR_USER: nats_monitor
NATS_MONITOR_PASSWORD: <generated-32-char-password>

# Cluster User (multi-node)
NATS_CLUSTER_USER: nats_cluster
NATS_CLUSTER_PASSWORD: <generated-32-char-password>

# System Account (REQUIRED)
NATS_SYSTEM_USER: nats_system
NATS_SYSTEM_PASSWORD: <generated-32-char-password>

# JetStream Encryption (REQUIRED - AES-256)
NATS_JETSTREAM_KEY: <generated-32-byte-key>
```

**TLS Configuration:**
```bash
# Generate NATS TLS certificates
cd config/certs
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout nats-server.key \
  -out nats-server.crt \
  -days 365 \
  -subj "/CN=nats.sahool.local"

# Enable TLS in config/nats/nats-secure.conf
```

**Access Control:**
- Port 4222: Non-TLS (development only)
- Port 4223: TLS (production)
- Port 8222: Monitoring (localhost only)
- Port 6222: Cluster (internal network)

**JetStream Encryption:**
- At-rest encryption: Enabled with NATS_JETSTREAM_KEY
- In-transit encryption: TLS on port 4223
- Key rotation: Manual (update key and restart)

---

### User Service

**Security Settings:**
```yaml
# Service binding
ports:
  - "127.0.0.1:3025:3025"  # localhost only

# JWT Configuration
JWT_SECRET_KEY: <generated-32-char-password>
JWT_ALGORITHM: HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES: 30
JWT_REFRESH_TOKEN_EXPIRE_DAYS: 7

# CORS (restrict in production)
CORS_ALLOWED_ORIGINS: https://sahool.com,https://app.sahool.com,https://admin.sahool.com
```

**Access Control:**
- Direct access: Blocked (localhost only)
- Public access: Via Kong API Gateway only
- Authentication: JWT required
- Rate limiting: Enforced by Kong

---

## Certificate Management

### Development (Self-Signed)

```bash
# Create certificates directory
mkdir -p config/certs

# Generate CA certificate
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout config/certs/ca.key \
  -out config/certs/ca.crt \
  -days 3650 \
  -subj "/CN=SAHOOL Development CA"

# Generate service certificates (example: NATS)
openssl req -new -newkey rsa:4096 -nodes \
  -keyout config/certs/nats-server.key \
  -out config/certs/nats-server.csr \
  -subj "/CN=nats.sahool.local"

openssl x509 -req -in config/certs/nats-server.csr \
  -CA config/certs/ca.crt \
  -CAkey config/certs/ca.key \
  -CAcreateserial \
  -out config/certs/nats-server.crt \
  -days 365

# Set permissions
chmod 600 config/certs/*.key
chmod 644 config/certs/*.crt
```

### Production (Let's Encrypt)

```bash
# Use Certbot for Let's Encrypt
certbot certonly --standalone -d api.sahool.com

# Copy to config/certs
cp /etc/letsencrypt/live/api.sahool.com/fullchain.pem config/certs/server.crt
cp /etc/letsencrypt/live/api.sahool.com/privkey.pem config/certs/server.key
```

---

## Environment Variable Reference

### Required Variables

| Variable | Service | Example | Required |
|----------|---------|---------|----------|
| POSTGRES_PASSWORD | PostgreSQL | 32+ chars | ✅ Yes |
| REDIS_PASSWORD | Redis | 32+ chars | ✅ Yes |
| NATS_USER | NATS | sahool_app | ✅ Yes |
| NATS_PASSWORD | NATS | 32+ chars | ✅ Yes |
| NATS_ADMIN_PASSWORD | NATS | 32+ chars | ✅ Yes |
| NATS_MONITOR_PASSWORD | NATS | 32+ chars | ✅ Yes |
| NATS_CLUSTER_PASSWORD | NATS | 32+ chars | ✅ Yes |
| NATS_SYSTEM_USER | NATS | nats_system | ✅ Yes |
| NATS_SYSTEM_PASSWORD | NATS | 32+ chars | ✅ Yes |
| NATS_JETSTREAM_KEY | NATS | 32 bytes | ✅ Yes |
| JWT_SECRET_KEY | All services | 32+ chars | ✅ Yes |

### Optional but Recommended

| Variable | Service | Default | Recommended |
|----------|---------|---------|-------------|
| REDIS_APP_PASSWORD | Redis | REDIS_PASSWORD | Unique per service |
| REDIS_ADMIN_PASSWORD | Redis | REDIS_PASSWORD | Separate admin password |
| REDIS_KONG_PASSWORD | Redis | REDIS_PASSWORD | Kong-specific password |
| KONG_SSL_CERT | Kong | None | Production cert path |
| KONG_SSL_CERT_KEY | Kong | None | Production key path |

---

## Monitoring & Health Checks

### Health Check Endpoints

```bash
# Kong
curl http://localhost:8001/status

# PostgreSQL (via PgBouncer)
psql -h localhost -p 6432 -U sahool -d sahool -c "SELECT 1"

# Redis
redis-cli -a "$REDIS_PASSWORD" ping

# NATS
curl http://localhost:8222/healthz

# User Service
curl http://localhost:3025/api/v1/health
```

### Monitoring Metrics

```bash
# Start monitoring stack
make monitoring-up

# Access Grafana
open http://localhost:3001  # Default: admin/admin

# Prometheus
open http://localhost:9090
```

**Available Metrics:**
- Kong: http://localhost:8001/metrics
- Redis: redis_exporter on port 9121
- NATS: http://localhost:7777/metrics
- PostgreSQL: postgres_exporter on port 9187

---

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker compose logs -f [service-name]

# Common issues:
# 1. Missing environment variables → Check .env file
# 2. Port conflicts → Change port bindings
# 3. Permission denied → Check volume permissions
# 4. Health check failing → Increase start_period
```

### Authentication Failures

```bash
# PgBouncer userlist.txt not found
docker compose exec pgbouncer cat /etc/pgbouncer/runtime/userlist.txt

# Redis password incorrect
docker compose exec redis redis-cli -a "$REDIS_PASSWORD" ping

# NATS authentication failed
docker compose exec nats nats account info
```

### Performance Issues

```bash
# Check resource usage
docker stats

# PgBouncer pool exhaustion
docker compose exec pgbouncer psql -p 6432 -U pgbouncer pgbouncer -c "SHOW POOLS"

# Redis memory usage
docker compose exec redis redis-cli -a "$REDIS_PASSWORD" info memory
```

---

## Security Best Practices

### DO ✅

- Use strong passwords (32+ characters)
- Enable TLS for all services in production
- Bind services to localhost unless public access needed
- Use environment variables for secrets
- Rotate credentials regularly
- Monitor logs for suspicious activity
- Keep Docker images updated
- Use read-only volumes where possible
- Enable health checks
- Set resource limits

### DON'T ❌

- Commit .env files to git
- Use default passwords
- Expose admin APIs publicly
- Disable TLS in production
- Run containers as root
- Use `--privileged` flag
- Share credentials between environments
- Ignore security warnings
- Skip updates
- Disable logging

---

## Compliance & Audit

### Logging

All services log to stdout/stderr for Docker log aggregation:

```bash
# View all logs
docker compose logs -f

# Service-specific logs
docker compose logs -f kong pgbouncer redis nats

# Save logs to file
docker compose logs > logs/infrastructure-$(date +%Y%m%d).log
```

### Audit Trail

- Kong: Access logs via KONG_PROXY_ACCESS_LOG
- PostgreSQL: Via PgBouncer logging
- Redis: Slow query log enabled
- NATS: Audit via system account

---

## Migration Guide

### From Development to Production

1. **Generate Production Secrets:**
   ```bash
   # Save to secure location (e.g., Vault)
   ./scripts/generate-production-secrets.sh > .env.production.secret
   ```

2. **Enable TLS:**
   - Uncomment TLS settings in docker-compose.yml
   - Add production certificates to config/certs/
   - Update service URLs to use TLS ports

3. **Update Firewall Rules:**
   - Block direct access to services
   - Allow Kong proxy (8000, 8443)
   - Allow monitoring (9090, 3001)

4. **Configure Backups:**
   - PostgreSQL: WAL-G or pg_dump
   - Redis: AOF + RDB snapshots
   - NATS: JetStream snapshots

5. **Enable Monitoring:**
   - Prometheus metrics collection
   - Grafana dashboards
   - Alertmanager for critical alerts

---

## Support & Resources

- **Documentation**: `/docs/`
- **Validation Script**: `./scripts/validate-containers.sh`
- **Makefile Commands**: `make help`
- **Issue Tracker**: GitHub Issues
- **Security Policy**: `SECURITY.md`

---

**Last Updated**: 2026-02-11  
**Status**: ✅ Production Ready  
**Validated By**: Automated validation + Manual security review
