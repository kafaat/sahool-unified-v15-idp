# SAHOOL Observability Pack

## Overview

This package provides comprehensive observability for the SAHOOL platform:

- **Metrics**: Prometheus metrics and Platform KPIs
- **Dashboards**: Grafana dashboards for platform health
- **Alerts**: PrometheusRule alerts for critical conditions

## Directory Structure

```
observability/
├── metrics/           # Prometheus metrics configuration
│   ├── platform-kpis.yaml
│   └── service-metrics.yaml
├── dashboards/        # Grafana dashboards
│   ├── platform-health.json
│   ├── service-readiness.json
│   └── security-posture.json
└── alerts/           # Prometheus alerting rules
    ├── platform-alerts.yaml
    └── service-alerts.yaml
```

## Platform KPIs

| KPI                     | Target   | Description              |
| ----------------------- | -------- | ------------------------ |
| Time to create service  | < 15 min | Golden Path adoption     |
| Deployment success rate | > 99%    | GitOps reliability       |
| Services without owner  | 0        | Governance compliance    |
| Golden Path adoption    | > 90%    | Platform standardization |

## Required Labels

All services must expose these Prometheus labels:

```yaml
service: "<service-name>"
owner: "<owner>"
team: "<team>"
lifecycle: "<lifecycle>"
tier: "<tier>"
```

## Installation

Apply via ArgoCD:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: sahool-observability
spec:
  source:
    path: observability
```
