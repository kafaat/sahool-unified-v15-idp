"""
Tests for Knowledge Graph Service
اختبارات خدمة الرسم البياني للمعرفة
"""

import asyncio
import os
import sys

import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from services import KnowledgeGraphService

from models import Crop, Disease, RelationshipType, Treatment


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
        assert "crop:rice" in graph_service.entities

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
        assert "disease:blast" in graph_service.entities

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
        disease = await graph_service.get_disease("powdery_mildew")
        assert disease is not None
        assert disease.id == "powdery_mildew"

    @pytest.mark.asyncio
    async def test_get_related_entities(self, graph_service):
        """Test getting related entities"""
        # Get crops affected by powdery mildew (disease -> AFFECTS -> crop)
        related = await graph_service.get_related_entities(
            entity_type="disease",
            entity_id="powdery_mildew",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert len(related) > 0
        # Verify we got crops back (wheat is affected by powdery mildew)
        assert any("wheat" in str(r.get("id", "")) or "Wheat" in str(r.get("name_en", "")) for r in related)

    @pytest.mark.asyncio
    async def test_find_shortest_path(self, graph_service):
        """Test finding shortest path between entities"""
        # Path goes from treatment -> disease (treatment:sulfur --treats--> disease:powdery_mildew)
        path = await graph_service.find_shortest_path(
            source_type="treatment",
            source_id="sulfur",
            target_type="disease",
            target_id="powdery_mildew",
        )
        assert path is not None
        assert len(path.path) >= 2
        assert path.path[0] == "treatment:sulfur"
        assert path.path[-1] == "disease:powdery_mildew"

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
