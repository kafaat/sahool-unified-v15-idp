/// SAHOOL Access Control
/// التحكم في الوصول
///
/// Comprehensive access control system providing:
/// - Access Control Lists (ACL) | قوائم التحكم في الوصول
/// - Resource-based permissions | صلاحيات قائمة على الموارد
/// - Field-level security | أمان على مستوى الحقل
/// - Tenant isolation | عزل المستأجرين
/// - Hierarchical permissions | صلاحيات هرمية
library;


import 'package:flutter/foundation.dart';

import '../utils/app_logger.dart';
import 'models/iam_models.dart';
import 'permission_manager.dart';

// =============================================================================
// Resource Types
// أنواع الموارد
// =============================================================================

/// Supported resource types for access control
/// أنواع الموارد المدعومة للتحكم في الوصول
enum ResourceType {
  /// Farm resource | مزرعة
  farm('farm', 'Farm', 'مزرعة'),

  /// Field resource | حقل
  field('field', 'Field', 'حقل'),

  /// Task resource | مهمة
  task('task', 'Task', 'مهمة'),

  /// User resource | مستخدم
  user('user', 'User', 'مستخدم'),

  /// Team resource | فريق
  team('team', 'Team', 'فريق'),

  /// Report resource | تقرير
  report('report', 'Report', 'تقرير'),

  /// Equipment resource | معدات
  equipment('equipment', 'Equipment', 'معدات'),

  /// IoT device resource | جهاز استشعار
  device('device', 'Device', 'جهاز'),

  /// Document resource | مستند
  document('document', 'Document', 'مستند'),

  /// Advisory resource | استشارة
  advisory('advisory', 'Advisory', 'استشارة'),

  /// Inventory resource | مخزون
  inventory('inventory', 'Inventory', 'مخزون'),

  /// Market listing resource | عرض سوقي
  marketListing('market_listing', 'Market Listing', 'عرض سوقي'),

  /// Chat/Message resource | رسالة
  message('message', 'Message', 'رسالة'),

  /// Notification resource | إشعار
  notification('notification', 'Notification', 'إشعار');

  final String code;
  final String label;
  final String labelAr;

  const ResourceType(this.code, this.label, this.labelAr);

  String getLabel({String locale = 'ar'}) {
    return locale == 'ar' ? labelAr : label;
  }

  static ResourceType? fromCode(String code) {
    try {
      return ResourceType.values.firstWhere((t) => t.code == code);
    } catch (e) {
      return null;
    }
  }
}

// =============================================================================
// Access Actions
// إجراءات الوصول
// =============================================================================

/// Possible actions on resources
/// الإجراءات الممكنة على الموارد
enum AccessAction {
  /// View/Read access | الوصول للقراءة
  view('view', 'View', 'عرض'),

  /// Create new resource | إنشاء مورد جديد
  create('create', 'Create', 'إنشاء'),

  /// Update/Edit resource | تحديث/تعديل المورد
  update('update', 'Update', 'تحديث'),

  /// Delete resource | حذف المورد
  delete('delete', 'Delete', 'حذف'),

  /// Execute action on resource | تنفيذ إجراء على المورد
  execute('execute', 'Execute', 'تنفيذ'),

  /// Share resource | مشاركة المورد
  share('share', 'Share', 'مشاركة'),

  /// Export resource | تصدير المورد
  export('export', 'Export', 'تصدير'),

  /// Approve resource | اعتماد المورد
  approve('approve', 'Approve', 'اعتماد'),

  /// Assign resource | تعيين المورد
  assign('assign', 'Assign', 'تعيين'),

  /// Archive resource | أرشفة المورد
  archive('archive', 'Archive', 'أرشفة'),

  /// Full control | تحكم كامل
  manage('manage', 'Manage', 'إدارة');

  final String code;
  final String label;
  final String labelAr;

  const AccessAction(this.code, this.label, this.labelAr);

