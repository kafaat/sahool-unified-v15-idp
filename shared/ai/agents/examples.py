"""
Agent Examples
==============
أمثلة على الوكلاء

Example usage of SAHOOL AI agents inspired by:
- Dexter: Autonomous research agent
- OpenCode: Dual-agent pattern (Plan/Execute)
- Claude Code: Tool use and streaming

Author: SAHOOL Platform Team
Updated: January 2026
"""

import asyncio


async def example_agricultural_research():
    """
    Example: Use AgriculturalResearchAgent for crop analysis.
    مثال: استخدام وكيل البحث الزراعي لتحليل المحاصيل

    Inspired by Dexter's autonomous research pattern.
    """
    from .agricultural_research import AgriculturalResearchAgent
    from .base import AgentMode

    # Create research agent
    agent = AgriculturalResearchAgent(
        tenant_id="farm_001",
        mode=AgentMode.EXECUTE,
    )

    # Run research task
    result = await agent.run(
        task="What is the health status of wheat in Field F003? Provide recommendations.",
        context={
            "field_id": "F003",
            "crop_type": "wheat",
            "farm_id": "FARM-001",
        },
    )

    print("=== Agricultural Research Result ===")
    print(f"Success: {result['success']}")
    print(f"Steps executed: {result['steps_completed']}/{result['steps_total']}")
    print(f"Summary:\n{result['summary']}")

    return result


async def example_farm_advisor_plan_mode():
    """
    Example: Use FarmAdvisorAgent in PLAN mode (read-only).
    مثال: استخدام وكيل مستشار المزرعة في وضع التخطيط

    Inspired by OpenCode's Plan agent.
    """
    from .farm_advisor import FarmAdvisorAgent
    from .base import AgentMode

    # Create advisor in PLAN mode (safe, read-only)
    advisor = FarmAdvisorAgent(
        tenant_id="farm_001",
        mode=AgentMode.PLAN,
        preferred_language="ar",
    )

    # Ask irrigation question in Arabic
    result = await advisor.run(
        task="متى يجب أن أسقي القمح في الحقل F003؟",
        context={
            "field_id": "F003",
            "farm_id": "FARM-001",
        },
    )

    print("=== Farm Advisor (Plan Mode) ===")
    print(f"Mode: {advisor.mode.value}")
    print(f"Success: {result['success']}")
    print("This was read-only analysis - no changes were made.")

    return result


async def example_farm_advisor_execute_mode():
    """
    Example: Use FarmAdvisorAgent in EXECUTE mode with approval.
    مثال: استخدام وكيل مستشار المزرعة في وضع التنفيذ

    Inspired by OpenCode's Build agent with approval.
    """
    from .farm_advisor import FarmAdvisorAgent
    from .base import AgentMode, AgentStep

    # Approval callback
    def approve_plan(steps: list[AgentStep]) -> bool:
        print("\n=== Execution Plan Approval ===")
        for i, step in enumerate(steps):
            print(f"  {i + 1}. {step.description}")
            print(f"     {step.description_ar}")

        # In real app, this would prompt user
        # For demo, auto-approve
        print("\nPlan approved automatically for demo.")
        return True

    # Create advisor in HYBRID mode (plan then execute)
    advisor = FarmAdvisorAgent(
        tenant_id="farm_001",
        mode=AgentMode.HYBRID,
    )

    result = await advisor.run(
        task="Schedule irrigation for Field F003 based on current conditions",
        context={
            "field_id": "F003",
            "farm_id": "FARM-001",
        },
        approval_callback=approve_plan,
    )

    print("\n=== Farm Advisor (Execute Mode) ===")
    print(f"Success: {result['success']}")
    if result["success"]:
        print("Irrigation has been scheduled!")

    return result


