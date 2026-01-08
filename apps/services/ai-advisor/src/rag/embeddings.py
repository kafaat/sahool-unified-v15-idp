"""
Embeddings Manager
مدير التضمينات

Manages text embeddings using sentence-transformers.
يدير تضمينات النصوص باستخدام sentence-transformers.
"""

import numpy as np
import structlog
from sentence_transformers import SentenceTransformer

from ..config import settings

logger = structlog.get_logger()


class EmbeddingsManager:
    """
    Manages text embeddings for RAG
    يدير تضمينات النصوص لـ RAG

    Uses multilingual models to support both Arabic and English.
    يستخدم نماذج متعددة اللغات لدعم العربية والإنجليزية.
    """

    def __init__(
        self,
        model_name: str = None,
        device: str = None,
    ):
        """
        Initialize embeddings manager
        تهيئة مدير التضمينات

        Args:
            model_name: Name of the embedding model | اسم نموذج التضمين
            device: Device to use (cpu/cuda) | الجهاز المستخدم
        """
        self.model_name = model_name or settings.embeddings_model
        self.device = device or settings.embeddings_device

        logger.info("loading_embeddings_model", model_name=self.model_name, device=self.device)

        # Load the model
        # تحميل النموذج
        self.model = SentenceTransformer(self.model_name, device=self.device)

        self.embedding_dimension = self.model.get_sentence_embedding_dimension()

        logger.info(
            "embeddings_model_loaded",
            model_name=self.model_name,
            dimension=self.embedding_dimension,
        )

    def encode(
        self,
        texts: str | list[str],
        batch_size: int = 32,
        show_progress: bool = False,
    ) -> np.ndarray:
        """
        Generate embeddings for text(s)
        توليد التضمينات للنص/النصوص

        Args:
            texts: Single text or list of texts | نص واحد أو قائمة نصوص
            batch_size: Batch size for encoding | حجم الدفعة للترميز
            show_progress: Show progress bar | إظهار شريط التقدم

        Returns:
            Embeddings array | مصفوفة التضمينات
        """
        try:
            # Ensure texts is a list
            # التأكد من أن النصوص قائمة
            if isinstance(texts, str):
                texts = [texts]

            # Generate embeddings
            # توليد التضمينات
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True,
            )

            logger.debug(
                "embeddings_generated",
                num_texts=len(texts),
                embedding_shape=embeddings.shape,
            )

            return embeddings

        except Exception as e:
            logger.error("embedding_generation_failed", error=str(e))
            raise

    def encode_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a search query
        توليد التضمين لاستعلام البحث

        Args:
            query: Search query | استعلام البحث

        Returns:
            Query embedding | تضمين الاستعلام
        """
        return self.encode(query)[0]

    def encode_documents(
        self,
        documents: list[str],
        batch_size: int = 32,
    ) -> np.ndarray:
        """
        Generate embeddings for multiple documents
        توليد التضمينات لمستندات متعددة

        Args:
            documents: List of document texts | قائمة نصوص المستندات
            batch_size: Batch size for encoding | حجم الدفعة للترميز

        Returns:
            Document embeddings | تضمينات المستندات
        """
        return self.encode(documents, batch_size=batch_size, show_progress=True)

    def similarity(
        self,
        embedding1: np.ndarray,
        embedding2: np.ndarray,
    ) -> float:
        """
        Calculate cosine similarity between two embeddings
        حساب التشابه بين تضمينين

        Args:
            embedding1: First embedding | التضمين الأول
            embedding2: Second embedding | التضمين الثاني

        Returns:
            Cosine similarity score | درجة التشابه
        """
        # Normalize embeddings
        # تطبيع التضمينات
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Calculate cosine similarity
        # حساب التشابه
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)

        return float(similarity)

    def batch_similarity(
        self,
        query_embedding: np.ndarray,
        document_embeddings: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate similarity between query and multiple documents
        حساب التشابه بين الاستعلام ومستندات متعددة

        Args:
            query_embedding: Query embedding | تضمين الاستعلام
            document_embeddings: Document embeddings | تضمينات المستندات

        Returns:
            Array of similarity scores | مصفوفة درجات التشابه
        """
        # Normalize query embedding
        # تطبيع تضمين الاستعلام
        query_norm = query_embedding / np.linalg.norm(query_embedding)

        # Normalize document embeddings
        # تطبيع تضمينات المستندات
        doc_norms = np.linalg.norm(document_embeddings, axis=1, keepdims=True)
        doc_normalized = document_embeddings / doc_norms

        # Calculate cosine similarities
        # حساب التشابهات
        similarities = np.dot(doc_normalized, query_norm)

        return similarities

    def get_model_info(self) -> dict:
        """
        Get model information
        الحصول على معلومات النموذج

        Returns:
            Model information | معلومات النموذج
        """
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dimension,
            "device": self.device,
            "max_sequence_length": self.model.max_seq_length,
        }