  String getLabel({String locale = 'ar'}) {
    return locale == 'ar' ? labelAr : label;
  }

  static AccessAction? fromCode(String code) {
    try {
      return AccessAction.values.firstWhere((a) => a.code == code);
    } catch (e) {
      return null;
    }
  }
}

// =============================================================================
// Access Control Entry (ACE)
// إدخال التحكم في الوصول
// =============================================================================

/// Single access control entry
/// إدخال واحد للتحكم في الوصول
@immutable
class AccessControlEntry {
  /// Unique entry ID | معرف فريد للإدخال
  final String id;

  /// Principal ID (user or group) | معرف المستخدم أو المجموعة
  final String principalId;

  /// Principal type (user, group, role) | نوع المستخدم
  final PrincipalType principalType;

  /// Resource type | نوع المورد
  final ResourceType resourceType;

  /// Resource ID (or '*' for all) | معرف المورد
  final String resourceId;

  /// Allowed actions | الإجراءات المسموحة
  final Set<AccessAction> allowedActions;

  /// Denied actions | الإجراءات المرفوضة
  final Set<AccessAction> deniedActions;

  /// Conditions for access | شروط الوصول
  final Map<String, dynamic>? conditions;

  /// Entry expiry | انتهاء الصلاحية
  final DateTime? expiresAt;

  /// Whether this is inherited | هل موروث
  final bool inherited;

  /// Source of inheritance | مصدر الوراثة
  final String? inheritedFrom;

  /// Created at | تاريخ الإنشاء
  final DateTime createdAt;

  /// Created by | أنشئ بواسطة
  final String? createdBy;

  const AccessControlEntry({
    required this.id,
    required this.principalId,
    required this.principalType,
    required this.resourceType,
    required this.resourceId,
    this.allowedActions = const {},
    this.deniedActions = const {},
    this.conditions,
    this.expiresAt,
    this.inherited = false,
    this.inheritedFrom,
    required this.createdAt,
    this.createdBy,
  });

  /// Check if entry is expired
  bool get isExpired {
    if (expiresAt == null) return false;
    return DateTime.now().isAfter(expiresAt!);
  }

  /// Check if entry allows specific action
  bool allows(AccessAction action) {
    if (isExpired) return false;
    if (deniedActions.contains(action)) return false;
    return allowedActions.contains(action) || allowedActions.contains(AccessAction.manage);
  }

  /// Check if entry denies specific action
  bool denies(AccessAction action) {
    if (isExpired) return false;
    return deniedActions.contains(action);
  }

  factory AccessControlEntry.fromJson(Map<String, dynamic> json) {
    return AccessControlEntry(
      id: json['id'] as String,
      principalId: json['principal_id'] as String,
      principalType: PrincipalType.values.firstWhere(
        (t) => t.code == json['principal_type'],
        orElse: () => PrincipalType.user,
      ),
      resourceType: ResourceType.fromCode(json['resource_type'] as String) ?? ResourceType.field,
      resourceId: json['resource_id'] as String,
      allowedActions: (json['allowed_actions'] as List<dynamic>?)
              ?.map((a) => AccessAction.fromCode(a as String))
              .whereType<AccessAction>()
              .toSet() ??
          {},
      deniedActions: (json['denied_actions'] as List<dynamic>?)
              ?.map((a) => AccessAction.fromCode(a as String))
              .whereType<AccessAction>()
              .toSet() ??
          {},
      conditions: json['conditions'] as Map<String, dynamic>?,
      expiresAt: json['expires_at'] != null ? DateTime.tryParse(json['expires_at'] as String) : null,
      inherited: json['inherited'] as bool? ?? false,
      inheritedFrom: json['inherited_from'] as String?,
      createdAt: DateTime.tryParse(json['created_at'] as String) ?? DateTime.now(),
      createdBy: json['created_by'] as String?,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'principal_id': principalId,
      'principal_type': principalType.code,
      'resource_type': resourceType.code,
      'resource_id': resourceId,
      'allowed_actions': allowedActions.map((a) => a.code).toList(),
      'denied_actions': deniedActions.map((a) => a.code).toList(),
      'conditions': conditions,
      'expires_at': expiresAt?.toIso8601String(),
      'inherited': inherited,
      'inherited_from': inheritedFrom,
      'created_at': createdAt.toIso8601String(),
      'created_by': createdBy,
    };
  }
}

