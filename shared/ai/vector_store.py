"""
Vector Store Module for SAHOOL AI
==================================
مخزن المتجهات للذكاء الاصطناعي في منصة سهول

Provides persistent vector storage and similarity search for:
- Agricultural knowledge embeddings
- Farm memory retrieval
- Semantic search across advisory content
- Offline-first architecture with local storage

Inspired by GenAI Learning Roadmap - Vector Databases component.

Author: SAHOOL Platform Team
Created: January 2026
"""

from __future__ import annotations

import json
import logging
import os
import sqlite3
import struct
import uuid
from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


class VectorStoreBackend(StrEnum):
    """Supported vector store backends"""

    # Local backends (offline-first)
    SQLITE = "sqlite"
    FILESYSTEM = "filesystem"
    MEMORY = "memory"

    # Cloud backends (optional)
    QDRANT = "qdrant"


class DistanceMetric(StrEnum):
    """Distance metrics for similarity search"""

    COSINE = "cosine"
    EUCLIDEAN = "euclidean"
    DOT_PRODUCT = "dot_product"


class IndexType(StrEnum):
    """Index types for efficient search"""

    FLAT = "flat"  # Exact search (brute force)
    HNSW = "hnsw"  # Hierarchical Navigable Small World
    IVF = "ivf"  # Inverted File Index


@dataclass
class VectorStoreConfig:
    """Configuration for vector store

    إعدادات مخزن المتجهات
    """

    # Backend settings
    backend: VectorStoreBackend = VectorStoreBackend.SQLITE
    storage_path: str | None = None

    # Qdrant settings (used when backend=QDRANT)
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333

    # Vector settings
    dimension: int = 768  # Default for multilingual-e5-base
    distance_metric: DistanceMetric = DistanceMetric.COSINE
    normalize_vectors: bool = True

    # Index settings
    index_type: IndexType = IndexType.FLAT
    ef_construction: int = 200  # HNSW parameter
    ef_search: int = 50  # HNSW parameter
    m: int = 16  # HNSW parameter

    # Performance settings
    batch_size: int = 1000
    cache_enabled: bool = True
    cache_size: int = 10000

    # Collection settings
    default_collection: str = "default"

    def __post_init__(self):
        """Initialize defaults from environment"""
        if self.storage_path is None:
            self.storage_path = os.getenv("VECTOR_STORE_PATH", str(Path.home() / ".sahool" / "vector_store"))
        self.qdrant_host = os.getenv("QDRANT_HOST", self.qdrant_host)
        self.qdrant_port = int(os.getenv("QDRANT_PORT", str(self.qdrant_port)))
        # Auto-select Qdrant backend if QDRANT_HOST is explicitly set
        if os.getenv("QDRANT_HOST"):
            self.backend = VectorStoreBackend.QDRANT


@dataclass
class VectorDocument:
    """A document with vector embedding

    مستند مع تضمين متجه
    """

    id: str
    vector: list[float]
    content: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    # Timestamps
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    # Collection
    collection: str = "default"

    def __post_init__(self):
        """Generate ID if not provided"""
        if not self.id:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "vector": self.vector,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "collection": self.collection,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VectorDocument:
        """Create from dictionary"""
        return cls(
            id=data["id"],
            vector=data["vector"],
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if "created_at" in data else datetime.now(UTC),
            updated_at=datetime.fromisoformat(data["updated_at"]) if "updated_at" in data else datetime.now(UTC),
            collection=data.get("collection", "default"),
        )


@dataclass
class SearchResult:
    """Result of a similarity search

    نتيجة البحث بالتشابه
    """

    document: VectorDocument
    score: float  # Similarity score (higher is more similar for cosine)
    distance: float  # Distance (lower is more similar)
    rank: int = 0

    @property
    def id(self) -> str:
        return self.document.id

    @property
    def content(self) -> str:
        return self.document.content

    @property
    def metadata(self) -> dict[str, Any]:
        return self.document.metadata


@dataclass
class CollectionInfo:
    """Information about a collection

    معلومات المجموعة
    """

    name: str
    document_count: int
    dimension: int
    distance_metric: DistanceMetric
    created_at: datetime
    updated_at: datetime
    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Vector Store Backends
# ============================================================================


