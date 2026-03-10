"""
Tests for Agricultural Knowledge Graph Builder
================================================
اختبارات بناء الرسم البياني للمعرفة الزراعية

Tests for KGEntity, KGRelation, AgriculturalKnowledgeGraph,
and the build_agricultural_knowledge_graph() factory function.
"""

from __future__ import annotations

import pytest

from shared.ai.knowledge.graph_builder import (
    AgriculturalKnowledgeGraph,
    KGEntity,
    KGRelation,
    build_agricultural_knowledge_graph,
)


# ─── Data Class Tests ────────────────────────────────────────────────────────


class TestKGEntity:
    """Tests for KGEntity dataclass."""

    @pytest.mark.unit
    def test_basic_entity(self):
        """Test creating a basic entity."""
        entity = KGEntity(
            id="crop_wheat",
            name="Wheat",
            name_ar="قمح",
            entity_type="crop",
        )
        assert entity.id == "crop_wheat"
        assert entity.name == "Wheat"
        assert entity.name_ar == "قمح"
        assert entity.entity_type == "crop"
        assert entity.properties == {}

    @pytest.mark.unit
    def test_entity_with_properties(self):
        """Test entity with custom properties."""
        entity = KGEntity(
            id="crop_barley",
            name="Barley",
            name_ar="شعير",
            entity_type="crop",
            properties={"family": "Poaceae", "drought_tolerant": True},
        )
        assert entity.properties["family"] == "Poaceae"
        assert entity.properties["drought_tolerant"] is True

    @pytest.mark.unit
    def test_entity_bilingual(self):
        """Test bilingual entity names | اختبار ثنائية اللغة"""
        entity = KGEntity(id="pest_rpw", name="Red Palm Weevil", name_ar="سوسة النخيل الحمراء", entity_type="pest")
        assert entity.name_ar == "سوسة النخيل الحمراء"


class TestKGRelation:
    """Tests for KGRelation dataclass."""

    @pytest.mark.unit
    def test_basic_relation(self):
        """Test creating a basic relation."""
        rel = KGRelation(
            source_id="disease_rust",
            target_id="crop_wheat",
            relation_type="affects",
        )
        assert rel.source_id == "disease_rust"
        assert rel.target_id == "crop_wheat"
        assert rel.relation_type == "affects"
        assert rel.confidence == 1.0
        assert rel.evidence == []

    @pytest.mark.unit
    def test_relation_with_confidence(self):
        """Test relation with custom confidence score."""
        rel = KGRelation(
            source_id="treatment_propiconazole",
            target_id="disease_rust",
            relation_type="treats",
            confidence=0.92,
            evidence=["ICARDA field trials 2024"],
        )
        assert rel.confidence == 0.92
        assert len(rel.evidence) == 1


class TestAgriculturalKnowledgeGraph:
    """Tests for AgriculturalKnowledgeGraph container."""

    @pytest.mark.unit
    def test_empty_graph(self):
        """Test creating empty graph."""
        graph = AgriculturalKnowledgeGraph()
        assert graph.entities == []
        assert graph.relations == []

    @pytest.mark.unit
    def test_graph_with_data(self):
        """Test graph with entities and relations."""
        entity = KGEntity(id="crop_wheat", name="Wheat", name_ar="قمح", entity_type="crop")
        relation = KGRelation(source_id="disease_rust", target_id="crop_wheat", relation_type="affects")
        graph = AgriculturalKnowledgeGraph(entities=[entity], relations=[relation])
        assert len(graph.entities) == 1
        assert len(graph.relations) == 1


# ─── Factory Function Tests ──────────────────────────────────────────────────


