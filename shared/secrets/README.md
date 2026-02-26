# shared/secrets

Multi-backend secrets management for the SAHOOL platform. Provides a unified
`SecretsManager` interface over environment variables, HashiCorp Vault, AWS
Secrets Manager, and Azure Key Vault, with integrated audit logging and
Prometheus metrics.

## File Structure

```
shared/secrets/
├── __init__.py    # Module entry point; exports SecretKey, get_secrets_manager
├── manager.py     # Unified manager, backend enum, provider implementations
├── vault.py       # HashiCorp Vault client (KV v2, AppRole + token auth)
└── audit.py       # Audit logger, anomaly detection, Prometheus metrics
```

## Key Components

### manager.py

`SecretKey` enum maps logical names to hierarchical paths used across all backends:

| Category | Key (example) | Path |
|----------|--------------|------|
| Database | `DATABASE_PASSWORD` | `database/password` |
| Auth | `JWT_SECRET` | `auth/jwt_secret` |
| AI APIs | `ANTHROPIC_API_KEY` | `external/anthropic_api_key` |
| Satellite | `SENTINEL_HUB_CLIENT_ID` | `external/sentinel_hub_client_id` |
| App | `ENCRYPTION_KEY` | `app/encryption_key` |

`SecretBackend` enum: `ENVIRONMENT`, `VAULT`, `AWS_SECRETS_MANAGER`, `AZURE_KEY_VAULT`.
Backend is selected at runtime via the `SECRET_BACKEND` environment variable.

`SecretsProvider` ABC defines: `connect()`, `disconnect()`, `get_secret()`, `set_secret()`, `delete_secret()`, `health_check()`.

`EnvironmentSecretsProvider` maps `database/password` -> `DATABASE_PASSWORD` env var with
fallback variations (`SAHOOL_DATABASE_PASSWORD`). Best for development.

`get_secrets_manager()` convenience function returns an already-connected provider instance.

### vault.py

Full-featured async Vault client for production deployments.

- **Authentication**: Token-based or AppRole (recommended for production)
- **Auto-renewal**: Background task renews token 10 minutes before expiry; re-authenticates via AppRole on renewal
- **Caching**: In-memory TTL cache (default 5 min) to reduce Vault round-trips
- **KV v2**: All reads/writes use `secrets.kv.v2` API under a configurable `mount_point` and `path_prefix`
- **Batch**: `get_secrets_batch(paths)` fetches multiple paths, returning `None` for missing keys without raising
- **Health**: `health_check()` returns `initialized`, `sealed`, and `version` from Vault's sys endpoint

`VaultConfig` fields are read from environment variables by default; call `VaultConfig.from_env()`.

`get_vault_client()` / `close_vault_client()` manage a module-level singleton.

### audit.py

`SecretAuditLogger` records every access event and detects anomalies in-memory:

| Anomaly | Trigger |
|---------|---------|
| High frequency | Same user+path accessed > `alert_threshold` times (default 100) |
| Brute-force | 5 or more failures within 15 minutes |
| Off-hours | Access between 03:00–06:00 UTC |
| New IP | Access from IP not seen in last 100 events for that user |

`SecretAccessEvent` fields: `access_type`, `secret_path`, `backend`, `result`, `user`, `source_ip`, `service`, `duration_ms`.

Prometheus counters/histograms exported when `prometheus_client` is installed:
- `sahool_secret_access_total` (backend, access_type, result, service)
- `sahool_secret_access_duration_seconds`
- `sahool_secret_access_failures_total`

## Usage Example

```python
from shared.secrets import get_secrets_manager, SecretKey
from shared.secrets.vault import VaultClient, VaultConfig
from shared.secrets.audit import SecretAccessEvent, SecretAccessType, audit_secret_access

# Auto-detect backend (reads SECRET_BACKEND env var)
secrets = get_secrets_manager()

# Get standard platform secret
db_password = await secrets.get_secret(SecretKey.DATABASE_PASSWORD)
jwt_secret = await secrets.get_secret(SecretKey.JWT_SECRET)

# Custom path
api_key = await secrets.get_secret("external/my_custom_key")

# Production: HashiCorp Vault with AppRole
config = VaultConfig(
    address="https://vault.sahool.app:8200",
    role_id="prod-role-id",
    secret_id="prod-secret-id",
    mount_point="secret",
    path_prefix="sahool/prod",
)
client = VaultClient(config)
await client.connect()
creds = await client.get_secret("database/credentials")  # returns dict
password = await client.get_secret("database/credentials", "password")

# Batch fetch
secrets_map = await client.get_secrets_batch([
    "database/credentials",
    "auth/jwt_secret",
    "external/anthropic_api_key",
])

# Audit logging
event = SecretAccessEvent(
    access_type=SecretAccessType.READ,
    secret_path="database/credentials",
    backend="vault",
    user="field-management-service",
    service="field-management-service",
)
await audit_secret_access(event)

await client.disconnect()
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_BACKEND` | `environment` | Active backend: `environment`, `vault`, `aws_secrets_manager`, `azure_key_vault` |
| `VAULT_ADDR` | `http://localhost:8200` | Vault server URL |
| `VAULT_TOKEN` | — | Token auth (dev/staging) |
| `VAULT_ROLE_ID` | — | AppRole role ID (production) |
| `VAULT_SECRET_ID` | — | AppRole secret ID (production) |
| `VAULT_NAMESPACE` | — | Vault Enterprise namespace |
| `VAULT_MOUNT_POINT` | `secret` | KV v2 mount point |
| `VAULT_PATH_PREFIX` | `sahool` | Path prefix for all secrets |
