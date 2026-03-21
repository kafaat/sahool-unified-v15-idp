// ═══════════════════════════════════════════════════════════════════════════
// SAHOOL - Motion Preferences
// تفضيلات الحركة - للإمكانية والوصول وتوفير البطارية
// ═══════════════════════════════════════════════════════════════════════════

import 'dart:async';
import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'motion_service.dart';
import 'parallax_controller.dart';
import 'tilt_effect.dart';

// ─────────────────────────────────────────────────────────────────────────────
// MOTION PREFERENCES MODEL
// ─────────────────────────────────────────────────────────────────────────────

/// User preferences for motion effects
/// تفضيلات المستخدم لتأثيرات الحركة
class MotionPreferences {
  /// Whether motion effects are globally enabled
  final bool motionEffectsEnabled;

  /// Reduce motion for accessibility (lower intensity, fewer effects)
  final bool reduceMotion;

  /// Battery saver mode (lower sampling rate)
  final bool batterySaverMode;

  /// Global intensity multiplier (0.0 to 1.0)
  final double intensityMultiplier;

  /// Enable parallax effects
  final bool enableParallax;

  /// Enable tilt effects
  final bool enableTilt;

  /// Enable float effects
  final bool enableFloat;

  /// Enable shake detection
  final bool enableShakeDetection;

  /// Enable wave effects
  final bool enableWave;

  /// Enable haptic feedback on motion events
  final bool enableHaptics;

  /// Maximum sensor sampling rate (Hz)
  final int maxSamplingRate;

  /// Whether to respect system reduced motion setting
  final bool respectSystemReducedMotion;

  const MotionPreferences({
    this.motionEffectsEnabled = true,
    this.reduceMotion = false,
    this.batterySaverMode = false,
    this.intensityMultiplier = 1.0,
    this.enableParallax = true,
    this.enableTilt = true,
    this.enableFloat = true,
    this.enableShakeDetection = true,
    this.enableWave = true,
    this.enableHaptics = true,
    this.maxSamplingRate = 60,
    this.respectSystemReducedMotion = true,
  });

  /// Default preferences
  static const MotionPreferences defaultPreferences = MotionPreferences();

  /// Accessibility-friendly preferences
  static const MotionPreferences accessibility = MotionPreferences(
    reduceMotion: true,
    intensityMultiplier: 0.3,
    enableWave: false,
    enableFloat: false,
    maxSamplingRate: 30,
  );

  /// Battery saver preferences
  static const MotionPreferences batterySaver = MotionPreferences(
    batterySaverMode: true,
    intensityMultiplier: 0.5,
    enableWave: false,
    maxSamplingRate: 20,
  );

  /// Disabled preferences
  static const MotionPreferences disabled = MotionPreferences(
    motionEffectsEnabled: false,
    enableParallax: false,
    enableTilt: false,
    enableFloat: false,
    enableShakeDetection: false,
    enableWave: false,
  );

  /// Check if effects should be active
  bool get isEffectivelyEnabled =>
      motionEffectsEnabled && intensityMultiplier > 0;

  /// Get effective intensity based on settings
  double get effectiveIntensity {
    if (!motionEffectsEnabled) return 0.0;
    if (reduceMotion) return intensityMultiplier * 0.3;
    return intensityMultiplier;
  }

  /// Get ParallaxConfig based on preferences
  ParallaxConfig toParallaxConfig() {
    if (!enableParallax || !isEffectivelyEnabled) {
      return ParallaxConfig.defaultConfig.copyWith(enabled: false);
    }

    if (reduceMotion) {
      return ParallaxConfig.reducedMotion.copyWith(
        sensitivity: effectiveIntensity,
      );
    }

    return ParallaxConfig.defaultConfig.copyWith(
      sensitivity: effectiveIntensity,
      smoothing: batterySaverMode ? 0.1 : 0.15,
    );
  }

  /// Get TiltConfig based on preferences
  TiltConfig toTiltConfig() {
    if (!enableTilt || !isEffectivelyEnabled) {
      return TiltConfig.defaultConfig.copyWith(enabled: false);
    }

    if (reduceMotion) {
      return TiltConfig.reducedMotion;
    }

    return TiltConfig.defaultConfig.copyWith(
      maxTiltX: 15.0 * effectiveIntensity,
      maxTiltY: 15.0 * effectiveIntensity,
      enableGlare: !batterySaverMode,
    );
  }

