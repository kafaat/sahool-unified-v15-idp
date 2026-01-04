"""
مثال بسيط لاستخدام محقق حدود الحقول
Simple example of using the boundary validator

يمكن تشغيله مباشرة بعد تثبيت المتطلبات:
Can be run directly after installing requirements:

    pip install shapely>=2.0.0 pydantic>=2.0.0
    python example_boundary_validation.py
"""

import sys
import json
from pathlib import Path

# إضافة المسار للوحدات - Add path to modules
sys.path.insert(0, str(Path(__file__).parent))

try:
    from services.boundary_validator import (
        BoundaryValidator,
        YEMEN_BOUNDS,
        AREA_LIMITS,
    )

    print("=" * 80)
    print("مثال بسيط لخدمة التحقق من حدود الحقول")
    print("Simple Field Boundary Validation Example")
    print("=" * 80)

    # إنشاء المحقق - Create validator
    print("\n1. إنشاء المحقق - Creating validator...")
    validator = BoundaryValidator()
    print("   ✓ تم إنشاء المحقق بنجاح - Validator created successfully")

    # حقل صالح في صنعاء - Valid field in Sana'a
    print("\n2. التحقق من حقل صالح في صنعاء - Validating valid field in Sana'a...")
    valid_field = {
        "type": "Feature",
        "properties": {
            "name": "حقل القمح - Wheat Field",
            "crop": "wheat",
            "area_ha": 2.5,
        },
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [44.2, 15.35],
                    [44.22, 15.35],
                    [44.22, 15.37],
                    [44.2, 15.37],
                    [44.2, 15.35],
                ]
            ],
        },
    }

    result = validator.validate_geometry(valid_field)

    print(f"\n   النتيجة - Result:")
    print(f"   - صالح / Valid: {result.is_valid}")
    print(f"   - المساحة / Area: {result.area_hectares:.4f} هكتار / hectares")
    print(f"   - المحيط / Perimeter: {result.perimeter_meters:.2f} متر / meters")
    print(f"   - المركز / Centroid: {result.centroid}")

    if result.issues:
        print(f"\n   المشاكل / Issues ({len(result.issues)}):")
        for i, issue in enumerate(result.issues, 1):
            print(f"   {i}. [{issue.severity}] {issue.message_ar}")
            print(f"      [{issue.severity}] {issue.message_en}")
    else:
        print("\n   ✓ لا توجد مشاكل - No issues found")

    # عرض معلومات اليمن - Display Yemen info
    print("\n3. معلومات حدود اليمن - Yemen bounds information:")
    print(
        f"   - خط الطول / Longitude: {YEMEN_BOUNDS['longitude']['min']}° - {YEMEN_BOUNDS['longitude']['max']}°"
    )
    print(
        f"   - خط العرض / Latitude: {YEMEN_BOUNDS['latitude']['min']}° - {YEMEN_BOUNDS['latitude']['max']}°"
    )
    print(
        f"   - الحد الأدنى للمساحة / Min area: {AREA_LIMITS['min_hectares']} هكتار / ha"
    )
    print(
        f"   - الحد الأقصى للمساحة / Max area: {AREA_LIMITS['max_hectares']} هكتار / ha"
    )

    # مثال على حقل صغير جداً - Example of too small field
    print("\n4. اختبار حقل صغير جداً - Testing too small field...")
    small_field = {
        "type": "Polygon",
        "coordinates": [
            [
                [44.2, 15.35],
                [44.201, 15.35],
                [44.201, 15.351],
                [44.2, 15.351],
                [44.2, 15.35],
            ]
        ],
    }

    result2 = validator.validate_geometry(small_field)
    print(f"   - المساحة / Area: {result2.area_hectares:.6f} هكتار / hectares")
    print(f"   - صالح / Valid: {result2.is_valid}")

    area_issues = [
        issue for issue in result2.issues if "area" in issue.issue_type.lower()
    ]
    if area_issues:
        print(f"   - المشاكل / Issues:")
        for issue in area_issues:
            print(f"     [{issue.severity}] {issue.message_ar}")

    # مثال على كشف التداخل - Example of overlap detection
    print("\n5. مثال على كشف التداخل - Overlap detection example...")

    new_field = {
        "type": "Polygon",
        "coordinates": [
            [
                [44.2, 15.35],
                [44.22, 15.35],
                [44.22, 15.37],
                [44.2, 15.37],
                [44.2, 15.35],
            ]
        ],
    }

    existing_fields = [
        {
            "field_id": "field_001",
            "name": "حقل مجاور - Adjacent Field",
            "user_id": "user_123",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [44.21, 15.36],
                        [44.23, 15.36],
                        [44.23, 15.38],
                        [44.21, 15.38],
                        [44.21, 15.36],
                    ]
                ],
            },
        }
    ]

    overlap_result = validator.check_overlap_with_existing(
        new_boundary=new_field,
        existing_fields=existing_fields,
        tolerance_percentage=5.0,
    )

    print(f"   - يوجد تداخل / Has overlap: {overlap_result.has_overlap}")
    if overlap_result.has_overlap:
        print(
            f"   - عدد الحقول المتداخلة / Overlapping fields: {len(overlap_result.overlapping_fields)}"
        )
        print(
            f"   - أقصى نسبة تداخل / Max overlap: {overlap_result.max_overlap_percentage:.2f}%"
        )

    # عرض ملف حدود اليمن - Display Yemen boundaries file
    print("\n6. ملف حدود اليمن - Yemen boundaries file:")
    yemen_file = Path(__file__).parent / "data" / "yemen_boundaries.geojson"
    if yemen_file.exists():
        print(f"   ✓ الملف موجود / File exists: {yemen_file}")
        with open(yemen_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            print(f"   - عدد المعالم / Feature count: {len(data.get('features', []))}")
            print(f"   - النوع / Type: {data.get('type')}")
    else:
        print(f"   ✗ الملف غير موجود / File not found: {yemen_file}")

    print("\n" + "=" * 80)
    print("✓ المثال اكتمل بنجاح - Example completed successfully")
    print("=" * 80)

except ImportError as e:
    print("\n" + "=" * 80)
    print("تنبيه: مكتبة Shapely غير مثبتة")
    print("Warning: Shapely library not installed")
    print("=" * 80)
    print(f"\nالخطأ / Error: {e}")
    print("\nيرجى تثبيت المتطلبات:")
    print("Please install requirements:")
    print("\n  pip install shapely>=2.0.0 pydantic>=2.0.0")
    print("\nثم قم بتشغيل المثال مرة أخرى:")
    print("Then run the example again:")
    print("\n  python example_boundary_validation.py")
    print("\n" + "=" * 80)

except Exception as e:
    print(f"\n✗ خطأ / Error: {e}")
    import traceback

    traceback.print_exc()
