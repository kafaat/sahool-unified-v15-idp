"""
Knowledge Retriever
مسترجع المعرفة

Retrieves relevant knowledge from Qdrant vector database.
يسترجع المعرفة ذات الصلة من قاعدة بيانات المتجهات Qdrant.
"""

from dataclasses import dataclass
from typing import Any

import structlog
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    MatchValue,
    PointStruct,
    VectorParams,
)

from ..config import settings
from .embeddings import EmbeddingsManager

logger = structlog.get_logger()


@dataclass
class Document:
    """
    Retrieved document
    مستند مسترجع
    """

    content: str
    metadata: dict[str, Any]
    score: float
    id: str


class KnowledgeRetriever:
    """
    Retrieves relevant knowledge from vector database
    يسترجع المعرفة ذات الصلة من قاعدة بيانات المتجهات

    Uses Qdrant for vector storage and retrieval.
    يستخدم Qdrant لتخزين واسترجاع المتجهات.
    """

    def __init__(
        self,
        embeddings_manager: EmbeddingsManager | None = None,
        collection_name: str | None = None,
    ):
        """
        Initialize knowledge retriever
        تهيئة مسترجع المعرفة

        Args:
            embeddings_manager: Embeddings manager instance | مثيل مدير التضمينات
            collection_name: Qdrant collection name | اسم مجموعة Qdrant
        """
        self.embeddings = embeddings_manager or EmbeddingsManager()
        self.collection_name = collection_name or settings.qdrant_collection

        # Initialize Qdrant client
        # تهيئة عميل Qdrant
        self.client = QdrantClient(
            host=settings.qdrant_host,
            port=settings.qdrant_port,
            api_key=settings.qdrant_api_key,
        )

        # Ensure collection exists
        # التأكد من وجود المجموعة
        self._ensure_collection()

        logger.info(
            "knowledge_retriever_initialized",
            collection_name=self.collection_name,
            qdrant_host=settings.qdrant_host,
        )

    def _ensure_collection(self):
        """
        Ensure the collection exists in Qdrant
        التأكد من وجود المجموعة في Qdrant
        """
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]

            if self.collection_name not in collection_names:
                # Create collection
                # إنشاء المجموعة
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=self.embeddings.embedding_dimension,
                        distance=Distance.COSINE,
                    ),
                )
                logger.info(
                    "qdrant_collection_created", collection_name=self.collection_name
                )
            else:
                logger.info(
                    "qdrant_collection_exists", collection_name=self.collection_name
                )

        except Exception as e:
            logger.error("qdrant_collection_check_failed", error=str(e))
            # Continue without raising - collection might exist
            # المتابعة دون إثارة خطأ - قد تكون المجموعة موجودة

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
        ids: list[str] | None = None,
    ) -> bool:
        """
        Add documents to the knowledge base
        إضافة مستندات إلى قاعدة المعرفة

        Args:
            documents: List of document texts | قائمة نصوص المستندات
            metadatas: List of metadata dicts | قائمة قواميس البيانات الوصفية
            ids: List of document IDs | قائمة معرفات المستندات

        Returns:
            Success status | حالة النجاح
        """
        try:
            # Generate embeddings
            # توليد التضمينات
            embeddings = self.embeddings.encode_documents(documents)

            # Prepare metadata
            # تحضير البيانات الوصفية
            if metadatas is None:
                metadatas = [{} for _ in documents]

            # Generate IDs if not provided
            # توليد المعرفات إذا لم يتم توفيرها
            if ids is None:
                import uuid

                ids = [str(uuid.uuid4()) for _ in documents]

            # Create points
            # إنشاء النقاط
            points = [
                PointStruct(
                    id=doc_id,
                    vector=embedding.tolist(),
                    payload={
                        "content": document,
                        **metadata,
                    },
                )
                for doc_id, document, embedding, metadata in zip(
                    ids, documents, embeddings, metadatas, strict=False
                )
            ]

            # Upsert to Qdrant
            # إدراج في Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )

            logger.info(
                "documents_added_to_knowledge_base",
                num_documents=len(documents),
                collection_name=self.collection_name,
            )

            return True

        except Exception as e:
            logger.error(
                "document_addition_failed", error=str(e), num_documents=len(documents)
            )
            return False

    def retrieve(
        self,
        query: str,
        top_k: int = None,
        score_threshold: float = None,
        filters: dict[str, Any] | None = None,
    ) -> list[Document]:
        """
        Retrieve relevant documents
        استرجاع المستندات ذات الصلة

        Args:
            query: Search query | استعلام البحث
            top_k: Number of documents to retrieve | عدد المستندات المراد استرجاعها
            score_threshold: Minimum similarity score | الحد الأدنى لدرجة التشابه
            filters: Metadata filters | فلاتر البيانات الوصفية

        Returns:
            List of retrieved documents | قائمة المستندات المستردة
        """
        try:
            # Generate query embedding
            # توليد تضمين الاستعلام
            query_embedding = self.embeddings.encode_query(query)

            # Set defaults
            # تعيين القيم الافتراضية
            top_k = top_k or settings.rag_top_k
            score_threshold = score_threshold or settings.rag_score_threshold

            # Build filter if provided
            # بناء الفلتر إذا تم توفيره
            query_filter = None
            if filters:
                # Simple implementation - extend as needed
                # تنفيذ بسيط - قم بالتوسيع حسب الحاجة
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(key=key, match=MatchValue(value=value))
                    )
                if conditions:
                    query_filter = Filter(must=conditions)

            # Search in Qdrant
            # البحث في Qdrant
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=top_k,
                score_threshold=score_threshold,
                query_filter=query_filter,
            )

            # Convert to Document objects
            # التحويل إلى كائنات Document
            documents = []
            for result in search_results:
                doc = Document(
                    content=result.payload.get("content", ""),
                    metadata={
                        k: v for k, v in result.payload.items() if k != "content"
                    },
                    score=result.score,
                    id=str(result.id),
                )
                documents.append(doc)

            logger.info(
                "knowledge_retrieved",
                query_length=len(query),
                num_results=len(documents),
                top_score=documents[0].score if documents else 0,
            )

            return documents

        except Exception as e:
            logger.error("knowledge_retrieval_failed", error=str(e), query=query[:100])
            return []

    def delete_documents(
        self,
        ids: list[str],
    ) -> bool:
        """
        Delete documents from the knowledge base
        حذف مستندات من قاعدة المعرفة

        Args:
            ids: List of document IDs to delete | قائمة معرفات المستندات للحذف

        Returns:
            Success status | حالة النجاح
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=ids,
            )

            logger.info(
                "documents_deleted",
                num_documents=len(ids),
                collection_name=self.collection_name,
            )

            return True

        except Exception as e:
            logger.error("document_deletion_failed", error=str(e), num_ids=len(ids))
            return False

    def get_collection_info(self) -> dict[str, Any]:
        """
        Get information about the collection
        الحصول على معلومات حول المجموعة

        Returns:
            Collection information | معلومات المجموعة
        """
        try:
            collection_info = self.client.get_collection(
                collection_name=self.collection_name
            )

            return {
                "collection_name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status,
            }

        except Exception as e:
            logger.error("collection_info_retrieval_failed", error=str(e))
            return {"collection_name": self.collection_name, "error": str(e)}
