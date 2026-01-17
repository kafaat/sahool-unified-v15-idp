"""
SAHOOL MCP Skills Server Examples
==================================

Examples demonstrating how to use the skills server tools:
- crop_advisor: Get AI-powered crop advisory
- farm_documentation: Access agricultural documentation
- compress_context: Optimize context for AI
- query_memory: Search farm memory

Run examples:
    python -m shared.mcp.examples_skills

Author: SAHOOL Platform Team
Updated: January 2025
"""

import asyncio
import json
import logging
from typing import Any

from shared.mcp.client import MCPClient, MCPClientContext
from shared.mcp.skills_server import SAHOOLSkillsTools

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ==================== Example 1: Direct Skill Tools Usage ====================


async def example_direct_skills_usage():
    """
    Example: Using SAHOOLSkillsTools directly
    """
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 1: Direct Skills Tools Usage")
    logger.info("=" * 70)

    tools = SAHOOLSkillsTools()

    try:
        # List available skill tools
        tool_defs = tools.get_tool_definitions()
        logger.info(f"\nAvailable skill tools ({len(tool_defs)}):")
        for tool in tool_defs:
            logger.info(f"  - {tool['name']}: {tool['description'][:70]}...")

        # Example: Invoke crop advisor skill
        logger.info("\nInvoking crop_advisor skill...")
        result = await tools.crop_advisor(
            field_id="field-north-01",
            issue_type="disease_detection",
            include_weather=True,
            include_history=True,
            confidence_threshold=0.7,
        )
        logger.info(f"Crop advisor result: success={result.success}")
        if result.success:
            logger.info(f"  Recommendations: {len(result.data.get('recommendations', []))} items")
            logger.info(f"  Confidence: {result.data.get('confidence_score')}")
        else:
            logger.info(f"  Error: {result.error}")

        # Example: Invoke farm documentation skill
        logger.info("\nInvoking farm_documentation skill...")
        result = await tools.farm_documentation(
            document_type="pest_management",
            crop_type="tomatoes",
            language="en",
            include_images=False,
        )
        logger.info(f"Documentation result: success={result.success}")
        if result.success:
            logger.info(f"  Title: {result.data.get('title')}")
            logger.info(f"  Sections: {len(result.data.get('sections', []))} items")

        # Example: Invoke context compression skill
        logger.info("\nInvoking compress_context skill...")
        sample_data = {
            "field_id": "field-north-01",
            "name": "North Field",
            "area_hectares": 50,
            "crop_type": "wheat",
            "soil_properties": {"type": "loam", "ph": 7.2, "organic_matter": 3.5},
            "current_status": "healthy",
            "ndvi": 0.75,
            "last_irrigation": "2025-01-10",
            "irrigation_status": "sufficient",
            "weather": "clear",
            "temperature": 22,
        }
        result = await tools.compress_context(
            data=sample_data,
            data_type="field",
            compression_strategy="hybrid",
            target_ratio=0.3,
        )
        logger.info(f"Compression result: success={result.success}")
        if result.success:
            logger.info(f"  Original tokens: {result.data.get('original_tokens')}")
            logger.info(f"  Compressed tokens: {result.data.get('compressed_tokens')}")
            logger.info(f"  Savings: {result.data.get('savings_percentage'):.1f}%")

        # Example: Query memory skill
        logger.info("\nInvoking query_memory skill...")
        result = await tools.query_memory(
            tenant_id="tenant-001",
            query="irrigation recommendations for wheat",
            field_id="field-north-01",
            memory_types=["recommendation", "observation"],
            time_range_days=30,
            limit=5,
            min_relevance="high",
        )
        logger.info(f"Memory query result: success={result.success}")
        if result.success:
            logger.info(f"  Results: {result.data.get('results_count')} entries found")

    finally:
        await tools.close()


# ==================== Example 2: MCP Server Integration ====================


async def example_mcp_server_integration():
    """
    Example: Using skills within MCP server
    """
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 2: MCP Server Integration")
    logger.info("=" * 70)

    try:
        from shared.mcp.server import MCPServer
        from shared.mcp.skills_server import extend_mcp_server_with_skills

        # Create server
        server = MCPServer(name="sahool-skills-server", version="1.0.0")

        # Extend with skills
        server = extend_mcp_server_with_skills(server)

        # List all available tools (base + skills)
        all_tools = server.tools.get_tool_definitions()
        logger.info(f"\nTotal tools available: {len(all_tools)}")

        # Count skill tools
        skill_tools = [t for t in all_tools if t["name"] in [
            "crop_advisor",
            "farm_documentation",
            "compress_context",
            "query_memory",
        ]]
        logger.info(f"  - Skill tools: {len(skill_tools)}")
        logger.info(f"  - Base tools: {len(all_tools) - len(skill_tools)}")

        for tool in skill_tools:
            logger.info(f"    - {tool['name']}")

        # Example: Call a skill tool through server
        logger.info("\nInvoking skill through MCP server...")
        result = await server.tools.invoke_tool(
            "compress_context",
            {
                "data": {
                    "field_id": "field-1",
                    "name": "Test Field",
                    "crop": "wheat",
                    "status": "healthy",
                },
                "data_type": "field",
                "compression_strategy": "selective",
                "target_ratio": 0.5,
            },
        )
        logger.info(f"Invocation successful: {result.success}")

        await server.close()

    except Exception as e:
        logger.error(f"Server integration error: {e}")


