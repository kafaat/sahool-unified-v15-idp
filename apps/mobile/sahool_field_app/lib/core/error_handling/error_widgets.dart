/// SAHOOL Error Display Widgets
/// عناصر عرض الأخطاء لتطبيق سهول
///
/// Provides consistent, user-friendly error display widgets with:
/// - Bilingual support (Arabic/English)
/// - Recovery action buttons
/// - Error type-specific styling
library;

import 'package:flutter/material.dart';
import 'app_exceptions.dart';
import 'error_handler.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Error Snackbar
// ═══════════════════════════════════════════════════════════════════════════

/// Show an error snackbar with proper styling and optional retry action
void showErrorSnackbar(
  BuildContext context,
  AppException error, {
  VoidCallback? onRetry,
  Duration duration = const Duration(seconds: 4),
}) {
  final isRtl = Directionality.of(context) == TextDirection.rtl;
  final displayInfo = getErrorDisplayInfo(error);

  ScaffoldMessenger.of(context).showSnackBar(
    SnackBar(
      content: Row(
        children: [
          Icon(
            _getErrorIcon(error.type),
            color: Colors.white,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  displayInfo.getTitle(isArabic: isRtl),
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  error.getUserMessage(isArabic: isRtl),
                  style: const TextStyle(fontSize: 12),
                ),
              ],
            ),
          ),
        ],
      ),
      backgroundColor: _getErrorColor(error.severity),
      duration: duration,
      action: error.isRetryable && onRetry != null
          ? SnackBarAction(
              label: isRtl ? 'إعادة' : 'Retry',
              textColor: Colors.white,
              onPressed: onRetry,
            )
          : null,
      behavior: SnackBarBehavior.floating,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
    ),
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Error Dialog
// ═══════════════════════════════════════════════════════════════════════════

/// Show an error dialog with details and recovery options
Future<bool?> showErrorDialog(
  BuildContext context,
  AppException error, {
  VoidCallback? onRetry,
  VoidCallback? onDismiss,
  bool showDetails = false,
}) async {
  final isRtl = Directionality.of(context) == TextDirection.rtl;
  final displayInfo = getErrorDisplayInfo(error);

  return showDialog<bool>(
    context: context,
    builder: (context) => AlertDialog(
      icon: Icon(
        _getErrorIcon(error.type),
        color: _getErrorColor(error.severity),
        size: 48,
      ),
      title: Text(
        displayInfo.getTitle(isArabic: isRtl),
        textAlign: TextAlign.center,
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            error.getUserMessage(isArabic: isRtl),
            textAlign: TextAlign.center,
          ),
          if (error.getRecoverySuggestion(isArabic: isRtl) != null) ...[
            const SizedBox(height: 12),
            Text(
              error.getRecoverySuggestion(isArabic: isRtl)!,
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),
          ],
          if (showDetails && error.code != null) ...[
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey.shade100,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'Error code: ${error.code}',
                style: TextStyle(
                  fontSize: 11,
                  fontFamily: 'monospace',
                  color: Colors.grey.shade600,
                ),
              ),
            ),
          ],
        ],
      ),
      actions: [
        if (onDismiss != null || !error.isRetryable)
          TextButton(
            onPressed: () {
              Navigator.of(context).pop(false);
              onDismiss?.call();
            },
            child: Text(isRtl ? 'حسنًا' : 'OK'),
          ),
        if (error.isRetryable && onRetry != null)
          ElevatedButton(
            onPressed: () {
              Navigator.of(context).pop(true);
              onRetry();
            },
            child: Text(isRtl ? 'إعادة المحاولة' : 'Retry'),
          ),
      ],
      actionsAlignment: MainAxisAlignment.center,
    ),
  );
}

// ═══════════════════════════════════════════════════════════════════════════
// Error State Widget
// ═══════════════════════════════════════════════════════════════════════════

/// Widget to display when an error state occurs
class ErrorStateWidget extends StatelessWidget {
  final AppException error;
  final VoidCallback? onRetry;
  final bool compact;

