---
description: Scaffold a new SAHOOL microservice from IDP templates
argument-hint: <service-name> [python|node] [port]
---

Scaffold a new microservice under `apps/services/$1` using the templates in `idp/templates/`.

## Arguments
- `$1` — service name (kebab-case, e.g. `pest-alert-service`)
- `$2` — stack: `python` (FastAPI) or `node` (NestJS). Default: `python`.
- `$3` — port number. Must NOT collide with `packages/shared-types/src/contracts/service-ports.ts`.

## Pre-flight checks

Before creating any file, verify:

1. `apps/services/$1/` does NOT already exist.
2. The requested port is unused:
   - Read `packages/shared-types/src/contracts/service-ports.ts`
   - Confirm `$3` is not in `SERVICE_PORTS`
3. The service name is NOT in `archive/deprecated-services/` (so we don't revive a sunset service).
4. `governance/services.yaml` does NOT already list this service.

## Scaffolding steps

### Python (FastAPI)
1. Copy `idp/templates/python-fastapi/skeleton/` → `apps/services/$1/`
2. Replace template placeholders (`{{SERVICE_NAME}}`, `{{PORT}}`, `{{DESCRIPTION}}`) with real values.
3. Create `apps/services/$1/src/main.py` following the lifespan pattern from `CLAUDE.md` → "Main.py Pattern":
   - `lifespan` context manager for DB/NATS startup/shutdown
   - `shared.errors_py.setup_exception_handlers(app)`
   - `/healthz`, `/readyz`, `/metrics` endpoints
   - Version string `"16.0.0"`
4. Use Dockerfile **Pattern A** (3-tier mirror fallback) from `CLAUDE.md` → "Pip Mirror Configuration".
5. Include `-c constraints.txt` in the pip install command.
6. Run as non-root user `sahool` (UID 1000).
7. Add `HEALTHCHECK` directive.

### Node.js (NestJS)
1. Copy `idp/templates/node-service/` → `apps/services/$1/`
2. Prisma schema in `prisma/schema.prisma`.
3. Use the NPM mirror pattern: `npm config set registry https://registry.npmmirror.com`.
4. Non-root, HEALTHCHECK, multi-stage build.

## Post-scaffold registration

1. **Service registry** — append to `governance/services.yaml` under the correct category (acquisition / intelligence / decision / business).
2. **Contracts** — add to `packages/shared-types/src/contracts/service-ports.ts`:
   ```typescript
   export const SERVICE_PORTS = {
     // ...
     NEW_SERVICE_NAME: $3,  // $1
   }
   ```
3. **Contract version** — bump `CONTRACT_VERSION` (patch) in `packages/shared-types/src/contracts/index.ts`.
4. **Dart sync** — run `npx tsx scripts/sync-contracts-to-dart.ts`.
5. **Kong routing** — if the service needs gateway exposure, add a route to `infrastructure/gateway/kong/`.
6. **Docker Compose** — add the service to the appropriate `docker-compose*.yml`.
7. **Helm chart** — if targeting K8s, scaffold a chart under `helm/`.

## Output

Report to the user:
- Absolute paths of the files created
- The port chosen and confirmation it's free
- The exact `docker compose up $1` command to test it locally
- A checklist of any manual follow-ups (tests, docs, helm)
