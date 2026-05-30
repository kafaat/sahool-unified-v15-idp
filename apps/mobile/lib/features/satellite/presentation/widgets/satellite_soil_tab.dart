/// Satellite Soil Tab - تبويب التربة
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';

class SatelliteSoilTab extends StatefulWidget {
  final String fieldId;

  const SatelliteSoilTab({super.key, required this.fieldId});

  @override
  State<SatelliteSoilTab> createState() => _SatelliteSoilTabState();
}

class _SatelliteSoilTabState extends State<SatelliteSoilTab> {
  bool _loading = false;

  // Mock soil data (N ppm, P ppm, K ppm, pH, EC dS/m, OC %)
  final List<_SoilMetric> _metrics = const [
    _SoilMetric(
      label: 'نيتروجين',
      abbr: 'N',
      value: 18.0,
      unit: 'ppm',
      minOk: 20.0,
      maxOk: 40.0,
      icon: Icons.science,
      color: Colors.amber,
    ),
    _SoilMetric(
      label: 'فوسفور',
      abbr: 'P',
      value: 25.0,
      unit: 'ppm',
      minOk: 20.0,
      maxOk: 50.0,
      icon: Icons.circle,
      color: Colors.orange,
    ),
    _SoilMetric(
      label: 'بوتاسيوم',
      abbr: 'K',
      value: 150.0,
      unit: 'ppm',
      minOk: 100.0,
      maxOk: 300.0,
      icon: Icons.water_drop,
      color: Colors.purple,
    ),
    _SoilMetric(
      label: 'الرقم الهيدروجيني',
      abbr: 'pH',
      value: 7.2,
      unit: '',
      minOk: 6.0,
      maxOk: 7.5,
      icon: Icons.balance,
      color: Colors.teal,
    ),
    _SoilMetric(
      label: 'الملوحة',
      abbr: 'EC',
      value: 0.8,
      unit: 'dS/m',
      minOk: 0.0,
      maxOk: 2.0,
      icon: Icons.waves,
      color: Colors.blue,
    ),
    _SoilMetric(
      label: 'الكربون العضوي',
      abbr: 'OC',
      value: 1.2,
      unit: '%',
      minOk: 1.5,
      maxOk: 3.0,
      icon: Icons.eco,
      color: Colors.green,
    ),
  ];

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Center(
        child: CircularProgressIndicator(
          valueColor: AlwaysStoppedAnimation<Color>(SahoolColors.primary),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _buildSummaryCard(),
          const SizedBox(height: 16),
          ..._metrics.map(_buildMetricCard),
        ],
      ),
    );
  }

  Widget _buildSummaryCard() {
    final lowCount = _metrics.where((m) => m.value < m.minOk).length;
    final highCount = _metrics.where((m) => m.value > m.maxOk).length;
    final okCount = _metrics.length - lowCount - highCount;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: SahoolColors.primary.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: SahoolColors.primary.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.terrain, color: SahoolColors.primary, size: 24),
              const SizedBox(width: 8),
              const Text(
                'ملخص صحة التربة',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 15,
                  color: SahoolColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildSummaryBadge('$okCount مثالي', Colors.green),
              _buildSummaryBadge('$lowCount منخفض', Colors.orange),
              _buildSummaryBadge('$highCount مرتفع', Colors.red),
            ],
          ),
          if (lowCount > 0) ...[
            const SizedBox(height: 12),
            Text(
              'يُنصح بإضافة أسمدة لتحسين العناصر المنخفضة.',
              style: TextStyle(fontSize: 12, color: Colors.grey[700]),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildSummaryBadge(String text, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Text(
        text,
        style: TextStyle(
          color: color,
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),
    );
  }

  Widget _buildMetricCard(_SoilMetric m) {
    final isLow = m.value < m.minOk;
    final isHigh = m.value > m.maxOk;
    final statusColor = isLow || isHigh ? (isHigh ? Colors.red : Colors.orange) : Colors.green;
    final statusLabel = isLow ? 'منخفض' : isHigh ? 'مرتفع' : 'مثالي';

    // Progress: value relative to range [0, maxOk*1.5]
    final maxDisplay = m.maxOk * 1.5;
    final progress = (m.value / maxDisplay).clamp(0.0, 1.0);

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: m.color.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(m.icon, color: m.color, size: 20),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      m.label,
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 14,
                      ),
                    ),
                    Text(
                      m.abbr,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[500],
                      ),
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text(
                    '${m.value} ${m.unit}',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: m.color,
                    ),
                  ),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: statusColor.withValues(alpha: 0.12),
                      borderRadius: BorderRadius.circular(10),
                    ),
                    child: Text(
                      statusLabel,
                      style: TextStyle(
                        fontSize: 11,
                        color: statusColor,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(4),
            child: LinearProgressIndicator(
              value: progress,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(statusColor),
              minHeight: 6,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            'النطاق المثالي: ${m.minOk} - ${m.maxOk} ${m.unit}',
            style: TextStyle(fontSize: 10, color: Colors.grey[500]),
          ),
        ],
      ),
    );
  }
}

class _SoilMetric {
  final String label;
  final String abbr;
  final double value;
  final String unit;
  final double minOk;
  final double maxOk;
  final IconData icon;
  final Color color;

  const _SoilMetric({
    required this.label,
    required this.abbr,
    required this.value,
    required this.unit,
    required this.minOk,
    required this.maxOk,
    required this.icon,
    required this.color,
  });
}
