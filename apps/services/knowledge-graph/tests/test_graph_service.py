"""
Tests for Knowledge Graph Service
اختبارات خدمة الرسم البياني للمعرفة
"""

import pytest
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from services import KnowledgeGraphService
from models import Crop, Disease, Treatment, RelationshipType


@pytest.mark.asyncio
class TestKnowledgeGraphService:
    """Test suite for KnowledgeGraphService"""

    @pytest.fixture
    async def graph_service(self):
        """Create a graph service instance for testing"""
        service = KnowledgeGraphService()
        await service.initialize()
        return service

    @pytest.mark.asyncio
    async def test_initialization(self, graph_service):
        """Test that graph service initializes correctly"""
        assert graph_service.graph is not None
        assert graph_service.graph.number_of_nodes() > 0
        assert graph_service.graph.number_of_edges() > 0

    @pytest.mark.asyncio
    async def test_add_crop(self, graph_service):
        """Test adding a crop to the graph"""
        crop = Crop(
            id="rice",
            name_en="Rice",
            name_ar="الأرز",
            growing_season="summer",
        )
        result = await graph_service.add_crop(crop)
        assert result is True
        assert f"crop:rice" in graph_service.entities

    @pytest.mark.asyncio
    async def test_add_disease(self, graph_service):
        """Test adding a disease to the graph"""
        disease = Disease(
            id="blast",
            name_en="Blast",
            name_ar="الانفجار",
            pathogen_type="fungal",
        )
        result = await graph_service.add_disease(disease)
        assert result is True
        assert f"disease:blast" in graph_service.entities

    @pytest.mark.asyncio
    async def test_get_crop(self, graph_service):
        """Test retrieving a crop"""
        crop = await graph_service.get_crop("wheat")
        assert crop is not None
        assert crop.id == "wheat"
        assert crop.name_en == "Wheat"

    @pytest.mark.asyncio
    async def test_get_disease(self, graph_service):
        """Test retrieving a disease"""
        disease = await graph_service.get_disease("powdery-mildew")
        assert disease is not None
        assert disease.id == "powdery-mildew"

    @pytest.mark.asyncio
    async def test_get_related_entities(self, graph_service):
        """Test getting related entities"""
        # Get crops affected by powdery mildew
        related = await graph_service.get_related_entities(
            entity_type="disease",
            entity_id="powdery-mildew",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert len(related) > 0
        # Verify we got crops back
        assert any("wheat" in str(r.get("id")) for r in related)

    @pytest.mark.asyncio
    async def test_find_shortest_path(self, graph_service):
        """Test finding shortest path between entities"""
        path = await graph_service.find_shortest_path(
            source_type="disease",
            source_id="powdery-mildew",
            target_type="treatment",
            target_id="sulfur-dust",
        )
        assert path is not None
        assert len(path.path) >= 2
        assert path.path[0] == "disease:powdery-mildew"
        assert path.path[-1] == "treatment:sulfur-dust"

    @pytest.mark.asyncio
    async def test_search_entities(self, graph_service):
        """Test searching for entities"""
        results = await graph_service.search_entities(
            query="wheat",
            limit=10,
        )
        assert len(results) > 0
        assert any("wheat" in str(r.get("name_en", "")).lower() for r in results)

    @pytest.mark.asyncio
    async def test_get_graph_stats(self, graph_service):
        """Test getting graph statistics"""
        stats = await graph_service.get_graph_stats()
        assert stats["total_nodes"] > 0
        assert stats["total_edges"] > 0
        assert stats["crops"] > 0
        assert stats["diseases"] > 0
        assert stats["treatments"] > 0

    @pytest.mark.asyncio
    async def test_health_check(self, graph_service):
        """Test health check"""
        health = await graph_service.health_check()
        assert health is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
