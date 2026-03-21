/// SAHOOL Home Dashboard Providers
/// مزودات لوحة التحكم الرئيسية
///
/// Derives dashboard-level data from existing domain providers:
/// - Fields from fieldsRepoProvider
/// - Weather from weatherProvider
/// - Tasks from tasksProvider / pendingTasksProvider
/// - Alerts from alertsProvider

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/di/providers.dart';
import '../../../core/http/api_client.dart';
import '../../weather/presentation/providers/weather_provider.dart';
import '../../tasks/providers/tasks_provider.dart';
import '../../field/domain/entities/field.dart';

// =============================================================================
// Dashboard Fields Provider
// =============================================================================

/// All fields for current tenant (used by home dashboard)
final dashboardFieldsProvider = FutureProvider<List<Field>>((ref) async {
  final repo = ref.watch(fieldsRepoProvider);
  final apiClient = ref.watch(apiClientProvider);
  return repo.getAllFields(apiClient.tenantId);
});

/// Active fields count
final activeFieldsCountProvider = Provider<int>((ref) {
  final fieldsAsync = ref.watch(dashboardFieldsProvider);
  return fieldsAsync.when(
    data: (fields) => fields.where((f) => f.status == 'active' || f.status == null).length,
    loading: () => 0,
    error: (_, __) => 0,
  );
});

/// Total area in hectares
final totalAreaHectaresProvider = Provider<double>((ref) {
  final fieldsAsync = ref.watch(dashboardFieldsProvider);
  return fieldsAsync.when(
    data: (fields) => fields.fold(0.0, (sum, f) => sum + f.areaHectares),
    loading: () => 0.0,
    error: (_, __) => 0.0,
  );
});

/// Average NDVI across all fields
final averageNdviProvider = Provider<double?>((ref) {
  final fieldsAsync = ref.watch(dashboardFieldsProvider);
  return fieldsAsync.when(
    data: (fields) {
      final withNdvi = fields.where((f) => f.ndviCurrent != null).toList();
      if (withNdvi.isEmpty) return null;
      final sum = withNdvi.fold(0.0, (s, f) => s + f.ndviCurrent!);
      return sum / withNdvi.length;
    },
    loading: () => null,
    error: (_, __) => null,
  );
});

/// Average crop health percentage (derived from NDVI)
final cropHealthPercentProvider = Provider<int>((ref) {
  final ndvi = ref.watch(averageNdviProvider);
  if (ndvi == null) return 0;
  return (ndvi * 100).round().clamp(0, 100);
});

// =============================================================================
// Dashboard Tasks Provider
// =============================================================================

/// Today's due tasks count
final todayTasksCountProvider = Provider<int>((ref) {
  final pending = ref.watch(pendingTasksProvider);
  final now = DateTime.now();
  final todayEnd = DateTime(now.year, now.month, now.day, 23, 59, 59);
  return pending.where((t) => t.dueDate != null && t.dueDate!.isBefore(todayEnd)).length;
});

/// Total pending tasks count (for stats)
final pendingTasksCountProvider = Provider<int>((ref) {
  return ref.watch(pendingTasksProvider).length;
});

// =============================================================================
// Dashboard Alerts Provider
// =============================================================================

/// Active alerts count
final activeAlertsCountProvider = Provider<int>((ref) {
  final alertsState = ref.watch(alertsProvider);
  return alertsState.activeAlerts;
});

/// Whether there is at least one active alert
final hasActiveAlertProvider = Provider<bool>((ref) {
  final alertsState = ref.watch(alertsProvider);
  return alertsState.activeAlerts > 0;
});

/// First active alert (for banner display)
final primaryAlertProvider = Provider<({String title, String message})?>(
  (ref) {
    final alertsState = ref.watch(alertsProvider);
    final active = alertsState.alerts
        .where((a) => a.endTime.isAfter(DateTime.now()))
        .toList();
    if (active.isEmpty) return null;
    final first = active.first;
    return (title: 'تنبيه طقس', message: first.description);
  },
);

// =============================================================================
// Dashboard Weather Summary Provider
// =============================================================================

/// Weather summary string for compact display (e.g. "28°C مشمس")
final weatherSummaryProvider = Provider<String>((ref) {
  final weatherState = ref.watch(weatherProvider);
  if (weatherState.data == null) return '—';
  final current = weatherState.data!.current;
  return '${current.temperature.round()}°C ${current.conditionAr}';
});
