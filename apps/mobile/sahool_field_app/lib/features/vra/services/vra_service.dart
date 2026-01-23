/// VRA Service - خدمة التطبيق المتغير
/// يتواصل مع FastAPI VRA Service
library;

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/config/api_config.dart';
import '../models/vra_models.dart';

/// VRA Service Provider
final vraServiceProvider = Provider<VRAService>((ref) {
  return VRAService();
});

/// نتيجة API
class ApiResult<T> {
  final T? data;
  final String? error;
  final String? errorAr;
  final bool isSuccess;

  const ApiResult._({this.data, this.error, this.errorAr, required this.isSuccess});

  factory ApiResult.success(T data) => ApiResult._(data: data, isSuccess: true);
  factory ApiResult.failure(String error, [String? errorAr]) =>
      ApiResult._(error: error, errorAr: errorAr, isSuccess: false);
}

/// VRA Service
class VRAService {
  final Dio _dio;

  VRAService({Dio? dio})
      : _dio = dio ??
            Dio(BaseOptions(
              baseUrl: ApiConfig.vraServiceUrl,
              connectTimeout: ApiConfig.connectTimeout,
              sendTimeout: ApiConfig.sendTimeout,
              receiveTimeout: ApiConfig.receiveTimeout,
              headers: ApiConfig.defaultHeaders,
            ));

