/// Report Builder Controller - متحكم بناء التقرير
/// State management for report building process
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../domain/models/report_template.dart';
import '../domain/models/report_data.dart';
import '../domain/models/report_filter.dart';
import '../data/reports_repository.dart';
import 'reports_providers.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Builder State
// حالة المنشئ
// ═══════════════════════════════════════════════════════════════════════════

/// Report builder state
class ReportBuilderState {
  final ReportTemplate? selectedTemplate;
  final ReportFilter filter;
  final String? customTitle;
  final bool isGenerating;
  final ReportData? generatedReport;
  final String? error;

  const ReportBuilderState({
    this.selectedTemplate,
    required this.filter,
    this.customTitle,
    this.isGenerating = false,
    this.generatedReport,
    this.error,
  });

  /// Initial state
  factory ReportBuilderState.initial() {
    return ReportBuilderState(
      filter: ReportFilter.defaults(),
    );
  }

  /// Copy with
  ReportBuilderState copyWith({
    ReportTemplate? selectedTemplate,
    ReportFilter? filter,
    String? customTitle,
    bool? isGenerating,
    ReportData? generatedReport,
    String? error,
  }) {
    return ReportBuilderState(
      selectedTemplate: selectedTemplate ?? this.selectedTemplate,
      filter: filter ?? this.filter,
      customTitle: customTitle ?? this.customTitle,
      isGenerating: isGenerating ?? this.isGenerating,
      generatedReport: generatedReport ?? this.generatedReport,
      error: error,
    );
  }

  /// Is valid for generation
  bool get isValid =>
      selectedTemplate != null && !isGenerating;

  /// Has error
  bool get hasError => error != null;

  /// Is complete
  bool get isComplete => generatedReport != null;
}

// ═══════════════════════════════════════════════════════════════════════════
// Builder Controller
// متحكم المنشئ
// ═══════════════════════════════════════════════════════════════════════════

/// Report builder controller provider
final reportBuilderControllerProvider =
    StateNotifierProvider<ReportBuilderController, ReportBuilderState>((ref) {
  final repository = ref.watch(reportsRepositoryProvider);
  return ReportBuilderController(repository: repository);
});

/// Report builder controller
class ReportBuilderController extends StateNotifier<ReportBuilderState> {
  final ReportsRepository _repository;

  ReportBuilderController({
    required ReportsRepository repository,
  })  : _repository = repository,
        super(ReportBuilderState.initial());

  // ─────────────────────────────────────────────────────────────────────────
  // Template Selection
  // اختيار القالب
  // ─────────────────────────────────────────────────────────────────────────

  /// Select a template
  void selectTemplate(ReportTemplate template) {
    state = state.copyWith(
      selectedTemplate: template,
      filter: state.filter.copyWith(
        dateRange: DateRangePreset.values
            .firstWhere(
              (p) => p.name == 'last${template.defaultDateRangeDays}Days',
              orElse: () => DateRangePreset.last30Days,
            )
            .toDateRange(),
      ),
      generatedReport: null,
      error: null,
    );
  }

