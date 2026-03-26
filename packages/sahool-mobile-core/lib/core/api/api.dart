/// SAHOOL API Layer - Barrel Export
/// طبقة API الموحدة - تصدير شامل
///
/// This file re-exports all API-related modules for convenient imports.
/// يعيد تصدير جميع وحدات API لتسهيل الاستيراد.
///
/// Usage | الاستخدام:
/// ```dart
/// import 'package:sahool_field_app/core/api/api.dart';
/// ```
library;

// Unified API client (primary entry point)
// عميل API الموحد (نقطة الدخول الرئيسية)
export 'unified_api_client.dart';

// Base API service (singleton, offline queue, bilingual errors)
// خدمة API الأساسية (مفردة، طابور دون اتصال، أخطاء ثنائية اللغة)
export 'api_service.dart';

// Kong gateway client (circuit breaker, health checks, rate limiting)
// عميل بوابة Kong (قاطع الدارة، فحص الصحة، حد المعدل)
export 'kong_gateway_client.dart';