/// Principal types
/// أنواع المستخدمين
enum PrincipalType {
  user('user', 'User', 'مستخدم'),
  group('group', 'Group', 'مجموعة'),
  role('role', 'Role', 'دور'),
  team('team', 'Team', 'فريق'),
  tenant('tenant', 'Tenant', 'مستأجر');

  final String code;
  final String label;
  final String labelAr;

  const PrincipalType(this.code, this.label, this.labelAr);
}

// =============================================================================
// Access Control List (ACL)
// قائمة التحكم في الوصول
// =============================================================================

/// Access Control List for a resource
/// قائمة التحكم في الوصول لمورد
@immutable
class AccessControlList {
  /// Resource type | نوع المورد
  final ResourceType resourceType;

  /// Resource ID | معرف المورد
  final String resourceId;

  /// Tenant ID | معرف المستأجر
  final String tenantId;

  /// Owner user ID | معرف المالك
  final String ownerId;

  /// Access control entries | إدخالات التحكم في الوصول
  final List<AccessControlEntry> entries;

  /// Parent resource ID (for inheritance) | معرف المورد الأب
  final String? parentResourceId;

  /// Whether to inherit from parent | هل يورث من الأب
  final bool inheritFromParent;

  /// Last modified | آخر تعديل
  final DateTime lastModified;

  const AccessControlList({
    required this.resourceType,
    required this.resourceId,
    required this.tenantId,
    required this.ownerId,
    this.entries = const [],
    this.parentResourceId,
    this.inheritFromParent = true,
    required this.lastModified,
  });

  /// Get all entries for a principal
  List<AccessControlEntry> getEntriesForPrincipal(String principalId) {
    return entries.where((e) => e.principalId == principalId && !e.isExpired).toList();
  }

  /// Check if principal has action
  bool checkAccess(String principalId, AccessAction action) {
    final principalEntries = getEntriesForPrincipal(principalId);

    // Check for explicit denial first
    for (final entry in principalEntries) {
      if (entry.denies(action)) {
        return false;
      }
    }

    // Check for explicit allow
    for (final entry in principalEntries) {
      if (entry.allows(action)) {
        return true;
      }
    }

    return false;
  }

  factory AccessControlList.fromJson(Map<String, dynamic> json) {
    return AccessControlList(
      resourceType: ResourceType.fromCode(json['resource_type'] as String) ?? ResourceType.field,
      resourceId: json['resource_id'] as String,
      tenantId: json['tenant_id'] as String,
      ownerId: json['owner_id'] as String,
      entries: (json['entries'] as List<dynamic>?)
              ?.map((e) => AccessControlEntry.fromJson(e as Map<String, dynamic>))
              .toList() ??
          [],
      parentResourceId: json['parent_resource_id'] as String?,
      inheritFromParent: json['inherit_from_parent'] as bool? ?? true,
      lastModified: DateTime.tryParse(json['last_modified'] as String) ?? DateTime.now(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'resource_type': resourceType.code,
      'resource_id': resourceId,
      'tenant_id': tenantId,
      'owner_id': ownerId,
      'entries': entries.map((e) => e.toJson()).toList(),
      'parent_resource_id': parentResourceId,
      'inherit_from_parent': inheritFromParent,
      'last_modified': lastModified.toIso8601String(),
    };
  }
}

// =============================================================================
// Field-Level Security
// أمان على مستوى الحقل
// =============================================================================

/// Field-level security policy
/// سياسة الأمان على مستوى الحقل
@immutable
class FieldSecurityPolicy {
  /// Resource type this policy applies to | نوع المورد
  final ResourceType resourceType;

