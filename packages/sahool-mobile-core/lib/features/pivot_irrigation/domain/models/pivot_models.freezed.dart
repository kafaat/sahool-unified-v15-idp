// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'pivot_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

PivotConfiguration _$PivotConfigurationFromJson(Map<String, dynamic> json) {
  return _PivotConfiguration.fromJson(json);
}

/// @nodoc
mixin _$PivotConfiguration {
  String get id => throw _privateConstructorUsedError;
  String get fieldId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;

  /// Center point coordinates - نقطة المركز
  double get centerLat => throw _privateConstructorUsedError;
  double get centerLng => throw _privateConstructorUsedError;

  /// Pivot arm length in meters - طول الذراع بالأمتار
  double get lengthMeters => throw _privateConstructorUsedError;

  /// Overhang length (end gun extension) - امتداد المدفع الطرفي
  double get overhangMeters => throw _privateConstructorUsedError;

  /// Number of spans/towers - عدد الأبراج
  int get spansCount => throw _privateConstructorUsedError;

  /// Rotation direction - اتجاه الدوران
  RotationDirection get rotationDirection => throw _privateConstructorUsedError;

  /// Total irrigated area in hectares - المساحة المروية بالهكتار
  double get areaHectares => throw _privateConstructorUsedError;

  /// Pivot type - نوع المحوري
  PivotType get pivotType => throw _privateConstructorUsedError;

  /// Start angle for partial pivots (degrees) - زاوية البداية
  double get startAngle => throw _privateConstructorUsedError;

  /// End angle for partial pivots (degrees) - زاوية النهاية
  double get endAngle => throw _privateConstructorUsedError;

  /// Flow rate in liters per hour - معدل التدفق
  double get flowRateLph => throw _privateConstructorUsedError;

  /// Operating pressure in bars - ضغط التشغيل
  double get operatingPressureBar => throw _privateConstructorUsedError;

  /// Has Variable Rate Irrigation - معدل ري متغير
  bool get hasVRI => throw _privateConstructorUsedError;

  /// Has end gun - مدفع طرفي
  bool get hasEndGun => throw _privateConstructorUsedError;

  /// Has corner system - نظام الزوايا
  bool get hasCornerSystem => throw _privateConstructorUsedError;

  /// List of sectors - قائمة القطاعات
  List<PivotSector> get sectors => throw _privateConstructorUsedError;

  /// VRI zones if applicable - مناطق VRI
  List<VRIZone> get vriZones => throw _privateConstructorUsedError;

  /// Created timestamp
  DateTime? get createdAt => throw _privateConstructorUsedError;

  /// Last updated timestamp
  DateTime? get updatedAt => throw _privateConstructorUsedError;

  /// Serializes this PivotConfiguration to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PivotConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PivotConfigurationCopyWith<PivotConfiguration> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PivotConfigurationCopyWith<$Res> {
  factory $PivotConfigurationCopyWith(
          PivotConfiguration value, $Res Function(PivotConfiguration) then) =
      _$PivotConfigurationCopyWithImpl<$Res, PivotConfiguration>;
  @useResult
  $Res call(
      {String id,
      String fieldId,
      String name,
      String nameAr,
      double centerLat,
      double centerLng,
      double lengthMeters,
      double overhangMeters,
      int spansCount,
      RotationDirection rotationDirection,
      double areaHectares,
      PivotType pivotType,
      double startAngle,
      double endAngle,
      double flowRateLph,
      double operatingPressureBar,
      bool hasVRI,
      bool hasEndGun,
      bool hasCornerSystem,
      List<PivotSector> sectors,
      List<VRIZone> vriZones,
      DateTime? createdAt,
      DateTime? updatedAt});
}

/// @nodoc
class _$PivotConfigurationCopyWithImpl<$Res, $Val extends PivotConfiguration>
    implements $PivotConfigurationCopyWith<$Res> {
  _$PivotConfigurationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PivotConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? fieldId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? centerLat = null,
    Object? centerLng = null,
    Object? lengthMeters = null,
    Object? overhangMeters = null,
    Object? spansCount = null,
    Object? rotationDirection = null,
    Object? areaHectares = null,
    Object? pivotType = null,
    Object? startAngle = null,
    Object? endAngle = null,
    Object? flowRateLph = null,
    Object? operatingPressureBar = null,
    Object? hasVRI = null,
    Object? hasEndGun = null,
    Object? hasCornerSystem = null,
    Object? sectors = null,
    Object? vriZones = null,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      centerLat: null == centerLat
          ? _value.centerLat
          : centerLat // ignore: cast_nullable_to_non_nullable
              as double,
      centerLng: null == centerLng
          ? _value.centerLng
          : centerLng // ignore: cast_nullable_to_non_nullable
              as double,
      lengthMeters: null == lengthMeters
          ? _value.lengthMeters
          : lengthMeters // ignore: cast_nullable_to_non_nullable
              as double,
      overhangMeters: null == overhangMeters
          ? _value.overhangMeters
          : overhangMeters // ignore: cast_nullable_to_non_nullable
              as double,
      spansCount: null == spansCount
          ? _value.spansCount
          : spansCount // ignore: cast_nullable_to_non_nullable
              as int,
      rotationDirection: null == rotationDirection
          ? _value.rotationDirection
          : rotationDirection // ignore: cast_nullable_to_non_nullable
              as RotationDirection,
      areaHectares: null == areaHectares
          ? _value.areaHectares
          : areaHectares // ignore: cast_nullable_to_non_nullable
              as double,
      pivotType: null == pivotType
          ? _value.pivotType
          : pivotType // ignore: cast_nullable_to_non_nullable
              as PivotType,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: null == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double,
      flowRateLph: null == flowRateLph
          ? _value.flowRateLph
          : flowRateLph // ignore: cast_nullable_to_non_nullable
              as double,
      operatingPressureBar: null == operatingPressureBar
          ? _value.operatingPressureBar
          : operatingPressureBar // ignore: cast_nullable_to_non_nullable
              as double,
      hasVRI: null == hasVRI
          ? _value.hasVRI
          : hasVRI // ignore: cast_nullable_to_non_nullable
              as bool,
      hasEndGun: null == hasEndGun
          ? _value.hasEndGun
          : hasEndGun // ignore: cast_nullable_to_non_nullable
              as bool,
      hasCornerSystem: null == hasCornerSystem
          ? _value.hasCornerSystem
          : hasCornerSystem // ignore: cast_nullable_to_non_nullable
              as bool,
      sectors: null == sectors
          ? _value.sectors
          : sectors // ignore: cast_nullable_to_non_nullable
              as List<PivotSector>,
      vriZones: null == vriZones
          ? _value.vriZones
          : vriZones // ignore: cast_nullable_to_non_nullable
              as List<VRIZone>,
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
abstract class _$$PivotConfigurationImplCopyWith<$Res>
    implements $PivotConfigurationCopyWith<$Res> {
  factory _$$PivotConfigurationImplCopyWith(_$PivotConfigurationImpl value,
          $Res Function(_$PivotConfigurationImpl) then) =
      __$$PivotConfigurationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String fieldId,
      String name,
      String nameAr,
      double centerLat,
      double centerLng,
      double lengthMeters,
      double overhangMeters,
      int spansCount,
      RotationDirection rotationDirection,
      double areaHectares,
      PivotType pivotType,
      double startAngle,
      double endAngle,
      double flowRateLph,
      double operatingPressureBar,
      bool hasVRI,
      bool hasEndGun,
      bool hasCornerSystem,
      List<PivotSector> sectors,
      List<VRIZone> vriZones,
      DateTime? createdAt,
      DateTime? updatedAt});
}

/// @nodoc
class __$$PivotConfigurationImplCopyWithImpl<$Res>
    extends _$PivotConfigurationCopyWithImpl<$Res, _$PivotConfigurationImpl>
    implements _$$PivotConfigurationImplCopyWith<$Res> {
  __$$PivotConfigurationImplCopyWithImpl(_$PivotConfigurationImpl _value,
      $Res Function(_$PivotConfigurationImpl) _then)
      : super(_value, _then);

  /// Create a copy of PivotConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? fieldId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? centerLat = null,
    Object? centerLng = null,
    Object? lengthMeters = null,
    Object? overhangMeters = null,
    Object? spansCount = null,
    Object? rotationDirection = null,
    Object? areaHectares = null,
    Object? pivotType = null,
    Object? startAngle = null,
    Object? endAngle = null,
    Object? flowRateLph = null,
    Object? operatingPressureBar = null,
    Object? hasVRI = null,
    Object? hasEndGun = null,
    Object? hasCornerSystem = null,
    Object? sectors = null,
    Object? vriZones = null,
    Object? createdAt = freezed,
    Object? updatedAt = freezed,
  }) {
    return _then(_$PivotConfigurationImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      centerLat: null == centerLat
          ? _value.centerLat
          : centerLat // ignore: cast_nullable_to_non_nullable
              as double,
      centerLng: null == centerLng
          ? _value.centerLng
          : centerLng // ignore: cast_nullable_to_non_nullable
              as double,
      lengthMeters: null == lengthMeters
          ? _value.lengthMeters
          : lengthMeters // ignore: cast_nullable_to_non_nullable
              as double,
      overhangMeters: null == overhangMeters
          ? _value.overhangMeters
          : overhangMeters // ignore: cast_nullable_to_non_nullable
              as double,
      spansCount: null == spansCount
          ? _value.spansCount
          : spansCount // ignore: cast_nullable_to_non_nullable
              as int,
      rotationDirection: null == rotationDirection
          ? _value.rotationDirection
          : rotationDirection // ignore: cast_nullable_to_non_nullable
              as RotationDirection,
      areaHectares: null == areaHectares
          ? _value.areaHectares
          : areaHectares // ignore: cast_nullable_to_non_nullable
              as double,
      pivotType: null == pivotType
          ? _value.pivotType
          : pivotType // ignore: cast_nullable_to_non_nullable
              as PivotType,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: null == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double,
      flowRateLph: null == flowRateLph
          ? _value.flowRateLph
          : flowRateLph // ignore: cast_nullable_to_non_nullable
              as double,
      operatingPressureBar: null == operatingPressureBar
          ? _value.operatingPressureBar
          : operatingPressureBar // ignore: cast_nullable_to_non_nullable
              as double,
      hasVRI: null == hasVRI
          ? _value.hasVRI
          : hasVRI // ignore: cast_nullable_to_non_nullable
              as bool,
      hasEndGun: null == hasEndGun
          ? _value.hasEndGun
          : hasEndGun // ignore: cast_nullable_to_non_nullable
              as bool,
      hasCornerSystem: null == hasCornerSystem
          ? _value.hasCornerSystem
          : hasCornerSystem // ignore: cast_nullable_to_non_nullable
              as bool,
      sectors: null == sectors
          ? _value._sectors
          : sectors // ignore: cast_nullable_to_non_nullable
              as List<PivotSector>,
      vriZones: null == vriZones
          ? _value._vriZones
          : vriZones // ignore: cast_nullable_to_non_nullable
              as List<VRIZone>,
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
class _$PivotConfigurationImpl implements _PivotConfiguration {
  const _$PivotConfigurationImpl(
      {required this.id,
      required this.fieldId,
      required this.name,
      this.nameAr = '',
      required this.centerLat,
      required this.centerLng,
      required this.lengthMeters,
      this.overhangMeters = 0,
      required this.spansCount,
      this.rotationDirection = RotationDirection.clockwise,
      required this.areaHectares,
      this.pivotType = PivotType.fullCircle,
      this.startAngle = 0,
      this.endAngle = 360,
      required this.flowRateLph,
      this.operatingPressureBar = 2.5,
      this.hasVRI = false,
      this.hasEndGun = false,
      this.hasCornerSystem = false,
      final List<PivotSector> sectors = const [],
      final List<VRIZone> vriZones = const [],
      this.createdAt,
      this.updatedAt})
      : _sectors = sectors,
        _vriZones = vriZones;

  factory _$PivotConfigurationImpl.fromJson(Map<String, dynamic> json) =>
      _$$PivotConfigurationImplFromJson(json);

  @override
  final String id;
  @override
  final String fieldId;
  @override
  final String name;
  @override
  @JsonKey()
  final String nameAr;

  /// Center point coordinates - نقطة المركز
  @override
  final double centerLat;
  @override
  final double centerLng;

  /// Pivot arm length in meters - طول الذراع بالأمتار
  @override
  final double lengthMeters;

  /// Overhang length (end gun extension) - امتداد المدفع الطرفي
  @override
  @JsonKey()
  final double overhangMeters;

  /// Number of spans/towers - عدد الأبراج
  @override
  final int spansCount;

  /// Rotation direction - اتجاه الدوران
  @override
  @JsonKey()
  final RotationDirection rotationDirection;

  /// Total irrigated area in hectares - المساحة المروية بالهكتار
  @override
  final double areaHectares;

  /// Pivot type - نوع المحوري
  @override
  @JsonKey()
  final PivotType pivotType;

  /// Start angle for partial pivots (degrees) - زاوية البداية
  @override
  @JsonKey()
  final double startAngle;

  /// End angle for partial pivots (degrees) - زاوية النهاية
  @override
  @JsonKey()
  final double endAngle;

  /// Flow rate in liters per hour - معدل التدفق
  @override
  final double flowRateLph;

  /// Operating pressure in bars - ضغط التشغيل
  @override
  @JsonKey()
  final double operatingPressureBar;

  /// Has Variable Rate Irrigation - معدل ري متغير
  @override
  @JsonKey()
  final bool hasVRI;

  /// Has end gun - مدفع طرفي
  @override
  @JsonKey()
  final bool hasEndGun;

  /// Has corner system - نظام الزوايا
  @override
  @JsonKey()
  final bool hasCornerSystem;

  /// List of sectors - قائمة القطاعات
  final List<PivotSector> _sectors;

  /// List of sectors - قائمة القطاعات
  @override
  @JsonKey()
  List<PivotSector> get sectors {
    if (_sectors is EqualUnmodifiableListView) return _sectors;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_sectors);
  }

  /// VRI zones if applicable - مناطق VRI
  final List<VRIZone> _vriZones;

  /// VRI zones if applicable - مناطق VRI
  @override
  @JsonKey()
  List<VRIZone> get vriZones {
    if (_vriZones is EqualUnmodifiableListView) return _vriZones;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_vriZones);
  }

  /// Created timestamp
  @override
  final DateTime? createdAt;

  /// Last updated timestamp
  @override
  final DateTime? updatedAt;

  @override
  String toString() {
    return 'PivotConfiguration(id: $id, fieldId: $fieldId, name: $name, nameAr: $nameAr, centerLat: $centerLat, centerLng: $centerLng, lengthMeters: $lengthMeters, overhangMeters: $overhangMeters, spansCount: $spansCount, rotationDirection: $rotationDirection, areaHectares: $areaHectares, pivotType: $pivotType, startAngle: $startAngle, endAngle: $endAngle, flowRateLph: $flowRateLph, operatingPressureBar: $operatingPressureBar, hasVRI: $hasVRI, hasEndGun: $hasEndGun, hasCornerSystem: $hasCornerSystem, sectors: $sectors, vriZones: $vriZones, createdAt: $createdAt, updatedAt: $updatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PivotConfigurationImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.fieldId, fieldId) || other.fieldId == fieldId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.centerLat, centerLat) ||
                other.centerLat == centerLat) &&
            (identical(other.centerLng, centerLng) ||
                other.centerLng == centerLng) &&
            (identical(other.lengthMeters, lengthMeters) ||
                other.lengthMeters == lengthMeters) &&
            (identical(other.overhangMeters, overhangMeters) ||
                other.overhangMeters == overhangMeters) &&
            (identical(other.spansCount, spansCount) ||
                other.spansCount == spansCount) &&
            (identical(other.rotationDirection, rotationDirection) ||
                other.rotationDirection == rotationDirection) &&
            (identical(other.areaHectares, areaHectares) ||
                other.areaHectares == areaHectares) &&
            (identical(other.pivotType, pivotType) ||
                other.pivotType == pivotType) &&
            (identical(other.startAngle, startAngle) ||
                other.startAngle == startAngle) &&
            (identical(other.endAngle, endAngle) ||
                other.endAngle == endAngle) &&
            (identical(other.flowRateLph, flowRateLph) ||
                other.flowRateLph == flowRateLph) &&
            (identical(other.operatingPressureBar, operatingPressureBar) ||
                other.operatingPressureBar == operatingPressureBar) &&
            (identical(other.hasVRI, hasVRI) || other.hasVRI == hasVRI) &&
            (identical(other.hasEndGun, hasEndGun) ||
                other.hasEndGun == hasEndGun) &&
            (identical(other.hasCornerSystem, hasCornerSystem) ||
                other.hasCornerSystem == hasCornerSystem) &&
            const DeepCollectionEquality().equals(other._sectors, _sectors) &&
            const DeepCollectionEquality().equals(other._vriZones, _vriZones) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt) &&
            (identical(other.updatedAt, updatedAt) ||
                other.updatedAt == updatedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        id,
        fieldId,
        name,
        nameAr,
        centerLat,
        centerLng,
        lengthMeters,
        overhangMeters,
        spansCount,
        rotationDirection,
        areaHectares,
        pivotType,
        startAngle,
        endAngle,
        flowRateLph,
        operatingPressureBar,
        hasVRI,
        hasEndGun,
        hasCornerSystem,
        const DeepCollectionEquality().hash(_sectors),
        const DeepCollectionEquality().hash(_vriZones),
        createdAt,
        updatedAt
      ]);

  /// Create a copy of PivotConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PivotConfigurationImplCopyWith<_$PivotConfigurationImpl> get copyWith =>
      __$$PivotConfigurationImplCopyWithImpl<_$PivotConfigurationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PivotConfigurationImplToJson(
      this,
    );
  }
}

