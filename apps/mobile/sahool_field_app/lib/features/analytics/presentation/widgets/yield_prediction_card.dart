/// Yield Prediction Card Widget
/// ودجت بطاقة توقع الإنتاجية
library;

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../data/models/analytics_models.dart';

/// Displays yield prediction with revenue estimate
/// يعرض توقع الإنتاجية مع تقدير الإيرادات
class YieldPredictionCard extends StatelessWidget {
  final YieldPrediction prediction;

  const YieldPredictionCard({
    super.key,
    required this.prediction,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isRtl = Directionality.of(context) == TextDirection.rtl;
    final numberFormat = NumberFormat('#,###');

    return Card(
      elevation: 4,
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.green.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.agriculture,
                    color: Colors.green,
                    size: 32,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        isRtl ? 'توقع الإنتاجية' : 'Yield Prediction',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        isRtl ? prediction.cropTypeAr : prediction.cropType,
                        style: TextStyle(
                          color: Colors.grey.shade600,
                        ),
                      ),
                    ],
                  ),
                ),
                _buildQualityBadge(isRtl),
              ],
            ),

            const Divider(height: 32),

            // Predicted yield
            _buildStatRow(
              context,
              icon: Icons.scale,
              label: isRtl ? 'الإنتاجية المتوقعة' : 'Predicted Yield',
              value: '${numberFormat.format(prediction.predictedYield)} ${isRtl ? 'كجم' : 'kg'}',
              color: Colors.green,
            ),

            const SizedBox(height: 12),

            // Yield range
            _buildStatRow(
              context,
              icon: Icons.swap_vert,
              label: isRtl ? 'النطاق المتوقع' : 'Expected Range',
              value:
                  '${numberFormat.format(prediction.minYield)} - ${numberFormat.format(prediction.maxYield)} ${isRtl ? 'كجم' : 'kg'}',
              color: Colors.blue,
            ),

            const SizedBox(height: 12),

            // Harvest date
            _buildStatRow(
              context,
              icon: Icons.calendar_today,
              label: isRtl ? 'تاريخ الحصاد' : 'Harvest Date',
              value: DateFormat('dd MMM yyyy', isRtl ? 'ar' : 'en')
                  .format(prediction.harvestDate),
              color: Colors.orange,
            ),

            const Divider(height: 32),

            // Revenue estimate
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.green.withOpacity(0.1),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Row(
                children: [
                  const Icon(Icons.attach_money, color: Colors.green, size: 32),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isRtl ? 'تقدير الإيرادات' : 'Revenue Estimate',
                          style: TextStyle(
                            color: Colors.grey.shade600,
                          ),
                        ),
                        Text(
                          '${numberFormat.format(prediction.revenueEstimate)} ${isRtl ? 'ريال' : 'YER'}',
                          style: theme.textTheme.headlineSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                            color: Colors.green,
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildQualityBadge(bool isRtl) {
    final quality = prediction.quality;
    final color = _getQualityColor(quality);

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color),
      ),
      child: Text(
        isRtl ? _getQualityNameAr(quality) : _getQualityName(quality),
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),
    );
  }

  Widget _buildStatRow(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Row(
      children: [
        Icon(icon, color: color, size: 20),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            label,
            style: TextStyle(color: Colors.grey.shade600),
          ),
        ),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
      ],
    );
  }

  Color _getQualityColor(YieldQuality quality) {
    switch (quality) {
      case YieldQuality.excellent:
        return Colors.green;
      case YieldQuality.good:
        return Colors.lightGreen;
      case YieldQuality.average:
        return Colors.amber;
      case YieldQuality.belowAverage:
        return Colors.orange;
      case YieldQuality.poor:
        return Colors.red;
    }
  }

  String _getQualityName(YieldQuality quality) {
    switch (quality) {
      case YieldQuality.excellent:
        return 'Excellent';
      case YieldQuality.good:
        return 'Good';
      case YieldQuality.average:
        return 'Average';
      case YieldQuality.belowAverage:
        return 'Below Avg';
      case YieldQuality.poor:
        return 'Poor';
    }
  }

  String _getQualityNameAr(YieldQuality quality) {
    switch (quality) {
      case YieldQuality.excellent:
        return 'ممتاز';
      case YieldQuality.good:
        return 'جيد';
      case YieldQuality.average:
        return 'متوسط';
      case YieldQuality.belowAverage:
        return 'أقل من المتوسط';
      case YieldQuality.poor:
        return 'ضعيف';
    }
  }
}
