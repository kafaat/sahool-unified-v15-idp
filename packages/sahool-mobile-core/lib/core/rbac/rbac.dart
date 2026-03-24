// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL RBAC - Role-Based Access Control
// نظام التحكم في الوصول المبني على الأدوار
// ═══════════════════════════════════════════════════════════════════════════
//
// This is the barrel export file for the SAHOOL RBAC system.
// Import this file to access all RBAC functionality.
//
// هذا هو ملف التصدير الرئيسي لنظام التحكم في الوصول.
// استورد هذا الملف للوصول لجميع وظائف التحكم في الوصول.
//
// Usage / الاستخدام:
// ```dart
// import 'package:sahool_mobile_core/core/rbac/rbac.dart';
//
// // Check permissions
// if (rbacService.can(Permissions.fieldsCreate)) {
//   // Create field
// }
//
// // Use in widgets
// RoleGuard(
//   permission: Permissions.tasksView,
//   child: TaskList(),
// )
//
// // Initialize after login
// initializeRbac(ref, userId: 'user123', roleString: 'manager');
// ```

// Role model - الأدوار
export 'role_model.dart';

// Permission model - الصلاحيات
export 'permission_model.dart';

// RBAC configuration - التكوين
export 'rbac_config.dart';

// RBAC service - الخدمة
export 'rbac_service.dart';

// Role guards (widgets) - الحراس
export 'role_guard.dart';

// Riverpod providers - المزودات
export 'rbac_providers.dart' hide RouteGuardService, RouteGuardResult;
