#!/usr/bin/env python3
"""
SAHOOL Compose Generator
Generates docker-compose files from services.yaml

Usage:
    python tools/generators/compose-generator.py
"""

from pathlib import Path

import yaml

# Paths
ROOT_DIR = Path(__file__).parent.parent.parent
SERVICES_YAML = ROOT_DIR / "governance" / "services.yaml"
OUTPUT_DIR = ROOT_DIR / "docker" / "compose"


def load_services():
    """Load services from services.yaml"""
    with open(SERVICES_YAML) as f:
        return yaml.safe_load(f)


def generate_service_compose(name: str, config: dict) -> dict:
    """Generate docker-compose service definition"""
    service_type = config.get("type", "python")
    port = config.get("port", 8000)
    path = config.get("path", f"apps/services/{name}")

    service = {
        "build": {
            "context": f"../../{path}",
            "dockerfile": "Dockerfile",
        },
        "ports": [f"{port}:{port}"],
        "environment": [
            f"PORT={port}",
            (
                "NODE_ENV=production"
                if service_type == "nestjs"
                else "ENVIRONMENT=production"
            ),
        ],
        "healthcheck": {
            "test": [
                "CMD",
                "curl",
                "-f",
                f"http://localhost:{port}{config.get('health_endpoint', '/health')}",
            ],
            "interval": "30s",
            "timeout": "10s",
            "retries": 3,
        },
        "restart": "unless-stopped",
    }

    # Add resource limits
    resources = config.get("resources", {})
    if resources:
        service["deploy"] = {
            "resources": {
                "limits": {
                    "cpus": resources.get("cpu", "500m").replace("m", "").zfill(1),
                    "memory": resources.get("memory", "512Mi"),
                }
            }
        }

    # Add dependencies
    deps = config.get("dependencies", [])
    if deps:
        # Filter to only include service dependencies (not packages)
        service_deps = [d for d in deps if not d.startswith("sahool-")]
        if service_deps:
            service["depends_on"] = service_deps

    return service


def generate_compose_by_layer(data: dict) -> dict:
    """Generate compose files grouped by layer"""
    layers = {}

    for name, config in data.get("services", {}).items():
        layer = config.get("layer", "business")
        if layer not in layers:
            layers[layer] = {}
        layers[layer][name] = generate_service_compose(name, config)

    return layers


def write_compose_file(filename: str, services: dict):
    """Write a docker-compose file"""
    compose = {
        "version": "3.8",
        "services": services,
        "networks": {
            "sahool-network": {
                "driver": "bridge",
            }
        },
    }

    output_path = OUTPUT_DIR / filename
    with open(output_path, "w") as f:
        yaml.dump(
            compose, f, default_flow_style=False, allow_unicode=True, sort_keys=False
        )

    print(f"  Generated: {output_path}")


def main():
    print("SAHOOL Compose Generator")
    print("=" * 50)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load services
    data = load_services()
    print(f"Loaded {len(data.get('services', {}))} services from services.yaml")

    # Generate by layer
    layers = generate_compose_by_layer(data)

    # Write layer-specific compose files
    for layer, services in layers.items():
        write_compose_file(f"compose.{layer}.yml", services)

    # Write all-services compose file
    all_services = {}
    for services in layers.values():
        all_services.update(services)
    write_compose_file("compose.all.yml", all_services)

    print("\nDone!")


if __name__ == "__main__":
    main()
