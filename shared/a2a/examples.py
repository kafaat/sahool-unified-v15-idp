"""
A2A Protocol Usage Examples
أمثلة استخدام بروتوكول A2A

Demonstrates various usage patterns for the A2A protocol implementation.
يوضح أنماط استخدام متنوعة لتطبيق بروتوكول A2A.
"""

import asyncio
from typing import List
import structlog

from .client import A2AClient, AgentDiscovery
from .protocol import TaskMessage, TaskState
from .agent import A2AAgent, AgentCapability

logger = structlog.get_logger()


# Example 1: Simple Agent Discovery
# مثال 1: اكتشاف وكيل بسيط

async def example_discover_agent():
    """
    Discover a single agent via its well-known endpoint
    اكتشاف وكيل واحد عبر نقطة النهاية well-known
    """
    print("\n=== Example 1: Agent Discovery ===\n")

    discovery = AgentDiscovery()

    # Discover AI Advisor agent
    # اكتشاف وكيل المستشار الذكي
    agent_card = await discovery.discover_agent("http://localhost:8001")

    if agent_card:
        print(f"✅ Discovered Agent: {agent_card.name}")
        print(f"   ID: {agent_card.agent_id}")
        print(f"   Version: {agent_card.version}")
        print(f"   Provider: {agent_card.provider}")
        print(f"\n   Capabilities ({len(agent_card.capabilities)}):")
        for cap in agent_card.capabilities:
            print(f"   - {cap.name}: {cap.description[:80]}...")
    else:
        print("❌ Failed to discover agent")


# Example 2: Send a Task
# مثال 2: إرسال مهمة

async def example_send_task():
    """
    Send a task to an agent and receive the result
    إرسال مهمة إلى وكيل واستقبال النتيجة
    """
    print("\n=== Example 2: Send Task ===\n")

    # Discover agent
    # اكتشاف الوكيل
    discovery = AgentDiscovery()
    agent_card = await discovery.discover_agent("http://localhost:8001")

    if not agent_card:
        print("❌ Agent not available")
        return

    # Create client
    # إنشاء العميل
    client = A2AClient(sender_agent_id="example-app")

    # Send disease diagnosis task
    # إرسال مهمة تشخيص المرض
    print("📤 Sending disease diagnosis task...")
    result = await client.send_task(
        agent_card=agent_card,
        task_type="crop-disease-diagnosis",
        task_description="Diagnose tomato plant disease from symptoms",
        parameters={
            "crop_type": "tomato",
            "symptoms": {
                "leaf_condition": "yellow spots with brown edges",
                "color_changes": "progressive yellowing",
                "growth_issues": "stunted growth"
            },
            "location": "greenhouse-A"
        },
        priority=8
    )

    print(f"\n📥 Received Result:")
    print(f"   State: {result.state}")
    print(f"   Execution Time: {result.execution_time_ms}ms")

    if result.state == TaskState.COMPLETED:
        print(f"   Diagnosis: {result.result.get('diagnosis', 'N/A')}")
        print(f"   Confidence: {result.result.get('confidence', 0):.2%}")
        print(f"   Treatment: {result.result.get('treatment_recommendations', [])}")
    else:
        print(f"   Error: {result.result}")


# Example 3: Streaming Task
# مثال 3: مهمة متدفقة

async def example_streaming_task():
    """
    Send a task and receive streaming progress updates
    إرسال مهمة واستقبال تحديثات التقدم المتدفقة
    """
    print("\n=== Example 3: Streaming Task ===\n")

    discovery = AgentDiscovery()
    agent_card = await discovery.discover_agent("http://localhost:8001")

    if not agent_card or not agent_card.supports_streaming:
        print("❌ Streaming not supported")
        return

    client = A2AClient(sender_agent_id="example-app")

    print("📤 Starting field analysis with streaming...")

    try:
        async for update in client.stream_task(
            agent_card=agent_card,
            task_type="field-analysis",
            task_description="Comprehensive field analysis",
            parameters={
                "field_id": "field-42",
                "crop_type": "wheat",
                "include_disease_check": True,
                "include_irrigation": True,
                "include_yield_prediction": True
            }
        ):
            if update.is_final:
                print(f"\n✅ Analysis Complete!")
                print(f"   Execution Time: {update.execution_time_ms}ms")
                print(f"   Results: {list(update.result.keys())}")
            else:
                progress_pct = (update.progress or 0) * 100
                print(f"⏳ Progress: {progress_pct:.1f}%", end="\r")

    except Exception as e:
        print(f"\n❌ Streaming failed: {e}")


