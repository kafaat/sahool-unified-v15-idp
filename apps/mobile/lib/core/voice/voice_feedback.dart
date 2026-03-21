import 'dart:async';
import 'dart:io';
import 'dart:math';
import 'package:flutter/foundation.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_tts/flutter_tts.dart';
import '../utils/app_logger.dart';
import 'voice_commands.dart';

/// SAHOOL Voice Feedback Service
/// خدمة التغذية الراجعة الصوتية
///
/// Features:
/// - Text-to-speech responses
/// - Arabic TTS support
/// - Audio feedback sounds
/// - Visual feedback coordination
/// - Haptic feedback integration
/// - Queue management for responses

// ═══════════════════════════════════════════════════════════════════════════
// Enums & Models
// ═══════════════════════════════════════════════════════════════════════════

/// Voice feedback status
enum VoiceFeedbackStatus {
  idle,
  initializing,
  ready,
  speaking,
  paused,
  error,
}

/// Feedback language
enum FeedbackLanguage {
  arabic('ar-SA', 'Arabic', 'العربية'),
  english('en-US', 'English', 'English');

  final String locale;
  final String nameEn;
  final String nameAr;

  const FeedbackLanguage(this.locale, this.nameEn, this.nameAr);

  bool get isArabic => locale.startsWith('ar');
}

/// Audio feedback type
enum AudioFeedbackType {
  listeningStart,
  listeningStop,
  commandRecognized,
  commandNotRecognized,
  commandExecuted,
  error,
  notification,
  success,
  warning,
}

/// Speech priority
enum SpeechPriority {
  low(0),
  normal(1),
  high(2),
  urgent(3);

  final int value;
  const SpeechPriority(this.value);
}

/// Queued speech item
class SpeechQueueItem {
  final String text;
  final FeedbackLanguage language;
  final SpeechPriority priority;
  final bool waitForCompletion;
  final VoidCallback? onComplete;
  final DateTime queuedAt;

  SpeechQueueItem({
    required this.text,
    required this.language,
    this.priority = SpeechPriority.normal,
    this.waitForCompletion = false,
    this.onComplete,
  }) : queuedAt = DateTime.now();
}

/// Voice feedback configuration
class VoiceFeedbackConfig {
  final double speechRate;
  final double volume;
  final double pitch;
  final bool enableAudioFeedback;
  final bool enableHapticFeedback;
  final bool speakInBackground;
  final FeedbackLanguage defaultLanguage;

  const VoiceFeedbackConfig({
    this.speechRate = 0.5, // 0.0 - 1.0
    this.volume = 1.0, // 0.0 - 1.0
    this.pitch = 1.0, // 0.5 - 2.0
    this.enableAudioFeedback = true,
    this.enableHapticFeedback = true,
    this.speakInBackground = false,
    this.defaultLanguage = FeedbackLanguage.arabic,
  });

