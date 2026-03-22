"""
Tests for Disease & Pest Knowledge Scenarios
==============================================
سيناريوهات اختبار قاعدة معرفة الأمراض والآفات

Integration scenarios verifying:
1. New disease entities (bacterial, viral, abiotic) in graph_builder
2. New pest entities (sunn pest, armyworm, bollworm, nematode, etc.)
3. Vector transmission relations (pest → disease transmits)
4. Disease diagnosis pathways via knowledge graph traversal
5. Collection populator coverage for new disease docs
"""

from __future__ import annotations

from pathlib import Path

import pytest

from shared.ai.knowledge.collection_populator import (
    KnowledgeBasePopulator,
)
from shared.ai.knowledge.collections import (
    PEST_KNOWLEDGE,
)
from shared.ai.knowledge.graph_builder import (
    AgriculturalKnowledgeGraph,
    build_agricultural_knowledge_graph,
)


@pytest.fixture(scope="module")
def graph() -> AgriculturalKnowledgeGraph:
    """Build graph once for all tests in module."""
    return build_agricultural_knowledge_graph()


# ─── Helper Utilities ────────────────────────────────────────────────────────


def _entities_by_type(graph: AgriculturalKnowledgeGraph, entity_type: str) -> dict[str, str]:
    """Return {id: name} for entities of a given type."""
    return {e.id: e.name for e in graph.entities if e.entity_type == entity_type}


def _relations_of_type(graph: AgriculturalKnowledgeGraph, rel_type: str) -> list:
    """Return relations of a given type."""
    return [r for r in graph.relations if r.relation_type == rel_type]


def _get_entity(graph: AgriculturalKnowledgeGraph, entity_id: str):
    """Get an entity by ID."""
    for e in graph.entities:
        if e.id == entity_id:
            return e
    return None


def _find_relations(graph: AgriculturalKnowledgeGraph, source_id: str, rel_type: str) -> list:
    """Find all relations from a source entity of a given type."""
    return [r for r in graph.relations if r.source_id == source_id and r.relation_type == rel_type]


def _find_reverse_relations(graph: AgriculturalKnowledgeGraph, target_id: str, rel_type: str) -> list:
    """Find all relations targeting an entity of a given type."""
    return [r for r in graph.relations if r.target_id == target_id and r.relation_type == rel_type]


