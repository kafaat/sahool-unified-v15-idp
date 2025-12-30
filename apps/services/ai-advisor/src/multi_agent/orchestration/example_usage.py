"""
Master Advisor Usage Example
مثال على استخدام المستشار الرئيسي

Demonstrates how to initialize and use the MasterAdvisor for multi-agent coordination.
يوضح كيفية تهيئة واستخدام المستشار الرئيسي لتنسيق الوكلاء المتعددين.
"""

import asyncio
import os
from datetime import datetime

from master_advisor import (
    MasterAdvisor,
    AgentRegistry,
    ContextStore,
    NATSBridge,
    FarmerQuery,
    QueryType,
)

# Import existing agents
# استيراد الوكلاء الموجودين
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from agents import (
    FieldAnalystAgent,
    DiseaseExpertAgent,
    IrrigationAdvisorAgent,
    YieldPredictorAgent,
    EcologicalExpertAgent,
)
from tools import CropHealthTool, WeatherTool, SatelliteTool
from rag import KnowledgeRetriever, EmbeddingsManager


async def setup_master_advisor():
    """
    Setup and configure the MasterAdvisor
    إعداد وتكوين المستشار الرئيسي
    """
    print("Setting up Master Advisor...")
    print("جاري إعداد المستشار الرئيسي...")

    # 1. Initialize tools
    # تهيئة الأدوات
    crop_health_tool = CropHealthTool()
    weather_tool = WeatherTool()
    satellite_tool = SatelliteTool()

    # 2. Initialize RAG retriever (optional)
    # تهيئة مسترجع RAG (اختياري)
    try:
        embeddings_manager = EmbeddingsManager()
        retriever = KnowledgeRetriever(embeddings_manager)
    except Exception as e:
        print(f"Warning: Could not initialize RAG retriever: {e}")
        retriever = None

    # 3. Initialize agents
    # تهيئة الوكلاء
    print("\nInitializing agents...")
    print("جاري تهيئة الوكلاء...")

    field_analyst = FieldAnalystAgent(
        name="field_analyst",
        tools=[satellite_tool],
        retriever=retriever
    )

    disease_expert = DiseaseExpertAgent(
        name="disease_expert",
        tools=[crop_health_tool],
        retriever=retriever
    )

    irrigation_advisor = IrrigationAdvisorAgent(
        name="irrigation_advisor",
        tools=[weather_tool],
        retriever=retriever
    )

    yield_predictor = YieldPredictorAgent(
        name="yield_predictor",
        tools=[weather_tool, satellite_tool],
        retriever=retriever
    )

    ecological_expert = EcologicalExpertAgent(
        name="ecological_expert",
        tools=[],
        retriever=retriever
    )

    # 4. Create Agent Registry and register agents
    # إنشاء سجل الوكلاء وتسجيل الوكلاء
    print("\nRegistering agents...")
    print("جاري تسجيل الوكلاء...")

    registry = AgentRegistry()

    registry.register_agent(
        "field_analyst",
        field_analyst,
        [QueryType.FIELD_ANALYSIS, QueryType.GENERAL_ADVISORY]
    )

    registry.register_agent(
        "disease_expert",
        disease_expert,
        [QueryType.DIAGNOSIS, QueryType.TREATMENT, QueryType.PEST_MANAGEMENT]
    )

    registry.register_agent(
        "irrigation_advisor",
        irrigation_advisor,
        [QueryType.IRRIGATION, QueryType.FERTILIZATION]
    )

    registry.register_agent(
        "yield_predictor",
        yield_predictor,
        [QueryType.YIELD_PREDICTION, QueryType.HARVEST_PLANNING]
    )

    registry.register_agent(
        "ecological_expert",
        ecological_expert,
        [QueryType.ECOLOGICAL_TRANSITION, QueryType.GENERAL_ADVISORY]
    )

    # 5. Initialize support components
    # تهيئة المكونات الداعمة
    context_store = ContextStore()

    # Optional: Initialize NATS bridge
    # اختياري: تهيئة جسر NATS
    nats_url = os.getenv("NATS_URL", "nats://nats:4222")
    nats_bridge = NATSBridge(nats_url)
    # await nats_bridge.connect()  # Uncomment when NATS is fully implemented

    # 6. Create MasterAdvisor
    # إنشاء المستشار الرئيسي
    print("\nCreating Master Advisor...")
    print("جاري إنشاء المستشار الرئيسي...")

    master_advisor = MasterAdvisor(
        agent_registry=registry,
        context_store=context_store,
        nats_bridge=nats_bridge,
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
        model="claude-3-5-sonnet-20241022"
    )

    print("\n✓ Master Advisor ready!")
    print("✓ المستشار الرئيسي جاهز!")

    return master_advisor