abstract class _PivotConfiguration implements PivotConfiguration {
  const factory _PivotConfiguration(
      {required final String id,
      required final String fieldId,
      required final String name,
      final String nameAr,
      required final double centerLat,
      required final double centerLng,
      required final double lengthMeters,
      final double overhangMeters,
      required final int spansCount,
      final RotationDirection rotationDirection,
      required final double areaHectares,
      final PivotType pivotType,
      final double startAngle,
      final double endAngle,
      required final double flowRateLph,
      final double operatingPressureBar,
      final bool hasVRI,
      final bool hasEndGun,
      final bool hasCornerSystem,
      final List<PivotSector> sectors,
      final List<VRIZone> vriZones,
      final DateTime? createdAt,
      final DateTime? updatedAt}) = _$PivotConfigurationImpl;

  factory _PivotConfiguration.fromJson(Map<String, dynamic> json) =
      _$PivotConfigurationImpl.fromJson;

  @override
  String get id;
  @override
  String get fieldId;
  @override
  String get name;
  @override
  String get nameAr;

  /// Center point coordinates - نقطة المركز
  @override
  double get centerLat;
  @override
  double get centerLng;

  /// Pivot arm length in meters - طول الذراع بالأمتار
  @override
  double get lengthMeters;

  /// Overhang length (end gun extension) - امتداد المدفع الطرفي
  @override
  double get overhangMeters;

  /// Number of spans/towers - عدد الأبراج
  @override
  int get spansCount;

  /// Rotation direction - اتجاه الدوران
  @override
  RotationDirection get rotationDirection;

  /// Total irrigated area in hectares - المساحة المروية بالهكتار
  @override
  double get areaHectares;

  /// Pivot type - نوع المحوري
  @override
  PivotType get pivotType;

  /// Start angle for partial pivots (degrees) - زاوية البداية
  @override
  double get startAngle;

  /// End angle for partial pivots (degrees) - زاوية النهاية
  @override
  double get endAngle;

  /// Flow rate in liters per hour - معدل التدفق
  @override
  double get flowRateLph;

  /// Operating pressure in bars - ضغط التشغيل
  @override
  double get operatingPressureBar;

  /// Has Variable Rate Irrigation - معدل ري متغير
  @override
  bool get hasVRI;

  /// Has end gun - مدفع طرفي
  @override
  bool get hasEndGun;

  /// Has corner system - نظام الزوايا
  @override
  bool get hasCornerSystem;

  /// List of sectors - قائمة القطاعات
  @override
  List<PivotSector> get sectors;

  /// VRI zones if applicable - مناطق VRI
  @override
  List<VRIZone> get vriZones;

  /// Created timestamp
  @override
  DateTime? get createdAt;

  /// Last updated timestamp
  @override
  DateTime? get updatedAt;

  /// Create a copy of PivotConfiguration
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PivotConfigurationImplCopyWith<_$PivotConfigurationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PivotSector _$PivotSectorFromJson(Map<String, dynamic> json) {
  return _PivotSector.fromJson(json);
}

/// @nodoc
mixin _$PivotSector {
  String get id => throw _privateConstructorUsedError;
  int get sectorNumber => throw _privateConstructorUsedError;

  /// Sector name - اسم القطاع
  String get name => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;

  /// Start angle in degrees - زاوية البداية
  double get startAngle => throw _privateConstructorUsedError;

  /// End angle in degrees - زاوية النهاية
  double get endAngle => throw _privateConstructorUsedError;

  /// Irrigation depth in mm - عمق الري
  double get irrigationDepthMm => throw _privateConstructorUsedError;

  /// Application rate (mm/hr) - معدل التطبيق
  double get applicationRateMmHr => throw _privateConstructorUsedError;

  /// Is sector enabled - القطاع مفعل
  bool get isEnabled => throw _privateConstructorUsedError;

  /// Speed percentage (50-100%) - نسبة السرعة
  double get speedPercent => throw _privateConstructorUsedError;

  /// Crop type in this sector - نوع المحصول
  String get cropType => throw _privateConstructorUsedError;

  /// Soil type in this sector - نوع التربة
  String get soilType => throw _privateConstructorUsedError;

  /// NDVI value (if available) - قيمة NDVI
  double? get ndviValue => throw _privateConstructorUsedError;

  /// Soil moisture percentage - نسبة رطوبة التربة
  double? get soilMoisturePercent => throw _privateConstructorUsedError;

  /// Color for visualization - لون العرض
  String get color => throw _privateConstructorUsedError;

  /// Serializes this PivotSector to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PivotSector
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PivotSectorCopyWith<PivotSector> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PivotSectorCopyWith<$Res> {
  factory $PivotSectorCopyWith(
          PivotSector value, $Res Function(PivotSector) then) =
      _$PivotSectorCopyWithImpl<$Res, PivotSector>;
  @useResult
  $Res call(
      {String id,
      int sectorNumber,
      String name,
      String nameAr,
      double startAngle,
      double endAngle,
      double irrigationDepthMm,
      double applicationRateMmHr,
      bool isEnabled,
      double speedPercent,
      String cropType,
      String soilType,
      double? ndviValue,
      double? soilMoisturePercent,
      String color});
}

/// @nodoc
class _$PivotSectorCopyWithImpl<$Res, $Val extends PivotSector>
    implements $PivotSectorCopyWith<$Res> {
  _$PivotSectorCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PivotSector
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? sectorNumber = null,
    Object? name = null,
    Object? nameAr = null,
    Object? startAngle = null,
    Object? endAngle = null,
    Object? irrigationDepthMm = null,
    Object? applicationRateMmHr = null,
    Object? isEnabled = null,
    Object? speedPercent = null,
    Object? cropType = null,
    Object? soilType = null,
    Object? ndviValue = freezed,
    Object? soilMoisturePercent = freezed,
    Object? color = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      sectorNumber: null == sectorNumber
          ? _value.sectorNumber
          : sectorNumber // ignore: cast_nullable_to_non_nullable
              as int,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: null == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationDepthMm: null == irrigationDepthMm
          ? _value.irrigationDepthMm
          : irrigationDepthMm // ignore: cast_nullable_to_non_nullable
              as double,
      applicationRateMmHr: null == applicationRateMmHr
          ? _value.applicationRateMmHr
          : applicationRateMmHr // ignore: cast_nullable_to_non_nullable
              as double,
      isEnabled: null == isEnabled
          ? _value.isEnabled
          : isEnabled // ignore: cast_nullable_to_non_nullable
              as bool,
      speedPercent: null == speedPercent
          ? _value.speedPercent
          : speedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      ndviValue: freezed == ndviValue
          ? _value.ndviValue
          : ndviValue // ignore: cast_nullable_to_non_nullable
              as double?,
      soilMoisturePercent: freezed == soilMoisturePercent
          ? _value.soilMoisturePercent
          : soilMoisturePercent // ignore: cast_nullable_to_non_nullable
              as double?,
      color: null == color
          ? _value.color
          : color // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PivotSectorImplCopyWith<$Res>
    implements $PivotSectorCopyWith<$Res> {
  factory _$$PivotSectorImplCopyWith(
          _$PivotSectorImpl value, $Res Function(_$PivotSectorImpl) then) =
      __$$PivotSectorImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      int sectorNumber,
      String name,
      String nameAr,
      double startAngle,
      double endAngle,
      double irrigationDepthMm,
      double applicationRateMmHr,
      bool isEnabled,
      double speedPercent,
      String cropType,
      String soilType,
      double? ndviValue,
      double? soilMoisturePercent,
      String color});
}

/// @nodoc
class __$$PivotSectorImplCopyWithImpl<$Res>
    extends _$PivotSectorCopyWithImpl<$Res, _$PivotSectorImpl>
    implements _$$PivotSectorImplCopyWith<$Res> {
  __$$PivotSectorImplCopyWithImpl(
      _$PivotSectorImpl _value, $Res Function(_$PivotSectorImpl) _then)
      : super(_value, _then);

  /// Create a copy of PivotSector
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? sectorNumber = null,
    Object? name = null,
    Object? nameAr = null,
    Object? startAngle = null,
    Object? endAngle = null,
    Object? irrigationDepthMm = null,
    Object? applicationRateMmHr = null,
    Object? isEnabled = null,
    Object? speedPercent = null,
    Object? cropType = null,
    Object? soilType = null,
    Object? ndviValue = freezed,
    Object? soilMoisturePercent = freezed,
    Object? color = null,
  }) {
    return _then(_$PivotSectorImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      sectorNumber: null == sectorNumber
          ? _value.sectorNumber
          : sectorNumber // ignore: cast_nullable_to_non_nullable
              as int,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: null == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationDepthMm: null == irrigationDepthMm
          ? _value.irrigationDepthMm
          : irrigationDepthMm // ignore: cast_nullable_to_non_nullable
              as double,
      applicationRateMmHr: null == applicationRateMmHr
          ? _value.applicationRateMmHr
          : applicationRateMmHr // ignore: cast_nullable_to_non_nullable
              as double,
      isEnabled: null == isEnabled
          ? _value.isEnabled
          : isEnabled // ignore: cast_nullable_to_non_nullable
              as bool,
      speedPercent: null == speedPercent
          ? _value.speedPercent
          : speedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      ndviValue: freezed == ndviValue
          ? _value.ndviValue
          : ndviValue // ignore: cast_nullable_to_non_nullable
              as double?,
      soilMoisturePercent: freezed == soilMoisturePercent
          ? _value.soilMoisturePercent
          : soilMoisturePercent // ignore: cast_nullable_to_non_nullable
              as double?,
      color: null == color
          ? _value.color
          : color // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PivotSectorImpl implements _PivotSector {
  const _$PivotSectorImpl(
      {required this.id,
      required this.sectorNumber,
      this.name = '',
      this.nameAr = '',
      required this.startAngle,
      required this.endAngle,
      this.irrigationDepthMm = 25,
      this.applicationRateMmHr = 6.0,
      this.isEnabled = true,
      this.speedPercent = 100,
      this.cropType = '',
      this.soilType = '',
      this.ndviValue,
      this.soilMoisturePercent,
      this.color = '#4CAF50'});

  factory _$PivotSectorImpl.fromJson(Map<String, dynamic> json) =>
      _$$PivotSectorImplFromJson(json);

  @override
  final String id;
  @override
  final int sectorNumber;

  /// Sector name - اسم القطاع
  @override
  @JsonKey()
  final String name;
  @override
  @JsonKey()
  final String nameAr;

  /// Start angle in degrees - زاوية البداية
  @override
  final double startAngle;

  /// End angle in degrees - زاوية النهاية
  @override
  final double endAngle;

  /// Irrigation depth in mm - عمق الري
  @override
  @JsonKey()
  final double irrigationDepthMm;

  /// Application rate (mm/hr) - معدل التطبيق
  @override
  @JsonKey()
  final double applicationRateMmHr;

  /// Is sector enabled - القطاع مفعل
  @override
  @JsonKey()
  final bool isEnabled;

  /// Speed percentage (50-100%) - نسبة السرعة
  @override
  @JsonKey()
  final double speedPercent;

  /// Crop type in this sector - نوع المحصول
  @override
  @JsonKey()
  final String cropType;

  /// Soil type in this sector - نوع التربة
  @override
  @JsonKey()
  final String soilType;

  /// NDVI value (if available) - قيمة NDVI
  @override
  final double? ndviValue;

  /// Soil moisture percentage - نسبة رطوبة التربة
  @override
  final double? soilMoisturePercent;

  /// Color for visualization - لون العرض
  @override
  @JsonKey()
  final String color;

  @override
  String toString() {
    return 'PivotSector(id: $id, sectorNumber: $sectorNumber, name: $name, nameAr: $nameAr, startAngle: $startAngle, endAngle: $endAngle, irrigationDepthMm: $irrigationDepthMm, applicationRateMmHr: $applicationRateMmHr, isEnabled: $isEnabled, speedPercent: $speedPercent, cropType: $cropType, soilType: $soilType, ndviValue: $ndviValue, soilMoisturePercent: $soilMoisturePercent, color: $color)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PivotSectorImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.sectorNumber, sectorNumber) ||
                other.sectorNumber == sectorNumber) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.startAngle, startAngle) ||
                other.startAngle == startAngle) &&
            (identical(other.endAngle, endAngle) ||
                other.endAngle == endAngle) &&
            (identical(other.irrigationDepthMm, irrigationDepthMm) ||
                other.irrigationDepthMm == irrigationDepthMm) &&
            (identical(other.applicationRateMmHr, applicationRateMmHr) ||
                other.applicationRateMmHr == applicationRateMmHr) &&
            (identical(other.isEnabled, isEnabled) ||
                other.isEnabled == isEnabled) &&
            (identical(other.speedPercent, speedPercent) ||
                other.speedPercent == speedPercent) &&
            (identical(other.cropType, cropType) ||
                other.cropType == cropType) &&
            (identical(other.soilType, soilType) ||
                other.soilType == soilType) &&
            (identical(other.ndviValue, ndviValue) ||
                other.ndviValue == ndviValue) &&
            (identical(other.soilMoisturePercent, soilMoisturePercent) ||
                other.soilMoisturePercent == soilMoisturePercent) &&
            (identical(other.color, color) || other.color == color));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      sectorNumber,
      name,
      nameAr,
      startAngle,
      endAngle,
      irrigationDepthMm,
      applicationRateMmHr,
      isEnabled,
      speedPercent,
      cropType,
      soilType,
      ndviValue,
      soilMoisturePercent,
      color);

  /// Create a copy of PivotSector
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PivotSectorImplCopyWith<_$PivotSectorImpl> get copyWith =>
      __$$PivotSectorImplCopyWithImpl<_$PivotSectorImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PivotSectorImplToJson(
      this,
    );
  }
}

