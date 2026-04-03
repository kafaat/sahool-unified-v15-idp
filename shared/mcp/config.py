"""
SAHOOL MCP Configuration - Model Context Protocol Configuration
================================================================

Provides centralized configuration for SAHOOL MCP server and client.
Supports environment-based configuration with sensible defaults.

Configuration includes:
- Server settings (host, port, transport)
- API endpoints for SAHOOL services
- Rate limiting and timeouts
- Authentication settings
- Agent configuration
- Bilingual settings (Arabic/English)

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TransportType(Enum):
    """Supported MCP transport types"""

    STDIO = "stdio"
    HTTP = "http"
    SSE = "sse"
    WEBSOCKET = "websocket"


class Language(Enum):
    """Supported languages for bilingual output"""

    ENGLISH = "en"
    ARABIC = "ar"
    BOTH = "both"


class AgentType(Enum):
    """Types of AI agents that can be spawned"""

    CROP_ADVISOR = "crop_advisor"
    IRRIGATION_SPECIALIST = "irrigation_specialist"
    PEST_MANAGEMENT = "pest_management"
    SOIL_ANALYST = "soil_analyst"
    WEATHER_ANALYST = "weather_analyst"
    FARM_PLANNER = "farm_planner"
    GENERAL_ASSISTANT = "general_assistant"


class RateLimitTier(Enum):
    """Rate limiting tiers"""

    FREE = "free"
    STANDARD = "standard"
    PREMIUM = "premium"
    INTERNAL = "internal"


# Rate limit configurations (requests per minute)
RATE_LIMITS: dict[RateLimitTier, dict[str, int]] = {
    RateLimitTier.FREE: {"per_minute": 30, "per_hour": 500},
    RateLimitTier.STANDARD: {"per_minute": 60, "per_hour": 2000},
    RateLimitTier.PREMIUM: {"per_minute": 120, "per_hour": 5000},
    RateLimitTier.INTERNAL: {"per_minute": 1000, "per_hour": 50000},
}


@dataclass
class ServerConfig:
    """
    MCP Server Configuration

    Attributes:
        name: Server name for identification
        version: Server version string
        host: Host to bind for HTTP/SSE transport
        port: Port to bind for HTTP/SSE transport
        transport: Transport type (stdio, http, sse)
        debug: Enable debug logging
        cors_origins: Allowed CORS origins
    """

    name: str = "sahool-mcp-server"
    name_ar: str = "خادم سهول MCP"
    version: str = "1.0.0"
    host: str = field(default_factory=lambda: os.getenv("MCP_HOST", "0.0.0.0"))  # nosec B104 - default for containerized deployment, overridden by env
    port: int = field(default_factory=lambda: int(os.getenv("MCP_PORT", "8200")))
    transport: TransportType = field(default_factory=lambda: TransportType(os.getenv("MCP_TRANSPORT", "http")))
    debug: bool = field(default_factory=lambda: os.getenv("MCP_DEBUG", "false").lower() == "true")
    cors_origins: list[str] = field(
        default_factory=lambda: os.getenv("MCP_CORS_ORIGINS", "http://localhost:3000,http://localhost:8200").split(",")
    )
    protocol_version: str = "2024-11-05"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "version": self.version,
            "host": self.host,
            "port": self.port,
            "transport": self.transport.value,
            "debug": self.debug,
            "cors_origins": self.cors_origins,
            "protocol_version": self.protocol_version,
        }


@dataclass
class APIConfig:
    """
    SAHOOL API Configuration

    Configures endpoints for various SAHOOL services that MCP tools connect to.
    """

    base_url: str = field(default_factory=lambda: os.getenv("SAHOOL_API_URL", "http://localhost:8000"))

    # Service URLs
    field_service_url: str = field(
        default_factory=lambda: os.getenv("FIELD_SERVICE_URL", "http://field-management-service:3000")
    )
    weather_service_url: str = field(
        default_factory=lambda: os.getenv("WEATHER_SERVICE_URL", "http://weather-service:8092")
    )
    crop_intelligence_url: str = field(
        default_factory=lambda: os.getenv("CROP_INTELLIGENCE_URL", "http://crop-intelligence-service:8095")
    )
    irrigation_service_url: str = field(
        default_factory=lambda: os.getenv("IRRIGATION_SERVICE_URL", "http://irrigation-smart:8094")
    )
    advisory_service_url: str = field(
        default_factory=lambda: os.getenv("ADVISORY_SERVICE_URL", "http://advisory-service:8093")
    )
    user_service_url: str = field(default_factory=lambda: os.getenv("USER_SERVICE_URL", "http://user-service:3025"))
    notification_service_url: str = field(
        default_factory=lambda: os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8110")
    )

    # Timeouts (seconds)
    default_timeout: float = field(default_factory=lambda: float(os.getenv("MCP_DEFAULT_TIMEOUT", "30")))
    long_timeout: float = field(default_factory=lambda: float(os.getenv("MCP_LONG_TIMEOUT", "120")))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "base_url": self.base_url,
            "field_service_url": self.field_service_url,
            "weather_service_url": self.weather_service_url,
            "crop_intelligence_url": self.crop_intelligence_url,
            "irrigation_service_url": self.irrigation_service_url,
            "advisory_service_url": self.advisory_service_url,
            "user_service_url": self.user_service_url,
            "notification_service_url": self.notification_service_url,
            "default_timeout": self.default_timeout,
            "long_timeout": self.long_timeout,
        }


@dataclass
class AuthConfig:
    """
    Authentication Configuration

    Settings for JWT authentication and API key validation.
    """

    jwt_secret_key: str = field(
        default_factory=lambda: os.getenv("JWT_SECRET_KEY", "")
    )  # Empty = auth rejects all tokens; MUST be set for production
    jwt_algorithm: str = field(default_factory=lambda: os.getenv("JWT_ALGORITHM", "HS256"))
    jwt_expiry_minutes: int = field(default_factory=lambda: int(os.getenv("JWT_EXPIRY_MINUTES", "60")))
    api_key_header: str = "X-API-Key"
    bearer_header: str = "Authorization"

    # Rate limiting
    rate_limit_tier: RateLimitTier = field(
        default_factory=lambda: RateLimitTier(os.getenv("MCP_RATE_LIMIT_TIER", "standard"))
    )

    @property
    def rate_limits(self) -> dict[str, int]:
        """Get rate limits for current tier"""
        return RATE_LIMITS[self.rate_limit_tier]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary (excluding secrets)"""
        return {
            "jwt_algorithm": self.jwt_algorithm,
            "jwt_expiry_minutes": self.jwt_expiry_minutes,
            "api_key_header": self.api_key_header,
            "bearer_header": self.bearer_header,
            "rate_limit_tier": self.rate_limit_tier.value,
            "rate_limits": self.rate_limits,
        }


