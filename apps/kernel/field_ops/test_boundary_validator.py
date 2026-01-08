"""
اختبار محقق حدود الحقول - Boundary Validator Test
====================================================
أمثلة شاملة لاستخدام خدمة التحقق من حدود الحقول

Comprehensive examples of using the field boundary validation service
"""

from pathlib import Path

from services.boundary_validator import (
    AREA_LIMITS,
    YEMEN_BOUNDS,
    YEMEN_GOVERNORATES,
    BoundaryValidator,
)


def test_basic_validation():
    """
    اختبار التحقق الأساسي من حدود حقل
    Test basic field boundary validation
    """
    print("=" * 80)
    print("اختبار 1: التحقق الأساسي من حدود حقل صالح")
    print("Test 1: Basic validation of valid field boundary")
    print("=" * 80)

    # إنشاء المحقق - Create validator
    validator = BoundaryValidator()

    # حقل صالح في صنعاء - Valid field in Sana'a
    valid_field = {
        "type": "Feature",
        "properties": {"name": "حقل القمح - Wheat Field", "crop": "wheat", "farmer": "أحمد محمد"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [44.2, 15.35],  # نقطة 1
                    [44.21, 15.35],  # نقطة 2
                    [44.21, 15.36],  # نقطة 3
                    [44.2, 15.36],  # نقطة 4
                    [44.2, 15.35],  # نقطة الإغلاق
                ]
            ],
        },
    }

    # التحقق من الحقل - Validate field
    result = validator.validate_geometry(valid_field)

    # عرض النتائج - Display results
    print(f"\nصالح: {result.is_valid}")
    print(f"Valid: {result.is_valid}")
    print(f"\nالمساحة: {result.area_hectares:.4f} هكتار")
    print(f"Area: {result.area_hectares:.4f} hectares")
    print(f"\nالمحيط: {result.perimeter_meters:.2f} متر")
    print(f"Perimeter: {result.perimeter_meters:.2f} meters")
    print(f"\nالمركز: {result.centroid}")
    print(f"Centroid: {result.centroid}")
    print(f"\nالمربع المحيط: {result.bounding_box}")
    print(f"Bounding box: {result.bounding_box}")

    if result.issues:
        print(f"\nالمشاكل المكتشفة: {len(result.issues)}")
        print(f"Issues found: {len(result.issues)}")
        for i, issue in enumerate(result.issues, 1):
            print(f"\n  {i}. [{issue.severity.value}] {issue.message_ar}")
            print(f"     [{issue.severity.value}] {issue.message_en}")
            print(f"     قابل للإصلاح: {issue.fixable} - Fixable: {issue.fixable}")
    else:
        print("\nلا توجد مشاكل - No issues found ✓")

    return result


def test_self_intersection():
    """
    اختبار كشف التقاطع الذاتي
    Test self-intersection detection
    """
    print("\n" + "=" * 80)
    print("اختبار 2: كشف التقاطع الذاتي")
    print("Test 2: Self-intersection detection")
    print("=" * 80)

    validator = BoundaryValidator()

    # حقل مع تقاطع ذاتي - Field with self-intersection (bow-tie shape)
    self_intersecting_field = {
        "type": "Polygon",
        "coordinates": [
            [
                [44.2, 15.35],
                [44.21, 15.36],  # يتقاطع مع الخط التالي
                [44.21, 15.35],
                [44.2, 15.36],
                [44.2, 15.35],
            ]
        ],
    }

    result = validator.validate_geometry(self_intersecting_field)

    print(f"\nصالح: {result.is_valid}")
    print(f"Valid: {result.is_valid}")
    print(f"\nعدد المشاكل: {len(result.issues)}")
    print(f"Issue count: {len(result.issues)}")

    for i, issue in enumerate(result.issues, 1):
        print(f"\n  {i}. [{issue.severity.value}] {issue.message_ar}")
        print(f"     [{issue.severity.value}] {issue.message_en}")

    # عرض الهندسة المصلحة إذا كانت متوفرة
    if result.fixed_geometry:
        print("\nالهندسة المصلحة متوفرة - Fixed geometry available ✓")

    return result


