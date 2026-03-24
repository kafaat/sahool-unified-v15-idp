/// Pivot Irrigation Models - Valley Style
/// نماذج الري المحوري - بأسلوب فالي
library;

import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:latlong2/latlong.dart';

part 'pivot_models.freezed.dart';
part 'pivot_models.g.dart';

// ═══════════════════════════════════════════════════════════════════════════
// Pivot Configuration - إعدادات الري المحوري
// ═══════════════════════════════════════════════════════════════════════════

/// Pivot irrigation system configuration
/// إعدادات نظام الري المحوري
@freezed
class PivotConfiguration with _$PivotConfiguration {
  const factory PivotConfiguration({
    required String id,
    required String fieldId,
    required String name,
    @Default('') String nameAr,

    /// Center point coordinates - نقطة المركز
    required double centerLat,
    required double centerLng,

    /// Pivot arm length in meters - طول الذراع بالأمتار
    required double lengthMeters,

    /// Overhang length (end gun extension) - امتداد المدفع الطرفي
    @Default(0) double overhangMeters,

    /// Number of spans/towers - عدد الأبراج
    required int spansCount,

    /// Rotation direction - اتجاه الدوران
    @Default(RotationDirection.clockwise) RotationDirection rotationDirection,

    /// Total irrigated area in hectares - المساحة المروية بالهكتار
    required double areaHectares,

    /// Pivot type - نوع المحوري
    @Default(PivotType.fullCircle) PivotType pivotType,

    /// Start angle for partial pivots (degrees) - زاوية البداية
    @Default(0) double startAngle,

    /// End angle for partial pivots (degrees) - زاوية النهاية
    @Default(360) double endAngle,

    /// Flow rate in liters per hour - معدل التدفق
    required double flowRateLph,

    /// Operating pressure in bars - ضغط التشغيل
    @Default(2.5) double operatingPressureBar,

    /// Has Variable Rate Irrigation - معدل ري متغير
    @Default(false) bool hasVRI,

    /// Has end gun - مدفع طرفي
    @Default(false) bool hasEndGun,

    /// Has corner system - نظام الزوايا
    @Default(false) bool hasCornerSystem,

    /// List of sectors - قائمة القطاعات
    @Default([]) List<PivotSector> sectors,

    /// VRI zones if applicable - مناطق VRI
    @Default([]) List<VRIZone> vriZones,

    /// Created timestamp
    DateTime? createdAt,

    /// Last updated timestamp
    DateTime? updatedAt,
  }) = _PivotConfiguration;

  factory PivotConfiguration.fromJson(Map<String, dynamic> json) =>
      _$PivotConfigurationFromJson(json);
}

/// Pivot type enumeration
enum PivotType {
  @JsonValue('full_circle')
  fullCircle,
  @JsonValue('partial_circle')
  partialCircle,
  @JsonValue('corner')
  corner,
  @JsonValue('linear')
  linear,
}

/// Rotation direction
enum RotationDirection {
  @JsonValue('clockwise')
  clockwise,
  @JsonValue('counterclockwise')
  counterclockwise,
}

// ═══════════════════════════════════════════════════════════════════════════
// Pivot Sector - قطاع المحوري
// ═══════════════════════════════════════════════════════════════════════════