# ==================== Example 3: MCP Client Usage ====================


async def example_mcp_client_usage():
    """
    Example: Calling skills through MCP client
    """
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 3: MCP Client Usage")
    logger.info("=" * 70)

    try:
        # Connect to MCP server via HTTP
        async with MCPClientContext(server_url="http://localhost:8200") as client:
            # List available tools
            tools = await client.list_tools()
            logger.info(f"\nAvailable tools: {len(tools)}")

            # Find skill tools
            skill_tools = [t for t in tools if t["name"] in [
                "crop_advisor",
                "farm_documentation",
                "compress_context",
                "query_memory",
            ]]
            logger.info(f"Skill tools found: {len(skill_tools)}")

            if skill_tools:
                # Call a skill tool
                logger.info("\nCalling crop_advisor tool...")
                result = await client.call_tool(
                    "crop_advisor",
                    {
                        "field_id": "field-123",
                        "issue_type": "pest_management",
                    },
                )
                logger.info(f"Result: {result.isError == False}")

    except Exception as e:
        logger.info(f"Client connection note: {e}")
        logger.info("(This is expected if server is not running)")


# ==================== Example 4: Skill Tool Definitions ====================


async def example_skill_tool_definitions():
    """
    Example: Exploring skill tool definitions
    """
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 4: Skill Tool Definitions")
    logger.info("=" * 70)

    tools = SAHOOLSkillsTools()
    defs = tools.get_tool_definitions()

    logger.info(f"\nSkill Tools Overview ({len(defs)} tools):\n")

    for tool in defs:
        logger.info(f"Tool: {tool['name']}")
        logger.info(f"Description: {tool['description']}")
        logger.info("Parameters:")

        input_schema = tool.get("inputSchema", {})
        properties = input_schema.get("properties", {})

        for param_name, param_spec in properties.items():
            param_type = param_spec.get("type", "unknown")
            param_desc = param_spec.get("description", "")
            param_default = param_spec.get("default", "")
            logger.info(f"  - {param_name} ({param_type})")
            logger.info(f"      {param_desc}")
            if param_default:
                logger.info(f"      (default: {param_default})")

        required = input_schema.get("required", [])
        if required:
            logger.info(f"Required: {', '.join(required)}")

        logger.info()

    await tools.close()


# ==================== Example 5: Context Compression Details ====================


async def example_context_compression_details():
    """
    Example: Detailed context compression use case
    """
    logger.info("\n" + "=" * 70)
    logger.info("EXAMPLE 5: Context Compression Details")
    logger.info("=" * 70)

    tools = SAHOOLSkillsTools()

    try:
        # Sample large field data
        field_data = {
            "field_id": "field-north-01",
            "name": "North Field",
            "location": {"latitude": 15.5527, "longitude": 48.5164},
            "area_hectares": 50,
            "crop_type": "wheat",
            "growth_stage": "vegetative",
            "soil_properties": {
                "type": "loam",
                "ph": 7.2,
                "organic_matter": 3.5,
                "nitrogen_ppm": 25,
                "phosphorus_ppm": 15,
                "potassium_ppm": 200,
            },
            "current_status": "healthy",
            "ndvi": 0.75,
            "last_irrigation": "2025-01-10",
            "irrigation_status": "sufficient",
            "moisture_level": 65,
            "weather": "clear",
            "temperature": 22,
            "humidity": 55,
            "last_activity": "irrigation",
            "notes": "Field is performing well this season. Expect good yield.",
            "history": [
                {"date": "2025-01-10", "action": "irrigation", "amount_mm": 25},
                {"date": "2025-01-05", "action": "fertilizer", "type": "NPK"},
                {"date": "2024-12-25", "action": "planting", "seed_variety": "wheat-01"},
            ],
        }

        logger.info("\nCompression Strategies Comparison:")
        logger.info(f"Original data size: {len(json.dumps(field_data))} characters")

        strategies = ["selective", "extractive", "abstractive", "hybrid"]
        for strategy in strategies:
            result = await tools.compress_context(
                data=field_data,
                data_type="field",
                compression_strategy=strategy,
                target_ratio=0.3,
            )

            if result.success:
                logger.info(f"\n{strategy.upper()}:")
                logger.info(f"  Original tokens: {result.data.get('original_tokens')}")
                logger.info(f"  Compressed tokens: {result.data.get('compressed_tokens')}")
                logger.info(f"  Compression ratio: {result.data.get('compression_ratio'):.2f}")
                logger.info(f"  Savings: {result.data.get('savings_percentage'):.1f}%")

    finally:
        await tools.close()


# ==================== Main Runner ====================


async def main():
    """Run all examples"""
    logger.info("SAHOOL MCP Skills Server Examples")
    logger.info("=" * 70)

    # Run examples
    await example_skill_tool_definitions()
    await example_direct_skills_usage()
    await example_context_compression_details()
    await example_mcp_server_integration()
    await example_mcp_client_usage()

    logger.info("\n" + "=" * 70)
    logger.info("Examples completed!")
    logger.info("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
