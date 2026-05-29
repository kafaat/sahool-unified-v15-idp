#!/usr/bin/env python3
# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Decision-Surface Neutrality Guard - حارس حياد سطوح القرار
============================================================
Fails CI if location-specific data leaks into location-neutral surfaces:

    shared/digital_twin/
    shared/crop_cards/
    shared/process_models/
    shared/knowledge_layer/
    shared/workspace/

Two passes:
  1. Raw-text regex sweep for known farm/district/cultivar identifiers.
  2. AST sweep of string constants in .py files (resists trivial obfuscation).

Exit codes:
  0 – clean
  1 – violations found

Run locally:
    python scripts/check_decision_neutrality.py
"""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]

# Patterns that must NEVER appear in neutral-core code or YAML cards.
# Each entry: (compiled regex, human reason).
LEAK_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (
        re.compile(r"\b(al[_-]?jawf|aljawf|al jawf|الجوف)\b", re.IGNORECASE),
        "specific governorate (Al-Jawf)",
    ),
    (
        re.compile(r"\b(tihama|تهامة)\b", re.IGNORECASE),
        "specific region (Tihama)",
    ),
    (
        re.compile(r"\b(sakha[_-]?\d+)\b", re.IGNORECASE),
        "specific cultivar (Sakha-N)",
    ),
    (
        re.compile(r"\bfarm[_-]?id\s*[:=]\s*[\"'][A-Za-z0-9_-]+[\"']", re.IGNORECASE),
        "concrete farm_id literal",
    ),
]

TARGET_ROOTS: list[str] = [
    "shared/digital_twin",
    "shared/crop_cards",
    "shared/process_models",
    "shared/knowledge_layer",
    "shared/workspace",
]


# Self-references that must NEVER trigger the guard. The guard itself
# describes the leak patterns; we must not detect ourselves.
SELF_REFERENCE_MARKERS = (
    "LEAK_PATTERNS",
    "neutrality",
    "check_decision_neutrality",
)


def _line_self_referential(line: str) -> bool:
    return any(marker in line for marker in SELF_REFERENCE_MARKERS)


def _scan_text_lines(text: str) -> list[tuple[str, int]]:
    """Return list of (reason, line_no) leaks found in text."""
    leaks: list[tuple[str, int]] = []
    for ln, line in enumerate(text.splitlines(), 1):
        if _line_self_referential(line):
            continue
        for pat, reason in LEAK_PATTERNS:
            if pat.search(line):
                leaks.append((reason, ln))
    return leaks


def _scan_ast_constants(text: str, path: Path) -> list[tuple[str, int]]:
    """Walk an AST and check string constants. Resists case-mangling tricks."""
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError:
        return []

    leaks: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            # Skip the guard's own pattern strings.
            if any(marker in node.value for marker in SELF_REFERENCE_MARKERS):
                continue
            for pat, reason in LEAK_PATTERNS:
                if pat.search(node.value):
                    leaks.append((f"AST: {reason}", getattr(node, "lineno", 0)))
    return leaks


def scan_file(path: Path) -> list[tuple[Path, str, int]]:
    """Return [(path, reason, line_no), ...] of violations for one file."""
    try:
        text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []

    out: list[tuple[Path, str, int]] = []
    for reason, ln in _scan_text_lines(text):
        out.append((path, reason, ln))
    if path.suffix == ".py":
        for reason, ln in _scan_ast_constants(text, path):
            out.append((path, reason, ln))
    return out


def main() -> int:
    violations: list[tuple[Path, str, int]] = []
    for root in TARGET_ROOTS:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_dir():
                continue
            if path.suffix not in {".py", ".yaml", ".yml"}:
                continue
            if "__pycache__" in path.parts:
                continue
            violations.extend(scan_file(path))

    if not violations:
        print("PASS: neutrality guard — no location-specific data in neutral surfaces.")
        return 0

    print(f"FAIL: neutrality guard — {len(violations)} violation(s):")
    for path, reason, ln in violations:
        rel = path.relative_to(REPO_ROOT)
        print(f"  {rel}:{ln}  {reason}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
