#!/usr/bin/env python3
"""
SAHOOL Platform - OpenAPI Documentation Aggregator
Fetches and merges OpenAPI specifications from all 39 microservices
Organized by package tier: Starter, Professional, Enterprise
"""

import json
import logging
import sys
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

import requests
import yaml

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


@dataclass
class ServiceConfig:
    """Configuration for a microservice"""

    name: str
    port: int
    tier: str  # starter, professional, enterprise
    type: str  # python (FastAPI) or nestjs
    description_en: str
    description_ar: str
    container_name: str = ""

    @property
    def openapi_url(self) -> str:
        """Get the OpenAPI spec URL based on service type"""
        base_url = f"http://localhost:{self.port}"
        if self.type == "nestjs":
            return f"{base_url}/api-json"
        else:  # python/fastapi
            return f"{base_url}/openapi.json"


# Define all 39 services across three tiers
SERVICES = [
    # ═══════════════════════════════════════════════════════════════
    # STARTER PACKAGE - حزمة سهول المبتدئة
    # ═══════════════════════════════════════════════════════════════
    ServiceConfig(
        name="field_core",
        port=3000,
        tier="starter",
        type="nestjs",
        description_en="Field Management Core - Manage agricultural fields and boundaries",
        description_ar="إدارة الحقول الزراعية - إدارة الحقول والحدود الزراعية",
    ),
    ServiceConfig(
        name="weather_core",
        port=8108,
        tier="starter",
        type="python",
        description_en="Weather Service - Real-time weather data and forecasts",
        description_ar="خدمة الطقس - بيانات الطقس والتنبؤات في الوقت الفعلي",
    ),
    ServiceConfig(
        name="astronomical_calendar",
        port=8111,
        tier="starter",
        type="python",
        description_en="Yemeni Agricultural Astronomical Calendar",
        description_ar="التقويم الفلكي الزراعي اليمني",
    ),
    ServiceConfig(
        name="agro_advisor",
        port=8105,
        tier="starter",
        type="python",
        description_en="Agricultural Advisory - Crop recommendations and advice",
        description_ar="المستشار الزراعي - توصيات ونصائح زراعية",
    ),
    ServiceConfig(
        name="notification_service",
        port=8110,
        tier="starter",
        type="python",
        description_en="Notification Service - Email, SMS, and push notifications",
        description_ar="خدمة الإشعارات - البريد الإلكتروني والرسائل والإشعارات",
    ),
    # ═══════════════════════════════════════════════════════════════
    # PROFESSIONAL PACKAGE - حزمة سهول الاحترافية
    # ═══════════════════════════════════════════════════════════════
    ServiceConfig(
        name="satellite_service",
        port=8090,
        tier="professional",
        type="python",
        description_en="Satellite Imagery Service - Sentinel Hub, NASA, Planet integration",
        description_ar="خدمة الأقمار الصناعية - تكامل مع Sentinel Hub وNASA وPlanet",
    ),
    ServiceConfig(
        name="ndvi_engine",
        port=8107,
        tier="professional",
        type="python",
        description_en="NDVI Analysis Engine - Vegetation index calculation",
        description_ar="محرك تحليل NDVI - حساب مؤشر الغطاء النباتي",
    ),
    ServiceConfig(
        name="crop_health_ai",
        port=8095,
        tier="professional",
        type="python",
        description_en="Crop Health AI - Disease detection using computer vision",
        description_ar="الذكاء الاصطناعي لصحة المحاصيل - كشف الأمراض باستخدام الرؤية الحاسوبية",
    ),
    ServiceConfig(
        name="irrigation_smart",
        port=8094,
        tier="professional",
        type="python",
        description_en="Smart Irrigation - ET0 calculation and irrigation scheduling",
        description_ar="الري الذكي - حساب التبخر والنتح وجدولة الري",
    ),
    ServiceConfig(
        name="virtual_sensors",
        port=8096,
        tier="professional",
        type="python",
        description_en="Virtual Sensors - ML-based sensor data prediction",
        description_ar="المستشعرات الافتراضية - التنبؤ ببيانات المستشعرات باستخدام التعلم الآلي",
    ),
    ServiceConfig(
        name="yield_engine",
        port=8098,
        tier="professional",
        type="python",
        description_en="Yield Prediction Engine - Crop yield forecasting",
        description_ar="محرك التنبؤ بالإنتاجية - التنبؤ بإنتاجية المحاصيل",
    ),
    ServiceConfig(
        name="fertilizer_advisor",
        port=8093,
        tier="professional",
        type="python",
        description_en="Fertilizer Advisor - NPK recommendations based on soil analysis",
        description_ar="مستشار التسميد - توصيات NPK بناءً على تحليل التربة",
    ),
    ServiceConfig(
        name="inventory_service",
        port=8113,
        tier="professional",
        type="python",
        description_en="Inventory Management - Track seeds, fertilizers, equipment",
        description_ar="إدارة المخزون - تتبع البذور والأسمدة والمعدات",
    ),
    ServiceConfig(
        name="crop_health",
        port=8091,
        tier="professional",
        type="python",
        description_en="Crop Health Monitoring - Track crop stages and health",
        description_ar="مراقبة صحة المحاصيل - تتبع مراحل المحاصيل وصحتها",
    ),
    ServiceConfig(
        name="field_ops",
        port=8092,
        tier="professional",
        type="python",
        description_en="Field Operations - Manage farming activities and tasks",
        description_ar="عمليات الحقل - إدارة الأنشطة الزراعية والمهام",
    ),
    ServiceConfig(
        name="task_service",
        port=8109,
        tier="professional",
        type="python",
        description_en="Task Management - Create and assign agricultural tasks",
        description_ar="إدارة المهام - إنشاء وتعيين المهام الزراعية",
    ),
    ServiceConfig(
        name="equipment_service",
        port=8097,
        tier="professional",
        type="python",
        description_en="Equipment Management - Track and maintain farm equipment",
        description_ar="إدارة المعدات - تتبع وصيانة المعدات الزراعية",
    ),
    ServiceConfig(
        name="field_chat",
        port=8088,
        tier="professional",
        type="python",
        description_en="Field Chat - Communication and collaboration for farmers",
        description_ar="محادثات الحقل - التواصل والتعاون بين المزارعين",
    ),
    ServiceConfig(
        name="indicators_service",
        port=8114,
        tier="professional",
        type="python",
        description_en="Agricultural Indicators - Calculate and track farm KPIs",
        description_ar="المؤشرات الزراعية - حساب وتتبع مؤشرات الأداء الزراعي",
    ),
    # ═══════════════════════════════════════════════════════════════
    # ENTERPRISE PACKAGE - حزمة سهول للمؤسسات
    # ═══════════════════════════════════════════════════════════════
    ServiceConfig(
        name="ai_advisor",
        port=8112,
        tier="enterprise",
        type="python",
        description_en="Multi-Agent AI Advisor - RAG-powered agricultural intelligence",
        description_ar="المستشار الذكي متعدد الوكلاء - الذكاء الزراعي المدعوم بـ RAG",
    ),
    ServiceConfig(
        name="iot_gateway",
        port=8106,
        tier="enterprise",
        type="python",
        description_en="IoT Gateway - Connect and manage agricultural sensors",
        description_ar="بوابة إنترنت الأشياء - توصيل وإدارة أجهزة الاستشعار الزراعية",
    ),
    ServiceConfig(
        name="research_core",
        port=3015,
        tier="enterprise",
        type="nestjs",
        description_en="Research Core - Scientific research and trials management",
        description_ar="نواة البحث العلمي - إدارة البحوث والتجارب العلمية",
    ),
    ServiceConfig(
        name="marketplace_service",
        port=3010,
        tier="enterprise",
        type="nestjs",
        description_en="SAHOOL Marketplace - Buy and sell agricultural products",
        description_ar="سوق سهول - بيع وشراء المنتجات الزراعية",
    ),
    ServiceConfig(
        name="billing_core",
        port=8089,
        tier="enterprise",
        type="python",
        description_en="Billing Service - Subscription and payment management",
        description_ar="خدمة الفوترة - إدارة الاشتراكات والمدفوعات",
    ),
    ServiceConfig(
        name="disaster_assessment",
        port=3020,
        tier="enterprise",
        type="nestjs",
        description_en="Disaster Assessment - Evaluate agricultural disaster impact",
        description_ar="تقييم الكوارث - تقييم تأثير الكوارث الزراعية",
    ),
    ServiceConfig(
        name="crop_growth_model",
        port=3023,
        tier="enterprise",
        type="nestjs",
        description_en="Crop Growth Simulation - WOFOST-based crop modeling",
        description_ar="محاكاة نمو المحاصيل - نمذجة المحاصيل بناءً على WOFOST",
    ),
    ServiceConfig(
        name="lai_estimation",
        port=3022,
        tier="enterprise",
        type="nestjs",
        description_en="LAI Estimation - Leaf Area Index calculation from satellite",
        description_ar="تقدير مؤشر مساحة الأوراق - حساب LAI من صور الأقمار",
    ),
    ServiceConfig(
        name="weather_advanced",
        port=8115,
        tier="enterprise",
        type="python",
        description_en="Advanced Weather - High-resolution forecasts and climate data",
        description_ar="الطقس المتقدم - تنبؤات عالية الدقة وبيانات المناخ",
    ),
    ServiceConfig(
        name="provider_config",
        port=8116,
        tier="enterprise",
        type="python",
        description_en="Provider Configuration - Manage external API integrations",
        description_ar="تكوين المزودين - إدارة تكاملات الـ API الخارجية",
    ),
    ServiceConfig(
        name="ws_gateway",
        port=8117,
        tier="enterprise",
        type="python",
        description_en="WebSocket Gateway - Real-time data streaming",
        description_ar="بوابة WebSocket - بث البيانات في الوقت الفعلي",
    ),
    ServiceConfig(
        name="community_chat",
        port=3024,
        tier="enterprise",
        type="nestjs",
        description_en="Community Chat - Farmer community discussions",
        description_ar="محادثات المجتمع - نقاشات مجتمع المزارعين",
    ),
    ServiceConfig(
        name="iot_service",
        port=3025,
        tier="enterprise",
        type="nestjs",
        description_en="IoT Management - Device provisioning and data processing",
        description_ar="إدارة إنترنت الأشياء - توفير الأجهزة ومعالجة البيانات",
    ),
    ServiceConfig(
        name="field_service",
        port=8118,
        tier="enterprise",
        type="python",
        description_en="Field Service Management - Coordinate field workers and tasks",
        description_ar="إدارة خدمات الحقل - تنسيق العمال والمهام الميدانية",
    ),
    ServiceConfig(
        name="alert_service",
        port=8119,
        tier="enterprise",
        type="python",
        description_en="Alert Service - Automated alerts for critical events",
        description_ar="خدمة التنبيهات - تنبيهات تلقائية للأحداث الحرجة",
    ),
    ServiceConfig(
        name="ndvi_processor",
        port=8120,
        tier="enterprise",
        type="python",
        description_en="NDVI Processor - Batch processing of satellite imagery",
        description_ar="معالج NDVI - معالجة دفعات صور الأقمار الصناعية",
    ),
    ServiceConfig(
        name="yield_prediction",
        port=8121,
        tier="enterprise",
        type="python",
        description_en="Yield Prediction ML - Advanced ML models for yield forecasting",
        description_ar="التنبؤ بالإنتاجية - نماذج تعلم آلي متقدمة للتنبؤ بالإنتاجية",
    ),
    ServiceConfig(
        name="agro_rules",
        port=8122,
        tier="enterprise",
        type="python",
        description_en="Agricultural Rules Engine - Business rules and automation",
        description_ar="محرك القواعد الزراعية - قواعد العمل والأتمتة",
    ),
    ServiceConfig(
        name="chat_service",
        port=3026,
        tier="enterprise",
        type="nestjs",
        description_en="Chat Service - General messaging and communication",
        description_ar="خدمة المحادثة - الرسائل والتواصل العام",
    ),
]


