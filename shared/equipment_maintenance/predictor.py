"""
SAHOOL Equipment Predictive Maintenance - الصيانة التنبؤية للمعدات

Provides predictive maintenance functionality including:
- Usage pattern analysis
- Failure probability estimation
- Remaining useful life (RUL) prediction
- Anomaly detection
- Component wear estimation
- Cost optimization recommendations

Version: 1.0.0
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from enum import StrEnum

from .models import (
    AlertSeverity,
    AlertType,
    Equipment,
    EquipmentType,
    MaintenanceAlert,
    MaintenancePriority,
    MaintenanceType,
    ServiceRecord,
    generate_id,
)

# ==============================================================================
# Enumerations - التعدادات
# ==============================================================================


class RiskLevel(StrEnum):
    """Risk level for equipment failure - مستوى خطر فشل المعدات"""

    MINIMAL = "minimal"  # الحد الأدنى
    LOW = "low"  # منخفض
    MODERATE = "moderate"  # متوسط
    HIGH = "high"  # مرتفع
    CRITICAL = "critical"  # حرج


class ComponentType(StrEnum):
    """Equipment component type - نوع مكون المعدات"""

    ENGINE = "engine"  # المحرك
    TRANSMISSION = "transmission"  # ناقل الحركة
    HYDRAULIC_SYSTEM = "hydraulic_system"  # النظام الهيدروليكي
    ELECTRICAL_SYSTEM = "electrical_system"  # النظام الكهربائي
    COOLING_SYSTEM = "cooling_system"  # نظام التبريد
    FUEL_SYSTEM = "fuel_system"  # نظام الوقود
    BRAKE_SYSTEM = "brake_system"  # نظام الفرامل
    STEERING = "steering"  # التوجيه
    PTO = "pto"  # عمود الإدارة
    CUTTING_SYSTEM = "cutting_system"  # نظام القطع
    THRESHING_SYSTEM = "threshing_system"  # نظام الدراس
    SPRAY_SYSTEM = "spray_system"  # نظام الرش
    PUMP = "pump"  # المضخة
    FILTRATION = "filtration"  # الترشيح
    TIRES = "tires"  # الإطارات
    BELTS = "belts"  # الأحزمة
    BEARINGS = "bearings"  # المحامل


class FailureMode(StrEnum):
    """Common failure modes - أوضاع الفشل الشائعة"""

    WEAR = "wear"  # تآكل
    FATIGUE = "fatigue"  # إجهاد
    CORROSION = "corrosion"  # تآكل كيميائي
    OVERHEATING = "overheating"  # ارتفاع حرارة
    CONTAMINATION = "contamination"  # تلوث
    LEAKAGE = "leakage"  # تسريب
    BLOCKAGE = "blockage"  # انسداد
    ELECTRICAL_FAULT = "electrical_fault"  # عطل كهربائي
    MECHANICAL_DAMAGE = "mechanical_damage"  # ضرر ميكانيكي
    CALIBRATION_DRIFT = "calibration_drift"  # انحراف المعايرة


# ==============================================================================
# Data Classes - فئات البيانات
# ==============================================================================


@dataclass
class UsageMetrics:
    """Usage metrics for an equipment - مقاييس الاستخدام للمعدات"""

    equipment_id: str
    period_start: datetime
    period_end: datetime

    # Operating hours - ساعات التشغيل
    total_hours: float = 0.0
    avg_daily_hours: float = 0.0
    max_daily_hours: float = 0.0
    operating_days: int = 0
    idle_days: int = 0

    # Intensity metrics - مقاييس الكثافة
    avg_load_percent: float = 50.0  # متوسط الحمل
    peak_load_percent: float = 100.0  # أقصى حمل
    overload_events: int = 0  # أحداث الحمل الزائد

    # Area/distance - المساحة/المسافة
    total_hectares: float = 0.0
    total_kilometers: float = 0.0
    avg_speed_kmh: float = 0.0

    # Fuel consumption - استهلاك الوقود
    total_fuel_l: float = 0.0
    avg_fuel_consumption_l_hr: float = 0.0
    fuel_efficiency_trend: str = "stable"  # improving, stable, declining

    # Environmental factors - العوامل البيئية
    avg_ambient_temp_c: float = 25.0
    dust_exposure_level: str = "normal"  # low, normal, high, severe
    humidity_exposure_level: str = "normal"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "equipment_id": self.equipment_id,
            "period_start": self.period_start.isoformat(),
            "period_end": self.period_end.isoformat(),
            "total_hours": self.total_hours,
            "avg_daily_hours": self.avg_daily_hours,
            "operating_days": self.operating_days,
            "avg_load_percent": self.avg_load_percent,
            "total_hectares": self.total_hectares,
            "total_fuel_l": self.total_fuel_l,
            "fuel_efficiency_trend": self.fuel_efficiency_trend,
        }


@dataclass
class ComponentHealth:
    """Health status of an equipment component - حالة صحة مكون المعدات"""

    component_type: ComponentType
    equipment_id: str

    # Health score - درجة الصحة
    health_score: float = 100.0  # 0-100, higher is healthier
    confidence: float = 0.8  # 0-1, confidence in the score

    # Degradation - التدهور
    degradation_rate: float = 0.0  # % per 100 hours
    current_wear_percent: float = 0.0  # Current wear level

    # Remaining useful life - العمر المتبقي
    estimated_rul_hours: float | None = None  # Remaining useful life
    estimated_rul_days: int | None = None
    rul_confidence_low: float | None = None  # Lower bound
    rul_confidence_high: float | None = None  # Upper bound

    # Risk assessment - تقييم المخاطر
    risk_level: RiskLevel = RiskLevel.LOW
    failure_probability_30d: float = 0.0  # % probability of failure in 30 days
    failure_probability_90d: float = 0.0

    # Primary failure modes - أوضاع الفشل الأساسية
    primary_failure_modes: list[FailureMode] = field(default_factory=list)
    failure_mode_probabilities: dict[str, float] = field(default_factory=dict)

    # Recommendations - التوصيات
    recommended_action: str = ""
    recommended_action_ar: str = ""
    urgency: MaintenancePriority = MaintenancePriority.LOW

    # Last assessment - آخر تقييم
    assessed_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    assessed_at_hours: float = 0.0

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "component_type": self.component_type.value,
            "equipment_id": self.equipment_id,
            "health_score": self.health_score,
            "confidence": self.confidence,
            "degradation_rate": self.degradation_rate,
            "current_wear_percent": self.current_wear_percent,
            "estimated_rul_hours": self.estimated_rul_hours,
            "estimated_rul_days": self.estimated_rul_days,
            "risk_level": self.risk_level.value,
            "failure_probability_30d": self.failure_probability_30d,
            "failure_probability_90d": self.failure_probability_90d,
            "primary_failure_modes": [fm.value for fm in self.primary_failure_modes],
            "recommended_action": self.recommended_action,
            "recommended_action_ar": self.recommended_action_ar,
            "urgency": self.urgency.value,
        }


@dataclass
class PredictiveInsight:
    """Predictive maintenance insight - رؤية الصيانة التنبؤية"""

    id: str
    equipment_id: str
    tenant_id: str

    # Insight details - تفاصيل الرؤية
    title: str
    title_ar: str
    description: str
    description_ar: str
    insight_type: str  # anomaly, trend, prediction, recommendation

    # Affected components - المكونات المتأثرة
    components: list[ComponentType] = field(default_factory=list)
    component_health: list[ComponentHealth] = field(default_factory=list)

    # Prediction - التنبؤ
    predicted_event: str = ""  # What is predicted
    predicted_event_ar: str = ""
    probability: float = 0.0  # 0-1
    confidence: float = 0.0  # 0-1
    time_horizon_days: int = 30  # Prediction horizon

    # Impact assessment - تقييم الأثر
    risk_level: RiskLevel = RiskLevel.LOW
    potential_downtime_hours: float = 0.0
    estimated_repair_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"
    production_impact: str = ""  # Impact on farm operations
    production_impact_ar: str = ""

    # Recommended action - الإجراء الموصى به
    recommended_action: str = ""
    recommended_action_ar: str = ""
    action_deadline: datetime | None = None
    priority: MaintenancePriority = MaintenancePriority.MEDIUM

    # Supporting data - البيانات الداعمة
    supporting_factors: list[str] = field(default_factory=list)
    supporting_factors_ar: list[str] = field(default_factory=list)
    data_quality: float = 0.8  # 0-1

    # Metadata
    generated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    valid_until: datetime | None = None
    is_active: bool = True
    acknowledged: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "equipment_id": self.equipment_id,
            "title": self.title,
            "title_ar": self.title_ar,
            "description": self.description,
            "description_ar": self.description_ar,
            "insight_type": self.insight_type,
            "components": [c.value for c in self.components],
            "probability": self.probability,
            "confidence": self.confidence,
            "risk_level": self.risk_level.value,
            "potential_downtime_hours": self.potential_downtime_hours,
            "estimated_repair_cost": str(self.estimated_repair_cost),
            "recommended_action": self.recommended_action,
            "recommended_action_ar": self.recommended_action_ar,
            "priority": self.priority.value,
            "generated_at": self.generated_at.isoformat(),
        }


@dataclass
class FailurePrediction:
    """Failure prediction for equipment - تنبؤ الفشل للمعدات"""

    equipment_id: str
    component: ComponentType
    failure_mode: FailureMode

    # Probability - الاحتمالية
    probability: float  # 0-1
    confidence: float  # 0-1

    # Timing - التوقيت
    earliest_failure: datetime | None = None
    most_likely_failure: datetime | None = None
    latest_failure: datetime | None = None

    # Impact - الأثر
    severity: AlertSeverity = AlertSeverity.WARNING
    estimated_repair_hours: float = 0.0
    estimated_cost: Decimal = Decimal("0.00")
    currency: str = "SAR"

    # Contributing factors - العوامل المساهمة
    contributing_factors: list[str] = field(default_factory=list)
    contributing_factors_ar: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "equipment_id": self.equipment_id,
            "component": self.component.value,
            "failure_mode": self.failure_mode.value,
            "probability": self.probability,
            "confidence": self.confidence,
            "earliest_failure": self.earliest_failure.isoformat() if self.earliest_failure else None,
            "most_likely_failure": self.most_likely_failure.isoformat() if self.most_likely_failure else None,
            "severity": self.severity.value,
            "estimated_repair_hours": self.estimated_repair_hours,
            "estimated_cost": str(self.estimated_cost),
        }


@dataclass
class CostOptimizationRecommendation:
    """Cost optimization recommendation - توصية تحسين التكلفة"""

    equipment_id: str
    recommendation_type: str  # timing, bundling, parts, outsourcing

    title: str
    title_ar: str
    description: str
    description_ar: str

    # Current vs recommended - الحالي مقابل الموصى به
    current_approach: str
    current_approach_ar: str
    recommended_approach: str
    recommended_approach_ar: str

    # Cost analysis - تحليل التكلفة
    current_cost: Decimal = Decimal("0.00")
    recommended_cost: Decimal = Decimal("0.00")
    potential_savings: Decimal = Decimal("0.00")
    savings_percent: float = 0.0
    currency: str = "SAR"

    # Implementation - التنفيذ
    implementation_effort: str = "low"  # low, medium, high
    implementation_steps: list[str] = field(default_factory=list)
    implementation_steps_ar: list[str] = field(default_factory=list)

    # Confidence - الثقة
    confidence: float = 0.8
    data_quality: float = 0.8

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "equipment_id": self.equipment_id,
            "recommendation_type": self.recommendation_type,
            "title": self.title,
            "title_ar": self.title_ar,
            "current_cost": str(self.current_cost),
            "recommended_cost": str(self.recommended_cost),
            "potential_savings": str(self.potential_savings),
            "savings_percent": self.savings_percent,
            "implementation_effort": self.implementation_effort,
            "confidence": self.confidence,
        }


# ==============================================================================
# Component Profiles - ملفات تعريف المكونات
# ==============================================================================


# Default component life expectancy (hours) by equipment type
COMPONENT_LIFE_HOURS: dict[EquipmentType, dict[ComponentType, float]] = {
    EquipmentType.TRACTOR: {
        ComponentType.ENGINE: 10000,
        ComponentType.TRANSMISSION: 8000,
        ComponentType.HYDRAULIC_SYSTEM: 5000,
        ComponentType.ELECTRICAL_SYSTEM: 6000,
        ComponentType.COOLING_SYSTEM: 4000,
        ComponentType.FUEL_SYSTEM: 5000,
        ComponentType.BRAKE_SYSTEM: 3000,
        ComponentType.STEERING: 6000,
        ComponentType.PTO: 5000,
        ComponentType.TIRES: 3000,
        ComponentType.BELTS: 1500,
        ComponentType.BEARINGS: 4000,
    },
    EquipmentType.HARVESTER: {
        ComponentType.ENGINE: 8000,
        ComponentType.TRANSMISSION: 6000,
        ComponentType.HYDRAULIC_SYSTEM: 4000,
        ComponentType.ELECTRICAL_SYSTEM: 5000,
        ComponentType.CUTTING_SYSTEM: 1000,
        ComponentType.THRESHING_SYSTEM: 2000,
        ComponentType.BELTS: 500,
        ComponentType.BEARINGS: 2000,
    },
    EquipmentType.SPRAYER: {
        ComponentType.PUMP: 2000,
        ComponentType.SPRAY_SYSTEM: 1500,
        ComponentType.FILTRATION: 500,
        ComponentType.HYDRAULIC_SYSTEM: 3000,
        ComponentType.TIRES: 2000,
    },
    EquipmentType.IRRIGATION_SYSTEM: {
        ComponentType.PUMP: 8000,
        ComponentType.FILTRATION: 2000,
        ComponentType.ELECTRICAL_SYSTEM: 5000,
        ComponentType.BEARINGS: 4000,
    },
}

# Failure mode probabilities by component
FAILURE_MODE_PROBABILITY: dict[ComponentType, dict[FailureMode, float]] = {
    ComponentType.ENGINE: {
        FailureMode.WEAR: 0.35,
        FailureMode.OVERHEATING: 0.20,
        FailureMode.CONTAMINATION: 0.15,
        FailureMode.FATIGUE: 0.15,
        FailureMode.LEAKAGE: 0.15,
    },
    ComponentType.HYDRAULIC_SYSTEM: {
        FailureMode.LEAKAGE: 0.40,
        FailureMode.CONTAMINATION: 0.25,
        FailureMode.WEAR: 0.20,
        FailureMode.OVERHEATING: 0.15,
    },
    ComponentType.PUMP: {
        FailureMode.WEAR: 0.35,
        FailureMode.LEAKAGE: 0.25,
        FailureMode.CONTAMINATION: 0.20,
        FailureMode.BLOCKAGE: 0.20,
    },
    ComponentType.ELECTRICAL_SYSTEM: {
        FailureMode.ELECTRICAL_FAULT: 0.45,
        FailureMode.CORROSION: 0.25,
        FailureMode.WEAR: 0.15,
        FailureMode.OVERHEATING: 0.15,
    },
    ComponentType.BELTS: {
        FailureMode.WEAR: 0.50,
        FailureMode.FATIGUE: 0.35,
        FailureMode.MECHANICAL_DAMAGE: 0.15,
    },
    ComponentType.BEARINGS: {
        FailureMode.WEAR: 0.45,
        FailureMode.FATIGUE: 0.30,
        FailureMode.CONTAMINATION: 0.15,
        FailureMode.OVERHEATING: 0.10,
    },
    ComponentType.FILTRATION: {
        FailureMode.BLOCKAGE: 0.60,
        FailureMode.CONTAMINATION: 0.25,
        FailureMode.WEAR: 0.15,
    },
    ComponentType.SPRAY_SYSTEM: {
        FailureMode.BLOCKAGE: 0.35,
        FailureMode.WEAR: 0.25,
        FailureMode.CORROSION: 0.20,
        FailureMode.LEAKAGE: 0.20,
    },
}

# Average repair costs by component (SAR)
REPAIR_COST_SAR: dict[ComponentType, dict[str, float]] = {
    ComponentType.ENGINE: {"minor": 2000, "moderate": 8000, "major": 25000},
    ComponentType.TRANSMISSION: {"minor": 1500, "moderate": 5000, "major": 15000},
    ComponentType.HYDRAULIC_SYSTEM: {"minor": 500, "moderate": 2000, "major": 8000},
    ComponentType.ELECTRICAL_SYSTEM: {"minor": 300, "moderate": 1000, "major": 3000},
    ComponentType.PUMP: {"minor": 400, "moderate": 1500, "major": 5000},
    ComponentType.BELTS: {"minor": 100, "moderate": 300, "major": 800},
    ComponentType.BEARINGS: {"minor": 200, "moderate": 600, "major": 1500},
    ComponentType.FILTRATION: {"minor": 100, "moderate": 300, "major": 800},
    ComponentType.SPRAY_SYSTEM: {"minor": 200, "moderate": 800, "major": 2500},
    ComponentType.CUTTING_SYSTEM: {"minor": 500, "moderate": 2000, "major": 6000},
    ComponentType.TIRES: {"minor": 300, "moderate": 800, "major": 2000},
}


# ==============================================================================
# Predictive Maintenance Engine - محرك الصيانة التنبؤية
# ==============================================================================


class PredictiveMaintenanceEngine:
    """
    Predictive maintenance engine for agricultural equipment
    محرك الصيانة التنبؤية للمعدات الزراعية
    """

    def __init__(self, tenant_id: str):
        """
        Initialize the predictive maintenance engine

        Args:
            tenant_id: Tenant identifier
        """
        if not tenant_id:
            raise ValueError("tenant_id is required for PredictiveMaintenanceEngine")
        self.tenant_id = tenant_id
        self._equipment: dict[str, Equipment] = {}
        self._service_history: dict[str, list[ServiceRecord]] = {}
        self._usage_data: dict[str, list[UsageMetrics]] = {}

    def register_equipment(self, equipment: Equipment) -> None:
        """
        Register equipment with the engine
        تسجيل المعدات مع المحرك
        """
        equipment_tenant_id = getattr(equipment, "tenant_id", None)
        if not equipment_tenant_id:
            raise ValueError("Equipment tenant_id is required and must be non-empty")
        if equipment_tenant_id != self.tenant_id:
            raise ValueError("Equipment does not belong to this tenant")
        self._equipment[equipment.id] = equipment

    def add_service_record(self, record: ServiceRecord) -> None:
        """
        Add a service record for analysis
        إضافة سجل خدمة للتحليل
        """
        if record.equipment_id not in self._service_history:
            self._service_history[record.equipment_id] = []
        self._service_history[record.equipment_id].append(record)

    def add_usage_metrics(self, metrics: UsageMetrics) -> None:
        """
        Add usage metrics for analysis
        إضافة مقاييس الاستخدام للتحليل
        """
        if metrics.equipment_id not in self._usage_data:
            self._usage_data[metrics.equipment_id] = []
        self._usage_data[metrics.equipment_id].append(metrics)

    def calculate_usage_metrics(
        self,
        equipment_id: str,
        period_days: int = 30,
    ) -> UsageMetrics | None:
        """
        Calculate usage metrics for an equipment over a period
        حساب مقاييس الاستخدام للمعدات خلال فترة
        """
        equipment = self._equipment.get(equipment_id)
        if not equipment:
            return None

        end_date = datetime.now(UTC)
        start_date = end_date - timedelta(days=period_days)

        # Get service records in period
        records = self._service_history.get(equipment_id, [])
        [r for r in records if start_date <= r.service_date <= end_date]

        # Calculate metrics (simplified - real implementation would use telemetry)
        avg_daily_hours = equipment.total_hours / max(
            (datetime.now(UTC) - (equipment.created_at or datetime.now(UTC))).days, 1
        )

        metrics = UsageMetrics(
            equipment_id=equipment_id,
            period_start=start_date,
            period_end=end_date,
            total_hours=avg_daily_hours * period_days,
            avg_daily_hours=avg_daily_hours,
            max_daily_hours=avg_daily_hours * 1.5,  # Estimate
            operating_days=int(period_days * 0.7),  # Estimate 70% utilization
            idle_days=int(period_days * 0.3),
            total_hectares=equipment.total_hectares
            / max((datetime.now(UTC) - (equipment.created_at or datetime.now(UTC))).days, 1)
            * period_days,
        )

        return metrics

    def assess_component_health(
        self,
        equipment_id: str,
        component: ComponentType,
    ) -> ComponentHealth:
        """
        Assess health of a specific component
        تقييم صحة مكون محدد
        """
        equipment = self._equipment.get(equipment_id)
        if not equipment:
            return ComponentHealth(
                component_type=component,
                equipment_id=equipment_id,
                health_score=0,
                confidence=0,
            )

        # Get expected life for this component
        expected_life = COMPONENT_LIFE_HOURS.get(equipment.equipment_type, {}).get(component, 5000)

        # Calculate wear based on operating hours
        total_hours = equipment.total_hours
        wear_percent = min((total_hours / expected_life) * 100, 100)

        # Health score decreases as wear increases (exponential decay)
        health_score = 100 * math.exp(-0.02 * wear_percent)

        # Estimate degradation rate (% per 100 hours)
        service_records = self._service_history.get(equipment_id, [])
        if len(service_records) >= 2:
            # Calculate from service history
            sorted_records = sorted(service_records, key=lambda r: r.hours_at_service)
            if len(sorted_records) >= 2:
                hours_diff = sorted_records[-1].hours_at_service - sorted_records[0].hours_at_service
                if hours_diff > 0:
                    degradation_rate = (100 - health_score) / (hours_diff / 100)
                else:
                    degradation_rate = 1.0
            else:
                degradation_rate = 1.0
        else:
            # Default degradation based on component type
            degradation_rate = 100 / (expected_life / 100)

        # Estimate remaining useful life
        if degradation_rate > 0:
            rul_hours = max(0, (100 - wear_percent) / degradation_rate * 100)
            rul_days = int(rul_hours / 8) if rul_hours > 0 else 0  # Assume 8h/day usage
        else:
            rul_hours = expected_life - total_hours
            rul_days = int(rul_hours / 8)

        # Calculate failure probabilities
        failure_prob_30d = self._calculate_failure_probability(wear_percent, degradation_rate, days=30)
        failure_prob_90d = self._calculate_failure_probability(wear_percent, degradation_rate, days=90)

        # Determine risk level
        if failure_prob_30d > 0.5:
            risk_level = RiskLevel.CRITICAL
            urgency = MaintenancePriority.EMERGENCY
        elif failure_prob_30d > 0.3:
            risk_level = RiskLevel.HIGH
            urgency = MaintenancePriority.HIGH
        elif failure_prob_30d > 0.15:
            risk_level = RiskLevel.MODERATE
            urgency = MaintenancePriority.MEDIUM
        elif failure_prob_30d > 0.05:
            risk_level = RiskLevel.LOW
            urgency = MaintenancePriority.LOW
        else:
            risk_level = RiskLevel.MINIMAL
            urgency = MaintenancePriority.LOW

        # Get failure modes for this component
        failure_modes = list(FAILURE_MODE_PROBABILITY.get(component, {}).keys())[:3]
        failure_mode_probs = FAILURE_MODE_PROBABILITY.get(component, {})

        # Generate recommendations
        if risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
            recommended_action = f"Immediate inspection of {component.value} recommended"
            recommended_action_ar = f"يوصى بالفحص الفوري لـ {self._get_component_name_ar(component)}"
        elif risk_level == RiskLevel.MODERATE:
            recommended_action = f"Schedule {component.value} inspection within 2 weeks"
            recommended_action_ar = f"جدولة فحص {self._get_component_name_ar(component)} خلال أسبوعين"
        else:
            recommended_action = f"Continue normal monitoring of {component.value}"
            recommended_action_ar = f"استمر في المراقبة العادية لـ {self._get_component_name_ar(component)}"

        return ComponentHealth(
            component_type=component,
            equipment_id=equipment_id,
            health_score=round(health_score, 1),
            confidence=0.75 if len(service_records) > 2 else 0.5,
            degradation_rate=round(degradation_rate, 2),
            current_wear_percent=round(wear_percent, 1),
            estimated_rul_hours=round(rul_hours, 0) if rul_hours > 0 else None,
            estimated_rul_days=rul_days if rul_days > 0 else None,
            rul_confidence_low=round(rul_hours * 0.7, 0) if rul_hours > 0 else None,
            rul_confidence_high=round(rul_hours * 1.3, 0) if rul_hours > 0 else None,
            risk_level=risk_level,
            failure_probability_30d=round(failure_prob_30d, 3),
            failure_probability_90d=round(failure_prob_90d, 3),
            primary_failure_modes=failure_modes,
            failure_mode_probabilities={fm.value: round(p, 2) for fm, p in failure_mode_probs.items()},
            recommended_action=recommended_action,
            recommended_action_ar=recommended_action_ar,
            urgency=urgency,
            assessed_at_hours=total_hours,
        )

    def _calculate_failure_probability(
        self,
        wear_percent: float,
        degradation_rate: float,
        days: int,
    ) -> float:
        """
        Calculate failure probability using Weibull distribution approximation
        حساب احتمالية الفشل باستخدام تقريب توزيع ويبل
        """
        # Simplified Weibull-based calculation
        # Higher wear and degradation increase failure probability
        hours = days * 8  # Assume 8h/day usage
        projected_wear = wear_percent + (degradation_rate * hours / 100)

        # Failure probability increases exponentially as wear approaches 100%
        if projected_wear >= 100:
            return min(0.95, 0.5 + (projected_wear - 100) * 0.01)

        # Use logistic function for smooth probability curve
        k = 0.08  # Steepness
        x0 = 80  # Midpoint (80% wear = 50% failure probability)
        probability = 1 / (1 + math.exp(-k * (projected_wear - x0)))

        return min(max(probability, 0.01), 0.95)

    def _get_component_name_ar(self, component: ComponentType) -> str:
        """Get Arabic name for component"""
        names = {
            ComponentType.ENGINE: "المحرك",
            ComponentType.TRANSMISSION: "ناقل الحركة",
            ComponentType.HYDRAULIC_SYSTEM: "النظام الهيدروليكي",
            ComponentType.ELECTRICAL_SYSTEM: "النظام الكهربائي",
            ComponentType.COOLING_SYSTEM: "نظام التبريد",
            ComponentType.FUEL_SYSTEM: "نظام الوقود",
            ComponentType.BRAKE_SYSTEM: "نظام الفرامل",
            ComponentType.STEERING: "التوجيه",
            ComponentType.PTO: "عمود الإدارة",
            ComponentType.CUTTING_SYSTEM: "نظام القطع",
            ComponentType.THRESHING_SYSTEM: "نظام الدراس",
            ComponentType.SPRAY_SYSTEM: "نظام الرش",
            ComponentType.PUMP: "المضخة",
            ComponentType.FILTRATION: "الترشيح",
            ComponentType.TIRES: "الإطارات",
            ComponentType.BELTS: "الأحزمة",
            ComponentType.BEARINGS: "المحامل",
        }
        return names.get(component, component.value)

    def assess_equipment_health(
        self,
        equipment_id: str,
    ) -> list[ComponentHealth]:
        """
        Assess health of all components for an equipment
        تقييم صحة جميع مكونات المعدات
        """
        equipment = self._equipment.get(equipment_id)
        if not equipment:
            return []

        # Get components for this equipment type
        components = COMPONENT_LIFE_HOURS.get(equipment.equipment_type, {}).keys()

        health_assessments = []
        for component in components:
            health = self.assess_component_health(equipment_id, component)
            health_assessments.append(health)

        # Sort by risk level (highest risk first)
        risk_order = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MODERATE: 2,
            RiskLevel.LOW: 3,
            RiskLevel.MINIMAL: 4,
        }
        health_assessments.sort(key=lambda h: risk_order.get(h.risk_level, 5))

        return health_assessments

    def predict_failures(
        self,
        equipment_id: str,
        horizon_days: int = 90,
    ) -> list[FailurePrediction]:
        """
        Predict potential failures for equipment
        التنبؤ بالأعطال المحتملة للمعدات
        """
        equipment = self._equipment.get(equipment_id)
        if not equipment:
            return []

        predictions: list[FailurePrediction] = []
        health_assessments = self.assess_equipment_health(equipment_id)

        now = datetime.now(UTC)

        for health in health_assessments:
            if health.failure_probability_90d > 0.1:  # At least 10% probability
                # Get most likely failure modes
                for failure_mode in health.primary_failure_modes[:2]:
                    mode_prob = health.failure_mode_probabilities.get(failure_mode.value, 0.3)

                    # Estimate timing
                    if health.estimated_rul_hours:
                        hours_to_failure = health.estimated_rul_hours
                        days_to_failure = int(hours_to_failure / 8)
                        most_likely = now + timedelta(days=days_to_failure)
                        earliest = now + timedelta(days=int(days_to_failure * 0.5))
                        latest = now + timedelta(days=int(days_to_failure * 1.5))
                    else:
                        most_likely = None
                        earliest = None
                        latest = None

                    # Estimate cost
                    repair_costs = REPAIR_COST_SAR.get(health.component_type, {})
                    if health.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                        estimated_cost = Decimal(str(repair_costs.get("major", 5000)))
                        severity = AlertSeverity.CRITICAL
                    elif health.risk_level == RiskLevel.MODERATE:
                        estimated_cost = Decimal(str(repair_costs.get("moderate", 2000)))
                        severity = AlertSeverity.WARNING
                    else:
                        estimated_cost = Decimal(str(repair_costs.get("minor", 500)))
                        severity = AlertSeverity.INFO

                    prediction = FailurePrediction(
                        equipment_id=equipment_id,
                        component=health.component_type,
                        failure_mode=failure_mode,
                        probability=round(health.failure_probability_90d * mode_prob, 3),
                        confidence=health.confidence,
                        earliest_failure=earliest,
                        most_likely_failure=most_likely,
                        latest_failure=latest,
                        severity=severity,
                        estimated_repair_hours=self._get_repair_hours(health.component_type, health.risk_level),
                        estimated_cost=estimated_cost,
                        contributing_factors=[
                            f"Current wear: {health.current_wear_percent:.0f}%",
                            f"Degradation rate: {health.degradation_rate:.1f}%/100h",
                            f"Operating hours: {health.assessed_at_hours:.0f}h",
                        ],
                        contributing_factors_ar=[
                            f"التآكل الحالي: {health.current_wear_percent:.0f}%",
                            f"معدل التدهور: {health.degradation_rate:.1f}%/100 ساعة",
                            f"ساعات التشغيل: {health.assessed_at_hours:.0f} ساعة",
                        ],
                    )
                    predictions.append(prediction)

        # Sort by probability (highest first)
        predictions.sort(key=lambda p: p.probability, reverse=True)

        return predictions

    def _get_repair_hours(self, component: ComponentType, risk_level: RiskLevel) -> float:
        """Get estimated repair hours based on component and risk"""
        base_hours = {
            ComponentType.ENGINE: 16,
            ComponentType.TRANSMISSION: 12,
            ComponentType.HYDRAULIC_SYSTEM: 6,
            ComponentType.ELECTRICAL_SYSTEM: 4,
            ComponentType.PUMP: 4,
            ComponentType.SPRAY_SYSTEM: 3,
            ComponentType.CUTTING_SYSTEM: 4,
            ComponentType.BELTS: 2,
            ComponentType.BEARINGS: 3,
            ComponentType.FILTRATION: 1,
            ComponentType.TIRES: 2,
        }

        hours = base_hours.get(component, 4)

        # Adjust based on risk level (worse condition = longer repair)
        if risk_level == RiskLevel.CRITICAL:
            return hours * 1.5
        elif risk_level == RiskLevel.HIGH:
            return hours * 1.2
        return hours

    def generate_insights(
        self,
        equipment_id: str,
    ) -> list[PredictiveInsight]:
        """
        Generate predictive maintenance insights for equipment
        إنشاء رؤى الصيانة التنبؤية للمعدات
        """
        equipment = self._equipment.get(equipment_id)
        if not equipment:
            return []

        insights: list[PredictiveInsight] = []
        health_assessments = self.assess_equipment_health(equipment_id)
        predictions = self.predict_failures(equipment_id)

        now = datetime.now(UTC)

        # Insight 1: Overall equipment health
        avg_health = statistics.mean([h.health_score for h in health_assessments]) if health_assessments else 100
        critical_components = [h for h in health_assessments if h.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]]

        if critical_components:
            component_names = ", ".join([c.component_type.value for c in critical_components])
            component_names_ar = ", ".join([self._get_component_name_ar(c.component_type) for c in critical_components])

            insight = PredictiveInsight(
                id=generate_id("insight"),
                equipment_id=equipment_id,
                tenant_id=self.tenant_id,
                title="Critical Components Require Attention",
                title_ar="مكونات حرجة تتطلب الانتباه",
                description=f"The following components are at high risk: {component_names}. Overall equipment health score is {avg_health:.0f}%.",
                description_ar=f"المكونات التالية معرضة لخطر عالي: {component_names_ar}. درجة صحة المعدات الإجمالية {avg_health:.0f}%.",
                insight_type="prediction",
                components=[c.component_type for c in critical_components],
                component_health=critical_components,
                risk_level=RiskLevel.HIGH
                if any(h.risk_level == RiskLevel.CRITICAL for h in critical_components)
                else RiskLevel.MODERATE,
                potential_downtime_hours=sum(
                    self._get_repair_hours(c.component_type, c.risk_level) for c in critical_components
                ),
                estimated_repair_cost=Decimal(
                    str(
                        sum(
                            REPAIR_COST_SAR.get(c.component_type, {}).get("moderate", 2000) for c in critical_components
                        )
                    )
                ),
                recommended_action="Schedule comprehensive inspection and preventive maintenance",
                recommended_action_ar="جدولة فحص شامل وصيانة وقائية",
                action_deadline=now + timedelta(days=14),
                priority=MaintenancePriority.HIGH,
                supporting_factors=[
                    f"Avg health: {avg_health:.0f}%",
                    f"Critical components: {len(critical_components)}",
                ],
                supporting_factors_ar=[
                    f"متوسط الصحة: {avg_health:.0f}%",
                    f"المكونات الحرجة: {len(critical_components)}",
                ],
                valid_until=now + timedelta(days=30),
            )
            insights.append(insight)

        # Insight 2: Upcoming failures
        high_prob_failures = [p for p in predictions if p.probability > 0.2]
        if high_prob_failures:
            top_failure = high_prob_failures[0]
            insight = PredictiveInsight(
                id=generate_id("insight"),
                equipment_id=equipment_id,
                tenant_id=self.tenant_id,
                title=f"High Probability of {top_failure.failure_mode.value.replace('_', ' ').title()} Failure",
                title_ar=f"احتمالية عالية لفشل {self._get_failure_mode_ar(top_failure.failure_mode)}",
                description=f"There is a {top_failure.probability * 100:.0f}% probability of {top_failure.failure_mode.value} failure in the {top_failure.component.value}.",
                description_ar=f"هناك احتمالية {top_failure.probability * 100:.0f}% لفشل {self._get_failure_mode_ar(top_failure.failure_mode)} في {self._get_component_name_ar(top_failure.component)}.",
                insight_type="prediction",
                components=[top_failure.component],
                predicted_event=f"{top_failure.failure_mode.value} failure",
                predicted_event_ar=f"فشل {self._get_failure_mode_ar(top_failure.failure_mode)}",
                probability=top_failure.probability,
                confidence=top_failure.confidence,
                time_horizon_days=90,
                risk_level=RiskLevel.HIGH if top_failure.severity == AlertSeverity.CRITICAL else RiskLevel.MODERATE,
                potential_downtime_hours=top_failure.estimated_repair_hours,
                estimated_repair_cost=top_failure.estimated_cost,
                recommended_action=f"Inspect {top_failure.component.value} and consider preventive replacement",
                recommended_action_ar=f"فحص {self._get_component_name_ar(top_failure.component)} والنظر في الاستبدال الوقائي",
                priority=MaintenancePriority.HIGH if top_failure.probability > 0.4 else MaintenancePriority.MEDIUM,
                supporting_factors=top_failure.contributing_factors,
                supporting_factors_ar=top_failure.contributing_factors_ar,
                valid_until=now + timedelta(days=30),
            )
            insights.append(insight)

        # Insight 3: Usage pattern analysis
        usage_metrics = self.calculate_usage_metrics(equipment_id, period_days=30)
        if usage_metrics and usage_metrics.avg_daily_hours > 10:
            insight = PredictiveInsight(
                id=generate_id("insight"),
                equipment_id=equipment_id,
                tenant_id=self.tenant_id,
                title="High Equipment Utilization Detected",
                title_ar="تم اكتشاف استخدام مرتفع للمعدات",
                description=f"Average daily usage is {usage_metrics.avg_daily_hours:.1f} hours, which is above normal. Consider increasing maintenance frequency.",
                description_ar=f"متوسط الاستخدام اليومي {usage_metrics.avg_daily_hours:.1f} ساعة، وهو أعلى من المعتاد. فكر في زيادة تكرار الصيانة.",
                insight_type="trend",
                risk_level=RiskLevel.MODERATE,
                recommended_action="Reduce service intervals by 20% due to high utilization",
                recommended_action_ar="تقليل فترات الخدمة بنسبة 20% بسبب الاستخدام المرتفع",
                priority=MaintenancePriority.MEDIUM,
                supporting_factors=[
                    f"Avg daily hours: {usage_metrics.avg_daily_hours:.1f}h",
                    f"Operating days: {usage_metrics.operating_days}",
                ],
                supporting_factors_ar=[
                    f"متوسط الساعات اليومية: {usage_metrics.avg_daily_hours:.1f} ساعة",
                    f"أيام التشغيل: {usage_metrics.operating_days}",
                ],
                valid_until=now + timedelta(days=14),
            )
            insights.append(insight)

        return insights

    def _get_failure_mode_ar(self, failure_mode: FailureMode) -> str:
        """Get Arabic name for failure mode"""
        names = {
            FailureMode.WEAR: "التآكل",
            FailureMode.FATIGUE: "الإجهاد",
            FailureMode.CORROSION: "التآكل الكيميائي",
            FailureMode.OVERHEATING: "ارتفاع الحرارة",
            FailureMode.CONTAMINATION: "التلوث",
            FailureMode.LEAKAGE: "التسريب",
            FailureMode.BLOCKAGE: "الانسداد",
            FailureMode.ELECTRICAL_FAULT: "العطل الكهربائي",
            FailureMode.MECHANICAL_DAMAGE: "الضرر الميكانيكي",
            FailureMode.CALIBRATION_DRIFT: "انحراف المعايرة",
        }
        return names.get(failure_mode, failure_mode.value)

    def get_cost_optimization_recommendations(
        self,
        equipment_id: str,
    ) -> list[CostOptimizationRecommendation]:
        """
        Get cost optimization recommendations for maintenance
        الحصول على توصيات تحسين التكلفة للصيانة
        """
        equipment = self._equipment.get(equipment_id)
        if not equipment:
            return []

        recommendations: list[CostOptimizationRecommendation] = []

        # Get service history and health data
        service_records = self._service_history.get(equipment_id, [])
        health_assessments = self.assess_equipment_health(equipment_id)

        # Recommendation 1: Bundling maintenance tasks
        # Check if multiple components need service around the same time
        components_due_soon = [h for h in health_assessments if h.risk_level in [RiskLevel.MODERATE, RiskLevel.HIGH]]
        if len(components_due_soon) >= 2:
            individual_cost = sum(
                REPAIR_COST_SAR.get(h.component_type, {}).get("minor", 500) for h in components_due_soon
            )
            # Bundling typically saves 15-20% on labor
            bundled_cost = individual_cost * 0.82

            rec = CostOptimizationRecommendation(
                equipment_id=equipment_id,
                recommendation_type="bundling",
                title="Bundle Multiple Maintenance Tasks",
                title_ar="تجميع مهام الصيانة المتعددة",
                description=f"Bundle maintenance for {len(components_due_soon)} components to save on labor costs.",
                description_ar=f"تجميع صيانة {len(components_due_soon)} مكونات لتوفير تكاليف العمالة.",
                current_approach="Perform maintenance separately as each becomes due",
                current_approach_ar="إجراء الصيانة بشكل منفصل عند استحقاق كل منها",
                recommended_approach="Schedule combined maintenance session for all components",
                recommended_approach_ar="جدولة جلسة صيانة مجمعة لجميع المكونات",
                current_cost=Decimal(str(individual_cost)),
                recommended_cost=Decimal(str(int(bundled_cost))),
                potential_savings=Decimal(str(int(individual_cost - bundled_cost))),
                savings_percent=round((1 - bundled_cost / individual_cost) * 100, 1),
                implementation_effort="low",
                implementation_steps=[
                    "Identify all components due for service",
                    "Order all required parts together",
                    "Schedule single maintenance window",
                    "Execute bundled maintenance",
                ],
                implementation_steps_ar=[
                    "تحديد جميع المكونات المستحقة للخدمة",
                    "طلب جميع قطع الغيار المطلوبة معاً",
                    "جدولة نافذة صيانة واحدة",
                    "تنفيذ الصيانة المجمعة",
                ],
            )
            recommendations.append(rec)

        # Recommendation 2: Preventive vs Corrective timing
        # If equipment has had emergency repairs, suggest better preventive timing
        emergency_records = [r for r in service_records if r.service_type == MaintenanceType.EMERGENCY]
        if len(emergency_records) >= 1:
            # Estimate cost savings from prevention
            emergency_cost = sum(float(r.total_cost) for r in emergency_records)
            preventive_cost = emergency_cost * 0.4  # Preventive typically 40% of emergency cost

            rec = CostOptimizationRecommendation(
                equipment_id=equipment_id,
                recommendation_type="timing",
                title="Shift from Reactive to Predictive Maintenance",
                title_ar="التحول من الصيانة التفاعلية إلى التنبؤية",
                description=f"Equipment has had {len(emergency_records)} emergency repairs. Predictive maintenance could reduce costs significantly.",
                description_ar=f"المعدات شهدت {len(emergency_records)} إصلاحات طارئة. الصيانة التنبؤية يمكن أن تقلل التكاليف بشكل كبير.",
                current_approach="React to failures as they occur",
                current_approach_ar="الاستجابة للأعطال عند حدوثها",
                recommended_approach="Monitor component health and perform maintenance before failure",
                recommended_approach_ar="مراقبة صحة المكونات وإجراء الصيانة قبل الفشل",
                current_cost=Decimal(str(int(emergency_cost))),
                recommended_cost=Decimal(str(int(preventive_cost))),
                potential_savings=Decimal(str(int(emergency_cost - preventive_cost))),
                savings_percent=round((1 - preventive_cost / emergency_cost) * 100 if emergency_cost > 0 else 0, 1),
                implementation_effort="medium",
                implementation_steps=[
                    "Enable telemetry monitoring if available",
                    "Set up regular health assessments",
                    "Adjust maintenance intervals based on predictions",
                    "Track and compare costs over time",
                ],
                implementation_steps_ar=[
                    "تمكين مراقبة القياس عن بعد إن توفرت",
                    "إعداد تقييمات صحية منتظمة",
                    "تعديل فترات الصيانة بناءً على التنبؤات",
                    "تتبع ومقارنة التكاليف بمرور الوقت",
                ],
            )
            recommendations.append(rec)

        # Recommendation 3: Parts inventory optimization
        # Check if parts are frequently needed
        parts_used = []
        for record in service_records:
            parts_used.extend(record.parts_used)

        if len(parts_used) > 5:
            rec = CostOptimizationRecommendation(
                equipment_id=equipment_id,
                recommendation_type="parts",
                title="Optimize Parts Inventory",
                title_ar="تحسين مخزون قطع الغيار",
                description="Maintain stock of frequently used parts to reduce downtime and enable bulk purchasing.",
                description_ar="الحفاظ على مخزون من القطع المستخدمة بشكل متكرر لتقليل وقت التوقف وتمكين الشراء بالجملة.",
                current_approach="Order parts as needed for each repair",
                current_approach_ar="طلب القطع حسب الحاجة لكل إصلاح",
                recommended_approach="Maintain optimal stock levels based on usage patterns",
                recommended_approach_ar="الحفاظ على مستويات مخزون مثلى بناءً على أنماط الاستخدام",
                current_cost=Decimal("0"),  # Would need actual data
                recommended_cost=Decimal("0"),
                potential_savings=Decimal("0"),
                savings_percent=10.0,  # Estimated
                implementation_effort="low",
                implementation_steps=[
                    "Analyze parts usage history",
                    "Identify frequently used parts",
                    "Set minimum stock levels",
                    "Negotiate bulk purchase agreements",
                ],
                implementation_steps_ar=[
                    "تحليل سجل استخدام القطع",
                    "تحديد القطع المستخدمة بشكل متكرر",
                    "تعيين مستويات المخزون الأدنى",
                    "التفاوض على اتفاقيات الشراء بالجملة",
                ],
                confidence=0.7,
            )
            recommendations.append(rec)

        return recommendations

    def generate_maintenance_alerts(
        self,
        equipment_id: str | None = None,
    ) -> list[MaintenanceAlert]:
        """
        Generate predictive maintenance alerts
        إنشاء تنبيهات الصيانة التنبؤية
        """
        alerts: list[MaintenanceAlert] = []
        equipment_ids = [equipment_id] if equipment_id else list(self._equipment.keys())

        for equip_id in equipment_ids:
            equipment = self._equipment.get(equip_id)
            if not equipment:
                continue

            health_assessments = self.assess_equipment_health(equip_id)

            for health in health_assessments:
                if health.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]:
                    severity = (
                        AlertSeverity.CRITICAL if health.risk_level == RiskLevel.CRITICAL else AlertSeverity.WARNING
                    )

                    alert = MaintenanceAlert(
                        id=generate_id("alert"),
                        tenant_id=self.tenant_id,
                        equipment_id=equip_id,
                        alert_type=AlertType.PREDICTIVE_WARNING,
                        severity=severity,
                        title=f"Predictive Alert: {health.component_type.value.replace('_', ' ').title()}",
                        title_ar=f"تنبيه تنبؤي: {self._get_component_name_ar(health.component_type)}",
                        message=f"Component health score: {health.health_score:.0f}%. Failure probability (30d): {health.failure_probability_30d * 100:.0f}%",
                        message_ar=f"درجة صحة المكون: {health.health_score:.0f}%. احتمالية الفشل (30 يوم): {health.failure_probability_30d * 100:.0f}%",
                        triggered_by="predictive_analysis",
                        trigger_value=f"Health: {health.health_score:.0f}%",
                        threshold_value="Health < 50%",
                        recommended_action=health.recommended_action,
                        recommended_action_ar=health.recommended_action_ar,
                    )
                    alerts.append(alert)

        return alerts
