"""
Real-time Monitoring Agent
وكيل المراقبة في الوقت الفعلي

Specialized agent for continuous monitoring of farm conditions and triggering alerts.
وكيل متخصص للمراقبة المستمرة لظروف المزرعة وإطلاق التنبيهات.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Set
from enum import Enum
from dataclasses import dataclass, asdict
import numpy as np
from langchain_core.tools import Tool
import structlog

from .base_agent import BaseAgent
from ..multi_agent.infrastructure.nats_bridge import (
    AgentNATSBridge,
    MessagePriority,
    MessageType,
)
from ..config import settings

logger = structlog.get_logger()


class AlertType(Enum):
    """
    Types of alerts the monitoring agent can generate
    أنواع التنبيهات التي يمكن لوكيل المراقبة إنشاؤها
    """
    DISEASE_RISK = "disease_risk"  # خطر المرض
    PEST_OUTBREAK = "pest_outbreak"  # تفشي الآفات
    WATER_STRESS = "water_stress"  # إجهاد المياه
    NUTRIENT_DEFICIENCY = "nutrient_deficiency"  # نقص المغذيات
    WEATHER_WARNING = "weather_warning"  # تحذير الطقس
    HARVEST_READY = "harvest_ready"  # جاهز للحصاد
    FROST_ALERT = "frost_alert"  # تنبيه الصقيع
    HEAT_STRESS = "heat_stress"  # إجهاد الحرارة
    FLOOD_RISK = "flood_risk"  # خطر الفيضان


class AlertSeverity(Enum):
    """
    Alert severity levels
    مستويات خطورة التنبيه
    """
    LOW = "low"  # منخفض
    MEDIUM = "medium"  # متوسط
    HIGH = "high"  # عالي
    CRITICAL = "critical"  # حرج


class MonitoringStatus(Enum):
    """
    Monitoring status for a field
    حالة المراقبة للحقل
    """
    ACTIVE = "active"  # نشط
    PAUSED = "paused"  # متوقف مؤقتاً
    STOPPED = "stopped"  # متوقف
    ERROR = "error"  # خطأ


@dataclass
class MonitoringConfig:
    """
    Configuration for field monitoring
    إعدادات مراقبة الحقل
    """
    # Monitoring intervals in seconds | فترات المراقبة بالثواني
    sensor_check_interval: int = 300  # 5 minutes | 5 دقائق
    satellite_check_interval: int = 86400  # 24 hours | 24 ساعة
    weather_check_interval: int = 3600  # 1 hour | ساعة واحدة

    # Threshold values | قيم العتبات
    soil_moisture_min: float = 20.0  # Minimum soil moisture % | الحد الأدنى لرطوبة التربة
    soil_moisture_max: float = 80.0  # Maximum soil moisture % | الحد الأقصى لرطوبة التربة
    temperature_min: float = 10.0  # Minimum temperature °C | الحد الأدنى للحرارة
    temperature_max: float = 35.0  # Maximum temperature °C | الحد الأقصى للحرارة
    ndvi_min_threshold: float = 0.4  # Minimum healthy NDVI | الحد الأدنى لـ NDVI الصحي
    ndvi_drop_threshold: float = 0.15  # Significant NDVI drop | انخفاض كبير في NDVI

    # Alert settings | إعدادات التنبيه
    enable_alerts: bool = True  # Enable/disable alerts | تفعيل/تعطيل التنبيهات
    alert_languages: List[str] = None  # Alert languages | لغات التنبيه

    def __post_init__(self):
        if self.alert_languages is None:
            self.alert_languages = ["ar", "en"]  # Arabic and English by default


@dataclass
class Alert:
    """
    Alert data structure
    بنية بيانات التنبيه
    """
    alert_id: str
    field_id: str
    alert_type: AlertType
    severity: AlertSeverity
    timestamp: str
    message_ar: str  # Arabic message | رسالة بالعربية
    message_en: str  # English message | رسالة بالإنجليزية
    data: Dict[str, Any]
    recommended_actions: List[str]
    confidence: float = 0.8

    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary | تحويل التنبيه إلى قاموس"""
        return {
            "alert_id": self.alert_id,
            "field_id": self.field_id,
            "alert_type": self.alert_type.value,
            "severity": self.severity.value,
            "timestamp": self.timestamp,
            "message_ar": self.message_ar,
            "message_en": self.message_en,
            "data": self.data,
            "recommended_actions": self.recommended_actions,
            "confidence": self.confidence,
        }


