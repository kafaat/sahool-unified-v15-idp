/// SAHOOL Permission Manager
/// مدير الصلاحيات
///
/// Comprehensive permission management system with:
/// - Complete permission enumeration | تعداد كامل للصلاحيات
/// - Permission checking methods | طرق فحص الصلاحيات
/// - Permission caching | تخزين مؤقت للصلاحيات
/// - Role-based access control (RBAC) | التحكم بالوصول المبني على الأدوار
/// - Attribute-based access control (ABAC) | التحكم بالوصول المبني على الخصائص
library;



import '../utils/app_logger.dart';
import 'models/iam_models.dart';

// =============================================================================
// Permission Categories
// فئات الصلاحيات
// =============================================================================

/// Permission categories for organization
/// فئات الصلاحيات للتنظيم
enum PermissionCategory {
  /// Field operations | عمليات الحقل
  fieldOps('field_ops', 'عمليات الحقل'),

  /// Task management | إدارة المهام
  tasks('tasks', 'المهام'),

  /// NDVI/Remote sensing | الاستشعار عن بعد
  remoteSensing('remote_sensing', 'الاستشعار عن بعد'),

  /// Weather data | بيانات الطقس
  weather('weather', 'الطقس'),

  /// IoT devices | أجهزة إنترنت الأشياء
  iot('iot', 'أجهزة الاستشعار'),

  /// Irrigation | الري
  irrigation('irrigation', 'الري'),

  /// Reports & Analytics | التقارير والتحليلات
  reports('reports', 'التقارير'),

  /// Chat & Communication | المحادثات والتواصل
  communication('communication', 'التواصل'),

  /// User management | إدارة المستخدمين
  userManagement('user_management', 'إدارة المستخدمين'),

  /// Billing & Subscription | الفوترة والاشتراك
  billing('billing', 'الفوترة'),

  /// System administration | إدارة النظام
  admin('admin', 'الإدارة'),

  /// Offline capabilities | قدرات العمل بدون اتصال
  offline('offline', 'بدون اتصال'),

  /// Equipment & Assets | المعدات والأصول
  equipment('equipment', 'المعدات'),

  /// Advisory services | الخدمات الاستشارية
  advisory('advisory', 'الاستشارات'),

  /// Market & Trade | السوق والتجارة
  market('market', 'السوق');

  final String code;
  final String labelAr;

  const PermissionCategory(this.code, this.labelAr);
}

// =============================================================================
// Permission Definitions
// تعريفات الصلاحيات
// =============================================================================

/// Complete permission enumeration with metadata
/// تعداد الصلاحيات الكامل مع البيانات الوصفية
enum IAMPermission {
  // ─────────────────────────────────────────────────────────────────────────
  // Field Operations | عمليات الحقل
  // ─────────────────────────────────────────────────────────────────────────
  fieldView('fieldops:field.view', 'View fields', 'عرض الحقول', PermissionCategory.fieldOps),
  fieldCreate('fieldops:field.create', 'Create fields', 'إنشاء الحقول', PermissionCategory.fieldOps),
  fieldEdit('fieldops:field.edit', 'Edit fields', 'تعديل الحقول', PermissionCategory.fieldOps),
  fieldDelete('fieldops:field.delete', 'Delete fields', 'حذف الحقول', PermissionCategory.fieldOps),
  fieldBoundaryEdit('fieldops:field.boundary.edit', 'Edit field boundaries', 'تعديل حدود الحقول', PermissionCategory.fieldOps),
  fieldArchive('fieldops:field.archive', 'Archive fields', 'أرشفة الحقول', PermissionCategory.fieldOps),

