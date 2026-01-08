# SAHOOL Certificate Rotation - Quick Start Guide

## Overview

This guide provides a quick start for setting up automated certificate rotation for the SAHOOL platform. The system automatically manages TLS certificates for PostgreSQL, PgBouncer, Redis, NATS, and Kong Gateway.

## What Was Created

### Scripts (`/scripts/certs/`)

| File | Purpose | Executable |
|------|---------|------------|
| `generate-certs.sh` | Generate and manage TLS certificates | ✓ |
| `validate-certs.sh` | Validate certificates and check expiration | ✓ |
| `rotate-certs.sh` | Automate certificate rotation | ✓ |
| `README.md` | Script documentation | - |

### Infrastructure (`/infrastructure/certs/`)

| File | Purpose | Type |
|------|---------|------|
| `cert-rotation.service` | Systemd service unit | systemd |
| `cert-rotation.timer` | Systemd timer (daily at 2 AM) | systemd |
| `cert-rotation.cron` | Alternative cron configuration | cron |
| `README.md` | Infrastructure setup guide | - |

### Documentation (`/docs/`)

| File | Purpose |
|------|---------|
| `CERTIFICATE_ROTATION.md` | Complete rotation guide (22 KB) |
| `CERTIFICATE_ROTATION_QUICKSTART.md` | This quick start guide |

## 5-Minute Setup

### Step 1: Generate Initial Certificates

```bash
cd /home/user/sahool-unified-v15-idp

# Generate certificates for all services
./scripts/certs/generate-certs.sh

# Expected output:
# ═══════════════════════════════════════════════════════════════════════════════
#   SAHOOL Certificate Generation
#   Platform: SAHOOL v16.0.0
# ═══════════════════════════════════════════════════════════════════════════════
# [INFO] OpenSSL version: OpenSSL X.X.X
# [STEP] Generating Certificate Authority (CA)
# [SUCCESS] CA certificate generated successfully
# [STEP] Generating certificate for: postgres
# [SUCCESS] Certificate for postgres generated successfully
# ...
```

### Step 2: Validate Certificates

```bash
# Check all certificates
./scripts/certs/validate-certs.sh

# Expected output:
# ═══════════════════════════════════════════════════════════════════════════════
#   SAHOOL Certificate Validation Report
# ═══════════════════════════════════════════════════════════════════════════════
# [SUCCESS] postgres: Certificate valid for 825 days
# [SUCCESS] pgbouncer: Certificate valid for 825 days
# [SUCCESS] redis: Certificate valid for 825 days
# [SUCCESS] nats: Certificate valid for 825 days
# [SUCCESS] kong: Certificate valid for 825 days
#
# Summary:
#   Total Certificates:   5
#   Valid:                5
#   Warnings:             0
#   Errors/Critical:      0
```

### Step 3: Enable Automated Rotation

**Choose ONE of the following options:**

#### Option A: Systemd Timer (Recommended)

```bash
# Copy systemd files
sudo cp infrastructure/certs/cert-rotation.service /etc/systemd/system/
sudo cp infrastructure/certs/cert-rotation.timer /etc/systemd/system/

# Update paths (if not using /opt/sahool)
sudo sed -i 's|/opt/sahool|/home/user/sahool-unified-v15-idp|g' /etc/systemd/system/cert-rotation.service

# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable cert-rotation.timer
sudo systemctl start cert-rotation.timer

# Verify
sudo systemctl status cert-rotation.timer
```

#### Option B: Cron Job

```bash
# Install cron configuration
sudo cp infrastructure/certs/cert-rotation.cron /etc/cron.d/sahool-cert-rotation
sudo chmod 644 /etc/cron.d/sahool-cert-rotation

# Update paths
sudo sed -i 's|/opt/sahool|/home/user/sahool-unified-v15-idp|g' /etc/cron.d/sahool-cert-rotation

# Verify
cat /etc/cron.d/sahool-cert-rotation
```

### Step 4: Configure Notifications (Optional)

```bash
# Create configuration file
sudo tee /etc/default/sahool-certs <<EOF
# Rotation threshold (days before expiration)
ROTATION_THRESHOLD_DAYS=30

# Email notifications
NOTIFICATION_EMAIL=admin@example.com

# Slack webhook (optional)
# SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Backup retention
BACKUP_RETENTION=10

# Unattended mode (no prompts)
UNATTENDED=1
EOF

sudo chmod 600 /etc/default/sahool-certs
```

### Step 5: Test the System

```bash
# Test rotation in dry-run mode
./scripts/certs/rotate-certs.sh --dry-run

# Expected output:
# ═══════════════════════════════════════════════════════════════════════════════
#   SAHOOL Certificate Rotation
#   Platform: SAHOOL v16.0.0
#   Mode: DRY RUN (no changes will be made)
# ═══════════════════════════════════════════════════════════════════════════════
# [STEP] Checking certificate expiration status
# [INFO] postgres: Certificate valid for 825 days, no rotation needed
# [INFO] pgbouncer: Certificate valid for 825 days, no rotation needed
# [INFO] redis: Certificate valid for 825 days, no rotation needed
# [INFO] nats: Certificate valid for 825 days, no rotation needed
# [INFO] kong: Certificate valid for 825 days, no rotation needed
# [SUCCESS] No certificates need rotation at this time
```

