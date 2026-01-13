# Multi-Region / Multi-Cluster (HCI)

Included:

- Argo CD ApplicationSet to deploy SAHOOL to multiple clusters
- Cluster registry pattern for on-prem HCI

Approach:

- Register clusters in Argo CD
- Use ApplicationSet to target clusters by labels (region=tehama, region=jawf, etc.)
- Environment overlays remain in git (`gitops/environments/*`)

This is safer than Kubernetes federation for most ops teams.
