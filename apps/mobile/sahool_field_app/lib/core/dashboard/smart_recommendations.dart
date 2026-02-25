import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_logger.dart';

/// SAHOOL Smart Dashboard Recommendations
/// توصيات لوحة القيادة الذكية
///
/// Provides personalized, proactive recommendations:
/// - Field-specific alerts (irrigation, pest, weather)
/// - Task prioritization based on urgency
/// - Seasonal crop stage guidance
/// - IoT sensor anomaly notifications

// ═══════════════════════════════════════════════════════════════════════════
// Recommendation Models
// ═══════════════════════════════════════════════════════════════════════════

/// Priority level for recommendations
enum RecommendationPriority {
  /// Critical - immediate action needed (< 6 hours)
  critical,

  /// High - action within 24 hours
  high,

  /// Medium - action within 1 week
  medium,

  /// Low - informational / for awareness
  low,
}

/// Extension for RecommendationPriority
extension RecommendationPriorityExtension on RecommendationPriority {
  String get labelAr {
    switch (this) {
      case RecommendationPriority.critical:
        return 'حرج';
      case RecommendationPriority.high:
        return 'مرتفع';
      case RecommendationPriority.medium:
        return 'متوسط';
      case RecommendationPriority.low:
        return 'منخفض';
    }
  }

  String get labelEn {
    switch (this) {
      case RecommendationPriority.critical:
        return 'Critical';
      case RecommendationPriority.high:
        return 'High';
      case RecommendationPriority.medium:
        return 'Medium';
      case RecommendationPriority.low:
        return 'Low';
    }
  }

  /// Sort weight (higher = more urgent)
  int get sortWeight {
    switch (this) {
      case RecommendationPriority.critical:
        return 100;
      case RecommendationPriority.high:
        return 75;
      case RecommendationPriority.medium:
        return 50;
      case RecommendationPriority.low:
        return 25;
    }
  }
}

/// Category of the recommendation
enum RecommendationCategory {
  irrigation,
  pest,
  disease,
  weather,
  harvest,
  fertilizer,
  equipment,
  task,
  general,
}

/// Extension for RecommendationCategory
extension RecommendationCategoryExtension on RecommendationCategory {
  String get labelAr {
    switch (this) {
      case RecommendationCategory.irrigation:
        return 'الري';
      case RecommendationCategory.pest:
        return 'الآفات';
      case RecommendationCategory.disease:
        return 'الأمراض';
      case RecommendationCategory.weather:
        return 'الطقس';
      case RecommendationCategory.harvest:
        return 'الحصاد';
      case RecommendationCategory.fertilizer:
        return 'التسميد';
      case RecommendationCategory.equipment:
        return 'المعدات';
      case RecommendationCategory.task:
        return 'المهام';
      case RecommendationCategory.general:
        return 'عام';
    }
  }

  String get labelEn {
    switch (this) {
      case RecommendationCategory.irrigation:
        return 'Irrigation';
      case RecommendationCategory.pest:
        return 'Pest';
      case RecommendationCategory.disease:
        return 'Disease';
      case RecommendationCategory.weather:
        return 'Weather';
      case RecommendationCategory.harvest:
        return 'Harvest';
      case RecommendationCategory.fertilizer:
        return 'Fertilizer';
      case RecommendationCategory.equipment:
        return 'Equipment';
      case RecommendationCategory.task:
        return 'Task';
      case RecommendationCategory.general:
        return 'General';
    }
  }

  /// Icon name for the category
  String get iconName {
    switch (this) {
      case RecommendationCategory.irrigation:
        return 'water_drop';
      case RecommendationCategory.pest:
        return 'bug_report';
      case RecommendationCategory.disease:
        return 'healing';
      case RecommendationCategory.weather:
        return 'cloud';
      case RecommendationCategory.harvest:
        return 'agriculture';
      case RecommendationCategory.fertilizer:
        return 'science';
      case RecommendationCategory.equipment:
        return 'build';
      case RecommendationCategory.task:
        return 'task_alt';
      case RecommendationCategory.general:
        return 'info';
    }
  }
}

/// A single smart recommendation
@immutable
class SmartRecommendation {
  final String id;
  final String titleAr;
  final String titleEn;
  final String descriptionAr;
  final String descriptionEn;
  final RecommendationPriority priority;
  final RecommendationCategory category;
  final DateTime createdAt;
  final DateTime? expiresAt;
  final String? fieldId;
  final String? actionRoute;
  final Map<String, dynamic> metadata;
  final bool isDismissed;

  const SmartRecommendation({
    required this.id,
    required this.titleAr,
    required this.titleEn,
    required this.descriptionAr,
    required this.descriptionEn,
    required this.priority,
    required this.category,
    required this.createdAt,
    this.expiresAt,
    this.fieldId,
    this.actionRoute,
    this.metadata = const {},
    this.isDismissed = false,
  });

