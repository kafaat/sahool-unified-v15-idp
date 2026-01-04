"""
مثال استخدام خدمة تصدير البيانات
Example usage of SAHOOL Data Export Service
============================================

This file demonstrates how to use the DataExporter service
to export field data in various formats and generate reports.
"""

from datetime import date, timedelta

from data_exporter import (
    DataExporter,
    ExportFormat,
    ReportType,
    export_field_csv,
    export_field_excel,
    generate_daily_report,
)


def example_basic_csv_export():
    """
    مثال 1: تصدير بيانات الحقل بصيغة CSV
    Example 1: Basic CSV export of field data
    """
    print("=" * 60)
    print("Example 1: CSV Export")
    print("=" * 60)

    exporter = DataExporter()

    # Export field data for the last 30 days
    end_date = date.today()
    start_date = end_date - timedelta(days=30)

    result = exporter.export_field_data(
        field_id="FIELD_001",
        format=ExportFormat.CSV,
        date_range=(start_date, end_date),
        include_metadata=True,
        include_ndvi=True,
        include_sensors=True,
        include_weather=True,
        include_recommendations=True,
        include_actions=True,
    )

    print("✓ Export completed successfully!")
    print(f"  Filename: {result.filename}")
    print(f"  Format: {result.format.value}")
    print(f"  Size: {result.size_bytes} bytes")
    print(f"  Generated at: {result.generated_at}")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "w", encoding="utf-8") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_excel_multi_sheet_export():
    """
    مثال 2: تصدير بيانات الحقل بصيغة Excel مع أوراق متعددة
    Example 2: Excel export with multiple sheets
    """
    print("=" * 60)
    print("Example 2: Excel Multi-Sheet Export")
    print("=" * 60)

    exporter = DataExporter()

    result = exporter.export_field_data(
        field_id="FIELD_001",
        format=ExportFormat.EXCEL,
        date_range=(date.today() - timedelta(days=60), date.today()),
        include_metadata=True,
        include_ndvi=True,
        include_sensors=True,
        include_weather=True,
        include_recommendations=True,
        include_actions=True,
    )

    print("✓ Excel export completed!")
    print(f"  Filename: {result.filename}")
    print("  Sheets included:")
    print("    - معلومات الحقل (Field Info)")
    print("    - NDVI History")
    print("    - قراءات المستشعرات (Sensors)")
    print("    - بيانات الطقس (Weather)")
    print("    - التوصيات (Recommendations)")
    print("    - الإجراءات (Actions)")
    print(f"  Size: {result.size_bytes} bytes")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "wb") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_geojson_export():
    """
    مثال 3: تصدير بيانات الحقل بصيغة GeoJSON
    Example 3: GeoJSON export for spatial data
    """
    print("=" * 60)
    print("Example 3: GeoJSON Export")
    print("=" * 60)

    exporter = DataExporter()

    result = exporter.export_field_data(
        field_id="FIELD_001",
        format=ExportFormat.GEOJSON,
        include_metadata=True,
        include_ndvi=True,
    )

    print("✓ GeoJSON export completed!")
    print(f"  Filename: {result.filename}")
    print(f"  Format: {result.format.value}")
    print(f"  Content Type: {result.content_type}")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "w", encoding="utf-8") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_sensor_readings_export():
    """
    مثال 4: تصدير قراءات المستشعرات فقط
    Example 4: Export only sensor readings
    """
    print("=" * 60)
    print("Example 4: Sensor Readings Export")
    print("=" * 60)

    exporter = DataExporter()

    # Export last 7 days of sensor data
    end_date = date.today()
    start_date = end_date - timedelta(days=7)

    result = exporter.export_sensor_readings(
        field_id="FIELD_001",
        format=ExportFormat.EXCEL,
        date_range=(start_date, end_date),
    )

    print("✓ Sensor readings exported!")
    print(f"  Filename: {result.filename}")
    print(f"  Period: {start_date} to {end_date}")
    print(f"  Size: {result.size_bytes} bytes")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "wb") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_recommendations_export():
    """
    مثال 5: تصدير التوصيات فقط
    Example 5: Export only recommendations
    """
    print("=" * 60)
    print("Example 5: Recommendations Export")
    print("=" * 60)

    exporter = DataExporter()

    result = exporter.export_recommendations(
        field_id="FIELD_001",
        format=ExportFormat.PDF,
        date_range=(date.today() - timedelta(days=30), date.today()),
    )

    print("✓ Recommendations exported as PDF!")
    print(f"  Filename: {result.filename}")
    print(f"  Size: {result.size_bytes} bytes")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "wb") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_daily_summary_report():
    """
    مثال 6: إنشاء تقرير يومي شامل
    Example 6: Generate comprehensive daily summary report
    """
    print("=" * 60)
    print("Example 6: Daily Summary Report")
    print("=" * 60)

    exporter = DataExporter()

    result = exporter.generate_report(
        report_type=ReportType.DAILY_SUMMARY,
        params={"field_id": "FIELD_001", "date": date.today()},
    )

    print("✓ Daily summary report generated!")
    print(f"  Filename: {result.filename}")
    print(f"  Report Date: {date.today()}")
    print(f"  Size: {result.size_bytes} bytes")
    print()
    print("  Report includes:")
    print("    - Executive summary with status indicators")
    print("    - Field information")
    print("    - NDVI analysis and trends")
    print("    - Sensor readings")
    print("    - Weather data and forecast")
    print("    - Recommendations")
    print("    - Actions taken")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "wb") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_weekly_analysis_report():
    """
    مثال 7: إنشاء تقرير تحليل أسبوعي
    Example 7: Generate weekly analysis report
    """
    print("=" * 60)
    print("Example 7: Weekly Analysis Report")
    print("=" * 60)

    exporter = DataExporter()

    result = exporter.generate_report(
        report_type=ReportType.WEEKLY_ANALYSIS,
        params={"field_id": "FIELD_001", "end_date": date.today()},
    )

    print("✓ Weekly analysis report generated!")
    print(f"  Filename: {result.filename}")
    print(f"  Size: {result.size_bytes} bytes")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "wb") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_monthly_report():
    """
    مثال 8: إنشاء تقرير شهري
    Example 8: Generate monthly report
    """
    print("=" * 60)
    print("Example 8: Monthly Report")
    print("=" * 60)

    exporter = DataExporter()

    result = exporter.generate_report(
        report_type=ReportType.MONTHLY_REPORT,
        params={
            "field_id": "FIELD_001",
            "month": date.today().month,
            "year": date.today().year,
        },
    )

    print("✓ Monthly report generated!")
    print(f"  Filename: {result.filename}")
    print("  Format: Excel with multiple sheets")
    print(f"  Size: {result.size_bytes} bytes")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "wb") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_seasonal_comparison():
    """
    مثال 9: إنشاء تقرير مقارنة المواسم
    Example 9: Generate seasonal comparison report
    """
    print("=" * 60)
    print("Example 9: Seasonal Comparison Report")
    print("=" * 60)

    exporter = DataExporter()

    result = exporter.generate_report(
        report_type=ReportType.SEASONAL_COMPARISON,
        params={
            "field_id": "FIELD_001",
            "seasons": ["2023-winter", "2024-spring", "2024-summer"],
        },
    )

    print("✓ Seasonal comparison report generated!")
    print(f"  Filename: {result.filename}")
    print("  Format: JSON")
    print("  Seasons compared: 3")
    print(f"  Size: {result.size_bytes} bytes")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "w", encoding="utf-8") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_yield_forecast_report():
    """
    مثال 10: إنشاء تقرير توقعات الإنتاج
    Example 10: Generate yield forecast report
    """
    print("=" * 60)
    print("Example 10: Yield Forecast Report")
    print("=" * 60)

    exporter = DataExporter()

    result = exporter.generate_report(
        report_type=ReportType.YIELD_FORECAST, params={"field_id": "FIELD_001"}
    )

    print("✓ Yield forecast report generated!")
    print(f"  Filename: {result.filename}")
    print("  Format: PDF")
    print(f"  Size: {result.size_bytes} bytes")
    print()
    print("  Report includes:")
    print("    - Predicted yield (kg/ha)")
    print("    - Confidence score")
    print("    - Contributing factors")
    print("    - Recommendations for optimization")
    print()

    # Save to file
    with open(f"/tmp/{result.filename}", "wb") as f:
        f.write(result.data)
    print(f"✓ File saved to: /tmp/{result.filename}")
    print()


