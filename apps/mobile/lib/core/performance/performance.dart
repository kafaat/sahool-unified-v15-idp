/// SAHOOL Performance Core
/// ملفات تحسين الأداء
///
/// يشمل:
/// - إدارة كاش الصور
/// - قوائم محسّنة
/// - إدارة الذاكرة
/// - كاش الشبكة
/// - مراقبة الأداء
/// - جمع المقاييس
/// - تتبع API
/// - لوحة الأداء (للتطوير)
library;

// Core performance utilities
export 'image_cache_manager.dart';
export 'memory_manager.dart';
export 'network_cache.dart';
export 'optimized_list.dart';

// Performance monitoring (debug/profile only)
export 'performance_monitor.dart';
export 'metrics_collector.dart';
export 'api_tracker.dart';
export 'performance_overlay.dart';
