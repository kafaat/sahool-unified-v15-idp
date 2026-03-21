/// SAHOOL Error Fallback UI Widgets
/// واجهات المستخدم الاحتياطية للأخطاء
///
/// Provides user-friendly fallback UI components when errors occur.
/// Supports RTL layout for Arabic language and bilingual text.
library;

import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../config/theme.dart';
import 'error_messages.dart';

/// Full-screen error fallback widget
class ErrorFallbackScreen extends StatelessWidget {
  /// The error that occurred
  final Object error;

  /// Stack trace for debugging
  final StackTrace? stackTrace;

  /// Callback when retry is pressed
  final VoidCallback? onRetry;

  /// Callback when go back is pressed
  final VoidCallback? onGoBack;

  /// Custom error message override
  final ErrorMessage? errorMessage;

  /// Whether to show debug information
  final bool showDebugInfo;

  /// Custom title override
  final String? title;

  /// Custom message override
  final String? message;

  const ErrorFallbackScreen({
    super.key,
    required this.error,
    this.stackTrace,
    this.onRetry,
    this.onGoBack,
    this.errorMessage,
    this.showDebugInfo = false,
    this.title,
    this.message,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final isRtl = locale.languageCode == 'ar';
    final theme = Theme.of(context);
    final errMsg = errorMessage ?? ErrorMessages.fromException(error);

    return Directionality(
      textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
      child: Scaffold(
        backgroundColor: theme.scaffoldBackgroundColor,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const Spacer(),

                // Error icon with animation
                _ErrorIcon(
                  icon: errMsg.icon,
                  color: errMsg.color ?? SahoolTheme.error,
                ),
                const SizedBox(height: 32),

                // Error title
                Text(
                  title ?? errMsg.getTitle(locale),
                  style: theme.textTheme.headlineSmall?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: theme.colorScheme.onSurface,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 16),

                // Error message
                Text(
                  message ?? errMsg.getMessage(locale),
                  style: theme.textTheme.bodyLarge?.copyWith(
                    color: Colors.grey[600],
                    height: 1.5,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 32),

                // Action buttons
                _ActionButtons(
                  locale: locale,
                  onRetry: onRetry,
                  onGoBack: onGoBack,
                  errorMessage: errMsg,
                ),

                const Spacer(),

                // Debug info toggle
                if (showDebugInfo || kDebugMode)
                  _DebugInfoSection(
                    error: error,
                    stackTrace: stackTrace,
                    locale: locale,
                  ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

/// Compact error fallback widget for inline use
class ErrorFallbackWidget extends StatelessWidget {
  /// The error that occurred
  final Object error;

  /// Stack trace for debugging
  final StackTrace? stackTrace;

  /// Callback when retry is pressed
  final VoidCallback? onRetry;

  /// Custom error message override
  final ErrorMessage? errorMessage;

  /// Whether to show in compact mode
  final bool compact;

  /// Custom icon size
  final double? iconSize;

  const ErrorFallbackWidget({
    super.key,
    required this.error,
    this.stackTrace,
    this.onRetry,
    this.errorMessage,
    this.compact = false,
    this.iconSize,
  });

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context);
    final isRtl = locale.languageCode == 'ar';
    final theme = Theme.of(context);
    final errMsg = errorMessage ?? ErrorMessages.fromException(error);

    if (compact) {
      return _CompactErrorWidget(
        errMsg: errMsg,
        locale: locale,
        onRetry: onRetry,
        theme: theme,
        isRtl: isRtl,
      );
    }

    return Directionality(
      textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
      child: Center(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Error icon
              Container(
                width: iconSize ?? 64,
                height: iconSize ?? 64,
                decoration: BoxDecoration(
                  color: (errMsg.color ?? SahoolTheme.error).withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: Icon(
                  errMsg.icon,
                  size: (iconSize ?? 64) * 0.5,
                  color: errMsg.color ?? SahoolTheme.error,
                ),
              ),
              const SizedBox(height: 16),

              // Error title
              Text(
                errMsg.getTitle(locale),
                style: theme.textTheme.titleMedium?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 8),

              // Error message
              Text(
                errMsg.getMessage(locale),
                style: theme.textTheme.bodyMedium?.copyWith(
                  color: Colors.grey[600],
                ),
                textAlign: TextAlign.center,
              ),

              // Retry button
              if (onRetry != null) ...[
                const SizedBox(height: 16),
                TextButton.icon(
                  onPressed: onRetry,
                  icon: const Icon(Icons.refresh),
                  label: Text(
                    errMsg.getAction(locale) ?? ErrorMessages.retryEn,
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}

/// Compact error widget for list items or small spaces
class _CompactErrorWidget extends StatelessWidget {
  final ErrorMessage errMsg;
  final Locale locale;
  final VoidCallback? onRetry;
  final ThemeData theme;
  final bool isRtl;

  const _CompactErrorWidget({
    required this.errMsg,
    required this.locale,
    required this.onRetry,
    required this.theme,
    required this.isRtl,
  });

  @override
  Widget build(BuildContext context) {
    return Directionality(
      textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: (errMsg.color ?? SahoolTheme.error).withOpacity(0.1),
          borderRadius: BorderRadius.circular(12),
          border: Border.all(
            color: (errMsg.color ?? SahoolTheme.error).withOpacity(0.3),
          ),
        ),
        child: Row(
          children: [
            Icon(
              errMsg.icon,
              size: 24,
              color: errMsg.color ?? SahoolTheme.error,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                errMsg.getTitle(locale),
                style: theme.textTheme.bodyMedium?.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
            ),
            if (onRetry != null)
              IconButton(
                icon: const Icon(Icons.refresh, size: 20),
                onPressed: onRetry,
                color: errMsg.color ?? SahoolTheme.error,
                visualDensity: VisualDensity.compact,
              ),
          ],
        ),
      ),
    );
  }
}

/// Animated error icon
class _ErrorIcon extends StatefulWidget {
  final IconData icon;
  final Color color;

  const _ErrorIcon({
    required this.icon,
    required this.color,
  });

  @override
  State<_ErrorIcon> createState() => _ErrorIconState();
}

class _ErrorIconState extends State<_ErrorIcon>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;
  late Animation<double> _opacityAnimation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(milliseconds: 600),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.elasticOut),
    );

    _opacityAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeIn),
    );

    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: _controller,
      builder: (context, child) {
        return Opacity(
          opacity: _opacityAnimation.value,
          child: Transform.scale(
            scale: _scaleAnimation.value,
            child: Container(
              width: 100,
              height: 100,
              decoration: BoxDecoration(
                color: widget.color.withOpacity(0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                widget.icon,
                size: 56,
                color: widget.color,
              ),
            ),
          ),
        );
      },
    );
  }
}

/// Action buttons for error fallback
class _ActionButtons extends StatelessWidget {
  final Locale locale;
  final VoidCallback? onRetry;
  final VoidCallback? onGoBack;
  final ErrorMessage errorMessage;

  const _ActionButtons({
    required this.locale,
    required this.onRetry,
    required this.onGoBack,
    required this.errorMessage,
  });

  @override
  Widget build(BuildContext context) {
    final hasRetry = onRetry != null;
    final hasGoBack = onGoBack != null;

    if (!hasRetry && !hasGoBack) {
      return const SizedBox.shrink();
    }

    return Column(
      children: [
        // Primary action (Retry)
        if (hasRetry)
          SizedBox(
            width: double.infinity,
            child: ElevatedButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh),
              label: Text(
                errorMessage.getAction(locale) ??
                    (locale.languageCode == 'ar'
                        ? ErrorMessages.retryAr
                        : ErrorMessages.retryEn),
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: SahoolTheme.primary,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),

        // Secondary action (Go Back)
        if (hasGoBack) ...[
          const SizedBox(height: 12),
          SizedBox(
            width: double.infinity,
            child: OutlinedButton.icon(
              onPressed: onGoBack,
              icon: Icon(
                locale.languageCode == 'ar'
                    ? Icons.arrow_forward
                    : Icons.arrow_back,
              ),
              label: Text(
                locale.languageCode == 'ar'
                    ? ErrorMessages.goBackAr
                    : ErrorMessages.goBackEn,
              ),
              style: OutlinedButton.styleFrom(
                padding: const EdgeInsets.symmetric(
                  horizontal: 32,
                  vertical: 16,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ),
        ],
      ],
    );
  }
}

/// Debug information section
class _DebugInfoSection extends StatefulWidget {
  final Object error;
  final StackTrace? stackTrace;
  final Locale locale;

  const _DebugInfoSection({
    required this.error,
    required this.stackTrace,
    required this.locale,
  });

  @override
  State<_DebugInfoSection> createState() => _DebugInfoSectionState();
}

class _DebugInfoSectionState extends State<_DebugInfoSection> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      children: [
        // Toggle button
        TextButton.icon(
          onPressed: () => setState(() => _expanded = !_expanded),
          icon: Icon(
            _expanded ? Icons.expand_less : Icons.expand_more,
            size: 18,
          ),
          label: Text(
            widget.locale.languageCode == 'ar'
                ? 'تفاصيل الخطأ'
                : 'Error Details',
            style: TextStyle(color: Colors.grey[600], fontSize: 13),
          ),
        ),

        // Expandable debug info
        if (_expanded)
          Container(
            width: double.infinity,
            margin: const EdgeInsets.only(top: 8),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.grey[100],
              borderRadius: BorderRadius.circular(8),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Error type
                _DebugRow(
                  label: 'Type',
                  value: widget.error.runtimeType.toString(),
                ),
                const SizedBox(height: 8),

                // Error message
                _DebugRow(
                  label: 'Error',
                  value: widget.error.toString(),
                  maxLines: 3,
                ),

                // Stack trace
                if (widget.stackTrace != null) ...[
                  const SizedBox(height: 8),
                  Text(
                    'Stack Trace:',
                    style: theme.textTheme.labelSmall?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Container(
                    height: 120,
                    width: double.infinity,
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: SingleChildScrollView(
                      child: Text(
                        widget.stackTrace.toString(),
                        style: const TextStyle(
                          fontFamily: 'monospace',
                          fontSize: 10,
                        ),
                      ),
                    ),
                  ),
                ],

                // Copy button
                const SizedBox(height: 12),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () => _copyErrorDetails(context),
                    icon: const Icon(Icons.copy, size: 16),
                    label: Text(
                      widget.locale.languageCode == 'ar'
                          ? 'نسخ التفاصيل'
                          : 'Copy Details',
                    ),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 8),
                    ),
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  void _copyErrorDetails(BuildContext context) {
    final text = '''
Error: ${widget.error}

Stack Trace:
${widget.stackTrace ?? 'No stack trace available'}
''';

    Clipboard.setData(ClipboardData(text: text));

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          widget.locale.languageCode == 'ar'
              ? 'تم نسخ تفاصيل الخطأ'
              : 'Error details copied',
        ),
        duration: const Duration(seconds: 2),
      ),
    );
  }
}

/// Debug row widget
class _DebugRow extends StatelessWidget {
  final String label;
  final String value;
  final int maxLines;

  const _DebugRow({
    required this.label,
    required this.value,
    this.maxLines = 1,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 50,
          child: Text(
            '$label:',
            style: theme.textTheme.labelSmall?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            value,
            style: theme.textTheme.bodySmall?.copyWith(
              fontFamily: 'monospace',
              fontSize: 11,
            ),
            maxLines: maxLines,
            overflow: TextOverflow.ellipsis,
          ),
        ),
      ],
    );
  }
}

/// Error snackbar helper
class ErrorSnackBar {
  ErrorSnackBar._();

  /// Show error snackbar
  static void show(
    BuildContext context, {
    required Object error,
    ErrorMessage? errorMessage,
    VoidCallback? onRetry,
    Duration duration = const Duration(seconds: 4),
  }) {
    final locale = Localizations.localeOf(context);
    final errMsg = errorMessage ?? ErrorMessages.fromException(error);

    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              errMsg.icon,
              color: Colors.white,
              size: 20,
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                errMsg.getTitle(locale),
                style: const TextStyle(color: Colors.white),
              ),
            ),
          ],
        ),
        backgroundColor: errMsg.color ?? SahoolTheme.error,
        duration: duration,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
        ),
        action: onRetry != null
            ? SnackBarAction(
                label: locale.languageCode == 'ar'
                    ? ErrorMessages.retryAr
                    : ErrorMessages.retryEn,
                textColor: Colors.white,
                onPressed: onRetry,
              )
            : null,
      ),
    );
  }
}

