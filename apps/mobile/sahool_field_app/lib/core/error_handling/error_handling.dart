/// SAHOOL Error Handling Module
/// وحدة معالجة الأخطاء لتطبيق سهول
///
/// Central export file for all error handling components.
///
/// Usage:
/// ```dart
/// import 'package:sahool_field_app/core/error_handling/error_handling.dart';
/// ```
///
/// Features:
/// - Unified exception hierarchy with bilingual messages
/// - Error categorization for analytics
/// - Recovery strategies and retry mechanisms
/// - User-facing error display widgets
/// - Error boundary for widget tree protection
library;

// Core exception types
export 'app_exceptions.dart';

// Error handler and recovery utilities
export 'error_handler.dart';

// Error boundary widget
export 'error_boundary.dart';

// Error display widgets
export 'error_widgets.dart';
