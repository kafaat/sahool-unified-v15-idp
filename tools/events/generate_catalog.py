#!/usr/bin/env python3
"""
SAHOOL Event Catalog Generator
Generates documentation from event schema registry.

Usage:
    python -m tools.events.generate_catalog
    # or
    make event-catalog
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REGISTRY_FILE = ROOT / "shared" / "contracts" / "events" / "registry.json"
OUTPUT_FILE = ROOT / "docs" / "EVENT_CATALOG.md"


def load_registry() -> dict:
    """Load the schema registry"""
    return json.loads(REGISTRY_FILE.read_text(encoding="utf-8"))


def load_schema(filename: str) -> dict:
    """Load an individual schema file"""
    schema_path = REGISTRY_FILE.parent / filename
    return json.loads(schema_path.read_text(encoding="utf-8"))


def generate_catalog() -> str:
    """Generate the event catalog markdown"""
    data = load_registry()
    schemas = data.get("schemas", [])

    lines = [
        "# Event Catalog",
        "",
        "> Auto-generated from `shared/contracts/events/registry.json`",
        f"> Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Overview",
        "",
        f"Total registered events: **{len(schemas)}**",
        "",
        "## Event Registry",
        "",
        "| Ref | Topic | Version | Owner | Breaking Policy |",
        "|-----|-------|--------:|-------|-----------------|",
    ]

    for s in schemas:
        ref = s.get("ref", "")
        topic = s.get("topic", "")
        version = s.get("version", 1)
        owner = s.get("owner", "unknown")
        policy = s.get("breaking_policy", "new_version")
        lines.append(f"| `{ref}` | `{topic}` | {version} | {owner} | {policy} |")

    lines.extend([
        "",
        "## Event Details",
        "",
    ])

    # Group by owner
    by_owner: dict[str, list] = {}
    for s in schemas:
        owner = s.get("owner", "unknown")
        if owner not in by_owner:
            by_owner[owner] = []
        by_owner[owner].append(s)

    for owner, owner_schemas in sorted(by_owner.items()):
        lines.append(f"### {owner}")
        lines.append("")

        for s in owner_schemas:
            ref = s.get("ref", "")
            topic = s.get("topic", "")
            filename = s.get("file", "")

            lines.append(f"#### `{topic}`")
            lines.append("")
            lines.append(f"- **Schema Ref:** `{ref}`")
            lines.append(f"- **Version:** {s.get('version', 1)}")
            lines.append(f"- **File:** `{filename}`")
            lines.append("")

            # Load schema for details
            try:
                schema = load_schema(filename)
                title = schema.get("title", "")
                desc = schema.get("description", "")

                if title:
                    lines.append(f"**{title}**")
                    lines.append("")
                if desc:
                    lines.append(f"{desc}")
                    lines.append("")

                # Required fields
                required = schema.get("required", [])
                if required:
                    lines.append("**Required Fields:**")
                    for field in required:
                        lines.append(f"- `{field}`")
                    lines.append("")

                # Properties
                props = schema.get("properties", {})
                if props:
                    lines.append("**Fields:**")
                    lines.append("")
                    lines.append("| Field | Type | Description |")
                    lines.append("|-------|------|-------------|")
                    for field_name, field_def in props.items():
                        field_type = field_def.get("type", "any")
                        if "format" in field_def:
                            field_type = f"{field_type} ({field_def['format']})"
                        field_desc = field_def.get("description", "")
                        is_required = "✓" if field_name in required else ""
                        lines.append(f"| `{field_name}` {is_required} | {field_type} | {field_desc} |")
                    lines.append("")

            except Exception as e:
                lines.append(f"_Error loading schema: {e}_")
                lines.append("")

    # Footer
    lines.extend([
        "---",
        "",
        "## Usage",
        "",
        "### Producing Events",
        "",
        "```python",
        "from shared.libs.events.producer import enqueue_event",
        "",
        "enqueue_event(",
        "    db=session,",
        "    event_type='field.created',",
        "    schema_ref='events.field.created:v1',",
        "    tenant_id=tenant_id,",
        "    correlation_id=correlation_id,",
        "    producer='field_suite',",
        "    payload={",
        "        'field_id': str(field.id),",
        "        'farm_id': str(field.farm_id),",
        "        'name': field.name,",
        "        'geometry_wkt': field.boundary_wkt,",
        "        'created_at': field.created_at.isoformat(),",
        "    },",
        ")",
        "```",
        "",
        "### Validating Payloads",
        "",
        "```python",
        "from shared.libs.events.schema_registry import SchemaRegistry",
        "",
        "registry = SchemaRegistry.load()",
        "registry.validate('events.field.created:v1', payload)",
        "```",
        "",
    ])

    return "\n".join(lines)


def main() -> None:
    """Generate and write the event catalog"""
    print("=" * 60)
    print("SAHOOL Event Catalog Generator")
    print("=" * 60)
    print()

    # Generate catalog
    catalog = generate_catalog()

    # Ensure output directory exists
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Write catalog
    OUTPUT_FILE.write_text(catalog, encoding="utf-8")

    print(f"✅ Generated {OUTPUT_FILE}")
    print(f"   Size: {len(catalog)} bytes")

    # Print summary
    data = load_registry()
    schemas = data.get("schemas", [])
    print(f"   Events: {len(schemas)}")


if __name__ == "__main__":
    main()
