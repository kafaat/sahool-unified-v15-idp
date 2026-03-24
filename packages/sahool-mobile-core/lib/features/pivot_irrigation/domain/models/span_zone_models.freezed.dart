// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'span_zone_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

SpanConfiguration _$SpanConfigurationFromJson(Map<String, dynamic> json) {
  return _SpanConfiguration.fromJson(json);
}

/// @nodoc
mixin _$SpanConfiguration {
  String get id => throw _privateConstructorUsedError;
  int get spanNumber => throw _privateConstructorUsedError;

  /// Distance from center in meters - المسافة من المركز
  double get distanceFromCenter => throw _privateConstructorUsedError;

  /// Span length in meters - طول البرج
  double get spanLengthMeters => throw _privateConstructorUsedError;

  /// Number of nozzles on this span - عدد الفوهات
  int get nozzleCount => throw _privateConstructorUsedError;

  /// Nozzle package type - نوع حزمة الفوهات
  NozzlePackage get nozzlePackage => throw _privateConstructorUsedError;

  /// Base application rate (mm/hr) - معدل التطبيق الأساسي
  double get baseApplicationRateMmHr => throw _privateConstructorUsedError;

  /// Span zones for VRI - مناطق البرج لـ VRI
  List<SpanZone> get zones => throw _privateConstructorUsedError;

  /// Is span operational - البرج يعمل
  bool get isOperational => throw _privateConstructorUsedError;

  /// Last maintenance date
  DateTime? get lastMaintenanceDate => throw _privateConstructorUsedError;

  /// Serializes this SpanConfiguration to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SpanConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SpanConfigurationCopyWith<SpanConfiguration> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SpanConfigurationCopyWith<$Res> {
  factory $SpanConfigurationCopyWith(
          SpanConfiguration value, $Res Function(SpanConfiguration) then) =
      _$SpanConfigurationCopyWithImpl<$Res, SpanConfiguration>;
  @useResult
  $Res call(
      {String id,
      int spanNumber,
      double distanceFromCenter,
      double spanLengthMeters,
      int nozzleCount,
      NozzlePackage nozzlePackage,
      double baseApplicationRateMmHr,
      List<SpanZone> zones,
      bool isOperational,
      DateTime? lastMaintenanceDate});
}

/// @nodoc
class _$SpanConfigurationCopyWithImpl<$Res, $Val extends SpanConfiguration>
    implements $SpanConfigurationCopyWith<$Res> {
  _$SpanConfigurationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SpanConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? spanNumber = null,
    Object? distanceFromCenter = null,
    Object? spanLengthMeters = null,
    Object? nozzleCount = null,
    Object? nozzlePackage = null,
    Object? baseApplicationRateMmHr = null,
    Object? zones = null,
    Object? isOperational = null,
    Object? lastMaintenanceDate = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      spanNumber: null == spanNumber
          ? _value.spanNumber
          : spanNumber // ignore: cast_nullable_to_non_nullable
              as int,
      distanceFromCenter: null == distanceFromCenter
          ? _value.distanceFromCenter
          : distanceFromCenter // ignore: cast_nullable_to_non_nullable
              as double,
      spanLengthMeters: null == spanLengthMeters
          ? _value.spanLengthMeters
          : spanLengthMeters // ignore: cast_nullable_to_non_nullable
              as double,
      nozzleCount: null == nozzleCount
          ? _value.nozzleCount
          : nozzleCount // ignore: cast_nullable_to_non_nullable
              as int,
      nozzlePackage: null == nozzlePackage
          ? _value.nozzlePackage
          : nozzlePackage // ignore: cast_nullable_to_non_nullable
              as NozzlePackage,
      baseApplicationRateMmHr: null == baseApplicationRateMmHr
          ? _value.baseApplicationRateMmHr
          : baseApplicationRateMmHr // ignore: cast_nullable_to_non_nullable
              as double,
      zones: null == zones
          ? _value.zones
          : zones // ignore: cast_nullable_to_non_nullable
              as List<SpanZone>,
      isOperational: null == isOperational
          ? _value.isOperational
          : isOperational // ignore: cast_nullable_to_non_nullable
              as bool,
      lastMaintenanceDate: freezed == lastMaintenanceDate
          ? _value.lastMaintenanceDate
          : lastMaintenanceDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SpanConfigurationImplCopyWith<$Res>
    implements $SpanConfigurationCopyWith<$Res> {
  factory _$$SpanConfigurationImplCopyWith(_$SpanConfigurationImpl value,
          $Res Function(_$SpanConfigurationImpl) then) =
      __$$SpanConfigurationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      int spanNumber,
      double distanceFromCenter,
      double spanLengthMeters,
      int nozzleCount,
      NozzlePackage nozzlePackage,
      double baseApplicationRateMmHr,
      List<SpanZone> zones,
      bool isOperational,
      DateTime? lastMaintenanceDate});
}

