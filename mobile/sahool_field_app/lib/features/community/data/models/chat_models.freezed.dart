// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'chat_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

ChatMessage _$ChatMessageFromJson(Map<String, dynamic> json) {
  return _ChatMessage.fromJson(json);
}

/// @nodoc
mixin _$ChatMessage {
  String get id => throw _privateConstructorUsedError;
  String get roomId => throw _privateConstructorUsedError;
  String get author => throw _privateConstructorUsedError;
  String get authorType => throw _privateConstructorUsedError;
  String get message => throw _privateConstructorUsedError;
  List<String> get attachments => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $ChatMessageCopyWith<ChatMessage> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChatMessageCopyWith<$Res> {
  factory $ChatMessageCopyWith(
          ChatMessage value, $Res Function(ChatMessage) then) =
      _$ChatMessageCopyWithImpl<$Res, ChatMessage>;
  @useResult
  $Res call(
      {String id,
      String roomId,
      String author,
      String authorType,
      String message,
      List<String> attachments,
      DateTime timestamp,
      String status});
}

/// @nodoc
class _$ChatMessageCopyWithImpl<$Res, $Val extends ChatMessage>
    implements $ChatMessageCopyWith<$Res> {
  _$ChatMessageCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? roomId = null,
    Object? author = null,
    Object? authorType = null,
    Object? message = null,
    Object? attachments = null,
    Object? timestamp = null,
    Object? status = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      roomId: null == roomId
          ? _value.roomId
          : roomId // ignore: cast_nullable_to_non_nullable
              as String,
      author: null == author
          ? _value.author
          : author // ignore: cast_nullable_to_non_nullable
              as String,
      authorType: null == authorType
          ? _value.authorType
          : authorType // ignore: cast_nullable_to_non_nullable
              as String,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      attachments: null == attachments
          ? _value.attachments
          : attachments // ignore: cast_nullable_to_non_nullable
              as List<String>,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChatMessageImplCopyWith<$Res>
    implements $ChatMessageCopyWith<$Res> {
  factory _$$ChatMessageImplCopyWith(
          _$ChatMessageImpl value, $Res Function(_$ChatMessageImpl) then) =
      __$$ChatMessageImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String roomId,
      String author,
      String authorType,
      String message,
      List<String> attachments,
      DateTime timestamp,
      String status});
}

/// @nodoc
class __$$ChatMessageImplCopyWithImpl<$Res>
    extends _$ChatMessageCopyWithImpl<$Res, _$ChatMessageImpl>
    implements _$$ChatMessageImplCopyWith<$Res> {
  __$$ChatMessageImplCopyWithImpl(
      _$ChatMessageImpl _value, $Res Function(_$ChatMessageImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? roomId = null,
    Object? author = null,
    Object? authorType = null,
    Object? message = null,
    Object? attachments = null,
    Object? timestamp = null,
    Object? status = null,
  }) {
    return _then(_$ChatMessageImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      roomId: null == roomId
          ? _value.roomId
          : roomId // ignore: cast_nullable_to_non_nullable
              as String,
      author: null == author
          ? _value.author
          : author // ignore: cast_nullable_to_non_nullable
              as String,
      authorType: null == authorType
          ? _value.authorType
          : authorType // ignore: cast_nullable_to_non_nullable
              as String,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      attachments: null == attachments
          ? _value._attachments
          : attachments // ignore: cast_nullable_to_non_nullable
              as List<String>,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChatMessageImpl implements _ChatMessage {
  const _$ChatMessageImpl(
      {required this.id,
      required this.roomId,
      required this.author,
      this.authorType = 'farmer',
      required this.message,
      final List<String> attachments = const [],
      required this.timestamp,
      this.status = 'delivered'})
      : _attachments = attachments;

  factory _$ChatMessageImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChatMessageImplFromJson(json);

  @override
  final String id;
  @override
  final String roomId;
  @override
  final String author;
  @override
  @JsonKey()
  final String authorType;
  @override
  final String message;
  final List<String> _attachments;
  @override
  @JsonKey()
  List<String> get attachments {
    if (_attachments is EqualUnmodifiableListView) return _attachments;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_attachments);
  }

  @override
  final DateTime timestamp;
  @override
  @JsonKey()
  final String status;

  @override
  String toString() {
    return 'ChatMessage(id: $id, roomId: $roomId, author: $author, authorType: $authorType, message: $message, attachments: $attachments, timestamp: $timestamp, status: $status)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChatMessageImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.roomId, roomId) || other.roomId == roomId) &&
            (identical(other.author, author) || other.author == author) &&
            (identical(other.authorType, authorType) ||
                other.authorType == authorType) &&
            (identical(other.message, message) || other.message == message) &&
            const DeepCollectionEquality()
                .equals(other._attachments, _attachments) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.status, status) || other.status == status));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      roomId,
      author,
      authorType,
      message,
      const DeepCollectionEquality().hash(_attachments),
      timestamp,
      status);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$ChatMessageImplCopyWith<_$ChatMessageImpl> get copyWith =>
      __$$ChatMessageImplCopyWithImpl<_$ChatMessageImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChatMessageImplToJson(
      this,
    );
  }
}

