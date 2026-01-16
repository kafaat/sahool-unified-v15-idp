# SLO/SLI Guidance

## Overview

Service Level Objectives (SLOs) and Service Level Indicators (SLIs) define the reliability targets for SAHOOL platform services.

## Service Tiers

Services are categorized into three tiers based on criticality:

### Critical Tier

- **Kong API Gateway**
- **PostgreSQL Database**
- **Redis Cache**
- **NATS Message Queue**

**SLO Target**: 99.95% availability (22 minutes/month downtime)

### High Tier

- **Crop Growth Model**
- **Crop Health AI**
- **Weather Service**
- **IoT Gateway**
- **Notification Service**

**SLO Target**: 99.9% availability (43 minutes/month downtime)

### Medium Tier

- **Satellite Service**
- **Marketplace Service**
- **Analytics Service**

**SLO Target**: 99.5% availability (3.6 hours/month downtime)

## Service Level Indicators (SLIs)

### 1. Availability

**Definition**: Percentage of successful health checks

**Measurement**:

```promql
(
  sum(rate(up{job="sahool-services"}[5m]))
  /
  count(up{job="sahool-services"})
) * 100
```

**Target**:

- Critical: 99.95%
- High: 99.9%
- Medium: 99.5%

**Alert Threshold**:

```yaml
- alert: SLOAvailabilityBreach
  expr: |
    (
      sum(rate(up{job="sahool-services"}[30m]))
      /
      count(up{job="sahool-services"})
    ) < 0.999
  for: 5m
  labels:
    severity: critical
    tier: high
```

### 2. Request Success Rate

**Definition**: Percentage of requests returning 2xx or 3xx status codes

**Measurement**:

```promql
(
  sum(rate(service_requests_total{status=~"2..|3.."}[5m]))
  /
  sum(rate(service_requests_total[5m]))
) * 100
```

**Target**:

- Critical: 99.9% success rate
- High: 99.5% success rate
- Medium: 99% success rate

**Alert Threshold**:

```yaml
- alert: SLOSuccessRateBreach
  expr: |
    (
      sum(rate(service_requests_total{status=~"2..|3.."}[30m])) by (service)
      /
      sum(rate(service_requests_total[30m])) by (service)
    ) < 0.995
  for: 10m
  labels:
    severity: warning
    tier: high
```

### 3. Request Latency

**Definition**: 95th percentile request latency

**Measurement**:

```promql
histogram_quantile(0.95,
  rate(service_request_duration_seconds_bucket[5m])
)
```

**Target**:

- Critical (API Gateway): P95 < 100ms
- High (Application Services): P95 < 1s
- Medium (Batch Services): P95 < 5s

**Alert Threshold**:

```yaml
- alert: SLOLatencyBreach
  expr: |
    histogram_quantile(0.95,
      rate(service_request_duration_seconds_bucket{tier="high"}[30m])
    ) > 1
  for: 15m
  labels:
    severity: warning
    tier: high
```

### 4. Data Freshness

**Definition**: Time since last successful data update

**Measurement**:

```promql
time() - max(last_update_timestamp) by (service, data_type)
```

**Target**:

- Weather data: < 1 hour
- Satellite imagery: < 24 hours
- Field data: < 5 minutes
- Sensor data: < 1 minute

**Alert Threshold**:

```yaml
- alert: SLODataFreshnessBreach
  expr: |
    time() - max(last_update_timestamp{data_type="weather"}) > 3600
  for: 5m
  labels:
    severity: warning
    data_type: weather
```

## Error Budgets

Error budget = (1 - SLO) × Total requests

### Calculation Example

For a service with 99.9% SLO handling 1M requests/month:

- **Error budget**: 0.1% × 1,000,000 = 1,000 failed requests
- **Daily budget**: 1,000 / 30 ≈ 33 failed requests/day
- **Hourly budget**: 33 / 24 ≈ 1.4 failed requests/hour

### Error Budget Consumption

Monitor error budget consumption:

```promql
# Remaining error budget (percentage)
(
  1 - (
    sum(increase(service_requests_total{status=~"5.."}[30d]))
    /
    sum(increase(service_requests_total[30d]))
  )
) / (1 - 0.999) * 100
```

### Error Budget Policy

| Budget Remaining | Action                                                |
| ---------------- | ----------------------------------------------------- |
| > 50%            | Normal development pace                               |
| 25-50%           | Review recent changes, increase monitoring            |
| 10-25%           | Freeze non-critical deploys, focus on reliability     |
| < 10%            | Deploy freeze, incident review, all-hands reliability |

## Alert Configuration

### Alert Severity Levels

#### Page-Worthy (Critical)

- Service completely down
- Error rate > 50%
- SLO breach for Critical tier services
- Data loss detected

**Action**: Immediate response, page on-call

#### High (Warning)

