/// Reports API - واجهة برمجة التقارير
/// Remote API client for reports service
library;

import 'dart:convert';
import 'package:http/http.dart' as http;
import '../../../core/config/api_config.dart';
import '../domain/models/report_template.dart';
import '../domain/models/report_data.dart';
import '../domain/models/report_filter.dart';

/// Exception for reports API errors
/// استثناء أخطاء واجهة التقارير
class ReportsApiException implements Exception {
  final String message;
  final String messageAr;
  final int? statusCode;

  ReportsApiException(this.message, {this.messageAr = '', this.statusCode});

  @override
  String toString() => 'ReportsApiException: $message';
}

/// Reports API client
/// عميل واجهة برمجة التقارير
class ReportsApi {
  final http.Client _client;
  final String? _authToken;
  final String? _tenantId;
  final String _baseUrl;

  ReportsApi({
    http.Client? client,
    String? authToken,
    String? tenantId,
    String? baseUrl,
  })  : _client = client ?? http.Client(),
        _authToken = authToken,
        _tenantId = tenantId,
        _baseUrl = baseUrl ?? ApiConfig.baseUrl;

  Map<String, String> get _headers => {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        if (_authToken != null) 'Authorization': 'Bearer $_authToken',
        if (_tenantId != null) 'X-Tenant-Id': _tenantId!,
      };

  // ═══════════════════════════════════════════════════════════════════════════
  // Template APIs
  // واجهات القوالب
  // ═══════════════════════════════════════════════════════════════════════════

