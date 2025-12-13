# SAHOOL Kernel on Kubernetes (Helm)

## Build images (example)
You will need to build/push images to a registry accessible by your cluster.

Example naming used by the chart:
- `<repo>-image-diagnosis:<tag>`
- `<repo>-disease-risk:<tag>`

Set in `values.yaml`:
- `image.repository`
- `image.tag`

## Install
```bash
helm install sahool ./k8s/helm/sahool-kernel
```

## Notes
- This Helm chart deploys: NATS, Redis, image-diagnosis, disease-risk (minimal set).
- Observability can be deployed separately (Tempo/Loki/Grafana/Collector).
