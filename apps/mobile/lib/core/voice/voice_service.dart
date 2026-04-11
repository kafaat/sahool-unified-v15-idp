import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_recognition_error.dart';
import '../utils/app_logger.dart';

/// SAHOOL Voice Service
/// خدمة التعرف على الصوت
///
/// Features:
/// - Speech recognition integration (speech_to_text)
/// - Arabic and English language support
/// - Continuous listening mode
/// - Wake word detection preparation
/// - Noise level monitoring
/// - Offline-capable when device supports

// ═══════════════════════════════════════════════════════════════════════════
// Enums & Models
// ═══════════════════════════════════════════════════════════════════════════

/// Voice service status
enum VoiceServiceStatus {
  uninitialized,
  initializing,
  ready,
  listening,
  processing,
  paused,
  error,
  unavailable,
}

/// Supported languages for speech recognition
enum VoiceLanguage {
  arabicYemen('ar-YE', 'العربية (اليمن)', 'Arabic (Yemen)'),
  arabicSaudi('ar-SA', 'العربية (السعودية)', 'Arabic (Saudi Arabia)'),
  arabicEgypt('ar-EG', 'العربية (مصر)', 'Arabic (Egypt)'),
  arabicGeneral('ar', 'العربية', 'Arabic'),
  englishUS('en-US', 'English (US)', 'English (US)'),
  englishUK('en-GB', 'English (UK)', 'English (UK)');

  final String localeId;
  final String nameAr;
  final String nameEn;

  const VoiceLanguage(this.localeId, this.nameAr, this.nameEn);

  bool get isArabic => localeId.startsWith('ar');
}

/// Speech recognition result
class SpeechResult {
  final String recognizedText;
  final double confidence;
  final bool isFinal;
  final VoiceLanguage language;
  final DateTime timestamp;
  final List<String> alternates;

  const SpeechResult({
    required this.recognizedText,
    required this.confidence,
    required this.isFinal,
    required this.language,
    required this.timestamp,
    this.alternates = const [],
  });

  @override
  String toString() =>
      'SpeechResult(text: "$recognizedText", confidence: ${(confidence * 100).toStringAsFixed(1)}%, isFinal: $isFinal)';
}

/// Voice service error
class VoiceServiceError {
  final String code;
  final String message;
  final String messageAr;
  final bool isPermanent;

  const VoiceServiceError({
    required this.code,
    required this.message,
    required this.messageAr,
    this.isPermanent = false,
  });

  static const permissionDenied = VoiceServiceError(
    code: 'permission_denied',
    message: 'Microphone permission was denied',
    messageAr: 'تم رفض إذن الميكروفون',
    isPermanent: false,
  );

  /// User tapped "Don't ask again" / "Deny permanently" — the only way
  /// forward is to open the system settings screen. UI layers should
  /// detect this code and show an "Open Settings" button.
  static const permissionPermanentlyDenied = VoiceServiceError(
    code: 'permission_permanently_denied',
    message: 'Microphone permission was permanently denied. Open app settings to enable it.',
    messageAr: 'تم رفض إذن الميكروفون بشكل دائم. افتح إعدادات التطبيق لتفعيله.',
    isPermanent: true,
  );

  /// Platform reports that the microphone hardware is physically unavailable
  /// (e.g. no microphone on this device, or another app is holding it).
  static const notAvailable = VoiceServiceError(
    code: 'not_available',
    message: 'Speech recognition is not available on this device',
    messageAr: 'التعرف على الصوت غير متاح على هذا الجهاز',
    isPermanent: true,
  );

  static const networkError = VoiceServiceError(
    code: 'network_error',
    message: 'Network error occurred during speech recognition',
    messageAr: 'حدث خطأ في الشبكة أثناء التعرف على الصوت',
  );

  static const timeout = VoiceServiceError(
    code: 'timeout',
    message: 'Speech recognition timed out',
    messageAr: 'انتهت مهلة التعرف على الصوت',
  );

