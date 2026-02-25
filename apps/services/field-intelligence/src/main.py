"""
SAHOOL Field Intelligence Service - Main API
خدمة ذكاء الحقول والقواعد الآلية
Port: 8120
Version: 16.0.0

Features:
- محرك القواعد للأتمتة الحقلية (Rules Engine for Field Automation)
- معالجة الأحداث (Event Processing: NDVI, Weather, Soil Moisture)
- إنشاء المهام التلقائية (Auto Task Creation)
- تفعيل الإشعارات (Notification Triggers)
- التكامل مع التقويم الفلكي (Astronomical Calendar Integration)
"""

import logging
import os
import sys
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timezone
from pathlib import Path as PathLib

from fastapi import FastAPI

# Shared middleware imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))


# Add path to shared modules
# في Docker، shared موجود في /app/shared
SHARED_PATH = PathLib("/app/shared")
if not SHARED_PATH.exists():
    # Fallback للتطوير المحلي
    SHARED_PATH = PathLib(__file__).parent.parent.parent / "shared"
if str(SHARED_PATH) not in sys.path:
    sys.path.insert(0, str(SHARED_PATH))

_logger = logging.getLogger(__name__)

try:
    from config.cors_config import setup_cors_middleware
except ImportError:
    _logger.warning("config.cors_config not available, CORS setup will be skipped")

    def setup_cors_middleware(app):
        _logger.debug("CORS middleware not configured (module unavailable)")


try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers
except ImportError:
    _logger.warning("shared.errors_py not available, using default error handling")

    def setup_exception_handlers(app):
        _logger.debug("Exception handlers not configured (module unavailable)")

    def add_request_id_middleware(app):
        _logger.debug("Request ID middleware not configured (module unavailable)")


from shared.middleware.tenant_context import TenantContextMiddleware


from shared.middleware.tenant_context import TenantContextMiddleware


# Security headers middleware
try:
    from shared.middleware.security_headers import setup_security_headers

    SECURITY_HEADERS_AVAILABLE = True
except ImportError:
    SECURITY_HEADERS_AVAILABLE = False
    _logger.warning("shared.middleware.security_headers not available")

    def setup_security_headers(app):
        _logger.debug("Security headers not configured (module unavailable)")


from .api.routes import router
from .services.event_processor import EventProcessor
from .services.rules_engine import RulesEngine

# Database module
try:
    from .database import close_pool, rules_repo
    from .database import init_db as init_database

    DB_MODULE_AVAILABLE = True
except ImportError:
    DB_MODULE_AVAILABLE = False

