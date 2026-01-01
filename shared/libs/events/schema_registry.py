"""
SAHOOL Schema Registry
Loads and validates event schemas from contracts
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Optional dependency for validation
try:
    import jsonschema

    HAS_JSONSCHEMA = True
except ImportError:
    jsonschema = None  # type: ignore
    HAS_JSONSCHEMA = False


# Path configuration
ROOT = Path(__file__).resolve().parents[3]
REGISTRY_FILE = ROOT / "shared" / "contracts" / "events" / "registry.json"
SCHEMAS_DIR = ROOT / "shared" / "contracts" / "events"


@dataclass(frozen=True)
class SchemaEntry:
    """Metadata about a registered event schema"""

    ref: str
    file: str
    topic: str
    version: int
    owner: str
    breaking_policy: str = "new_version"


class SchemaRegistry:
    """
    Registry for event schemas.

    Loads schemas from shared/contracts/events/ and provides validation.
    """

    def __init__(
        self,
        entries: dict[str, SchemaEntry],
        schemas: dict[str, dict[str, Any]],
    ):
        self._entries = entries
        self._schemas = schemas

    @classmethod
    def load(cls, registry_path: Path | None = None) -> SchemaRegistry:
        """
        Load the schema registry from disk.

        Args:
            registry_path: Optional path to registry.json (defaults to standard location)

        Returns:
            SchemaRegistry instance
        """
        reg_file = registry_path or REGISTRY_FILE
        schemas_dir = reg_file.parent

        if not reg_file.exists():
            raise FileNotFoundError(f"Registry file not found: {reg_file}")

        data = json.loads(reg_file.read_text(encoding="utf-8"))
        entries: dict[str, SchemaEntry] = {}
        schemas: dict[str, dict[str, Any]] = {}

        for item in data.get("schemas", []):
            entry = SchemaEntry(
                ref=item["ref"],
                file=item["file"],
                topic=item["topic"],
                version=int(item["version"]),
                owner=item.get("owner", "unknown"),
                breaking_policy=item.get("breaking_policy", "new_version"),
            )
            entries[entry.ref] = entry

            # Load the actual schema
            schema_path = schemas_dir / entry.file
            if schema_path.exists():
                schemas[entry.ref] = json.loads(schema_path.read_text(encoding="utf-8"))
            else:
                raise FileNotFoundError(f"Schema file not found: {schema_path}")

        return cls(entries=entries, schemas=schemas)

    def entry(self, schema_ref: str) -> SchemaEntry:
        """
        Get schema entry by reference.

        Args:
            schema_ref: Schema reference (e.g., 'events.field.created:v1')

        Returns:
            SchemaEntry

        Raises:
            KeyError: If schema_ref is not registered
        """
        if schema_ref not in self._entries:
            raise KeyError(f"Unknown schema_ref: {schema_ref}")
        return self._entries[schema_ref]

    def get_schema(self, schema_ref: str) -> dict[str, Any]:
        """
        Get the JSON schema for a reference.

        Args:
            schema_ref: Schema reference

        Returns:
            JSON Schema dictionary

        Raises:
            KeyError: If schema not found
        """
        if schema_ref not in self._schemas:
            raise KeyError(f"Schema not found for ref: {schema_ref}")
        return self._schemas[schema_ref]

    def validate(self, schema_ref: str, payload: dict[str, Any]) -> None:
        """
        Validate a payload against its schema.

        Args:
            schema_ref: Schema reference
            payload: Event payload to validate

        Raises:
            RuntimeError: If jsonschema is not installed
            KeyError: If schema not found
            jsonschema.ValidationError: If payload is invalid
        """
        if not HAS_JSONSCHEMA:
            raise RuntimeError(
                "jsonschema is not installed. "
                "Add it to dependencies: pip install jsonschema"
            )

        schema = self.get_schema(schema_ref)
        # Enable format validation for UUIDs, dates, etc.
        validator = jsonschema.Draft202012Validator(
            schema, format_checker=jsonschema.FormatChecker()
        )
        validator.validate(payload)

    def list_schemas(self) -> list[SchemaEntry]:
        """List all registered schemas"""
        return list(self._entries.values())

    def list_by_owner(self, owner: str) -> list[SchemaEntry]:
        """List schemas owned by a specific domain"""
        return [e for e in self._entries.values() if e.owner == owner]

    def list_topics(self) -> list[str]:
        """List all unique topics"""
        return list(set(e.topic for e in self._entries.values()))

    def __contains__(self, schema_ref: str) -> bool:
        """Check if a schema_ref is registered"""
        return schema_ref in self._entries
