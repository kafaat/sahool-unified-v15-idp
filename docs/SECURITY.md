# SAHOOL v15.3.2 Security Guide

## Overview

SAHOOL implements a comprehensive security layer including:

- JWT-based authentication
- Role-Based Access Control (RBAC)
- Audit logging
- mTLS between services (optional)
- Secret management

## Authentication (JWT)

### Token Structure

Access tokens contain these claims:

```json
{
  "sub": "user-uuid",           // User ID
  "tid": "tenant-uuid",         // Tenant ID
  "roles": ["worker", "supervisor"],
  "scopes": ["fieldops:task.read", "fieldops:task.complete"],
  "exp": 1699999999,            // Expiration
  "iat": 1699990000,            // Issued at
  "iss": "sahool-idp",          // Issuer
  "aud": "sahool-platform"      // Audience
}
```

### Token Usage

```bash
# Include in Authorization header
curl -H "Authorization: Bearer <token>" http://localhost:8080/api/tasks
```

### Token Refresh

```bash
curl -X POST http://localhost:8080/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{"refresh_token": "<refresh_token>"}'
```

## Authorization (RBAC)

### Roles

| Role | Description | Typical Permissions |
|------|-------------|---------------------|
| `viewer` | Read-only access | View tasks, fields, reports |
| `worker` | Field operations | Complete tasks, send chat messages |
| `supervisor` | Team lead | Create/assign tasks |
| `manager` | Full operations | All CRUD, exports |
| `admin` | Tenant admin | User management, audit logs |
| `super_admin` | Platform admin | Cross-tenant access |

### Permission Format

Permissions follow the format: `service:resource.action`

Examples:
- `fieldops:task.read`
- `fieldops:task.create`
- `fieldops:task.complete`
- `admin:users.create`

### Role Hierarchy

```
super_admin
    └── admin
        └── manager
            └── supervisor
                └── worker
                    └── viewer
```

### Using Guards in Code

```python
from shared.security.deps import get_principal
from shared.security.guard import require, require_role

@app.post("/tasks/{task_id}/complete")
async def complete_task(
    task_id: str,
    principal: dict = Depends(get_principal)
):
    # Check permission
    require(principal, "fieldops:task.complete")

    # Or check role
    require_role(principal, "worker")

    # ... business logic
```

## Audit Logging

### What's Logged

- Authentication events (login, logout, token refresh)
- Authorization failures
- Data changes (create, update, delete)
- Administrative actions
- Security events

### Audit Log Schema

```json
{
  "id": "uuid",
  "tenant_id": "tenant-uuid",
  "user_id": "user-uuid",
  "action": "data.task.completed",
  "category": "data",
  "severity": "info",
  "resource_type": "task",
  "resource_id": "task-uuid",
  "ip_address": "192.168.1.100",
  "success": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Querying Audit Logs

```python
from shared.security.audit import get_user_audit_trail

# Get user's recent activity
logs = await get_user_audit_trail(
    tenant_id="tenant-uuid",
    user_id="user-uuid",
    limit=100
)

# Get security events
from shared.security.audit import get_security_events
events = await get_security_events(tenant_id="tenant-uuid")
```

## mTLS Configuration

### Generate Certificates

```bash
./scripts/security/generate-certs.sh
```

This creates:
- Root CA certificate
- Service certificates for each component
- Docker secrets structure

### Enable mTLS

1. Set environment variable:
```bash
ENABLE_MTLS=true
```

2. Mount certificates in Docker Compose:
```yaml
services:
  field_ops:
    volumes:
      - ./secrets/certs/services/field_ops:/certs:ro
    environment:
      - SSL_CERT_FILE=/certs/field_ops.crt
      - SSL_KEY_FILE=/certs/field_ops.key
      - SSL_CA_FILE=/certs/ca.crt
```

## Secret Management

### Rotate Secrets

```bash
# Rotate all secrets
./scripts/security/rotate-secrets.sh --all

# Rotate specific secrets
./scripts/security/rotate-secrets.sh --jwt      # JWT keys only
./scripts/security/rotate-secrets.sh --database # DB passwords only
```

### Secret Storage

Secrets are stored in:
- `secrets/jwt/` - JWT keys
- `secrets/database/` - Database passwords
- `secrets/nats/` - NATS credentials
- `secrets/encryption/` - Encryption keys

**Never commit secrets to git!**

### Production Secret Management

For production, use:
- HashiCorp Vault
- AWS Secrets Manager
- Azure Key Vault
- Kubernetes Secrets (with encryption at rest)

## Security Headers

All services include these headers:

```
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Rate Limiting

Default limits:

| Endpoint Type | Limit |
|--------------|-------|
| Authentication | 10/minute/IP |
| API reads | 100/minute/user |
| API writes | 30/minute/user |
| WebSocket | 50 connections/user |

## Security Checklist

### Before Production

- [ ] Generate unique JWT secret (min 64 characters)
- [ ] Generate unique database passwords
- [ ] Enable HTTPS/TLS on ingress
- [ ] Configure CORS properly
- [ ] Enable audit logging
- [ ] Set up log aggregation
- [ ] Configure rate limiting
- [ ] Enable mTLS between services (optional)
- [ ] Set up secrets rotation schedule
- [ ] Configure backup encryption

### Ongoing

- [ ] Monitor audit logs for suspicious activity
- [ ] Rotate secrets quarterly
- [ ] Update dependencies monthly
- [ ] Review access permissions
- [ ] Test backup restoration

## Incident Response

### Suspected Breach

1. **Contain**: Revoke affected tokens
   ```bash
   # Rotate JWT key (invalidates all tokens)
   ./scripts/security/rotate-secrets.sh --jwt
   ```

2. **Investigate**: Check audit logs
   ```sql
   SELECT * FROM security_audit_logs
   WHERE success = false
   ORDER BY created_at DESC;
   ```

3. **Remediate**: Reset affected credentials

4. **Document**: Record incident details

## Compliance

SAHOOL supports compliance with:

- **GDPR**: Data isolation per tenant, audit trails
- **SOC2**: Comprehensive audit logging
- **ISO 27001**: Security controls framework

For compliance questions, contact your security team.
