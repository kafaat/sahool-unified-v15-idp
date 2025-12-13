# PR Preview URLs (Ingress + Internal DNS)

This enables a **stable URL per Pull Request**, e.g.:
- https://pr-123.sahool.internal

## Components
- Ingress-NGINX
- cert-manager (internal CA)
- wildcard DNS: *.sahool.internal -> ingress IP
- ApplicationSet injects PR number into hostnames

## Flow
PR opened -> Argo Application created -> Ingress created -> URL available
PR closed -> resources pruned -> URL removed
