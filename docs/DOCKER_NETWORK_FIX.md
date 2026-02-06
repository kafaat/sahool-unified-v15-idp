# Docker Network Configuration Fix

## Problem

When running `docker compose up -d <service-name>` for individual services, users encountered the following warning:

```
time="2026-02-04T23:04:05+03:00" level=warning msg="a network with name sahool-network exists but was not created for project \"sahool\".\nSet `external: true` to use an existing network"
```

Additionally, dependent services like `terrain-core-service` would fail to start when starting services like `leveling-optimizer-service`.

## Root Cause

The `sahool-network` was defined in multiple docker-compose files with a custom `name:` property but **without** `external: true`. This caused Docker Compose to be unsure whether the network was:

1. Created by the current project
2. An external network that should be reused

When running services individually or across multiple compose files, this ambiguity led to warnings and potential failures.

## Solution

The network configuration was updated across all docker-compose files to mark `sahool-network` as external:

### Before
```yaml
networks:
  sahool-network:
    driver: bridge
    name: sahool-network
```

### After
```yaml
networks:
  sahool-network:
    external: true
    name: sahool-network
```

## Files Updated

1. `docker-compose.yml` - Main compose file
2. `docker/docker-compose.infra.yml` - Infrastructure services
3. `docker-compose.telemetry.yml` - Telemetry and monitoring
4. `Makefile` - Updated targets to create network before starting services

## Makefile Updates

All development targets now include `network-create` as a prerequisite:

- `make dev` → Creates network, then starts full environment
- `make up` → Creates network, then starts all services
- `make infra-up` → Creates network, then starts infrastructure
- `make dev-terrain` → Creates network, then starts terrain services
- `make dev-vision` → Creates network, then starts vision service
- `make dev-edge` → Creates network, then starts edge orchestrator

The `network-create` target uses `docker network create sahool-network 2>/dev/null || true` to ensure the network exists without failing if it's already created.

## Usage

### Starting Services

Simply use the Makefile targets as before:

```bash
# Full development environment
make dev

# Infrastructure only
make infra-up

# Terrain services (includes terrain-core, hydrology, leveling-optimizer)
make dev-terrain

# Vision service
make dev-vision

# Edge orchestrator
make dev-edge
```

### Manual Network Creation

If you need to manually create the network:

```bash
make network-create
```

Or directly with Docker:

```bash
docker network create sahool-network
```

### Verifying Network

```bash
# List networks
docker network ls | grep sahool

# Inspect network details
make network-inspect
```

## Benefits

1. **No More Warnings**: The ambiguity is resolved - the network is explicitly external
2. **Better Isolation**: Services can be started independently without network conflicts
3. **Multi-Compose Support**: Multiple docker-compose files can share the same network
4. **Consistent Behavior**: Whether starting the full stack or individual services, network behavior is consistent

## Technical Details

### Why External Networks?

The SAHOOL platform uses multiple docker-compose files:
- `docker-compose.yml` - Main platform services
- `docker/docker-compose.infra.yml` - Infrastructure (postgres, redis, nats)
- `docker-compose.telemetry.yml` - Monitoring stack (prometheus, grafana, jaeger)
- `docker/docker-compose.iot.yml` - IoT gateway services

When services from different compose files need to communicate, they must share a network. By marking the network as external:

1. Docker Compose knows not to recreate it
2. All compose files reference the same network
3. Services can communicate regardless of which compose file started them

### Network Properties

- **Name**: `sahool-network`
- **Driver**: `bridge` (default)
- **External**: `true`
- **Scope**: `local`

## Troubleshooting

### Network Already Exists Error

If you see an error that the network already exists when running `docker network create`:

```bash
# Remove the existing network (ensure no containers are using it)
docker network rm sahool-network

# Recreate it
make network-create
```

### Services Can't Communicate

If services can't communicate across the network:

```bash
# Verify network exists
docker network ls | grep sahool

# Inspect network to see connected containers
docker network inspect sahool-network

# Ensure services are on the same network
docker compose config | grep -A 2 "networks:"
```

### Warning Still Appears

If you still see the warning after the fix:

1. Verify you're using the updated docker-compose files
2. Check that the network is marked as `external: true`
3. Remove old containers and recreate them

```bash
make down
make up
```

## References

- [Docker Compose Networks Documentation](https://docs.docker.com/compose/networking/)
- [External Networks in Compose](https://docs.docker.com/compose/compose-file/06-networks/#external)
- Related Files:
  - `docker-compose.yml`
  - `docker/docker-compose.infra.yml`
  - `docker-compose.telemetry.yml`
  - `Makefile`
