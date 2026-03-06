# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Ingestion Pipeline
# خط أنابيب استيعاب المعرفة الزراعية
# ═══════════════════════════════════════════════════════════════════════════════
#
# Pipeline stages:
#   1. Extract  → MarkdownExtractor / PDFExtractor / HTMLExtractor
#   2. Preprocess → Arabic normalization, term unification, metadata enrichment
#   3. Validate source → Source credibility check via registry
#   4. Validate content → Scientific range checks, bilingual support
#   5. Region relevance → Climate/crop/soil compatibility filter
#   6. Store → Chunk & embed via UltraRAG KnowledgeBase
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import structlog

from ..agrovoc import AgrovocLookup
from ..collections import GENERAL_AGRICULTURE
from ..models import (
    BaseKnowledgeDocument,
    FRESHMetadata,
    GeospatialMetadata,
    KnowledgeDomain,
    KnowledgeSourceMeta,
    SourceCredibilityLevel,
    VerificationStatus,
)
from ..sources.registry import KnowledgeSourceRegistry
from ..validators import KnowledgeValidator, ValidationResult
from .chunker import ChunkConfig, TextChunker

if TYPE_CHECKING:
    from ..vector_store_integration import KnowledgeVectorStore
from .extractors import ExtractedContent, HTMLExtractor, MarkdownExtractor, PDFExtractor
from .preprocessors import AgriculturalTermNormalizer, ArabicTextPreprocessor, MetadataEnricher

logger = structlog.get_logger(__name__)


@dataclass
class IngestionResult:
    """Result of a single document ingestion | نتيجة استيعاب وثيقة واحدة"""

    document_id: str = ""
    success: bool = False
    collection: str = ""
    source_credibility: int = 0
    validation: ValidationResult | None = None
    domains_detected: list[str] = field(default_factory=list)
    regions_detected: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    vector_ids: list[str] = field(default_factory=list)
    chunks_count: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class BatchIngestionReport:
    """Report for a batch ingestion run | تقرير تشغيل استيعاب مجمع"""

    total: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    results: list[IngestionResult] = field(default_factory=list)
    by_collection: dict[str, int] = field(default_factory=dict)
    by_domain: dict[str, int] = field(default_factory=dict)


