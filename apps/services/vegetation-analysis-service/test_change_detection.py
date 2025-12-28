"""
Test script for Change Detection System
اختبار نظام كشف التغيرات
"""

import asyncio
from datetime import date, timedelta
from src.change_detector import (
    ChangeDetector,
    ChangeType,
    SeverityLevel,
    NDVIDataPoint,
)


async def test_change_detector():
    """Test the change detector with simulated data"""
    print("=" * 70)
    print("Testing SAHOOL Change Detection System")
    print("اختبار نظام كشف التغيرات - سهول")
    print("=" * 70)

    detector = ChangeDetector()

    # Test 1: Detect changes over time
    print("\n[Test 1] Detecting changes over 90 days...")

    # Simulate NDVI time series with a decline (water stress event)
    today = date.today()
    start_date = today - timedelta(days=90)

    ndvi_series = []
    for i in range(15):
        obs_date = start_date + timedelta(days=i*6)

        # Simulate declining NDVI (stress event)
        if i < 5:
            ndvi = 0.75  # Healthy
        elif i < 10:
            ndvi = 0.75 - (i - 5) * 0.08  # Declining
        else:
            ndvi = 0.35  # Stressed

        ndvi_series.append(
            NDVIDataPoint(
                date=obs_date,
                ndvi=round(ndvi, 3),
                ndwi=0.2 - (i * 0.02) if i >= 5 else 0.2,
                cloud_cover=10.0,
            )
        )

    report = await detector.detect_changes(
        field_id="test_field_001",
        latitude=15.5,
        longitude=44.2,
        start_date=start_date,
        end_date=today,
        crop_type="wheat",
        ndvi_timeseries=ndvi_series,
    )

    print(f"✓ Analysis Period: {report.analysis_period['start_date']} to {report.analysis_period['end_date']}")
    print(f"✓ Events Detected: {len(report.events)}")
    print(f"✓ Overall Trend: {report.overall_trend.value}")
    print(f"✓ NDVI Trend Slope: {report.ndvi_trend:.6f}")
    print(f"✓ Anomalies: {report.anomaly_count}")

    print(f"\n[Arabic Summary] {report.summary_ar}")
    print(f"[English Summary] {report.summary_en}")

    if report.events:
        print(f"\n[Detected Events]")
        for i, event in enumerate(report.events[:3], 1):
            print(f"  Event {i}:")
            print(f"    - Type: {event.change_type.value}")
            print(f"    - Severity: {event.severity.value}")
            print(f"    - Date: {event.detected_date}")
            print(f"    - NDVI Change: {event.ndvi_change:.3f} ({event.change_percent:.1f}%)")
            print(f"    - Confidence: {event.confidence:.2f}")
            print(f"    - Description (AR): {event.description_ar}")
            print(f"    - Recommendation (AR): {event.recommended_action_ar}")

    if report.recommendations_ar:
        print(f"\n[Recommendations - التوصيات]")
        for rec in report.recommendations_ar:
            print(f"  • {rec}")

    # Test 2: Compare two dates
    print("\n" + "=" * 70)
    print("[Test 2] Comparing two specific dates...")

    date1 = today - timedelta(days=30)
    date2 = today - timedelta(days=5)

    event = await detector.compare_dates(
        field_id="test_field_002",
        latitude=15.5,
        longitude=44.2,
        date1=date1,
        date2=date2,
        ndvi1=0.75,
        ndvi2=0.45,
        ndwi1=0.25,
        ndwi2=0.10,
    )

    print(f"✓ Date 1: {date1} (NDVI: {event.ndvi_before})")
    print(f"✓ Date 2: {date2} (NDVI: {event.ndvi_after})")
    print(f"✓ Change Type: {event.change_type.value}")
    print(f"✓ Severity: {event.severity.value}")
    print(f"✓ Change: {event.ndvi_change:.3f} ({event.change_percent:.1f}%)")
    print(f"✓ Confidence: {event.confidence:.2f}")
    print(f"\n  [AR] {event.description_ar}")
    print(f"  [EN] {event.description_en}")
    print(f"\n  [Recommendation AR] {event.recommended_action_ar}")
    print(f"  [Recommendation EN] {event.recommended_action_en}")

    # Test 3: Anomaly detection
    print("\n" + "=" * 70)
    print("[Test 3] Detecting anomalies...")

    # Create time series with anomaly
    normal_ndvi = 0.7
    series_with_anomaly = []

    for i in range(12):
        obs_date = start_date + timedelta(days=i*7)

        # Insert anomaly at index 6
        if i == 6:
            ndvi = 0.3  # Sudden drop
        else:
            ndvi = normal_ndvi + (0.05 if i % 2 == 0 else -0.05)

        series_with_anomaly.append(
            NDVIDataPoint(
                date=obs_date,
                ndvi=round(ndvi, 3),
                ndwi=0.2,
                cloud_cover=5.0,
            )
        )

    anomalies = await detector.detect_anomalies(series_with_anomaly)

    print(f"✓ Total Observations: {len(series_with_anomaly)}")
    print(f"✓ Anomalies Detected: {len(anomalies)}")

    if anomalies:
        print("\n[Anomaly Details]")
        for anomaly in anomalies[:3]:
            print(f"  - Date: {anomaly['date']}")
            print(f"    NDVI: {anomaly['ndvi']:.3f} (Expected: {anomaly['expected']:.3f})")
            print(f"    Deviation: {anomaly['deviation']:.3f}")
            print(f"    Z-Score: {anomaly['z_score']:.2f}")

    # Test 4: Classification logic
    print("\n" + "=" * 70)
    print("[Test 4] Testing change type classification...")

    test_cases = [
        # (ndvi_before, ndvi_after, days, description)
        (0.75, 0.25, 10, "Rapid decline (harvest)"),
        (0.20, 0.60, 30, "Growth from bare soil (planting)"),
        (0.70, 0.50, 20, "Moderate decline (stress)"),
        (0.50, 0.70, 25, "Vegetation increase"),
    ]

    for ndvi_before, ndvi_after, days, description in test_cases:
        change_type = detector.classify_change(
            ndvi_before=ndvi_before,
            ndvi_after=ndvi_after,
            days_between=days,
            season="summer",
        )
        print(f"  {description:30s} → {change_type.value}")

    print("\n" + "=" * 70)
    print("✅ All tests completed successfully!")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(test_change_detector())
