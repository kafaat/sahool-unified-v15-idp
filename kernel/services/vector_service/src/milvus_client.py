"""
Milvus Client - Vector database operations
عميل Milvus - عمليات قاعدة بيانات المتجهات
"""
from typing import Optional
from pymilvus import (
    connections,
    FieldSchema,
    CollectionSchema,
    DataType,
    Collection,
    utility,
)
from .settings import settings

# Global collection reference
_collection: Optional[Collection] = None


def connect() -> None:
    """Connect to Milvus server"""
    connections.connect(
        alias="default",
        host=settings.milvus_host,
        port=str(settings.milvus_port),
    )


def disconnect() -> None:
    """Disconnect from Milvus server"""
    connections.disconnect(alias="default")


def is_connected() -> bool:
    """Check if connected to Milvus"""
    try:
        return connections.has_connection("default")
    except Exception:
        return False


def ensure_collection() -> Collection:
    """Ensure collection exists and is loaded"""
    global _collection

    if _collection is not None:
        return _collection

    name = settings.milvus_collection

    if utility.has_collection(name):
        _collection = Collection(name)
        _collection.load()
        return _collection

    # Create schema
    fields = [
        FieldSchema(
            name="id",
            dtype=DataType.VARCHAR,
            is_primary=True,
            auto_id=False,
            max_length=256,
        ),
        FieldSchema(
            name="tenant_id",
            dtype=DataType.VARCHAR,
            max_length=64,
        ),
        FieldSchema(
            name="namespace",
            dtype=DataType.VARCHAR,
            max_length=64,
        ),
        FieldSchema(
            name="doc_id",
            dtype=DataType.VARCHAR,
            max_length=256,
        ),
        FieldSchema(
            name="text",
            dtype=DataType.VARCHAR,
            max_length=65535,
        ),
        FieldSchema(
            name="metadata_json",
            dtype=DataType.VARCHAR,
            max_length=65535,
        ),
        FieldSchema(
            name="embedding",
            dtype=DataType.FLOAT_VECTOR,
            dim=settings.embedding_dim,
        ),
    ]

    schema = CollectionSchema(
        fields=fields,
        description="SAHOOL Multi-tenant vector storage for RAG",
    )

    _collection = Collection(name=name, schema=schema)

    # Create HNSW index for fast similarity search
    _collection.create_index(
        field_name="embedding",
        index_params={
            "index_type": "HNSW",
            "metric_type": "IP",  # Inner Product (cosine for normalized vectors)
            "params": {
                "M": 16,
                "efConstruction": 200,
            },
        },
    )

    # Load collection into memory
    _collection.load()

    return _collection


def get_collection() -> Collection:
    """Get the collection (must be initialized first)"""
    global _collection
    if _collection is None:
        raise RuntimeError("Collection not initialized. Call ensure_collection() first.")
    return _collection


def collection_stats() -> dict:
    """Get collection statistics"""
    col = get_collection()
    return {
        "name": col.name,
        "num_entities": col.num_entities,
        "is_loaded": True,
    }
