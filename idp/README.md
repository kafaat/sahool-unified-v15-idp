# Internal Developer Platform (IDP)

> منصة المطور الداخلية | Internal Developer Platform

The SAHOOL Internal Developer Platform provides self-service infrastructure for creating, managing, and deploying microservices. Built on [Backstage](https://backstage.io/), it offers service scaffolding, catalog management, and API documentation.

## Directory Structure

```
idp/
├── backstage/           # Backstage Developer Portal configuration
│   └── app-config.yaml  # Portal settings (localhost:7007)
├── catalog/             # Service catalog definitions
│   ├── all.yaml         # Master catalog index
│   ├── apis/            # API definitions (OpenAPI specs)
│   └── services/        # Service component definitions
├── sahoolctl/           # CLI tool for rapid service scaffolding
│   └── sahoolctl.py     # Service generator script
└── templates/           # Service scaffolding templates
    ├── python-fastapi/  # Python FastAPI service template
    ├── node-service/    # Node.js NestJS service template
    ├── flutter-mobile/  # Flutter mobile app template
    └── data-pipeline/   # Data pipeline template
```

## Backstage Developer Portal

The portal runs on `localhost:7007` and provides:

- **Service Catalog**: Browse all 71+ microservices with metadata
- **API Documentation**: OpenAPI specs for vision, terrain, hydrology, leveling, edge services
- **Template Marketplace**: Create new services from standardized templates
- **Kubernetes Integration**: Multi-tenant cluster visibility (sahool-dev)

### Configuration

```yaml
# backstage/app-config.yaml
app:
  title: SAHOOL Developer Portal
  baseUrl: http://localhost:7007
organization:
  name: SAHOOL
```

## sahoolctl CLI

Quick service scaffolding tool that generates a complete, runnable service skeleton.

### Usage

```bash
python3 idp/sahoolctl/sahoolctl.py <service-name> \
  --template <python-fastapi|node-service|flutter-mobile|data-pipeline> \
  --port <port-number> \
  --layer <acquisition|intelligence|decision|business>
```

### Example

```bash
python3 idp/sahoolctl/sahoolctl.py ndvi-preprocessor \
  --template python-fastapi \
  --port 8099 \
  --layer decision
```

**Output**: Generates `apps/services/ndvi-preprocessor/` with Dockerfile, requirements.txt, main.py, catalog-info.yaml, and Helm values snippet.

## Service Templates

| Template | Framework | Output |
|----------|-----------|--------|
| `python-fastapi` | FastAPI + asyncpg | Dockerfile, main.py, requirements.txt, health endpoints |
| `node-service` | NestJS + Prisma | package.json, src/index.ts, tsconfig.json |
| `flutter-mobile` | Flutter + Drift | pubspec.yaml, lib/ structure, SQLCipher setup |
| `data-pipeline` | Python batch | requirements.txt, src/main.py, pipeline config |

All templates include:
- Health endpoints (`/healthz`, `/readyz`)
- Backstage `catalog-info.yaml` for auto-discovery
- Docker multi-stage builds
- Feature flags configuration

## Catalog

The catalog (`catalog/all.yaml`) registers services and APIs for portal discovery:

| Type | Count | Examples |
|------|-------|---------|
| API Definitions | 5 | yolo26-vision, terrain-core, hydrology, leveling-optimizer, edge-orchestrator |
| Service Components | 5 | Matching service definitions for each API |

### Adding a New Service

1. Generate scaffold: `sahoolctl.py <name> --template python-fastapi --port <port>`
2. Add catalog entry to `catalog/all.yaml`
3. Create API definition in `catalog/apis/`
4. Register in `governance/services.yaml`

## Related Documentation

- [Service Registry](../governance/services.yaml) — Source of truth for all services
- [API Contracts](../packages/shared-types/src/contracts/) — Unified API contracts
- [Helm Charts](../helm/) — Kubernetes deployment charts
- [GitOps](../gitops/) — ArgoCD application definitions
