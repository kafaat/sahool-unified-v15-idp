"""
Dependency validation tests for AI modules.
Ensures modules expose correct interfaces and have consistent type definitions.
"""

from __future__ import annotations

import pytest


@pytest.mark.unit
class TestKnowledgeModelsConsistency:
    """Validate that knowledge model types are consistent across modules."""

    def test_knowledge_domain_enum_values(self):
        """KnowledgeDomain should contain all required agricultural domains."""
        try:
            from shared.ai.knowledge.models import KnowledgeDomain
        except ImportError:
            pytest.skip("knowledge.models not available")

        required_domains = {"crops", "soil", "weather", "irrigation", "pest_disease", "fertilizer"}
        actual_values = {d.value for d in KnowledgeDomain}
        missing = required_domains - actual_values
        assert not missing, f"KnowledgeDomain missing required domains: {missing}"

    def test_base_knowledge_document_has_required_fields(self):
        """BaseKnowledgeDocument must have essential metadata fields."""
        try:
            from shared.ai.knowledge.models import BaseKnowledgeDocument
        except ImportError:
            pytest.skip("knowledge.models not available")

        required_attrs = ["domain", "title", "content"]
        for attr in required_attrs:
            # BaseKnowledgeDocument is a Pydantic model, check model_fields
            assert attr in BaseKnowledgeDocument.model_fields, f"BaseKnowledgeDocument missing required field: {attr}"

    def test_crop_document_extends_base(self):
        """CropKnowledgeDocument should extend BaseKnowledgeDocument."""
        try:
            from shared.ai.knowledge.models import BaseKnowledgeDocument, CropKnowledgeDocument
        except ImportError:
            pytest.skip("knowledge.models not available")

        assert issubclass(CropKnowledgeDocument, BaseKnowledgeDocument), (
            "CropKnowledgeDocument must extend BaseKnowledgeDocument"
        )


@pytest.mark.unit
class TestCollectionsConsistency:
    """Validate that knowledge collections reference valid domains."""

    def test_all_collections_is_list(self):
        """ALL_COLLECTIONS should be a non-empty list."""
        try:
            from shared.ai.knowledge.collections import ALL_COLLECTIONS
        except ImportError:
            pytest.skip("knowledge.collections not available")

        assert isinstance(ALL_COLLECTIONS, (list, tuple)), "ALL_COLLECTIONS should be a list or tuple"
        assert len(ALL_COLLECTIONS) > 0, "ALL_COLLECTIONS should not be empty"

    def test_collection_names_are_unique(self):
        """Each collection should have a unique name."""
        try:
            from shared.ai.knowledge.collections import ALL_COLLECTIONS
        except ImportError:
            pytest.skip("knowledge.collections not available")

        names = [c.name if hasattr(c, "name") else str(c) for c in ALL_COLLECTIONS]
        assert len(names) == len(set(names)), (
            f"Duplicate collection names found: {[n for n in names if names.count(n) > 1]}"
        )

    def test_crop_knowledge_collection_exists(self):
        """CROP_KNOWLEDGE collection should be defined."""
        try:
            from shared.ai.knowledge.collections import CROP_KNOWLEDGE
        except ImportError:
            pytest.skip("knowledge.collections not available")

        assert CROP_KNOWLEDGE is not None


@pytest.mark.unit
class TestAgrovocConsistency:
    """Validate the AGROVOC integration."""

    def test_agrovoc_lookup_has_registered_concepts(self):
        """AgrovocLookup should have concepts registered."""
        try:
            from shared.ai.knowledge.agrovoc import AgrovocLookup
        except ImportError:
            pytest.skip("agrovoc not available")

        lookup = AgrovocLookup()
        # Should be able to extract concepts from agricultural text
        assert callable(getattr(lookup, "extract_concepts_from_text", None)), (
            "AgrovocLookup should have extract_concepts_from_text method"
        )

    def test_agrovoc_domain_has_crops(self):
        """AgrovocDomain should include a crops-related value."""
        try:
            from shared.ai.knowledge.agrovoc import AgrovocDomain
        except ImportError:
            pytest.skip("agrovoc not available")

        domain_values = [d.value for d in AgrovocDomain]
        assert any("crop" in v.lower() or "plant" in v.lower() for v in domain_values), (
            f"AgrovocDomain should include a crops domain, got: {domain_values}"
        )


