"""
SAHOOL Document Ingestion
Sprint 9: Document processing and chunking

Handles document ingestion into the vector store with
configurable chunking strategies.
"""

from __future__ import annotations

from advisor.rag.doc_store import DocChunk, VectorStore


def chunk_text(
    text: str,
    chunk_size: int = 600,
    overlap: int = 80,
) -> list[str]:
    """Split text into overlapping chunks.

    Args:
        text: Text to split
        chunk_size: Maximum characters per chunk
        overlap: Characters to overlap between chunks

    Returns:
        List of text chunks

    Raises:
        ValueError: If chunk_size <= overlap
    """
    if chunk_size <= overlap:
        raise ValueError("chunk_size must be > overlap")

    if not text:
        return []

    chunks: list[str] = []
    i = 0
    while i < len(text):
        chunks.append(text[i : i + chunk_size])
        i += chunk_size - overlap

    return chunks


def chunk_by_sentences(
    text: str,
    max_chunk_size: int = 600,
    sentence_delimiters: str = ".!?。",
) -> list[str]:
    """Split text into chunks at sentence boundaries.

    Args:
        text: Text to split
        max_chunk_size: Maximum characters per chunk
        sentence_delimiters: Characters that end sentences

    Returns:
        List of text chunks
    """
    if not text:
        return []

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    # Simple sentence splitting
    sentences: list[str] = []
    current_sentence: list[str] = []

    for char in text:
        current_sentence.append(char)
        if char in sentence_delimiters:
            sentences.append("".join(current_sentence).strip())
            current_sentence = []

    # Don't forget the last sentence
    if current_sentence:
        sentences.append("".join(current_sentence).strip())

    # Group sentences into chunks
    for sentence in sentences:
        if not sentence:
            continue

        if current_length + len(sentence) > max_chunk_size and current_chunk:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

        current_chunk.append(sentence)
        current_length += len(sentence) + 1  # +1 for space

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def ingest_document(
    store: VectorStore,
    *,
    collection: str,
    doc_id: str,
    text: str,
    source: str,
    chunk_size: int = 600,
    overlap: int = 80,
    metadata: dict | None = None,
) -> int:
    """Ingest a document into the vector store.

    Args:
        store: Vector store instance
        collection: Collection name
        doc_id: Document identifier
        text: Document text content
        source: Source name (for attribution)
        chunk_size: Chunk size for splitting
        overlap: Overlap between chunks
        metadata: Additional metadata for chunks

    Returns:
        Number of chunks created
    """
    pieces = chunk_text(text, chunk_size=chunk_size, overlap=overlap)

    base_metadata = {"source": source}
    if metadata:
        base_metadata.update(metadata)

    chunks = [
        DocChunk(
            doc_id=doc_id,
            chunk_id=str(idx),
            text=piece,
            metadata=base_metadata,
        )
        for idx, piece in enumerate(pieces)
    ]

    store.upsert_chunks(collection=collection, chunks=chunks)
    return len(chunks)


def ingest_documents_batch(
    store: VectorStore,
    *,
    collection: str,
    documents: list[dict],
    chunk_size: int = 600,
    overlap: int = 80,
) -> dict[str, int]:
    """Ingest multiple documents.

    Args:
        store: Vector store instance
        collection: Collection name
        documents: List of document dicts with keys: doc_id, text, source
        chunk_size: Chunk size
        overlap: Overlap

    Returns:
        Dict mapping doc_id to number of chunks created
    """
    results: dict[str, int] = {}

    for doc in documents:
        doc_id = doc["doc_id"]
        text = doc["text"]
        source = doc.get("source", "unknown")
        metadata = doc.get("metadata")

        count = ingest_document(
            store,
            collection=collection,
            doc_id=doc_id,
            text=text,
            source=source,
            chunk_size=chunk_size,
            overlap=overlap,
            metadata=metadata,
        )
        results[doc_id] = count

    return results
