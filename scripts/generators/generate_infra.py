#!/usr/bin/env python3
"""
SAHOOL Infrastructure Generator
================================
Generates Docker Compose and Helm configurations from governance/services.yaml

This script ensures that:
- services.yaml is the Single Source of Truth
- Docker Compose and Helm are always in sync with the registry
- No manual editing of infrastructure files is needed

Usage:
    python scripts/generators/generate_infra.py [--compose] [--helm] [--all]

    Options:
        --compose   Generate docker-compose.generated.yml
        --helm      Generate helm/sahool/values.generated.yaml
        --all       Generate all (default)
        --dry-run   Print output without writing files
"""

import yaml
import argparse
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
SERVICES_YAML = ROOT_DIR / "governance" / "services.yaml"
COMPOSE_OUTPUT = ROOT_DIR / "docker" / "compose.generated.yml"
HELM_OUTPUT = ROOT_DIR / "helm" / "sahool" / "values.generated.yaml"


def load_services_yaml() -> Dict[str, Any]:
    """Load and parse services.yaml"""
    if not SERVICES_YAML.exists():
        print(f"ERROR: {SERVICES_YAML} not found")
        sys.exit(1)

    with open(SERVICES_YAML, "r") as f:
        return yaml.safe_load(f)


def generate_compose_service(name: str, service: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a Docker Compose service definition"""
    path = service.get("path", f"apps/services/{name}")
    port = service.get("port", 3000)
    health_endpoint = service.get("health_endpoint", "/health")

    compose_service = {
        "build": {
            "context": f"./{path}",
            "dockerfile": "Dockerfile"
        },
        "container_name": f"sahool-{name}",
        "ports": [f"{port}:{port}"],
        "environment": [
            "NODE_ENV=${NODE_ENV:-development}",
            f"PORT={port}",
            "DATABASE_URL=${DATABASE_URL}",
            "REDIS_URL=${REDIS_URL}",
            "NATS_URL=${NATS_URL:-nats://nats:4222}"
        ],
        "healthcheck": {
            "test": ["CMD", "curl", "-f", f"http://localhost:{port}{health_endpoint}"],
            "interval": "30s",
            "timeout": "10s",
            "retries": 3,
            "start_period": "40s"
        },
        "depends_on": {
            "postgres": {"condition": "service_healthy"},
            "redis": {"condition": "service_healthy"},
            "nats": {"condition": "service_healthy"}
        },
        "networks": ["sahool-network"],
        "restart": "unless-stopped"
    }

    # Add database-specific config
    if "database" in service:
        db = service["database"]
        db_name = db.get("name", f"sahool_{name.replace('-', '_')}")
        compose_service["environment"].append(f"DB_NAME={db_name}")

    # Add MQTT for IoT services
    if "message_broker" in service:
        broker = service["message_broker"]
        if broker.get("type") == "mqtt":
            compose_service["environment"].append("MQTT_URL=${MQTT_URL:-mqtt://mqtt:1883}")
            compose_service["depends_on"]["mqtt"] = {"condition": "service_started"}

    # Add labels for service discovery
    compose_service["labels"] = [
        f"sahool.service={name}",
        f"sahool.port={port}",
        f"sahool.category={service.get('category', 'core')}",
        "traefik.enable=true",
        f"traefik.http.routers.{name}.rule=PathPrefix(`/api/v1/{name.replace('-', '/')}`)"
    ]

    return compose_service


def generate_docker_compose(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate complete Docker Compose configuration"""
    services = data.get("services", {})
    applications = data.get("applications", {})

    compose = {
        "# AUTO-GENERATED FILE - DO NOT EDIT MANUALLY": None,
        "# Generated from governance/services.yaml": None,
        "# Run: make generate-infra": None,
        "version": "3.9",
        "services": {},
        "networks": {
            "sahool-network": {
                "driver": "bridge"
            }
        },
        "volumes": {}
    }

    # Generate backend services
    for name, service in services.items():
        compose["services"][name] = generate_compose_service(name, service)

    # Generate frontend applications
    for name, app in applications.items():
        path = app.get("path", f"apps/{name}")
        port = app.get("port", 3000)

        compose["services"][name] = {
            "build": {
                "context": f"./{path}",
                "dockerfile": "Dockerfile"
            },
            "container_name": f"sahool-{name}",
            "ports": [f"{port}:{port}"],
            "environment": [
                "NODE_ENV=${NODE_ENV:-development}",
                "NEXT_PUBLIC_API_URL=${API_URL:-http://localhost:8000}"
            ],
            "networks": ["sahool-network"],
            "restart": "unless-stopped"
        }

    return compose


def generate_helm_service(name: str, service: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Helm values for a service"""
    resources = service.get("resources", {})

    return {
        "enabled": service.get("status") == "active",
        "name": name,
        "image": {
            "repository": f"ghcr.io/kafaat/sahool-{name}",
            "tag": "latest",
            "pullPolicy": "IfNotPresent"
        },
        "replicaCount": resources.get("replicas", 1),
        "port": service.get("port", 3000),
        "healthCheck": {
            "path": service.get("health_endpoint", "/health"),
            "initialDelaySeconds": 30,
            "periodSeconds": 10
        },
        "resources": {
            "requests": {
                "cpu": resources.get("cpu", "100m"),
                "memory": resources.get("memory", "128Mi")
            },
            "limits": {
                "cpu": resources.get("cpu", "500m").replace("m", "000m") if "m" in str(resources.get("cpu", "500m")) else "1000m",
                "memory": resources.get("memory", "512Mi")
            }
        },
        "env": [
            {"name": "NODE_ENV", "value": "production"},
            {"name": "PORT", "value": str(service.get("port", 3000))}
        ],
        "serviceAccount": {
            "create": True,
            "name": f"sahool-{name}"
        },
        "podAnnotations": {
            "prometheus.io/scrape": "true",
            "prometheus.io/port": str(service.get("port", 3000)),
            "prometheus.io/path": "/metrics"
        }
    }


def generate_helm_values(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate Helm values.yaml"""
    services = data.get("services", {})
    applications = data.get("applications", {})
    infrastructure = data.get("infrastructure", {})

    values = {
        "# AUTO-GENERATED FILE - DO NOT EDIT MANUALLY": None,
        "# Generated from governance/services.yaml": None,
        "# Run: make generate-infra": None,

        "global": {
            "environment": "production",
            "imageRegistry": "ghcr.io/kafaat",
            "imagePullSecrets": ["ghcr-secret"],
            "storageClass": "standard"
        },

        "services": {},
        "applications": {},

        "infrastructure": {
            "postgresql": {
                "enabled": True,
                "auth": {
                    "postgresPassword": "",  # Set via secrets
                    "database": "sahool"
                },
                "primary": {
                    "persistence": {
                        "size": "20Gi"
                    }
                }
            },
            "redis": {
                "enabled": True,
                "auth": {
                    "password": ""  # Set via secrets
                },
                "master": {
                    "persistence": {
                        "size": "5Gi"
                    }
                }
            },
            "nats": {
                "enabled": True,
                "jetstream": {
                    "enabled": True,
                    "memStorage": {
                        "size": "1Gi"
                    },
                    "fileStorage": {
                        "size": "10Gi"
                    }
                }
            }
        },

        "ingress": {
            "enabled": True,
            "className": "nginx",
            "annotations": {
                "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                "nginx.ingress.kubernetes.io/proxy-body-size": "50m"
            },
            "hosts": [
                {
                    "host": "api.sahool.app",
                    "paths": []
                }
            ],
            "tls": [
                {
                    "secretName": "sahool-tls",
                    "hosts": ["api.sahool.app"]
                }
            ]
        },

        "autoscaling": {
            "enabled": True,
            "minReplicas": 2,
            "maxReplicas": 10,
            "targetCPUUtilizationPercentage": 70,
            "targetMemoryUtilizationPercentage": 80
        },

        "monitoring": {
            "prometheus": {
                "enabled": True,
                "serviceMonitor": {
                    "enabled": True,
                    "interval": "30s"
                }
            },
            "grafana": {
                "enabled": True,
                "dashboards": {
                    "enabled": True
                }
            }
        }
    }

    # Generate service values
    for name, service in services.items():
        values["services"][name] = generate_helm_service(name, service)

        # Add ingress paths
        values["ingress"]["hosts"][0]["paths"].append({
            "path": f"/api/v1/{name.replace('-', '/')}",
            "pathType": "Prefix",
            "service": name,
            "port": service.get("port", 3000)
        })

    # Generate application values
    for name, app in applications.items():
        values["applications"][name] = {
            "enabled": app.get("status") == "active",
            "name": name,
            "image": {
                "repository": f"ghcr.io/kafaat/sahool-{name}",
                "tag": "latest"
            },
            "replicaCount": 2,
            "port": app.get("port", 3000)
        }

    return values


def clean_yaml_output(data: Dict[str, Any]) -> str:
    """Convert to YAML and clean up comment markers"""
    yaml_str = yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False)

    # Add header (no timestamp to avoid spurious diffs in CI)
    header = """# ═══════════════════════════════════════════════════════════════════════════════
# AUTO-GENERATED FILE - DO NOT EDIT MANUALLY
# Generated from: governance/services.yaml
# Regenerate: make generate-infra
# ═══════════════════════════════════════════════════════════════════════════════

"""

    # Remove the comment markers we used as dict keys
    lines = []
    for line in yaml_str.split("\n"):
        if line.startswith("'# AUTO-GENERATED") or line.startswith("'# Generated") or line.startswith("'# Run:"):
            continue
        if ": null" in line and "#" in line:
            continue
        lines.append(line)

    return header + "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate infrastructure from services.yaml")
    parser.add_argument("--compose", action="store_true", help="Generate Docker Compose only")
    parser.add_argument("--helm", action="store_true", help="Generate Helm values only")
    parser.add_argument("--all", action="store_true", help="Generate all (default)")
    parser.add_argument("--dry-run", action="store_true", help="Print without writing files")
    args = parser.parse_args()

    # Default to all if no specific option
    if not args.compose and not args.helm:
        args.all = True

    print("📦 Loading governance/services.yaml...")
    data = load_services_yaml()

    service_count = len(data.get("services", {}))
    app_count = len(data.get("applications", {}))
    print(f"   Found {service_count} services, {app_count} applications")

    if args.compose or args.all:
        print("\n🐳 Generating Docker Compose...")
        compose = generate_docker_compose(data)
        compose_yaml = clean_yaml_output(compose)

        if args.dry_run:
            print(compose_yaml[:2000] + "\n... [truncated]")
        else:
            COMPOSE_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            with open(COMPOSE_OUTPUT, "w") as f:
                f.write(compose_yaml)
            print(f"   ✅ Written to {COMPOSE_OUTPUT}")

    if args.helm or args.all:
        print("\n⎈ Generating Helm values...")
        helm = generate_helm_values(data)
        helm_yaml = clean_yaml_output(helm)

        if args.dry_run:
            print(helm_yaml[:2000] + "\n... [truncated]")
        else:
            HELM_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            with open(HELM_OUTPUT, "w") as f:
                f.write(helm_yaml)
            print(f"   ✅ Written to {HELM_OUTPUT}")

    print("\n✅ Infrastructure generation complete!")
    print("   Run 'make validate-infra' to verify generated files")


if __name__ == "__main__":
    main()
