# SAHOOL - All Enhancements Added

This repo includes:
- IDP (Backstage + templates + sahoolctl)
- Secrets GitOps (External Secrets Operator + examples)
- Billing & quotas skeleton (billing-core)
- Feature flags baseline (flagd + OpenFeature guidance)
- Multi-cluster deployment (Argo CD ApplicationSet)

## Apply apps (single-cluster)
```bash
kubectl apply -f gitops/argocd/applications/external-secrets-app.yaml
kubectl apply -f gitops/argocd/applications/secrets-root-app.yaml
kubectl apply -f gitops/argocd/applications/idp-root-app.yaml
kubectl apply -f gitops/argocd/applications/billing-core-app.yaml
kubectl apply -f gitops/argocd/applications/feature-flags-app.yaml
```

## Multi-cluster
Apply ApplicationSet:
```bash
kubectl apply -f gitops/argocd/applicationsets/sahool-multicluster-appset.yaml
```


## PR Preview Environments
```bash
./gitops/scripts/install-pr-previews.sh
```
See `docs/PR_PREVIEW_ENVIRONMENTS.md`.
