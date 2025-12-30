"""
Shared Context Store for Multi-Agent System
مخزن السياق المشترك لنظام متعدد الوكلاء

This module provides a Redis-based shared context store for multi-agent collaboration.
توفر هذه الوحدة مخزن سياق مشترك يعتمد على Redis للتعاون بين الوكلاء المتعددين.

Features:
- Centralized context storage for field data
- Agent opinions and recommendations tracking
- Fast Redis-based access with TTL
- Serialization/deserialization support
- Thread-safe operations

الميزات:
- تخزين مركزي للسياق لبيانات الحقل
- تتبع آراء الوكلاء والتوصيات
- وصول سريع يعتمد على Redis مع TTL
- دعم التسلسل/إلغاء التسلسل
- عمليات آمنة للخيوط

Author: SAHOOL Platform Team
License: MIT
"""

import json
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Union
from enum import Enum

# Import Redis client from shared cache
# استيراد عميل Redis من التخزين المؤقت المشترك
import sys
from pathlib import Path

# Add shared cache to path
# إضافة التخزين المؤقت المشترك إلى المسار
shared_cache_path = Path(__file__).parent.parent.parent.parent.parent.parent.parent / "shared" / "cache"
sys.path.insert(0, str(shared_cache_path))

from redis_sentinel import RedisSentinelClient, RedisSentinelConfig

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Data Classes - فئات البيانات
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class SoilAnalysis:
    """
    Soil analysis data
    بيانات تحليل التربة

    Attributes:
        ph: pH level (درجة الحموضة)
        nitrogen: Nitrogen content in ppm (محتوى النيتروجين)
        phosphorus: Phosphorus content in ppm (محتوى الفوسفور)
        potassium: Potassium content in ppm (محتوى البوتاسيوم)
        organic_matter: Organic matter percentage (نسبة المادة العضوية)
        texture: Soil texture type (نوع قوام التربة)
        moisture: Soil moisture percentage (نسبة رطوبة التربة)
        ec: Electrical conductivity (التوصيل الكهربائي)
        analysis_date: Date of analysis (تاريخ التحليل)
    """
    ph: float
    nitrogen: float  # ppm
    phosphorus: float  # ppm
    potassium: float  # ppm
    organic_matter: float  # percentage
    texture: str  # sandy, loamy, clay, etc.
    moisture: Optional[float] = None  # percentage
    ec: Optional[float] = None  # Electrical Conductivity (dS/m)
    analysis_date: Optional[str] = None


@dataclass
class WeatherData:
    """
    Weather data (current and forecast)
    بيانات الطقس (الحالية والمتوقعة)

    Attributes:
        temperature: Temperature in Celsius (درجة الحرارة)
        humidity: Humidity percentage (نسبة الرطوبة)
        precipitation: Precipitation in mm (هطول الأمطار)
        wind_speed: Wind speed in km/h (سرعة الرياح)
        wind_direction: Wind direction (اتجاه الرياح)
        conditions: Weather conditions description (وصف الأحوال الجوية)
        forecast_days: Number of forecast days (عدد أيام التوقعات)
        daily_forecasts: Daily forecast data (بيانات التوقعات اليومية)
    """
    temperature: float  # Celsius
    humidity: float  # percentage
    precipitation: float  # mm
    wind_speed: float  # km/h
    wind_direction: Optional[str] = None
    conditions: Optional[str] = None
    forecast_days: int = 7
    daily_forecasts: Optional[List[Dict[str, Any]]] = None


@dataclass
class SatelliteIndices:
    """
    Satellite vegetation indices
    مؤشرات الأقمار الصناعية للنباتات

    Attributes:
        ndvi: Normalized Difference Vegetation Index (مؤشر الغطاء النباتي)
        ndwi: Normalized Difference Water Index (مؤشر المياه)
        evi: Enhanced Vegetation Index (مؤشر الغطاء النباتي المحسن)
        savi: Soil Adjusted Vegetation Index (مؤشر الغطاء النباتي المعدل بالتربة)
        ndmi: Normalized Difference Moisture Index (مؤشر الرطوبة)
        capture_date: Date of satellite capture (تاريخ التقاط القمر الصناعي)
        cloud_coverage: Cloud coverage percentage (نسبة تغطية السحب)
    """
    ndvi: Optional[float] = None  # -1 to 1
    ndwi: Optional[float] = None  # -1 to 1
    evi: Optional[float] = None  # -1 to 1
    savi: Optional[float] = None  # -1 to 1
    ndmi: Optional[float] = None  # -1 to 1
    capture_date: Optional[str] = None
    cloud_coverage: Optional[float] = None  # percentage


