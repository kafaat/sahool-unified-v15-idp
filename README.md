# SAHOOL Internal Developer Platform (IDP) Add-on Pack

This add-on pack extends your **Microservices + SaaS + HCI** platform with an **Internal Developer Platform**:
- Developer Portal (Backstage) + Catalog
- Golden Paths (service templates)
- Self-service scaffolding (create service + GitOps wiring)
- Local internal dev cluster bootstrap (k3d) for fast iteration
- Policy guardrails hooks (Kyverno-ready)

## What you get
- `idp/backstage/` : Backstage app + deployment manifests + catalog
- `idp/templates/` : service scaffolder templates (FastAPI + Node/Nest-ish)
- `idp/sahoolctl/` : `sahoolctl` CLI to scaffold and wire services
- `dev/` : k3d-based internal dev environment (HCI-friendly patterns)
- `gitops/` : Argo CD applications to install Backstage (and optional Crossplane later)

## Quick start (internal dev env)
1) Create a local cluster:
```bash
./dev/k3d/create-cluster.sh
```

2) Install baseline platform (Argo CD / observability / policies) using your existing GitOps root-app,
then install IDP apps:
```bash
kubectl apply -f gitops/argocd/applications/idp-root-app.yaml
```

3) Open Backstage:
```bash
kubectl -n backstage port-forward svc/backstage 7007:7007
# open http://localhost:7007
```

## Notes
- This pack is designed to be dropped into your unified repo and committed.
- Replace `REPLACE_WITH_YOUR_REPO_URL` occurrences.
- Default namespace for Backstage: `backstage`.

Generated: 2025-12-13
