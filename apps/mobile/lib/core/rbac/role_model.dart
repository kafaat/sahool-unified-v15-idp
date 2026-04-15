// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL RBAC - Role Model
// نظام التحكم في الوصول المبني على الأدوار - نموذج الأدوار
// ═══════════════════════════════════════════════════════════════════════════
//
// This file defines the role hierarchy for the SAHOOL agricultural platform.
// Roles are hierarchical: higher roles inherit all permissions from lower roles.
//
// هذا الملف يحدد التسلسل الهرمي للأدوار في منصة سهول الزراعية.
// الأدوار هرمية: الأدوار الأعلى ترث جميع الصلاحيات من الأدوار الأدنى.

import 'package:flutter/material.dart';

/// Role in the SAHOOL platform
/// الدور في منصة سهول
enum Role {
  /// Guest - Limited read-only access
  /// ضيف - وصول قراءة فقط محدود
  guest('guest', 'ضيف', 0),

  /// Viewer - Read-only access to most features
  /// مشاهد - وصول قراءة فقط لمعظم الميزات
  viewer('viewer', 'مشاهد', 1),

  /// Field Worker - Execute tasks, view assigned fields
  /// عامل حقل - تنفيذ المهام، عرض الحقول المخصصة
  fieldWorker('field_worker', 'عامل حقل', 2),

  /// Agronomist - Advisory, reports, all field data
  /// مهندس زراعي - استشارات، تقارير، جميع بيانات الحقول
  agronomist('agronomist', 'مهندس زراعي', 3),

  /// Manager - Manage fields, tasks, workers
  /// مشرف - إدارة الحقول والمهام والعمال
  manager('manager', 'مشرف', 4),

  /// Admin - Full access to tenant
  /// مدير - وصول كامل للمستأجر
  admin('admin', 'مدير', 5);

  /// Internal value (for API/storage)
  final String value;

  /// Arabic display name
  final String nameAr;

  /// Hierarchy level (higher = more permissions)
  final int level;

  const Role(this.value, this.nameAr, this.level);

  /// Get English display name
  String get nameEn => switch (this) {
        Role.guest => 'Guest',
        Role.viewer => 'Viewer',
        Role.fieldWorker => 'Field Worker',
        Role.agronomist => 'Agronomist',
        Role.manager => 'Manager',
        Role.admin => 'Administrator',
      };

  /// Get localized name based on locale
  String getName(Locale locale) {
    return locale.languageCode == 'ar' ? nameAr : nameEn;
  }

  /// Get role description in English
  String get descriptionEn => switch (this) {
        Role.guest => 'Limited access for visitors',
        Role.viewer => 'Read-only access to view data',
        Role.fieldWorker => 'Execute assigned tasks and operations',
        Role.agronomist => 'Provide advisory and generate reports',
        Role.manager => 'Manage fields, tasks, and workers',
        Role.admin => 'Full administrative access',
      };

  /// Get role description in Arabic
  String get descriptionAr => switch (this) {
        Role.guest => 'وصول محدود للزوار',
        Role.viewer => 'وصول للقراءة فقط لعرض البيانات',
        Role.fieldWorker => 'تنفيذ المهام والعمليات المخصصة',
        Role.agronomist => 'تقديم الاستشارات وإنشاء التقارير',
        Role.manager => 'إدارة الحقول والمهام والعمال',
        Role.admin => 'وصول إداري كامل',
      };

  /// Get localized description based on locale
  String getDescription(Locale locale) {
    return locale.languageCode == 'ar' ? descriptionAr : descriptionEn;
  }

  /// Get icon for the role
  IconData get icon => switch (this) {
        Role.guest => Icons.person_outline,
        Role.viewer => Icons.visibility,
        Role.fieldWorker => Icons.agriculture,
        Role.agronomist => Icons.science,
        Role.manager => Icons.supervisor_account,
        Role.admin => Icons.admin_panel_settings,
      };

  /// Get color for the role
  Color get color => switch (this) {
        Role.guest => Colors.grey,
        Role.viewer => Colors.blue,
        Role.fieldWorker => Colors.green,
        Role.agronomist => Colors.orange,
        Role.manager => Colors.purple,
        Role.admin => Colors.red,
      };

  /// Check if this role is at least as high as another role
  /// التحقق مما إذا كان هذا الدور على الأقل بمستوى دور آخر
  bool isAtLeast(Role other) => level >= other.level;

  /// Check if this role is higher than another role
  /// التحقق مما إذا كان هذا الدور أعلى من دور آخر
  bool isHigherThan(Role other) => level > other.level;