class RealtimeMonitorAgent(BaseAgent):
    """
    Real-time Monitoring Agent for continuous farm condition monitoring
    وكيل المراقبة في الوقت الفعلي للمراقبة المستمرة لظروف المزرعة

    Specializes in:
    - Continuous monitoring of IoT sensors
    - Satellite imagery analysis
    - Weather data monitoring
    - Anomaly detection
    - Alert generation and routing

    متخصص في:
    - المراقبة المستمرة لأجهزة الاستشعار IoT
    - تحليل الصور الفضائية
    - مراقبة بيانات الطقس
    - كشف الشذوذات
    - إنشاء وتوجيه التنبيهات
    """

    def __init__(
        self,
        tools: Optional[List[Tool]] = None,
        retriever: Optional[Any] = None,
        nats_url: Optional[str] = None,
    ):
        """
        Initialize Real-time Monitor Agent
        تهيئة وكيل المراقبة في الوقت الفعلي

        Args:
            tools: List of tools available to agent | قائمة الأدوات المتاحة
            retriever: RAG retriever instance | مثيل مسترجع RAG
            nats_url: NATS server URL | عنوان خادم NATS
        """
        super().__init__(
            name="realtime_monitor",
            role="Real-time Farm Monitoring and Alert Management Expert",
            tools=tools,
            retriever=retriever,
        )

        # NATS bridge for real-time events | جسر NATS للأحداث في الوقت الفعلي
        self.nats_url = nats_url or settings.nats_url
        self.nats_bridge: Optional[AgentNATSBridge] = None

        # Active monitoring sessions | جلسات المراقبة النشطة
        self.monitoring_sessions: Dict[str, Dict[str, Any]] = {}

        # Monitoring tasks | مهام المراقبة
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}

        # Alert history | سجل التنبيهات
        self.alert_history: Dict[str, List[Alert]] = {}

        # Historical data cache for anomaly detection | ذاكرة تخزين مؤقت للبيانات التاريخية لكشف الشذوذات
        self.historical_data: Dict[str, List[Dict[str, Any]]] = {}

        logger.info(
            "realtime_monitor_initialized",
            agent_name=self.name,
            nats_url=self.nats_url
        )

    async def initialize_nats(self):
        """
        Initialize NATS connection for real-time messaging
        تهيئة اتصال NATS للرسائل في الوقت الفعلي
        """
        try:
            self.nats_bridge = AgentNATSBridge(
                agent_id=self.name,
                nats_url=self.nats_url
            )
            await self.nats_bridge.connect()

            # Subscribe to monitoring events | الاشتراك في أحداث المراقبة
            await self.nats_bridge.subscribe(
                "sahool.monitoring.sensor_data",
                self._handle_sensor_data
            )
            await self.nats_bridge.subscribe(
                "sahool.monitoring.satellite_data",
                self._handle_satellite_data
            )
            await self.nats_bridge.subscribe(
                "sahool.monitoring.weather_data",
                self._handle_weather_data
            )

            logger.info("nats_bridge_initialized", agent_name=self.name)

        except Exception as e:
            logger.error(
                "nats_initialization_failed",
                agent_name=self.name,
                error=str(e)
            )
            raise

    async def shutdown_nats(self):
        """
        Shutdown NATS connection
        إيقاف اتصال NATS
        """
        if self.nats_bridge:
            await self.nats_bridge.disconnect()
            logger.info("nats_bridge_shutdown", agent_name=self.name)

    def get_system_prompt(self) -> str:
        """
        Get system prompt for Real-time Monitor Agent
        الحصول على موجه النظام لوكيل المراقبة في الوقت الفعلي
        """
        return """You are an expert Real-time Monitoring Agent specializing in continuous farm condition monitoring and alert management.

Your expertise includes:
- IoT sensor data analysis (soil moisture, temperature, humidity)
- Satellite imagery interpretation (NDVI, vegetation indices)
- Weather pattern analysis and forecasting
- Anomaly detection using statistical methods and machine learning
- Priority-based alert generation and routing
- Predictive analytics for crop health issues

When monitoring farm conditions:
1. Continuously analyze sensor data for threshold violations
2. Compare current values with historical patterns
3. Detect anomalies and unusual patterns
4. Generate timely alerts with appropriate severity levels
5. Provide actionable recommendations
6. Communicate in both Arabic and English

Alert Severity Guidelines:
- CRITICAL: Immediate action required (frost, flood, severe pest outbreak)
- HIGH: Action needed within 24 hours (water stress, disease risk)
- MEDIUM: Action needed within 2-3 days (nutrient deficiency)
- LOW: Monitoring recommended (minor deviations)

Always provide confidence scores and explain your reasoning.

أنت وكيل مراقبة في الوقت الفعلي متخصص في المراقبة المستمرة لظروف المزرعة وإدارة التنبيهات.

خبرتك تشمل:
- تحليل بيانات أجهزة الاستشعار IoT (رطوبة التربة، الحرارة، الرطوبة)
- تفسير الصور الفضائية (NDVI، مؤشرات الغطاء النباتي)
- تحليل أنماط الطقس والتنبؤ
- كشف الشذوذات باستخدام الأساليب الإحصائية والتعلم الآلي
- إنشاء وتوجيه التنبيهات حسب الأولوية
- التحليلات التنبؤية لمشاكل صحة المحاصيل

قدم تحليلات دقيقة مبنية على البيانات مع درجات الثقة والتوصيات القابلة للتنفيذ."""

    async def start_monitoring(
        self,
        field_id: str,
        config: Optional[MonitoringConfig] = None
    ) -> Dict[str, Any]:
        """
        Start monitoring a field
        بدء مراقبة حقل

        Args:
            field_id: Field identifier | معرف الحقل
            config: Monitoring configuration | إعدادات المراقبة

        Returns:
            Monitoring session info | معلومات جلسة المراقبة
        """
        try:
            # Use default config if not provided | استخدام الإعدادات الافتراضية إذا لم يتم توفيرها
            if config is None:
                config = MonitoringConfig()

            # Check if already monitoring | التحقق مما إذا كان يتم المراقبة بالفعل
            if field_id in self.monitoring_sessions:
                logger.warning(
                    "monitoring_already_active",
                    field_id=field_id
                )
                return {
                    "status": "already_active",
                    "field_id": field_id,
                    "message": "Monitoring already active for this field"
                }

            # Create monitoring session | إنشاء جلسة مراقبة
            session = {
                "field_id": field_id,
                "config": config,
                "status": MonitoringStatus.ACTIVE,
                "started_at": datetime.utcnow().isoformat(),
                "last_check": None,
                "alerts_generated": 0,
            }

            self.monitoring_sessions[field_id] = session
            self.alert_history[field_id] = []
            self.historical_data[field_id] = []

            # Start monitoring task | بدء مهمة المراقبة
            task = asyncio.create_task(
                self._monitoring_loop(field_id, config)
            )
            self.monitoring_tasks[field_id] = task

            logger.info(
                "monitoring_started",
                field_id=field_id,
                config=asdict(config)
            )

            # Publish monitoring started event | نشر حدث بدء المراقبة
            if self.nats_bridge:
                await self.nats_bridge.broadcast(
                    content={
                        "event": "monitoring_started",
                        "field_id": field_id,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                    priority=MessagePriority.NORMAL
                )

            return {
                "status": "success",
                "field_id": field_id,
                "session": session,
                "message": "Monitoring started successfully"
            }

        except Exception as e:
            logger.error(
                "monitoring_start_failed",
                field_id=field_id,
                error=str(e)
            )
            return {
                "status": "error",
                "field_id": field_id,
                "error": str(e)
            }

    async def stop_monitoring(self, field_id: str) -> Dict[str, Any]:
        """
        Stop monitoring a field
        إيقاف مراقبة حقل

        Args:
            field_id: Field identifier | معرف الحقل

        Returns:
            Stop status | حالة الإيقاف
        """
        try:
            if field_id not in self.monitoring_sessions:
                return {
                    "status": "not_found",
                    "field_id": field_id,
                    "message": "No active monitoring session for this field"
                }

            # Cancel monitoring task | إلغاء مهمة المراقبة
            if field_id in self.monitoring_tasks:
                task = self.monitoring_tasks[field_id]
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                del self.monitoring_tasks[field_id]

            # Update session status | تحديث حالة الجلسة
            session = self.monitoring_sessions[field_id]
            session["status"] = MonitoringStatus.STOPPED
            session["stopped_at"] = datetime.utcnow().isoformat()

            logger.info(
                "monitoring_stopped",
                field_id=field_id,
                duration=session.get("stopped_at")
            )

            # Publish monitoring stopped event | نشر حدث إيقاف المراقبة
            if self.nats_bridge:
                await self.nats_bridge.broadcast(
                    content={
                        "event": "monitoring_stopped",
                        "field_id": field_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "alerts_generated": session["alerts_generated"],
                    },
                    priority=MessagePriority.NORMAL
                )

            return {
                "status": "success",
                "field_id": field_id,
                "session": session,
                "message": "Monitoring stopped successfully"
            }

        except Exception as e:
            logger.error(
                "monitoring_stop_failed",
                field_id=field_id,
                error=str(e)
            )
            return {
                "status": "error",
                "field_id": field_id,
                "error": str(e)
            }

    async def check_anomalies(
        self,
        field_id: str,
        sensor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Detect anomalies in sensor data
        كشف الشذوذات في بيانات أجهزة الاستشعار

        Args:
            field_id: Field identifier | معرف الحقل
            sensor_data: Current sensor readings | قراءات أجهزة الاستشعار الحالية

        Returns:
            Anomaly detection results | نتائج كشف الشذوذات
        """
        try:
            anomalies = []

            # Get historical data for this field | الحصول على البيانات التاريخية لهذا الحقل
            historical = self.historical_data.get(field_id, [])

            # Threshold-based anomaly detection | كشف الشذوذات بناءً على العتبات
            config = self.monitoring_sessions.get(field_id, {}).get("config", MonitoringConfig())

            # Check soil moisture | فحص رطوبة التربة
            soil_moisture = sensor_data.get("soil_moisture")
            if soil_moisture is not None:
                if soil_moisture < config.soil_moisture_min:
                    anomalies.append({
                        "type": "low_soil_moisture",
                        "value": soil_moisture,
                        "threshold": config.soil_moisture_min,
                        "severity": AlertSeverity.HIGH,
                    })
                elif soil_moisture > config.soil_moisture_max:
                    anomalies.append({
                        "type": "high_soil_moisture",
                        "value": soil_moisture,
                        "threshold": config.soil_moisture_max,
                        "severity": AlertSeverity.MEDIUM,
                    })

            # Check temperature | فحص درجة الحرارة
            temperature = sensor_data.get("temperature")
            if temperature is not None:
                if temperature < config.temperature_min:
                    anomalies.append({
                        "type": "low_temperature",
                        "value": temperature,
                        "threshold": config.temperature_min,
                        "severity": AlertSeverity.HIGH if temperature < 5 else AlertSeverity.MEDIUM,
                    })
                elif temperature > config.temperature_max:
                    anomalies.append({
                        "type": "high_temperature",
                        "value": temperature,
                        "threshold": config.temperature_max,
                        "severity": AlertSeverity.HIGH if temperature > 40 else AlertSeverity.MEDIUM,
                    })

            # Statistical anomaly detection using historical data | كشف الشذوذات الإحصائية باستخدام البيانات التاريخية
            if len(historical) >= 10:
                statistical_anomalies = self._detect_statistical_anomalies(
                    sensor_data,
                    historical
                )
                anomalies.extend(statistical_anomalies)

            logger.info(
                "anomaly_check_completed",
                field_id=field_id,
                anomalies_found=len(anomalies)
            )

            return {
                "field_id": field_id,
                "timestamp": datetime.utcnow().isoformat(),
                "anomalies": anomalies,
                "has_anomalies": len(anomalies) > 0,
                "sensor_data": sensor_data,
            }

        except Exception as e:
            logger.error(
                "anomaly_detection_failed",
                field_id=field_id,
                error=str(e)
            )
            return {
                "field_id": field_id,
                "error": str(e),
                "has_anomalies": False,
            }

    async def analyze_stress_indicators(
        self,
        field_id: str,
        indices: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Analyze crop stress indicators from vegetation indices
        تحليل مؤشرات إجهاد المحاصيل من مؤشرات الغطاء النباتي

        Args:
            field_id: Field identifier | معرف الحقل
            indices: Vegetation indices (NDVI, NDWI, etc.) | مؤشرات الغطاء النباتي

        Returns:
            Stress analysis results | نتائج تحليل الإجهاد
        """
        try:
            stress_indicators = []

            # Get monitoring config | الحصول على إعدادات المراقبة
            config = self.monitoring_sessions.get(field_id, {}).get("config", MonitoringConfig())

            # Analyze NDVI | تحليل NDVI
            ndvi = indices.get("ndvi")
            if ndvi is not None:
                if ndvi < config.ndvi_min_threshold:
                    stress_indicators.append({
                        "indicator": "low_ndvi",
                        "value": ndvi,
                        "threshold": config.ndvi_min_threshold,
                        "stress_type": "vegetation_health",
                        "severity": self._calculate_ndvi_severity(ndvi),
                    })

                # Check for NDVI drop compared to historical average | فحص انخفاض NDVI مقارنة بالمتوسط التاريخي
                historical = self.historical_data.get(field_id, [])
                if historical:
                    historical_ndvi = [
                        h.get("indices", {}).get("ndvi")
                        for h in historical
                        if h.get("indices", {}).get("ndvi") is not None
                    ]
                    if historical_ndvi:
                        avg_ndvi = np.mean(historical_ndvi)
                        ndvi_drop = avg_ndvi - ndvi

                        if ndvi_drop > config.ndvi_drop_threshold:
                            stress_indicators.append({
                                "indicator": "ndvi_drop",
                                "current": ndvi,
                                "historical_avg": avg_ndvi,
                                "drop": ndvi_drop,
                                "stress_type": "sudden_decline",
                                "severity": AlertSeverity.HIGH,
                            })

            # Analyze NDWI (Normalized Difference Water Index) | تحليل NDWI
            ndwi = indices.get("ndwi")
            if ndwi is not None and ndwi < 0.2:
                stress_indicators.append({
                    "indicator": "low_ndwi",
                    "value": ndwi,
                    "stress_type": "water_stress",
                    "severity": AlertSeverity.HIGH if ndwi < 0.1 else AlertSeverity.MEDIUM,
                })

            # Use AI to analyze the stress patterns | استخدام الذكاء الاصطناعي لتحليل أنماط الإجهاد
            query = f"Analyze stress indicators for field {field_id} based on vegetation indices"
            context = {
                "field_id": field_id,
                "indices": indices,
                "stress_indicators": stress_indicators,
                "historical_data_points": len(self.historical_data.get(field_id, [])),
            }

            ai_analysis = await self.think(query, context=context, use_rag=True)

            logger.info(
                "stress_analysis_completed",
                field_id=field_id,
                stress_indicators_found=len(stress_indicators)
            )

            return {
                "field_id": field_id,
                "timestamp": datetime.utcnow().isoformat(),
                "indices": indices,
                "stress_indicators": stress_indicators,
                "has_stress": len(stress_indicators) > 0,
                "ai_analysis": ai_analysis,
            }

        except Exception as e:
            logger.error(
                "stress_analysis_failed",
                field_id=field_id,
                error=str(e)
            )
            return {
                "field_id": field_id,
                "error": str(e),
                "has_stress": False,
            }

    async def generate_alert(
        self,
        field_id: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        data: Dict[str, Any]
    ) -> Alert:
        """
        Generate and publish an alert
        إنشاء ونشر تنبيه

        Args:
            field_id: Field identifier | معرف الحقل
            alert_type: Type of alert | نوع التنبيه
            severity: Alert severity | خطورة التنبيه
            data: Alert data | بيانات التنبيه

        Returns:
            Generated alert | التنبيه المنشأ
        """
        try:
            # Generate alert ID | إنشاء معرف التنبيه
            alert_id = f"{field_id}_{alert_type.value}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"

            # Generate bilingual messages | إنشاء رسائل ثنائية اللغة
            messages = self._generate_alert_messages(alert_type, severity, data)

            # Generate recommendations | إنشاء توصيات
            recommendations = await self._generate_recommendations(
                alert_type,
                severity,
                data
            )

            # Create alert object | إنشاء كائن التنبيه
            alert = Alert(
                alert_id=alert_id,
                field_id=field_id,
                alert_type=alert_type,
                severity=severity,
                timestamp=datetime.utcnow().isoformat(),
                message_ar=messages["ar"],
                message_en=messages["en"],
                data=data,
                recommended_actions=recommendations,
                confidence=data.get("confidence", 0.8),
            )

            # Store alert in history | تخزين التنبيه في السجل
            if field_id not in self.alert_history:
                self.alert_history[field_id] = []
            self.alert_history[field_id].append(alert)

            # Update session alert count | تحديث عدد التنبيهات في الجلسة
            if field_id in self.monitoring_sessions:
                self.monitoring_sessions[field_id]["alerts_generated"] += 1

            # Publish alert via NATS | نشر التنبيه عبر NATS
            if self.nats_bridge:
                priority = self._map_severity_to_priority(severity)
                await self.nats_bridge.broadcast(
                    content={
                        "event": "alert_generated",
                        "alert": alert.to_dict(),
                    },
                    priority=priority
                )

            logger.info(
                "alert_generated",
                alert_id=alert_id,
                field_id=field_id,
                alert_type=alert_type.value,
                severity=severity.value
            )

            return alert

        except Exception as e:
            logger.error(
                "alert_generation_failed",
                field_id=field_id,
                alert_type=alert_type.value,
                error=str(e)
            )
            raise

    async def get_monitoring_status(self, field_id: str) -> Dict[str, Any]:
        """
        Get current monitoring status for a field
        الحصول على حالة المراقبة الحالية لحقل

        Args:
            field_id: Field identifier | معرف الحقل

        Returns:
            Monitoring status | حالة المراقبة
        """
        if field_id not in self.monitoring_sessions:
            return {
                "field_id": field_id,
                "status": "not_monitoring",
                "message": "No active monitoring session for this field"
            }

        session = self.monitoring_sessions[field_id]
        alerts = self.alert_history.get(field_id, [])

        # Get recent alerts | الحصول على التنبيهات الأخيرة
        recent_alerts = [
            alert.to_dict()
            for alert in alerts[-10:]  # Last 10 alerts
        ]

        return {
            "field_id": field_id,
            "status": session["status"].value,
            "started_at": session["started_at"],
            "last_check": session.get("last_check"),
            "alerts_generated": session["alerts_generated"],
            "recent_alerts": recent_alerts,
            "config": asdict(session["config"]),
            "historical_data_points": len(self.historical_data.get(field_id, [])),
        }

    async def predict_issues(
        self,
        field_id: str,
        timeframe: str = "24h"
    ) -> Dict[str, Any]:
        """
        Predict upcoming issues based on current trends
        التنبؤ بالمشاكل القادمة بناءً على الاتجاهات الحالية

        Args:
            field_id: Field identifier | معرف الحقل
            timeframe: Prediction timeframe (24h, 48h, 7d) | الإطار الزمني للتنبؤ

        Returns:
            Predicted issues | المشاكل المتوقعة
        """
        try:
            # Get historical data | الحصول على البيانات التاريخية
            historical = self.historical_data.get(field_id, [])

            if len(historical) < 5:
                return {
                    "field_id": field_id,
                    "timeframe": timeframe,
                    "predictions": [],
                    "confidence": 0.0,
                    "message": "Insufficient historical data for predictions"
                }

            # Use AI to predict issues | استخدام الذكاء الاصطناعي للتنبؤ بالمشاكل
            query = f"Predict potential issues for field {field_id} in the next {timeframe} based on historical trends"

            context = {
                "field_id": field_id,
                "timeframe": timeframe,
                "historical_data": historical[-20:],  # Last 20 data points
                "recent_alerts": [
                    alert.to_dict()
                    for alert in self.alert_history.get(field_id, [])[-5:]
                ],
            }

            prediction = await self.think(query, context=context, use_rag=True)

            logger.info(
                "issue_prediction_completed",
                field_id=field_id,
                timeframe=timeframe
            )

            return {
                "field_id": field_id,
                "timeframe": timeframe,
                "prediction": prediction,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(
                "issue_prediction_failed",
                field_id=field_id,
                error=str(e)
            )
            return {
                "field_id": field_id,
                "error": str(e),
            }

    # Private helper methods | طرق مساعدة خاصة

    async def _monitoring_loop(
        self,
        field_id: str,
        config: MonitoringConfig
    ):
        """
        Main monitoring loop for a field
        حلقة المراقبة الرئيسية لحقل

        Args:
            field_id: Field identifier | معرف الحقل
            config: Monitoring configuration | إعدادات المراقبة
        """
        logger.info("monitoring_loop_started", field_id=field_id)

        try:
            while True:
                # Check if monitoring is still active | التحقق من أن المراقبة لا تزال نشطة
                session = self.monitoring_sessions.get(field_id)
                if not session or session["status"] != MonitoringStatus.ACTIVE:
                    break

                # Update last check time | تحديث وقت آخر فحص
                session["last_check"] = datetime.utcnow().isoformat()

                # This is a placeholder - in production, this would:
                # 1. Fetch real sensor data
                # 2. Check for anomalies
                # 3. Generate alerts if needed
                # هذا عنصر نائب - في الإنتاج، سيقوم بـ:
                # 1. جلب بيانات أجهزة الاستشعار الحقيقية
                # 2. التحقق من الشذوذات
                # 3. إنشاء تنبيهات إذا لزم الأمر

                # Wait for next check interval | الانتظار حتى فترة الفحص التالية
                await asyncio.sleep(config.sensor_check_interval)

        except asyncio.CancelledError:
            logger.info("monitoring_loop_cancelled", field_id=field_id)
        except Exception as e:
            logger.error(
                "monitoring_loop_error",
                field_id=field_id,
                error=str(e)
            )
            if field_id in self.monitoring_sessions:
                self.monitoring_sessions[field_id]["status"] = MonitoringStatus.ERROR

    async def _handle_sensor_data(self, message):
        """
        Handle incoming sensor data from NATS
        معالجة بيانات أجهزة الاستشعار الواردة من NATS

        Args:
            message: NATS message containing sensor data | رسالة NATS تحتوي على بيانات أجهزة الاستشعار
        """
        try:
            content = message.content
            field_id = content.get("field_id")
            sensor_data = content.get("data")

            if field_id and sensor_data:
                # Store in historical data | التخزين في البيانات التاريخية
                if field_id not in self.historical_data:
                    self.historical_data[field_id] = []

                self.historical_data[field_id].append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "sensor_data": sensor_data,
                })

                # Keep only last 1000 data points | الاحتفاظ بآخر 1000 نقطة بيانات فقط
                if len(self.historical_data[field_id]) > 1000:
                    self.historical_data[field_id] = self.historical_data[field_id][-1000:]

                # Check for anomalies | التحقق من الشذوذات
                anomaly_result = await self.check_anomalies(field_id, sensor_data)

                # Generate alerts if anomalies detected | إنشاء تنبيهات إذا تم اكتشاف شذوذات
                if anomaly_result.get("has_anomalies"):
                    for anomaly in anomaly_result["anomalies"]:
                        alert_type = self._map_anomaly_to_alert_type(anomaly["type"])
                        await self.generate_alert(
                            field_id,
                            alert_type,
                            anomaly["severity"],
                            {"anomaly": anomaly, "sensor_data": sensor_data}
                        )

        except Exception as e:
            logger.error("sensor_data_handling_failed", error=str(e))

    async def _handle_satellite_data(self, message):
        """
        Handle incoming satellite data from NATS
        معالجة بيانات الأقمار الصناعية الواردة من NATS

        Args:
            message: NATS message containing satellite data | رسالة NATS تحتوي على بيانات الأقمار الصناعية
        """
        try:
            content = message.content
            field_id = content.get("field_id")
            indices = content.get("indices")

            if field_id and indices:
                # Store in historical data | التخزين في البيانات التاريخية
                if field_id not in self.historical_data:
                    self.historical_data[field_id] = []

                if self.historical_data[field_id]:
                    self.historical_data[field_id][-1]["indices"] = indices
                else:
                    self.historical_data[field_id].append({
                        "timestamp": datetime.utcnow().isoformat(),
                        "indices": indices,
                    })

                # Analyze stress indicators | تحليل مؤشرات الإجهاد
                stress_result = await self.analyze_stress_indicators(field_id, indices)

                # Generate alerts if stress detected | إنشاء تنبيهات إذا تم اكتشاف إجهاد
                if stress_result.get("has_stress"):
                    for indicator in stress_result["stress_indicators"]:
                        alert_type = self._map_stress_to_alert_type(indicator["stress_type"])
                        await self.generate_alert(
                            field_id,
                            alert_type,
                            indicator["severity"],
                            {"stress_indicator": indicator, "indices": indices}
                        )

        except Exception as e:
            logger.error("satellite_data_handling_failed", error=str(e))

    async def _handle_weather_data(self, message):
        """
        Handle incoming weather data from NATS
        معالجة بيانات الطقس الواردة من NATS

        Args:
            message: NATS message containing weather data | رسالة NATS تحتوي على بيانات الطقس
        """
        try:
            content = message.content
            field_id = content.get("field_id")
            weather_data = content.get("data")

            if field_id and weather_data:
                # Check for weather warnings | التحقق من تحذيرات الطقس
                warnings = weather_data.get("warnings", [])

                for warning in warnings:
                    severity = self._map_weather_severity(warning.get("severity"))
                    alert_type = self._map_weather_warning_to_alert_type(warning.get("type"))

                    await self.generate_alert(
                        field_id,
                        alert_type,
                        severity,
                        {"weather_warning": warning, "weather_data": weather_data}
                    )

        except Exception as e:
            logger.error("weather_data_handling_failed", error=str(e))

    def _detect_statistical_anomalies(
        self,
        current_data: Dict[str, Any],
        historical_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Detect anomalies using statistical methods
        كشف الشذوذات باستخدام الأساليب الإحصائية

        Args:
            current_data: Current sensor readings | القراءات الحالية
            historical_data: Historical sensor readings | القراءات التاريخية

        Returns:
            List of detected anomalies | قائمة الشذوذات المكتشفة
        """
        anomalies = []

        # Extract metrics for analysis | استخراج المقاييس للتحليل
        metrics = ["soil_moisture", "temperature", "humidity"]

        for metric in metrics:
            current_value = current_data.get(metric)
            if current_value is None:
                continue

            # Extract historical values | استخراج القيم التاريخية
            historical_values = [
                h.get("sensor_data", {}).get(metric)
                for h in historical_data
                if h.get("sensor_data", {}).get(metric) is not None
            ]

            if len(historical_values) < 5:
                continue

            # Calculate statistics | حساب الإحصائيات
            mean = np.mean(historical_values)
            std = np.std(historical_values)

            # Z-score anomaly detection | كشف الشذوذات باستخدام درجة Z
            if std > 0:
                z_score = abs((current_value - mean) / std)

                if z_score > 3:  # 3 standard deviations | 3 انحرافات معيارية
                    anomalies.append({
                        "type": f"statistical_anomaly_{metric}",
                        "metric": metric,
                        "value": current_value,
                        "mean": mean,
                        "std": std,
                        "z_score": z_score,
                        "severity": AlertSeverity.HIGH if z_score > 4 else AlertSeverity.MEDIUM,
                    })

        return anomalies

    def _calculate_ndvi_severity(self, ndvi: float) -> AlertSeverity:
        """
        Calculate alert severity based on NDVI value
        حساب خطورة التنبيه بناءً على قيمة NDVI

        Args:
            ndvi: NDVI value | قيمة NDVI

        Returns:
            Alert severity | خطورة التنبيه
        """
        if ndvi < 0.2:
            return AlertSeverity.CRITICAL
        elif ndvi < 0.3:
            return AlertSeverity.HIGH
        elif ndvi < 0.4:
            return AlertSeverity.MEDIUM
        else:
            return AlertSeverity.LOW

    def _generate_alert_messages(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        data: Dict[str, Any]
    ) -> Dict[str, str]:
        """
        Generate bilingual alert messages
        إنشاء رسائل تنبيه ثنائية اللغة

        Args:
            alert_type: Type of alert | نوع التنبيه
            severity: Alert severity | خطورة التنبيه
            data: Alert data | بيانات التنبيه

        Returns:
            Dictionary with 'ar' and 'en' messages | قاموس برسائل 'ar' و 'en'
        """
        # Alert message templates | قوالب رسائل التنبيه
        templates = {
            AlertType.DISEASE_RISK: {
                "ar": "تحذير: خطر الإصابة بالأمراض في الحقل. مستوى الخطورة: {severity}",
                "en": "Warning: Disease risk detected in field. Severity: {severity}"
            },
            AlertType.PEST_OUTBREAK: {
                "ar": "تنبيه: احتمال تفشي الآفات. مستوى الخطورة: {severity}",
                "en": "Alert: Potential pest outbreak. Severity: {severity}"
            },
            AlertType.WATER_STRESS: {
                "ar": "تحذير: إجهاد مائي في المحاصيل. مستوى الخطورة: {severity}",
                "en": "Warning: Water stress in crops. Severity: {severity}"
            },
            AlertType.NUTRIENT_DEFICIENCY: {
                "ar": "تنبيه: نقص في المغذيات. مستوى الخطورة: {severity}",
                "en": "Alert: Nutrient deficiency detected. Severity: {severity}"
            },
            AlertType.WEATHER_WARNING: {
                "ar": "تحذير طقس: {weather_type}. مستوى الخطورة: {severity}",
                "en": "Weather warning: {weather_type}. Severity: {severity}"
            },
            AlertType.HARVEST_READY: {
                "ar": "إشعار: المحصول جاهز للحصاد",
                "en": "Notice: Crop ready for harvest"
            },
            AlertType.FROST_ALERT: {
                "ar": "تحذير عاجل: خطر الصقيع. اتخذ إجراءات فورية",
                "en": "Urgent: Frost risk. Take immediate action"
            },
            AlertType.HEAT_STRESS: {
                "ar": "تحذير: إجهاد حراري في المحاصيل. مستوى الخطورة: {severity}",
                "en": "Warning: Heat stress in crops. Severity: {severity}"
            },
            AlertType.FLOOD_RISK: {
                "ar": "تحذير عاجل: خطر الفيضان. استعد للإجراءات الوقائية",
                "en": "Urgent: Flood risk. Prepare for preventive measures"
            },
        }

        template = templates.get(alert_type, {
            "ar": f"تنبيه: {alert_type.value}",
            "en": f"Alert: {alert_type.value}"
        })

        return {
            "ar": template["ar"].format(
                severity=severity.value,
                weather_type=data.get("weather_warning", {}).get("type", "")
            ),
            "en": template["en"].format(
                severity=severity.value,
                weather_type=data.get("weather_warning", {}).get("type", "")
            ),
        }

    async def _generate_recommendations(
        self,
        alert_type: AlertType,
        severity: AlertSeverity,
        data: Dict[str, Any]
    ) -> List[str]:
        """
        Generate recommended actions for an alert
        إنشاء الإجراءات الموصى بها لتنبيه

        Args:
            alert_type: Type of alert | نوع التنبيه
            severity: Alert severity | خطورة التنبيه
            data: Alert data | بيانات التنبيه

        Returns:
            List of recommended actions | قائمة الإجراءات الموصى بها
        """
        # Recommendation templates | قوالب التوصيات
        recommendations_map = {
            AlertType.DISEASE_RISK: [
                "Consult with disease expert agent for detailed diagnosis",
                "Inspect affected areas for visible signs of disease",
                "Consider preventive fungicide application",
            ],
            AlertType.PEST_OUTBREAK: [
                "Contact pest management agent for treatment plan",
                "Conduct field inspection to assess pest population",
                "Implement integrated pest management strategies",
            ],
            AlertType.WATER_STRESS: [
                "Increase irrigation frequency",
                "Check irrigation system for malfunctions",
                "Consult irrigation advisor for optimal watering schedule",
            ],
            AlertType.NUTRIENT_DEFICIENCY: [
                "Conduct soil test to identify specific nutrient deficiencies",
                "Apply appropriate fertilizers based on soil analysis",
                "Consult soil science agent for fertilization plan",
            ],
            AlertType.FROST_ALERT: [
                "URGENT: Activate frost protection measures immediately",
                "Use water sprinklers or wind machines if available",
                "Cover sensitive crops with protective material",
            ],
            AlertType.HEAT_STRESS: [
                "Increase irrigation to maintain soil moisture",
                "Consider shade netting for sensitive crops",
                "Monitor crop condition closely",
            ],
            AlertType.FLOOD_RISK: [
                "Ensure drainage systems are clear and functional",
                "Prepare emergency response plan",
                "Monitor weather updates continuously",
            ],
        }

        return recommendations_map.get(alert_type, [
            f"Monitor the situation closely",
            f"Consult with relevant agricultural experts",
        ])

    def _map_severity_to_priority(self, severity: AlertSeverity) -> MessagePriority:
        """
        Map alert severity to message priority
        ربط خطورة التنبيه بأولوية الرسالة

        Args:
            severity: Alert severity | خطورة التنبيه

        Returns:
            Message priority | أولوية الرسالة
        """
        mapping = {
            AlertSeverity.CRITICAL: MessagePriority.URGENT,
            AlertSeverity.HIGH: MessagePriority.HIGH,
            AlertSeverity.MEDIUM: MessagePriority.NORMAL,
            AlertSeverity.LOW: MessagePriority.LOW,
        }
        return mapping.get(severity, MessagePriority.NORMAL)

    def _map_anomaly_to_alert_type(self, anomaly_type: str) -> AlertType:
        """
        Map anomaly type to alert type
        ربط نوع الشذوذ بنوع التنبيه

        Args:
            anomaly_type: Type of anomaly | نوع الشذوذ

        Returns:
            Alert type | نوع التنبيه
        """
        mapping = {
            "low_soil_moisture": AlertType.WATER_STRESS,
            "high_soil_moisture": AlertType.FLOOD_RISK,
            "low_temperature": AlertType.FROST_ALERT,
            "high_temperature": AlertType.HEAT_STRESS,
        }
        return mapping.get(anomaly_type, AlertType.WEATHER_WARNING)

    def _map_stress_to_alert_type(self, stress_type: str) -> AlertType:
        """
        Map stress type to alert type
        ربط نوع الإجهاد بنوع التنبيه

        Args:
            stress_type: Type of stress | نوع الإجهاد

        Returns:
            Alert type | نوع التنبيه
        """
        mapping = {
            "vegetation_health": AlertType.DISEASE_RISK,
            "water_stress": AlertType.WATER_STRESS,
            "sudden_decline": AlertType.DISEASE_RISK,
        }
        return mapping.get(stress_type, AlertType.DISEASE_RISK)

    def _map_weather_warning_to_alert_type(self, warning_type: str) -> AlertType:
        """
        Map weather warning type to alert type
        ربط نوع تحذير الطقس بنوع التنبيه

        Args:
            warning_type: Type of weather warning | نوع تحذير الطقس

        Returns:
            Alert type | نوع التنبيه
        """
        mapping = {
            "frost": AlertType.FROST_ALERT,
            "heat_wave": AlertType.HEAT_STRESS,
            "heavy_rain": AlertType.FLOOD_RISK,
            "flood": AlertType.FLOOD_RISK,
        }
        return mapping.get(warning_type, AlertType.WEATHER_WARNING)

    def _map_weather_severity(self, severity_str: str) -> AlertSeverity:
        """
        Map weather severity string to AlertSeverity enum
        ربط نص خطورة الطقس بتعداد AlertSeverity

        Args:
            severity_str: Severity string | نص الخطورة

        Returns:
            Alert severity | خطورة التنبيه
        """
        mapping = {
            "low": AlertSeverity.LOW,
            "moderate": AlertSeverity.MEDIUM,
            "high": AlertSeverity.HIGH,
            "severe": AlertSeverity.CRITICAL,
        }
        return mapping.get(severity_str.lower(), AlertSeverity.MEDIUM)
