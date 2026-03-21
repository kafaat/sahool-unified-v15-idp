/// Reports Providers - مزودات التقارير
/// Riverpod providers for the reports feature
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:http/http.dart' as http;
import '../../../core/auth/auth_service.dart';
import '../../../core/sync/network_status.dart';
import '../domain/models/report_template.dart';
import '../domain/models/report_data.dart';
import '../domain/models/report_filter.dart';
import '../data/reports_api.dart';
import '../data/reports_repository.dart';
import '../data/report_generator.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Core Providers
// المزودات الأساسية
// ═══════════════════════════════════════════════════════════════════════════

/// Network status provider (stub - should be overridden)
final networkStatusProvider = Provider<NetworkStatus>((ref) {
  // This should be overridden with actual network status
  return NetworkStatus();
});

/// Reports API provider
final reportsApiProvider = Provider<ReportsApi>((ref) {
  final authState = ref.watch(authStateProvider);
  return ReportsApi(
    client: http.Client(),
    authToken: authState.accessToken,
    tenantId: authState.user?.tenantId,
  );
});

/// Report generator provider
final reportGeneratorProvider = Provider<ReportGenerator>((ref) {
  return ReportGenerator();
});

/// Reports repository provider
final reportsRepositoryProvider = Provider<ReportsRepository>((ref) {
  final api = ref.watch(reportsApiProvider);
  final generator = ref.watch(reportGeneratorProvider);
  final networkStatus = ref.watch(networkStatusProvider);

  return ReportsRepository(
    api: api,
    generator: generator,
    networkStatus: networkStatus,
  );
});

// ═══════════════════════════════════════════════════════════════════════════
// Template Providers
// مزودات القوالب
// ═══════════════════════════════════════════════════════════════════════════

/// All report templates provider
final reportTemplatesProvider = FutureProvider<List<ReportTemplate>>((ref) async {
  final repository = ref.watch(reportsRepositoryProvider);
  return repository.getTemplates();
});

/// Template by ID provider
final templateByIdProvider =
    FutureProvider.family<ReportTemplate?, String>((ref, id) async {
  final repository = ref.watch(reportsRepositoryProvider);
  return repository.getTemplate(id);
});

/// Template by type provider
final templateByTypeProvider =
    Provider.family<ReportTemplate, ReportType>((ref, type) {
  final repository = ref.read(reportsRepositoryProvider);
  return repository.getTemplateByType(type);
});

/// Free templates only provider
final freeTemplatesProvider = FutureProvider<List<ReportTemplate>>((ref) async {
  final templates = await ref.watch(reportTemplatesProvider.future);
  return templates.where((t) => !t.isPremium).toList();
});

/// Premium templates provider
final premiumTemplatesProvider = FutureProvider<List<ReportTemplate>>((ref) async {
  final templates = await ref.watch(reportTemplatesProvider.future);
  return templates.where((t) => t.isPremium).toList();
});

// ═══════════════════════════════════════════════════════════════════════════
// Report Providers
// مزودات التقارير
// ═══════════════════════════════════════════════════════════════════════════

/// Report by ID provider
final reportByIdProvider =
    FutureProvider.family<ReportData?, String>((ref, id) async {
  final repository = ref.watch(reportsRepositoryProvider);
  return repository.getReport(id);
});

/// Report history provider
final reportHistoryProvider = FutureProvider<List<ReportHistoryEntry>>((ref) async {
  final repository = ref.watch(reportsRepositoryProvider);
  return repository.getReportHistory();
});

/// Paginated report history provider
final paginatedReportHistoryProvider = FutureProvider.family<
    List<ReportHistoryEntry>,
    ({int limit, int offset})>((ref, params) async {
  final repository = ref.watch(reportsRepositoryProvider);
  return repository.getReportHistory(
    limit: params.limit,
    offset: params.offset,
  );
});

/// Cached reports provider
final cachedReportsProvider = Provider<List<ReportData>>((ref) {
  final repository = ref.watch(reportsRepositoryProvider);
  return repository.getCachedReports();
});

// ═══════════════════════════════════════════════════════════════════════════
// Filter Providers
// مزودات الفلاتر
// ═══════════════════════════════════════════════════════════════════════════

/// Current filter state provider
final currentFilterProvider = StateProvider<ReportFilter>((ref) {
  return ReportFilter.defaults();
});

/// Selected fields provider
final selectedFieldsProvider = StateProvider<List<String>>((ref) {
  return [];
});

/// Selected farms provider
final selectedFarmsProvider = StateProvider<List<String>>((ref) {
  return [];
});

/// Date range preset provider
final dateRangePresetProvider = StateProvider<DateRangePreset>((ref) {
  return DateRangePreset.last30Days;
});

/// Date range provider
final dateRangeProvider = StateProvider<DateRange>((ref) {
  return DateRangePreset.last30Days.toDateRange();
});

// ═══════════════════════════════════════════════════════════════════════════
// Generation State Providers
// مزودات حالة التوليد
// ═══════════════════════════════════════════════════════════════════════════

/// Report generation state
enum ReportGenerationState {
  idle,
  generating,
  completed,
  failed,
}

/// Report generation state provider
final reportGenerationStateProvider =
    StateProvider<ReportGenerationState>((ref) {
  return ReportGenerationState.idle;
});

/// Generated report provider
final generatedReportProvider = StateProvider<ReportData?>((ref) {
  return null;
});

/// Generation error provider
final generationErrorProvider = StateProvider<String?>((ref) {
  return null;
});

// ═══════════════════════════════════════════════════════════════════════════
// Export State Providers
// مزودات حالة التصدير
// ═══════════════════════════════════════════════════════════════════════════

/// Export state
enum ExportState {
  idle,
  exporting,
  completed,
  failed,
}

/// Export state provider
final exportStateProvider = StateProvider<ExportState>((ref) {
  return ExportState.idle;
});

/// Exported file path provider
final exportedFilePathProvider = StateProvider<String?>((ref) {
  return null;
});

/// Export error provider
final exportErrorProvider = StateProvider<String?>((ref) {
  return null;
});

// ═══════════════════════════════════════════════════════════════════════════
// Utility Providers
// مزودات المرافق
// ═══════════════════════════════════════════════════════════════════════════

/// Is online provider
final isOnlineProvider = Provider<bool>((ref) {
  final networkStatus = ref.watch(networkStatusProvider);
  return networkStatus.isOnline;
});

/// Report count provider
final reportCountProvider = Provider<int>((ref) {
  final history = ref.watch(reportHistoryProvider).valueOrNull;
  return history?.length ?? 0;
});

/// Recent reports provider (last 5)
final recentReportsProvider = FutureProvider<List<ReportHistoryEntry>>((ref) async {
  final history = await ref.watch(reportHistoryProvider.future);
  return history.take(5).toList();
});
