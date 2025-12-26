/// Conversation Model
/// نموذج المحادثة
///
/// Represents a chat conversation between users

import 'message_model.dart';

/// Conversation type
enum ConversationType {
  direct,    // محادثة مباشرة (بين مستخدمين)
  group,     // محادثة جماعية
  support,   // دعم فني
}

/// Participant in conversation
class ConversationParticipant {
  /// User ID
  final String userId;

  /// User name
  final String name;

  /// User name in Arabic
  final String? nameAr;

  /// User avatar URL
  final String? avatarUrl;

  /// User role (buyer/seller)
  final String? role;

  /// Is user online
  final bool isOnline;

  /// Last seen timestamp
  final DateTime? lastSeen;

  const ConversationParticipant({
    required this.userId,
    required this.name,
    this.nameAr,
    this.avatarUrl,
    this.role,
    this.isOnline = false,
    this.lastSeen,
  });

  factory ConversationParticipant.fromJson(Map<String, dynamic> json) {
    return ConversationParticipant(
      userId: json['userId'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String?,
      avatarUrl: json['avatarUrl'] as String?,
      role: json['role'] as String?,
      isOnline: json['isOnline'] as bool? ?? false,
      lastSeen: json['lastSeen'] != null
          ? DateTime.parse(json['lastSeen'] as String)
          : null,
    );
  }

  Map<String, dynamic> toJson() => {
        'userId': userId,
        'name': name,
        'nameAr': nameAr,
        'avatarUrl': avatarUrl,
        'role': role,
        'isOnline': isOnline,
        'lastSeen': lastSeen?.toIso8601String(),
      };

  /// Get display name (Arabic if available)
  String get displayName => nameAr ?? name;

  /// Get role in Arabic
  String? get roleAr {
    if (role == null) return null;
    switch (role?.toLowerCase()) {
      case 'seller':
        return 'بائع';
      case 'buyer':
        return 'مشتري';
      case 'admin':
        return 'مسؤول';
      default:
        return role;
    }
  }

  ConversationParticipant copyWith({
    String? userId,
    String? name,
    String? nameAr,
    String? avatarUrl,
    String? role,
    bool? isOnline,
    DateTime? lastSeen,
  }) {
    return ConversationParticipant(
      userId: userId ?? this.userId,
      name: name ?? this.name,
      nameAr: nameAr ?? this.nameAr,
      avatarUrl: avatarUrl ?? this.avatarUrl,
      role: role ?? this.role,
      isOnline: isOnline ?? this.isOnline,
      lastSeen: lastSeen ?? this.lastSeen,
    );
  }
}

/// Conversation Model
class Conversation {
  /// Conversation ID
  final String id;

  /// Conversation type
  final ConversationType type;

  /// Conversation title (for groups)
  final String? title;

  /// Conversation participants
  final List<ConversationParticipant> participants;

  /// Last message
  final Message? lastMessage;

  /// Unread message count
  final int unreadCount;

  /// Related product ID (if chat is about a product)
  final String? productId;

  /// Related order ID (if chat is about an order)
  final String? orderId;

  /// Metadata
  final Map<String, dynamic>? metadata;

  /// Is user typing (other participant)
  final bool isTyping;

  /// Created at timestamp
  final DateTime createdAt;

  /// Updated at timestamp
  final DateTime updatedAt;

  const Conversation({
    required this.id,
    required this.type,
    this.title,
    required this.participants,
    this.lastMessage,
    this.unreadCount = 0,
    this.productId,
    this.orderId,
    this.metadata,
    this.isTyping = false,
    required this.createdAt,
    required this.updatedAt,
  });

