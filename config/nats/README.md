# NATS Authentication Configuration

This directory contains NATS server configuration files with authentication enabled for the SAHOOL platform.

## Overview

NATS authentication has been implemented to secure the message queue infrastructure and prevent unauthorized access to the event bus system.

## Configuration Files

### Production Configuration

**File**: `nats.conf`

This is the main production configuration with:
- Multi-user authentication (admin, application, monitoring)
- JetStream enabled for persistent messaging
- Granular authorization rules per subject namespace
- Production-ready performance tuning

### Test Configuration

**File**: `nats-test.conf`

Simplified configuration for testing environments with:
- Single test user authentication
- Reduced resource limits
- Basic JetStream configuration

## Environment Variables

The following environment variables must be set in your `.env` file:

### Required Variables

```bash
# Application service credentials
NATS_USER=sahool_app
NATS_PASSWORD=<secure_password_32_chars_min>

# Administrator credentials (full access)
NATS_ADMIN_USER=nats_admin
NATS_ADMIN_PASSWORD=<secure_password_32_chars_min>

# Monitoring/read-only credentials
NATS_MONITOR_USER=nats_monitor
NATS_MONITOR_PASSWORD=<secure_password_32_chars_min>

# Connection URL (automatically constructed)
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
```

### Optional Variables (for clustering)

```bash
NATS_CLUSTER_USER=nats_cluster
NATS_CLUSTER_PASSWORD=<secure_password_32_chars_min>
```

## Generating Secure Passwords

Generate strong passwords using OpenSSL:

```bash
openssl rand -base64 32
```

Example output:
```
zK8mN3pQ7rL9vX2wY5tA1bC4dE6fG8hJ0kL2mN4pQ6r=
```

## User Roles and Permissions

### 1. Admin User (`NATS_ADMIN_USER`)

**Purpose**: Full administrative access for operations and debugging

**Permissions**:
- Publish to all subjects: `>`
- Subscribe to all subjects: `>`

**Use Cases**:
- Administrative tools
- Debugging and monitoring
- Stream management
- Account operations

### 2. Application User (`NATS_USER`)

**Purpose**: Standard access for SAHOOL services

**Permissions**:
- Publish/Subscribe to SAHOOL-specific subjects:
  - `sahool.>` - Core SAHOOL events
  - `field.>` - Field operations
  - `weather.>` - Weather data
  - `iot.>` - IoT sensor data
  - `notification.>` - Notifications
  - `marketplace.>` - Marketplace events
  - `billing.>` - Billing events
  - `chat.>` - Chat messages
  - `alert.>` - Alert events
  - `_INBOX.>` - Request-reply patterns

**Use Cases**:
- All SAHOOL application services
- API services
- Background workers

### 3. Monitor User (`NATS_MONITOR_USER`)

**Purpose**: Read-only access for monitoring and observability

**Permissions**:
- Subscribe to all subjects: `>`
- Publish denied: `>`

**Use Cases**:
- Monitoring tools (Prometheus, Grafana)
- Log aggregation
- Analytics
- Debugging (read-only)

## Subject Namespacing

All SAHOOL events use a hierarchical subject structure:

```
<module>.<service>.<action>.<entity>
```

Examples:
```
field.operations.created.field
weather.forecast.updated.location
iot.sensors.reading.temperature
notification.email.sent.user
marketplace.order.created.product
```

## Connection Strings

### Production Services

Services in `docker-compose.yml` use authenticated connections:

```yaml
environment:
  - NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222
```

### Test Services

Test services use test credentials:

```yaml
environment:
  - NATS_URL=nats://test_user:test_password@nats_test:4222
```

### Application Code (Python)

```python
import os
from nats.aio.client import Client as NATS

async def connect_nats():
    nc = NATS()
    await nc.connect(os.getenv("NATS_URL"))
    return nc
```

### Application Code (Node.js)

```javascript
import { connect } from 'nats';

async function connectNats() {
  const nc = await connect({
    servers: process.env.NATS_URL
  });
  return nc;
}
```

## Health Checks

NATS provides a monitoring HTTP endpoint that doesn't require authentication:

```bash
curl http://localhost:8222/healthz
```

Response:
```json
{
  "status": "ok"
}
```

Other monitoring endpoints:
- `/varz` - Server information
- `/connz` - Connection information
- `/routez` - Routing information
- `/subsz` - Subscription information

## Security Best Practices

### 1. Password Management

- **Never commit credentials**: Use `.env` files (ignored in `.gitignore`)
- **Rotate regularly**: Change passwords every 90 days
- **Use strong passwords**: Minimum 32 characters, alphanumeric + symbols
- **Separate environments**: Different credentials for dev/staging/prod

### 2. Network Security

- **Bind to localhost**: `ports: - "127.0.0.1:4222:4222"`
- **Use TLS in production**: Enable TLS configuration in `nats.conf`
- **Firewall rules**: Restrict NATS port access
- **VPN/VPC**: Deploy NATS within private networks

### 3. Access Control

- **Principle of least privilege**: Services only get necessary permissions
- **Service isolation**: Different credentials per service if needed
- **Monitor access**: Track connection attempts and failures
- **Audit logs**: Enable NATS logging for security audits

### 4. TLS Configuration (Production)