  /// Create a copy with modifications
  MotionPreferences copyWith({
    bool? motionEffectsEnabled,
    bool? reduceMotion,
    bool? batterySaverMode,
    double? intensityMultiplier,
    bool? enableParallax,
    bool? enableTilt,
    bool? enableFloat,
    bool? enableShakeDetection,
    bool? enableWave,
    bool? enableHaptics,
    int? maxSamplingRate,
    bool? respectSystemReducedMotion,
  }) {
    return MotionPreferences(
      motionEffectsEnabled: motionEffectsEnabled ?? this.motionEffectsEnabled,
      reduceMotion: reduceMotion ?? this.reduceMotion,
      batterySaverMode: batterySaverMode ?? this.batterySaverMode,
      intensityMultiplier: intensityMultiplier ?? this.intensityMultiplier,
      enableParallax: enableParallax ?? this.enableParallax,
      enableTilt: enableTilt ?? this.enableTilt,
      enableFloat: enableFloat ?? this.enableFloat,
      enableShakeDetection: enableShakeDetection ?? this.enableShakeDetection,
      enableWave: enableWave ?? this.enableWave,
      enableHaptics: enableHaptics ?? this.enableHaptics,
      maxSamplingRate: maxSamplingRate ?? this.maxSamplingRate,
      respectSystemReducedMotion:
          respectSystemReducedMotion ?? this.respectSystemReducedMotion,
    );
  }

  /// Convert to JSON
  Map<String, dynamic> toJson() {
    return {
      'motionEffectsEnabled': motionEffectsEnabled,
      'reduceMotion': reduceMotion,
      'batterySaverMode': batterySaverMode,
      'intensityMultiplier': intensityMultiplier,
      'enableParallax': enableParallax,
      'enableTilt': enableTilt,
      'enableFloat': enableFloat,
      'enableShakeDetection': enableShakeDetection,
      'enableWave': enableWave,
      'enableHaptics': enableHaptics,
      'maxSamplingRate': maxSamplingRate,
      'respectSystemReducedMotion': respectSystemReducedMotion,
    };
  }

  /// Create from JSON
  factory MotionPreferences.fromJson(Map<String, dynamic> json) {
    return MotionPreferences(
      motionEffectsEnabled: (json['motionEffectsEnabled'] as bool?) ?? true,
      reduceMotion: (json['reduceMotion'] as bool?) ?? false,
      batterySaverMode: (json['batterySaverMode'] as bool?) ?? false,
      intensityMultiplier: ((json['intensityMultiplier'] as num?) ?? 1.0).toDouble(),
      enableParallax: (json['enableParallax'] as bool?) ?? true,
      enableTilt: (json['enableTilt'] as bool?) ?? true,
      enableFloat: (json['enableFloat'] as bool?) ?? true,
      enableShakeDetection: (json['enableShakeDetection'] as bool?) ?? true,
      enableWave: (json['enableWave'] as bool?) ?? true,
      enableHaptics: (json['enableHaptics'] as bool?) ?? true,
      maxSamplingRate: (json['maxSamplingRate'] as int?) ?? 60,
      respectSystemReducedMotion: (json['respectSystemReducedMotion'] as bool?) ?? true,
    );
  }

  @override
  bool operator ==(Object other) =>
      identical(this, other) ||
      other is MotionPreferences &&
          runtimeType == other.runtimeType &&
          motionEffectsEnabled == other.motionEffectsEnabled &&
          reduceMotion == other.reduceMotion &&
          batterySaverMode == other.batterySaverMode &&
          intensityMultiplier == other.intensityMultiplier &&
          enableParallax == other.enableParallax &&
          enableTilt == other.enableTilt &&
          enableFloat == other.enableFloat &&
          enableShakeDetection == other.enableShakeDetection &&
          enableWave == other.enableWave &&
          enableHaptics == other.enableHaptics &&
          maxSamplingRate == other.maxSamplingRate &&
          respectSystemReducedMotion == other.respectSystemReducedMotion;

  @override
  int get hashCode =>
      motionEffectsEnabled.hashCode ^
      reduceMotion.hashCode ^
      batterySaverMode.hashCode ^
      intensityMultiplier.hashCode ^
      enableParallax.hashCode ^
      enableTilt.hashCode ^
      enableFloat.hashCode ^
      enableShakeDetection.hashCode ^
      enableWave.hashCode ^
      enableHaptics.hashCode ^
      maxSamplingRate.hashCode ^
      respectSystemReducedMotion.hashCode;
}

