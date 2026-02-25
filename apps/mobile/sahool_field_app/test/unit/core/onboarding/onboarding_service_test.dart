import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/onboarding/onboarding_service.dart';

void main() {
  group('OnboardingStep', () {
    test('should have 6 steps', () {
      expect(OnboardingStep.values.length, 6);
    });

    test('should include all expected steps', () {
      expect(OnboardingStep.values, contains(OnboardingStep.welcome));
      expect(OnboardingStep.values, contains(OnboardingStep.featureTour));
      expect(OnboardingStep.values, contains(OnboardingStep.fieldSetup));
      expect(OnboardingStep.values, contains(OnboardingStep.notificationSetup));
      expect(OnboardingStep.values, contains(OnboardingStep.iotPairing));
      expect(OnboardingStep.values, contains(OnboardingStep.completed));
    });

    test('should have Arabic titles', () {
      expect(OnboardingStep.welcome.titleAr, 'مرحباً بك');
      expect(OnboardingStep.featureTour.titleAr, 'جولة في الميزات');
      expect(OnboardingStep.fieldSetup.titleAr, 'إعداد الحقل الأول');
      expect(OnboardingStep.notificationSetup.titleAr, 'إعداد الإشعارات');
      expect(OnboardingStep.iotPairing.titleAr, 'ربط أجهزة IoT');
      expect(OnboardingStep.completed.titleAr, 'مكتمل');
    });

    test('should have English titles', () {
      expect(OnboardingStep.welcome.titleEn, 'Welcome');
      expect(OnboardingStep.featureTour.titleEn, 'Feature Tour');
      expect(OnboardingStep.fieldSetup.titleEn, 'Field Setup');
      expect(OnboardingStep.notificationSetup.titleEn, 'Notification Setup');
      expect(OnboardingStep.iotPairing.titleEn, 'IoT Device Pairing');
      expect(OnboardingStep.completed.titleEn, 'Completed');
    });

    test('should have Arabic descriptions', () {
      expect(OnboardingStep.welcome.descriptionAr, isNotEmpty);
      expect(OnboardingStep.featureTour.descriptionAr, isNotEmpty);
      expect(OnboardingStep.fieldSetup.descriptionAr, isNotEmpty);
      expect(OnboardingStep.notificationSetup.descriptionAr, isNotEmpty);
      expect(OnboardingStep.iotPairing.descriptionAr, isNotEmpty);
      expect(OnboardingStep.completed.descriptionAr, isNotEmpty);
    });

    test('required steps should be welcome, featureTour, fieldSetup, completed',
        () {
      expect(OnboardingStep.welcome.isRequired, true);
      expect(OnboardingStep.featureTour.isRequired, true);
      expect(OnboardingStep.fieldSetup.isRequired, true);
      expect(OnboardingStep.completed.isRequired, true);
    });

    test('optional steps should be notificationSetup and iotPairing', () {
      expect(OnboardingStep.notificationSetup.isRequired, false);
      expect(OnboardingStep.iotPairing.isRequired, false);
    });

    test('stepIndex should return correct indices', () {
      expect(OnboardingStep.welcome.stepIndex, 0);
      expect(OnboardingStep.featureTour.stepIndex, 1);
      expect(OnboardingStep.fieldSetup.stepIndex, 2);
      expect(OnboardingStep.notificationSetup.stepIndex, 3);
      expect(OnboardingStep.iotPairing.stepIndex, 4);
      expect(OnboardingStep.completed.stepIndex, 5);
    });

    test('totalSteps should exclude completed', () {
      // 6 values - 1 (completed) = 5
      expect(OnboardingStepExtension.totalSteps, 5);
    });
  });

  group('OnboardingState', () {
    test('should have sensible defaults', () {
      const state = OnboardingState();
      expect(state.currentStep, OnboardingStep.welcome);
      expect(state.completedSteps, isEmpty);
      expect(state.isComplete, false);
      expect(state.wasSkipped, false);
      expect(state.firstFieldId, isNull);
      expect(state.pairedDeviceIds, isEmpty);
    });

    test('progress should be 0 initially', () {
      const state = OnboardingState();
      expect(state.progress, 0);
      expect(state.progressFormatted, '0%');
    });

    test('progress should be 1.0 when complete', () {
      const state = OnboardingState(isComplete: true);
      expect(state.progress, 1.0);
      expect(state.progressFormatted, '100%');
    });

    test('progress should reflect completed steps', () {
      const state = OnboardingState(
        completedSteps: {OnboardingStep.welcome, OnboardingStep.featureTour},
      );
      // 2 / 5 = 0.4
      expect(state.progress, closeTo(0.4, 0.01));
      expect(state.progressFormatted, '40%');
    });

    test('completedCount and remainingCount should be correct', () {
      const state = OnboardingState(
        completedSteps: {
          OnboardingStep.welcome,
          OnboardingStep.featureTour,
          OnboardingStep.fieldSetup,
        },
      );
      expect(state.completedCount, 3);
      expect(state.remainingCount, 2); // 5 - 3
    });

    test('hasSetupField should check for fieldSetup completion', () {
      const withSetup = OnboardingState(
        completedSteps: {OnboardingStep.fieldSetup},
      );
      const withoutSetup = OnboardingState(
        completedSteps: {OnboardingStep.welcome},
      );

      expect(withSetup.hasSetupField, true);
      expect(withoutSetup.hasSetupField, false);
    });

    test('hasIotDevices should check pairedDeviceIds', () {
      const withDevices = OnboardingState(
        pairedDeviceIds: ['device-1', 'device-2'],
      );
      const withoutDevices = OnboardingState();

      expect(withDevices.hasIotDevices, true);
      expect(withoutDevices.hasIotDevices, false);
    });

    test('copyWith should update specified fields', () {
      const original = OnboardingState();
      final updated = original.copyWith(
        currentStep: OnboardingStep.featureTour,
        isComplete: true,
        wasSkipped: true,
        firstFieldId: 'field-123',
        pairedDeviceIds: ['dev-1'],
      );

      expect(updated.currentStep, OnboardingStep.featureTour);
      expect(updated.isComplete, true);
      expect(updated.wasSkipped, true);
      expect(updated.firstFieldId, 'field-123');
      expect(updated.pairedDeviceIds, ['dev-1']);
    });

    test('copyWith should preserve unspecified fields', () {
      const original = OnboardingState(
        currentStep: OnboardingStep.fieldSetup,
        isComplete: false,
        firstFieldId: 'abc',
      );
      final updated = original.copyWith(wasSkipped: true);

      expect(updated.currentStep, OnboardingStep.fieldSetup);
      expect(updated.isComplete, false);
      expect(updated.firstFieldId, 'abc');
      expect(updated.wasSkipped, true);
    });
  });
}
