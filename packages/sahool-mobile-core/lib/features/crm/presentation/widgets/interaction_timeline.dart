/// Interaction Timeline Widget
/// عرض الجدول الزمني للتفاعلات
///
/// Displays a timeline of farmer interactions
library;

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../domain/models/interaction.dart';

/// Interaction Timeline Widget
/// ويدجت عرض الجدول الزمني للتفاعلات
class InteractionTimeline extends StatelessWidget {
  final List<Interaction> interactions;
  final Function(Interaction)? onInteractionTap;
  final bool showFarmerName;
  final int? maxItems;

  const InteractionTimeline({
    super.key,
    required this.interactions,
    this.onInteractionTap,
    this.showFarmerName = false,
    this.maxItems,
  });

  @override
  Widget build(BuildContext context) {
    final items = maxItems != null
        ? interactions.take(maxItems!).toList()
        : interactions;

    if (items.isEmpty) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.history,
                size: 48,
                color: Colors.grey[400],
              ),
              const SizedBox(height: 16),
              Text(
                'لا توجد تفاعلات',
                style: TextStyle(
                  color: Colors.grey[600],
                  fontSize: 16,
                ),
              ),
            ],
          ),
        ),
      );
    }

    return ListView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      itemCount: items.length,
      itemBuilder: (context, index) {
        final interaction = items[index];
        final isLast = index == items.length - 1;

        return InteractionTimelineItem(
          interaction: interaction,
          isLast: isLast,
          showFarmerName: showFarmerName,
          onTap: () => onInteractionTap?.call(interaction),
        );
      },
    );
  }
}

/// Interaction Timeline Item
/// عنصر واحد في الجدول الزمني
class InteractionTimelineItem extends StatelessWidget {
  final Interaction interaction;
  final bool isLast;
  final bool showFarmerName;
  final VoidCallback? onTap;

  const InteractionTimelineItem({
    super.key,
    required this.interaction,
    this.isLast = false,
    this.showFarmerName = false,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final dateFormat = DateFormat('d MMM yyyy', 'ar');
    final timeFormat = DateFormat('h:mm a', 'ar');

    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Timeline indicator
            Column(
              children: [
                // Icon circle
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    color: _getTypeColor().withValues(alpha: 0.15),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    _getTypeIcon(),
                    size: 18,
                    color: _getTypeColor(),
                  ),
                ),
                // Connecting line
                if (!isLast)
                  Container(
                    width: 2,
                    height: 60,
                    color: Colors.grey[300],
                  ),
              ],
            ),

            const SizedBox(width: 12),

