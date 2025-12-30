import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'permission_service.dart';

/// SAHOOL Runtime Permission Providers
/// مزودات حالة صلاحيات النظام
///
/// Riverpod providers for managing runtime permissions state

// ═══════════════════════════════════════════════════════════════════════════
// Permission Service Provider
// ═══════════════════════════════════════════════════════════════════════════

/// Provides singleton instance of PermissionService
final permissionServiceProvider = Provider<PermissionService>((ref) {
  return PermissionService();
});

// ═══════════════════════════════════════════════════════════════════════════
// Permission Status Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Location permission status provider
final locationPermissionStatusProvider =
    FutureProvider<PermissionStatus>((ref) async {
  final service = ref.watch(permissionServiceProvider);
  return await service.checkLocationPermission();
});

/// Camera permission status provider
final cameraPermissionStatusProvider =
    FutureProvider<PermissionStatus>((ref) async {
  final service = ref.watch(permissionServiceProvider);
  return await service.checkCameraPermission();
});

/// Storage permission status provider
final storagePermissionStatusProvider =
    FutureProvider<PermissionStatus>((ref) async {
  final service = ref.watch(permissionServiceProvider);
  return await service.checkStoragePermission();
});

/// Notification permission status provider
final notificationPermissionStatusProvider =
    FutureProvider<PermissionStatus>((ref) async {
  final service = ref.watch(permissionServiceProvider);
  return await service.checkNotificationPermission();
});

/// All permissions status provider
final allPermissionsStatusProvider =
    FutureProvider<Map<PermissionType, PermissionStatus>>((ref) async {
  final service = ref.watch(permissionServiceProvider);
  return await service.checkAllPermissions();
});

// ═══════════════════════════════════════════════════════════════════════════
// Permission State Notifiers
// ═══════════════════════════════════════════════════════════════════════════

/// State class for permission status
class PermissionState {
  final Map<PermissionType, PermissionStatus> permissions;
  final bool isLoading;
  final String? error;

  const PermissionState({
    this.permissions = const {},
    this.isLoading = false,
    this.error,
  });

  PermissionState copyWith({
    Map<PermissionType, PermissionStatus>? permissions,
    bool? isLoading,
    String? error,
  }) {
    return PermissionState(
      permissions: permissions ?? this.permissions,
      isLoading: isLoading ?? this.isLoading,
      error: error ?? this.error,
    );
  }

  /// Check if all required permissions are granted
  bool get hasAllPermissions {
    return permissions.values.every((status) => status.isGranted);
  }

  /// Check if specific permission is granted
  bool isGranted(PermissionType type) {
    return permissions[type]?.isGranted ?? false;
  }

  /// Get list of denied permissions
  List<PermissionType> get deniedPermissions {
    return permissions.entries
        .where((entry) => !entry.value.isGranted)
        .map((entry) => entry.key)
        .toList();
  }

  /// Get list of permanently denied permissions
  List<PermissionType> get permanentlyDeniedPermissions {
    return permissions.entries
        .where((entry) => entry.value.isPermanentlyDenied)
        .map((entry) => entry.key)
        .toList();
  }
}

/// Permission state notifier
class PermissionStateNotifier extends StateNotifier<PermissionState> {
  final PermissionService _service;

  PermissionStateNotifier(this._service) : super(const PermissionState()) {
    // Load initial permissions on creation
    _loadPermissions();
  }

  /// Load all permissions status
  Future<void> _loadPermissions() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final permissions = await _service.checkAllPermissions();
      state = state.copyWith(
        permissions: permissions,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: 'فشل تحميل حالة الصلاحيات: $e',
      );
    }
  }

  /// Refresh permissions status
  Future<void> refresh() async {
    await _loadPermissions();
  }

  /// Update single permission status
  void updatePermission(PermissionType type, PermissionStatus status) {
    final updatedPermissions = Map<PermissionType, PermissionStatus>.from(
      state.permissions,
    );
    updatedPermissions[type] = status;

    state = state.copyWith(permissions: updatedPermissions);
  }

  /// Update multiple permissions
  void updatePermissions(Map<PermissionType, PermissionStatus> permissions) {
    final updatedPermissions = Map<PermissionType, PermissionStatus>.from(
      state.permissions,
    );
    updatedPermissions.addAll(permissions);

    state = state.copyWith(permissions: updatedPermissions);
  }
}

/// Permission state provider
final permissionStateProvider =
    StateNotifierProvider<PermissionStateNotifier, PermissionState>((ref) {
  final service = ref.watch(permissionServiceProvider);
  return PermissionStateNotifier(service);
});

// ═══════════════════════════════════════════════════════════════════════════
// Derived Providers (Computed State)
// ═══════════════════════════════════════════════════════════════════════════

