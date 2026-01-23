# Prometheus Service Discovery

This directory contains file-based service discovery configurations for dynamic service registration.

## How It Works

Prometheus can automatically discover services by reading JSON or YAML files in this directory.
The files are refreshed every 30 seconds (configurable in prometheus.yml).

## File Format

### JSON Format

```json
[
  {
    "targets": ["service-name:8080"],
    "labels": {
      "service": "service-name",
      "tier": "application",
      "component": "api",
      "language": "python"
    }
  }
]
```

### YAML Format

```yaml
- targets:
    - service-name:8080
  labels:
    service: service-name
    tier: application
    component: api
    language: python
```

## Integration with Kubernetes

In Kubernetes environments, use a sidecar or init container to generate these files from:
- Kubernetes Service annotations
- ConfigMaps
- External service registries

Example Kubernetes annotation:
```yaml
metadata:
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/port: "8080"
    prometheus.io/path: "/metrics"
```

## Integration with Docker Compose

Use a service discovery tool or script that:
1. Monitors Docker container events
2. Updates the JSON/YAML files when containers start/stop
3. Prometheus automatically picks up changes

## Standard Labels

Use consistent labels across all services:

| Label | Description | Example Values |
|-------|-------------|----------------|
| `service` | Service name | `weather-service` |
| `tier` | Architecture tier | `infrastructure`, `business`, `intelligence`, `decision` |
| `component` | Functional component | `database`, `cache`, `api`, `ai-ml` |
| `language` | Programming language | `python`, `nodejs`, `go` |
| `layer` | Event architecture layer | `acquisition`, `intelligence`, `decision`, `business` |
| `status` | Service status | `active`, `deprecated` |
| `replaced_by` | Replacement service (if deprecated) | `new-service-name` |

## Files in This Directory

- `services/*.json` - Auto-discovered services
- `services/*.yml` - Manually configured services

## Troubleshooting

1. Check Prometheus logs for file parsing errors
2. Validate JSON/YAML syntax
3. Ensure file permissions allow Prometheus to read
4. Verify refresh_interval in prometheus.yml
