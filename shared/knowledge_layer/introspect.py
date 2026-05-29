# SPDX-License-Identifier: Proprietary
# Copyright (c) 2026 KAFAAT - SAHOOL Platform
"""
Introspection API - واجهة الاستكشاف
=====================================
Read-only query helpers over the manifests + decision chains. Pure Python;
no DB. Designed to be called from CLI scripts, services, or tests.
"""

from __future__ import annotations

from typing import Any

from shared.knowledge_layer.loader import all_manifests, load_manifest


def who_depends_on(module_path: str) -> list[str]:
    """
    Return manifest module_paths that list ``module_path`` in their depends_on.
    أسماء الوحدات التي تعتمد على ``module_path``.
    """
    return sorted(m.module_path for m in all_manifests() if module_path in m.depends_on)


def flow_of(observable_name: str) -> list[dict[str, str]]:
    """
    Trace the flow of one observable through the manifests:
    every module that consumes it as input or emits it as output, in order
    of discovery.

    Returns a list of {"module": str, "direction": "in"|"out"} entries.
    """
    flow: list[dict[str, str]] = []
    for m in all_manifests():
        for inp in m.inputs:
            if inp.name == observable_name or inp.kind == observable_name:
                flow.append({"module": m.module_path, "direction": "in"})
        for out in m.outputs:
            if out.name == observable_name or out.kind == observable_name:
                flow.append({"module": m.module_path, "direction": "out"})
    return flow


def describe_recommendation(recommendation: Any) -> dict[str, Any]:
    """
    Produce a human-readable explanation of a recommendation by combining its
    runtime decision_chain with the static manifests of each step's module.

    Accepts any object with a ``decision_chain`` attribute (typically
    ``IrrigationRecommendation``). Returns {} when no chain is attached.
    """
    chain = getattr(recommendation, "decision_chain", None)
    if chain is None:
        return {"summary": "no_decision_chain", "steps": []}

    steps_out: list[dict[str, Any]] = []
    for step in chain.steps:
        meaning_ar: str | None = None
        meaning_en: str | None = None
        # The step's name may match a module suffix (e.g. "field_lifecycle").
        # Try several common module roots without failing if none match.
        for prefix in ("shared.digital_twin.", "shared.process_models.", "shared.crop_cards."):
            try:
                m = load_manifest(prefix + step.name)
                meaning_ar = m.business_meaning_ar
                meaning_en = m.business_meaning_en
                break
            except (FileNotFoundError, ValueError):
                continue
        steps_out.append(
            {
                "name": step.name,
                "kind": step.kind,
                "gate_passed": step.gate_passed,
                "confidence_before": step.confidence_before,
                "confidence_after": step.confidence_after,
                "cost_estimate_ms": step.cost_estimate_ms,
                "business_meaning_ar": meaning_ar,
                "business_meaning_en": meaning_en,
            }
        )

    return {
        "workspace_key": chain.workspace_key,
        "total_cost_ms": chain.total_cost_ms(),
        "step_count": len(chain.steps),
        "steps": steps_out,
    }


def describe_feedback_loop() -> dict[str, list[str]]:
    """
    Return the closed feedback-loop wiring as a structured map of phases →
    modules participating in that phase. Useful for orientation/debug.
    """
    return {
        "analysis": [
            "shared.digital_twin.pipeline",
            "shared.digital_twin.assimilation",
            "packages.sahool-eo",
            "shared.satellite.sentinel_ndvi",
        ],
        "prescription": [
            "shared.digital_twin.decisions",
            "shared.digital_twin.field_lifecycle",
            "shared.digital_twin.evidence_class",
            "shared.digital_twin.pesticide_gate",
        ],
        "execution": [
            "apps.services.irrigation-smart",
            "apps.services.equipment-service",
            "apps.services.task-service",
        ],
        "outcome_collection": [
            "shared.harvest_quality",
            "shared.traceability",
            "apps.services.iot-service",
        ],
        "evaluation": [
            "shared.digital_twin.feedback_loop",
        ],
        "recalibration": [
            "shared.calibration",
        ],
    }


__all__ = [
    "who_depends_on",
    "flow_of",
    "describe_recommendation",
    "describe_feedback_loop",
]
