// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Motion Service
// خدمة استشعار الحركة - جيروسكوب ومقياس التسارع
// ═══════════════════════════════════════════════════════════════════════════

import 'dart:async';
import 'dart:math' as math;
import 'dart:ui';

import 'package:flutter/foundation.dart';
import 'package:sensors_plus/sensors_plus.dart';

// ─────────────────────────────────────────────────────────────────────────────
// MOTION DATA MODELS
// ─────────────────────────────────────────────────────────────────────────────

/// Normalized motion data combining gyroscope and accelerometer
/// بيانات الحركة المطبّعة من الجيروسكوب ومقياس التسارع
class MotionData {
  /// X-axis tilt (-1.0 to 1.0) - Left/Right
  final double tiltX;

  /// Y-axis tilt (-1.0 to 1.0) - Forward/Backward
  final double tiltY;

  /// Z-axis rotation (-1.0 to 1.0)
  final double rotationZ;

  /// Acceleration magnitude (0.0 to 1.0+)
  final double accelerationMagnitude;

  /// Angular velocity magnitude
  final double angularVelocity;

  /// Whether device is mostly still
  final bool isStable;

  /// Raw gyroscope values (rad/s)
  final Vector3 gyroscope;

  /// Raw accelerometer values (m/s^2)
  final Vector3 accelerometer;

  /// Timestamp of the reading
  final DateTime timestamp;

  const MotionData({
    this.tiltX = 0.0,
    this.tiltY = 0.0,
    this.rotationZ = 0.0,
    this.accelerationMagnitude = 0.0,
    this.angularVelocity = 0.0,
    this.isStable = true,
    this.gyroscope = const Vector3(0, 0, 0),
    this.accelerometer = const Vector3(0, 0, 9.8),
    DateTime? timestamp,
  }) : timestamp = timestamp ?? const _ConstDateTime();

  /// Zero motion data (device at rest, flat)
  static const MotionData zero = MotionData();

  /// Create a copy with updated values
  MotionData copyWith({
    double? tiltX,
    double? tiltY,
    double? rotationZ,
    double? accelerationMagnitude,
    double? angularVelocity,
    bool? isStable,
    Vector3? gyroscope,
    Vector3? accelerometer,
    DateTime? timestamp,
  }) {
    return MotionData(
      tiltX: tiltX ?? this.tiltX,
      tiltY: tiltY ?? this.tiltY,
      rotationZ: rotationZ ?? this.rotationZ,
      accelerationMagnitude: accelerationMagnitude ?? this.accelerationMagnitude,
      angularVelocity: angularVelocity ?? this.angularVelocity,
      isStable: isStable ?? this.isStable,
      gyroscope: gyroscope ?? this.gyroscope,
      accelerometer: accelerometer ?? this.accelerometer,
      timestamp: timestamp ?? this.timestamp,
    );
  }

  @override
  String toString() =>
      'MotionData(tiltX: ${tiltX.toStringAsFixed(2)}, tiltY: ${tiltY.toStringAsFixed(2)}, stable: $isStable)';
}

/// Helper class for constant DateTime
class _ConstDateTime implements DateTime {
  const _ConstDateTime();

  @override
  dynamic noSuchMethod(Invocation invocation) => DateTime.now();
}

/// Simple 3D vector class
class Vector3 {
  final double x;
  final double y;
  final double z;

  const Vector3(this.x, this.y, this.z);

  double get magnitude => math.sqrt(x * x + y * y + z * z);

  Vector3 operator +(Vector3 other) =>
      Vector3(x + other.x, y + other.y, z + other.z);

  Vector3 operator -(Vector3 other) =>
      Vector3(x - other.x, y - other.y, z - other.z);

  Vector3 operator *(double scalar) =>
      Vector3(x * scalar, y * scalar, z * scalar);

  @override
  String toString() =>
      'Vector3(${x.toStringAsFixed(2)}, ${y.toStringAsFixed(2)}, ${z.toStringAsFixed(2)})';
}

// ─────────────────────────────────────────────────────────────────────────────
// SMOOTHING ALGORITHMS
// ─────────────────────────────────────────────────────────────────────────────

/// Low-pass filter for smoothing sensor data
/// مرشح تمرير منخفض لتنعيم بيانات المستشعر
class LowPassFilter {
  final double alpha;
  double _value = 0.0;
  bool _initialized = false;

  /// Creates a low-pass filter with smoothing factor [alpha] (0.0 to 1.0)
  /// Lower alpha = more smoothing, higher alpha = more responsive
  LowPassFilter({this.alpha = 0.1});

