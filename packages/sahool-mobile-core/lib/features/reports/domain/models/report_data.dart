/// Report Data Models - نماذج بيانات التقارير
/// Data structures for report content and results
library;

import 'report_template.dart';
import 'report_filter.dart';
import 'chart_config.dart';

/// Export format for reports - صيغ التصدير
enum ExportFormat {
  /// PDF document
  pdf,

  /// Excel spreadsheet
  excel,

  /// CSV file
  csv,

  /// PNG image
  image,
}

/// Report status - حالة التقرير
enum ReportStatus {
  /// Draft - not yet generated
  draft,

  /// Generating - in progress
  generating,

  /// Ready - completed successfully
  ready,

  /// Failed - generation error
  failed,
}

/// Report section model - قسم التقرير
class ReportSection {
  /// Section ID
  final String id;

  /// Section title (English)
  final String title;

  /// Section title (Arabic)
  final String titleAr;

  /// Section type (summary, chart, table, text)
  final String type;

  /// Section order
  final int order;

  /// Section data
  final Map<String, dynamic> data;

  /// Chart configuration (if chart type)
  final ChartConfig? chartConfig;

  /// Is section visible
  final bool isVisible;

  const ReportSection({
    required this.id,
    required this.title,
    required this.titleAr,
    required this.type,
    required this.order,
    this.data = const {},
    this.chartConfig,
    this.isVisible = true,
  });

  factory ReportSection.fromJson(Map<String, dynamic> json) {
    return ReportSection(
      id: json['id'] as String,
      title: json['title'] as String,
      titleAr: json['title_ar'] as String? ?? json['title'] as String,
      type: json['type'] as String,
      order: json['order'] as int? ?? 0,
      data: json['data'] as Map<String, dynamic>? ?? {},
      chartConfig: json['chart_config'] != null
          ? ChartConfig.fromJson(json['chart_config'] as Map<String, dynamic>)
          : null,
      isVisible: json['is_visible'] as bool? ?? true,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'title': title,
        'title_ar': titleAr,
        'type': type,
        'order': order,
        'data': data,
        'chart_config': chartConfig?.toJson(),
        'is_visible': isVisible,
      };

  ReportSection copyWith({
    String? id,
    String? title,
    String? titleAr,
    String? type,
    int? order,
    Map<String, dynamic>? data,
    ChartConfig? chartConfig,
    bool? isVisible,
  }) {
    return ReportSection(
      id: id ?? this.id,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      type: type ?? this.type,
      order: order ?? this.order,
      data: data ?? this.data,
      chartConfig: chartConfig ?? this.chartConfig,
      isVisible: isVisible ?? this.isVisible,
    );
  }
}

/// Summary statistic - إحصائية ملخصة
class SummaryStat {
  /// Stat label (English)
  final String label;

  /// Stat label (Arabic)
  final String labelAr;

  /// Stat value
  final String value;

  /// Unit (optional)
  final String? unit;

  /// Change percentage (optional)
  final double? changePercent;

  /// Is positive change
  final bool? isPositiveChange;

  /// Icon name
  final String? iconName;

  /// Color hex code
  final String? colorHex;

  const SummaryStat({
    required this.label,
    required this.labelAr,
    required this.value,
    this.unit,
    this.changePercent,
    this.isPositiveChange,
    this.iconName,
    this.colorHex,
  });