def example_convenience_functions():
    """
    مثال 11: استخدام دوال الاختصار
    Example 11: Using convenience functions
    """
    print("=" * 60)
    print("Example 11: Convenience Functions")
    print("=" * 60)

    # Quick CSV export
    print("Quick CSV export...")
    result = export_field_csv("FIELD_001")
    print(f"✓ CSV exported: {result.filename}")

    # Quick Excel export
    print("Quick Excel export...")
    result = export_field_excel("FIELD_001")
    print(f"✓ Excel exported: {result.filename}")

    # Quick daily report
    print("Quick daily report...")
    result = generate_daily_report("FIELD_001")
    print(f"✓ Daily report generated: {result.filename}")
    print()


def example_custom_arabic_headers():
    """
    مثال 12: تصدير CSV مع عناوين عربية مخصصة
    Example 12: CSV export with custom Arabic headers
    """
    print("=" * 60)
    print("Example 12: Custom Arabic Headers")
    print("=" * 60)

    exporter = DataExporter()

    # Customize Arabic headers
    exporter.ARABIC_HEADERS.update(
        {"custom_field": "حقل مخصص", "new_metric": "مؤشر جديد"}
    )

    result = exporter.export_field_data(
        field_id="FIELD_001", format=ExportFormat.CSV, include_ndvi=True
    )

    print("✓ CSV with custom headers exported!")
    print(f"  Filename: {result.filename}")
    print("  Headers are fully bilingual (Arabic/English)")
    print()


def main():
    """
    Run all examples
    تشغيل جميع الأمثلة
    """
    print("\n")
    print("█" * 60)
    print("█" + " " * 58 + "█")
    print("█" + "  SAHOOL Data Export Service - Examples  ".center(58) + "█")
    print("█" + "  خدمة تصدير البيانات - أمثلة  ".center(58) + "█")
    print("█" + " " * 58 + "█")
    print("█" * 60)
    print("\n")

    try:
        # Basic exports
        example_basic_csv_export()
        example_excel_multi_sheet_export()
        example_geojson_export()

        # Specialized exports
        example_sensor_readings_export()
        example_recommendations_export()

        # Reports
        example_daily_summary_report()
        example_weekly_analysis_report()
        example_monthly_report()
        example_seasonal_comparison()
        example_yield_forecast_report()

        # Convenience functions
        example_convenience_functions()
        example_custom_arabic_headers()

        print("\n")
        print("=" * 60)
        print("✓ All examples completed successfully!")
        print("=" * 60)
        print("\nAll exported files saved to /tmp/")
        print()

    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
