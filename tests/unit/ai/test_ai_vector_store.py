"""
Tests for Vector Store Module
==============================
اختبارات وحدة مخزن المتجهات

Tests for persistent vector storage including:
- Configuration management
- Document storage and retrieval
- Similarity search
- Multiple backends (SQLite, Memory)
- Collection management

Author: SAHOOL Platform Team
Created: January 2026
"""

import shutil
import tempfile
from datetime import UTC, datetime, timezone
from pathlib import Path

import pytest

from shared.ai.vector_store import (
    CollectionInfo,
    DistanceMetric,
    IndexType,
    MemoryBackend,
    SearchResult,
    SQLiteBackend,
    VectorDocument,
    VectorStore,
    VectorStoreBackend,
    VectorStoreBackendBase,
    VectorStoreConfig,
    add_documents,
    get_vector_store,
    search_documents,
)

# ============================================================================
# Config Tests
# ============================================================================


class TestVectorStoreConfig:
    """Tests for VectorStoreConfig"""

    def test_default_config(self):
        """Test default configuration values"""
        config = VectorStoreConfig()

        assert config.backend == VectorStoreBackend.SQLITE
        assert config.dimension == 768
        assert config.distance_metric == DistanceMetric.COSINE
        assert config.normalize_vectors is True
        assert config.index_type == IndexType.FLAT
        assert config.cache_enabled is True
        assert config.default_collection == "default"

    def test_custom_config(self):
        """Test custom configuration"""
        config = VectorStoreConfig(
            backend=VectorStoreBackend.MEMORY,
            dimension=1024,
            distance_metric=DistanceMetric.EUCLIDEAN,
            default_collection="custom",
        )

        assert config.backend == VectorStoreBackend.MEMORY
        assert config.dimension == 1024
        assert config.distance_metric == DistanceMetric.EUCLIDEAN
        assert config.default_collection == "custom"


# ============================================================================
# Enum Tests
# ============================================================================


class TestEnums:
    """Tests for enumeration types"""

    def test_backend_types(self):
        """Test VectorStoreBackend enum values"""
        assert VectorStoreBackend.SQLITE.value == "sqlite"
        assert VectorStoreBackend.FILESYSTEM.value == "filesystem"
        assert VectorStoreBackend.MEMORY.value == "memory"

    def test_distance_metrics(self):
        """Test DistanceMetric enum values"""
        assert DistanceMetric.COSINE.value == "cosine"
        assert DistanceMetric.EUCLIDEAN.value == "euclidean"
        assert DistanceMetric.DOT_PRODUCT.value == "dot_product"

    def test_index_types(self):
        """Test IndexType enum values"""
        assert IndexType.FLAT.value == "flat"
        assert IndexType.HNSW.value == "hnsw"
        assert IndexType.IVF.value == "ivf"


# ============================================================================
# Data Class Tests
# ============================================================================


class TestVectorDocument:
    """Tests for VectorDocument data class"""

    def test_document_creation(self):
        """Test creating a vector document"""
        doc = VectorDocument(
            id="doc_001",
            vector=[0.1, 0.2, 0.3],
            content="Test content",
            metadata={"key": "value"},
        )

        assert doc.id == "doc_001"
        assert doc.vector == [0.1, 0.2, 0.3]
        assert doc.content == "Test content"
        assert doc.metadata == {"key": "value"}

    def test_document_auto_id(self):
        """Test auto-generated document ID"""
        doc = VectorDocument(
            id="",
            vector=[0.1, 0.2],
        )

        assert doc.id != ""
        assert len(doc.id) > 0

    def test_document_to_dict(self):
        """Test converting document to dictionary"""
        doc = VectorDocument(
            id="doc_001",
            vector=[0.1, 0.2],
            content="Test",
            metadata={"key": "value"},
            collection="test_collection",
        )

        data = doc.to_dict()

        assert data["id"] == "doc_001"
        assert data["vector"] == [0.1, 0.2]
        assert data["content"] == "Test"
        assert data["metadata"] == {"key": "value"}
        assert data["collection"] == "test_collection"

    def test_document_from_dict(self):
        """Test creating document from dictionary"""
        data = {
            "id": "doc_002",
            "vector": [0.3, 0.4],
            "content": "Test content",
            "metadata": {"type": "test"},
            "created_at": datetime.now(UTC).isoformat(),
            "updated_at": datetime.now(UTC).isoformat(),
            "collection": "default",
        }

        doc = VectorDocument.from_dict(data)

        assert doc.id == "doc_002"
        assert doc.vector == [0.3, 0.4]
        assert doc.content == "Test content"