/// @nodoc
class __$$SpanConfigurationImplCopyWithImpl<$Res>
    extends _$SpanConfigurationCopyWithImpl<$Res, _$SpanConfigurationImpl>
    implements _$$SpanConfigurationImplCopyWith<$Res> {
  __$$SpanConfigurationImplCopyWithImpl(_$SpanConfigurationImpl _value,
      $Res Function(_$SpanConfigurationImpl) _then)
      : super(_value, _then);

  /// Create a copy of SpanConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? spanNumber = null,
    Object? distanceFromCenter = null,
    Object? spanLengthMeters = null,
    Object? nozzleCount = null,
    Object? nozzlePackage = null,
    Object? baseApplicationRateMmHr = null,
    Object? zones = null,
    Object? isOperational = null,
    Object? lastMaintenanceDate = freezed,
  }) {
    return _then(_$SpanConfigurationImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      spanNumber: null == spanNumber
          ? _value.spanNumber
          : spanNumber // ignore: cast_nullable_to_non_nullable
              as int,
      distanceFromCenter: null == distanceFromCenter
          ? _value.distanceFromCenter
          : distanceFromCenter // ignore: cast_nullable_to_non_nullable
              as double,
      spanLengthMeters: null == spanLengthMeters
          ? _value.spanLengthMeters
          : spanLengthMeters // ignore: cast_nullable_to_non_nullable
              as double,
      nozzleCount: null == nozzleCount
          ? _value.nozzleCount
          : nozzleCount // ignore: cast_nullable_to_non_nullable
              as int,
      nozzlePackage: null == nozzlePackage
          ? _value.nozzlePackage
          : nozzlePackage // ignore: cast_nullable_to_non_nullable
              as NozzlePackage,
      baseApplicationRateMmHr: null == baseApplicationRateMmHr
          ? _value.baseApplicationRateMmHr
          : baseApplicationRateMmHr // ignore: cast_nullable_to_non_nullable
              as double,
      zones: null == zones
          ? _value._zones
          : zones // ignore: cast_nullable_to_non_nullable
              as List<SpanZone>,
      isOperational: null == isOperational
          ? _value.isOperational
          : isOperational // ignore: cast_nullable_to_non_nullable
              as bool,
      lastMaintenanceDate: freezed == lastMaintenanceDate
          ? _value.lastMaintenanceDate
          : lastMaintenanceDate // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SpanConfigurationImpl implements _SpanConfiguration {
  const _$SpanConfigurationImpl(
      {required this.id,
      required this.spanNumber,
      required this.distanceFromCenter,
      required this.spanLengthMeters,
      this.nozzleCount = 10,
      this.nozzlePackage = NozzlePackage.standard,
      this.baseApplicationRateMmHr = 6.0,
      final List<SpanZone> zones = const [],
      this.isOperational = true,
      this.lastMaintenanceDate})
      : _zones = zones;

  factory _$SpanConfigurationImpl.fromJson(Map<String, dynamic> json) =>
      _$$SpanConfigurationImplFromJson(json);

  @override
  final String id;
  @override
  final int spanNumber;

  /// Distance from center in meters - المسافة من المركز
  @override
  final double distanceFromCenter;

  /// Span length in meters - طول البرج
  @override
  final double spanLengthMeters;

  /// Number of nozzles on this span - عدد الفوهات
  @override
  @JsonKey()
  final int nozzleCount;

  /// Nozzle package type - نوع حزمة الفوهات
  @override
  @JsonKey()
  final NozzlePackage nozzlePackage;

  /// Base application rate (mm/hr) - معدل التطبيق الأساسي
  @override
  @JsonKey()
  final double baseApplicationRateMmHr;

  /// Span zones for VRI - مناطق البرج لـ VRI
  final List<SpanZone> _zones;

  /// Span zones for VRI - مناطق البرج لـ VRI
  @override
  @JsonKey()
  List<SpanZone> get zones {
    if (_zones is EqualUnmodifiableListView) return _zones;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_zones);
  }

  /// Is span operational - البرج يعمل
  @override
  @JsonKey()
  final bool isOperational;

  /// Last maintenance date
  @override
  final DateTime? lastMaintenanceDate;

  @override
  String toString() {
    return 'SpanConfiguration(id: $id, spanNumber: $spanNumber, distanceFromCenter: $distanceFromCenter, spanLengthMeters: $spanLengthMeters, nozzleCount: $nozzleCount, nozzlePackage: $nozzlePackage, baseApplicationRateMmHr: $baseApplicationRateMmHr, zones: $zones, isOperational: $isOperational, lastMaintenanceDate: $lastMaintenanceDate)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SpanConfigurationImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.spanNumber, spanNumber) ||
                other.spanNumber == spanNumber) &&
            (identical(other.distanceFromCenter, distanceFromCenter) ||
                other.distanceFromCenter == distanceFromCenter) &&
            (identical(other.spanLengthMeters, spanLengthMeters) ||
                other.spanLengthMeters == spanLengthMeters) &&
            (identical(other.nozzleCount, nozzleCount) ||
                other.nozzleCount == nozzleCount) &&
            (identical(other.nozzlePackage, nozzlePackage) ||
                other.nozzlePackage == nozzlePackage) &&
            (identical(
                    other.baseApplicationRateMmHr, baseApplicationRateMmHr) ||
                other.baseApplicationRateMmHr == baseApplicationRateMmHr) &&
            const DeepCollectionEquality().equals(other._zones, _zones) &&
            (identical(other.isOperational, isOperational) ||
                other.isOperational == isOperational) &&
            (identical(other.lastMaintenanceDate, lastMaintenanceDate) ||
                other.lastMaintenanceDate == lastMaintenanceDate));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      spanNumber,
      distanceFromCenter,
      spanLengthMeters,
      nozzleCount,
      nozzlePackage,
      baseApplicationRateMmHr,
      const DeepCollectionEquality().hash(_zones),
      isOperational,
      lastMaintenanceDate);

  /// Create a copy of SpanConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SpanConfigurationImplCopyWith<_$SpanConfigurationImpl> get copyWith =>
      __$$SpanConfigurationImplCopyWithImpl<_$SpanConfigurationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SpanConfigurationImplToJson(
      this,
    );
  }
}

abstract class _SpanConfiguration implements SpanConfiguration {
  const factory _SpanConfiguration(
      {required final String id,
      required final int spanNumber,
      required final double distanceFromCenter,
      required final double spanLengthMeters,
      final int nozzleCount,
      final NozzlePackage nozzlePackage,
      final double baseApplicationRateMmHr,
      final List<SpanZone> zones,
      final bool isOperational,
      final DateTime? lastMaintenanceDate}) = _$SpanConfigurationImpl;

  factory _SpanConfiguration.fromJson(Map<String, dynamic> json) =
      _$SpanConfigurationImpl.fromJson;

  @override
  String get id;
  @override
  int get spanNumber;

  /// Distance from center in meters - المسافة من المركز
  @override
  double get distanceFromCenter;

  /// Span length in meters - طول البرج
  @override
  double get spanLengthMeters;

  /// Number of nozzles on this span - عدد الفوهات
  @override
  int get nozzleCount;

  /// Nozzle package type - نوع حزمة الفوهات
  @override
  NozzlePackage get nozzlePackage;

  /// Base application rate (mm/hr) - معدل التطبيق الأساسي
  @override
  double get baseApplicationRateMmHr;

  /// Span zones for VRI - مناطق البرج لـ VRI
  @override
  List<SpanZone> get zones;

  /// Is span operational - البرج يعمل
  @override
  bool get isOperational;

  /// Last maintenance date
  @override
  DateTime? get lastMaintenanceDate;

  /// Create a copy of SpanConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SpanConfigurationImplCopyWith<_$SpanConfigurationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SpanZone _$SpanZoneFromJson(Map<String, dynamic> json) {
  return _SpanZone.fromJson(json);
}

