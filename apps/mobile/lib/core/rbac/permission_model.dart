// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL RBAC - Permission Model
// نظام التحكم في الوصول المبني على الأدوار - نموذج الصلاحيات
// ═══════════════════════════════════════════════════════════════════════════
//
// This file defines all permissions in the SAHOOL agricultural platform.
// Permissions are organized by category with CRUD operations.
//
// هذا الملف يحدد جميع الصلاحيات في منصة سهول الزراعية.
// الصلاحيات منظمة حسب الفئة مع عمليات CRUD.

import 'package:flutter/material.dart';

/// Permission action types (CRUD + special)
/// أنواع إجراءات الصلاحيات
enum PermissionAction {
  /// View/Read permission
  view('view', 'عرض'),

  /// Create permission
  create('create', 'إنشاء'),

  /// Update/Edit permission
  update('update', 'تعديل'),

  /// Delete permission
  delete('delete', 'حذف'),

  /// Execute/Run permission (for tasks)
  execute('execute', 'تنفيذ'),

  /// Assign permission (for tasks to users)
  assign('assign', 'تعيين'),

  /// Export permission
  export('export', 'تصدير'),

  /// Sync permission (offline sync)
  sync('sync', 'مزامنة'),

  /// Control permission (for irrigation, IoT)
  control('control', 'تحكم'),

  /// Manage permission (full management)
  manage('manage', 'إدارة');

  final String value;
  final String nameAr;

  const PermissionAction(this.value, this.nameAr);

  String get nameEn => switch (this) {
        PermissionAction.view => 'View',
        PermissionAction.create => 'Create',
        PermissionAction.update => 'Update',
        PermissionAction.delete => 'Delete',
        PermissionAction.execute => 'Execute',
        PermissionAction.assign => 'Assign',
        PermissionAction.export => 'Export',
        PermissionAction.sync => 'Sync',
        PermissionAction.control => 'Control',
        PermissionAction.manage => 'Manage',
      };
}

/// Permission categories in SAHOOL
/// فئات الصلاحيات في سهول
enum PermissionCategory {
  /// Fields management - إدارة الحقول
  fields('fields', 'الحقول', Icons.grass),

  /// Tasks management - إدارة المهام
  tasks('tasks', 'المهام', Icons.task_alt),

  /// Irrigation control - التحكم بالري
  irrigation('irrigation', 'الري', Icons.water_drop),

  /// Weather data - بيانات الطقس
  weather('weather', 'الطقس', Icons.cloud),

  /// Reports and analytics - التقارير والتحليلات
  reports('reports', 'التقارير', Icons.assessment),

  /// User management - إدارة المستخدمين
  users('users', 'المستخدمين', Icons.people),

  /// Settings and configuration - الإعدادات والتكوين
  settings('settings', 'الإعدادات', Icons.settings),

  /// NDVI and vegetation - مؤشر النبات والغطاء الأخضر
  ndvi('ndvi', 'مؤشر النبات', Icons.eco),

  /// IoT devices and sensors - أجهزة الاستشعار
  iot('iot', 'الأجهزة', Icons.sensors),

  /// Chat and communication - المحادثات والتواصل
  chat('chat', 'المحادثات', Icons.chat),

  /// Advisory services - الخدمات الاستشارية
  advisory('advisory', 'الاستشارات', Icons.tips_and_updates),

  /// Billing and payments - الفوترة والمدفوعات
  billing('billing', 'الفوترة', Icons.payment),

  /// Audit and logging - التدقيق والسجلات
  audit('audit', 'التدقيق', Icons.history),

  /// Equipment management - إدارة المعدات
  equipment('equipment', 'المعدات', Icons.construction),

  /// Inventory management - إدارة المخزون
  inventory('inventory', 'المخزون', Icons.inventory),

  /// Offline capabilities - إمكانيات العمل دون اتصال
  offline('offline', 'العمل دون اتصال', Icons.offline_bolt);

  final String value;
  final String nameAr;
  final IconData icon;

  const PermissionCategory(this.value, this.nameAr, this.icon);

