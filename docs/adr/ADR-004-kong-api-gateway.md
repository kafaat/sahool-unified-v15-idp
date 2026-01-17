# ADR-004: Kong as API Gateway

## Status

Accepted

## Context

SAHOOL's microservices architecture requires a centralized API Gateway for:

1. **Traffic management**: Rate limiting, load balancing
2. **Authentication**: JWT validation, OAuth2 integration
3. **Observability**: Logging, metrics, tracing
4. **Security**: IP filtering, request transformation
5. **High availability**: Multi-node clustering, failover

We evaluated several API Gateway solutions for our agricultural platform.

## Decision

We chose **Kong Gateway** as our API Gateway solution with a 3-node HA cluster.

### Key Reasons

1. **Declarative configuration**: GitOps-friendly, version-controlled
2. **Plugin ecosystem**: Authentication, rate limiting, logging out of the box
3. **Performance**: Low latency, high throughput (10,000+ req/s per node)
4. **Kubernetes-native**: Easy deployment on K8s
5. **Open source**: Community edition sufficient for our needs
6. **Multi-tenancy**: Path-based routing per tenant

### Implementation Pattern

```yaml
# Kong declarative configuration
_format_version: "3.0"

services:
  - name: field-ops-service
    url: http://field-ops:8080
    routes:
      - name: field-ops-route
        paths:
          - /api/v1/field-ops
        strip_path: true
    plugins:
      - name: jwt
        config:
          key_claim_name: kid
          claims_to_verify:
            - exp
      - name: rate-limiting
        config:
          minute: 100
          policy: local

  - name: satellite-service
    url: http://satellite-service:8081
    routes:
      - name: satellite-route
        paths:
          - /api/v1/satellite
    plugins:
      - name: proxy-cache
        config:
          response_code:
            - 200
          request_method:
            - GET
          content_type:
            - application/json
          cache_ttl: 300
```

### HA Architecture

```
                   ┌──────────────┐
                   │   Nginx LB   │
                   │   (HAProxy)  │
                   └──────┬───────┘
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │ Kong Node 1│  │ Kong Node 2│  │ Kong Node 3│
   │  (Primary) │  │(Secondary) │  │ (Tertiary) │
   └─────┬──────┘  └─────┬──────┘  └─────┬──────┘
         └───────────────┼───────────────┘
                         ▼
              ┌─────────────────────┐
              │  PostgreSQL (Shared)│
              │   + Redis Cluster   │
              └─────────────────────┘
```

## Consequences

### Positive

- **Centralized gateway**: Single entry point for all services
- **Security layer**: JWT validation before reaching services
- **Rate limiting**: Protects services from abuse
- **Caching**: Reduces load on satellite imagery endpoints
- **Observability**: Prometheus metrics exposed on :8001
- **Failover**: Automatic node failover in HA mode

### Negative

- **Added latency**: ~1-2ms per request through gateway
- **Operational complexity**: Need to manage Kong cluster
- **Learning curve**: Plugin configuration takes time
- **Resource overhead**: Each Kong node requires ~512MB RAM

### Neutral

- PostgreSQL required for Kong clustering
- DB-less mode available for simpler deployments

## Alternatives Considered

### Alternative 1: Traefik

**Considered because:**

- Simpler configuration
- Built into many container orchestrators
- Lower resource footprint

**Rejected because:**

- Less mature plugin ecosystem
- Limited rate limiting options
- Less enterprise adoption in our region

### Alternative 2: AWS API Gateway

**Considered because:**

- Fully managed service
- Tight AWS integration

**Rejected because:**

- Vendor lock-in
- Expensive at our projected scale
- Less flexibility for custom plugins

### Alternative 3: Nginx + Custom Lua

**Rejected because:**

- High development effort
- Need to build all features from scratch
- Maintenance burden

## Configuration Patterns

### Multi-Tenant Routing

```yaml
routes:
  - name: tenant-route
    paths:
      - /api/v1/tenants/(?<tenant_id>[^/]+)
    plugins:
      - name: request-transformer
        config:
          add:
            headers:
              - X-Tenant-ID:$(uri_captures.tenant_id)
```

### Circuit Breaker Integration

The client-side circuit breaker (see `shared/python-lib/sahool_core/resilient_client.py`)
complements Kong's health checks:

```python
from sahool_core import circuit_breaker

result = await circuit_breaker.call(
    "field-ops",
    "/api/v1/fields"
)
```

## References

- [Kong Documentation](https://docs.konghq.com/)
- [Kong Declarative Configuration](https://docs.konghq.com/gateway/latest/production/deployment-topologies/db-less-and-declarative-config/)
- [SAHOOL Kong HA Setup](../infrastructure/KONG_HA_SETUP.md)
- [Circuit Breaker Pattern](../infrastructure/CIRCUIT_BREAKER.md)
