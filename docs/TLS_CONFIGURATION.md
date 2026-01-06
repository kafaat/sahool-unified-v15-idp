# SAHOOL Platform - TLS/SSL Configuration Guide

## Overview

The SAHOOL platform uses TLS/SSL encryption to secure all internal service communication. This guide provides comprehensive information about the TLS setup, configuration, and management.

## Architecture

### TLS Implementation

```
┌─────────────────────────────────────────────────────────────────┐
│                     SAHOOL Internal CA                           │
│                    (Self-Signed Root CA)                         │
│                   Valid for 10 years                             │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─── Signs ──→ PostgreSQL Certificate (825 days)
             ├─── Signs ──→ PgBouncer Certificate (825 days)
             ├─── Signs ──→ Redis Certificate (825 days)
             ├─── Signs ──→ NATS Certificate (825 days)
             └─── Signs ──→ Kong Certificate (825 days)
```

### Service Communication

```
┌──────────────┐                    ┌──────────────┐
│   Services   │ ─── TLS 1.2+ ────→ │  PostgreSQL  │
│  (Node.js/   │                    │   (Port 5432)│
│   Python)    │ ←── Encrypted ──── │   SSL ON     │
└──────────────┘                    └──────────────┘
       │
       │ TLS 1.2+
       ↓
┌──────────────┐                    ┌──────────────┐
│   PgBouncer  │ ─── TLS 1.2+ ────→ │  PostgreSQL  │
│  (Port 6432) │                    │              │
└──────────────┘                    └──────────────┘

┌──────────────┐                    ┌──────────────┐
│   Services   │ ─── TLS 1.2+ ────→ │    Redis     │
│              │                    │  (TLS Port   │
│              │ ←── Encrypted ──── │   6379)      │
└──────────────┘                    └──────────────┘

┌──────────────┐                    ┌──────────────┐
│   Services   │ ─── TLS 1.2+ ────→ │    NATS      │
│              │                    │  (Port 4222) │
│              │ ←── Encrypted ──── │   TLS ON     │
└──────────────┘                    └──────────────┘

┌──────────────┐                    ┌──────────────┐
│   Clients    │ ─── HTTPS ───────→ │    Kong      │
│              │                    │ (Port 8443)  │
│              │ ←── Encrypted ──── │   SSL ON     │
└──────────────┘                    └──────────────┘
```

## Certificate Infrastructure

### Certificate Authority (CA)

**Location**: `/home/user/sahool-unified-v15-idp/config/certs/ca/`

- **Certificate**: `ca.crt` (Public, can be distributed)
- **Private Key**: `ca.key` (SECRET - never commit or share)
- **Validity**: 10 years
- **Key Size**: 4096 bits RSA
- **Signature**: SHA-256

**Subject DN**:
```
C=YE, ST=Sana'a, L=Sana'a, O=SAHOOL, OU=Platform Security, CN=SAHOOL Internal CA
```

### Service Certificates

Each service has its own certificate with Subject Alternative Names (SANs):

| Service | Location | SANs |
|---------|----------|------|
| PostgreSQL | `/config/certs/postgres/` | postgres, postgres.sahool.local, sahool-postgres, localhost |
| PgBouncer | `/config/certs/pgbouncer/` | pgbouncer, pgbouncer.sahool.local, sahool-pgbouncer, localhost |
| Redis | `/config/certs/redis/` | redis, redis.sahool.local, sahool-redis, localhost |
| NATS | `/config/certs/nats/` | nats, nats.sahool.local, sahool-nats, localhost |
| Kong | `/config/certs/kong/` | kong, kong.sahool.local, sahool-kong, localhost |