  // ─────────────────────────────────────────────────────────────────────────
  // Tasks | المهام
  // ─────────────────────────────────────────────────────────────────────────
  taskView('fieldops:task.view', 'View tasks', 'عرض المهام', PermissionCategory.tasks),
  taskCreate('fieldops:task.create', 'Create tasks', 'إنشاء المهام', PermissionCategory.tasks),
  taskEdit('fieldops:task.edit', 'Edit tasks', 'تعديل المهام', PermissionCategory.tasks),
  taskDelete('fieldops:task.delete', 'Delete tasks', 'حذف المهام', PermissionCategory.tasks),
  taskAssign('fieldops:task.assign', 'Assign tasks', 'تعيين المهام', PermissionCategory.tasks),
  taskExecute('fieldops:task.execute', 'Execute tasks', 'تنفيذ المهام', PermissionCategory.tasks),
  taskComplete('fieldops:task.complete', 'Complete tasks', 'إكمال المهام', PermissionCategory.tasks),
  taskApprove('fieldops:task.approve', 'Approve tasks', 'اعتماد المهام', PermissionCategory.tasks),

  // ─────────────────────────────────────────────────────────────────────────
  // Remote Sensing (NDVI) | الاستشعار عن بعد
  // ─────────────────────────────────────────────────────────────────────────
  ndviView('ndvi:view', 'View NDVI data', 'عرض بيانات NDVI', PermissionCategory.remoteSensing),
  ndviCompute('ndvi:compute', 'Compute NDVI', 'حساب NDVI', PermissionCategory.remoteSensing),
  ndviExport('ndvi:export', 'Export NDVI data', 'تصدير بيانات NDVI', PermissionCategory.remoteSensing),
  ndviHistory('ndvi:history', 'View NDVI history', 'عرض تاريخ NDVI', PermissionCategory.remoteSensing),
  satelliteRequest('satellite:request', 'Request satellite imagery', 'طلب صور الأقمار الصناعية', PermissionCategory.remoteSensing),

  // ─────────────────────────────────────────────────────────────────────────
  // Weather | الطقس
  // ─────────────────────────────────────────────────────────────────────────
  weatherView('weather:view', 'View weather data', 'عرض بيانات الطقس', PermissionCategory.weather),
  weatherForecast('weather:forecast', 'View weather forecast', 'عرض توقعات الطقس', PermissionCategory.weather),
  weatherAlerts('weather:alerts', 'Manage weather alerts', 'إدارة تنبيهات الطقس', PermissionCategory.weather),

  // ─────────────────────────────────────────────────────────────────────────
  // IoT | أجهزة إنترنت الأشياء
  // ─────────────────────────────────────────────────────────────────────────
  iotDeviceView('iot:device.view', 'View IoT devices', 'عرض أجهزة الاستشعار', PermissionCategory.iot),
  iotDeviceManage('iot:device.manage', 'Manage IoT devices', 'إدارة أجهزة الاستشعار', PermissionCategory.iot),
  iotDeviceProvision('iot:device.provision', 'Provision IoT devices', 'تسجيل أجهزة الاستشعار', PermissionCategory.iot),
  sensorView('iot:sensor.view', 'View sensor data', 'عرض بيانات المستشعرات', PermissionCategory.iot),
  sensorCalibrate('iot:sensor.calibrate', 'Calibrate sensors', 'معايرة المستشعرات', PermissionCategory.iot),

  // ─────────────────────────────────────────────────────────────────────────
  // Irrigation | الري
  // ─────────────────────────────────────────────────────────────────────────
  irrigationView('irrigation:view', 'View irrigation data', 'عرض بيانات الري', PermissionCategory.irrigation),
  irrigationControl('irrigation:control', 'Control irrigation', 'التحكم بالري', PermissionCategory.irrigation),
  irrigationSchedule('irrigation:schedule', 'Schedule irrigation', 'جدولة الري', PermissionCategory.irrigation),
  irrigationManual('irrigation:manual', 'Manual irrigation control', 'التحكم اليدوي بالري', PermissionCategory.irrigation),

