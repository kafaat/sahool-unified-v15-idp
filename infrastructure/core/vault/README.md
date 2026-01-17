# SAHOOL Vault Setup

HashiCorp Vault for secrets management in SAHOOL platform.

## Development Setup

```bash
# Start Vault in dev mode
docker compose -f infra/vault/docker-compose.vault.yml up -d

# Set environment variables
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=dev-root-token

# Verify
vault status
```

## Access

- **UI**: http://localhost:8200/ui
- **Token**: `dev-root-token` (development only!)

## Secret Paths

| Path                          | Description               |
| ----------------------------- | ------------------------- |
| `secret/database/postgres`    | PostgreSQL credentials    |
| `secret/auth/jwt`             | JWT signing configuration |
| `secret/messaging/nats`       | NATS connection           |
| `secret/cache/redis`          | Redis connection          |
| `secret/external/openweather` | OpenWeather API           |
| `secret/external/sentinel`    | Sentinel Hub API          |

## Usage in Code

```python
from shared.libs.security.vault_client import from_env

# Create client from environment
vault = from_env()

# Read secrets
db_creds = vault.read_kv("database/postgres")
print(db_creds["username"])

# With ENV fallback during migration
jwt_secret = vault.get_secret_or_env(
    "auth/jwt", "secret_key", "JWT_SECRET_KEY"
)
```

## Production Considerations

1. **Never use dev mode** - Use proper unsealing
2. **Use AppRole auth** - Not root tokens
3. **Enable audit logging** - Required for compliance
4. **High availability** - Use Raft or Consul backend
5. **Auto-unseal** - Use cloud KMS or HSM

## AppRole Setup (Production)

```bash
# Enable AppRole
vault auth enable approle

# Create policy
vault policy write sahool-app - <<EOF
path "secret/data/*" {
  capabilities = ["read"]
}
EOF

# Create role
vault write auth/approle/role/sahool-service \
    token_policies="sahool-app" \
    token_ttl=1h \
    token_max_ttl=4h

# Get role_id and secret_id
vault read auth/approle/role/sahool-service/role-id
vault write -f auth/approle/role/sahool-service/secret-id
```
