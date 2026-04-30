#!/usr/bin/env python3
"""Validate and query the SAHOOL Low-Code schema registry."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
REGISTRY_PATH = REPO_ROOT / "schema-registry" / "registry.json"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_openapi(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _operation_exists(spec: dict[str, Any], operation_id: str, method: str, path: str) -> bool:
    operation = spec.get("paths", {}).get(path, {}).get(method.lower())
    return isinstance(operation, dict) and operation.get("operationId") == operation_id


def _query_parameter_names(operation: dict[str, Any]) -> set[str]:
    return {
        str(parameter.get("name"))
        for parameter in operation.get("parameters", [])
        if isinstance(parameter, dict) and parameter.get("in") == "query" and parameter.get("name")
    }


def _operation(spec: dict[str, Any], method: str, path: str) -> dict[str, Any]:
    operation = spec.get("paths", {}).get(path, {}).get(method.lower())
    if not isinstance(operation, dict):
        raise ValueError(f"Operation not found: {method} {path}")
    return operation


def validate_registry(registry_path: Path = REGISTRY_PATH) -> list[str]:
    registry = _load_json(registry_path)
    findings: list[str] = []
    seen: set[tuple[str, str]] = set()

    for spec_entry in registry.get("specs", []):
        service = spec_entry.get("service")
        spec_path = REPO_ROOT / spec_entry.get("spec", "")
        approved_path = REPO_ROOT / spec_entry.get("approvedOperations", "")
        templates_path = REPO_ROOT / spec_entry.get("templates", "")

        for path in (spec_path, approved_path, templates_path):
            if not path.exists():
                findings.append(f"missing file for {service}: {path.relative_to(REPO_ROOT)}")

        if findings:
            continue

        spec = _load_openapi(spec_path)
        approved = _load_json(approved_path)
        templates = _load_json(templates_path).get("templates", {})

        for approved_operation in approved.get("operations", []):
            operation_id = approved_operation.get("operationId")
            method = str(approved_operation.get("method", "")).upper()
            path = approved_operation.get("path")
            template = approved_operation.get("template")
            key = (str(service), str(operation_id))

            if key in seen:
                findings.append(f"duplicate approved operation: {service}/{operation_id}")
            seen.add(key)

            if template not in templates:
                findings.append(f"unknown template for {service}/{operation_id}: {template}")
            if not _operation_exists(spec, str(operation_id), method, str(path)):
                findings.append(f"approved operation not found in OpenAPI: {service}/{operation_id}")
                continue

            operation = _operation(spec, method, str(path))
            query_params = _query_parameter_names(operation)
            if approved_operation.get("requiresPagination") and not {"limit", "offset"}.issubset(query_params):
                findings.append(f"approved operation lacks limit/offset pagination: {service}/{operation_id}")
            pagination_sorting_params_only = {"limit", "offset", "page", "sort", "sortBy", "order", "orderBy"}
            if approved_operation.get("requiresFiltering") and query_params <= pagination_sorting_params_only:
                findings.append(f"approved operation lacks query filters: {service}/{operation_id}")
            if template == "list.table" and not ({"sort", "sortBy", "order", "orderBy"} & query_params):
                findings.append(f"DataTable operation lacks sorting parameter: {service}/{operation_id}")
            if not approved_operation.get("requiresTenantContext"):
                findings.append(f"approved operation must require tenant context: {service}/{operation_id}")
            if not approved_operation.get("requiresUnifiedResponse"):
                findings.append(f"approved operation must require unified response handling: {service}/{operation_id}")

    return findings


def approved_operations(registry_path: Path = REGISTRY_PATH) -> list[dict[str, Any]]:
    registry = _load_json(registry_path)
    operations: list[dict[str, Any]] = []
    for spec_entry in registry.get("specs", []):
        approved_path = REPO_ROOT / spec_entry.get("approvedOperations", "")
        if not approved_path.exists():
            continue
        approved = _load_json(approved_path)
        for operation in approved.get("operations", []):
            operations.append({"service": spec_entry.get("service"), **operation})
    return operations


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "list"))
    args = parser.parse_args()

    if args.command == "list":
        print(json.dumps(approved_operations(), indent=2, ensure_ascii=False))
        return 0

    findings = validate_registry()
    if findings:
        print("\n".join(f"LOWCODE-REGISTRY: {finding}" for finding in findings))
        return 1
    print("LOWCODE-REGISTRY: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
