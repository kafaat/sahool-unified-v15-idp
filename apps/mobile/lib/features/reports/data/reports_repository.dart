/// Reports Repository - مستودع التقارير
/// Data layer for managing reports with offline support
library;

import 'dart:convert';
import 'package:uuid/uuid.dart';
import '../../../core/sync/network_status.dart';
import '../domain/models/report_template.dart';
import '../domain/models/report_data.dart';
import '../domain/models/report_filter.dart';
import '../domain/models/chart_config.dart';
import 'reports_api.dart';
import 'report_generator.dart';

/// Reports repository with offline-first support
/// مستودع التقارير مع دعم العمل بدون اتصال
class ReportsRepository {
  final ReportsApi _api;
  final ReportGenerator _generator;
  final NetworkStatus _networkStatus;

  // Cache for offline support
  final List<ReportTemplate> _cachedTemplates = [];
  final Map<String, ReportData> _cachedReports = {};
  final List<ReportHistoryEntry> _cachedHistory = [];

  ReportsRepository({
    required ReportsApi api,
    required ReportGenerator generator,
    required NetworkStatus networkStatus,
  })  : _api = api,
        _generator = generator,
        _networkStatus = networkStatus;

  // ═══════════════════════════════════════════════════════════════════════════
  // Templates
  // القوالب
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get all available report templates
  /// جلب جميع قوالب التقارير المتاحة
  Future<List<ReportTemplate>> getTemplates({bool forceRefresh = false}) async {
    // Return cached if available and not forcing refresh
    if (_cachedTemplates.isNotEmpty && !forceRefresh) {
      return _cachedTemplates;
    }

    if (await _networkStatus.isConnected) {
      try {
        final templates = await _api.getTemplates();
        _cachedTemplates.clear();
        _cachedTemplates.addAll(templates);
        return templates;
      } catch (_) {
        // Fall through to predefined
      }
    }

    // Return predefined templates
    final templates = ReportTemplates.all;
    _cachedTemplates.clear();
    _cachedTemplates.addAll(templates);
    return templates;
  }

  /// Get template by ID
  /// جلب قالب بالمعرف
  Future<ReportTemplate?> getTemplate(String templateId) async {
    // Check cache first
    final cached = _cachedTemplates
        .where((t) => t.id == templateId)
        .firstOrNull;
    if (cached != null) return cached;

    if (await _networkStatus.isConnected) {
      final template = await _api.getTemplate(templateId);
      if (template != null) {
        _cachedTemplates.add(template);
        return template;
      }
    }

    return ReportTemplates.getById(templateId);
  }