  // ─────────────────────────────────────────────────────────────────────────
  // Reports | التقارير
  // ─────────────────────────────────────────────────────────────────────────
  reportView('reports:view', 'View reports', 'عرض التقارير', PermissionCategory.reports),
  reportCreate('reports:create', 'Create reports', 'إنشاء التقارير', PermissionCategory.reports),
  reportExport('reports:export', 'Export reports', 'تصدير التقارير', PermissionCategory.reports),
  reportSchedule('reports:schedule', 'Schedule reports', 'جدولة التقارير', PermissionCategory.reports),
  analyticsView('analytics:view', 'View analytics', 'عرض التحليلات', PermissionCategory.reports),

  // ─────────────────────────────────────────────────────────────────────────
  // Communication | التواصل
  // ─────────────────────────────────────────────────────────────────────────
  chatRead('chat:read', 'Read chat messages', 'قراءة الرسائل', PermissionCategory.communication),
  chatWrite('chat:write', 'Send chat messages', 'إرسال الرسائل', PermissionCategory.communication),
  chatModerate('chat:moderate', 'Moderate chat', 'إدارة المحادثات', PermissionCategory.communication),
  notificationManage('notification:manage', 'Manage notifications', 'إدارة الإشعارات', PermissionCategory.communication),

  // ─────────────────────────────────────────────────────────────────────────
  // User Management | إدارة المستخدمين
  // ─────────────────────────────────────────────────────────────────────────
  userView('admin:users.view', 'View users', 'عرض المستخدمين', PermissionCategory.userManagement),
  userCreate('admin:users.create', 'Create users', 'إنشاء المستخدمين', PermissionCategory.userManagement),
  userEdit('admin:users.edit', 'Edit users', 'تعديل المستخدمين', PermissionCategory.userManagement),
  userDelete('admin:users.delete', 'Delete users', 'حذف المستخدمين', PermissionCategory.userManagement),
  userManage('admin:users.manage', 'Manage users', 'إدارة المستخدمين', PermissionCategory.userManagement),
  roleAssign('admin:roles.assign', 'Assign roles', 'تعيين الأدوار', PermissionCategory.userManagement),

  // ─────────────────────────────────────────────────────────────────────────
  // Billing | الفوترة
  // ─────────────────────────────────────────────────────────────────────────
  billingView('billing:view', 'View billing', 'عرض الفواتير', PermissionCategory.billing),
  billingManage('billing:manage', 'Manage billing', 'إدارة الفوترة', PermissionCategory.billing),
  subscriptionManage('billing:subscription.manage', 'Manage subscription', 'إدارة الاشتراك', PermissionCategory.billing),

  // ─────────────────────────────────────────────────────────────────────────
  // Admin | الإدارة
  // ─────────────────────────────────────────────────────────────────────────
  tenantManage('admin:tenant.manage', 'Manage tenant', 'إدارة المستأجر', PermissionCategory.admin),
  auditView('admin:audit.view', 'View audit logs', 'عرض سجلات التدقيق', PermissionCategory.admin),
  settingsManage('admin:settings.manage', 'Manage settings', 'إدارة الإعدادات', PermissionCategory.admin),
  systemConfig('admin:system.config', 'Configure system', 'إعداد النظام', PermissionCategory.admin),

  // ─────────────────────────────────────────────────────────────────────────
  // Offline | بدون اتصال
  // ─────────────────────────────────────────────────────────────────────────
  offlineSync('offline:sync', 'Sync offline data', 'مزامنة البيانات', PermissionCategory.offline),
  offlinePhotoUpload('offline:photo.upload', 'Upload photos offline', 'رفع الصور', PermissionCategory.offline),
  offlineDataAccess('offline:data.access', 'Access data offline', 'الوصول للبيانات', PermissionCategory.offline),

  // ─────────────────────────────────────────────────────────────────────────
  // Equipment | المعدات
  // ─────────────────────────────────────────────────────────────────────────
  equipmentView('equipment:view', 'View equipment', 'عرض المعدات', PermissionCategory.equipment),
  equipmentManage('equipment:manage', 'Manage equipment', 'إدارة المعدات', PermissionCategory.equipment),
  equipmentMaintenance('equipment:maintenance', 'Log maintenance', 'تسجيل الصيانة', PermissionCategory.equipment),

