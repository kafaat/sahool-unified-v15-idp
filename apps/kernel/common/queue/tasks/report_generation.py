"""
SAHOOL Report Generation Handler
معالج إنشاء التقارير

Handles background generation of field reports.
يعالج إنشاء تقارير الحقول في الخلفية.

Author: SAHOOL Platform Team
License: MIT
"""

import logging
import os
import time
import uuid
from datetime import date, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Import the DataExporter from field_ops services
try:
    import sys

    # Add kernel path for imports (apps/kernel/ to import from field_ops.services)
    kernel_path = Path(__file__).parent.parent.parent.parent
    if str(kernel_path) not in sys.path:
        sys.path.insert(0, str(kernel_path))

    from kernel.field_ops.services.data_exporter import (
        DataExporter,
        ExportFormat,
        ExportResult,
        ReportType,
    )

    DATA_EXPORTER_AVAILABLE = True
except ImportError:
    # Try alternative import path (when running from apps/ directory)
    try:
        from field_ops.services.data_exporter import (
            DataExporter,
            ExportFormat,
            ExportResult,
            ReportType,
        )

        DATA_EXPORTER_AVAILABLE = True
    except ImportError:
        DATA_EXPORTER_AVAILABLE = False
        logger.warning("DataExporter not available, report generation will use fallback")


def handle_report_generation(payload: dict[str, Any]) -> dict[str, Any]:
    """
    إنشاء تقرير الحقل
    Generate field report

    Args:
        payload: {
            "field_id": str - معرف الحقل / Field ID
            "user_id": str - معرف المستخدم / User ID
            "report_type": str - نوع التقرير / Report type (daily, weekly, monthly, custom)
            "start_date": str - تاريخ البداية / Start date
            "end_date": str - تاريخ النهاية / End date
            "include_sections": List[str] - الأقسام المطلوبة / Required sections
            "format": str - التنسيق / Format (pdf, excel, html)
            "language": str - اللغة / Language (ar, en)
        }

    Returns:
        {
            "report_url": str - رابط التقرير / Report URL
            "report_id": str - معرف التقرير / Report ID
            "metadata": dict - البيانات الوصفية / Metadata
            "generation_time": float - وقت الإنشاء / Generation time
        }
    """
    logger.info(f"Generating report for field: {payload.get('field_id')}")

    try:
        # استخراج البيانات من الحمولة
        # Extract data from payload
        field_id = payload.get("field_id")
        user_id = payload.get("user_id")
        report_type = payload.get("report_type", "daily")
        report_format = payload.get("format", "pdf")
        language = payload.get("language", "ar")

        if not field_id or not user_id:
            raise ValueError("field_id and user_id are required")

        # Parse optional date parameters
        # تحليل معلمات التاريخ الاختيارية
        start_date_str = payload.get("start_date")
        end_date_str = payload.get("end_date")
        include_sections = payload.get("include_sections", [])

        date_range = None
        if start_date_str and end_date_str:
            date_range = (
                date.fromisoformat(start_date_str),
                date.fromisoformat(end_date_str),
            )

        # Start timing for generation performance tracking
        # بدء توقيت الأداء لتتبع إنشاء التقارير
        start_time = time.time()

        # Generate unique report ID
        # إنشاء معرف تقرير فريد
        report_id = f"RPT-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}"

        # Generate report using DataExporter if available
        # إنشاء التقرير باستخدام DataExporter إذا كان متاحاً
        if DATA_EXPORTER_AVAILABLE:
            export_result = _generate_report_with_exporter(
                field_id=field_id,
                report_type=report_type,
                report_format=report_format,
                language=language,
                date_range=date_range,
                include_sections=include_sections,
            )
        else:
            # Fallback to basic report generation
            # العودة إلى إنشاء التقارير الأساسي
            export_result = _generate_basic_report(
                field_id=field_id,
                report_type=report_type,
                report_format=report_format,
                language=language,
            )

        # Calculate generation time
        # حساب وقت الإنشاء
        generation_time = time.time() - start_time

        # Simulate saving to storage (S3)
        # محاكاة الحفظ في التخزين (S3)
        storage_path = _save_report_to_storage(
            report_data=export_result.get("data"),
            report_id=report_id,
            field_id=field_id,
            report_format=report_format,
        )

        # Compile final result with all metadata
        # تجميع النتيجة النهائية مع جميع البيانات الوصفية
        result = {
            "report_url": storage_path,
            "report_id": report_id,
            "metadata": {
                "field_id": field_id,
                "user_id": user_id,
                "report_type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "language": language,
                "format": report_format,
                "filename": export_result.get("filename", f"{report_id}.{report_format}"),
                "page_count": export_result.get("page_count", 1),
                "file_size_bytes": export_result.get("size_bytes", 0),
                "sections_included": export_result.get("sections_included", include_sections),
                "data_sources": [
                    "satellite_imagery",
                    "iot_sensors",
                    "weather_api",
                    "manual_observations",
                ],
                "bilingual": language in ["ar", "en", "both"],
            },
            "summary_stats": export_result.get("summary_stats", {}),
            "generation_time": round(generation_time, 2),
            "status": "success",
        }

        logger.info(
            f"Report generated successfully: {report_id} "
            f"(field={field_id}, type={report_type}, format={report_format}, "
            f"size={result['metadata']['file_size_bytes']} bytes, time={generation_time:.2f}s)"
        )
        return result

    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        raise


