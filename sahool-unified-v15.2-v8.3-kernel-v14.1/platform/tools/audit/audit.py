#!/usr/bin/env python3
"""SAHOOL Governance Audit Tool v15.2 (Governed)

Checks:
- YAML validity (compose + workflows + observability)
- Required governance docs + schemas exist
- Service endpoints include /healthz and /metrics
- Event schemas exist for known subjects
"""

from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[2]

REQUIRED_SCHEMAS = [
    "internal.image.analyzed.v15.2.json",
    "decision.disease.risk_assessed.v15.2.json",
]

def _load_yaml(path: Path):
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        raise SystemExit(f"YAML parse error in {path}: {e}")

def check_exists(rel: str):
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"Missing required file: {rel}")

def check_yaml_valid(rel: str):
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f"Missing YAML: {rel}")
    _load_yaml(p)

def check_service_has_metrics(rel: str):
    p = ROOT / rel
    txt = p.read_text(encoding="utf-8")
    if "/metrics" not in txt:
        raise SystemExit(f"Missing /metrics endpoint in {rel}")
    if "/healthz" not in txt:
        raise SystemExit(f"Missing /healthz endpoint in {rel}")

def check_schemas():
    for s in REQUIRED_SCHEMAS:
        check_exists(f"governance/schemas/{s}")

def main():
    # governance
    check_exists("governance/LAYER_RULES.md")
    check_exists("governance/OBSERVABILITY_RULES.md")
    check_exists("governance/EVENT_CONTRACTS.md")
    check_schemas()

    # yaml
    check_yaml_valid(".github/workflows/system-main.yml")
    check_yaml_valid("kernel/docker/docker-compose.yml")
    check_yaml_valid("docker/observability/docker-compose.yml")
    check_yaml_valid("docker/observability/otel-collector.yml")
    check_yaml_valid("docker/observability/tempo.yml")
    check_yaml_valid("docker/observability/prometheus.yml")

    # services (at least reference ones)
    check_service_has_metrics("kernel/services/image-diagnosis/src/main.py")
    check_service_has_metrics("kernel/services/disease-risk/src/main.py")

    print("✅ SAHOOL audit passed (v15.2 governed)")

if __name__ == "__main__":
    main()
