"""
SAHOOL Multi-Agent Performance Monitoring - Example Usage
مثال استخدام نظام مراقبة الأداء للوكلاء المتعدد لسهول

Demonstrates how to use the performance monitoring and feedback system
for agricultural AI agents.

يوضح كيفية استخدام نظام مراقبة الأداء والتعليقات
للوكلاء الذكيين الزراعيين.
"""

import asyncio
from datetime import timedelta
from performance_monitor import (
    PerformanceMonitor,
    FeedbackCollector,
    FeedbackRating,
    ImprovementArea,
    PROMETHEUS_AVAILABLE,
)


# ═══════════════════════════════════════════════════════════════════════════════
# Example 1: Basic Performance Monitoring
# مثال 1: مراقبة الأداء الأساسية
# ═══════════════════════════════════════════════════════════════════════════════

async def example_basic_monitoring():
    """
    Basic performance monitoring example
    مثال مراقبة الأداء الأساسية
    """
    print("\n" + "="*80)
    print("Example 1: Basic Performance Monitoring")
    print("مثال 1: مراقبة الأداء الأساسية")
    print("="*80 + "\n")

    # Initialize performance monitor
    monitor = PerformanceMonitor(
        max_history=1000,
        percentile_window=100,
        enable_prometheus=True
    )

    # Simulate agent requests
    agent_id = "disease-expert"

    print(f"📊 Tracking requests for agent: {agent_id}\n")

    for i in range(10):
        # Record request
        request_id = await monitor.record_request(
            agent_id=agent_id,
            request_data={
                "agent_type": "disease_diagnosis",
                "query": f"Diagnose wheat disease {i+1}",
                "language": "ar"
            }
        )

        # Simulate processing time
        await asyncio.sleep(0.1)

        # Record response
        success = i < 9  # Fail the last one for testing
        latency = 1.5 + (i * 0.1)  # Increasing latency
        confidence = 0.85 + (i * 0.01)  # Increasing confidence

        await monitor.record_response(
            agent_id=agent_id,
            response_data={
                "diagnosis": "yellow_rust" if success else None,
                "treatment": "fungicide_application" if success else None,
            },
            success=success,
            latency=latency,
            confidence=confidence,
            tokens_used=150 + (i * 10),
            error="Model timeout" if not success else None
        )

        print(f"✓ Request {i+1}: {'Success' if success else 'Failed'} "
              f"(latency: {latency:.2f}s, confidence: {confidence:.2%})")

    # Get metrics
    metrics = await monitor.get_metrics(agent_id)

    print(f"\n📈 Agent Metrics for {agent_id}:")
    print(f"  Total Requests: {metrics.total_requests}")
    print(f"  Success Rate: {metrics.success_rate():.2f}%")
    print(f"  Error Rate: {metrics.error_rate():.2f}%")
    print(f"  Avg Response Time: {metrics.avg_response_time:.2f}s")
    print(f"  P95 Response Time: {metrics.p95_response_time:.2f}s")
    print(f"  P99 Response Time: {metrics.p99_response_time:.2f}s")
    print(f"  Avg Confidence: {metrics.avg_confidence:.2%}")
    print(f"  Total Tokens: {metrics.tokens_used}")
    print(f"  Estimated Cost: ${metrics.cost_estimate:.4f}")
    print(f"  Cost per Request: ${metrics.cost_per_request():.4f}")

    return monitor, agent_id


# ═══════════════════════════════════════════════════════════════════════════════
# Example 2: User Feedback Collection
# مثال 2: جمع تعليقات المستخدمين
# ═══════════════════════════════════════════════════════════════════════════════

async def example_feedback_collection(monitor, agent_id):
    """
    User feedback collection example
    مثال جمع تعليقات المستخدمين
    """
    print("\n" + "="*80)
    print("Example 2: User Feedback Collection")
    print("مثال 2: جمع تعليقات المستخدمين")
    print("="*80 + "\n")

    # Initialize feedback collector
    collector = FeedbackCollector(monitor)

    # Get recent requests
    request_ids = list(monitor._requests.keys())[-5:]

    print(f"💬 Collecting feedback for {len(request_ids)} requests\n")

    # Simulate user feedback
    feedback_data = [
        (5, "Excellent diagnosis! Very accurate and helpful. / تشخيص ممتاز! دقيق جداً ومفيد."),
        (4, "Good response, but could be faster. / استجابة جيدة، لكن يمكن أن تكون أسرع."),
        (5, "Perfect! Exactly what I needed. / مثالي! بالضبط ما احتاجه."),
        (3, "Decent but unclear in some parts. / لائق لكن غير واضح في بعض الأجزاء."),
        (4, "Very helpful, thank you! / مفيد جداً، شكراً!"),
    ]

    for i, (request_id, (rating, comments)) in enumerate(zip(request_ids, feedback_data)):
        feedback_id = await collector.submit_feedback(
            request_id=request_id,
            rating=rating,
            comments=comments,
            agent_id=agent_id
        )
        print(f"✓ Feedback {i+1}: Rating {rating}/5 - {comments[:50]}...")

    # Get feedback summary
    summary = await collector.get_feedback_summary(agent_id)

    print(f"\n📊 Feedback Summary for {agent_id}:")
    print(f"  Total Feedback: {summary['total_feedback']}")
    print(f"  Average Rating: {summary['average_rating']:.2f}/5.0")
    print(f"  Rating Distribution:")
    for rating, count in sorted(summary['rating_distribution'].items()):
        stars = "⭐" * rating
        print(f"    {stars} ({rating}): {count}")

    # Get updated metrics
    metrics = await monitor.get_metrics(agent_id)
    print(f"\n  User Satisfaction Score: {metrics.user_satisfaction_score:.2f}/5.0")

    return collector