**Certificate Properties**:
- **Validity**: 825 days (~2.25 years, Apple's maximum)
- **Key Size**: 2048 bits RSA
- **Signature**: SHA-256
- **Key Usage**: Digital Signature, Key Encipherment
- **Extended Key Usage**: Server Authentication, Client Authentication

## Service Configuration

### PostgreSQL

**Configuration File**: Configured via command-line arguments in `docker-compose.tls.yml`

**TLS Settings**:
```bash
ssl=on
ssl_cert_file=/var/lib/postgresql/certs/server.crt
ssl_key_file=/var/lib/postgresql/certs/server.key
ssl_ca_file=/var/lib/postgresql/certs/ca.crt
ssl_min_protocol_version=TLSv1.2
ssl_prefer_server_ciphers=on
```

**Client Connection**:
```bash
# Connection string with TLS
postgresql://user:pass@postgres:5432/db?sslmode=prefer

# Environment variables
PGSSLMODE=prefer
PGSSLROOTCERT=/path/to/ca.crt
```

**SSL Modes**:
- `disable`: No SSL (not recommended)
- `allow`: Try non-SSL first, then SSL
- `prefer`: Try SSL first, then non-SSL (default with TLS enabled)
- `require`: Require SSL (don't verify certificate)
- `verify-ca`: Require SSL and verify server certificate
- `verify-full`: Require SSL and verify hostname

### PgBouncer

**Configuration File**: `/home/user/sahool-unified-v15-idp/infrastructure/core/pgbouncer/pgbouncer.ini`

**TLS Settings**:
```ini
# Server-side TLS (to PostgreSQL)
server_tls_sslmode = prefer
server_tls_ca_file = /etc/pgbouncer/certs/ca.crt

# Client-side TLS (from applications)
client_tls_sslmode = prefer
client_tls_cert_file = /etc/pgbouncer/certs/server.crt
client_tls_key_file = /etc/pgbouncer/certs/server.key
```

### Redis

**Configuration**: Command-line arguments in `docker-compose.tls.yml`

**TLS Settings**:
```bash
--tls-port 6379
--port 0                              # Disable non-TLS port
--tls-cert-file /etc/redis/certs/server.crt
--tls-key-file /etc/redis/certs/server.key
--tls-ca-cert-file /etc/redis/certs/ca.crt
--tls-auth-clients optional           # Allow both TLS and non-TLS clients initially
--tls-protocols "TLSv1.2 TLSv1.3"
--tls-prefer-server-ciphers yes
--tls-session-caching yes
```

**Client Connection**:
```bash
# Connection string with TLS
rediss://:password@redis:6379/0

# Python example
redis.Redis(host='redis', port=6379, password='pass', ssl=True, ssl_ca_certs='/path/to/ca.crt')
```

### NATS

**Configuration File**: `/home/user/sahool-unified-v15-idp/config/nats/nats.conf`

**TLS Settings**:
```conf
tls {
    cert_file: "/etc/nats/certs/server.crt"
    key_file: "/etc/nats/certs/server.key"
    ca_file: "/etc/nats/certs/ca.crt"
    verify: true
    timeout: 2
}
```

**Client Connection**:
```bash
# Connection string with TLS
nats://user:pass@nats:4222?tls=true&tls_ca=/path/to/ca.crt
```

### Kong

**Configuration**: Environment variables in `docker-compose.tls.yml`

**TLS Settings**:
```yaml
KONG_PROXY_LISTEN: "0.0.0.0:8000, 0.0.0.0:8443 ssl"
KONG_SSL_CERT: /etc/kong/certs/server.crt
KONG_SSL_CERT_KEY: /etc/kong/certs/server.key
```

**Access**:
```bash
# HTTPS access
curl https://kong:8443/api/v1/health

# Admin API (localhost only, no TLS required)
curl http://localhost:8001/status
```

## Deployment

### Standard Deployment (No TLS)

```bash
docker-compose up -d
```

### TLS-Enabled Deployment

```bash
# Method 1: Command line
docker-compose -f docker-compose.yml -f docker-compose.tls.yml up -d

# Method 2: Environment variable (add to .env)
echo "COMPOSE_FILE=docker-compose.yml:docker-compose.tls.yml" >> .env
docker-compose up -d
```

### Certificate Generation Before First Run

```bash
# Navigate to certs directory
cd /home/user/sahool-unified-v15-idp/config/certs

# Generate all certificates
./generate-internal-tls.sh

# Verify certificates
./generate-internal-tls.sh --verify
```

## Application Integration

### Environment Variables

Add to your service `.env` or docker-compose environment:

```bash
# PostgreSQL
DATABASE_URL=postgresql://user:pass@postgres:5432/db?sslmode=prefer
PGSSLMODE=prefer
PGSSLROOTCERT=/app/certs/ca.crt

# Redis
REDIS_URL=rediss://:password@redis:6379/0
REDIS_TLS_ENABLED=true
REDIS_TLS_CA_CERTS=/app/certs/ca.crt

# NATS
NATS_URL=nats://user:pass@nats:4222?tls=true
NATS_TLS_ENABLED=true
NATS_TLS_CA=/app/certs/ca.crt
```

### Code Examples

#### Python - PostgreSQL with asyncpg

```python
import asyncpg
import ssl

# Create SSL context
ssl_context = ssl.create_default_context(cafile='/app/certs/ca.crt')

# Connect with TLS
conn = await asyncpg.connect(
    host='postgres',
    port=5432,
    user='sahool',
    password='password',
    database='sahool',
    ssl=ssl_context
)
```

#### Python - Redis with redis-py

```python
import redis
import ssl

# Create SSL context
ssl_context = ssl.create_default_context(cafile='/app/certs/ca.crt')

# Connect with TLS
client = redis.Redis(
    host='redis',
    port=6379,
    password='password',
    ssl=True,
    ssl_cert_reqs=ssl.CERT_REQUIRED,
    ssl_ca_certs='/app/certs/ca.crt'
)
```

#### Node.js - PostgreSQL with pg

```javascript
const { Pool } = require('pg');
const fs = require('fs');

const pool = new Pool({
  host: 'postgres',
  port: 5432,
  database: 'sahool',
  user: 'sahool',
  password: 'password',
  ssl: {
    rejectUnauthorized: true,
    ca: fs.readFileSync('/app/certs/ca.crt').toString()
  }
});
```

#### Node.js - Redis with ioredis

```javascript
const Redis = require('ioredis');
const fs = require('fs');

const redis = new Redis({
  host: 'redis',
  port: 6379,
  password: 'password',
  tls: {
    ca: fs.readFileSync('/app/certs/ca.crt')
  }
});
```

## Monitoring & Maintenance

### Certificate Expiration Monitoring

```bash
# Check all certificate expiration dates
cd /home/user/sahool-unified-v15-idp/config/certs

for service in postgres pgbouncer redis nats kong; do
  echo "=== $service ==="
  openssl x509 -in "$service/server.crt" -noout -dates
  echo ""
done
```

### Automated Monitoring Script

```bash
#!/bin/bash
# monitor-certs.sh

WARN_DAYS=30
CERT_DIR="/home/user/sahool-unified-v15-idp/config/certs"

for cert in $CERT_DIR/*/server.crt; do
  service=$(basename $(dirname $cert))
  expiry=$(openssl x509 -in "$cert" -noout -enddate | cut -d= -f2)
  expiry_epoch=$(date -d "$expiry" +%s)
  now_epoch=$(date +%s)
  days_left=$(( ($expiry_epoch - $now_epoch) / 86400 ))

  if [ $days_left -lt $WARN_DAYS ]; then
    echo "⚠️  WARNING: $service certificate expires in $days_left days!"
  else
    echo "✓ $service certificate valid for $days_left more days"
  fi
done
```

### Health Check Endpoints

Monitor TLS connectivity:

```bash
# PostgreSQL
docker-compose exec postgres psql -U sahool -c "SHOW ssl;"

# Redis
docker-compose exec redis redis-cli INFO server | grep ssl

# NATS
curl http://localhost:8222/varz | jq '.tls'

# Kong
curl -k https://localhost:8443/
```

## Troubleshooting

### Common Issues

#### 1. Certificate Verification Failed

**Error**: `SSL error: certificate verify failed`

**Causes**:
- CA certificate not provided to client
- Certificate expired
- Hostname mismatch

**Solutions**:
```bash
# Verify certificate is valid
openssl verify -CAfile config/certs/ca/ca.crt config/certs/postgres/server.crt

# Check expiration
openssl x509 -in config/certs/postgres/server.crt -noout -dates

# Regenerate if needed
cd config/certs && ./generate-internal-tls.sh --force
```

#### 2. Connection Refused

**Error**: `Connection refused` or `Connection reset by peer`

**Causes**:
- Service not configured for TLS
- Wrong port
- Firewall blocking TLS port

**Solutions**:
```bash
# Check service logs
docker-compose logs postgres | grep -i ssl
docker-compose logs redis | grep -i tls

# Verify TLS is enabled
docker-compose exec postgres psql -U sahool -c "SHOW ssl;"

# Test connection
openssl s_client -connect localhost:5432 -starttls postgres
```

#### 3. Permission Denied Reading Certificate

**Error**: `Permission denied` when accessing certificate files

**Solution**:
```bash
# Fix permissions
cd /home/user/sahool-unified-v15-idp/config/certs
chmod 600 */server.key
chmod 644 */server.crt ca/ca.crt
```

#### 4. Wrong SSL Mode

**Error**: `sslmode value "require" is not valid`

**Solution**: Use correct sslmode values:
- PostgreSQL: `disable`, `allow`, `prefer`, `require`, `verify-ca`, `verify-full`
- Update connection string or environment variable

## Security Considerations

### Development Environment

- ✅ Use `sslmode=prefer` to allow gradual migration
- ✅ Self-signed certificates are acceptable
- ✅ Keep certificates in version control (except `.key` files)

### Production Environment

- ⚠️ Use `sslmode=require` or `sslmode=verify-full`
- ⚠️ Consider using CA-signed certificates
- ⚠️ Store certificates in secrets management (Vault, AWS Secrets Manager)
- ⚠️ Enable certificate pinning for critical services
- ⚠️ Implement automated certificate rotation
- ⚠️ Monitor certificate expiration

### Best Practices

1. **Never commit private keys** (`.key` files) to version control
2. **Rotate certificates regularly** (before expiration)
3. **Use strong ciphers** (TLS 1.2+, disable weak ciphers)
4. **Monitor TLS connections** (failed handshakes, expired certs)
5. **Implement certificate pinning** for critical clients
6. **Use separate certificates per environment** (dev/staging/prod)
7. **Keep CA private key extremely secure**
8. **Audit certificate access and usage**

## Migration Path

### Phase 1: Enable TLS (Optional Mode)

```bash
# Services support both TLS and non-TLS
# PostgreSQL: sslmode=prefer
# Redis: tls-auth-clients optional
```

### Phase 2: Update Applications

```bash
# Update all services to use TLS connections
# Test thoroughly
```

### Phase 3: Enforce TLS (Required Mode)

```bash
# PostgreSQL: sslmode=require
# Redis: tls-auth-clients yes
# NATS: verify=true
```

### Phase 4: Enable Mutual TLS (mTLS)

```bash
# Require client certificates
# PostgreSQL: sslmode=verify-full, clientcert=verify-full
# Redis: tls-auth-clients yes
# NATS: verify_and_map=true
```

## References

- [PostgreSQL SSL Documentation](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [Redis TLS Documentation](https://redis.io/docs/management/security/encryption/)
- [NATS TLS Documentation](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/tls)
- [Kong SSL Configuration](https://docs.konghq.com/gateway/latest/production/networking/cp-dp-proxy/)
- [OpenSSL Documentation](https://www.openssl.org/docs/)

## Support

For issues or questions about TLS configuration:

1. Check service logs: `docker-compose logs <service>`
2. Verify certificates: `./config/certs/generate-internal-tls.sh --verify`
3. Review this documentation
4. Check `/home/user/sahool-unified-v15-idp/config/certs/README.md`

---

**Document Version**: 1.0
**Last Updated**: 2026-01-06
**Maintained By**: SAHOOL Platform Team