def _generate_report_with_exporter(
    field_id: str,
    report_type: str,
    report_format: str,
    language: str,
    date_range: tuple[date, date] | None,
    include_sections: list[str],
) -> dict[str, Any]:
    """
    إنشاء تقرير باستخدام DataExporter
    Generate report using DataExporter

    Args:
        field_id: معرف الحقل / Field ID
        report_type: نوع التقرير / Report type (daily, weekly, monthly, custom)
        report_format: التنسيق / Format (pdf, excel)
        language: اللغة / Language (ar, en)
        date_range: نطاق التاريخ / Date range
        include_sections: الأقسام المطلوبة / Required sections

    Returns:
        Dict containing report data, filename, size, and metadata
    """
    # Initialize exporter with Arabic font support if available
    # تهيئة المصدر مع دعم الخط العربي إذا كان متاحاً
    arabic_font_path = os.environ.get("SAHOOL_ARABIC_FONT_PATH")
    exporter = DataExporter(arabic_font_path=arabic_font_path)

    # Map format string to ExportFormat enum
    # تعيين سلسلة التنسيق إلى تعداد ExportFormat
    format_map = {
        "pdf": ExportFormat.PDF,
        "excel": ExportFormat.EXCEL,
        "xlsx": ExportFormat.EXCEL,
        "csv": ExportFormat.CSV,
        "json": ExportFormat.JSON,
    }
    export_format = format_map.get(report_format.lower(), ExportFormat.PDF)

    # Map report type string to ReportType enum
    # تعيين سلسلة نوع التقرير إلى تعداد ReportType
    report_type_map = {
        "daily": ReportType.DAILY_SUMMARY,
        "daily_summary": ReportType.DAILY_SUMMARY,
        "weekly": ReportType.WEEKLY_ANALYSIS,
        "weekly_analysis": ReportType.WEEKLY_ANALYSIS,
        "monthly": ReportType.MONTHLY_REPORT,
        "monthly_report": ReportType.MONTHLY_REPORT,
        "seasonal": ReportType.SEASONAL_COMPARISON,
        "seasonal_comparison": ReportType.SEASONAL_COMPARISON,
        "yield": ReportType.YIELD_FORECAST,
        "yield_forecast": ReportType.YIELD_FORECAST,
    }

    result_data: dict[str, Any] = {
        "data": None,
        "filename": "",
        "size_bytes": 0,
        "page_count": 1,
        "sections_included": [],
        "summary_stats": {},
    }

    try:
        # Generate report based on type
        # إنشاء التقرير بناءً على النوع
        if report_type.lower() in report_type_map:
            # Use predefined report type
            # استخدام نوع التقرير المحدد مسبقاً
            report_type_enum = report_type_map[report_type.lower()]
            params = {
                "field_id": field_id,
                "date": date_range[1] if date_range else date.today(),
                "end_date": date_range[1] if date_range else date.today(),
            }
            if date_range:
                params["month"] = date_range[1].month
                params["year"] = date_range[1].year

            export_result: ExportResult = exporter.generate_report(report_type_enum, params)

            result_data["data"] = export_result.data
            result_data["filename"] = export_result.filename
            result_data["size_bytes"] = export_result.size_bytes
            result_data["sections_included"] = _get_sections_for_report_type(report_type)

        else:
            # Custom field data export
            # تصدير بيانات الحقل المخصص
            export_result = exporter.export_field_data(
                field_id=field_id,
                format=export_format,
                date_range=date_range,
                include_metadata=True,
                include_ndvi=True,
                include_sensors=True,
                include_weather=True,
                include_recommendations=True,
                include_actions=True,
            )

            result_data["data"] = export_result.data
            result_data["filename"] = export_result.filename
            result_data["size_bytes"] = export_result.size_bytes
            result_data["sections_included"] = [
                "field_metadata",
                "ndvi_history",
                "sensor_readings",
                "weather_data",
                "recommendations",
                "actions",
            ]

        # Estimate page count for PDF reports
        # تقدير عدد الصفحات لتقارير PDF
        if export_format == ExportFormat.PDF:
            # Rough estimate: ~3KB per page for PDF
            result_data["page_count"] = max(1, result_data["size_bytes"] // 3000)

        # Generate summary statistics based on field data
        # إنشاء إحصائيات ملخصة بناءً على بيانات الحقل
        result_data["summary_stats"] = _calculate_summary_stats(exporter, field_id, date_range)

    except Exception as e:
        logger.error(f"Error generating report with DataExporter: {e}", exc_info=True)
        # Re-raise to trigger fallback
        raise

    return result_data


def _generate_basic_report(
    field_id: str,
    report_type: str,
    report_format: str,
    language: str,
) -> dict[str, Any]:
    """
    إنشاء تقرير أساسي (احتياطي)
    Generate basic report (fallback)

    Generates a simple report when DataExporter is not available.
    يُنشئ تقريراً بسيطاً عندما لا يكون DataExporter متاحاً.
    """
    import json

    # Create bilingual content based on language preference
    # إنشاء محتوى ثنائي اللغة بناءً على تفضيل اللغة
    if language == "ar":
        title = f"تقرير الحقل - {field_id}"
        generated_text = "تم الإنشاء"
        field_label = "معرف الحقل"
        type_label = "نوع التقرير"
    else:
        title = f"Field Report - {field_id}"
        generated_text = "Generated"
        field_label = "Field ID"
        type_label = "Report Type"

    report_content = {
        "title": title,
        "generated_at": datetime.utcnow().isoformat(),
        "field_id": field_id,
        "report_type": report_type,
        "language": language,
        "content": {
            field_label: field_id,
            type_label: report_type,
            generated_text: datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        },
        "sections": [
            {
                "name": "Executive Summary" if language == "en" else "الملخص التنفيذي",
                "content": "Report generated successfully." if language == "en" else "تم إنشاء التقرير بنجاح.",
            },
            {
                "name": "Field Overview" if language == "en" else "نظرة عامة على الحقل",
                "content": f"Field {field_id} data summary." if language == "en" else f"ملخص بيانات الحقل {field_id}.",
            },
        ],
    }

    # Convert to requested format
    # تحويل إلى التنسيق المطلوب
    if report_format.lower() in ["json"]:
        data = json.dumps(report_content, ensure_ascii=False, indent=2)
        filename = f"report_{field_id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
    else:
        # For PDF/Excel without libraries, return JSON as fallback
        # لـ PDF/Excel بدون مكتبات، يُرجع JSON كاحتياطي
        data = json.dumps(report_content, ensure_ascii=False, indent=2)
        filename = f"report_{field_id}_{datetime.utcnow().strftime('%Y%m%d')}.json"
        logger.warning(f"Format {report_format} requires additional libraries, falling back to JSON")

    return {
        "data": data,
        "filename": filename,
        "size_bytes": len(data.encode("utf-8")) if isinstance(data, str) else len(data),
        "page_count": 1,
        "sections_included": ["executive_summary", "field_overview"],
        "summary_stats": {
            "field_health_score": 0.0,
            "average_ndvi": 0.0,
            "data_available": False,
        },
    }


def _save_report_to_storage(
    report_data: bytes | str | None,
    report_id: str,
    field_id: str,
    report_format: str,
) -> str:
    """
    حفظ التقرير في التخزين
    Save report to storage

    In production, this would upload to S3/MinIO.
    For now, returns a simulated S3 URL.

    في الإنتاج، سيتم الرفع إلى S3/MinIO.
    حالياً، يُرجع عنوان URL محاكى لـ S3.
    """
    # Get storage bucket from environment or use default
    # الحصول على حاوية التخزين من البيئة أو استخدام الافتراضي
    storage_bucket = os.environ.get("SAHOOL_REPORTS_BUCKET", "sahool-reports")
    os.environ.get("SAHOOL_AWS_REGION", "me-south-1")

    # Generate storage path with date-based partitioning
    # إنشاء مسار التخزين مع التقسيم على أساس التاريخ
    date_partition = datetime.utcnow().strftime("%Y/%m/%d")
    file_extension = _get_file_extension(report_format)
    storage_key = f"reports/{field_id}/{date_partition}/{report_id}.{file_extension}"

    # Simulated S3 URL (in production, use boto3 to upload)
    # عنوان URL محاكى لـ S3 (في الإنتاج، استخدم boto3 للرفع)
    storage_url = f"s3://{storage_bucket}/{storage_key}"

    # Log storage details
    logger.debug(
        f"Report storage: bucket={storage_bucket}, key={storage_key}, "
        f"size={len(report_data) if report_data else 0} bytes"
    )

    # In production environment, actually upload the file
    # في بيئة الإنتاج، يتم رفع الملف فعلياً
    if os.environ.get("SAHOOL_ENABLE_S3_UPLOAD") == "true" and report_data:
        try:
            _upload_to_s3(
                bucket=storage_bucket,
                key=storage_key,
                data=report_data,
                content_type=_get_content_type(report_format),
            )
            logger.info(f"Report uploaded to S3: {storage_url}")
        except Exception as e:
            logger.error(f"Failed to upload report to S3: {e}")
            # Return URL anyway, upload can be retried
            # إرجاع عنوان URL على أي حال، يمكن إعادة محاولة الرفع

    return storage_url


def _upload_to_s3(
    bucket: str,
    key: str,
    data: bytes | str,
    content_type: str,
) -> None:
    """
    رفع الملف إلى S3
    Upload file to S3

    Requires boto3 and proper AWS credentials.
    يتطلب boto3 وبيانات اعتماد AWS صحيحة.
    """
    try:
        import boto3

        s3_client = boto3.client("s3")

        # Convert string to bytes if needed
        if isinstance(data, str):
            data = data.encode("utf-8")

        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
            Metadata={
                "generator": "sahool-report-service",
                "generated_at": datetime.utcnow().isoformat(),
            },
        )
    except ImportError:
        logger.warning("boto3 not available, skipping S3 upload")
        raise
    except Exception as e:
        logger.error(f"S3 upload error: {e}")
        raise


