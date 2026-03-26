"""
Cross-module interaction tests for the knowledge base system.
Tests that modules work correctly together (not just individually).
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestKnowledgePersistenceIntegration:
    """Test that knowledge models work with persistence layer."""

    def test_store_and_retrieve_crop_document(self):
        """CropKnowledgeDocument can be stored and retrieved via InMemoryKnowledgeRepository."""
        try:
            from shared.ai.knowledge.models import CropKnowledgeDocument, KnowledgeDomain
            from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        repo = InMemoryKnowledgeRepository()
        doc = CropKnowledgeDocument(
            domain=KnowledgeDomain.CROPS,
            title="Wheat Cultivation Guide",
            title_ar="دليل زراعة القمح",
            content="Wheat requires well-drained soil and adequate moisture.",
            content_ar="يحتاج القمح إلى تربة جيدة الصرف ورطوبة كافية.",
        )

        repo.save(doc)
        retrieved = repo.get_by_id(doc.id)
        assert retrieved is not None
        assert retrieved.title == "Wheat Cultivation Guide"
        assert retrieved.title_ar == "دليل زراعة القمح"

    def test_store_multiple_documents_and_query(self):
        """Multiple documents can be stored and queried by domain."""
        try:
            from shared.ai.knowledge.models import CropKnowledgeDocument, KnowledgeDomain
            from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        repo = InMemoryKnowledgeRepository()

        for i in range(5):
            doc = CropKnowledgeDocument(
                domain=KnowledgeDomain.CROPS,
                title=f"Crop Document {i}",
                content=f"Content for crop document {i}",
            )
            repo.save(doc)

        from shared.ai.knowledge.persistence import DocumentQuery

        query = DocumentQuery(domain=KnowledgeDomain.CROPS)
        page = repo.find(query)
        assert len(page.items) == 5, f"Expected exactly 5 documents, got {len(page.items)}"
        # Verify all stored documents are present with correct titles
        stored_titles = {item.title for item in page.items}
        for i in range(5):
            assert f"Crop Document {i}" in stored_titles, f"Missing 'Crop Document {i}' in results"


@pytest.mark.unit
class TestKnowledgeValidationIntegration:
    """Test that validators work with actual knowledge documents."""

    def test_validate_valid_crop_document(self):
        """Valid crop document should pass validation."""
        try:
            from shared.ai.knowledge.models import CropKnowledgeDocument, KnowledgeDomain
            from shared.ai.knowledge.validators import KnowledgeValidator
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        validator = KnowledgeValidator()
        doc = CropKnowledgeDocument(
            domain=KnowledgeDomain.CROPS,
            title="Valid Wheat Document",
            title_ar="وثيقة قمح صالحة",
            content="Detailed information about wheat cultivation in arid regions.",
            content_ar="معلومات مفصلة عن زراعة القمح في المناطق الجافة.",
        )

        result = validator.validate(doc)
        assert result.is_valid, f"Valid document failed validation: {result.issues}"

    def test_validate_minimal_document(self):
        """Document with minimal content should generate warnings."""
        try:
            from shared.ai.knowledge.models import CropKnowledgeDocument, KnowledgeDomain
            from shared.ai.knowledge.validators import KnowledgeValidator
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        validator = KnowledgeValidator()
        doc = CropKnowledgeDocument(
            domain=KnowledgeDomain.CROPS,
            title="X",
            content="Y",
        )

        result = validator.validate(doc)
        assert isinstance(result.issues, list)
        # A minimal document (single-char title/content, no Arabic) should produce warnings
        assert len(result.issues) > 0, "Minimal document should generate validation warnings"
        warning_fields = [issue.field for issue in result.issues]
        assert len(warning_fields) > 0, "Expected at least one field flagged"


@pytest.mark.unit
class TestKnowledgeCacheIntegration:
    """Test cache with actual knowledge data patterns."""

    def test_cache_knowledge_query_result(self):
        """Cache should handle serialized knowledge query results."""
        try:
            from shared.ai.knowledge.cache import KnowledgeCache
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        cache = KnowledgeCache()
        query_result = {
            "query": "wheat irrigation schedule",
            "results": [
                {"doc_id": "crop-001", "score": 0.92, "title": "Wheat Irrigation"},
                {"doc_id": "crop-002", "score": 0.85, "title": "Wheat Water Needs"},
            ],
            "total": 2,
        }

        cache.put("query:wheat_irrigation", query_result)
        retrieved = cache.get("query:wheat_irrigation")
        assert retrieved is not None, "Cache should return the stored query result"
        assert retrieved["query"] == "wheat irrigation schedule"
        assert retrieved["total"] == 2
        assert len(retrieved["results"]) == 2
        assert retrieved["results"][0]["doc_id"] == "crop-001"
        assert retrieved["results"][0]["score"] == 0.92
        assert retrieved["results"][0]["title"] == "Wheat Irrigation"
        assert retrieved["results"][1]["doc_id"] == "crop-002"
        assert retrieved["results"][1]["score"] == 0.85
        assert retrieved["results"][1]["title"] == "Wheat Water Needs"


@pytest.mark.unit
class TestQualityGateIntegration:
    """Test quality gate with actual knowledge documents."""

    def test_quality_check_on_crop_document(self):
        """Quality gate should check document quality dimensions."""
        try:
            from shared.ai.knowledge.models import CropKnowledgeDocument, KnowledgeDomain
            from shared.ai.knowledge.quality_gate import KnowledgeQualityGate
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        gate = KnowledgeQualityGate()
        doc = CropKnowledgeDocument(
            domain=KnowledgeDomain.CROPS,
            title="High Quality Wheat Document",
            title_ar="وثيقة قمح عالية الجودة",
            content="Comprehensive guide to wheat cultivation including soil preparation, "
            "seed selection, irrigation scheduling, and pest management strategies "
            "for arid and semi-arid regions of the Middle East.",
            content_ar="دليل شامل لزراعة القمح يتضمن تحضير التربة واختيار البذور "
            "وجدولة الري واستراتيجيات إدارة الآفات للمناطق الجافة وشبه الجافة "
            "في الشرق الأوسط.",
        )

        # gate.check expects a list of documents
        result = gate.check([doc])
        assert isinstance(result.checks, list), "QualityCheckResult should contain a list of checks"
        assert len(result.checks) > 0, "Quality gate should run at least one sub-check"
        assert 0.0 <= result.score <= 1.0, f"Score should be between 0 and 1, got {result.score}"
        # Verify each check has the expected structure
        for check in result.checks:
            assert "name" in check, "Each check should have a 'name' key"
            assert "passed" in check, "Each check should have a 'passed' key"
            assert "score" in check, "Each check should have a 'score' key"


@pytest.mark.unit
class TestSerializationIntegration:
    """Test serialization with actual knowledge documents."""

    def test_serialize_and_deserialize_document(self):
        """Document should survive JSON round-trip."""
        try:
            from shared.ai.knowledge.models import CropKnowledgeDocument, KnowledgeDomain
            from shared.ai.knowledge.serialization import KnowledgeSerializer
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        serializer = KnowledgeSerializer()
        doc = CropKnowledgeDocument(
            domain=KnowledgeDomain.CROPS,
            title="Serialization Test",
            content="Testing serialization round-trip.",
        )

        exported = serializer.export_to_dict([doc])
        assert "manifest" in exported, "Exported dict should contain 'manifest'"
        assert "documents" in exported, "Exported dict should contain 'documents'"
        assert exported["manifest"]["total_documents"] == 1
        assert "crops" in exported["manifest"]["domains"]

        docs_imported, result = serializer.import_from_dict(exported)
        assert len(docs_imported) == 1, f"Expected 1 imported doc, got {len(docs_imported)}"
        assert docs_imported[0].title == doc.title
        assert docs_imported[0].content == doc.content
        assert docs_imported[0].domain == doc.domain
        assert result.imported == 1
        assert result.errors == []


@pytest.mark.unit
class TestVersioningIntegration:
    """Test document versioning."""

    def test_version_tracking(self):
        """DocumentVersionManager should track changes."""
        try:
            from shared.ai.knowledge.models import CropKnowledgeDocument, KnowledgeDomain
            from shared.ai.knowledge.versioning import DocumentVersionManager
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        manager = DocumentVersionManager()
        doc = CropKnowledgeDocument(
            domain=KnowledgeDomain.CROPS,
            title="Version 1",
            content="Original content.",
        )

        version_id = manager.track(doc)
        assert isinstance(version_id, str), "track() should return a version string"
        assert version_id == "1.0.0", f"First version should be '1.0.0', got '{version_id}'"

        history = manager.get_history(doc.id)
        assert len(history) == 1, f"Expected exactly 1 version in history, got {len(history)}"
        assert history[0].version == "1.0.0"
        assert history[0].data["title"] == "Version 1"
        assert history[0].data["content"] == "Original content."


@pytest.mark.unit
class TestFreshnessMonitorIntegration:
    """Test freshness monitoring with actual documents."""

    def test_freshness_check(self):
        """FreshnessMonitor should assess document freshness."""
        try:
            from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
            from shared.ai.knowledge.models import CropKnowledgeDocument, KnowledgeDomain
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        monitor = KnowledgeFreshnessMonitor()
        doc = CropKnowledgeDocument(
            domain=KnowledgeDomain.CROPS,
            title="Freshness Test",
            content="Test content for freshness monitoring.",
        )

        # check_single returns None when the document has no expiration_date set
        report = monitor.check_single(doc)
        assert report is None, (
            "Document without expiration_date should return None from check_single, "
            f"got {report}"
        )

        # Now test with an expired document to verify non-None path
        from datetime import date

        expired_doc = CropKnowledgeDocument(
            domain=KnowledgeDomain.CROPS,
            title="Expired Doc",
            content="Expired content.",
        )
        expired_doc.fresh.expiration_date = date(2020, 1, 1)

        alert = monitor.check_single(expired_doc)
        assert alert is not None, "Expired document should produce a FreshnessAlert"
        assert alert.severity == "expired"
        assert alert.days_until_expiry is not None and alert.days_until_expiry < 0


@pytest.mark.unit
class TestGraphBuilderIntegration:
    """Test knowledge graph builder."""

    def test_build_agricultural_graph(self):
        """build_agricultural_knowledge_graph should create a non-empty graph."""
        try:
            from shared.ai.knowledge.graph_builder import build_agricultural_knowledge_graph
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        graph = build_agricultural_knowledge_graph()
        assert graph is not None, "build_agricultural_knowledge_graph() should return a graph object"
        assert len(graph.entities) > 0, "Graph should contain entities"
        assert len(graph.relations) > 0, "Graph should contain relations"
        # Verify entities have required structure
        for entity in graph.entities:
            assert hasattr(entity, "entity_type"), "Each entity should have an entity_type"
            assert hasattr(entity, "name"), "Each entity should have a name"
            assert entity.name, f"Entity name should be non-empty, got: {entity.name!r}"
        # Verify relations have required attributes
        for relation in graph.relations:
            assert hasattr(relation, "source_id"), "Each relation should have a source_id"
            assert hasattr(relation, "target_id"), "Each relation should have a target_id"
            assert hasattr(relation, "relation_type"), "Each relation should have a relation_type"

    def test_graph_has_crop_entities(self):
        """Graph should contain crop-related entities."""
        try:
            from shared.ai.knowledge.graph_builder import build_agricultural_knowledge_graph
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        graph = build_agricultural_knowledge_graph()
        entity_types = {e.entity_type for e in graph.entities}
        assert len(entity_types) >= 2, f"Graph should have diverse entity types, got: {entity_types}"
        # Agricultural graph should include crop-related entity types
        entity_type_lower = {t.lower() for t in entity_types}
        has_crop_related = any(
            keyword in t for t in entity_type_lower
            for keyword in ("crop", "plant", "disease", "pest", "soil", "irrigation")
        )
        assert has_crop_related, (
            f"Graph should contain at least one agricultural entity type "
            f"(crop, plant, disease, pest, soil, irrigation), got: {entity_types}"
        )


@pytest.mark.unit
class TestCorrectiveRetrievalIntegration:
    """Test CRAG engine integration."""

    def test_crag_engine_instantiation(self):
        """CorrectiveRetrievalEngine should instantiate."""
        try:
            from shared.ai.knowledge.corrective_retrieval import CorrectiveRetrievalEngine
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        engine = CorrectiveRetrievalEngine()
        assert hasattr(engine, "CORRECT_THRESHOLD"), "Engine should have CORRECT_THRESHOLD"
        assert hasattr(engine, "AMBIGUOUS_THRESHOLD"), "Engine should have AMBIGUOUS_THRESHOLD"
        assert engine.CORRECT_THRESHOLD > engine.AMBIGUOUS_THRESHOLD, (
            "CORRECT_THRESHOLD should be higher than AMBIGUOUS_THRESHOLD"
        )

    def test_retrieval_action_values(self):
        """RetrievalAction should have CORRECT, AMBIGUOUS, INCORRECT."""
        try:
            from shared.ai.knowledge.corrective_retrieval import RetrievalAction
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        values = {a.value for a in RetrievalAction}
        assert len(values) >= 3, f"RetrievalAction should have 3+ values, got: {values}"


@pytest.mark.unit
class TestPivotManagementIntegration:
    """Test pivot management geometry and VRI conversion together."""

    def test_geometry_to_vri_pipeline(self):
        """PivotGeometry → VRI prescription should work end-to-end."""
        try:
            from shared.pivot_management.geometry import create_pivot_zone_grid
            from shared.pivot_management.vri_converter import ndvi_to_vri_prescription
        except ImportError as e:
            pytest.skip(f"Missing dependency: {e}")

        grid = create_pivot_zone_grid(
            pivot_id="test-pivot-001",
            center_lon=46.7,
            center_lat=24.7,
            radius_m=400.0,
            span_count=4,
            angular_divisions=6,
        )
        assert len(grid.zones) > 0, "Grid should contain zones"
        # Verify grid dimensions match the requested parameters
        expected_zone_count = 4 * 6  # span_count * angular_divisions
        assert len(grid.zones) == expected_zone_count, (
            f"Expected {expected_zone_count} zones (4 spans x 6 angles), got {len(grid.zones)}"
        )

        ndvi_data = [[0.5 + (r * 0.05) + (c * 0.01) for c in range(10)] for r in range(10)]
        ndvi_bounds = (46.695, 24.695, 46.705, 24.705)
        prescription = ndvi_to_vri_prescription(
            pivot_id="test-pivot-001",
            zone_grid=grid,
            ndvi_data=ndvi_data,
            ndvi_bounds=ndvi_bounds,
        )
        assert len(prescription.zones) > 0, "Prescription should contain VRI zones"
        assert prescription.pivot_id == "test-pivot-001"
        assert prescription.source_type == "ndvi", (
            f"Source type should be 'ndvi', got '{prescription.source_type}'"
        )
        # Each zone should have a valid application rate
        for zone in prescription.zones:
            assert 0.0 <= zone.application_rate_percent <= 150.0, (
                f"Zone {zone.zone_id} rate {zone.application_rate_percent}% out of range"
            )
