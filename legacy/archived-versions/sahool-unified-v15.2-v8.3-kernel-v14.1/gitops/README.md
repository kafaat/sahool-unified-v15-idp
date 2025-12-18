# SAHOOL GitOps (Argo CD)

This folder enables **GitOps deployments** for SAHOOL using **Argo CD** with an **App-of-Apps** pattern.

## What you get
- A dedicated `AppProject` and namespaces
- A root Argo CD `Application` that deploys:
  - SAHOOL (Helm) into the `sahool` namespace
  - Observability stack (optional) into `observability`
- Environment separation via `gitops/environments/{dev,staging,prod}` value files

## 1) Install Argo CD
> Run once per cluster.

```bash
kubectl create namespace argocd || true
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

(Optional) Port-forward:
```bash
kubectl -n argocd port-forward svc/argocd-server 8080:443
```

Get initial admin password:
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d && echo
```

## 2) Bootstrap SAHOOL GitOps apps
```bash
kubectl apply -f gitops/argocd/namespace.yaml
kubectl apply -f gitops/argocd/project-sahool.yaml
kubectl apply -f gitops/argocd/applications/root-app.yaml
```

## 3) Choose environment
By default, `root-app.yaml` points to **prod** values.
To switch:
- Edit `gitops/argocd/applications/sahool-kernel-app.yaml`
- Replace the `valueFiles` entry to:
  - `gitops/environments/dev/values.yaml`, or
  - `gitops/environments/staging/values.yaml`

## Notes
- This setup assumes the repo is accessible by Argo CD (same repo you commit/push to).
- If your repo is private, add a repo credential secret in Argo CD (see Argo CD docs).
