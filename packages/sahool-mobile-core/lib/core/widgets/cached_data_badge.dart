/// SAHOOL Cached Data Badge
/// شارة البيانات المخزنة مؤقتاً - تشير إلى أن البيانات المعروضة من التخزين المحلي
///
/// Features:
/// - Cloud-off icon with "Cached data" label
/// - Bilingual Arabic/English support
/// - Subtle chip style
library;

import 'package:flutter/material.dart';

/// شارة البيانات المخزنة مؤقتاً
/// Small badge indicating data is served from local cache
class CachedDataBadge extends StatelessWidget {
  /// Whether to use Arabic labels (default: true)
  final bool useArabic;

  /// Background color override
  final Color? backgroundColor;

  /// Text/icon color override
  final Color? foregroundColor;

  const CachedDataBadge({
    super.key,
    this.useArabic = true,
    this.backgroundColor,
    this.foregroundColor,
  });

  @override
  Widget build(BuildContext context) {
    final bg = backgroundColor ?? Colors.grey.shade200;
    final fg = foregroundColor ?? Colors.grey.shade600;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.cloud_off_rounded,
            size: 12,
            color: fg,
          ),
          const SizedBox(width: 4),
          Text(
            useArabic ? 'بيانات مخزنة مؤقتا' : 'Cached data',
            style: TextStyle(
              fontSize: 11,
              color: fg,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
