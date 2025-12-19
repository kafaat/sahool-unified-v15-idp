// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'fertilizer_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

SoilAnalysis _$SoilAnalysisFromJson(Map<String, dynamic> json) {
  return _SoilAnalysis.fromJson(json);
}

/// @nodoc
mixin _$SoilAnalysis {
  double get ph => throw _privateConstructorUsedError;
  double get nitrogen => throw _privateConstructorUsedError; // mg/kg
  double get phosphorus => throw _privateConstructorUsedError; // mg/kg
  double get potassium => throw _privateConstructorUsedError; // mg/kg
  double get organicMatter => throw _privateConstructorUsedError; // %
  String get soilType => throw _privateConstructorUsedError;
  String get soilTypeAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $SoilAnalysisCopyWith<SoilAnalysis> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SoilAnalysisCopyWith<$Res> {
  factory $SoilAnalysisCopyWith(
          SoilAnalysis value, $Res Function(SoilAnalysis) then) =
      _$SoilAnalysisCopyWithImpl<$Res, SoilAnalysis>;
  @useResult
  $Res call(
      {double ph,
      double nitrogen,
      double phosphorus,
      double potassium,
      double organicMatter,
      String soilType,
      String soilTypeAr});
}

/// @nodoc
class _$SoilAnalysisCopyWithImpl<$Res, $Val extends SoilAnalysis>
    implements $SoilAnalysisCopyWith<$Res> {
  _$SoilAnalysisCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? ph = null,
    Object? nitrogen = null,
    Object? phosphorus = null,
    Object? potassium = null,
    Object? organicMatter = null,
    Object? soilType = null,
    Object? soilTypeAr = null,
  }) {
    return _then(_value.copyWith(
      ph: null == ph
          ? _value.ph
          : ph // ignore: cast_nullable_to_non_nullable
              as double,
      nitrogen: null == nitrogen
          ? _value.nitrogen
          : nitrogen // ignore: cast_nullable_to_non_nullable
              as double,
      phosphorus: null == phosphorus
          ? _value.phosphorus
          : phosphorus // ignore: cast_nullable_to_non_nullable
              as double,
      potassium: null == potassium
          ? _value.potassium
          : potassium // ignore: cast_nullable_to_non_nullable
              as double,
      organicMatter: null == organicMatter
          ? _value.organicMatter
          : organicMatter // ignore: cast_nullable_to_non_nullable
              as double,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      soilTypeAr: null == soilTypeAr
          ? _value.soilTypeAr
          : soilTypeAr // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SoilAnalysisImplCopyWith<$Res>
    implements $SoilAnalysisCopyWith<$Res> {
  factory _$$SoilAnalysisImplCopyWith(
          _$SoilAnalysisImpl value, $Res Function(_$SoilAnalysisImpl) then) =
      __$$SoilAnalysisImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {double ph,
      double nitrogen,
      double phosphorus,
      double potassium,
      double organicMatter,
      String soilType,
      String soilTypeAr});
}

/// @nodoc
class __$$SoilAnalysisImplCopyWithImpl<$Res>
    extends _$SoilAnalysisCopyWithImpl<$Res, _$SoilAnalysisImpl>
    implements _$$SoilAnalysisImplCopyWith<$Res> {
  __$$SoilAnalysisImplCopyWithImpl(
      _$SoilAnalysisImpl _value, $Res Function(_$SoilAnalysisImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? ph = null,
    Object? nitrogen = null,
    Object? phosphorus = null,
    Object? potassium = null,
    Object? organicMatter = null,
    Object? soilType = null,
    Object? soilTypeAr = null,
  }) {
    return _then(_$SoilAnalysisImpl(
      ph: null == ph
          ? _value.ph
          : ph // ignore: cast_nullable_to_non_nullable
              as double,
      nitrogen: null == nitrogen
          ? _value.nitrogen
          : nitrogen // ignore: cast_nullable_to_non_nullable
              as double,
      phosphorus: null == phosphorus
          ? _value.phosphorus
          : phosphorus // ignore: cast_nullable_to_non_nullable
              as double,
      potassium: null == potassium
          ? _value.potassium
          : potassium // ignore: cast_nullable_to_non_nullable
              as double,
      organicMatter: null == organicMatter
          ? _value.organicMatter
          : organicMatter // ignore: cast_nullable_to_non_nullable
              as double,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      soilTypeAr: null == soilTypeAr
          ? _value.soilTypeAr
          : soilTypeAr // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SoilAnalysisImpl implements _SoilAnalysis {
  const _$SoilAnalysisImpl(
      {required this.ph,
      required this.nitrogen,
      required this.phosphorus,
      required this.potassium,
      this.organicMatter = 0,
      this.soilType = '',
      this.soilTypeAr = ''});

  factory _$SoilAnalysisImpl.fromJson(Map<String, dynamic> json) =>
      _$$SoilAnalysisImplFromJson(json);

  @override
  final double ph;
  @override
  final double nitrogen;
// mg/kg
  @override
  final double phosphorus;
// mg/kg
  @override
  final double potassium;
// mg/kg
  @override
  @JsonKey()
  final double organicMatter;
// %
  @override
  @JsonKey()
  final String soilType;
  @override
  @JsonKey()
  final String soilTypeAr;

  @override
  String toString() {
    return 'SoilAnalysis(ph: $ph, nitrogen: $nitrogen, phosphorus: $phosphorus, potassium: $potassium, organicMatter: $organicMatter, soilType: $soilType, soilTypeAr: $soilTypeAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SoilAnalysisImpl &&
            (identical(other.ph, ph) || other.ph == ph) &&
            (identical(other.nitrogen, nitrogen) ||
                other.nitrogen == nitrogen) &&
            (identical(other.phosphorus, phosphorus) ||
                other.phosphorus == phosphorus) &&
            (identical(other.potassium, potassium) ||
                other.potassium == potassium) &&
            (identical(other.organicMatter, organicMatter) ||
                other.organicMatter == organicMatter) &&
            (identical(other.soilType, soilType) ||
                other.soilType == soilType) &&
            (identical(other.soilTypeAr, soilTypeAr) ||
                other.soilTypeAr == soilTypeAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(runtimeType, ph, nitrogen, phosphorus,
      potassium, organicMatter, soilType, soilTypeAr);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$SoilAnalysisImplCopyWith<_$SoilAnalysisImpl> get copyWith =>
      __$$SoilAnalysisImplCopyWithImpl<_$SoilAnalysisImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SoilAnalysisImplToJson(
      this,
    );
  }
}

abstract class _SoilAnalysis implements SoilAnalysis {
  const factory _SoilAnalysis(
      {required final double ph,
      required final double nitrogen,
      required final double phosphorus,
      required final double potassium,
      final double organicMatter,
      final String soilType,
      final String soilTypeAr}) = _$SoilAnalysisImpl;

  factory _SoilAnalysis.fromJson(Map<String, dynamic> json) =
      _$SoilAnalysisImpl.fromJson;

  @override
  double get ph;
  @override
  double get nitrogen;
  @override // mg/kg
  double get phosphorus;
  @override // mg/kg
  double get potassium;
  @override // mg/kg
  double get organicMatter;
  @override // %
  String get soilType;
  @override
  String get soilTypeAr;
  @override
  @JsonKey(ignore: true)
  _$$SoilAnalysisImplCopyWith<_$SoilAnalysisImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

FertilizerRequest _$FertilizerRequestFromJson(Map<String, dynamic> json) {
  return _FertilizerRequest.fromJson(json);
}

/// @nodoc
mixin _$FertilizerRequest {
  String get cropType => throw _privateConstructorUsedError;
  double get fieldArea => throw _privateConstructorUsedError; // hectares
  SoilAnalysis get soilAnalysis => throw _privateConstructorUsedError;
  String get growthStage => throw _privateConstructorUsedError;
  String get governorate => throw _privateConstructorUsedError;
  String get irrigationType => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $FertilizerRequestCopyWith<FertilizerRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $FertilizerRequestCopyWith<$Res> {
  factory $FertilizerRequestCopyWith(
          FertilizerRequest value, $Res Function(FertilizerRequest) then) =
      _$FertilizerRequestCopyWithImpl<$Res, FertilizerRequest>;
  @useResult
  $Res call(
      {String cropType,
      double fieldArea,
      SoilAnalysis soilAnalysis,
      String growthStage,
      String governorate,
      String irrigationType});

  $SoilAnalysisCopyWith<$Res> get soilAnalysis;
}

/// @nodoc
class _$FertilizerRequestCopyWithImpl<$Res, $Val extends FertilizerRequest>
    implements $FertilizerRequestCopyWith<$Res> {
  _$FertilizerRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropType = null,
    Object? fieldArea = null,
    Object? soilAnalysis = null,
    Object? growthStage = null,
    Object? governorate = null,
    Object? irrigationType = null,
  }) {
    return _then(_value.copyWith(
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      fieldArea: null == fieldArea
          ? _value.fieldArea
          : fieldArea // ignore: cast_nullable_to_non_nullable
              as double,
      soilAnalysis: null == soilAnalysis
          ? _value.soilAnalysis
          : soilAnalysis // ignore: cast_nullable_to_non_nullable
              as SoilAnalysis,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      governorate: null == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String,
      irrigationType: null == irrigationType
          ? _value.irrigationType
          : irrigationType // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }

  @override
  @pragma('vm:prefer-inline')
  $SoilAnalysisCopyWith<$Res> get soilAnalysis {
    return $SoilAnalysisCopyWith<$Res>(_value.soilAnalysis, (value) {
      return _then(_value.copyWith(soilAnalysis: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$FertilizerRequestImplCopyWith<$Res>
    implements $FertilizerRequestCopyWith<$Res> {
  factory _$$FertilizerRequestImplCopyWith(_$FertilizerRequestImpl value,
          $Res Function(_$FertilizerRequestImpl) then) =
      __$$FertilizerRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String cropType,
      double fieldArea,
      SoilAnalysis soilAnalysis,
      String growthStage,
      String governorate,
      String irrigationType});

  @override
  $SoilAnalysisCopyWith<$Res> get soilAnalysis;
}

/// @nodoc
class __$$FertilizerRequestImplCopyWithImpl<$Res>
    extends _$FertilizerRequestCopyWithImpl<$Res, _$FertilizerRequestImpl>
    implements _$$FertilizerRequestImplCopyWith<$Res> {
  __$$FertilizerRequestImplCopyWithImpl(_$FertilizerRequestImpl _value,
      $Res Function(_$FertilizerRequestImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropType = null,
    Object? fieldArea = null,
    Object? soilAnalysis = null,
    Object? growthStage = null,
    Object? governorate = null,
    Object? irrigationType = null,
  }) {
    return _then(_$FertilizerRequestImpl(
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      fieldArea: null == fieldArea
          ? _value.fieldArea
          : fieldArea // ignore: cast_nullable_to_non_nullable
              as double,
      soilAnalysis: null == soilAnalysis
          ? _value.soilAnalysis
          : soilAnalysis // ignore: cast_nullable_to_non_nullable
              as SoilAnalysis,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      governorate: null == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String,
      irrigationType: null == irrigationType
          ? _value.irrigationType
          : irrigationType // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$FertilizerRequestImpl implements _FertilizerRequest {
  const _$FertilizerRequestImpl(
      {required this.cropType,
      required this.fieldArea,
      required this.soilAnalysis,
      required this.growthStage,
      this.governorate = '',
      this.irrigationType = ''});

  factory _$FertilizerRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$FertilizerRequestImplFromJson(json);

  @override
  final String cropType;
  @override
  final double fieldArea;
// hectares
  @override
  final SoilAnalysis soilAnalysis;
  @override
  final String growthStage;
  @override
  @JsonKey()
  final String governorate;
  @override
  @JsonKey()
  final String irrigationType;

  @override
  String toString() {
    return 'FertilizerRequest(cropType: $cropType, fieldArea: $fieldArea, soilAnalysis: $soilAnalysis, growthStage: $growthStage, governorate: $governorate, irrigationType: $irrigationType)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$FertilizerRequestImpl &&
            (identical(other.cropType, cropType) ||
                other.cropType == cropType) &&
            (identical(other.fieldArea, fieldArea) ||
                other.fieldArea == fieldArea) &&
            (identical(other.soilAnalysis, soilAnalysis) ||
                other.soilAnalysis == soilAnalysis) &&
            (identical(other.growthStage, growthStage) ||
                other.growthStage == growthStage) &&
            (identical(other.governorate, governorate) ||
                other.governorate == governorate) &&
            (identical(other.irrigationType, irrigationType) ||
                other.irrigationType == irrigationType));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(runtimeType, cropType, fieldArea,
      soilAnalysis, growthStage, governorate, irrigationType);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$FertilizerRequestImplCopyWith<_$FertilizerRequestImpl> get copyWith =>
      __$$FertilizerRequestImplCopyWithImpl<_$FertilizerRequestImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$FertilizerRequestImplToJson(
      this,
    );
  }
}

abstract class _FertilizerRequest implements FertilizerRequest {
  const factory _FertilizerRequest(
      {required final String cropType,
      required final double fieldArea,
      required final SoilAnalysis soilAnalysis,
      required final String growthStage,
      final String governorate,
      final String irrigationType}) = _$FertilizerRequestImpl;

  factory _FertilizerRequest.fromJson(Map<String, dynamic> json) =
      _$FertilizerRequestImpl.fromJson;

  @override
  String get cropType;
  @override
  double get fieldArea;
  @override // hectares
  SoilAnalysis get soilAnalysis;
  @override
  String get growthStage;
  @override
  String get governorate;
  @override
  String get irrigationType;
  @override
  @JsonKey(ignore: true)
  _$$FertilizerRequestImplCopyWith<_$FertilizerRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

NpkRecommendation _$NpkRecommendationFromJson(Map<String, dynamic> json) {
  return _NpkRecommendation.fromJson(json);
}

/// @nodoc
mixin _$NpkRecommendation {
  double get nitrogenKg => throw _privateConstructorUsedError; // كجم/هكتار
  double get phosphorusKg => throw _privateConstructorUsedError;
  double get potassiumKg => throw _privateConstructorUsedError;
  double get totalKgPerHectare => throw _privateConstructorUsedError;
  double get totalKgForField => throw _privateConstructorUsedError;
  String get applicationMethod => throw _privateConstructorUsedError;
  String get applicationMethodAr => throw _privateConstructorUsedError;
  String get timing => throw _privateConstructorUsedError;
  String get timingAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $NpkRecommendationCopyWith<NpkRecommendation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $NpkRecommendationCopyWith<$Res> {
  factory $NpkRecommendationCopyWith(
          NpkRecommendation value, $Res Function(NpkRecommendation) then) =
      _$NpkRecommendationCopyWithImpl<$Res, NpkRecommendation>;
  @useResult
  $Res call(
      {double nitrogenKg,
      double phosphorusKg,
      double potassiumKg,
      double totalKgPerHectare,
      double totalKgForField,
      String applicationMethod,
      String applicationMethodAr,
      String timing,
      String timingAr});
}

/// @nodoc
class _$NpkRecommendationCopyWithImpl<$Res, $Val extends NpkRecommendation>
    implements $NpkRecommendationCopyWith<$Res> {
  _$NpkRecommendationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? nitrogenKg = null,
    Object? phosphorusKg = null,
    Object? potassiumKg = null,
    Object? totalKgPerHectare = null,
    Object? totalKgForField = null,
    Object? applicationMethod = null,
    Object? applicationMethodAr = null,
    Object? timing = null,
    Object? timingAr = null,
  }) {
    return _then(_value.copyWith(
      nitrogenKg: null == nitrogenKg
          ? _value.nitrogenKg
          : nitrogenKg // ignore: cast_nullable_to_non_nullable
              as double,
      phosphorusKg: null == phosphorusKg
          ? _value.phosphorusKg
          : phosphorusKg // ignore: cast_nullable_to_non_nullable
              as double,
      potassiumKg: null == potassiumKg
          ? _value.potassiumKg
          : potassiumKg // ignore: cast_nullable_to_non_nullable
              as double,
      totalKgPerHectare: null == totalKgPerHectare
          ? _value.totalKgPerHectare
          : totalKgPerHectare // ignore: cast_nullable_to_non_nullable
              as double,
      totalKgForField: null == totalKgForField
          ? _value.totalKgForField
          : totalKgForField // ignore: cast_nullable_to_non_nullable
              as double,
      applicationMethod: null == applicationMethod
          ? _value.applicationMethod
          : applicationMethod // ignore: cast_nullable_to_non_nullable
              as String,
      applicationMethodAr: null == applicationMethodAr
          ? _value.applicationMethodAr
          : applicationMethodAr // ignore: cast_nullable_to_non_nullable
              as String,
      timing: null == timing
          ? _value.timing
          : timing // ignore: cast_nullable_to_non_nullable
              as String,
      timingAr: null == timingAr
          ? _value.timingAr
          : timingAr // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$NpkRecommendationImplCopyWith<$Res>
    implements $NpkRecommendationCopyWith<$Res> {
  factory _$$NpkRecommendationImplCopyWith(_$NpkRecommendationImpl value,
          $Res Function(_$NpkRecommendationImpl) then) =
      __$$NpkRecommendationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {double nitrogenKg,
      double phosphorusKg,
      double potassiumKg,
      double totalKgPerHectare,
      double totalKgForField,
      String applicationMethod,
      String applicationMethodAr,
      String timing,
      String timingAr});
}

/// @nodoc
class __$$NpkRecommendationImplCopyWithImpl<$Res>
    extends _$NpkRecommendationCopyWithImpl<$Res, _$NpkRecommendationImpl>
    implements _$$NpkRecommendationImplCopyWith<$Res> {
  __$$NpkRecommendationImplCopyWithImpl(_$NpkRecommendationImpl _value,
      $Res Function(_$NpkRecommendationImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? nitrogenKg = null,
    Object? phosphorusKg = null,
    Object? potassiumKg = null,
    Object? totalKgPerHectare = null,
    Object? totalKgForField = null,
    Object? applicationMethod = null,
    Object? applicationMethodAr = null,
    Object? timing = null,
    Object? timingAr = null,
  }) {
    return _then(_$NpkRecommendationImpl(
      nitrogenKg: null == nitrogenKg
          ? _value.nitrogenKg
          : nitrogenKg // ignore: cast_nullable_to_non_nullable
              as double,
      phosphorusKg: null == phosphorusKg
          ? _value.phosphorusKg
          : phosphorusKg // ignore: cast_nullable_to_non_nullable
              as double,
      potassiumKg: null == potassiumKg
          ? _value.potassiumKg
          : potassiumKg // ignore: cast_nullable_to_non_nullable
              as double,
      totalKgPerHectare: null == totalKgPerHectare
          ? _value.totalKgPerHectare
          : totalKgPerHectare // ignore: cast_nullable_to_non_nullable
              as double,
      totalKgForField: null == totalKgForField
          ? _value.totalKgForField
          : totalKgForField // ignore: cast_nullable_to_non_nullable
              as double,
      applicationMethod: null == applicationMethod
          ? _value.applicationMethod
          : applicationMethod // ignore: cast_nullable_to_non_nullable
              as String,
      applicationMethodAr: null == applicationMethodAr
          ? _value.applicationMethodAr
          : applicationMethodAr // ignore: cast_nullable_to_non_nullable
              as String,
      timing: null == timing
          ? _value.timing
          : timing // ignore: cast_nullable_to_non_nullable
              as String,
      timingAr: null == timingAr
          ? _value.timingAr
          : timingAr // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$NpkRecommendationImpl implements _NpkRecommendation {
  const _$NpkRecommendationImpl(
      {required this.nitrogenKg,
      required this.phosphorusKg,
      required this.potassiumKg,
      required this.totalKgPerHectare,
      required this.totalKgForField,
      this.applicationMethod = '',
      this.applicationMethodAr = '',
      this.timing = '',
      this.timingAr = ''});

  factory _$NpkRecommendationImpl.fromJson(Map<String, dynamic> json) =>
      _$$NpkRecommendationImplFromJson(json);

  @override
  final double nitrogenKg;
// كجم/هكتار
  @override
  final double phosphorusKg;
  @override
  final double potassiumKg;
  @override
  final double totalKgPerHectare;
  @override
  final double totalKgForField;
  @override
  @JsonKey()
  final String applicationMethod;
  @override
  @JsonKey()
  final String applicationMethodAr;
  @override
  @JsonKey()
  final String timing;
  @override
  @JsonKey()
  final String timingAr;

  @override
  String toString() {
    return 'NpkRecommendation(nitrogenKg: $nitrogenKg, phosphorusKg: $phosphorusKg, potassiumKg: $potassiumKg, totalKgPerHectare: $totalKgPerHectare, totalKgForField: $totalKgForField, applicationMethod: $applicationMethod, applicationMethodAr: $applicationMethodAr, timing: $timing, timingAr: $timingAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$NpkRecommendationImpl &&
            (identical(other.nitrogenKg, nitrogenKg) ||
                other.nitrogenKg == nitrogenKg) &&
            (identical(other.phosphorusKg, phosphorusKg) ||
                other.phosphorusKg == phosphorusKg) &&
            (identical(other.potassiumKg, potassiumKg) ||
                other.potassiumKg == potassiumKg) &&
            (identical(other.totalKgPerHectare, totalKgPerHectare) ||
                other.totalKgPerHectare == totalKgPerHectare) &&
            (identical(other.totalKgForField, totalKgForField) ||
                other.totalKgForField == totalKgForField) &&
            (identical(other.applicationMethod, applicationMethod) ||
                other.applicationMethod == applicationMethod) &&
            (identical(other.applicationMethodAr, applicationMethodAr) ||
                other.applicationMethodAr == applicationMethodAr) &&
            (identical(other.timing, timing) || other.timing == timing) &&
            (identical(other.timingAr, timingAr) ||
                other.timingAr == timingAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      nitrogenKg,
      phosphorusKg,
      potassiumKg,
      totalKgPerHectare,
      totalKgForField,
      applicationMethod,
      applicationMethodAr,
      timing,
      timingAr);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$NpkRecommendationImplCopyWith<_$NpkRecommendationImpl> get copyWith =>
      __$$NpkRecommendationImplCopyWithImpl<_$NpkRecommendationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$NpkRecommendationImplToJson(
      this,
    );
  }
}

abstract class _NpkRecommendation implements NpkRecommendation {
  const factory _NpkRecommendation(
      {required final double nitrogenKg,
      required final double phosphorusKg,
      required final double potassiumKg,
      required final double totalKgPerHectare,
      required final double totalKgForField,
      final String applicationMethod,
      final String applicationMethodAr,
      final String timing,
      final String timingAr}) = _$NpkRecommendationImpl;

  factory _NpkRecommendation.fromJson(Map<String, dynamic> json) =
      _$NpkRecommendationImpl.fromJson;

  @override
  double get nitrogenKg;
  @override // كجم/هكتار
  double get phosphorusKg;
  @override
  double get potassiumKg;
  @override
  double get totalKgPerHectare;
  @override
  double get totalKgForField;
  @override
  String get applicationMethod;
  @override
  String get applicationMethodAr;
  @override
  String get timing;
  @override
  String get timingAr;
  @override
  @JsonKey(ignore: true)
  _$$NpkRecommendationImplCopyWith<_$NpkRecommendationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

FertilizerProduct _$FertilizerProductFromJson(Map<String, dynamic> json) {
  return _FertilizerProduct.fromJson(json);
}

/// @nodoc
mixin _$FertilizerProduct {
  String get productId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;
  String get npkRatio => throw _privateConstructorUsedError; // e.g., "15-15-15"
  double get quantityKg => throw _privateConstructorUsedError;
  double get pricePerKg => throw _privateConstructorUsedError;
  String get applicationNotes => throw _privateConstructorUsedError;
  String get applicationNotesAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $FertilizerProductCopyWith<FertilizerProduct> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $FertilizerProductCopyWith<$Res> {
  factory $FertilizerProductCopyWith(
          FertilizerProduct value, $Res Function(FertilizerProduct) then) =
      _$FertilizerProductCopyWithImpl<$Res, FertilizerProduct>;
  @useResult
  $Res call(
      {String productId,
      String name,
      String nameAr,
      String npkRatio,
      double quantityKg,
      double pricePerKg,
      String applicationNotes,
      String applicationNotesAr});
}

/// @nodoc
class _$FertilizerProductCopyWithImpl<$Res, $Val extends FertilizerProduct>
    implements $FertilizerProductCopyWith<$Res> {
  _$FertilizerProductCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? productId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? npkRatio = null,
    Object? quantityKg = null,
    Object? pricePerKg = null,
    Object? applicationNotes = null,
    Object? applicationNotesAr = null,
  }) {
    return _then(_value.copyWith(
      productId: null == productId
          ? _value.productId
          : productId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      npkRatio: null == npkRatio
          ? _value.npkRatio
          : npkRatio // ignore: cast_nullable_to_non_nullable
              as String,
      quantityKg: null == quantityKg
          ? _value.quantityKg
          : quantityKg // ignore: cast_nullable_to_non_nullable
              as double,
      pricePerKg: null == pricePerKg
          ? _value.pricePerKg
          : pricePerKg // ignore: cast_nullable_to_non_nullable
              as double,
      applicationNotes: null == applicationNotes
          ? _value.applicationNotes
          : applicationNotes // ignore: cast_nullable_to_non_nullable
              as String,
      applicationNotesAr: null == applicationNotesAr
          ? _value.applicationNotesAr
          : applicationNotesAr // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$FertilizerProductImplCopyWith<$Res>
    implements $FertilizerProductCopyWith<$Res> {
  factory _$$FertilizerProductImplCopyWith(_$FertilizerProductImpl value,
          $Res Function(_$FertilizerProductImpl) then) =
      __$$FertilizerProductImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String productId,
      String name,
      String nameAr,
      String npkRatio,
      double quantityKg,
      double pricePerKg,
      String applicationNotes,
      String applicationNotesAr});
}

/// @nodoc
class __$$FertilizerProductImplCopyWithImpl<$Res>
    extends _$FertilizerProductCopyWithImpl<$Res, _$FertilizerProductImpl>
    implements _$$FertilizerProductImplCopyWith<$Res> {
  __$$FertilizerProductImplCopyWithImpl(_$FertilizerProductImpl _value,
      $Res Function(_$FertilizerProductImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? productId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? npkRatio = null,
    Object? quantityKg = null,
    Object? pricePerKg = null,
    Object? applicationNotes = null,
    Object? applicationNotesAr = null,
  }) {
    return _then(_$FertilizerProductImpl(
      productId: null == productId
          ? _value.productId
          : productId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      npkRatio: null == npkRatio
          ? _value.npkRatio
          : npkRatio // ignore: cast_nullable_to_non_nullable
              as String,
      quantityKg: null == quantityKg
          ? _value.quantityKg
          : quantityKg // ignore: cast_nullable_to_non_nullable
              as double,
      pricePerKg: null == pricePerKg
          ? _value.pricePerKg
          : pricePerKg // ignore: cast_nullable_to_non_nullable
              as double,
      applicationNotes: null == applicationNotes
          ? _value.applicationNotes
          : applicationNotes // ignore: cast_nullable_to_non_nullable
              as String,
      applicationNotesAr: null == applicationNotesAr
          ? _value.applicationNotesAr
          : applicationNotesAr // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$FertilizerProductImpl implements _FertilizerProduct {
  const _$FertilizerProductImpl(
      {required this.productId,
      required this.name,
      required this.nameAr,
      required this.npkRatio,
      required this.quantityKg,
      this.pricePerKg = 0,
      this.applicationNotes = '',
      this.applicationNotesAr = ''});

  factory _$FertilizerProductImpl.fromJson(Map<String, dynamic> json) =>
      _$$FertilizerProductImplFromJson(json);

  @override
  final String productId;
  @override
  final String name;
  @override
  final String nameAr;
  @override
  final String npkRatio;
// e.g., "15-15-15"
  @override
  final double quantityKg;
  @override
  @JsonKey()
  final double pricePerKg;
  @override
  @JsonKey()
  final String applicationNotes;
  @override
  @JsonKey()
  final String applicationNotesAr;

  @override
  String toString() {
    return 'FertilizerProduct(productId: $productId, name: $name, nameAr: $nameAr, npkRatio: $npkRatio, quantityKg: $quantityKg, pricePerKg: $pricePerKg, applicationNotes: $applicationNotes, applicationNotesAr: $applicationNotesAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$FertilizerProductImpl &&
            (identical(other.productId, productId) ||
                other.productId == productId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.npkRatio, npkRatio) ||
                other.npkRatio == npkRatio) &&
            (identical(other.quantityKg, quantityKg) ||
                other.quantityKg == quantityKg) &&
            (identical(other.pricePerKg, pricePerKg) ||
                other.pricePerKg == pricePerKg) &&
            (identical(other.applicationNotes, applicationNotes) ||
                other.applicationNotes == applicationNotes) &&
            (identical(other.applicationNotesAr, applicationNotesAr) ||
                other.applicationNotesAr == applicationNotesAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(runtimeType, productId, name, nameAr,
      npkRatio, quantityKg, pricePerKg, applicationNotes, applicationNotesAr);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$FertilizerProductImplCopyWith<_$FertilizerProductImpl> get copyWith =>
      __$$FertilizerProductImplCopyWithImpl<_$FertilizerProductImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$FertilizerProductImplToJson(
      this,
    );
  }
}

abstract class _FertilizerProduct implements FertilizerProduct {
  const factory _FertilizerProduct(
      {required final String productId,
      required final String name,
      required final String nameAr,
      required final String npkRatio,
      required final double quantityKg,
      final double pricePerKg,
      final String applicationNotes,
      final String applicationNotesAr}) = _$FertilizerProductImpl;

  factory _FertilizerProduct.fromJson(Map<String, dynamic> json) =
      _$FertilizerProductImpl.fromJson;

  @override
  String get productId;
  @override
  String get name;
  @override
  String get nameAr;
  @override
  String get npkRatio;
  @override // e.g., "15-15-15"
  double get quantityKg;
  @override
  double get pricePerKg;
  @override
  String get applicationNotes;
  @override
  String get applicationNotesAr;
  @override
  @JsonKey(ignore: true)
  _$$FertilizerProductImplCopyWith<_$FertilizerProductImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

FertilizerRecommendation _$FertilizerRecommendationFromJson(
    Map<String, dynamic> json) {
  return _FertilizerRecommendation.fromJson(json);
}

/// @nodoc
mixin _$FertilizerRecommendation {
  String get recommendationId => throw _privateConstructorUsedError;
  String get fieldId => throw _privateConstructorUsedError;
  String get cropType => throw _privateConstructorUsedError;
  String get cropTypeAr => throw _privateConstructorUsedError;
  NpkRecommendation get npkRecommendation => throw _privateConstructorUsedError;
  List<FertilizerProduct> get suggestedProducts =>
      throw _privateConstructorUsedError;
  String get soilHealthStatus => throw _privateConstructorUsedError;
  String get soilHealthStatusAr => throw _privateConstructorUsedError;
  List<String> get deficiencies => throw _privateConstructorUsedError;
  List<String> get deficienciesAr => throw _privateConstructorUsedError;
  List<String> get warnings => throw _privateConstructorUsedError;
  List<String> get warningsAr => throw _privateConstructorUsedError;
  DateTime get generatedAt => throw _privateConstructorUsedError;
  String get seasonalNote => throw _privateConstructorUsedError;
  String get seasonalNoteAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $FertilizerRecommendationCopyWith<FertilizerRecommendation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $FertilizerRecommendationCopyWith<$Res> {
  factory $FertilizerRecommendationCopyWith(FertilizerRecommendation value,
          $Res Function(FertilizerRecommendation) then) =
      _$FertilizerRecommendationCopyWithImpl<$Res, FertilizerRecommendation>;
  @useResult
  $Res call(
      {String recommendationId,
      String fieldId,
      String cropType,
      String cropTypeAr,
      NpkRecommendation npkRecommendation,
      List<FertilizerProduct> suggestedProducts,
      String soilHealthStatus,
      String soilHealthStatusAr,
      List<String> deficiencies,
      List<String> deficienciesAr,
      List<String> warnings,
      List<String> warningsAr,
      DateTime generatedAt,
      String seasonalNote,
      String seasonalNoteAr});

  $NpkRecommendationCopyWith<$Res> get npkRecommendation;
}

/// @nodoc
class _$FertilizerRecommendationCopyWithImpl<$Res,
        $Val extends FertilizerRecommendation>
    implements $FertilizerRecommendationCopyWith<$Res> {
  _$FertilizerRecommendationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? recommendationId = null,
    Object? fieldId = null,
    Object? cropType = null,
    Object? cropTypeAr = null,
    Object? npkRecommendation = null,
    Object? suggestedProducts = null,
    Object? soilHealthStatus = null,
    Object? soilHealthStatusAr = null,
    Object? deficiencies = null,
    Object? deficienciesAr = null,
    Object? warnings = null,
    Object? warningsAr = null,
    Object? generatedAt = null,
    Object? seasonalNote = null,
    Object? seasonalNoteAr = null,
  }) {
    return _then(_value.copyWith(
      recommendationId: null == recommendationId
          ? _value.recommendationId
          : recommendationId // ignore: cast_nullable_to_non_nullable
              as String,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      cropTypeAr: null == cropTypeAr
          ? _value.cropTypeAr
          : cropTypeAr // ignore: cast_nullable_to_non_nullable
              as String,
      npkRecommendation: null == npkRecommendation
          ? _value.npkRecommendation
          : npkRecommendation // ignore: cast_nullable_to_non_nullable
              as NpkRecommendation,
      suggestedProducts: null == suggestedProducts
          ? _value.suggestedProducts
          : suggestedProducts // ignore: cast_nullable_to_non_nullable
              as List<FertilizerProduct>,
      soilHealthStatus: null == soilHealthStatus
          ? _value.soilHealthStatus
          : soilHealthStatus // ignore: cast_nullable_to_non_nullable
              as String,
      soilHealthStatusAr: null == soilHealthStatusAr
          ? _value.soilHealthStatusAr
          : soilHealthStatusAr // ignore: cast_nullable_to_non_nullable
              as String,
      deficiencies: null == deficiencies
          ? _value.deficiencies
          : deficiencies // ignore: cast_nullable_to_non_nullable
              as List<String>,
      deficienciesAr: null == deficienciesAr
          ? _value.deficienciesAr
          : deficienciesAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warningsAr: null == warningsAr
          ? _value.warningsAr
          : warningsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      generatedAt: null == generatedAt
          ? _value.generatedAt
          : generatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      seasonalNote: null == seasonalNote
          ? _value.seasonalNote
          : seasonalNote // ignore: cast_nullable_to_non_nullable
              as String,
      seasonalNoteAr: null == seasonalNoteAr
          ? _value.seasonalNoteAr
          : seasonalNoteAr // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }

  @override
  @pragma('vm:prefer-inline')
  $NpkRecommendationCopyWith<$Res> get npkRecommendation {
    return $NpkRecommendationCopyWith<$Res>(_value.npkRecommendation, (value) {
      return _then(_value.copyWith(npkRecommendation: value) as $Val);
    });
  }
}

/// @nodoc
abstract class _$$FertilizerRecommendationImplCopyWith<$Res>
    implements $FertilizerRecommendationCopyWith<$Res> {
  factory _$$FertilizerRecommendationImplCopyWith(
          _$FertilizerRecommendationImpl value,
          $Res Function(_$FertilizerRecommendationImpl) then) =
      __$$FertilizerRecommendationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String recommendationId,
      String fieldId,
      String cropType,
      String cropTypeAr,
      NpkRecommendation npkRecommendation,
      List<FertilizerProduct> suggestedProducts,
      String soilHealthStatus,
      String soilHealthStatusAr,
      List<String> deficiencies,
      List<String> deficienciesAr,
      List<String> warnings,
      List<String> warningsAr,
      DateTime generatedAt,
      String seasonalNote,
      String seasonalNoteAr});

  @override
  $NpkRecommendationCopyWith<$Res> get npkRecommendation;
}

/// @nodoc
class __$$FertilizerRecommendationImplCopyWithImpl<$Res>
    extends _$FertilizerRecommendationCopyWithImpl<$Res,
        _$FertilizerRecommendationImpl>
    implements _$$FertilizerRecommendationImplCopyWith<$Res> {
  __$$FertilizerRecommendationImplCopyWithImpl(
      _$FertilizerRecommendationImpl _value,
      $Res Function(_$FertilizerRecommendationImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? recommendationId = null,
    Object? fieldId = null,
    Object? cropType = null,
    Object? cropTypeAr = null,
    Object? npkRecommendation = null,
    Object? suggestedProducts = null,
    Object? soilHealthStatus = null,
    Object? soilHealthStatusAr = null,
    Object? deficiencies = null,
    Object? deficienciesAr = null,
    Object? warnings = null,
    Object? warningsAr = null,
    Object? generatedAt = null,
    Object? seasonalNote = null,
    Object? seasonalNoteAr = null,
  }) {
    return _then(_$FertilizerRecommendationImpl(
      recommendationId: null == recommendationId
          ? _value.recommendationId
          : recommendationId // ignore: cast_nullable_to_non_nullable
              as String,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      cropTypeAr: null == cropTypeAr
          ? _value.cropTypeAr
          : cropTypeAr // ignore: cast_nullable_to_non_nullable
              as String,
      npkRecommendation: null == npkRecommendation
          ? _value.npkRecommendation
          : npkRecommendation // ignore: cast_nullable_to_non_nullable
              as NpkRecommendation,
      suggestedProducts: null == suggestedProducts
          ? _value._suggestedProducts
          : suggestedProducts // ignore: cast_nullable_to_non_nullable
              as List<FertilizerProduct>,
      soilHealthStatus: null == soilHealthStatus
          ? _value.soilHealthStatus
          : soilHealthStatus // ignore: cast_nullable_to_non_nullable
              as String,
      soilHealthStatusAr: null == soilHealthStatusAr
          ? _value.soilHealthStatusAr
          : soilHealthStatusAr // ignore: cast_nullable_to_non_nullable
              as String,
      deficiencies: null == deficiencies
          ? _value._deficiencies
          : deficiencies // ignore: cast_nullable_to_non_nullable
              as List<String>,
      deficienciesAr: null == deficienciesAr
          ? _value._deficienciesAr
          : deficienciesAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warnings: null == warnings
          ? _value._warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warningsAr: null == warningsAr
          ? _value._warningsAr
          : warningsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      generatedAt: null == generatedAt
          ? _value.generatedAt
          : generatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
      seasonalNote: null == seasonalNote
          ? _value.seasonalNote
          : seasonalNote // ignore: cast_nullable_to_non_nullable
              as String,
      seasonalNoteAr: null == seasonalNoteAr
          ? _value.seasonalNoteAr
          : seasonalNoteAr // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$FertilizerRecommendationImpl implements _FertilizerRecommendation {
  const _$FertilizerRecommendationImpl(
      {required this.recommendationId,
      required this.fieldId,
      required this.cropType,
      required this.cropTypeAr,
      required this.npkRecommendation,
      required final List<FertilizerProduct> suggestedProducts,
      required this.soilHealthStatus,
      required this.soilHealthStatusAr,
      final List<String> deficiencies = const [],
      final List<String> deficienciesAr = const [],
      final List<String> warnings = const [],
      final List<String> warningsAr = const [],
      required this.generatedAt,
      this.seasonalNote = '',
      this.seasonalNoteAr = ''})
      : _suggestedProducts = suggestedProducts,
        _deficiencies = deficiencies,
        _deficienciesAr = deficienciesAr,
        _warnings = warnings,
        _warningsAr = warningsAr;

  factory _$FertilizerRecommendationImpl.fromJson(Map<String, dynamic> json) =>
      _$$FertilizerRecommendationImplFromJson(json);

  @override
  final String recommendationId;
  @override
  final String fieldId;
  @override
  final String cropType;
  @override
  final String cropTypeAr;
  @override
  final NpkRecommendation npkRecommendation;
  final List<FertilizerProduct> _suggestedProducts;
  @override
  List<FertilizerProduct> get suggestedProducts {
    if (_suggestedProducts is EqualUnmodifiableListView)
      return _suggestedProducts;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_suggestedProducts);
  }

  @override
  final String soilHealthStatus;
  @override
  final String soilHealthStatusAr;
  final List<String> _deficiencies;
  @override
  @JsonKey()
  List<String> get deficiencies {
    if (_deficiencies is EqualUnmodifiableListView) return _deficiencies;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_deficiencies);
  }

  final List<String> _deficienciesAr;
  @override
  @JsonKey()
  List<String> get deficienciesAr {
    if (_deficienciesAr is EqualUnmodifiableListView) return _deficienciesAr;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_deficienciesAr);
  }

  final List<String> _warnings;
  @override
  @JsonKey()
  List<String> get warnings {
    if (_warnings is EqualUnmodifiableListView) return _warnings;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_warnings);
  }

  final List<String> _warningsAr;
  @override
  @JsonKey()
  List<String> get warningsAr {
    if (_warningsAr is EqualUnmodifiableListView) return _warningsAr;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_warningsAr);
  }

  @override
  final DateTime generatedAt;
  @override
  @JsonKey()
  final String seasonalNote;
  @override
  @JsonKey()
  final String seasonalNoteAr;

  @override
  String toString() {
    return 'FertilizerRecommendation(recommendationId: $recommendationId, fieldId: $fieldId, cropType: $cropType, cropTypeAr: $cropTypeAr, npkRecommendation: $npkRecommendation, suggestedProducts: $suggestedProducts, soilHealthStatus: $soilHealthStatus, soilHealthStatusAr: $soilHealthStatusAr, deficiencies: $deficiencies, deficienciesAr: $deficienciesAr, warnings: $warnings, warningsAr: $warningsAr, generatedAt: $generatedAt, seasonalNote: $seasonalNote, seasonalNoteAr: $seasonalNoteAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$FertilizerRecommendationImpl &&
            (identical(other.recommendationId, recommendationId) ||
                other.recommendationId == recommendationId) &&
            (identical(other.fieldId, fieldId) || other.fieldId == fieldId) &&
            (identical(other.cropType, cropType) ||
                other.cropType == cropType) &&
            (identical(other.cropTypeAr, cropTypeAr) ||
                other.cropTypeAr == cropTypeAr) &&
            (identical(other.npkRecommendation, npkRecommendation) ||
                other.npkRecommendation == npkRecommendation) &&
            const DeepCollectionEquality()
                .equals(other._suggestedProducts, _suggestedProducts) &&
            (identical(other.soilHealthStatus, soilHealthStatus) ||
                other.soilHealthStatus == soilHealthStatus) &&
            (identical(other.soilHealthStatusAr, soilHealthStatusAr) ||
                other.soilHealthStatusAr == soilHealthStatusAr) &&
            const DeepCollectionEquality()
                .equals(other._deficiencies, _deficiencies) &&
            const DeepCollectionEquality()
                .equals(other._deficienciesAr, _deficienciesAr) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings) &&
            const DeepCollectionEquality()
                .equals(other._warningsAr, _warningsAr) &&
            (identical(other.generatedAt, generatedAt) ||
                other.generatedAt == generatedAt) &&
            (identical(other.seasonalNote, seasonalNote) ||
                other.seasonalNote == seasonalNote) &&
            (identical(other.seasonalNoteAr, seasonalNoteAr) ||
                other.seasonalNoteAr == seasonalNoteAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      recommendationId,
      fieldId,
      cropType,
      cropTypeAr,
      npkRecommendation,
      const DeepCollectionEquality().hash(_suggestedProducts),
      soilHealthStatus,
      soilHealthStatusAr,
      const DeepCollectionEquality().hash(_deficiencies),
      const DeepCollectionEquality().hash(_deficienciesAr),
      const DeepCollectionEquality().hash(_warnings),
      const DeepCollectionEquality().hash(_warningsAr),
      generatedAt,
      seasonalNote,
      seasonalNoteAr);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$FertilizerRecommendationImplCopyWith<_$FertilizerRecommendationImpl>
      get copyWith => __$$FertilizerRecommendationImplCopyWithImpl<
          _$FertilizerRecommendationImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$FertilizerRecommendationImplToJson(
      this,
    );
  }
}

abstract class _FertilizerRecommendation implements FertilizerRecommendation {
  const factory _FertilizerRecommendation(
      {required final String recommendationId,
      required final String fieldId,
      required final String cropType,
      required final String cropTypeAr,
      required final NpkRecommendation npkRecommendation,
      required final List<FertilizerProduct> suggestedProducts,
      required final String soilHealthStatus,
      required final String soilHealthStatusAr,
      final List<String> deficiencies,
      final List<String> deficienciesAr,
      final List<String> warnings,
      final List<String> warningsAr,
      required final DateTime generatedAt,
      final String seasonalNote,
      final String seasonalNoteAr}) = _$FertilizerRecommendationImpl;

  factory _FertilizerRecommendation.fromJson(Map<String, dynamic> json) =
      _$FertilizerRecommendationImpl.fromJson;

  @override
  String get recommendationId;
  @override
  String get fieldId;
  @override
  String get cropType;
  @override
  String get cropTypeAr;
  @override
  NpkRecommendation get npkRecommendation;
  @override
  List<FertilizerProduct> get suggestedProducts;
  @override
  String get soilHealthStatus;
  @override
  String get soilHealthStatusAr;
  @override
  List<String> get deficiencies;
  @override
  List<String> get deficienciesAr;
  @override
  List<String> get warnings;
  @override
  List<String> get warningsAr;
  @override
  DateTime get generatedAt;
  @override
  String get seasonalNote;
  @override
  String get seasonalNoteAr;
  @override
  @JsonKey(ignore: true)
  _$$FertilizerRecommendationImplCopyWith<_$FertilizerRecommendationImpl>
      get copyWith => throw _privateConstructorUsedError;
}

DeficiencySymptom _$DeficiencySymptomFromJson(Map<String, dynamic> json) {
  return _DeficiencySymptom.fromJson(json);
}

/// @nodoc
mixin _$DeficiencySymptom {
  String get nutrient => throw _privateConstructorUsedError;
  String get nutrientAr => throw _privateConstructorUsedError;
  String get severity =>
      throw _privateConstructorUsedError; // low, medium, high, critical
  List<String> get visualSymptoms => throw _privateConstructorUsedError;
  List<String> get visualSymptomsAr => throw _privateConstructorUsedError;
  String get recommendation => throw _privateConstructorUsedError;
  String get recommendationAr => throw _privateConstructorUsedError;
  String get imageUrl => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $DeficiencySymptomCopyWith<DeficiencySymptom> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DeficiencySymptomCopyWith<$Res> {
  factory $DeficiencySymptomCopyWith(
          DeficiencySymptom value, $Res Function(DeficiencySymptom) then) =
      _$DeficiencySymptomCopyWithImpl<$Res, DeficiencySymptom>;
  @useResult
  $Res call(
      {String nutrient,
      String nutrientAr,
      String severity,
      List<String> visualSymptoms,
      List<String> visualSymptomsAr,
      String recommendation,
      String recommendationAr,
      String imageUrl});
}

/// @nodoc
class _$DeficiencySymptomCopyWithImpl<$Res, $Val extends DeficiencySymptom>
    implements $DeficiencySymptomCopyWith<$Res> {
  _$DeficiencySymptomCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? nutrient = null,
    Object? nutrientAr = null,
    Object? severity = null,
    Object? visualSymptoms = null,
    Object? visualSymptomsAr = null,
    Object? recommendation = null,
    Object? recommendationAr = null,
    Object? imageUrl = null,
  }) {
    return _then(_value.copyWith(
      nutrient: null == nutrient
          ? _value.nutrient
          : nutrient // ignore: cast_nullable_to_non_nullable
              as String,
      nutrientAr: null == nutrientAr
          ? _value.nutrientAr
          : nutrientAr // ignore: cast_nullable_to_non_nullable
              as String,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as String,
      visualSymptoms: null == visualSymptoms
          ? _value.visualSymptoms
          : visualSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      visualSymptomsAr: null == visualSymptomsAr
          ? _value.visualSymptomsAr
          : visualSymptomsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      recommendation: null == recommendation
          ? _value.recommendation
          : recommendation // ignore: cast_nullable_to_non_nullable
              as String,
      recommendationAr: null == recommendationAr
          ? _value.recommendationAr
          : recommendationAr // ignore: cast_nullable_to_non_nullable
              as String,
      imageUrl: null == imageUrl
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DeficiencySymptomImplCopyWith<$Res>
    implements $DeficiencySymptomCopyWith<$Res> {
  factory _$$DeficiencySymptomImplCopyWith(_$DeficiencySymptomImpl value,
          $Res Function(_$DeficiencySymptomImpl) then) =
      __$$DeficiencySymptomImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String nutrient,
      String nutrientAr,
      String severity,
      List<String> visualSymptoms,
      List<String> visualSymptomsAr,
      String recommendation,
      String recommendationAr,
      String imageUrl});
}

/// @nodoc
class __$$DeficiencySymptomImplCopyWithImpl<$Res>
    extends _$DeficiencySymptomCopyWithImpl<$Res, _$DeficiencySymptomImpl>
    implements _$$DeficiencySymptomImplCopyWith<$Res> {
  __$$DeficiencySymptomImplCopyWithImpl(_$DeficiencySymptomImpl _value,
      $Res Function(_$DeficiencySymptomImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? nutrient = null,
    Object? nutrientAr = null,
    Object? severity = null,
    Object? visualSymptoms = null,
    Object? visualSymptomsAr = null,
    Object? recommendation = null,
    Object? recommendationAr = null,
    Object? imageUrl = null,
  }) {
    return _then(_$DeficiencySymptomImpl(
      nutrient: null == nutrient
          ? _value.nutrient
          : nutrient // ignore: cast_nullable_to_non_nullable
              as String,
      nutrientAr: null == nutrientAr
          ? _value.nutrientAr
          : nutrientAr // ignore: cast_nullable_to_non_nullable
              as String,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as String,
      visualSymptoms: null == visualSymptoms
          ? _value._visualSymptoms
          : visualSymptoms // ignore: cast_nullable_to_non_nullable
              as List<String>,
      visualSymptomsAr: null == visualSymptomsAr
          ? _value._visualSymptomsAr
          : visualSymptomsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      recommendation: null == recommendation
          ? _value.recommendation
          : recommendation // ignore: cast_nullable_to_non_nullable
              as String,
      recommendationAr: null == recommendationAr
          ? _value.recommendationAr
          : recommendationAr // ignore: cast_nullable_to_non_nullable
              as String,
      imageUrl: null == imageUrl
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DeficiencySymptomImpl implements _DeficiencySymptom {
  const _$DeficiencySymptomImpl(
      {required this.nutrient,
      required this.nutrientAr,
      required this.severity,
      required final List<String> visualSymptoms,
      required final List<String> visualSymptomsAr,
      required this.recommendation,
      required this.recommendationAr,
      this.imageUrl = ''})
      : _visualSymptoms = visualSymptoms,
        _visualSymptomsAr = visualSymptomsAr;

  factory _$DeficiencySymptomImpl.fromJson(Map<String, dynamic> json) =>
      _$$DeficiencySymptomImplFromJson(json);

  @override
  final String nutrient;
  @override
  final String nutrientAr;
  @override
  final String severity;
// low, medium, high, critical
  final List<String> _visualSymptoms;
// low, medium, high, critical
  @override
  List<String> get visualSymptoms {
    if (_visualSymptoms is EqualUnmodifiableListView) return _visualSymptoms;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_visualSymptoms);
  }

  final List<String> _visualSymptomsAr;
  @override
  List<String> get visualSymptomsAr {
    if (_visualSymptomsAr is EqualUnmodifiableListView)
      return _visualSymptomsAr;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_visualSymptomsAr);
  }

  @override
  final String recommendation;
  @override
  final String recommendationAr;
  @override
  @JsonKey()
  final String imageUrl;

  @override
  String toString() {
    return 'DeficiencySymptom(nutrient: $nutrient, nutrientAr: $nutrientAr, severity: $severity, visualSymptoms: $visualSymptoms, visualSymptomsAr: $visualSymptomsAr, recommendation: $recommendation, recommendationAr: $recommendationAr, imageUrl: $imageUrl)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DeficiencySymptomImpl &&
            (identical(other.nutrient, nutrient) ||
                other.nutrient == nutrient) &&
            (identical(other.nutrientAr, nutrientAr) ||
                other.nutrientAr == nutrientAr) &&
            (identical(other.severity, severity) ||
                other.severity == severity) &&
            const DeepCollectionEquality()
                .equals(other._visualSymptoms, _visualSymptoms) &&
            const DeepCollectionEquality()
                .equals(other._visualSymptomsAr, _visualSymptomsAr) &&
            (identical(other.recommendation, recommendation) ||
                other.recommendation == recommendation) &&
            (identical(other.recommendationAr, recommendationAr) ||
                other.recommendationAr == recommendationAr) &&
            (identical(other.imageUrl, imageUrl) ||
                other.imageUrl == imageUrl));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      nutrient,
      nutrientAr,
      severity,
      const DeepCollectionEquality().hash(_visualSymptoms),
      const DeepCollectionEquality().hash(_visualSymptomsAr),
      recommendation,
      recommendationAr,
      imageUrl);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$DeficiencySymptomImplCopyWith<_$DeficiencySymptomImpl> get copyWith =>
      __$$DeficiencySymptomImplCopyWithImpl<_$DeficiencySymptomImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DeficiencySymptomImplToJson(
      this,
    );
  }
}

abstract class _DeficiencySymptom implements DeficiencySymptom {
  const factory _DeficiencySymptom(
      {required final String nutrient,
      required final String nutrientAr,
      required final String severity,
      required final List<String> visualSymptoms,
      required final List<String> visualSymptomsAr,
      required final String recommendation,
      required final String recommendationAr,
      final String imageUrl}) = _$DeficiencySymptomImpl;

  factory _DeficiencySymptom.fromJson(Map<String, dynamic> json) =
      _$DeficiencySymptomImpl.fromJson;

  @override
  String get nutrient;
  @override
  String get nutrientAr;
  @override
  String get severity;
  @override // low, medium, high, critical
  List<String> get visualSymptoms;
  @override
  List<String> get visualSymptomsAr;
  @override
  String get recommendation;
  @override
  String get recommendationAr;
  @override
  String get imageUrl;
  @override
  @JsonKey(ignore: true)
  _$$DeficiencySymptomImplCopyWith<_$DeficiencySymptomImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SoilInterpretation _$SoilInterpretationFromJson(Map<String, dynamic> json) {
  return _SoilInterpretation.fromJson(json);
}

/// @nodoc
mixin _$SoilInterpretation {
  String get overallHealth =>
      throw _privateConstructorUsedError; // excellent, good, fair, poor
  String get overallHealthAr => throw _privateConstructorUsedError;
  Map<String, String> get nutrientLevels =>
      throw _privateConstructorUsedError; // nutrient -> level
  Map<String, String> get nutrientLevelsAr =>
      throw _privateConstructorUsedError;
  List<String> get recommendations => throw _privateConstructorUsedError;
  List<String> get recommendationsAr => throw _privateConstructorUsedError;
  double get fertilitySCore => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $SoilInterpretationCopyWith<SoilInterpretation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SoilInterpretationCopyWith<$Res> {
  factory $SoilInterpretationCopyWith(
          SoilInterpretation value, $Res Function(SoilInterpretation) then) =
      _$SoilInterpretationCopyWithImpl<$Res, SoilInterpretation>;
  @useResult
  $Res call(
      {String overallHealth,
      String overallHealthAr,
      Map<String, String> nutrientLevels,
      Map<String, String> nutrientLevelsAr,
      List<String> recommendations,
      List<String> recommendationsAr,
      double fertilitySCore});
}

/// @nodoc
class _$SoilInterpretationCopyWithImpl<$Res, $Val extends SoilInterpretation>
    implements $SoilInterpretationCopyWith<$Res> {
  _$SoilInterpretationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? overallHealth = null,
    Object? overallHealthAr = null,
    Object? nutrientLevels = null,
    Object? nutrientLevelsAr = null,
    Object? recommendations = null,
    Object? recommendationsAr = null,
    Object? fertilitySCore = null,
  }) {
    return _then(_value.copyWith(
      overallHealth: null == overallHealth
          ? _value.overallHealth
          : overallHealth // ignore: cast_nullable_to_non_nullable
              as String,
      overallHealthAr: null == overallHealthAr
          ? _value.overallHealthAr
          : overallHealthAr // ignore: cast_nullable_to_non_nullable
              as String,
      nutrientLevels: null == nutrientLevels
          ? _value.nutrientLevels
          : nutrientLevels // ignore: cast_nullable_to_non_nullable
              as Map<String, String>,
      nutrientLevelsAr: null == nutrientLevelsAr
          ? _value.nutrientLevelsAr
          : nutrientLevelsAr // ignore: cast_nullable_to_non_nullable
              as Map<String, String>,
      recommendations: null == recommendations
          ? _value.recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as List<String>,
      recommendationsAr: null == recommendationsAr
          ? _value.recommendationsAr
          : recommendationsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      fertilitySCore: null == fertilitySCore
          ? _value.fertilitySCore
          : fertilitySCore // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SoilInterpretationImplCopyWith<$Res>
    implements $SoilInterpretationCopyWith<$Res> {
  factory _$$SoilInterpretationImplCopyWith(_$SoilInterpretationImpl value,
          $Res Function(_$SoilInterpretationImpl) then) =
      __$$SoilInterpretationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String overallHealth,
      String overallHealthAr,
      Map<String, String> nutrientLevels,
      Map<String, String> nutrientLevelsAr,
      List<String> recommendations,
      List<String> recommendationsAr,
      double fertilitySCore});
}

/// @nodoc
class __$$SoilInterpretationImplCopyWithImpl<$Res>
    extends _$SoilInterpretationCopyWithImpl<$Res, _$SoilInterpretationImpl>
    implements _$$SoilInterpretationImplCopyWith<$Res> {
  __$$SoilInterpretationImplCopyWithImpl(_$SoilInterpretationImpl _value,
      $Res Function(_$SoilInterpretationImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? overallHealth = null,
    Object? overallHealthAr = null,
    Object? nutrientLevels = null,
    Object? nutrientLevelsAr = null,
    Object? recommendations = null,
    Object? recommendationsAr = null,
    Object? fertilitySCore = null,
  }) {
    return _then(_$SoilInterpretationImpl(
      overallHealth: null == overallHealth
          ? _value.overallHealth
          : overallHealth // ignore: cast_nullable_to_non_nullable
              as String,
      overallHealthAr: null == overallHealthAr
          ? _value.overallHealthAr
          : overallHealthAr // ignore: cast_nullable_to_non_nullable
              as String,
      nutrientLevels: null == nutrientLevels
          ? _value._nutrientLevels
          : nutrientLevels // ignore: cast_nullable_to_non_nullable
              as Map<String, String>,
      nutrientLevelsAr: null == nutrientLevelsAr
          ? _value._nutrientLevelsAr
          : nutrientLevelsAr // ignore: cast_nullable_to_non_nullable
              as Map<String, String>,
      recommendations: null == recommendations
          ? _value._recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as List<String>,
      recommendationsAr: null == recommendationsAr
          ? _value._recommendationsAr
          : recommendationsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      fertilitySCore: null == fertilitySCore
          ? _value.fertilitySCore
          : fertilitySCore // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SoilInterpretationImpl implements _SoilInterpretation {
  const _$SoilInterpretationImpl(
      {required this.overallHealth,
      required this.overallHealthAr,
      required final Map<String, String> nutrientLevels,
      required final Map<String, String> nutrientLevelsAr,
      required final List<String> recommendations,
      required final List<String> recommendationsAr,
      required this.fertilitySCore})
      : _nutrientLevels = nutrientLevels,
        _nutrientLevelsAr = nutrientLevelsAr,
        _recommendations = recommendations,
        _recommendationsAr = recommendationsAr;

  factory _$SoilInterpretationImpl.fromJson(Map<String, dynamic> json) =>
      _$$SoilInterpretationImplFromJson(json);

  @override
  final String overallHealth;
// excellent, good, fair, poor
  @override
  final String overallHealthAr;
  final Map<String, String> _nutrientLevels;
  @override
  Map<String, String> get nutrientLevels {
    if (_nutrientLevels is EqualUnmodifiableMapView) return _nutrientLevels;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_nutrientLevels);
  }

// nutrient -> level
  final Map<String, String> _nutrientLevelsAr;
// nutrient -> level
  @override
  Map<String, String> get nutrientLevelsAr {
    if (_nutrientLevelsAr is EqualUnmodifiableMapView) return _nutrientLevelsAr;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_nutrientLevelsAr);
  }

  final List<String> _recommendations;
  @override
  List<String> get recommendations {
    if (_recommendations is EqualUnmodifiableListView) return _recommendations;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_recommendations);
  }

  final List<String> _recommendationsAr;
  @override
  List<String> get recommendationsAr {
    if (_recommendationsAr is EqualUnmodifiableListView)
      return _recommendationsAr;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_recommendationsAr);
  }

  @override
  final double fertilitySCore;

  @override
  String toString() {
    return 'SoilInterpretation(overallHealth: $overallHealth, overallHealthAr: $overallHealthAr, nutrientLevels: $nutrientLevels, nutrientLevelsAr: $nutrientLevelsAr, recommendations: $recommendations, recommendationsAr: $recommendationsAr, fertilitySCore: $fertilitySCore)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SoilInterpretationImpl &&
            (identical(other.overallHealth, overallHealth) ||
                other.overallHealth == overallHealth) &&
            (identical(other.overallHealthAr, overallHealthAr) ||
                other.overallHealthAr == overallHealthAr) &&
            const DeepCollectionEquality()
                .equals(other._nutrientLevels, _nutrientLevels) &&
            const DeepCollectionEquality()
                .equals(other._nutrientLevelsAr, _nutrientLevelsAr) &&
            const DeepCollectionEquality()
                .equals(other._recommendations, _recommendations) &&
            const DeepCollectionEquality()
                .equals(other._recommendationsAr, _recommendationsAr) &&
            (identical(other.fertilitySCore, fertilitySCore) ||
                other.fertilitySCore == fertilitySCore));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      overallHealth,
      overallHealthAr,
      const DeepCollectionEquality().hash(_nutrientLevels),
      const DeepCollectionEquality().hash(_nutrientLevelsAr),
      const DeepCollectionEquality().hash(_recommendations),
      const DeepCollectionEquality().hash(_recommendationsAr),
      fertilitySCore);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$SoilInterpretationImplCopyWith<_$SoilInterpretationImpl> get copyWith =>
      __$$SoilInterpretationImplCopyWithImpl<_$SoilInterpretationImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SoilInterpretationImplToJson(
      this,
    );
  }
}

abstract class _SoilInterpretation implements SoilInterpretation {
  const factory _SoilInterpretation(
      {required final String overallHealth,
      required final String overallHealthAr,
      required final Map<String, String> nutrientLevels,
      required final Map<String, String> nutrientLevelsAr,
      required final List<String> recommendations,
      required final List<String> recommendationsAr,
      required final double fertilitySCore}) = _$SoilInterpretationImpl;

  factory _SoilInterpretation.fromJson(Map<String, dynamic> json) =
      _$SoilInterpretationImpl.fromJson;

  @override
  String get overallHealth;
  @override // excellent, good, fair, poor
  String get overallHealthAr;
  @override
  Map<String, String> get nutrientLevels;
  @override // nutrient -> level
  Map<String, String> get nutrientLevelsAr;
  @override
  List<String> get recommendations;
  @override
  List<String> get recommendationsAr;
  @override
  double get fertilitySCore;
  @override
  @JsonKey(ignore: true)
  _$$SoilInterpretationImplCopyWith<_$SoilInterpretationImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CropTypeOption _$CropTypeOptionFromJson(Map<String, dynamic> json) {
  return _CropTypeOption.fromJson(json);
}

/// @nodoc
mixin _$CropTypeOption {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;
  String get category => throw _privateConstructorUsedError;
  String get categoryAr => throw _privateConstructorUsedError;
  List<String> get growthStages => throw _privateConstructorUsedError;
  List<String> get growthStagesAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $CropTypeOptionCopyWith<CropTypeOption> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CropTypeOptionCopyWith<$Res> {
  factory $CropTypeOptionCopyWith(
          CropTypeOption value, $Res Function(CropTypeOption) then) =
      _$CropTypeOptionCopyWithImpl<$Res, CropTypeOption>;
  @useResult
  $Res call(
      {String id,
      String name,
      String nameAr,
      String category,
      String categoryAr,
      List<String> growthStages,
      List<String> growthStagesAr});
}

/// @nodoc
class _$CropTypeOptionCopyWithImpl<$Res, $Val extends CropTypeOption>
    implements $CropTypeOptionCopyWith<$Res> {
  _$CropTypeOptionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? nameAr = null,
    Object? category = null,
    Object? categoryAr = null,
    Object? growthStages = null,
    Object? growthStagesAr = null,
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
      category: null == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      categoryAr: null == categoryAr
          ? _value.categoryAr
          : categoryAr // ignore: cast_nullable_to_non_nullable
              as String,
      growthStages: null == growthStages
          ? _value.growthStages
          : growthStages // ignore: cast_nullable_to_non_nullable
              as List<String>,
      growthStagesAr: null == growthStagesAr
          ? _value.growthStagesAr
          : growthStagesAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CropTypeOptionImplCopyWith<$Res>
    implements $CropTypeOptionCopyWith<$Res> {
  factory _$$CropTypeOptionImplCopyWith(_$CropTypeOptionImpl value,
          $Res Function(_$CropTypeOptionImpl) then) =
      __$$CropTypeOptionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String nameAr,
      String category,
      String categoryAr,
      List<String> growthStages,
      List<String> growthStagesAr});
}

/// @nodoc
class __$$CropTypeOptionImplCopyWithImpl<$Res>
    extends _$CropTypeOptionCopyWithImpl<$Res, _$CropTypeOptionImpl>
    implements _$$CropTypeOptionImplCopyWith<$Res> {
  __$$CropTypeOptionImplCopyWithImpl(
      _$CropTypeOptionImpl _value, $Res Function(_$CropTypeOptionImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? nameAr = null,
    Object? category = null,
    Object? categoryAr = null,
    Object? growthStages = null,
    Object? growthStagesAr = null,
  }) {
    return _then(_$CropTypeOptionImpl(
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
      category: null == category
          ? _value.category
          : category // ignore: cast_nullable_to_non_nullable
              as String,
      categoryAr: null == categoryAr
          ? _value.categoryAr
          : categoryAr // ignore: cast_nullable_to_non_nullable
              as String,
      growthStages: null == growthStages
          ? _value._growthStages
          : growthStages // ignore: cast_nullable_to_non_nullable
              as List<String>,
      growthStagesAr: null == growthStagesAr
          ? _value._growthStagesAr
          : growthStagesAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CropTypeOptionImpl implements _CropTypeOption {
  const _$CropTypeOptionImpl(
      {required this.id,
      required this.name,
      required this.nameAr,
      required this.category,
      required this.categoryAr,
      final List<String> growthStages = const [],
      final List<String> growthStagesAr = const []})
      : _growthStages = growthStages,
        _growthStagesAr = growthStagesAr;

  factory _$CropTypeOptionImpl.fromJson(Map<String, dynamic> json) =>
      _$$CropTypeOptionImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String nameAr;
  @override
  final String category;
  @override
  final String categoryAr;
  final List<String> _growthStages;
  @override
  @JsonKey()
  List<String> get growthStages {
    if (_growthStages is EqualUnmodifiableListView) return _growthStages;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_growthStages);
  }

  final List<String> _growthStagesAr;
  @override
  @JsonKey()
  List<String> get growthStagesAr {
    if (_growthStagesAr is EqualUnmodifiableListView) return _growthStagesAr;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_growthStagesAr);
  }

  @override
  String toString() {
    return 'CropTypeOption(id: $id, name: $name, nameAr: $nameAr, category: $category, categoryAr: $categoryAr, growthStages: $growthStages, growthStagesAr: $growthStagesAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CropTypeOptionImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.category, category) ||
                other.category == category) &&
            (identical(other.categoryAr, categoryAr) ||
                other.categoryAr == categoryAr) &&
            const DeepCollectionEquality()
                .equals(other._growthStages, _growthStages) &&
            const DeepCollectionEquality()
                .equals(other._growthStagesAr, _growthStagesAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      nameAr,
      category,
      categoryAr,
      const DeepCollectionEquality().hash(_growthStages),
      const DeepCollectionEquality().hash(_growthStagesAr));

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$CropTypeOptionImplCopyWith<_$CropTypeOptionImpl> get copyWith =>
      __$$CropTypeOptionImplCopyWithImpl<_$CropTypeOptionImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CropTypeOptionImplToJson(
      this,
    );
  }
}

abstract class _CropTypeOption implements CropTypeOption {
  const factory _CropTypeOption(
      {required final String id,
      required final String name,
      required final String nameAr,
      required final String category,
      required final String categoryAr,
      final List<String> growthStages,
      final List<String> growthStagesAr}) = _$CropTypeOptionImpl;

  factory _CropTypeOption.fromJson(Map<String, dynamic> json) =
      _$CropTypeOptionImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get nameAr;
  @override
  String get category;
  @override
  String get categoryAr;
  @override
  List<String> get growthStages;
  @override
  List<String> get growthStagesAr;
  @override
  @JsonKey(ignore: true)
  _$$CropTypeOptionImplCopyWith<_$CropTypeOptionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
