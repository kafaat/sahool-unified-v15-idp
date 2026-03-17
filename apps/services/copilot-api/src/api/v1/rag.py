"""
RAG Management Endpoints
نقاط نهاية إدارة RAG

Document management and search for knowledge base.

Author: SAHOOL Platform Team
Updated: March 2026
"""

from __future__ import annotations

import time
from typing import Any

import structlog
from fastapi import APIRouter, Body, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from ...models.schemas import RAGDocument, RAGSearchResult
from ...rag import get_rag_service
from ..deps import get_current_user

logger = structlog.get_logger(__name__)
router = APIRouter(prefix="/rag", tags=["RAG"])


# ═══════════════════════════════════════════════════════════════════════════════
# Request Models | نماذج الطلبات
# ═══════════════════════════════════════════════════════════════════════════════


class AddDocumentRequest(BaseModel):
    """Request body for adding a document | طلب إضافة وثيقة"""

    text: str = Field(..., min_length=1, max_length=50000, description="Document text (English)")
    text_ar: str | None = Field(default=None, max_length=50000, description="Document text (Arabic)")
    category: str | None = Field(default=None, description="Document category")
    tenant_id: str | None = Field(default=None, description="Tenant ID")
    metadata: dict[str, Any] | None = Field(default=None, description="Additional metadata")


class BatchDocumentItem(BaseModel):
    """Single document in a batch request | وثيقة واحدة في طلب دفعة"""

    text: str = Field(..., min_length=1)
    text_ar: str | None = None
    metadata: dict[str, Any] | None = None
    id: str | None = None


class BatchDocumentsRequest(BaseModel):
    """Request body for batch document addition | طلب إضافة وثائق دفعة"""

    documents: list[BatchDocumentItem] = Field(..., min_length=1, max_length=100)


# ═══════════════════════════════════════════════════════════════════════════════
# Endpoints | نقاط النهاية
# ═══════════════════════════════════════════════════════════════════════════════


@router.get("/search", response_model=RAGSearchResult)
async def search(
    query: str = Query(..., min_length=1, max_length=1000, description="Search query"),
    k: int = Query(default=5, ge=1, le=50, description="Number of results"),
    category: str | None = Query(default=None, description="Filter by category"),
    tenant_id: str | None = Query(default=None, description="Tenant ID"),
    user: dict = Depends(get_current_user),
):
    """
    Search the knowledge base.
    البحث في قاعدة المعرفة
    """
    start_time = time.time()

    rag_service = get_rag_service()

    metadata_filter = {"category": category} if category else None

    results = await rag_service.search(
        query=query,
        top_k=k,
        metadata_filter=metadata_filter,
        tenant_id=tenant_id,
    )

    search_time = (time.time() - start_time) * 1000

    documents = [
        RAGDocument(
            id=r.document.id,
            text=r.document.text,
            text_ar=r.document.text_ar,
            metadata={**r.document.metadata, "score": r.score},
        )
        for r in results
    ]

    return RAGSearchResult(
        documents=documents,
        query=query,
        total_found=len(documents),
        search_time_ms=search_time,
    )


@router.post("/documents", response_model=RAGDocument)
async def add_document(
    request: AddDocumentRequest = Body(...),
    user: dict = Depends(get_current_user),
):
    """
    Add a document to the knowledge base.
    إضافة وثيقة إلى قاعدة المعرفة
    """
    rag_service = get_rag_service()

    doc_metadata = request.metadata or {}
    if request.category:
        doc_metadata["category"] = request.category
    if request.tenant_id:
        doc_metadata["tenant_id"] = request.tenant_id

    doc = await rag_service.add_document(
        text=request.text,
        text_ar=request.text_ar,
        metadata=doc_metadata,
    )

    return RAGDocument(
        id=doc.id,
        text=doc.text,
        text_ar=doc.text_ar,
        metadata=doc.metadata,
    )


@router.post("/documents/batch")
async def add_documents_batch(
    request: BatchDocumentsRequest = Body(...),
    user: dict = Depends(get_current_user),
):
    """
    Add multiple documents in batch.
    إضافة وثائق متعددة دفعة واحدة
    """
    rag_service = get_rag_service()

    docs = [d.model_dump(exclude_none=True) for d in request.documents]
    results = await rag_service.add_documents_batch(docs)

    return {
        "added": len(results),
        "documents": [{"id": d.id} for d in results],
    }


