"""
محرك القواعد الذكي للحقول - Field Intelligence Rules Engine
====================================================================

محرك متقدم لتقييم وتنفيذ القواعد الآلية بناءً على أحداث الحقول الزراعية
Advanced rules engine for evaluating and executing automation rules based on field events

الميزات الرئيسية - Key Features:
- قواعد NDVI (مؤشر الغطاء النباتي)
- قواعد الطقس والأمطار
- قواعد رطوبة التربة
- قواعد الأحداث الفلكية الزراعية
- إنشاء وتحديث المهام تلقائياً
- إرسال الإشعارات
- حل التعارضات بين القواعد
- تفعيل/تعطيل القواعد لكل حقل

Author: SAHOOL Platform
License: MIT
"""

import logging
import os
from datetime import UTC, datetime, timedelta, timezone
from typing import Any

import httpx

from ..models.events import EventResponse, EventSeverity, EventType
from ..models.rules import (
    ActionConfig,
    ActionType,
    AlertConfig,
    ConditionOperator,
    NotificationConfig,
    Rule,
    RuleCondition,
    RuleConditionGroup,
    RuleCreate,
    RuleExecutionResult,
    RuleStatus,
    TaskConfig,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════════════════
# Service URLs Configuration - إعدادات عناوين الخدمات
# ═══════════════════════════════════════════════════════════════════════════════

TASK_SERVICE_URL = os.getenv("TASK_SERVICE_URL", "http://task-service:8103")
NOTIFICATION_SERVICE_URL = os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8110")
ALERT_SERVICE_URL = os.getenv("ALERT_SERVICE_URL", "http://alert-service:8113")


# ═══════════════════════════════════════════════════════════════════════════════
# Default Rules Configuration - إعدادات القواعد الافتراضية
# ═══════════════════════════════════════════════════════════════════════════════


def get_default_rules(tenant_id: str) -> list[RuleCreate]:
    """
    الحصول على القواعد الافتراضية للمزرعة
    Get default rules for a farm

    تتضمن قواعد لـ:
    - انخفاض NDVI (صحة النبات)
    - تنبيهات الطقس (أمطار، صقيع، موجات حر)
    - رطوبة التربة (حاجة للري)
    - الأحداث الفلكية (أوقات الزراعة والحصاد)

    Args:
        tenant_id: معرف المزرعة

    Returns:
        قائمة القواعد الافتراضية
    """
    return [
        # ═══════════════════════════════════════════════════════════════════════
        # قاعدة 1: انخفاض حاد في NDVI - Critical NDVI Drop
        # ═══════════════════════════════════════════════════════════════════════
        RuleCreate(
            tenant_id=tenant_id,
            name="Critical NDVI Drop Alert",
            name_ar="تنبيه انخفاض حاد في صحة النبات",
            description="Alert when NDVI drops below 0.3, indicating severe plant stress",
            description_ar="تنبيه عند انخفاض مؤشر NDVI عن 0.3، مما يشير إلى ضغط شديد على النباتات",
            status=RuleStatus.ACTIVE,
            event_types=[EventType.NDVI_DROP.value, EventType.NDVI_ANOMALY.value],
            priority=10,  # أعلى أولوية
            cooldown_minutes=360,  # 6 ساعات بين التنبيهات
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.current_ndvi",
                        operator=ConditionOperator.LESS_THAN,
                        value=0.3,
                        value_type="number",
                    ),
                    RuleCondition(
                        field="severity",
                        operator=ConditionOperator.IN,
                        value=[EventSeverity.HIGH.value, EventSeverity.CRITICAL.value],
                        value_type="list",
                    ),
                ],
            ),
            actions=[
                # إنشاء مهمة عاجلة للفحص الميداني
                ActionConfig(
                    action_type=ActionType.CREATE_TASK,
                    enabled=True,
                    task_config=TaskConfig(
                        title="Urgent Field Inspection Required",
                        title_ar="فحص ميداني عاجل مطلوب",
                        description="NDVI has dropped critically. Immediate inspection needed to identify issues.",
                        description_ar="انخفض مؤشر NDVI بشكل حرج. يلزم فحص فوري لتحديد المشاكل.",
                        task_type="inspection",
                        priority="urgent",
                        assign_to="field_owner",
                        due_hours=4,
                        metadata={
                            "rule_type": "ndvi_critical",
                            "action_required": "immediate_inspection",
                        },
                    ),
                ),
                # إرسال إشعار عاجل
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push", "sms"],
                        recipients=["field_owner"],
                        title="⚠️ Critical Plant Health Alert",
                        title_ar="⚠️ تنبيه حرج لصحة النبات",
                        message="NDVI has dropped to critical levels. Immediate action required.",
                        message_ar="انخفض مؤشر NDVI إلى مستويات حرجة. يلزم اتخاذ إجراء فوري.",
                        priority="urgent",
                    ),
                ),
                # إنشاء تنبيه
                ActionConfig(
                    action_type=ActionType.CREATE_ALERT,
                    enabled=True,
                    alert_config=AlertConfig(
                        alert_type="plant_health",
                        severity="critical",
                        title="Critical NDVI Drop Detected",
                        title_ar="اكتشاف انخفاض حرج في NDVI",
                        message="Plant health index has reached critical levels",
                        message_ar="وصل مؤشر صحة النبات إلى مستويات حرجة",
                        recommendations=[
                            "Inspect field immediately",
                            "Check irrigation system",
                            "Look for pest or disease signs",
                        ],
                        recommendations_ar=[
                            "فحص الحقل فوراً",
                            "التحقق من نظام الري",
                            "البحث عن علامات الآفات أو الأمراض",
                        ],
                        expire_hours=48,
                    ),
                ),
            ],
            metadata={"rule_category": "ndvi", "auto_generated": True},
        ),
        # ═══════════════════════════════════════════════════════════════════════
        # قاعدة 2: انخفاض متوسط في NDVI - Moderate NDVI Drop
        # ═══════════════════════════════════════════════════════════════════════
        RuleCreate(
            tenant_id=tenant_id,
            name="Moderate NDVI Drop Alert",
            name_ar="تنبيه انخفاض متوسط في صحة النبات",
            description="Alert when NDVI is between 0.3 and 0.5",
            description_ar="تنبيه عند انخفاض NDVI بين 0.3 و 0.5",
            status=RuleStatus.ACTIVE,
            event_types=[EventType.NDVI_DROP.value],
            priority=20,
            cooldown_minutes=720,  # 12 ساعة
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.current_ndvi",
                        operator=ConditionOperator.BETWEEN,
                        value=[0.3, 0.5],
                        value_type="list",
                    ),
                ],
            ),
            actions=[
                ActionConfig(
                    action_type=ActionType.CREATE_TASK,
                    enabled=True,
                    task_config=TaskConfig(
                        title="Field Inspection Recommended",
                        title_ar="يُنصح بفحص الحقل",
                        description="NDVI shows moderate decline. Schedule inspection within 24 hours.",
                        description_ar="يظهر NDVI انخفاضاً متوسطاً. حدد موعد فحص خلال 24 ساعة.",
                        task_type="inspection",
                        priority="high",
                        assign_to="field_owner",
                        due_hours=24,
                    ),
                ),
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push"],
                        recipients=["field_owner"],
                        title="Plant Health Declining",
                        title_ar="تراجع صحة النبات",
                        message="NDVI shows moderate decline. Consider inspection.",
                        message_ar="يظهر NDVI انخفاضاً متوسطاً. يُنصح بالفحص.",
                        priority="high",
                    ),
                ),
            ],
            metadata={"rule_category": "ndvi", "auto_generated": True},
        ),
        # ═══════════════════════════════════════════════════════════════════════
        # قاعدة 3: رطوبة تربة منخفضة - Low Soil Moisture
        # ═══════════════════════════════════════════════════════════════════════
        RuleCreate(
            tenant_id=tenant_id,
            name="Low Soil Moisture - Irrigation Needed",
            name_ar="رطوبة تربة منخفضة - حاجة للري",
            description="Alert when soil moisture drops below 30%",
            description_ar="تنبيه عند انخفاض رطوبة التربة عن 30%",
            status=RuleStatus.ACTIVE,
            event_types=[EventType.SOIL_MOISTURE_LOW.value, EventType.IRRIGATION_NEEDED.value],
            priority=15,
            cooldown_minutes=180,  # 3 ساعات
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.current_moisture_percent",
                        operator=ConditionOperator.LESS_THAN,
                        value=30,
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
                        title_ar="الري مطلوب",
                        description="Soil moisture has dropped below optimal levels. Irrigate soon.",
                        description_ar="انخفضت رطوبة التربة دون المستوى الأمثل. الري مطلوب قريباً.",
                        task_type="irrigation",
                        priority="high",
                        assign_to="field_owner",
                        due_hours=6,
                        metadata={"action_type": "irrigation"},
                    ),
                ),
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push", "sms"],
                        recipients=["field_owner"],
                        title="💧 Irrigation Needed",
                        title_ar="💧 الري مطلوب",
                        message="Soil moisture is low. Irrigation recommended within 6 hours.",
                        message_ar="رطوبة التربة منخفضة. يُنصح بالري خلال 6 ساعات.",
                        priority="high",
                    ),
                ),
            ],
            metadata={"rule_category": "soil_moisture", "auto_generated": True},
        ),
        # ═══════════════════════════════════════════════════════════════════════
        # قاعدة 4: رطوبة تربة عالية جداً - High Soil Moisture
        # ═══════════════════════════════════════════════════════════════════════
        RuleCreate(
            tenant_id=tenant_id,
            name="Excessive Soil Moisture Alert",
            name_ar="تنبيه رطوبة تربة مفرطة",
            description="Alert when soil moisture exceeds 80% (risk of root rot)",
            description_ar="تنبيه عند تجاوز رطوبة التربة 80% (خطر تعفن الجذور)",
            status=RuleStatus.ACTIVE,
            event_types=[EventType.SOIL_MOISTURE_HIGH.value],
            priority=25,
            cooldown_minutes=360,
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.current_moisture_percent",
                        operator=ConditionOperator.GREATER_THAN,
                        value=80,
                        value_type="number",
                    ),
                ],
            ),
            actions=[
                ActionConfig(
                    action_type=ActionType.CREATE_TASK,
                    enabled=True,
                    task_config=TaskConfig(
                        title="Check Drainage System",
                        title_ar="فحص نظام الصرف",
                        description="Soil moisture is excessive. Check drainage and reduce irrigation.",
                        description_ar="رطوبة التربة مفرطة. فحص الصرف وتقليل الري.",
                        task_type="maintenance",
                        priority="high",
                        assign_to="field_owner",
                        due_hours=12,
                    ),
                ),
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push"],
                        recipients=["field_owner"],
                        title="⚠️ Excessive Soil Moisture",
                        title_ar="⚠️ رطوبة تربة مفرطة",
                        message="Soil is waterlogged. Risk of root rot. Check drainage.",
                        message_ar="التربة مشبعة بالماء. خطر تعفن الجذور. فحص الصرف.",
                        priority="high",
                    ),
                ),
            ],
            metadata={"rule_category": "soil_moisture", "auto_generated": True},
        ),
        # ═══════════════════════════════════════════════════════════════════════
        # قاعدة 5: تنبيه طقس - أمطار غزيرة - Heavy Rain Weather Alert
        # ═══════════════════════════════════════════════════════════════════════
        RuleCreate(
            tenant_id=tenant_id,
            name="Heavy Rain - Postpone Irrigation",
            name_ar="أمطار غزيرة - تأجيل الري",
            description="Postpone irrigation when heavy rain is forecasted",
            description_ar="تأجيل الري عند توقع أمطار غزيرة",
            status=RuleStatus.ACTIVE,
            event_types=[EventType.WEATHER_ALERT.value],
            priority=5,  # أولوية عالية جداً
            cooldown_minutes=1440,  # 24 ساعة
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.precipitation_mm",
                        operator=ConditionOperator.GREATER_THAN,
                        value=20,
                        value_type="number",
                    ),
                    RuleCondition(
                        field="metadata.forecast_hours",
                        operator=ConditionOperator.LESS_EQUAL,
                        value=48,
                        value_type="number",
                    ),
                ],
            ),
            actions=[
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push"],
                        recipients=["field_owner"],
                        title="🌧️ Heavy Rain Forecast",
                        title_ar="🌧️ توقع أمطار غزيرة",
                        message="Heavy rain expected. Postpone irrigation activities.",
                        message_ar="أمطار غزيرة متوقعة. أجّل أنشطة الري.",
                        priority="high",
                    ),
                ),
                ActionConfig(
                    action_type=ActionType.LOG_EVENT,
                    enabled=True,
                ),
            ],
            metadata={"rule_category": "weather", "auto_generated": True},
        ),
        # ═══════════════════════════════════════════════════════════════════════
        # قاعدة 6: تنبيه صقيع - Frost Alert
        # ═══════════════════════════════════════════════════════════════════════
        RuleCreate(
            tenant_id=tenant_id,
            name="Frost Alert - Protect Crops",
            name_ar="تنبيه صقيع - حماية المحاصيل",
            description="Alert farmers about frost risk to protect sensitive crops",
            description_ar="تنبيه المزارعين بخطر الصقيع لحماية المحاصيل الحساسة",
            status=RuleStatus.ACTIVE,
            event_types=[EventType.WEATHER_ALERT.value, EventType.TEMPERATURE_EXTREME.value],
            priority=3,  # أولوية قصوى
            cooldown_minutes=720,
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.temperature_celsius",
                        operator=ConditionOperator.LESS_EQUAL,
                        value=2,
                        value_type="number",
                    ),
                    RuleCondition(
                        field="metadata.alert_type",
                        operator=ConditionOperator.CONTAINS,
                        value="frost",
                        value_type="string",
                    ),
                ],
            ),
            actions=[
                ActionConfig(
                    action_type=ActionType.CREATE_TASK,
                    enabled=True,
                    task_config=TaskConfig(
                        title="Urgent: Protect Crops from Frost",
                        title_ar="عاجل: حماية المحاصيل من الصقيع",
                        description="Frost expected tonight. Cover sensitive plants or use frost protection methods.",
                        description_ar="صقيع متوقع الليلة. غطِّ النباتات الحساسة أو استخدم طرق الحماية من الصقيع.",
                        task_type="protection",
                        priority="urgent",
                        assign_to="field_owner",
                        due_hours=2,
                    ),
                ),
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push", "sms"],
                        recipients=["field_owner"],
                        title="❄️ URGENT: Frost Alert",
                        title_ar="❄️ عاجل: تنبيه صقيع",
                        message="Frost expected tonight! Protect sensitive crops immediately.",
                        message_ar="صقيع متوقع الليلة! احمِ المحاصيل الحساسة فوراً.",
                        priority="urgent",
                    ),
                ),
                ActionConfig(
                    action_type=ActionType.CREATE_ALERT,
                    enabled=True,
                    alert_config=AlertConfig(
                        alert_type="frost",
                        severity="critical",
                        title="Frost Warning",
                        title_ar="تحذير من الصقيع",
                        message="Frost conditions expected",
                        message_ar="ظروف صقيع متوقعة",
                        recommendations=[
                            "Cover sensitive plants",
                            "Use frost cloth or blankets",
                            "Consider sprinkler irrigation",
                        ],
                        recommendations_ar=[
                            "غطِّ النباتات الحساسة",
                            "استخدم قماش أو بطانيات مقاومة للصقيع",
                            "فكّر في الري بالرش",
                        ],
                        expire_hours=24,
                    ),
                ),
            ],
            metadata={"rule_category": "weather", "auto_generated": True},
        ),
        # ═══════════════════════════════════════════════════════════════════════
        # قاعدة 7: حدث فلكي - زراعة في القمر المناسب
        # Astronomical Event - Planting on Favorable Moon Phase
        # ═══════════════════════════════════════════════════════════════════════
        RuleCreate(
            tenant_id=tenant_id,
            name="Favorable Moon Phase for Planting",
            name_ar="طور قمر مناسب للزراعة",
            description="Suggest planting activities during favorable moon phases",
            description_ar="اقتراح أنشطة الزراعة خلال أطوار القمر المناسبة",
            status=RuleStatus.ACTIVE,
            event_types=[EventType.ASTRONOMICAL_EVENT.value],
            priority=50,  # أولوية منخفضة (اقتراح فقط)
            cooldown_minutes=10080,  # 7 أيام
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.event_category",
                        operator=ConditionOperator.EQUALS,
                        value="planting",
                        value_type="string",
                    ),
                ],
            ),
            actions=[
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push"],
                        recipients=["field_owner"],
                        title="🌙 Favorable Time for Planting",
                        title_ar="🌙 وقت مناسب للزراعة",
                        message="Traditional farming wisdom suggests this is a good time for planting.",
                        message_ar="حكمة الزراعة التقليدية تقترح أن هذا وقت جيد للزراعة.",
                        priority="normal",
                    ),
                ),
                ActionConfig(
                    action_type=ActionType.LOG_EVENT,
                    enabled=True,
                ),
            ],
            metadata={"rule_category": "astronomical", "auto_generated": True},
        ),
        # ═══════════════════════════════════════════════════════════════════════
        # قاعدة 8: حدث فلكي - حصاد في الوقت المناسب
        # Astronomical Event - Harvest at Optimal Time
        # ═══════════════════════════════════════════════════════════════════════
        RuleCreate(
            tenant_id=tenant_id,
            name="Favorable Moon Phase for Harvest",
            name_ar="طور قمر مناسب للحصاد",
            description="Suggest harvest activities during favorable moon phases",
            description_ar="اقتراح أنشطة الحصاد خلال أطوار القمر المناسبة",
            status=RuleStatus.ACTIVE,
            event_types=[EventType.ASTRONOMICAL_EVENT.value],
            priority=50,
            cooldown_minutes=10080,  # 7 أيام
            conditions=RuleConditionGroup(
                logic="AND",
                conditions=[
                    RuleCondition(
                        field="metadata.event_category",
                        operator=ConditionOperator.EQUALS,
                        value="harvest",
                        value_type="string",
                    ),
                ],
            ),
            actions=[
                ActionConfig(
                    action_type=ActionType.SEND_NOTIFICATION,
                    enabled=True,
                    notification_config=NotificationConfig(
                        channels=["push"],
                        recipients=["field_owner"],
                        title="🌙 Favorable Time for Harvest",
                        title_ar="🌙 وقت مناسب للحصاد",
                        message="Traditional farming suggests this is an optimal harvest period.",
                        message_ar="الزراعة التقليدية تقترح أن هذه فترة حصاد مثالية.",
                        priority="normal",
                    ),
                ),
                ActionConfig(
                    action_type=ActionType.LOG_EVENT,
                    enabled=True,
                ),
            ],
            metadata={"rule_category": "astronomical", "auto_generated": True},
        ),
    ]


