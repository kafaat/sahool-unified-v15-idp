"""
Vector Service Settings
إعدادات خدمة المتجهات
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Configuration settings for Vector Service"""

    # Milvus connection
    milvus_host: str = "milvus"
    milvus_port: int = 19530
    milvus_db: str = "sahool"
    milvus_collection: str = "sahool_vectors"

    # Embedding configuration
    embedding_provider: str = "sentence_transformers"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_dim: int = 384

    # Security
    tenant_filter_required: bool = True

    # Service
    port: int = 8111

    # Search defaults
    default_top_k: int = 5
    max_top_k: int = 20
    max_context_chars: int = 4000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
