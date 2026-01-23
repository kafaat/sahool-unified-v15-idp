/// Phenology Timeline Widget - ودجت الجدول الزمني لمراحل النمو
/// Visual timeline for crop growth stages
library;

import 'package:flutter/material.dart';
import '../data/models/phenology_data.dart';

class PhenologyTimeline extends StatelessWidget {
  final List<GrowthStageInfo> stages;
  final GrowthStage currentStage;

  const PhenologyTimeline({
    super.key,
    required this.stages,
    required this.currentStage,
  });

  @override
  Widget build(BuildContext context) {
    final isArabic = Localizations.localeOf(context).languageCode == 'ar';

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            isArabic ? 'الجدول الزمني للنمو' : 'Growth Timeline',
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 20),
          ...stages.asMap().entries.map((entry) {
            final index = entry.key;
            final stage = entry.value;
            final isLast = index == stages.length - 1;

            return _buildTimelineItem(
              stage: stage,
              isLast: isLast,
              isArabic: isArabic,
            );
          }),
        ],
      ),
    );
  }

  Widget _buildTimelineItem({
    required GrowthStageInfo stage,
    required bool isLast,
    required bool isArabic,
  }) {
    final stageColor = Color(int.parse(stage.stage.colorHex.replaceFirst('#', '0xFF')));

    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Timeline indicator
        Column(
          children: [
            Container(
              width: 32,
              height: 32,
              decoration: BoxDecoration(
                color: stage.isCompleted || stage.isCurrent
                    ? stageColor
                    : Colors.grey.withOpacity(0.3),
                shape: BoxShape.circle,
                border: Border.all(
                  color: stage.isCurrent ? stageColor : Colors.transparent,
                  width: 3,
                ),
              ),
              child: Center(
                child: Icon(
                  stage.isCompleted
                      ? Icons.check
                      : stage.isCurrent
                          ? Icons.radio_button_checked
                          : Icons.radio_button_unchecked,
                  color: stage.isCompleted || stage.isCurrent
                      ? Colors.white
                      : Colors.grey,
                  size: 16,
                ),
              ),
            ),
            if (!isLast)
              Container(
                width: 2,
                height: 50,
                color: stage.isCompleted
                    ? stageColor
                    : Colors.grey.withOpacity(0.3),
              ),
          ],
        ),
        const SizedBox(width: 16),
        // Stage info
        Expanded(
          child: Padding(
            padding: EdgeInsets.only(bottom: isLast ? 0 : 16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isArabic ? stage.nameAr : stage.name,
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: stage.isCurrent ? FontWeight.bold : FontWeight.normal,
                    color: stage.isCurrent ? stageColor : Colors.black87,
                  ),
                ),
                const SizedBox(height: 4),
                if (stage.description.isNotEmpty)
                  Text(
                    isArabic ? stage.descriptionAr : stage.description,
                    style: TextStyle(
                      fontSize: 12,
                      color: Colors.grey[600],
                    ),
                  ),
                const SizedBox(height: 4),
                Text(
                  '${isArabic ? 'المدة' : 'Duration'}: ${stage.durationDays} ${isArabic ? 'يوم' : 'days'}',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
                if (stage.isCurrent && stage.tasks.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: stageColor.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(8),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isArabic ? 'المهام:' : 'Tasks:',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: stageColor,
                          ),
                        ),
                        const SizedBox(height: 4),
                        ...((isArabic ? stage.tasksAr : stage.tasks).take(2).map((task) => Padding(
                              padding: const EdgeInsets.only(top: 2),
                              child: Row(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text('• ', style: TextStyle(color: stageColor)),
                                  Expanded(
                                    child: Text(
                                      task,
                                      style: TextStyle(
                                        fontSize: 11,
                                        color: Colors.grey[700],
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ))),
                      ],
                    ),
                  ),
                ],
              ],
            ),
          ),
        ),
      ],
    );
  }
}
