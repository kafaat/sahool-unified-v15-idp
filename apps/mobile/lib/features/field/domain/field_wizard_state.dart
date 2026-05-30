import 'package:latlong2/latlong.dart';

/// حالة معالج إنشاء الحقل - 6 خطوات
class FieldWizardState {
  final int currentStep;
  final String? farmId;
  final List<LatLng> polygonPoints;
  final double area; // hectares
  final String name;
  final String? seasonName;
  final DateTime? plantingDate;
  final DateTime? harvestDate;
  final String cropType;
  final String? previousCrop;
  final String soilType;
  final String irrigationType;
  final String? error;
  final bool isSubmitting;

  const FieldWizardState({
    this.currentStep = 0,
    this.farmId,
    this.polygonPoints = const [],
    this.area = 0.0,
    this.name = '',
    this.seasonName,
    this.plantingDate,
    this.harvestDate,
    this.cropType = '',
    this.previousCrop,
    this.soilType = '',
    this.irrigationType = '',
    this.error,
    this.isSubmitting = false,
  });

  FieldWizardState copyWith({
    int? currentStep,
    String? farmId,
    List<LatLng>? polygonPoints,
    double? area,
    String? name,
    String? seasonName,
    DateTime? plantingDate,
    DateTime? harvestDate,
    String? cropType,
    String? previousCrop,
    String? soilType,
    String? irrigationType,
    String? error,
    bool? isSubmitting,
    bool clearFarmId = false,
    bool clearSeasonName = false,
    bool clearPlantingDate = false,
    bool clearHarvestDate = false,
    bool clearPreviousCrop = false,
    bool clearError = false,
  }) {
    return FieldWizardState(
      currentStep: currentStep ?? this.currentStep,
      farmId: clearFarmId ? null : (farmId ?? this.farmId),
      polygonPoints: polygonPoints ?? this.polygonPoints,
      area: area ?? this.area,
      name: name ?? this.name,
      seasonName: clearSeasonName ? null : (seasonName ?? this.seasonName),
      plantingDate: clearPlantingDate ? null : (plantingDate ?? this.plantingDate),
      harvestDate: clearHarvestDate ? null : (harvestDate ?? this.harvestDate),
      cropType: cropType ?? this.cropType,
      previousCrop: clearPreviousCrop ? null : (previousCrop ?? this.previousCrop),
      soilType: soilType ?? this.soilType,
      irrigationType: irrigationType ?? this.irrigationType,
      error: clearError ? null : (error ?? this.error),
      isSubmitting: isSubmitting ?? this.isSubmitting,
    );
  }
}
