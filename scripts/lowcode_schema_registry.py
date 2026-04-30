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
NON_FILTERING_QUERY_PARAMS = frozenset({"limit", "offset", "page", "sort", "sortBy", "order", "orderBy"})


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_openapi(path: Path) -> dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _registry_file_path(spec_entry: dict[str, Any], key: str, service: object, findings: list[str]) -> Path | None:
    raw_path = spec_entry.get(key)
    if not isinstance(raw_path, str) or not raw_path.strip():
        findings.append(f"missing non-empty {key} path for {service}")
        return None

    path = (REPO_ROOT / raw_path).resolve()
    try:
        relative_path = path.relative_to(REPO_ROOT.resolve())
    except ValueError:
        findings.append(f"{key} path for {service} escapes repository root: {raw_path}")
        return None

    if not path.is_file():
        findings.append(f"missing regular file for {service}: {relative_path}")
        return None
    return path


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
        entry_findings: list[str] = []
        spec_path = _registry_file_path(spec_entry, "spec", service, entry_findings)
        approved_path = _registry_file_path(spec_entry, "approvedOperations", service, entry_findings)
        templates_path = _registry_file_path(spec_entry, "templates", service, entry_findings)

        if entry_findings:
            findings.extend(entry_findings)
            continue

        spec = _load_openapi(spec_path)
        approved = _load_json(approved_path)
        templates = _load_json(templates_path).get("templates", {})

        for approved_operation in approved.get("operations", []):
            operation_id = approved_operation.get("operationId")
            method = str(approved_operation.get("method", "")).upper()
            path = approved_operation.get("path")
            template = approved_operation.get("template")
            permission = approved_operation.get("permission")
            key = (str(service), str(operation_id))

            if key in seen:
                findings.append(f"duplicate approved operation: {service}/{operation_id}")
            seen.add(key)

            if template not in templates:
                findings.append(f"unknown template for {service}/{operation_id}: {template}")
            if not isinstance(permission, str) or not permission.strip():
                findings.append(f"approved operation must declare permission: {service}/{operation_id}")
            if not _operation_exists(spec, str(operation_id), method, str(path)):
                findings.append(f"approved operation not found in OpenAPI: {service}/{operation_id}")
                continue

            operation = _operation(spec, method, str(path))
            query_params = _query_parameter_names(operation)
            if approved_operation.get("requiresPagination") and not {"limit", "offset"}.issubset(query_params):
                findings.append(f"approved operation lacks limit/offset pagination: {service}/{operation_id}")
            if approved_operation.get("requiresFiltering") and query_params <= NON_FILTERING_QUERY_PARAMS:
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