// ─────────────────────────────────────────────────────────────────────────────
// MOTION PREFERENCES SERVICE
// ─────────────────────────────────────────────────────────────────────────────

/// Service for managing motion preferences
/// خدمة إدارة تفضيلات الحركة
class MotionPreferencesService extends ChangeNotifier {
  static const _prefsKey = 'motion_preferences';
  static MotionPreferencesService? _instance;

  /// Singleton instance
  static MotionPreferencesService get instance {
    _instance ??= MotionPreferencesService._();
    return _instance!;
  }

  MotionPreferencesService._();

  SharedPreferences? _sharedPrefs;
  MotionPreferences _preferences = MotionPreferences.defaultPreferences;
  bool _initialized = false;

  /// Current preferences
  MotionPreferences get preferences => _preferences;

  /// Whether service is initialized
  bool get isInitialized => _initialized;

  /// Initialize the service
  Future<void> initialize() async {
    if (_initialized) return;

    _sharedPrefs = await SharedPreferences.getInstance();
    await _loadPreferences();
    await _checkSystemReducedMotion();

    _initialized = true;
    debugPrint('✅ MotionPreferencesService: Initialized');
  }

  /// Load preferences from storage
  Future<void> _loadPreferences() async {
    final json = _sharedPrefs?.getString(_prefsKey);
    if (json != null) {
      try {
        _preferences = MotionPreferences.fromJson(
          jsonDecode(json) as Map<String, dynamic>,
        );
      } catch (e) {
        debugPrint('❌ MotionPreferencesService: Failed to load: $e');
        _preferences = MotionPreferences.defaultPreferences;
      }
    }
  }

  /// Check system accessibility settings
  Future<void> _checkSystemReducedMotion() async {
    if (!_preferences.respectSystemReducedMotion) return;

    try {
      // Check platform accessibility settings
      final binding = WidgetsBinding.instance;
      final isReducedMotion = binding.platformDispatcher.accessibilityFeatures.reduceMotion;

      if (isReducedMotion && !_preferences.reduceMotion) {
        _preferences = _preferences.copyWith(reduceMotion: true);
        await _savePreferences();
        debugPrint('⚠️ MotionPreferencesService: System reduced motion detected');
      }
    } catch (e) {
      debugPrint('⚠️ MotionPreferencesService: Could not check system settings: $e');
    }
  }

  /// Save preferences to storage
  Future<void> _savePreferences() async {
    if (_sharedPrefs == null) {
      await initialize();
    }

    await _sharedPrefs?.setString(_prefsKey, jsonEncode(_preferences.toJson()));
    notifyListeners();
    debugPrint('✅ MotionPreferencesService: Preferences saved');
  }

  /// Update preferences
  Future<void> updatePreferences(MotionPreferences preferences) async {
    _preferences = preferences;
    await _savePreferences();

    // Apply to motion service
    _applyToMotionService();
  }

  /// Update a single preference
  Future<void> updatePreference(
    MotionPreferences Function(MotionPreferences) update,
  ) async {
    _preferences = update(_preferences);
    await _savePreferences();
    _applyToMotionService();
  }

  /// Apply preferences to motion service
  void _applyToMotionService() {
    final motionService = MotionService.instance;

    // Set battery saver mode
    motionService.setBatterySaverMode(_preferences.batterySaverMode);

    // Set sensitivity
    motionService.setSensitivity(_preferences.effectiveIntensity);
  }

  /// Enable motion effects
  Future<void> enableMotionEffects() async {
    await updatePreference((prefs) => prefs.copyWith(motionEffectsEnabled: true));
  }

  /// Disable motion effects
  Future<void> disableMotionEffects() async {
    await updatePreference((prefs) => prefs.copyWith(motionEffectsEnabled: false));
  }

  /// Enable reduced motion mode
  Future<void> enableReducedMotion() async {
    await updatePreference((prefs) => prefs.copyWith(
      reduceMotion: true,
      intensityMultiplier: 0.3,
    ));
  }

  /// Disable reduced motion mode
  Future<void> disableReducedMotion() async {
    await updatePreference((prefs) => prefs.copyWith(
      reduceMotion: false,
      intensityMultiplier: 1.0,
    ));
  }

