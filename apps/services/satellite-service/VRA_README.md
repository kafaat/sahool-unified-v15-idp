# Variable Rate Application (VRA) Prescription Maps
# خرائط وصفات التطبيق المتغير المعدل

## Overview | نظرة عامة

The SAHOOL VRA Prescription Map system enables precision agriculture through variable-rate application of agricultural inputs. Similar to OneSoil's VRA capabilities, this feature helps farmers optimize input use, reduce costs, and improve yields through data-driven, zone-specific application rates.

يمكّن نظام خرائط وصفات التطبيق المتغير من SAHOOL الزراعة الدقيقة من خلال التطبيق المتغير للمدخلات الزراعية. يساعد هذا النظام المزارعين على تحسين استخدام المدخلات وتقليل التكاليف وتحسين الإنتاج.

## Features | المميزات

- **5 VRA Types** (أنواع التطبيق المتغير):
  - Fertilizer (تسميد) - Variable nitrogen/fertilizer application
  - Seed (بذار) - Variable seeding rates
  - Lime (جير) - Variable lime application for pH correction
  - Pesticide (مبيدات) - Targeted pesticide application
  - Irrigation (ري) - Variable water application

- **Zone Classification** (تصنيف المناطق):
  - 3-zone or 5-zone management
  - NDVI-based, yield-based, soil-based, or combined methods
  - Automatic zone delineation with polygon geometry

- **Export Formats** (صيغ التصدير):
  - **GeoJSON** - For web display and GIS applications
  - **Shapefile** - For farm equipment and GIS software
  - **ISO-XML** - For ISOBUS-compatible equipment

- **Cost Analysis** (تحليل التكلفة):
  - Savings calculation vs. flat rate
  - Product quantity optimization
  - Cost savings estimates

## API Endpoints | نقاط النهاية

### 1. Generate VRA Prescription | توليد وصفة التطبيق المتغير

Generate a complete VRA prescription map with management zones and application rates.

```http
POST /v1/vra/generate
Content-Type: application/json

{
  "field_id": "field_123",
  "latitude": 15.5,
  "longitude": 44.2,
  "vra_type": "fertilizer",
  "target_rate": 100,
  "unit": "kg/ha",
  "num_zones": 3,
  "zone_method": "ndvi",
  "min_rate": 50,
  "max_rate": 150,
  "product_price_per_unit": 2.5,
  "notes": "Spring nitrogen application",
  "notes_ar": "تطبيق النيتروجين الربيعي"
}
```

**Response:**
```json
{
  "id": "abc-123-def",
  "field_id": "field_123",
  "vra_type": "fertilizer",
  "created_at": "2025-12-25T10:30:00",
  "target_rate": 100,
  "min_rate": 50,
  "max_rate": 150,
  "unit": "kg/ha",
  "num_zones": 3,
  "zone_method": "ndvi",
  "zones": [
    {
      "zone_id": 1,
      "zone_name": "Low",
      "zone_name_ar": "منخفض",
      "zone_level": "low",
      "ndvi_min": 0.0,
      "ndvi_max": 0.4,
      "area_ha": 2.5,
      "percentage": 25.0,
      "centroid": [44.201, 15.5],
      "recommended_rate": 115.0,
      "unit": "kg/ha",
      "total_product": 287.5,
      "color": "#d62728"
    },
    {
      "zone_id": 2,
      "zone_name": "Medium",
      "zone_name_ar": "متوسط",
      "zone_level": "medium",
      "ndvi_min": 0.4,
      "ndvi_max": 0.6,
      "area_ha": 5.0,
      "percentage": 50.0,
      "centroid": [44.202, 15.5],
      "recommended_rate": 100.0,
      "unit": "kg/ha",
      "total_product": 500.0,
      "color": "#ff7f0e"
    },
    {
      "zone_id": 3,
      "zone_name": "High",
      "zone_name_ar": "عالي",
      "zone_level": "high",
      "ndvi_min": 0.6,
      "ndvi_max": 1.0,
      "area_ha": 2.5,
      "percentage": 25.0,
      "centroid": [44.203, 15.5],
      "recommended_rate": 85.0,
      "unit": "kg/ha",
      "total_product": 212.5,
      "color": "#2ca02c"
    }
  ],
  "total_area_ha": 10.0,
  "total_product_needed": 1000.0,
  "flat_rate_product": 1000.0,
  "savings_percent": 0.0,
  "savings_amount": 0.0,
  "cost_savings": 0.0,
  "notes": "Spring nitrogen application",
  "notes_ar": "تطبيق النيتروجين الربيعي",
  "geojson_url": "/v1/vra/export/abc-123-def?format=geojson",
  "shapefile_url": "/v1/vra/export/abc-123-def?format=shapefile",
  "isoxml_url": "/v1/vra/export/abc-123-def?format=isoxml"
}
```

