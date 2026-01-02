# SAHOOL Data Export Service

## خدمة تصدير البيانات

A comprehensive data export and reporting service for SAHOOL agricultural platform, supporting multiple export formats and bilingual (Arabic/English) reports.

خدمة شاملة لتصدير البيانات وإنشاء التقارير لمنصة صحول الزراعية، مع دعم صيغ تصدير متعددة وتقارير ثنائية اللغة (عربي/إنجليزي).

---

## Features / الميزات

### Export Formats / صيغ التصدير

- **CSV** - مع عناوين عربية (With Arabic headers)
- **Excel (XLSX)** - أوراق متعددة (Multiple sheets)
- **JSON** - بيانات منظمة (Structured data)
- **GeoJSON** - بيانات مكانية (Spatial data)
- **PDF** - تقارير منسقة (Formatted reports)

### Report Types / أنواع التقارير

1. **Daily Summary** - تقرير يومي شامل
2. **Weekly Analysis** - تحليل أسبوعي
3. **Monthly Report** - تقرير شهري
4. **Seasonal Comparison** - مقارنة المواسم
5. **Yield Forecast** - توقعات الإنتاج

### Data Included / البيانات المضمنة

- **Field Metadata** - معلومات الحقل (name, area, crop, soil type)
- **NDVI History** - سجل NDVI التاريخي
- **Sensor Readings** - قراءات المستشعرات
- **Weather Data** - بيانات الطقس
- **Recommendations** - التوصيات المستلمة
- **Actions Taken** - الإجراءات المتخذة

---

## Installation / التثبيت

### Requirements / المتطلبات

```bash
pip install pydantic>=2.0.0
pip install python-dateutil>=2.8.0
pip install openpyxl>=3.1.0      # For Excel export
pip install reportlab>=4.0.0     # For PDF generation
pip install pandas>=2.0.0        # For advanced data manipulation
```

Or install all at once:

```bash
pip install -r requirements.txt
```

---

## Quick Start / البدء السريع

### Basic CSV Export

```python
from data_exporter import export_field_csv
from datetime import date, timedelta

# Export last 30 days of field data
end_date = date.today()
start_date = end_date - timedelta(days=30)

result = export_field_csv("FIELD_001", date_range=(start_date, end_date))

# Save to file
with open(result.filename, "w", encoding="utf-8") as f:
    f.write(result.data)

print(f"Exported to: {result.filename}")
```

### Excel Export with Multiple Sheets

```python
from data_exporter import export_field_excel

result = export_field_excel("FIELD_001")

# Save to file
with open(result.filename, "wb") as f:
    f.write(result.data)
```

### Generate Daily Report

```python
from data_exporter import generate_daily_report

result = generate_daily_report("FIELD_001")

# Save PDF
with open(result.filename, "wb") as f:
    f.write(result.data)
```

---

## Detailed Usage / الاستخدام التفصيلي

### 1. Initialize DataExporter

```python
from data_exporter import DataExporter, ExportFormat, ReportType

# Basic initialization
exporter = DataExporter()

# With Arabic font for PDF (optional)
exporter = DataExporter(arabic_font_path="/path/to/arabic.ttf")
```

### 2. Export Field Data

```python
from datetime import date, timedelta

# Define date range
end_date = date.today()
start_date = end_date - timedelta(days=30)

# Export comprehensive field data
result = exporter.export_field_data(
    field_id="FIELD_001",
    format=ExportFormat.CSV,  # or EXCEL, JSON, GEOJSON, PDF
    date_range=(start_date, end_date),
    include_metadata=True,
    include_ndvi=True,
    include_sensors=True,
    include_weather=True,
    include_recommendations=True,
    include_actions=True
)

# Access result
print(f"Filename: {result.filename}")
print(f"Size: {result.size_bytes} bytes")
print(f"Format: {result.format}")
print(f"Generated: {result.generated_at}")

# Save to file
if isinstance(result.data, str):
    with open(result.filename, "w", encoding="utf-8") as f:
        f.write(result.data)
else:
    with open(result.filename, "wb") as f:
        f.write(result.data)
```

