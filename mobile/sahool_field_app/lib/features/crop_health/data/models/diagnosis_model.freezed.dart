// coverage:ignore-file
// GENERATED CODE - DO NOT MODIFY BY HAND
// ignore_for_file: type=lint
// ignore_for_file: unused_element, deprecated_member_use, deprecated_member_use_from_same_package, use_function_type_syntax_for_parameters, unnecessary_const, avoid_init_to_null, invalid_override_different_default_values_named, prefer_expression_function_bodies, annotate_overrides, invalid_annotation_target, unnecessary_question_mark

part of 'diagnosis_model.dart';

// **************************************************************************
// FreezedGenerator
// **************************************************************************

T _$identity<T>(T value) => value;

final _privateConstructorUsedError = UnsupportedError(
    'It seems like you constructed your class using `MyClass._()`. This constructor is only meant to be used by freezed and you are not supposed to need it nor use it.\nPlease check the documentation here for more information: https://github.com/rrousselGit/freezed#adding-getters-and-methods-to-our-models');

TreatmentModel _$TreatmentModelFromJson(Map<String, dynamic> json) {
  return _TreatmentModel.fromJson(json);
}

/// @nodoc
mixin _$TreatmentModel {
  @JsonKey(name: 'treatment_type')
  String get treatmentType => throw _privateConstructorUsedError;
  @JsonKey(name: 'product_name')
  String get productName => throw _privateConstructorUsedError;
  @JsonKey(name: 'product_name_ar')
  String get productNameAr => throw _privateConstructorUsedError;
  String get dosage => throw _privateConstructorUsedError;
  @JsonKey(name: 'dosage_ar')
  String get dosageAr => throw _privateConstructorUsedError;
  @JsonKey(name: 'application_method')
  String get applicationMethod => throw _privateConstructorUsedError;
  @JsonKey(name: 'application_method_ar')
  String get applicationMethodAr => throw _privateConstructorUsedError;
  String get frequency => throw _privateConstructorUsedError;
  @JsonKey(name: 'frequency_ar')
  String get frequencyAr => throw _privateConstructorUsedError;
  List<String> get precautions => throw _privateConstructorUsedError;
  @JsonKey(name: 'precautions_ar')
  List<String> get precautionsAr => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $TreatmentModelCopyWith<TreatmentModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $TreatmentModelCopyWith<$Res> {
  factory $TreatmentModelCopyWith(
          TreatmentModel value, $Res Function(TreatmentModel) then) =
      _$TreatmentModelCopyWithImpl<$Res, TreatmentModel>;
  @useResult
  $Res call(
      {@JsonKey(name: 'treatment_type') String treatmentType,
      @JsonKey(name: 'product_name') String productName,
      @JsonKey(name: 'product_name_ar') String productNameAr,
      String dosage,
      @JsonKey(name: 'dosage_ar') String dosageAr,
      @JsonKey(name: 'application_method') String applicationMethod,
      @JsonKey(name: 'application_method_ar') String applicationMethodAr,
      String frequency,
      @JsonKey(name: 'frequency_ar') String frequencyAr,
      List<String> precautions,
      @JsonKey(name: 'precautions_ar') List<String> precautionsAr});
}

/// @nodoc
class _$TreatmentModelCopyWithImpl<$Res, $Val extends TreatmentModel>
    implements $TreatmentModelCopyWith<$Res> {
  _$TreatmentModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? treatmentType = null,
    Object? productName = null,
    Object? productNameAr = null,
    Object? dosage = null,
    Object? dosageAr = null,
    Object? applicationMethod = null,
    Object? applicationMethodAr = null,
    Object? frequency = null,
    Object? frequencyAr = null,
    Object? precautions = null,
    Object? precautionsAr = null,
  }) {
    return _then(_value.copyWith(
      treatmentType: null == treatmentType
          ? _value.treatmentType
          : treatmentType // ignore: cast_nullable_to_non_nullable
              as String,
      productName: null == productName
          ? _value.productName
          : productName // ignore: cast_nullable_to_non_nullable
              as String,
      productNameAr: null == productNameAr
          ? _value.productNameAr
          : productNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      dosage: null == dosage
          ? _value.dosage
          : dosage // ignore: cast_nullable_to_non_nullable
              as String,
      dosageAr: null == dosageAr
          ? _value.dosageAr
          : dosageAr // ignore: cast_nullable_to_non_nullable
              as String,
      applicationMethod: null == applicationMethod
          ? _value.applicationMethod
          : applicationMethod // ignore: cast_nullable_to_non_nullable
              as String,
      applicationMethodAr: null == applicationMethodAr
          ? _value.applicationMethodAr
          : applicationMethodAr // ignore: cast_nullable_to_non_nullable
              as String,
      frequency: null == frequency
          ? _value.frequency
          : frequency // ignore: cast_nullable_to_non_nullable
              as String,
      frequencyAr: null == frequencyAr
          ? _value.frequencyAr
          : frequencyAr // ignore: cast_nullable_to_non_nullable
              as String,
      precautions: null == precautions
          ? _value.precautions
          : precautions // ignore: cast_nullable_to_non_nullable
              as List<String>,
      precautionsAr: null == precautionsAr
          ? _value.precautionsAr
          : precautionsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$TreatmentModelImplCopyWith<$Res>
    implements $TreatmentModelCopyWith<$Res> {
  factory _$$TreatmentModelImplCopyWith(_$TreatmentModelImpl value,
          $Res Function(_$TreatmentModelImpl) then) =
      __$$TreatmentModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'treatment_type') String treatmentType,
      @JsonKey(name: 'product_name') String productName,
      @JsonKey(name: 'product_name_ar') String productNameAr,
      String dosage,
      @JsonKey(name: 'dosage_ar') String dosageAr,
      @JsonKey(name: 'application_method') String applicationMethod,
      @JsonKey(name: 'application_method_ar') String applicationMethodAr,
      String frequency,
      @JsonKey(name: 'frequency_ar') String frequencyAr,
      List<String> precautions,
      @JsonKey(name: 'precautions_ar') List<String> precautionsAr});
}

