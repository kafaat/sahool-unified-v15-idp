# SAHOOL Platform - Secrets Management Documentation

**Version:** 2.0
**Last Updated:** 2026-01-06
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Supported Backends](#supported-backends)
4. [Quick Start](#quick-start)
5. [Vault Setup](#vault-setup)
6. [Kubernetes Integration](#kubernetes-integration)
7. [Docker Secrets](#docker-secrets)
8. [Secret Rotation](#secret-rotation)
9. [Audit & Monitoring](#audit--monitoring)
10. [Best Practices](#best-practices)
11. [Troubleshooting](#troubleshooting)

---

## Overview

SAHOOL Platform implements a comprehensive secrets management system that supports multiple backends:

- **Environment Variables** - For development and simple deployments
- **HashiCorp Vault** - Recommended for production
- **AWS Secrets Manager** - For AWS deployments
- **Azure Key Vault** - For Azure deployments

### Key Features

✅ **Multi-backend support** - Seamlessly switch between secrets providers
✅ **Automatic rotation** - Scheduled secret rotation with zero downtime
✅ **Audit logging** - Complete audit trail of all secret access
✅ **Encryption at rest** - AES-256-GCM encryption for sensitive data
✅ **Dynamic secrets** - Database credentials with automatic rotation
✅ **Kubernetes integration** - External Secrets Operator support
✅ **Anomaly detection** - Alert on suspicious access patterns

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    SAHOOL Applications                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │Field Ops │  │Weather   │  │Satellite │  │AI Advisor│   │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘   │
│       │             │              │             │          │
└───────┼─────────────┼──────────────┼─────────────┼──────────┘
        │             │              │             │
        └─────────────┴──────────────┴─────────────┘
                          │
        ┌─────────────────▼──────────────────┐
        │   Secrets Manager (manager.py)     │
        │  - Unified API                     │
        │  - Caching (5min TTL)              │
        │  - Fallback to environment         │
        │  - Audit logging                   │
        └─────────────────┬──────────────────┘
                          │
        ┌─────────────────┴──────────────────┐
        │                                     │
   ┌────▼─────┐  ┌───────▼────┐  ┌─────▼────┐  ┌────▼─────┐
   │   Vault  │  │    AWS     │  │  Azure   │  │   Env    │
   │  (Prod)  │  │  Secrets   │  │ KeyVault │  │Variables │
   └──────────┘  └────────────┘  └──────────┘  └──────────┘
```

### Components

1. **Secrets Manager** (`shared/secrets/manager.py`)
   - Unified interface for all backends
   - Automatic backend detection
   - Caching and fallback mechanisms

2. **Vault Client** (`shared/secrets/vault.py`)
   - HashiCorp Vault integration
   - Token renewal and caching
   - AppRole authentication

3. **Audit Logger** (`shared/secrets/audit.py`)
   - Access logging and monitoring
   - Anomaly detection
   - Prometheus metrics

4. **Rotation Scheduler** (`scripts/security/automated-rotation-scheduler.sh`)
   - Automated secret rotation
   - Policy enforcement
   - Notification system

---

## Supported Backends

### 1. Environment Variables (Development)

**Use Cases:** Local development, testing, simple deployments

**Configuration:**
```bash
# .env
SECRET_BACKEND=environment
DATABASE_PASSWORD=your-db-password
REDIS_PASSWORD=your-redis-password
JWT_SECRET_KEY=your-jwt-secret
```

**Pros:**
- Simple and straightforward
- No external dependencies
- Fast access

**Cons:**
- No rotation support
- Limited security
- No audit trail

---

### 2. HashiCorp Vault (Production - Recommended)

**Use Cases:** Production deployments, high-security environments

**Configuration:**
```bash
# .env
SECRET_BACKEND=vault
VAULT_ADDR=https://vault.sahool.com:8200
VAULT_ROLE_ID=<your-role-id>
VAULT_SECRET_ID=<your-secret-id>
VAULT_MOUNT_POINT=secret
VAULT_PATH_PREFIX=sahool
```

**Features:**
- Dynamic secrets with automatic rotation
- Comprehensive audit logging
- Encryption at rest and in transit
- High availability support
- Fine-grained access control

**Setup:** See [Vault Setup](#vault-setup)

---

### 3. AWS Secrets Manager

**Use Cases:** AWS deployments, EKS clusters

**Configuration:**
```bash
# .env
SECRET_BACKEND=aws_secrets_manager
AWS_REGION=us-east-1
AWS_SECRETS_PREFIX=sahool/
# Optional: Use IAM role instead of keys
# AWS_ACCESS_KEY_ID=<your-access-key>
# AWS_SECRET_ACCESS_KEY=<your-secret-key>
```

**Features:**
- Automatic rotation support
- IAM-based access control
- Integration with AWS services
- Versioning and recovery

---

### 4. Azure Key Vault

**Use Cases:** Azure deployments, AKS clusters

**Configuration:**
```bash
# .env
SECRET_BACKEND=azure_key_vault
AZURE_KEY_VAULT_URL=https://sahool-vault.vault.azure.net/
AZURE_TENANT_ID=<your-tenant-id>
AZURE_CLIENT_ID=<your-client-id>
AZURE_CLIENT_SECRET=<your-client-secret>
```

**Features:**
- Managed identities support
- Hardware security module (HSM) backed keys
- Automatic key rotation
- Azure AD integration

---

## Quick Start

### Development Setup (Environment Variables)

1. **Copy environment template:**
```bash
cp .env.example .env
```

2. **Generate secure secrets:**
```bash
# PostgreSQL password
openssl rand -base64 32 > /tmp/pg_pass
echo "POSTGRES_PASSWORD=$(cat /tmp/pg_pass)" >> .env

# Redis password
openssl rand -base64 32 > /tmp/redis_pass
echo "REDIS_PASSWORD=$(cat /tmp/redis_pass)" >> .env

# JWT secret
openssl rand -base64 32 > /tmp/jwt_secret
echo "JWT_SECRET_KEY=$(cat /tmp/jwt_secret)" >> .env

# Cleanup
rm /tmp/{pg_pass,redis_pass,jwt_secret}
```

3. **Use secrets in application:**
```python
from shared.secrets import get_secrets_manager, SecretKey

# Initialize secrets manager
secrets = get_secrets_manager()
await secrets.initialize()

# Get secrets
db_password = await secrets.get_secret(SecretKey.DATABASE_PASSWORD)
jwt_secret = await secrets.get_secret(SecretKey.JWT_SECRET)
```

---

## Vault Setup

### Prerequisites

- Docker or Kubernetes cluster
- `vault` CLI installed
- TLS certificates (production)

### 1. Deploy Vault

**Docker Compose (Development):**
```bash
docker compose -f infrastructure/core/vault/docker-compose.vault.yml up -d
```

**Kubernetes (Production):**
```bash
helm repo add hashicorp https://helm.releases.hashicorp.com
helm install vault hashicorp/vault \
  --values helm/vault-values.yaml \
  --namespace vault \
  --create-namespace
```

### 2. Initialize Vault

```bash
# Set Vault address
export VAULT_ADDR=https://vault.sahool.com:8200

# Initialize (first time only)
vault operator init

# Unseal Vault (or configure auto-unseal)
vault operator unseal <unseal-key-1>
vault operator unseal <unseal-key-2>
vault operator unseal <unseal-key-3>

# Login with root token
vault login <root-token>
```

### 3. Configure SAHOOL Secrets

Run the initialization script:

```bash
# Set required environment variables
export POSTGRES_PASSWORD=$(openssl rand -base64 32)
export REDIS_PASSWORD=$(openssl rand -base64 32)
export JWT_SECRET_KEY=$(openssl rand -base64 32)

# Run initialization
./infrastructure/core/vault/vault-init.sh
```

This script will:
- Enable secrets engines (KV v2, Database, PKI)
- Create SAHOOL secret structure
- Configure authentication (AppRole, Kubernetes)
- Enable audit logging
- Generate AppRole credentials

### 4. Save Credentials

The script outputs AppRole credentials:

```bash
VAULT_ROLE_ID=<role-id>
VAULT_SECRET_ID=<secret-id>
```

**Store these securely:**

For Kubernetes:
```bash
kubectl create secret generic vault-approle-secret \
  --from-literal=role-id=<role-id> \
  --from-literal=secret-id=<secret-id> \
  -n sahool
```

For environment:
```bash
echo "VAULT_ROLE_ID=<role-id>" >> .env
echo "VAULT_SECRET_ID=<secret-id>" >> .env
```

### 5. Configure Applications

Update application configuration to use Vault:

```bash
# .env
SECRET_BACKEND=vault
VAULT_ADDR=https://vault.sahool.com:8200
VAULT_ROLE_ID=<from-step-4>
VAULT_SECRET_ID=<from-step-4>
```

### 6. Test Secret Access

```bash
# Python
python3 <<EOF
import asyncio
from shared.secrets import get_secrets_manager, SecretKey

async def test():
    secrets = get_secrets_manager()
    await secrets.initialize()
    password = await secrets.get_secret(SecretKey.DATABASE_PASSWORD)
    print(f"Database password retrieved: {password[:4]}...")

asyncio.run(test())
EOF
```

### Production Vault Configuration

For production, use the provided configuration:

**File:** `infrastructure/core/vault/vault-production.hcl`

**Features:**
- Raft storage (integrated HA)
- TLS encryption
- Auto-unseal (AWS KMS, Azure KeyVault, GCP Cloud KMS)
- Audit logging
- Prometheus metrics

**Enable auto-unseal:**

For AWS:
```hcl
seal "awskms" {
  region     = "us-east-1"
  kms_key_id = "alias/sahool-vault-unseal"
}
```

For Azure:
```hcl
seal "azurekeyvault" {
  tenant_id     = "<tenant-id>"
  vault_name    = "sahool-vault"
  key_name      = "vault-unseal-key"
}
```

---

## Kubernetes Integration

SAHOOL uses **External Secrets Operator** to sync secrets from Vault/AWS/Azure to Kubernetes.

### 1. Install External Secrets Operator

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets \
  -n external-secrets-system \
  --create-namespace
```

### 2. Configure SecretStore

Apply the SAHOOL SecretStore configuration:

```bash
kubectl apply -f gitops/secrets/external-secrets-operator.yaml
```

This creates:
- **SecretStore** for Vault/AWS/Azure
- **ExternalSecret** resources for PostgreSQL, Redis, NATS, JWT, etc.
- Automatic secret synchronization every 1 hour

### 3. Verify Secrets

```bash
# Check ExternalSecrets status
kubectl get externalsecrets -n sahool

# Check synchronized secrets
kubectl get secrets -n sahool

# View secret details (without values)
kubectl describe secret sahool-postgresql-secret -n sahool
```

### 4. Force Secret Refresh

To immediately refresh secrets:

```bash
kubectl annotate externalsecret postgresql-credentials \
  force-sync="$(date +%s)" \
  -n sahool \
  --overwrite
```

---

## Docker Secrets

For Docker Compose or Docker Swarm deployments:

### 1. Create Secret Files

```bash
mkdir -p docker/secrets
cd docker/secrets

# Generate secrets
openssl rand -base64 32 > postgres_password.txt
openssl rand -base64 32 > redis_password.txt
openssl rand -base64 32 > jwt_secret_key.txt

# Set permissions
chmod 600 *.txt
```

### 2. Use Docker Secrets

**File:** `docker/docker-compose.secrets.yml`

```yaml
services:
  postgres:
    secrets:
      - postgres_password
    environment:
      POSTGRES_PASSWORD_FILE: /run/secrets/postgres_password

secrets:
  postgres_password:
    file: ./secrets/postgres_password.txt
```

### 3. Deploy with Secrets

```bash
docker compose -f docker-compose.yml \
  -f docker/docker-compose.secrets.yml \
  up -d
```

---

## Secret Rotation

SAHOOL implements **automated secret rotation** with configurable policies.

### Rotation Schedule

| Secret Type | Rotation Interval | Implementation |
|-------------|------------------|----------------|
| Database passwords | Every 90 days | Vault dynamic secrets or manual |
| JWT signing keys | Every 180 days | Manual with grace period |
| Redis passwords | Every 90 days | Manual (requires restart) |
| API keys | Every 90 days | Manual |
| Encryption keys | Every 365 days | Manual with re-encryption |

### Manual Rotation

```bash
# Rotate all secrets that need rotation
./scripts/security/automated-rotation-scheduler.sh --rotate-all

# Force rotate specific secrets
./scripts/security/automated-rotation-scheduler.sh --force-database
./scripts/security/automated-rotation-scheduler.sh --force-jwt
```

### Automated Rotation (Cron)

Add to crontab:

```bash
# Check and rotate daily at 2 AM
0 2 * * * /path/to/automated-rotation-scheduler.sh --rotate-all >> /var/log/sahool-rotation.log 2>&1
```

### Rotation Status

```bash
./scripts/security/automated-rotation-scheduler.sh --status
```

Output:
```
═══════════════════════════════════════════════════════════════════
                    Secret Rotation Status
═══════════════════════════════════════════════════════════════════

Secret: database
  Last Rotation: 2026-01-06
  Days Since:    0 days

Secret: jwt
  Last Rotation: 2025-07-10
  Days Since:    180 days

[... more secrets ...]
```

### Vault Dynamic Secrets

For automatic database credential rotation:

```bash
# Enable in .env
USE_VAULT_DYNAMIC_SECRETS=true
```

Vault will:
- Generate new database credentials on demand
- Automatically rotate credentials based on TTL (24h default)
- Revoke old credentials after expiry

**Benefits:**
- Zero-touch rotation
- Least privilege access
- Automatic cleanup

---

## Audit & Monitoring

### Secret Access Logging

All secret access is logged and audited:

```python
from shared.secrets.audit import SecretAccessEvent, AccessResult, audit_secret_access

# Log secret access
event = SecretAccessEvent(
    access_type=SecretAccessType.READ,
    secret_path="database/password",
    backend="vault",
    result=AccessResult.SUCCESS,
    user="field-ops-service",
    source_ip="10.0.1.15",
    service="field-ops",
    duration_ms=45.2
)

await audit_secret_access(event)
```

### Audit Logs Location

- **File:** `/var/log/sahool/secret-audit.log`
- **Format:** JSON (structured logging)
- **Retention:** 90 days (configurable)

### Anomaly Detection

The audit system automatically detects:

1. **High-frequency access** (>100 requests/hour to same secret)
2. **Multiple failed attempts** (>5 failures in 15 minutes)
3. **Unusual access times** (3-6 AM)
4. **Access from new IPs**

**Alerts are sent via:**
- Log warnings
- Slack/Teams webhooks (configure `SLACK_WEBHOOK_URL`)
- Email notifications

### Prometheus Metrics

Available metrics:

```
# Total secret accesses
sahool_secret_access_total{backend,access_type,result,service}

# Secret access duration
sahool_secret_access_duration_seconds{backend,access_type}

# Failed access attempts
sahool_secret_access_failures_total{backend,result,user}
```

**Grafana Dashboard:** Import `monitoring/grafana/dashboards/secrets.json`

### Access Statistics

Get access statistics:

```python
from shared.secrets.audit import get_audit_logger

logger = get_audit_logger()
stats = logger.get_access_stats(hours=24)

print(stats)
# {
#   "total_accesses": 1250,
#   "successful": 1248,
#   "failed": 2,
#   "unique_users": 15,
#   "unique_paths": 42,
#   "by_backend": {"vault": 1200, "environment": 50},
#   "by_user": {"field-ops": 400, "weather-core": 350, ...}
# }
```

---

## Best Practices

### 1. Secret Generation

**Always use cryptographically secure random generation:**

```bash
# Good ✅
openssl rand -base64 32

# Good ✅
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Bad ❌
echo "password123"

# Bad ❌
date +%s | sha256sum
```

### 2. Secret Storage

**Never commit secrets to Git:**

```bash
# .gitignore
.env
.env.*
!.env.example
secrets/
*.pem
*.key
*.p12
credentials.json
```

**Use proper file permissions:**

```bash
chmod 600 .env
chmod 600 secrets/*
chmod 700 secrets/
```

### 3. Secret Length

**Minimum lengths:**

- Passwords: 32 characters
- API keys: 48 characters
- JWT secrets: 32 characters
- Encryption keys: 32 bytes (256 bits)
- RSA keys: 4096 bits

### 4. Secret Rotation

**Implement rotation policies:**

- Database passwords: Every 90 days
- JWT keys: Every 180 days
- Never reuse old secrets
- Always test after rotation

### 5. Access Control

**Principle of least privilege:**

```python
# Good ✅ - Only request needed secrets
password = await secrets.get_secret(SecretKey.DATABASE_PASSWORD)

# Bad ❌ - Don't fetch all secrets
all_secrets = await secrets.get_all_secrets()
```

**Use service-specific credentials:**

- field-ops → database_field_ops_user
- weather-core → database_weather_user
- admin → database_admin_user

### 6. Environment Separation

**Keep environments isolated:**

```
vault/
  ├── sahool/dev/database/password
  ├── sahool/staging/database/password
  └── sahool/prod/database/password
```

**Use different encryption keys per environment**

### 7. Monitoring & Alerts

**Monitor for:**

- Failed authentication attempts
- Unusual access patterns
- Secret rotation failures
- Vault seal status

**Set up alerts for:**

- Secrets expiring in < 7 days
- Rotation policy violations
- High failure rates
- Vault downtime

---

## Troubleshooting

### Issue: "Cannot connect to Vault"

**Symptoms:**
```
ConnectionError: Cannot connect to Vault at https://vault:8200
```

**Solutions:**

1. Check Vault is running:
```bash
docker ps | grep vault
# or
kubectl get pods -n vault
```

2. Verify VAULT_ADDR:
```bash
echo $VAULT_ADDR
curl -k $VAULT_ADDR/v1/sys/health
```

3. Check network connectivity:
```bash
ping vault
telnet vault 8200
```

4. Verify TLS certificates:
```bash
openssl s_client -connect vault:8200 -showcerts
```

---

### Issue: "Invalid Vault token"

**Symptoms:**
```
ConnectionError: Invalid Vault token
```

**Solutions:**

1. Check token is set:
```bash
echo $VAULT_TOKEN
```

2. Verify token is valid:
```bash
vault token lookup
```

3. Use AppRole instead:
```bash
unset VAULT_TOKEN
export VAULT_ROLE_ID=<role-id>
export VAULT_SECRET_ID=<secret-id>
```

4. Renew token:
```bash
vault token renew
```

---

### Issue: "Secret not found"

**Symptoms:**
```
KeyError: Secret not found: database/password
```

**Solutions:**

1. List available secrets:
```bash
vault kv list secret/sahool
```

2. Check secret path:
```bash
# Correct ✅
vault kv get secret/sahool/database/postgres

# Incorrect ❌
vault kv get secret/database/postgres
```

3. Verify SECRET_BACKEND:
```bash
echo $SECRET_BACKEND
# Should be: vault, aws_secrets_manager, azure_key_vault, or environment
```

4. Check fallback to environment:
```bash
# If Vault fails, it falls back to environment variables
echo $DATABASE_PASSWORD
```

---

### Issue: "External Secrets not syncing"

**Symptoms:**
- ExternalSecret status shows error
- Kubernetes secrets not created

**Solutions:**

1. Check ExternalSecret status:
```bash
kubectl describe externalsecret postgresql-credentials -n sahool
```

2. Check SecretStore:
```bash
kubectl describe secretstore vault-backend -n sahool
```

3. Verify Vault connectivity from cluster:
```bash
kubectl run vault-test --rm -it --image=hashicorp/vault -- \
  vault status -address=https://vault:8200
```

4. Check AppRole secret:
```bash
kubectl get secret vault-approle-secret -n sahool
```

5. Force refresh:
```bash
kubectl delete externalsecret postgresql-credentials -n sahool
kubectl apply -f gitops/secrets/external-secrets-operator.yaml
```

---

### Issue: "Secret rotation failed"

**Symptoms:**
```
[ERROR] Failed to rotate database password
```

**Solutions:**

1. Check rotation logs:
```bash
cat /var/log/sahool-rotation.log
```

2. Verify Vault permissions:
```bash
vault token capabilities secret/sahool/database/postgres
# Should include: create, update
```

3. Test manual rotation:
```bash
./scripts/security/rotate-secrets.sh --database
```

4. Check database connectivity:
```bash
PGPASSWORD=$POSTGRES_ADMIN_PASSWORD psql -h postgres -U postgres -c "SELECT 1"
```

5. Verify rotation state:
```bash
ls -la .rotation-state/
cat .rotation-state/database_last_rotation
```

---

## Additional Resources

### Documentation

- [Vault Setup Guide](../infrastructure/core/vault/README.md)
- [External Secrets Operator](https://external-secrets.io/latest/)
- [Secret Rotation Policy](./SECRETS_ROTATION_POLICY.md)
- [Security Audit Report](../tests/database/SECRETS_MANAGEMENT_AUDIT.md)

### Scripts

- `scripts/security/rotate-secrets.sh` - Manual secret rotation
- `scripts/security/automated-rotation-scheduler.sh` - Automated rotation
- `infrastructure/core/vault/vault-init.sh` - Vault initialization

### Configuration Files

- `.env.example` - Environment variable template
- `infrastructure/core/vault/vault-production.hcl` - Vault production config
- `gitops/secrets/external-secrets-operator.yaml` - Kubernetes integration
- `docker/docker-compose.secrets.yml` - Docker secrets

---

## Support

For issues or questions:

1. Check this documentation
2. Review audit logs: `/var/log/sahool/secret-audit.log`
3. Check application logs
4. Create an issue in the repository
5. Contact DevOps team

---

**Document Version:** 2.0
**Last Updated:** 2026-01-06
**Next Review:** 2026-04-06
