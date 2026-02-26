import '../../../core/api/kong_gateway_client.dart';

/// Soil Analysis Service API
/// خدمة تحليل التربة - متصلة بـ soil-analysis-service (port 8134)
///
/// Endpoints:
///   GET  /samples          - List samples with pagination/filters
///   GET  /samples/:id      - Get sample details
///   POST /samples          - Create new sample
///   PUT  /samples/:id/status - Update sample status
///   GET  /samples/:id/results - Get analysis results
///   GET  /stats            - Get lab statistics
class SoilAnalysisApi {
  final KongGatewayClient _gateway;

  SoilAnalysisApi({KongGatewayClient? gateway})
      : _gateway = gateway ?? kongGateway;

  /// List samples with optional filters
  /// قائمة العينات مع فلاتر اختيارية
  Future<ApiResponse<SamplesPageResponse>> getSamples({
    String? fieldId,
    String? status,
    String? type,
    int page = 1,
    int limit = 50,
  }) async {
    return _gateway.get<SamplesPageResponse>(
      KongServices.soilAnalysis,
      '/samples',
      queryParams: {
        'page': page,
        'limit': limit,
        if (fieldId != null) 'field_id': fieldId,
        if (status != null) 'status': status,
        if (type != null) 'type': type,
      },
      fromJson: (data) => SamplesPageResponse.fromJson(
        data as Map<String, dynamic>,
      ),
    );
  }

  /// Get a specific sample by ID
  /// الحصول على عينة محددة
  Future<ApiResponse<SoilSampleModel>> getSample({
    required String sampleId,
  }) async {
    return _gateway.get<SoilSampleModel>(
      KongServices.soilAnalysis,
      '/samples/$sampleId',
      fromJson: (data) => SoilSampleModel.fromJson(
        data as Map<String, dynamic>,
      ),
    );
  }

  /// Create a new sample
  /// إنشاء عينة جديدة
  Future<ApiResponse<SoilSampleModel>> createSample({
    required String type,
    required String experimentName,
    required String plotCode,
    required String collectedBy,
    String? fieldId,
    String? notes,
  }) async {
    return _gateway.post<SoilSampleModel>(
      KongServices.soilAnalysis,
      '/samples',
      data: {
        'type': type,
        'experiment_name': experimentName,
        'plot_code': plotCode,
        'collected_by': collectedBy,
        if (fieldId != null) 'field_id': fieldId,
        if (notes != null) 'notes': notes,
      },
      fromJson: (data) => SoilSampleModel.fromJson(
        data as Map<String, dynamic>,
      ),
    );
  }

  /// Update sample status
  /// تحديث حالة العينة
  Future<ApiResponse<SoilSampleModel>> updateSampleStatus({
    required String sampleId,
    required String status,
    String? userId,
  }) async {
    return _gateway.put<SoilSampleModel>(
      KongServices.soilAnalysis,
      '/samples/$sampleId/status',
      data: {
        'status': status,
        if (userId != null) 'updated_by': userId,
      },
      fromJson: (data) => SoilSampleModel.fromJson(
        data as Map<String, dynamic>,
      ),
    );
  }

  /// Get analysis results for a sample
  /// الحصول على نتائج التحليل
  Future<ApiResponse<AnalysisResultModel>> getAnalysisResults({
    required String sampleId,
  }) async {
    return _gateway.get<AnalysisResultModel>(
      KongServices.soilAnalysis,
      '/samples/$sampleId/results',
      fromJson: (data) => AnalysisResultModel.fromJson(
        data as Map<String, dynamic>,
      ),
    );
  }

  /// Get lab statistics
  /// الحصول على إحصائيات المختبر
  Future<ApiResponse<LabStats>> getLabStats({
    String? fieldId,
  }) async {
    return _gateway.get<LabStats>(
      KongServices.soilAnalysis,
      '/stats',
      queryParams: {
        if (fieldId != null) 'field_id': fieldId,
      },
      fromJson: (data) => LabStats.fromJson(
        data as Map<String, dynamic>,
      ),
    );
  }

