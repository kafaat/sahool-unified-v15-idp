"""
Copilot API Configuration
إعدادات Copilot API

Centralized configuration management with environment variables.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    إعدادات التطبيق المحملة من متغيرات البيئة
    """

    # ═══════════════════════════════════════════════════════════════════════════
    # SERVICE CONFIGURATION
    # ═══════════════════════════════════════════════════════════════════════════

    service_name: str = Field(default="copilot-api", description="Service name")
    service_version: str = Field(default="1.0.0", description="Service version")
    environment: str = Field(default="development", description="Environment")
    debug: bool = Field(default=False, description="Debug mode")
    log_level: str = Field(default="INFO", description="Log level")

    # Server settings (0.0.0.0 is intentional for containerized deployment)
    host: str = Field(default="0.0.0.0", description="Server host")  # nosec B104
    port: int = Field(default=8088, description="Server port")
    workers: int = Field(default=1, description="Number of workers")

    # ═══════════════════════════════════════════════════════════════════════════
    # SECURITY
    # ═══════════════════════════════════════════════════════════════════════════

    jwt_secret_key: str = Field(default="changeme-in-production-minimum-32-chars", description="JWT secret key")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")
    jwt_expiration_minutes: int = Field(default=60, description="JWT expiration")

    # API Key (optional for internal services)
    api_key: str | None = Field(default=None, description="API key for authentication")

    # CORS
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:8080", description="Allowed CORS origins")

    # ═══════════════════════════════════════════════════════════════════════════
    # COPILOT SETTINGS
    # ═══════════════════════════════════════════════════════════════════════════

    # Mode
    copilot_mode: str = Field(default="offline", description="Copilot mode")
    enable_external: bool = Field(default=False, description="Enable external access")

    # Limits
    max_prompt_chars: int = Field(default=12000, description="Max prompt characters")
    max_args_size: int = Field(default=20000, description="Max tool args size")
    request_timeout_s: float = Field(default=30.0, description="Request timeout")
    max_files_changed: int = Field(default=20, description="Max files changed")

    # ═══════════════════════════════════════════════════════════════════════════
    # EXTERNAL LLM (Optional)
    # ═══════════════════════════════════════════════════════════════════════════

    external_llm_base_url: str | None = Field(default=None, description="External LLM URL")
    external_llm_api_key: str | None = Field(default=None, description="External LLM API key")
    external_llm_model: str = Field(default="gpt-4o-mini", description="External LLM model")
    external_llm_temperature: float = Field(default=0.2, description="LLM temperature")

    # Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama URL")
    ollama_model: str = Field(default="codellama:7b", description="Ollama model")

    # ═══════════════════════════════════════════════════════════════════════════
    # QDRANT (Vector Database)
    # ═══════════════════════════════════════════════════════════════════════════

    qdrant_host: str = Field(default="localhost", description="Qdrant host")
    qdrant_port: int = Field(default=6333, description="Qdrant port")
    qdrant_collection: str = Field(default="sahool_copilot_knowledge", description="Qdrant collection name")
    use_qdrant: bool = Field(default=True, description="Use Qdrant for RAG")

    # ═══════════════════════════════════════════════════════════════════════════
    # EMBEDDINGS
    # ═══════════════════════════════════════════════════════════════════════════

    embedding_provider: str = Field(default="sentence_transformers", description="Embedding provider")
    embedding_model: str = Field(default="paraphrase-multilingual-MiniLM-L12-v2", description="Embedding model")

    # ═══════════════════════════════════════════════════════════════════════════
    # DATABASE (PostgreSQL)
    # ═══════════════════════════════════════════════════════════════════════════

    database_url: str | None = Field(default=None, description="PostgreSQL connection URL for chat history persistence")

    # ═══════════════════════════════════════════════════════════════════════════
    # REDIS
    # ═══════════════════════════════════════════════════════════════════════════

    redis_url: str | None = Field(default=None, description="Redis URL")
    redis_password: str | None = Field(default=None, description="Redis password")

    # ═══════════════════════════════════════════════════════════════════════════
    # NATS
    # ═══════════════════════════════════════════════════════════════════════════

    nats_url: str = Field(default="nats://localhost:4222", description="NATS URL")

    # ═══════════════════════════════════════════════════════════════════════════
    # INTERNAL SERVICES
    # ═══════════════════════════════════════════════════════════════════════════

    # Code-Fix-Agent
    code_fix_agent_url: str = Field(default="http://localhost:8161", description="Code-Fix-Agent URL")

    # AI Advisor
    ai_advisor_url: str = Field(default="http://localhost:8112", description="AI Advisor URL")

    # Field Management
    field_management_url: str = Field(default="http://localhost:3000", description="Field Management Service URL")

    # Weather Service
    weather_service_url: str = Field(default="http://localhost:8108", description="Weather Service URL")

    # ═══════════════════════════════════════════════════════════════════════════
    # COMPUTED PROPERTIES
    # ═══════════════════════════════════════════════════════════════════════════

    @property
    def cors_origins_list(self) -> list[str]:
        """Get CORS origins as list"""
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.environment.lower() == "production"

    @property
    def is_offline_mode(self) -> bool:
        """Check if running in offline mode"""
        return self.copilot_mode.lower() == "offline" or not self.enable_external

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """
    Get cached settings instance.
    الحصول على نسخة مخزنة من الإعدادات
    """
    return Settings()