  /// Apply the filter to a new value
  double filter(double newValue) {
    if (!_initialized) {
      _value = newValue;
      _initialized = true;
      return _value;
    }

    _value = alpha * newValue + (1 - alpha) * _value;
    return _value;
  }

  /// Reset the filter
  void reset() {
    _value = 0.0;
    _initialized = false;
  }

  /// Current filtered value
  double get value => _value;
}

/// Exponential moving average for smoother transitions
/// المتوسط المتحرك الأسي لانتقالات أكثر سلاسة
class ExponentialMovingAverage {
  final int windowSize;
  final List<double> _values = [];
  double _ema = 0.0;
  late final double _multiplier;

  ExponentialMovingAverage({this.windowSize = 10}) {
    _multiplier = 2.0 / (windowSize + 1);
  }

  double add(double value) {
    if (_values.isEmpty) {
      _ema = value;
    } else {
      _ema = (value - _ema) * _multiplier + _ema;
    }

    _values.add(value);
    if (_values.length > windowSize) {
      _values.removeAt(0);
    }

    return _ema;
  }

  double get value => _ema;

  void reset() {
    _values.clear();
    _ema = 0.0;
  }
}

/// Kalman-like filter for optimal smoothing
/// مرشح كالمان للتنعيم الأمثل
class KalmanFilter {
  double _estimate = 0.0;
  double _errorEstimate = 1.0;
  final double processNoise;
  final double measurementNoise;
  bool _initialized = false;

  KalmanFilter({
    this.processNoise = 0.01,
    this.measurementNoise = 0.1,
  });

  double filter(double measurement) {
    if (!_initialized) {
      _estimate = measurement;
      _initialized = true;
      return _estimate;
    }

    // Prediction
    final errorPrediction = _errorEstimate + processNoise;

    // Update
    final kalmanGain = errorPrediction / (errorPrediction + measurementNoise);
    _estimate = _estimate + kalmanGain * (measurement - _estimate);
    _errorEstimate = (1 - kalmanGain) * errorPrediction;

    return _estimate;
  }

  double get value => _estimate;

