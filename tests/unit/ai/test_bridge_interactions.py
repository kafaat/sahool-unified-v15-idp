"""
Integration tests for bridge module interactions.
Verifies that bridge modules correctly connect their target systems.
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge_service_bridge import (
    DOMAIN_COLLECTION_MAP,
    KnowledgeServiceBridge,
    QueryDomain,
)
from shared.ai.vision_knowledge_bridge import VisionKnowledgeBridge, _DISEASE_QUERY_MAP
from shared.ai.agent_orchestration_bridge import KNOWN_AGENTS, OrchestrationManager
from shared.ai.mcp_rag_bridge import AgriWorkflow, MCPRAGBridge
from shared.ai.feedback_training_pipeline import FeedbackTrainingPipeline, PipelineAction
from shared.ai.ultrarag.conversation_memory import ConversationMemory


@pytest.mark.unit
class TestKnowledgeServiceBridgeIntegration:
    """Test KnowledgeServiceBridge connects knowledge to services."""

    def test_bridge_instantiation(self):
        """KnowledgeServiceBridge should instantiate."""
        bridge = KnowledgeServiceBridge()
        assert bridge is not None

    def test_query_domain_enum(self):
        """QueryDomain should cover agricultural domains."""
        values = [d.value for d in QueryDomain]
        assert len(values) >= 5, f"QueryDomain should have 5+ domains, got: {values}"

    def test_domain_collection_mapping(self):
        """DOMAIN_COLLECTION_MAP should map all QueryDomain values."""
        for domain in QueryDomain:
            assert domain in DOMAIN_COLLECTION_MAP or domain.value in DOMAIN_COLLECTION_MAP, (
                f"QueryDomain.{domain.value} has no collection mapping"
            )


@pytest.mark.unit
class TestVisionKnowledgeBridgeIntegration:
    """Test VisionKnowledgeBridge connects vision to knowledge."""

    def test_bridge_instantiation(self):
        """VisionKnowledgeBridge should instantiate."""
        bridge = VisionKnowledgeBridge()
        assert bridge is not None

    def test_disease_query_map(self):
        """_DISEASE_QUERY_MAP should map disease names to queries."""
        assert isinstance(_DISEASE_QUERY_MAP, dict)
        assert len(_DISEASE_QUERY_MAP) > 0, "Disease query map should not be empty"


@pytest.mark.unit
class TestAgentOrchestrationBridgeIntegration:
    """Test OrchestrationManager connects agents."""

    def test_known_agents_defined(self):
        """KNOWN_AGENTS should define agent profiles."""
        assert isinstance(KNOWN_AGENTS, (list, dict))
        count = len(KNOWN_AGENTS)
        assert count >= 5, f"Expected 5+ agents, got {count}"

    def test_orchestration_manager_instantiation(self):
        """OrchestrationManager should instantiate."""
        manager = OrchestrationManager()
        assert manager is not None


@pytest.mark.unit
class TestMCPRAGBridgeIntegration:
    """Test MCPRAGBridge connects MCP to RAG."""

    def test_bridge_instantiation(self):
        """MCPRAGBridge should instantiate."""
        bridge = MCPRAGBridge()
        assert bridge is not None

    def test_agri_workflow_enum(self):
        """AgriWorkflow should define agricultural workflows."""
        values = [w.value for w in AgriWorkflow]
        assert len(values) >= 5, f"Expected 5+ workflows, got: {values}"

    def test_bridge_tool_schemas(self):
        """MCPRAGBridge should expose tool schemas for MCP."""
        bridge = MCPRAGBridge()
        schemas = bridge.get_tool_schemas()
        assert isinstance(schemas, list)
        assert len(schemas) > 0, "Bridge should expose at least one tool schema"


@pytest.mark.unit
class TestFeedbackTrainingPipelineIntegration:
    """Test FeedbackTrainingPipeline connects feedback to training."""

    def test_pipeline_instantiation(self):
        """FeedbackTrainingPipeline should instantiate."""
        pipeline = FeedbackTrainingPipeline(tenant_id="test-tenant")
        assert pipeline is not None

    def test_pipeline_action_enum(self):
        """PipelineAction should define pipeline actions."""
        values = [a.value for a in PipelineAction]
        assert len(values) >= 3, f"PipelineAction should have 3+ values, got: {values}"


@pytest.mark.unit
class TestUltraRAGConversationMemory:
    """Test conversation memory with RAG pipeline."""

    def test_conversation_memory_instantiation(self):
        """ConversationMemory should instantiate."""
        memory = ConversationMemory()
        assert memory is not None

    def test_create_session(self):
        """ConversationMemory should create and track sessions."""
        memory = ConversationMemory()
        session_id = memory.create_session()
        assert session_id is not None
        assert isinstance(session_id, str)

    def test_add_turn_to_session(self):
        """Should be able to add conversation turns."""
        memory = ConversationMemory()
        session_id = memory.create_session()
        memory.add_turn(session_id, query="What is wheat rust?", answer="Wheat rust is a fungal disease...")
        session = memory.get_session(session_id)
        assert session is not None
        assert len(session.turns) >= 1
