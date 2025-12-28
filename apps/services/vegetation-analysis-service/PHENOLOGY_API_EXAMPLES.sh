#!/bin/bash
# SAHOOL Phenology Detection API Examples
# مثال على استخدام واجهة برمجة التطبيقات لكشف مراحل النمو

BASE_URL="http://localhost:8090"

echo "🌱 SAHOOL Crop Phenology Detection API Examples"
echo "================================================"
echo ""

# Example 1: List supported crops
echo "1️⃣  List all supported crops:"
echo "   GET $BASE_URL/v1/phenology/crops"
echo ""
curl -X GET "$BASE_URL/v1/phenology/crops" | jq '.'
echo ""
echo "---"
echo ""

# Example 2: Detect current growth stage for wheat field
echo "2️⃣  Detect current growth stage (Wheat):"
echo "   GET $BASE_URL/v1/phenology/field_001?crop_type=wheat&lat=15.3694&lon=44.1910&planting_date=2024-11-01&days=60"
echo ""
curl -X GET "$BASE_URL/v1/phenology/field_001?crop_type=wheat&lat=15.3694&lon=44.1910&planting_date=2024-11-01&days=60" | jq '.'
echo ""
echo "---"
echo ""

# Example 3: Get phenology timeline for planning
echo "3️⃣  Get phenology timeline (Tomato):"
echo "   GET $BASE_URL/v1/phenology/field_002/timeline?crop_type=tomato&planting_date=2024-12-01"
echo ""
curl -X GET "$BASE_URL/v1/phenology/field_002/timeline?crop_type=tomato&planting_date=2024-12-01" | jq '.'
echo ""
echo "---"
echo ""

# Example 4: Get stage-specific recommendations
echo "4️⃣  Get recommendations for wheat flowering stage:"
echo "   GET $BASE_URL/v1/phenology/recommendations/wheat/flowering"
echo ""
curl -X GET "$BASE_URL/v1/phenology/recommendations/wheat/flowering" | jq '.'
echo ""
echo "---"
echo ""

# Example 5: Detect with ActionTemplate generation
echo "5️⃣  Detect phenology with ActionTemplate (Sorghum):"
echo "   POST $BASE_URL/v1/phenology/field_003/analyze-with-action"
echo ""
curl -X POST "$BASE_URL/v1/phenology/field_003/analyze-with-action" \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "field_003",
    "farmer_id": "farmer_123",
    "tenant_id": "tenant_abc",
    "crop_type": "sorghum",
    "latitude": 15.3694,
    "longitude": 44.1910,
    "planting_date": "2024-11-15",
    "days": 60,
    "publish_event": true
  }' | jq '.'
echo ""
echo "---"
echo ""

# Example 6: Multiple crop comparison
echo "6️⃣  Compare timelines for different crops:"
echo ""

for crop in wheat sorghum tomato coffee; do
  echo "  📊 $crop:"
  curl -s -X GET "$BASE_URL/v1/phenology/field_multi/timeline?crop_type=$crop&planting_date=2024-11-01" \
    | jq -r '"    Season length: \(.season_length_days) days | Harvest: \(.harvest_estimate)"'
done

echo ""
echo "---"
echo ""

# Example 7: Get recommendations for different stages
echo "7️⃣  Recommendations across growth stages (Wheat):"
echo ""

for stage in germination tillering flowering ripening; do
  echo "  🌾 $stage stage:"
  curl -s -X GET "$BASE_URL/v1/phenology/recommendations/wheat/$stage" \
    | jq -r '.recommendations_en[0]' | sed 's/^/    /'
done

echo ""
echo "================================================"
echo "✅ Examples complete!"
echo ""
echo "💡 Tip: Use jq for JSON formatting, or remove '| jq' to see raw JSON"
echo "📖 Full documentation: See PHENOLOGY_README.md"
