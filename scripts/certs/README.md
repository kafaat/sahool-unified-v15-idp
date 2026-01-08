# SAHOOL Certificate Management Scripts

This directory contains automated scripts for TLS certificate management in the SAHOOL platform.

## Scripts Overview

### 🔐 generate-certs.sh
**Purpose**: Generate TLS certificates for all infrastructure services

**Usage:**
```bash
# Generate all certificates
./generate-certs.sh

# Force regenerate all certificates
./generate-certs.sh --force

# Generate certificate for specific service
./generate-certs.sh --service redis

# Show certificate information
./generate-certs.sh --info postgres

# Verify all certificates
./generate-certs.sh --verify
```

**Features:**
- Generates self-signed CA certificate (10 years)
- Creates service certificates (2.25 years)
- Sets proper file permissions
- Validates certificate chain
- Shows detailed certificate information

### ✅ validate-certs.sh
**Purpose**: Validate TLS certificates and check for expiration

**Usage:**
```bash
# Validate all certificates
./validate-certs.sh

# Validate specific service
./validate-certs.sh --service redis

# Set custom warning threshold (days)
./validate-certs.sh --warning-days 60

# JSON output for monitoring
./validate-certs.sh --json

# Nagios plugin format
./validate-certs.sh --nagios
```

**Features:**
- Checks certificate expiration
- Validates certificate chain
- Verifies private key matches certificate
- Multiple output formats (text, JSON, Nagios)
- Configurable warning thresholds

**Exit Codes:**
- `0` - All certificates valid
- `1` - Certificate error or expired
- `2` - Certificate expiring soon (warning)

### 🔄 rotate-certs.sh
**Purpose**: Automate certificate rotation with zero downtime

**Usage:**
```bash
# Rotate all expiring certificates
./rotate-certs.sh

# Dry run (preview without changes)
./rotate-certs.sh --dry-run

# Rotate specific service
./rotate-certs.sh --service redis

# Force rotation (even if not expiring)
./rotate-certs.sh --force

# Rotate without restarting services
./rotate-certs.sh --skip-restart

# Rotate without backup
./rotate-certs.sh --no-backup
```

**Features:**
- Automatic expiration checking (30-day threshold)
- Backup management with retention
- Zero-downtime service restarts
- Notification support (email, Slack)
- Rollback capability
- Comprehensive logging

## Quick Start

### 1. Initial Certificate Generation

```bash
# Generate certificates for all services
./generate-certs.sh

# Verify certificates were created
./validate-certs.sh
```

### 2. Enable Automated Rotation

**Option A: Systemd (Recommended for Linux servers)**

```bash
# Copy systemd files
sudo cp ../../infrastructure/certs/cert-rotation.service /etc/systemd/system/
sudo cp ../../infrastructure/certs/cert-rotation.timer /etc/systemd/system/

# Enable and start timer
sudo systemctl daemon-reload
sudo systemctl enable cert-rotation.timer
sudo systemctl start cert-rotation.timer

# Verify
sudo systemctl status cert-rotation.timer
```

**Option B: Cron Job**

```bash
# Add to crontab (runs daily at 2 AM)
sudo crontab -e

# Add this line:
0 2 * * * cd /home/user/sahool-unified-v15-idp && ./scripts/certs/rotate-certs.sh --backup >> /var/log/sahool-cert-rotation.log 2>&1
```

### 3. Configure Notifications (Optional)

```bash
# Create configuration file
sudo tee /etc/default/sahool-certs <<EOF
# Email notifications
NOTIFICATION_EMAIL=admin@example.com

# Slack notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL
EOF
```

## Certificate Structure

```
config/certs/
├── ca/
│   ├── ca.crt              # Root CA certificate (10 years)
│   └── ca.key              # CA private key (SECRET)
├── postgres/
│   ├── server.crt          # PostgreSQL certificate (2.25 years)
│   ├── server.key          # Private key (SECRET)
│   └── ca.crt              # CA copy
├── pgbouncer/
│   ├── server.crt
│   ├── server.key          # (SECRET)
│   └── ca.crt
├── redis/
│   ├── server.crt
│   ├── server.key          # (SECRET)
│   └── ca.crt
├── nats/
│   ├── server.crt
│   ├── server.key          # (SECRET)
│   └── ca.crt
├── kong/
│   ├── server.crt
│   ├── server.key          # (SECRET)
│   └── ca.crt
└── backups/                # Automatic backups (last 10 kept)
    ├── postgres/
    ├── pgbouncer/
    ├── redis/
    ├── nats/
    └── kong/
```

## Common Tasks

### Check Certificate Expiration

```bash
# Check all certificates
./validate-certs.sh

# Check specific service
./validate-certs.sh --service redis

# Get JSON output for monitoring
./validate-certs.sh --json | jq .
```

### Manual Certificate Rotation

```bash
# Dry run first to see what will happen
./rotate-certs.sh --dry-run

# Rotate expiring certificates
./rotate-certs.sh

# Force rotate specific service
./rotate-certs.sh --force --service postgres
```

### View Certificate Details

```bash
# Using our script
./generate-certs.sh --info postgres

# Using OpenSSL directly
openssl x509 -in ../../config/certs/postgres/server.crt -noout -text
openssl x509 -in ../../config/certs/postgres/server.crt -noout -dates
```

### Backup and Restore