  /// Check if this role is lower than another role
  /// التحقق مما إذا كان هذا الدور أدنى من دور آخر
  bool isLowerThan(Role other) => level < other.level;

  /// Get all roles this role inherits from
  /// الحصول على جميع الأدوار التي يرثها هذا الدور
  List<Role> get inheritedRoles {
    return Role.values.where((r) => r.level < level).toList();
  }

  /// Get all roles that inherit from this role
  /// الحصول على جميع الأدوار التي ترث من هذا الدور
  List<Role> get inheritingRoles {
    return Role.values.where((r) => r.level > level).toList();
  }

  /// Parse role from string value
  /// تحليل الدور من قيمة نصية
  static Role fromString(String value) {
    return Role.values.firstWhere(
      (r) => r.value == value || r.name == value,
      orElse: () => Role.guest,
    );
  }

  /// Try to parse role from string, returns null if not found
  /// محاولة تحليل الدور من نص، يُرجع null إذا لم يُعثر عليه
  static Role? tryParse(String? value) {
    if (value == null) return null;
    try {
      return Role.values.firstWhere(
        (r) => r.value == value || r.name == value,
      );
    } catch (e) {
      return null;
    }
  }
}

/// Role hierarchy utilities
/// أدوات التسلسل الهرمي للأدوار
class RoleHierarchy {
  /// Get the minimum role required for a given level
  /// الحصول على الحد الأدنى من الدور المطلوب لمستوى معين
  static Role getMinimumRoleForLevel(int level) {
    return Role.values.firstWhere(
      (r) => r.level >= level,
      orElse: () => Role.admin,
    );
  }

  /// Get all roles at or above a given role
  /// الحصول على جميع الأدوار بمستوى معين أو أعلى
  static List<Role> getRolesAtOrAbove(Role role) {
    return Role.values.where((r) => r.level >= role.level).toList();
  }

  /// Get all roles below a given role
  /// الحصول على جميع الأدوار دون مستوى معين
  static List<Role> getRolesBelow(Role role) {
    return Role.values.where((r) => r.level < role.level).toList();
  }

  /// Check if source role can manage target role
  /// التحقق مما إذا كان دور المصدر يمكنه إدارة الدور الهدف
  static bool canManage(Role source, Role target) {
    // Only admin can manage other admins
    if (target == Role.admin) {
      return source == Role.admin;
    }
    // Must be higher level to manage
    return source.level > target.level;
  }

  /// Get the highest role from a list
  /// الحصول على أعلى دور من قائمة
  static Role getHighestRole(List<Role> roles) {
    if (roles.isEmpty) return Role.guest;
    return roles.reduce((a, b) => a.level >= b.level ? a : b);
  }

  /// Get the lowest role from a list
  /// الحصول على أدنى دور من قائمة
  static Role getLowestRole(List<Role> roles) {
    if (roles.isEmpty) return Role.guest;
    return roles.reduce((a, b) => a.level <= b.level ? a : b);
  }
}

/// Extension methods for Role
/// طرق الامتداد للدور
extension RoleExtension on Role {
  /// Check if role can view data
  /// التحقق مما إذا كان الدور يمكنه عرض البيانات
  bool get canView => level >= Role.viewer.level;

  /// Check if role can edit data
  /// التحقق مما إذا كان الدور يمكنه تعديل البيانات
  bool get canEdit => level >= Role.fieldWorker.level;

  /// Check if role can create data
  /// التحقق مما إذا كان الدور يمكنه إنشاء البيانات
  bool get canCreate => level >= Role.manager.level;

  /// Check if role can delete data
  /// التحقق مما إذا كان الدور يمكنه حذف البيانات
  bool get canDelete => level >= Role.manager.level;

  /// Check if role can manage users
  /// التحقق مما إذا كان الدور يمكنه إدارة المستخدمين
  bool get canManageUsers => level >= Role.admin.level;

  /// Check if role can generate reports
  /// التحقق مما إذا كان الدور يمكنه إنشاء التقارير
  bool get canGenerateReports => level >= Role.agronomist.level;

  /// Check if role can provide advisory
  /// التحقق مما إذا كان الدور يمكنه تقديم الاستشارات
  bool get canProvideAdvisory => level >= Role.agronomist.level;

  /// Check if role has offline capabilities
  /// التحقق مما إذا كان الدور لديه إمكانيات العمل دون اتصال
  bool get hasOfflineCapabilities => level >= Role.fieldWorker.level;
}
