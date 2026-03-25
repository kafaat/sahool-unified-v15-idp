"""
Graph API endpoints
نقاط نهاية API الرسم البياني
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query

logger = logging.getLogger(__name__)

from models import RelationshipType

# Authentication dependency
try:
    from shared.auth.dependencies import get_current_user
    from shared.auth.models import User
except ImportError:
    from fastapi import HTTPException as _HTTPException

    class User:
        id: str = "anonymous"
        tenant_id: str | None = None

    async def get_current_user():
        raise _HTTPException(status_code=503, detail="Authentication backend unavailable")


router = APIRouter(prefix="/api/v1/graphs", tags=["graphs"])


@router.get("/stats")
async def get_graph_statistics(request, _user=Depends(get_current_user)):
    """
    Get knowledge graph statistics

    Returns statistics about nodes, edges, and entities in the graph.
    """
    graph_service = request.app.state.graph_service
    try:
        stats = await graph_service.get_graph_stats()
        return {
            "status": "success",
            "data": stats,
        }
    except Exception as e:
        logger.error("Failed to get graph statistics: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.get("/path")
async def find_relationship_path(
    request,
    source_type: str = Query(..., description="Source entity type (crop, disease, treatment)"),
    source_id: str = Query(..., description="Source entity ID"),
    target_type: str = Query(..., description="Target entity type (crop, disease, treatment)"),
    target_id: str = Query(..., description="Target entity ID"),
):
    """
    Find the shortest path between two entities

    Shows the relationship chain connecting two entities in the knowledge graph.
    Useful for understanding how crops, diseases, and treatments are connected.
    """
    graph_service = request.app.state.graph_service
    try:
        path = await graph_service.find_shortest_path(
            source_type=source_type,
            source_id=source_id,
            target_type=target_type,
            target_id=target_id,
        )

        if not path:
            raise HTTPException(
                status_code=404,
                detail=f"No path found between {source_type}:{source_id} and {target_type}:{target_id}",
            )

        return {
            "status": "success",
            "data": path.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to find relationship path: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")


@router.get("/search")
async def search_graph(
    request,
    q: str = Query(..., description="Search query"),
    entity_type: str | None = Query(None, description="Filter by entity type (crop, disease, treatment)"),
    limit: int = Query(20, ge=1, le=100, description="Maximum results"),
):
    """
    Search for entities in the knowledge graph

    Searches across all entity types (crops, diseases, treatments) for matching names or descriptions.
    """
    graph_service = request.app.state.graph_service
    try:
        results = await graph_service.search_entities(
            query=q,
            entity_type=entity_type,
            limit=limit,
        )

        return {
            "status": "success",
            "query": q,
            "total_results": len(results),
            "data": results,
        }
    except Exception as e:
        logger.error("Failed to search graph: %s", e, exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error | خطأ داخلي في الخادم")
