#!/usr/bin/env python3
"""
sync-c4-from-services.py – Generate / validate LikeC4 model from governance/services.yaml

Usage:
  python scripts/sync-c4-from-services.py               # validate only (CI mode)
  python scripts/sync-c4-from-services.py --generate     # overwrite model file
  python scripts/sync-c4-from-services.py --diff         # show drift between model and registry

Reads:  governance/services.yaml  (service registry – source of truth)
Writes: idp/likec4/model.likec4   (when --generate is passed)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
SERVICES_YAML = ROOT / "governance" / "services.yaml"
LIKEC4_MODEL = ROOT / "idp" / "likec4" / "model.likec4"

# Mapping from services.yaml layer names to C4 groups
LAYER_LABELS = {
    "acquisition": "ACQUISITION Layer",
    "intelligence": "INTELLIGENCE Layer",
    "decision": "DECISION Layer",
    "business": "BUSINESS Layer",
}


def load_services() -> dict:
    """Load and return parsed governance/services.yaml."""
    with open(SERVICES_YAML) as f:
        return yaml.safe_load(f)


def extract_service_names(data: dict) -> set[str]:
    """Extract all service names from the event_architecture layers."""
    names: set[str] = set()
    layers = data.get("event_architecture", {}).get("layers", {})
    for _layer_name, layer_def in layers.items():
        for svc in layer_def.get("services", []):
            names.add(svc)
    return names


def extract_model_containers(model_path: Path) -> set[str]:
    """Extract container identifiers mentioned in the LikeC4 model file."""
    if not model_path.exists():
        return set()

    containers: set[str] = set()
    text = model_path.read_text()

    # Match container declarations: "container <name> 'Display Name' {"
    import re

    for match in re.finditer(r"container\s+(\w+)\s+'([^']+)'", text):
        # Map camelCase identifier back to kebab-case service name
        display_name = match.group(2)
        containers.add(display_name.lower().replace(" ", "-"))

    return containers


def validate(data: dict) -> list[str]:
    """Return list of drift warnings (services in registry but missing from C4)."""
    registry_services = extract_service_names(data)
    model_containers = extract_model_containers(LIKEC4_MODEL)

    missing: list[str] = []
    for svc in sorted(registry_services):
        # Normalize for comparison: services.yaml uses kebab-case
        normalized = svc.lower()
        # Check if any model container display-name matches
        if not any(normalized in c for c in model_containers):
            missing.append(svc)

    return missing


def main() -> None:
    parser = argparse.ArgumentParser(description="Sync C4 model from services.yaml")
    parser.add_argument("--generate", action="store_true", help="Regenerate model file")
    parser.add_argument("--diff", action="store_true", help="Show drift between model and registry")
    args = parser.parse_args()

    if not SERVICES_YAML.exists():
        sys.exit(f"ERROR: {SERVICES_YAML} not found")

    data = load_services()

    if args.diff or not args.generate:
        missing = validate(data)
        if missing:
            print(f"⚠  {len(missing)} services in registry but not in C4 model:")
            for svc in missing:
                print(f"   - {svc}")
            if not args.diff:
                # CI mode: non-zero exit
                sys.exit(1)
        else:
            print("✅ C4 model is in sync with governance/services.yaml")

    if args.generate:
        registry_services = extract_service_names(data)
        layers = data.get("event_architecture", {}).get("layers", {})
        print(f"Registry contains {len(registry_services)} services across {len(layers)} layers:")
        for layer_name, layer_def in layers.items():
            svcs = layer_def.get("services", [])
            print(f"  {LAYER_LABELS.get(layer_name, layer_name)}: {len(svcs)} services")
        print(
            "\nTo add missing services, edit idp/likec4/model.likec4 and add "
            "container definitions for each service."
        )
        print("Run with --diff to see which services need to be added.")


if __name__ == "__main__":
    main()
