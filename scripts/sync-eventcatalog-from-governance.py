#!/usr/bin/env python3
"""
sync-eventcatalog-from-governance.py – Generate EventCatalog entries from governance sources.

Reads:
  - governance/events/catalog.yaml        (event definitions)
  - governance/services.yaml              (service registry)

Validates that every event in the governance catalog has a corresponding
EventCatalog entry under idp/eventcatalog/events/.

Usage:
  python scripts/sync-eventcatalog-from-governance.py              # validate (CI)
  python scripts/sync-eventcatalog-from-governance.py --diff       # show missing entries
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("PyYAML is required: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
CATALOG_YAML = ROOT / "governance" / "events" / "catalog.yaml"
EVENTCATALOG_DIR = ROOT / "idp" / "eventcatalog"


def load_governance_events() -> dict[str, dict]:
    """Load events from governance catalog."""
    with open(CATALOG_YAML) as f:
        data = yaml.safe_load(f)
    return data.get("events", {})


def find_eventcatalog_entries() -> set[str]:
    """Find all event IDs present in the EventCatalog directory."""
    entries: set[str] = set()
    events_dir = EVENTCATALOG_DIR / "events"
    if not events_dir.exists():
        print(f"ℹ  EventCatalog events directory not found: {events_dir}", file=sys.stderr)
        return entries

    for index_md in events_dir.rglob("index.md"):
        # The parent directory name is the event ID
        event_id = index_md.parent.name
        entries.add(event_id)

    return entries


def validate() -> tuple[list[str], list[str]]:
    """Return (missing_in_catalog, extra_in_catalog) lists."""
    gov_events = set(load_governance_events().keys())
    catalog_entries = find_eventcatalog_entries()

    missing = sorted(gov_events - catalog_entries)
    extra = sorted(catalog_entries - gov_events)
    return missing, extra


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate EventCatalog entries against governance"
    )
    parser.add_argument("--diff", action="store_true", help="Show differences")
    args = parser.parse_args()

    if not CATALOG_YAML.exists():
        sys.exit(f"ERROR: {CATALOG_YAML} not found")

    missing, extra = validate()

    if missing:
        print(f"⚠  {len(missing)} governance events missing from EventCatalog:")
        for e in missing:
            print(f"   - {e}")

    if extra:
        print(f"ℹ  {len(extra)} EventCatalog entries not in governance (extensions):")
        for e in extra:
            print(f"   + {e}")

    if not missing and not extra:
        print("✅ EventCatalog is fully in sync with governance/events/catalog.yaml")
        return

    if missing and not args.diff:
        sys.exit(1)


if __name__ == "__main__":
    main()
