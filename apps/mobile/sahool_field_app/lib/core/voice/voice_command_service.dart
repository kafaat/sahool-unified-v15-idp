import 'dart:async';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../utils/app_logger.dart';

/// SAHOOL Voice Command Service
/// خدمة الأوامر الصوتية
///
/// Features:
/// - Arabic speech recognition
/// - Command parsing and execution
/// - Offline-capable (when possible)
/// - Farmer-friendly commands

class VoiceCommandService {
  static VoiceCommandService? _instance;
  static VoiceCommandService get instance {
    _instance ??= VoiceCommandService._();
    return _instance!;
  }

  VoiceCommandService._();

  bool _isInitialized = false;
  bool _isListening = false;
  String _currentLanguage = 'ar-YE'; // Yemeni Arabic

  final _statusController = StreamController<VoiceStatus>.broadcast();
  Stream<VoiceStatus> get statusStream => _statusController.stream;

  final _resultController = StreamController<VoiceResult>.broadcast();
  Stream<VoiceResult> get resultStream => _resultController.stream;

  VoiceStatus _currentStatus = VoiceStatus.idle;
  VoiceStatus get currentStatus => _currentStatus;

  bool get isListening => _isListening;

  // ═══════════════════════════════════════════════════════════════════════════
  // التهيئة
  // ═══════════════════════════════════════════════════════════════════════════

  /// تهيئة خدمة الصوت
  Future<bool> initialize() async {
    if (_isInitialized) return true;

    try {
      // In real implementation, initialize speech_to_text package
      // await _speech.initialize();

      _isInitialized = true;
      _updateStatus(VoiceStatus.ready);

      AppLogger.i('Voice command service initialized', tag: 'VOICE');
      return true;
    } catch (e) {
      AppLogger.e('Failed to initialize voice service', tag: 'VOICE', error: e);
      _updateStatus(VoiceStatus.error);
      return false;
    }
  }