  /// Field name | اسم الحقل
  final String fieldName;

  /// Minimum role required to read | الحد الأدنى للدور للقراءة
  final IAMRole? minRoleToRead;

  /// Minimum role required to write | الحد الأدنى للدور للكتابة
  final IAMRole? minRoleToWrite;

  /// Specific permissions required to read | صلاحيات محددة للقراءة
  final Set<IAMPermission>? permissionsToRead;

  /// Specific permissions required to write | صلاحيات محددة للكتابة
  final Set<IAMPermission>? permissionsToWrite;

  /// Whether field is always masked | هل الحقل مخفي دائماً
  final bool alwaysMasked;

  /// Mask pattern (e.g., '***' or partial mask) | نمط الإخفاء
  final String? maskPattern;

  /// Whether field is PII (Personal Identifiable Information) | هل الحقل بيانات شخصية
  final bool isPII;

  /// Whether field is encrypted at rest | هل الحقل مشفر
  final bool isEncrypted;

  const FieldSecurityPolicy({
    required this.resourceType,
    required this.fieldName,
    this.minRoleToRead,
    this.minRoleToWrite,
    this.permissionsToRead,
    this.permissionsToWrite,
    this.alwaysMasked = false,
    this.maskPattern,
    this.isPII = false,
    this.isEncrypted = false,
  });

  /// Check if user can read field
  bool canRead(PermissionManager permissionManager) {
    if (alwaysMasked) return false;

    if (minRoleToRead != null) {
      if (!permissionManager.hasRoleAtLeast(minRoleToRead!)) {
        return false;
      }
    }

    if (permissionsToRead != null && permissionsToRead!.isNotEmpty) {
      if (!permissionManager.canAnyOf(permissionsToRead!.toList())) {
        return false;
      }
    }

    return true;
  }

  /// Check if user can write field
  bool canWrite(PermissionManager permissionManager) {
    if (minRoleToWrite != null) {
      if (!permissionManager.hasRoleAtLeast(minRoleToWrite!)) {
        return false;
      }
    }

    if (permissionsToWrite != null && permissionsToWrite!.isNotEmpty) {
      if (!permissionManager.canAnyOf(permissionsToWrite!.toList())) {
        return false;
      }
    }

    return true;
  }

  /// Mask field value | إخفاء قيمة الحقل
  String maskValue(String value) {
    if (maskPattern != null) {
      return maskPattern!;
    }
    if (value.length <= 4) {
      return '****';
    }
    // Show last 4 characters
    return '****${value.substring(value.length - 4)}';
  }
}

// =============================================================================
// Access Control Service
// خدمة التحكم في الوصول
// =============================================================================

/// Main access control service
/// خدمة التحكم في الوصول الرئيسية
class AccessControlService {
  /// Current user identity | هوية المستخدم الحالية
  final UserIdentity? _user;

  /// Permission manager | مدير الصلاحيات
  final PermissionManager _permissionManager;

  /// ACL cache | ذاكرة تخزين ACL
  final Map<String, AccessControlList> _aclCache = {};

  /// Field security policies | سياسات أمان الحقول
  final Map<String, List<FieldSecurityPolicy>> _fieldPolicies = {};

  /// Resource hierarchy (parent -> children) | هرم الموارد
  final Map<String, Set<String>> _resourceHierarchy = {};

  /// Audit callback | استدعاء التدقيق
  final void Function(AccessAuditEntry)? onAudit;

  AccessControlService({
    UserIdentity? user,
    required PermissionManager permissionManager,
    this.onAudit,
  })  : _user = user,
        _permissionManager = permissionManager;

  // ===========================================================================
  // Resource Access Checking | فحص الوصول للموارد
  // ===========================================================================