/// Individual sector of the pivot (pie slice)
/// قطاع فردي من المحوري (شريحة)
@freezed
class PivotSector with _$PivotSector {
  const factory PivotSector({
    required String id,
    required int sectorNumber,

    /// Sector name - اسم القطاع
    @Default('') String name,
    @Default('') String nameAr,

    /// Start angle in degrees - زاوية البداية
    required double startAngle,

    /// End angle in degrees - زاوية النهاية
    required double endAngle,

    /// Irrigation depth in mm - عمق الري
    @Default(25) double irrigationDepthMm,

    /// Application rate (mm/hr) - معدل التطبيق
    @Default(6.0) double applicationRateMmHr,

    /// Is sector enabled - القطاع مفعل
    @Default(true) bool isEnabled,

    /// Speed percentage (50-100%) - نسبة السرعة
    @Default(100) double speedPercent,

    /// Crop type in this sector - نوع المحصول
    @Default('') String cropType,

    /// Soil type in this sector - نوع التربة
    @Default('') String soilType,

    /// NDVI value (if available) - قيمة NDVI
    double? ndviValue,

    /// Soil moisture percentage - نسبة رطوبة التربة
    double? soilMoisturePercent,

    /// Color for visualization - لون العرض
    @Default('#4CAF50') String color,
  }) = _PivotSector;

  factory PivotSector.fromJson(Map<String, dynamic> json) =>
      _$PivotSectorFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════
// VRI Zone - منطقة الري متغير المعدل
// ═══════════════════════════════════════════════════════════════════════════

/// Variable Rate Irrigation zone
/// منطقة الري متغير المعدل
@freezed
class VRIZone with _$VRIZone {
  const factory VRIZone({
    required String id,
    required String name,
    @Default('') String nameAr,

    /// Zone polygon coordinates (within pivot circle)
    required List<List<double>> coordinates,

    /// Application rate multiplier (0.0 - 1.5) - مضاعف معدل التطبيق
    @Default(1.0) double rateMultiplier,

    /// Target soil moisture - رطوبة التربة المستهدفة
    @Default(60) double targetSoilMoisturePercent,

    /// Management zone type - نوع منطقة الإدارة
    @Default(VRIZoneType.normal) VRIZoneType zoneType,

    /// Color for visualization
    @Default('#2196F3') String color,

    /// Is zone active
    @Default(true) bool isActive,
  }) = _VRIZone;

  factory VRIZone.fromJson(Map<String, dynamic> json) =>
      _$VRIZoneFromJson(json);
}

/// VRI Zone types
enum VRIZoneType {
  @JsonValue('normal')
  normal,
  @JsonValue('high_need')
  highNeed,
  @JsonValue('low_need')
  lowNeed,
  @JsonValue('no_irrigation')
  noIrrigation,
  @JsonValue('drainage')
  drainage,
}

// ═══════════════════════════════════════════════════════════════════════════
// Pivot Status - حالة المحوري
// ═══════════════════════════════════════════════════════════════════════════

/// Real-time pivot status
/// حالة المحوري في الوقت الحقيقي
@freezed
class PivotStatus with _$PivotStatus {
  const factory PivotStatus({
    required String pivotId,

    /// Current angle position (0-360°) - الموقع الزاوي الحالي
    required double currentAngle,

    /// Operating status - حالة التشغيل
    required PivotOperatingStatus operatingStatus,

    /// Direction of movement - اتجاه الحركة
    required PivotDirection direction,

    /// Current speed percentage (0-100%) - السرعة الحالية
    required double speedPercent,

    /// Timer setting in hours - إعداد المؤقت
    @Default(0) double timerHours,

    /// Elapsed time in minutes - الوقت المنقضي
    @Default(0) double elapsedMinutes,

    /// Current flow rate L/h - معدل التدفق الحالي
    @Default(0) double currentFlowRateLph,

    /// Current pressure (bar) - الضغط الحالي
    @Default(0) double currentPressureBar,

    /// End gun status - حالة المدفع الطرفي
    @Default(false) bool endGunActive,

    /// Corner system status - حالة نظام الزوايا
    @Default(false) bool cornerSystemActive,

    /// Water applied this run (m³) - المياه المطبقة هذه الدورة
    @Default(0) double waterAppliedM3,

    /// Energy consumed this run (kWh) - الطاقة المستهلكة
    @Default(0) double energyConsumedKwh,

    /// Estimated completion time
    DateTime? estimatedCompletionTime,

    /// Last update timestamp
    required DateTime lastUpdated,

    /// Active alerts - التنبيهات النشطة
    @Default([]) List<PivotAlert> activeAlerts,

    /// GPS coordinates of pivot end (arm tip)
    double? armEndLat,
    double? armEndLng,
  }) = _PivotStatus;

