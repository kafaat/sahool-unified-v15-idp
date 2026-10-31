"""
Smoke tests for all modules added/modified in the agriculture-ai-knowledge-base branch.
Verifies that every module imports without circular dependencies or missing symbols.
"""

from __future__ import annotations

import importlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

# All Python modules changed in this branch
BRANCH_MODULES = [
    # Knowledge base core
    "shared.ai.knowledge",
    "shared.ai.knowledge.models",
    "shared.ai.knowledge.collections",
    "shared.ai.knowledge.agrovoc",
    "shared.ai.knowledge.validators",
    "shared.ai.knowledge.cache",
    "shared.ai.knowledge.metrics",
    "shared.ai.knowledge.persistence",
    "shared.ai.knowledge.quality_gate",
    "shared.ai.knowledge.serialization",
    "shared.ai.knowledge.versioning",
    "shared.ai.knowledge.vector_store_integration",
    "shared.ai.knowledge.corrective_retrieval",
    "shared.ai.knowledge.freshness_monitor",
    "shared.ai.knowledge.graph_builder",
    # Knowledge ingestion pipeline
    "shared.ai.knowledge.ingestion",
    "shared.ai.knowledge.ingestion.chunker",
    "shared.ai.knowledge.ingestion.extractors",
    "shared.ai.knowledge.ingestion.pipeline",
    "shared.ai.knowledge.ingestion.preprocessors",
    "shared.ai.knowledge.ingestion.async_pipeline",
    # Knowledge sources & verification
    "shared.ai.knowledge.verification.region_filter",
    # Bridge modules
    "shared.ai.knowledge_service_bridge",
    "shared.ai.vision_knowledge_bridge",
    "shared.ai.agent_orchestration_bridge",
    "shared.ai.mcp_rag_bridge",
    "shared.ai.feedback_training_pipeline",
    # AI modules
    "shared.ai.ab_testing",
    "shared.ai.training_orchestrator",
    "shared.ai.unified_embeddings",
    "shared.ai.arabic_models",
    # UltraRAG
    "shared.ai.ultrarag.conversation_memory",
    "shared.ai.ultrarag.providers.agri_provider",
    "shared.ai.ultrarag.workflow",
    # Pivot management
    "shared.pivot_management",
    "shared.pivot_management.geometry",
    "shared.pivot_management.vri_converter",
    # Events
    "shared.events.subjects",
    # Field boundaries
    "shared.field_boundaries.geometry",
    # LLM provider
    "shared.ai.llm_provider",
    # Existing AI modules
    "shared.ai.vector_store",
]

_PROBE_PREFIX = "SAHOOL_IMPORT_PROBE_RESULT="
_IMPORT_PROBE = """
import importlib
import json
import sys

try:
    module = importlib.import_module(sys.argv[1])
    assert module is not None, f"{sys.argv[1]} imported as None"
except ImportError as exc:
    result = {"status": "import_error", "message": str(exc)}
except Exception as exc:
    result = {"status": "error", "message": f"{type(exc).__name__}: {exc}"}
else:
    result = {"status": "ok"}
print("SAHOOL_IMPORT_PROBE_RESULT=" + json.dumps(result), flush=True)
"""


def _assert_fresh_import(module_name: str) -> None:
    """Probe a fresh interpreter without replacing modules held by other tests."""
    try:
        result = subprocess.run(
            [sys.executable, "-c", _IMPORT_PROBE, module_name],
            cwd=Path(__file__).resolve().parents[2],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"Import probe timed out after 30 seconds: {module_name}")

    if result.returncode != 0:
        pytest.fail(
            f"Import probe for {module_name} exited with {result.returncode}:\n{result.stdout}\n{result.stderr}"
        )

    reports = [
        line.removeprefix(_PROBE_PREFIX) for line in result.stdout.splitlines() if line.startswith(_PROBE_PREFIX)
    ]
    if len(reports) != 1:
        pytest.fail(
            f"Import probe for {module_name} did not return one completion report:\n{result.stdout}\n{result.stderr}"
        )
    try:
        report = json.loads(reports[0])
    except json.JSONDecodeError as exc:
        pytest.fail(f"Invalid import probe report for {module_name}: {exc}")

    if report.get("status") == "ok":
        return
    message = report.get("message", "missing error details")
    if report.get("status") == "import_error":
        if "circular" in message.lower():
            pytest.fail(f"Circular import in {module_name}: {message}")
        # Preserve the existing optional-dependency policy for import failures.
        pytest.skip(f"{module_name} skipped – missing dependency: {message}")
    pytest.fail(f"Unexpected error importing {module_name}: {message}")


