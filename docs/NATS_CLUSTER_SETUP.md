# NATS Cluster Setup Guide for SAHOOL Platform

> **High Availability Multi-Cluster NATS Configuration**
> Version: 1.0
> Last Updated: 2026-01-07

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
  - [Docker Deployment](#docker-deployment)
  - [Kubernetes Deployment](#kubernetes-deployment)
- [Configuration](#configuration)
- [JetStream Setup](#jetstream-setup)
- [Security](#security)
- [Monitoring & Health Checks](#monitoring--health-checks)
- [Operations](#operations)
- [Troubleshooting](#troubleshooting)
- [Performance Tuning](#performance-tuning)
- [Multi-Region Setup](#multi-region-setup)
- [Backup & Recovery](#backup--recovery)
- [Migration Guide](#migration-guide)

---

## Overview

This guide covers the setup and operation of a high-availability NATS cluster for the SAHOOL platform. The cluster consists of 3 nodes with JetStream enabled, providing:

- **High Availability**: N+2 redundancy (can lose 2 nodes)
- **JetStream Replication**: Replication factor 3 for data persistence
- **TLS Encryption**: All communication encrypted (client, cluster, gateway)
- **Gateway Support**: Super-cluster capability for multi-region deployments
- **Comprehensive Monitoring**: Health checks, metrics, and alerting

### Key Features

✅ 3-node cluster with full mesh topology
✅ JetStream with at-rest encryption (AES-256)
✅ TLS 1.2+ with modern cipher suites
✅ Granular authentication and authorization
✅ Rate limiting and connection controls
✅ Gateway configuration for geo-replication
✅ Automated health monitoring
✅ Prometheus metrics integration

---

## Architecture

### Cluster Topology

```
┌─────────────────────────────────────────────────────────────────┐
│                    SAHOOL NATS Cluster                          │
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐ │
│  │   Node 1     │◄────►│   Node 2     │◄────►│   Node 3     │ │
│  │              │      │              │      │              │ │
│  │  JetStream   │      │  JetStream   │      │  JetStream   │ │
│  │  Replica 1   │      │  Replica 2   │      │  Replica 3   │ │
│  └──────┬───────┘      └──────┬───────┘      └──────┬───────┘ │
│         │                     │                     │         │
│         └─────────────────────┴─────────────────────┘         │
│                    Full Mesh Cluster Routes                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Client Connections (TLS)
                              ▼
                    ┌──────────────────┐
                    │  Load Balancer   │
                    │  or Service      │
                    └──────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Applications    │
                    └──────────────────┘
```

### Communication Ports

| Port | Protocol | Purpose |
|------|----------|---------|
| 4222 | TCP/TLS | Client connections |
| 6222 | TCP/TLS | Cluster routing (inter-node communication) |
| 7222 | TCP/TLS | Gateway connections (super-cluster) |
| 8222 | HTTP | Monitoring and health checks |
| 7777 | HTTP | Prometheus metrics |

---

## Prerequisites

### Docker Deployment

- Docker Engine 20.10+
- Docker Compose 2.0+
- 6GB+ available RAM
- 150GB+ available storage for JetStream
- TLS certificates (or use self-signed for testing)

### Kubernetes Deployment

- Kubernetes 1.23+
- kubectl CLI configured
- Storage class with dynamic provisioning (e.g., `fast-ssd`)
- 150GB+ persistent storage (50GB per node)
- TLS certificates in Kubernetes secrets

### Common Requirements

- `jq` (for health check script)
- `curl` or `wget`
- NATS CLI (optional, for management): `https://github.com/nats-io/natscli`

---

## Quick Start

### Docker Deployment

#### 1. Generate Certificates

```bash
# Generate self-signed certificates for testing
cd /home/user/sahool-unified-v15-idp
./scripts/security/generate-nats-credentials.sh

# Or use your own certificates
mkdir -p config/certs/nats
cp /path/to/server.crt config/certs/nats/
cp /path/to/server.key config/certs/nats/
cp /path/to/ca.crt config/certs/nats/
```

#### 2. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Authentication
NATS_ADMIN_USER=admin
NATS_ADMIN_PASSWORD=$(openssl rand -base64 32)
NATS_USER=sahool
NATS_PASSWORD=$(openssl rand -base64 32)
NATS_MONITOR_USER=monitor
NATS_MONITOR_PASSWORD=$(openssl rand -base64 32)
NATS_SYSTEM_USER=system
NATS_SYSTEM_PASSWORD=$(openssl rand -base64 32)

# Cluster Authentication
NATS_CLUSTER_USER=cluster_user
NATS_CLUSTER_PASSWORD=$(openssl rand -base64 32)

# Gateway Authentication
NATS_GATEWAY_USER=gateway_user
NATS_GATEWAY_PASSWORD=$(openssl rand -base64 32)

# JetStream Encryption (32-byte key, base64 encoded)
NATS_JETSTREAM_KEY=$(openssl rand -base64 32)
```

**Important**: Save these credentials securely. You'll need them for client connections.

#### 3. Create External Network

```bash
docker network create sahool-network
```

#### 4. Start the Cluster

```bash
docker-compose -f infrastructure/nats/docker-compose.nats-cluster.yml up -d
```

#### 5. Verify Cluster Health

```bash
# Run health check
./scripts/nats/cluster-health-check.sh -e docker -v

# Check individual nodes
curl http://localhost:8222/varz  # Node 1
curl http://localhost:8223/varz  # Node 2
curl http://localhost:8224/varz  # Node 3

# Check cluster routes
curl http://localhost:8222/routez
```

#### 6. View Logs

```bash
# All nodes
docker-compose -f infrastructure/nats/docker-compose.nats-cluster.yml logs -f

# Specific node
docker logs -f sahool-nats-node1
```

---

### Kubernetes Deployment

#### 1. Create Namespace

```bash
kubectl create namespace nats-system
```

#### 2. Create TLS Certificates Secret

```bash
# Using cert-manager (recommended)
kubectl apply -f - <<EOF
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: nats-tls-certs
  namespace: nats-system
spec:
  secretName: nats-tls-certs
  issuerRef:
    name: letsencrypt-prod
    kind: ClusterIssuer
  dnsNames:
    - nats.nats-system.svc.cluster.local
    - "*.nats.nats-system.svc.cluster.local"
EOF

# Or create from existing certificates
kubectl create secret tls nats-tls-certs \
  --cert=/path/to/tls.crt \
  --key=/path/to/tls.key \
  -n nats-system

# Add CA certificate
kubectl create secret generic nats-ca-cert \
  --from-file=ca.crt=/path/to/ca.crt \
  -n nats-system
```

#### 3. Update Credentials Secret

Edit `infrastructure/nats/kubernetes/nats-statefulset.yaml` and replace placeholder passwords in the `nats-credentials` secret:

```bash
# Generate strong passwords
ADMIN_PASS=$(openssl rand -base64 32)
USER_PASS=$(openssl rand -base64 32)
MONITOR_PASS=$(openssl rand -base64 32)
SYSTEM_PASS=$(openssl rand -base64 32)
CLUSTER_PASS=$(openssl rand -base64 32)
GATEWAY_PASS=$(openssl rand -base64 32)
JS_KEY=$(openssl rand -base64 32)

# Create secret
kubectl create secret generic nats-credentials \
  --from-literal=NATS_ADMIN_USER=admin \
  --from-literal=NATS_ADMIN_PASSWORD="$ADMIN_PASS" \
  --from-literal=NATS_USER=sahool \
  --from-literal=NATS_PASSWORD="$USER_PASS" \
  --from-literal=NATS_MONITOR_USER=monitor \
  --from-literal=NATS_MONITOR_PASSWORD="$MONITOR_PASS" \
  --from-literal=NATS_SYSTEM_USER=system \
  --from-literal=NATS_SYSTEM_PASSWORD="$SYSTEM_PASS" \
  --from-literal=NATS_CLUSTER_USER=cluster_user \
  --from-literal=NATS_CLUSTER_PASSWORD="$CLUSTER_PASS" \
  --from-literal=NATS_GATEWAY_USER=gateway_user \
  --from-literal=NATS_GATEWAY_PASSWORD="$GATEWAY_PASS" \
  --from-literal=NATS_JETSTREAM_KEY="$JS_KEY" \
  -n nats-system
```

#### 4. Deploy NATS Cluster

```bash
# Deploy StatefulSet and Services
kubectl apply -f infrastructure/nats/kubernetes/nats-statefulset.yaml
kubectl apply -f infrastructure/nats/kubernetes/nats-service.yaml

# Wait for pods to be ready
kubectl wait --for=condition=ready pod -l app=nats -n nats-system --timeout=300s
```

#### 5. Verify Deployment

```bash
# Check pods
kubectl get pods -n nats-system

# Check services
kubectl get svc -n nats-system

# Check PVCs
kubectl get pvc -n nats-system

# Run health check
./scripts/nats/cluster-health-check.sh -e kubernetes -n nats-system -v
```

#### 6. Access Monitoring

```bash
# Port forward to monitoring endpoint
kubectl port-forward -n nats-system nats-0 8222:8222

# In another terminal, check status
curl http://localhost:8222/varz
curl http://localhost:8222/routez
curl http://localhost:8222/jsz
```

---

## Configuration

### Node Configuration Files

Each node has its own configuration file:

- **Node 1**: `config/nats/nats-cluster-node1.conf`
- **Node 2**: `config/nats/nats-cluster-node2.conf`
- **Node 3**: `config/nats/nats-cluster-node3.conf`

### Key Configuration Sections

#### JetStream Configuration

```conf
jetstream {
    store_dir: /data/jetstream
    max_memory_store: 2GB
    max_file_store: 20GB
    key: $NATS_JETSTREAM_KEY  # At-rest encryption
    cipher: "aes"
    domain: sahool
    unique_tag: "node-1"
    sync_interval: "2m"
}
```

#### Cluster Configuration

```conf
cluster {
    name: sahool-cluster
    listen: 0.0.0.0:6222

    tls {
        cert_file: "/etc/nats/certs/server.crt"
        key_file: "/etc/nats/certs/server.key"
        ca_file: "/etc/nats/certs/ca.crt"
        verify: true
    }

    authorization {
        user: $NATS_CLUSTER_USER
        password: $NATS_CLUSTER_PASSWORD
    }

    routes = [
        nats://$NATS_CLUSTER_USER:$NATS_CLUSTER_PASSWORD@nats-node2:6222
        nats://$NATS_CLUSTER_USER:$NATS_CLUSTER_PASSWORD@nats-node3:6222
    ]
}
```

#### Gateway Configuration (Super-Cluster)

```conf
gateway {
    name: sahool-dc1
    listen: 0.0.0.0:7222

    tls {
        cert_file: "/etc/nats/certs/server.crt"
        key_file: "/etc/nats/certs/server.key"
        ca_file: "/etc/nats/certs/ca.crt"
        verify: true
    }

    authorization {
        user: $NATS_GATEWAY_USER
        password: $NATS_GATEWAY_PASSWORD
    }
}
```

---

## JetStream Setup

### Creating Streams

Streams should be created with replication factor 3 for high availability:

```bash
# Install NATS CLI
# https://github.com/nats-io/natscli/releases

# Connect to cluster
export NATS_URL=nats://sahool:$NATS_PASSWORD@localhost:4222

# Create a stream with replication factor 3
nats stream add \
  --subjects="field.>" \
  --storage=file \
  --retention=limits \
  --max-age=7d \
  --max-msgs=-1 \
  --max-bytes=10GB \
  --replicas=3 \
  field_events

# Verify stream replication
nats stream info field_events
```

### Example Streams for SAHOOL Platform

```bash
# Field Operations Stream
nats stream add field_events \
  --subjects="field.>" \
  --storage=file \
  --retention=limits \
  --max-age=30d \
  --max-bytes=50GB \
  --replicas=3

# IoT Sensor Data Stream
nats stream add iot_data \
  --subjects="iot.>" \
  --storage=file \
  --retention=limits \
  --max-age=7d \
  --max-bytes=100GB \
  --replicas=3 \
  --discard=old

# Notification Stream
nats stream add notifications \
  --subjects="notification.>" \
  --storage=file \
  --retention=work-queue \
  --max-age=24h \
  --replicas=3

# Billing Events Stream
nats stream add billing \
  --subjects="billing.>" \
  --storage=file \
  --retention=limits \
  --max-age=90d \
  --replicas=3

# Chat Messages Stream
nats stream add chat \
  --subjects="chat.>" \
  --storage=file \
  --retention=limits \
  --max-age=365d \
  --max-msgs=1000000 \
  --replicas=3
```

### Creating Consumers

```bash
# Create a durable consumer
nats consumer add field_events field_processor \
  --filter="field.crop.>" \
  --ack=explicit \
  --pull \
  --deliver=all \
  --max-deliver=3 \
  --max-pending=100 \
  --replay=instant

# Create a push consumer
nats consumer add iot_data iot_processor \
  --filter="iot.sensor.temperature" \
  --ack=explicit \
  --target="iot.process.temperature" \
  --deliver=new \
  --max-deliver=5
```

---

## Security

### TLS/SSL Configuration

All communication in the cluster uses TLS encryption:

- **Client Connections**: TLS 1.2+ with certificate verification
- **Cluster Routes**: Mutual TLS between nodes
- **Gateway Connections**: TLS for inter-datacenter communication

### Authentication & Authorization

The cluster uses a multi-account setup:

#### System Account (SYS)

- Internal monitoring and metrics
- Not accessible to applications

#### Application Account (APP)

- **Admin User**: Full access to all subjects
- **Application User**: Granular permissions per subject namespace
- **Monitor User**: Read-only access

### Subject-Level Permissions

```conf
permissions = {
    publish = {
        allow = [
            "sahool.>",
            "field.>",
            "weather.>",
            "iot.>",
            "notification.>",
            "marketplace.>",
            "billing.>",
            "chat.>",
            "alert.>",
            "_INBOX.>"
        ]
        deny = ["$SYS.>", "$JS.API.SYSTEM.>"]
    }
    subscribe = {
        allow = [
            "sahool.>",
            "field.>",
            # ... same as publish
            "$JS.API.CONSUMER.>",
            "$JS.API.STREAM.>"
        ]
        deny = ["$SYS.>"]
    }
}
```

### JetStream Encryption

Data is encrypted at rest using AES-256:

```bash
# Generate encryption key
openssl rand -base64 32 > jetstream.key

# Set in environment
export NATS_JETSTREAM_KEY=$(cat jetstream.key)
```

### Security Best Practices

1. **Use Strong Passwords**: Minimum 32 characters, randomly generated
2. **Rotate Credentials**: Regular rotation (quarterly recommended)
3. **TLS Certificates**: Use cert-manager for automatic renewal
4. **Network Policies**: Restrict access in Kubernetes
5. **Audit Logging**: Enable and monitor access logs
6. **NKey Authentication**: Consider migrating to NKey for enhanced security

---

## Monitoring & Health Checks

### Health Check Script

Run the automated health check:

```bash
# Docker environment
./scripts/nats/cluster-health-check.sh -e docker -v

# Kubernetes environment
./scripts/nats/cluster-health-check.sh -e kubernetes -n nats-system -v

# Continuous monitoring (every 30 seconds)
./scripts/nats/cluster-health-check.sh -e docker -c

# With alert checking
./scripts/nats/cluster-health-check.sh -e docker -v -a
```

### Monitoring Endpoints

#### Server Information (varz)

```bash
curl http://localhost:8222/varz | jq
```

Returns:
- Server version and uptime
- Connection count
- Message statistics
- Memory and CPU usage

#### Cluster Routes (routez)

```bash
curl http://localhost:8222/routez | jq
```

Returns:
- Cluster topology
- Route connections
- Pending messages per route

#### Connections (connz)

```bash
curl http://localhost:8222/connz | jq
```

Returns:
- Active client connections
- IP addresses and user info
- Pending bytes per connection

#### JetStream Status (jsz)

```bash
curl http://localhost:8222/jsz | jq
```

Returns:
- JetStream enabled status
- Stream and consumer counts
- Memory and storage usage
- Replica status

### Prometheus Metrics

Metrics are exposed on port 7777 by the NATS exporter:

```bash
curl http://localhost:7777/metrics
```

Key metrics:
- `nats_up`: Server availability
- `nats_varz_connections`: Connection count
- `nats_varz_in_msgs`: Inbound messages
- `nats_varz_out_msgs`: Outbound messages
- `nats_varz_mem`: Memory usage
- `nats_varz_cpu`: CPU usage
- `nats_jetstream_streams`: Stream count
- `nats_jetstream_consumers`: Consumer count

### Grafana Dashboards

Import the NATS dashboard:
- Dashboard ID: 2279 (NATS Server)
- Dashboard ID: 11187 (NATS JetStream)

---

## Operations

### Client Connection

#### Connection String

For high availability, specify all nodes:

```
nats://sahool:PASSWORD@nats-node1:4222,nats://sahool:PASSWORD@nats-node2:4222,nats://sahool:PASSWORD@nats-node3:4222
```

Kubernetes:
```
nats://sahool:PASSWORD@nats-client.nats-system.svc.cluster.local:4222
```

#### Application Examples

**Go:**
```go
nc, err := nats.Connect(
    "nats://nats-node1:4222,nats://nats-node2:4222,nats://nats-node3:4222",
    nats.UserInfo("sahool", "PASSWORD"),
    nats.Secure(&tls.Config{
        MinVersion: tls.VersionTLS12,
    }),
    nats.MaxReconnects(-1),
    nats.ReconnectWait(2*time.Second),
)
```

**Python:**
```python
import asyncio
from nats.aio.client import Client as NATS

async def connect():
    nc = NATS()
    await nc.connect(
        servers=[
            "nats://nats-node1:4222",
            "nats://nats-node2:4222",
            "nats://nats-node3:4222"
        ],
        user="sahool",
        password="PASSWORD",
        tls_required=True,
        max_reconnect_attempts=-1
    )
    return nc
```

**Node.js/TypeScript:**
```typescript
import { connect, StringCodec } from 'nats';

const nc = await connect({
    servers: [
        'nats://nats-node1:4222',
        'nats://nats-node2:4222',
        'nats://nats-node3:4222'
    ],
    user: 'sahool',
    pass: 'PASSWORD',
    tls: {
        minVersion: 'TLSv1.2'
    },
    maxReconnectAttempts: -1,
    reconnectTimeWait: 2000
});
```

### Scaling Operations

#### Add a Node (Kubernetes)

```bash
# Scale the StatefulSet
kubectl scale statefulset nats -n nats-system --replicas=5

# Verify new pods
kubectl get pods -n nats-system -w
```

#### Remove a Node

```bash
# Scale down
kubectl scale statefulset nats -n nats-system --replicas=3

# Clean up PVC if needed
kubectl delete pvc data-nats-4 -n nats-system
```

### Upgrades

#### Rolling Update (Kubernetes)

```bash
# Update the image version
kubectl set image statefulset/nats nats=nats:2.11-alpine -n nats-system

# Monitor the rollout
kubectl rollout status statefulset/nats -n nats-system
```

#### Docker Compose Update

```bash
# Pull new images
docker-compose -f infrastructure/nats/docker-compose.nats-cluster.yml pull

# Restart nodes one at a time
docker-compose -f infrastructure/nats/docker-compose.nats-cluster.yml up -d nats-node1
sleep 30
docker-compose -f infrastructure/nats/docker-compose.nats-cluster.yml up -d nats-node2
sleep 30
docker-compose -f infrastructure/nats/docker-compose.nats-cluster.yml up -d nats-node3
```

---

## Troubleshooting

### Common Issues

#### 1. Cluster Not Forming

**Symptoms**: Nodes start but don't see each other

**Check**:
```bash
# View cluster routes
curl http://localhost:8222/routez

# Check logs
docker logs sahool-nats-node1 | grep -i cluster
```

**Solution**:
- Verify network connectivity between nodes
- Check cluster authentication credentials
- Ensure cluster routes are correctly configured
- Verify TLS certificates are valid

#### 2. JetStream Sync Issues

**Symptoms**: Replicas out of sync

**Check**:
```bash
# Check stream info
nats stream info field_events

# Look for sync status
curl http://localhost:8222/jsz?streams=true | jq '.streams[].cluster'
```

**Solution**:
- Verify all nodes have JetStream enabled
- Check storage capacity
- Review logs for sync errors
- Consider increasing `sync_interval`

#### 3. High Memory Usage

**Symptoms**: Memory consumption growing

**Check**:
```bash
# Check memory stats
curl http://localhost:8222/varz | jq '.mem'

# Check JetStream usage
curl http://localhost:8222/jsz | jq '.memory, .store'
```

**Solution**:
- Review stream retention policies
- Implement message TTL
- Increase max file storage
- Add more nodes

#### 4. Connection Failures

**Symptoms**: Clients can't connect

**Check**:
```bash
# Test connection
telnet localhost 4222

# Check TLS
openssl s_client -connect localhost:4222 -servername nats-node1
```

**Solution**:
- Verify credentials
- Check TLS certificates
- Review firewall rules
- Check connection limits

### Debug Mode

Enable debug logging:

```conf
debug: true
trace: true
```

Restart the node and check logs:

```bash
docker logs -f sahool-nats-node1
```

---

## Performance Tuning

### Resource Limits

#### Docker

Update `docker-compose.nats-cluster.yml`:

```yaml
services:
  nats-node1:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

#### Kubernetes

Update resource requests/limits in StatefulSet:

```yaml
resources:
  requests:
    cpu: 1000m
    memory: 2Gi
  limits:
    cpu: 4000m
    memory: 8Gi
```

### Configuration Tuning

#### Connection Limits

```conf
max_connections: 2000
max_connections_per_ip: 200
max_payload: 8MB
max_pending: 64MB
```

#### Write Performance

```conf
write_deadline: 10s
max_control_line: 4KB
```

#### JetStream Performance

```conf
jetstream {
    max_memory_store: 4GB
    max_file_store: 100GB
    sync_interval: "2m"
}
```

### Storage Performance

- Use SSD storage for JetStream
- Consider NVMe for high-throughput workloads
- Use storage class with high IOPS in Kubernetes

---

## Multi-Region Setup

### Gateway Configuration

Configure gateways to connect clusters across regions:

**Region 1 (us-east-1):**
```conf
gateway {
    name: sahool-dc1
    listen: 0.0.0.0:7222

    gateways: [
        {
            name: "sahool-dc2"
            url: "nats://gateway_user:PASSWORD@dc2-gateway.example.com:7222"
        },
        {
            name: "sahool-dc3"
            url: "nats://gateway_user:PASSWORD@dc3-gateway.example.com:7222"
        }
    ]
}
```

**Region 2 (eu-west-1):**
```conf
gateway {
    name: sahool-dc2
    listen: 0.0.0.0:7222

    gateways: [
        {
            name: "sahool-dc1"
            url: "nats://gateway_user:PASSWORD@dc1-gateway.example.com:7222"
        }
    ]
}
```

### Subject Interest Propagation

Gateway connections propagate subject interest between clusters automatically. No additional configuration needed.

---

## Backup & Recovery

### Backup JetStream Data

#### Docker

```bash
# Backup all nodes
for node in 1 2 3; do
    docker run --rm \
        -v nats-node${node}-data:/data \
        -v $(pwd)/backups:/backup \
        alpine \
        tar czf /backup/nats-node${node}-$(date +%Y%m%d).tar.gz -C /data .
done
```

#### Kubernetes

```bash
# Backup PVC data
for i in 0 1 2; do
    kubectl exec -n nats-system nats-$i -- \
        tar czf - /data/jetstream > backup-nats-$i-$(date +%Y%m%d).tar.gz
done
```

### Restore JetStream Data

#### Docker

```bash
# Stop the cluster
docker-compose -f infrastructure/nats/docker-compose.nats-cluster.yml down

# Restore data
for node in 1 2 3; do
    docker run --rm \
        -v nats-node${node}-data:/data \
        -v $(pwd)/backups:/backup \
        alpine \
        tar xzf /backup/nats-node${node}-backup.tar.gz -C /data
done

# Start the cluster
docker-compose -f infrastructure/nats/docker-compose.nats-cluster.yml up -d
```

### Stream Backup (Alternative)

Use NATS CLI to backup/restore streams:

```bash
# Backup stream
nats stream backup field_events field_events_backup.json

# Restore stream
nats stream restore field_events field_events_backup.json
```

---

## Migration Guide

### Migrating from Single Node to Cluster

1. **Backup existing data**
   ```bash
   nats stream backup --all
   ```

2. **Deploy cluster** (see Quick Start)

3. **Restore streams with replication**
   ```bash
   nats stream restore field_events backup.json --replicas=3
   ```

4. **Update application connection strings** to use all nodes

5. **Decommission old node** once verified

### Migrating Between Environments

#### Docker to Kubernetes

1. **Backup JetStream data** from Docker volumes
2. **Deploy Kubernetes cluster**
3. **Create PVCs** and copy data
4. **Update DNS/connection strings**
5. **Verify and cutover**

---

## Appendix

### File Locations

```
sahool-unified-v15-idp/
├── config/nats/
│   ├── nats-cluster-node1.conf
│   ├── nats-cluster-node2.conf
│   └── nats-cluster-node3.conf
├── infrastructure/nats/
│   ├── docker-compose.nats-cluster.yml
│   └── kubernetes/
│       ├── nats-statefulset.yaml
│       └── nats-service.yaml
├── scripts/nats/
│   └── cluster-health-check.sh
└── docs/
    └── NATS_CLUSTER_SETUP.md (this file)
```

### References

- [NATS Documentation](https://docs.nats.io/)
- [JetStream Guide](https://docs.nats.io/nats-concepts/jetstream)
- [NATS CLI](https://github.com/nats-io/natscli)
- [NATS Security](https://docs.nats.io/running-a-nats-service/configuration/securing_nats)
- [Prometheus Exporter](https://github.com/nats-io/prometheus-nats-exporter)

### Support

For issues or questions:
- GitHub Issues: [SAHOOL Platform Repository]
- NATS Slack: https://slack.nats.io
- Email: platform-team@sahool.io

---

**Document Version**: 1.0
**Last Updated**: 2026-01-07
**Maintained by**: SAHOOL Platform Team
