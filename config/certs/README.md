# SAHOOL Internal TLS Configuration

This directory contains self-signed TLS certificates for encrypting internal service communication in the SAHOOL platform.

## Overview

Internal TLS encryption is configured for the following critical services:

- **PostgreSQL**: Database connections encrypted with TLS
- **PgBouncer**: Connection pooler with TLS to PostgreSQL and clients
- **Redis**: Cache and session store with TLS
- **NATS**: Message queue with TLS
- **Kong**: API Gateway with TLS termination

## Directory Structure

```
config/certs/
├── ca/
│   ├── ca.crt              # Root CA certificate (public, safe to distribute)
│   ├── ca.key              # Root CA private key (SECRET - never commit!)
│   └── ca.srl              # Certificate serial number
├── postgres/
│   ├── server.crt          # PostgreSQL server certificate
│   ├── server.key          # PostgreSQL private key (SECRET)
│   └── ca.crt              # CA certificate (copy)
├── pgbouncer/
│   ├── server.crt          # PgBouncer server certificate
│   ├── server.key          # PgBouncer private key (SECRET)
│   └── ca.crt              # CA certificate (copy)
├── redis/
│   ├── server.crt          # Redis server certificate
│   ├── server.key          # Redis private key (SECRET)
│   └── ca.crt              # CA certificate (copy)
├── nats/
│   ├── server.crt          # NATS server certificate
│   ├── server.key          # NATS private key (SECRET)
│   └── ca.crt              # CA certificate (copy)
├── kong/
│   ├── server.crt          # Kong server certificate
│   ├── server.key          # Kong private key (SECRET)
│   └── ca.crt              # CA certificate (copy)
├── generate-internal-tls.sh # Certificate generation script
├── .gitignore              # Prevents committing private keys
└── README.md               # This file
```

## Quick Start

### 1. Generate Certificates

Generate all certificates with a single command:

```bash
cd config/certs
./generate-internal-tls.sh
```

This will:
- Create a Root CA valid for 10 years
- Generate service certificates valid for ~2.25 years (825 days)
- Verify all certificates
- Set proper file permissions

### 2. Enable TLS in Docker Compose

Use the TLS override configuration:

```bash
# Option 1: Command line
docker-compose -f docker-compose.yml -f docker-compose.tls.yml up

# Option 2: Environment variable (add to .env)
COMPOSE_FILE=docker-compose.yml:docker-compose.tls.yml
docker-compose up
```

### 3. Update Application Connection Strings

Applications need to be updated to use TLS:

#### PostgreSQL Connections

```bash
# Prefer TLS (falls back to non-TLS if unavailable)
postgresql://user:pass@postgres:5432/db?sslmode=prefer

# Require TLS
postgresql://user:pass@postgres:5432/db?sslmode=require

# Require TLS with server verification
postgresql://user:pass@postgres:5432/db?sslmode=verify-ca&sslrootcert=/path/to/ca.crt

# Full verification (hostname + certificate)
postgresql://user:pass@postgres:5432/db?sslmode=verify-full&sslrootcert=/path/to/ca.crt
```

#### Redis Connections

```bash
# TLS enabled (rediss:// instead of redis://)
rediss://:password@redis:6379/0

# With CA verification
rediss://:password@redis:6379/0?ssl_ca_certs=/path/to/ca.crt
```

#### NATS Connections

```bash
# TLS enabled
nats://user:pass@nats:4222?tls=true

# With certificate verification
nats://user:pass@nats:4222?tls=true&tls_ca=/path/to/ca.crt
```

#### Kong

```bash
# Access Kong proxy via HTTPS
https://kong:8443

# Admin API (localhost only)
http://localhost:8001
```

## Certificate Management

### View Certificate Information

```bash
# View a service certificate
./generate-internal-tls.sh --info postgres

# View CA certificate
openssl x509 -in ca/ca.crt -noout -text
```

### Verify Certificates

```bash
# Verify all certificates
./generate-internal-tls.sh --verify

# Verify a specific certificate against CA
openssl verify -CAfile ca/ca.crt postgres/server.crt
```

### Generate Single Service Certificate

```bash
# Generate only for a specific service
./generate-internal-tls.sh --service redis
```

### Regenerate All Certificates

```bash
# Force regeneration (deletes and recreates all)
./generate-internal-tls.sh --force
```

### Certificate Rotation

Certificates expire after 825 days (~2.25 years). Plan rotation before expiration:

1. **Check expiration dates:**
   ```bash
   for cert in */server.crt; do
     echo "=== $cert ==="
     openssl x509 -in "$cert" -noout -dates
   done
   ```

2. **Generate new certificates:**
   ```bash
   ./generate-internal-tls.sh --force
   ```

3. **Rolling restart services:**
   ```bash
   # Restart services one at a time
   docker-compose restart postgres
   docker-compose restart pgbouncer
   docker-compose restart redis
   docker-compose restart nats
   docker-compose restart kong
   ```