  /// Create from JSON
  factory Conversation.fromJson(Map<String, dynamic> json, {String? currentUserId}) {
    return Conversation(
      id: json['id'] as String? ?? json['_id'] as String,
      type: _parseConversationType(json['type'] as String?),
      title: json['title'] as String?,
      participants: (json['participants'] as List<dynamic>?)
              ?.map((p) => ConversationParticipant.fromJson(p as Map<String, dynamic>))
              .toList() ??
          [],
      lastMessage: json['lastMessage'] != null
          ? Message.fromJson(
              json['lastMessage'] as Map<String, dynamic>,
              currentUserId: currentUserId,
            )
          : null,
      unreadCount: json['unreadCount'] as int? ?? 0,
      productId: json['productId'] as String?,
      orderId: json['orderId'] as String?,
      metadata: json['metadata'] as Map<String, dynamic>?,
      isTyping: json['isTyping'] as bool? ?? false,
      createdAt: json['createdAt'] != null
          ? DateTime.parse(json['createdAt'] as String)
          : DateTime.now(),
      updatedAt: json['updatedAt'] != null
          ? DateTime.parse(json['updatedAt'] as String)
          : DateTime.now(),
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() => {
        'id': id,
        'type': type.name,
        'title': title,
        'participants': participants.map((p) => p.toJson()).toList(),
        'lastMessage': lastMessage?.toJson(),
        'unreadCount': unreadCount,
        'productId': productId,
        'orderId': orderId,
        'metadata': metadata,
        'isTyping': isTyping,
        'createdAt': createdAt.toIso8601String(),
        'updatedAt': updatedAt.toIso8601String(),
      };

  /// Copy with
  Conversation copyWith({
    String? id,
    ConversationType? type,
    String? title,
    List<ConversationParticipant>? participants,
    Message? lastMessage,
    int? unreadCount,
    String? productId,
    String? orderId,
    Map<String, dynamic>? metadata,
    bool? isTyping,
    DateTime? createdAt,
    DateTime? updatedAt,
  }) {
    return Conversation(
      id: id ?? this.id,
      type: type ?? this.type,
      title: title ?? this.title,
      participants: participants ?? this.participants,
      lastMessage: lastMessage ?? this.lastMessage,
      unreadCount: unreadCount ?? this.unreadCount,
      productId: productId ?? this.productId,
      orderId: orderId ?? this.orderId,
      metadata: metadata ?? this.metadata,
      isTyping: isTyping ?? this.isTyping,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  /// Get other participant (for direct conversations)
  ConversationParticipant? getOtherParticipant(String currentUserId) {
    try {
      return participants.firstWhere((p) => p.userId != currentUserId);
    } catch (_) {
      return null;
    }
  }

  /// Get conversation display name
  String getDisplayName(String currentUserId) {
    if (title != null && title!.isNotEmpty) {
      return title!;
    }

    final other = getOtherParticipant(currentUserId);
    if (other != null) {
      return other.displayName;
    }

    return 'محادثة';
  }

  /// Get conversation avatar URL
  String? getAvatarUrl(String currentUserId) {
    final other = getOtherParticipant(currentUserId);
    return other?.avatarUrl;
  }

  /// Check if conversation has unread messages
  bool get hasUnread => unreadCount > 0;

  /// Get last message preview
  String get lastMessagePreview {
    if (lastMessage == null) return '';

    switch (lastMessage!.type) {
      case MessageType.text:
        return lastMessage!.content;
      case MessageType.image:
        return '📷 صورة';
      case MessageType.file:
        return '📎 ملف';
      case MessageType.location:
        return '📍 موقع';
      case MessageType.product:
        return '🛒 منتج';
      case MessageType.order:
        return '📦 طلب';
    }
  }

  /// Get formatted time (relative)
  String get formattedTime {
    if (lastMessage == null) return '';

    final now = DateTime.now();
    final diff = now.difference(lastMessage!.createdAt);

    if (diff.inMinutes < 1) {
      return 'الآن';
    } else if (diff.inMinutes < 60) {
      return 'منذ ${diff.inMinutes} د';
    } else if (diff.inHours < 24) {
      return 'منذ ${diff.inHours} س';
    } else if (diff.inDays < 7) {
      return 'منذ ${diff.inDays} يوم';
    } else {
      return '${lastMessage!.createdAt.day}/${lastMessage!.createdAt.month}';
    }
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is Conversation &&
          runtimeType == other.runtimeType &&
          id == other.id;

  @override
  int get hashCode => id.hashCode;

  @override
  String toString() => 'Conversation($id: $title)';
}

// Helper functions

ConversationType _parseConversationType(String? type) {
  switch (type?.toLowerCase()) {
    case 'group':
      return ConversationType.group;
    case 'support':
      return ConversationType.support;
    case 'direct':
    default:
      return ConversationType.direct;
  }
}
