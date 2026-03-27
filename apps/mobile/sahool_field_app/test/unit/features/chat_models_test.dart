import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/features/chat/data/models/message_model.dart';
import 'package:sahool_field_app/features/chat/data/models/conversation_model.dart';

void main() {
  // ═══════════════════════════════════════════════════════════════════════════
  // MessageStatus Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('MessageStatus', () {
    test('has exactly 5 values', () {
      expect(MessageStatus.values.length, 5);
    });

    test('contains all expected values', () {
      expect(MessageStatus.values, contains(MessageStatus.sending));
      expect(MessageStatus.values, contains(MessageStatus.sent));
      expect(MessageStatus.values, contains(MessageStatus.delivered));
      expect(MessageStatus.values, contains(MessageStatus.read));
      expect(MessageStatus.values, contains(MessageStatus.failed));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // MessageType Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('MessageType', () {
    test('has exactly 6 values', () {
      expect(MessageType.values.length, 6);
    });

    test('contains all expected values', () {
      expect(MessageType.values, contains(MessageType.text));
      expect(MessageType.values, contains(MessageType.image));
      expect(MessageType.values, contains(MessageType.file));
      expect(MessageType.values, contains(MessageType.location));
      expect(MessageType.values, contains(MessageType.product));
      expect(MessageType.values, contains(MessageType.order));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ConversationType Enum
  // ═══════════════════════════════════════════════════════════════════════════

  group('ConversationType', () {
    test('has exactly 3 values', () {
      expect(ConversationType.values.length, 3);
    });

    test('contains all expected values', () {
      expect(ConversationType.values, contains(ConversationType.direct));
      expect(ConversationType.values, contains(ConversationType.group));
      expect(ConversationType.values, contains(ConversationType.support));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Message Model
  // ═══════════════════════════════════════════════════════════════════════════

  group('Message', () {
    final baseJson = <String, dynamic>{
      'id': 'msg-001',
      'conversationId': 'conv-001',
      'senderId': 'user-001',
      'senderName': 'Ahmed',
      'senderAvatar': 'https://example.com/avatar.png',
      'type': 'text',
      'content': 'Hello world',
      'attachmentUrl': null,
      'metadata': null,
      'status': 'sent',
      'createdAt': '2026-03-20T10:00:00.000Z',
      'updatedAt': '2026-03-20T10:01:00.000Z',
    };

    test('fromJson creates Message with all fields', () {
      final message = Message.fromJson(baseJson);
      expect(message.id, 'msg-001');
      expect(message.conversationId, 'conv-001');
      expect(message.senderId, 'user-001');
      expect(message.senderName, 'Ahmed');
      expect(message.senderAvatar, 'https://example.com/avatar.png');
      expect(message.type, MessageType.text);
      expect(message.content, 'Hello world');
      expect(message.status, MessageStatus.sent);
      expect(message.isMine, false);
    });

    test('fromJson uses _id as fallback for id', () {
      final json = Map<String, dynamic>.from(baseJson);
      json.remove('id');
      json['_id'] = 'msg-fallback';
      final message = Message.fromJson(json);
      expect(message.id, 'msg-fallback');
    });

    test('fromJson sets isMine true when senderId matches currentUserId', () {
      final message = Message.fromJson(baseJson, currentUserId: 'user-001');
      expect(message.isMine, true);
    });

    test('fromJson sets isMine false when senderId does not match', () {
      final message = Message.fromJson(baseJson, currentUserId: 'user-999');
      expect(message.isMine, false);
    });

    test('fromJson sets isMine false when currentUserId is null', () {
      final message = Message.fromJson(baseJson);
      expect(message.isMine, false);
    });

    test('fromJson defaults content to empty string when null', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['content'] = null;
      final message = Message.fromJson(json);
      expect(message.content, '');
    });

    test('fromJson defaults status to sending when null', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['status'] = null;
      final message = Message.fromJson(json);
      expect(message.status, MessageStatus.sending);
    });

    test('fromJson defaults type to text when null', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['type'] = null;
      final message = Message.fromJson(json);
      expect(message.type, MessageType.text);
    });

    test('fromJson parses all MessageType values', () {
      for (final typeName in ['text', 'image', 'file', 'location', 'product', 'order']) {
        final json = Map<String, dynamic>.from(baseJson);
        json['type'] = typeName;
        final message = Message.fromJson(json);
        expect(message.type, MessageType.values.byName(typeName));
      }
    });

    test('fromJson parses all MessageStatus values', () {
      for (final statusName in ['sending', 'sent', 'delivered', 'read', 'failed']) {
        final json = Map<String, dynamic>.from(baseJson);
        json['status'] = statusName;
        final message = Message.fromJson(json);
        expect(message.status, MessageStatus.values.byName(statusName));
      }
    });

    test('fromJson parses updatedAt when present', () {
      final message = Message.fromJson(baseJson);
      expect(message.updatedAt, isNotNull);
      expect(message.updatedAt, DateTime.parse('2026-03-20T10:01:00.000Z'));
    });

    test('fromJson sets updatedAt to null when absent', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['updatedAt'] = null;
      final message = Message.fromJson(json);
      expect(message.updatedAt, isNull);
    });

    test('fromJson parses metadata map', () {
      final json = Map<String, dynamic>.from(baseJson);
      json['metadata'] = {'productId': 'prod-1', 'price': 500};
      final message = Message.fromJson(json);
      expect(message.metadata, isNotNull);
      expect(message.metadata!['productId'], 'prod-1');
    });

    test('toJson produces correct map', () {
      final message = Message.fromJson(baseJson);
      final json = message.toJson();
      expect(json['id'], 'msg-001');
      expect(json['conversationId'], 'conv-001');
      expect(json['senderId'], 'user-001');
      expect(json['senderName'], 'Ahmed');
      expect(json['type'], 'text');
      expect(json['content'], 'Hello world');
      expect(json['status'], 'sent');
      expect(json['createdAt'], isNotNull);
      expect(json['updatedAt'], isNotNull);
    });

    test('toJson round-trips through fromJson', () {
      final message = Message.fromJson(baseJson);
      final json = message.toJson();
      final restored = Message.fromJson(json);
      expect(restored.id, message.id);
      expect(restored.conversationId, message.conversationId);
      expect(restored.senderId, message.senderId);
      expect(restored.type, message.type);
      expect(restored.content, message.content);
      expect(restored.status, message.status);
    });

    test('statusAr returns correct Arabic for sending', () {
      final message = Message.fromJson(baseJson).copyWith(status: MessageStatus.sending);
      expect(message.statusAr, 'جاري الإرسال');
    });

    test('statusAr returns correct Arabic for sent', () {
      final message = Message.fromJson(baseJson).copyWith(status: MessageStatus.sent);
      expect(message.statusAr, 'تم الإرسال');
    });

    test('statusAr returns correct Arabic for delivered', () {
      final message = Message.fromJson(baseJson).copyWith(status: MessageStatus.delivered);
      expect(message.statusAr, 'تم التسليم');
    });

    test('statusAr returns correct Arabic for read', () {
      final message = Message.fromJson(baseJson).copyWith(status: MessageStatus.read);
      expect(message.statusAr, 'تمت القراءة');
    });

    test('statusAr returns correct Arabic for failed', () {
      final message = Message.fromJson(baseJson).copyWith(status: MessageStatus.failed);
      expect(message.statusAr, 'فشل الإرسال');
    });

    test('copyWith changes specified fields only', () {
      final original = Message.fromJson(baseJson);
      final copied = original.copyWith(content: 'Updated', status: MessageStatus.delivered);
      expect(copied.content, 'Updated');
      expect(copied.status, MessageStatus.delivered);
      expect(copied.id, original.id);
      expect(copied.conversationId, original.conversationId);
      expect(copied.senderId, original.senderId);
    });

    test('copyWith with no arguments returns equivalent message', () {
      final original = Message.fromJson(baseJson);
      final copied = original.copyWith();
      expect(copied.id, original.id);
      expect(copied.content, original.content);
      expect(copied.type, original.type);
    });

    test('copyWith can change isMine', () {
      final message = Message.fromJson(baseJson);
      expect(message.isMine, false);
      final mine = message.copyWith(isMine: true);
      expect(mine.isMine, true);
    });

    test('equality is based on id', () {
      final m1 = Message.fromJson(baseJson);
      final json2 = Map<String, dynamic>.from(baseJson);
      json2['content'] = 'Different content';
      final m2 = Message.fromJson(json2);
      expect(m1, equals(m2));
    });

    test('different ids means not equal', () {
      final m1 = Message.fromJson(baseJson);
      final json2 = Map<String, dynamic>.from(baseJson);
      json2['id'] = 'msg-999';
      final m2 = Message.fromJson(json2);
      expect(m1, isNot(equals(m2)));
    });

    test('hashCode is based on id', () {
      final m1 = Message.fromJson(baseJson);
      final m2 = Message.fromJson(baseJson);
      expect(m1.hashCode, m2.hashCode);
    });

    test('toString contains id and content', () {
      final message = Message.fromJson(baseJson);
      expect(message.toString(), contains('msg-001'));
      expect(message.toString(), contains('Hello world'));
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // ConversationParticipant Model
  // ═══════════════════════════════════════════════════════════════════════════

  group('ConversationParticipant', () {
    final participantJson = <String, dynamic>{
      'userId': 'user-001',
      'name': 'Ahmed Ali',
      'nameAr': 'أحمد علي',
      'avatarUrl': 'https://example.com/avatar.png',
      'role': 'seller',
      'isOnline': true,
      'lastSeen': '2026-03-20T10:00:00.000Z',
    };

    test('fromJson creates participant with all fields', () {
      final p = ConversationParticipant.fromJson(participantJson);
      expect(p.userId, 'user-001');
      expect(p.name, 'Ahmed Ali');
      expect(p.nameAr, 'أحمد علي');
      expect(p.avatarUrl, 'https://example.com/avatar.png');
      expect(p.role, 'seller');
      expect(p.isOnline, true);
      expect(p.lastSeen, isNotNull);
    });

    test('fromJson defaults isOnline to false when null', () {
      final json = Map<String, dynamic>.from(participantJson);
      json['isOnline'] = null;
      final p = ConversationParticipant.fromJson(json);
      expect(p.isOnline, false);
    });

    test('fromJson sets lastSeen to null when absent', () {
      final json = Map<String, dynamic>.from(participantJson);
      json['lastSeen'] = null;
      final p = ConversationParticipant.fromJson(json);
      expect(p.lastSeen, isNull);
    });

    test('toJson produces correct map', () {
      final p = ConversationParticipant.fromJson(participantJson);
      final json = p.toJson();
      expect(json['userId'], 'user-001');
      expect(json['name'], 'Ahmed Ali');
      expect(json['nameAr'], 'أحمد علي');
      expect(json['role'], 'seller');
      expect(json['isOnline'], true);
    });

    test('displayName returns nameAr when available', () {
      final p = ConversationParticipant.fromJson(participantJson);
      expect(p.displayName, 'أحمد علي');
    });

    test('displayName returns name when nameAr is null', () {
      final json = Map<String, dynamic>.from(participantJson);
      json['nameAr'] = null;
      final p = ConversationParticipant.fromJson(json);
      expect(p.displayName, 'Ahmed Ali');
    });

    test('roleAr returns Arabic for seller', () {
      final p = ConversationParticipant.fromJson(participantJson);
      expect(p.roleAr, 'بائع');
    });

    test('roleAr returns Arabic for buyer', () {
      final json = Map<String, dynamic>.from(participantJson);
      json['role'] = 'buyer';
      final p = ConversationParticipant.fromJson(json);
      expect(p.roleAr, 'مشتري');
    });

    test('roleAr returns Arabic for admin', () {
      final json = Map<String, dynamic>.from(participantJson);
      json['role'] = 'admin';
      final p = ConversationParticipant.fromJson(json);
      expect(p.roleAr, 'مسؤول');
    });

    test('roleAr returns original role for unknown role', () {
      final json = Map<String, dynamic>.from(participantJson);
      json['role'] = 'moderator';
      final p = ConversationParticipant.fromJson(json);
      expect(p.roleAr, 'moderator');
    });

    test('roleAr returns null when role is null', () {
      final json = Map<String, dynamic>.from(participantJson);
      json['role'] = null;
      final p = ConversationParticipant.fromJson(json);
      expect(p.roleAr, isNull);
    });

    test('copyWith changes specified fields', () {
      final p = ConversationParticipant.fromJson(participantJson);
      final copied = p.copyWith(name: 'Omar', isOnline: false);
      expect(copied.name, 'Omar');
      expect(copied.isOnline, false);
      expect(copied.userId, p.userId);
    });
  });

  // ═══════════════════════════════════════════════════════════════════════════
  // Conversation Model
  // ═══════════════════════════════════════════════════════════════════════════

  group('Conversation', () {
    final conversationJson = <String, dynamic>{
      'id': 'conv-001',
      'type': 'direct',
      'title': null,
      'participants': [
        {
          'userId': 'user-001',
          'name': 'Ahmed',
          'nameAr': 'أحمد',
          'role': 'buyer',
          'isOnline': true,
        },
        {
          'userId': 'user-002',
          'name': 'Omar',
          'nameAr': 'عمر',
          'role': 'seller',
          'isOnline': false,
        },
      ],
      'lastMessage': {
        'id': 'msg-001',
        'conversationId': 'conv-001',
        'senderId': 'user-001',
        'type': 'text',
        'content': 'Last message content',
        'status': 'read',
        'createdAt': '2026-03-20T10:00:00.000Z',
      },
      'unreadCount': 3,
      'productId': 'prod-001',
      'orderId': null,
      'metadata': null,
      'isTyping': false,
      'isMuted': false,
      'createdAt': '2026-03-19T08:00:00.000Z',
      'updatedAt': '2026-03-20T10:00:00.000Z',
    };

    test('fromJson creates conversation with all fields', () {
      final conv = Conversation.fromJson(conversationJson);
      expect(conv.id, 'conv-001');
      expect(conv.type, ConversationType.direct);
      expect(conv.participants.length, 2);
      expect(conv.lastMessage, isNotNull);
      expect(conv.unreadCount, 3);
      expect(conv.productId, 'prod-001');
    });

    test('fromJson uses _id as fallback', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json.remove('id');
      json['_id'] = 'conv-fallback';
      final conv = Conversation.fromJson(json);
      expect(conv.id, 'conv-fallback');
    });

    test('fromJson parses type group', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['type'] = 'group';
      final conv = Conversation.fromJson(json);
      expect(conv.type, ConversationType.group);
    });

    test('fromJson parses type support', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['type'] = 'support';
      final conv = Conversation.fromJson(json);
      expect(conv.type, ConversationType.support);
    });

    test('fromJson defaults type to direct for unknown values', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['type'] = 'unknown_type';
      final conv = Conversation.fromJson(json);
      expect(conv.type, ConversationType.direct);
    });

    test('fromJson defaults unreadCount to 0 when null', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['unreadCount'] = null;
      final conv = Conversation.fromJson(json);
      expect(conv.unreadCount, 0);
    });

    test('fromJson handles null participants list', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['participants'] = null;
      final conv = Conversation.fromJson(json);
      expect(conv.participants, isEmpty);
    });

    test('fromJson handles null lastMessage', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['lastMessage'] = null;
      final conv = Conversation.fromJson(json);
      expect(conv.lastMessage, isNull);
    });

    test('fromJson passes currentUserId to lastMessage', () {
      final conv = Conversation.fromJson(conversationJson, currentUserId: 'user-001');
      expect(conv.lastMessage!.isMine, true);
    });

    test('toJson produces correct map', () {
      final conv = Conversation.fromJson(conversationJson);
      final json = conv.toJson();
      expect(json['id'], 'conv-001');
      expect(json['type'], 'direct');
      expect(json['participants'], isList);
      expect((json['participants'] as List).length, 2);
      expect(json['unreadCount'], 3);
    });

    test('toJson round-trips through fromJson', () {
      final conv = Conversation.fromJson(conversationJson);
      final json = conv.toJson();
      final restored = Conversation.fromJson(json);
      expect(restored.id, conv.id);
      expect(restored.type, conv.type);
      expect(restored.participants.length, conv.participants.length);
      expect(restored.unreadCount, conv.unreadCount);
    });

    test('hasUnread returns true when unreadCount > 0', () {
      final conv = Conversation.fromJson(conversationJson);
      expect(conv.hasUnread, true);
    });

    test('hasUnread returns false when unreadCount is 0', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['unreadCount'] = 0;
      final conv = Conversation.fromJson(json);
      expect(conv.hasUnread, false);
    });

    test('lastMessagePreview returns text content for text messages', () {
      final conv = Conversation.fromJson(conversationJson);
      expect(conv.lastMessagePreview, 'Last message content');
    });

    test('lastMessagePreview returns empty string when no lastMessage', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['lastMessage'] = null;
      final conv = Conversation.fromJson(json);
      expect(conv.lastMessagePreview, '');
    });

    test('lastMessagePreview returns emoji for image type', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['type'] = 'image';
      final conv = Conversation.fromJson(json);
      expect(conv.lastMessagePreview, contains('صورة'));
    });

    test('lastMessagePreview returns emoji for file type', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['type'] = 'file';
      final conv = Conversation.fromJson(json);
      expect(conv.lastMessagePreview, contains('ملف'));
    });

    test('lastMessagePreview returns emoji for location type', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['type'] = 'location';
      final conv = Conversation.fromJson(json);
      expect(conv.lastMessagePreview, contains('موقع'));
    });

    test('lastMessagePreview returns emoji for product type', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['type'] = 'product';
      final conv = Conversation.fromJson(json);
      expect(conv.lastMessagePreview, contains('منتج'));
    });

    test('lastMessagePreview returns emoji for order type', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['type'] = 'order';
      final conv = Conversation.fromJson(json);
      expect(conv.lastMessagePreview, contains('طلب'));
    });

    test('formattedTime returns empty string when no lastMessage', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['lastMessage'] = null;
      final conv = Conversation.fromJson(json);
      expect(conv.formattedTime, '');
    });

    test('formattedTime returns "الآن" for recent messages', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['createdAt'] =
          DateTime.now().toIso8601String();
      final conv = Conversation.fromJson(json);
      expect(conv.formattedTime, 'الآن');
    });

    test('formattedTime returns minutes for messages within an hour', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['createdAt'] =
          DateTime.now().subtract(const Duration(minutes: 30)).toIso8601String();
      final conv = Conversation.fromJson(json);
      expect(conv.formattedTime, contains('د'));
      expect(conv.formattedTime, contains('منذ'));
    });

    test('formattedTime returns hours for messages within a day', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['createdAt'] =
          DateTime.now().subtract(const Duration(hours: 5)).toIso8601String();
      final conv = Conversation.fromJson(json);
      expect(conv.formattedTime, contains('س'));
      expect(conv.formattedTime, contains('منذ'));
    });

    test('formattedTime returns days for messages within a week', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['createdAt'] =
          DateTime.now().subtract(const Duration(days: 3)).toIso8601String();
      final conv = Conversation.fromJson(json);
      expect(conv.formattedTime, contains('يوم'));
    });

    test('formattedTime returns date for messages older than a week', () {
      final json = Map<String, dynamic>.from(conversationJson);
      (json['lastMessage'] as Map<String, dynamic>)['createdAt'] =
          DateTime.now().subtract(const Duration(days: 14)).toIso8601String();
      final conv = Conversation.fromJson(json);
      expect(conv.formattedTime, contains('/'));
    });

    test('getOtherParticipant returns the other user', () {
      final conv = Conversation.fromJson(conversationJson);
      final other = conv.getOtherParticipant('user-001');
      expect(other, isNotNull);
      expect(other!.userId, 'user-002');
      expect(other.name, 'Omar');
    });

    test('getOtherParticipant returns null when no other participant', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['participants'] = [
        {'userId': 'user-001', 'name': 'Ahmed'},
      ];
      final conv = Conversation.fromJson(json);
      final other = conv.getOtherParticipant('user-001');
      expect(other, isNull);
    });

    test('getOtherParticipant returns null for empty participants', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['participants'] = <dynamic>[];
      final conv = Conversation.fromJson(json);
      expect(conv.getOtherParticipant('user-001'), isNull);
    });

    test('getDisplayName returns title when set', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['title'] = 'Team Chat';
      final conv = Conversation.fromJson(json);
      expect(conv.getDisplayName('user-001'), 'Team Chat');
    });

    test('getDisplayName returns other participant displayName when no title', () {
      final conv = Conversation.fromJson(conversationJson);
      expect(conv.getDisplayName('user-001'), 'عمر');
    });

    test('getDisplayName returns default Arabic text when no title and no other participant', () {
      final json = Map<String, dynamic>.from(conversationJson);
      json['title'] = null;
      json['participants'] = <dynamic>[];
      final conv = Conversation.fromJson(json);
      expect(conv.getDisplayName('user-001'), 'محادثة');
    });

    test('copyWith changes specified fields', () {
      final conv = Conversation.fromJson(conversationJson);
      final copied = conv.copyWith(unreadCount: 0, isMuted: true);
      expect(copied.unreadCount, 0);
      expect(copied.isMuted, true);
      expect(copied.id, conv.id);
    });

    test('copyWith clearLastMessage sets lastMessage to null', () {
      final conv = Conversation.fromJson(conversationJson);
      expect(conv.lastMessage, isNotNull);
      final copied = conv.copyWith(clearLastMessage: true);
      expect(copied.lastMessage, isNull);
    });

    test('copyWith without clearLastMessage preserves lastMessage', () {
      final conv = Conversation.fromJson(conversationJson);
      final copied = conv.copyWith(unreadCount: 5);
      expect(copied.lastMessage, isNotNull);
      expect(copied.lastMessage!.id, conv.lastMessage!.id);
    });

    test('equality is based on id', () {
      final c1 = Conversation.fromJson(conversationJson);
      final json2 = Map<String, dynamic>.from(conversationJson);
      json2['unreadCount'] = 99;
      final c2 = Conversation.fromJson(json2);
      expect(c1, equals(c2));
    });

    test('different ids means not equal', () {
      final c1 = Conversation.fromJson(conversationJson);
      final json2 = Map<String, dynamic>.from(conversationJson);
      json2['id'] = 'conv-999';
      final c2 = Conversation.fromJson(json2);
      expect(c1, isNot(equals(c2)));
    });

    test('hashCode is based on id', () {
      final c1 = Conversation.fromJson(conversationJson);
      final c2 = Conversation.fromJson(conversationJson);
      expect(c1.hashCode, c2.hashCode);
    });

    test('toString contains id', () {
      final conv = Conversation.fromJson(conversationJson);
      expect(conv.toString(), contains('conv-001'));
    });
  });
}
