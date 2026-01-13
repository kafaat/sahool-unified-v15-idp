# SAHOOL Platform Security Hardening Guide

**Version:** 1.0
**Last Updated:** 2026-01-07
**Platform:** SAHOOL Unified v15

---

## Table of Contents

1. [Overview](#overview)
2. [Security Architecture](#security-architecture)
3. [Hardening Scripts](#hardening-scripts)
4. [Component Hardening](#component-hardening)
5. [Security Policies](#security-policies)
6. [Vulnerability Management](#vulnerability-management)
7. [Monitoring and Auditing](#monitoring-and-auditing)
8. [Incident Response](#incident-response)
9. [Best Practices](#best-practices)
10. [Compliance](#compliance)

---

## Overview

This guide provides comprehensive security hardening procedures for the SAHOOL platform. It covers all infrastructure components, containers, and services with step-by-step instructions for implementing security best practices.

### Security Objectives

- **Confidentiality**: Protect sensitive data from unauthorized access
- **Integrity**: Ensure data accuracy and prevent unauthorized modifications
- **Availability**: Maintain system uptime and resilience
- **Compliance**: Meet industry standards and regulatory requirements

### Security Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimum necessary access rights
3. **Zero Trust**: Never trust, always verify
4. **Security by Design**: Built-in security from the start
5. **Continuous Monitoring**: Real-time threat detection

---

## Security Architecture

### Security Layers

```
┌─────────────────────────────────────────────────────────────┐
│                        Users / Clients                       │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                    Network Layer Security                    │
│  • TLS/SSL Encryption      • Rate Limiting                  │
│  • Firewall Rules          • DDoS Protection                │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  API Gateway (Kong/Envoy)                    │
│  • Authentication          • Authorization                   │
│  • API Key Management      • Request Validation             │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Application Services                       │
│  • Input Validation        • Output Encoding                │
│  • Session Management      • Error Handling                 │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  Container Security Layer                    │
│  • Non-root Users          • Read-only Filesystems          │
│  • Resource Limits         • Security Profiles              │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer Security                        │
│  • Encryption at Rest      • Encryption in Transit          │
│  • Access Control          • Audit Logging                  │
└─────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Security                      │
│  • OS Hardening            • Network Segmentation           │
│  • Patch Management        • Backup & Recovery              │
└─────────────────────────────────────────────────────────────┘
```

### Network Architecture

```
Internet
   │
   ├─── Firewall / WAF
   │         │
   │         ├─── Load Balancer (HTTPS)
   │         │         │
   │         │         ├─── API Gateway (Kong)
   │         │         │         │
   │         │         │         ├─── Internal Network (Microservices)
   │         │         │         │         │
   │         │         │         │         ├─── PostgreSQL (TLS)
   │         │         │         │         ├─── Redis (TLS + Auth)
   │         │         │         │         ├─── NATS (TLS + NKeys)
   │         │         │         │         └─── MinIO (TLS + Auth)
```

---

## Hardening Scripts

### Available Scripts

All hardening scripts are located in `/home/user/sahool-unified-v15-idp/scripts/security/`:

| Script                    | Purpose                       | Usage                              |
| ------------------------- | ----------------------------- | ---------------------------------- |
| `harden-postgres.sh`      | PostgreSQL security hardening | `./harden-postgres.sh --full`      |
| `harden-redis.sh`         | Redis security hardening      | `./harden-redis.sh --full`         |
| `harden-nats.sh`          | NATS security hardening       | `./harden-nats.sh --full`          |
| `harden-docker.sh`        | Docker security hardening     | `sudo ./harden-docker.sh --full`   |
| `audit-security.sh`       | Comprehensive security audit  | `./audit-security.sh --full`       |
| `scan-vulnerabilities.sh` | Vulnerability scanning        | `./scan-vulnerabilities.sh --full` |
| `rotate-secrets.sh`       | Secret rotation               | `./rotate-secrets.sh --all`        |

### Quick Start

```bash
# 1. Make scripts executable
chmod +x /home/user/sahool-unified-v15-idp/scripts/security/*.sh

# 2. Run comprehensive security audit (recommended first step)
./scripts/security/audit-security.sh --full

# 3. Review audit report
cat reports/security/security-audit-*.md

# 4. Run hardening scripts
./scripts/security/harden-postgres.sh --full
./scripts/security/harden-redis.sh --full
./scripts/security/harden-nats.sh --full
sudo ./scripts/security/harden-docker.sh --full

# 5. Run vulnerability scan
./scripts/security/scan-vulnerabilities.sh --full

# 6. Verify changes with another audit
./scripts/security/audit-security.sh --full
```

---

## Component Hardening

### PostgreSQL Hardening

#### Authentication

```bash
# Enable SCRAM-SHA-256 password encryption
docker exec sahool-postgres psql -U sahool -d sahool -c \
  "ALTER SYSTEM SET password_encryption = 'scram-sha-256';"

# Update pg_hba.conf for strict authentication
cat > /path/to/pg_hba.conf <<EOF
# TYPE  DATABASE        USER            ADDRESS                 METHOD
local   all             all                                     scram-sha-256
hostssl all             all             0.0.0.0/0               scram-sha-256 clientcert=verify-full
EOF
```

#### SSL/TLS Configuration

```bash
# Enable SSL in postgresql.conf
cat >> /path/to/postgresql.conf <<EOF
ssl = on
ssl_cert_file = '/var/lib/postgresql/server.crt'
ssl_key_file = '/var/lib/postgresql/server.key'
ssl_ca_file = '/var/lib/postgresql/root.crt'
ssl_min_protocol_version = 'TLSv1.2'
ssl_ciphers = 'HIGH:MEDIUM:+3DES:!aNULL'
ssl_prefer_server_ciphers = on
EOF
```

#### Connection Limits

```sql
-- Set connection limits
ALTER SYSTEM SET max_connections = 250;
ALTER SYSTEM SET superuser_reserved_connections = 5;
ALTER SYSTEM SET statement_timeout = '30s';
ALTER SYSTEM SET idle_in_transaction_session_timeout = '10min';

-- Reload configuration
SELECT pg_reload_conf();
```

#### Audit Logging

```sql
-- Enable comprehensive logging
ALTER SYSTEM SET log_connections = on;
ALTER SYSTEM SET log_disconnections = on;
ALTER SYSTEM SET log_line_prefix = '%t [%p]: user=%u,db=%d,app=%a,client=%h ';
ALTER SYSTEM SET log_statement = 'ddl';
ALTER SYSTEM SET log_min_duration_statement = 1000;
```

#### Row Level Security

```sql
-- Enable RLS on sensitive tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY user_access_policy ON users
  FOR ALL
  TO app_user
  USING (user_id = current_setting('app.current_user_id')::INTEGER);
```

### Redis Hardening

#### Authentication

```bash
# Set strong password
redis-cli CONFIG SET requirepass "$(openssl rand -base64 32)"

# Configure ACL users
redis-cli ACL SETUSER admin on >admin_password ~* &* +@all
redis-cli ACL SETUSER app on >app_password ~app:* &* +@all -@dangerous
redis-cli ACL SETUSER readonly on >readonly_password ~* &* +@read -@write
```

#### Rename Dangerous Commands

```bash
# Add to redis.conf
cat >> /etc/redis/redis.conf <<EOF
rename-command FLUSHDB "FLUSHDB_MY_SECRET_$(openssl rand -hex 16)"
rename-command FLUSHALL "FLUSHALL_MY_SECRET_$(openssl rand -hex 16)"
rename-command CONFIG "CONFIG_MY_SECRET_$(openssl rand -hex 16)"
rename-command KEYS ""
rename-command SHUTDOWN "SHUTDOWN_MY_SECRET_$(openssl rand -hex 16)"
EOF
```

#### TLS Configuration

```bash
# Enable TLS
cat >> /etc/redis/redis.conf <<EOF
port 0
tls-port 6379
tls-cert-file /etc/redis/certs/redis.crt
tls-key-file /etc/redis/certs/redis.key
tls-ca-cert-file /etc/redis/certs/ca.crt
tls-protocols "TLSv1.2 TLSv1.3"
tls-prefer-server-ciphers yes
tls-auth-clients yes
EOF
```

#### Memory and Persistence

```bash
# Configure memory limits
cat >> /etc/redis/redis.conf <<EOF
maxmemory 512mb
maxmemory-policy allkeys-lru
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
EOF
```

### NATS Hardening

#### NKey Authentication

```bash
# Generate NKeys using hardening script
./scripts/security/harden-nats.sh --generate-nkeys

# NKeys are stored in: /home/user/sahool-unified-v15-idp/scripts/nats/keys/

# Configure services to use NKeys
cat > /path/to/service-config.yaml <<EOF
nats:
  url: nats://nats:4222
  credentials_file: /run/secrets/nats_creds
  tls:
    enabled: true
    cert_file: /certs/client.crt
    key_file: /certs/client.key
    ca_file: /certs/ca.crt
EOF
```

#### TLS Configuration

```bash
# Add to nats-server.conf
cat >> /etc/nats/nats-server.conf <<EOF
tls {
  cert_file: "/etc/nats/certs/nats.crt"
  key_file: "/etc/nats/certs/nats.key"
  ca_file: "/etc/nats/certs/ca.crt"
  verify: true
  timeout: 2
  min_version: "1.2"
}
EOF
```

#### JetStream Security

```bash
# Configure JetStream with security
cat >> /etc/nats/nats-server.conf <<EOF
jetstream {
  store_dir: "/data/jetstream"
  max_memory_store: 1GB
  max_file_store: 10GB
  domain: "sahool"
}

accounts {
  APP: {
    jetstream: {
      max_mem: 512MB
      max_file: 5GB
      max_streams: 100
      max_consumers: 1000
    }
  }
}
EOF
```

### Docker Hardening

#### Daemon Configuration

```json
{
  "icc": false,
  "userns-remap": "default",
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
```

#### Container Best Practices

```yaml
# Secure container configuration example
services:
  secure-service:
    image: your-image:tag
    user: "1000:1000" # Non-root user
    read_only: true # Read-only filesystem

    security_opt:
      - no-new-privileges:true
      - seccomp=/etc/docker/seccomp-profile.json
      - apparmor=docker-sahool

    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE

    tmpfs:
      - /tmp:noexec,nosuid,size=100m

    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
          pids: 100
```

---

## Security Policies

Security policies are defined in `/home/user/sahool-unified-v15-idp/infrastructure/security/security-policies.yaml`.

### Key Policies

#### Password Policy

- Minimum 12 characters
- Requires uppercase, lowercase, numbers, special characters
- 90-day rotation
- Password history: 5
- Account lockout: 5 failed attempts

#### Session Policy

- Timeout: 30 minutes
- Absolute timeout: 12 hours
- Maximum concurrent sessions: 3
- Secure cookies with HttpOnly and SameSite

#### Encryption Policy

- At rest: AES-256-GCM
- In transit: TLS 1.2+
- Key rotation: 90 days

---

## Vulnerability Management

### Scanning Schedule

| Scan Type              | Frequency | Tool            |
| ---------------------- | --------- | --------------- |
| Container Images       | Daily     | Trivy, Grype    |
| Dependencies (npm)     | Weekly    | npm audit, Snyk |
| Dependencies (Python)  | Weekly    | Safety          |
| Secrets in Code        | On commit | Gitleaks        |
| Infrastructure as Code | Weekly    | Checkov         |

### Running Scans

```bash
# Full vulnerability scan
./scripts/security/scan-vulnerabilities.sh --full

# Container images only
./scripts/security/scan-vulnerabilities.sh --containers

# Dependencies only
./scripts/security/scan-vulnerabilities.sh --dependencies

# Secret detection
./scripts/security/scan-vulnerabilities.sh --secrets
```

### Remediation SLA

| Severity | Response Time | Patch Window |
| -------- | ------------- | ------------ |
| Critical | 24 hours      | 7 days       |
| High     | 48 hours      | 30 days      |
| Medium   | 1 week        | 90 days      |
| Low      | 1 month       | 180 days     |

---

## Monitoring and Auditing

### Security Events to Monitor

1. **Authentication Events**
   - Failed login attempts
   - Successful logins from new locations
   - MFA bypasses
   - Password changes

2. **Authorization Events**
   - Access denied
   - Privilege escalation attempts
   - Role changes

3. **Infrastructure Events**
   - Configuration changes
   - Container starts/stops
   - Network connections
   - Resource limit violations

4. **Data Events**
   - Database queries (sensitive tables)
   - File access (sensitive data)
   - Data exports
   - Data modifications

### Audit Logging

```bash
# Enable audit logging for PostgreSQL
docker exec sahool-postgres psql -U sahool -d sahool <<SQL
CREATE EXTENSION IF NOT EXISTS pgaudit;
ALTER SYSTEM SET pgaudit.log = 'write, ddl';
ALTER SYSTEM SET pgaudit.log_catalog = off;
ALTER SYSTEM SET pgaudit.log_parameter = on;
SELECT pg_reload_conf();
SQL
```

### Log Retention

- Security logs: 365 days
- Audit logs: 730 days
- Application logs: 90 days
- Debug logs: 30 days

---

## Incident Response

### Incident Classification

| Level | Description | Examples                         | Response  |
| ----- | ----------- | -------------------------------- | --------- |
| P0    | Critical    | Data breach, system compromise   | Immediate |
| P1    | High        | Security vulnerability exploited | 1 hour    |
| P2    | Medium      | Suspicious activity detected     | 4 hours   |
| P3    | Low         | Policy violation                 | 24 hours  |

### Response Procedure

1. **Detection**
   - Alert triggered
   - Log analysis
   - User report

2. **Containment**
   - Isolate affected systems
   - Block malicious IPs
   - Revoke compromised credentials

3. **Eradication**
   - Remove malware
   - Patch vulnerabilities
   - Close security gaps

4. **Recovery**
   - Restore from backups
   - Verify system integrity
   - Resume normal operations

5. **Post-Incident**
   - Root cause analysis
   - Documentation
   - Lessons learned
   - Process improvements

### Incident Response Team

- **Security Team**: Lead investigation
- **DevOps Team**: System recovery
- **Development Team**: Code fixes
- **Legal Team**: Compliance and reporting
- **Communications**: Stakeholder updates

---

## Best Practices

### Development

1. **Secure Coding**
   - Input validation
   - Output encoding
   - Parameterized queries
   - Error handling
   - Secure session management

2. **Code Review**
   - Security-focused reviews
   - Automated SAST scanning
   - Dependency checking

3. **Testing**
   - Unit tests for security functions
   - Integration tests
   - Penetration testing

### Deployment

1. **Pre-deployment**
   - Security scan
   - Vulnerability assessment
   - Configuration review

2. **Deployment**
   - Blue-green deployment
   - Canary releases
   - Rollback plan

3. **Post-deployment**
   - Smoke tests
   - Security monitoring
   - Incident readiness

### Operations

1. **Patch Management**
   - Regular updates
   - Emergency patches
   - Testing before deployment

2. **Backup and Recovery**
   - Daily backups
   - Offsite storage
   - Regular restore testing

3. **Access Management**
   - Least privilege
   - Regular access reviews
   - MFA enforcement

---

## Compliance

### CIS Benchmarks

- **Docker CIS Benchmark v1.4.0**
  - Score target: 90%+
  - Audit frequency: Monthly
  - Tool: Docker Bench Security

- **PostgreSQL CIS Benchmark v1.0**
  - Score target: 85%+
  - Audit frequency: Monthly

### Security Standards

- **OWASP Top 10 (2021)**
  - Regular assessments
  - Mitigation tracking
  - Developer training

- **NIST Cybersecurity Framework**
  - Identify
  - Protect
  - Detect
  - Respond
  - Recover

### Compliance Checklist

- [ ] All services use TLS/SSL
- [ ] Strong authentication enabled
- [ ] Secrets properly managed
- [ ] Regular vulnerability scans
- [ ] Audit logging enabled
- [ ] Backup and recovery tested
- [ ] Incident response plan documented
- [ ] Security training completed
- [ ] Access reviews conducted
- [ ] Compliance reports generated

---

## Additional Resources

### Documentation

- [SECURITY.md](/home/user/sahool-unified-v15-idp/docs/SECURITY.md) - Security overview
- [SECRETS_MANAGEMENT.md](/home/user/sahool-unified-v15-idp/docs/SECRETS_MANAGEMENT.md) - Secrets management guide
- [TLS_CONFIGURATION.md](/home/user/sahool-unified-v15-idp/docs/TLS_CONFIGURATION.md) - TLS setup guide

### Scripts

- `/home/user/sahool-unified-v15-idp/scripts/security/` - Security hardening scripts
- `/home/user/sahool-unified-v15-idp/infrastructure/security/` - Security policies

### External Resources

- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [PostgreSQL Security](https://www.postgresql.org/docs/current/security.html)
- [Redis Security](https://redis.io/docs/management/security/)
- [NATS Security](https://docs.nats.io/running-a-nats-service/configuration/securing_nats)

---

## Support and Maintenance

### Regular Tasks

| Task                 | Frequency | Owner           |
| -------------------- | --------- | --------------- |
| Security audit       | Monthly   | Security Team   |
| Vulnerability scan   | Daily     | DevOps          |
| Certificate rotation | Quarterly | DevOps          |
| Secret rotation      | Quarterly | Security Team   |
| Access review        | Quarterly | Security Team   |
| Penetration test     | Annually  | External Vendor |

### Contact

For security issues or questions:

- Email: security@sahool.local
- Slack: #security-team
- On-call: security-oncall@sahool.local

---

**Last Updated:** 2026-01-07
**Next Review:** 2026-04-07