# ═══════════════════════════════════════════════════════════════════════════════
# Configuration
# الإعدادات
# ═══════════════════════════════════════════════════════════════════════════════

ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# ═══════════════════════════════════════════════════════════════════════════════
# Logging Configuration
# إعداد السجلات
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Lifespan Management
# إدارة دورة حياة التطبيق
# ═══════════════════════════════════════════════════════════════════════════════


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    إدارة دورة حياة التطبيق
    Application Lifespan Management
    """
    logger.info("🚀 Starting Field Intelligence Service...")

    # تهيئة المحركات
    rules_engine = RulesEngine()
    event_processor = EventProcessor(rules_engine)

    app.state.rules_engine = rules_engine
    app.state.event_processor = event_processor

    # Initialize connection status flags
    app.state.db_connected = False
    app.state.nats_connected = False
    app.state.rules_loaded = 0

    # تهيئة اتصال قاعدة البيانات (PostgreSQL) using database module
    if DB_MODULE_AVAILABLE:
        try:
            db_initialized = await init_database()
            if db_initialized:
                app.state.db_connected = True
                logger.info("✓ Database connected and tables initialized")

                # Load count of active rules from database
                try:
                    rules_count = await rules_repo.count_active_rules()
                    app.state.rules_loaded = rules_count
                    logger.info(f"✓ Loaded {app.state.rules_loaded} active rules from database")
                except Exception as e:
                    logger.warning(f"Failed to count rules from database: {e}")
                    app.state.rules_loaded = 0
            else:
                logger.warning("Database not configured - running in memory mode")
        except Exception as e:
            logger.warning(f"Database initialization failed: {e}")
            app.state.db_connected = False
    else:
        # Fallback to direct asyncpg if database module not available
        db_url = os.getenv("DATABASE_URL")
        # Enforce sslmode for non-development database connections
        if db_url and os.getenv("ENVIRONMENT", "development") != "development":
            if "sslmode" not in db_url:
                db_url += "?sslmode=require" if "?" not in db_url else "&sslmode=require"
        if db_url:
            try:
                import asyncpg

                app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
                app.state.db_connected = True
                logger.info("✓ Database connected (legacy mode)")
            except Exception as e:
                logger.warning(f"Database connection failed: {e}")
                app.state.db_pool = None

    # تهيئة NATS للرسائل
    nats_url = os.getenv("NATS_URL")
    if nats_url:
        try:
            import nats

            app.state.nc = await nats.connect(nats_url)
            app.state.nats_connected = True
            logger.info("✓ NATS connected")
        except Exception as e:
            logger.warning(f"NATS connection failed: {e}")
            app.state.nc = None

    logger.info("✓ Field Intelligence Service ready on port 8120")
    logger.info("✓ Rules Engine initialized")
    logger.info("✓ Event Processor initialized")

    yield

    # التنظيف عند الإيقاف
    logger.info("Shutting down Field Intelligence Service...")

    # إغلاق الاتصالات
    await event_processor.close()

    # Close database connection using database module
    if DB_MODULE_AVAILABLE:
        try:
            await close_pool()
            logger.info("✓ Database connection pool closed")
        except Exception as e:
            logger.warning(f"Error closing database pool: {e}")
    elif hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("✓ Database connection closed (legacy mode)")

    # Close NATS connection
    if hasattr(app.state, "nc") and app.state.nc:
        await app.state.nc.close()
        logger.info("✓ NATS connection closed")

    logger.info("✓ Field Intelligence Service stopped")


# ═══════════════════════════════════════════════════════════════════════════════
# FastAPI App
# تطبيق FastAPI
# ═══════════════════════════════════════════════════════════════════════════════

app = FastAPI(
    title="SAHOOL Field Intelligence Service",
    description="""
    خدمة ذكاء الحقول والقواعد الآلية
    Field Intelligence and Automation Rules Service

    **Features:**
    - 🤖 محرك القواعد للأتمتة الحقلية - Rules engine for field automation
    - 📊 معالجة الأحداث - Event processing (NDVI drop, weather alert, soil moisture)
    - ✅ إنشاء المهام التلقائية - Auto task creation from events
    - 🔔 تفعيل الإشعارات - Notification triggers
    - 🌙 التكامل مع التقويم الفلكي - Integration with astronomical calendar

    **Supported Events:**
    - NDVI drop/anomaly detection
    - Weather alerts (frost, heatwave, storm, etc.)
    - Soil moisture (low/high)
    - Temperature extremes
    - Pest/disease detection
    - Irrigation needs
    - Harvest readiness
    - Astronomical events

    **Automation Actions:**
    - Create tasks automatically
    - Send notifications (push, SMS, email, WhatsApp)
    - Create alerts
    - Trigger irrigation systems
    - Call webhooks
    - Log events
    """,
    version="16.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Setup unified error handling
setup_exception_handlers(app)
add_request_id_middleware(app)

# CORS - استخدام الإعداد المركزي الآمن
setup_cors_middleware(app)

# Security headers - رؤوس الأمان
if SECURITY_HEADERS_AVAILABLE:
    setup_security_headers(app)

app.add_middleware(TenantContextMiddleware)

# تضمين المسارات
app.include_router(router, prefix="/api/v1", tags=["Field Intelligence"])


# ═══════════════════════════════════════════════════════════════════════════════
# Health Endpoints
# نقاط فحص الصحة
# ═══════════════════════════════════════════════════════════════════════════════


@app.get("/health", tags=["Health"])
def health():
    """
    فحص صحة الخدمة - Health check
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": "field-intelligence",
        "version": "16.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/healthz", tags=["Health"])
