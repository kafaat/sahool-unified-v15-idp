import 'dart:async';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:latlong2/latlong.dart';

import '../../../../core/di/providers.dart';
import '../../../../core/utils/app_logger.dart';
import '../../data/repo/fields_repo.dart';
import '../../domain/entities/field.dart';

/// Field Controller State
/// Manages field CRUD operations and UI state
class FieldControllerState {
  final bool isLoading;
  final bool isSaving;
  final bool isDeleting;
  final bool isRefreshing;
  final String? error;
  final Field? selectedField;
  final List<Field> fields;
  final int unsyncedCount;

  const FieldControllerState({
    this.isLoading = false,
    this.isSaving = false,
    this.isDeleting = false,
    this.isRefreshing = false,
    this.error,
    this.selectedField,
    this.fields = const [],
    this.unsyncedCount = 0,
  });

  FieldControllerState copyWith({
    bool? isLoading,
    bool? isSaving,
    bool? isDeleting,
    bool? isRefreshing,
    String? error,
    Field? selectedField,
    List<Field>? fields,
    int? unsyncedCount,
    bool clearError = false,
    bool clearSelectedField = false,
  }) {
    return FieldControllerState(
      isLoading: isLoading ?? this.isLoading,
      isSaving: isSaving ?? this.isSaving,
      isDeleting: isDeleting ?? this.isDeleting,
      isRefreshing: isRefreshing ?? this.isRefreshing,
      error: clearError ? null : (error ?? this.error),
      selectedField:
          clearSelectedField ? null : (selectedField ?? this.selectedField),
      fields: fields ?? this.fields,
      unsyncedCount: unsyncedCount ?? this.unsyncedCount,
    );
  }

  /// Check if any operation is in progress
  bool get isBusy => isLoading || isSaving || isDeleting || isRefreshing;

  /// Fields that need attention (stressed or critical)
  List<Field> get fieldsNeedingAttention =>
      fields.where((f) => f.needsAttention).toList();

  /// Critical fields only
  List<Field> get criticalFields => fields.where((f) => f.isCritical).toList();

  /// Total area in hectares
  double get totalAreaHectares =>
      fields.fold(0.0, (sum, f) => sum + f.areaHectares);

  /// Average NDVI
  double get averageNdvi {
    final fieldsWithNdvi = fields.where((f) => f.ndviCurrent != null).toList();
    if (fieldsWithNdvi.isEmpty) return 0.0;
    return fieldsWithNdvi.fold(0.0, (sum, f) => sum + f.ndvi) /
        fieldsWithNdvi.length;
  }
}

/// Field Controller - Manages field operations
class FieldController extends StateNotifier<FieldControllerState> {
  final FieldsRepo _repo;
  final String _tenantId;

  FieldController({
    required FieldsRepo repo,
    required String tenantId,
  })  : _repo = repo,
        _tenantId = tenantId,
        super(const FieldControllerState()) {
    _init();
  }

  /// Initialize controller - load fields
  Future<void> _init() async {
    await loadFields();
  }

