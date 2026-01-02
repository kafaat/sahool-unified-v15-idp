#!/bin/bash
# Field Health API - curl Example
# مثال استخدام واجهة صحة الحقل باستخدام curl

# API endpoint
API_URL="http://localhost:8080/api/v1/field-health"

echo "========================================"
echo "Field Health API Test - اختبار واجهة صحة الحقل"
echo "========================================"
echo ""

# Test Case 1: Healthy Field (حقل صحي)
echo "📊 Test Case 1: Healthy Field"
echo "----------------------------------------"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field-001",
    "crop_type": "wheat",
    "sensor_data": {
      "soil_moisture": 30.0,
      "temperature": 22.0,
      "humidity": 65.0
    },
    "ndvi_data": {
      "ndvi_value": 0.65,
      "image_date": "2024-01-20",
      "cloud_coverage": 10.0
    },
    "weather_data": {
      "precipitation": 8.0,
      "wind_speed": 15.0,
      "forecast_days": 7
    }
  }' | python3 -m json.tool

echo ""
echo ""

# Test Case 2: Drought Stress (إجهاد الجفاف)
echo "🌵 Test Case 2: Drought Stress"
echo "----------------------------------------"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field-002-drought",
    "crop_type": "corn",
    "sensor_data": {
      "soil_moisture": 12.0,
      "temperature": 38.0,
      "humidity": 25.0
    },
    "ndvi_data": {
      "ndvi_value": 0.22,
      "image_date": "2024-01-20",
      "cloud_coverage": 5.0
    },
    "weather_data": {
      "precipitation": 0.0,
      "wind_speed": 28.0,
      "forecast_days": 7
    }
  }' | python3 -m json.tool

echo ""
echo ""

# Test Case 3: Waterlogged Field (حقل مغمور)
echo "💧 Test Case 3: Waterlogged Field"
echo "----------------------------------------"
curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field-003-wet",
    "crop_type": "rice",
    "sensor_data": {
      "soil_moisture": 78.0,
      "temperature": 19.0,
      "humidity": 88.0
    },
    "ndvi_data": {
      "ndvi_value": 0.48,
      "image_date": "2024-01-20",
      "cloud_coverage": 45.0
    },
    "weather_data": {
      "precipitation": 65.0,
      "wind_speed": 42.0,
      "forecast_days": 7
    }
  }' | python3 -m json.tool

echo ""
echo "✅ Tests completed!"
