/// Message Bubble Widget
/// فقاعة الرسالة
///
/// Displays a chat message with:
/// - Message bubble (green for sent, gray for received)
/// - Sender name and avatar
/// - Message content
/// - Timestamp
/// - Status indicator (sent/delivered/read)

import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../core/config/theme.dart';
import '../data/models/message_model.dart';

class MessageBubble extends StatelessWidget {
  final Message message;
  final bool showAvatar;
  final bool showName;

  const MessageBubble({
    super.key,
    required this.message,
    this.showAvatar = true,
    this.showName = true,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: Row(
        mainAxisAlignment:
            message.isMine ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          // Avatar (for received messages)
          if (!message.isMine && showAvatar) _buildAvatar(),

          if (!message.isMine && showAvatar) const SizedBox(width: 8),

          // Message bubble
          Flexible(
            child: Column(
              crossAxisAlignment: message.isMine
                  ? CrossAxisAlignment.end
                  : CrossAxisAlignment.start,
              children: [
                // Sender name (for received messages)
                if (!message.isMine && showName && message.senderName != null)
                  Padding(
                    padding: const EdgeInsets.only(bottom: 4, right: 12),
                    child: Text(
                      message.senderName!,
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                  ),

                // Message content
                _buildMessageContent(context),

                const SizedBox(height: 2),

                // Timestamp and status
                _buildTimestampAndStatus(context),
              ],
            ),
          ),

          if (message.isMine && showAvatar) const SizedBox(width: 8),

          // Avatar (for sent messages)
          if (message.isMine && showAvatar) _buildAvatar(),
        ],
      ),
    );
  }

  Widget _buildAvatar() {
    return CircleAvatar(
      radius: 16,
      backgroundColor: SahoolTheme.primary.withOpacity(0.1),
      backgroundImage:
          message.senderAvatar != null ? CachedNetworkImageProvider(message.senderAvatar!) : null,
      child: message.senderAvatar == null
          ? Icon(
              Icons.person,
              size: 16,
              color: SahoolTheme.primary,
            )
          : null,
    );
  }

  Widget _buildMessageContent(BuildContext context) {
    switch (message.type) {
      case MessageType.text:
        return _buildTextMessage();

      case MessageType.image:
        return _buildImageMessage();

      case MessageType.file:
        return _buildFileMessage();

      case MessageType.location:
        return _buildLocationMessage();

      case MessageType.product:
        return _buildProductMessage();

      case MessageType.order:
        return _buildOrderMessage();
    }
  }