### 3. Export Sensor Readings Only

```python
result = exporter.export_sensor_readings(
    field_id="FIELD_001",
    format=ExportFormat.EXCEL,
    date_range=(start_date, end_date)
)
```

### 4. Export Recommendations Only

```python
result = exporter.export_recommendations(
    field_id="FIELD_001",
    format=ExportFormat.PDF,
    date_range=(start_date, end_date)
)
```

### 5. Generate Reports

#### Daily Summary Report

```python
result = exporter.generate_report(
    report_type=ReportType.DAILY_SUMMARY,
    params={
        "field_id": "FIELD_001",
        "date": date.today()
    }
)
```

#### Weekly Analysis Report

```python
result = exporter.generate_report(
    report_type=ReportType.WEEKLY_ANALYSIS,
    params={
        "field_id": "FIELD_001",
        "end_date": date.today()
    }
)
```

#### Monthly Report

```python
result = exporter.generate_report(
    report_type=ReportType.MONTHLY_REPORT,
    params={
        "field_id": "FIELD_001",
        "month": 10,
        "year": 2024
    }
)
```

#### Seasonal Comparison

```python
result = exporter.generate_report(
    report_type=ReportType.SEASONAL_COMPARISON,
    params={
        "field_id": "FIELD_001",
        "seasons": ["2023-winter", "2024-spring", "2024-summer"]
    }
)
```

#### Yield Forecast

```python
result = exporter.generate_report(
    report_type=ReportType.YIELD_FORECAST,
    params={
        "field_id": "FIELD_001"
    }
)
```

---

## Export Format Details / تفاصيل صيغ التصدير

### CSV Format

- **Encoding**: UTF-8 with BOM (for Excel compatibility)
- **Headers**: Bilingual (Arabic/English)
- **Separator**: Comma (,)
- **Suitable for**: Data analysis, spreadsheet import

**Example CSV output:**

```csv
معرف الحقل,التاريخ,متوسط NDVI,الحرارة,الرطوبة
FIELD_001,2024-01-01,0.65,28.5,45.0
FIELD_001,2024-01-02,0.67,29.0,43.5
```

### Excel Format

- **Multiple sheets**: Each data type on separate sheet
- **Formatted headers**: Colored headers with bold text
- **Auto-sized columns**: Optimized for readability
- **Suitable for**: Professional reports, presentations

**Sheet structure:**
1. معلومات الحقل (Field Info)
2. NDVI History
3. قراءات المستشعرات (Sensors)
4. بيانات الطقس (Weather)
5. التوصيات (Recommendations)
6. الإجراءات (Actions)

### JSON Format

- **Structured data**: Hierarchical organization
- **UTF-8 encoding**: Full Unicode support
- **Pretty printed**: Indented for readability
- **Suitable for**: API integration, data processing

**Example JSON structure:**

```json
{
  "field_id": "FIELD_001",
  "export_date": "2024-01-15T10:30:00",
  "metadata": {
    "name": "حقل القمح الشمالي",
    "area_hectares": 5.0,
    "crop_type": "قمح"
  },
  "ndvi_history": [
    {
      "date": "2024-01-01",
      "mean": 0.65,
      "min": 0.45,
      "max": 0.85
    }
  ]
}
```

### GeoJSON Format

- **Spatial data**: Geographic coordinates
- **Feature-based**: Single Feature or FeatureCollection
- **Standards compliant**: RFC 7946
- **Suitable for**: GIS applications, mapping

**Example GeoJSON:**

```json
{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [44.1910, 15.3694]
  },
  "properties": {
    "field_id": "FIELD_001",
    "ndvi_mean": 0.65,
    "crop_type": "قمح"
  }
}
```

### PDF Format

- **Bilingual reports**: Arabic and English
- **Professional layout**: Tables, charts, formatting
- **SAHOOL branding**: Header and footer
- **Suitable for**: Official reports, stakeholders

