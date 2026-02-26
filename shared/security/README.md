# shared/security

Security primitives for the SAHOOL platform: JWT validation, RBAC, policy enforcement, token revocation, audit logging, and secrets management. All FastAPI services use this module as the single source of truth for authorization decisions.

**Version**: 15.4.0

---

## Module Structure

```
shared/security/
├── jwt.py              # Token creation and verification (HS256)
├── rbac.py             # Roles, permissions, and access checks
├── policy_engine.py    # Route-level and resource-level policy evaluation
├── deps.py             # FastAPI dependencies (get_principal, get_tenant_id)
├── guard.py            # Permission guards and decorators
├── audit.py            # Audit logging with hash-chain integrity
├── audit_models.py     # Tortoise ORM model for AuditLog table
├── token_revocation.py # JTI/user/tenant token revocation
└── config.py           # Secrets management (env vars + HashiCorp Vault)
```

---

## JWT Authentication

### Verifying a token

```python
from shared.security import verify_token, AuthError

try:
    payload = verify_token(token)
    user_id = payload["sub"]
    tenant_id = payload["tid"]
    roles = payload["roles"]
except AuthError as e:
    # e.code: "token_expired" | "token_revoked" | "invalid_token" | ...
    raise HTTPException(status_code=401, detail=e.message)
```

### Creating tokens

```python
from shared.security import create_token
from shared.security.jwt import create_token_pair

# Full token pair (access + refresh)
tokens = create_token_pair(
    user_id="user-uuid",
    tenant_id="tenant-uuid",
    roles=["manager"],
    scopes=["fieldops:task.read"],
)
# Returns: {"access_token": "...", "refresh_token": "...", "token_type": "bearer", "expires_in": 1800}

# Single access token with custom expiry
from datetime import timedelta
token = create_token(
    user_id="user-uuid",
    tenant_id="tenant-uuid",
    roles=["worker"],
    scopes=[],
    expires_delta=timedelta(hours=12),
)
```

**Token claims**: `sub` (user_id), `tid` (tenant_id), `roles`, `scopes`, `iss`, `aud`, `jti`, `iat`, `exp`.

Only HS256 is accepted. The `none` algorithm and RS256 are explicitly rejected.

---

## FastAPI Dependencies

Use these as route dependencies to require authentication:

```python
from fastapi import Depends
from shared.security import get_principal, get_optional_principal
from shared.security.deps import get_tenant_id, get_user_id, Principal, TenantID

# Require authentication — raises HTTP 401 if missing/invalid
@router.get("/fields")
async def list_fields(principal: dict = Depends(get_principal)):
    tenant_id = principal["tid"]
    ...

# Typed aliases (equivalent, cleaner syntax)
@router.get("/tasks")
async def list_tasks(principal: Principal, tenant_id: TenantID):
    ...

# Optional auth — returns None for unauthenticated requests
@router.get("/public-data")
async def public_data(principal: dict | None = Depends(get_optional_principal)):
    ...

# API key auth (for external integrations)
from shared.security.deps import require_api_key
@router.post("/webhook")
async def webhook(api_key: str = Depends(require_api_key)):
    ...
```

---

## RBAC — Roles and Permissions

### Roles (ascending privilege)

| Role | Description |
|------|-------------|
| `viewer` | Read-only access across all domains |
| `worker` | Field task updates, chat write |
| `supervisor` | Task creation and assignment, IoT device updates |
| `manager` | Full field/IoT/report/chat management |
| `admin` | Tenant user administration, audit log access |
| `super_admin` | Cross-tenant access, tenant management |

### Permission format

`service:resource.action` — e.g., `fieldops:task.create`, `ndvi:compute`, `admin:users.delete`.

### Permission checks

```python
from shared.security import has_permission, ROLE_PERMISSIONS
from shared.security.rbac import has_any_permission, has_all_permissions, can_access_resource

# Single permission check
if has_permission(principal, "fieldops:task.delete"):
    ...

# Any of several permissions
if has_any_permission(principal, ["fieldops:task.read", "fieldops:task.admin"]):
    ...

# Combined permission + tenant isolation
if can_access_resource(principal, "ndvi:read", resource_tenant_id):
    ...

# Inspect a role's permissions
perms = ROLE_PERMISSIONS["manager"]  # returns set[str]
```

