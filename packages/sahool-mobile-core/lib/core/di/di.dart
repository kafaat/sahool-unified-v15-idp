// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Dependency Injection Barrel Export
// تصدير حقن التبعيات
// ═══════════════════════════════════════════════════════════════════════════
//
// Single import for all DI-related providers:
// استيراد واحد لجميع مزودات حقن التبعيات:
//
//   import 'package:sahool_mobile_core/core/di/di.dart';
//
// ═══════════════════════════════════════════════════════════════════════════
library;

/// Core providers (database, sync, auth, env, crash reporter, api client)
/// المزودات الأساسية (قاعدة البيانات، المزامنة، المصادقة، البيئة، الأعطال، عميل API)
export 'core_providers.dart';

/// Existing providers (fields repo, fields API, fields stream, etc.)
/// المزودات الحالية (مستودع الحقول، واجهة الحقول، تدفق الحقول، إلخ)
export 'providers.dart';