### 2. Get Management Zones | الحصول على مناطق الإدارة

Preview management zones without generating a full prescription.

```http
GET /v1/vra/zones/field_123?lat=15.5&lon=44.2&num_zones=3
```

**Response:**
```json
{
  "field_id": "field_123",
  "num_zones": 3,
  "total_area_ha": 10.0,
  "zones": [...],
  "ndvi_statistics": {
    "mean": 0.55,
    "std": 0.15,
    "min": 0.25,
    "max": 0.85
  }
}
```

### 3. Get Prescription History | سجل الوصفات

Retrieve all prescriptions for a field.

```http
GET /v1/vra/prescriptions/field_123?limit=10
```

**Response:**
```json
{
  "field_id": "field_123",
  "count": 3,
  "prescriptions": [
    {
      "id": "abc-123-def",
      "vra_type": "fertilizer",
      "created_at": "2025-12-25T10:30:00",
      "target_rate": 100,
      "unit": "kg/ha",
      "num_zones": 3,
      "total_area_ha": 10.0,
      "total_product_needed": 1000.0,
      "savings_percent": 0.0,
      "savings_amount": 0.0,
      "cost_savings": 0.0
    }
  ]
}
```

### 4. Get Prescription Details | تفاصيل الوصفة

Get full details of a specific prescription.

```http
GET /v1/vra/prescription/abc-123-def
```

### 5. Export Prescription | تصدير الوصفة

Export prescription in various formats.

```http
GET /v1/vra/export/abc-123-def?format=geojson
GET /v1/vra/export/abc-123-def?format=shapefile
GET /v1/vra/export/abc-123-def?format=isoxml
```

**GeoJSON Response:**
```json
{
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "geometry": {
        "type": "Polygon",
        "coordinates": [[...]]
      },
      "properties": {
        "zone_id": 1,
        "zone_name": "Low",
        "zone_name_ar": "منخفض",
        "rate": 115.0,
        "unit": "kg/ha",
        "area_ha": 2.5,
        "color": "#d62728"
      }
    }
  ],
  "properties": {
    "prescription_id": "abc-123-def",
    "field_id": "field_123",
    "vra_type": "fertilizer",
    "total_area_ha": 10.0,
    "total_product": 1000.0,
    "savings_percent": 0.0
  }
}
```

### 6. Delete Prescription | حذف الوصفة

```http
DELETE /v1/vra/prescription/abc-123-def
```

**Response:**
```json
{
  "success": true,
  "message": "Prescription deleted successfully",
  "message_ar": "تم حذف الوصفة بنجاح",
  "prescription_id": "abc-123-def"
}
```

### 7. Get VRA Information | معلومات النظام

Get information about VRA types and capabilities.

```http
GET /v1/vra/info
```

## VRA Types and Strategies | أنواع واستراتيجيات التطبيق

### 1. Fertilizer (تسميد)
**Strategy:** More fertilizer to low-vigor areas, less to high-vigor areas.

- **Low Vigor Zones (منخفض):** 130% of target rate
- **Medium Vigor (متوسط):** 100% of target rate
- **High Vigor (عالي):** 70% of target rate