  factory PivotStatus.fromJson(Map<String, dynamic> json) =>
      _$PivotStatusFromJson(json);
}

/// Pivot operating status
enum PivotOperatingStatus {
  @JsonValue('stopped')
  stopped,
  @JsonValue('running')
  running,
  @JsonValue('paused')
  paused,
  @JsonValue('fault')
  fault,
  @JsonValue('maintenance')
  maintenance,
  @JsonValue('scheduled')
  scheduled,
}

/// Pivot movement direction
enum PivotDirection {
  @JsonValue('forward')
  forward,
  @JsonValue('reverse')
  reverse,
  @JsonValue('stopped')
  stopped,
}

// ═══════════════════════════════════════════════════════════════════════════
// Pivot Alerts - تنبيهات المحوري
// ═══════════════════════════════════════════════════════════════════════════

/// Pivot alert/alarm
/// تنبيه المحوري
@freezed
class PivotAlert with _$PivotAlert {
  const factory PivotAlert({
    required String id,
    required String pivotId,

    /// Alert type - نوع التنبيه
    required PivotAlertType alertType,

    /// Severity level - مستوى الخطورة
    required AlertSeverity severity,

    /// Alert message
    required String message,
    required String messageAr,

    /// Tower/span number if applicable
    int? towerNumber,

    /// Is alert acknowledged
    @Default(false) bool isAcknowledged,

    /// Alert timestamp
    required DateTime timestamp,

    /// Resolution timestamp
    DateTime? resolvedAt,
  }) = _PivotAlert;

  factory PivotAlert.fromJson(Map<String, dynamic> json) =>
      _$PivotAlertFromJson(json);
}

/// Alert types specific to pivot irrigation
enum PivotAlertType {
  @JsonValue('low_pressure')
  lowPressure,
  @JsonValue('high_pressure')
  highPressure,
  @JsonValue('power_failure')
  powerFailure,
  @JsonValue('motor_overload')
  motorOverload,
  @JsonValue('tower_alignment')
  towerAlignment,
  @JsonValue('end_gun_fault')
  endGunFault,
  @JsonValue('corner_system_fault')
  cornerSystemFault,
  @JsonValue('low_flow')
  lowFlow,
  @JsonValue('high_flow')
  highFlow,
  @JsonValue('obstacle_detected')
  obstacleDetected,
  @JsonValue('pipeline_leak')
  pipelineLeak,
  @JsonValue('scheduled_maintenance')
  scheduledMaintenance,
  @JsonValue('communication_lost')
  communicationLost,
}

/// Alert severity levels
enum AlertSeverity {
  @JsonValue('info')
  info,
  @JsonValue('warning')
  warning,
  @JsonValue('critical')
  critical,
  @JsonValue('emergency')
  emergency,
}

// ═══════════════════════════════════════════════════════════════════════════
// Pivot Schedule - جدول المحوري
// ═══════════════════════════════════════════════════════════════════════════

/// Pivot irrigation schedule
/// جدول ري المحوري
@freezed
class PivotSchedule with _$PivotSchedule {
  const factory PivotSchedule({
    required String id,
    required String pivotId,
    required String name,
    @Default('') String nameAr,

    /// Schedule type - نوع الجدول
    required ScheduleType scheduleType,

    /// List of scheduled runs
    required List<ScheduledRun> runs,

    /// Is schedule active
    @Default(true) bool isActive,

    /// Created timestamp
    DateTime? createdAt,
  }) = _PivotSchedule;

