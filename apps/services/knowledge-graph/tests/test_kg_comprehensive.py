"""
Comprehensive tests for Knowledge Graph Service
اختبارات شاملة لخدمة الرسم البياني للمعرفة

Covers: models, graph_service, entity_service, relationship_service, API endpoints
"""
import os
import sys

import pytest

# Add service src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from unittest.mock import AsyncMock, MagicMock, patch

from services import EntityService, KnowledgeGraphService, RelationshipService

from models import (
    Crop,
    Disease,
    GraphEdge,
    GraphNode,
    HealthCheckResponse,
    PathResponse,
    Relationship,
    RelationshipType,
    Treatment,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Model Tests
# ═══════════════════════════════════════════════════════════════════════════════
class TestModels:
    """Tests for Pydantic models in graph_models.py"""

    def test_crop_model_creation(self):
        """Test creating a Crop model with all fields."""
        crop = Crop(
            id="barley",
            name_en="Barley",
            name_ar="الشعير",
            description_en="A cereal grain",
            description_ar="حبوب",
            growing_season="winter",
            family="Poaceae",
            attributes={"water_req": "low"},
        )
        assert crop.id == "barley"
        assert crop.name_en == "Barley"
        assert crop.name_ar == "الشعير"
        assert crop.growing_season == "winter"
        assert crop.family == "Poaceae"
        assert crop.attributes == {"water_req": "low"}

    def test_crop_model_minimal(self):
        """Test creating a Crop with only required fields."""
        crop = Crop(id="test", name_en="Test", name_ar="تجربة")
        assert crop.id == "test"
        assert crop.description_en is None
        assert crop.growing_season is None
        assert crop.attributes == {}

    def test_disease_model_creation(self):
        """Test creating a Disease model with severity validation."""
        disease = Disease(
            id="rust",
            name_en="Leaf Rust",
            name_ar="صدأ الأوراق",
            pathogen_type="fungal",
            severity_level=8,
            symptoms_en=["Yellow spots", "Brown pustules"],
            symptoms_ar=["بقع صفراء", "بثور بنية"],
            incubation_days=7,
        )
        assert disease.severity_level == 8
        assert len(disease.symptoms_en) == 2
        assert disease.incubation_days == 7

    def test_disease_severity_range(self):
        """Test Disease severity_level must be 1-10."""
        with pytest.raises(Exception):
            Disease(id="bad", name_en="Bad", name_ar="سيء", severity_level=15)

    def test_treatment_model_creation(self):
        """Test creating a Treatment model."""
        treatment = Treatment(
            id="neem-oil",
            name_en="Neem Oil",
            name_ar="زيت النيم",
            treatment_type="insecticide",
            active_ingredient="Azadirachtin",
            concentration="0.3%",
            application_method="spray",
            safety_level=1,
            cost_per_liter=25.0,
        )
        assert treatment.treatment_type == "insecticide"
        assert treatment.safety_level == 1
        assert treatment.cost_per_liter == 25.0

    def test_treatment_safety_range(self):
        """Test Treatment safety_level must be 1-5."""
        with pytest.raises(Exception):
            Treatment(id="bad", name_en="Bad", name_ar="سيء", safety_level=10)

    def test_relationship_type_enum(self):
        """Test RelationshipType enum values."""
        assert RelationshipType.AFFECTS == "affects"
        assert RelationshipType.TREATED_BY == "treated_by"
        assert RelationshipType.PREVENTS == "prevents"
        assert RelationshipType.RESISTANT_TO == "resistant_to"
        assert RelationshipType.COMPATIBLE == "compatible"
        assert RelationshipType.FOLLOWS == "follows"

    def test_relationship_model(self):
        """Test Relationship model with confidence bounds."""
        rel = Relationship(
            id="rel-1",
            source_type="disease",
            source_id="rust",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
            confidence=0.95,
            evidence=["Study A", "Study B"],
        )
        assert rel.confidence == 0.95
        assert len(rel.evidence) == 2

    def test_relationship_confidence_bounds(self):
        """Test Relationship confidence must be 0-1."""
        with pytest.raises(Exception):
            Relationship(
                id="bad",
                source_type="a",
                source_id="b",
                target_type="c",
                target_id="d",
                relationship_type=RelationshipType.AFFECTS,
                confidence=1.5,
            )

    def test_graph_node_model(self):
        """Test GraphNode model."""
        node = GraphNode(
            id="crop:wheat",
            node_type="crop",
            label="Wheat",
            label_ar="القمح",
            metadata={"region": "Middle East"},
        )
        assert node.id == "crop:wheat"
        assert node.label_ar == "القمح"

    def test_graph_edge_model(self):
        """Test GraphEdge model."""
        edge = GraphEdge(
            id="e1",
            source="disease:rust",
            target="crop:wheat",
            relationship_type=RelationshipType.AFFECTS,
            confidence=0.9,
        )
        assert edge.source == "disease:rust"
        assert edge.confidence == 0.9

    def test_path_response_model(self):
        """Test PathResponse model."""
        path = PathResponse(
            start_node=GraphNode(id="a", node_type="crop", label="A"),
            end_node=GraphNode(id="b", node_type="disease", label="B"),
            path=["a", "b"],
            length=1,
            edges=[],
            explanation="Direct path",
        )
        assert path.length == 1
        assert path.explanation == "Direct path"

    def test_health_check_response_model(self):
        """Test HealthCheckResponse model."""
        resp = HealthCheckResponse(
            status="healthy",
            service="knowledge-graph",
            version="16.0.0",
            database=True,
        )
        assert resp.status == "healthy"
        assert resp.database is True
# ═══════════════════════════════════════════════════════════════════════════════
# KnowledgeGraphService Tests (graph_service.py)
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
class TestKnowledgeGraphServiceUnit:
    """Unit tests for KnowledgeGraphService with mocked shared builder."""

    @pytest.fixture
    async def service(self):
        """Create a service with fallback data (no shared builder)."""
        with patch("services.graph_service._HAS_SHARED_KG", False):
            svc = KnowledgeGraphService()
            await svc._load_fallback_data()
        return svc

    async def test_fallback_data_loads_crops(self, service):
        """Test fallback data loads wheat and tomato."""
        assert "crop:wheat" in service.entities
        assert "crop:tomato" in service.entities
        assert service.graph.number_of_nodes() >= 2

    async def test_add_crop(self, service):
        """Test adding a crop node."""
        crop = Crop(id="corn", name_en="Corn", name_ar="الذرة")
        result = await service.add_crop(crop)
        assert result is True
        assert "crop:corn" in service.entities
        assert service.graph.has_node("crop:corn")

    async def test_add_disease(self, service):
        """Test adding a disease node."""
        disease = Disease(id="blight", name_en="Blight", name_ar="اللفحة")
        result = await service.add_disease(disease)
        assert result is True
        assert "disease:blight" in service.entities

    async def test_add_treatment(self, service):
        """Test adding a treatment node."""
        treatment = Treatment(id="copper", name_en="Copper Spray", name_ar="رش النحاس")
        result = await service.add_treatment(treatment)
        assert result is True
        assert "treatment:copper" in service.entities

    async def test_add_relationship_success(self, service):
        """Test adding a relationship between existing nodes."""
        disease = Disease(id="mildew", name_en="Mildew", name_ar="العفن")
        await service.add_disease(disease)
        result = await service.add_relationship(
            source_type="disease",
            source_id="mildew",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
            confidence=0.85,
        )
        assert result is True
        assert service.graph.has_edge("disease:mildew", "crop:wheat")

    async def test_add_relationship_missing_node(self, service):
        """Test adding a relationship when a node doesn't exist."""
        result = await service.add_relationship(
            source_type="disease",
            source_id="nonexistent",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert result is False

    async def test_get_crop_found(self, service):
        """Test getting an existing crop."""
        crop = await service.get_crop("wheat")
        assert crop is not None
        assert crop.name_en == "Wheat"

    async def test_get_crop_not_found(self, service):
        """Test getting a non-existent crop returns None."""
        crop = await service.get_crop("banana")
        assert crop is None

    async def test_get_disease_not_found(self, service):
        """Test getting a non-existent disease returns None."""
        disease = await service.get_disease("nonexistent")
        assert disease is None

    async def test_get_treatment_not_found(self, service):
        """Test getting a non-existent treatment returns None."""
        treatment = await service.get_treatment("nonexistent")
        assert treatment is None

    async def test_get_related_entities_no_node(self, service):
        """Test related entities for non-existent node returns empty list."""
        related = await service.get_related_entities(
            entity_type="crop",
            entity_id="nonexistent",
        )
        assert related == []

    async def test_get_related_entities_with_filter(self, service):
        """Test related entities with relationship type filter."""
        # Setup: disease -> crop
        disease = Disease(id="scab", name_en="Scab", name_ar="الجرب")
        await service.add_disease(disease)
        await service.add_relationship(
            source_type="disease",
            source_id="scab",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
        )
        # Filter by AFFECTS should return wheat
        related = await service.get_related_entities(
            entity_type="disease",
            entity_id="scab",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert len(related) == 1
        # Filter by TREATED_BY should return empty
        related_empty = await service.get_related_entities(
            entity_type="disease",
            entity_id="scab",
            relationship_type=RelationshipType.TREATED_BY,
        )
        assert len(related_empty) == 0

    async def test_find_shortest_path_success(self, service):
        """Test finding shortest path between connected nodes."""
        disease = Disease(id="d1", name_en="D1", name_ar="م1")
        treatment = Treatment(id="t1", name_en="T1", name_ar="ع1")
        await service.add_disease(disease)
        await service.add_treatment(treatment)
        await service.add_relationship(
            source_type="disease",
            source_id="d1",
            target_type="treatment",
            target_id="t1",
            relationship_type=RelationshipType.TREATED_BY,
        )
        path = await service.find_shortest_path("disease", "d1", "treatment", "t1")
        assert path is not None
        assert path.length == 1
        assert len(path.edges) == 1

    async def test_find_shortest_path_no_path(self, service):
        """Test finding path between disconnected nodes returns None."""
        disease = Disease(id="isolated", name_en="Isolated", name_ar="معزول")
        await service.add_disease(disease)
        path = await service.find_shortest_path("disease", "isolated", "crop", "wheat")
        assert path is None

    async def test_find_shortest_path_missing_node(self, service):
        """Test path with non-existent node returns None."""
        path = await service.find_shortest_path("crop", "nonexistent", "crop", "wheat")
        assert path is None

    async def test_search_entities_by_name(self, service):
        """Test searching entities by English name."""
        results = await service.search_entities("Wheat")
        assert len(results) >= 1
        assert any("wheat" in r.get("id", "").lower() for r in results)

    async def test_search_entities_by_type(self, service):
        """Test searching entities filtered by type."""
        results = await service.search_entities("Wheat", entity_type="crop")
        assert len(results) >= 1
        # Type filter on disease should exclude wheat
        results_disease = await service.search_entities("Wheat", entity_type="disease")
        assert len(results_disease) == 0

    async def test_search_entities_limit(self, service):
        """Test search respects limit parameter."""
        results = await service.search_entities("", limit=1)
        assert len(results) <= 1

    async def test_get_all_crops(self, service):
        """Test getting all crops."""
        crops = await service.get_all_crops()
        assert len(crops) >= 2  # wheat and tomato from fallback
        assert all("crop:" in c["id"] for c in crops)

    async def test_get_all_diseases(self, service):
        """Test getting all diseases (empty initially in fallback)."""
        diseases = await service.get_all_diseases()
        assert isinstance(diseases, list)

    async def test_get_all_treatments(self, service):
        """Test getting all treatments."""
        treatments = await service.get_all_treatments()
        assert isinstance(treatments, list)

    async def test_get_graph_stats(self, service):
        """Test graph statistics."""
        stats = await service.get_graph_stats()
        assert stats["total_nodes"] >= 2
        assert stats["crops"] >= 2
        assert "total_edges" in stats
        assert "relationships" in stats

    async def test_health_check_healthy(self, service):
        """Test health check with populated graph."""
        assert await service.health_check() is True

    async def test_health_check_empty_graph(self):
        """Test health check with empty graph returns False."""
        svc = KnowledgeGraphService()
        assert await svc.health_check() is False

    async def test_add_generic_entity(self, service):
        """Test _add_generic_entity for irrigation/equipment types."""
        mock_entity = MagicMock()
        mock_entity.entity_type = "irrigation"
        mock_entity.id = "irr_drip"
        mock_entity.name = "Drip Irrigation"
        mock_entity.name_ar = "ري بالتنقيط"
        mock_entity.properties = {"efficiency": 0.95}
        result = await service._add_generic_entity(mock_entity)
        assert result is True
        assert "irrigation:drip" in service.entities

    async def test_get_disease_found(self, service):
        """Test getting an existing disease."""
        disease = Disease(id="mildew", name_en="Mildew", name_ar="العفن")
        await service.add_disease(disease)
        result = await service.get_disease("mildew")
        assert result is not None
        assert result.name_en == "Mildew"

    async def test_get_treatment_found(self, service):
        """Test getting an existing treatment."""
        treatment = Treatment(id="copper", name_en="Copper", name_ar="نحاس")
        await service.add_treatment(treatment)
        result = await service.get_treatment("copper")
        assert result is not None
        assert result.name_en == "Copper"

    async def test_get_all_crops_with_limit(self, service):
        """Test get_all_crops respects limit."""
        crops = await service.get_all_crops(limit=1)
        assert len(crops) == 1

    async def test_get_all_diseases_with_data(self, service):
        """Test get_all_diseases after adding diseases."""
        await service.add_disease(Disease(id="rust-a", name_en="Rust A", name_ar="صدأ أ"))
        await service.add_disease(Disease(id="rust-b", name_en="Rust B", name_ar="صدأ ب"))
        diseases = await service.get_all_diseases(limit=10)
        assert len(diseases) >= 2

    async def test_get_all_treatments_with_data(self, service):
        """Test get_all_treatments after adding treatments."""
        await service.add_treatment(Treatment(id="spray-a", name_en="Spray A", name_ar="رش أ"))
        treatments = await service.get_all_treatments(limit=10)
        assert len(treatments) >= 1

    async def test_search_arabic_name(self, service):
        """Test searching by Arabic name."""
        results = await service.search_entities("القمح")
        assert len(results) >= 1

    async def test_get_related_entities_with_limit(self, service):
        """Test related entities respects limit."""
        disease = Disease(id="rl-d", name_en="TestD", name_ar="تجربة")
        await service.add_disease(disease)
        await service.add_relationship(
            source_type="disease", source_id="rl-d",
            target_type="crop", target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
        )
        await service.add_relationship(
            source_type="disease", source_id="rl-d",
            target_type="crop", target_id="tomato",
            relationship_type=RelationshipType.AFFECTS,
        )
        related = await service.get_related_entities("disease", "rl-d", limit=1)
        assert len(related) == 1

    async def test_health_check_exception(self):
        """Test health check handles exception gracefully."""
        svc = KnowledgeGraphService()
        # Corrupt the graph to cause exception
        svc.graph = None
        result = await svc.health_check()
        assert result is False
# ═══════════════════════════════════════════════════════════════════════════════
# EntityService Tests (entity_service.py)
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
class TestEntityService:
    """Tests for EntityService layer."""

    @pytest.fixture
    def mock_graph(self):
        """Create a mock graph service."""
        graph = AsyncMock()
        graph.add_crop = AsyncMock(return_value=True)
        graph.add_disease = AsyncMock(return_value=True)
        graph.add_treatment = AsyncMock(return_value=True)
        graph.get_crop = AsyncMock(return_value=Crop(id="wheat", name_en="Wheat", name_ar="القمح"))
        graph.get_disease = AsyncMock(return_value=None)
        graph.get_treatment = AsyncMock(return_value=None)
        graph.get_all_crops = AsyncMock(return_value=[{"id": "crop:wheat", "name_en": "Wheat", "name_ar": "القمح"}])
        graph.get_all_diseases = AsyncMock(return_value=[])
        graph.get_all_treatments = AsyncMock(return_value=[])
        graph.search_entities = AsyncMock(return_value=[
            {"id": "crop:wheat", "name_en": "Wheat", "name_ar": "القمح"},
        ])
        return graph

    @pytest.fixture
    def entity_service(self, mock_graph):
        return EntityService(mock_graph)

    async def test_create_crop_success(self, entity_service):
        crop = Crop(id="rice", name_en="Rice", name_ar="الأرز")
        result = await entity_service.create_crop(crop)
        assert result is True

    async def test_create_crop_failure(self, entity_service, mock_graph):
        mock_graph.add_crop = AsyncMock(side_effect=Exception("DB error"))
        crop = Crop(id="rice", name_en="Rice", name_ar="الأرز")
        result = await entity_service.create_crop(crop)
        assert result is False

    async def test_create_disease_success(self, entity_service):
        disease = Disease(id="blight", name_en="Blight", name_ar="اللفحة")
        result = await entity_service.create_disease(disease)
        assert result is True

    async def test_create_disease_failure(self, entity_service, mock_graph):
        mock_graph.add_disease = AsyncMock(side_effect=RuntimeError("fail"))
        disease = Disease(id="blight", name_en="Blight", name_ar="اللفحة")
        result = await entity_service.create_disease(disease)
        assert result is False

    async def test_create_treatment_success(self, entity_service):
        treatment = Treatment(id="copper", name_en="Copper", name_ar="نحاس")
        result = await entity_service.create_treatment(treatment)
        assert result is True

    async def test_create_treatment_failure(self, entity_service, mock_graph):
        mock_graph.add_treatment = AsyncMock(side_effect=Exception("fail"))
        treatment = Treatment(id="copper", name_en="Copper", name_ar="نحاس")
        result = await entity_service.create_treatment(treatment)
        assert result is False

    async def test_get_crop(self, entity_service):
        crop = await entity_service.get_crop("wheat")
        assert crop is not None
        assert crop.name_en == "Wheat"

    async def test_list_crops(self, entity_service):
        crops = await entity_service.list_crops()
        assert len(crops) >= 1
        assert crops[0]["name_en"] == "Wheat"

    async def test_list_diseases(self, entity_service):
        diseases = await entity_service.list_diseases()
        assert isinstance(diseases, list)

    async def test_list_treatments(self, entity_service):
        treatments = await entity_service.list_treatments()
        assert isinstance(treatments, list)

    async def test_search(self, entity_service):
        results = await entity_service.search("wheat")
        assert results["query"] == "wheat"
        assert results["total_results"] >= 1
        assert "crops" in results["results"]

    async def test_format_crop_response_with_prefix(self):
        """Test _format_crop_response strips crop: prefix."""
        formatted = EntityService._format_crop_response({"id": "crop:wheat", "name_en": "Wheat"})
        assert formatted["id"] == "wheat"

    async def test_format_crop_response_without_prefix(self):
        """Test _format_crop_response without prefix."""
        formatted = EntityService._format_crop_response({"id": "wheat", "name_en": "Wheat"})
        assert formatted["id"] == "wheat"

    async def test_format_disease_response_strips_prefix(self):
        """Test _format_disease_response strips disease: prefix."""
        formatted = EntityService._format_disease_response({"id": "disease:rust", "name_en": "Rust"})
        assert formatted["id"] == "rust"

    async def test_format_treatment_response_strips_prefix(self):
        """Test _format_treatment_response strips treatment: prefix."""
        formatted = EntityService._format_treatment_response({"id": "treatment:sulfur", "name_en": "Sulfur"})
        assert formatted["id"] == "sulfur"

    async def test_get_disease(self, entity_service, mock_graph):
        """Test get_disease delegates to graph."""
        mock_graph.get_disease = AsyncMock(return_value=Disease(id="rust", name_en="Rust", name_ar="صدأ"))
        disease = await entity_service.get_disease("rust")
        assert disease is not None
        assert disease.name_en == "Rust"

    async def test_get_treatment(self, entity_service, mock_graph):
        """Test get_treatment delegates to graph."""
        mock_graph.get_treatment = AsyncMock(return_value=Treatment(id="sulfur", name_en="Sulfur", name_ar="كبريت"))
        treatment = await entity_service.get_treatment("sulfur")
        assert treatment is not None
        assert treatment.name_en == "Sulfur"

    async def test_search_with_disease_results(self, entity_service, mock_graph):
        """Test search organizes disease results correctly."""
        mock_graph.search_entities = AsyncMock(return_value=[
            {"id": "disease:rust", "name_en": "Leaf Rust", "name_ar": "صدأ"},
        ])
        results = await entity_service.search("rust")
        assert len(results["results"]["diseases"]) == 1
        assert results["results"]["diseases"][0]["id"] == "rust"

    async def test_search_with_treatment_results(self, entity_service, mock_graph):
        """Test search organizes treatment results correctly."""
        mock_graph.search_entities = AsyncMock(return_value=[
            {"id": "treatment:copper", "name_en": "Copper Spray", "name_ar": "نحاس"},
        ])
        results = await entity_service.search("copper")
        assert len(results["results"]["treatments"]) == 1
        assert results["results"]["treatments"][0]["id"] == "copper"

    async def test_search_mixed_results(self, entity_service, mock_graph):
        """Test search with mixed entity types."""
        mock_graph.search_entities = AsyncMock(return_value=[
            {"id": "crop:wheat", "name_en": "Wheat", "name_ar": "القمح"},
            {"id": "disease:rust", "name_en": "Wheat Rust", "name_ar": "صدأ القمح"},
            {"id": "treatment:fungicide", "name_en": "Fungicide", "name_ar": "مبيد فطري"},
        ])
        results = await entity_service.search("wheat")
        assert len(results["results"]["crops"]) == 1
        assert len(results["results"]["diseases"]) == 1
        assert len(results["results"]["treatments"]) == 1
        assert results["total_results"] == 3
# ═══════════════════════════════════════════════════════════════════════════════
# RelationshipService Tests (relationship_service.py)
# ═══════════════════════════════════════════════════════════════════════════════
@pytest.mark.asyncio
class TestRelationshipService:
    """Tests for RelationshipService layer."""

    @pytest.fixture
    def mock_graph(self):
        graph = AsyncMock()
        graph.add_relationship = AsyncMock(return_value=True)
        graph.get_related_entities = AsyncMock(return_value=[
            {"id": "crop:wheat", "name_en": "Wheat", "relationship": {"type": "affects", "confidence": 0.9}},
        ])
        graph.find_shortest_path = AsyncMock(return_value=PathResponse(
            start_node=GraphNode(id="a", node_type="disease", label="A"),
            end_node=GraphNode(id="b", node_type="treatment", label="B"),
            path=["a", "b"],
            length=1,
            edges=[],
        ))
        graph.relationships = {}
        return graph

    @pytest.fixture
    def rel_service(self, mock_graph):
        return RelationshipService(mock_graph)

    async def test_add_relationship_success(self, rel_service):
        result = await rel_service.add_relationship(
            source_type="disease",
            source_id="rust",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert result is True

    async def test_add_relationship_failure(self, rel_service, mock_graph):
        mock_graph.add_relationship = AsyncMock(side_effect=Exception("fail"))
        result = await rel_service.add_relationship(
            source_type="disease",
            source_id="rust",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert result is False

    async def test_get_related_by_type(self, rel_service):
        results = await rel_service.get_related_by_type(
            entity_type="disease",
            entity_id="rust",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert len(results) >= 1

    async def test_get_related_by_type_exception(self, rel_service, mock_graph):
        mock_graph.get_related_entities = AsyncMock(side_effect=Exception("fail"))
        results = await rel_service.get_related_by_type(
            entity_type="disease",
            entity_id="rust",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert results == []

    async def test_get_all_related(self, rel_service):
        results = await rel_service.get_all_related("disease", "rust")
        assert len(results) >= 1

    async def test_get_all_related_exception(self, rel_service, mock_graph):
        mock_graph.get_related_entities = AsyncMock(side_effect=Exception("err"))
        results = await rel_service.get_all_related("disease", "rust")
        assert results == []

    async def test_find_relationship_path(self, rel_service):
        result = await rel_service.find_relationship_path("disease", "d1", "treatment", "t1")
        assert result is not None
        assert result["length"] == 1

    async def test_find_relationship_path_none(self, rel_service, mock_graph):
        mock_graph.find_shortest_path = AsyncMock(return_value=None)
        result = await rel_service.find_relationship_path("disease", "d1", "treatment", "t1")
        assert result is None

    async def test_find_relationship_path_exception(self, rel_service, mock_graph):
        mock_graph.find_shortest_path = AsyncMock(side_effect=Exception("err"))
        result = await rel_service.find_relationship_path("disease", "d1", "treatment", "t1")
        assert result is None

    async def test_get_affected_crops(self, rel_service):
        results = await rel_service.get_affected_crops("rust")
        assert len(results) >= 1

    async def test_get_disease_treatments(self, rel_service):
        results = await rel_service.get_disease_treatments("rust")
        assert isinstance(results, list)

    async def test_get_crop_compatible_treatments(self, rel_service):
        results = await rel_service.get_crop_compatible_treatments("wheat")
        assert isinstance(results, list)

    async def test_get_diseases_affecting_crop(self, rel_service, mock_graph):
        mock_graph.get_related_entities = AsyncMock(return_value=[
            {"id": "disease:rust"},
            {"id": "crop:barley"},
        ])
        results = await rel_service.get_diseases_affecting_crop("wheat")
        assert len(results) == 1
        assert results[0]["id"] == "disease:rust"

    async def test_get_preventive_treatments(self, rel_service):
        results = await rel_service.get_preventive_treatments("rust")
        assert isinstance(results, list)

    async def test_validate_relationship_exists(self, rel_service, mock_graph):
        rel = Relationship(
            id="disease:rust--affects--crop:wheat",
            source_type="disease",
            source_id="rust",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
        )
        mock_graph.relationships = {"disease:rust--affects--crop:wheat": rel}
        result = await rel_service.validate_relationship(
            source_type="disease",
            source_id="rust",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert result["exists"] is True
        assert result["relationship"] is not None

    async def test_validate_relationship_not_exists(self, rel_service, mock_graph):
        mock_graph.relationships = {}
        result = await rel_service.validate_relationship(
            source_type="disease",
            source_id="nonexistent",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert result["exists"] is False

    async def test_validate_relationship_exception(self, rel_service, mock_graph):
        # Make relationships access raise an exception
        type(mock_graph).relationships = property(lambda self: (_ for _ in ()).throw(Exception("err")))
        result = await rel_service.validate_relationship(
            source_type="disease",
            source_id="rust",
            target_type="crop",
            target_id="wheat",
            relationship_type=RelationshipType.AFFECTS,
        )
        assert result["exists"] is False
        assert "error" in result
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