  /// Fetch available report templates
  /// جلب قوالب التقارير المتاحة
  Future<List<ReportTemplate>> getTemplates() async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/api/v1/reports/templates'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as List;
        return data.map((e) => ReportTemplate.fromJson(e as Map<String, dynamic>)).toList();
      }

      // Fallback to predefined templates
      return ReportTemplates.all;
    } catch (e) {
      // Return predefined templates on error
      return ReportTemplates.all;
    }
  }

  /// Get template by ID
  /// جلب قالب بالمعرف
  Future<ReportTemplate?> getTemplate(String templateId) async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/api/v1/reports/templates/$templateId'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return ReportTemplate.fromJson(json.decode(response.body) as Map<String, dynamic>);
      }
      return ReportTemplates.getById(templateId);
    } catch (e) {
      return ReportTemplates.getById(templateId);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Report Generation APIs
  // واجهات توليد التقارير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate a new report
  /// توليد تقرير جديد
  Future<ReportData> generateReport({
    required String templateId,
    required ReportFilter filter,
    String? customTitle,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/api/v1/reports/generate'),
        headers: _headers,
        body: json.encode({
          'template_id': templateId,
          'filter': filter.toJson(),
          'custom_title': customTitle,
        }),
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return ReportData.fromJson(json.decode(response.body) as Map<String, dynamic>);
      }

      throw ReportsApiException(
        'Failed to generate report',
        messageAr: 'فشل في توليد التقرير',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is ReportsApiException) rethrow;
      throw ReportsApiException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get report by ID
  /// جلب تقرير بالمعرف
  Future<ReportData> getReport(String reportId) async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/api/v1/reports/$reportId'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return ReportData.fromJson(json.decode(response.body) as Map<String, dynamic>);
      }

      throw ReportsApiException(
        'Report not found',
        messageAr: 'التقرير غير موجود',
        statusCode: response.statusCode,
      );
    } catch (e) {
      if (e is ReportsApiException) rethrow;
      throw ReportsApiException(
        'Network error: ${e.toString()}',
        messageAr: 'خطأ في الشبكة',
      );
    }
  }

  /// Get report history
  /// جلب سجل التقارير
  Future<List<ReportHistoryEntry>> getReportHistory({
    int limit = 20,
    int offset = 0,
  }) async {
    try {
      final uri = Uri.parse('$_baseUrl/api/v1/reports/history').replace(
        queryParameters: {
          'limit': limit.toString(),
          'offset': offset.toString(),
        },
      );

      final response = await _client.get(uri, headers: _headers);

      if (response.statusCode == 200) {
        final data = json.decode(response.body) as List;
        return data.map((e) => ReportHistoryEntry.fromJson(e as Map<String, dynamic>)).toList();
      }

      return [];
    } catch (e) {
      return [];
    }
  }

  /// Delete report
  /// حذف تقرير
  Future<bool> deleteReport(String reportId) async {
    try {
      final response = await _client.delete(
        Uri.parse('$_baseUrl/api/v1/reports/$reportId'),
        headers: _headers,
      );

      return response.statusCode == 200 || response.statusCode == 204;
    } catch (e) {
      return false;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Data APIs for Report Generation
  // واجهات البيانات لتوليد التقارير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Fetch field performance data
  /// جلب بيانات أداء الحقل
  Future<Map<String, dynamic>> getFieldPerformanceData({
    required String fieldId,
    required DateRange dateRange,
  }) async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/api/v1/reports/data/field-performance').replace(
          queryParameters: {
            'field_id': fieldId,
            'start_date': dateRange.start.toIso8601String(),
            'end_date': dateRange.end.toIso8601String(),
          },
        ),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }

      return {};
    } catch (e) {
      return {};
    }
  }

  /// Fetch NDVI trend data
  /// جلب بيانات اتجاه NDVI
  Future<Map<String, dynamic>> getNdviTrendData({
    required String fieldId,
    required DateRange dateRange,
  }) async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/api/v1/reports/data/ndvi-trend').replace(
          queryParameters: {
            'field_id': fieldId,
            'start_date': dateRange.start.toIso8601String(),
            'end_date': dateRange.end.toIso8601String(),
          },
        ),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }

      return {};
    } catch (e) {
      return {};
    }
  }

  /// Fetch irrigation summary data
  /// جلب بيانات ملخص الري
  Future<Map<String, dynamic>> getIrrigationSummaryData({
    required List<String> fieldIds,
    required DateRange dateRange,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/api/v1/reports/data/irrigation-summary'),
        headers: _headers,
        body: json.encode({
          'field_ids': fieldIds,
          'start_date': dateRange.start.toIso8601String(),
          'end_date': dateRange.end.toIso8601String(),
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }

      return {};
    } catch (e) {
      return {};
    }
  }

  /// Fetch task completion data
  /// جلب بيانات إنجاز المهام
  Future<Map<String, dynamic>> getTaskCompletionData({
    required DateRange dateRange,
    List<String>? fieldIds,
    String? taskType,
    String? assigneeId,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/api/v1/reports/data/task-completion'),
        headers: _headers,
        body: json.encode({
          'start_date': dateRange.start.toIso8601String(),
          'end_date': dateRange.end.toIso8601String(),
          if (fieldIds != null && fieldIds.isNotEmpty) 'field_ids': fieldIds,
          if (taskType != null) 'task_type': taskType,
          if (assigneeId != null) 'assignee_id': assigneeId,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }

      return {};
    } catch (e) {
      return {};
    }
  }

  /// Fetch weather analysis data
  /// جلب بيانات تحليل الطقس
  Future<Map<String, dynamic>> getWeatherAnalysisData({
    required double latitude,
    required double longitude,
    required DateRange dateRange,
  }) async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/api/v1/reports/data/weather-analysis').replace(
          queryParameters: {
            'lat': latitude.toString(),
            'lng': longitude.toString(),
            'start_date': dateRange.start.toIso8601String(),
            'end_date': dateRange.end.toIso8601String(),
          },
        ),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }

      return {};
    } catch (e) {
      return {};
    }
  }

  /// Fetch cost/profit analysis data
  /// جلب بيانات تحليل التكاليف والأرباح
  Future<Map<String, dynamic>> getCostProfitData({
    required DateRange dateRange,
    List<String>? fieldIds,
    String? category,
  }) async {
    try {
      final response = await _client.post(
        Uri.parse('$_baseUrl/api/v1/reports/data/cost-profit'),
        headers: _headers,
        body: json.encode({
          'start_date': dateRange.start.toIso8601String(),
          'end_date': dateRange.end.toIso8601String(),
          if (fieldIds != null && fieldIds.isNotEmpty) 'field_ids': fieldIds,
          if (category != null) 'category': category,
        }),
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }

      return {};
    } catch (e) {
      return {};
    }
  }

  /// Fetch yield prediction data
  /// جلب بيانات توقع الإنتاج
  Future<Map<String, dynamic>> getYieldPredictionData({
    required String fieldId,
    String? cropType,
  }) async {
    try {
      final queryParams = {
        'field_id': fieldId,
        if (cropType != null) 'crop_type': cropType,
      };

      final response = await _client.get(
        Uri.parse('$_baseUrl/api/v1/reports/data/yield-prediction')
            .replace(queryParameters: queryParams),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }

      return {};
    } catch (e) {
      return {};
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Export APIs
  // واجهات التصدير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Export report to PDF (server-side)
  /// تصدير التقرير إلى PDF (من السيرفر)
  Future<List<int>?> exportToPdf(String reportId) async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/api/v1/reports/$reportId/export/pdf'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return response.bodyBytes;
      }

      return null;
    } catch (e) {
      return null;
    }
  }

  /// Export report to Excel (server-side)
  /// تصدير التقرير إلى Excel (من السيرفر)
  Future<List<int>?> exportToExcel(String reportId) async {
    try {
      final response = await _client.get(
        Uri.parse('$_baseUrl/api/v1/reports/$reportId/export/excel'),
        headers: _headers,
      );

      if (response.statusCode == 200) {
        return response.bodyBytes;
      }

      return null;
    } catch (e) {
      return null;
    }
  }

  /// Dispose the HTTP client
  void dispose() {
    _client.close();
  }
}
