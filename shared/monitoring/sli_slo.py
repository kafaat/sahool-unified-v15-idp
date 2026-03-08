"""
SAHOOL Platform - SLI/SLO Definitions
تعريفات مؤشرات ومستويات الخدمة

Service Level Indicators (SLIs) and Service Level Objectives (SLOs)
for the SAHOOL Agricultural Intelligence Platform.

Based on Google SRE principles and agricultural domain requirements.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class ServiceTier(StrEnum):
    """Service tier classification | تصنيف مستوى الخدمة"""

    CRITICAL = "critical"  # Core infrastructure (Postgres, Redis, NATS)
    ESSENTIAL = "essential"  # Core services (field-management, user-service)
    STANDARD = "standard"  # Application services (advisory, notifications)
    ANALYTICS = "analytics"  # Analytics/ML services (NDVI, AI)
    EDGE = "edge"  # Edge/IoT services


class SLIType(StrEnum):
    """SLI measurement type | نوع قياس مؤشر الخدمة"""

    AVAILABILITY = "availability"  # Service uptime
    LATENCY = "latency"  # Response time
    ERROR_RATE = "error_rate"  # Error percentage
    THROUGHPUT = "throughput"  # Requests per second
    SATURATION = "saturation"  # Resource usage
    FRESHNESS = "freshness"  # Data age
    CORRECTNESS = "correctness"  # Data accuracy


@dataclass
class SLI:
    """
    Service Level Indicator definition.
    تعريف مؤشر مستوى الخدمة.
    """

    name: str
    name_ar: str
    type: SLIType
    description: str
    description_ar: str
    prometheus_query: str
    unit: str = ""
    good_events_query: str = ""
    total_events_query: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "type": self.type.value,
            "description": self.description,
            "prometheus_query": self.prometheus_query,
            "unit": self.unit,
        }


@dataclass
class SLO:
    """
    Service Level Objective definition.
    تعريف هدف مستوى الخدمة.
    """

    name: str
    name_ar: str
    sli: SLI
    target: float
    window: str  # e.g., "30d", "7d", "1d"
    tier: ServiceTier
    alert_burn_rate_1h: float = 14.4  # 1h burn rate for critical alert
    alert_burn_rate_6h: float = 6.0  # 6h burn rate for warning alert
    alert_burn_rate_3d: float = 1.0  # 3d burn rate for ticket

    @property
    def error_budget(self) -> float:
        """Calculate error budget (1 - target)"""
        return 1 - self.target

    @property
    def error_budget_percent(self) -> float:
        """Error budget as percentage"""
        return self.error_budget * 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "name_ar": self.name_ar,
            "target": self.target,
            "target_percent": self.target * 100,
            "error_budget_percent": self.error_budget_percent,
            "window": self.window,
            "tier": self.tier.value,
            "sli": self.sli.to_dict(),
        }


@dataclass
class ServiceSLOs:
    """
    Collection of SLOs for a service.
    مجموعة أهداف مستوى الخدمة لخدمة معينة.
    """

    service_name: str
    service_name_ar: str
    tier: ServiceTier
    slos: list[SLO] = field(default_factory=list)

    def add_slo(self, slo: SLO) -> None:
        self.slos.append(slo)

    def to_dict(self) -> dict[str, Any]:
        return {
            "service_name": self.service_name,
            "service_name_ar": self.service_name_ar,
            "tier": self.tier.value,
            "slos": [slo.to_dict() for slo in self.slos],
        }


# ═══════════════════════════════════════════════════════════════════════════════
# Standard SLI Definitions | تعريفات مؤشرات الخدمة القياسية
# ═══════════════════════════════════════════════════════════════════════════════

# Availability SLIs
AVAILABILITY_SLI = SLI(
    name="service_availability",
    name_ar="توفر الخدمة",
    type=SLIType.AVAILABILITY,
    description="Percentage of time the service is available",
    description_ar="نسبة وقت توفر الخدمة",
    prometheus_query='avg_over_time(up{{job="{service}"}}[{window}])',
    unit="ratio",
    good_events_query='sum(up{{job="{service}"}})',
    total_events_query='count(up{{job="{service}"}})',
)

# Latency SLIs (P50, P95, P99)
LATENCY_P50_SLI = SLI(
    name="latency_p50",
    name_ar="زمن الاستجابة P50",
    type=SLIType.LATENCY,
    description="50th percentile request latency",
    description_ar="زمن الاستجابة في النسبة المئوية 50",
    prometheus_query="""
        histogram_quantile(0.50,
            sum by (le) (
                rate(http_request_duration_seconds_bucket{{job="{service}"}}[{window}])
            )
        )
    """,
    unit="seconds",
)

LATENCY_P95_SLI = SLI(
    name="latency_p95",
    name_ar="زمن الاستجابة P95",
    type=SLIType.LATENCY,
    description="95th percentile request latency",
    description_ar="زمن الاستجابة في النسبة المئوية 95",
    prometheus_query="""
        histogram_quantile(0.95,
            sum by (le) (
                rate(http_request_duration_seconds_bucket{{job="{service}"}}[{window}])
            )
        )
    """,
    unit="seconds",
    good_events_query="""
        sum(rate(http_request_duration_seconds_bucket{{job="{service}",le="0.5"}}[{window}]))
    """,
    total_events_query="""
        sum(rate(http_request_duration_seconds_count{{job="{service}"}}[{window}]))
    """,
)

LATENCY_P99_SLI = SLI(
    name="latency_p99",
    name_ar="زمن الاستجابة P99",
    type=SLIType.LATENCY,
    description="99th percentile request latency",
    description_ar="زمن الاستجابة في النسبة المئوية 99",
    prometheus_query="""
        histogram_quantile(0.99,
            sum by (le) (
                rate(http_request_duration_seconds_bucket{{job="{service}"}}[{window}])
            )
        )
    """,
    unit="seconds",
)

# Error Rate SLI
ERROR_RATE_SLI = SLI(
    name="error_rate",
    name_ar="معدل الأخطاء",
    type=SLIType.ERROR_RATE,
    description="Percentage of requests resulting in errors (5xx)",
    description_ar="نسبة الطلبات التي تنتج أخطاء (5xx)",
    prometheus_query="""
        (
            sum(rate(http_requests_total{{job="{service}",status=~"5.."}}[{window}]))
            /
            sum(rate(http_requests_total{{job="{service}"}}[{window}]))
        )
    """,
    unit="ratio",
    good_events_query="""
        sum(rate(http_requests_total{{job="{service}",status!~"5.."}}[{window}]))
    """,
    total_events_query="""
        sum(rate(http_requests_total{{job="{service}"}}[{window}]))
    """,
)

# Throughput SLI
THROUGHPUT_SLI = SLI(
    name="throughput",
    name_ar="معدل الإنتاجية",
    type=SLIType.THROUGHPUT,
    description="Requests processed per second",
    description_ar="الطلبات المعالجة في الثانية",
    prometheus_query='sum(rate(http_requests_total{{job="{service}"}}[{window}]))',
    unit="requests/second",
)

# Saturation SLI (Resource Usage)
CPU_SATURATION_SLI = SLI(
    name="cpu_saturation",
    name_ar="إشباع المعالج",
    type=SLIType.SATURATION,
    description="CPU utilization percentage",
    description_ar="نسبة استخدام المعالج",
    prometheus_query="""
        avg(rate(process_cpu_seconds_total{{job="{service}"}}[{window}])) * 100
    """,
    unit="percent",
)

MEMORY_SATURATION_SLI = SLI(
    name="memory_saturation",
    name_ar="إشباع الذاكرة",
    type=SLIType.SATURATION,
    description="Memory utilization percentage",
    description_ar="نسبة استخدام الذاكرة",
    prometheus_query="""
        (
            process_resident_memory_bytes{{job="{service}"}}
            /
            machine_memory_bytes
        ) * 100
    """,
    unit="percent",
)

# ═══════════════════════════════════════════════════════════════════════════════
# Agricultural Domain SLIs | مؤشرات الخدمة للمجال الزراعي
# ═══════════════════════════════════════════════════════════════════════════════

# NDVI Data Freshness
NDVI_FRESHNESS_SLI = SLI(
    name="ndvi_data_freshness",
    name_ar="حداثة بيانات NDVI",
    type=SLIType.FRESHNESS,
    description="Age of latest NDVI data in hours",
    description_ar="عمر أحدث بيانات NDVI بالساعات",
    prometheus_query="""
        (time() - ndvi_last_update_timestamp_seconds) / 3600
    """,
    unit="hours",
)

# Weather Data Freshness
WEATHER_FRESHNESS_SLI = SLI(
    name="weather_data_freshness",
    name_ar="حداثة بيانات الطقس",
    type=SLIType.FRESHNESS,
    description="Age of latest weather data in minutes",
    description_ar="عمر أحدث بيانات الطقس بالدقائق",
    prometheus_query="""
        (time() - weather_last_update_timestamp_seconds) / 60
    """,
    unit="minutes",
)

# Advisory Accuracy (based on user feedback)
ADVISORY_CORRECTNESS_SLI = SLI(
    name="advisory_correctness",
    name_ar="دقة التوصيات",
    type=SLIType.CORRECTNESS,
    description="Percentage of accurate advisory recommendations",
    description_ar="نسبة التوصيات الاستشارية الدقيقة",
    prometheus_query="""
        (
            sum(advisory_feedback_positive_total)
            /
            sum(advisory_feedback_total)
        )
    """,
    unit="ratio",
)

# IoT Sensor Data Freshness
SENSOR_FRESHNESS_SLI = SLI(
    name="sensor_data_freshness",
    name_ar="حداثة بيانات المستشعرات",
    type=SLIType.FRESHNESS,
    description="Age of latest sensor readings in minutes",
    description_ar="عمر أحدث قراءات المستشعرات بالدقائق",
    prometheus_query="""
        avg(time() - iot_sensor_last_reading_timestamp_seconds) / 60
    """,
    unit="minutes",
)

# AI Model Inference Latency
AI_INFERENCE_LATENCY_SLI = SLI(
    name="ai_inference_latency",
    name_ar="زمن استدلال الذكاء الاصطناعي",
    type=SLIType.LATENCY,
    description="AI model inference latency (P95)",
    description_ar="زمن استدلال نموذج الذكاء الاصطناعي (P95)",
    prometheus_query="""
        histogram_quantile(0.95,
            sum by (le) (
                rate(ai_inference_duration_seconds_bucket{{job="{service}"}}[{window}])
            )
        )
    """,
    unit="seconds",
)


# ═══════════════════════════════════════════════════════════════════════════════
# SLO Definitions by Service Tier | تعريفات أهداف الخدمة حسب المستوى
# ═══════════════════════════════════════════════════════════════════════════════


def create_critical_service_slos(service_name: str, service_name_ar: str) -> ServiceSLOs:
    """
    Create SLOs for critical infrastructure services.
    إنشاء أهداف مستوى الخدمة للخدمات الحرجة.

    Target: 99.9% availability (8.76 hours downtime/year)
    """
    service_slos = ServiceSLOs(
        service_name=service_name,
        service_name_ar=service_name_ar,
        tier=ServiceTier.CRITICAL,
    )

    # 99.9% Availability (3 nines)
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_availability",
            name_ar=f"توفر {service_name_ar}",
            sli=AVAILABILITY_SLI,
            target=0.999,
            window="30d",
            tier=ServiceTier.CRITICAL,
        )
    )

    # P95 Latency < 100ms
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_latency_p95",
            name_ar=f"زمن استجابة {service_name_ar} P95",
            sli=LATENCY_P95_SLI,
            target=0.999,  # 99.9% of requests < 100ms
            window="30d",
            tier=ServiceTier.CRITICAL,
        )
    )

    # Error Rate < 0.1%
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_error_rate",
            name_ar=f"معدل أخطاء {service_name_ar}",
            sli=ERROR_RATE_SLI,
            target=0.999,  # < 0.1% errors
            window="30d",
            tier=ServiceTier.CRITICAL,
        )
    )

    return service_slos


def create_essential_service_slos(service_name: str, service_name_ar: str) -> ServiceSLOs:
    """
    Create SLOs for essential services.
    إنشاء أهداف مستوى الخدمة للخدمات الأساسية.

    Target: 99.5% availability (43.8 hours downtime/year)
    """
    service_slos = ServiceSLOs(
        service_name=service_name,
        service_name_ar=service_name_ar,
        tier=ServiceTier.ESSENTIAL,
    )

    # 99.5% Availability
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_availability",
            name_ar=f"توفر {service_name_ar}",
            sli=AVAILABILITY_SLI,
            target=0.995,
            window="30d",
            tier=ServiceTier.ESSENTIAL,
        )
    )

    # P95 Latency < 300ms
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_latency_p95",
            name_ar=f"زمن استجابة {service_name_ar} P95",
            sli=LATENCY_P95_SLI,
            target=0.99,  # 99% of requests < 300ms
            window="30d",
            tier=ServiceTier.ESSENTIAL,
        )
    )

    # Error Rate < 0.5%
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_error_rate",
            name_ar=f"معدل أخطاء {service_name_ar}",
            sli=ERROR_RATE_SLI,
            target=0.995,
            window="30d",
            tier=ServiceTier.ESSENTIAL,
        )
    )

    return service_slos


def create_standard_service_slos(service_name: str, service_name_ar: str) -> ServiceSLOs:
    """
    Create SLOs for standard application services.
    إنشاء أهداف مستوى الخدمة للخدمات القياسية.

    Target: 99% availability (87.6 hours downtime/year)
    """
    service_slos = ServiceSLOs(
        service_name=service_name,
        service_name_ar=service_name_ar,
        tier=ServiceTier.STANDARD,
    )

    # 99% Availability (2 nines)
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_availability",
            name_ar=f"توفر {service_name_ar}",
            sli=AVAILABILITY_SLI,
            target=0.99,
            window="30d",
            tier=ServiceTier.STANDARD,
        )
    )

    # P95 Latency < 500ms
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_latency_p95",
            name_ar=f"زمن استجابة {service_name_ar} P95",
            sli=LATENCY_P95_SLI,
            target=0.95,  # 95% of requests < 500ms
            window="30d",
            tier=ServiceTier.STANDARD,
        )
    )

    # Error Rate < 1%
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_error_rate",
            name_ar=f"معدل أخطاء {service_name_ar}",
            sli=ERROR_RATE_SLI,
            target=0.99,
            window="30d",
            tier=ServiceTier.STANDARD,
        )
    )

    return service_slos


def create_analytics_service_slos(service_name: str, service_name_ar: str) -> ServiceSLOs:
    """
    Create SLOs for analytics/ML services.
    إنشاء أهداف مستوى الخدمة لخدمات التحليلات والتعلم الآلي.

    Target: 95% availability with higher latency tolerance
    """
    service_slos = ServiceSLOs(
        service_name=service_name,
        service_name_ar=service_name_ar,
        tier=ServiceTier.ANALYTICS,
    )

    # 95% Availability
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_availability",
            name_ar=f"توفر {service_name_ar}",
            sli=AVAILABILITY_SLI,
            target=0.95,
            window="30d",
            tier=ServiceTier.ANALYTICS,
        )
    )

    # P95 Latency < 5s (ML inference can be slow)
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_latency_p95",
            name_ar=f"زمن استجابة {service_name_ar} P95",
            sli=LATENCY_P95_SLI,
            target=0.90,  # 90% of requests < 5s
            window="30d",
            tier=ServiceTier.ANALYTICS,
        )
    )

    # Error Rate < 2%
    service_slos.add_slo(
        SLO(
            name=f"{service_name}_error_rate",
            name_ar=f"معدل أخطاء {service_name_ar}",
            sli=ERROR_RATE_SLI,
            target=0.98,
            window="30d",
            tier=ServiceTier.ANALYTICS,
        )
    )

    return service_slos


# ═══════════════════════════════════════════════════════════════════════════════
# SAHOOL Platform SLO Registry | سجل أهداف الخدمة لمنصة سهول
# ═══════════════════════════════════════════════════════════════════════════════


class SAHOOLSLORegistry:
    """
    Central registry for all SAHOOL platform SLOs.
    السجل المركزي لجميع أهداف مستوى الخدمة لمنصة سهول.
    """

    def __init__(self):
        self.services: dict[str, ServiceSLOs] = {}
        self._initialize_slos()

    def _initialize_slos(self) -> None:
        """Initialize SLOs for all SAHOOL services."""

        # Critical Infrastructure
        self.services["postgres"] = create_critical_service_slos("postgres", "قاعدة البيانات PostgreSQL")
        self.services["redis"] = create_critical_service_slos("redis", "ذاكرة التخزين المؤقت Redis")
        self.services["nats"] = create_critical_service_slos("nats", "نظام الرسائل NATS")

        # Essential Services
        self.services["field-management-service"] = create_essential_service_slos(
            "field-management-service", "خدمة إدارة الحقول"
        )
        self.services["user-service"] = create_essential_service_slos("user-service", "خدمة المستخدمين")
        self.services["kong"] = create_essential_service_slos("kong", "بوابة API")

        # Standard Application Services
        self.services["weather-service"] = create_standard_service_slos("weather-service", "خدمة الطقس")
        self.services["advisory-service"] = create_standard_service_slos("advisory-service", "خدمة الاستشارات")
        self.services["notification-service"] = create_standard_service_slos("notification-service", "خدمة الإشعارات")
        self.services["irrigation-smart"] = create_standard_service_slos("irrigation-smart", "خدمة الري الذكي")
        self.services["task-service"] = create_standard_service_slos("task-service", "خدمة المهام")

        # Analytics/ML Services
        self.services["vegetation-analysis-service"] = create_analytics_service_slos(
            "vegetation-analysis-service", "خدمة تحليل الغطاء النباتي"
        )
        self.services["crop-intelligence-service"] = create_analytics_service_slos(
            "crop-intelligence-service", "خدمة ذكاء المحاصيل"
        )
        self.services["yolo26-vision-service"] = create_analytics_service_slos(
            "yolo26-vision-service", "خدمة الرؤية الحاسوبية"
        )
        self.services["yield-engine"] = create_analytics_service_slos("yield-engine", "محرك التنبؤ بالإنتاجية")
        self.services["terrain-core-service"] = create_analytics_service_slos(
            "terrain-core-service", "خدمة تحليل التضاريس"
        )
        self.services["hydrology-service"] = create_analytics_service_slos("hydrology-service", "خدمة الهيدرولوجيا")

    def get_service_slos(self, service_name: str) -> ServiceSLOs | None:
        """Get SLOs for a specific service."""
        return self.services.get(service_name)

    def get_all_slos(self) -> dict[str, ServiceSLOs]:
        """Get all service SLOs."""
        return self.services

    def get_slos_by_tier(self, tier: ServiceTier) -> list[ServiceSLOs]:
        """Get all SLOs for a specific tier."""
        return [slo for slo in self.services.values() if slo.tier == tier]

    def export_prometheus_rules(self) -> str:
        """
        Export SLO burn rate alerting rules for Prometheus.
        تصدير قواعد تنبيه معدل حرق SLO لـ Prometheus.
        """
        rules = ["# SAHOOL SLO Burn Rate Alerting Rules", "# Auto-generated", ""]
        rules.append("groups:")

        for service_name, service_slos in self.services.items():
            rules.append(f"  - name: slo_{service_name.replace('-', '_')}")
            rules.append("    rules:")

            for slo in service_slos.slos:
                # Multi-window burn rate alerting
                rules.append(f"      # {slo.name}: {slo.target * 100}% target")
                rules.append(f"      - alert: SLOBurnRateCritical_{service_name.replace('-', '_')}")
                rules.append("        expr: |")
                rules.append(f"          # 1h burn rate > {slo.alert_burn_rate_1h}")
                rules.append(f"          (1 - {slo.sli.prometheus_query.format(service=service_name, window='1h')})")
                rules.append(f"          / {slo.error_budget}")
                rules.append(f"          > {slo.alert_burn_rate_1h}")
                rules.append("        for: 2m")
                rules.append("        labels:")
                rules.append("          severity: critical")
                rules.append(f"          service: {service_name}")
                rules.append(f"          slo: {slo.name}")
                rules.append("        annotations:")
                rules.append(f'          summary: "SLO burn rate critical for {service_name}"')
                rules.append(f'          summary_ar: "معدل حرق SLO حرج لـ {service_slos.service_name_ar}"')
                rules.append("")

        return "\n".join(rules)


# Global SLO Registry instance
_slo_registry: SAHOOLSLORegistry | None = None


def get_slo_registry() -> SAHOOLSLORegistry:
    """Get the global SLO registry instance."""
    global _slo_registry
    if _slo_registry is None:
        _slo_registry = SAHOOLSLORegistry()
    return _slo_registry


def get_service_slos(service_name: str) -> ServiceSLOs | None:
    """Convenience function to get SLOs for a service."""
    return get_slo_registry().get_service_slos(service_name)