async def example_planner_agent():
    """
    Example: Use PlannerAgent for seasonal planning.
    مثال: استخدام وكيل التخطيط للتخطيط الموسمي

    Creates detailed plans without executing anything.
    """
    from .planner import PlannerAgent

    planner = PlannerAgent(tenant_id="farm_001")

    # Create execution plan
    plan = await planner.create_plan(
        objective="Plan winter wheat planting for Field F003",
        context={
            "field_id": "F003",
            "farm_id": "FARM-001",
            "season": "winter",
        },
    )

    print("=== Execution Plan ===")
    print(f"Plan ID: {plan.plan_id}")
    print(f"Title: {plan.title}")
    print(f"Title (AR): {plan.title_ar}")
    print(f"Risk Level: {plan.risk_level}")
    print(f"Requires Approval: {plan.requires_approval}")
    print(f"\nSteps ({len(plan.steps)}):")
    for i, step in enumerate(plan.steps[:5]):  # Show first 5
        print(f"  {i + 1}. {step.get('description', 'N/A')}")

    return plan


async def example_streaming_progress():
    """
    Example: Stream agent progress in real-time.
    مثال: بث تقدم الوكيل في الوقت الفعلي

    Like Claude Code's streaming updates.
    """
    from .agricultural_research import AgriculturalResearchAgent

    agent = AgriculturalResearchAgent(tenant_id="farm_001")

    print("=== Streaming Agent Progress ===")

    async for update in agent.run_stream(
        task="Analyze crop health for Field F003",
        context={"field_id": "F003", "crop_type": "wheat"},
    ):
        update_type = update.get("type")

        if update_type == "status":
            print(f"[Status] {update.get('message')}")
            print(f"         {update.get('message_ar')}")

        elif update_type == "plan":
            print(f"[Plan] Created {update.get('total_steps')} steps")

        elif update_type == "step_start":
            print(
                f"[Step {update.get('step_number')}/{update.get('total_steps')}] Starting: {update.get('description')}"
            )

        elif update_type == "step_complete":
            status = "✓" if update.get("success") else "✗"
            print(f"[Step {update.get('step_number')}] {status} Complete")

        elif update_type == "complete":
            print(f"[Done] Success: {update.get('success')}")


async def example_multi_agent_workflow():
    """
    Example: Multi-agent workflow combining planner and executor.
    مثال: سير عمل متعدد الوكلاء يجمع بين المخطط والمنفذ

    Inspired by OpenCode's dual-agent pattern.
    """
    from .planner import PlannerAgent
    from .farm_advisor import FarmAdvisorAgent
    from .base import AgentMode

    print("=== Multi-Agent Workflow ===")

    # Step 1: Planner creates the plan (read-only)
    print("\n1. Planning phase (read-only)...")
    planner = PlannerAgent(tenant_id="farm_001")
    plan = await planner.create_plan(
        objective="Optimize irrigation for wheat field",
        context={"field_id": "F003", "farm_id": "FARM-001"},
    )
    print(f"   Plan created: {plan.title}")
    print(f"   Risk level: {plan.risk_level}")

    # Step 2: User reviews and approves
    print("\n2. Plan review...")
    print(f"   Steps: {len(plan.steps)}")
    approved = True  # Simulated approval

    # Step 3: Executor implements the plan
    if approved:
        print("\n3. Execution phase...")
        executor = FarmAdvisorAgent(
            tenant_id="farm_001",
            mode=AgentMode.EXECUTE,
        )

        result = await executor.run(
            task="Implement irrigation optimization from approved plan",
            context={
                "field_id": "F003",
                "farm_id": "FARM-001",
                "approved_plan_id": plan.plan_id,
            },
        )

        print(f"   Execution success: {result['success']}")
        print(f"   Steps completed: {result['steps_completed']}")

    return {"plan": plan, "execution_result": result if approved else None}


# Run examples
if __name__ == "__main__":
    print("SAHOOL AI Agents - Examples")
    print("=" * 50)

    # Run one example at a time
    asyncio.run(example_agricultural_research())
