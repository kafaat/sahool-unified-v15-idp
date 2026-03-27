/// AI Chat Bubble Widget
/// فقاعة محادثة المستشار الذكي
///
/// Displays chat messages from user and AI assistant
library;

import 'package:cached_network_image/cached_network_image.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/config/theme.dart';
import '../../domain/models/advisory.dart';
import '../../data/remote/ai_advisor_api.dart';
import 'advisory_card.dart';

class AiChatBubble extends StatelessWidget {
  final ChatMessage message;
  final bool showAvatar;
  final Function(bool isPositive)? onFeedback;
  final Function(Advisory advisory)? onAdvisoryTap;

  const AiChatBubble({
    super.key,
    required this.message,
    this.showAvatar = true,
    this.onFeedback,
    this.onAdvisoryTap,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // AI Avatar (for assistant messages)
          if (!isUser && showAvatar) _buildAvatar(),
          if (!isUser && showAvatar) const SizedBox(width: 8),
          if (!isUser && !showAvatar) const SizedBox(width: 48),

          // Message content
          Flexible(
            child: Column(
              crossAxisAlignment:
                  isUser ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                // Main message bubble
                _buildMessageBubble(context, isUser),

                // Recommendations cards (if any)
                if (message.recommendations != null &&
                    message.recommendations!.isNotEmpty)
                  ..._buildRecommendations(),

                // Feedback buttons (for AI messages)
                if (!isUser && onFeedback != null)
                  _buildFeedbackButtons(),

                // Timestamp
                _buildTimestamp(isUser),
              ],
            ),
          ),

          if (isUser && showAvatar) const SizedBox(width: 8),
          if (isUser && showAvatar) _buildUserAvatar(),
          if (isUser && !showAvatar) const SizedBox(width: 48),
        ],
      ),
    );
  }

  Widget _buildAvatar() {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: SahoolTheme.primary.withValues(alpha: 0.1),
        shape: BoxShape.circle,
      ),
      child: const Icon(
        Icons.psychology,
        size: 24,
        color: SahoolTheme.primary,
      ),
    );
  }

  Widget _buildUserAvatar() {
    return Container(
      width: 40,
      height: 40,
      decoration: BoxDecoration(
        color: Colors.grey[200],
        shape: BoxShape.circle,
      ),
      child: Icon(
        Icons.person,
        size: 24,
        color: Colors.grey[600],
      ),
    );
  }

  Widget _buildMessageBubble(BuildContext context, bool isUser) {
    final content = message.contentAr ?? message.content;

    return Container(
      constraints: BoxConstraints(
        maxWidth: MediaQuery.of(context).size.width * 0.75,
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isUser ? SahoolTheme.primary : Colors.grey[100],
        borderRadius: BorderRadius.only(
          topLeft: const Radius.circular(16),
          topRight: const Radius.circular(16),
          bottomLeft: isUser ? const Radius.circular(16) : const Radius.circular(4),
          bottomRight: isUser ? const Radius.circular(4) : const Radius.circular(16),
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Message text
          SelectableText(
            content,
            style: TextStyle(
              fontSize: 15,
              color: isUser ? Colors.white : const Color(0xFF1A1A1A),
              height: 1.5,
            ),
          ),

          // Confidence indicator (for AI messages)
          if (!isUser && message.metadata != null &&
              message.metadata!['confidence'] != null)
            _buildConfidenceIndicator(
              (message.metadata!['confidence'] as num).toDouble(),
            ),

          // Sources (for AI messages)
          if (!isUser && message.metadata != null &&
              message.metadata!['sources'] != null &&
              (message.metadata!['sources'] as List).isNotEmpty)
            _buildSources(context, message.metadata!['sources'] as List),
        ],
      ),
    );
  }

  Widget _buildConfidenceIndicator(double confidence) {
    final percentage = (confidence * 100).round();
    Color color;

    if (confidence >= 0.8) {
      color = Colors.green;
    } else if (confidence >= 0.6) {
      color = Colors.orange;
    } else {
      color = Colors.red;
    }

    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.verified, size: 14, color: color),
          const SizedBox(width: 4),
          Text(
            'ثقة $percentage%',
            style: TextStyle(
              fontSize: 11,
              color: color,
            ),
          ),
        ],
      ),
    );
  }

  void _showSourcesDialog(BuildContext context, List sources) {
    showDialog(
      context: context,
      builder: (dialogContext) {
        return AlertDialog(
          title: const Text(
            'مصادر المعلومات | Information Sources',
            style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
          ),
          content: SizedBox(
            width: double.maxFinite,
            child: ListView.builder(
              shrinkWrap: true,
              itemCount: sources.length,
              itemBuilder: (context, index) {
                final source = sources[index].toString();
                final isUrl = source.startsWith('http');
                return ListTile(
                  leading: Icon(
                    isUrl ? Icons.link : Icons.article_outlined,
                    size: 20,
                    color: isUrl ? SahoolTheme.primary : Colors.grey[600],
                  ),
                  title: Text(
                    source,
                    style: TextStyle(
                      fontSize: 13,
                      color: isUrl ? SahoolTheme.primary : const Color(0xFF1A1A1A),
                      decoration: isUrl ? TextDecoration.underline : null,
                    ),
                  ),
                  dense: true,
                  contentPadding: EdgeInsets.zero,
                );
              },
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(dialogContext).pop(),
              child: const Text('إغلاق'),
            ),
          ],
        );
      },
    );
  }

  Widget _buildSources(BuildContext context, List sources) {
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: InkWell(
        onTap: () {
          _showSourcesDialog(context, sources);
        },
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(Icons.link, size: 14, color: Colors.grey[600]),
            const SizedBox(width: 4),
            Text(
              '${sources.length} مصادر',
              style: TextStyle(
                fontSize: 11,
                color: Colors.grey[600],
                decoration: TextDecoration.underline,
              ),
            ),
          ],
        ),
      ),
    );
  }

  List<Widget> _buildRecommendations() {
    return [
      const SizedBox(height: 8),
      ...message.recommendations!.map((advisory) => Padding(
        padding: const EdgeInsets.only(bottom: 8),
        child: AdvisoryCard(
          advisory: advisory,
          compact: true,
          onTap: onAdvisoryTap != null ? () => onAdvisoryTap!(advisory) : null,
        ),
      )),
    ];
  }

  Widget _buildFeedbackButtons() {
    return Padding(
      padding: const EdgeInsets.only(top: 8),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          _buildFeedbackButton(
            icon: Icons.thumb_up_outlined,
            activeIcon: Icons.thumb_up,
            isPositive: true,
            tooltip: 'مفيد',
          ),
          const SizedBox(width: 8),
          _buildFeedbackButton(
            icon: Icons.thumb_down_outlined,
            activeIcon: Icons.thumb_down,
            isPositive: false,
            tooltip: 'غير مفيد',
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackButton({
    required IconData icon,
    required IconData activeIcon,
    required bool isPositive,
    required String tooltip,
  }) {
    return Material(
      color: Colors.transparent,
      child: InkWell(
        onTap: onFeedback != null ? () => onFeedback!(isPositive) : null,
        borderRadius: BorderRadius.circular(20),
        child: Tooltip(
          message: tooltip,
          child: Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: Colors.grey[200],
              borderRadius: BorderRadius.circular(20),
            ),
            child: Icon(
              icon,
              size: 16,
              color: Colors.grey[600],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildTimestamp(bool isUser) {
    return Padding(
      padding: const EdgeInsets.only(top: 4),
      child: Text(
        DateFormat('HH:mm').format(message.timestamp),
        style: TextStyle(
          fontSize: 11,
          color: Colors.grey[500],
        ),
      ),
    );
  }
}

/// System message bubble (for notifications, errors, etc.)
class SystemMessageBubble extends StatelessWidget {
  final String message;
  final IconData? icon;
  final Color? color;

  const SystemMessageBubble({
    super.key,
    required this.message,
    this.icon,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 8),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: (color ?? Colors.grey).withValues(alpha: 0.1),
          borderRadius: BorderRadius.circular(16),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (icon != null) ...[
              Icon(icon, size: 16, color: color ?? Colors.grey[600]),
              const SizedBox(width: 8),
            ],
            Text(
              message,
              style: TextStyle(
                fontSize: 13,
                color: color ?? Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

/// Image message bubble for diagnosis
class ImageMessageBubble extends StatelessWidget {
  final String imagePath;
  final String? caption;
  final DateTime timestamp;
  final bool isUser;

  const ImageMessageBubble({
    super.key,
    required this.imagePath,
    this.caption,
    required this.timestamp,
    required this.isUser,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.65,
            ),
            decoration: BoxDecoration(
              color: isUser ? SahoolTheme.primary : Colors.grey[100],
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                ClipRRect(
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(16),
                  ),
                  child: CachedNetworkImage(
                    imageUrl: imagePath,
                    fit: BoxFit.cover,
                    placeholder: (_, __) => const SizedBox(height: 150, child: Center(child: CircularProgressIndicator(strokeWidth: 2))),
                    errorWidget: (context, _, __) => Container(
                      height: 150,
                      color: Colors.grey[300],
                      child: const Center(
                        child: Icon(Icons.broken_image, size: 40),
                      ),
                    ),
                  ),
                ),
                if (caption != null)
                  Padding(
                    padding: const EdgeInsets.all(12),
                    child: Text(
                      caption!,
                      style: TextStyle(
                        fontSize: 14,
                        color: isUser ? Colors.white : Colors.black87,
                      ),
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
