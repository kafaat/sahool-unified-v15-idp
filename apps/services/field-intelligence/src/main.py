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
from datetime import UTC, datetime
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

try:
    from config.cors_config import setup_cors_middleware
except ImportError:
    # Fallback إذا لم يكن الموديول متاح
    def setup_cors_middleware(app):
        pass


try:
    from shared.errors_py import add_request_id_middleware, setup_exception_handlers
except ImportError:
    # Fallback إذا لم يكن الموديول متاح
    def setup_exception_handlers(app):
        pass

    def add_request_id_middleware(app):
        pass


from .api.routes import router
from .services.event_processor import EventProcessor
from .services.rules_engine import RulesEngine

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

    # تهيئة اتصال قاعدة البيانات (PostgreSQL)
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        try:
            import asyncpg

            app.state.db_pool = await asyncpg.create_pool(db_url, min_size=2, max_size=10)
            app.state.db_connected = True
            logger.info("✓ Database connected")
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

    # تحميل القواعد النشطة من قاعدة البيانات
    if app.state.db_connected and app.state.db_pool:
        try:
            async with app.state.db_pool.acquire() as conn:
                # Load count of active rules from database
                result = await conn.fetchval(
                    "SELECT COUNT(*) FROM rules WHERE status = 'active'"
                )
                app.state.rules_loaded = result or 0
                logger.info(f"✓ Loaded {app.state.rules_loaded} active rules from database")
        except Exception as e:
            logger.warning(f"Failed to load rules from database: {e}")
            app.state.rules_loaded = 0

    logger.info("✓ Field Intelligence Service ready on port 8119")
    logger.info("✓ Rules Engine initialized")
    logger.info("✓ Event Processor initialized")

    yield

    # التنظيف عند الإيقاف
    logger.info("Shutting down Field Intelligence Service...")

    # إغلاق الاتصالات
    await event_processor.close()

    # Close database connection
    if hasattr(app.state, "db_pool") and app.state.db_pool:
        await app.state.db_pool.close()
        logger.info("✓ Database connection closed")

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
        "port": 8119,
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
        """
        from uuid import uuid4

        from .api.routes import rules_db
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

        demo_rules = []

        # قاعدة 1: إنشاء مهمة فحص عند انخفاض NDVI
        rule1 = Rule(
            rule_id=str(uuid4()),
            tenant_id="demo_tenant",
            name="NDVI Drop - Create Inspection Task",
            name_ar="انخفاض NDVI - إنشاء مهمة فحص",
            description="Create field inspection task when NDVI drops significantly",
            description_ar="إنشاء مهمة فحص الحقل عند انخفاض NDVI بشكل كبير",
            status=RuleStatus.ACTIVE,
            field_ids=[],  # ينطبق على جميع الحقول
            event_types=["ndvi_drop", "ndvi_anomaly"],
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.drop_percentage",
                        operator=ConditionOperator.GREATER_THAN,
                        value=15.0,
                        value_type="number",
                    ),
                    RuleCondition(
                        field="severity",
                        operator=ConditionOperator.IN,
                        value=["high", "critical"],
                        value_type="list",
                    ),
                ],
            ),
            actions=[
                ActionConfig(
                    action_type=ActionType.CREATE_TASK,
                    enabled=True,
                    task_config=TaskConfig(
                        title="Field Inspection Required",
                        title_ar="مطلوب فحص الحقل",
                        description="NDVI drop detected. Inspect field for issues.",
                        description_ar="تم اكتشاف انخفاض في NDVI. فحص الحقل للمشاكل.",
                        task_type="scouting",
                        priority="high",
                        due_hours=24,
                    ),
                ),
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push", "sms"],
                        recipients=["field_owner"],
                        title="NDVI Alert",
                        title_ar="تنبيه NDVI",
                        message="NDVI drop detected in your field. Immediate inspection recommended.",
                        message_ar="تم اكتشاف انخفاض في NDVI في حقلك. يوصى بالفحص الفوري.",
                        priority="high",
                    ),
                ),
            ],
            cooldown_minutes=120,
            priority=10,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # قاعدة 2: إشعار الطقس القاسي
        rule2 = Rule(
            rule_id=str(uuid4()),
            tenant_id="demo_tenant",
            name="Severe Weather - Notification",
            name_ar="طقس قاسي - إشعار",
            description="Send urgent notification for severe weather alerts",
            description_ar="إرسال إشعار عاجل لتنبيهات الطقس القاسي",
            status=RuleStatus.ACTIVE,
            field_ids=[],
            event_types=["weather_alert"],
            conditions=RuleConditionGroup(
                logic="OR",
                conditions=[
                    RuleCondition(
                        field="metadata.alert_type",
                        operator=ConditionOperator.IN,
                        value=["frost", "heatwave", "storm"],
                        value_type="list",
                    ),
                    RuleCondition(
                        field="severity",
                        operator=ConditionOperator.EQUALS,
                        value="critical",
                        value_type="string",
                    ),
                ],
            ),
            actions=[
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push", "sms", "whatsapp"],
                        recipients=["field_owner"],
                        title="Severe Weather Alert",
                        title_ar="تنبيه طقس قاسي",
                        message="Severe weather conditions expected. Take protective measures.",
                        message_ar="ظروف طقس قاسية متوقعة. اتخذ التدابير الوقائية.",
                        priority="urgent",
                    ),
                ),
            ],
            cooldown_minutes=60,
            priority=5,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        # قاعدة 3: رطوبة منخفضة - مهمة ري
        rule3 = Rule(
            rule_id=str(uuid4()),
            tenant_id="demo_tenant",
            name="Low Soil Moisture - Irrigation Task",
            name_ar="رطوبة منخفضة - مهمة ري",
            description="Create irrigation task when soil moisture is low",
            description_ar="إنشاء مهمة ري عند انخفاض رطوبة التربة",
            status=RuleStatus.ACTIVE,
            field_ids=[],
            event_types=["soil_moisture_low"],
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.current_moisture_percent",
                        operator=ConditionOperator.LESS_THAN,
                        value=30.0,
                        value_type="number",
                    ),
                ],
            ),
            actions=[
                ActionConfig(
                    action_type=ActionType.CREATE_TASK,
                    enabled=True,
                    task_config=TaskConfig(
                        title="Irrigation Required",
                        title_ar="ري مطلوب",
                        description="Soil moisture is low. Irrigate the field.",
                        description_ar="رطوبة التربة منخفضة. قم بري الحقل.",
                        task_type="irrigation",
                        priority="medium",
                        due_hours=12,
                    ),
                ),
            ],
            cooldown_minutes=240,  # 4 ساعات
            priority=20,
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )

        demo_rules = [rule1, rule2, rule3]

        # حفظ القواعد
        for rule in demo_rules:
            rules_db[rule.rule_id] = rule

        logger.info(f"✓ تم بذر {len(demo_rules)} قاعدة تجريبية")

        return {
            "status": "success",
            "message": "Demo rules created",
            "rules_created": len(demo_rules),
            "rule_ids": [r.rule_id for r in demo_rules],
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