class OpenAPIAggregator:
    """Aggregates OpenAPI specifications from multiple services"""

    def __init__(self, services: list[ServiceConfig]):
        self.services = services
        self.specs: dict[str, Any] = {}
        self.errors: list[str] = []

    def fetch_spec(self, service: ServiceConfig, timeout: int = 5) -> dict | None:
        """Fetch OpenAPI spec from a service with error handling"""
        try:
            logger.info(f"Fetching spec from {service.name} at {service.openapi_url}")
            response = requests.get(service.openapi_url, timeout=timeout)
            response.raise_for_status()

            spec = response.json()
            logger.info(f"✓ Successfully fetched spec from {service.name}")
            return spec

        except requests.exceptions.ConnectionError:
            error_msg = f"✗ Connection refused for {service.name} (service may be down)"
            logger.warning(error_msg)
            self.errors.append(error_msg)
            return None

        except requests.exceptions.Timeout:
            error_msg = f"✗ Timeout fetching {service.name}"
            logger.warning(error_msg)
            self.errors.append(error_msg)
            return None

        except requests.exceptions.HTTPError as e:
            error_msg = f"✗ HTTP error for {service.name}: {e}"
            logger.warning(error_msg)
            self.errors.append(error_msg)
            return None

        except Exception as e:
            error_msg = f"✗ Unexpected error for {service.name}: {e}"
            logger.error(error_msg)
            self.errors.append(error_msg)
            return None

    def fetch_all_specs(self):
        """Fetch specs from all services"""
        logger.info(f"Fetching OpenAPI specs from {len(self.services)} services...")

        for service in self.services:
            spec = self.fetch_spec(service)
            if spec:
                self.specs[service.name] = {"spec": spec, "config": service}

        logger.info(f"\nSuccessfully fetched {len(self.specs)}/{len(self.services)} specs")
        if self.errors:
            logger.warning(f"Failed to fetch {len(self.errors)} specs")

    def merge_specs(self) -> dict:
        """Merge all specs into a unified OpenAPI document"""
        logger.info("Merging OpenAPI specifications...")

        # Create the base unified spec
        unified_spec = {
            "openapi": "3.1.0",
            "info": {
                "title": "SAHOOL Platform - Unified API Documentation / واجهات برمجة منصة سهول الموحدة",
                "version": "1.0.0",
                "description": self._get_platform_description(),
                "contact": {
                    "name": "SAHOOL Platform",
                    "url": "https://sahool.com",
                    "email": "support@sahool.com",
                },
                "license": {"name": "Proprietary", "url": "https://sahool.com/license"},
            },
            "servers": [
                {"url": "http://localhost", "description": "Local Development"},
                {"url": "https://api.sahool.com", "description": "Production"},
            ],
            "paths": {},
            "components": {
                "schemas": {},
                "securitySchemes": {
                    "bearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT",
                        "description": "JWT authentication token / رمز المصادقة JWT",
                    }
                },
            },
            "tags": self._generate_tags(),
            "x-tagGroups": self._generate_tag_groups(),
        }

        # Merge paths and components from each service
        for service_name, service_data in self.specs.items():
            spec = service_data["spec"]
            config = service_data["config"]

            self._merge_service_paths(unified_spec, spec, config)
            self._merge_service_components(unified_spec, spec, service_name)

        return unified_spec

    def _get_platform_description(self) -> str:
        """Get the platform description in English and Arabic"""
        return """
# SAHOOL Agricultural Platform API

**منصة سهول الزراعية**

A comprehensive agricultural intelligence platform serving Yemen's farmers with cutting-edge technology.

منصة زراعية متكاملة تخدم مزارعي اليمن بأحدث التقنيات.

## Package Tiers / مستويات الباقات

### 🌱 Starter Package - الباقة المبتدئة
Essential services for small farms:
- Field Management (إدارة الحقول)
- Weather Services (خدمات الطقس)
- Agricultural Calendar (التقويم الزراعي)
- Basic Advisory (الإرشاد الأساسي)

### 🚜 Professional Package - الباقة الاحترافية
Advanced features for commercial farms:
- Satellite Imagery (صور الأقمار الصناعية)
- AI Crop Health (صحة المحاصيل بالذكاء الاصطناعي)
- Smart Irrigation (الري الذكي)
- Yield Prediction (التنبؤ بالإنتاجية)
- Inventory Management (إدارة المخزون)

### 🏢 Enterprise Package - الباقة المؤسسية
Complete solution for large enterprises:
- Multi-Agent AI Advisor (المستشار الذكي متعدد الوكلاء)
- IoT Integration (تكامل إنترنت الأشياء)
- Research & Trials (البحث والتجارب)
- Marketplace (السوق)
- Advanced Analytics (التحليلات المتقدمة)

## Authentication / المصادقة

All API endpoints require JWT authentication unless otherwise specified.

جميع نقاط النهاية تتطلب مصادقة JWT ما لم يُذكر خلاف ذلك.
"""

    def _generate_tags(self) -> list[dict]:
        """Generate tags for all services organized by tier"""
        tags = []

        # Group services by tier
        services_by_tier = defaultdict(list)
        for service in self.services:
            services_by_tier[service.tier].append(service)

        # Add tags for each service
        for tier in ["starter", "professional", "enterprise"]:
            for service in services_by_tier[tier]:
                tags.append(
                    {
                        "name": service.name,
                        "description": f"{service.description_en}\n\n{service.description_ar}",
                        "x-tier": tier,
                    }
                )

        return tags

    def _generate_tag_groups(self) -> list[dict]:
        """Generate tag groups for organizing services by tier"""
        return [
            {
                "name": "🌱 Starter Package - الباقة المبتدئة",
                "tags": [s.name for s in self.services if s.tier == "starter"],
            },
            {
                "name": "🚜 Professional Package - الباقة الاحترافية",
                "tags": [s.name for s in self.services if s.tier == "professional"],
            },
            {
                "name": "🏢 Enterprise Package - الباقة المؤسسية",
                "tags": [s.name for s in self.services if s.tier == "enterprise"],
            },
        ]

    def _merge_service_paths(self, unified: dict, service_spec: dict, config: ServiceConfig):
        """Merge paths from a service spec into the unified spec"""
        if "paths" not in service_spec:
            return

        for path, path_item in service_spec["paths"].items():
            # Prefix path with service name to avoid conflicts
            unified_path = f"/{config.name}{path}"

            # Add service tag to all operations
            for method in ["get", "post", "put", "patch", "delete", "options", "head"]:
                if method in path_item:
                    operation = path_item[method]

                    # Add service tag
                    if "tags" not in operation:
                        operation["tags"] = []
                    if config.name not in operation["tags"]:
                        operation["tags"].insert(0, config.name)

                    # Add tier information
                    operation["x-tier"] = config.tier

                    # Add server override for this operation
                    operation["servers"] = [
                        {
                            "url": f"http://localhost:{config.port}",
                            "description": f"{config.description_en}",
                        }
                    ]

            unified["paths"][unified_path] = path_item

    def _merge_service_components(self, unified: dict, service_spec: dict, service_name: str):
        """Merge components (schemas) from a service spec"""
        if "components" not in service_spec:
            return

        if "schemas" in service_spec["components"]:
            for schema_name, schema in service_spec["components"]["schemas"].items():
                # Prefix schema name with service name to avoid conflicts
                unified_schema_name = f"{service_name}_{schema_name}"
                unified["components"]["schemas"][unified_schema_name] = schema

    def save_to_file(self, spec: dict, output_file: str):
        """Save the unified spec to a YAML file"""
        logger.info(f"Saving unified spec to {output_file}")

        try:
            with open(output_file, "w", encoding="utf-8") as f:
                yaml.dump(
                    spec,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                    width=120,
                )
            logger.info(f"✓ Successfully saved to {output_file}")

            # Also save as JSON for easier programmatic access
            json_file = output_file.replace(".yaml", ".json")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(spec, f, indent=2, ensure_ascii=False)
            logger.info(f"✓ Also saved JSON version to {json_file}")

        except Exception as e:
            logger.error(f"✗ Failed to save file: {e}")
            raise

    def print_summary(self):
        """Print a summary of the aggregation"""
        print("\n" + "=" * 80)
        print("SAHOOL OpenAPI Aggregation Summary")
        print("=" * 80)

        # Group by tier
        services_by_tier = defaultdict(list)
        for service_name, service_data in self.specs.items():
            tier = service_data["config"].tier
            services_by_tier[tier].append(service_name)

        for tier in ["starter", "professional", "enterprise"]:
            print(f"\n{tier.upper()} TIER: {len(services_by_tier[tier])} services")
            for service in sorted(services_by_tier[tier]):
                print(f"  ✓ {service}")

        if self.errors:
            print(f"\n⚠ ERRORS ({len(self.errors)}):")
            for error in self.errors:
                print(f"  {error}")

        print("\n" + "=" * 80)
        print(f"Total: {len(self.specs)}/{len(self.services)} services aggregated")
        print("=" * 80 + "\n")


def main():
    """Main execution function"""
    try:
        # Create aggregator
        aggregator = OpenAPIAggregator(SERVICES)

        # Fetch all specs
        aggregator.fetch_all_specs()

        # Check if we got at least some specs
        if not aggregator.specs:
            logger.error("Failed to fetch any OpenAPI specs. Are the services running?")
            logger.info(
                "Start services with: docker-compose -f packages/starter/docker-compose.yml up -d"
            )
            sys.exit(1)

        # Merge specs
        unified_spec = aggregator.merge_specs()

        # Save to file
        output_file = "openapi-unified.yaml"
        aggregator.save_to_file(unified_spec, output_file)

        # Print summary
        aggregator.print_summary()

        logger.info("✓ OpenAPI aggregation completed successfully!")

    except Exception as e:
        logger.error(f"✗ Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
