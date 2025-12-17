// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'virtual_sensor_models.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

WeatherInput _$WeatherInputFromJson(Map<String, dynamic> json) {
  return _WeatherInput.fromJson(json);
}

/// @nodoc
mixin _$WeatherInput {
  double get temperatureMax => throw _privateConstructorUsedError;
  double get temperatureMin => throw _privateConstructorUsedError;
  double get humidity => throw _privateConstructorUsedError;
  double get windSpeed => throw _privateConstructorUsedError;
  double? get solarRadiation => throw _privateConstructorUsedError;
  double? get sunshineHours => throw _privateConstructorUsedError;
  double get latitude => throw _privateConstructorUsedError;
  double get altitude => throw _privateConstructorUsedError;
  DateTime? get date => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $WeatherInputCopyWith<WeatherInput> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $WeatherInputCopyWith<$Res> {
  factory $WeatherInputCopyWith(
          WeatherInput value, $Res Function(WeatherInput) then) =
      _$WeatherInputCopyWithImpl<$Res, WeatherInput>;
  @useResult
  $Res call(
      {double temperatureMax,
      double temperatureMin,
      double humidity,
      double windSpeed,
      double? solarRadiation,
      double? sunshineHours,
      double latitude,
      double altitude,
      DateTime? date});
}

/// @nodoc
class _$WeatherInputCopyWithImpl<$Res, $Val extends WeatherInput>
    implements $WeatherInputCopyWith<$Res> {
  _$WeatherInputCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? temperatureMax = null,
    Object? temperatureMin = null,
    Object? humidity = null,
    Object? windSpeed = null,
    Object? solarRadiation = freezed,
    Object? sunshineHours = freezed,
    Object? latitude = null,
    Object? altitude = null,
    Object? date = freezed,
  }) {
    return _then(_value.copyWith(
      temperatureMax: null == temperatureMax
          ? _value.temperatureMax
          : temperatureMax // ignore: cast_nullable_to_non_nullable
              as double,
      temperatureMin: null == temperatureMin
          ? _value.temperatureMin
          : temperatureMin // ignore: cast_nullable_to_non_nullable
              as double,
      humidity: null == humidity
          ? _value.humidity
          : humidity // ignore: cast_nullable_to_non_nullable
              as double,
      windSpeed: null == windSpeed
          ? _value.windSpeed
          : windSpeed // ignore: cast_nullable_to_non_nullable
              as double,
      solarRadiation: freezed == solarRadiation
          ? _value.solarRadiation
          : solarRadiation // ignore: cast_nullable_to_non_nullable
              as double?,
      sunshineHours: freezed == sunshineHours
          ? _value.sunshineHours
          : sunshineHours // ignore: cast_nullable_to_non_nullable
              as double?,
      latitude: null == latitude
          ? _value.latitude
          : latitude // ignore: cast_nullable_to_non_nullable
              as double,
      altitude: null == altitude
          ? _value.altitude
          : altitude // ignore: cast_nullable_to_non_nullable
              as double,
      date: freezed == date
          ? _value.date
          : date // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$WeatherInputImplCopyWith<$Res>
    implements $WeatherInputCopyWith<$Res> {
  factory _$$WeatherInputImplCopyWith(
          _$WeatherInputImpl value, $Res Function(_$WeatherInputImpl) then) =
      __$$WeatherInputImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {double temperatureMax,
      double temperatureMin,
      double humidity,
      double windSpeed,
      double? solarRadiation,
      double? sunshineHours,
      double latitude,
      double altitude,
      DateTime? date});
}

/// @nodoc
class __$$WeatherInputImplCopyWithImpl<$Res>
    extends _$WeatherInputCopyWithImpl<$Res, _$WeatherInputImpl>
    implements _$$WeatherInputImplCopyWith<$Res> {
  __$$WeatherInputImplCopyWithImpl(
      _$WeatherInputImpl _value, $Res Function(_$WeatherInputImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? temperatureMax = null,
    Object? temperatureMin = null,
    Object? humidity = null,
    Object? windSpeed = null,
    Object? solarRadiation = freezed,
    Object? sunshineHours = freezed,
    Object? latitude = null,
    Object? altitude = null,
    Object? date = freezed,
  }) {
    return _then(_$WeatherInputImpl(
      temperatureMax: null == temperatureMax
          ? _value.temperatureMax
          : temperatureMax // ignore: cast_nullable_to_non_nullable
              as double,
      temperatureMin: null == temperatureMin
          ? _value.temperatureMin
          : temperatureMin // ignore: cast_nullable_to_non_nullable
              as double,
      humidity: null == humidity
          ? _value.humidity
          : humidity // ignore: cast_nullable_to_non_nullable
              as double,
      windSpeed: null == windSpeed
          ? _value.windSpeed
          : windSpeed // ignore: cast_nullable_to_non_nullable
              as double,
      solarRadiation: freezed == solarRadiation
          ? _value.solarRadiation
          : solarRadiation // ignore: cast_nullable_to_non_nullable
              as double?,
      sunshineHours: freezed == sunshineHours
          ? _value.sunshineHours
          : sunshineHours // ignore: cast_nullable_to_non_nullable
              as double?,
      latitude: null == latitude
          ? _value.latitude
          : latitude // ignore: cast_nullable_to_non_nullable
              as double,
      altitude: null == altitude
          ? _value.altitude
          : altitude // ignore: cast_nullable_to_non_nullable
              as double,
      date: freezed == date
          ? _value.date
          : date // ignore: cast_nullable_to_non_nullable
              as DateTime?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$WeatherInputImpl implements _WeatherInput {
  const _$WeatherInputImpl(
      {required this.temperatureMax,
      required this.temperatureMin,
      required this.humidity,
      required this.windSpeed,
      this.solarRadiation,
      this.sunshineHours,
      required this.latitude,
      this.altitude = 0,
      this.date});

  factory _$WeatherInputImpl.fromJson(Map<String, dynamic> json) =>
      _$$WeatherInputImplFromJson(json);

  @override
  final double temperatureMax;
  @override
  final double temperatureMin;
  @override
  final double humidity;
  @override
  final double windSpeed;
  @override
  final double? solarRadiation;
  @override
  final double? sunshineHours;
  @override
  final double latitude;
  @override
  @JsonKey()
  final double altitude;
  @override
  final DateTime? date;

  @override
  String toString() {
    return 'WeatherInput(temperatureMax: $temperatureMax, temperatureMin: $temperatureMin, humidity: $humidity, windSpeed: $windSpeed, solarRadiation: $solarRadiation, sunshineHours: $sunshineHours, latitude: $latitude, altitude: $altitude, date: $date)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$WeatherInputImpl &&
            (identical(other.temperatureMax, temperatureMax) ||
                other.temperatureMax == temperatureMax) &&
            (identical(other.temperatureMin, temperatureMin) ||
                other.temperatureMin == temperatureMin) &&
            (identical(other.humidity, humidity) ||
                other.humidity == humidity) &&
            (identical(other.windSpeed, windSpeed) ||
                other.windSpeed == windSpeed) &&
            (identical(other.solarRadiation, solarRadiation) ||
                other.solarRadiation == solarRadiation) &&
            (identical(other.sunshineHours, sunshineHours) ||
                other.sunshineHours == sunshineHours) &&
            (identical(other.latitude, latitude) ||
                other.latitude == latitude) &&
            (identical(other.altitude, altitude) ||
                other.altitude == altitude) &&
            (identical(other.date, date) || other.date == date));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      temperatureMax,
      temperatureMin,
      humidity,
      windSpeed,
      solarRadiation,
      sunshineHours,
      latitude,
      altitude,
      date);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$WeatherInputImplCopyWith<_$WeatherInputImpl> get copyWith =>
      __$$WeatherInputImplCopyWithImpl<_$WeatherInputImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$WeatherInputImplToJson(
      this,
    );
  }
}

abstract class _WeatherInput implements WeatherInput {
  const factory _WeatherInput(
      {required final double temperatureMax,
      required final double temperatureMin,
      required final double humidity,
      required final double windSpeed,
      final double? solarRadiation,
      final double? sunshineHours,
      required final double latitude,
      final double altitude,
      final DateTime? date}) = _$WeatherInputImpl;

  factory _WeatherInput.fromJson(Map<String, dynamic> json) =
      _$WeatherInputImpl.fromJson;

  @override
  double get temperatureMax;
  @override
  double get temperatureMin;
  @override
  double get humidity;
  @override
  double get windSpeed;
  @override
  double? get solarRadiation;
  @override
  double? get sunshineHours;
  @override
  double get latitude;
  @override
  double get altitude;
  @override
  DateTime? get date;
  @override
  @JsonKey(ignore: true)
  _$$WeatherInputImplCopyWith<_$WeatherInputImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

ET0Response _$ET0ResponseFromJson(Map<String, dynamic> json) {
  return _ET0Response.fromJson(json);
}

/// @nodoc
mixin _$ET0Response {
  double get et0 => throw _privateConstructorUsedError;
  String get et0Ar => throw _privateConstructorUsedError;
  String get method => throw _privateConstructorUsedError;
  Map<String, dynamic> get weatherSummary => throw _privateConstructorUsedError;
  DateTime get calculationDate => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $ET0ResponseCopyWith<ET0Response> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $ET0ResponseCopyWith<$Res> {
  factory $ET0ResponseCopyWith(
          ET0Response value, $Res Function(ET0Response) then) =
      _$ET0ResponseCopyWithImpl<$Res, ET0Response>;
  @useResult
  $Res call(
      {double et0,
      String et0Ar,
      String method,
      Map<String, dynamic> weatherSummary,
      DateTime calculationDate});
}

/// @nodoc
class _$ET0ResponseCopyWithImpl<$Res, $Val extends ET0Response>
    implements $ET0ResponseCopyWith<$Res> {
  _$ET0ResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? et0 = null,
    Object? et0Ar = null,
    Object? method = null,
    Object? weatherSummary = null,
    Object? calculationDate = null,
  }) {
    return _then(_value.copyWith(
      et0: null == et0
          ? _value.et0
          : et0 // ignore: cast_nullable_to_non_nullable
              as double,
      et0Ar: null == et0Ar
          ? _value.et0Ar
          : et0Ar // ignore: cast_nullable_to_non_nullable
              as String,
      method: null == method
          ? _value.method
          : method // ignore: cast_nullable_to_non_nullable
              as String,
      weatherSummary: null == weatherSummary
          ? _value.weatherSummary
          : weatherSummary // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      calculationDate: null == calculationDate
          ? _value.calculationDate
          : calculationDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$ET0ResponseImplCopyWith<$Res>
    implements $ET0ResponseCopyWith<$Res> {
  factory _$$ET0ResponseImplCopyWith(
          _$ET0ResponseImpl value, $Res Function(_$ET0ResponseImpl) then) =
      __$$ET0ResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {double et0,
      String et0Ar,
      String method,
      Map<String, dynamic> weatherSummary,
      DateTime calculationDate});
}

/// @nodoc
class __$$ET0ResponseImplCopyWithImpl<$Res>
    extends _$ET0ResponseCopyWithImpl<$Res, _$ET0ResponseImpl>
    implements _$$ET0ResponseImplCopyWith<$Res> {
  __$$ET0ResponseImplCopyWithImpl(
      _$ET0ResponseImpl _value, $Res Function(_$ET0ResponseImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? et0 = null,
    Object? et0Ar = null,
    Object? method = null,
    Object? weatherSummary = null,
    Object? calculationDate = null,
  }) {
    return _then(_$ET0ResponseImpl(
      et0: null == et0
          ? _value.et0
          : et0 // ignore: cast_nullable_to_non_nullable
              as double,
      et0Ar: null == et0Ar
          ? _value.et0Ar
          : et0Ar // ignore: cast_nullable_to_non_nullable
              as String,
      method: null == method
          ? _value.method
          : method // ignore: cast_nullable_to_non_nullable
              as String,
      weatherSummary: null == weatherSummary
          ? _value._weatherSummary
          : weatherSummary // ignore: cast_nullable_to_non_nullable
              as Map<String, dynamic>,
      calculationDate: null == calculationDate
          ? _value.calculationDate
          : calculationDate // ignore: cast_nullable_to_non_nullable
              as DateTime,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$ET0ResponseImpl implements _ET0Response {
  const _$ET0ResponseImpl(
      {required this.et0,
      required this.et0Ar,
      required this.method,
      required final Map<String, dynamic> weatherSummary,
      required this.calculationDate})
      : _weatherSummary = weatherSummary;

  factory _$ET0ResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$ET0ResponseImplFromJson(json);

  @override
  final double et0;
  @override
  final String et0Ar;
  @override
  final String method;
  final Map<String, dynamic> _weatherSummary;
  @override
  Map<String, dynamic> get weatherSummary {
    if (_weatherSummary is EqualUnmodifiableMapView) return _weatherSummary;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableMapView(_weatherSummary);
  }

  @override
  final DateTime calculationDate;

  @override
  String toString() {
    return 'ET0Response(et0: $et0, et0Ar: $et0Ar, method: $method, weatherSummary: $weatherSummary, calculationDate: $calculationDate)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$ET0ResponseImpl &&
            (identical(other.et0, et0) || other.et0 == et0) &&
            (identical(other.et0Ar, et0Ar) || other.et0Ar == et0Ar) &&
            (identical(other.method, method) || other.method == method) &&
            const DeepCollectionEquality()
                .equals(other._weatherSummary, _weatherSummary) &&
            (identical(other.calculationDate, calculationDate) ||
                other.calculationDate == calculationDate));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(runtimeType, et0, et0Ar, method,
      const DeepCollectionEquality().hash(_weatherSummary), calculationDate);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$ET0ResponseImplCopyWith<_$ET0ResponseImpl> get copyWith =>
      __$$ET0ResponseImplCopyWithImpl<_$ET0ResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$ET0ResponseImplToJson(
      this,
    );
  }
}

abstract class _ET0Response implements ET0Response {
  const factory _ET0Response(
      {required final double et0,
      required final String et0Ar,
      required final String method,
      required final Map<String, dynamic> weatherSummary,
      required final DateTime calculationDate}) = _$ET0ResponseImpl;

  factory _ET0Response.fromJson(Map<String, dynamic> json) =
      _$ET0ResponseImpl.fromJson;

  @override
  double get et0;
  @override
  String get et0Ar;
  @override
  String get method;
  @override
  Map<String, dynamic> get weatherSummary;
  @override
  DateTime get calculationDate;
  @override
  @JsonKey(ignore: true)
  _$$ET0ResponseImplCopyWith<_$ET0ResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CropETcResponse _$CropETcResponseFromJson(Map<String, dynamic> json) {
  return _CropETcResponse.fromJson(json);
}

/// @nodoc
mixin _$CropETcResponse {
  String get cropType => throw _privateConstructorUsedError;
  String get cropNameAr => throw _privateConstructorUsedError;
  String get growthStage => throw _privateConstructorUsedError;
  double get kc => throw _privateConstructorUsedError;
  double get et0 => throw _privateConstructorUsedError;
  double get etc => throw _privateConstructorUsedError;
  double get dailyWaterNeedLiters => throw _privateConstructorUsedError;
  double get dailyWaterNeedM3 => throw _privateConstructorUsedError;
  double get weeklyWaterNeedM3 => throw _privateConstructorUsedError;
  bool get criticalPeriod => throw _privateConstructorUsedError;
  String get notes => throw _privateConstructorUsedError;
  String get notesAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $CropETcResponseCopyWith<CropETcResponse> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CropETcResponseCopyWith<$Res> {
  factory $CropETcResponseCopyWith(
          CropETcResponse value, $Res Function(CropETcResponse) then) =
      _$CropETcResponseCopyWithImpl<$Res, CropETcResponse>;
  @useResult
  $Res call(
      {String cropType,
      String cropNameAr,
      String growthStage,
      double kc,
      double et0,
      double etc,
      double dailyWaterNeedLiters,
      double dailyWaterNeedM3,
      double weeklyWaterNeedM3,
      bool criticalPeriod,
      String notes,
      String notesAr});
}

/// @nodoc
class _$CropETcResponseCopyWithImpl<$Res, $Val extends CropETcResponse>
    implements $CropETcResponseCopyWith<$Res> {
  _$CropETcResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropType = null,
    Object? cropNameAr = null,
    Object? growthStage = null,
    Object? kc = null,
    Object? et0 = null,
    Object? etc = null,
    Object? dailyWaterNeedLiters = null,
    Object? dailyWaterNeedM3 = null,
    Object? weeklyWaterNeedM3 = null,
    Object? criticalPeriod = null,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_value.copyWith(
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      cropNameAr: null == cropNameAr
          ? _value.cropNameAr
          : cropNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      kc: null == kc
          ? _value.kc
          : kc // ignore: cast_nullable_to_non_nullable
              as double,
      et0: null == et0
          ? _value.et0
          : et0 // ignore: cast_nullable_to_non_nullable
              as double,
      etc: null == etc
          ? _value.etc
          : etc // ignore: cast_nullable_to_non_nullable
              as double,
      dailyWaterNeedLiters: null == dailyWaterNeedLiters
          ? _value.dailyWaterNeedLiters
          : dailyWaterNeedLiters // ignore: cast_nullable_to_non_nullable
              as double,
      dailyWaterNeedM3: null == dailyWaterNeedM3
          ? _value.dailyWaterNeedM3
          : dailyWaterNeedM3 // ignore: cast_nullable_to_non_nullable
              as double,
      weeklyWaterNeedM3: null == weeklyWaterNeedM3
          ? _value.weeklyWaterNeedM3
          : weeklyWaterNeedM3 // ignore: cast_nullable_to_non_nullable
              as double,
      criticalPeriod: null == criticalPeriod
          ? _value.criticalPeriod
          : criticalPeriod // ignore: cast_nullable_to_non_nullable
              as bool,
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
abstract class _$$CropETcResponseImplCopyWith<$Res>
    implements $CropETcResponseCopyWith<$Res> {
  factory _$$CropETcResponseImplCopyWith(_$CropETcResponseImpl value,
          $Res Function(_$CropETcResponseImpl) then) =
      __$$CropETcResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String cropType,
      String cropNameAr,
      String growthStage,
      double kc,
      double et0,
      double etc,
      double dailyWaterNeedLiters,
      double dailyWaterNeedM3,
      double weeklyWaterNeedM3,
      bool criticalPeriod,
      String notes,
      String notesAr});
}

/// @nodoc
class __$$CropETcResponseImplCopyWithImpl<$Res>
    extends _$CropETcResponseCopyWithImpl<$Res, _$CropETcResponseImpl>
    implements _$$CropETcResponseImplCopyWith<$Res> {
  __$$CropETcResponseImplCopyWithImpl(
      _$CropETcResponseImpl _value, $Res Function(_$CropETcResponseImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropType = null,
    Object? cropNameAr = null,
    Object? growthStage = null,
    Object? kc = null,
    Object? et0 = null,
    Object? etc = null,
    Object? dailyWaterNeedLiters = null,
    Object? dailyWaterNeedM3 = null,
    Object? weeklyWaterNeedM3 = null,
    Object? criticalPeriod = null,
    Object? notes = null,
    Object? notesAr = null,
  }) {
    return _then(_$CropETcResponseImpl(
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      cropNameAr: null == cropNameAr
          ? _value.cropNameAr
          : cropNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      kc: null == kc
          ? _value.kc
          : kc // ignore: cast_nullable_to_non_nullable
              as double,
      et0: null == et0
          ? _value.et0
          : et0 // ignore: cast_nullable_to_non_nullable
              as double,
      etc: null == etc
          ? _value.etc
          : etc // ignore: cast_nullable_to_non_nullable
              as double,
      dailyWaterNeedLiters: null == dailyWaterNeedLiters
          ? _value.dailyWaterNeedLiters
          : dailyWaterNeedLiters // ignore: cast_nullable_to_non_nullable
              as double,
      dailyWaterNeedM3: null == dailyWaterNeedM3
          ? _value.dailyWaterNeedM3
          : dailyWaterNeedM3 // ignore: cast_nullable_to_non_nullable
              as double,
      weeklyWaterNeedM3: null == weeklyWaterNeedM3
          ? _value.weeklyWaterNeedM3
          : weeklyWaterNeedM3 // ignore: cast_nullable_to_non_nullable
              as double,
      criticalPeriod: null == criticalPeriod
          ? _value.criticalPeriod
          : criticalPeriod // ignore: cast_nullable_to_non_nullable
              as bool,
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
class _$CropETcResponseImpl implements _CropETcResponse {
  const _$CropETcResponseImpl(
      {required this.cropType,
      required this.cropNameAr,
      required this.growthStage,
      required this.kc,
      required this.et0,
      required this.etc,
      required this.dailyWaterNeedLiters,
      required this.dailyWaterNeedM3,
      required this.weeklyWaterNeedM3,
      required this.criticalPeriod,
      required this.notes,
      required this.notesAr});

  factory _$CropETcResponseImpl.fromJson(Map<String, dynamic> json) =>
      _$$CropETcResponseImplFromJson(json);

  @override
  final String cropType;
  @override
  final String cropNameAr;
  @override
  final String growthStage;
  @override
  final double kc;
  @override
  final double et0;
  @override
  final double etc;
  @override
  final double dailyWaterNeedLiters;
  @override
  final double dailyWaterNeedM3;
  @override
  final double weeklyWaterNeedM3;
  @override
  final bool criticalPeriod;
  @override
  final String notes;
  @override
  final String notesAr;

  @override
  String toString() {
    return 'CropETcResponse(cropType: $cropType, cropNameAr: $cropNameAr, growthStage: $growthStage, kc: $kc, et0: $et0, etc: $etc, dailyWaterNeedLiters: $dailyWaterNeedLiters, dailyWaterNeedM3: $dailyWaterNeedM3, weeklyWaterNeedM3: $weeklyWaterNeedM3, criticalPeriod: $criticalPeriod, notes: $notes, notesAr: $notesAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CropETcResponseImpl &&
            (identical(other.cropType, cropType) ||
                other.cropType == cropType) &&
            (identical(other.cropNameAr, cropNameAr) ||
                other.cropNameAr == cropNameAr) &&
            (identical(other.growthStage, growthStage) ||
                other.growthStage == growthStage) &&
            (identical(other.kc, kc) || other.kc == kc) &&
            (identical(other.et0, et0) || other.et0 == et0) &&
            (identical(other.etc, etc) || other.etc == etc) &&
            (identical(other.dailyWaterNeedLiters, dailyWaterNeedLiters) ||
                other.dailyWaterNeedLiters == dailyWaterNeedLiters) &&
            (identical(other.dailyWaterNeedM3, dailyWaterNeedM3) ||
                other.dailyWaterNeedM3 == dailyWaterNeedM3) &&
            (identical(other.weeklyWaterNeedM3, weeklyWaterNeedM3) ||
                other.weeklyWaterNeedM3 == weeklyWaterNeedM3) &&
            (identical(other.criticalPeriod, criticalPeriod) ||
                other.criticalPeriod == criticalPeriod) &&
            (identical(other.notes, notes) || other.notes == notes) &&
            (identical(other.notesAr, notesAr) || other.notesAr == notesAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      cropType,
      cropNameAr,
      growthStage,
      kc,
      et0,
      etc,
      dailyWaterNeedLiters,
      dailyWaterNeedM3,
      weeklyWaterNeedM3,
      criticalPeriod,
      notes,
      notesAr);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$CropETcResponseImplCopyWith<_$CropETcResponseImpl> get copyWith =>
      __$$CropETcResponseImplCopyWithImpl<_$CropETcResponseImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CropETcResponseImplToJson(
      this,
    );
  }
}

abstract class _CropETcResponse implements CropETcResponse {
  const factory _CropETcResponse(
      {required final String cropType,
      required final String cropNameAr,
      required final String growthStage,
      required final double kc,
      required final double et0,
      required final double etc,
      required final double dailyWaterNeedLiters,
      required final double dailyWaterNeedM3,
      required final double weeklyWaterNeedM3,
      required final bool criticalPeriod,
      required final String notes,
      required final String notesAr}) = _$CropETcResponseImpl;

  factory _CropETcResponse.fromJson(Map<String, dynamic> json) =
      _$CropETcResponseImpl.fromJson;

  @override
  String get cropType;
  @override
  String get cropNameAr;
  @override
  String get growthStage;
  @override
  double get kc;
  @override
  double get et0;
  @override
  double get etc;
  @override
  double get dailyWaterNeedLiters;
  @override
  double get dailyWaterNeedM3;
  @override
  double get weeklyWaterNeedM3;
  @override
  bool get criticalPeriod;
  @override
  String get notes;
  @override
  String get notesAr;
  @override
  @JsonKey(ignore: true)
  _$$CropETcResponseImplCopyWith<_$CropETcResponseImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

CropKcOption _$CropKcOptionFromJson(Map<String, dynamic> json) {
  return _CropKcOption.fromJson(json);
}

/// @nodoc
mixin _$CropKcOption {
  String get cropId => throw _privateConstructorUsedError;
  String get name => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;
  double get kcInitial => throw _privateConstructorUsedError;
  double get kcMid => throw _privateConstructorUsedError;
  double get kcEnd => throw _privateConstructorUsedError;
  double get rootDepthMax => throw _privateConstructorUsedError;
  List<String> get criticalPeriods => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $CropKcOptionCopyWith<CropKcOption> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $CropKcOptionCopyWith<$Res> {
  factory $CropKcOptionCopyWith(
          CropKcOption value, $Res Function(CropKcOption) then) =
      _$CropKcOptionCopyWithImpl<$Res, CropKcOption>;
  @useResult
  $Res call(
      {String cropId,
      String name,
      String nameAr,
      double kcInitial,
      double kcMid,
      double kcEnd,
      double rootDepthMax,
      List<String> criticalPeriods});
}

/// @nodoc
class _$CropKcOptionCopyWithImpl<$Res, $Val extends CropKcOption>
    implements $CropKcOptionCopyWith<$Res> {
  _$CropKcOptionCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? kcInitial = null,
    Object? kcMid = null,
    Object? kcEnd = null,
    Object? rootDepthMax = null,
    Object? criticalPeriods = null,
  }) {
    return _then(_value.copyWith(
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
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
      rootDepthMax: null == rootDepthMax
          ? _value.rootDepthMax
          : rootDepthMax // ignore: cast_nullable_to_non_nullable
              as double,
      criticalPeriods: null == criticalPeriods
          ? _value.criticalPeriods
          : criticalPeriods // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$CropKcOptionImplCopyWith<$Res>
    implements $CropKcOptionCopyWith<$Res> {
  factory _$$CropKcOptionImplCopyWith(
          _$CropKcOptionImpl value, $Res Function(_$CropKcOptionImpl) then) =
      __$$CropKcOptionImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String cropId,
      String name,
      String nameAr,
      double kcInitial,
      double kcMid,
      double kcEnd,
      double rootDepthMax,
      List<String> criticalPeriods});
}

/// @nodoc
class __$$CropKcOptionImplCopyWithImpl<$Res>
    extends _$CropKcOptionCopyWithImpl<$Res, _$CropKcOptionImpl>
    implements _$$CropKcOptionImplCopyWith<$Res> {
  __$$CropKcOptionImplCopyWithImpl(
      _$CropKcOptionImpl _value, $Res Function(_$CropKcOptionImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropId = null,
    Object? name = null,
    Object? nameAr = null,
    Object? kcInitial = null,
    Object? kcMid = null,
    Object? kcEnd = null,
    Object? rootDepthMax = null,
    Object? criticalPeriods = null,
  }) {
    return _then(_$CropKcOptionImpl(
      cropId: null == cropId
          ? _value.cropId
          : cropId // ignore: cast_nullable_to_non_nullable
              as String,
      name: null == name
          ? _value.name
          : name // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
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
      rootDepthMax: null == rootDepthMax
          ? _value.rootDepthMax
          : rootDepthMax // ignore: cast_nullable_to_non_nullable
              as double,
      criticalPeriods: null == criticalPeriods
          ? _value._criticalPeriods
          : criticalPeriods // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$CropKcOptionImpl implements _CropKcOption {
  const _$CropKcOptionImpl(
      {required this.cropId,
      required this.name,
      required this.nameAr,
      required this.kcInitial,
      required this.kcMid,
      required this.kcEnd,
      required this.rootDepthMax,
      final List<String> criticalPeriods = const []})
      : _criticalPeriods = criticalPeriods;

  factory _$CropKcOptionImpl.fromJson(Map<String, dynamic> json) =>
      _$$CropKcOptionImplFromJson(json);

  @override
  final String cropId;
  @override
  final String name;
  @override
  final String nameAr;
  @override
  final double kcInitial;
  @override
  final double kcMid;
  @override
  final double kcEnd;
  @override
  final double rootDepthMax;
  final List<String> _criticalPeriods;
  @override
  @JsonKey()
  List<String> get criticalPeriods {
    if (_criticalPeriods is EqualUnmodifiableListView) return _criticalPeriods;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_criticalPeriods);
  }

  @override
  String toString() {
    return 'CropKcOption(cropId: $cropId, name: $name, nameAr: $nameAr, kcInitial: $kcInitial, kcMid: $kcMid, kcEnd: $kcEnd, rootDepthMax: $rootDepthMax, criticalPeriods: $criticalPeriods)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$CropKcOptionImpl &&
            (identical(other.cropId, cropId) || other.cropId == cropId) &&
            (identical(other.name, name) || other.name == name) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.kcInitial, kcInitial) ||
                other.kcInitial == kcInitial) &&
            (identical(other.kcMid, kcMid) || other.kcMid == kcMid) &&
            (identical(other.kcEnd, kcEnd) || other.kcEnd == kcEnd) &&
            (identical(other.rootDepthMax, rootDepthMax) ||
                other.rootDepthMax == rootDepthMax) &&
            const DeepCollectionEquality()
                .equals(other._criticalPeriods, _criticalPeriods));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      cropId,
      name,
      nameAr,
      kcInitial,
      kcMid,
      kcEnd,
      rootDepthMax,
      const DeepCollectionEquality().hash(_criticalPeriods));

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$CropKcOptionImplCopyWith<_$CropKcOptionImpl> get copyWith =>
      __$$CropKcOptionImplCopyWithImpl<_$CropKcOptionImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$CropKcOptionImplToJson(
      this,
    );
  }
}

abstract class _CropKcOption implements CropKcOption {
  const factory _CropKcOption(
      {required final String cropId,
      required final String name,
      required final String nameAr,
      required final double kcInitial,
      required final double kcMid,
      required final double kcEnd,
      required final double rootDepthMax,
      final List<String> criticalPeriods}) = _$CropKcOptionImpl;

  factory _CropKcOption.fromJson(Map<String, dynamic> json) =
      _$CropKcOptionImpl.fromJson;

  @override
  String get cropId;
  @override
  String get name;
  @override
  String get nameAr;
  @override
  double get kcInitial;
  @override
  double get kcMid;
  @override
  double get kcEnd;
  @override
  double get rootDepthMax;
  @override
  List<String> get criticalPeriods;
  @override
  @JsonKey(ignore: true)
  _$$CropKcOptionImplCopyWith<_$CropKcOptionImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

VirtualSoilMoistureResponse _$VirtualSoilMoistureResponseFromJson(
    Map<String, dynamic> json) {
  return _VirtualSoilMoistureResponse.fromJson(json);
}

/// @nodoc
mixin _$VirtualSoilMoistureResponse {
  String get calculationId => throw _privateConstructorUsedError;
  double get estimatedMoisture => throw _privateConstructorUsedError;
  double get moisturePercentage => throw _privateConstructorUsedError;
  int get daysSinceIrrigation => throw _privateConstructorUsedError;
  double get totalEtLoss => throw _privateConstructorUsedError;
  double get availableWater => throw _privateConstructorUsedError;
  double get totalAvailableWater => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  String get statusAr => throw _privateConstructorUsedError;
  UrgencyLevel get urgency => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $VirtualSoilMoistureResponseCopyWith<VirtualSoilMoistureResponse>
      get copyWith => throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $VirtualSoilMoistureResponseCopyWith<$Res> {
  factory $VirtualSoilMoistureResponseCopyWith(
          VirtualSoilMoistureResponse value,
          $Res Function(VirtualSoilMoistureResponse) then) =
      _$VirtualSoilMoistureResponseCopyWithImpl<$Res,
          VirtualSoilMoistureResponse>;
  @useResult
  $Res call(
      {String calculationId,
      double estimatedMoisture,
      double moisturePercentage,
      int daysSinceIrrigation,
      double totalEtLoss,
      double availableWater,
      double totalAvailableWater,
      String status,
      String statusAr,
      UrgencyLevel urgency});
}

/// @nodoc
class _$VirtualSoilMoistureResponseCopyWithImpl<$Res,
        $Val extends VirtualSoilMoistureResponse>
    implements $VirtualSoilMoistureResponseCopyWith<$Res> {
  _$VirtualSoilMoistureResponseCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? calculationId = null,
    Object? estimatedMoisture = null,
    Object? moisturePercentage = null,
    Object? daysSinceIrrigation = null,
    Object? totalEtLoss = null,
    Object? availableWater = null,
    Object? totalAvailableWater = null,
    Object? status = null,
    Object? statusAr = null,
    Object? urgency = null,
  }) {
    return _then(_value.copyWith(
      calculationId: null == calculationId
          ? _value.calculationId
          : calculationId // ignore: cast_nullable_to_non_nullable
              as String,
      estimatedMoisture: null == estimatedMoisture
          ? _value.estimatedMoisture
          : estimatedMoisture // ignore: cast_nullable_to_non_nullable
              as double,
      moisturePercentage: null == moisturePercentage
          ? _value.moisturePercentage
          : moisturePercentage // ignore: cast_nullable_to_non_nullable
              as double,
      daysSinceIrrigation: null == daysSinceIrrigation
          ? _value.daysSinceIrrigation
          : daysSinceIrrigation // ignore: cast_nullable_to_non_nullable
              as int,
      totalEtLoss: null == totalEtLoss
          ? _value.totalEtLoss
          : totalEtLoss // ignore: cast_nullable_to_non_nullable
              as double,
      availableWater: null == availableWater
          ? _value.availableWater
          : availableWater // ignore: cast_nullable_to_non_nullable
              as double,
      totalAvailableWater: null == totalAvailableWater
          ? _value.totalAvailableWater
          : totalAvailableWater // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      statusAr: null == statusAr
          ? _value.statusAr
          : statusAr // ignore: cast_nullable_to_non_nullable
              as String,
      urgency: null == urgency
          ? _value.urgency
          : urgency // ignore: cast_nullable_to_non_nullable
              as UrgencyLevel,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$VirtualSoilMoistureResponseImplCopyWith<$Res>
    implements $VirtualSoilMoistureResponseCopyWith<$Res> {
  factory _$$VirtualSoilMoistureResponseImplCopyWith(
          _$VirtualSoilMoistureResponseImpl value,
          $Res Function(_$VirtualSoilMoistureResponseImpl) then) =
      __$$VirtualSoilMoistureResponseImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String calculationId,
      double estimatedMoisture,
      double moisturePercentage,
      int daysSinceIrrigation,
      double totalEtLoss,
      double availableWater,
      double totalAvailableWater,
      String status,
      String statusAr,
      UrgencyLevel urgency});
}

/// @nodoc
class __$$VirtualSoilMoistureResponseImplCopyWithImpl<$Res>
    extends _$VirtualSoilMoistureResponseCopyWithImpl<$Res,
        _$VirtualSoilMoistureResponseImpl>
    implements _$$VirtualSoilMoistureResponseImplCopyWith<$Res> {
  __$$VirtualSoilMoistureResponseImplCopyWithImpl(
      _$VirtualSoilMoistureResponseImpl _value,
      $Res Function(_$VirtualSoilMoistureResponseImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? calculationId = null,
    Object? estimatedMoisture = null,
    Object? moisturePercentage = null,
    Object? daysSinceIrrigation = null,
    Object? totalEtLoss = null,
    Object? availableWater = null,
    Object? totalAvailableWater = null,
    Object? status = null,
    Object? statusAr = null,
    Object? urgency = null,
  }) {
    return _then(_$VirtualSoilMoistureResponseImpl(
      calculationId: null == calculationId
          ? _value.calculationId
          : calculationId // ignore: cast_nullable_to_non_nullable
              as String,
      estimatedMoisture: null == estimatedMoisture
          ? _value.estimatedMoisture
          : estimatedMoisture // ignore: cast_nullable_to_non_nullable
              as double,
      moisturePercentage: null == moisturePercentage
          ? _value.moisturePercentage
          : moisturePercentage // ignore: cast_nullable_to_non_nullable
              as double,
      daysSinceIrrigation: null == daysSinceIrrigation
          ? _value.daysSinceIrrigation
          : daysSinceIrrigation // ignore: cast_nullable_to_non_nullable
              as int,
      totalEtLoss: null == totalEtLoss
          ? _value.totalEtLoss
          : totalEtLoss // ignore: cast_nullable_to_non_nullable
              as double,
      availableWater: null == availableWater
          ? _value.availableWater
          : availableWater // ignore: cast_nullable_to_non_nullable
              as double,
      totalAvailableWater: null == totalAvailableWater
          ? _value.totalAvailableWater
          : totalAvailableWater // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      statusAr: null == statusAr
          ? _value.statusAr
          : statusAr // ignore: cast_nullable_to_non_nullable
              as String,
      urgency: null == urgency
          ? _value.urgency
          : urgency // ignore: cast_nullable_to_non_nullable
              as UrgencyLevel,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$VirtualSoilMoistureResponseImpl
    implements _VirtualSoilMoistureResponse {
  const _$VirtualSoilMoistureResponseImpl(
      {required this.calculationId,
      required this.estimatedMoisture,
      required this.moisturePercentage,
      required this.daysSinceIrrigation,
      required this.totalEtLoss,
      required this.availableWater,
      required this.totalAvailableWater,
      required this.status,
      required this.statusAr,
      required this.urgency});

  factory _$VirtualSoilMoistureResponseImpl.fromJson(
          Map<String, dynamic> json) =>
      _$$VirtualSoilMoistureResponseImplFromJson(json);

  @override
  final String calculationId;
  @override
  final double estimatedMoisture;
  @override
  final double moisturePercentage;
  @override
  final int daysSinceIrrigation;
  @override
  final double totalEtLoss;
  @override
  final double availableWater;
  @override
  final double totalAvailableWater;
  @override
  final String status;
  @override
  final String statusAr;
  @override
  final UrgencyLevel urgency;

  @override
  String toString() {
    return 'VirtualSoilMoistureResponse(calculationId: $calculationId, estimatedMoisture: $estimatedMoisture, moisturePercentage: $moisturePercentage, daysSinceIrrigation: $daysSinceIrrigation, totalEtLoss: $totalEtLoss, availableWater: $availableWater, totalAvailableWater: $totalAvailableWater, status: $status, statusAr: $statusAr, urgency: $urgency)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$VirtualSoilMoistureResponseImpl &&
            (identical(other.calculationId, calculationId) ||
                other.calculationId == calculationId) &&
            (identical(other.estimatedMoisture, estimatedMoisture) ||
                other.estimatedMoisture == estimatedMoisture) &&
            (identical(other.moisturePercentage, moisturePercentage) ||
                other.moisturePercentage == moisturePercentage) &&
            (identical(other.daysSinceIrrigation, daysSinceIrrigation) ||
                other.daysSinceIrrigation == daysSinceIrrigation) &&
            (identical(other.totalEtLoss, totalEtLoss) ||
                other.totalEtLoss == totalEtLoss) &&
            (identical(other.availableWater, availableWater) ||
                other.availableWater == availableWater) &&
            (identical(other.totalAvailableWater, totalAvailableWater) ||
                other.totalAvailableWater == totalAvailableWater) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.statusAr, statusAr) ||
                other.statusAr == statusAr) &&
            (identical(other.urgency, urgency) || other.urgency == urgency));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      calculationId,
      estimatedMoisture,
      moisturePercentage,
      daysSinceIrrigation,
      totalEtLoss,
      availableWater,
      totalAvailableWater,
      status,
      statusAr,
      urgency);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$VirtualSoilMoistureResponseImplCopyWith<_$VirtualSoilMoistureResponseImpl>
      get copyWith => __$$VirtualSoilMoistureResponseImplCopyWithImpl<
          _$VirtualSoilMoistureResponseImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$VirtualSoilMoistureResponseImplToJson(
      this,
    );
  }
}

abstract class _VirtualSoilMoistureResponse
    implements VirtualSoilMoistureResponse {
  const factory _VirtualSoilMoistureResponse(
      {required final String calculationId,
      required final double estimatedMoisture,
      required final double moisturePercentage,
      required final int daysSinceIrrigation,
      required final double totalEtLoss,
      required final double availableWater,
      required final double totalAvailableWater,
      required final String status,
      required final String statusAr,
      required final UrgencyLevel urgency}) = _$VirtualSoilMoistureResponseImpl;

  factory _VirtualSoilMoistureResponse.fromJson(Map<String, dynamic> json) =
      _$VirtualSoilMoistureResponseImpl.fromJson;

  @override
  String get calculationId;
  @override
  double get estimatedMoisture;
  @override
  double get moisturePercentage;
  @override
  int get daysSinceIrrigation;
  @override
  double get totalEtLoss;
  @override
  double get availableWater;
  @override
  double get totalAvailableWater;
  @override
  String get status;
  @override
  String get statusAr;
  @override
  UrgencyLevel get urgency;
  @override
  @JsonKey(ignore: true)
  _$$VirtualSoilMoistureResponseImplCopyWith<_$VirtualSoilMoistureResponseImpl>
      get copyWith => throw _privateConstructorUsedError;
}

IrrigationRecommendation _$IrrigationRecommendationFromJson(
    Map<String, dynamic> json) {
  return _IrrigationRecommendation.fromJson(json);
}

/// @nodoc
mixin _$IrrigationRecommendation {
  String get recommendationId => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError; // Field info
  String get cropType => throw _privateConstructorUsedError;
  String get cropNameAr => throw _privateConstructorUsedError;
  String get growthStage => throw _privateConstructorUsedError;
  double get fieldAreaHectares =>
      throw _privateConstructorUsedError; // Calculations
  double get et0 => throw _privateConstructorUsedError;
  double get kc => throw _privateConstructorUsedError;
  double get etc => throw _privateConstructorUsedError; // Soil status
  String get soilType => throw _privateConstructorUsedError;
  String get soilTypeAr => throw _privateConstructorUsedError;
  double get estimatedMoisture => throw _privateConstructorUsedError;
  double get moistureDepletionPercent =>
      throw _privateConstructorUsedError; // Recommendation
  bool get irrigationNeeded => throw _privateConstructorUsedError;
  UrgencyLevel get urgency => throw _privateConstructorUsedError;
  String get urgencyAr => throw _privateConstructorUsedError;
  double get recommendedAmountMm => throw _privateConstructorUsedError;
  double get recommendedAmountLiters => throw _privateConstructorUsedError;
  double get recommendedAmountM3 => throw _privateConstructorUsedError;
  double get grossIrrigationMm => throw _privateConstructorUsedError; // Timing
  String get optimalTime => throw _privateConstructorUsedError;
  String get optimalTimeAr => throw _privateConstructorUsedError;
  int get nextIrrigationDays => throw _privateConstructorUsedError; // Advice
  String get advice => throw _privateConstructorUsedError;
  String get adviceAr => throw _privateConstructorUsedError;
  List<String> get warnings => throw _privateConstructorUsedError;
  List<String> get warningsAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $IrrigationRecommendationCopyWith<IrrigationRecommendation> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IrrigationRecommendationCopyWith<$Res> {
  factory $IrrigationRecommendationCopyWith(IrrigationRecommendation value,
          $Res Function(IrrigationRecommendation) then) =
      _$IrrigationRecommendationCopyWithImpl<$Res, IrrigationRecommendation>;
  @useResult
  $Res call(
      {String recommendationId,
      DateTime timestamp,
      String cropType,
      String cropNameAr,
      String growthStage,
      double fieldAreaHectares,
      double et0,
      double kc,
      double etc,
      String soilType,
      String soilTypeAr,
      double estimatedMoisture,
      double moistureDepletionPercent,
      bool irrigationNeeded,
      UrgencyLevel urgency,
      String urgencyAr,
      double recommendedAmountMm,
      double recommendedAmountLiters,
      double recommendedAmountM3,
      double grossIrrigationMm,
      String optimalTime,
      String optimalTimeAr,
      int nextIrrigationDays,
      String advice,
      String adviceAr,
      List<String> warnings,
      List<String> warningsAr});
}

/// @nodoc
class _$IrrigationRecommendationCopyWithImpl<$Res,
        $Val extends IrrigationRecommendation>
    implements $IrrigationRecommendationCopyWith<$Res> {
  _$IrrigationRecommendationCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? recommendationId = null,
    Object? timestamp = null,
    Object? cropType = null,
    Object? cropNameAr = null,
    Object? growthStage = null,
    Object? fieldAreaHectares = null,
    Object? et0 = null,
    Object? kc = null,
    Object? etc = null,
    Object? soilType = null,
    Object? soilTypeAr = null,
    Object? estimatedMoisture = null,
    Object? moistureDepletionPercent = null,
    Object? irrigationNeeded = null,
    Object? urgency = null,
    Object? urgencyAr = null,
    Object? recommendedAmountMm = null,
    Object? recommendedAmountLiters = null,
    Object? recommendedAmountM3 = null,
    Object? grossIrrigationMm = null,
    Object? optimalTime = null,
    Object? optimalTimeAr = null,
    Object? nextIrrigationDays = null,
    Object? advice = null,
    Object? adviceAr = null,
    Object? warnings = null,
    Object? warningsAr = null,
  }) {
    return _then(_value.copyWith(
      recommendationId: null == recommendationId
          ? _value.recommendationId
          : recommendationId // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      cropNameAr: null == cropNameAr
          ? _value.cropNameAr
          : cropNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      fieldAreaHectares: null == fieldAreaHectares
          ? _value.fieldAreaHectares
          : fieldAreaHectares // ignore: cast_nullable_to_non_nullable
              as double,
      et0: null == et0
          ? _value.et0
          : et0 // ignore: cast_nullable_to_non_nullable
              as double,
      kc: null == kc
          ? _value.kc
          : kc // ignore: cast_nullable_to_non_nullable
              as double,
      etc: null == etc
          ? _value.etc
          : etc // ignore: cast_nullable_to_non_nullable
              as double,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      soilTypeAr: null == soilTypeAr
          ? _value.soilTypeAr
          : soilTypeAr // ignore: cast_nullable_to_non_nullable
              as String,
      estimatedMoisture: null == estimatedMoisture
          ? _value.estimatedMoisture
          : estimatedMoisture // ignore: cast_nullable_to_non_nullable
              as double,
      moistureDepletionPercent: null == moistureDepletionPercent
          ? _value.moistureDepletionPercent
          : moistureDepletionPercent // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationNeeded: null == irrigationNeeded
          ? _value.irrigationNeeded
          : irrigationNeeded // ignore: cast_nullable_to_non_nullable
              as bool,
      urgency: null == urgency
          ? _value.urgency
          : urgency // ignore: cast_nullable_to_non_nullable
              as UrgencyLevel,
      urgencyAr: null == urgencyAr
          ? _value.urgencyAr
          : urgencyAr // ignore: cast_nullable_to_non_nullable
              as String,
      recommendedAmountMm: null == recommendedAmountMm
          ? _value.recommendedAmountMm
          : recommendedAmountMm // ignore: cast_nullable_to_non_nullable
              as double,
      recommendedAmountLiters: null == recommendedAmountLiters
          ? _value.recommendedAmountLiters
          : recommendedAmountLiters // ignore: cast_nullable_to_non_nullable
              as double,
      recommendedAmountM3: null == recommendedAmountM3
          ? _value.recommendedAmountM3
          : recommendedAmountM3 // ignore: cast_nullable_to_non_nullable
              as double,
      grossIrrigationMm: null == grossIrrigationMm
          ? _value.grossIrrigationMm
          : grossIrrigationMm // ignore: cast_nullable_to_non_nullable
              as double,
      optimalTime: null == optimalTime
          ? _value.optimalTime
          : optimalTime // ignore: cast_nullable_to_non_nullable
              as String,
      optimalTimeAr: null == optimalTimeAr
          ? _value.optimalTimeAr
          : optimalTimeAr // ignore: cast_nullable_to_non_nullable
              as String,
      nextIrrigationDays: null == nextIrrigationDays
          ? _value.nextIrrigationDays
          : nextIrrigationDays // ignore: cast_nullable_to_non_nullable
              as int,
      advice: null == advice
          ? _value.advice
          : advice // ignore: cast_nullable_to_non_nullable
              as String,
      adviceAr: null == adviceAr
          ? _value.adviceAr
          : adviceAr // ignore: cast_nullable_to_non_nullable
              as String,
      warnings: null == warnings
          ? _value.warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warningsAr: null == warningsAr
          ? _value.warningsAr
          : warningsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IrrigationRecommendationImplCopyWith<$Res>
    implements $IrrigationRecommendationCopyWith<$Res> {
  factory _$$IrrigationRecommendationImplCopyWith(
          _$IrrigationRecommendationImpl value,
          $Res Function(_$IrrigationRecommendationImpl) then) =
      __$$IrrigationRecommendationImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String recommendationId,
      DateTime timestamp,
      String cropType,
      String cropNameAr,
      String growthStage,
      double fieldAreaHectares,
      double et0,
      double kc,
      double etc,
      String soilType,
      String soilTypeAr,
      double estimatedMoisture,
      double moistureDepletionPercent,
      bool irrigationNeeded,
      UrgencyLevel urgency,
      String urgencyAr,
      double recommendedAmountMm,
      double recommendedAmountLiters,
      double recommendedAmountM3,
      double grossIrrigationMm,
      String optimalTime,
      String optimalTimeAr,
      int nextIrrigationDays,
      String advice,
      String adviceAr,
      List<String> warnings,
      List<String> warningsAr});
}

/// @nodoc
class __$$IrrigationRecommendationImplCopyWithImpl<$Res>
    extends _$IrrigationRecommendationCopyWithImpl<$Res,
        _$IrrigationRecommendationImpl>
    implements _$$IrrigationRecommendationImplCopyWith<$Res> {
  __$$IrrigationRecommendationImplCopyWithImpl(
      _$IrrigationRecommendationImpl _value,
      $Res Function(_$IrrigationRecommendationImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? recommendationId = null,
    Object? timestamp = null,
    Object? cropType = null,
    Object? cropNameAr = null,
    Object? growthStage = null,
    Object? fieldAreaHectares = null,
    Object? et0 = null,
    Object? kc = null,
    Object? etc = null,
    Object? soilType = null,
    Object? soilTypeAr = null,
    Object? estimatedMoisture = null,
    Object? moistureDepletionPercent = null,
    Object? irrigationNeeded = null,
    Object? urgency = null,
    Object? urgencyAr = null,
    Object? recommendedAmountMm = null,
    Object? recommendedAmountLiters = null,
    Object? recommendedAmountM3 = null,
    Object? grossIrrigationMm = null,
    Object? optimalTime = null,
    Object? optimalTimeAr = null,
    Object? nextIrrigationDays = null,
    Object? advice = null,
    Object? adviceAr = null,
    Object? warnings = null,
    Object? warningsAr = null,
  }) {
    return _then(_$IrrigationRecommendationImpl(
      recommendationId: null == recommendationId
          ? _value.recommendationId
          : recommendationId // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      cropNameAr: null == cropNameAr
          ? _value.cropNameAr
          : cropNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      fieldAreaHectares: null == fieldAreaHectares
          ? _value.fieldAreaHectares
          : fieldAreaHectares // ignore: cast_nullable_to_non_nullable
              as double,
      et0: null == et0
          ? _value.et0
          : et0 // ignore: cast_nullable_to_non_nullable
              as double,
      kc: null == kc
          ? _value.kc
          : kc // ignore: cast_nullable_to_non_nullable
              as double,
      etc: null == etc
          ? _value.etc
          : etc // ignore: cast_nullable_to_non_nullable
              as double,
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      soilTypeAr: null == soilTypeAr
          ? _value.soilTypeAr
          : soilTypeAr // ignore: cast_nullable_to_non_nullable
              as String,
      estimatedMoisture: null == estimatedMoisture
          ? _value.estimatedMoisture
          : estimatedMoisture // ignore: cast_nullable_to_non_nullable
              as double,
      moistureDepletionPercent: null == moistureDepletionPercent
          ? _value.moistureDepletionPercent
          : moistureDepletionPercent // ignore: cast_nullable_to_non_nullable
              as double,
      irrigationNeeded: null == irrigationNeeded
          ? _value.irrigationNeeded
          : irrigationNeeded // ignore: cast_nullable_to_non_nullable
              as bool,
      urgency: null == urgency
          ? _value.urgency
          : urgency // ignore: cast_nullable_to_non_nullable
              as UrgencyLevel,
      urgencyAr: null == urgencyAr
          ? _value.urgencyAr
          : urgencyAr // ignore: cast_nullable_to_non_nullable
              as String,
      recommendedAmountMm: null == recommendedAmountMm
          ? _value.recommendedAmountMm
          : recommendedAmountMm // ignore: cast_nullable_to_non_nullable
              as double,
      recommendedAmountLiters: null == recommendedAmountLiters
          ? _value.recommendedAmountLiters
          : recommendedAmountLiters // ignore: cast_nullable_to_non_nullable
              as double,
      recommendedAmountM3: null == recommendedAmountM3
          ? _value.recommendedAmountM3
          : recommendedAmountM3 // ignore: cast_nullable_to_non_nullable
              as double,
      grossIrrigationMm: null == grossIrrigationMm
          ? _value.grossIrrigationMm
          : grossIrrigationMm // ignore: cast_nullable_to_non_nullable
              as double,
      optimalTime: null == optimalTime
          ? _value.optimalTime
          : optimalTime // ignore: cast_nullable_to_non_nullable
              as String,
      optimalTimeAr: null == optimalTimeAr
          ? _value.optimalTimeAr
          : optimalTimeAr // ignore: cast_nullable_to_non_nullable
              as String,
      nextIrrigationDays: null == nextIrrigationDays
          ? _value.nextIrrigationDays
          : nextIrrigationDays // ignore: cast_nullable_to_non_nullable
              as int,
      advice: null == advice
          ? _value.advice
          : advice // ignore: cast_nullable_to_non_nullable
              as String,
      adviceAr: null == adviceAr
          ? _value.adviceAr
          : adviceAr // ignore: cast_nullable_to_non_nullable
              as String,
      warnings: null == warnings
          ? _value._warnings
          : warnings // ignore: cast_nullable_to_non_nullable
              as List<String>,
      warningsAr: null == warningsAr
          ? _value._warningsAr
          : warningsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IrrigationRecommendationImpl implements _IrrigationRecommendation {
  const _$IrrigationRecommendationImpl(
      {required this.recommendationId,
      required this.timestamp,
      required this.cropType,
      required this.cropNameAr,
      required this.growthStage,
      required this.fieldAreaHectares,
      required this.et0,
      required this.kc,
      required this.etc,
      required this.soilType,
      required this.soilTypeAr,
      required this.estimatedMoisture,
      required this.moistureDepletionPercent,
      required this.irrigationNeeded,
      required this.urgency,
      required this.urgencyAr,
      required this.recommendedAmountMm,
      required this.recommendedAmountLiters,
      required this.recommendedAmountM3,
      required this.grossIrrigationMm,
      required this.optimalTime,
      required this.optimalTimeAr,
      required this.nextIrrigationDays,
      required this.advice,
      required this.adviceAr,
      final List<String> warnings = const [],
      final List<String> warningsAr = const []})
      : _warnings = warnings,
        _warningsAr = warningsAr;

  factory _$IrrigationRecommendationImpl.fromJson(Map<String, dynamic> json) =>
      _$$IrrigationRecommendationImplFromJson(json);

  @override
  final String recommendationId;
  @override
  final DateTime timestamp;
// Field info
  @override
  final String cropType;
  @override
  final String cropNameAr;
  @override
  final String growthStage;
  @override
  final double fieldAreaHectares;
// Calculations
  @override
  final double et0;
  @override
  final double kc;
  @override
  final double etc;
// Soil status
  @override
  final String soilType;
  @override
  final String soilTypeAr;
  @override
  final double estimatedMoisture;
  @override
  final double moistureDepletionPercent;
// Recommendation
  @override
  final bool irrigationNeeded;
  @override
  final UrgencyLevel urgency;
  @override
  final String urgencyAr;
  @override
  final double recommendedAmountMm;
  @override
  final double recommendedAmountLiters;
  @override
  final double recommendedAmountM3;
  @override
  final double grossIrrigationMm;
// Timing
  @override
  final String optimalTime;
  @override
  final String optimalTimeAr;
  @override
  final int nextIrrigationDays;
// Advice
  @override
  final String advice;
  @override
  final String adviceAr;
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
  String toString() {
    return 'IrrigationRecommendation(recommendationId: $recommendationId, timestamp: $timestamp, cropType: $cropType, cropNameAr: $cropNameAr, growthStage: $growthStage, fieldAreaHectares: $fieldAreaHectares, et0: $et0, kc: $kc, etc: $etc, soilType: $soilType, soilTypeAr: $soilTypeAr, estimatedMoisture: $estimatedMoisture, moistureDepletionPercent: $moistureDepletionPercent, irrigationNeeded: $irrigationNeeded, urgency: $urgency, urgencyAr: $urgencyAr, recommendedAmountMm: $recommendedAmountMm, recommendedAmountLiters: $recommendedAmountLiters, recommendedAmountM3: $recommendedAmountM3, grossIrrigationMm: $grossIrrigationMm, optimalTime: $optimalTime, optimalTimeAr: $optimalTimeAr, nextIrrigationDays: $nextIrrigationDays, advice: $advice, adviceAr: $adviceAr, warnings: $warnings, warningsAr: $warningsAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IrrigationRecommendationImpl &&
            (identical(other.recommendationId, recommendationId) ||
                other.recommendationId == recommendationId) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.cropType, cropType) ||
                other.cropType == cropType) &&
            (identical(other.cropNameAr, cropNameAr) ||
                other.cropNameAr == cropNameAr) &&
            (identical(other.growthStage, growthStage) ||
                other.growthStage == growthStage) &&
            (identical(other.fieldAreaHectares, fieldAreaHectares) ||
                other.fieldAreaHectares == fieldAreaHectares) &&
            (identical(other.et0, et0) || other.et0 == et0) &&
            (identical(other.kc, kc) || other.kc == kc) &&
            (identical(other.etc, etc) || other.etc == etc) &&
            (identical(other.soilType, soilType) ||
                other.soilType == soilType) &&
            (identical(other.soilTypeAr, soilTypeAr) ||
                other.soilTypeAr == soilTypeAr) &&
            (identical(other.estimatedMoisture, estimatedMoisture) ||
                other.estimatedMoisture == estimatedMoisture) &&
            (identical(
                    other.moistureDepletionPercent, moistureDepletionPercent) ||
                other.moistureDepletionPercent == moistureDepletionPercent) &&
            (identical(other.irrigationNeeded, irrigationNeeded) ||
                other.irrigationNeeded == irrigationNeeded) &&
            (identical(other.urgency, urgency) || other.urgency == urgency) &&
            (identical(other.urgencyAr, urgencyAr) ||
                other.urgencyAr == urgencyAr) &&
            (identical(other.recommendedAmountMm, recommendedAmountMm) ||
                other.recommendedAmountMm == recommendedAmountMm) &&
            (identical(
                    other.recommendedAmountLiters, recommendedAmountLiters) ||
                other.recommendedAmountLiters == recommendedAmountLiters) &&
            (identical(other.recommendedAmountM3, recommendedAmountM3) ||
                other.recommendedAmountM3 == recommendedAmountM3) &&
            (identical(other.grossIrrigationMm, grossIrrigationMm) ||
                other.grossIrrigationMm == grossIrrigationMm) &&
            (identical(other.optimalTime, optimalTime) ||
                other.optimalTime == optimalTime) &&
            (identical(other.optimalTimeAr, optimalTimeAr) ||
                other.optimalTimeAr == optimalTimeAr) &&
            (identical(other.nextIrrigationDays, nextIrrigationDays) ||
                other.nextIrrigationDays == nextIrrigationDays) &&
            (identical(other.advice, advice) || other.advice == advice) &&
            (identical(other.adviceAr, adviceAr) ||
                other.adviceAr == adviceAr) &&
            const DeepCollectionEquality().equals(other._warnings, _warnings) &&
            const DeepCollectionEquality()
                .equals(other._warningsAr, _warningsAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        recommendationId,
        timestamp,
        cropType,
        cropNameAr,
        growthStage,
        fieldAreaHectares,
        et0,
        kc,
        etc,
        soilType,
        soilTypeAr,
        estimatedMoisture,
        moistureDepletionPercent,
        irrigationNeeded,
        urgency,
        urgencyAr,
        recommendedAmountMm,
        recommendedAmountLiters,
        recommendedAmountM3,
        grossIrrigationMm,
        optimalTime,
        optimalTimeAr,
        nextIrrigationDays,
        advice,
        adviceAr,
        const DeepCollectionEquality().hash(_warnings),
        const DeepCollectionEquality().hash(_warningsAr)
      ]);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$IrrigationRecommendationImplCopyWith<_$IrrigationRecommendationImpl>
      get copyWith => __$$IrrigationRecommendationImplCopyWithImpl<
          _$IrrigationRecommendationImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IrrigationRecommendationImplToJson(
      this,
    );
  }
}

abstract class _IrrigationRecommendation implements IrrigationRecommendation {
  const factory _IrrigationRecommendation(
      {required final String recommendationId,
      required final DateTime timestamp,
      required final String cropType,
      required final String cropNameAr,
      required final String growthStage,
      required final double fieldAreaHectares,
      required final double et0,
      required final double kc,
      required final double etc,
      required final String soilType,
      required final String soilTypeAr,
      required final double estimatedMoisture,
      required final double moistureDepletionPercent,
      required final bool irrigationNeeded,
      required final UrgencyLevel urgency,
      required final String urgencyAr,
      required final double recommendedAmountMm,
      required final double recommendedAmountLiters,
      required final double recommendedAmountM3,
      required final double grossIrrigationMm,
      required final String optimalTime,
      required final String optimalTimeAr,
      required final int nextIrrigationDays,
      required final String advice,
      required final String adviceAr,
      final List<String> warnings,
      final List<String> warningsAr}) = _$IrrigationRecommendationImpl;

  factory _IrrigationRecommendation.fromJson(Map<String, dynamic> json) =
      _$IrrigationRecommendationImpl.fromJson;

  @override
  String get recommendationId;
  @override
  DateTime get timestamp;
  @override // Field info
  String get cropType;
  @override
  String get cropNameAr;
  @override
  String get growthStage;
  @override
  double get fieldAreaHectares;
  @override // Calculations
  double get et0;
  @override
  double get kc;
  @override
  double get etc;
  @override // Soil status
  String get soilType;
  @override
  String get soilTypeAr;
  @override
  double get estimatedMoisture;
  @override
  double get moistureDepletionPercent;
  @override // Recommendation
  bool get irrigationNeeded;
  @override
  UrgencyLevel get urgency;
  @override
  String get urgencyAr;
  @override
  double get recommendedAmountMm;
  @override
  double get recommendedAmountLiters;
  @override
  double get recommendedAmountM3;
  @override
  double get grossIrrigationMm;
  @override // Timing
  String get optimalTime;
  @override
  String get optimalTimeAr;
  @override
  int get nextIrrigationDays;
  @override // Advice
  String get advice;
  @override
  String get adviceAr;
  @override
  List<String> get warnings;
  @override
  List<String> get warningsAr;
  @override
  @JsonKey(ignore: true)
  _$$IrrigationRecommendationImplCopyWith<_$IrrigationRecommendationImpl>
      get copyWith => throw _privateConstructorUsedError;
}

QuickIrrigationCheck _$QuickIrrigationCheckFromJson(Map<String, dynamic> json) {
  return _QuickIrrigationCheck.fromJson(json);
}

/// @nodoc
mixin _$QuickIrrigationCheck {
  String get cropType => throw _privateConstructorUsedError;
  String get cropNameAr => throw _privateConstructorUsedError;
  String get growthStage => throw _privateConstructorUsedError;
  int get daysSinceIrrigation => throw _privateConstructorUsedError;
  double get estimatedEt0 => throw _privateConstructorUsedError;
  double get kc => throw _privateConstructorUsedError;
  double get estimatedEtc => throw _privateConstructorUsedError;
  double get estimatedWaterLossMm => throw _privateConstructorUsedError;
  double get estimatedDepletionPercent => throw _privateConstructorUsedError;
  String get status => throw _privateConstructorUsedError;
  String get statusAr => throw _privateConstructorUsedError;
  bool get needsIrrigation => throw _privateConstructorUsedError;
  String get recommendation => throw _privateConstructorUsedError;
  String get recommendationAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $QuickIrrigationCheckCopyWith<QuickIrrigationCheck> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $QuickIrrigationCheckCopyWith<$Res> {
  factory $QuickIrrigationCheckCopyWith(QuickIrrigationCheck value,
          $Res Function(QuickIrrigationCheck) then) =
      _$QuickIrrigationCheckCopyWithImpl<$Res, QuickIrrigationCheck>;
  @useResult
  $Res call(
      {String cropType,
      String cropNameAr,
      String growthStage,
      int daysSinceIrrigation,
      double estimatedEt0,
      double kc,
      double estimatedEtc,
      double estimatedWaterLossMm,
      double estimatedDepletionPercent,
      String status,
      String statusAr,
      bool needsIrrigation,
      String recommendation,
      String recommendationAr});
}

/// @nodoc
class _$QuickIrrigationCheckCopyWithImpl<$Res,
        $Val extends QuickIrrigationCheck>
    implements $QuickIrrigationCheckCopyWith<$Res> {
  _$QuickIrrigationCheckCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropType = null,
    Object? cropNameAr = null,
    Object? growthStage = null,
    Object? daysSinceIrrigation = null,
    Object? estimatedEt0 = null,
    Object? kc = null,
    Object? estimatedEtc = null,
    Object? estimatedWaterLossMm = null,
    Object? estimatedDepletionPercent = null,
    Object? status = null,
    Object? statusAr = null,
    Object? needsIrrigation = null,
    Object? recommendation = null,
    Object? recommendationAr = null,
  }) {
    return _then(_value.copyWith(
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      cropNameAr: null == cropNameAr
          ? _value.cropNameAr
          : cropNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      daysSinceIrrigation: null == daysSinceIrrigation
          ? _value.daysSinceIrrigation
          : daysSinceIrrigation // ignore: cast_nullable_to_non_nullable
              as int,
      estimatedEt0: null == estimatedEt0
          ? _value.estimatedEt0
          : estimatedEt0 // ignore: cast_nullable_to_non_nullable
              as double,
      kc: null == kc
          ? _value.kc
          : kc // ignore: cast_nullable_to_non_nullable
              as double,
      estimatedEtc: null == estimatedEtc
          ? _value.estimatedEtc
          : estimatedEtc // ignore: cast_nullable_to_non_nullable
              as double,
      estimatedWaterLossMm: null == estimatedWaterLossMm
          ? _value.estimatedWaterLossMm
          : estimatedWaterLossMm // ignore: cast_nullable_to_non_nullable
              as double,
      estimatedDepletionPercent: null == estimatedDepletionPercent
          ? _value.estimatedDepletionPercent
          : estimatedDepletionPercent // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      statusAr: null == statusAr
          ? _value.statusAr
          : statusAr // ignore: cast_nullable_to_non_nullable
              as String,
      needsIrrigation: null == needsIrrigation
          ? _value.needsIrrigation
          : needsIrrigation // ignore: cast_nullable_to_non_nullable
              as bool,
      recommendation: null == recommendation
          ? _value.recommendation
          : recommendation // ignore: cast_nullable_to_non_nullable
              as String,
      recommendationAr: null == recommendationAr
          ? _value.recommendationAr
          : recommendationAr // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$QuickIrrigationCheckImplCopyWith<$Res>
    implements $QuickIrrigationCheckCopyWith<$Res> {
  factory _$$QuickIrrigationCheckImplCopyWith(_$QuickIrrigationCheckImpl value,
          $Res Function(_$QuickIrrigationCheckImpl) then) =
      __$$QuickIrrigationCheckImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String cropType,
      String cropNameAr,
      String growthStage,
      int daysSinceIrrigation,
      double estimatedEt0,
      double kc,
      double estimatedEtc,
      double estimatedWaterLossMm,
      double estimatedDepletionPercent,
      String status,
      String statusAr,
      bool needsIrrigation,
      String recommendation,
      String recommendationAr});
}

/// @nodoc
class __$$QuickIrrigationCheckImplCopyWithImpl<$Res>
    extends _$QuickIrrigationCheckCopyWithImpl<$Res, _$QuickIrrigationCheckImpl>
    implements _$$QuickIrrigationCheckImplCopyWith<$Res> {
  __$$QuickIrrigationCheckImplCopyWithImpl(_$QuickIrrigationCheckImpl _value,
      $Res Function(_$QuickIrrigationCheckImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? cropType = null,
    Object? cropNameAr = null,
    Object? growthStage = null,
    Object? daysSinceIrrigation = null,
    Object? estimatedEt0 = null,
    Object? kc = null,
    Object? estimatedEtc = null,
    Object? estimatedWaterLossMm = null,
    Object? estimatedDepletionPercent = null,
    Object? status = null,
    Object? statusAr = null,
    Object? needsIrrigation = null,
    Object? recommendation = null,
    Object? recommendationAr = null,
  }) {
    return _then(_$QuickIrrigationCheckImpl(
      cropType: null == cropType
          ? _value.cropType
          : cropType // ignore: cast_nullable_to_non_nullable
              as String,
      cropNameAr: null == cropNameAr
          ? _value.cropNameAr
          : cropNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      growthStage: null == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String,
      daysSinceIrrigation: null == daysSinceIrrigation
          ? _value.daysSinceIrrigation
          : daysSinceIrrigation // ignore: cast_nullable_to_non_nullable
              as int,
      estimatedEt0: null == estimatedEt0
          ? _value.estimatedEt0
          : estimatedEt0 // ignore: cast_nullable_to_non_nullable
              as double,
      kc: null == kc
          ? _value.kc
          : kc // ignore: cast_nullable_to_non_nullable
              as double,
      estimatedEtc: null == estimatedEtc
          ? _value.estimatedEtc
          : estimatedEtc // ignore: cast_nullable_to_non_nullable
              as double,
      estimatedWaterLossMm: null == estimatedWaterLossMm
          ? _value.estimatedWaterLossMm
          : estimatedWaterLossMm // ignore: cast_nullable_to_non_nullable
              as double,
      estimatedDepletionPercent: null == estimatedDepletionPercent
          ? _value.estimatedDepletionPercent
          : estimatedDepletionPercent // ignore: cast_nullable_to_non_nullable
              as double,
      status: null == status
          ? _value.status
          : status // ignore: cast_nullable_to_non_nullable
              as String,
      statusAr: null == statusAr
          ? _value.statusAr
          : statusAr // ignore: cast_nullable_to_non_nullable
              as String,
      needsIrrigation: null == needsIrrigation
          ? _value.needsIrrigation
          : needsIrrigation // ignore: cast_nullable_to_non_nullable
              as bool,
      recommendation: null == recommendation
          ? _value.recommendation
          : recommendation // ignore: cast_nullable_to_non_nullable
              as String,
      recommendationAr: null == recommendationAr
          ? _value.recommendationAr
          : recommendationAr // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$QuickIrrigationCheckImpl implements _QuickIrrigationCheck {
  const _$QuickIrrigationCheckImpl(
      {required this.cropType,
      required this.cropNameAr,
      required this.growthStage,
      required this.daysSinceIrrigation,
      required this.estimatedEt0,
      required this.kc,
      required this.estimatedEtc,
      required this.estimatedWaterLossMm,
      required this.estimatedDepletionPercent,
      required this.status,
      required this.statusAr,
      required this.needsIrrigation,
      required this.recommendation,
      required this.recommendationAr});

  factory _$QuickIrrigationCheckImpl.fromJson(Map<String, dynamic> json) =>
      _$$QuickIrrigationCheckImplFromJson(json);

  @override
  final String cropType;
  @override
  final String cropNameAr;
  @override
  final String growthStage;
  @override
  final int daysSinceIrrigation;
  @override
  final double estimatedEt0;
  @override
  final double kc;
  @override
  final double estimatedEtc;
  @override
  final double estimatedWaterLossMm;
  @override
  final double estimatedDepletionPercent;
  @override
  final String status;
  @override
  final String statusAr;
  @override
  final bool needsIrrigation;
  @override
  final String recommendation;
  @override
  final String recommendationAr;

  @override
  String toString() {
    return 'QuickIrrigationCheck(cropType: $cropType, cropNameAr: $cropNameAr, growthStage: $growthStage, daysSinceIrrigation: $daysSinceIrrigation, estimatedEt0: $estimatedEt0, kc: $kc, estimatedEtc: $estimatedEtc, estimatedWaterLossMm: $estimatedWaterLossMm, estimatedDepletionPercent: $estimatedDepletionPercent, status: $status, statusAr: $statusAr, needsIrrigation: $needsIrrigation, recommendation: $recommendation, recommendationAr: $recommendationAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$QuickIrrigationCheckImpl &&
            (identical(other.cropType, cropType) ||
                other.cropType == cropType) &&
            (identical(other.cropNameAr, cropNameAr) ||
                other.cropNameAr == cropNameAr) &&
            (identical(other.growthStage, growthStage) ||
                other.growthStage == growthStage) &&
            (identical(other.daysSinceIrrigation, daysSinceIrrigation) ||
                other.daysSinceIrrigation == daysSinceIrrigation) &&
            (identical(other.estimatedEt0, estimatedEt0) ||
                other.estimatedEt0 == estimatedEt0) &&
            (identical(other.kc, kc) || other.kc == kc) &&
            (identical(other.estimatedEtc, estimatedEtc) ||
                other.estimatedEtc == estimatedEtc) &&
            (identical(other.estimatedWaterLossMm, estimatedWaterLossMm) ||
                other.estimatedWaterLossMm == estimatedWaterLossMm) &&
            (identical(other.estimatedDepletionPercent,
                    estimatedDepletionPercent) ||
                other.estimatedDepletionPercent == estimatedDepletionPercent) &&
            (identical(other.status, status) || other.status == status) &&
            (identical(other.statusAr, statusAr) ||
                other.statusAr == statusAr) &&
            (identical(other.needsIrrigation, needsIrrigation) ||
                other.needsIrrigation == needsIrrigation) &&
            (identical(other.recommendation, recommendation) ||
                other.recommendation == recommendation) &&
            (identical(other.recommendationAr, recommendationAr) ||
                other.recommendationAr == recommendationAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      cropType,
      cropNameAr,
      growthStage,
      daysSinceIrrigation,
      estimatedEt0,
      kc,
      estimatedEtc,
      estimatedWaterLossMm,
      estimatedDepletionPercent,
      status,
      statusAr,
      needsIrrigation,
      recommendation,
      recommendationAr);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$QuickIrrigationCheckImplCopyWith<_$QuickIrrigationCheckImpl>
      get copyWith =>
          __$$QuickIrrigationCheckImplCopyWithImpl<_$QuickIrrigationCheckImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$QuickIrrigationCheckImplToJson(
      this,
    );
  }
}

abstract class _QuickIrrigationCheck implements QuickIrrigationCheck {
  const factory _QuickIrrigationCheck(
      {required final String cropType,
      required final String cropNameAr,
      required final String growthStage,
      required final int daysSinceIrrigation,
      required final double estimatedEt0,
      required final double kc,
      required final double estimatedEtc,
      required final double estimatedWaterLossMm,
      required final double estimatedDepletionPercent,
      required final String status,
      required final String statusAr,
      required final bool needsIrrigation,
      required final String recommendation,
      required final String recommendationAr}) = _$QuickIrrigationCheckImpl;

  factory _QuickIrrigationCheck.fromJson(Map<String, dynamic> json) =
      _$QuickIrrigationCheckImpl.fromJson;

  @override
  String get cropType;
  @override
  String get cropNameAr;
  @override
  String get growthStage;
  @override
  int get daysSinceIrrigation;
  @override
  double get estimatedEt0;
  @override
  double get kc;
  @override
  double get estimatedEtc;
  @override
  double get estimatedWaterLossMm;
  @override
  double get estimatedDepletionPercent;
  @override
  String get status;
  @override
  String get statusAr;
  @override
  bool get needsIrrigation;
  @override
  String get recommendation;
  @override
  String get recommendationAr;
  @override
  @JsonKey(ignore: true)
  _$$QuickIrrigationCheckImplCopyWith<_$QuickIrrigationCheckImpl>
      get copyWith => throw _privateConstructorUsedError;
}

SoilTypeInfo _$SoilTypeInfoFromJson(Map<String, dynamic> json) {
  return _SoilTypeInfo.fromJson(json);
}

/// @nodoc
mixin _$SoilTypeInfo {
  String get soilType => throw _privateConstructorUsedError;
  String get nameAr => throw _privateConstructorUsedError;
  double get fieldCapacity => throw _privateConstructorUsedError;
  double get wiltingPoint => throw _privateConstructorUsedError;
  double get availableWaterCapacity => throw _privateConstructorUsedError;
  double get infiltrationRateMmHr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $SoilTypeInfoCopyWith<SoilTypeInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $SoilTypeInfoCopyWith<$Res> {
  factory $SoilTypeInfoCopyWith(
          SoilTypeInfo value, $Res Function(SoilTypeInfo) then) =
      _$SoilTypeInfoCopyWithImpl<$Res, SoilTypeInfo>;
  @useResult
  $Res call(
      {String soilType,
      String nameAr,
      double fieldCapacity,
      double wiltingPoint,
      double availableWaterCapacity,
      double infiltrationRateMmHr});
}

/// @nodoc
class _$SoilTypeInfoCopyWithImpl<$Res, $Val extends SoilTypeInfo>
    implements $SoilTypeInfoCopyWith<$Res> {
  _$SoilTypeInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? soilType = null,
    Object? nameAr = null,
    Object? fieldCapacity = null,
    Object? wiltingPoint = null,
    Object? availableWaterCapacity = null,
    Object? infiltrationRateMmHr = null,
  }) {
    return _then(_value.copyWith(
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      fieldCapacity: null == fieldCapacity
          ? _value.fieldCapacity
          : fieldCapacity // ignore: cast_nullable_to_non_nullable
              as double,
      wiltingPoint: null == wiltingPoint
          ? _value.wiltingPoint
          : wiltingPoint // ignore: cast_nullable_to_non_nullable
              as double,
      availableWaterCapacity: null == availableWaterCapacity
          ? _value.availableWaterCapacity
          : availableWaterCapacity // ignore: cast_nullable_to_non_nullable
              as double,
      infiltrationRateMmHr: null == infiltrationRateMmHr
          ? _value.infiltrationRateMmHr
          : infiltrationRateMmHr // ignore: cast_nullable_to_non_nullable
              as double,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$SoilTypeInfoImplCopyWith<$Res>
    implements $SoilTypeInfoCopyWith<$Res> {
  factory _$$SoilTypeInfoImplCopyWith(
          _$SoilTypeInfoImpl value, $Res Function(_$SoilTypeInfoImpl) then) =
      __$$SoilTypeInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String soilType,
      String nameAr,
      double fieldCapacity,
      double wiltingPoint,
      double availableWaterCapacity,
      double infiltrationRateMmHr});
}

/// @nodoc
class __$$SoilTypeInfoImplCopyWithImpl<$Res>
    extends _$SoilTypeInfoCopyWithImpl<$Res, _$SoilTypeInfoImpl>
    implements _$$SoilTypeInfoImplCopyWith<$Res> {
  __$$SoilTypeInfoImplCopyWithImpl(
      _$SoilTypeInfoImpl _value, $Res Function(_$SoilTypeInfoImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? soilType = null,
    Object? nameAr = null,
    Object? fieldCapacity = null,
    Object? wiltingPoint = null,
    Object? availableWaterCapacity = null,
    Object? infiltrationRateMmHr = null,
  }) {
    return _then(_$SoilTypeInfoImpl(
      soilType: null == soilType
          ? _value.soilType
          : soilType // ignore: cast_nullable_to_non_nullable
              as String,
      nameAr: null == nameAr
          ? _value.nameAr
          : nameAr // ignore: cast_nullable_to_non_nullable
              as String,
      fieldCapacity: null == fieldCapacity
          ? _value.fieldCapacity
          : fieldCapacity // ignore: cast_nullable_to_non_nullable
              as double,
      wiltingPoint: null == wiltingPoint
          ? _value.wiltingPoint
          : wiltingPoint // ignore: cast_nullable_to_non_nullable
              as double,
      availableWaterCapacity: null == availableWaterCapacity
          ? _value.availableWaterCapacity
          : availableWaterCapacity // ignore: cast_nullable_to_non_nullable
              as double,
      infiltrationRateMmHr: null == infiltrationRateMmHr
          ? _value.infiltrationRateMmHr
          : infiltrationRateMmHr // ignore: cast_nullable_to_non_nullable
              as double,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$SoilTypeInfoImpl implements _SoilTypeInfo {
  const _$SoilTypeInfoImpl(
      {required this.soilType,
      required this.nameAr,
      required this.fieldCapacity,
      required this.wiltingPoint,
      required this.availableWaterCapacity,
      required this.infiltrationRateMmHr});

  factory _$SoilTypeInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$SoilTypeInfoImplFromJson(json);

  @override
  final String soilType;
  @override
  final String nameAr;
  @override
  final double fieldCapacity;
  @override
  final double wiltingPoint;
  @override
  final double availableWaterCapacity;
  @override
  final double infiltrationRateMmHr;

  @override
  String toString() {
    return 'SoilTypeInfo(soilType: $soilType, nameAr: $nameAr, fieldCapacity: $fieldCapacity, wiltingPoint: $wiltingPoint, availableWaterCapacity: $availableWaterCapacity, infiltrationRateMmHr: $infiltrationRateMmHr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$SoilTypeInfoImpl &&
            (identical(other.soilType, soilType) ||
                other.soilType == soilType) &&
            (identical(other.nameAr, nameAr) || other.nameAr == nameAr) &&
            (identical(other.fieldCapacity, fieldCapacity) ||
                other.fieldCapacity == fieldCapacity) &&
            (identical(other.wiltingPoint, wiltingPoint) ||
                other.wiltingPoint == wiltingPoint) &&
            (identical(other.availableWaterCapacity, availableWaterCapacity) ||
                other.availableWaterCapacity == availableWaterCapacity) &&
            (identical(other.infiltrationRateMmHr, infiltrationRateMmHr) ||
                other.infiltrationRateMmHr == infiltrationRateMmHr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(runtimeType, soilType, nameAr, fieldCapacity,
      wiltingPoint, availableWaterCapacity, infiltrationRateMmHr);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$SoilTypeInfoImplCopyWith<_$SoilTypeInfoImpl> get copyWith =>
      __$$SoilTypeInfoImplCopyWithImpl<_$SoilTypeInfoImpl>(this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$SoilTypeInfoImplToJson(
      this,
    );
  }
}

abstract class _SoilTypeInfo implements SoilTypeInfo {
  const factory _SoilTypeInfo(
      {required final String soilType,
      required final String nameAr,
      required final double fieldCapacity,
      required final double wiltingPoint,
      required final double availableWaterCapacity,
      required final double infiltrationRateMmHr}) = _$SoilTypeInfoImpl;

  factory _SoilTypeInfo.fromJson(Map<String, dynamic> json) =
      _$SoilTypeInfoImpl.fromJson;

  @override
  String get soilType;
  @override
  String get nameAr;
  @override
  double get fieldCapacity;
  @override
  double get wiltingPoint;
  @override
  double get availableWaterCapacity;
  @override
  double get infiltrationRateMmHr;
  @override
  @JsonKey(ignore: true)
  _$$SoilTypeInfoImplCopyWith<_$SoilTypeInfoImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

IrrigationMethodInfo _$IrrigationMethodInfoFromJson(Map<String, dynamic> json) {
  return _IrrigationMethodInfo.fromJson(json);
}

/// @nodoc
mixin _$IrrigationMethodInfo {
  String get method => throw _privateConstructorUsedError;
  double get efficiency => throw _privateConstructorUsedError;
  String get efficiencyPercent => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $IrrigationMethodInfoCopyWith<IrrigationMethodInfo> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $IrrigationMethodInfoCopyWith<$Res> {
  factory $IrrigationMethodInfoCopyWith(IrrigationMethodInfo value,
          $Res Function(IrrigationMethodInfo) then) =
      _$IrrigationMethodInfoCopyWithImpl<$Res, IrrigationMethodInfo>;
  @useResult
  $Res call({String method, double efficiency, String efficiencyPercent});
}

/// @nodoc
class _$IrrigationMethodInfoCopyWithImpl<$Res,
        $Val extends IrrigationMethodInfo>
    implements $IrrigationMethodInfoCopyWith<$Res> {
  _$IrrigationMethodInfoCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? method = null,
    Object? efficiency = null,
    Object? efficiencyPercent = null,
  }) {
    return _then(_value.copyWith(
      method: null == method
          ? _value.method
          : method // ignore: cast_nullable_to_non_nullable
              as String,
      efficiency: null == efficiency
          ? _value.efficiency
          : efficiency // ignore: cast_nullable_to_non_nullable
              as double,
      efficiencyPercent: null == efficiencyPercent
          ? _value.efficiencyPercent
          : efficiencyPercent // ignore: cast_nullable_to_non_nullable
              as String,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$IrrigationMethodInfoImplCopyWith<$Res>
    implements $IrrigationMethodInfoCopyWith<$Res> {
  factory _$$IrrigationMethodInfoImplCopyWith(_$IrrigationMethodInfoImpl value,
          $Res Function(_$IrrigationMethodInfoImpl) then) =
      __$$IrrigationMethodInfoImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call({String method, double efficiency, String efficiencyPercent});
}

/// @nodoc
class __$$IrrigationMethodInfoImplCopyWithImpl<$Res>
    extends _$IrrigationMethodInfoCopyWithImpl<$Res, _$IrrigationMethodInfoImpl>
    implements _$$IrrigationMethodInfoImplCopyWith<$Res> {
  __$$IrrigationMethodInfoImplCopyWithImpl(_$IrrigationMethodInfoImpl _value,
      $Res Function(_$IrrigationMethodInfoImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? method = null,
    Object? efficiency = null,
    Object? efficiencyPercent = null,
  }) {
    return _then(_$IrrigationMethodInfoImpl(
      method: null == method
          ? _value.method
          : method // ignore: cast_nullable_to_non_nullable
              as String,
      efficiency: null == efficiency
          ? _value.efficiency
          : efficiency // ignore: cast_nullable_to_non_nullable
              as double,
      efficiencyPercent: null == efficiencyPercent
          ? _value.efficiencyPercent
          : efficiencyPercent // ignore: cast_nullable_to_non_nullable
              as String,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$IrrigationMethodInfoImpl implements _IrrigationMethodInfo {
  const _$IrrigationMethodInfoImpl(
      {required this.method,
      required this.efficiency,
      required this.efficiencyPercent});

  factory _$IrrigationMethodInfoImpl.fromJson(Map<String, dynamic> json) =>
      _$$IrrigationMethodInfoImplFromJson(json);

  @override
  final String method;
  @override
  final double efficiency;
  @override
  final String efficiencyPercent;

  @override
  String toString() {
    return 'IrrigationMethodInfo(method: $method, efficiency: $efficiency, efficiencyPercent: $efficiencyPercent)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$IrrigationMethodInfoImpl &&
            (identical(other.method, method) || other.method == method) &&
            (identical(other.efficiency, efficiency) ||
                other.efficiency == efficiency) &&
            (identical(other.efficiencyPercent, efficiencyPercent) ||
                other.efficiencyPercent == efficiencyPercent));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode =>
      Object.hash(runtimeType, method, efficiency, efficiencyPercent);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$IrrigationMethodInfoImplCopyWith<_$IrrigationMethodInfoImpl>
      get copyWith =>
          __$$IrrigationMethodInfoImplCopyWithImpl<_$IrrigationMethodInfoImpl>(
              this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$IrrigationMethodInfoImplToJson(
      this,
    );
  }
}

abstract class _IrrigationMethodInfo implements IrrigationMethodInfo {
  const factory _IrrigationMethodInfo(
      {required final String method,
      required final double efficiency,
      required final String efficiencyPercent}) = _$IrrigationMethodInfoImpl;

  factory _IrrigationMethodInfo.fromJson(Map<String, dynamic> json) =
      _$IrrigationMethodInfoImpl.fromJson;

  @override
  String get method;
  @override
  double get efficiency;
  @override
  String get efficiencyPercent;
  @override
  @JsonKey(ignore: true)
  _$$IrrigationMethodInfoImplCopyWith<_$IrrigationMethodInfoImpl>
      get copyWith => throw _privateConstructorUsedError;
}
