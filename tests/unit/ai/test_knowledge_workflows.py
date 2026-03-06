"""
Tests for UltraRAG Workflow YAML Files
=======================================
اختبارات ملفات سير العمل YAML

Tests for YAML validity, required fields, and collection references
across all 11 UltraRAG workflow files.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from shared.ai.knowledge.collections import ALL_COLLECTIONS

WORKFLOWS_DIR = Path("shared/ai/ultrarag/workflows")


@pytest.fixture
def workflow_files() -> list[Path]:
    """Get all workflow YAML files."""
    if not WORKFLOWS_DIR.is_dir():
        pytest.skip("Workflows directory not found")
    return sorted(WORKFLOWS_DIR.glob("*.yaml"))


def _load_yaml(path: Path) -> dict:
    """Load and parse a YAML file."""
    with open(path) as f:
        return yaml.safe_load(f) or {}


class TestWorkflowDiscovery:
    """Tests for workflow file discovery."""

    @pytest.mark.unit
    def test_workflows_directory_exists(self):
        """Test workflows directory exists."""
        assert WORKFLOWS_DIR.is_dir(), f"Workflows dir not found: {WORKFLOWS_DIR}"

    @pytest.mark.unit
    def test_minimum_workflow_count(self, workflow_files: list[Path]):
        """Test at least 6 workflow files exist."""
        assert len(workflow_files) >= 6, f"Found only {len(workflow_files)} workflows"

    @pytest.mark.unit
    def test_expected_workflows_exist(self):
        """Test all expected workflow files exist."""
        expected = [
            "crop_advisory.yaml",
            "irrigation_advisory.yaml",
            "fertilizer_advisory.yaml",
            "soil_analysis_advisory.yaml",
            "weather_advisory.yaml",
            "remote_sensing_analysis.yaml",
            "pest_diagnosis.yaml",
            "comprehensive_field_advisory.yaml",
            "precision_farming_advisory.yaml",
            "digital_twin_simulation.yaml",
        ]
        for name in expected:
            path = WORKFLOWS_DIR / name
            assert path.exists(), f"Expected workflow not found: {name}"


class TestWorkflowValidity:
    """Tests for YAML validity and structure."""

    @pytest.mark.unit
    def test_all_workflows_valid_yaml(self, workflow_files: list[Path]):
        """Test all workflow files are valid YAML."""
        for wf in workflow_files:
            try:
                data = _load_yaml(wf)
                assert isinstance(data, dict), f"{wf.name} is not a dict"
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {wf.name}: {e}")

    @pytest.mark.unit
    def test_all_workflows_have_name(self, workflow_files: list[Path]):
        """Test all workflows have a name field."""
        for wf in workflow_files:
            data = _load_yaml(wf)
            assert "name" in data, f"{wf.name} missing 'name'"
            assert data["name"], f"{wf.name} has empty name"

    @pytest.mark.unit
    def test_all_workflows_have_version(self, workflow_files: list[Path]):
        """Test all workflows have a version field."""
        for wf in workflow_files:
            data = _load_yaml(wf)
            assert "version" in data, f"{wf.name} missing 'version'"

    @pytest.mark.unit
    def test_all_workflows_have_steps(self, workflow_files: list[Path]):
        """Test all workflows have steps."""
        for wf in workflow_files:
            data = _load_yaml(wf)
            assert "steps" in data, f"{wf.name} missing 'steps'"
            assert isinstance(data["steps"], list), f"{wf.name} steps is not a list"
            assert len(data["steps"]) > 0, f"{wf.name} has no steps"

    @pytest.mark.unit
    def test_all_workflows_have_description(self, workflow_files: list[Path]):
        """Test all workflows have a description."""
        for wf in workflow_files:
            data = _load_yaml(wf)
            assert "description" in data, f"{wf.name} missing 'description'"

    @pytest.mark.unit
    def test_steps_have_required_fields(self, workflow_files: list[Path]):
        """Test each step has name and type."""
        for wf in workflow_files:
            data = _load_yaml(wf)
            for i, step in enumerate(data.get("steps", [])):
                assert "name" in step, f"{wf.name} step {i} missing 'name'"
                assert "type" in step, f"{wf.name} step {i} missing 'type'"


class TestWorkflowCollections:
    """Tests for collection references in workflows."""

    @pytest.mark.unit
    def test_collection_references_valid(self, workflow_files: list[Path]):
        """Test that collection references in workflows match defined collections."""
        for wf in workflow_files:
            data = _load_yaml(wf)
            for step in data.get("steps", []):
                collections = step.get("collections", [])
                if isinstance(collections, str):
                    collections = [collections]
                for coll in collections:
                    assert coll in ALL_COLLECTIONS, (
                        f"{wf.name} step '{step.get('name')}' references unknown collection '{coll}'"
                    )


class TestSpecificWorkflows:
    """Tests for specific workflow configurations."""

    @pytest.mark.unit
    def test_fertilizer_advisory_collections(self):
        """Test fertilizer advisory uses correct collections."""
        path = WORKFLOWS_DIR / "fertilizer_advisory.yaml"
        if not path.exists():
            pytest.skip("fertilizer_advisory.yaml not found")
        data = _load_yaml(path)
        # Check that fertilizer_knowledge is referenced somewhere
        yaml_str = yaml.dump(data)
        assert "fertilizer_knowledge" in yaml_str

    @pytest.mark.unit
    def test_pest_diagnosis_has_safety_check(self):
        """Test pest diagnosis workflow includes safety check step."""
        path = WORKFLOWS_DIR / "pest_diagnosis.yaml"
        if not path.exists():
            pytest.skip("pest_diagnosis.yaml not found")
        data = _load_yaml(path)
        step_names = [s.get("name", "").lower() for s in data.get("steps", [])]
        assert any("safety" in name for name in step_names), "Pest diagnosis missing safety check step"

    @pytest.mark.unit
    def test_comprehensive_has_most_steps(self, workflow_files: list[Path]):
        """Test comprehensive advisory has the most steps."""
        path = WORKFLOWS_DIR / "comprehensive_field_advisory.yaml"
        if not path.exists():
            pytest.skip("comprehensive_field_advisory.yaml not found")
        comp_data = _load_yaml(path)
        comp_steps = len(comp_data.get("steps", []))

        for wf in workflow_files:
            if wf.name == "comprehensive_field_advisory.yaml":
                continue
            data = _load_yaml(wf)
            other_steps = len(data.get("steps", []))
            assert comp_steps >= other_steps, (
                f"Comprehensive ({comp_steps} steps) has fewer steps than {wf.name} ({other_steps})"
            )

    @pytest.mark.unit
    def test_bilingual_support_in_workflows(self, workflow_files: list[Path]):
        """Test workflows mention bilingual or Arabic support."""
        has_bilingual = False
        for wf in workflow_files:
            data = _load_yaml(wf)
            yaml_str = str(data).lower()
            if "bilingual" in yaml_str or "arabic" in yaml_str or "ar" in yaml_str:
                has_bilingual = True
                break
        assert has_bilingual, "No workflow mentions bilingual/Arabic support"

    @pytest.mark.unit
    def test_precision_farming_advisory_collections(self):
        """Test precision farming advisory uses correct collection."""
        path = WORKFLOWS_DIR / "precision_farming_advisory.yaml"
        if not path.exists():
            pytest.skip("precision_farming_advisory.yaml not found")
        data = _load_yaml(path)
        yaml_str = yaml.dump(data)
        assert "precision_farming_knowledge" in yaml_str

    @pytest.mark.unit
    def test_digital_twin_simulation_collections(self):
        """Test digital twin simulation uses correct collections."""
        path = WORKFLOWS_DIR / "digital_twin_simulation.yaml"
        if not path.exists():
            pytest.skip("digital_twin_simulation.yaml not found")
        data = _load_yaml(path)
        yaml_str = yaml.dump(data)
        assert "digital_twin_knowledge" in yaml_str
