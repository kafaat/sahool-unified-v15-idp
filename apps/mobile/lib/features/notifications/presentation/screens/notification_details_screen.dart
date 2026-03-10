/// SAHOOL Notification Details Screen
/// شاشة تفاصيل الإشعار
///
/// Full details view for a notification including:
/// - Complete message content
/// - Actions
/// - Related entity navigation

import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:intl/intl.dart';

import '../../domain/models/notification.dart';
import '../../domain/models/notification_action.dart';
import '../../state/notifications_providers.dart';
import '../widgets/actionable_notification.dart';

class NotificationDetailsScreen extends ConsumerStatefulWidget {
  final AppNotification notification;

  const NotificationDetailsScreen({
    super.key,
    required this.notification,
  });

  @override
  ConsumerState<NotificationDetailsScreen> createState() =>
      _NotificationDetailsScreenState();
}

class _NotificationDetailsScreenState
    extends ConsumerState<NotificationDetailsScreen> {
  late AppNotification _notification;
  bool _isExecutingAction = false;

  @override
  void initState() {
    super.initState();
    _notification = widget.notification;
  }

  @override
  Widget build(BuildContext context) {
    final category = _notification.category;
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Scaffold(
      appBar: AppBar(
        title: Text(category.labelAr),
        backgroundColor: category.color.withOpacity(0.1),
        foregroundColor: category.color,
        actions: [
          // Mark read/unread toggle
          IconButton(
            icon: Icon(
              _notification.isRead
                  ? Icons.mark_email_unread
                  : Icons.mark_email_read,
            ),
            tooltip: _notification.isRead ? 'تعليم كغير مقروء' : 'تعليم كمقروء',
            onPressed: _toggleReadStatus,
          ),

          // More options
          PopupMenuButton<String>(
            onSelected: _handleMenuAction,
            itemBuilder: (context) => [
              if (_notification.category.canSnooze)
                const PopupMenuItem(
                  value: 'snooze',
                  child: ListTile(
                    leading: Icon(Icons.snooze),
                    title: Text('تأجيل'),
                    contentPadding: EdgeInsets.zero,
                  ),
                ),
              const PopupMenuItem(
                value: 'archive',
                child: ListTile(
                  leading: Icon(Icons.archive),
                  title: Text('أرشفة'),
                  contentPadding: EdgeInsets.zero,
                ),
              ),
              const PopupMenuItem(
                value: 'delete',
                child: ListTile(
                  leading: Icon(Icons.delete, color: Colors.red),
                  title: Text('حذف', style: TextStyle(color: Colors.red)),
                  contentPadding: EdgeInsets.zero,
                ),
              ),
            ],
          ),
        ],
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header with icon and category
            _buildHeader(context),

            // Title
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
              child: Text(
                _notification.getTitle(isArabic),
                style: const TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

            // Timestamp and status
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: _buildMetaInfo(),
            ),

            const Divider(height: 32),

            // Body
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Text(
                _notification.getBody(isArabic),
                style: const TextStyle(
                  fontSize: 16,
                  height: 1.6,
                ),
              ),
            ),

            // Image if available
            if (_notification.imageUrl != null) ...[
              const SizedBox(height: 16),
              _buildImage(),
            ],

            // Related entity
            if (_notification.hasRelatedEntity) ...[
              const SizedBox(height: 24),
              _buildRelatedEntity(context),
            ],

            // Actions
            if (_notification.hasActions) ...[
              const SizedBox(height: 24),
              _buildActions(context),
            ],

            // Additional data
            if (_notification.data != null &&
                _notification.data!.isNotEmpty) ...[
              const SizedBox(height: 24),
              _buildAdditionalData(),
            ],

            const SizedBox(height: 32),
          ],
        ),
      ),

      // Primary action button
      bottomNavigationBar: _notification.primaryAction != null
          ? _buildPrimaryActionBar(context)
          : null,
    );
  }

  Widget _buildHeader(BuildContext context) {
    final category = _notification.category;

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: category.lightColor,
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(24),
          bottomRight: Radius.circular(24),
        ),
      ),
      child: Column(
        children: [
          // Priority badge
          if (_notification.isHighPriority)
            Container(
              margin: const EdgeInsets.only(bottom: 12),
              padding: const EdgeInsets.symmetric(
                horizontal: 12,
                vertical: 4,
              ),
              decoration: BoxDecoration(
                color: _notification.priority.color,
                borderRadius: BorderRadius.circular(12),
              ),
              child: Text(
                _notification.priority.labelAr,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),

          // Category icon
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              shape: BoxShape.circle,
              boxShadow: [
                BoxShadow(
                  color: category.color.withOpacity(0.3),
                  blurRadius: 8,
                  spreadRadius: 2,
                ),
              ],
            ),
            child: Icon(
              category.icon,
              size: 40,
              color: category.color,
            ),
          ),

          const SizedBox(height: 12),

          // Category name
          Text(
            category.labelAr,
            style: TextStyle(
              fontSize: 14,
              color: category.color,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMetaInfo() {
    final dateFormat = DateFormat('dd MMM yyyy, HH:mm', 'ar');

    return Wrap(
      spacing: 16,
      runSpacing: 8,
      children: [
        // Time
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.access_time, size: 16, color: Colors.grey.shade600),
            const SizedBox(width: 4),
            Text(
              dateFormat.format(_notification.createdAt),
              style: TextStyle(
                fontSize: 13,
                color: Colors.grey.shade600,
              ),
            ),
          ],
        ),

        // Status
        Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              _notification.isRead ? Icons.drafts : Icons.mail,
              size: 16,
              color: _notification.isRead ? Colors.grey : Colors.blue,
            ),
            const SizedBox(width: 4),
            Text(
              _notification.isRead ? 'مقروء' : 'غير مقروء',
              style: TextStyle(
                fontSize: 13,
                color: _notification.isRead ? Colors.grey.shade600 : Colors.blue,
              ),
            ),
          ],
        ),

        // Source
        if (_notification.source != 'local')
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                _notification.source == 'push'
                    ? Icons.notifications
                    : Icons.sync,
                size: 16,
                color: Colors.grey.shade600,
              ),
              const SizedBox(width: 4),
              Text(
                _notification.source == 'push' ? 'إشعار فوري' : 'مزامنة',
                style: TextStyle(
                  fontSize: 13,
                  color: Colors.grey.shade600,
                ),
              ),
            ],
          ),
      ],
    );
  }

  Widget _buildImage() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: CachedNetworkImage(
          imageUrl: _notification.imageUrl!,
          width: double.infinity,
          fit: BoxFit.cover,
          placeholder: (_, __) => const SizedBox(height: 150, child: Center(child: CircularProgressIndicator(strokeWidth: 2))),
          errorWidget: (context, _, __) => Container(
            height: 150,
            color: Colors.grey.shade200,
            child: const Center(
              child: Icon(Icons.broken_image, size: 40),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildRelatedEntity(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Card(
        child: ListTile(
          leading: Icon(
            _getEntityIcon(_notification.relatedEntityType!),
            color: Theme.of(context).primaryColor,
          ),
          title: Text(_getEntityLabel(_notification.relatedEntityType!)),
          subtitle: Text(_notification.relatedEntityId!),
          trailing: const Icon(Icons.chevron_left),
          onTap: () => _navigateToEntity(context),
        ),
      ),
    );
  }

  Widget _buildActions(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'الإجراءات المتاحة',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: Colors.grey.shade700,
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: _notification.actions.map((action) {
              return ActionableNotification(
                action: action,
                onExecute: () => _executeAction(action),
                isLoading: _isExecutingAction,
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildAdditionalData() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: ExpansionTile(
        title: const Text('بيانات إضافية'),
        tilePadding: EdgeInsets.zero,
        children: [
          ..._notification.data!.entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    '${entry.key}: ',
                    style: const TextStyle(fontWeight: FontWeight.w600),
                  ),
                  Expanded(
                    child: Text(
                      entry.value.toString(),
                      style: TextStyle(color: Colors.grey.shade700),
                    ),
                  ),
                ],
              ),
            );
          }),
        ],
      ),
    );
  }

  Widget _buildPrimaryActionBar(BuildContext context) {
    final action = _notification.primaryAction!;

    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: ElevatedButton.icon(
          onPressed: _isExecutingAction ? null : () => _executeAction(action),
          style: ElevatedButton.styleFrom(
            backgroundColor: action.color ?? Theme.of(context).primaryColor,
            foregroundColor: Colors.white,
            minimumSize: const Size(double.infinity, 50),
          ),
          icon: _isExecutingAction
              ? const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                    color: Colors.white,
                  ),
                )
              : Icon(action.icon),
          label: Text(
            action.labelAr,
            style: const TextStyle(fontSize: 16),
          ),
        ),
      ),
    );
  }

  // ─────────────────────────────────────────────────────────────────────────────
  // Actions
  // ─────────────────────────────────────────────────────────────────────────────

  void _toggleReadStatus() {
    if (_notification.isRead) {
      ref
          .read(notificationsControllerProvider.notifier)
          .markAsUnread(_notification.id);
      setState(() {
        _notification = _notification.markAsUnread();
      });
    } else {
      ref
          .read(notificationsControllerProvider.notifier)
          .markAsRead(_notification.id);
      setState(() {
        _notification = _notification.markAsRead();
      });
    }
  }

  void _handleMenuAction(String action) {
    switch (action) {
      case 'snooze':
        _showSnoozeDialog();
        break;
      case 'archive':
        _archiveNotification();
        break;
      case 'delete':
        _deleteNotification();
        break;
    }
  }

  void _showSnoozeDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('تأجيل الإشعار'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              title: const Text('30 دقيقة'),
              onTap: () {
                Navigator.pop(context);
                _snoozeNotification(const Duration(minutes: 30));
              },
            ),
            ListTile(
              title: const Text('ساعة واحدة'),
              onTap: () {
                Navigator.pop(context);
                _snoozeNotification(const Duration(hours: 1));
              },
            ),
            ListTile(
              title: const Text('3 ساعات'),
              onTap: () {
                Navigator.pop(context);
                _snoozeNotification(const Duration(hours: 3));
              },
            ),
            ListTile(
              title: const Text('غداً'),
              onTap: () {
                Navigator.pop(context);
                _snoozeNotification(const Duration(hours: 24));
              },
            ),
          ],
        ),
      ),
    );
  }

  void _snoozeNotification(Duration duration) {
    ref.read(notificationsControllerProvider.notifier).snoozeNotification(
          _notification.id,
          duration: duration,
        );

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تم تأجيل الإشعار')),
    );

    Navigator.pop(context);
  }

  void _archiveNotification() {
    ref
        .read(notificationsControllerProvider.notifier)
        .archiveNotification(_notification.id);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('تم أرشفة الإشعار')),
    );

    Navigator.pop(context);
  }

  void _deleteNotification() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('حذف الإشعار'),
        content: const Text('هل تريد حذف هذا الإشعار؟'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('إلغاء'),
          ),
          ElevatedButton(
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red),
            onPressed: () {
              Navigator.pop(context);
              ref
                  .read(notificationsControllerProvider.notifier)
                  .deleteNotification(_notification.id);

              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('تم حذف الإشعار')),
              );

              Navigator.pop(context);
            },
            child: const Text('حذف'),
          ),
        ],
      ),
    );
  }

  Future<void> _executeAction(NotificationAction action) async {
    if (action.requiresConfirmation) {
      final confirmed = await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: Text(action.labelAr),
          content: const Text('هل تريد تنفيذ هذا الإجراء؟'),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context, false),
              child: const Text('إلغاء'),
            ),
            ElevatedButton(
              onPressed: () => Navigator.pop(context, true),
              child: const Text('تأكيد'),
            ),
          ],
        ),
      );

      if (confirmed != true) return;
    }

    setState(() {
      _isExecutingAction = true;
    });

    try {
      await ref
          .read(notificationsControllerProvider.notifier)
          .executeAction(_notification.id, action);

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('تم تنفيذ: ${action.labelAr}')),
        );

        if (action.closeOnAction) {
          Navigator.pop(context);
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('فشل التنفيذ: $e')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isExecutingAction = false;
        });
      }
    }
  }

  void _navigateToEntity(BuildContext context) {
    // Navigate based on entity type
    final type = _notification.relatedEntityType;
    final id = _notification.relatedEntityId;

    if (type == null || id == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('لا يمكن الانتقال | Cannot navigate')),
      );
      return;
    }

    switch (type.toLowerCase()) {
      case 'field':
        Navigator.of(context).pushNamed('/fields/$id');
      case 'task':
        Navigator.of(context).pushNamed('/tasks/$id');
      case 'irrigation':
        Navigator.of(context).pushNamed('/irrigation/$id');
      case 'alert':
        Navigator.of(context).pushNamed('/alerts/$id');
      case 'equipment':
        Navigator.of(context).pushNamed('/equipment/$id');
      default:
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('نوع غير معروف | Unknown type')),
        );
    }
  }

  IconData _getEntityIcon(String entityType) {
    switch (entityType.toLowerCase()) {
      case 'field':
        return Icons.landscape;
      case 'task':
        return Icons.task_alt;
      case 'irrigation':
        return Icons.water_drop;
      case 'alert':
        return Icons.warning;
      case 'equipment':
        return Icons.agriculture;
      default:
        return Icons.info;
    }
  }

  String _getEntityLabel(String entityType) {
    switch (entityType.toLowerCase()) {
      case 'field':
        return 'الحقل';
      case 'task':
        return 'المهمة';
      case 'irrigation':
        return 'الري';
      case 'alert':
        return 'التنبيه';
      case 'equipment':
        return 'المعدات';
      default:
        return entityType;
    }
  }
}
