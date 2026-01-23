# SAHOOL Mobile Voice Commands System

## دليل الأوامر الصوتية لتطبيق سهول

A comprehensive voice command system for the SAHOOL mobile app, enabling hands-free operation for farmers in the field.

---

## Overview | نظرة عامة

The Voice Commands system allows farmers to control the SAHOOL app using voice commands in both Arabic and English. This is especially useful when working in the field with dirty hands or while operating equipment.

نظام الأوامر الصوتية يتيح للمزارعين التحكم في تطبيق سهول باستخدام الأوامر الصوتية بالعربية والإنجليزية.

### Key Features | الميزات الرئيسية

- **Bilingual Support**: Arabic (Yemeni, Saudi, Egyptian) and English
- **Offline Capable**: Works without internet when device supports on-device recognition
- **Fuzzy Matching**: Understands variations of commands
- **Audio Feedback**: Text-to-speech responses
- **Visual Feedback**: Animated UI indicators

---

## Available Commands | الأوامر المتاحة

### Navigation Commands | أوامر التنقل

| Arabic | English | Description |
|--------|---------|-------------|
| "افتح الحقول" | "Open fields" | Navigate to fields list |
| "أظهر الطقس" | "Show weather" | View weather information |
| "فحص NDVI" | "Check NDVI" | View vegetation health map |
| "افتح المهام" | "Open tasks" | Navigate to task list |
| "افتح المستشار" | "Open advisor" | Open agricultural advisor |
| "افتح الإعدادات" | "Open settings" | Open app settings |
| "الرئيسية" | "Go home" | Return to home screen |
| "رجوع" | "Go back" | Go to previous screen |

### Field Operations | عمليات الحقل

| Arabic | English | Description |
|--------|---------|-------------|
| "افتح حقل 1" | "Open field 1" | Select specific field |
| "الحقل الأول" | "Field number one" | Select first field |
| "تفاصيل الحقل" | "Field details" | View field information |
| "صحة المحصول" | "Crop health" | Check crop health status |

### Irrigation Commands | أوامر الري

| Arabic | English | Description |
|--------|---------|-------------|
| "جدول الري" | "Schedule irrigation" | Open irrigation scheduler |
| "سجل ري" | "Record irrigation" | Log irrigation activity |
| "أوقف الري" | "Stop irrigation" | Stop ongoing irrigation |
| "حالة الري" | "Irrigation status" | Check irrigation status |

### Task Management | إدارة المهام

| Arabic | English | Description |
|--------|---------|-------------|
| "إنشاء مهمة" | "Create task" | Create new task |
| "مهام اليوم" | "Today's tasks" | View today's tasks |
| "أكمل المهمة" | "Complete task" | Mark task as complete |
| "المهام المتأخرة" | "Overdue tasks" | Show overdue tasks |

### Weather Commands | أوامر الطقس

| Arabic | English | Description |
|--------|---------|-------------|
| "كيف الطقس" | "How's the weather" | Current conditions |
| "توقعات الطقس" | "Weather forecast" | Multi-day forecast |
| "هل ستمطر" | "Will it rain" | Rain probability |

### Scouting & Reports | الفحص والتقارير

| Arabic | English | Description |
|--------|---------|-------------|
| "ابدأ الفحص" | "Start scouting" | Begin field scouting |
| "التقط صورة" | "Take photo" | Capture documentation photo |
| "بلغ عن مشكلة" | "Report problem" | Report field issue |
| "عرض التقارير" | "View reports" | See scouting reports |

### Utility Commands | أوامر المساعدة

| Arabic | English | Description |
|--------|---------|-------------|
| "مساعدة" | "Help" | Show available commands |
| "إلغاء" | "Cancel" | Cancel current operation |
| "كرر" | "Repeat" | Repeat last response |
| "ملخص اليوم" | "Daily summary" | Get farm summary |

---

## Usage Guide | دليل الاستخدام

### Starting Voice Recognition

1. **Tap the microphone button** (green button, usually floating at bottom-right)
2. **Wait for the listening indicator** (button turns red, pulsing animation)
3. **Speak your command clearly**
4. **Wait for confirmation** (audio feedback confirms the command)

### Tips for Better Recognition | نصائح للتعرف الأفضل

1. **Speak clearly and naturally** - لا تتحدث بسرعة كبيرة
2. **Reduce background noise** - قلل الضوضاء المحيطة
3. **Use exact command phrases** - استخدم العبارات المحددة
4. **Wait for the indicator** before speaking - انتظر مؤشر الاستماع

### Command Variations

The system supports fuzzy matching, so variations work:

**Arabic Examples:**
- "افتح الحقول" = "اعرض الحقول" = "شوف الحقول"
- "كيف الطقس" = "شو الجو" = "أحوال الطقس"

**English Examples:**
- "Open fields" = "Show fields" = "View fields"
- "How's the weather" = "Weather" = "What's the weather"

---

## Technical Architecture | البنية التقنية

### Components

```
lib/core/voice/
├── voice.dart                  # Barrel file (exports)
├── voice_service.dart          # Speech recognition (speech_to_text)
├── voice_commands.dart         # Command definitions & parsing
├── voice_feedback.dart         # TTS feedback (flutter_tts)
├── voice_command_handler.dart  # Command execution
├── voice_ui.dart              # UI widgets
├── voice_command_service.dart  # Legacy service (backward compatibility)
└── voice_button_widget.dart   # Legacy widget (backward compatibility)
```

### Dependencies

```yaml
# pubspec.yaml
dependencies:
  speech_to_text: ^7.0.0   # Speech recognition
  flutter_tts: ^4.2.0      # Text-to-speech
```