  // ─────────────────────────────────────────────────────────────────────────
  // Advisory | الاستشارات
  // ─────────────────────────────────────────────────────────────────────────
  advisoryView('advisory:view', 'View advisory', 'عرض الاستشارات', PermissionCategory.advisory),
  advisoryCreate('advisory:create', 'Create advisory', 'إنشاء الاستشارات', PermissionCategory.advisory),
  advisoryApprove('advisory:approve', 'Approve advisory', 'اعتماد الاستشارات', PermissionCategory.advisory),

  // ─────────────────────────────────────────────────────────────────────────
  // Market | السوق
  // ─────────────────────────────────────────────────────────────────────────
  marketView('market:view', 'View marketplace', 'عرض السوق', PermissionCategory.market),
  marketSell('market:sell', 'Sell on marketplace', 'البيع في السوق', PermissionCategory.market),
  marketBuy('market:buy', 'Buy from marketplace', 'الشراء من السوق', PermissionCategory.market);

  final String code;
  final String label;
  final String labelAr;
  final PermissionCategory category;

  const IAMPermission(this.code, this.label, this.labelAr, this.category);

  /// Get permission by code
  static IAMPermission? fromCode(String code) {
    try {
      return IAMPermission.values.firstWhere((p) => p.code == code);
    } catch (e) {
      return null;
    }
  }

  /// Get all permissions in a category
  static List<IAMPermission> byCategory(PermissionCategory category) {
    return IAMPermission.values.where((p) => p.category == category).toList();
  }

  /// Get localized label
  String getLabel({String locale = 'ar'}) {
    return locale == 'ar' ? labelAr : label;
  }
}

// =============================================================================
// Role Definitions
// تعريفات الأدوار
// =============================================================================

/// System roles with permission sets
/// أدوار النظام مع مجموعات الصلاحيات
enum IAMRole {
  /// Viewer - Read-only access | مشاهد - قراءة فقط
  viewer('viewer', 'Viewer', 'مشاهد'),

  /// Worker - Field operations | عامل ميداني
  worker('worker', 'Field Worker', 'عامل ميداني'),

  /// Supervisor - Team management | مشرف
  supervisor('supervisor', 'Supervisor', 'مشرف'),

  /// Manager - Full operational control | مدير
  manager('manager', 'Manager', 'مدير'),

  /// Admin - Tenant administration | مسؤول
  admin('admin', 'Administrator', 'مسؤول'),

  /// Super Admin - System-wide access | مسؤول النظام
  superAdmin('super_admin', 'Super Admin', 'مسؤول النظام');

  final String code;
  final String label;
  final String labelAr;

  const IAMRole(this.code, this.label, this.labelAr);

  /// Get role by code
  static IAMRole fromCode(String code) {
    return IAMRole.values.firstWhere(
      (r) => r.code == code,
      orElse: () => IAMRole.viewer,
    );
  }

  /// Get localized label
  String getLabel({String locale = 'ar'}) {
    return locale == 'ar' ? labelAr : label;
  }

  /// Get role hierarchy level (higher = more permissions)
  int get level {
    switch (this) {
      case IAMRole.viewer:
        return 0;
      case IAMRole.worker:
        return 1;
      case IAMRole.supervisor:
        return 2;
      case IAMRole.manager:
        return 3;
      case IAMRole.admin:
        return 4;
      case IAMRole.superAdmin:
        return 5;
    }
  }

  /// Check if this role includes another role
  bool includes(IAMRole other) => level >= other.level;
}

// =============================================================================
// Role Permission Mappings
// تعيينات صلاحيات الأدوار
// =============================================================================

