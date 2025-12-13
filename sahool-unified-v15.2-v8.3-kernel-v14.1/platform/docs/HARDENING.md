# Hardening Guide (v15.2)

## 1) Enable mTLS (dev bootstrap)
```bash
bash tools/security/gen_certs.sh
docker compose -f kernel/docker/docker-compose.yml -f kernel/docker/docker-compose.tls.override.yml up -d --build
```

> NOTE: TLS on NATS server is present as a config stub; enable it by uncommenting TLS block in `kernel/docker/nats-server.conf`.

## 2) Enable Auth for public endpoints
Set:
- `SAHOOL_AUTH_ENABLED=true`

Then protect endpoints in your public-facing services (Layer 3/4).
The kernel provides `shared/security/jwt.py` as a minimal gate.
For full verification, integrate `pyjwt` or `python-jose`.

## 3) K8s Deployment
Build & push images, set `values.yaml` accordingly, then:

```bash
helm install sahool ./k8s/helm/sahool-kernel
```
