/// Advisory Card Widget
/// بطاقة التوصية
///
/// Displays an advisory in a card format with actions
library;

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/config/theme.dart';
import '../../domain/models/advisory.dart';

class AdvisoryCard extends StatelessWidget {
  final Advisory advisory;
  final VoidCallback? onTap;
  final VoidCallback? onApply;
  final VoidCallback? onDismiss;
  final bool compact;

  const AdvisoryCard({
    super.key,
    required this.advisory,
    this.onTap,
    this.onApply,
    this.onDismiss,
    this.compact = false,
  });

  @override
  Widget build(BuildContext context) {
    final priorityColor = Color(int.parse(
      advisory.priorityColorHex.replaceFirst('#', '0xFF'),
    ));

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: advisory.status == AdvisoryStatus.pending
              ? priorityColor.withOpacity(0.3)
              : Colors.grey[200]!,
        ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: EdgeInsets.all(compact ? 12 : 16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Header row
              Row(
                children: [
                  // Type icon
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: _getTypeColor(advisory.type).withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Icon(
                      _getTypeIcon(advisory.type),
                      size: compact ? 18 : 22,
                      color: _getTypeColor(advisory.type),
                    ),
                  ),
                  const SizedBox(width: 12),

                  // Title and type
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          advisory.titleAr.isNotEmpty
                              ? advisory.titleAr
                              : advisory.title,
                          style: TextStyle(
                            fontSize: compact ? 14 : 16,
                            fontWeight: FontWeight.w600,
                          ),
                          maxLines: compact ? 1 : 2,
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 2),
                        Text(
                          advisory.typeAr,
                          style: TextStyle(
                            fontSize: 12,
                            color: _getTypeColor(advisory.type),
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),

                  // Priority badge
                  if (!compact) _buildPriorityBadge(priorityColor),
                ],
              ),

              // Description (if not compact)
              if (!compact && advisory.summaryAr != null) ...[
                const SizedBox(height: 12),
                Text(
                  advisory.summaryAr!,
                  style: TextStyle(
                    fontSize: 14,
                    color: Colors.grey[700],
                    height: 1.4,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ],

              // Field and time info
              const SizedBox(height: 12),
              Row(
                children: [
                  // Field name
                  if (advisory.fieldName != null) ...[
                    Icon(Icons.grass, size: 14, color: Colors.grey[500]),
                    const SizedBox(width: 4),
                    Text(
                      advisory.fieldName!,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(width: 12),
                  ],

                  // Time
                  Icon(Icons.access_time, size: 14, color: Colors.grey[500]),
                  const SizedBox(width: 4),
                  Text(
                    _formatTime(advisory.createdAt),
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),

                  const Spacer(),

                  // Status badge
                  _buildStatusBadge(),
                ],
              ),

              // Actions (if pending and not compact)
              if (!compact &&
                  advisory.status == AdvisoryStatus.pending &&
                  (onApply != null || onDismiss != null)) ...[
                const Divider(height: 24),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    if (onDismiss != null)
                      TextButton(
                        onPressed: onDismiss,
                        child: Text(
                          'تجاهل',
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                      ),
                    if (onApply != null) ...[
                      const SizedBox(width: 8),
                      ElevatedButton.icon(
                        onPressed: onApply,
                        icon: const Icon(Icons.check, size: 18),
                        label: const Text('تم التطبيق'),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 16,
                            vertical: 8,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildPriorityBadge(Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.flag, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            advisory.priorityAr,
            style: TextStyle(
              fontSize: 11,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatusBadge() {
    Color color;
    String label;
    IconData icon;

    switch (advisory.status) {
      case AdvisoryStatus.pending:
        color = Colors.orange;
        label = 'قيد الانتظار';
        icon = Icons.hourglass_empty;
        break;
      case AdvisoryStatus.applied:
        color = Colors.green;
        label = 'مطبقة';
        icon = Icons.check_circle;
        break;
      case AdvisoryStatus.dismissed:
        color = Colors.grey;
        label = 'متجاهلة';
        icon = Icons.cancel_outlined;
        break;
      case AdvisoryStatus.expired:
        color = Colors.red;
        label = 'منتهية';
        icon = Icons.timer_off;
        break;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: color),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 10,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getTypeIcon(AdvisoryType type) {
    switch (type) {
      case AdvisoryType.irrigation:
        return Icons.water_drop;
      case AdvisoryType.fertilization:
        return Icons.eco;
      case AdvisoryType.pestControl:
        return Icons.pest_control;
      case AdvisoryType.diseaseControl:
        return Icons.healing;
      case AdvisoryType.harvest:
        return Icons.agriculture;
      case AdvisoryType.planting:
        return Icons.grass;
      case AdvisoryType.weather:
        return Icons.cloud;
      case AdvisoryType.general:
        return Icons.lightbulb;
    }
  }

  Color _getTypeColor(AdvisoryType type) {
    switch (type) {
      case AdvisoryType.irrigation:
        return Colors.blue;
      case AdvisoryType.fertilization:
        return Colors.green;
      case AdvisoryType.pestControl:
        return Colors.orange;
      case AdvisoryType.diseaseControl:
        return Colors.red;
      case AdvisoryType.harvest:
        return Colors.amber[700]!;
      case AdvisoryType.planting:
        return Colors.teal;
      case AdvisoryType.weather:
        return Colors.indigo;
      case AdvisoryType.general:
        return SahoolTheme.primary;
    }
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final diff = now.difference(time);

    if (diff.inMinutes < 60) {
      return 'منذ ${diff.inMinutes} دقيقة';
    } else if (diff.inHours < 24) {
      return 'منذ ${diff.inHours} ساعة';
    } else if (diff.inDays < 7) {
      return 'منذ ${diff.inDays} يوم';
    } else {
      return DateFormat('dd/MM').format(time);
    }
  }
}
