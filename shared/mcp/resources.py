"""
SAHOOL MCP Resources - Agricultural Data Resources
===================================================

Implements MCP resource providers for SAHOOL agricultural data.
Resources provide read-only access to structured data following MCP specification.
"""

import os
from abc import ABC, abstractmethod
from typing import Any

import httpx
from pydantic import BaseModel


class Resource(BaseModel):
    """MCP Resource representation"""

    uri: str
    name: str
    description: str | None = None
    mimeType: str = "application/json"


class ResourceContent(BaseModel):
    """MCP Resource content"""

    uri: str
    mimeType: str = "application/json"
    text: str | None = None
    blob: str | None = None


class ResourceProvider(ABC):
    """Base class for resource providers"""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or os.getenv("SAHOOL_API_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(timeout=30.0)

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
    soil properties, crop information, and activities.
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
                resources.extend(
                    [
                        Resource(
                            uri=f"field://{field_id}/info",
                            name=f"Field {field.get('name', field_id)} - Info",
                            description=f"General information for field {field.get('name', field_id)}",
                        ),
                        Resource(
                            uri=f"field://{field_id}/boundaries",
                            name=f"Field {field.get('name', field_id)} - Boundaries",
                            description=f"Geospatial boundaries (GeoJSON) for field {field.get('name', field_id)}",
                            mimeType="application/geo+json",
                        ),
                        Resource(
                            uri=f"field://{field_id}/soil",
                            name=f"Field {field.get('name', field_id)} - Soil Data",
                            description=f"Soil properties and test results for field {field.get('name', field_id)}",
                        ),
                        Resource(
                            uri=f"field://{field_id}/activities",
                            name=f"Field {field.get('name', field_id)} - Activities",
                            description=f"Historical activities and tasks for field {field.get('name', field_id)}",
                        ),
                    ]
                )

            return resources
        except Exception as e:
            print(f"Error listing field resources: {e}")
            return []

    async def get_resource(self, uri: str) -> ResourceContent:
        """Get field resource content"""
        # Parse URI: field://{field_id}/{resource_type}
        if not uri.startswith("field://"):
            raise ValueError(f"Invalid field URI: {uri}")

        parts = uri.replace("field://", "").split("/")
        if len(parts) < 2:
            raise ValueError(f"Invalid field URI format: {uri}")

        field_id = parts[0]
        resource_type = parts[1]

        try:
            if resource_type == "info":
                response = await self.client.get(f"{self.base_url}/api/fields/{field_id}")
            elif resource_type == "boundaries":
                response = await self.client.get(
                    f"{self.base_url}/api/fields/{field_id}/boundaries"
                )
            elif resource_type == "soil":
                response = await self.client.get(f"{self.base_url}/api/fields/{field_id}/soil")
            elif resource_type == "activities":
                response = await self.client.get(
                    f"{self.base_url}/api/fields/{field_id}/activities"
                )
            else:
                raise ValueError(f"Unknown resource type: {resource_type}")

            response.raise_for_status()
            data = response.json()

            import json

            mime_type = (
                "application/geo+json" if resource_type == "boundaries" else "application/json"
            )

            return ResourceContent(uri=uri, mimeType=mime_type, text=json.dumps(data, indent=2))

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch field resource: {str(e)}")


class WeatherDataResource(ResourceProvider):
    """
    Weather Data Resource Provider

    Provides access to weather forecasts, historical weather data,
    and agricultural weather advisories.
    """

    async def list_resources(self) -> list[Resource]:
        """List all available weather resources"""
        return [
            Resource(
                uri="weather://current",
                name="Current Weather Conditions",
                description="Current weather conditions for registered fields",
            ),
            Resource(
                uri="weather://forecast/7day",
                name="7-Day Weather Forecast",
                description="7-day weather forecast for all locations",
            ),
            Resource(
                uri="weather://forecast/14day",
                name="14-Day Weather Forecast",
                description="14-day extended weather forecast",
            ),
            Resource(
                uri="weather://advisories",
                name="Agricultural Weather Advisories",
                description="Weather-based agricultural advisories and alerts",
            ),
            Resource(
                uri="weather://historical/30day",
                name="30-Day Historical Weather",
                description="Historical weather data for the last 30 days",
            ),
        ]

    async def get_resource(self, uri: str) -> ResourceContent:
        """Get weather resource content"""
        import json

        if not uri.startswith("weather://"):
            raise ValueError(f"Invalid weather URI: {uri}")

        resource_path = uri.replace("weather://", "")

        try:
            if resource_path == "current":
                response = await self.client.get(f"{self.base_url}/api/weather/current")
            elif resource_path.startswith("forecast/"):
                days = resource_path.split("/")[1].replace("day", "")
                response = await self.client.get(
                    f"{self.base_url}/api/weather/forecast", params={"days": days}
                )
            elif resource_path == "advisories":
                response = await self.client.get(f"{self.base_url}/api/weather/advisories")
            elif resource_path.startswith("historical/"):
                days = resource_path.split("/")[1].replace("day", "")
                response = await self.client.get(
                    f"{self.base_url}/api/weather/historical", params={"days": days}
                )
            else:
                raise ValueError(f"Unknown weather resource: {resource_path}")

            response.raise_for_status()
            data = response.json()

            return ResourceContent(
                uri=uri, mimeType="application/json", text=json.dumps(data, indent=2)
            )

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch weather resource: {str(e)}")


class CropCatalogResource(ResourceProvider):
    """
    Crop Catalog Resource Provider

    Provides access to crop information, growing guides, pest/disease databases,
    and agricultural best practices.
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
                    description="Complete catalog of supported crops and varieties",
                ),
            ]

            # Add resources for each crop
            for crop in crops.get("crops", []):
                crop_id = crop.get("id")
                crop_name = crop.get("name")

                resources.extend(
                    [
                        Resource(
                            uri=f"crops://{crop_id}/info",
                            name=f"{crop_name} - Information",
                            description=f"Complete information about {crop_name}",
                        ),
                        Resource(
                            uri=f"crops://{crop_id}/growing-guide",
                            name=f"{crop_name} - Growing Guide",
                            description=f"Growing guide and best practices for {crop_name}",
                        ),
                        Resource(
                            uri=f"crops://{crop_id}/pests",
                            name=f"{crop_name} - Pest Management",
                            description=f"Common pests and management strategies for {crop_name}",
                        ),
                        Resource(
                            uri=f"crops://{crop_id}/diseases",
                            name=f"{crop_name} - Disease Management",
                            description=f"Common diseases and treatment for {crop_name}",
                        ),
                    ]
                )

            return resources
        except Exception as e:
            print(f"Error listing crop resources: {e}")
            return []

    async def get_resource(self, uri: str) -> ResourceContent:
        """Get crop catalog resource content"""
        import json

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

                if resource_type == "info":
                    response = await self.client.get(f"{self.base_url}/api/crops/{crop_id}")
                elif resource_type == "growing-guide":
                    response = await self.client.get(
                        f"{self.base_url}/api/crops/{crop_id}/growing-guide"
                    )
                elif resource_type == "pests":
                    response = await self.client.get(f"{self.base_url}/api/crops/{crop_id}/pests")
                elif resource_type == "diseases":
                    response = await self.client.get(
                        f"{self.base_url}/api/crops/{crop_id}/diseases"
                    )
                else:
                    raise ValueError(f"Unknown resource type: {resource_type}")

            response.raise_for_status()
            data = response.json()

            return ResourceContent(
                uri=uri, mimeType="application/json", text=json.dumps(data, indent=2)
            )

        except httpx.HTTPError as e:
            raise RuntimeError(f"Failed to fetch crop resource: {str(e)}")


class ResourceManager:
    """
    Manages all resource providers

    Coordinates multiple resource providers and provides unified access
    to all SAHOOL resources.
    """

    def __init__(self, base_url: str | None = None):
        self.providers: dict[str, ResourceProvider] = {
            "field": FieldDataResource(base_url),
            "weather": WeatherDataResource(base_url),
            "crops": CropCatalogResource(base_url),
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
                "description": "Access field data, boundaries, soil info, and activities",
                "mimeType": "application/json",
            },
            {
                "uriTemplate": "weather://{resource_type}",
                "name": "Weather Resources",
                "description": "Access weather forecasts, current conditions, and advisories",
                "mimeType": "application/json",
            },
            {
                "uriTemplate": "crops://{crop_id}/{resource_type}",
                "name": "Crop Catalog Resources",
                "description": "Access crop information, growing guides, and pest/disease management",
                "mimeType": "application/json",
            },
        ]
