/// SAHOOL Last Updated Indicator
/// مؤشر آخر تحديث - يعرض الوقت النسبي لآخر تحديث للبيانات
///
/// Features:
/// - Relative time display (just now, X min ago, X hours ago, yesterday)
/// - Bilingual Arabic/English support
/// - Optional refresh button
/// - Subtle grey text style (12px)
library;

import 'package:flutter/material.dart';

/// مؤشر آخر تحديث
/// Shows when data was last refreshed from server
class LastUpdatedIndicator extends StatelessWidget {
  /// The timestamp of the last data update
  final DateTime? lastUpdated;

  /// Whether to use Arabic labels (default: true)
  final bool useArabic;

  /// Optional callback when refresh is tapped
  final VoidCallback? onRefresh;

  /// Text color override
  final Color? color;

  const LastUpdatedIndicator({
    super.key,
    required this.lastUpdated,
    this.useArabic = true,
    this.onRefresh,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final textColor = color ?? Colors.grey.shade500;

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(
          Icons.access_time_rounded,
          size: 12,
          color: textColor,
        ),
        const SizedBox(width: 4),
        Text(
          _formatLastUpdated(),
          style: TextStyle(
            fontSize: 12,
            color: textColor,
          ),
        ),
        if (onRefresh != null) ...[
          const SizedBox(width: 4),
          GestureDetector(
            onTap: onRefresh,
            child: Icon(
              Icons.refresh_rounded,
              size: 14,
              color: textColor,
            ),
          ),
        ],
      ],
    );
  }

  String _formatLastUpdated() {
    if (lastUpdated == null) {
      return useArabic ? 'لم يتم التحديث بعد' : 'Not updated yet';
    }

    final now = DateTime.now();
    final diff = now.difference(lastUpdated!);

    final relative = _formatRelativeTime(diff);
    final prefix = useArabic ? 'آخر تحديث: ' : 'Last updated: ';
    return '$prefix$relative';
  }

  String _formatRelativeTime(Duration diff) {
    if (diff.inSeconds < 60) {
      return useArabic ? 'الآن' : 'just now';
    }
    if (diff.inMinutes < 60) {
      final m = diff.inMinutes;
      return useArabic ? 'منذ $m دقيقة' : '$m min ago';
    }
    if (diff.inHours < 24) {
      final h = diff.inHours;
      return useArabic ? 'منذ $h ساعة' : '$h hours ago';
    }
    if (diff.inDays == 1) {
      return useArabic ? 'أمس' : 'yesterday';
    }
    final d = diff.inDays;
    return useArabic ? 'منذ $d يوم' : '$d days ago';
  }
}
