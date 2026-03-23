/// Low Stock Alert Widget - تنبيه المخزون المنخفض
library;

import 'package:flutter/material.dart';

/// بانر تنبيه المخزون المنخفض
class LowStockAlert extends StatelessWidget {
  final int count;
  final VoidCallback? onTap;

  const LowStockAlert({
    super.key,
    required this.count,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (count <= 0) return const SizedBox.shrink();

    return InkWell(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [
              Colors.red.shade600,
              Colors.red.shade700,
            ],
          ),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.red.withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, 4),
            ),
          ],
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.white.withOpacity(0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.warning_amber_rounded,
                color: Colors.white,
                size: 32,
              ),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'تنبيه مخزون منخفض',
                    style: TextStyle(
                      color: Colors.white,
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '$count ${count == 1 ? 'عنصر يحتاج' : 'عناصر تحتاج'} إلى إعادة طلب',
                    style: TextStyle(
                      color: Colors.white.withOpacity(0.9),
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),
            const Icon(
              Icons.arrow_forward_ios,
              color: Colors.white,
              size: 18,
            ),
          ],
        ),
      ),
    );
  }
}

/// بطاقة تنبيه صغيرة
class CompactLowStockAlert extends StatelessWidget {
  final int count;
  final VoidCallback? onTap;

  const CompactLowStockAlert({
    super.key,
    required this.count,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (count <= 0) return const SizedBox.shrink();

    return InkWell(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.red.shade50,
          border: Border.all(color: Colors.red.shade200),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.warning_amber_rounded,
              color: Colors.red.shade700,
              size: 20,
            ),
            const SizedBox(width: 8),
            Text(
              '$count عنصر بمخزون منخفض',
              style: TextStyle(
                color: Colors.red.shade900,
                fontWeight: FontWeight.w600,
                fontSize: 14,
              ),
            ),
            const SizedBox(width: 4),
            Icon(
              Icons.arrow_forward_ios,
              color: Colors.red.shade700,
              size: 14,
            ),
          ],
        ),
      ),
    );
  }
}
