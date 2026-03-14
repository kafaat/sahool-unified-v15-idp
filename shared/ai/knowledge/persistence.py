# ═══════════════════════════════════════════════════════════════════════════════
# Knowledge Persistence Layer
# طبقة استمرارية المعرفة
# ═══════════════════════════════════════════════════════════════════════════════
#
# Repository-pattern persistence for agricultural knowledge documents:
#   - Abstract KnowledgeRepository base with full CRUD contract
#   - InMemoryKnowledgeRepository for testing and development
#   - Paginated queries with domain, collection, tag, region, and text filters
#
# ═══════════════════════════════════════════════════════════════════════════════

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime

from shared.ai.knowledge._logging import get_logger

from .models import BaseKnowledgeDocument, KnowledgeDomain

logger = get_logger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Query & Pagination Data Classes
# ─────────────────────────────────────────────────────────────────────────────


@dataclass
class DocumentQuery:
    """Query parameters for document search.
    معاملات الاستعلام للبحث عن الوثائق"""

    domain: KnowledgeDomain | None = None
    collection: str | None = None
    tags: list[str] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)
    min_credibility: int = 1
    verification_status: str | None = None
    text_search: str = ""
    limit: int = 100
    offset: int = 0


@dataclass
class DocumentPage:
    """Paginated document results.
    نتائج الوثائق المقسمة لصفحات"""

    items: list[BaseKnowledgeDocument]
    total: int = 0
    limit: int = 100
    offset: int = 0

    @property
    def has_next(self) -> bool:
        """Whether more pages are available | هل يوجد صفحات إضافية"""
        return self.offset + self.limit < self.total


# ─────────────────────────────────────────────────────────────────────────────
# Abstract Repository
# ─────────────────────────────────────────────────────────────────────────────


class KnowledgeRepository(ABC):
    """Abstract repository for knowledge document persistence.
    مستودع مجرد لاستمرارية وثائق المعرفة"""

    @abstractmethod
    def save(self, document: BaseKnowledgeDocument) -> str:
        """Save a document and return its ID.
        حفظ وثيقة وإرجاع معرفها"""
        ...

    @abstractmethod
    def save_batch(self, documents: list[BaseKnowledgeDocument]) -> list[str]:
        """Save multiple documents and return their IDs.
        حفظ وثائق متعددة وإرجاع معرفاتها"""
        ...

    @abstractmethod
    def get_by_id(self, document_id: str) -> BaseKnowledgeDocument | None:
        """Retrieve a document by ID, or None if not found.
        استرجاع وثيقة بالمعرف أو لا شيء إذا لم توجد"""
        ...

    @abstractmethod
    def find(self, query: DocumentQuery) -> DocumentPage:
        """Find documents matching query parameters with pagination.
        البحث عن وثائق مطابقة لمعاملات الاستعلام مع التقسيم لصفحات"""
        ...

    @abstractmethod
    def update(self, document: BaseKnowledgeDocument) -> bool:
        """Update an existing document. Returns True if the document existed.
        تحديث وثيقة موجودة. يرجع صحيح إذا كانت الوثيقة موجودة"""
        ...

    @abstractmethod
    def delete(self, document_id: str) -> bool:
        """Delete a document by ID. Returns True if deleted.
        حذف وثيقة بالمعرف. يرجع صحيح إذا تم الحذف"""
        ...

    @abstractmethod
    def count(self, collection: str | None = None) -> int:
        """Count documents, optionally filtered by collection.
        عد الوثائق مع مرشح اختياري بالمجموعة"""
        ...

    @abstractmethod
    def list_collections(self) -> list[str]:
        """List all distinct collection names.
        سرد جميع أسماء المجموعات المميزة"""
        ...


# ─────────────────────────────────────────────────────────────────────────────
# In-Memory Implementation
# ─────────────────────────────────────────────────────────────────────────────