  /// Whether the recommendation has expired
  bool get isExpired {
    if (expiresAt == null) return false;
    return DateTime.now().isAfter(expiresAt!);
  }

  /// Whether this is field-specific
  bool get isFieldSpecific => fieldId != null;

  /// Whether this has an associated action
  bool get hasAction => actionRoute != null;

  SmartRecommendation copyWith({
    bool? isDismissed,
  }) {
    return SmartRecommendation(
      id: id,
      titleAr: titleAr,
      titleEn: titleEn,
      descriptionAr: descriptionAr,
      descriptionEn: descriptionEn,
      priority: priority,
      category: category,
      createdAt: createdAt,
      expiresAt: expiresAt,
      fieldId: fieldId,
      actionRoute: actionRoute,
      metadata: metadata,
      isDismissed: isDismissed ?? this.isDismissed,
    );
  }

  @override
  String toString() =>
      'SmartRecommendation($id: ${priority.labelEn} ${category.labelEn})';
}

// ═══════════════════════════════════════════════════════════════════════════
// Dashboard Statistics
// ═══════════════════════════════════════════════════════════════════════════

/// Real-time dashboard statistics
@immutable
class DashboardStats {
  /// Total number of fields
  final int totalFields;

  /// Fields needing attention
  final int fieldsNeedingAttention;

  /// Average NDVI across all fields
  final double? averageNdvi;

  /// Pending tasks count
  final int pendingTasks;

  /// Overdue tasks count
  final int overdueTasks;

  /// Total area in hectares
  final double totalAreaHectares;

  /// Active IoT sensors count
  final int activeSensors;

  /// Offline sensors count
  final int offlineSensors;

  /// Today's weather summary
  final String? weatherSummaryAr;
  final String? weatherSummaryEn;

  /// Water usage today (cubic meters)
  final double? waterUsageToday;

  /// Last sync timestamp
  final DateTime? lastSyncAt;

  const DashboardStats({
    this.totalFields = 0,
    this.fieldsNeedingAttention = 0,
    this.averageNdvi,
    this.pendingTasks = 0,
    this.overdueTasks = 0,
    this.totalAreaHectares = 0,
    this.activeSensors = 0,
    this.offlineSensors = 0,
    this.weatherSummaryAr,
    this.weatherSummaryEn,
    this.waterUsageToday,
    this.lastSyncAt,
  });

  /// Field health percentage (fields OK / total)
  double get fieldHealthPercent {
    if (totalFields == 0) return 100;
    return ((totalFields - fieldsNeedingAttention) / totalFields) * 100;
  }

  /// Sensor health percentage
  double get sensorHealthPercent {
    final total = activeSensors + offlineSensors;
    if (total == 0) return 100;
    return (activeSensors / total) * 100;
  }

  /// Task completion summary
  String get taskSummaryAr {
    if (overdueTasks > 0) return '$overdueTasks مهمة متأخرة';
    if (pendingTasks > 0) return '$pendingTasks مهمة معلقة';
    return 'لا مهام معلقة';
  }

  String get taskSummaryEn {
    if (overdueTasks > 0) return '$overdueTasks overdue tasks';
    if (pendingTasks > 0) return '$pendingTasks pending tasks';
    return 'No pending tasks';
  }

  /// Sync freshness check
  bool get isSyncFresh {
    if (lastSyncAt == null) return false;
    return DateTime.now().difference(lastSyncAt!).inMinutes < 30;
  }