@dataclass
class AgentConfig:
    """
    AI Agent Configuration

    Settings for spawning and managing AI agents.
    """

    # Agent pool settings
    max_agents: int = field(default_factory=lambda: int(os.getenv("MCP_MAX_AGENTS", "10")))
    agent_timeout_seconds: int = field(default_factory=lambda: int(os.getenv("MCP_AGENT_TIMEOUT", "300")))
    agent_cleanup_interval_seconds: int = field(
        default_factory=lambda: int(os.getenv("MCP_AGENT_CLEANUP_INTERVAL", "60"))
    )

    # Model settings
    default_model: str = field(default_factory=lambda: os.getenv("MCP_DEFAULT_MODEL", "claude-3-sonnet"))
    ollama_url: str = field(default_factory=lambda: os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))
    ollama_model: str = field(default_factory=lambda: os.getenv("OLLAMA_MODEL", "codellama:7b"))

    # Agent types configuration
    available_agent_types: list[AgentType] = field(default_factory=lambda: list(AgentType))

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "max_agents": self.max_agents,
            "agent_timeout_seconds": self.agent_timeout_seconds,
            "agent_cleanup_interval_seconds": self.agent_cleanup_interval_seconds,
            "default_model": self.default_model,
            "ollama_url": self.ollama_url,
            "ollama_model": self.ollama_model,
            "available_agent_types": [at.value for at in self.available_agent_types],
        }


