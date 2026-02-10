"""
Smart Agriculture Deployment Manager | مدير نشر الزراعة الذكية

Manages deployment modes for smart agriculture systems including
SaaS and custom deployment options with low-code configuration.

يدير أوضاع النشر لأنظمة الزراعة الذكية بما في ذلك
خيارات SaaS والنشر المخصص مع تكوين منخفض الكود.

Deployment Options:
- SaaS Mode: ~8000 yuan/year, Web/App lightweight
- Custom Mode: 3-5k one-time, local server + edge gateway

Features:
- Low-code engine for drag-drop threshold customization
- Annual maintenance: ~500 yuan/year | الصيانة السنوية: ~500 يوان/سنة
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class DeploymentMode(Enum):
    """
    Deployment mode options.
    خيارات وضع النشر.
    """

    SAAS = "saas"
    CUSTOM = "custom"
    HYBRID = "hybrid"


class ServiceTier(Enum):
    """
    Service tier levels.
    مستويات طبقة الخدمة.
    """

    BASIC = "basic"
    STANDARD = "standard"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


@dataclass
class SaaSConfig:
    """
    SaaS deployment configuration.
    تكوين نشر SaaS.

    Attributes:
        annual_cost_yuan: Annual subscription cost | التكلفة السنوية للاشتراك
        tier: Service tier | طبقة الخدمة
        max_fields: Maximum fields supported | الحد الأقصى للحقول
        max_sensors: Maximum sensors supported | الحد الأقصى للمستشعرات
        features: List of included features | قائمة الميزات المضمنة
        support_level: Support level | مستوى الدعم
    """

    annual_cost_yuan: float = 8000.0
    tier: ServiceTier = ServiceTier.STANDARD
    max_fields: int = 50
    max_sensors: int = 200
    features: list[str] = field(default_factory=list)
    support_level: str = "email"

    def __post_init__(self):
        """Set default features based on tier."""
        if not self.features:
            self.features = self._get_tier_features()

    def _get_tier_features(self) -> list[str]:
        """Get features for the service tier."""
        base_features = [
            "water_fertilizer_pid",
            "environmental_ifttt",
            "basic_analytics",
            "mobile_app",
            "web_dashboard",
        ]

        tier_features = {
            ServiceTier.BASIC: base_features,
            ServiceTier.STANDARD: base_features
            + [
                "blockchain_trace",
                "advanced_analytics",
                "api_access",
            ],
            ServiceTier.PROFESSIONAL: base_features
            + [
                "blockchain_trace",
                "advanced_analytics",
                "api_access",
                "ai_advisory",
                "satellite_imagery",
                "custom_reports",
            ],
            ServiceTier.ENTERPRISE: base_features
            + [
                "blockchain_trace",
                "advanced_analytics",
                "api_access",
                "ai_advisory",
                "satellite_imagery",
                "custom_reports",
                "dedicated_support",
                "custom_integration",
                "white_label",
            ],
        }

        return tier_features.get(self.tier, base_features)


@dataclass
class CustomConfig:
    """
    Custom deployment configuration.
    تكوين النشر المخصص.

    Attributes:
        one_time_cost_yuan: One-time setup cost | تكلفة الإعداد لمرة واحدة
        hardware_cost_yuan: Hardware cost | تكلفة الأجهزة
        includes_server: Includes local server | يشمل خادم محلي
        includes_gateway: Includes edge gateway | يشمل بوابة حافة
        customizations: List of customizations | قائمة التخصيصات
    """

    one_time_cost_yuan: float = 4000.0
    hardware_cost_yuan: float = 0.0
    includes_server: bool = True
    includes_gateway: bool = True
    customizations: list[str] = field(default_factory=list)

    @property
    def total_cost(self) -> float:
        """Get total initial deployment cost."""
        return self.one_time_cost_yuan + self.hardware_cost_yuan


@dataclass
class LowCodeConfig:
    """
    Low-code engine configuration for threshold customization.
    تكوين محرك الكود المنخفض لتخصيص العتبات.

    Attributes:
        threshold_configs: Drag-drop threshold configurations | تكوينات العتبة
        rule_templates: Available rule templates | قوالب القواعد المتاحة
        custom_widgets: Custom dashboard widgets | أدوات لوحة القيادة المخصصة
        automation_flows: Automation flow definitions | تعريفات تدفق الأتمتة
    """

    threshold_configs: list[dict[str, Any]] = field(default_factory=list)
    rule_templates: list[dict[str, Any]] = field(default_factory=list)
    custom_widgets: list[dict[str, Any]] = field(default_factory=list)
    automation_flows: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class MaintenancePlan:
    """
    Annual maintenance plan.
    خطة الصيانة السنوية.

    Attributes:
        annual_cost_yuan: Annual maintenance cost | تكلفة الصيانة السنوية
        includes_updates: Includes software updates | يشمل تحديثات البرامج
        includes_support: Includes technical support | يشمل الدعم الفني
        response_time_hours: Support response time | وقت استجابة الدعم
        visits_per_year: On-site visits per year | زيارات الموقع في السنة
    """

    annual_cost_yuan: float = 500.0
    includes_updates: bool = True
    includes_support: bool = True
    response_time_hours: int = 24
    visits_per_year: int = 2


@dataclass
class ROIAnalysis:
    """
    Return on Investment analysis.
    تحليل العائد على الاستثمار.

    Attributes:
        initial_investment: Initial investment | الاستثمار الأولي
        annual_costs: Annual operating costs | التكاليف التشغيلية السنوية
        annual_savings: Annual savings from system | التوفير السنوي من النظام
        payback_months: Payback period in months | فترة الاسترداد بالأشهر
        five_year_roi: 5-year ROI percentage | عائد الاستثمار لـ 5 سنوات
        benefits: Itemized benefits | الفوائد المفصلة
    """

    initial_investment: float
    annual_costs: float
    annual_savings: float
    payback_months: int
    five_year_roi: float
    benefits: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "initial_investment_yuan": self.initial_investment,
            "annual_costs_yuan": self.annual_costs,
            "annual_savings_yuan": self.annual_savings,
            "payback_months": self.payback_months,
            "five_year_roi_pct": self.five_year_roi,
            "benefits": self.benefits,
        }

    def summary(self, language: str = "en") -> str:
        """Generate human-readable summary."""
        if language == "ar":
            return (
                f"تحليل العائد على الاستثمار\n"
                f"الاستثمار الأولي: {self.initial_investment:,.0f} يوان\n"
                f"التكاليف السنوية: {self.annual_costs:,.0f} يوان\n"
                f"التوفير السنوي: {self.annual_savings:,.0f} يوان\n"
                f"فترة الاسترداد: {self.payback_months} شهر\n"
                f"عائد الاستثمار (5 سنوات): {self.five_year_roi:.1f}%"
            )
        return (
            f"ROI Analysis\n"
            f"Initial Investment: {self.initial_investment:,.0f} yuan\n"
            f"Annual Costs: {self.annual_costs:,.0f} yuan\n"
            f"Annual Savings: {self.annual_savings:,.0f} yuan\n"
            f"Payback Period: {self.payback_months} months\n"
            f"5-Year ROI: {self.five_year_roi:.1f}%"
        )


class DeploymentManager:
    """
    Smart Agriculture Deployment Manager.
    مدير نشر الزراعة الذكية.

    Manages deployment configurations and provides ROI analysis
    for smart agriculture system implementations.

    يدير تكوينات النشر ويوفر تحليل العائد على الاستثمار
    لتطبيقات نظام الزراعة الذكية.

    Deployment modes:
    - SaaS Mode: ~8000 yuan/year, Web/App lightweight access
      وضع SaaS: ~8000 يوان/سنة، وصول خفيف عبر الويب/التطبيق
    - Custom Mode: 3-5k one-time, local server + edge gateway
      الوضع المخصص: 3-5 آلاف لمرة واحدة، خادم محلي + بوابة حافة

    Example usage:
        manager = DeploymentManager()
        config = manager.configure_saas(tier=ServiceTier.STANDARD)
        lowcode = manager.setup_low_code_engine()
        roi = manager.get_roi_analysis()
    """

    # Pricing tiers (yuan)
    SAAS_PRICING = {
        ServiceTier.BASIC: 4000,
        ServiceTier.STANDARD: 8000,
        ServiceTier.PROFESSIONAL: 15000,
        ServiceTier.ENTERPRISE: 30000,
    }

    CUSTOM_PRICING = {
        "basic": 3000,
        "standard": 4000,
        "advanced": 5000,
    }

    def __init__(self):
        """
        Initialize the deployment manager.
        تهيئة مدير النشر.
        """
        self._mode: DeploymentMode | None = None
        self._saas_config: SaaSConfig | None = None
        self._custom_config: CustomConfig | None = None
        self._lowcode_config: LowCodeConfig | None = None
        self._maintenance_plan: MaintenancePlan | None = None
        self._deployment_date: datetime | None = None

        # Default savings estimates (yuan/year per hectare)
        self._savings_estimates = {
            "fertilizer": 200,  # From PID controller
            "water": 150,
            "labor": 300,
            "yield_increase": 500,
            "premium_value": 250,  # From blockchain
        }

    def configure_saas(
        self,
        tier: ServiceTier = ServiceTier.STANDARD,
        max_fields: int | None = None,
        max_sensors: int | None = None,
    ) -> SaaSConfig:
        """
        Configure SaaS deployment mode.
        تكوين وضع نشر SaaS.

        SaaS deployment provides lightweight web and mobile access
        with no hardware requirements.

        نشر SaaS يوفر وصول خفيف عبر الويب والجوال
        بدون متطلبات أجهزة.

        Args:
            tier: Service tier level | مستوى طبقة الخدمة
            max_fields: Maximum fields (optional override)
            max_sensors: Maximum sensors (optional override)

        Returns:
            SaaSConfig: SaaS configuration | تكوين SaaS
        """
        self._mode = DeploymentMode.SAAS
        annual_cost = self.SAAS_PRICING.get(tier, 8000)

        # Tier-based limits
        tier_limits = {
            ServiceTier.BASIC: {"fields": 20, "sensors": 50},
            ServiceTier.STANDARD: {"fields": 50, "sensors": 200},
            ServiceTier.PROFESSIONAL: {"fields": 200, "sensors": 500},
            ServiceTier.ENTERPRISE: {"fields": 1000, "sensors": 5000},
        }

        limits = tier_limits.get(tier, tier_limits[ServiceTier.STANDARD])

        self._saas_config = SaaSConfig(
            annual_cost_yuan=annual_cost,
            tier=tier,
            max_fields=max_fields or limits["fields"],
            max_sensors=max_sensors or limits["sensors"],
            support_level="24/7" if tier == ServiceTier.ENTERPRISE else "email",
        )

        return self._saas_config

    def configure_custom(
        self,
        complexity: str = "standard",
        include_hardware: bool = True,
        customizations: list[str] | None = None,
    ) -> CustomConfig:
        """
        Configure custom deployment mode.
        تكوين وضع النشر المخصص.

        Custom deployment includes local server and edge gateway
        for full offline capability.

        النشر المخصص يشمل خادم محلي وبوابة حافة
        للقدرة الكاملة بدون اتصال.

        Args:
            complexity: 'basic', 'standard', or 'advanced' | التعقيد
            include_hardware: Include hardware in cost | تضمين الأجهزة
            customizations: List of required customizations | التخصيصات المطلوبة

        Returns:
            CustomConfig: Custom deployment configuration
        """
        self._mode = DeploymentMode.CUSTOM
        one_time_cost = self.CUSTOM_PRICING.get(complexity, 4000)

        hardware_cost = 0.0
        if include_hardware:
            hardware_costs = {
                "basic": 1500,
                "standard": 2500,
                "advanced": 4000,
            }
            hardware_cost = hardware_costs.get(complexity, 2500)

        self._custom_config = CustomConfig(
            one_time_cost_yuan=one_time_cost,
            hardware_cost_yuan=hardware_cost,
            includes_server=True,
            includes_gateway=True,
            customizations=customizations or [],
        )

        return self._custom_config

    def setup_low_code_engine(
        self,
        threshold_configs: list[dict[str, Any]] | None = None,
    ) -> LowCodeConfig:
        """
        Setup low-code engine for drag-drop threshold customization.
        إعداد محرك الكود المنخفض لتخصيص العتبات بالسحب والإفلات.

        Enables farmers to customize thresholds without coding
        through a visual interface.

        يمكن المزارعين من تخصيص العتبات بدون برمجة
        من خلال واجهة مرئية.

        Args:
            threshold_configs: Initial threshold configurations

        Returns:
            LowCodeConfig: Low-code engine configuration
        """
        default_thresholds = [
            {
                "id": "temp_low",
                "name": "Low Temperature Alert",
                "name_ar": "تنبيه درجة الحرارة المنخفضة",
                "parameter": "temperature",
                "operator": "<",
                "default_value": 10,
                "min_value": 0,
                "max_value": 20,
                "unit": "°C",
                "action": "start_heating",
            },
            {
                "id": "temp_high",
                "name": "High Temperature Alert",
                "name_ar": "تنبيه درجة الحرارة المرتفعة",
                "parameter": "temperature",
                "operator": ">",
                "default_value": 35,
                "min_value": 25,
                "max_value": 45,
                "unit": "°C",
                "action": "start_cooling",
            },
            {
                "id": "humidity_high",
                "name": "High Humidity Alert",
                "name_ar": "تنبيه الرطوبة العالية",
                "parameter": "humidity",
                "operator": ">",
                "default_value": 90,
                "min_value": 70,
                "max_value": 100,
                "unit": "%",
                "action": "activate_ventilation",
            },
            {
                "id": "soil_moisture_low",
                "name": "Low Soil Moisture Alert",
                "name_ar": "تنبيه رطوبة التربة المنخفضة",
                "parameter": "soil_moisture",
                "operator": "<",
                "default_value": 30,
                "min_value": 10,
                "max_value": 50,
                "unit": "%",
                "action": "start_irrigation",
            },
        ]

        default_templates = [
            {
                "id": "greenhouse_basic",
                "name": "Basic Greenhouse Control",
                "name_ar": "التحكم الأساسي في الدفيئة",
                "description": "Standard temperature and humidity control",
                "rules": ["temp_low", "temp_high", "humidity_high"],
            },
            {
                "id": "irrigation_smart",
                "name": "Smart Irrigation",
                "name_ar": "الري الذكي",
                "description": "Soil moisture-based irrigation control",
                "rules": ["soil_moisture_low"],
            },
            {
                "id": "full_automation",
                "name": "Full Greenhouse Automation",
                "name_ar": "الأتمتة الكاملة للدفيئة",
                "description": "Complete environmental control",
                "rules": ["temp_low", "temp_high", "humidity_high", "soil_moisture_low"],
            },
        ]

        self._lowcode_config = LowCodeConfig(
            threshold_configs=threshold_configs or default_thresholds,
            rule_templates=default_templates,
            custom_widgets=[
                {
                    "id": "sensor_overview",
                    "name": "Sensor Overview",
                    "name_ar": "نظرة عامة على المستشعرات",
                    "type": "dashboard",
                },
                {
                    "id": "alert_history",
                    "name": "Alert History",
                    "name_ar": "سجل التنبيهات",
                    "type": "timeline",
                },
            ],
            automation_flows=[],
        )

        return self._lowcode_config

    def calculate_maintenance_cost(
        self,
        include_updates: bool = True,
        include_support: bool = True,
        visits_per_year: int = 2,
    ) -> MaintenancePlan:
        """
        Calculate annual maintenance cost.
        حساب تكلفة الصيانة السنوية.

        Default maintenance: ~500 yuan/year | الصيانة الافتراضية: ~500 يوان/سنة

        Args:
            include_updates: Include software updates | تضمين تحديثات البرامج
            include_support: Include technical support | تضمين الدعم الفني
            visits_per_year: Number of on-site visits | عدد زيارات الموقع

        Returns:
            MaintenancePlan: Maintenance plan details
        """
        base_cost = 300.0

        if include_updates:
            base_cost += 100.0
        if include_support:
            base_cost += 100.0

        # Additional cost per site visit
        visit_cost = visits_per_year * 100

        self._maintenance_plan = MaintenancePlan(
            annual_cost_yuan=base_cost + visit_cost,
            includes_updates=include_updates,
            includes_support=include_support,
            response_time_hours=24 if include_support else 72,
            visits_per_year=visits_per_year,
        )

        return self._maintenance_plan

    def get_roi_analysis(
        self,
        area_hectares: float = 10.0,
        years: int = 5,
    ) -> ROIAnalysis:
        """
        Generate ROI analysis for the deployment.
        إنشاء تحليل العائد على الاستثمار للنشر.

        Args:
            area_hectares: Farm area in hectares | مساحة المزرعة بالهكتار
            years: Analysis period in years | فترة التحليل بالسنوات

        Returns:
            ROIAnalysis: Comprehensive ROI analysis
        """
        # Calculate initial investment
        initial = 0.0
        annual_costs = 0.0

        if self._mode == DeploymentMode.SAAS and self._saas_config:
            annual_costs = self._saas_config.annual_cost_yuan
        elif self._mode == DeploymentMode.CUSTOM and self._custom_config:
            initial = self._custom_config.total_cost

        # Add maintenance costs
        if self._maintenance_plan:
            annual_costs += self._maintenance_plan.annual_cost_yuan
        else:
            annual_costs += 500.0  # Default maintenance

        # Calculate annual savings (per hectare * area)
        annual_savings = sum(self._savings_estimates.values()) * area_hectares

        # Calculate benefits breakdown
        benefits = {f"{k}_savings": v * area_hectares for k, v in self._savings_estimates.items()}

        # Calculate payback period
        net_annual_benefit = annual_savings - annual_costs
        if net_annual_benefit > 0:
            payback_months = int((initial / net_annual_benefit) * 12) if initial > 0 else 0
        else:
            payback_months = -1  # Never pays back

        # Calculate 5-year ROI
        total_savings = annual_savings * years
        total_costs = initial + (annual_costs * years)
        if total_costs > 0:
            five_year_roi = ((total_savings - total_costs) / total_costs) * 100
        else:
            five_year_roi = 0.0

        return ROIAnalysis(
            initial_investment=initial,
            annual_costs=annual_costs,
            annual_savings=annual_savings,
            payback_months=max(0, payback_months),
            five_year_roi=round(five_year_roi, 1),
            benefits=benefits,
        )

    def get_deployment_summary(self, language: str = "en") -> str:
        """
        Generate deployment configuration summary.
        إنشاء ملخص تكوين النشر.

        Args:
            language: Output language ('en' or 'ar')

        Returns:
            str: Formatted summary
        """
        if language == "ar":
            return self._get_summary_ar()
        return self._get_summary_en()

    def _get_summary_en(self) -> str:
        """Generate English summary."""
        lines = ["Smart Agriculture Deployment Summary", "=" * 40]

        if self._mode == DeploymentMode.SAAS and self._saas_config:
            lines.extend(
                [
                    "Mode: SaaS (Cloud)",
                    f"Tier: {self._saas_config.tier.value.title()}",
                    f"Annual Cost: {self._saas_config.annual_cost_yuan:,.0f} yuan/year",
                    f"Max Fields: {self._saas_config.max_fields}",
                    f"Max Sensors: {self._saas_config.max_sensors}",
                    f"Features: {len(self._saas_config.features)}",
                ]
            )
        elif self._mode == DeploymentMode.CUSTOM and self._custom_config:
            lines.extend(
                [
                    "Mode: Custom (On-Premise)",
                    f"One-time Cost: {self._custom_config.one_time_cost_yuan:,.0f} yuan",
                    f"Hardware Cost: {self._custom_config.hardware_cost_yuan:,.0f} yuan",
                    f"Total Initial: {self._custom_config.total_cost:,.0f} yuan",
                    f"Local Server: {'Yes' if self._custom_config.includes_server else 'No'}",
                    f"Edge Gateway: {'Yes' if self._custom_config.includes_gateway else 'No'}",
                ]
            )

        if self._maintenance_plan:
            lines.extend(
                [
                    "",
                    "Maintenance Plan:",
                    f"  Annual Cost: {self._maintenance_plan.annual_cost_yuan:,.0f} yuan/year",
                    f"  Updates: {'Included' if self._maintenance_plan.includes_updates else 'Not included'}",
                    f"  Support: {'Included' if self._maintenance_plan.includes_support else 'Not included'}",
                ]
            )

        return "\n".join(lines)

    def _get_summary_ar(self) -> str:
        """Generate Arabic summary."""
        lines = ["ملخص نشر الزراعة الذكية", "=" * 40]

        if self._mode == DeploymentMode.SAAS and self._saas_config:
            lines.extend(
                [
                    "الوضع: SaaS (سحابي)",
                    f"الطبقة: {self._saas_config.tier.value}",
                    f"التكلفة السنوية: {self._saas_config.annual_cost_yuan:,.0f} يوان/سنة",
                    f"الحد الأقصى للحقول: {self._saas_config.max_fields}",
                    f"الحد الأقصى للمستشعرات: {self._saas_config.max_sensors}",
                ]
            )
        elif self._mode == DeploymentMode.CUSTOM and self._custom_config:
            lines.extend(
                [
                    "الوضع: مخصص (محلي)",
                    f"تكلفة لمرة واحدة: {self._custom_config.one_time_cost_yuan:,.0f} يوان",
                    f"تكلفة الأجهزة: {self._custom_config.hardware_cost_yuan:,.0f} يوان",
                    f"الإجمالي الأولي: {self._custom_config.total_cost:,.0f} يوان",
                ]
            )

        if self._maintenance_plan:
            lines.extend(
                [
                    "",
                    "خطة الصيانة:",
                    f"  التكلفة السنوية: {self._maintenance_plan.annual_cost_yuan:,.0f} يوان/سنة",
                ]
            )

        return "\n".join(lines)

    def export_configuration(self) -> dict[str, Any]:
        """
        Export full configuration as dictionary.
        تصدير التكوين الكامل كقاموس.
        """
        config = {
            "mode": self._mode.value if self._mode else None,
            "deployment_date": self._deployment_date.isoformat() if self._deployment_date else None,
        }

        if self._saas_config:
            config["saas"] = {
                "annual_cost": self._saas_config.annual_cost_yuan,
                "tier": self._saas_config.tier.value,
                "max_fields": self._saas_config.max_fields,
                "max_sensors": self._saas_config.max_sensors,
                "features": self._saas_config.features,
            }

        if self._custom_config:
            config["custom"] = {
                "one_time_cost": self._custom_config.one_time_cost_yuan,
                "hardware_cost": self._custom_config.hardware_cost_yuan,
                "includes_server": self._custom_config.includes_server,
                "includes_gateway": self._custom_config.includes_gateway,
            }

        if self._lowcode_config:
            config["lowcode"] = {
                "threshold_count": len(self._lowcode_config.threshold_configs),
                "template_count": len(self._lowcode_config.rule_templates),
            }

        if self._maintenance_plan:
            config["maintenance"] = {
                "annual_cost": self._maintenance_plan.annual_cost_yuan,
                "includes_updates": self._maintenance_plan.includes_updates,
                "includes_support": self._maintenance_plan.includes_support,
            }

        return config

    def get_pricing_table(self, language: str = "en") -> str:
        """
        Generate pricing comparison table.
        إنشاء جدول مقارنة الأسعار.
        """
        if language == "ar":
            header = "الطبقة          | السعر السنوي | الحقول | المستشعرات"
            separator = "-" * 55
            rows = [
                "أساسي          | 4,000 يوان   | 20     | 50",
                "قياسي          | 8,000 يوان   | 50     | 200",
                "احترافي        | 15,000 يوان  | 200    | 500",
                "مؤسسي         | 30,000 يوان  | 1000   | 5000",
            ]
        else:
            header = "Tier           | Annual Price | Fields | Sensors"
            separator = "-" * 55
            rows = [
                "Basic          | 4,000 yuan   | 20     | 50",
                "Standard       | 8,000 yuan   | 50     | 200",
                "Professional   | 15,000 yuan  | 200    | 500",
                "Enterprise     | 30,000 yuan  | 1000   | 5000",
            ]

        return "\n".join([header, separator] + rows)
