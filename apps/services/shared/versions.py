"""
SAHOOL Unified Library Versions
إصدارات المكتبات الموحدة لمنصة سهول

هذا الملف يحتوي على جميع إصدارات المكتبات المستخدمة في الخدمات
يجب أن تستخدم جميع الخدمات هذه الإصدارات لضمان التوافقية

Updated: December 2025
"""

# =============================================================================
# Core Framework Versions - إصدارات الإطار الأساسي
# =============================================================================

VERSIONS = {
    # Web Framework
    "fastapi": "0.126.0",
    "uvicorn": "0.27.0",  # uvicorn[standard]
    "pydantic": "2.9.2",
    "starlette": "0.41.3",  # Included with FastAPI

    # HTTP Clients
    "httpx": "0.28.1",
    "aiohttp": "3.11.12",  # Security fix for CVE-2025-53643

    # Database - PostgreSQL
    "sqlalchemy": "2.0.36",
    "psycopg2-binary": "2.9.10",
    "asyncpg": "0.30.0",
    "alembic": "1.14.0",
    "greenlet": "3.1.1",

    # Database - Tortoise ORM (legacy support)
    "tortoise-orm": "0.21.7",
    "aerich": "0.7.2",

    # Messaging
    "nats-py": "2.9.0",
    "redis": "5.2.1",

    # Authentication & Security
    "pyjwt": "2.10.1",
    "bcrypt": "4.2.1",
    "passlib": "1.7.4",
    "python-jose": "3.3.0",  # Legacy, prefer PyJWT

    # Validation
    "jsonschema": "4.23.0",

    # Image Processing
    "pillow": "11.0.0",
    "numpy": "1.26.4",  # <2.1.0 for TensorFlow compatibility

    # AI/ML
    "tensorflow-cpu": "2.18.0",

    # Firebase
    "firebase-admin": "6.6.0",

    # Scheduling
    "apscheduler": "3.10.4",

    # Payment
    "stripe": "7.0.0",

    # Date/Time
    "python-dateutil": "2.9.0",

    # Observability
    "prometheus-client": "0.21.1",
    "opentelemetry-api": "1.29.0",
    "opentelemetry-sdk": "1.29.0",
    "opentelemetry-instrumentation-fastapi": "0.50b0",
    "structlog": "24.4.0",

    # Utilities
    "python-dotenv": "1.0.1",
    "python-multipart": "0.0.18",

    # Testing
    "pytest": "8.3.4",
    "pytest-asyncio": "0.24.0",
}

# =============================================================================
# Service Ports - منافذ الخدمات
# =============================================================================

SERVICE_PORTS = {
    "billing-core": 8089,
    "satellite-service": 8090,
    "indicators-service": 8091,
    "weather-advanced": 8092,
    "fertilizer-advisor": 8093,
    "irrigation-smart": 8094,
    "crop-health-ai": 8095,
    "virtual-sensors": 8096,
    "yield-engine": 8098,
    "notification-service": 8109,
    "astronomical-calendar": 8111,
}

# =============================================================================
# Service Versions - إصدارات الخدمات
# =============================================================================

SERVICE_VERSIONS = {
    "billing-core": "15.4.0",
    "satellite-service": "15.3.0",
    "indicators-service": "15.3.0",
    "weather-advanced": "15.4.0",
    "fertilizer-advisor": "15.3.0",
    "irrigation-smart": "15.3.0",
    "crop-health-ai": "15.3.0",
    "virtual-sensors": "15.3.0",
    "yield-engine": "15.3.0",
    "notification-service": "15.3.0",
    "astronomical-calendar": "15.3.0",
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
        f"sqlalchemy=={VERSIONS['sqlalchemy']}",
        f"psycopg2-binary=={VERSIONS['psycopg2-binary']}",
        f"asyncpg=={VERSIONS['asyncpg']}",
        f"alembic=={VERSIONS['alembic']}",
        f"greenlet=={VERSIONS['greenlet']}",
    ]
    return "\n".join(lines)


def generate_auth_requirements() -> str:
    """Generate authentication requirements"""
    lines = [
        "# Authentication Requirements",
        f"PyJWT=={VERSIONS['pyjwt']}",
        f"bcrypt=={VERSIONS['bcrypt']}",
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
    return {
        name: f"http://{host}:{port}"
        for name, port in SERVICE_PORTS.items()
    }