abstract class _PivotSector implements PivotSector {
  const factory _PivotSector(
      {required final String id,
      required final int sectorNumber,
      final String name,
      final String nameAr,
      required final double startAngle,
      required final double endAngle,
      final double irrigationDepthMm,
      final double applicationRateMmHr,
      final bool isEnabled,
      final double speedPercent,
      final String cropType,
      final String soilType,
      final double? ndviValue,
      final double? soilMoisturePercent,
      final String color}) = _$PivotSectorImpl;

  factory _PivotSector.fromJson(Map<String, dynamic> json) =
      _$PivotSectorImpl.fromJson;

  @override
  String get id;
  @override
  int get sectorNumber;

  /// Sector name - اسم القطاع
  @override
  String get name;
  @override
  String get nameAr;

  /// Start angle in degrees - زاوية البداية
  @override
  double get startAngle;

  /// End angle in degrees - زاوية النهاية
  @override
  double get endAngle;

  /// Irrigation depth in mm - عمق الري
  @override
  double get irrigationDepthMm;

  /// Application rate (mm/hr) - معدل التطبيق
  @override
  double get applicationRateMmHr;

  /// Is sector enabled - القطاع مفعل
  @override
  bool get isEnabled;

  /// Speed percentage (50-100%) - نسبة السرعة
  @override
  double get speedPercent;

  /// Crop type in this sector - نوع المحصول
  @override
  String get cropType;

  /// Soil type in this sector - نوع التربة
  @override
  String get soilType;

  /// NDVI value (if available) - قيمة NDVI
  @override
  double? get ndviValue;

  /// Soil moisture percentage - نسبة رطوبة التربة
  @override
  double? get soilMoisturePercent;

  /// Color for visualization - لون العرض
  @override
  String get color;

  /// Create a copy of PivotSector
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PivotSectorImplCopyWith<_$PivotSectorImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

VRIZone _$VRIZoneFromJson(Map<String, dynamic> json) {
  return _VRIZone.fromJson(json);
}

/// @nodoc
mixin _$VRIZone {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;

  /// Zone polygon coordinates (within pivot circle)
  List<List<double>> get coordinates => throw _privateConstructorUsedError;

  /// Application rate multiplier (0.0 - 1.5) - مضاعف معدل التطبيق
  double get rateMultiplier => throw _privateConstructorUsedError;

  /// Target soil moisture - رطوبة التربة المستهدفة
  double get targetSoilMoisturePercent => throw _privateConstructorUsedError;

  /// Management zone type - نوع منطقة الإدارة
  VRIZoneType get zoneType => throw _privateConstructorUsedError;

  /// Color for visualization
  String get color => throw _privateConstructorUsedError;

  /// Is zone active
  bool get isActive => throw _privateConstructorUsedError;

  /// Serializes this VRIZone to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of VRIZone
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $VRIZoneCopyWith<VRIZone> get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $VRIZoneCopyWith<$Res> {
  factory $VRIZoneCopyWith(VRIZone value, $Res Function(VRIZone) then) =
      _$VRIZoneCopyWithImpl<$Res, VRIZone>;
  @useResult
  $Res call(
      {String id,
      String name,
      String nameAr,
      List<List<double>> coordinates,
      double rateMultiplier,
      double targetSoilMoisturePercent,
      VRIZoneType zoneType,
      String color,
      bool isActive});
}

/// @nodoc
class _$VRIZoneCopyWithImpl<$Res, $Val extends VRIZone>
    implements $VRIZoneCopyWith<$Res> {
  _$VRIZoneCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of VRIZone
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? nameAr = null,
    Object? coordinates = null,
    Object? rateMultiplier = null,
    Object? targetSoilMoisturePercent = null,
    Object? zoneType = null,
    Object? color = null,
    Object? isActive = null,
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
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      coordinates: null == coordinates
          ? _value.coordinates
          : coordinates // ignore: cast_nullable_to_non_nullable
              as List<List<double>>,
      rateMultiplier: null == rateMultiplier
          ? _value.rateMultiplier
          : rateMultiplier // ignore: cast_nullable_to_non_nullable
              as double,
      targetSoilMoisturePercent: null == targetSoilMoisturePercent
          ? _value.targetSoilMoisturePercent
          : targetSoilMoisturePercent // ignore: cast_nullable_to_non_nullable
              as double,
      zoneType: null == zoneType
          ? _value.zoneType
          : zoneType // ignore: cast_nullable_to_non_nullable
              as VRIZoneType,
      color: null == color
          ? _value.color
          : color // ignore: cast_nullable_to_non_nullable
              as String,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$VRIZoneImplCopyWith<$Res> implements $VRIZoneCopyWith<$Res> {
  factory _$$VRIZoneImplCopyWith(
          _$VRIZoneImpl value, $Res Function(_$VRIZoneImpl) then) =
      __$$VRIZoneImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String nameAr,
      List<List<double>> coordinates,
      double rateMultiplier,
      double targetSoilMoisturePercent,
      VRIZoneType zoneType,
      String color,
      bool isActive});
}

/// @nodoc
class __$$VRIZoneImplCopyWithImpl<$Res>
    extends _$VRIZoneCopyWithImpl<$Res, _$VRIZoneImpl>
    implements _$$VRIZoneImplCopyWith<$Res> {
  __$$VRIZoneImplCopyWithImpl(
      _$VRIZoneImpl _value, $Res Function(_$VRIZoneImpl) _then)
      : super(_value, _then);

  /// Create a copy of VRIZone
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? nameAr = null,
    Object? coordinates = null,
    Object? rateMultiplier = null,
    Object? targetSoilMoisturePercent = null,
    Object? zoneType = null,
    Object? color = null,
    Object? isActive = null,
  }) {
    return _then(_$VRIZoneImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      coordinates: null == coordinates
          ? _value._coordinates
          : coordinates // ignore: cast_nullable_to_non_nullable
              as List<List<double>>,
      rateMultiplier: null == rateMultiplier
          ? _value.rateMultiplier
          : rateMultiplier // ignore: cast_nullable_to_non_nullable
              as double,
      targetSoilMoisturePercent: null == targetSoilMoisturePercent
          ? _value.targetSoilMoisturePercent
          : targetSoilMoisturePercent // ignore: cast_nullable_to_non_nullable
              as double,
      zoneType: null == zoneType
          ? _value.zoneType
          : zoneType // ignore: cast_nullable_to_non_nullable
              as VRIZoneType,
      color: null == color
          ? _value.color
          : color // ignore: cast_nullable_to_non_nullable
              as String,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$VRIZoneImpl implements _VRIZone {
  const _$VRIZoneImpl(
      {required this.id,
      required this.name,
      this.nameAr = '',
      required final List<List<double>> coordinates,
      this.rateMultiplier = 1.0,
      this.targetSoilMoisturePercent = 60,
      this.zoneType = VRIZoneType.normal,
      this.color = '#2196F3',
      this.isActive = true})
      : _coordinates = coordinates;

  factory _$VRIZoneImpl.fromJson(Map<String, dynamic> json) =>
      _$$VRIZoneImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  @JsonKey()
  final String nameAr;

  /// Zone polygon coordinates (within pivot circle)
  final List<List<double>> _coordinates;

  /// Zone polygon coordinates (within pivot circle)
  @override
  List<List<double>> get coordinates {
    if (_coordinates is EqualUnmodifiableListView) return _coordinates;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_coordinates);
  }

  /// Application rate multiplier (0.0 - 1.5) - مضاعف معدل التطبيق
  @override
  @JsonKey()
  final double rateMultiplier;

  /// Target soil moisture - رطوبة التربة المستهدفة
  @override
  @JsonKey()
  final double targetSoilMoisturePercent;

  /// Management zone type - نوع منطقة الإدارة
  @override
  @JsonKey()
  final VRIZoneType zoneType;

  /// Color for visualization
  @override
  @JsonKey()
  final String color;

  /// Is zone active
  @override
  @JsonKey()
  final bool isActive;

  @override
  String toString() {
    return 'VRIZone(id: $id, name: $name, nameAr: $nameAr, coordinates: $coordinates, rateMultiplier: $rateMultiplier, targetSoilMoisturePercent: $targetSoilMoisturePercent, zoneType: $zoneType, color: $color, isActive: $isActive)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VRIZoneImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            const DeepCollectionEquality()
                .equals(other._coordinates, _coordinates) &&
            (identical(other.rateMultiplier, rateMultiplier) ||
                other.rateMultiplier == rateMultiplier) &&
            (identical(other.targetSoilMoisturePercent,
                    targetSoilMoisturePercent) ||
                other.targetSoilMoisturePercent == targetSoilMoisturePercent) &&
            (identical(other.zoneType, zoneType) ||
                other.zoneType == zoneType) &&
            (identical(other.color, color) || other.color == color) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      nameAr,
      const DeepCollectionEquality().hash(_coordinates),
      rateMultiplier,
      targetSoilMoisturePercent,
      zoneType,
      color,
      isActive);

  /// Create a copy of VRIZone
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$VRIZoneImplCopyWith<_$VRIZoneImpl> get copyWith =>
      __$$VRIZoneImplCopyWithImpl<_$VRIZoneImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$VRIZoneImplToJson(
      this,
    );
  }
}

abstract class _VRIZone implements VRIZone {
  const factory _VRIZone(
      {required final String id,
      required final String name,
      final String nameAr,
      required final List<List<double>> coordinates,
      final double rateMultiplier,
      final double targetSoilMoisturePercent,
      final VRIZoneType zoneType,
      final String color,
      final bool isActive}) = _$VRIZoneImpl;

  factory _VRIZone.fromJson(Map<String, dynamic> json) = _$VRIZoneImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get nameAr;

  /// Zone polygon coordinates (within pivot circle)
  @override
  List<List<double>> get coordinates;

  /// Application rate multiplier (0.0 - 1.5) - مضاعف معدل التطبيق
  @override
  double get rateMultiplier;

  /// Target soil moisture - رطوبة التربة المستهدفة
  @override
  double get targetSoilMoisturePercent;

  /// Management zone type - نوع منطقة الإدارة
  @override
  VRIZoneType get zoneType;

  /// Color for visualization
  @override
  String get color;

  /// Is zone active
  @override
  bool get isActive;

