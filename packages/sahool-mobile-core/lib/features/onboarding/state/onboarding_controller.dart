import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../domain/onboarding_step.dart';
import '../domain/onboarding_progress.dart';
import 'onboarding_providers.dart';

/// SAHOOL Onboarding Controller
/// متحكم الإعداد الأولي
///
/// Manages the onboarding flow state and transitions
/// يدير حالة تدفق الإعداد والانتقالات

class OnboardingController extends StateNotifier<OnboardingProgress> {
  final Ref _ref;
  SharedPreferences? _prefs;

  OnboardingController(this._ref) : super(const OnboardingProgress()) {
    _initialize();
  }

  /// Initialize the controller and load saved progress
  /// تهيئة المتحكم وتحميل التقدم المحفوظ
  Future<void> _initialize() async {
    _prefs = await SharedPreferences.getInstance();

    // Check if onboarding was already completed
    final completed = _prefs?.getBool('sahool_onboarding_completed') ?? false;
    if (completed) {
      state = state.copyWith(
        isCompleted: true,
        currentStep: OnboardingStepType.completion,
      );
      return;
    }

    // Try to load saved progress
    try {
      final savedProgress =
          await _ref.read(savedOnboardingProgressProvider.future);
      if (savedProgress != null) {
        state = savedProgress;
      }
    } catch (e) {
      // Start fresh if loading fails
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Navigation Methods
  // طرق التنقل
  // ═══════════════════════════════════════════════════════════════════════════

  /// Go to the next step in the onboarding flow
  /// الانتقال للخطوة التالية في تدفق الإعداد
  void nextStep() {
    final currentStep = state.currentStep;

    OnboardingStepType nextStep;
    switch (currentStep) {
      case OnboardingStepType.welcome:
        nextStep = OnboardingStepType.featuresTour;
        break;
      case OnboardingStepType.featuresTour:
        nextStep = OnboardingStepType.permissions;
        break;
      case OnboardingStepType.permissions:
        nextStep = OnboardingStepType.profileSetup;
        break;
      case OnboardingStepType.profileSetup:
        nextStep = OnboardingStepType.firstField;
        break;
      case OnboardingStepType.firstField:
        nextStep = OnboardingStepType.completion;
        break;
      case OnboardingStepType.completion:
        // Already at the end
        return;
    }

    state = state.copyWith(currentStep: nextStep);
    _saveProgress();
  }

  /// Go to the previous step
  /// الرجوع للخطوة السابقة
  void previousStep() {
    final currentStep = state.currentStep;

    OnboardingStepType previousStep;
    switch (currentStep) {
      case OnboardingStepType.welcome:
        // Already at the beginning
        return;
      case OnboardingStepType.featuresTour:
        previousStep = OnboardingStepType.welcome;
        break;
      case OnboardingStepType.permissions:
        previousStep = OnboardingStepType.featuresTour;
        break;
      case OnboardingStepType.profileSetup:
        previousStep = OnboardingStepType.permissions;
        break;
      case OnboardingStepType.firstField:
        previousStep = OnboardingStepType.profileSetup;
        break;
      case OnboardingStepType.completion:
        previousStep = OnboardingStepType.firstField;
        break;
    }

    state = state.copyWith(currentStep: previousStep);
    _saveProgress();
  }

  /// Go to a specific step
  /// الانتقال لخطوة محددة
  void goToStep(OnboardingStepType step) {
    state = state.copyWith(currentStep: step);
    _saveProgress();
  }

  /// Skip the entire onboarding
  /// تخطي الإعداد بالكامل
  Future<void> skipOnboarding() async {
    state = state.copyWith(
      isCompleted: true,
      wasSkipped: true,
      completedAt: DateTime.now(),
    );
    await _markCompleted();
  }

  /// Complete the onboarding
  /// إكمال الإعداد
  Future<void> completeOnboarding() async {
    state = state.copyWith(
      isCompleted: true,
      wasSkipped: false,
      completedAt: DateTime.now(),
      currentStep: OnboardingStepType.completion,
    );
    await _markCompleted();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Features Tour Methods
  // طرق جولة الميزات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Go to the next feature in the tour
  /// الانتقال للميزة التالية في الجولة
  void nextFeature() {
    final currentPage = state.featuresTourPage;
    if (currentPage < OnboardingProgress.totalFeaturesTourPages - 1) {
      state = state.copyWith(featuresTourPage: currentPage + 1);
      _saveProgress();
    } else {
      // Move to next step after last feature
      nextStep();
    }
  }

  /// Go to the previous feature in the tour
  /// الرجوع للميزة السابقة في الجولة
  void previousFeature() {
    final currentPage = state.featuresTourPage;
    if (currentPage > 0) {
      state = state.copyWith(featuresTourPage: currentPage - 1);
      _saveProgress();
    } else {
      // Move to previous step
      previousStep();
    }
  }

  /// Set features tour page directly
  /// تعيين صفحة جولة الميزات مباشرة
  void setFeaturesTourPage(int page) {
    if (page >= 0 && page < OnboardingProgress.totalFeaturesTourPages) {
      state = state.copyWith(featuresTourPage: page);
      _saveProgress();
    }
  }

  /// Skip the features tour
  /// تخطي جولة الميزات
  void skipFeaturesTour() {
    nextStep();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Permission Methods
  // طرق الأذونات
  // ═══════════════════════════════════════════════════════════════════════════

  /// Request a specific permission
  /// طلب إذن محدد
  Future<bool> requestPermission(String permissionId) async {
    bool granted = false;

    switch (permissionId) {
      case 'location':
        final status = await Permission.locationWhenInUse.request();
        granted = status.isGranted;
        break;
      case 'notifications':
        final status = await Permission.notification.request();
        granted = status.isGranted;
        break;
      case 'camera':
        final status = await Permission.camera.request();
        granted = status.isGranted;
        break;
    }

    // Update state
    final newPermissionStates = Map<String, bool>.from(state.permissionStates);
    newPermissionStates[permissionId] = granted;

    state = state.copyWith(permissionStates: newPermissionStates);
    _saveProgress();

    return granted;
  }

  /// Request all permissions
  /// طلب جميع الأذونات
  Future<void> requestAllPermissions() async {
    for (final permission in OnboardingPermissions.permissions) {
      await requestPermission(permission.id);
    }
  }

  /// Check current permission status
  /// فحص حالة الإذن الحالية
  Future<void> checkPermissionStatus(String permissionId) async {
    bool granted = false;

    switch (permissionId) {
      case 'location':
        granted = await Permission.locationWhenInUse.isGranted;
        break;
      case 'notifications':
        granted = await Permission.notification.isGranted;
        break;
      case 'camera':
        granted = await Permission.camera.isGranted;
        break;
    }

    final newPermissionStates = Map<String, bool>.from(state.permissionStates);
    newPermissionStates[permissionId] = granted;

    state = state.copyWith(permissionStates: newPermissionStates);
  }

  /// Check all permissions status
  /// فحص حالة جميع الأذونات
  Future<void> checkAllPermissionsStatus() async {
    for (final permission in OnboardingPermissions.permissions) {
      await checkPermissionStatus(permission.id);
    }
  }

  /// Skip permissions step
  /// تخطي خطوة الأذونات
  void skipPermissions() {
    nextStep();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Profile Methods
  // طرق الملف الشخصي
  // ═══════════════════════════════════════════════════════════════════════════

  /// Update user name
  /// تحديث اسم المستخدم
  void updateUserName(String name) {
    state = state.copyWith(
      profile: state.profile.copyWith(userName: name),
    );
    _saveProgress();
  }

  /// Update farm name
  /// تحديث اسم المزرعة
  void updateFarmName(String name) {
    state = state.copyWith(
      profile: state.profile.copyWith(farmName: name),
    );
    _saveProgress();
  }

  /// Update profile image
  /// تحديث صورة الملف الشخصي
  void updateProfileImage(String? imagePath) {
    state = state.copyWith(
      profile: state.profile.copyWith(profileImagePath: imagePath),
    );
    _saveProgress();
  }

  /// Save profile and move to next step
  /// حفظ الملف الشخصي والانتقال للخطوة التالية
  Future<void> saveProfile({
    required String userName,
    String? farmName,
  }) async {
    state = state.copyWith(
      profile: state.profile.copyWith(
        userName: userName,
        farmName: farmName,
      ),
    );
    _saveProgress();
    nextStep();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // First Field Methods
  // طرق الحقل الأول
  // ═══════════════════════════════════════════════════════════════════════════

  /// Update first field name
  /// تحديث اسم الحقل الأول
  void updateFirstFieldName(String name) {
    state = state.copyWith(
      firstField: state.firstField.copyWith(fieldName: name),
    );
    _saveProgress();
  }

  /// Update first field crop type
  /// تحديث نوع محصول الحقل الأول
  void updateFirstFieldCropType(String cropType) {
    state = state.copyWith(
      firstField: state.firstField.copyWith(cropType: cropType),
    );
    _saveProgress();
  }

  /// Save first field
  /// حفظ الحقل الأول
  Future<void> saveFirstField({
    required String fieldName,
    String? cropType,
    double? areaHectares,
  }) async {
    state = state.copyWith(
      firstField: state.firstField.copyWith(
        fieldName: fieldName,
        cropType: cropType,
        areaHectares: areaHectares,
        isCreated: true,
      ),
    );
    _saveProgress();
    nextStep();
  }

  /// Skip first field creation
  /// تخطي إنشاء الحقل الأول
  void skipFirstField() {
    state = state.copyWith(
      firstField: state.firstField.copyWith(isSkipped: true),
    );
    _saveProgress();
    nextStep();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Storage Methods
  // طرق التخزين
  // ═══════════════════════════════════════════════════════════════════════════

  /// Save current progress to local storage
  /// حفظ التقدم الحالي في التخزين المحلي
  Future<void> _saveProgress() async {
    if (_prefs != null) {
      await saveOnboardingProgress(_prefs!, state);
    }
  }

  /// Mark onboarding as completed
  /// تحديد الإعداد كمكتمل
  Future<void> _markCompleted() async {
    if (_prefs != null) {
      await markOnboardingCompleted(_prefs!);
      await _saveProgress();
    }
  }

  /// Reset onboarding progress
  /// إعادة تعيين تقدم الإعداد
  Future<void> resetProgress() async {
    if (_prefs != null) {
      await resetOnboarding(_prefs!);
    }
    state = const OnboardingProgress();
  }
}
