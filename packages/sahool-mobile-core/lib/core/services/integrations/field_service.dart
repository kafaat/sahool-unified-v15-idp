/// SAHOOL Field Service Integration
/// تكامل خدمة إدارة الحقول
///
/// Handles all field-related operations:
/// - Field CRUD operations
/// - Field synchronization
/// - Nearby fields discovery
/// - Task management
library;

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../network/api_result.dart';
import '../service_connector.dart';

/// Field model
class Field {
  final String id;
  final String name;
  final String? nameAr;
  final double area;
  final String? areaUnit;
  final String? cropType;
  final String? cropStage;
  final Map<String, dynamic>? boundary;
  final Map<String, dynamic>? centroid;
  final String? status;
  final String? tenantId;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final Map<String, dynamic>? metadata;

  const Field({
    required this.id,
    required this.name,
    this.nameAr,
    required this.area,
    this.areaUnit,
    this.cropType,
    this.cropStage,
    this.boundary,
    this.centroid,
    this.status,
    this.tenantId,
    this.createdAt,
    this.updatedAt,
    this.metadata,
  });

  factory Field.fromJson(Map<String, dynamic> json) {
    return Field(
      id: json['id'] as String? ?? json['_id'] as String? ?? '',
      name: json['name'] as String? ?? '',
      nameAr: json['name_ar'] as String?,
      area: (json['area'] as num?)?.toDouble() ?? 0.0,
      areaUnit: json['area_unit'] as String?,
      cropType: json['crop_type'] as String?,
      cropStage: json['crop_stage'] as String?,
      boundary: json['boundary'] as Map<String, dynamic>?,
      centroid: json['centroid'] as Map<String, dynamic>?,
      status: json['status'] as String?,
      tenantId: json['tenant_id'] as String?,
      createdAt: json['created_at'] != null
          ? DateTime.tryParse(json['created_at'] as String)
          : null,
      updatedAt: json['updated_at'] != null
          ? DateTime.tryParse(json['updated_at'] as String)
          : null,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        'name': name,
        if (nameAr != null) 'name_ar': nameAr,
        'area': area,
        if (areaUnit != null) 'area_unit': areaUnit,
        if (cropType != null) 'crop_type': cropType,
        if (cropStage != null) 'crop_stage': cropStage,
        if (boundary != null) 'boundary': boundary,
        if (centroid != null) 'centroid': centroid,
        if (status != null) 'status': status,
        if (tenantId != null) 'tenant_id': tenantId,
        if (metadata != null) 'metadata': metadata,
      };
}

/// Task model
class FieldTask {
  final String id;
  final String? fieldId;
  final String title;
  final String? titleAr;
  final String? description;
  final String? descriptionAr;
  final String type;
  final String status;
  final String? priority;
  final DateTime? dueDate;
  final DateTime? completedAt;
  final String? assignedTo;
  final Map<String, dynamic>? metadata;

  const FieldTask({
    required this.id,
    this.fieldId,
    required this.title,
    this.titleAr,
    this.description,
    this.descriptionAr,
    required this.type,
    required this.status,
    this.priority,
    this.dueDate,
    this.completedAt,
    this.assignedTo,
    this.metadata,
  });