  String get nameEn => switch (this) {
        PermissionCategory.fields => 'Fields',
        PermissionCategory.tasks => 'Tasks',
        PermissionCategory.irrigation => 'Irrigation',
        PermissionCategory.weather => 'Weather',
        PermissionCategory.reports => 'Reports',
        PermissionCategory.users => 'Users',
        PermissionCategory.settings => 'Settings',
        PermissionCategory.ndvi => 'NDVI',
        PermissionCategory.iot => 'IoT Devices',
        PermissionCategory.chat => 'Chat',
        PermissionCategory.advisory => 'Advisory',
        PermissionCategory.billing => 'Billing',
        PermissionCategory.audit => 'Audit',
        PermissionCategory.equipment => 'Equipment',
        PermissionCategory.inventory => 'Inventory',
        PermissionCategory.offline => 'Offline',
      };

  String getName(Locale locale) {
    return locale.languageCode == 'ar' ? nameAr : nameEn;
  }
}

/// A permission in the SAHOOL platform
/// صلاحية في منصة سهول
class Permission {
  /// Permission identifier (e.g., 'fields:view')
  final String id;

  /// Category of the permission
  final PermissionCategory category;

  /// Action type
  final PermissionAction action;

  /// English description
  final String descriptionEn;

  /// Arabic description
  final String descriptionAr;

  /// Whether this permission can be used offline
  final bool offlineCapable;

  const Permission({
    required this.id,
    required this.category,
    required this.action,
    required this.descriptionEn,
    required this.descriptionAr,
    this.offlineCapable = false,
  });

  /// Get localized description
  String getDescription(Locale locale) {
    return locale.languageCode == 'ar' ? descriptionAr : descriptionEn;
  }

  /// Create permission ID from category and action
  static String createId(PermissionCategory category, PermissionAction action) {
    return '${category.value}:${action.value}';
  }

  @override
  bool operator ==(Object other) {
    if (identical(this, other)) return true;
    return other is Permission && other.id == id;
  }

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'Permission($id)';
}

/// All permissions in SAHOOL
/// جميع الصلاحيات في سهول
class Permissions {
  // ─────────────────────────────────────────────────────────────────────────
  // Fields Permissions - صلاحيات الحقول
  // ─────────────────────────────────────────────────────────────────────────

  static const fieldsView = Permission(
    id: 'fields:view',
    category: PermissionCategory.fields,
    action: PermissionAction.view,
    descriptionEn: 'View fields and their data',
    descriptionAr: 'عرض الحقول وبياناتها',
    offlineCapable: true,
  );

  static const fieldsCreate = Permission(
    id: 'fields:create',
    category: PermissionCategory.fields,
    action: PermissionAction.create,
    descriptionEn: 'Create new fields',
    descriptionAr: 'إنشاء حقول جديدة',
    offlineCapable: true,
  );

  static const fieldsUpdate = Permission(
    id: 'fields:update',
    category: PermissionCategory.fields,
    action: PermissionAction.update,
    descriptionEn: 'Update field information',
    descriptionAr: 'تحديث معلومات الحقول',
    offlineCapable: true,
  );

