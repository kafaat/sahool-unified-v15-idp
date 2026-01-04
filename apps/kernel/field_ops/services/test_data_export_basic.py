"""
اختبار أساسي لخدمة تصدير البيانات
Basic test for Data Export Service
====================================

Simple tests to verify the data export service works correctly
"""

import sys


def test_imports():
    """Test that all modules import correctly"""
    print("Testing imports...")

    try:
        from data_exporter import (
            DataExporter,
            ExportFormat,
            ExportResult,
            ReportType,
            export_field_csv,
            export_field_excel,
            generate_daily_report,
        )
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False


def test_enums():
    """Test that enums are defined correctly"""
    print("\nTesting enums...")

    try:
        from data_exporter import ExportFormat, ReportType

        # Test ExportFormat
        assert ExportFormat.CSV == "csv"
        assert ExportFormat.EXCEL == "xlsx"
        assert ExportFormat.JSON == "json"
        assert ExportFormat.GEOJSON == "geojson"
        assert ExportFormat.PDF == "pdf"
        print("✓ ExportFormat enum works")

        # Test ReportType
        assert ReportType.DAILY_SUMMARY == "daily_summary"
        assert ReportType.WEEKLY_ANALYSIS == "weekly_analysis"
        assert ReportType.MONTHLY_REPORT == "monthly_report"
        assert ReportType.SEASONAL_COMPARISON == "seasonal_comparison"
        assert ReportType.YIELD_FORECAST == "yield_forecast"
        print("✓ ReportType enum works")

        return True
    except Exception as e:
        print(f"✗ Enum test failed: {e}")
        return False


def test_exporter_initialization():
    """Test DataExporter initialization"""
    print("\nTesting DataExporter initialization...")

    try:
        from data_exporter import DataExporter

        # Basic initialization
        exporter = DataExporter()
        print("✓ Basic initialization successful")

        # Check attributes
        assert hasattr(exporter, 'CONTENT_TYPES')
        assert hasattr(exporter, 'ARABIC_HEADERS')
        print("✓ Required attributes present")

        # Check methods
        assert hasattr(exporter, 'export_field_data')
        assert hasattr(exporter, 'export_sensor_readings')
        assert hasattr(exporter, 'export_recommendations')
        assert hasattr(exporter, 'generate_report')
        print("✓ Required methods present")

        return True
    except Exception as e:
        print(f"✗ Initialization test failed: {e}")
        return False


def test_csv_export():
    """Test basic CSV export"""
    print("\nTesting CSV export...")

    try:
        from data_exporter import DataExporter, ExportFormat

        exporter = DataExporter()

        result = exporter.export_field_data(
            field_id="TEST_FIELD",
            format=ExportFormat.CSV,
            include_metadata=True,
            include_ndvi=False,
            include_sensors=False,
            include_weather=False,
            include_recommendations=False,
            include_actions=False
        )

        # Verify result
        assert result.format == ExportFormat.CSV
        assert result.filename.endswith('.csv')
        assert isinstance(result.data, str)
        assert result.size_bytes > 0
        assert result.generated_at is not None

        print("✓ CSV export successful")
        print(f"  Filename: {result.filename}")
        print(f"  Size: {result.size_bytes} bytes")

        return True
    except Exception as e:
        print(f"✗ CSV export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_json_export():
    """Test basic JSON export"""
    print("\nTesting JSON export...")

    try:
        import json

        from data_exporter import DataExporter, ExportFormat

        exporter = DataExporter()

        result = exporter.export_field_data(
            field_id="TEST_FIELD",
            format=ExportFormat.JSON,
            include_metadata=True,
            include_ndvi=True
        )

        # Verify result
        assert result.format == ExportFormat.JSON
        assert result.filename.endswith('.json')
        assert isinstance(result.data, str)

        # Verify JSON is valid
        data = json.loads(result.data)
        assert 'field_id' in data
        assert data['field_id'] == "TEST_FIELD"

        print("✓ JSON export successful")
        print(f"  Filename: {result.filename}")
        print("  Valid JSON: Yes")

        return True
    except Exception as e:
        print(f"✗ JSON export test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_convenience_functions():
    """Test convenience functions"""
    print("\nTesting convenience functions...")

    try:
        from data_exporter import export_field_csv

        result = export_field_csv("TEST_FIELD")

        assert result.format.value == "csv"
        assert result.filename.endswith('.csv')

        print("✓ Convenience function works")
        print(f"  Filename: {result.filename}")

        return True
    except Exception as e:
        print(f"✗ Convenience function test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_arabic_headers():
    """Test Arabic headers"""
    print("\nTesting Arabic headers...")

    try:
        from data_exporter import DataExporter

        exporter = DataExporter()

        # Check some Arabic headers
        assert 'field_id' in exporter.ARABIC_HEADERS
        assert exporter.ARABIC_HEADERS['field_id'] == "معرف الحقل"
        assert exporter.ARABIC_HEADERS['crop_type'] == "نوع المحصول"

        print("✓ Arabic headers configured")
        print(f"  Headers count: {len(exporter.ARABIC_HEADERS)}")

        return True
    except Exception as e:
        print(f"✗ Arabic headers test failed: {e}")
        return False


def test_report_template_import():
    """Test report template import"""
    print("\nTesting report template import...")

    try:
        from report_templates.daily_summary import DailySummaryReport

        print("✓ Report template imports successfully")
        return True
    except ImportError as e:
        print(f"✗ Report template import failed: {e}")
        return False


def check_dependencies():
    """Check optional dependencies"""
    print("\nChecking optional dependencies...")

    results = {}

    try:
        import openpyxl
        results['openpyxl'] = True
        print("✓ openpyxl installed (Excel support)")
    except ImportError:
        results['openpyxl'] = False
        print("✗ openpyxl not installed (Excel export unavailable)")

    try:
        import reportlab
        results['reportlab'] = True
        print("✓ reportlab installed (PDF support)")
    except ImportError:
        results['reportlab'] = False
        print("✗ reportlab not installed (PDF export unavailable)")

    try:
        import pandas
        results['pandas'] = True
        print("✓ pandas installed (Advanced data manipulation)")
    except ImportError:
        results['pandas'] = False
        print("✗ pandas not installed")

    return results


def run_all_tests():
    """Run all tests"""
    print("=" * 70)
    print("SAHOOL Data Export Service - Basic Tests")
    print("اختبار خدمة تصدير البيانات - اختبارات أساسية")
    print("=" * 70)

    results = []

    # Check dependencies first
    check_dependencies()

    # Run tests
    results.append(("Imports", test_imports()))
    results.append(("Enums", test_enums()))
    results.append(("Initialization", test_exporter_initialization()))
    results.append(("CSV Export", test_csv_export()))
    results.append(("JSON Export", test_json_export()))
    results.append(("Convenience Functions", test_convenience_functions()))
    results.append(("Arabic Headers", test_arabic_headers()))
    results.append(("Report Template Import", test_report_template_import()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print("\n" + "-" * 70)
    print(f"Total: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All tests passed successfully!")
    else:
        print(f"\n⚠ {total - passed} test(s) failed")

    print("=" * 70)

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
