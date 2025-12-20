import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../domain/entities/field_task.dart';
import '../../../../core/ui/task_mapper.dart';
import '../../../../core/theme/sahool_theme.dart';

/// Task Tile Widget - بطاقة المهمة التفاعلية
///
/// تعرض مهمة واحدة مع:
/// - أيقونة النوع ملونة
/// - عنوان المهمة (يُشطب عند الإكمال)
/// - اسم الحقل ووقت الاستحقاق
/// - Checkbox دائري للإكمال
/// - Haptic feedback عند التفاعل
class TaskTile extends StatefulWidget {
  final FieldTask task;
  final ValueChanged<bool>? onCompletedChanged;
  final VoidCallback? onTap;

  const TaskTile({
    super.key,
    required this.task,
    this.onCompletedChanged,
    this.onTap,
  });

  @override
  State<TaskTile> createState() => _TaskTileState();
}

class _TaskTileState extends State<TaskTile>
    with SingleTickerProviderStateMixin {
  late bool _isChecked;
  late AnimationController _controller;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _isChecked = widget.task.isCompleted;

    _controller = AnimationController(
      duration: const Duration(milliseconds: 150),
      vsync: this,
    );

    _scaleAnimation = Tween<double>(begin: 1.0, end: 0.95).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  void didUpdateWidget(TaskTile oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.task.isCompleted != widget.task.isCompleted) {
      _isChecked = widget.task.isCompleted;
    }
  }

  void _toggleCheckbox() {
    setState(() {
      _isChecked = !_isChecked;
    });

    // Haptic feedback
    HapticFeedback.mediumImpact();

    // Scale animation
    _controller.forward().then((_) => _controller.reverse());

    // Notify parent
    widget.onCompletedChanged?.call(_isChecked);
  }

  @override
  Widget build(BuildContext context) {
    final task = widget.task;

    return ScaleTransition(
      scale: _scaleAnimation,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 2),
            ),
          ],
          border: task.isOverdue && !_isChecked
              ? Border.all(color: SahoolColors.danger.withOpacity(0.5), width: 1.5)
              : null,
        ),
        child: Material(
          color: Colors.transparent,
          child: InkWell(
            onTap: widget.onTap ?? _toggleCheckbox,
            borderRadius: BorderRadius.circular(16),
            child: Padding(
              padding: const EdgeInsets.all(12),
              child: Row(
                children: [
                  // Type Icon
                  _buildTypeIcon(task),

                  const SizedBox(width: 12),

                  // Title & Subtitle
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        // Title with strikethrough animation
                        AnimatedDefaultTextStyle(
                          duration: const Duration(milliseconds: 200),
                          style: TextStyle(
                            fontSize: 15,
                            fontWeight: FontWeight.w600,
                            color: _isChecked ? Colors.grey : Colors.black87,
                            decoration: _isChecked
                                ? TextDecoration.lineThrough
                                : TextDecoration.none,
                            decorationColor: Colors.grey,
                            decorationThickness: 2,
                          ),
                          child: Text(task.title),
                        ),

                        const SizedBox(height: 4),

                        // Field name & time
                        Row(
                          children: [
                            Icon(
                              Icons.location_on_outlined,
                              size: 12,
                              color: Colors.grey[500],
                            ),
                            const SizedBox(width: 2),
                            Text(
                              task.fieldName,
                              style: TextStyle(
                                color: Colors.grey[600],
                                fontSize: 12,
                              ),
                            ),
                            const SizedBox(width: 8),
                            Icon(
                              Icons.access_time,
                              size: 12,
                              color: task.isOverdue && !_isChecked
                                  ? SahoolColors.danger
                                  : Colors.grey[500],
                            ),
                            const SizedBox(width: 2),
                            Text(
                              task.dueTimeFormatted,
                              style: TextStyle(
                                color: task.isOverdue && !_isChecked
                                    ? SahoolColors.danger
                                    : Colors.grey[600],
                                fontSize: 12,
                                fontWeight: task.isOverdue && !_isChecked
                                    ? FontWeight.bold
                                    : FontWeight.normal,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  // Priority indicator (if urgent/high)
                  if (task.priority == TaskPriority.urgent ||
                      task.priority == TaskPriority.high)
                    Container(
                      margin: const EdgeInsets.only(left: 8),
                      child: Icon(
                        task.priority.icon,
                        size: 16,
                        color: task.priorityColor,
                      ),
                    ),

                  // Checkbox
                  _buildCheckbox(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTypeIcon(FieldTask task) {
    return AnimatedContainer(
      duration: const Duration(milliseconds: 200),
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: _isChecked
            ? Colors.grey[200]
            : task.typeLightColor,
        shape: BoxShape.circle,
      ),
      child: Icon(
        task.typeIcon,
        color: _isChecked ? Colors.grey : task.typeColor,
        size: 20,
      ),
    );
  }

  Widget _buildCheckbox() {
    return GestureDetector(
      onTap: _toggleCheckbox,
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 200),
        width: 28,
        height: 28,
        decoration: BoxDecoration(
          shape: BoxShape.circle,
          color: _isChecked ? SahoolColors.success : Colors.transparent,
          border: Border.all(
            color: _isChecked ? SahoolColors.success : Colors.grey[400]!,
            width: 2,
          ),
        ),
        child: _isChecked
            ? const Icon(
                Icons.check,
                size: 16,
                color: Colors.white,
              )
            : null,
      ),
    );
  }
}

/// Dismissible Task Tile - بطاقة قابلة للسحب
class DismissibleTaskTile extends StatelessWidget {
  final FieldTask task;
  final ValueChanged<bool>? onCompletedChanged;
  final VoidCallback? onDismissed;
  final VoidCallback? onTap;

  const DismissibleTaskTile({
    super.key,
    required this.task,
    this.onCompletedChanged,
    this.onDismissed,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Dismissible(
      key: ValueKey(task.id),
      direction: DismissDirection.endToStart,
      onDismissed: (_) => onDismissed?.call(),
      background: Container(
        margin: const EdgeInsets.symmetric(vertical: 6, horizontal: 16),
        decoration: BoxDecoration(
          color: SahoolColors.danger,
          borderRadius: BorderRadius.circular(16),
        ),
        alignment: Alignment.centerRight,
        padding: const EdgeInsets.only(right: 20),
        child: const Icon(
          Icons.delete_outline,
          color: Colors.white,
          size: 24,
        ),
      ),
      child: TaskTile(
        task: task,
        onCompletedChanged: onCompletedChanged,
        onTap: onTap,
      ),
    );
  }
}
