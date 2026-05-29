# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Manifest ↔ Code Validators - مدقّقات تطابق البيانات الشارحة مع الكود
======================================================================
A manifest is only useful if it tracks the real module. These validators
ensure every manifest:

  1. Points at an existing Python module on disk
  2. Lists ``depends_on`` entries that themselves resolve

Run by pytest in ``tests/unit/test_knowledge_layer.py``.

Security note: we deliberately use a **filesystem existence check** here
instead of ``importlib.import_module``. The validator is only proving that
the manifest's ``module_path`` points at a real file in the ``shared/`` tree
— it never needs to execute the module. Skipping the dynamic import removes
the entire code-execution surface that Semgrep / CodeQL flag for non-literal
``import_module`` calls.
"""

from __future__ import annotations

import re
from pathlib import Path

from shared.knowledge_layer.manifest import ModuleManifest


_SAFE_SEGMENT = re.compile(r"^[a-z0-9_]+$")
_ALLOWED_TOP_LEVEL = frozenset({"shared"})

# Repo root is two parents up: shared/knowledge_layer/validators.py → shared/ → repo
_REPO_ROOT = Path(__file__).resolve().parents[2]


def _is_safe_module_path(module_path: str) -> bool:
    """Strict allowlist check: top-level must be 'shared', every dotted segment must match [a-z0-9_]+."""
    segments = module_path.split(".")
    if len(segments) < 2:
        return False
    if segments[0] not in _ALLOWED_TOP_LEVEL:
        return False
    return all(_SAFE_SEGMENT.match(s) for s in segments)


def _module_exists_on_disk(module_path: str) -> bool:
    """
    Resolve ``shared.X.Y`` to a path under the repo and check that either
    ``shared/X/Y.py`` or ``shared/X/Y/__init__.py`` exists. No dynamic import
    is performed.
    """
    if not _is_safe_module_path(module_path):
        return False

    base = _REPO_ROOT.joinpath(*module_path.split(".")).resolve()
    # Defence in depth: ensure the resolved path stays under the repo root,
    # even though _is_safe_module_path already forbids path-traversal segments.
    if not base.is_relative_to(_REPO_ROOT):
        return False
    return base.with_suffix(".py").is_file() or (base / "__init__.py").is_file()


def validate_manifest_against_module(manifest: ModuleManifest) -> list[str]:
    """
    Return a list of human-readable errors. Empty list = manifest is consistent.

    Allows ``depends_on`` entries that point to non-shared modules (e.g.
    ``packages.sahool-eo``, ``apps.services.*``) — we only verify modules
    under the ``shared.*`` namespace, because those are what this repo
    actually owns. External dependencies are documented but not file-checked.
    """
    errors: list[str] = []

    if not _module_exists_on_disk(manifest.module_path):
        errors.append(f"module_path not importable: {manifest.module_path!r}")

    for dep in manifest.depends_on:
        if not dep.startswith("shared."):
            continue
        if not _module_exists_on_disk(dep):
            errors.append(f"depends_on not importable: {dep!r}")

    return errors


__all__ = ["validate_manifest_against_module"]