## Daily Operations

### Check Certificate Status

```bash
# View all certificates
./scripts/certs/validate-certs.sh

# Check specific service
./scripts/certs/validate-certs.sh --service redis

# JSON output for monitoring
./scripts/certs/validate-certs.sh --json
```

### Manual Rotation

```bash
# Rotate expiring certificates
./scripts/certs/rotate-certs.sh

# Force rotate specific service
./scripts/certs/rotate-certs.sh --force --service postgres

# Preview without changes
./scripts/certs/rotate-certs.sh --dry-run
```

### Monitor Automated Rotation

**Systemd:**
```bash
# Check timer status
sudo systemctl status cert-rotation.timer

# View next run time
sudo systemctl list-timers cert-rotation.timer

# View rotation logs
sudo journalctl -u cert-rotation.service -n 50

# Follow logs in real-time
sudo journalctl -u cert-rotation.service -f
```

**Cron:**
```bash
# View rotation log
tail -f /var/log/sahool-cert-rotation.log

# Check cron execution in syslog
grep cert-rotation /var/log/syslog | tail -20
```

## Rotation Workflow

The automated rotation system works as follows:

```
Daily Check (2:00 AM)
    ↓
Check Certificate Expiration
    ↓
Expiring < 30 days? ─── No ──→ Exit (No action)
    ↓ Yes
Backup Current Certificate
    ↓
Generate New Certificate
    ↓
Validate New Certificate
    ↓
Restart Service (Zero Downtime)
    ↓
Verify Service Health
    ↓
Send Success Notification
    ↓
Log Rotation Event
```

## Certificate Lifecycle

| Phase | Duration | Action |
|-------|----------|--------|
| **Fresh** | 795+ days | ✓ No action needed |
| **Valid** | 31-795 days | ✓ Monitor regularly |
| **Warning** | 8-30 days | ⚠ Rotation scheduled |
| **Critical** | 1-7 days | 🔴 Immediate rotation |
| **Expired** | < 0 days | 🚨 Emergency rotation |

## Common Commands

### Generate Certificates

```bash
# All services
./scripts/certs/generate-certs.sh

# Specific service
./scripts/certs/generate-certs.sh --service redis

# Force regenerate
./scripts/certs/generate-certs.sh --force

# View certificate info
./scripts/certs/generate-certs.sh --info postgres
```

### Validate Certificates

```bash
# Validate all
./scripts/certs/validate-certs.sh

# Specific service
./scripts/certs/validate-certs.sh --service postgres

# Custom warning threshold (60 days)
./scripts/certs/validate-certs.sh --warning-days 60

# JSON output
./scripts/certs/validate-certs.sh --json

# Nagios format
./scripts/certs/validate-certs.sh --nagios
```

### Rotate Certificates

```bash
# Auto-rotate expiring certs
./scripts/certs/rotate-certs.sh

# Dry run
./scripts/certs/rotate-certs.sh --dry-run

# Force rotation
./scripts/certs/rotate-certs.sh --force

# Specific service
./scripts/certs/rotate-certs.sh --service redis

# No backup
./scripts/certs/rotate-certs.sh --no-backup

# No restart
./scripts/certs/rotate-certs.sh --skip-restart
```

## Troubleshooting

### Certificate Generation Issues

```bash
# Verify OpenSSL is installed
openssl version

# Check permissions
ls -la config/certs/

# Force regenerate
./scripts/certs/generate-certs.sh --force --service postgres
```

### Validation Failures

```bash
# Check certificate expiration
openssl x509 -in config/certs/postgres/server.crt -noout -dates

# Verify certificate chain
openssl verify -CAfile config/certs/ca/ca.crt config/certs/postgres/server.crt

# Check key matches certificate
./scripts/certs/validate-certs.sh --service postgres
```

### Service Won't Start After Rotation

```bash
# Check Docker logs
docker-compose logs postgres

# Verify permissions
chmod 600 config/certs/postgres/server.key
chmod 644 config/certs/postgres/server.crt

# Restore from backup
ls -lt config/certs/backups/postgres/
cp config/certs/backups/postgres/server_TIMESTAMP.crt config/certs/postgres/server.crt
cp config/certs/backups/postgres/server_TIMESTAMP.key config/certs/postgres/server.key
docker-compose restart postgres
```

### Systemd Timer Not Running

```bash
# Check timer status
sudo systemctl status cert-rotation.timer

# Enable and start
sudo systemctl enable cert-rotation.timer
sudo systemctl start cert-rotation.timer

# View logs
sudo journalctl -u cert-rotation.service -xe
```

### Cron Job Not Running

