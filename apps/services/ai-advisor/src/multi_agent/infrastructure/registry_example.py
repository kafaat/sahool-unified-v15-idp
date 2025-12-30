"""
Agent Registry Client Usage Example
مثال استخدام عميل سجل الوكلاء

Demonstrates how to use the AgentRegistryClient for dynamic agent discovery.
يوضح كيفية استخدام عميل سجل الوكلاء للاكتشاف الديناميكي.
"""

import asyncio
from datetime import datetime
from .registry_client import (
    AgentCard,
    AgentCapability,
    AgentStatus,
    AgentRegistryClient,
)


async def main():
    """
    Example usage of Agent Registry Client
    مثال على استخدام عميل سجل الوكلاء
    """
    # ═══════════════════════════════════════════════════════════════════════
    # Initialize Registry Client
    # تهيئة عميل السجل
    # ═══════════════════════════════════════════════════════════════════════

    print("=" * 80)
    print("🌾 SAHOOL Agent Registry - Usage Example")
    print("مثال استخدام سجل وكلاء سهول")
    print("=" * 80)

    # Connect to Redis-backed registry
    async with AgentRegistryClient(
        redis_url="redis://localhost:6379/0",
        key_prefix="sahool:agents:",
        cache_ttl=300,
        agent_ttl=3600,
    ) as registry:

        # ═══════════════════════════════════════════════════════════════════
        # Register Agents
        # تسجيل الوكلاء
        # ═══════════════════════════════════════════════════════════════════

        print("\n📝 Registering Agents / تسجيل الوكلاء\n")

        # Disease Expert Agent
        disease_agent = AgentCard(
            agent_id="disease-expert",
            name="Disease Expert Agent",
            description="AI agent specialized in diagnosing crop diseases and recommending treatments",
            description_ar="وكيل ذكاء اصطناعي متخصص في تشخيص أمراض المحاصيل والتوصية بالعلاجات",
            capabilities=[
                AgentCapability.DIAGNOSIS,
                AgentCapability.TREATMENT,
                AgentCapability.IMAGE_ANALYSIS,
            ],
            skills=["plant_pathology", "disease_identification", "treatment_planning"],
            model="claude-3-5-sonnet-20241022",
            endpoint="http://localhost:8112/agents/disease-expert",
            status=AgentStatus.ACTIVE,
            performance_score=0.92,
            tags=["disease", "diagnosis", "أمراض", "تشخيص"],
        )
        await registry.register_agent(disease_agent)
        print(f"✅ Registered: {disease_agent.name}")

        # Irrigation Advisor Agent
        irrigation_agent = AgentCard(
            agent_id="irrigation-advisor",
            name="Irrigation Advisor Agent",
            description="Optimizes irrigation schedules based on soil, weather, and crop needs",
            description_ar="يحسن جداول الري بناءً على التربة والطقس واحتياجات المحاصيل",
            capabilities=[
                AgentCapability.IRRIGATION,
                AgentCapability.WEATHER_ANALYSIS,
                AgentCapability.SOIL_SCIENCE,
            ],
            skills=["water_management", "scheduling", "soil_moisture"],
            model="claude-3-5-sonnet-20241022",
            endpoint="http://localhost:8112/agents/irrigation-advisor",
            status=AgentStatus.ACTIVE,
            performance_score=0.88,
            tags=["irrigation", "water", "ري", "مياه"],
        )
        await registry.register_agent(irrigation_agent)
        print(f"✅ Registered: {irrigation_agent.name}")

        # Yield Predictor Agent
        yield_agent = AgentCard(
            agent_id="yield-predictor",
            name="Yield Prediction Agent",
            description="Forecasts crop yields using satellite data and weather patterns",
            description_ar="يتنبأ بمحصول المحاصيل باستخدام بيانات الأقمار الصناعية وأنماط الطقس",
            capabilities=[
                AgentCapability.YIELD_PREDICTION,
                AgentCapability.SATELLITE_ANALYSIS,
                AgentCapability.WEATHER_ANALYSIS,
            ],
            skills=["forecasting", "data_analysis", "satellite_imagery"],
            model="claude-3-5-sonnet-20241022",
            endpoint="http://localhost:8112/agents/yield-predictor",
            status=AgentStatus.ACTIVE,
            performance_score=0.85,
            tags=["yield", "prediction", "محصول", "توقع"],
        )
        await registry.register_agent(yield_agent)
        print(f"✅ Registered: {yield_agent.name}")

        # Ecological Expert Agent
        ecological_agent = AgentCard(
            agent_id="ecological-expert",
            name="Ecological Expert Agent",
            description="Analyzes ecological impact and sustainability of farming practices",
            description_ar="يحلل التأثير البيئي واستدامة الممارسات الزراعية",
            capabilities=[
                AgentCapability.ECOLOGICAL,
                AgentCapability.SOIL_SCIENCE,
            ],
            skills=["sustainability", "environmental_impact", "biodiversity"],
            model="claude-3-5-sonnet-20241022",
            endpoint="http://localhost:8112/agents/ecological-expert",
            status=AgentStatus.ACTIVE,
            performance_score=0.90,
            tags=["ecology", "sustainability", "بيئة", "استدامة"],
        )
        await registry.register_agent(ecological_agent)
        print(f"✅ Registered: {ecological_agent.name}")

        # ═══════════════════════════════════════════════════════════════════
        # Agent Discovery
        # اكتشاف الوكلاء
        # ═══════════════════════════════════════════════════════════════════

        print("\n🔍 Discovering Agents / اكتشاف الوكلاء\n")

        # Discover agents with diagnosis capability
        print("1. Finding agents with DIAGNOSIS capability:")
        diagnosis_agents = await registry.discover_agents([AgentCapability.DIAGNOSIS])
        for agent in diagnosis_agents:
            print(f"   - {agent.name} (Score: {agent.performance_score:.2f})")

        # Discover agents with multiple capabilities
        print("\n2. Finding agents with IRRIGATION + WEATHER_ANALYSIS:")
        irrigation_agents = await registry.discover_agents([
            AgentCapability.IRRIGATION,
            AgentCapability.WEATHER_ANALYSIS,
        ])
        for agent in irrigation_agents:
            print(f"   - {agent.name} (Score: {agent.performance_score:.2f})")

        # Get best agent for a specific capability
        print("\n3. Getting best agent for YIELD_PREDICTION:")
        best_yield_agent = await registry.get_best_agent(AgentCapability.YIELD_PREDICTION)
        if best_yield_agent:
            print(f"   ⭐ {best_yield_agent.name}")
            print(f"      Performance Score: {best_yield_agent.performance_score:.2f}")
            print(f"      Endpoint: {best_yield_agent.endpoint}")

        # ═══════════════════════════════════════════════════════════════════
        # Agent Status Management
        # إدارة حالة الوكلاء
        # ═══════════════════════════════════════════════════════════════════

        print("\n🔄 Managing Agent Status / إدارة حالة الوكلاء\n")

        # Update agent status
        print("1. Setting disease-expert to BUSY:")
        await registry.update_status("disease-expert", AgentStatus.BUSY)
        agent = await registry.get_agent("disease-expert")
        print(f"   Status: {agent.status.value}")

        # Send heartbeat
        print("\n2. Sending heartbeat for irrigation-advisor:")
        await registry.heartbeat("irrigation-advisor")
        agent = await registry.get_agent("irrigation-advisor")
        print(f"   Last heartbeat: {agent.last_heartbeat.isoformat()}")

        # Update performance score
        print("\n3. Updating performance score for yield-predictor:")
        await registry.update_performance("yield-predictor", 0.91)
        agent = await registry.get_agent("yield-predictor")
        print(f"   New score: {agent.performance_score:.2f}")

        # ═══════════════════════════════════════════════════════════════════
        # Registry Statistics
        # إحصائيات السجل
        # ═══════════════════════════════════════════════════════════════════

        print("\n📊 Registry Statistics / إحصائيات السجل\n")

        stats = await registry.get_registry_stats()
        print(f"Total Agents: {stats['total_agents']}")
        print(f"Average Performance: {stats['average_performance']:.3f}")
        print(f"\nStatus Distribution:")
        for status, count in stats['status_distribution'].items():
            print(f"  - {status}: {count}")
        print(f"\nCapability Distribution:")
        for capability, count in stats['capability_distribution'].items():
            print(f"  - {capability}: {count}")

        # ═══════════════════════════════════════════════════════════════════
        # Cleanup
        # تنظيف
        # ═══════════════════════════════════════════════════════════════════

        print("\n🧹 Cleaning Up / تنظيف\n")

        # Deregister an agent
        await registry.deregister_agent("ecological-expert")
        print("✅ Deregistered ecological-expert")

        # Verify it's gone
        agent = await registry.get_agent("ecological-expert")
        print(f"Agent found: {agent is not None}")

    print("\n" + "=" * 80)
    print("✅ Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())