  static const fieldsDelete = Permission(
    id: 'fields:delete',
    category: PermissionCategory.fields,
    action: PermissionAction.delete,
    descriptionEn: 'Delete fields',
    descriptionAr: 'حذف الحقول',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Tasks Permissions - صلاحيات المهام
  // ─────────────────────────────────────────────────────────────────────────

  static const tasksView = Permission(
    id: 'tasks:view',
    category: PermissionCategory.tasks,
    action: PermissionAction.view,
    descriptionEn: 'View tasks and assignments',
    descriptionAr: 'عرض المهام والتكليفات',
    offlineCapable: true,
  );

  static const tasksCreate = Permission(
    id: 'tasks:create',
    category: PermissionCategory.tasks,
    action: PermissionAction.create,
    descriptionEn: 'Create new tasks',
    descriptionAr: 'إنشاء مهام جديدة',
    offlineCapable: true,
  );

  static const tasksUpdate = Permission(
    id: 'tasks:update',
    category: PermissionCategory.tasks,
    action: PermissionAction.update,
    descriptionEn: 'Update task details',
    descriptionAr: 'تحديث تفاصيل المهام',
    offlineCapable: true,
  );

  static const tasksDelete = Permission(
    id: 'tasks:delete',
    category: PermissionCategory.tasks,
    action: PermissionAction.delete,
    descriptionEn: 'Delete tasks',
    descriptionAr: 'حذف المهام',
    offlineCapable: false,
  );

  static const tasksExecute = Permission(
    id: 'tasks:execute',
    category: PermissionCategory.tasks,
    action: PermissionAction.execute,
    descriptionEn: 'Execute and complete tasks',
    descriptionAr: 'تنفيذ وإكمال المهام',
    offlineCapable: true,
  );

  static const tasksAssign = Permission(
    id: 'tasks:assign',
    category: PermissionCategory.tasks,
    action: PermissionAction.assign,
    descriptionEn: 'Assign tasks to workers',
    descriptionAr: 'تعيين المهام للعمال',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Irrigation Permissions - صلاحيات الري
  // ─────────────────────────────────────────────────────────────────────────

  static const irrigationView = Permission(
    id: 'irrigation:view',
    category: PermissionCategory.irrigation,
    action: PermissionAction.view,
    descriptionEn: 'View irrigation schedules and status',
    descriptionAr: 'عرض جداول الري والحالة',
    offlineCapable: true,
  );

  static const irrigationControl = Permission(
    id: 'irrigation:control',
    category: PermissionCategory.irrigation,
    action: PermissionAction.control,
    descriptionEn: 'Control irrigation systems',
    descriptionAr: 'التحكم في أنظمة الري',
    offlineCapable: false,
  );

  static const irrigationCreate = Permission(
    id: 'irrigation:create',
    category: PermissionCategory.irrigation,
    action: PermissionAction.create,
    descriptionEn: 'Create irrigation schedules',
    descriptionAr: 'إنشاء جداول الري',
    offlineCapable: true,
  );

  static const irrigationUpdate = Permission(
    id: 'irrigation:update',
    category: PermissionCategory.irrigation,
    action: PermissionAction.update,
    descriptionEn: 'Update irrigation settings',
    descriptionAr: 'تحديث إعدادات الري',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Weather Permissions - صلاحيات الطقس
  // ─────────────────────────────────────────────────────────────────────────

  static const weatherView = Permission(
    id: 'weather:view',
    category: PermissionCategory.weather,
    action: PermissionAction.view,
    descriptionEn: 'View weather data and forecasts',
    descriptionAr: 'عرض بيانات الطقس والتوقعات',
    offlineCapable: true,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Reports Permissions - صلاحيات التقارير
  // ─────────────────────────────────────────────────────────────────────────

  static const reportsView = Permission(
    id: 'reports:view',
    category: PermissionCategory.reports,
    action: PermissionAction.view,
    descriptionEn: 'View reports and analytics',
    descriptionAr: 'عرض التقارير والتحليلات',
    offlineCapable: true,
  );

  static const reportsCreate = Permission(
    id: 'reports:create',
    category: PermissionCategory.reports,
    action: PermissionAction.create,
    descriptionEn: 'Generate reports',
    descriptionAr: 'إنشاء التقارير',
    offlineCapable: false,
  );

  static const reportsExport = Permission(
    id: 'reports:export',
    category: PermissionCategory.reports,
    action: PermissionAction.export,
    descriptionEn: 'Export reports',
    descriptionAr: 'تصدير التقارير',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Users Permissions - صلاحيات المستخدمين
  // ─────────────────────────────────────────────────────────────────────────

  static const usersView = Permission(
    id: 'users:view',
    category: PermissionCategory.users,
    action: PermissionAction.view,
    descriptionEn: 'View user list and profiles',
    descriptionAr: 'عرض قائمة المستخدمين وملفاتهم',
    offlineCapable: false,
  );

  static const usersCreate = Permission(
    id: 'users:create',
    category: PermissionCategory.users,
    action: PermissionAction.create,
    descriptionEn: 'Create new users',
    descriptionAr: 'إنشاء مستخدمين جدد',
    offlineCapable: false,
  );

  static const usersUpdate = Permission(
    id: 'users:update',
    category: PermissionCategory.users,
    action: PermissionAction.update,
    descriptionEn: 'Update user information',
    descriptionAr: 'تحديث معلومات المستخدمين',
    offlineCapable: false,
  );

  static const usersDelete = Permission(
    id: 'users:delete',
    category: PermissionCategory.users,
    action: PermissionAction.delete,
    descriptionEn: 'Delete users',
    descriptionAr: 'حذف المستخدمين',
    offlineCapable: false,
  );

  static const usersManage = Permission(
    id: 'users:manage',
    category: PermissionCategory.users,
    action: PermissionAction.manage,
    descriptionEn: 'Full user management',
    descriptionAr: 'إدارة المستخدمين الكاملة',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Settings Permissions - صلاحيات الإعدادات
  // ─────────────────────────────────────────────────────────────────────────

  static const settingsView = Permission(
    id: 'settings:view',
    category: PermissionCategory.settings,
    action: PermissionAction.view,
    descriptionEn: 'View application settings',
    descriptionAr: 'عرض إعدادات التطبيق',
    offlineCapable: true,
  );

  static const settingsUpdate = Permission(
    id: 'settings:update',
    category: PermissionCategory.settings,
    action: PermissionAction.update,
    descriptionEn: 'Update application settings',
    descriptionAr: 'تحديث إعدادات التطبيق',
    offlineCapable: false,
  );

  static const settingsManage = Permission(
    id: 'settings:manage',
    category: PermissionCategory.settings,
    action: PermissionAction.manage,
    descriptionEn: 'Full settings management',
    descriptionAr: 'إدارة الإعدادات الكاملة',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // NDVI Permissions - صلاحيات مؤشر النبات
  // ─────────────────────────────────────────────────────────────────────────

  static const ndviView = Permission(
    id: 'ndvi:view',
    category: PermissionCategory.ndvi,
    action: PermissionAction.view,
    descriptionEn: 'View NDVI data and maps',
    descriptionAr: 'عرض بيانات وخرائط مؤشر النبات',
    offlineCapable: true,
  );

  static const ndviCreate = Permission(
    id: 'ndvi:create',
    category: PermissionCategory.ndvi,
    action: PermissionAction.create,
    descriptionEn: 'Request NDVI analysis',
    descriptionAr: 'طلب تحليل مؤشر النبات',
    offlineCapable: false,
  );

  static const ndviExport = Permission(
    id: 'ndvi:export',
    category: PermissionCategory.ndvi,
    action: PermissionAction.export,
    descriptionEn: 'Export NDVI reports',
    descriptionAr: 'تصدير تقارير مؤشر النبات',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // IoT Permissions - صلاحيات أجهزة الاستشعار
  // ─────────────────────────────────────────────────────────────────────────

  static const iotView = Permission(
    id: 'iot:view',
    category: PermissionCategory.iot,
    action: PermissionAction.view,
    descriptionEn: 'View IoT devices and sensor data',
    descriptionAr: 'عرض الأجهزة وبيانات الاستشعار',
    offlineCapable: true,
  );

  static const iotCreate = Permission(
    id: 'iot:create',
    category: PermissionCategory.iot,
    action: PermissionAction.create,
    descriptionEn: 'Register new IoT devices',
    descriptionAr: 'تسجيل أجهزة جديدة',
    offlineCapable: false,
  );

  static const iotUpdate = Permission(
    id: 'iot:update',
    category: PermissionCategory.iot,
    action: PermissionAction.update,
    descriptionEn: 'Update IoT device settings',
    descriptionAr: 'تحديث إعدادات الأجهزة',
    offlineCapable: false,
  );

  static const iotManage = Permission(
    id: 'iot:manage',
    category: PermissionCategory.iot,
    action: PermissionAction.manage,
    descriptionEn: 'Full IoT device management',
    descriptionAr: 'إدارة الأجهزة الكاملة',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Chat Permissions - صلاحيات المحادثات
  // ─────────────────────────────────────────────────────────────────────────

  static const chatView = Permission(
    id: 'chat:view',
    category: PermissionCategory.chat,
    action: PermissionAction.view,
    descriptionEn: 'View chat messages',
    descriptionAr: 'عرض رسائل المحادثات',
    offlineCapable: true,
  );

  static const chatCreate = Permission(
    id: 'chat:create',
    category: PermissionCategory.chat,
    action: PermissionAction.create,
    descriptionEn: 'Send chat messages',
    descriptionAr: 'إرسال رسائل المحادثات',
    offlineCapable: true,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Advisory Permissions - صلاحيات الاستشارات
  // ─────────────────────────────────────────────────────────────────────────

  static const advisoryView = Permission(
    id: 'advisory:view',
    category: PermissionCategory.advisory,
    action: PermissionAction.view,
    descriptionEn: 'View advisory recommendations',
    descriptionAr: 'عرض التوصيات الاستشارية',
    offlineCapable: true,
  );

  static const advisoryCreate = Permission(
    id: 'advisory:create',
    category: PermissionCategory.advisory,
    action: PermissionAction.create,
    descriptionEn: 'Create advisory recommendations',
    descriptionAr: 'إنشاء التوصيات الاستشارية',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Billing Permissions - صلاحيات الفوترة
  // ─────────────────────────────────────────────────────────────────────────

  static const billingView = Permission(
    id: 'billing:view',
    category: PermissionCategory.billing,
    action: PermissionAction.view,
    descriptionEn: 'View billing information',
    descriptionAr: 'عرض معلومات الفوترة',
    offlineCapable: false,
  );

  static const billingManage = Permission(
    id: 'billing:manage',
    category: PermissionCategory.billing,
    action: PermissionAction.manage,
    descriptionEn: 'Manage billing and payments',
    descriptionAr: 'إدارة الفوترة والمدفوعات',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Audit Permissions - صلاحيات التدقيق
  // ─────────────────────────────────────────────────────────────────────────

  static const auditView = Permission(
    id: 'audit:view',
    category: PermissionCategory.audit,
    action: PermissionAction.view,
    descriptionEn: 'View audit logs',
    descriptionAr: 'عرض سجلات التدقيق',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Equipment Permissions - صلاحيات المعدات
  // ─────────────────────────────────────────────────────────────────────────

  static const equipmentView = Permission(
    id: 'equipment:view',
    category: PermissionCategory.equipment,
    action: PermissionAction.view,
    descriptionEn: 'View equipment and machinery',
    descriptionAr: 'عرض المعدات والآلات',
    offlineCapable: true,
  );

  static const equipmentCreate = Permission(
    id: 'equipment:create',
    category: PermissionCategory.equipment,
    action: PermissionAction.create,
    descriptionEn: 'Register new equipment',
    descriptionAr: 'تسجيل معدات جديدة',
    offlineCapable: false,
  );

  static const equipmentUpdate = Permission(
    id: 'equipment:update',
    category: PermissionCategory.equipment,
    action: PermissionAction.update,
    descriptionEn: 'Update equipment information',
    descriptionAr: 'تحديث معلومات المعدات',
    offlineCapable: false,
  );

  static const equipmentDelete = Permission(
    id: 'equipment:delete',
    category: PermissionCategory.equipment,
    action: PermissionAction.delete,
    descriptionEn: 'Delete equipment',
    descriptionAr: 'حذف المعدات',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Inventory Permissions - صلاحيات المخزون
  // ─────────────────────────────────────────────────────────────────────────

  static const inventoryView = Permission(
    id: 'inventory:view',
    category: PermissionCategory.inventory,
    action: PermissionAction.view,
    descriptionEn: 'View inventory items',
    descriptionAr: 'عرض عناصر المخزون',
    offlineCapable: true,
  );

  static const inventoryCreate = Permission(
    id: 'inventory:create',
    category: PermissionCategory.inventory,
    action: PermissionAction.create,
    descriptionEn: 'Add inventory items',
    descriptionAr: 'إضافة عناصر المخزون',
    offlineCapable: true,
  );

  static const inventoryUpdate = Permission(
    id: 'inventory:update',
    category: PermissionCategory.inventory,
    action: PermissionAction.update,
    descriptionEn: 'Update inventory items',
    descriptionAr: 'تحديث عناصر المخزون',
    offlineCapable: true,
  );

  static const inventoryDelete = Permission(
    id: 'inventory:delete',
    category: PermissionCategory.inventory,
    action: PermissionAction.delete,
    descriptionEn: 'Delete inventory items',
    descriptionAr: 'حذف عناصر المخزون',
    offlineCapable: false,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // Offline Permissions - صلاحيات العمل دون اتصال
  // ─────────────────────────────────────────────────────────────────────────

  static const offlineSync = Permission(
    id: 'offline:sync',
    category: PermissionCategory.offline,
    action: PermissionAction.sync,
    descriptionEn: 'Sync data offline',
    descriptionAr: 'مزامنة البيانات دون اتصال',
    offlineCapable: true,
  );

  static const offlineExport = Permission(
    id: 'offline:export',
    category: PermissionCategory.offline,
    action: PermissionAction.export,
    descriptionEn: 'Export data for offline use',
    descriptionAr: 'تصدير البيانات للعمل دون اتصال',
    offlineCapable: true,
  );

  // ─────────────────────────────────────────────────────────────────────────
  // All Permissions List
  // ─────────────────────────────────────────────────────────────────────────

  /// Get all defined permissions
  static List<Permission> get all => [
        // Fields
        fieldsView,
        fieldsCreate,
        fieldsUpdate,
        fieldsDelete,
        // Tasks
        tasksView,
        tasksCreate,
        tasksUpdate,
        tasksDelete,
        tasksExecute,
        tasksAssign,
        // Irrigation
        irrigationView,
        irrigationControl,
        irrigationCreate,
        irrigationUpdate,
        // Weather
        weatherView,
        // Reports
        reportsView,
        reportsCreate,
        reportsExport,
        // Users
        usersView,
        usersCreate,
        usersUpdate,
        usersDelete,
        usersManage,
        // Settings
        settingsView,
        settingsUpdate,
        settingsManage,
        // NDVI
        ndviView,
        ndviCreate,
        ndviExport,
        // IoT
        iotView,
        iotCreate,
        iotUpdate,
        iotManage,
        // Chat
        chatView,
        chatCreate,
        // Advisory
        advisoryView,
        advisoryCreate,
        // Billing
        billingView,
        billingManage,
        // Audit
        auditView,
        // Equipment
        equipmentView,
        equipmentCreate,
        equipmentUpdate,
        equipmentDelete,
        // Inventory
        inventoryView,
        inventoryCreate,
        inventoryUpdate,
        inventoryDelete,
        // Offline
        offlineSync,
        offlineExport,
      ];

  /// Get permissions by category
  static List<Permission> getByCategory(PermissionCategory category) {
    return all.where((p) => p.category == category).toList();
  }

  /// Get permissions by action
  static List<Permission> getByAction(PermissionAction action) {
    return all.where((p) => p.action == action).toList();
  }

  /// Get offline-capable permissions
  static List<Permission> get offlineCapable {
    return all.where((p) => p.offlineCapable).toList();
  }

  /// Find permission by ID
  static Permission? findById(String id) {
    try {
      return all.firstWhere((p) => p.id == id);
    } catch (_) {
      return null;
    }
  }
}

/// Permission set for easy checking
/// مجموعة الصلاحيات للتحقق السهل
class PermissionSet {
  final Set<String> _permissionIds;

  PermissionSet(Iterable<Permission> permissions)
      : _permissionIds = permissions.map((p) => p.id).toSet();

  PermissionSet.fromIds(Iterable<String> ids) : _permissionIds = ids.toSet();

  /// Check if permission is in set
  bool has(Permission permission) => _permissionIds.contains(permission.id);

  /// Check if permission ID is in set
  bool hasId(String id) => _permissionIds.contains(id);

  /// Check if any of the permissions is in set
  bool hasAny(Iterable<Permission> permissions) {
    return permissions.any((p) => _permissionIds.contains(p.id));
  }

  /// Check if all of the permissions are in set
  bool hasAll(Iterable<Permission> permissions) {
    return permissions.every((p) => _permissionIds.contains(p.id));
  }

  /// Get all permission IDs
  Set<String> get ids => Set.unmodifiable(_permissionIds);

  /// Get all permissions
  List<Permission> get permissions {
    return _permissionIds
        .map((id) => Permissions.findById(id))
        .whereType<Permission>()
        .toList();
  }

  /// Get count of permissions
  int get length => _permissionIds.length;

  /// Check if empty
  bool get isEmpty => _permissionIds.isEmpty;

  /// Check if not empty
  bool get isNotEmpty => _permissionIds.isNotEmpty;
}
