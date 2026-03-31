// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL RBAC - Service
// نظام التحكم في الوصول المبني على الأدوار - الخدمة
// ═══════════════════════════════════════════════════════════════════════════
//
// This service provides role and permission checking functionality.
// Supports online and offline modes with capability tokens.
//
// هذه الخدمة توفر وظائف التحقق من الأدوار والصلاحيات.
// تدعم الوضع المتصل وغير المتصل مع رموز القدرات.

import 'package:flutter/material.dart';
import 'role_model.dart';
import 'permission_model.dart';
import 'rbac_config.dart';

/// User information for RBAC
/// معلومات المستخدم للتحكم في الوصول
class RbacUser {
  /// User ID
  final String id;

  /// User's role
  final Role role;

  /// Tenant ID
  final String? tenantId;

  /// Assigned field IDs (for ABAC)
  final List<String> assignedFieldIds;

  /// Assigned farm IDs (for ABAC)
  final List<String> assignedFarmIds;

  /// Custom permissions (in addition to role permissions)
  final Set<Permission> customPermissions;

  /// Denied permissions (override role permissions)
  final Set<Permission> deniedPermissions;

  const RbacUser({
    required this.id,
    required this.role,
    this.tenantId,
    this.assignedFieldIds = const [],
    this.assignedFarmIds = const [],
    this.customPermissions = const {},
    this.deniedPermissions = const {},
  });

  /// Create from JSON
  factory RbacUser.fromJson(Map<String, dynamic> json) {
    return RbacUser(
      id: json['id'] as String,
      role: Role.fromString(json['role'] as String? ?? 'guest'),
      tenantId: json['tenant_id'] as String?,
      assignedFieldIds: List<String>.from((json['assigned_field_ids'] ?? []) as Iterable),
      assignedFarmIds: List<String>.from((json['assigned_farm_ids'] ?? []) as Iterable),
      customPermissions: (json['custom_permissions'] as List?)
              ?.map((p) => Permissions.findById(p as String))
              .whereType<Permission>()
              .toSet() ??
          {},
      deniedPermissions: (json['denied_permissions'] as List?)
              ?.map((p) => Permissions.findById(p as String))
              .whereType<Permission>()
              .toSet() ??
          {},
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'role': role.value,
        'tenant_id': tenantId,
        'assigned_field_ids': assignedFieldIds,
        'assigned_farm_ids': assignedFarmIds,
        'custom_permissions': customPermissions.map((p) => p.id).toList(),
        'denied_permissions': deniedPermissions.map((p) => p.id).toList(),
      };

  /// Create a copy with modifications
  RbacUser copyWith({
    String? id,
    Role? role,
    String? tenantId,
    List<String>? assignedFieldIds,
    List<String>? assignedFarmIds,
    Set<Permission>? customPermissions,
    Set<Permission>? deniedPermissions,
  }) {
    return RbacUser(
      id: id ?? this.id,
      role: role ?? this.role,
      tenantId: tenantId ?? this.tenantId,
      assignedFieldIds: assignedFieldIds ?? this.assignedFieldIds,
      assignedFarmIds: assignedFarmIds ?? this.assignedFarmIds,
      customPermissions: customPermissions ?? this.customPermissions,
      deniedPermissions: deniedPermissions ?? this.deniedPermissions,
    );
  }

  /// Guest user
  static const guest = RbacUser(
    id: 'guest',
    role: Role.guest,
  );
}

/// Offline capability token
/// رمز القدرات للعمل دون اتصال
class CapabilityToken {
  /// User ID
  final String userId;

  /// Tenant ID
  final String tenantId;

  /// User role
  final Role role;

  /// Granted capabilities (permission IDs)
  final Set<String> capabilities;

  /// Assigned field IDs
  final List<String> assignedFieldIds;

  /// Assigned farm IDs
  final List<String> assignedFarmIds;

  /// Token expiration time
  final DateTime expiresAt;

  /// Token issue time
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

  /// Check if token is expired
  bool get isExpired => DateTime.now().isAfter(expiresAt);

  /// Check if token is valid
  bool get isValid => !isExpired;

  /// Remaining validity duration
  Duration get remainingValidity => expiresAt.difference(DateTime.now());