# ═══════════════════════════════════════════════════════════════════════════════
# 1. Disease Category Coverage Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestDiseaseCategoryCoverage:
    """Verify all three disease categories (fungal, bacterial, viral) plus abiotic."""

    @pytest.mark.unit
    def test_fungal_diseases_present(self, graph: AgriculturalKnowledgeGraph):
        """Test fungal diseases are in the graph."""
        diseases = _entities_by_type(graph, "disease")
        fungal = [d for d in diseases if _get_entity(graph, d).properties.get("pathogen_type") == "fungal"]
        assert len(fungal) >= 5, f"Expected >= 5 fungal diseases, got {len(fungal)}"
        fungal_ids = set(fungal)
        assert "disease_rust" in fungal_ids
        assert "disease_powdery_mildew" in fungal_ids
        assert "disease_fusarium" in fungal_ids
        assert "disease_late_blight" in fungal_ids

    @pytest.mark.unit
    def test_bacterial_diseases_present(self, graph: AgriculturalKnowledgeGraph):
        """Test bacterial diseases are in the graph | التحقق من الأمراض البكتيرية."""
        diseases = _entities_by_type(graph, "disease")
        bacterial = [d for d in diseases if _get_entity(graph, d).properties.get("pathogen_type") == "bacterial"]
        assert len(bacterial) >= 4, f"Expected >= 4 bacterial diseases, got {len(bacterial)}"
        bacterial_ids = set(bacterial)
        assert "disease_bacterial_blight" in bacterial_ids
        assert "disease_bacterial_wilt" in bacterial_ids
        assert "disease_fire_blight" in bacterial_ids
        assert "disease_bacterial_canker" in bacterial_ids

    @pytest.mark.unit
    def test_viral_diseases_present(self, graph: AgriculturalKnowledgeGraph):
        """Test viral diseases are in the graph | التحقق من الأمراض الفيروسية."""
        diseases = _entities_by_type(graph, "disease")
        viral = [d for d in diseases if _get_entity(graph, d).properties.get("pathogen_type") == "viral"]
        assert len(viral) >= 4, f"Expected >= 4 viral diseases, got {len(viral)}"
        viral_ids = set(viral)
        assert "disease_mosaic_virus" in viral_ids
        assert "disease_tylcv" in viral_ids
        assert "disease_ctv" in viral_ids
        assert "disease_cotton_leaf_curl" in viral_ids

    @pytest.mark.unit
    def test_abiotic_disorders_present(self, graph: AgriculturalKnowledgeGraph):
        """Test nutrient deficiency disorders are in the graph | نقص العناصر الغذائية."""
        diseases = _entities_by_type(graph, "disease")
        abiotic = [d for d in diseases if _get_entity(graph, d).properties.get("pathogen_type") == "abiotic"]
        assert len(abiotic) >= 3, f"Expected >= 3 abiotic disorders, got {len(abiotic)}"
        abiotic_ids = set(abiotic)
        assert "disease_nitrogen_deficiency" in abiotic_ids
        assert "disease_phosphorus_deficiency" in abiotic_ids
        assert "disease_potassium_deficiency" in abiotic_ids

    @pytest.mark.unit
    def test_total_disease_count(self, graph: AgriculturalKnowledgeGraph):
        """Test total disease count meets minimum threshold."""
        diseases = _entities_by_type(graph, "disease")
        assert len(diseases) >= 17, f"Expected >= 17 total diseases, got {len(diseases)}"

    @pytest.mark.unit
    def test_all_diseases_have_severity(self, graph: AgriculturalKnowledgeGraph):
        """Test all diseases have severity_level property."""
        for e in graph.entities:
            if e.entity_type == "disease":
                assert "severity_level" in e.properties, f"Disease {e.id} missing severity_level"
                assert 1 <= e.properties["severity_level"] <= 10, f"Disease {e.id} severity out of range"


# ═══════════════════════════════════════════════════════════════════════════════
# 2. New Pest Entity Validation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestNewPestEntities:
    """Validate new pest entities and their properties."""

    @pytest.mark.unit
    def test_total_pest_count(self, graph: AgriculturalKnowledgeGraph):
        """Test total pest count meets minimum threshold."""
        pests = _entities_by_type(graph, "pest")
        assert len(pests) >= 15, f"Expected >= 15 pests, got {len(pests)}"

    @pytest.mark.unit
    def test_sunn_pest_exists(self, graph: AgriculturalKnowledgeGraph):
        """Test Sunn Pest entity | حشرة السونة."""
        entity = _get_entity(graph, "pest_sunn_pest")
        assert entity is not None
        assert entity.name_ar == "حشرة السونة"
        assert entity.properties["severity"] == "high"

    @pytest.mark.unit
    def test_armyworm_exists(self, graph: AgriculturalKnowledgeGraph):
        """Test Fall Armyworm entity | دودة الحشد."""
        entity = _get_entity(graph, "pest_armyworm")
        assert entity is not None
        assert entity.properties.get("activity") == "nocturnal"

    @pytest.mark.unit
    def test_bollworm_exists(self, graph: AgriculturalKnowledgeGraph):
        """Test Cotton Bollworm entity | دودة اللوز."""
        entity = _get_entity(graph, "pest_bollworm")
        assert entity is not None
        assert entity.name_ar == "دودة اللوز"

    @pytest.mark.unit
    def test_nematode_exists(self, graph: AgriculturalKnowledgeGraph):
        """Test Root-Knot Nematode entity | نيماتودا."""
        entity = _get_entity(graph, "pest_nematode")
        assert entity is not None
        assert entity.properties["type"] == "nematode"

    @pytest.mark.unit
    def test_citrus_psyllid_is_reportable(self, graph: AgriculturalKnowledgeGraph):
        """Test Citrus Psyllid is a reportable pest (quarantine)."""
        entity = _get_entity(graph, "pest_citrus_psyllid")
        assert entity is not None
        assert entity.properties.get("reportable") is True
        assert entity.properties["severity"] == "critical"

    @pytest.mark.unit
    def test_fruit_fly_exists(self, graph: AgriculturalKnowledgeGraph):
        """Test Fruit Fly entity | ذبابة الفاكهة."""
        entity = _get_entity(graph, "pest_fruit_fly")
        assert entity is not None
        assert entity.properties.get("reportable") is True

    @pytest.mark.unit
    def test_all_pests_have_bilingual_names(self, graph: AgriculturalKnowledgeGraph):
        """Test all pests have Arabic names."""
        for e in graph.entities:
            if e.entity_type == "pest":
                assert e.name_ar, f"Pest {e.id} missing Arabic name"
                assert len(e.name_ar) > 0

    @pytest.mark.unit
    def test_pest_crop_relations_exist(self, graph: AgriculturalKnowledgeGraph):
        """Test new pests have 'affects' relations to crops."""
        new_pests = [
            "pest_sunn_pest",
            "pest_armyworm",
            "pest_thrips",
            "pest_bollworm",
            "pest_nematode",
            "pest_fruit_fly",
        ]
        for pest_id in new_pests:
            relations = _find_relations(graph, pest_id, "affects")
            assert len(relations) >= 1, f"Pest {pest_id} has no 'affects' relations"