/// Default permissions for each role
/// الصلاحيات الافتراضية لكل دور
final Map<IAMRole, Set<IAMPermission>> _rolePermissions = {
  // Viewer - مشاهد
  IAMRole.viewer: {
    IAMPermission.fieldView,
    IAMPermission.taskView,
    IAMPermission.ndviView,
    IAMPermission.weatherView,
    IAMPermission.iotDeviceView,
    IAMPermission.sensorView,
    IAMPermission.irrigationView,
    IAMPermission.reportView,
    IAMPermission.chatRead,
    IAMPermission.equipmentView,
    IAMPermission.advisoryView,
    IAMPermission.marketView,
  },

  // Worker - عامل ميداني
  IAMRole.worker: {
    // Inherits viewer
    IAMPermission.fieldView,
    IAMPermission.taskView,
    IAMPermission.ndviView,
    IAMPermission.weatherView,
    IAMPermission.iotDeviceView,
    IAMPermission.sensorView,
    IAMPermission.irrigationView,
    IAMPermission.reportView,
    IAMPermission.chatRead,
    IAMPermission.equipmentView,
    IAMPermission.advisoryView,
    IAMPermission.marketView,
    // Worker additions
    IAMPermission.taskEdit,
    IAMPermission.taskExecute,
    IAMPermission.taskComplete,
    IAMPermission.chatWrite,
    IAMPermission.offlineSync,
    IAMPermission.offlinePhotoUpload,
    IAMPermission.offlineDataAccess,
    IAMPermission.equipmentMaintenance,
  },

  // Supervisor - مشرف
  IAMRole.supervisor: {
    // Inherits worker
    IAMPermission.fieldView,
    IAMPermission.taskView,
    IAMPermission.taskEdit,
    IAMPermission.taskExecute,
    IAMPermission.taskComplete,
    IAMPermission.ndviView,
    IAMPermission.weatherView,
    IAMPermission.iotDeviceView,
    IAMPermission.sensorView,
    IAMPermission.irrigationView,
    IAMPermission.irrigationControl,
    IAMPermission.reportView,
    IAMPermission.chatRead,
    IAMPermission.chatWrite,
    IAMPermission.offlineSync,
    IAMPermission.offlinePhotoUpload,
    IAMPermission.offlineDataAccess,
    IAMPermission.equipmentView,
    IAMPermission.equipmentMaintenance,
    IAMPermission.advisoryView,
    IAMPermission.marketView,
    // Supervisor additions
    IAMPermission.taskCreate,
    IAMPermission.taskAssign,
    IAMPermission.fieldEdit,
    IAMPermission.irrigationSchedule,
    IAMPermission.reportCreate,
    IAMPermission.userView,
  },

  // Manager - مدير
  IAMRole.manager: {
    // Inherits supervisor + more
    IAMPermission.fieldView,
    IAMPermission.fieldCreate,
    IAMPermission.fieldEdit,
    IAMPermission.fieldDelete,
    IAMPermission.fieldBoundaryEdit,
    IAMPermission.taskView,
    IAMPermission.taskCreate,
    IAMPermission.taskEdit,
    IAMPermission.taskDelete,
    IAMPermission.taskAssign,
    IAMPermission.taskExecute,
    IAMPermission.taskComplete,
    IAMPermission.taskApprove,
    IAMPermission.ndviView,
    IAMPermission.ndviCompute,
    IAMPermission.ndviExport,
    IAMPermission.ndviHistory,
    IAMPermission.weatherView,
    IAMPermission.weatherForecast,
    IAMPermission.weatherAlerts,
    IAMPermission.iotDeviceView,
    IAMPermission.iotDeviceManage,
    IAMPermission.sensorView,
    IAMPermission.sensorCalibrate,
    IAMPermission.irrigationView,
    IAMPermission.irrigationControl,
    IAMPermission.irrigationSchedule,
    IAMPermission.irrigationManual,
    IAMPermission.reportView,
    IAMPermission.reportCreate,
    IAMPermission.reportExport,
    IAMPermission.analyticsView,
    IAMPermission.chatRead,
    IAMPermission.chatWrite,
    IAMPermission.userView,
    IAMPermission.offlineSync,
    IAMPermission.offlinePhotoUpload,
    IAMPermission.offlineDataAccess,
    IAMPermission.equipmentView,
    IAMPermission.equipmentManage,
    IAMPermission.equipmentMaintenance,
    IAMPermission.advisoryView,
    IAMPermission.advisoryCreate,
    IAMPermission.marketView,
    IAMPermission.marketSell,
    IAMPermission.marketBuy,
    IAMPermission.billingView,
  },

  // Admin - مسؤول
  IAMRole.admin: {
    // Inherits manager + admin capabilities
    ...IAMPermission.values.toSet()
      ..remove(IAMPermission.tenantManage)
      ..remove(IAMPermission.systemConfig),
  },

  // Super Admin - مسؤول النظام
  IAMRole.superAdmin: {
    // All permissions
    ...IAMPermission.values.toSet(),
  },
};

