import 'package:flutter/material.dart';
import '../theme/sahool_theme.dart';

/// SahoolErrorState - حالة الخطأ الموحدة
/// Unified error state widget with retry support
///
/// Provides a consistent error display across all screens with:
/// - Bilingual messages (Arabic default, English fallback)
/// - Retry button styled with SahoolColors
/// - Configurable icon (cloud_off for network, error_outline for general)
/// - Compact mode for inline use within lists/cards
/// - Full-screen mode with centered layout
///
/// Usage:
/// ```dart
/// // Full-screen error
/// SahoolErrorState(
///   message: 'تعذر تحميل البيانات',
///   messageEn: 'Failed to load data',
///   onRetry: () => ref.invalidate(myProvider),
/// )
///
/// // Compact inline error
/// SahoolErrorState.compact(
///   message: 'خطأ في التحميل',
///   onRetry: () => ref.invalidate(myProvider),
/// )
///
/// // Network error
/// SahoolErrorState.network(
///   onRetry: () => ref.invalidate(myProvider),
/// )
/// ```
class SahoolErrorState extends StatelessWidget {
  /// Arabic error message (primary)
  final String? message;

  /// English error message (fallback)
  final String? messageEn;

  /// Callback when retry button is pressed
  final VoidCallback? onRetry;

  /// Icon to display above the message
  final IconData icon;

  /// Whether to use compact inline layout
  final bool compact;

  /// Optional icon color override
  final Color? iconColor;

  const SahoolErrorState({
    super.key,
    this.message,
    this.messageEn,
    this.onRetry,
    this.icon = Icons.error_outline_rounded,
    this.compact = false,
    this.iconColor,
  });

  /// Network-specific error state with cloud_off icon
  /// حالة خطأ الشبكة مع أيقونة عدم الاتصال
  const SahoolErrorState.network({
    super.key,
    this.onRetry,
    this.compact = false,
  })  : message = 'تعذر الاتصال بالخادم. تحقق من اتصالك بالإنترنت.',
        messageEn = 'Could not connect to the server. Check your internet connection.',
        icon = Icons.cloud_off_rounded,
        iconColor = null;

  /// Compact inline error for use within lists or cards
  /// حالة خطأ مضغوطة للاستخدام داخل القوائم أو البطاقات
  const SahoolErrorState.compact({
    super.key,
    this.message,
    this.messageEn,
    this.onRetry,
    this.icon = Icons.error_outline_rounded,
    this.iconColor,
  }) : compact = true;

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return _buildCompact(context);
    }
    return _buildFullScreen(context);
  }

  Widget _buildCompact(BuildContext context) {
    final effectiveColor = iconColor ?? SahoolColors.danger;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: effectiveColor.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: effectiveColor.withValues(alpha: 0.2),
        ),
      ),
      child: Row(
        children: [
          Icon(icon, color: effectiveColor, size: 24),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  message ?? 'حدث خطأ',
                  style: TextStyle(
                    color: effectiveColor,
                    fontSize: 14,
                    fontWeight: FontWeight.w500,
                  ),
                ),
                if (messageEn != null) ...[
                  const SizedBox(height: 2),
                  Text(
                    messageEn!,
                    style: TextStyle(
                      color: effectiveColor.withValues(alpha: 0.7),
                      fontSize: 12,
                    ),
                  ),
                ],
              ],
            ),
          ),
          if (onRetry != null)
            IconButton(
              onPressed: onRetry,
              icon: Icon(Icons.refresh_rounded, color: effectiveColor),
              tooltip: 'إعادة المحاولة',
            ),
        ],
      ),
    );
  }

  Widget _buildFullScreen(BuildContext context) {
    final effectiveColor = iconColor ?? SahoolColors.danger;
    final locale = Localizations.localeOf(context);
    final isArabic = locale.languageCode == 'ar';

    return Center(
      child: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Icon
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: effectiveColor.withValues(alpha: 0.1),
                shape: BoxShape.circle,
              ),
              child: Icon(
                icon,
                size: 56,
                color: effectiveColor,
              ),
            ),

            const SizedBox(height: 24),

            // Arabic message (primary)
            Text(
              message ?? 'حدث خطأ غير متوقع',
              style: Theme.of(context).textTheme.titleLarge?.copyWith(
                    fontWeight: FontWeight.bold,
                    color: SahoolColors.textDark,
                  ),
              textAlign: TextAlign.center,
            ),

            // English message (secondary)
            if (messageEn != null) ...[
              const SizedBox(height: 4),
              Text(
                messageEn!,
                style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: Colors.grey[600],
                    ),
                textAlign: TextAlign.center,
              ),
            ],

            const SizedBox(height: 12),

            // Subtitle hint
            Text(
              isArabic
                  ? 'يرجى المحاولة مرة أخرى لاحقاً'
                  : 'Please try again later',
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: SahoolColors.textSecondary,
                  ),
              textAlign: TextAlign.center,
            ),

            const SizedBox(height: 32),

            // Retry Button
            if (onRetry != null)
              ElevatedButton.icon(
                onPressed: onRetry,
                icon: const Icon(Icons.refresh_rounded),
                label: Text(isArabic ? 'إعادة المحاولة' : 'Retry'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: SahoolColors.primary,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 32,
                    vertical: 14,
                  ),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }
}
