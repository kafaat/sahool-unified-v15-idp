/// SAHOOL Services Layer
/// طبقة الخدمات المحسنة
///
/// This barrel file exports all service-related classes,
/// connectors, and providers for the SAHOOL mobile app.
///
/// Usage:
/// ```dart
/// import 'package:sahool_mobile_core/core/services/services.dart';
/// ```
library;

// Core Service Infrastructure
export 'service_registry.dart';
export 'service_connector.dart';
export 'service_health.dart';

// Real-time Communication
export 'websocket_manager.dart';
export 'event_bus.dart';

// Service Integrations
export 'integrations/integrations.dart';

// Existing Services
export 'auth_service.dart';
export 'sync_service.dart';
export 'crash_reporting_service.dart';
export 'map_provider_service.dart';
export 'tile_service.dart';
export 'weather_provider_service.dart' hide ForecastDay;
