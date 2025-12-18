# SAHOOL GitOps: Rollouts Analysis + Auto-Rollback

This repo ships production GitOps with **Argo CD** + **Argo Rollouts** and an **AnalysisTemplate** per service.

## What you get
- Canary releases via `kind: Rollout` (Helm)
- Automatic analysis during canary steps
- Automatic abort/rollback when analysis fails

## Prereqs
- Argo CD installed (included via app-of-apps)
- Argo Rollouts installed (included via app-of-apps)
- Prometheus installed (kube-prometheus-stack app)

## How it works
Each service rollout references:

- `AnalysisTemplate: <release>-<service>-analysis`
- Prometheus queries:
  - CPU per pod (works out of the box)
  - Optional HTTP 5xx ratio (requires `http_requests_total`)
  - Optional latency p95 (requires `http_request_duration_seconds_bucket`)

You can tune thresholds in:
`k8s/helm/sahool-kernel/values.yaml` under `rollouts.analysis.*`

## Verify
```bash
kubectl get rollout -n sahool
kubectl argo rollouts get rollout sahool-auth-service -n sahool
kubectl argo rollouts list rollouts -n sahool
kubectl get analysistemplate -n sahool
```

## Notes
If your services do not export the optional HTTP metrics yet, keep the thresholds permissive or disable them by setting:
- `rollouts.analysis.http5xx.failureCondition` to a very high value, or
- remove the metric from `templates/analysis-templates.yaml`.

