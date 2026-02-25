# Service Templates

> قوالب الخدمات | Service Templates

Standardized service scaffolding templates used by the governance system to ensure consistency across all new SAHOOL microservices.

## Available Templates

| Template | Use Case |
|----------|----------|
| [api-extension/](./api-extension/) | Extend existing API services with new endpoints |
| [backend-service/](./backend-service/) | Full backend microservice (API + DB + events) |
| [worker-service/](./worker-service/) | Background worker (event consumer, batch processing) |

## Template Structure

Each template provides:
- Service boilerplate (Dockerfile, requirements/package.json)
- Health endpoints (`/healthz`, `/readyz`)
- NATS event integration
- Database connection patterns
- Backstage catalog entry (`catalog-info.yaml`)
- Helm values snippet

## Usage

Templates are consumed by:
1. **sahoolctl CLI**: `python3 idp/sahoolctl/sahoolctl.py <name> --template <type>`
2. **Backstage Portal**: Self-service creation via IDP UI
3. **Manual**: Copy template and customize

## Template vs IDP Templates

| Location | Purpose |
|----------|---------|
| `governance/templates/` | Governance-level patterns (what a service must include) |
| `idp/templates/` | Scaffolding implementation (actual file generation) |

## Related

- [IDP Templates](../../idp/templates/) — Scaffolding implementations
- [sahoolctl](../../idp/sahoolctl/) — CLI tool
- [Service Registry](../services.yaml) — Service definitions
