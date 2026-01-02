# خدمة التحقق من حدود الحقول - Field Boundary Validation Service

## نظرة عامة - Overview

خدمة شاملة للتحقق من صحة حدود الحقول الجغرافية في منصة SAHOOL، مع دعم خاص للقيود الجغرافية لليمن.

Comprehensive field boundary validation service for the SAHOOL platform, with special support for Yemen geographic constraints.

## الميزات الرئيسية - Key Features

### 1. التحقق من الهندسة - Geometry Validation

- **التقاطع الذاتي** - Self-intersection detection
- **اتجاه النقاط** - Winding order validation (CCW for exterior, CW for holes)
- **النقاط المكررة** - Duplicate point detection
- **عدد النقاط الكافي** - Sufficient point count validation
- **صحة المضلع** - Polygon validity checking

### 2. قيود اليمن الجغرافية - Yemen Geographic Constraints

- **حدود خطوط الطول**: 42.0° - 54.0° شرقاً
- **Longitude bounds**: 42.0° - 54.0° E

- **حدود خطوط العرض**: 12.0° - 19.0° شمالاً
- **Latitude bounds**: 12.0° - 19.0° N

- **التحقق من المحافظات** - Governorate validation (22 governorate)
- **استبعاد المناطق البحرية** - Maritime area exclusion

### 3. حدود المساحة - Area Constraints

- **الحد الأدنى**: 0.1 هكتار (1000 م²)
- **Minimum area**: 0.1 hectare (1000 m²)

- **الحد الأقصى**: 1000 هكتار
- **Maximum area**: 1000 hectares

### 4. كشف التداخل - Overlap Detection

- فحص التداخل مع الحقول الموجودة
- Check overlap with existing fields

- حساب مساحة ونسبة التداخل
- Calculate overlap area and percentage

- دعم استبعاد حقول نفس المستخدم
- Support for same-user field exclusion

### 5. حسابات هندسية - Geometric Calculations

- **المساحة بالهكتار** - Area in hectares (geodesic calculation)
- **المحيط بالأمتار** - Perimeter in meters
- **نقطة المركز** - Centroid coordinates
- **المربع المحيط** - Bounding box

### 6. إصلاح تلقائي - Automatic Repair

- إصلاح المضلعات غير الصالحة
- Fix invalid polygons

- إزالة النقاط المكررة
- Remove duplicate points

- تصحيح الاتجاه
- Correct winding order

- تبسيط الهندسة
- Geometry simplification

## التثبيت - Installation

```bash
# تثبيت المتطلبات - Install requirements
pip install shapely>=2.0.0 pydantic>=2.0.0
```

## الاستخدام السريع - Quick Start

### 1. التحقق الأساسي - Basic Validation

```python
from services.boundary_validator import BoundaryValidator

# إنشاء المحقق - Create validator
validator = BoundaryValidator()

# حدود الحقل (GeoJSON) - Field boundary (GeoJSON)
field_boundary = {
    "type": "Feature",
    "properties": {
        "name": "حقل القمح - Wheat Field"
    },
    "geometry": {
        "type": "Polygon",
        "coordinates": [
            [
                [44.2, 15.35],
                [44.21, 15.35],
                [44.21, 15.36],
                [44.2, 15.36],
                [44.2, 15.35]
            ]
        ]
    }
}

# التحقق - Validate
result = validator.validate_geometry(field_boundary)

# النتائج - Results
print(f"صالح: {result.is_valid}")
print(f"المساحة: {result.area_hectares} هكتار")
print(f"المحيط: {result.perimeter_meters} متر")
print(f"المركز: {result.centroid}")

# عرض المشاكل - Display issues
for issue in result.issues:
    print(f"[{issue.severity}] {issue.message_ar}")
```

### 2. التحقق مع حدود اليمن التفصيلية - Validation with Detailed Yemen Boundaries

```python
from pathlib import Path

# تحميل حدود اليمن - Load Yemen boundaries
yemen_boundaries_path = Path("data/yemen_boundaries.geojson")
validator = BoundaryValidator(yemen_boundaries_path=str(yemen_boundaries_path))

# التحقق - Validate
result = validator.validate_geometry(field_boundary)

# التحقق من المحافظة - Check governorate
from shapely.geometry import shape
polygon = shape(field_boundary['geometry'])
is_in_sanaa = validator.validate_governorate(polygon, "صنعاء")
```

### 3. كشف التداخل - Overlap Detection