/// @nodoc
mixin _$SpanZone {
  String get id => throw _privateConstructorUsedError;

  /// Span number this zone belongs to - رقم البرج
  int get spanNumber => throw _privateConstructorUsedError;

  /// Zone number within the span - رقم المنطقة داخل البرج
  int get zoneNumber => throw _privateConstructorUsedError;

  /// Start angle in degrees - زاوية البداية
  double get startAngle => throw _privateConstructorUsedError;

  /// End angle in degrees - زاوية النهاية
  double get endAngle => throw _privateConstructorUsedError;

  /// Application rate percentage (0-150%) - نسبة معدل التطبيق
  /// 100 = normal, 50 = half, 150 = 1.5x, 0 = off
  double get applicationRatePercent => throw _privateConstructorUsedError;

  /// Zone prescription (for VRA maps) - وصفة المنطقة
  String? get prescriptionId => throw _privateConstructorUsedError;

  /// NDVI value if available - قيمة NDVI
  double? get ndviValue => throw _privateConstructorUsedError;

  /// Soil type for this zone - نوع التربة
  String get soilType => throw _privateConstructorUsedError;

  /// Crop type for this zone - نوع المحصول
  String get cropType => throw _privateConstructorUsedError;

  /// Zone enabled - المنطقة مفعلة
  bool get isEnabled => throw _privateConstructorUsedError;

  /// Color for visualization
  String get color => throw _privateConstructorUsedError;

  /// Zone notes
  String get notes => throw _privateConstructorUsedError;
  String get notesAr => throw _privateConstructorUsedError;

  /// Serializes this SpanZone to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of SpanZone
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $SpanZoneCopyWith<SpanZone> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SpanZoneCopyWith<$Res> {
  factory $SpanZoneCopyWith(SpanZone value, $Res Function(SpanZone) then) =
      _$SpanZoneCopyWithImpl<$Res, SpanZone>;
  @useResult
  $Res call(
      {String id,
      int spanNumber,
      int zoneNumber,
      double startAngle,
      double endAngle,
      double applicationRatePercent,
      String? prescriptionId,
      double? ndviValue,
      String soilType,
      String cropType,
      bool isEnabled,
      String color,
      String notes,
      String notesAr});
}

/// @nodoc
class _$SpanZoneCopyWithImpl<$Res, $Val extends SpanZone>
    implements $SpanZoneCopyWith<$Res> {
  _$SpanZoneCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of SpanZone
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? spanNumber = null,
    Object? zoneNumber = null,
    Object? startAngle = null,
    Object? endAngle = null,
    Object? applicationRatePercent = null,
    Object? prescriptionId = freezed,
    Object? ndviValue = freezed,
    Object? soilType = null,
    Object? cropType = null,
    Object? isEnabled = null,
    Object? color = null,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      spanNumber: null == spanNumber
          ? _value.spanNumber
          : spanNumber // ignore: cast_nullable_to_non_nullable
              as int,
      zoneNumber: null == zoneNumber
          ? _value.zoneNumber
          : zoneNumber // ignore: cast_nullable_to_non_nullable
              as int,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: null == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double,
      applicationRatePercent: null == applicationRatePercent
          ? _value.applicationRatePercent
          : applicationRatePercent // ignore: cast_nullable_to_non_nullable
              as double,
      prescriptionId: freezed == prescriptionId
          ? _value.prescriptionId
          : prescriptionId // ignore: cast_nullable_to_non_nullable
              as String?,
      ndviValue: freezed == ndviValue
          ? _value.ndviValue
          : ndviValue // ignore: cast_nullable_to_non_nullable
              as double?,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      isEnabled: null == isEnabled
          ? _value.isEnabled
          : isEnabled // ignore: cast_nullable_to_non_nullable
              as bool,
      color: null == color
          ? _value.color
          : color // ignore: cast_nullable_to_non_nullable
              as String,
      notes: null == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String,
      notesAr: null == notesAr
          ? _value.notesAr
          : notesAr // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SpanZoneImplCopyWith<$Res>
    implements $SpanZoneCopyWith<$Res> {
  factory _$$SpanZoneImplCopyWith(
          _$SpanZoneImpl value, $Res Function(_$SpanZoneImpl) then) =
      __$$SpanZoneImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      int spanNumber,
      int zoneNumber,
      double startAngle,
      double endAngle,
      double applicationRatePercent,
      String? prescriptionId,
      double? ndviValue,
      String soilType,
      String cropType,
      bool isEnabled,
      String color,
      String notes,
      String notesAr});
}

/// @nodoc
class __$$SpanZoneImplCopyWithImpl<$Res>
    extends _$SpanZoneCopyWithImpl<$Res, _$SpanZoneImpl>
    implements _$$SpanZoneImplCopyWith<$Res> {
  __$$SpanZoneImplCopyWithImpl(
      _$SpanZoneImpl _value, $Res Function(_$SpanZoneImpl) _then)
      : super(_value, _then);

  /// Create a copy of SpanZone
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? spanNumber = null,
    Object? zoneNumber = null,
    Object? startAngle = null,
    Object? endAngle = null,
    Object? applicationRatePercent = null,
    Object? prescriptionId = freezed,
    Object? ndviValue = freezed,
    Object? soilType = null,
    Object? cropType = null,
    Object? isEnabled = null,
    Object? color = null,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_$SpanZoneImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      spanNumber: null == spanNumber
          ? _value.spanNumber
          : spanNumber // ignore: cast_nullable_to_non_nullable
              as int,
      zoneNumber: null == zoneNumber
          ? _value.zoneNumber
          : zoneNumber // ignore: cast_nullable_to_non_nullable
              as int,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: null == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double,
      applicationRatePercent: null == applicationRatePercent
          ? _value.applicationRatePercent
          : applicationRatePercent // ignore: cast_nullable_to_non_nullable
              as double,
      prescriptionId: freezed == prescriptionId
          ? _value.prescriptionId
          : prescriptionId // ignore: cast_nullable_to_non_nullable
              as String?,
      ndviValue: freezed == ndviValue
          ? _value.ndviValue
          : ndviValue // ignore: cast_nullable_to_non_nullable
              as double?,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      isEnabled: null == isEnabled
          ? _value.isEnabled
          : isEnabled // ignore: cast_nullable_to_non_nullable
              as bool,
      color: null == color
          ? _value.color
          : color // ignore: cast_nullable_to_non_nullable
              as String,
      notes: null == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String,
      notesAr: null == notesAr
          ? _value.notesAr
          : notesAr // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SpanZoneImpl implements _SpanZone {
  const _$SpanZoneImpl(
      {required this.id,
      required this.spanNumber,
      required this.zoneNumber,
      required this.startAngle,
      required this.endAngle,
      this.applicationRatePercent = 100,
      this.prescriptionId,
      this.ndviValue,
      this.soilType = '',
      this.cropType = '',
      this.isEnabled = true,
      this.color = '#4CAF50',
      this.notes = '',
      this.notesAr = ''});

  factory _$SpanZoneImpl.fromJson(Map<String, dynamic> json) =>
      _$$SpanZoneImplFromJson(json);

  @override
  final String id;

  /// Span number this zone belongs to - رقم البرج
  @override
  final int spanNumber;

  /// Zone number within the span - رقم المنطقة داخل البرج
  @override
  final int zoneNumber;

  /// Start angle in degrees - زاوية البداية
  @override
  final double startAngle;

  /// End angle in degrees - زاوية النهاية
  @override
  final double endAngle;

  /// Application rate percentage (0-150%) - نسبة معدل التطبيق
  /// 100 = normal, 50 = half, 150 = 1.5x, 0 = off
  @override
  @JsonKey()
  final double applicationRatePercent;

  /// Zone prescription (for VRA maps) - وصفة المنطقة
  @override
  final String? prescriptionId;

  /// NDVI value if available - قيمة NDVI
  @override
  final double? ndviValue;

  /// Soil type for this zone - نوع التربة
  @override
  @JsonKey()
  final String soilType;

  /// Crop type for this zone - نوع المحصول
  @override
  @JsonKey()
  final String cropType;

  /// Zone enabled - المنطقة مفعلة
  @override
  @JsonKey()
  final bool isEnabled;

  /// Color for visualization
  @override
  @JsonKey()
  final String color;

  /// Zone notes
  @override
  @JsonKey()
  final String notes;
  @override
  @JsonKey()
  final String notesAr;

  @override
  String toString() {
    return 'SpanZone(id: $id, spanNumber: $spanNumber, zoneNumber: $zoneNumber, startAngle: $startAngle, endAngle: $endAngle, applicationRatePercent: $applicationRatePercent, prescriptionId: $prescriptionId, ndviValue: $ndviValue, soilType: $soilType, cropType: $cropType, isEnabled: $isEnabled, color: $color, notes: $notes, notesAr: $notesAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SpanZoneImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.spanNumber, spanNumber) ||
                other.spanNumber == spanNumber) &&
            (identical(other.zoneNumber, zoneNumber) ||
                other.zoneNumber == zoneNumber) &&
            (identical(other.startAngle, startAngle) ||
                other.startAngle == startAngle) &&
            (identical(other.endAngle, endAngle) ||
                other.endAngle == endAngle) &&
            (identical(other.applicationRatePercent, applicationRatePercent) ||
                other.applicationRatePercent == applicationRatePercent) &&
            (identical(other.prescriptionId, prescriptionId) ||
                other.prescriptionId == prescriptionId) &&
            (identical(other.ndviValue, ndviValue) ||
                other.ndviValue == ndviValue) &&
            (identical(other.soilType, soilType) ||
                other.soilType == soilType) &&
            (identical(other.cropType, cropType) ||
                other.cropType == cropType) &&
            (identical(other.isEnabled, isEnabled) ||
                other.isEnabled == isEnabled) &&
            (identical(other.color, color) || other.color == color) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            (identical(other.notesAr, notesAr) || other.notesAr == notesAr));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      spanNumber,
      zoneNumber,
      startAngle,
      endAngle,
      applicationRatePercent,
      prescriptionId,
      ndviValue,
      soilType,
      cropType,
      isEnabled,
      color,
      notes,
      notesAr);

  /// Create a copy of SpanZone
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$SpanZoneImplCopyWith<_$SpanZoneImpl> get copyWith =>
      __$$SpanZoneImplCopyWithImpl<_$SpanZoneImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SpanZoneImplToJson(
      this,
    );
  }
}

