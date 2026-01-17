# SAHOOL Certificate Rotation - Infrastructure Configuration

This directory contains systemd and cron configurations for automated certificate rotation.

## Files

| File                    | Purpose                | Type          |
| ----------------------- | ---------------------- | ------------- |
| `cert-rotation.service` | Systemd service unit   | systemd       |
| `cert-rotation.timer`   | Systemd timer unit     | systemd       |
| `cert-rotation.cron`    | Cron job configuration | cron          |
| `README.md`             | This file              | documentation |

## Quick Start

### Option 1: Systemd Timer (Recommended for Linux Servers)

**Advantages:**

- Better logging integration (journald)
- Dependency management
- On-boot execution support
- Fine-grained control
- Persistent timers (catch up missed runs)

**Installation:**

```bash
# 1. Copy systemd files to system directory
sudo cp cert-rotation.service /etc/systemd/system/
sudo cp cert-rotation.timer /etc/systemd/system/

# 2. Update paths in service file (if not using /opt/sahool)
sudo sed -i 's|/opt/sahool|/home/user/sahool-unified-v15-idp|g' /etc/systemd/system/cert-rotation.service

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable timer (starts automatically on boot)
sudo systemctl enable cert-rotation.timer

# 5. Start timer
sudo systemctl start cert-rotation.timer

# 6. Verify timer is active
sudo systemctl status cert-rotation.timer
sudo systemctl list-timers cert-rotation.timer
```

**Management Commands:**

```bash
# Check timer status
sudo systemctl status cert-rotation.timer

# View next scheduled run
sudo systemctl list-timers cert-rotation.timer

# View last rotation logs
sudo journalctl -u cert-rotation.service -n 50

# Follow logs in real-time
sudo journalctl -u cert-rotation.service -f

# Trigger rotation immediately
sudo systemctl start cert-rotation.service

# Stop timer
sudo systemctl stop cert-rotation.timer

# Disable timer
sudo systemctl disable cert-rotation.timer

# Restart timer (after config changes)
sudo systemctl daemon-reload
sudo systemctl restart cert-rotation.timer
```

### Option 2: Cron Job (Alternative)

**Advantages:**

- Simpler setup
- Works on any Unix-like system
- Familiar to most administrators
- No systemd dependency

**Installation:**

```bash
# Method A: Install as system cron job
sudo cp cert-rotation.cron /etc/cron.d/sahool-cert-rotation
sudo chmod 644 /etc/cron.d/sahool-cert-rotation

# Update paths in cron file
sudo sed -i 's|/opt/sahool|/home/user/sahool-unified-v15-idp|g' /etc/cron.d/sahool-cert-rotation

# Verify syntax
cat /etc/cron.d/sahool-cert-rotation

# Method B: Add to root crontab
sudo crontab -e
# Then add this line:
# 0 2 * * * cd /home/user/sahool-unified-v15-idp && ./scripts/certs/rotate-certs.sh --backup >> /var/log/sahool-cert-rotation.log 2>&1
```

**Management Commands:**

```bash
# View cron jobs
sudo crontab -l

# Edit cron jobs
sudo crontab -e

# View cron logs (Ubuntu/Debian)
grep CRON /var/log/syslog | grep cert-rotation

# View rotation logs
tail -f /var/log/sahool-cert-rotation.log

# Disable cron job (comment out the line)
sudo crontab -e
# Add # at the beginning of the cert-rotation line

# Remove cron job
sudo rm /etc/cron.d/sahool-cert-rotation
```

## Configuration

### Systemd Service Configuration

Edit `/etc/systemd/system/cert-rotation.service`:

```ini
[Service]
# Change working directory
WorkingDirectory=/your/sahool/path

# Configure notifications
Environment="NOTIFICATION_EMAIL=admin@example.com"
Environment="SLACK_WEBHOOK_URL=https://hooks.slack.com/services/XXX"

# Adjust resource limits
CPUQuota=50%
MemoryLimit=512M
```

After editing:

```bash
sudo systemctl daemon-reload
sudo systemctl restart cert-rotation.timer
```

### Systemd Timer Configuration

Edit `/etc/systemd/system/cert-rotation.timer`:

```ini
[Timer]
# Run weekly instead of daily
OnCalendar=weekly

# Run every Monday at 3 AM
OnCalendar=Mon *-*-* 03:00:00

# Run on 1st and 15th of month at 2 AM
OnCalendar=*-*-01,15 02:00:00

# Adjust randomization delay
RandomizedDelaySec=30min
```