// =============================================================================
// Permission Manager
// مدير الصلاحيات
// =============================================================================

/// Permission Manager with caching and efficient lookup
/// مدير الصلاحيات مع التخزين المؤقت والبحث الفعال
class PermissionManager {
  /// Current user identity | هوية المستخدم الحالية
  final UserIdentity? _user;

  /// Permission cache | ذاكرة تخزين الصلاحيات
  final Map<String, bool> _permissionCache = {};

  /// Custom permissions (beyond role-based) | صلاحيات مخصصة
  final Set<String> _customPermissions = {};

  /// Denied permissions (explicit denials) | صلاحيات مرفوضة
  final Set<String> _deniedPermissions = {};

  /// Cache validity duration | مدة صلاحية الذاكرة المؤقتة
  static const Duration _cacheDuration = Duration(minutes: 5);

  /// Last cache refresh | آخر تحديث للذاكرة المؤقتة
  DateTime? _lastCacheRefresh;

  PermissionManager({UserIdentity? user}) : _user = user;

  /// Get current user role
  IAMRole get currentRole {
    if (_user == null) return IAMRole.viewer;
    return IAMRole.fromCode(_user.role);
  }

  /// Get all effective permissions | الحصول على جميع الصلاحيات الفعالة
  Set<String> get effectivePermissions {
    final permissions = <String>{};

    // Add role-based permissions
    final rolePerms = _rolePermissions[currentRole];
    if (rolePerms != null) {
      permissions.addAll(rolePerms.map((p) => p.code));
    }

    // Add user's custom permissions
    if (_user != null) {
      permissions.addAll(_user.permissions);
    }

    // Add any additional custom permissions
    permissions.addAll(_customPermissions);

    // Remove explicitly denied permissions
    permissions.removeAll(_deniedPermissions);

    return permissions;
  }

  // ===========================================================================
  // Permission Checking | فحص الصلاحيات
  // ===========================================================================

  /// Check if user has a specific permission
  /// التحقق مما إذا كان للمستخدم صلاحية محددة
  bool can(String permission) {
    if (_user == null) return false;

    // Super admin has all permissions
    if (currentRole == IAMRole.superAdmin) return true;

    // Check cache first
    if (_isCacheValid() && _permissionCache.containsKey(permission)) {
      return _permissionCache[permission]!;
    }

    // Check if explicitly denied
    if (_deniedPermissions.contains(permission)) {
      _cacheResult(permission, false);
      return false;
    }

    // Check effective permissions
    final hasPermission = effectivePermissions.contains(permission);
    _cacheResult(permission, hasPermission);
    return hasPermission;
  }

  /// Check if user has permission using enum
  /// التحقق من الصلاحية باستخدام التعداد
  bool canDo(IAMPermission permission) => can(permission.code);