# ═══════════════════════════════════════════════════════════════════════════════
# 3. Vector Transmission Relation Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestVectorTransmission:
    """Test pest → disease 'transmits' relations (vector transmission)."""

    @pytest.mark.unit
    def test_transmits_relation_type_exists(self, graph: AgriculturalKnowledgeGraph):
        """Test 'transmits' relation type is in the graph."""
        rel_types = {r.relation_type for r in graph.relations}
        assert "transmits" in rel_types, "Missing 'transmits' relation type"

    @pytest.mark.unit
    def test_whitefly_transmits_tylcv(self, graph: AgriculturalKnowledgeGraph):
        """Test whitefly → TYLCV vector transmission | الذبابة البيضاء تنقل TYLCV."""
        transmits = _find_relations(graph, "pest_whitefly", "transmits")
        targets = {r.target_id for r in transmits}
        assert "disease_tylcv" in targets, "Missing whitefly → TYLCV transmission"

    @pytest.mark.unit
    def test_whitefly_transmits_cotton_leaf_curl(self, graph: AgriculturalKnowledgeGraph):
        """Test whitefly → CLCuV vector transmission."""
        transmits = _find_relations(graph, "pest_whitefly", "transmits")
        targets = {r.target_id for r in transmits}
        assert "disease_cotton_leaf_curl" in targets

    @pytest.mark.unit
    def test_aphid_transmits_mosaic(self, graph: AgriculturalKnowledgeGraph):
        """Test aphid → mosaic virus transmission | المن ينقل الموزايك."""
        transmits = _find_relations(graph, "pest_aphid", "transmits")
        targets = {r.target_id for r in transmits}
        assert "disease_mosaic_virus" in targets

    @pytest.mark.unit
    def test_aphid_transmits_ctv(self, graph: AgriculturalKnowledgeGraph):
        """Test aphid → CTV transmission."""
        transmits = _find_relations(graph, "pest_aphid", "transmits")
        targets = {r.target_id for r in transmits}
        assert "disease_ctv" in targets

    @pytest.mark.unit
    def test_transmits_confidence_range(self, graph: AgriculturalKnowledgeGraph):
        """Test all transmits relations have valid confidence."""
        transmits = _relations_of_type(graph, "transmits")
        assert len(transmits) >= 4, f"Expected >= 4 transmits relations, got {len(transmits)}"
        for r in transmits:
            assert 0.5 <= r.confidence <= 1.0, f"Low confidence {r.confidence} for {r.source_id}→{r.target_id}"


# ═══════════════════════════════════════════════════════════════════════════════
# 4. Diagnosis Scenario Tests (End-to-End Graph Traversal)
# ═══════════════════════════════════════════════════════════════════════════════


