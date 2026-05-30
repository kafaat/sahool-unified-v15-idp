/// Satellite Alerts Tab - تبويب التنبيهات
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';

class SatelliteAlertsTab extends StatefulWidget {
  final String fieldId;

  const SatelliteAlertsTab({super.key, required this.fieldId});

  @override
  State<SatelliteAlertsTab> createState() => _SatelliteAlertsTabState();
}

class _SatelliteAlertsTabState extends State<SatelliteAlertsTab> {
  String _filterSeverity = 'الكل';

  final List<_AlertItem> _alerts = [
    const _AlertItem(
      id: '1',
      title: 'نقص في النيتروجين',
      description:
          'تم رصد انخفاض في مستوى النيتروجين في القطاع الجنوبي من الحقل. يُنصح بإضافة 46 كجم/هـ من اليوريا.',
      severity: 'تحذير',
      date: '2026-05-24',
      resolved: false,
    ),
    const _AlertItem(
      id: '2',
      title: 'ضغط مائي في المنطقة الغربية',
      description:
          'مؤشر NDWI يشير إلى جفاف محتمل في الجزء الغربي. ضخ إضافي 25 مم مطلوب.',
      severity: 'حرج',
      date: '2026-05-23',
      resolved: false,
    ),
    const _AlertItem(
      id: '3',
      title: 'توقع تقلبات درجات الحرارة',
      description: 'يُتوقع انخفاض حاد في درجات الحرارة ليلاً قد يؤثر على نمو المحصول.',
      severity: 'استشارة',
      date: '2026-05-22',
      resolved: false,
    ),
  ];

  static const _severities = ['الكل', 'حرج', 'تحذير', 'استشارة'];

  List<_AlertItem> get _filtered {
    if (_filterSeverity == 'الكل') return _alerts.where((a) => !a.resolved).toList();
    return _alerts.where((a) => a.severity == _filterSeverity && !a.resolved).toList();
  }

  Color _severityColor(String severity) {
    switch (severity) {
      case 'حرج':
        return Colors.red;
      case 'تحذير':
        return Colors.orange;
      case 'استشارة':
        return Colors.blue;
      default:
        return Colors.grey;
    }
  }

  IconData _severityIcon(String severity) {
    switch (severity) {
      case 'حرج':
        return Icons.crisis_alert;
      case 'تحذير':
        return Icons.warning_amber;
      case 'استشارة':
        return Icons.info_outline;
      default:
        return Icons.notifications;
    }
  }

  void _resolveAlert(String id) {
    final idx = _alerts.indexWhere((a) => a.id == id);
    if (idx == -1) return;
    setState(() {
      _alerts[idx] = _AlertItem(
        id: _alerts[idx].id,
        title: _alerts[idx].title,
        description: _alerts[idx].description,
        severity: _alerts[idx].severity,
        date: _alerts[idx].date,
        resolved: true,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _filtered;

    return Column(
      children: [
        _buildFilterChips(),
        Expanded(
          child: filtered.isEmpty
              ? _buildEmptyState()
              : ListView.builder(
                  padding: const EdgeInsets.all(12),
                  itemCount: filtered.length,
                  itemBuilder: (_, i) => _buildAlertCard(filtered[i]),
                ),
        ),
      ],
    );
  }

  Widget _buildFilterChips() {
    return Container(
      color: Colors.white,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        child: Row(
          children: _severities.map((sev) {
            final isSelected = _filterSeverity == sev;
            final color = sev == 'الكل' ? SahoolColors.primary : _severityColor(sev);
            return Padding(
              padding: const EdgeInsets.only(left: 8),
              child: FilterChip(
                label: Text(sev),
                selected: isSelected,
                onSelected: (_) => setState(() => _filterSeverity = sev),
                selectedColor: color.withValues(alpha: 0.2),
                labelStyle: TextStyle(
                  color: isSelected ? color : Colors.grey[700],
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  fontSize: 12,
                ),
                side: BorderSide(
                  color: isSelected ? color : Colors.grey[300]!,
                ),
                showCheckmark: false,
              ),
            );
          }).toList(),
        ),
      ),
    );
  }

  Widget _buildAlertCard(_AlertItem alert) {
    final color = _severityColor(alert.severity);

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border(
          right: BorderSide(color: color, width: 4),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.04),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(6),
                  ),
                  child: Icon(_severityIcon(alert.severity), color: color, size: 18),
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        alert.title,
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          fontSize: 14,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 6, vertical: 1),
                            decoration: BoxDecoration(
                              color: color.withValues(alpha: 0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Text(
                              alert.severity,
                              style: TextStyle(
                                fontSize: 10,
                                color: color,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            alert.date,
                            style: TextStyle(fontSize: 11, color: Colors.grey[500]),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              alert.description,
              style: TextStyle(fontSize: 13, color: Colors.grey[700], height: 1.4),
            ),
            const SizedBox(height: 12),
            Align(
              alignment: Alignment.centerLeft,
              child: TextButton.icon(
                onPressed: () => _resolveAlert(alert.id),
                icon: const Icon(Icons.check_circle_outline, size: 16),
                label: const Text('تم الحل', style: TextStyle(fontSize: 12)),
                style: TextButton.styleFrom(
                  foregroundColor: Colors.green,
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                  minimumSize: Size.zero,
                  tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.check_circle_outline, size: 64, color: Colors.green[300]),
          const SizedBox(height: 16),
          const Text(
            'لا توجد تنبيهات نشطة',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
          ),
          const SizedBox(height: 8),
          Text(
            'الحقل في حالة جيدة',
            style: TextStyle(color: Colors.grey[600], fontSize: 13),
          ),
        ],
      ),
    );
  }
}

class _AlertItem {
  final String id;
  final String title;
  final String description;
  final String severity;
  final String date;
  final bool resolved;

  const _AlertItem({
    required this.id,
    required this.title,
    required this.description,
    required this.severity,
    required this.date,
    required this.resolved,
  });
}