class KnowledgeIngestionPipeline:
    """Main pipeline for ingesting agricultural knowledge from multiple sources.
    خط أنابيب رئيسي لاستيعاب المعرفة الزراعية من مصادر متعددة"""

    def __init__(
        self,
        source_registry: KnowledgeSourceRegistry | None = None,
        validator: KnowledgeValidator | None = None,
        vector_store: KnowledgeVectorStore | None = None,
        chunk_config: ChunkConfig | None = None,
        min_source_credibility: int = 1,
        require_bilingual: bool = False,
        enable_agrovoc: bool = True,
        enable_vector_storage: bool = True,
    ) -> None:
        self._md_extractor = MarkdownExtractor()
        self._pdf_extractor = PDFExtractor()
        self._html_extractor = HTMLExtractor()
        self._arabic_preprocessor = ArabicTextPreprocessor()
        self._term_normalizer = AgriculturalTermNormalizer()
        self._metadata_enricher = MetadataEnricher()
        self._source_registry = source_registry or KnowledgeSourceRegistry()
        self._validator = validator or KnowledgeValidator()
        self._min_credibility = min_source_credibility
        self._require_bilingual = require_bilingual
        self._agrovoc = AgrovocLookup() if enable_agrovoc else None
        self._enable_vector_storage = enable_vector_storage
        self._vector_store = vector_store
        self._chunker = TextChunker(chunk_config or ChunkConfig())

    # ─── Public API ───────────────────────────────────────────────────────────

    def ingest_file(
        self,
        file_path: str | Path,
        source_url: str = "",
        target_collection: str | None = None,
        extra_metadata: dict[str, Any] | None = None,
    ) -> IngestionResult:
        """Ingest a single file through the full pipeline.
        استيعاب ملف واحد عبر خط الأنابيب الكامل"""
        result = IngestionResult()
        path = Path(file_path)

        # Stage 1: Extract
        extracted = self._extract(path)
        if not extracted.content and not extracted.content_ar:
            result.errors.append(f"No content extracted from {path}")
            return result

        # Stage 2: Preprocess
        extracted = self._preprocess(extracted)

        # Stage 3: Source credibility
        credibility = self._check_source(source_url)
        result.source_credibility = credibility.value
        if credibility.value < self._min_credibility:
            result.errors.append(f"Source credibility {credibility.value} below minimum {self._min_credibility}")
            result.warnings.append("Low credibility source - requires additional verification")

        # Stage 4: Detect domains & regions
        full_text = f"{extracted.content} {extracted.content_ar}"
        domains = self._metadata_enricher.detect_domains(full_text)
        regions = self._metadata_enricher.detect_regions(full_text)
        tags = self._metadata_enricher.extract_tags(full_text, extracted.metadata)
        result.domains_detected = [d.value for d in domains]
        result.regions_detected = regions
        result.tags = tags

        # Stage 5: Build document model
        primary_domain = domains[0] if domains else KnowledgeDomain.GENERAL
        collection = target_collection or self._resolve_collection(primary_domain)
        result.collection = collection

        # AGROVOC concept extraction
        agrovoc_concepts = extracted.metadata.get("agrovoc", [])
        if self._agrovoc and not agrovoc_concepts:
            found_concepts = self._agrovoc.extract_concepts_from_text(full_text)
            agrovoc_concepts = [c.uri for c in found_concepts]

        # AGROVOC tag enrichment
        if self._agrovoc:
            tags = self._agrovoc.enrich_tags(tags)

        # Seasonal relevance detection (AgriSaathi pattern)
        seasonal = self._metadata_enricher.detect_seasonal_relevance(full_text)

        doc = BaseKnowledgeDocument(
            title=extracted.title or path.stem,
            title_ar=extracted.title_ar,
            content=extracted.content,
            content_ar=extracted.content_ar,
            domain=primary_domain,
            tags=tags,
            fresh=FRESHMetadata(
                format=extracted.source_type or "md",
                relevance_domains=domains,
                seasonal_relevance=seasonal,
            ),
            geospatial=GeospatialMetadata(
                applicable_regions=regions,
            ),
            source=KnowledgeSourceMeta(
                source_url=source_url,
                source_name=path.name,
                credibility=credibility,
                agrovoc_concepts=agrovoc_concepts,
            ),
            verification_status=(VerificationStatus.APPROVED if credibility.value >= 4 else VerificationStatus.PENDING),
        )
        result.document_id = doc.id

        # Stage 6: Validate
        validation = self._validator.validate(doc)
        result.validation = validation

        if self._require_bilingual and not doc.content_ar:
            result.warnings.append("Bilingual content recommended but Arabic content missing")

        for issue in validation.issues:
            if issue.severity == "error":
                result.errors.append(f"[{issue.field}] {issue.message}")
            else:
                result.warnings.append(f"[{issue.field}] {issue.message}")

        # Mark success if no errors
        result.success = validation.is_valid

        # Stage 7: Chunk, embed, and store in vector DB
        # مرحلة 7: تقطيع وتضمين وتخزين في قاعدة بيانات المتجهات
        if result.success and self._enable_vector_storage:
            vector_ids = self._store_in_vector_db(doc)
            result.vector_ids = vector_ids
            if vector_ids:
                result.chunks_count = len(vector_ids)

        logger.info(
            "document_ingested",
            document_id=doc.id,
            collection=collection,
            domain=primary_domain.value,
            success=result.success,
            credibility=credibility.value,
            vector_ids_count=len(result.vector_ids),
        )

        return result

    def ingest_text(
        self,
        text: str,
        title: str = "",
        source_url: str = "",
        target_collection: str | None = None,
    ) -> IngestionResult:
        """Ingest raw text content through the pipeline.
        استيعاب نص خام عبر خط الأنابيب"""
        result = IngestionResult()

        # Extract from markdown text
        extracted = self._md_extractor.extract_from_text(text, source=source_url)
        if title:
            extracted.title = title

        # Preprocess
        extracted = self._preprocess(extracted)

        # Source credibility
        credibility = self._check_source(source_url)
        result.source_credibility = credibility.value

        # Detect domains & metadata
        full_text = f"{extracted.content} {extracted.content_ar}"
        domains = self._metadata_enricher.detect_domains(full_text)
        regions = self._metadata_enricher.detect_regions(full_text)
        tags = self._metadata_enricher.extract_tags(full_text, extracted.metadata)
        result.domains_detected = [d.value for d in domains]
        result.regions_detected = regions
        result.tags = tags

        primary_domain = domains[0] if domains else KnowledgeDomain.GENERAL
        collection = target_collection or self._resolve_collection(primary_domain)
        result.collection = collection

        doc = BaseKnowledgeDocument(
            title=extracted.title or "Untitled",
            title_ar=extracted.title_ar,
            content=extracted.content,
            content_ar=extracted.content_ar,
            domain=primary_domain,
            tags=tags,
            source=KnowledgeSourceMeta(source_url=source_url, credibility=credibility),
        )
        result.document_id = doc.id

        validation = self._validator.validate(doc)
        result.validation = validation
        result.success = validation.is_valid

        # Store in vector DB if validation passed
        if result.success and self._enable_vector_storage:
            vector_ids = self._store_in_vector_db(doc)
            result.vector_ids = vector_ids
            if vector_ids:
                result.chunks_count = len(vector_ids)

        return result

    def ingest_directory(
        self,
        directory: str | Path,
        patterns: list[str] | None = None,
        target_collection: str | None = None,
    ) -> BatchIngestionReport:
        """Ingest all matching files from a directory.
        استيعاب جميع الملفات المطابقة من مجلد"""
        dir_path = Path(directory)
        if not dir_path.is_dir():
            logger.error("directory_not_found", path=str(dir_path))
            return BatchIngestionReport()

        if patterns is None:
            patterns = ["*.md", "*.txt"]

        files: list[Path] = []
        for pattern in patterns:
            files.extend(dir_path.glob(pattern))

        report = BatchIngestionReport(total=len(files))

        for file_path in sorted(files):
            if file_path.name.startswith(".") or file_path.name == "README.md":
                report.skipped += 1
                continue

            result = self.ingest_file(file_path, target_collection=target_collection)
            report.results.append(result)

            if result.success:
                report.succeeded += 1
                report.by_collection[result.collection] = report.by_collection.get(result.collection, 0) + 1
                for d in result.domains_detected:
                    report.by_domain[d] = report.by_domain.get(d, 0) + 1
            else:
                report.failed += 1

        logger.info(
            "batch_ingestion_complete",
            total=report.total,
            succeeded=report.succeeded,
            failed=report.failed,
            skipped=report.skipped,
        )

        return report

    # ─── Internal Pipeline Stages ─────────────────────────────────────────────

    def _extract(self, path: Path) -> ExtractedContent:
        """Stage 1: Extract content based on file type."""
        suffix = path.suffix.lower()
        if suffix in (".md", ".markdown", ".txt"):
            return self._md_extractor.extract(path)
        elif suffix == ".pdf":
            return self._pdf_extractor.extract(path)
        elif suffix in (".html", ".htm"):
            return self._html_extractor.extract(path)
        else:
            # Fallback: treat as plain text
            return self._md_extractor.extract(path)

    def _preprocess(self, content: ExtractedContent) -> ExtractedContent:
        """Stage 2: Preprocess extracted content."""
        # Normalize Arabic text
        if content.content_ar:
            content.content_ar = self._arabic_preprocessor.normalize(content.content_ar)
        if content.title_ar:
            content.title_ar = self._arabic_preprocessor.normalize(content.title_ar)

        # Normalize agricultural terms
        if content.content:
            content.content = self._term_normalizer.normalize_terms(content.content)

        return content

    def _check_source(self, url: str) -> SourceCredibilityLevel:
        """Stage 3: Check source credibility."""
        if not url:
            return SourceCredibilityLevel.COMMUNITY
        return self._source_registry.get_source_credibility(url)

    def _store_in_vector_db(self, document: BaseKnowledgeDocument) -> list[str]:
        """Stage 7: Chunk document and store embeddings in vector DB.
        المرحلة 7: تقطيع الوثيقة وتخزين التضمينات في قاعدة بيانات المتجهات

        Steps:
            1. Chunk the document content using TextChunker
            2. Pass chunks to KnowledgeVectorStore which generates embeddings
               and stores them
            3. Return the list of vector IDs for all stored chunks

        Returns:
            List of vector IDs for stored chunks, empty list if storage
            is disabled or no vector store is configured.
        """
        if not self._vector_store:
            logger.debug("vector_storage_skipped_no_store", document_id=document.id)
            return []

        try:
            # Chunk the document content
            base_metadata = {
                "document_id": document.id,
                "domain": document.domain.value,
                "title": document.title,
                "title_ar": document.title_ar,
                "tags": document.tags,
                "credibility": document.source.credibility.value,
                "verification_status": document.verification_status.value,
            }

            chunks = self._chunker.chunk(
                content=document.content,
                content_ar=document.content_ar,
                base_metadata=base_metadata,
            )

            if not chunks:
                logger.debug(
                    "vector_storage_no_chunks",
                    document_id=document.id,
                )
                return []

            # Store document with chunks in vector store
            # KnowledgeVectorStore.store_document handles embedding generation
            vector_ids = self._vector_store.store_document(
                document=document,
                chunks=chunks,
            )

            logger.info(
                "vector_storage_complete",
                document_id=document.id,
                chunks_count=len(chunks),
                vector_ids_count=len(vector_ids),
            )

            return vector_ids

        except Exception as e:
            logger.error(
                "vector_storage_error",
                document_id=document.id,
                error=str(e),
            )
            return []

    def _resolve_collection(self, domain: KnowledgeDomain) -> str:
        """Resolve domain to target collection name."""
        from ..collections import (
            CROP_KNOWLEDGE,
            DIGITAL_TWIN_KNOWLEDGE,
            FERTILIZER_KNOWLEDGE,
            IRRIGATION_PRACTICES,
            PEST_KNOWLEDGE,
            PRECISION_FARMING_KNOWLEDGE,
            REMOTE_SENSING_KNOWLEDGE,
            SMART_AGRICULTURE_KNOWLEDGE,
            SOIL_KNOWLEDGE,
            WEATHER_KNOWLEDGE,
        )

        domain_map = {
            KnowledgeDomain.CROPS: CROP_KNOWLEDGE,
            KnowledgeDomain.SOIL: SOIL_KNOWLEDGE,
            KnowledgeDomain.IRRIGATION: IRRIGATION_PRACTICES,
            KnowledgeDomain.FERTILIZER: FERTILIZER_KNOWLEDGE,
            KnowledgeDomain.PEST_DISEASE: PEST_KNOWLEDGE,
            KnowledgeDomain.WEATHER: WEATHER_KNOWLEDGE,
            KnowledgeDomain.REMOTE_SENSING: REMOTE_SENSING_KNOWLEDGE,
            KnowledgeDomain.SMART_AGRICULTURE: SMART_AGRICULTURE_KNOWLEDGE,
            KnowledgeDomain.PRECISION_FARMING: PRECISION_FARMING_KNOWLEDGE,
            KnowledgeDomain.DIGITAL_TWIN: DIGITAL_TWIN_KNOWLEDGE,
            KnowledgeDomain.GENERAL: GENERAL_AGRICULTURE,
        }
        return domain_map.get(domain, GENERAL_AGRICULTURE)
