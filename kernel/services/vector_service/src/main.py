"""
SAHOOL Vector Service - Main FastAPI Application
خدمة المتجهات - التطبيق الرئيسي

Multi-tenant vector storage and RAG support using Milvus.
"""
import json
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .settings import settings
from .schemas import (
    UpsertVectorRequest,
    UpsertVectorResponse,
    BatchUpsertRequest,
    BatchUpsertResponse,
    SearchRequest,
    SearchResponse,
    SearchHit,
    DeleteRequest,
    DeleteResponse,
    HealthResponse,
)
from .embedder import create_embedder, BaseEmbedder
from .milvus_client import connect, ensure_collection, is_connected, get_collection
from .rag import build_context, build_arabic_context, extract_source_references

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global embedder instance
embedder: BaseEmbedder = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global embedder

    # Startup
    logger.info("Starting Vector Service...")

    try:
        connect()
        ensure_collection()
        logger.info("Connected to Milvus")
    except Exception as e:
        logger.error(f"Failed to connect to Milvus: {e}")

    try:
        embedder = create_embedder()
        logger.info(f"Loaded embedding model: {settings.embedding_model}")
    except Exception as e:
        logger.error(f"Failed to load embedding model: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Vector Service...")


app = FastAPI(
    title="SAHOOL Vector Service",
    description="Multi-tenant vector storage and RAG support for agricultural AI",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return HealthResponse(
        ok=True,
        milvus_connected=is_connected(),
        collection_loaded=True,
        embedding_model=settings.embedding_model,
    )


@app.post("/v1/vectors:upsert", response_model=UpsertVectorResponse)
def upsert_vector(req: UpsertVectorRequest):
    """
    Upsert a single vector.

    The vector ID is computed as: {tenant_id}:{namespace}:{doc_id}
    """
    if settings.tenant_filter_required and not req.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    try:
        # Generate embedding
        vec = embedder.embed(req.text)

        # Compute unique ID
        _id = f"{req.tenant_id}:{req.namespace}:{req.doc_id}"
        metadata_json = json.dumps(req.metadata, ensure_ascii=False)

        # Prepare entities for insertion
        entities = [
            [_id],  # id
            [req.tenant_id],  # tenant_id
            [req.namespace],  # namespace
            [req.doc_id],  # doc_id
            [req.text],  # text
            [metadata_json],  # metadata_json
            [vec],  # embedding
        ]

        collection = get_collection()
        collection.insert(entities)
        collection.flush()

        logger.info(f"Upserted vector: {_id}")
        return UpsertVectorResponse(inserted=1, ids=[_id])

    except Exception as e:
        logger.error(f"Upsert failed: {e}")
        raise HTTPException(status_code=500, detail=f"upsert_failed: {str(e)}")


@app.post("/v1/vectors:batch-upsert", response_model=BatchUpsertResponse)
def batch_upsert(req: BatchUpsertRequest):
    """
    Upsert multiple vectors in a batch.
    """
    if settings.tenant_filter_required and not req.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    if not req.documents:
        return BatchUpsertResponse(inserted=0, ids=[], failed=[])

    ids = []
    failed = []

    try:
        # Prepare batch data
        all_ids = []
        all_tenant_ids = []
        all_namespaces = []
        all_doc_ids = []
        all_texts = []
        all_metadata = []
        all_embeddings = []

        texts_to_embed = [doc.get("text", "") for doc in req.documents]
        embeddings = embedder.embed_batch(texts_to_embed)

        for i, doc in enumerate(req.documents):
            doc_id = doc.get("doc_id", f"doc_{i}")
            text = doc.get("text", "")
            metadata = doc.get("metadata", {})

            _id = f"{req.tenant_id}:{req.namespace}:{doc_id}"

            all_ids.append(_id)
            all_tenant_ids.append(req.tenant_id)
            all_namespaces.append(req.namespace)
            all_doc_ids.append(doc_id)
            all_texts.append(text)
            all_metadata.append(json.dumps(metadata, ensure_ascii=False))
            all_embeddings.append(embeddings[i])

        entities = [
            all_ids,
            all_tenant_ids,
            all_namespaces,
            all_doc_ids,
            all_texts,
            all_metadata,
            all_embeddings,
        ]

        collection = get_collection()
        collection.insert(entities)
        collection.flush()

        ids = all_ids
        logger.info(f"Batch upserted {len(ids)} vectors")

    except Exception as e:
        logger.error(f"Batch upsert failed: {e}")
        raise HTTPException(status_code=500, detail=f"batch_upsert_failed: {str(e)}")

    return BatchUpsertResponse(inserted=len(ids), ids=ids, failed=failed)


@app.post("/v1/vectors:search", response_model=SearchResponse)
def search_vectors(req: SearchRequest):
    """
    Search for similar vectors.

    Results are filtered by tenant_id and namespace (mandatory).
    """
    if settings.tenant_filter_required and not req.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    try:
        # Generate query embedding
        qvec = embedder.embed(req.query)

        # Build filter expression (mandatory tenant + namespace filter)
        expr = f'tenant_id == "{req.tenant_id}" and namespace == "{req.namespace}"'

        search_params = {
            "metric_type": "IP",
            "params": {"ef": 128},
        }

        collection = get_collection()
        results = collection.search(
            data=[qvec],
            anns_field="embedding",
            param=search_params,
            limit=req.top_k,
            expr=expr,
            output_fields=["doc_id", "text", "metadata_json"],
        )

        hits = []
        for hit in results[0]:
            score = float(hit.distance)

            # Apply minimum score filter
            if score < req.min_score:
                continue

            # Parse metadata
            metadata = {}
            try:
                metadata = json.loads(hit.entity.get("metadata_json") or "{}")
            except Exception:
                pass

            hits.append(SearchHit(
                doc_id=hit.entity.get("doc_id", ""),
                score=score,
                text=hit.entity.get("text", ""),
                metadata=metadata,
            ))

        logger.info(f"Search returned {len(hits)} hits for query: {req.query[:50]}...")
        return SearchResponse(hits=hits, query=req.query, total_found=len(hits))

    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=f"search_failed: {str(e)}")