## Security Best Practices

### DO:
- ✅ Keep `*.key` files secure (never commit to git)
- ✅ Use `sslmode=require` or higher in production
- ✅ Rotate certificates before expiration
- ✅ Monitor certificate expiration dates
- ✅ Use strong passwords for service authentication
- ✅ Enable TLS for all internal service communication
- ✅ Keep the CA private key (`ca.key`) extremely secure

### DON'T:
- ❌ Never commit `*.key` files to version control
- ❌ Never use these self-signed certs for public-facing services
- ❌ Never share the CA private key
- ❌ Don't use `sslmode=disable` in production
- ❌ Don't ignore certificate expiration warnings
- ❌ Don't reuse certificates across environments

## Troubleshooting

### Certificate Errors

**Problem**: `certificate verify failed`

**Solution**: Ensure the CA certificate is properly configured:
```bash
# Check if CA cert is accessible
ls -la ca/ca.crt

# Verify certificate chain
openssl verify -CAfile ca/ca.crt postgres/server.crt
```

### Connection Refused

**Problem**: Service refuses TLS connection

**Solution**: Check service configuration:
```bash
# Check if TLS is enabled in service
docker-compose logs postgres | grep -i ssl
docker-compose logs redis | grep -i tls
docker-compose logs nats | grep -i tls
```

### Permission Denied

**Problem**: Cannot read certificate files

**Solution**: Fix file permissions:
```bash
# Set proper permissions
chmod 600 */server.key
chmod 644 */server.crt ca/ca.crt
```

### Certificate Expired

**Problem**: Certificate has expired

**Solution**: Regenerate certificates:
```bash
./generate-internal-tls.sh --force
docker-compose restart
```

## Environment Variables

For applications that support environment-based TLS configuration:

```bash
# PostgreSQL
PGSSLMODE=prefer
PGSSLROOTCERT=/path/to/ca.crt

# Redis (Python redis-py)
REDIS_SSL=True
REDIS_SSL_CA_CERTS=/path/to/ca.crt

# Node.js applications
NODE_TLS_REJECT_UNAUTHORIZED=1  # Require valid certificates
```

## Client Code Examples

### Python (PostgreSQL)

```python
import psycopg2

conn = psycopg2.connect(
    host="postgres",
    port=5432,
    database="sahool",
    user="sahool",
    password="password",
    sslmode="verify-ca",
    sslrootcert="/app/certs/ca.crt"
)
```

### Python (Redis)

```python
import redis

client = redis.Redis(
    host='redis',
    port=6379,
    password='password',
    ssl=True,
    ssl_ca_certs='/app/certs/ca.crt'
)
```

### Node.js (PostgreSQL)

```javascript
const { Pool } = require('pg');

const pool = new Pool({
  host: 'postgres',
  port: 5432,
  database: 'sahool',
  user: 'sahool',
  password: 'password',
  ssl: {
    rejectUnauthorized: true,
    ca: fs.readFileSync('/app/certs/ca.crt').toString(),
  }
});
```

### Node.js (Redis)

```javascript
const redis = require('redis');

const client = redis.createClient({
  socket: {
    host: 'redis',
    port: 6379,
    tls: true,
    ca: fs.readFileSync('/app/certs/ca.crt'),
  },
  password: 'password'
});
```

## Production Considerations

### For Production Deployments:

1. **Use a proper CA**: Replace self-signed certificates with CA-signed certificates from Let's Encrypt, DigiCert, or your organization's PKI

2. **Certificate Storage**: Store certificates in a secrets management system:
   - HashiCorp Vault
   - AWS Secrets Manager
   - Azure Key Vault
   - Kubernetes Secrets

3. **Automated Rotation**: Implement automated certificate rotation:
   - cert-manager for Kubernetes
   - AWS Certificate Manager
   - Custom automation scripts

4. **Monitoring**: Set up monitoring for:
   - Certificate expiration (alert 30 days before)
   - TLS handshake failures
   - Certificate validation errors

5. **Audit Logging**: Enable audit logging for:
   - Certificate generation
   - Certificate access
   - TLS connection attempts
   - Certificate rotation events

## Additional Resources

- [PostgreSQL SSL Documentation](https://www.postgresql.org/docs/current/ssl-tcp.html)
- [Redis TLS Documentation](https://redis.io/docs/management/security/encryption/)
- [NATS TLS Documentation](https://docs.nats.io/running-a-nats-service/configuration/securing_nats/tls)
- [Kong SSL Documentation](https://docs.konghq.com/gateway/latest/production/networking/cp-dp-proxy/)

## Support

For issues or questions:
1. Check service logs: `docker-compose logs <service>`
2. Verify certificates: `./generate-internal-tls.sh --verify`
3. Review this documentation
4. Contact the platform team

---

**Last Updated**: 2026-01-06
**Certificate Validity**: 825 days (approx. 2.25 years)
**Next Rotation Due**: Run `./generate-internal-tls.sh --verify` to check
