"""
SPRING Add-on Usage Examples
أمثلة استخدام وحدة SPRING

This file demonstrates how to use the SPRING add-on for water management
in agricultural operations, with specific examples for Yemen context.

يوضح هذا الملف كيفية استخدام وحدة SPRING الإضافية لإدارة المياه
في العمليات الزراعية، مع أمثلة محددة للسياق اليمني.
"""

from datetime import date

from spring_integration import (
    calculate_water_footprint,
    generate_usage_alerts,
)
from spring_report_generator import (
    WaterBalanceCalculation,
    export_report_to_text,
    generate_spring_report,
)

# Import SPRING components
from water_metrics import (
    IrrigationEfficiency,
    IrrigationMethod,
    WaterEfficiencyScore,
    WaterQualityStatus,
    WaterQualityTest,
    WaterSource,
    WaterSourceType,
    WaterUsageMetric,
    classify_water_efficiency,
)

# ==================== EXAMPLE 1: Define Water Sources ====================


def example_1_water_sources():
    """
    Example 1: Define farm water sources with permits
    مثال 1: تحديد مصادر مياه المزرعة مع التصاريح
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Water Sources Definition")
    print("مثال 1: تحديد مصادر المياه")
    print("=" * 80)

    # Define a well source
    well = WaterSource(
        source_id="WELL-001",
        source_type=WaterSourceType.WELL,
        name_en="North Field Well",
        name_ar="بئر الحقل الشمالي",
        location="N15.5527 E48.5164",
        depth_meters=120.0,
        capacity_cubic_meters=50000.0,
        legal_permit_number="YE-WR-2024-1234",
        permit_expiry_date=date(2026, 12, 31),
        max_daily_extraction_m3=500.0,
        is_active=True,
    )

    # Define a rainwater harvesting system
    rainwater = WaterSource(
        source_id="RWH-001",
        source_type=WaterSourceType.RAINWATER,
        name_en="Roof Rainwater Collection",
        name_ar="تجميع مياه الأمطار من الأسطح",
        capacity_cubic_meters=100.0,
        is_active=True,
        notes="Monsoon season collection (April-September)",
    )

    print(f"\nWell Source: {well.name_en} / {well.name_ar}")
    print(f"  Depth: {well.depth_meters}m")
    print(f"  Permit: {well.legal_permit_number}")
    print(f"  Max Extraction: {well.max_daily_extraction_m3} m³/day")

    print(f"\nRainwater Source: {rainwater.name_en} / {rainwater.name_ar}")
    print(f"  Capacity: {rainwater.capacity_cubic_meters} m³")

    return [well, rainwater]


# ==================== EXAMPLE 2: Record Water Usage ====================


def example_2_water_usage():
    """
    Example 2: Record water usage for irrigation
    مثال 2: تسجيل استخدام المياه للري
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Water Usage Recording")
    print("مثال 2: تسجيل استخدام المياه")
    print("=" * 80)

    usage_records = []

    # Record 1: Drip irrigation for tomatoes
    usage1 = WaterUsageMetric(
        usage_id="WU-2024-12-001",
        source_id="WELL-001",
        field_id="FIELD-N1",
        crop_type="Tomatoes",
        measurement_date=date(2024, 12, 15),
        volume_cubic_meters=125.5,
        crop_area_hectares=2.5,
        irrigation_method=IrrigationMethod.DRIP,
        duration_hours=6.0,
    )
    usage_records.append(usage1)

    # Record 2: Sprinkler irrigation for cucumbers
    usage2 = WaterUsageMetric(
        usage_id="WU-2024-12-002",
        source_id="WELL-001",
        field_id="FIELD-S1",
        crop_type="Cucumbers",
        measurement_date=date(2024, 12, 16),
        volume_cubic_meters=180.0,
        crop_area_hectares=3.0,
        irrigation_method=IrrigationMethod.SPRINKLER,
        duration_hours=8.0,
    )
    usage_records.append(usage2)

    print(f"\nRecorded {len(usage_records)} water usage events:")
    for usage in usage_records:
        print(f"\n  {usage.crop_type} ({usage.irrigation_method.value})")
        print(f"    Volume: {usage.volume_cubic_meters} m³")
        print(f"    Area: {usage.crop_area_hectares} ha")
        print(f"    Rate: {usage.flow_rate_m3_per_hour:.2f} m³/h")

    return usage_records