class TestSearchResult:
    """Tests for SearchResult data class"""

    def test_search_result_creation(self):
        """Test creating a search result"""
        doc = VectorDocument(
            id="doc_001",
            vector=[0.1, 0.2],
            content="Test",
        )

        result = SearchResult(
            document=doc,
            score=0.95,
            distance=0.05,
            rank=1,
        )

        assert result.document == doc
        assert result.score == 0.95
        assert result.distance == 0.05
        assert result.rank == 1

    def test_search_result_properties(self):
        """Test search result properties"""
        doc = VectorDocument(
            id="doc_001",
            vector=[0.1, 0.2],
            content="Test content",
            metadata={"key": "value"},
        )

        result = SearchResult(
            document=doc,
            score=0.9,
            distance=0.1,
        )

        assert result.id == "doc_001"
        assert result.content == "Test content"
        assert result.metadata == {"key": "value"}


class TestCollectionInfo:
    """Tests for CollectionInfo data class"""

    def test_collection_info_creation(self):
        """Test creating collection info"""
        info = CollectionInfo(
            name="test_collection",
            document_count=100,
            dimension=768,
            distance_metric=DistanceMetric.COSINE,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
            metadata={"description": "Test collection"},
        )

        assert info.name == "test_collection"
        assert info.document_count == 100
        assert info.dimension == 768
        assert info.distance_metric == DistanceMetric.COSINE


# ============================================================================
# Memory Backend Tests
# ============================================================================