# ═══════════════════════════════════════════════════════════════════════════════
# Service Clients - عملاء الخدمات
# ═══════════════════════════════════════════════════════════════════════════════


class ServiceClient:
    """
    عميل HTTP للاتصال بالخدمات الأخرى
    HTTP Client for communicating with other services

    يستخدم httpx للاتصال بـ:
    - خدمة المهام (Task Service)
    - خدمة الإشعارات (Notification Service)
    - خدمة التنبيهات (Alert Service)
    """

    def __init__(self, base_url: str, service_name: str):
        """
        تهيئة عميل الخدمة
        Initialize service client

        Args:
            base_url: عنوان الخدمة الأساسي
            service_name: اسم الخدمة للتسجيل
        """
        self.base_url = base_url
        self.service_name = service_name
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """الحصول على عميل HTTP أو إنشاءه - Get or create HTTP client"""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=30.0,
                headers={
                    "Content-Type": "application/json",
                    "X-Service-Name": "field-intelligence",
                },
            )
        return self._client

    async def close(self):
        """إغلاق عميل HTTP - Close HTTP client"""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def post(self, endpoint: str, data: dict) -> dict[str, Any]:
        """
        إرسال طلب POST
        Send POST request

        Args:
            endpoint: نقطة النهاية (مثل /tasks)
            data: البيانات للإرسال

        Returns:
            استجابة JSON
        """
        client = await self._get_client()

        try:
            response = await client.post(endpoint, json=data)

            if response.status_code in (200, 201):
                logger.info(f"✅ {self.service_name}: طلب ناجح إلى {endpoint}")
                return {"success": True, "data": response.json()}
            else:
                logger.warning(
                    f"⚠️ {self.service_name}: استجابة {response.status_code} من {endpoint}"
                )
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "details": response.text,
                }

        except httpx.ConnectError as e:
            logger.error(f"❌ {self.service_name}: فشل الاتصال - {str(e)}")
            return {"success": False, "error": "connection_error", "details": str(e)}

        except Exception as e:
            logger.error(f"❌ {self.service_name}: خطأ - {str(e)}", exc_info=True)
            return {"success": False, "error": "unknown_error", "details": str(e)}

    async def patch(self, endpoint: str, data: dict) -> dict[str, Any]:
        """
        إرسال طلب PATCH للتحديث
        Send PATCH request for updates

        Args:
            endpoint: نقطة النهاية
            data: البيانات للتحديث

        Returns:
            استجابة JSON
        """
        client = await self._get_client()

        try:
            response = await client.patch(endpoint, json=data)

            if response.status_code in (200, 204):
                logger.info(f"✅ {self.service_name}: تحديث ناجح - {endpoint}")
                return {"success": True, "data": response.json() if response.content else {}}
            else:
                logger.warning(
                    f"⚠️ {self.service_name}: استجابة {response.status_code} من {endpoint}"
                )
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                }

        except Exception as e:
            logger.error(f"❌ {self.service_name}: خطأ في التحديث - {str(e)}")
            return {"success": False, "error": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# Field Rules Engine - محرك القواعد الحقلية
# ═══════════════════════════════════════════════════════════════════════════════


class FieldRulesEngine:
    """
    محرك القواعد الذكي للحقول الزراعية
    Field Intelligence Rules Engine

    المسؤوليات - Responsibilities:
    ✓ تقييم الأحداث ضد القواعد النشطة
    ✓ تنفيذ الإجراءات (مهام، إشعارات، تنبيهات)
    ✓ حل التعارضات بين القواعد (الأولوية)
    ✓ إدارة فترة التهدئة (Cooldown)
    ✓ التحقق من صحة القواعد
    ✓ تمكين/تعطيل القواعد لكل حقل
    ✓ التكامل مع الخدمات الأخرى عبر HTTP
    ✓ تسجيل الأحداث والأخطاء

    الميزات - Features:
    - قواعد NDVI (مؤشر الغطاء النباتي)
    - قواعد الطقس (الأمطار، الصقيع، موجات الحر)
    - قواعد رطوبة التربة
    - قواعد الأحداث الفلكية
    - أولوية القواعد وحل التعارضات
    - معالجة غير متزامنة للأحداث
    """

    def __init__(
        self,
        task_service_url: str = TASK_SERVICE_URL,
        notification_service_url: str = NOTIFICATION_SERVICE_URL,
        alert_service_url: str = ALERT_SERVICE_URL,
    ):
        """
        تهيئة محرك القواعد
        Initialize rules engine

        Args:
            task_service_url: عنوان خدمة المهام
            notification_service_url: عنوان خدمة الإشعارات
            alert_service_url: عنوان خدمة التنبيهات
        """
        # عملاء الخدمات - Service clients
        self.task_client = ServiceClient(task_service_url, "TaskService")
        self.notification_client = ServiceClient(notification_service_url, "NotificationService")
        self.alert_client = ServiceClient(alert_service_url, "AlertService")

        # سجل التنفيذ لإدارة فترة التهدئة - Execution history for cooldown
        self.execution_history: dict[str, datetime] = {}

        # إحصائيات - Statistics
        self.stats = {
            "total_evaluations": 0,
            "total_executions": 0,
            "total_failures": 0,
        }

        logger.info("✅ محرك القواعد الحقلية جاهز - Field Rules Engine initialized")

    async def close(self):
        """
        إغلاق الاتصالات
        Close connections
        """
        await self.task_client.close()
        await self.notification_client.close()
        await self.alert_client.close()
        logger.info("✅ تم إغلاق محرك القواعد - Rules engine closed")

    # ═══════════════════════════════════════════════════════════════════════════
    # Rule Validation - التحقق من صحة القواعد
    # ═══════════════════════════════════════════════════════════════════════════

    def validate_rule(self, rule: Rule | RuleCreate) -> tuple[bool, str | None]:
        """
        التحقق من صحة القاعدة
        Validate rule configuration

        Args:
            rule: القاعدة للتحقق منها

        Returns:
            (صحيحة, رسالة_خطأ_أو_None)
        """
        # التحقق من وجود شروط
        if not rule.conditions or not rule.conditions.conditions:
            return False, "القاعدة يجب أن تحتوي على شرط واحد على الأقل"

        # التحقق من وجود إجراءات
        if not rule.actions:
            return False, "القاعدة يجب أن تحتوي على إجراء واحد على الأقل"

        # التحقق من صحة الإجراءات
        for action in rule.actions:
            if action.action_type == ActionType.CREATE_TASK and not action.task_config:
                return False, "إجراء CREATE_TASK يحتاج إلى task_config"

            if (
                action.action_type == ActionType.SEND_NOTIFICATION
                and not action.notification_config
            ):
                return False, "إجراء SEND_NOTIFICATION يحتاج إلى notification_config"

            if action.action_type == ActionType.CREATE_ALERT and not action.alert_config:
                return False, "إجراء CREATE_ALERT يحتاج إلى alert_config"

            if action.action_type == ActionType.WEBHOOK and not action.webhook_config:
                return False, "إجراء WEBHOOK يحتاج إلى webhook_config"

        # التحقق من الأولوية
        if rule.priority < 0 or rule.priority > 1000:
            return False, "الأولوية يجب أن تكون بين 0 و 1000"

        # التحقق من فترة التهدئة
        if rule.cooldown_minutes < 0:
            return False, "فترة التهدئة لا يمكن أن تكون سالبة"

        logger.info(f"✅ القاعدة '{rule.name}' صحيحة")
        return True, None

    # ═══════════════════════════════════════════════════════════════════════════
    # Rule Evaluation - تقييم القواعد
    # ═══════════════════════════════════════════════════════════════════════════

    async def evaluate_rules(
        self, event: EventResponse, rules: list[Rule]
    ) -> list[RuleExecutionResult]:
        """
        تقييم قائمة القواعد على حدث معين
        Evaluate list of rules against an event

        Args:
            event: الحدث المراد تقييمه
            rules: قائمة القواعد

        Returns:
            نتائج التنفيذ
        """
        self.stats["total_evaluations"] += 1

        results: list[RuleExecutionResult] = []

        # فلترة القواعد النشطة فقط
        # Filter only active rules
        active_rules = [r for r in rules if r.status == RuleStatus.ACTIVE]

        logger.info(
            f"📋 تقييم {len(active_rules)} قاعدة نشطة من أصل {len(rules)} - "
            f"Evaluating {len(active_rules)} active rules out of {len(rules)}"
        )

        # ترتيب حسب الأولوية (أقل رقم = أعلى أولوية)
        # Sort by priority (lower number = higher priority)
        active_rules.sort(key=lambda r: r.priority)

        # تقييم كل قاعدة
        for rule in active_rules:
            try:
                result = await self.evaluate_single_rule(event, rule)
                if result:
                    results.append(result)
                    if result.success:
                        self.stats["total_executions"] += 1
                    else:
                        self.stats["total_failures"] += 1

            except Exception as e:
                logger.error(
                    f"❌ خطأ في تقييم القاعدة {rule.rule_id} ({rule.name}): {str(e)}",
                    exc_info=True,
                )
                self.stats["total_failures"] += 1
                results.append(
                    RuleExecutionResult(
                        rule_id=rule.rule_id,
                        event_id=event.event_id,
                        success=False,
                        executed_at=datetime.now(UTC),
                        actions_executed=0,
                        actions_failed=0,
                        error_message=str(e),
                    )
                )

        logger.info(
            f"📊 نتائج التقييم: {len(results)} قاعدة نُفذت - "
            f"Evaluation results: {len(results)} rules executed"
        )

        return results

    async def evaluate_single_rule(
        self, event: EventResponse, rule: Rule
    ) -> RuleExecutionResult | None:
        """
        تقييم قاعدة واحدة ضد حدث
        Evaluate a single rule against an event

        Args:
            event: الحدث
            rule: القاعدة

        Returns:
            نتيجة التنفيذ أو None إذا لم تطابق الشروط
        """
        # التحقق من فترة التهدئة (Cooldown)
        # Check cooldown period
        if not self._check_cooldown(rule):
            logger.debug(f"⏸️ القاعدة {rule.rule_id} ({rule.name}) ضمن فترة التهدئة - تم التجاهل")
            return None

        # التحقق من الحقول المطبقة
        # Check applicable fields
        if rule.field_ids and event.field_id not in rule.field_ids:
            logger.debug(f"⏭️ القاعدة {rule.rule_id} لا تنطبق على الحقل {event.field_id}")
            return None

        # التحقق من أنواع الأحداث
        # Check event types
        if rule.event_types and event.event_type.value not in rule.event_types:
            logger.debug(
                f"⏭️ القاعدة {rule.rule_id} لا تنطبق على نوع الحدث {event.event_type.value}"
            )
            return None

        # تقييم الشروط
        # Evaluate conditions
        if not self._evaluate_conditions(event, rule.conditions):
            logger.debug(f"⏭️ القاعدة {rule.rule_id} ({rule.name}) - الشروط لم تتحقق")
            return None

        logger.info(
            f"✅ القاعدة {rule.rule_id} ({rule.name}) طابقت الحدث {event.event_id} - "
            f"Rule matched event"
        )

        # تنفيذ الإجراءات
        # Execute actions
        execution_result = await self._execute_actions(event, rule)

        # تحديث آخر وقت تفعيل
        # Update last execution time
        self.execution_history[rule.rule_id] = datetime.now(UTC)

        return execution_result

    def _check_cooldown(self, rule: Rule) -> bool:
        """
        التحقق من فترة التهدئة للقاعدة
        Check if rule is in cooldown period

        Args:
            rule: القاعدة

        Returns:
            True إذا كانت القاعدة قابلة للتنفيذ
        """
        if rule.rule_id not in self.execution_history:
            return True

        last_execution = self.execution_history[rule.rule_id]
        cooldown_end = last_execution + timedelta(minutes=rule.cooldown_minutes)
        can_execute = datetime.now(UTC) >= cooldown_end

        if not can_execute:
            remaining_minutes = (cooldown_end - datetime.now(UTC)).total_seconds() / 60
            logger.debug(
                f"⏸️ القاعدة {rule.rule_id} في فترة تهدئة. متبقي {remaining_minutes:.1f} دقيقة"
            )

        return can_execute

    def _evaluate_conditions(
        self, event: EventResponse, condition_group: RuleConditionGroup
    ) -> bool:
        """
        تقييم مجموعة الشروط
        Evaluate condition group

        Args:
            event: الحدث
            condition_group: مجموعة الشروط

        Returns:
            True إذا تحققت الشروط
        """
        if not condition_group.conditions:
            return True

        results = []
        for condition in condition_group.conditions:
            result = self._evaluate_single_condition(event, condition)
            results.append(result)
            logger.debug(
                f"  شرط: {condition.field} {condition.operator.value} {condition.value} = {result}"
            )

        # تطبيق المعامل المنطقي (AND/OR)
        # Apply logical operator
        if condition_group.logic.upper() == "AND":
            final_result = all(results)
        elif condition_group.logic.upper() == "OR":
            final_result = any(results)
        else:
            logger.warning(f"⚠️ معامل منطقي غير معروف: {condition_group.logic}، استخدام AND")
            final_result = all(results)

        logger.debug(f"  نتيجة المجموعة ({condition_group.logic}): {final_result}")
        return final_result

    def _evaluate_single_condition(self, event: EventResponse, condition: RuleCondition) -> bool:
        """
        تقييم شرط واحد
        Evaluate single condition

        Args:
            event: الحدث
            condition: الشرط

        Returns:
            True إذا تحقق الشرط
        """
        try:
            # استخراج قيمة الحقل من الحدث
            # Extract field value from event
            field_value = self._get_field_value(event, condition.field)

            if field_value is None:
                logger.debug(f"⚠️ الحقل {condition.field} غير موجود في الحدث")
                return False

            # تطبيق المعامل
            # Apply operator
            operator = condition.operator
            expected_value = condition.value

            if operator == ConditionOperator.EQUALS:
                return field_value == expected_value

            elif operator == ConditionOperator.NOT_EQUALS:
                return field_value != expected_value

            elif operator == ConditionOperator.GREATER_THAN:
                return float(field_value) > float(expected_value)

            elif operator == ConditionOperator.LESS_THAN:
                return float(field_value) < float(expected_value)

            elif operator == ConditionOperator.GREATER_EQUAL:
                return float(field_value) >= float(expected_value)

            elif operator == ConditionOperator.LESS_EQUAL:
                return float(field_value) <= float(expected_value)

            elif operator == ConditionOperator.CONTAINS:
                return expected_value in str(field_value)

            elif operator == ConditionOperator.IN:
                return field_value in expected_value

            elif operator == ConditionOperator.BETWEEN:
                if isinstance(expected_value, list) and len(expected_value) == 2:
                    return expected_value[0] <= float(field_value) <= expected_value[1]
                return False

            else:
                logger.warning(f"⚠️ معامل غير معروف: {operator}")
                return False

        except Exception as e:
            logger.error(f"❌ خطأ في تقييم الشرط {condition.field}: {str(e)}")
            return False

    def _get_field_value(self, event: EventResponse, field_path: str) -> Any:
        """
        استخراج قيمة حقل من الحدث (يدعم النقاط للحقول المتداخلة)
        Extract field value from event (supports dot notation for nested fields)

        Args:
            event: الحدث
            field_path: مسار الحقل (مثل: metadata.current_ndvi)

        Returns:
            قيمة الحقل أو None
        """
        parts = field_path.split(".")
        value: Any = event

        for part in parts:
            value = value.get(part) if isinstance(value, dict) else getattr(value, part, None)

            if value is None:
                return None

        return value

    # ═══════════════════════════════════════════════════════════════════════════
    # Action Execution - تنفيذ الإجراءات
    # ═══════════════════════════════════════════════════════════════════════════

    async def _execute_actions(self, event: EventResponse, rule: Rule) -> RuleExecutionResult:
        """
        تنفيذ إجراءات القاعدة
        Execute rule actions

        Args:
            event: الحدث
            rule: القاعدة

        Returns:
            نتيجة التنفيذ
        """
        execution_details = []
        actions_executed = 0
        actions_failed = 0

        logger.info(
            f"🚀 تنفيذ {len(rule.actions)} إجراء للقاعدة {rule.name} - "
            f"Executing {len(rule.actions)} actions for rule {rule.name}"
        )

        for action in rule.actions:
            if not action.enabled:
                logger.debug(f"  ⏭️ الإجراء {action.action_type.value} معطل - تم تجاهله")
                continue

            try:
                action_result = await self._execute_single_action(event, rule, action)
                execution_details.append(action_result)

                if action_result.get("success"):
                    actions_executed += 1
                    logger.info(f"  ✅ الإجراء {action.action_type.value} نُفذ بنجاح")
                else:
                    actions_failed += 1
                    logger.warning(
                        f"  ⚠️ فشل الإجراء {action.action_type.value}: "
                        f"{action_result.get('error', 'unknown')}"
                    )

            except Exception as e:
                logger.error(
                    f"  ❌ خطأ في تنفيذ الإجراء {action.action_type.value}: {str(e)}",
                    exc_info=True,
                )
                actions_failed += 1
                execution_details.append(
                    {
                        "action_type": action.action_type.value,
                        "success": False,
                        "error": str(e),
                    }
                )

        return RuleExecutionResult(
            rule_id=rule.rule_id,
            event_id=event.event_id,
            success=actions_failed == 0,
            executed_at=datetime.now(UTC),
            actions_executed=actions_executed,
            actions_failed=actions_failed,
            execution_details=execution_details,
        )

    async def _execute_single_action(
        self, event: EventResponse, rule: Rule, action: ActionConfig
    ) -> dict[str, Any]:
        """
        تنفيذ إجراء واحد
        Execute single action

        Args:
            event: الحدث
            rule: القاعدة
            action: الإجراء

        Returns:
            نتيجة التنفيذ
        """
        action_type = action.action_type

        if action_type == ActionType.CREATE_TASK:
            return await self._create_task(event, rule, action)

        elif action_type == ActionType.SEND_NOTIFICATION:
            return await self._send_notification(event, rule, action)

        elif action_type == ActionType.CREATE_ALERT:
            return await self._create_alert(event, rule, action)

        elif action_type == ActionType.WEBHOOK:
            return await self._call_webhook(event, rule, action)

        elif action_type == ActionType.LOG_EVENT:
            return self._log_event(event, rule, action)

        elif action_type == ActionType.UPDATE_FIELD:
            return await self._update_field(event, rule, action)

        else:
            logger.warning(f"⚠️ نوع إجراء غير مدعوم: {action_type}")
            return {
                "action_type": action_type.value,
                "success": False,
                "error": "نوع إجراء غير مدعوم - Unsupported action type",
            }

    # ─────────────────────────────────────────────────────────────────────────
    # Action: Create Task - إنشاء مهمة
    # ─────────────────────────────────────────────────────────────────────────

    async def _create_task(
        self, event: EventResponse, rule: Rule, action: ActionConfig
    ) -> dict[str, Any]:
        """
        إنشاء مهمة تلقائية في خدمة المهام
        Create automated task in task service

        Args:
            event: الحدث المحفز
            rule: القاعدة
            action: إعداد الإجراء

        Returns:
            نتيجة الإنشاء
        """
        if not action.task_config:
            return {
                "action_type": "create_task",
                "success": False,
                "error": "إعداد المهمة غير موجود - Task config missing",
            }

        task_config = action.task_config

        # حساب موعد الاستحقاق
        # Calculate due date
        due_date = datetime.now(UTC) + timedelta(hours=task_config.due_hours)

        # إعداد البيانات للإرسال
        # Prepare payload
        payload = {
            "tenant_id": event.tenant_id,
            "field_id": event.field_id,
            "title": task_config.title,
            "title_ar": task_config.title_ar,
            "description": task_config.description,
            "description_ar": task_config.description_ar,
            "task_type": task_config.task_type,
            "priority": task_config.priority,
            "due_date": due_date.isoformat(),
            "status": "open",
            "source": "field-intelligence-rules",
            "correlation_id": event.event_id,
            "metadata": {
                **task_config.metadata,
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "event_type": event.event_type.value,
                "auto_generated": True,
            },
        }

        # تعيين المهمة للمستخدم
        # Assign task
        if task_config.assign_to and task_config.assign_to != "field_owner":
            payload["assigned_to"] = task_config.assign_to

        logger.info(f"📋 إنشاء مهمة: {task_config.title} للحقل {event.field_id}")

        # إرسال الطلب إلى خدمة المهام
        # Send request to task service
        result = await self.task_client.post("/api/tasks", payload)

        if result["success"]:
            task_id = result["data"].get("task_id", "unknown")
            return {
                "action_type": "create_task",
                "success": True,
                "task_id": task_id,
                "task_title": task_config.title,
            }
        else:
            return {
                "action_type": "create_task",
                "success": False,
                "error": result.get("error", "unknown"),
            }

    # ─────────────────────────────────────────────────────────────────────────
    # Action: Update Task - تحديث مهمة
    # ─────────────────────────────────────────────────────────────────────────

    async def _update_task(self, task_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """
        تحديث مهمة موجودة
        Update existing task

        Args:
            task_id: معرف المهمة
            updates: التحديثات المطلوبة

        Returns:
            نتيجة التحديث
        """
        logger.info(f"🔄 تحديث المهمة: {task_id}")

        result = await self.task_client.patch(f"/api/tasks/{task_id}", updates)

        return {
            "action_type": "update_task",
            "success": result["success"],
            "task_id": task_id,
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Action: Send Notification - إرسال إشعار
    # ─────────────────────────────────────────────────────────────────────────

    async def _send_notification(
        self, event: EventResponse, rule: Rule, action: ActionConfig
    ) -> dict[str, Any]:
        """
        إرسال إشعار عبر خدمة الإشعارات
        Send notification via notification service

        Args:
            event: الحدث
            rule: القاعدة
            action: إعداد الإجراء

        Returns:
            نتيجة الإرسال
        """
        if not action.notification_config:
            return {
                "action_type": "send_notification",
                "success": False,
                "error": "إعداد الإشعار غير موجود - Notification config missing",
            }

        notif_config = action.notification_config

        # إعداد البيانات
        # Prepare payload
        payload = {
            "tenant_id": event.tenant_id,
            "recipients": notif_config.recipients,
            "channels": notif_config.channels,
            "title": notif_config.title,
            "title_ar": notif_config.title_ar,
            "message": notif_config.message,
            "message_ar": notif_config.message_ar,
            "priority": notif_config.priority,
            "template_id": notif_config.template_id,
            "metadata": {
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "event_id": event.event_id,
                "event_type": event.event_type.value,
                "field_id": event.field_id,
            },
        }

        logger.info(f"🔔 إرسال إشعار: {notif_config.title} عبر {notif_config.channels}")

        # إرسال الطلب إلى خدمة الإشعارات
        # Send request to notification service
        result = await self.notification_client.post("/api/notifications/send", payload)

        if result["success"]:
            return {
                "action_type": "send_notification",
                "success": True,
                "channels": notif_config.channels,
                "recipients_count": len(notif_config.recipients),
            }
        else:
            return {
                "action_type": "send_notification",
                "success": False,
                "error": result.get("error", "unknown"),
            }

    # ─────────────────────────────────────────────────────────────────────────
    # Action: Create Alert - إنشاء تنبيه
    # ─────────────────────────────────────────────────────────────────────────

    async def _create_alert(
        self, event: EventResponse, rule: Rule, action: ActionConfig
    ) -> dict[str, Any]:
        """
        إنشاء تنبيه في خدمة التنبيهات
        Create alert in alert service

        Args:
            event: الحدث
            rule: القاعدة
            action: إعداد الإجراء

        Returns:
            نتيجة الإنشاء
        """
        if not action.alert_config:
            return {
                "action_type": "create_alert",
                "success": False,
                "error": "إعداد التنبيه غير موجود - Alert config missing",
            }

        alert_config = action.alert_config

        # حساب موعد الانتهاء
        # Calculate expiry
        expire_at = None
        if alert_config.expire_hours:
            expire_at = (datetime.now(UTC) + timedelta(hours=alert_config.expire_hours)).isoformat()

        # إعداد البيانات
        # Prepare payload
        payload = {
            "tenant_id": event.tenant_id,
            "field_id": event.field_id,
            "alert_type": alert_config.alert_type,
            "severity": alert_config.severity,
            "title": alert_config.title,
            "title_ar": alert_config.title_ar,
            "message": alert_config.message,
            "message_ar": alert_config.message_ar,
            "recommendations": alert_config.recommendations,
            "recommendations_ar": alert_config.recommendations_ar,
            "expire_at": expire_at,
            "source_event_id": event.event_id,
            "metadata": {
                "rule_id": rule.rule_id,
                "rule_name": rule.name,
                "event_type": event.event_type.value,
            },
        }

        logger.info(f"⚠️ إنشاء تنبيه: {alert_config.title} بخطورة {alert_config.severity}")

        # إرسال الطلب إلى خدمة التنبيهات
        # Send request to alert service
        result = await self.alert_client.post("/api/alerts", payload)

        if result["success"]:
            alert_id = result["data"].get("alert_id", "unknown")
            return {
                "action_type": "create_alert",
                "success": True,
                "alert_id": alert_id,
                "severity": alert_config.severity,
            }
        else:
            return {
                "action_type": "create_alert",
                "success": False,
                "error": result.get("error", "unknown"),
            }

    # ─────────────────────────────────────────────────────────────────────────
    # Action: Call Webhook - استدعاء Webhook
    # ─────────────────────────────────────────────────────────────────────────

    async def _call_webhook(
        self, event: EventResponse, rule: Rule, action: ActionConfig
    ) -> dict[str, Any]:
        """
        استدعاء Webhook خارجي
        Call external webhook

        Args:
            event: الحدث
            rule: القاعدة
            action: إعداد الإجراء

        Returns:
            نتيجة الاستدعاء
        """
        if not action.webhook_config:
            return {
                "action_type": "webhook",
                "success": False,
                "error": "إعداد Webhook غير موجود - Webhook config missing",
            }

        webhook_config = action.webhook_config

        # إعداد البيانات
        # Prepare payload
        if webhook_config.body_template:
            # استخدام قالب مخصص
            # Use custom template
            payload = webhook_config.body_template
        else:
            # بيانات افتراضية
            # Default payload
            payload = {
                "event": event.dict(),
                "rule": {
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "name_ar": rule.name_ar,
                },
                "timestamp": datetime.now(UTC).isoformat(),
            }

        logger.info(f"🌐 استدعاء Webhook: {webhook_config.method} {webhook_config.url}")

        try:
            async with httpx.AsyncClient(timeout=webhook_config.timeout_seconds) as client:
                response = await client.request(
                    method=webhook_config.method,
                    url=webhook_config.url,
                    json=payload,
                    headers=webhook_config.headers,
                )

                if response.status_code in (200, 201, 202, 204):
                    return {
                        "action_type": "webhook",
                        "success": True,
                        "url": webhook_config.url,
                        "method": webhook_config.method,
                        "status_code": response.status_code,
                    }
                else:
                    return {
                        "action_type": "webhook",
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "details": response.text,
                    }

        except Exception as e:
            logger.error(f"❌ فشل استدعاء Webhook: {str(e)}")
            return {
                "action_type": "webhook",
                "success": False,
                "error": str(e),
            }

    # ─────────────────────────────────────────────────────────────────────────
    # Action: Log Event - تسجيل الحدث
    # ─────────────────────────────────────────────────────────────────────────

    def _log_event(self, event: EventResponse, rule: Rule, action: ActionConfig) -> dict[str, Any]:
        """
        تسجيل الحدث في السجلات
        Log event to logs

        Args:
            event: الحدث
            rule: القاعدة
            action: إعداد الإجراء

        Returns:
            نتيجة التسجيل
        """
        logger.info(
            f"📝 تسجيل حدث: [{event.event_type.value}] {event.title} - القاعدة: {rule.name}"
        )

        logger.info(f"   الحقل: {event.field_id}")
        logger.info(f"   الخطورة: {event.severity.value}")
        logger.info(f"   الوصف: {event.description}")

        if event.metadata:
            logger.info(f"   البيانات الإضافية: {event.metadata}")

        return {
            "action_type": "log_event",
            "success": True,
            "logged_at": datetime.now(UTC).isoformat(),
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Action: Update Field - تحديث حقل
    # ─────────────────────────────────────────────────────────────────────────

    async def _update_field(
        self, event: EventResponse, rule: Rule, action: ActionConfig
    ) -> dict[str, Any]:
        """
        تحديث بيانات الحقل (placeholder)
        Update field data (placeholder for future implementation)

        Args:
            event: الحدث
            rule: القاعدة
            action: إعداد الإجراء

        Returns:
            نتيجة التحديث
        """
        logger.info(f"🔄 تحديث الحقل: {event.field_id}")

        # هذا الإجراء سيتم تطبيقه في المستقبل
        # This action will be implemented in the future
        return {
            "action_type": "update_field",
            "success": True,
            "field_id": event.field_id,
            "note": "Placeholder - implementation pending",
        }

    # ═══════════════════════════════════════════════════════════════════════════
    # Statistics & Monitoring - الإحصائيات والمراقبة
    # ═══════════════════════════════════════════════════════════════════════════

    def get_statistics(self) -> dict[str, Any]:
        """
        الحصول على إحصائيات محرك القواعد
        Get rules engine statistics

        Returns:
            إحصائيات الأداء
        """
        return {
            **self.stats,
            "active_cooldowns": len(self.execution_history),
        }

    def reset_statistics(self):
        """
        إعادة تعيين الإحصائيات
        Reset statistics
        """
        self.stats = {
            "total_evaluations": 0,
            "total_executions": 0,
            "total_failures": 0,
        }
        logger.info("📊 تم إعادة تعيين الإحصائيات - Statistics reset")


# ═══════════════════════════════════════════════════════════════════════════════
# Module Exports - تصدير الوحدة
# ═══════════════════════════════════════════════════════════════════════════════

# Alias for backward compatibility
RulesEngine = FieldRulesEngine

__all__ = [
    "FieldRulesEngine",
    "RulesEngine",  # Alias for backward compatibility
    "ServiceClient",
    "get_default_rules",
]
