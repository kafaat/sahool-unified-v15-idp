# SAHOOL Deployment Strategies

This document describes the deployment strategies implemented for SAHOOL, including canary deployments, blue-green deployments, and emergency rollback procedures.

## Table of Contents

- [Overview](#overview)
- [Deployment Strategies](#deployment-strategies)
  - [Canary Deployment](#canary-deployment)
  - [Blue-Green Deployment](#blue-green-deployment)
  - [Rolling Update](#rolling-update)
- [Traffic Management](#traffic-management)
- [Metrics and Analysis](#metrics-and-analysis)
- [Promotion Procedures](#promotion-procedures)
- [Rollback Procedures](#rollback-procedures)
- [Emergency Procedures](#emergency-procedures)
- [Monitoring and Alerts](#monitoring-and-alerts)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

## Overview

SAHOOL uses advanced deployment strategies to ensure zero-downtime releases and minimize risk when deploying new versions. Our deployment infrastructure leverages:

- **Argo Rollouts** - Advanced deployment controller for Kubernetes
- **Istio Service Mesh** - Traffic management and observability
- **Prometheus** - Metrics collection and analysis
- **Automated Analysis** - Metric-based promotion and rollback decisions

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Ingress Gateway                         │
│                     (Istio/NGINX)                           │
└────────────┬────────────────────────────┬───────────────────┘
             │                            │
             ▼                            ▼
    ┌────────────────┐          ┌────────────────┐
    │ Stable Service │          │ Canary Service │
    │   (100% - X%)  │          │     (X%)       │
    └────────┬───────┘          └───────┬────────┘
             │                           │
             ▼                           ▼
    ┌────────────────┐          ┌────────────────┐
    │ Stable Pods    │          │ Canary Pods    │
    │   (v1.0.0)     │          │   (v1.1.0)     │
    └────────────────┘          └────────────────┘
             │                           │
             └───────────┬───────────────┘
                         ▼
                 ┌───────────────┐
                 │  Prometheus   │
                 │  (Analysis)   │
                 └───────────────┘
```

## Deployment Strategies

### Canary Deployment

Canary deployment gradually shifts traffic from the stable version to the new version while monitoring metrics. If the new version performs well, traffic is gradually increased until the canary becomes the new stable version.

#### When to Use

- **Production deployments** - Minimize risk by testing with small user percentage
- **High-traffic services** - Ensure new version handles production load
- **Critical services** - Detect issues before full rollout
- **Feature validation** - Validate new features with real users

#### How It Works

1. **Initial Deployment** (5% traffic)
   - Deploy canary pods alongside stable pods
   - Route 5% of traffic to canary
   - Monitor metrics for 2 minutes

2. **Gradual Increase** (20% → 40% → 60% → 80%)
   - Incrementally increase traffic to canary
   - Run automated analysis at each step
   - Pause 5 minutes between steps

3. **Final Analysis** (before 100%)
   - Comprehensive metric validation
   - Success rate, latency, error rate checks
   - CPU and memory utilization verification

4. **Promotion**
   - Shift 100% traffic to canary
   - Update stable deployment
   - Scale down old version

#### Configuration

```yaml
# helm/charts/sahool-agent/values.yaml
canary:
  enabled: true
  replicaCount: 1
  version: "1.1.0"

rollout:
  enabled: true
  strategy: canary
  canary:
    steps:
    - setWeight: 5
    - pause: {duration: 2m}
    - setWeight: 20
    - pause: {duration: 5m}
    # ... more steps
```

#### Manual Deployment

```bash
# Deploy canary version
helm upgrade sahool-agent ./helm/charts/sahool-agent \
  --namespace sahool \
  --set canary.enabled=true \
  --set canary.version=1.1.0 \
  --wait

# Monitor rollout
kubectl argo rollouts get rollout sahool-agent -n sahool --watch

# Promote manually (if auto-promotion disabled)
./scripts/deploy/canary-promote.sh --namespace sahool --service sahool-agent
```

### Blue-Green Deployment

Blue-Green deployment runs two identical production environments (Blue = current, Green = new). Traffic is switched from Blue to Green after validation.

#### When to Use

- **Database migrations** - Ensure schema compatibility before switching
- **Major version updates** - Test complete environment before cutover
- **Instant rollback required** - Immediate switch back to previous version
- **Regulatory requirements** - Full environment validation needed

#### How It Works

1. **Deploy Green Environment**
   - Deploy new version in preview mode
   - Keep Blue (stable) handling all traffic
   - Run smoke tests on Green

2. **Validation**
   - Run automated tests against Green
   - Manual validation if required
   - Performance testing

3. **Switch Traffic**
   - Instantly route 100% traffic to Green
   - Blue remains running for quick rollback
   - Monitor Green for issues

4. **Cleanup**
   - After stabilization period, scale down Blue
   - Green becomes new Blue for next deployment

#### Configuration

```yaml
rollout:
  enabled: true
  strategy: blueGreen
  blueGreen:
    autoPromotionEnabled: false
    autoPromotionSeconds: 300
    scaleDownDelaySeconds: 30
    previewReplicaCount: 3
```

#### Manual Deployment

```bash
# Deploy green version
helm upgrade sahool-agent ./helm/charts/sahool-agent \
  --namespace sahool \
  --set rollout.strategy=blueGreen \
  --set image.tag=1.1.0

# Preview the new version
kubectl argo rollouts get rollout sahool-agent -n sahool

# Promote to production
kubectl argo rollouts promote sahool-agent -n sahool

# Rollback if needed (immediate)
kubectl argo rollouts undo sahool-agent -n sahool
```

### Rolling Update

Standard Kubernetes rolling update with configurable surge and unavailability.

#### When to Use

- **Non-critical services** - Lower risk services
- **Internal services** - Services not facing end users
- **Configuration changes** - Simple config updates
- **Development/staging** - Non-production environments

#### Configuration

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 25%
    maxUnavailable: 0
```

## Traffic Management

### Istio Virtual Service

Traffic routing is controlled via Istio VirtualService with support for:

#### Weight-Based Routing

```yaml
# Automatically managed by Argo Rollouts
- route:
  - destination:
      host: sahool-agent-canary
      subset: canary
    weight: 20  # 20% to canary
  - destination:
      host: sahool-agent-stable
      subset: stable
    weight: 80  # 80% to stable
```

#### Header-Based Routing

```bash
# Test canary version with specific header
curl -H "X-Canary: true" https://api.sahool.io/endpoint

# Beta users automatically routed to canary
curl -H "Cookie: beta_user=true" https://api.sahool.io/endpoint
```

#### Traffic Mirroring

```yaml
# Mirror 10% of traffic to canary for testing (shadow traffic)
mirror:
  host: sahool-agent-canary
  subset: canary
mirrorPercentage:
  value: 10.0
```

### Manual Traffic Control

```bash
# Update traffic weights manually
kubectl patch virtualservice sahool-agent -n sahool --type='json' \
  -p='[{"op": "replace", "path": "/spec/http/0/route/0/weight", "value": 50}]'

# Set all traffic to stable (emergency)
kubectl patch virtualservice sahool-agent -n sahool --type='json' \
  -p='[{"op": "replace", "path": "/spec/http/0/route/0/weight", "value": 0},
       {"op": "replace", "path": "/spec/http/0/route/1/weight", "value": 100}]'
```

## Metrics and Analysis

### Automated Analysis Templates

Our Argo Rollouts configuration includes several analysis templates:

#### Success Rate Analysis

```yaml
# Threshold: 95% success rate
successCondition: result[0] >= 0.95
query: |
  sum(rate(http_requests_total{status=~"2.."}[5m])) /
  sum(rate(http_requests_total[5m]))
```

#### Latency Analysis (P95)

```yaml
# Threshold: 500ms
successCondition: result[0] <= 500
query: |
  histogram_quantile(0.95,
    sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
  ) * 1000
```

#### Error Rate Analysis

```yaml
# Threshold: 5% error rate
successCondition: result[0] <= 0.05
query: |
  sum(rate(http_requests_total{status=~"5.."}[5m])) /
  sum(rate(http_requests_total[5m]))
```

#### CPU/Memory Analysis

```yaml
# Threshold: 80% utilization
successCondition: result[0] <= 0.8
```

### Custom Metrics

Add custom metrics to analysis:

```yaml
analysis:
  templates:
  - templateName: custom-business-metric
  args:
  - name: metric-threshold
    value: "1000"
```

## Promotion Procedures

### Automated Promotion

When analysis passes all checks, Argo Rollouts automatically promotes:

```yaml
rollout:
  canary:
    steps:
    # ... traffic steps
    - analysis:
        templates:
        - templateName: sahool-agent-success-rate
        - templateName: sahool-agent-latency
```

### Manual Promotion

Use our promotion script:

```bash
# Standard promotion with verification
./scripts/deploy/canary-promote.sh \
  --namespace sahool \
  --service sahool-agent

# Dry run to preview changes
./scripts/deploy/canary-promote.sh --dry-run

# Force promotion (skip checks)
./scripts/deploy/canary-promote.sh --force --skip-metrics

# Custom thresholds
./scripts/deploy/canary-promote.sh \
  --threshold 0.99 \
  --wait 600
```

### Promotion Checklist

Before manual promotion:

- [ ] All canary pods are healthy
- [ ] Success rate >= 95%
- [ ] Error rate <= 5%
- [ ] P95 latency within acceptable range
- [ ] No crash loops or OOM kills
- [ ] Traffic has been at high percentage (>60%) for at least 10 minutes
- [ ] No alerts firing for the canary deployment

## Rollback Procedures

### Automated Rollback

Argo Rollouts automatically rolls back when:

- Analysis run fails
- Pod readiness probes fail consistently
- Progress deadline exceeded

### Manual Rollback

#### Quick Rollback (Traffic Only)

```bash
# Immediately shift all traffic to stable
./scripts/deploy/rollback.sh \
  --type traffic \
  --immediate \
  --force
```

#### Full Rollback

```bash
# Standard rollback with verification
./scripts/deploy/rollback.sh \
  --namespace sahool \
  --service sahool-agent

# Rollback to specific revision
./scripts/deploy/rollback.sh \
  --revision 5

# Zero-downtime rollback
./scripts/deploy/rollback.sh \
  --zero-downtime
```

#### Using Argo Rollouts CLI

```bash
# Abort current rollout
kubectl argo rollouts abort sahool-agent -n sahool

# Undo to previous revision
kubectl argo rollouts undo sahool-agent -n sahool

# Undo to specific revision
kubectl argo rollouts undo sahool-agent -n sahool --to-revision=3

# Check status
kubectl argo rollouts status sahool-agent -n sahool
```

## Emergency Procedures

### Critical Production Issue

When a critical issue is detected in production:

1. **Immediate Traffic Shift** (< 30 seconds)
   ```bash
   ./scripts/deploy/rollback.sh --immediate --force --notify
   ```

2. **Verify Rollback**
   ```bash
   # Check pod status
   kubectl get pods -n sahool -l app=sahool-agent

   # Check service health
   kubectl run test-curl --rm -i --restart=Never --image=curlimages/curl -- \
     curl -f http://sahool-agent:8080/health/ready
   ```

3. **Incident Response**
   - Create incident in PagerDuty
   - Notify team in Slack
   - Document the issue
   - Schedule post-mortem

### Canary Causing Issues

If canary is causing issues but not auto-rolling back:

```bash
# 1. Reduce canary traffic to 0%
kubectl argo rollouts set weight sahool-agent 0 -n sahool

# 2. Scale down canary
kubectl scale deployment sahool-agent-canary -n sahool --replicas=0

# 3. Abort the rollout
kubectl argo rollouts abort sahool-agent -n sahool
```

### Database Migration Failure

If database migration fails during deployment:

```bash
# 1. Rollback deployment
./scripts/deploy/rollback.sh --immediate

# 2. Rollback database migration
kubectl exec -it deployment/sahool-agent-stable -n sahool -- \
  npm run migrate:rollback

# 3. Verify database state
kubectl exec -it deployment/sahool-agent-stable -n sahool -- \
  npm run migrate:status
```

### Network/Service Mesh Issues

If Istio or traffic routing has issues:

```bash
# 1. Check Istio proxy status
kubectl get pods -n sahool -l app=sahool-agent \
  -o jsonpath='{.items[*].status.containerStatuses[?(@.name=="istio-proxy")].ready}'

# 2. Restart Envoy sidecar
kubectl rollout restart deployment/sahool-agent-stable -n sahool

# 3. Bypass service mesh (emergency only)
kubectl patch deployment sahool-agent-stable -n sahool \
  -p '{"spec":{"template":{"metadata":{"annotations":{"sidecar.istio.io/inject":"false"}}}}}'
```

## Monitoring and Alerts

### Key Metrics

Monitor these metrics during deployments:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Success Rate | < 95% | Auto-rollback |
| Error Rate | > 5% | Auto-rollback |
| P95 Latency | > 1000ms | Warning |
| P99 Latency | > 2000ms | Investigation |
| CPU Utilization | > 80% | Scale up |
| Memory Utilization | > 80% | Scale up |
| Pod Restarts | > 3 in 15min | Rollback |

### Alert Hierarchy

1. **Critical (Page)** - Immediate action required
   - RolloutFailed
   - CanaryHighErrorRate
   - CanarySLOViolation
   - CanaryOOMKilled

2. **Warning (Slack)** - Investigate within 1 hour
   - RolloutDegraded
   - CanaryHighLatency
   - CanaryHighCPU
   - CanaryHighMemory

3. **Info (Dashboard)** - Informational only
   - RolloutProgressing
   - CanaryTrafficIncreased

### Dashboards

Access monitoring dashboards:

- **Rollout Dashboard**: https://grafana.sahool.io/d/rollouts
- **Service Dashboard**: https://grafana.sahool.io/d/services
- **Canary Analysis**: https://grafana.sahool.io/d/canary-analysis

### Logs

View deployment logs:

```bash
# Rollout controller logs
kubectl logs -n argo-rollouts deployment/argo-rollouts -f

# Service logs (stable)
kubectl logs -n sahool deployment/sahool-agent-stable -f

# Service logs (canary)
kubectl logs -n sahool deployment/sahool-agent-canary -f

# All service logs
kubectl logs -n sahool -l app=sahool-agent -f --max-log-requests=10
```

## Best Practices

### Pre-Deployment

1. **Test Thoroughly**
   - Run all unit tests
   - Run integration tests
   - Run E2E tests in staging
   - Perform load testing

2. **Review Changes**
   - Code review completed
   - Database migrations reviewed
   - Configuration changes validated
   - Dependencies updated and tested

3. **Prepare Rollback Plan**
   - Document rollback procedure
   - Test rollback in staging
   - Identify rollback owner
   - Prepare communication plan

### During Deployment

1. **Monitor Actively**
   - Watch rollout progress
   - Monitor metrics dashboard
   - Check logs for errors
   - Verify traffic distribution

2. **Communicate**
   - Announce deployment in Slack
   - Update status page
   - Keep stakeholders informed
   - Document any issues

3. **Be Ready to Rollback**
   - Have rollback script ready
   - Monitor alert channels
   - Keep PagerDuty accessible
   - Don't leave deployment unattended

### Post-Deployment

1. **Verify Success**
   - Check all metrics returned to baseline
   - Verify no alerts firing
   - Test critical user flows
   - Review error logs

2. **Clean Up**
   - Scale down old canary
   - Remove obsolete resources
   - Update documentation
   - Close deployment ticket

3. **Learn and Improve**
   - Document what worked well
   - Note any issues encountered
   - Update runbooks
   - Share knowledge with team

### Deployment Windows

Recommended deployment windows:

- **Production**: Tuesday-Thursday, 10:00-15:00 (business hours)
- **Staging**: Anytime
- **Avoid**: Fridays, weekends, holidays, major sales events

### Change Freeze

Do not deploy during:

- Major sales/promotional events
- End of quarter/year
- Known high-traffic periods
- Active incidents
- During change freeze periods

## Troubleshooting

### Common Issues

#### Rollout Stuck in Progressing

**Symptoms**: Rollout shows "Progressing" for extended time

**Diagnosis**:
```bash
kubectl argo rollouts get rollout sahool-agent -n sahool
kubectl describe rollout sahool-agent -n sahool
```

**Solutions**:
1. Check if analysis is running: `kubectl get analysisrun -n sahool`
2. Check pod status: `kubectl get pods -n sahool -l app=sahool-agent`
3. Abort and retry: `kubectl argo rollouts abort sahool-agent -n sahool`

#### Analysis Run Failing

**Symptoms**: Analysis runs consistently fail

**Diagnosis**:
```bash
kubectl get analysisrun -n sahool
kubectl describe analysisrun <name> -n sahool
```

**Solutions**:
1. Check Prometheus connectivity
2. Verify metric queries are correct
3. Review metric thresholds
4. Check if service is receiving traffic

#### Canary Pods Not Ready

**Symptoms**: Canary pods fail readiness probe

**Diagnosis**:
```bash
kubectl get pods -n sahool -l deployment-type=canary
kubectl describe pod <pod-name> -n sahool
kubectl logs <pod-name> -n sahool
```

**Solutions**:
1. Check application logs for errors
2. Verify database connectivity
3. Check secret/configmap availability
4. Review resource limits

#### Traffic Not Routing to Canary

**Symptoms**: All traffic goes to stable despite weight settings

**Diagnosis**:
```bash
kubectl get virtualservice sahool-agent -n sahool -o yaml
kubectl get destinationrule sahool-agent -n sahool -o yaml
```

**Solutions**:
1. Verify VirtualService weights are set correctly
2. Check DestinationRule subsets match labels
3. Verify Istio proxy is injected: `kubectl get pods -n sahool -o jsonpath='{.items[*].spec.containers[*].name}'`
4. Check Istio pilot logs

### Debug Commands

```bash
# Get rollout details
kubectl argo rollouts get rollout sahool-agent -n sahool

# View rollout history
kubectl argo rollouts history sahool-agent -n sahool

# Get analysis runs
kubectl get analysisrun -n sahool

# Describe specific analysis run
kubectl describe analysisrun <name> -n sahool

# Check Istio configuration
istioctl analyze -n sahool

# View Envoy configuration
kubectl exec -it <pod-name> -n sahool -c istio-proxy -- \
  pilot-agent request GET config_dump

# Test service connectivity
kubectl run test-curl --rm -i --restart=Never --image=curlimages/curl -n sahool -- \
  curl -v http://sahool-agent:8080/health
```

## Support and Resources

### Documentation

- [Argo Rollouts Documentation](https://argoproj.github.io/argo-rollouts/)
- [Istio Traffic Management](https://istio.io/latest/docs/concepts/traffic-management/)
- [Prometheus Querying](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [SAHOOL Architecture](./INFRASTRUCTURE.md)

### Runbooks

- [Rollout Degraded](https://docs.sahool.io/runbooks/rollout-degraded)
- [Rollout Failed](https://docs.sahool.io/runbooks/rollout-failed)
- [Canary High Error Rate](https://docs.sahool.io/runbooks/canary-high-error-rate)
- [Emergency Rollback](https://docs.sahool.io/runbooks/emergency-rollback)

### Support Channels

- **Slack**: #deployments, #platform-team
- **PagerDuty**: Platform Team
- **Email**: platform-team@sahool.io

### Emergency Contacts

- **Platform Team Lead**: platform-lead@sahool.io
- **SRE On-Call**: oncall@sahool.io
- **DevOps Team**: devops@sahool.io

---

**Document Version**: 1.0.0
**Last Updated**: 2025-12-28
**Owner**: Platform Team
**Review Cycle**: Quarterly