  DashboardStats copyWith({
    int? totalFields,
    int? fieldsNeedingAttention,
    double? averageNdvi,
    int? pendingTasks,
    int? overdueTasks,
    double? totalAreaHectares,
    int? activeSensors,
    int? offlineSensors,
    String? weatherSummaryAr,
    String? weatherSummaryEn,
    double? waterUsageToday,
    DateTime? lastSyncAt,
  }) {
    return DashboardStats(
      totalFields: totalFields ?? this.totalFields,
      fieldsNeedingAttention:
          fieldsNeedingAttention ?? this.fieldsNeedingAttention,
      averageNdvi: averageNdvi ?? this.averageNdvi,
      pendingTasks: pendingTasks ?? this.pendingTasks,
      overdueTasks: overdueTasks ?? this.overdueTasks,
      totalAreaHectares: totalAreaHectares ?? this.totalAreaHectares,
      activeSensors: activeSensors ?? this.activeSensors,
      offlineSensors: offlineSensors ?? this.offlineSensors,
      weatherSummaryAr: weatherSummaryAr ?? this.weatherSummaryAr,
      weatherSummaryEn: weatherSummaryEn ?? this.weatherSummaryEn,
      waterUsageToday: waterUsageToday ?? this.waterUsageToday,
      lastSyncAt: lastSyncAt ?? this.lastSyncAt,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Recommendation Engine
// ═══════════════════════════════════════════════════════════════════════════

/// Smart recommendation engine
class SmartRecommendationEngine {
  final List<SmartRecommendation> _recommendations = [];
  final Set<String> _dismissedIds = {};

  /// All active (non-dismissed, non-expired) recommendations
  List<SmartRecommendation> get activeRecommendations {
    return _recommendations
        .where((r) => !r.isDismissed && !r.isExpired)
        .toList()
      ..sort((a, b) => b.priority.sortWeight.compareTo(a.priority.sortWeight));
  }

  /// Critical recommendations
  List<SmartRecommendation> get criticalRecommendations {
    return activeRecommendations
        .where((r) => r.priority == RecommendationPriority.critical)
        .toList();
  }

  /// Recommendations for a specific field
  List<SmartRecommendation> forField(String fieldId) {
    return activeRecommendations.where((r) => r.fieldId == fieldId).toList();
  }

  /// Recommendations by category
  List<SmartRecommendation> byCategory(RecommendationCategory category) {
    return activeRecommendations.where((r) => r.category == category).toList();
  }

  /// Count of active recommendations per priority
  Map<RecommendationPriority, int> get countByPriority {
    final counts = <RecommendationPriority, int>{};
    for (final r in activeRecommendations) {
      counts[r.priority] = (counts[r.priority] ?? 0) + 1;
    }
    return counts;
  }

  /// Add a recommendation
  void addRecommendation(SmartRecommendation recommendation) {
    if (_dismissedIds.contains(recommendation.id)) return;
    // Replace if same ID exists
    _recommendations.removeWhere((r) => r.id == recommendation.id);
    _recommendations.add(recommendation);
    AppLogger.d(
      'Recommendation added: ${recommendation.id} (${recommendation.priority.labelEn})',
      tag: 'DASHBOARD',
    );
  }

  /// Dismiss a recommendation
  void dismiss(String recommendationId) {
    _dismissedIds.add(recommendationId);
    final index = _recommendations.indexWhere((r) => r.id == recommendationId);
    if (index >= 0) {
      _recommendations[index] =
          _recommendations[index].copyWith(isDismissed: true);
    }
  }

  /// Clear all expired recommendations
  int clearExpired() {
    final before = _recommendations.length;
    _recommendations.removeWhere((r) => r.isExpired);
    final removed = before - _recommendations.length;
    if (removed > 0) {
      AppLogger.d('Cleared $removed expired recommendations', tag: 'DASHBOARD');
    }
    return removed;
  }

  /// Reset all recommendations
  void reset() {
    _recommendations.clear();
    _dismissedIds.clear();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Dashboard State
// ═══════════════════════════════════════════════════════════════════════════

/// Combined dashboard state
@immutable
class DashboardState {
  final DashboardStats stats;
  final List<SmartRecommendation> recommendations;
  final bool isLoading;
  final String? error;
  final DateTime? lastRefreshAt;

  const DashboardState({
    this.stats = const DashboardStats(),
    this.recommendations = const [],
    this.isLoading = false,
    this.error,
    this.lastRefreshAt,
  });

  /// Whether the dashboard has data
  bool get hasData => stats.totalFields > 0 || recommendations.isNotEmpty;

  /// Whether there are critical alerts
  bool get hasCriticalAlerts =>
      recommendations.any((r) => r.priority == RecommendationPriority.critical);

  /// Number of active recommendations
  int get activeRecommendationCount =>
      recommendations.where((r) => !r.isDismissed && !r.isExpired).length;

  DashboardState copyWith({
    DashboardStats? stats,
    List<SmartRecommendation>? recommendations,
    bool? isLoading,
    String? error,
    DateTime? lastRefreshAt,
    bool clearError = false,
  }) {
    return DashboardState(
      stats: stats ?? this.stats,
      recommendations: recommendations ?? this.recommendations,
      isLoading: isLoading ?? this.isLoading,
      error: clearError ? null : (error ?? this.error),
      lastRefreshAt: lastRefreshAt ?? this.lastRefreshAt,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for the recommendation engine
final recommendationEngineProvider = Provider<SmartRecommendationEngine>((ref) {
  return SmartRecommendationEngine();
});

/// Provider for dashboard state
final dashboardStateProvider = StateProvider<DashboardState>((ref) {
  return const DashboardState();
});

/// Provider for dashboard stats
final dashboardStatsProvider = Provider<DashboardStats>((ref) {
  return ref.watch(dashboardStateProvider).stats;
});

/// Provider for active recommendations
final activeRecommendationsProvider =
    Provider<List<SmartRecommendation>>((ref) {
  final state = ref.watch(dashboardStateProvider);
  return state.recommendations
      .where((r) => !r.isDismissed && !r.isExpired)
      .toList()
    ..sort((a, b) => b.priority.sortWeight.compareTo(a.priority.sortWeight));
});

/// Provider for critical alerts count
final criticalAlertsCountProvider = Provider<int>((ref) {
  return ref
      .watch(activeRecommendationsProvider)
      .where((r) => r.priority == RecommendationPriority.critical)
      .length;
});
