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

Security note: ``importlib.import_module`` is fed a STRING from the manifest.
Even though the manifest comes from a YAML file in this repo, we sanitise the
module path against a strict allowlist (``shared.*`` plus dotted segments
matching ``[a-z0-9_]+``) before passing it through ``import_module``, so the
function can never be coaxed into loading attacker-controlled paths.
"""

from __future__ import annotations

import importlib
import re

from shared.knowledge_layer.manifest import ModuleManifest


_SAFE_SEGMENT = re.compile(r"^[a-z0-9_]+$")
_ALLOWED_TOP_LEVEL = frozenset({"shared"})


def _is_safe_module_path(module_path: str) -> bool:
    """Strict allowlist check before any dynamic import."""
    segments = module_path.split(".")
    if len(segments) < 2:
        return False
    if segments[0] not in _ALLOWED_TOP_LEVEL:
        return False
    return all(_SAFE_SEGMENT.match(s) for s in segments)


def _try_import(module_path: str) -> bool:
    if not _is_safe_module_path(module_path):
        return False
    try:
        importlib.import_module(module_path)  # nosec B403 — input vetted by _is_safe_module_path
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