abstract class _SpanZone implements SpanZone {
  const factory _SpanZone(
      {required final String id,
      required final int spanNumber,
      required final int zoneNumber,
      required final double startAngle,
      required final double endAngle,
      final double applicationRatePercent,
      final String? prescriptionId,
      final double? ndviValue,
      final String soilType,
      final String cropType,
      final bool isEnabled,
      final String color,
      final String notes,
      final String notesAr}) = _$SpanZoneImpl;

  factory _SpanZone.fromJson(Map<String, dynamic> json) =
      _$SpanZoneImpl.fromJson;

  @override
  String get id;

  /// Span number this zone belongs to - رقم البرج
  @override
  int get spanNumber;

  /// Zone number within the span - رقم المنطقة داخل البرج
  @override
  int get zoneNumber;

  /// Start angle in degrees - زاوية البداية
  @override
  double get startAngle;

  /// End angle in degrees - زاوية النهاية
  @override
  double get endAngle;

  /// Application rate percentage (0-150%) - نسبة معدل التطبيق
  /// 100 = normal, 50 = half, 150 = 1.5x, 0 = off
  @override
  double get applicationRatePercent;

  /// Zone prescription (for VRA maps) - وصفة المنطقة
  @override
  String? get prescriptionId;

  /// NDVI value if available - قيمة NDVI
  @override
  double? get ndviValue;

  /// Soil type for this zone - نوع التربة
  @override
  String get soilType;

  /// Crop type for this zone - نوع المحصول
  @override
  String get cropType;

  /// Zone enabled - المنطقة مفعلة
  @override
  bool get isEnabled;

  /// Color for visualization
  @override
  String get color;

  /// Zone notes
  @override
  String get notes;
  @override
  String get notesAr;