  /// Check if current user can perform action on resource
  /// التحقق مما إذا كان المستخدم الحالي يمكنه تنفيذ إجراء على مورد
  AccessDecision checkResourceAccess({
    required ResourceType resourceType,
    required String resourceId,
    required AccessAction action,
    Map<String, dynamic>? context,
  }) {
    if (_user == null) {
      return const AccessDecision(
        allowed: false,
        reason: 'Not authenticated',
        reasonAr: 'غير مصادق',
      );
    }

    // Super admin has full access
    if (_permissionManager.isSuperAdmin) {
      _audit(resourceType, resourceId, action, true, 'Super admin access');
      return const AccessDecision(
        allowed: true,
        reason: 'Super admin access',
        reasonAr: 'وصول مسؤول النظام',
      );
    }

    // Check tenant isolation
    if (!_checkTenantAccess(resourceType, resourceId)) {
      _audit(resourceType, resourceId, action, false, 'Tenant isolation');
      return const AccessDecision(
        allowed: false,
        reason: 'Resource belongs to different tenant',
        reasonAr: 'المورد ينتمي لمستأجر مختلف',
      );
    }

    // Check ACL
    final acl = _aclCache['${resourceType.code}:$resourceId'];
    if (acl != null) {
      // Owner has full access
      if (acl.ownerId == _user.id) {
        _audit(resourceType, resourceId, action, true, 'Owner access');
        return const AccessDecision(
          allowed: true,
          reason: 'Owner access',
          reasonAr: 'وصول المالك',
        );
      }

      // Check ACL entries
      if (acl.checkAccess(_user.id, action)) {
        _audit(resourceType, resourceId, action, true, 'ACL granted');
        return const AccessDecision(
          allowed: true,
          reason: 'Access granted by ACL',
          reasonAr: 'تم منح الوصول بواسطة قائمة التحكم',
        );
      }

      // Check role-based entries
      final roleEntry = acl.entries.firstWhere(
        (e) => e.principalType == PrincipalType.role && e.principalId == _user.role,
        orElse: () => AccessControlEntry(
          id: '',
          principalId: '',
          principalType: PrincipalType.user,
          resourceType: resourceType,
          resourceId: resourceId,
          createdAt: DateTime.now(),
        ),
      );

      if (roleEntry.id.isNotEmpty && roleEntry.allows(action)) {
        _audit(resourceType, resourceId, action, true, 'Role-based access');
        return const AccessDecision(
          allowed: true,
          reason: 'Role-based access',
          reasonAr: 'وصول مبني على الدور',
        );
      }
    }

    // Check permission-based access
    final permissionCode = _getPermissionForAction(resourceType, action);
    if (permissionCode != null && _permissionManager.can(permissionCode)) {
      _audit(resourceType, resourceId, action, true, 'Permission-based access');
      return const AccessDecision(
        allowed: true,
        reason: 'Permission-based access',
        reasonAr: 'وصول مبني على الصلاحية',
      );
    }

    // Check hierarchical access
    if (_checkHierarchicalAccess(resourceType, resourceId, action)) {
      _audit(resourceType, resourceId, action, true, 'Hierarchical access');
      return const AccessDecision(
        allowed: true,
        reason: 'Inherited from parent resource',
        reasonAr: 'موروث من المورد الأب',
      );
    }

    _audit(resourceType, resourceId, action, false, 'Access denied');
    return const AccessDecision(
      allowed: false,
      reason: 'Access denied',
      reasonAr: 'الوصول مرفوض',
    );
  }

  /// Check multiple resources at once | فحص موارد متعددة مرة واحدة
  Map<String, AccessDecision> checkBulkAccess({
    required ResourceType resourceType,
    required List<String> resourceIds,
    required AccessAction action,
  }) {
    final results = <String, AccessDecision>{};

    for (final resourceId in resourceIds) {
      results[resourceId] = checkResourceAccess(
        resourceType: resourceType,
        resourceId: resourceId,
        action: action,
      );
    }

    return results;
  }

