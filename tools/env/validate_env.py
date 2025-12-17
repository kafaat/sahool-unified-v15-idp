#!/usr/bin/env python3
"""
SAHOOL Environment Validator
Validates environment variables against required_env.json schema.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_FILE = ROOT / "tools/env/required_env.json"


def load_schema() -> dict:
    """Load the environment schema."""
    with open(SCHEMA_FILE) as f:
        return json.load(f)


def validate_var(name: str, value: str | None, spec: dict) -> list[str]:
    """Validate a single environment variable."""
    errors = []

    # Check if required
    if spec.get("required", False) and not value:
        errors.append(f"❌ {name}: Required but not set")
        return errors

    if not value:
        return errors

    # Check minimum length
    min_length = spec.get("min_length")
    if min_length and len(value) < min_length:
        errors.append(f"❌ {name}: Must be at least {min_length} characters")

    # Check allowed values
    allowed = spec.get("allowed_values")
    if allowed and value not in allowed:
        errors.append(f"❌ {name}: Must be one of {allowed}, got '{value}'")

    # Check pattern
    pattern = spec.get("pattern")
    if pattern and not re.match(pattern, value):
        errors.append(f"❌ {name}: Does not match pattern {pattern}")

    return errors


def main() -> int:
    """Main validation function."""
    print("🔍 Validating SAHOOL environment variables...")
    print("=" * 60)

    # Load .env file if exists
    env_file = ROOT / ".env"
    if env_file.exists():
        print(f"📄 Loading from {env_file}")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, _, value = line.partition("=")
                    os.environ.setdefault(key.strip(), value.strip())

    schema = load_schema()
    all_errors = []

    # Validate required variables
    print("\n📋 Required Variables:")
    for category, vars_list in schema.get("required_vars", {}).items():
        print(f"\n  [{category}]")
        for var_spec in vars_list:
            name = var_spec["name"]
            value = os.environ.get(name)
            errors = validate_var(name, value, var_spec)

            if errors:
                all_errors.extend(errors)
                for err in errors:
                    print(f"    {err}")
            else:
                display = "***" if "secret" in name.lower() or "key" in name.lower() else value
                print(f"    ✅ {name}: {display}")

    # Check optional variables (just informational)
    print("\n📋 Optional Variables:")
    for category, vars_list in schema.get("optional_vars", {}).items():
        print(f"\n  [{category}]")
        for var_spec in vars_list:
            name = var_spec["name"]
            value = os.environ.get(name)
            default = var_spec.get("default")

            if value:
                display = "***" if "secret" in name.lower() or "key" in name.lower() else value
                print(f"    ✅ {name}: {display}")
            elif default:
                print(f"    ⚪ {name}: (using default: {default})")
            else:
                print(f"    ⚪ {name}: (not set)")

    print("\n" + "=" * 60)

    if all_errors:
        print(f"❌ Validation FAILED: {len(all_errors)} error(s) found")
        return 1
    else:
        print("✅ All required environment variables are valid!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
