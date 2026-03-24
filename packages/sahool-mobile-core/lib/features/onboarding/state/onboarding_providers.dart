import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';

import '../domain/onboarding_step.dart';
import '../domain/onboarding_progress.dart';
import 'onboarding_controller.dart';

/// SAHOOL Onboarding Providers
/// مزودات الإعداد الأولي
///
/// Riverpod providers for onboarding state management
/// مزودات Riverpod لإدارة حالة الإعداد الأولي

// ═══════════════════════════════════════════════════════════════════════════
// Storage Key Constants
// ثوابت مفاتيح التخزين
// ═══════════════════════════════════════════════════════════════════════════

/// Key for storing onboarding completion status
const String _onboardingCompletedKey = 'sahool_onboarding_completed';

/// Key for storing onboarding progress
const String _onboardingProgressKey = 'sahool_onboarding_progress';

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// المزودات
// ═══════════════════════════════════════════════════════════════════════════

/// SharedPreferences provider
/// مزود SharedPreferences
final sharedPreferencesProvider = FutureProvider<SharedPreferences>((ref) async {
  return SharedPreferences.getInstance();
});

/// Provider to check if onboarding has been completed
/// مزود للتحقق من إكمال الإعداد الأولي
final onboardingCompletedProvider = FutureProvider<bool>((ref) async {
  final prefs = await ref.watch(sharedPreferencesProvider.future);
  return prefs.getBool(_onboardingCompletedKey) ?? false;
});

/// Provider for saved onboarding progress
/// مزود لتقدم الإعداد المحفوظ
final savedOnboardingProgressProvider =
    FutureProvider<OnboardingProgress?>((ref) async {
  final prefs = await ref.watch(sharedPreferencesProvider.future);
  final progressJson = prefs.getString(_onboardingProgressKey);

  if (progressJson == null) return null;

  try {
    final json = jsonDecode(progressJson) as Map<String, dynamic>;
    return OnboardingProgress.fromJson(json);
  } catch (e) {
    // If parsing fails, return null to start fresh
    return null;
  }
});

/// Main onboarding state notifier provider
/// مزود إدارة حالة الإعداد الرئيسي
final onboardingControllerProvider =
    StateNotifierProvider<OnboardingController, OnboardingProgress>((ref) {
  return OnboardingController(ref);
});

/// Current step provider (derived from controller)
/// مزود الخطوة الحالية
final currentOnboardingStepProvider = Provider<OnboardingStepType>((ref) {
  return ref.watch(onboardingControllerProvider).currentStep;
});

/// Features tour page provider
/// مزود صفحة جولة الميزات
final featuresTourPageProvider = Provider<int>((ref) {
  return ref.watch(onboardingControllerProvider).featuresTourPage;
});

/// Profile data provider
/// مزود بيانات الملف الشخصي
final onboardingProfileProvider = Provider<OnboardingProfile>((ref) {
  return ref.watch(onboardingControllerProvider).profile;
});

/// First field data provider
/// مزود بيانات الحقل الأول
final onboardingFirstFieldProvider = Provider<OnboardingFirstField>((ref) {
  return ref.watch(onboardingControllerProvider).firstField;
});

/// Permission states provider
/// مزود حالات الأذونات
final onboardingPermissionStatesProvider = Provider<Map<String, bool>>((ref) {
  return ref.watch(onboardingControllerProvider).permissionStates;
});

/// Progress percentage provider
/// مزود نسبة التقدم
final onboardingProgressPercentageProvider = Provider<double>((ref) {
  return ref.watch(onboardingControllerProvider).progressPercentage;
});

/// Is onboarding completed provider
/// مزود إكمال الإعداد
final isOnboardingCompletedProvider = Provider<bool>((ref) {
  return ref.watch(onboardingControllerProvider).isCompleted;
});

/// Current features list provider
/// مزود قائمة الميزات الحالية
final onboardingFeaturesProvider = Provider<List<OnboardingFeature>>((ref) {
  return OnboardingFeatures.features;
});

/// Current feature provider (based on tour page)
/// مزود الميزة الحالية
final currentFeatureProvider = Provider<OnboardingFeature?>((ref) {
  final features = ref.watch(onboardingFeaturesProvider);
  final currentPage = ref.watch(featuresTourPageProvider);

  if (currentPage >= 0 && currentPage < features.length) {
    return features[currentPage];
  }
  return null;
});

/// Permissions list provider
/// مزود قائمة الأذونات
final onboardingPermissionsListProvider =
    Provider<List<OnboardingPermission>>((ref) {
  final permissionStates = ref.watch(onboardingPermissionStatesProvider);

  return OnboardingPermissions.permissions.map((permission) {
    return permission.copyWith(
      isGranted: permissionStates[permission.id] ?? false,
    );
  }).toList();
});

/// All required permissions granted provider
/// مزود إكمال جميع الأذونات المطلوبة
final allRequiredPermissionsGrantedProvider = Provider<bool>((ref) {
  return ref.watch(onboardingControllerProvider).allRequiredPermissionsGranted;
});

/// Can proceed to next step provider
/// مزود إمكانية الانتقال للخطوة التالية
final canProceedToNextStepProvider = Provider<bool>((ref) {
  final progress = ref.watch(onboardingControllerProvider);

  switch (progress.currentStep) {
    case OnboardingStepType.welcome:
      return true;
    case OnboardingStepType.featuresTour:
      return true; // Can always proceed from features tour
    case OnboardingStepType.permissions:
      return progress.allRequiredPermissionsGranted;
    case OnboardingStepType.profileSetup:
      return progress.profile.isComplete;
    case OnboardingStepType.firstField:
      return true; // Can skip
    case OnboardingStepType.completion:
      return true;
  }
});

// ═══════════════════════════════════════════════════════════════════════════
// Storage Helper Functions
// دوال مساعدة للتخزين
// ═══════════════════════════════════════════════════════════════════════════

/// Save onboarding progress to local storage
/// حفظ تقدم الإعداد في التخزين المحلي
Future<void> saveOnboardingProgress(
  SharedPreferences prefs,
  OnboardingProgress progress,
) async {
  final json = jsonEncode(progress.toJson());
  await prefs.setString(_onboardingProgressKey, json);
}

/// Mark onboarding as completed
/// تحديد الإعداد كمكتمل
Future<void> markOnboardingCompleted(SharedPreferences prefs) async {
  await prefs.setBool(_onboardingCompletedKey, true);
}

/// Reset onboarding (for testing or re-onboarding)
/// إعادة تعيين الإعداد
Future<void> resetOnboarding(SharedPreferences prefs) async {
  await prefs.remove(_onboardingCompletedKey);
  await prefs.remove(_onboardingProgressKey);
}
