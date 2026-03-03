# Architecture Evaluation: Vite SPA + Nginx + Node Sidecar

**Date**: 2026-03-01
**Status**: Evaluated - Not Recommended
**Evaluator**: Architecture Review

## Context

A "Vite SPA + Nginx reverse proxy + Node sidecar" architecture was proposed for evaluation against SAHOOL's current stack. This document records the analysis and decision.

### Proposed Architecture

- **Vite SPA**: Client-side rendered frontend
- **Nginx**: Static file server + reverse proxy to `/api/`
- **Node sidecar**: Dynamic RPC handler discovery at runtime
- **K8s manifests**: Raw Deployment/Service/HTTPRoute/Secret templates

---

## Current SAHOOL Architecture (Baseline)

| Aspect | Current Technology | Files |
|--------|-------------------|-------|
| Frontend Framework | Next.js 15 (App Router, SSR) | `apps/web/`, `apps/admin/` |
| Build Output | Next.js Standalone | `next.config.js` |
| API Proxy | Next.js rewrites → Kong | `next.config.js` → `rewrites()` |
| API Gateway | Kong 3.x (JWT, ACL, Rate Limiting, CORS, Bot Detection) | `infrastructure/gateway/kong/kong.yml` |
| Docker | Multi-stage (4 stages) | `apps/web/Dockerfile`, `apps/admin/Dockerfile` |
| K8s | Helm Charts with helpers | `helm/charts/web/`, `helm/sahool/` |
| Health Probes | liveness + readiness | `helm/charts/web/values.yaml` |
| Security | runAsNonRoot, readOnlyRootFilesystem, drop ALL | `helm/sahool/templates/_helpers.tpl` |
| Secrets | External Secrets Operator (Vault) | `gitops/secrets/` |
| Autoscaling | HPA v2 + VPA + PDB | `helm/charts/web/templates/` |
| Deployment | Argo Rollouts (Canary/Blue-Green) | `helm/sahool/templates/rollout.yaml` |
| Routing | Static file-based (Next.js) | `apps/web/src/app/api/` |

---

## Comparison

### 1. Vite SPA vs Next.js 15 Standalone

| Feature | Vite SPA | Next.js 15 (Current) |
|---------|----------|---------------------|
| SSR/SSG | No | Yes (Server Components, ISR) |
| Built-in API Routes | No (needs sidecar) | Yes (Route Handlers) |
| Edge Middleware | No | Yes (auth, CSP, rate limiting) |
| Image Optimization | No | Built-in |
| Security Headers | Requires nginx config | Built into middleware.ts |
| SEO | Weak (CSR only) | Excellent (SSR) |
| Monorepo Support | Limited | Built-in (transpilePackages) |

**Verdict**: Current setup is superior.

### 2. Nginx vs Kong API Gateway

| Feature | Nginx | Kong 3.x (Current) |
|---------|-------|---------------------|
| JWT Authentication | Requires module | Built-in |
| Rate Limiting | Basic | Advanced (per-consumer, per-route) |
| ACL | No | Built-in |
| Bot Detection | No | Built-in |
| Prometheus Metrics | Requires module | Built-in |
| Plugin System | Limited | 100+ plugins |

**Verdict**: Current setup is significantly superior.

### 3. Node Sidecar (Dynamic RPC) vs Next.js Route Handlers

| Feature | Node Sidecar + Dynamic Discovery | Next.js Route Handlers (Current) |
|---------|----------------------------------|-------------------------------|
| Type Safety | Weak (runtime) | Excellent (compile-time) |
| Security | Path traversal risk | Safe (file-based) |
| Debugging | Difficult | Easy (static imports) |
| Performance | Dynamic require overhead | Build-optimized |
| Complexity | High | Low |

**Verdict**: Current setup is simpler and safer.

### 4. Raw K8s Manifests vs Helm Charts

| Feature | Raw YAML | Helm Charts (Current) |
|---------|----------|----------------------|
| Template Reuse | No | Yes (_helpers.tpl) |
| Values Override | No | Yes (per environment) |
| Package Tiers | Manual | Built-in (starter/professional/enterprise) |
| Rollback | kubectl only | helm rollback + Argo Rollouts |

**Verdict**: Current setup is significantly superior.

### 5. Secret Templates vs External Secrets Operator

| Feature | Plain Secret YAML | ESO (Current) |
|---------|-------------------|---------------|
| Auto Rotation | No | Yes (1h refresh) |
| Vault Integration | No | Built-in |
| Audit Trail | No | Yes |
| Git Safety | Risk (secrets in repo) | Safe (references only) |

**Verdict**: Current setup is more secure.

---

## Decision

**Rejected** - The proposed architecture would be a regression from the current stack.

| Component | Decision |
|-----------|----------|
| Vite SPA | Not needed - Next.js is more capable |
| Nginx proxy | Not needed - Kong is more capable |
| Node sidecar | Not needed - Next.js Route Handlers are simpler and safer |
| Dynamic RPC | Not needed - adds complexity without benefit |
| Raw K8s manifests | Not needed - Helm Charts are more powerful |
| Secret templates | Not needed - ESO is more secure |
| HTTPRoute (Gateway API) | Consider for future migration (Kong supports it as provider) |

### Actionable Items Identified

1. **Admin Helm Chart**: Admin app (`apps/admin/`) lacks a dedicated Helm chart (Web has `helm/charts/web/`)
2. **Kong Caching**: Consider enabling response caching for static assets at the gateway level
3. **Gateway API**: Plan future migration when Kubernetes Gateway API becomes more widely adopted

---

_This evaluation is for the SAHOOL platform v16.0.0 architecture review._
