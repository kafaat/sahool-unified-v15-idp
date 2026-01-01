"""
SAHOOL Qdrant Vector Store Adapter
Sprint 9: Qdrant implementation of VectorStore protocol

This adapter provides integration with Qdrant vector database.
Embeddings are handled externally to allow flexibility in embedding providers.
"""

from __future__ import annotations

from dataclasses import asdict
from typing import Any

from advisor.rag.doc_store import DocChunk, VectorStore

# Optional import - Qdrant client may not be installed
try:
    from qdrant_client import QdrantClient
    from qdrant_client.http.models import Distance, VectorParams, PointStruct

    QDRANT_AVAILABLE = True
except ImportError:
    QdrantClient = None  # type: ignore
    QDRANT_AVAILABLE = False


class QdrantVectorStore(VectorStore):
    """Qdrant-based vector store implementation.

    Note: This implementation uses placeholder vectors.
    In production, you should:
    1. Use an embedding adapter to generate real embeddings
    2. Pass embeddings along with chunks
    """

    def __init__(self, url: str = "http://localhost:6333", vector_size: int = 384):
        """Initialize Qdrant client.

        Args:
            url: Qdrant server URL
            vector_size: Dimension of embedding vectors (default: 384 for MiniLM)
        """
        if not QDRANT_AVAILABLE:
            raise RuntimeError(
                "qdrant-client not installed. "
                "Install with: pip install qdrant-client"
            )
        self._client = QdrantClient(url=url)
        self._vector_size = vector_size

    def ensure_collection(self, collection: str) -> None:
        """Ensure collection exists, create if not.

        Args:
            collection: Collection name
        """
        existing = [c.name for c in self._client.get_collections().collections]
        if collection in existing:
            return
        self._client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(
                size=self._vector_size,
                distance=Distance.COSINE,
            ),
        )

    def upsert_chunks(self, collection: str, chunks: list[DocChunk]) -> None:
        """Upsert chunks to Qdrant.

        NOTE: Uses placeholder zero vectors. In production:
        - Use an embedding adapter to generate embeddings
        - Replace the zero vectors with real embeddings

        Args:
            collection: Collection name
            chunks: Document chunks to upsert
        """
        self.ensure_collection(collection)

        points: list[PointStruct] = []
        for chunk in chunks:
            # Placeholder vector - replace with real embeddings in production
            # Example with sentence-transformers:
            # from sentence_transformers import SentenceTransformer
            # model = SentenceTransformer('all-MiniLM-L6-v2')
            # vector = model.encode(chunk.text).tolist()
            vector = [0.0] * self._vector_size

            point_id = f"{chunk.doc_id}:{chunk.chunk_id}"
            points.append(
                PointStruct(
                    id=point_id,
                    vector=vector,
                    payload=asdict(chunk),
                )
            )

        self._client.upsert(collection_name=collection, points=points)

    def search(
        self, collection: str, query: str, limit: int
    ) -> list[tuple[DocChunk, float]]:
        """Search for similar chunks.

        NOTE: Uses placeholder zero vector for query. In production:
        - Embed the query using the same embedding model
        - Replace the zero vector with the real query embedding

        Args:
            collection: Collection name
            query: Search query
            limit: Maximum results

        Returns:
            List of (chunk, score) tuples
        """
        self.ensure_collection(collection)

        # Placeholder query vector - replace with real embedding in production
        query_vector = [0.0] * self._vector_size

        results = self._client.search(
            collection_name=collection,
            query_vector=query_vector,
            limit=limit,
        )

        output: list[tuple[DocChunk, float]] = []
        for result in results:
            payload = result.payload or {}
            chunk = DocChunk(
                doc_id=payload.get("doc_id", ""),
                chunk_id=payload.get("chunk_id", ""),
                text=payload.get("text", ""),
                metadata=payload.get("metadata", {}),
            )
            output.append((chunk, float(result.score)))

        return output

    def delete_collection(self, collection: str) -> bool:
        """Delete a collection.

        Args:
            collection: Collection name

        Returns:
            True if deleted, False if didn't exist
        """
        existing = [c.name for c in self._client.get_collections().collections]
        if collection not in existing:
            return False
        self._client.delete_collection(collection_name=collection)
        return True

    def get_collection_info(self, collection: str) -> dict[str, Any]:
        """Get collection information.

        Args:
            collection: Collection name

        Returns:
            Collection info dict
        """
        info = self._client.get_collection(collection_name=collection)
        return {
            "name": collection,
            "points_count": info.points_count,
            "vectors_count": info.vectors_count,
            "status": info.status.value,
        }
