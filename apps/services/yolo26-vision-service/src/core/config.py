"""
YOLO26 Vision Service Configuration.

Settings management using pydantic-settings for the SAHOOL agricultural
computer vision service.
"""

import logging
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Service Configuration
    service_name: str = Field(default="yolo26-vision-service", description="Service name")
    service_version: str = Field(default="16.0.0", description="Service version")
    environment: Literal["development", "staging", "production", "test"] = Field(
        default="development", description="Deployment environment"
    )
    debug: bool = Field(default=False, description="Enable debug mode")
    host: str = Field(default="0.0.0.0", description="Service host")
    port: int = Field(default=8150, description="Service port")

    # Database Configuration
    database_url: str = Field(
        default="",
        description="PostgreSQL connection URL with PostGIS",
    )
    db_pool_min_size: int = Field(default=2, description="Minimum database pool size")
    db_pool_max_size: int = Field(default=10, description="Maximum database pool size")

    # NATS Configuration
    nats_url: str = Field(default="", description="NATS server URL")
    nats_cluster_id: str = Field(default="sahool-cluster", description="NATS cluster ID")

    # Redis Configuration
    redis_url: str = Field(default="", description="Redis connection URL")
    redis_ttl_seconds: int = Field(default=3600, description="Default Redis TTL")

    # JWT Authentication — empty default ensures decode fails (no silent auth bypass)
    jwt_secret_key: str = Field(default="", description="JWT secret key — must be set via JWT_SECRET_KEY env var")
    jwt_algorithm: str = Field(default="HS256", description="JWT algorithm")

    # CORS Configuration
    cors_origins: list[str] = Field(
        default=["*"],
        description="Allowed CORS origins",
    )

    # Model Configuration
    model_base_path: str = Field(
        default="/models",
        description="Base path for YOLO26 models",
    )
    default_model_variant: Literal["n", "s", "m", "l", "x"] = Field(
        default="m",
        description="Default YOLO26 model variant (n=nano, s=small, m=medium, l=large, x=xlarge)",
    )
    enable_tensorrt: bool = Field(
        default=False,
        description="Enable TensorRT optimization for inference",
    )
    model_cache_size: int = Field(
        default=5,
        description="Maximum number of models to cache in memory",
    )

    # Inference Configuration
    default_confidence_threshold: float = Field(
        default=0.25,
        ge=0.0,
        le=1.0,
        description="Default confidence threshold for detections",
    )
    default_iou_threshold: float = Field(
        default=0.45,
        ge=0.0,
        le=1.0,
        description="Default IoU threshold for NMS",
    )
    max_detections: int = Field(
        default=300,
        ge=1,
        le=1000,
        description="Maximum detections per image",
    )
    default_image_size: int = Field(
        default=640,
        description="Default input image size",
    )

    # GPU Configuration
    device: str = Field(
        default="cuda:0",
        description="Device for inference (cuda:0, cuda:1, cpu)",
    )
    half_precision: bool = Field(
        default=True,
        description="Use FP16 half precision for faster inference",
    )

    # Performance Configuration
    batch_size: int = Field(default=1, ge=1, le=32, description="Batch size for inference")
    num_workers: int = Field(default=4, ge=1, le=16, description="Number of worker threads")

    # Logging Configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level",
    )

    # Upload Configuration
    max_upload_size_mb: int = Field(
        default=50,
        description="Maximum upload file size in MB",
    )
    allowed_image_extensions: list[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"],
        description="Allowed image file extensions",
    )

    # VLM Secondary Verification Configuration
    # Reduces false positives ~40% and false negatives ~30% (YOLO + Qwen-VL cooperative)
    vlm_provider: str = Field(
        default="disabled",
        description="VLM provider for secondary verification: disabled | qwen_vl | ollama | vllm",
    )
    qwen_vl_api_key: str = Field(
        default="",
        description="DashScope API key for Qwen-VL (set via QWEN_VL_API_KEY env var)",
    )
    qwen_vl_api_url: str = Field(
        default="",
        description="Qwen-VL API endpoint URL (empty = use DashScope default)",
    )
    qwen_vl_model: str = Field(
        default="qwen-vl-plus",
        description="Qwen-VL model variant (qwen-vl-plus or qwen-vl-max)",
    )
    ollama_vlm_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server base URL for local vision models",
    )
    ollama_vlm_model: str = Field(
        default="llava:7b",
        description="Ollama vision model name (llava:7b, bakllava, llava:13b, etc.)",
    )
    # vLLM — platform-internal OpenAI-compat multimodal service (sahool-vllm:8270)
    vllm_vlm_url: str = Field(
        default="http://sahool-vllm:8270/v1",
        description="vLLM server base URL for vision inference (platform-internal)",
    )
    vllm_vlm_model: str = Field(
        default="deepseek-ai/deepseek-vl2",
        description="Model name served by the vLLM server (must support vision/multimodal input)",
    )
    vlm_confirm_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="VLM confidence >= this value confirms detection (CONFIRMED verdict)",
    )
    vlm_suspect_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="VLM confidence >= this value but < confirm_threshold marks detection as suspicious",
    )
    vlm_timeout_seconds: float = Field(
        default=30.0,
        gt=0.0,
        description="Timeout in seconds for VLM API calls",
    )

    @field_validator("jwt_secret_key", mode="after")
    @classmethod
    def warn_empty_jwt_secret(cls, v: str) -> str:
        """Warn if JWT secret key is not configured."""
        if not v:
            _logger.warning("JWT_SECRET_KEY not set — authentication will reject all tokens")
        return v

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | list[str]) -> list[str]:
        """Parse CORS origins from comma-separated string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    @field_validator("allowed_image_extensions", mode="before")
    @classmethod
    def parse_extensions(cls, v: str | list[str]) -> list[str]:
        """Parse allowed extensions from comma-separated string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",") if ext.strip()]
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        """Get maximum upload size in bytes."""
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Export settings instance for convenience
settings = get_settings()