  const ErrorStateWidget({
    super.key,
    required this.error,
    this.onRetry,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final displayInfo = getErrorDisplayInfo(error);
    final theme = Theme.of(context);

    if (compact) {
      return _buildCompact(context, isRtl, displayInfo, theme);
    }

    return _buildFull(context, isRtl, displayInfo, theme);
  }

  Widget _buildCompact(
    BuildContext context,
    bool isRtl,
    ErrorDisplayInfo displayInfo,
    ThemeData theme,
  ) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _getErrorColor(error.severity).withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: _getErrorColor(error.severity).withOpacity(0.3),
        ),
      ),
      child: Row(
        children: [
          Icon(
            _getErrorIcon(error.type),
            color: _getErrorColor(error.severity),
            size: 24,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  displayInfo.getTitle(isArabic: isRtl),
                  style: theme.textTheme.titleSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                Text(
                  error.getUserMessage(isArabic: isRtl),
                  style: theme.textTheme.bodySmall,
                ),
              ],
            ),
          ),
          if (error.isRetryable && onRetry != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: onRetry,
              tooltip: isRtl ? 'إعادة المحاولة' : 'Retry',
            ),
        ],
      ),
    );
  }

  Widget _buildFull(
    BuildContext context,
    bool isRtl,
    ErrorDisplayInfo displayInfo,
    ThemeData theme,
  ) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Error icon
            Container(
              width: 80,
              height: 80,
              decoration: BoxDecoration(
                color: _getErrorColor(error.severity).withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                _getErrorIcon(error.type),
                size: 40,
                color: _getErrorColor(error.severity),
              ),
            ),
            const SizedBox(height: 24),

            // Title
            Text(
              displayInfo.getTitle(isArabic: isRtl),
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 12),

            // Message
            Text(
              error.getUserMessage(isArabic: isRtl),
              style: theme.textTheme.bodyLarge?.copyWith(
                color: Colors.grey.shade600,
              ),
              textAlign: TextAlign.center,
            ),

            // Recovery suggestion
            if (error.getRecoverySuggestion(isArabic: isRtl) != null) ...[
              const SizedBox(height: 8),
              Text(
                error.getRecoverySuggestion(isArabic: isRtl)!,
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: Colors.grey.shade500,
                ),
                textAlign: TextAlign.center,
              ),
            ],

            // Retry button
            if (error.isRetryable && onRetry != null) ...[
              const SizedBox(height: 32),
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh),
                label: Text(isRtl ? 'إعادة المحاولة' : 'Try Again'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 16,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Offline Banner
// ═══════════════════════════════════════════════════════════════════════════

/// Banner to show when the app is offline
class OfflineBanner extends StatelessWidget {
  final VoidCallback? onRetry;

  const OfflineBanner({super.key, this.onRetry});

  @override
  Widget build(BuildContext context) {
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    return Material(
      color: Colors.orange.shade700,
      child: SafeArea(
        bottom: false,
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: [
              const Icon(Icons.wifi_off, color: Colors.white, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  isRtl
                      ? 'أنت غير متصل. البيانات المحفوظة متاحة.'
                      : 'You are offline. Cached data is available.',
                  style: const TextStyle(color: Colors.white, fontSize: 13),
                ),
              ),
              if (onRetry != null)
                TextButton(
                  onPressed: onRetry,
                  style: TextButton.styleFrom(
                    foregroundColor: Colors.white,
                    padding: const EdgeInsets.symmetric(horizontal: 8),
                  ),
                  child: Text(isRtl ? 'إعادة الاتصال' : 'Reconnect'),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Helper Functions
// ═══════════════════════════════════════════════════════════════════════════

IconData _getErrorIcon(ErrorType type) {
  switch (type) {
    case ErrorType.network:
      return Icons.wifi_off;
    case ErrorType.server:
      return Icons.cloud_off;
    case ErrorType.auth:
      return Icons.lock_outline;
    case ErrorType.validation:
      return Icons.warning_amber;
    case ErrorType.notFound:
      return Icons.search_off;
    case ErrorType.rateLimit:
      return Icons.hourglass_empty;
    case ErrorType.security:
      return Icons.security;
    case ErrorType.storage:
      return Icons.storage;
    case ErrorType.sync:
      return Icons.sync_problem;
    case ErrorType.timeout:
      return Icons.timer_off;
    case ErrorType.client:
    case ErrorType.unknown:
      return Icons.error_outline;
  }
}

Color _getErrorColor(ErrorSeverity severity) {
  switch (severity) {
    case ErrorSeverity.info:
      return Colors.blue;
    case ErrorSeverity.warning:
      return Colors.orange;
    case ErrorSeverity.error:
      return Colors.red;
    case ErrorSeverity.critical:
      return Colors.red.shade900;
  }
}
