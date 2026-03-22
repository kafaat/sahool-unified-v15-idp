/// Water Balance Card Widget - بطاقة توازن المياه
/// Visual card showing soil moisture gauge, ET0/ETc values,
/// water deficit/surplus, and next irrigation countdown.
/// بطاقة مرئية تعرض مقياس رطوبة التربة والتبخر-نتح والعجز المائي
library;
import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../../data/repository/irrigation_repository.dart';

/// Water Balance Card
/// بطاقة توازن المياه المرئية
class WaterBalanceCard extends StatelessWidget {
  final WaterBalanceData waterBalance;
  final bool isArabic;
  final VoidCallback? onTap;

  const WaterBalanceCard({
    super.key,
    required this.waterBalance,
    this.isArabic = true,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return OrganicCard(
      onTap: onTap,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.blue.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.water_drop, color: Colors.blue),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isArabic ? 'توازن المياه' : 'Water Balance',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                    Text(
                      isArabic
                          ? waterBalance.statusAr
                          : waterBalance.status,
                      style: TextStyle(
                        color: _getStatusColor(),
                        fontSize: 13,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ],
                ),
              ),
              // Status indicator
              Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: _getStatusColor(),
                  shape: BoxShape.circle,
                ),
              ),
            ],
          ),

          const SizedBox(height: 20),

          // Soil Moisture Gauge - مقياس رطوبة التربة
          Center(
            child: _SoilMoistureGauge(
              percent: waterBalance.soilMoisturePercent,
              isArabic: isArabic,
            ),
          ),

          const SizedBox(height: 20),

          // ET Values Bar - قيم التبخر-نتح
          _buildETValuesBar(),

          const SizedBox(height: 16),

          // Water Balance Summary - ملخص توازن المياه
          _buildBalanceSummary(),

          // Deficit/Surplus Alert
          if (waterBalance.deficit > 0 || waterBalance.surplus > 0) ...[
            const SizedBox(height: 12),
            _buildDeficitSurplusAlert(),
          ],
        ],
      ),
    );
  }

  /// ET0/ETc comparison bar
  Widget _buildETValuesBar() {
    final maxET = math.max(waterBalance.et0, waterBalance.etc);
    final et0Width = maxET > 0 ? waterBalance.et0 / maxET : 0.0;
    final etcWidth = maxET > 0 ? waterBalance.etc / maxET : 0.0;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          isArabic ? 'التبخر-نتح' : 'Evapotranspiration',
          style: TextStyle(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: Colors.grey[700],
          ),
        ),
        const SizedBox(height: 8),
        // ET0 bar
        Row(
          children: [
            SizedBox(
              width: 40,
              child: Text(
                'ET0',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ),
            Expanded(
              child: Stack(
                children: [
                  Container(
                    height: 16,
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  FractionallySizedBox(
                    widthFactor: et0Width.clamp(0, 1),
                    child: Container(
                      height: 16,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFFFF9800), Color(0xFFFF5722)],
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 55,
              child: Text(
                '${waterBalance.et0.toStringAsFixed(1)} mm',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.end,
              ),
            ),
          ],
        ),
        const SizedBox(height: 6),
        // ETc bar
        Row(
          children: [
            SizedBox(
              width: 40,
              child: Text(
                'ETc',
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ),
            Expanded(
              child: Stack(
                children: [
                  Container(
                    height: 16,
                    decoration: BoxDecoration(
                      color: Colors.grey[200],
                      borderRadius: BorderRadius.circular(8),
                    ),
                  ),
                  FractionallySizedBox(
                    widthFactor: etcWidth.clamp(0, 1),
                    child: Container(
                      height: 16,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            SahoolColors.forestGreen.withOpacity(0.6),
                            SahoolColors.forestGreen,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(8),
                      ),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 8),
            SizedBox(
              width: 55,
              child: Text(
                '${waterBalance.etc.toStringAsFixed(1)} mm',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.end,
              ),
            ),
          ],
        ),
      ],
    );
  }

  /// Water balance summary row
  Widget _buildBalanceSummary() {
    return Row(
      children: [
        Expanded(
          child: _BalanceItem(
            icon: Icons.grain,
            label: isArabic ? 'أمطار' : 'Rain',
            value: '${waterBalance.rainfall.toStringAsFixed(1)} mm',
            color: Colors.blue,
          ),
        ),
        Container(
          width: 1,
          height: 36,
          color: Colors.grey[200],
        ),
        Expanded(
          child: _BalanceItem(
            icon: Icons.water,
            label: isArabic ? 'ري مطبق' : 'Applied',
            value: '${waterBalance.irrigationApplied.toStringAsFixed(1)} mm',
            color: SahoolColors.forestGreen,
          ),
        ),
        Container(
          width: 1,
          height: 36,
          color: Colors.grey[200],
        ),
        Expanded(
          child: _BalanceItem(
            icon: waterBalance.deficit > 0
                ? Icons.arrow_downward
                : Icons.arrow_upward,
            label: waterBalance.deficit > 0
                ? (isArabic ? 'عجز' : 'Deficit')
                : (isArabic ? 'فائض' : 'Surplus'),
            value: waterBalance.deficit > 0
                ? '${waterBalance.deficit.toStringAsFixed(1)} mm'
                : '${waterBalance.surplus.toStringAsFixed(1)} mm',
            color: waterBalance.deficit > 0
                ? SahoolColors.danger
                : SahoolColors.forestGreen,
          ),
        ),
      ],
    );
  }

  /// Deficit/Surplus alert banner
  Widget _buildDeficitSurplusAlert() {
    final isDeficit = waterBalance.deficit > 0;
    final color = isDeficit ? SahoolColors.harvestGold : Colors.blue;

    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: color.withOpacity(0.08),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withOpacity(0.2)),
      ),
      child: Row(
        children: [
          Icon(
            isDeficit ? Icons.warning_amber : Icons.info_outline,
            color: color,
            size: 18,
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Text(
              isDeficit
                  ? (isArabic
                      ? 'يحتاج الحقل ري: عجز ${waterBalance.deficit.toStringAsFixed(1)} مم'
                      : 'Field needs irrigation: deficit ${waterBalance.deficit.toStringAsFixed(1)} mm')
                  : (isArabic
                      ? 'رطوبة التربة كافية. فائض ${waterBalance.surplus.toStringAsFixed(1)} مم'
                      : 'Soil moisture adequate. Surplus ${waterBalance.surplus.toStringAsFixed(1)} mm'),
              style: TextStyle(
                color: color,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor() {
    final percent = waterBalance.soilMoisturePercent;
    if (percent >= 60) return SahoolColors.forestGreen;
    if (percent >= 40) return SahoolColors.harvestGold;
    if (percent >= 20) return Colors.orange;
    return SahoolColors.danger;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Soil Moisture Gauge - مقياس رطوبة التربة
// ═══════════════════════════════════════════════════════════════════════════════

class _SoilMoistureGauge extends StatelessWidget {
  final double percent;
  final bool isArabic;
  final double size;

  const _SoilMoistureGauge({
    required this.percent,
    this.isArabic = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = _getColor();

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: CustomPaint(
            painter: _MoistureGaugePainter(
              percent: percent / 100,
              color: color,
              backgroundColor: Colors.grey[200]!,
            ),
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    Icons.water_drop,
                    color: color,
                    size: size * 0.18,
                  ),
                  Text(
                    '${percent.toStringAsFixed(0)}%',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: size * 0.2,
                      color: color,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(height: 8),
        Text(
          isArabic ? 'رطوبة التربة' : 'Soil Moisture',
          style: TextStyle(
            color: Colors.grey[600],
            fontWeight: FontWeight.w500,
            fontSize: 14,
          ),
        ),
        Text(
          _getLabel(),
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.w600,
            fontSize: 13,
          ),
        ),
      ],
    );
  }

  Color _getColor() {
    if (percent >= 60) return SahoolColors.forestGreen;
    if (percent >= 40) return SahoolColors.harvestGold;
    if (percent >= 20) return Colors.orange;
    return SahoolColors.danger;
  }

  String _getLabel() {
    if (percent >= 75) return isArabic ? 'ممتازة' : 'Excellent';
    if (percent >= 60) return isArabic ? 'جيدة' : 'Good';
    if (percent >= 40) return isArabic ? 'متوسطة' : 'Moderate';
    if (percent >= 20) return isArabic ? 'منخفضة' : 'Low';
    return isArabic ? 'حرجة - يجب الري فوراً!' : 'Critical - Irrigate now!';
  }
}

/// Custom painter for the soil moisture gauge arc
class _MoistureGaugePainter extends CustomPainter {
  final double percent;
  final Color color;
  final Color backgroundColor;

  _MoistureGaugePainter({
    required this.percent,
    required this.color,
    required this.backgroundColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = math.min(size.width, size.height) / 2 - 10;
    const strokeWidth = 14.0;
    const startAngle = math.pi * 0.75;
    const sweepAngle = math.pi * 1.5;

    // Background arc
    final bgPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      startAngle,
      sweepAngle,
      false,
      bgPaint,
    );

    // Gradient foreground arc
    final sweepRect = Rect.fromCircle(center: center, radius: radius);
    final gradient = SweepGradient(
      startAngle: startAngle,
      endAngle: startAngle + sweepAngle * percent,
      colors: [
        color.withOpacity(0.5),
        color,
      ],
    );

    final fgPaint = Paint()
      ..shader = gradient.createShader(sweepRect)
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      sweepRect,
      startAngle,
      sweepAngle * percent,
      false,
      fgPaint,
    );

    // Zone markers (wilting point, field capacity thresholds)
    final tickPaint = Paint()
      ..color = Colors.grey[400]!
      ..style = PaintingStyle.stroke
      ..strokeWidth = 1.5;

    // 20% mark (wilting danger zone)
    _drawTick(canvas, center, radius, strokeWidth, startAngle, sweepAngle,
        0.2, tickPaint);
    // 40% mark
    _drawTick(canvas, center, radius, strokeWidth, startAngle, sweepAngle,
        0.4, tickPaint);
    // 60% mark (field capacity zone)
    _drawTick(canvas, center, radius, strokeWidth, startAngle, sweepAngle,
        0.6, tickPaint);
  }

  void _drawTick(Canvas canvas, Offset center, double radius,
      double strokeWidth, double startAngle, double sweepAngle,
      double position, Paint paint) {
    final angle = startAngle + sweepAngle * position;
    final innerRadius = radius - strokeWidth / 2 - 4;
    final outerRadius = radius - strokeWidth / 2 - 12;

    canvas.drawLine(
      Offset(
        center.dx + innerRadius * math.cos(angle),
        center.dy + innerRadius * math.sin(angle),
      ),
      Offset(
        center.dx + outerRadius * math.cos(angle),
        center.dy + outerRadius * math.sin(angle),
      ),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant _MoistureGaugePainter oldDelegate) {
    return percent != oldDelegate.percent || color != oldDelegate.color;
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Balance Item Widget
// ═══════════════════════════════════════════════════════════════════════════════

class _BalanceItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _BalanceItem({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Icon(icon, color: color, size: 18),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 13,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 11, color: Colors.grey[600]),
        ),
      ],
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════════
// Compact Water Balance Card (for use in lists)
// ═══════════════════════════════════════════════════════════════════════════════

/// Compact water balance card for list views
/// بطاقة توازن المياه المختصرة للقوائم
class CompactWaterBalanceCard extends StatelessWidget {
  final WaterBalanceData waterBalance;
  final bool isArabic;
  final VoidCallback? onTap;

  const CompactWaterBalanceCard({
    super.key,
    required this.waterBalance,
    this.isArabic = true,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final moistureColor = _getMoistureColor();

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          border: Border.all(color: Colors.grey.withOpacity(0.1)),
        ),
        child: Row(
          children: [
            // Moisture indicator
            Container(
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                color: moistureColor.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.water_drop, color: moistureColor, size: 18),
                  Text(
                    '${waterBalance.soilMoisturePercent.toStringAsFixed(0)}%',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 11,
                      color: moistureColor,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    isArabic ? 'توازن المياه' : 'Water Balance',
                    style: const TextStyle(
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                  const SizedBox(height: 2),
                  Text(
                    'ET0: ${waterBalance.et0.toStringAsFixed(1)} | '
                    'ETc: ${waterBalance.etc.toStringAsFixed(1)} mm',
                    style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                  ),
                ],
              ),
            ),
            if (waterBalance.needsIrrigation)
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(
                  color: SahoolColors.harvestGold.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  isArabic ? 'يحتاج ري' : 'Needs water',
                  style: const TextStyle(
                    fontSize: 10,
                    color: SahoolColors.harvestGold,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Color _getMoistureColor() {
    final percent = waterBalance.soilMoisturePercent;
    if (percent >= 60) return SahoolColors.forestGreen;
    if (percent >= 40) return SahoolColors.harvestGold;
    if (percent >= 20) return Colors.orange;
    return SahoolColors.danger;
  }
}
