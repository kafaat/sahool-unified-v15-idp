#!/usr/bin/env python3
"""
otel-propagation-audit.py – Audit OpenTelemetry trace propagation across all SAHOOL services.

Scans each service directory for OTEL instrumentation patterns and reports:
  ✅  Properly instrumented services
  ⚠   Partially instrumented (missing propagator or exporter)
  ❌  Not instrumented

Usage:
  python scripts/otel-propagation-audit.py                # full audit to stdout
  python scripts/otel-propagation-audit.py --markdown     # generate markdown report
  python scripts/otel-propagation-audit.py --json         # JSON output for CI

Checks:
  Python services:
    - opentelemetry-api / opentelemetry-sdk in requirements.txt
    - FastAPIInstrumentor or trace imports in source code
    - OTEL_SERVICE_NAME or TracerProvider configuration
    - W3C TraceContext propagation headers

  Node.js services:
    - @opentelemetry/api in package.json
    - Instrumentation setup in source code
    - Trace context propagation

Exit code: 0 if all tier-1 services pass, 1 otherwise.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
SERVICES_DIR = ROOT / "apps" / "services"
SERVICES_YAML = ROOT / "governance" / "services.yaml"

# Patterns to detect OTEL instrumentation
PYTHON_OTEL_PATTERNS = [
    re.compile(r"opentelemetry", re.IGNORECASE),
    re.compile(r"TracerProvider|trace\.get_tracer", re.IGNORECASE),
    re.compile(r"FastAPIInstrumentor|instrument_app", re.IGNORECASE),
    re.compile(r"OTEL_SERVICE_NAME|otel.*exporter", re.IGNORECASE),
]

NODE_OTEL_PATTERNS = [
    re.compile(r"@opentelemetry", re.IGNORECASE),
    re.compile(r"NodeTracerProvider|trace\.getTracer", re.IGNORECASE),
    re.compile(r"registerInstrumentations|HttpInstrumentation", re.IGNORECASE),
]

PROPAGATION_PATTERNS = [
    re.compile(r"W3CTraceContextPropagator|traceparent|TraceContext", re.IGNORECASE),
    re.compile(r"propagat(e|or|ion)", re.IGNORECASE),
]


@dataclass
class ServiceAudit:
    name: str
    service_type: str = "unknown"  # python / nestjs
    tier: str = "tier-3"
    layer: str = "unknown"
    has_otel_dependency: bool = False
    has_tracer_setup: bool = False
    has_instrumentation: bool = False
    has_propagation: bool = False
    has_service_name: bool = False
    issues: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        checks = [
            self.has_otel_dependency,
            self.has_tracer_setup,
            self.has_instrumentation,
        ]
        if all(checks) and self.has_propagation:
            return "✅ PASS"
        if any(checks):
            return "⚠ PARTIAL"
        return "❌ MISSING"

    @property
    def score(self) -> int:
        return sum([
            self.has_otel_dependency,
            self.has_tracer_setup,
            self.has_instrumentation,
            self.has_propagation,
            self.has_service_name,
        ])


def load_service_metadata() -> dict[str, dict]:
    """Load service metadata from governance/services.yaml."""
    if not SERVICES_YAML.exists():
        return {}
    with open(SERVICES_YAML) as f:
        data = yaml.safe_load(f)

    metadata: dict[str, dict] = {}
    # Extract from event_architecture layers
    layers = data.get("event_architecture", {}).get("layers", {})
    for layer_name, layer_def in layers.items():
        for svc_name in layer_def.get("services", []):
            metadata.setdefault(svc_name, {})["layer"] = layer_name

    # Extract from services definitions (if present at top level)
    for key, val in data.items():
        if isinstance(val, dict) and "port" in val:
            metadata.setdefault(key, {}).update({
                "type": val.get("type", "unknown"),
                "tier": val.get("tier", "tier-3"),
                "layer": val.get("layer", metadata.get(key, {}).get("layer", "unknown")),
            })

    return metadata


def scan_file_for_patterns(filepath: Path, patterns: list[re.Pattern]) -> list[bool]:
    """Return list of booleans indicating which patterns matched."""
    try:
        content = filepath.read_text(errors="ignore")
    except (OSError, UnicodeDecodeError):
        return [False] * len(patterns)
    return [bool(p.search(content)) for p in patterns]


def audit_python_service(svc_dir: Path) -> ServiceAudit:
    """Audit a Python (FastAPI) service for OTEL instrumentation."""
    audit = ServiceAudit(name=svc_dir.name, service_type="python")

    # Check requirements.txt
    req_file = svc_dir / "requirements.txt"
    if req_file.exists():
        content = req_file.read_text(errors="ignore").lower()
        audit.has_otel_dependency = "opentelemetry" in content
        if not audit.has_otel_dependency:
            audit.issues.append("opentelemetry packages not in requirements.txt")

    # Scan Python source files
    src_files = list(svc_dir.rglob("*.py"))
    for src_file in src_files:
        results = scan_file_for_patterns(src_file, PYTHON_OTEL_PATTERNS)
        if results[0]:
            audit.has_otel_dependency = True
        if results[1]:
            audit.has_tracer_setup = True
        if results[2]:
            audit.has_instrumentation = True
        if results[3]:
            audit.has_service_name = True

        prop_results = scan_file_for_patterns(src_file, PROPAGATION_PATTERNS)
        if any(prop_results):
            audit.has_propagation = True

    if not audit.has_tracer_setup:
        audit.issues.append("No TracerProvider setup found")
    if not audit.has_instrumentation:
        audit.issues.append("No FastAPIInstrumentor or instrument_app found")
    if not audit.has_propagation:
        audit.issues.append("No W3C TraceContext propagation configured")

    return audit


def audit_node_service(svc_dir: Path) -> ServiceAudit:
    """Audit a Node.js (NestJS) service for OTEL instrumentation."""
    audit = ServiceAudit(name=svc_dir.name, service_type="nestjs")

    # Check package.json
    pkg_file = svc_dir / "package.json"
    if pkg_file.exists():
        content = pkg_file.read_text(errors="ignore")
        audit.has_otel_dependency = "@opentelemetry" in content
        if not audit.has_otel_dependency:
            audit.issues.append("@opentelemetry packages not in package.json")

    # Scan source files
    src_files = list(svc_dir.rglob("*.ts")) + list(svc_dir.rglob("*.js"))
    for src_file in src_files:
        if "node_modules" in str(src_file):
            continue
        results = scan_file_for_patterns(src_file, NODE_OTEL_PATTERNS)
        if results[0]:
            audit.has_otel_dependency = True
        if results[1]:
            audit.has_tracer_setup = True
        if results[2]:
            audit.has_instrumentation = True

        prop_results = scan_file_for_patterns(src_file, PROPAGATION_PATTERNS)
        if any(prop_results):
            audit.has_propagation = True

    # Check for OTEL_SERVICE_NAME in Dockerfile or env
    for config_file in [svc_dir / "Dockerfile", svc_dir / ".env.example"]:
        if config_file.exists():
            content = config_file.read_text(errors="ignore")
            if "OTEL_SERVICE_NAME" in content:
                audit.has_service_name = True

    if not audit.has_tracer_setup:
        audit.issues.append("No TracerProvider setup found")
    if not audit.has_propagation:
        audit.issues.append("No trace context propagation configured")

    return audit


def detect_service_type(svc_dir: Path) -> str:
    """Detect if a service is Python or Node.js."""
    if (svc_dir / "requirements.txt").exists():
        return "python"
    if (svc_dir / "package.json").exists():
        return "nestjs"
    if list(svc_dir.rglob("*.py")):
        return "python"
    if list(svc_dir.rglob("*.ts")):
        return "nestjs"
    return "unknown"


def run_audit() -> list[ServiceAudit]:
    """Run OTEL audit across all services."""
    metadata = load_service_metadata()
    audits: list[ServiceAudit] = []

    if not SERVICES_DIR.exists():
        return audits

    for svc_dir in sorted(SERVICES_DIR.iterdir()):
        if not svc_dir.is_dir():
            continue
        if svc_dir.name.startswith("."):
            continue

        svc_type = detect_service_type(svc_dir)
        if svc_type == "python":
            audit = audit_python_service(svc_dir)
        elif svc_type == "nestjs":
            audit = audit_node_service(svc_dir)
        else:
            audit = ServiceAudit(name=svc_dir.name, service_type="unknown")
            audit.issues.append("Could not detect service type")

        # Enrich with governance metadata
        meta = metadata.get(svc_dir.name, {})
        audit.tier = meta.get("tier", "tier-3")
        audit.layer = meta.get("layer", "unknown")

        audits.append(audit)

    return audits


def print_markdown(audits: list[ServiceAudit]) -> None:
    """Print audit results as markdown."""
    total = len(audits)
    passing = sum(1 for a in audits if a.status == "✅ PASS")
    partial = sum(1 for a in audits if a.status == "⚠ PARTIAL")
    missing = sum(1 for a in audits if a.status == "❌ MISSING")

    print("# SAHOOL OTEL Propagation Audit Report")
    print()
    print(f"**Date:** Auto-generated")
    print(f"**Services scanned:** {total}")
    print(f"**Fully instrumented:** {passing} ({passing * 100 // max(total, 1)}%)")
    print(f"**Partially instrumented:** {partial}")
    print(f"**Not instrumented:** {missing}")
    print()
    print("## Summary by Layer")
    print()
    print("| Layer | Total | ✅ Pass | ⚠ Partial | ❌ Missing |")
    print("|-------|-------|---------|-----------|------------|")
    for layer in ["acquisition", "intelligence", "decision", "business", "unknown"]:
        layer_audits = [a for a in audits if a.layer == layer]
        if not layer_audits:
            continue
        lp = sum(1 for a in layer_audits if a.status == "✅ PASS")
        lw = sum(1 for a in layer_audits if a.status == "⚠ PARTIAL")
        lm = sum(1 for a in layer_audits if a.status == "❌ MISSING")
        print(f"| {layer.title()} | {len(layer_audits)} | {lp} | {lw} | {lm} |")

    print()
    print("## Detailed Results")
    print()
    print("| Service | Type | Layer | Tier | Status | Score | Issues |")
    print("|---------|------|-------|------|--------|-------|--------|")
    status_priority = {"✅ PASS": 3, "⚠ PARTIAL": 2, "❌ MISSING": 1}
    for a in sorted(audits, key=lambda x: (-status_priority.get(x.status, 0), x.name)):
        issues_str = "; ".join(a.issues[:2]) if a.issues else "—"
        print(f"| {a.name} | {a.service_type} | {a.layer} | {a.tier} | {a.status} | {a.score}/5 | {issues_str} |")

    print()
    print("## Recommendations")
    print()
    print("1. **Tier-1 services** must have full OTEL instrumentation (score 5/5)")
    print("2. Add `opentelemetry-api`, `opentelemetry-sdk` to Python `requirements.txt`")
    print("3. Add `@opentelemetry/api`, `@opentelemetry/sdk-node` to Node.js `package.json`")
    print("4. Configure `W3CTraceContextPropagator` for cross-service trace propagation")
    print("5. Set `OTEL_SERVICE_NAME` in Dockerfile or environment configuration")
    print("6. Use `shared/observability/` module for standardized instrumentation")


def print_json(audits: list[ServiceAudit]) -> None:
    """Print audit results as JSON."""
    results = []
    for a in audits:
        results.append({
            "name": a.name,
            "type": a.service_type,
            "layer": a.layer,
            "tier": a.tier,
            "status": a.status,
            "score": a.score,
            "checks": {
                "otel_dependency": a.has_otel_dependency,
                "tracer_setup": a.has_tracer_setup,
                "instrumentation": a.has_instrumentation,
                "propagation": a.has_propagation,
                "service_name": a.has_service_name,
            },
            "issues": a.issues,
        })
    print(json.dumps({"audits": results, "total": len(results)}, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(description="OTEL propagation audit for SAHOOL services")
    parser.add_argument("--markdown", action="store_true", help="Output as markdown")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    audits = run_audit()

    if args.json:
        print_json(audits)
    elif args.markdown:
        print_markdown(audits)
    else:
        # Default: summary table
        print_markdown(audits)

    # CI gate: fail if any tier-1 service is not fully instrumented
    tier1_failures = [a for a in audits if a.tier == "tier-1" and a.status != "✅ PASS"]
    if tier1_failures:
        print(f"\n❌ {len(tier1_failures)} tier-1 service(s) failing OTEL audit", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
