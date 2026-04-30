#!/usr/bin/env python3
"""Generate a guarded Flutter form PoC from one OpenAPI operation."""

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
REQUIRED_MESSAGE = "Required / مطلوب"


@dataclass(frozen=True)
class Field:
    name: str
    dart_type: str
    label: str
    required: bool
    enum_values: tuple[str, ...] = ()
    multiline: bool = False


def _load_openapi(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as file:
        if path.suffix == ".json":
            return json.load(file)
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
    if "allOf" in schema:
        merged: dict[str, Any] = {"type": "object", "properties": {}, "required": []}
        for item in schema["allOf"]:
            resolved = _resolve_schema(spec, item)
            merged["properties"].update(resolved.get("properties", {}))
            merged["required"].extend(resolved.get("required", []))
        return merged
    return schema


def _operation_by_id(spec: dict[str, Any], operation_id: str) -> tuple[str, str, dict[str, Any]]:
    for path, methods in spec.get("paths", {}).items():
        if not isinstance(methods, dict):
            continue
        for method, operation in methods.items():
            if isinstance(operation, dict) and operation.get("operationId") == operation_id:
                return path, method.upper(), operation
    raise ValueError(f"OpenAPI operationId not found: {operation_id}")


def _operation_by_path(spec: dict[str, Any], path_value: str, method_value: str) -> tuple[str, str, dict[str, Any]]:
    operation = spec.get("paths", {}).get(path_value, {}).get(method_value.lower())
    if not isinstance(operation, dict):
        raise ValueError(f"OpenAPI operation not found: {method_value.upper()} {path_value}")
    return path_value, method_value.upper(), operation


def _request_schema(spec: dict[str, Any], operation: dict[str, Any]) -> dict[str, Any]:
    request_body = operation.get("requestBody") or {}
    if "$ref" in request_body:
        request_body = _resolve_ref(spec, request_body["$ref"])
    content = request_body.get("content") or {}
    media = content.get("application/json") or next(iter(content.values()), {})
    schema = media.get("schema") or {"type": "object", "properties": {}}
    return _resolve_schema(spec, schema)


def _field_type(property_schema: dict[str, Any]) -> str:
    if "enum" in property_schema:
        return "String"
    schema_type = property_schema.get("type", "string")
    if schema_type == "integer":
        return "int"
    if schema_type == "number":
        return "double"
    if schema_type == "boolean":
        return "bool"
    return "String"


def _extract_fields(spec: dict[str, Any], operation: dict[str, Any]) -> list[Field]:
    schema = _request_schema(spec, operation)
    properties = schema.get("properties", {})
    required = set(schema.get("required", []))
    fields: list[Field] = []

    for name, raw_property_schema in properties.items():
        property_schema = _resolve_schema(spec, raw_property_schema)
        description = property_schema.get("description") or _human_label(name)
        enum_values = tuple(str(value) for value in property_schema.get("enum", []))
        fields.append(
            Field(
                name=name,
                dart_type=_field_type(property_schema),
                label=str(description).replace("\n", " "),
                required=name in required,
                enum_values=enum_values,
                multiline=property_schema.get("type") == "object" or property_schema.get("type") == "array",
            )
        )
    return fields


def _pascal_case(value: str) -> str:
    parts = re.split(r"[^a-zA-Z0-9]+", value)
    return "".join(part[:1].upper() + part[1:] for part in parts if part)


def _camel_case(value: str) -> str:
    pascal = _pascal_case(value)
    return pascal[:1].lower() + pascal[1:]


def _human_label(value: str) -> str:
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", value)
    value = value.replace("_", " ").replace("-", " ")
    return " ".join(part.capitalize() for part in value.split())


def _dart_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def _emit_field_controller(field: Field) -> str:
    if field.dart_type == "bool" or field.enum_values:
        return ""
    return f"  final _{_camel_case(field.name)}Controller = TextEditingController();"


def _emit_dispose(field: Field) -> str:
    if field.dart_type == "bool" or field.enum_values:
        return ""
    return f"    _{_camel_case(field.name)}Controller.dispose();"


def _emit_state(field: Field) -> str:
    name = _camel_case(field.name)
    if field.dart_type == "bool":
        return f"  bool _{name} = false;"
    if field.enum_values:
        return f"  String? _{name};"
    return ""


def _emit_payload_line(field: Field) -> str:
    key = _dart_string(field.name)
    name = _camel_case(field.name)
    if field.dart_type == "bool" or field.enum_values:
        return f"      {key}: _{name},"
    if field.dart_type == "int":
        return f"      {key}: int.tryParse(_{name}Controller.text),"
    if field.dart_type == "double":
        return f"      {key}: double.tryParse(_{name}Controller.text),"
    return f"      {key}: _{name}Controller.text.trim(),"


def _emit_validator(field: Field) -> str:
    if not field.required or field.dart_type == "bool":
        return "null"
    if field.enum_values:
        return f"(value) => value == null ? {_dart_string(REQUIRED_MESSAGE)} : null"
    if field.dart_type == "int":
        return (
            f"(value) => value == null || value.trim().isEmpty ? {_dart_string(REQUIRED_MESSAGE)} "
            f": int.tryParse(value.trim()) == null ? {_dart_string('Enter a valid integer / أدخل عددًا صحيحًا')} : null"
        )
    if field.dart_type == "double":
        return (
            f"(value) => value == null || value.trim().isEmpty ? {_dart_string(REQUIRED_MESSAGE)} "
            f": double.tryParse(value.trim()) == null ? {_dart_string('Enter a valid number / أدخل رقمًا صحيحًا')} : null"
        )
    return f"(value) => value == null || value.trim().isEmpty ? {_dart_string(REQUIRED_MESSAGE)} : null"


def _emit_widget(field: Field) -> str:
    name = _camel_case(field.name)
    label = _dart_string(field.label)
    if field.dart_type == "bool":
        return "\n".join(
            [
                "          CheckboxListTile(",
                f"            title: Text({label}),",
                f"            value: _{name},",
                f"            onChanged: (value) => setState(() => _{name} = value ?? false),",
                "          ),",
            ]
        )
    if field.enum_values:
        items = [
            f"              DropdownMenuItem(value: {_dart_string(value)}, child: Text({_dart_string(value)})),"
            for value in field.enum_values
        ]
        return "\n".join(
            [
                "          DropdownButtonFormField<String>(",
                f"            value: _{name},",
                f"            decoration: const InputDecoration(labelText: {label}),",
                "            items: [",
                *items,
                "            ],",
                f"            validator: {_emit_validator(field)},",
                f"            onChanged: (value) => setState(() => _{name} = value ?? _{name}),",
                "          ),",
            ]
        )
    keyboard_type = "TextInputType.number" if field.dart_type in {"int", "double"} else "TextInputType.text"
    max_lines = "3" if field.multiline else "1"
    return "\n".join(
        [
            "          TextFormField(",
            f"            controller: _{name}Controller,",
            f"            decoration: const InputDecoration(labelText: {label}),",
            f"            keyboardType: {keyboard_type},",
            f"            maxLines: {max_lines},",
            f"            validator: {_emit_validator(field)},",
            "          ),",
        ]
    )


def generate_widget(
    spec: dict[str, Any],
    path: str,
    method: str,
    operation: dict[str, Any],
    fields: list[Field],
    permission: str | None = None,
) -> str:
    operation_id = operation.get("operationId") or f"{method}_{path}"
    class_name = f"{_pascal_case(operation_id)}LowCodeForm"
    title = operation.get("summary") or operation_id
    required_permission = permission or f"{operation_id}:write"

    return "\n".join(
        [
            "// AUTO-GENERATED - DO NOT EDIT MANUALLY",
            "// Generated from one OpenAPI operation for the SAHOOL Low-Code PoC.",
            "// This widget intentionally emits form data via onSubmit; it does not perform API calls.",
            "// TENANT_ID_REQUIRED",
            "// PERMISSION_CHECK_REQUIRED",
            "",
            "import 'package:flutter/material.dart';",
            "",
            f"class {class_name} extends StatefulWidget {{",
            f"  const {class_name}({{",
            "    super.key,",
            "    required this.tenantId,",
            "    required this.permissions,",
            "    required this.onSubmit,",
            "  });",
            "",
            "  final String tenantId;",
            "  final Set<String> permissions;",
            "  final ValueChanged<Map<String, Object?>> onSubmit;",
            "",
            "  @override",
            f"  State<{class_name}> createState() => _{class_name}State();",
            "}",
            "",
            f"class _{class_name}State extends State<{class_name}> {{",
            "  static const requiredPermission = " + _dart_string(required_permission) + ";",
            "  final _formKey = GlobalKey<FormState>();",
            *[line for field in fields for line in (_emit_field_controller(field), _emit_state(field)) if line],
            "",
            "  @override",
            "  void dispose() {",
            *[line for field in fields if (line := _emit_dispose(field))],
            "    super.dispose();",
            "  }",
            "",
            "  void _submit() {",
            "    if (!_formKey.currentState!.validate()) {",
            "      return;",
            "    }",
            "    widget.onSubmit(<String, Object?>{",
            "      'tenantId': widget.tenantId,",
            "      'operationId': " + _dart_string(operation_id) + ",",
            "      'method': " + _dart_string(method) + ",",
            "      'path': " + _dart_string(path) + ",",
            *[_emit_payload_line(field) for field in fields],
            "    });",
            "  }",
            "",
            "  @override",
            "  Widget build(BuildContext context) {",
            "    if (widget.tenantId.trim().isEmpty) {",
            "      return const _LowCodeGuardMessage(message: 'Tenant context is required before UI generation.');",
            "    }",
            "    if (!widget.permissions.contains(requiredPermission)) {",
            "      return const _LowCodeGuardMessage(message: 'Missing permission for generated form.');",
            "    }",
            "",
            "    return Form(",
            "      key: _formKey,",
            "      child: ListView(",
            "        padding: const EdgeInsets.all(16),",
            "        children: [",
            f"          Text({_dart_string(title)}, style: Theme.of(context).textTheme.titleLarge),",
            "          const SizedBox(height: 16),",
            *[_emit_widget(field) for field in fields],
            "          const SizedBox(height: 24),",
            "          FilledButton.icon(",
            "            // PERMISSION_CHECK_REQUIRED",
            "            onPressed: _submit,",
            "            icon: const Icon(Icons.check),",
            "            label: const Text('Submit'),",
            "          ),",
            "        ],",
            "      ),",
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
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--operation-id")
    group.add_argument("--path")
    parser.add_argument("--method", default="post")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--permission")
    args = parser.parse_args()

    spec = _load_openapi(args.openapi)
    if args.operation_id:
        path, method, operation = _operation_by_id(spec, args.operation_id)
    else:
        path, method, operation = _operation_by_path(spec, args.path, args.method)

    fields = _extract_fields(spec, operation)
    if not fields:
        raise ValueError("Selected OpenAPI operation has no JSON request-body fields to generate")

    operation_id = operation.get("operationId") or f"{method}_{path}"
    filename = f"{re.sub(r'[^a-zA-Z0-9]+', '_', operation_id).strip('_').lower()}_form.dart"
    output_path = args.output_dir / filename
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(generate_widget(spec, path, method, operation, fields, args.permission), encoding="utf-8")
    print(f"Generated {output_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
