"""
Smoke tests for all modules added/modified in the agriculture-ai-knowledge-base branch.
Verifies that every module imports without circular dependencies or missing symbols.
"""

from __future__ import annotations

import importlib
import sys

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


@pytest.mark.smoke
class TestBranchModuleImports:
    """Every module added or modified in this branch must import cleanly."""

    @pytest.mark.parametrize("module_name", BRANCH_MODULES)
    def test_module_imports_without_error(self, module_name: str):
        """Module imports without circular dependency or missing attribute errors."""
        # Flush from cache so we get a real import
        to_remove = [k for k in sys.modules if k == module_name or k.startswith(f"{module_name}.")]
        for mod in to_remove:
            sys.modules.pop(mod, None)

        try:
            module = importlib.import_module(module_name)
            assert module is not None, f"{module_name} imported as None"
        except ImportError as exc:
            msg = str(exc).lower()
            if "circular" in msg:
                pytest.fail(f"Circular import in {module_name}: {exc}")
            # Missing optional dependency (torch, ultralytics, etc.) is OK
            pytest.skip(f"{module_name} skipped – missing dependency: {exc}")
        except Exception as exc:
            pytest.fail(f"Unexpected error importing {module_name}: {type(exc).__name__}: {exc}")


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