  /// Create a copy of VRIZone
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$VRIZoneImplCopyWith<_$VRIZoneImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PivotStatus _$PivotStatusFromJson(Map<String, dynamic> json) {
  return _PivotStatus.fromJson(json);
}

/// @nodoc
mixin _$PivotStatus {
  String get pivotId => throw _privateConstructorUsedError;

  /// Current angle position (0-360°) - الموقع الزاوي الحالي
  double get currentAngle => throw _privateConstructorUsedError;

  /// Operating status - حالة التشغيل
  PivotOperatingStatus get operatingStatus =>
      throw _privateConstructorUsedError;

  /// Direction of movement - اتجاه الحركة
  PivotDirection get direction => throw _privateConstructorUsedError;

  /// Current speed percentage (0-100%) - السرعة الحالية
  double get speedPercent => throw _privateConstructorUsedError;

  /// Timer setting in hours - إعداد المؤقت
  double get timerHours => throw _privateConstructorUsedError;

  /// Elapsed time in minutes - الوقت المنقضي
  double get elapsedMinutes => throw _privateConstructorUsedError;

  /// Current flow rate L/h - معدل التدفق الحالي
  double get currentFlowRateLph => throw _privateConstructorUsedError;

  /// Current pressure (bar) - الضغط الحالي
  double get currentPressureBar => throw _privateConstructorUsedError;

  /// End gun status - حالة المدفع الطرفي
  bool get endGunActive => throw _privateConstructorUsedError;

  /// Corner system status - حالة نظام الزوايا
  bool get cornerSystemActive => throw _privateConstructorUsedError;

  /// Water applied this run (m³) - المياه المطبقة هذه الدورة
  double get waterAppliedM3 => throw _privateConstructorUsedError;

  /// Energy consumed this run (kWh) - الطاقة المستهلكة
  double get energyConsumedKwh => throw _privateConstructorUsedError;

  /// Estimated completion time
  DateTime? get estimatedCompletionTime => throw _privateConstructorUsedError;

  /// Last update timestamp
  DateTime get lastUpdated => throw _privateConstructorUsedError;

  /// Active alerts - التنبيهات النشطة
  List<PivotAlert> get activeAlerts => throw _privateConstructorUsedError;

  /// GPS coordinates of pivot end (arm tip)
  double? get armEndLat => throw _privateConstructorUsedError;
  double? get armEndLng => throw _privateConstructorUsedError;

  /// Serializes this PivotStatus to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PivotStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PivotStatusCopyWith<PivotStatus> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PivotStatusCopyWith<$Res> {
  factory $PivotStatusCopyWith(
          PivotStatus value, $Res Function(PivotStatus) then) =
      _$PivotStatusCopyWithImpl<$Res, PivotStatus>;
  @useResult
  $Res call(
      {String pivotId,
      double currentAngle,
      PivotOperatingStatus operatingStatus,
      PivotDirection direction,
      double speedPercent,
      double timerHours,
      double elapsedMinutes,
      double currentFlowRateLph,
      double currentPressureBar,
      bool endGunActive,
      bool cornerSystemActive,
      double waterAppliedM3,
      double energyConsumedKwh,
      DateTime? estimatedCompletionTime,
      DateTime lastUpdated,
      List<PivotAlert> activeAlerts,
      double? armEndLat,
      double? armEndLng});
}

/// @nodoc
class _$PivotStatusCopyWithImpl<$Res, $Val extends PivotStatus>
    implements $PivotStatusCopyWith<$Res> {
  _$PivotStatusCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PivotStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pivotId = null,
    Object? currentAngle = null,
    Object? operatingStatus = null,
    Object? direction = null,
    Object? speedPercent = null,
    Object? timerHours = null,
    Object? elapsedMinutes = null,
    Object? currentFlowRateLph = null,
    Object? currentPressureBar = null,
    Object? endGunActive = null,
    Object? cornerSystemActive = null,
    Object? waterAppliedM3 = null,
    Object? energyConsumedKwh = null,
    Object? estimatedCompletionTime = freezed,
    Object? lastUpdated = null,
    Object? activeAlerts = null,
    Object? armEndLat = freezed,
    Object? armEndLng = freezed,
  }) {
    return _then(_value.copyWith(
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      currentAngle: null == currentAngle
          ? _value.currentAngle
          : currentAngle // ignore: cast_nullable_to_non_nullable
              as double,
      operatingStatus: null == operatingStatus
          ? _value.operatingStatus
          : operatingStatus // ignore: cast_nullable_to_non_nullable
              as PivotOperatingStatus,
      direction: null == direction
          ? _value.direction
          : direction // ignore: cast_nullable_to_non_nullable
              as PivotDirection,
      speedPercent: null == speedPercent
          ? _value.speedPercent
          : speedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      timerHours: null == timerHours
          ? _value.timerHours
          : timerHours // ignore: cast_nullable_to_non_nullable
              as double,
      elapsedMinutes: null == elapsedMinutes
          ? _value.elapsedMinutes
          : elapsedMinutes // ignore: cast_nullable_to_non_nullable
              as double,
      currentFlowRateLph: null == currentFlowRateLph
          ? _value.currentFlowRateLph
          : currentFlowRateLph // ignore: cast_nullable_to_non_nullable
              as double,
      currentPressureBar: null == currentPressureBar
          ? _value.currentPressureBar
          : currentPressureBar // ignore: cast_nullable_to_non_nullable
              as double,
      endGunActive: null == endGunActive
          ? _value.endGunActive
          : endGunActive // ignore: cast_nullable_to_non_nullable
              as bool,
      cornerSystemActive: null == cornerSystemActive
          ? _value.cornerSystemActive
          : cornerSystemActive // ignore: cast_nullable_to_non_nullable
              as bool,
      waterAppliedM3: null == waterAppliedM3
          ? _value.waterAppliedM3
          : waterAppliedM3 // ignore: cast_nullable_to_non_nullable
              as double,
      energyConsumedKwh: null == energyConsumedKwh
          ? _value.energyConsumedKwh
          : energyConsumedKwh // ignore: cast_nullable_to_non_nullable
              as double,
      estimatedCompletionTime: freezed == estimatedCompletionTime
          ? _value.estimatedCompletionTime
          : estimatedCompletionTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastUpdated: null == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime,
      activeAlerts: null == activeAlerts
          ? _value.activeAlerts
          : activeAlerts // ignore: cast_nullable_to_non_nullable
              as List<PivotAlert>,
      armEndLat: freezed == armEndLat
          ? _value.armEndLat
          : armEndLat // ignore: cast_nullable_to_non_nullable
              as double?,
      armEndLng: freezed == armEndLng
          ? _value.armEndLng
          : armEndLng // ignore: cast_nullable_to_non_nullable
              as double?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PivotStatusImplCopyWith<$Res>
    implements $PivotStatusCopyWith<$Res> {
  factory _$$PivotStatusImplCopyWith(
          _$PivotStatusImpl value, $Res Function(_$PivotStatusImpl) then) =
      __$$PivotStatusImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String pivotId,
      double currentAngle,
      PivotOperatingStatus operatingStatus,
      PivotDirection direction,
      double speedPercent,
      double timerHours,
      double elapsedMinutes,
      double currentFlowRateLph,
      double currentPressureBar,
      bool endGunActive,
      bool cornerSystemActive,
      double waterAppliedM3,
      double energyConsumedKwh,
      DateTime? estimatedCompletionTime,
      DateTime lastUpdated,
      List<PivotAlert> activeAlerts,
      double? armEndLat,
      double? armEndLng});
}

/// @nodoc
class __$$PivotStatusImplCopyWithImpl<$Res>
    extends _$PivotStatusCopyWithImpl<$Res, _$PivotStatusImpl>
    implements _$$PivotStatusImplCopyWith<$Res> {
  __$$PivotStatusImplCopyWithImpl(
      _$PivotStatusImpl _value, $Res Function(_$PivotStatusImpl) _then)
      : super(_value, _then);

  /// Create a copy of PivotStatus
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pivotId = null,
    Object? currentAngle = null,
    Object? operatingStatus = null,
    Object? direction = null,
    Object? speedPercent = null,
    Object? timerHours = null,
    Object? elapsedMinutes = null,
    Object? currentFlowRateLph = null,
    Object? currentPressureBar = null,
    Object? endGunActive = null,
    Object? cornerSystemActive = null,
    Object? waterAppliedM3 = null,
    Object? energyConsumedKwh = null,
    Object? estimatedCompletionTime = freezed,
    Object? lastUpdated = null,
    Object? activeAlerts = null,
    Object? armEndLat = freezed,
    Object? armEndLng = freezed,
  }) {
    return _then(_$PivotStatusImpl(
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      currentAngle: null == currentAngle
          ? _value.currentAngle
          : currentAngle // ignore: cast_nullable_to_non_nullable
              as double,
      operatingStatus: null == operatingStatus
          ? _value.operatingStatus
          : operatingStatus // ignore: cast_nullable_to_non_nullable
              as PivotOperatingStatus,
      direction: null == direction
          ? _value.direction
          : direction // ignore: cast_nullable_to_non_nullable
              as PivotDirection,
      speedPercent: null == speedPercent
          ? _value.speedPercent
          : speedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      timerHours: null == timerHours
          ? _value.timerHours
          : timerHours // ignore: cast_nullable_to_non_nullable
              as double,
      elapsedMinutes: null == elapsedMinutes
          ? _value.elapsedMinutes
          : elapsedMinutes // ignore: cast_nullable_to_non_nullable
              as double,
      currentFlowRateLph: null == currentFlowRateLph
          ? _value.currentFlowRateLph
          : currentFlowRateLph // ignore: cast_nullable_to_non_nullable
              as double,
      currentPressureBar: null == currentPressureBar
          ? _value.currentPressureBar
          : currentPressureBar // ignore: cast_nullable_to_non_nullable
              as double,
      endGunActive: null == endGunActive
          ? _value.endGunActive
          : endGunActive // ignore: cast_nullable_to_non_nullable
              as bool,
      cornerSystemActive: null == cornerSystemActive
          ? _value.cornerSystemActive
          : cornerSystemActive // ignore: cast_nullable_to_non_nullable
              as bool,
      waterAppliedM3: null == waterAppliedM3
          ? _value.waterAppliedM3
          : waterAppliedM3 // ignore: cast_nullable_to_non_nullable
              as double,
      energyConsumedKwh: null == energyConsumedKwh
          ? _value.energyConsumedKwh
          : energyConsumedKwh // ignore: cast_nullable_to_non_nullable
              as double,
      estimatedCompletionTime: freezed == estimatedCompletionTime
          ? _value.estimatedCompletionTime
          : estimatedCompletionTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      lastUpdated: null == lastUpdated
          ? _value.lastUpdated
          : lastUpdated // ignore: cast_nullable_to_non_nullable
              as DateTime,
      activeAlerts: null == activeAlerts
          ? _value._activeAlerts
          : activeAlerts // ignore: cast_nullable_to_non_nullable
              as List<PivotAlert>,
      armEndLat: freezed == armEndLat
          ? _value.armEndLat
          : armEndLat // ignore: cast_nullable_to_non_nullable
              as double?,
      armEndLng: freezed == armEndLng
          ? _value.armEndLng
          : armEndLng // ignore: cast_nullable_to_non_nullable
              as double?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PivotStatusImpl implements _PivotStatus {
  const _$PivotStatusImpl(
      {required this.pivotId,
      required this.currentAngle,
      required this.operatingStatus,
      required this.direction,
      required this.speedPercent,
      this.timerHours = 0,
      this.elapsedMinutes = 0,
      this.currentFlowRateLph = 0,
      this.currentPressureBar = 0,
      this.endGunActive = false,
      this.cornerSystemActive = false,
      this.waterAppliedM3 = 0,
      this.energyConsumedKwh = 0,
      this.estimatedCompletionTime,
      required this.lastUpdated,
      final List<PivotAlert> activeAlerts = const [],
      this.armEndLat,
      this.armEndLng})
      : _activeAlerts = activeAlerts;

  factory _$PivotStatusImpl.fromJson(Map<String, dynamic> json) =>
      _$$PivotStatusImplFromJson(json);

  @override
  final String pivotId;

  /// Current angle position (0-360°) - الموقع الزاوي الحالي
  @override
  final double currentAngle;

  /// Operating status - حالة التشغيل
  @override
  final PivotOperatingStatus operatingStatus;

  /// Direction of movement - اتجاه الحركة
  @override
  final PivotDirection direction;

  /// Current speed percentage (0-100%) - السرعة الحالية
  @override
  final double speedPercent;

  /// Timer setting in hours - إعداد المؤقت
  @override
  @JsonKey()
  final double timerHours;

  /// Elapsed time in minutes - الوقت المنقضي
  @override
  @JsonKey()
  final double elapsedMinutes;

  /// Current flow rate L/h - معدل التدفق الحالي
  @override
  @JsonKey()
  final double currentFlowRateLph;

  /// Current pressure (bar) - الضغط الحالي
  @override
  @JsonKey()
  final double currentPressureBar;

  /// End gun status - حالة المدفع الطرفي
  @override
  @JsonKey()
  final bool endGunActive;

  /// Corner system status - حالة نظام الزوايا
  @override
  @JsonKey()
  final bool cornerSystemActive;

  /// Water applied this run (m³) - المياه المطبقة هذه الدورة
  @override
  @JsonKey()
  final double waterAppliedM3;

  /// Energy consumed this run (kWh) - الطاقة المستهلكة
  @override
  @JsonKey()
  final double energyConsumedKwh;

  /// Estimated completion time
  @override
  final DateTime? estimatedCompletionTime;

  /// Last update timestamp
  @override
  final DateTime lastUpdated;

  /// Active alerts - التنبيهات النشطة
  final List<PivotAlert> _activeAlerts;

  /// Active alerts - التنبيهات النشطة
  @override
  @JsonKey()
  List<PivotAlert> get activeAlerts {
    if (_activeAlerts is EqualUnmodifiableListView) return _activeAlerts;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_activeAlerts);
  }

  /// GPS coordinates of pivot end (arm tip)
  @override
  final double? armEndLat;
  @override
  final double? armEndLng;

  @override
  String toString() {
    return 'PivotStatus(pivotId: $pivotId, currentAngle: $currentAngle, operatingStatus: $operatingStatus, direction: $direction, speedPercent: $speedPercent, timerHours: $timerHours, elapsedMinutes: $elapsedMinutes, currentFlowRateLph: $currentFlowRateLph, currentPressureBar: $currentPressureBar, endGunActive: $endGunActive, cornerSystemActive: $cornerSystemActive, waterAppliedM3: $waterAppliedM3, energyConsumedKwh: $energyConsumedKwh, estimatedCompletionTime: $estimatedCompletionTime, lastUpdated: $lastUpdated, activeAlerts: $activeAlerts, armEndLat: $armEndLat, armEndLng: $armEndLng)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PivotStatusImpl &&
            (identical(other.pivotId, pivotId) || other.pivotId == pivotId) &&
            (identical(other.currentAngle, currentAngle) ||
                other.currentAngle == currentAngle) &&
            (identical(other.operatingStatus, operatingStatus) ||
                other.operatingStatus == operatingStatus) &&
            (identical(other.direction, direction) ||
                other.direction == direction) &&
            (identical(other.speedPercent, speedPercent) ||
                other.speedPercent == speedPercent) &&
            (identical(other.timerHours, timerHours) ||
                other.timerHours == timerHours) &&
            (identical(other.elapsedMinutes, elapsedMinutes) ||
                other.elapsedMinutes == elapsedMinutes) &&
            (identical(other.currentFlowRateLph, currentFlowRateLph) ||
                other.currentFlowRateLph == currentFlowRateLph) &&
            (identical(other.currentPressureBar, currentPressureBar) ||
                other.currentPressureBar == currentPressureBar) &&
            (identical(other.endGunActive, endGunActive) ||
                other.endGunActive == endGunActive) &&
            (identical(other.cornerSystemActive, cornerSystemActive) ||
                other.cornerSystemActive == cornerSystemActive) &&
            (identical(other.waterAppliedM3, waterAppliedM3) ||
                other.waterAppliedM3 == waterAppliedM3) &&
            (identical(other.energyConsumedKwh, energyConsumedKwh) ||
                other.energyConsumedKwh == energyConsumedKwh) &&
            (identical(
                    other.estimatedCompletionTime, estimatedCompletionTime) ||
                other.estimatedCompletionTime == estimatedCompletionTime) &&
            (identical(other.lastUpdated, lastUpdated) ||
                other.lastUpdated == lastUpdated) &&
            const DeepCollectionEquality()
                .equals(other._activeAlerts, _activeAlerts) &&
            (identical(other.armEndLat, armEndLat) ||
                other.armEndLat == armEndLat) &&
            (identical(other.armEndLng, armEndLng) ||
                other.armEndLng == armEndLng));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      pivotId,
      currentAngle,
      operatingStatus,
      direction,
      speedPercent,
      timerHours,
      elapsedMinutes,
      currentFlowRateLph,
      currentPressureBar,
      endGunActive,
      cornerSystemActive,
      waterAppliedM3,
      energyConsumedKwh,
      estimatedCompletionTime,
      lastUpdated,
      const DeepCollectionEquality().hash(_activeAlerts),
      armEndLat,
      armEndLng);

  /// Create a copy of PivotStatus
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PivotStatusImplCopyWith<_$PivotStatusImpl> get copyWith =>
      __$$PivotStatusImplCopyWithImpl<_$PivotStatusImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PivotStatusImplToJson(
      this,
    );
  }
}

abstract class _PivotStatus implements PivotStatus {
  const factory _PivotStatus(
      {required final String pivotId,
      required final double currentAngle,
      required final PivotOperatingStatus operatingStatus,
      required final PivotDirection direction,
      required final double speedPercent,
      final double timerHours,
      final double elapsedMinutes,
      final double currentFlowRateLph,
      final double currentPressureBar,
      final bool endGunActive,
      final bool cornerSystemActive,
      final double waterAppliedM3,
      final double energyConsumedKwh,
      final DateTime? estimatedCompletionTime,
      required final DateTime lastUpdated,
      final List<PivotAlert> activeAlerts,
      final double? armEndLat,
      final double? armEndLng}) = _$PivotStatusImpl;

  factory _PivotStatus.fromJson(Map<String, dynamic> json) =
      _$PivotStatusImpl.fromJson;

  @override
  String get pivotId;

  /// Current angle position (0-360°) - الموقع الزاوي الحالي
  @override
  double get currentAngle;

  /// Operating status - حالة التشغيل
  @override
  PivotOperatingStatus get operatingStatus;

  /// Direction of movement - اتجاه الحركة
  @override
  PivotDirection get direction;

  /// Current speed percentage (0-100%) - السرعة الحالية
  @override
  double get speedPercent;

  /// Timer setting in hours - إعداد المؤقت
  @override
  double get timerHours;

  /// Elapsed time in minutes - الوقت المنقضي
  @override
  double get elapsedMinutes;

  /// Current flow rate L/h - معدل التدفق الحالي
  @override
  double get currentFlowRateLph;

  /// Current pressure (bar) - الضغط الحالي
  @override
  double get currentPressureBar;

  /// End gun status - حالة المدفع الطرفي
  @override
  bool get endGunActive;

  /// Corner system status - حالة نظام الزوايا
  @override
  bool get cornerSystemActive;

  /// Water applied this run (m³) - المياه المطبقة هذه الدورة
  @override
  double get waterAppliedM3;

  /// Energy consumed this run (kWh) - الطاقة المستهلكة
  @override
  double get energyConsumedKwh;

  /// Estimated completion time
  @override
  DateTime? get estimatedCompletionTime;

  /// Last update timestamp
  @override
  DateTime get lastUpdated;

  /// Active alerts - التنبيهات النشطة
  @override
  List<PivotAlert> get activeAlerts;

  /// GPS coordinates of pivot end (arm tip)
  @override
  double? get armEndLat;
  @override
  double? get armEndLng;

