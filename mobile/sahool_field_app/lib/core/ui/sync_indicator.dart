import 'package:flutter/material.dart';

/// Sync Indicator Widget
/// مؤشر حالة المزامنة للـ Home Cockpit
///
/// يعرض حالة الاتصال والمزامنة بشكل بصري واضح
class SyncIndicator extends StatelessWidget {
  final bool isOnline;
  final int pendingCount;
  final bool isSyncing;
  final VoidCallback? onTap;

  const SyncIndicator({
    super.key,
    required this.isOnline,
    this.pendingCount = 0,
    this.isSyncing = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: _backgroundColor,
          borderRadius: BorderRadius.circular(20),
          boxShadow: [
            BoxShadow(
              color: _iconColor.withOpacity(0.3),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            // Sync icon with animation
            if (isSyncing)
              SizedBox(
                width: 16,
                height: 16,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  valueColor: AlwaysStoppedAnimation(_iconColor),
                ),
              )
            else
              Icon(
                _icon,
                size: 16,
                color: _iconColor,
              ),
            const SizedBox(width: 6),
            // Status text
            Text(
              _statusText,
              style: TextStyle(
                color: _iconColor,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),
            // Pending badge
            if (pendingCount > 0 && !isSyncing) ...[
              const SizedBox(width: 6),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: Colors.orange,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Text(
                  '$pendingCount',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Color get _backgroundColor {
    if (isSyncing) return Colors.blue.withOpacity(0.15);
    if (!isOnline) return Colors.red.withOpacity(0.15);
    if (pendingCount > 0) return Colors.orange.withOpacity(0.15);
    return Colors.green.withOpacity(0.15);
  }

  Color get _iconColor {
    if (isSyncing) return Colors.blue;
    if (!isOnline) return Colors.red;
    if (pendingCount > 0) return Colors.orange;
    return Colors.green;
  }

  IconData get _icon {
    if (!isOnline) return Icons.cloud_off;
    if (pendingCount > 0) return Icons.cloud_upload;
    return Icons.cloud_done;
  }

  String get _statusText {
    if (isSyncing) return 'مزامنة...';
    if (!isOnline) return 'غير متصل';
    if (pendingCount > 0) return 'معلق';
    return 'متصل';
  }
}

/// Compact version for AppBar
class SyncIndicatorCompact extends StatelessWidget {
  final bool isOnline;
  final int pendingCount;
  final bool isSyncing;

  const SyncIndicatorCompact({
    super.key,
    required this.isOnline,
    this.pendingCount = 0,
    this.isSyncing = false,
  });

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        if (isSyncing)
          const SizedBox(
            width: 24,
            height: 24,
            child: CircularProgressIndicator(
              strokeWidth: 2,
              valueColor: AlwaysStoppedAnimation(Colors.white),
            ),
          )
        else
          Icon(
            isOnline ? Icons.cloud_done : Icons.cloud_off,
            color: isOnline ? Colors.green : Colors.red,
            size: 24,
          ),
        if (pendingCount > 0 && !isSyncing)
          Positioned(
            right: 0,
            top: 0,
            child: Container(
              width: 12,
              height: 12,
              decoration: const BoxDecoration(
                color: Colors.orange,
                shape: BoxShape.circle,
              ),
              child: Center(
                child: Text(
                  pendingCount > 9 ? '9+' : '$pendingCount',
                  style: const TextStyle(
                    color: Colors.white,
                    fontSize: 8,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ),
      ],
    );
  }
}
