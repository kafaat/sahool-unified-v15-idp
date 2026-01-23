/// Stock Level Indicator Widget - مؤشر مستوى المخزون
library;

import 'package:flutter/material.dart';

/// مؤشر مستوى المخزون مع شريط ملون
class StockLevelIndicator extends StatelessWidget {
  final double current;
  final double reorderLevel;
  final double maxCapacity;
  final bool showPercentage;
  final bool showLabels;
  final double height;

  const StockLevelIndicator({
    super.key,
    required this.current,
    required this.reorderLevel,
    required this.maxCapacity,
    this.showPercentage = true,
    this.showLabels = false,
    this.height = 24,
  });

  @override
  Widget build(BuildContext context) {
    final percentage = maxCapacity > 0 ? (current / maxCapacity).clamp(0.0, 1.0) : 0.0;
    final reorderPercentage = maxCapacity > 0 ? (reorderLevel / maxCapacity).clamp(0.0, 1.0) : 0.0;

    // تحديد اللون بناءً على المستوى
    Color getColor() {
      if (current <= 0) return Colors.red.shade700;
      if (current <= reorderLevel * 0.5) return Colors.red.shade600;
      if (current <= reorderLevel) return Colors.orange.shade600;
      if (current <= reorderLevel * 2) return Colors.yellow.shade700;
      return Colors.green.shade600;
    }

    final color = getColor();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      mainAxisSize: MainAxisSize.min,
      children: [
        if (showLabels)
          Padding(
            padding: const EdgeInsets.only(bottom: 4),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'المخزون الحالي',
                  style: Theme.of(context).textTheme.bodySmall,
                ),
                Text(
                  '${current.toStringAsFixed(1)} / ${maxCapacity.toStringAsFixed(0)}',
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
          ),
        Stack(
          children: [
            // الخلفية
            Container(
              height: height,
              decoration: BoxDecoration(
                color: Colors.grey.shade200,
                borderRadius: BorderRadius.circular(height / 2),
              ),
            ),
            // خط مستوى إعادة الطلب
            if (reorderPercentage > 0)
              Positioned(
                left: reorderPercentage * MediaQuery.of(context).size.width * 0.9,
                top: 0,
                bottom: 0,
                child: Container(
                  width: 2,
                  color: Colors.orange.shade300,
                ),
              ),
            // شريط المخزون الحالي
            AnimatedContainer(
              duration: const Duration(milliseconds: 300),
              height: height,
              width: percentage * MediaQuery.of(context).size.width * 0.9,
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [
                    color,
                    color.withOpacity(0.7),
                  ],
                ),
                borderRadius: BorderRadius.circular(height / 2),
                boxShadow: [
                  BoxShadow(
                    color: color.withOpacity(0.3),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
            ),
            // النسبة المئوية
            if (showPercentage && percentage > 0.15)
              Positioned.fill(
                child: Center(
                  child: Text(
                    '${(percentage * 100).toStringAsFixed(0)}%',
                    style: TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                      fontSize: height * 0.5,
                      shadows: [
                        Shadow(
                          color: Colors.black.withOpacity(0.5),
                          blurRadius: 2,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
          ],
        ),
        if (showLabels)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: Row(
              children: [
                _buildLegendItem(
                  context,
                  'حرج',
                  Colors.red.shade600,
                ),
                const SizedBox(width: 12),
                _buildLegendItem(
                  context,
                  'منخفض',
                  Colors.orange.shade600,
                ),
                const SizedBox(width: 12),
                _buildLegendItem(
                  context,
                  'جيد',
                  Colors.green.shade600,
                ),
              ],
            ),
          ),
      ],
    );
  }

  Widget _buildLegendItem(BuildContext context, String label, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Container(
          width: 12,
          height: 12,
          decoration: BoxDecoration(
            color: color,
            shape: BoxShape.circle,
          ),
        ),
        const SizedBox(width: 4),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall,
        ),
      ],
    );
  }
}

/// مؤشر دائري بسيط لحالة المخزون
class StockStatusIndicator extends StatelessWidget {
  final double current;
  final double reorderLevel;
  final double size;

  const StockStatusIndicator({
    super.key,
    required this.current,
    required this.reorderLevel,
    this.size = 12,
  });

  @override
  Widget build(BuildContext context) {
    Color getColor() {
      if (current <= 0) return Colors.red.shade700;
      if (current <= reorderLevel * 0.5) return Colors.red.shade600;
      if (current <= reorderLevel) return Colors.orange.shade600;
      return Colors.green.shade600;
    }

    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        color: getColor(),
        shape: BoxShape.circle,
        boxShadow: [
          BoxShadow(
            color: getColor().withOpacity(0.3),
            blurRadius: 4,
            spreadRadius: 1,
          ),
        ],
      ),
    );
  }
}
