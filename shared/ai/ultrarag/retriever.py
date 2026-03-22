# ═══════════════════════════════════════════════════════════════════════════════
# UltraRAG Retriever - Multi-Strategy Retrieval System
# نظام الاسترجاع متعدد الاستراتيجيات
# ═══════════════════════════════════════════════════════════════════════════════

import asyncio
import hashlib
import re
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

import structlog

from .models import (
    KnowledgeChunk,
    RetrievalResult,
    RetrievalStrategy,
)

logger = structlog.get_logger(__name__)


@dataclass
class RetrievalConfig:
    """Configuration for retrieval | تكوين الاسترجاع"""

    strategy: RetrievalStrategy = RetrievalStrategy.HYBRID
    top_k: int = 10
    dense_weight: float = 0.7
    sparse_weight: float = 0.3
    min_score_threshold: float = 0.1
    use_query_expansion: bool = True
    max_query_terms: int = 10
    collection: str = "default"
    filters: dict[str, Any] = field(default_factory=dict)


class Retriever(ABC):
    """Abstract base class for retrievers | فئة أساسية مجردة للمسترجعات"""

    @abstractmethod
    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> list[RetrievalResult]:
        """Retrieve relevant chunks for a query"""
        pass

    @abstractmethod
    async def add_documents(
        self,
        chunks: list[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Add documents to the retriever index"""
        pass


class DenseRetriever(Retriever):
    """Dense vector-based retriever using embeddings | مسترجع كثيف يعتمد على المتجهات"""

    def __init__(
        self,
        vector_store: Any,  # VectorStore from shared/ai/vector_store.py
        embedding_service: Any,  # EmbeddingsAdapter from shared/ai/embeddings.py
    ):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self._cache: dict[str, list[float]] = {}
        self._cache_max_size = 10000

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> list[RetrievalResult]:
        """Retrieve using dense vector similarity"""
        start_time = time.time()

        try:
            # Get query embedding (with caching)
            query_vector = await self._get_embedding(query)

            # Search vector store
            search_results = await self.vector_store.search(
                vector=query_vector,
                collection=config.collection,
                top_k=config.top_k,
                filter=config.filters if config.filters else None,
            )

            # Convert to RetrievalResult
            results = []
            for i, result in enumerate(search_results):
                chunk = KnowledgeChunk(
                    id=result.id,
                    text=result.text or "",
                    text_ar=result.metadata.get("text_ar") if result.metadata else None,
                    document_id=result.metadata.get("document_id", "") if result.metadata else "",
                    collection=config.collection,
                    metadata=result.metadata or {},
                )
                results.append(
                    RetrievalResult(
                        chunk=chunk,
                        score=result.score,
                        retrieval_method="dense",
                        rank=i + 1,
                    )
                )

            # Filter by minimum score
            results = [r for r in results if r.score >= config.min_score_threshold]

            elapsed = (time.time() - start_time) * 1000
            logger.info(
                "dense_retrieval_complete",
                query_length=len(query),
                results_count=len(results),
                elapsed_ms=elapsed,
            )

            return results

        except Exception as e:
            logger.error("dense_retrieval_error", error=str(e))
            return []

    async def add_documents(
        self,
        chunks: list[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Add documents with embeddings to vector store"""
        try:
            texts = [c.text for c in chunks]
            ids = [c.id for c in chunks]
            metadatas = [
                {
                    **c.metadata,
                    "text_ar": c.text_ar,
                    "document_id": c.document_id,
                    "chunk_index": c.chunk_index,
                }
                for c in chunks
            ]

            # Generate embeddings
            embeddings = await self._get_embeddings_batch(texts)

            # Add to vector store
            await self.vector_store.add(
                texts=texts,
                vectors=embeddings,
                ids=ids,
                metadatas=metadatas,
                collection=collection,
            )

            logger.info(
                "documents_added",
                count=len(chunks),
                collection=collection,
            )
            return True

        except Exception as e:
            logger.error("add_documents_error", error=str(e))
            return False

    async def _get_embedding(self, text: str) -> list[float]:
        """Get embedding with caching"""
        cache_key = hashlib.md5(text.encode(), usedforsecurity=False).hexdigest()

        if cache_key in self._cache:
            return self._cache[cache_key]

        result = await self.embedding_service.embed(text)
        vector = result.embedding

        # Cache management
        if len(self._cache) >= self._cache_max_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self._cache.keys())[:1000]
            for key in keys_to_remove:
                del self._cache[key]

        self._cache[cache_key] = vector
        return vector

    async def _get_embeddings_batch(self, texts: list[str]) -> list[list[float]]:
        """Get embeddings for multiple texts"""
        results = await self.embedding_service.embed_batch(texts)
        return [r.embedding for r in results]


class SparseRetriever(Retriever):
    """BM25-based sparse retriever | مسترجع متفرق يعتمد على BM25"""

    def __init__(self, vector_store: Any):
        self.vector_store = vector_store
        self._index: dict[str, dict[str, list[tuple[str, int]]]] = {}  # collection -> term -> [(doc_id, count)]
        self._doc_lengths: dict[str, dict[str, int]] = {}  # collection -> doc_id -> length
        self._avg_doc_length: dict[str, float] = {}  # collection -> avg_length
        self._k1 = 1.5
        self._b = 0.75

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> list[RetrievalResult]:
        """Retrieve using BM25 scoring"""
        start_time = time.time()

        try:
            # Tokenize query
            query_terms = self._tokenize(query)

            if not query_terms:
                return []

            collection = config.collection

            # Calculate BM25 scores
            scores: dict[str, float] = {}
            N = len(self._doc_lengths.get(collection, {}))

            if N == 0:
                logger.warning("sparse_retrieval_empty_index", collection=collection)
                return []

            avg_dl = self._avg_doc_length.get(collection, 1.0)

            for term in query_terms:
                if collection not in self._index or term not in self._index[collection]:
                    continue

                doc_freqs = self._index[collection][term]
                df = len(doc_freqs)
                idf = self._calculate_idf(N, df)

                for doc_id, tf in doc_freqs:
                    dl = self._doc_lengths.get(collection, {}).get(doc_id, 1)
                    score = self._calculate_bm25_score(tf, idf, dl, avg_dl)

                    if doc_id not in scores:
                        scores[doc_id] = 0
                    scores[doc_id] += score

            # Sort by score and get top_k
            sorted_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            top_docs = sorted_docs[: config.top_k]

            # Convert to RetrievalResult
            results = []
            for i, (doc_id, score) in enumerate(top_docs):
                if score < config.min_score_threshold:
                    continue

                # Fetch document from vector store
                doc = await self.vector_store.get(doc_id, collection=collection)
                if doc:
                    chunk = KnowledgeChunk(
                        id=doc_id,
                        text=doc.text or "",
                        text_ar=doc.metadata.get("text_ar") if doc.metadata else None,
                        document_id=doc.metadata.get("document_id", "") if doc.metadata else "",
                        collection=collection,
                        metadata=doc.metadata or {},
                    )
                    results.append(
                        RetrievalResult(
                            chunk=chunk,
                            score=score,
                            retrieval_method="sparse",
                            rank=i + 1,
                        )
                    )

            elapsed = (time.time() - start_time) * 1000
            logger.info(
                "sparse_retrieval_complete",
                query_length=len(query),
                results_count=len(results),
                elapsed_ms=elapsed,
            )

            return results

        except Exception as e:
            logger.error("sparse_retrieval_error", error=str(e))
            return []

    async def add_documents(
        self,
        chunks: list[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Build BM25 index from documents"""
        try:
            if collection not in self._index:
                self._index[collection] = {}
                self._doc_lengths[collection] = {}

            total_length = 0

            for chunk in chunks:
                terms = self._tokenize(chunk.text)
                self._doc_lengths[collection][chunk.id] = len(terms)
                total_length += len(terms)

                term_counts: dict[str, int] = {}
                for term in terms:
                    term_counts[term] = term_counts.get(term, 0) + 1

                for term, count in term_counts.items():
                    if term not in self._index[collection]:
                        self._index[collection][term] = []
                    self._index[collection][term].append((chunk.id, count))

            # Update average document length
            num_docs = len(self._doc_lengths[collection])
            self._avg_doc_length[collection] = total_length / num_docs if num_docs > 0 else 1.0

            logger.info(
                "sparse_index_updated",
                collection=collection,
                num_docs=num_docs,
                num_terms=len(self._index[collection]),
            )
            return True

        except Exception as e:
            logger.error("sparse_add_documents_error", error=str(e))
            return False

    def _tokenize(self, text: str) -> list[str]:
        """Simple tokenization with Arabic support"""
        # Lowercase and split on non-alphanumeric (preserving Arabic)
        text = text.lower()
        # Pattern that matches word characters including Arabic
        tokens = re.findall(r"[\w\u0600-\u06FF]+", text)
        # Remove stopwords and short tokens
        tokens = [t for t in tokens if len(t) > 2]
        return tokens

    def _calculate_idf(self, N: int, df: int) -> float:
        """Calculate inverse document frequency"""
        import math

        return math.log((N - df + 0.5) / (df + 0.5) + 1)

    def _calculate_bm25_score(self, tf: int, idf: float, dl: int, avg_dl: float) -> float:
        """Calculate BM25 score for a term"""
        numerator = tf * (self._k1 + 1)
        denominator = tf + self._k1 * (1 - self._b + self._b * (dl / avg_dl))
        return idf * (numerator / denominator)


class HybridRetriever(Retriever):
    """Hybrid retriever combining dense and sparse methods | مسترجع هجين يجمع بين الكثيف والمتفرق"""

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
    ):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> list[RetrievalResult]:
        """Retrieve using both dense and sparse methods, then fuse results"""
        start_time = time.time()

        try:
            # Run both retrievers in parallel
            dense_task = asyncio.create_task(self.dense_retriever.retrieve(query, config))
            sparse_task = asyncio.create_task(self.sparse_retriever.retrieve(query, config))

            dense_results, sparse_results = await asyncio.gather(dense_task, sparse_task)

            # Reciprocal Rank Fusion (RRF)
            k = 60  # RRF constant
            fused_scores: dict[str, tuple[float, KnowledgeChunk]] = {}

            # Process dense results
            for result in dense_results:
                doc_id = result.chunk.id
                rrf_score = config.dense_weight / (k + result.rank)
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = (rrf_score, result.chunk)
                else:
                    current_score, chunk = fused_scores[doc_id]
                    fused_scores[doc_id] = (current_score + rrf_score, chunk)

            # Process sparse results
            for result in sparse_results:
                doc_id = result.chunk.id
                rrf_score = config.sparse_weight / (k + result.rank)
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = (rrf_score, result.chunk)
                else:
                    current_score, chunk = fused_scores[doc_id]
                    fused_scores[doc_id] = (current_score + rrf_score, chunk)

            # Sort by fused score
            sorted_results = sorted(fused_scores.items(), key=lambda x: x[1][0], reverse=True)

            # Create final results
            results = []
            for i, (doc_id, (score, chunk)) in enumerate(sorted_results[: config.top_k]):
                results.append(
                    RetrievalResult(
                        chunk=chunk,
                        score=score,
                        retrieval_method="hybrid",
                        rank=i + 1,
                    )
                )

            elapsed = (time.time() - start_time) * 1000
            logger.info(
                "hybrid_retrieval_complete",
                query_length=len(query),
                dense_count=len(dense_results),
                sparse_count=len(sparse_results),
                fused_count=len(results),
                elapsed_ms=elapsed,
            )

            return results

        except Exception as e:
            logger.error("hybrid_retrieval_error", error=str(e))
            return []

    async def add_documents(
        self,
        chunks: list[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Add documents to both dense and sparse indices"""
        dense_ok = await self.dense_retriever.add_documents(chunks, collection)
        sparse_ok = await self.sparse_retriever.add_documents(chunks, collection)
        return dense_ok and sparse_ok


class AdaptiveRetriever(Retriever):
    """Adaptive retriever that selects strategy based on query | مسترجع تكيفي يختار الاستراتيجية بناءً على الاستعلام"""

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
        hybrid_retriever: HybridRetriever,
    ):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.hybrid_retriever = hybrid_retriever

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> list[RetrievalResult]:
        """Adaptively select retrieval strategy based on query characteristics"""
        # Analyze query
        query_type = self._analyze_query(query)

        logger.info(
            "adaptive_retrieval_strategy",
            query_type=query_type,
            query_preview=query[:50],
        )

        # Select strategy based on query type
        if query_type == "keyword":
            # Short, keyword-like queries benefit from sparse retrieval
            return await self.sparse_retriever.retrieve(query, config)
        elif query_type == "semantic":
            # Long, semantic queries benefit from dense retrieval
            return await self.dense_retriever.retrieve(query, config)
        else:
            # Mixed queries use hybrid approach
            return await self.hybrid_retriever.retrieve(query, config)

    async def add_documents(
        self,
        chunks: list[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Add documents to all retriever indices"""
        return await self.hybrid_retriever.add_documents(chunks, collection)

    def _analyze_query(self, query: str) -> str:
        """Analyze query to determine best retrieval strategy"""
        words = query.split()
        num_words = len(words)

        # Check for question words
        question_words = {
            "what",
            "how",
            "why",
            "when",
            "where",
            "who",
            "which",
            "ما",
            "كيف",
            "لماذا",
            "متى",
            "أين",
            "من",
        }
        has_question_word = any(w.lower() in question_words for w in words)

        # Check for technical terms or specific patterns
        bool(re.search(r"[:\-_/\\.]", query))

        if num_words <= 3 and not has_question_word:
            return "keyword"
        elif num_words >= 8 or has_question_word:
            return "semantic"
        else:
            return "hybrid"


class KnowledgeGraphRetriever(Retriever):
    """
    Knowledge Graph Retriever for multi-hop reasoning
    مسترجع خرائط المعرفة للاستدلال متعدد القفزات

    Part of the Tri-RAG framework from AgriGPT.
    Performs entity extraction, graph traversal, and context enrichment.
    """

    def __init__(
        self,
        embedding_service: Any | None = None,
    ):
        self.embedding_service = embedding_service
        # In-memory graph storage (can be replaced with Neo4j, etc.)
        self._entities: dict[str, Any] = {}
        self._relations: list[dict[str, Any]] = []
        self._entity_embeddings: dict[str, list[float]] = {}

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> list[RetrievalResult]:
        """Retrieve relevant context using knowledge graph traversal"""
        from .models import (
            KnowledgeChunk,
        )

        start_time = time.time()
        results: list[RetrievalResult] = []

        try:
            # Step 1: Extract entities from query
            query_entities = await self._extract_entities(query)

            if not query_entities:
                logger.info("kg_no_entities_found", query_preview=query[:50])
                return results

            # Step 2: Find matching entities in graph
            matched_entities = await self._match_entities(query_entities)

            # Step 3: Multi-hop traversal from matched entities
            max_hops = config.filters.get("kg_max_hops", 2) if config.filters else 2
            expanded_context = await self._traverse_graph(
                matched_entities,
                max_hops=max_hops,
            )

            # Step 4: Convert to retrieval results
            for i, (entity_id, context_info) in enumerate(expanded_context.items()):
                entity = self._entities.get(entity_id)
                if entity:
                    # Create a knowledge chunk from the entity and its relations
                    chunk_text = self._create_context_text(entity, context_info)
                    chunk = KnowledgeChunk(
                        id=f"kg_{entity_id}",
                        text=chunk_text,
                        text_ar=context_info.get("text_ar", ""),
                        metadata={
                            "entity_type": entity.get("entity_type", ""),
                            "relations": context_info.get("relations", []),
                            "hop_distance": context_info.get("hop_distance", 0),
                        },
                    )
                    results.append(
                        RetrievalResult(
                            chunk=chunk,
                            score=context_info.get("relevance_score", 0.5),
                            retrieval_method="knowledge_graph",
                            rank=i + 1,
                        )
                    )

            elapsed = (time.time() - start_time) * 1000
            logger.info(
                "kg_retrieval_complete",
                query_entities=len(query_entities),
                matched_entities=len(matched_entities),
                results_count=len(results),
                elapsed_ms=elapsed,
            )

            return results[: config.top_k]

        except Exception as e:
            logger.error("kg_retrieval_error", error=str(e))
            return []

    async def add_documents(
        self,
        chunks: list[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Extract entities and relations from documents to build the knowledge graph"""
        try:
            for chunk in chunks:
                # Extract entities from text
                entities = await self._extract_entities_from_text(chunk.text)
                for entity in entities:
                    self._entities[entity["id"]] = entity

                    # Compute embedding for entity matching
                    if self.embedding_service:
                        result = await self.embedding_service.embed(entity["name"])
                        self._entity_embeddings[entity["id"]] = result.embedding

                # Extract relations (simplified - can be enhanced with NER/RE models)
                relations = await self._extract_relations_from_text(chunk.text, entities)
                self._relations.extend(relations)

            logger.info(
                "kg_documents_added",
                chunks=len(chunks),
                entities=len(self._entities),
                relations=len(self._relations),
            )
            return True

        except Exception as e:
            logger.error("kg_add_documents_error", error=str(e))
            return False

    async def add_entity(
        self,
        entity: dict[str, Any],
    ) -> bool:
        """Add a single entity to the knowledge graph"""
        try:
            self._entities[entity["id"]] = entity
            if self.embedding_service and "name" in entity:
                result = await self.embedding_service.embed(entity["name"])
                self._entity_embeddings[entity["id"]] = result.embedding
            return True
        except Exception as e:
            logger.error("kg_add_entity_error", error=str(e))
            return False

    async def add_relation(
        self,
        relation: dict[str, Any],
    ) -> bool:
        """Add a relationship to the knowledge graph"""
        try:
            self._relations.append(relation)
            return True
        except Exception as e:
            logger.error("kg_add_relation_error", error=str(e))
            return False

    async def _extract_entities(self, query: str) -> list[str]:
        """Extract potential entity mentions from query"""
        # Simple keyword extraction - can be replaced with NER
        # Agricultural domain keywords
        ag_keywords = {
            "wheat",
            "rice",
            "corn",
            "tomato",
            "cotton",
            "date",
            "palm",
            "قمح",
            "أرز",
            "ذرة",
            "طماطم",
            "قطن",
            "تمر",
            "نخيل",
            "pest",
            "disease",
            "fertilizer",
            "irrigation",
            "soil",
            "آفة",
            "مرض",
            "سماد",
            "ري",
            "تربة",
            "nitrogen",
            "phosphorus",
            "potassium",
            "نيتروجين",
            "فوسفور",
            "بوتاسيوم",
        }
        words = re.findall(r"[\w\u0600-\u06FF]+", query.lower())
        return [w for w in words if w in ag_keywords or len(w) > 4]

    async def _extract_entities_from_text(self, text: str) -> list[dict[str, Any]]:
        """Extract entities from document text"""
        entities = []
        # Simplified entity extraction
        words = await self._extract_entities(text)
        for word in set(words):
            entity_id = f"entity_{hash(word) % 1000000:06d}"
            entities.append(
                {
                    "id": entity_id,
                    "name": word,
                    "entity_type": self._guess_entity_type(word),
                }
            )
        return entities

    async def _extract_relations_from_text(
        self,
        text: str,
        entities: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Extract relations between entities (simplified)"""
        relations = []
        # Simple co-occurrence based relation extraction
        entity_ids = [e["id"] for e in entities]
        for i, e1_id in enumerate(entity_ids):
            for e2_id in entity_ids[i + 1 :]:
                relations.append(
                    {
                        "id": f"rel_{hash(e1_id + e2_id) % 1000000:06d}",
                        "source_id": e1_id,
                        "target_id": e2_id,
                        "relation_type": "related_to",
                        "weight": 0.5,
                    }
                )
        return relations

    async def _match_entities(self, query_entities: list[str]) -> list[str]:
        """Match query entities to knowledge graph entities"""
        matched = []
        for q_entity in query_entities:
            # Direct name match
            for entity_id, entity in self._entities.items():
                if entity.get("name", "").lower() == q_entity.lower():
                    matched.append(entity_id)
                    break
                # Check aliases
                aliases = entity.get("aliases", [])
                if q_entity.lower() in [a.lower() for a in aliases]:
                    matched.append(entity_id)
                    break
        return matched

    async def _traverse_graph(
        self,
        start_entities: list[str],
        max_hops: int = 2,
    ) -> dict[str, dict[str, Any]]:
        """Traverse graph from start entities up to max_hops"""
        visited: dict[str, dict[str, Any]] = {}
        current_level = set(start_entities)

        for hop in range(max_hops + 1):
            next_level = set()
            for entity_id in current_level:
                if entity_id in visited:
                    continue
                visited[entity_id] = {
                    "hop_distance": hop,
                    "relations": [],
                    "relevance_score": 1.0 / (hop + 1),  # Closer = more relevant
                }
                # Find connected entities
                for rel in self._relations:
                    if rel["source_id"] == entity_id:
                        next_level.add(rel["target_id"])
                        visited[entity_id]["relations"].append(rel)
                    elif rel["target_id"] == entity_id:
                        next_level.add(rel["source_id"])
                        visited[entity_id]["relations"].append(rel)
            current_level = next_level

        return visited

    def _create_context_text(
        self,
        entity: dict[str, Any],
        context_info: dict[str, Any],
    ) -> str:
        """Create context text from entity and its relations"""
        parts = [
            f"Entity: {entity.get('name', '')}",
            f"Type: {entity.get('entity_type', '')}",
        ]
        if entity.get("description"):
            parts.append(f"Description: {entity['description']}")

        relations = context_info.get("relations", [])
        if relations:
            parts.append("Related to:")
            for rel in relations[:5]:  # Limit relations
                target_id = rel.get("target_id") or rel.get("source_id")
                target = self._entities.get(target_id, {})
                if target:
                    parts.append(f"  - {target.get('name', '')} ({rel.get('relation_type', '')})")

        return "\n".join(parts)

    def _guess_entity_type(self, word: str) -> str:
        """Guess entity type from word"""
        crop_words = {"wheat", "rice", "corn", "tomato", "cotton", "قمح", "أرز", "ذرة", "طماطم"}
        pest_words = {"pest", "aphid", "locust", "آفة", "من", "جراد"}
        disease_words = {"disease", "rust", "blight", "مرض", "صدأ"}
        fertilizer_words = {"fertilizer", "nitrogen", "سماد", "نيتروجين"}

        word_lower = word.lower()
        if word_lower in crop_words:
            return "crop"
        elif word_lower in pest_words:
            return "pest"
        elif word_lower in disease_words:
            return "disease"
        elif word_lower in fertilizer_words:
            return "fertilizer"
        return "unknown"


class TriRAGRetriever(Retriever):
    """
    Tri-RAG Retriever combining Dense, Sparse, and Knowledge Graph retrieval
    مسترجع Tri-RAG يجمع بين الاسترجاع الكثيف والمتفرق وخرائط المعرفة

    Based on AgriGPT's triple-channel RAG framework:
    - Channel 1: Dense (semantic) retrieval
    - Channel 2: Sparse (keyword/BM25) retrieval
    - Channel 3: Knowledge Graph (multi-hop reasoning)

    Results are fused using Reciprocal Rank Fusion (RRF).
    """

    def __init__(
        self,
        dense_retriever: DenseRetriever,
        sparse_retriever: SparseRetriever,
        kg_retriever: KnowledgeGraphRetriever,
        config: Any | None = None,  # TriRAGConfig
    ):
        self.dense_retriever = dense_retriever
        self.sparse_retriever = sparse_retriever
        self.kg_retriever = kg_retriever

        # Default weights if no config
        self.dense_weight = 0.4
        self.sparse_weight = 0.3
        self.kg_weight = 0.3
        self.rrf_k = 60

        if config:
            self.dense_weight = getattr(config, "dense_weight", 0.4)
            self.sparse_weight = getattr(config, "sparse_weight", 0.3)
            self.kg_weight = getattr(config, "kg_weight", 0.3)
            self.rrf_k = getattr(config, "rrf_k", 60)

    async def retrieve(
        self,
        query: str,
        config: RetrievalConfig,
    ) -> list[RetrievalResult]:
        """
        Retrieve using all three channels and fuse results

        استرجاع باستخدام القنوات الثلاث ودمج النتائج
        """
        start_time = time.time()

        try:
            # Run all three retrievers in parallel
            dense_task = asyncio.create_task(self.dense_retriever.retrieve(query, config))
            sparse_task = asyncio.create_task(self.sparse_retriever.retrieve(query, config))
            kg_task = asyncio.create_task(self.kg_retriever.retrieve(query, config))

            dense_results, sparse_results, kg_results = await asyncio.gather(dense_task, sparse_task, kg_task)

            # Reciprocal Rank Fusion (RRF) across all channels
            fused_scores: dict[str, tuple[float, KnowledgeChunk, str]] = {}

            # Process dense results
            for result in dense_results:
                doc_id = result.chunk.id
                rrf_score = self.dense_weight / (self.rrf_k + result.rank)
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = (rrf_score, result.chunk, "dense")
                else:
                    current_score, chunk, method = fused_scores[doc_id]
                    fused_scores[doc_id] = (current_score + rrf_score, chunk, f"{method}+dense")

            # Process sparse results
            for result in sparse_results:
                doc_id = result.chunk.id
                rrf_score = self.sparse_weight / (self.rrf_k + result.rank)
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = (rrf_score, result.chunk, "sparse")
                else:
                    current_score, chunk, method = fused_scores[doc_id]
                    fused_scores[doc_id] = (current_score + rrf_score, chunk, f"{method}+sparse")

            # Process knowledge graph results
            for result in kg_results:
                doc_id = result.chunk.id
                rrf_score = self.kg_weight / (self.rrf_k + result.rank)
                if doc_id not in fused_scores:
                    fused_scores[doc_id] = (rrf_score, result.chunk, "kg")
                else:
                    current_score, chunk, method = fused_scores[doc_id]
                    fused_scores[doc_id] = (current_score + rrf_score, chunk, f"{method}+kg")

            # Sort by fused score
            sorted_results = sorted(fused_scores.items(), key=lambda x: x[1][0], reverse=True)

            # Create final results
            results = []
            for i, (doc_id, (score, chunk, method)) in enumerate(sorted_results[: config.top_k]):
                results.append(
                    RetrievalResult(
                        chunk=chunk,
                        score=score,
                        retrieval_method=f"tri_rag:{method}",
                        rank=i + 1,
                    )
                )

            elapsed = (time.time() - start_time) * 1000
            logger.info(
                "tri_rag_retrieval_complete",
                query_length=len(query),
                dense_count=len(dense_results),
                sparse_count=len(sparse_results),
                kg_count=len(kg_results),
                fused_count=len(results),
                elapsed_ms=elapsed,
            )

            return results

        except Exception as e:
            logger.error("tri_rag_retrieval_error", error=str(e))
            return []

    async def add_documents(
        self,
        chunks: list[KnowledgeChunk],
        collection: str = "default",
    ) -> bool:
        """Add documents to all three retrievers"""
        try:
            # Add to dense and sparse in parallel
            dense_task = asyncio.create_task(self.dense_retriever.add_documents(chunks, collection))
            sparse_task = asyncio.create_task(self.sparse_retriever.add_documents(chunks, collection))
            kg_task = asyncio.create_task(self.kg_retriever.add_documents(chunks, collection))

            results = await asyncio.gather(dense_task, sparse_task, kg_task)
            return all(results)

        except Exception as e:
            logger.error("tri_rag_add_documents_error", error=str(e))
            return False


# Export classes
__all__ = [
    "Retriever",
    "DenseRetriever",
    "SparseRetriever",
    "HybridRetriever",
    "AdaptiveRetriever",
    "KnowledgeGraphRetriever",
    "TriRAGRetriever",
    "RetrievalConfig",
    "RetrievalResult",
]