  /// Filter resources by access | تصفية الموارد حسب الوصول
  List<String> filterByAccess({
    required ResourceType resourceType,
    required List<String> resourceIds,
    required AccessAction action,
  }) {
    return resourceIds.where((id) {
      final decision = checkResourceAccess(
        resourceType: resourceType,
        resourceId: id,
        action: action,
      );
      return decision.allowed;
    }).toList();
  }

  // ===========================================================================
  // Field-Level Security | أمان على مستوى الحقل
  // ===========================================================================

  /// Register field security policy | تسجيل سياسة أمان الحقل
  void registerFieldPolicy(FieldSecurityPolicy policy) {
    final key = policy.resourceType.code;
    _fieldPolicies[key] ??= [];
    _fieldPolicies[key]!.add(policy);
    AppLogger.d('Registered field policy for ${policy.fieldName}', tag: 'ACL');
  }

  /// Get field policy | الحصول على سياسة الحقل
  FieldSecurityPolicy? getFieldPolicy(ResourceType resourceType, String fieldName) {
    final policies = _fieldPolicies[resourceType.code];
    if (policies == null) return null;

    return policies.firstWhere(
      (p) => p.fieldName == fieldName,
      orElse: () => FieldSecurityPolicy(
        resourceType: resourceType,
        fieldName: fieldName,
      ),
    );
  }

  /// Check if field can be read | التحقق من إمكانية قراءة الحقل
  bool canReadField(ResourceType resourceType, String fieldName) {
    final policy = getFieldPolicy(resourceType, fieldName);
    if (policy == null) return true; // No policy = accessible

    return policy.canRead(_permissionManager);
  }

  /// Check if field can be written | التحقق من إمكانية كتابة الحقل
  bool canWriteField(ResourceType resourceType, String fieldName) {
    final policy = getFieldPolicy(resourceType, fieldName);
    if (policy == null) return true;

    return policy.canWrite(_permissionManager);
  }

  /// Mask field value if needed | إخفاء قيمة الحقل إذا لزم الأمر
  dynamic maskFieldIfNeeded(
    ResourceType resourceType,
    String fieldName,
    dynamic value,
  ) {
    if (value == null) return null;

    final policy = getFieldPolicy(resourceType, fieldName);
    if (policy == null) return value;

    if (!policy.canRead(_permissionManager)) {
      if (value is String) {
        return policy.maskValue(value);
      }
      return null;
    }

    return value;
  }

  /// Filter object fields based on security | تصفية حقول الكائن بناءً على الأمان
  Map<String, dynamic> filterFields(
    ResourceType resourceType,
    Map<String, dynamic> data,
  ) {
    final filtered = <String, dynamic>{};

    for (final entry in data.entries) {
      if (canReadField(resourceType, entry.key)) {
        filtered[entry.key] = maskFieldIfNeeded(
          resourceType,
          entry.key,
          entry.value,
        );
      }
    }

    return filtered;
  }

  /// Get list of writable fields | الحصول على قائمة الحقول القابلة للكتابة
  List<String> getWritableFields(ResourceType resourceType) {
    final policies = _fieldPolicies[resourceType.code] ?? [];
    final allFields = <String>[];

    for (final policy in policies) {
      if (policy.canWrite(_permissionManager)) {
        allFields.add(policy.fieldName);
      }
    }

    return allFields;
  }

  // ===========================================================================
  // ACL Management | إدارة قوائم التحكم في الوصول
  // ===========================================================================

  /// Set ACL for resource | تعيين قائمة التحكم في الوصول للمورد
  void setAcl(AccessControlList acl) {
    final key = '${acl.resourceType.code}:${acl.resourceId}';
    _aclCache[key] = acl;
    AppLogger.d('Set ACL for $key', tag: 'ACL');
  }

  /// Get ACL for resource | الحصول على قائمة التحكم في الوصول للمورد
  AccessControlList? getAcl(ResourceType resourceType, String resourceId) {
    return _aclCache['${resourceType.code}:$resourceId'];
  }