@dataclass
class FarmAction:
    """
    Farm action/operation record
    سجل عملية/إجراء زراعي

    Attributes:
        action_id: Unique action identifier (معرف فريد للعملية)
        action_type: Type of action (نوع العملية)
        date: Date of action (تاريخ العملية)
        description: Action description (وصف العملية)
        products_used: List of products used (قائمة المنتجات المستخدمة)
        quantity: Quantity used (الكمية المستخدمة)
        unit: Unit of measurement (وحدة القياس)
        cost: Cost of action (تكلفة العملية)
        notes: Additional notes (ملاحظات إضافية)
    """
    action_id: str
    action_type: str  # irrigation, fertilization, pesticide, etc.
    date: str
    description: str
    products_used: Optional[List[str]] = None
    quantity: Optional[float] = None
    unit: Optional[str] = None
    cost: Optional[float] = None
    notes: Optional[str] = None


@dataclass
class Issue:
    """
    Current farm issue/problem
    مشكلة زراعية حالية

    Attributes:
        issue_id: Unique issue identifier (معرف فريد للمشكلة)
        issue_type: Type of issue (نوع المشكلة)
        severity: Severity level (مستوى الخطورة)
        description: Issue description (وصف المشكلة)
        detected_date: Date issue was detected (تاريخ اكتشاف المشكلة)
        affected_area: Affected area percentage (نسبة المساحة المتأثرة)
        images: List of image URLs (قائمة روابط الصور)
        status: Current status (الحالة الحالية)
    """
    issue_id: str
    issue_type: str  # disease, pest, nutrient_deficiency, water_stress, etc.
    severity: str  # low, medium, high, critical
    description: str
    detected_date: str
    affected_area: Optional[float] = None  # percentage
    images: Optional[List[str]] = None
    status: str = "active"  # active, monitoring, resolved


@dataclass
class FarmContext:
    """
    Complete farm/field context for multi-agent decision making
    سياق المزرعة/الحقل الكامل لاتخاذ القرارات متعددة الوكلاء

    This dataclass holds all relevant information about a farm field that agents
    need to make informed decisions and recommendations.

    تحتوي فئة البيانات هذه على جميع المعلومات ذات الصلة بحقل المزرعة التي يحتاجها
    الوكلاء لاتخاذ قرارات وتوصيات مستنيرة.

    Attributes:
        farm_id: Unique farm identifier (معرف فريد للمزرعة)
        field_id: Unique field identifier (معرف فريد للحقل)
        tenant_id: Tenant/owner identifier (معرف المستأجر/المالك)
        crop_type: Type of crop (نوع المحصول)
        growth_stage: Current growth stage (مرحلة النمو الحالية)
        planting_date: Date of planting (تاريخ الزراعة)
        soil_data: Soil analysis data (بيانات تحليل التربة)
        weather_data: Weather data (بيانات الطقس)
        satellite_indices: Satellite indices (مؤشرات الأقمار الصناعية)
        recent_actions: Recent farm actions (العمليات الزراعية الأخيرة)
        active_issues: Current active issues (المشاكل النشطة الحالية)
        agent_opinions: Opinions from different agents (آراء من وكلاء مختلفين)
        created_at: Context creation timestamp (وقت إنشاء السياق)
        updated_at: Last update timestamp (وقت آخر تحديث)
    """
    # Basic identifiers | المعرفات الأساسية
    farm_id: str
    field_id: str
    tenant_id: str

    # Crop information | معلومات المحصول
    crop_type: str
    growth_stage: str
    planting_date: str

    # Analysis data | بيانات التحليل
    soil_data: Optional[SoilAnalysis] = None
    weather_data: Optional[WeatherData] = None
    satellite_indices: Optional[SatelliteIndices] = None

    # Farm operations | العمليات الزراعية
    recent_actions: List[FarmAction] = field(default_factory=list)
    active_issues: List[Issue] = field(default_factory=list)

    # Multi-agent collaboration | التعاون متعدد الوكلاء
    agent_opinions: Dict[str, Dict[str, Any]] = field(default_factory=dict)

    # Metadata | البيانات الوصفية
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization
        تحويل إلى قاموس للتسلسل

        Returns:
            Dictionary representation (تمثيل القاموس)
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FarmContext':
        """
        Create FarmContext from dictionary
        إنشاء FarmContext من القاموس

        Args:
            data: Dictionary data (بيانات القاموس)

        Returns:
            FarmContext instance (مثيل FarmContext)
        """
        # Convert nested dataclasses | تحويل فئات البيانات المتداخلة
        if data.get('soil_data'):
            data['soil_data'] = SoilAnalysis(**data['soil_data'])

        if data.get('weather_data'):
            data['weather_data'] = WeatherData(**data['weather_data'])

        if data.get('satellite_indices'):
            data['satellite_indices'] = SatelliteIndices(**data['satellite_indices'])

        if data.get('recent_actions'):
            data['recent_actions'] = [
                FarmAction(**action) for action in data['recent_actions']
            ]

        if data.get('active_issues'):
            data['active_issues'] = [
                Issue(**issue) for issue in data['active_issues']
            ]

        return cls(**data)


