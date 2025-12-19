import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/theme/sahool_glass.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../logic/drawing_provider.dart';
import '../../../../core/di/providers.dart';
import '../../../polygon_editor/utils/geo_utils.dart';

/// أدوات التحكم في الرسم - Drawing Controls
/// تظهر في أسفل الشاشة عند تفعيل وضع الرسم
class DrawingControls extends ConsumerWidget {
  final VoidCallback? onSave;
  final String tenantId;

  const DrawingControls({
    super.key,
    this.onSave,
    required this.tenantId,
  });

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final drawingState = ref.watch(drawingProvider);

    if (!drawingState.isDrawing) return const SizedBox.shrink();

    final areaHa = drawingState.isValid
        ? GeoUtils.calculateAreaHectares(drawingState.points)
        : 0.0;

    return Positioned(
      bottom: 40,
      left: 20,
      right: 20,
      child: SahoolGlass(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 16),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // عداد النقاط والمساحة
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildInfoChip(
                  icon: Icons.location_on,
                  label: '${drawingState.pointCount} نقاط',
                  color: SahoolColors.info,
                ),
                const SizedBox(width: 16),
                if (drawingState.isValid)
                  _buildInfoChip(
                    icon: Icons.straighten,
                    label: '${areaHa.toStringAsFixed(2)} هكتار',
                    color: SahoolColors.success,
                  ),
              ],
            ),
            const SizedBox(height: 16),

            // أزرار التحكم
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                // زر الإلغاء
                _ControlButton(
                  icon: Icons.close,
                  label: 'إلغاء',
                  color: SahoolColors.danger,
                  onPressed: () => ref.read(drawingProvider.notifier).cancelDrawing(),
                ),

                // زر التراجع
                _ControlButton(
                  icon: Icons.undo,
                  label: 'تراجع',
                  color: SahoolColors.warning,
                  onPressed: drawingState.points.isEmpty
                      ? null
                      : () => ref.read(drawingProvider.notifier).undoLastPoint(),
                ),

                // زر المسح
                _ControlButton(
                  icon: Icons.delete_outline,
                  label: 'مسح',
                  color: Colors.grey,
                  onPressed: drawingState.points.isEmpty
                      ? null
                      : () => ref.read(drawingProvider.notifier).clearPoints(),
                ),

                // زر الحفظ
                _ControlButton(
                  icon: Icons.check,
                  label: 'حفظ',
                  color: SahoolColors.success,
                  onPressed: drawingState.isValid
                      ? () => _saveField(context, ref)
                      : null,
                  isPrimary: true,
                ),
              ],
            ),

            // تعليمات
            const SizedBox(height: 12),
            Text(
              drawingState.isValid
                  ? 'اضغط حفظ لإنشاء الحقل'
                  : 'انقر على الخريطة لإضافة ${3 - drawingState.pointCount} نقاط على الأقل',
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoChip({
    required IconData icon,
    required String label,
    required Color color,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 6),
          Text(
            label,
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: color,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _saveField(BuildContext context, WidgetRef ref) async {
    final points = ref.read(drawingProvider).points;

    // عرض Dialog لإدخال اسم الحقل
    final fieldName = await showDialog<String>(
      context: context,
      builder: (context) => _FieldNameDialog(),
    );

    if (fieldName == null || fieldName.isEmpty) return;

    try {
      final repo = ref.read(fieldsRepoProvider);

      await repo.createField(
        tenantId: tenantId,
        name: fieldName,
        boundary: points,
      );

      // إنهاء الرسم
      ref.read(drawingProvider.notifier).cancelDrawing();

      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Row(
              children: [
                const Icon(Icons.check_circle, color: Colors.white),
                const SizedBox(width: 8),
                Text('تم حفظ الحقل "$fieldName" بنجاح!'),
              ],
            ),
            backgroundColor: SahoolColors.success,
            behavior: SnackBarBehavior.floating,
          ),
        );
      }

      onSave?.call();
    } catch (e) {
      if (context.mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('خطأ في حفظ الحقل: $e'),
            backgroundColor: SahoolColors.danger,
          ),
        );
      }
    }
  }
}

class _ControlButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final Color color;
  final VoidCallback? onPressed;
  final bool isPrimary;

  const _ControlButton({
    required this.icon,
    required this.label,
    required this.color,
    this.onPressed,
    this.isPrimary = false,
  });

  @override
  Widget build(BuildContext context) {
    final isEnabled = onPressed != null;

    return GestureDetector(
      onTap: onPressed,
      child: Opacity(
        opacity: isEnabled ? 1.0 : 0.4,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: EdgeInsets.all(isPrimary ? 14 : 10),
              decoration: BoxDecoration(
                color: isPrimary && isEnabled
                    ? color
                    : color.withOpacity(0.1),
                shape: BoxShape.circle,
                border: Border.all(
                  color: color.withOpacity(0.3),
                  width: isPrimary ? 2 : 1,
                ),
              ),
              child: Icon(
                icon,
                color: isPrimary && isEnabled ? Colors.white : color,
                size: isPrimary ? 28 : 22,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              label,
              style: TextStyle(
                fontSize: 11,
                color: isEnabled ? color : Colors.grey,
                fontWeight: isEnabled ? FontWeight.w600 : FontWeight.normal,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _FieldNameDialog extends StatefulWidget {
  @override
  State<_FieldNameDialog> createState() => _FieldNameDialogState();
}

class _FieldNameDialogState extends State<_FieldNameDialog> {
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Row(
        children: [
          Icon(Icons.grass, color: SahoolColors.primary),
          const SizedBox(width: 8),
          const Text('اسم الحقل'),
        ],
      ),
      content: TextField(
        controller: _controller,
        autofocus: true,
        decoration: const InputDecoration(
          hintText: 'أدخل اسم الحقل...',
          prefixIcon: Icon(Icons.edit),
        ),
        onSubmitted: (value) {
          if (value.isNotEmpty) {
            Navigator.pop(context, value);
          }
        },
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('إلغاء'),
        ),
        ElevatedButton(
          onPressed: () {
            if (_controller.text.isNotEmpty) {
              Navigator.pop(context, _controller.text);
            }
          },
          child: const Text('حفظ'),
        ),
      ],
    );
  }
}
