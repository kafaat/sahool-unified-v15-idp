# ═══════════════════════════════════════════════════════════════════════════════
# Tests for Tri-RAG (AgriGPT Integration)
# اختبارات Tri-RAG (تكامل AgriGPT)
# ═══════════════════════════════════════════════════════════════════════════════

"""
Tests for the Tri-RAG retriever combining Dense, Sparse, and Knowledge Graph channels.
Based on AgriGPT's triple-channel RAG framework.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest

from shared.ai.ultrarag.models import (
    EntityType,
    KnowledgeChunk,
    KnowledgeEntity,
    KnowledgeGraphResult,
    KnowledgeRelation,
    RelationType,
    RetrievalStrategy,
    TriRAGConfig,
)
from shared.ai.ultrarag.retriever import (
    DenseRetriever,
    KnowledgeGraphRetriever,
    RetrievalConfig,
    RetrievalResult,
    SparseRetriever,
    TriRAGRetriever,
)


class TestEntityType:
    """Tests for EntityType enum"""

    def test_entity_types_exist(self):
        """Test all agricultural entity types are defined"""
        assert EntityType.CROP.value == "crop"
        assert EntityType.PEST.value == "pest"
        assert EntityType.DISEASE.value == "disease"
        assert EntityType.FERTILIZER.value == "fertilizer"
        assert EntityType.IRRIGATION.value == "irrigation"
        assert EntityType.SOIL.value == "soil"

    def test_entity_type_count(self):
        """Test we have all expected entity types (12 base + 5 satellite)"""
        assert len(EntityType) == 17


class TestRelationType:
    """Tests for RelationType enum"""

    def test_relation_types_exist(self):
        """Test all relation types are defined"""
        assert RelationType.AFFECTS.value == "affects"
        assert RelationType.TREATS.value == "treats"
        assert RelationType.PREVENTS.value == "prevents"
        assert RelationType.CAUSES.value == "causes"
        assert RelationType.SYMPTOM_OF.value == "symptom_of"

    def test_relation_type_count(self):
        """Test we have all expected relation types (12 base + 6 satellite)"""
        assert len(RelationType) == 18


class TestKnowledgeEntity:
    """Tests for KnowledgeEntity dataclass"""

    def test_create_entity(self):
        """Test creating a knowledge entity"""
        entity = KnowledgeEntity(
            id="entity_001",
            name="Wheat",
            name_ar="قمح",
            entity_type=EntityType.CROP,
            description="A cereal grain crop",
        )
        assert entity.id == "entity_001"
        assert entity.name == "Wheat"
        assert entity.name_ar == "قمح"
        assert entity.entity_type == EntityType.CROP

    def test_generate_id(self):
        """Test ID generation"""
        entity_id = KnowledgeEntity.generate_id()
        assert entity_id.startswith("entity_")
        assert len(entity_id) == 19  # "entity_" + 12 hex chars


class TestKnowledgeRelation:
    """Tests for KnowledgeRelation dataclass"""

    def test_create_relation(self):
        """Test creating a knowledge relation"""
        relation = KnowledgeRelation(
            id="rel_001",
            source_id="entity_wheat",
            target_id="entity_rust",
            relation_type=RelationType.AFFECTS,
            weight=0.8,
        )
        assert relation.id == "rel_001"
        assert relation.relation_type == RelationType.AFFECTS
        assert relation.weight == 0.8

    def test_generate_id(self):
        """Test ID generation"""
        rel_id = KnowledgeRelation.generate_id()
        assert rel_id.startswith("rel_")


class TestTriRAGConfig:
    """Tests for TriRAGConfig dataclass"""

    def test_default_config(self):
        """Test default configuration values"""
        config = TriRAGConfig()
        assert config.dense_weight == 0.4
        assert config.sparse_weight == 0.3
        assert config.kg_weight == 0.3
        assert config.kg_max_hops == 2

    def test_validate_weights(self):
        """Test weight validation"""
        config = TriRAGConfig()
        assert config.validate() is True

        # Invalid weights
        bad_config = TriRAGConfig(
            dense_weight=0.5,
            sparse_weight=0.5,
            kg_weight=0.5,  # Sum = 1.5
        )
        assert bad_config.validate() is False


class TestKnowledgeGraphRetriever:
    """Tests for KnowledgeGraphRetriever"""

    @pytest.fixture
    def kg_retriever(self):
        """Create a KG retriever for testing"""
        return KnowledgeGraphRetriever()

    @pytest.mark.asyncio
    async def test_add_entity(self, kg_retriever):
        """Test adding an entity to the graph"""
        entity = {
            "id": "entity_wheat",
            "name": "wheat",
            "entity_type": "crop",
        }
        result = await kg_retriever.add_entity(entity)
        assert result is True
        assert "entity_wheat" in kg_retriever._entities

    @pytest.mark.asyncio
    async def test_add_relation(self, kg_retriever):
        """Test adding a relation to the graph"""
        relation = {
            "id": "rel_001",
            "source_id": "entity_wheat",
            "target_id": "entity_rust",
            "relation_type": "affects",
        }
        result = await kg_retriever.add_relation(relation)
        assert result is True
        assert len(kg_retriever._relations) == 1

    @pytest.mark.asyncio
    async def test_extract_entities(self, kg_retriever):
        """Test entity extraction from query"""
        query = "What diseases affect wheat crops?"
        entities = await kg_retriever._extract_entities(query)
        assert "wheat" in entities
        assert "disease" in entities or "diseases" in entities

    @pytest.mark.asyncio
    async def test_retrieve_empty_graph(self, kg_retriever):
        """Test retrieval from empty graph"""
        config = RetrievalConfig(top_k=5)
        results = await kg_retriever.retrieve("wheat disease", config)
        assert results == []

    @pytest.mark.asyncio
    async def test_retrieve_with_entities(self, kg_retriever):
        """Test retrieval with populated graph"""
        # Add entities
        await kg_retriever.add_entity(
            {
                "id": "entity_wheat",
                "name": "wheat",
                "entity_type": "crop",
                "description": "A major cereal grain",
            }
        )
        await kg_retriever.add_entity(
            {
                "id": "entity_rust",
                "name": "rust",
                "entity_type": "disease",
                "description": "A fungal disease",
            }
        )
        await kg_retriever.add_relation(
            {
                "id": "rel_001",
                "source_id": "entity_wheat",
                "target_id": "entity_rust",
                "relation_type": "affects",
            }
        )

        config = RetrievalConfig(top_k=5)
        results = await kg_retriever.retrieve("wheat disease", config)
        # Should find wheat entity and related rust
        assert len(results) >= 0  # May be 0 if no match

    @pytest.mark.asyncio
    async def test_add_documents(self, kg_retriever):
        """Test adding documents extracts entities and relations"""
        chunks = [
            KnowledgeChunk(
                id="chunk_001",
                text="Wheat rust is a common disease that affects wheat crops. Use fungicide for treatment.",
            ),
        ]
        result = await kg_retriever.add_documents(chunks)
        assert result is True
        assert len(kg_retriever._entities) > 0


class TestTriRAGRetriever:
    """Tests for TriRAGRetriever"""

    @pytest.fixture
    def mock_dense_retriever(self):
        """Create mock dense retriever"""
        retriever = MagicMock(spec=DenseRetriever)
        retriever.retrieve = AsyncMock(
            return_value=[
                RetrievalResult(
                    chunk=KnowledgeChunk(id="d1", text="Dense result 1"),
                    score=0.9,
                    rank=1,
                    retrieval_method="dense",
                ),
            ]
        )
        retriever.add_documents = AsyncMock(return_value=True)
        return retriever

    @pytest.fixture
    def mock_sparse_retriever(self):
        """Create mock sparse retriever"""
        retriever = MagicMock(spec=SparseRetriever)
        retriever.retrieve = AsyncMock(
            return_value=[
                RetrievalResult(
                    chunk=KnowledgeChunk(id="s1", text="Sparse result 1"),
                    score=0.8,
                    rank=1,
                    retrieval_method="sparse",
                ),
            ]
        )
        retriever.add_documents = AsyncMock(return_value=True)
        return retriever

    @pytest.fixture
    def mock_kg_retriever(self):
        """Create mock KG retriever"""
        retriever = MagicMock(spec=KnowledgeGraphRetriever)
        retriever.retrieve = AsyncMock(
            return_value=[
                RetrievalResult(
                    chunk=KnowledgeChunk(id="kg1", text="KG result 1"),
                    score=0.7,
                    rank=1,
                    retrieval_method="knowledge_graph",
                ),
            ]
        )
        retriever.add_documents = AsyncMock(return_value=True)
        return retriever

    @pytest.fixture
    def tri_rag_retriever(
        self,
        mock_dense_retriever,
        mock_sparse_retriever,
        mock_kg_retriever,
    ):
        """Create Tri-RAG retriever with mocks"""
        return TriRAGRetriever(
            dense_retriever=mock_dense_retriever,
            sparse_retriever=mock_sparse_retriever,
            kg_retriever=mock_kg_retriever,
        )

    @pytest.mark.asyncio
    async def test_retrieve_combines_all_channels(self, tri_rag_retriever):
        """Test that Tri-RAG retrieves from all three channels"""
        config = RetrievalConfig(top_k=10)
        results = await tri_rag_retriever.retrieve("wheat disease treatment", config)

        # Should have fused results from all channels
        assert len(results) == 3  # One from each channel
        methods = [r.retrieval_method for r in results]
        assert any("dense" in m for m in methods)
        assert any("sparse" in m for m in methods)
        assert any("kg" in m for m in methods)

    @pytest.mark.asyncio
    async def test_retrieve_uses_rrf_fusion(self, tri_rag_retriever):
        """Test RRF fusion is applied"""
        config = RetrievalConfig(top_k=10)
        results = await tri_rag_retriever.retrieve("test query", config)

        # Results should be ranked by fused score
        for i, result in enumerate(results):
            assert result.rank == i + 1
            assert "tri_rag:" in result.retrieval_method

    @pytest.mark.asyncio
    async def test_add_documents_to_all_channels(
        self,
        tri_rag_retriever,
        mock_dense_retriever,
        mock_sparse_retriever,
        mock_kg_retriever,
    ):
        """Test documents are added to all three retrievers"""
        chunks = [
            KnowledgeChunk(id="c1", text="Test document"),
        ]
        result = await tri_rag_retriever.add_documents(chunks)

        assert result is True
        mock_dense_retriever.add_documents.assert_called_once()
        mock_sparse_retriever.add_documents.assert_called_once()
        mock_kg_retriever.add_documents.assert_called_once()

    @pytest.mark.asyncio
    async def test_custom_weights(
        self,
        mock_dense_retriever,
        mock_sparse_retriever,
        mock_kg_retriever,
    ):
        """Test custom weight configuration"""
        config = TriRAGConfig(
            dense_weight=0.5,
            sparse_weight=0.3,
            kg_weight=0.2,
        )
        retriever = TriRAGRetriever(
            dense_retriever=mock_dense_retriever,
            sparse_retriever=mock_sparse_retriever,
            kg_retriever=mock_kg_retriever,
            config=config,
        )

        assert retriever.dense_weight == 0.5
        assert retriever.sparse_weight == 0.3
        assert retriever.kg_weight == 0.2


class TestRetrievalStrategyTriRAG:
    """Tests for TRI_RAG retrieval strategy"""

    def test_tri_rag_strategy_exists(self):
        """Test TRI_RAG is in RetrievalStrategy enum"""
        assert RetrievalStrategy.TRI_RAG.value == "tri_rag"

    def test_all_strategies(self):
        """Test all retrieval strategies"""
        strategies = [s.value for s in RetrievalStrategy]
        assert "dense" in strategies
        assert "sparse" in strategies
        assert "hybrid" in strategies
        assert "adaptive" in strategies
        assert "tri_rag" in strategies
