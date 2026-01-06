# TLS Quick Start Guide

## 🚀 Quick Start (5 minutes)

### 1. Generate Certificates
```bash
cd /home/user/sahool-unified-v15-idp/config/certs
./generate-internal-tls.sh
```

### 2. Start Services with TLS
```bash
cd /home/user/sahool-unified-v15-idp
docker-compose -f docker-compose.yml -f docker-compose.tls.yml up -d
```

### 3. Verify TLS is Working
```bash
# Check PostgreSQL
docker-compose exec postgres psql -U sahool -c "SHOW ssl;"
# Expected: ssl | on

# Check Redis
docker-compose exec redis redis-cli CONFIG GET tls-port
# Expected: tls-port | 6379

# Check NATS
curl http://localhost:8222/varz | jq '.tls'
# Expected: TLS configuration shown

# Check Kong
curl -k https://localhost:8443/
# Expected: Kong response
```

## 📋 Common Commands

### Certificate Management
```bash
# View certificate info
./generate-internal-tls.sh --info postgres

# Verify all certificates
./generate-internal-tls.sh --verify

# Regenerate all certificates
./generate-internal-tls.sh --force

# Generate single service certificate
./generate-internal-tls.sh --service redis
```

### Service Management
```bash
# Start with TLS
docker-compose -f docker-compose.yml -f docker-compose.tls.yml up -d

# Stop services
docker-compose down

# Restart single service
docker-compose restart postgres

# View logs
docker-compose logs postgres | grep -i ssl
docker-compose logs redis | grep -i tls
```

### Testing Connections
```bash
# Test PostgreSQL TLS
psql "postgresql://sahool:password@localhost:5432/sahool?sslmode=require"

# Test Redis TLS
redis-cli --tls --cacert config/certs/ca/ca.crt -h localhost -p 6379

# Test NATS TLS
nats sub test --tlscert=config/certs/nats/server.crt \
              --tlskey=config/certs/nats/server.key \
              --tlsca=config/certs/ca/ca.crt

# Test Kong HTTPS
curl -k https://localhost:8443/
```

## 🔧 Troubleshooting

### Certificate Errors
```bash
# Verify certificate chain
openssl verify -CAfile ca/ca.crt postgres/server.crt

# Check certificate dates
openssl x509 -in postgres/server.crt -noout -dates

# View certificate details
openssl x509 -in postgres/server.crt -noout -text
```

### Connection Issues
```bash
# Check if service is listening on TLS port
docker-compose exec postgres ss -tlnp | grep 5432
docker-compose exec redis ss -tlnp | grep 6379

# Test TLS handshake
openssl s_client -connect localhost:5432 -starttls postgres
openssl s_client -connect localhost:6379
```

### Permission Issues
```bash
# Fix certificate permissions
chmod 600 */server.key
chmod 644 */server.crt ca/ca.crt
```

## ⚡ Environment Variables

Add to your `.env` file:

```bash
# Enable TLS override
COMPOSE_FILE=docker-compose.yml:docker-compose.tls.yml

# PostgreSQL
PGSSLMODE=prefer
PGSSLROOTCERT=/app/certs/ca.crt

# Redis
REDIS_TLS_ENABLED=true
REDIS_TLS_CA_CERTS=/app/certs/ca.crt

# NATS
NATS_TLS_ENABLED=true
NATS_TLS_CA=/app/certs/ca.crt
```

## 📚 More Information

- Full Documentation: `/home/user/sahool-unified-v15-idp/docs/TLS_CONFIGURATION.md`
- Certificate Details: `/home/user/sahool-unified-v15-idp/config/certs/README.md`
- Docker Compose TLS: `/home/user/sahool-unified-v15-idp/docker-compose.tls.yml`

## 🔒 Security Reminders

- ✅ Never commit `*.key` files to git
- ✅ Rotate certificates before expiration (825 days)
- ✅ Use `sslmode=require` in production
- ✅ Keep CA private key secure
- ✅ Monitor certificate expiration dates