def test_area_limits():
    """
    اختبار حدود المساحة
    Test area limits
    """
    print("\n" + "=" * 80)
    print("اختبار 3: حدود المساحة")
    print("Test 3: Area limits")
    print("=" * 80)

    validator = BoundaryValidator()

    # حقل صغير جداً - Very small field (< 0.1 ha)
    small_field = {
        "type": "Polygon",
        "coordinates": [
            [
                [44.2, 15.35],
                [44.201, 15.35],  # صغير جداً
                [44.201, 15.351],
                [44.2, 15.351],
                [44.2, 15.35],
            ]
        ],
    }

    result = validator.validate_geometry(small_field)

    print(f"\nالمساحة: {result.area_hectares:.6f} هكتار")
    print(f"Area: {result.area_hectares:.6f} hectares")
    print(f"الحد الأدنى: {AREA_LIMITS['min_hectares']} هكتار")
    print(f"Minimum: {AREA_LIMITS['min_hectares']} hectares")

    area_issues = [issue for issue in result.issues if "area" in issue.issue_type.lower()]
    if area_issues:
        for issue in area_issues:
            print(f"\n  [{issue.severity.value}] {issue.message_ar}")
            print(f"  [{issue.severity.value}] {issue.message_en}")

    return result


def test_yemen_bounds():
    """
    اختبار حدود اليمن الجغرافية
    Test Yemen geographic bounds
    """
    print("\n" + "=" * 80)
    print("اختبار 4: حدود اليمن الجغرافية")
    print("Test 4: Yemen geographic bounds")
    print("=" * 80)

    validator = BoundaryValidator()

    # حقل خارج حدود اليمن - Field outside Yemen bounds
    outside_field = {
        "type": "Polygon",
        "coordinates": [
            [
                [30.0, 20.0],  # خارج اليمن
                [30.1, 20.0],
                [30.1, 20.1],
                [30.0, 20.1],
                [30.0, 20.0],
            ]
        ],
    }

    result = validator.validate_geometry(outside_field)

    print("\nحدود اليمن - Yemen bounds:")
    print(f"  خط العرض: {YEMEN_BOUNDS['latitude']['min']} - {YEMEN_BOUNDS['latitude']['max']}")
    print(f"  Latitude: {YEMEN_BOUNDS['latitude']['min']} - {YEMEN_BOUNDS['latitude']['max']}")
    print(f"  خط الطول: {YEMEN_BOUNDS['longitude']['min']} - {YEMEN_BOUNDS['longitude']['max']}")
    print(f"  Longitude: {YEMEN_BOUNDS['longitude']['min']} - {YEMEN_BOUNDS['longitude']['max']}")

    print(f"\nحدود الحقل - Field bounds: {result.bounding_box}")

    yemen_issues = [issue for issue in result.issues if "yemen" in issue.issue_type.lower()]
    if yemen_issues:
        for issue in yemen_issues:
            print(f"\n  [{issue.severity.value}] {issue.message_ar}")
            print(f"  [{issue.severity.value}] {issue.message_en}")

    return result


