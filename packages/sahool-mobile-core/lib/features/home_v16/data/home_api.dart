/// SAHOOL Home API v16
/// واجهة برمجة الشاشة الرئيسية
library;

import '../../../core/http/api_client.dart';
import '../../../core/config/api_config.dart';

/// Dashboard summary data from indicators service
class DashboardSummary {
  final double ndviAvg;
  final int alertsOpen;
  final String weatherSummary;
  final int tasksDue;
  final int fieldsCount;
  final double irrigationDue;

  DashboardSummary({
    required this.ndviAvg,
    required this.alertsOpen,
    required this.weatherSummary,
    required this.tasksDue,
    required this.fieldsCount,
    required this.irrigationDue,
  });

  factory DashboardSummary.fromJson(Map<String, dynamic> json) {
    return DashboardSummary(
      ndviAvg: (json['ndvi_avg'] as num?)?.toDouble() ?? 0.0,
      alertsOpen: json['alerts_open'] as int? ?? 0,
      weatherSummary: json['weather_summary'] as String? ?? '—',
      tasksDue: json['tasks_due'] as int? ?? 0,
      fieldsCount: json['fields_count'] as int? ?? 0,
      irrigationDue: (json['irrigation_due'] as num?)?.toDouble() ?? 0.0,
    );
  }
}

/// Home API - fetches dashboard data from indicators service
class HomeApi {
  final ApiClient _client;

  HomeApi(this._client);

  /// Fetch dashboard summary for tenant
  ///
  /// Returns aggregated metrics including NDVI, alerts, tasks, and fields
  Future<DashboardSummary> fetchDashboardSummary({
    required String tenantId,
  }) async {
    final response = await _client.get(
      ApiConfig.dashboardByTenant(tenantId),
    );

    if (response is Map<String, dynamic>) {
      return DashboardSummary.fromJson(response);
    }

    throw Exception('Invalid dashboard response format');
  }
}