  VoiceFeedbackConfig copyWith({
    double? speechRate,
    double? volume,
    double? pitch,
    bool? enableAudioFeedback,
    bool? enableHapticFeedback,
    bool? speakInBackground,
    FeedbackLanguage? defaultLanguage,
  }) {
    return VoiceFeedbackConfig(
      speechRate: speechRate ?? this.speechRate,
      volume: volume ?? this.volume,
      pitch: pitch ?? this.pitch,
      enableAudioFeedback: enableAudioFeedback ?? this.enableAudioFeedback,
      enableHapticFeedback: enableHapticFeedback ?? this.enableHapticFeedback,
      speakInBackground: speakInBackground ?? this.speakInBackground,
      defaultLanguage: defaultLanguage ?? this.defaultLanguage,
    );
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Voice Feedback Service
// ═══════════════════════════════════════════════════════════════════════════

class VoiceFeedbackService {
  static VoiceFeedbackService? _instance;
  static VoiceFeedbackService get instance {
    _instance ??= VoiceFeedbackService._();
    return _instance!;
  }

  VoiceFeedbackService._();

  // TTS engine
  final FlutterTts _tts = FlutterTts();

  // State
  VoiceFeedbackStatus _status = VoiceFeedbackStatus.idle;
  VoiceFeedbackConfig _config = const VoiceFeedbackConfig();
  List<dynamic> _availableVoices = [];
  FeedbackLanguage _currentLanguage = FeedbackLanguage.arabic;

  // Speech queue
  final List<SpeechQueueItem> _speechQueue = [];
  bool _isProcessingQueue = false;
  SpeechQueueItem? _currentItem;

  // Stream controllers
  final _statusController = StreamController<VoiceFeedbackStatus>.broadcast();
  final _speechProgressController = StreamController<double>.broadcast();

  // Getters
  VoiceFeedbackStatus get status => _status;
  VoiceFeedbackConfig get config => _config;
  FeedbackLanguage get currentLanguage => _currentLanguage;
  List<dynamic> get availableVoices => _availableVoices;
  bool get isSpeaking => _status == VoiceFeedbackStatus.speaking;
  bool get isReady => _status == VoiceFeedbackStatus.ready;

  // Streams
  Stream<VoiceFeedbackStatus> get statusStream => _statusController.stream;
  Stream<double> get speechProgressStream => _speechProgressController.stream;

  // ═══════════════════════════════════════════════════════════════════════════
  // Initialization
  // ═══════════════════════════════════════════════════════════════════════════

  /// Initialize the voice feedback service
  Future<bool> initialize({VoiceFeedbackConfig? config}) async {
    if (_status == VoiceFeedbackStatus.ready) return true;

    _updateStatus(VoiceFeedbackStatus.initializing);
    AppLogger.i('Initializing voice feedback service...', tag: 'VOICE_TTS');

    try {
      if (config != null) {
        _config = config;
      }

      // Configure TTS engine
      await _configureTts();

      // Set up event handlers
      _setupEventHandlers();

      // Get available voices
      _availableVoices = (await _tts.getVoices) as List<dynamic>;
      AppLogger.d('Available voices: ${_availableVoices.length}', tag: 'VOICE_TTS');

      // Set default language
      await setLanguage(_config.defaultLanguage);

      _updateStatus(VoiceFeedbackStatus.ready);
      AppLogger.i('Voice feedback service initialized', tag: 'VOICE_TTS');
      return true;
    } catch (e, stack) {
      AppLogger.e('Failed to initialize voice feedback', tag: 'VOICE_TTS', error: e, stackTrace: stack);
      _updateStatus(VoiceFeedbackStatus.error);
      return false;
    }
  }

  /// Configure TTS engine settings
  Future<void> _configureTts() async {
    await _tts.setVolume(_config.volume);
    await _tts.setSpeechRate(_config.speechRate);
    await _tts.setPitch(_config.pitch);

    // iOS specific configuration
    if (Platform.isIOS) {
      await _tts.setSharedInstance(true);
      await _tts.setIosAudioCategory(
        IosTextToSpeechAudioCategory.playback,
        [
          IosTextToSpeechAudioCategoryOptions.allowBluetooth,
          IosTextToSpeechAudioCategoryOptions.allowBluetoothA2DP,
          IosTextToSpeechAudioCategoryOptions.mixWithOthers,
        ],
        IosTextToSpeechAudioMode.voicePrompt,
      );
    }

    // Android specific configuration
    if (Platform.isAndroid) {
      final engines = await _tts.getEngines;
      AppLogger.d('TTS engines: $engines', tag: 'VOICE_TTS');
    }
  }

  /// Set up TTS event handlers
  void _setupEventHandlers() {
    _tts.setStartHandler(() {
      _updateStatus(VoiceFeedbackStatus.speaking);
      AppLogger.d('TTS started speaking', tag: 'VOICE_TTS');
    });

    _tts.setCompletionHandler(() {
      _updateStatus(VoiceFeedbackStatus.ready);
      _currentItem?.onComplete?.call();
      _currentItem = null;
      AppLogger.d('TTS completed', tag: 'VOICE_TTS');
      _processQueue();
    });

    _tts.setErrorHandler((message) {
      AppLogger.e('TTS error: $message', tag: 'VOICE_TTS');
      _updateStatus(VoiceFeedbackStatus.error);
      _currentItem = null;
      _processQueue();
    });

    _tts.setCancelHandler(() {
      _updateStatus(VoiceFeedbackStatus.ready);
      _currentItem = null;
      AppLogger.d('TTS cancelled', tag: 'VOICE_TTS');
    });

    _tts.setPauseHandler(() {
      _updateStatus(VoiceFeedbackStatus.paused);
      AppLogger.d('TTS paused', tag: 'VOICE_TTS');
    });

    _tts.setContinueHandler(() {
      _updateStatus(VoiceFeedbackStatus.speaking);
      AppLogger.d('TTS resumed', tag: 'VOICE_TTS');
    });

    _tts.setProgressHandler((text, start, end, word) {
      final progress = end / text.length;
      _speechProgressController.add(progress);
    });
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Language Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Set TTS language
  Future<void> setLanguage(FeedbackLanguage language) async {
    try {
      // Check if language is available
      final isAvailable = (await _tts.isLanguageAvailable(language.locale)) as bool? ?? false;

      if (isAvailable) {
        await _tts.setLanguage(language.locale);
        _currentLanguage = language;
        AppLogger.d('TTS language set to: ${language.locale}', tag: 'VOICE_TTS');
      } else {
        // Fallback to alternative
        final fallback = language.isArabic ? 'ar' : 'en-US';
        final fallbackAvailable = (await _tts.isLanguageAvailable(fallback)) as bool? ?? false;
        if (fallbackAvailable) {
          await _tts.setLanguage(fallback);
          AppLogger.w('Language ${language.locale} not available, using $fallback', tag: 'VOICE_TTS');
        }
      }
    } catch (e) {
      AppLogger.e('Failed to set language', tag: 'VOICE_TTS', error: e);
    }
  }

  /// Get available languages
  Future<List<String>> getAvailableLanguages() async {
    try {
      final languages = await _tts.getLanguages;
      return List<String>.from(languages as Iterable);
    } catch (e) {
      return [];
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Speech Control
  // ═══════════════════════════════════════════════════════════════════════════

  /// Speak text
  Future<void> speak(
    String text, {
    FeedbackLanguage? language,
    SpeechPriority priority = SpeechPriority.normal,
    bool waitForCompletion = false,
    VoidCallback? onComplete,
  }) async {
    if (text.isEmpty) return;

    if (!isReady && _status != VoiceFeedbackStatus.speaking) {
      await initialize();
    }

    final item = SpeechQueueItem(
      text: text,
      language: language ?? _currentLanguage,
      priority: priority,
      waitForCompletion: waitForCompletion,
      onComplete: onComplete,
    );

    // Add to queue based on priority
    if (priority == SpeechPriority.urgent) {
      // Urgent - stop current and speak immediately
      await stop();
      _speechQueue.insert(0, item);
    } else {
      // Add to appropriate position in queue
      final insertIndex = _speechQueue.indexWhere((i) => i.priority.value < priority.value);
      if (insertIndex == -1) {
        _speechQueue.add(item);
      } else {
        _speechQueue.insert(insertIndex, item);
      }
    }

    _processQueue();
  }

  /// Process speech queue
  Future<void> _processQueue() async {
    if (_isProcessingQueue || _speechQueue.isEmpty) return;
    if (isSpeaking) return;

    _isProcessingQueue = true;

    try {
      final item = _speechQueue.removeAt(0);
      _currentItem = item;

      // Set language if different
      if (item.language != _currentLanguage) {
        await setLanguage(item.language);
      }

      AppLogger.d('Speaking: "${item.text.substring(0, min(50, item.text.length))}..."', tag: 'VOICE_TTS');
      await _tts.speak(item.text);
    } catch (e) {
      AppLogger.e('Error processing speech queue', tag: 'VOICE_TTS', error: e);
    } finally {
      _isProcessingQueue = false;
    }
  }

  /// Stop speaking
  Future<void> stop() async {
    _speechQueue.clear();
    await _tts.stop();
    _updateStatus(VoiceFeedbackStatus.ready);
  }

  /// Pause speaking
  Future<void> pause() async {
    await _tts.pause();
  }

  /// Resume speaking
  Future<void> resume() async {
    // Note: Resume is only supported on iOS
    if (Platform.isIOS) {
      // Flutter TTS doesn't have a direct resume, but we can use stop and re-speak
      AppLogger.d('Resume not directly supported', tag: 'VOICE_TTS');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Bilingual Speech Helpers
  // ═══════════════════════════════════════════════════════════════════════════

  /// Speak in Arabic
  Future<void> speakArabic(String text, {SpeechPriority priority = SpeechPriority.normal}) async {
    await speak(text, language: FeedbackLanguage.arabic, priority: priority);
  }

  /// Speak in English
  Future<void> speakEnglish(String text, {SpeechPriority priority = SpeechPriority.normal}) async {
    await speak(text, language: FeedbackLanguage.english, priority: priority);
  }

  /// Speak bilingual message
  Future<void> speakBilingual(String arabicText, String englishText) async {
    await speakArabic(arabicText);
    await speakEnglish(englishText);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Command Feedback
  // ═══════════════════════════════════════════════════════════════════════════

  /// Provide feedback for recognized command
  Future<void> announceCommandRecognized(ParsedVoiceCommand command) async {
    if (!_config.enableAudioFeedback) return;

    await playAudioFeedback(AudioFeedbackType.commandRecognized);

    final definition = VoiceCommandRegistry.getCommand(command.type);
    if (definition != null) {
      final text = command.isArabic
          ? 'تم التعرف على الأمر: ${definition.nameAr}'
          : 'Command recognized: ${definition.nameEn}';

      await speak(
        text,
        language: command.isArabic ? FeedbackLanguage.arabic : FeedbackLanguage.english,
        priority: SpeechPriority.high,
      );
    }
  }

  /// Provide feedback for unrecognized command
  Future<void> announceCommandNotRecognized({bool isArabic = true}) async {
    await playAudioFeedback(AudioFeedbackType.commandNotRecognized);

    final text = isArabic
        ? 'لم أفهم الأمر. قل "مساعدة" لعرض الأوامر المتاحة.'
        : 'I didn\'t understand. Say "help" to see available commands.';

    await speak(
      text,
      language: isArabic ? FeedbackLanguage.arabic : FeedbackLanguage.english,
    );
  }

  /// Announce listening started
  Future<void> announceListeningStarted({bool isArabic = true}) async {
    await playAudioFeedback(AudioFeedbackType.listeningStart);

    if (_config.enableHapticFeedback) {
      await HapticFeedback.mediumImpact();
    }
  }

  /// Announce listening stopped
  Future<void> announceListeningStopped({bool isArabic = true}) async {
    await playAudioFeedback(AudioFeedbackType.listeningStop);

    if (_config.enableHapticFeedback) {
      await HapticFeedback.lightImpact();
    }
  }

  /// Announce command executed successfully
  Future<void> announceSuccess(String messageAr, String messageEn, {bool isArabic = true}) async {
    await playAudioFeedback(AudioFeedbackType.success);

    if (_config.enableHapticFeedback) {
      await HapticFeedback.heavyImpact();
    }

    await speak(
      isArabic ? messageAr : messageEn,
      language: isArabic ? FeedbackLanguage.arabic : FeedbackLanguage.english,
    );
  }

  /// Announce error
  Future<void> announceError(String messageAr, String messageEn, {bool isArabic = true}) async {
    await playAudioFeedback(AudioFeedbackType.error);

    if (_config.enableHapticFeedback) {
      await HapticFeedback.vibrate();
    }

    await speak(
      isArabic ? messageAr : messageEn,
      language: isArabic ? FeedbackLanguage.arabic : FeedbackLanguage.english,
      priority: SpeechPriority.high,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Audio Feedback (Sound Effects)
  // ═══════════════════════════════════════════════════════════════════════════

  /// Play audio feedback sound
  Future<void> playAudioFeedback(AudioFeedbackType type) async {
    if (!_config.enableAudioFeedback) return;

    // Using system sounds since we don't have custom audio files
    // In production, you would use assets/sounds/ with audioplayers package

    try {
      switch (type) {
        case AudioFeedbackType.listeningStart:
          await HapticFeedback.selectionClick();
          break;
        case AudioFeedbackType.listeningStop:
          await HapticFeedback.selectionClick();
          break;
        case AudioFeedbackType.commandRecognized:
          await HapticFeedback.lightImpact();
          break;
        case AudioFeedbackType.commandNotRecognized:
          await HapticFeedback.mediumImpact();
          break;
        case AudioFeedbackType.commandExecuted:
          await HapticFeedback.heavyImpact();
          break;
        case AudioFeedbackType.error:
          await HapticFeedback.vibrate();
          break;
        case AudioFeedbackType.notification:
          await HapticFeedback.selectionClick();
          break;
        case AudioFeedbackType.success:
          await HapticFeedback.lightImpact();
          break;
        case AudioFeedbackType.warning:
          await HapticFeedback.mediumImpact();
          break;
      }
    } catch (e) {
      AppLogger.w('Failed to play audio feedback', tag: 'VOICE_TTS');
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Predefined Responses
  // ═══════════════════════════════════════════════════════════════════════════

  /// Get predefined response for command type
  VoiceFeedbackResponse getResponseForCommand(VoiceCommandType type) {
    return _predefinedResponses[type] ?? _defaultResponse;
  }

  static const _defaultResponse = VoiceFeedbackResponse(
    arabicText: 'جاري تنفيذ الأمر',
    englishText: 'Executing command',
  );

  static const Map<VoiceCommandType, VoiceFeedbackResponse> _predefinedResponses = {
    VoiceCommandType.openFields: VoiceFeedbackResponse(
      arabicText: 'جاري فتح قائمة الحقول',
      englishText: 'Opening fields list',
    ),
    VoiceCommandType.openWeather: VoiceFeedbackResponse(
      arabicText: 'جاري عرض حالة الطقس',
      englishText: 'Showing weather',
    ),
    VoiceCommandType.openNDVI: VoiceFeedbackResponse(
      arabicText: 'جاري فتح خريطة صحة النباتات',
      englishText: 'Opening vegetation health map',
    ),
    VoiceCommandType.openTasks: VoiceFeedbackResponse(
      arabicText: 'جاري فتح قائمة المهام',
      englishText: 'Opening tasks list',
    ),
    VoiceCommandType.scheduleIrrigation: VoiceFeedbackResponse(
      arabicText: 'جاري فتح جدولة الري',
      englishText: 'Opening irrigation schedule',
    ),
    VoiceCommandType.createTask: VoiceFeedbackResponse(
      arabicText: 'جاري إنشاء مهمة جديدة',
      englishText: 'Creating new task',
    ),
    VoiceCommandType.startScouting: VoiceFeedbackResponse(
      arabicText: 'جاري بدء جلسة الفحص الميداني',
      englishText: 'Starting field scouting session',
    ),
    VoiceCommandType.capturePhoto: VoiceFeedbackResponse(
      arabicText: 'جاري فتح الكاميرا',
      englishText: 'Opening camera',
    ),
    VoiceCommandType.help: VoiceFeedbackResponse(
      arabicText: 'جاري عرض الأوامر المتاحة',
      englishText: 'Showing available commands',
    ),
    VoiceCommandType.goBack: VoiceFeedbackResponse(
      arabicText: 'رجوع',
      englishText: 'Going back',
    ),
    VoiceCommandType.openHome: VoiceFeedbackResponse(
      arabicText: 'جاري الانتقال للرئيسية',
      englishText: 'Going to home',
    ),
    VoiceCommandType.dailySummary: VoiceFeedbackResponse(
      arabicText: 'جاري تحضير ملخص اليوم',
      englishText: 'Preparing daily summary',
    ),
  };

  // ═══════════════════════════════════════════════════════════════════════════
  // Configuration
  // ═══════════════════════════════════════════════════════════════════════════

  /// Update configuration
  Future<void> updateConfig(VoiceFeedbackConfig newConfig) async {
    _config = newConfig;
    await _configureTts();
    await setLanguage(newConfig.defaultLanguage);
  }

  /// Set speech rate
  Future<void> setSpeechRate(double rate) async {
    _config = _config.copyWith(speechRate: rate.clamp(0.0, 1.0));
    await _tts.setSpeechRate(_config.speechRate);
  }

  /// Set volume
  Future<void> setVolume(double volume) async {
    _config = _config.copyWith(volume: volume.clamp(0.0, 1.0));
    await _tts.setVolume(_config.volume);
  }

  /// Set pitch
  Future<void> setPitch(double pitch) async {
    _config = _config.copyWith(pitch: pitch.clamp(0.5, 2.0));
    await _tts.setPitch(_config.pitch);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Utilities
  // ═══════════════════════════════════════════════════════════════════════════

  void _updateStatus(VoiceFeedbackStatus newStatus) {
    if (_status == newStatus) return;
    _status = newStatus;
    _statusController.add(newStatus);
  }

  /// Dispose resources
  void dispose() {
    _tts.stop();
    _speechQueue.clear();
    _statusController.close();
    _speechProgressController.close();
  }
}

/// Voice feedback response model
class VoiceFeedbackResponse {
  final String arabicText;
  final String englishText;

  const VoiceFeedbackResponse({
    required this.arabicText,
    required this.englishText,
  });

  String getText(bool isArabic) => isArabic ? arabicText : englishText;
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Voice feedback service provider
final voiceFeedbackServiceProvider = Provider<VoiceFeedbackService>((ref) {
  return VoiceFeedbackService.instance;
});

/// Voice feedback status provider
final voiceFeedbackStatusProvider = StreamProvider<VoiceFeedbackStatus>((ref) {
  return VoiceFeedbackService.instance.statusStream;
});

/// Speech progress provider
final speechProgressProvider = StreamProvider<double>((ref) {
  return VoiceFeedbackService.instance.speechProgressStream;
});

/// Voice feedback config provider
final voiceFeedbackConfigProvider = StateProvider<VoiceFeedbackConfig>((ref) {
  return VoiceFeedbackService.instance.config;
});

/// Is speaking provider
final isSpeakingProvider = Provider<bool>((ref) {
  final status = ref.watch(voiceFeedbackStatusProvider);
  return status.when(
    data: (s) => s == VoiceFeedbackStatus.speaking,
    loading: () => false,
    error: (_, __) => false,
  );
});

// ═══════════════════════════════════════════════════════════════════════════
// Helper Extension
// ═══════════════════════════════════════════════════════════════════════════

extension VoiceFeedbackX on VoiceFeedbackService {
  /// Speak command response with appropriate language
  Future<void> speakCommandResponse(VoiceCommandType type, {required bool isArabic}) async {
    final response = getResponseForCommand(type);
    await speak(
      response.getText(isArabic),
      language: isArabic ? FeedbackLanguage.arabic : FeedbackLanguage.english,
    );
  }
}