  /// Clear template selection
  void clearTemplate() {
    state = state.copyWith(
      selectedTemplate: null,
      generatedReport: null,
      error: null,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Filter Configuration
  // تكوين الفلتر
  // ─────────────────────────────────────────────────────────────────────────

  /// Update filter
  void updateFilter(ReportFilter filter) {
    state = state.copyWith(
      filter: filter,
      generatedReport: null,
      error: null,
    );
  }

  /// Set date range preset
  void setDateRangePreset(DateRangePreset preset) {
    state = state.copyWith(
      filter: state.filter.copyWith(
        dateRangePreset: preset,
        dateRange: preset.toDateRange(),
      ),
      generatedReport: null,
      error: null,
    );
  }

  /// Set custom date range
  void setDateRange(DateRange dateRange) {
    state = state.copyWith(
      filter: state.filter.copyWith(
        dateRangePreset: DateRangePreset.custom,
        dateRange: dateRange,
      ),
      generatedReport: null,
      error: null,
    );
  }

  /// Set selected fields
  void setSelectedFields(List<String> fieldIds) {
    state = state.copyWith(
      filter: state.filter.copyWith(fieldIds: fieldIds),
      generatedReport: null,
      error: null,
    );
  }

  /// Set selected farms
  void setSelectedFarms(List<String> farmIds) {
    state = state.copyWith(
      filter: state.filter.copyWith(farmIds: farmIds),
      generatedReport: null,
      error: null,
    );
  }

  /// Set crop type filter
  void setCropType(String? cropType) {
    state = state.copyWith(
      filter: state.filter.copyWith(cropType: cropType),
      generatedReport: null,
      error: null,
    );
  }

  /// Set task type filter
  void setTaskType(String? taskType) {
    state = state.copyWith(
      filter: state.filter.copyWith(taskType: taskType),
      generatedReport: null,
      error: null,
    );
  }

  /// Set compare with previous period
  void setCompareWithPrevious(bool compare) {
    state = state.copyWith(
      filter: state.filter.copyWith(compareWithPrevious: compare),
      generatedReport: null,
      error: null,
    );
  }

  /// Set sort options
  void setSortOptions({String? sortBy, bool? ascending}) {
    state = state.copyWith(
      filter: state.filter.copyWith(
        sortBy: sortBy,
        sortAscending: ascending,
      ),
      generatedReport: null,
      error: null,
    );
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Title Configuration
  // تكوين العنوان
  // ─────────────────────────────────────────────────────────────────────────

  /// Set custom title
  void setCustomTitle(String? title) {
    state = state.copyWith(customTitle: title);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Report Generation
  // توليد التقرير
  // ─────────────────────────────────────────────────────────────────────────

  /// Generate report
  Future<ReportData?> generateReport({
    required String tenantId,
    String? userId,
  }) async {
    if (state.selectedTemplate == null) {
      state = state.copyWith(error: 'يرجى اختيار قالب التقرير');
      return null;
    }

    state = state.copyWith(
      isGenerating: true,
      error: null,
    );

    try {
      final report = await _repository.generateReport(
        template: state.selectedTemplate!,
        filter: state.filter,
        tenantId: tenantId,
        customTitle: state.customTitle,
        userId: userId,
      );

      state = state.copyWith(
        isGenerating: false,
        generatedReport: report,
      );

      return report;
    } catch (e) {
      state = state.copyWith(
        isGenerating: false,
        error: e.toString(),
      );
      return null;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Export
  // التصدير
  // ─────────────────────────────────────────────────────────────────────────

  /// Export to PDF
  Future<String?> exportToPdf() async {
    if (state.generatedReport == null) return null;

    try {
      return await _repository.exportToPdf(state.generatedReport!);
    } catch (e) {
      state = state.copyWith(error: 'فشل في تصدير PDF: $e');
      return null;
    }
  }

  /// Export to Excel
  Future<String?> exportToExcel() async {
    if (state.generatedReport == null) return null;

    try {
      return await _repository.exportToExcel(state.generatedReport!);
    } catch (e) {
      state = state.copyWith(error: 'فشل في تصدير Excel: $e');
      return null;
    }
  }

  /// Export to CSV
  Future<String?> exportToCsv() async {
    if (state.generatedReport == null) return null;

    try {
      return await _repository.exportToCsv(state.generatedReport!);
    } catch (e) {
      state = state.copyWith(error: 'فشل في تصدير CSV: $e');
      return null;
    }
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Reset
  // إعادة التعيين
  // ─────────────────────────────────────────────────────────────────────────

  /// Reset builder state
  void reset() {
    state = ReportBuilderState.initial();
  }

  /// Clear generated report
  void clearGeneratedReport() {
    state = state.copyWith(
      generatedReport: null,
      error: null,
    );
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(error: null);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Providers
// مزودات مساعدة
// ═══════════════════════════════════════════════════════════════════════════

/// Selected template provider
final selectedTemplateProvider = Provider<ReportTemplate?>((ref) {
  final builderState = ref.watch(reportBuilderControllerProvider);
  return builderState.selectedTemplate;
});

/// Builder filter provider
final builderFilterProvider = Provider<ReportFilter>((ref) {
  final builderState = ref.watch(reportBuilderControllerProvider);
  return builderState.filter;
});

/// Is generating provider
final isGeneratingProvider = Provider<bool>((ref) {
  final builderState = ref.watch(reportBuilderControllerProvider);
  return builderState.isGenerating;
});

/// Builder error provider
final builderErrorProvider = Provider<String?>((ref) {
  final builderState = ref.watch(reportBuilderControllerProvider);
  return builderState.error;
});

/// Generated report from builder provider
final builderGeneratedReportProvider = Provider<ReportData?>((ref) {
  final builderState = ref.watch(reportBuilderControllerProvider);
  return builderState.generatedReport;
});

/// Can generate report provider
final canGenerateReportProvider = Provider<bool>((ref) {
  final builderState = ref.watch(reportBuilderControllerProvider);
  return builderState.isValid;
});
