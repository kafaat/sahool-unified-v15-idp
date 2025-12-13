# Multi-cluster with Argo CD ApplicationSet

1) Ensure ApplicationSet controller is enabled in Argo CD.
2) Register clusters in Argo CD and label them:
   - sahool/enabled=true
   - region=...
3) Replace repo URL placeholders.
4) Apply the ApplicationSet:
```bash
kubectl apply -f gitops/argocd/applicationsets/sahool-multicluster-appset.yaml
```
