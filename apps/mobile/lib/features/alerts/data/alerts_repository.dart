/// SAHOOL Alerts Repository
/// مستودع التنبيهات - تتصل بـ alert-service (port 8113)
///
/// يوفر قائمة التنبيهات مع دعم التصفية والتحديث

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_config.dart';
import '../../../core/network/api_result.dart';
import '../../../core/offline/offline_sync_engine.dart';
import '../../../core/utils/app_logger.dart';
import '../domain/alert_models.dart';

// =============================================================================
// Models
// =============================================================================

/// نموذج التنبيه القادم من الخادم
class AlertModel {
  final String id;
  final String title;
  final String subtitle;
  final AlertType type;
  final DateTime time;
  final bool isRead;

  const AlertModel({
    required this.id,
    required this.title,
    required this.subtitle,
    required this.type,
    required this.time,
    required this.isRead,
  });

  AlertModel copyWith({bool? isRead}) {
    return AlertModel(
      id: id,
      title: title,
      subtitle: subtitle,
      type: type,
      time: time,
      isRead: isRead ?? this.isRead,
    );
  }

  factory AlertModel.fromJson(Map<String, dynamic> json) {
    return AlertModel(
      id: (json['id'] ?? json['_id'] ?? '').toString(),
      title: (json['title'] ?? json['titleAr'] ?? '').toString(),
      subtitle: (json['message'] ?? json['subtitle'] ?? json['description'] ?? '').toString(),
      type: _parseType(json['severity'] ?? json['type'] ?? 'info'),
      time: json['createdAt'] != null
          ? DateTime.tryParse(json['createdAt'].toString()) ?? DateTime.now()
          : DateTime.now(),
      isRead: json['isRead'] == true || json['read'] == true,
    );
  }

  static AlertType _parseType(dynamic raw) {
    final value = raw?.toString().toLowerCase() ?? 'info';
    return switch (value) {
      'critical' || 'danger' || 'error' => AlertType.danger,
      'warning' || 'warn' => AlertType.warning,
      'success' || 'resolved' => AlertType.success,
      _ => AlertType.info,
    };
  }
}

// =============================================================================
// Providers
// =============================================================================

/// مزود مستودع التنبيهات
final alertsRepoProvider = Provider<AlertsRepository>((ref) {
  return AlertsRepository();
});

/// مزود قائمة التنبيهات
final alertsProvider = FutureProvider.autoDispose<List<AlertModel>>((ref) async {
  final repo = ref.read(alertsRepoProvider);
  final result = await repo.getAlerts();
  return result.when(
    success: (alerts) => alerts,
    failure: (message, statusCode) => throw Exception(message),
  );
});

// =============================================================================
// Repository
// =============================================================================

/// مستودع التنبيهات
class AlertsRepository {
  final Dio _dio;

  AlertsRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// جلب قائمة التنبيهات
  Future<ApiResult<List<AlertModel>>> getAlerts({bool? unreadOnly}) async {
    try {
      final queryParams = <String, dynamic>{};
      if (unreadOnly == true) queryParams['unread'] = true;

      final response = await _dio.get(
        '/api/v1/alerts',
        queryParameters: queryParams.isNotEmpty ? queryParams : null,
      );

      final List data = response.data is List
          ? response.data as List
          : (response.data as Map<String, dynamic>)['alerts'] as List? ??
              (response.data as Map<String, dynamic>)['data'] as List? ??
              [];

      return Success(
        data
            .map((e) => AlertModel.fromJson(e as Map<String, dynamic>))
            .toList(),
      );
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل التنبيهات'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// تعليم تنبيه كمقروء
  Future<ApiResult<void>> acknowledgeAlert(String alertId) async {
    try {
      await _dio.post('/api/v1/alerts/$alertId/acknowledge');
      return const Success(null);
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueUpdate(
          entityType: 'alert',
          entityId: alertId,
          data: {'acknowledged': true},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Alert acknowledgement queued for offline sync (API unavailable)', tag: 'AlertsRepo');
        return const Failure(
          'Saved offline - will sync when connected\nتم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return Failure(
        _getErrorMessage(e, 'فشل تحديث التنبيه'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// تعليم جميع التنبيهات كمقروءة
  Future<ApiResult<void>> acknowledgeAllAlerts() async {
    try {
      await _dio.post('/api/v1/alerts/acknowledge-all');
      return const Success(null);
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueUpdate(
          entityType: 'alert',
          entityId: 'all',
          data: {'acknowledge_all': true},
          priority: SyncPriority.medium,
        );

        AppLogger.w('Acknowledge all alerts queued for offline sync (API unavailable)', tag: 'AlertsRepo');
        return const Failure(
          'Saved offline - will sync when connected\nتم الحفظ محلياً - ستتم المزامنة عند الاتصال',
        );
      }

      return Failure(
        _getErrorMessage(e, 'فشل تحديث التنبيهات'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  String _getErrorMessage(DioException e, String defaultMessage) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return 'انتهت مهلة الاتصال. تحقق من اتصالك بالإنترنت.';
    }
    if (e.type == DioExceptionType.connectionError) {
      return 'لا يمكن الاتصال بالخادم. تأكد من اتصالك بالإنترنت.';
    }
    if (e.response?.data != null && e.response?.data is Map) {
      final data = e.response?.data as Map;
      return (data['message'] ?? data['detail'] ?? defaultMessage).toString();
    }
    return defaultMessage;
  }
}
