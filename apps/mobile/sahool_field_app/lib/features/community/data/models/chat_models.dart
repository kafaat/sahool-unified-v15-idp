// Sahool Community Chat Models
// نماذج بيانات الدردشة لمجتمع سهول

import 'package:freezed_annotation/freezed_annotation.dart';

part 'chat_models.freezed.dart';
part 'chat_models.g.dart';

/// رسالة في المحادثة
@freezed
class ChatMessage with _$ChatMessage {
  const factory ChatMessage({
    required String id,
    required String roomId,
    required String author,
    @Default('farmer') String authorType,
    required String message,
    @Default([]) List<String> attachments,
    required DateTime timestamp,
    @Default('delivered') String status,
  }) = _ChatMessage;

  factory ChatMessage.fromJson(Map<String, dynamic> json) =>
      _$ChatMessageFromJson(json);
}

/// غرفة محادثة / طلب دعم
@freezed
class ChatRoom with _$ChatRoom {
  const factory ChatRoom({
    required String id,
    String? farmerId,
    String? farmerName,
    String? expertId,
    String? expertName,
    String? governorate,
    String? topic,
    String? diagnosisId,
    @Default('pending') String status,
    required DateTime createdAt,
    DateTime? acceptedAt,
  }) = _ChatRoom;

  factory ChatRoom.fromJson(Map<String, dynamic> json) =>
      _$ChatRoomFromJson(json);
}

/// مستخدم نشط
@freezed
class ChatUser with _$ChatUser {
  const factory ChatUser({
    required String id,
    required String name,
    String? nameAr,
    @Default('farmer') String type,
    String? governorate,
    @Default(false) bool isOnline,
  }) = _ChatUser;

  factory ChatUser.fromJson(Map<String, dynamic> json) =>
      _$ChatUserFromJson(json);
}

/// طلب مساعدة خبير
@freezed
class ExpertRequest with _$ExpertRequest {
  const factory ExpertRequest({
    required String roomId,
    required String farmerId,
    required String farmerName,
    String? governorate,
    @Default('استشارة زراعية') String topic,
    String? diagnosisId,
    @Default('pending') String status,
    required DateTime createdAt,
  }) = _ExpertRequest;

  factory ExpertRequest.fromJson(Map<String, dynamic> json) =>
      _$ExpertRequestFromJson(json);
}

/// إحصائيات الشات
@freezed
class ChatStats with _$ChatStats {
  const factory ChatStats({
    @Default(0) int totalConnections,
    @Default(0) int onlineExperts,
    @Default(0) int activeRooms,
    @Default(0) int totalMessages,
  }) = _ChatStats;

  factory ChatStats.fromJson(Map<String, dynamic> json) =>
      _$ChatStatsFromJson(json);
}
