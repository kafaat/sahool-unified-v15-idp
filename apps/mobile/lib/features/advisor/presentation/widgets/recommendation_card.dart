/// Recommendation Card Widget
/// بطاقة التوصية
///
/// Displays an agricultural recommendation with type icon,
/// title, description, priority badge, action button,
/// and expandable details including cost/ROI analysis.
library;

import 'package:flutter/material.dart';
import '../../../../core/theme/sahool_theme.dart';
import '../../../../core/theme/organic_widgets.dart';
import '../providers/advisor_provider.dart';

/// Recommendation card with priority badge, type icon,
/// and expandable details
/// بطاقة التوصية مع شارة الاولوية وايقونة النوع وتفاصيل قابلة للتوسيع
class RecommendationCard extends StatefulWidget {
  final Recommendation recommendation;
  final VoidCallback? onAction;
  final VoidCallback? onComplete;

  const RecommendationCard({
    super.key,
    required this.recommendation,
    this.onAction,
    this.onComplete,
  });

  @override
  State<RecommendationCard> createState() => _RecommendationCardState();
}

class _RecommendationCardState extends State<RecommendationCard> {
  bool _isExpanded = false;

  @override
  Widget build(BuildContext context) {
    final rec = widget.recommendation;
    final priorityColor = _getPriorityColor(rec.priority);
    final isCompleted = rec.isCompleted;

    return Opacity(
      opacity: isCompleted ? 0.6 : 1.0,
      child: OrganicCard(
        padding: EdgeInsets.zero,
        child: Column(
          children: [
            // Priority bar at top
            Container(
              height: 4,
              decoration: BoxDecoration(
                color: priorityColor,
                borderRadius:
                    const BorderRadius.vertical(top: Radius.circular(28)),
              ),
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _buildHeader(rec, priorityColor),
                  const SizedBox(height: 10),
                  _buildDescription(rec),
                  if (_isExpanded) ...[
                    const SizedBox(height: 12),
                    _buildExpandedDetails(rec),
                  ],
                  const SizedBox(height: 12),
                  _buildFooter(rec, priorityColor),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  /// Card header with type icon, title, and priority badge
  /// رأس البطاقة مع ايقونة النوع والعنوان وشارة الاولوية
  Widget _buildHeader(
      Recommendation rec, Color priorityColor) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Type icon
        Container(
          width: 44,
          height: 44,
          decoration: BoxDecoration(
            color: _getTypeColor(rec.type).withOpacity(0.1),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(
            _getTypeIcon(rec.type),
            color: _getTypeColor(rec.type),
            size: 22,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                rec.titleAr,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 15,
                ),
              ),
              const SizedBox(height: 2),
              Text(
                rec.title,
                style: TextStyle(fontSize: 12, color: Colors.grey[600]),
              ),
            ],
          ),
        ),
        _buildPriorityBadge(rec.priority, priorityColor),
      ],
    );
  }

  /// Priority badge with Arabic label
  /// شارة الاولوية مع التسمية العربية
  Widget _buildPriorityBadge(
      RecommendationPriority priority, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        priority.nameAr,
        style: TextStyle(
          fontSize: 10,
          color: color,
          fontWeight: FontWeight.bold,
        ),
      ),
    );
  }

  /// Description text with Arabic priority
  /// نص الوصف مع الاولوية بالعربية
  Widget _buildDescription(Recommendation rec) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          rec.descriptionAr,
          style: TextStyle(
            color: Colors.grey[800],
            height: 1.5,
            fontSize: 13,
          ),
          maxLines: _isExpanded ? null : 2,
          overflow: _isExpanded ? null : TextOverflow.ellipsis,
        ),
        if (!_isExpanded && rec.description.length > 80) ...[
          const SizedBox(height: 4),
          GestureDetector(
            onTap: () => setState(() => _isExpanded = true),
            child: const Text(
              'Show more... | المزيد',
              style: TextStyle(
                color: SahoolColors.forestGreen,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
        if (rec.fieldName != null) ...[
          const SizedBox(height: 6),
          Row(
            children: [
              const Icon(Icons.location_on,
                  size: 14, color: Colors.grey),
              const SizedBox(width: 4),
              Text(
                rec.fieldName!,
                style: TextStyle(fontSize: 11, color: Colors.grey[500]),
              ),
            ],
          ),
        ],
      ],
    );
  }

  /// Expanded details with cost/ROI analysis
  /// التفاصيل الموسعة مع تحليل التكلفة والعائد
  Widget _buildExpandedDetails(Recommendation rec) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: SahoolColors.paleOlive.withOpacity(0.5),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // English description
          Text(
            rec.description,
            style: TextStyle(
              fontSize: 12,
              color: Colors.grey[700],
              height: 1.4,
            ),
          ),

          // Cost / ROI analysis
          if (rec.estimatedCost != null || rec.estimatedROI != null) ...[
            const Divider(height: 16),
            const Text(
              'Economic Analysis | التحليل الاقتصادي',
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                if (rec.estimatedCost != null)
                  Expanded(
                    child: _EconomicItem(
                      icon: Icons.payments,
                      label: 'Cost | التكلفة',
                      value:
                          '${rec.estimatedCost!.toStringAsFixed(0)} SAR',
                      color: SahoolColors.danger,
                    ),
                  ),
                if (rec.estimatedROI != null)
                  Expanded(
                    child: _EconomicItem(
                      icon: Icons.trending_up,
                      label: 'Expected Return | العائد',
                      value:
                          '${rec.estimatedROI!.toStringAsFixed(0)} SAR',
                      color: SahoolColors.success,
                    ),
                  ),
              ],
            ),
            if (rec.roiExplanationAr != null) ...[
              const SizedBox(height: 8),
              Text(
                rec.roiExplanationAr!,
                style: TextStyle(
                  fontSize: 11,
                  color: Colors.grey[600],
                  fontStyle: FontStyle.italic,
                ),
              ),
            ],
          ],

          // Collapse button
          const SizedBox(height: 8),
          GestureDetector(
            onTap: () => setState(() => _isExpanded = false),
            child: const Text(
              'Show less | اقل',
              style: TextStyle(
                color: SahoolColors.forestGreen,
                fontSize: 12,
                fontWeight: FontWeight.w500,
              ),
            ),
          ),
        ],
      ),
    );
  }

  /// Footer with action button and timestamp
  /// تذييل مع زر الاجراء والوقت
  Widget _buildFooter(
      Recommendation rec, Color priorityColor) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        // Timestamp
        Text(
          _formatTimeAgo(rec.createdAt),
          style: TextStyle(fontSize: 11, color: Colors.grey[400]),
        ),

        // Action buttons
        Row(
          children: [
            if (widget.onComplete != null && !rec.isCompleted)
              GestureDetector(
                onTap: widget.onComplete,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 10, vertical: 6),
                  decoration: BoxDecoration(
                    color: Colors.grey[100],
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(Icons.check, size: 16, color: Colors.grey),
                      SizedBox(width: 4),
                      Text(
                        'Done | تم',
                        style: TextStyle(fontSize: 11, color: Colors.grey),
                      ),
                    ],
                  ),
                ),
              ),
            if (rec.actionLabel != null) ...[
              const SizedBox(width: 8),
              GestureDetector(
                onTap: widget.onAction,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                      horizontal: 14, vertical: 6),
                  decoration: BoxDecoration(
                    color: priorityColor,
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    rec.actionLabelAr ?? rec.actionLabel!,
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ],
        ),
      ],
    );
  }

  // ===========================================================================
  // Helpers
  // دوال مساعدة
  // ===========================================================================

  Color _getPriorityColor(RecommendationPriority priority) {
    switch (priority) {
      case RecommendationPriority.critical:
        return SahoolColors.danger;
      case RecommendationPriority.warning:
        return const Color(0xFFFF8F00);
      case RecommendationPriority.advisory:
        return SahoolColors.info;
      case RecommendationPriority.info:
        return SahoolColors.sageGreen;
    }
  }

  IconData _getTypeIcon(RecommendationType type) {
    switch (type) {
      case RecommendationType.irrigation:
        return Icons.water_drop;
      case RecommendationType.fertilizer:
        return Icons.science;
      case RecommendationType.pest:
        return Icons.bug_report;
      case RecommendationType.disease:
        return Icons.healing;
      case RecommendationType.weather:
        return Icons.wb_sunny;
      case RecommendationType.harvest:
        return Icons.agriculture;
      case RecommendationType.general:
        return Icons.lightbulb;
    }
  }

  Color _getTypeColor(RecommendationType type) {
    switch (type) {
      case RecommendationType.irrigation:
        return SahoolColors.info;
      case RecommendationType.fertilizer:
        return SahoolColors.forestGreen;
      case RecommendationType.pest:
        return const Color(0xFFFF8F00);
      case RecommendationType.disease:
        return SahoolColors.danger;
      case RecommendationType.weather:
        return SahoolColors.harvestGold;
      case RecommendationType.harvest:
        return SahoolColors.earthBrown;
      case RecommendationType.general:
        return SahoolColors.sageGreen;
    }
  }

  String _formatTimeAgo(DateTime dateTime) {
    final difference = DateTime.now().difference(dateTime);

    if (difference.inMinutes < 1) {
      return 'Just now | الان';
    } else if (difference.inMinutes < 60) {
      return '${difference.inMinutes} min ago | منذ ${difference.inMinutes} دقيقة';
    } else if (difference.inHours < 24) {
      return '${difference.inHours}h ago | منذ ${difference.inHours} ساعة';
    } else {
      return '${difference.inDays}d ago | منذ ${difference.inDays} يوم';
    }
  }
}

/// Economic metric display item
/// عنصر عرض المقياس الاقتصادي
class _EconomicItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;
  final Color color;

  const _EconomicItem({
    required this.icon,
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 16, color: color),
        const SizedBox(width: 6),
        Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              label,
              style: TextStyle(fontSize: 10, color: Colors.grey[500]),
            ),
            Text(
              value,
              style: TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ],
    );
  }
}