  /// Create a copy of SpanZone
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$SpanZoneImplCopyWith<_$SpanZoneImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

VRIZoneGrid _$VRIZoneGridFromJson(Map<String, dynamic> json) {
  return _VRIZoneGrid.fromJson(json);
}

/// @nodoc
mixin _$VRIZoneGrid {
  String get pivotId => throw _privateConstructorUsedError;

  /// Number of spans - عدد الأبراج
  int get spanCount => throw _privateConstructorUsedError;

  /// Number of angular divisions per span - عدد التقسيمات الزاوية لكل برج
  int get angularDivisions => throw _privateConstructorUsedError;

  /// Grid of zones [span][angle] - شبكة المناطق
  List<List<SpanZone>> get grid => throw _privateConstructorUsedError;

  /// Total zone count - إجمالي عدد المناطق
  int? get totalZones => throw _privateConstructorUsedError;

  /// Grid resolution (degrees per angular division)
  double? get angularResolution => throw _privateConstructorUsedError;

  /// Created timestamp
  DateTime? get createdAt => throw _privateConstructorUsedError;

  /// Last updated timestamp
  DateTime? get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this VRIZoneGrid to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of VRIZoneGrid
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $VRIZoneGridCopyWith<VRIZoneGrid> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $VRIZoneGridCopyWith<$Res> {
  factory $VRIZoneGridCopyWith(
          VRIZoneGrid value, $Res Function(VRIZoneGrid) then) =
      _$VRIZoneGridCopyWithImpl<$Res, VRIZoneGrid>;
  @useResult
  $Res call(
      {String pivotId,
      int spanCount,
      int angularDivisions,
      List<List<SpanZone>> grid,
      int? totalZones,
      double? angularResolution,
      DateTime? createdAt,
      DateTime? updatedAt});
}

/// @nodoc
class _$VRIZoneGridCopyWithImpl<$Res, $Val extends VRIZoneGrid>
    implements $VRIZoneGridCopyWith<$Res> {
  _$VRIZoneGridCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of VRIZoneGrid
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pivotId = null,
    Object? spanCount = null,
    Object? angularDivisions = null,
    Object? grid = null,
    Object? totalZones = freezed,
    Object? angularResolution = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
  }) {
    return _then(_value.copyWith(
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      spanCount: null == spanCount
          ? _value.spanCount
          : spanCount // ignore: cast_nullable_to_non_nullable
              as int,
      angularDivisions: null == angularDivisions
          ? _value.angularDivisions
          : angularDivisions // ignore: cast_nullable_to_non_nullable
              as int,
      grid: null == grid
          ? _value.grid
          : grid // ignore: cast_nullable_to_non_nullable
              as List<List<SpanZone>>,
      totalZones: freezed == totalZones
          ? _value.totalZones
          : totalZones // ignore: cast_nullable_to_non_nullable
              as int?,
      angularResolution: freezed == angularResolution
          ? _value.angularResolution
          : angularResolution // ignore: cast_nullable_to_non_nullable
              as double?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$VRIZoneGridImplCopyWith<$Res>
    implements $VRIZoneGridCopyWith<$Res> {
  factory _$$VRIZoneGridImplCopyWith(
          _$VRIZoneGridImpl value, $Res Function(_$VRIZoneGridImpl) then) =
      __$$VRIZoneGridImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String pivotId,
      int spanCount,
      int angularDivisions,
      List<List<SpanZone>> grid,
      int? totalZones,
      double? angularResolution,
      DateTime? createdAt,
      DateTime? updatedAt});
}

/// @nodoc
class __$$VRIZoneGridImplCopyWithImpl<$Res>
    extends _$VRIZoneGridCopyWithImpl<$Res, _$VRIZoneGridImpl>
    implements _$$VRIZoneGridImplCopyWith<$Res> {
  __$$VRIZoneGridImplCopyWithImpl(
      _$VRIZoneGridImpl _value, $Res Function(_$VRIZoneGridImpl) _then)
      : super(_value, _then);

  /// Create a copy of VRIZoneGrid
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pivotId = null,
    Object? spanCount = null,
    Object? angularDivisions = null,
    Object? grid = null,
    Object? totalZones = freezed,
    Object? angularResolution = freezed,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
  }) {
    return _then(_$VRIZoneGridImpl(
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      spanCount: null == spanCount
          ? _value.spanCount
          : spanCount // ignore: cast_nullable_to_non_nullable
              as int,
      angularDivisions: null == angularDivisions
          ? _value.angularDivisions
          : angularDivisions // ignore: cast_nullable_to_non_nullable
              as int,
      grid: null == grid
          ? _value._grid
          : grid // ignore: cast_nullable_to_non_nullable
              as List<List<SpanZone>>,
      totalZones: freezed == totalZones
          ? _value.totalZones
          : totalZones // ignore: cast_nullable_to_non_nullable
              as int?,
      angularResolution: freezed == angularResolution
          ? _value.angularResolution
          : angularResolution // ignore: cast_nullable_to_non_nullable
              as double?,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      updatedAt: freezed == updatedAt
          ? _value.updatedAt
          : updatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$VRIZoneGridImpl implements _VRIZoneGrid {
  const _$VRIZoneGridImpl(
      {required this.pivotId,
      required this.spanCount,
      required this.angularDivisions,
      required final List<List<SpanZone>> grid,
      this.totalZones,
      this.angularResolution,
      this.createdAt,
      this.updatedAt})
      : _grid = grid;

  factory _$VRIZoneGridImpl.fromJson(Map<String, dynamic> json) =>
      _$$VRIZoneGridImplFromJson(json);

  @override
  final String pivotId;

  /// Number of spans - عدد الأبراج
  @override
  final int spanCount;

  /// Number of angular divisions per span - عدد التقسيمات الزاوية لكل برج
  @override
  final int angularDivisions;

  /// Grid of zones [span][angle] - شبكة المناطق
  final List<List<SpanZone>> _grid;

  /// Grid of zones [span][angle] - شبكة المناطق
  @override
  List<List<SpanZone>> get grid {
    if (_grid is EqualUnmodifiableListView) return _grid;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_grid);
  }

  /// Total zone count - إجمالي عدد المناطق
  @override
  final int? totalZones;

  /// Grid resolution (degrees per angular division)
  @override
  final double? angularResolution;

  /// Created timestamp
  @override
  final DateTime? createdAt;

  /// Last updated timestamp
  @override
  final DateTime? updatedAt;

  @override
  String toString() {
    return 'VRIZoneGrid(pivotId: $pivotId, spanCount: $spanCount, angularDivisions: $angularDivisions, grid: $grid, totalZones: $totalZones, angularResolution: $angularResolution, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VRIZoneGridImpl &&
            (identical(other.pivotId, pivotId) || other.pivotId == pivotId) &&
            (identical(other.spanCount, spanCount) ||
                other.spanCount == spanCount) &&
            (identical(other.angularDivisions, angularDivisions) ||
                other.angularDivisions == angularDivisions) &&
            const DeepCollectionEquality().equals(other._grid, _grid) &&
            (identical(other.totalZones, totalZones) ||
                other.totalZones == totalZones) &&
            (identical(other.angularResolution, angularResolution) ||
                other.angularResolution == angularResolution) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      pivotId,
      spanCount,
      angularDivisions,
      const DeepCollectionEquality().hash(_grid),
      totalZones,
      angularResolution,
      createdAt,
      updatedAt);

  /// Create a copy of VRIZoneGrid
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$VRIZoneGridImplCopyWith<_$VRIZoneGridImpl> get copyWith =>
      __$$VRIZoneGridImplCopyWithImpl<_$VRIZoneGridImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$VRIZoneGridImplToJson(
      this,
    );
  }
}

abstract class _VRIZoneGrid implements VRIZoneGrid {
  const factory _VRIZoneGrid(
      {required final String pivotId,
      required final int spanCount,
      required final int angularDivisions,
      required final List<List<SpanZone>> grid,
      final int? totalZones,
      final double? angularResolution,
      final DateTime? createdAt,
      final DateTime? updatedAt}) = _$VRIZoneGridImpl;

  factory _VRIZoneGrid.fromJson(Map<String, dynamic> json) =
      _$VRIZoneGridImpl.fromJson;

  @override
  String get pivotId;

  /// Number of spans - عدد الأبراج
  @override
  int get spanCount;

  /// Number of angular divisions per span - عدد التقسيمات الزاوية لكل برج
  @override
  int get angularDivisions;

  /// Grid of zones [span][angle] - شبكة المناطق
  @override
  List<List<SpanZone>> get grid;

  /// Total zone count - إجمالي عدد المناطق
  @override
  int? get totalZones;

  /// Grid resolution (degrees per angular division)
  @override
  double? get angularResolution;

  /// Created timestamp
  @override
  DateTime? get createdAt;

  /// Last updated timestamp
  @override
  DateTime? get updatedAt;

  /// Create a copy of VRIZoneGrid
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$VRIZoneGridImplCopyWith<_$VRIZoneGridImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PrescriptionMap _$PrescriptionMapFromJson(Map<String, dynamic> json) {
  return _PrescriptionMap.fromJson(json);
}

/// @nodoc
mixin _$PrescriptionMap {
  String get id => throw _privateConstructorUsedError;
  String get pivotId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;

  /// Prescription type - نوع الوصفة
  PrescriptionType get prescriptionType => throw _privateConstructorUsedError;

  /// Source of prescription data - مصدر بيانات الوصفة
  PrescriptionSource get source => throw _privateConstructorUsedError;

  /// Zone values - قيم المناطق
  Map<String, double> get zoneValues => throw _privateConstructorUsedError;

  /// Minimum value
  double get minValue => throw _privateConstructorUsedError;

  /// Maximum value
  double get maxValue => throw _privateConstructorUsedError;

  /// Unit for values
  String get unit => throw _privateConstructorUsedError;

  /// Valid from date
  DateTime? get validFrom => throw _privateConstructorUsedError;

  /// Valid until date
  DateTime? get validUntil => throw _privateConstructorUsedError;

  /// Is active
  bool get isActive => throw _privateConstructorUsedError;

  /// Created timestamp
  DateTime? get createdAt => throw _privateConstructorUsedError;

  /// Notes
  String get notes => throw _privateConstructorUsedError;
  String get notesAr => throw _privateConstructorUsedError;

  /// Serializes this PrescriptionMap to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PrescriptionMap
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PrescriptionMapCopyWith<PrescriptionMap> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PrescriptionMapCopyWith<$Res> {
  factory $PrescriptionMapCopyWith(
          PrescriptionMap value, $Res Function(PrescriptionMap) then) =
      _$PrescriptionMapCopyWithImpl<$Res, PrescriptionMap>;
  @useResult
  $Res call(
      {String id,
      String pivotId,
      String name,
      String nameAr,
      PrescriptionType prescriptionType,
      PrescriptionSource source,
      Map<String, double> zoneValues,
      double minValue,
      double maxValue,
      String unit,
      DateTime? validFrom,
      DateTime? validUntil,
      bool isActive,
      DateTime? createdAt,
      String notes,
      String notesAr});
}

/// @nodoc
class _$PrescriptionMapCopyWithImpl<$Res, $Val extends PrescriptionMap>
    implements $PrescriptionMapCopyWith<$Res> {
  _$PrescriptionMapCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PrescriptionMap
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? pivotId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? prescriptionType = null,
    Object? source = null,
    Object? zoneValues = null,
    Object? minValue = null,
    Object? maxValue = null,
    Object? unit = null,
    Object? validFrom = freezed,
    Object? validUntil = freezed,
    Object? isActive = null,
    Object? createdAt = freezed,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      prescriptionType: null == prescriptionType
          ? _value.prescriptionType
          : prescriptionType // ignore: cast_nullable_to_non_nullable
              as PrescriptionType,
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as PrescriptionSource,
      zoneValues: null == zoneValues
          ? _value.zoneValues
          : zoneValues // ignore: cast_nullable_to_non_nullable
              as Map<String, double>,
      minValue: null == minValue
          ? _value.minValue
          : minValue // ignore: cast_nullable_to_non_nullable
              as double,
      maxValue: null == maxValue
          ? _value.maxValue
          : maxValue // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _value.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      validFrom: freezed == validFrom
          ? _value.validFrom
          : validFrom // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      validUntil: freezed == validUntil
          ? _value.validUntil
          : validUntil // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      notes: null == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String,
      notesAr: null == notesAr
          ? _value.notesAr
          : notesAr // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PrescriptionMapImplCopyWith<$Res>
    implements $PrescriptionMapCopyWith<$Res> {
  factory _$$PrescriptionMapImplCopyWith(_$PrescriptionMapImpl value,
          $Res Function(_$PrescriptionMapImpl) then) =
      __$$PrescriptionMapImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String pivotId,
      String name,
      String nameAr,
      PrescriptionType prescriptionType,
      PrescriptionSource source,
      Map<String, double> zoneValues,
      double minValue,
      double maxValue,
      String unit,
      DateTime? validFrom,
      DateTime? validUntil,
      bool isActive,
      DateTime? createdAt,
      String notes,
      String notesAr});
}

/// @nodoc
class __$$PrescriptionMapImplCopyWithImpl<$Res>
    extends _$PrescriptionMapCopyWithImpl<$Res, _$PrescriptionMapImpl>
    implements _$$PrescriptionMapImplCopyWith<$Res> {
  __$$PrescriptionMapImplCopyWithImpl(
      _$PrescriptionMapImpl _value, $Res Function(_$PrescriptionMapImpl) _then)
      : super(_value, _then);

  /// Create a copy of PrescriptionMap
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? pivotId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? prescriptionType = null,
    Object? source = null,
    Object? zoneValues = null,
    Object? minValue = null,
    Object? maxValue = null,
    Object? unit = null,
    Object? validFrom = freezed,
    Object? validUntil = freezed,
    Object? isActive = null,
    Object? createdAt = freezed,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_$PrescriptionMapImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      prescriptionType: null == prescriptionType
          ? _value.prescriptionType
          : prescriptionType // ignore: cast_nullable_to_non_nullable
              as PrescriptionType,
      source: null == source
          ? _value.source
          : source // ignore: cast_nullable_to_non_nullable
              as PrescriptionSource,
      zoneValues: null == zoneValues
          ? _value._zoneValues
          : zoneValues // ignore: cast_nullable_to_non_nullable
              as Map<String, double>,
      minValue: null == minValue
          ? _value.minValue
          : minValue // ignore: cast_nullable_to_non_nullable
              as double,
      maxValue: null == maxValue
          ? _value.maxValue
          : maxValue // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _value.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      validFrom: freezed == validFrom
          ? _value.validFrom
          : validFrom // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      validUntil: freezed == validUntil
          ? _value.validUntil
          : validUntil // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      notes: null == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String,
      notesAr: null == notesAr
          ? _value.notesAr
          : notesAr // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PrescriptionMapImpl implements _PrescriptionMap {
  const _$PrescriptionMapImpl(
      {required this.id,
      required this.pivotId,
      required this.name,
      this.nameAr = '',
      required this.prescriptionType,
      required this.source,
      required final Map<String, double> zoneValues,
      this.minValue = 0,
      this.maxValue = 150,
      this.unit = '%',
      this.validFrom,
      this.validUntil,
      this.isActive = true,
      this.createdAt,
      this.notes = '',
      this.notesAr = ''})
      : _zoneValues = zoneValues;

  factory _$PrescriptionMapImpl.fromJson(Map<String, dynamic> json) =>
      _$$PrescriptionMapImplFromJson(json);

  @override
  final String id;
  @override
  final String pivotId;
  @override
  final String name;
  @override
  @JsonKey()
  final String nameAr;

  /// Prescription type - نوع الوصفة
  @override
  final PrescriptionType prescriptionType;

  /// Source of prescription data - مصدر بيانات الوصفة
  @override
  final PrescriptionSource source;

  /// Zone values - قيم المناطق
  final Map<String, double> _zoneValues;

  /// Zone values - قيم المناطق
  @override
  Map<String, double> get zoneValues {
    if (_zoneValues is EqualUnmodifiableMapView) return _zoneValues;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_zoneValues);
  }

  /// Minimum value
  @override
  @JsonKey()
  final double minValue;

  /// Maximum value
  @override
  @JsonKey()
  final double maxValue;

  /// Unit for values
  @override
  @JsonKey()
  final String unit;

  /// Valid from date
  @override
  final DateTime? validFrom;

  /// Valid until date
  @override
  final DateTime? validUntil;

  /// Is active
  @override
  @JsonKey()
  final bool isActive;

  /// Created timestamp
  @override
  final DateTime? createdAt;

  /// Notes
  @override
  @JsonKey()
  final String notes;
  @override
  @JsonKey()
  final String notesAr;

  @override
  String toString() {
    return 'PrescriptionMap(id: $id, pivotId: $pivotId, name: $name, nameAr: $nameAr, prescriptionType: $prescriptionType, source: $source, zoneValues: $zoneValues, minValue: $minValue, maxValue: $maxValue, unit: $unit, validFrom: $validFrom, validUntil: $validUntil, isActive: $isActive, createdAt: $createdAt, notes: $notes, notesAr: $notesAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PrescriptionMapImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.pivotId, pivotId) || other.pivotId == pivotId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.prescriptionType, prescriptionType) ||
                other.prescriptionType == prescriptionType) &&
            (identical(other.source, source) || other.source == source) &&
            const DeepCollectionEquality()
                .equals(other._zoneValues, _zoneValues) &&
            (identical(other.minValue, minValue) ||
                other.minValue == minValue) &&
            (identical(other.maxValue, maxValue) ||
                other.maxValue == maxValue) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.validFrom, validFrom) ||
                other.validFrom == validFrom) &&
            (identical(other.validUntil, validUntil) ||
                other.validUntil == validUntil) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            (identical(other.notesAr, notesAr) || other.notesAr == notesAr));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      pivotId,
      name,
      nameAr,
      prescriptionType,
      source,
      const DeepCollectionEquality().hash(_zoneValues),
      minValue,
      maxValue,
      unit,
      validFrom,
      validUntil,
      isActive,
      createdAt,
      notes,
      notesAr);

  /// Create a copy of PrescriptionMap
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PrescriptionMapImplCopyWith<_$PrescriptionMapImpl> get copyWith =>
      __$$PrescriptionMapImplCopyWithImpl<_$PrescriptionMapImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PrescriptionMapImplToJson(
      this,
    );
  }
}

