"""
Simple test for cost tracker functionality
اختبار بسيط لوظائف متتبع التكاليف
"""

import asyncio

from cost_tracker import CostTracker


async def test_cost_tracker():
    """Test basic cost tracker functionality"""
    tracker = CostTracker(
        daily_limit=10.0,
        monthly_limit=100.0,
    )

    print("Testing Cost Tracker...")
    print("-" * 50)

    # Test 1: Calculate cost
    cost = tracker.calculate_cost(
        model="claude-3-5-sonnet-20241022", input_tokens=1000, output_tokens=500
    )
    print("Test 1 - Cost Calculation:")
    print("  Model: claude-3-5-sonnet-20241022")
    print("  Input tokens: 1000, Output tokens: 500")
    print(f"  Calculated cost: ${cost:.4f}")
    print()

    # Test 2: Record usage
    record = await tracker.record_usage(
        model="claude-3-5-sonnet-20241022",
        input_tokens=1000,
        output_tokens=500,
        user_id="test_user",
        request_type="chat",
    )
    print("Test 2 - Record Usage:")
    print(f"  Timestamp: {record.timestamp}")
    print(f"  Model: {record.model}")
    print(f"  Cost: ${record.cost:.4f}")
    print(f"  User ID: {record.user_id}")
    print()

    # Test 3: Get usage stats
    stats = tracker.get_usage_stats(user_id="test_user")
    print("Test 3 - Usage Statistics:")
    print(f"  Daily cost: ${stats['daily_cost']:.4f}")
    print(f"  Monthly cost: ${stats['monthly_cost']:.4f}")
    print(f"  Daily limit: ${stats['daily_limit']:.2f}")
    print(f"  Monthly limit: ${stats['monthly_limit']:.2f}")
    print(f"  Total requests: {stats['total_requests']}")
    print()

    # Test 4: Budget check
    within_budget, message = await tracker.check_budget(user_id="test_user")
    print("Test 4 - Budget Check:")
    print(f"  Within budget: {within_budget}")
    if message:
        print(f"  Message: {message}")
    print()

    # Test 5: Multiple requests
    print("Test 5 - Multiple Requests:")
    for i in range(3):
        await tracker.record_usage(
            model="gpt-4o", input_tokens=500, output_tokens=300, user_id="test_user"
        )
        print(f"  Request {i+1} recorded")

    stats = tracker.get_usage_stats(user_id="test_user")
    print(f"  Updated daily cost: ${stats['daily_cost']:.4f}")
    print(f"  Total requests: {stats['total_requests']}")
    print()

    # Test 6: Test different models
    print("Test 6 - Different Models:")
    models = ["claude-3-opus-20240229", "gpt-4-turbo", "gemini-1.5-pro"]
    for model in models:
        cost = tracker.calculate_cost(model, 1000, 1000)
        print(f"  {model}: ${cost:.4f} (1K input + 1K output)")
    print()

    print("-" * 50)
    print("All tests completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_cost_tracker())