  /// Create a copy of PivotStatus
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PivotStatusImplCopyWith<_$PivotStatusImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PivotAlert _$PivotAlertFromJson(Map<String, dynamic> json) {
  return _PivotAlert.fromJson(json);
}

/// @nodoc
mixin _$PivotAlert {
  String get id => throw _privateConstructorUsedError;
  String get pivotId => throw _privateConstructorUsedError;

  /// Alert type - نوع التنبيه
  PivotAlertType get alertType => throw _privateConstructorUsedError;

  /// Severity level - مستوى الخطورة
  AlertSeverity get severity => throw _privateConstructorUsedError;

  /// Alert message
  String get message => throw _privateConstructorUsedError;
  String get messageAr => throw _privateConstructorUsedError;

  /// Tower/span number if applicable
  int? get towerNumber => throw _privateConstructorUsedError;

  /// Is alert acknowledged
  bool get isAcknowledged => throw _privateConstructorUsedError;

  /// Alert timestamp
  DateTime get timestamp => throw _privateConstructorUsedError;

  /// Resolution timestamp
  DateTime? get resolvedAt => throw _privateConstructorUsedError;

  /// Serializes this PivotAlert to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PivotAlert
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PivotAlertCopyWith<PivotAlert> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PivotAlertCopyWith<$Res> {
  factory $PivotAlertCopyWith(
          PivotAlert value, $Res Function(PivotAlert) then) =
      _$PivotAlertCopyWithImpl<$Res, PivotAlert>;
  @useResult
  $Res call(
      {String id,
      String pivotId,
      PivotAlertType alertType,
      AlertSeverity severity,
      String message,
      String messageAr,
      int? towerNumber,
      bool isAcknowledged,
      DateTime timestamp,
      DateTime? resolvedAt});
}

/// @nodoc
class _$PivotAlertCopyWithImpl<$Res, $Val extends PivotAlert>
    implements $PivotAlertCopyWith<$Res> {
  _$PivotAlertCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PivotAlert
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? pivotId = null,
    Object? alertType = null,
    Object? severity = null,
    Object? message = null,
    Object? messageAr = null,
    Object? towerNumber = freezed,
    Object? isAcknowledged = null,
    Object? timestamp = null,
    Object? resolvedAt = freezed,
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
      alertType: null == alertType
          ? _value.alertType
          : alertType // ignore: cast_nullable_to_non_nullable
              as PivotAlertType,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as AlertSeverity,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      messageAr: null == messageAr
          ? _value.messageAr
          : messageAr // ignore: cast_nullable_to_non_nullable
              as String,
      towerNumber: freezed == towerNumber
          ? _value.towerNumber
          : towerNumber // ignore: cast_nullable_to_non_nullable
              as int?,
      isAcknowledged: null == isAcknowledged
          ? _value.isAcknowledged
          : isAcknowledged // ignore: cast_nullable_to_non_nullable
              as bool,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      resolvedAt: freezed == resolvedAt
          ? _value.resolvedAt
          : resolvedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PivotAlertImplCopyWith<$Res>
    implements $PivotAlertCopyWith<$Res> {
  factory _$$PivotAlertImplCopyWith(
          _$PivotAlertImpl value, $Res Function(_$PivotAlertImpl) then) =
      __$$PivotAlertImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String pivotId,
      PivotAlertType alertType,
      AlertSeverity severity,
      String message,
      String messageAr,
      int? towerNumber,
      bool isAcknowledged,
      DateTime timestamp,
      DateTime? resolvedAt});
}

/// @nodoc
class __$$PivotAlertImplCopyWithImpl<$Res>
    extends _$PivotAlertCopyWithImpl<$Res, _$PivotAlertImpl>
    implements _$$PivotAlertImplCopyWith<$Res> {
  __$$PivotAlertImplCopyWithImpl(
      _$PivotAlertImpl _value, $Res Function(_$PivotAlertImpl) _then)
      : super(_value, _then);

  /// Create a copy of PivotAlert
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? pivotId = null,
    Object? alertType = null,
    Object? severity = null,
    Object? message = null,
    Object? messageAr = null,
    Object? towerNumber = freezed,
    Object? isAcknowledged = null,
    Object? timestamp = null,
    Object? resolvedAt = freezed,
  }) {
    return _then(_$PivotAlertImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      alertType: null == alertType
          ? _value.alertType
          : alertType // ignore: cast_nullable_to_non_nullable
              as PivotAlertType,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as AlertSeverity,
      message: null == message
          ? _value.message
          : message // ignore: cast_nullable_to_non_nullable
              as String,
      messageAr: null == messageAr
          ? _value.messageAr
          : messageAr // ignore: cast_nullable_to_non_nullable
              as String,
      towerNumber: freezed == towerNumber
          ? _value.towerNumber
          : towerNumber // ignore: cast_nullable_to_non_nullable
              as int?,
      isAcknowledged: null == isAcknowledged
          ? _value.isAcknowledged
          : isAcknowledged // ignore: cast_nullable_to_non_nullable
              as bool,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      resolvedAt: freezed == resolvedAt
          ? _value.resolvedAt
          : resolvedAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PivotAlertImpl implements _PivotAlert {
  const _$PivotAlertImpl(
      {required this.id,
      required this.pivotId,
      required this.alertType,
      required this.severity,
      required this.message,
      required this.messageAr,
      this.towerNumber,
      this.isAcknowledged = false,
      required this.timestamp,
      this.resolvedAt});

  factory _$PivotAlertImpl.fromJson(Map<String, dynamic> json) =>
      _$$PivotAlertImplFromJson(json);

  @override
  final String id;
  @override
  final String pivotId;

  /// Alert type - نوع التنبيه
  @override
  final PivotAlertType alertType;

  /// Severity level - مستوى الخطورة
  @override
  final AlertSeverity severity;

  /// Alert message
  @override
  final String message;
  @override
  final String messageAr;

  /// Tower/span number if applicable
  @override
  final int? towerNumber;

  /// Is alert acknowledged
  @override
  @JsonKey()
  final bool isAcknowledged;

  /// Alert timestamp
  @override
  final DateTime timestamp;

  /// Resolution timestamp
  @override
  final DateTime? resolvedAt;

  @override
  String toString() {
    return 'PivotAlert(id: $id, pivotId: $pivotId, alertType: $alertType, severity: $severity, message: $message, messageAr: $messageAr, towerNumber: $towerNumber, isAcknowledged: $isAcknowledged, timestamp: $timestamp, resolvedAt: $resolvedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PivotAlertImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.pivotId, pivotId) || other.pivotId == pivotId) &&
            (identical(other.alertType, alertType) ||
                other.alertType == alertType) &&
            (identical(other.severity, severity) ||
                other.severity == severity) &&
            (identical(other.message, message) || other.message == message) &&
            (identical(other.messageAr, messageAr) ||
                other.messageAr == messageAr) &&
            (identical(other.towerNumber, towerNumber) ||
                other.towerNumber == towerNumber) &&
            (identical(other.isAcknowledged, isAcknowledged) ||
                other.isAcknowledged == isAcknowledged) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.resolvedAt, resolvedAt) ||
                other.resolvedAt == resolvedAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(runtimeType, id, pivotId, alertType, severity,
      message, messageAr, towerNumber, isAcknowledged, timestamp, resolvedAt);

  /// Create a copy of PivotAlert
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PivotAlertImplCopyWith<_$PivotAlertImpl> get copyWith =>
      __$$PivotAlertImplCopyWithImpl<_$PivotAlertImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PivotAlertImplToJson(
      this,
    );
  }
}

abstract class _PivotAlert implements PivotAlert {
  const factory _PivotAlert(
      {required final String id,
      required final String pivotId,
      required final PivotAlertType alertType,
      required final AlertSeverity severity,
      required final String message,
      required final String messageAr,
      final int? towerNumber,
      final bool isAcknowledged,
      required final DateTime timestamp,
      final DateTime? resolvedAt}) = _$PivotAlertImpl;

  factory _PivotAlert.fromJson(Map<String, dynamic> json) =
      _$PivotAlertImpl.fromJson;

  @override
  String get id;
  @override
  String get pivotId;

  /// Alert type - نوع التنبيه
  @override
  PivotAlertType get alertType;

  /// Severity level - مستوى الخطورة
  @override
  AlertSeverity get severity;

  /// Alert message
  @override
  String get message;
  @override
  String get messageAr;

  /// Tower/span number if applicable
  @override
  int? get towerNumber;

  /// Is alert acknowledged
  @override
  bool get isAcknowledged;

  /// Alert timestamp
  @override
  DateTime get timestamp;

  /// Resolution timestamp
  @override
  DateTime? get resolvedAt;

  /// Create a copy of PivotAlert
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PivotAlertImplCopyWith<_$PivotAlertImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PivotSchedule _$PivotScheduleFromJson(Map<String, dynamic> json) {
  return _PivotSchedule.fromJson(json);
}

/// @nodoc
mixin _$PivotSchedule {
  String get id => throw _privateConstructorUsedError;
  String get pivotId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;

  /// Schedule type - نوع الجدول
  ScheduleType get scheduleType => throw _privateConstructorUsedError;

  /// List of scheduled runs
  List<ScheduledRun> get runs => throw _privateConstructorUsedError;

  /// Is schedule active
  bool get isActive => throw _privateConstructorUsedError;

  /// Created timestamp
  DateTime? get createdAt => throw _privateConstructorUsedError;

  /// Serializes this PivotSchedule to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PivotSchedule
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PivotScheduleCopyWith<PivotSchedule> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PivotScheduleCopyWith<$Res> {
  factory $PivotScheduleCopyWith(
          PivotSchedule value, $Res Function(PivotSchedule) then) =
      _$PivotScheduleCopyWithImpl<$Res, PivotSchedule>;
  @useResult
  $Res call(
      {String id,
      String pivotId,
      String name,
      String nameAr,
      ScheduleType scheduleType,
      List<ScheduledRun> runs,
      bool isActive,
      DateTime? createdAt});
}

/// @nodoc
class _$PivotScheduleCopyWithImpl<$Res, $Val extends PivotSchedule>
    implements $PivotScheduleCopyWith<$Res> {
  _$PivotScheduleCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PivotSchedule
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? pivotId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? scheduleType = null,
    Object? runs = null,
    Object? isActive = null,
    Object? createdAt = freezed,
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
      scheduleType: null == scheduleType
          ? _value.scheduleType
          : scheduleType // ignore: cast_nullable_to_non_nullable
              as ScheduleType,
      runs: null == runs
          ? _value.runs
          : runs // ignore: cast_nullable_to_non_nullable
              as List<ScheduledRun>,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PivotScheduleImplCopyWith<$Res>
    implements $PivotScheduleCopyWith<$Res> {
  factory _$$PivotScheduleImplCopyWith(
          _$PivotScheduleImpl value, $Res Function(_$PivotScheduleImpl) then) =
      __$$PivotScheduleImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String pivotId,
      String name,
      String nameAr,
      ScheduleType scheduleType,
      List<ScheduledRun> runs,
      bool isActive,
      DateTime? createdAt});
}

/// @nodoc
class __$$PivotScheduleImplCopyWithImpl<$Res>
    extends _$PivotScheduleCopyWithImpl<$Res, _$PivotScheduleImpl>
    implements _$$PivotScheduleImplCopyWith<$Res> {
  __$$PivotScheduleImplCopyWithImpl(
      _$PivotScheduleImpl _value, $Res Function(_$PivotScheduleImpl) _then)
      : super(_value, _then);

  /// Create a copy of PivotSchedule
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? pivotId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? scheduleType = null,
    Object? runs = null,
    Object? isActive = null,
    Object? createdAt = freezed,
  }) {
    return _then(_$PivotScheduleImpl(
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
      scheduleType: null == scheduleType
          ? _value.scheduleType
          : scheduleType // ignore: cast_nullable_to_non_nullable
              as ScheduleType,
      runs: null == runs
          ? _value._runs
          : runs // ignore: cast_nullable_to_non_nullable
              as List<ScheduledRun>,
      isActive: null == isActive
          ? _value.isActive
          : isActive // ignore: cast_nullable_to_non_nullable
              as bool,
      createdAt: freezed == createdAt
          ? _value.createdAt
          : createdAt // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PivotScheduleImpl implements _PivotSchedule {
  const _$PivotScheduleImpl(
      {required this.id,
      required this.pivotId,
      required this.name,
      this.nameAr = '',
      required this.scheduleType,
      required final List<ScheduledRun> runs,
      this.isActive = true,
      this.createdAt})
      : _runs = runs;

  factory _$PivotScheduleImpl.fromJson(Map<String, dynamic> json) =>
      _$$PivotScheduleImplFromJson(json);

  @override
  final String id;
  @override
  final String pivotId;
  @override
  final String name;
  @override
  @JsonKey()
  final String nameAr;

  /// Schedule type - نوع الجدول
  @override
  final ScheduleType scheduleType;

  /// List of scheduled runs
  final List<ScheduledRun> _runs;

  /// List of scheduled runs
  @override
  List<ScheduledRun> get runs {
    if (_runs is EqualUnmodifiableListView) return _runs;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_runs);
  }

  /// Is schedule active
  @override
  @JsonKey()
  final bool isActive;

  /// Created timestamp
  @override
  final DateTime? createdAt;

  @override
  String toString() {
    return 'PivotSchedule(id: $id, pivotId: $pivotId, name: $name, nameAr: $nameAr, scheduleType: $scheduleType, runs: $runs, isActive: $isActive, createdAt: $createdAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PivotScheduleImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.pivotId, pivotId) || other.pivotId == pivotId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.scheduleType, scheduleType) ||
                other.scheduleType == scheduleType) &&
            const DeepCollectionEquality().equals(other._runs, _runs) &&
            (identical(other.isActive, isActive) ||
                other.isActive == isActive) &&
            (identical(other.createdAt, createdAt) ||
                other.createdAt == createdAt));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      pivotId,
      name,
      nameAr,
      scheduleType,
      const DeepCollectionEquality().hash(_runs),
      isActive,
      createdAt);

  /// Create a copy of PivotSchedule
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PivotScheduleImplCopyWith<_$PivotScheduleImpl> get copyWith =>
      __$$PivotScheduleImplCopyWithImpl<_$PivotScheduleImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PivotScheduleImplToJson(
      this,
    );
  }
}

abstract class _PivotSchedule implements PivotSchedule {
  const factory _PivotSchedule(
      {required final String id,
      required final String pivotId,
      required final String name,
      final String nameAr,
      required final ScheduleType scheduleType,
      required final List<ScheduledRun> runs,
      final bool isActive,
      final DateTime? createdAt}) = _$PivotScheduleImpl;

  factory _PivotSchedule.fromJson(Map<String, dynamic> json) =
      _$PivotScheduleImpl.fromJson;

  @override
  String get id;
  @override
  String get pivotId;
  @override
  String get name;
  @override
  String get nameAr;

  /// Schedule type - نوع الجدول
  @override
  ScheduleType get scheduleType;

  /// List of scheduled runs
  @override
  List<ScheduledRun> get runs;

  /// Is schedule active
  @override
  bool get isActive;

  /// Created timestamp
  @override
  DateTime? get createdAt;