  void reset() {
    _estimate = 0.0;
    _errorEstimate = 1.0;
    _initialized = false;
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// MOTION SERVICE
// ─────────────────────────────────────────────────────────────────────────────

/// Motion service for handling gyroscope and accelerometer data
/// خدمة الحركة لمعالجة بيانات الجيروسكوب ومقياس التسارع
class MotionService extends ChangeNotifier {
  static MotionService? _instance;

  /// Singleton instance
  static MotionService get instance {
    _instance ??= MotionService._();
    return _instance!;
  }

  MotionService._();

  /// Factory constructor for testing
  factory MotionService.create() => MotionService._();

  // Stream subscriptions
  StreamSubscription<GyroscopeEvent>? _gyroscopeSubscription;
  StreamSubscription<AccelerometerEvent>? _accelerometerSubscription;

  // Filters for smoothing
  final _tiltXFilter = KalmanFilter(processNoise: 0.005, measurementNoise: 0.05);
  final _tiltYFilter = KalmanFilter(processNoise: 0.005, measurementNoise: 0.05);
  final _rotationZFilter = LowPassFilter(alpha: 0.15);
  final _accelMagFilter = ExponentialMovingAverage(windowSize: 5);

  // Current state
  MotionData _currentData = MotionData.zero;
  Vector3 _lastGyroscope = const Vector3(0, 0, 0);
  Vector3 _lastAccelerometer = const Vector3(0, 0, 9.8);

  // Configuration
  bool _isActive = false;
  bool _isBatterySaverMode = false;
  Duration _samplingPeriod = const Duration(milliseconds: 16); // ~60fps
  double _sensitivity = 1.0;

  // Stability detection
  final List<double> _recentAccelMagnitudes = [];
  static const int _stabilityWindowSize = 10;
  static const double _stabilityThreshold = 0.5;

  // Battery saver settings
  static const Duration _batterySaverPeriod = Duration(milliseconds: 50); // ~20fps
  static const Duration _normalPeriod = Duration(milliseconds: 16); // ~60fps

  // Shake detection
  double _lastShakeMagnitude = 0.0;
  DateTime _lastShakeTime = DateTime.now();
  final List<Function()> _shakeListeners = [];

  /// Current motion data
  MotionData get currentData => _currentData;

  /// Whether the service is currently active
  bool get isActive => _isActive;

  /// Whether battery saver mode is enabled
  bool get isBatterySaverMode => _isBatterySaverMode;

  /// Current sensitivity (0.1 to 2.0)
  double get sensitivity => _sensitivity;

  /// Stream of motion data
  Stream<MotionData> get motionStream => _motionController.stream;
  final _motionController = StreamController<MotionData>.broadcast();

  /// Initialize and start the motion service
  /// بدء خدمة الحركة
  Future<void> start() async {
    if (_isActive) return;

    _isActive = true;
    debugPrint('🎯 MotionService: Starting sensors...');

    try {
      // Configure sampling period based on battery mode
      final period = _isBatterySaverMode ? _batterySaverPeriod : _normalPeriod;
      _samplingPeriod = period;

      // Start gyroscope
      _gyroscopeSubscription = gyroscopeEventStream(
        samplingPeriod: period,
      ).listen(_handleGyroscopeEvent, onError: _handleSensorError);

      // Start accelerometer
      _accelerometerSubscription = accelerometerEventStream(
        samplingPeriod: period,
      ).listen(_handleAccelerometerEvent, onError: _handleSensorError);

      debugPrint('✅ MotionService: Sensors started successfully');
    } catch (e) {
      debugPrint('❌ MotionService: Failed to start sensors: $e');
      _isActive = false;
    }
  }

  /// Stop the motion service
  /// إيقاف خدمة الحركة
  Future<void> stop() async {
    if (!_isActive) return;

    _isActive = false;
    debugPrint('🛑 MotionService: Stopping sensors...');

    await _gyroscopeSubscription?.cancel();
    await _accelerometerSubscription?.cancel();

    _gyroscopeSubscription = null;
    _accelerometerSubscription = null;

    // Reset filters
    _tiltXFilter.reset();
    _tiltYFilter.reset();
    _rotationZFilter.reset();
    _accelMagFilter.reset();

    _currentData = MotionData.zero;
    notifyListeners();

    debugPrint('✅ MotionService: Sensors stopped');
  }

  /// Pause sensor readings (for background)
  /// إيقاف القراءات مؤقتاً
  void pause() {
    _gyroscopeSubscription?.pause();
    _accelerometerSubscription?.pause();
  }

  /// Resume sensor readings
  /// استئناف القراءات
  void resume() {
    _gyroscopeSubscription?.resume();
    _accelerometerSubscription?.resume();
  }

  /// Set battery saver mode
  /// تفعيل وضع توفير البطارية
  Future<void> setBatterySaverMode(bool enabled) async {
    if (_isBatterySaverMode == enabled) return;

    _isBatterySaverMode = enabled;

    // Restart with new sampling period if active
    if (_isActive) {
      await stop();
      await start();
    }

    debugPrint('🔋 MotionService: Battery saver mode: $enabled');
  }

  /// Set motion sensitivity (0.1 to 2.0)
  /// ضبط حساسية الحركة
  void setSensitivity(double sensitivity) {
    _sensitivity = sensitivity.clamp(0.1, 2.0);
    debugPrint('⚙️ MotionService: Sensitivity set to $_sensitivity');
  }

  /// Add shake listener
  /// إضافة مستمع للاهتزاز
  void addShakeListener(Function() listener) {
    _shakeListeners.add(listener);
  }

  /// Remove shake listener
  void removeShakeListener(Function() listener) {
    _shakeListeners.remove(listener);
  }

  /// Handle gyroscope event
  void _handleGyroscopeEvent(GyroscopeEvent event) {
    _lastGyroscope = Vector3(event.x, event.y, event.z);
    _updateMotionData();
  }

  /// Handle accelerometer event
  void _handleAccelerometerEvent(AccelerometerEvent event) {
    _lastAccelerometer = Vector3(event.x, event.y, event.z);
    _detectShake();
    _updateMotionData();
  }

  /// Handle sensor errors
  void _handleSensorError(dynamic error) {
    debugPrint('⚠️ MotionService: Sensor error: $error');
  }

  /// Update motion data with smoothing
  void _updateMotionData() {
    final accel = _lastAccelerometer;
    final gyro = _lastGyroscope;

    // Calculate tilt from accelerometer (gravity vector)
    // Normalize to -1.0 to 1.0 range
    final gravity = 9.81;

    // Tilt X: Roll (left-right tilt)
    final rawTiltX = (accel.x / gravity).clamp(-1.0, 1.0);
    final tiltX = _tiltXFilter.filter(rawTiltX * _sensitivity);

    // Tilt Y: Pitch (forward-backward tilt)
    final rawTiltY = (accel.y / gravity).clamp(-1.0, 1.0);
    final tiltY = _tiltYFilter.filter(rawTiltY * _sensitivity);

    // Rotation Z from gyroscope
    final rotationZ = _rotationZFilter.filter(gyro.z * _sensitivity);

    // Acceleration magnitude (excluding gravity)
    final accelMag = math.sqrt(accel.x * accel.x + accel.y * accel.y + accel.z * accel.z);
    final normalizedAccel = (accelMag - gravity).abs() / gravity;
    final filteredAccelMag = _accelMagFilter.add(normalizedAccel);

    // Angular velocity magnitude
    final angularVelocity = gyro.magnitude;

    // Stability detection
    _updateStability(filteredAccelMag);
    final isStable = _isDeviceStable();

    // Create new motion data
    _currentData = MotionData(
      tiltX: tiltX.clamp(-1.0, 1.0),
      tiltY: tiltY.clamp(-1.0, 1.0),
      rotationZ: rotationZ.clamp(-1.0, 1.0),
      accelerationMagnitude: filteredAccelMag.clamp(0.0, 2.0),
      angularVelocity: angularVelocity,
      isStable: isStable,
      gyroscope: gyro,
      accelerometer: accel,
      timestamp: DateTime.now(),
    );

    // Notify listeners
    _motionController.add(_currentData);
    notifyListeners();
  }

  /// Update stability tracking
  void _updateStability(double magnitude) {
    _recentAccelMagnitudes.add(magnitude);
    if (_recentAccelMagnitudes.length > _stabilityWindowSize) {
      _recentAccelMagnitudes.removeAt(0);
    }
  }

  /// Check if device is stable
  bool _isDeviceStable() {
    if (_recentAccelMagnitudes.length < _stabilityWindowSize) return true;

    final variance = _calculateVariance(_recentAccelMagnitudes);
    return variance < _stabilityThreshold;
  }

  /// Calculate variance of a list of values
  double _calculateVariance(List<double> values) {
    if (values.isEmpty) return 0.0;

    final mean = values.reduce((a, b) => a + b) / values.length;
    final squaredDiffs = values.map((v) => math.pow(v - mean, 2));
    return squaredDiffs.reduce((a, b) => a + b) / values.length;
  }

  /// Detect shake gestures
  void _detectShake() {
    final accel = _lastAccelerometer;
    final magnitude = accel.magnitude;

    // Shake threshold (approximately 2.5g)
    const shakeThreshold = 25.0;
    const shakeCooldown = Duration(milliseconds: 500);

    final now = DateTime.now();
    final timeSinceLastShake = now.difference(_lastShakeTime);

    if (magnitude > shakeThreshold &&
        _lastShakeMagnitude <= shakeThreshold &&
        timeSinceLastShake > shakeCooldown) {
      _lastShakeTime = now;
      debugPrint('📳 MotionService: Shake detected!');

      // Notify shake listeners
      for (final listener in _shakeListeners) {
        listener();
      }
    }

    _lastShakeMagnitude = magnitude;
  }

  /// Calibrate sensors (reset filters to current position as zero)
  /// معايرة المستشعرات
  void calibrate() {
    _tiltXFilter.reset();
    _tiltYFilter.reset();
    _rotationZFilter.reset();
    _accelMagFilter.reset();
    _recentAccelMagnitudes.clear();

    debugPrint('🎯 MotionService: Calibrated');
  }

  @override
  void dispose() {
    stop();
    _motionController.close();
    super.dispose();
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// UTILITY EXTENSIONS
// ─────────────────────────────────────────────────────────────────────────────

/// Extension for easier motion data usage
extension MotionDataExtension on MotionData {
  /// Get tilt as Offset (for parallax effects)
  Offset toOffset() => Offset(tiltX, tiltY);

  /// Get tilt magnitude (0.0 to ~1.41)
  double get tiltMagnitude => math.sqrt(tiltX * tiltX + tiltY * tiltY);

  /// Get tilt angle in radians
  double get tiltAngle => math.atan2(tiltY, tiltX);

  /// Check if tilted significantly
  bool get isTilted => tiltMagnitude > 0.1;

  /// Interpolate between two motion data
  MotionData lerp(MotionData other, double t) {
    return MotionData(
      tiltX: _lerpDouble(tiltX, other.tiltX, t),
      tiltY: _lerpDouble(tiltY, other.tiltY, t),
      rotationZ: _lerpDouble(rotationZ, other.rotationZ, t),
      accelerationMagnitude:
          _lerpDouble(accelerationMagnitude, other.accelerationMagnitude, t),
      angularVelocity: _lerpDouble(angularVelocity, other.angularVelocity, t),
      isStable: t < 0.5 ? isStable : other.isStable,
      gyroscope: gyroscope,
      accelerometer: accelerometer,
      timestamp: timestamp,
    );
  }

  double _lerpDouble(double a, double b, double t) => a + (b - a) * t;
}

/// Offset extension for motion
extension OffsetExtension on Offset {
  /// Create from motion data
  static Offset fromMotionData(MotionData data) => Offset(data.tiltX, data.tiltY);
}