- Availability < SLO target
- Error rate > 5%
- Latency > 2× SLO target
- Error budget < 25%

**Action**: Investigate within 15 minutes

#### Medium (Info)

- Error budget < 50%
- Latency > 1.5× SLO target
- Cache hit rate < 50%

**Action**: Review during business hours

### Alert Routing

```yaml
# alertmanager.yml
route:
  receiver: "default"
  routes:
    # Critical alerts - page immediately
    - match:
        severity: critical
      receiver: "pagerduty-critical"
      continue: true

    # High alerts - Slack + email
    - match:
        severity: warning
        tier: critical
      receiver: "slack-critical"
      continue: true

    # Medium alerts - Slack only
    - match:
        severity: warning
      receiver: "slack-warnings"
```

## SLO Dashboards

### Grafana Dashboard Panels

1. **Availability Trend**
   - Line chart showing 7-day availability
   - SLO target line
   - Current availability

2. **Error Budget Burn Rate**
   - Gauge showing remaining error budget
   - Trend showing consumption rate
   - Projection to budget exhaustion

3. **Request Success Rate**
   - Success vs error rate over time
   - Breakdown by endpoint
   - SLO target line

4. **Latency Distribution**
   - P50, P95, P99 latencies
   - SLO target line
   - Breakdown by endpoint

5. **Incident Impact**
   - Timeline of incidents
   - Duration and impact on SLO
   - MTTR (Mean Time To Recovery)

## SLO Review Process

### Weekly Review

- Check SLO compliance for past week
- Review error budget consumption
- Identify trends and patterns
- Create tickets for improvements

### Monthly Review

- Calculate monthly SLO achievement
- Analyze SLO breaches
- Review incident post-mortems
- Adjust SLOs if needed

### Quarterly Review

- Review SLO definitions
- Adjust targets based on business needs
- Update alert thresholds
- Plan reliability improvements

## Implementation Checklist

### For Each Service

- [ ] Define service tier (Critical/High/Medium)
- [ ] Set SLO targets (availability, latency, success rate)
- [ ] Implement health checks
- [ ] Add Prometheus metrics
- [ ] Configure alerts
- [ ] Create Grafana dashboard
- [ ] Document in service README
- [ ] Set up on-call rotation
- [ ] Create runbook
- [ ] Test alert routing

## Best Practices

### 1. Start Conservative

- Begin with achievable SLOs (e.g., 99.5%)
- Increase targets as reliability improves
- Don't over-promise on new services

### 2. Measure What Matters

- Focus on user-facing metrics
- Don't create vanity metrics
- Align SLIs with business objectives

### 3. Balance Reliability and Velocity

- Use error budgets to inform decisions
- Don't sacrifice all velocity for 100% reliability
- 99.9% is often better than 99.99% (cost/benefit)

### 4. Learn from Incidents

- Every SLO breach is a learning opportunity
- Update runbooks after incidents
- Adjust alerts to catch issues earlier

### 5. Communicate Clearly

- Share SLO status with stakeholders
- Explain error budget policy
- Celebrate reliability wins

## Example: Crop Health AI Service

### SLO Definition

```yaml
service: crop-health-ai
tier: high
slos:
  availability:
    target: 99.9%
    window: 30d

  latency:
    target_p95: 1s
    window: 5m

  success_rate:
    target: 99.5%
    window: 30d

  data_freshness:
    target: 5m
    metric: last_prediction_timestamp
```

### Alerts

```yaml
groups:
  - name: crop_health_ai_slo
    rules:
      - alert: CropHealthAI_AvailabilityBreach
        expr: |
          (
            avg_over_time(up{service="crop-health-ai"}[30m])
          ) < 0.999
        for: 5m
        labels:
          severity: critical
          service: crop-health-ai
        annotations:
          summary: "Crop Health AI availability below SLO"

      - alert: CropHealthAI_LatencyBreach
        expr: |
          histogram_quantile(0.95,
            rate(service_request_duration_seconds_bucket{service="crop-health-ai"}[30m])
          ) > 1
        for: 15m
        labels:
          severity: warning
          service: crop-health-ai
        annotations:
          summary: "Crop Health AI P95 latency above 1s"

      - alert: CropHealthAI_ErrorBudgetLow
        expr: |
          (
            1 - (
              sum(increase(service_requests_total{service="crop-health-ai",status=~"5.."}[30d]))
              /
              sum(increase(service_requests_total{service="crop-health-ai"}[30d]))
            )
          ) / 0.001 < 0.25
        labels:
          severity: warning
          service: crop-health-ai
        annotations:
          summary: "Crop Health AI error budget below 25%"
```

## Resources

- [Google SRE Book - Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Prometheus Alerting Best Practices](https://prometheus.io/docs/practices/alerting/)
- [Grafana SLO Dashboards](https://grafana.com/grafana/dashboards/slo/)
