import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../utils/app_logger.dart';

/// SAHOOL Onboarding Service
/// خدمة التعريف بالتطبيق
///
/// Manages the interactive onboarding flow:
/// - Feature tour / walkthrough tracking
/// - First field setup progress
/// - IoT device pairing status
/// - Completion persistence

// ═══════════════════════════════════════════════════════════════════════════
// Onboarding Steps
// ═══════════════════════════════════════════════════════════════════════════

/// Steps in the onboarding flow
enum OnboardingStep {
  /// Welcome screen and app introduction
  welcome,

  /// Feature tour walkthrough
  featureTour,

  /// Set up the first field (boundary, crop, area)
  fieldSetup,

  /// Configure notification preferences
  notificationSetup,

  /// Optional: IoT device pairing
  iotPairing,

  /// Onboarding complete
  completed,
}

/// Extension for OnboardingStep
extension OnboardingStepExtension on OnboardingStep {
  String get titleAr {
    switch (this) {
      case OnboardingStep.welcome:
        return 'مرحباً بك';
      case OnboardingStep.featureTour:
        return 'جولة في الميزات';
      case OnboardingStep.fieldSetup:
        return 'إعداد الحقل الأول';
      case OnboardingStep.notificationSetup:
        return 'إعداد الإشعارات';
      case OnboardingStep.iotPairing:
        return 'ربط أجهزة IoT';
      case OnboardingStep.completed:
        return 'مكتمل';
    }
  }

  String get titleEn {
    switch (this) {
      case OnboardingStep.welcome:
        return 'Welcome';
      case OnboardingStep.featureTour:
        return 'Feature Tour';
      case OnboardingStep.fieldSetup:
        return 'Field Setup';
      case OnboardingStep.notificationSetup:
        return 'Notification Setup';
      case OnboardingStep.iotPairing:
        return 'IoT Device Pairing';
      case OnboardingStep.completed:
        return 'Completed';
    }
  }

  String get descriptionAr {
    switch (this) {
      case OnboardingStep.welcome:
        return 'تعرف على منصة سهول الزراعية';
      case OnboardingStep.featureTour:
        return 'استكشف الميزات الرئيسية للتطبيق';
      case OnboardingStep.fieldSetup:
        return 'أضف حقلك الأول مع المحصول والمساحة';
      case OnboardingStep.notificationSetup:
        return 'اختر التنبيهات التي تهمك';
      case OnboardingStep.iotPairing:
        return 'اربط أجهزة الاستشعار مع التطبيق';
      case OnboardingStep.completed:
        return 'أنت جاهز لاستخدام سهول!';
    }
  }

  /// Whether this step is required (vs optional)
  bool get isRequired {
    switch (this) {
      case OnboardingStep.welcome:
      case OnboardingStep.featureTour:
      case OnboardingStep.fieldSetup:
      case OnboardingStep.completed:
        return true;
      case OnboardingStep.notificationSetup:
      case OnboardingStep.iotPairing:
        return false;
    }
  }

  /// Step index (0-based)
  int get stepIndex => OnboardingStep.values.indexOf(this);

  /// Total number of steps (excluding completed)
  static int get totalSteps => OnboardingStep.values.length - 1;
}

// ═══════════════════════════════════════════════════════════════════════════
// Onboarding State
// ═══════════════════════════════════════════════════════════════════════════

/// State of the onboarding flow
@immutable
class OnboardingState {
  /// Current step in the onboarding
  final OnboardingStep currentStep;

  /// Steps that have been completed
  final Set<OnboardingStep> completedSteps;

  /// Whether onboarding has been fully completed
  final bool isComplete;

  /// Whether onboarding was skipped
  final bool wasSkipped;

  /// First field ID (set during field setup)
  final String? firstFieldId;

  /// IoT device IDs (set during IoT pairing)
  final List<String> pairedDeviceIds;

  const OnboardingState({
    this.currentStep = OnboardingStep.welcome,
    this.completedSteps = const {},
    this.isComplete = false,
    this.wasSkipped = false,
    this.firstFieldId,
    this.pairedDeviceIds = const [],
  });

  /// Progress percentage (0.0 to 1.0)
  double get progress {
    if (isComplete) return 1.0;
    final total = OnboardingStepExtension.totalSteps;
    return total > 0 ? completedSteps.length / total : 0;
  }

  /// Progress as percentage string
  String get progressFormatted => '${(progress * 100).toStringAsFixed(0)}%';

  /// Number of completed steps
  int get completedCount => completedSteps.length;

  /// Number of remaining steps
  int get remainingCount =>
      OnboardingStepExtension.totalSteps - completedSteps.length;

  /// Whether the field setup step has been completed
  bool get hasSetupField => completedSteps.contains(OnboardingStep.fieldSetup);

  /// Whether IoT devices have been paired
  bool get hasIotDevices => pairedDeviceIds.isNotEmpty;

