# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Module Manifests + Registries - بيانات الوحدات والسجلّات
==========================================================
A ModuleManifest is a strict YAML-backed description of one Python module
in the Decision Kernel. It declares:

    purpose, business_meaning, decision_role, inputs, outputs, depends_on,
    governs_decisions, version

EngineRegistry classifies modules into 5 engine roles (spatial, operations,
decision, memory, connectivity) sourced from ``engines.yaml``.

SourceOfTruthRegistry maps observables → authoritative source + tie-breaker
sourced from ``sources_of_truth.yaml``. Resolves the "ERP vs combine vs
user-edits" conflict at the platform level.
"""

from __future__ import annotations

from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field


class DecisionRole(StrEnum):
    """The role a module plays in the Decision Kernel."""

    GUARD = "guard"  # Enforces invariants / gates
    ENGINE = "engine"  # Core computation
    ADAPTER = "adapter"  # Converts between forms / boundaries
    VIEW = "view"  # Presents a slice (e.g. farmer vs backend)
    GATE = "gate"  # Hard safety gate
    REGISTRY = "registry"  # Holds reference data or traces


class InputSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    kind: str  # e.g. "ec_dsm", "ndvi", "kg_ha"
    source_type: str  # e.g. "lab", "sensor", "satellite", "user"


class OutputSpec(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    kind: str
    consumed_by: list[str] = Field(default_factory=list)


class ModuleManifest(BaseModel):
    """A neutrality-locked description of one module."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    module_path: str  # e.g. "shared.digital_twin.field_lifecycle"
    purpose_ar: str = Field(min_length=1)
    purpose_en: str = Field(min_length=1)
    business_meaning_ar: str = Field(min_length=1)
    business_meaning_en: str = Field(min_length=1)
    decision_role: DecisionRole
    inputs: list[InputSpec] = Field(default_factory=list)
    outputs: list[OutputSpec] = Field(default_factory=list)
    depends_on: list[str] = Field(default_factory=list)
    governs_decisions: list[str] = Field(default_factory=list)
    version: str = Field(default="1.0.0")


# ---------------------------------------------------------------------------
# Engine registry (5 engines → modules)
# ---------------------------------------------------------------------------

_ENGINES_FILE = Path(__file__).resolve().parent / "engines.yaml"


class EngineRegistry:
    """In-memory registry mapping a module path to its engine role."""

    _cache: dict[str, str] | None = None

    @classmethod
    def _load(cls) -> dict[str, str]:
        if cls._cache is None:
            data = yaml.safe_load(_ENGINES_FILE.read_text(encoding="utf-8")) or {}
            mapping: dict[str, str] = {}
            for role, modules in (data.get("engines") or {}).items():
                for m in modules or []:
                    mapping[m] = role
            cls._cache = mapping
        return cls._cache

    @classmethod
    def role_of(cls, module_path: str) -> str | None:
        """Return the engine role for a module path, or None if unclassified."""
        return cls._load().get(module_path)

    @classmethod
    def modules_for(cls, role: str) -> list[str]:
        return sorted(m for m, r in cls._load().items() if r == role)

    @classmethod
    def known_roles(cls) -> list[str]:
        return sorted(set(cls._load().values()))


# ---------------------------------------------------------------------------
# Source-of-truth registry (observable → authoritative source)
# ---------------------------------------------------------------------------

_SOT_FILE = Path(__file__).resolve().parent / "sources_of_truth.yaml"


class SourceOfTruthRegistry:
    """In-memory registry resolving authority over each observable."""

    _cache: dict[str, dict[str, object]] | None = None

    @classmethod
    def _load(cls) -> dict[str, dict[str, object]]:
        if cls._cache is None:
            data = yaml.safe_load(_SOT_FILE.read_text(encoding="utf-8")) or {}
            cls._cache = data.get("observables") or {}
        return cls._cache

    @classmethod
    def authority_for(cls, observable: str) -> str | None:
        entry = cls._load().get(observable)
        if not entry:
            return None
        value = entry.get("authoritative_source")
        return value if isinstance(value, str) else None

    @classmethod
    def acceptable_sources(cls, observable: str) -> list[str]:
        entry = cls._load().get(observable) or {}
        value = entry.get("acceptable_sources") or []
        return [v for v in value if isinstance(v, str)]

    @classmethod
    def tie_breaker(cls, observable: str) -> str | None:
        entry = cls._load().get(observable) or {}
        value = entry.get("tie_breaker")
        return value if isinstance(value, str) else None

    @classmethod
    def all_observables(cls) -> list[str]:
        return sorted(cls._load().keys())


__all__ = [
    "DecisionRole",
    "InputSpec",
    "OutputSpec",
    "ModuleManifest",
    "EngineRegistry",
    "SourceOfTruthRegistry",
]