def test_overlap_detection():
    """
    اختبار كشف التداخل بين الحقول
    Test field overlap detection
    """
    print("\n" + "=" * 80)
    print("اختبار 5: كشف التداخل بين الحقول")
    print("Test 5: Field overlap detection")
    print("=" * 80)

    validator = BoundaryValidator()

    # حقل جديد - New field
    new_field = {
        "type": "Polygon",
        "coordinates": [
            [[44.2, 15.35], [44.22, 15.35], [44.22, 15.37], [44.2, 15.37], [44.2, 15.35]]
        ],
    }

    # قاعدة بيانات الحقول الموجودة - Existing fields database
    existing_fields = [
        {
            "field_id": "field_001",
            "name": "حقل القمح - Wheat Field",
            "user_id": "user_123",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[44.21, 15.36], [44.23, 15.36], [44.23, 15.38], [44.21, 15.38], [44.21, 15.36]]
                ],
            },
        },
        {
            "field_id": "field_002",
            "name": "حقل الذرة - Corn Field",
            "user_id": "user_456",
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [[44.19, 15.34], [44.2, 15.34], [44.2, 15.36], [44.19, 15.36], [44.19, 15.34]]
                ],
            },
        },
    ]

    # فحص التداخل - Check overlap
    overlap_result = validator.check_overlap_with_existing(
        new_boundary=new_field, existing_fields=existing_fields, tolerance_percentage=5.0
    )

    print(f"\nيوجد تداخل: {overlap_result.has_overlap}")
    print(f"Has overlap: {overlap_result.has_overlap}")

    if overlap_result.has_overlap:
        print(f"\nعدد الحقول المتداخلة: {len(overlap_result.overlapping_fields)}")
        print(f"Overlapping field count: {len(overlap_result.overlapping_fields)}")
        print(f"\nمساحة التداخل الكلية: {overlap_result.total_overlap_area_hectares:.4f} هكتار")
        print(f"Total overlap area: {overlap_result.total_overlap_area_hectares:.4f} hectares")
        print(f"\nأقصى نسبة تداخل: {overlap_result.max_overlap_percentage:.2f}%")
        print(f"Max overlap percentage: {overlap_result.max_overlap_percentage:.2f}%")

        for i, field in enumerate(overlap_result.overlapping_fields, 1):
            print(f"\n  {i}. حقل: {field['field_id']} - {field.get('field_name', '')}")
            print(f"     Field: {field['field_id']} - {field.get('field_name', '')}")
            print(f"     مساحة التداخل: {field['overlap_area_hectares']:.4f} هكتار")
            print(f"     Overlap area: {field['overlap_area_hectares']:.4f} hectares")
            print(f"     نسبة التداخل: {field['overlap_percentage']:.2f}%")
            print(f"     Overlap percentage: {field['overlap_percentage']:.2f}%")
    else:
        print("\nلا يوجد تداخل - No overlap ✓")

    return overlap_result


def test_geometry_fixing():
    """
    اختبار إصلاح المشاكل الهندسية
    Test geometry issue fixing
    """
    print("\n" + "=" * 80)
    print("اختبار 6: إصلاح المشاكل الهندسية")
    print("Test 6: Geometry issue fixing")
    print("=" * 80)

    validator = BoundaryValidator()

    # حقل مع نقاط مكررة - Field with duplicate points
    field_with_issues = {
        "type": "Polygon",
        "coordinates": [
            [
                [44.2, 15.35],
                [44.2, 15.35],  # نقطة مكررة
                [44.21, 15.35],
                [44.21, 15.35],  # نقطة مكررة
                [44.21, 15.36],
                [44.2, 15.36],
                [44.2, 15.35],
            ]
        ],
    }

    result = validator.validate_geometry(field_with_issues)

    print(f"\nالهندسة الأصلية صالحة: {result.is_valid}")
    print(f"Original geometry valid: {result.is_valid}")

    duplicate_issues = [issue for issue in result.issues if issue.issue_type == "duplicate_points"]
    if duplicate_issues:
        print(f"\nمشاكل النقاط المكررة: {len(duplicate_issues)}")
        print(f"Duplicate point issues: {len(duplicate_issues)}")
        for issue in duplicate_issues:
            print(f"  - {issue.message_ar}")
            print(f"    {issue.message_en}")

    if result.fixed_geometry:
        print("\n✓ تم إصلاح الهندسة تلقائياً")
        print("✓ Geometry auto-fixed")
        print(f"\nعدد النقاط الأصلية: {len(field_with_issues['coordinates'][0])}")
        print(f"Original point count: {len(field_with_issues['coordinates'][0])}")
        print(f"عدد النقاط بعد الإصلاح: {len(result.fixed_geometry['coordinates'][0])}")
        print(f"Fixed point count: {len(result.fixed_geometry['coordinates'][0])}")

    return result