  /// Check if user has ANY of the specified permissions
  /// التحقق مما إذا كان للمستخدم أي من الصلاحيات المحددة
  bool canAny(List<String> permissions) {
    return permissions.any((p) => can(p));
  }

  /// Check if user has ANY of the specified permissions (enum version)
  bool canAnyOf(List<IAMPermission> permissions) {
    return permissions.any((p) => canDo(p));
  }

  /// Check if user has ALL of the specified permissions
  /// التحقق مما إذا كان للمستخدم جميع الصلاحيات المحددة
  bool canAll(List<String> permissions) {
    return permissions.every((p) => can(p));
  }

  /// Check if user has ALL of the specified permissions (enum version)
  bool canAllOf(List<IAMPermission> permissions) {
    return permissions.every((p) => canDo(p));
  }

  // ===========================================================================
  // Role Checking | فحص الأدوار
  // ===========================================================================

  /// Check if user has a specific role
  /// التحقق مما إذا كان للمستخدم دور محدد
  bool hasRole(IAMRole role) {
    return currentRole == role;
  }

  /// Check if user has ANY of the specified roles
  /// التحقق مما إذا كان للمستخدم أي من الأدوار المحددة
  bool hasAnyRole(List<IAMRole> roles) {
    return roles.contains(currentRole);
  }

  /// Check if user's role is at least the specified level
  /// التحقق مما إذا كان مستوى دور المستخدم على الأقل المستوى المحدد
  bool hasRoleAtLeast(IAMRole minimumRole) {
    return currentRole.includes(minimumRole);
  }

  /// Convenience getters for common role checks
  bool get isViewer => currentRole.level >= IAMRole.viewer.level;
  bool get isWorker => currentRole.level >= IAMRole.worker.level;
  bool get isSupervisor => currentRole.level >= IAMRole.supervisor.level;
  bool get isManager => currentRole.level >= IAMRole.manager.level;
  bool get isAdmin => currentRole.level >= IAMRole.admin.level;
  bool get isSuperAdmin => currentRole == IAMRole.superAdmin;

  // ===========================================================================
  // Permission Management | إدارة الصلاحيات
  // ===========================================================================

  /// Grant additional permission
  /// منح صلاحية إضافية
  void grantPermission(String permission) {
    _customPermissions.add(permission);
    _deniedPermissions.remove(permission);
    _invalidateCache(permission);
    AppLogger.d('Granted permission: $permission', tag: 'PERMISSION');
  }

  /// Revoke permission
  /// سحب صلاحية
  void revokePermission(String permission) {
    _customPermissions.remove(permission);
    _deniedPermissions.add(permission);
    _invalidateCache(permission);
    AppLogger.d('Revoked permission: $permission', tag: 'PERMISSION');
  }

  /// Clear all custom permissions
  /// مسح جميع الصلاحيات المخصصة
  void clearCustomPermissions() {
    _customPermissions.clear();
    _deniedPermissions.clear();
    _clearCache();
  }

  // ===========================================================================
  // Cache Management | إدارة الذاكرة المؤقتة
  // ===========================================================================

  /// Check if cache is still valid
  bool _isCacheValid() {
    if (_lastCacheRefresh == null) return false;
    return DateTime.now().difference(_lastCacheRefresh!) < _cacheDuration;
  }

  /// Cache permission result
  void _cacheResult(String permission, bool result) {
    _permissionCache[permission] = result;
    _lastCacheRefresh ??= DateTime.now();
  }

  /// Invalidate specific permission in cache
  void _invalidateCache(String permission) {
    _permissionCache.remove(permission);
  }

  /// Clear entire cache
  void _clearCache() {
    _permissionCache.clear();
    _lastCacheRefresh = null;
  }

  /// Refresh cache
  void refreshCache() {
    _clearCache();
    AppLogger.d('Permission cache refreshed', tag: 'PERMISSION');
  }

  // ===========================================================================
  // Permission Queries | استعلامات الصلاحيات
  // ===========================================================================