  // ─────────────────────────────────────────────────────────────────────────────
  // Prescriptions CRUD
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب جميع الوصفات
  Future<ApiResult<List<VRAPrescription>>> getPrescriptions({
    String? fieldId,
    VRAType? vraType,
    PrescriptionStatus? status,
    DateTime? startDate,
    DateTime? endDate,
    int limit = 50,
    int offset = 0,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'limit': limit,
        'offset': offset,
      };
      if (fieldId != null) queryParams['field_id'] = fieldId;
      if (vraType != null) queryParams['vra_type'] = vraType.value;
      if (status != null) queryParams['status'] = status.value;
      if (startDate != null) queryParams['start_date'] = startDate.toIso8601String();
      if (endDate != null) queryParams['end_date'] = endDate.toIso8601String();

      final response = await _dio.get(
        '/v1/vra/prescriptions',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final prescriptions = (data['prescriptions'] as List)
          .map((e) => VRAPrescription.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(prescriptions);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch prescriptions',
        'فشل في جلب الوصفات',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// جلب وصفة محددة
  Future<ApiResult<VRAPrescription>> getPrescriptionById(String prescriptionId) async {
    try {
      final response = await _dio.get('/v1/vra/prescriptions/$prescriptionId');
      return ApiResult.success(
        VRAPrescription.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Prescription not found', 'الوصفة غير موجودة');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to fetch prescription',
        'فشل في جلب الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إنشاء وصفة جديدة (توليد تلقائي)
  Future<ApiResult<VRAPrescription>> generatePrescription({
    required String fieldId,
    required VRAType vraType,
    required ZoningMethod zoningMethod,
    required int zonesCount,
    String? name,
    String? nameAr,
    DateTime? scheduledDate,
    String? notes,
    String? notesAr,
    Map<String, dynamic>? parameters,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/vra/prescriptions/generate',
        data: {
          'field_id': fieldId,
          'vra_type': vraType.value,
          'zoning_method': zoningMethod.value,
          'zones_count': zonesCount,
          'name': name,
          'name_ar': nameAr,
          'scheduled_date': scheduledDate?.toIso8601String(),
          'notes': notes,
          'notes_ar': notesAr,
          'parameters': parameters,
        },
      );

      return ApiResult.success(
        VRAPrescription.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to generate prescription',
        'فشل في توليد الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إنشاء وصفة يدوية
  Future<ApiResult<VRAPrescription>> createPrescription({
    required String fieldId,
    required String name,
    String? nameAr,
    required VRAType vraType,
    required ZoningMethod zoningMethod,
    required List<ManagementZone> zones,
    required List<ApplicationRate> rates,
    DateTime? scheduledDate,
    String? notes,
    String? notesAr,
    Map<String, dynamic>? parameters,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/vra/prescriptions',
        data: {
          'field_id': fieldId,
          'name': name,
          'name_ar': nameAr,
          'vra_type': vraType.value,
          'zoning_method': zoningMethod.value,
          'zones': zones.map((e) => e.toJson()).toList(),
          'rates': rates.map((e) => e.toJson()).toList(),
          'scheduled_date': scheduledDate?.toIso8601String(),
          'notes': notes,
          'notes_ar': notesAr,
          'parameters': parameters,
        },
      );

      return ApiResult.success(
        VRAPrescription.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to create prescription',
        'فشل في إنشاء الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تحديث وصفة
  Future<ApiResult<VRAPrescription>> updatePrescription(
    String prescriptionId,
    Map<String, dynamic> updates,
  ) async {
    try {
      final response = await _dio.put(
        '/v1/vra/prescriptions/$prescriptionId',
        data: updates,
      );

      return ApiResult.success(
        VRAPrescription.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Prescription not found', 'الوصفة غير موجودة');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to update prescription',
        'فشل في تحديث الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// حذف وصفة
  Future<ApiResult<void>> deletePrescription(String prescriptionId) async {
    try {
      await _dio.delete('/v1/vra/prescriptions/$prescriptionId');
      return ApiResult.success(null);
    } on DioException catch (e) {
      if (e.response?.statusCode == 404) {
        return ApiResult.failure('Prescription not found', 'الوصفة غير موجودة');
      }
      return ApiResult.failure(
        e.message ?? 'Failed to delete prescription',
        'فشل في حذف الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Prescription Actions
  // ─────────────────────────────────────────────────────────────────────────────

  /// اعتماد وصفة
  Future<ApiResult<VRAPrescription>> approvePrescription(
    String prescriptionId, {
    String? notes,
    String? notesAr,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/vra/prescriptions/$prescriptionId/approve',
        data: {
          'notes': notes,
          'notes_ar': notesAr,
        },
      );

      return ApiResult.success(
        VRAPrescription.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to approve prescription',
        'فشل في اعتماد الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تطبيق وصفة
  Future<ApiResult<VRAPrescription>> applyPrescription(
    String prescriptionId, {
    DateTime? appliedDate,
    String? notes,
    String? notesAr,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/vra/prescriptions/$prescriptionId/apply',
        data: {
          'applied_date': appliedDate?.toIso8601String(),
          'notes': notes,
          'notes_ar': notesAr,
        },
      );

      return ApiResult.success(
        VRAPrescription.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to apply prescription',
        'فشل في تطبيق الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// إلغاء وصفة
  Future<ApiResult<VRAPrescription>> cancelPrescription(
    String prescriptionId, {
    String? reason,
    String? reasonAr,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/vra/prescriptions/$prescriptionId/cancel',
        data: {
          'reason': reason,
          'reason_ar': reasonAr,
        },
      );

      return ApiResult.success(
        VRAPrescription.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to cancel prescription',
        'فشل في إلغاء الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Export
  // ─────────────────────────────────────────────────────────────────────────────

  /// تصدير وصفة
  Future<ApiResult<Map<String, dynamic>>> exportPrescription(
    String prescriptionId, {
    required String format, // geojson, shapefile, iso11783
  }) async {
    try {
      final response = await _dio.get(
        '/v1/vra/prescriptions/$prescriptionId/export',
        queryParameters: {'format': format},
      );

      return ApiResult.success(response.data as Map<String, dynamic>);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to export prescription',
        'فشل في تصدير الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// تنزيل وصفة كملف
  Future<ApiResult<String>> downloadPrescription(
    String prescriptionId, {
    required String format,
    required String savePath,
  }) async {
    try {
      await _dio.download(
        '/v1/vra/prescriptions/$prescriptionId/download',
        savePath,
        queryParameters: {'format': format},
      );

      return ApiResult.success(savePath);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to download prescription',
        'فشل في تنزيل الوصفة',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Statistics
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب إحصائيات VRA
  Future<ApiResult<VRAStats>> getStats() async {
    try {
      final response = await _dio.get('/v1/vra/stats');
      return ApiResult.success(
        VRAStats.fromJson(response.data as Map<String, dynamic>),
      );
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch stats',
        'فشل في جلب الإحصائيات',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Management Zones
  // ─────────────────────────────────────────────────────────────────────────────

  /// جلب مناطق الإدارة لحقل
  Future<ApiResult<List<ManagementZone>>> getFieldZones(
    String fieldId, {
    ZoningMethod? zoningMethod,
    int? zonesCount,
  }) async {
    try {
      final queryParams = <String, dynamic>{};
      if (zoningMethod != null) queryParams['zoning_method'] = zoningMethod.value;
      if (zonesCount != null) queryParams['zones_count'] = zonesCount;

      final response = await _dio.get(
        '/v1/vra/fields/$fieldId/zones',
        queryParameters: queryParams,
      );

      final data = response.data as Map<String, dynamic>;
      final zones = (data['zones'] as List)
          .map((e) => ManagementZone.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(zones);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to fetch zones',
        'فشل في جلب المناطق',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }

  /// توليد مناطق إدارة
  Future<ApiResult<List<ManagementZone>>> generateZones({
    required String fieldId,
    required ZoningMethod zoningMethod,
    required int zonesCount,
    Map<String, dynamic>? parameters,
  }) async {
    try {
      final response = await _dio.post(
        '/v1/vra/zones/generate',
        data: {
          'field_id': fieldId,
          'zoning_method': zoningMethod.value,
          'zones_count': zonesCount,
          'parameters': parameters,
        },
      );

      final data = response.data as Map<String, dynamic>;
      final zones = (data['zones'] as List)
          .map((e) => ManagementZone.fromJson(e as Map<String, dynamic>))
          .toList();

      return ApiResult.success(zones);
    } on DioException catch (e) {
      return ApiResult.failure(
        e.message ?? 'Failed to generate zones',
        'فشل في توليد المناطق',
      );
    } catch (e) {
      return ApiResult.failure(e.toString(), 'حدث خطأ غير متوقع');
    }
  }
}