def test_with_yemen_boundaries():
    """
    اختبار التحقق مع حدود اليمن التفصيلية
    Test validation with detailed Yemen boundaries
    """
    print("\n" + "=" * 80)
    print("اختبار 7: التحقق مع حدود اليمن التفصيلية")
    print("Test 7: Validation with detailed Yemen boundaries")
    print("=" * 80)

    # تحميل حدود اليمن - Load Yemen boundaries
    data_dir = Path(__file__).parent / "data"
    yemen_boundaries_path = data_dir / "yemen_boundaries.geojson"

    if yemen_boundaries_path.exists():
        validator = BoundaryValidator(yemen_boundaries_path=str(yemen_boundaries_path))

        print(f"\n✓ تم تحميل حدود اليمن من: {yemen_boundaries_path}")
        print(f"✓ Yemen boundaries loaded from: {yemen_boundaries_path}")

        # حقل في صنعاء - Field in Sana'a
        field_in_sanaa = {
            "type": "Polygon",
            "coordinates": [
                [[44.2, 15.35], [44.22, 15.35], [44.22, 15.37], [44.2, 15.37], [44.2, 15.35]]
            ],
        }

        result = validator.validate_geometry(field_in_sanaa)

        print(f"\nصالح: {result.is_valid}")
        print(f"Valid: {result.is_valid}")
        print(f"المساحة: {result.area_hectares:.4f} هكتار")
        print(f"Area: {result.area_hectares:.4f} hectares")

        # التحقق من المحافظة - Check governorate
        from shapely.geometry import shape

        shape(field_in_sanaa)

        print("\nالمحافظات المتاحة للتحقق:")
        print("Available governorates for validation:")
        for gov in YEMEN_GOVERNORATES[:5]:  # عرض أول 5
            print(f"  - {gov}")
        print(f"  ... وغيرها ({len(YEMEN_GOVERNORATES)} محافظة)")
        print(f"  ... and more ({len(YEMEN_GOVERNORATES)} governorates)")

        return result
    else:
        print(f"\nملف حدود اليمن غير موجود: {yemen_boundaries_path}")
        print(f"Yemen boundaries file not found: {yemen_boundaries_path}")
        return None


def test_simplification():
    """
    اختبار تبسيط الهندسة
    Test geometry simplification
    """
    print("\n" + "=" * 80)
    print("اختبار 8: تبسيط الهندسة")
    print("Test 8: Geometry simplification")
    print("=" * 80)

    validator = BoundaryValidator()

    # حقل مع نقاط كثيرة - Field with many points
    complex_field = {
        "type": "Polygon",
        "coordinates": [
            [
                [44.2, 15.35],
                [44.205, 15.35],
                [44.21, 15.35],
                [44.215, 15.352],
                [44.22, 15.355],
                [44.22, 15.36],
                [44.22, 15.365],
                [44.215, 15.37],
                [44.21, 15.37],
                [44.205, 15.37],
                [44.2, 15.37],
                [44.2, 15.365],
                [44.2, 15.36],
                [44.2, 15.355],
                [44.2, 15.35],
            ]
        ],
    }

    result = validator.validate_geometry(complex_field)

    print(f"\nعدد النقاط الأصلية: {len(complex_field['coordinates'][0])}")
    print(f"Original point count: {len(complex_field['coordinates'][0])}")

    if result.simplified_geometry:
        print(f"عدد النقاط المبسطة: {len(result.simplified_geometry['coordinates'][0])}")
        print(f"Simplified point count: {len(result.simplified_geometry['coordinates'][0])}")

        print(f"\nالمساحة الأصلية: {result.area_hectares:.6f} هكتار")
        print(f"Original area: {result.area_hectares:.6f} hectares")

        # حساب مساحة الهندسة المبسطة
        from shapely.geometry import shape

        simplified_polygon = shape(result.simplified_geometry)
        simplified_area = validator.calculate_area_hectares(simplified_polygon)

        print(f"المساحة المبسطة: {simplified_area:.6f} هكتار")
        print(f"Simplified area: {simplified_area:.6f} hectares")

        difference = abs(result.area_hectares - simplified_area)
        print(
            f"\nالفرق في المساحة: {difference:.6f} هكتار ({difference / result.area_hectares * 100:.2f}%)"
        )
        print(
            f"Area difference: {difference:.6f} hectares ({difference / result.area_hectares * 100:.2f}%)"
        )

    return result


def main():
    """
    تشغيل جميع الاختبارات
    Run all tests
    """
    print("\n" + "=" * 80)
    print("اختبار خدمة التحقق من حدود الحقول - SAHOOL Boundary Validator Tests")
    print("=" * 80)

    try:
        # تشغيل الاختبارات - Run tests
        test_basic_validation()
        test_self_intersection()
        test_area_limits()
        test_yemen_bounds()
        test_overlap_detection()
        test_geometry_fixing()
        test_with_yemen_boundaries()
        test_simplification()

        print("\n" + "=" * 80)
        print("✓ جميع الاختبارات اكتملت بنجاح")
        print("✓ All tests completed successfully")
        print("=" * 80)

    except Exception as e:
        print(f"\n✗ خطأ في الاختبارات: {e}")
        print(f"✗ Test error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