  static const noMatch = VoiceServiceError(
    code: 'no_match',
    message: 'Could not understand the speech',
    messageAr: 'لم أستطع فهم ما قلته',
  );

  static const busy = VoiceServiceError(
    code: 'busy',
    message: 'Speech recognizer is busy',
    messageAr: 'التعرف على الصوت مشغول',
  );

  static VoiceServiceError fromSpeechError(SpeechRecognitionError error) {
    switch (error.errorMsg) {
      case 'error_permission':
        return permissionDenied;
      case 'error_network':
      case 'error_network_timeout':
        return networkError;
      case 'error_speech_timeout':
        return timeout;
      case 'error_no_match':
        return noMatch;
      case 'error_busy':
        return busy;
      default:
        return VoiceServiceError(
          code: error.errorMsg,
          message: 'Speech recognition error: ${error.errorMsg}',
          messageAr: 'خطأ في التعرف على الصوت: ${error.errorMsg}',
        );
    }
  }
}

/// Listening options
class ListeningOptions {
  /// Upper bound on how long the speech engine will listen before
  /// auto-stopping. `null` means "continuous listening with no hard
  /// deadline" — only use this with [continuousOptions] where the UI
  /// layer owns the stop lifecycle explicitly. For any normal
  /// listen-once interaction, leave this at the default 30 s.
  ///
  /// Independently of this value, [VoiceService] installs a watchdog
  /// [Timer] that force-stops the recognizer at `listenFor + 2s` (or at
  /// [watchdogFallback] when `listenFor` is null) so a stuck engine can
  /// never leave the service pinned in the `listening` state.
  final Duration? listenFor;

  /// Pause duration to consider speech ended
  final Duration pauseFor;

  /// Callback for partial results
  final bool partialResults;

  /// On-device recognition (offline)
  final bool onDevice;

  /// Listen mode (single phrase or continuous)
  final ListenMode listenMode;

  const ListeningOptions({
    this.listenFor = const Duration(seconds: 30),
    this.pauseFor = const Duration(seconds: 2),
    this.partialResults = true,
    this.onDevice = false,
    this.listenMode = ListenMode.confirmation,
  });

  /// Sensible default for single-phrase interactions (voice commands,
  /// short questions): 30-second hard cap. Balances "long enough to
  /// finish a sentence" with "short enough to recover from a crash".
  static const defaultOptions = ListeningOptions();

  /// Continuous listening (wake-word / dictation) where the upper bound
  /// is explicitly unbounded. Even here, [VoiceService] still installs
  /// a [watchdogFallback] Timer so the service cannot leak the
  /// `listening` state indefinitely.
  static const continuousOptions = ListeningOptions(
    listenFor: null,
    pauseFor: Duration(seconds: 3),
    partialResults: true,
    listenMode: ListenMode.dictation,
  );

  /// Watchdog deadline used when [listenFor] is null. After this elapses
  /// without the engine emitting `done`, the service force-cancels to
  /// recover the `ready` state.
  static const watchdogFallback = Duration(minutes: 2);
}

/// Wake word configuration
class WakeWordConfig {
  final List<String> wakeWords;
  final List<String> wakeWordsAr;
  final double sensitivity;
  final bool enabled;

