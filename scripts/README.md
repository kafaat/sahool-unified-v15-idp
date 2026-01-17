# SAHOOL Scripts

## Overview

سكريبتات التشغيل والتوليد والأمان لمنصة سهول.

---

## Structure

```
scripts/
├── bootstrap.sh                    # Platform bootstrap script
├── generate_sahool_all_in_one.sh   # Full platform generator
├── generate_sahool_field_enterprise.sh  # Field enterprise generator
├── db_health_check.sh              # Database health monitoring
│
├── generators/                     # Code generators
│   ├── generate_design_tokens.py   # Design token generation
│   └── generate_infra.py           # Infrastructure generation
│
└── security/                       # Security scripts
    ├── check-secrets.sh            # Secret leak detection
    ├── generate-certs.sh           # TLS certificate generation
    └── rotate-secrets.sh           # Secret rotation
```

---

## Main Scripts

### bootstrap.sh

Platform bootstrap and initialization.

```bash
# Full bootstrap
./scripts/bootstrap.sh

# Specific environment
./scripts/bootstrap.sh --env production

# Skip dependency check
./scripts/bootstrap.sh --skip-deps
```

**Actions:**

- Install dependencies
- Initialize databases
- Generate certificates
- Start core services

---

### generate_sahool_all_in_one.sh

Generate complete SAHOOL platform structure.

```bash
# Generate full platform
./scripts/generate_sahool_all_in_one.sh

# With custom output directory
./scripts/generate_sahool_all_in_one.sh --output ./new-project
```

**Generates:**

- All microservices
- Frontend applications
- Infrastructure configs
- Docker Compose files

---

### generate_sahool_field_enterprise.sh

Generate field enterprise edition.

```bash
./scripts/generate_sahool_field_enterprise.sh
```

**Features:**

- Field management services
- Satellite integration
- IoT sensor support
- Weather services

---

## Generators

### generate_design_tokens.py

Generate design tokens from Figma or config.

```bash
python scripts/generators/generate_design_tokens.py

# With custom input
python scripts/generators/generate_design_tokens.py --config tokens.json
```

**Output:**

- `packages/design-system/tokens/`
- CSS custom properties
- TypeScript types

---

### generate_infra.py

Generate infrastructure configurations.

```bash
python scripts/generators/generate_infra.py

# For specific environment
python scripts/generators/generate_infra.py --env staging
```

**Generates:**

- Docker Compose files
- Kubernetes manifests
- Environment files

---

## Monitoring & Operations Scripts

### db_health_check.sh

Comprehensive database health monitoring for PostgreSQL and PgBouncer.

```bash
# Basic health check
./scripts/db_health_check.sh

# JSON output for monitoring systems
./scripts/db_health_check.sh --json

# Check with custom thresholds
./scripts/db_health_check.sh --disk-warning 85 --conn-critical 90

# Include replication lag check
./scripts/db_health_check.sh --check-replication
```

**Checks:**

- PostgreSQL connectivity
- PgBouncer pool status
- Active connections count
- Long-running queries (>30s)
- Disk space usage
- Replication lag (optional)
- Database size

**Exit Codes:**

- `0` = Healthy
- `1` = Warning
- `2` = Critical

**Kubernetes Integration:**

```yaml
livenessProbe:
  exec:
    command: ["/scripts/db_health_check.sh", "--json"]
  initialDelaySeconds: 30
  periodSeconds: 30
  timeoutSeconds: 10
  failureThreshold: 3
```

---

## Security Scripts

### check-secrets.sh

Scan for secret leaks in codebase.

```bash
./scripts/security/check-secrets.sh

# Specific directory
./scripts/security/check-secrets.sh apps/

# Verbose output
./scripts/security/check-secrets.sh --verbose
```

**Checks for:**

- API keys
- Passwords
- Private keys
- Access tokens

---

### generate-certs.sh

Generate TLS certificates.

```bash
# Development certs
./scripts/security/generate-certs.sh --dev

# Production (Let's Encrypt)
./scripts/security/generate-certs.sh --production --domain sahool.app

# Custom CA
./scripts/security/generate-certs.sh --ca /path/to/ca.pem
```

**Generates:**

- `tools/security/certs/server.crt`
- `tools/security/certs/server.key`
- `tools/security/certs/ca.crt`

---

### rotate-secrets.sh

Rotate secrets and credentials.

```bash
# Rotate all secrets
./scripts/security/rotate-secrets.sh

# Specific secret
./scripts/security/rotate-secrets.sh --secret JWT_SECRET_KEY

# Dry run
./scripts/security/rotate-secrets.sh --dry-run
```

**Rotates:**

- JWT secrets
- Database passwords
- API keys
- Service tokens

---

## Usage Examples

### Development Setup

```bash
# 1. Clone repository
git clone https://github.com/kafaat/sahool-unified-v15-idp

# 2. Bootstrap platform
./scripts/bootstrap.sh --env development

# 3. Generate dev certs
./scripts/security/generate-certs.sh --dev
```

### CI/CD Pipeline

```bash
# 1. Check for secret leaks
./scripts/security/check-secrets.sh

# 2. Generate infrastructure
python scripts/generators/generate_infra.py --env staging

# 3. Deploy (in CI)
docker compose up -d
```

### Security Audit

```bash
# 1. Check secrets
./scripts/security/check-secrets.sh --verbose

# 2. Rotate if needed
./scripts/security/rotate-secrets.sh

# 3. Regenerate certs
./scripts/security/generate-certs.sh --production
```

---

## Related Documentation

- [Docker Guide](../docs/DOCKER.md)
- [Infrastructure](../infra/README.md)
- [Tools](../tools/README.md)

---

<p align="center">
  <sub>SAHOOL Scripts v15.5</sub>
  <br>
  <sub>December 2025</sub>
</p>