async def example_queries(master_advisor: MasterAdvisor):
    """
    Run example queries through the MasterAdvisor
    تشغيل استفسارات تجريبية عبر المستشار الرئيسي
    """
    print("\n" + "="*60)
    print("Running Example Queries")
    print("تشغيل استفسارات تجريبية")
    print("="*60)

    # Example 1: Disease Diagnosis (Arabic)
    # مثال 1: تشخيص مرض (عربي)
    print("\n1. Disease Diagnosis Query (Arabic):")
    print("1. استفسار تشخيص مرض (عربي):")

    query1 = FarmerQuery(
        query="أوراق الطماطم في حقلي تتحول إلى اللون الأصفر وبها بقع بنية. ما المشكلة وكيف أعالجها؟",
        farmer_id="farmer_123",
        field_id="field_456",
        crop_type="tomato",
        language="ar",
        priority="high"
    )

    response1 = await master_advisor.process_query(query1, session_id="session_1")

    print(f"\nQuery Type: {response1.query_type.value}")
    print(f"Execution Mode: {response1.execution_mode.value}")
    print(f"Agents Consulted: {', '.join(response1.agents_consulted)}")
    print(f"Confidence: {response1.confidence:.2f}")
    print(f"\nAnswer:\n{response1.answer[:300]}...")
    if response1.recommendations:
        print(f"\nRecommendations:")
        for i, rec in enumerate(response1.recommendations[:3], 1):
            print(f"  {i}. {rec}")

    # Example 2: Irrigation Advice (English)
    # مثال 2: نصائح الري (إنجليزي)
    print("\n" + "-"*60)
    print("\n2. Irrigation Optimization Query (English):")
    print("2. استفسار تحسين الري (إنجليزي):")

    query2 = FarmerQuery(
        query="When should I irrigate my wheat field? It's in the vegetative stage and we haven't had rain for 2 weeks.",
        farmer_id="farmer_123",
        field_id="field_789",
        crop_type="wheat",
        language="en",
        context={
            "soil_type": "clay",
            "last_irrigation": "14 days ago",
            "current_temperature": 28
        }
    )

    response2 = await master_advisor.process_query(query2, session_id="session_1")

    print(f"\nQuery Type: {response2.query_type.value}")
    print(f"Agents Consulted: {', '.join(response2.agents_consulted)}")
    print(f"\nAnswer:\n{response2.answer[:300]}...")

    # Example 3: Emergency - Council Mode
    # مثال 3: طوارئ - وضع المجلس
    print("\n" + "-"*60)
    print("\n3. Emergency Query (Council Mode):")
    print("3. استفسار طارئ (وضع المجلس):")

    query3 = FarmerQuery(
        query="محصول الذرة بدأ يموت بشكل سريع! ما الحل السريع؟",
        farmer_id="farmer_123",
        field_id="field_789",
        crop_type="corn",
        language="ar",
        priority="emergency"  # This will trigger council mode
    )

    response3 = await master_advisor.process_query(query3, session_id="session_2")

    print(f"\nQuery Type: {response3.query_type.value}")
    print(f"Execution Mode: {response3.execution_mode.value}")
    print(f"Agents Consulted: {', '.join(response3.agents_consulted)}")
    print(f"\nAnswer:\n{response3.answer[:300]}...")
    if response3.warnings:
        print(f"\nWarnings:")
        for warning in response3.warnings:
            print(f"  ⚠ {warning}")

    # Example 4: Complex Multi-Agent Query
    # مثال 4: استفسار معقد متعدد الوكلاء
    print("\n" + "-"*60)
    print("\n4. Complex Multi-Agent Query:")
    print("4. استفسار معقد متعدد الوكلاء:")

    query4 = FarmerQuery(
        query="I want to maximize my corn yield this season. What should I do regarding irrigation, fertilization, and disease prevention?",
        farmer_id="farmer_456",
        field_id="field_001",
        crop_type="corn",
        language="en",
        context={
            "field_size_hectares": 10,
            "growth_stage": "vegetative",
            "soil_analysis": {
                "nitrogen": "medium",
                "phosphorus": "low",
                "potassium": "high"
            }
        }
    )

    response4 = await master_advisor.process_query(query4, session_id="session_3")

    print(f"\nQuery Type: {response4.query_type.value}")
    print(f"Execution Mode: {response4.execution_mode.value}")
    print(f"Agents Consulted: {', '.join(response4.agents_consulted)}")
    print(f"Confidence: {response4.confidence:.2f}")
    print(f"\nAnswer:\n{response4.answer[:400]}...")
    if response4.next_steps:
        print(f"\nNext Steps:")
        for i, step in enumerate(response4.next_steps, 1):
            print(f"  {i}. {step}")

    print("\n" + "="*60)
    print("Examples Complete!")
    print("اكتملت الأمثلة!")
    print("="*60)


async def main():
    """
    Main function to run the example
    الدالة الرئيسية لتشغيل المثال
    """
    print("\n" + "="*60)
    print("SAHOOL Master Advisor - Usage Example")
    print("مثال استخدام المستشار الرئيسي لنظام SAHOOL")
    print("="*60)

    try:
        # Setup Master Advisor
        # إعداد المستشار الرئيسي
        master_advisor = await setup_master_advisor()

        # Run example queries
        # تشغيل استفسارات تجريبية
        await example_queries(master_advisor)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        print(f"❌ خطأ: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the example
    # تشغيل المثال
    asyncio.run(main())
