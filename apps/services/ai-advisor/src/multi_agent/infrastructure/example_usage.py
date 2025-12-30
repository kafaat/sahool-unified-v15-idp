"""
NATS Bridge Usage Example
مثال استخدام جسر NATS

This example demonstrates how to use the AgentNATSBridge for agent communication.
يوضح هذا المثال كيفية استخدام AgentNATSBridge لتواصل الوكلاء.
"""

import asyncio
from typing import Dict, Any
from nats_bridge import (
    AgentNATSBridge,
    AgentMessage,
    MessageType,
    MessagePriority,
)


class ExampleAgent:
    """
    Example agent demonstrating NATS bridge usage
    وكيل مثال يوضح استخدام جسر NATS
    """

    def __init__(self, agent_id: str, nats_url: str = "nats://localhost:4222"):
        """
        Initialize example agent
        تهيئة الوكيل المثال
        """
        self.agent_id = agent_id
        self.bridge = AgentNATSBridge(
            agent_id=agent_id,
            nats_url=nats_url
        )

    async def start(self):
        """
        Start the agent and connect to NATS
        بدء الوكيل والاتصال بـ NATS
        """
        await self.bridge.connect()
        print(f"Agent {self.agent_id} started and connected to NATS")

        # Subscribe to custom topics
        # الاشتراك في مواضيع مخصصة
        await self.bridge.subscribe(
            f"sahool.agents.{self.agent_id}.request",
            self.handle_request
        )

    async def stop(self):
        """
        Stop the agent and disconnect
        إيقاف الوكيل وقطع الاتصال
        """
        await self.bridge.disconnect()
        print(f"Agent {self.agent_id} stopped")

    async def handle_request(self, message: AgentMessage):
        """
        Handle incoming requests
        معالجة الطلبات الواردة

        Args:
            message: Incoming message | الرسالة الواردة
        """
        print(f"\n[{self.agent_id}] Received request from {message.sender_id}")
        print(f"Query: {message.content.get('query')}")

        # Process the request (simulate some work)
        # معالجة الطلب (محاكاة بعض العمل)
        await asyncio.sleep(1)

        # Send response back
        # إرسال الاستجابة
        response_content = {
            "answer": f"Response from {self.agent_id}",
            "confidence": 0.95,
            "metadata": {
                "processed_at": "2024-01-01T00:00:00Z"
            }
        }

        await self.bridge.send_response(
            recipient_id=message.sender_id,
            content=response_content,
            correlation_id=message.correlation_id
        )

        print(f"[{self.agent_id}] Sent response to {message.sender_id}")

    async def request_opinion(self, target_agent: str, query: str):
        """
        Request opinion from another agent
        طلب رأي من وكيل آخر

        Args:
            target_agent: Target agent ID | معرف الوكيل المستهدف
            query: Question to ask | سؤال للطرح
        """
        print(f"\n[{self.agent_id}] Requesting opinion from {target_agent}")
        print(f"Query: {query}")

        try:
            response = await self.bridge.request_opinion(
                agent_id=target_agent,
                query=query,
                timeout=10.0,
                max_retries=3
            )

            print(f"[{self.agent_id}] Received response:")
            print(f"Answer: {response.get('answer')}")
            print(f"Confidence: {response.get('confidence')}")

            return response

        except TimeoutError as e:
            print(f"[{self.agent_id}] Request timed out: {e}")
            return None

    async def broadcast_message(self, message: str):
        """
        Broadcast message to all agents
        بث رسالة إلى جميع الوكلاء

        Args:
            message: Message to broadcast | رسالة للبث
        """
        print(f"\n[{self.agent_id}] Broadcasting: {message}")

        await self.bridge.broadcast(
            content={
                "message": message,
                "type": "announcement"
            },
            priority=MessagePriority.NORMAL
        )

    async def join_council(self, council_id: str):
        """
        Join a council for group discussions
        الانضمام إلى مجلس للمناقشات الجماعية

        Args:
            council_id: Council identifier | معرف المجلس
        """
        print(f"\n[{self.agent_id}] Joining council: {council_id}")

        await self.bridge.subscribe_to_council(
            council_id=council_id,
            handler=self.handle_council_message
        )

    async def handle_council_message(self, message: AgentMessage):
        """
        Handle council messages
        معالجة رسائل المجلس

        Args:
            message: Council message | رسالة المجلس
        """
        print(f"\n[{self.agent_id}] Council message from {message.sender_id}")
        print(f"Content: {message.content}")


