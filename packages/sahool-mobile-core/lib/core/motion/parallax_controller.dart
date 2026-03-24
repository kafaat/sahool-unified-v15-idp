// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Parallax Controller
// متحكم تأثير المنظور - التحكم في شدة وإعدادات المنظور
// ═══════════════════════════════════════════════════════════════════════════

import 'dart:async';
import 'dart:ui';

import 'package:flutter/foundation.dart';

import 'motion_service.dart';

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX CONFIGURATION
// ─────────────────────────────────────────────────────────────────────────────

/// Configuration for parallax effect behavior
/// إعدادات سلوك تأثير المنظور
class ParallaxConfig {
  /// Maximum displacement in pixels
  final double maxDisplacement;

  /// Sensitivity multiplier (0.1 to 2.0)
  final double sensitivity;

  /// Smoothing factor (0.0 to 1.0, lower = smoother)
  final double smoothing;

  /// Whether to invert X axis
  final bool invertX;

  /// Whether to invert Y axis
  final bool invertY;

  /// Whether effect is enabled
  final bool enabled;

  /// Whether to use accelerometer (true) or gyroscope (false)
  final bool useAccelerometer;

  /// Dead zone threshold (ignore small movements)
  final double deadZone;

  const ParallaxConfig({
    this.maxDisplacement = 30.0,
    this.sensitivity = 1.0,
    this.smoothing = 0.15,
    this.invertX = false,
    this.invertY = false,
    this.enabled = true,
    this.useAccelerometer = true,
    this.deadZone = 0.02,
  });

  /// Default configuration
  static const ParallaxConfig defaultConfig = ParallaxConfig();

  /// Subtle configuration (minimal effect)
  static const ParallaxConfig subtle = ParallaxConfig(
    maxDisplacement: 15.0,
    sensitivity: 0.5,
    smoothing: 0.1,
  );

  /// Intense configuration (dramatic effect)
  static const ParallaxConfig intense = ParallaxConfig(
    maxDisplacement: 50.0,
    sensitivity: 1.5,
    smoothing: 0.2,
  );

  /// Reduced motion configuration (accessibility)
  static const ParallaxConfig reducedMotion = ParallaxConfig(
    maxDisplacement: 5.0,
    sensitivity: 0.3,
    smoothing: 0.05,
  );