# ═══════════════════════════════════════════════════════════════════════════════
# Example 3: Accuracy Tracking
# مثال 3: تتبع الدقة
# ═══════════════════════════════════════════════════════════════════════════════

async def example_accuracy_tracking(monitor, collector, agent_id):
    """
    Accuracy tracking example
    مثال تتبع الدقة
    """
    print("\n" + "="*80)
    print("Example 3: Accuracy Tracking")
    print("مثال 3: تتبع الدقة")
    print("="*80 + "\n")

    # Get some requests for accuracy testing
    request_ids = list(monitor._requests.keys())[:8]

    print(f"🎯 Submitting actual outcomes for {len(request_ids)} requests\n")

    # Simulate actual outcomes
    actual_outcomes = [
        "yellow_rust",
        "yellow_rust",
        "yellow_rust",
        "brown_rust",  # This one is different
        "yellow_rust",
        "yellow_rust",
        "yellow_rust",
        "yellow_rust",
    ]

    for i, (request_id, actual) in enumerate(zip(request_ids, actual_outcomes)):
        await collector.submit_outcome(
            request_id=request_id,
            actual_result=actual,
            agent_id=agent_id
        )

        # Get predicted result
        request = monitor._requests[request_id]
        predicted = request.response_data.get('diagnosis') if request.response_data else None

        match = "✓" if predicted == actual else "✗"
        print(f"{match} Request {i+1}: Predicted={predicted}, Actual={actual}")

    # Calculate accuracy
    accuracy_outcomes = list(zip(request_ids, actual_outcomes))
    accuracy = await monitor.calculate_accuracy(agent_id, accuracy_outcomes)

    print(f"\n📊 Accuracy Metrics:")
    print(f"  Accuracy Score: {accuracy:.2%}")
    print(f"  Correct Predictions: 7/8")
    print(f"  Incorrect Predictions: 1/8")


# ═══════════════════════════════════════════════════════════════════════════════
# Example 4: Performance Recommendations
# مثال 4: توصيات الأداء
# ═══════════════════════════════════════════════════════════════════════════════

async def example_recommendations(monitor, collector, agent_id):
    """
    Performance recommendations example
    مثال توصيات الأداء
    """
    print("\n" + "="*80)
    print("Example 4: Performance Recommendations")
    print("مثال 4: توصيات الأداء")
    print("="*80 + "\n")

    # Get recommendations
    recommendations = await monitor.get_recommendations(
        agent_id=agent_id,
        threshold_response_time=2.0,
        threshold_accuracy=0.9,
        threshold_satisfaction=4.5
    )

    print(f"💡 Performance Recommendations ({len(recommendations)} found):\n")

    for i, rec in enumerate(recommendations, 1):
        severity_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🟢'
        }.get(rec.get('severity', 'low'), '⚪')

        print(f"{severity_emoji} Recommendation {i}:")
        print(f"  Area: {rec['area']} / {rec.get('area_ar', '')}")
        print(f"  Severity: {rec.get('severity', 'N/A')}")
        print(f"  Current: {rec.get('current_value', 'N/A')}")
        print(f"  Target: {rec.get('target_value', 'N/A')}")
        print(f"  Suggestion: {rec['suggestion']}")
        if 'suggestion_ar' in rec:
            print(f"  الاقتراح: {rec['suggestion_ar']}")
        print()

    # Get improvement areas from feedback
    improvement_areas = await collector.identify_improvement_areas(agent_id)

    print(f"🔍 Improvement Areas Identified ({len(improvement_areas)} areas):\n")

    for i, area in enumerate(improvement_areas, 1):
        print(f"{i}. {area.get('area', 'unknown').upper()}")
        if 'mentions' in area:
            print(f"   User Mentions: {area['mentions']}")
            print(f"   Priority: {area.get('priority', 'N/A')}")
        if 'suggestion' in area:
            print(f"   Suggestion: {area['suggestion']}")
        print()


