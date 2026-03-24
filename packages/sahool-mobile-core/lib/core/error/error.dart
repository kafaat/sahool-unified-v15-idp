/// SAHOOL Error Handling Module
/// وحدة معالجة الأخطاء
///
/// Provides comprehensive error handling for the SAHOOL mobile application:
/// - Error boundary widgets for catching widget tree errors
/// - Fallback UI components for graceful error display
/// - Error reporter for Sentry/analytics integration
/// - Bilingual error messages (Arabic/English)
/// - RTL layout support
///
/// Usage:
/// ```dart
/// import 'package:sahool_mobile_core/core/error/error.dart';
///
/// // Wrap a screen with error boundary
/// ErrorBoundary.screen(
///   screenName: 'HomeScreen',
///   child: HomeScreen(),
/// )
///
/// // Use extension method
/// MyWidget().withErrorBoundary(
///   config: ErrorBoundaryConfig.debug,
/// )
///
/// // Report an error manually
/// errorReporter.reportError(
///   error,
///   stackTrace: stackTrace,
///   severity: ReportSeverity.error,
/// );
/// ```

library;

// Error boundary widgets
export 'error_boundary.dart'
    show
        ErrorBoundary,
        ErrorBoundaryConfig,
        ConsumerErrorBoundary,
        AsyncErrorBoundary,
        WidgetErrorBoundary,
        GlobalErrorHandler,
        ErrorBoundaryExtension;

// Error fallback UI components
export 'error_fallback.dart'
    show
        ErrorFallbackScreen,
        ErrorFallbackWidget,
        ErrorSnackBar,
        ErrorDialog;

// Error messages (bilingual)
export 'error_messages.dart'
    show
        ErrorType,
        ErrorMessage,
        ErrorMessages,
        ErrorMessageLocalization;

// Error reporter service
export 'error_reporter.dart'
    show
        ErrorReporter,
        ErrorReport,
        ErrorContext,
        ReportSeverity,
        errorReporter,
        errorReporterProvider,
        ErrorReporterExtension;