  /// Create a copy of PivotSchedule
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PivotScheduleImplCopyWith<_$PivotScheduleImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ScheduledRun _$ScheduledRunFromJson(Map<String, dynamic> json) {
  return _ScheduledRun.fromJson(json);
}

/// @nodoc
mixin _$ScheduledRun {
  String get id => throw _privateConstructorUsedError;

  /// Day of week (0=Sunday) for weekly schedules
  int? get dayOfWeek => throw _privateConstructorUsedError;

  /// Start time (HH:mm)
  String get startTime => throw _privateConstructorUsedError;

  /// Duration in hours
  double get durationHours => throw _privateConstructorUsedError;

  /// Speed percentage
  double get speedPercent => throw _privateConstructorUsedError;

  /// Direction
  PivotDirection get direction => throw _privateConstructorUsedError;

  /// Start angle (for partial runs)
  double get startAngle => throw _privateConstructorUsedError;

  /// End angle (for partial runs)
  double get endAngle => throw _privateConstructorUsedError;

  /// Apply irrigation depth in mm
  double get irrigationDepthMm => throw _privateConstructorUsedError;

  /// Is run enabled
  bool get isEnabled => throw _privateConstructorUsedError;

  /// Serializes this ScheduledRun to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of ScheduledRun
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $ScheduledRunCopyWith<ScheduledRun> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ScheduledRunCopyWith<$Res> {
  factory $ScheduledRunCopyWith(
          ScheduledRun value, $Res Function(ScheduledRun) then) =
      _$ScheduledRunCopyWithImpl<$Res, ScheduledRun>;
  @useResult
  $Res call(
      {String id,
      int? dayOfWeek,
      String startTime,
      double durationHours,
      double speedPercent,
      PivotDirection direction,
      double startAngle,
      double endAngle,
      double irrigationDepthMm,
      bool isEnabled});
}

/// @nodoc
class _$ScheduledRunCopyWithImpl<$Res, $Val extends ScheduledRun>
    implements $ScheduledRunCopyWith<$Res> {
  _$ScheduledRunCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of ScheduledRun
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? dayOfWeek = freezed,
    Object? startTime = null,
    Object? durationHours = null,
    Object? speedPercent = null,
    Object? direction = null,
    Object? startAngle = null,
    Object? endAngle = null,
    Object? irrigationDepthMm = null,
    Object? isEnabled = null,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      dayOfWeek: freezed == dayOfWeek
          ? _value.dayOfWeek
          : dayOfWeek // ignore: cast_nullable_to_non_nullable
              as int?,
      startTime: null == startTime
          ? _value.startTime
          : startTime // ignore: cast_nullable_to_non_nullable
              as String,
      durationHours: null == durationHours
          ? _value.durationHours
          : durationHours // ignore: cast_nullable_to_non_nullable
              as double,
      speedPercent: null == speedPercent
          ? _value.speedPercent
          : speedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      direction: null == direction
          ? _value.direction
          : direction // ignore: cast_nullable_to_non_nullable
              as PivotDirection,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: null == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationDepthMm: null == irrigationDepthMm
          ? _value.irrigationDepthMm
          : irrigationDepthMm // ignore: cast_nullable_to_non_nullable
              as double,
      isEnabled: null == isEnabled
          ? _value.isEnabled
          : isEnabled // ignore: cast_nullable_to_non_nullable
              as bool,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ScheduledRunImplCopyWith<$Res>
    implements $ScheduledRunCopyWith<$Res> {
  factory _$$ScheduledRunImplCopyWith(
          _$ScheduledRunImpl value, $Res Function(_$ScheduledRunImpl) then) =
      __$$ScheduledRunImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      int? dayOfWeek,
      String startTime,
      double durationHours,
      double speedPercent,
      PivotDirection direction,
      double startAngle,
      double endAngle,
      double irrigationDepthMm,
      bool isEnabled});
}

/// @nodoc
class __$$ScheduledRunImplCopyWithImpl<$Res>
    extends _$ScheduledRunCopyWithImpl<$Res, _$ScheduledRunImpl>
    implements _$$ScheduledRunImplCopyWith<$Res> {
  __$$ScheduledRunImplCopyWithImpl(
      _$ScheduledRunImpl _value, $Res Function(_$ScheduledRunImpl) _then)
      : super(_value, _then);

  /// Create a copy of ScheduledRun
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? dayOfWeek = freezed,
    Object? startTime = null,
    Object? durationHours = null,
    Object? speedPercent = null,
    Object? direction = null,
    Object? startAngle = null,
    Object? endAngle = null,
    Object? irrigationDepthMm = null,
    Object? isEnabled = null,
  }) {
    return _then(_$ScheduledRunImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      dayOfWeek: freezed == dayOfWeek
          ? _value.dayOfWeek
          : dayOfWeek // ignore: cast_nullable_to_non_nullable
              as int?,
      startTime: null == startTime
          ? _value.startTime
          : startTime // ignore: cast_nullable_to_non_nullable
              as String,
      durationHours: null == durationHours
          ? _value.durationHours
          : durationHours // ignore: cast_nullable_to_non_nullable
              as double,
      speedPercent: null == speedPercent
          ? _value.speedPercent
          : speedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      direction: null == direction
          ? _value.direction
          : direction // ignore: cast_nullable_to_non_nullable
              as PivotDirection,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: null == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationDepthMm: null == irrigationDepthMm
          ? _value.irrigationDepthMm
          : irrigationDepthMm // ignore: cast_nullable_to_non_nullable
              as double,
      isEnabled: null == isEnabled
          ? _value.isEnabled
          : isEnabled // ignore: cast_nullable_to_non_nullable
              as bool,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ScheduledRunImpl implements _ScheduledRun {
  const _$ScheduledRunImpl(
      {required this.id,
      this.dayOfWeek,
      required this.startTime,
      required this.durationHours,
      this.speedPercent = 100,
      this.direction = PivotDirection.forward,
      this.startAngle = 0,
      this.endAngle = 360,
      this.irrigationDepthMm = 25,
      this.isEnabled = true});

  factory _$ScheduledRunImpl.fromJson(Map<String, dynamic> json) =>
      _$$ScheduledRunImplFromJson(json);

  @override
  final String id;

  /// Day of week (0=Sunday) for weekly schedules
  @override
  final int? dayOfWeek;

  /// Start time (HH:mm)
  @override
  final String startTime;

  /// Duration in hours
  @override
  final double durationHours;

  /// Speed percentage
  @override
  @JsonKey()
  final double speedPercent;

  /// Direction
  @override
  @JsonKey()
  final PivotDirection direction;

  /// Start angle (for partial runs)
  @override
  @JsonKey()
  final double startAngle;

  /// End angle (for partial runs)
  @override
  @JsonKey()
  final double endAngle;

  /// Apply irrigation depth in mm
  @override
  @JsonKey()
  final double irrigationDepthMm;

  /// Is run enabled
  @override
  @JsonKey()
  final bool isEnabled;

  @override
  String toString() {
    return 'ScheduledRun(id: $id, dayOfWeek: $dayOfWeek, startTime: $startTime, durationHours: $durationHours, speedPercent: $speedPercent, direction: $direction, startAngle: $startAngle, endAngle: $endAngle, irrigationDepthMm: $irrigationDepthMm, isEnabled: $isEnabled)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ScheduledRunImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.dayOfWeek, dayOfWeek) ||
                other.dayOfWeek == dayOfWeek) &&
            (identical(other.startTime, startTime) ||
                other.startTime == startTime) &&
            (identical(other.durationHours, durationHours) ||
                other.durationHours == durationHours) &&
            (identical(other.speedPercent, speedPercent) ||
                other.speedPercent == speedPercent) &&
            (identical(other.direction, direction) ||
                other.direction == direction) &&
            (identical(other.startAngle, startAngle) ||
                other.startAngle == startAngle) &&
            (identical(other.endAngle, endAngle) ||
                other.endAngle == endAngle) &&
            (identical(other.irrigationDepthMm, irrigationDepthMm) ||
                other.irrigationDepthMm == irrigationDepthMm) &&
            (identical(other.isEnabled, isEnabled) ||
                other.isEnabled == isEnabled));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      dayOfWeek,
      startTime,
      durationHours,
      speedPercent,
      direction,
      startAngle,
      endAngle,
      irrigationDepthMm,
      isEnabled);

  /// Create a copy of ScheduledRun
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$ScheduledRunImplCopyWith<_$ScheduledRunImpl> get copyWith =>
      __$$ScheduledRunImplCopyWithImpl<_$ScheduledRunImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ScheduledRunImplToJson(
      this,
    );
  }
}

abstract class _ScheduledRun implements ScheduledRun {
  const factory _ScheduledRun(
      {required final String id,
      final int? dayOfWeek,
      required final String startTime,
      required final double durationHours,
      final double speedPercent,
      final PivotDirection direction,
      final double startAngle,
      final double endAngle,
      final double irrigationDepthMm,
      final bool isEnabled}) = _$ScheduledRunImpl;

  factory _ScheduledRun.fromJson(Map<String, dynamic> json) =
      _$ScheduledRunImpl.fromJson;

  @override
  String get id;

  /// Day of week (0=Sunday) for weekly schedules
  @override
  int? get dayOfWeek;

  /// Start time (HH:mm)
  @override
  String get startTime;

  /// Duration in hours
  @override
  double get durationHours;

  /// Speed percentage
  @override
  double get speedPercent;

  /// Direction
  @override
  PivotDirection get direction;

  /// Start angle (for partial runs)
  @override
  double get startAngle;

  /// End angle (for partial runs)
  @override
  double get endAngle;

  /// Apply irrigation depth in mm
  @override
  double get irrigationDepthMm;

  /// Is run enabled
  @override
  bool get isEnabled;

  /// Create a copy of ScheduledRun
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$ScheduledRunImplCopyWith<_$ScheduledRunImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PivotRunHistory _$PivotRunHistoryFromJson(Map<String, dynamic> json) {
  return _PivotRunHistory.fromJson(json);
}

/// @nodoc
mixin _$PivotRunHistory {
  String get id => throw _privateConstructorUsedError;
  String get pivotId => throw _privateConstructorUsedError;

  /// Run start time - وقت البداية
  DateTime get startTime => throw _privateConstructorUsedError;

  /// Run end time - وقت النهاية
  DateTime? get endTime => throw _privateConstructorUsedError;

  /// Start angle
  double get startAngle => throw _privateConstructorUsedError;

  /// End angle
  double? get endAngle => throw _privateConstructorUsedError;

  /// Direction
  PivotDirection get direction => throw _privateConstructorUsedError;

  /// Average speed percent
  double get avgSpeedPercent => throw _privateConstructorUsedError;

  /// Total water applied (m³) - إجمالي المياه
  double get waterAppliedM3 => throw _privateConstructorUsedError;

  /// Energy consumed (kWh) - الطاقة المستهلكة
  double get energyConsumedKwh => throw _privateConstructorUsedError;

  /// Run status - حالة الدورة
  RunStatus get status => throw _privateConstructorUsedError;

  /// Stop reason if stopped early
  String? get stopReason => throw _privateConstructorUsedError;

  /// Alerts during run
  List<PivotAlert> get alerts => throw _privateConstructorUsedError;

  /// Serializes this PivotRunHistory to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PivotRunHistory
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PivotRunHistoryCopyWith<PivotRunHistory> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PivotRunHistoryCopyWith<$Res> {
  factory $PivotRunHistoryCopyWith(
          PivotRunHistory value, $Res Function(PivotRunHistory) then) =
      _$PivotRunHistoryCopyWithImpl<$Res, PivotRunHistory>;
  @useResult
  $Res call(
      {String id,
      String pivotId,
      DateTime startTime,
      DateTime? endTime,
      double startAngle,
      double? endAngle,
      PivotDirection direction,
      double avgSpeedPercent,
      double waterAppliedM3,
      double energyConsumedKwh,
      RunStatus status,
      String? stopReason,
      List<PivotAlert> alerts});
}

/// @nodoc
class _$PivotRunHistoryCopyWithImpl<$Res, $Val extends PivotRunHistory>
    implements $PivotRunHistoryCopyWith<$Res> {
  _$PivotRunHistoryCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PivotRunHistory
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? pivotId = null,
    Object? startTime = null,
    Object? endTime = freezed,
    Object? startAngle = null,
    Object? endAngle = freezed,
    Object? direction = null,
    Object? avgSpeedPercent = null,
    Object? waterAppliedM3 = null,
    Object? energyConsumedKwh = null,
    Object? status = null,
    Object? stopReason = freezed,
    Object? alerts = null,
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
      startTime: null == startTime
          ? _value.startTime
          : startTime // ignore: cast_nullable_to_non_nullable
              as DateTime,
      endTime: freezed == endTime
          ? _value.endTime
          : endTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: freezed == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double?,
      direction: null == direction
          ? _value.direction
          : direction // ignore: cast_nullable_to_non_nullable
              as PivotDirection,
      avgSpeedPercent: null == avgSpeedPercent
          ? _value.avgSpeedPercent
          : avgSpeedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      waterAppliedM3: null == waterAppliedM3
          ? _value.waterAppliedM3
          : waterAppliedM3 // ignore: cast_nullable_to_non_nullable
              as double,
      energyConsumedKwh: null == energyConsumedKwh
          ? _value.energyConsumedKwh
          : energyConsumedKwh // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as RunStatus,
      stopReason: freezed == stopReason
          ? _value.stopReason
          : stopReason // ignore: cast_nullable_to_non_nullable
              as String?,
      alerts: null == alerts
          ? _value.alerts
          : alerts // ignore: cast_nullable_to_non_nullable
              as List<PivotAlert>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PivotRunHistoryImplCopyWith<$Res>
    implements $PivotRunHistoryCopyWith<$Res> {
  factory _$$PivotRunHistoryImplCopyWith(_$PivotRunHistoryImpl value,
          $Res Function(_$PivotRunHistoryImpl) then) =
      __$$PivotRunHistoryImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String pivotId,
      DateTime startTime,
      DateTime? endTime,
      double startAngle,
      double? endAngle,
      PivotDirection direction,
      double avgSpeedPercent,
      double waterAppliedM3,
      double energyConsumedKwh,
      RunStatus status,
      String? stopReason,
      List<PivotAlert> alerts});
}

/// @nodoc
class __$$PivotRunHistoryImplCopyWithImpl<$Res>
    extends _$PivotRunHistoryCopyWithImpl<$Res, _$PivotRunHistoryImpl>
    implements _$$PivotRunHistoryImplCopyWith<$Res> {
  __$$PivotRunHistoryImplCopyWithImpl(
      _$PivotRunHistoryImpl _value, $Res Function(_$PivotRunHistoryImpl) _then)
      : super(_value, _then);

  /// Create a copy of PivotRunHistory
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? pivotId = null,
    Object? startTime = null,
    Object? endTime = freezed,
    Object? startAngle = null,
    Object? endAngle = freezed,
    Object? direction = null,
    Object? avgSpeedPercent = null,
    Object? waterAppliedM3 = null,
    Object? energyConsumedKwh = null,
    Object? status = null,
    Object? stopReason = freezed,
    Object? alerts = null,
  }) {
    return _then(_$PivotRunHistoryImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      startTime: null == startTime
          ? _value.startTime
          : startTime // ignore: cast_nullable_to_non_nullable
              as DateTime,
      endTime: freezed == endTime
          ? _value.endTime
          : endTime // ignore: cast_nullable_to_non_nullable
              as DateTime?,
      startAngle: null == startAngle
          ? _value.startAngle
          : startAngle // ignore: cast_nullable_to_non_nullable
              as double,
      endAngle: freezed == endAngle
          ? _value.endAngle
          : endAngle // ignore: cast_nullable_to_non_nullable
              as double?,
      direction: null == direction
          ? _value.direction
          : direction // ignore: cast_nullable_to_non_nullable
              as PivotDirection,
      avgSpeedPercent: null == avgSpeedPercent
          ? _value.avgSpeedPercent
          : avgSpeedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      waterAppliedM3: null == waterAppliedM3
          ? _value.waterAppliedM3
          : waterAppliedM3 // ignore: cast_nullable_to_non_nullable
              as double,
      energyConsumedKwh: null == energyConsumedKwh
          ? _value.energyConsumedKwh
          : energyConsumedKwh // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as RunStatus,
      stopReason: freezed == stopReason
          ? _value.stopReason
          : stopReason // ignore: cast_nullable_to_non_nullable
              as String?,
      alerts: null == alerts
          ? _value._alerts
          : alerts // ignore: cast_nullable_to_non_nullable
              as List<PivotAlert>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PivotRunHistoryImpl implements _PivotRunHistory {
  const _$PivotRunHistoryImpl(
      {required this.id,
      required this.pivotId,
      required this.startTime,
      this.endTime,
      required this.startAngle,
      this.endAngle,
      required this.direction,
      required this.avgSpeedPercent,
      required this.waterAppliedM3,
      this.energyConsumedKwh = 0,
      required this.status,
      this.stopReason,
      final List<PivotAlert> alerts = const []})
      : _alerts = alerts;

  factory _$PivotRunHistoryImpl.fromJson(Map<String, dynamic> json) =>
      _$$PivotRunHistoryImplFromJson(json);

  @override
  final String id;
  @override
  final String pivotId;

  /// Run start time - وقت البداية
  @override
  final DateTime startTime;

  /// Run end time - وقت النهاية
  @override
  final DateTime? endTime;

  /// Start angle
  @override
  final double startAngle;

  /// End angle
  @override
  final double? endAngle;

  /// Direction
  @override
  final PivotDirection direction;

  /// Average speed percent
  @override
  final double avgSpeedPercent;

  /// Total water applied (m³) - إجمالي المياه
  @override
  final double waterAppliedM3;

  /// Energy consumed (kWh) - الطاقة المستهلكة
  @override
  @JsonKey()
  final double energyConsumedKwh;

  /// Run status - حالة الدورة
  @override
  final RunStatus status;

  /// Stop reason if stopped early
  @override
  final String? stopReason;

  /// Alerts during run
  final List<PivotAlert> _alerts;

  /// Alerts during run
  @override
  @JsonKey()
  List<PivotAlert> get alerts {
    if (_alerts is EqualUnmodifiableListView) return _alerts;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_alerts);
  }

  @override
  String toString() {
    return 'PivotRunHistory(id: $id, pivotId: $pivotId, startTime: $startTime, endTime: $endTime, startAngle: $startAngle, endAngle: $endAngle, direction: $direction, avgSpeedPercent: $avgSpeedPercent, waterAppliedM3: $waterAppliedM3, energyConsumedKwh: $energyConsumedKwh, status: $status, stopReason: $stopReason, alerts: $alerts)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PivotRunHistoryImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.pivotId, pivotId) || other.pivotId == pivotId) &&
            (identical(other.startTime, startTime) ||
                other.startTime == startTime) &&
            (identical(other.endTime, endTime) || other.endTime == endTime) &&
            (identical(other.startAngle, startAngle) ||
                other.startAngle == startAngle) &&
            (identical(other.endAngle, endAngle) ||
                other.endAngle == endAngle) &&
            (identical(other.direction, direction) ||
                other.direction == direction) &&
            (identical(other.avgSpeedPercent, avgSpeedPercent) ||
                other.avgSpeedPercent == avgSpeedPercent) &&
            (identical(other.waterAppliedM3, waterAppliedM3) ||
                other.waterAppliedM3 == waterAppliedM3) &&
            (identical(other.energyConsumedKwh, energyConsumedKwh) ||
                other.energyConsumedKwh == energyConsumedKwh) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.stopReason, stopReason) ||
                other.stopReason == stopReason) &&
            const DeepCollectionEquality().equals(other._alerts, _alerts));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      pivotId,
      startTime,
      endTime,
      startAngle,
      endAngle,
      direction,
      avgSpeedPercent,
      waterAppliedM3,
      energyConsumedKwh,
      status,
      stopReason,
      const DeepCollectionEquality().hash(_alerts));

  /// Create a copy of PivotRunHistory
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PivotRunHistoryImplCopyWith<_$PivotRunHistoryImpl> get copyWith =>
      __$$PivotRunHistoryImplCopyWithImpl<_$PivotRunHistoryImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PivotRunHistoryImplToJson(
      this,
    );
  }
}

