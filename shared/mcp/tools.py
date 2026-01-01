"""
SAHOOL MCP Tools - Agricultural Intelligence Tools
===================================================

Implements MCP tool specifications for SAHOOL agricultural platform.
Each tool follows the Model Context Protocol specification for tool invocation.
"""

import asyncio
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import httpx
from pydantic import BaseModel, Field


class ToolResult(BaseModel):
    """Standard result format for tool execution"""

    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SAHOOLTools:
    """
    SAHOOL Agricultural Tools for MCP Integration

    Provides agricultural intelligence tools that can be invoked by AI assistants
    through the Model Context Protocol.
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize SAHOOL Tools

        Args:
            base_url: Base URL for SAHOOL API (default: from env or localhost)
        """
        self.base_url = base_url or os.getenv("SAHOOL_API_URL", "http://localhost:8000")
        self.client = httpx.AsyncClient(timeout=30.0)

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()

    # ==================== Tool Definitions ====================

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get MCP tool definitions for all SAHOOL tools

        Returns:
            List of tool definitions following MCP specification
        """
        return [
            {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for a specific location. Returns temperature, humidity, precipitation, wind speed, and agricultural advisories for the next 7 days.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "latitude": {
                            "type": "number",
                            "description": "Latitude of the location",
                            "minimum": -90,
                            "maximum": 90,
                        },
                        "longitude": {
                            "type": "number",
                            "description": "Longitude of the location",
                            "minimum": -180,
                            "maximum": 180,
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days to forecast (1-14)",
                            "default": 7,
                            "minimum": 1,
                            "maximum": 14,
                        },
                    },
                    "required": ["latitude", "longitude"],
                },
            },
            {
                "name": "analyze_crop_health",
                "description": "Analyze crop health using satellite imagery and NDVI analysis. Identifies stress areas, disease risks, and provides recommendations.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Unique identifier for the agricultural field",
                        },
                        "analysis_type": {
                            "type": "string",
                            "description": "Type of analysis to perform",
                            "enum": ["ndvi", "ndwi", "full"],
                            "default": "ndvi",
                        },
                        "date": {
                            "type": "string",
                            "description": "Date for analysis in YYYY-MM-DD format (default: latest available)",
                        },
                    },
                    "required": ["field_id"],
                },
            },
            {
                "name": "get_field_data",
                "description": "Retrieve comprehensive field data including boundaries, soil properties, crop information, and historical data.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Unique identifier for the field",
                        },
                        "include_history": {
                            "type": "boolean",
                            "description": "Include historical data and activities",
                            "default": False,
                        },
                        "include_sensors": {
                            "type": "boolean",
                            "description": "Include IoT sensor data",
                            "default": False,
                        },
                    },
                    "required": ["field_id"],
                },
            },
            {
                "name": "calculate_irrigation",
                "description": "Calculate optimal irrigation requirements based on soil moisture, weather forecast, crop type, and field conditions.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Unique identifier for the field",
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop (e.g., wheat, corn, tomatoes)",
                        },
                        "soil_moisture": {
                            "type": "number",
                            "description": "Current soil moisture percentage (0-100)",
                            "minimum": 0,
                            "maximum": 100,
                        },
                        "growth_stage": {
                            "type": "string",
                            "description": "Current growth stage of the crop",
                            "enum": [
                                "germination",
                                "vegetative",
                                "flowering",
                                "fruiting",
                                "maturation",
                            ],
                        },
                    },
                    "required": [
                        "field_id",
                        "crop_type",
                        "soil_moisture",
                        "growth_stage",
                    ],
                },
            },
            {
                "name": "get_fertilizer_recommendation",
                "description": "Get fertilizer recommendations based on soil analysis, crop requirements, and growth stage. Includes NPK ratios and application schedules.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "field_id": {
                            "type": "string",
                            "description": "Unique identifier for the field",
                        },
                        "crop_type": {
                            "type": "string",
                            "description": "Type of crop being grown",
                        },
                        "soil_test": {
                            "type": "object",
                            "description": "Soil test results (NPK values, pH, organic matter)",
                            "properties": {
                                "nitrogen_ppm": {"type": "number"},
                                "phosphorus_ppm": {"type": "number"},
                                "potassium_ppm": {"type": "number"},
                                "ph": {"type": "number"},
                                "organic_matter_pct": {"type": "number"},
                            },
                        },
                        "target_yield": {
                            "type": "number",
                            "description": "Target yield in tons per hectare",
                        },
                    },
                    "required": ["field_id", "crop_type"],
                },
            },
        ]

    # ==================== Tool Implementations ====================

    async def get_weather_forecast(
        self, latitude: float, longitude: float, days: int = 7
    ) -> ToolResult:
        """
        Get weather forecast for a location

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
            days: Number of days to forecast

        Returns:
            ToolResult with weather forecast data
        """
        try:
            response = await self.client.get(
                f"{self.base_url}/api/weather/forecast",
                params={"latitude": latitude, "longitude": longitude, "days": days},
            )
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "location": {"latitude": latitude, "longitude": longitude},
                    "forecast": data.get("forecast", []),
                    "advisories": data.get("advisories", []),
                    "summary": data.get("summary", ""),
                },
                metadata={
                    "provider": data.get("provider", "unknown"),
                    "updated_at": datetime.utcnow().isoformat(),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(success=False, error=f"Weather API error: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=f"Unexpected error: {str(e)}")

    async def analyze_crop_health(
        self, field_id: str, analysis_type: str = "ndvi", date: Optional[str] = None
    ) -> ToolResult:
        """
        Analyze crop health using satellite imagery

        Args:
            field_id: Unique identifier for the field
            analysis_type: Type of analysis (ndvi, ndwi, full)
            date: Date for analysis (YYYY-MM-DD)

        Returns:
            ToolResult with crop health analysis
        """
        try:
            params = {"field_id": field_id, "analysis_type": analysis_type}
            if date:
                params["date"] = date

            response = await self.client.get(
                f"{self.base_url}/api/crop-health/analyze", params=params
            )
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "field_id": field_id,
                    "analysis_type": analysis_type,
                    "ndvi_average": data.get("ndvi_average"),
                    "health_status": data.get("health_status"),
                    "stress_areas": data.get("stress_areas", []),
                    "disease_risk": data.get("disease_risk", {}),
                    "recommendations": data.get("recommendations", []),
                },
                metadata={
                    "analysis_date": data.get("analysis_date"),
                    "satellite_source": data.get("satellite_source", "Sentinel-2"),
                    "cloud_coverage": data.get("cloud_coverage"),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(success=False, error=f"Crop health API error: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=f"Unexpected error: {str(e)}")

    async def get_field_data(
        self,
        field_id: str,
        include_history: bool = False,
        include_sensors: bool = False,
    ) -> ToolResult:
        """
        Retrieve comprehensive field data

        Args:
            field_id: Unique identifier for the field
            include_history: Include historical data
            include_sensors: Include IoT sensor data

        Returns:
            ToolResult with field data
        """
        try:
            params = {
                "include_history": include_history,
                "include_sensors": include_sensors,
            }

            response = await self.client.get(
                f"{self.base_url}/api/fields/{field_id}", params=params
            )
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "field_id": field_id,
                    "name": data.get("name"),
                    "area_hectares": data.get("area_hectares"),
                    "boundaries": data.get("boundaries", {}),
                    "soil_properties": data.get("soil_properties", {}),
                    "current_crop": data.get("current_crop", {}),
                    "history": data.get("history", []) if include_history else None,
                    "sensors": data.get("sensors", []) if include_sensors else None,
                },
                metadata={
                    "last_updated": data.get("updated_at"),
                    "owner": data.get("owner"),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(success=False, error=f"Field data API error: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=f"Unexpected error: {str(e)}")

    async def calculate_irrigation(
        self,
        field_id: str,
        crop_type: str,
        soil_moisture: float,
        growth_stage: str,
    ) -> ToolResult:
        """
        Calculate optimal irrigation requirements

        Args:
            field_id: Unique identifier for the field
            crop_type: Type of crop
            soil_moisture: Current soil moisture percentage
            growth_stage: Current growth stage

        Returns:
            ToolResult with irrigation recommendations
        """
        try:
            response = await self.client.post(
                f"{self.base_url}/api/irrigation/calculate",
                json={
                    "field_id": field_id,
                    "crop_type": crop_type,
                    "soil_moisture": soil_moisture,
                    "growth_stage": growth_stage,
                },
            )
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "field_id": field_id,
                    "recommendation": data.get("recommendation"),
                    "water_amount_mm": data.get("water_amount_mm"),
                    "duration_minutes": data.get("duration_minutes"),
                    "next_irrigation_date": data.get("next_irrigation_date"),
                    "soil_moisture_target": data.get("soil_moisture_target"),
                    "adjustment_factors": data.get("adjustment_factors", {}),
                },
                metadata={
                    "calculation_method": data.get("calculation_method"),
                    "confidence": data.get("confidence"),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(success=False, error=f"Irrigation API error: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=f"Unexpected error: {str(e)}")

    async def get_fertilizer_recommendation(
        self,
        field_id: str,
        crop_type: str,
        soil_test: Optional[Dict[str, float]] = None,
        target_yield: Optional[float] = None,
    ) -> ToolResult:
        """
        Get fertilizer recommendations

        Args:
            field_id: Unique identifier for the field
            crop_type: Type of crop
            soil_test: Soil test results
            target_yield: Target yield in tons/ha

        Returns:
            ToolResult with fertilizer recommendations
        """
        try:
            payload = {
                "field_id": field_id,
                "crop_type": crop_type,
            }
            if soil_test:
                payload["soil_test"] = soil_test
            if target_yield:
                payload["target_yield"] = target_yield

            response = await self.client.post(
                f"{self.base_url}/api/fertilizer/recommend", json=payload
            )
            response.raise_for_status()
            data = response.json()

            return ToolResult(
                success=True,
                data={
                    "field_id": field_id,
                    "crop_type": crop_type,
                    "npk_recommendation": data.get("npk_recommendation", {}),
                    "application_schedule": data.get("application_schedule", []),
                    "total_cost_estimate": data.get("total_cost_estimate"),
                    "organic_alternatives": data.get("organic_alternatives", []),
                    "warnings": data.get("warnings", []),
                },
                metadata={
                    "recommendation_basis": data.get("recommendation_basis"),
                    "confidence_score": data.get("confidence_score"),
                    "generated_at": datetime.utcnow().isoformat(),
                },
            )
        except httpx.HTTPError as e:
            return ToolResult(success=False, error=f"Fertilizer API error: {str(e)}")
        except Exception as e:
            return ToolResult(success=False, error=f"Unexpected error: {str(e)}")

    async def invoke_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> ToolResult:
        """
        Invoke a tool by name with arguments

        Args:
            tool_name: Name of the tool to invoke
            arguments: Tool arguments

        Returns:
            ToolResult from tool execution
        """
        tool_map = {
            "get_weather_forecast": self.get_weather_forecast,
            "analyze_crop_health": self.analyze_crop_health,
            "get_field_data": self.get_field_data,
            "calculate_irrigation": self.calculate_irrigation,
            "get_fertilizer_recommendation": self.get_fertilizer_recommendation,
        }

        if tool_name not in tool_map:
            return ToolResult(success=False, error=f"Unknown tool: {tool_name}")

        try:
            return await tool_map[tool_name](**arguments)
        except TypeError as e:
            return ToolResult(
                success=False, error=f"Invalid arguments for {tool_name}: {str(e)}"
            )
        except Exception as e:
            return ToolResult(success=False, error=f"Tool execution error: {str(e)}")
