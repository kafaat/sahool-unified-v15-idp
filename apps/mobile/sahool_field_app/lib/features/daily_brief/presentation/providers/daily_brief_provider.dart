import 'package:flutter_riverpod/flutter_riverpod.dart';

/// Daily Brief Provider
/// موفر بيانات الملخص اليومي

final dailyBriefProvider = FutureProvider<DailyBrief>((ref) async {
  // In production, this would fetch from API
  await Future.delayed(const Duration(milliseconds: 500));

  return DailyBrief(
    greeting: _getGreeting(),
    headline: _getHeadline(),
    weather: WeatherSummary(
      temperature: 28,
      condition: 'sunny',
      humidity: 45,
      recommendation: 'طقس مثالي للعمل في الحقل',
    ),
    priorityItems: [
      PriorityItem(
        id: '1',
        title: 'ري حقل الشمال - منسوب الرطوبة منخفض',
        priority: Priority.high,
        type: PriorityType.irrigation,
        actionLabel: 'ابدأ الري',
      ),
      PriorityItem(
        id: '2',
        title: 'فحص البيت المحمي - علامات مبكرة للآفات',
        priority: Priority.medium,
        type: PriorityType.inspection,
        actionLabel: 'افحص',
      ),
      PriorityItem(
        id: '3',
        title: 'تسميد المنطقة الجنوبية',
        priority: Priority.low,
        type: PriorityType.task,
      ),
    ],
    pendingTasksCount: 5,
    alertsCount: 2,
    fieldsHealth: 85,
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
}

enum Priority { high, medium, low }

enum PriorityType { irrigation, inspection, task, alert, weather }