```python
# حدود حقل جديد - New field boundary
new_field = {
    "type": "Polygon",
    "coordinates": [[...]]
}

# الحقول الموجودة - Existing fields
existing_fields = [
    {
        "field_id": "field_001",
        "name": "حقل القمح",
        "user_id": "user_123",
        "geometry": {...}
    },
    # ... المزيد من الحقول
]

# فحص التداخل - Check overlap
overlap_result = validator.check_overlap_with_existing(
    new_boundary=new_field,
    existing_fields=existing_fields,
    user_id="user_123",  # اختياري - optional
    tolerance_percentage=5.0  # التفاوت المسموح - allowed tolerance
)

# النتائج - Results
if overlap_result.has_overlap:
    print(f"عدد الحقول المتداخلة: {len(overlap_result.overlapping_fields)}")
    print(f"مساحة التداخل: {overlap_result.total_overlap_area_hectares} هكتار")
    print(f"أقصى نسبة تداخل: {overlap_result.max_overlap_percentage}%")

    for field in overlap_result.overlapping_fields:
        print(f"  - {field['field_id']}: {field['overlap_percentage']:.2f}%")
```

### 4. حساب المساحة والمحيط - Area and Perimeter Calculation

```python
from shapely.geometry import shape

# تحويل GeoJSON إلى Shapely polygon
polygon = shape(field_boundary['geometry'])

# الحسابات - Calculations
area_ha = validator.calculate_area_hectares(polygon)
perimeter_m = validator.calculate_perimeter_meters(polygon)
centroid = validator.get_centroid(polygon)
bbox = validator.get_bounding_box(polygon)

print(f"المساحة: {area_ha} هكتار")
print(f"المحيط: {perimeter_m} متر")
print(f"المركز: {centroid}")
print(f"المربع المحيط: {bbox}")
```

### 5. إصلاح المشاكل - Fix Issues

```python
from shapely.geometry import shape

# حقل مع مشاكل - Field with issues
problematic_field = {...}
polygon = shape(problematic_field['geometry'])

# إصلاح - Fix
fixed_polygon = validator.fix_common_issues(polygon)

# تبسيط - Simplify
simplified_polygon = validator.simplify_geometry(
    polygon,
    tolerance=0.00001  # ≈ 1 meter
)

# التحقق من الصحة - Verify validity
print(f"صالح بعد الإصلاح: {fixed_polygon.is_valid}")
```

## نماذج البيانات - Data Models

### BoundaryValidationResult

```python
{
    "is_valid": bool,
    "issues": [ValidationIssue],
    "area_hectares": float,
    "perimeter_meters": float,
    "centroid": {"longitude": float, "latitude": float},
    "bounding_box": {
        "min_longitude": float,
        "min_latitude": float,
        "max_longitude": float,
        "max_latitude": float
    },
    "simplified_geometry": GeoJSON,  # اختياري - optional
    "fixed_geometry": GeoJSON,       # اختياري - optional
    "validation_timestamp": datetime,
    "validator_version": str
}
```

### ValidationIssue

```python
{
    "issue_type": str,  # GeometryIssueType or BoundarySeverity
    "severity": str,    # info, warning, error, critical
    "message_ar": str,
    "message_en": str,
    "location": {"longitude": float, "latitude": float},  # اختياري
    "fixable": bool,
    "details": dict
}
```

### OverlapResult

```python
{
    "has_overlap": bool,
    "overlapping_fields": [
        {
            "field_id": str,
            "overlap_area_hectares": float,
            "overlap_percentage": float,
            "field_name": str,
            "intersection_geometry": GeoJSON
        }
    ],
    "total_overlap_area_hectares": float,
    "max_overlap_percentage": float
}
```

## أنواع المشاكل - Issue Types

### GeometryIssueType

- `self_intersection` - تقاطع ذاتي
- `invalid_winding` - اتجاه خاطئ
- `duplicate_points` - نقاط مكررة
- `insufficient_points` - نقاط غير كافية
- `invalid_polygon` - مضلع غير صالح
- `topology_error` - خطأ في الطوبولوجيا

### BoundarySeverity

- `out_of_yemen` - خارج اليمن
- `partially_out` - جزئياً خارج الحدود
- `area_too_small` - مساحة صغيرة جداً
- `area_too_large` - مساحة كبيرة جداً
- `maritime_area` - منطقة بحرية

### ValidationSeverity

- `info` - معلومات (لا تؤثر على الصلاحية)
- `warning` - تحذير (ينصح بالإصلاح)
- `error` - خطأ (يجب الإصلاح)
- `critical` - حرج (غير صالح)

