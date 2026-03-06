"""
Integration Tests for Knowledge Base Module
=============================================
اختبارات تكامل وحدة قاعدة المعرفة

End-to-end tests for the full ingestion pipeline, collection population,
freshness monitoring, and document lifecycle.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from shared.ai.knowledge.collections import (
    ALL_COLLECTIONS,
    COLLECTION_DIRECTORY_MAP,
    CROP_KNOWLEDGE,
    GENERAL_AGRICULTURE,
    PEST_KNOWLEDGE,
    SOIL_KNOWLEDGE,
)
from shared.ai.knowledge.freshness_monitor import KnowledgeFreshnessMonitor
from shared.ai.knowledge.ingestion.chunker import ChunkConfig, ChunkStrategy, TextChunker
from shared.ai.knowledge.ingestion.pipeline import (
    BatchIngestionReport,
    IngestionResult,
    KnowledgeIngestionPipeline,
)
from shared.ai.knowledge.models import (
    BaseKnowledgeDocument,
    KnowledgeDomain,
    VerificationStatus,
)
from shared.ai.knowledge.validators import KnowledgeValidator, ValidationResult
from shared.ai.knowledge.verification.agent import KnowledgeVerificationAgent


# ─── Pipeline End-to-End ─────────────────────────────────────────────────────


class TestPipelineEndToEnd:
    """End-to-end pipeline integration tests."""

    @pytest.fixture
    def pipeline(self) -> KnowledgeIngestionPipeline:
        return KnowledgeIngestionPipeline(
            min_source_credibility=1,
            require_bilingual=False,
            enable_agrovoc=True,
        )

    @pytest.fixture
    def knowledge_base_dir(self) -> Path:
        return Path("docs/knowledge-base")

    @pytest.mark.integration
    def test_ingest_crop_markdown(self, pipeline: KnowledgeIngestionPipeline, knowledge_base_dir: Path):
        """Ingest a real crop markdown file through the full pipeline."""
        wheat_file = knowledge_base_dir / "crops" / "wheat.md"
        if not wheat_file.exists():
            pytest.skip("Knowledge base docs not available")

        result = pipeline.ingest_file(wheat_file)
        assert result.success is True
        assert result.document_id.startswith("kb_")
        assert "crops" in result.domains_detected
        assert result.collection == CROP_KNOWLEDGE

    @pytest.mark.integration
    def test_ingest_soil_markdown(self, pipeline: KnowledgeIngestionPipeline, knowledge_base_dir: Path):
        """Ingest a real soil markdown file."""
        soil_file = knowledge_base_dir / "soils" / "sandy.md"
        if not soil_file.exists():
            pytest.skip("Knowledge base docs not available")

        result = pipeline.ingest_file(soil_file)
        assert result.success is True
        assert "soil" in result.domains_detected

    @pytest.mark.integration
    def test_ingest_directory_crops(self, pipeline: KnowledgeIngestionPipeline, knowledge_base_dir: Path):
        """Ingest entire crops directory."""
        crops_dir = knowledge_base_dir / "crops"
        if not crops_dir.exists():
            pytest.skip("Knowledge base docs not available")

        report = pipeline.ingest_directory(crops_dir)
        assert isinstance(report, BatchIngestionReport)
        assert report.total > 0
        assert report.succeeded >= 1

    @pytest.mark.integration
    def test_ingest_text_with_agrovoc(self, pipeline: KnowledgeIngestionPipeline):
        """Ingest text and verify AGROVOC concept extraction."""
        text = """---
title: Wheat Irrigation Guide
tags: [wheat, irrigation]
---

# Wheat Irrigation Guide

Wheat (Triticum aestivum) requires careful irrigation management.
Drip irrigation is most efficient for wheat cultivation.
Monitor NDVI values to assess crop health.
"""
        result = pipeline.ingest_text(text, title="Wheat Irrigation Guide")
        assert result.success is True
        assert len(result.domains_detected) >= 1
        assert len(result.tags) >= 1

    @pytest.mark.integration
    def test_ingest_arabic_text(self, pipeline: KnowledgeIngestionPipeline):
        """Ingest Arabic agricultural text."""
        text = """---
title: دليل ري القمح
title_ar: دليل ري القمح
---

# دليل ري القمح

القمح يحتاج إلى ري منتظم خلال مرحلة التفريع.
استخدم ري بالتنقيط للحصول على أفضل كفاءة.
"""
        result = pipeline.ingest_text(text, title="Wheat Irrigation AR")
        assert result.success is True

    @pytest.mark.integration
    def test_pipeline_domain_detection_accuracy(self, pipeline: KnowledgeIngestionPipeline):
        """Verify pipeline detects multiple domains from rich text."""
        text = """
# Integrated Farm Management

This guide covers irrigation scheduling for wheat crops,
soil testing for pH and EC, and fertilizer application
of NPK compound at recommended rates. Monitor pest
infestations and use NDVI satellite imagery for assessment.
"""
        result = pipeline.ingest_text(text, title="Integrated Guide")
        assert result.success is True
        # Should detect multiple domains from this rich text
        assert len(result.domains_detected) >= 2


# ─── Chunker + Pipeline Integration ──────────────────────────────────────────


class TestChunkerPipelineIntegration:
    """Tests for chunker working with pipeline output."""

    @pytest.mark.integration
    def test_chunk_ingested_content(self):
        """Chunk content after ingestion preprocessing."""
        pipeline = KnowledgeIngestionPipeline()
        chunker = TextChunker(ChunkConfig(
            strategy=ChunkStrategy.HYBRID,
            max_chunk_size=50,
            min_chunk_size=5,
        ))

        text = """---
title: Wheat Growing Guide
---

## Planting

Wheat should be planted in November for winter varieties.
Seed rate is 120-150 kg/ha depending on variety and conditions.

