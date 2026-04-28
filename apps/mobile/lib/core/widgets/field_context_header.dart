/// FieldContextHeader – شريط سياق الحقل المشترك
///
/// A compact persistent header that answers "which field am I looking at?"
/// in every screen that is scoped to a specific field. Displays:
///   • Field name (with crop emoji)
///   • Crop type badge
///   • Health indicator dot + label
///   • Last updated timestamp
///
/// Use as a `SliverToBoxAdapter` or inside a `Column`.
library;

import 'package:flutter/material.dart';

import '../../features/fields/domain/entities/field_entity.dart';

/// A compact, read-only banner that shows the essential context for a field.
class FieldContextHeader extends StatelessWidget {
  final FieldEntity field;
  final EdgeInsetsGeometry padding;

  const FieldContextHeader({
    super.key,
    required this.field,
    this.padding = const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
  });

  @override
  Widget build(BuildContext context) {
    final healthColor = _healthColor(field.healthScore);

    return Container(
      padding: padding,
      color: Theme.of(context).colorScheme.surface,
      child: Row(
        children: [
          // Crop emoji avatar
          Container(
            width: 40,
            height: 40,
            decoration: BoxDecoration(
              color: const Color(0xFF367C2B).withValues(alpha: 0.08),
              borderRadius: BorderRadius.circular(10),
            ),
            child: Center(
              child: Text(
                field.cropEmoji,
                style: const TextStyle(fontSize: 22),
              ),
            ),
          ),

          const SizedBox(width: 12),

          // Field name + crop type
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  field.name,
                  style: const TextStyle(
                    fontWeight: FontWeight.bold,
                    fontSize: 15,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                const SizedBox(height: 2),
                Text(
                  field.cropType.isEmpty ? 'غير محدد' : field.cropType,
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
          ),

          const SizedBox(width: 8),

          // Health dot + label + last-updated
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: healthColor,
                      shape: BoxShape.circle,
                    ),
                  ),
                  const SizedBox(width: 4),
                  Text(
                    field.healthLabel,
                    style: TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: healthColor,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 2),
              Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.update, size: 11, color: Colors.grey[400]),
                  const SizedBox(width: 2),
                  Text(
                    _relativeTime(field.updatedAt),
                    style: TextStyle(fontSize: 11, color: Colors.grey[400]),
                  ),
                ],
              ),
            ],
          ),
        ],
      ),
    );
  }

  Color _healthColor(double score) {
    if (score >= 0.8) return const Color(0xFF2E7D32);
    if (score >= 0.6) return const Color(0xFF4CAF50);
    if (score >= 0.4) return Colors.orange;
    return Colors.red;
  }

  String _relativeTime(DateTime dt) {
    final diff = DateTime.now().difference(dt);
    if (diff.inMinutes < 60) return 'منذ ${diff.inMinutes} د';
    if (diff.inHours < 24) return 'منذ ${diff.inHours} س';
    if (diff.inDays == 1) return 'البارحة';
    if (diff.inDays < 7) return 'منذ ${diff.inDays} أيام';
    return '${dt.day}/${dt.month}/${dt.year}';
  }
}