@dataclass
class BilingualConfig:
    """
    Bilingual Configuration

    Settings for Arabic/English bilingual support.
    """

    default_language: Language = field(default_factory=lambda: Language(os.getenv("MCP_DEFAULT_LANGUAGE", "en")))
    include_both_languages: bool = field(default_factory=lambda: os.getenv("MCP_BILINGUAL", "true").lower() == "true")
    arabic_rtl: bool = True  # Always use RTL for Arabic

    # Common translations
    translations: dict[str, dict[str, str]] = field(
        default_factory=lambda: {
            "success": {"en": "Success", "ar": "نجاح"},
            "error": {"en": "Error", "ar": "خطأ"},
            "field": {"en": "Field", "ar": "حقل"},
            "farm": {"en": "Farm", "ar": "مزرعة"},
            "farmer": {"en": "Farmer", "ar": "مزارع"},
            "crop": {"en": "Crop", "ar": "محصول"},
            "weather": {"en": "Weather", "ar": "طقس"},
            "irrigation": {"en": "Irrigation", "ar": "ري"},
            "fertilizer": {"en": "Fertilizer", "ar": "سماد"},
            "recommendation": {"en": "Recommendation", "ar": "توصية"},
            "analysis": {"en": "Analysis", "ar": "تحليل"},
            "health": {"en": "Health", "ar": "صحة"},
            "status": {"en": "Status", "ar": "حالة"},
            "agent": {"en": "Agent", "ar": "وكيل"},
            "advisory": {"en": "Advisory", "ar": "استشارة"},
            "soil": {"en": "Soil", "ar": "تربة"},
            "pest": {"en": "Pest", "ar": "آفة"},
            "disease": {"en": "Disease", "ar": "مرض"},
            "yield": {"en": "Yield", "ar": "محصول"},
            "area": {"en": "Area", "ar": "مساحة"},
            "hectare": {"en": "Hectare", "ar": "هكتار"},
            "date": {"en": "Date", "ar": "تاريخ"},
            "temperature": {"en": "Temperature", "ar": "درجة حرارة"},
            "humidity": {"en": "Humidity", "ar": "رطوبة"},
            "precipitation": {"en": "Precipitation", "ar": "هطول"},
            "wind": {"en": "Wind", "ar": "رياح"},
            "ndvi": {"en": "NDVI (Vegetation Index)", "ar": "مؤشر الغطاء النباتي"},
            "sensor": {"en": "Sensor", "ar": "مستشعر"},
            "history": {"en": "History", "ar": "تاريخ"},
            "action_required": {"en": "Action Required", "ar": "إجراء مطلوب"},
            "warning": {"en": "Warning", "ar": "تحذير"},
            "critical": {"en": "Critical", "ar": "حرج"},
            "normal": {"en": "Normal", "ar": "عادي"},
        }
    )

    def translate(self, key: str, language: Language | None = None) -> str:
        """Get translation for a key"""
        lang = language or self.default_language
        if key in self.translations:
            if lang == Language.BOTH:
                return f"{self.translations[key]['en']} | {self.translations[key]['ar']}"
            return self.translations[key].get(lang.value, key)
        return key

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "default_language": self.default_language.value,
            "include_both_languages": self.include_both_languages,
            "arabic_rtl": self.arabic_rtl,
        }