class TestDiagnosisScenarios:
    """Simulate diagnosis scenarios via knowledge graph traversal."""

    @pytest.mark.unit
    def test_scenario_wheat_yellowing(self, graph: AgriculturalKnowledgeGraph):
        """Scenario: Wheat leaves yellowing → nitrogen deficiency.

        سيناريو: اصفرار أوراق القمح → نقص نيتروجين
        Path: crop_wheat ←[affects]← disease_nitrogen_deficiency
        """
        wheat_diseases = _find_reverse_relations(graph, "crop_wheat", "affects")
        disease_ids = {r.source_id for r in wheat_diseases}
        assert "disease_nitrogen_deficiency" in disease_ids, "Nitrogen deficiency should affect wheat"
        assert "disease_rust" in disease_ids, "Rust should also affect wheat (differential diagnosis)"

    @pytest.mark.unit
    def test_scenario_tomato_leaf_curl(self, graph: AgriculturalKnowledgeGraph):
        """Scenario: Tomato leaf curling → TYLCV → whitefly vector.

        سيناريو: تجعد أوراق الطماطم → TYLCV → الذبابة البيضاء
        Path: crop_tomato ←[affects]← disease_tylcv ←[transmits]← pest_whitefly
        """
        # Step 1: Find diseases affecting tomato
        tomato_diseases = _find_reverse_relations(graph, "crop_tomato", "affects")
        disease_ids = {r.source_id for r in tomato_diseases}
        assert "disease_tylcv" in disease_ids

        # Step 2: Find vector for TYLCV
        tylcv_vectors = _find_reverse_relations(graph, "disease_tylcv", "transmits")
        vector_ids = {r.source_id for r in tylcv_vectors}
        assert "pest_whitefly" in vector_ids

        # Step 3: Find treatment for vector
        whitefly_treatments = _find_reverse_relations(graph, "pest_whitefly", "treats")
        treatment_ids = {r.source_id for r in whitefly_treatments}
        assert "treat_imidacloprid" in treatment_ids

    @pytest.mark.unit
    def test_scenario_rpw_emergency(self, graph: AgriculturalKnowledgeGraph):
        """Scenario: Red Palm Weevil detection → emergency response.

        سيناريو: كشف سوسة النخيل الحمراء → استجابة طارئة
        Path: pest_rpw →[affects]→ crop_date_palm
              treat_emamectin →[treats]→ pest_rpw
        """
        rpw = _get_entity(graph, "pest_rpw")
        assert rpw is not None
        assert rpw.properties["severity"] == "critical"
        assert rpw.properties["response_window_hours"] == 48

        # Affects date palm
        affects = _find_relations(graph, "pest_rpw", "affects")
        crop_ids = {r.target_id for r in affects}
        assert "crop_date_palm" in crop_ids

        # Has treatment
        treatments = _find_reverse_relations(graph, "pest_rpw", "treats")
        assert len(treatments) >= 1, "RPW should have at least one treatment"

    @pytest.mark.unit
    def test_scenario_potato_multiple_diseases(self, graph: AgriculturalKnowledgeGraph):
        """Scenario: Potato has multiple disease threats.

        سيناريو: البطاطس عرضة لأمراض متعددة
        Path: crop_potato ← late_blight, bacterial_wilt, blackleg
        """
        potato_diseases = _find_reverse_relations(graph, "crop_potato", "affects")
        disease_ids = {r.source_id for r in potato_diseases}
        assert "disease_late_blight" in disease_ids, "Late blight should affect potato"
        assert "disease_bacterial_wilt" in disease_ids, "Bacterial wilt should affect potato"
        assert "disease_blackleg" in disease_ids, "Blackleg should affect potato"

    @pytest.mark.unit
    def test_scenario_copper_treats_bacterial(self, graph: AgriculturalKnowledgeGraph):
        """Scenario: Copper fungicide treats bacterial diseases.

        سيناريو: مبيدات النحاس تعالج الأمراض البكتيرية
        Path: treat_copper_fungicide →[treats]→ bacterial_blight, bacterial_canker, fire_blight
        """
        copper_treats = _find_relations(graph, "treat_copper_fungicide", "treats")
        treated_ids = {r.target_id for r in copper_treats}
        assert "disease_bacterial_blight" in treated_ids
        assert "disease_bacterial_canker" in treated_ids
        assert "disease_fire_blight" in treated_ids

    @pytest.mark.unit
    def test_scenario_sunn_pest_wheat(self, graph: AgriculturalKnowledgeGraph):
        """Scenario: Sunn Pest affects wheat in Middle East.

        سيناريو: حشرة السونة تصيب القمح في الشرق الأوسط
        """
        sunn_affects = _find_relations(graph, "pest_sunn_pest", "affects")
        crop_ids = {r.target_id for r in sunn_affects}
        assert "crop_wheat" in crop_ids
        assert "crop_barley" in crop_ids


