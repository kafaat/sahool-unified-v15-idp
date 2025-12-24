import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'auth_service.dart';

/// SAHOOL Permission Service
/// خدمة الصلاحيات مع دعم العمل بدون اتصال
///
/// Features:
/// - RBAC (Role-Based Access Control)
/// - ABAC (Attribute-Based Access Control)
/// - Offline Capability Tokens
/// - Context-aware permissions (Field, Farm, Task)

// ═══════════════════════════════════════════════════════════════════════════
// Permission Definitions
// تعريفات الصلاحيات
// ═══════════════════════════════════════════════════════════════════════════

/// All permissions in SAHOOL
class Permission {
  // FieldOps - عمليات الحقل
  static const fieldView = 'fieldops:field.view';
  static const fieldCreate = 'fieldops:field.create';
  static const fieldEdit = 'fieldops:field.edit';
  static const fieldDelete = 'fieldops:field.delete';

  // Tasks - المهام
  static const taskView = 'fieldops:task.view';
  static const taskCreate = 'fieldops:task.create';
  static const taskEdit = 'fieldops:task.edit';
  static const taskDelete = 'fieldops:task.delete';
  static const taskAssign = 'fieldops:task.assign';
  static const taskExecute = 'fieldops:task.execute';
  static const taskComplete = 'fieldops:task.complete';

  // NDVI - مؤشر النبات
  static const ndviView = 'ndvi:view';
  static const ndviCompute = 'ndvi:compute';
  static const ndviExport = 'ndvi:export';

  // Weather - الطقس
  static const weatherView = 'weather:view';

  // IoT - أجهزة الاستشعار
  static const iotView = 'iot:device.view';
  static const iotManage = 'iot:device.manage';
  static const sensorView = 'iot:sensor.view';

  // Irrigation - الري
  static const irrigationView = 'irrigation:view';
  static const irrigationControl = 'irrigation:control';

  // Reports - التقارير
  static const reportView = 'reports:view';
  static const reportExport = 'reports:export';

  // Chat - المحادثات
  static const chatRead = 'chat:read';
  static const chatWrite = 'chat:write';

  // Admin - الإدارة
  static const userView = 'admin:users.view';
  static const userManage = 'admin:users.manage';
  static const tenantManage = 'admin:tenant.manage';
  static const auditView = 'admin:audit.view';

  // Billing - الفوترة
  static const billingView = 'billing:view';
  static const billingManage = 'billing:manage';

  // Offline-specific - خاص بالعمل بدون اتصال
  static const offlineSync = 'offline:sync';
  static const offlinePhotoUpload = 'offline:photo.upload';
}

// ═══════════════════════════════════════════════════════════════════════════
// Role Definitions
// تعريفات الأدوار
// ═══════════════════════════════════════════════════════════════════════════

/// System roles
enum UserRole {
  viewer('viewer', 'مشاهد'),
  worker('worker', 'عامل ميداني'),
  supervisor('supervisor', 'مشرف'),
  manager('manager', 'مدير'),
  admin('admin', 'مسؤول'),
  superAdmin('super_admin', 'مسؤول النظام');

  final String value;
  final String arabicLabel;

  const UserRole(this.value, this.arabicLabel);

  static UserRole fromString(String value) {
    return UserRole.values.firstWhere(
      (r) => r.value == value,
      orElse: () => UserRole.viewer,
    );
  }
}

