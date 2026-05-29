# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Manifest Loader - محمّل البيانات الشارحة
==========================================
Loads ModuleManifest YAML files from ``manifests/`` with a path-traversal guard.
"""

from __future__ import annotations

import re
from pathlib import Path

import yaml

from shared.knowledge_layer.manifest import ModuleManifest


_MANIFESTS_ROOT = Path(__file__).resolve().parent / "manifests"

# A module_path translates to a path segment by replacing dots with slashes.
# We strip the "shared." prefix so manifests/{package}/{module}.yaml works.
_VALID_SEGMENT = re.compile(r"^[a-z0-9_]+$")


def _module_path_to_yaml_path(module_path: str) -> Path:
    segments = module_path.split(".")
    if segments and segments[0] == "shared":
        segments = segments[1:]
    for seg in segments:
        if not _VALID_SEGMENT.match(seg):
            raise ValueError(f"invalid module path segment {seg!r} in {module_path!r}")
    return _MANIFESTS_ROOT.joinpath(*segments).with_suffix(".yaml")


def load_manifest(module_path: str) -> ModuleManifest:
    """Load and validate one manifest by its target module path."""
    path = _module_path_to_yaml_path(module_path).resolve()
    if not path.is_relative_to(_MANIFESTS_ROOT.resolve()):
        raise ValueError(f"path escapes manifests root: {module_path!r}")
    if not path.exists():
        raise FileNotFoundError(f"no manifest for {module_path!r}")
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return ModuleManifest.model_validate(data)


def all_manifests() -> list[ModuleManifest]:
    """Load every manifest under manifests/ recursively. Skips files starting with '_'."""
    if not _MANIFESTS_ROOT.exists():
        return []
    out: list[ModuleManifest] = []
    for path in sorted(_MANIFESTS_ROOT.rglob("*.yaml")):
        if path.name.startswith("_"):
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        out.append(ModuleManifest.model_validate(data))
    return out


def business_meaning(module_path: str, lang: str = "ar") -> str:
    """Return the business_meaning_{lang} for a module. Raises on unknown lang."""
    if lang not in ("ar", "en"):
        raise ValueError(f"lang must be 'ar' or 'en', got {lang!r}")
    manifest = load_manifest(module_path)
    return manifest.business_meaning_ar if lang == "ar" else manifest.business_meaning_en


__all__ = [
    "load_manifest",
    "all_manifests",
    "business_meaning",
]