### Supported Languages

| Locale | Name | Dialect |
|--------|------|---------|
| ar-YE | Arabic (Yemen) | Primary |
| ar-SA | Arabic (Saudi Arabia) | Fallback |
| ar-EG | Arabic (Egypt) | Fallback |
| ar | Arabic (General) | Fallback |
| en-US | English (US) | Alternative |
| en-GB | English (UK) | Alternative |

---

## Integration Guide | دليل التكامل

### Adding Voice Button to a Screen

```dart
import 'package:sahool_field_app/core/voice/voice.dart';

class MyScreen extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      body: Stack(
        children: [
          // Your content
          YourContent(),

          // Add floating voice button
          FloatingVoiceButton(
            onCommand: (command) {
              // Handle command result
              print('Command: ${command.type}');
            },
          ),
        ],
      ),
    );
  }
}
```

### Using Voice Control Mixin

```dart
class MyScreen extends ConsumerStatefulWidget {
  @override
  ConsumerState<MyScreen> createState() => _MyScreenState();
}

class _MyScreenState extends ConsumerState<MyScreen>
    with VoiceControlMixin<MyScreen> {

  @override
  void setupVoiceHandlers() {
    // Register custom handler for this screen
    registerVoiceHandler(
      VoiceCommandType.selectField,
      (command, context) async {
        final fieldId = command.parameters['fieldId'];
        // Custom handling
        return CommandHandlerResult(
          command: command,
          status: CommandExecutionStatus.success,
          messageAr: 'تم تحديد الحقل',
          messageEn: 'Field selected',
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: /* your content */,
      floatingActionButton: VoiceButton(),
    );
  }
}
```

### Listening to Command Results

```dart
class MyWidget extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Listen to command results
    ref.listen(commandResultProvider, (prev, next) {
      next.whenData((result) {
        if (result.isSuccess) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text(result.messageAr ?? '')),
          );
        }
      });
    });

    return /* your widget */;
  }
}
```

---

## Adding New Commands | إضافة أوامر جديدة

### 1. Add Command Type

```dart
// In voice_commands.dart
enum VoiceCommandType {
  // ... existing commands

  myNewCommand('my_new_command', 'Category', 'التصنيف'),
}
```

### 2. Add Command Definition

```dart
// In VoiceCommandRegistry.commands
VoiceCommandDefinition(
  type: VoiceCommandType.myNewCommand,
  nameEn: 'My New Command',
  nameAr: 'أمري الجديد',
  descriptionEn: 'Description of what this command does',
  descriptionAr: 'وصف ما يفعله هذا الأمر',
  patternsEn: ['my new command', 'do my thing', 'execute new'],
  patternsAr: ['أمري الجديد', 'نفذ أمري', 'شغل الجديد'],
  examplesEn: ['My new command', 'Do my thing'],
  examplesAr: ['أمري الجديد', 'نفذ أمري'],
),
```

### 3. Add Handler

```dart
// In voice_command_handler.dart _defaultCommandHandler
case VoiceCommandType.myNewCommand:
  return _navigateTo(command, '/my-route',
      messageAr: 'جاري تنفيذ الأمر', messageEn: 'Executing command');
```

### 4. Add Feedback Response (Optional)

```dart
// In voice_feedback.dart _predefinedResponses
VoiceCommandType.myNewCommand: VoiceFeedbackResponse(
  arabicText: 'جاري تنفيذ الأمر الجديد',
  englishText: 'Executing new command',
),
```

---

## Troubleshooting | استكشاف الأخطاء

### Common Issues

#### "Speech recognition not available"

- **Cause**: Device doesn't support speech recognition
- **Solution**: Install Google Speech services (Android) or check iOS settings

#### "Microphone permission denied"

- **Cause**: App doesn't have microphone permission
- **Solution**: Go to Settings > Apps > SAHOOL > Permissions > Microphone

#### "Command not recognized"

- **Cause**: Speech wasn't clear or command not in registry
- **Solution**:
  - Speak more clearly
  - Use exact command phrases
  - Say "مساعدة" to see available commands

#### "No Arabic voice available"

- **Cause**: Arabic TTS voice not installed
- **Solution**:
  - Android: Settings > Accessibility > Text-to-speech > Install Arabic
  - iOS: Settings > Accessibility > Spoken Content > Voices

### Debug Logging

Enable debug logging to troubleshoot:

```dart
AppLogger.configure(
  enabled: true,
  minLevel: LogLevel.debug,
);
```

Check logs with tag `VOICE`, `VOICE_CMD`, `VOICE_TTS`, `VOICE_HANDLER`.

---

## Platform-Specific Notes

### Android

- Requires Google Speech Services for best recognition
- Arabic voices may need manual download from TTS settings
- Minimum SDK 23 (Android 6.0)

### iOS

- Uses built-in speech recognition
- Arabic language pack may need download in Settings
- Works well with Siri Arabic voice

---

## Future Enhancements | تحسينات مستقبلية

1. **Wake Word Detection** - Hands-free activation ("Hey Sahool" / "يا سهول")
2. **Continuous Listening Mode** - Always-on voice mode
3. **Voice Dictation** - Free-form text input for notes
4. **Conversation Mode** - Multi-turn dialogues with advisor
5. **Offline Training** - Improved offline recognition

---

## Support | الدعم

For issues with voice commands:

1. Check this documentation first
2. Enable debug logging and capture logs
3. Report issues with:
   - Device model
   - OS version
   - Language settings
   - Steps to reproduce

---

*Last Updated: January 2026*
