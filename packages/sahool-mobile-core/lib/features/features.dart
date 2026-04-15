/// SAHOOL Features - All Feature Module Barrel Exports
/// ميزات سهول - تصدير جميع وحدات الميزات
///
/// Master barrel file for all feature modules in the SAHOOL mobile core package.
/// Import this file to access any feature module.
///
/// Usage:
/// ```dart
/// import 'package:sahool_mobile_core/features/features.dart';
/// ```
library;

// ============================================================================
// Agricultural Core - الزراعة الأساسية
// ============================================================================

/// Field management, health monitoring, and zone visualization
export 'field/field.dart';

/// Field listing and details views
export 'fields/fields.dart';

/// Unified field dashboard view
export 'field_hub/field_hub.dart';

/// Field scouting sessions and observations
export 'field_scout/field_scout.dart';

/// Crop management and information
export 'crops/crops.dart';

/// Crop health diagnosis and monitoring
export 'crop_health/crop_health.dart';

/// Crop rotation planning
export 'rotation/rotation.dart';

/// Irrigation scheduling and water balance
export 'irrigation/irrigation.dart';

/// Center pivot irrigation management
export 'pivot_irrigation/pivot_irrigation.dart';

/// Spray scheduling and weather window analysis
export 'spray/spray.dart';

/// Growing Degree Days tracking
export 'gdd/gdd.dart';

/// Variable Rate Application maps
export 'vra/vra.dart';

/// Soil analysis lab sample tracking
export 'lab/lab.dart';

// ============================================================================
// Intelligence & Satellite - الذكاء والأقمار الصناعية
// ============================================================================

/// NDVI and spectral index analysis
export 'ndvi/ndvi.dart';

/// Satellite imagery and phenology analysis
export 'satellite/satellite.dart';

/// On-device YOLO26 vision for pest/disease detection
export 'vision/vision.dart';

/// Terrain analysis and elevation profiles
export 'terrain/terrain.dart';

/// Virtual sensor data and visualization
export 'virtual_sensors/virtual_sensors.dart';

/// IoT device management and control
export 'iot/iot.dart';

// ============================================================================
// Advisory & AI - الاستشارات والذكاء الاصطناعي
// ============================================================================

/// Agricultural advisor with fertilizer and irrigation recommendations
export 'advisor/advisor.dart';

/// AI-powered advisory with chat interface
export 'ai_advisor/ai_advisor.dart';

/// Daily farm briefing
export 'daily_brief/daily_brief.dart';

/// Smart AI-powered alerts
export 'smart_alerts/smart_alerts.dart';

// ============================================================================
// Weather & Astronomy - الطقس والفلك
// ============================================================================

/// Weather forecasts, alerts, and agricultural impact
export 'weather/weather.dart';

/// Astronomical calendar with lunar mansions
export 'astronomical/astronomical.dart';

/// Astronomical calendar entities and data
export 'astronomical_calendar/astronomical_calendar.dart';

// ============================================================================
// Operations - العمليات
// ============================================================================

/// Task management with astronomical integration
export 'tasks/tasks.dart';

/// Equipment tracking, maintenance, and fuel logging
export 'equipment/equipment.dart';

/// Inventory management with barcode scanning
export 'inventory/inventory.dart';

/// Barcode and QR code scanning
export 'scanner/scanner.dart';

/// Field scouting and observation recording
export 'scouting/scouting.dart';

/// Report builder, viewer, and sharing
export 'reports/reports.dart';

/// Crop profitability analysis
export 'profitability/profitability.dart';

/// Field analytics and NDVI trends
export 'analytics/analytics.dart';

/// Research experiments and daily observations
export 'research/research.dart';

// ============================================================================
// Maps & Geospatial - الخرائط والمكانية
// ============================================================================

/// Offline maps with region download
export 'maps/maps.dart';

/// Main map view with field context
export 'map_home/map_home.dart';

/// Polygon editor for field boundaries
export 'polygon_editor/polygon_editor.dart';

// ============================================================================
// Business & Marketplace - الأعمال والسوق
// ============================================================================

/// Agricultural marketplace
export 'marketplace/marketplace.dart';

/// Market prices and harvest selling
export 'market/market.dart';

/// Billing plans and subscription management
export 'billing/billing.dart';

/// Payment gateway integration
export 'payment/payment.dart';

/// Digital wallet management
export 'wallet/wallet.dart';

/// Farmer CRM with profiles and interactions
export 'crm/crm.dart';

/// Gamification and achievements
export 'gamification/gamification.dart';

// ============================================================================
// Communication - التواصل
// ============================================================================

/// Real-time messaging with location sharing
export 'chat/chat.dart';

/// Community chat and social features
export 'community/community.dart';

/// Notification center with settings
export 'notifications/notifications.dart';

/// Alert management and display
export 'alerts/alerts.dart';

// ============================================================================
// User & App - المستخدم والتطبيق
// ============================================================================

/// Authentication, OTP, and biometric login
export 'auth/auth.dart';

/// User profile management
export 'profile/profile.dart';

/// Application settings and preferences
export 'settings/settings.dart';

/// Onboarding flow for new users
export 'onboarding/onboarding.dart';

/// Splash screen
export 'splash/splash.dart';

/// Offline sync with conflict resolution
export 'sync/sync.dart';

// ============================================================================
// Layout & Navigation - التخطيط والتنقل
// ============================================================================

/// Main app layout and navigation
export 'main_layout/main_layout.dart';

/// Home dashboard
export 'home/home.dart';

/// Home v16 redesign
export 'home_v16/home_v16.dart';

// ============================================================================
// Shared - مشترك
// ============================================================================

/// Shared widgets used across features
export 'shared/shared.dart';
