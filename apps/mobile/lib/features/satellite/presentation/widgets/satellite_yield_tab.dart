/// Satellite Yield Tab - تبويب الإنتاجية
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';

class SatelliteYieldTab extends StatefulWidget {
  final String fieldId;

  const SatelliteYieldTab({super.key, required this.fieldId});

  @override
  State<SatelliteYieldTab> createState() => _SatelliteYieldTabState();
}

class _SatelliteYieldTabState extends State<SatelliteYieldTab> {
  bool _loading = false;

  // Mock yield prediction data
  final double _yieldTonPerHa = 4.5;
  final int _confidencePct = 78;
  final int _daysToHarvest = 45;
  final int _totalGrowthDays = 120;
  final String _harvestDate = '2026-07-10';

  final List<String> _yieldFactors = const [
    'مؤشر NDVI مستقر عند 0.65 يشير إلى غطاء نباتي كثيف ومنتج',
    'ظروف مناخية مواتية خلال مرحلة الإزهار أسهمت في تحسين التلقيح',
    'إدارة الري المثلى خفّضت الضغط المائي وزادت الإنتاجية المتوقعة',
  ];

  int get _elapsedDays => _totalGrowthDays - _daysToHarvest;
  double get _harvestProgress => _elapsedDays / _totalGrowthDays;

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
          _buildYieldCard(),
          const SizedBox(height: 16),
          _buildHarvestCard(),
          const SizedBox(height: 16),
          _buildProgressCard(),
          const SizedBox(height: 16),
          _buildFactorsCard(),
        ],
      ),
    );
  }

  Widget _buildYieldCard() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: SahoolColors.primary.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: SahoolColors.primary.withValues(alpha: 0.2),
        ),
      ),
      child: Column(
        children: [
          const Icon(Icons.agriculture, color: SahoolColors.primary, size: 40),
          const SizedBox(height: 12),
          const Text(
            'الإنتاجية المتوقعة',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey,
              fontWeight: FontWeight.w500,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '$_yieldTonPerHa طن/هـ',
            style: const TextStyle(
              fontSize: 36,
              fontWeight: FontWeight.bold,
              color: SahoolColors.primary,
            ),
          ),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            decoration: BoxDecoration(
              color: Colors.green.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(20),
            ),
            child: Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                const Icon(Icons.verified, color: Colors.green, size: 16),
                const SizedBox(width: 6),
                Text(
                  'مستوى الثقة: $_confidencePct%',
                  style: const TextStyle(
                    color: Colors.green,
                    fontWeight: FontWeight.w600,
                    fontSize: 13,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildHarvestCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
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
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: Colors.amber.withValues(alpha: 0.12),
              borderRadius: BorderRadius.circular(12),
            ),
            child: const Icon(Icons.calendar_today, color: Colors.amber, size: 28),
          ),
          const SizedBox(width: 16),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'الموعد المتوقع للحصاد',
                  style: TextStyle(fontSize: 13, color: Colors.grey),
                ),
                const SizedBox(height: 4),
                Text(
                  _harvestDate,
                  style: const TextStyle(
                    fontSize: 22,
                    fontWeight: FontWeight.bold,
                    color: Colors.amber,
                  ),
                ),
              ],
            ),
          ),
          Column(
            children: [
              Text(
                '$_daysToHarvest',
                style: const TextStyle(
                  fontSize: 30,
                  fontWeight: FontWeight.bold,
                  color: SahoolColors.primary,
                ),
              ),
              const Text(
                'يوم متبقي',
                style: TextStyle(fontSize: 11, color: Colors.grey),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildProgressCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              const Text(
                'تقدم موسم النمو',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
              Text(
                '${(_harvestProgress * 100).toStringAsFixed(0)}%',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  color: SahoolColors.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ClipRRect(
            borderRadius: BorderRadius.circular(6),
            child: LinearProgressIndicator(
              value: _harvestProgress,
              backgroundColor: Colors.grey[200],
              valueColor:
                  const AlwaysStoppedAnimation<Color>(SahoolColors.primary),
              minHeight: 10,
            ),
          ),
          const SizedBox(height: 8),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'مضى: $_elapsedDays يوم',
                style: TextStyle(fontSize: 11, color: Colors.grey[600]),
              ),
              Text(
                'المتبقي: $_daysToHarvest يوم',
                style: TextStyle(fontSize: 11, color: Colors.grey[600]),
              ),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFactorsCard() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(14),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.05),
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
              const Icon(Icons.insights, color: SahoolColors.primary, size: 20),
              const SizedBox(width: 8),
              const Text(
                'العوامل المؤثرة على الإنتاجية',
                style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ..._yieldFactors.asMap().entries.map((e) => Padding(
                padding: const EdgeInsets.only(bottom: 10),
                child: Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Container(
                      width: 22,
                      height: 22,
                      margin: const EdgeInsets.only(top: 1, left: 8),
                      decoration: BoxDecoration(
                        color: SahoolColors.primary.withValues(alpha: 0.12),
                        shape: BoxShape.circle,
                      ),
                      child: Center(
                        child: Text(
                          '${e.key + 1}',
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: SahoolColors.primary,
                          ),
                        ),
                      ),
                    ),
                    Expanded(
                      child: Text(
                        e.value,
                        style: TextStyle(
                          fontSize: 13,
                          color: Colors.grey[700],
                          height: 1.4,
                        ),
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}