  factory PivotSchedule.fromJson(Map<String, dynamic> json) =>
      _$PivotScheduleFromJson(json);
}

/// Schedule type
enum ScheduleType {
  @JsonValue('daily')
  daily,
  @JsonValue('weekly')
  weekly,
  @JsonValue('custom')
  custom,
  @JsonValue('sensor_triggered')
  sensorTriggered,
}

/// Scheduled irrigation run
/// دورة ري مجدولة
@freezed
class ScheduledRun with _$ScheduledRun {
  const factory ScheduledRun({
    required String id,

    /// Day of week (0=Sunday) for weekly schedules
    int? dayOfWeek,

    /// Start time (HH:mm)
    required String startTime,

    /// Duration in hours
    required double durationHours,

    /// Speed percentage
    @Default(100) double speedPercent,

    /// Direction
    @Default(PivotDirection.forward) PivotDirection direction,

    /// Start angle (for partial runs)
    @Default(0) double startAngle,

    /// End angle (for partial runs)
    @Default(360) double endAngle,

    /// Apply irrigation depth in mm
    @Default(25) double irrigationDepthMm,

    /// Is run enabled
    @Default(true) bool isEnabled,
  }) = _ScheduledRun;

  factory ScheduledRun.fromJson(Map<String, dynamic> json) =>
      _$ScheduledRunFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════
// Pivot Run History - سجل دورات المحوري
// ═══════════════════════════════════════════════════════════════════════════

/// Historical pivot run record
/// سجل دورة المحوري التاريخية
@freezed
class PivotRunHistory with _$PivotRunHistory {
  const factory PivotRunHistory({
    required String id,
    required String pivotId,

    /// Run start time - وقت البداية
    required DateTime startTime,

    /// Run end time - وقت النهاية
    DateTime? endTime,

    /// Start angle
    required double startAngle,

    /// End angle
    double? endAngle,

    /// Direction
    required PivotDirection direction,

    /// Average speed percent
    required double avgSpeedPercent,

    /// Total water applied (m³) - إجمالي المياه
    required double waterAppliedM3,

    /// Energy consumed (kWh) - الطاقة المستهلكة
    @Default(0) double energyConsumedKwh,

    /// Run status - حالة الدورة
    required RunStatus status,

    /// Stop reason if stopped early
    String? stopReason,

    /// Alerts during run
    @Default([]) List<PivotAlert> alerts,
  }) = _PivotRunHistory;

  factory PivotRunHistory.fromJson(Map<String, dynamic> json) =>
      _$PivotRunHistoryFromJson(json);
}

/// Run status
enum RunStatus {
  @JsonValue('completed')
  completed,
  @JsonValue('in_progress')
  inProgress,
  @JsonValue('stopped')
  stopped,
  @JsonValue('faulted')
  faulted,
}

// ═══════════════════════════════════════════════════════════════════════════
// Pivot Statistics - إحصائيات المحوري
// ═══════════════════════════════════════════════════════════════════════════

/// Pivot performance statistics
/// إحصائيات أداء المحوري
@freezed
class PivotStatistics with _$PivotStatistics {
  const factory PivotStatistics({
    required String pivotId,
    required String period, // daily, weekly, monthly, seasonal

    /// Total water applied (m³) - إجمالي المياه
    required double totalWaterM3,

    /// Total energy consumed (kWh) - إجمالي الطاقة
    required double totalEnergyKwh,

    /// Total run time (hours) - إجمالي وقت التشغيل
    required double totalRunHours,

    /// Number of complete circles - عدد الدورات الكاملة
    required int completeCircles,

    /// Average irrigation depth (mm) - متوسط عمق الري
    required double avgIrrigationDepthMm,

    /// Average speed percent
    required double avgSpeedPercent,

    /// Efficiency percentage - كفاءة الري
    required double efficiencyPercent,

    /// Water cost (currency) - تكلفة المياه
    @Default(0) double waterCost,

    /// Energy cost (currency) - تكلفة الطاقة
    @Default(0) double energyCost,

    /// Number of faults - عدد الأعطال
    @Default(0) int faultCount,

    /// Downtime hours - ساعات التوقف
    @Default(0) double downtimeHours,

    /// Period start date
    required DateTime periodStart,

    /// Period end date
    required DateTime periodEnd,
  }) = _PivotStatistics;

