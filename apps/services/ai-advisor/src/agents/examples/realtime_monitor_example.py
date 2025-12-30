"""
Example Usage of Real-time Monitor Agent
مثال على استخدام وكيل المراقبة في الوقت الفعلي

This example demonstrates how to use the Real-time Monitor Agent for continuous
farm monitoring and alert generation.

يوضح هذا المثال كيفية استخدام وكيل المراقبة في الوقت الفعلي للمراقبة المستمرة
للمزرعة وإنشاء التنبيهات.
"""

import asyncio
from datetime import datetime

from agents.realtime_monitor_agent import (
    RealtimeMonitorAgent,
    MonitoringConfig,
    AlertType,
    AlertSeverity,
)


async def main():
    """
    Main example function
    الدالة الرئيسية للمثال
    """
    print("=" * 80)
    print("Real-time Monitor Agent Example")
    print("مثال وكيل المراقبة في الوقت الفعلي")
    print("=" * 80)

    # Initialize the agent | تهيئة الوكيل
    print("\n1. Initializing Real-time Monitor Agent...")
    print("   تهيئة وكيل المراقبة في الوقت الفعلي...")

    agent = RealtimeMonitorAgent()

    # Initialize NATS connection (optional) | تهيئة اتصال NATS (اختياري)
    # In production, this would connect to actual NATS server
    # في الإنتاج، سيتم الاتصال بخادم NATS الفعلي
    try:
        await agent.initialize_nats()
        print("   ✓ NATS connection initialized")
    except Exception as e:
        print(f"   ⚠ NATS not available (running in demo mode): {e}")

    # Example 1: Start monitoring a field | بدء مراقبة حقل
    print("\n2. Starting field monitoring...")
    print("   بدء مراقبة الحقل...")

    field_id = "field_001"

    # Create custom monitoring configuration | إنشاء إعدادات مراقبة مخصصة
    config = MonitoringConfig(
        sensor_check_interval=300,  # 5 minutes | 5 دقائق
        satellite_check_interval=86400,  # 24 hours | 24 ساعة
        weather_check_interval=3600,  # 1 hour | ساعة واحدة
        soil_moisture_min=25.0,
        soil_moisture_max=75.0,
        temperature_min=12.0,
        temperature_max=32.0,
        ndvi_min_threshold=0.5,
        enable_alerts=True,
        alert_languages=["ar", "en"],
    )

    result = await agent.start_monitoring(field_id, config)
    print(f"   ✓ Monitoring started: {result['status']}")
    print(f"   Started at: {result['session']['started_at']}")

    # Example 2: Check for anomalies in sensor data | التحقق من الشذوذات في بيانات أجهزة الاستشعار
    print("\n3. Checking for anomalies in sensor data...")
    print("   التحقق من الشذوذات في بيانات أجهزة الاستشعار...")

    # Simulate sensor data | محاكاة بيانات أجهزة الاستشعار
    sensor_data = {
        "soil_moisture": 18.5,  # Below threshold | أقل من الحد الأدنى
        "temperature": 28.3,
        "humidity": 65.0,
        "timestamp": datetime.utcnow().isoformat(),
    }

    anomaly_result = await agent.check_anomalies(field_id, sensor_data)
    print(f"   Anomalies detected: {anomaly_result['has_anomalies']}")
    if anomaly_result['has_anomalies']:
        for i, anomaly in enumerate(anomaly_result['anomalies'], 1):
            print(f"   {i}. Type: {anomaly['type']}")
            print(f"      Severity: {anomaly['severity'].value}")

    # Example 3: Analyze stress indicators | تحليل مؤشرات الإجهاد
    print("\n4. Analyzing crop stress indicators...")
    print("   تحليل مؤشرات إجهاد المحاصيل...")

    # Simulate vegetation indices | محاكاة مؤشرات الغطاء النباتي
    indices = {
        "ndvi": 0.42,  # Low NDVI | قيمة NDVI منخفضة
        "ndwi": 0.15,  # Low water content | محتوى مائي منخفض
        "evi": 0.38,
        "timestamp": datetime.utcnow().isoformat(),
    }

    stress_result = await agent.analyze_stress_indicators(field_id, indices)
    print(f"   Stress detected: {stress_result['has_stress']}")
    if stress_result['has_stress']:
        for i, indicator in enumerate(stress_result['stress_indicators'], 1):
            print(f"   {i}. Indicator: {indicator['indicator']}")
            print(f"      Stress type: {indicator['stress_type']}")
            print(f"      Severity: {indicator['severity'].value}")

    # Example 4: Generate an alert | إنشاء تنبيه
    print("\n5. Generating alert...")
    print("   إنشاء تنبيه...")

    alert = await agent.generate_alert(
        field_id=field_id,
        alert_type=AlertType.WATER_STRESS,
        severity=AlertSeverity.HIGH,
        data={
            "soil_moisture": sensor_data["soil_moisture"],
            "threshold": config.soil_moisture_min,
            "confidence": 0.85,
        }
    )

    print(f"   Alert generated: {alert.alert_id}")
    print(f"   Type: {alert.alert_type.value}")
    print(f"   Severity: {alert.severity.value}")
    print(f"   Message (EN): {alert.message_en}")
    print(f"   Message (AR): {alert.message_ar}")
    print(f"   Recommended actions:")
    for i, action in enumerate(alert.recommended_actions, 1):
        print(f"      {i}. {action}")

    # Example 5: Get monitoring status | الحصول على حالة المراقبة
    print("\n6. Getting monitoring status...")
    print("   الحصول على حالة المراقبة...")

    status = await agent.get_monitoring_status(field_id)
    print(f"   Status: {status['status']}")
    print(f"   Alerts generated: {status['alerts_generated']}")
    print(f"   Historical data points: {status['historical_data_points']}")

    # Example 6: Predict upcoming issues | التنبؤ بالمشاكل القادمة
    print("\n7. Predicting upcoming issues...")
    print("   التنبؤ بالمشاكل القادمة...")

    # Add some historical data for prediction | إضافة بعض البيانات التاريخية للتنبؤ
    agent.historical_data[field_id] = [
        {
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_data": {"soil_moisture": 30.0, "temperature": 25.0},
            "indices": {"ndvi": 0.65},
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_data": {"soil_moisture": 28.0, "temperature": 26.5},
            "indices": {"ndvi": 0.62},
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_data": {"soil_moisture": 25.0, "temperature": 28.0},
            "indices": {"ndvi": 0.58},
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_data": {"soil_moisture": 22.0, "temperature": 29.5},
            "indices": {"ndvi": 0.52},
        },
        {
            "timestamp": datetime.utcnow().isoformat(),
            "sensor_data": sensor_data,
            "indices": indices,
        },
    ]

    prediction = await agent.predict_issues(field_id, timeframe="24h")
    print(f"   Prediction for next 24h:")
    print(f"   Agent: {prediction['prediction']['agent']}")
    print(f"   Response: {prediction['prediction']['response'][:200]}...")

    # Example 7: Stop monitoring | إيقاف المراقبة
    print("\n8. Stopping monitoring...")
    print("   إيقاف المراقبة...")

    stop_result = await agent.stop_monitoring(field_id)
    print(f"   ✓ Monitoring stopped: {stop_result['status']}")

    # Clean up NATS connection | تنظيف اتصال NATS
    try:
        await agent.shutdown_nats()
        print("   ✓ NATS connection closed")
    except Exception:
        pass

    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("اكتمل المثال بنجاح!")
    print("=" * 80)


if __name__ == "__main__":
    # Run the example | تشغيل المثال
    asyncio.run(main())
