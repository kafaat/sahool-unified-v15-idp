from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

SCHEMA_DIR = Path(__file__).resolve().parents[2] / "governance" / "schemas"

# Minimal JSON-schema-ish validation:
# - ensures required keys exist
# - ensures schema_version and event_type match expected
# We avoid adding heavy deps; full JSON Schema validation can be enabled later with jsonschema package.


def _load_schema(event_type: str, schema_version: str) -> Dict[str, Any]:
    fname = f"{event_type}.{schema_version}.json"
    path = SCHEMA_DIR / fname
    if not path.exists():
        raise FileNotFoundError(f"Missing schema file: governance/schemas/{fname}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_event(event: Dict[str, Any], *, expect_type: Optional[str] = None, expect_version: str = "v15.2") -> Tuple[bool, str]:
    if not isinstance(event, dict):
        return False, "event_not_object"

    required = ["event_id","event_type","tenant_id","timestamp","correlation_id","payload","schema_version"]
    for k in required:
        if k not in event:
            return False, f"missing_{k}"

    if expect_type and event.get("event_type") != expect_type:
        return False, "event_type_mismatch"

    if event.get("schema_version") != expect_version:
        return False, "schema_version_mismatch"

    # lightweight schema file presence check
    try:
        _load_schema(event.get("event_type",""), event.get("schema_version",""))
    except Exception as e:
        return False, f"schema_missing_or_invalid:{e}"

    # payload must be dict
    if not isinstance(event.get("payload"), dict):
        return False, "payload_not_object"

    return True, "ok"