abstract class _ChatMessage implements ChatMessage {
  const factory _ChatMessage(
      {required final String id,
      required final String roomId,
      required final String author,
      final String authorType,
      required final String message,
      final List<String> attachments,
      required final DateTime timestamp,
      final String status}) = _$ChatMessageImpl;

  factory _ChatMessage.fromJson(Map<String, dynamic> json) =
      _$ChatMessageImpl.fromJson;

  @override
  String get id;
  @override
  String get roomId;
  @override
  String get author;
  @override
  String get authorType;
  @override
  String get message;
  @override
  List<String> get attachments;
  @override
  DateTime get timestamp;
  @override
  String get status;
  @override
  @JsonKey(ignore: true)
  _$$ChatMessageImplCopyWith<_$ChatMessageImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ChatRoom _$ChatRoomFromJson(Map<String, dynamic> json) {
  return _ChatRoom.fromJson(json);
}

/// @nodoc
mixin _$ChatRoom {
  String get id => throw _privateConstructorUsedError;
  String? get farmerId => throw _privateConstructorUsedError;
  String? get farmerName => throw _privateConstructorUsedError;
  String? get expertId => throw _privateConstructorUsedError;
  String? get expertName => throw _privateConstructorUsedError;
  String? get governorate => throw _privateConstructorUsedError;
  String? get topic => throw _privateConstructorUsedError;
  String? get diagnosisId => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;
  DateTime? get acceptedAt => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $ChatRoomCopyWith<ChatRoom> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChatRoomCopyWith<$Res> {
  factory $ChatRoomCopyWith(ChatRoom value, $Res Function(ChatRoom) then) =
      _$ChatRoomCopyWithImpl<$Res, ChatRoom>;
  @useResult
  $Res call(
      {String id,
      String? farmerId,
      String? farmerName,
      String? expertId,
      String? expertName,
      String? governorate,
      String? topic,
      String? diagnosisId,
      String status,
      DateTime createdAt,
      DateTime? acceptedAt});
}

/// @nodoc
class _$ChatRoomCopyWithImpl<$Res, $Val extends ChatRoom>
    implements $ChatRoomCopyWith<$Res> {
  _$ChatRoomCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? farmerId = freezed,
    Object? farmerName = freezed,
    Object? expertId = freezed,
    Object? expertName = freezed,
    Object? governorate = freezed,
    Object? topic = freezed,
    Object? diagnosisId = freezed,
    Object? status = null,
    Object? createdAt = null,
    Object? acceptedAt = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      farmerId: freezed == farmerId
          ? _value.farmerId
          : farmerId // ignore: cast_nullable_to_non_nullable
              as String?,
      farmerName: freezed == farmerName
          ? _value.farmerName
          : farmerName // ignore: cast_nullable_to_non_nullable
              as String?,
      expertId: freezed == expertId
          ? _value.expertId
          : expertId // ignore: cast_nullable_to_non_nullable
              as String?,
      expertName: freezed == expertName
          ? _value.expertName
          : expertName // ignore: cast_nullable_to_non_nullable
              as String?,
      governorate: freezed == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String?,
      topic: freezed == topic
          ? _value.topic
          : topic // ignore: cast_nullable_to_non_nullable
              as String?,
      diagnosisId: freezed == diagnosisId
          ? _value.diagnosisId
          : diagnosisId // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      acceptedAt: freezed == acceptedAt
          ? _value.acceptedAt
          : acceptedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChatRoomImplCopyWith<$Res>
    implements $ChatRoomCopyWith<$Res> {
  factory _$$ChatRoomImplCopyWith(
          _$ChatRoomImpl value, $Res Function(_$ChatRoomImpl) then) =
      __$$ChatRoomImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String? farmerId,
      String? farmerName,
      String? expertId,
      String? expertName,
      String? governorate,
      String? topic,
      String? diagnosisId,
      String status,
      DateTime createdAt,
      DateTime? acceptedAt});
}

/// @nodoc
class __$$ChatRoomImplCopyWithImpl<$Res>
    extends _$ChatRoomCopyWithImpl<$Res, _$ChatRoomImpl>
    implements _$$ChatRoomImplCopyWith<$Res> {
  __$$ChatRoomImplCopyWithImpl(
      _$ChatRoomImpl _value, $Res Function(_$ChatRoomImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? farmerId = freezed,
    Object? farmerName = freezed,
    Object? expertId = freezed,
    Object? expertName = freezed,
    Object? governorate = freezed,
    Object? topic = freezed,
    Object? diagnosisId = freezed,
    Object? status = null,
    Object? createdAt = null,
    Object? acceptedAt = freezed,
  }) {
    return _then(_$ChatRoomImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      farmerId: freezed == farmerId
          ? _value.farmerId
          : farmerId // ignore: cast_nullable_to_non_nullable
              as String?,
      farmerName: freezed == farmerName
          ? _value.farmerName
          : farmerName // ignore: cast_nullable_to_non_nullable
              as String?,
      expertId: freezed == expertId
          ? _value.expertId
          : expertId // ignore: cast_nullable_to_non_nullable
              as String?,
      expertName: freezed == expertName
          ? _value.expertName
          : expertName // ignore: cast_nullable_to_non_nullable
              as String?,
      governorate: freezed == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String?,
      topic: freezed == topic
          ? _value.topic
          : topic // ignore: cast_nullable_to_non_nullable
              as String?,
      diagnosisId: freezed == diagnosisId
          ? _value.diagnosisId
          : diagnosisId // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      acceptedAt: freezed == acceptedAt
          ? _value.acceptedAt
          : acceptedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChatRoomImpl implements _ChatRoom {
  const _$ChatRoomImpl(
      {required this.id,
      this.farmerId,
      this.farmerName,
      this.expertId,
      this.expertName,
      this.governorate,
      this.topic,
      this.diagnosisId,
      this.status = 'pending',
      required this.createdAt,
      this.acceptedAt});

  factory _$ChatRoomImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChatRoomImplFromJson(json);

  @override
  final String id;
  @override
  final String? farmerId;
  @override
  final String? farmerName;
  @override
  final String? expertId;
  @override
  final String? expertName;
  @override
  final String? governorate;
  @override
  final String? topic;
  @override
  final String? diagnosisId;
  @override
  @JsonKey()
  final String status;
  @override
  final DateTime createdAt;
  @override
  final DateTime? acceptedAt;

  @override
  String toString() {
    return 'ChatRoom(id: $id, farmerId: $farmerId, farmerName: $farmerName, expertId: $expertId, expertName: $expertName, governorate: $governorate, topic: $topic, diagnosisId: $diagnosisId, status: $status, createdAt: $createdAt, acceptedAt: $acceptedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChatRoomImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.farmerId, farmerId) ||
                other.farmerId == farmerId) &&
            (identical(other.farmerName, farmerName) ||
                other.farmerName == farmerName) &&
            (identical(other.expertId, expertId) ||
                other.expertId == expertId) &&
            (identical(other.expertName, expertName) ||
                other.expertName == expertName) &&
            (identical(other.governorate, governorate) ||
                other.governorate == governorate) &&
            (identical(other.topic, topic) || other.topic == topic) &&
            (identical(other.diagnosisId, diagnosisId) ||
                other.diagnosisId == diagnosisId) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.acceptedAt, acceptedAt) ||
                other.acceptedAt == acceptedAt));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      farmerId,
      farmerName,
      expertId,
      expertName,
      governorate,
      topic,
      diagnosisId,
      status,
      createdAt,
      acceptedAt);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$ChatRoomImplCopyWith<_$ChatRoomImpl> get copyWith =>
      __$$ChatRoomImplCopyWithImpl<_$ChatRoomImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChatRoomImplToJson(
      this,
    );
  }
}

