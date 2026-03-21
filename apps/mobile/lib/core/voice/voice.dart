/// SAHOOL Voice Core
/// ملفات الأوامر الصوتية
///
/// A comprehensive voice command system for the SAHOOL mobile app.
/// نظام أوامر صوتية شامل لتطبيق سهول
///
/// Components:
/// - VoiceService: Speech recognition (speech_to_text)
/// - VoiceCommands: Command definitions with fuzzy matching
/// - VoiceFeedback: Text-to-speech responses (flutter_tts)
/// - VoiceCommandHandler: Command parsing and execution
/// - VoiceUI: UI widgets (button, overlay, suggestions)
///
/// يشمل:
/// - خدمة التعرف على الصوت
/// - تعريفات الأوامر مع المطابقة الضبابية
/// - التغذية الراجعة الصوتية (تحويل النص إلى كلام)
/// - معالج الأوامر الصوتية
/// - مكونات واجهة المستخدم الصوتية
///
/// Features:
/// - Arabic and English bilingual support
/// - Offline-capable speech recognition
/// - Fuzzy command matching
/// - Visual and audio feedback
/// - Wake word detection preparation
library;

// Core voice service (speech recognition)
export 'voice_service.dart';

// Command definitions and parsing
export 'voice_commands.dart';

// TTS feedback service
export 'voice_feedback.dart';

// Command handling and execution
export 'voice_command_handler.dart';

// UI components
export 'voice_ui.dart';

// Legacy exports (for backward compatibility)
export 'voice_command_service.dart' hide VoiceCommandType;
export 'voice_button_widget.dart' hide FloatingVoiceButton, VoiceHelpSheet, VoiceStatusIndicator;
