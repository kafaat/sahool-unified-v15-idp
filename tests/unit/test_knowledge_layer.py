# SPDX-License-Identifier: Proprietary
"""Unit tests for shared.knowledge_layer."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from shared.knowledge_layer import (
    EngineRegistry,
    ModuleManifest,
    SourceOfTruthRegistry,
    all_manifests,
    business_meaning,
    describe_feedback_loop,
    flow_of,
    load_manifest,
    validate_manifest_against_module,
    who_depends_on,
)


pytestmark = pytest.mark.unit


# ── Manifest loading ────────────────────────────────────────────────────


def test_load_manifest_for_field_lifecycle() -> None:
    m = load_manifest("shared.digital_twin.field_lifecycle")
    assert isinstance(m, ModuleManifest)
    assert m.decision_role == "guard"
    assert m.business_meaning_ar
    assert m.business_meaning_en


def test_load_manifest_for_unknown_path_raises() -> None:
    with pytest.raises(FileNotFoundError):
        load_manifest("shared.digital_twin.does_not_exist")


def test_load_manifest_rejects_non_shared_root() -> None:
    """Loader is a shared.* loader; apps.* / packages.* paths must be refused."""
    with pytest.raises(ValueError, match="must start with 'shared.'"):
        load_manifest("apps.services.advisory-service")
    with pytest.raises(ValueError, match="must start with 'shared.'"):
        load_manifest("packages.sahool-eo")


def test_load_manifest_rejects_bare_shared() -> None:
    with pytest.raises(ValueError, match="needs a sub-module"):
        load_manifest("shared")


def test_manifest_extra_forbid_rejects_unknown_fields() -> None:
    """Mechanical neutrality: schema rejects undeclared keys."""
    with pytest.raises(ValidationError):
        ModuleManifest(
            module_path="x.y",
            purpose_ar="x",
            purpose_en="x",
            business_meaning_ar="x",
            business_meaning_en="x",
            decision_role="guard",
            uncategorised_field="leak",  # type: ignore[call-arg]
        )


def test_all_manifests_returns_non_empty() -> None:
    mans = all_manifests()
    assert len(mans) >= 8
    paths = {m.module_path for m in mans}
    assert "shared.digital_twin.field_lifecycle" in paths
    assert "shared.digital_twin.pesticide_gate" in paths


def test_all_manifests_have_non_empty_business_meaning_ar() -> None:
    """Decision Kernel invariant: every manifest must explain its agronomic 'why' in Arabic."""
    for m in all_manifests():
        assert m.business_meaning_ar.strip(), f"empty business_meaning_ar in {m.module_path}"


# ── business_meaning helper ──────────────────────────────────────────────


def test_business_meaning_arabic() -> None:
    text = business_meaning("shared.digital_twin.pesticide_gate", lang="ar")
    assert "السلامة" in text or "سلامة" in text


def test_business_meaning_english() -> None:
    text = business_meaning("shared.digital_twin.pesticide_gate", lang="en")
    assert "safety" in text.lower() or "phi" in text.lower()


def test_business_meaning_invalid_lang_raises() -> None:
    with pytest.raises(ValueError):
        business_meaning("shared.digital_twin.field_lifecycle", lang="fr")


# ── who_depends_on / flow_of ────────────────────────────────────────────


def test_who_depends_on_evidence_class_includes_uncertainty() -> None:
    """evidence_class manifest declares depends_on: [shared.process_models.uncertainty]."""
    deps_of_uncertainty = who_depends_on("shared.process_models.uncertainty")
    assert "shared.digital_twin.evidence_class" in deps_of_uncertainty


def test_who_depends_on_unknown_returns_empty() -> None:
    assert who_depends_on("nonexistent.module") == []


def test_flow_of_emits_modules_when_observable_present() -> None:
    flow = flow_of("decision_chain")
    assert isinstance(flow, list)


# ── Engine + SourceOfTruth registries ────────────────────────────────────


def test_engine_registry_classifies_known_modules() -> None:
    assert EngineRegistry.role_of("shared.digital_twin.feedback_loop") == "memory"
    assert EngineRegistry.role_of("shared.crop_cards") == "decision"
    assert EngineRegistry.role_of("shared.workspace") == "memory"


def test_engine_registry_unknown_module_returns_none() -> None:
    assert EngineRegistry.role_of("shared.never.exists") is None


def test_engine_registry_lists_all_known_roles() -> None:
    roles = EngineRegistry.known_roles()
    for required in ("spatial", "operations", "decision", "memory", "connectivity"):
        assert required in roles


def test_source_of_truth_for_yield_has_authority() -> None:
    auth = SourceOfTruthRegistry.authority_for("yield_kg_ha")
    assert auth is not None
    assert "harvest_record" in auth


def test_source_of_truth_for_soil_ec_governs_with_lab() -> None:
    auth = SourceOfTruthRegistry.authority_for("soil_ec_dsm")
    assert auth == "lab_analysis"


def test_source_of_truth_tie_breaker_present_for_key_observables() -> None:
    for obs in ("yield_kg_ha", "soil_ec_dsm", "irrigation_volume_mm"):
        assert SourceOfTruthRegistry.tie_breaker(obs) is not None


def test_source_of_truth_unknown_observable_returns_none() -> None:
    assert SourceOfTruthRegistry.authority_for("nothing_real") is None


# ── validators ───────────────────────────────────────────────────────────


def test_validate_manifest_against_real_module_returns_no_errors() -> None:
    m = load_manifest("shared.digital_twin.field_lifecycle")
    errors = validate_manifest_against_module(m)
    assert errors == []


def test_validate_manifest_against_fake_module_returns_errors() -> None:
    fake = ModuleManifest(
        module_path="shared.never.exists",
        purpose_ar="x",
        purpose_en="x",
        business_meaning_ar="x",
        business_meaning_en="x",
        decision_role="guard",
    )
    errors = validate_manifest_against_module(fake)
    assert any("not importable" in e for e in errors)


# ── describe_feedback_loop ──────────────────────────────────────────────


def test_describe_feedback_loop_lists_six_phases() -> None:
    loop = describe_feedback_loop()
    assert set(loop.keys()) == {
        "analysis",
        "prescription",
        "execution",
        "outcome_collection",
        "evaluation",
        "recalibration",
    }
    assert "shared.digital_twin.feedback_loop" in loop["evaluation"]
    assert "shared.calibration" in loop["recalibration"]
