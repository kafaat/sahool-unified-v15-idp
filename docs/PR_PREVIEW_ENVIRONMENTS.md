# PR Preview Environments (Argo CD ApplicationSet)

Date: 2025-12-13

This adds **automatic ephemeral environments** per Pull Request.

## How it works
- A GitHub webhook (or periodic poll) provides PR metadata
- Argo CD **ApplicationSet** uses the `pullRequest` generator to create an `Application` per PR
- Each PR gets a namespace like: `pr-<number>-sahool`
- When PR closes, Argo prunes the preview environment

## Requirements
- Argo CD ApplicationSet controller enabled
- Argo CD configured with GitHub token secret for PR generator
- Your repo structure contains:
  - Helm chart at: `k8s/helm/sahool-kernel`
  - Values overlay for preview at: `gitops/environments/preview/values.yaml`

## Files included
- `gitops/environments/preview/values.yaml`
- `gitops/argocd/applicationsets/sahool-pr-previews-appset.yaml`
- `gitops/argocd/secrets/github-pr-generator-secret.yaml` (template)
- `gitops/scripts/install-pr-previews.sh`

## Install
1) Create GitHub token secret (read-only):
```bash
kubectl apply -f gitops/argocd/secrets/github-pr-generator-secret.yaml
```

2) Apply the ApplicationSet:
```bash
kubectl apply -f gitops/argocd/applicationsets/sahool-pr-previews-appset.yaml
```

## Notes
- For security, use a GitHub token scoped minimally (repo read, PR read).
- Preview values should use smaller replicas & cheaper resources.
