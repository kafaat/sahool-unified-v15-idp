import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/http/api_client.dart';

/// Daily Brief Provider
/// موفر بيانات الملخص اليومي

/// API client provider for daily brief
final _apiClientProvider = Provider.autoDispose<ApiClient>((ref) => ApiClient());

final dailyBriefProvider = FutureProvider.autoDispose<DailyBrief>((ref) async {
  final apiClient = ref.watch(_apiClientProvider);

  try {
    final response = await apiClient.get('/api/v1/daily-brief');

    if (response.statusCode == 200 && response.data != null) {
      return DailyBrief.fromJson(response.data as Map<String, dynamic>);
    }
  } catch (_) {
    // Fallback to local data when API is unavailable (offline-first)
    // الرجوع إلى البيانات المحلية عند عدم توفر الاتصال
  }

  // Offline fallback — construct from locally available data
  return DailyBrief(
    greeting: _getGreeting(),
    headline: _getHeadline(),
    weather: const WeatherSummary(
      temperature: 0,
      condition: 'unknown',
      humidity: 0,
      recommendation: 'لا توجد بيانات طقس - تحقق من الاتصال',
    ),
    priorityItems: const [],
    pendingTasksCount: 0,
    alertsCount: 0,
    fieldsHealth: 0,
  );
});

String _getGreeting() {
  final hour = DateTime.now().hour;
  if (hour < 12) return 'صباح الخير';
  if (hour < 17) return 'مساء الخير';
  return 'مساء النور';
}

String _getHeadline() {
  final hour = DateTime.now().hour;
  if (hour < 12) return 'ملخص يومك الزراعي';
  return 'تحديث المساء';
}

// ═══════════════════════════════════════════════════════════════════════════
// Models
// ═══════════════════════════════════════════════════════════════════════════

class DailyBrief {
  final String greeting;
  final String headline;
  final WeatherSummary weather;
  final List<PriorityItem> priorityItems;
  final int pendingTasksCount;
  final int alertsCount;
  final int fieldsHealth;

  const DailyBrief({
    required this.greeting,
    required this.headline,
    required this.weather,
    required this.priorityItems,
    required this.pendingTasksCount,
    required this.alertsCount,
    required this.fieldsHealth,
  });

  factory DailyBrief.fromJson(Map<String, dynamic> json) {
    return DailyBrief(
      greeting: json['greeting'] as String? ?? _getGreeting(),
      headline: json['headline'] as String? ?? _getHeadline(),
      weather: json['weather'] != null
          ? WeatherSummary.fromJson(json['weather'] as Map<String, dynamic>)
          : const WeatherSummary(temperature: 0, condition: 'unknown', humidity: 0, recommendation: ''),
      priorityItems: (json['priority_items'] as List<dynamic>?)
              ?.map((e) => PriorityItem.fromJson(e as Map<String, dynamic>))
              .toList() ??
          const [],
      pendingTasksCount: json['pending_tasks_count'] as int? ?? 0,
      alertsCount: json['alerts_count'] as int? ?? 0,
      fieldsHealth: json['fields_health'] as int? ?? 0,
    );
  }
}

class WeatherSummary {
  final int temperature;
  final String condition;
  final int humidity;
  final String recommendation;

  const WeatherSummary({
    required this.temperature,
    required this.condition,
    required this.humidity,
    required this.recommendation,
  });

  factory WeatherSummary.fromJson(Map<String, dynamic> json) {
    return WeatherSummary(
      temperature: json['temperature'] as int? ?? 0,
      condition: json['condition'] as String? ?? 'unknown',
      humidity: json['humidity'] as int? ?? 0,
      recommendation: json['recommendation'] as String? ?? '',
    );
  }
}

class PriorityItem {
  final String id;
  final String title;
  final Priority priority;
  final PriorityType type;
  final String? actionLabel;
  final String? actionRoute;

  const PriorityItem({
    required this.id,
    required this.title,
    required this.priority,
    required this.type,
    this.actionLabel,
    this.actionRoute,
  });

  factory PriorityItem.fromJson(Map<String, dynamic> json) {
    return PriorityItem(
      id: json['id'] as String? ?? '',
      title: json['title'] as String? ?? '',
      priority: Priority.values.firstWhere(
        (e) => e.name == json['priority'],
        orElse: () => Priority.low,
      ),
      type: PriorityType.values.firstWhere(
        (e) => e.name == json['type'],
        orElse: () => PriorityType.task,
      ),
      actionLabel: json['action_label'] as String?,
      actionRoute: json['action_route'] as String?,
    );
  }
}

enum Priority { high, medium, low }

enum PriorityType { irrigation, inspection, task, alert, weather }
