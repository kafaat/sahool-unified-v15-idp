# SAHOOL v16 Security Checklist

## Pre-Deployment

- [ ] NATS authentication: bcrypt hashes in production (`nats-secure.conf`)
- [ ] TLS certificates: valid and not expired
- [ ] Secrets: rotated and stored in HashiCorp Vault
- [ ] RLS: enabled on all tenant tables
- [ ] mTLS: configured in Istio (`PeerAuthentication` STRICT mode)
- [ ] Images: scanned with Trivy (no critical CVEs)
- [ ] Dependencies: no known CVEs (`safety check`)

## Runtime

- [ ] Audit logging: enabled
- [ ] Rate limiting: configured per tier
- [ ] Circuit breakers: active (AI service)
- [ ] Health checks: all services passing
- [ ] Metrics: Prometheus collecting
- [ ] Alerts: Grafana rules configured

## Compliance

- [ ] Data retention: 7 years for audit stream (`SAHOOL_AUDIT`)
- [ ] Tenant isolation: RLS policies verified
- [ ] Access logs: retained for 1 year