**PDF Report sections:**
- Executive summary with status indicators
- Field information table
- NDVI analysis and trends
- Sensor readings
- Weather data and forecast
- Recommendations
- Actions taken

---

## Report Templates / قوالب التقارير

### Daily Summary Report Template

Located at: `report_templates/daily_summary.py`

**Features:**
- Executive summary with status indicators (good/warning/critical)
- Field metadata table
- NDVI analysis with interpretation
- Weekly NDVI trend
- Sensor readings table
- Weather conditions and 3-day forecast
- Recommendations with priority levels
- Actions taken
- Bilingual headers and content

**Customization:**

```python
from report_templates.daily_summary import DailySummaryReport

# Create custom report instance
report = DailySummaryReport(exporter)

# Generate report
result = report.generate(field_id="FIELD_001", report_date=date.today())
```

---

## Arabic Text Support / دعم النصوص العربية

### CSV with Arabic Headers

All CSV exports include Arabic headers by default:

```python
exporter.ARABIC_HEADERS = {
    "field_id": "معرف الحقل",
    "field_name": "اسم الحقل",
    "date": "التاريخ",
    "crop_type": "نوع المحصول",
    # ... more headers
}
```

### Custom Arabic Headers

Add your own custom Arabic headers:

```python
exporter.ARABIC_HEADERS.update({
    "custom_field": "حقل مخصص",
    "new_metric": "مؤشر جديد"
})
```

### PDF with Arabic Font

To use Arabic fonts in PDF reports, provide the font path:

```python
exporter = DataExporter(arabic_font_path="/usr/share/fonts/truetype/DejaVuSans.ttf")
```

Recommended Arabic fonts:
- DejaVu Sans
- Arial Unicode MS
- Amiri
- Noto Sans Arabic

---

## Integration Examples / أمثلة التكامل

### FastAPI Endpoint

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from data_exporter import DataExporter, ExportFormat
import io

app = FastAPI()

@app.get("/api/fields/{field_id}/export")
async def export_field_data(
    field_id: str,
    format: str = "csv",
    days: int = 30
):
    exporter = DataExporter()

    export_format = ExportFormat(format.lower())
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    result = exporter.export_field_data(
        field_id=field_id,
        format=export_format,
        date_range=(start_date, end_date)
    )

    if isinstance(result.data, str):
        content = io.BytesIO(result.data.encode("utf-8"))
    else:
        content = io.BytesIO(result.data)

    return StreamingResponse(
        content,
        media_type=result.content_type,
        headers={
            "Content-Disposition": f"attachment; filename={result.filename}"
        }
    )
```

### Django View

```python
from django.http import HttpResponse
from data_exporter import DataExporter, ReportType
from datetime import date

def generate_daily_report_view(request, field_id):
    exporter = DataExporter()

    result = exporter.generate_report(
        report_type=ReportType.DAILY_SUMMARY,
        params={
            "field_id": field_id,
            "date": date.today()
        }
    )

    response = HttpResponse(result.data, content_type=result.content_type)
    response['Content-Disposition'] = f'attachment; filename="{result.filename}"'

    return response
```

### Scheduled Reports with Celery

```python
from celery import Celery
from data_exporter import DataExporter, ReportType
from datetime import date

app = Celery('sahool')

@app.task
def generate_daily_reports():
    """Generate daily reports for all active fields"""
    exporter = DataExporter()

    for field_id in get_active_field_ids():
        result = exporter.generate_report(
            report_type=ReportType.DAILY_SUMMARY,
            params={
                "field_id": field_id,
                "date": date.today()
            }
        )

        # Save to storage
        save_report_to_storage(result)

        # Send to farmer via email
        send_report_email(field_id, result)
