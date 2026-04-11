/// Phase 4A regression tests for VoiceService value objects.
/// اختبارات انحدار لقيم VoiceService — المرحلة 4أ
///
/// These tests are intentionally narrow: they exercise only the
/// pure-Dart value classes (ListeningOptions, VoiceServiceError,
/// VoiceLanguage, SpeechResult) without touching the platform
/// speech_to_text / permission_handler plugins. That makes them safe
/// to run in a vanilla `flutter test` environment with zero mocks.
///
/// Regression targets:
///   - Commit c6eb4bb (watchdog Timer): defaultOptions.listenFor must
///     default to 30s, continuousOptions must remain null, watchdog
///     fallback must be 2 minutes.
///   - Commit 164c4dd (permission check): permissionPermanentlyDenied
///     constant must exist and be marked permanent; permissionDenied
///     must no longer be permanent (so UI can retry on soft denial).
///   - Commit 3ea2f69 (platform permissions): indirect — validated by
///     not breaking the existing VoiceLanguage / SpeechResult surface.
library;

import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/voice/voice_service.dart';
import 'package:speech_to_text/speech_recognition_error.dart';

void main() {
  group('ListeningOptions — watchdog regression (commit c6eb4bb)', () {
    test('defaultOptions.listenFor is 30 seconds (was null)', () {
      // This is the core regression fix: callers that used
      // startListening() without arguments used to listen forever.
      expect(
        ListeningOptions.defaultOptions.listenFor,
        const Duration(seconds: 30),
      );
    });

    test('defaultOptions keeps existing pauseFor/partialResults/mode', () {
      const opts = ListeningOptions.defaultOptions;
      expect(opts.pauseFor, const Duration(seconds: 2));
      expect(opts.partialResults, isTrue);
      expect(opts.onDevice, isFalse);
    });

    test('continuousOptions still has null listenFor for unbounded streams', () {
      // Continuous mode (wake-word / dictation) is the one place where
      // callers intentionally want no hard deadline. Changing this would
      // be a breaking change for wake-word UIs.
      expect(ListeningOptions.continuousOptions.listenFor, isNull);
      expect(
        ListeningOptions.continuousOptions.pauseFor,
        const Duration(seconds: 3),
      );
    });

    test('watchdogFallback is 2 minutes', () {
      expect(
        ListeningOptions.watchdogFallback,
        const Duration(minutes: 2),
      );
    });

    test('explicit listenFor override still works', () {
      // Users can still pass listenFor: null explicitly for continuous
      // listening, or any other Duration for custom windows.
      const custom = ListeningOptions(listenFor: null);
      expect(custom.listenFor, isNull);

      const tenSec = ListeningOptions(listenFor: Duration(seconds: 10));
      expect(tenSec.listenFor, const Duration(seconds: 10));
    });
  });

  group('VoiceServiceError — permission regression (commit 164c4dd)', () {
    test('permissionDenied is NOT permanent so UI can retry', () {
      // Commit 164c4dd changed isPermanent from true → false because
      // a soft denial (user tapped "Deny" but not "Don't ask again")
      // is recoverable on the next initialize() call.
      expect(VoiceServiceError.permissionDenied.isPermanent, isFalse);
      expect(VoiceServiceError.permissionDenied.code, 'permission_denied');
    });

    test('permissionPermanentlyDenied exists and is permanent', () {
      // New constant introduced in commit 164c4dd. UI layers must
      // switch on this specifically to show an "Open Settings" CTA.
      expect(
        VoiceServiceError.permissionPermanentlyDenied.isPermanent,
        isTrue,
      );
      expect(
        VoiceServiceError.permissionPermanentlyDenied.code,
        'permission_permanently_denied',
      );
    });

    test('permissionPermanentlyDenied is bilingual EN/AR', () {
      final err = VoiceServiceError.permissionPermanentlyDenied;
      expect(err.message, contains('permanently denied'));
      expect(err.message, contains('settings'));
      expect(err.messageAr, contains('الميكروفون'));
      expect(err.messageAr, contains('الإعدادات'));
    });

    test('notAvailable remains permanent (unchanged)', () {
      expect(VoiceServiceError.notAvailable.isPermanent, isTrue);
      expect(VoiceServiceError.notAvailable.code, 'not_available');
    });

    test('timeout error has expected code for watchdog emissions', () {
      // The watchdog Timer (commit c6eb4bb) emits this error when it
      // force-cancels a stuck recognizer.
      expect(VoiceServiceError.timeout.code, 'timeout');
      expect(VoiceServiceError.timeout.isPermanent, isFalse);
    });
  });

  group('VoiceServiceError.fromSpeechError mapping', () {
    test('error_permission maps to permissionDenied', () {
      final err = VoiceServiceError.fromSpeechError(
        SpeechRecognitionError('error_permission', true),
      );
      expect(err.code, VoiceServiceError.permissionDenied.code);
    });

    test('error_network maps to networkError', () {
      final err = VoiceServiceError.fromSpeechError(
        SpeechRecognitionError('error_network', false),
      );
      expect(err.code, VoiceServiceError.networkError.code);
    });

    test('error_network_timeout also maps to networkError', () {
      final err = VoiceServiceError.fromSpeechError(
        SpeechRecognitionError('error_network_timeout', false),
      );
      expect(err.code, VoiceServiceError.networkError.code);
    });

    test('error_speech_timeout maps to timeout', () {
      final err = VoiceServiceError.fromSpeechError(
        SpeechRecognitionError('error_speech_timeout', false),
      );
      expect(err.code, VoiceServiceError.timeout.code);
    });

    test('error_no_match maps to noMatch', () {
      final err = VoiceServiceError.fromSpeechError(
        SpeechRecognitionError('error_no_match', false),
      );
      expect(err.code, VoiceServiceError.noMatch.code);
    });

    test('unknown error code is passed through verbatim', () {
      final err = VoiceServiceError.fromSpeechError(
        SpeechRecognitionError('error_futuristic_widget', false),
      );
      expect(err.code, 'error_futuristic_widget');
      expect(err.message, contains('error_futuristic_widget'));
      expect(err.messageAr, contains('error_futuristic_widget'));
    });
  });

  group('VoiceLanguage — language detection', () {
    test('all Arabic variants report isArabic = true', () {
      expect(VoiceLanguage.arabicYemen.isArabic, isTrue);
      expect(VoiceLanguage.arabicSaudi.isArabic, isTrue);
      expect(VoiceLanguage.arabicEgypt.isArabic, isTrue);
      expect(VoiceLanguage.arabicGeneral.isArabic, isTrue);
    });

    test('English variants report isArabic = false', () {
      expect(VoiceLanguage.englishUS.isArabic, isFalse);
      expect(VoiceLanguage.englishUK.isArabic, isFalse);
    });

    test('Yemen is the default Arabic dialect', () {
      // Priority order in _selectBestArabicLocale is ar-YE > ar-SA >
      // ar-EG > ar. The Yemen-first default reflects SAHOOL's primary
      // target audience.
      expect(VoiceLanguage.arabicYemen.localeId, 'ar-YE');
      expect(VoiceLanguage.arabicYemen.nameAr, contains('اليمن'));
    });

    test('localeId prefix matches isArabic correctly', () {
      for (final lang in VoiceLanguage.values) {
        expect(
          lang.isArabic,
          lang.localeId.startsWith('ar'),
          reason: '${lang.localeId} isArabic mismatch',
        );
      }
    });
  });

  group('SpeechResult — value semantics', () {
    final now = DateTime(2026, 4, 11, 20, 0);

    test('toString includes recognized text and confidence', () {
      final result = SpeechResult(
        recognizedText: 'ابدأ ري القمح',
        confidence: 0.87,
        isFinal: true,
        language: VoiceLanguage.arabicYemen,
        timestamp: now,
      );
      final s = result.toString();
      expect(s, contains('ابدأ ري القمح'));
      expect(s, contains('87.0%'));
      expect(s, contains('isFinal: true'));
    });

    test('alternates default to empty list', () {
      final result = SpeechResult(
        recognizedText: 'hello',
        confidence: 0.5,
        isFinal: false,
        language: VoiceLanguage.englishUS,
        timestamp: now,
      );
      expect(result.alternates, isEmpty);
    });

    test('alternates can be provided explicitly', () {
      final result = SpeechResult(
        recognizedText: 'سماد اليوريا',
        confidence: 0.92,
        isFinal: true,
        language: VoiceLanguage.arabicYemen,
        timestamp: now,
        alternates: const ['سماد اليوريا', 'سماد المعرفة', 'سماد الأمم'],
      );
      expect(result.alternates.length, 3);
      expect(result.alternates.first, 'سماد اليوريا');
    });
  });
}
