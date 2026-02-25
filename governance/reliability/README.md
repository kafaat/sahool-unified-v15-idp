# Reliability & SLO Definitions

> الموثوقية وأهداف مستوى الخدمة | Reliability & SLO Definitions

Service Level Objectives (SLOs) and Service Level Indicators (SLIs) for all SAHOOL platform services, defining reliability targets and error budgets.

## Contents

| File | Description |
|------|-------------|
| [slo-definitions.yaml](./slo-definitions.yaml) | Complete SLO/SLI definitions for all services |

## SLO Categories

| Category | Target | Measurement |
|----------|--------|-------------|
| **Availability** | 99.9% | Successful requests / total requests |
| **Latency (p50)** | < 200ms | Median response time |
| **Latency (p99)** | < 2s | 99th percentile response time |
| **Error Rate** | < 0.1% | 5xx responses / total responses |
| **Throughput** | Varies | Requests per second per service |

## Error Budgets

Each service has a monthly error budget calculated from its SLO:
- **99.9% SLO** = 43.2 minutes/month downtime budget
- **99.5% SLO** = 3.6 hours/month downtime budget

## Monitoring Integration

SLOs are monitored via:
- **Prometheus**: Metrics collection and alerting rules
- **Grafana**: SLO dashboards (`infrastructure/monitoring/grafana/dashboards/`)
- **Alert Rules**: `infrastructure/monitoring/prometheus/rules/slo-rules.yml`

## Related

- [Monitoring Infrastructure](../../infrastructure/monitoring/) — Prometheus/Grafana stack
- [Disaster Recovery](../../docs/disaster-recovery/) — DR runbook
- [Policies](../policies/) — Kyverno enforcement policies
