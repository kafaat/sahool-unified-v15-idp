import 'package:flutter/material.dart';
import '../../../crops/data/crop_helper.dart';

/// بطاقة الحقل
class FieldCard extends StatelessWidget {
  final String fieldId;
  final String name;
  final double areaHectares;
  final String cropType;
  final double healthScore;
  final VoidCallback? onTap;

  const FieldCard({
    super.key,
    required this.fieldId,
    required this.name,
    required this.areaHectares,
    required this.cropType,
    required this.healthScore,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final healthColor = _getHealthColor();
    final healthLabel = _getHealthLabel();

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // أيقونة المحصول
              Container(
                width: 56,
                height: 56,
                decoration: BoxDecoration(
                  color: const Color(0xFF367C2B).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    _getCropEmoji(),
                    style: const TextStyle(fontSize: 28),
                  ),
                ),
              ),

              const SizedBox(width: 16),

              // المعلومات
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.straighten, size: 14, color: Colors.grey[600]),
                        const SizedBox(width: 4),
                        Text(
                          '${areaHectares.toStringAsFixed(1)} هكتار',
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 13,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Icon(Icons.eco, size: 14, color: Colors.grey[600]),
                        const SizedBox(width: 4),
                        Text(
                          CropHelper.getCropNameAr(cropType),
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

              // مؤشر الصحة
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 10,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: healthColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(20),
                    ),
                    child: Row(
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
                        const SizedBox(width: 6),
                        Text(
                          healthLabel,
                          style: TextStyle(
                            color: healthColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${(healthScore * 100).round()}%',
                    style: TextStyle(
                      color: healthColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 18,
                    ),
                  ),
                ],
              ),

              const SizedBox(width: 8),
              Icon(Icons.chevron_left, color: Colors.grey[400]),
            ],
          ),
        ),
      ),
    );
  }

  Color _getHealthColor() {
    if (healthScore >= 0.7) return Colors.green;
    if (healthScore >= 0.5) return Colors.orange;
    return Colors.red;
  }

  String _getHealthLabel() {
    if (healthScore >= 0.7) return 'جيد';
    if (healthScore >= 0.5) return 'متوسط';
    return 'ضعيف';
  }

  String _getCropEmoji() {
    return CropHelper.getCropEmoji(cropType);
  }
}
