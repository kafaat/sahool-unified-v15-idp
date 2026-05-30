/// Satellite Overview Tab - تبويب النظرة العامة للأقمار الصناعية
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';

class SatelliteOverviewTab extends StatefulWidget {
  final String fieldId;

  const SatelliteOverviewTab({super.key, required this.fieldId});

  @override
  State<SatelliteOverviewTab> createState() => _SatelliteOverviewTabState();
}

class _SatelliteOverviewTabState extends State<SatelliteOverviewTab> {
  bool _loading = false;

  // Mock data — replace with real API call when available
  final double _ndvi = 0.65;
  final double _evi = 0.52;
  final double _ndwi = 0.31;
  final double _lai = 3.2;
  final String _healthStatus = 'صحي';
  final String _cropType = 'قمح';
  final double _areaha = 8.5;
  final String _lastUpdated = 'منذ 3 ساعات';

  Color _healthColor(String status) {
    switch (status) {
      case 'صحي':
        return Colors.green;
      case 'متوسط':
        return Colors.amber;
      case 'مجهد':
        return Colors.orange;
      case 'حرج':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  IconData _healthIcon(String status) {
    switch (status) {
      case 'صحي':
        return Icons.eco;
      case 'متوسط':
        return Icons.warning_amber;
      case 'مجهد':
        return Icons.energy_savings_leaf;
      case 'حرج':
        return Icons.crisis_alert;
      default:
        return Icons.help_outline;
    }
  }

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
          _buildHealthCard(),
          const SizedBox(height: 16),
          _buildFieldInfoRow(),
          const SizedBox(height: 16),
          _buildQuickStats(),
          const SizedBox(height: 16),
          _buildRecommendationCard(),
        ],
      ),
    );
  }

  Widget _buildHealthCard() {
    final color = _healthColor(_healthStatus);
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: 0.4), width: 1.5),
      ),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: color.withValues(alpha: 0.2),
              shape: BoxShape.circle,
            ),
            child: Icon(_healthIcon(_healthStatus), color: color, size: 36),
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'حالة الحقل',
                  style: TextStyle(fontSize: 13, color: Colors.grey[600]),
                ),
                const SizedBox(height: 4),
                Text(
                  _healthStatus,
                  style: TextStyle(
                    fontSize: 26,
                    fontWeight: FontWeight.bold,
                    color: color,
                  ),
                ),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
            decoration: BoxDecoration(
              color: color,
              borderRadius: BorderRadius.circular(20),
            ),
            child: Text(
              'NDVI $_ndvi',
              style: const TextStyle(
                color: Colors.white,
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFieldInfoRow() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildInfoItem(Icons.crop_square, '${_areaha} هـ', 'المساحة'),
          _buildDivider(),
          _buildInfoItem(Icons.grass, _cropType, 'المحصول'),
          _buildDivider(),
          _buildInfoItem(Icons.update, _lastUpdated, 'آخر تحديث'),
        ],
      ),
    );
  }

  Widget _buildInfoItem(IconData icon, String value, String label) {
    return Column(
      children: [
        Icon(icon, color: SahoolColors.primary, size: 22),
        const SizedBox(height: 4),
        Text(
          value,
          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
        ),
        Text(label, style: TextStyle(fontSize: 11, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildDivider() {
    return Container(height: 40, width: 1, color: Colors.grey[200]);
  }

  Widget _buildQuickStats() {
    final stats = [
      _StatItem('NDVI', _ndvi.toStringAsFixed(2), Colors.green, 'مؤشر النباتات'),
      _StatItem('EVI', _evi.toStringAsFixed(2), Colors.teal, 'مؤشر محسّن'),
      _StatItem('NDWI', _ndwi.toStringAsFixed(2), Colors.blue, 'مؤشر المياه'),
      _StatItem('LAI', _lai.toStringAsFixed(1), Colors.lightGreen, 'مؤشر الورق'),
    ];

    return GridView.count(
      crossAxisCount: 2,
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisSpacing: 12,
      mainAxisSpacing: 12,
      childAspectRatio: 2.0,
      children: stats.map(_buildStatCard).toList(),
    );
  }

  Widget _buildStatCard(_StatItem stat) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 4,
            height: 40,
            decoration: BoxDecoration(
              color: stat.color,
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Text(
                  stat.value,
                  style: TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                    color: stat.color,
                  ),
                ),
                Text(
                  stat.label,
                  style: TextStyle(fontSize: 11, color: Colors.grey[600]),
                  overflow: TextOverflow.ellipsis,
                ),
              ],
            ),
          ),
          Text(
            stat.name,
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: Colors.grey[500],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.blue[50],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.blue[200]!),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(Icons.lightbulb, color: Colors.blue[700], size: 22),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'توصية سريعة',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: Colors.blue[800],
                    fontSize: 14,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  'المحصول في حالة جيدة. يُنصح بمتابعة مستوى الرطوبة خلال الأيام القادمة نظراً للتوقعات الجوية.',
                  style: TextStyle(color: Colors.blue[900], fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _StatItem {
  final String name;
  final String value;
  final Color color;
  final String label;

  const _StatItem(this.name, this.value, this.color, this.label);
}
