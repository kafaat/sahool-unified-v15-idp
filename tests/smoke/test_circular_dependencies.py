"""
Circular dependency detection tests for the agriculture-ai-knowledge-base branch.
Imports modules in different orders to surface hidden circular import chains.
"""

from __future__ import annotations

import importlib
import sys
from typing import List

import pytest


def _fresh_import(module_name: str):
    """Remove module and all sub-modules from cache, then import fresh."""
    to_remove = [k for k in list(sys.modules) if k == module_name or k.startswith(f"{module_name}.")]
    for mod in to_remove:
        sys.modules.pop(mod, None)
    return importlib.import_module(module_name)


def _import_chain(modules: list[str]):
    """Import a chain of modules in order; fail on circular import."""
    for mod_name in modules:
        try:
            _fresh_import(mod_name)
        except ImportError as exc:
            if "circular" in str(exc).lower():
                pytest.fail(f"Circular import detected at {mod_name}: {exc}")
            pytest.skip(f"Missing dependency for {mod_name}: {exc}")


@pytest.mark.smoke
class TestCircularDependencyChains:
    """Test import chains that are most likely to trigger circular imports."""

    def test_knowledge_models_then_validators(self):
        """models → validators should not be circular."""
        _import_chain(
            [
                "shared.ai.knowledge.models",
                "shared.ai.knowledge.validators",
            ]
        )

    def test_knowledge_models_then_persistence(self):
        """models → persistence should not be circular."""
        _import_chain(
            [
                "shared.ai.knowledge.models",
                "shared.ai.knowledge.persistence",
            ]
        )

    def test_knowledge_persistence_then_models(self):
        """persistence → models (reverse) should not be circular."""
        _import_chain(
            [
                "shared.ai.knowledge.persistence",
                "shared.ai.knowledge.models",
            ]
        )

    def test_knowledge_collections_then_vector_store(self):
        """collections → vector_store_integration should not be circular."""
        _import_chain(
            [
                "shared.ai.knowledge.collections",
                "shared.ai.knowledge.vector_store_integration",
            ]
        )

    def test_corrective_retrieval_then_agri_provider(self):
        """corrective_retrieval → agri_provider should not be circular."""
        _import_chain(
            [
                "shared.ai.knowledge.corrective_retrieval",
                "shared.ai.ultrarag.providers.agri_provider",
            ]
        )

    def test_ultrarag_pipeline_then_mcp_bridge(self):
        """ultrarag.pipeline → mcp_rag_bridge should not be circular."""
        _import_chain(
            [
                "shared.ai.ultrarag.pipeline",
                "shared.ai.mcp_rag_bridge",
            ]
        )

    def test_mcp_bridge_then_ultrarag_pipeline(self):
        """mcp_rag_bridge → ultrarag.pipeline (reverse) should not be circular."""
        _import_chain(
            [
                "shared.ai.mcp_rag_bridge",
                "shared.ai.ultrarag.pipeline",
            ]
        )

    def test_conversation_memory_then_pipeline(self):
        """conversation_memory → pipeline should not be circular."""
        _import_chain(
            [
                "shared.ai.ultrarag.conversation_memory",
                "shared.ai.ultrarag.pipeline",
            ]
        )

    def test_embeddings_then_unified_embeddings(self):
        """embeddings → unified_embeddings should not be circular."""
        _import_chain(
            [
                "shared.ai.embeddings",
                "shared.ai.unified_embeddings",
            ]
        )

    def test_unified_embeddings_then_embeddings(self):
        """unified_embeddings → embeddings (reverse) should not be circular."""
        _import_chain(
            [
                "shared.ai.unified_embeddings",
                "shared.ai.embeddings",
            ]
        )

    def test_training_orchestrator_then_model_training(self):
        """training_orchestrator → model_training should not be circular."""
        _import_chain(
            [
                "shared.ai.training_orchestrator",
                "shared.ai.model_training",
            ]
        )

    def test_feedback_pipeline_then_experience_learning(self):
        """feedback_training_pipeline → experience_learning should not be circular."""
        _import_chain(
            [
                "shared.ai.feedback_training_pipeline",
                "shared.ai.experience_learning",
            ]
        )

    def test_agent_orchestration_then_circuit_breaker(self):
        """agent_orchestration_bridge → circuit_breaker should not be circular."""
        _import_chain(
            [
                "shared.ai.agent_orchestration_bridge",
                "shared.ai.circuit_breaker",
            ]
        )

    def test_vision_bridge_then_crop_vision(self):
        """vision_knowledge_bridge → crop_vision should not be circular."""
        _import_chain(
            [
                "shared.ai.vision_knowledge_bridge",
                "shared.ai.crop_vision",
            ]
        )

    def test_full_knowledge_stack(self):
        """Full knowledge stack import chain should be clean."""
        _import_chain(
            [
                "shared.ai.knowledge.models",
                "shared.ai.knowledge.collections",
                "shared.ai.knowledge.agrovoc",
                "shared.ai.knowledge.validators",
                "shared.ai.knowledge.persistence",
                "shared.ai.knowledge.cache",
                "shared.ai.knowledge.metrics",
                "shared.ai.knowledge.quality_gate",
                "shared.ai.knowledge.serialization",
                "shared.ai.knowledge.versioning",
                "shared.ai.knowledge.vector_store_integration",
                "shared.ai.knowledge.corrective_retrieval",
                "shared.ai.knowledge.freshness_monitor",
                "shared.ai.knowledge.graph_builder",
            ]
        )

    def test_full_bridge_stack(self):
        """All bridge modules import without circular dependencies."""
        _import_chain(
            [
                "shared.ai.knowledge_service_bridge",
                "shared.ai.vision_knowledge_bridge",
                "shared.ai.agent_orchestration_bridge",
                "shared.ai.mcp_rag_bridge",
                "shared.ai.feedback_training_pipeline",
            ]
        )

    def test_reverse_bridge_stack(self):
        """Bridge modules in reverse order should also be clean."""
        _import_chain(
            [
                "shared.ai.feedback_training_pipeline",
                "shared.ai.mcp_rag_bridge",
                "shared.ai.agent_orchestration_bridge",
                "shared.ai.vision_knowledge_bridge",
                "shared.ai.knowledge_service_bridge",
            ]
        )

    def test_pivot_management_chain(self):
        """pivot_management modules should not be circular."""
        _import_chain(
            [
                "shared.pivot_management.geometry",
                "shared.pivot_management.vri_converter",
                "shared.pivot_management",
            ]
        )

    def test_cross_domain_chain(self):
        """Cross-domain chain: events → knowledge → bridge should be clean."""
        _import_chain(
            [
                "shared.events.subjects",
                "shared.ai.knowledge.models",
                "shared.ai.knowledge.collections",
                "shared.ai.knowledge_service_bridge",
            ]
        )
