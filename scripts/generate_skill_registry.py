#!/usr/bin/env python3
"""
generate_skill_registry.py — Bootstrap Skill Registry for Phase 1 (ADR-010).

Scans .claude/skills/ for SKILL.md (Anthropic spec) and legacy *.md skills,
extracts YAML frontmatter, and writes .claude/skills/index.yaml.

Deliberately minimal per ADR-010 Step 0:
- No schema validation
- No smart trigger extraction (simple quoted-phrase pull)
- No CLI flags
- No abstraction layers

The Skill Router (skill-router-service) consumes index.yaml as its data source.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

SKILLS_DIR = Path(__file__).resolve().parent.parent / ".claude" / "skills"
REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = SKILLS_DIR / "index.yaml"


def parse_frontmatter(md_path: Path) -> dict | None:
    """Return the YAML frontmatter dict, or None if no frontmatter present."""
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError:
        return None
    return fm if isinstance(fm, dict) else None


def extract_triggers(description: str) -> list[str]:
    """Pull quoted phrases from description as trigger keywords.

    Router will refine these at runtime; index is just a starting point.
    """
    quoted = re.findall(r'"([^"]+)"', description or "")
    quoted += re.findall(r"'([^']+)'", description or "")
    # Deduplicate, preserve order
    seen: set[str] = set()
    result: list[str] = []
    for phrase in quoted:
        key = phrase.lower().strip()
        if key and key not in seen:
            seen.add(key)
            result.append(phrase.strip())
    return result


def build_entry(md_path: Path, fm: dict, source: str) -> dict | None:
    """Build one registry entry from frontmatter."""
    name = fm.get("name")
    if not name:
        return None

    metadata = fm.get("metadata") or {}
    skill_path = md_path.parent if source == "SKILL.md" else md_path
    rel_path = skill_path.relative_to(REPO_ROOT).as_posix()

    return {
        "name": name,
        "path": rel_path,
        "version": str(metadata.get("version", "0.1.0")),
        "description": fm.get("description", "").strip(),
        "triggers": extract_triggers(fm.get("description", "")),
        "tenant_id": "*",
        "deprecated": False,
        "source": source,
    }


def main() -> int:
    skills: list[dict] = []
    skipped: list[str] = []

    # 1. Anthropic-compliant skills (SKILL.md inside skill folders)
    for md in sorted(SKILLS_DIR.rglob("SKILL.md")):
        fm = parse_frontmatter(md)
        if not fm:
            skipped.append(md.relative_to(REPO_ROOT).as_posix())
            continue
        entry = build_entry(md, fm, source="SKILL.md")
        if entry:
            skills.append(entry)
        else:
            skipped.append(md.relative_to(REPO_ROOT).as_posix())

    # 2. Legacy skills (single *.md grouped under category folders)
    for md in sorted(SKILLS_DIR.rglob("*.md")):
        if md.name in ("SKILL.md", "README.md"):
            continue
        if md.parent == SKILLS_DIR:  # root README/index
            continue
        # Skip files inside a folder that also contains a SKILL.md (reference files)
        if (md.parent / "SKILL.md").exists():
            continue
        fm = parse_frontmatter(md)
        if not fm:
            skipped.append(md.relative_to(REPO_ROOT).as_posix())
            continue
        entry = build_entry(md, fm, source="legacy")
        if entry:
            skills.append(entry)

    # Deduplicate by name (first wins)
    seen_names: set[str] = set()
    deduped: list[dict] = []
    for s in skills:
        if s["name"] in seen_names:
            continue
        seen_names.add(s["name"])
        deduped.append(s)

    output = {
        "version": "0.1.0",
        "generated_by": "scripts/generate_skill_registry.py",
        "skill_count": len(deduped),
        "skills": sorted(deduped, key=lambda s: s["name"]),
    }

    OUTPUT.write_text(
        yaml.safe_dump(output, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )

    print(f"Wrote {len(deduped)} skills to {OUTPUT.relative_to(REPO_ROOT)}")
    if skipped:
        print(f"Skipped {len(skipped)} file(s) without valid frontmatter:", file=sys.stderr)
        for p in skipped:
            print(f"  - {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