  /// Get all permissions for a specific category
  /// الحصول على جميع الصلاحيات لفئة محددة
  List<IAMPermission> getPermissionsForCategory(PermissionCategory category) {
    return IAMPermission.byCategory(category)
        .where((p) => can(p.code))
        .toList();
  }

  /// Get all granted permissions as IAMPermission enums
  /// الحصول على جميع الصلاحيات الممنوحة كتعدادات
  List<IAMPermission> get grantedPermissions {
    return effectivePermissions
        .map((code) => IAMPermission.fromCode(code))
        .whereType<IAMPermission>()
        .toList();
  }

  /// Get permissions grouped by category
  /// الحصول على الصلاحيات مجمعة حسب الفئة
  Map<PermissionCategory, List<IAMPermission>> get permissionsByCategory {
    final result = <PermissionCategory, List<IAMPermission>>{};

    for (final category in PermissionCategory.values) {
      final perms = getPermissionsForCategory(category);
      if (perms.isNotEmpty) {
        result[category] = perms;
      }
    }

    return result;
  }

  /// Get default permissions for a role
  /// الحصول على الصلاحيات الافتراضية لدور
  static Set<IAMPermission> getPermissionsForRole(IAMRole role) {
    return _rolePermissions[role] ?? {};
  }

  /// Get all roles that have a specific permission
  /// الحصول على جميع الأدوار التي لديها صلاحية محددة
  static List<IAMRole> getRolesWithPermission(IAMPermission permission) {
    return IAMRole.values.where((role) {
      final perms = _rolePermissions[role];
      return perms != null && perms.contains(permission);
    }).toList();
  }
}

// =============================================================================
// Permission Checker Mixin
// مزيج فاحص الصلاحيات
// =============================================================================

/// Mixin for easy permission checking in services
/// مزيج لفحص الصلاحيات بسهولة في الخدمات
mixin PermissionCheckerMixin {
  PermissionManager get permissionManager;

  /// Assert user has permission, throw if not
  void assertPermission(String permission) {
    if (!permissionManager.can(permission)) {
      throw PermissionDeniedException(
        'Permission denied: $permission',
        'الصلاحية مرفوضة: $permission',
        permission: permission,
      );
    }
  }

  /// Assert user has permission (enum version)
  void assertCan(IAMPermission permission) {
    assertPermission(permission.code);
  }

  /// Assert user has any of the permissions
  void assertAnyPermission(List<String> permissions) {
    if (!permissionManager.canAny(permissions)) {
      throw PermissionDeniedException(
        'Permission denied: requires one of $permissions',
        'الصلاحية مرفوضة: يتطلب إحدى $permissions',
        permission: permissions.join(', '),
      );
    }
  }

  /// Assert user has all permissions
  void assertAllPermissions(List<String> permissions) {
    if (!permissionManager.canAll(permissions)) {
      throw PermissionDeniedException(
        'Permission denied: requires all of $permissions',
        'الصلاحية مرفوضة: يتطلب جميع $permissions',
        permission: permissions.join(', '),
      );
    }
  }

  /// Assert user has minimum role
  void assertRole(IAMRole minimumRole) {
    if (!permissionManager.hasRoleAtLeast(minimumRole)) {
      throw PermissionDeniedException(
        'Role required: ${minimumRole.code}',
        'الدور المطلوب: ${minimumRole.labelAr}',
        permission: minimumRole.code,
      );
    }
  }
}

// =============================================================================
// Permission Denied Exception
// استثناء رفض الصلاحية
// =============================================================================

/// Exception thrown when permission is denied
class PermissionDeniedException implements Exception {
  final String message;
  final String messageAr;
  final String? permission;

  const PermissionDeniedException(
    this.message,
    this.messageAr, {
    this.permission,
  });

  String getLocalizedMessage({String locale = 'ar'}) {
    return locale == 'ar' ? messageAr : message;
  }

  @override
  String toString() => 'PermissionDeniedException: $message';
}