  Widget _buildTextMessage() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: message.isMine
            ? SahoolTheme.primary
            : Colors.grey[200],
        borderRadius: BorderRadius.only(
          topLeft: const Radius.circular(16),
          topRight: const Radius.circular(16),
          bottomLeft: message.isMine
              ? const Radius.circular(16)
              : const Radius.circular(4),
          bottomRight: message.isMine
              ? const Radius.circular(4)
              : const Radius.circular(16),
        ),
      ),
      child: Text(
        message.content,
        style: TextStyle(
          fontSize: 15,
          color: message.isMine ? Colors.white : const Color(0xFF1A1A1A),
          height: 1.4,
        ),
      ),
    );
  }

  Widget _buildImageMessage() {
    return Column(
      crossAxisAlignment: message.isMine
          ? CrossAxisAlignment.end
          : CrossAxisAlignment.start,
      children: [
        if (message.attachmentUrl != null)
          ClipRRect(
            borderRadius: BorderRadius.circular(12),
            child: CachedNetworkImage(
              imageUrl: message.attachmentUrl!,
              width: 200,
              fit: BoxFit.cover,
              placeholder: (context, url) => Container(
                width: 200,
                height: 150,
                color: Colors.grey[200],
                child: const Center(
                  child: CircularProgressIndicator(
                    strokeWidth: 2,
                  ),
                ),
              ),
              errorWidget: (context, url, error) => Container(
                width: 200,
                height: 150,
                color: Colors.grey[300],
                child: const Icon(Icons.broken_image, size: 40),
              ),
            ),
          ),
        if (message.content.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 4),
            child: _buildTextMessage(),
          ),
      ],
    );
  }

  Widget _buildFileMessage() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: message.isMine
            ? SahoolTheme.primary
            : Colors.grey[200],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.insert_drive_file,
            color: message.isMine ? Colors.white : SahoolTheme.primary,
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              message.content,
              style: TextStyle(
                fontSize: 14,
                color: message.isMine ? Colors.white : const Color(0xFF1A1A1A),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildLocationMessage() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: message.isMine
            ? SahoolTheme.primary
            : Colors.grey[200],
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            Icons.location_on,
            color: message.isMine ? Colors.white : Colors.red,
          ),
          const SizedBox(width: 8),
          Flexible(
            child: Text(
              message.content.isNotEmpty ? message.content : 'موقع',
              style: TextStyle(
                fontSize: 14,
                color: message.isMine ? Colors.white : const Color(0xFF1A1A1A),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildProductMessage() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: message.isMine
            ? SahoolTheme.primary.withOpacity(0.9)
            : Colors.grey[200],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: message.isMine
              ? SahoolTheme.primaryLight
              : SahoolTheme.primary.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.shopping_bag,
                color: message.isMine ? Colors.white : SahoolTheme.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'منتج',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: message.isMine ? Colors.white70 : Colors.grey[600],
                ),
              ),
            ],
          ),
          if (message.content.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              message.content,
              style: TextStyle(
                fontSize: 14,
                color: message.isMine ? Colors.white : const Color(0xFF1A1A1A),
              ),
            ),
          ],
          if (message.metadata != null) ...[
            const SizedBox(height: 4),
            Text(
              message.metadata!['price'] != null
                  ? 'السعر: ${message.metadata!['price']} ريال'
                  : '',
              style: TextStyle(
                fontSize: 12,
                color: message.isMine ? Colors.white70 : Colors.grey[600],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildOrderMessage() {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: message.isMine
            ? SahoolTheme.primary.withOpacity(0.9)
            : Colors.grey[200],
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: message.isMine
              ? SahoolTheme.primaryLight
              : SahoolTheme.primary.withOpacity(0.3),
          width: 1,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.receipt_long,
                color: message.isMine ? Colors.white : SahoolTheme.primary,
                size: 20,
              ),
              const SizedBox(width: 8),
              Text(
                'طلب',
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: message.isMine ? Colors.white70 : Colors.grey[600],
                ),
              ),
            ],
          ),
          if (message.content.isNotEmpty) ...[
            const SizedBox(height: 8),
            Text(
              message.content,
              style: TextStyle(
                fontSize: 14,
                color: message.isMine ? Colors.white : const Color(0xFF1A1A1A),
              ),
            ),
          ],
          if (message.metadata != null) ...[
            const SizedBox(height: 4),
            Text(
              message.metadata!['orderNumber'] != null
                  ? 'رقم الطلب: ${message.metadata!['orderNumber']}'
                  : '',
              style: TextStyle(
                fontSize: 12,
                color: message.isMine ? Colors.white70 : Colors.grey[600],
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildTimestampAndStatus(BuildContext context) {
    final locale = Localizations.localeOf(context).languageCode;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          // Timestamp
          Text(
            DateFormat('HH:mm', locale).format(message.createdAt),
            style: TextStyle(
              fontSize: 11,
              color: Colors.grey[600],
            ),
          ),

          // Status indicator (for sent messages)
          if (message.isMine) ...[
            const SizedBox(width: 4),
            _buildStatusIcon(),
          ],
        ],
      ),
    );
  }

  Widget _buildStatusIcon() {
    IconData icon;
    Color color;

    switch (message.status) {
      case MessageStatus.sending:
        icon = Icons.access_time;
        color = Colors.grey;
        break;
      case MessageStatus.sent:
        icon = Icons.check;
        color = Colors.grey;
        break;
      case MessageStatus.delivered:
        icon = Icons.done_all;
        color = Colors.grey;
        break;
      case MessageStatus.read:
        icon = Icons.done_all;
        color = Colors.blue;
        break;
      case MessageStatus.failed:
        icon = Icons.error_outline;
        color = Colors.red;
        break;
    }

    return Icon(
      icon,
      size: 14,
      color: color,
    );
  }
}
