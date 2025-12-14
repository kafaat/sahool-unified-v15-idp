# Security Fix: JWT Key Configuration Changes

## Summary
This document describes the security improvements made to remove hardcoded private key file paths from Docker Compose configurations.

## Problem
The CI security checks detected patterns related to "private_key" in docker-compose files at:
- `sahool-unified-v15.2-v8.3-kernel-v14.1/docker-compose.yml` (lines 46, 55, 151)
- `sahool-unified-v15.2-v8.3-kernel-v14.1/infrastructure/docker/docker-compose.yml` (line 117)

These references pointed to hardcoded file paths for JWT private/public keys, which posed security risks.

## Solution
Replaced file path references with environment variables for better security and flexibility.

### Changes Made

#### 1. Docker Compose Files
**Before:**
```yaml
environment:
  JWT_PRIVATE_KEY_PATH: /run/secrets/jwt_private_key
  JWT_PUBLIC_KEY_PATH: /run/secrets/jwt_public_key
secrets:
  - jwt_private_key
  - jwt_public_key
secrets:
  jwt_private_key:
    file: ./infrastructure/secrets/jwt_private.pem
```

**After:**
```yaml
environment:
  JWT_PRIVATE_KEY: ${JWT_PRIVATE_KEY}
  JWT_PUBLIC_KEY: ${JWT_PUBLIC_KEY}
# No more secrets section or file references
```

#### 2. Application Code Updates
Updated `auth-service` and `api-gateway` to support both:
- Direct environment variables (preferred)
- File paths (backward compatibility)

**auth-service/src/index.ts:**
```typescript
// Support both environment variable directly OR file path
let privateKey: string;
let publicKey: string;

if (process.env.JWT_PRIVATE_KEY && process.env.JWT_PUBLIC_KEY) {
  // Keys provided directly as environment variables (preferred for security)
  privateKey = process.env.JWT_PRIVATE_KEY.replace(/\\n/g, '\n');
  publicKey = process.env.JWT_PUBLIC_KEY.replace(/\\n/g, '\n');
} else {
  // Fallback to file paths (for backward compatibility)
  const JWT_PRIVATE_KEY_PATH = process.env.JWT_PRIVATE_KEY_PATH || "./keys/private.pem";
  const JWT_PUBLIC_KEY_PATH = process.env.JWT_PUBLIC_KEY_PATH || "./keys/public.pem";
  privateKey = fs.readFileSync(JWT_PRIVATE_KEY_PATH, "utf8");
  publicKey = fs.readFileSync(JWT_PUBLIC_KEY_PATH, "utf8");
}
```

#### 3. Security Infrastructure
- **Added `.gitignore`** to exclude sensitive files: `*.pem`, `*.key`, `secrets/`, etc.
- **Added `.env.example`** as a template for required environment variables
- **Updated `docs/SECURITY.md`** with comprehensive JWT key setup instructions

## How to Use

### Development Setup
1. Generate RSA key pair:
   ```bash
   openssl genrsa -out jwt_private.pem 2048
   openssl rsa -in jwt_private.pem -pubout -out jwt_public.pem
   ```

2. Set environment variables:
   ```bash
   export JWT_PRIVATE_KEY=$(awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' jwt_private.pem)
   export JWT_PUBLIC_KEY=$(awk 'NF {sub(/\r/, ""); printf "%s\\n",$0;}' jwt_public.pem)
   ```

3. Or create `.env` file:
   ```bash
   cp .env.example .env
   # Edit .env and add your JWT keys
   ```

### Production Setup
Use a secret manager:
- **Kubernetes:** Store as secrets, mount as environment variables
- **AWS:** Use AWS Secrets Manager
- **Azure:** Use Azure Key Vault
- **HashiCorp:** Use Vault

## Security Benefits
1. ✅ No hardcoded file paths in version control
2. ✅ Keys can be rotated without code changes
3. ✅ Support for secret managers in production
4. ✅ `.gitignore` prevents accidental key commits
5. ✅ Backward compatible with existing file-based setups

## Migration Path
For existing deployments using file-based keys:
1. Keep existing setup (backward compatible)
2. Gradually migrate to environment variables
3. Update CI/CD pipelines to use GitHub Secrets or equivalent

## Verification
Run these commands to verify the setup:
```bash
# No embedded private keys
grep -r "BEGIN.*PRIVATE KEY" --include="*.yml" . | grep -v ".github"

# No sensitive files
find . -name "*.pem" -o -name "*.key"

# Docker Compose validation
docker compose config --quiet
```

## References
- [SECURITY.md](docs/SECURITY.md) - Complete security documentation
- [.env.example](.env.example) - Environment variable template
