/// Context Indicator Widget
/// مؤشر السياق
///
/// Shows what context data the AI advisor has access to
library;

import 'package:flutter/material.dart';
import '../../../../core/config/theme.dart';
import '../../domain/models/advisory_context.dart';

class ContextIndicator extends StatelessWidget {
  final AdvisoryContext context;
  final String? fieldName;
  final VoidCallback? onTap;

  const ContextIndicator({
    super.key,
    required this.context,
    this.fieldName,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final availableTypes = this.context.availableContextTypes;
    final completeness = this.context.completeness;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
        decoration: BoxDecoration(
          color: SahoolTheme.primary.withValues(alpha: 0.05),
          border: Border(
            bottom: BorderSide(
              color: SahoolTheme.primary.withValues(alpha: 0.1),
            ),
          ),
        ),
        child: Row(
          children: [
            // AI icon
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: SahoolTheme.primary.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(
                Icons.psychology,
                size: 18,
                color: SahoolTheme.primary,
              ),
            ),
            const SizedBox(width: 12),

            // Context info
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    fieldName != null
                        ? 'سياق الحقل: $fieldName'
                        : 'السياق المتاح',
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 4),
                  // Context type icons
                  Row(
                    children: [
                      ...availableTypes.map((type) => _buildTypeIcon(type)),
                      const Spacer(),
                      _buildCompletenessIndicator(completeness),
                    ],
                  ),
                ],
              ),
            ),

            // Arrow icon
            if (onTap != null)
              Icon(
                Icons.chevron_left,
                color: Colors.grey[400],
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildTypeIcon(ContextType type) {
    IconData icon;
    Color color;
    String tooltip;

    switch (type) {
      case ContextType.field:
        icon = Icons.grass;
        color = Colors.green;
        tooltip = 'الحقل';
        break;
      case ContextType.weather:
        icon = Icons.cloud;
        color = Colors.blue;
        tooltip = 'الطقس';
        break;
      case ContextType.crop:
        icon = Icons.eco;
        color = Colors.teal;
        tooltip = 'المحصول';
        break;
      case ContextType.soil:
        icon = Icons.landscape;
        color = Colors.brown;
        tooltip = 'التربة';
        break;
      case ContextType.history:
        icon = Icons.history;
        color = Colors.purple;
        tooltip = 'السجل';
        break;
    }

    return Tooltip(
      message: tooltip,
      child: Container(
        margin: const EdgeInsets.only(left: 8),
        padding: const EdgeInsets.all(4),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Icon(icon, size: 14, color: color),
      ),
    );
  }

  Widget _buildCompletenessIndicator(double completeness) {
    final percentage = (completeness * 100).round();
    Color color;

    if (completeness >= 0.8) {
      color = Colors.green;
    } else if (completeness >= 0.5) {
      color = Colors.orange;
    } else {
      color = Colors.grey;
    }

    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: 40,
          height: 4,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(2),
            child: LinearProgressIndicator(
              value: completeness,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
        ),
        const SizedBox(width: 4),
        Text(
          '$percentage%',
          style: TextStyle(
            fontSize: 10,
            color: color,
            fontWeight: FontWeight.w600,
          ),
        ),
      ],
    );
  }
}

/// Detailed context card for showing in bottom sheet or dialog
class ContextDetailCard extends StatelessWidget {
  final AdvisoryContext context;

