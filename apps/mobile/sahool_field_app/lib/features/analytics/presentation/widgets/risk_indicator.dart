/// Risk Indicator Widget
/// ودجت مؤشر المخاطر
library;

import 'package:flutter/material.dart';
import '../../data/models/analytics_models.dart';

/// Displays overall risk level with visual gauge
/// يعرض مستوى المخاطر الإجمالي مع مقياس بصري
class RiskIndicator extends StatelessWidget {
  final double score;
  final RiskLevel level;

  const RiskIndicator({
    super.key,
    required this.score,
    required this.level,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isRtl = Directionality.of(context) == TextDirection.rtl;

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  isRtl ? 'مستوى المخاطر الإجمالي' : 'Overall Risk Level',
                  style: theme.textTheme.titleMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                _buildLevelBadge(isRtl),
              ],
            ),
            const SizedBox(height: 20),
            _buildRiskGauge(context),
            const SizedBox(height: 16),
            _buildRiskScale(isRtl),
          ],
        ),
      ),
    );
  }

  Widget _buildLevelBadge(bool isRtl) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: _getLevelColor(level).withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: _getLevelColor(level)),
      ),
      child: Text(
        isRtl ? _getLevelNameAr(level) : _getLevelName(level),
        style: TextStyle(
          color: _getLevelColor(level),
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  Widget _buildRiskGauge(BuildContext context) {
    return SizedBox(
      height: 30,
      child: Stack(
        children: [
          // Background gradient bar
          Container(
            height: 20,
            decoration: BoxDecoration(
              borderRadius: BorderRadius.circular(10),
              gradient: const LinearGradient(
                colors: [
                  Colors.green,
                  Colors.lightGreen,
                  Colors.yellow,
                  Colors.orange,
                  Colors.red,
                ],
              ),
            ),
          ),
          // Position indicator
          Positioned(
            left: (score / 100) * (MediaQuery.of(context).size.width - 72) - 10,
            top: -5,
            child: Container(
              width: 30,
              height: 30,
              decoration: BoxDecoration(
                color: Colors.white,
                shape: BoxShape.circle,
                border: Border.all(
                  color: _getLevelColor(level),
                  width: 3,
                ),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.2),
                    blurRadius: 4,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: Center(
                child: Text(
                  score.toStringAsFixed(0),
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: _getLevelColor(level),
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRiskScale(bool isRtl) {
    final labels = isRtl
        ? ['ضئيل', 'منخفض', 'متوسط', 'عالي', 'حرج']
        : ['Minimal', 'Low', 'Moderate', 'High', 'Critical'];

    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: labels
          .map((label) => Text(
                label,
                style: const TextStyle(fontSize: 10, color: Colors.grey),
              ))
          .toList(),
    );
  }

  Color _getLevelColor(RiskLevel level) {
    switch (level) {
      case RiskLevel.minimal:
        return Colors.green;
      case RiskLevel.low:
        return Colors.lightGreen;
      case RiskLevel.moderate:
        return Colors.amber;
      case RiskLevel.high:
        return Colors.orange;
      case RiskLevel.critical:
        return Colors.red;
    }
  }

  String _getLevelName(RiskLevel level) {
    switch (level) {
      case RiskLevel.minimal:
        return 'Minimal';
      case RiskLevel.low:
        return 'Low';
      case RiskLevel.moderate:
        return 'Moderate';
      case RiskLevel.high:
        return 'High';
      case RiskLevel.critical:
        return 'Critical';
    }
  }

  String _getLevelNameAr(RiskLevel level) {
    switch (level) {
      case RiskLevel.minimal:
        return 'ضئيل';
      case RiskLevel.low:
        return 'منخفض';
      case RiskLevel.moderate:
        return 'متوسط';
      case RiskLevel.high:
        return 'عالي';
      case RiskLevel.critical:
        return 'حرج';
    }
  }
}