@dataclass
class MCPConfig:
    """
    Main MCP Configuration

    Aggregates all configuration sections into a single configuration object.

    Usage:
        config = MCPConfig()
        print(config.server.host)
        print(config.api.base_url)
    """

    server: ServerConfig = field(default_factory=ServerConfig)
    api: APIConfig = field(default_factory=APIConfig)
    auth: AuthConfig = field(default_factory=AuthConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    bilingual: BilingualConfig = field(default_factory=BilingualConfig)

    @classmethod
    def from_env(cls) -> MCPConfig:
        """Create configuration from environment variables"""
        return cls(
            server=ServerConfig(),
            api=APIConfig(),
            auth=AuthConfig(),
            agent=AgentConfig(),
            bilingual=BilingualConfig(),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary"""
        return {
            "server": self.server.to_dict(),
            "api": self.api.to_dict(),
            "auth": self.auth.to_dict(),
            "agent": self.agent.to_dict(),
            "bilingual": self.bilingual.to_dict(),
        }

    def validate(self) -> list[str]:
        """
        Validate configuration and return list of warnings/errors

        Returns:
            List of validation messages (empty if valid)
        """
        issues = []

        # Check required settings
        if not self.auth.jwt_secret_key and self.server.transport != TransportType.STDIO:
            issues.append(
                "CRITICAL: JWT_SECRET_KEY not set — all authenticated endpoints will "
                "reject requests. Set JWT_SECRET_KEY env var before production use."
            )

        if self.server.port < 1 or self.server.port > 65535:
            issues.append(f"ERROR: Invalid port number: {self.server.port}")

        if self.agent.max_agents < 1:
            issues.append("ERROR: max_agents must be at least 1")

        if self.api.default_timeout < 1:
            issues.append("WARNING: default_timeout is very low")

        return issues


# ==================== Tool Description Templates ====================


class ToolDescriptions:
    """
    Bilingual tool descriptions for MCP tools

    Provides English and Arabic descriptions for all SAHOOL MCP tools.
    """

    FETCH_FIELD_DATA = {
        "en": "Retrieve comprehensive field data including boundaries, soil properties, "
        "crop information, sensor data, and historical activities.",
        "ar": "استرجاع بيانات الحقل الشاملة بما في ذلك الحدود وخصائص التربة "
        "ومعلومات المحصول وبيانات المستشعرات والأنشطة التاريخية.",
    }

    ANALYZE_CROP_HEALTH = {
        "en": "Analyze crop health using satellite imagery and NDVI analysis. "
        "Identifies stress areas, disease risks, and provides recommendations.",
        "ar": "تحليل صحة المحصول باستخدام صور الأقمار الصناعية وتحليل NDVI. "
        "يحدد مناطق الإجهاد ومخاطر الأمراض ويقدم التوصيات.",
    }

    GET_WEATHER_FORECAST = {
        "en": "Get weather forecast for a specific location. Returns temperature, "
        "humidity, precipitation, wind speed, and agricultural advisories.",
        "ar": "الحصول على توقعات الطقس لموقع محدد. يعرض درجة الحرارة والرطوبة "
        "والهطول وسرعة الرياح والإرشادات الزراعية.",
    }

    IRRIGATION_RECOMMENDATION = {
        "en": "Calculate optimal irrigation requirements based on soil moisture, "
        "weather forecast, crop type, and growth stage.",
        "ar": "حساب متطلبات الري المثلى بناءً على رطوبة التربة وتوقعات الطقس ونوع المحصول ومرحلة النمو.",
    }

    FERTILIZER_RECOMMENDATION = {
        "en": "Get fertilizer recommendations based on soil analysis, crop requirements, "
        "and growth stage. Includes NPK ratios and application schedules.",
        "ar": "الحصول على توصيات الأسمدة بناءً على تحليل التربة ومتطلبات المحصول "
        "ومرحلة النمو. يشمل نسب NPK وجداول التطبيق.",
    }

    GET_FARMER_INFO = {
        "en": "Retrieve farmer profile information including contact details, "
        "farm portfolio, preferences, and interaction history.",
        "ar": "استرجاع معلومات ملف المزارع بما في ذلك بيانات الاتصال ومحفظة المزرعة والتفضيلات وسجل التفاعلات.",
    }

    LOG_INTERACTION = {
        "en": "Log an interaction with a farmer. Records advisory given, "
        "farmer response, and follow-up actions needed.",
        "ar": "تسجيل تفاعل مع مزارع. يسجل الاستشارة المقدمة واستجابة المزارع والإجراءات المطلوبة للمتابعة.",
    }

    GET_RECOMMENDATIONS_HISTORY = {
        "en": "Get history of recommendations given to a farmer, including outcomes and feedback received.",
        "ar": "الحصول على سجل التوصيات المقدمة للمزارع بما في ذلك النتائج والتعليقات المستلمة.",
    }

    SPAWN_AGENT = {
        "en": "Create a specialized AI agent for agricultural tasks. "
        "Agents can be crop advisors, irrigation specialists, pest managers, etc.",
        "ar": "إنشاء وكيل ذكاء اصطناعي متخصص للمهام الزراعية. "
        "يمكن أن يكون الوكلاء مستشاري محاصيل أو متخصصين في الري أو مديري آفات.",
    }

    QUERY_AGENT = {
        "en": "Send a query to a spawned AI agent and receive specialized advice. "
        "Supports context from field data and previous interactions.",
        "ar": "إرسال استفسار إلى وكيل الذكاء الاصطناعي والحصول على نصيحة متخصصة. "
        "يدعم السياق من بيانات الحقل والتفاعلات السابقة.",
    }

    GET_AGENT_STATUS = {
        "en": "Check the status of a spawned AI agent including activity, resource usage, and pending tasks.",
        "ar": "التحقق من حالة وكيل الذكاء الاصطناعي بما في ذلك النشاط واستخدام الموارد والمهام المعلقة.",
    }

    @classmethod
    def get(cls, tool_name: str, language: Language = Language.BOTH) -> str:
        """Get description for a tool in specified language"""
        descriptions = {
            "fetch_field_data": cls.FETCH_FIELD_DATA,
            "analyze_crop_health": cls.ANALYZE_CROP_HEALTH,
            "get_weather_forecast": cls.GET_WEATHER_FORECAST,
            "irrigation_recommendation": cls.IRRIGATION_RECOMMENDATION,
            "fertilizer_recommendation": cls.FERTILIZER_RECOMMENDATION,
            "get_farmer_info": cls.GET_FARMER_INFO,
            "log_interaction": cls.LOG_INTERACTION,
            "get_recommendations_history": cls.GET_RECOMMENDATIONS_HISTORY,
            "spawn_agent": cls.SPAWN_AGENT,
            "query_agent": cls.QUERY_AGENT,
            "get_agent_status": cls.GET_AGENT_STATUS,
        }

        if tool_name not in descriptions:
            return f"No description available for {tool_name}"

        desc = descriptions[tool_name]
        if language == Language.BOTH:
            return f"{desc['en']}\n\n{desc['ar']}"
        return desc.get(language.value, desc["en"])


# ==================== Resource Description Templates ====================


class ResourceDescriptions:
    """
    Bilingual resource descriptions for MCP resources
    """

    FIELD_INFO = {
        "en": "General field information including name, location, area, and current crop",
        "ar": "معلومات الحقل العامة بما في ذلك الاسم والموقع والمساحة والمحصول الحالي",
    }

    FIELD_BOUNDARIES = {
        "en": "Geospatial field boundaries in GeoJSON format",
        "ar": "حدود الحقل الجغرافية المكانية بتنسيق GeoJSON",
    }

    FIELD_SOIL = {
        "en": "Soil properties and test results including NPK, pH, organic matter",
        "ar": "خصائص التربة ونتائج الاختبارات بما في ذلك NPK ودرجة الحموضة والمادة العضوية",
    }

    FIELD_SENSORS = {
        "en": "IoT sensor data from field including soil moisture, temperature",
        "ar": "بيانات مستشعرات إنترنت الأشياء من الحقل بما في ذلك رطوبة التربة ودرجة الحرارة",
    }

    FARMER_PROFILE = {
        "en": "Farmer profile with contact information and preferences",
        "ar": "ملف المزارع مع معلومات الاتصال والتفضيلات",
    }

    FARMER_FARMS = {
        "en": "List of farms owned or managed by the farmer",
        "ar": "قائمة المزارع المملوكة أو المُدارة من قبل المزارع",
    }

    WEATHER_CURRENT = {
        "en": "Current weather conditions for registered locations",
        "ar": "أحوال الطقس الحالية للمواقع المسجلة",
    }

    WEATHER_FORECAST = {
        "en": "Weather forecast for the coming days",
        "ar": "توقعات الطقس للأيام القادمة",
    }

    KNOWLEDGE_CROPS = {
        "en": "Crop growing guides and best practices",
        "ar": "أدلة زراعة المحاصيل وأفضل الممارسات",
    }

    KNOWLEDGE_PESTS = {
        "en": "Pest identification and management guides",
        "ar": "أدلة تحديد الآفات وإدارتها",
    }

    KNOWLEDGE_DISEASES = {
        "en": "Crop disease identification and treatment guides",
        "ar": "أدلة تحديد أمراض المحاصيل وعلاجها",
    }

    @classmethod
    def get(cls, resource_name: str, language: Language = Language.BOTH) -> str:
        """Get description for a resource in specified language"""
        descriptions = {
            "field_info": cls.FIELD_INFO,
            "field_boundaries": cls.FIELD_BOUNDARIES,
            "field_soil": cls.FIELD_SOIL,
            "field_sensors": cls.FIELD_SENSORS,
            "farmer_profile": cls.FARMER_PROFILE,
            "farmer_farms": cls.FARMER_FARMS,
            "weather_current": cls.WEATHER_CURRENT,
            "weather_forecast": cls.WEATHER_FORECAST,
            "knowledge_crops": cls.KNOWLEDGE_CROPS,
            "knowledge_pests": cls.KNOWLEDGE_PESTS,
            "knowledge_diseases": cls.KNOWLEDGE_DISEASES,
        }

        if resource_name not in descriptions:
            return f"No description available for {resource_name}"

        desc = descriptions[resource_name]
        if language == Language.BOTH:
            return f"{desc['en']} | {desc['ar']}"
        return desc.get(language.value, desc["en"])


# ==================== Default Configuration Instance ====================


# Create default configuration from environment
default_config = MCPConfig.from_env()


def get_config() -> MCPConfig:
    """Get the default MCP configuration"""
    return default_config


def reload_config() -> MCPConfig:
    """Reload configuration from environment"""
    global default_config
    default_config = MCPConfig.from_env()
    return default_config


if __name__ == "__main__":
    # Print current configuration
    import json

    config = get_config()
    print("SAHOOL MCP Configuration")
    print("=" * 50)
    print(json.dumps(config.to_dict(), indent=2, ensure_ascii=False))

    # Validate configuration
    issues = config.validate()
    if issues:
        print("\nValidation Issues:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("\nConfiguration is valid.")
