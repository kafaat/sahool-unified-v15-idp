# SAHOOL Unified Merge Report (v15.2 + v8.3)

**Output package:** sahool-unified-v15.2-v8.3-enterprise

## What was taken from v8.3 (Domain / Services)
All runnable application services and the docker-compose stack were preserved from **sahool-platform-v8.3-enhanced-fixed**:
- platform-core: api-gateway, auth-service
- signal-producers: ndvi-signal, weather-signal, astronomical-calendar-signal
- decision-services: crop-advisor
- execution-services: task-manager, alert-dispatcher
- infrastructure: docker, monitoring, secrets
- mobile/: kept as-is

## What was added from v15.2 (Governance / Security / K8s)
Added under **platform/** and **k8s/**:
- platform/governance/: Layer rules, Event contracts, Observability rules, JSON schemas
- platform/tools/: audit tool + security utilities
- platform/shared_py/: python shared libs (events validator, otel, jwt helpers)
- platform/observability/docker/: otel collector, tempo, prometheus configs
- platform/docs/: hardening notes
- .github/: CODEOWNERS + system workflow
- k8s/: Kubernetes/Helm structure + README

## Conflict handling
- No v8.3 files were overwritten; new v15.2 assets were placed in new folders.
- Python shared libs were placed in **platform/shared_py** to avoid clashing with v8.3 TypeScript shared libs (**shared/**).

## Next recommended steps
1. Align service names between docker-compose and Helm values (for Helm deploy).
2. Standardize event topics vs governance/event-contracts.
3. Wire the audit tool into CI to fail builds on governance violations.


### Added from sahool-kernel-v14.1
- Docs copied to `platform/kernel-v14.1-docs/`
- Astral/seasonal SQL seeds copied to `platform/astral/data/seeds/` and bundled into `infrastructure/postgres/init/10-astral-seeds.sql`
- Kernel services copied to `platform-core/kernel-services/`
- Kernel docker-compose references saved in `docker/`
- Main `docker-compose.yml` updated to use PostGIS image and mount init scripts.

## GitOps (Argo CD)
- Added gitops/ folder with Argo CD App-of-Apps setup.
- Replace `REPLACE_WITH_YOUR_REPO_URL` in Argo CD Applications.