abstract class _PivotRunHistory implements PivotRunHistory {
  const factory _PivotRunHistory(
      {required final String id,
      required final String pivotId,
      required final DateTime startTime,
      final DateTime? endTime,
      required final double startAngle,
      final double? endAngle,
      required final PivotDirection direction,
      required final double avgSpeedPercent,
      required final double waterAppliedM3,
      final double energyConsumedKwh,
      required final RunStatus status,
      final String? stopReason,
      final List<PivotAlert> alerts}) = _$PivotRunHistoryImpl;

  factory _PivotRunHistory.fromJson(Map<String, dynamic> json) =
      _$PivotRunHistoryImpl.fromJson;

  @override
  String get id;
  @override
  String get pivotId;

  /// Run start time - وقت البداية
  @override
  DateTime get startTime;

  /// Run end time - وقت النهاية
  @override
  DateTime? get endTime;

  /// Start angle
  @override
  double get startAngle;

  /// End angle
  @override
  double? get endAngle;

  /// Direction
  @override
  PivotDirection get direction;

  /// Average speed percent
  @override
  double get avgSpeedPercent;

  /// Total water applied (m³) - إجمالي المياه
  @override
  double get waterAppliedM3;

  /// Energy consumed (kWh) - الطاقة المستهلكة
  @override
  double get energyConsumedKwh;

  /// Run status - حالة الدورة
  @override
  RunStatus get status;

  /// Stop reason if stopped early
  @override
  String? get stopReason;

  /// Alerts during run
  @override
  List<PivotAlert> get alerts;

  /// Create a copy of PivotRunHistory
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PivotRunHistoryImplCopyWith<_$PivotRunHistoryImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PivotStatistics _$PivotStatisticsFromJson(Map<String, dynamic> json) {
  return _PivotStatistics.fromJson(json);
}

/// @nodoc
mixin _$PivotStatistics {
  String get pivotId => throw _privateConstructorUsedError;
  String get period =>
      throw _privateConstructorUsedError; // daily, weekly, monthly, seasonal
  /// Total water applied (m³) - إجمالي المياه
  double get totalWaterM3 => throw _privateConstructorUsedError;

  /// Total energy consumed (kWh) - إجمالي الطاقة
  double get totalEnergyKwh => throw _privateConstructorUsedError;

  /// Total run time (hours) - إجمالي وقت التشغيل
  double get totalRunHours => throw _privateConstructorUsedError;

  /// Number of complete circles - عدد الدورات الكاملة
  int get completeCircles => throw _privateConstructorUsedError;

  /// Average irrigation depth (mm) - متوسط عمق الري
  double get avgIrrigationDepthMm => throw _privateConstructorUsedError;

  /// Average speed percent
  double get avgSpeedPercent => throw _privateConstructorUsedError;

  /// Efficiency percentage - كفاءة الري
  double get efficiencyPercent => throw _privateConstructorUsedError;

  /// Water cost (currency) - تكلفة المياه
  double get waterCost => throw _privateConstructorUsedError;

  /// Energy cost (currency) - تكلفة الطاقة
  double get energyCost => throw _privateConstructorUsedError;

  /// Number of faults - عدد الأعطال
  int get faultCount => throw _privateConstructorUsedError;

  /// Downtime hours - ساعات التوقف
  double get downtimeHours => throw _privateConstructorUsedError;

  /// Period start date
  DateTime get periodStart => throw _privateConstructorUsedError;

  /// Period end date
  DateTime get periodEnd => throw _privateConstructorUsedError;

  /// Serializes this PivotStatistics to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PivotStatistics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PivotStatisticsCopyWith<PivotStatistics> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PivotStatisticsCopyWith<$Res> {
  factory $PivotStatisticsCopyWith(
          PivotStatistics value, $Res Function(PivotStatistics) then) =
      _$PivotStatisticsCopyWithImpl<$Res, PivotStatistics>;
  @useResult
  $Res call(
      {String pivotId,
      String period,
      double totalWaterM3,
      double totalEnergyKwh,
      double totalRunHours,
      int completeCircles,
      double avgIrrigationDepthMm,
      double avgSpeedPercent,
      double efficiencyPercent,
      double waterCost,
      double energyCost,
      int faultCount,
      double downtimeHours,
      DateTime periodStart,
      DateTime periodEnd});
}

/// @nodoc
class _$PivotStatisticsCopyWithImpl<$Res, $Val extends PivotStatistics>
    implements $PivotStatisticsCopyWith<$Res> {
  _$PivotStatisticsCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PivotStatistics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pivotId = null,
    Object? period = null,
    Object? totalWaterM3 = null,
    Object? totalEnergyKwh = null,
    Object? totalRunHours = null,
    Object? completeCircles = null,
    Object? avgIrrigationDepthMm = null,
    Object? avgSpeedPercent = null,
    Object? efficiencyPercent = null,
    Object? waterCost = null,
    Object? energyCost = null,
    Object? faultCount = null,
    Object? downtimeHours = null,
    Object? periodStart = null,
    Object? periodEnd = null,
  }) {
    return _then(_value.copyWith(
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      period: null == period
          ? _value.period
          : period // ignore: cast_nullable_to_non_nullable
              as String,
      totalWaterM3: null == totalWaterM3
          ? _value.totalWaterM3
          : totalWaterM3 // ignore: cast_nullable_to_non_nullable
              as double,
      totalEnergyKwh: null == totalEnergyKwh
          ? _value.totalEnergyKwh
          : totalEnergyKwh // ignore: cast_nullable_to_non_nullable
              as double,
      totalRunHours: null == totalRunHours
          ? _value.totalRunHours
          : totalRunHours // ignore: cast_nullable_to_non_nullable
              as double,
      completeCircles: null == completeCircles
          ? _value.completeCircles
          : completeCircles // ignore: cast_nullable_to_non_nullable
              as int,
      avgIrrigationDepthMm: null == avgIrrigationDepthMm
          ? _value.avgIrrigationDepthMm
          : avgIrrigationDepthMm // ignore: cast_nullable_to_non_nullable
              as double,
      avgSpeedPercent: null == avgSpeedPercent
          ? _value.avgSpeedPercent
          : avgSpeedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      efficiencyPercent: null == efficiencyPercent
          ? _value.efficiencyPercent
          : efficiencyPercent // ignore: cast_nullable_to_non_nullable
              as double,
      waterCost: null == waterCost
          ? _value.waterCost
          : waterCost // ignore: cast_nullable_to_non_nullable
              as double,
      energyCost: null == energyCost
          ? _value.energyCost
          : energyCost // ignore: cast_nullable_to_non_nullable
              as double,
      faultCount: null == faultCount
          ? _value.faultCount
          : faultCount // ignore: cast_nullable_to_non_nullable
              as int,
      downtimeHours: null == downtimeHours
          ? _value.downtimeHours
          : downtimeHours // ignore: cast_nullable_to_non_nullable
              as double,
      periodStart: null == periodStart
          ? _value.periodStart
          : periodStart // ignore: cast_nullable_to_non_nullable
              as DateTime,
      periodEnd: null == periodEnd
          ? _value.periodEnd
          : periodEnd // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PivotStatisticsImplCopyWith<$Res>
    implements $PivotStatisticsCopyWith<$Res> {
  factory _$$PivotStatisticsImplCopyWith(_$PivotStatisticsImpl value,
          $Res Function(_$PivotStatisticsImpl) then) =
      __$$PivotStatisticsImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String pivotId,
      String period,
      double totalWaterM3,
      double totalEnergyKwh,
      double totalRunHours,
      int completeCircles,
      double avgIrrigationDepthMm,
      double avgSpeedPercent,
      double efficiencyPercent,
      double waterCost,
      double energyCost,
      int faultCount,
      double downtimeHours,
      DateTime periodStart,
      DateTime periodEnd});
}

/// @nodoc
class __$$PivotStatisticsImplCopyWithImpl<$Res>
    extends _$PivotStatisticsCopyWithImpl<$Res, _$PivotStatisticsImpl>
    implements _$$PivotStatisticsImplCopyWith<$Res> {
  __$$PivotStatisticsImplCopyWithImpl(
      _$PivotStatisticsImpl _value, $Res Function(_$PivotStatisticsImpl) _then)
      : super(_value, _then);

  /// Create a copy of PivotStatistics
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pivotId = null,
    Object? period = null,
    Object? totalWaterM3 = null,
    Object? totalEnergyKwh = null,
    Object? totalRunHours = null,
    Object? completeCircles = null,
    Object? avgIrrigationDepthMm = null,
    Object? avgSpeedPercent = null,
    Object? efficiencyPercent = null,
    Object? waterCost = null,
    Object? energyCost = null,
    Object? faultCount = null,
    Object? downtimeHours = null,
    Object? periodStart = null,
    Object? periodEnd = null,
  }) {
    return _then(_$PivotStatisticsImpl(
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      period: null == period
          ? _value.period
          : period // ignore: cast_nullable_to_non_nullable
              as String,
      totalWaterM3: null == totalWaterM3
          ? _value.totalWaterM3
          : totalWaterM3 // ignore: cast_nullable_to_non_nullable
              as double,
      totalEnergyKwh: null == totalEnergyKwh
          ? _value.totalEnergyKwh
          : totalEnergyKwh // ignore: cast_nullable_to_non_nullable
              as double,
      totalRunHours: null == totalRunHours
          ? _value.totalRunHours
          : totalRunHours // ignore: cast_nullable_to_non_nullable
              as double,
      completeCircles: null == completeCircles
          ? _value.completeCircles
          : completeCircles // ignore: cast_nullable_to_non_nullable
              as int,
      avgIrrigationDepthMm: null == avgIrrigationDepthMm
          ? _value.avgIrrigationDepthMm
          : avgIrrigationDepthMm // ignore: cast_nullable_to_non_nullable
              as double,
      avgSpeedPercent: null == avgSpeedPercent
          ? _value.avgSpeedPercent
          : avgSpeedPercent // ignore: cast_nullable_to_non_nullable
              as double,
      efficiencyPercent: null == efficiencyPercent
          ? _value.efficiencyPercent
          : efficiencyPercent // ignore: cast_nullable_to_non_nullable
              as double,
      waterCost: null == waterCost
          ? _value.waterCost
          : waterCost // ignore: cast_nullable_to_non_nullable
              as double,
      energyCost: null == energyCost
          ? _value.energyCost
          : energyCost // ignore: cast_nullable_to_non_nullable
              as double,
      faultCount: null == faultCount
          ? _value.faultCount
          : faultCount // ignore: cast_nullable_to_non_nullable
              as int,
      downtimeHours: null == downtimeHours
          ? _value.downtimeHours
          : downtimeHours // ignore: cast_nullable_to_non_nullable
              as double,
      periodStart: null == periodStart
          ? _value.periodStart
          : periodStart // ignore: cast_nullable_to_non_nullable
              as DateTime,
      periodEnd: null == periodEnd
          ? _value.periodEnd
          : periodEnd // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PivotStatisticsImpl implements _PivotStatistics {
  const _$PivotStatisticsImpl(
      {required this.pivotId,
      required this.period,
      required this.totalWaterM3,
      required this.totalEnergyKwh,
      required this.totalRunHours,
      required this.completeCircles,
      required this.avgIrrigationDepthMm,
      required this.avgSpeedPercent,
      required this.efficiencyPercent,
      this.waterCost = 0,
      this.energyCost = 0,
      this.faultCount = 0,
      this.downtimeHours = 0,
      required this.periodStart,
      required this.periodEnd});

  factory _$PivotStatisticsImpl.fromJson(Map<String, dynamic> json) =>
      _$$PivotStatisticsImplFromJson(json);

  @override
  final String pivotId;
  @override
  final String period;
// daily, weekly, monthly, seasonal
  /// Total water applied (m³) - إجمالي المياه
  @override
  final double totalWaterM3;

  /// Total energy consumed (kWh) - إجمالي الطاقة
  @override
  final double totalEnergyKwh;

  /// Total run time (hours) - إجمالي وقت التشغيل
  @override
  final double totalRunHours;

  /// Number of complete circles - عدد الدورات الكاملة
  @override
  final int completeCircles;

  /// Average irrigation depth (mm) - متوسط عمق الري
  @override
  final double avgIrrigationDepthMm;

  /// Average speed percent
  @override
  final double avgSpeedPercent;

  /// Efficiency percentage - كفاءة الري
  @override
  final double efficiencyPercent;

  /// Water cost (currency) - تكلفة المياه
  @override
  @JsonKey()
  final double waterCost;

  /// Energy cost (currency) - تكلفة الطاقة
  @override
  @JsonKey()
  final double energyCost;

  /// Number of faults - عدد الأعطال
  @override
  @JsonKey()
  final int faultCount;

  /// Downtime hours - ساعات التوقف
  @override
  @JsonKey()
  final double downtimeHours;

  /// Period start date
  @override
  final DateTime periodStart;

  /// Period end date
  @override
  final DateTime periodEnd;

  @override
  String toString() {
    return 'PivotStatistics(pivotId: $pivotId, period: $period, totalWaterM3: $totalWaterM3, totalEnergyKwh: $totalEnergyKwh, totalRunHours: $totalRunHours, completeCircles: $completeCircles, avgIrrigationDepthMm: $avgIrrigationDepthMm, avgSpeedPercent: $avgSpeedPercent, efficiencyPercent: $efficiencyPercent, waterCost: $waterCost, energyCost: $energyCost, faultCount: $faultCount, downtimeHours: $downtimeHours, periodStart: $periodStart, periodEnd: $periodEnd)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PivotStatisticsImpl &&
            (identical(other.pivotId, pivotId) || other.pivotId == pivotId) &&
            (identical(other.period, period) || other.period == period) &&
            (identical(other.totalWaterM3, totalWaterM3) ||
                other.totalWaterM3 == totalWaterM3) &&
            (identical(other.totalEnergyKwh, totalEnergyKwh) ||
                other.totalEnergyKwh == totalEnergyKwh) &&
            (identical(other.totalRunHours, totalRunHours) ||
                other.totalRunHours == totalRunHours) &&
            (identical(other.completeCircles, completeCircles) ||
                other.completeCircles == completeCircles) &&
            (identical(other.avgIrrigationDepthMm, avgIrrigationDepthMm) ||
                other.avgIrrigationDepthMm == avgIrrigationDepthMm) &&
            (identical(other.avgSpeedPercent, avgSpeedPercent) ||
                other.avgSpeedPercent == avgSpeedPercent) &&
            (identical(other.efficiencyPercent, efficiencyPercent) ||
                other.efficiencyPercent == efficiencyPercent) &&
            (identical(other.waterCost, waterCost) ||
                other.waterCost == waterCost) &&
            (identical(other.energyCost, energyCost) ||
                other.energyCost == energyCost) &&
            (identical(other.faultCount, faultCount) ||
                other.faultCount == faultCount) &&
            (identical(other.downtimeHours, downtimeHours) ||
                other.downtimeHours == downtimeHours) &&
            (identical(other.periodStart, periodStart) ||
                other.periodStart == periodStart) &&
            (identical(other.periodEnd, periodEnd) ||
                other.periodEnd == periodEnd));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      pivotId,
      period,
      totalWaterM3,
      totalEnergyKwh,
      totalRunHours,
      completeCircles,
      avgIrrigationDepthMm,
      avgSpeedPercent,
      efficiencyPercent,
      waterCost,
      energyCost,
      faultCount,
      downtimeHours,
      periodStart,
      periodEnd);

  /// Create a copy of PivotStatistics
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PivotStatisticsImplCopyWith<_$PivotStatisticsImpl> get copyWith =>
      __$$PivotStatisticsImplCopyWithImpl<_$PivotStatisticsImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PivotStatisticsImplToJson(
      this,
    );
  }
}

