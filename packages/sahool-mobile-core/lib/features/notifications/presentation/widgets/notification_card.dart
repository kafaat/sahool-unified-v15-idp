/// SAHOOL Notification Card Widget
/// عنصر بطاقة الإشعار
///
/// Displays a single notification in list format with:
/// - Category icon and color
/// - Title and summary
/// - Time and status
/// - Swipe actions
library;

import 'package:flutter/material.dart';

import '../../domain/models/notification.dart';
import '../../domain/models/notification_category.dart';

class NotificationCard extends StatelessWidget {
  final AppNotification notification;
  final bool isSelected;
  final bool showCheckbox;
  final VoidCallback? onTap;
  final VoidCallback? onLongPress;
  final VoidCallback? onDismiss;
  final VoidCallback? onMarkRead;

  const NotificationCard({
    super.key,
    required this.notification,
    this.isSelected = false,
    this.showCheckbox = false,
    this.onTap,
    this.onLongPress,
    this.onDismiss,
    this.onMarkRead,
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';
    final category = notification.category;

    return Semantics(
      label: '${notification.getTitle(isArabic)}'
          '${notification.isHighPriority ? ", ${isArabic ? notification.priority.labelAr : "Priority: ${notification.priority.labelAr}"}" : ""}'
          '${notification.isUnread ? (isArabic ? "، غير مقروء" : ", Unread") : ""}',
      button: onTap != null,
      child: Dismissible(
      key: Key(notification.id),
      direction: DismissDirection.horizontal,
      confirmDismiss: (direction) async {
        if (direction == DismissDirection.endToStart) {
          // Delete
          onDismiss?.call();
          return true;
        } else {
          // Mark read/unread
          onMarkRead?.call();
          return false;
        }
      },
      background: Container(
        color: Colors.green,
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.start,
          children: [
            const SizedBox(width: 20),
            Icon(
              notification.isRead ? Icons.mark_email_unread : Icons.mark_email_read,
              color: Colors.white,
            ),
            const SizedBox(width: 8),
            Text(
              notification.isRead ? 'غير مقروء' : 'مقروء',
              style: const TextStyle(color: Colors.white),
            ),
          ],
        ),
      ),
      secondaryBackground: Container(
        color: Colors.red,
        alignment: Alignment.centerLeft,
        padding: const EdgeInsets.only(left: 20),
        child: const Row(
          mainAxisAlignment: MainAxisAlignment.end,
          children: [
            Text(
              'حذف',
              style: TextStyle(color: Colors.white),
            ),
            SizedBox(width: 8),
            Icon(Icons.delete, color: Colors.white),
            SizedBox(width: 20),
          ],
        ),
      ),
      child: Material(
        color: _getBackgroundColor(context),
        child: InkWell(
          onTap: onTap,
          onLongPress: onLongPress,
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              border: Border(
                bottom: BorderSide(
                  color: Colors.grey.shade200,
                  width: 1,
                ),
              ),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Checkbox for selection mode
                if (showCheckbox)
                  Padding(
                    padding: const EdgeInsets.only(left: 8),
                    child: Checkbox(
                      value: isSelected,
                      onChanged: (_) => onTap?.call(),
                    ),
                  ),

                // Category icon
                _buildCategoryIcon(category),

                const SizedBox(width: 12),

                // Content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Title row with priority badge
                      Row(
                        children: [
                          // Priority badge
                          if (notification.isHighPriority)
                            Container(
                              margin: const EdgeInsets.only(left: 6),
                              padding: const EdgeInsets.symmetric(
                                horizontal: 6,
                                vertical: 2,
                              ),
                              decoration: BoxDecoration(
                                color: notification.priority.color,
                                borderRadius: BorderRadius.circular(4),
                              ),
                              child: Text(
                                notification.priority.labelAr,
                                style: const TextStyle(
                                  color: Colors.white,
                                  fontSize: 10,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),

                          // Title
                          Expanded(
                            child: Text(
                              notification.getTitle(isArabic),
                              style: TextStyle(
                                fontWeight: notification.isUnread
                                    ? FontWeight.bold
                                    : FontWeight.normal,
                                fontSize: 15,
                              ),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 4),

                      // Body/Summary
                      Text(
                        notification.getSummary(isArabic) ??
                            notification.getBody(isArabic),
                        style: TextStyle(
                          color: Colors.grey.shade600,
                          fontSize: 13,
                        ),
                        maxLines: 2,
                        overflow: TextOverflow.ellipsis,
                      ),

                      const SizedBox(height: 6),

                      // Bottom row: Time and category
                      Row(
                        children: [
                          // Time
                          Text(
                            isArabic
                                ? notification.ageStringAr
                                : notification.ageString,
                            style: TextStyle(
                              color: Colors.grey.shade500,
                              fontSize: 12,
                            ),
                          ),

                          const SizedBox(width: 8),

                          // Category badge
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: category.lightColor,
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Text(
                              category.labelAr,
                              style: TextStyle(
                                color: category.color,
                                fontSize: 11,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                          ),

                          // Snoozed indicator
                          if (notification.isSnoozed) ...[
                            const SizedBox(width: 8),
                            Icon(
                              Icons.snooze,
                              size: 14,
                              color: Colors.orange.shade600,
                            ),
                          ],
                        ],
                      ),
                    ],
                  ),
                ),

                // Unread indicator
                if (notification.isUnread)
                  Container(
                    margin: const EdgeInsets.only(right: 4),
                    width: 10,
                    height: 10,
                    decoration: BoxDecoration(
                      color: category.color,
                      shape: BoxShape.circle,
                    ),
                  ),
              ],
            ),
          ),
        ),
      ),
    ),
    );
  }

  Widget _buildCategoryIcon(NotificationCategory category) {
    return ExcludeSemantics(child: Container(
      width: 44,
      height: 44,
      decoration: BoxDecoration(
        color: category.lightColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Center(
        child: Icon(
          category.icon,
          color: category.color,
          size: 22,
        ),
      ),
    ));
  }

  Color _getBackgroundColor(BuildContext context) {
    if (isSelected) {
      return Theme.of(context).primaryColor.withOpacity(0.1);
    }
    if (notification.isUnread) {
      return Colors.white;
    }
    return Colors.grey.shade50;
  }
}