# ==================== EXAMPLE 3: Water Quality Testing ====================


def example_3_water_quality():
    """
    Example 3: Record water quality test results
    مثال 3: تسجيل نتائج اختبار جودة المياه
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Water Quality Testing")
    print("مثال 3: اختبار جودة المياه")
    print("=" * 80)

    quality_test = WaterQualityTest(
        test_id="WQ-2024-Q4-001",
        source_id="WELL-001",
        test_date=date(2024, 12, 15),
        laboratory="Yemen Agricultural Laboratory",
        ph_level=7.2,
        ec_ds_per_m=1.5,
        tds_ppm=960,
        salinity_ppm=450,
        nitrate_ppm=8.5,
        phosphate_ppm=0.3,
        bacterial_count=10,
        quality_status=WaterQualityStatus.GOOD,
        meets_irrigation_standards=True,
        notes="Water quality suitable for drip irrigation of vegetables",
    )

    print(f"\nTest: {quality_test.test_id}")
    print(f"  pH: {quality_test.ph_level}")
    print(f"  EC: {quality_test.ec_ds_per_m} dS/m")
    print(f"  Salinity: {quality_test.salinity_ppm} ppm")
    print(f"  Status: {quality_test.quality_status.value}")
    print(
        f"  Meets Standards: {'✓' if quality_test.meets_irrigation_standards else '✗'}"
    )

    return [quality_test]


# ==================== EXAMPLE 4: Calculate Irrigation Efficiency ====================


def example_4_irrigation_efficiency():
    """
    Example 4: Calculate and record irrigation efficiency
    مثال 4: حساب وتسجيل كفاءة الري
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Irrigation Efficiency Calculation")
    print("مثال 4: حساب كفاءة الري")
    print("=" * 80)

    efficiency = IrrigationEfficiency(
        efficiency_id="IE-2024-Q4-001",
        field_id="FIELD-N1",
        measurement_period_start=date(2024, 10, 1),
        measurement_period_end=date(2024, 12, 31),
        irrigation_method=IrrigationMethod.DRIP,
        water_applied_m3=5000,
        water_stored_in_root_zone_m3=4250,
        application_efficiency_percent=85.0,
        distribution_uniformity_percent=92.0,
        water_use_efficiency_kg_per_m3=8.5,
        crop_yield_kg=42500,
        irrigation_scheduling_method="Soil moisture sensors + weather data",
        soil_moisture_monitoring=True,
        weather_based_scheduling=True,
        notes="High efficiency achieved with drip irrigation and precision scheduling",
    )

    level_en, level_ar = classify_water_efficiency(
        efficiency.application_efficiency_percent
    )

    print(f"\nEfficiency Assessment: {efficiency.efficiency_id}")
    print(f"  Application Efficiency: {efficiency.application_efficiency_percent}%")
    print(f"  Distribution Uniformity: {efficiency.distribution_uniformity_percent}%")
    print(f"  Water Use Efficiency: {efficiency.water_use_efficiency_kg_per_m3} kg/m³")
    print(f"  Performance Level: {level_en} / {level_ar}")

    return [efficiency]


# ==================== EXAMPLE 5: Calculate Water Balance ====================


