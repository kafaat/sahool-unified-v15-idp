"""
Vector Service Schemas
مخططات البيانات لخدمة المتجهات
"""
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class UpsertVectorRequest(BaseModel):
    """Request to upsert a vector"""
    tenant_id: str = Field(..., min_length=2, description="Tenant identifier")
    namespace: str = Field(..., min_length=2, description="Namespace (e.g., advisor, ndvi_cases, docs)")
    doc_id: str = Field(..., min_length=2, description="Document identifier")
    text: str = Field(..., min_length=1, description="Text content to embed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class UpsertVectorResponse(BaseModel):
    """Response from upsert operation"""
    inserted: int
    ids: List[str]


class BatchUpsertRequest(BaseModel):
    """Request to upsert multiple vectors"""
    tenant_id: str = Field(..., min_length=2)
    namespace: str = Field(..., min_length=2)
    documents: List[Dict[str, Any]] = Field(..., description="List of {doc_id, text, metadata}")


class BatchUpsertResponse(BaseModel):
    """Response from batch upsert"""
    inserted: int
    ids: List[str]
    failed: List[str] = Field(default_factory=list)


class SearchRequest(BaseModel):
    """Request to search vectors"""
    tenant_id: str = Field(..., min_length=2, description="Tenant identifier")
    namespace: str = Field(..., min_length=2, description="Namespace to search in")
    query: str = Field(..., min_length=1, description="Search query text")
    top_k: int = Field(default=5, ge=1, le=20, description="Number of results to return")
    filters: Optional[Dict[str, Any]] = Field(None, description="Optional metadata filters")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score")


class SearchHit(BaseModel):
    """Single search result"""
    doc_id: str
    score: float
    text: str
    metadata: Dict[str, Any]


class SearchResponse(BaseModel):
    """Response from search operation"""
    hits: List[SearchHit]
    query: str
    total_found: int


class DeleteRequest(BaseModel):
    """Request to delete vectors"""
    tenant_id: str = Field(..., min_length=2)
    namespace: str = Field(..., min_length=2)
    doc_ids: List[str] = Field(..., description="Document IDs to delete")


class DeleteResponse(BaseModel):
    """Response from delete operation"""
    deleted: int


class HealthResponse(BaseModel):
    """Health check response"""
    ok: bool
    milvus_connected: bool
    collection_loaded: bool
    embedding_model: str