# ═══════════════════════════════════════════════════════════════════════════════
# Shared Context Store - مخزن السياق المشترك
# ═══════════════════════════════════════════════════════════════════════════════


class SharedContextStore:
    """
    Redis-based shared context store for multi-agent system
    مخزن السياق المشترك يعتمد على Redis لنظام متعدد الوكلاء

    This class provides centralized storage and retrieval of farm context data
    that multiple agents can access and contribute to during decision-making.

    توفر هذه الفئة تخزين واسترجاع مركزي لبيانات سياق المزرعة التي يمكن لعدة وكلاء
    الوصول إليها والمساهمة فيها أثناء اتخاذ القرارات.

    Features:
    - Fast Redis-based storage (تخزين سريع يعتمد على Redis)
    - Context TTL management (إدارة TTL للسياق)
    - Agent opinions tracking (تتبع آراء الوكلاء)
    - Thread-safe operations (عمليات آمنة للخيوط)
    - JSON serialization (تسلسل JSON)

    Example:
        >>> store = SharedContextStore()
        >>> context = FarmContext(farm_id="F1", field_id="FLD1", ...)
        >>> store.set_context("FLD1", context)
        >>> retrieved = store.get_context("FLD1")
        >>> store.add_agent_opinion("FLD1", "disease_expert", {...})
    """

    def __init__(
        self,
        redis_client: Optional[RedisSentinelClient] = None,
        ttl: int = 3600,
        key_prefix: str = "sahool:multi_agent:context"
    ):
        """
        Initialize shared context store
        تهيئة مخزن السياق المشترك

        Args:
            redis_client: Redis client instance (مثيل عميل Redis)
            ttl: Time-to-live in seconds (وقت البقاء بالثواني)
            key_prefix: Redis key prefix (بادئة مفتاح Redis)
        """
        self.redis_client = redis_client or RedisSentinelClient()
        self.ttl = ttl
        self.key_prefix = key_prefix

        logger.info(
            f"SharedContextStore initialized with TTL={ttl}s, prefix={key_prefix}"
        )

    def _make_key(self, field_id: str, suffix: str = "") -> str:
        """
        Create Redis key for field context
        إنشاء مفتاح Redis لسياق الحقل

        Args:
            field_id: Field identifier (معرف الحقل)
            suffix: Optional key suffix (لاحقة اختيارية للمفتاح)

        Returns:
            Redis key (مفتاح Redis)
        """
        if suffix:
            return f"{self.key_prefix}:{field_id}:{suffix}"
        return f"{self.key_prefix}:{field_id}"

    def get_context(self, field_id: str) -> Optional[FarmContext]:
        """
        Get farm context for a field
        الحصول على سياق المزرعة لحقل

        Args:
            field_id: Field identifier (معرف الحقل)

        Returns:
            FarmContext instance or None (مثيل FarmContext أو None)
        """
        try:
            key = self._make_key(field_id)
            data = self.redis_client.get(key, use_slave=True)

            if not data:
                logger.debug(f"No context found for field_id={field_id}")
                return None

            # Deserialize from JSON | إلغاء التسلسل من JSON
            context_dict = json.loads(data)
            context = FarmContext.from_dict(context_dict)

            logger.info(f"Context retrieved for field_id={field_id}")
            return context

        except Exception as e:
            logger.error(f"Failed to get context for field_id={field_id}: {e}")
            return None

    def set_context(self, field_id: str, context: FarmContext) -> bool:
        """
        Set/update farm context for a field
        تعيين/تحديث سياق المزرعة لحقل

        Args:
            field_id: Field identifier (معرف الحقل)
            context: FarmContext instance (مثيل FarmContext)

        Returns:
            True if successful (True إذا نجحت)
        """
        try:
            # Update timestamp | تحديث الوقت
            context.updated_at = datetime.now().isoformat()
            if not context.created_at:
                context.created_at = context.updated_at

            # Serialize to JSON | التسلسل إلى JSON
            context_dict = context.to_dict()
            data = json.dumps(context_dict, ensure_ascii=False, default=str)

            # Store in Redis with TTL | التخزين في Redis مع TTL
            key = self._make_key(field_id)
            result = self.redis_client.set(key, data, ex=self.ttl)

            if result:
                logger.info(
                    f"Context stored for field_id={field_id}, "
                    f"crop={context.crop_type}, stage={context.growth_stage}"
                )

            return bool(result)

        except Exception as e:
            logger.error(f"Failed to set context for field_id={field_id}: {e}")
            return False

    def update_context(
        self,
        field_id: str,
        updates: Dict[str, Any]
    ) -> bool:
        """
        Update specific fields in farm context
        تحديث حقول محددة في سياق المزرعة

        Args:
            field_id: Field identifier (معرف الحقل)
            updates: Dictionary of fields to update (قاموس الحقول للتحديث)

        Returns:
            True if successful (True إذا نجحت)
        """
        try:
            # Get existing context | الحصول على السياق الموجود
            context = self.get_context(field_id)
            if not context:
                logger.warning(
                    f"Cannot update - no context exists for field_id={field_id}"
                )
                return False

            # Update fields | تحديث الحقول
            context_dict = context.to_dict()
            for key, value in updates.items():
                if key in context_dict:
                    context_dict[key] = value

            # Create updated context | إنشاء سياق محدث
            updated_context = FarmContext.from_dict(context_dict)

            # Save updated context | حفظ السياق المحدث
            return self.set_context(field_id, updated_context)

        except Exception as e:
            logger.error(f"Failed to update context for field_id={field_id}: {e}")
            return False

    def add_agent_opinion(
        self,
        field_id: str,
        agent_id: str,
        opinion: Dict[str, Any]
    ) -> bool:
        """
        Add an agent's opinion/recommendation to the context
        إضافة رأي/توصية وكيل إلى السياق

        Args:
            field_id: Field identifier (معرف الحقل)
            agent_id: Agent identifier (معرف الوكيل)
            opinion: Agent's opinion dictionary (قاموس رأي الوكيل)

        Returns:
            True if successful (True إذا نجحت)
        """
        try:
            # Get existing context | الحصول على السياق الموجود
            context = self.get_context(field_id)
            if not context:
                logger.warning(
                    f"Cannot add opinion - no context exists for field_id={field_id}"
                )
                return False

            # Add timestamp to opinion | إضافة وقت إلى الرأي
            opinion['timestamp'] = datetime.now().isoformat()
            opinion['agent_id'] = agent_id

            # Update agent opinions | تحديث آراء الوكلاء
            context.agent_opinions[agent_id] = opinion

            # Save updated context | حفظ السياق المحدث
            result = self.set_context(field_id, context)

            if result:
                logger.info(
                    f"Opinion added for field_id={field_id}, agent={agent_id}"
                )

            return result

        except Exception as e:
            logger.error(
                f"Failed to add opinion for field_id={field_id}, "
                f"agent={agent_id}: {e}"
            )
            return False

    def get_all_opinions(self, field_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all agent opinions for a field
        الحصول على جميع آراء الوكلاء لحقل

        Args:
            field_id: Field identifier (معرف الحقل)

        Returns:
            Dictionary of agent opinions (قاموس آراء الوكلاء)
        """
        try:
            context = self.get_context(field_id)
            if not context:
                logger.debug(f"No context found for field_id={field_id}")
                return {}

            logger.info(
                f"Retrieved {len(context.agent_opinions)} opinions "
                f"for field_id={field_id}"
            )
            return context.agent_opinions

        except Exception as e:
            logger.error(f"Failed to get opinions for field_id={field_id}: {e}")
            return {}

    def clear_opinions(self, field_id: str) -> bool:
        """
        Clear all agent opinions after decision is made
        مسح جميع آراء الوكلاء بعد اتخاذ القرار

        Args:
            field_id: Field identifier (معرف الحقل)

        Returns:
            True if successful (True إذا نجحت)
        """
        try:
            context = self.get_context(field_id)
            if not context:
                logger.warning(
                    f"Cannot clear opinions - no context exists for field_id={field_id}"
                )
                return False

            # Clear opinions | مسح الآراء
            context.agent_opinions = {}

            # Save updated context | حفظ السياق المحدث
            result = self.set_context(field_id, context)

            if result:
                logger.info(f"Opinions cleared for field_id={field_id}")

            return result

        except Exception as e:
            logger.error(f"Failed to clear opinions for field_id={field_id}: {e}")
            return False

    def delete_context(self, field_id: str) -> bool:
        """
        Delete context for a field
        حذف السياق لحقل

        Args:
            field_id: Field identifier (معرف الحقل)

        Returns:
            True if successful (True إذا نجحت)
        """
        try:
            key = self._make_key(field_id)
            result = self.redis_client.delete(key)

            if result:
                logger.info(f"Context deleted for field_id={field_id}")

            return bool(result)

        except Exception as e:
            logger.error(f"Failed to delete context for field_id={field_id}: {e}")
            return False

    def context_exists(self, field_id: str) -> bool:
        """
        Check if context exists for a field
        التحقق من وجود سياق لحقل

        Args:
            field_id: Field identifier (معرف الحقل)

        Returns:
            True if exists (True إذا كان موجوداً)
        """
        try:
            key = self._make_key(field_id)
            return bool(self.redis_client.exists(key))
        except Exception as e:
            logger.error(f"Failed to check context existence for field_id={field_id}: {e}")
            return False

    def get_ttl(self, field_id: str) -> int:
        """
        Get remaining TTL for context
        الحصول على TTL المتبقي للسياق

        Args:
            field_id: Field identifier (معرف الحقل)

        Returns:
            Remaining seconds (-1 if no expiry, -2 if not exists)
            (الثواني المتبقية (-1 إذا لا نهاية، -2 إذا غير موجود))
        """
        try:
            key = self._make_key(field_id)
            return self.redis_client.ttl(key)
        except Exception as e:
            logger.error(f"Failed to get TTL for field_id={field_id}: {e}")
            return -2

    def refresh_ttl(self, field_id: str) -> bool:
        """
        Refresh TTL for context
        تحديث TTL للسياق

        Args:
            field_id: Field identifier (معرف الحقل)

        Returns:
            True if successful (True إذا نجحت)
        """
        try:
            key = self._make_key(field_id)
            result = self.redis_client.expire(key, self.ttl)

            if result:
                logger.debug(f"TTL refreshed for field_id={field_id}")

            return bool(result)

        except Exception as e:
            logger.error(f"Failed to refresh TTL for field_id={field_id}: {e}")
            return False

    def health_check(self) -> Dict[str, Any]:
        """
        Check health of the context store
        فحص صحة مخزن السياق

        Returns:
            Health status dictionary (قاموس حالة الصحة)
        """
        try:
            ping_result = self.redis_client.ping()

            return {
                "status": "healthy" if ping_result else "unhealthy",
                "redis_connected": ping_result,
                "ttl": self.ttl,
                "key_prefix": self.key_prefix,
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "redis_connected": False,
                "error": str(e),
            }


# ═══════════════════════════════════════════════════════════════════════════════
# Singleton Instance - مثيل فردي
# ═══════════════════════════════════════════════════════════════════════════════

_shared_context_store: Optional[SharedContextStore] = None


def get_shared_context_store(
    ttl: int = 3600,
    key_prefix: str = "sahool:multi_agent:context"
) -> SharedContextStore:
    """
    Get shared context store singleton instance
    الحصول على مثيل فردي لمخزن السياق المشترك

    Args:
        ttl: Time-to-live in seconds (وقت البقاء بالثواني)
        key_prefix: Redis key prefix (بادئة مفتاح Redis)

    Returns:
        SharedContextStore instance (مثيل SharedContextStore)
    """
    global _shared_context_store

    if _shared_context_store is None:
        _shared_context_store = SharedContextStore(ttl=ttl, key_prefix=key_prefix)

    return _shared_context_store