  OnboardingState copyWith({
    OnboardingStep? currentStep,
    Set<OnboardingStep>? completedSteps,
    bool? isComplete,
    bool? wasSkipped,
    String? firstFieldId,
    List<String>? pairedDeviceIds,
  }) {
    return OnboardingState(
      currentStep: currentStep ?? this.currentStep,
      completedSteps: completedSteps ?? this.completedSteps,
      isComplete: isComplete ?? this.isComplete,
      wasSkipped: wasSkipped ?? this.wasSkipped,
      firstFieldId: firstFieldId ?? this.firstFieldId,
      pairedDeviceIds: pairedDeviceIds ?? this.pairedDeviceIds,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Onboarding Service
// ═══════════════════════════════════════════════════════════════════════════

/// Manages onboarding flow and persistence
class OnboardingService {
  static const String _prefix = 'onboarding_';
  static const String _completedKey = '${_prefix}completed';
  static const String _skippedKey = '${_prefix}skipped';
  static const String _currentStepKey = '${_prefix}current_step';
  static const String _completedStepsKey = '${_prefix}completed_steps';
  static const String _firstFieldKey = '${_prefix}first_field_id';

  final SharedPreferences _prefs;

  OnboardingService(this._prefs);

  /// Check if onboarding has been completed
  bool get isCompleted => _prefs.getBool(_completedKey) ?? false;

  /// Check if onboarding was skipped
  bool get wasSkipped => _prefs.getBool(_skippedKey) ?? false;

  /// Get current state from preferences
  OnboardingState loadState() {
    final isComplete = _prefs.getBool(_completedKey) ?? false;
    final wasSkipped = _prefs.getBool(_skippedKey) ?? false;
    final stepIndex = _prefs.getInt(_currentStepKey) ?? 0;
    final completedList = _prefs.getStringList(_completedStepsKey) ?? [];
    final firstFieldId = _prefs.getString(_firstFieldKey);

    final completedSteps = completedList
        .map((s) => int.tryParse(s))
        .where((i) => i != null && i < OnboardingStep.values.length)
        .map((i) => OnboardingStep.values[i!])
        .toSet();

    final currentStep = stepIndex < OnboardingStep.values.length
        ? OnboardingStep.values[stepIndex]
        : OnboardingStep.welcome;

    return OnboardingState(
      currentStep: isComplete ? OnboardingStep.completed : currentStep,
      completedSteps: completedSteps,
      isComplete: isComplete,
      wasSkipped: wasSkipped,
      firstFieldId: firstFieldId,
    );
  }

  /// Save current state to preferences
  Future<void> saveState(OnboardingState state) async {
    await _prefs.setBool(_completedKey, state.isComplete);
    await _prefs.setBool(_skippedKey, state.wasSkipped);
    await _prefs.setInt(_currentStepKey, state.currentStep.index);
    await _prefs.setStringList(
      _completedStepsKey,
      state.completedSteps.map((s) => s.index.toString()).toList(),
    );
    if (state.firstFieldId != null) {
      await _prefs.setString(_firstFieldKey, state.firstFieldId!);
    }
  }

  /// Mark a step as completed
  Future<OnboardingState> completeStep(
    OnboardingState state,
    OnboardingStep step,
  ) async {
    final newCompleted = {...state.completedSteps, step};

    // Determine next step
    OnboardingStep nextStep;
    final stepIndex = step.index;
    if (stepIndex + 1 < OnboardingStep.values.length - 1) {
      nextStep = OnboardingStep.values[stepIndex + 1];
    } else {
      nextStep = OnboardingStep.completed;
    }

    // Check if all required steps are done
    final requiredSteps = OnboardingStep.values
        .where((s) => s.isRequired && s != OnboardingStep.completed);
    final allRequiredDone = requiredSteps.every(
      (s) => newCompleted.contains(s),
    );

    final newState = state.copyWith(
      currentStep: nextStep,
      completedSteps: newCompleted,
      isComplete: allRequiredDone,
    );

    await saveState(newState);
    AppLogger.i(
      'Onboarding step completed: ${step.titleEn}',
      tag: 'ONBOARDING',
    );

    return newState;
  }

  /// Skip the onboarding
  Future<OnboardingState> skip(OnboardingState state) async {
    final newState = state.copyWith(
      isComplete: true,
      wasSkipped: true,
      currentStep: OnboardingStep.completed,
    );
    await saveState(newState);
    AppLogger.i('Onboarding skipped', tag: 'ONBOARDING');
    return newState;
  }

  /// Reset onboarding (for testing/re-onboarding)
  Future<OnboardingState> reset() async {
    final keys = _prefs.getKeys().where((k) => k.startsWith(_prefix)).toList();
    for (final key in keys) {
      await _prefs.remove(key);
    }
    AppLogger.i('Onboarding reset', tag: 'ONBOARDING');
    return const OnboardingState();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Provider for the onboarding service
final onboardingServiceProvider =
    FutureProvider<OnboardingService>((ref) async {
  final prefs = await SharedPreferences.getInstance();
  return OnboardingService(prefs);
});

/// Provider for onboarding state
final onboardingStateProvider = FutureProvider<OnboardingState>((ref) async {
  final service = await ref.watch(onboardingServiceProvider.future);
  return service.loadState();
});

/// Provider to check if onboarding is needed
final needsOnboardingProvider = FutureProvider<bool>((ref) async {
  final service = await ref.watch(onboardingServiceProvider.future);
  return !service.isCompleted;
});