  /// Enable battery saver mode
  Future<void> enableBatterySaver() async {
    await updatePreference((prefs) => prefs.copyWith(batterySaverMode: true));
  }

  /// Disable battery saver mode
  Future<void> disableBatterySaver() async {
    await updatePreference((prefs) => prefs.copyWith(batterySaverMode: false));
  }

  /// Set intensity
  Future<void> setIntensity(double intensity) async {
    await updatePreference((prefs) => prefs.copyWith(
      intensityMultiplier: intensity.clamp(0.0, 1.0),
    ));
  }

  /// Reset to defaults
  Future<void> resetToDefaults() async {
    await updatePreferences(MotionPreferences.defaultPreferences);
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// MOTION PREFERENCES SCREEN
// ─────────────────────────────────────────────────────────────────────────────

/// Settings screen for motion preferences
/// شاشة إعدادات تفضيلات الحركة
class MotionPreferencesScreen extends StatefulWidget {
  const MotionPreferencesScreen({super.key});

  @override
  State<MotionPreferencesScreen> createState() =>
      _MotionPreferencesScreenState();
}

class _MotionPreferencesScreenState extends State<MotionPreferencesScreen> {
  late MotionPreferences _prefs;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _loadPreferences();
  }

  Future<void> _loadPreferences() async {
    final service = MotionPreferencesService.instance;
    if (!service.isInitialized) {
      await service.initialize();
    }

    setState(() {
      _prefs = service.preferences;
      _loading = false;
    });
  }

  Future<void> _updatePreferences() async {
    await MotionPreferencesService.instance.updatePreferences(_prefs);
    if (mounted) {
      // Provide haptic feedback if enabled
      if (_prefs.enableHaptics) {
        unawaited(HapticFeedback.lightImpact());
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('تأثيرات الحركة'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () async {
              await MotionPreferencesService.instance.resetToDefaults();
              await _loadPreferences();
            },
            tooltip: 'إعادة تعيين',
          ),
        ],
      ),
      body: ListView(
        children: [
          // Main toggle
          _buildSectionHeader('عام'),
          SwitchListTile(
            title: const Text('تفعيل تأثيرات الحركة'),
            subtitle: const Text('التحكم العام في جميع تأثيرات الحركة'),
            secondary: const Icon(Icons.motion_photos_on),
            value: _prefs.motionEffectsEnabled,
            onChanged: (value) {
              setState(() {
                _prefs = _prefs.copyWith(motionEffectsEnabled: value);
              });
              _updatePreferences();
            },
          ),

          // Accessibility
          const Divider(),
          _buildSectionHeader('إمكانية الوصول'),
          SwitchListTile(
            title: const Text('تقليل الحركة'),
            subtitle: const Text('تقليل الحركة للأشخاص الحساسين للحركة'),
            secondary: const Icon(Icons.accessibility_new),
            value: _prefs.reduceMotion,
            onChanged: _prefs.motionEffectsEnabled
                ? (value) {
                    setState(() {
                      _prefs = _prefs.copyWith(
                        reduceMotion: value,
                        intensityMultiplier: value ? 0.3 : 1.0,
                      );
                    });
                    _updatePreferences();
                  }
                : null,
          ),
          ListTile(
            title: const Text('شدة التأثيرات'),
            subtitle: Text('${(_prefs.intensityMultiplier * 100).round()}%'),
            leading: const Icon(Icons.tune),
            trailing: SizedBox(
              width: 150,
              child: Slider(
                value: _prefs.intensityMultiplier,
                min: 0.0,
                max: 1.0,
                divisions: 10,
                onChanged: _prefs.motionEffectsEnabled && !_prefs.reduceMotion
                    ? (value) {
                        setState(() {
                          _prefs = _prefs.copyWith(intensityMultiplier: value);
                        });
                        _updatePreferences();
                      }
                    : null,
              ),
            ),
          ),

          // Battery
          const Divider(),
          _buildSectionHeader('البطارية'),
          SwitchListTile(
            title: const Text('وضع توفير البطارية'),
            subtitle: const Text('تقليل معدل استشعار الحركة'),
            secondary: const Icon(Icons.battery_saver),
            value: _prefs.batterySaverMode,
            onChanged: _prefs.motionEffectsEnabled
                ? (value) {
                    setState(() {
                      _prefs = _prefs.copyWith(batterySaverMode: value);
                    });
                    _updatePreferences();
                  }
                : null,
          ),

          // Effect types
          const Divider(),
          _buildSectionHeader('أنواع التأثيرات'),
          SwitchListTile(
            title: const Text('تأثير المنظور'),
            subtitle: const Text('حركة الخلفية والطبقات'),
            secondary: const Icon(Icons.layers),
            value: _prefs.enableParallax,
            onChanged: _prefs.motionEffectsEnabled
                ? (value) {
                    setState(() {
                      _prefs = _prefs.copyWith(enableParallax: value);
                    });
                    _updatePreferences();
                  }
                : null,
          ),
          SwitchListTile(
            title: const Text('تأثير الميلان'),
            subtitle: const Text('ميلان ثلاثي الأبعاد للبطاقات'),
            secondary: const Icon(Icons.view_in_ar),
            value: _prefs.enableTilt,
            onChanged: _prefs.motionEffectsEnabled
                ? (value) {
                    setState(() {
                      _prefs = _prefs.copyWith(enableTilt: value);
                    });
                    _updatePreferences();
                  }
                : null,
          ),
          SwitchListTile(
            title: const Text('تأثير الطفو'),
            subtitle: const Text('حركة طفو لطيفة للعناصر'),
            secondary: const Icon(Icons.bubble_chart),
            value: _prefs.enableFloat,
            onChanged: _prefs.motionEffectsEnabled
                ? (value) {
                    setState(() {
                      _prefs = _prefs.copyWith(enableFloat: value);
                    });
                    _updatePreferences();
                  }
                : null,
          ),
          SwitchListTile(
            title: const Text('تأثير الموجة'),
            subtitle: const Text('حركة موجية للقوائم'),
            secondary: const Icon(Icons.waves),
            value: _prefs.enableWave,
            onChanged: _prefs.motionEffectsEnabled
                ? (value) {
                    setState(() {
                      _prefs = _prefs.copyWith(enableWave: value);
                    });
                    _updatePreferences();
                  }
                : null,
          ),
          SwitchListTile(
            title: const Text('كشف الاهتزاز'),
            subtitle: const Text('الاهتزاز للتحديث والإجراءات'),
            secondary: const Icon(Icons.vibration),
            value: _prefs.enableShakeDetection,
            onChanged: _prefs.motionEffectsEnabled
                ? (value) {
                    setState(() {
                      _prefs = _prefs.copyWith(enableShakeDetection: value);
                    });
                    _updatePreferences();
                  }
                : null,
          ),

          // Feedback
          const Divider(),
          _buildSectionHeader('التغذية الراجعة'),
          SwitchListTile(
            title: const Text('ردود فعل لمسية'),
            subtitle: const Text('اهتزاز خفيف عند التفاعل'),
            secondary: const Icon(Icons.touch_app),
            value: _prefs.enableHaptics,
            onChanged: (value) {
              setState(() {
                _prefs = _prefs.copyWith(enableHaptics: value);
              });
              _updatePreferences();
            },
          ),

          const SizedBox(height: 32),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Text(
        title,
        style: Theme.of(context).textTheme.titleMedium?.copyWith(
              fontWeight: FontWeight.bold,
              color: Theme.of(context).primaryColor,
            ),
      ),
    );
  }
}

// ─────────────────────────────────────────────────────────────────────────────
// MOTION AWARE WIDGET
// ─────────────────────────────────────────────────────────────────────────────

/// Widget that automatically adapts based on motion preferences
/// ودجة تتكيف تلقائياً مع تفضيلات الحركة
class MotionAware extends StatelessWidget {
  /// Child widget with motion effects
  final Widget Function(BuildContext context, MotionPreferences prefs) builder;

  /// Fallback child when motion is disabled
  final Widget? fallback;

  const MotionAware({
    super.key,
    required this.builder,
    this.fallback,
  });

  @override
  Widget build(BuildContext context) {
    return ListenableBuilder(
      listenable: MotionPreferencesService.instance,
      builder: (context, _) {
        final prefs = MotionPreferencesService.instance.preferences;

        if (!prefs.motionEffectsEnabled && fallback != null) {
          return fallback!;
        }

        return builder(context, prefs);
      },
    );
  }
}