After editing:

```bash
sudo systemctl daemon-reload
sudo systemctl restart cert-rotation.timer
```

### Cron Configuration

Edit `/etc/cron.d/sahool-cert-rotation` or use `sudo crontab -e`:

```bash
# Daily at 2 AM
0 2 * * * root cd /path/to/sahool && ./scripts/certs/rotate-certs.sh --backup

# Weekly on Sundays at 3 AM
0 3 * * 0 root cd /path/to/sahool && ./scripts/certs/rotate-certs.sh --backup

# Monthly on the 1st at 2 AM
0 2 1 * * root cd /path/to/sahool && ./scripts/certs/rotate-certs.sh --backup

# Twice monthly (1st and 15th) at 2 AM
0 2 1,15 * * root cd /path/to/sahool && ./scripts/certs/rotate-certs.sh --backup
```

### Environment Variables

Create `/etc/default/sahool-certs`:

```bash
# Rotation threshold (days before expiration)
ROTATION_THRESHOLD_DAYS=30

# Email notifications
NOTIFICATION_EMAIL=admin@example.com

# Slack webhook
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Backup retention (number of backups to keep)
BACKUP_RETENTION=10

# Enable unattended mode (no prompts)
UNATTENDED=1
```

This file is automatically loaded by the systemd service.

## Scheduling Guidelines

### Recommended Schedules

| Frequency | Use Case            | Cron Expression | Systemd OnCalendar               |
| --------- | ------------------- | --------------- | -------------------------------- |
| Daily     | Production systems  | `0 2 * * *`     | `daily` or `*-*-* 02:00:00`      |
| Weekly    | Staging systems     | `0 3 * * 0`     | `weekly` or `Sun *-*-* 03:00:00` |
| Monthly   | Development systems | `0 2 1 * *`     | `monthly` or `*-*-01 02:00:00`   |

### Best Practices

1. **Schedule during low-traffic periods** (typically 2-4 AM)
2. **Run frequently enough** to catch expiring certificates (at least weekly)
3. **Enable persistent timers** to catch up on missed runs
4. **Add randomization** to avoid thundering herd effects
5. **Monitor logs** regularly for rotation issues
6. **Test in staging** before enabling in production

## Monitoring

### Check Rotation Status

```bash
# Systemd
sudo systemctl status cert-rotation.timer
sudo journalctl -u cert-rotation.service --since today

# Cron
tail -f /var/log/sahool-cert-rotation.log
grep cert-rotation /var/log/syslog
```

### Verify Certificates

```bash
cd /home/user/sahool-unified-v15-idp
./scripts/certs/validate-certs.sh
```

### View Rotation History

```bash
# View rotation log
cat /home/user/sahool-unified-v15-idp/config/certs/rotation.log

# View systemd journal
sudo journalctl -u cert-rotation.service --since "30 days ago"
```

## Notifications

### Email Notifications

Configure in `/etc/default/sahool-certs`:

```bash
NOTIFICATION_EMAIL=admin@example.com,ops@example.com
```

Requires `mail` or `mailx` to be installed:

```bash
# Install mail client (Ubuntu/Debian)
sudo apt-get install mailutils

# Test email
echo "Test" | mail -s "Test Subject" admin@example.com
```

### Slack Notifications

1. Create a Slack webhook:
   - Go to https://api.slack.com/messaging/webhooks
   - Create an incoming webhook
   - Copy the webhook URL

2. Configure in `/etc/default/sahool-certs`:

```bash
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXX
```

3. Test notification:

```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test notification from SAHOOL"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Syslog Integration

Rotation events are automatically logged to syslog with tag `sahool-cert-rotation`:

```bash
# View syslog entries
grep sahool-cert-rotation /var/log/syslog

# Monitor in real-time
tail -f /var/log/syslog | grep sahool-cert-rotation
```

## Troubleshooting

### Systemd Issues

**Problem**: Timer not running

```bash
# Check if timer is enabled
sudo systemctl is-enabled cert-rotation.timer

# Check for errors
sudo systemctl status cert-rotation.timer
sudo journalctl -xe

# Solution: Enable and start
sudo systemctl enable cert-rotation.timer
sudo systemctl start cert-rotation.timer
```

**Problem**: Service fails to execute

```bash
# Check service status
sudo systemctl status cert-rotation.service

# View detailed logs
sudo journalctl -u cert-rotation.service -n 100

# Test script manually
cd /home/user/sahool-unified-v15-idp
sudo ./scripts/certs/rotate-certs.sh --dry-run
```

**Problem**: Permission denied

```bash
# Check service file permissions
ls -la /etc/systemd/system/cert-rotation.*