/// Error dialog helper
class ErrorDialog {
  ErrorDialog._();

  /// Show error dialog
  static Future<void> show(
    BuildContext context, {
    required Object error,
    StackTrace? stackTrace,
    ErrorMessage? errorMessage,
    VoidCallback? onRetry,
    VoidCallback? onDismiss,
    bool showDebugInfo = false,
  }) async {
    final locale = Localizations.localeOf(context);
    final isRtl = locale.languageCode == 'ar';
    final errMsg = errorMessage ?? ErrorMessages.fromException(error);

    return showDialog(
      context: context,
      barrierDismissible: true,
      builder: (context) => Directionality(
        textDirection: isRtl ? TextDirection.rtl : TextDirection.ltr,
        child: AlertDialog(
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(20),
          ),
          icon: Container(
            width: 64,
            height: 64,
            decoration: BoxDecoration(
              color: (errMsg.color ?? SahoolTheme.error).withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              errMsg.icon,
              size: 32,
              color: errMsg.color ?? SahoolTheme.error,
            ),
          ),
          title: Text(
            errMsg.getTitle(locale),
            textAlign: TextAlign.center,
          ),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                errMsg.getMessage(locale),
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey[600]),
              ),
              if (showDebugInfo && kDebugMode) ...[
                const SizedBox(height: 16),
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    error.toString(),
                    style: const TextStyle(
                      fontFamily: 'monospace',
                      fontSize: 10,
                    ),
                    maxLines: 3,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
              ],
            ],
          ),
          actions: [
            if (onRetry != null)
              TextButton(
                onPressed: () {
                  Navigator.of(context).pop();
                  onRetry();
                },
                child: Text(
                  errMsg.getAction(locale) ??
                      (isRtl ? ErrorMessages.retryAr : ErrorMessages.retryEn),
                ),
              ),
            TextButton(
              onPressed: () {
                Navigator.of(context).pop();
                onDismiss?.call();
              },
              child: Text(
                isRtl ? ErrorMessages.dismissAr : ErrorMessages.dismissEn,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
