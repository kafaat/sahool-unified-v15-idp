import 'package:flutter_test/flutter_test.dart';
import 'package:sahool_field_app/core/voice/voice_command_service.dart';

void main() {
  late VoiceCommandService service;

  setUp(() {
    // Create a fresh instance for testing via the public constructor
    // Since VoiceCommandService uses a singleton, we test via the instance
    service = VoiceCommandService.instance;
  });

  group('VoiceCommandType', () {
    test('should have all expected command types', () {
      expect(VoiceCommandType.values.length, 12);
      expect(VoiceCommandType.values, contains(VoiceCommandType.openField));
      expect(VoiceCommandType.values, contains(VoiceCommandType.cropStatus));
      expect(
          VoiceCommandType.values, contains(VoiceCommandType.recordIrrigation));
      expect(VoiceCommandType.values, contains(VoiceCommandType.showTasks));
      expect(VoiceCommandType.values, contains(VoiceCommandType.createTask));
      expect(VoiceCommandType.values, contains(VoiceCommandType.weather));
      expect(VoiceCommandType.values, contains(VoiceCommandType.startScout));
      expect(VoiceCommandType.values, contains(VoiceCommandType.reportIssue));
      expect(VoiceCommandType.values, contains(VoiceCommandType.capturePhoto));
      expect(VoiceCommandType.values, contains(VoiceCommandType.dailySummary));
      expect(VoiceCommandType.values, contains(VoiceCommandType.help));
      expect(VoiceCommandType.values, contains(VoiceCommandType.unknown));
    });
  });

  group('VoiceCommand', () {
    test('should identify recognized commands', () {
      const cmd = VoiceCommand(
        type: VoiceCommandType.openField,
        parameters: {'fieldId': '1'},
        rawText: 'افتح الحقل الأول',
      );
      expect(cmd.isRecognized, true);
    });

    test('should identify unrecognized commands', () {
      const cmd = VoiceCommand(
        type: VoiceCommandType.unknown,
        parameters: {},
        rawText: 'something random',
      );
      expect(cmd.isRecognized, false);
    });
  });

  group('VoiceResult', () {
    test('should store all properties', () {
      final now = DateTime.now();
      const cmd = VoiceCommand(
        type: VoiceCommandType.weather,
        parameters: {},
        rawText: 'كيف الطقس',
      );
      final result = VoiceResult(
        text: 'كيف الطقس',
        command: cmd,
        confidence: 0.92,
        timestamp: now,
      );

      expect(result.text, 'كيف الطقس');
      expect(result.command, isNotNull);
      expect(result.command!.type, VoiceCommandType.weather);
      expect(result.confidence, 0.92);
      expect(result.timestamp, now);
    });

    test('should allow null command', () {
      final result = VoiceResult(
        text: 'unclear audio',
        confidence: 0.3,
        timestamp: DateTime.now(),
      );
      expect(result.command, isNull);
    });
  });

  group('VoiceHelpItem', () {
    test('should contain all help commands', () {
      final helpCommands = service.getHelpCommands();
      expect(helpCommands.length, 8);
    });

    test('should have command, description, and examples for each', () {
      final helpCommands = service.getHelpCommands();
      for (final item in helpCommands) {
        expect(item.command, isNotEmpty);
        expect(item.description, isNotEmpty);
        expect(item.examples, isNotEmpty);
      }
    });

    test('should include field navigation help', () {
      final helpCommands = service.getHelpCommands();
      final fieldHelp = helpCommands.firstWhere(
        (h) => h.command.contains('حقل'),
      );
      expect(fieldHelp.description, contains('حقل'));
    });

    test('should include weather help', () {
      final helpCommands = service.getHelpCommands();
      final weatherHelp = helpCommands.firstWhere(
        (h) => h.command.contains('الطقس'),
      );
      expect(weatherHelp.description, contains('الطقس'));
    });
  });

  group('VoiceStatus', () {
    test('should have all expected statuses', () {
      expect(VoiceStatus.values.length, 5);
      expect(VoiceStatus.values, contains(VoiceStatus.idle));
      expect(VoiceStatus.values, contains(VoiceStatus.ready));
      expect(VoiceStatus.values, contains(VoiceStatus.listening));
      expect(VoiceStatus.values, contains(VoiceStatus.processing));
      expect(VoiceStatus.values, contains(VoiceStatus.error));
    });
  });

  group('VoiceCommandService initialization', () {
    test('should initialize successfully', () async {
      final result = await service.initialize();
      expect(result, true);
    });

    test('should report not listening initially', () {
      expect(service.isListening, false);
    });

    test('should emit status stream events', () async {
      await service.initialize();

      final statuses = <VoiceStatus>[];
      final sub = service.statusStream.listen(statuses.add);

      // Trigger a status change
      service.cancelListening();

      await Future.delayed(const Duration(milliseconds: 50));
      await sub.cancel();

      expect(statuses, contains(VoiceStatus.idle));
    });
  });

  group('VoiceCommandService language', () {
    test('should set language', () {
      service.setLanguage('ar-SA');
      // No way to check internal state, but should not throw
    });

    test('should accept various locales', () {
      service.setLanguage('ar-YE');
      service.setLanguage('ar-SA');
      service.setLanguage('en-US');
      // Should not throw for any locale
    });
  });

  group('VoiceCommandService listening', () {
    test('should set listening state when starting', () async {
      await service.initialize();
      await service.startListening();
      expect(service.isListening, true);

      service.cancelListening();
      expect(service.isListening, false);
    });

    test('should not start listening twice', () async {
      await service.initialize();
      await service.startListening();
      final firstState = service.isListening;
      await service.startListening(); // Should be no-op
      expect(service.isListening, firstState);

      service.cancelListening();
    });

    test('stopListening should update status', () async {
      await service.initialize();
      await service.startListening();
      await service.stopListening();
      expect(service.isListening, false);
    });

    test('cancelListening should set idle status', () async {
      await service.initialize();
      await service.startListening();

      final statuses = <VoiceStatus>[];
      final sub = service.statusStream.listen(statuses.add);

      service.cancelListening();

      await Future.delayed(const Duration(milliseconds: 50));
      await sub.cancel();

      expect(statuses, contains(VoiceStatus.idle));
      expect(service.isListening, false);
    });
  });
}