  factory PivotStatistics.fromJson(Map<String, dynamic> json) =>
      _$PivotStatisticsFromJson(json);
}

// ═══════════════════════════════════════════════════════════════════════════
// Pivot Control Command - أمر التحكم
// ═══════════════════════════════════════════════════════════════════════════

/// Command to control pivot
/// أمر للتحكم في المحوري
@freezed
class PivotControlCommand with _$PivotControlCommand {
  const factory PivotControlCommand({
    required String pivotId,
    required PivotCommandType commandType,

    /// Target speed percent (for speed commands)
    double? speedPercent,

    /// Target angle (for move-to commands)
    double? targetAngle,

    /// Direction (for direction commands)
    PivotDirection? direction,

    /// End gun setting
    bool? endGunEnabled,

    /// Timer hours (for timer commands)
    double? timerHours,

    /// Sector numbers to enable/disable
    List<int>? sectorNumbers,

    /// Command issued by user ID
    required String issuedBy,

    /// Timestamp
    required DateTime timestamp,
  }) = _PivotControlCommand;

  factory PivotControlCommand.fromJson(Map<String, dynamic> json) =>
      _$PivotControlCommandFromJson(json);
}

/// Command types
enum PivotCommandType {
  @JsonValue('start')
  start,
  @JsonValue('stop')
  stop,
  @JsonValue('pause')
  pause,
  @JsonValue('resume')
  resume,
  @JsonValue('set_speed')
  setSpeed,
  @JsonValue('set_direction')
  setDirection,
  @JsonValue('move_to_angle')
  moveToAngle,
  @JsonValue('toggle_end_gun')
  toggleEndGun,
  @JsonValue('set_timer')
  setTimer,
  @JsonValue('enable_sectors')
  enableSectors,
  @JsonValue('disable_sectors')
  disableSectors,
  @JsonValue('emergency_stop')
  emergencyStop,
}

// ═══════════════════════════════════════════════════════════════════════════
// Extension Methods - طرق الامتداد
// ═══════════════════════════════════════════════════════════════════════════

extension PivotConfigurationX on PivotConfiguration {
  /// Calculate area for a given angle span
  double areaForAngleSpan(double startAngle, double endAngle) {
    final span = (endAngle - startAngle).abs() / 360.0;
    return areaHectares * span;
  }

  /// Get center as LatLng
  LatLng get center => LatLng(centerLat, centerLng);

  /// Calculate total radius including overhang
  double get totalRadiusMeters => lengthMeters + overhangMeters;
}

extension PivotStatusX on PivotStatus {
  /// Is pivot currently irrigating
  bool get isIrrigating => operatingStatus == PivotOperatingStatus.running;

  /// Has any active alerts
  bool get hasAlerts => activeAlerts.isNotEmpty;

  /// Has critical alerts
  bool get hasCriticalAlerts => activeAlerts.any(
    (a) => a.severity == AlertSeverity.critical ||
           a.severity == AlertSeverity.emergency
  );

  /// Progress percentage for current run (0-100)
  double get progressPercent {
    if (timerHours <= 0) return 0;
    return ((elapsedMinutes / 60) / timerHours * 100).clamp(0, 100);
  }
}

extension PivotSectorX on PivotSector {
  /// Calculate sector angle span
  double get angleSpan => (endAngle - startAngle).abs();

  /// Calculate time to irrigate this sector at 100% speed
  double irrigationTimeMinutes(double fullCircleMinutes) {
    return fullCircleMinutes * (angleSpan / 360.0) * (100 / speedPercent);
  }
}