# Ensure script is executable
chmod +x /home/user/sahool-unified-v15-idp/scripts/certs/*.sh

# Check working directory permissions
ls -la /home/user/sahool-unified-v15-idp/config/certs/
```

### Cron Issues

**Problem**: Cron job not running

```bash
# Check if cron is running
sudo systemctl status cron

# View cron logs
grep CRON /var/log/syslog | tail -20

# Verify cron job is installed
sudo crontab -l
# or
cat /etc/cron.d/sahool-cert-rotation
```

**Problem**: Script errors in cron

```bash
# Check rotation log
tail -f /var/log/sahool-cert-rotation.log

# Test script with same environment as cron
env -i /bin/bash --noprofile --norc -c "cd /home/user/sahool-unified-v15-idp && ./scripts/certs/rotate-certs.sh --dry-run"
```

**Problem**: Path issues

```bash
# Use absolute paths in cron
# Update PATH in cron file:
PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

# Specify full path to script:
0 2 * * * root /home/user/sahool-unified-v15-idp/scripts/certs/rotate-certs.sh
```

## Security Considerations

### File Permissions

```bash
# Systemd files
sudo chmod 644 /etc/systemd/system/cert-rotation.service
sudo chmod 644 /etc/systemd/system/cert-rotation.timer

# Cron files
sudo chmod 644 /etc/cron.d/sahool-cert-rotation

# Configuration file (contains sensitive data)
sudo chmod 600 /etc/default/sahool-certs

# Scripts
chmod 755 /home/user/sahool-unified-v15-idp/scripts/certs/*.sh

# Certificate directories
chmod 700 /home/user/sahool-unified-v15-idp/config/certs/ca/
chmod 600 /home/user/sahool-unified-v15-idp/config/certs/**/*.key
chmod 644 /home/user/sahool-unified-v15-idp/config/certs/**/*.crt
```

### SELinux Considerations

If using SELinux:

```bash
# Allow systemd to execute scripts
sudo chcon -t systemd_unit_file_t /etc/systemd/system/cert-rotation.*

# Allow scripts to read/write cert directories
sudo semanage fcontext -a -t cert_t '/home/user/sahool-unified-v15-idp/config/certs(/.*)?'
sudo restorecon -Rv /home/user/sahool-unified-v15-idp/config/certs/
```

## Testing

### Test Rotation

```bash
# Systemd
sudo systemctl start cert-rotation.service
sudo journalctl -u cert-rotation.service -f

# Cron (run manually)
cd /home/user/sahool-unified-v15-idp
sudo -u root ./scripts/certs/rotate-certs.sh --dry-run
```

### Test Notifications

```bash
# Set environment
export NOTIFICATION_EMAIL=test@example.com
export SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK

# Run rotation
./scripts/certs/rotate-certs.sh --force --service redis
```

## Backup and Recovery

### Backup Configuration

```bash
# Backup systemd files
sudo cp /etc/systemd/system/cert-rotation.* ~/sahool-backup/

# Backup cron configuration
sudo cp /etc/cron.d/sahool-cert-rotation ~/sahool-backup/
sudo crontab -l > ~/sahool-backup/root-crontab.txt

# Backup environment
sudo cp /etc/default/sahool-certs ~/sahool-backup/
```

### Recovery

```bash
# Restore systemd
sudo cp ~/sahool-backup/cert-rotation.* /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cert-rotation.timer
sudo systemctl start cert-rotation.timer

# Restore cron
sudo cp ~/sahool-backup/sahool-cert-rotation /etc/cron.d/
sudo chmod 644 /etc/cron.d/sahool-cert-rotation

# Restore environment
sudo cp ~/sahool-backup/sahool-certs /etc/default/
sudo chmod 600 /etc/default/sahool-certs
```

## Related Documentation

- [Certificate Rotation Guide](../../docs/CERTIFICATE_ROTATION.md) - Complete guide
- [Scripts README](../../scripts/certs/README.md) - Script documentation
- [TLS Setup](../../config/certs/README.md) - Certificate generation

## Support

For issues:

1. Check logs (systemd journal or cron logs)
2. Test scripts manually with `--dry-run`
3. Review [Certificate Rotation Guide](../../docs/CERTIFICATE_ROTATION.md)
4. Contact platform team

---

**Version**: 1.0
**Last Updated**: 2026-01-07
**Maintainer**: SAHOOL Platform Team