class TestMemoryBackend:
    """Tests for MemoryBackend"""

    @pytest.fixture
    def backend(self):
        """Create a memory backend for testing"""
        return MemoryBackend()

    @pytest.mark.asyncio
    async def test_initialize(self, backend):
        """Test backend initialization"""
        await backend.initialize()
        # Should not raise

    @pytest.mark.asyncio
    async def test_create_collection(self, backend):
        """Test creating a collection"""
        await backend.initialize()

        info = await backend.create_collection(
            name="test_collection",
            dimension=768,
            distance_metric=DistanceMetric.COSINE,
        )

        assert info.name == "test_collection"
        assert info.dimension == 768

    @pytest.mark.asyncio
    async def test_list_collections(self, backend):
        """Test listing collections"""
        await backend.initialize()

        await backend.create_collection("collection1", 768, DistanceMetric.COSINE)
        await backend.create_collection("collection2", 1024, DistanceMetric.EUCLIDEAN)

        collections = await backend.list_collections()

        assert len(collections) == 2
        assert any(c.name == "collection1" for c in collections)
        assert any(c.name == "collection2" for c in collections)

    @pytest.mark.asyncio
    async def test_delete_collection(self, backend):
        """Test deleting a collection"""
        await backend.initialize()

        await backend.create_collection("to_delete", 768, DistanceMetric.COSINE)

        result = await backend.delete_collection("to_delete")
        assert result is True

        info = await backend.get_collection_info("to_delete")
        assert info is None

    @pytest.mark.asyncio
    async def test_insert_documents(self, backend):
        """Test inserting documents"""
        await backend.initialize()
        await backend.create_collection("test", 3, DistanceMetric.COSINE)

        docs = [
            VectorDocument(id="doc1", vector=[0.1, 0.2, 0.3], content="Content 1"),
            VectorDocument(id="doc2", vector=[0.4, 0.5, 0.6], content="Content 2"),
        ]

        ids = await backend.insert(docs, "test")

        assert ids == ["doc1", "doc2"]
        assert await backend.count("test") == 2

    @pytest.mark.asyncio
    async def test_get_document(self, backend):
        """Test getting a document"""
        await backend.initialize()
        await backend.create_collection("test", 3, DistanceMetric.COSINE)

        doc = VectorDocument(id="doc1", vector=[0.1, 0.2, 0.3], content="Test")
        await backend.insert([doc], "test")

        retrieved = await backend.get("doc1", "test")

        assert retrieved is not None
        assert retrieved.id == "doc1"
        assert retrieved.content == "Test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_document(self, backend):
        """Test getting a non-existent document"""
        await backend.initialize()
        await backend.create_collection("test", 3, DistanceMetric.COSINE)

        retrieved = await backend.get("nonexistent", "test")

        assert retrieved is None

    @pytest.mark.asyncio
    async def test_delete_documents(self, backend):
        """Test deleting documents"""
        await backend.initialize()
        await backend.create_collection("test", 3, DistanceMetric.COSINE)

        docs = [
            VectorDocument(id="doc1", vector=[0.1, 0.2, 0.3]),
            VectorDocument(id="doc2", vector=[0.4, 0.5, 0.6]),
        ]
        await backend.insert(docs, "test")

        count = await backend.delete(["doc1"], "test")

        assert count == 1
        assert await backend.count("test") == 1
        assert await backend.get("doc1", "test") is None

    @pytest.mark.asyncio
    async def test_search_cosine(self, backend):
        """Test cosine similarity search"""
        await backend.initialize()
        await backend.create_collection("test", 3, DistanceMetric.COSINE)

        docs = [
            VectorDocument(id="doc1", vector=[1.0, 0.0, 0.0], content="X axis"),
            VectorDocument(id="doc2", vector=[0.0, 1.0, 0.0], content="Y axis"),
            VectorDocument(id="doc3", vector=[0.9, 0.1, 0.0], content="Near X"),
        ]
        await backend.insert(docs, "test")

        # Search near X axis
        results = await backend.search([1.0, 0.0, 0.0], "test", top_k=2)

        assert len(results) == 2
        assert results[0].id == "doc1"  # Exact match
        assert results[1].id == "doc3"  # Similar to X

    @pytest.mark.asyncio
    async def test_search_with_filter(self, backend):
        """Test search with metadata filter"""
        await backend.initialize()
        await backend.create_collection("test", 3, DistanceMetric.COSINE)

        docs = [
            VectorDocument(id="doc1", vector=[1.0, 0.0, 0.0], metadata={"type": "A"}),
            VectorDocument(id="doc2", vector=[0.9, 0.1, 0.0], metadata={"type": "B"}),
            VectorDocument(id="doc3", vector=[0.8, 0.2, 0.0], metadata={"type": "A"}),
        ]
        await backend.insert(docs, "test")

        results = await backend.search(
            [1.0, 0.0, 0.0],
            "test",
            top_k=10,
            filter={"type": "A"},
        )

        assert len(results) == 2
        assert all(r.metadata["type"] == "A" for r in results)

    @pytest.mark.asyncio
    async def test_update_document(self, backend):
        """Test updating a document"""
        await backend.initialize()
        await backend.create_collection("test", 3, DistanceMetric.COSINE)

        doc = VectorDocument(id="doc1", vector=[0.1, 0.2, 0.3], content="Original")
        await backend.insert([doc], "test")

        doc.content = "Updated"
        doc.vector = [0.4, 0.5, 0.6]
        result = await backend.update(doc, "test")

        assert result is True

        updated = await backend.get("doc1", "test")
        assert updated.content == "Updated"

    @pytest.mark.asyncio
    async def test_close(self, backend):
        """Test closing backend"""
        await backend.initialize()

        await backend.close()

        # Collections should be cleared
        collections = await backend.list_collections()
        assert len(collections) == 0


# ============================================================================
# SQLite Backend Tests
# ============================================================================


