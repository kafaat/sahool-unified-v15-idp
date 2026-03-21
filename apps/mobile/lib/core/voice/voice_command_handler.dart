import 'dart:async';
import 'dart:math';
import 'package:flutter/widgets.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../utils/app_logger.dart';
import 'voice_service.dart';
import 'voice_commands.dart';
import 'voice_feedback.dart';

/// SAHOOL Voice Command Handler
/// معالج الأوامر الصوتية
///
/// Features:
/// - Parse recognized text into commands
/// - Map commands to app actions
/// - Execute navigation and operations
/// - Handle ambiguous commands
/// - Maintain command history
/// - Context-aware suggestions

// ═══════════════════════════════════════════════════════════════════════════
// Handler Result Models
// ═══════════════════════════════════════════════════════════════════════════

/// Command execution result
enum CommandExecutionStatus {
  success,
  partialSuccess,
  needsConfirmation,
  needsMoreInfo,
  failed,
  cancelled,
}

/// Result of command handling
class CommandHandlerResult {
  final ParsedVoiceCommand command;
  final CommandExecutionStatus status;
  final String? messageAr;
  final String? messageEn;
  final Map<String, dynamic>? resultData;
  final VoiceCommandType? suggestedCommand;
  final List<String>? clarificationOptions;
  final DateTime timestamp;

  CommandHandlerResult({
    required this.command,
    required this.status,
    this.messageAr,
    this.messageEn,
    this.resultData,
    this.suggestedCommand,
    this.clarificationOptions,
  }) : timestamp = DateTime.now();

  bool get isSuccess => status == CommandExecutionStatus.success;
  bool get needsMoreInfo => status == CommandExecutionStatus.needsMoreInfo;

  String getMessage(bool isArabic) {
    return (isArabic ? messageAr : messageEn) ?? '';
  }
}

/// Command execution context
class CommandContext {
  final BuildContext? buildContext;
  final String? currentRoute;
  final String? currentFieldId;
  final Map<String, dynamic> additionalData;

  const CommandContext({
    this.buildContext,
    this.currentRoute,
    this.currentFieldId,
    this.additionalData = const {},
  });

  CommandContext copyWith({
    BuildContext? buildContext,
    String? currentRoute,
    String? currentFieldId,
    Map<String, dynamic>? additionalData,
  }) {
    return CommandContext(
      buildContext: buildContext ?? this.buildContext,
      currentRoute: currentRoute ?? this.currentRoute,
      currentFieldId: currentFieldId ?? this.currentFieldId,
      additionalData: additionalData ?? this.additionalData,
    );
  }
}

/// Command history entry
class CommandHistoryEntry {
  final ParsedVoiceCommand command;
  final CommandHandlerResult result;
  final DateTime executedAt;

  const CommandHistoryEntry({
    required this.command,
    required this.result,
    required this.executedAt,
  });
}

// ═══════════════════════════════════════════════════════════════════════════
// Navigation Routes
// ═══════════════════════════════════════════════════════════════════════════

/// App route definitions for voice navigation
class VoiceRoutes {
  static const String home = '/';
  static const String fields = '/fields';
  static const String fieldDetails = '/fields/:id';
  static const String weather = '/weather';
  static const String ndvi = '/ndvi';
  static const String tasks = '/tasks';
  static const String createTask = '/tasks/create';
  static const String advisor = '/advisor';
  static const String settings = '/settings';
  static const String irrigation = '/irrigation';
  static const String irrigationSchedule = '/irrigation/schedule';
  static const String scouting = '/scouting';
  static const String camera = '/camera';
  static const String reports = '/reports';
  static const String help = '/help';
}

// ═══════════════════════════════════════════════════════════════════════════
// Voice Command Handler
// ═══════════════════════════════════════════════════════════════════════════

class VoiceCommandHandler {
  final VoiceService _voiceService;
  final VoiceFeedbackService _feedbackService;

