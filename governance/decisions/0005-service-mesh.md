# ADR-0005: Service Mesh Strategy

- **Status**: Accepted
- **Date**: 2026-04-02
- **Deciders**: Platform Architecture Team, Infrastructure Team

## Context

> السياق | Context

SAHOOL operates 72+ microservices in Kubernetes with inter-service communication via HTTP and NATS. As the platform scales, we need a strategy for secure service-to-service communication, observability, and traffic management.

Key requirements:
1. **mTLS** — Encrypt all service-to-service communication
2. **Observability** — Distributed tracing across service boundaries
3. **Traffic management** — Canary deployments, traffic splitting
4. **Access control** — Service-level authorization policies
5. **Operational simplicity** — Minimize operational burden

Options considered:
- **A) Istio** — Full-featured service mesh (sidecar proxy)
- **B) Linkerd** — Lightweight service mesh (Rust proxy)
- **C) Kong Mesh / Kuma** — Kong-native mesh
- **D) No mesh — Application-level** — TLS + Kong gateway only

## Decision

> القرار | Decision

We adopt a **phased approach**, starting with **Option D (Application-level)** and migrating to **Option A (Istio)** as operational maturity increases:

### Phase 1: Current (Application-Level Security)

| Layer | Mechanism | Status |
|-------|-----------|--------|
| **External traffic** | Kong API Gateway with TLS termination | ✅ Production |
| **Service-to-service** | Internal Kubernetes networking (ClusterIP) | ✅ Production |
| **Authentication** | JWT tokens validated by each service | ✅ Production |
| **Observability** | OpenTelemetry SDK in each service | ✅ Production |
| **Rate limiting** | Kong rate-limiting plugin + shared middleware | ✅ Production |

### Phase 2: Network Policies (Next)

| Layer | Mechanism | Status |
|-------|-----------|--------|
| **Network isolation** | Kubernetes NetworkPolicy per namespace | 🔄 Kyverno audit mode |
| **Pod-to-pod** | Default deny + explicit allow rules | 🔄 Planned |
| **Egress control** | Restrict outbound traffic to approved destinations | 🔄 Planned |

### Phase 3: Istio Service Mesh (Future)

| Layer | Mechanism | Status |
|-------|-----------|--------|
| **mTLS** | Istio automatic mTLS (STRICT mode) | 📋 Planned |
| **Authorization** | Istio AuthorizationPolicy (service-level RBAC) | 📋 Planned |
| **Traffic management** | VirtualService, DestinationRule for canary/blue-green | 📋 Planned |
| **Observability** | Envoy proxy metrics + Kiali dashboard | 📋 Planned |

### Decision Rationale

1. **Phase 1** is sufficient for current scale (< 100 services, single cluster)
2. **Phase 2** (NetworkPolicy) provides significant security improvement with minimal operational complexity
3. **Phase 3** (Istio) adds mTLS and advanced traffic management when the platform reaches multi-cluster or requires strict zero-trust networking
4. Premature Istio adoption would add unnecessary operational complexity

### Kyverno Enforcement

New Kyverno policies enforce Phase 2 preparation:
- `require-network-policy.yaml` — Audits namespaces without NetworkPolicy
- `require-pod-disruption-budget.yaml` — Audits production deployments without PDB

## Consequences

> النتائج | Consequences

### Positive

- **Incremental adoption** — Each phase adds security without disruption
- **Low initial cost** — Phase 1 uses existing Kong + OTel infrastructure
- **Kyverno alignment** — Network policies enforced via existing Kyverno framework
- **Future-ready** — Istio configuration directory exists at `infrastructure/istio/`

### Negative

- **No mTLS yet** — Service-to-service traffic is unencrypted within the cluster (Phase 1)
- **Manual network policies** — Phase 2 requires per-namespace policy definitions
- **Deferred complexity** — Istio migration (Phase 3) will require significant effort

### Mitigations

- **Cluster isolation** — Kubernetes namespaces + RBAC provide baseline isolation
- **Kong proxy** — External traffic is always encrypted via TLS
- **Monitoring** — OpenTelemetry traces detect unauthorized cross-service calls
- **Istio prep** — `infrastructure/istio/` directory maintained for future readiness

## Related

- [Kyverno Policies](../policies/kyverno/)
- [Kong Gateway](../../infrastructure/gateway/kong/)
- [Istio Config](../../infrastructure/istio/)
- [OpenTelemetry](../../shared/observability/)
- [Security Policies](../../infrastructure/security/security-policies.yaml)
