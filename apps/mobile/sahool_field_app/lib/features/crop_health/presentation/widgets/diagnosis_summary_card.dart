import 'package:flutter/material.dart';
import '../../domain/entities/crop_health_entities.dart';

/// بطاقة ملخص التشخيص
class DiagnosisSummaryCard extends StatelessWidget {
  final DiagnosisSummary summary;

  const DiagnosisSummaryCard({
    super.key,
    required this.summary,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.assessment, color: Color(0xFF367C2B)),
                const SizedBox(width: 8),
                Text(
                  'ملخص حالة الحقل',
                  style: Theme.of(context).textTheme.titleMedium?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const Divider(height: 24),
            Row(
              children: [
                Expanded(
                  child: _buildStatItem(
                    context,
                    icon: Icons.landscape,
                    label: 'إجمالي المناطق',
                    value: summary.zonesTotal.toString(),
                    color: Colors.grey,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    context,
                    icon: Icons.error,
                    label: 'حرجة',
                    value: summary.zonesCritical.toString(),
                    color: Colors.red,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    context,
                    icon: Icons.warning,
                    label: 'تحذير',
                    value: summary.zonesWarning.toString(),
                    color: Colors.orange,
                  ),
                ),
                Expanded(
                  child: _buildStatItem(
                    context,
                    icon: Icons.check_circle,
                    label: 'سليمة',
                    value: summary.zonesOk.toString(),
                    color: Colors.green,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            // شريط التقدم
            ClipRRect(
              borderRadius: BorderRadius.circular(8),
              child: SizedBox(
                height: 12,
                child: Row(
                  children: [
                    if (summary.zonesCritical > 0)
                      Flexible(
                        flex: summary.zonesCritical,
                        child: Container(color: Colors.red),
                      ),
                    if (summary.zonesWarning > 0)
                      Flexible(
                        flex: summary.zonesWarning,
                        child: Container(color: Colors.orange),
                      ),
                    if (summary.zonesOk > 0)
                      Flexible(
                        flex: summary.zonesOk,
                        child: Container(color: Colors.green),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatItem(
    BuildContext context, {
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          child: Icon(icon, color: color, size: 24),
        ),
        const SizedBox(height: 8),
        Text(
          value,
          style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                color: color,
              ),
        ),
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                color: Colors.grey[600],
              ),
        ),
      ],
    );
  }
}
