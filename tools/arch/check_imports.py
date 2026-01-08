#!/usr/bin/env python3
"""
SAHOOL Architecture Import Checker
Validates that domain boundaries are not violated through imports.

Usage:
    python -m tools.arch.check_imports [--verbose] [--fix-suggestions]

Exit codes:
    0 - All checks passed
    1 - Architecture violations found
"""

from __future__ import annotations

import argparse
import ast
import sys
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

# Domain definitions
DOMAINS = {
    "kernel_domain": {
        "allowed_imports": ["shared"],
        "forbidden_imports": ["field_suite", "advisor"],
    },
    "field_suite": {
        "allowed_imports": ["shared"],
        "forbidden_imports": ["kernel_domain", "advisor"],
    },
    "advisor": {
        "allowed_imports": ["shared"],
        "forbidden_imports": ["kernel_domain", "field_suite"],
    },
    "legacy": {
        "allowed_imports": ["kernel_domain", "field_suite", "advisor", "shared"],
        "forbidden_imports": [],
    },
}


@dataclass
class ImportViolation:
    """Represents an architecture import violation"""

    file_path: Path
    line_number: int
    importing_domain: str
    imported_module: str
    forbidden_domain: str

    def __str__(self) -> str:
        return (
            f"{self.file_path}:{self.line_number}: "
            f"'{self.importing_domain}' cannot import from '{self.forbidden_domain}' "
            f"(imported: {self.imported_module})"
        )


class ImportVisitor(ast.NodeVisitor):
    """AST visitor to extract import statements"""

    def __init__(self):
        self.imports: list[tuple[int, str]] = []

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append((node.lineno, alias.name))
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.append((node.lineno, node.module))
        self.generic_visit(node)


def get_domain_from_path(file_path: Path) -> str | None:
    """Extract domain name from file path"""
    parts = file_path.parts
    for domain in DOMAINS:
        if domain in parts:
            return domain
    return None


def get_imported_domain(module_name: str) -> str | None:
    """Extract domain from import module name"""
    first_part = module_name.split(".")[0]
    if first_part in DOMAINS:
        return first_part
    return None


def check_file(file_path: Path) -> Iterator[ImportViolation]:
    """Check a single file for import violations"""
    importing_domain = get_domain_from_path(file_path)
    if not importing_domain:
        return

    domain_rules = DOMAINS.get(importing_domain)
    if not domain_rules:
        return

    try:
        content = file_path.read_text(encoding="utf-8")
        tree = ast.parse(content)
    except (SyntaxError, UnicodeDecodeError) as e:
        print(f"Warning: Could not parse {file_path}: {e}", file=sys.stderr)
        return

    visitor = ImportVisitor()
    visitor.visit(tree)

    for line_number, module_name in visitor.imports:
        imported_domain = get_imported_domain(module_name)
        if imported_domain and imported_domain in domain_rules["forbidden_imports"]:
            yield ImportViolation(
                file_path=file_path,
                line_number=line_number,
                importing_domain=importing_domain,
                imported_module=module_name,
                forbidden_domain=imported_domain,
            )


def find_python_files(root: Path) -> Iterator[Path]:
    """Find all Python files in domain directories"""
    for domain in DOMAINS:
        domain_path = root / domain
        if domain_path.exists():
            yield from domain_path.rglob("*.py")


def check_architecture(root: Path, verbose: bool = False) -> list[ImportViolation]:
    """Check all files for architecture violations"""
    violations = []

    for file_path in find_python_files(root):
        if verbose:
            print(f"Checking {file_path}...", file=sys.stderr)

        file_violations = list(check_file(file_path))
        violations.extend(file_violations)

    return violations


def print_suggestions(violations: list[ImportViolation]) -> None:
    """Print suggestions for fixing violations"""
    print("\n=== Fix Suggestions ===\n")

    for violation in violations:
        print(f"File: {violation.file_path}:{violation.line_number}")
        print(f"  Problem: {violation.importing_domain} imports from {violation.forbidden_domain}")
        print(f"  Import: {violation.imported_module}")
        print("  Solutions:")
        print("    1. Move shared logic to 'shared/' package")
        print("    2. Use contracts (shared/contracts/) for data exchange")
        print("    3. Pass data through application layer instead of direct import")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description="Check for architecture import violations")
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show verbose output",
    )
    parser.add_argument(
        "--fix-suggestions",
        action="store_true",
        help="Show suggestions for fixing violations",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Root directory to check (default: current directory)",
    )

    args = parser.parse_args()

    print("=" * 60)
    print("SAHOOL Architecture Import Checker")
    print("=" * 60)
    print()

    violations = check_architecture(args.root, verbose=args.verbose)

    if violations:
        print(f"❌ Found {len(violations)} architecture violation(s):\n")
        for violation in violations:
            print(f"  • {violation}")

        if args.fix_suggestions:
            print_suggestions(violations)

        print("\nRun with --fix-suggestions for remediation advice.")
        return 1
    else:
        print("✅ No architecture violations found!")
        print(f"   Checked domains: {', '.join(DOMAINS.keys())}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
