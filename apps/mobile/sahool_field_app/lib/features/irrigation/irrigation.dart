/// Irrigation Feature - Smart Irrigation Management
/// ميزة الري - إدارة الري الذكي
///
/// Provides comprehensive irrigation management for offline-first agriculture:
/// - Smart irrigation calculations using ET-based methods
/// - Weather-integrated scheduling
/// - Offline-first data management with sync
/// - Sensor-triggered irrigation
/// - Pivot irrigation support
library;

// Data Layer - طبقة البيانات
export 'data/remote/irrigation_api.dart';
export 'data/repositories/irrigation_repository.dart';

// Domain Layer - طبقة النطاق
export 'domain/services/water_calculator.dart';
export 'domain/services/irrigation_scheduler.dart' hide RecommendationType;
export 'domain/services/weather_irrigation_integration.dart';

// Presentation Layer - طبقة العرض
export 'presentation/providers/irrigation_providers.dart';