/// @nodoc
class __$$TreatmentModelImplCopyWithImpl<$Res>
    extends _$TreatmentModelCopyWithImpl<$Res, _$TreatmentModelImpl>
    implements _$$TreatmentModelImplCopyWith<$Res> {
  __$$TreatmentModelImplCopyWithImpl(
      _$TreatmentModelImpl _value, $Res Function(_$TreatmentModelImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? treatmentType = null,
    Object? productName = null,
    Object? productNameAr = null,
    Object? dosage = null,
    Object? dosageAr = null,
    Object? applicationMethod = null,
    Object? applicationMethodAr = null,
    Object? frequency = null,
    Object? frequencyAr = null,
    Object? precautions = null,
    Object? precautionsAr = null,
  }) {
    return _then(_$TreatmentModelImpl(
      treatmentType: null == treatmentType
          ? _value.treatmentType
          : treatmentType // ignore: cast_nullable_to_non_nullable
              as String,
      productName: null == productName
          ? _value.productName
          : productName // ignore: cast_nullable_to_non_nullable
              as String,
      productNameAr: null == productNameAr
          ? _value.productNameAr
          : productNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      dosage: null == dosage
          ? _value.dosage
          : dosage // ignore: cast_nullable_to_non_nullable
              as String,
      dosageAr: null == dosageAr
          ? _value.dosageAr
          : dosageAr // ignore: cast_nullable_to_non_nullable
              as String,
      applicationMethod: null == applicationMethod
          ? _value.applicationMethod
          : applicationMethod // ignore: cast_nullable_to_non_nullable
              as String,
      applicationMethodAr: null == applicationMethodAr
          ? _value.applicationMethodAr
          : applicationMethodAr // ignore: cast_nullable_to_non_nullable
              as String,
      frequency: null == frequency
          ? _value.frequency
          : frequency // ignore: cast_nullable_to_non_nullable
              as String,
      frequencyAr: null == frequencyAr
          ? _value.frequencyAr
          : frequencyAr // ignore: cast_nullable_to_non_nullable
              as String,
      precautions: null == precautions
          ? _value._precautions
          : precautions // ignore: cast_nullable_to_non_nullable
              as List<String>,
      precautionsAr: null == precautionsAr
          ? _value._precautionsAr
          : precautionsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$TreatmentModelImpl implements _TreatmentModel {
  const _$TreatmentModelImpl(
      {@JsonKey(name: 'treatment_type') required this.treatmentType,
      @JsonKey(name: 'product_name') required this.productName,
      @JsonKey(name: 'product_name_ar') required this.productNameAr,
      required this.dosage,
      @JsonKey(name: 'dosage_ar') required this.dosageAr,
      @JsonKey(name: 'application_method') required this.applicationMethod,
      @JsonKey(name: 'application_method_ar') required this.applicationMethodAr,
      required this.frequency,
      @JsonKey(name: 'frequency_ar') required this.frequencyAr,
      final List<String> precautions = const [],
      @JsonKey(name: 'precautions_ar')
      final List<String> precautionsAr = const []})
      : _precautions = precautions,
        _precautionsAr = precautionsAr;

  factory _$TreatmentModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$TreatmentModelImplFromJson(json);

  @override
  @JsonKey(name: 'treatment_type')
  final String treatmentType;
  @override
  @JsonKey(name: 'product_name')
  final String productName;
  @override
  @JsonKey(name: 'product_name_ar')
  final String productNameAr;
  @override
  final String dosage;
  @override
  @JsonKey(name: 'dosage_ar')
  final String dosageAr;
  @override
  @JsonKey(name: 'application_method')
  final String applicationMethod;
  @override
  @JsonKey(name: 'application_method_ar')
  final String applicationMethodAr;
  @override
  final String frequency;
  @override
  @JsonKey(name: 'frequency_ar')
  final String frequencyAr;
  final List<String> _precautions;
  @override
  @JsonKey()
  List<String> get precautions {
    if (_precautions is EqualUnmodifiableListView) return _precautions;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_precautions);
  }

  final List<String> _precautionsAr;
  @override
  @JsonKey(name: 'precautions_ar')
  List<String> get precautionsAr {
    if (_precautionsAr is EqualUnmodifiableListView) return _precautionsAr;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_precautionsAr);
  }

  @override
  String toString() {
    return 'TreatmentModel(treatmentType: $treatmentType, productName: $productName, productNameAr: $productNameAr, dosage: $dosage, dosageAr: $dosageAr, applicationMethod: $applicationMethod, applicationMethodAr: $applicationMethodAr, frequency: $frequency, frequencyAr: $frequencyAr, precautions: $precautions, precautionsAr: $precautionsAr)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$TreatmentModelImpl &&
            (identical(other.treatmentType, treatmentType) ||
                other.treatmentType == treatmentType) &&
            (identical(other.productName, productName) ||
                other.productName == productName) &&
            (identical(other.productNameAr, productNameAr) ||
                other.productNameAr == productNameAr) &&
            (identical(other.dosage, dosage) || other.dosage == dosage) &&
            (identical(other.dosageAr, dosageAr) ||
                other.dosageAr == dosageAr) &&
            (identical(other.applicationMethod, applicationMethod) ||
                other.applicationMethod == applicationMethod) &&
            (identical(other.applicationMethodAr, applicationMethodAr) ||
                other.applicationMethodAr == applicationMethodAr) &&
            (identical(other.frequency, frequency) ||
                other.frequency == frequency) &&
            (identical(other.frequencyAr, frequencyAr) ||
                other.frequencyAr == frequencyAr) &&
            const DeepCollectionEquality()
                .equals(other._precautions, _precautions) &&
            const DeepCollectionEquality()
                .equals(other._precautionsAr, _precautionsAr));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hash(
      runtimeType,
      treatmentType,
      productName,
      productNameAr,
      dosage,
      dosageAr,
      applicationMethod,
      applicationMethodAr,
      frequency,
      frequencyAr,
      const DeepCollectionEquality().hash(_precautions),
      const DeepCollectionEquality().hash(_precautionsAr));

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$TreatmentModelImplCopyWith<_$TreatmentModelImpl> get copyWith =>
      __$$TreatmentModelImplCopyWithImpl<_$TreatmentModelImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$TreatmentModelImplToJson(
      this,
    );
  }
}

abstract class _TreatmentModel implements TreatmentModel {
  const factory _TreatmentModel(
          {@JsonKey(name: 'treatment_type') required final String treatmentType,
          @JsonKey(name: 'product_name') required final String productName,
          @JsonKey(name: 'product_name_ar') required final String productNameAr,
          required final String dosage,
          @JsonKey(name: 'dosage_ar') required final String dosageAr,
          @JsonKey(name: 'application_method')
          required final String applicationMethod,
          @JsonKey(name: 'application_method_ar')
          required final String applicationMethodAr,
          required final String frequency,
          @JsonKey(name: 'frequency_ar') required final String frequencyAr,
          final List<String> precautions,
          @JsonKey(name: 'precautions_ar') final List<String> precautionsAr}) =
      _$TreatmentModelImpl;

  factory _TreatmentModel.fromJson(Map<String, dynamic> json) =
      _$TreatmentModelImpl.fromJson;

  @override
  @JsonKey(name: 'treatment_type')
  String get treatmentType;
  @override
  @JsonKey(name: 'product_name')
  String get productName;
  @override
  @JsonKey(name: 'product_name_ar')
  String get productNameAr;
  @override
  String get dosage;
  @override
  @JsonKey(name: 'dosage_ar')
  String get dosageAr;
  @override
  @JsonKey(name: 'application_method')
  String get applicationMethod;
  @override
  @JsonKey(name: 'application_method_ar')
  String get applicationMethodAr;
  @override
  String get frequency;
  @override
  @JsonKey(name: 'frequency_ar')
  String get frequencyAr;
  @override
  List<String> get precautions;
  @override
  @JsonKey(name: 'precautions_ar')
  List<String> get precautionsAr;
  @override
  @JsonKey(ignore: true)
  _$$TreatmentModelImplCopyWith<_$TreatmentModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

DiagnosisModel _$DiagnosisModelFromJson(Map<String, dynamic> json) {
  return _DiagnosisModel.fromJson(json);
}

/// @nodoc
mixin _$DiagnosisModel {
  @JsonKey(name: 'diagnosis_id')
  String get diagnosisId => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError; // معلومات المرض
  @JsonKey(name: 'disease_name')
  String get diseaseName => throw _privateConstructorUsedError;
  @JsonKey(name: 'disease_name_ar')
  String get diseaseNameAr => throw _privateConstructorUsedError;
  @JsonKey(name: 'disease_description')
  String? get diseaseDescription => throw _privateConstructorUsedError;
  @JsonKey(name: 'disease_description_ar')
  String? get diseaseDescriptionAr =>
      throw _privateConstructorUsedError; // الثقة والشدة
  double get confidence => throw _privateConstructorUsedError;
  DiseaseSeverity get severity => throw _privateConstructorUsedError;
  @JsonKey(name: 'affected_area_percent')
  double get affectedAreaPercent =>
      throw _privateConstructorUsedError; // المحصول
  @JsonKey(name: 'detected_crop')
  String? get detectedCrop => throw _privateConstructorUsedError;
  @JsonKey(name: 'growth_stage')
  String? get growthStage => throw _privateConstructorUsedError; // العلاج
  List<TreatmentModel> get treatments => throw _privateConstructorUsedError;
  @JsonKey(name: 'urgent_action_required')
  bool get urgentActionRequired =>
      throw _privateConstructorUsedError; // مراجعة الخبير
  @JsonKey(name: 'needs_expert_review')
  bool get needsExpertReview => throw _privateConstructorUsedError;
  @JsonKey(name: 'expert_review_reason')
  String? get expertReviewReason =>
      throw _privateConstructorUsedError; // نصائح إضافية
  @JsonKey(name: 'weather_consideration')
  String? get weatherConsideration => throw _privateConstructorUsedError;
  @JsonKey(name: 'prevention_tips')
  List<String> get preventionTips => throw _privateConstructorUsedError;
  @JsonKey(name: 'prevention_tips_ar')
  List<String> get preventionTipsAr =>
      throw _privateConstructorUsedError; // الصورة المحفوظة
  @JsonKey(name: 'image_url')
  String? get imageUrl => throw _privateConstructorUsedError;

  Map<String, dynamic> toJson() => throw _privateConstructorUsedError;
  @JsonKey(ignore: true)
  $DiagnosisModelCopyWith<DiagnosisModel> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DiagnosisModelCopyWith<$Res> {
  factory $DiagnosisModelCopyWith(
          DiagnosisModel value, $Res Function(DiagnosisModel) then) =
      _$DiagnosisModelCopyWithImpl<$Res, DiagnosisModel>;
  @useResult
  $Res call(
      {@JsonKey(name: 'diagnosis_id') String diagnosisId,
      DateTime timestamp,
      @JsonKey(name: 'disease_name') String diseaseName,
      @JsonKey(name: 'disease_name_ar') String diseaseNameAr,
      @JsonKey(name: 'disease_description') String? diseaseDescription,
      @JsonKey(name: 'disease_description_ar') String? diseaseDescriptionAr,
      double confidence,
      DiseaseSeverity severity,
      @JsonKey(name: 'affected_area_percent') double affectedAreaPercent,
      @JsonKey(name: 'detected_crop') String? detectedCrop,
      @JsonKey(name: 'growth_stage') String? growthStage,
      List<TreatmentModel> treatments,
      @JsonKey(name: 'urgent_action_required') bool urgentActionRequired,
      @JsonKey(name: 'needs_expert_review') bool needsExpertReview,
      @JsonKey(name: 'expert_review_reason') String? expertReviewReason,
      @JsonKey(name: 'weather_consideration') String? weatherConsideration,
      @JsonKey(name: 'prevention_tips') List<String> preventionTips,
      @JsonKey(name: 'prevention_tips_ar') List<String> preventionTipsAr,
      @JsonKey(name: 'image_url') String? imageUrl});
}

/// @nodoc
class _$DiagnosisModelCopyWithImpl<$Res, $Val extends DiagnosisModel>
    implements $DiagnosisModelCopyWith<$Res> {
  _$DiagnosisModelCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? diagnosisId = null,
    Object? timestamp = null,
    Object? diseaseName = null,
    Object? diseaseNameAr = null,
    Object? diseaseDescription = freezed,
    Object? diseaseDescriptionAr = freezed,
    Object? confidence = null,
    Object? severity = null,
    Object? affectedAreaPercent = null,
    Object? detectedCrop = freezed,
    Object? growthStage = freezed,
    Object? treatments = null,
    Object? urgentActionRequired = null,
    Object? needsExpertReview = null,
    Object? expertReviewReason = freezed,
    Object? weatherConsideration = freezed,
    Object? preventionTips = null,
    Object? preventionTipsAr = null,
    Object? imageUrl = freezed,
  }) {
    return _then(_value.copyWith(
      diagnosisId: null == diagnosisId
          ? _value.diagnosisId
          : diagnosisId // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      diseaseName: null == diseaseName
          ? _value.diseaseName
          : diseaseName // ignore: cast_nullable_to_non_nullable
              as String,
      diseaseNameAr: null == diseaseNameAr
          ? _value.diseaseNameAr
          : diseaseNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      diseaseDescription: freezed == diseaseDescription
          ? _value.diseaseDescription
          : diseaseDescription // ignore: cast_nullable_to_non_nullable
              as String?,
      diseaseDescriptionAr: freezed == diseaseDescriptionAr
          ? _value.diseaseDescriptionAr
          : diseaseDescriptionAr // ignore: cast_nullable_to_non_nullable
              as String?,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as DiseaseSeverity,
      affectedAreaPercent: null == affectedAreaPercent
          ? _value.affectedAreaPercent
          : affectedAreaPercent // ignore: cast_nullable_to_non_nullable
              as double,
      detectedCrop: freezed == detectedCrop
          ? _value.detectedCrop
          : detectedCrop // ignore: cast_nullable_to_non_nullable
              as String?,
      growthStage: freezed == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String?,
      treatments: null == treatments
          ? _value.treatments
          : treatments // ignore: cast_nullable_to_non_nullable
              as List<TreatmentModel>,
      urgentActionRequired: null == urgentActionRequired
          ? _value.urgentActionRequired
          : urgentActionRequired // ignore: cast_nullable_to_non_nullable
              as bool,
      needsExpertReview: null == needsExpertReview
          ? _value.needsExpertReview
          : needsExpertReview // ignore: cast_nullable_to_non_nullable
              as bool,
      expertReviewReason: freezed == expertReviewReason
          ? _value.expertReviewReason
          : expertReviewReason // ignore: cast_nullable_to_non_nullable
              as String?,
      weatherConsideration: freezed == weatherConsideration
          ? _value.weatherConsideration
          : weatherConsideration // ignore: cast_nullable_to_non_nullable
              as String?,
      preventionTips: null == preventionTips
          ? _value.preventionTips
          : preventionTips // ignore: cast_nullable_to_non_nullable
              as List<String>,
      preventionTipsAr: null == preventionTipsAr
          ? _value.preventionTipsAr
          : preventionTipsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      imageUrl: freezed == imageUrl
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DiagnosisModelImplCopyWith<$Res>
    implements $DiagnosisModelCopyWith<$Res> {
  factory _$$DiagnosisModelImplCopyWith(_$DiagnosisModelImpl value,
          $Res Function(_$DiagnosisModelImpl) then) =
      __$$DiagnosisModelImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {@JsonKey(name: 'diagnosis_id') String diagnosisId,
      DateTime timestamp,
      @JsonKey(name: 'disease_name') String diseaseName,
      @JsonKey(name: 'disease_name_ar') String diseaseNameAr,
      @JsonKey(name: 'disease_description') String? diseaseDescription,
      @JsonKey(name: 'disease_description_ar') String? diseaseDescriptionAr,
      double confidence,
      DiseaseSeverity severity,
      @JsonKey(name: 'affected_area_percent') double affectedAreaPercent,
      @JsonKey(name: 'detected_crop') String? detectedCrop,
      @JsonKey(name: 'growth_stage') String? growthStage,
      List<TreatmentModel> treatments,
      @JsonKey(name: 'urgent_action_required') bool urgentActionRequired,
      @JsonKey(name: 'needs_expert_review') bool needsExpertReview,
      @JsonKey(name: 'expert_review_reason') String? expertReviewReason,
      @JsonKey(name: 'weather_consideration') String? weatherConsideration,
      @JsonKey(name: 'prevention_tips') List<String> preventionTips,
      @JsonKey(name: 'prevention_tips_ar') List<String> preventionTipsAr,
      @JsonKey(name: 'image_url') String? imageUrl});
}

/// @nodoc
class __$$DiagnosisModelImplCopyWithImpl<$Res>
    extends _$DiagnosisModelCopyWithImpl<$Res, _$DiagnosisModelImpl>
    implements _$$DiagnosisModelImplCopyWith<$Res> {
  __$$DiagnosisModelImplCopyWithImpl(
      _$DiagnosisModelImpl _value, $Res Function(_$DiagnosisModelImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? diagnosisId = null,
    Object? timestamp = null,
    Object? diseaseName = null,
    Object? diseaseNameAr = null,
    Object? diseaseDescription = freezed,
    Object? diseaseDescriptionAr = freezed,
    Object? confidence = null,
    Object? severity = null,
    Object? affectedAreaPercent = null,
    Object? detectedCrop = freezed,
    Object? growthStage = freezed,
    Object? treatments = null,
    Object? urgentActionRequired = null,
    Object? needsExpertReview = null,
    Object? expertReviewReason = freezed,
    Object? weatherConsideration = freezed,
    Object? preventionTips = null,
    Object? preventionTipsAr = null,
    Object? imageUrl = freezed,
  }) {
    return _then(_$DiagnosisModelImpl(
      diagnosisId: null == diagnosisId
          ? _value.diagnosisId
          : diagnosisId // ignore: cast_nullable_to_non_nullable
              as String,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      diseaseName: null == diseaseName
          ? _value.diseaseName
          : diseaseName // ignore: cast_nullable_to_non_nullable
              as String,
      diseaseNameAr: null == diseaseNameAr
          ? _value.diseaseNameAr
          : diseaseNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      diseaseDescription: freezed == diseaseDescription
          ? _value.diseaseDescription
          : diseaseDescription // ignore: cast_nullable_to_non_nullable
              as String?,
      diseaseDescriptionAr: freezed == diseaseDescriptionAr
          ? _value.diseaseDescriptionAr
          : diseaseDescriptionAr // ignore: cast_nullable_to_non_nullable
              as String?,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as DiseaseSeverity,
      affectedAreaPercent: null == affectedAreaPercent
          ? _value.affectedAreaPercent
          : affectedAreaPercent // ignore: cast_nullable_to_non_nullable
              as double,
      detectedCrop: freezed == detectedCrop
          ? _value.detectedCrop
          : detectedCrop // ignore: cast_nullable_to_non_nullable
              as String?,
      growthStage: freezed == growthStage
          ? _value.growthStage
          : growthStage // ignore: cast_nullable_to_non_nullable
              as String?,
      treatments: null == treatments
          ? _value._treatments
          : treatments // ignore: cast_nullable_to_non_nullable
              as List<TreatmentModel>,
      urgentActionRequired: null == urgentActionRequired
          ? _value.urgentActionRequired
          : urgentActionRequired // ignore: cast_nullable_to_non_nullable
              as bool,
      needsExpertReview: null == needsExpertReview
          ? _value.needsExpertReview
          : needsExpertReview // ignore: cast_nullable_to_non_nullable
              as bool,
      expertReviewReason: freezed == expertReviewReason
          ? _value.expertReviewReason
          : expertReviewReason // ignore: cast_nullable_to_non_nullable
              as String?,
      weatherConsideration: freezed == weatherConsideration
          ? _value.weatherConsideration
          : weatherConsideration // ignore: cast_nullable_to_non_nullable
              as String?,
      preventionTips: null == preventionTips
          ? _value._preventionTips
          : preventionTips // ignore: cast_nullable_to_non_nullable
              as List<String>,
      preventionTipsAr: null == preventionTipsAr
          ? _value._preventionTipsAr
          : preventionTipsAr // ignore: cast_nullable_to_non_nullable
              as List<String>,
      imageUrl: freezed == imageUrl
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc
@JsonSerializable()
class _$DiagnosisModelImpl implements _DiagnosisModel {
  const _$DiagnosisModelImpl(
      {@JsonKey(name: 'diagnosis_id') required this.diagnosisId,
      required this.timestamp,
      @JsonKey(name: 'disease_name') required this.diseaseName,
      @JsonKey(name: 'disease_name_ar') required this.diseaseNameAr,
      @JsonKey(name: 'disease_description') this.diseaseDescription,
      @JsonKey(name: 'disease_description_ar') this.diseaseDescriptionAr,
      required this.confidence,
      required this.severity,
      @JsonKey(name: 'affected_area_percent') this.affectedAreaPercent = 0,
      @JsonKey(name: 'detected_crop') this.detectedCrop,
      @JsonKey(name: 'growth_stage') this.growthStage,
      final List<TreatmentModel> treatments = const [],
      @JsonKey(name: 'urgent_action_required')
      this.urgentActionRequired = false,
      @JsonKey(name: 'needs_expert_review') this.needsExpertReview = false,
      @JsonKey(name: 'expert_review_reason') this.expertReviewReason,
      @JsonKey(name: 'weather_consideration') this.weatherConsideration,
      @JsonKey(name: 'prevention_tips')
      final List<String> preventionTips = const [],
      @JsonKey(name: 'prevention_tips_ar')
      final List<String> preventionTipsAr = const [],
      @JsonKey(name: 'image_url') this.imageUrl})
      : _treatments = treatments,
        _preventionTips = preventionTips,
        _preventionTipsAr = preventionTipsAr;

  factory _$DiagnosisModelImpl.fromJson(Map<String, dynamic> json) =>
      _$$DiagnosisModelImplFromJson(json);

  @override
  @JsonKey(name: 'diagnosis_id')
  final String diagnosisId;
  @override
  final DateTime timestamp;
// معلومات المرض
  @override
  @JsonKey(name: 'disease_name')
  final String diseaseName;
  @override
  @JsonKey(name: 'disease_name_ar')
  final String diseaseNameAr;
  @override
  @JsonKey(name: 'disease_description')
  final String? diseaseDescription;
  @override
  @JsonKey(name: 'disease_description_ar')
  final String? diseaseDescriptionAr;
// الثقة والشدة
  @override
  final double confidence;
  @override
  final DiseaseSeverity severity;
  @override
  @JsonKey(name: 'affected_area_percent')
  final double affectedAreaPercent;
// المحصول
  @override
  @JsonKey(name: 'detected_crop')
  final String? detectedCrop;
  @override
  @JsonKey(name: 'growth_stage')
  final String? growthStage;
// العلاج
  final List<TreatmentModel> _treatments;
// العلاج
  @override
  @JsonKey()
  List<TreatmentModel> get treatments {
    if (_treatments is EqualUnmodifiableListView) return _treatments;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_treatments);
  }

  @override
  @JsonKey(name: 'urgent_action_required')
  final bool urgentActionRequired;
// مراجعة الخبير
  @override
  @JsonKey(name: 'needs_expert_review')
  final bool needsExpertReview;
  @override
  @JsonKey(name: 'expert_review_reason')
  final String? expertReviewReason;
// نصائح إضافية
  @override
  @JsonKey(name: 'weather_consideration')
  final String? weatherConsideration;
  final List<String> _preventionTips;
  @override
  @JsonKey(name: 'prevention_tips')
  List<String> get preventionTips {
    if (_preventionTips is EqualUnmodifiableListView) return _preventionTips;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_preventionTips);
  }

  final List<String> _preventionTipsAr;
  @override
  @JsonKey(name: 'prevention_tips_ar')
  List<String> get preventionTipsAr {
    if (_preventionTipsAr is EqualUnmodifiableListView)
      return _preventionTipsAr;
    // ignore: implicit_dynamic_type
    return EqualUnmodifiableListView(_preventionTipsAr);
  }

// الصورة المحفوظة
  @override
  @JsonKey(name: 'image_url')
  final String? imageUrl;

  @override
  String toString() {
    return 'DiagnosisModel(diagnosisId: $diagnosisId, timestamp: $timestamp, diseaseName: $diseaseName, diseaseNameAr: $diseaseNameAr, diseaseDescription: $diseaseDescription, diseaseDescriptionAr: $diseaseDescriptionAr, confidence: $confidence, severity: $severity, affectedAreaPercent: $affectedAreaPercent, detectedCrop: $detectedCrop, growthStage: $growthStage, treatments: $treatments, urgentActionRequired: $urgentActionRequired, needsExpertReview: $needsExpertReview, expertReviewReason: $expertReviewReason, weatherConsideration: $weatherConsideration, preventionTips: $preventionTips, preventionTipsAr: $preventionTipsAr, imageUrl: $imageUrl)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DiagnosisModelImpl &&
            (identical(other.diagnosisId, diagnosisId) ||
                other.diagnosisId == diagnosisId) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.diseaseName, diseaseName) ||
                other.diseaseName == diseaseName) &&
            (identical(other.diseaseNameAr, diseaseNameAr) ||
                other.diseaseNameAr == diseaseNameAr) &&
            (identical(other.diseaseDescription, diseaseDescription) ||
                other.diseaseDescription == diseaseDescription) &&
            (identical(other.diseaseDescriptionAr, diseaseDescriptionAr) ||
                other.diseaseDescriptionAr == diseaseDescriptionAr) &&
            (identical(other.confidence, confidence) ||
                other.confidence == confidence) &&
            (identical(other.severity, severity) ||
                other.severity == severity) &&
            (identical(other.affectedAreaPercent, affectedAreaPercent) ||
                other.affectedAreaPercent == affectedAreaPercent) &&
            (identical(other.detectedCrop, detectedCrop) ||
                other.detectedCrop == detectedCrop) &&
            (identical(other.growthStage, growthStage) ||
                other.growthStage == growthStage) &&
            const DeepCollectionEquality()
                .equals(other._treatments, _treatments) &&
            (identical(other.urgentActionRequired, urgentActionRequired) ||
                other.urgentActionRequired == urgentActionRequired) &&
            (identical(other.needsExpertReview, needsExpertReview) ||
                other.needsExpertReview == needsExpertReview) &&
            (identical(other.expertReviewReason, expertReviewReason) ||
                other.expertReviewReason == expertReviewReason) &&
            (identical(other.weatherConsideration, weatherConsideration) ||
                other.weatherConsideration == weatherConsideration) &&
            const DeepCollectionEquality()
                .equals(other._preventionTips, _preventionTips) &&
            const DeepCollectionEquality()
                .equals(other._preventionTipsAr, _preventionTipsAr) &&
            (identical(other.imageUrl, imageUrl) ||
                other.imageUrl == imageUrl));
  }

  @JsonKey(ignore: true)
  @override
  int get hashCode => Object.hashAll([
        runtimeType,
        diagnosisId,
        timestamp,
        diseaseName,
        diseaseNameAr,
        diseaseDescription,
        diseaseDescriptionAr,
        confidence,
        severity,
        affectedAreaPercent,
        detectedCrop,
        growthStage,
        const DeepCollectionEquality().hash(_treatments),
        urgentActionRequired,
        needsExpertReview,
        expertReviewReason,
        weatherConsideration,
        const DeepCollectionEquality().hash(_preventionTips),
        const DeepCollectionEquality().hash(_preventionTipsAr),
        imageUrl
      ]);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$DiagnosisModelImplCopyWith<_$DiagnosisModelImpl> get copyWith =>
      __$$DiagnosisModelImplCopyWithImpl<_$DiagnosisModelImpl>(
          this, _$identity);

  @override
  Map<String, dynamic> toJson() {
    return _$$DiagnosisModelImplToJson(
      this,
    );
  }
}

abstract class _DiagnosisModel implements DiagnosisModel {
  const factory _DiagnosisModel(
      {@JsonKey(name: 'diagnosis_id') required final String diagnosisId,
      required final DateTime timestamp,
      @JsonKey(name: 'disease_name') required final String diseaseName,
      @JsonKey(name: 'disease_name_ar') required final String diseaseNameAr,
      @JsonKey(name: 'disease_description') final String? diseaseDescription,
      @JsonKey(name: 'disease_description_ar')
      final String? diseaseDescriptionAr,
      required final double confidence,
      required final DiseaseSeverity severity,
      @JsonKey(name: 'affected_area_percent') final double affectedAreaPercent,
      @JsonKey(name: 'detected_crop') final String? detectedCrop,
      @JsonKey(name: 'growth_stage') final String? growthStage,
      final List<TreatmentModel> treatments,
      @JsonKey(name: 'urgent_action_required') final bool urgentActionRequired,
      @JsonKey(name: 'needs_expert_review') final bool needsExpertReview,
      @JsonKey(name: 'expert_review_reason') final String? expertReviewReason,
      @JsonKey(name: 'weather_consideration')
      final String? weatherConsideration,
      @JsonKey(name: 'prevention_tips') final List<String> preventionTips,
      @JsonKey(name: 'prevention_tips_ar') final List<String> preventionTipsAr,
      @JsonKey(name: 'image_url')
      final String? imageUrl}) = _$DiagnosisModelImpl;

  factory _DiagnosisModel.fromJson(Map<String, dynamic> json) =
      _$DiagnosisModelImpl.fromJson;

  @override
  @JsonKey(name: 'diagnosis_id')
  String get diagnosisId;
  @override
  DateTime get timestamp;
  @override // معلومات المرض
  @JsonKey(name: 'disease_name')
  String get diseaseName;
  @override
  @JsonKey(name: 'disease_name_ar')
  String get diseaseNameAr;
  @override
  @JsonKey(name: 'disease_description')
  String? get diseaseDescription;
  @override
  @JsonKey(name: 'disease_description_ar')
  String? get diseaseDescriptionAr;
  @override // الثقة والشدة
  double get confidence;
  @override
  DiseaseSeverity get severity;
  @override
  @JsonKey(name: 'affected_area_percent')
  double get affectedAreaPercent;
  @override // المحصول
  @JsonKey(name: 'detected_crop')
  String? get detectedCrop;
  @override
  @JsonKey(name: 'growth_stage')
  String? get growthStage;
  @override // العلاج
  List<TreatmentModel> get treatments;
  @override
  @JsonKey(name: 'urgent_action_required')
  bool get urgentActionRequired;
  @override // مراجعة الخبير
  @JsonKey(name: 'needs_expert_review')
  bool get needsExpertReview;
  @override
  @JsonKey(name: 'expert_review_reason')
  String? get expertReviewReason;
  @override // نصائح إضافية
  @JsonKey(name: 'weather_consideration')
  String? get weatherConsideration;
  @override
  @JsonKey(name: 'prevention_tips')
  List<String> get preventionTips;
  @override
  @JsonKey(name: 'prevention_tips_ar')
  List<String> get preventionTipsAr;
  @override // الصورة المحفوظة
  @JsonKey(name: 'image_url')
  String? get imageUrl;
  @override
  @JsonKey(ignore: true)
  _$$DiagnosisModelImplCopyWith<_$DiagnosisModelImpl> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
mixin _$DiagnosisSummary {
  String get id => throw _privateConstructorUsedError;
  String get diseaseNameAr => throw _privateConstructorUsedError;
  double get confidence => throw _privateConstructorUsedError;
  DiseaseSeverity get severity => throw _privateConstructorUsedError;
  DateTime get timestamp => throw _privateConstructorUsedError;
  String? get imageUrl => throw _privateConstructorUsedError;

  @JsonKey(ignore: true)
  $DiagnosisSummaryCopyWith<DiagnosisSummary> get copyWith =>
      throw _privateConstructorUsedError;
}

/// @nodoc
abstract class $DiagnosisSummaryCopyWith<$Res> {
  factory $DiagnosisSummaryCopyWith(
          DiagnosisSummary value, $Res Function(DiagnosisSummary) then) =
      _$DiagnosisSummaryCopyWithImpl<$Res, DiagnosisSummary>;
  @useResult
  $Res call(
      {String id,
      String diseaseNameAr,
      double confidence,
      DiseaseSeverity severity,
      DateTime timestamp,
      String? imageUrl});
}

/// @nodoc
class _$DiagnosisSummaryCopyWithImpl<$Res, $Val extends DiagnosisSummary>
    implements $DiagnosisSummaryCopyWith<$Res> {
  _$DiagnosisSummaryCopyWithImpl(this._value, this._then);

  // ignore: unused_field
  final $Val _value;
  // ignore: unused_field
  final $Res Function($Val) _then;

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? diseaseNameAr = null,
    Object? confidence = null,
    Object? severity = null,
    Object? timestamp = null,
    Object? imageUrl = freezed,
  }) {
    return _then(_value.copyWith(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      diseaseNameAr: null == diseaseNameAr
          ? _value.diseaseNameAr
          : diseaseNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as DiseaseSeverity,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      imageUrl: freezed == imageUrl
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String?,
    ) as $Val);
  }
}

/// @nodoc
abstract class _$$DiagnosisSummaryImplCopyWith<$Res>
    implements $DiagnosisSummaryCopyWith<$Res> {
  factory _$$DiagnosisSummaryImplCopyWith(_$DiagnosisSummaryImpl value,
          $Res Function(_$DiagnosisSummaryImpl) then) =
      __$$DiagnosisSummaryImplCopyWithImpl<$Res>;
  @override
  @useResult
  $Res call(
      {String id,
      String diseaseNameAr,
      double confidence,
      DiseaseSeverity severity,
      DateTime timestamp,
      String? imageUrl});
}

/// @nodoc
class __$$DiagnosisSummaryImplCopyWithImpl<$Res>
    extends _$DiagnosisSummaryCopyWithImpl<$Res, _$DiagnosisSummaryImpl>
    implements _$$DiagnosisSummaryImplCopyWith<$Res> {
  __$$DiagnosisSummaryImplCopyWithImpl(_$DiagnosisSummaryImpl _value,
      $Res Function(_$DiagnosisSummaryImpl) _then)
      : super(_value, _then);

  @pragma('vm:prefer-inline')
  @override
  $Res call({
    Object? id = null,
    Object? diseaseNameAr = null,
    Object? confidence = null,
    Object? severity = null,
    Object? timestamp = null,
    Object? imageUrl = freezed,
  }) {
    return _then(_$DiagnosisSummaryImpl(
      id: null == id
          ? _value.id
          : id // ignore: cast_nullable_to_non_nullable
              as String,
      diseaseNameAr: null == diseaseNameAr
          ? _value.diseaseNameAr
          : diseaseNameAr // ignore: cast_nullable_to_non_nullable
              as String,
      confidence: null == confidence
          ? _value.confidence
          : confidence // ignore: cast_nullable_to_non_nullable
              as double,
      severity: null == severity
          ? _value.severity
          : severity // ignore: cast_nullable_to_non_nullable
              as DiseaseSeverity,
      timestamp: null == timestamp
          ? _value.timestamp
          : timestamp // ignore: cast_nullable_to_non_nullable
              as DateTime,
      imageUrl: freezed == imageUrl
          ? _value.imageUrl
          : imageUrl // ignore: cast_nullable_to_non_nullable
              as String?,
    ));
  }
}

/// @nodoc

class _$DiagnosisSummaryImpl implements _DiagnosisSummary {
  const _$DiagnosisSummaryImpl(
      {required this.id,
      required this.diseaseNameAr,
      required this.confidence,
      required this.severity,
      required this.timestamp,
      this.imageUrl});

  @override
  final String id;
  @override
  final String diseaseNameAr;
  @override
  final double confidence;
  @override
  final DiseaseSeverity severity;
  @override
  final DateTime timestamp;
  @override
  final String? imageUrl;

  @override
  String toString() {
    return 'DiagnosisSummary(id: $id, diseaseNameAr: $diseaseNameAr, confidence: $confidence, severity: $severity, timestamp: $timestamp, imageUrl: $imageUrl)';
  }

  @override
  bool operator ==(Object other) {
    return identical(this, other) ||
        (other.runtimeType == runtimeType &&
            other is _$DiagnosisSummaryImpl &&
            (identical(other.id, id) || other.id == id) &&
            (identical(other.diseaseNameAr, diseaseNameAr) ||
                other.diseaseNameAr == diseaseNameAr) &&
            (identical(other.confidence, confidence) ||
                other.confidence == confidence) &&
            (identical(other.severity, severity) ||
                other.severity == severity) &&
            (identical(other.timestamp, timestamp) ||
                other.timestamp == timestamp) &&
            (identical(other.imageUrl, imageUrl) ||
                other.imageUrl == imageUrl));
  }

  @override
  int get hashCode => Object.hash(runtimeType, id, diseaseNameAr, confidence,
      severity, timestamp, imageUrl);

  @JsonKey(ignore: true)
  @override
  @pragma('vm:prefer-inline')
  _$$DiagnosisSummaryImplCopyWith<_$DiagnosisSummaryImpl> get copyWith =>
      __$$DiagnosisSummaryImplCopyWithImpl<_$DiagnosisSummaryImpl>(
          this, _$identity);
}

abstract class _DiagnosisSummary implements DiagnosisSummary {
  const factory _DiagnosisSummary(
      {required final String id,
      required final String diseaseNameAr,
      required final double confidence,
      required final DiseaseSeverity severity,
      required final DateTime timestamp,
      final String? imageUrl}) = _$DiagnosisSummaryImpl;

  @override
  String get id;
  @override
  String get diseaseNameAr;
  @override
  double get confidence;
  @override
  DiseaseSeverity get severity;
  @override
  DateTime get timestamp;
  @override
  String? get imageUrl;
  @override
  @JsonKey(ignore: true)
  _$$DiagnosisSummaryImplCopyWith<_$DiagnosisSummaryImpl> get copyWith =>
      throw _privateConstructorUsedError;
}
