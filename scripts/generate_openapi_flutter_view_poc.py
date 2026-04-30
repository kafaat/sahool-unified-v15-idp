#!/usr/bin/env python3
"""Generate a guarded Flutter Card/DataTable view PoC from one OpenAPI GET operation."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = REPO_ROOT / "apps" / "mobile" / "lib" / "features" / "lowcode" / "generated"


@dataclass(frozen=True)
class ViewField:
    name: str
    label: str


def _load_openapi(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def _resolve_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        raise ValueError(f"Only local OpenAPI refs are supported, got {ref}")
    current: Any = spec
    for part in ref.removeprefix("#/").split("/"):
        current = current[part]
    return current


def _resolve_schema(spec: dict[str, Any], schema: dict[str, Any]) -> dict[str, Any]:
    if "$ref" in schema:
        return _resolve_schema(spec, _resolve_ref(spec, schema["$ref"]))
    if "items" in schema and isinstance(schema["items"], dict):
        schema = dict(schema)
        schema["items"] = _resolve_schema(spec, schema["items"])
    return schema


def _operation_by_id(spec: dict[str, Any], operation_id: str) -> tuple[str, str, dict[str, Any]]:
    for path, methods in spec.get("paths", {}).items():
        if not isinstance(methods, dict):
            continue
        operation = methods.get("get")
        if isinstance(operation, dict) and operation.get("operationId") == operation_id:
            return path, "GET", operation
    raise ValueError(f"GET operationId not found: {operation_id}")


def _response_schema(spec: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    response = operation.get("responses", {}).get("200") or operation.get("responses", {}).get(200) or {}
    content = response.get("content", {})
    media = content.get("application/json") or next(iter(content.values()), {})
    return _resolve_schema(spec, media.get("schema") or {})


def _item_schema(spec: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    schema = _response_schema(spec, operation)
    if schema.get("type") == "array":
        return _resolve_schema(spec, schema.get("items", {}))
    items = schema.get("properties", {}).get("items")
    if isinstance(items, dict):
        resolved_items = _resolve_schema(spec, items)
        if resolved_items.get("type") == "array":
            return _resolve_schema(spec, resolved_items.get("items", {}))
    raise ValueError("Selected GET operation must return an array or paginated object with items[]")


def _query_parameter_names(operation: dict[str, Any]) -> set[str]:
    return {
        str(parameter.get("name"))
        for parameter in operation.get("parameters", [])
        if isinstance(parameter, dict) and parameter.get("in") == "query" and parameter.get("name")
    }


def _validate_layout(operation: dict[str, Any], layout: str) -> None:
    query_params = _query_parameter_names(operation)
    if not {"limit", "offset"}.issubset(query_params):
        raise ValueError("GET list views require limit/offset pagination in the OpenAPI spec")
    non_filtering_params = {"limit", "offset", "page", "sort", "sortBy", "order", "orderBy"}
    if query_params <= non_filtering_params:
        raise ValueError("GET list views require at least one query filter in the OpenAPI spec")
    if layout == "table" and not ({"sort", "sortBy", "order", "orderBy"} & query_params):
        raise ValueError("DataTable generation requires an explicit sorting query parameter in the OpenAPI spec")


def _pascal_case(value: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", value)
    return "".join(part[:1].upper() + part[1:] for part in parts if part)


def _human_label(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = value.replace("_", " ").replace("-", " ")
    return " ".join(part.capitalize() for part in value.split())


def _dart_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _field_is_scalar(schema: dict[str, Any]) -> bool:
    schema_type = schema.get("type", "string")
    if isinstance(schema_type, list):
        return any(item in {"string", "integer", "number", "boolean"} for item in schema_type)
    return schema_type in {"string", "integer", "number", "boolean"}


def _extract_fields(spec: dict[str, Any], operation: dict[str, Any], max_fields: int = 6) -> list[ViewField]:
    item_schema = _item_schema(spec, operation)
    properties = item_schema.get("properties", {})
    fields: list[ViewField] = []
    for name, raw_schema in properties.items():
        schema = _resolve_schema(spec, raw_schema) if isinstance(raw_schema, dict) else {}
        if _field_is_scalar(schema):
            fields.append(ViewField(name=name, label=_human_label(name)))
        if len(fields) >= max_fields:
            break
    if not fields:
        raise ValueError("No scalar fields found for generated list view")
    return fields


def _emit_card_fields(fields: list[ViewField]) -> list[str]:
    lines: list[str] = []
    for field in fields:
        lines.extend(
            [
                "                    Text(",
                f"                      '{field.label}: ${{row[{_dart_string(field.name)}] ?? ''}}',",
                "                    ),",
            ]
        )
    return lines


def _emit_table_columns(fields: list[ViewField]) -> str:
    return ", ".join(f"DataColumn(label: Text({_dart_string(field.label)}))" for field in fields)


def _emit_table_cells(fields: list[ViewField]) -> str:
    return ", ".join(f"DataCell(Text('${{row[{_dart_string(field.name)}] ?? ''}}'))" for field in fields)


def generate_view(path: str, operation: dict[str, Any], fields: list[ViewField], layout: str) -> str:
    operation_id = operation.get("operationId") or f"GET_{path}"
    title = operation.get("summary") or operation_id
    class_suffix = "Table" if layout == "table" else "CardList"
    class_name = f"{_pascal_case(operation_id)}LowCode{class_suffix}"
    permission = f"{operation_id}:read"

    if layout == "table":
        body_lines = [
            "          SingleChildScrollView(",
            "            scrollDirection: Axis.horizontal,",
            "            child: DataTable(",
            f"              columns: [{_emit_table_columns(fields)}],",
            "              rows: [",
            "                for (final row in rows)",
            f"                  DataRow(cells: [{_emit_table_cells(fields)}]),",
            "              ],",
            "            ),",
            "          ),",
        ]
    else:
        body_lines = [
            "          for (final row in rows)",
            "            Card(",
            "              child: Padding(",
            "                padding: const EdgeInsets.all(16),",
            "                child: Column(",
            "                  crossAxisAlignment: CrossAxisAlignment.start,",
            "                  children: [",
            *_emit_card_fields(fields),
            "                  ],",
            "                ),",
            "              ),",
            "            ),",
        ]

    return "\n".join(
        [
            "// AUTO-GENERATED - DO NOT EDIT MANUALLY",
            "// Generated from one approved OpenAPI GET operation for the SAHOOL Low-Code Builder PoC.",
            "// This widget renders caller-provided rows only; it does not perform API calls.",
            "// TENANT_ID_REQUIRED",
            "// PERMISSION_CHECK_REQUIRED",
            "",
            "import 'package:flutter/material.dart';",
            "",
            f"class {class_name} extends StatelessWidget {{",
            f"  const {class_name}({{",
            "    super.key,",
            "    required this.tenantId,",
            "    required this.permissions,",
            "    required this.rows,",
            "    this.onRefresh,",
            "  });",
            "",
            f"  static const requiredPermission = {_dart_string(permission)};",
            "  final String tenantId;",
            "  final Set<String> permissions;",
            "  final List<Map<String, Object?>> rows;",
            "  final VoidCallback? onRefresh;",
            "",
            "  @override",
            "  Widget build(BuildContext context) {",
            "    if (tenantId.trim().isEmpty) {",
            "      return const _LowCodeGuardMessage(message: 'Tenant context is required before UI generation.');",
            "    }",
            "    if (!permissions.contains(requiredPermission)) {",
            "      return const _LowCodeGuardMessage(message: 'Missing permission for generated view.');",
            "    }",
            "",
            "    return ListView(",
            "      padding: const EdgeInsets.all(16),",
            "      children: [",
            "        Row(",
            "          children: [",
            f"            Expanded(child: Text({_dart_string(title)}, style: Theme.of(context).textTheme.titleLarge)),",
            "            IconButton(",
            "              // PERMISSION_CHECK_REQUIRED",
            "              onPressed: onRefresh,",
            "              icon: const Icon(Icons.refresh),",
            "              tooltip: 'Refresh / تحديث',",
            "            ),",
            "          ],",
            "        ),",
            "        const SizedBox(height: 16),",
            "        if (rows.isEmpty)",
            "          const Card(",
            "            child: Padding(",
            "              padding: EdgeInsets.all(16),",
            "              child: Text('No records / لا توجد سجلات'),",
            "            ),",
            "          )",
            "        else",
            *body_lines,
            "      ],",
            "    );",
            "  }",
            "}",
            "",
            "class _LowCodeGuardMessage extends StatelessWidget {",
            "  const _LowCodeGuardMessage({required this.message});",
            "",
            "  final String message;",
            "",
            "  @override",
            "  Widget build(BuildContext context) {",
            "    return Card(",
            "      child: Padding(",
            "        padding: const EdgeInsets.all(16),",
            "        child: Text(message),",
            "      ),",
            "    );",
            "  }",
            "}",
            "",
        ]
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--openapi", type=Path, required=True)
    parser.add_argument("--operation-id", required=True)
    parser.add_argument("--layout", choices=("card", "table"), default="card")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    args = parser.parse_args()

    spec = _load_openapi(args.openapi)
    path, _method, operation = _operation_by_id(spec, args.operation_id)
    _validate_layout(operation, args.layout)
    fields = _extract_fields(spec, operation)

    suffix = "table" if args.layout == "table" else "card_list"
    filename = f"{re.sub(r'[^a-zA-Z0-9]+', '_', args.operation_id).strip('_').lower()}_{suffix}.dart"
    output_path = args.output_dir / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_view(path, operation, fields, args.layout), encoding="utf-8")
    print(f"Generated {output_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