```bash
# Verify cron is running
sudo systemctl status cron

# Check cron logs
grep cert-rotation /var/log/syslog | tail -20

# Test manually
sudo -u root /home/user/sahool-unified-v15-idp/scripts/certs/rotate-certs.sh --dry-run
```

## File Locations

### Generated Certificates

```
config/certs/
├── ca/
│   ├── ca.crt              # Root CA (10 years)
│   └── ca.key              # CA private key (SECRET)
├── postgres/
│   ├── server.crt          # PostgreSQL cert (2.25 years)
│   ├── server.key          # Private key (SECRET)
│   └── ca.crt              # CA copy
├── pgbouncer/              # PgBouncer certificates
├── redis/                  # Redis certificates
├── nats/                   # NATS certificates
├── kong/                   # Kong certificates
├── backups/                # Automatic backups (last 10)
│   ├── postgres/
│   ├── pgbouncer/
│   ├── redis/
│   ├── nats/
│   └── kong/
└── rotation.log            # Rotation history
```

### Configuration Files

```
/etc/systemd/system/
├── cert-rotation.service   # Systemd service
└── cert-rotation.timer     # Systemd timer

/etc/cron.d/
└── sahool-cert-rotation    # Cron configuration

/etc/default/
└── sahool-certs            # Environment variables

/var/log/
├── sahool-cert-rotation.log     # Cron rotation log
└── sahool-cert-validation.log   # Validation log
```

## Security Checklist

- [ ] Private keys (`.key`) are **never** committed to git
- [ ] Private keys have `600` permissions (owner read/write only)
- [ ] Certificates have `644` permissions (world-readable)
- [ ] CA private key is stored securely (offline backup)
- [ ] Automated rotation is enabled and tested
- [ ] Notifications are configured
- [ ] Monitoring is set up (Prometheus/Grafana/Nagios)
- [ ] Backups are enabled (default: last 10 kept)
- [ ] Rotation logs are monitored regularly
- [ ] Test rotation in staging before production

## Next Steps

1. **Review Documentation**
   - Read full guide: `docs/CERTIFICATE_ROTATION.md`
   - Review script docs: `scripts/certs/README.md`
   - Check infrastructure: `infrastructure/certs/README.md`

2. **Test in Staging**
   - Generate certificates
   - Test rotation with `--dry-run`
   - Verify services restart correctly
   - Test rollback procedures

3. **Production Deployment**
   - Generate production certificates
   - Enable automated rotation
   - Configure monitoring
   - Set up notifications
   - Schedule regular audits

4. **Ongoing Maintenance**
   - Monitor certificate expiration
   - Review rotation logs weekly
   - Test rotation quarterly
   - Update CA before expiration (10 years)
   - Keep backups in secure storage

## Support Resources

### Documentation
- **Complete Guide**: `docs/CERTIFICATE_ROTATION.md` (comprehensive)
- **Script Reference**: `scripts/certs/README.md` (script usage)
- **Infrastructure Setup**: `infrastructure/certs/README.md` (systemd/cron)
- **TLS Setup**: `config/certs/README.md` (certificate basics)

### Logs
- **Rotation Logs**: `config/certs/rotation.log`
- **Systemd Journal**: `sudo journalctl -u cert-rotation.service`
- **Cron Logs**: `/var/log/sahool-cert-rotation.log`
- **Syslog**: `grep sahool-cert-rotation /var/log/syslog`

### Commands
- **Validate**: `./scripts/certs/validate-certs.sh`
- **Dry Run**: `./scripts/certs/rotate-certs.sh --dry-run`
- **Timer Status**: `sudo systemctl status cert-rotation.timer`
- **Service Logs**: `docker-compose logs <service>`

## Summary

You now have a complete automated certificate rotation system with:

✅ **Automated Generation** - Create certificates for all services
✅ **Validation** - Check expiration and certificate health
✅ **Rotation** - Automated renewal before expiration
✅ **Backup Management** - Automatic backups with retention
✅ **Zero Downtime** - Rolling service restarts
✅ **Monitoring** - Multiple output formats (text, JSON, Nagios)
✅ **Notifications** - Email and Slack integration
✅ **Scheduling** - Systemd timer or cron job
✅ **Documentation** - Comprehensive guides and references

The system will automatically check daily at 2:00 AM and rotate any certificates expiring within 30 days, ensuring continuous security without manual intervention.

---

**Quick Reference Commands:**

```bash
# Generate certificates
./scripts/certs/generate-certs.sh

# Validate certificates
./scripts/certs/validate-certs.sh

# Rotate certificates (dry run)
./scripts/certs/rotate-certs.sh --dry-run

# Check rotation status (systemd)
sudo systemctl status cert-rotation.timer

# View rotation logs
sudo journalctl -u cert-rotation.service -n 50

# Manual rotation
./scripts/certs/rotate-certs.sh
```

---

**Version**: 1.0
**Last Updated**: 2026-01-07
**Maintainer**: SAHOOL Platform Team
