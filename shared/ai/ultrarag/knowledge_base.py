# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Knowledge Base - Document Management and Chunking
# قاعدة المعرفة - إدارة المستندات والتقسيم
# ═══════════════════════════════════════════════════════════════════════════════

import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import structlog

from .models import (
    ChunkingStrategy,
    KnowledgeChunk,
    KnowledgeDocument,
)

logger = structlog.get_logger(__name__)


@dataclass
class ChunkingConfig:
    """Configuration for chunking | تكوين التقسيم"""

    strategy: ChunkingStrategy = ChunkingStrategy.RECURSIVE
    chunk_size: int = 500
    chunk_overlap: int = 50
    min_chunk_size: int = 100
    max_chunk_size: int = 2000
    separators: list[str] = field(default_factory=lambda: ["\n\n", "\n", ". ", " "])
    preserve_sentences: bool = True
    language: str = "en"  # "en", "ar", or "both"


class Chunker:
    """
    Document chunking with multiple strategies
    تقسيم المستندات بعدة استراتيجيات
    """

    def __init__(self, config: ChunkingConfig | None = None):
        self.config = config or ChunkingConfig()

        # Arabic-specific separators
        self._arabic_separators = ["\n\n", "\n", "۔ ", "، ", " "]
        self._arabic_sentence_endings = ["۔", "؟", "!", "。"]

    def chunk(
        self,
        document: KnowledgeDocument,
        config: ChunkingConfig | None = None,
    ) -> list[KnowledgeChunk]:
        """Chunk a document based on strategy"""
        cfg = config or self.config

        if cfg.strategy == ChunkingStrategy.FIXED_SIZE:
            return self._chunk_fixed_size(document, cfg)
        elif cfg.strategy == ChunkingStrategy.SENTENCE:
            return self._chunk_sentence(document, cfg)
        elif cfg.strategy == ChunkingStrategy.PARAGRAPH:
            return self._chunk_paragraph(document, cfg)
        elif cfg.strategy == ChunkingStrategy.SEMANTIC:
            return self._chunk_semantic(document, cfg)
        elif cfg.strategy == ChunkingStrategy.HIERARCHICAL:
            return self._chunk_hierarchical(document, cfg)
        else:  # RECURSIVE (default)
            return self._chunk_recursive(document, cfg)

    def _chunk_fixed_size(
        self,
        document: KnowledgeDocument,
        config: ChunkingConfig,
    ) -> list[KnowledgeChunk]:
        """Fixed-size chunking with overlap"""
        chunks = []
        text = document.content
        text_ar = document.content_ar

        start = 0
        chunk_index = 0

        while start < len(text):
            end = min(start + config.chunk_size, len(text))

            # Get chunk text
            chunk_text = text[start:end]

            # Get Arabic text if available
            chunk_text_ar = None
            if text_ar:
                ar_end = min(start + config.chunk_size, len(text_ar))
                chunk_text_ar = text_ar[start:ar_end]

            # Create chunk
            chunk = KnowledgeChunk(
                id=f"{document.id}_c{chunk_index}",
                text=chunk_text,
                text_ar=chunk_text_ar,
                document_id=document.id,
                collection=document.collection,
                metadata={**document.metadata, "source": document.source},
                start_char=start,
                end_char=end,
                chunk_index=chunk_index,
            )
            chunks.append(chunk)

            # Move to next chunk with overlap
            start = end - config.chunk_overlap
            chunk_index += 1

        return chunks

    def _chunk_sentence(
        self,
        document: KnowledgeDocument,
        config: ChunkingConfig,
    ) -> list[KnowledgeChunk]:
        """Sentence-based chunking"""
        chunks = []
        sentences = self._split_sentences(document.content, config.language)
        sentences_ar = (
            self._split_sentences(document.content_ar, "ar") if document.content_ar else []
        )

        current_chunk = []
        current_length = 0
        chunk_index = 0
        start_char = 0

        for i, sentence in enumerate(sentences):
            sentence_len = len(sentence)

            if current_length + sentence_len > config.chunk_size and current_chunk:
                # Create chunk from accumulated sentences
                chunk_text = " ".join(current_chunk)
                chunk_text_ar = (
                    " ".join(sentences_ar[: len(current_chunk)]) if sentences_ar else None
                )

                chunk = KnowledgeChunk(
                    id=f"{document.id}_c{chunk_index}",
                    text=chunk_text,
                    text_ar=chunk_text_ar,
                    document_id=document.id,
                    collection=document.collection,
                    metadata={**document.metadata, "source": document.source},
                    start_char=start_char,
                    end_char=start_char + len(chunk_text),
                    chunk_index=chunk_index,
                )
                chunks.append(chunk)

                # Reset
                start_char += len(chunk_text) + 1
                current_chunk = []
                current_length = 0
                chunk_index += 1

            current_chunk.append(sentence)
            current_length += sentence_len

        # Handle remaining sentences
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk = KnowledgeChunk(
                id=f"{document.id}_c{chunk_index}",
                text=chunk_text,
                document_id=document.id,
                collection=document.collection,
                metadata={**document.metadata, "source": document.source},
                start_char=start_char,
                end_char=start_char + len(chunk_text),
                chunk_index=chunk_index,
            )
            chunks.append(chunk)

        return chunks

    def _chunk_paragraph(
        self,
        document: KnowledgeDocument,
        config: ChunkingConfig,
    ) -> list[KnowledgeChunk]:
        """Paragraph-based chunking"""
        chunks = []
        paragraphs = document.content.split("\n\n")
        paragraphs_ar = document.content_ar.split("\n\n") if document.content_ar else []

        chunk_index = 0
        current_pos = 0

        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if not paragraph:
                continue

            # Get corresponding Arabic paragraph
            para_ar = paragraphs_ar[i].strip() if i < len(paragraphs_ar) else None

            # If paragraph is too long, split it
            if len(paragraph) > config.max_chunk_size:
                sub_chunks = self._chunk_long_text(
                    paragraph,
                    config.chunk_size,
                    config.chunk_overlap,
                )
                for j, sub_text in enumerate(sub_chunks):
                    chunk = KnowledgeChunk(
                        id=f"{document.id}_c{chunk_index}",
                        text=sub_text,
                        text_ar=para_ar if j == 0 else None,  # Arabic only on first sub-chunk
                        document_id=document.id,
                        collection=document.collection,
                        metadata={
                            **document.metadata,
                            "source": document.source,
                            "paragraph_index": i,
                        },
                        start_char=current_pos,
                        end_char=current_pos + len(sub_text),
                        chunk_index=chunk_index,
                    )
                    chunks.append(chunk)
                    current_pos += len(sub_text)
                    chunk_index += 1
            else:
                chunk = KnowledgeChunk(
                    id=f"{document.id}_c{chunk_index}",
                    text=paragraph,
                    text_ar=para_ar,
                    document_id=document.id,
                    collection=document.collection,
                    metadata={**document.metadata, "source": document.source, "paragraph_index": i},
                    start_char=current_pos,
                    end_char=current_pos + len(paragraph),
                    chunk_index=chunk_index,
                )
                chunks.append(chunk)
                current_pos += len(paragraph) + 2  # +2 for \n\n
                chunk_index += 1

        return chunks

    def _chunk_recursive(
        self,
        document: KnowledgeDocument,
        config: ChunkingConfig,
    ) -> list[KnowledgeChunk]:
        """Recursive character text splitter (LangChain-style)"""
        separators = config.separators.copy()
        if config.language == "ar" or config.language == "both":
            separators.extend(self._arabic_separators)

        text_splits = self._recursive_split(
            document.content,
            separators,
            config.chunk_size,
            config.chunk_overlap,
        )

        chunks = []
        current_pos = 0

        for i, split_text in enumerate(text_splits):
            chunk = KnowledgeChunk(
                id=f"{document.id}_c{i}",
                text=split_text,
                document_id=document.id,
                collection=document.collection,
                metadata={**document.metadata, "source": document.source},
                start_char=current_pos,
                end_char=current_pos + len(split_text),
                chunk_index=i,
            )
            chunks.append(chunk)
            current_pos += len(split_text)

        return chunks

    def _chunk_semantic(
        self,
        document: KnowledgeDocument,
        config: ChunkingConfig,
    ) -> list[KnowledgeChunk]:
        """Semantic chunking (requires embeddings - falls back to recursive)"""
        # For now, fall back to recursive chunking
        # Full implementation would use embeddings to find semantic boundaries
        logger.warning("semantic_chunking_fallback", message="Using recursive chunking as fallback")
        return self._chunk_recursive(document, config)

    def _chunk_hierarchical(
        self,
        document: KnowledgeDocument,
        config: ChunkingConfig,
    ) -> list[KnowledgeChunk]:
        """Hierarchical chunking with parent-child relationships"""
        chunks = []

        # First level: Sections
        sections = self._split_by_headers(document.content)

        chunk_index = 0
        current_pos = 0

        for section_idx, (header, content) in enumerate(sections):
            # Create section-level chunk
            section_text = f"{header}\n{content}" if header else content

            section_chunk = KnowledgeChunk(
                id=f"{document.id}_s{section_idx}",
                text=section_text,
                document_id=document.id,
                collection=document.collection,
                metadata={
                    **document.metadata,
                    "source": document.source,
                    "level": "section",
                    "section_header": header,
                },
                start_char=current_pos,
                end_char=current_pos + len(section_text),
                chunk_index=chunk_index,
            )
            chunks.append(section_chunk)
            chunk_index += 1

            # Create sub-chunks for long sections
            if len(content) > config.chunk_size:
                sub_chunks = self._chunk_long_text(content, config.chunk_size, config.chunk_overlap)
                for sub_idx, sub_text in enumerate(sub_chunks):
                    sub_chunk = KnowledgeChunk(
                        id=f"{document.id}_s{section_idx}_c{sub_idx}",
                        text=sub_text,
                        document_id=document.id,
                        collection=document.collection,
                        metadata={
                            **document.metadata,
                            "source": document.source,
                            "level": "chunk",
                            "parent_id": section_chunk.id,
                            "section_header": header,
                        },
                        start_char=current_pos,
                        end_char=current_pos + len(sub_text),
                        chunk_index=chunk_index,
                    )
                    chunks.append(sub_chunk)
                    current_pos += len(sub_text)
                    chunk_index += 1

            current_pos += len(section_text)

        return chunks

    # ═══════════════════════════════════════════════════════════════════════════
    # Helper Methods
    # ═══════════════════════════════════════════════════════════════════════════

    def _split_sentences(self, text: str, language: str = "en") -> list[str]:
        """Split text into sentences"""
        if language == "ar":
            # Arabic sentence endings
            pattern = r"[۔؟!。\.\?\!]+"
        else:
            # English/general sentence endings
            pattern = r"[.!?]+"

        sentences = re.split(f"({pattern})", text)

        # Reconstruct sentences with their endings
        result = []
        for i in range(0, len(sentences) - 1, 2):
            sentence = sentences[i] + (sentences[i + 1] if i + 1 < len(sentences) else "")
            sentence = sentence.strip()
            if sentence:
                result.append(sentence)

        # Add last part if no ending punctuation
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            result.append(sentences[-1].strip())

        return result

    def _recursive_split(
        self,
        text: str,
        separators: list[str],
        chunk_size: int,
        overlap: int,
    ) -> list[str]:
        """Recursively split text using separators"""
        if not text:
            return []

        # If text is small enough, return it
        if len(text) <= chunk_size:
            return [text]

        # Find the best separator
        separator = None
        for sep in separators:
            if sep in text:
                separator = sep
                break

        if separator is None:
            # No separator found, split by size
            return self._chunk_long_text(text, chunk_size, overlap)

        # Split by separator
        splits = text.split(separator)

        # Merge small splits
        chunks = []
        current_chunk = []
        current_length = 0

        for split in splits:
            split_len = len(split)

            if current_length + split_len > chunk_size and current_chunk:
                # Save current chunk
                chunk_text = separator.join(current_chunk)
                chunks.append(chunk_text)

                # Start new chunk with overlap
                overlap_text = separator.join(current_chunk[-2:]) if len(current_chunk) > 1 else ""
                current_chunk = [overlap_text] if overlap_text else []
                current_length = len(overlap_text)

            current_chunk.append(split)
            current_length += split_len + len(separator)

        # Add remaining
        if current_chunk:
            chunks.append(separator.join(current_chunk))

        return chunks

    def _chunk_long_text(
        self,
        text: str,
        chunk_size: int,
        overlap: int,
    ) -> list[str]:
        """Split long text into fixed-size chunks"""
        chunks = []
        start = 0

        while start < len(text):
            end = min(start + chunk_size, len(text))
            chunks.append(text[start:end])
            start = end - overlap

        return chunks

    def _split_by_headers(self, text: str) -> list[tuple[str, str]]:
        """Split text by markdown-style headers"""
        # Match headers like # Header, ## Header, ### Header
        header_pattern = r"^(#{1,6}\s+.+)$"

        sections = []
        current_header = ""
        current_content = []

        for line in text.split("\n"):
            if re.match(header_pattern, line):
                # Save previous section
                if current_content:
                    sections.append((current_header, "\n".join(current_content)))
                current_header = line
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_content:
            sections.append((current_header, "\n".join(current_content)))

        return sections


