#!/usr/bin/env python3
"""
generate_skill_registry.py — Bootstrap Skill Registry for Phase 1 (ADR-010).

Scans .claude/skills/ for SKILL.md (Anthropic spec) and legacy *.md skills,
extracts YAML frontmatter, and writes .claude/skills/index.yaml.

Deliberately minimal per ADR-010 Step 0:
- No schema validation
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

# Iteration 1 P0: keyword extraction stopwords (common English + skill boilerplate).
_STOPWORDS = {
    "a", "an", "the", "this", "that", "these", "those",
    "for", "to", "of", "in", "on", "at", "by", "with",
    "and", "or", "but", "not", "is", "are", "was", "were",
    "from", "as", "into", "onto", "about", "any", "all", "some",
    "use", "used", "uses", "using", "when", "trigger", "asks",
    "user", "your", "our", "my", "their", "its", "it",
    "what", "whether", "such", "also", "only", "than",
    "has", "have", "had", "will", "should", "would", "can",
    "here", "there", "then", "now",
}

# Iteration 2 P1: tokens that look like acronyms but are skill-boilerplate noise.
_CAPS_NOISE = {"TRIGGER", "DO", "NOT", "OR", "AND", "ARE", "AI", "ML", "SDK"}


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


def _add(result: list[str], seen: set[str], token: str) -> None:
    """Add a normalized trigger if not already present."""
    key = token.lower().strip()
    if not key or key in seen:
        return
    seen.add(key)
    result.append(token.strip())


def extract_triggers(description: str) -> list[str]:
    """Extract trigger phrases and individual keywords.

    Strategy:
      P0 (already present):
        1. Quoted phrases as-is (multi-word matchers).
        2. Keywords from within quoted phrases.
        3. Slash-separated tech tokens (ruff/mypy/bandit, SRT/VTT).
        4. Slash-commands and hyphenated tool names.
      P1 (body-keyword extraction):
        5. ALL-CAPS acronyms anywhere in description (NDVI, RPW, PHI, LAI, GPS).
        6. Mixed-case internal-capital tokens (PostGIS, FastAPI, SQLCipher).
        7. Words inside parentheticals (Pydantic, Riverpod, NATS, health endpoints).
    """
    result: list[str] = []
    seen: set[str] = set()
    text = description or ""

    # 1. Quoted phrases (double + single quotes, curly quotes).
    phrase_pattern = re.compile(r'["\'""„«]([^"\'""„«»]+)["\'""»]')
    phrases = phrase_pattern.findall(text)
    for phrase in phrases:
        _add(result, seen, phrase)

    # 2. Keywords within quoted phrases (length >=4, not stopword).
    for phrase in phrases:
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", phrase):
            wl = word.lower()
            if wl not in _STOPWORDS:
                _add(result, seen, wl)

    # 3. Slash-separated tech tokens anywhere in description
    #    (e.g. "ruff/mypy/bandit", "SRT/VTT", "EN/AR").
    for tech in re.findall(r"\b([A-Za-z][A-Za-z0-9]+(?:/[A-Za-z][A-Za-z0-9]+)+)\b", text):
        for word in tech.split("/"):
            wl = word.lower()
            if len(wl) >= 3 and wl not in _STOPWORDS:
                _add(result, seen, wl)

    # 4. Slash-commands and tool names (/fixops-run, /check-contracts, code-fix-agent).
    for token in re.findall(r"/([a-z][a-z0-9-]+)|\b([a-z][a-z0-9]*(?:-[a-z][a-z0-9]*)+)\b", text):
        for t in token:
            if t and len(t) >= 4:
                _add(result, seen, t.lower())

    # 5. All-caps acronyms (NDVI, RPW, LAI, PHI, GPS, NATS, SQL, RBAC).
    for acronym in re.findall(r"\b[A-Z]{2,}\b", text):
        if acronym in _CAPS_NOISE:
            continue
        _add(result, seen, acronym.lower())

    # 6. Mixed-case tokens with internal capital (PostGIS, FastAPI, SQLCipher, NestJS).
    for word in re.findall(r"\b[A-Z][a-z]+[A-Z][A-Za-z0-9]+\b", text):
        _add(result, seen, word.lower())

    # 7. Parenthetical content — technical term lists.
    for paren in re.findall(r"\(([^)]+)\)", text):
        for word in re.findall(r"[A-Za-z][A-Za-z0-9_-]{3,}", paren):
            wl = word.lower()
            if wl not in _STOPWORDS:
                _add(result, seen, wl)

    return result


def _is_external(skill_path: Path) -> bool:
    """Bundled plugin skills live in folders we recognize as external."""
    external_markers = {
        "docker-development",
        "docker-compose-orchestration",
        "next-best-practices",
        "next-upgrade",
        "postgres-best-practices",
    }
    # Check the skill folder itself plus all its parents
    return any(part in external_markers for part in skill_path.parts)


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
        "external": _is_external(skill_path),
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
        "version": "0.2.0",  # bumped for Iteration 1 P0 schema (external field, keyword triggers)
        "generated_by": "scripts/generate_skill_registry.py",
        "skill_count": len(deduped),
        "skills": sorted(deduped, key=lambda s: s["name"]),
    }

    OUTPUT.write_text(
        yaml.safe_dump(output, sort_keys=False, allow_unicode=True, width=120),
        encoding="utf-8",
    )

    print(f"Wrote {len(deduped)} skills to {OUTPUT.relative_to(REPO_ROOT)}")
    external_count = sum(1 for s in deduped if s.get("external"))
    print(f"  - {external_count} flagged external (bundled plugins)")
    if skipped:
        print(f"Skipped {len(skipped)} file(s) without valid frontmatter:", file=sys.stderr)
        for p in skipped:
            print(f"  - {p}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