  /// Get template by type
  /// جلب قالب بالنوع
  ReportTemplate getTemplateByType(ReportType type) {
    return ReportTemplates.getByType(type);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Report Generation
  // توليد التقارير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Generate a report
  /// توليد تقرير
  Future<ReportData> generateReport({
    required ReportTemplate template,
    required ReportFilter filter,
    required String tenantId,
    String? customTitle,
    String? userId,
  }) async {
    final reportId = const Uuid().v4();
    final now = DateTime.now();

    // Determine title
    final title = customTitle ?? template.name;
    final titleAr = customTitle ?? template.nameAr;

    // Try online generation first
    if (await _networkStatus.isConnected && !(await _shouldGenerateOffline(template, filter))) {
      try {
        final report = await _api.generateReport(
          templateId: template.id,
          filter: filter,
          customTitle: customTitle,
        );

        _cachedReports[report.id] = report;
        _addToHistory(report);
        return report;
      } catch (_) {
        // Fall through to offline generation
      }
    }

    // Generate offline
    final report = await _generateOfflineReport(
      reportId: reportId,
      template: template,
      filter: filter,
      tenantId: tenantId,
      title: title,
      titleAr: titleAr,
      userId: userId,
    );

    _cachedReports[report.id] = report;
    _addToHistory(report);
    return report;
  }

  /// Check if should generate offline
  Future<bool> _shouldGenerateOffline(ReportTemplate template, ReportFilter filter) async {
    // Always generate offline if template supports it and we're offline
    if (!(await _networkStatus.isConnected) && template.supportsOffline) {
      return true;
    }
    return false;
  }

  /// Generate report offline
  Future<ReportData> _generateOfflineReport({
    required String reportId,
    required ReportTemplate template,
    required ReportFilter filter,
    required String tenantId,
    required String title,
    required String titleAr,
    String? userId,
  }) async {
    // Use local generator
    final sections = await _generator.generateSections(
      template: template,
      filter: filter,
    );

    final summaryStats = await _generator.generateSummaryStats(
      template: template,
      filter: filter,
    );

    return ReportData(
      id: reportId,
      template: template,
      title: title,
      titleAr: titleAr,
      subtitle: filter.dateRange.formatted,
      subtitleAr: filter.dateRange.formattedAr,
      filter: filter,
      status: ReportStatus.ready,
      generatedAt: DateTime.now(),
      sections: sections,
      summaryStats: summaryStats,
      isOffline: true,
      tenantId: tenantId,
      userId: userId,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Report Access
  // الوصول للتقارير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get report by ID
  /// جلب تقرير بالمعرف
  Future<ReportData?> getReport(String reportId) async {
    // Check cache first
    if (_cachedReports.containsKey(reportId)) {
      return _cachedReports[reportId];
    }

    if (await _networkStatus.isConnected) {
      try {
        final report = await _api.getReport(reportId);
        _cachedReports[reportId] = report;
        return report;
      } catch (_) {
        return null;
      }
    }

    return null;
  }

  /// Get cached reports
  /// جلب التقارير المخزنة مؤقتاً
  List<ReportData> getCachedReports() {
    return _cachedReports.values.toList()
      ..sort((a, b) => b.generatedAt.compareTo(a.generatedAt));
  }

  /// Get report history
  /// جلب سجل التقارير
  Future<List<ReportHistoryEntry>> getReportHistory({
    int limit = 20,
    int offset = 0,
    bool forceRefresh = false,
  }) async {
    if (_cachedHistory.isNotEmpty && !forceRefresh) {
      final start = offset;
      final end = (offset + limit).clamp(0, _cachedHistory.length);
      return _cachedHistory.sublist(start, end);
    }

    if (await _networkStatus.isConnected) {
      try {
        final history = await _api.getReportHistory(
          limit: limit,
          offset: offset,
        );
        if (offset == 0) {
          _cachedHistory.clear();
        }
        _cachedHistory.addAll(history);
        return history;
      } catch (_) {
        // Fall through
      }
    }

    // Return locally generated history
    return _generateLocalHistory(limit, offset);
  }

  /// Add report to history
  void _addToHistory(ReportData report) {
    final entry = ReportHistoryEntry(
      id: const Uuid().v4(),
      reportId: report.id,
      templateType: report.template.type,
      title: report.title,
      generatedAt: report.generatedAt,
      isOffline: report.isOffline,
    );

    _cachedHistory.insert(0, entry);

    // Limit history size
    if (_cachedHistory.length > 100) {
      _cachedHistory.removeRange(100, _cachedHistory.length);
    }
  }

  /// Generate local history from cached reports
  List<ReportHistoryEntry> _generateLocalHistory(int limit, int offset) {
    return getCachedReports()
        .skip(offset)
        .take(limit)
        .map((r) => ReportHistoryEntry(
              id: r.id,
              reportId: r.id,
              templateType: r.template.type,
              title: r.title,
              generatedAt: r.generatedAt,
              isOffline: r.isOffline,
            ))
        .toList();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Report Management
  // إدارة التقارير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Delete report
  /// حذف تقرير
  Future<bool> deleteReport(String reportId) async {
    // Remove from cache
    _cachedReports.remove(reportId);
    _cachedHistory.removeWhere((e) => e.reportId == reportId);

    if (await _networkStatus.isConnected) {
      return await _api.deleteReport(reportId);
    }

    return true;
  }

  /// Clear all cached reports
  /// مسح جميع التقارير المخزنة
  void clearCache() {
    _cachedReports.clear();
    _cachedHistory.clear();
    _cachedTemplates.clear();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Export
  // التصدير
  // ═══════════════════════════════════════════════════════════════════════════

  /// Export report to PDF
  /// تصدير التقرير إلى PDF
  Future<String?> exportToPdf(
    ReportData report, {
    bool includeArabic = true,
  }) async {
    // Try server-side export first
    if (await _networkStatus.isConnected) {
      final bytes = await _api.exportToPdf(report.id);
      if (bytes != null) {
        return await _generator.saveExportedFile(
          bytes,
          '${report.title}_${_formatDateForFile(report.generatedAt)}.pdf',
        );
      }
    }

    // Use local generator
    return await _generator.generatePdf(
      report,
      includeArabic: includeArabic,
    );
  }

  /// Export report to Excel
  /// تصدير التقرير إلى Excel
  Future<String?> exportToExcel(ReportData report) async {
    // Try server-side export first
    if (await _networkStatus.isConnected) {
      final bytes = await _api.exportToExcel(report.id);
      if (bytes != null) {
        return await _generator.saveExportedFile(
          bytes,
          '${report.title}_${_formatDateForFile(report.generatedAt)}.xlsx',
        );
      }
    }

    // Use local generator
    return await _generator.generateExcel(report);
  }

  /// Export report to CSV
  /// تصدير التقرير إلى CSV
  Future<String?> exportToCsv(ReportData report) async {
    return await _generator.generateCsv(report);
  }

  /// Format date for file name
  String _formatDateForFile(DateTime date) {
    return '${date.year}${date.month.toString().padLeft(2, '0')}${date.day.toString().padLeft(2, '0')}';
  }

  /// Dispose resources
  void dispose() {
    _api.dispose();
  }
}
