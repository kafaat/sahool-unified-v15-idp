#!/usr/bin/env python3
"""
Example usage of SAHOOL SAR Soil Moisture endpoints
مثال على استخدام نقاط نهاية رطوبة التربة SAR

This script demonstrates how to:
1. Check current soil moisture
2. Detect recent irrigation events
3. Get SAR time series data
4. Interpret results for irrigation decisions
"""

import httpx
import asyncio
from datetime import datetime, timedelta


async def check_field_soil_moisture():
    """Check soil moisture for a field in Yemen"""

    # Example field in Sana'a region
    field_id = "field_sanaa_001"
    latitude = 15.3694
    longitude = 44.1910

    base_url = "http://localhost:8090"

    async with httpx.AsyncClient() as client:
        print("=" * 80)
        print("SAHOOL SAR Soil Moisture Monitoring Example")
        print("مثال على مراقبة رطوبة التربة SAR")
        print("=" * 80)

        # 1. Get current soil moisture
        print(f"\n1. Current Soil Moisture | رطوبة التربة الحالية")
        print("-" * 80)

        response = await client.get(
            f"{base_url}/v1/soil-moisture/{field_id}",
            params={"lat": latitude, "lon": longitude}
        )

        if response.status_code == 200:
            data = response.json()

            print(f"Field ID: {data['field_id']}")
            print(f"Timestamp: {data['timestamp']}")
            print(f"\nSoil Moisture:")
            print(f"  - Percentage: {data['soil_moisture']['percent']}%")
            print(f"  - Volumetric: {data['soil_moisture']['volumetric_water_content']} m³/m³")
            print(f"  - Status: {data['soil_moisture']['status']}")
            print(f"  - الحالة: {data['soil_moisture']['status_ar']}")
            print(f"\nSAR Data:")
            print(f"  - VV Backscatter: {data['sar_data']['vv_backscatter_db']} dB")
            print(f"  - VH Backscatter: {data['sar_data']['vh_backscatter_db']} dB")
            print(f"  - Incidence Angle: {data['sar_data']['incidence_angle_deg']}°")
            print(f"  - Data Source: {data['sar_data']['data_source']}")
            print(f"\nConfidence: {data['confidence'] * 100:.0f}%")
            print(f"\nRecommendation:")
            print(f"  EN: {data['recommendation_en']}")
            print(f"  AR: {data['recommendation_ar']}")

            # Decision making
            moisture = data['soil_moisture']['percent']
            if moisture < 20:
                print(f"\n⚠️  ALERT: Immediate irrigation recommended!")
                print(f"⚠️  تنبيه: يوصى بالري الفوري!")
            elif moisture < 30:
                print(f"\n⚡ Plan irrigation within 2-3 days")
                print(f"⚡ خطط للري خلال 2-3 أيام")
            else:
                print(f"\n✅ Moisture level is adequate")
                print(f"✅ مستوى الرطوبة كافٍ")

        # 2. Check irrigation events
        print(f"\n\n2. Recent Irrigation Events | أحداث الري الأخيرة")
        print("-" * 80)

        response = await client.get(
            f"{base_url}/v1/irrigation-events/{field_id}",
            params={"days": 30}
        )

        if response.status_code == 200:
            data = response.json()

            print(f"Period: Last {data['period_days']} days")
            print(f"Events detected: {data['events_detected']}")

            if data['events_detected'] > 0:
                print(f"\nSummary:")
                print(f"  - Total water applied: {data['summary']['total_water_applied_mm']} mm")
                print(f"  - Average per event: {data['summary']['average_application_mm']} mm")

                print(f"\nDetailed events:")
                for i, event in enumerate(data['events'][:5], 1):  # Show first 5
                    print(f"\n  Event {i}:")
                    print(f"    Date: {event['detected_date']}")
                    print(f"    Moisture change: {event['moisture_change']['before_percent']}% → "
                          f"{event['moisture_change']['after_percent']}% "
                          f"(+{event['moisture_change']['increase_percent']}%)")
                    print(f"    Estimated water: {event['estimated_water_mm']} mm")
                    print(f"    Confidence: {event['confidence'] * 100:.0f}%")
            else:
                print(f"No irrigation events detected in the period")
                print(f"لم يتم الكشف عن أحداث ري في الفترة")

        # 3. Get time series data
        print(f"\n\n3. SAR Time Series | السلسلة الزمنية SAR")
        print("-" * 80)

        end_date = datetime.now()
        start_date = end_date - timedelta(days=60)

        response = await client.get(
            f"{base_url}/v1/sar-timeseries/{field_id}",
            params={
                "start_date": start_date.strftime("%Y-%m-%d"),
                "end_date": end_date.strftime("%Y-%m-%d"),
                "lat": latitude,
                "lon": longitude
            }
        )

        if response.status_code == 200:
            data = response.json()

            print(f"Period: {data['start_date']} to {data['end_date']}")
            print(f"Data points: {data['data_points_count']}")

            print(f"\nStatistics:")
            stats = data['statistics']
            print(f"  - Average moisture: {stats['average_moisture_percent']}%")
            print(f"  - Range: {stats['min_moisture_percent']}% - {stats['max_moisture_percent']}%")
            print(f"  - Variability: {stats['moisture_range_percent']}%")
            print(f"  - Trend: {stats['trend']}")

            # Show recent data points
            print(f"\nRecent acquisitions:")
            for point in data['timeseries'][-5:]:  # Last 5 points
                date = datetime.fromisoformat(point['acquisition_date'])
                print(f"  {date.strftime('%Y-%m-%d')}: "
                      f"{point['soil_moisture_percent']:5.1f}% "
                      f"(VV: {point['backscatter']['vv_db']:6.1f} dB, "
                      f"VH: {point['backscatter']['vh_db']:6.1f} dB) "
                      f"[{point['orbit_direction']}]")

            # Trend analysis
            if stats['trend'] == 'increasing':
                print(f"\n📈 Soil moisture is increasing (recent rainfall or irrigation)")
                print(f"📈 رطوبة التربة تتزايد (أمطار أو ري حديث)")
            elif stats['trend'] == 'decreasing':
                print(f"\n📉 Soil moisture is decreasing (consider irrigation)")
                print(f"📉 رطوبة التربة تتناقص (فكر في الري)")
            else:
                print(f"\n➡️  Soil moisture is stable")
                print(f"➡️  رطوبة التربة مستقرة")

        print("\n" + "=" * 80)
        print("✅ Analysis complete | اكتمل التحليل")
        print("=" * 80)


if __name__ == "__main__":
    print("\nNote: Make sure the satellite service is running on port 8090")
    print("ملاحظة: تأكد من تشغيل خدمة الأقمار الصناعية على المنفذ 8090\n")

    try:
        asyncio.run(check_field_soil_moisture())
    except httpx.ConnectError:
        print("\n❌ Error: Cannot connect to satellite service")
        print("❌ خطأ: لا يمكن الاتصال بخدمة الأقمار الصناعية")
        print("\nStart the service with:")
        print("  cd apps/services/satellite-service")
        print("  uvicorn src.main:app --port 8090")