Uncomment and configure TLS in `nats.conf`:

```conf
tls {
    cert_file: "/etc/nats/certs/server-cert.pem"
    key_file: "/etc/nats/certs/server-key.pem"
    ca_file: "/etc/nats/certs/ca.pem"
    verify: true
    timeout: 2
}
```

Update connection URL:
```bash
NATS_URL=nats://${NATS_USER}:${NATS_PASSWORD}@nats:4222?tls=true
```

## Troubleshooting

### Connection Refused

**Symptom**: `Error: connect ECONNREFUSED 127.0.0.1:4222`

**Solutions**:
1. Verify NATS container is running: `docker ps | grep nats`
2. Check NATS logs: `docker logs sahool-nats`
3. Verify port binding: `netstat -an | grep 4222`

### Authentication Failed

**Symptom**: `Error: Authorization Violation`

**Solutions**:
1. Verify credentials in `.env` file match `nats.conf`
2. Check NATS_URL format: `nats://username:password@host:port`
3. Verify environment variables are loaded: `docker exec sahool-nats env | grep NATS`
4. Review NATS logs: `docker logs sahool-nats | grep -i auth`

### Permission Denied

**Symptom**: `Error: Permissions Violation for Publish to "subject.name"`

**Solutions**:
1. Verify subject namespace matches allowed permissions
2. Check authorization section in `nats.conf`
3. Use admin user for testing: `NATS_URL=nats://${NATS_ADMIN_USER}:${NATS_ADMIN_PASSWORD}@nats:4222`

### Healthcheck Failing

**Symptom**: NATS container unhealthy

**Solutions**:
1. Check monitoring port: `curl http://localhost:8222/healthz`
2. Verify config file is valid: `docker exec sahool-nats nats-server -c /etc/nats/nats.conf -t`
3. Check volume mount: `docker exec sahool-nats ls -la /etc/nats/`

## Monitoring and Observability

### Prometheus Metrics

NATS exposes Prometheus metrics at:
```
http://localhost:8222/metrics
```

Key metrics:
- `nats_server_connections` - Active connections
- `nats_server_in_msgs` - Incoming messages
- `nats_server_out_msgs` - Outgoing messages
- `nats_server_subscriptions` - Active subscriptions

### Grafana Dashboard

A Grafana dashboard for NATS monitoring is available in:
```
infrastructure/monitoring/grafana/dashboards/nats.json
```

### Logging

View NATS logs:
```bash
docker logs -f sahool-nats
```

Enable debug logging (development only):
```yaml
# In docker-compose.yml, add to nats environment:
environment:
  - NATS_DEBUG=true
  - NATS_TRACE=true
```

## Migration Guide

### Migrating Existing Deployments

If you have an existing SAHOOL deployment without NATS authentication:

1. **Backup your data**:
   ```bash
   docker exec sahool-nats tar czf /data/backup.tar.gz /data
   docker cp sahool-nats:/data/backup.tar.gz ./nats-backup-$(date +%Y%m%d).tar.gz
   ```

2. **Stop services**:
   ```bash
   docker-compose down
   ```

3. **Update environment variables**:
   ```bash
   cp .env .env.backup
   nano .env
   # Add NATS credentials (see above)
   ```

4. **Start NATS with new config**:
   ```bash
   docker-compose up -d nats
   docker logs -f sahool-nats  # Verify authentication is working
   ```

5. **Start remaining services**:
   ```bash
   docker-compose up -d
   ```

6. **Verify connectivity**:
   ```bash
   # Check service logs for NATS connection errors
   docker-compose logs | grep -i "nats\|authorization"
   ```

### Rolling Back

If issues occur, rollback:

1. Stop all services: `docker-compose down`
2. Restore old environment: `mv .env.backup .env`
3. Update docker-compose.yml to remove auth config
4. Restart: `docker-compose up -d`

## Advanced Configuration

### High Availability (HA) Setup

For production HA deployment, enable clustering in `nats.conf`:

```conf
cluster {
    name: sahool-cluster
    listen: 0.0.0.0:6222

    authorization {
        user: $NATS_CLUSTER_USER
        password: $NATS_CLUSTER_PASSWORD
    }

    routes = [
        nats://nats-1:6222
        nats://nats-2:6222
        nats://nats-3:6222
    ]
}
```

### NKey Authentication (Advanced)

For enhanced security, consider NKey authentication:

```bash
# Generate NKey
nk -gen user -pubout
```

Update `nats.conf`:
```conf
authorization {
    users = [
        { nkey: "UABC..." }
    ]
}
```

## Support and Documentation

- **NATS Documentation**: https://docs.nats.io/
- **NATS Security**: https://docs.nats.io/running-a-nats-service/configuration/securing_nats
- **JetStream Guide**: https://docs.nats.io/nats-concepts/jetstream
- **SAHOOL Documentation**: `docs/NATS_INTEGRATION.md`

## Change Log

### Version 1.0.0 (2026-01-06)

- ✅ Initial NATS authentication implementation
- ✅ Multi-user authentication (admin, app, monitor)
- ✅ Granular authorization per subject namespace
- ✅ Production and test configurations
- ✅ Updated all docker-compose files
- ✅ Updated all service connection strings
- ✅ Documentation and troubleshooting guides
