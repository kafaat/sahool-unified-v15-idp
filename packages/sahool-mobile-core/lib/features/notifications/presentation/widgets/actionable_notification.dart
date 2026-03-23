/// SAHOOL Actionable Notification Widget
/// عنصر إشعار قابل للتنفيذ
///
/// Displays action buttons for notifications with:
/// - Icon and label
/// - Loading state
/// - Confirmation dialogs
library;

import 'package:flutter/material.dart';

import '../../domain/models/notification_action.dart';

class ActionableNotification extends StatelessWidget {
  final NotificationAction action;
  final VoidCallback onExecute;
  final bool isLoading;
  final bool compact;

  const ActionableNotification({
    super.key,
    required this.action,
    required this.onExecute,
    this.isLoading = false,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    if (compact) {
      return _buildCompactButton(context);
    }
    return _buildFullButton(context);
  }

  Widget _buildFullButton(BuildContext context) {
    final color = action.color ?? Theme.of(context).primaryColor;

    return ElevatedButton.icon(
      onPressed: isLoading ? null : onExecute,
      style: ElevatedButton.styleFrom(
        backgroundColor: color.withOpacity(0.1),
        foregroundColor: color,
        elevation: 0,
        side: BorderSide(color: color.withOpacity(0.3)),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      ),
      icon: isLoading
          ? SizedBox(
              width: 18,
              height: 18,
              child: CircularProgressIndicator(
                strokeWidth: 2,
                color: color,
              ),
            )
          : Icon(action.icon, size: 18),
      label: Text(action.labelAr),
    );
  }

  Widget _buildCompactButton(BuildContext context) {
    final color = action.color ?? Theme.of(context).primaryColor;

    return InkWell(
      onTap: isLoading ? null : onExecute,
      borderRadius: BorderRadius.circular(8),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: color.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (isLoading)
              SizedBox(
                width: 14,
                height: 14,
                child: CircularProgressIndicator(
                  strokeWidth: 2,
                  color: color,
                ),
              )
            else
              Icon(action.icon, size: 14, color: color),
            const SizedBox(width: 4),
            Text(
              action.labelAr,
              style: TextStyle(
                color: color,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Action buttons row for notification cards
class NotificationActionsRow extends StatelessWidget {
  final List<NotificationAction> actions;
  final Function(NotificationAction) onExecute;
  final String? executingActionId;
  final int maxVisible;

  const NotificationActionsRow({
    super.key,
    required this.actions,
    required this.onExecute,
    this.executingActionId,
    this.maxVisible = 3,
  });

  @override
  Widget build(BuildContext context) {
    if (actions.isEmpty) return const SizedBox.shrink();

    final visibleActions = actions.take(maxVisible).toList();
    final hasMore = actions.length > maxVisible;

    return Row(
      mainAxisAlignment: MainAxisAlignment.start,
      children: [
        ...visibleActions.map((action) {
          return Padding(
            padding: const EdgeInsets.only(left: 8),
            child: ActionableNotification(
              action: action,
              onExecute: () => onExecute(action),
              isLoading: executingActionId == action.id,
              compact: true,
            ),
          );
        }),
        if (hasMore)
          Padding(
            padding: const EdgeInsets.only(right: 8),
            child: _MoreActionsButton(
              actions: actions.skip(maxVisible).toList(),
              onExecute: onExecute,
              executingActionId: executingActionId,
            ),
          ),
      ],
    );
  }
}

class _MoreActionsButton extends StatelessWidget {
  final List<NotificationAction> actions;
  final Function(NotificationAction) onExecute;
  final String? executingActionId;

  const _MoreActionsButton({
    required this.actions,
    required this.onExecute,
    this.executingActionId,
  });

  @override
  Widget build(BuildContext context) {
    return PopupMenuButton<NotificationAction>(
      onSelected: onExecute,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: Colors.grey.withOpacity(0.1),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(
              Icons.more_horiz,
              size: 14,
              color: Colors.grey.shade600,
            ),
            const SizedBox(width: 4),
            Text(
              '${actions.length}+',
              style: TextStyle(
                color: Colors.grey.shade600,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
      itemBuilder: (context) {
        return actions.map((action) {
          final isExecuting = executingActionId == action.id;
          return PopupMenuItem<NotificationAction>(
            value: action,
            enabled: !isExecuting,
            child: Row(
              children: [
                if (isExecuting)
                  SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: action.color ?? Theme.of(context).primaryColor,
                    ),
                  )
                else
                  Icon(
                    action.icon,
                    color: action.color ?? Theme.of(context).primaryColor,
                    size: 20,
                  ),
                const SizedBox(width: 12),
                Text(action.labelAr),
              ],
            ),
          );
        }).toList();
      },
    );
  }
}

/// Quick action buttons (swipe actions style)
class QuickActionButtons extends StatelessWidget {
  final List<NotificationAction> actions;
  final Function(NotificationAction) onExecute;

  const QuickActionButtons({
    super.key,
    required this.actions,
    required this.onExecute,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: actions.map((action) {
        return _QuickActionButton(
          action: action,
          onTap: () => onExecute(action),
        );
      }).toList(),
    );
  }
}

class _QuickActionButton extends StatelessWidget {
  final NotificationAction action;
  final VoidCallback onTap;

  const _QuickActionButton({
    required this.action,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = action.color ?? Theme.of(context).primaryColor;

    return Material(
      color: color,
      child: InkWell(
        onTap: onTap,
        child: Container(
          width: 72,
          height: double.infinity,
          alignment: Alignment.center,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                action.icon,
                color: Colors.white,
                size: 24,
              ),
              const SizedBox(height: 4),
              Text(
                action.labelAr,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 11,
                ),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Snooze options bottom sheet
class SnoozeOptionsSheet extends StatelessWidget {
  final Function(Duration) onSnooze;

  const SnoozeOptionsSheet({
    super.key,
    required this.onSnooze,
  });

  @override
  Widget build(BuildContext context) {
    return SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text(
              'تأجيل لمدة',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          const Divider(height: 1),
          _buildOption(
            context,
            icon: Icons.schedule,
            label: '30 دقيقة',
            duration: const Duration(minutes: 30),
          ),
          _buildOption(
            context,
            icon: Icons.schedule,
            label: 'ساعة واحدة',
            duration: const Duration(hours: 1),
          ),
          _buildOption(
            context,
            icon: Icons.schedule,
            label: '3 ساعات',
            duration: const Duration(hours: 3),
          ),
          _buildOption(
            context,
            icon: Icons.wb_sunny,
            label: 'غداً صباحاً',
            duration: _getNextMorning(),
          ),
          _buildOption(
            context,
            icon: Icons.next_week,
            label: 'الأسبوع القادم',
            duration: const Duration(days: 7),
          ),
          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _buildOption(
    BuildContext context, {
    required IconData icon,
    required String label,
    required Duration duration,
  }) {
    return ListTile(
      leading: Icon(icon, color: Colors.orange),
      title: Text(label),
      onTap: () {
        Navigator.pop(context);
        onSnooze(duration);
      },
    );
  }

  Duration _getNextMorning() {
    final now = DateTime.now();
    final tomorrow = DateTime(now.year, now.month, now.day + 1, 8, 0);
    return tomorrow.difference(now);
  }
}