  /// Create from JSON
  factory CapabilityToken.fromJson(Map<String, dynamic> json) {
    return CapabilityToken(
      userId: json['user_id'] as String,
      tenantId: json['tenant_id'] as String,
      role: Role.fromString(json['role'] as String),
      capabilities: Set<String>.from(json['capabilities'] as List? ?? []),
      assignedFieldIds: List<String>.from((json['assigned_field_ids'] ?? []) as Iterable),
      assignedFarmIds: List<String>.from((json['assigned_farm_ids'] ?? []) as Iterable),
      expiresAt: DateTime.tryParse(json['expires_at'] as String) ?? DateTime.now(),
      issuedAt: DateTime.tryParse(json['issued_at'] as String) ?? DateTime.now(),
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
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

/// RBAC Service for checking roles and permissions
/// خدمة التحكم في الوصول للتحقق من الأدوار والصلاحيات
class RbacService {
  /// Current user
  final RbacUser? user;

  /// RBAC configuration
  final RbacConfig config;

  /// Offline capability token
  CapabilityToken? _capabilityToken;

  /// Current environment
  final String environment;

  /// Whether the device is offline
  final bool isOffline;

  RbacService({
    this.user,
    RbacConfig? config,
    this.environment = 'production',
    this.isOffline = false,
  }) : config = config ?? DefaultRbacConfig.instance;

  // ─────────────────────────────────────────────────────────────────────────
  // Capability Token Management
  // ─────────────────────────────────────────────────────────────────────────

  /// Set offline capability token
  void setCapabilityToken(CapabilityToken? token) {
    _capabilityToken = token;
  }

  /// Get current capability token
  CapabilityToken? get capabilityToken => _capabilityToken;

  /// Check if capability token is available and valid
  bool get hasValidCapabilityToken =>
      _capabilityToken != null && _capabilityToken!.isValid;

  // ─────────────────────────────────────────────────────────────────────────
  // Role Checking
  // ─────────────────────────────────────────────────────────────────────────

  /// Get current user's role
  Role get currentRole {
    if (user == null) return Role.guest;
    return user!.role;
  }

  /// Check if user has a specific role
  bool hasRole(Role role) {
    return currentRole == role;
  }

  /// Check if user has any of the specified roles
  bool hasAnyRole(List<Role> roles) {
    return roles.contains(currentRole);
  }

  /// Check if user's role is at least the specified role (hierarchy)
  bool isAtLeast(Role role) {
    return currentRole.isAtLeast(role);
  }

  /// Check if user is admin
  bool get isAdmin => hasRole(Role.admin);

  /// Check if user is manager or higher
  bool get isManager => isAtLeast(Role.manager);

  /// Check if user is agronomist or higher
  bool get isAgronomist => isAtLeast(Role.agronomist);

  /// Check if user is field worker or higher
  bool get isFieldWorker => isAtLeast(Role.fieldWorker);

  // ─────────────────────────────────────────────────────────────────────────
  // Permission Checking
  // ─────────────────────────────────────────────────────────────────────────

  /// Get all permissions for current user
  Set<Permission> get permissions {
    if (user == null) return {};

    // Use capability token if available and valid (offline mode)
    if (hasValidCapabilityToken) {
      return _capabilityToken!.capabilities
          .map((id) => Permissions.findById(id))
          .whereType<Permission>()
          .toSet();
    }

    // Get role permissions from config
    final rolePerms = config.getPermissionsForRole(
      currentRole,
      environment: environment,
      tenantId: user!.tenantId,
    );

    // Add custom permissions
    final allPerms = {...rolePerms, ...user!.customPermissions};

    // Remove denied permissions
    allPerms.removeAll(user!.deniedPermissions);

    return allPerms;
  }

  /// Get permission IDs as strings
  Set<String> get permissionIds => permissions.map((p) => p.id).toSet();

  /// Check if user has a specific permission
  bool can(Permission permission) {
    if (user == null) return false;

    // Admin has all permissions
    if (isAdmin) return true;

    // Check if permission is denied
    if (user!.deniedPermissions.contains(permission)) return false;

    // Check offline mode restrictions
    if (isOffline && !permission.offlineCapable) return false;

    return permissions.contains(permission);
  }

  /// Check if user has permission by ID
  bool canById(String permissionId) {
    final permission = Permissions.findById(permissionId);
    if (permission == null) return false;
    return can(permission);
  }

  /// Check if user has any of the specified permissions
  bool canAny(List<Permission> permissionList) {
    return permissionList.any((p) => can(p));
  }

  /// Check if user has all of the specified permissions
  bool canAll(List<Permission> permissionList) {
    return permissionList.every((p) => can(p));
  }

  // ─────────────────────────────────────────────────────────────────────────
  // ABAC (Attribute-Based Access Control)
  // ─────────────────────────────────────────────────────────────────────────

  /// Check if user can access a specific field
  bool canAccessField(String fieldId, Permission permission) {
    if (!can(permission)) return false;

    // Admin can access all fields
    if (isAdmin) return true;

    // Manager can access all fields in tenant
    if (isManager) return true;

    // Use capability token if in offline mode
    if (hasValidCapabilityToken) {
      return _capabilityToken!.assignedFieldIds.contains(fieldId);
    }

    // Check assigned fields
    if (user != null && user!.assignedFieldIds.isNotEmpty) {
      return user!.assignedFieldIds.contains(fieldId);
    }

    // Default to true for online mode (server validates)
    return !isOffline;
  }

  /// Check if user can access a specific farm
  bool canAccessFarm(String farmId) {
    // Admin can access all farms
    if (isAdmin) return true;

    // Manager can access all farms in tenant
    if (isManager) return true;

    // Use capability token if in offline mode
    if (hasValidCapabilityToken) {
      return _capabilityToken!.assignedFarmIds.contains(farmId);
    }

    // Check assigned farms
    if (user != null && user!.assignedFarmIds.isNotEmpty) {
      return user!.assignedFarmIds.contains(farmId);
    }

    // Default to true for online mode
    return !isOffline;
  }

  /// Check if user can execute a task
  bool canExecuteTask({
    required String taskId,
    String? assignedTo,
    required bool requiresApproval,
  }) {
    // Must have task execute permission
    if (!can(Permissions.tasksExecute)) return false;

    // Check assignment
    if (assignedTo != null && user != null && assignedTo != user!.id) {
      // Only managers and above can execute unassigned tasks
      if (!isManager) return false;
    }

    // Tasks requiring approval cannot be executed offline
    if (isOffline && requiresApproval) return false;

    return true;
  }

  /// Check if user can assign tasks
  bool canAssignTask() => can(Permissions.tasksAssign);

  /// Check if user can manage IoT devices
  bool canManageIoT() => can(Permissions.iotManage);

  /// Check if user can control irrigation
  bool canControlIrrigation() => can(Permissions.irrigationControl);

  /// Check if user can export reports
  bool canExportReports() => can(Permissions.reportsExport);

  /// Check if user can manage users
  bool canManageUsers() => can(Permissions.usersManage);

  // ─────────────────────────────────────────────────────────────────────────
  // Screen Access
  // ─────────────────────────────────────────────────────────────────────────

  /// Check if user can access a screen
  bool canAccessScreen(AppScreen screen) {
    if (user == null) return false;

    return config.canAccessScreen(currentRole, screen);
  }

  /// Get all accessible screens for current user
  List<AppScreen> get accessibleScreens {
    if (user == null) return [];
    return config.getAccessibleScreens(currentRole);
  }

  /// Check if user can access a route
  bool canAccessRoute(String route) {
    final routeConfig = RbacRoutes.getRouteConfig(route);
    if (routeConfig == null) return true; // Unknown routes allowed

    // Check required role
    if (routeConfig.requiredRole != null) {
      if (!isAtLeast(routeConfig.requiredRole!)) return false;
    }

    // Check required permissions
    if (routeConfig.requiredPermissions.isNotEmpty) {
      if (!canAny(routeConfig.requiredPermissions)) return false;
    }

    return true;
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Feature Flags
  // ─────────────────────────────────────────────────────────────────────────

  /// Check if user has a feature flag
  bool hasFeature(String feature) {
    return RbacFeatures.hasFeature(currentRole, feature);
  }

  /// Get all features for current user
  Set<String> get features {
    return RbacFeatures.getFeatures(currentRole);
  }

  // ─────────────────────────────────────────────────────────────────────────
  // Action Guards
  // ─────────────────────────────────────────────────────────────────────────

  /// Check if action is allowed
  bool isActionAllowed(RbacAction action) {
    // Check permission
    if (action.permission != null && !can(action.permission!)) {
      return false;
    }

    // Check minimum role
    if (action.minRole != null && !isAtLeast(action.minRole!)) {
      return false;
    }

    // Check offline capability
    if (isOffline && !action.offlineCapable) {
      return false;
    }

    // Check feature flag
    if (action.featureFlag != null && !hasFeature(action.featureFlag!)) {
      return false;
    }

    // Custom check
    if (action.customCheck != null && !action.customCheck!(this)) {
      return false;
    }

    return true;
  }

  /// Get denial reason for action
  String? getActionDenialReason(RbacAction action, {Locale? locale}) {
    final isArabic = locale?.languageCode == 'ar';

    if (action.permission != null && !can(action.permission!)) {
      return isArabic
          ? 'ليس لديك صلاحية ${action.permission!.descriptionAr}'
          : 'You do not have permission: ${action.permission!.descriptionEn}';
    }

    if (action.minRole != null && !isAtLeast(action.minRole!)) {
      return isArabic
          ? 'يتطلب دور ${action.minRole!.nameAr} أو أعلى'
          : 'Requires ${action.minRole!.nameEn} role or higher';
    }

    if (isOffline && !action.offlineCapable) {
      return isArabic
          ? 'هذا الإجراء غير متاح بدون اتصال'
          : 'This action is not available offline';
    }

    if (action.featureFlag != null && !hasFeature(action.featureFlag!)) {
      return isArabic
          ? 'هذه الميزة غير متاحة لك'
          : 'This feature is not available for your account';
    }

    return null;
  }
}

/// Action definition for RBAC checking
/// تعريف الإجراء للتحقق من الوصول
class RbacAction {
  /// Action identifier
  final String id;

  /// Required permission
  final Permission? permission;

  /// Minimum required role
  final Role? minRole;

  /// Whether action can be performed offline
  final bool offlineCapable;

  /// Required feature flag
  final String? featureFlag;

  /// Custom check function
  final bool Function(RbacService service)? customCheck;

  const RbacAction({
    required this.id,
    this.permission,
    this.minRole,
    this.offlineCapable = true,
    this.featureFlag,
    this.customCheck,
  });
}

/// Common RBAC actions
/// إجراءات التحكم في الوصول الشائعة
class RbacActions {
  // Fields
  static const createField = RbacAction(
    id: 'create_field',
    permission: Permissions.fieldsCreate,
    minRole: Role.manager,
  );

  static const editField = RbacAction(
    id: 'edit_field',
    permission: Permissions.fieldsUpdate,
    minRole: Role.manager,
  );

  static const deleteField = RbacAction(
    id: 'delete_field',
    permission: Permissions.fieldsDelete,
    minRole: Role.manager,
    offlineCapable: false,
  );

  // Tasks
  static const createTask = RbacAction(
    id: 'create_task',
    permission: Permissions.tasksCreate,
    minRole: Role.agronomist,
  );

  static const assignTask = RbacAction(
    id: 'assign_task',
    permission: Permissions.tasksAssign,
    minRole: Role.manager,
    offlineCapable: false,
  );

  static const executeTask = RbacAction(
    id: 'execute_task',
    permission: Permissions.tasksExecute,
    minRole: Role.fieldWorker,
    offlineCapable: true,
  );

  static const deleteTask = RbacAction(
    id: 'delete_task',
    permission: Permissions.tasksDelete,
    minRole: Role.manager,
    offlineCapable: false,
  );

  // Reports
  static const createReport = RbacAction(
    id: 'create_report',
    permission: Permissions.reportsCreate,
    minRole: Role.agronomist,
    offlineCapable: false,
  );

  static const exportReport = RbacAction(
    id: 'export_report',
    permission: Permissions.reportsExport,
    minRole: Role.agronomist,
    offlineCapable: false,
  );

  // Irrigation
  static const controlIrrigation = RbacAction(
    id: 'control_irrigation',
    permission: Permissions.irrigationControl,
    minRole: Role.manager,
    offlineCapable: false,
  );

  // Users
  static const manageUsers = RbacAction(
    id: 'manage_users',
    permission: Permissions.usersManage,
    minRole: Role.admin,
    offlineCapable: false,
  );

  // IoT
  static const manageIoT = RbacAction(
    id: 'manage_iot',
    permission: Permissions.iotManage,
    minRole: Role.manager,
    offlineCapable: false,
  );

  // Settings
  static const manageSettings = RbacAction(
    id: 'manage_settings',
    permission: Permissions.settingsManage,
    minRole: Role.admin,
    offlineCapable: false,
  );
}

/// Access check result
/// نتيجة التحقق من الوصول
class AccessCheckResult {
  /// Whether access is granted
  final bool granted;

  /// Reason for denial (if denied)
  final String? denialReason;

  /// Denial reason in Arabic
  final String? denialReasonAr;

  /// Required role (if denied due to role)
  final Role? requiredRole;

  /// Required permission (if denied due to permission)
  final Permission? requiredPermission;

  const AccessCheckResult({
    required this.granted,
    this.denialReason,
    this.denialReasonAr,
    this.requiredRole,
    this.requiredPermission,
  });

  /// Access granted
  static const allowed = AccessCheckResult(granted: true);

  /// Create denied result
  factory AccessCheckResult.denied({
    required String reason,
    required String reasonAr,
    Role? requiredRole,
    Permission? requiredPermission,
  }) {
    return AccessCheckResult(
      granted: false,
      denialReason: reason,
      denialReasonAr: reasonAr,
      requiredRole: requiredRole,
      requiredPermission: requiredPermission,
    );
  }

  /// Get localized denial reason
  String? getDenialReason(Locale locale) {
    if (granted) return null;
    return locale.languageCode == 'ar' ? denialReasonAr : denialReason;
  }
}
