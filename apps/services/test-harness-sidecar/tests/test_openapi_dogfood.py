"""Schemathesis dogfooding — the sidecar's own openapi.yaml is loaded
through the SAME tooling the sidecar exists to enable.

If openapi.yaml itself is malformed (missing required fields,
unresolvable $refs, type mismatches), Schemathesis throws and the
test fails — catches contract drift before any deploy.

Does NOT spin up a live server. We just verify the spec parses
through the production-grade loader.
"""

from __future__ import annotations

from pathlib import Path

import pytest


pytestmark = pytest.mark.unit


def test_openapi_yaml_loads_through_schemathesis():
    schemathesis = pytest.importorskip("schemathesis")
    spec_path = Path(__file__).resolve().parent.parent / "openapi.yaml"
    assert spec_path.exists(), f"sidecar openapi.yaml not found at {spec_path}"

    schema = schemathesis.openapi.from_path(str(spec_path))
    ops = list(schema.get_all_operations())
    assert len(ops) > 0, "Schemathesis loaded the spec but found no operations"


def test_openapi_yaml_passes_strict_validator():
    """openapi-spec-validator is stricter than schemathesis on OpenAPI 3.1."""
    yaml = pytest.importorskip("yaml")
    pytest.importorskip("openapi_spec_validator")
    from openapi_spec_validator import validate

    spec_path = Path(__file__).resolve().parent.parent / "openapi.yaml"
    spec = yaml.safe_load(spec_path.read_text("utf-8"))
    # Raises if invalid
    validate(spec)


def test_contract_version_field_present():
    """The ``x-contract-version`` field is the framework's compat anchor."""
    yaml = pytest.importorskip("yaml")

    spec_path = Path(__file__).resolve().parent.parent / "openapi.yaml"
    spec = yaml.safe_load(spec_path.read_text("utf-8"))
    assert spec["info"].get("x-contract-version"), (
        "openapi.yaml::info.x-contract-version is missing — "
        "the framework reads this for compatibility checks via /version"
    )