  ParallaxConfig copyWith({
    double? maxDisplacement,
    double? sensitivity,
    double? smoothing,
    bool? invertX,
    bool? invertY,
    bool? enabled,
    bool? useAccelerometer,
    double? deadZone,
  }) {
    return ParallaxConfig(
      maxDisplacement: maxDisplacement ?? this.maxDisplacement,
      sensitivity: sensitivity ?? this.sensitivity,
      smoothing: smoothing ?? this.smoothing,
      invertX: invertX ?? this.invertX,
      invertY: invertY ?? this.invertY,
      enabled: enabled ?? this.enabled,
      useAccelerometer: useAccelerometer ?? this.useAccelerometer,
      deadZone: deadZone ?? this.deadZone,
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX OFFSET
// ─────────────────────────────────────────────────────────────────────────────

/// Calculated parallax offset values
/// قيم إزاحة المنظور المحسوبة
class ParallaxOffset {
  /// X offset in pixels
  final double x;

  /// Y offset in pixels
  final double y;

  /// Normalized X (-1.0 to 1.0)
  final double normalizedX;

  /// Normalized Y (-1.0 to 1.0)
  final double normalizedY;

  /// Whether the offset is significant
  final bool isActive;

  const ParallaxOffset({
    this.x = 0.0,
    this.y = 0.0,
    this.normalizedX = 0.0,
    this.normalizedY = 0.0,
    this.isActive = false,
  });

  /// Zero offset
  static const ParallaxOffset zero = ParallaxOffset();

  /// Convert to Offset
  Offset toOffset() => Offset(x, y);

  /// Scale the offset by a factor (for depth layers)
  ParallaxOffset scale(double factor) {
    return ParallaxOffset(
      x: x * factor,
      y: y * factor,
      normalizedX: normalizedX,
      normalizedY: normalizedY,
      isActive: isActive,
    );
  }

  /// Invert the offset
  ParallaxOffset invert({bool x = false, bool y = false}) {
    return ParallaxOffset(
      x: x ? -this.x : this.x,
      y: y ? -this.y : this.y,
      normalizedX: x ? -normalizedX : normalizedX,
      normalizedY: y ? -normalizedY : normalizedY,
      isActive: isActive,
    );
  }

  @override
  String toString() =>
      'ParallaxOffset(x: ${x.toStringAsFixed(1)}, y: ${y.toStringAsFixed(1)})';
}

// ─────────────────────────────────────────────────────────────────────────────
// PARALLAX CONTROLLER
// ─────────────────────────────────────────────────────────────────────────────

/// Controller for managing parallax effects across screens
/// متحكم إدارة تأثيرات المنظور عبر الشاشات
class ParallaxController extends ChangeNotifier {
  final MotionService _motionService;

  /// Current configuration
  ParallaxConfig _config;

  /// Current calculated offset
  ParallaxOffset _currentOffset = ParallaxOffset.zero;

  /// Smoothed offset values
  double _smoothedX = 0.0;
  double _smoothedY = 0.0;

  /// Whether controller is active
  bool _isActive = false;

  /// Screen-specific enabled states
  final Map<String, bool> _screenStates = {};

  /// Current screen identifier
  String? _currentScreen;

  /// Stream subscription
  StreamSubscription<MotionData>? _motionSubscription;

  /// Offset stream for widgets
  final _offsetController = StreamController<ParallaxOffset>.broadcast();

  ParallaxController({
    required MotionService motionService,
    ParallaxConfig config = ParallaxConfig.defaultConfig,
  })  : _motionService = motionService,
        _config = config;

  /// Current parallax offset
  ParallaxOffset get currentOffset => _currentOffset;

  /// Current configuration
  ParallaxConfig get config => _config;

  /// Whether controller is active
  bool get isActive => _isActive;

  /// Stream of parallax offsets
  Stream<ParallaxOffset> get offsetStream => _offsetController.stream;

  /// Start the parallax controller
  /// بدء متحكم المنظور
  Future<void> start() async {
    if (_isActive) return;

    _isActive = true;

    // Start motion service if not already running
    if (!_motionService.isActive) {
      await _motionService.start();
    }

    // Subscribe to motion data
    _motionSubscription = _motionService.motionStream.listen(_onMotionData);

    debugPrint('✅ ParallaxController: Started');
    notifyListeners();
  }

  /// Stop the parallax controller
  /// إيقاف متحكم المنظور
  Future<void> stop() async {
    if (!_isActive) return;

    _isActive = false;

    await _motionSubscription?.cancel();
    _motionSubscription = null;

    // Reset offset
    _currentOffset = ParallaxOffset.zero;
    _smoothedX = 0.0;
    _smoothedY = 0.0;

    _offsetController.add(_currentOffset);
    notifyListeners();

    debugPrint('🛑 ParallaxController: Stopped');
  }

  /// Update configuration
  /// تحديث الإعدادات
  void updateConfig(ParallaxConfig config) {
    _config = config;

    // Apply sensitivity to motion service
    _motionService.setSensitivity(config.sensitivity);

    notifyListeners();
    debugPrint('⚙️ ParallaxController: Config updated');
  }

  /// Set intensity (convenience method)
  /// ضبط الشدة
  void setIntensity(double intensity) {
    updateConfig(_config.copyWith(
      sensitivity: intensity.clamp(0.1, 2.0),
    ));
  }

  /// Set max displacement
  void setMaxDisplacement(double displacement) {
    updateConfig(_config.copyWith(
      maxDisplacement: displacement.clamp(5.0, 100.0),
    ));
  }

  /// Enable/disable for specific screen
  /// تفعيل/تعطيل لشاشة محددة
  void setEnabledForScreen(String screenId, bool enabled) {
    _screenStates[screenId] = enabled;
    debugPrint('📱 ParallaxController: Screen $screenId enabled: $enabled');
  }

  /// Check if enabled for current screen
  bool isEnabledForScreen(String screenId) {
    return _screenStates[screenId] ?? true;
  }

  /// Set current screen
  void setCurrentScreen(String? screenId) {
    _currentScreen = screenId;
  }

  /// Check if parallax should be active for current screen
  bool get isEffectivelyEnabled {
    if (!_config.enabled) return false;
    if (_currentScreen == null) return true;
    return isEnabledForScreen(_currentScreen!);
  }

  /// Reset position to center
  /// إعادة الموضع للمركز
  void resetPosition() {
    _smoothedX = 0.0;
    _smoothedY = 0.0;
    _currentOffset = ParallaxOffset.zero;
    _offsetController.add(_currentOffset);
    notifyListeners();

    debugPrint('🔄 ParallaxController: Position reset');
  }

  /// Calibrate (use current position as center)
  /// المعايرة
  void calibrate() {
    _motionService.calibrate();
    resetPosition();
  }

  /// Handle motion data
  void _onMotionData(MotionData data) {
    if (!_config.enabled || !isEffectivelyEnabled) {
      if (_currentOffset.isActive) {
        _currentOffset = ParallaxOffset.zero;
        _offsetController.add(_currentOffset);
        notifyListeners();
      }
      return;
    }

    // Get raw tilt values
    double rawX = data.tiltX;
    double rawY = data.tiltY;

    // Apply dead zone
    if (rawX.abs() < _config.deadZone) rawX = 0.0;
    if (rawY.abs() < _config.deadZone) rawY = 0.0;

    // Apply inversion
    if (_config.invertX) rawX = -rawX;
    if (_config.invertY) rawY = -rawY;

    // Apply smoothing (exponential moving average)
    _smoothedX = _smoothedX + (_config.smoothing * (rawX - _smoothedX));
    _smoothedY = _smoothedY + (_config.smoothing * (rawY - _smoothedY));

    // Calculate pixel offset
    final maxDisp = _config.maxDisplacement;
    final x = _smoothedX * maxDisp;
    final y = _smoothedY * maxDisp;

    // Create new offset
    _currentOffset = ParallaxOffset(
      x: x,
      y: y,
      normalizedX: _smoothedX,
      normalizedY: _smoothedY,
      isActive: _smoothedX.abs() > 0.01 || _smoothedY.abs() > 0.01,
    );

    _offsetController.add(_currentOffset);
    notifyListeners();
  }

  /// Get offset for a specific depth layer (0.0 = background, 1.0 = foreground)
  /// الحصول على الإزاحة لطبقة عمق محددة
  ParallaxOffset getOffsetForDepth(double depth) {
    // Depth factor: background moves more, foreground moves less (or opposite direction)
    // عامل العمق: الخلفية تتحرك أكثر، الواجهة تتحرك أقل
    final factor = 1.0 - (depth * 0.8); // Background (0) = 1.0x, Foreground (1) = 0.2x
    return _currentOffset.scale(factor);
  }

  /// Get offset with inverse depth (foreground moves more)
  /// الحصول على الإزاحة مع عمق معكوس
  ParallaxOffset getOffsetForDepthInverse(double depth) {
    final factor = 0.2 + (depth * 0.8); // Background (0) = 0.2x, Foreground (1) = 1.0x
    return _currentOffset.scale(factor).invert(x: true, y: true);
  }

  @override
  void dispose() {
    stop();
    _offsetController.close();
    super.dispose();
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// DEPTH LAYER PRESETS
// ─────────────────────────────────────────────────────────────────────────────

/// Predefined depth layers for parallax effects
/// طبقات العمق المحددة مسبقاً لتأثيرات المنظور
class ParallaxDepthLayers {
  /// Far background layer (moves most)
  static const double farBackground = 0.0;

  /// Mid background layer
  static const double midBackground = 0.25;

  /// Near background layer
  static const double nearBackground = 0.4;

  /// Content layer (default)
  static const double content = 0.5;

  /// Near foreground layer
  static const double nearForeground = 0.65;

  /// Mid foreground layer
  static const double midForeground = 0.8;

  /// Far foreground layer (moves least/opposite)
  static const double farForeground = 1.0;

  /// Get preset layers as a list (for building layered effects)
  static List<double> get allLayers => [
        farBackground,
        midBackground,
        nearBackground,
        content,
        nearForeground,
        midForeground,
        farForeground,
      ];

  /// Get standard 3-layer preset
  static List<double> get threeLayers => [
        farBackground,
        content,
        farForeground,
      ];

  /// Get 5-layer preset for rich effects
  static List<double> get fiveLayers => [
        farBackground,
        nearBackground,
        content,
        nearForeground,
        farForeground,
      ];
}
