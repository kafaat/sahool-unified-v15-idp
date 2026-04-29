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


REPO_ROOT = Path(__file__).resolve().parent.parent
DESIGN_DOC = REPO_ROOT / "SAHOOL_DESIGN.md"
SKILLS_DIR = REPO_ROOT / ".claude" / "skills" / "sahool-starter"
EXPECTED_SKILLS = {
    "dashboard.md": "sahool-dashboard",
    "mobile-field-flow.md": "sahool-mobile-field-flow",
    "ndvi-report.md": "sahool-ndvi-report",
}
REQUIRED_DESIGN_REFERENCES = (
    "governance/design/design-tokens.yaml",
    "shared/design-system/tokens.json",
    "colors.primary.500",
    "colors.state.synced",
    "colors.domain.ndvi_high",
)
REQUIRED_SKILL_SECTIONS = ("## Scope", "## Required Inputs", "## Output Checklist", "## Do Not")
FORBIDDEN_IMPORT_PATTERNS = (
    r"\bsource:\s*github\b",
    r"\bsourceType:\s*github\b",
    r"\bimport\s+project\b",
    r"\bclone\s+",
)


def error(message: str) -> str:
    return f"SAHOOL-LINT: {message}"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def check_design_doc() -> list[str]:
    if not DESIGN_DOC.exists():
        return [error("SAHOOL_DESIGN.md is missing")]

    text = read_text(DESIGN_DOC)
    findings = [
        error(f"SAHOOL_DESIGN.md must reference `{reference}`")
        for reference in REQUIRED_DESIGN_REFERENCES
        if reference not in text
    ]
    if "Only these three starter skills are in scope" not in text:
        findings.append(error("SAHOOL_DESIGN.md must state the three-skill starter scope"))
    return findings


def parse_frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}

    frontmatter: dict[str, str] = {}
    for line in parts[1].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        frontmatter[key.strip()] = value.strip()
    return frontmatter


def check_skill_file(path: Path, expected_name: str) -> list[str]:
    text = read_text(path)
    findings: list[str] = []
    frontmatter = parse_frontmatter(text)

    if frontmatter.get("name") != expected_name:
        findings.append(error(f"{path.relative_to(REPO_ROOT)} must declare name `{expected_name}`"))
    if not frontmatter.get("description"):
        findings.append(error(f"{path.relative_to(REPO_ROOT)} must include a description"))

    for section in REQUIRED_SKILL_SECTIONS:
        if section not in text:
            findings.append(error(f"{path.relative_to(REPO_ROOT)} missing section `{section}`"))

    for pattern in FORBIDDEN_IMPORT_PATTERNS:
        if re.search(pattern, text, flags=re.IGNORECASE):
            findings.append(error(f"{path.relative_to(REPO_ROOT)} contains forbidden import pattern `{pattern}`"))

    if "SAHOOL_DESIGN.md" not in text:
        findings.append(error(f"{path.relative_to(REPO_ROOT)} must reference SAHOOL_DESIGN.md"))

    return findings


def check_starter_skills() -> list[str]:
    if not SKILLS_DIR.exists():
        return [error(".claude/skills/sahool-starter is missing")]

    actual_files = sorted(path.name for path in SKILLS_DIR.glob("*.md"))
    expected_files = sorted(EXPECTED_SKILLS)
    if actual_files != expected_files:
        return [error(f"starter skills must be exactly {expected_files}; found {actual_files}")]

    findings: list[str] = []
    for filename, expected_name in EXPECTED_SKILLS.items():
        findings.extend(check_skill_file(SKILLS_DIR / filename, expected_name))
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