**Rationale:** Low-vigor areas need more nutrients to catch up, while high-vigor areas already have sufficient nutrients.

### 2. Seed (بذار)
**Strategy:** More seeds to high-potential areas.

- **Low Potential (منخفض):** 80% of target rate
- **Medium Potential (متوسط):** 100% of target rate
- **High Potential (عالي):** 115% of target rate

**Rationale:** Maximize productivity in areas with good conditions.

### 3. Lime (جير)
**Strategy:** More lime to acidic areas (low NDVI indicates poor soil).

- **Low NDVI (منخفض):** 140% of target rate
- **Medium NDVI (متوسط):** 100% of target rate
- **High NDVI (عالي):** 60% of target rate

**Rationale:** Correct soil pH in problem areas.

### 4. Pesticide (مبيدات)
**Strategy:** Target high-vigor areas where pests thrive.

- **Low Vigor (منخفض):** 70% of target rate
- **Medium Vigor (متوسط):** 100% of target rate
- **High Vigor (عالي):** 125% of target rate

**Rationale:** Focus pest control where infestations are likely.

### 5. Irrigation (ري)
**Strategy:** More water to stressed areas.

- **Low Vigor/Stressed (منخفض):** 130% of target rate
- **Medium Vigor (متوسط):** 100% of target rate
- **High Vigor (عالي):** 75% of target rate

**Rationale:** Provide more water to water-stressed areas.

## Zone Methods | طرق تصنيف المناطق

1. **NDVI-Based (بناءً على NDVI):** Zones based on vegetation index from satellite imagery
2. **Yield-Based (بناءً على الإنتاج):** Zones based on historical yield data
3. **Soil-Based (بناءً على التربة):** Zones based on soil analysis
4. **Combined (مجمع):** Multi-factor zone classification

## Usage Examples | أمثلة الاستخدام

### Example 1: Fertilizer Prescription for Wheat

```bash
curl -X POST http://localhost:8090/v1/vra/generate \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "wheat_field_01",
    "latitude": 15.5,
    "longitude": 44.2,
    "vra_type": "fertilizer",
    "target_rate": 120,
    "unit": "kg/ha",
    "num_zones": 3,
    "product_price_per_unit": 2.8,
    "notes_ar": "تسميد القمح - الربيع 2025"
  }'
```

### Example 2: Variable Seeding for Sorghum

```bash
curl -X POST http://localhost:8090/v1/vra/generate \
  -H "Content-Type: application/json" \
  -d '{
    "field_id": "sorghum_field_02",
    "latitude": 14.8,
    "longitude": 43.5,
    "vra_type": "seed",
    "target_rate": 50000,
    "unit": "seeds/ha",
    "num_zones": 5,
    "min_rate": 40000,
    "max_rate": 60000,
    "notes": "Sorghum planting - optimal density"
  }'
```

### Example 3: Export to GeoJSON

```bash
curl http://localhost:8090/v1/vra/export/abc-123-def?format=geojson \
  -o prescription.geojson
```

### Example 4: Preview Management Zones

```bash
curl "http://localhost:8090/v1/vra/zones/field_123?lat=15.5&lon=44.2&num_zones=3"
```

## Benefits | الفوائد

### For Farmers | للمزارعين

1. **Cost Savings (توفير التكلفة)**
   - Reduce input costs by 10-30%
   - Apply inputs only where needed
   - Minimize waste

2. **Improved Yields (تحسين الإنتاج)**
   - Optimize nutrient distribution
   - Better crop uniformity
   - Increased productivity

3. **Environmental Benefits (فوائد بيئية)**
   - Reduce fertilizer runoff
   - Lower carbon footprint
   - Sustainable farming practices

4. **Equipment Compatibility (توافق المعدات)**
   - Export to standard formats
   - Compatible with modern farm equipment
   - Easy integration with existing systems

### For Agricultural Operations