  factory FieldTask.fromJson(Map<String, dynamic> json) {
    return FieldTask(
      id: json['id'] as String? ?? json['_id'] as String? ?? '',
      fieldId: json['field_id'] as String?,
      title: json['title'] as String? ?? '',
      titleAr: json['title_ar'] as String?,
      description: json['description'] as String?,
      descriptionAr: json['description_ar'] as String?,
      type: json['type'] as String? ?? 'general',
      status: json['status'] as String? ?? 'pending',
      priority: json['priority'] as String?,
      dueDate: json['due_date'] != null
          ? DateTime.tryParse(json['due_date'] as String)
          : null,
      completedAt: json['completed_at'] != null
          ? DateTime.tryParse(json['completed_at'] as String)
          : null,
      assignedTo: json['assigned_to'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
    );
  }

  Map<String, dynamic> toJson() => {
        'id': id,
        if (fieldId != null) 'field_id': fieldId,
        'title': title,
        if (titleAr != null) 'title_ar': titleAr,
        if (description != null) 'description': description,
        if (descriptionAr != null) 'description_ar': descriptionAr,
        'type': type,
        'status': status,
        if (priority != null) 'priority': priority,
        if (dueDate != null) 'due_date': dueDate!.toIso8601String(),
        if (assignedTo != null) 'assigned_to': assignedTo,
        if (metadata != null) 'metadata': metadata,
      };
}

/// Field Service Connector
/// موصل خدمة الحقول
class FieldServiceConnector extends ServiceConnector {
  FieldServiceConnector({required super.ref}) : super(serviceId: 'field-management');

  /// Get all fields
  /// الحصول على جميع الحقول
  Future<ApiResult<List<Field>>> getFields({
    int? page,
    int? limit,
    String? status,
    String? cropType,
  }) async {
    final queryParams = <String, dynamic>{
      if (page != null) 'page': page,
      if (limit != null) 'limit': limit,
      if (status != null) 'status': status,
      if (cropType != null) 'crop_type': cropType,
    };

    return get(
      getEndpoint('fields') ?? '/api/v1/fields',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => Field.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['data'] != null) {
          return (data['data'] as List)
              .map((e) => Field.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <Field>[];
      },
    );
  }