class TestBuildAgriculturalKnowledgeGraph:
    """Tests for build_agricultural_knowledge_graph() factory function."""

    @pytest.fixture
    def graph(self) -> AgriculturalKnowledgeGraph:
        return build_agricultural_knowledge_graph()

    @pytest.mark.unit
    def test_returns_graph(self, graph: AgriculturalKnowledgeGraph):
        """Test that build returns an AgriculturalKnowledgeGraph."""
        assert isinstance(graph, AgriculturalKnowledgeGraph)

    @pytest.mark.unit
    def test_has_entities(self, graph: AgriculturalKnowledgeGraph):
        """Test that the graph contains entities."""
        assert len(graph.entities) > 0

    @pytest.mark.unit
    def test_has_relations(self, graph: AgriculturalKnowledgeGraph):
        """Test that the graph contains relations."""
        assert len(graph.relations) > 0

    @pytest.mark.unit
    def test_entity_types_present(self, graph: AgriculturalKnowledgeGraph):
        """Test all expected entity types are present."""
        entity_types = {e.entity_type for e in graph.entities}
        assert "crop" in entity_types
        assert "disease" in entity_types
        assert "pest" in entity_types
        assert "treatment" in entity_types
        assert "fertilizer" in entity_types
        assert "irrigation" in entity_types

    @pytest.mark.unit
    def test_crops_present(self, graph: AgriculturalKnowledgeGraph):
        """Test key crops are in the graph."""
        crop_ids = {e.id for e in graph.entities if e.entity_type == "crop"}
        assert "crop_wheat" in crop_ids
        assert "crop_barley" in crop_ids
        assert "crop_date_palm" in crop_ids

    @pytest.mark.unit
    def test_crop_count(self, graph: AgriculturalKnowledgeGraph):
        """Test at least 12 crops in graph."""
        crops = [e for e in graph.entities if e.entity_type == "crop"]
        assert len(crops) >= 12

    @pytest.mark.unit
    def test_diseases_present(self, graph: AgriculturalKnowledgeGraph):
        """Test key diseases are in the graph."""
        disease_ids = {e.id for e in graph.entities if e.entity_type == "disease"}
        assert "disease_rust" in disease_ids

    @pytest.mark.unit
    def test_pests_present(self, graph: AgriculturalKnowledgeGraph):
        """Test key pests like RPW are in the graph."""
        pest_ids = {e.id for e in graph.entities if e.entity_type == "pest"}
        assert "pest_rpw" in pest_ids

    @pytest.mark.unit
    def test_irrigation_methods_present(self, graph: AgriculturalKnowledgeGraph):
        """Test irrigation methods are in the graph."""
        irrigation_ids = {e.id for e in graph.entities if e.entity_type == "irrigation"}
        assert len(irrigation_ids) >= 5

    @pytest.mark.unit
    def test_all_entities_have_bilingual_names(self, graph: AgriculturalKnowledgeGraph):
        """Test all entities have both EN and AR names."""
        for entity in graph.entities:
            assert entity.name, f"Entity {entity.id} missing name"
            assert entity.name_ar, f"Entity {entity.id} missing name_ar"

    @pytest.mark.unit
    def test_all_entities_have_id(self, graph: AgriculturalKnowledgeGraph):
        """Test all entities have non-empty IDs."""
        for entity in graph.entities:
            assert entity.id, "Entity has empty id"

    @pytest.mark.unit
    def test_no_duplicate_entity_ids(self, graph: AgriculturalKnowledgeGraph):
        """Test no duplicate entity IDs."""
        ids = [e.id for e in graph.entities]
        assert len(ids) == len(set(ids)), "Duplicate entity IDs found"

    @pytest.mark.unit
    def test_relations_reference_valid_entities(self, graph: AgriculturalKnowledgeGraph):
        """Test all relations reference existing entity IDs."""
        entity_ids = {e.id for e in graph.entities}
        for rel in graph.relations:
            assert rel.source_id in entity_ids, f"Relation source {rel.source_id} not in entities"
            assert rel.target_id in entity_ids, f"Relation target {rel.target_id} not in entities"

    @pytest.mark.unit
    def test_relation_types(self, graph: AgriculturalKnowledgeGraph):
        """Test expected relation types exist."""
        rel_types = {r.relation_type for r in graph.relations}
        assert "affects" in rel_types
        assert "treats" in rel_types

    @pytest.mark.unit
    def test_relation_confidence_range(self, graph: AgriculturalKnowledgeGraph):
        """Test all relation confidences are in [0, 1]."""
        for rel in graph.relations:
            assert 0.0 <= rel.confidence <= 1.0, (
                f"Confidence {rel.confidence} out of range for {rel.source_id}→{rel.target_id}"
            )

    @pytest.mark.unit
    def test_wheat_rust_relation_exists(self, graph: AgriculturalKnowledgeGraph):
        """Test wheat-rust relationship exists (key agricultural knowledge)."""
        rust_wheat = [
            r
            for r in graph.relations
            if r.relation_type == "affects" and "rust" in r.source_id and "wheat" in r.target_id
        ]
        assert len(rust_wheat) >= 1, "Missing wheat-rust affects relationship"