class KnowledgeBase:
    """
    Knowledge Base Manager - Document ingestion, storage, and retrieval
    مدير قاعدة المعرفة - استيعاب المستندات وتخزينها واسترجاعها
    """

    def __init__(
        self,
        vector_store: Any = None,
        embedding_service: Any = None,
        retriever: Any = None,
        chunker: Chunker | None = None,
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.retriever = retriever
        self.chunker = chunker or Chunker()

        # In-memory document store (for metadata)
        self._documents: dict[str, KnowledgeDocument] = {}
        self._chunks: dict[str, KnowledgeChunk] = {}

    async def add_document(
        self,
        document: KnowledgeDocument,
        chunking_config: ChunkingConfig | None = None,
    ) -> bool:
        """
        Add a document to the knowledge base
        إضافة مستند إلى قاعدة المعرفة
        """
        start_time = time.time()

        try:
            # Chunk the document
            chunks = self.chunker.chunk(document, chunking_config)

            # Store document metadata
            self._documents[document.id] = document
            document.chunks = chunks

            # Store chunks
            for chunk in chunks:
                self._chunks[chunk.id] = chunk

            # Add to retriever if available
            if self.retriever:
                await self.retriever.add_documents(chunks, document.collection)

            elapsed = (time.time() - start_time) * 1000

            logger.info(
                "document_added",
                document_id=document.id,
                title=document.title,
                chunks_count=len(chunks),
                elapsed_ms=elapsed,
            )

            return True

        except Exception as e:
            logger.error("document_add_error", document_id=document.id, error=str(e))
            return False

    async def add_documents(
        self,
        documents: list[KnowledgeDocument],
        chunking_config: ChunkingConfig | None = None,
    ) -> int:
        """Add multiple documents"""
        success_count = 0

        for doc in documents:
            if await self.add_document(doc, chunking_config):
                success_count += 1

        return success_count

    async def add_text(
        self,
        text: str,
        title: str = "Untitled",
        text_ar: str | None = None,
        title_ar: str | None = None,
        source: str = "",
        collection: str = "default",
        metadata: dict[str, Any] = None,
        chunking_config: ChunkingConfig | None = None,
    ) -> KnowledgeDocument | None:
        """
        Add text content as a new document
        إضافة محتوى نصي كمستند جديد
        """
        document = KnowledgeDocument(
            id=KnowledgeDocument.generate_id(),
            title=title,
            title_ar=title_ar,
            content=text,
            content_ar=text_ar,
            source=source,
            collection=collection,
            metadata=metadata or {},
        )

        if await self.add_document(document, chunking_config):
            return document
        return None

    async def add_file(
        self,
        file_path: str | Path,
        collection: str = "default",
        metadata: dict[str, Any] = None,
        chunking_config: ChunkingConfig | None = None,
    ) -> KnowledgeDocument | None:
        """
        Add a file to the knowledge base
        إضافة ملف إلى قاعدة المعرفة
        """
        path = Path(file_path)

        if not path.exists():
            logger.error("file_not_found", path=str(path))
            return None

        try:
            # Read file content
            content = path.read_text(encoding="utf-8")

            # Create document
            return await self.add_text(
                text=content,
                title=path.stem,
                source=str(path),
                collection=collection,
                metadata={**(metadata or {}), "file_type": path.suffix},
                chunking_config=chunking_config,
            )

        except Exception as e:
            logger.error("file_read_error", path=str(path), error=str(e))
            return None

    async def add_directory(
        self,
        directory_path: str | Path,
        collection: str = "default",
        patterns: list[str] = None,
        chunking_config: ChunkingConfig | None = None,
    ) -> int:
        """
        Add all matching files from a directory
        إضافة جميع الملفات المطابقة من مجلد
        """
        directory = Path(directory_path)
        patterns = patterns or ["*.txt", "*.md", "*.json"]

        if not directory.exists():
            logger.error("directory_not_found", path=str(directory))
            return 0

        added_count = 0

        for pattern in patterns:
            for file_path in directory.glob(f"**/{pattern}"):
                doc = await self.add_file(
                    file_path,
                    collection=collection,
                    chunking_config=chunking_config,
                )
                if doc:
                    added_count += 1

        logger.info(
            "directory_added",
            directory=str(directory),
            documents_added=added_count,
        )

        return added_count

    def get_document(self, document_id: str) -> KnowledgeDocument | None:
        """Get a document by ID"""
        return self._documents.get(document_id)

    def get_chunk(self, chunk_id: str) -> KnowledgeChunk | None:
        """Get a chunk by ID"""
        return self._chunks.get(chunk_id)

    def list_documents(
        self,
        collection: str = None,
        limit: int = 100,
    ) -> list[KnowledgeDocument]:
        """List documents, optionally filtered by collection"""
        docs = list(self._documents.values())

        if collection:
            docs = [d for d in docs if d.collection == collection]

        return docs[:limit]

    def list_collections(self) -> list[str]:
        """List all collections"""
        collections = set()
        for doc in self._documents.values():
            collections.add(doc.collection)
        return sorted(collections)

    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its chunks"""
        if document_id not in self._documents:
            return False

        document = self._documents[document_id]

        # Delete chunks
        for chunk in document.chunks:
            if chunk.id in self._chunks:
                del self._chunks[chunk.id]

        # Delete document
        del self._documents[document_id]

        logger.info("document_deleted", document_id=document_id)
        return True

    async def clear_collection(self, collection: str) -> int:
        """Clear all documents in a collection"""
        to_delete = [
            doc_id for doc_id, doc in self._documents.items() if doc.collection == collection
        ]

        for doc_id in to_delete:
            await self.delete_document(doc_id)

        return len(to_delete)

    def get_stats(self) -> dict[str, Any]:
        """Get knowledge base statistics"""
        collections = {}
        for doc in self._documents.values():
            if doc.collection not in collections:
                collections[doc.collection] = {"documents": 0, "chunks": 0}
            collections[doc.collection]["documents"] += 1
            collections[doc.collection]["chunks"] += len(doc.chunks)

        return {
            "total_documents": len(self._documents),
            "total_chunks": len(self._chunks),
            "collections": collections,
        }


# Export classes
__all__ = [
    "KnowledgeBase",
    "Chunker",
    "ChunkingConfig",
    "ChunkingStrategy",
    "KnowledgeDocument",
    "KnowledgeChunk",
]
