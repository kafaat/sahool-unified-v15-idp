# SAHOOL IDP (GitOps)

1. Replace repo URL placeholders:

- `gitops/argocd/applications/idp-root-app.yaml`
- `gitops/idp/applications/backstage-app.yaml`

2. Apply:

```bash
kubectl apply -f gitops/argocd/applications/idp-root-app.yaml
```

3. Access Backstage:

```bash
kubectl -n backstage port-forward svc/backstage 7007:7007
```
