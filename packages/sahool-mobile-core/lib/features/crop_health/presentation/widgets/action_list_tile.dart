import 'package:flutter/material.dart';
import '../../domain/entities/crop_health_entities.dart';

/// بطاقة الإجراء الموصى به
class ActionListTile extends StatelessWidget {
  final DiagnosisAction action;
  final VoidCallback? onTap;

  const ActionListTile({
    super.key,
    required this.action,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final priorityColor = Color(
      int.parse(action.priorityColor.replaceFirst('#', '0xFF')),
    );

    return Card(
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(
          color: priorityColor.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // أيقونة نوع الإجراء
              Container(
                width: 48,
                height: 48,
                decoration: BoxDecoration(
                  color: priorityColor.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    action.typeIcon,
                    style: const TextStyle(fontSize: 24),
                  ),
                ),
              ),

              const SizedBox(width: 16),

              // المحتوى
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // العنوان
                    Text(
                      action.title,
                      style: Theme.of(context).textTheme.titleSmall?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),

                    const SizedBox(height: 4),

                    // المنطقة
                    Row(
                      children: [
                        Icon(
                          Icons.location_on,
                          size: 14,
                          color: Colors.grey[600],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          action.zoneId,
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                                color: Colors.grey[600],
                              ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 8),

                    // السبب (مختصر)
                    Text(
                      action.reason,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: Theme.of(context).textTheme.bodySmall,
                    ),

                    const SizedBox(height: 8),

                    // شارات
                    Row(
                      children: [
                        // شارة الأولوية
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 4,
                          ),
                          decoration: BoxDecoration(
                            color: priorityColor,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            action.priorityLabel,
                            style: const TextStyle(
                              color: Colors.white,
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),

                        const SizedBox(width: 8),

                        // النافذة الزمنية
                        if (action.recommendedWindowHours != null)
                          Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 4,
                            ),
                            decoration: BoxDecoration(
                              color: Colors.grey[200],
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.schedule, size: 12),
                                const SizedBox(width: 4),
                                Text(
                                  '${action.recommendedWindowHours} ساعة',
                                  style: const TextStyle(fontSize: 12),
                                ),
                              ],
                            ),
                          ),
                      ],
                    ),
                  ],
                ),
              ),

              // سهم
              Icon(
                Icons.chevron_left,
                color: Colors.grey[400],
              ),
            ],
          ),
        ),
      ),
    );
  }
}