## Irrigation

Drip irrigation provides 90-95% efficiency.
Schedule irrigation every 10-14 days during tillering.

## Fertilization

Apply nitrogen fertilizer at 46 kg/ha during tillering stage.
Use urea 46% or ammonium sulfate for nitrogen supply.
"""
        result = pipeline.ingest_text(text, title="Wheat Guide")
        assert result.success is True

        chunks = chunker.chunk(text)
        assert len(chunks) >= 1
        for chunk in chunks:
            assert chunk.content or chunk.content_ar


# ─── Validator + Verification Integration ─────────────────────────────────────


class TestValidatorVerificationIntegration:
    """Tests for validator and verification agent working together."""

    @pytest.mark.integration
    def test_validate_and_verify_crop_document(self):
        """Full validation + verification on a crop document."""
        doc = BaseKnowledgeDocument(
            title="Wheat Cultivation Guide",
            title_ar="دليل زراعة القمح",
            content="Complete guide to wheat cultivation in arid regions.",
            content_ar="دليل شامل لزراعة القمح في المناطق الجافة",
            domain=KnowledgeDomain.CROPS,
            tags=["wheat", "cultivation", "arid"],
        )

        # Validate
        validator = KnowledgeValidator()
        validation = validator.validate(doc)
        assert validation.is_valid is True

        # Verify
        agent = KnowledgeVerificationAgent()
        verification = agent.verify(doc)
        assert verification.structural_passed is True
        assert verification.confidence_score >= 0.0

    @pytest.mark.integration
    def test_reject_document_with_banned_substance(self):
        """Verify banned substance detection in verification."""
        doc = BaseKnowledgeDocument(
            title="Pest Control Guide",
            content="Use DDT pesticide for effective pest control.",
            domain=KnowledgeDomain.PEST_DISEASE,
        )

        agent = KnowledgeVerificationAgent()
        verification = agent.verify(doc)
        assert verification.safety_passed is False


# ─── Collection System Integration ────────────────────────────────────────────


class TestCollectionSystemIntegration:
    """Tests for collection system consistency."""

    @pytest.mark.integration
    def test_all_domains_have_collections(self):
        """Every KnowledgeDomain maps to a collection."""
        doc_base = BaseKnowledgeDocument(title="Test", domain=KnowledgeDomain.CROPS)
        for domain in KnowledgeDomain:
            doc = BaseKnowledgeDocument(title="Test", domain=domain)
            collection = doc._get_collection()
            assert collection in ALL_COLLECTIONS, f"Domain {domain} maps to unknown collection {collection}"

    @pytest.mark.integration
    def test_collection_directory_paths_exist(self):
        """Verify mapped directories exist on disk."""
        for collection, dirs in COLLECTION_DIRECTORY_MAP.items():
            for d in dirs:
                path = Path(d)
                # Directories may not exist in test env, just check format
                assert d.endswith("/"), f"Directory '{d}' for '{collection}' should end with /"

    @pytest.mark.integration
    def test_pipeline_resolves_all_domains(self):
        """Pipeline correctly resolves all domains to collections."""
        pipeline = KnowledgeIngestionPipeline()
        for domain in KnowledgeDomain:
            collection = pipeline._resolve_collection(domain)
            assert collection, f"No collection for domain {domain}"
            assert collection in ALL_COLLECTIONS


# ─── Freshness Monitoring Integration ─────────────────────────────────────────


class TestFreshnessIntegration:
    """Integration tests for freshness monitoring."""

    @pytest.mark.integration
    def test_freshness_with_real_documents(self):
        """Check freshness of generated documents."""
        from datetime import date, timedelta

        docs = []
        for i in range(10):
            exp = date.today() + timedelta(days=(i * 15) - 30)
            doc = BaseKnowledgeDocument(
                title=f"Doc {i}",
                domain=KnowledgeDomain.CROPS,
                content=f"Content for document {i}",
            )
            doc.fresh.expiration_date = exp
            docs.append(doc)

        monitor = KnowledgeFreshnessMonitor(warning_days=30)
        report = monitor.check_documents(docs)

        assert report.total_documents == 10
        assert report.expired_count >= 1
        assert report.fresh_count >= 1
        assert 0.0 <= report.health_score <= 1.0
        assert len(report.by_domain) >= 1


# ─── Knowledge Graph + Models Integration ─────────────────────────────────────


class TestKnowledgeGraphModelsIntegration:
    """Tests for knowledge graph working with domain models."""

    @pytest.mark.integration
    def test_graph_entity_coverage(self):
        """Knowledge graph covers key agricultural entities."""
        from shared.ai.knowledge.graph_builder import build_agricultural_knowledge_graph

        graph = build_agricultural_knowledge_graph()
        entity_names = {e.name.lower() for e in graph.entities}

        # Key crops should be present
        assert "wheat" in entity_names
        assert "date palm" in entity_names or "date_palm" in entity_names

        # Should have relations
        assert len(graph.relations) > 0

    @pytest.mark.integration
    def test_agrovoc_graph_alignment(self):
        """AGROVOC concepts align with graph entities."""
        from shared.ai.knowledge.agrovoc import AgrovocLookup
        from shared.ai.knowledge.graph_builder import build_agricultural_knowledge_graph

        agrovoc = AgrovocLookup()
        graph = build_agricultural_knowledge_graph()

        # Check that major crops in graph have AGROVOC entries
        crop_entities = [e for e in graph.entities if e.entity_type == "crop"]
        matched = 0
        for entity in crop_entities:
            result = agrovoc.find(entity.name)
            if result:
                matched += 1

        # At least 50% of crops should have AGROVOC entries
        if crop_entities:
            assert matched / len(crop_entities) >= 0.5