class TestSQLiteBackend:
    """Tests for SQLiteBackend"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.fixture
    def backend(self, temp_dir):
        """Create a SQLite backend for testing"""
        return SQLiteBackend(storage_path=temp_dir)

    @pytest.mark.asyncio
    async def test_initialize(self, backend, temp_dir):
        """Test backend initialization"""
        await backend.initialize()

        db_path = Path(temp_dir) / "vectors.db"
        assert db_path.exists()

    @pytest.mark.asyncio
    async def test_create_and_list_collections(self, backend):
        """Test creating and listing collections"""
        await backend.initialize()

        await backend.create_collection("collection1", 768, DistanceMetric.COSINE)
        await backend.create_collection("collection2", 1024, DistanceMetric.EUCLIDEAN)

        collections = await backend.list_collections()

        assert len(collections) == 2

    @pytest.mark.asyncio
    async def test_insert_and_search(self, backend):
        """Test inserting and searching documents"""
        await backend.initialize()
        await backend.create_collection("test", 3, DistanceMetric.COSINE)

        docs = [
            VectorDocument(id="doc1", vector=[1.0, 0.0, 0.0], content="X"),
            VectorDocument(id="doc2", vector=[0.0, 1.0, 0.0], content="Y"),
            VectorDocument(id="doc3", vector=[0.0, 0.0, 1.0], content="Z"),
        ]
        await backend.insert(docs, "test")

        results = await backend.search([1.0, 0.0, 0.0], "test", top_k=1)

        assert len(results) == 1
        assert results[0].id == "doc1"

    @pytest.mark.asyncio
    async def test_persistence(self, temp_dir):
        """Test that data persists across backend instances"""
        # First backend instance
        backend1 = SQLiteBackend(storage_path=temp_dir)
        await backend1.initialize()
        await backend1.create_collection("test", 3, DistanceMetric.COSINE)

        doc = VectorDocument(id="doc1", vector=[0.1, 0.2, 0.3], content="Test")
        await backend1.insert([doc], "test")
        await backend1.close()

        # Second backend instance
        backend2 = SQLiteBackend(storage_path=temp_dir)
        await backend2.initialize()

        retrieved = await backend2.get("doc1", "test")
        assert retrieved is not None
        assert retrieved.content == "Test"

        await backend2.close()


# ============================================================================
# Main VectorStore Tests
# ============================================================================


class TestVectorStore:
    """Tests for main VectorStore class"""

    @pytest.fixture
    def memory_store(self):
        """Create a memory-backed vector store"""
        config = VectorStoreConfig(backend=VectorStoreBackend.MEMORY)
        return VectorStore(config)

    @pytest.mark.asyncio
    async def test_initialize(self, memory_store):
        """Test vector store initialization"""
        await memory_store.initialize()

        # Default collection should exist
        collections = await memory_store.list_collections()
        assert any(c.name == "default" for c in collections)

    @pytest.mark.asyncio
    async def test_create_collection(self, memory_store):
        """Test creating a collection"""
        await memory_store.initialize()

        info = await memory_store.create_collection(
            name="test_collection",
            dimension=512,
        )

        assert info.name == "test_collection"
        assert info.dimension == 512

    @pytest.mark.asyncio
    async def test_add_with_vectors(self, memory_store):
        """Test adding documents with vectors"""
        await memory_store.initialize()

        ids = await memory_store.add(
            vectors=[[0.1, 0.2], [0.3, 0.4]],
            texts=["Text 1", "Text 2"],
            metadatas=[{"key": "a"}, {"key": "b"}],
        )

        assert len(ids) == 2
        assert await memory_store.count() == 2

    @pytest.mark.asyncio
    async def test_add_with_custom_ids(self, memory_store):
        """Test adding documents with custom IDs"""
        await memory_store.initialize()

        ids = await memory_store.add(
            vectors=[[0.1, 0.2]],
            ids=["custom_id"],
        )

        assert ids == ["custom_id"]

        doc = await memory_store.get("custom_id")
        assert doc is not None

    @pytest.mark.asyncio
    async def test_search_with_vector(self, memory_store):
        """Test searching with a vector"""
        await memory_store.initialize()

        # Tag the test corpus with tenant_id="__GLOBAL__" so the
        # fail-closed search guard in VectorStore lets it through.
        await memory_store.add(
            vectors=[[1.0, 0.0], [0.0, 1.0], [0.9, 0.1]],
            texts=["X", "Y", "Near X"],
            metadatas=[{"tenant_id": "__GLOBAL__"}] * 3,
        )

        results = await memory_store.search(
            vector=[1.0, 0.0],
            top_k=2,
            tenant_id="__GLOBAL__",
        )

        assert len(results) == 2
        assert results[0].content == "X"  # Exact match

    @pytest.mark.asyncio
    async def test_get_document(self, memory_store):
        """Test getting a document by ID"""
        await memory_store.initialize()

        ids = await memory_store.add(
            vectors=[[0.1, 0.2]],
            texts=["Test content"],
            ids=["test_id"],
        )

        doc = await memory_store.get("test_id")

        assert doc is not None
        assert doc.content == "Test content"

    @pytest.mark.asyncio
    async def test_delete_documents(self, memory_store):
        """Test deleting documents"""
        await memory_store.initialize()

        await memory_store.add(
            vectors=[[0.1, 0.2], [0.3, 0.4]],
            ids=["doc1", "doc2"],
        )

        count = await memory_store.delete(["doc1"])

        assert count == 1
        assert await memory_store.count() == 1

    @pytest.mark.asyncio
    async def test_update_document(self, memory_store):
        """Test updating a document"""
        await memory_store.initialize()

        await memory_store.add(
            vectors=[[0.1, 0.2]],
            texts=["Original"],
            ids=["doc1"],
        )

        result = await memory_store.update(
            id="doc1",
            vector=[0.3, 0.4],
            metadata={"updated": True},
        )

        assert result is True

        doc = await memory_store.get("doc1")
        assert doc.metadata.get("updated") is True

    @pytest.mark.asyncio
    async def test_stats(self, memory_store):
        """Test getting statistics"""
        await memory_store.initialize()

        await memory_store.add(
            vectors=[[0.1, 0.2]],
        )

        stats = memory_store.stats

        assert "total_inserts" in stats
        assert stats["total_inserts"] == 1

    @pytest.mark.asyncio
    async def test_close(self, memory_store):
        """Test closing the store"""
        await memory_store.initialize()

        await memory_store.close()
        # Should not raise


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for vector store"""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory"""
        temp_path = tempfile.mkdtemp()
        yield temp_path
        shutil.rmtree(temp_path)

    @pytest.mark.asyncio
    async def test_full_workflow(self, temp_dir):
        """Test complete workflow with SQLite backend"""
        config = VectorStoreConfig(
            backend=VectorStoreBackend.SQLITE,
            storage_path=temp_dir,
            dimension=3,
        )
        store = VectorStore(config)
        await store.initialize()

        # Create collection
        await store.create_collection("products", dimension=3)

        # Add documents; tag tenant_id="__GLOBAL__" so the fail-closed
        # search path lets this cross-tenant integration test through.
        await store.add(
            vectors=[[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
            texts=["Product A", "Product B", "Product C"],
            metadatas=[
                {"category": "electronics", "tenant_id": "__GLOBAL__"},
                {"category": "clothing", "tenant_id": "__GLOBAL__"},
                {"category": "electronics", "tenant_id": "__GLOBAL__"},
            ],
            collection="products",
        )

        # Search
        results = await store.search(
            vector=[1.0, 0.0, 0.0],
            collection="products",
            top_k=2,
            tenant_id="__GLOBAL__",
        )

        assert len(results) == 2
        assert results[0].content == "Product A"

        # Search with filter
        results = await store.search(
            vector=[0.5, 0.5, 0.0],
            collection="products",
            filter={"category": "electronics"},
            tenant_id="__GLOBAL__",
        )

        assert all(r.metadata["category"] == "electronics" for r in results)

        await store.close()

    @pytest.mark.asyncio
    async def test_multiple_collections(self):
        """Test working with multiple collections"""
        config = VectorStoreConfig(backend=VectorStoreBackend.MEMORY)
        store = VectorStore(config)
        await store.initialize()

        # Create collections
        await store.create_collection("collection_a", dimension=2)
        await store.create_collection("collection_b", dimension=2)

        # Add to different collections
        await store.add(
            vectors=[[0.1, 0.2]],
            texts=["In A"],
            collection="collection_a",
        )
        await store.add(
            vectors=[[0.3, 0.4]],
            texts=["In B"],
            collection="collection_b",
        )

        # Verify separation
        assert await store.count("collection_a") == 1
        assert await store.count("collection_b") == 1

        await store.close()


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_empty_collection_search(self):
        """Test searching an empty collection"""
        config = VectorStoreConfig(backend=VectorStoreBackend.MEMORY)
        store = VectorStore(config)
        await store.initialize()

        results = await store.search(vector=[0.1, 0.2], tenant_id="__GLOBAL__")

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_delete_nonexistent_document(self):
        """Test deleting a non-existent document"""
        config = VectorStoreConfig(backend=VectorStoreBackend.MEMORY)
        store = VectorStore(config)
        await store.initialize()

        count = await store.delete(["nonexistent"])

        assert count == 0

    @pytest.mark.asyncio
    async def test_update_nonexistent_document(self):
        """Test updating a non-existent document"""
        config = VectorStoreConfig(backend=VectorStoreBackend.MEMORY)
        store = VectorStore(config)
        await store.initialize()

        result = await store.update(
            id="nonexistent",
            vector=[0.1, 0.2],
        )

        assert result is False

    @pytest.mark.asyncio
    async def test_add_empty_list(self):
        """Test adding empty list of documents"""
        config = VectorStoreConfig(backend=VectorStoreBackend.MEMORY)
        store = VectorStore(config)
        await store.initialize()

        ids = await store.add(vectors=[])

        assert ids == []

    @pytest.mark.asyncio
    async def test_search_top_k_larger_than_collection(self):
        """Test search when top_k is larger than collection size"""
        config = VectorStoreConfig(backend=VectorStoreBackend.MEMORY)
        store = VectorStore(config)
        await store.initialize()

        await store.add(
            vectors=[[0.1, 0.2], [0.3, 0.4]],
            metadatas=[{"tenant_id": "__GLOBAL__"}, {"tenant_id": "__GLOBAL__"}],
        )

        results = await store.search(vector=[0.1, 0.2], top_k=100, tenant_id="__GLOBAL__")

        assert len(results) == 2  # Should return all documents


# ============================================================================
# Distance Metric Tests
# ============================================================================


class TestDistanceMetrics:
    """Tests for different distance metrics"""

    @pytest.mark.asyncio
    async def test_cosine_similarity(self):
        """Test cosine similarity search"""
        backend = MemoryBackend(distance_metric=DistanceMetric.COSINE)
        await backend.initialize()
        await backend.create_collection("test", 2, DistanceMetric.COSINE)

        docs = [
            VectorDocument(id="doc1", vector=[1.0, 0.0]),
            VectorDocument(id="doc2", vector=[0.0, 1.0]),
        ]
        await backend.insert(docs, "test")

        results = await backend.search([1.0, 0.0], "test")

        assert results[0].id == "doc1"
        assert results[0].score > 0.99  # Should be ~1.0

    @pytest.mark.asyncio
    async def test_euclidean_distance(self):
        """Test Euclidean distance search"""
        backend = MemoryBackend(distance_metric=DistanceMetric.EUCLIDEAN)
        await backend.initialize()
        await backend.create_collection("test", 2, DistanceMetric.EUCLIDEAN)

        docs = [
            VectorDocument(id="close", vector=[0.1, 0.0]),
            VectorDocument(id="far", vector=[10.0, 10.0]),
        ]
        await backend.insert(docs, "test")

        results = await backend.search([0.0, 0.0], "test")

        assert results[0].id == "close"  # Should be closest
