/// Message Model
/// نموذج الرسالة
///
/// Represents a chat message in a conversation

/// Message status
enum MessageStatus {
  sending,   // قيد الإرسال
  sent,      // تم الإرسال
  delivered, // تم التسليم
  read,      // تم القراءة
  failed,    // فشل الإرسال
}

/// Message type
enum MessageType {
  text,         // نص
  image,        // صورة
  file,         // ملف
  location,     // موقع
  product,      // منتج (من السوق)
  order,        // طلب (من السوق)
}

/// Message Model
class Message {
  /// Message ID
  final String id;

  /// Conversation ID
  final String conversationId;

  /// Sender user ID
  final String senderId;

  /// Sender name
  final String? senderName;

  /// Sender avatar URL
  final String? senderAvatar;

  /// Message type
  final MessageType type;

  /// Message content (text)
  final String content;

  /// Attachment URL (for images/files)
  final String? attachmentUrl;

  /// Metadata (for product/order links)
  final Map<String, dynamic>? metadata;

  /// Message status
  final MessageStatus status;

  /// Created at timestamp
  final DateTime createdAt;

  /// Updated at timestamp
  final DateTime? updatedAt;

  /// Is message from current user
  final bool isMine;

  const Message({
    required this.id,
    required this.conversationId,
    required this.senderId,
    this.senderName,
    this.senderAvatar,
    required this.type,
    required this.content,
    this.attachmentUrl,
    this.metadata,
    required this.status,
    required this.createdAt,
    this.updatedAt,
    this.isMine = false,
  });

  /// Create from JSON
  factory Message.fromJson(Map<String, dynamic> json, {String? currentUserId}) {
    return Message(
      id: json['id'] as String? ?? json['_id'] as String,
      conversationId: json['conversationId'] as String,
      senderId: json['senderId'] as String,
      senderName: json['senderName'] as String?,
      senderAvatar: json['senderAvatar'] as String?,
      type: _parseMessageType(json['type'] as String?),
      content: json['content'] as String? ?? '',
      attachmentUrl: json['attachmentUrl'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      status: _parseMessageStatus(json['status'] as String?),
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'] as String)
          : DateTime.now(),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'] as String)
          : null,
      isMine: currentUserId != null && json['senderId'] == currentUserId,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'conversationId': conversationId,
        'senderId': senderId,
        'senderName': senderName,
        'senderAvatar': senderAvatar,
        'type': type.name,
        'content': content,
        'attachmentUrl': attachmentUrl,
        'metadata': metadata,
        'status': status.name,
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt?.toIso8601String(),
      };

  /// Copy with
  Message copyWith({
    String? id,
    String? conversationId,
    String? senderId,
    String? senderName,
    String? senderAvatar,
    MessageType? type,
    String? content,
    String? attachmentUrl,
    Map<String, dynamic>? metadata,
    MessageStatus? status,
    DateTime? createdAt,
    DateTime? updatedAt,
    bool? isMine,
  }) {
    return Message(
      id: id ?? this.id,
      conversationId: conversationId ?? this.conversationId,
      senderId: senderId ?? this.senderId,
      senderName: senderName ?? this.senderName,
      senderAvatar: senderAvatar ?? this.senderAvatar,
      type: type ?? this.type,
      content: content ?? this.content,
      attachmentUrl: attachmentUrl ?? this.attachmentUrl,
      metadata: metadata ?? this.metadata,
      status: status ?? this.status,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isMine: isMine ?? this.isMine,
    );
  }

  /// Get status text in Arabic
  String get statusAr {
    switch (status) {
      case MessageStatus.sending:
        return 'جاري الإرسال';
      case MessageStatus.sent:
        return 'تم الإرسال';
      case MessageStatus.delivered:
        return 'تم التسليم';
      case MessageStatus.read:
        return 'تمت القراءة';
      case MessageStatus.failed:
        return 'فشل الإرسال';
    }
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Message && runtimeType == other.runtimeType && id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'Message($id: $content)';
}

// Helper functions

MessageType _parseMessageType(String? type) {
  switch (type?.toLowerCase()) {
    case 'image':
      return MessageType.image;
    case 'file':
      return MessageType.file;
    case 'location':
      return MessageType.location;
    case 'product':
      return MessageType.product;
    case 'order':
      return MessageType.order;
    case 'text':
    default:
      return MessageType.text;
  }
}

MessageStatus _parseMessageStatus(String? status) {
  switch (status?.toLowerCase()) {
    case 'sent':
      return MessageStatus.sent;
    case 'delivered':
      return MessageStatus.delivered;
    case 'read':
      return MessageStatus.read;
    case 'failed':
      return MessageStatus.failed;
    case 'sending':
    default:
      return MessageStatus.sending;
  }
}