def example_5_water_balance():
    """
    Example 5: Calculate water balance for the farm
    مثال 5: حساب توازن المياه للمزرعة
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Water Balance Calculation")
    print("مثال 5: حساب توازن المياه")
    print("=" * 80)

    balance = WaterBalanceCalculation(
        period_start=date(2024, 10, 1),
        period_end=date(2024, 12, 31),
        farm_id="FARM-YE-001",
        irrigation_water_m3=14500,
        rainfall_m3=450,
        recycled_water_m3=50,
        total_input_m3=15000,
        crop_evapotranspiration_m3=12500,
        runoff_m3=300,
        deep_percolation_m3=1800,
        evaporation_m3=400,
        total_output_m3=15000,
        storage_change_m3=0,
        balance_error_percent=0.5,
        beneficial_use_efficiency_percent=83.3,
        water_productivity_kg_per_m3=6.8,
    )

    print(f"\nWater Balance ({balance.period_start} to {balance.period_end}):")
    print("\n  INPUTS:")
    print(f"    Irrigation: {balance.irrigation_water_m3:,.0f} m³")
    print(f"    Rainfall: {balance.rainfall_m3:,.0f} m³")
    print(f"    Recycled: {balance.recycled_water_m3:,.0f} m³")
    print(f"    TOTAL: {balance.total_input_m3:,.0f} m³")

    print("\n  OUTPUTS:")
    print(f"    Crop ET: {balance.crop_evapotranspiration_m3:,.0f} m³")
    print(f"    Runoff: {balance.runoff_m3:,.0f} m³")
    print(f"    Deep Percolation: {balance.deep_percolation_m3:,.0f} m³")
    print(f"    Evaporation: {balance.evaporation_m3:,.0f} m³")
    print(f"    TOTAL: {balance.total_output_m3:,.0f} m³")

    print("\n  EFFICIENCY:")
    print(f"    Beneficial Use: {balance.beneficial_use_efficiency_percent}%")
    print(f"    Water Productivity: {balance.water_productivity_kg_per_m3} kg/m³")

    return balance


# ==================== EXAMPLE 6: Calculate Water Footprint ====================


def example_6_water_footprint():
    """
    Example 6: Calculate water footprint for tomato production
    مثال 6: حساب البصمة المائية لإنتاج الطماطم
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Water Footprint Calculation")
    print("مثال 6: حساب البصمة المائية")
    print("=" * 80)

    footprint = calculate_water_footprint(
        crop_type="Tomatoes",
        production_kg=50000,
        irrigation_water_m3=7500,
        rainfall_water_m3=2500,
        fertilizer_use_kg=500,
    )

    print(f"\nWater Footprint for {footprint.crop_type}:")
    print(f"  Production: {footprint.production_kg:,.0f} kg")
    print(f"\n  Blue Water (irrigation): {footprint.blue_water_m3_per_kg} m³/kg")
    print(f"  Green Water (rainfall): {footprint.green_water_m3_per_kg} m³/kg")
    print(f"  Grey Water (pollution): {footprint.grey_water_m3_per_kg} m³/kg")
    print(f"  TOTAL: {footprint.total_water_footprint_m3_per_kg} m³/kg")

    if footprint.regional_benchmark_m3_per_kg:
        print(f"\n  Regional Benchmark: {footprint.regional_benchmark_m3_per_kg} m³/kg")
    if footprint.global_benchmark_m3_per_kg:
        print(f"  Global Benchmark: {footprint.global_benchmark_m3_per_kg} m³/kg")
    print(f"\n  Performance: {footprint.performance_vs_benchmark}")

    return footprint


# ==================== EXAMPLE 7: Generate Alerts ====================