abstract class _PrescriptionMap implements PrescriptionMap {
  const factory _PrescriptionMap(
      {required final String id,
      required final String pivotId,
      required final String name,
      final String nameAr,
      required final PrescriptionType prescriptionType,
      required final PrescriptionSource source,
      required final Map<String, double> zoneValues,
      final double minValue,
      final double maxValue,
      final String unit,
      final DateTime? validFrom,
      final DateTime? validUntil,
      final bool isActive,
      final DateTime? createdAt,
      final String notes,
      final String notesAr}) = _$PrescriptionMapImpl;

  factory _PrescriptionMap.fromJson(Map<String, dynamic> json) =
      _$PrescriptionMapImpl.fromJson;

  @override
  String get id;
  @override
  String get pivotId;
  @override
  String get name;
  @override
  String get nameAr;

  /// Prescription type - نوع الوصفة
  @override
  PrescriptionType get prescriptionType;

  /// Source of prescription data - مصدر بيانات الوصفة
  @override
  PrescriptionSource get source;

  /// Zone values - قيم المناطق
  @override
  Map<String, double> get zoneValues;

  /// Minimum value
  @override
  double get minValue;

  /// Maximum value
  @override
  double get maxValue;

  /// Unit for values
  @override
  String get unit;

  /// Valid from date
  @override
  DateTime? get validFrom;

