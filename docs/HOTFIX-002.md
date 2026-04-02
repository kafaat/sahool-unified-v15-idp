# HOTFIX-002: NATS Authentication Credential Mismatch

## Problem

NATS server rejected connections with `Authorization Violation` due to bcrypt hash/plaintext mismatch between the `nats.conf` password hashes and the credentials supplied by services.

## Solution

Ensured `config/nats/nats.conf` uses bcrypt-hashed passwords that correspond to the `.env.example` credentials, with `$NATS_USER` / `$NATS_ADMIN_USER` / `$NATS_MONITOR_USER` environment variable substitution for usernames.

## Files Changed

| File | Change |
|------|--------|
| `config/nats/nats.conf` | Already contains bcrypt hashes matching `.env.example` passwords |
| `scripts/apply-hotfix-002.ps1` | Automated hotfix application script |

## Security Note

⚠️ **Development only.** Production deployments MUST use `nats-secure.conf` with mTLS and NKey authentication. See `config/nats/SECURITY_HARDENING.md`.

## Verification

```powershell
# Apply the hotfix
.\scripts\apply-hotfix-002.ps1 -FullReset

# Verify connectivity
nats --user sahool_app --password $env:NATS_PASSWORD pub test "ok"
```