def example_7_generate_alerts(sources, usage_records):
    """
    Example 7: Generate water usage alerts
    مثال 7: إنشاء تنبيهات استخدام المياه
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Water Usage Alerts")
    print("مثال 7: تنبيهات استخدام المياه")
    print("=" * 80)

    alerts = generate_usage_alerts(
        farm_id="FARM-YE-001",
        usage_records=usage_records,
        water_sources=sources,
        current_month_usage_m3=15000,
        previous_month_usage_m3=11000,
        groundwater_level_change_m=-2.5,  # Declined 2.5 meters - critical for Yemen
    )

    print(f"\nGenerated {len(alerts)} alerts:")
    for alert in alerts:
        print(f"\n  [{alert.severity.value}] {alert.alert_type.value}")
        print(f"    EN: {alert.title_en}")
        print(f"    AR: {alert.title_ar}")
        print(f"    {alert.message_en}")
        if alert.recommended_action_en:
            print(f"    Action: {alert.recommended_action_en}")

    return alerts


# ==================== EXAMPLE 8: Generate SPRING Report ====================


def example_8_generate_report(
    balance, sources, usage_records, quality_tests, efficiency_records
):
    """
    Example 8: Generate complete SPRING compliance report
    مثال 8: إنشاء تقرير امتثال SPRING كامل
    """
    print("\n" + "=" * 80)
    print("EXAMPLE 8: SPRING Compliance Report")
    print("مثال 8: تقرير امتثال SPRING")
    print("=" * 80)

    # Define compliant items (for demo, marking all mandatory as compliant)
    compliant_items = [
        "WS.01",
        "WS.02",
        "WE.01",
        "WE.02",
        "WE.03",
        "IS.01",
        "IS.02",
        "IS.03",
        "WQ.01",
        "WQ.02",
        "WQ.03",
        "LC.01",
        "LC.02",
        "MR.01",
        "MR.02",
        "MR.03",
    ]

    # Create efficiency score
    efficiency_score = WaterEfficiencyScore(
        assessment_id="SPRING-2024-Q4",
        farm_id="FARM-YE-001",
        assessment_date=date(2024, 12, 31),
        assessment_period_start=date(2024, 10, 1),
        assessment_period_end=date(2024, 12, 31),
        total_water_sources=len(sources),
        sources_with_legal_permits=len([s for s in sources if s.legal_permit_number]),
        total_water_used_m3=15000,
        total_irrigated_area_ha=10.0,
        water_use_per_hectare_m3=1500,
        average_application_efficiency=82.0,
        drip_irrigation_percentage=85.0,
        soil_moisture_monitoring_coverage=75.0,
        rainwater_harvested_m3=500,
        rainwater_percentage=3.33,
        water_quality_tests_conducted=4,
        sources_meeting_standards=len(sources),
        overall_spring_score=85.5,
        compliance_level="EXCELLENT",
    )

    # Generate report
    report = generate_spring_report(
        farm_id="FARM-YE-001",
        farm_name_en="Al-Khair Agricultural Farm",
        farm_name_ar="مزرعة الخير الزراعية",
        period_start=date(2024, 10, 1),
        period_end=date(2024, 12, 31),
        water_balance=balance,
        efficiency_score=efficiency_score,
        compliant_items=compliant_items,
        water_sources=sources,
        usage_records=usage_records,
        quality_tests=quality_tests,
        efficiency_records=efficiency_records,
        include_yemen_context=True,
    )

    print(f"\nReport Generated: {report.report_id}")
    print(f"  Farm: {report.farm_name_en} / {report.farm_name_ar}")
    print(f"  Period: {report.report_period_start} to {report.report_period_end}")
    print(f"  Overall Score: {report.efficiency_score.overall_spring_score}")
    print(
        f"  Compliance: {report.compliance_summary['overall_compliance_percentage']}%"
    )
    print(f"  Sections: {len(report.sections)}")
    print(f"  Recommendations: {len(report.recommendations_en)}")

    # Export to text
    text_report = export_report_to_text(report, language="en")
    print(f"\n  Report Length: {len(text_report)} characters")
    print(f"  First 500 chars:\n{text_report[:500]}...")

    return report


# ==================== MAIN EXECUTION ====================


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("SPRING ADD-ON USAGE EXAMPLES")
    print("أمثلة استخدام وحدة SPRING الإضافية")
    print("=" * 80)

    # Run examples
    sources = example_1_water_sources()
    usage_records = example_2_water_usage()
    quality_tests = example_3_water_quality()
    efficiency_records = example_4_irrigation_efficiency()
    balance = example_5_water_balance()
    footprint = example_6_water_footprint()
    alerts = example_7_generate_alerts(sources, usage_records)
    report = example_8_generate_report(
        balance, sources, usage_records, quality_tests, efficiency_records
    )

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
    print("تم إكمال جميع الأمثلة بنجاح!")
    print("=" * 80)
    print("\nFor more information, see README.md")
    print("لمزيد من المعلومات، راجع README.md")


if __name__ == "__main__":
    main()
