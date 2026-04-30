#!/usr/bin/env python3
"""Simple SAHOOL starter linter.

Checks the intentionally small starter surface:
- SAHOOL_DESIGN.md exists and references token sources.
- Exactly three starter skills exist.
- Starter skills include frontmatter, required sections, and no external imports.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import yaml


_REPO_ROOT = Path(__file__).resolve().parent.parent
_DESIGN_DOC = _REPO_ROOT / "SAHOOL_DESIGN.md"
_LOWCODE_DOC = _REPO_ROOT / "docs" / "LOW_CODE_POC.md"
_LOWCODE_SPRINT_PLAN = _REPO_ROOT / "docs" / "LOW_CODE_BUILDER_SPRINT_PLAN.md"
_SCHEMA_REGISTRY = _REPO_ROOT / "schema-registry" / "registry.json"
_SKILLS_DIR = _REPO_ROOT / ".claude" / "skills" / "sahool-starter"
_GENERATED_THEME = _REPO_ROOT / "apps" / "mobile" / "lib" / "core" / "theme" / "generated" / "sahool_token_theme.dart"
_GENERATED_FORM = (
    _REPO_ROOT / "apps" / "mobile" / "lib" / "features" / "lowcode" / "generated" / "analyzesatellitegeometry_form.dart"
)
_GENERATED_VIEW = _REPO_ROOT / "apps" / "mobile" / "lib" / "features" / "lowcode" / "generated" / "listfields_card_list.dart"
_GENERATED_FORM_TEST = (
    _REPO_ROOT / "apps" / "mobile" / "test" / "features" / "lowcode" / "generated" / "analyzesatellitegeometry_form_test.dart"
)
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
_REQUIRED_LOWCODE_DOC_REFERENCES = (
    "governance/design/design-tokens.yaml",
    "api/services/vegetation-analysis-service.openapi.yaml",
    "Tenant Context",
    "RBAC",
    "does not perform API calls",
)
_REQUIRED_SPRINT_PLAN_REFERENCES = (
    "Week 1: Widget Tests",
    "Week 2: Schema Registry Adapter",
    "Weeks 3-4: GET View Generation",
    "Unified Response",
)
_REQUIRED_GENERATED_FORM_REFERENCES = (
    "final String tenantId;",
    "final Set<String> permissions;",
    "requiredPermission",
    "does not perform API calls",
)
_REQUIRED_GENERATED_VIEW_REFERENCES = (
    "final String tenantId;",
    "final Set<String> permissions;",
    "requiredPermission",
    "does not perform API calls",
)
_REQUIRED_GENERATED_TEST_REFERENCES = (
    "Tenant Context missing shows guard message",
    "Permission missing shows guard message",
    "Required field empty shows validation error",
    "Valid input calls onSubmit with payload",
)
_FORBIDDEN_IMPORT_PATTERNS = (
    (r"\bsource:\s*github\b", "GitHub-sourced skill imports"),
    (r"\bsourceType:\s*github\b", "GitHub source metadata"),
    (r"\bimport\s+project\b", "whole-project imports"),
    (r"\bclone\s+", "clone-based imports"),
)
_FRONTMATTER_PATTERN = re.compile(r"\A---\n(?P<body>.*?)\n---\n", re.DOTALL)


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

    match = _FRONTMATTER_PATTERN.match(text)
    if not match:
        return {}

    frontmatter = yaml.safe_load(match.group("body")) or {}
    if not isinstance(frontmatter, dict):
        return {}
    return {str(key): str(value) for key, value in frontmatter.items()}


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


def check_lowcode_poc() -> list[str]:
    findings: list[str] = []

    if not _LOWCODE_DOC.exists():
        findings.append(create_lint_error("docs/LOW_CODE_POC.md is missing"))
    else:
        text = _LOWCODE_DOC.read_text(encoding="utf-8")
        findings.extend(
            create_lint_error(f"docs/LOW_CODE_POC.md must reference `{reference}`")
            for reference in _REQUIRED_LOWCODE_DOC_REFERENCES
            if reference not in text
        )

    if not _GENERATED_THEME.exists():
        findings.append(create_lint_error("generated Flutter token theme is missing"))
    else:
        theme_text = _GENERATED_THEME.read_text(encoding="utf-8")
        if "SahoolGeneratedTheme" not in theme_text:
            findings.append(create_lint_error("generated Flutter token theme must expose SahoolGeneratedTheme"))
        if "governance/design/design-tokens.yaml" not in theme_text:
            findings.append(create_lint_error("generated Flutter token theme must identify its token source"))

    if not _GENERATED_FORM.exists():
        findings.append(create_lint_error("generated OpenAPI Flutter form PoC is missing"))
    else:
        form_text = _GENERATED_FORM.read_text(encoding="utf-8")
        findings.extend(
            create_lint_error(f"generated OpenAPI Flutter form must include `{reference}`")
            for reference in _REQUIRED_GENERATED_FORM_REFERENCES
            if reference not in form_text
        )
        if "package:dio/" in form_text or "package:http/" in form_text:
            findings.append(create_lint_error("generated OpenAPI Flutter form must not perform direct HTTP calls"))

    if not _LOWCODE_SPRINT_PLAN.exists():
        findings.append(create_lint_error("docs/LOW_CODE_BUILDER_SPRINT_PLAN.md is missing"))
    else:
        sprint_text = _LOWCODE_SPRINT_PLAN.read_text(encoding="utf-8")
        findings.extend(
            create_lint_error(f"docs/LOW_CODE_BUILDER_SPRINT_PLAN.md must reference `{reference}`")
            for reference in _REQUIRED_SPRINT_PLAN_REFERENCES
            if reference not in sprint_text
        )

    if not _SCHEMA_REGISTRY.exists():
        findings.append(create_lint_error("schema-registry/registry.json is missing"))
    else:
        registry_check = subprocess.run(
            [sys.executable, str(_REPO_ROOT / "scripts" / "lowcode_schema_registry.py"), "validate"],
            capture_output=True,
            check=False,
            text=True,
        )
        if registry_check.returncode != 0:
            output = registry_check.stdout or registry_check.stderr
            findings.extend(
                create_lint_error(f"schema registry invalid: {line}")
                for line in output.splitlines()
                if line.strip()
            )

    if not _GENERATED_VIEW.exists():
        findings.append(create_lint_error("generated OpenAPI Flutter view PoC is missing"))
    else:
        view_text = _GENERATED_VIEW.read_text(encoding="utf-8")
        findings.extend(
            create_lint_error(f"generated OpenAPI Flutter view must include `{reference}`")
            for reference in _REQUIRED_GENERATED_VIEW_REFERENCES
            if reference not in view_text
        )
        if "package:dio/" in view_text or "package:http/" in view_text:
            findings.append(create_lint_error("generated OpenAPI Flutter view must not perform direct HTTP calls"))

    if not _GENERATED_FORM_TEST.exists():
        findings.append(create_lint_error("generated OpenAPI Flutter form widget test is missing"))
    else:
        test_text = _GENERATED_FORM_TEST.read_text(encoding="utf-8")
        findings.extend(
            create_lint_error(f"generated OpenAPI Flutter form test must include `{reference}`")
            for reference in _REQUIRED_GENERATED_TEST_REFERENCES
            if reference not in test_text
        )

    return findings


def main() -> int:
    findings = [*check_design_doc(), *check_starter_skills(), *check_lowcode_poc()]
    if findings:
        print("\n".join(findings), file=sys.stderr)
        return 1

    print("SAHOOL-LINT: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