@router.get("/documents")
async def list_documents(
    tenant_id: str | None = Query(default=None, description="Tenant ID"),
    limit: int = Query(default=100, ge=1, le=1000, description="Limit"),
    offset: int = Query(default=0, ge=0, description="Offset"),
    user: dict = Depends(get_current_user),
):
    """
    List documents in the knowledge base.
    عرض قائمة الوثائق في قاعدة المعرفة
    """
    rag_service = get_rag_service()

    docs = await rag_service.list_documents(
        tenant_id=tenant_id,
        limit=limit,
        offset=offset,
    )

    return {
        "documents": [d.to_dict() for d in docs],
        "total": len(docs),
        "limit": limit,
        "offset": offset,
    }


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, user: dict = Depends(get_current_user)):
    """
    Delete a document from the knowledge base.
    حذف وثيقة من قاعدة المعرفة
    """
    rag_service = get_rag_service()

    success = await rag_service.delete_document(doc_id)

    if not success:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"deleted": True, "id": doc_id}


@router.get("/stats")
async def get_stats(user: dict = Depends(get_current_user)):
    """
    Get RAG service statistics.
    الحصول على إحصائيات خدمة RAG
    """
    rag_service = get_rag_service()
    stats = await rag_service.get_stats()
    return stats


@router.post("/index/sahool-docs")
async def index_sahool_docs(user: dict = Depends(get_current_user)):
    """
    Index SAHOOL documentation for RAG.
    فهرسة وثائق SAHOOL للـ RAG
    """
    rag_service = get_rag_service()

    # Add core SAHOOL knowledge
    docs = [
        {
            "text": """SAHOOL is a National Agricultural Intelligence Platform providing
            offline-first agricultural advisory, irrigation management, NDVI analysis,
            and crop health monitoring for farmers in the Middle East.""",
            "text_ar": """سهول هي منصة الذكاء الزراعي الوطنية التي توفر استشارات
            زراعية offline-first وإدارة الري وتحليل NDVI ومراقبة صحة المحاصيل
            للمزارعين في الشرق الأوسط.""",
            "metadata": {"category": "overview", "source": "documentation"},
        },
        {
            "text": """Wheat irrigation schedule: During tillering stage, irrigate
            every 10-14 days. Apply 25-30mm per irrigation. Monitor soil moisture
            and adjust based on weather forecast.""",
            "text_ar": """جدول ري القمح: خلال مرحلة التفريع، يُنصح بالري كل 10-14 يوم.
            تطبيق 25-30 ملم لكل رية. مراقبة رطوبة التربة والتعديل بناءً على توقعات الطقس.""",
            "metadata": {"category": "irrigation", "crop": "wheat"},
        },
        {
            "text": """NDVI (Normalized Difference Vegetation Index) values:
            - 0.1-0.2: Bare soil or sparse vegetation
            - 0.2-0.4: Moderate vegetation
            - 0.4-0.6: Dense vegetation
            - 0.6-0.9: Very dense/healthy vegetation""",
            "text_ar": """قيم مؤشر الغطاء النباتي NDVI:
            - 0.1-0.2: تربة عارية أو غطاء نباتي متفرق
            - 0.2-0.4: غطاء نباتي متوسط
            - 0.4-0.6: غطاء نباتي كثيف
            - 0.6-0.9: غطاء نباتي كثيف جداً/صحي""",
            "metadata": {"category": "ndvi", "type": "reference"},
        },
        {
            "text": """Nitrogen deficiency symptoms in wheat: Yellowing of older
            leaves starting from the tips, stunted growth, reduced tillering.
            Apply urea (46% N) at 46 kg/ha during tillering stage.""",
            "text_ar": """أعراض نقص النيتروجين في القمح: اصفرار الأوراق القديمة
            بدءاً من الأطراف، تقزم النمو، قلة التفريع.
            يُطبق اليوريا (46% نيتروجين) بمعدل 46 كجم/هكتار خلال مرحلة التفريع.""",
            "metadata": {"category": "fertilizer", "crop": "wheat", "nutrient": "nitrogen"},
        },
    ]

    results = await rag_service.add_documents_batch(docs)

    return {
        "indexed": len(results),
        "message": "SAHOOL documentation indexed successfully",
        "message_ar": "تم فهرسة وثائق سهول بنجاح",
    }