---

## Guards — Enforcing Permissions in Routes

Guards raise `HTTP 403` automatically on failure with bilingual error messages (AR/EN).

```python
from shared.security import require, require_any, require_all
from shared.security.guard import (
    require_role, require_tenant, require_resource_access,
    require_owner_or_permission,
)

@router.post("/tasks")
async def create_task(principal: dict = Depends(get_principal)):
    require(principal, "fieldops:task.create")
    ...

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str, principal: dict = Depends(get_principal)):
    task = await get_task(task_id)
    # Enforce permission + tenant isolation in one call
    require_resource_access(principal, "fieldops:task.delete", task.tenant_id)
    ...

@router.put("/users/{user_id}/profile")
async def update_profile(user_id: str, principal: dict = Depends(get_principal)):
    # Owner can edit their own profile; otherwise requires admin permission
    require_owner_or_permission(principal, user_id, "admin:users.update")
    ...
```

### Decorator form

```python
from shared.security.guard import requires, requires_role

@router.delete("/devices/{device_id}")
@requires("iot:device.delete")
async def delete_device(device_id: str, principal: dict = Depends(get_principal)):
    ...

@router.get("/admin/users")
@requires_role("admin")
async def list_users(principal: dict = Depends(get_principal)):
    ...
```

---

## Policy Engine

The `PolicyEngine` provides route-level and resource-level authorization decisions. It is the single evaluation point shared by the Next.js middleware, React route guards, and API guards.

```python
from shared.security import PolicyEngine, PolicyContext, can_access, evaluate_policy

# Route-level check
context = PolicyContext.from_principal(principal)
result = evaluate_policy(context, "/admin/tenants")

if not result.allowed:
    return redirect(result.redirect_to)  # e.g., "/login", "/dashboard"

# Resource-level check (with tenant isolation)
result = can_access(
    context,
    resource_type="field",
    resource_id=field_id,
    resource_tenant_id=field.tenant_id,
    action="delete",
)

if result.decision == PolicyDecision.DENY:
    raise HTTPException(403, result.reason)
```

Custom policies can be registered at startup:

```python
from shared.security.policy_engine import get_policy_engine, RoutePolicy

engine = get_policy_engine()
engine.add_policy("/api/v1/reports/export", RoutePolicy(
    path_pattern="/api/v1/reports/export",
    require_auth=True,
    require_any_permission=["reports:export"],
))
```

---

## Token Revocation

Revocation is checked automatically inside `verify_token`. The service supports three levels of revocation:

```python
from shared.security import revoke_token, revoke_user_tokens, is_token_revoked
from shared.security.token_revocation import revoke_tenant_tokens

# Revoke a specific token by JTI (e.g., on logout)
revoke_token(jti=payload["jti"], reason="logout")

# Revoke all tokens for a user (e.g., on password change)
revoke_user_tokens(user_id="user-uuid", reason="password_changed")

# Revoke all tokens for an entire tenant (emergency use)
revoke_tenant_tokens(tenant_id="tenant-uuid", reason="security_breach")

# Manual check
is_revoked, reason = is_token_revoked(jti=jti, user_id=user_id, tenant_id=tenant_id, issued_at=iat)
```

The default backend is in-memory. For multi-instance deployments, replace the singleton in `get_revocation_service()` with a Redis-backed implementation.

---

## Audit Logging

All audit entries are persisted via `AuditLog` (Tortoise ORM) and also emitted to the structured logger. Entries form a SHA-256 hash chain for tamper detection.

