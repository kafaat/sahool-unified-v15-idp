"""
AI Advisor Service Configuration
إعدادات خدمة المستشار الذكي

This module manages all environment variables and service configuration.
تدير هذه الوحدة جميع متغيرات البيئة وإعدادات الخدمة.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    إعدادات التطبيق المحملة من متغيرات البيئة
    """

    # Service Configuration | إعدادات الخدمة
    service_name: str = "ai-advisor"
    service_port: int = 8112
    log_level: str = "INFO"

    # Anthropic Claude API | واجهة برمجة Claude
    anthropic_api_key: str
    claude_model: str = "claude-3-5-sonnet-20241022"
    max_tokens: int = 4096
    temperature: float = 0.7

    # External Services | الخدمات الخارجية
    crop_health_ai_url: str = "http://crop-health-ai:8109"
    weather_core_url: str = "http://weather-core:8002"
    satellite_service_url: str = "http://satellite-service:8108"
    agro_advisor_url: str = "http://agro-advisor:8003"

    # Qdrant Vector Database | قاعدة بيانات المتجهات Qdrant
    qdrant_host: str = "qdrant"
    qdrant_port: int = 6333
    qdrant_collection: str = "agricultural_knowledge"
    qdrant_api_key: Optional[str] = None

    # NATS Messaging | نظام الرسائل NATS
    nats_url: str = "nats://nats:4222"
    nats_subject_prefix: str = "sahool.ai-advisor"

    # Embeddings Model | نموذج التضمينات
    embeddings_model: str = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    embeddings_device: str = "cpu"  # or "cuda" for GPU

    # Agent Configuration | إعدادات الوكلاء
    max_agent_iterations: int = 5
    agent_timeout: int = 120  # seconds

    # RAG Configuration | إعدادات RAG
    rag_top_k: int = 5
    rag_score_threshold: float = 0.7

    # Cache Settings | إعدادات التخزين المؤقت
    enable_cache: bool = True
    cache_ttl: int = 3600  # seconds

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance | مثيل الإعدادات العام
settings = Settings()