def _calculate_summary_stats(
    exporter: "DataExporter",
    field_id: str,
    date_range: tuple[date, date] | None,
) -> dict[str, Any]:
    """
    حساب الإحصائيات الملخصة
    Calculate summary statistics for the report
    """
    try:
        # Get field data for statistics
        # الحصول على بيانات الحقل للإحصائيات
        metadata = exporter._get_field_metadata(field_id)
        ndvi_history = exporter._get_ndvi_history(field_id, date_range)
        weather_data = exporter._get_weather_data(field_id, date_range)
        recommendations = exporter._get_recommendations(field_id, date_range)

        # Calculate NDVI statistics
        # حساب إحصائيات NDVI
        if ndvi_history:
            ndvi_values = [r.get("mean", 0) for r in ndvi_history if r.get("mean")]
            avg_ndvi = sum(ndvi_values) / len(ndvi_values) if ndvi_values else 0.0
            min_ndvi = min(ndvi_values) if ndvi_values else 0.0
            max_ndvi = max(ndvi_values) if ndvi_values else 0.0
        else:
            avg_ndvi = min_ndvi = max_ndvi = 0.0

        # Calculate weather averages
        # حساب متوسطات الطقس
        if weather_data:
            avg_temp = sum(w.get("temp_max", 0) for w in weather_data) / len(weather_data)
            total_rainfall = sum(w.get("rainfall", 0) for w in weather_data)
        else:
            avg_temp = total_rainfall = 0.0

        # Calculate field health score (weighted average)
        # حساب درجة صحة الحقل (متوسط مرجح)
        health_score = min(10.0, (avg_ndvi * 10) + 2.0)  # Base health on NDVI

        return {
            "field_health_score": round(health_score, 1),
            "average_ndvi": round(avg_ndvi, 3),
            "min_ndvi": round(min_ndvi, 3),
            "max_ndvi": round(max_ndvi, 3),
            "ndvi_data_points": len(ndvi_history) if ndvi_history else 0,
            "average_temperature_c": round(avg_temp, 1),
            "total_rainfall_mm": round(total_rainfall, 1),
            "recommendations_count": len(recommendations) if recommendations else 0,
            "field_area_hectares": metadata.get("area_hectares", 0),
            "crop_type": metadata.get("crop_type_en", "unknown"),
        }

    except Exception as e:
        logger.warning(f"Error calculating summary stats: {e}")
        return {
            "field_health_score": 0.0,
            "average_ndvi": 0.0,
            "error": str(e),
        }


