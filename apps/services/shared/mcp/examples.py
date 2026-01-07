"""
SAHOOL MCP Examples
===================

Example usage of SAHOOL MCP client and server.
"""

import asyncio
import logging

from .client import MCPClientContext

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def example_http_client():
    """Example: Using MCP client with HTTP transport"""
    logger.info("=" * 60)
    logger.info("Example: MCP Client with HTTP Transport")
    logger.info("=" * 60)

    async with MCPClientContext(server_url="http://localhost:8200") as client:
        # Initialize and get server info
        logger.info(f"Connected to: {client.server_info}")
        logger.info(f"Capabilities: {client.capabilities}")

        # List available tools
        tools = await client.list_tools()
        logger.info(f"\nAvailable Tools ({len(tools)}):")
        for tool in tools:
            logger.info(f"  - {tool['name']}: {tool['description']}")

        # Example 1: Get weather forecast
        logger.info("\n" + "=" * 60)
        logger.info("Example 1: Get Weather Forecast")
        logger.info("=" * 60)

        try:
            weather = await client.get_weather_forecast(
                latitude=15.5527,  # Sana'a, Yemen
                longitude=48.5164,
                days=7,
            )
            logger.info(f"Weather forecast: {weather}")
        except Exception as e:
            logger.error(f"Weather forecast failed: {e}")

        # Example 2: Analyze crop health
        logger.info("\n" + "=" * 60)
        logger.info("Example 2: Analyze Crop Health")
        logger.info("=" * 60)

        try:
            health = await client.analyze_crop_health(
                field_id="field-123", analysis_type="ndvi"
            )
            logger.info(f"Crop health: {health}")
        except Exception as e:
            logger.error(f"Crop health analysis failed: {e}")

        # Example 3: Get field data
        logger.info("\n" + "=" * 60)
        logger.info("Example 3: Get Field Data")
        logger.info("=" * 60)

        try:
            field_data = await client.get_field_data(
                field_id="field-123", include_history=True, include_sensors=True
            )
            logger.info(f"Field data: {field_data}")
        except Exception as e:
            logger.error(f"Get field data failed: {e}")

        # Example 4: Calculate irrigation
        logger.info("\n" + "=" * 60)
        logger.info("Example 4: Calculate Irrigation")
        logger.info("=" * 60)

        try:
            irrigation = await client.calculate_irrigation(
                field_id="field-123",
                crop_type="wheat",
                soil_moisture=45.5,
                growth_stage="flowering",
            )
            logger.info(f"Irrigation recommendation: {irrigation}")
        except Exception as e:
            logger.error(f"Calculate irrigation failed: {e}")

        # Example 5: Get fertilizer recommendation
        logger.info("\n" + "=" * 60)
        logger.info("Example 5: Get Fertilizer Recommendation")
        logger.info("=" * 60)

        try:
            fertilizer = await client.get_fertilizer_recommendation(
                field_id="field-123",
                crop_type="corn",
                soil_test={
                    "nitrogen_ppm": 20,
                    "phosphorus_ppm": 15,
                    "potassium_ppm": 150,
                    "ph": 6.5,
                    "organic_matter_pct": 2.5,
                },
                target_yield=8.5,
            )
            logger.info(f"Fertilizer recommendation: {fertilizer}")
        except Exception as e:
            logger.error(f"Get fertilizer recommendation failed: {e}")

        # List resources
        logger.info("\n" + "=" * 60)
        logger.info("Available Resources")
        logger.info("=" * 60)

        try:
            resources = await client.list_resources()
            logger.info(f"Total resources: {len(resources)}")
            for resource in resources[:5]:  # Show first 5
                logger.info(f"  - {resource['uri']}: {resource['name']}")
        except Exception as e:
            logger.error(f"List resources failed: {e}")

        # Get resource templates
        logger.info("\n" + "=" * 60)
        logger.info("Resource Templates")
        logger.info("=" * 60)

        try:
            templates = await client.list_resource_templates()
            for template in templates:
                logger.info(f"  - {template['uriTemplate']}: {template['description']}")
        except Exception as e:
            logger.error(f"List resource templates failed: {e}")

        # List prompts
        logger.info("\n" + "=" * 60)
        logger.info("Available Prompts")
        logger.info("=" * 60)

        try:
            prompts = await client.list_prompts()
            for prompt in prompts:
                logger.info(f"  - {prompt['name']}: {prompt['description']}")
        except Exception as e:
            logger.error(f"List prompts failed: {e}")

        # Get a prompt
        logger.info("\n" + "=" * 60)
        logger.info("Get Prompt: field_analysis")
        logger.info("=" * 60)

        try:
            prompt = await client.get_prompt(
                name="field_analysis", arguments={"field_id": "field-123"}
            )
            logger.info(f"Prompt: {prompt}")
        except Exception as e:
            logger.error(f"Get prompt failed: {e}")


async def example_low_level_client():
    """Example: Using low-level MCP client methods"""
    logger.info("=" * 60)
    logger.info("Example: Low-Level MCP Client")
    logger.info("=" * 60)

    async with MCPClientContext(server_url="http://localhost:8200") as client:
        # Call tool using low-level method
        result = await client.call_tool(
            name="get_weather_forecast",
            arguments={
                "latitude": 15.5527,
                "longitude": 48.5164,
                "days": 7,
            },
        )

        logger.info("Tool result:")
        logger.info(f"  Is Error: {result.isError}")
        logger.info(f"  Content: {result.content}")

        # Read a resource
        try:
            resource_content = await client.read_resource(uri="weather://current")
            logger.info("\nResource content:")
            logger.info(f"  URI: {resource_content.get('uri')}")
            logger.info(f"  MIME Type: {resource_content.get('mimeType')}")
            logger.info(f"  Text: {resource_content.get('text')[:200]}...")
        except Exception as e:
            logger.error(f"Read resource failed: {e}")


async def example_batch_operations():
    """Example: Batch operations with MCP client"""
    logger.info("=" * 60)
    logger.info("Example: Batch Operations")
    logger.info("=" * 60)

    async with MCPClientContext(server_url="http://localhost:8200") as client:
        # Run multiple operations concurrently
        results = await asyncio.gather(
            client.get_weather_forecast(latitude=15.5527, longitude=48.5164, days=7),
            client.analyze_crop_health(field_id="field-123", analysis_type="ndvi"),
            client.get_field_data(field_id="field-123"),
            return_exceptions=True,
        )

        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                logger.error(f"Operation {i} failed: {result}")
            else:
                logger.info(f"Operation {i} succeeded: {type(result)}")


async def main():
    """Run all examples"""
    try:
        await example_http_client()
        print("\n" + "=" * 60 + "\n")
        await example_low_level_client()
        print("\n" + "=" * 60 + "\n")
        await example_batch_operations()
    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)


if __name__ == "__main__":
    asyncio.run(main())
