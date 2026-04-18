"""
SAHOOL Unified Library Versions
إصدارات المكتبات الموحدة لمنصة سهول

هذا الملف يحتوي على جميع إصدارات المكتبات المستخدمة في الخدمات
يجب أن تستخدم جميع الخدمات هذه الإصدارات لضمان التوافقية

NOTE: The single source of truth for service ports is the TypeScript contracts at
packages/shared-types/src/contracts/service-ports.ts. This Python mirror must stay
in sync with that file.

Updated: February 2026
"""

# =============================================================================
# Core Framework Versions - إصدارات الإطار الأساسي
# Kept in sync with pyproject.toml [project.optional-dependencies]
# =============================================================================

VERSIONS = {
    # Web Framework
    "fastapi": "0.128.5",
    "uvicorn": "0.40.0",  # uvicorn[standard]
    "pydantic": "2.10.0",
    # HTTP Clients
    "httpx": "0.28.1",
    "aiohttp": "3.13.3",  # Security fixes for CVE-2025-53643 and CVE-2025-69223
    # Database - PostgreSQL
    "asyncpg": "0.31.0",
    # Database - Tortoise ORM
    "tortoise-orm": "0.25.4",
    "aerich": "0.9.2",
    # Messaging
    "nats-py": "2.13.1",
    # Authentication & Security
    "passlib": "1.7.4",
    # NOTE: python-jose was removed — no active code in apps/services/ or
    # shared/ imports ``jose``. Services standardize on PyJWT. If a new
    # service needs JWT support, add PyJWT here rather than reintroducing
    # python-jose (deprecated upstream, CVE history).
    # Image Processing
    "pillow": "11.3.0",
    # AI/ML
    "tensorflow-cpu": "2.20.0",
    # Observability
    "prometheus-client": "0.24.1",
    "opentelemetry-api": "1.39.1",
    "opentelemetry-sdk": "1.39.1",
    "opentelemetry-instrumentation-fastapi": "0.60b1",
    "structlog": "24.4.0",
    # Utilities
    "python-dotenv": "1.2.1",
    # Testing
    "pytest": "8.4.2",
    "pytest-asyncio": "0.26.0",
}

# =============================================================================
# Service Ports - منافذ الخدمات
# Mirror of packages/shared-types/src/contracts/service-ports.ts (v16.0.0)
# =============================================================================

SERVICE_PORTS = {
    # ── Core Services ────────────────────────────────────────────────────
    "field-management-service": 3000,
    "user-service": 3025,
    "marketplace-service": 3010,
    "research-core": 3015,
    "disaster-assessment": 3020,
    # ── Intelligence Layer ───────────────────────────────────────────────
    "vegetation-analysis-service": 8090,
    "indicators-service": 8091,
    "weather-service": 8092,
    "advisory-service": 8093,
    "irrigation-smart": 8094,
    "crop-intelligence-service": 8095,
    "ndvi-processor": 8118,
    "virtual-sensors": 8119,
    "field-intelligence": 8120,
    "skills-service": 8121,
    "lai-estimation": 3022,
    "crop-growth-model": 3023,
    # ── Decision Layer ───────────────────────────────────────────────────
    "yield-prediction-service": 8152,
    "agro-rules": 8151,
    # ── Business Layer ───────────────────────────────────────────────────
    "task-service": 8103,
    "equipment-service": 8101,
    "notification-service": 8110,
    "alert-service": 8113,
    "audit-service": 8114,
    "billing-core": 8089,
    "provider-config": 8104,
    "inventory-service": 8116,
    # ── Communication ────────────────────────────────────────────────────
    "ws-gateway": 8081,
    "chat-service": 8115,
    # ── IoT & Sensors ────────────────────────────────────────────────────
    "iot-service": 8117,
    "iot-gateway": 8106,
    "iot-sensor-hub": 8251,
    # ── AI & Agents ──────────────────────────────────────────────────────
    "copilot-api": 8088,
    "ai-advisor": 8112,
    "ai-agents-core": 8161,
    "ai-agents-service": 8130,
    "ai-chat-assistant": 8260,
    "agent-registry": 8160,
    "llm-orchestrator-service": 8164,
    "knowledge-graph": 8140,
    "code-fix-agent": 8162,
    "code-review-agent": 8145,
    "code-review-service": 8102,
    # ── Vision & Terrain ─────────────────────────────────────────────────
    "yolo26-vision-service": 8150,
    "ground-vision-service": 8182,
    "terrain-core-service": 8185,
    "hydrology-service": 8165,
    "leveling-optimizer-service": 8170,
    "edge-orchestrator-service": 8180,
    # ── Agriculture Domain ───────────────────────────────────────────────
    "soil-analysis-service": 8134,
    "pest-detection-service": 8125,
    "drone-service": 8126,
    "cooperative-service": 8127,
    "globalgap-compliance": 8128,
    "traceability-service": 8123,
    "crm-service": 8131,
    "astronomical-calendar": 8111,
    # ── Specialized ──────────────────────────────────────────────────────
    "logistics-service": 8167,
    "supply-chain-service": 8230,
    "lowcode-engine": 8132,
    "wechat-service": 8133,
    "whatsapp-bot-service": 8240,
    "ussd-gateway": 8183,
    "fertigation-engine": 8252,
    "irrigation-cycle-engine": 8250,
    "digital-twin-engine": 8253,
    "mcp-server": 8201,
    "demo-data": 8261,
}

# =============================================================================
# Base Requirements Generation
# =============================================================================


def generate_base_requirements() -> str:
    """Generate base requirements.txt content"""
    lines = [
        "# SAHOOL Base Requirements - Auto-generated",
        "# إصدارات المكتبات الأساسية الموحدة",
        "# DO NOT EDIT MANUALLY - Use versions.py",
        "",
        "# Web Framework",
        f"fastapi=={VERSIONS['fastapi']}",
        f"uvicorn[standard]=={VERSIONS['uvicorn']}",
        f"pydantic=={VERSIONS['pydantic']}",
        "",
        "# HTTP Client",
        f"httpx=={VERSIONS['httpx']}",
        "",
        "# Utilities",
        f"python-dotenv=={VERSIONS['python-dotenv']}",
        "",
    ]
    return "\n".join(lines)


def generate_database_requirements() -> str:
    """Generate database requirements"""
    lines = [
        "# Database Requirements",
        f"asyncpg=={VERSIONS['asyncpg']}",
        f"tortoise-orm=={VERSIONS['tortoise-orm']}",
        f"aerich=={VERSIONS['aerich']}",
    ]
    return "\n".join(lines)


def generate_auth_requirements() -> str:
    """Generate authentication requirements.

    python-jose was removed from VERSIONS — services should use PyJWT.
    This helper now only emits passlib; callers that previously depended
    on python-jose need to migrate to PyJWT explicitly.
    """
    lines = [
        "# Authentication Requirements",
        f"passlib[bcrypt]=={VERSIONS['passlib']}",
    ]
    return "\n".join(lines)


def get_service_url(service_name: str, host: str = "localhost") -> str:
    """Get the URL for a service"""
    port = SERVICE_PORTS.get(service_name)
    if port:
        return f"http://{host}:{port}"
    raise ValueError(f"Unknown service: {service_name}")


def get_all_service_urls(host: str = "localhost") -> dict:
    """Get URLs for all services"""
    return {name: f"http://{host}:{port}" for name, port in SERVICE_PORTS.items()}
