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


## Autoscaling + Observability (Best Option)

Install Metrics Server + kube-prometheus-stack + prometheus-adapter:

```bash
./k8s/addons/install-autoscaling-observability.sh
```

Then install SAHOOL Helm chart:

```bash
helm upgrade --install sahool-kernel k8s/helm/sahool-kernel -n sahool --create-namespace
```

Validate HPA:

```bash
kubectl get hpa -n sahool
kubectl top pods -n sahool
```