@app.post("/v1/vectors:delete", response_model=DeleteResponse)
def delete_vectors(req: DeleteRequest):
    """
    Delete vectors by document IDs.
    """
    if settings.tenant_filter_required and not req.tenant_id:
        raise HTTPException(status_code=400, detail="tenant_id is required")

    try:
        # Build IDs to delete
        ids_to_delete = [
            f"{req.tenant_id}:{req.namespace}:{doc_id}"
            for doc_id in req.doc_ids
        ]

        expr = f'id in {ids_to_delete}'

        collection = get_collection()
        collection.delete(expr)
        collection.flush()

        logger.info(f"Deleted {len(ids_to_delete)} vectors")
        return DeleteResponse(deleted=len(ids_to_delete))

    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=f"delete_failed: {str(e)}")


@app.post("/v1/rag:context")
def get_rag_context(
    req: SearchRequest,
    format: str = Query(default="plain", enum=["plain", "arabic"]),
    max_chars: int = Query(default=4000, ge=100, le=10000),
):
    """
    Search and return formatted context for RAG.

    This is a convenience endpoint that combines search + context building.
    """
    # Perform search
    search_response = search_vectors(req)

    # Convert hits to dicts
    hits = [
        {
            "doc_id": h.doc_id,
            "score": h.score,
            "text": h.text,
            "metadata": h.metadata,
        }
        for h in search_response.hits
    ]

    # Build context based on format
    if format == "arabic":
        context = build_arabic_context(hits, max_chars=max_chars)
    else:
        context = build_context(hits, max_chars=max_chars)

    # Extract source references
    sources = extract_source_references(hits)

    return {
        "context": context,
        "sources": sources,
        "query": req.query,
        "hits_count": len(hits),
    }