/// Role to Permissions mapping
final Map<UserRole, Set<String>> rolePermissions = {
  // Viewer - مشاهد (قراءة فقط)
  UserRole.viewer: {
    Permission.fieldView,
    Permission.taskView,
    Permission.ndviView,
    Permission.weatherView,
    Permission.iotView,
    Permission.sensorView,
    Permission.irrigationView,
    Permission.reportView,
    Permission.chatRead,
  },

  // Worker - عامل ميداني
  UserRole.worker: {
    // All viewer permissions
    Permission.fieldView,
    Permission.taskView,
    Permission.ndviView,
    Permission.weatherView,
    Permission.iotView,
    Permission.sensorView,
    Permission.irrigationView,
    Permission.reportView,
    Permission.chatRead,
    // Worker-specific
    Permission.taskEdit,
    Permission.taskExecute,
    Permission.taskComplete,
    Permission.chatWrite,
    Permission.offlineSync,
    Permission.offlinePhotoUpload,
  },

  // Supervisor - مشرف
  UserRole.supervisor: {
    // All worker permissions
    Permission.fieldView,
    Permission.taskView,
    Permission.taskEdit,
    Permission.taskExecute,
    Permission.taskComplete,
    Permission.ndviView,
    Permission.weatherView,
    Permission.iotView,
    Permission.sensorView,
    Permission.irrigationView,
    Permission.irrigationControl,
    Permission.reportView,
    Permission.chatRead,
    Permission.chatWrite,
    Permission.offlineSync,
    Permission.offlinePhotoUpload,
    // Supervisor-specific
    Permission.taskCreate,
    Permission.taskAssign,
    Permission.fieldEdit,
  },

  // Manager - مدير
  UserRole.manager: {
    // All supervisor permissions plus
    Permission.fieldView,
    Permission.fieldCreate,
    Permission.fieldEdit,
    Permission.fieldDelete,
    Permission.taskView,
    Permission.taskCreate,
    Permission.taskEdit,
    Permission.taskDelete,
    Permission.taskAssign,
    Permission.taskExecute,
    Permission.taskComplete,
    Permission.ndviView,
    Permission.ndviCompute,
    Permission.ndviExport,
    Permission.weatherView,
    Permission.iotView,
    Permission.iotManage,
    Permission.sensorView,
    Permission.irrigationView,
    Permission.irrigationControl,
    Permission.reportView,
    Permission.reportExport,
    Permission.chatRead,
    Permission.chatWrite,
    Permission.userView,
    Permission.offlineSync,
    Permission.offlinePhotoUpload,
  },

  // Admin - مسؤول
  UserRole.admin: {
    // All manager permissions plus admin
    Permission.fieldView,
    Permission.fieldCreate,
    Permission.fieldEdit,
    Permission.fieldDelete,
    Permission.taskView,
    Permission.taskCreate,
    Permission.taskEdit,
    Permission.taskDelete,
    Permission.taskAssign,
    Permission.taskExecute,
    Permission.taskComplete,
    Permission.ndviView,
    Permission.ndviCompute,
    Permission.ndviExport,
    Permission.weatherView,
    Permission.iotView,
    Permission.iotManage,
    Permission.sensorView,
    Permission.irrigationView,
    Permission.irrigationControl,
    Permission.reportView,
    Permission.reportExport,
    Permission.chatRead,
    Permission.chatWrite,
    Permission.userView,
    Permission.userManage,
    Permission.billingView,
    Permission.billingManage,
    Permission.auditView,
    Permission.offlineSync,
    Permission.offlinePhotoUpload,
  },

  // Super Admin - مسؤول النظام
  UserRole.superAdmin: {
    // Everything
    Permission.fieldView,
    Permission.fieldCreate,
    Permission.fieldEdit,
    Permission.fieldDelete,
    Permission.taskView,
    Permission.taskCreate,
    Permission.taskEdit,
    Permission.taskDelete,
    Permission.taskAssign,
    Permission.taskExecute,
    Permission.taskComplete,
    Permission.ndviView,
    Permission.ndviCompute,
    Permission.ndviExport,
    Permission.weatherView,
    Permission.iotView,
    Permission.iotManage,
    Permission.sensorView,
    Permission.irrigationView,
    Permission.irrigationControl,
    Permission.reportView,
    Permission.reportExport,
    Permission.chatRead,
    Permission.chatWrite,
    Permission.userView,
    Permission.userManage,
    Permission.tenantManage,
    Permission.billingView,
    Permission.billingManage,
    Permission.auditView,
    Permission.offlineSync,
    Permission.offlinePhotoUpload,
  },
};

// ═══════════════════════════════════════════════════════════════════════════
// Capability Token (للعمل بدون اتصال)
// ═══════════════════════════════════════════════════════════════════════════

/// Offline capability token
class CapabilityToken {
  final String userId;
  final String tenantId;
  final UserRole role;
  final Set<String> capabilities;
  final List<String> assignedFieldIds;
  final List<String> assignedFarmIds;
  final DateTime expiresAt;
  final DateTime issuedAt;

  const CapabilityToken({
    required this.userId,
    required this.tenantId,
    required this.role,
    required this.capabilities,
    this.assignedFieldIds = const [],
    this.assignedFarmIds = const [],
    required this.expiresAt,
    required this.issuedAt,
  });

  bool get isExpired => DateTime.now().isAfter(expiresAt);

  bool get isValid => !isExpired;

  /// Check if user can access a specific field
  bool canAccessField(String fieldId) {
    // Super admin and admin can access all
    if (role == UserRole.superAdmin || role == UserRole.admin) {
      return true;
    }
    // Others need explicit assignment
    return assignedFieldIds.contains(fieldId);
  }

  /// Check if user can access a specific farm
  bool canAccessFarm(String farmId) {
    if (role == UserRole.superAdmin || role == UserRole.admin) {
      return true;
    }
    return assignedFarmIds.contains(farmId);
  }

