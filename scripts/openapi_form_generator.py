#!/usr/bin/env python3
"""Generate approved SAHOOL Low-Code Flutter UI from OpenAPI operations."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

from lowcode_schema_registry import REGISTRY_PATH, REPO_ROOT, approved_operations, validate_registry


DEFAULT_OUTPUT_DIR = REPO_ROOT / "apps" / "mobile" / "lib" / "features" / "lowcode" / "generated"


def _load_openapi(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _operation_method(spec: dict[str, Any], operation_id: str) -> str:
    for methods in spec.get("paths", {}).values():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if isinstance(operation, dict) and operation.get("operationId") == operation_id:
                return method.upper()
    raise ValueError(f"OpenAPI operationId not found: {operation_id}")


def _approved_operation(operation_id: str) -> dict[str, Any]:
    for operation in approved_operations():
        if operation.get("operationId") == operation_id:
            return operation
    raise ValueError(f"Operation is not approved for Low-Code generation: {operation_id}")


def _registry_spec_for_service(service: str) -> Path:
    import json

    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for entry in registry.get("specs", []):
        if entry.get("service") == service:
            return REPO_ROOT / str(entry["spec"])
    raise ValueError(f"No OpenAPI spec registered for service: {service}")


def _run_generator(script: str, *args: str) -> None:
    script_path = REPO_ROOT.joinpath("scripts", script).resolve()
    try:
        script_path.relative_to(REPO_ROOT.resolve())
    except ValueError:
        raise ValueError(f"Generator path escapes repository root: {script}")
    subprocess.run([sys.executable, str(script_path), *args], check=True, timeout=60)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--openapi", type=Path)
    parser.add_argument("--layout", choices=("card", "table"), default="card")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    findings = validate_registry()
    if findings:
        raise ValueError("Schema registry validation failed: " + "; ".join(findings))

    approved = _approved_operation(args.operation_id)
    permission = str(approved["permission"])
    spec_path = args.openapi or _registry_spec_for_service(str(approved["service"]))
    method = _operation_method(_load_openapi(spec_path), args.operation_id)

    if method == "GET":
        _run_generator(
            "generate_openapi_flutter_view_poc.py",
            "--openapi",
            str(spec_path),
            "--operation-id",
            args.operation_id,
            "--layout",
            args.layout,
            "--output-dir",
            str(args.output_dir),
            "--permission",
            permission,
        )
    elif method in {"POST", "PUT", "PATCH"}:
        _run_generator(
            "generate_openapi_flutter_form_poc.py",
            "--openapi",
            str(spec_path),
            "--operation-id",
            args.operation_id,
            "--output-dir",
            str(args.output_dir),
            "--permission",
            permission,
        )
    else:
        raise ValueError(f"Unsupported Low-Code operation method: {method}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