## محافظات اليمن - Yemen Governorates

المحافظات المدعومة (22 محافظة):

```python
YEMEN_GOVERNORATES = [
    "صنعاء", "عدن", "تعز", "الحديدة", "إب", "ذمار", "حضرموت",
    "المحويت", "حجة", "صعدة", "عمران", "البيضاء", "أبين", "شبوة",
    "المهرة", "لحج", "الضالع", "مأرب", "الجوف", "ريمة", "سقطرى", "أمانة العاصمة"
]
```

## أمثلة متقدمة - Advanced Examples

### تكامل مع API

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
validator = BoundaryValidator(yemen_boundaries_path="data/yemen_boundaries.geojson")

class FieldBoundary(BaseModel):
    field_id: str
    geometry: dict
    user_id: str

@app.post("/validate-boundary")
async def validate_boundary(field: FieldBoundary):
    """التحقق من حدود حقل - Validate field boundary"""

    # التحقق من الهندسة - Validate geometry
    result = validator.validate_geometry(field.geometry)

    if not result.is_valid:
        raise HTTPException(
            status_code=400,
            detail={
                "message_ar": "حدود الحقل غير صالحة",
                "message_en": "Invalid field boundary",
                "issues": [
                    {
                        "severity": issue.severity,
                        "message_ar": issue.message_ar,
                        "message_en": issue.message_en
                    }
                    for issue in result.issues
                ]
            }
        )

    # فحص التداخل - Check overlap
    # ... (fetch existing fields from database)

    return {
        "valid": True,
        "area_hectares": result.area_hectares,
        "perimeter_meters": result.perimeter_meters,
        "centroid": result.centroid
    }
```

### دفعة التحقق - Batch Validation

```python
def validate_multiple_fields(fields: list) -> dict:
    """التحقق من عدة حقول دفعة واحدة"""

    results = {
        "total": len(fields),
        "valid": 0,
        "invalid": 0,
        "warnings": 0,
        "details": []
    }

    for field in fields:
        result = validator.validate_geometry(field['geometry'])

        field_result = {
            "field_id": field['field_id'],
            "is_valid": result.is_valid,
            "area_hectares": result.area_hectares,
            "issues": [
                {
                    "severity": issue.severity,
                    "message": issue.message_ar
                }
                for issue in result.issues
            ]
        }

        if result.is_valid:
            results["valid"] += 1
        else:
            results["invalid"] += 1

        if any(issue.severity == "warning" for issue in result.issues):
            results["warnings"] += 1

        results["details"].append(field_result)

    return results
```

## الاختبار - Testing

```bash
# تشغيل الاختبارات - Run tests
cd apps/kernel/field_ops
python test_boundary_validator.py
```

## الأداء - Performance

- **التحقق الأساسي**: < 10ms لكل حقل
- **Basic validation**: < 10ms per field

- **كشف التداخل**: < 50ms لـ 100 حقل
- **Overlap detection**: < 50ms for 100 fields

- **التحقق مع حدود اليمن**: < 20ms لكل حقل
- **Yemen bounds validation**: < 20ms per field

## الملاحظات - Notes

1. **دقة الإحداثيات**: 6 منازل عشرية (≈ 0.11 متر)
   - **Coordinate precision**: 6 decimal places (≈ 0.11 meters)

2. **نظام الإحداثيات**: WGS84 (EPSG:4326)
   - **Coordinate system**: WGS84 (EPSG:4326)

3. **حساب المساحة**: استخدام تقريب جيوديزي بناءً على خط العرض
   - **Area calculation**: Geodesic approximation based on latitude

4. **التبسيط**: التفاوت الافتراضي ≈ 1 متر
   - **Simplification**: Default tolerance ≈ 1 meter

## المراجع - References

- [Shapely Documentation](https://shapely.readthedocs.io/)
- [GeoJSON Specification](https://geojson.org/)
- [FAO Yemen Country Profile](http://www.fao.org/countryprofiles/index/en/?iso3=YEM)

## الدعم - Support

للمساعدة والأسئلة:
- البريد الإلكتروني: support@sahool.ye
- الوثائق: https://docs.sahool.ye

For help and questions:
- Email: support@sahool.ye
- Documentation: https://docs.sahool.ye

---

**المطور**: SAHOOL Platform
**Developer**: SAHOOL Platform

**الإصدار**: 1.0.0
**Version**: 1.0.0

**الترخيص**: Proprietary
**License**: Proprietary