```python
from shared.security import audit_log, AuditAction
from shared.security.audit import audit_auth, audit_data_change, audit_security_event

# General purpose
await audit_log(
    tenant_id=principal["tid"],
    user_id=principal["sub"],
    action=AuditAction.TASK_COMPLETED,
    resource_type="task",
    resource_id=task_id,
    ip_address=request.client.host,
)

# Auth events
await audit_auth(tenant_id, user_id, AuditAction.LOGIN_FAILED,
                 success=False, ip_address=ip, error_message="bad password")

# Data change with before/after values
await audit_data_change(tenant_id, user_id, AuditAction.FIELD_UPDATED,
                        resource_type="field", resource_id=field_id,
                        old_value={"name": "Old"}, new_value={"name": "New"})
```

### Querying the audit trail

```python
from shared.security.audit import (
    get_user_audit_trail, get_resource_audit_trail,
    get_security_events, get_failed_logins,
    validate_hash_chain, get_compliance_report, export_audit_logs,
)

# Recent failed logins (last 24 hours)
events = await get_failed_logins(tenant_id, hours=24)

# Validate chain integrity
result = await validate_hash_chain(tenant_id)
print(result.valid, result.errors)

# Generate a GDPR/SOC2/ISO27001 compliance report
report = await get_compliance_report(tenant_id, start_date, end_date, framework="SOC2")
```

---

## Secrets Management

`config.py` provides a `SecretManager` that reads from environment variables by default and falls back gracefully from HashiCorp Vault.

```python
from shared.security.config import get_config, get_jwt_secret, is_production

# Typed config helpers
port = get_config("PORT", default="8080", cast_type=int)
debug = get_config("DEBUG", default="false", cast_type=bool)
origins = get_config("CORS_ALLOWED_ORIGINS", cast_type=list)  # comma-separated

# Common getters
jwt_secret = get_jwt_secret()  # required=True, raises on missing
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `JWT_SECRET_KEY` | Yes (prod) | — | HS256 signing key (min 32 chars in production) |
| `JWT_ALGORITHM` | No | `HS256` | Must be `HS256` |
| `JWT_ISSUER` | No | `sahool-idp` | Expected `iss` claim |
| `JWT_AUDIENCE` | No | `sahool-platform` | Expected `aud` claim |
| `JWT_ACCESS_EXPIRE_MINUTES` | No | `30` | Access token TTL |
| `JWT_REFRESH_EXPIRE_DAYS` | No | `7` | Refresh token TTL |
| `ENVIRONMENT` | No | `development` | `development` / `staging` / `production` |
| `SECRET_BACKEND` | No | `environment` | `environment` or `vault` |
| `VAULT_ADDR` | Vault only | — | HashiCorp Vault address |
| `VAULT_TOKEN` | Vault only | — | Vault token (or use AppRole) |
| `VAULT_ROLE_ID` | Vault only | — | AppRole role ID |
| `VAULT_SECRET_ID` | Vault only | — | AppRole secret ID |

---

## Integration with Services

Standard pattern for a protected FastAPI service:

```python
from fastapi import Depends
from shared.security import get_principal, require, audit_log, AuditAction
from shared.security.deps import TenantID

@router.post("/fields")
async def create_field(
    body: FieldCreate,
    principal: dict = Depends(get_principal),
    tenant_id: TenantID = Depends(),
):
    require(principal, "fieldops:field.create")

    field = await Field.create(**body.model_dump(), tenant_id=tenant_id)

    await audit_log(
        tenant_id=tenant_id,
        user_id=principal["sub"],
        action=AuditAction.FIELD_CREATED,
        resource_type="field",
        resource_id=str(field.id),
    )
    return field
```

---

## Security Notes

- RS256 support has been removed. Only HS256 is accepted. The algorithm whitelist is hardcoded to prevent algorithm confusion attacks.
- `decode_token_unsafe()` skips signature verification. Never use it for authorization decisions.
- The `super_admin` role bypasses all permission and tenant checks. Assign it with care.
- In production, `JWT_SECRET_KEY` must be at least 32 characters or startup raises `RuntimeError`.
- The token revocation service is in-memory by default. Replace the singleton in `get_revocation_service()` with a Redis-backed implementation for multi-instance deployments.