  // Command history
  final List<CommandHistoryEntry> _history = [];
  static const int _maxHistorySize = 50;

  // Current context
  CommandContext _context = const CommandContext();

  // Pending confirmation
  ParsedVoiceCommand? _pendingCommand;

  // Callbacks
  final Map<VoiceCommandType, Future<CommandHandlerResult> Function(ParsedVoiceCommand, CommandContext)>
      _customHandlers = {};

  // Stream controllers
  final _resultController = StreamController<CommandHandlerResult>.broadcast();
  final _suggestionController = StreamController<List<VoiceCommandDefinition>>.broadcast();

  VoiceCommandHandler({
    VoiceService? voiceService,
    VoiceFeedbackService? feedbackService,
  })  : _voiceService = voiceService ?? VoiceService.instance,
        _feedbackService = feedbackService ?? VoiceFeedbackService.instance {
    _setupListeners();
  }

  // Getters
  List<CommandHistoryEntry> get history => List.unmodifiable(_history);
  CommandContext get context => _context;
  Stream<CommandHandlerResult> get resultStream => _resultController.stream;
  Stream<List<VoiceCommandDefinition>> get suggestionStream => _suggestionController.stream;

  // ═══════════════════════════════════════════════════════════════════════════
  // Setup
  // ═══════════════════════════════════════════════════════════════════════════

  void _setupListeners() {
    // Listen to speech results
    _voiceService.resultStream.listen((result) {
      if (result.isFinal && result.recognizedText.isNotEmpty) {
        handleSpeechResult(result);
      } else if (!result.isFinal) {
        // Provide real-time suggestions based on partial input
        _provideSuggestions(result.recognizedText);
      }
    });
  }

