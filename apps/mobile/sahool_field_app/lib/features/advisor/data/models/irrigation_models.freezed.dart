// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'irrigation_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

IrrigationRequest _$IrrigationRequestFromJson(Map<String, dynamic> json) {
  return _IrrigationRequest.fromJson(json);
}

/// @nodoc
mixin _$IrrigationRequest {
  String get cropType => throw _privateConstructorUsedError;
  String get growthStage => throw _privateConstructorUsedError;
  double get fieldArea => throw _privateConstructorUsedError; // hectares
  String get soilType => throw _privateConstructorUsedError;
  String get irrigationMethod =>
      throw _privateConstructorUsedError; // drip, sprinkler, flood, pivot
  double get currentSoilMoisture => throw _privateConstructorUsedError; // %
  double get temperature => throw _privateConstructorUsedError; // °C
  double get humidity => throw _privateConstructorUsedError; // %
  String get governorate => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $IrrigationRequestCopyWith<IrrigationRequest> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IrrigationRequestCopyWith<$Res> {
  factory $IrrigationRequestCopyWith(
          IrrigationRequest value, $Res Function(IrrigationRequest) then) =
      _$IrrigationRequestCopyWithImpl<$Res, IrrigationRequest>;
  @useResult
  $Res call(
      {String cropType,
      String growthStage,
      double fieldArea,
      String soilType,
      String irrigationMethod,
      double currentSoilMoisture,
      double temperature,
      double humidity,
      String governorate});
}

/// @nodoc
class _$IrrigationRequestCopyWithImpl<$Res, $Val extends IrrigationRequest>
    implements $IrrigationRequestCopyWith<$Res> {
  _$IrrigationRequestCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropType = null,
    Object? growthStage = null,
    Object? fieldArea = null,
    Object? soilType = null,
    Object? irrigationMethod = null,
    Object? currentSoilMoisture = null,
    Object? temperature = null,
    Object? humidity = null,
    Object? governorate = null,
  }) {
    return _then(_value.copyWith(
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      fieldArea: null == fieldArea
          ? _value.fieldArea
          : fieldArea // ignore: cast_nullable_to_non_nullable
              as double,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      irrigationMethod: null == irrigationMethod
          ? _value.irrigationMethod
          : irrigationMethod // ignore: cast_nullable_to_non_nullable
              as String,
      currentSoilMoisture: null == currentSoilMoisture
          ? _value.currentSoilMoisture
          : currentSoilMoisture // ignore: cast_nullable_to_non_nullable
              as double,
      temperature: null == temperature
          ? _value.temperature
          : temperature // ignore: cast_nullable_to_non_nullable
              as double,
      humidity: null == humidity
          ? _value.humidity
          : humidity // ignore: cast_nullable_to_non_nullable
              as double,
      governorate: null == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IrrigationRequestImplCopyWith<$Res>
    implements $IrrigationRequestCopyWith<$Res> {
  factory _$$IrrigationRequestImplCopyWith(_$IrrigationRequestImpl value,
          $Res Function(_$IrrigationRequestImpl) then) =
      __$$IrrigationRequestImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String cropType,
      String growthStage,
      double fieldArea,
      String soilType,
      String irrigationMethod,
      double currentSoilMoisture,
      double temperature,
      double humidity,
      String governorate});
}

/// @nodoc
class __$$IrrigationRequestImplCopyWithImpl<$Res>
    extends _$IrrigationRequestCopyWithImpl<$Res, _$IrrigationRequestImpl>
    implements _$$IrrigationRequestImplCopyWith<$Res> {
  __$$IrrigationRequestImplCopyWithImpl(_$IrrigationRequestImpl _value,
      $Res Function(_$IrrigationRequestImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropType = null,
    Object? growthStage = null,
    Object? fieldArea = null,
    Object? soilType = null,
    Object? irrigationMethod = null,
    Object? currentSoilMoisture = null,
    Object? temperature = null,
    Object? humidity = null,
    Object? governorate = null,
  }) {
    return _then(_$IrrigationRequestImpl(
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      fieldArea: null == fieldArea
          ? _value.fieldArea
          : fieldArea // ignore: cast_nullable_to_non_nullable
              as double,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      irrigationMethod: null == irrigationMethod
          ? _value.irrigationMethod
          : irrigationMethod // ignore: cast_nullable_to_non_nullable
              as String,
      currentSoilMoisture: null == currentSoilMoisture
          ? _value.currentSoilMoisture
          : currentSoilMoisture // ignore: cast_nullable_to_non_nullable
              as double,
      temperature: null == temperature
          ? _value.temperature
          : temperature // ignore: cast_nullable_to_non_nullable
              as double,
      humidity: null == humidity
          ? _value.humidity
          : humidity // ignore: cast_nullable_to_non_nullable
              as double,
      governorate: null == governorate
          ? _value.governorate
          : governorate // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IrrigationRequestImpl implements _IrrigationRequest {
  const _$IrrigationRequestImpl(
      {required this.cropType,
      required this.growthStage,
      required this.fieldArea,
      required this.soilType,
      required this.irrigationMethod,
      this.currentSoilMoisture = 0,
      this.temperature = 0,
      this.humidity = 0,
      this.governorate = ''});

  factory _$IrrigationRequestImpl.fromJson(Map<String, dynamic> json) =>
      _$$IrrigationRequestImplFromJson(json);

  @override
  final String cropType;
  @override
  final String growthStage;
  @override
  final double fieldArea;
// hectares
  @override
  final String soilType;
  @override
  final String irrigationMethod;
// drip, sprinkler, flood, pivot
  @override
  @JsonKey()
  final double currentSoilMoisture;
// %
  @override
  @JsonKey()
  final double temperature;
// °C
  @override
  @JsonKey()
  final double humidity;
// %
  @override
  @JsonKey()
  final String governorate;

  @override
  String toString() {
    return 'IrrigationRequest(cropType: $cropType, growthStage: $growthStage, fieldArea: $fieldArea, soilType: $soilType, irrigationMethod: $irrigationMethod, currentSoilMoisture: $currentSoilMoisture, temperature: $temperature, humidity: $humidity, governorate: $governorate)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IrrigationRequestImpl &&
            (identical(other.cropType, cropType) ||
                other.cropType == cropType) &&
            (identical(other.growthStage, growthStage) ||
                other.growthStage == growthStage) &&
            (identical(other.fieldArea, fieldArea) ||
                other.fieldArea == fieldArea) &&
            (identical(other.soilType, soilType) ||
                other.soilType == soilType) &&
            (identical(other.irrigationMethod, irrigationMethod) ||
                other.irrigationMethod == irrigationMethod) &&
            (identical(other.currentSoilMoisture, currentSoilMoisture) ||
                other.currentSoilMoisture == currentSoilMoisture) &&
            (identical(other.temperature, temperature) ||
                other.temperature == temperature) &&
            (identical(other.humidity, humidity) ||
                other.humidity == humidity) &&
            (identical(other.governorate, governorate) ||
                other.governorate == governorate));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      cropType,
      growthStage,
      fieldArea,
      soilType,
      irrigationMethod,
      currentSoilMoisture,
      temperature,
      humidity,
      governorate);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$IrrigationRequestImplCopyWith<_$IrrigationRequestImpl> get copyWith =>
      __$$IrrigationRequestImplCopyWithImpl<_$IrrigationRequestImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IrrigationRequestImplToJson(
      this,
    );
  }
}

abstract class _IrrigationRequest implements IrrigationRequest {
  const factory _IrrigationRequest(
      {required final String cropType,
      required final String growthStage,
      required final double fieldArea,
      required final String soilType,
      required final String irrigationMethod,
      final double currentSoilMoisture,
      final double temperature,
      final double humidity,
      final String governorate}) = _$IrrigationRequestImpl;

  factory _IrrigationRequest.fromJson(Map<String, dynamic> json) =
      _$IrrigationRequestImpl.fromJson;

  @override
  String get cropType;
  @override
  String get growthStage;
  @override
  double get fieldArea;
  @override // hectares
  String get soilType;
  @override
  String get irrigationMethod;
  @override // drip, sprinkler, flood, pivot
  double get currentSoilMoisture;
  @override // %
  double get temperature;
  @override // °C
  double get humidity;
  @override // %
  String get governorate;
  @override
  @JsonKey(ignore: true)
  _$$IrrigationRequestImplCopyWith<_$IrrigationRequestImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

IrrigationCalculation _$IrrigationCalculationFromJson(
    Map<String, dynamic> json) {
  return _IrrigationCalculation.fromJson(json);
}

/// @nodoc
mixin _$IrrigationCalculation {
  double get waterRequirementMm => throw _privateConstructorUsedError; // mm/day
  double get waterRequirementLiters =>
      throw _privateConstructorUsedError; // liters/hectare/day
  double get totalWaterLiters =>
      throw _privateConstructorUsedError; // total for field
  double get etCrop =>
      throw _privateConstructorUsedError; // crop evapotranspiration
  double get irrigationEfficiency => throw _privateConstructorUsedError; // %
  String get recommendedFrequency => throw _privateConstructorUsedError;
  String get recommendedFrequencyAr => throw _privateConstructorUsedError;
  int get durationMinutes => throw _privateConstructorUsedError;
  String get notes => throw _privateConstructorUsedError;
  String get notesAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $IrrigationCalculationCopyWith<IrrigationCalculation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IrrigationCalculationCopyWith<$Res> {
  factory $IrrigationCalculationCopyWith(IrrigationCalculation value,
          $Res Function(IrrigationCalculation) then) =
      _$IrrigationCalculationCopyWithImpl<$Res, IrrigationCalculation>;
  @useResult
  $Res call(
      {double waterRequirementMm,
      double waterRequirementLiters,
      double totalWaterLiters,
      double etCrop,
      double irrigationEfficiency,
      String recommendedFrequency,
      String recommendedFrequencyAr,
      int durationMinutes,
      String notes,
      String notesAr});
}

/// @nodoc
class _$IrrigationCalculationCopyWithImpl<$Res,
        $Val extends IrrigationCalculation>
    implements $IrrigationCalculationCopyWith<$Res> {
  _$IrrigationCalculationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? waterRequirementMm = null,
    Object? waterRequirementLiters = null,
    Object? totalWaterLiters = null,
    Object? etCrop = null,
    Object? irrigationEfficiency = null,
    Object? recommendedFrequency = null,
    Object? recommendedFrequencyAr = null,
    Object? durationMinutes = null,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_value.copyWith(
      waterRequirementMm: null == waterRequirementMm
          ? _value.waterRequirementMm
          : waterRequirementMm // ignore: cast_nullable_to_non_nullable
              as double,
      waterRequirementLiters: null == waterRequirementLiters
          ? _value.waterRequirementLiters
          : waterRequirementLiters // ignore: cast_nullable_to_non_nullable
              as double,
      totalWaterLiters: null == totalWaterLiters
          ? _value.totalWaterLiters
          : totalWaterLiters // ignore: cast_nullable_to_non_nullable
              as double,
      etCrop: null == etCrop
          ? _value.etCrop
          : etCrop // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationEfficiency: null == irrigationEfficiency
          ? _value.irrigationEfficiency
          : irrigationEfficiency // ignore: cast_nullable_to_non_nullable
              as double,
      recommendedFrequency: null == recommendedFrequency
          ? _value.recommendedFrequency
          : recommendedFrequency // ignore: cast_nullable_to_non_nullable
              as String,
      recommendedFrequencyAr: null == recommendedFrequencyAr
          ? _value.recommendedFrequencyAr
          : recommendedFrequencyAr // ignore: cast_nullable_to_non_nullable
              as String,
      durationMinutes: null == durationMinutes
          ? _value.durationMinutes
          : durationMinutes // ignore: cast_nullable_to_non_nullable
              as int,
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
abstract class _$$IrrigationCalculationImplCopyWith<$Res>
    implements $IrrigationCalculationCopyWith<$Res> {
  factory _$$IrrigationCalculationImplCopyWith(
          _$IrrigationCalculationImpl value,
          $Res Function(_$IrrigationCalculationImpl) then) =
      __$$IrrigationCalculationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {double waterRequirementMm,
      double waterRequirementLiters,
      double totalWaterLiters,
      double etCrop,
      double irrigationEfficiency,
      String recommendedFrequency,
      String recommendedFrequencyAr,
      int durationMinutes,
      String notes,
      String notesAr});
}

/// @nodoc
class __$$IrrigationCalculationImplCopyWithImpl<$Res>
    extends _$IrrigationCalculationCopyWithImpl<$Res,
        _$IrrigationCalculationImpl>
    implements _$$IrrigationCalculationImplCopyWith<$Res> {
  __$$IrrigationCalculationImplCopyWithImpl(_$IrrigationCalculationImpl _value,
      $Res Function(_$IrrigationCalculationImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? waterRequirementMm = null,
    Object? waterRequirementLiters = null,
    Object? totalWaterLiters = null,
    Object? etCrop = null,
    Object? irrigationEfficiency = null,
    Object? recommendedFrequency = null,
    Object? recommendedFrequencyAr = null,
    Object? durationMinutes = null,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_$IrrigationCalculationImpl(
      waterRequirementMm: null == waterRequirementMm
          ? _value.waterRequirementMm
          : waterRequirementMm // ignore: cast_nullable_to_non_nullable
              as double,
      waterRequirementLiters: null == waterRequirementLiters
          ? _value.waterRequirementLiters
          : waterRequirementLiters // ignore: cast_nullable_to_non_nullable
              as double,
      totalWaterLiters: null == totalWaterLiters
          ? _value.totalWaterLiters
          : totalWaterLiters // ignore: cast_nullable_to_non_nullable
              as double,
      etCrop: null == etCrop
          ? _value.etCrop
          : etCrop // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationEfficiency: null == irrigationEfficiency
          ? _value.irrigationEfficiency
          : irrigationEfficiency // ignore: cast_nullable_to_non_nullable
              as double,
      recommendedFrequency: null == recommendedFrequency
          ? _value.recommendedFrequency
          : recommendedFrequency // ignore: cast_nullable_to_non_nullable
              as String,
      recommendedFrequencyAr: null == recommendedFrequencyAr
          ? _value.recommendedFrequencyAr
          : recommendedFrequencyAr // ignore: cast_nullable_to_non_nullable
              as String,
      durationMinutes: null == durationMinutes
          ? _value.durationMinutes
          : durationMinutes // ignore: cast_nullable_to_non_nullable
              as int,
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
class _$IrrigationCalculationImpl implements _IrrigationCalculation {
  const _$IrrigationCalculationImpl(
      {required this.waterRequirementMm,
      required this.waterRequirementLiters,
      required this.totalWaterLiters,
      required this.etCrop,
      required this.irrigationEfficiency,
      required this.recommendedFrequency,
      required this.recommendedFrequencyAr,
      required this.durationMinutes,
      this.notes = '',
      this.notesAr = ''});

  factory _$IrrigationCalculationImpl.fromJson(Map<String, dynamic> json) =>
      _$$IrrigationCalculationImplFromJson(json);

  @override
  final double waterRequirementMm;
// mm/day
  @override
  final double waterRequirementLiters;
// liters/hectare/day
  @override
  final double totalWaterLiters;
// total for field
  @override
  final double etCrop;
// crop evapotranspiration
  @override
  final double irrigationEfficiency;
// %
  @override
  final String recommendedFrequency;
  @override
  final String recommendedFrequencyAr;
  @override
  final int durationMinutes;
  @override
  @JsonKey()
  final String notes;
  @override
  @JsonKey()
  final String notesAr;

  @override
  String toString() {
    return 'IrrigationCalculation(waterRequirementMm: $waterRequirementMm, waterRequirementLiters: $waterRequirementLiters, totalWaterLiters: $totalWaterLiters, etCrop: $etCrop, irrigationEfficiency: $irrigationEfficiency, recommendedFrequency: $recommendedFrequency, recommendedFrequencyAr: $recommendedFrequencyAr, durationMinutes: $durationMinutes, notes: $notes, notesAr: $notesAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IrrigationCalculationImpl &&
            (identical(other.waterRequirementMm, waterRequirementMm) ||
                other.waterRequirementMm == waterRequirementMm) &&
            (identical(other.waterRequirementLiters, waterRequirementLiters) ||
                other.waterRequirementLiters == waterRequirementLiters) &&
            (identical(other.totalWaterLiters, totalWaterLiters) ||
                other.totalWaterLiters == totalWaterLiters) &&
            (identical(other.etCrop, etCrop) || other.etCrop == etCrop) &&
            (identical(other.irrigationEfficiency, irrigationEfficiency) ||
                other.irrigationEfficiency == irrigationEfficiency) &&
            (identical(other.recommendedFrequency, recommendedFrequency) ||
                other.recommendedFrequency == recommendedFrequency) &&
            (identical(other.recommendedFrequencyAr, recommendedFrequencyAr) ||
                other.recommendedFrequencyAr == recommendedFrequencyAr) &&
            (identical(other.durationMinutes, durationMinutes) ||
                other.durationMinutes == durationMinutes) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            (identical(other.notesAr, notesAr) || other.notesAr == notesAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      waterRequirementMm,
      waterRequirementLiters,
      totalWaterLiters,
      etCrop,
      irrigationEfficiency,
      recommendedFrequency,
      recommendedFrequencyAr,
      durationMinutes,
      notes,
      notesAr);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$IrrigationCalculationImplCopyWith<_$IrrigationCalculationImpl>
      get copyWith => __$$IrrigationCalculationImplCopyWithImpl<
          _$IrrigationCalculationImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IrrigationCalculationImplToJson(
      this,
    );
  }
}

abstract class _IrrigationCalculation implements IrrigationCalculation {
  const factory _IrrigationCalculation(
      {required final double waterRequirementMm,
      required final double waterRequirementLiters,
      required final double totalWaterLiters,
      required final double etCrop,
      required final double irrigationEfficiency,
      required final String recommendedFrequency,
      required final String recommendedFrequencyAr,
      required final int durationMinutes,
      final String notes,
      final String notesAr}) = _$IrrigationCalculationImpl;

  factory _IrrigationCalculation.fromJson(Map<String, dynamic> json) =
      _$IrrigationCalculationImpl.fromJson;

  @override
  double get waterRequirementMm;
  @override // mm/day
  double get waterRequirementLiters;
  @override // liters/hectare/day
  double get totalWaterLiters;
  @override // total for field
  double get etCrop;
  @override // crop evapotranspiration
  double get irrigationEfficiency;
  @override // %
  String get recommendedFrequency;
  @override
  String get recommendedFrequencyAr;
  @override
  int get durationMinutes;
  @override
  String get notes;
  @override
  String get notesAr;
  @override
  @JsonKey(ignore: true)
  _$$IrrigationCalculationImplCopyWith<_$IrrigationCalculationImpl>
      get copyWith => throw _privateConstructorUsedError;
}

IrrigationSchedule _$IrrigationScheduleFromJson(Map<String, dynamic> json) {
  return _IrrigationSchedule.fromJson(json);
}

/// @nodoc
mixin _$IrrigationSchedule {
  String get scheduleId => throw _privateConstructorUsedError;
  String get fieldId => throw _privateConstructorUsedError;
  List<IrrigationEvent> get events => throw _privateConstructorUsedError;
  DateTime get startDate => throw _privateConstructorUsedError;
  DateTime get endDate => throw _privateConstructorUsedError;
  double get totalWaterPlanned => throw _privateConstructorUsedError; // liters
  String get notes => throw _privateConstructorUsedError;
  String get notesAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $IrrigationScheduleCopyWith<IrrigationSchedule> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IrrigationScheduleCopyWith<$Res> {
  factory $IrrigationScheduleCopyWith(
          IrrigationSchedule value, $Res Function(IrrigationSchedule) then) =
      _$IrrigationScheduleCopyWithImpl<$Res, IrrigationSchedule>;
  @useResult
  $Res call(
      {String scheduleId,
      String fieldId,
      List<IrrigationEvent> events,
      DateTime startDate,
      DateTime endDate,
      double totalWaterPlanned,
      String notes,
      String notesAr});
}

/// @nodoc
class _$IrrigationScheduleCopyWithImpl<$Res, $Val extends IrrigationSchedule>
    implements $IrrigationScheduleCopyWith<$Res> {
  _$IrrigationScheduleCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? scheduleId = null,
    Object? fieldId = null,
    Object? events = null,
    Object? startDate = null,
    Object? endDate = null,
    Object? totalWaterPlanned = null,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_value.copyWith(
      scheduleId: null == scheduleId
          ? _value.scheduleId
          : scheduleId // ignore: cast_nullable_to_non_nullable
              as String,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      events: null == events
          ? _value.events
          : events // ignore: cast_nullable_to_non_nullable
              as List<IrrigationEvent>,
      startDate: null == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      endDate: null == endDate
          ? _value.endDate
          : endDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      totalWaterPlanned: null == totalWaterPlanned
          ? _value.totalWaterPlanned
          : totalWaterPlanned // ignore: cast_nullable_to_non_nullable
              as double,
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
abstract class _$$IrrigationScheduleImplCopyWith<$Res>
    implements $IrrigationScheduleCopyWith<$Res> {
  factory _$$IrrigationScheduleImplCopyWith(_$IrrigationScheduleImpl value,
          $Res Function(_$IrrigationScheduleImpl) then) =
      __$$IrrigationScheduleImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String scheduleId,
      String fieldId,
      List<IrrigationEvent> events,
      DateTime startDate,
      DateTime endDate,
      double totalWaterPlanned,
      String notes,
      String notesAr});
}

/// @nodoc
class __$$IrrigationScheduleImplCopyWithImpl<$Res>
    extends _$IrrigationScheduleCopyWithImpl<$Res, _$IrrigationScheduleImpl>
    implements _$$IrrigationScheduleImplCopyWith<$Res> {
  __$$IrrigationScheduleImplCopyWithImpl(_$IrrigationScheduleImpl _value,
      $Res Function(_$IrrigationScheduleImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? scheduleId = null,
    Object? fieldId = null,
    Object? events = null,
    Object? startDate = null,
    Object? endDate = null,
    Object? totalWaterPlanned = null,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_$IrrigationScheduleImpl(
      scheduleId: null == scheduleId
          ? _value.scheduleId
          : scheduleId // ignore: cast_nullable_to_non_nullable
              as String,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      events: null == events
          ? _value._events
          : events // ignore: cast_nullable_to_non_nullable
              as List<IrrigationEvent>,
      startDate: null == startDate
          ? _value.startDate
          : startDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      endDate: null == endDate
          ? _value.endDate
          : endDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
      totalWaterPlanned: null == totalWaterPlanned
          ? _value.totalWaterPlanned
          : totalWaterPlanned // ignore: cast_nullable_to_non_nullable
              as double,
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
class _$IrrigationScheduleImpl implements _IrrigationSchedule {
  const _$IrrigationScheduleImpl(
      {required this.scheduleId,
      required this.fieldId,
      required final List<IrrigationEvent> events,
      required this.startDate,
      required this.endDate,
      required this.totalWaterPlanned,
      this.notes = '',
      this.notesAr = ''})
      : _events = events;

  factory _$IrrigationScheduleImpl.fromJson(Map<String, dynamic> json) =>
      _$$IrrigationScheduleImplFromJson(json);

  @override
  final String scheduleId;
  @override
  final String fieldId;
  final List<IrrigationEvent> _events;
  @override
  List<IrrigationEvent> get events {
    if (_events is EqualUnmodifiableListView) return _events;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_events);
  }

  @override
  final DateTime startDate;
  @override
  final DateTime endDate;
  @override
  final double totalWaterPlanned;
// liters
  @override
  @JsonKey()
  final String notes;
  @override
  @JsonKey()
  final String notesAr;

  @override
  String toString() {
    return 'IrrigationSchedule(scheduleId: $scheduleId, fieldId: $fieldId, events: $events, startDate: $startDate, endDate: $endDate, totalWaterPlanned: $totalWaterPlanned, notes: $notes, notesAr: $notesAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IrrigationScheduleImpl &&
            (identical(other.scheduleId, scheduleId) ||
                other.scheduleId == scheduleId) &&
            (identical(other.fieldId, fieldId) || other.fieldId == fieldId) &&
            const DeepCollectionEquality().equals(other._events, _events) &&
            (identical(other.startDate, startDate) ||
                other.startDate == startDate) &&
            (identical(other.endDate, endDate) || other.endDate == endDate) &&
            (identical(other.totalWaterPlanned, totalWaterPlanned) ||
                other.totalWaterPlanned == totalWaterPlanned) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            (identical(other.notesAr, notesAr) || other.notesAr == notesAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      scheduleId,
      fieldId,
      const DeepCollectionEquality().hash(_events),
      startDate,
      endDate,
      totalWaterPlanned,
      notes,
      notesAr);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$IrrigationScheduleImplCopyWith<_$IrrigationScheduleImpl> get copyWith =>
      __$$IrrigationScheduleImplCopyWithImpl<_$IrrigationScheduleImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IrrigationScheduleImplToJson(
      this,
    );
  }
}

abstract class _IrrigationSchedule implements IrrigationSchedule {
  const factory _IrrigationSchedule(
      {required final String scheduleId,
      required final String fieldId,
      required final List<IrrigationEvent> events,
      required final DateTime startDate,
      required final DateTime endDate,
      required final double totalWaterPlanned,
      final String notes,
      final String notesAr}) = _$IrrigationScheduleImpl;

  factory _IrrigationSchedule.fromJson(Map<String, dynamic> json) =
      _$IrrigationScheduleImpl.fromJson;

  @override
  String get scheduleId;
  @override
  String get fieldId;
  @override
  List<IrrigationEvent> get events;
  @override
  DateTime get startDate;
  @override
  DateTime get endDate;
  @override
  double get totalWaterPlanned;
  @override // liters
  String get notes;
  @override
  String get notesAr;
  @override
  @JsonKey(ignore: true)
  _$$IrrigationScheduleImplCopyWith<_$IrrigationScheduleImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

IrrigationEvent _$IrrigationEventFromJson(Map<String, dynamic> json) {
  return _IrrigationEvent.fromJson(json);
}

/// @nodoc
mixin _$IrrigationEvent {
  String get eventId => throw _privateConstructorUsedError;
  DateTime get scheduledTime => throw _privateConstructorUsedError;
  int get durationMinutes => throw _privateConstructorUsedError;
  double get waterLiters => throw _privateConstructorUsedError;
  String get status =>
      throw _privateConstructorUsedError; // pending, in_progress, completed, skipped
  String get statusAr => throw _privateConstructorUsedError;
  String get notes => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $IrrigationEventCopyWith<IrrigationEvent> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IrrigationEventCopyWith<$Res> {
  factory $IrrigationEventCopyWith(
          IrrigationEvent value, $Res Function(IrrigationEvent) then) =
      _$IrrigationEventCopyWithImpl<$Res, IrrigationEvent>;
  @useResult
  $Res call(
      {String eventId,
      DateTime scheduledTime,
      int durationMinutes,
      double waterLiters,
      String status,
      String statusAr,
      String notes});
}

/// @nodoc
class _$IrrigationEventCopyWithImpl<$Res, $Val extends IrrigationEvent>
    implements $IrrigationEventCopyWith<$Res> {
  _$IrrigationEventCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? eventId = null,
    Object? scheduledTime = null,
    Object? durationMinutes = null,
    Object? waterLiters = null,
    Object? status = null,
    Object? statusAr = null,
    Object? notes = null,
  }) {
    return _then(_value.copyWith(
      eventId: null == eventId
          ? _value.eventId
          : eventId // ignore: cast_nullable_to_non_nullable
              as String,
      scheduledTime: null == scheduledTime
          ? _value.scheduledTime
          : scheduledTime // ignore: cast_nullable_to_non_nullable
              as DateTime,
      durationMinutes: null == durationMinutes
          ? _value.durationMinutes
          : durationMinutes // ignore: cast_nullable_to_non_nullable
              as int,
      waterLiters: null == waterLiters
          ? _value.waterLiters
          : waterLiters // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      statusAr: null == statusAr
          ? _value.statusAr
          : statusAr // ignore: cast_nullable_to_non_nullable
              as String,
      notes: null == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IrrigationEventImplCopyWith<$Res>
    implements $IrrigationEventCopyWith<$Res> {
  factory _$$IrrigationEventImplCopyWith(_$IrrigationEventImpl value,
          $Res Function(_$IrrigationEventImpl) then) =
      __$$IrrigationEventImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String eventId,
      DateTime scheduledTime,
      int durationMinutes,
      double waterLiters,
      String status,
      String statusAr,
      String notes});
}

/// @nodoc
class __$$IrrigationEventImplCopyWithImpl<$Res>
    extends _$IrrigationEventCopyWithImpl<$Res, _$IrrigationEventImpl>
    implements _$$IrrigationEventImplCopyWith<$Res> {
  __$$IrrigationEventImplCopyWithImpl(
      _$IrrigationEventImpl _value, $Res Function(_$IrrigationEventImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? eventId = null,
    Object? scheduledTime = null,
    Object? durationMinutes = null,
    Object? waterLiters = null,
    Object? status = null,
    Object? statusAr = null,
    Object? notes = null,
  }) {
    return _then(_$IrrigationEventImpl(
      eventId: null == eventId
          ? _value.eventId
          : eventId // ignore: cast_nullable_to_non_nullable
              as String,
      scheduledTime: null == scheduledTime
          ? _value.scheduledTime
          : scheduledTime // ignore: cast_nullable_to_non_nullable
              as DateTime,
      durationMinutes: null == durationMinutes
          ? _value.durationMinutes
          : durationMinutes // ignore: cast_nullable_to_non_nullable
              as int,
      waterLiters: null == waterLiters
          ? _value.waterLiters
          : waterLiters // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      statusAr: null == statusAr
          ? _value.statusAr
          : statusAr // ignore: cast_nullable_to_non_nullable
              as String,
      notes: null == notes
          ? _value.notes
          : notes // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IrrigationEventImpl implements _IrrigationEvent {
  const _$IrrigationEventImpl(
      {required this.eventId,
      required this.scheduledTime,
      required this.durationMinutes,
      required this.waterLiters,
      required this.status,
      required this.statusAr,
      this.notes = ''});

  factory _$IrrigationEventImpl.fromJson(Map<String, dynamic> json) =>
      _$$IrrigationEventImplFromJson(json);

  @override
  final String eventId;
  @override
  final DateTime scheduledTime;
  @override
  final int durationMinutes;
  @override
  final double waterLiters;
  @override
  final String status;
// pending, in_progress, completed, skipped
  @override
  final String statusAr;
  @override
  @JsonKey()
  final String notes;

  @override
  String toString() {
    return 'IrrigationEvent(eventId: $eventId, scheduledTime: $scheduledTime, durationMinutes: $durationMinutes, waterLiters: $waterLiters, status: $status, statusAr: $statusAr, notes: $notes)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IrrigationEventImpl &&
            (identical(other.eventId, eventId) || other.eventId == eventId) &&
            (identical(other.scheduledTime, scheduledTime) ||
                other.scheduledTime == scheduledTime) &&
            (identical(other.durationMinutes, durationMinutes) ||
                other.durationMinutes == durationMinutes) &&
            (identical(other.waterLiters, waterLiters) ||
                other.waterLiters == waterLiters) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.statusAr, statusAr) ||
                other.statusAr == statusAr) &&
            (identical(other.notes, notes) || other.notes == notes));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(runtimeType, eventId, scheduledTime,
      durationMinutes, waterLiters, status, statusAr, notes);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$IrrigationEventImplCopyWith<_$IrrigationEventImpl> get copyWith =>
      __$$IrrigationEventImplCopyWithImpl<_$IrrigationEventImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IrrigationEventImplToJson(
      this,
    );
  }
}

abstract class _IrrigationEvent implements IrrigationEvent {
  const factory _IrrigationEvent(
      {required final String eventId,
      required final DateTime scheduledTime,
      required final int durationMinutes,
      required final double waterLiters,
      required final String status,
      required final String statusAr,
      final String notes}) = _$IrrigationEventImpl;

  factory _IrrigationEvent.fromJson(Map<String, dynamic> json) =
      _$IrrigationEventImpl.fromJson;

  @override
  String get eventId;
  @override
  DateTime get scheduledTime;
  @override
  int get durationMinutes;
  @override
  double get waterLiters;
  @override
  String get status;
  @override // pending, in_progress, completed, skipped
  String get statusAr;
  @override
  String get notes;
  @override
  @JsonKey(ignore: true)
  _$$IrrigationEventImplCopyWith<_$IrrigationEventImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

WaterBalance _$WaterBalanceFromJson(Map<String, dynamic> json) {
  return _WaterBalance.fromJson(json);
}

/// @nodoc
mixin _$WaterBalance {
  double get soilMoisturePercent => throw _privateConstructorUsedError;
  double get fieldCapacity => throw _privateConstructorUsedError;
  double get wiltingPoint => throw _privateConstructorUsedError;
  double get availableWater => throw _privateConstructorUsedError;
  double get depletionPercent => throw _privateConstructorUsedError;
  String get status =>
      throw _privateConstructorUsedError; // optimal, low, critical, excess
  String get statusAr => throw _privateConstructorUsedError;
  bool get irrigationNeeded => throw _privateConstructorUsedError;
  double get recommendedWaterMm => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $WaterBalanceCopyWith<WaterBalance> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WaterBalanceCopyWith<$Res> {
  factory $WaterBalanceCopyWith(
          WaterBalance value, $Res Function(WaterBalance) then) =
      _$WaterBalanceCopyWithImpl<$Res, WaterBalance>;
  @useResult
  $Res call(
      {double soilMoisturePercent,
      double fieldCapacity,
      double wiltingPoint,
      double availableWater,
      double depletionPercent,
      String status,
      String statusAr,
      bool irrigationNeeded,
      double recommendedWaterMm});
}

/// @nodoc
class _$WaterBalanceCopyWithImpl<$Res, $Val extends WaterBalance>
    implements $WaterBalanceCopyWith<$Res> {
  _$WaterBalanceCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? soilMoisturePercent = null,
    Object? fieldCapacity = null,
    Object? wiltingPoint = null,
    Object? availableWater = null,
    Object? depletionPercent = null,
    Object? status = null,
    Object? statusAr = null,
    Object? irrigationNeeded = null,
    Object? recommendedWaterMm = null,
  }) {
    return _then(_value.copyWith(
      soilMoisturePercent: null == soilMoisturePercent
          ? _value.soilMoisturePercent
          : soilMoisturePercent // ignore: cast_nullable_to_non_nullable
              as double,
      fieldCapacity: null == fieldCapacity
          ? _value.fieldCapacity
          : fieldCapacity // ignore: cast_nullable_to_non_nullable
              as double,
      wiltingPoint: null == wiltingPoint
          ? _value.wiltingPoint
          : wiltingPoint // ignore: cast_nullable_to_non_nullable
              as double,
      availableWater: null == availableWater
          ? _value.availableWater
          : availableWater // ignore: cast_nullable_to_non_nullable
              as double,
      depletionPercent: null == depletionPercent
          ? _value.depletionPercent
          : depletionPercent // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      statusAr: null == statusAr
          ? _value.statusAr
          : statusAr // ignore: cast_nullable_to_non_nullable
              as String,
      irrigationNeeded: null == irrigationNeeded
          ? _value.irrigationNeeded
          : irrigationNeeded // ignore: cast_nullable_to_non_nullable
              as bool,
      recommendedWaterMm: null == recommendedWaterMm
          ? _value.recommendedWaterMm
          : recommendedWaterMm // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$WaterBalanceImplCopyWith<$Res>
    implements $WaterBalanceCopyWith<$Res> {
  factory _$$WaterBalanceImplCopyWith(
          _$WaterBalanceImpl value, $Res Function(_$WaterBalanceImpl) then) =
      __$$WaterBalanceImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {double soilMoisturePercent,
      double fieldCapacity,
      double wiltingPoint,
      double availableWater,
      double depletionPercent,
      String status,
      String statusAr,
      bool irrigationNeeded,
      double recommendedWaterMm});
}

/// @nodoc
class __$$WaterBalanceImplCopyWithImpl<$Res>
    extends _$WaterBalanceCopyWithImpl<$Res, _$WaterBalanceImpl>
    implements _$$WaterBalanceImplCopyWith<$Res> {
  __$$WaterBalanceImplCopyWithImpl(
      _$WaterBalanceImpl _value, $Res Function(_$WaterBalanceImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? soilMoisturePercent = null,
    Object? fieldCapacity = null,
    Object? wiltingPoint = null,
    Object? availableWater = null,
    Object? depletionPercent = null,
    Object? status = null,
    Object? statusAr = null,
    Object? irrigationNeeded = null,
    Object? recommendedWaterMm = null,
  }) {
    return _then(_$WaterBalanceImpl(
      soilMoisturePercent: null == soilMoisturePercent
          ? _value.soilMoisturePercent
          : soilMoisturePercent // ignore: cast_nullable_to_non_nullable
              as double,
      fieldCapacity: null == fieldCapacity
          ? _value.fieldCapacity
          : fieldCapacity // ignore: cast_nullable_to_non_nullable
              as double,
      wiltingPoint: null == wiltingPoint
          ? _value.wiltingPoint
          : wiltingPoint // ignore: cast_nullable_to_non_nullable
              as double,
      availableWater: null == availableWater
          ? _value.availableWater
          : availableWater // ignore: cast_nullable_to_non_nullable
              as double,
      depletionPercent: null == depletionPercent
          ? _value.depletionPercent
          : depletionPercent // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      statusAr: null == statusAr
          ? _value.statusAr
          : statusAr // ignore: cast_nullable_to_non_nullable
              as String,
      irrigationNeeded: null == irrigationNeeded
          ? _value.irrigationNeeded
          : irrigationNeeded // ignore: cast_nullable_to_non_nullable
              as bool,
      recommendedWaterMm: null == recommendedWaterMm
          ? _value.recommendedWaterMm
          : recommendedWaterMm // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$WaterBalanceImpl implements _WaterBalance {
  const _$WaterBalanceImpl(
      {required this.soilMoisturePercent,
      required this.fieldCapacity,
      required this.wiltingPoint,
      required this.availableWater,
      required this.depletionPercent,
      required this.status,
      required this.statusAr,
      required this.irrigationNeeded,
      this.recommendedWaterMm = 0});

  factory _$WaterBalanceImpl.fromJson(Map<String, dynamic> json) =>
      _$$WaterBalanceImplFromJson(json);

  @override
  final double soilMoisturePercent;
  @override
  final double fieldCapacity;
  @override
  final double wiltingPoint;
  @override
  final double availableWater;
  @override
  final double depletionPercent;
  @override
  final String status;
// optimal, low, critical, excess
  @override
  final String statusAr;
  @override
  final bool irrigationNeeded;
  @override
  @JsonKey()
  final double recommendedWaterMm;

  @override
  String toString() {
    return 'WaterBalance(soilMoisturePercent: $soilMoisturePercent, fieldCapacity: $fieldCapacity, wiltingPoint: $wiltingPoint, availableWater: $availableWater, depletionPercent: $depletionPercent, status: $status, statusAr: $statusAr, irrigationNeeded: $irrigationNeeded, recommendedWaterMm: $recommendedWaterMm)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WaterBalanceImpl &&
            (identical(other.soilMoisturePercent, soilMoisturePercent) ||
                other.soilMoisturePercent == soilMoisturePercent) &&
            (identical(other.fieldCapacity, fieldCapacity) ||
                other.fieldCapacity == fieldCapacity) &&
            (identical(other.wiltingPoint, wiltingPoint) ||
                other.wiltingPoint == wiltingPoint) &&
            (identical(other.availableWater, availableWater) ||
                other.availableWater == availableWater) &&
            (identical(other.depletionPercent, depletionPercent) ||
                other.depletionPercent == depletionPercent) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.statusAr, statusAr) ||
                other.statusAr == statusAr) &&
            (identical(other.irrigationNeeded, irrigationNeeded) ||
                other.irrigationNeeded == irrigationNeeded) &&
            (identical(other.recommendedWaterMm, recommendedWaterMm) ||
                other.recommendedWaterMm == recommendedWaterMm));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      soilMoisturePercent,
      fieldCapacity,
      wiltingPoint,
      availableWater,
      depletionPercent,
      status,
      statusAr,
      irrigationNeeded,
      recommendedWaterMm);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$WaterBalanceImplCopyWith<_$WaterBalanceImpl> get copyWith =>
      __$$WaterBalanceImplCopyWithImpl<_$WaterBalanceImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$WaterBalanceImplToJson(
      this,
    );
  }
}

abstract class _WaterBalance implements WaterBalance {
  const factory _WaterBalance(
      {required final double soilMoisturePercent,
      required final double fieldCapacity,
      required final double wiltingPoint,
      required final double availableWater,
      required final double depletionPercent,
      required final String status,
      required final String statusAr,
      required final bool irrigationNeeded,
      final double recommendedWaterMm}) = _$WaterBalanceImpl;

  factory _WaterBalance.fromJson(Map<String, dynamic> json) =
      _$WaterBalanceImpl.fromJson;

  @override
  double get soilMoisturePercent;
  @override
  double get fieldCapacity;
  @override
  double get wiltingPoint;
  @override
  double get availableWater;
  @override
  double get depletionPercent;
  @override
  String get status;
  @override // optimal, low, critical, excess
  String get statusAr;
  @override
  bool get irrigationNeeded;
  @override
  double get recommendedWaterMm;
  @override
  @JsonKey(ignore: true)
  _$$WaterBalanceImplCopyWith<_$WaterBalanceImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

SensorReading _$SensorReadingFromJson(Map<String, dynamic> json) {
  return _SensorReading.fromJson(json);
}

/// @nodoc
mixin _$SensorReading {
  String get sensorId => throw _privateConstructorUsedError;
  String get sensorType =>
      throw _privateConstructorUsedError; // soil_moisture, temperature, humidity
  double get value => throw _privateConstructorUsedError;
  String get unit => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  String get fieldId => throw _privateConstructorUsedError;
  String get location => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $SensorReadingCopyWith<SensorReading> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SensorReadingCopyWith<$Res> {
  factory $SensorReadingCopyWith(
          SensorReading value, $Res Function(SensorReading) then) =
      _$SensorReadingCopyWithImpl<$Res, SensorReading>;
  @useResult
  $Res call(
      {String sensorId,
      String sensorType,
      double value,
      String unit,
      DateTime timestamp,
      String fieldId,
      String location});
}

/// @nodoc
class _$SensorReadingCopyWithImpl<$Res, $Val extends SensorReading>
    implements $SensorReadingCopyWith<$Res> {
  _$SensorReadingCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? sensorId = null,
    Object? sensorType = null,
    Object? value = null,
    Object? unit = null,
    Object? timestamp = null,
    Object? fieldId = null,
    Object? location = null,
  }) {
    return _then(_value.copyWith(
      sensorId: null == sensorId
          ? _value.sensorId
          : sensorId // ignore: cast_nullable_to_non_nullable
              as String,
      sensorType: null == sensorType
          ? _value.sensorType
          : sensorType // ignore: cast_nullable_to_non_nullable
              as String,
      value: null == value
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _value.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      location: null == location
          ? _value.location
          : location // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SensorReadingImplCopyWith<$Res>
    implements $SensorReadingCopyWith<$Res> {
  factory _$$SensorReadingImplCopyWith(
          _$SensorReadingImpl value, $Res Function(_$SensorReadingImpl) then) =
      __$$SensorReadingImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String sensorId,
      String sensorType,
      double value,
      String unit,
      DateTime timestamp,
      String fieldId,
      String location});
}

/// @nodoc
class __$$SensorReadingImplCopyWithImpl<$Res>
    extends _$SensorReadingCopyWithImpl<$Res, _$SensorReadingImpl>
    implements _$$SensorReadingImplCopyWith<$Res> {
  __$$SensorReadingImplCopyWithImpl(
      _$SensorReadingImpl _value, $Res Function(_$SensorReadingImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? sensorId = null,
    Object? sensorType = null,
    Object? value = null,
    Object? unit = null,
    Object? timestamp = null,
    Object? fieldId = null,
    Object? location = null,
  }) {
    return _then(_$SensorReadingImpl(
      sensorId: null == sensorId
          ? _value.sensorId
          : sensorId // ignore: cast_nullable_to_non_nullable
              as String,
      sensorType: null == sensorType
          ? _value.sensorType
          : sensorType // ignore: cast_nullable_to_non_nullable
              as String,
      value: null == value
          ? _value.value
          : value // ignore: cast_nullable_to_non_nullable
              as double,
      unit: null == unit
          ? _value.unit
          : unit // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      location: null == location
          ? _value.location
          : location // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SensorReadingImpl implements _SensorReading {
  const _$SensorReadingImpl(
      {required this.sensorId,
      required this.sensorType,
      required this.value,
      required this.unit,
      required this.timestamp,
      required this.fieldId,
      this.location = ''});

  factory _$SensorReadingImpl.fromJson(Map<String, dynamic> json) =>
      _$$SensorReadingImplFromJson(json);

  @override
  final String sensorId;
  @override
  final String sensorType;
// soil_moisture, temperature, humidity
  @override
  final double value;
  @override
  final String unit;
  @override
  final DateTime timestamp;
  @override
  final String fieldId;
  @override
  @JsonKey()
  final String location;

  @override
  String toString() {
    return 'SensorReading(sensorId: $sensorId, sensorType: $sensorType, value: $value, unit: $unit, timestamp: $timestamp, fieldId: $fieldId, location: $location)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SensorReadingImpl &&
            (identical(other.sensorId, sensorId) ||
                other.sensorId == sensorId) &&
            (identical(other.sensorType, sensorType) ||
                other.sensorType == sensorType) &&
            (identical(other.value, value) || other.value == value) &&
            (identical(other.unit, unit) || other.unit == unit) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.fieldId, fieldId) || other.fieldId == fieldId) &&
            (identical(other.location, location) ||
                other.location == location));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(runtimeType, sensorId, sensorType, value,
      unit, timestamp, fieldId, location);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$SensorReadingImplCopyWith<_$SensorReadingImpl> get copyWith =>
      __$$SensorReadingImplCopyWithImpl<_$SensorReadingImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SensorReadingImplToJson(
      this,
    );
  }
}

abstract class _SensorReading implements SensorReading {
  const factory _SensorReading(
      {required final String sensorId,
      required final String sensorType,
      required final double value,
      required final String unit,
      required final DateTime timestamp,
      required final String fieldId,
      final String location}) = _$SensorReadingImpl;

  factory _SensorReading.fromJson(Map<String, dynamic> json) =
      _$SensorReadingImpl.fromJson;

  @override
  String get sensorId;
  @override
  String get sensorType;
  @override // soil_moisture, temperature, humidity
  double get value;
  @override
  String get unit;
  @override
  DateTime get timestamp;
  @override
  String get fieldId;
  @override
  String get location;
  @override
  @JsonKey(ignore: true)
  _$$SensorReadingImplCopyWith<_$SensorReadingImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

IrrigationEfficiencyReport _$IrrigationEfficiencyReportFromJson(
    Map<String, dynamic> json) {
  return _IrrigationEfficiencyReport.fromJson(json);
}

/// @nodoc
mixin _$IrrigationEfficiencyReport {
  String get reportId => throw _privateConstructorUsedError;
  String get fieldId => throw _privateConstructorUsedError;
  String get period =>
      throw _privateConstructorUsedError; // weekly, monthly, seasonal
  double get waterUsedLiters => throw _privateConstructorUsedError;
  double get waterSavedLiters => throw _privateConstructorUsedError;
  double get efficiencyPercent => throw _privateConstructorUsedError;
  double get costSaved => throw _privateConstructorUsedError; // currency
  Map<String, double> get dailyUsage =>
      throw _privateConstructorUsedError; // date -> liters
  List<String> get recommendations => throw _privateConstructorUsedError;
  List<String> get recommendationsAr => throw _privateConstructorUsedError;
  DateTime get generatedAt => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $IrrigationEfficiencyReportCopyWith<IrrigationEfficiencyReport>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IrrigationEfficiencyReportCopyWith<$Res> {
  factory $IrrigationEfficiencyReportCopyWith(IrrigationEfficiencyReport value,
          $Res Function(IrrigationEfficiencyReport) then) =
      _$IrrigationEfficiencyReportCopyWithImpl<$Res,
          IrrigationEfficiencyReport>;
  @useResult
  $Res call(
      {String reportId,
      String fieldId,
      String period,
      double waterUsedLiters,
      double waterSavedLiters,
      double efficiencyPercent,
      double costSaved,
      Map<String, double> dailyUsage,
      List<String> recommendations,
      List<String> recommendationsAr,
      DateTime generatedAt});
}

/// @nodoc
class _$IrrigationEfficiencyReportCopyWithImpl<$Res,
        $Val extends IrrigationEfficiencyReport>
    implements $IrrigationEfficiencyReportCopyWith<$Res> {
  _$IrrigationEfficiencyReportCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? reportId = null,
    Object? fieldId = null,
    Object? period = null,
    Object? waterUsedLiters = null,
    Object? waterSavedLiters = null,
    Object? efficiencyPercent = null,
    Object? costSaved = null,
    Object? dailyUsage = null,
    Object? recommendations = null,
    Object? recommendationsAr = null,
    Object? generatedAt = null,
  }) {
    return _then(_value.copyWith(
      reportId: null == reportId
          ? _value.reportId
          : reportId // ignore: cast_nullable_to_non_nullable
              as String,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      period: null == period
          ? _value.period
          : period // ignore: cast_nullable_to_non_nullable
              as String,
      waterUsedLiters: null == waterUsedLiters
          ? _value.waterUsedLiters
          : waterUsedLiters // ignore: cast_nullable_to_non_nullable
              as double,
      waterSavedLiters: null == waterSavedLiters
          ? _value.waterSavedLiters
          : waterSavedLiters // ignore: cast_nullable_to_non_nullable
              as double,
      efficiencyPercent: null == efficiencyPercent
          ? _value.efficiencyPercent
          : efficiencyPercent // ignore: cast_nullable_to_non_nullable
              as double,
      costSaved: null == costSaved
          ? _value.costSaved
          : costSaved // ignore: cast_nullable_to_non_nullable
              as double,
      dailyUsage: null == dailyUsage
          ? _value.dailyUsage
          : dailyUsage // ignore: cast_nullable_to_non_nullable
              as Map<String, double>,
      recommendations: null == recommendations
          ? _value.recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as List<String>,
      recommendationsAr: null == recommendationsAr
          ? _value.recommendationsAr
          : recommendationsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      generatedAt: null == generatedAt
          ? _value.generatedAt
          : generatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IrrigationEfficiencyReportImplCopyWith<$Res>
    implements $IrrigationEfficiencyReportCopyWith<$Res> {
  factory _$$IrrigationEfficiencyReportImplCopyWith(
          _$IrrigationEfficiencyReportImpl value,
          $Res Function(_$IrrigationEfficiencyReportImpl) then) =
      __$$IrrigationEfficiencyReportImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String reportId,
      String fieldId,
      String period,
      double waterUsedLiters,
      double waterSavedLiters,
      double efficiencyPercent,
      double costSaved,
      Map<String, double> dailyUsage,
      List<String> recommendations,
      List<String> recommendationsAr,
      DateTime generatedAt});
}

/// @nodoc
class __$$IrrigationEfficiencyReportImplCopyWithImpl<$Res>
    extends _$IrrigationEfficiencyReportCopyWithImpl<$Res,
        _$IrrigationEfficiencyReportImpl>
    implements _$$IrrigationEfficiencyReportImplCopyWith<$Res> {
  __$$IrrigationEfficiencyReportImplCopyWithImpl(
      _$IrrigationEfficiencyReportImpl _value,
      $Res Function(_$IrrigationEfficiencyReportImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? reportId = null,
    Object? fieldId = null,
    Object? period = null,
    Object? waterUsedLiters = null,
    Object? waterSavedLiters = null,
    Object? efficiencyPercent = null,
    Object? costSaved = null,
    Object? dailyUsage = null,
    Object? recommendations = null,
    Object? recommendationsAr = null,
    Object? generatedAt = null,
  }) {
    return _then(_$IrrigationEfficiencyReportImpl(
      reportId: null == reportId
          ? _value.reportId
          : reportId // ignore: cast_nullable_to_non_nullable
              as String,
      fieldId: null == fieldId
          ? _value.fieldId
          : fieldId // ignore: cast_nullable_to_non_nullable
              as String,
      period: null == period
          ? _value.period
          : period // ignore: cast_nullable_to_non_nullable
              as String,
      waterUsedLiters: null == waterUsedLiters
          ? _value.waterUsedLiters
          : waterUsedLiters // ignore: cast_nullable_to_non_nullable
              as double,
      waterSavedLiters: null == waterSavedLiters
          ? _value.waterSavedLiters
          : waterSavedLiters // ignore: cast_nullable_to_non_nullable
              as double,
      efficiencyPercent: null == efficiencyPercent
          ? _value.efficiencyPercent
          : efficiencyPercent // ignore: cast_nullable_to_non_nullable
              as double,
      costSaved: null == costSaved
          ? _value.costSaved
          : costSaved // ignore: cast_nullable_to_non_nullable
              as double,
      dailyUsage: null == dailyUsage
          ? _value._dailyUsage
          : dailyUsage // ignore: cast_nullable_to_non_nullable
              as Map<String, double>,
      recommendations: null == recommendations
          ? _value._recommendations
          : recommendations // ignore: cast_nullable_to_non_nullable
              as List<String>,
      recommendationsAr: null == recommendationsAr
          ? _value._recommendationsAr
          : recommendationsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      generatedAt: null == generatedAt
          ? _value.generatedAt
          : generatedAt // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IrrigationEfficiencyReportImpl implements _IrrigationEfficiencyReport {
  const _$IrrigationEfficiencyReportImpl(
      {required this.reportId,
      required this.fieldId,
      required this.period,
      required this.waterUsedLiters,
      required this.waterSavedLiters,
      required this.efficiencyPercent,
      required this.costSaved,
      required final Map<String, double> dailyUsage,
      required final List<String> recommendations,
      required final List<String> recommendationsAr,
      required this.generatedAt})
      : _dailyUsage = dailyUsage,
        _recommendations = recommendations,
        _recommendationsAr = recommendationsAr;

  factory _$IrrigationEfficiencyReportImpl.fromJson(
          Map<String, dynamic> json) =>
      _$$IrrigationEfficiencyReportImplFromJson(json);

  @override
  final String reportId;
  @override
  final String fieldId;
  @override
  final String period;
// weekly, monthly, seasonal
  @override
  final double waterUsedLiters;
  @override
  final double waterSavedLiters;
  @override
  final double efficiencyPercent;
  @override
  final double costSaved;
// currency
  final Map<String, double> _dailyUsage;
// currency
  @override
  Map<String, double> get dailyUsage {
    if (_dailyUsage is EqualUnmodifiableMapView) return _dailyUsage;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_dailyUsage);
  }

// date -> liters
  final List<String> _recommendations;
// date -> liters
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
  final DateTime generatedAt;

  @override
  String toString() {
    return 'IrrigationEfficiencyReport(reportId: $reportId, fieldId: $fieldId, period: $period, waterUsedLiters: $waterUsedLiters, waterSavedLiters: $waterSavedLiters, efficiencyPercent: $efficiencyPercent, costSaved: $costSaved, dailyUsage: $dailyUsage, recommendations: $recommendations, recommendationsAr: $recommendationsAr, generatedAt: $generatedAt)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IrrigationEfficiencyReportImpl &&
            (identical(other.reportId, reportId) ||
                other.reportId == reportId) &&
            (identical(other.fieldId, fieldId) || other.fieldId == fieldId) &&
            (identical(other.period, period) || other.period == period) &&
            (identical(other.waterUsedLiters, waterUsedLiters) ||
                other.waterUsedLiters == waterUsedLiters) &&
            (identical(other.waterSavedLiters, waterSavedLiters) ||
                other.waterSavedLiters == waterSavedLiters) &&
            (identical(other.efficiencyPercent, efficiencyPercent) ||
                other.efficiencyPercent == efficiencyPercent) &&
            (identical(other.costSaved, costSaved) ||
                other.costSaved == costSaved) &&
            const DeepCollectionEquality()
                .equals(other._dailyUsage, _dailyUsage) &&
            const DeepCollectionEquality()
                .equals(other._recommendations, _recommendations) &&
            const DeepCollectionEquality()
                .equals(other._recommendationsAr, _recommendationsAr) &&
            (identical(other.generatedAt, generatedAt) ||
                other.generatedAt == generatedAt));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      reportId,
      fieldId,
      period,
      waterUsedLiters,
      waterSavedLiters,
      efficiencyPercent,
      costSaved,
      const DeepCollectionEquality().hash(_dailyUsage),
      const DeepCollectionEquality().hash(_recommendations),
      const DeepCollectionEquality().hash(_recommendationsAr),
      generatedAt);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$IrrigationEfficiencyReportImplCopyWith<_$IrrigationEfficiencyReportImpl>
      get copyWith => __$$IrrigationEfficiencyReportImplCopyWithImpl<
          _$IrrigationEfficiencyReportImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IrrigationEfficiencyReportImplToJson(
      this,
    );
  }
}

abstract class _IrrigationEfficiencyReport
    implements IrrigationEfficiencyReport {
  const factory _IrrigationEfficiencyReport(
      {required final String reportId,
      required final String fieldId,
      required final String period,
      required final double waterUsedLiters,
      required final double waterSavedLiters,
      required final double efficiencyPercent,
      required final double costSaved,
      required final Map<String, double> dailyUsage,
      required final List<String> recommendations,
      required final List<String> recommendationsAr,
      required final DateTime generatedAt}) = _$IrrigationEfficiencyReportImpl;

  factory _IrrigationEfficiencyReport.fromJson(Map<String, dynamic> json) =
      _$IrrigationEfficiencyReportImpl.fromJson;

  @override
  String get reportId;
  @override
  String get fieldId;
  @override
  String get period;
  @override // weekly, monthly, seasonal
  double get waterUsedLiters;
  @override
  double get waterSavedLiters;
  @override
  double get efficiencyPercent;
  @override
  double get costSaved;
  @override // currency
  Map<String, double> get dailyUsage;
  @override // date -> liters
  List<String> get recommendations;
  @override
  List<String> get recommendationsAr;
  @override
  DateTime get generatedAt;
  @override
  @JsonKey(ignore: true)
  _$$IrrigationEfficiencyReportImplCopyWith<_$IrrigationEfficiencyReportImpl>
      get copyWith => throw _privateConstructorUsedError;
}

IrrigationMethodOption _$IrrigationMethodOptionFromJson(
    Map<String, dynamic> json) {
  return _IrrigationMethodOption.fromJson(json);
}

/// @nodoc
mixin _$IrrigationMethodOption {
  String get id => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;
  double get efficiency =>
      throw _privateConstructorUsedError; // typical efficiency %
  String get description => throw _privateConstructorUsedError;
  String get descriptionAr => throw _privateConstructorUsedError;
  List<String> get suitableCrops => throw _privateConstructorUsedError;
  List<String> get suitableCropsAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $IrrigationMethodOptionCopyWith<IrrigationMethodOption> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IrrigationMethodOptionCopyWith<$Res> {
  factory $IrrigationMethodOptionCopyWith(IrrigationMethodOption value,
          $Res Function(IrrigationMethodOption) then) =
      _$IrrigationMethodOptionCopyWithImpl<$Res, IrrigationMethodOption>;
  @useResult
  $Res call(
      {String id,
      String name,
      String nameAr,
      double efficiency,
      String description,
      String descriptionAr,
      List<String> suitableCrops,
      List<String> suitableCropsAr});
}

/// @nodoc
class _$IrrigationMethodOptionCopyWithImpl<$Res,
        $Val extends IrrigationMethodOption>
    implements $IrrigationMethodOptionCopyWith<$Res> {
  _$IrrigationMethodOptionCopyWithImpl(this._value, this._then);

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
    Object? efficiency = null,
    Object? description = null,
    Object? descriptionAr = null,
    Object? suitableCrops = null,
    Object? suitableCropsAr = null,
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
      efficiency: null == efficiency
          ? _value.efficiency
          : efficiency // ignore: cast_nullable_to_non_nullable
              as double,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      descriptionAr: null == descriptionAr
          ? _value.descriptionAr
          : descriptionAr // ignore: cast_nullable_to_non_nullable
              as String,
      suitableCrops: null == suitableCrops
          ? _value.suitableCrops
          : suitableCrops // ignore: cast_nullable_to_non_nullable
              as List<String>,
      suitableCropsAr: null == suitableCropsAr
          ? _value.suitableCropsAr
          : suitableCropsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IrrigationMethodOptionImplCopyWith<$Res>
    implements $IrrigationMethodOptionCopyWith<$Res> {
  factory _$$IrrigationMethodOptionImplCopyWith(
          _$IrrigationMethodOptionImpl value,
          $Res Function(_$IrrigationMethodOptionImpl) then) =
      __$$IrrigationMethodOptionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String name,
      String nameAr,
      double efficiency,
      String description,
      String descriptionAr,
      List<String> suitableCrops,
      List<String> suitableCropsAr});
}

/// @nodoc
class __$$IrrigationMethodOptionImplCopyWithImpl<$Res>
    extends _$IrrigationMethodOptionCopyWithImpl<$Res,
        _$IrrigationMethodOptionImpl>
    implements _$$IrrigationMethodOptionImplCopyWith<$Res> {
  __$$IrrigationMethodOptionImplCopyWithImpl(
      _$IrrigationMethodOptionImpl _value,
      $Res Function(_$IrrigationMethodOptionImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? name = null,
    Object? nameAr = null,
    Object? efficiency = null,
    Object? description = null,
    Object? descriptionAr = null,
    Object? suitableCrops = null,
    Object? suitableCropsAr = null,
  }) {
    return _then(_$IrrigationMethodOptionImpl(
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
      efficiency: null == efficiency
          ? _value.efficiency
          : efficiency // ignore: cast_nullable_to_non_nullable
              as double,
      description: null == description
          ? _value.description
          : description // ignore: cast_nullable_to_non_nullable
              as String,
      descriptionAr: null == descriptionAr
          ? _value.descriptionAr
          : descriptionAr // ignore: cast_nullable_to_non_nullable
              as String,
      suitableCrops: null == suitableCrops
          ? _value._suitableCrops
          : suitableCrops // ignore: cast_nullable_to_non_nullable
              as List<String>,
      suitableCropsAr: null == suitableCropsAr
          ? _value._suitableCropsAr
          : suitableCropsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IrrigationMethodOptionImpl implements _IrrigationMethodOption {
  const _$IrrigationMethodOptionImpl(
      {required this.id,
      required this.name,
      required this.nameAr,
      required this.efficiency,
      required this.description,
      required this.descriptionAr,
      final List<String> suitableCrops = const [],
      final List<String> suitableCropsAr = const []})
      : _suitableCrops = suitableCrops,
        _suitableCropsAr = suitableCropsAr;

  factory _$IrrigationMethodOptionImpl.fromJson(Map<String, dynamic> json) =>
      _$$IrrigationMethodOptionImplFromJson(json);

  @override
  final String id;
  @override
  final String name;
  @override
  final String nameAr;
  @override
  final double efficiency;
// typical efficiency %
  @override
  final String description;
  @override
  final String descriptionAr;
  final List<String> _suitableCrops;
  @override
  @JsonKey()
  List<String> get suitableCrops {
    if (_suitableCrops is EqualUnmodifiableListView) return _suitableCrops;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_suitableCrops);
  }

  final List<String> _suitableCropsAr;
  @override
  @JsonKey()
  List<String> get suitableCropsAr {
    if (_suitableCropsAr is EqualUnmodifiableListView) return _suitableCropsAr;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_suitableCropsAr);
  }

  @override
  String toString() {
    return 'IrrigationMethodOption(id: $id, name: $name, nameAr: $nameAr, efficiency: $efficiency, description: $description, descriptionAr: $descriptionAr, suitableCrops: $suitableCrops, suitableCropsAr: $suitableCropsAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IrrigationMethodOptionImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.efficiency, efficiency) ||
                other.efficiency == efficiency) &&
            (identical(other.description, description) ||
                other.description == description) &&
            (identical(other.descriptionAr, descriptionAr) ||
                other.descriptionAr == descriptionAr) &&
            const DeepCollectionEquality()
                .equals(other._suitableCrops, _suitableCrops) &&
            const DeepCollectionEquality()
                .equals(other._suitableCropsAr, _suitableCropsAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      id,
      name,
      nameAr,
      efficiency,
      description,
      descriptionAr,
      const DeepCollectionEquality().hash(_suitableCrops),
      const DeepCollectionEquality().hash(_suitableCropsAr));

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$IrrigationMethodOptionImplCopyWith<_$IrrigationMethodOptionImpl>
      get copyWith => __$$IrrigationMethodOptionImplCopyWithImpl<
          _$IrrigationMethodOptionImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IrrigationMethodOptionImplToJson(
      this,
    );
  }
}

abstract class _IrrigationMethodOption implements IrrigationMethodOption {
  const factory _IrrigationMethodOption(
      {required final String id,
      required final String name,
      required final String nameAr,
      required final double efficiency,
      required final String description,
      required final String descriptionAr,
      final List<String> suitableCrops,
      final List<String> suitableCropsAr}) = _$IrrigationMethodOptionImpl;

  factory _IrrigationMethodOption.fromJson(Map<String, dynamic> json) =
      _$IrrigationMethodOptionImpl.fromJson;

  @override
  String get id;
  @override
  String get name;
  @override
  String get nameAr;
  @override
  double get efficiency;
  @override // typical efficiency %
  String get description;
  @override
  String get descriptionAr;
  @override
  List<String> get suitableCrops;
  @override
  List<String> get suitableCropsAr;
  @override
  @JsonKey(ignore: true)
  _$$IrrigationMethodOptionImplCopyWith<_$IrrigationMethodOptionImpl>
      get copyWith => throw _privateConstructorUsedError;
}

CropWaterRequirement _$CropWaterRequirementFromJson(Map<String, dynamic> json) {
  return _CropWaterRequirement.fromJson(json);
}

/// @nodoc
mixin _$CropWaterRequirement {
  String get cropId => throw _privateConstructorUsedError;
  String get cropName => throw _privateConstructorUsedError;
  String get cropNameAr => throw _privateConstructorUsedError;
  Map<String, double> get stageRequirements =>
      throw _privateConstructorUsedError; // growth_stage -> mm/day
  double get kcInitial => throw _privateConstructorUsedError;
  double get kcMid => throw _privateConstructorUsedError;
  double get kcEnd => throw _privateConstructorUsedError;
  int get rootDepthCm => throw _privateConstructorUsedError;
  double get criticalDepletionFraction => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $CropWaterRequirementCopyWith<CropWaterRequirement> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CropWaterRequirementCopyWith<$Res> {
  factory $CropWaterRequirementCopyWith(CropWaterRequirement value,
          $Res Function(CropWaterRequirement) then) =
      _$CropWaterRequirementCopyWithImpl<$Res, CropWaterRequirement>;
  @useResult
  $Res call(
      {String cropId,
      String cropName,
      String cropNameAr,
      Map<String, double> stageRequirements,
      double kcInitial,
      double kcMid,
      double kcEnd,
      int rootDepthCm,
      double criticalDepletionFraction});
}

/// @nodoc
class _$CropWaterRequirementCopyWithImpl<$Res,
        $Val extends CropWaterRequirement>
    implements $CropWaterRequirementCopyWith<$Res> {
  _$CropWaterRequirementCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropId = null,
    Object? cropName = null,
    Object? cropNameAr = null,
    Object? stageRequirements = null,
    Object? kcInitial = null,
    Object? kcMid = null,
    Object? kcEnd = null,
    Object? rootDepthCm = null,
    Object? criticalDepletionFraction = null,
  }) {
    return _then(_value.copyWith(
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      cropName: null == cropName
          ? _value.cropName
          : cropName // ignore: cast_nullable_to_non_nullable
              as String,
      cropNameAr: null == cropNameAr
          ? _value.cropNameAr
          : cropNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      stageRequirements: null == stageRequirements
          ? _value.stageRequirements
          : stageRequirements // ignore: cast_nullable_to_non_nullable
              as Map<String, double>,
      kcInitial: null == kcInitial
          ? _value.kcInitial
          : kcInitial // ignore: cast_nullable_to_non_nullable
              as double,
      kcMid: null == kcMid
          ? _value.kcMid
          : kcMid // ignore: cast_nullable_to_non_nullable
              as double,
      kcEnd: null == kcEnd
          ? _value.kcEnd
          : kcEnd // ignore: cast_nullable_to_non_nullable
              as double,
      rootDepthCm: null == rootDepthCm
          ? _value.rootDepthCm
          : rootDepthCm // ignore: cast_nullable_to_non_nullable
              as int,
      criticalDepletionFraction: null == criticalDepletionFraction
          ? _value.criticalDepletionFraction
          : criticalDepletionFraction // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CropWaterRequirementImplCopyWith<$Res>
    implements $CropWaterRequirementCopyWith<$Res> {
  factory _$$CropWaterRequirementImplCopyWith(_$CropWaterRequirementImpl value,
          $Res Function(_$CropWaterRequirementImpl) then) =
      __$$CropWaterRequirementImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String cropId,
      String cropName,
      String cropNameAr,
      Map<String, double> stageRequirements,
      double kcInitial,
      double kcMid,
      double kcEnd,
      int rootDepthCm,
      double criticalDepletionFraction});
}

/// @nodoc
class __$$CropWaterRequirementImplCopyWithImpl<$Res>
    extends _$CropWaterRequirementCopyWithImpl<$Res, _$CropWaterRequirementImpl>
    implements _$$CropWaterRequirementImplCopyWith<$Res> {
  __$$CropWaterRequirementImplCopyWithImpl(_$CropWaterRequirementImpl _value,
      $Res Function(_$CropWaterRequirementImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropId = null,
    Object? cropName = null,
    Object? cropNameAr = null,
    Object? stageRequirements = null,
    Object? kcInitial = null,
    Object? kcMid = null,
    Object? kcEnd = null,
    Object? rootDepthCm = null,
    Object? criticalDepletionFraction = null,
  }) {
    return _then(_$CropWaterRequirementImpl(
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      cropName: null == cropName
          ? _value.cropName
          : cropName // ignore: cast_nullable_to_non_nullable
              as String,
      cropNameAr: null == cropNameAr
          ? _value.cropNameAr
          : cropNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      stageRequirements: null == stageRequirements
          ? _value._stageRequirements
          : stageRequirements // ignore: cast_nullable_to_non_nullable
              as Map<String, double>,
      kcInitial: null == kcInitial
          ? _value.kcInitial
          : kcInitial // ignore: cast_nullable_to_non_nullable
              as double,
      kcMid: null == kcMid
          ? _value.kcMid
          : kcMid // ignore: cast_nullable_to_non_nullable
              as double,
      kcEnd: null == kcEnd
          ? _value.kcEnd
          : kcEnd // ignore: cast_nullable_to_non_nullable
              as double,
      rootDepthCm: null == rootDepthCm
          ? _value.rootDepthCm
          : rootDepthCm // ignore: cast_nullable_to_non_nullable
              as int,
      criticalDepletionFraction: null == criticalDepletionFraction
          ? _value.criticalDepletionFraction
          : criticalDepletionFraction // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CropWaterRequirementImpl implements _CropWaterRequirement {
  const _$CropWaterRequirementImpl(
      {required this.cropId,
      required this.cropName,
      required this.cropNameAr,
      required final Map<String, double> stageRequirements,
      required this.kcInitial,
      required this.kcMid,
      required this.kcEnd,
      required this.rootDepthCm,
      required this.criticalDepletionFraction})
      : _stageRequirements = stageRequirements;

  factory _$CropWaterRequirementImpl.fromJson(Map<String, dynamic> json) =>
      _$$CropWaterRequirementImplFromJson(json);

  @override
  final String cropId;
  @override
  final String cropName;
  @override
  final String cropNameAr;
  final Map<String, double> _stageRequirements;
  @override
  Map<String, double> get stageRequirements {
    if (_stageRequirements is EqualUnmodifiableMapView)
      return _stageRequirements;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_stageRequirements);
  }

// growth_stage -> mm/day
  @override
  final double kcInitial;
  @override
  final double kcMid;
  @override
  final double kcEnd;
  @override
  final int rootDepthCm;
  @override
  final double criticalDepletionFraction;

  @override
  String toString() {
    return 'CropWaterRequirement(cropId: $cropId, cropName: $cropName, cropNameAr: $cropNameAr, stageRequirements: $stageRequirements, kcInitial: $kcInitial, kcMid: $kcMid, kcEnd: $kcEnd, rootDepthCm: $rootDepthCm, criticalDepletionFraction: $criticalDepletionFraction)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CropWaterRequirementImpl &&
            (identical(other.cropId, cropId) || other.cropId == cropId) &&
            (identical(other.cropName, cropName) ||
                other.cropName == cropName) &&
            (identical(other.cropNameAr, cropNameAr) ||
                other.cropNameAr == cropNameAr) &&
            const DeepCollectionEquality()
                .equals(other._stageRequirements, _stageRequirements) &&
            (identical(other.kcInitial, kcInitial) ||
                other.kcInitial == kcInitial) &&
            (identical(other.kcMid, kcMid) || other.kcMid == kcMid) &&
            (identical(other.kcEnd, kcEnd) || other.kcEnd == kcEnd) &&
            (identical(other.rootDepthCm, rootDepthCm) ||
                other.rootDepthCm == rootDepthCm) &&
            (identical(other.criticalDepletionFraction,
                    criticalDepletionFraction) ||
                other.criticalDepletionFraction == criticalDepletionFraction));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      cropId,
      cropName,
      cropNameAr,
      const DeepCollectionEquality().hash(_stageRequirements),
      kcInitial,
      kcMid,
      kcEnd,
      rootDepthCm,
      criticalDepletionFraction);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$CropWaterRequirementImplCopyWith<_$CropWaterRequirementImpl>
      get copyWith =>
          __$$CropWaterRequirementImplCopyWithImpl<_$CropWaterRequirementImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CropWaterRequirementImplToJson(
      this,
    );
  }
}

abstract class _CropWaterRequirement implements CropWaterRequirement {
  const factory _CropWaterRequirement(
          {required final String cropId,
          required final String cropName,
          required final String cropNameAr,
          required final Map<String, double> stageRequirements,
          required final double kcInitial,
          required final double kcMid,
          required final double kcEnd,
          required final int rootDepthCm,
          required final double criticalDepletionFraction}) =
      _$CropWaterRequirementImpl;

  factory _CropWaterRequirement.fromJson(Map<String, dynamic> json) =
      _$CropWaterRequirementImpl.fromJson;

  @override
  String get cropId;
  @override
  String get cropName;
  @override
  String get cropNameAr;
  @override
  Map<String, double> get stageRequirements;
  @override // growth_stage -> mm/day
  double get kcInitial;
  @override
  double get kcMid;
  @override
  double get kcEnd;
  @override
  int get rootDepthCm;
  @override
  double get criticalDepletionFraction;
  @override
  @JsonKey(ignore: true)
  _$$CropWaterRequirementImplCopyWith<_$CropWaterRequirementImpl>
      get copyWith => throw _privateConstructorUsedError;
}
