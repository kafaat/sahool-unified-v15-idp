// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'chat_models.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ChatMessageImpl _$$ChatMessageImplFromJson(Map<String, dynamic> json) =>
    _$ChatMessageImpl(
      id: json['id'] as String,
      roomId: json['roomId'] as String,
      author: json['author'] as String,
      authorType: json['authorType'] as String? ?? 'farmer',
      message: json['message'] as String,
      attachments: (json['attachments'] as List<dynamic>?)
              ?.map((e) => e as String)
              .toList() ??
          const [],
      timestamp: DateTime.parse(json['timestamp'] as String),
      status: json['status'] as String? ?? 'delivered',
    );

Map<String, dynamic> _$$ChatMessageImplToJson(_$ChatMessageImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'roomId': instance.roomId,
      'author': instance.author,
      'authorType': instance.authorType,
      'message': instance.message,
      'attachments': instance.attachments,
      'timestamp': instance.timestamp.toIso8601String(),
      'status': instance.status,
    };

_$ChatRoomImpl _$$ChatRoomImplFromJson(Map<String, dynamic> json) =>
    _$ChatRoomImpl(
      id: json['id'] as String,
      farmerId: json['farmerId'] as String?,
      farmerName: json['farmerName'] as String?,
      expertId: json['expertId'] as String?,
      expertName: json['expertName'] as String?,
      governorate: json['governorate'] as String?,
      topic: json['topic'] as String?,
      diagnosisId: json['diagnosisId'] as String?,
      status: json['status'] as String? ?? 'pending',
      createdAt: DateTime.parse(json['createdAt'] as String),
      acceptedAt: json['acceptedAt'] == null
          ? null
          : DateTime.parse(json['acceptedAt'] as String),
    );

Map<String, dynamic> _$$ChatRoomImplToJson(_$ChatRoomImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'farmerId': instance.farmerId,
      'farmerName': instance.farmerName,
      'expertId': instance.expertId,
      'expertName': instance.expertName,
      'governorate': instance.governorate,
      'topic': instance.topic,
      'diagnosisId': instance.diagnosisId,
      'status': instance.status,
      'createdAt': instance.createdAt.toIso8601String(),
      'acceptedAt': instance.acceptedAt?.toIso8601String(),
    };

_$ChatUserImpl _$$ChatUserImplFromJson(Map<String, dynamic> json) =>
    _$ChatUserImpl(
      id: json['id'] as String,
      name: json['name'] as String,
      nameAr: json['nameAr'] as String?,
      type: json['type'] as String? ?? 'farmer',
      governorate: json['governorate'] as String?,
      isOnline: json['isOnline'] as bool? ?? false,
    );

Map<String, dynamic> _$$ChatUserImplToJson(_$ChatUserImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'nameAr': instance.nameAr,
      'type': instance.type,
      'governorate': instance.governorate,
      'isOnline': instance.isOnline,
    };

_$ExpertRequestImpl _$$ExpertRequestImplFromJson(Map<String, dynamic> json) =>
    _$ExpertRequestImpl(
      roomId: json['roomId'] as String,
      farmerId: json['farmerId'] as String,
      farmerName: json['farmerName'] as String,
      governorate: json['governorate'] as String?,
      topic: json['topic'] as String? ?? 'استشارة زراعية',
      diagnosisId: json['diagnosisId'] as String?,
      status: json['status'] as String? ?? 'pending',
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$$ExpertRequestImplToJson(_$ExpertRequestImpl instance) =>
    <String, dynamic>{
      'roomId': instance.roomId,
      'farmerId': instance.farmerId,
      'farmerName': instance.farmerName,
      'governorate': instance.governorate,
      'topic': instance.topic,
      'diagnosisId': instance.diagnosisId,
      'status': instance.status,
      'createdAt': instance.createdAt.toIso8601String(),
    };

_$ChatStatsImpl _$$ChatStatsImplFromJson(Map<String, dynamic> json) =>
    _$ChatStatsImpl(
      totalConnections: (json['totalConnections'] as num?)?.toInt() ?? 0,
      onlineExperts: (json['onlineExperts'] as num?)?.toInt() ?? 0,
      activeRooms: (json['activeRooms'] as num?)?.toInt() ?? 0,
      totalMessages: (json['totalMessages'] as num?)?.toInt() ?? 0,
    );

Map<String, dynamic> _$$ChatStatsImplToJson(_$ChatStatsImpl instance) =>
    <String, dynamic>{
      'totalConnections': instance.totalConnections,
      'onlineExperts': instance.onlineExperts,
      'activeRooms': instance.activeRooms,
      'totalMessages': instance.totalMessages,
    };