```

---

## Testing / الاختبار

Run the example file to test all functionality:

```bash
cd /home/user/sahool-unified-v15-idp/apps/kernel/field_ops/services
python example_data_export.py
```

This will:
- Generate sample exports in all formats
- Create all report types
- Save files to `/tmp/`
- Display detailed output for each operation

---

## Performance Considerations / اعتبارات الأداء

### Large Datasets

For large datasets (>10,000 records):

1. **Use pagination** when fetching data
2. **Stream data** instead of loading all in memory
3. **Use CSV** for fastest export
4. **Excel**: Limit to reasonable number of rows (<100,000)

### Memory Usage

- **CSV**: Low memory footprint
- **JSON**: Moderate memory usage
- **Excel**: Higher memory for large datasets
- **PDF**: Highest memory for complex reports

### Optimization Tips

```python
# For large exports, fetch data in chunks
def export_large_dataset(field_id, format):
    exporter = DataExporter()

    # Only include necessary data
    result = exporter.export_field_data(
        field_id=field_id,
        format=format,
        include_metadata=False,  # Skip if not needed
        include_ndvi=True,
        include_sensors=False,   # Skip if not needed
        include_weather=False,
        include_recommendations=False,
        include_actions=False
    )

    return result
```

---

## Error Handling / معالجة الأخطاء

### Common Errors

```python
try:
    result = exporter.export_field_data(
        field_id="FIELD_001",
        format=ExportFormat.PDF
    )
except ValueError as e:
    # Invalid format or parameters
    print(f"Invalid input: {e}")
except RuntimeError as e:
    # Missing dependencies (reportlab, openpyxl)
    print(f"Missing dependency: {e}")
except Exception as e:
    # Other errors
    print(f"Export failed: {e}")
```

### Validation

```python
from data_exporter import ExportFormat, ReportType

# Validate format
try:
    format = ExportFormat("invalid")
except ValueError:
    print("Invalid format")

# Check dependencies
import data_exporter
if not data_exporter.REPORTLAB_AVAILABLE:
    print("PDF export not available - install reportlab")
if not data_exporter.OPENPYXL_AVAILABLE:
    print("Excel export not available - install openpyxl")
```

---

## API Reference / مرجع API

### DataExporter Class

#### Methods

- **export_field_data**(field_id, format, date_range, **options) → ExportResult
- **export_sensor_readings**(field_id, format, date_range) → ExportResult
- **export_recommendations**(field_id, format, date_range) → ExportResult
- **generate_report**(report_type, params) → ExportResult

#### Properties

- **CONTENT_TYPES**: Dict[ExportFormat, str]
- **ARABIC_HEADERS**: Dict[str, str]

### ExportResult Class

#### Attributes

- **format**: ExportFormat
- **filename**: str
- **content_type**: str
- **data**: Union[str, bytes]
- **size_bytes**: int
- **generated_at**: datetime
- **metadata**: Dict[str, Any]

### Enums

- **ExportFormat**: CSV, EXCEL, JSON, GEOJSON, PDF
- **ReportType**: DAILY_SUMMARY, WEEKLY_ANALYSIS, MONTHLY_REPORT, SEASONAL_COMPARISON, YIELD_FORECAST

---

## Future Enhancements / التحسينات المستقبلية

- [ ] Add KML export format
- [ ] Support for multiple fields in single export
- [ ] Interactive PDF reports with charts
- [ ] Email integration for automated reports
- [ ] Cloud storage integration (S3, GCS)
- [ ] Real-time streaming exports
- [ ] Custom report templates
- [ ] Data compression for large exports
- [ ] Export scheduling and automation
- [ ] Multi-language support (beyond Arabic/English)

---

## Support / الدعم

For questions or issues:
- Check the example file: `example_data_export.py`
- Review the code documentation
- Contact SAHOOL development team

---

## License / الترخيص

Copyright © 2024 SAHOOL Agricultural Platform
All rights reserved.

---

## Changelog / سجل التغييرات

### Version 1.0.0 (2024-01-15)
- Initial release
- Support for CSV, Excel, JSON, GeoJSON, PDF formats
- 5 report types
- Bilingual Arabic/English support
- Comprehensive field data export
- Report templates framework