  factory CapabilityToken.fromJson(Map<String, dynamic> json) {
    return CapabilityToken(
      userId: json['user_id'] as String,
      tenantId: json['tenant_id'] as String,
      role: UserRole.fromString(json['role'] as String),
      capabilities: Set<String>.from(json['capabilities'] as List),
      assignedFieldIds: List<String>.from(json['assigned_field_ids'] ?? []),
      assignedFarmIds: List<String>.from(json['assigned_farm_ids'] ?? []),
      expiresAt: DateTime.parse(json['expires_at'] as String),
      issuedAt: DateTime.parse(json['issued_at'] as String),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'tenant_id': tenantId,
      'role': role.value,
      'capabilities': capabilities.toList(),
      'assigned_field_ids': assignedFieldIds,
      'assigned_farm_ids': assignedFarmIds,
      'expires_at': expiresAt.toIso8601String(),
      'issued_at': issuedAt.toIso8601String(),
    };
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Permission Service
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for PermissionService
final permissionServiceProvider = Provider<PermissionService>((ref) {
  final authState = ref.watch(authStateProvider);
  return PermissionService(user: authState.user);
});

/// Permission checking service
class PermissionService {
  final User? user;
  CapabilityToken? _capabilityToken;

  PermissionService({this.user});

  /// Set offline capability token
  void setCapabilityToken(CapabilityToken token) {
    _capabilityToken = token;
  }

  /// Get current role
  UserRole get currentRole {
    if (user == null) return UserRole.viewer;
    return UserRole.fromString(user!.role);
  }

  /// Get all permissions for current user
  Set<String> get permissions {
    // If we have a capability token, use it (offline mode)
    if (_capabilityToken != null && _capabilityToken!.isValid) {
      return _capabilityToken!.capabilities;
    }
    // Otherwise, use role-based permissions
    return rolePermissions[currentRole] ?? {};
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Permission Checking
  // ─────────────────────────────────────────────────────────────────────────

  /// Check if user has a specific permission
  bool can(String permission) {
    if (user == null) return false;

    // Super admin has all permissions
    if (currentRole == UserRole.superAdmin) return true;

    return permissions.contains(permission);
  }

  /// Check if user has any of the specified permissions
  bool canAny(List<String> permissionList) {
    return permissionList.any((p) => can(p));
  }

  /// Check if user has all of the specified permissions
  bool canAll(List<String> permissionList) {
    return permissionList.every((p) => can(p));
  }

  /// Check if user has a specific role
  bool hasRole(UserRole role) {
    return currentRole == role;
  }

  /// Check if user has any of the specified roles
  bool hasAnyRole(List<UserRole> roles) {
    return roles.contains(currentRole);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // ABAC (Attribute-Based Access Control)
  // ─────────────────────────────────────────────────────────────────────────

  /// Check if user can access a specific field
  bool canAccessField(String fieldId, String permission) {
    if (!can(permission)) return false;

    // Use capability token if available
    if (_capabilityToken != null) {
      return _capabilityToken!.canAccessField(fieldId);
    }

    // Default to true if online (server will validate)
    return true;
  }

  /// Check if user can execute a task
  bool canExecuteTask({
    required String taskId,
    required String? assignedTo,
    required bool requiresApproval,
    required bool isOffline,
  }) {
    // Must have task.execute permission
    if (!can(Permission.taskExecute)) return false;

    // Check assignment
    if (assignedTo != null && assignedTo != user?.id) {
      // Supervisors and above can execute any task
      if (!hasAnyRole([
        UserRole.supervisor,
        UserRole.manager,
        UserRole.admin,
        UserRole.superAdmin,
      ])) {
        return false;
      }
    }

    // Check offline restrictions
    if (isOffline && requiresApproval) {
      // Tasks requiring approval cannot be executed offline
      return false;
    }

    return true;
  }

  /// Check if user can assign tasks to others
  bool canAssignTask() {
    return can(Permission.taskAssign);
  }

  /// Check if user can manage IoT devices
  bool canManageIoT() {
    return can(Permission.iotManage);
  }

  /// Check if user can control irrigation
  bool canControlIrrigation() {
    return can(Permission.irrigationControl);
  }

  /// Check if user can export reports
  bool canExportReports() {
    return can(Permission.reportExport);
  }

  /// Check if user can manage billing
  bool canManageBilling() {
    return can(Permission.billingManage);
  }

  /// Check if user is admin or higher
  bool get isAdmin {
    return hasAnyRole([UserRole.admin, UserRole.superAdmin]);
  }

  /// Check if user is manager or higher
  bool get isManager {
    return hasAnyRole([
      UserRole.manager,
      UserRole.admin,
      UserRole.superAdmin,
    ]);
  }

  /// Check if user is supervisor or higher
  bool get isSupervisor {
    return hasAnyRole([
      UserRole.supervisor,
      UserRole.manager,
      UserRole.admin,
      UserRole.superAdmin,
    ]);
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Permission Helper Extension
// ═══════════════════════════════════════════════════════════════════════════

/// Extension on WidgetRef for easy permission checking
extension PermissionRefExtension on WidgetRef {
  /// Get permission service
  PermissionService get permissions => read(permissionServiceProvider);

  /// Check if user can perform action
  bool can(String permission) => permissions.can(permission);

  /// Check if user has role
  bool hasRole(UserRole role) => permissions.hasRole(role);
}