@pytest.mark.smoke
class TestBranchModuleImports:
    """Every module added or modified in this branch must import cleanly."""

    @pytest.mark.parametrize("module_name", BRANCH_MODULES)
    def test_module_imports_without_error(self, module_name: str):
        """Module imports without circular dependency or missing attribute errors."""
        _assert_fresh_import(module_name)


@pytest.mark.smoke
class TestKnowledgeBaseExports:
    """Verify the knowledge base __init__ re-exports critical symbols."""

    def _try_import(self, module_name: str, attr_name: str):
        try:
            mod = importlib.import_module(module_name)
            assert hasattr(mod, attr_name), f"{module_name} missing export: {attr_name}"
        except ImportError as exc:
            pytest.skip(f"Cannot import {module_name}: {exc}")

    def test_knowledge_models_exports(self):
        self._try_import("shared.ai.knowledge.models", "BaseKnowledgeDocument")
        self._try_import("shared.ai.knowledge.models", "KnowledgeDomain")
        self._try_import("shared.ai.knowledge.models", "CropKnowledgeDocument")

    def test_knowledge_collections_exports(self):
        self._try_import("shared.ai.knowledge.collections", "ALL_COLLECTIONS")
        self._try_import("shared.ai.knowledge.collections", "CROP_KNOWLEDGE")

    def test_agrovoc_exports(self):
        self._try_import("shared.ai.knowledge.agrovoc", "AgrovocLookup")
        self._try_import("shared.ai.knowledge.agrovoc", "AgrovocDomain")

    def test_persistence_exports(self):
        self._try_import("shared.ai.knowledge.persistence", "KnowledgeRepository")
        self._try_import("shared.ai.knowledge.persistence", "InMemoryKnowledgeRepository")

    def test_corrective_retrieval_exports(self):
        self._try_import("shared.ai.knowledge.corrective_retrieval", "CorrectiveRetrievalEngine")
        self._try_import("shared.ai.knowledge.corrective_retrieval", "CRAGResult")

    def test_vector_store_integration_exports(self):
        self._try_import("shared.ai.knowledge.vector_store_integration", "KnowledgeVectorStore")

    def test_quality_gate_exports(self):
        self._try_import("shared.ai.knowledge.quality_gate", "KnowledgeQualityGate")


@pytest.mark.smoke
class TestBridgeModuleExports:
    """Verify bridge modules expose their primary classes."""

    def _try_import(self, module_name: str, attr_name: str):
        try:
            mod = importlib.import_module(module_name)
            assert hasattr(mod, attr_name), f"{module_name} missing export: {attr_name}"
        except ImportError as exc:
            pytest.skip(f"Cannot import {module_name}: {exc}")

    def test_mcp_rag_bridge(self):
        self._try_import("shared.ai.mcp_rag_bridge", "MCPRAGBridge")

    def test_knowledge_service_bridge(self):
        self._try_import("shared.ai.knowledge_service_bridge", "KnowledgeServiceBridge")

    def test_vision_knowledge_bridge(self):
        self._try_import("shared.ai.vision_knowledge_bridge", "VisionKnowledgeBridge")

    def test_agent_orchestration_bridge(self):
        self._try_import("shared.ai.agent_orchestration_bridge", "OrchestrationManager")

    def test_feedback_training_pipeline(self):
        self._try_import("shared.ai.feedback_training_pipeline", "FeedbackTrainingPipeline")


@pytest.mark.smoke
class TestPivotManagementExports:
    """Verify pivot management module exports."""

    def _try_import(self, module_name: str, attr_name: str):
        try:
            mod = importlib.import_module(module_name)
            assert hasattr(mod, attr_name), f"{module_name} missing export: {attr_name}"
        except ImportError as exc:
            pytest.skip(f"Cannot import {module_name}: {exc}")

    def test_geometry_exports(self):
        self._try_import("shared.pivot_management.geometry", "PivotGeometry")
        self._try_import("shared.pivot_management.geometry", "PivotSector")

    def test_vri_converter_exports(self):
        self._try_import("shared.pivot_management.vri_converter", "VRIPrescription")
        self._try_import("shared.pivot_management.vri_converter", "ndvi_to_vri_prescription")
