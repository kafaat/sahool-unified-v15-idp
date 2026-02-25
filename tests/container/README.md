# Container Tests

Tests that validate Docker container definitions, Dockerfile best practices, and docker-compose configuration integrity. These tests parse YAML and Dockerfile files statically — no Docker daemon is required to run them.

## Running

```bash
# All container tests
pytest tests/container/ -v

# Python container function tests
pytest tests/container/test_docker_container_functions.py -v

# Network configuration shell test
bash tests/container/test_network_config.sh

# Via Makefile
make test-docker
```

## Test Files

### `test_docker_container_functions.py`

Validates the `docker-compose.yml` and service Dockerfiles against platform standards:

**Compose Structure**
- Backbone infrastructure containers present (PostgreSQL/PostGIS, PgBouncer, Redis, NATS, Kong, Vault)
- Supporting containers present (Qdrant, Milvus, MinIO, Mosquitto, Ollama, MLflow)
- All Python FastAPI services have `build:` directives pointing to existing Dockerfiles
- All Node.js/NestJS services are defined with correct port mappings

**Dockerfile Best Practices**
- Non-root user `sahool` (UID 1000) declared in all service Dockerfiles
- `HEALTHCHECK` directives present
- Multi-stage builds used where appropriate
- `EXPOSE` directives match service port registry

**Cross-file Consistency**
- Service names consistent between `docker-compose.yml` and `governance/services.yaml`
- Port assignments do not conflict across services

### `test_network_config.sh`

Shell script that validates Docker network isolation:
- Internal network (`sahool-internal`) does not expose ports externally
- External network (`sahool-external`) is limited to Kong and gateway services
- Network driver settings match the expected bridge configuration

## Audit Reports

The `tests/container/` directory also contains generated audit reports from previous container review passes. These are reference documents, not executable tests:

| Report | Contents |
|--------|----------|
| `BASE_IMAGE_REPORT.md` | Base image versions across all 109 Dockerfiles |
| `DOCKERFILE_LINT_REPORT.md` | Hadolint results |
| `NON_ROOT_USER_REPORT.md` | Non-root user compliance per service |
| `HEALTHCHECK_REPORT.md` | HEALTHCHECK presence and configuration |
| `MULTISTAGE_BUILD_REPORT.md` | Multi-stage build usage |
| `SECRETS_SCAN_REPORT.md` | Secrets in Dockerfiles/compose files |
| `RESOURCE_LIMITS_REPORT.md` | CPU/memory limit settings |
| `NETWORK_ISOLATION_REPORT.md` | Network segmentation analysis |

## Related

- Dockerfiles: `apps/services/*/Dockerfile`, `docker/`
- Docker Compose files: `docker-compose.yml`, `docker-compose.*.yml`
- CI workflow: `.github/workflows/docker-buildx.yml`, `container-tests.yml`