```bash
# Backups are automatic during rotation
# Manual backup:
cp -r ../../config/certs ../../config/certs.backup.$(date +%Y%m%d)

# Restore from backup:
cp ../../config/certs/backups/redis/server_20260107_020000.crt ../../config/certs/redis/server.crt
cp ../../config/certs/backups/redis/server_20260107_020000.key ../../config/certs/redis/server.key
docker-compose restart redis
```

## Monitoring Integration

### Prometheus Metrics

```bash
# Export certificate expiration metrics
while true; do
  for cert in ../../config/certs/*/server.crt; do
    service=$(basename $(dirname $cert))
    days=$(./validate-certs.sh --service $service --json | jq '.validation_results[0].days_until_expiry')
    echo "sahool_cert_expiry_days{service=\"$service\"} $days"
  done
  sleep 60
done
```

### Nagios/Icinga Check

```bash
# Add to Nagios commands.cfg
define command {
    command_name    check_sahool_certs
    command_line    /home/user/sahool-unified-v15-idp/scripts/certs/validate-certs.sh --nagios
}
```

### Health Check Endpoint

```bash
# Simple HTTP endpoint for load balancers
python3 -c "
import http.server
import subprocess
import json

class CertHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        result = subprocess.run(['./validate-certs.sh', '--json'],
                              capture_output=True, text=True)
        self.send_response(200 if result.returncode == 0 else 503)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(result.stdout.encode())

http.server.HTTPServer(('', 8080), CertHandler).serve_forever()
"
```

## Troubleshooting

### Certificate Generation Fails

```bash
# Check OpenSSL is installed
openssl version

# Check write permissions
ls -la ../../config/certs/

# Regenerate with verbose output
bash -x ./generate-certs.sh --service postgres
```

### Rotation Fails

```bash
# Check current certificate status
./validate-certs.sh

# View rotation logs
tail -f ../../config/certs/rotation.log

# View systemd logs
sudo journalctl -u cert-rotation.service -f

# Run in dry-run mode to see issues
./rotate-certs.sh --dry-run
```

### Service Won't Start After Rotation

```bash
# Check certificate files exist
ls -la ../../config/certs/postgres/

# Verify permissions
chmod 600 ../../config/certs/postgres/server.key
chmod 644 ../../config/certs/postgres/server.crt

# Verify certificate is valid
openssl verify -CAfile ../../config/certs/ca/ca.crt ../../config/certs/postgres/server.crt

# Check Docker logs
docker-compose logs postgres

# Restore from backup if needed
ls -lt ../../config/certs/backups/postgres/
```

## Security Best Practices

### ✅ DO:

- Keep private keys (`.key` files) secure with `600` permissions
- Never commit private keys to version control
- Rotate certificates before expiration (30-day threshold)
- Enable automated rotation
- Monitor certificate expiration continuously
- Keep backups in encrypted storage
- Use separate certificates for each environment

### ❌ DON'T:

- Never share private keys via email/chat
- Never use the same certificates across environments
- Never disable certificate validation
- Never ignore expiration warnings
- Never commit `.key` files to git

### File Permissions

```bash
# Set correct permissions (run after generation)
find ../../config/certs -name "*.key" -exec chmod 600 {} \;
find ../../config/certs -name "*.crt" -exec chmod 644 {} \;
```

### Git Protection

```bash
# Ensure .gitignore excludes private keys
grep -q "*.key" ../../.gitignore || echo "*.key" >> ../../.gitignore
grep -q "config/certs/**/*.key" ../../.gitignore || echo "config/certs/**/*.key" >> ../../.gitignore
```

## Environment Variables

Configure in `/etc/default/sahool-certs` or export before running scripts:

| Variable | Description | Default |
|----------|-------------|---------|
| `ROTATION_THRESHOLD_DAYS` | Days before expiration to rotate | 30 |
| `WARNING_DAYS` | Days before expiration to warn | 30 |
| `NOTIFICATION_EMAIL` | Email address for notifications | None |
| `SLACK_WEBHOOK_URL` | Slack webhook for notifications | None |
| `BACKUP_RETENTION` | Number of backups to keep | 10 |
| `UNATTENDED` | Skip interactive prompts | 0 |

## Advanced Usage

### Custom Rotation Threshold

```bash
# Rotate if expiring within 60 days
ROTATION_THRESHOLD_DAYS=60 ./rotate-certs.sh
```

### Silent Mode (for Automation)

```bash
# No interactive prompts
UNATTENDED=1 ./rotate-certs.sh
```

### Integration with Configuration Management

```bash
# Ansible playbook example
- name: Rotate SAHOOL certificates
  command: /opt/sahool/scripts/certs/rotate-certs.sh --backup
  environment:
    UNATTENDED: "1"
    NOTIFICATION_EMAIL: "ops@example.com"
  register: rotation_result
  failed_when: rotation_result.rc != 0
```

## Related Documentation

- [Certificate Rotation Guide](../../docs/CERTIFICATE_ROTATION.md) - Comprehensive guide
- [TLS Setup Summary](../../TLS_SETUP_SUMMARY.md) - Initial TLS configuration
- [Security Best Practices](../../SECURITY.md) - Platform security
- [Deployment Checklist](../../DEPLOYMENT_CHECKLIST.md) - Production deployment

## Support

For issues or questions:

1. Check the [Certificate Rotation Guide](../../docs/CERTIFICATE_ROTATION.md)
2. Review script output and logs
3. Run validation: `./validate-certs.sh`
4. Check service logs: `docker-compose logs <service>`
5. Contact the platform team

---

**Version**: 1.0
**Last Updated**: 2026-01-07
**Maintainer**: SAHOOL Platform Team