  /// تغيير اللغة
  void setLanguage(String locale) {
    _currentLanguage = locale;
    AppLogger.d('Voice language set to: $locale', tag: 'VOICE');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // الاستماع
  // ═══════════════════════════════════════════════════════════════════════════

  /// بدء الاستماع
  Future<void> startListening() async {
    if (!_isInitialized) {
      await initialize();
    }

    if (_isListening) return;

    _isListening = true;
    _updateStatus(VoiceStatus.listening);

    AppLogger.d('Started listening...', tag: 'VOICE');

    // In real implementation, use speech_to_text
    // _speech.listen(
    //   onResult: _onSpeechResult,
    //   localeId: _currentLanguage,
    // );

    // Simulate for now
    Timer(const Duration(seconds: 3), () {
      if (_isListening) {
        _processResult('افتح الحقل الأول');
      }
    });
  }

  /// إيقاف الاستماع
  Future<void> stopListening() async {
    if (!_isListening) return;

    _isListening = false;
    _updateStatus(VoiceStatus.processing);

    // In real implementation
    // await _speech.stop();

    AppLogger.d('Stopped listening', tag: 'VOICE');
  }

  /// إلغاء الاستماع
  void cancelListening() {
    _isListening = false;
    _updateStatus(VoiceStatus.idle);

    // In real implementation
    // _speech.cancel();

    AppLogger.d('Listening cancelled', tag: 'VOICE');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // معالجة النتائج
  // ═══════════════════════════════════════════════════════════════════════════

  void _processResult(String text) {
    _updateStatus(VoiceStatus.processing);

    final command = _parseCommand(text);

    final result = VoiceResult(
      text: text,
      command: command,
      confidence: 0.85,
      timestamp: DateTime.now(),
    );

    _resultController.add(result);
    _updateStatus(VoiceStatus.ready);

    AppLogger.i('Voice command parsed: ${command?.type.name ?? "unknown"}', tag: 'VOICE');
  }

  /// تحليل الأمر من النص
  VoiceCommand? _parseCommand(String text) {
    final normalized = _normalizeText(text);

    // فتح حقل
    if (_matchesPattern(normalized, ['افتح', 'فتح', 'اعرض', 'شوف'], ['حقل', 'الحقل'])) {
      final fieldId = _extractFieldIdentifier(normalized);
      return VoiceCommand(
        type: VoiceCommandType.openField,
        parameters: {'fieldId': fieldId},
        rawText: text,
      );
    }

    // حالة المحصول
    if (_matchesPattern(normalized, ['حالة', 'كيف', 'ما'], ['محصول', 'المحصول', 'الزراعة'])) {
      return VoiceCommand(
        type: VoiceCommandType.cropStatus,
        parameters: {},
        rawText: text,
      );
    }

    // تسجيل ري
    if (_matchesPattern(normalized, ['سجل', 'اضف', 'ابدأ'], ['ري', 'الري', 'سقي'])) {
      final fieldId = _extractFieldIdentifier(normalized);
      return VoiceCommand(
        type: VoiceCommandType.recordIrrigation,
        parameters: {'fieldId': fieldId},
        rawText: text,
      );
    }

    // عرض المهام
    if (_matchesPattern(normalized, ['عرض', 'اعرض', 'شوف', 'ما'], ['مهام', 'المهام', 'الأعمال'])) {
      return VoiceCommand(
        type: VoiceCommandType.showTasks,
        parameters: {},
        rawText: text,
      );
    }

    // إضافة مهمة
    if (_matchesPattern(normalized, ['اضف', 'سجل', 'انشئ'], ['مهمة', 'عمل', 'شغل'])) {
      return VoiceCommand(
        type: VoiceCommandType.createTask,
        parameters: {},
        rawText: text,
      );
    }

    // الطقس
    if (_matchesPattern(normalized, ['كيف', 'ما', 'شو'], ['طقس', 'الطقس', 'الجو'])) {
      return VoiceCommand(
        type: VoiceCommandType.weather,
        parameters: {},
        rawText: text,
      );
    }

    // بدء مسح
    if (_matchesPattern(normalized, ['ابدأ', 'بدء', 'شغل'], ['مسح', 'فحص', 'جولة'])) {
      return VoiceCommand(
        type: VoiceCommandType.startScout,
        parameters: {},
        rawText: text,
      );
    }

    // تسجيل مشكلة
    if (_matchesPattern(normalized, ['سجل', 'في'], ['مشكلة', 'آفة', 'مرض', 'حشرة'])) {
      return VoiceCommand(
        type: VoiceCommandType.reportIssue,
        parameters: {},
        rawText: text,
      );
    }

    // التقاط صورة
    if (_matchesPattern(normalized, ['صور', 'التقط', 'خذ'], ['صورة', 'صوره'])) {
      return VoiceCommand(
        type: VoiceCommandType.capturePhoto,
        parameters: {},
        rawText: text,
      );
    }

    // ملخص اليوم
    if (_matchesPattern(normalized, ['ملخص', 'تقرير', 'ايش', 'شو'], ['اليوم', 'يومي'])) {
      return VoiceCommand(
        type: VoiceCommandType.dailySummary,
        parameters: {},
        rawText: text,
      );
    }

    // مساعدة
    if (_matchesPattern(normalized, ['مساعدة', 'ساعدني', 'كيف', 'شو'], ['اقول', 'اسوي', 'استخدم'])) {
      return VoiceCommand(
        type: VoiceCommandType.help,
        parameters: {},
        rawText: text,
      );
    }

    // لم يتم التعرف على الأمر
    return VoiceCommand(
      type: VoiceCommandType.unknown,
      parameters: {},
      rawText: text,
    );
  }

  /// تطبيع النص
  String _normalizeText(String text) {
    return text
        .toLowerCase()
        .replaceAll('أ', 'ا')
        .replaceAll('إ', 'ا')
        .replaceAll('آ', 'ا')
        .replaceAll('ة', 'ه')
        .replaceAll('ى', 'ي')
        .trim();
  }

  /// التحقق من تطابق النمط
  bool _matchesPattern(String text, List<String> actions, List<String> targets) {
    final hasAction = actions.any((a) => text.contains(a));
    final hasTarget = targets.any((t) => text.contains(t));
    return hasAction && hasTarget;
  }

  /// استخراج معرف الحقل
  String? _extractFieldIdentifier(String text) {
    // Try to extract field number or name
    final numberPattern = RegExp(r'(?:حقل|الحقل)\s*(?:رقم)?\s*(\d+|الأول|الثاني|الثالث|الرابع|الخامس)');
    final match = numberPattern.firstMatch(text);

    if (match != null) {
      final value = match.group(1);
      return switch (value) {
        'الأول' => '1',
        'الثاني' => '2',
        'الثالث' => '3',
        'الرابع' => '4',
        'الخامس' => '5',
        _ => value,
      };
    }

    return null;
  }

  /// تحديث الحالة
  void _updateStatus(VoiceStatus status) {
    _currentStatus = status;
    _statusController.add(status);
  }

  /// الحصول على أوامر المساعدة
  List<VoiceHelpItem> getHelpCommands() {
    return [
      const VoiceHelpItem(
        command: 'افتح حقل رقم 1',
        description: 'فتح تفاصيل حقل معين',
        examples: ['افتح الحقل الأول', 'اعرض حقل 3'],
      ),
      const VoiceHelpItem(
        command: 'حالة المحصول',
        description: 'عرض حالة المحصول الحالية',
        examples: ['كيف المحصول', 'ما حالة الزراعة'],
      ),
      const VoiceHelpItem(
        command: 'سجل ري',
        description: 'تسجيل عملية ري جديدة',
        examples: ['سجل ري للحقل 1', 'ابدأ الري'],
      ),
      const VoiceHelpItem(
        command: 'عرض المهام',
        description: 'عرض قائمة المهام',
        examples: ['ما المهام اليوم', 'شوف الأعمال'],
      ),
      const VoiceHelpItem(
        command: 'كيف الطقس',
        description: 'عرض حالة الطقس',
        examples: ['ما الطقس', 'شو الجو اليوم'],
      ),
      const VoiceHelpItem(
        command: 'ابدأ مسح',
        description: 'بدء جلسة مسح للحقل',
        examples: ['ابدأ جولة فحص', 'شغل المسح'],
      ),
      const VoiceHelpItem(
        command: 'التقط صورة',
        description: 'التقاط صورة للتوثيق',
        examples: ['صور', 'خذ صورة'],
      ),
      const VoiceHelpItem(
        command: 'ملخص اليوم',
        description: 'عرض ملخص اليوم',
        examples: ['تقرير اليوم', 'ايش صار اليوم'],
      ),
    ];
  }

  /// إغلاق الخدمة
  void dispose() {
    _statusController.close();
    _resultController.close();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// النماذج
// ═══════════════════════════════════════════════════════════════════════════

/// حالة خدمة الصوت
enum VoiceStatus {
  idle,
  ready,
  listening,
  processing,
  error,
}

/// نوع الأمر الصوتي
enum VoiceCommandType {
  openField,
  cropStatus,
  recordIrrigation,
  showTasks,
  createTask,
  weather,
  startScout,
  reportIssue,
  capturePhoto,
  dailySummary,
  help,
  unknown,
}

/// أمر صوتي
class VoiceCommand {
  final VoiceCommandType type;
  final Map<String, dynamic> parameters;
  final String rawText;

  const VoiceCommand({
    required this.type,
    required this.parameters,
    required this.rawText,
  });

  bool get isRecognized => type != VoiceCommandType.unknown;
}

/// نتيجة الصوت
class VoiceResult {
  final String text;
  final VoiceCommand? command;
  final double confidence;
  final DateTime timestamp;

  const VoiceResult({
    required this.text,
    this.command,
    required this.confidence,
    required this.timestamp,
  });
}

/// عنصر مساعدة صوتية
class VoiceHelpItem {
  final String command;
  final String description;
  final List<String> examples;

  const VoiceHelpItem({
    required this.command,
    required this.description,
    required this.examples,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Providers
// ═══════════════════════════════════════════════════════════════════════════

final voiceCommandServiceProvider = Provider<VoiceCommandService>((ref) {
  return VoiceCommandService.instance;
});

final voiceStatusProvider = StreamProvider<VoiceStatus>((ref) {
  return VoiceCommandService.instance.statusStream;
});

final voiceResultProvider = StreamProvider<VoiceResult>((ref) {
  return VoiceCommandService.instance.resultStream;
});

final voiceHelpProvider = Provider<List<VoiceHelpItem>>((ref) {
  return VoiceCommandService.instance.getHelpCommands();
});