  /// Initialize handler
  Future<void> initialize() async {
    await _voiceService.initialize();
    await _feedbackService.initialize();
    AppLogger.i('Voice command handler initialized', tag: 'VOICE_HANDLER');
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Context Management
  // ═══════════════════════════════════════════════════════════════════════════

  /// Update command context
  void updateContext(CommandContext newContext) {
    _context = newContext;
    AppLogger.d('Command context updated', tag: 'VOICE_HANDLER', data: {
      'route': newContext.currentRoute,
      'fieldId': newContext.currentFieldId,
    });
  }

  /// Set current route
  void setCurrentRoute(String route) {
    _context = _context.copyWith(currentRoute: route);
  }

  /// Set current field
  void setCurrentField(String fieldId) {
    _context = _context.copyWith(currentFieldId: fieldId);
  }

  /// Set build context
  void setBuildContext(BuildContext context) {
    _context = _context.copyWith(buildContext: context);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Command Processing
  // ═══════════════════════════════════════════════════════════════════════════

  /// Handle speech recognition result
  Future<CommandHandlerResult> handleSpeechResult(SpeechResult result) async {
    AppLogger.i('Processing speech result: "${result.recognizedText}"', tag: 'VOICE_HANDLER');

    // Parse the command
    final command = VoiceCommandParser.parse(result.recognizedText);

    // Handle the parsed command
    return await handleCommand(command);
  }

  /// Handle parsed command
  Future<CommandHandlerResult> handleCommand(ParsedVoiceCommand command) async {
    AppLogger.i('Handling command: ${command.type.id}', tag: 'VOICE_HANDLER', data: {
      'confidence': '${(command.confidence * 100).toStringAsFixed(1)}%',
      'params': command.parameters,
    });

    CommandHandlerResult result;

    if (!command.isRecognized) {
      // Command not recognized
      result = await _handleUnknownCommand(command);
    } else if (!command.isHighConfidence) {
      // Low confidence - ask for confirmation
      result = await _handleLowConfidenceCommand(command);
    } else {
      // Execute the command
      result = await _executeCommand(command);
    }

    // Add to history
    _addToHistory(command, result);

    // Emit result
    _resultController.add(result);

    // Provide audio feedback
    await _provideFeedback(result);

    return result;
  }

  /// Handle unknown/unrecognized command
  Future<CommandHandlerResult> _handleUnknownCommand(ParsedVoiceCommand command) async {
    AppLogger.d('Unknown command: "${command.rawText}"', tag: 'VOICE_HANDLER');

    // Try to suggest similar commands
    final suggestions = _getSimilarCommands(command.rawText, command.isArabic);

    return CommandHandlerResult(
      command: command,
      status: CommandExecutionStatus.failed,
      messageAr: 'لم أفهم الأمر. جرب أن تقول مثلاً "${suggestions.firstOrNull?.nameAr ?? 'افتح الحقول'}"',
      messageEn: 'I didn\'t understand. Try saying "${suggestions.firstOrNull?.nameEn ?? 'Open fields'}"',
      clarificationOptions: suggestions.map((s) => command.isArabic ? s.nameAr : s.nameEn).toList(),
    );
  }

  /// Handle low confidence command
  Future<CommandHandlerResult> _handleLowConfidenceCommand(ParsedVoiceCommand command) async {
    final definition = VoiceCommandRegistry.getCommand(command.type);

    _pendingCommand = command;

    return CommandHandlerResult(
      command: command,
      status: CommandExecutionStatus.needsConfirmation,
      messageAr: 'هل تقصد "${definition?.nameAr ?? command.type.id}"؟',
      messageEn: 'Did you mean "${definition?.nameEn ?? command.type.id}"?',
    );
  }

  /// Execute recognized command
  Future<CommandHandlerResult> _executeCommand(ParsedVoiceCommand command) async {
    // Check for custom handler first
    if (_customHandlers.containsKey(command.type)) {
      try {
        return await _customHandlers[command.type]!(command, _context);
      } catch (e, stack) {
        AppLogger.e('Custom handler error', tag: 'VOICE_HANDLER', error: e, stackTrace: stack);
      }
    }

    // Use default handler
    return await _defaultCommandHandler(command);
  }

  /// Default command handler implementation
  Future<CommandHandlerResult> _defaultCommandHandler(ParsedVoiceCommand command) async {
    final ctx = _context.buildContext;

    switch (command.type) {
      // ─────────────────────────────────────────────────────────────────────
      // Navigation Commands
      // ─────────────────────────────────────────────────────────────────────
      case VoiceCommandType.openFields:
        return _navigateTo(command, VoiceRoutes.fields,
            messageAr: 'جاري فتح الحقول', messageEn: 'Opening fields');

      case VoiceCommandType.openWeather:
        return _navigateTo(command, VoiceRoutes.weather,
            messageAr: 'جاري فتح الطقس', messageEn: 'Opening weather');

      case VoiceCommandType.openNDVI:
        return _navigateTo(command, VoiceRoutes.ndvi,
            messageAr: 'جاري فتح خريطة NDVI', messageEn: 'Opening NDVI map');

      case VoiceCommandType.openTasks:
        return _navigateTo(command, VoiceRoutes.tasks,
            messageAr: 'جاري فتح المهام', messageEn: 'Opening tasks');

      case VoiceCommandType.openAdvisor:
        return _navigateTo(command, VoiceRoutes.advisor,
            messageAr: 'جاري فتح المستشار', messageEn: 'Opening advisor');

      case VoiceCommandType.openSettings:
        return _navigateTo(command, VoiceRoutes.settings,
            messageAr: 'جاري فتح الإعدادات', messageEn: 'Opening settings');

      case VoiceCommandType.openHome:
        return _navigateTo(command, VoiceRoutes.home,
            messageAr: 'جاري الانتقال للرئيسية', messageEn: 'Going to home');

      case VoiceCommandType.goBack:
        if (ctx != null && ctx.mounted) {
          if (GoRouter.of(ctx).canPop()) {
            GoRouter.of(ctx).pop();
            return _successResult(command, messageAr: 'رجوع', messageEn: 'Going back');
          }
        }
        return _failedResult(command,
            messageAr: 'لا يمكن الرجوع', messageEn: 'Cannot go back');

      // ─────────────────────────────────────────────────────────────────────
      // Field Operations
      // ─────────────────────────────────────────────────────────────────────
      case VoiceCommandType.selectField:
        final fieldId = command.parameters['fieldId'];
        if (fieldId != null) {
          return _navigateTo(command, '/fields/$fieldId',
              messageAr: 'جاري فتح الحقل $fieldId', messageEn: 'Opening field $fieldId');
        }
        return _needsMoreInfo(command,
            messageAr: 'أي حقل تريد فتحه؟', messageEn: 'Which field do you want to open?');

      case VoiceCommandType.viewFieldDetails:
        final fieldId = command.parameters['fieldId'] ?? _context.currentFieldId;
        if (fieldId != null) {
          return _navigateTo(command, '/fields/$fieldId',
              messageAr: 'جاري عرض تفاصيل الحقل', messageEn: 'Showing field details');
        }
        return _needsMoreInfo(command,
            messageAr: 'أي حقل تريد عرض تفاصيله؟', messageEn: 'Which field details do you want?');

      case VoiceCommandType.checkNDVI:
        final fieldId = command.parameters['fieldId'] ?? _context.currentFieldId;
        if (fieldId != null) {
          return _navigateTo(command, '/ndvi/$fieldId',
              messageAr: 'جاري فحص NDVI للحقل', messageEn: 'Checking field NDVI');
        }
        return _navigateTo(command, VoiceRoutes.ndvi,
            messageAr: 'جاري فتح خريطة NDVI', messageEn: 'Opening NDVI map');

      case VoiceCommandType.viewCropHealth:
        return _successResult(command,
            messageAr: 'جاري عرض صحة المحصول', messageEn: 'Showing crop health',
            resultData: {'action': 'show_crop_health'});

      // ─────────────────────────────────────────────────────────────────────
      // Irrigation Commands
      // ─────────────────────────────────────────────────────────────────────
      case VoiceCommandType.scheduleIrrigation:
        return _navigateTo(command, VoiceRoutes.irrigationSchedule,
            messageAr: 'جاري فتح جدولة الري', messageEn: 'Opening irrigation schedule');

      case VoiceCommandType.recordIrrigation:
        final fieldId = command.parameters['fieldId'] ?? _context.currentFieldId;
        return _successResult(command,
            messageAr: 'جاري تسجيل عملية الري', messageEn: 'Recording irrigation',
            resultData: {'action': 'record_irrigation', 'fieldId': fieldId});

      case VoiceCommandType.stopIrrigation:
        return _successResult(command,
            messageAr: 'جاري إيقاف الري', messageEn: 'Stopping irrigation',
            resultData: {'action': 'stop_irrigation'});

      case VoiceCommandType.checkIrrigationStatus:
        return _navigateTo(command, VoiceRoutes.irrigation,
            messageAr: 'جاري عرض حالة الري', messageEn: 'Showing irrigation status');

      // ─────────────────────────────────────────────────────────────────────
      // Task Commands
      // ─────────────────────────────────────────────────────────────────────
      case VoiceCommandType.createTask:
        return _navigateTo(command, VoiceRoutes.createTask,
            messageAr: 'جاري إنشاء مهمة جديدة', messageEn: 'Creating new task');

      case VoiceCommandType.viewTodayTasks:
        return _navigateTo(command, '${VoiceRoutes.tasks}?filter=today',
            messageAr: 'جاري عرض مهام اليوم', messageEn: 'Showing today\'s tasks');

      case VoiceCommandType.completeTask:
        final taskId = command.parameters['taskId'];
        if (taskId != null) {
          return _successResult(command,
              messageAr: 'جاري إكمال المهمة $taskId', messageEn: 'Completing task $taskId',
              resultData: {'action': 'complete_task', 'taskId': taskId});
        }
        return _needsMoreInfo(command,
            messageAr: 'أي مهمة تريد إكمالها؟', messageEn: 'Which task do you want to complete?');

      case VoiceCommandType.showOverdueTasks:
        return _navigateTo(command, '${VoiceRoutes.tasks}?filter=overdue',
            messageAr: 'جاري عرض المهام المتأخرة', messageEn: 'Showing overdue tasks');

      // ─────────────────────────────────────────────────────────────────────
      // Weather Commands
      // ─────────────────────────────────────────────────────────────────────
      case VoiceCommandType.showWeather:
        return _navigateTo(command, VoiceRoutes.weather,
            messageAr: 'جاري عرض الطقس الحالي', messageEn: 'Showing current weather');

      case VoiceCommandType.showForecast:
        return _navigateTo(command, '${VoiceRoutes.weather}?view=forecast',
            messageAr: 'جاري عرض توقعات الطقس', messageEn: 'Showing weather forecast');

      case VoiceCommandType.checkRainProbability:
        return _successResult(command,
            messageAr: 'جاري التحقق من احتمال المطر', messageEn: 'Checking rain probability',
            resultData: {'action': 'check_rain'});

      // ─────────────────────────────────────────────────────────────────────
      // Scouting & Reports
      // ─────────────────────────────────────────────────────────────────────
      case VoiceCommandType.startScouting:
        return _navigateTo(command, VoiceRoutes.scouting,
            messageAr: 'جاري بدء الفحص الميداني', messageEn: 'Starting field scouting');

      case VoiceCommandType.capturePhoto:
        return _navigateTo(command, VoiceRoutes.camera,
            messageAr: 'جاري فتح الكاميرا', messageEn: 'Opening camera');

      case VoiceCommandType.reportProblem:
        return _successResult(command,
            messageAr: 'جاري فتح نموذج الإبلاغ عن مشكلة', messageEn: 'Opening problem report form',
            resultData: {'action': 'report_problem'});

      case VoiceCommandType.viewReports:
        return _navigateTo(command, VoiceRoutes.reports,
            messageAr: 'جاري عرض التقارير', messageEn: 'Showing reports');

      // ─────────────────────────────────────────────────────────────────────
      // Advisory
      // ─────────────────────────────────────────────────────────────────────
      case VoiceCommandType.getAdvice:
        return _navigateTo(command, VoiceRoutes.advisor,
            messageAr: 'جاري فتح المستشار الزراعي', messageEn: 'Opening agricultural advisor');

      case VoiceCommandType.askQuestion:
        return _navigateTo(command, '${VoiceRoutes.advisor}?mode=chat',
            messageAr: 'تفضل اسأل سؤالك', messageEn: 'Go ahead, ask your question');

      // ─────────────────────────────────────────────────────────────────────
      // Utility Commands
      // ─────────────────────────────────────────────────────────────────────
      case VoiceCommandType.help:
        return _successResult(command,
            messageAr: 'جاري عرض الأوامر المتاحة', messageEn: 'Showing available commands',
            resultData: {'action': 'show_help', 'commands': VoiceCommandRegistry.commands.length});

      case VoiceCommandType.cancel:
        _pendingCommand = null;
        return _successResult(command, messageAr: 'تم الإلغاء', messageEn: 'Cancelled');

      case VoiceCommandType.repeat:
        final lastEntry = _history.lastOrNull;
        if (lastEntry != null) {
          return _successResult(command,
              messageAr: lastEntry.result.messageAr ?? 'لا يوجد رد سابق',
              messageEn: lastEntry.result.messageEn ?? 'No previous response');
        }
        return _failedResult(command,
            messageAr: 'لا يوجد رد سابق للتكرار', messageEn: 'No previous response to repeat');

      case VoiceCommandType.dailySummary:
        return _successResult(command,
            messageAr: 'جاري تحضير ملخص اليوم', messageEn: 'Preparing daily summary',
            resultData: {'action': 'daily_summary'});

      case VoiceCommandType.unknown:
      default:
        return _handleUnknownCommand(command);
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Helper Methods
  // ═══════════════════════════════════════════════════════════════════════════

  CommandHandlerResult _navigateTo(
    ParsedVoiceCommand command,
    String route, {
    required String messageAr,
    required String messageEn,
  }) {
    final ctx = _context.buildContext;

    if (ctx != null && ctx.mounted) {
      try {
        GoRouter.of(ctx).go(route);
        return _successResult(command, messageAr: messageAr, messageEn: messageEn,
            resultData: {'route': route});
      } catch (e) {
        AppLogger.e('Navigation error', tag: 'VOICE_HANDLER', error: e);
      }
    }

    // Return success anyway - navigation will be handled by listener
    return CommandHandlerResult(
      command: command,
      status: CommandExecutionStatus.success,
      messageAr: messageAr,
      messageEn: messageEn,
      resultData: {'route': route, 'deferred': true},
    );
  }

  CommandHandlerResult _successResult(
    ParsedVoiceCommand command, {
    required String messageAr,
    required String messageEn,
    Map<String, dynamic>? resultData,
  }) {
    return CommandHandlerResult(
      command: command,
      status: CommandExecutionStatus.success,
      messageAr: messageAr,
      messageEn: messageEn,
      resultData: resultData,
    );
  }

  CommandHandlerResult _failedResult(
    ParsedVoiceCommand command, {
    required String messageAr,
    required String messageEn,
  }) {
    return CommandHandlerResult(
      command: command,
      status: CommandExecutionStatus.failed,
      messageAr: messageAr,
      messageEn: messageEn,
    );
  }

  CommandHandlerResult _needsMoreInfo(
    ParsedVoiceCommand command, {
    required String messageAr,
    required String messageEn,
  }) {
    return CommandHandlerResult(
      command: command,
      status: CommandExecutionStatus.needsMoreInfo,
      messageAr: messageAr,
      messageEn: messageEn,
    );
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Suggestions
  // ═══════════════════════════════════════════════════════════════════════════

  void _provideSuggestions(String partialText) {
    if (partialText.length < 2) return;

    final suggestions = _getSimilarCommands(partialText, _containsArabic(partialText));
    _suggestionController.add(suggestions);
  }

  List<VoiceCommandDefinition> _getSimilarCommands(String text, bool isArabic) {
    final normalizedText = isArabic ? _normalizeArabic(text) : text.toLowerCase();

    final scored = <MapEntry<VoiceCommandDefinition, double>>[];

    for (final cmd in VoiceCommandRegistry.commands) {
      if (cmd.type == VoiceCommandType.unknown) continue;

      final patterns = isArabic ? cmd.patternsAr : cmd.patternsEn;
      double bestScore = 0;

      for (final pattern in patterns) {
        final normalizedPattern = isArabic ? _normalizeArabic(pattern) : pattern.toLowerCase();

        // Check if pattern starts with or contains the text
        if (normalizedPattern.startsWith(normalizedText)) {
          bestScore = 0.9;
          break;
        } else if (normalizedPattern.contains(normalizedText)) {
          bestScore = max(bestScore, 0.7);
        } else if (normalizedText.contains(normalizedPattern)) {
          bestScore = max(bestScore, 0.6);
        }
      }

      if (bestScore > 0.5) {
        scored.add(MapEntry(cmd, bestScore));
      }
    }

    // Sort by score descending
    scored.sort((a, b) => b.value.compareTo(a.value));

    return scored.take(5).map((e) => e.key).toList();
  }

  bool _containsArabic(String text) {
    return RegExp(r'[\u0600-\u06FF]').hasMatch(text);
  }

  String _normalizeArabic(String text) {
    return text
        .replaceAll('أ', 'ا')
        .replaceAll('إ', 'ا')
        .replaceAll('آ', 'ا')
        .replaceAll('ة', 'ه')
        .replaceAll('ى', 'ي')
        .replaceAll(RegExp(r'[\u064B-\u065F]'), '')
        .trim();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Feedback
  // ═══════════════════════════════════════════════════════════════════════════

  Future<void> _provideFeedback(CommandHandlerResult result) async {
    final isArabic = result.command.isArabic;

    switch (result.status) {
      case CommandExecutionStatus.success:
        await _feedbackService.announceSuccess(
          result.messageAr ?? '',
          result.messageEn ?? '',
          isArabic: isArabic,
        );
        break;

      case CommandExecutionStatus.needsConfirmation:
        await _feedbackService.speak(
          result.getMessage(isArabic),
          language: isArabic ? FeedbackLanguage.arabic : FeedbackLanguage.english,
        );
        break;

      case CommandExecutionStatus.needsMoreInfo:
        await _feedbackService.speak(
          result.getMessage(isArabic),
          language: isArabic ? FeedbackLanguage.arabic : FeedbackLanguage.english,
        );
        break;

      case CommandExecutionStatus.failed:
        await _feedbackService.announceCommandNotRecognized(isArabic: isArabic);
        break;

      default:
        break;
    }
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // History
  // ═══════════════════════════════════════════════════════════════════════════

  void _addToHistory(ParsedVoiceCommand command, CommandHandlerResult result) {
    _history.add(CommandHistoryEntry(
      command: command,
      result: result,
      executedAt: DateTime.now(),
    ));

    if (_history.length > _maxHistorySize) {
      _history.removeAt(0);
    }
  }

  void clearHistory() {
    _history.clear();
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Custom Handlers
  // ═══════════════════════════════════════════════════════════════════════════

  /// Register a custom handler for a command type
  void registerHandler(
    VoiceCommandType type,
    Future<CommandHandlerResult> Function(ParsedVoiceCommand, CommandContext) handler,
  ) {
    _customHandlers[type] = handler;
  }

  /// Unregister a custom handler
  void unregisterHandler(VoiceCommandType type) {
    _customHandlers.remove(type);
  }

  // ═══════════════════════════════════════════════════════════════════════════
  // Confirmation
  // ═══════════════════════════════════════════════════════════════════════════

  /// Confirm pending command
  Future<CommandHandlerResult?> confirmPendingCommand() async {
    if (_pendingCommand == null) return null;

    final command = _pendingCommand!;
    _pendingCommand = null;

    return await _executeCommand(command);
  }

  /// Cancel pending command
  void cancelPendingCommand() {
    _pendingCommand = null;
  }

  /// Check if there's a pending command
  bool get hasPendingCommand => _pendingCommand != null;

  // ═══════════════════════════════════════════════════════════════════════════
  // Cleanup
  // ═══════════════════════════════════════════════════════════════════════════

  void dispose() {
    _resultController.close();
    _suggestionController.close();
  }
}

// ═══════════════════════════════════════════════════════════════════════════
// Riverpod Providers
// ═══════════════════════════════════════════════════════════════════════════

/// Voice command handler provider
final voiceCommandHandlerProvider = Provider<VoiceCommandHandler>((ref) {
  final handler = VoiceCommandHandler();
  ref.onDispose(handler.dispose);
  return handler;
});

/// Command result stream provider
final commandResultProvider = StreamProvider<CommandHandlerResult>((ref) {
  final handler = ref.watch(voiceCommandHandlerProvider);
  return handler.resultStream;
});

/// Command suggestions stream provider
final commandSuggestionsProvider = StreamProvider<List<VoiceCommandDefinition>>((ref) {
  final handler = ref.watch(voiceCommandHandlerProvider);
  return handler.suggestionStream;
});

/// Command history provider
final commandHistoryProvider = Provider<List<CommandHistoryEntry>>((ref) {
  final handler = ref.watch(voiceCommandHandlerProvider);
  return handler.history;
});