  /// Search sample by barcode
  /// البحث عن عينة بالباركود
  Future<ApiResponse<SoilSampleModel>> searchByBarcode({
    required String barcode,
  }) async {
    return _gateway.get<SoilSampleModel>(
      KongServices.soilAnalysis,
      '/samples/barcode/$barcode',
      fromJson: (data) => SoilSampleModel.fromJson(
        data as Map<String, dynamic>,
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Models - نماذج البيانات
// ═══════════════════════════════════════════════════════════════════════════

class SamplesPageResponse {
  final List<SoilSampleModel> samples;
  final int total;
  final int page;
  final int limit;

  SamplesPageResponse({
    required this.samples,
    required this.total,
    required this.page,
    required this.limit,
  });

  factory SamplesPageResponse.fromJson(Map<String, dynamic> json) {
    final items = json['samples'] ?? json['items'] ?? json['data'] ?? [];
    return SamplesPageResponse(
      samples: (items as List)
          .map((e) => SoilSampleModel.fromJson(e as Map<String, dynamic>))
          .toList(),
      total: json['total'] ?? 0,
      page: json['page'] ?? 1,
      limit: json['limit'] ?? 50,
    );
  }
}

class SoilSampleModel {
  final String id;
  final String barcode;
  final String type;
  final String status;
  final String experimentName;
  final String plotCode;
  final String collectedBy;
  final String? fieldId;
  final String? notes;
  final DateTime collectedAt;
  final DateTime? receivedAt;
  final DateTime? analyzedAt;
  final Map<String, dynamic>? results;
  final Map<String, dynamic>? metadata;

  SoilSampleModel({
    required this.id,
    required this.barcode,
    required this.type,
    required this.status,
    required this.experimentName,
    required this.plotCode,
    required this.collectedBy,
    this.fieldId,
    this.notes,
    required this.collectedAt,
    this.receivedAt,
    this.analyzedAt,
    this.results,
    this.metadata,
  });

  factory SoilSampleModel.fromJson(Map<String, dynamic> json) {
    return SoilSampleModel(
      id: json['id'] ?? '',
      barcode: json['barcode'] ?? '',
      type: json['type'] ?? 'soil',
      status: json['status'] ?? 'pending',
      experimentName: json['experiment_name'] ?? json['experiment'] ?? '',
      plotCode: json['plot_code'] ?? json['plot'] ?? '',
      collectedBy: json['collected_by'] ?? '',
      fieldId: json['field_id'],
      notes: json['notes'],
      collectedAt:
          DateTime.tryParse(json['collected_at'] ?? '') ?? DateTime.now(),
      receivedAt: json['received_at'] != null
          ? DateTime.tryParse(json['received_at'])
          : null,
      analyzedAt: json['analyzed_at'] != null
          ? DateTime.tryParse(json['analyzed_at'])
          : null,
      results: json['results'],
      metadata: json['metadata'],
    );
  }

  /// Map API status string to SampleStatus enum
  SampleStatus get sampleStatus {
    switch (status) {
      case 'pending':
        return SampleStatus.pending;
      case 'in_transit':
        return SampleStatus.inTransit;
      case 'received':
        return SampleStatus.received;
      case 'processing':
        return SampleStatus.processing;
      case 'analyzed':
        return SampleStatus.analyzed;
      default:
        return SampleStatus.pending;
    }
  }

  /// Map API type string to Arabic display
  String get typeAr {
    switch (type) {
      case 'soil':
        return 'تربة';
      case 'leaf':
        return 'أوراق';
      case 'water':
        return 'ماء';
      case 'fruit':
        return 'ثمار';
      case 'seed':
        return 'بذور';
      default:
        return type;
    }
  }
}

class AnalysisResultModel {
  final String sampleId;
  final Map<String, dynamic> results;
  final String? interpretation;
  final String? interpretationAr;
  final List<String> recommendations;
  final DateTime analyzedAt;

  AnalysisResultModel({
    required this.sampleId,
    required this.results,
    this.interpretation,
    this.interpretationAr,
    required this.recommendations,
    required this.analyzedAt,
  });

  factory AnalysisResultModel.fromJson(Map<String, dynamic> json) {
    return AnalysisResultModel(
      sampleId: json['sample_id'] ?? '',
      results: json['results'] ?? {},
      interpretation: json['interpretation'],
      interpretationAr: json['interpretation_ar'],
      recommendations: (json['recommendations'] as List?)?.cast<String>() ?? [],
      analyzedAt:
          DateTime.tryParse(json['analyzed_at'] ?? '') ?? DateTime.now(),
    );
  }
}

class LabStats {
  final int totalSamples;
  final int pendingSamples;
  final int inTransitSamples;
  final int processingSamples;
  final int analyzedSamples;
  final double averageProcessingDays;

  LabStats({
    required this.totalSamples,
    required this.pendingSamples,
    required this.inTransitSamples,
    required this.processingSamples,
    required this.analyzedSamples,
    required this.averageProcessingDays,
  });

  factory LabStats.fromJson(Map<String, dynamic> json) {
    return LabStats(
      totalSamples: json['total'] ?? json['total_samples'] ?? 0,
      pendingSamples: json['pending'] ?? 0,
      inTransitSamples: json['in_transit'] ?? 0,
      processingSamples: json['processing'] ?? 0,
      analyzedSamples: json['analyzed'] ?? 0,
      averageProcessingDays: (json['avg_processing_days'] ?? 0.0).toDouble(),
    );
  }
}

/// Reusable sample status enum
enum SampleStatus {
  pending,
  inTransit,
  received,
  processing,
  analyzed,
}