            // Content
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Header row
                  Row(
                    children: [
                      // Type badge
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: _getTypeColor().withValues(alpha: 0.1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          interaction.typeAr,
                          style: TextStyle(
                            color: _getTypeColor(),
                            fontSize: 11,
                            fontWeight: FontWeight.w600,
                          ),
                        ),
                      ),

                      const Spacer(),

                      // Date
                      Text(
                        dateFormat.format(interaction.interactionAt),
                        style: TextStyle(
                          color: Colors.grey[500],
                          fontSize: 11,
                        ),
                      ),
                    ],
                  ),

                  const SizedBox(height: 6),

                  // Subject
                  Text(
                    interaction.displaySubject,
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w600,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),

                  if (showFarmerName && interaction.farmerName != null) ...[
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(
                          Icons.person_outline,
                          size: 14,
                          color: Colors.grey[500],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          interaction.farmerName!,
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ],

                  if (interaction.description != null &&
                      interaction.description!.isNotEmpty) ...[
                    const SizedBox(height: 4),
                    Text(
                      interaction.displayDescription!,
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12,
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ],

                  const SizedBox(height: 8),

                  // Footer row
                  Row(
                    children: [
                      // Time
                      Icon(
                        Icons.access_time,
                        size: 12,
                        color: Colors.grey[400],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        timeFormat.format(interaction.interactionAt),
                        style: TextStyle(
                          color: Colors.grey[500],
                          fontSize: 11,
                        ),
                      ),

                      // Duration
                      if (interaction.durationMinutes != null) ...[
                        const SizedBox(width: 12),
                        Icon(
                          Icons.timer_outlined,
                          size: 12,
                          color: Colors.grey[400],
                        ),
                        const SizedBox(width: 4),
                        Text(
                          interaction.durationFormatted!,
                          style: TextStyle(
                            color: Colors.grey[500],
                            fontSize: 11,
                          ),
                        ),
                      ],

                      const Spacer(),

                      // Outcome badge
                      _buildOutcomeBadge(),
                    ],
                  ),

                  // Follow-up indicator
                  if (interaction.hasFollowUp) ...[
                    const SizedBox(height: 8),
                    _buildFollowUpIndicator(),
                  ],

                  // Attachments indicator
                  if (interaction.hasAttachments) ...[
                    const SizedBox(height: 8),
                    _buildAttachmentsIndicator(),
                  ],
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildOutcomeBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: _getOutcomeColor().withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(
        interaction.outcomeAr,
        style: TextStyle(
          color: _getOutcomeColor(),
          fontSize: 10,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }

  Widget _buildFollowUpIndicator() {
    final isOverdue = interaction.isFollowUpOverdue;
    final color = isOverdue ? Colors.red : Colors.orange;
    final dateFormat = DateFormat('d MMM', 'ar');

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            isOverdue ? Icons.warning_amber : Icons.event,
            size: 14,
            color: color,
          ),
          const SizedBox(width: 4),
          Text(
            isOverdue ? 'متابعة متأخرة' : 'متابعة',
            style: TextStyle(
              color: color,
              fontSize: 11,
              fontWeight: FontWeight.w600,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            dateFormat.format(interaction.followUpAt!),
            style: TextStyle(
              color: color,
              fontSize: 11,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAttachmentsIndicator() {
    final hasPhotos = interaction.photos.isNotEmpty;
    final hasDocs = interaction.documents.isNotEmpty;
    final hasVoice = interaction.voiceRecordingUrl != null;

    return Wrap(
      spacing: 8,
      runSpacing: 4,
      children: [
        if (hasPhotos)
          _buildAttachmentChip(
            Icons.photo_library_outlined,
            '${interaction.photos.length} صور',
          ),
        if (hasDocs)
          _buildAttachmentChip(
            Icons.attach_file,
            '${interaction.documents.length} مرفقات',
          ),
        if (hasVoice)
          _buildAttachmentChip(
            Icons.mic,
            'تسجيل صوتي',
          ),
      ],
    );
  }

  Widget _buildAttachmentChip(IconData icon, String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(4),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 12, color: Colors.grey[600]),
          const SizedBox(width: 4),
          Text(
            label,
            style: TextStyle(
              color: Colors.grey[600],
              fontSize: 10,
            ),
          ),
        ],
      ),
    );
  }

  IconData _getTypeIcon() {
    switch (interaction.type) {
      case InteractionType.call:
        return Icons.phone;
      case InteractionType.visit:
        return Icons.location_on;
      case InteractionType.whatsapp:
        return Icons.chat;
      case InteractionType.sms:
        return Icons.sms;
      case InteractionType.email:
        return Icons.email;
      case InteractionType.meeting:
        return Icons.groups;
      case InteractionType.note:
        return Icons.note;
      case InteractionType.task:
        return Icons.task_alt;
      case InteractionType.demo:
        return Icons.play_circle;
      case InteractionType.training:
        return Icons.school;
      case InteractionType.complaint:
        return Icons.report_problem;
      case InteractionType.feedback:
        return Icons.feedback;
      case InteractionType.sale:
        return Icons.shopping_cart;
      case InteractionType.followUp:
        return Icons.replay;
    }
  }

  Color _getTypeColor() {
    switch (interaction.type) {
      case InteractionType.call:
        return Colors.blue;
      case InteractionType.visit:
        return Colors.green;
      case InteractionType.whatsapp:
        return const Color(0xFF25D366);
      case InteractionType.sms:
        return Colors.purple;
      case InteractionType.email:
        return Colors.red;
      case InteractionType.meeting:
        return Colors.indigo;
      case InteractionType.note:
        return Colors.grey;
      case InteractionType.task:
        return Colors.teal;
      case InteractionType.demo:
        return Colors.orange;
      case InteractionType.training:
        return Colors.amber;
      case InteractionType.complaint:
        return Colors.red;
      case InteractionType.feedback:
        return Colors.cyan;
      case InteractionType.sale:
        return Colors.green;
      case InteractionType.followUp:
        return Colors.deepPurple;
    }
  }

  Color _getOutcomeColor() {
    switch (interaction.outcome) {
      case InteractionOutcome.successful:
        return Colors.green;
      case InteractionOutcome.noAnswer:
        return Colors.grey;
      case InteractionOutcome.busy:
        return Colors.orange;
      case InteractionOutcome.rescheduled:
        return Colors.blue;
      case InteractionOutcome.notInterested:
        return Colors.red;
      case InteractionOutcome.interested:
        return Colors.teal;
      case InteractionOutcome.converted:
        return Colors.green;
      case InteractionOutcome.pending:
        return Colors.amber;
      case InteractionOutcome.cancelled:
        return Colors.grey;
    }
  }
}
