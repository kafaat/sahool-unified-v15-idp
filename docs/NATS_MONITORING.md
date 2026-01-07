# NATS Monitoring Guide
# دليل مراقبة NATS

**Version:** 1.0.0
**Date:** 2026-01-07
**Platform:** SAHOOL Agricultural Platform

---

## Table of Contents - جدول المحتويات

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Setup & Installation](#setup--installation)
4. [Metrics & Monitoring](#metrics--monitoring)
5. [Alerting Rules](#alerting-rules)
6. [Dashboards](#dashboards)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)
9. [Reference](#reference)

---

## Overview

NATS is the message queue backbone of the SAHOOL platform, enabling event-driven communication between 39+ microservices. This document describes the comprehensive monitoring solution for NATS JetStream.

### نظرة عامة

NATS هو العمود الفقري لنظام الرسائل في منصة سهول، مما يتيح الاتصال الموجه بالأحداث بين أكثر من 39 خدمة صغيرة. يصف هذا المستند حل المراقبة الشامل لـ NATS JetStream.

### Key Features - الميزات الرئيسية

- ✅ **Real-time Metrics**: Prometheus-based metrics collection
- ✅ **JetStream Monitoring**: Stream and consumer-level visibility
- ✅ **Comprehensive Alerts**: 30+ alerting rules for proactive monitoring
- ✅ **Performance Tracking**: Message rates, latency, and throughput
- ✅ **Health Checks**: Server, cluster, and connection monitoring
- ✅ **Resource Monitoring**: CPU, memory, and storage tracking

---

## Architecture

### Monitoring Stack - مكونات المراقبة

```
┌─────────────────────────────────────────────────────────────┐
│                     NATS Monitoring Stack                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │              │      │              │                     │
│  │  NATS Server │◄─────┤  NATS        │                     │
│  │  (Port 4222) │      │  Prometheus  │                     │
│  │              │      │  Exporter    │                     │
│  └──────┬───────┘      └──────┬───────┘                     │
│         │                     │                             │
│         │ HTTP Metrics        │ Enhanced Metrics            │
│         │ (Port 8222)         │ (Port 7777)                 │
│         │                     │                             │
│         ▼                     ▼                             │
│  ┌─────────────────────────────────────┐                   │
│  │                                       │                   │
│  │      Prometheus                       │                   │
│  │      (Port 9090)                      │                   │
│  │                                       │                   │
│  │  - Scrapes metrics every 15s          │                   │
│  │  - Evaluates 30+ alert rules          │                   │
│  │  - Stores 30 days of data             │                   │
│  │                                       │                   │
│  └───────────────┬──────────────────────┘                   │
│                  │                                           │
│                  ▼                                           │
│  ┌───────────────────────────┬─────────────────────────┐   │
│  │                           │                         │   │
│  │      Alertmanager         │       Grafana           │   │
│  │      (Port 9093)          │       (Port 3002)       │   │
│  │                           │                         │   │
│  │  - Routes alerts          │  - Visualizes metrics   │   │
│  │  - De-duplicates          │  - Real-time dashboards │   │
│  │  - Sends notifications    │  - Historical analysis  │   │
│  │                           │                         │   │
│  └───────────────────────────┴─────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Components - المكونات

1. **NATS Server (nats:2.10-alpine)**
   - Exposes HTTP monitoring endpoint on port 8222
   - Provides `/metrics`, `/varz`, `/connz`, `/jsz` endpoints
   - JetStream enabled with encryption at rest

2. **NATS Prometheus Exporter (natsio/prometheus-nats-exporter:0.14.0)**
   - Scrapes NATS monitoring endpoints
   - Transforms to Prometheus format
   - Exposes enhanced metrics on port 7777

3. **Prometheus**
   - Scrapes both NATS direct metrics and exporter metrics
   - Evaluates alerting rules every 15-30 seconds
   - Stores metrics for 30 days

4. **Alertmanager**
   - Receives alerts from Prometheus
   - Routes to appropriate channels (Slack, Email, PagerDuty)
   - Handles alert de-duplication and grouping

5. **Grafana**
   - Visualizes NATS metrics
   - Pre-built dashboards for streams and consumers
   - Real-time and historical analysis

---

## Setup & Installation

### Prerequisites - المتطلبات الأساسية

- Docker & Docker Compose
- SAHOOL platform running
- Monitoring stack deployed
- Environment variables configured

### Quick Start - البدء السريع

#### 1. Deploy NATS Monitoring

```bash
# Start the main platform (if not already running)
docker-compose up -d

# The NATS exporter is included in the main docker-compose.yml
# It will start automatically with the platform

# Verify NATS exporter is running
docker ps | grep nats-prometheus-exporter

# Check exporter metrics endpoint
curl http://localhost:7777/metrics
```

#### 2. Verify Prometheus Scraping

```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.component == "message-queue")'

# Verify NATS metrics are being collected
curl -G http://localhost:9090/api/v1/query --data-urlencode 'query=gnatsd_varz_connections'
```

#### 3. Load Grafana Dashboards

```bash
# Open Grafana
open http://localhost:3002

# Login with credentials from .env
# Username: admin
# Password: [GRAFANA_ADMIN_PASSWORD]

# Import NATS Dashboard
# Go to: Dashboards > Import > Enter ID: 2279
# Select Prometheus datasource

# Import JetStream Dashboard
# Go to: Dashboards > Import > Enter ID: 14522
```

#### 4. Test Alerting

```bash
# Check alert rules are loaded
curl http://localhost:9090/api/v1/rules | jq '.data.groups[] | select(.name | contains("nats"))'

# Verify no active alerts (in healthy state)
curl http://localhost:9090/api/v1/alerts | jq '.data.alerts[] | select(.labels.component == "message-queue")'
```

---

## Metrics & Monitoring

### Core NATS Metrics - مقاييس NATS الأساسية

#### Server Health Metrics

| Metric | Description | Type | Arabic |
|--------|-------------|------|--------|
| `gnatsd_varz_connections` | Current active connections | Gauge | الاتصالات النشطة |
| `gnatsd_varz_total_connections` | Total connections since start | Counter | إجمالي الاتصالات |
| `gnatsd_varz_in_msgs` | Incoming messages | Counter | الرسائل الواردة |
| `gnatsd_varz_out_msgs` | Outgoing messages | Counter | الرسائل الصادرة |
| `gnatsd_varz_in_bytes` | Incoming bytes | Counter | البايتات الواردة |
| `gnatsd_varz_out_bytes` | Outgoing bytes | Counter | البايتات الصادرة |
| `gnatsd_varz_slow_consumers` | Number of slow consumers | Gauge | المستهلكون البطيئون |
| `gnatsd_varz_subscriptions` | Active subscriptions | Gauge | الاشتراكات النشطة |
| `gnatsd_varz_cpu` | CPU usage percentage | Gauge | استخدام المعالج |
| `gnatsd_varz_mem` | Memory usage in bytes | Gauge | استخدام الذاكرة |

#### JetStream Metrics

| Metric | Description | Type | Arabic |
|--------|-------------|------|--------|
| `gnatsd_jetstream_enabled` | JetStream status (1=enabled, 0=disabled) | Gauge | حالة JetStream |
| `gnatsd_jetstream_memory_used` | JetStream memory usage | Gauge | استخدام ذاكرة JetStream |
| `gnatsd_jetstream_storage_used` | JetStream storage usage | Gauge | استخدام تخزين JetStream |
| `gnatsd_jetstream_streams` | Number of streams | Gauge | عدد التدفقات |
| `gnatsd_jetstream_consumers` | Number of consumers | Gauge | عدد المستهلكين |
| `gnatsd_jetstream_messages` | Total messages in all streams | Gauge | إجمالي الرسائل |

#### Per-Stream Metrics

| Metric | Description | Labels | Arabic |
|--------|-------------|--------|--------|
| `nats_jetstream_stream_messages` | Messages in stream | stream, account | الرسائل في التدفق |
| `nats_jetstream_stream_bytes` | Bytes in stream | stream, account | بايتات التدفق |
| `nats_jetstream_stream_first_seq` | First sequence number | stream | أول رقم تسلسلي |
| `nats_jetstream_stream_last_seq` | Last sequence number | stream | آخر رقم تسلسلي |

#### Per-Consumer Metrics

| Metric | Description | Labels | Arabic |
|--------|-------------|--------|--------|
| `nats_jetstream_consumer_num_pending` | Pending messages | stream, consumer | الرسائل المعلقة |
| `nats_jetstream_consumer_num_ack_pending` | Unacknowledged messages | stream, consumer | الرسائل غير المؤكدة |
| `nats_jetstream_consumer_delivered` | Delivered messages | stream, consumer | الرسائل المسلمة |
| `nats_jetstream_consumer_redelivered` | Redelivered messages | stream, consumer | الرسائل المعاد تسليمها |

### Useful PromQL Queries - استعلامات PromQL مفيدة

#### Message Rate

```promql
# Messages per second (incoming)
rate(gnatsd_varz_in_msgs[5m])

# Messages per second (outgoing)
rate(gnatsd_varz_out_msgs[5m])

# Bytes per second (throughput)
rate(gnatsd_varz_in_bytes[5m])
```

#### Connection Monitoring

```promql
# Current connections
gnatsd_varz_connections

# Connection rate
rate(gnatsd_varz_total_connections[5m])

# Connection utilization (percentage)
(gnatsd_varz_connections / gnatsd_varz_max_connections) * 100
```

#### JetStream Health

```promql
# Memory usage percentage
(gnatsd_jetstream_memory_used / 1073741824) * 100  # Assuming 1GB limit

# Storage usage percentage
(gnatsd_jetstream_storage_used / 10737418240) * 100  # Assuming 10GB limit

# Total pending messages across all consumers
sum(nats_jetstream_consumer_num_pending)
```

#### Consumer Performance

```promql
# Consumer processing rate
rate(nats_jetstream_consumer_delivered{stream="my-stream"}[5m])

# Consumer lag (pending messages)
nats_jetstream_consumer_num_pending{stream="my-stream", consumer="my-consumer"}

# Redelivery rate (indicates processing failures)
rate(nats_jetstream_consumer_redelivered[5m])
```

---

## Alerting Rules

### Alert Severity Levels - مستويات خطورة التنبيهات

| Severity | Description | Response Time | Arabic |
|----------|-------------|---------------|--------|
| **Critical** | Service down, data loss imminent | Immediate (< 5 min) | حرج |
| **Warning** | Degraded performance, attention needed | Within 1 hour | تحذير |
| **Info** | Informational, for awareness | Best effort | معلومات |

### Critical Alerts - تنبيهات حرجة

#### NATSServerDown
```yaml
alert: NATSServerDown
expr: up{service="nats"} == 0
for: 1m
severity: critical
```
**Impact:** All async messaging stopped, platform-wide communication failure.
**Action:** Check NATS container logs, restart service immediately.

#### JetStreamMemoryCritical
```yaml
alert: JetStreamMemoryCritical
expr: gnatsd_jetstream_memory_used > 966367642  # 900MB (90% of 1GB)
for: 2m
severity: critical
```
**Impact:** New messages may be rejected, message loss possible.
**Action:** Increase memory limit or purge old streams immediately.

#### NATSConnectionLimitReached
```yaml
alert: NATSConnectionLimitReached
expr: gnatsd_varz_connections >= gnatsd_varz_max_connections * 0.95
for: 2m
severity: critical
```
**Impact:** New clients cannot connect, service degradation.
**Action:** Increase max_connections or fix connection leaks.

### Warning Alerts - تنبيهات تحذيرية

#### JetStreamStreamBacklog
```yaml
alert: JetStreamStreamBacklog
expr: nats_jetstream_stream_messages > 100000
for: 10m
severity: warning
```
**Impact:** Messages not being consumed fast enough.
**Action:** Scale consumers, check processing capacity.

#### NATSHighCPUUsage
```yaml
alert: NATSHighCPUUsage
expr: gnatsd_varz_cpu > 80
for: 5m
severity: warning
```
**Impact:** Message processing may be slowed.
**Action:** Check for message backlog, consider scaling cluster.

#### NATSSlowConsumersDetected
```yaml
alert: NATSSlowConsumersDetected
expr: gnatsd_varz_slow_consumers > 0
for: 3m
severity: warning
```
**Impact:** Message delivery may be delayed or dropped.
**Action:** Identify and fix slow consumer services.

### Alert Handling - معالجة التنبيهات

#### Alert Routing (Alertmanager Configuration)

```yaml
route:
  group_by: ['alertname', 'component', 'severity']
  group_wait: 10s
  group_interval: 5m
  repeat_interval: 4h
  receiver: 'default'

  routes:
    # Critical NATS alerts - page on-call
    - match:
        severity: critical
        component: message-queue
      receiver: 'pagerduty-critical'
      continue: true

    # Warning alerts - Slack only
    - match:
        severity: warning
        component: message-queue
      receiver: 'slack-monitoring'

receivers:
  - name: 'pagerduty-critical'
    pagerduty_configs:
      - service_key: '<pagerduty-key>'

  - name: 'slack-monitoring'
    slack_configs:
      - channel: '#monitoring-alerts'
        text: '{{ range .Alerts }}{{ .Annotations.summary }}{{ end }}'
```

---

## Dashboards

### Grafana NATS Dashboard

#### Official NATS Dashboard (ID: 2279)

**Panels:**
- Server overview (connections, messages, throughput)
- CPU and memory usage
- Message rates (in/out)
- Connection breakdown by client
- Subscription statistics

**Import Steps:**
1. Open Grafana: http://localhost:3002
2. Navigate to: Dashboards → Import
3. Enter Dashboard ID: `2279`
4. Select Prometheus datasource
5. Click Import

#### JetStream Dashboard (ID: 14522)

**Panels:**
- JetStream memory and storage usage
- Stream list with message counts
- Consumer lag and processing rates
- Redelivery rates
- Acknowledgment pending

**Import Steps:**
1. Open Grafana: http://localhost:3002
2. Navigate to: Dashboards → Import
3. Enter Dashboard ID: `14522`
4. Select Prometheus datasource
5. Click Import

### Custom Dashboard Panels

#### Stream Health Panel

```json
{
  "title": "Stream Message Count",
  "targets": [
    {
      "expr": "nats_jetstream_stream_messages",
      "legendFormat": "{{ stream }}"
    }
  ],
  "type": "graph"
}
```

#### Consumer Lag Panel

```json
{
  "title": "Consumer Pending Messages",
  "targets": [
    {
      "expr": "nats_jetstream_consumer_num_pending",
      "legendFormat": "{{ stream }}/{{ consumer }}"
    }
  ],
  "type": "graph",
  "alert": {
    "conditions": [
      {
        "evaluator": { "type": "gt", "params": [10000] },
        "operator": { "type": "and" },
        "query": { "params": ["A", "5m", "now"] },
        "type": "query"
      }
    ]
  }
}
```

---

## Troubleshooting

### Common Issues - المشاكل الشائعة

#### 1. NATS Exporter Not Starting

**Symptoms:**
- Container exits immediately
- No metrics at http://localhost:7777/metrics
- Error in logs: "connection refused"

**Diagnosis:**
```bash
# Check NATS is accessible
curl http://localhost:8222/varz

# Check exporter logs
docker logs sahool-nats-prometheus-exporter

# Verify network connectivity
docker exec sahool-nats-prometheus-exporter wget -O- http://nats:8222/varz
```

**Solution:**
1. Ensure NATS is running and healthy
2. Verify NATS monitoring port (8222) is accessible
3. Check Docker network connectivity
4. Restart exporter: `docker-compose restart nats-prometheus-exporter`

#### 2. Metrics Not Appearing in Prometheus

**Symptoms:**
- Prometheus shows target as "down"
- No NATS metrics in Prometheus UI
- Queries return no data

**Diagnosis:**
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | select(.labels.job == "nats-exporter")'

# Test exporter endpoint manually
curl http://localhost:7777/metrics | grep nats

# Check Prometheus logs
docker logs sahool-monitoring-prometheus | grep nats
```

**Solution:**
1. Verify scrape config in `prometheus.yml`
2. Ensure exporter is in correct Docker network
3. Reload Prometheus config: `curl -X POST http://localhost:9090/-/reload`
4. Check firewall/network policies

#### 3. High Memory Usage

**Symptoms:**
- JetStream memory alerts firing
- NATS container memory at limit
- Messages being rejected

**Diagnosis:**
```bash
# Check JetStream memory usage
curl http://localhost:8222/jsz?acc=APP | jq '.memory'

# Check stream details
curl http://localhost:8222/jsz?acc=APP&streams=true | jq '.streams[] | {name, state}'

# List streams sorted by message count
curl http://localhost:8222/jsz?acc=APP&streams=true | jq -r '.streams[] | "\(.state.messages) \(.config.name)"' | sort -rn
```

**Solution:**
1. Review retention policies on streams
2. Purge old messages: `nats stream purge <stream-name>`
3. Increase JetStream memory limit in config
4. Archive old streams to object storage

#### 4. Slow Consumer Issues

**Symptoms:**
- `NATSSlowConsumersDetected` alert firing
- Messages being dropped
- Consumer lag increasing

**Diagnosis:**
```bash
# Check slow consumers
curl http://localhost:8222/connz?state=slow | jq '.'

# Identify slow consumer services
docker ps --filter "label=com.sahool.tier=application" --format "{{.Names}}" | xargs -I {} docker logs {} --tail=100 | grep -i "slow consumer"

# Check consumer processing rate
curl -G http://localhost:9090/api/v1/query --data-urlencode 'query=rate(nats_jetstream_consumer_delivered[5m])'
```

**Solution:**
1. Scale consumer service horizontally
2. Optimize message processing logic
3. Increase consumer max_ack_pending
4. Review consumer configuration (batch size, timeout)

#### 5. Connection Limit Reached

**Symptoms:**
- New connections being rejected
- "maximum connections exceeded" errors
- Services can't connect to NATS

**Diagnosis:**
```bash
# Check current connections
curl http://localhost:8222/varz | jq '{connections, max_connections}'

# List connections by client
curl http://localhost:8222/connz | jq '.connections[] | {ip, name, subscriptions}'

# Find connection leaks
docker exec sahool-nats nats server list connections
```

**Solution:**
1. Increase `max_connections` in NATS config
2. Review services for connection leaks
3. Implement connection pooling in clients
4. Check for zombie connections and cleanup

---

## Best Practices

### Performance Optimization - تحسين الأداء

#### 1. Connection Pooling

**Python Example:**
```python
import asyncio
from nats.aio.client import Client as NATS

# Create connection pool
nc = NATS()

async def connect():
    await nc.connect(
        servers=["nats://nats:4222"],
        max_reconnect_attempts=-1,  # Infinite reconnects
        reconnect_time_wait=2,      # 2 seconds between attempts
        ping_interval=120,           # Keep-alive ping
        max_outstanding_pings=3      # Max missed pings before disconnect
    )

# Reuse connection across requests
async def publish_message(subject, data):
    await nc.publish(subject, data.encode())
```

#### 2. Message Batching

```python
# Bad: Publishing one message at a time
for i in range(1000):
    await nc.publish("subject", f"message-{i}".encode())

# Good: Batch publishing
messages = [f"message-{i}".encode() for i in range(1000)]
for msg in messages:
    await nc.publish("subject", msg)
await nc.flush()  # Single flush for all messages
```

#### 3. Stream Configuration

```bash
# Create stream with appropriate limits
nats stream add \
  --subjects "sahool.events.>" \
  --retention limits \
  --max-msgs 1000000 \
  --max-bytes 10GB \
  --max-age 7d \
  --storage file \
  --replicas 1 \
  --discard old \
  --dupe-window 2m
```

#### 4. Consumer Configuration

```bash
# Create consumer with optimal settings
nats consumer add \
  --stream EVENTS \
  --filter "sahool.events.critical" \
  --deliver all \
  --ack explicit \
  --max-deliver 5 \
  --max-ack-pending 1000 \
  --replay instant
```

### Monitoring Best Practices - أفضل ممارسات المراقبة

1. **Set Retention Policies**
   - Define appropriate message retention for each stream
   - Balance between data availability and storage costs
   - Use time-based or count-based limits

2. **Monitor Consumer Lag**
   - Set alerts for consumer lag thresholds
   - Track processing rates over time
   - Identify bottlenecks early

3. **Capacity Planning**
   - Track growth trends in message volume
   - Plan storage expansion proactively
   - Monitor connection count growth

4. **Alert Tuning**
   - Adjust thresholds based on workload patterns
   - Reduce false positives with appropriate `for` durations
   - Group related alerts to reduce noise

5. **Regular Audits**
   - Review unused streams and consumers
   - Clean up old data regularly
   - Optimize stream configurations

### Security Best Practices - أفضل ممارسات الأمان

1. **Use Authentication**
   - Always use user/password or NKeys
   - Rotate credentials regularly
   - Use separate accounts per service

2. **Enable TLS**
   - Enforce TLS for all connections
   - Use valid certificates
   - Disable non-TLS ports in production

3. **Restrict Monitoring Access**
   - Limit access to monitoring port (8222)
   - Use firewall rules to restrict access
   - Don't expose monitoring port publicly

4. **Implement Authorization**
   - Use granular subject-based permissions
   - Follow principle of least privilege
   - Use separate accounts for different services

5. **Enable At-Rest Encryption**
   - Use JetStream encryption with strong keys
   - Rotate encryption keys periodically
   - Secure key storage (environment variables, secrets)

---

## Reference

### File Locations - مواقع الملفات

| File | Path | Description |
|------|------|-------------|
| **NATS Config** | `/home/user/sahool-unified-v15-idp/config/nats/nats-secure.conf` | Main NATS configuration |
| **Exporter Config** | `/home/user/sahool-unified-v15-idp/infrastructure/monitoring/prometheus/nats-exporter.yml` | Prometheus scrape configuration |
| **Alert Rules** | `/home/user/sahool-unified-v15-idp/infrastructure/monitoring/prometheus/rules/nats-alerts.yml` | NATS alerting rules |
| **Docker Compose** | `/home/user/sahool-unified-v15-idp/infrastructure/monitoring/docker-compose.nats-monitoring.yml` | NATS monitoring stack |
| **Main Compose** | `/home/user/sahool-unified-v15-idp/docker-compose.yml` | Main platform compose (includes exporter) |

### Useful Commands - أوامر مفيدة

#### NATS CLI Commands

```bash
# Install NATS CLI
curl -sf https://binaries.nats.dev/nats-io/natscli/nats@latest | sh

# Connect to NATS
nats context save sahool \
  --server nats://localhost:4222 \
  --user $NATS_USER \
  --password $NATS_PASSWORD

# List streams
nats stream list

# View stream info
nats stream info <stream-name>

# List consumers
nats consumer list <stream-name>

# Purge stream
nats stream purge <stream-name>

# Publish test message
nats pub sahool.test "Test message"

# Subscribe to subject
nats sub "sahool.>"

# Check server info
nats server list
```

#### Docker Commands

```bash
# View NATS logs
docker logs sahool-nats -f

# View exporter logs
docker logs sahool-nats-prometheus-exporter -f

# Restart NATS
docker-compose restart nats

# Restart exporter
docker-compose restart nats-prometheus-exporter

# Check NATS container stats
docker stats sahool-nats
```

#### Metrics Endpoints

```bash
# NATS native metrics
curl http://localhost:8222/metrics

# Server variables
curl http://localhost:8222/varz

# Connections
curl http://localhost:8222/connz

# JetStream info
curl http://localhost:8222/jsz?acc=APP

# Exporter metrics
curl http://localhost:7777/metrics
```

### External Resources - موارد خارجية

- **NATS Documentation**: https://docs.nats.io/
- **JetStream Guide**: https://docs.nats.io/nats-concepts/jetstream
- **Prometheus Exporter**: https://github.com/nats-io/prometheus-nats-exporter
- **Grafana Dashboards**: https://grafana.com/grafana/dashboards/?search=nats
- **NATS Community**: https://natsio.slack.com/

### Support - الدعم

For issues with NATS monitoring:
1. Check this documentation first
2. Review Docker logs for errors
3. Consult NATS documentation
4. Contact platform team: platform@sahool.io

---

**Document Version:** 1.0.0
**Last Updated:** 2026-01-07
**Maintained by:** SAHOOL Platform Team