class VectorStoreBackendBase(ABC):
    """Abstract base class for vector store backends

    الفئة الأساسية لواجهات مخزن المتجهات
    """

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the backend"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the backend"""
        pass

    @abstractmethod
    async def create_collection(
        self,
        name: str,
        dimension: int,
        distance_metric: DistanceMetric,
        metadata: dict[str, Any] | None = None,
    ) -> CollectionInfo:
        """Create a new collection"""
        pass

    @abstractmethod
    async def delete_collection(self, name: str) -> bool:
        """Delete a collection"""
        pass

    @abstractmethod
    async def list_collections(self) -> list[CollectionInfo]:
        """List all collections"""
        pass

    @abstractmethod
    async def get_collection_info(self, name: str) -> CollectionInfo | None:
        """Get collection information"""
        pass

    @abstractmethod
    async def insert(
        self,
        documents: list[VectorDocument],
        collection: str,
    ) -> list[str]:
        """Insert documents into collection"""
        pass

    @abstractmethod
    async def update(
        self,
        document: VectorDocument,
        collection: str,
    ) -> bool:
        """Update a document"""
        pass

    @abstractmethod
    async def delete(
        self,
        ids: list[str],
        collection: str,
    ) -> int:
        """Delete documents by IDs"""
        pass

    @abstractmethod
    async def get(
        self,
        id: str,
        collection: str,
    ) -> VectorDocument | None:
        """Get document by ID"""
        pass

    @abstractmethod
    async def search(
        self,
        vector: list[float],
        collection: str,
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors"""
        pass

    @abstractmethod
    async def count(self, collection: str) -> int:
        """Count documents in collection"""
        pass


class SQLiteBackend(VectorStoreBackendBase):
    """SQLite-based vector store backend

    واجهة SQLite لمخزن المتجهات

    Optimized for offline-first architecture with:
    - Persistent local storage
    - Efficient binary vector storage
    - Full-text search support
    - Transaction support
    """

    def __init__(
        self,
        storage_path: str,
        distance_metric: DistanceMetric = DistanceMetric.COSINE,
    ):
        self.storage_path = Path(storage_path)
        self.distance_metric = distance_metric
        self._conn: sqlite3.Connection | None = None

    def _serialize_vector(self, vector: list[float]) -> bytes:
        """Serialize vector to bytes for storage"""
        return struct.pack(f"{len(vector)}f", *vector)

    def _deserialize_vector(self, data: bytes) -> list[float]:
        """Deserialize vector from bytes"""
        count = len(data) // 4  # 4 bytes per float
        return list(struct.unpack(f"{count}f", data))

    def _cosine_similarity(self, v1: list[float], v2: list[float]) -> float:
        """Calculate cosine similarity"""
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = sum(a * a for a in v1) ** 0.5
        norm2 = sum(b * b for b in v2) ** 0.5
        return dot / (norm1 * norm2) if norm1 and norm2 else 0.0

    def _euclidean_distance(self, v1: list[float], v2: list[float]) -> float:
        """Calculate Euclidean distance"""
        return sum((a - b) ** 2 for a, b in zip(v1, v2)) ** 0.5

    def _dot_product(self, v1: list[float], v2: list[float]) -> float:
        """Calculate dot product"""
        return sum(a * b for a, b in zip(v1, v2))

    async def initialize(self) -> None:
        """Initialize SQLite database"""
        self.storage_path.mkdir(parents=True, exist_ok=True)
        db_path = self.storage_path / "vectors.db"

        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row

        # Create tables
        cursor = self._conn.cursor()

        # Collections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS collections (
                name TEXT PRIMARY KEY,
                dimension INTEGER NOT NULL,
                distance_metric TEXT NOT NULL,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Documents table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                id TEXT PRIMARY KEY,
                collection TEXT NOT NULL,
                vector BLOB NOT NULL,
                content TEXT,
                metadata TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (collection) REFERENCES collections(name)
            )
        """)

        # Indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_documents_collection
            ON documents(collection)
        """)

        # FTS5 for full-text search
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                id,
                content,
                content='documents',
                content_rowid='rowid'
            )
        """)

        self._conn.commit()
        logger.info(f"SQLite backend initialized at {db_path}")

    async def close(self) -> None:
        """Close database connection"""
        if self._conn:
            self._conn.close()
            self._conn = None

    async def create_collection(
        self,
        name: str,
        dimension: int,
        distance_metric: DistanceMetric,
        metadata: dict[str, Any] | None = None,
    ) -> CollectionInfo:
        """Create a new collection"""
        now = datetime.now(UTC).isoformat()

        cursor = self._conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO collections
            (name, dimension, distance_metric, metadata, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """,
            (
                name,
                dimension,
                distance_metric.value,
                json.dumps(metadata or {}),
                now,
                now,
            ),
        )
        self._conn.commit()

        return CollectionInfo(
            name=name,
            document_count=0,
            dimension=dimension,
            distance_metric=distance_metric,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
            metadata=metadata or {},
        )

    async def delete_collection(self, name: str) -> bool:
        """Delete a collection and all its documents"""
        cursor = self._conn.cursor()

        # Delete documents
        cursor.execute("DELETE FROM documents WHERE collection = ?", (name,))

        # Delete collection
        cursor.execute("DELETE FROM collections WHERE name = ?", (name,))

        self._conn.commit()
        return cursor.rowcount > 0

    async def list_collections(self) -> list[CollectionInfo]:
        """List all collections"""
        cursor = self._conn.cursor()
        cursor.execute("""
            SELECT c.*, COUNT(d.id) as doc_count
            FROM collections c
            LEFT JOIN documents d ON c.name = d.collection
            GROUP BY c.name
        """)

        results = []
        for row in cursor.fetchall():
            results.append(
                CollectionInfo(
                    name=row["name"],
                    document_count=row["doc_count"],
                    dimension=row["dimension"],
                    distance_metric=DistanceMetric(row["distance_metric"]),
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                )
            )

        return results

    async def get_collection_info(self, name: str) -> CollectionInfo | None:
        """Get collection information"""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT c.*, COUNT(d.id) as doc_count
            FROM collections c
            LEFT JOIN documents d ON c.name = d.collection
            WHERE c.name = ?
            GROUP BY c.name
        """,
            (name,),
        )

        row = cursor.fetchone()
        if not row:
            return None

        return CollectionInfo(
            name=row["name"],
            document_count=row["doc_count"],
            dimension=row["dimension"],
            distance_metric=DistanceMetric(row["distance_metric"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
        )

    async def insert(
        self,
        documents: list[VectorDocument],
        collection: str,
    ) -> list[str]:
        """Insert documents into collection"""
        cursor = self._conn.cursor()
        ids = []

        for doc in documents:
            cursor.execute(
                """
                INSERT OR REPLACE INTO documents
                (id, collection, vector, content, metadata, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    doc.id,
                    collection,
                    self._serialize_vector(doc.vector),
                    doc.content,
                    json.dumps(doc.metadata),
                    doc.created_at.isoformat(),
                    doc.updated_at.isoformat(),
                ),
            )
            ids.append(doc.id)

            # Update FTS
            cursor.execute(
                """
                INSERT OR REPLACE INTO documents_fts (id, content)
                VALUES (?, ?)
            """,
                (doc.id, doc.content),
            )

        # Update collection timestamp
        cursor.execute(
            """
            UPDATE collections SET updated_at = ?
            WHERE name = ?
        """,
            (datetime.now(UTC).isoformat(), collection),
        )

        self._conn.commit()
        return ids

    async def update(
        self,
        document: VectorDocument,
        collection: str,
    ) -> bool:
        """Update a document"""
        document.updated_at = datetime.now(UTC)
        cursor = self._conn.cursor()

        cursor.execute(
            """
            UPDATE documents
            SET vector = ?, content = ?, metadata = ?, updated_at = ?
            WHERE id = ? AND collection = ?
        """,
            (
                self._serialize_vector(document.vector),
                document.content,
                json.dumps(document.metadata),
                document.updated_at.isoformat(),
                document.id,
                collection,
            ),
        )

        # Update FTS
        cursor.execute(
            """
            INSERT OR REPLACE INTO documents_fts (id, content)
            VALUES (?, ?)
        """,
            (document.id, document.content),
        )

        self._conn.commit()
        return cursor.rowcount > 0

    async def delete(
        self,
        ids: list[str],
        collection: str,
    ) -> int:
        """Delete documents by IDs"""
        cursor = self._conn.cursor()

        # Using parameterized query with ? placeholders - safe from SQL injection
        placeholders = ",".join("?" * len(ids))
        delete_docs_sql = f"""
            DELETE FROM documents
            WHERE id IN ({placeholders}) AND collection = ?
        """  # nosec B608 - parameterized query with ? placeholders
        cursor.execute(  # nosemgrep: python.lang.security.audit.formatted-sql-query
            delete_docs_sql,
            (*ids, collection),
        )

        # Delete from FTS
        delete_fts_sql = f"""
            DELETE FROM documents_fts
            WHERE id IN ({placeholders})
        """  # nosec B608 - parameterized query with ? placeholders
        cursor.execute(  # nosemgrep: python.lang.security.audit.formatted-sql-query
            delete_fts_sql,
            ids,
        )

        self._conn.commit()
        return cursor.rowcount

    async def get(
        self,
        id: str,
        collection: str,
    ) -> VectorDocument | None:
        """Get document by ID"""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT * FROM documents
            WHERE id = ? AND collection = ?
        """,
            (id, collection),
        )

        row = cursor.fetchone()
        if not row:
            return None

        return VectorDocument(
            id=row["id"],
            vector=self._deserialize_vector(row["vector"]),
            content=row["content"] or "",
            metadata=json.loads(row["metadata"]) if row["metadata"] else {},
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            collection=row["collection"],
        )

    async def search(
        self,
        vector: list[float],
        collection: str,
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors"""
        cursor = self._conn.cursor()

        # Get documents in collection (brute force for FLAT index, capped at 50000 for safety)
        max_scan = 50000
        cursor.execute(
            """
            SELECT * FROM documents WHERE collection = ? LIMIT ?
        """,
            (collection, max_scan),
        )

        results = []
        for row in cursor.fetchall():
            doc_vector = self._deserialize_vector(row["vector"])
            metadata = json.loads(row["metadata"]) if row["metadata"] else {}

            # Apply metadata filter
            if filter:
                match = True
                for key, value in filter.items():
                    if key not in metadata or metadata[key] != value:
                        match = False
                        break
                if not match:
                    continue

            # Calculate similarity
            if self.distance_metric == DistanceMetric.COSINE:
                score = self._cosine_similarity(vector, doc_vector)
                distance = 1.0 - score
            elif self.distance_metric == DistanceMetric.EUCLIDEAN:
                distance = self._euclidean_distance(vector, doc_vector)
                score = 1.0 / (1.0 + distance)
            else:  # DOT_PRODUCT
                score = self._dot_product(vector, doc_vector)
                distance = -score  # Higher dot product = closer

            doc = VectorDocument(
                id=row["id"],
                vector=doc_vector,
                content=row["content"] or "",
                metadata=metadata,
                created_at=datetime.fromisoformat(row["created_at"]),
                updated_at=datetime.fromisoformat(row["updated_at"]),
                collection=row["collection"],
            )

            results.append(
                SearchResult(
                    document=doc,
                    score=score,
                    distance=distance,
                )
            )

        # Sort by score (descending) and take top_k
        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:top_k]

        # Add ranks
        for i, result in enumerate(results):
            result.rank = i + 1

        return results

    async def count(self, collection: str) -> int:
        """Count documents in collection"""
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT COUNT(*) FROM documents WHERE collection = ?
        """,
            (collection,),
        )
        return cursor.fetchone()[0]

    async def full_text_search(
        self,
        query: str,
        collection: str,
        top_k: int = 10,
    ) -> list[VectorDocument]:
        """Full-text search on document content

        بحث نصي كامل في محتوى المستندات
        """
        cursor = self._conn.cursor()
        cursor.execute(
            """
            SELECT d.* FROM documents d
            JOIN documents_fts fts ON d.id = fts.id
            WHERE documents_fts MATCH ? AND d.collection = ?
            ORDER BY rank
            LIMIT ?
        """,
            (query, collection, top_k),
        )

        results = []
        for row in cursor.fetchall():
            results.append(
                VectorDocument(
                    id=row["id"],
                    vector=self._deserialize_vector(row["vector"]),
                    content=row["content"] or "",
                    metadata=json.loads(row["metadata"]) if row["metadata"] else {},
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    collection=row["collection"],
                )
            )

        return results


class MemoryBackend(VectorStoreBackendBase):
    """In-memory vector store backend

    واجهة الذاكرة لمخزن المتجهات

    Fast but non-persistent storage for:
    - Testing
    - Temporary caching
    - Development
    """

    def __init__(self, distance_metric: DistanceMetric = DistanceMetric.COSINE):
        self.distance_metric = distance_metric
        self._collections: dict[str, CollectionInfo] = {}
        self._documents: dict[str, dict[str, VectorDocument]] = {}

    async def initialize(self) -> None:
        """Initialize memory backend"""
        logger.info("Memory backend initialized")

    async def close(self) -> None:
        """Close memory backend"""
        self._collections.clear()
        self._documents.clear()

    async def create_collection(
        self,
        name: str,
        dimension: int,
        distance_metric: DistanceMetric,
        metadata: dict[str, Any] | None = None,
    ) -> CollectionInfo:
        """Create a new collection"""
        now = datetime.now(UTC)

        info = CollectionInfo(
            name=name,
            document_count=0,
            dimension=dimension,
            distance_metric=distance_metric,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

        self._collections[name] = info
        self._documents[name] = {}

        return info

    async def delete_collection(self, name: str) -> bool:
        """Delete a collection"""
        if name in self._collections:
            del self._collections[name]
            del self._documents[name]
            return True
        return False

    async def list_collections(self) -> list[CollectionInfo]:
        """List all collections"""
        result = []
        for name, info in self._collections.items():
            info.document_count = len(self._documents.get(name, {}))
            result.append(info)
        return result

    async def get_collection_info(self, name: str) -> CollectionInfo | None:
        """Get collection information"""
        info = self._collections.get(name)
        if info:
            info.document_count = len(self._documents.get(name, {}))
        return info

    async def insert(
        self,
        documents: list[VectorDocument],
        collection: str,
    ) -> list[str]:
        """Insert documents"""
        if collection not in self._documents:
            self._documents[collection] = {}

        ids = []
        for doc in documents:
            self._documents[collection][doc.id] = doc
            ids.append(doc.id)

        if collection in self._collections:
            self._collections[collection].updated_at = datetime.now(UTC)

        return ids

    async def update(
        self,
        document: VectorDocument,
        collection: str,
    ) -> bool:
        """Update a document"""
        if collection in self._documents and document.id in self._documents[collection]:
            document.updated_at = datetime.now(UTC)
            self._documents[collection][document.id] = document
            return True
        return False

    async def delete(
        self,
        ids: list[str],
        collection: str,
    ) -> int:
        """Delete documents"""
        count = 0
        if collection in self._documents:
            for id in ids:
                if id in self._documents[collection]:
                    del self._documents[collection][id]
                    count += 1
        return count

    async def get(
        self,
        id: str,
        collection: str,
    ) -> VectorDocument | None:
        """Get document by ID"""
        return self._documents.get(collection, {}).get(id)

    async def search(
        self,
        vector: list[float],
        collection: str,
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors"""
        if collection not in self._documents:
            return []

        results = []
        for doc in self._documents[collection].values():
            # Apply filter
            if filter:
                match = True
                for key, value in filter.items():
                    if key not in doc.metadata or doc.metadata[key] != value:
                        match = False
                        break
                if not match:
                    continue

            # Calculate similarity
            if self.distance_metric == DistanceMetric.COSINE:
                dot = sum(a * b for a, b in zip(vector, doc.vector))
                norm1 = sum(a * a for a in vector) ** 0.5
                norm2 = sum(b * b for b in doc.vector) ** 0.5
                score = dot / (norm1 * norm2) if norm1 and norm2 else 0.0
                distance = 1.0 - score
            elif self.distance_metric == DistanceMetric.EUCLIDEAN:
                distance = sum((a - b) ** 2 for a, b in zip(vector, doc.vector)) ** 0.5
                score = 1.0 / (1.0 + distance)
            else:
                score = sum(a * b for a, b in zip(vector, doc.vector))
                distance = -score

            results.append(
                SearchResult(
                    document=doc,
                    score=score,
                    distance=distance,
                )
            )

        results.sort(key=lambda x: x.score, reverse=True)
        results = results[:top_k]

        for i, r in enumerate(results):
            r.rank = i + 1

        return results

    async def count(self, collection: str) -> int:
        """Count documents"""
        return len(self._documents.get(collection, {}))


# ============================================================================
# Qdrant Backend
# ============================================================================


class QdrantBackend(VectorStoreBackendBase):
    """Qdrant vector database backend

    واجهة Qdrant لمخزن المتجهات

    Production-grade vector search with:
    - HNSW indexing for fast ANN search
    - Payload filtering
    - Collection management
    - Horizontal scalability

    Requires: pip install qdrant-client
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6333,
        distance_metric: DistanceMetric = DistanceMetric.COSINE,
    ):
        self.host = host
        self.port = port
        self.distance_metric = distance_metric
        self._client: Any = None

    def _get_qdrant_distance(self) -> Any:
        """Map DistanceMetric to Qdrant Distance enum"""
        from qdrant_client.models import Distance

        mapping = {
            DistanceMetric.COSINE: Distance.COSINE,
            DistanceMetric.EUCLIDEAN: Distance.EUCLID,
            DistanceMetric.DOT_PRODUCT: Distance.DOT,
        }
        return mapping[self.distance_metric]

    async def initialize(self) -> None:
        """Initialize Qdrant connection"""
        try:
            from qdrant_client import QdrantClient

            self._client = QdrantClient(host=self.host, port=self.port)
            # Verify connection
            self._client.get_collections()
            logger.info(f"Qdrant backend initialized at {self.host}:{self.port}")
        except ImportError:
            raise ImportError("qdrant-client is required for Qdrant backend. Install with: pip install qdrant-client")
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Qdrant at {self.host}:{self.port}: {e}")

    async def close(self) -> None:
        """Close Qdrant connection"""
        if self._client:
            self._client.close()
            self._client = None

    async def create_collection(
        self,
        name: str,
        dimension: int,
        distance_metric: DistanceMetric,
        metadata: dict[str, Any] | None = None,
    ) -> CollectionInfo:
        """Create a new Qdrant collection"""
        from qdrant_client.models import VectorParams

        self.distance_metric = distance_metric

        collections = self._client.get_collections().collections
        if not any(c.name == name for c in collections):
            self._client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=dimension,
                    distance=self._get_qdrant_distance(),
                ),
            )

        now = datetime.now(UTC)
        return CollectionInfo(
            name=name,
            document_count=0,
            dimension=dimension,
            distance_metric=distance_metric,
            created_at=now,
            updated_at=now,
            metadata=metadata or {},
        )

    async def delete_collection(self, name: str) -> bool:
        """Delete a Qdrant collection"""
        try:
            self._client.delete_collection(collection_name=name)
            return True
        except Exception:
            return False

    async def list_collections(self) -> list[CollectionInfo]:
        """List all Qdrant collections"""
        collections = self._client.get_collections().collections
        results = []
        for c in collections:
            info = self._client.get_collection(collection_name=c.name)
            results.append(
                CollectionInfo(
                    name=c.name,
                    document_count=info.points_count or 0,
                    dimension=info.config.params.vectors.size if info.config.params.vectors else 0,
                    distance_metric=self.distance_metric,
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                )
            )
        return results

    async def get_collection_info(self, name: str) -> CollectionInfo | None:
        """Get Qdrant collection info"""
        try:
            info = self._client.get_collection(collection_name=name)
            return CollectionInfo(
                name=name,
                document_count=info.points_count or 0,
                dimension=info.config.params.vectors.size if info.config.params.vectors else 0,
                distance_metric=self.distance_metric,
                created_at=datetime.now(UTC),
                updated_at=datetime.now(UTC),
            )
        except Exception:
            return None

    async def insert(
        self,
        documents: list[VectorDocument],
        collection: str,
    ) -> list[str]:
        """Insert documents into Qdrant"""
        from qdrant_client.models import PointStruct

        points = []
        ids = []
        for doc in documents:
            payload = {
                "content": doc.content,
                "created_at": doc.created_at.isoformat(),
                "updated_at": doc.updated_at.isoformat(),
                **doc.metadata,
            }
            points.append(
                PointStruct(
                    id=doc.id,
                    vector=doc.vector,
                    payload=payload,
                )
            )
            ids.append(doc.id)

        self._client.upsert(collection_name=collection, points=points)
        return ids

    async def update(
        self,
        document: VectorDocument,
        collection: str,
    ) -> bool:
        """Update a document in Qdrant"""
        from qdrant_client.models import PointStruct

        document.updated_at = datetime.now(UTC)
        payload = {
            "content": document.content,
            "created_at": document.created_at.isoformat(),
            "updated_at": document.updated_at.isoformat(),
            **document.metadata,
        }
        self._client.upsert(
            collection_name=collection,
            points=[
                PointStruct(
                    id=document.id,
                    vector=document.vector,
                    payload=payload,
                )
            ],
        )
        return True

    async def delete(
        self,
        ids: list[str],
        collection: str,
    ) -> int:
        """Delete documents from Qdrant"""
        from qdrant_client.models import PointIdsList

        self._client.delete(
            collection_name=collection,
            points_selector=PointIdsList(points=ids),
        )
        return len(ids)

    async def get(
        self,
        id: str,
        collection: str,
    ) -> VectorDocument | None:
        """Get document by ID from Qdrant"""
        results = self._client.retrieve(
            collection_name=collection,
            ids=[id],
            with_vectors=True,
        )
        if not results:
            return None

        point = results[0]
        payload = point.payload or {}
        metadata = {k: v for k, v in payload.items() if k not in ("content", "created_at", "updated_at")}

        return VectorDocument(
            id=str(point.id),
            vector=point.vector,
            content=payload.get("content", ""),
            metadata=metadata,
            created_at=datetime.fromisoformat(payload["created_at"]) if "created_at" in payload else datetime.now(UTC),
            updated_at=datetime.fromisoformat(payload["updated_at"]) if "updated_at" in payload else datetime.now(UTC),
            collection=collection,
        )

    async def search(
        self,
        vector: list[float],
        collection: str,
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Search for similar vectors in Qdrant"""
        from qdrant_client.models import FieldCondition, Filter, MatchValue

        qdrant_filter = None
        if filter:
            conditions = []
            for key, value in filter.items():
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
            qdrant_filter = Filter(must=conditions)

        hits = self._client.search(
            collection_name=collection,
            query_vector=vector,
            limit=top_k,
            query_filter=qdrant_filter,
            with_vectors=True,
        )

        results = []
        for rank, hit in enumerate(hits, 1):
            payload = hit.payload or {}
            metadata = {k: v for k, v in payload.items() if k not in ("content", "created_at", "updated_at")}

            doc = VectorDocument(
                id=str(hit.id),
                vector=hit.vector or [],
                content=payload.get("content", ""),
                metadata=metadata,
                collection=collection,
            )

            score = hit.score
            distance = 1.0 - score if self.distance_metric == DistanceMetric.COSINE else score

            results.append(
                SearchResult(
                    document=doc,
                    score=score,
                    distance=distance,
                    rank=rank,
                )
            )

        return results

    async def count(self, collection: str) -> int:
        """Count documents in Qdrant collection"""
        try:
            info = self._client.get_collection(collection_name=collection)
            return info.points_count or 0
        except Exception:
            return 0


# ============================================================================
# Main Vector Store Class
# ============================================================================


class VectorStore:
    """Main vector store class with high-level operations

    مخزن المتجهات الرئيسي

    Provides:
    - Document storage and retrieval
    - Similarity search
    - Metadata filtering
    - Integration with embedding providers

    Example:
        store = VectorStore()
        await store.initialize()

        # Add documents
        await store.add(
            texts=["Agricultural advice for wheat", "نصائح زراعية للقمح"],
            metadatas=[{"crop": "wheat"}, {"crop": "wheat", "lang": "ar"}],
            collection="advisories",
        )

        # Search
        results = await store.search(
            query="wheat irrigation",
            collection="advisories",
            top_k=5,
        )
    """

    def __init__(self, config: VectorStoreConfig | None = None):
        self.config = config or VectorStoreConfig()

        # Backend
        self._backend: VectorStoreBackendBase | None = None

        # Embedding function (to be set)
        self._embed_fn: Callable | None = None

        # Statistics
        self._stats = {
            "total_inserts": 0,
            "total_searches": 0,
            "total_deletes": 0,
        }

    async def initialize(self) -> None:
        """Initialize vector store"""
        # Create backend
        if self.config.backend == VectorStoreBackend.SQLITE:
            self._backend = SQLiteBackend(
                storage_path=self.config.storage_path,
                distance_metric=self.config.distance_metric,
            )
        elif self.config.backend == VectorStoreBackend.MEMORY:
            self._backend = MemoryBackend(
                distance_metric=self.config.distance_metric,
            )
        elif self.config.backend == VectorStoreBackend.QDRANT:
            self._backend = QdrantBackend(
                host=self.config.qdrant_host,
                port=self.config.qdrant_port,
                distance_metric=self.config.distance_metric,
            )
        else:
            raise ValueError(f"Unsupported backend: {self.config.backend}")

        await self._backend.initialize()

        # Create default collection
        collections = await self._backend.list_collections()
        if not any(c.name == self.config.default_collection for c in collections):
            await self._backend.create_collection(
                name=self.config.default_collection,
                dimension=self.config.dimension,
                distance_metric=self.config.distance_metric,
            )

        logger.info(f"Vector store initialized with {self.config.backend.value} backend")

    async def close(self) -> None:
        """Close vector store"""
        if self._backend:
            await self._backend.close()

    def set_embedding_function(self, fn: Callable) -> None:
        """Set embedding function for automatic text embedding

        تعيين دالة التضمين
        """
        self._embed_fn = fn

    async def create_collection(
        self,
        name: str,
        dimension: int | None = None,
        metadata: dict[str, Any] | None = None,
        tenant_id: str | None = None,
    ) -> CollectionInfo:
        """Create a new collection

        إنشاء مجموعة جديدة

        Args:
            name: Collection name
            dimension: Vector dimension (uses config default if None)
            metadata: Optional collection metadata
            tenant_id: Tenant identifier for namespace isolation
        """
        collection_name = f"{tenant_id}:{name}" if tenant_id else name
        return await self._backend.create_collection(
            name=collection_name,
            dimension=dimension or self.config.dimension,
            distance_metric=self.config.distance_metric,
            metadata=metadata,
        )

    async def delete_collection(self, name: str) -> bool:
        """Delete a collection

        حذف مجموعة
        """
        return await self._backend.delete_collection(name)

    async def list_collections(self) -> list[CollectionInfo]:
        """List all collections

        قائمة المجموعات
        """
        return await self._backend.list_collections()

    async def add(
        self,
        texts: list[str] | None = None,
        vectors: list[list[float]] | None = None,
        ids: list[str] | None = None,
        metadatas: list[dict[str, Any]] | None = None,
        collection: str | None = None,
    ) -> list[str]:
        """Add documents to collection

        إضافة مستندات للمجموعة

        Args:
            texts: Text content (will be embedded if embed_fn is set)
            vectors: Pre-computed vectors (optional if texts provided)
            ids: Document IDs (auto-generated if not provided)
            metadatas: Metadata for each document
            collection: Collection name

        Returns:
            List of document IDs
        """
        collection = collection or self.config.default_collection

        # Ensure collection exists
        info = await self._backend.get_collection_info(collection)
        if not info:
            await self.create_collection(collection)

        # Determine count
        count = len(texts) if texts else len(vectors) if vectors else 0
        if count == 0:
            return []

        # Generate IDs if not provided
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in range(count)]

        # Generate vectors if needed
        if vectors is None:
            if texts is None:
                raise ValueError("Either texts or vectors must be provided")
            if self._embed_fn is None:
                raise ValueError("Embedding function not set. Call set_embedding_function() first.")

            # Embed texts
            vectors = await self._embed_fn(texts)

        # Create documents
        documents = []
        for i in range(count):
            doc = VectorDocument(
                id=ids[i],
                vector=vectors[i],
                content=texts[i] if texts else "",
                metadata=metadatas[i] if metadatas else {},
                collection=collection,
            )
            documents.append(doc)

        # Insert
        result_ids = await self._backend.insert(documents, collection)
        self._stats["total_inserts"] += len(result_ids)

        return result_ids

    async def search(
        self,
        query: str | None = None,
        vector: list[float] | None = None,
        collection: str | None = None,
        top_k: int = 10,
        filter: dict[str, Any] | None = None,
        include_content: bool = True,
    ) -> list[SearchResult]:
        """Search for similar documents

        البحث عن مستندات متشابهة

        Args:
            query: Query text (will be embedded)
            vector: Query vector (alternative to query)
            collection: Collection to search
            top_k: Number of results
            filter: Metadata filter
            include_content: Include document content

        Returns:
            List of SearchResult
        """
        collection = collection or self.config.default_collection

        # Get query vector
        if vector is None:
            if query is None:
                raise ValueError("Either query or vector must be provided")
            if self._embed_fn is None:
                raise ValueError("Embedding function not set")

            vectors = await self._embed_fn([query])
            vector = vectors[0]

        # Search
        results = await self._backend.search(
            vector=vector,
            collection=collection,
            top_k=top_k,
            filter=filter,
        )

        self._stats["total_searches"] += 1

        return results

    async def get(
        self,
        id: str,
        collection: str | None = None,
    ) -> VectorDocument | None:
        """Get document by ID

        الحصول على مستند بواسطة المعرف
        """
        collection = collection or self.config.default_collection
        return await self._backend.get(id, collection)

    async def delete(
        self,
        ids: list[str],
        collection: str | None = None,
    ) -> int:
        """Delete documents by IDs

        حذف مستندات
        """
        collection = collection or self.config.default_collection
        count = await self._backend.delete(ids, collection)
        self._stats["total_deletes"] += count
        return count

    async def count(self, collection: str | None = None) -> int:
        """Count documents in collection

        عدد المستندات في المجموعة
        """
        collection = collection or self.config.default_collection
        return await self._backend.count(collection)

    async def update(
        self,
        id: str,
        text: str | None = None,
        vector: list[float] | None = None,
        metadata: dict[str, Any] | None = None,
        collection: str | None = None,
    ) -> bool:
        """Update a document

        تحديث مستند
        """
        collection = collection or self.config.default_collection

        # Get existing document
        doc = await self._backend.get(id, collection)
        if not doc:
            return False

        # Update fields
        if text is not None:
            doc.content = text
            if self._embed_fn:
                vectors = await self._embed_fn([text])
                doc.vector = vectors[0]

        if vector is not None:
            doc.vector = vector

        if metadata is not None:
            doc.metadata.update(metadata)

        return await self._backend.update(doc, collection)

    @property
    def stats(self) -> dict[str, Any]:
        """Get statistics"""
        return self._stats.copy()


# ============================================================================
# Singleton and Convenience Functions
# ============================================================================

_store_instance: VectorStore | None = None


async def get_vector_store(
    config: VectorStoreConfig | None = None,
) -> VectorStore:
    """Get or create vector store singleton

    الحصول على مخزن المتجهات
    """
    global _store_instance

    if _store_instance is None or config is not None:
        _store_instance = VectorStore(config)
        await _store_instance.initialize()

    return _store_instance


async def add_documents(
    texts: list[str],
    metadatas: list[dict[str, Any]] | None = None,
    collection: str = "default",
) -> list[str]:
    """Convenience function to add documents

    دالة مساعدة لإضافة مستندات
    """
    store = await get_vector_store()
    return await store.add(
        texts=texts,
        metadatas=metadatas,
        collection=collection,
    )


async def search_documents(
    query: str,
    collection: str = "default",
    top_k: int = 10,
    filter: dict[str, Any] | None = None,
) -> list[SearchResult]:
    """Convenience function to search documents

    دالة مساعدة للبحث في المستندات
    """
    store = await get_vector_store()
    return await store.search(
        query=query,
        collection=collection,
        top_k=top_k,
        filter=filter,
    )


# Export all public symbols
__all__ = [
    # Config
    "VectorStoreConfig",
    # Enums
    "VectorStoreBackend",
    "DistanceMetric",
    "IndexType",
    # Data classes
    "VectorDocument",
    "SearchResult",
    "CollectionInfo",
    # Backends
    "VectorStoreBackendBase",
    "SQLiteBackend",
    "MemoryBackend",
    "QdrantBackend",
    # Main class
    "VectorStore",
    # Convenience functions
    "get_vector_store",
    "add_documents",
    "search_documents",
]