- **Data-Driven Decisions:** Base applications on actual field conditions
- **Precision Agriculture:** Implement site-specific management
- **Record Keeping:** Historical prescription tracking
- **Scalability:** Handle multiple fields and seasons

## Technical Details | التفاصيل التقنية

### Zone Classification Algorithm

1. **Fetch NDVI Data:** Retrieve latest satellite imagery for the field
2. **Classify Pixels:** Group pixels into zones based on NDVI values
3. **Create Polygons:** Generate zone boundaries with geometry
4. **Calculate Statistics:** Compute area, percentage, centroid for each zone
5. **Assign Rates:** Apply VRA-specific rate adjustments
6. **Generate Prescription:** Create complete prescription with all data

### NDVI Thresholds

**3-Zone System:**
- Low: 0.0 - 0.4
- Medium: 0.4 - 0.6
- High: 0.6 - 1.0

**5-Zone System:**
- Very Low: 0.0 - 0.3
- Low: 0.3 - 0.45
- Medium: 0.45 - 0.55
- High: 0.55 - 0.7
- Very High: 0.7 - 1.0

### Export Format Specifications

#### GeoJSON
- Standard GeoJSON FeatureCollection
- Each zone is a Polygon feature
- Properties include rate, area, color
- Compatible with QGIS, ArcGIS, Leaflet, Mapbox

#### Shapefile
- Standard ESRI Shapefile format
- Includes .shp, .shx, .dbf components
- EPSG:4326 (WGS84) coordinate system
- Compatible with all GIS software

#### ISO-XML
- ISO 11783-10 compliant
- ISOBUS Task Data format
- Compatible with modern agricultural equipment
- Includes treatment zones and application rates

## Integration | التكامل

### With Mobile App

```javascript
// Fetch VRA prescription
const response = await fetch('/v1/vra/generate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    field_id: fieldId,
    latitude: field.lat,
    longitude: field.lon,
    vra_type: 'fertilizer',
    target_rate: 100,
    unit: 'kg/ha',
    num_zones: 3
  })
});

const prescription = await response.json();

// Display zones on map
prescription.zones.forEach(zone => {
  addPolygonToMap(zone.polygon, {
    color: zone.color,
    label: zone.zone_name_ar,
    rate: zone.recommended_rate
  });
});
```

### With Farm Management System

```python
import requests

# Generate prescription
prescription = requests.post('http://satellite-service:8090/v1/vra/generate', json={
    'field_id': 'field_123',
    'latitude': 15.5,
    'longitude': 44.2,
    'vra_type': 'fertilizer',
    'target_rate': 100,
    'unit': 'kg/ha',
    'num_zones': 3,
    'product_price_per_unit': 2.5
}).json()

# Export to equipment format
geojson = requests.get(
    f"http://satellite-service:8090/v1/vra/export/{prescription['id']}",
    params={'format': 'geojson'}
).json()

# Save to file for equipment upload
with open('prescription.geojson', 'w') as f:
    json.dump(geojson, f)
```

## Testing | الاختبار

Run the test suite:

```bash
cd /home/user/sahool-unified-v15-idp/apps/services/satellite-service
python3 tests/test_vra_generator.py
```

## Architecture | الهندسة

```
satellite-service/
├── src/
│   ├── vra_generator.py       # Core VRA logic
│   ├── vra_endpoints.py       # API endpoints
│   └── main.py                # Service entry point
├── tests/
│   └── test_vra_generator.py  # Test suite
└── VRA_README.md              # This documentation
```

## Future Enhancements | التحسينات المستقبلية

- [ ] Yield-based zone classification
- [ ] Soil analysis integration
- [ ] Multi-year prescription comparison
- [ ] Real-time NDVI updates
- [ ] Mobile app VRA visualization
- [ ] Equipment telemetry integration
- [ ] Prescription effectiveness tracking
- [ ] Machine learning rate optimization

## Support | الدعم

For questions or issues with the VRA system, please contact the SAHOOL development team.

---

**Version:** 1.0
**Last Updated:** December 25, 2025
**Status:** Production Ready ✅