# ═══════════════════════════════════════════════════════════════════════════════
# Example 5: Multi-Agent Monitoring
# مثال 5: مراقبة الوكلاء المتعددين
# ═══════════════════════════════════════════════════════════════════════════════

async def example_multi_agent_monitoring():
    """
    Multi-agent monitoring example
    مثال مراقبة الوكلاء المتعددين
    """
    print("\n" + "="*80)
    print("Example 5: Multi-Agent Monitoring")
    print("مثال 5: مراقبة الوكلاء المتعددين")
    print("="*80 + "\n")

    monitor = PerformanceMonitor()

    # Simulate multiple agents
    agents = [
        ("disease-expert", "disease_diagnosis"),
        ("irrigation-advisor", "irrigation_planning"),
        ("fertilizer-expert", "fertilization"),
        ("weather-analyst", "weather_analysis"),
    ]

    print(f"👥 Monitoring {len(agents)} agents\n")

    for agent_id, agent_type in agents:
        # Simulate requests
        for i in range(5):
            request_id = await monitor.record_request(
                agent_id=agent_id,
                request_data={"agent_type": agent_type, "request_num": i+1}
            )

            await monitor.record_response(
                agent_id=agent_id,
                response_data={"result": f"response_{i+1}"},
                success=True,
                latency=1.0 + (i * 0.2),
                confidence=0.8 + (i * 0.02),
                tokens_used=100 + (i * 10)
            )

    # Get all metrics
    all_metrics = await monitor.get_all_metrics()

    print("📊 All Agent Metrics:\n")

    for agent_id, metrics in all_metrics.items():
        print(f"  {agent_id}:")
        print(f"    Requests: {metrics.total_requests}")
        print(f"    Success Rate: {metrics.success_rate():.2f}%")
        print(f"    Avg Response Time: {metrics.avg_response_time:.2f}s")
        print(f"    Avg Confidence: {metrics.avg_confidence:.2%}")
        print(f"    Cost: ${metrics.cost_estimate:.4f}")
        print()


# ═══════════════════════════════════════════════════════════════════════════════
# Example 6: Metrics Export
# مثال 6: تصدير المقاييس
# ═══════════════════════════════════════════════════════════════════════════════

async def example_metrics_export(monitor, agent_id):
    """
    Metrics export example
    مثال تصدير المقاييس
    """
    print("\n" + "="*80)
    print("Example 6: Metrics Export")
    print("مثال 6: تصدير المقاييس")
    print("="*80 + "\n")

    # Export as JSON
    print("📄 Exporting metrics as JSON...\n")
    json_export = await monitor.export_metrics(format="json")
    print("JSON Export (first 500 characters):")
    print(json_export[:500] + "...\n")

    # Export as Prometheus (if available)
    if PROMETHEUS_AVAILABLE:
        print("📊 Exporting metrics as Prometheus format...\n")
        prom_export = await monitor.export_metrics(format="prometheus")
        print("Prometheus Export (first 800 characters):")
        print(prom_export[:800] + "...\n")
    else:
        print("⚠️  Prometheus export not available (prometheus_client not installed)\n")


# ═══════════════════════════════════════════════════════════════════════════════
# Main Execution
# التنفيذ الرئيسي
# ═══════════════════════════════════════════════════════════════════════════════

async def main():
    """
    Main execution function
    دالة التنفيذ الرئيسية
    """
    print("\n" + "╔" + "="*78 + "╗")
    print("║" + " "*15 + "SAHOOL Multi-Agent Performance Monitor" + " "*24 + "║")
    print("║" + " "*12 + "نظام مراقبة الأداء للوكلاء المتعدد لسهول" + " "*19 + "║")
    print("╚" + "="*78 + "╝\n")

    # Run examples
    try:
        # Example 1: Basic monitoring
        monitor, agent_id = await example_basic_monitoring()

        # Example 2: Feedback collection
        collector = await example_feedback_collection(monitor, agent_id)

        # Example 3: Accuracy tracking
        await example_accuracy_tracking(monitor, collector, agent_id)

        # Example 4: Recommendations
        await example_recommendations(monitor, collector, agent_id)

        # Example 5: Multi-agent monitoring
        await example_multi_agent_monitoring()

        # Example 6: Metrics export
        await example_metrics_export(monitor, agent_id)

        print("\n" + "="*80)
        print("✅ All examples completed successfully!")
        print("✅ جميع الأمثلة اكتملت بنجاح!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
