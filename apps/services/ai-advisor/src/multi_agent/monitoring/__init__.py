"""
SAHOOL Multi-Agent Monitoring Module
وحدة مراقبة الوكلاء المتعدد لسهول

Performance monitoring, metrics collection, and feedback management for
agricultural AI agents.

مراقبة الأداء، جمع المقاييس، وإدارة التعليقات للوكلاء الذكيين الزراعيين.

This module provides comprehensive monitoring capabilities for the SAHOOL
multi-agent system, including:
- Real-time performance tracking / تتبع الأداء في الوقت الفعلي
- Request/response metrics / مقاييس الطلبات والاستجابات
- User feedback collection / جمع تعليقات المستخدمين
- Accuracy tracking / تتبع الدقة
- Cost monitoring / مراقبة التكلفة
- Prometheus integration / تكامل Prometheus

Example Usage / مثال الاستخدام:
    ```python
    from multi_agent.monitoring import (
        PerformanceMonitor,
        FeedbackCollector,
        AgentMetrics,
        FeedbackRating,
        ImprovementArea,
    )

    # Initialize performance monitor
    monitor = PerformanceMonitor(
        max_history=1000,
        enable_prometheus=True
    )

    # Track a request
    request_id = await monitor.record_request(
        agent_id="disease-expert",
        request_data={"query": "diagnose wheat disease"}
    )

    # Record response
    await monitor.record_response(
        agent_id="disease-expert",
        response_data={"diagnosis": "yellow rust"},
        success=True,
        latency=1.5,
        confidence=0.92,
        tokens_used=150
    )

    # Initialize feedback collector
    collector = FeedbackCollector(monitor)

    # Collect user feedback
    await collector.submit_feedback(
        request_id=request_id,
        rating=5,
        comments="Excellent diagnosis!"
    )

    # Get performance metrics
    metrics = await monitor.get_metrics("disease-expert")
    print(f"Success rate: {metrics.success_rate():.2f}%")
    print(f"Avg response time: {metrics.avg_response_time:.2f}s")
    print(f"User satisfaction: {metrics.user_satisfaction_score:.2f}/5.0")

    # Get improvement recommendations
    recommendations = await monitor.get_recommendations("disease-expert")
    for rec in recommendations:
        print(f"Area: {rec['area']} - {rec['suggestion']}")

    # Export metrics
    json_metrics = await monitor.export_metrics(format="json")
    prometheus_metrics = await monitor.export_metrics(format="prometheus")
    ```
"""

from .performance_monitor import (
    # Main classes / الفئات الرئيسية
    PerformanceMonitor,
    FeedbackCollector,

    # Data models / نماذج البيانات
    AgentMetrics,
    RequestRecord,
    FeedbackRecord,

    # Enums / التعدادات
    MetricType,
    FeedbackRating,
    ImprovementArea,

    # Prometheus availability flag / علامة توفر Prometheus
    PROMETHEUS_AVAILABLE,
)

__all__ = [
    # Main classes
    "PerformanceMonitor",
    "FeedbackCollector",

    # Data models
    "AgentMetrics",
    "RequestRecord",
    "FeedbackRecord",

    # Enums
    "MetricType",
    "FeedbackRating",
    "ImprovementArea",

    # Flags
    "PROMETHEUS_AVAILABLE",
]

__version__ = "1.0.0"
__author__ = "SAHOOL AI Team"
__description__ = "Performance monitoring and feedback system for SAHOOL multi-agent"
