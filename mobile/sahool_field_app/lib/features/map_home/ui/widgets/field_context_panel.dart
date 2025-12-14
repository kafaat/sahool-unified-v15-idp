import 'package:flutter/material.dart';
import '../../../../core/ui/field_status_mapper.dart';
import '../../../field/domain/entities/field.dart';
import '../../../../core/theme/sahool_theme.dart';

/// Field Context Panel - لوحة معلومات الحقل
///
/// تظهر عند الضغط على حقل في الخريطة
/// توفر نظرة سريعة + أزرار الإجراءات
class FieldContextPanel extends StatelessWidget {
  final Field field;
  final VoidCallback onClose;
  final VoidCallback onDetails;
  final VoidCallback? onAddTask;
  final VoidCallback? onNavigate;

  const FieldContextPanel({
    super.key,
    required this.field,
    required this.onClose,
    required this.onDetails,
    this.onAddTask,
    this.onNavigate,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.15),
            blurRadius: 20,
            offset: const Offset(0, -5),
          ),
        ],
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Drag handle
          Center(
            child: Container(
              margin: const EdgeInsets.only(top: 12),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),

          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Header: Name + Status + Close
                _buildHeader(),

                const SizedBox(height: 16),

                // Quick Stats Row
                _buildStatsRow(),

                const SizedBox(height: 16),

                // NDVI Progress Bar
                _buildNdviBar(),

                const SizedBox(height: 20),

                // Action Buttons
                _buildActions(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Status indicator circle
        Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            color: field.statusBackgroundColor,
            shape: BoxShape.circle,
          ),
          child: Icon(
            field.statusIcon,
            color: field.statusColor,
            size: 24,
          ),
        ),
        const SizedBox(width: 12),

        // Name and crop type
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                field.name,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 18,
                ),
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Icon(Icons.grass, size: 14, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    field.cropType,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                  const SizedBox(width: 12),
                  Icon(Icons.square_foot, size: 14, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text(
                    field.areaFormatted,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 13,
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),

        // Close button
        IconButton(
          onPressed: onClose,
          icon: const Icon(Icons.close),
          style: IconButton.styleFrom(
            backgroundColor: Colors.grey[100],
          ),
        ),
      ],
    );
  }

  Widget _buildStatsRow() {
    return Row(
      children: [
        // Status badge
        _buildBadge(
          label: field.statusText,
          color: field.statusColor,
          textColor: Colors.white,
          icon: field.statusIcon,
        ),

        const SizedBox(width: 8),

        // NDVI badge
        _buildBadge(
          label: 'NDVI ${field.ndviFormatted}',
          color: field.statusBackgroundColor,
          textColor: field.statusColor,
        ),

        const Spacer(),

        // Pending tasks (if any)
        if (field.pendingTasks > 0)
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.orange.withOpacity(0.1),
              borderRadius: BorderRadius.circular(12),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.task_alt, size: 14, color: Colors.orange),
                const SizedBox(width: 4),
                Text(
                  '${field.pendingTasks} مهام',
                  style: const TextStyle(
                    color: Colors.orange,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildNdviBar() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(
              'مؤشر صحة المحصول',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
            Text(
              field.ndviPercentage,
              style: TextStyle(
                color: field.statusColor,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: field.ndvi,
            backgroundColor: Colors.grey[200],
            valueColor: AlwaysStoppedAnimation(field.statusColor),
            minHeight: 8,
          ),
        ),
      ],
    );
  }

  Widget _buildActions() {
    return Row(
      children: [
        // Primary action: View Details
        Expanded(
          flex: 2,
          child: ElevatedButton.icon(
            onPressed: onDetails,
            icon: const Icon(Icons.analytics_outlined),
            label: const Text('تحليل شامل'),
            style: ElevatedButton.styleFrom(
              backgroundColor: SahoolColors.primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ),

        const SizedBox(width: 12),

        // Secondary action: Add Task
        _buildIconAction(
          icon: Icons.add_task,
          onTap: onAddTask,
          tooltip: 'إضافة مهمة',
        ),

        const SizedBox(width: 8),

        // Navigate to field
        _buildIconAction(
          icon: Icons.navigation,
          onTap: onNavigate,
          tooltip: 'الانتقال للحقل',
        ),
      ],
    );
  }

  Widget _buildIconAction({
    required IconData icon,
    VoidCallback? onTap,
    required String tooltip,
  }) {
    return Tooltip(
      message: tooltip,
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: 48,
          height: 48,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey[300]!),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: Colors.grey[700]),
        ),
      ),
    );
  }

  Widget _buildBadge({
    required String label,
    required Color color,
    required Color textColor,
    IconData? icon,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (icon != null) ...[
            Icon(icon, size: 14, color: textColor),
            const SizedBox(width: 4),
          ],
          Text(
            label,
            style: TextStyle(
              color: textColor,
              fontWeight: FontWeight.bold,
              fontSize: 12,
            ),
          ),
        ],
      ),
    );
  }
}

/// Animated wrapper for the context panel
class AnimatedFieldContextPanel extends StatelessWidget {
  final Field? field;
  final VoidCallback onClose;
  final VoidCallback onDetails;
  final VoidCallback? onAddTask;

  const AnimatedFieldContextPanel({
    super.key,
    required this.field,
    required this.onClose,
    required this.onDetails,
    this.onAddTask,
  });

  @override
  Widget build(BuildContext context) {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 300),
      transitionBuilder: (Widget child, Animation<double> animation) {
        return SlideTransition(
          position: Tween<Offset>(
            begin: const Offset(0, 1),
            end: Offset.zero,
          ).animate(CurvedAnimation(
            parent: animation,
            curve: Curves.easeOutCubic,
          )),
          child: child,
        );
      },
      child: field != null
          ? FieldContextPanel(
              key: ValueKey(field!.id),
              field: field!,
              onClose: onClose,
              onDetails: onDetails,
              onAddTask: onAddTask,
            )
          : const SizedBox.shrink(),
    );
  }
}