def _get_sections_for_report_type(report_type: str) -> list[str]:
    """
    الحصول على الأقسام لنوع التقرير
    Get sections included for a given report type
    """
    sections_map = {
        "daily": [
            "executive_summary",
            "field_overview",
            "ndvi_today",
            "sensor_readings",
            "weather_summary",
            "recommendations",
            "actions_taken",
        ],
        "weekly": [
            "executive_summary",
            "field_overview",
            "ndvi_trend",
            "weather_analysis",
            "recommendations_summary",
            "actions_summary",
        ],
        "monthly": [
            "executive_summary",
            "field_overview",
            "ndvi_monthly_analysis",
            "weather_monthly",
            "irrigation_summary",
            "cost_analysis",
            "recommendations",
        ],
        "seasonal": [
            "season_comparison",
            "ndvi_trends",
            "yield_comparison",
            "cost_benefit_analysis",
        ],
        "yield": [
            "yield_forecast",
            "confidence_analysis",
            "contributing_factors",
            "recommendations",
        ],
    }

    # Normalize report type
    normalized_type = report_type.lower().split("_")[0]
    return sections_map.get(normalized_type, ["executive_summary", "field_overview"])


def _get_file_extension(report_format: str) -> str:
    """Get file extension for report format"""
    extension_map = {
        "pdf": "pdf",
        "excel": "xlsx",
        "xlsx": "xlsx",
        "csv": "csv",
        "json": "json",
        "geojson": "geojson",
        "html": "html",
    }
    return extension_map.get(report_format.lower(), "pdf")


def _get_content_type(report_format: str) -> str:
    """Get MIME content type for report format"""
    content_type_map = {
        "pdf": "application/pdf",
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "csv": "text/csv; charset=utf-8",
        "json": "application/json; charset=utf-8",
        "geojson": "application/geo+json; charset=utf-8",
        "html": "text/html; charset=utf-8",
    }
    return content_type_map.get(report_format.lower(), "application/octet-stream")
