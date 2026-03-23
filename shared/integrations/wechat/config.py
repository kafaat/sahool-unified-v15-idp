"""
WeChat Integration Configuration
================================
تكوين تكامل WeChat

Configuration management for WeChat MCP integration with SAHOOL platform.
Supports environment variable loading and validation.

Author: SAHOOL Platform Team
Updated: January 2026
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import structlog

logger = structlog.get_logger()


class WeChatEnvironment(StrEnum):
    """
    WeChat deployment environment.
    بيئة نشر WeChat
    """

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class WeChatTransport(StrEnum):
    """
    WeChat MCP transport type.
    نوع نقل WeChat MCP
    """

    HTTP = "http"
    WEBSOCKET = "websocket"
    STDIO = "stdio"


class AgentModel(StrEnum):
    """
    AI model options for WeChat agents.
    خيارات نماذج الذكاء الاصطناعي لوكلاء WeChat
    """

    CLAUDE_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_HAIKU = "claude-3-5-haiku-20241022"
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    QWEN_PLUS = "qwen-plus"  # For Chinese language optimization
    OLLAMA_LOCAL = "ollama-local"


@dataclass
class RateLimitConfig:
    """
    Rate limiting configuration for WeChat API.
    تكوين تحديد معدل API WeChat
    """

    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    burst_limit: int = 10
    retry_after_seconds: int = 60


@dataclass
class RetryConfig:
    """
    Retry configuration for failed requests.
    تكوين إعادة المحاولة للطلبات الفاشلة
    """

    max_retries: int = 3
    base_delay_seconds: float = 1.0
    max_delay_seconds: float = 60.0
    exponential_base: float = 2.0


@dataclass
class CacheConfig:
    """
    Cache configuration for WeChat data.
    تكوين ذاكرة التخزين المؤقت لبيانات WeChat
    """

    enabled: bool = True
    ttl_seconds: int = 300  # 5 minutes
    max_size: int = 1000
    message_cache_ttl: int = 3600  # 1 hour for messages
    contact_cache_ttl: int = 86400  # 24 hours for contacts


@dataclass
class WeChatConfig:
    """
    WeChat MCP Client Configuration.
    تكوين عميل WeChat MCP

    Loads configuration from environment variables with sensible defaults.
    Supports both development and production environments.

    Environment Variables:
        WECHAT_MCP_URL: MCP server URL
        WECHAT_MCP_API_KEY: API key for authentication
        WECHAT_APP_ID: WeChat App ID
        WECHAT_APP_SECRET: WeChat App Secret
        WECHAT_ENVIRONMENT: Deployment environment
        WECHAT_TIMEOUT: Request timeout in seconds
        WECHAT_LANGUAGE: Default language (ar/en/zh)

    Example:
        config = WeChatConfig.from_env()
        client = WeChatMCPClient(config)
    """

    # Connection settings
    mcp_url: str = "http://localhost:8765"
    api_key: str | None = None
    transport: WeChatTransport = WeChatTransport.HTTP

    # WeChat credentials
    app_id: str | None = None
    app_secret: str | None = None
    access_token: str | None = None
    token_expires_at: int | None = None

    # Environment
    environment: WeChatEnvironment = WeChatEnvironment.DEVELOPMENT
    tenant_id: str = "sahool"

    # Timeouts (seconds)
    connect_timeout: float = 10.0
    read_timeout: float = 30.0
    write_timeout: float = 30.0

    # Bilingual settings
    default_language: str = "ar"  # ar, en, zh
    supported_languages: list[str] = field(default_factory=lambda: ["ar", "en", "zh"])

    # Agent settings
    agent_model: AgentModel = AgentModel.CLAUDE_SONNET
    agent_temperature: float = 0.7
    agent_max_tokens: int = 4096

    # Feature flags
    enable_auto_reply: bool = True
    enable_message_summary: bool = True
    enable_sentiment_analysis: bool = True
    enable_priority_detection: bool = True
    enable_agricultural_context: bool = True

    # Rate limiting
    rate_limit: RateLimitConfig = field(default_factory=RateLimitConfig)

    # Retry configuration
    retry: RetryConfig = field(default_factory=RetryConfig)

    # Cache configuration
    cache: CacheConfig = field(default_factory=CacheConfig)

    # Logging
    log_level: str = "INFO"
    log_messages: bool = False  # Be careful with privacy

    # Agricultural domain settings
    farm_context_enabled: bool = True
    crop_vocabulary_enabled: bool = True
    weather_integration: bool = True

    # Metadata
    version: str = "1.0.0"
    service_name: str = "wechat-integration"
    service_name_ar: str = "تكامل WeChat"

    @classmethod
    def from_env(cls) -> WeChatConfig:
        """
        Create configuration from environment variables.
        إنشاء التكوين من متغيرات البيئة

        Returns:
            WeChatConfig: Configuration instance

        Example:
            config = WeChatConfig.from_env()
        """

        def get_bool(key: str, default: bool = False) -> bool:
            return os.getenv(key, str(default)).lower() in ("true", "1", "yes")

        def get_float(key: str, default: float) -> float:
            try:
                return float(os.getenv(key, str(default)))
            except ValueError:
                return default

        def get_int(key: str, default: int) -> int:
            try:
                return int(os.getenv(key, str(default)))
            except ValueError:
                return default

        # Parse transport
        transport_str = os.getenv("WECHAT_TRANSPORT", "http").lower()
        transport = (
            WeChatTransport(transport_str)
            if transport_str in [t.value for t in WeChatTransport]
            else WeChatTransport.HTTP
        )

        # Parse environment
        env_str = os.getenv("WECHAT_ENVIRONMENT", "development").lower()
        environment = (
            WeChatEnvironment(env_str)
            if env_str in [e.value for e in WeChatEnvironment]
            else WeChatEnvironment.DEVELOPMENT
        )

        # Parse agent model
        model_str = os.getenv("WECHAT_AGENT_MODEL", "claude-3-5-sonnet-20241022")
        try:
            agent_model = AgentModel(model_str)
        except ValueError:
            agent_model = AgentModel.CLAUDE_SONNET

        # Create rate limit config
        rate_limit = RateLimitConfig(
            requests_per_minute=get_int("WECHAT_RATE_LIMIT_RPM", 60),
            requests_per_hour=get_int("WECHAT_RATE_LIMIT_RPH", 1000),
            burst_limit=get_int("WECHAT_RATE_LIMIT_BURST", 10),
            retry_after_seconds=get_int("WECHAT_RATE_LIMIT_RETRY", 60),
        )

        # Create retry config
        retry = RetryConfig(
            max_retries=get_int("WECHAT_MAX_RETRIES", 3),
            base_delay_seconds=get_float("WECHAT_RETRY_DELAY", 1.0),
            max_delay_seconds=get_float("WECHAT_RETRY_MAX_DELAY", 60.0),
            exponential_base=get_float("WECHAT_RETRY_EXPONENTIAL", 2.0),
        )

        # Create cache config
        cache = CacheConfig(
            enabled=get_bool("WECHAT_CACHE_ENABLED", True),
            ttl_seconds=get_int("WECHAT_CACHE_TTL", 300),
            max_size=get_int("WECHAT_CACHE_MAX_SIZE", 1000),
            message_cache_ttl=get_int("WECHAT_MESSAGE_CACHE_TTL", 3600),
            contact_cache_ttl=get_int("WECHAT_CONTACT_CACHE_TTL", 86400),
        )

        config = cls(
            # Connection
            mcp_url=os.getenv("WECHAT_MCP_URL", "http://localhost:8765"),
            api_key=os.getenv("WECHAT_MCP_API_KEY"),
            transport=transport,
            # WeChat credentials
            app_id=os.getenv("WECHAT_APP_ID"),
            app_secret=os.getenv("WECHAT_APP_SECRET"),
            access_token=os.getenv("WECHAT_ACCESS_TOKEN"),
            # Environment
            environment=environment,
            tenant_id=os.getenv("TENANT_ID", "sahool"),
            # Timeouts
            connect_timeout=get_float("WECHAT_CONNECT_TIMEOUT", 10.0),
            read_timeout=get_float("WECHAT_READ_TIMEOUT", 30.0),
            write_timeout=get_float("WECHAT_WRITE_TIMEOUT", 30.0),
            # Language
            default_language=os.getenv("WECHAT_DEFAULT_LANGUAGE", "ar"),
            # Agent settings
            agent_model=agent_model,
            agent_temperature=get_float("WECHAT_AGENT_TEMPERATURE", 0.7),
            agent_max_tokens=get_int("WECHAT_AGENT_MAX_TOKENS", 4096),
            # Features
            enable_auto_reply=get_bool("WECHAT_AUTO_REPLY", True),
            enable_message_summary=get_bool("WECHAT_MESSAGE_SUMMARY", True),
            enable_sentiment_analysis=get_bool("WECHAT_SENTIMENT_ANALYSIS", True),
            enable_priority_detection=get_bool("WECHAT_PRIORITY_DETECTION", True),
            enable_agricultural_context=get_bool("WECHAT_AGRICULTURAL_CONTEXT", True),
            # Configs
            rate_limit=rate_limit,
            retry=retry,
            cache=cache,
            # Logging
            log_level=os.getenv("WECHAT_LOG_LEVEL", "INFO"),
            log_messages=get_bool("WECHAT_LOG_MESSAGES", False),
            # Agricultural
            farm_context_enabled=get_bool("WECHAT_FARM_CONTEXT", True),
            crop_vocabulary_enabled=get_bool("WECHAT_CROP_VOCABULARY", True),
            weather_integration=get_bool("WECHAT_WEATHER_INTEGRATION", True),
        )

        logger.info(
            "wechat_config_loaded",
            environment=config.environment.value,
            mcp_url=config.mcp_url,
            tenant_id=config.tenant_id,
            default_language=config.default_language,
        )

        return config

    def validate(self) -> list[str]:
        """
        Validate configuration and return list of errors.
        التحقق من صحة التكوين وإرجاع قائمة الأخطاء

        Returns:
            list[str]: List of validation error messages
        """
        errors = []

        # Check required credentials for production
        if self.environment == WeChatEnvironment.PRODUCTION:
            if not self.api_key:
                errors.append("API key required for production | مطلوب مفتاح API للإنتاج")
            if not self.app_id:
                errors.append("WeChat App ID required for production | مطلوب معرف تطبيق WeChat للإنتاج")
            if not self.app_secret:
                errors.append("WeChat App Secret required for production | مطلوب سر تطبيق WeChat للإنتاج")

        # SECURITY: Validate MCP URL scheme to prevent SSRF
        if self.mcp_url:
            from urllib.parse import urlparse

            parsed = urlparse(self.mcp_url)
            if parsed.scheme not in ("http", "https"):
                errors.append(
                    f"mcp_url must use http/https scheme, got '{parsed.scheme}' | "
                    f"يجب أن يستخدم عنوان MCP بروتوكول http/https"
                )
            if not parsed.hostname:
                errors.append("mcp_url must have a valid hostname | يجب أن يحتوي عنوان MCP على اسم مضيف صالح")

        # Validate timeouts
        if self.connect_timeout <= 0:
            errors.append("Connect timeout must be positive | يجب أن يكون وقت الاتصال إيجابياً")
        if self.read_timeout <= 0:
            errors.append("Read timeout must be positive | يجب أن يكون وقت القراءة إيجابياً")

        # SECURITY: Enforce timeout upper bounds to prevent resource exhaustion
        if self.connect_timeout > 120:
            errors.append(
                f"Connect timeout must not exceed 120 seconds, got {self.connect_timeout} | "
                f"يجب ألا يتجاوز وقت الاتصال 120 ثانية"
            )
        if self.read_timeout > 300:
            errors.append(
                f"Read timeout must not exceed 300 seconds, got {self.read_timeout} | "
                f"يجب ألا يتجاوز وقت القراءة 300 ثانية"
            )

        # Validate agent settings
        if self.agent_temperature < 0 or self.agent_temperature > 2:
            errors.append("Agent temperature must be between 0 and 2 | يجب أن تكون درجة حرارة الوكيل بين 0 و 2")
        if self.agent_max_tokens < 100:
            errors.append("Agent max tokens must be at least 100 | يجب أن يكون الحد الأقصى لرموز الوكيل 100 على الأقل")

        # Validate language
        if self.default_language not in self.supported_languages:
            errors.append(
                f"Default language must be one of {self.supported_languages} | يجب أن تكون اللغة الافتراضية واحدة من {self.supported_languages}"
            )

        return errors

    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary (safe for logging).
        تحويل التكوين إلى قاموس (آمن للتسجيل)

        Returns:
            dict: Configuration as dictionary with secrets masked
        """
        return {
            "mcp_url": self.mcp_url,
            "transport": self.transport.value,
            "environment": self.environment.value,
            "tenant_id": self.tenant_id,
            "app_id": self.app_id[:8] + "..." if self.app_id else None,
            "api_key": "***" if self.api_key else None,
            "connect_timeout": self.connect_timeout,
            "read_timeout": self.read_timeout,
            "default_language": self.default_language,
            "agent_model": self.agent_model.value,
            "enable_auto_reply": self.enable_auto_reply,
            "enable_message_summary": self.enable_message_summary,
            "farm_context_enabled": self.farm_context_enabled,
            "version": self.version,
        }


# Singleton config instance
_config_instance: WeChatConfig | None = None


def get_wechat_config() -> WeChatConfig:
    """
    Get WeChat configuration singleton.
    الحصول على تكوين WeChat المفرد

    Returns:
        WeChatConfig: Configuration instance
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = WeChatConfig.from_env()
    return _config_instance


def reset_config() -> None:
    """
    Reset configuration singleton (for testing).
    إعادة تعيين تكوين المفرد (للاختبار)
    """
    global _config_instance
    _config_instance = None