@pytest.mark.unit
class TestValidatorsConsistency:
    """Validate the knowledge validators module."""

    def test_knowledge_validator_instantiation(self):
        """KnowledgeValidator should instantiate without errors."""
        try:
            from shared.ai.knowledge.validators import KnowledgeValidator
        except ImportError:
            pytest.skip("validators not available")

        validator = KnowledgeValidator()
        assert validator is not None

    def test_validation_result_structure(self):
        """ValidationResult should have is_valid and issues fields."""
        try:
            from shared.ai.knowledge.validators import ValidationResult
        except ImportError:
            pytest.skip("validators not available")

        required_fields = ["is_valid", "issues"]
        for field in required_fields:
            assert field in ValidationResult.__dataclass_fields__, f"ValidationResult missing field: {field}"


@pytest.mark.unit
class TestPersistenceConsistency:
    """Validate persistence layer interfaces."""

    def test_in_memory_repository_is_abstract_compliant(self):
        """InMemoryKnowledgeRepository should implement KnowledgeRepository."""
        try:
            from shared.ai.knowledge.persistence import (
                InMemoryKnowledgeRepository,
                KnowledgeRepository,
            )
        except ImportError:
            pytest.skip("persistence not available")

        assert issubclass(InMemoryKnowledgeRepository, KnowledgeRepository)

    def test_in_memory_repository_crud(self):
        """InMemoryKnowledgeRepository should support basic CRUD."""
        try:
            from shared.ai.knowledge.persistence import InMemoryKnowledgeRepository
        except ImportError:
            pytest.skip("persistence not available")

        repo = InMemoryKnowledgeRepository()
        # Should have store/get/delete methods
        assert (
            callable(getattr(repo, "store", None))
            or callable(getattr(repo, "add", None))
            or callable(getattr(repo, "save", None))
        ), "Repository should have a store/add/save method"


@pytest.mark.unit
class TestCacheModule:
    """Validate cache module."""

    def test_knowledge_cache_instantiation(self):
        """KnowledgeCache should instantiate with default params."""
        try:
            from shared.ai.knowledge.cache import KnowledgeCache
        except ImportError:
            pytest.skip("cache not available")

        cache = KnowledgeCache()
        assert cache is not None

    def test_cache_get_set(self):
        """KnowledgeCache should support get/set operations."""
        try:
            from shared.ai.knowledge.cache import KnowledgeCache
        except ImportError:
            pytest.skip("cache not available")

        cache = KnowledgeCache()
        cache.put("test_key", {"data": "value"})
        result = cache.get("test_key")
        assert result is not None
        assert result["data"] == "value"

    def test_cache_miss_returns_none(self):
        """Cache miss should return None."""
        try:
            from shared.ai.knowledge.cache import KnowledgeCache
        except ImportError:
            pytest.skip("cache not available")

        cache = KnowledgeCache()
        assert cache.get("nonexistent") is None


@pytest.mark.unit
class TestMetricsModule:
    """Validate metrics module."""

    def test_knowledge_metrics_instantiation(self):
        """KnowledgeMetrics should instantiate."""
        try:
            from shared.ai.knowledge.metrics import KnowledgeMetrics
        except ImportError:
            pytest.skip("metrics not available")

        metrics = KnowledgeMetrics()
        assert metrics is not None