  /// Valid until date
  @override
  DateTime? get validUntil;

  /// Is active
  @override
  bool get isActive;

  /// Created timestamp
  @override
  DateTime? get createdAt;

  /// Notes
  @override
  String get notes;
  @override
  String get notesAr;

  /// Create a copy of PrescriptionMap
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PrescriptionMapImplCopyWith<_$PrescriptionMapImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

VRIZoneStatistics _$VRIZoneStatisticsFromJson(Map<String, dynamic> json) {
  return _VRIZoneStatistics.fromJson(json);
}

/// @nodoc
mixin _$VRIZoneStatistics {
  int get totalZones => throw _privateConstructorUsedError;
  int get activeZones => throw _privateConstructorUsedError;
  int get offZones => throw _privateConstructorUsedError;
  double get avgApplicationRate => throw _privateConstructorUsedError;
  double get minApplicationRate => throw _privateConstructorUsedError;
  double get maxApplicationRate => throw _privateConstructorUsedError;
  Map<String, int> get rateDistribution => throw _privateConstructorUsedError;
  double get waterSavingsPercent => throw _privateConstructorUsedError;

  /// Serializes this VRIZoneStatistics to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of VRIZoneStatistics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $VRIZoneStatisticsCopyWith<VRIZoneStatistics> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $VRIZoneStatisticsCopyWith<$Res> {
  factory $VRIZoneStatisticsCopyWith(
          VRIZoneStatistics value, $Res Function(VRIZoneStatistics) then) =
      _$VRIZoneStatisticsCopyWithImpl<$Res, VRIZoneStatistics>;
  @useResult
  $Res call(
      {int totalZones,
      int activeZones,
      int offZones,
      double avgApplicationRate,
      double minApplicationRate,
      double maxApplicationRate,
      Map<String, int> rateDistribution,
      double waterSavingsPercent});
}

/// @nodoc
class _$VRIZoneStatisticsCopyWithImpl<$Res, $Val extends VRIZoneStatistics>
    implements $VRIZoneStatisticsCopyWith<$Res> {
  _$VRIZoneStatisticsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of VRIZoneStatistics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalZones = null,
    Object? activeZones = null,
    Object? offZones = null,
    Object? avgApplicationRate = null,
    Object? minApplicationRate = null,
    Object? maxApplicationRate = null,
    Object? rateDistribution = null,
    Object? waterSavingsPercent = null,
  }) {
    return _then(_value.copyWith(
      totalZones: null == totalZones
          ? _value.totalZones
          : totalZones // ignore: cast_nullable_to_non_nullable
              as int,
      activeZones: null == activeZones
          ? _value.activeZones
          : activeZones // ignore: cast_nullable_to_non_nullable
              as int,
      offZones: null == offZones
          ? _value.offZones
          : offZones // ignore: cast_nullable_to_non_nullable
              as int,
      avgApplicationRate: null == avgApplicationRate
          ? _value.avgApplicationRate
          : avgApplicationRate // ignore: cast_nullable_to_non_nullable
              as double,
      minApplicationRate: null == minApplicationRate
          ? _value.minApplicationRate
          : minApplicationRate // ignore: cast_nullable_to_non_nullable
              as double,
      maxApplicationRate: null == maxApplicationRate
          ? _value.maxApplicationRate
          : maxApplicationRate // ignore: cast_nullable_to_non_nullable
              as double,
      rateDistribution: null == rateDistribution
          ? _value.rateDistribution
          : rateDistribution // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
      waterSavingsPercent: null == waterSavingsPercent
          ? _value.waterSavingsPercent
          : waterSavingsPercent // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$VRIZoneStatisticsImplCopyWith<$Res>
    implements $VRIZoneStatisticsCopyWith<$Res> {
  factory _$$VRIZoneStatisticsImplCopyWith(_$VRIZoneStatisticsImpl value,
          $Res Function(_$VRIZoneStatisticsImpl) then) =
      __$$VRIZoneStatisticsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {int totalZones,
      int activeZones,
      int offZones,
      double avgApplicationRate,
      double minApplicationRate,
      double maxApplicationRate,
      Map<String, int> rateDistribution,
      double waterSavingsPercent});
}

/// @nodoc
class __$$VRIZoneStatisticsImplCopyWithImpl<$Res>
    extends _$VRIZoneStatisticsCopyWithImpl<$Res, _$VRIZoneStatisticsImpl>
    implements _$$VRIZoneStatisticsImplCopyWith<$Res> {
  __$$VRIZoneStatisticsImplCopyWithImpl(_$VRIZoneStatisticsImpl _value,
      $Res Function(_$VRIZoneStatisticsImpl) _then)
      : super(_value, _then);

  /// Create a copy of VRIZoneStatistics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? totalZones = null,
    Object? activeZones = null,
    Object? offZones = null,
    Object? avgApplicationRate = null,
    Object? minApplicationRate = null,
    Object? maxApplicationRate = null,
    Object? rateDistribution = null,
    Object? waterSavingsPercent = null,
  }) {
    return _then(_$VRIZoneStatisticsImpl(
      totalZones: null == totalZones
          ? _value.totalZones
          : totalZones // ignore: cast_nullable_to_non_nullable
              as int,
      activeZones: null == activeZones
          ? _value.activeZones
          : activeZones // ignore: cast_nullable_to_non_nullable
              as int,
      offZones: null == offZones
          ? _value.offZones
          : offZones // ignore: cast_nullable_to_non_nullable
              as int,
      avgApplicationRate: null == avgApplicationRate
          ? _value.avgApplicationRate
          : avgApplicationRate // ignore: cast_nullable_to_non_nullable
              as double,
      minApplicationRate: null == minApplicationRate
          ? _value.minApplicationRate
          : minApplicationRate // ignore: cast_nullable_to_non_nullable
              as double,
      maxApplicationRate: null == maxApplicationRate
          ? _value.maxApplicationRate
          : maxApplicationRate // ignore: cast_nullable_to_non_nullable
              as double,
      rateDistribution: null == rateDistribution
          ? _value._rateDistribution
          : rateDistribution // ignore: cast_nullable_to_non_nullable
              as Map<String, int>,
      waterSavingsPercent: null == waterSavingsPercent
          ? _value.waterSavingsPercent
          : waterSavingsPercent // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$VRIZoneStatisticsImpl extends _VRIZoneStatistics {
  const _$VRIZoneStatisticsImpl(
      {required this.totalZones,
      required this.activeZones,
      required this.offZones,
      required this.avgApplicationRate,
      required this.minApplicationRate,
      required this.maxApplicationRate,
      required final Map<String, int> rateDistribution,
      required this.waterSavingsPercent})
      : _rateDistribution = rateDistribution,
        super._();

  factory _$VRIZoneStatisticsImpl.fromJson(Map<String, dynamic> json) =>
      _$$VRIZoneStatisticsImplFromJson(json);

  @override
  final int totalZones;
  @override
  final int activeZones;
  @override
  final int offZones;
  @override
  final double avgApplicationRate;
  @override
  final double minApplicationRate;
  @override
  final double maxApplicationRate;
  final Map<String, int> _rateDistribution;
  @override
  Map<String, int> get rateDistribution {
    if (_rateDistribution is EqualUnmodifiableMapView) return _rateDistribution;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_rateDistribution);
  }

  @override
  final double waterSavingsPercent;

  @override
  String toString() {
    return 'VRIZoneStatistics(totalZones: $totalZones, activeZones: $activeZones, offZones: $offZones, avgApplicationRate: $avgApplicationRate, minApplicationRate: $minApplicationRate, maxApplicationRate: $maxApplicationRate, rateDistribution: $rateDistribution, waterSavingsPercent: $waterSavingsPercent)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VRIZoneStatisticsImpl &&
            (identical(other.totalZones, totalZones) ||
                other.totalZones == totalZones) &&
            (identical(other.activeZones, activeZones) ||
                other.activeZones == activeZones) &&
            (identical(other.offZones, offZones) ||
                other.offZones == offZones) &&
            (identical(other.avgApplicationRate, avgApplicationRate) ||
                other.avgApplicationRate == avgApplicationRate) &&
            (identical(other.minApplicationRate, minApplicationRate) ||
                other.minApplicationRate == minApplicationRate) &&
            (identical(other.maxApplicationRate, maxApplicationRate) ||
                other.maxApplicationRate == maxApplicationRate) &&
            const DeepCollectionEquality()
                .equals(other._rateDistribution, _rateDistribution) &&
            (identical(other.waterSavingsPercent, waterSavingsPercent) ||
                other.waterSavingsPercent == waterSavingsPercent));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      totalZones,
      activeZones,
      offZones,
      avgApplicationRate,
      minApplicationRate,
      maxApplicationRate,
      const DeepCollectionEquality().hash(_rateDistribution),
      waterSavingsPercent);

  /// Create a copy of VRIZoneStatistics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$VRIZoneStatisticsImplCopyWith<_$VRIZoneStatisticsImpl> get copyWith =>
      __$$VRIZoneStatisticsImplCopyWithImpl<_$VRIZoneStatisticsImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$VRIZoneStatisticsImplToJson(
      this,
    );
  }
}

abstract class _VRIZoneStatistics extends VRIZoneStatistics {
  const factory _VRIZoneStatistics(
      {required final int totalZones,
      required final int activeZones,
      required final int offZones,
      required final double avgApplicationRate,
      required final double minApplicationRate,
      required final double maxApplicationRate,
      required final Map<String, int> rateDistribution,
      required final double waterSavingsPercent}) = _$VRIZoneStatisticsImpl;
  const _VRIZoneStatistics._() : super._();

  factory _VRIZoneStatistics.fromJson(Map<String, dynamic> json) =
      _$VRIZoneStatisticsImpl.fromJson;

  @override
  int get totalZones;
  @override
  int get activeZones;
  @override
  int get offZones;
  @override
  double get avgApplicationRate;
  @override
  double get minApplicationRate;
  @override
  double get maxApplicationRate;
  @override
  Map<String, int> get rateDistribution;
  @override
  double get waterSavingsPercent;

  /// Create a copy of VRIZoneStatistics
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$VRIZoneStatisticsImplCopyWith<_$VRIZoneStatisticsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