abstract class _ChatRoom implements ChatRoom {
  const factory _ChatRoom(
      {required final String id,
      final String? farmerId,
      final String? farmerName,
      final String? expertId,
      final String? expertName,
      final String? governorate,
      final String? topic,
      final String? diagnosisId,
      final String status,
      required final DateTime createdAt,
      final DateTime? acceptedAt}) = _$ChatRoomImpl;

  factory _ChatRoom.fromJson(Map<String, dynamic> json) =
      _$ChatRoomImpl.fromJson;

  @override
  String get id;
  @override
  String? get farmerId;
  @override
  String? get farmerName;
  @override
  String? get expertId;
  @override
  String? get expertName;
  @override
  String? get governorate;
  @override
  String? get topic;
  @override
  String? get diagnosisId;
  @override
  String get status;
  @override
  DateTime get createdAt;
  @override
  DateTime? get acceptedAt;
  @override
  @JsonKey(ignore: true)
  _$$ChatRoomImplCopyWith<_$ChatRoomImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ChatUser _$ChatUserFromJson(Map<String, dynamic> json) {
  return _ChatUser.fromJson(json);
}

/// @nodoc
mixin _$ChatUser {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String? get nameAr => throw _privateConstructorUsedError;
  String get type => throw _privateConstructorUsedError;
  String? get governorate => throw _privateConstructorUsedError;
  bool get isOnline => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $ChatUserCopyWith<ChatUser> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChatUserCopyWith<$Res> {
  factory $ChatUserCopyWith(ChatUser value, $Res Function(ChatUser) then) =
      _$ChatUserCopyWithImpl<$Res, ChatUser>;
  @useResult
  $Res call(
      {String id,
      String name,
      String? nameAr,
      String type,
      String? governorate,
      bool isOnline});
}

/// @nodoc
class _$ChatUserCopyWithImpl<$Res, $Val extends ChatUser>
    implements $ChatUserCopyWith<$Res> {
  _$ChatUserCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? nameAr = freezed,
    Object? type = null,
    Object? governorate = freezed,
    Object? isOnline = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: freezed == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String?,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      governorate: freezed == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String?,
      isOnline: null == isOnline
          ? _value.isOnline
          : isOnline // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChatUserImplCopyWith<$Res>
    implements $ChatUserCopyWith<$Res> {
  factory _$$ChatUserImplCopyWith(
          _$ChatUserImpl value, $Res Function(_$ChatUserImpl) then) =
      __$$ChatUserImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String? nameAr,
      String type,
      String? governorate,
      bool isOnline});
}

/// @nodoc
class __$$ChatUserImplCopyWithImpl<$Res>
    extends _$ChatUserCopyWithImpl<$Res, _$ChatUserImpl>
    implements _$$ChatUserImplCopyWith<$Res> {
  __$$ChatUserImplCopyWithImpl(
      _$ChatUserImpl _value, $Res Function(_$ChatUserImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? nameAr = freezed,
    Object? type = null,
    Object? governorate = freezed,
    Object? isOnline = null,
  }) {
    return _then(_$ChatUserImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: freezed == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String?,
      type: null == type
          ? _value.type
          : type // ignore: cast_nullable_to_non_nullable
              as String,
      governorate: freezed == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String?,
      isOnline: null == isOnline
          ? _value.isOnline
          : isOnline // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChatUserImpl implements _ChatUser {
  const _$ChatUserImpl(
      {required this.id,
      required this.name,
      this.nameAr,
      this.type = 'farmer',
      this.governorate,
      this.isOnline = false});

  factory _$ChatUserImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChatUserImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String? nameAr;
  @override
  @JsonKey()
  final String type;
  @override
  final String? governorate;
  @override
  @JsonKey()
  final bool isOnline;

  @override
  String toString() {
    return 'ChatUser(id: $id, name: $name, nameAr: $nameAr, type: $type, governorate: $governorate, isOnline: $isOnline)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChatUserImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.type, type) || other.type == type) &&
            (identical(other.governorate, governorate) ||
                other.governorate == governorate) &&
            (identical(other.isOnline, isOnline) ||
                other.isOnline == isOnline));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode =>
      Object.hash(runtimeType, id, name, nameAr, type, governorate, isOnline);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$ChatUserImplCopyWith<_$ChatUserImpl> get copyWith =>
      __$$ChatUserImplCopyWithImpl<_$ChatUserImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChatUserImplToJson(
      this,
    );
  }
}

abstract class _ChatUser implements ChatUser {
  const factory _ChatUser(
      {required final String id,
      required final String name,
      final String? nameAr,
      final String type,
      final String? governorate,
      final bool isOnline}) = _$ChatUserImpl;

  factory _ChatUser.fromJson(Map<String, dynamic> json) =
      _$ChatUserImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String? get nameAr;
  @override
  String get type;
  @override
  String? get governorate;
  @override
  bool get isOnline;
  @override
  @JsonKey(ignore: true)
  _$$ChatUserImplCopyWith<_$ChatUserImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ExpertRequest _$ExpertRequestFromJson(Map<String, dynamic> json) {
  return _ExpertRequest.fromJson(json);
}

/// @nodoc
mixin _$ExpertRequest {
  String get roomId => throw _privateConstructorUsedError;
  String get farmerId => throw _privateConstructorUsedError;
  String get farmerName => throw _privateConstructorUsedError;
  String? get governorate => throw _privateConstructorUsedError;
  String get topic => throw _privateConstructorUsedError;
  String? get diagnosisId => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  DateTime get createdAt => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $ExpertRequestCopyWith<ExpertRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ExpertRequestCopyWith<$Res> {
  factory $ExpertRequestCopyWith(
          ExpertRequest value, $Res Function(ExpertRequest) then) =
      _$ExpertRequestCopyWithImpl<$Res, ExpertRequest>;
  @useResult
  $Res call(
      {String roomId,
      String farmerId,
      String farmerName,
      String? governorate,
      String topic,
      String? diagnosisId,
      String status,
      DateTime createdAt});
}

/// @nodoc
class _$ExpertRequestCopyWithImpl<$Res, $Val extends ExpertRequest>
    implements $ExpertRequestCopyWith<$Res> {
  _$ExpertRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? roomId = null,
    Object? farmerId = null,
    Object? farmerName = null,
    Object? governorate = freezed,
    Object? topic = null,
    Object? diagnosisId = freezed,
    Object? status = null,
    Object? createdAt = null,
  }) {
    return _then(_value.copyWith(
      roomId: null == roomId
          ? _value.roomId
          : roomId // ignore: cast_nullable_to_non_nullable
              as String,
      farmerId: null == farmerId
          ? _value.farmerId
          : farmerId // ignore: cast_nullable_to_non_nullable
              as String,
      farmerName: null == farmerName
          ? _value.farmerName
          : farmerName // ignore: cast_nullable_to_non_nullable
              as String,
      governorate: freezed == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String?,
      topic: null == topic
          ? _value.topic
          : topic // ignore: cast_nullable_to_non_nullable
              as String,
      diagnosisId: freezed == diagnosisId
          ? _value.diagnosisId
          : diagnosisId // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ExpertRequestImplCopyWith<$Res>
    implements $ExpertRequestCopyWith<$Res> {
  factory _$$ExpertRequestImplCopyWith(
          _$ExpertRequestImpl value, $Res Function(_$ExpertRequestImpl) then) =
      __$$ExpertRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String roomId,
      String farmerId,
      String farmerName,
      String? governorate,
      String topic,
      String? diagnosisId,
      String status,
      DateTime createdAt});
}

/// @nodoc
class __$$ExpertRequestImplCopyWithImpl<$Res>
    extends _$ExpertRequestCopyWithImpl<$Res, _$ExpertRequestImpl>
    implements _$$ExpertRequestImplCopyWith<$Res> {
  __$$ExpertRequestImplCopyWithImpl(
      _$ExpertRequestImpl _value, $Res Function(_$ExpertRequestImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? roomId = null,
    Object? farmerId = null,
    Object? farmerName = null,
    Object? governorate = freezed,
    Object? topic = null,
    Object? diagnosisId = freezed,
    Object? status = null,
    Object? createdAt = null,
  }) {
    return _then(_$ExpertRequestImpl(
      roomId: null == roomId
          ? _value.roomId
          : roomId // ignore: cast_nullable_to_non_nullable
              as String,
      farmerId: null == farmerId
          ? _value.farmerId
          : farmerId // ignore: cast_nullable_to_non_nullable
              as String,
      farmerName: null == farmerName
          ? _value.farmerName
          : farmerName // ignore: cast_nullable_to_non_nullable
              as String,
      governorate: freezed == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String?,
      topic: null == topic
          ? _value.topic
          : topic // ignore: cast_nullable_to_non_nullable
              as String,
      diagnosisId: freezed == diagnosisId
          ? _value.diagnosisId
          : diagnosisId // ignore: cast_nullable_to_non_nullable
              as String?,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      createdAt: null == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ExpertRequestImpl implements _ExpertRequest {
  const _$ExpertRequestImpl(
      {required this.roomId,
      required this.farmerId,
      required this.farmerName,
      this.governorate,
      this.topic = 'استشارة زراعية',
      this.diagnosisId,
      this.status = 'pending',
      required this.createdAt});

  factory _$ExpertRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$ExpertRequestImplFromJson(json);

  @override
  final String roomId;
  @override
  final String farmerId;
  @override
  final String farmerName;
  @override
  final String? governorate;
  @override
  @JsonKey()
  final String topic;
  @override
  final String? diagnosisId;
  @override
  @JsonKey()
  final String status;
  @override
  final DateTime createdAt;

  @override
  String toString() {
    return 'ExpertRequest(roomId: $roomId, farmerId: $farmerId, farmerName: $farmerName, governorate: $governorate, topic: $topic, diagnosisId: $diagnosisId, status: $status, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ExpertRequestImpl &&
            (identical(other.roomId, roomId) || other.roomId == roomId) &&
            (identical(other.farmerId, farmerId) ||
                other.farmerId == farmerId) &&
            (identical(other.farmerName, farmerName) ||
                other.farmerName == farmerName) &&
            (identical(other.governorate, governorate) ||
                other.governorate == governorate) &&
            (identical(other.topic, topic) || other.topic == topic) &&
            (identical(other.diagnosisId, diagnosisId) ||
                other.diagnosisId == diagnosisId) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(runtimeType, roomId, farmerId, farmerName,
      governorate, topic, diagnosisId, status, createdAt);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$ExpertRequestImplCopyWith<_$ExpertRequestImpl> get copyWith =>
      __$$ExpertRequestImplCopyWithImpl<_$ExpertRequestImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ExpertRequestImplToJson(
      this,
    );
  }
}

abstract class _ExpertRequest implements ExpertRequest {
  const factory _ExpertRequest(
      {required final String roomId,
      required final String farmerId,
      required final String farmerName,
      final String? governorate,
      final String topic,
      final String? diagnosisId,
      final String status,
      required final DateTime createdAt}) = _$ExpertRequestImpl;

  factory _ExpertRequest.fromJson(Map<String, dynamic> json) =
      _$ExpertRequestImpl.fromJson;

  @override
  String get roomId;
  @override
  String get farmerId;
  @override
  String get farmerName;
  @override
  String? get governorate;
  @override
  String get topic;
  @override
  String? get diagnosisId;
  @override
  String get status;
  @override
  DateTime get createdAt;
  @override
  @JsonKey(ignore: true)
  _$$ExpertRequestImplCopyWith<_$ExpertRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ChatStats _$ChatStatsFromJson(Map<String, dynamic> json) {
  return _ChatStats.fromJson(json);
}

/// @nodoc
mixin _$ChatStats {
  int get totalConnections => throw _privateConstructorUsedError;
  int get onlineExperts => throw _privateConstructorUsedError;
  int get activeRooms => throw _privateConstructorUsedError;
  int get totalMessages => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $ChatStatsCopyWith<ChatStats> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ChatStatsCopyWith<$Res> {
  factory $ChatStatsCopyWith(ChatStats value, $Res Function(ChatStats) then) =
      _$ChatStatsCopyWithImpl<$Res, ChatStats>;
  @useResult
  $Res call(
      {int totalConnections,
      int onlineExperts,
      int activeRooms,
      int totalMessages});
}

/// @nodoc
class _$ChatStatsCopyWithImpl<$Res, $Val extends ChatStats>
    implements $ChatStatsCopyWith<$Res> {
  _$ChatStatsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalConnections = null,
    Object? onlineExperts = null,
    Object? activeRooms = null,
    Object? totalMessages = null,
  }) {
    return _then(_value.copyWith(
      totalConnections: null == totalConnections
          ? _value.totalConnections
          : totalConnections // ignore: cast_nullable_to_non_nullable
              as int,
      onlineExperts: null == onlineExperts
          ? _value.onlineExperts
          : onlineExperts // ignore: cast_nullable_to_non_nullable
              as int,
      activeRooms: null == activeRooms
          ? _value.activeRooms
          : activeRooms // ignore: cast_nullable_to_non_nullable
              as int,
      totalMessages: null == totalMessages
          ? _value.totalMessages
          : totalMessages // ignore: cast_nullable_to_non_nullable
              as int,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ChatStatsImplCopyWith<$Res>
    implements $ChatStatsCopyWith<$Res> {
  factory _$$ChatStatsImplCopyWith(
          _$ChatStatsImpl value, $Res Function(_$ChatStatsImpl) then) =
      __$$ChatStatsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int totalConnections,
      int onlineExperts,
      int activeRooms,
      int totalMessages});
}

/// @nodoc
class __$$ChatStatsImplCopyWithImpl<$Res>
    extends _$ChatStatsCopyWithImpl<$Res, _$ChatStatsImpl>
    implements _$$ChatStatsImplCopyWith<$Res> {
  __$$ChatStatsImplCopyWithImpl(
      _$ChatStatsImpl _value, $Res Function(_$ChatStatsImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalConnections = null,
    Object? onlineExperts = null,
    Object? activeRooms = null,
    Object? totalMessages = null,
  }) {
    return _then(_$ChatStatsImpl(
      totalConnections: null == totalConnections
          ? _value.totalConnections
          : totalConnections // ignore: cast_nullable_to_non_nullable
              as int,
      onlineExperts: null == onlineExperts
          ? _value.onlineExperts
          : onlineExperts // ignore: cast_nullable_to_non_nullable
              as int,
      activeRooms: null == activeRooms
          ? _value.activeRooms
          : activeRooms // ignore: cast_nullable_to_non_nullable
              as int,
      totalMessages: null == totalMessages
          ? _value.totalMessages
          : totalMessages // ignore: cast_nullable_to_non_nullable
              as int,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ChatStatsImpl implements _ChatStats {
  const _$ChatStatsImpl(
      {this.totalConnections = 0,
      this.onlineExperts = 0,
      this.activeRooms = 0,
      this.totalMessages = 0});

  factory _$ChatStatsImpl.fromJson(Map<String, dynamic> json) =>
      _$$ChatStatsImplFromJson(json);

  @override
  @JsonKey()
  final int totalConnections;
  @override
  @JsonKey()
  final int onlineExperts;
  @override
  @JsonKey()
  final int activeRooms;
  @override
  @JsonKey()
  final int totalMessages;

  @override
  String toString() {
    return 'ChatStats(totalConnections: $totalConnections, onlineExperts: $onlineExperts, activeRooms: $activeRooms, totalMessages: $totalMessages)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ChatStatsImpl &&
            (identical(other.totalConnections, totalConnections) ||
                other.totalConnections == totalConnections) &&
            (identical(other.onlineExperts, onlineExperts) ||
                other.onlineExperts == onlineExperts) &&
            (identical(other.activeRooms, activeRooms) ||
                other.activeRooms == activeRooms) &&
            (identical(other.totalMessages, totalMessages) ||
                other.totalMessages == totalMessages));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType, totalConnections, onlineExperts, activeRooms, totalMessages);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$ChatStatsImplCopyWith<_$ChatStatsImpl> get copyWith =>
      __$$ChatStatsImplCopyWithImpl<_$ChatStatsImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ChatStatsImplToJson(
      this,
    );
  }
}

abstract class _ChatStats implements ChatStats {
  const factory _ChatStats(
      {final int totalConnections,
      final int onlineExperts,
      final int activeRooms,
      final int totalMessages}) = _$ChatStatsImpl;

  factory _ChatStats.fromJson(Map<String, dynamic> json) =
      _$ChatStatsImpl.fromJson;

  @override
  int get totalConnections;
  @override
  int get onlineExperts;
  @override
  int get activeRooms;
  @override
  int get totalMessages;
  @override
  @JsonKey(ignore: true)
  _$$ChatStatsImplCopyWith<_$ChatStatsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