# Example 4: Batch Tasks
# مثال 4: مهام دفعية

async def example_batch_tasks():
    """
    Send multiple tasks to the same agent concurrently
    إرسال مهام متعددة إلى نفس الوكيل بشكل متزامن
    """
    print("\n=== Example 4: Batch Tasks ===\n")

    discovery = AgentDiscovery()
    agent_card = await discovery.discover_agent("http://localhost:8001")

    if not agent_card:
        print("❌ Agent not available")
        return

    client = A2AClient(sender_agent_id="example-app")

    # Prepare multiple tasks
    # تحضير مهام متعددة
    tasks = [
        {
            "task_type": "crop-disease-diagnosis",
            "task_description": "Diagnose wheat rust",
            "parameters": {
                "crop_type": "wheat",
                "symptoms": {"leaf_condition": "rust-colored pustules"}
            }
        },
        {
            "task_type": "irrigation-optimization",
            "task_description": "Optimize corn irrigation",
            "parameters": {
                "crop_type": "corn",
                "growth_stage": "flowering",
                "soil_data": {"moisture_level": 0.4}
            }
        },
        {
            "task_type": "yield-prediction",
            "task_description": "Predict rice yield",
            "parameters": {
                "crop_type": "rice",
                "area_hectares": 5.0,
                "growth_stage": "maturity"
            }
        }
    ]

    print(f"📤 Sending {len(tasks)} tasks in batch...")

    results = await client.batch_send_tasks(
        tasks=tasks,
        agent_card=agent_card,
        conversation_id="batch-example-123"
    )

    print(f"\n📥 Received {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"\n   Task {i}:")
        print(f"   - State: {result.state}")
        print(f"   - Time: {result.execution_time_ms}ms")
        if result.state == TaskState.COMPLETED:
            print(f"   - Result Keys: {list(result.result.keys())}")


# Example 5: Multi-Agent Discovery
# مثال 5: اكتشاف وكلاء متعددة

async def example_multi_agent_discovery():
    """
    Discover multiple agents and search by capability
    اكتشاف وكلاء متعددة والبحث حسب القدرة
    """
    print("\n=== Example 5: Multi-Agent Discovery ===\n")

    discovery = AgentDiscovery()

    # Discover multiple agents
    # اكتشاف وكلاء متعددة
    agent_urls = [
        "http://localhost:8001",  # AI Advisor
        "http://localhost:8002",  # Weather Service
        "http://localhost:8003",  # Satellite Service
    ]

    print(f"🔍 Discovering {len(agent_urls)} agents...")
    agents = await discovery.discover_multiple(agent_urls)

    print(f"\n✅ Discovered {len(agents)} agents:")
    for agent in agents:
        print(f"\n   {agent.name} (v{agent.version})")
        print(f"   - ID: {agent.agent_id}")
        print(f"   - Capabilities: {len(agent.capabilities)}")
        print(f"   - Streaming: {'Yes' if agent.supports_streaming else 'No'}")

    # Search by capability
    # البحث حسب القدرة
    print("\n🔍 Searching for disease diagnosis capability...")
    disease_agents = discovery.get_agents_by_capability("crop-disease-diagnosis")
    print(f"   Found {len(disease_agents)} agents with disease diagnosis")

    # Search by tags
    # البحث حسب العلامات
    print("\n🔍 Searching for agriculture-related agents...")
    agri_agents = discovery.search_agents(tags=["agriculture"])
    print(f"   Found {len(agri_agents)} agricultural agents")


# Example 6: Conversation Tracking
# مثال 6: تتبع المحادثة

async def example_conversation_tracking():
    """
    Track a multi-turn conversation with an agent
    تتبع محادثة متعددة الأدوار مع وكيل
    """
    print("\n=== Example 6: Conversation Tracking ===\n")

    discovery = AgentDiscovery()
    agent_card = await discovery.discover_agent("http://localhost:8001")

    if not agent_card:
        print("❌ Agent not available")
        return

    client = A2AClient(sender_agent_id="example-app")
    conversation_id = "conv-field-analysis-123"

    print(f"💬 Starting conversation: {conversation_id}\n")

    # Turn 1: General query
    # دورة 1: استعلام عام
    print("📤 Turn 1: Ask about crop health...")
    result1 = await client.send_task(
        agent_card=agent_card,
        task_type="general-agricultural-query",
        task_description="How to improve wheat health?",
        parameters={
            "question": "What are the key factors for maintaining wheat crop health?",
            "language": "en"
        },
        conversation_id=conversation_id
    )
    print(f"📥 Response: {result1.result.get('answer', '')[:100]}...\n")

    # Turn 2: Follow-up specific to disease
    # دورة 2: متابعة محددة للمرض
    print("📤 Turn 2: Follow-up on disease prevention...")
    result2 = await client.send_task(
        agent_card=agent_card,
        task_type="crop-disease-diagnosis",
        task_description="Check for common wheat diseases",
        parameters={
            "crop_type": "wheat",
            "symptoms": {"leaf_condition": "normal"},
            "location": "field-42"
        },
        conversation_id=conversation_id
    )
    print(f"📥 Risk Assessment: {result2.result}\n")

    # Turn 3: Get irrigation advice
    # دورة 3: الحصول على نصائح الري
    print("📤 Turn 3: Get irrigation recommendations...")
    result3 = await client.send_task(
        agent_card=agent_card,
        task_type="irrigation-optimization",
        task_description="Optimize irrigation for the field",
        parameters={
            "crop_type": "wheat",
            "growth_stage": "flowering",
            "soil_data": {"moisture_level": 0.35}
        },
        conversation_id=conversation_id
    )
    print(f"📥 Irrigation Plan: {result3.result}\n")

    print(f"✅ Conversation complete with 3 turns")


# Example 7: Error Handling
# مثال 7: معالجة الأخطاء

async def example_error_handling():
    """
    Demonstrate error handling in A2A communication
    توضيح معالجة الأخطاء في اتصال A2A
    """
    print("\n=== Example 7: Error Handling ===\n")

    discovery = AgentDiscovery()
    client = A2AClient(sender_agent_id="example-app")

    # Try to discover non-existent agent
    # محاولة اكتشاف وكيل غير موجود
    print("🔍 Attempting to discover non-existent agent...")
    bad_agent = await discovery.discover_agent("http://localhost:9999")
    if bad_agent:
        print("   ✅ Agent found")
    else:
        print("   ❌ Agent not found (expected)")

    # Discover valid agent
    # اكتشاف وكيل صحيح
    agent_card = await discovery.discover_agent("http://localhost:8001")
    if not agent_card:
        print("   ⚠️  Cannot run error handling examples - agent unavailable")
        return

    # Send task with invalid parameters
    # إرسال مهمة بمعاملات غير صحيحة
    print("\n📤 Sending task with invalid parameters...")
    result = await client.send_task(
        agent_card=agent_card,
        task_type="invalid-task-type",
        task_description="This should fail",
        parameters={}
    )

    if result.state == TaskState.FAILED:
        print(f"   ❌ Task failed (expected)")
        print(f"   Error: {result.result.get('error', 'Unknown error')}")
    else:
        print(f"   ✅ Task succeeded unexpectedly")


# Main function to run all examples
# الدالة الرئيسية لتشغيل جميع الأمثلة

async def run_all_examples():
    """
    Run all A2A protocol examples
    تشغيل جميع أمثلة بروتوكول A2A
    """
    print("=" * 60)
    print("A2A Protocol Examples")
    print("أمثلة بروتوكول A2A")
    print("=" * 60)

    examples = [
        ("Agent Discovery", example_discover_agent),
        ("Send Task", example_send_task),
        ("Streaming Task", example_streaming_task),
        ("Batch Tasks", example_batch_tasks),
        ("Multi-Agent Discovery", example_multi_agent_discovery),
        ("Conversation Tracking", example_conversation_tracking),
        ("Error Handling", example_error_handling),
    ]

    for name, example_func in examples:
        try:
            await example_func()
        except Exception as e:
            print(f"\n❌ Example '{name}' failed: {e}")
            logger.error("example_failed", example=name, error=str(e))

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Run all examples
    # تشغيل جميع الأمثلة
    asyncio.run(run_all_examples())
