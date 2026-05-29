# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Manifest ↔ Code Validators - مدقّقات تطابق البيانات الشارحة مع الكود
======================================================================
A manifest is only useful if it tracks the real module. These validators
ensure every manifest:

  1. Points at an importable Python module
  2. Lists ``depends_on`` entries that themselves resolve

Run by pytest in ``tests/unit/test_knowledge_layer.py``.
"""

from __future__ import annotations

import importlib

from shared.knowledge_layer.manifest import ModuleManifest


def _try_import(module_path: str) -> bool:
    try:
        importlib.import_module(module_path)
        return True
    except ImportError:
        return False


def validate_manifest_against_module(manifest: ModuleManifest) -> list[str]:
    """
    Return a list of human-readable errors. Empty list = manifest is consistent.

    Allows ``depends_on`` entries that point to non-shared modules (e.g.
    ``packages.sahool-eo``, ``apps.services.*``) — we only verify modules
    under the ``shared.*`` namespace, because those are what this repo
    actually owns. External dependencies are documented but not import-checked.
    """
    errors: list[str] = []

    if not _try_import(manifest.module_path):
        errors.append(f"module_path not importable: {manifest.module_path!r}")

    for dep in manifest.depends_on:
        if not dep.startswith("shared."):
            continue
        if not _try_import(dep):
            errors.append(f"depends_on not importable: {dep!r}")

    return errors


__all__ = ["validate_manifest_against_module"]
