"""
SAHOOL MCP Resources - Agricultural Data Resources
===================================================

Implements MCP resource providers for SAHOOL agricultural data.
Resources provide read-only access to structured data following MCP specification.

Resource Categories:
- Field Resources: Field data, boundaries, soil, sensors, activities
- Farmer Resources: Farmer profiles, farms, interactions
- Weather Resources: Current conditions, forecasts, advisories
- Crop Catalog Resources: Crop info, growing guides, pest/disease management
- Knowledge Base Resources: Agricultural documentation, best practices

All resources include bilingual descriptions (English/Arabic).

Author: SAHOOL Platform Team
Version: 1.0.0
Updated: January 2026
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import BaseModel

from .config import Language, MCPConfig, ResourceDescriptions, get_config


class Resource(BaseModel):
    """MCP Resource representation"""

    uri: str
    name: str
    name_ar: str | None = None
    description: str | None = None
    description_ar: str | None = None
    mimeType: str = "application/json"


class ResourceContent(BaseModel):
    """MCP Resource content"""

    uri: str
    mimeType: str = "application/json"
    text: str | None = None
    blob: str | None = None


class ResourceProvider(ABC):
    """Base class for resource providers"""

    def __init__(self, base_url: str | None = None, config: MCPConfig | None = None):
        self.config = config or get_config()
        self.base_url = base_url or self.config.api.base_url
        self.client = httpx.AsyncClient(timeout=self.config.api.default_timeout)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    @abstractmethod
    async def list_resources(self) -> list[Resource]:
        """List available resources"""
        pass

    @abstractmethod
    async def get_resource(self, uri: str) -> ResourceContent:
        """Get resource content by URI"""
        pass


class FieldDataResource(ResourceProvider):
    """
    Field Data Resource Provider

    Provides access to agricultural field data including boundaries,
    soil properties, crop information, sensors, and activities.

    URI Patterns:
    - field://{field_id}/info - General field information
    - field://{field_id}/boundaries - GeoJSON boundaries
    - field://{field_id}/soil - Soil properties and tests
    - field://{field_id}/sensors - IoT sensor data
    - field://{field_id}/activities - Historical activities
    - field://{field_id}/health - Crop health metrics
    """

    async def list_resources(self) -> list[Resource]:
        """List all available field resources"""
        try:
            response = await self.client.get(f"{self.base_url}/api/fields")
            response.raise_for_status()
            fields = response.json()

            resources = []
            for field in fields.get("fields", []):
                field_id = field.get("id")
                field_name = field.get("name", field_id)
                field_name_ar = field.get("name_ar", field_name)

                resources.extend(
                    [
                        Resource(
                            uri=f"field://{field_id}/info",
                            name=f"Field {field_name} - Info",
                            name_ar=f"حقل {field_name_ar} - معلومات",
                            description=ResourceDescriptions.get("field_info", Language.ENGLISH),
                            description_ar=ResourceDescriptions.get("field_info", Language.ARABIC),
                        ),
                        Resource(
                            uri=f"field://{field_id}/boundaries",
                            name=f"Field {field_name} - Boundaries",
                            name_ar=f"حقل {field_name_ar} - الحدود",
                            description=ResourceDescriptions.get("field_boundaries", Language.ENGLISH),
                            description_ar=ResourceDescriptions.get("field_boundaries", Language.ARABIC),
                            mimeType="application/geo+json",
                        ),
                        Resource(
                            uri=f"field://{field_id}/soil",
                            name=f"Field {field_name} - Soil Data",
                            name_ar=f"حقل {field_name_ar} - بيانات التربة",
                            description=ResourceDescriptions.get("field_soil", Language.ENGLISH),
                            description_ar=ResourceDescriptions.get("field_soil", Language.ARABIC),
                        ),
                        Resource(
                            uri=f"field://{field_id}/sensors",
                            name=f"Field {field_name} - Sensors",
                            name_ar=f"حقل {field_name_ar} - المستشعرات",
                            description=ResourceDescriptions.get("field_sensors", Language.ENGLISH),
                            description_ar=ResourceDescriptions.get("field_sensors", Language.ARABIC),
                        ),
                        Resource(
                            uri=f"field://{field_id}/activities",
                            name=f"Field {field_name} - Activities",
                            name_ar=f"حقل {field_name_ar} - الأنشطة",
                            description="Historical activities and tasks for the field | الأنشطة والمهام التاريخية للحقل",
                        ),
                        Resource(
                            uri=f"field://{field_id}/health",
                            name=f"Field {field_name} - Health",
                            name_ar=f"حقل {field_name_ar} - الصحة",
                            description="Crop health metrics and NDVI data | مقاييس صحة المحصول وبيانات NDVI",
                        ),
                    ]
                )

            return resources
        except Exception as e:
            print(f"Error listing field resources: {e}")
            return []

    async def get_resource(self, uri: str) -> ResourceContent:
        """Get field resource content"""
        if not uri.startswith("field://"):
            raise ValueError(f"Invalid field URI: {uri}")

        parts = uri.replace("field://", "").split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid field URI format: {uri}")

        field_id = parts[0]
        resource_type = parts[1]

        try:
            endpoint_map = {
                "info": f"/api/fields/{field_id}",
                "boundaries": f"/api/fields/{field_id}/boundaries",
                "soil": f"/api/fields/{field_id}/soil",
                "sensors": f"/api/fields/{field_id}/sensors",
                "activities": f"/api/fields/{field_id}/activities",
                "health": f"/api/fields/{field_id}/health",
            }

            if resource_type not in endpoint_map:
                raise ValueError(f"Unknown resource type: {resource_type}")

            response = await self.client.get(f"{self.base_url}{endpoint_map[resource_type]}")
            response.raise_for_status()
            data = response.json()

            mime_type = "application/geo+json" if resource_type == "boundaries" else "application/json"

            return ResourceContent(
                uri=uri,
                mimeType=mime_type,
                text=json.dumps(data, indent=2, ensure_ascii=False),
            )

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch field resource: {str(e)}")


class FarmerDataResource(ResourceProvider):
    """
    Farmer Data Resource Provider

    Provides access to farmer profiles, farm portfolios, and interaction history.

    URI Patterns:
    - farmer://{farmer_id}/profile - Farmer profile information
    - farmer://{farmer_id}/farms - List of farms owned/managed
    - farmer://{farmer_id}/preferences - Farmer preferences and settings
    - farmer://{farmer_id}/interactions - Interaction history
    - farmer://{farmer_id}/recommendations - Recommendation history
    """

    async def list_resources(self) -> list[Resource]:
        """List all available farmer resources"""
        try:
            response = await self.client.get(f"{self.base_url}/api/farmers")
            response.raise_for_status()
            farmers = response.json()

            resources = []
            for farmer in farmers.get("farmers", []):
                farmer_id = farmer.get("id")
                farmer_name = farmer.get("name", farmer_id)
                farmer_name_ar = farmer.get("name_ar", farmer_name)

                resources.extend(
                    [
                        Resource(
                            uri=f"farmer://{farmer_id}/profile",
                            name=f"Farmer {farmer_name} - Profile",
                            name_ar=f"مزارع {farmer_name_ar} - الملف الشخصي",
                            description=ResourceDescriptions.get("farmer_profile", Language.ENGLISH),
                            description_ar=ResourceDescriptions.get("farmer_profile", Language.ARABIC),
                        ),
                        Resource(
                            uri=f"farmer://{farmer_id}/farms",
                            name=f"Farmer {farmer_name} - Farms",
                            name_ar=f"مزارع {farmer_name_ar} - المزارع",
                            description=ResourceDescriptions.get("farmer_farms", Language.ENGLISH),
                            description_ar=ResourceDescriptions.get("farmer_farms", Language.ARABIC),
                        ),
                        Resource(
                            uri=f"farmer://{farmer_id}/preferences",
                            name=f"Farmer {farmer_name} - Preferences",
                            name_ar=f"مزارع {farmer_name_ar} - التفضيلات",
                            description="Farmer communication and advisory preferences | تفضيلات التواصل والاستشارة للمزارع",
                        ),
                        Resource(
                            uri=f"farmer://{farmer_id}/interactions",
                            name=f"Farmer {farmer_name} - Interactions",
                            name_ar=f"مزارع {farmer_name_ar} - التفاعلات",
                            description="History of interactions and communications | سجل التفاعلات والاتصالات",
                        ),
                        Resource(
                            uri=f"farmer://{farmer_id}/recommendations",
                            name=f"Farmer {farmer_name} - Recommendations",
                            name_ar=f"مزارع {farmer_name_ar} - التوصيات",
                            description="History of recommendations and outcomes | سجل التوصيات والنتائج",
                        ),
                    ]
                )

            return resources
        except Exception as e:
            print(f"Error listing farmer resources: {e}")
            return []

    async def get_resource(self, uri: str) -> ResourceContent:
        """Get farmer resource content"""
        if not uri.startswith("farmer://"):
            raise ValueError(f"Invalid farmer URI: {uri}")

        parts = uri.replace("farmer://", "").split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid farmer URI format: {uri}")

        farmer_id = parts[0]
        resource_type = parts[1]

        try:
            endpoint_map = {
                "profile": f"/api/farmers/{farmer_id}",
                "farms": f"/api/farmers/{farmer_id}/farms",
                "preferences": f"/api/farmers/{farmer_id}/preferences",
                "interactions": f"/api/farmers/{farmer_id}/interactions",
                "recommendations": f"/api/farmers/{farmer_id}/recommendations",
            }

            if resource_type not in endpoint_map:
                raise ValueError(f"Unknown resource type: {resource_type}")

            response = await self.client.get(f"{self.base_url}{endpoint_map[resource_type]}")
            response.raise_for_status()
            data = response.json()

            return ResourceContent(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(data, indent=2, ensure_ascii=False),
            )

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch farmer resource: {str(e)}")


class WeatherDataResource(ResourceProvider):
    """
    Weather Data Resource Provider

    Provides access to weather forecasts, historical weather data,
    and agricultural weather advisories.

    URI Patterns:
    - weather://current - Current weather conditions
    - weather://forecast/7day - 7-day forecast
    - weather://forecast/14day - 14-day forecast
    - weather://advisories - Agricultural weather advisories
    - weather://historical/30day - Last 30 days historical data
    - weather://alerts - Active weather alerts
    """

    async def list_resources(self) -> list[Resource]:
        """List all available weather resources"""
        return [
            Resource(
                uri="weather://current",
                name="Current Weather Conditions",
                name_ar="أحوال الطقس الحالية",
                description=ResourceDescriptions.get("weather_current", Language.ENGLISH),
                description_ar=ResourceDescriptions.get("weather_current", Language.ARABIC),
            ),
            Resource(
                uri="weather://forecast/7day",
                name="7-Day Weather Forecast",
                name_ar="توقعات الطقس لـ 7 أيام",
                description=ResourceDescriptions.get("weather_forecast", Language.ENGLISH),
                description_ar=ResourceDescriptions.get("weather_forecast", Language.ARABIC),
            ),
            Resource(
                uri="weather://forecast/14day",
                name="14-Day Weather Forecast",
                name_ar="توقعات الطقس لـ 14 يوم",
                description="Extended 14-day weather forecast | توقعات الطقس الممتدة لـ 14 يوم",
            ),
            Resource(
                uri="weather://advisories",
                name="Agricultural Weather Advisories",
                name_ar="الإرشادات الزراعية المتعلقة بالطقس",
                description="Weather-based agricultural advisories and alerts | الإرشادات والتنبيهات الزراعية المتعلقة بالطقس",
            ),
            Resource(
                uri="weather://historical/30day",
                name="30-Day Historical Weather",
                name_ar="بيانات الطقس التاريخية لـ 30 يوم",
                description="Historical weather data for the last 30 days | بيانات الطقس التاريخية لآخر 30 يوم",
            ),
            Resource(
                uri="weather://alerts",
                name="Active Weather Alerts",
                name_ar="تنبيهات الطقس النشطة",
                description="Current active weather alerts and warnings | تنبيهات وتحذيرات الطقس النشطة الحالية",
            ),
        ]

    async def get_resource(self, uri: str) -> ResourceContent:
        """Get weather resource content"""
        if not uri.startswith("weather://"):
            raise ValueError(f"Invalid weather URI: {uri}")

        resource_path = uri.replace("weather://", "")

        try:
            if resource_path == "current":
                response = await self.client.get(f"{self.base_url}/api/weather/current")
            elif resource_path.startswith("forecast/"):
                days = resource_path.split("/")[1].replace("day", "")
                response = await self.client.get(f"{self.base_url}/api/weather/forecast", params={"days": days})
            elif resource_path == "advisories":
                response = await self.client.get(f"{self.base_url}/api/weather/advisories")
            elif resource_path.startswith("historical/"):
                days = resource_path.split("/")[1].replace("day", "")
                response = await self.client.get(f"{self.base_url}/api/weather/historical", params={"days": days})
            elif resource_path == "alerts":
                response = await self.client.get(f"{self.base_url}/api/weather/alerts")
            else:
                raise ValueError(f"Unknown weather resource: {resource_path}")

            response.raise_for_status()
            data = response.json()

            return ResourceContent(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(data, indent=2, ensure_ascii=False),
            )

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch weather resource: {str(e)}")


class CropCatalogResource(ResourceProvider):
    """
    Crop Catalog Resource Provider

    Provides access to crop information, growing guides, pest/disease databases,
    and agricultural best practices.

    URI Patterns:
    - crops://catalog - Complete crop catalog
    - crops://{crop_id}/info - Crop information
    - crops://{crop_id}/growing-guide - Growing guide
    - crops://{crop_id}/pests - Pest management
    - crops://{crop_id}/diseases - Disease management
    - crops://{crop_id}/varieties - Crop varieties
    """

    async def list_resources(self) -> list[Resource]:
        """List all available crop catalog resources"""
        try:
            response = await self.client.get(f"{self.base_url}/api/crops/catalog")
            response.raise_for_status()
            crops = response.json()

            resources = [
                Resource(
                    uri="crops://catalog",
                    name="Complete Crop Catalog",
                    name_ar="كتالوج المحاصيل الكامل",
                    description="Complete catalog of supported crops and varieties | كتالوج كامل للمحاصيل والأصناف المدعومة",
                ),
            ]

            for crop in crops.get("crops", []):
                crop_id = crop.get("id")
                crop_name = crop.get("name")
                crop_name_ar = crop.get("name_ar", crop_name)

                resources.extend(
                    [
                        Resource(
                            uri=f"crops://{crop_id}/info",
                            name=f"{crop_name} - Information",
                            name_ar=f"{crop_name_ar} - معلومات",
                            description=f"Complete information about {crop_name} | معلومات شاملة عن {crop_name_ar}",
                        ),
                        Resource(
                            uri=f"crops://{crop_id}/growing-guide",
                            name=f"{crop_name} - Growing Guide",
                            name_ar=f"{crop_name_ar} - دليل الزراعة",
                            description=ResourceDescriptions.get("knowledge_crops", Language.ENGLISH),
                            description_ar=ResourceDescriptions.get("knowledge_crops", Language.ARABIC),
                        ),
                        Resource(
                            uri=f"crops://{crop_id}/pests",
                            name=f"{crop_name} - Pest Management",
                            name_ar=f"{crop_name_ar} - إدارة الآفات",
                            description=ResourceDescriptions.get("knowledge_pests", Language.ENGLISH),
                            description_ar=ResourceDescriptions.get("knowledge_pests", Language.ARABIC),
                        ),
                        Resource(
                            uri=f"crops://{crop_id}/diseases",
                            name=f"{crop_name} - Disease Management",
                            name_ar=f"{crop_name_ar} - إدارة الأمراض",
                            description=ResourceDescriptions.get("knowledge_diseases", Language.ENGLISH),
                            description_ar=ResourceDescriptions.get("knowledge_diseases", Language.ARABIC),
                        ),
                        Resource(
                            uri=f"crops://{crop_id}/varieties",
                            name=f"{crop_name} - Varieties",
                            name_ar=f"{crop_name_ar} - الأصناف",
                            description=f"Available varieties of {crop_name} | الأصناف المتاحة من {crop_name_ar}",
                        ),
                    ]
                )

            return resources
        except Exception as e:
            print(f"Error listing crop resources: {e}")
            return []

    async def get_resource(self, uri: str) -> ResourceContent:
        """Get crop catalog resource content"""
        if not uri.startswith("crops://"):
            raise ValueError(f"Invalid crop URI: {uri}")

        resource_path = uri.replace("crops://", "")

        try:
            if resource_path == "catalog":
                response = await self.client.get(f"{self.base_url}/api/crops/catalog")
            else:
                parts = resource_path.split("/")
                if len(parts) < 2:
                    raise ValueError(f"Invalid crop URI format: {uri}")

                crop_id = parts[0]
                resource_type = parts[1]

                endpoint_map = {
                    "info": f"/api/crops/{crop_id}",
                    "growing-guide": f"/api/crops/{crop_id}/growing-guide",
                    "pests": f"/api/crops/{crop_id}/pests",
                    "diseases": f"/api/crops/{crop_id}/diseases",
                    "varieties": f"/api/crops/{crop_id}/varieties",
                }

                if resource_type not in endpoint_map:
                    raise ValueError(f"Unknown resource type: {resource_type}")

                response = await self.client.get(f"{self.base_url}{endpoint_map[resource_type]}")

            response.raise_for_status()
            data = response.json()

            return ResourceContent(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(data, indent=2, ensure_ascii=False),
            )

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch crop resource: {str(e)}")


class KnowledgeBaseResource(ResourceProvider):
    """
    Knowledge Base Resource Provider

    Provides access to agricultural documentation, best practices,
    tutorials, and educational content.

    URI Patterns:
    - knowledge://topics - List of all topics
    - knowledge://irrigation/guide - Irrigation best practices
    - knowledge://soil/management - Soil management guide
    - knowledge://fertilizer/guide - Fertilizer application guide
    - knowledge://pest-control/ipm - Integrated pest management
    - knowledge://organic/certification - Organic farming certification
    - knowledge://globalgap/compliance - GlobalGAP compliance guide
    - knowledge://faq - Frequently asked questions
    """

    TOPICS = [
        {
            "id": "irrigation",
            "name": "Irrigation Management",
            "name_ar": "إدارة الري",
            "subtopics": ["guide", "drip", "sprinkler", "scheduling", "efficiency"],
        },
        {
            "id": "soil",
            "name": "Soil Management",
            "name_ar": "إدارة التربة",
            "subtopics": ["management", "testing", "amendments", "health"],
        },
        {
            "id": "fertilizer",
            "name": "Fertilizer Application",
            "name_ar": "تطبيق الأسمدة",
            "subtopics": ["guide", "npk", "organic", "timing", "methods"],
        },
        {
            "id": "pest-control",
            "name": "Pest Control",
            "name_ar": "مكافحة الآفات",
            "subtopics": ["ipm", "biological", "chemical", "prevention"],
        },
        {
            "id": "disease-management",
            "name": "Disease Management",
            "name_ar": "إدارة الأمراض",
            "subtopics": [
                "identification",
                "prevention",
                "treatment",
                "fungal",
                "bacterial",
                "viral",
            ],
        },
        {
            "id": "organic",
            "name": "Organic Farming",
            "name_ar": "الزراعة العضوية",
            "subtopics": ["certification", "practices", "inputs", "marketing"],
        },
        {
            "id": "globalgap",
            "name": "GlobalGAP Compliance",
            "name_ar": "الامتثال لـ GlobalGAP",
            "subtopics": ["compliance", "audit", "documentation", "traceability"],
        },
        {
            "id": "harvest",
            "name": "Harvest & Post-Harvest",
            "name_ar": "الحصاد وما بعد الحصاد",
            "subtopics": ["timing", "techniques", "storage", "quality"],
        },
        {
            "id": "climate",
            "name": "Climate Adaptation",
            "name_ar": "التكيف مع المناخ",
            "subtopics": ["heat-stress", "drought", "frost", "resilience"],
        },
    ]

    async def list_resources(self) -> list[Resource]:
        """List all available knowledge base resources"""
        resources = [
            Resource(
                uri="knowledge://topics",
                name="Knowledge Base Topics",
                name_ar="مواضيع قاعدة المعرفة",
                description="List of all knowledge base topics | قائمة بجميع مواضيع قاعدة المعرفة",
            ),
            Resource(
                uri="knowledge://faq",
                name="Frequently Asked Questions",
                name_ar="الأسئلة الشائعة",
                description="Common questions and answers | الأسئلة والإجابات الشائعة",
            ),
        ]

        for topic in self.TOPICS:
            topic_id = topic["id"]
            topic_name = topic["name"]
            topic_name_ar = topic["name_ar"]

            for subtopic in topic["subtopics"]:
                resources.append(
                    Resource(
                        uri=f"knowledge://{topic_id}/{subtopic}",
                        name=f"{topic_name} - {subtopic.replace('-', ' ').title()}",
                        name_ar=f"{topic_name_ar} - {subtopic}",
                        description=f"Documentation about {topic_name.lower()} {subtopic} | وثائق حول {subtopic} {topic_name_ar}",
                    )
                )

        return resources

    async def get_resource(self, uri: str) -> ResourceContent:
        """Get knowledge base resource content"""
        if not uri.startswith("knowledge://"):
            raise ValueError(f"Invalid knowledge URI: {uri}")

        resource_path = uri.replace("knowledge://", "")

        try:
            if resource_path == "topics":
                data = {
                    "topics": self.TOPICS,
                    "total_topics": len(self.TOPICS),
                    "languages": ["en", "ar"],
                }
            elif resource_path == "faq":
                response = await self.client.get(f"{self.base_url}/api/knowledge/faq")
                response.raise_for_status()
                data = response.json()
            else:
                parts = resource_path.split("/")
                if len(parts) < 2:
                    raise ValueError(f"Invalid knowledge URI format: {uri}")

                topic_id = parts[0]
                subtopic = parts[1]

                response = await self.client.get(f"{self.base_url}/api/knowledge/{topic_id}/{subtopic}")
                response.raise_for_status()
                data = response.json()

            return ResourceContent(
                uri=uri,
                mimeType="application/json",
                text=json.dumps(data, indent=2, ensure_ascii=False),
            )

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch knowledge resource: {str(e)}")


class ResourceManager:
    """
    Manages all resource providers

    Coordinates multiple resource providers and provides unified access
    to all SAHOOL resources.
    """

    def __init__(self, base_url: str | None = None, config: MCPConfig | None = None):
        config = config or get_config()
        base_url = base_url or config.api.base_url

        self.providers: dict[str, ResourceProvider] = {
            "field": FieldDataResource(base_url, config),
            "farmer": FarmerDataResource(base_url, config),
            "weather": WeatherDataResource(base_url, config),
            "crops": CropCatalogResource(base_url, config),
            "knowledge": KnowledgeBaseResource(base_url, config),
        }

    async def close(self):
        """Close all resource providers"""
        for provider in self.providers.values():
            await provider.close()

    async def list_all_resources(self) -> list[Resource]:
        """List all resources from all providers"""
        all_resources = []
        for provider in self.providers.values():
            resources = await provider.list_resources()
            all_resources.extend(resources)
        return all_resources

    async def get_resource(self, uri: str) -> ResourceContent:
        """Get resource by URI, routing to appropriate provider"""
        scheme = uri.split("://")[0] if "://" in uri else None

        if not scheme or scheme not in self.providers:
            raise ValueError(f"Unknown resource scheme in URI: {uri}")

        return await self.providers[scheme].get_resource(uri)

    def get_resource_templates(self) -> list[dict[str, Any]]:
        """Get resource URI templates for discovery"""
        return [
            {
                "uriTemplate": "field://{field_id}/{resource_type}",
                "name": "Field Resources",
                "name_ar": "موارد الحقل",
                "description": "Access field data, boundaries, soil info, sensors, and activities | الوصول إلى بيانات الحقل والحدود ومعلومات التربة والمستشعرات والأنشطة",
                "mimeType": "application/json",
                "variables": {
                    "field_id": "Field identifier | معرف الحقل",
                    "resource_type": "info, boundaries, soil, sensors, activities, health",
                },
            },
            {
                "uriTemplate": "farmer://{farmer_id}/{resource_type}",
                "name": "Farmer Resources",
                "name_ar": "موارد المزارع",
                "description": "Access farmer profiles, farms, preferences, and interactions | الوصول إلى ملفات المزارعين والمزارع والتفضيلات والتفاعلات",
                "mimeType": "application/json",
                "variables": {
                    "farmer_id": "Farmer identifier | معرف المزارع",
                    "resource_type": "profile, farms, preferences, interactions, recommendations",
                },
            },
            {
                "uriTemplate": "weather://{resource_type}",
                "name": "Weather Resources",
                "name_ar": "موارد الطقس",
                "description": "Access weather forecasts, current conditions, and advisories | الوصول إلى توقعات الطقس والأحوال الحالية والإرشادات",
                "mimeType": "application/json",
                "variables": {
                    "resource_type": "current, forecast/7day, forecast/14day, advisories, historical/30day, alerts",
                },
            },
            {
                "uriTemplate": "crops://{crop_id}/{resource_type}",
                "name": "Crop Catalog Resources",
                "name_ar": "موارد كتالوج المحاصيل",
                "description": "Access crop information, growing guides, and pest/disease management | الوصول إلى معلومات المحاصيل وأدلة الزراعة وإدارة الآفات والأمراض",
                "mimeType": "application/json",
                "variables": {
                    "crop_id": "Crop identifier (e.g., wheat, tomato) | معرف المحصول",
                    "resource_type": "info, growing-guide, pests, diseases, varieties",
                },
            },
            {
                "uriTemplate": "knowledge://{topic}/{subtopic}",
                "name": "Knowledge Base Resources",
                "name_ar": "موارد قاعدة المعرفة",
                "description": "Access agricultural documentation, guides, and best practices | الوصول إلى الوثائق الزراعية والأدلة وأفضل الممارسات",
                "mimeType": "application/json",
                "variables": {
                    "topic": "Topic (irrigation, soil, fertilizer, pest-control, etc.) | الموضوع",
                    "subtopic": "Subtopic within the topic | الموضوع الفرعي",
                },
            },
        ]

    def list_providers(self) -> list[dict[str, Any]]:
        """List all registered resource providers"""
        return [
            {
                "scheme": scheme,
                "provider": provider.__class__.__name__,
                "description": provider.__doc__.split("\n")[1].strip() if provider.__doc__ else "",
            }
            for scheme, provider in self.providers.items()
        ]
