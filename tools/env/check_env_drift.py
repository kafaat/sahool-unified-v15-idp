#!/usr/bin/env python3
"""
SAHOOL ENV Drift Checker
Compares ENV variables used in code against .env.example documentation.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV_EXAMPLE = ROOT / ".env.example"
USED_ENV_FILE = ROOT / "tools/env/used_env.txt"


def parse_env_example() -> set[str]:
    """Parse .env.example to get documented variables."""
    keys = set()

    if not ENV_EXAMPLE.exists():
        print(f"⚠️  {ENV_EXAMPLE} not found!")
        return keys

    for line in ENV_EXAMPLE.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key = line.split("=")[0].strip()
            keys.add(key)

    return keys


def parse_used_env() -> set[str]:
    """Parse used_env.txt to get variables found in code."""
    if not USED_ENV_FILE.exists():
        print(f"⚠️  {USED_ENV_FILE} not found!")
        print("   Run: python tools/env/scan_env_usage.py > tools/env/used_env.txt")
        return set()

    return set(
        line.strip() for line in USED_ENV_FILE.read_text().splitlines() if line.strip()
    )


def main() -> int:
    """Main drift check function."""
    print("🔍 Checking for ENV drift...")
    print("=" * 60)

    documented = parse_env_example()
    used = parse_used_env()

    # Variables used but not documented
    missing = used - documented

    # Variables documented but not used (informational)
    unused = documented - used

    print(f"\n📊 Summary:")
    print(f"   Documented in .env.example: {len(documented)}")
    print(f"   Used in codebase: {len(used)}")

    if missing:
        print(
            f"\n❌ ENV vars used in code but missing in .env.example ({len(missing)}):"
        )
        for key in sorted(missing):
            print(f"   - {key}")

    if unused:
        print(f"\n⚠️  ENV vars documented but not found in code ({len(unused)}):")
        for key in sorted(unused):
            print(f"   - {key} (may be used in config files)")

    print("\n" + "=" * 60)

    if missing:
        print("❌ ENV drift detected! Please update .env.example")
        return 1

    print("✅ No ENV drift detected!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