/// Check if location permission is granted
final hasLocationPermissionProvider = Provider<bool>((ref) {
  final state = ref.watch(permissionStateProvider);
  return state.isGranted(PermissionType.location);
});

/// Check if camera permission is granted
final hasCameraPermissionProvider = Provider<bool>((ref) {
  final state = ref.watch(permissionStateProvider);
  return state.isGranted(PermissionType.camera);
});

/// Check if storage permission is granted
final hasStoragePermissionProvider = Provider<bool>((ref) {
  final state = ref.watch(permissionStateProvider);
  return state.isGranted(PermissionType.storage);
});

/// Check if notification permission is granted
final hasNotificationPermissionProvider = Provider<bool>((ref) {
  final state = ref.watch(permissionStateProvider);
  return state.isGranted(PermissionType.notification);
});

/// Check if all field operations permissions are granted
/// (Location, Camera, Storage)
final hasFieldOperationsPermissionsProvider = Provider<bool>((ref) {
  final state = ref.watch(permissionStateProvider);
  return state.isGranted(PermissionType.location) &&
      state.isGranted(PermissionType.camera) &&
      state.isGranted(PermissionType.storage);
});

/// Get list of missing permissions for field operations
final missingFieldOperationsPermissionsProvider =
    Provider<List<PermissionType>>((ref) {
  final state = ref.watch(permissionStateProvider);
  final required = [
    PermissionType.location,
    PermissionType.camera,
    PermissionType.storage,
  ];

  return required.where((type) => !state.isGranted(type)).toList();
});

// ═══════════════════════════════════════════════════════════════════════════
// Permission Request Controllers
// ═══════════════════════════════════════════════════════════════════════════

/// Controller for permission requests
class PermissionController {
  final Ref _ref;

  PermissionController(this._ref);

  PermissionService get _service => _ref.read(permissionServiceProvider);
  PermissionStateNotifier get _notifier =>
      _ref.read(permissionStateProvider.notifier);

  /// Request location permission
  Future<bool> requestLocation() async {
    final granted = await _service.requestLocationPermission();
    final status =
        granted ? PermissionStatus.granted : PermissionStatus.denied;
    _notifier.updatePermission(PermissionType.location, status);
    return granted;
  }

  /// Request camera permission
  Future<bool> requestCamera() async {
    final granted = await _service.requestCameraPermission();
    final status =
        granted ? PermissionStatus.granted : PermissionStatus.denied;
    _notifier.updatePermission(PermissionType.camera, status);
    return granted;
  }

  /// Request storage permission
  Future<bool> requestStorage() async {
    final granted = await _service.requestStoragePermission();
    final status =
        granted ? PermissionStatus.granted : PermissionStatus.denied;
    _notifier.updatePermission(PermissionType.storage, status);
    return granted;
  }

  /// Request notification permission
  Future<bool> requestNotification() async {
    final granted = await _service.requestNotificationPermission();
    final status =
        granted ? PermissionStatus.granted : PermissionStatus.denied;
    _notifier.updatePermission(PermissionType.notification, status);
    return granted;
  }

  /// Request all field operations permissions
  Future<Map<PermissionType, bool>> requestFieldOperationsPermissions() async {
    final results = await _service.requestFieldOperationsPermissions();

    // Update state for each permission
    for (final entry in results.entries) {
      final status =
          entry.value ? PermissionStatus.granted : PermissionStatus.denied;
      _notifier.updatePermission(entry.key, status);
    }

    return results;
  }

  /// Request all permissions
  Future<Map<PermissionType, bool>> requestAllPermissions() async {
    final results = await _service.requestAllPermissions();

    // Update state for each permission
    for (final entry in results.entries) {
      final status =
          entry.value ? PermissionStatus.granted : PermissionStatus.denied;
      _notifier.updatePermission(entry.key, status);
    }

    return results;
  }

  /// Open app settings
  Future<bool> openSettings() async {
    return await _service.openSettings();
  }

  /// Refresh permissions status
  Future<void> refresh() async {
    await _notifier.refresh();
  }
}

/// Permission controller provider
final permissionControllerProvider = Provider<PermissionController>((ref) {
  return PermissionController(ref);
});

// ═══════════════════════════════════════════════════════════════════════════
// Helper Extensions
// ═══════════════════════════════════════════════════════════════════════════

/// Extension on WidgetRef for easy permission access
extension PermissionRefExtension on WidgetRef {
  /// Get permission controller
  PermissionController get permissions => read(permissionControllerProvider);

  /// Get permission state
  PermissionState get permissionState => read(permissionStateProvider);

  /// Check if permission is granted
  bool hasPermission(PermissionType type) {
    return permissionState.isGranted(type);
  }

  /// Check if all field operations permissions are granted
  bool get hasFieldOperationsPermissions {
    return read(hasFieldOperationsPermissionsProvider);
  }
}
