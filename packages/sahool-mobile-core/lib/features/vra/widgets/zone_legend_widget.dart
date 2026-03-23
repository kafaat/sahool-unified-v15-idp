/// Zone Legend Widget - مفتاح ألوان المناطق
library;

import 'package:flutter/material.dart';

import '../models/vra_models.dart';

/// مفتاح ألوان المناطق
class ZoneLegendWidget extends StatelessWidget {
  final List<ManagementZone> zones;
  final List<ApplicationRate> rates;
  final VRAType vraType;

  const ZoneLegendWidget({
    super.key,
    required this.zones,
    required this.rates,
    required this.vraType,
  });

  Color _getZoneColor(ManagementZone zone, int index) {
    // نفس المنطق الموجود في ZoneMapWidget
    final rate = rates.firstWhere(
      (r) => r.zoneId == zone.zoneId,
      orElse: () => ApplicationRate(
        rateId: '',
        zoneId: zone.zoneId,
        rate: 0,
        unit: '',
      ),
    );

    if (rates.isEmpty) {
      final hue = (index * 360 / zones.length) % 360;
      return HSLColor.fromAHSL(0.6, hue, 0.7, 0.5).toColor();
    }

    // حساب نطاق المعدلات
    final allRates = rates.map((r) => r.rate).toList();
    final minRate = allRates.reduce((a, b) => a < b ? a : b);
    final maxRate = allRates.reduce((a, b) => a > b ? a : b);

    // تطبيع المعدل
    double normalizedRate;
    if (maxRate == minRate) {
      normalizedRate = 0.5;
    } else {
      normalizedRate = (rate.rate - minRate) / (maxRate - minRate);
    }

    // تدرج من الأخضر (منخفض) إلى الأحمر (مرتفع)
    final hue = (1 - normalizedRate) * 120; // 120 = green, 0 = red
    return HSLColor.fromAHSL(0.6, hue, 0.8, 0.5).toColor();
  }

  String _getRateLabel(String locale, bool isRTL) {
    switch (vraType) {
      case VRAType.fertilizer:
        return isRTL ? 'كجم/هكتار' : 'kg/ha';
      case VRAType.seed:
        return isRTL ? 'بذور/هكتار' : 'seeds/ha';
      case VRAType.pesticide:
        return isRTL ? 'لتر/هكتار' : 'L/ha';
      case VRAType.irrigation:
        return isRTL ? 'مم' : 'mm';
    }
  }

  @override
  Widget build(BuildContext context) {
    final locale = Localizations.localeOf(context).languageCode;
    final isRTL = locale == 'ar';

    if (zones.isEmpty) {
      return const SizedBox.shrink();
    }

    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              Icon(Icons.palette, size: 20, color: Colors.grey[700]),
              const SizedBox(width: 8),
              Text(
                isRTL ? 'مفتاح الألوان' : 'Legend',
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ],
          ),
          const Divider(),

          // قائمة المناطق
          ...zones.asMap().entries.map((entry) {
            final index = entry.key;
            final zone = entry.value;
            final rate = rates.firstWhere(
              (r) => r.zoneId == zone.zoneId,
              orElse: () => ApplicationRate(
                rateId: '',
                zoneId: zone.zoneId,
                rate: 0,
                unit: '',
              ),
            );

            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                children: [
                  // مربع اللون
                  Container(
                    width: 24,
                    height: 24,
                    decoration: BoxDecoration(
                      color: _getZoneColor(zone, index),
                      borderRadius: BorderRadius.circular(4),
                      border: Border.all(color: Colors.grey[400]!),
                    ),
                  ),
                  const SizedBox(width: 12),

                  // معلومات المنطقة
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          zone.getDisplayName(locale),
                          style: const TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 13,
                          ),
                        ),
                        if (rates.isNotEmpty)
                          Text(
                            '${rate.rate.toStringAsFixed(2)} ${_getRateLabel(locale, isRTL)}',
                            style: TextStyle(
                              fontSize: 11,
                              color: Colors.grey[600],
                            ),
                          ),
                      ],
                    ),
                  ),

                  // المساحة
                  Text(
                    '${zone.area.toStringAsFixed(1)} ${isRTL ? 'ها' : 'ha'}',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w500,
                    ),
                  ),
                ],
              ),
            );
          }),

          // ملخص
          if (rates.isNotEmpty) ...[
            const Divider(),
            _buildSummaryRow(
              isRTL ? 'المجموع' : 'Total',
              zones.fold<double>(0, (sum, zone) => sum + zone.area).toStringAsFixed(1),
              isRTL ? 'هكتار' : 'ha',
              isRTL,
            ),
            _buildSummaryRow(
              isRTL ? 'متوسط المعدل' : 'Avg Rate',
              _calculateAverageRate().toStringAsFixed(2),
              _getRateLabel(locale, isRTL),
              isRTL,
            ),
            if (_hasRateDifference())
              _buildSummaryRow(
                isRTL ? 'الفرق' : 'Range',
                '${_getMinRate().toStringAsFixed(1)} - ${_getMaxRate().toStringAsFixed(1)}',
                _getRateLabel(locale, isRTL),
                isRTL,
              ),
          ],
        ],
      ),
    );
  }

  Widget _buildSummaryRow(String label, String value, String unit, bool isRTL) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[700],
              fontWeight: FontWeight.w500,
            ),
          ),
          Text(
            '$value $unit',
            style: const TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }

  double _calculateAverageRate() {
    if (rates.isEmpty || zones.isEmpty) return 0;

    double totalQuantity = 0;
    double totalArea = 0;

    for (final zone in zones) {
      final rate = rates.firstWhere(
        (r) => r.zoneId == zone.zoneId,
        orElse: () => ApplicationRate(
          rateId: '',
          zoneId: zone.zoneId,
          rate: 0,
          unit: '',
        ),
      );

      totalQuantity += rate.rate * zone.area;
      totalArea += zone.area;
    }

    return totalArea > 0 ? totalQuantity / totalArea : 0;
  }

  double _getMinRate() {
    if (rates.isEmpty) return 0;
    return rates.map((r) => r.rate).reduce((a, b) => a < b ? a : b);
  }

  double _getMaxRate() {
    if (rates.isEmpty) return 0;
    return rates.map((r) => r.rate).reduce((a, b) => a > b ? a : b);
  }

  bool _hasRateDifference() {
    if (rates.isEmpty) return false;
    return _getMaxRate() - _getMinRate() > 0.01;
  }
}
