#!/usr/bin/env python3
"""
SAHOOL ENV Scanner
Scans codebase for os.getenv() calls to find all used environment variables.
"""

from __future__ import annotations

import re
from pathlib import Path

# Patterns to find ENV usage
ENV_PATTERNS = [
    re.compile(r"os\.getenv\([\"']([A-Z0-9_]+)[\"']"),
    re.compile(r"os\.environ\.get\([\"']([A-Z0-9_]+)[\"']"),
    re.compile(r"os\.environ\[[\"']([A-Z0-9_]+)[\"']\]"),
    re.compile(r"environ\.get\([\"']([A-Z0-9_]+)[\"']"),
    re.compile(r"settings\.([A-Z][A-Z0-9_]+)"),
]

ROOT = Path(__file__).resolve().parents[2]

# Directories to skip
SKIP_DIRS = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "build",
    "dist",
}


def scan_file(filepath: Path) -> set[str]:
    """Scan a single file for ENV variable usage."""
    found = set()

    try:
        text = filepath.read_text(encoding="utf-8", errors="ignore")
        for pattern in ENV_PATTERNS:
            for match in pattern.findall(text):
                found.add(match)
    except Exception:
        pass

    return found


def main() -> None:
    """Main scanner function."""
    found: set[str] = set()

    # Scan Python files
    for py_file in ROOT.rglob("*.py"):
        if any(skip in py_file.parts for skip in SKIP_DIRS):
            continue
        found.update(scan_file(py_file))

    # Scan TypeScript/JavaScript files
    for ext in ["*.ts", "*.tsx", "*.js", "*.jsx"]:
        for js_file in ROOT.rglob(ext):
            if any(skip in js_file.parts for skip in SKIP_DIRS):
                continue
            found.update(scan_file(js_file))

    # Output sorted list
    for env_var in sorted(found):
        print(env_var)


if __name__ == "__main__":
    main()