  const WakeWordConfig({
    this.wakeWords = const ['hey sahool', 'ok sahool', 'sahool'],
    this.wakeWordsAr = const ['يا سهول', 'سهول', 'هيي سهول'],
    this.sensitivity = 0.5,
    this.enabled = false, // Disabled by default - requires continuous listening
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Voice Service Implementation
// ═══════════════════════════════════════════════════════════════════════════

class VoiceService {
  static VoiceService? _instance;
  static VoiceService get instance {
    _instance ??= VoiceService._();
    return _instance!;
  }

  VoiceService._();

  // Core speech recognition
  final SpeechToText _speech = SpeechToText();

  // State
  VoiceServiceStatus _status = VoiceServiceStatus.uninitialized;
  VoiceLanguage _currentLanguage = VoiceLanguage.arabicYemen;
  List<LocaleName> _availableLocales = [];
  double _currentSoundLevel = 0.0;
  WakeWordConfig _wakeWordConfig = const WakeWordConfig();

  /// Watchdog timer that force-stops recognition if the speech engine
  /// fails to emit `done` within the listen window. Without this, the
  /// service can be pinned in [VoiceServiceStatus.listening] forever on
  /// devices where the underlying recognizer crashes silently.
  Timer? _listeningWatchdog;

  // Stream controllers
  final _statusController = StreamController<VoiceServiceStatus>.broadcast();
  final _resultController = StreamController<SpeechResult>.broadcast();
  final _errorController = StreamController<VoiceServiceError>.broadcast();
  final _soundLevelController = StreamController<double>.broadcast();

  // Getters
  VoiceServiceStatus get status => _status;
  VoiceLanguage get currentLanguage => _currentLanguage;
  List<LocaleName> get availableLocales => _availableLocales;
  double get currentSoundLevel => _currentSoundLevel;
  bool get isListening => _status == VoiceServiceStatus.listening;
  bool get isReady => _status == VoiceServiceStatus.ready;
  bool get isAvailable => _status != VoiceServiceStatus.unavailable;

  // Streams
  Stream<VoiceServiceStatus> get statusStream => _statusController.stream;
  Stream<SpeechResult> get resultStream => _resultController.stream;
  Stream<VoiceServiceError> get errorStream => _errorController.stream;
  Stream<double> get soundLevelStream => _soundLevelController.stream;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the voice service.
  ///
  /// This performs two distinct checks in order:
  ///   1. Microphone permission via [permission_handler]. If the user has
  ///      never been asked, a system prompt is shown. If the user previously
  ///      selected "Don't ask again" / "Deny permanently", we emit a
  ///      [VoiceServiceError.permissionPermanentlyDenied] so the caller can
  ///      direct the user to app settings via [openAppSettings].
  ///   2. Speech recognition availability via [_speech.initialize]. This
  ///      only runs after the mic permission is confirmed, so the
  ///      "not available" path now genuinely means hardware/engine
  ///      unavailable rather than a silent permission denial.
  ///
  /// Returns `true` only when both checks pass.
  Future<bool> initialize() async {
    if (_status == VoiceServiceStatus.ready) return true;

    _updateStatus(VoiceServiceStatus.initializing);
    AppLogger.i('Initializing voice service...', tag: 'VOICE');

    try {
      // ── Step 1: explicit microphone permission check ──────────────────
      final permissionOk = await _ensureMicrophonePermission();
      if (!permissionOk) {
        // Error already emitted by _ensureMicrophonePermission.
        // Status was set to error/unavailable there as well.
        return false;
      }

      // ── Step 2: speech engine availability ────────────────────────────
      final available = await _speech.initialize(
        onStatus: _handleStatusChange,
        onError: _handleError,
        debugLogging: kDebugMode,
      );

      if (!available) {
        _updateStatus(VoiceServiceStatus.unavailable);
        AppLogger.w(
          'Speech recognition engine not available (permission already granted)',
          tag: 'VOICE',
        );
        _errorController.add(VoiceServiceError.notAvailable);
        return false;
      }

      // Get available locales
      _availableLocales = await _speech.locales();
      AppLogger.d('Available locales: ${_availableLocales.length}', tag: 'VOICE');

      // Find best Arabic locale
      _selectBestArabicLocale();

      _updateStatus(VoiceServiceStatus.ready);
      AppLogger.i('Voice service initialized successfully', tag: 'VOICE', data: {
        'language': _currentLanguage.localeId,
        'availableLocales': _availableLocales.length,
      });

      return true;
    } catch (e, stack) {
      AppLogger.e('Failed to initialize voice service', tag: 'VOICE', error: e, stackTrace: stack);
      _updateStatus(VoiceServiceStatus.error);
      _errorController.add(VoiceServiceError(
        code: 'init_error',
        message: 'Failed to initialize: $e',
        messageAr: 'فشل في التهيئة: $e',
      ));
      return false;
    }
  }

  /// Request (or verify) microphone permission.
  ///
  /// Returns `true` only when the permission is granted. Any non-granted
  /// state results in an error being emitted on [errorStream] and the
  /// service status transitioning to [VoiceServiceStatus.unavailable]
  /// (for permanently denied) or [VoiceServiceStatus.error] (for
  /// transient denial / restricted).
  ///
  /// Callers that want to retry after the user opens app settings can call
  /// [initialize] again; this method is idempotent.
  @visibleForTesting
  Future<bool> ensureMicrophonePermission() => _ensureMicrophonePermission();

  Future<bool> _ensureMicrophonePermission() async {
    final status = await Permission.microphone.status;
    AppLogger.d('Microphone permission status: $status', tag: 'VOICE');

    if (status.isGranted || status.isLimited) {
      return true;
    }

    if (status.isPermanentlyDenied) {
      AppLogger.w('Microphone permission permanently denied', tag: 'VOICE');
      _updateStatus(VoiceServiceStatus.unavailable);
      _errorController.add(VoiceServiceError.permissionPermanentlyDenied);
      return false;
    }

    if (status.isRestricted) {
      // iOS parental controls / MDM restriction — user cannot grant.
      AppLogger.w('Microphone permission restricted by device policy', tag: 'VOICE');
      _updateStatus(VoiceServiceStatus.unavailable);
      _errorController.add(VoiceServiceError.permissionPermanentlyDenied);
      return false;
    }

    // status is denied (first-time or soft-denied) — request now.
    final requested = await Permission.microphone.request();
    AppLogger.d('Microphone permission after request: $requested', tag: 'VOICE');

    if (requested.isGranted || requested.isLimited) {
      return true;
    }

    if (requested.isPermanentlyDenied) {
      _updateStatus(VoiceServiceStatus.unavailable);
      _errorController.add(VoiceServiceError.permissionPermanentlyDenied);
      return false;
    }

    // User tapped "Deny" on the system prompt but not permanently.
    _updateStatus(VoiceServiceStatus.error);
    _errorController.add(VoiceServiceError.permissionDenied);
    return false;
  }

  /// Open the OS app-settings screen so the user can change the
  /// microphone permission after a permanent denial. Call this from the
  /// UI layer when you receive [VoiceServiceError.permissionPermanentlyDenied].
  Future<bool> openMicrophoneSettings() => openAppSettings();

  /// Select the best available Arabic locale
  void _selectBestArabicLocale() {
    // Priority: ar-YE > ar-SA > ar-EG > ar > en-US
    final priorities = [
      VoiceLanguage.arabicYemen,
      VoiceLanguage.arabicSaudi,
      VoiceLanguage.arabicEgypt,
      VoiceLanguage.arabicGeneral,
      VoiceLanguage.englishUS,
    ];

    for (final lang in priorities) {
      if (_availableLocales.any((l) => l.localeId == lang.localeId)) {
        _currentLanguage = lang;
        AppLogger.d('Selected language: ${lang.localeId}', tag: 'VOICE');
        return;
      }
    }

    // Fallback to any available Arabic locale
    final arabicLocale = _availableLocales.firstWhere(
      (l) => l.localeId.startsWith('ar'),
      orElse: () => _availableLocales.isNotEmpty
          ? _availableLocales.first
          : LocaleName(_currentLanguage.localeId, _currentLanguage.nameEn),
    );

    _currentLanguage = VoiceLanguage.values.firstWhere(
      (lang) => lang.localeId == arabicLocale.localeId,
      orElse: () => VoiceLanguage.arabicGeneral,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Listening Control
  // ═══════════════════════════════════════════════════════════════════════════

  /// Start listening for speech
  Future<void> startListening({
    VoiceLanguage? language,
    ListeningOptions options = ListeningOptions.defaultOptions,
  }) async {
    if (!isReady && _status != VoiceServiceStatus.paused) {
      final initialized = await initialize();
      if (!initialized) {
        AppLogger.w('Cannot start listening - service not available', tag: 'VOICE');
        return;
      }
    }

    if (isListening) {
      AppLogger.d('Already listening', tag: 'VOICE');
      return;
    }

    final targetLanguage = language ?? _currentLanguage;
    _currentLanguage = targetLanguage;

    AppLogger.i('Starting speech recognition', tag: 'VOICE', data: {
      'language': targetLanguage.localeId,
      'listenFor': options.listenFor?.inSeconds,
      'onDevice': options.onDevice,
    });

    try {
      await _speech.listen(
        onResult: _handleResult,
        localeId: targetLanguage.localeId,
        listenFor: options.listenFor,
        pauseFor: options.pauseFor,
        partialResults: options.partialResults,
        onDevice: options.onDevice,
        listenMode: options.listenMode,
        onSoundLevelChange: _handleSoundLevelChange,
      );

      _updateStatus(VoiceServiceStatus.listening);
      _armWatchdog(options);
    } catch (e, stack) {
      AppLogger.e('Failed to start listening', tag: 'VOICE', error: e, stackTrace: stack);
      _updateStatus(VoiceServiceStatus.error);
      _errorController.add(VoiceServiceError(
        code: 'listen_error',
        message: 'Failed to start listening: $e',
        messageAr: 'فشل في بدء الاستماع: $e',
      ));
    }
  }

  /// Install a watchdog Timer that force-stops the recognizer if it
  /// fails to emit a terminal state within the listen window. This is
  /// the recovery path for devices where the platform recognizer
  /// crashes silently and never delivers `done` or `error`, which used
  /// to leave the service pinned in the `listening` state indefinitely.
  ///
  /// Budget = `options.listenFor + 2s` (grace for the native engine to
  /// deliver its own timeout), or [ListeningOptions.watchdogFallback]
  /// when `listenFor` is null (continuous mode).
  void _armWatchdog(ListeningOptions options) {
    _listeningWatchdog?.cancel();
    final baseline = options.listenFor ?? ListeningOptions.watchdogFallback;
    final budget = baseline + const Duration(seconds: 2);
    _listeningWatchdog = Timer(budget, _onWatchdogFired);
    AppLogger.d(
      'Watchdog armed for ${budget.inSeconds}s',
      tag: 'VOICE',
    );
  }

  void _disarmWatchdog() {
    _listeningWatchdog?.cancel();
    _listeningWatchdog = null;
  }

  Future<void> _onWatchdogFired() async {
    if (!isListening) {
      // The engine already finished naturally; nothing to do.
      _disarmWatchdog();
      return;
    }
    AppLogger.w(
      'Speech recognizer watchdog fired — force-cancelling to recover',
      tag: 'VOICE',
    );
    try {
      await _speech.cancel();
    } catch (e) {
      AppLogger.e('Watchdog cancel failed', tag: 'VOICE', error: e);
    }
    _disarmWatchdog();
    _updateStatus(VoiceServiceStatus.ready);
    _errorController.add(VoiceServiceError.timeout);
  }

  /// Stop listening
  Future<void> stopListening() async {
    if (!isListening) return;

    AppLogger.d('Stopping speech recognition', tag: 'VOICE');
    _disarmWatchdog();

    try {
      await _speech.stop();
      _updateStatus(VoiceServiceStatus.ready);
    } catch (e) {
      AppLogger.e('Error stopping listening', tag: 'VOICE', error: e);
    }
  }

  /// Cancel listening without processing
  Future<void> cancelListening() async {
    if (!isListening) return;

    AppLogger.d('Cancelling speech recognition', tag: 'VOICE');
    _disarmWatchdog();

    try {
      await _speech.cancel();
      _updateStatus(VoiceServiceStatus.ready);
    } catch (e) {
      AppLogger.e('Error cancelling listening', tag: 'VOICE', error: e);
    }
  }

  /// Pause listening (can be resumed)
  Future<void> pauseListening() async {
    if (!isListening) return;

    _disarmWatchdog();
    try {
      await _speech.stop();
      _updateStatus(VoiceServiceStatus.paused);
    } catch (e) {
      AppLogger.e('Error pausing listening', tag: 'VOICE', error: e);
    }
  }

  /// Resume listening after pause
  Future<void> resumeListening() async {
    if (_status != VoiceServiceStatus.paused) return;

    await startListening();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Language Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Set the recognition language
  void setLanguage(VoiceLanguage language) {
    if (_currentLanguage == language) return;

    final wasListening = isListening;
    if (wasListening) {
      cancelListening();
    }

    _currentLanguage = language;
    AppLogger.i('Voice language changed to: ${language.localeId}', tag: 'VOICE');

    if (wasListening) {
      startListening();
    }
  }

  /// Toggle between Arabic and English
  void toggleLanguage() {
    if (_currentLanguage.isArabic) {
      setLanguage(VoiceLanguage.englishUS);
    } else {
      setLanguage(VoiceLanguage.arabicYemen);
    }
  }

  /// Get supported languages that are available on device
  List<VoiceLanguage> getSupportedLanguages() {
    return VoiceLanguage.values.where((lang) {
      return _availableLocales.any((locale) => locale.localeId == lang.localeId);
    }).toList();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Wake Word Detection (Preparation)
  // ═══════════════════════════════════════════════════════════════════════════

  /// Configure wake word detection
  void configureWakeWord(WakeWordConfig config) {
    _wakeWordConfig = config;
    AppLogger.d('Wake word config updated', tag: 'VOICE', data: {
      'enabled': config.enabled,
      'words': config.wakeWords,
    });
  }

  /// Check if text contains wake word
  bool containsWakeWord(String text) {
    final normalizedText = _normalizeText(text);

    // Check English wake words
    for (final word in _wakeWordConfig.wakeWords) {
      if (normalizedText.contains(_normalizeText(word))) {
        return true;
      }
    }

    // Check Arabic wake words
    for (final word in _wakeWordConfig.wakeWordsAr) {
      if (normalizedText.contains(_normalizeArabicText(word))) {
        return true;
      }
    }

    return false;
  }

  /// Remove wake word from text
  String removeWakeWord(String text) {
    var result = text;

    for (final word in [..._wakeWordConfig.wakeWords, ..._wakeWordConfig.wakeWordsAr]) {
      result = result.replaceAll(RegExp(word, caseSensitive: false), '').trim();
    }

    return result;
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Event Handlers
  // ═══════════════════════════════════════════════════════════════════════════

  void _handleResult(SpeechRecognitionResult result) {
    AppLogger.d(
      'Speech result: "${result.recognizedWords}" (final: ${result.finalResult}, confidence: ${result.confidence})',
      tag: 'VOICE',
    );

    final speechResult = SpeechResult(
      recognizedText: result.recognizedWords,
      confidence: result.confidence,
      isFinal: result.finalResult,
      language: _currentLanguage,
      timestamp: DateTime.now(),
      alternates: result.alternates.map((a) => a.recognizedWords).toList(),
    );

    _resultController.add(speechResult);

    if (result.finalResult) {
      _updateStatus(VoiceServiceStatus.processing);
      // Auto-return to ready after processing
      Future.delayed(const Duration(milliseconds: 100), () {
        if (_status == VoiceServiceStatus.processing) {
          _updateStatus(VoiceServiceStatus.ready);
        }
      });
    }
  }

  void _handleStatusChange(String status) {
    AppLogger.d('Speech status: $status', tag: 'VOICE');

    switch (status) {
      case 'listening':
        _updateStatus(VoiceServiceStatus.listening);
        break;
      case 'notListening':
        if (_status == VoiceServiceStatus.listening) {
          _updateStatus(VoiceServiceStatus.ready);
        }
        // Engine reported a clean stop — the watchdog is no longer
        // needed; cancelling it here avoids a spurious "timeout" event
        // firing after the recognizer has already gone home.
        _disarmWatchdog();
        break;
      case 'done':
        _updateStatus(VoiceServiceStatus.ready);
        _disarmWatchdog();
        break;
    }
  }

  void _handleError(SpeechRecognitionError error) {
    AppLogger.e('Speech error: ${error.errorMsg}', tag: 'VOICE', data: {
      'permanent': error.permanent,
    });

    // The engine is done — tear down the watchdog to avoid a stale
    // timeout being emitted after the real error.
    _disarmWatchdog();

    final voiceError = VoiceServiceError.fromSpeechError(error);
    _errorController.add(voiceError);

    if (error.permanent) {
      _updateStatus(VoiceServiceStatus.error);
    } else {
      _updateStatus(VoiceServiceStatus.ready);
    }
  }

  void _handleSoundLevelChange(double level) {
    _currentSoundLevel = level;
    _soundLevelController.add(level);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Utilities
  // ═══════════════════════════════════════════════════════════════════════════

  void _updateStatus(VoiceServiceStatus newStatus) {
    if (_status == newStatus) return;
    _status = newStatus;
    _statusController.add(newStatus);
  }

  String _normalizeText(String text) {
    return text.toLowerCase().trim();
  }

  String _normalizeArabicText(String text) {
    return text
        .replaceAll('أ', 'ا')
        .replaceAll('إ', 'ا')
        .replaceAll('آ', 'ا')
        .replaceAll('ة', 'ه')
        .replaceAll('ى', 'ي')
        .trim();
  }

  /// Check if speech recognition is available on this device.
  ///
  /// This is a *cheap* check intended for UI gating (e.g. hiding a voice
  /// button on devices without a microphone). It does NOT request
  /// permission; use [initialize] for that.
  ///
  /// Returns `true` only when:
  ///   - the microphone permission is already granted, AND
  ///   - the platform speech engine reports itself available.
  Future<bool> checkAvailability() async {
    try {
      final micStatus = await Permission.microphone.status;
      if (!micStatus.isGranted && !micStatus.isLimited) {
        return false;
      }
      return await _speech.initialize();
    } catch (e) {
      AppLogger.e('checkAvailability failed', tag: 'VOICE', error: e);
      return false;
    }
  }

  /// Dispose resources
  void dispose() {
    _disarmWatchdog();
    _speech.stop();
    _speech.cancel();
    _statusController.close();
    _resultController.close();
    _errorController.close();
    _soundLevelController.close();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Voice service singleton provider
final voiceServiceProvider = Provider<VoiceService>((ref) {
  return VoiceService.instance;
});

/// Voice service status stream provider
final voiceServiceStatusProvider = StreamProvider<VoiceServiceStatus>((ref) {
  return VoiceService.instance.statusStream;
});

/// Speech result stream provider
final speechResultProvider = StreamProvider<SpeechResult>((ref) {
  return VoiceService.instance.resultStream;
});

/// Voice error stream provider
final voiceErrorProvider = StreamProvider<VoiceServiceError>((ref) {
  return VoiceService.instance.errorStream;
});

/// Sound level stream provider
final voiceSoundLevelProvider = StreamProvider<double>((ref) {
  return VoiceService.instance.soundLevelStream;
});

/// Current voice language provider
final voiceLanguageProvider = Provider<VoiceLanguage>((ref) {
  return VoiceService.instance.currentLanguage;
});

/// Is listening provider
final isVoiceListeningProvider = Provider<bool>((ref) {
  final status = ref.watch(voiceServiceStatusProvider);
  return status.when(
    data: (s) => s == VoiceServiceStatus.listening,
    loading: () => false,
    error: (_, __) => false,
  );
});
