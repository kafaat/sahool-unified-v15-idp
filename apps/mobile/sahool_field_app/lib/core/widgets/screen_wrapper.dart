import 'package:flutter/material.dart';
import 'error_boundary.dart';
import 'loading_states.dart';

/// SAHOOL Screen Wrapper
/// غلاف الشاشة الموحد مع معالجة الأخطاء والتحميل
///
/// Wraps feature screens with consistent:
/// - Error boundary with retry capability
/// - Scaffold with RTL support
/// - Optional loading overlay for async operations
///
/// Usage:
/// ```dart
/// SahoolScreenWrapper(
///   title: 'الحقول',
///   isLoading: state.isSaving,
///   loadingMessage: 'جاري الحفظ...',
///   actions: [...],
///   body: MyContent(),
///   floatingActionButton: FloatingActionButton(...),
/// )
/// ```
class SahoolScreenWrapper extends StatelessWidget {
  /// Screen title (shown in AppBar)
  final String title;

  /// Main body content
  final Widget body;

  /// Whether an async operation is in progress (shows overlay)
  final bool isLoading;

  /// Loading message to show in overlay
  final String? loadingMessage;

  /// AppBar actions
  final List<Widget>? actions;

  /// Floating action button
  final Widget? floatingActionButton;

  /// Bottom navigation bar
  final Widget? bottomNavigationBar;

  /// Whether to wrap body with error boundary
  final bool enableErrorBoundary;

  /// Whether to use RTL direction
  final bool isRTL;

  /// AppBar background color
  final Color? appBarColor;

  /// Error callback for error boundary
  final void Function(Object error, StackTrace? stackTrace)? onError;

  /// Custom error builder
  final Widget Function(Object error, VoidCallback retry)? errorBuilder;

  /// Custom AppBar (overrides title and actions)
  final PreferredSizeWidget? appBar;

  const SahoolScreenWrapper({
    super.key,
    required this.title,
    required this.body,
    this.isLoading = false,
    this.loadingMessage,
    this.actions,
    this.floatingActionButton,
    this.bottomNavigationBar,
    this.enableErrorBoundary = true,
    this.isRTL = true,
    this.appBarColor,
    this.onError,
    this.errorBuilder,
    this.appBar,
  });

  @override
  Widget build(BuildContext context) {
    Widget content = body;

    // Wrap with error boundary if enabled
    if (enableErrorBoundary) {
      content = SahoolErrorBoundary(
        onError: onError ??
            (error, stackTrace) {
              debugPrint('SahoolScreenWrapper error: $error');
            },
        errorBuilder: errorBuilder,
        child: content,
      );
    }

    // Wrap with loading overlay if needed
    content = SahoolLoadingOverlay(
      isLoading: isLoading,
      message: loadingMessage,
      child: content,
    );

    Widget scaffold = Scaffold(
      appBar: appBar ??
          AppBar(
            title: Text(title),
            backgroundColor: appBarColor ?? const Color(0xFF367C2B),
            foregroundColor: Colors.white,
            actions: actions,
          ),
      body: content,
      floatingActionButton: floatingActionButton,
      bottomNavigationBar: bottomNavigationBar,
    );

    // Apply RTL direction
    if (isRTL) {
      scaffold = Directionality(
        textDirection: TextDirection.rtl,
        child: scaffold,
      );
    }

    return scaffold;
  }
}
