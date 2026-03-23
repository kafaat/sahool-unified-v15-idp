/// SAHOOL Mobile Core - الحزمة الأساسية المشتركة
///
/// مكتبة موحدة توفر البنية التحتية والميزات المشتركة
/// لجميع تطبيقات سهول على الهاتف.
///
/// Unified library providing shared infrastructure and features
/// for all SAHOOL mobile applications.
///
/// ## Usage
/// ```dart
/// import 'package:sahool_mobile_core/sahool_mobile_core.dart';
/// ```
///
/// ## Architecture
/// ```
/// sahool_mobile_core/
/// ├── core/        ← Infrastructure (45 modules)
/// ├── features/    ← Business features (56+ modules)
/// ├── services/    ← Service layer
/// └── generated/   ← Code generation outputs
/// ```
library sahool_mobile_core;

// ═══════════════════════════════════════════════════════════════════════════
// Core Infrastructure - البنية التحتية الأساسية
// ═══════════════════════════════════════════════════════════════════════════

// Core barrel export (animations, config, state, ui, offline, etc.)
export 'core/exports.dart';

// Authentication - المصادقة
export 'core/auth/auth_service.dart';

// Configuration - التكوين
export 'core/config/env_config.dart';
export 'core/config/theme.dart';

// Crash Reporting - تقارير الأعطال
export 'core/crash/crash_reporter.dart';

// Database - قاعدة البيانات
export 'core/storage/database.dart';

// Error Handling - معالجة الأخطاء
export 'core/error/error.dart';

// IAM - إدارة الهوية والوصول
export 'core/iam/iam.dart';

// RBAC - التحكم بالوصول المبني على الأدوار
export 'core/rbac/rbac.dart';

// Feature Flags - أعلام الميزات
export 'core/feature_flags/feature_flags.dart';

// Persistence - الثبات
export 'core/persistence/app_state_manager.dart';
export 'core/persistence/preferences_manager.dart';
export 'core/persistence/draft_manager.dart';

// Routes - المسارات
export 'core/routes/app_router.dart';

// Security - الأمان
export 'core/security/device_integrity_service.dart';
export 'core/security/security_config.dart';

// Sync - المزامنة
export 'core/sync/sync_engine.dart';
export 'core/sync/background_sync_task.dart';

// Logging - التسجيل
export 'core/logging/logging.dart';

// Validation - التحقق
export 'core/validation/validators.dart';

// Contracts - العقود
export 'core/contracts/service_ports.dart';
export 'core/contracts/error_codes.dart';
export 'core/contracts/api_endpoints.dart';

// Analytics - التحليلات
export 'core/analytics/analytics_service.dart';
