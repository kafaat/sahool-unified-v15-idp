"""
Field Health API Usage Example
مثال استخدام واجهة صحة الحقل

This example demonstrates how to call the Field Health API endpoint
"""

import json

import requests

# API endpoint
API_URL = "http://localhost:8080/api/v1/field-health"

# Example request payload
example_request = {
    "field_id": "field-123-abc",
    "crop_type": "wheat",
    "sensor_data": {
        "soil_moisture": 28.5,  # رطوبة التربة - Soil moisture (%)
        "temperature": 22.3,  # درجة الحرارة - Temperature (°C)
        "humidity": 65.0,  # الرطوبة النسبية - Relative humidity (%)
    },
    "ndvi_data": {
        "ndvi_value": 0.52,  # قيمة NDVI - NDVI value
        "image_date": "2024-01-15",
        "cloud_coverage": 15.0,  # تغطية السحب - Cloud coverage (%)
    },
    "weather_data": {
        "precipitation": 12.5,  # هطول الأمطار - Precipitation (mm)
        "wind_speed": 18.0,  # سرعة الرياح - Wind speed (km/h)
        "forecast_days": 7,
    },
}


def test_field_health_api():
    """Test the field health API endpoint"""
    print("=" * 60)
    print("Testing Field Health API - اختبار واجهة صحة الحقل")
    print("=" * 60)

    print("\n📤 Request Payload:")
    print(json.dumps(example_request, indent=2, ensure_ascii=False))

    try:
        # Make POST request
        response = requests.post(API_URL, json=example_request)
        response.raise_for_status()

        # Parse response
        result = response.json()

        print("\n📥 Response:")
        print("=" * 60)
        print(f"Field ID: {result['field_id']}")
        print(f"Crop Type: {result['crop_type']}")
        print(f"\n🏥 Overall Health Score: {result['overall_health_score']}/100")
        print(f"Status: {result['health_status']} ({result['health_status_ar']})")

        print("\n📊 Component Scores:")
        print(f"  • NDVI Score (40%): {result['ndvi_score']}/100")
        print(f"  • Soil Moisture Score (25%): {result['soil_moisture_score']}/100")
        print(f"  • Weather Score (20%): {result['weather_score']}/100")
        print(f"  • Sensor Anomaly Score (15%): {result['sensor_anomaly_score']}/100")

        print(f"\n⚠️  Risk Factors ({len(result['risk_factors'])}):")
        for risk in result["risk_factors"]:
            print(f"  • [{risk['severity'].upper()}] {risk['type']}")
            print(f"    AR: {risk['description_ar']}")
            print(f"    EN: {risk['description_en']}")
            print(f"    Impact: {risk['impact_score']}/100")

        print("\n💡 Recommendations (Arabic):")
        for i, rec in enumerate(result["recommendations_ar"], 1):
            print(f"  {i}. {rec}")

        print("\n💡 Recommendations (English):")
        for i, rec in enumerate(result["recommendations_en"], 1):
            print(f"  {i}. {rec}")

        print(f"\n📅 Analysis Timestamp: {result['analysis_timestamp']}")

        print("\n✅ Test completed successfully!")

    except requests.exceptions.RequestException as e:
        print(f"\n❌ Error: {e}")
        if hasattr(e.response, "text"):
            print(f"Response: {e.response.text}")


# Additional test cases
test_cases = {
    "healthy_field": {
        "field_id": "field-healthy-001",
        "crop_type": "tomato",
        "sensor_data": {"soil_moisture": 30.0, "temperature": 24.0, "humidity": 70.0},
        "ndvi_data": {"ndvi_value": 0.68, "image_date": "2024-01-20", "cloud_coverage": 5.0},
        "weather_data": {"precipitation": 5.0, "wind_speed": 12.0, "forecast_days": 7},
    },
    "drought_stress": {
        "field_id": "field-drought-002",
        "crop_type": "corn",
        "sensor_data": {
            "soil_moisture": 15.0,  # Low moisture
            "temperature": 35.0,  # High temperature
            "humidity": 30.0,  # Low humidity
        },
        "ndvi_data": {
            "ndvi_value": 0.25,  # Low NDVI
            "image_date": "2024-01-20",
            "cloud_coverage": 10.0,
        },
        "weather_data": {
            "precipitation": 0.0,  # No rain
            "wind_speed": 25.0,
            "forecast_days": 7,
        },
    },
    "waterlogged_field": {
        "field_id": "field-wet-003",
        "crop_type": "wheat",
        "sensor_data": {
            "soil_moisture": 75.0,  # Very high moisture
            "temperature": 18.0,
            "humidity": 85.0,  # High humidity
        },
        "ndvi_data": {
            "ndvi_value": 0.35,  # Low NDVI
            "image_date": "2024-01-20",
            "cloud_coverage": 40.0,  # High cloud coverage
        },
        "weather_data": {
            "precipitation": 55.0,  # Heavy rain
            "wind_speed": 35.0,  # Strong winds
            "forecast_days": 7,
        },
    },
}


def run_all_test_cases():
    """Run all test cases"""
    print("\n" + "=" * 80)
    print("Running All Test Cases - تشغيل جميع حالات الاختبار")
    print("=" * 80)

    for test_name, test_data in test_cases.items():
        print(f"\n\n🧪 Test Case: {test_name}")
        print("-" * 80)

        try:
            response = requests.post(API_URL, json=test_data)
            response.raise_for_status()
            result = response.json()

            print(f"✅ Health Score: {result['overall_health_score']}/100")
            print(f"   Status: {result['health_status_ar']}")
            print(f"   Risks: {len(result['risk_factors'])}")
            print(f"   Recommendations: {len(result['recommendations_ar'])}")

        except Exception as e:
            print(f"❌ Failed: {e}")


if __name__ == "__main__":
    # Run the basic test
    test_field_health_api()

    # Optionally run all test cases (uncomment to enable)
    # run_all_test_cases()
