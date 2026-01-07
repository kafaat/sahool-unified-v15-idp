"""
Configuration settings for Code Review Service
إعدادات خدمة مراجعة الكود

Enhanced with multi-model support, caching, and GitHub integration
محسن بدعم النماذج المتعددة والتخزين المؤقت وتكامل GitHub
"""

from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class ModelConfig(BaseSettings):
    """Configuration for a single LLM model"""
    name: str = "deepseek-coder-v2"
    endpoint: str = "http://ollama:11434"
    timeout: int = 60
    temperature: float = 0.3
    max_tokens: int = 2000
    priority: int = 1  # Lower = higher priority


class Settings(BaseSettings):
    """Application settings - Enhanced"""

    # ═══════════════════════════════════════════════════════════════════════════
    # Multi-Model Configuration (with fallback support)
    # ═══════════════════════════════════════════════════════════════════════════

    # Primary model (deepseek-coder-v2 - latest version optimized for code)
    ollama_url: str = "http://ollama:11434"
    ollama_model: str = "deepseek-coder-v2"

    # Fallback models (comma-separated: model1@url1,model2@url2)
    # Priority: deepseek-coder-v2 > deepseek-coder > codellama > starcoder > llama2
    fallback_models: str = "deepseek-coder@http://ollama:11434,codellama@http://ollama:11434,starcoder@http://ollama:11434,llama2@http://ollama:11434"

    # Model selection strategy: "primary_first", "round_robin", "fastest"
    model_strategy: str = "primary_first"

    # Enable automatic model fallback
    enable_fallback: bool = True

    # Retry configuration
    max_retries: int = 3
    retry_delay: float = 1.0  # seconds

    # ═══════════════════════════════════════════════════════════════════════════
    # GitHub Integration
    # ═══════════════════════════════════════════════════════════════════════════

    github_token: Optional[str] = None
    github_api_url: str = "https://api.github.com"
    github_webhook_secret: Optional[str] = None

    # Auto-comment on PRs
    github_auto_comment: bool = True
    github_comment_threshold: int = 70  # Only comment if score < threshold

    # Repository configuration
    github_repo_owner: str = "kafaat"
    github_repo_name: str = "sahool-unified-v15-idp"

    # ═══════════════════════════════════════════════════════════════════════════
    # Caching Configuration
    # ═══════════════════════════════════════════════════════════════════════════

    # Enable review caching
    enable_cache: bool = True

    # Cache backend: "memory", "redis", "file"
    cache_backend: str = "memory"

    # Redis configuration (if cache_backend = "redis")
    redis_url: str = "redis://redis:6379/2"

    # Cache TTL in seconds (1 hour default)
    cache_ttl: int = 3600

    # Maximum cache size (for memory backend)
    cache_max_size: int = 1000

    # Cache file path (for file backend)
    cache_file_path: str = "/app/cache/reviews.json"

    # ═══════════════════════════════════════════════════════════════════════════
    # Agricultural Domain Rules
    # ═══════════════════════════════════════════════════════════════════════════

    # Enable SAHOOL-specific agricultural rules
    enable_agricultural_rules: bool = True

    # Agricultural patterns to check
    agricultural_keywords: str = "ndvi,lai,evapotranspiration,soil_moisture,crop_health,irrigation,harvest,yield,fertilizer,pesticide,sensor,iot"

    # NDVI value range validation
    ndvi_min_value: float = -1.0
    ndvi_max_value: float = 1.0

    # LAI value range validation
    lai_min_value: float = 0.0
    lai_max_value: float = 10.0

    # Soil moisture range (percentage)
    soil_moisture_min: float = 0.0
    soil_moisture_max: float = 100.0

    # ═══════════════════════════════════════════════════════════════════════════
    # Watch Configuration
    # ═══════════════════════════════════════════════════════════════════════════

    watch_paths: str = "infrastructure:docker-compose.yml:docker:apps/services"
    review_on_change: bool = True
    max_file_size: int = 1000000  # 1MB

    # Debounce delay for file changes (seconds)
    debounce_delay: float = 2.0

    # ═══════════════════════════════════════════════════════════════════════════
    # API Server Configuration
    # ═══════════════════════════════════════════════════════════════════════════

    api_host: str = "0.0.0.0"
    api_port: int = 8096

    # Rate limiting
    rate_limit_requests: int = 100
    rate_limit_period: int = 60  # seconds

    # ═══════════════════════════════════════════════════════════════════════════
    # Logging & Observability
    # ═══════════════════════════════════════════════════════════════════════════

    log_level: str = "INFO"
    log_reviews_to_file: bool = True
    metrics_enabled: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = False

    def get_fallback_models_list(self) -> list[tuple[str, str]]:
        """Parse fallback models string into list of (model, url) tuples"""
        models = []
        if self.fallback_models:
            for entry in self.fallback_models.split(","):
                entry = entry.strip()
                if "@" in entry:
                    model, url = entry.split("@", 1)
                    models.append((model.strip(), url.strip()))
                else:
                    # Use default ollama_url if no URL specified
                    models.append((entry.strip(), self.ollama_url))
        return models

    def get_agricultural_keywords_list(self) -> list[str]:
        """Parse agricultural keywords into list"""
        return [kw.strip().lower() for kw in self.agricultural_keywords.split(",") if kw.strip()]