async def main():
    """
    Main example demonstrating multi-agent communication
    مثال رئيسي يوضح التواصل بين الوكلاء المتعددين
    """
    print("=" * 60)
    print("NATS Bridge Multi-Agent Communication Example")
    print("مثال التواصل بين الوكلاء المتعددين باستخدام جسر NATS")
    print("=" * 60)

    # Create multiple agents
    # إنشاء وكلاء متعددين
    field_analyst = ExampleAgent("field-analyst")
    disease_expert = ExampleAgent("disease-expert")
    irrigation_advisor = ExampleAgent("irrigation-advisor")

    # Start all agents
    # بدء جميع الوكلاء
    await field_analyst.start()
    await disease_expert.start()
    await irrigation_advisor.start()

    # Wait for connections to stabilize
    # انتظار استقرار الاتصالات
    await asyncio.sleep(2)

    # Example 1: Request-Response Pattern
    # مثال 1: نمط الطلب-الاستجابة
    print("\n" + "=" * 60)
    print("Example 1: Request Opinion from Another Agent")
    print("مثال 1: طلب رأي من وكيل آخر")
    print("=" * 60)

    await field_analyst.request_opinion(
        target_agent="disease-expert",
        query="What disease might be affecting wheat crops with yellow leaves?"
    )

    await asyncio.sleep(3)

    # Example 2: Broadcast Pattern
    # مثال 2: نمط البث
    print("\n" + "=" * 60)
    print("Example 2: Broadcast to All Agents")
    print("مثال 2: بث إلى جميع الوكلاء")
    print("=" * 60)

    await field_analyst.broadcast_message(
        "New weather alert: Heavy rain expected in 24 hours"
    )

    await asyncio.sleep(2)

    # Example 3: Council Communication
    # مثال 3: اتصالات المجلس
    print("\n" + "=" * 60)
    print("Example 3: Council Group Discussion")
    print("مثال 3: مناقشة جماعية في المجلس")
    print("=" * 60)

    council_id = "crop-management-council"

    # All agents join the council
    # جميع الوكلاء ينضمون إلى المجلس
    await field_analyst.join_council(council_id)
    await disease_expert.join_council(council_id)
    await irrigation_advisor.join_council(council_id)

    await asyncio.sleep(1)

    # Field analyst sends message to council
    # محلل الحقل يرسل رسالة إلى المجلس
    await field_analyst.bridge.publish_to_council(
        council_id=council_id,
        content={
            "topic": "Crop Health Assessment",
            "message": "I've detected anomalies in field sector A-12. Need input from disease and irrigation experts."
        },
        priority=MessagePriority.HIGH
    )

    await asyncio.sleep(3)

    # Example 4: Health Check
    # مثال 4: فحص الصحة
    print("\n" + "=" * 60)
    print("Example 4: Health Check")
    print("مثال 4: فحص الصحة")
    print("=" * 60)

    health = await field_analyst.bridge.health_check()
    print(f"\nField Analyst Health Status:")
    print(f"  Connected: {health['connected']}")
    print(f"  Subscriptions: {health['subscriptions']}")
    print(f"  Pending Requests: {health['pending_requests']}")

    # Clean shutdown
    # إيقاف نظيف
    print("\n" + "=" * 60)
    print("Shutting down agents...")
    print("إيقاف الوكلاء...")
    print("=" * 60)

    await field_analyst.stop()
    await disease_expert.stop()
    await irrigation_advisor.stop()

    print("\nExample completed successfully!")
    print("اكتمل المثال بنجاح!")


if __name__ == "__main__":
    asyncio.run(main())