  /// Remove ACL for resource | إزالة قائمة التحكم في الوصول للمورد
  void removeAcl(ResourceType resourceType, String resourceId) {
    _aclCache.remove('${resourceType.code}:$resourceId');
  }

  /// Clear all cached ACLs | مسح جميع قوائم التحكم المخزنة مؤقتاً
  void clearAclCache() {
    _aclCache.clear();
  }

  // ===========================================================================
  // Resource Hierarchy | هرم الموارد
  // ===========================================================================

  /// Set parent-child relationship | تعيين علاقة الأب-الابن
  void setResourceParent(String childId, String parentId) {
    _resourceHierarchy[parentId] ??= {};
    _resourceHierarchy[parentId]!.add(childId);
  }

  /// Get child resources | الحصول على الموارد الفرعية
  Set<String> getChildResources(String parentId) {
    return _resourceHierarchy[parentId] ?? {};
  }

  // ===========================================================================
  // Private Methods | الدوال الخاصة
  // ===========================================================================

  bool _checkTenantAccess(ResourceType resourceType, String resourceId) {
    if (_user == null) return false;

    final acl = _aclCache['${resourceType.code}:$resourceId'];
    if (acl == null) return true; // No ACL = allow (will be checked elsewhere)

    return acl.tenantId == _user.tenantId;
  }

  bool _checkHierarchicalAccess(
    ResourceType resourceType,
    String resourceId,
    AccessAction action,
  ) {
    final acl = _aclCache['${resourceType.code}:$resourceId'];
    if (acl == null || !acl.inheritFromParent || acl.parentResourceId == null) {
      return false;
    }

    // Recursively check parent
    return checkResourceAccess(
      resourceType: resourceType,
      resourceId: acl.parentResourceId!,
      action: action,
    ).allowed;
  }

  String? _getPermissionForAction(ResourceType resourceType, AccessAction action) {
    // Map resource type + action to permission code
    final mapping = {
      '${ResourceType.field.code}:${AccessAction.view.code}': 'fieldops:field.view',
      '${ResourceType.field.code}:${AccessAction.create.code}': 'fieldops:field.create',
      '${ResourceType.field.code}:${AccessAction.update.code}': 'fieldops:field.edit',
      '${ResourceType.field.code}:${AccessAction.delete.code}': 'fieldops:field.delete',
      '${ResourceType.task.code}:${AccessAction.view.code}': 'fieldops:task.view',
      '${ResourceType.task.code}:${AccessAction.create.code}': 'fieldops:task.create',
      '${ResourceType.task.code}:${AccessAction.update.code}': 'fieldops:task.edit',
      '${ResourceType.task.code}:${AccessAction.delete.code}': 'fieldops:task.delete',
      '${ResourceType.task.code}:${AccessAction.execute.code}': 'fieldops:task.execute',
      '${ResourceType.task.code}:${AccessAction.assign.code}': 'fieldops:task.assign',
      '${ResourceType.user.code}:${AccessAction.view.code}': 'admin:users.view',
      '${ResourceType.user.code}:${AccessAction.manage.code}': 'admin:users.manage',
      '${ResourceType.report.code}:${AccessAction.view.code}': 'reports:view',
      '${ResourceType.report.code}:${AccessAction.export.code}': 'reports:export',
      '${ResourceType.equipment.code}:${AccessAction.view.code}': 'equipment:view',
      '${ResourceType.equipment.code}:${AccessAction.manage.code}': 'equipment:manage',
      '${ResourceType.device.code}:${AccessAction.view.code}': 'iot:device.view',
      '${ResourceType.device.code}:${AccessAction.manage.code}': 'iot:device.manage',
    };

    return mapping['${resourceType.code}:${action.code}'];
  }