class InMemoryKnowledgeRepository(KnowledgeRepository):
    """In-memory implementation for testing and development.
    تنفيذ في الذاكرة للاختبار والتطوير

    Stores documents in a plain dict keyed by document ID.
    Supports all query filters: domain, collection, tags, regions,
    credibility, verification status, and free-text search.
    """

    def __init__(self) -> None:
        self._store: dict[str, BaseKnowledgeDocument] = {}
        logger.info("in_memory_knowledge_repository_init")

    # ─── CRUD ─────────────────────────────────────────────────────────────

    def save(self, document: BaseKnowledgeDocument) -> str:
        """Save a document and return its ID.
        حفظ وثيقة وإرجاع معرفها"""
        self._store[document.id] = document
        logger.debug("document_saved", document_id=document.id, domain=document.domain.value)
        return document.id

    def save_batch(self, documents: list[BaseKnowledgeDocument]) -> list[str]:
        """Save multiple documents and return their IDs.
        حفظ وثائق متعددة وإرجاع معرفاتها"""
        ids: list[str] = []
        for doc in documents:
            ids.append(self.save(doc))
        logger.info("batch_saved", count=len(ids))
        return ids

    def get_by_id(self, document_id: str) -> BaseKnowledgeDocument | None:
        """Retrieve a document by ID, or None if not found.
        استرجاع وثيقة بالمعرف أو لا شيء إذا لم توجد"""
        doc = self._store.get(document_id)
        if doc is None:
            logger.debug("document_not_found", document_id=document_id)
        return doc

    def find(self, query: DocumentQuery) -> DocumentPage:
        """Find documents matching query parameters with pagination.
        البحث عن وثائق مطابقة لمعاملات الاستعلام مع التقسيم لصفحات"""
        matching = [doc for doc in self._store.values() if self._matches_query(doc, query)]
        total = len(matching)

        # Apply pagination
        page_items = matching[query.offset : query.offset + query.limit]

        logger.debug(
            "find_completed",
            total_matching=total,
            returned=len(page_items),
            offset=query.offset,
            limit=query.limit,
        )

        return DocumentPage(
            items=page_items,
            total=total,
            limit=query.limit,
            offset=query.offset,
        )

    def update(self, document: BaseKnowledgeDocument) -> bool:
        """Update an existing document. Returns True if the document existed.
        تحديث وثيقة موجودة. يرجع صحيح إذا كانت الوثيقة موجودة"""
        if document.id not in self._store:
            logger.debug("update_document_not_found", document_id=document.id)
            return False
        document.updated_at = datetime.utcnow()
        self._store[document.id] = document
        logger.debug("document_updated", document_id=document.id)
        return True

    def delete(self, document_id: str) -> bool:
        """Delete a document by ID. Returns True if deleted.
        حذف وثيقة بالمعرف. يرجع صحيح إذا تم الحذف"""
        if document_id not in self._store:
            logger.debug("delete_document_not_found", document_id=document_id)
            return False
        del self._store[document_id]
        logger.info("document_deleted", document_id=document_id)
        return True

    def count(self, collection: str | None = None) -> int:
        """Count documents, optionally filtered by collection.
        عد الوثائق مع مرشح اختياري بالمجموعة"""
        if collection is None:
            return len(self._store)
        return sum(1 for doc in self._store.values() if doc._get_collection() == collection)

    def list_collections(self) -> list[str]:
        """List all distinct collection names.
        سرد جميع أسماء المجموعات المميزة"""
        collections: set[str] = set()
        for doc in self._store.values():
            collections.add(doc._get_collection())
        return sorted(collections)

    # ─── Internal Filtering ───────────────────────────────────────────────

    def _matches_query(self, doc: BaseKnowledgeDocument, query: DocumentQuery) -> bool:
        """Check if a document matches all query criteria.
        التحقق من مطابقة وثيقة لجميع معايير الاستعلام"""

        # Domain filter
        if query.domain is not None and doc.domain != query.domain:
            return False

        # Collection filter
        if query.collection is not None and doc._get_collection() != query.collection:
            return False

        # Tags filter: all requested tags must be present
        if query.tags:
            if not all(tag in doc.tags for tag in query.tags):
                return False

        # Regions filter: at least one requested region must match
        if query.regions:
            doc_regions = doc.geospatial.applicable_regions
            if not any(r in doc_regions for r in query.regions):
                return False

        # Minimum credibility filter
        if query.min_credibility > 1:
            if doc.source.credibility.value < query.min_credibility:
                return False

        # Verification status filter
        if query.verification_status is not None:
            if doc.verification_status.value != query.verification_status:
                return False

        # Free-text search across title, content, and Arabic variants
        if query.text_search:
            search_lower = query.text_search.lower()
            searchable = " ".join(
                [
                    doc.title.lower(),
                    doc.title_ar,
                    doc.content.lower(),
                    doc.content_ar,
                ]
            )
            if search_lower not in searchable:
                return False

        return True
