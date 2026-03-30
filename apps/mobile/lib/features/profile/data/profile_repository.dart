/// SAHOOL Profile Repository
/// مستودع الملف الشخصي - يتصل بـ user-service (port 3025)
///
/// يوفر بيانات المستخدم الحالي مع دعم التحديث ورفع الصورة

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/config/api_config.dart';
import '../../../core/network/api_result.dart';
import '../../../core/offline/offline_sync_engine.dart';
import '../presentation/providers/profile_provider.dart';

// =============================================================================
// Providers
// =============================================================================

/// مزود مستودع الملف الشخصي
final profileRepoProvider = Provider<ProfileRepository>((ref) {
  return ProfileRepository();
});

// =============================================================================
// Repository
// =============================================================================

/// مستودع الملف الشخصي
/// Profile repository connecting to user-service (port 3025)
class ProfileRepository {
  final Dio _dio;

  ProfileRepository({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.effectiveBaseUrl,
              connectTimeout: ApiConfig.connectTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  /// جلب ملف المستخدم الحالي من user-service
  /// Endpoint: GET /api/v1/users/me
  Future<ApiResult<ProfileState>> getMe() async {
    try {
      final response = await _dio.get('/api/v1/users/me');

      final data = response.data is Map<String, dynamic>
          ? response.data as Map<String, dynamic>
          : <String, dynamic>{};

      return Success(_parseProfile(data));
    } on DioException catch (e) {
      return Failure(
        _getErrorMessage(e, 'فشل تحميل الملف الشخصي'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// تحديث الملف الشخصي
  /// Endpoint: PATCH /api/v1/users/me
  Future<ApiResult<ProfileState>> updateMe({
    String? userName,
    String? phone,
    String? farmName,
  }) async {
    final body = <String, dynamic>{};
    if (userName != null) body['name'] = userName;
    if (phone != null) body['phone'] = phone;
    if (farmName != null) body['farmName'] = farmName;

    try {
      final response = await _dio.patch('/api/v1/users/me', data: body);

      final data = response.data is Map<String, dynamic>
          ? response.data as Map<String, dynamic>
          : <String, dynamic>{};

      return Success(_parseProfile(data));
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueUpdate(
          entityType: 'user_preference',
          entityId: 'me',
          data: body,
          priority: SyncPriority.medium,
        );

        return Failure(
          'Saved offline - will sync when connected',
          statusCode: e.response?.statusCode,
          originalError: e,
        );
      }

      return Failure(
        _getErrorMessage(e, 'فشل تحديث الملف الشخصي'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  /// رفع صورة الملف الشخصي
  /// Endpoint: POST /api/v1/users/me/avatar
  Future<ApiResult<String>> uploadAvatar(String filePath) async {
    try {
      final formData = FormData.fromMap({
        'avatar': await MultipartFile.fromFile(filePath),
      });
      final response = await _dio.post('/api/v1/users/me/avatar', data: formData);
      String url = '';
      if (response.data is Map<String, dynamic>) {
        final responseData = response.data as Map<String, dynamic>;
        url = (responseData['avatarUrl'] ?? responseData['url'] ?? '').toString();
      }
      return Success(url);
    } on DioException catch (e) {
      // Only enqueue for offline sync on transient/network errors, not 4xx client errors
      final isTransient = e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.sendTimeout ||
          e.type == DioExceptionType.receiveTimeout ||
          e.type == DioExceptionType.connectionError ||
          (e.response?.statusCode != null && (e.response!.statusCode! >= 500 || e.response!.statusCode! == 429));

      if (isTransient) {
        await OfflineSyncEngine.instance.enqueueCreate(
          entityType: 'user_preference',
          data: {'filePath': filePath, 'type': 'avatar_upload'},
          priority: SyncPriority.medium,
        );

        return Failure(
          'Saved offline - will sync when connected',
          statusCode: e.response?.statusCode,
          originalError: e,
        );
      }

      return Failure(
        _getErrorMessage(e, 'فشل رفع الصورة'),
        statusCode: e.response?.statusCode,
        originalError: e,
      );
    } catch (e) {
      return Failure('خطأ غير متوقع: $e');
    }
  }

  static int _parseInt(dynamic value, {int defaultValue = 0}) {
    if (value == null) return defaultValue;
    if (value is int) return value;
    if (value is num) return value.toInt();
    if (value is String) return int.tryParse(value) ?? defaultValue;
    return defaultValue;
  }

  static double _parseDouble(dynamic value, {double defaultValue = 0}) {
    if (value == null) return defaultValue;
    if (value is num) return value.toDouble();
    if (value is String) return double.tryParse(value) ?? defaultValue;
    return defaultValue;
  }

  /// تحليل بيانات الملف الشخصي القادمة من الخادم
  ProfileState _parseProfile(Map<String, dynamic> data) {
    // Support both flat response and nested `user` key
    final user = data.containsKey('user') && data['user'] is Map
        ? data['user'] as Map<String, dynamic>
        : data;

    return ProfileState(
      userId: (user['id'] ?? user['userId'] ?? user['_id'] ?? '').toString(),
      userName: (user['name'] ?? user['userName'] ?? user['fullName'] ?? '').toString(),
      userNameAr: (user['nameAr'] ?? user['userNameAr'] ?? user['name'] ?? '').toString(),
      email: (user['email'] ?? '').toString(),
      phone: (user['phone'] ?? user['phoneNumber'] ?? '').toString(),
      avatarUrl: user['avatarUrl']?.toString() ?? user['avatar']?.toString(),
      farmName: (user['farmName'] ?? user['farm']?['name'] ?? '').toString(),
      farmNameAr: (user['farmNameAr'] ?? user['farm']?['nameAr'] ?? user['farmName'] ?? '').toString(),
      farmAreaHectares:
          _parseDouble(user['farmAreaHectares'] ?? user['farm']?['area']),
      location: (user['location'] ?? user['address'] ?? '').toString(),
      language: (user['language'] ?? user['lang'] ?? 'ar').toString(),
      fieldsCount: _parseInt(user['fieldsCount'] ?? user['stats']?['fields']),
      tasksCompleted:
          _parseInt(user['tasksCompleted'] ?? user['stats']?['tasks']),
      achievementsCount:
          _parseInt(user['achievementsCount'] ?? user['stats']?['achievements']),
    );
  }

  String _getErrorMessage(DioException e, String defaultMessage) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return 'انتهت مهلة الاتصال. تحقق من اتصالك بالإنترنت.';
    }
    if (e.type == DioExceptionType.connectionError) {
      return 'لا يمكن الاتصال بالخادم. تأكد من اتصالك بالإنترنت.';
    }
    if (e.response?.statusCode == 401) {
      return 'انتهت جلسة العمل. الرجاء تسجيل الدخول من جديد.';
    }
    if (e.response?.data != null && e.response?.data is Map) {
      final data = e.response?.data as Map;
      return (data['message'] ?? data['detail'] ?? defaultMessage).toString();
    }
    return defaultMessage;
  }
}