def healthz():
    """
    فحص صحة الخدمة - Kubernetes liveness probe
    Liveness probe for Kubernetes
    """
    return {
        "status": "healthy",
        "service": "field-intelligence",
        "version": "16.0.0",
        "rules_engine": "operational",
        "event_processor": "operational",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@app.get("/readyz", tags=["Health"])
def readiness():
    """
    فحص جاهزية الخدمة - Kubernetes readiness probe
    Readiness probe for Kubernetes
    """
    # Get actual connection status from app.state
    db_connected = getattr(app.state, "db_connected", False)
    nats_connected = getattr(app.state, "nats_connected", False)
    rules_loaded = getattr(app.state, "rules_loaded", 0)

    # Get events processed count from rules engine statistics
    events_processed = 0
    if hasattr(app.state, "rules_engine"):
        stats = app.state.rules_engine.get_statistics()
        events_processed = stats.get("total_evaluations", 0)

    # Determine database status
    if db_connected:
        db_status = "connected"
    elif os.getenv("DATABASE_URL"):
        db_status = "disconnected"
    else:
        db_status = "not_configured"

    # Determine NATS status
    if nats_connected:
        nats_status = "connected"
    elif os.getenv("NATS_URL"):
        nats_status = "disconnected"
    else:
        nats_status = "not_configured"

    # Service is ready if core components are initialized
    # Database and NATS are optional (graceful degradation)
    is_ready = hasattr(app.state, "rules_engine") and hasattr(app.state, "event_processor")

    return {
        "status": "ready" if is_ready else "not_ready",
        "database": db_status,
        "nats": nats_status,
        "rules_loaded": rules_loaded,
        "events_processed": events_processed,
    }


@app.get("/", tags=["Info"])
def root():
    """
    معلومات الخدمة - Service information
    Root endpoint with service information
    """
    return {
        "service": "SAHOOL Field Intelligence Service",
        "service_ar": "خدمة ذكاء الحقول والقواعد الآلية",
        "version": "16.0.0",
        "description": "Intelligent field event processing and automation rules engine",
        "description_ar": "محرك ذكي لمعالجة أحداث الحقول وتنفيذ قواعد الأتمتة",
        "port": 8120,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "features": {
            "rules_engine": "محرك القواعد للأتمتة",
            "event_processing": "معالجة الأحداث (NDVI, Weather, Soil)",
            "auto_tasks": "إنشاء مهام تلقائية",
            "notifications": "إشعارات متعددة القنوات",
            "astronomical": "تكامل مع التقويم الفلكي",
        },
        "endpoints": {
            "events": "/api/v1/events",
            "rules": "/api/v1/rules",
        },
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Demo Data Seeding (للتطوير فقط)
# بذر بيانات تجريبية (Development Only)
# ═══════════════════════════════════════════════════════════════════════════════

# Only register dev endpoint in development/test environments
if ENVIRONMENT in ("development", "dev", "test"):

    @app.post("/dev/seed-demo-rules", tags=["Development"], include_in_schema=False)
    async def seed_demo_rules():
        """
        بذر قواعد تجريبية - Seed demo rules (Development only)
        Creates sample automation rules for testing

        Stores rules in PostgreSQL if available, otherwise in-memory fallback.
        """
        from uuid import uuid4

        from .api.routes import _rules_fallback, is_db_connected
        from .models.rules import (
            ActionConfig,
            ActionType,
            ConditionOperator,
            NotificationConfig,
            Rule,
            RuleCondition,
            RuleConditionGroup,
            RuleStatus,
            TaskConfig,
        )

        demo_rules_data = []

        # قاعدة 1: إنشاء مهمة فحص عند انخفاض NDVI
        rule1_data = {
            "rule_id": str(uuid4()),
            "tenant_id": "demo_tenant",
            "name": "NDVI Drop - Create Inspection Task",
            "name_ar": "انخفاض NDVI - إنشاء مهمة فحص",
            "description": "Create field inspection task when NDVI drops significantly",
            "description_ar": "إنشاء مهمة فحص الحقل عند انخفاض NDVI بشكل كبير",
            "status": "active",
            "field_ids": [],
            "event_types": ["ndvi_drop", "ndvi_anomaly"],
            "conditions": {
                "logic": "AND",
                "conditions": [
                    {
                        "field": "metadata.drop_percentage",
                        "operator": "greater_than",
                        "value": 15.0,
                        "value_type": "number",
                    },
                    {
                        "field": "severity",
                        "operator": "in",
                        "value": ["high", "critical"],
                        "value_type": "list",
                    },
                ],
            },
            "actions": [
                {
                    "action_type": "create_task",
                    "enabled": True,
                    "task_config": {
                        "title": "Field Inspection Required",
                        "title_ar": "مطلوب فحص الحقل",
                        "description": "NDVI drop detected. Inspect field for issues.",
                        "description_ar": "تم اكتشاف انخفاض في NDVI. فحص الحقل للمشاكل.",
                        "task_type": "scouting",
                        "priority": "high",
                        "due_hours": 24,
                    },
                },
                {
                    "action_type": "send_notification",
                    "enabled": True,
                    "notification_config": {
                        "channels": ["push", "sms"],
                        "recipients": ["field_owner"],
                        "title": "NDVI Alert",
                        "title_ar": "تنبيه NDVI",
                        "message": "NDVI drop detected in your field. Immediate inspection recommended.",
                        "message_ar": "تم اكتشاف انخفاض في NDVI في حقلك. يوصى بالفحص الفوري.",
                        "priority": "high",
                    },
                },
            ],
            "cooldown_minutes": 120,
            "priority": 10,
            "metadata": {},
        }

        # قاعدة 2: إشعار الطقس القاسي
        rule2_data = {
            "rule_id": str(uuid4()),
            "tenant_id": "demo_tenant",
            "name": "Severe Weather - Notification",
            "name_ar": "طقس قاسي - إشعار",
            "description": "Send urgent notification for severe weather alerts",
            "description_ar": "إرسال إشعار عاجل لتنبيهات الطقس القاسي",
            "status": "active",
            "field_ids": [],
            "event_types": ["weather_alert"],
            "conditions": {
                "logic": "OR",
                "conditions": [
                    {
                        "field": "metadata.alert_type",
                        "operator": "in",
                        "value": ["frost", "heatwave", "storm"],
                        "value_type": "list",
                    },
                    {
                        "field": "severity",
                        "operator": "equals",
                        "value": "critical",
                        "value_type": "string",
                    },
                ],
            },
            "actions": [
                {
                    "action_type": "send_notification",
                    "enabled": True,
                    "notification_config": {
                        "channels": ["push", "sms", "whatsapp"],
                        "recipients": ["field_owner"],
                        "title": "Severe Weather Alert",
                        "title_ar": "تنبيه طقس قاسي",
                        "message": "Severe weather conditions expected. Take protective measures.",
                        "message_ar": "ظروف طقس قاسية متوقعة. اتخذ التدابير الوقائية.",
                        "priority": "urgent",
                    },
                },
            ],
            "cooldown_minutes": 60,
            "priority": 5,
            "metadata": {},
        }

        # قاعدة 3: رطوبة منخفضة - مهمة ري
        rule3_data = {
            "rule_id": str(uuid4()),
            "tenant_id": "demo_tenant",
            "name": "Low Soil Moisture - Irrigation Task",
            "name_ar": "رطوبة منخفضة - مهمة ري",
            "description": "Create irrigation task when soil moisture is low",
            "description_ar": "إنشاء مهمة ري عند انخفاض رطوبة التربة",
            "status": "active",
            "field_ids": [],
            "event_types": ["soil_moisture_low"],
            "conditions": {
                "logic": "AND",
                "conditions": [
                    {
                        "field": "metadata.current_moisture_percent",
                        "operator": "less_than",
                        "value": 30.0,
                        "value_type": "number",
                    },
                ],
            },
            "actions": [
                {
                    "action_type": "create_task",
                    "enabled": True,
                    "task_config": {
                        "title": "Irrigation Required",
                        "title_ar": "ري مطلوب",
                        "description": "Soil moisture is low. Irrigate the field.",
                        "description_ar": "رطوبة التربة منخفضة. قم بري الحقل.",
                        "task_type": "irrigation",
                        "priority": "medium",
                        "due_hours": 12,
                    },
                },
            ],
            "cooldown_minutes": 240,
            "priority": 20,
            "metadata": {},
        }

        demo_rules_data = [rule1_data, rule2_data, rule3_data]
        created_rule_ids = []

        # Check if database is available
        db_connected = await is_db_connected()

        if db_connected and DB_MODULE_AVAILABLE:
            # حفظ القواعد في PostgreSQL
            for rule_data in demo_rules_data:
                try:
                    result = await rules_repo.create(**rule_data)
                    if result:
                        created_rule_ids.append(rule_data["rule_id"])
                except Exception as e:
                    logger.warning(f"Failed to create rule {rule_data['rule_id']}: {e}")

            logger.info(f"✓ تم بذر {len(created_rule_ids)} قاعدة تجريبية في PostgreSQL")
        else:
            # حفظ القواعد في الذاكرة (fallback)
            for rule_data in demo_rules_data:
                rule = Rule(
                    rule_id=rule_data["rule_id"],
                    tenant_id=rule_data["tenant_id"],
                    name=rule_data["name"],
                    name_ar=rule_data["name_ar"],
                    description=rule_data["description"],
                    description_ar=rule_data["description_ar"],
                    status=RuleStatus.ACTIVE,
                    field_ids=rule_data["field_ids"],
                    event_types=rule_data["event_types"],
                    conditions=RuleConditionGroup(**rule_data["conditions"]),
                    actions=[ActionConfig(**a) for a in rule_data["actions"]],
                    cooldown_minutes=rule_data["cooldown_minutes"],
                    priority=rule_data["priority"],
                    created_at=datetime.now(UTC),
                    updated_at=datetime.now(UTC),
                    metadata=rule_data["metadata"],
                )
                _rules_fallback[rule.rule_id] = rule
                created_rule_ids.append(rule.rule_id)

            logger.info(f"✓ تم بذر {len(created_rule_ids)} قاعدة تجريبية في الذاكرة")

        return {
            "status": "success",
            "message": "Demo rules created",
            "storage": "postgresql" if db_connected and DB_MODULE_AVAILABLE else "memory",
            "rules_created": len(created_rule_ids),
            "rule_ids": created_rule_ids,
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Main Entry Point
# نقطة الدخول الرئيسية
# ═══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8120))
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=port,
        reload=True,  # للتطوير فقط
        log_level="info",
    )