  void _audit(
    ResourceType resourceType,
    String resourceId,
    AccessAction action,
    bool allowed,
    String reason,
  ) {
    if (onAudit == null) return;

    onAudit!(AccessAuditEntry(
      userId: _user?.id ?? 'anonymous',
      tenantId: _user?.tenantId ?? '',
      resourceType: resourceType,
      resourceId: resourceId,
      action: action,
      allowed: allowed,
      reason: reason,
      timestamp: DateTime.now(),
    ));
  }
}

// =============================================================================
// Access Decision
// قرار الوصول
// =============================================================================

/// Result of access check
/// نتيجة فحص الوصول
@immutable
class AccessDecision {
  /// Whether access is allowed | هل الوصول مسموح
  final bool allowed;

  /// Reason for decision | سبب القرار
  final String reason;

  /// Reason in Arabic | السبب بالعربية
  final String reasonAr;

  /// Additional conditions that must be met | شروط إضافية يجب استيفاؤها
  final Map<String, dynamic>? conditions;

  const AccessDecision({
    required this.allowed,
    required this.reason,
    required this.reasonAr,
    this.conditions,
  });

  String getLocalizedReason({String locale = 'ar'}) {
    return locale == 'ar' ? reasonAr : reason;
  }
}

// =============================================================================
// Access Audit Entry
// سجل تدقيق الوصول
// =============================================================================

/// Audit entry for access checks
/// سجل تدقيق لفحوصات الوصول
@immutable
class AccessAuditEntry {
  final String userId;
  final String tenantId;
  final ResourceType resourceType;
  final String resourceId;
  final AccessAction action;
  final bool allowed;
  final String reason;
  final DateTime timestamp;

  const AccessAuditEntry({
    required this.userId,
    required this.tenantId,
    required this.resourceType,
    required this.resourceId,
    required this.action,
    required this.allowed,
    required this.reason,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'tenant_id': tenantId,
      'resource_type': resourceType.code,
      'resource_id': resourceId,
      'action': action.code,
      'allowed': allowed,
      'reason': reason,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

// =============================================================================
// Default Field Security Policies
// سياسات أمان الحقول الافتراضية
// =============================================================================

/// Get default field security policies for SAHOOL
/// الحصول على سياسات أمان الحقول الافتراضية لسهول
List<FieldSecurityPolicy> getDefaultFieldSecurityPolicies() {
  return [
    // User sensitive fields
    const FieldSecurityPolicy(
      resourceType: ResourceType.user,
      fieldName: 'password_hash',
      alwaysMasked: true,
      isPII: true,
      isEncrypted: true,
    ),
    const FieldSecurityPolicy(
      resourceType: ResourceType.user,
      fieldName: 'phone',
      isPII: true,
      minRoleToRead: IAMRole.supervisor,
      maskPattern: '***-***-****',
    ),
    const FieldSecurityPolicy(
      resourceType: ResourceType.user,
      fieldName: 'email',
      isPII: true,
      minRoleToRead: IAMRole.supervisor,
    ),
    const FieldSecurityPolicy(
      resourceType: ResourceType.user,
      fieldName: 'national_id',
      isPII: true,
      alwaysMasked: true,
      isEncrypted: true,
    ),

    // Farm/Field sensitive fields
    const FieldSecurityPolicy(
      resourceType: ResourceType.farm,
      fieldName: 'exact_coordinates',
      minRoleToRead: IAMRole.worker,
      minRoleToWrite: IAMRole.supervisor,
    ),
    const FieldSecurityPolicy(
      resourceType: ResourceType.field,
      fieldName: 'soil_analysis_raw',
      minRoleToRead: IAMRole.supervisor,
      permissionsToWrite: {IAMPermission.fieldEdit},
    ),

    // Financial fields
    const FieldSecurityPolicy(
      resourceType: ResourceType.report,
      fieldName: 'cost_breakdown',
      minRoleToRead: IAMRole.manager,
      permissionsToRead: {IAMPermission.billingView},
    ),
    const FieldSecurityPolicy(
      resourceType: ResourceType.marketListing,
      fieldName: 'seller_contact',
      isPII: true,
      minRoleToRead: IAMRole.worker,
    ),
  ];
}