  const ContextDetailCard({
    super.key,
    required this.context,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Field context
        if (this.context.hasFieldData)
          _buildContextSection(
            icon: Icons.grass,
            iconColor: Colors.green,
            title: 'الحقل',
            children: [
              _buildInfoRow('الاسم', this.context.field!.nameAr ?? this.context.field!.name),
              if (this.context.field!.areaHectares != null)
                _buildInfoRow('المساحة', '${this.context.field!.areaHectares} هكتار'),
              if (this.context.field!.ndvi != null)
                _buildInfoRow('NDVI', '${(this.context.field!.ndvi! * 100).round()}%'),
              if (this.context.field!.healthStatusAr != null)
                _buildInfoRow('الحالة', this.context.field!.healthStatusAr!),
            ],
          ),

        // Weather context
        if (this.context.hasWeatherData)
          _buildContextSection(
            icon: Icons.cloud,
            iconColor: Colors.blue,
            title: 'الطقس',
            children: [
              _buildInfoRow('الحرارة', this.context.weather!.temperatureSummaryAr),
              if (this.context.weather!.humidity != null)
                _buildInfoRow('الرطوبة', '${this.context.weather!.humidity}%'),
              if (this.context.weather!.conditionAr != null)
                _buildInfoRow('الحالة', this.context.weather!.conditionAr!),
              if (this.context.weather!.isRainExpected)
                _buildInfoRow('المطر', 'متوقع'),
            ],
          ),

        // Crop context
        if (this.context.hasCropData)
          _buildContextSection(
            icon: Icons.eco,
            iconColor: Colors.teal,
            title: 'المحصول',
            children: [
              _buildInfoRow('النوع', this.context.crop!.typeAr),
              if (this.context.crop!.varietyAr != null)
                _buildInfoRow('الصنف', this.context.crop!.varietyAr!),
              if (this.context.crop!.growthStageAr != null)
                _buildInfoRow('المرحلة', this.context.crop!.growthStageAr!),
              if (this.context.crop!.daysUntilHarvest != null)
                _buildInfoRow('للحصاد', '${this.context.crop!.daysUntilHarvest} يوم'),
            ],
          ),

        // Soil context
        if (this.context.hasSoilData)
          _buildContextSection(
            icon: Icons.landscape,
            iconColor: Colors.brown,
            title: 'التربة',
            children: [
              _buildInfoRow('الرطوبة', this.context.soil!.moistureStatusAr),
              if (this.context.soil!.ph != null)
                _buildInfoRow('pH', '${this.context.soil!.ph!.toStringAsFixed(1)} (${this.context.soil!.phStatusAr})'),
              if (this.context.soil!.soilTypeAr != null)
                _buildInfoRow('النوع', this.context.soil!.soilTypeAr!),
            ],
          ),

        // No data message
        if (this.context.availableContextTypes.isEmpty)
          Center(
            child: Padding(
              padding: const EdgeInsets.all(32),
              child: Column(
                children: [
                  Icon(Icons.info_outline, size: 48, color: Colors.grey[400]),
                  const SizedBox(height: 16),
                  Text(
                    'لا توجد بيانات سياق متاحة',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'اختر حقلاً للحصول على توصيات مخصصة',
                    style: TextStyle(fontSize: 12),
                  ),
                ],
              ),
            ),
          ),
      ],
    );
  }

  Widget _buildContextSection({
    required IconData icon,
    required Color iconColor,
    required String title,
    required List<Widget> children,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: iconColor.withValues(alpha: 0.05),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: iconColor.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: iconColor.withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Icon(icon, size: 20, color: iconColor),
              ),
              const SizedBox(width: 12),
              Text(
                title,
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: iconColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          ...children,
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(
            label,
            style: TextStyle(
              fontSize: 13,
              color: Colors.grey[700],
            ),
          ),
          Text(
            value,
            style: const TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }
}

/// Compact context badge for use in headers
class ContextBadge extends StatelessWidget {
  final AdvisoryContext? context;
  final VoidCallback? onTap;

  const ContextBadge({
    super.key,
    this.context,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    if (this.context == null) {
      return const SizedBox.shrink();
    }

    final count = this.context!.availableContextTypes.length;

    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
        decoration: BoxDecoration(
          color: SahoolTheme.primary.withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(
              Icons.dataset,
              size: 14,
              color: SahoolTheme.primary,
            ),
            const SizedBox(width: 4),
            Text(
              '$count',
              style: const TextStyle(
                fontSize: 12,
                fontWeight: FontWeight.bold,
                color: SahoolTheme.primary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
