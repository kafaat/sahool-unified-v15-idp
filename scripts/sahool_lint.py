#!/usr/bin/env python3
"""Simple SAHOOL starter linter.

Checks the intentionally small starter surface:
- SAHOOL_DESIGN.md exists and references token sources.
- Exactly three starter skills exist.
- Starter skills include frontmatter, required sections, and no external imports.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent.parent
_DESIGN_DOC = _REPO_ROOT / "SAHOOL_DESIGN.md"
_SKILLS_DIR = _REPO_ROOT / ".claude" / "skills" / "sahool-starter"
_EXPECTED_SKILLS = {
    "dashboard/SKILL.md": "sahool-dashboard",
    "mobile-field-flow/SKILL.md": "sahool-mobile-field-flow",
    "ndvi-report/SKILL.md": "sahool-ndvi-report",
}
_REQUIRED_DESIGN_REFERENCES = (
    "governance/design/design-tokens.yaml",
    "shared/design-system/tokens.json",
    "colors.primary.500",
    "colors.state.synced",
    "colors.domain.ndvi_high",
)
_REQUIRED_SCOPE_STATEMENT = "Only these three starter skills are in scope"
_REQUIRED_SKILL_SECTIONS = ("## Scope", "## Required Inputs", "## Output Checklist", "## Do Not")
_FORBIDDEN_IMPORT_PATTERNS = (
    (r"\bsource:\s*github\b", "GitHub-sourced skill imports"),
    (r"\bsourceType:\s*github\b", "GitHub source metadata"),
    (r"\bimport\s+project\b", "whole-project imports"),
    (r"\bclone\s+", "clone-based imports"),
)


def create_lint_error(message: str) -> str:
    return f"SAHOOL-LINT: {message}"


def check_design_doc() -> list[str]:
    if not _DESIGN_DOC.exists():
        return [create_lint_error("SAHOOL_DESIGN.md is missing")]

    text = _DESIGN_DOC.read_text(encoding="utf-8")
    findings = [
        create_lint_error(f"SAHOOL_DESIGN.md must reference `{reference}`")
        for reference in _REQUIRED_DESIGN_REFERENCES
        if reference not in text
    ]
    if _REQUIRED_SCOPE_STATEMENT not in text:
        findings.append(create_lint_error("SAHOOL_DESIGN.md must state the three-skill starter scope"))
    return findings


def parse_frontmatter(text: str) -> dict[str, str]:
    """Parse the YAML-style frontmatter block used by starter skills."""

    if not text.startswith("---\n"):
        return {}

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    frontmatter: dict[str, str] = {}
    for line in parts[1].splitlines():
        line = line.strip()
        if not line:
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()
    return frontmatter


def check_skill_file(path: Path, expected_name: str) -> list[str]:
    text = path.read_text(encoding="utf-8")
    findings: list[str] = []
    frontmatter = parse_frontmatter(text)

    if frontmatter.get("name") != expected_name:
        findings.append(create_lint_error(f"{path.relative_to(_REPO_ROOT)} must declare name `{expected_name}`"))
    if not frontmatter.get("description"):
        findings.append(create_lint_error(f"{path.relative_to(_REPO_ROOT)} must include a description"))

    for section in _REQUIRED_SKILL_SECTIONS:
        if section not in text:
            findings.append(create_lint_error(f"{path.relative_to(_REPO_ROOT)} missing section `{section}`"))

    for pattern, description in _FORBIDDEN_IMPORT_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append(create_lint_error(f"{path.relative_to(_REPO_ROOT)} contains forbidden content: {description}"))

    if "SAHOOL_DESIGN.md" not in text:
        findings.append(create_lint_error(f"{path.relative_to(_REPO_ROOT)} must reference SAHOOL_DESIGN.md"))

    return findings


def check_starter_skills() -> list[str]:
    if not _SKILLS_DIR.exists():
        return [create_lint_error(".claude/skills/sahool-starter is missing")]

    actual_files = sorted(path.relative_to(_SKILLS_DIR).as_posix() for path in _SKILLS_DIR.rglob("SKILL.md"))
    expected_files = sorted(_EXPECTED_SKILLS)
    if actual_files != expected_files:
        return [create_lint_error(f"starter skills must be exactly {expected_files}; found {actual_files}")]

    findings: list[str] = []
    for filename, expected_name in _EXPECTED_SKILLS.items():
        findings.extend(check_skill_file(_SKILLS_DIR / filename, expected_name))
    return findings


def main() -> int:
    findings = [*check_design_doc(), *check_starter_skills()]
    if findings:
        print("\n".join(findings), file=sys.stderr)
        return 1

    print("SAHOOL-LINT: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