abstract class _PivotStatistics implements PivotStatistics {
  const factory _PivotStatistics(
      {required final String pivotId,
      required final String period,
      required final double totalWaterM3,
      required final double totalEnergyKwh,
      required final double totalRunHours,
      required final int completeCircles,
      required final double avgIrrigationDepthMm,
      required final double avgSpeedPercent,
      required final double efficiencyPercent,
      final double waterCost,
      final double energyCost,
      final int faultCount,
      final double downtimeHours,
      required final DateTime periodStart,
      required final DateTime periodEnd}) = _$PivotStatisticsImpl;

  factory _PivotStatistics.fromJson(Map<String, dynamic> json) =
      _$PivotStatisticsImpl.fromJson;

  @override
  String get pivotId;
  @override
  String get period; // daily, weekly, monthly, seasonal
  /// Total water applied (m³) - إجمالي المياه
  @override
  double get totalWaterM3;

  /// Total energy consumed (kWh) - إجمالي الطاقة
  @override
  double get totalEnergyKwh;

  /// Total run time (hours) - إجمالي وقت التشغيل
  @override
  double get totalRunHours;

  /// Number of complete circles - عدد الدورات الكاملة
  @override
  int get completeCircles;

  /// Average irrigation depth (mm) - متوسط عمق الري
  @override
  double get avgIrrigationDepthMm;

  /// Average speed percent
  @override
  double get avgSpeedPercent;

  /// Efficiency percentage - كفاءة الري
  @override
  double get efficiencyPercent;

  /// Water cost (currency) - تكلفة المياه
  @override
  double get waterCost;

  /// Energy cost (currency) - تكلفة الطاقة
  @override
  double get energyCost;

  /// Number of faults - عدد الأعطال
  @override
  int get faultCount;

  /// Downtime hours - ساعات التوقف
  @override
  double get downtimeHours;

  /// Period start date
  @override
  DateTime get periodStart;

  /// Period end date
  @override
  DateTime get periodEnd;

  /// Create a copy of PivotStatistics
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PivotStatisticsImplCopyWith<_$PivotStatisticsImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

PivotControlCommand _$PivotControlCommandFromJson(Map<String, dynamic> json) {
  return _PivotControlCommand.fromJson(json);
}

/// @nodoc
mixin _$PivotControlCommand {
  String get pivotId => throw _privateConstructorUsedError;
  PivotCommandType get commandType => throw _privateConstructorUsedError;

  /// Target speed percent (for speed commands)
  double? get speedPercent => throw _privateConstructorUsedError;

  /// Target angle (for move-to commands)
  double? get targetAngle => throw _privateConstructorUsedError;

  /// Direction (for direction commands)
  PivotDirection? get direction => throw _privateConstructorUsedError;

  /// End gun setting
  bool? get endGunEnabled => throw _privateConstructorUsedError;

  /// Timer hours (for timer commands)
  double? get timerHours => throw _privateConstructorUsedError;

  /// Sector numbers to enable/disable
  List<int>? get sectorNumbers => throw _privateConstructorUsedError;

  /// Command issued by user ID
  String get issuedBy => throw _privateConstructorUsedError;

  /// Timestamp
  DateTime get timestamp => throw _privateConstructorUsedError;

  /// Serializes this PivotControlCommand to a JSON map.
  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;

  /// Create a copy of PivotControlCommand
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  $PivotControlCommandCopyWith<PivotControlCommand> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $PivotControlCommandCopyWith<$Res> {
  factory $PivotControlCommandCopyWith(
          PivotControlCommand value, $Res Function(PivotControlCommand) then) =
      _$PivotControlCommandCopyWithImpl<$Res, PivotControlCommand>;
  @useResult
  $Res call(
      {String pivotId,
      PivotCommandType commandType,
      double? speedPercent,
      double? targetAngle,
      PivotDirection? direction,
      bool? endGunEnabled,
      double? timerHours,
      List<int>? sectorNumbers,
      String issuedBy,
      DateTime timestamp});
}

/// @nodoc
class _$PivotControlCommandCopyWithImpl<$Res, $Val extends PivotControlCommand>
    implements $PivotControlCommandCopyWith<$Res> {
  _$PivotControlCommandCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  /// Create a copy of PivotControlCommand
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pivotId = null,
    Object? commandType = null,
    Object? speedPercent = freezed,
    Object? targetAngle = freezed,
    Object? direction = freezed,
    Object? endGunEnabled = freezed,
    Object? timerHours = freezed,
    Object? sectorNumbers = freezed,
    Object? issuedBy = null,
    Object? timestamp = null,
  }) {
    return _then(_value.copyWith(
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      commandType: null == commandType
          ? _value.commandType
          : commandType // ignore: cast_nullable_to_non_nullable
              as PivotCommandType,
      speedPercent: freezed == speedPercent
          ? _value.speedPercent
          : speedPercent // ignore: cast_nullable_to_non_nullable
              as double?,
      targetAngle: freezed == targetAngle
          ? _value.targetAngle
          : targetAngle // ignore: cast_nullable_to_non_nullable
              as double?,
      direction: freezed == direction
          ? _value.direction
          : direction // ignore: cast_nullable_to_non_nullable
              as PivotDirection?,
      endGunEnabled: freezed == endGunEnabled
          ? _value.endGunEnabled
          : endGunEnabled // ignore: cast_nullable_to_non_nullable
              as bool?,
      timerHours: freezed == timerHours
          ? _value.timerHours
          : timerHours // ignore: cast_nullable_to_non_nullable
              as double?,
      sectorNumbers: freezed == sectorNumbers
          ? _value.sectorNumbers
          : sectorNumbers // ignore: cast_nullable_to_non_nullable
              as List<int>?,
      issuedBy: null == issuedBy
          ? _value.issuedBy
          : issuedBy // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$PivotControlCommandImplCopyWith<$Res>
    implements $PivotControlCommandCopyWith<$Res> {
  factory _$$PivotControlCommandImplCopyWith(_$PivotControlCommandImpl value,
          $Res Function(_$PivotControlCommandImpl) then) =
      __$$PivotControlCommandImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String pivotId,
      PivotCommandType commandType,
      double? speedPercent,
      double? targetAngle,
      PivotDirection? direction,
      bool? endGunEnabled,
      double? timerHours,
      List<int>? sectorNumbers,
      String issuedBy,
      DateTime timestamp});
}

/// @nodoc
class __$$PivotControlCommandImplCopyWithImpl<$Res>
    extends _$PivotControlCommandCopyWithImpl<$Res, _$PivotControlCommandImpl>
    implements _$$PivotControlCommandImplCopyWith<$Res> {
  __$$PivotControlCommandImplCopyWithImpl(_$PivotControlCommandImpl _value,
      $Res Function(_$PivotControlCommandImpl) _then)
      : super(_value, _then);

  /// Create a copy of PivotControlCommand
  /// with the given fields replaced by the non-null parameter values.
  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? pivotId = null,
    Object? commandType = null,
    Object? speedPercent = freezed,
    Object? targetAngle = freezed,
    Object? direction = freezed,
    Object? endGunEnabled = freezed,
    Object? timerHours = freezed,
    Object? sectorNumbers = freezed,
    Object? issuedBy = null,
    Object? timestamp = null,
  }) {
    return _then(_$PivotControlCommandImpl(
      pivotId: null == pivotId
          ? _value.pivotId
          : pivotId // ignore: cast_nullable_to_non_nullable
              as String,
      commandType: null == commandType
          ? _value.commandType
          : commandType // ignore: cast_nullable_to_non_nullable
              as PivotCommandType,
      speedPercent: freezed == speedPercent
          ? _value.speedPercent
          : speedPercent // ignore: cast_nullable_to_non_nullable
              as double?,
      targetAngle: freezed == targetAngle
          ? _value.targetAngle
          : targetAngle // ignore: cast_nullable_to_non_nullable
              as double?,
      direction: freezed == direction
          ? _value.direction
          : direction // ignore: cast_nullable_to_non_nullable
              as PivotDirection?,
      endGunEnabled: freezed == endGunEnabled
          ? _value.endGunEnabled
          : endGunEnabled // ignore: cast_nullable_to_non_nullable
              as bool?,
      timerHours: freezed == timerHours
          ? _value.timerHours
          : timerHours // ignore: cast_nullable_to_non_nullable
              as double?,
      sectorNumbers: freezed == sectorNumbers
          ? _value._sectorNumbers
          : sectorNumbers // ignore: cast_nullable_to_non_nullable
              as List<int>?,
      issuedBy: null == issuedBy
          ? _value.issuedBy
          : issuedBy // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$PivotControlCommandImpl implements _PivotControlCommand {
  const _$PivotControlCommandImpl(
      {required this.pivotId,
      required this.commandType,
      this.speedPercent,
      this.targetAngle,
      this.direction,
      this.endGunEnabled,
      this.timerHours,
      final List<int>? sectorNumbers,
      required this.issuedBy,
      required this.timestamp})
      : _sectorNumbers = sectorNumbers;

  factory _$PivotControlCommandImpl.fromJson(Map<String, dynamic> json) =>
      _$$PivotControlCommandImplFromJson(json);

  @override
  final String pivotId;
  @override
  final PivotCommandType commandType;

  /// Target speed percent (for speed commands)
  @override
  final double? speedPercent;

  /// Target angle (for move-to commands)
  @override
  final double? targetAngle;

  /// Direction (for direction commands)
  @override
  final PivotDirection? direction;

  /// End gun setting
  @override
  final bool? endGunEnabled;

  /// Timer hours (for timer commands)
  @override
  final double? timerHours;

  /// Sector numbers to enable/disable
  final List<int>? _sectorNumbers;

  /// Sector numbers to enable/disable
  @override
  List<int>? get sectorNumbers {
    final value = _sectorNumbers;
    if (value == null) return null;
    if (_sectorNumbers is EqualUnmodifiableListView) return _sectorNumbers;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(value);
  }

  /// Command issued by user ID
  @override
  final String issuedBy;

  /// Timestamp
  @override
  final DateTime timestamp;

  @override
  String toString() {
    return 'PivotControlCommand(pivotId: $pivotId, commandType: $commandType, speedPercent: $speedPercent, targetAngle: $targetAngle, direction: $direction, endGunEnabled: $endGunEnabled, timerHours: $timerHours, sectorNumbers: $sectorNumbers, issuedBy: $issuedBy, timestamp: $timestamp)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$PivotControlCommandImpl &&
            (identical(other.pivotId, pivotId) || other.pivotId == pivotId) &&
            (identical(other.commandType, commandType) ||
                other.commandType == commandType) &&
            (identical(other.speedPercent, speedPercent) ||
                other.speedPercent == speedPercent) &&
            (identical(other.targetAngle, targetAngle) ||
                other.targetAngle == targetAngle) &&
            (identical(other.direction, direction) ||
                other.direction == direction) &&
            (identical(other.endGunEnabled, endGunEnabled) ||
                other.endGunEnabled == endGunEnabled) &&
            (identical(other.timerHours, timerHours) ||
                other.timerHours == timerHours) &&
            const DeepCollectionEquality()
                .equals(other._sectorNumbers, _sectorNumbers) &&
            (identical(other.issuedBy, issuedBy) ||
                other.issuedBy == issuedBy) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp));
  }

  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      pivotId,
      commandType,
      speedPercent,
      targetAngle,
      direction,
      endGunEnabled,
      timerHours,
      const DeepCollectionEquality().hash(_sectorNumbers),
      issuedBy,
      timestamp);

  /// Create a copy of PivotControlCommand
  /// with the given fields replaced by the non-null parameter values.
  @JsonKey(includeFromJson: false, includeToJson: false)
  @override
  @pragma('vm:prefer-inline')
  _$$PivotControlCommandImplCopyWith<_$PivotControlCommandImpl> get copyWith =>
      __$$PivotControlCommandImplCopyWithImpl<_$PivotControlCommandImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$PivotControlCommandImplToJson(
      this,
    );
  }
}

abstract class _PivotControlCommand implements PivotControlCommand {
  const factory _PivotControlCommand(
      {required final String pivotId,
      required final PivotCommandType commandType,
      final double? speedPercent,
      final double? targetAngle,
      final PivotDirection? direction,
      final bool? endGunEnabled,
      final double? timerHours,
      final List<int>? sectorNumbers,
      required final String issuedBy,
      required final DateTime timestamp}) = _$PivotControlCommandImpl;

  factory _PivotControlCommand.fromJson(Map<String, dynamic> json) =
      _$PivotControlCommandImpl.fromJson;

  @override
  String get pivotId;
  @override
  PivotCommandType get commandType;

  /// Target speed percent (for speed commands)
  @override
  double? get speedPercent;

  /// Target angle (for move-to commands)
  @override
  double? get targetAngle;

  /// Direction (for direction commands)
  @override
  PivotDirection? get direction;

  /// End gun setting
  @override
  bool? get endGunEnabled;

  /// Timer hours (for timer commands)
  @override
  double? get timerHours;

  /// Sector numbers to enable/disable
  @override
  List<int>? get sectorNumbers;

  /// Command issued by user ID
  @override
  String get issuedBy;

  /// Timestamp
  @override
  DateTime get timestamp;

  /// Create a copy of PivotControlCommand
  /// with the given fields replaced by the non-null parameter values.
  @override
  @JsonKey(includeFromJson: false, includeToJson: false)
  _$$PivotControlCommandImplCopyWith<_$PivotControlCommandImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
