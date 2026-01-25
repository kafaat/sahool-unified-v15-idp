#!/bin/bash
# SAHOOL Cloud Masking System - API Examples
# نظام تحديد الغطاء السحابي - أمثلة استخدام

# Service URL
BASE_URL="http://localhost:8090"

echo "======================================================================="
echo "🛰️ SAHOOL Cloud Masking System - API Examples"
echo "نظام تحديد الغطاء السحابي - أمثلة استخدام"
echo "======================================================================="

# Example coordinates (Sana'a region, Yemen)
FIELD_ID="field_sana_001"
LAT=15.5527
LON=44.2075

echo ""
echo "-----------------------------------------------------------------------"
echo "Example 1: Analyze Cloud Cover for Today"
echo "مثال 1: تحليل الغطاء السحابي لليوم"
echo "-----------------------------------------------------------------------"
curl -X GET "${BASE_URL}/v1/cloud-cover/${FIELD_ID}?lat=${LAT}&lon=${LON}" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "-----------------------------------------------------------------------"
echo "Example 2: Analyze Cloud Cover for Specific Date"
echo "مثال 2: تحليل الغطاء السحابي لتاريخ محدد"
echo "-----------------------------------------------------------------------"
curl -X GET "${BASE_URL}/v1/cloud-cover/${FIELD_ID}?lat=${LAT}&lon=${LON}&date=2024-03-15" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "-----------------------------------------------------------------------"
echo "Example 3: Find Clear Observations in Date Range"
echo "مثال 3: البحث عن الأرصاد الصافية في فترة زمنية"
echo "-----------------------------------------------------------------------"
curl -X GET "${BASE_URL}/v1/clear-observations/${FIELD_ID}?lat=${LAT}&lon=${LON}&start_date=2024-01-01&end_date=2024-03-31&max_cloud=15" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "-----------------------------------------------------------------------"
echo "Example 4: Find Best Observation Near Target Date"
echo "مثال 4: البحث عن أفضل رصد قريب من تاريخ محدد"
echo "-----------------------------------------------------------------------"
curl -X GET "${BASE_URL}/v1/best-observation/${FIELD_ID}?lat=${LAT}&lon=${LON}&target_date=2024-02-15&tolerance_days=10" \
  -H "Content-Type: application/json" | jq '.'

echo ""
echo "-----------------------------------------------------------------------"
echo "Example 5: Interpolate Cloudy Observations (Linear)"
echo "مثال 5: استكمال الأرصاد الملبدة بالغيوم (خطي)"
echo "-----------------------------------------------------------------------"
curl -X POST "${BASE_URL}/v1/interpolate-cloudy?field_id=${FIELD_ID}&method=linear" \
  -H "Content-Type: application/json" \
  -d '{
    "ndvi_series": [
      {"date": "2024-01-01", "ndvi": 0.65, "cloudy": false},
      {"date": "2024-01-10", "ndvi": 0.45, "cloudy": true},
      {"date": "2024-01-20", "ndvi": 0.75, "cloudy": false},
      {"date": "2024-01-30", "ndvi": 0.50, "cloudy": true},
      {"date": "2024-02-10", "ndvi": 0.70, "cloudy": false}
    ]
  }' | jq '.'

echo ""
echo "-----------------------------------------------------------------------"
echo "Example 6: Interpolate Cloudy Observations (Spline)"
echo "مثال 6: استكمال الأرصاد الملبدة بالغيوم (منحنى)"
echo "-----------------------------------------------------------------------"
curl -X POST "${BASE_URL}/v1/interpolate-cloudy?field_id=${FIELD_ID}&method=spline" \
  -H "Content-Type: application/json" \
  -d '{
    "ndvi_series": [
      {"date": "2024-01-01", "ndvi": 0.60, "cloudy": false},
      {"date": "2024-01-06", "ndvi": 0.45, "cloudy": true},
      {"date": "2024-01-11", "ndvi": 0.50, "cloudy": true},
      {"date": "2024-01-16", "ndvi": 0.70, "cloudy": false},
      {"date": "2024-01-21", "ndvi": 0.55, "cloudy": true},
      {"date": "2024-01-26", "ndvi": 0.75, "cloudy": false}
    ]
  }' | jq '.'

echo ""
echo "-----------------------------------------------------------------------"
echo "Example 7: Interpolate with Previous Value (Forward Fill)"
echo "مثال 7: استكمال بالقيمة السابقة"
echo "-----------------------------------------------------------------------"
curl -X POST "${BASE_URL}/v1/interpolate-cloudy?field_id=${FIELD_ID}&method=previous" \
  -H "Content-Type: application/json" \
  -d '{
    "ndvi_series": [
      {"date": "2024-01-01", "ndvi": 0.65, "cloudy": false},
      {"date": "2024-01-10", "ndvi": 0.45, "cloudy": true},
      {"date": "2024-01-20", "ndvi": 0.75, "cloudy": false}
    ]
  }' | jq '.'

echo ""
echo "-----------------------------------------------------------------------"
echo "Example 8: Find Very Clear Observations (< 5% cloud)"
echo "مثال 8: البحث عن أرصاد صافية جداً (< 5% غيوم)"
echo "-----------------------------------------------------------------------"
curl -X GET "${BASE_URL}/v1/clear-observations/${FIELD_ID}?lat=${LAT}&lon=${LON}&start_date=2024-01-01&end_date=2024-06-30&max_cloud=5" \
  -H "Content-Type: application/json" | jq '.observations | length'

echo ""
echo "======================================================================="
echo "✅ All examples completed!"
echo "جميع الأمثلة اكتملت!"
echo "======================================================================="