  /// Get field by ID
  /// الحصول على حقل بالمعرف
  Future<ApiResult<Field>> getFieldById(String fieldId) async {
    return get(
      '${getEndpoint('fields') ?? '/api/v1/fields'}/$fieldId',
      parser: (data) => Field.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Create new field
  /// إنشاء حقل جديد
  Future<ApiResult<Field>> createField(Field field) async {
    return post(
      getEndpoint('fields') ?? '/api/v1/fields',
      data: field.toJson(),
      parser: (data) => Field.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Update field
  /// تحديث حقل
  Future<ApiResult<Field>> updateField(String fieldId, Map<String, dynamic> updates) async {
    return patch(
      '${getEndpoint('fields') ?? '/api/v1/fields'}/$fieldId',
      data: updates,
      parser: (data) => Field.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Delete field
  /// حذف حقل
  Future<ApiResult<bool>> deleteField(String fieldId) async {
    return delete(
      '${getEndpoint('fields') ?? '/api/v1/fields'}/$fieldId',
      parser: (_) => true,
    );
  }

  /// Sync fields (for offline-first)
  /// مزامنة الحقول
  Future<ApiResult<Map<String, dynamic>>> syncFields({
    required DateTime lastSyncTime,
    required List<Map<String, dynamic>> localChanges,
  }) async {
    return post(
      getEndpoint('sync') ?? '/api/v1/fields/sync',
      data: {
        'last_sync': lastSyncTime.toIso8601String(),
        'changes': localChanges,
      },
      parser: (data) => data as Map<String, dynamic>,
    );
  }

  /// Batch create/update fields
  /// إنشاء/تحديث حقول دفعة واحدة
  Future<ApiResult<List<Field>>> batchFields(List<Field> fields) async {
    return post(
      getEndpoint('batch') ?? '/api/v1/fields/batch',
      data: {'fields': fields.map((f) => f.toJson()).toList()},
      parser: (data) {
        if (data is List) {
          return data.map((e) => Field.fromJson(e as Map<String, dynamic>)).toList();
        }
        return <Field>[];
      },
    );
  }

  /// Get nearby fields
  /// الحصول على الحقول القريبة
  Future<ApiResult<List<Field>>> getNearbyFields({
    required double latitude,
    required double longitude,
    double radiusKm = 10,
  }) async {
    return get(
      getEndpoint('nearby') ?? '/api/v1/fields/nearby',
      queryParameters: {
        'lat': latitude,
        'lng': longitude,
        'radius': radiusKm,
      },
      parser: (data) {
        if (data is List) {
          return data.map((e) => Field.fromJson(e as Map<String, dynamic>)).toList();
        }
        return <Field>[];
      },
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════════
  // Task Operations
  // ═══════════════════════════════════════════════════════════════════════════════

  /// Get tasks
  /// الحصول على المهام
  Future<ApiResult<List<FieldTask>>> getTasks({
    String? fieldId,
    String? status,
    String? type,
    int? page,
    int? limit,
  }) async {
    final queryParams = <String, dynamic>{
      if (fieldId != null) 'field_id': fieldId,
      if (status != null) 'status': status,
      if (type != null) 'type': type,
      if (page != null) 'page': page,
      if (limit != null) 'limit': limit,
    };

    return get(
      getEndpoint('tasks') ?? '/api/v1/tasks',
      queryParameters: queryParams.isNotEmpty ? queryParams : null,
      parser: (data) {
        if (data is List) {
          return data.map((e) => FieldTask.fromJson(e as Map<String, dynamic>)).toList();
        }
        if (data is Map && data['data'] != null) {
          return (data['data'] as List)
              .map((e) => FieldTask.fromJson(e as Map<String, dynamic>))
              .toList();
        }
        return <FieldTask>[];
      },
    );
  }

  /// Get task by ID
  /// الحصول على مهمة بالمعرف
  Future<ApiResult<FieldTask>> getTaskById(String taskId) async {
    return get(
      '${getEndpoint('tasks') ?? '/api/v1/tasks'}/$taskId',
      parser: (data) => FieldTask.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Create task
  /// إنشاء مهمة
  Future<ApiResult<FieldTask>> createTask(FieldTask task) async {
    return post(
      getEndpoint('tasks') ?? '/api/v1/tasks',
      data: task.toJson(),
      parser: (data) => FieldTask.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Update task
  /// تحديث مهمة
  Future<ApiResult<FieldTask>> updateTask(String taskId, Map<String, dynamic> updates) async {
    return patch(
      '${getEndpoint('tasks') ?? '/api/v1/tasks'}/$taskId',
      data: updates,
      parser: (data) => FieldTask.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Complete task
  /// إكمال مهمة
  Future<ApiResult<FieldTask>> completeTask(String taskId) async {
    return patch(
      '${getEndpoint('tasks') ?? '/api/v1/tasks'}/$taskId',
      data: {
        'status': 'completed',
        'completed_at': DateTime.now().toIso8601String(),
      },
      parser: (data) => FieldTask.fromJson(data as Map<String, dynamic>),
    );
  }

  /// Delete task
  /// حذف مهمة
  Future<ApiResult<bool>> deleteTask(String taskId) async {
    return delete(
      '${getEndpoint('tasks') ?? '/api/v1/tasks'}/$taskId',
      parser: (_) => true,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════════

/// Field Service Provider
final fieldServiceProvider = Provider<FieldServiceConnector>((ref) {
  return FieldServiceConnector(ref: ref);
});

/// Fields List Provider
final fieldsProvider = FutureProvider<List<Field>>((ref) async {
  final service = ref.watch(fieldServiceProvider);
  final result = await service.getFields();
  return result.dataOrNull ?? [];
});

/// Field by ID Provider
final fieldByIdProvider = FutureProvider.family<Field?, String>((ref, fieldId) async {
  final service = ref.watch(fieldServiceProvider);
  final result = await service.getFieldById(fieldId);
  return result.dataOrNull;
});

/// Tasks Provider
final tasksProvider = FutureProvider.family<List<FieldTask>, String?>((ref, fieldId) async {
  final service = ref.watch(fieldServiceProvider);
  final result = await service.getTasks(fieldId: fieldId);
  return result.dataOrNull ?? [];
});

/// Pending Tasks Count Provider
final pendingTasksCountProvider = FutureProvider<int>((ref) async {
  final service = ref.watch(fieldServiceProvider);
  final result = await service.getTasks(status: 'pending');
  return result.dataOrNull?.length ?? 0;
});