  /// Load all fields for the tenant
  Future<void> loadFields() async {
    state = state.copyWith(isLoading: true, clearError: true);

    try {
      final fields = await _repo.getAllFields(_tenantId);
      final unsynced = await _repo.getUnsyncedFields();

      state = state.copyWith(
        isLoading: false,
        fields: fields,
        unsyncedCount: unsynced.length,
      );

      AppLogger.i('Fields loaded', tag: 'FieldController', data: {
        'count': fields.length,
        'unsynced': unsynced.length,
      });
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل الحقول: $e',
      );
      AppLogger.e('Failed to load fields', tag: 'FieldController', error: e);
    }
  }

  /// Refresh fields from server
  Future<void> refreshFromServer() async {
    state = state.copyWith(isRefreshing: true, clearError: true);

    try {
      final count = await _repo.refreshFromServer(_tenantId);
      await loadFields(); // Reload local data

      state = state.copyWith(isRefreshing: false);

      AppLogger.i('Fields refreshed from server',
          tag: 'FieldController',
          data: {
            'synced': count,
          });
    } catch (e) {
      state = state.copyWith(
        isRefreshing: false,
        error: 'فشل تحديث الحقول من السيرفر: $e',
      );
      AppLogger.e('Failed to refresh fields', tag: 'FieldController', error: e);
    }
  }

  /// Create a new field
  Future<Field?> createField({
    required String name,
    required List<LatLng> boundary,
    String? cropType,
    String? farmId,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      final field = await _repo.createField(
        tenantId: _tenantId,
        name: name,
        boundary: boundary,
        cropType: cropType,
        farmId: farmId,
      );

      // Reload fields
      await loadFields();

      state = state.copyWith(
        isSaving: false,
        selectedField: field,
      );

      AppLogger.i('Field created', tag: 'FieldController', data: {
        'id': field.id,
        'name': field.name,
        'area': field.areaHectares.toStringAsFixed(2),
      });

      return field;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        error: 'فشل إنشاء الحقل: $e',
      );
      AppLogger.e('Failed to create field', tag: 'FieldController', error: e);
      return null;
    }
  }

  /// Update field boundary
  Future<bool> updateFieldBoundary({
    required String fieldId,
    required List<LatLng> newBoundary,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repo.updateFieldBoundary(
        fieldId: fieldId,
        newBoundary: newBoundary,
      );

      // Reload fields
      await loadFields();

      // Update selected field if it was the one being edited
      if (state.selectedField?.id == fieldId) {
        final updatedField = await _repo.getFieldById(fieldId);
        if (updatedField != null) {
          state = state.copyWith(selectedField: updatedField);
        }
      }

      state = state.copyWith(isSaving: false);

      AppLogger.i('Field boundary updated', tag: 'FieldController', data: {
        'fieldId': fieldId,
      });

      return true;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        error: 'فشل تحديث حدود الحقل: $e',
      );
      AppLogger.e('Failed to update field boundary',
          tag: 'FieldController', error: e);
      return false;
    }
  }

  /// Update field properties
  Future<bool> updateFieldProperties({
    required String fieldId,
    String? name,
    String? cropType,
    String? status,
  }) async {
    state = state.copyWith(isSaving: true, clearError: true);

    try {
      await _repo.updateFieldProperties(
        fieldId: fieldId,
        name: name,
        cropType: cropType,
        status: status,
      );

      // Reload fields
      await loadFields();

      // Update selected field if it was the one being edited
      if (state.selectedField?.id == fieldId) {
        final updatedField = await _repo.getFieldById(fieldId);
        if (updatedField != null) {
          state = state.copyWith(selectedField: updatedField);
        }
      }

      state = state.copyWith(isSaving: false);

      AppLogger.i('Field properties updated', tag: 'FieldController', data: {
        'fieldId': fieldId,
      });

      return true;
    } catch (e) {
      state = state.copyWith(
        isSaving: false,
        error: 'فشل تحديث بيانات الحقل: $e',
      );
      AppLogger.e('Failed to update field properties',
          tag: 'FieldController', error: e);
      return false;
    }
  }

  /// Delete field (soft delete)
  Future<bool> deleteField(String fieldId) async {
    state = state.copyWith(isDeleting: true, clearError: true);

    try {
      await _repo.deleteField(fieldId);

      // Clear selected field if it was deleted
      if (state.selectedField?.id == fieldId) {
        state = state.copyWith(clearSelectedField: true);
      }

      // Reload fields
      await loadFields();

      state = state.copyWith(isDeleting: false);

      AppLogger.i('Field deleted', tag: 'FieldController', data: {
        'fieldId': fieldId,
      });

      return true;
    } catch (e) {
      state = state.copyWith(
        isDeleting: false,
        error: 'فشل حذف الحقل: $e',
      );
      AppLogger.e('Failed to delete field', tag: 'FieldController', error: e);
      return false;
    }
  }

  /// Select a field
  void selectField(Field? field) {
    state = state.copyWith(
      selectedField: field,
      clearSelectedField: field == null,
    );
  }

  /// Select field by ID
  Future<void> selectFieldById(String fieldId) async {
    final field = await _repo.getFieldById(fieldId);
    selectField(field);
  }

  /// Clear error
  void clearError() {
    state = state.copyWith(clearError: true);
  }

  /// Get field by ID from local state
  Field? getFieldById(String fieldId) {
    try {
      return state.fields.firstWhere((f) => f.id == fieldId);
    } catch (e) {
      return null;
    }
  }

  /// Filter fields by status
  List<Field> filterByStatus(FieldStatus status) {
    return state.fields.where((f) => f.healthStatus == status).toList();
  }

  /// Filter fields by crop type
  List<Field> filterByCropType(String cropType) {
    return state.fields.where((f) => f.cropType == cropType).toList();
  }

  /// Search fields by name
  List<Field> searchByName(String query) {
    if (query.isEmpty) return state.fields;
    final lowerQuery = query.toLowerCase();
    return state.fields
        .where((f) => f.name.toLowerCase().contains(lowerQuery))
        .toList();
  }
}