  factory SummaryStat.fromJson(Map<String, dynamic> json) {
    return SummaryStat(
      label: json['label'] as String,
      labelAr: json['label_ar'] as String? ?? json['label'] as String,
      value: json['value'].toString(),
      unit: json['unit'] as String?,
      changePercent: (json['change_percent'] as num?)?.toDouble(),
      isPositiveChange: json['is_positive_change'] as bool?,
      iconName: json['icon_name'] as String?,
      colorHex: json['color_hex'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'label': label,
        'label_ar': labelAr,
        'value': value,
        'unit': unit,
        'change_percent': changePercent,
        'is_positive_change': isPositiveChange,
        'icon_name': iconName,
        'color_hex': colorHex,
      };
}

/// Table data for reports - بيانات الجدول
class ReportTableData {
  /// Column headers (English)
  final List<String> headers;

  /// Column headers (Arabic)
  final List<String> headersAr;

  /// Table rows
  final List<List<String>> rows;

  /// Total row (optional)
  final List<String>? totals;

  /// Sortable columns
  final List<int> sortableColumns;

  const ReportTableData({
    required this.headers,
    required this.headersAr,
    required this.rows,
    this.totals,
    this.sortableColumns = const [],
  });

  factory ReportTableData.fromJson(Map<String, dynamic> json) {
    return ReportTableData(
      headers: (json['headers'] as List<dynamic>)
          .map((e) => e.toString())
          .toList(),
      headersAr: (json['headers_ar'] as List<dynamic>?)
              ?.map((e) => e.toString())
              .toList() ??
          (json['headers'] as List<dynamic>).map((e) => e.toString()).toList(),
      rows: (json['rows'] as List<dynamic>)
          .map((row) =>
              (row as List<dynamic>).map((cell) => cell.toString()).toList())
          .toList(),
      totals: (json['totals'] as List<dynamic>?)
          ?.map((e) => e.toString())
          .toList(),
      sortableColumns: (json['sortable_columns'] as List<dynamic>?)
              ?.map((e) => e as int)
              .toList() ??
          [],
    );
  }

  Map<String, dynamic> toJson() => {
        'headers': headers,
        'headers_ar': headersAr,
        'rows': rows,
        'totals': totals,
        'sortable_columns': sortableColumns,
      };
}

/// Report data model - نموذج بيانات التقرير
class ReportData {
  /// Report unique ID
  final String id;

  /// Report template used
  final ReportTemplate template;

  /// Report title
  final String title;

  /// Report title (Arabic)
  final String titleAr;

  /// Report subtitle/description
  final String? subtitle;

  /// Report subtitle (Arabic)
  final String? subtitleAr;

  /// Applied filters
  final ReportFilter filter;

  /// Report status
  final ReportStatus status;

  /// Generation timestamp
  final DateTime generatedAt;

  /// Report sections
  final List<ReportSection> sections;

  /// Summary statistics
  final List<SummaryStat> summaryStats;

  /// Error message (if failed)
  final String? errorMessage;

  /// File path (if exported)
  final String? exportedFilePath;

  /// Is report generated offline
  final bool isOffline;

  /// Tenant ID
  final String tenantId;

  /// User ID who generated the report
  final String? userId;

  const ReportData({
    required this.id,
    required this.template,
    required this.title,
    required this.titleAr,
    this.subtitle,
    this.subtitleAr,
    required this.filter,
    required this.status,
    required this.generatedAt,
    this.sections = const [],
    this.summaryStats = const [],
    this.errorMessage,
    this.exportedFilePath,
    this.isOffline = false,
    required this.tenantId,
    this.userId,
  });

  /// Is report ready for viewing
  bool get isReady => status == ReportStatus.ready;

  /// Is report generating
  bool get isGenerating => status == ReportStatus.generating;

  /// Has error
  bool get hasError => status == ReportStatus.failed;

  /// Get visible sections
  List<ReportSection> get visibleSections =>
      sections.where((s) => s.isVisible).toList()..sort((a, b) => a.order.compareTo(b.order));

  /// Get chart sections
  List<ReportSection> get chartSections =>
      visibleSections.where((s) => s.type == 'chart').toList();

  /// Get table sections
  List<ReportSection> get tableSections =>
      visibleSections.where((s) => s.type == 'table').toList();

  factory ReportData.fromJson(Map<String, dynamic> json) {
    return ReportData(
      id: json['id'] as String,
      template: ReportTemplate.fromJson(
          json['template'] as Map<String, dynamic>),
      title: json['title'] as String,
      titleAr: json['title_ar'] as String? ?? json['title'] as String,
      subtitle: json['subtitle'] as String?,
      subtitleAr: json['subtitle_ar'] as String?,
      filter: ReportFilter.fromJson(json['filter'] as Map<String, dynamic>),
      status: ReportStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => ReportStatus.draft,
      ),
      generatedAt: DateTime.parse(json['generated_at'] as String),
      sections: (json['sections'] as List<dynamic>?)
              ?.map((e) => ReportSection.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      summaryStats: (json['summary_stats'] as List<dynamic>?)
              ?.map((e) => SummaryStat.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      errorMessage: json['error_message'] as String?,
      exportedFilePath: json['exported_file_path'] as String?,
      isOffline: json['is_offline'] as bool? ?? false,
      tenantId: json['tenant_id'] as String,
      userId: json['user_id'] as String?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'template': template.toJson(),
        'title': title,
        'title_ar': titleAr,
        'subtitle': subtitle,
        'subtitle_ar': subtitleAr,
        'filter': filter.toJson(),
        'status': status.name,
        'generated_at': generatedAt.toIso8601String(),
        'sections': sections.map((s) => s.toJson()).toList(),
        'summary_stats': summaryStats.map((s) => s.toJson()).toList(),
        'error_message': errorMessage,
        'exported_file_path': exportedFilePath,
        'is_offline': isOffline,
        'tenant_id': tenantId,
        'user_id': userId,
      };

  ReportData copyWith({
    String? id,
    ReportTemplate? template,
    String? title,
    String? titleAr,
    String? subtitle,
    String? subtitleAr,
    ReportFilter? filter,
    ReportStatus? status,
    DateTime? generatedAt,
    List<ReportSection>? sections,
    List<SummaryStat>? summaryStats,
    String? errorMessage,
    String? exportedFilePath,
    bool? isOffline,
    String? tenantId,
    String? userId,
  }) {
    return ReportData(
      id: id ?? this.id,
      template: template ?? this.template,
      title: title ?? this.title,
      titleAr: titleAr ?? this.titleAr,
      subtitle: subtitle ?? this.subtitle,
      subtitleAr: subtitleAr ?? this.subtitleAr,
      filter: filter ?? this.filter,
      status: status ?? this.status,
      generatedAt: generatedAt ?? this.generatedAt,
      sections: sections ?? this.sections,
      summaryStats: summaryStats ?? this.summaryStats,
      errorMessage: errorMessage ?? this.errorMessage,
      exportedFilePath: exportedFilePath ?? this.exportedFilePath,
      isOffline: isOffline ?? this.isOffline,
      tenantId: tenantId ?? this.tenantId,
      userId: userId ?? this.userId,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is ReportData &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'ReportData($id: $title, status: $status)';
}

/// Generated report history entry - سجل التقارير المولدة
class ReportHistoryEntry {
  /// Entry ID
  final String id;

  /// Report ID
  final String reportId;

  /// Template type used
  final ReportType templateType;

  /// Report title
  final String title;

  /// Generation timestamp
  final DateTime generatedAt;

  /// Export format (if exported)
  final ExportFormat? exportFormat;

  /// File size in bytes (if exported)
  final int? fileSizeBytes;

  /// Was generated offline
  final bool isOffline;

  const ReportHistoryEntry({
    required this.id,
    required this.reportId,
    required this.templateType,
    required this.title,
    required this.generatedAt,
    this.exportFormat,
    this.fileSizeBytes,
    this.isOffline = false,
  });

  factory ReportHistoryEntry.fromJson(Map<String, dynamic> json) {
    return ReportHistoryEntry(
      id: json['id'] as String,
      reportId: json['report_id'] as String,
      templateType: ReportType.values.firstWhere(
        (e) => e.name == json['template_type'],
        orElse: () => ReportType.fieldPerformance,
      ),
      title: json['title'] as String,
      generatedAt: DateTime.parse(json['generated_at'] as String),
      exportFormat: json['export_format'] != null
          ? ExportFormat.values.firstWhere(
              (e) => e.name == json['export_format'],
              orElse: () => ExportFormat.pdf,
            )
          : null,
      fileSizeBytes: json['file_size_bytes'] as int?,
      isOffline: json['is_offline'] as bool? ?? false,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'report_id': reportId,
        'template_type': templateType.name,
        'title': title,
        'generated_at': generatedAt.toIso8601String(),
        'export_format': exportFormat?.name,
        'file_size_bytes': fileSizeBytes,
        'is_offline': isOffline,
      };
}
