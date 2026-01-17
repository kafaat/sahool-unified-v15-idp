"""
Graph API endpoints
نقاط نهاية API الرسم البياني
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from models import RelationshipType

router = APIRouter(prefix="/api/v1/graphs", tags=["graphs"])


@router.get("/stats")
async def get_graph_statistics(request):
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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))


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
        raise HTTPException(status_code=500, detail=str(e))