/// Field Controller Provider
/// Creates a FieldController scoped to a tenant
/// Uses autoDispose with keepAlive for critical field data
/// Stays alive for 15 minutes after last use since fields are core data
final fieldControllerProvider = StateNotifierProvider.autoDispose
    .family<FieldController, FieldControllerState, String>((ref, tenantId) {
  final repo = ref.watch(fieldsRepoProvider);

  // Keep alive for 15 minutes - fields are critical app data
  final link = ref.keepAlive();
  final timer = Timer(const Duration(minutes: 15), link.close);
  ref.onDispose(timer.cancel);

  return FieldController(repo: repo, tenantId: tenantId);
});

/// Selected Field Provider - autoDispose to match parent
/// Convenience provider to get the currently selected field
final selectedFieldProvider =
    Provider.autoDispose.family<Field?, String>((ref, tenantId) {
  final state = ref.watch(fieldControllerProvider(tenantId));
  return state.selectedField;
});

/// Fields Needing Attention Provider - autoDispose to match parent
final fieldsNeedingAttentionProvider =
    Provider.autoDispose.family<List<Field>, String>((ref, tenantId) {
  final state = ref.watch(fieldControllerProvider(tenantId));
  return state.fieldsNeedingAttention;
});

/// Critical Fields Provider - autoDispose to match parent
final criticalFieldsProvider =
    Provider.autoDispose.family<List<Field>, String>((ref, tenantId) {
  final state = ref.watch(fieldControllerProvider(tenantId));
  return state.criticalFields;
});

/// Field Statistics Provider - autoDispose to match parent
final fieldStatsProvider =
    Provider.autoDispose.family<FieldStats, String>((ref, tenantId) {
  final state = ref.watch(fieldControllerProvider(tenantId));
  return FieldStats(
    totalFields: state.fields.length,
    totalAreaHectares: state.totalAreaHectares,
    averageNdvi: state.averageNdvi,
    unsyncedCount: state.unsyncedCount,
    criticalCount: state.criticalFields.length,
    needsAttentionCount: state.fieldsNeedingAttention.length,
  );
});

/// Field statistics data class
class FieldStats {
  final int totalFields;
  final double totalAreaHectares;
  final double averageNdvi;
  final int unsyncedCount;
  final int criticalCount;
  final int needsAttentionCount;

  const FieldStats({
    required this.totalFields,
    required this.totalAreaHectares,
    required this.averageNdvi,
    required this.unsyncedCount,
    required this.criticalCount,
    required this.needsAttentionCount,
  });
}

/// Field Loading State Provider - convenient access to loading state
final fieldLoadingProvider =
    Provider.autoDispose.family<bool, String>((ref, tenantId) {
  return ref.watch(fieldControllerProvider(tenantId)).isLoading;
});

/// Field Error State Provider - convenient access to error state
final fieldErrorProvider =
    Provider.autoDispose.family<String?, String>((ref, tenantId) {
  return ref.watch(fieldControllerProvider(tenantId)).error;
});

/// Field Is Busy Provider - check if any operation is in progress
final fieldIsBusyProvider =
    Provider.autoDispose.family<bool, String>((ref, tenantId) {
  return ref.watch(fieldControllerProvider(tenantId)).isBusy;
});