# ═══════════════════════════════════════════════════════════════════════════════
# 5. Collection Populator Tests for Disease Files
# ═══════════════════════════════════════════════════════════════════════════════


class TestDiseaseDocsPopulation:
    """Test that new disease docs are discoverable by the populator."""

    @pytest.fixture
    def real_populator(self) -> KnowledgeBasePopulator:
        """Create a populator pointed at the actual knowledge base."""
        docs_path = Path(__file__).parent.parent.parent.parent / "docs" / "knowledge-base"
        if not docs_path.exists():
            pytest.skip("docs/knowledge-base not found")
        return KnowledgeBasePopulator(base_docs_path=docs_path)

    @pytest.mark.unit
    def test_pest_knowledge_collection_finds_disease_files(self, real_populator: KnowledgeBasePopulator):
        """Test that pest_knowledge collection discovers new disease files."""
        report = real_populator.populate_from_docs(
            collections=[PEST_KNOWLEDGE],
            dry_run=True,
        )
        assert report.total_files >= 5, (
            f"Expected >= 5 disease files (fungal, bacterial, viral, nutrient-deficiency, pests), "
            f"got {report.total_files}"
        )

    @pytest.mark.unit
    def test_bacterial_md_exists(self):
        """Test bacterial.md file exists in the knowledge base."""
        path = Path(__file__).parent.parent.parent.parent / "docs" / "knowledge-base" / "diseases" / "bacterial.md"
        assert path.exists(), "bacterial.md not found in diseases/"

    @pytest.mark.unit
    def test_viral_md_exists(self):
        """Test viral.md file exists in the knowledge base."""
        path = Path(__file__).parent.parent.parent.parent / "docs" / "knowledge-base" / "diseases" / "viral.md"
        assert path.exists(), "viral.md not found in diseases/"

    @pytest.mark.unit
    def test_nutrient_deficiency_md_exists(self):
        """Test nutrient-deficiency.md file exists in the knowledge base."""
        path = (
            Path(__file__).parent.parent.parent.parent
            / "docs"
            / "knowledge-base"
            / "diseases"
            / "nutrient-deficiency.md"
        )
        assert path.exists(), "nutrient-deficiency.md not found in diseases/"

    @pytest.mark.unit
    def test_disease_files_have_frontmatter(self):
        """Test all disease files have YAML frontmatter."""
        diseases_dir = Path(__file__).parent.parent.parent.parent / "docs" / "knowledge-base" / "diseases"
        if not diseases_dir.exists():
            pytest.skip("diseases dir not found")
        for md_file in diseases_dir.glob("*.md"):
            if md_file.name == "README.md":
                continue
            content = md_file.read_text(encoding="utf-8")
            assert content.startswith("---"), f"{md_file.name} missing YAML frontmatter"
            assert "title:" in content[:500], f"{md_file.name} missing title in frontmatter"

    @pytest.mark.unit
    def test_disease_files_are_bilingual(self):
        """Test new disease files contain Arabic content."""
        diseases_dir = Path(__file__).parent.parent.parent.parent / "docs" / "knowledge-base" / "diseases"
        if not diseases_dir.exists():
            pytest.skip("diseases dir not found")
        for filename in ["bacterial.md", "viral.md", "nutrient-deficiency.md"]:
            content = (diseases_dir / filename).read_text(encoding="utf-8")
            # Check for Arabic characters
            has_arabic = any("\u0600" <= c <= "\u06ff" for c in content)
            assert has_arabic, f"{filename} has no Arabic content"