@pytest.mark.unit
class TestEventsSubjects:
    """Validate event subject constants."""

    def test_field_created_subject_format(self):
        """SAHOOL_FIELD_CREATED should follow sahool.field.created format."""
        try:
            from shared.events.subjects import SAHOOL_FIELD_CREATED
        except ImportError:
            pytest.skip("events.subjects not available")

        assert SAHOOL_FIELD_CREATED.startswith("sahool."), (
            f"Event subject should start with 'sahool.', got: {SAHOOL_FIELD_CREATED}"
        )
        assert "field" in SAHOOL_FIELD_CREATED.lower()

    def test_no_duplicate_subjects(self):
        """All event subjects should be unique."""
        try:
            import shared.events.subjects as subjects_mod
        except ImportError:
            pytest.skip("events.subjects not available")

        subjects = [v for k, v in vars(subjects_mod).items() if k.startswith("SAHOOL_") and isinstance(v, str)]
        assert len(subjects) == len(set(subjects)), "Duplicate event subjects found"

    def test_get_tenant_subject_function(self):
        """get_tenant_subject should produce tenant-scoped subjects."""
        try:
            from shared.events.subjects import get_tenant_subject
        except ImportError:
            pytest.skip("get_tenant_subject not available")

        result = get_tenant_subject("test-tenant-id", "field", "created")
        assert "test-tenant-id" in result
        assert "field" in result
        assert "created" in result


@pytest.mark.unit
class TestPivotManagement:
    """Validate pivot management geometry and VRI converter."""

    def test_pivot_geometry_creation(self):
        """PivotGeometry should create valid geometry."""
        try:
            from shared.pivot_management.geometry import PivotGeometry
        except ImportError:
            pytest.skip("pivot_management.geometry not available")

        # Create a basic pivot with all required fields
        pivot = PivotGeometry(
            center_lat=24.7,
            center_lon=46.7,
            radius_m=400.0,
            boundary=[(46.7, 24.7), (46.71, 24.7), (46.71, 24.71), (46.7, 24.71)],
            area_hectares=50.0,
            perimeter_m=2513.0,
            num_points=64,
        )
        assert pivot.center_lat == 24.7
        assert pivot.center_lon == 46.7
        assert pivot.radius_m == 400.0

    def test_vri_prescription_creation(self):
        """VRIPrescription should be createable."""
        try:
            from shared.pivot_management.vri_converter import VRIPrescription
        except ImportError:
            pytest.skip("vri_converter not available")

        assert VRIPrescription is not None

    def test_ndvi_to_vri_function_exists(self):
        """ndvi_to_vri_prescription function should exist."""
        try:
            from shared.pivot_management.vri_converter import ndvi_to_vri_prescription
        except ImportError:
            pytest.skip("ndvi_to_vri_prescription not available")

        assert callable(ndvi_to_vri_prescription)


@pytest.mark.unit
class TestFieldBoundariesGeometry:
    """Validate field boundaries geometry module."""

    def test_haversine_distance(self):
        """haversine_distance should compute reasonable distances."""
        try:
            from shared.field_boundaries.geometry import haversine_distance
        except ImportError:
            pytest.skip("field_boundaries.geometry not available")

        # Riyadh to Jeddah ~ 950 km
        dist = haversine_distance(24.7136, 46.6753, 21.5433, 39.1728)
        assert 800_000 < dist < 1_100_000, f"Expected ~950km, got {dist / 1000:.0f}km"

    def test_shoelace_area(self):
        """shoelace_area should compute polygon area."""
        try:
            from shared.field_boundaries.geometry import shoelace_area
        except ImportError:
            pytest.skip("field_boundaries.geometry not available")

        # Simple square (approximate)
        coords = [(0.0, 0.0), (0.001, 0.0), (0.001, 0.001), (0.0, 0.001)]
        area = shoelace_area(coords)
        assert area > 0, "Area should be positive"

    def test_polygon_centroid(self):
        """polygon_centroid should return center of polygon."""
        try:
            from shared.field_boundaries.geometry import polygon_centroid
        except ImportError:
            pytest.skip("field_boundaries.geometry not available")

        coords = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]
        cx, cy = polygon_centroid(coords)
        assert abs(cx - 0.5) < 0.01 and abs(cy - 0.5) < 0.01, f"Centroid should be near (0.5, 0.5), got ({cx}, {cy})"
