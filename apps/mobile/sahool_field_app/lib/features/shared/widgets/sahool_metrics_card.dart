import 'package:flutter/material.dart';
import '../../../core/theme/sahool_pro_theme.dart';

/// بطاقة المقاييس - Metrics Card
/// تصميم John Deere style لعرض البيانات بسرعة
class SahoolMetricsCard extends StatelessWidget {
  final String label;
  final String value;
  final String? subValue;
  final IconData icon;
  final Color? activeColor;
  final VoidCallback? onTap;

  const SahoolMetricsCard({
    super.key,
    required this.label,
    required this.value,
    this.subValue,
    required this.icon,
    this.activeColor,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final color = activeColor ?? SahoolProColors.johnGreen;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(14),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          border: Border(
            left: BorderSide(color: color, width: 4),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.08),
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
                Icon(icon, size: 20, color: color.withOpacity(0.7)),
                const Spacer(),
                if (subValue != null)
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                    decoration: BoxDecoration(
                      color: color.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Text(
                      subValue!,
                      style: TextStyle(
                        fontSize: 10,
                        color: color,
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),
              ],
            ),
            const SizedBox(height: 10),
            Text(
              value,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.w800,
                color: SahoolProColors.textDark,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                fontSize: 12,
                color: SahoolProColors.textMedium,
                fontWeight: FontWeight.w500,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// بطاقة مقاييس مصغرة - Mini Metrics Card
class SahoolMiniMetricsCard extends StatelessWidget {
  final String label;
  final String value;
  final IconData icon;
  final Color color;

  const SahoolMiniMetricsCard({
    super.key,
    required this.label,
    required this.value,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 16, color: color),
          const SizedBox(width: 6),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                value,
                style: TextStyle(
                  fontSize: 14,
                  fontWeight: FontWeight.bold,
                  color: color,
                ),
              ),
              Text(
                label,
                style: TextStyle(
                  fontSize: 10,
                  color: color.withOpacity(0.8),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

/// بطاقة حالة الحقل - Field Status Card
class SahoolFieldStatusCard extends StatelessWidget {
  final String fieldName;
  final String cropType;
  final double areaHa;
  final double? ndvi;
  final bool isSynced;
  final int pendingTasks;
  final VoidCallback? onTap;
  final VoidCallback? onClose;

  const SahoolFieldStatusCard({
    super.key,
    required this.fieldName,
    required this.cropType,
    required this.areaHa,
    this.ndvi,
    required this.isSynced,
    this.pendingTasks = 0,
    this.onTap,
    this.onClose,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 8,
      shadowColor: Colors.black.withOpacity(0.2),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // Header
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Text(
                              fieldName,
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            const SizedBox(width: 8),
                            _buildSyncBadge(),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          '$cropType • ${areaHa.toStringAsFixed(1)} هكتار',
                          style: TextStyle(
                            color: SahoolProColors.textMedium,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (onClose != null)
                    IconButton(
                      icon: const Icon(Icons.close),
                      onPressed: onClose,
                      color: SahoolProColors.textLight,
                    ),
                ],
              ),

              const Divider(height: 24),

              // Stats Row
              Row(
                children: [
                  if (ndvi != null)
                    Expanded(
                      child: _buildStatItem(
                        icon: Icons.grass,
                        label: 'NDVI',
                        value: ndvi!.toStringAsFixed(2),
                        color: _getNdviColor(ndvi!),
                      ),
                    ),
                  Expanded(
                    child: _buildStatItem(
                      icon: Icons.task_alt,
                      label: 'مهام',
                      value: pendingTasks.toString(),
                      color: pendingTasks > 0
                          ? SahoolProColors.warningOrange
                          : SahoolProColors.statusSynced,
                    ),
                  ),
                  Expanded(
                    child: _buildStatItem(
                      icon: Icons.straighten,
                      label: 'المساحة',
                      value: '${areaHa.toStringAsFixed(1)}ha',
                      color: SahoolProColors.johnGreen,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Action Buttons
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                children: [
                  _buildActionButton(Icons.insights, 'تحليل', SahoolProColors.johnGreen),
                  _buildActionButton(Icons.water_drop, 'ري', Colors.blue),
                  _buildActionButton(Icons.bug_report, 'فحص', SahoolProColors.warningOrange),
                  _buildActionButton(Icons.edit, 'تعديل', SahoolProColors.textMedium),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSyncBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: isSynced
            ? SahoolProColors.statusSynced.withOpacity(0.1)
            : SahoolProColors.statusPending.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isSynced ? Icons.cloud_done : Icons.cloud_upload,
            size: 12,
            color: isSynced
                ? SahoolProColors.statusSynced
                : SahoolProColors.statusPending,
          ),
          const SizedBox(width: 2),
          Text(
            isSynced ? 'متزامن' : 'قيد الرفع',
            style: TextStyle(
              fontSize: 10,
              color: isSynced
                  ? SahoolProColors.statusSynced
                  : SahoolProColors.statusPending,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem({
    required IconData icon,
    required String label,
    required String value,
    required Color color,
  }) {
    return Column(
      children: [
        Icon(icon, color: color, size: 24),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 16,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: SahoolProColors.textLight,
          ),
        ),
      ],
    );
  }

  Widget _buildActionButton(IconData icon, String label, Color color) {
    return Column(
      children: [
        CircleAvatar(
          radius: 22,
          backgroundColor: color.withOpacity(0.1),
          child: Icon(icon, color: color, size: 22),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: SahoolProColors.textMedium,
          ),
        ),
      ],
    );
  }

  Color _getNdviColor(double ndvi) {
    if (ndvi >= 0.7) return SahoolProColors.ndviExcellent;
    if (ndvi >= 0.5) return SahoolProColors.ndviGood;
    if (ndvi >= 0.3) return SahoolProColors.ndviModerate;
    if (ndvi >= 0.2) return SahoolProColors.ndviPoor;
    return SahoolProColors.ndviCritical;
  }
}
